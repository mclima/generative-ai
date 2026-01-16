from app.graph.state import NormalizedJob
from app.api.schemas import JobOut


def job_to_api(job: NormalizedJob) -> JobOut:
    u = job["understanding"]

    return JobOut(
        id=job["id"],
        title=job.get("title", "Unknown"),
        company=job.get("company", "Unknown"),
        role_category=u["role_category"],
        seniority=u["seniority"],
        skills=u["skills"],
        remote=u["remote"],
        location=u["location"],
        source=job["source"],
        url=job["url"],
        score=job.get("score"),
    )
