from langgraph.graph import StateGraph
from typing import TypedDict, List, Optional
from app.agents.classifier import classify_jobs
from app.agents.validator import validate_jobs
from app.agents.ranker import rank_jobs
from concurrent.futures import ThreadPoolExecutor, as_completed

# Note: Using 'graph' module name to access the graph package subdirectory
import app.graph.state as graph_state
import app.graph.teams.ingestion.adzuna_agent as adzuna_module
import app.graph.teams.ingestion.jsearch_agent as jsearch_module
import app.graph.teams.ingestion.jobicy_agent as jobicy_module
from app.graph.teams.ingestion.role_classifier import infer_role

GraphState = graph_state.GraphState
RawJob = graph_state.RawJob
ingest_jsearch = jsearch_module.ingest_jsearch
ingest_adzuna = adzuna_module.ingest_adzuna
ingest_jobicy = jobicy_module.ingest_jobicy

def process_raw_jobs(state: GraphState):
    """Convert raw jobs to normalized format"""
    raw_jobs = state.get("raw_jobs", [])
    print(f"Processing {len(raw_jobs)} raw jobs")
    
    jobs = []
    for idx, raw_job in enumerate(raw_jobs):
        content = raw_job.get("content", "")
        url = raw_job.get("url", "")
        source = raw_job.get("source", "unknown")
        
        # Extract title and company from content (format: title|company|description)
        parts = content.split('|')
        title = parts[0][:100] if parts else "Unknown Position"
        company = parts[1] if len(parts) > 1 else "Unknown"
        content_for_role = '|'.join(parts) if parts else content
        
        # Infer role using centralized classifier
        role = infer_role(title, content_for_role)
        
        # Generate unique ID from source and URL or index
        job_id = f"{source}_{idx}" if not url else url
        
        # Convert Unix timestamps to ISO format, leave other formats as-is
        from datetime import datetime
        posted_date = raw_job.get("posted_date", "")
        if posted_date and isinstance(posted_date, int):
            # Convert Unix timestamp to ISO format
            try:
                posted_date = datetime.fromtimestamp(posted_date).isoformat()
            except (ValueError, OSError):
                posted_date = ""
        
        description = raw_job.get("description", "")
        salary = raw_job.get("salary", "")
        
        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": "Remote",
            "remote": True,
            "role": role,
            "source": source,
            "url": url,
            "posted_date": posted_date,
            "score": 1.0,
            "description": description,
            "salary": salary
        })
    
    print(f"Processed {len(jobs)} raw jobs into normalized format")
    print(f"Sample job: {jobs[0] if jobs else 'None'}")
    return {"jobs": jobs, "role": state.get("role")}

def classify(state):
    jobs = state.get("jobs", [])
    print(f"Classify received {len(jobs)} jobs")
    if not jobs:
        print("Warning: No jobs to classify")
        return {"jobs": []}
    result = classify_jobs(jobs, state.get("role"))
    print(f"Classify returned {len(result)} jobs")
    return {"jobs": result}

def validate(state):
    jobs = state.get("jobs", [])
    if not jobs:
        print("Warning: No jobs to validate")
        return {"jobs": []}
    
    # Show which jobs are being filtered before validation
    print("\n=== VALIDATION DETAILS ===")
    filtered_jobs = []
    for job in jobs:
        if job.get("role") == "other":
            filtered_jobs.append(job)
            print(f"❌ FILTERED: {job.get('title', 'Unknown')[:80]}")
            print(f"   Company: {job.get('company')} | Source: {job.get('source')}")
            print(f"   Reason: Title doesn't match tech keywords")
            print()
    
    validated = validate_jobs(jobs)
    filtered_count = len(jobs) - len(validated)
    
    if filtered_count > 0:
        print(f"\n✅ Validation filtered out {filtered_count} non-tech jobs")
        print(f"✅ Kept {len(validated)} tech jobs")
    print(f"Validation: {len(jobs)} -> {len(validated)} jobs")
    print("=== END VALIDATION ===\n")
    return {"jobs": validated}

def rank(state):
    jobs = state.get("jobs", [])
    if not jobs:
        print("Warning: No jobs to rank")
        return {"jobs": []}
    return {"jobs": rank_jobs(jobs)}

# Helper function to run a single ingestion source
def run_ingestion_source(source_name: str, ingestion_func, state: GraphState):
    """Run a single ingestion source and return results with source name"""
    try:
        result = ingestion_func(state)
        jobs = result.get("raw_jobs", state.get("raw_jobs", []))
        # Calculate jobs added by this source
        new_jobs = jobs[len(state.get("raw_jobs", [])):]
        return (source_name, new_jobs, None)
    except Exception as e:
        return (source_name, [], str(e))

# Aggregator function to combine all ingestion results
def aggregate_ingestion(state: GraphState):
    """Aggregate results from all ingestion agents in parallel"""
    initial_state = {"raw_jobs": [], "role": state.get("role")}
    all_jobs = []
    
    # Active ingestion sources
    ingestion_sources = [
        ("JSearch", ingest_jsearch),
        ("Adzuna", ingest_adzuna),
        ("Jobicy", ingest_jobicy),
    ]
    
    # Execute all ingestion sources in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_source = {
            executor.submit(run_ingestion_source, name, func, initial_state): name 
            for name, func in ingestion_sources
        }
        
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                name, jobs, error = future.result()
                
                if error:
                    print(f"{name} ingestion failed: {error}")
                else:
                    job_count = len(jobs)
                    all_jobs.extend(jobs)
                    total_count = len(all_jobs)
                    print(f"{name}: fetched {job_count} jobs (total: {total_count})")
                    
            except Exception as e:
                print(f"{source_name} failed to process results: {e}")
    
    total_jobs = len(all_jobs)
    print(f"Total raw jobs collected: {total_jobs}")
    
    return {"raw_jobs": all_jobs, "role": state.get("role")}

# Create the graph with proper state
graph = StateGraph(GraphState)

# Add nodes
graph.add_node("ingest", aggregate_ingestion)
graph.add_node("process", process_raw_jobs)
graph.add_node("classify", classify)
graph.add_node("validate", validate)
graph.add_node("rank", rank)

# Set up pipeline
graph.set_entry_point("ingest")
graph.add_edge("ingest", "process")
graph.add_edge("process", "classify")
graph.add_edge("classify", "validate")
graph.add_edge("validate", "rank")
graph.set_finish_point("rank")

job_graph = graph.compile()
