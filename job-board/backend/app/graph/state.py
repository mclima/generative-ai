from typing import TypedDict, List, Optional

class RawJob(TypedDict):
    source: str
    url: str
    content: str
    posted_date: Optional[str]
    description: Optional[str]
    salary: Optional[str]

class Understanding(TypedDict):
    role_category: str
    seniority: str
    skills: List[str]
    remote: bool
    location: str

class NormalizedJob(TypedDict):
    id: str
    source: str
    url: str
    title: Optional[str]
    company: Optional[str]
    understanding: Understanding
    score: Optional[float]

class GraphState(TypedDict):
    raw_jobs: List[RawJob]
    normalized_jobs: List[NormalizedJob]
    jobs: List[dict]  # Processed jobs for classification/validation/ranking
    role: Optional[str]
