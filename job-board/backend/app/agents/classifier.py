def classify_jobs(jobs, role):
    if not role:
        return jobs
    return [j for j in jobs if role.lower() in j["role"].lower()]
