import requests
from bs4 import BeautifulSoup
from app.graph.state import RawJob, GraphState
from app.graph.teams.ingestion.job_filters import is_tech_job
from app.graph.teams.ingestion.description_formatter import format_description_to_html
import requests
import html
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
import re

# Specific company career pages - mix of AI, frontend, and general tech companies
COMPANY_PAGES = [
    # "https://boards.greenhouse.io/figma",
    # "https://jobs.ashbyhq.com/reddit",
    "https://job-boards.greenhouse.io/vercel",
    #"https://jobs.lever.co/openai",
    "https://boards.greenhouse.io/anthropic",
]

def fetch_job_details(job_url: str) -> tuple[str, str]:
    """Fetch job description and posted date from individual job page"""
    try:
        response = requests.get(job_url, timeout=10)
        if response.status_code != 200:
            return "", ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract description
        description = ""
        # Try common description selectors
        desc_selectors = [
            {"class": "content"},
            {"id": "content"},
            {"class": "job-description"},
            {"class": "description"},
            {"class": "posting-description"},
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.find("div", selector)
            if desc_elem:
                description = desc_elem.get_text(separator="\n", strip=True)
                break
        
        # If no description found, try to get any substantial text
        if not description:
            # Get main content area
            main = soup.find("main") or soup.find("article") or soup.find("body")
            if main:
                description = main.get_text(separator="\n", strip=True)
        
        # Format description with HTML tags
        if description:
            description = format_description_to_html(description)
        
        # Extract posted date
        posted_date = ""
        # Try to find date in common formats
        date_patterns = [
            r"Posted:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                posted_date = match.group(1)
                break
        
        return description, posted_date
        
    except Exception as e:
        print(f"  Error fetching job details from {job_url}: {e}")
        return "", ""

def ingest_company_pages(state: GraphState) -> dict:
    
    jobs: list[RawJob] = []

    for url in COMPANY_PAGES:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"Company page {url} returned status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract company name from URL and decode HTML entities
            if 'greenhouse' in url:
                company_name = html.unescape(url.split('/')[-1].title())
            elif 'ashbyhq' in url:
                company_name = html.unescape(url.split('/')[-1].title())
            else:
                company_name = html.unescape(url.split('//')[-1].split('/')[0].split('.')[0].title())
            
            # Try multiple selectors to find job listings
            job_links = []
            
            # Greenhouse selectors
            if 'greenhouse' in url:
                # Try new Greenhouse structure first (.job-post)
                sections = soup.select(".job-post")
                if not sections:
                    # Fallback to old structure (.opening)
                    sections = soup.select(".opening")
                print(f"  Found {len(sections)} job sections")
                for section in sections[:50]:  # Increased from 10 to 50
                    link = section.select_one("a")
                    if link:
                        href = link.get("href", "")
                        title = html.unescape(link.text.strip())
                        if title and len(title) > 5:  # Filter out empty/short titles
                            job_links.append((href, title))
                            if len(job_links) <= 3:  # Debug first 3
                                print(f"    Job: {title[:50]}... -> {href[:80]}...")
            
            # Ashby selectors
            elif 'ashbyhq' in url:
                links = soup.select("a[href*='/jobs/']")
                print(f"  Found {len(links)} job links")
                for link in links[:10]:
                    job_links.append((link.get("href", ""), html.unescape(link.text.strip())))
            
            # Generic selectors for other sites (including Anthropic)
            else:
                print(f"  Using generic selector for {company_name}")
                for link in soup.select("a")[:150]:
                    href = link.get("href", "")
                    text = link.text.strip()
                    # Expanded keywords for AI, frontend, web dev roles
                    if any(keyword in text.lower() for keyword in ['engineer', 'developer', 'scientist', 'analyst', 'manager', 'ai', 'frontend', 'web', 'prompt']) and len(text) > 15:
                        job_links.append((href, text))
                        if len(job_links) >= 15:
                            break
                print(f"  Found {len(job_links)} matching job links")
            
            # Process found job links
            for href, title in job_links:
                if title and len(title) > 10 and not any(skip in title.lower() for skip in ['our opportunity', 'life at', 'benefits', 'university', 'see open', 'view all']):
                    # Make URL absolute if relative
                    if href.startswith('/'):
                        base_url = '/'.join(url.split('/')[:3])
                        href = base_url + href
                    elif not href.startswith('http'):
                        continue
                    
                    # Fetch job details from individual page
                    description, posted_date = fetch_job_details(href)
                    
                    # Use description preview for content field
                    desc_preview = description[:200] if description else "Engineering position"
                    
                    jobs.append({
                        "source": "company",
                        "url": href,
                        "content": f"{title}|{company_name}|{desc_preview}",
                        "description": description,
                        "posted_date": posted_date
                    })
            
            print(f"Company page {company_name} fetched {len([j for j in jobs if company_name.lower() in j['content'].lower()])} jobs")
        except Exception as e:
            print(f"Company page {url} error: {e}")

    return {"raw_jobs": state["raw_jobs"] + jobs}
