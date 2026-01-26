from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    category: str
    source: str
    posted_date: datetime
    salary: Optional[str] = None
    apply_url: str

class JobCreate(JobBase):
    job_id: str

class JobResponse(JobBase):
    id: int
    job_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchedJob(JobResponse):
    match_score: float
    match_level: str
    matched_skills: List[str]
    missed_skills: List[str]
    title_score: float
    skill_score: float
    semantic_score: float

class ResumeUpload(BaseModel):
    resume_text: Optional[str] = None
    
class RefreshResponse(BaseModel):
    message: str
    jobs_added: int
    total_jobs: int

class LastRefreshResponse(BaseModel):
    last_refresh: Optional[datetime] = None
