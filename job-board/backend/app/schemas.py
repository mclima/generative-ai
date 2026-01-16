from pydantic import BaseModel
from typing import List, Optional

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    remote: bool
    role: str
    source: str
    url: Optional[str] = None
    posted_date: Optional[str] = None
    score: float = 1.0
    description: Optional[str] = None
    salary: Optional[str] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class JobOut(BaseModel):
    id: str
    title: str
    company: str
    role_category: str
    seniority: str
    skills: List[str]
    remote: bool
    location: str
    source: str
    url: str
    score: Optional[float] = None

class JobQuery(BaseModel):
    role: Optional[str] = None
    remote: Optional[bool] = None
