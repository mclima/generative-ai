import httpx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import random
from app.config import settings

CATEGORIES = ["AI", "Engineering"]

# Shared list of required title keywords for tech job filtering
REQUIRED_TITLE_KEYWORDS = [
    "software engineer", "software developer", "backend engineer", "backend developer",
    "frontend engineer", "frontend developer", "front-end engineer", "front-end developer",
    "full stack engineer", "full stack developer", "fullstack engineer", "fullstack developer",
    "data engineer", "data scientist", "ml engineer", "ml developer", 
    "machine learning engineer", "ai engineer", "ai developer",
    "artificial intelligence engineer", "nlp engineer", "computer vision engineer",
    "ai agent developer", "genai agent engineer", "generative ai engineer", "agentic ai engineer",
    "ai software engineer", "applied ai engineer", "gen ai developer", "agentic ai architect",
    "prompt engineer", "ai/ml developer",
    "cloud engineer", "platform engineer", "infrastructure engineer",
    "web developer", "mobile developer", "ios developer", "android developer",
    "react developer", "python developer", "java developer", "javascript developer",
    "node.js developer", "golang developer", "ruby developer", ".net developer",
    "qa engineer", "test engineer", "automation engineer", "security engineer",
    "software architect", "technical architect",
    "engineering manager", "lead engineer", "principal engineer", "staff engineer",
    "senior software engineer", "senior frontend", "senior backend", "senior full stack",
    "senior ai engineer", "senior ml engineer",
    "research scientist", "applied scientist"
]

class JobAggregator:
    def __init__(self):
        self.jobs = []
    
    async def fetch_jobs(self) -> List[Dict]:
        jobs = []
        
        jobicy_jobs = await self._fetch_from_jobicy()
        print(f"Jobicy: Fetched {len(jobicy_jobs)} jobs")
        jobs.extend(jobicy_jobs)
        
        jsearch_jobs = await self._fetch_from_jsearch()
        print(f"JSearch: Fetched {len(jsearch_jobs)} jobs")
        jobs.extend(jsearch_jobs)
        
        jobs_api_jobs = await self._fetch_from_jobs_api()
        print(f"Jobs API: Fetched {len(jobs_api_jobs)} jobs")
        jobs.extend(jobs_api_jobs)
        
        print(f"Total before deduplication: {len(jobs)} jobs")
        unique_jobs = self._filter_and_normalize(jobs)
        print(f"Total after deduplication: {len(unique_jobs)} jobs")
        
        return unique_jobs
    
    async def _fetch_from_jobicy(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://jobicy.com/",
                    "Origin": "https://jobicy.com",
                }
                params = {
                    "count": 50,
                    "geo": "usa",
                }
                response = await client.get(
                    "https://jobicy.com/api/v2/remote-jobs",
                    params=params,
                    headers=headers,
                )

                if response.status_code != 200:
                    print(f"Jobicy API error: {response.status_code}")
                    return []

                data = response.json()
                if data.get("success") is False:
                    error = data.get("error") or data.get("message") or "Unknown error"
                    print(f"Jobicy API unsuccessful response: {error}")
                    return []

                jobs = data.get("jobs", [])
                return self._normalize_jobicy_jobs(jobs)
        except Exception as e:
            print(f"Error fetching from Jobicy: {e}")
        return []
    
    async def _fetch_from_jsearch(self) -> List[Dict]:
        if not settings.rapidapi_key:
            print("RapidAPI key not configured, skipping JSearch")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "X-RapidAPI-Key": settings.rapidapi_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }
                
                # Broad search for tech jobs in USA, remote only
                params = {
                    "query": "(software engineer OR software developer OR backend engineer OR frontend engineer OR full stack engineer OR data engineer OR data scientist OR machine learning engineer OR AI engineer OR generative AI OR LLM) in USA",
                    "page": "1",
                    "num_pages": "1",
                    "date_posted": "week",
                    "remote_jobs_only": "true"
                }
                
                response = await client.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get("data", [])
                    return self._normalize_jsearch_jobs(jobs)
                else:
                    print(f"JSearch API error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching from JSearch: {e}")
        return []
    
    async def _fetch_from_jobs_api(self) -> List[Dict]:
        if not settings.rapidapi_key:
            print("RapidAPI key not configured, skipping Jobs API")
            return []
        
        all_jobs = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "X-RapidAPI-Key": settings.rapidapi_key,
                    "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
                }
                
                # Query 1: Broad query to capture tech jobs
                # Fetch multiple pages (up to 3 pages = ~30 jobs)
                params = {
                    "query": "software engineer developer",
                    "location": "United States",
                    "workplaceTypes": "remote",
                    "employmentTypes": "fulltime",
                    "datePosted": "week"
                }
                
                for page in range(3):  # Fetch up to 3 pages
                    response = await client.get(
                        "https://jobs-api14.p.rapidapi.com/v2/linkedin/search",
                        headers=headers,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        jobs = data.get("data", [])
                        all_jobs.extend(jobs)
                        
                        # Check for next page token
                        next_token = data.get("meta", {}).get("nextToken")
                        if not next_token or len(jobs) == 0:
                            break
                        
                        # Use token for next page
                        params = {"token": next_token}
                        await asyncio.sleep(1)  # Rate limit between pages
                    else:
                        print(f"Jobs API error (general): {response.status_code}")
                        break
                
                # Wait 1 second to respect rate limit
                await asyncio.sleep(1)
                
                # Query 2: Targeted query for AI/ML roles
                # Fetch multiple pages (up to 3 pages = ~30 jobs)
                ai_params = {
                    "query": "AI machine learning engineer",
                    "location": "United States",
                    "workplaceTypes": "remote",
                    "employmentTypes": "fulltime",
                    "datePosted": "week"
                }
                
                for page in range(3):  # Fetch up to 3 pages
                    ai_response = await client.get(
                        "https://jobs-api14.p.rapidapi.com/v2/linkedin/search",
                        headers=headers,
                        params=ai_params
                    )
                    
                    if ai_response.status_code == 200:
                        ai_data = ai_response.json()
                        ai_jobs = ai_data.get("data", [])
                        all_jobs.extend(ai_jobs)
                        
                        # Check for next page token
                        next_token = ai_data.get("meta", {}).get("nextToken")
                        if not next_token or len(ai_jobs) == 0:
                            break
                        
                        # Use token for next page
                        ai_params = {"token": next_token}
                        await asyncio.sleep(1)  # Rate limit between pages
                    else:
                        print(f"Jobs API error (AI): {ai_response.status_code}")
                        break
                
                # Wait 1 second to respect rate limit
                await asyncio.sleep(1)
                
                # Query 3: Targeted query for Generative AI/LLM roles
                # Fetch multiple pages (up to 3 pages = ~30 jobs)
                genai_params = {
                    "query": "generative AI LLM engineer",
                    "location": "United States",
                    "workplaceTypes": "remote",
                    "employmentTypes": "fulltime",
                    "datePosted": "week"
                }
                
                for page in range(3):  # Fetch up to 3 pages
                    genai_response = await client.get(
                        "https://jobs-api14.p.rapidapi.com/v2/linkedin/search",
                        headers=headers,
                        params=genai_params
                    )
                    
                    if genai_response.status_code == 200:
                        genai_data = genai_response.json()
                        genai_jobs = genai_data.get("data", [])
                        all_jobs.extend(genai_jobs)
                        
                        # Check for next page token
                        next_token = genai_data.get("meta", {}).get("nextToken")
                        if not next_token or len(genai_jobs) == 0:
                            break
                        
                        # Use token for next page
                        genai_params = {"token": next_token}
                        await asyncio.sleep(1)  # Rate limit between pages
                    else:
                        print(f"Jobs API error (GenAI): {genai_response.status_code}")
                        break
                
                # Return jobs without descriptions for fast refresh
                # Descriptions will be fetched in background after refresh
                return self._normalize_jobs_api_jobs(all_jobs)
        except Exception as e:
            print(f"Error fetching from Jobs API: {e}")
        return []
    
    def _normalize_jobicy_jobs(self, jobs: List[Dict]) -> List[Dict]:
        normalized = []
        from datetime import timezone
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=8)
        total_jobs = len(jobs)
        filtered_by_date = 0
        filtered_by_keyword = 0
        
        for job in jobs:
            try:
                posted_date_str = job.get("pubDate", "")
                if not posted_date_str:
                    continue
                
                # Parse ISO format date
                posted_date = datetime.fromisoformat(posted_date_str.replace("Z", "+00:00"))
                
                if posted_date < one_week_ago:
                    filtered_by_date += 1
                    continue
                
                title = job.get("jobTitle", "")
                description = job.get("jobDescription", "")
                
                # Filter for tech jobs only - title must contain engineering/developer keywords
                title_lower = title.lower()
                is_tech_job = any(keyword in title_lower for keyword in REQUIRED_TITLE_KEYWORDS)
                
                if not is_tech_job:
                    filtered_by_keyword += 1
                    continue
                
                category = self._categorize_job(title, description)
                
                # Extract salary information if available
                salary = None
                if job.get("salary"):
                    salary = job.get("salary")
                elif job.get("annualSalaryMin") and job.get("annualSalaryMax"):
                    min_sal = job.get("annualSalaryMin")
                    max_sal = job.get("annualSalaryMax")
                    salary = f"${min_sal:,.0f} - ${max_sal:,.0f} USD/year"
                
                normalized.append({
                    "job_id": f"jobicy_{job.get('id', '')}",
                    "title": title,
                    "company": job.get("companyName", ""),
                    "location": job.get("jobGeo", "Remote (US)"),
                    "description": description,
                    "category": category,
                    "source": "Jobicy",
                    "posted_date": posted_date,
                    "salary": salary,
                    "apply_url": job.get("url", "")
                })
            except Exception as e:
                print(f"Error normalizing Jobicy job: {e}")
                continue

        if total_jobs > 0 and len(normalized) == 0:
            sample = jobs[0]
            print(
                "Jobicy returned jobs but all were filtered out. "
                f"total={total_jobs}, filtered_by_date={filtered_by_date}, filtered_by_keyword={filtered_by_keyword}, "
                f"sample_title={sample.get('jobTitle', '')[:80]!r}, sample_pubDate={sample.get('pubDate', '')!r}, sample_geo={sample.get('jobGeo', '')!r}"
            )
        
        return normalized
    
    def _normalize_jsearch_jobs(self, jobs: List[Dict]) -> List[Dict]:
        normalized = []
        from datetime import timezone
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=8)
        
        for job in jobs:
            try:
                # Parse date
                posted_date_timestamp = job.get("job_posted_at_timestamp")
                if not posted_date_timestamp:
                    continue
                
                posted_date = datetime.fromtimestamp(posted_date_timestamp, tz=timezone.utc)
                
                if posted_date < one_week_ago:
                    continue
                
                title = job.get("job_title", "")
                description = job.get("job_description", "")
                
                # Filter for tech jobs only - title must contain engineering/developer keywords
                title_lower = title.lower()
                is_tech_job = any(keyword in title_lower for keyword in REQUIRED_TITLE_KEYWORDS)
                
                if not is_tech_job:
                    continue
                
                # Check if it's remote
                is_remote = job.get("job_is_remote", False)
                if not is_remote:
                    continue
                
                category = self._categorize_job(title, description)
                
                # Get location
                location = "Remote (US)"
                if job.get("job_city") and job.get("job_state"):
                    location = f"Remote ({job.get('job_city')}, {job.get('job_state')})"
                
                # Extract salary information if available
                salary = None
                if job.get("job_min_salary") and job.get("job_max_salary"):
                    min_sal = job.get("job_min_salary")
                    max_sal = job.get("job_max_salary")
                    salary_period = job.get("job_salary_period", "YEAR")
                    currency = job.get("job_salary_currency", "USD")
                    salary = f"${min_sal:,.0f} - ${max_sal:,.0f} {currency}/{salary_period.lower()}"
                elif job.get("job_salary_period"):
                    salary = job.get("job_salary_period")
                
                normalized.append({
                    "job_id": f"jsearch_{job.get('job_id', '')}",
                    "title": title,
                    "company": job.get("employer_name", ""),
                    "location": location,
                    "description": description or job.get("job_highlights", {}).get("Qualifications", [""])[0],
                    "category": category,
                    "source": "JSearch",
                    "posted_date": posted_date,
                    "salary": salary,
                    "apply_url": job.get("job_apply_link", "")
                })
            except Exception as e:
                print(f"Error normalizing JSearch job: {e}")
                continue
        
        return normalized
    
    def _normalize_jobs_api_jobs(self, jobs: List[Dict]) -> List[Dict]:
        normalized = []
        from datetime import timezone
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=8)
        
        for job in jobs:
            try:
                # Parse date - LinkedIn API format: "2025-12-18"
                posted_date_str = job.get("datePosted", "")
                if not posted_date_str:
                    continue
                
                # Parse date string (YYYY-MM-DD format)
                # Since API only provides date (no time), use current time to avoid showing jobs as ~24 hours old
                date_only = datetime.strptime(posted_date_str, "%Y-%m-%d").date()
                now = datetime.now(timezone.utc)
                posted_date = datetime.combine(date_only, now.time(), tzinfo=timezone.utc)
                
                if posted_date < one_week_ago:
                    continue
                
                title = job.get("title", "")
                company = job.get("companyName", "")
                
                # Filter out AI/ML Developer from DataAnnotation
                if title.lower() == "ai/ml developer" and "dataannotation" in company.lower():
                    continue
                
                # Filter for tech jobs only - title must contain engineering/developer keywords
                title_lower = title.lower()
                is_tech_job = any(keyword in title_lower for keyword in REQUIRED_TITLE_KEYWORDS)
                
                if not is_tech_job:
                    continue
                
                # Use placeholder description - will be fetched in background after refresh
                description = job.get("description", "Description will be loaded shortly...")
                category = self._categorize_job(title, description)
                
                # Get location
                location = job.get("location", "Remote (US)")
                if not location or location == "":
                    location = "Remote (US)"
                
                # Extract salary information if available
                salary = None
                if job.get("salary"):
                    salary = job.get("salary")
                elif job.get("salaryRange"):
                    salary = job.get("salaryRange")
                
                normalized.append({
                    "job_id": f"jobsapi_{job.get('id', '')}",
                    "title": title,
                    "company": job.get("companyName", ""),
                    "location": location,
                    "description": description,
                    "category": category,
                    "source": "Jobs API",
                    "posted_date": posted_date,
                    "salary": salary,
                    "apply_url": job.get("linkedinUrl", "")
                })
            except Exception as e:
                print(f"Error normalizing Jobs API job: {e}")
                continue
        
        return normalized
    
    def _categorize_job(self, title: str, description: str) -> str:
        title_lower = title.lower()
        
        # AI keywords for categorization
        ai_keywords = [
            "machine learning", "artificial intelligence", "deep learning", "nlp", "computer vision", 
            "data scientist", "data science", "ai engineer", "ml engineer", "ml developer", "ai developer",
            "ai/ml", "machine learning engineer", "ml/ai", "applied scientist", "research scientist",
            "ai agent", "genai", "generative ai", "agentic ai", "llm engineer",
            "ai software engineer", "applied ai", "prompt engineer"
        ]
        
        # Simple categorization: AI or Engineering
        if any(keyword in title_lower for keyword in ai_keywords):
            return "AI"
        
        return "Engineering"
    
    def _filter_and_normalize(self, jobs: List[Dict]) -> List[Dict]:
        seen_ids = set()
        seen_jobs = set()  # Track (title, company) to catch duplicates across sources
        unique_jobs = []
        
        for job in jobs:
            job_signature = (job["title"].lower().strip(), job["company"].lower().strip())
            
            if job["job_id"] not in seen_ids and job_signature not in seen_jobs:
                seen_ids.add(job["job_id"])
                seen_jobs.add(job_signature)
                unique_jobs.append(job)
        
        return unique_jobs
