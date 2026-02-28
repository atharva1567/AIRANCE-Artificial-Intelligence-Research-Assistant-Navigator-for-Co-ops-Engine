# main.py

import json
import os
import time
import sqlite3
from tabulate import tabulate

import sys
import threading

from job_fetcher import (
    fetch_all_jobs,
    init_driver,
    open_source_tabs
)

from user import create_account, login
from database import init_db
from config import DB_FILE
from emailer import send_email

SAVED_JOBS_FILE = "saved_jobs.json"

# ==========================
# LOADING BAR
# ==========================

loading = False

def loading_bar(text):
    def animate():
        bar_length = 30
        pct = 0

        while loading:
            pct = min(pct + 2, 98)  # smoothly fill up to 98%
            filled = int((pct / 100) * bar_length)
            bar = "█" * filled + "-" * (bar_length - filled)
            sys.stdout.write(f"\r{text} [{bar}] {pct}%")
            sys.stdout.flush()
            time.sleep(0.05)

        # Final full bar at 100%
        pct = 100
        bar = "█" * bar_length
        sys.stdout.write(f"\r{text} [{bar}] {pct}%\n")
        sys.stdout.flush()

    t = threading.Thread(target=animate)
    t.start()
    return t

# ==========================
# JSON STORAGE (for saved jobs)
# ==========================

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ==========================
# HELPERS
# ==========================

def truncate(text, max_len=40):
    text = "" if text is None else str(text)
    return text if len(text) <= max_len else text[:max_len - 3] + "..."

def display_jobs_table(jobs, show_status=False):
    table = []
    for i, job in enumerate(jobs, start=1):
        row = [
            i,
            truncate(job.get("title", ""), 35),
            truncate(job.get("company", ""), 25),
            truncate(job.get("location", ""), 25),
            job.get("source", "")
        ]

        if show_status:
            row.append(job.get("status", ""))

        table.append(row)

    headers = ["#", "Title", "Company", "Location", "Source"]
    if show_status:
        headers.append("Status")

    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

# ==========================
# OPEN JOB IN BROWSER
# ==========================

def open_job_in_browser(job):
    driver = init_driver()
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(job["link"])
    time.sleep(2)

    print("\n=== Job Opened in Browser ===")
    print("You can view the full job details directly on the website.\n")

# ==========================
# SAVE USER PREFERENCES
# ==========================

def save_user_preferences(username, field, location, job_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO user_preferences (user_id, field, location, job_type)
        VALUES (
            (SELECT id FROM users WHERE username=?),
            ?, ?, ?
        )
    """, (username, field, location, job_type))

    conn.commit()
    conn.close()

# ==========================
# CHECK FOR NEW JOBS + EMAIL ALERT
# ==========================

def check_for_new_jobs(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Get user ID + email
    c.execute("SELECT id, email FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return

    user_id, user_email = row

    # Get saved preferences
    c.execute("SELECT field, location, job_type FROM user_preferences WHERE user_id=?", (user_id,))
    prefs = c.fetchone()

    if not prefs:
        conn.close()
        return  # No saved search yet

    field, location, job_type = prefs

    # Fetch jobs
    jobs = fetch_all_jobs(field, location, job_type)

    # Get previously seen job links
    c.execute("SELECT link FROM jobs WHERE user_id=?", (user_id,))
    seen_links = {row[0] for row in c.fetchall()}

    # Filter new jobs
    new_jobs = [job for job in jobs if job["link"] not in seen_links]

    if not new_jobs:
        conn.close()
        return  # No new jobs → no email

    # Save new jobs to DB
    for job in new_jobs:
        c.execute("""
            INSERT INTO jobs (title, company, location, source, link, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job["title"], job["company"], job["location"],
            job["source"], job["link"], user_id
        ))

    conn.commit()
    conn.close()

    # Build rows
    rows = ""
    for job in new_jobs:
        rows += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">{job['title']}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{job['company']}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{job['location']}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{job['source']}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                <a href="{job['link']}" style="color: #1a73e8;">View</a>
            </td>
        </tr>
        """

    # Professional HTML email
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background: #f7f7f7;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

            <h2 style="color: #4A4A4A; text-align: center; margin-bottom: 10px;">
                🔔 New Job Matches for You
            </h2>

            <p style="font-size: 15px; color: #555;">
                Based on your saved preferences:
            </p>

            <ul style="font-size: 15px; color: #333; line-height: 1.6;">
                <li><strong>Field:</strong> {field}</li>
                <li><strong>Location:</strong> {location}</li>
                <li><strong>Job Type:</strong> {job_type}</li>
            </ul>

            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">

            <h3 style="color: #333; margin-bottom: 10px;">📄 New Job Postings</h3>

            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Title</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Company</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Location</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Source</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Link</th>
                </tr>
                {rows}
            </table>

            <p style="font-size: 14px; color: #777; margin-top: 25px; text-align: center;">
                This message was sent automatically by AIRANCE Job Alerts.
            </p>

        </div>
    </div>
    """

    send_email(
        to_address=user_email,
        subject="New Job Postings for You",
        body=html
    )

    print(f"\n📧 New job postings emailed to {user_email}!\n")

# ==========================
# USER SESSION
# ==========================

def user_session(username):
    saved_jobs = load_json(SAVED_JOBS_FILE, [])

    while True:
        print(f"\n=== Welcome, {username} ===")
        print("1. Search Jobs")
        print("2. View Saved Jobs")
        print("3. Open Saved Job")
        print("4. Update Application Status")
        print("5. Delete Saved Job")
        print("6. Logout")

        choice = input("Choose an option (1-6): ").strip()

        # SEARCH JOBS
        if choice == "1":
            field = input("Internship Field: ").strip()
            location = input("Location: ").strip()
            job_type = input("Full-time/Co-op/Any: ").strip()

            # Save preferences for job alerts
            save_user_preferences(username, field, location, job_type)

            # Opening browser tabs (actually opens LinkedIn + Indeed)
            global loading
            loading = True
            t = loading_bar("Opening browser tabs")
            open_source_tabs(field, location, job_type)
            loading = False
            t.join()

            # Fetching job listings (scraping both sites)
            loading = True
            t = loading_bar("Fetching job listings")
            jobs = fetch_all_jobs(field, location, job_type)
            loading = False
            t.join()

            # Check for new jobs + email alert (only if new)
            check_for_new_jobs(username)

            if not jobs:
                print("❌ No jobs found.")
                continue

            display_jobs_table(jobs)

            while True:
                print("\nOptions:")
                print("• Enter job number to open in browser")
                print("• Enter 's' to save jobs")
                print("• Enter 'b' to go back")
                c = input("Choice: ").strip().lower()

                if c == "b":
                    break

                elif c == "s":
                    nums = input("Enter job numbers to save (comma-separated): ").split(",")
                    for n in nums:
                        try:
                            idx = int(n.strip()) - 1
                            if 0 <= idx < len(jobs):
                                saved_jobs.append({
                                    "username": username,
                                    **jobs[idx],
                                    "status": "Saved"
                                })
                        except:
                            pass
                    save_json(SAVED_JOBS_FILE, saved_jobs)
                    print("✅ Jobs saved.")

                else:
                    try:
                        idx = int(c) - 1
                        if 0 <= idx < len(jobs):
                            open_job_in_browser(jobs[idx])
                        else:
                            print("❌ Invalid job number.")
                    except:
                        print("❌ Invalid choice.")

        # VIEW SAVED JOBS
        elif choice == "2":
            user_jobs = [j for j in saved_jobs if j["username"] == username]
            if not user_jobs:
                print("❌ No saved jobs.")
                continue

            display_jobs_table(user_jobs, show_status=True)
            print("\nEnter job number to open, or 'b' to go back.")
            c = input("Choice: ").strip().lower()

            if c == "b":
                continue

            try:
                idx = int(c) - 1
                if 0 <= idx < len(user_jobs):
                    open_job_in_browser(user_jobs[idx])
                else:
                    print("❌ Invalid job number.")
            except:
                print("❌ Invalid input.")

        # OPEN SAVED JOB
        elif choice == "3":
            user_jobs = [j for j in saved_jobs if j["username"] == username]
            if not user_jobs:
                print("❌ No saved jobs.")
                continue

            display_jobs_table(user_jobs, show_status=True)
            print("\nEnter job number to open, or 'b' to go back.")
            job_idx = input("Choice: ").strip().lower()

            if job_idx == "b":
                continue

            try:
                idx = int(job_idx) - 1
                if 0 <= idx < len(user_jobs):
                    open_job_in_browser(user_jobs[idx])
                else:
                    print("❌ Invalid job number.")
            except:
                print("❌ Invalid input.")

        # UPDATE STATUS
        elif choice == "4":
            user_jobs = [j for j in saved_jobs if j["username"] == username]
            if not user_jobs:
                print("❌ No saved jobs.")
                continue

            display_jobs_table(user_jobs, show_status=True)
            print("\nEnter job number to update, or 'b' to go back.")
            job_idx = input("Choice: ").strip().lower()

            if job_idx == "b":
                continue

            try:
                idx = int(job_idx) - 1
                if 0 <= idx < len(user_jobs):
                    status = input("New status (Applied/Interviewed/Rejected/Offer): ").strip()
                    user_jobs[idx]["status"] = status
                    save_json(SAVED_JOBS_FILE, saved_jobs)
                    print("✅ Status updated.")
                else:
                    print("❌ Invalid job number.")
            except:
                print("❌ Invalid input.")

        # DELETE SAVED JOB(S)
        elif choice == "5":
            user_jobs = [j for j in saved_jobs if j["username"] == username]
            if not user_jobs:
                print("❌ No saved jobs.")
                continue

            display_jobs_table(user_jobs, show_status=True)
            print("\nEnter job numbers to delete (comma-separated), or 'b' to go back.")
            job_input = input("Choice: ").strip().lower()

            if job_input == "b":
                continue

            nums = job_input.split(",")
            deleted_any = False

            for n in nums:
                try:
                    idx = int(n.strip()) - 1
                    if 0 <= idx < len(user_jobs):
                        job_to_delete = user_jobs[idx]
                        if job_to_delete in saved_jobs:
                            saved_jobs.remove(job_to_delete)
                            deleted_any = True
                except:
                    pass

            if deleted_any:
                save_json(SAVED_JOBS_FILE, saved_jobs)
                print("🗑️ Selected jobs deleted.")
            else:
                print("❌ No valid job numbers entered.")

        # LOGOUT
        elif choice == "6":
            break

# ==========================
# MAIN MENU
# ==========================

def main_menu():
    init_db()

    while True:
        print("\n=== AIRANCE - AI Internship Assistant ===")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            print("\n=== Create Account ===")
            email = input("Enter email: ").strip()
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            success, message = create_account(email, username, password)
            print(message)

        elif choice == "2":
            print("\n=== Login ===")
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()

            user = login(email, password)
            if user:
                username = user[2]
                print(f"Welcome back, {username}!")
                user_session(username)
            else:
                print("Invalid email or password.")

        elif choice == "3":
            print("Goodbye 👋")
            break

if __name__ == "__main__":
    main_menu()
