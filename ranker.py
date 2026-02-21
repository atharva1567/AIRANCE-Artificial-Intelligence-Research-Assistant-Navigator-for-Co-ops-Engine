def rank_jobs(jobs, resume_text):
    ranked = []
    for job in jobs:
        score = 0
        # Simple ranking by keyword match
        for skill in ["Python", "C++", "AI", "Data Analysis"]:
            if skill.lower() in resume_text.lower():
                score += 1
        ranked.append((score, job))
    ranked.sort(reverse=True, key=lambda x: x[0])
    return [job for score, job in ranked]
