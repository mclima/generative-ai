from psycopg2.extras import RealDictCursor
from app.job_aggregator import JobAggregator
from app.background_tasks import BackgroundDescriptionFetcher
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
import asyncio

class JobService:
    _refresh_lock = asyncio.Lock()
    
    def __init__(self, conn):
        self.conn = conn
        self.aggregator = JobAggregator()
    
    async def refresh_jobs(self) -> int:
        # Use lock to prevent duplicate refreshes
        async with JobService._refresh_lock:
            jobs_data = await self.aggregator.fetch_jobs()
            
            new_jobs_count = 0
            with self.conn.cursor() as cur:
                for job_data in jobs_data:
                    cur.execute("SELECT id FROM jobs WHERE job_id = %s", (job_data["job_id"],))
                    existing_job = cur.fetchone()
                    
                    if not existing_job:
                        cur.execute("""
                            INSERT INTO jobs (job_id, title, company, location, description, 
                                            category, source, posted_date, salary, apply_url)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_data["job_id"],
                            job_data["title"],
                            job_data["company"],
                            job_data["location"],
                            job_data["description"],
                            job_data["category"],
                            job_data["source"],
                            job_data["posted_date"],
                            job_data.get("salary"),
                            job_data["apply_url"]
                        ))
                        new_jobs_count += 1
                
                cur.execute("""
                    INSERT INTO refresh_logs (refresh_type, jobs_added)
                    VALUES (%s, %s)
                """, ("scheduled", new_jobs_count))
                
                cur.execute("""
                    DELETE FROM refresh_logs 
                    WHERE timestamp < NOW() - INTERVAL '30 days'
                """)
                
                cur.execute("""
                    DELETE FROM jobs 
                    WHERE posted_date < NOW() - INTERVAL '10 days'
                """)
            
            self.conn.commit()
            
            # Start background task to fetch descriptions
            # TEMPORARILY DISABLED to avoid excessive API calls during testing
            asyncio.create_task(BackgroundDescriptionFetcher.fetch_missing_descriptions())
            
            return new_jobs_count
    
    def get_all_jobs(self, sort_by: str = "newest") -> List[Dict]:
        order = "DESC" if sort_by == "newest" else "ASC"
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT * FROM jobs 
                WHERE posted_date >= NOW() - INTERVAL '10 days'
                ORDER BY posted_date {order}
            """)
            return cur.fetchall()
    
    def get_jobs_by_category(self, category: str, sort_by: str = "newest") -> List[Dict]:
        order = "DESC" if sort_by == "newest" else "ASC"
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT * FROM jobs 
                WHERE category = %s 
                AND posted_date >= NOW() - INTERVAL '10 days'
                ORDER BY posted_date {order}
            """, (category,))
            return cur.fetchall()
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            return cur.fetchone()
    
    def get_total_jobs_count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM jobs")
            return cur.fetchone()[0]
    
    def get_last_refresh_timestamp(self) -> Optional[datetime]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT timestamp FROM refresh_logs 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            result = cur.fetchone()
            if not result:
                return None

            ts = result['timestamp']
            return ts.replace(tzinfo=timezone.utc) if ts and ts.tzinfo is None else ts
