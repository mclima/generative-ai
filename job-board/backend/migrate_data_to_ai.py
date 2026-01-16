"""
Migration script to update all jobs with role='data' to role='ai'
Run this once to migrate existing database records.
"""
from sqlmodel import Session, select
from db import engine, JobDB

def migrate_data_roles_to_ai():
    """Update all jobs with role='data' to role='ai'"""
    with Session(engine) as session:
        # Find all jobs with role='data'
        statement = select(JobDB).where(JobDB.role == "data")
        data_jobs = session.exec(statement).all()
        
        if not data_jobs:
            print("No jobs found with role='data'. Migration not needed.")
            return
        
        print(f"Found {len(data_jobs)} jobs with role='data'")
        print("Updating to role='ai'...")
        
        # Update each job
        for job in data_jobs:
            job.role = "ai"
            session.add(job)
        
        # Commit all changes
        session.commit()
        print(f"✓ Successfully updated {len(data_jobs)} jobs from 'data' to 'ai'")
        
        # Verify the update
        verify_statement = select(JobDB).where(JobDB.role == "data")
        remaining = session.exec(verify_statement).all()
        
        if remaining:
            print(f"⚠ Warning: {len(remaining)} jobs still have role='data'")
        else:
            print("✓ Verification passed: No jobs with role='data' remain")

if __name__ == "__main__":
    print("Starting migration: data → ai")
    migrate_data_roles_to_ai()
    print("Migration complete!")
