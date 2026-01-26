import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from app.config import settings

connection_pool = None

def get_connection_pool():
    global connection_pool
    if connection_pool is None:
        connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.database_url
        )
    return connection_pool

@contextmanager
def get_db():
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
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
                    posted_date TIMESTAMP,
                    salary VARCHAR(255),
                    apply_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
                CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
                
                CREATE TABLE IF NOT EXISTS refresh_logs (
                    id SERIAL PRIMARY KEY,
                    refresh_type VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    jobs_added INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_refresh_logs_timestamp ON refresh_logs(timestamp DESC);
            """)
