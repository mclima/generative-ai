from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import SEARCH_QUERIES
from app.graph.teams.ingestion.salary_formatter import format_salary
from app.graph.teams.ingestion.description_formatter import format_description_to_html
import requests
import os
import html
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

def ingest_jsearch(state: GraphState) -> dict:
    """Fetch tech jobs from JSearch API (Google for Jobs aggregator) using shared criteria"""
    try:
        if not RAPIDAPI_KEY:
            print("JSearch: RAPIDAPI_KEY not found in environment")
            return {"raw_jobs": state["raw_jobs"]}
        
        jobs: list[RawJob] = []
        
        # Use centralized search queries with 'remote' keyword
        # JSearch works better with combined keywords, so we group them
        queries = [f"{query} remote" for query in SEARCH_QUERIES[:8]]
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        for query in queries[:2]:  # Limit to 2 queries to stay within free tier
            params = {
                "query": query,
                "page": "1",
                "num_pages": "1",
                "date_posted": "month"
            }
            
            try:
                response = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=15)
                
                if response.status_code != 200:
                    print(f"JSearch returned status {response.status_code} for query: {query}")
                    continue
                
                data = response.json()
                job_listings = data.get("data", [])
                
                if not job_listings:
                    continue
                
                for job in job_listings[:10]:  # Take 10 jobs per query
                    if not isinstance(job, dict):
                        continue
                    
                    title = html.unescape(job.get("job_title", ""))
                    company = html.unescape(job.get("employer_name", "Unknown"))
                    description = format_description_to_html(job.get("job_description", ""))
                    url = job.get("job_apply_link", "") or job.get("job_google_link", "")
                    posted_date = job.get("job_posted_at_datetime_utc", "")
                    
                    salary_min = job.get("job_min_salary")
                    salary_max = job.get("job_max_salary")
                    salary_currency = job.get("job_salary_currency", "USD")
                    salary_period = job.get("job_salary_period", "YEAR")
                    salary_is_estimated = job.get("job_salary_is_estimated", False)
                    
                    salary = format_salary(salary_min, salary_max, salary_currency, salary_period, is_estimated=salary_is_estimated)
                    
                    if not title or not url:
                        continue
                    
                    jobs.append({
                        "source": "jsearch",
                        "url": url,
                        "content": f"{title}|{company}|{description[:200] if description else ''}",
                        "posted_date": posted_date,
                        "description": description,
                        "salary": salary
                    })
                    
                    if len(jobs) >= 20:
                        break
                
                if len(jobs) >= 20:
                    break
                    
            except Exception as e:
                print(f"JSearch query error for '{query}': {e}")
                continue
        
        print(f"JSearch fetched {len(jobs)} jobs")
        return {"raw_jobs": state["raw_jobs"] + jobs}
    except Exception as e:
        print(f"JSearch error: {e}")
        return {"raw_jobs": state["raw_jobs"]}
