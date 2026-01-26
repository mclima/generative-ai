from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
from app.database import get_db, init_db
from app.schemas import JobResponse, MatchedJob, ResumeUpload, RefreshResponse, LastRefreshResponse
from app.services import JobService
from app.resume_matcher import ResumeMatcher
from app.resume_parser import ResumeParser

init_db()

app = FastAPI(title="Tech Job Board API", version="1.0.0")

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

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    category: Optional[str] = None,
    sort_by: str = "newest"
):
    with get_db() as conn:
        job_service = JobService(conn)
        
        if category and category != "All Jobs":
            jobs = job_service.get_jobs_by_category(category, sort_by)
        else:
            jobs = job_service.get_all_jobs(sort_by)
        
        return jobs

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
    with get_db() as conn:
        job_service = JobService(conn)
        jobs_added = await job_service.refresh_jobs()
        total_jobs = job_service.get_total_jobs_count()
        
        return RefreshResponse(
            message="Jobs refreshed successfully",
            jobs_added=jobs_added,
            total_jobs=total_jobs
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
        "categories": ["All Jobs", "AI", "Frontend", "Backend", "Full Stack", "DevOps", "Engineering"]
    }

@app.get("/api/stats")
async def get_stats():
    with get_db() as conn:
        job_service = JobService(conn)
        total_jobs = job_service.get_total_jobs_count()
        
        categories_count = {}
        for category in ["AI", "Frontend", "Backend", "Full Stack", "DevOps", "Engineering"]:
            count = len(job_service.get_jobs_by_category(category))
            categories_count[category] = count
        
        return {
            "total_jobs": total_jobs,
            "categories": categories_count
        }

@app.get("/api/last-refresh", response_model=LastRefreshResponse)
async def get_last_refresh():
    with get_db() as conn:
        job_service = JobService(conn)
        last_refresh = job_service.get_last_refresh_timestamp()
        
        return LastRefreshResponse(last_refresh=last_refresh)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
