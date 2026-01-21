from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import is_tech_job
from app.graph.teams.ingestion.html_formatter import format_html_description
from app.graph.teams.ingestion.description_formatter import format_description_to_html
import requests
import os
import html
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"

def ingest_jobicy(state: GraphState) -> dict:
    """Fetch tech jobs from Jobicy API - a remote-first job board with full job descriptions"""
    try:
        # Add headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://jobicy.com/",
            "Origin": "https://jobicy.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
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
            raw_title = job.get("jobTitle", "")
            title = html.unescape(raw_title)
            # Debug: print first job title to see encoding
            if job_list.index(job) == 0:
                print(f"DEBUG - Raw title from API: {raw_title}")
                print(f"DEBUG - After html.unescape: {title}")
            company = html.unescape(job.get("companyName", ""))
            location = job.get("jobGeo", "Remote")
            job_url = job.get("url", "")
            posted_date = job.get("pubDate", "")
            
            # Extract full job description (HTML format)
            job_description_html = job.get("jobDescription", "")
            
            # Convert HTML to plain text with better formatting
            if job_description_html:
                soup = BeautifulSoup(job_description_html, 'html.parser')
                
                # Add line breaks after block elements for better readability
                for br in soup.find_all('br'):
                    br.replace_with('\n')
                for p in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    p.insert_after('\n\n')
                for li in soup.find_all('li'):
                    li.insert_before('• ')
                    li.insert_after('\n')
                
                # Get text with preserved line breaks
                description_text = soup.get_text(separator=' ')
                
                # Clean up excessive whitespace while preserving line breaks
                lines = [line.strip() for line in description_text.split('\n')]
                description_text = '\n'.join(line for line in lines if line)
                
                # Format description with HTML tags
                description_text = format_description_to_html(description_text)
                
                # Limit to first 500 chars for content field
                description_preview = description_text[:500] if description_text else ""
            else:
                description_text = ""
                description_preview = ""
            
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
