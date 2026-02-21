# generator.py
def rank_jobs(jobs, resume_text=None):
    # For demo: prioritize by keyword matches
    ranked = []
    for job in jobs:
        score = 0
        if resume_text:
            score += sum(1 for skill in job.get("keywords", []) if skill.lower() in resume_text.lower())
        job['score'] = score
        ranked.append(job)
    ranked.sort(key=lambda x: x['score'], reverse=True)
    return ranked
