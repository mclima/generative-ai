from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import is_tech_job, SEARCH_QUERIES
from app.graph.teams.ingestion.salary_formatter import format_salary
from app.graph.teams.ingestion.html_formatter import format_html_description
import requests
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"

def fetch_adzuna_query(query: str) -> list:
    """Fetch jobs for a single search query"""
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 10,
        "what": query,
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(ADZUNA_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"Adzuna error for '{query}': {response.text[:200]}")
            return []
        
        data = response.json()
        results = data.get("results", [])
        
        jobs = []
        for job in results:
            title = job.get("title", "")
            company = job.get("company", {}).get("display_name", "Unknown")
            description_raw = job.get("description", "")
            
            # Format HTML description to plain text with structure
            description = format_html_description(description_raw)
            
            if is_tech_job(title, description=description):
                url = job.get("redirect_url", "")
                posted_date = job.get("created", "")
                
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                salary_is_predicted = job.get("salary_is_predicted", False)
                salary = format_salary(salary_min, salary_max, "$", "year", is_estimated=salary_is_predicted)
                
                jobs.append({
                    "source": "adzuna",
                    "url": url,
                    "content": f"{title}|{company}|{description[:200] if description else ''}",
                    "posted_date": posted_date,
                    "description": description,
                    "salary": salary
                })
        
        return jobs
    except Exception as e:
        print(f"Adzuna error for query '{query}': {e}")
        return []

def ingest_adzuna(state: GraphState) -> dict:
    """Fetch tech jobs from Adzuna API using parallel queries"""
    try:
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            print("Adzuna: API credentials not found in environment")
            return {"raw_jobs": state["raw_jobs"]}
        
        # Use centralized search queries
        search_queries = SEARCH_QUERIES
        
        all_jobs = []
        seen_urls = set()
        
        # Execute all queries in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_query = {executor.submit(fetch_adzuna_query, query): query for query in search_queries}
            
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    jobs = future.result()
                    
                    # Deduplicate and add to results
                    for job in jobs:
                        url = job.get("url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            all_jobs.append(job)
                            
                            if len(all_jobs) >= 25:
                                break
                    
                    if len(all_jobs) >= 25:
                        break
                        
                except Exception as e:
                    print(f"Adzuna failed to process results for '{query}': {e}")
        
        print(f"Adzuna fetched {len(all_jobs)} jobs")
        return {"raw_jobs": state["raw_jobs"] + all_jobs}
    except Exception as e:
        print(f"Adzuna error: {e}")
        return {"raw_jobs": state["raw_jobs"]}
