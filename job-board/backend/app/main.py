from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
from app.job_graph import job_graph
from app.schemas import Job
from app.llm import llm_config
from app.job_refresh import refresh_manager
from app.source_tracker import source_tracker
from app.cache import job_cache
from app.resume_matcher import extract_skills_from_resume, match_jobs_to_resume, generate_match_explanation
from app.file_parser import parse_resume_file
from fastapi import UploadFile, File, Form
from app.job_parser import parse_job_description
from repository import save_jobs, get_jobs, get_job_by_id
from db import create_tables
import threading
import json

app = FastAPI(title="Agentic Tech Job Board API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# App startup
# -------------------------
@app.on_event("startup")
def on_startup():
    create_tables()


# -------------------------
# Jobs endpoint
# -------------------------
def _refresh_jobs_background():
    """Background task to refresh jobs"""
    job_id = str(uuid.uuid4())[:8]
    
    try:
        print(f"[{job_id}] Starting background job refresh...")
        result = job_graph.invoke({
            "raw_jobs": [],
            "normalized_jobs": [],
            "role": None,
            "jobs": []
        })

        if result.get("jobs"):
            # Parsing disabled due to rate limits
            # for job in result["jobs"]:
            #     if job.get("description"):
            #         parsed = parse_job_description(job["description"])
            #         job["requirements"] = parsed.get("requirements", [])
            #         job["responsibilities"] = parsed.get("responsibilities", [])
            
            save_jobs(result["jobs"])
            refresh_manager.mark_refreshed()
            
            # Invalidate cache after new jobs are added
            job_cache.invalidate_all()
            
        print(f"[{job_id}] Background job refresh completed: {len(result.get('jobs', []))} jobs")
    except Exception as e:
        print(f"[{job_id}] Error in background job refresh: {e}")


@app.get("/jobs", response_model=list[Job])
def list_jobs(
    role: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("score"),
    order: str = Query("desc"),
):
    # Auto-refresh jobs in background if needed
    if refresh_manager.should_refresh():
        with refresh_manager.refresh_lock:
            # Double-check after acquiring lock
            if refresh_manager.should_refresh():
                print("Triggering job refresh in background...")
                thread = threading.Thread(target=_refresh_jobs_background, daemon=True)
                thread.start()

    # Try to get from cache first
    cached_jobs = job_cache.get_jobs(role, remote, limit, offset, sort_by, order)
    if cached_jobs is not None:
        return cached_jobs

    # Cache miss - query database
    jobs = get_jobs(
        role=role,
        remote=remote,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
    )
    
    # Parse JSON strings back to lists
    for job in jobs:
        if job.requirements:
            job.requirements = json.loads(job.requirements)
        if job.responsibilities:
            job.responsibilities = json.loads(job.responsibilities)
    
    # Cache the results for 15 minutes (900 seconds)
    job_cache.set_jobs(jobs, role, remote, limit, offset, sort_by, order, ttl=900)
    
    return jobs


@app.get("/jobs/refresh/status")
def get_refresh_status():
    """Get the status of job refresh"""
    last_refresh = refresh_manager.get_last_refresh_time()
    return {
        "last_refresh": last_refresh.isoformat() if last_refresh else None,
        "should_refresh": refresh_manager.should_refresh(),
        "refresh_interval_hours": refresh_manager.refresh_interval_hours,
        "sources": source_tracker.get_all_sources_status(),
        "cache": job_cache.get_stats()
    }


@app.post("/jobs/refresh")
def refresh_jobs(force: bool = Query(False, description="Force refresh all sources, bypassing intervals")):
    """Manually trigger job ingestion from all active sources"""
    try:
        # Run LangGraph ingestion + processing
        result = job_graph.invoke({
            "raw_jobs": [],
            "normalized_jobs": [],
            "role": None,
            "jobs": [],
            "force_refresh": force
        })

        # Persist deduplicated jobs
        if result.get("jobs"):
            # Parsing disabled due to rate limits
            # for job in result["jobs"]:
            #     if job.get("description"):
            #         parsed = parse_job_description(job["description"])
            #         job["requirements"] = parsed.get("requirements", [])
            #         job["responsibilities"] = parsed.get("responsibilities", [])
            
            save_jobs(result["jobs"])
        
        refresh_manager.mark_refreshed()
        
        # Invalidate cache after refresh
        job_cache.invalidate_all()
        
        return {
            "status": "success",
            "jobs_fetched": len(result.get("jobs", []))
        }
    except Exception as e:
        print(f"Error in job graph: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Job refresh failed: {str(e)}")


@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
    job = get_job_by_id(job_id)
    if job:
        # Parse JSON strings back to lists
        if job.requirements:
            job.requirements = json.loads(job.requirements)
        if job.responsibilities:
            job.responsibilities = json.loads(job.responsibilities)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# -------------------------
# Resume Matching endpoint
# -------------------------
@app.post("/jobs/match")
def match_resume(data: dict = Body(...)):
    """Match resume to jobs using AI"""
    try:
        resume_text = data.get("resume_text", "")
        
        if not resume_text or len(resume_text.strip()) < 100:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Resume text is required and must be at least 100 characters")
        
        # Extract skills and preferences from resume
        resume_data = extract_skills_from_resume(resume_text)
        
        # Get all jobs from database
        all_jobs = get_jobs(limit=500)
        
        # Convert to dict format for matching
        jobs_list = [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote": job.remote,
                "role": job.role,
                "source": job.source,
                "url": job.url,
                "posted_date": job.posted_date,
                "score": job.score,
                "description": job.description,
                "salary": job.salary
            }
            for job in all_jobs
        ]
        
        # Match jobs to resume
        matched_jobs = match_jobs_to_resume(resume_data, jobs_list)
        
        # Add match explanations
        for job in matched_jobs[:20]:  # Top 20 matches
            job["match_explanation"] = generate_match_explanation(job, resume_data)
        
        return {
            "resume_analysis": resume_data,
            "matched_jobs": matched_jobs[:20],  # Return top 20
            "total_matches": len(matched_jobs)
        }
    except Exception as e:
        print(f"Error matching resume: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Resume matching failed: {str(e)}")


@app.post("/jobs/match/upload")
async def match_resume_file(file: UploadFile = File(...)):
    """Match resume file (PDF, DOCX, TXT) to jobs using AI"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse file based on type
        resume_text = parse_resume_file(file.filename, file_content)
        
        if not resume_text or len(resume_text.strip()) < 100:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Resume text is too short or could not be extracted")
        
        # Extract skills and preferences from resume
        resume_data = extract_skills_from_resume(resume_text)
        
        # Get all jobs from database
        all_jobs = get_jobs(limit=500)
        
        # Convert to dict format for matching
        jobs_list = [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote": job.remote,
                "role": job.role,
                "source": job.source,
                "url": job.url,
                "posted_date": job.posted_date,
                "score": job.score,
                "description": job.description,
                "salary": job.salary
            }
            for job in all_jobs
        ]
        
        # Match jobs to resume
        matched_jobs = match_jobs_to_resume(resume_data, jobs_list)
        
        # Add match explanations
        for job in matched_jobs[:20]:  # Top 20 matches
            job["match_explanation"] = generate_match_explanation(job, resume_data)
        
        return {
            "resume_analysis": resume_data,
            "matched_jobs": matched_jobs[:20],  # Return top 20
            "total_matches": len(matched_jobs)
        }
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error matching resume file: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Resume matching failed: {str(e)}")


# -------------------------
# LLM Configuration endpoint
# -------------------------
@app.get("/config/llm")
def get_llm_config():
    return {
        "provider": "openai",
        "model": llm_config.model,
        "temperature": llm_config.temperature
    }
