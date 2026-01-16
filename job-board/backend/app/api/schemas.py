from pydantic import BaseModel
from typing import List, Optional

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str]
    remote: bool
    role: str
    source: str
    score: float

class JobQuery(BaseModel):
    role: Optional[str] = None
    remote: Optional[bool] = None
