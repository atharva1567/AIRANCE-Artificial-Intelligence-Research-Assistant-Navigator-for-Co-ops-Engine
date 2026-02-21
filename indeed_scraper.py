# indeed_scraper.py
def fetch_indeed_jobs(field, location, remote_or_hybrid='Any', job_type='Any'):
    jobs = [
        {
            'title': f'{field} Co-op',
            'company': 'Indeed Corp',
            'location': location,
            'type': job_type if job_type != 'Any' else 'Co-op',
            'remote_or_hybrid': remote_or_hybrid if remote_or_hybrid != 'Any' else 'Remote',
            'link': 'https://www.indeed.com/viewjob?jk=123456789',
            'source': 'Indeed'
        },
        {
            'title': f'{field} Internship',
            'company': 'NextGen Tech',
            'location': location,
            'type': job_type if job_type != 'Any' else 'Co-op',
            'remote_or_hybrid': remote_or_hybrid if remote_or_hybrid != 'Any' else 'Hybrid',
            'link': 'https://www.indeed.com/viewjob?jk=987654321',
            'source': 'Indeed'
        }
    ]
    return jobs