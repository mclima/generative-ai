#!/usr/bin/env python3
"""
Cron job script to refresh jobs daily at 3pm EST.
This script should be scheduled using cron or a task scheduler.

Example crontab entry (runs at 3pm EST daily):
0 20 * * * cd /path/to/tech-job-board/backend && /path/to/venv/bin/python app/cron_job.py

Note: 8pm UTC = 3pm EST (UTC-5)
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.services import JobService


async def run_daily_refresh():
    """Run the daily job refresh"""
    print("Starting daily job refresh at 3pm EST...")
    
    try:
        with get_db() as conn:
            job_service = JobService(conn)
            jobs_added = await job_service.refresh_jobs()
            total_jobs = job_service.get_total_jobs_count()
            
            print(f"Daily refresh completed successfully!")
            print(f"Jobs added: {jobs_added}")
            print(f"Total jobs in database: {total_jobs}")
            
            return jobs_added, total_jobs
    except Exception as e:
        print(f"Error during daily refresh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_daily_refresh())
