from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import is_tech_job
from app.graph.teams.ingestion.html_formatter import format_html_description
import requests
import os
from dotenv import load_dotenv

load_dotenv()

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"

def ingest_jobicy(state: GraphState) -> dict:
    """Fetch tech jobs from Jobicy API - a remote-first job board with full job descriptions"""
    try:
        # Add headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://jobicy.com/"
        }
        
        params = {
            "count": 50,  # Reduced count to be less aggressive
        }
        
        response = requests.get(JOBICY_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            print(f"Jobicy API returned unsuccessful response")
            return {"raw_jobs": state["raw_jobs"]}
        
        jobs: list[RawJob] = []
        job_list = data.get("jobs", [])
        
        for job in job_list:
            title = job.get("jobTitle", "")
            company = job.get("companyName", "")
            location = job.get("jobGeo", "Remote")
            job_url = job.get("url", "")
            posted_date = job.get("pubDate", "")
            
            # Extract full job description (HTML format)
            job_description_html = job.get("jobDescription", "")
            
            # Convert HTML to formatted plain text
            description_text = format_html_description(job_description_html)
            description_preview = description_text[:500] if description_text else ""
            
            # Extract salary information if available
            salary_min = job.get("salaryMin")
            salary_max = job.get("salaryMax")
            salary_currency = job.get("salaryCurrency", "USD")
            salary_period = job.get("salaryPeriod", "yearly")
            
            salary = None
            if salary_min or salary_max:
                if salary_min and salary_max:
                    salary = f"{salary_currency} {salary_min:,.0f} - {salary_max:,.0f} per {salary_period}"
                elif salary_min:
                    salary = f"{salary_currency} {salary_min:,.0f}+ per {salary_period}"
                elif salary_max:
                    salary = f"Up to {salary_currency} {salary_max:,.0f} per {salary_period}"
            
            # Check if it's a tech job
            job_industry = job.get("jobIndustry", [])
            if is_tech_job(title, tags=job_industry, description=description_text):
                jobs.append({
                    "source": "jobicy",
                    "url": job_url,
                    "content": f"{title}|{company}|{description_preview}",
                    "posted_date": posted_date,
                    "description": description_text,
                    "salary": salary
                })
        
        print(f"Jobicy fetched {len(jobs)} jobs")
        return {"raw_jobs": state["raw_jobs"] + jobs}
        
    except requests.exceptions.RequestException as e:
        print(f"Jobicy request error: {e}")
        return {"raw_jobs": state["raw_jobs"]}
    except Exception as e:
        print(f"Jobicy error: {e}")
        return {"raw_jobs": state["raw_jobs"]}
