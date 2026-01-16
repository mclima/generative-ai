import re

def is_english(text):
    """Check if text is primarily English by looking for common English words"""
    if not text or len(text) < 50:
        return True  # Allow short or empty descriptions
    
    # Convert to lowercase for checking
    text_lower = text.lower()
    
    # Common English words that should appear in job descriptions
    english_indicators = [
        'the', 'and', 'for', 'with', 'you', 'our', 'we', 'are', 'will', 'have',
        'experience', 'work', 'team', 'position', 'job', 'role', 'company',
        'skills', 'requirements', 'responsibilities', 'developer', 'engineer',
        'software', 'technical', 'technology', 'design', 'build', 'create'
    ]
    
    # Count how many English indicators appear
    matches = sum(1 for word in english_indicators if word in text_lower)
    
    # Very lenient - just need 2 common words
    return matches >= 2

def validate_jobs(jobs):
    required = {"id", "title", "company", "role"}
    validated = []
    
    for j in jobs:
        # Check required fields
        if not required.issubset(j):
            continue
            
        # Filter out non-tech jobs
        if j.get("role") == "other":
            continue
        
        # Language filtering disabled - too aggressive
        # TODO: Implement better language detection if needed
            
        validated.append(j)
    
    return validated
