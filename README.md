# AIRANCE Artificial Intelligence Research Assistant Navigator for Co-ops Engine
AIRANCE (Artificial Intelligence Research Assistant Navigator for Co‑ops Engine) is a full‑stack, terminal‑based job‑search automation system designed for students and early‑career engineers. It combines real‑time web scraping, personalized job‑alert intelligence, and a clean account‑based workflow to help users discover internships, co‑ops, and full‑time roles faster and more efficiently.

AIRANCE automatically logs into LinkedIn, scrapes both LinkedIn and Indeed for fresh postings, displays results in a structured table, and lets users save jobs, track application status, and open listings directly in the browser. Each user has a personal account with a saved search profile (field, location, job type), enabling AIRANCE to detect new postings that match their preferences.

AIRANCE also generates a polished, professional HTML report and emails it directly to the user’s real email address using a secure Gmail App Password. This transforms AIRANCE from a simple scraper into a proactive job‑alert engine—similar to LinkedIn Job Alerts, but fully customizable and running locally.

# Key Features

**Account System with SQLite:**  
Users create accounts with real emails, enabling personalized job tracking and email alerts.

Automated LinkedIn Login:  
AIRANCE logs into LinkedIn programmatically to access full job listings.

Real‑Time Scraping (LinkedIn + Indeed):  
Fetches fresh postings based on field, location, and job type.

Saved Search Profiles:  
AIRANCE remembers each user’s preferences and uses them to detect new postings.

New‑Job Detection Engine:  
Compares newly scraped jobs against previously seen ones to identify only fresh opportunities.

Professional HTML Email Reports:  
Sends polished, LinkedIn‑style job‑alert emails from airance@gmail.com with:

- Job titles
- Companies
- Locations
- Sources
- Direct apply links
- Clean, responsive formatting

Job Management Tools:  
Save jobs, update application status, delete entries, and open listings in the browser.

Terminal‑Based UI:  
Clean, simple, and fast—optimized for developers and students.
