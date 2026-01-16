from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobsdb")

engine = create_engine(DATABASE_URL, echo=False)

class JobDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_hash: str = Field(index=True, unique=True)

    title: str
    company: str
    location: Optional[str]
    remote: bool
    role: str
    source: str
    url: Optional[str] = None
    posted_date: Optional[str] = None
    score: float
    description: Optional[str] = None
    salary: Optional[str] = None
    requirements: Optional[str] = None  # JSON string of list
    responsibilities: Optional[str] = None  # JSON string of list

def create_tables():
    SQLModel.metadata.create_all(engine)

def hash_job(title: str, company: str, source: str) -> str:
    raw = f"{title}|{company}|{source}"
    return hashlib.sha256(raw.encode()).hexdigest()
