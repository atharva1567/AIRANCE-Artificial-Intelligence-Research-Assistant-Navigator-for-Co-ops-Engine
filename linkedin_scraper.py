# linkedin_scraper.py
def fetch_linkedin_jobs(field, location, remote_or_hybrid='Any', job_type='Any'):
    # Simulated job data
    jobs = [
        {
            'title': f'{field} Co-op',
            'company': 'LinkedIn Corp',
            'location': location,
            'type': job_type if job_type != 'Any' else 'Co-op',
            'remote_or_hybrid': remote_or_hybrid if remote_or_hybrid != 'Any' else 'Remote',
            'link': 'https://www.linkedin.com/jobs/view/123456789/',
            'source': 'LinkedIn'
        },
        {
            'title': f'{field} Internship',
            'company': 'Tech Innovators Inc.',
            'location': location,
            'type': job_type if job_type != 'Any' else 'Co-op',
            'remote_or_hybrid': remote_or_hybrid if remote_or_hybrid != 'Any' else 'Hybrid',
            'link': 'https://www.linkedin.com/jobs/view/987654321/',
            'source': 'LinkedIn'
        }
    ]
    return jobs