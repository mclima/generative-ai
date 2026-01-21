from sqlmodel import Session, select
from db import engine, JobDB, hash_job
import json
import re
from datetime import datetime, timedelta

ALLOWED_SORT_FIELDS = {
    "score": JobDB.score,
    "title": JobDB.title,
    "company": JobDB.company,
    "posted_date": JobDB.posted_date,
}

def cleanup_old_jobs():
    """Delete jobs older than 30 days"""
    with Session(engine) as session:
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Delete jobs with posted_date older than 30 days
        all_jobs = session.exec(select(JobDB)).all()
        deleted_count = 0
        
        for job in all_jobs:
            if job.posted_date:
                try:
                    # Parse ISO format string
                    if isinstance(job.posted_date, str) and job.posted_date:
                        # Handle both with and without timezone
                        job_date_str = job.posted_date.replace('Z', '+00:00')
                        job_date = datetime.fromisoformat(job_date_str)
                        
                        # Make timezone-aware if naive
                        if job_date.tzinfo is None:
                            job_date = job_date.replace(tzinfo=timezone.utc)
                        
                        if job_date < cutoff_date:
                            session.delete(job)
                            deleted_count += 1
                except (ValueError, TypeError) as e:
                    # Skip jobs with invalid date formats
                    pass
        
        session.commit()
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} jobs older than 30 days")

def save_jobs(jobs: list[dict]):
    with Session(engine) as session:
        for job in jobs:
            job_hash = hash_job(
                job.get("title", ""),
                job.get("company", ""),
                job.get("source", "")
            )
            
            existing = session.exec(
                select(JobDB).where(JobDB.job_hash == job_hash)
            ).first()
            
            if not existing:
                # Convert lists to JSON strings for storage
                requirements = job.get("requirements")
                responsibilities = job.get("responsibilities")
                
                # Get description (now with HTML formatting from ingestion agents)
                description = job.get("description")
                
                db_job = JobDB(
                    job_hash=job_hash,
                    title=job.get("title", "Unknown"),
                    company=job.get("company", "Unknown"),
                    location=job.get("location"),
                    remote=job.get("remote", False),
                    role=job.get("role", "unknown"),
                    source=job.get("source", "unknown"),
                    url=job.get("url"),
                    posted_date=job.get("posted_date"),
                    score=job.get("score", 1.0),
                    description=description,
                    salary=job.get("salary"),
                    requirements=json.dumps(requirements) if requirements else None,
                    responsibilities=json.dumps(responsibilities) if responsibilities else None
                )
                session.add(db_job)
        
        session.commit()
        
        # Clean up old jobs after saving new ones
        cleanup_old_jobs()

def get_jobs(
    role=None,
    remote=None,
    limit=20,
    offset=0,
    sort_by="posted_date",
    order="desc",
):
    with Session(engine) as session:
        query = select(JobDB)

        if role:
            query = query.where(JobDB.role == role)
        if remote is not None:
            query = query.where(JobDB.remote == remote)

        sort_column = ALLOWED_SORT_FIELDS.get(sort_by, JobDB.posted_date)
        query = query.order_by(
            sort_column.desc() if order == "desc" else sort_column.asc()
        )

        query = query.offset(offset).limit(limit)
        return session.exec(query).all()

def get_job_by_id(job_id: int):
    with Session(engine) as session:
        return session.get(JobDB, job_id)
