import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from app.config import settings
import time
import logging

logger = logging.getLogger(__name__)

connection_pool = None

def get_connection_pool():
    global connection_pool
    if connection_pool is None:
        connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.database_url,
            connect_timeout=10,  # 10 second timeout
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
    return connection_pool

@contextmanager
def get_db():
    pool = get_connection_pool()
    conn = None
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            conn = pool.getconn()
            
            # Test connection is alive
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            
            break  # Connection successful
            
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            
            if conn:
                try:
                    pool.putconn(conn, close=True)
                except:
                    pass
                conn = None
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            pool.putconn(conn)

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    company VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    description TEXT,
                    category VARCHAR(100),
                    source VARCHAR(100),
                    posted_date TIMESTAMPTZ,
                    salary VARCHAR(255),
                    apply_url TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    embedding_full TEXT,
                    embedding_responsibilities TEXT,
                    embedding_requirements TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
                CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
                
                CREATE TABLE IF NOT EXISTS refresh_logs (
                    id SERIAL PRIMARY KEY,
                    refresh_type VARCHAR(50),
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    jobs_added INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_refresh_logs_timestamp ON refresh_logs(timestamp DESC);
            """)
