from app.graph.teams.ingestion.job_filters import TECH_KEYWORDS

NON_TECH_KEYWORDS = ['pharmacy', 'medical', 'nurse', 'doctor', 'retail', 'sales', 'customer service', 'warehouse']

AI_ML_KEYWORDS = [
    "ai engineer", "ai/ml engineer", "artificial intelligence engineer",
    "machine learning engineer", "ml engineer", "mlops engineer",
    "deep learning engineer", "nlp engineer", "computer vision engineer",
    "llm engineer", "prompt engineer", "ai trainer", "ml trainer",
    "ai researcher", "ml researcher", "ai scientist",
    "genai developer", "generative ai engineer", "ai/ml software engineer",
    "ai solutions engineer", "applied ai engineer", "ai architect",
    "agentic ai engineer", "ai developer",
    "data scientist", "data science", "data engineer", "data analyst", "machine learning"
]

FRONTEND_KEYWORDS = [
    "frontend engineer", "front-end engineer", "frontend developer", "front-end developer",
    "ui engineer", "ux engineer", "react developer", "vue developer", "angular developer",
    "javascript developer", "typescript developer", "web developer", "ui/ux engineer"
]

BACKEND_KEYWORDS = [
    "backend engineer", "back-end engineer", "backend developer", "back-end developer",
    "api engineer", "server engineer", "java developer", "python developer", "node developer",
    "golang developer", "ruby developer", ".net developer"
]

FULLSTACK_KEYWORDS = ["fullstack", "full-stack", "full stack"]
DEVOPS_KEYWORDS = ["devops", "sre", "site reliability", "infrastructure engineer", "cloud engineer", "platform engineer"]
MANAGEMENT_KEYWORDS = ["manager", "lead", "director"]

# Content-based indicators for when title is ambiguous
FRONTEND_CONTENT_INDICATORS = [
    "react", "vue", "angular", "frontend", "front-end", "ui", "ux", "css", "html",
    "javascript", "typescript", "next.js", "svelte", "tailwind", "responsive design",
    "web components", "dom", "browser"
]

BACKEND_CONTENT_INDICATORS = [
    "backend", "back-end", "api", "rest", "graphql", "database", "sql", "nosql",
    "server", "microservices", "kubernetes", "docker", "aws", "azure", "gcp",
    "node.js", "django", "flask", "spring", "express", "postgresql", "mongodb"
]

def infer_role(title: str, content: str = "") -> str:
    """
    Infer job role from title and content.
    Returns: 'other' for non-tech, or specific role like 'ai', 'frontend', 'backend', 'fullstack', 'devops', 'engineering'
    """
    title_lower = title.lower()
    content_lower = content.lower()
    
    # Check if it's a tech job
    is_tech = any(keyword in title_lower for keyword in TECH_KEYWORDS)
    is_non_tech = any(keyword in title_lower for keyword in NON_TECH_KEYWORDS)
    
    if not is_tech or is_non_tech:
        return "other"
    
    # Check for specific roles (prioritize specific over generic)
    if any(keyword in title_lower for keyword in AI_ML_KEYWORDS):
        return "ai"
    elif any(keyword in title_lower for keyword in FRONTEND_KEYWORDS):
        return "frontend"
    elif any(keyword in title_lower for keyword in BACKEND_KEYWORDS):
        return "backend"
    elif any(keyword in title_lower for keyword in FULLSTACK_KEYWORDS):
        return "fullstack"
    elif any(keyword in title_lower for keyword in DEVOPS_KEYWORDS):
        return "devops"
    
    # For generic "Software Engineer" or "Engineer" titles, check content
    generic_engineer_titles = ["software engineer", "engineer", "developer"]
    is_generic = any(title_lower.strip().endswith(keyword) or title_lower.startswith(keyword) 
                     for keyword in generic_engineer_titles)
    
    if is_generic and content_lower:
        # Count frontend vs backend indicators in content
        frontend_score = sum(1 for indicator in FRONTEND_CONTENT_INDICATORS if indicator in content_lower)
        backend_score = sum(1 for indicator in BACKEND_CONTENT_INDICATORS if indicator in content_lower)
        
        # If strong signal for frontend or backend, classify accordingly
        if frontend_score > backend_score and frontend_score >= 2:
            return "frontend"
        elif backend_score > frontend_score and backend_score >= 2:
            return "backend"
        elif frontend_score >= 2 and backend_score >= 2:
            return "fullstack"
    
    # Management roles
    if any(keyword in title_lower for keyword in MANAGEMENT_KEYWORDS):
        return "engineering"
    
    # Default for tech jobs
    return "engineering"
