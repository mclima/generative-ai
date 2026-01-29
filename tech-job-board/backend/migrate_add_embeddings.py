#!/usr/bin/env python3
"""
Migration script to add embedding columns to jobs table.
Run this once to add the new columns to existing database.
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Adding embedding columns to jobs table...")
    
    cur.execute("""
        ALTER TABLE jobs 
        ADD COLUMN IF NOT EXISTS embedding_full TEXT,
        ADD COLUMN IF NOT EXISTS embedding_responsibilities TEXT,
        ADD COLUMN IF NOT EXISTS embedding_requirements TEXT;
    """)
    
    conn.commit()
    print("✅ Migration completed successfully!")
    print("Embedding columns added to jobs table.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    exit(1)
