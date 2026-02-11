from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import logging
import psycopg2
from datetime import datetime
from app.database import get_db, init_db
from app.schemas import JobResponse, MatchedJob, ResumeUpload, RefreshResponse, LastRefreshResponse
from app.services import JobService
from app.resume_matcher import ResumeMatcher
from app.resume_parser import ResumeParser
from app.task_manager import task_manager, TaskStatus

logger = logging.getLogger(__name__)

# In-memory cache for jobs (fallback when database is unavailable)
jobs_cache = {
    'jobs': [],
    'last_updated': None,
    'by_category': {}
}

app = FastAPI(title="Tech Job Board API", version="1.0.0")

# Try to initialize database, but don't fail if unavailable
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.warning(f"Database initialization failed (will retry on first request): {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Tech Job Board API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring database connectivity"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    response: Response,
    category: Optional[str] = None,
    sort_by: str = "newest"
):
    try:
        with get_db() as conn:
            job_service = JobService(conn)
            
            if category and category != "All Jobs":
                jobs = job_service.get_jobs_by_category(category, sort_by)
            else:
                jobs = job_service.get_all_jobs(sort_by)
            
            # Update cache on successful fetch
            cache_key = f"{category}_{sort_by}"
            jobs_cache['by_category'][cache_key] = jobs
            jobs_cache['last_updated'] = datetime.now()
            
            return jobs
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logger.error(f"Database connection error in get_jobs: {e}")
        
        # Try to return cached jobs
        cache_key = f"{category}_{sort_by}"
        if cache_key in jobs_cache['by_category'] and jobs_cache['by_category'][cache_key]:
            logger.info(f"Returning {len(jobs_cache['by_category'][cache_key])} cached jobs")
            response.headers["X-Data-Source"] = "cache"
            if jobs_cache['last_updated']:
                response.headers["X-Cache-Time"] = jobs_cache['last_updated'].isoformat()
            return jobs_cache['by_category'][cache_key]
        
        # No cache available, return empty list with error in header
        logger.warning("No cached jobs available")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable and no cached jobs available."
        )

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    with get_db() as conn:
        job_service = JobService(conn)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job

@app.post("/api/jobs/refresh", response_model=RefreshResponse)
async def refresh_jobs():
    try:
        with get_db() as conn:
            job_service = JobService(conn)
            jobs_added = await job_service.refresh_jobs()
            total_jobs = job_service.get_total_jobs_count()
            
            return RefreshResponse(
                message="Jobs refreshed successfully",
                jobs_added=jobs_added,
                total_jobs=total_jobs
            )
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logger.error(f"Database connection error in refresh_jobs: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Job refresh failed."
        )

@app.post("/api/match-resume", response_model=List[MatchedJob])
async def match_resume(
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None)
):
    if not resume_text and not resume_file:
        raise HTTPException(status_code=400, detail="Please provide either resume text or upload a file")
    
    if resume_file:
        file_content = await resume_file.read()
        try:
            resume_text = ResumeParser.parse_resume(file_content, resume_file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short or empty")
    
    with get_db() as conn:
        job_service = JobService(conn)
        all_jobs = job_service.get_all_jobs()
    
    matcher = ResumeMatcher()
    matched_jobs = await matcher.match_resume_to_jobs(resume_text, all_jobs)
    
    return matched_jobs

@app.get("/api/categories")
async def get_categories():
    return {
        "categories": ["All Jobs", "AI", "Engineering"]
    }

@app.get("/api/stats")
async def get_stats():
    with get_db() as conn:
        job_service = JobService(conn)
        total_jobs = job_service.get_total_jobs_count()
        
        categories_count = {}
        for category in ["AI", "Engineering"]:
            count = len(job_service.get_jobs_by_category(category))
            categories_count[category] = count
        
        return {
            "total_jobs": total_jobs,
            "categories": categories_count
        }

@app.get("/api/last-refresh", response_model=LastRefreshResponse)
async def get_last_refresh():
    try:
        with get_db() as conn:
            job_service = JobService(conn)
            last_refresh = job_service.get_last_refresh_timestamp()
            
            return LastRefreshResponse(last_refresh=last_refresh)
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logger.error(f"Database connection error in get_last_refresh: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please try again in a moment."
        )

async def process_resume_matching(task_id: str, resume_text: str):
    """Background task to process resume matching"""
    try:
        print(f"[Task {task_id}] Starting resume matching...")
        task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=5)
        await asyncio.sleep(0.5)  # Small delay to ensure frontend sees initial progress
        
        task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=10)
        
        print(f"[Task {task_id}] Fetching jobs from database...")
        with get_db() as conn:
            job_service = JobService(conn)
            all_jobs = job_service.get_all_jobs()
        print(f"[Task {task_id}] Found {len(all_jobs)} jobs to match against")
        
        task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=30)
        
        # Progress callback to update during matching
        def update_progress(progress: int):
            task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=progress)
        
        print(f"[Task {task_id}] Starting resume analysis and matching...")
        matcher = ResumeMatcher()
        matched_jobs = await matcher.match_resume_to_jobs(resume_text, all_jobs, progress_callback=update_progress)
        print(f"[Task {task_id}] Matching complete. Found {len(matched_jobs)} matches")
        
        task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=95)
        
        # Convert to dict for JSON serialization
        result = [job.dict() if hasattr(job, 'dict') else job for job in matched_jobs]
        
        task_manager.update_task(task_id, TaskStatus.COMPLETED, progress=100, result=result)
        print(f"[Task {task_id}] Task completed successfully")
        
    except Exception as e:
        print(f"[Task {task_id}] ERROR: {str(e)}")
        import traceback
        print(f"[Task {task_id}] Traceback: {traceback.format_exc()}")
        task_manager.update_task(task_id, TaskStatus.FAILED, error=str(e))

@app.post("/api/match-resume-async")
async def match_resume_async(
    background_tasks: BackgroundTasks,
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None)
):
    """Start async resume matching and return task ID immediately"""
    if resume_file:
        file_content = await resume_file.read()
        try:
            resume_text = ResumeParser.parse_resume(file_content, resume_file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short or empty")
    
    # Create task and return ID immediately
    task_id = task_manager.create_task()
    
    # Set initial progress so frontend shows activity immediately
    task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=1)
    
    # Start background processing
    background_tasks.add_task(process_resume_matching, task_id, resume_text)
    
    return {"task_id": task_id, "status": "processing", "progress": 1}

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of resume matching task"""
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
