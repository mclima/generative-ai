def rank_jobs(jobs):
    for j in jobs:
        j["score"] = 1.0
    return sorted(jobs, key=lambda x: x["score"], reverse=True)
