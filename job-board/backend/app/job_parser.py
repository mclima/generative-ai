import json
from app.llm import llm_config

def parse_job_description(description: str) -> dict:
    """
    Use LLM to parse job description into structured sections.
    Returns dict with 'requirements' and 'responsibilities' as lists of strings.
    """
    if not description or len(description.strip()) < 50:
        return {"requirements": [], "responsibilities": []}
    
    prompt = f"""Parse this job description and extract two sections:
1. Requirements (skills, experience, qualifications needed)
2. Responsibilities (what the person will do in the role)

Return ONLY a JSON object with this exact structure:
{{
  "requirements": ["requirement 1", "requirement 2", ...],
  "responsibilities": ["responsibility 1", "responsibility 2", ...]
}}

Job Description:
{description}

Return valid JSON only, no other text."""

    try:
        llm = llm_config.get_llm()
        response = llm.invoke(prompt)
        
        # Extract JSON from response
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Try to find JSON object in content
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            content = content[start:end]
        
        # Try to parse JSON
        parsed = json.loads(content)
        
        # Validate structure
        if not isinstance(parsed.get("requirements"), list):
            parsed["requirements"] = []
        if not isinstance(parsed.get("responsibilities"), list):
            parsed["responsibilities"] = []
            
        return parsed
        
    except Exception as e:
        print(f"Error parsing job description: {e}")
        return {"requirements": [], "responsibilities": []}
