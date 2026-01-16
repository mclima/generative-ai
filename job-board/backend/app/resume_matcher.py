from typing import List, Dict, Optional
from app.llm.config import llm_config
import re

def extract_skills_from_resume(resume_text: str) -> Dict[str, any]:
    """Use LLM to extract skills and preferences from resume text"""
    llm = llm_config.get_llm()
    
    prompt = f"""Analyze this resume and extract the following information in a structured format:

1. Technical Skills (programming languages, frameworks, tools, technologies)
2. Years of Experience (estimate if not explicitly stated)
3. Preferred Roles - Based on job titles, projects, and expertise. Choose from: ai, frontend, backend, fullstack, data, devops
   - List roles in order of PRIMARY to SECONDARY expertise
   - Maximum 3 roles
4. Seniority Level (junior, mid-level, senior, staff, principal)
5. Key Strengths (3-5 main competencies)

Resume:
{resume_text}

Return your analysis in this exact JSON format:
{{
    "skills": ["skill1", "skill2", ...],
    "years_experience": number,
    "preferred_roles": ["primary_role", "secondary_role"],
    "seniority": "level",
    "strengths": ["strength1", "strength2", ...]
}}
"""
    
    try:
        response = llm.invoke(prompt)
        
        # Extract JSON from response
        import json
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            # Fallback: basic parsing
            return {
                "skills": [],
                "years_experience": 0,
                "preferred_roles": [],
                "seniority": "unknown",
                "strengths": []
            }
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return {
            "skills": [],
            "years_experience": 0,
            "preferred_roles": [],
            "seniority": "unknown",
            "strengths": []
        }


def match_jobs_to_resume(resume_data: Dict, jobs: List[Dict]) -> List[Dict]:
    """Match jobs to resume based on skills, experience, and role fit"""
    skills = [s.lower() for s in resume_data.get("skills", [])]
    preferred_roles = [r.lower() for r in resume_data.get("preferred_roles", [])]
    years_experience = resume_data.get("years_experience", 0)
    seniority = resume_data.get("seniority", "").lower()
    
    matched_jobs = []
    
    for job in jobs:
        score = 0
        matched_skills = []
        mismatch_reasons = []
        
        # Check job description for skill matches
        description = (job.get("description") or "").lower()
        title = (job.get("title") or "").lower()
        
        # Check for experience requirements
        experience_match = True
        if "10+ years" in description or "10 years" in description:
            if years_experience < 10:
                mismatch_reasons.append("requires 10+ years experience")
                score -= 40
                experience_match = False
        elif "7+ years" in description or "7 years" in description:
            if years_experience < 7:
                mismatch_reasons.append("requires 7+ years experience")
                score -= 30
                experience_match = False
            elif years_experience >= 7:
                score += 15  # Bonus for meeting requirement
        elif "5+ years" in description or "5 years" in description:
            if years_experience < 5:
                mismatch_reasons.append("requires 5+ years experience")
                score -= 20
                experience_match = False
            elif years_experience >= 5:
                score += 10
        elif "3+ years" in description or "3 years" in description:
            if years_experience < 3:
                mismatch_reasons.append("requires 3+ years experience")
                score -= 15
                experience_match = False
            elif years_experience >= 3:
                score += 10
        # Check for junior/entry level roles (0-4 years)
        elif any(phrase in description for phrase in ["0–4 years", "0-4 years", "1-3 years", "2-4 years", "entry level", "junior"]):
            if years_experience <= 6:  # Good fit for junior/mid roles
                score += 15  # Bonus for being in range
            # No penalty for being overqualified - experienced devs can apply anywhere
        
        # Check for leadership requirements
        if any(keyword in description for keyword in ["lead team", "manage team", "team lead", "engineering manager", "tech lead"]):
            if seniority not in ["senior", "staff", "principal", "lead"]:
                mismatch_reasons.append("requires leadership experience")
                score -= 25
        
        # Skill matching - count unique skill matches (case-insensitive and flexible)
        skill_match_count = 0
        description_lower = description.lower()
        title_lower = title.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            # Extract core skill name (remove parentheses, versions, etc.)
            core_skill = skill_lower.split('(')[0].strip()
            
            # Check if skill or core skill appears in description/title
            if (skill_lower in description_lower or skill_lower in title_lower or
                core_skill in description_lower or core_skill in title_lower):
                skill_match_count += 1
                matched_skills.append(skill)
        
        # Score based on skill matches (more generous)
        if len(skills) > 0:
            # Give more credit for having relevant skills
            skill_match_ratio = skill_match_count / len(skills)
            score += int(skill_match_ratio * 50)  # Base points from skill ratio
            
            # Additional points for absolute number of matches
            score += min(skill_match_count * 3, 30)  # Up to 30 bonus points
        
        # Role preference matching (strong preference for exact role match)
        job_role = (job.get("role") or "").lower()
        
        # Map common role variations to our role categories
        role_mappings = {
            "ai": ["ai", "machine learning", "ml", "deep learning", "nlp", "data scientist", "data science"],
            "frontend": ["frontend", "front-end", "react", "vue", "angular", "ui", "ux"],
            "backend": ["backend", "back-end", "api", "server"],
            "fullstack": ["fullstack", "full-stack", "full stack"],
            "devops": ["devops", "sre", "infrastructure", "cloud"],
            "data": ["data engineer", "data engineering", "etl", "pipeline"],
            "engineering": ["software engineer", "engineer", "developer", "programmer"]  # Generic engineering
        }
        
        # Check if any preferred role matches the job role category
        # Give higher weight to primary role (first in list)
        role_match_bonus = 0
        for idx, pref_role in enumerate(preferred_roles):
            pref_role_lower = pref_role.lower()
            
            # Direct match
            if job_role == pref_role_lower:
                role_match_bonus = 50 if idx == 0 else 30  # Primary role gets more points
                break
            
            # Special case: "engineering" jobs should match with most software roles
            if job_role == "engineering":
                if pref_role_lower in ["fullstack", "backend", "frontend", "devops"]:
                    role_match_bonus = 40 if idx == 0 else 25  # Slightly lower bonus for generic match
                    break
            
            # Check role mappings
            for category, variations in role_mappings.items():
                if job_role == category:
                    if any(var in pref_role_lower for var in variations):
                        role_match_bonus = 50 if idx == 0 else 30  # Primary role gets more points
                        break
            
            if role_match_bonus > 0:
                break
        
        score += role_match_bonus
        
        # Additional bonus for AI/ML jobs matching AI-specific skills
        if job_role == "ai":
            ai_ml_skills = ["pytorch", "tensorflow", "transformers", "bert", "gpt", "nlp", 
                           "machine learning", "deep learning", "neural network", "huggingface",
                           "scikit-learn", "sklearn", "keras", "llm", "ml"]
            ai_skill_matches = sum(1 for skill in skills if any(ai_skill in skill for ai_skill in ai_ml_skills))
            if ai_skill_matches >= 3:
                score += 20  # Bonus for strong AI/ML skill set
        
        # Seniority alignment
        if "senior" in title or "sr." in title:
            if seniority in ["senior", "staff", "principal"]:
                score += 10
            elif seniority in ["junior", "entry"]:
                score -= 15
                mismatch_reasons.append("seniority mismatch")
        elif "junior" in title or "entry" in title:
            if seniority in ["junior", "entry", "mid-level"]:
                score += 10
            # No penalty for senior applying to junior roles
        
        # Remote preference
        if job.get("remote") and "remote" in [s.lower() for s in resume_data.get("strengths", [])]:
            score += 5
        
        # Calculate final percentage (ensure it's between 0-100)
        match_percentage = max(0, min(100, score))
        
        # Only include jobs with 60% or higher match
        if match_percentage >= 60:
            matched_jobs.append({
                **job,
                "match_score": score,
                "matched_skills": matched_skills,
                "match_percentage": match_percentage,
                "mismatch_reasons": mismatch_reasons
            })
    
    # Sort by match score
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matched_jobs


def generate_match_explanation(job: Dict, resume_data: Dict) -> str:
    """Generate explanation for why a job matches"""
    reasons = []
    
    matched_skills = job.get("matched_skills", [])
    if matched_skills:
        skills_str = ", ".join(matched_skills[:3])
        reasons.append(f"Matches your skills: {skills_str}")
    
    job_role = job.get("role", "")
    if job_role in resume_data.get("preferred_roles", []):
        reasons.append(f"Aligns with your preferred role: {job_role}")
    
    if job.get("remote"):
        reasons.append("Remote position")
    
    if not reasons:
        reasons.append("General match based on your profile")
    
    return " • ".join(reasons)
