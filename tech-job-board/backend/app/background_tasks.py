import asyncio
import httpx
from typing import List, Dict
from app.config import settings
from app.database import get_db

class BackgroundDescriptionFetcher:
    """Fetches job descriptions in background after fast refresh"""
    
    @staticmethod
    async def fetch_missing_descriptions():
        """Fetch descriptions for Jobs API jobs that don't have them yet"""
        try:
            # Get jobs that need descriptions
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, job_id 
                        FROM jobs 
                        WHERE source = 'Jobs API' 
                        AND (description = 'Description will be loaded shortly...' 
                             OR description IS NULL 
                             OR description = '')
                    """)
                    jobs_to_update = cur.fetchall()
            
            if not jobs_to_update:
                print("No jobs need description updates")
                return
            
            print(f"Fetching descriptions for {len(jobs_to_update)} jobs in background...")
            
            # Fetch descriptions
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "X-RapidAPI-Key": settings.rapidapi_key,
                    "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
                }
                
                for db_id, job_id in jobs_to_update:
                    try:
                        # Extract LinkedIn job ID from our job_id format (jobsapi_XXXXX)
                        linkedin_id = job_id.replace("jobsapi_", "")
                        
                        await asyncio.sleep(1)  # Rate limit
                        
                        detail_response = await client.get(
                            f"https://jobs-api14.p.rapidapi.com/v2/linkedin/get",
                            headers=headers,
                            params={"id": linkedin_id}
                        )
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            if detail_data.get("data"):
                                job_details = detail_data["data"]
                                description = job_details.get("description", "View full job details at LinkedIn")
                                
                                # Update database
                                with get_db() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute(
                                            "UPDATE jobs SET description = %s WHERE id = %s",
                                            (description, db_id)
                                        )
                                        conn.commit()
                                
                                print(f"Updated description for job {db_id}")
                        else:
                            print(f"Error fetching description for job {db_id}: {detail_response.status_code}")
                    
                    except Exception as e:
                        print(f"Error updating job {db_id}: {e}")
                        continue
            
            print(f"Background description fetching complete for {len(jobs_to_update)} jobs")
        
        except Exception as e:
            print(f"Error in background description fetcher: {e}")
    
    @staticmethod
    def start_background_fetch():
        """Start background task to fetch descriptions"""
        asyncio.create_task(BackgroundDescriptionFetcher.fetch_missing_descriptions())
