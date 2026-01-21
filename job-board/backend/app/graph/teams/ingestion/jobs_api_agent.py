from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import SEARCH_QUERIES
from app.graph.teams.ingestion.salary_formatter import format_salary
from app.graph.teams.ingestion.description_formatter import format_description_to_html
import requests
import os
import html
import time
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
JOBS_API_URL = "https://jobs-api14.p.rapidapi.com/v2/linkedin/search"
JOBS_DETAIL_URL = "https://jobs-api14.p.rapidapi.com/v2/linkedin/get"

def get_linkedin_job_details(job_id: str, headers: dict) -> str:
    """Fetch full job description from LinkedIn API"""
    try:
        # Rate limit: 1 call per second
        time.sleep(1)
        
        params = {"id": job_id}
        response = requests.get(JOBS_DETAIL_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("hasError"):
                job_data = data.get("data", {})
                description = job_data.get("description", "")
                if description:
                    return format_description_to_html(description)
        
        return ""
    except Exception as e:
        print(f"  Error fetching job details for ID {job_id}: {e}")
        return ""

def ingest_jobs_api(state: GraphState) -> dict:
    """Fetch tech jobs from LinkedIn Jobs API (RapidAPI) using shared criteria"""
    try:
        if not RAPIDAPI_KEY:
            print("LinkedIn Jobs API: RAPIDAPI_KEY not found in environment")
            return {"raw_jobs": state["raw_jobs"]}
        
        jobs: list[RawJob] = []
        
        # Use centralized search queries
        queries = SEARCH_QUERIES[:3]
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
        }
        
        for query in queries[:2]:  # Limit to 2 queries to stay within free tier
            # Rate limit: 1 call per second
            time.sleep(1)
            
            params = {
                "query": query,
                "location": "Worldwide",
                "datePosted": "month",
                "employmentTypes": "fulltime;contractor",
                "workplaceTypes": "remote"
            }
            
            try:
                response = requests.get(JOBS_API_URL, headers=headers, params=params, timeout=15)
                
                if response.status_code != 200:
                    print(f"Jobs API returned status {response.status_code} for query: {query}")
                    continue
                
                data = response.json()
                
                # Check for errors in response
                if data.get("hasError"):
                    print(f"LinkedIn API error for query '{query}': {data.get('errors', [])}")
                    continue
                
                job_listings = data.get("data", [])
                
                for job in job_listings[:20]:  # Take 20 jobs per query
                    if not isinstance(job, dict):
                        continue
                    
                    title = html.unescape(job.get("title", ""))
                    company = html.unescape(job.get("companyName", "Unknown"))
                    url = job.get("linkedinUrl", "")
                    posted_date = job.get("datePosted", "")
                    location = job.get("location", "Remote")
                    job_id = job.get("id", "")
                    
                    if not title or not url or not job_id:
                        continue
                    
                    # Fetch full job description using the detail endpoint
                    description = get_linkedin_job_details(job_id, headers)
                    
                    # Fallback if description fetch fails
                    if not description:
                        description = f"<p>{title} at {company}</p><p>Location: {location}</p>"
                    
                    jobs.append({
                        "source": "linkedin",
                        "url": url,
                        "content": f"{title}|{company}|{location}",
                        "posted_date": posted_date,
                        "description": description,
                        "salary": None
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"Jobs API request failed for query '{query}': {e}")
                continue
        
        print(f"LinkedIn API fetched {len(jobs)} jobs")
        return {"raw_jobs": state["raw_jobs"] + jobs}
        
    except Exception as e:
        print(f"LinkedIn API ingestion error: {e}")
        return {"raw_jobs": state["raw_jobs"]}
