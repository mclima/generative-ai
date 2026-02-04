"""
Migration script to convert TIMESTAMP columns to TIMESTAMPTZ
Run this once to fix existing database schema
"""
import psycopg2
from app.config import settings

def migrate_timestamps():
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    
    try:
        print("Starting timestamp migration...")
        
        # Alter jobs table columns
        print("Altering jobs.posted_date to TIMESTAMPTZ...")
        cur.execute("ALTER TABLE jobs ALTER COLUMN posted_date TYPE TIMESTAMPTZ USING posted_date AT TIME ZONE 'UTC';")
        
        print("Altering jobs.created_at to TIMESTAMPTZ...")
        cur.execute("ALTER TABLE jobs ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';")
        
        # Alter refresh_logs table column
        print("Altering refresh_logs.timestamp to TIMESTAMPTZ...")
        cur.execute("ALTER TABLE refresh_logs ALTER COLUMN timestamp TYPE TIMESTAMPTZ USING timestamp AT TIME ZONE 'UTC';")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate_timestamps()
