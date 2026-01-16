import requests
from bs4 import BeautifulSoup
from app.graph.state import RawJob, GraphState

# Specific company career pages - mix of AI, frontend, and general tech companies
COMPANY_PAGES = [
    "https://boards.greenhouse.io/figma",
    "https://jobs.ashbyhq.com/reddit",
    "https://boards.greenhouse.io/vercel",
    "https://jobs.lever.co/openai",
    "https://www.anthropic.com/careers",
]

def ingest_company_pages(state: GraphState) -> dict:
    jobs: list[RawJob] = []

    for url in COMPANY_PAGES:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"Company page {url} returned status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract company name from URL
            if 'greenhouse' in url:
                company_name = url.split('/')[-1].title()
            elif 'ashbyhq' in url:
                company_name = url.split('/')[-1].title()
            else:
                company_name = url.split('//')[-1].split('/')[0].split('.')[0].title()
            
            # Try multiple selectors to find job listings
            job_links = []
            
            # Greenhouse selectors
            if 'greenhouse' in url:
                sections = soup.select(".opening")
                print(f"  Found {len(sections)} .opening sections")
                for section in sections[:10]:
                    link = section.select_one("a")
                    if link:
                        job_links.append((link.get("href", ""), link.text.strip()))
            
            # Ashby selectors
            elif 'ashbyhq' in url:
                links = soup.select("a[href*='/jobs/']")
                print(f"  Found {len(links)} job links")
                for link in links[:10]:
                    job_links.append((link.get("href", ""), link.text.strip()))
            
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
                    
                    jobs.append({
                        "source": "company",
                        "url": href,
                        "content": f"{title}|{company_name}|Engineering position"
                    })
            
            print(f"Company page {company_name} fetched {len([j for j in jobs if company_name.lower() in j['content'].lower()])} jobs")
        except Exception as e:
            print(f"Company page {url} error: {e}")

    return {"raw_jobs": state["raw_jobs"] + jobs}
