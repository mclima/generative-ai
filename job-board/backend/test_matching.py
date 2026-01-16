#!/usr/bin/env python3
"""Test resume matching locally without API"""

import sys
sys.path.insert(0, '/Users/marialima/github/generative-ai/job-board/backend')

from app.resume_matcher import extract_skills_from_resume, match_jobs_to_resume
from repository import get_jobs

# Read resume
with open('/Users/marialima/github/generative-ai/job-board/test_frontend_resume.txt', 'r') as f:
    resume_text = f.read()

print("Extracting skills from resume...")
resume_data = extract_skills_from_resume(resume_text)

print(f"\nResume Analysis:")
print(f"  Skills: {len(resume_data['skills'])} - {resume_data['skills'][:5]}...")
print(f"  Preferred roles: {resume_data['preferred_roles']}")
print(f"  Seniority: {resume_data['seniority']}")
print(f"  Years experience: {resume_data['years_experience']}")

print(f"\nFetching jobs from database...")
all_jobs = get_jobs(limit=500)
print(f"Found {len(all_jobs)} jobs in database")

# Convert to dict format
jobs_list = [
    {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote": job.remote,
        "role": job.role,
        "source": job.source,
        "url": job.url,
        "posted_date": job.posted_date,
        "score": job.score,
        "description": job.description,
        "salary": job.salary
    }
    for job in all_jobs
]

print(f"\nMatching jobs to resume...")

# Temporarily lower threshold to see all scores
from app.resume_matcher import match_jobs_to_resume as original_match
import app.resume_matcher as matcher_module

# Get all jobs with scores (bypass threshold)
all_scored_jobs = []
for job in jobs_list:
    score = 0
    matched_skills = []
    
    description = (job.get("description") or "").lower()
    title = (job.get("title") or "").lower()
    job_role = (job.get("role") or "").lower()
    
    # Skill matching
    for skill in resume_data['skills']:
        skill_lower = skill.lower()
        core_skill = skill_lower.split('(')[0].strip()
        if (skill_lower in description or skill_lower in title or
            core_skill in description or core_skill in title):
            matched_skills.append(skill)
    
    skill_match_count = len(matched_skills)
    if skill_match_count > 0:
        score += min(skill_match_count * 5, 40)
        score += min(skill_match_count * 3, 30)
    
    # Role matching
    role_bonus = 0
    for idx, pref_role in enumerate(resume_data['preferred_roles']):
        pref_role_lower = pref_role.lower()
        if job_role == pref_role_lower:
            role_bonus = 50 if idx == 0 else 30
            break
        if job_role == "engineering" and pref_role_lower in ["fullstack", "backend", "frontend", "devops"]:
            role_bonus = 40 if idx == 0 else 25
            break
    
    score += role_bonus
    match_percentage = max(0, min(100, score))
    
    all_scored_jobs.append({
        'title': job['title'],
        'role': job_role,
        'score': score,
        'match_percentage': match_percentage,
        'skill_count': skill_match_count,
        'role_bonus': role_bonus,
        'matched_skills': matched_skills
    })

# Sort by score
all_scored_jobs.sort(key=lambda x: x['score'], reverse=True)

print(f"\n{'='*60}")
print(f"TOP 10 JOBS BY SCORE (showing all scores):")
print(f"{'='*60}")
for i, job in enumerate(all_scored_jobs[:10], 1):
    print(f"\n{i}. {job['title'][:60]}")
    print(f"   Role: {job['role']} | Score: {job['score']} | Match %: {job['match_percentage']}%")
    print(f"   Skills: {job['skill_count']}/{len(resume_data['skills'])} | Role bonus: {job['role_bonus']}")
    if job['matched_skills']:
        print(f"   Matched: {', '.join(job['matched_skills'][:5])}")

matched_jobs = match_jobs_to_resume(resume_data, jobs_list)

print(f"\n{'='*60}")
print(f"ACTUAL RESULTS (60% threshold): {len(matched_jobs)} matches found")
print(f"{'='*60}")
