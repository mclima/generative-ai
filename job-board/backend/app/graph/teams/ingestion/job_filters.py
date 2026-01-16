"""Shared job filtering utilities for all ingestion agents"""

# Comprehensive tech keywords used across all job sources
TECH_KEYWORDS = [
    'engineer', 'developer', 'software', 'data', 'product', 'programmer', 'architect',
    'frontend', 'front-end', 'backend', 'full stack', 'fullstack',
    'web', 'ai', 'artificial intelligence', 'machine learning', 'ml',
    'deep learning', 'nlp', 'computer vision', 'llm', 'prompt',
    'data scientist', 'data science', 'data analyst', 'devops', 'sre', 'react', 'vue',
    'angular', 'javascript', 'typescript', 'python', 'java', 'node',
    'genai', 'generative ai', 'ai/ml', 'mlops', 'agentic ai',
    'ai trainer', 'ml trainer', 'data labeling', 'annotation specialist'
]

# Centralized search queries used by all job sources
# Reduced to avoid API rate limits - commented queries are covered by broader terms
SEARCH_QUERIES = [
    "software engineer",
    #"software developer",
    "data scientist",
    "machine learning",
    #"artificial intelligence"
    "ai engineer",
    "generative ai",
    "frontend developer",
    # "front-end developer",  # Duplicate of "frontend developer"
    # "frontend engineer",  # Covered by "frontend developer"
    # "front-end engineer",  # Duplicate
    #"backend developer",
    "web developer", 
    "full stack",
    "devops",
    # "react",  # Covered by "frontend developer"
    # "angular",  # Covered by "frontend developer"
    # "vue",  # Covered by "frontend developer"
    # "python",  # Covered by "backend developer"
    # "javascript",  # Covered by "frontend developer"
    # "node.js",  # Covered by "backend developer"
    # "cloud engineer",  # Covered by "devops"
    # "aws",  # Covered by "devops"
    # "kubernetes"  # Covered by "devops"
]

def is_tech_job(title: str, tags: list = None, categories: list = None, description: str = None) -> bool:
    """
    Check if a job matches tech/engineering criteria.
    
    Args:
        title: Job title (required)
        tags: List of job tags (optional)
        categories: List of job categories (optional)
        description: Job description (optional)
    
    Returns:
        True if job matches tech criteria, False otherwise
    """
    title_lower = title.lower()
    
    # Check title
    if any(keyword in title_lower for keyword in TECH_KEYWORDS):
        return True
    
    # Check tags
    if tags:
        for tag in tags:
            if any(keyword in tag.lower() for keyword in TECH_KEYWORDS):
                return True
    
    # Check categories
    if categories:
        for cat in categories:
            if any(keyword in cat.lower() for keyword in TECH_KEYWORDS):
                return True
    
    # Check description (optional, for more thorough filtering)
    if description:
        desc_lower = description.lower()
        if any(keyword in desc_lower for keyword in TECH_KEYWORDS):
            return True
    
    return False
