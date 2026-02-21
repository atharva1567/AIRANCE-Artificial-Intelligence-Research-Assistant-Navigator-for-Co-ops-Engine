# main.py

import json
import os
import time
from tabulate import tabulate
from selenium.webdriver.common.by import By

from job_fetcher import (
    fetch_all_jobs,
    init_driver,
    open_source_tabs
)

USERS_FILE = "users.json"
SAVED_JOBS_FILE = "saved_jobs.json"

# ==========================
# JSON STORAGE
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
# ACCOUNT SYSTEM
# ==========================

def create_account(users):
    print("\n=== Create Account ===")
    username = input("Enter username: ").strip()
    if username in users:
        print("❌ Username already exists.")
        return users

    password = input("Enter password: ").strip()
    users[username] = {"password": password}
    save_json(USERS_FILE, users)
    print(f"✅ Account created for {username}")
    return users


def login(users):
    print("\n=== Login ===")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if username in users and users[username]["password"] == password:
        print(f"✅ Welcome back, {username}!")
        return username

    print("❌ Invalid username or password.")
    return None

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

        # -------------------------
        # SEARCH JOBS
        # -------------------------

        if choice == "1":
            field = input("Internship Field: ").strip()
            location = input("Location: ").strip()
            job_type = input("Full-time/Co-op/Any: ").strip()

            print("\nOpening browser tabs...")
            open_source_tabs(field, location, job_type)

            print("Fetching job listings...\n")
            jobs = fetch_all_jobs(field, location, job_type)

            if not jobs:
                print("❌ No jobs found.")
                continue

            display_jobs_table(jobs, show_status=False)

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

        # -------------------------
        # VIEW SAVED JOBS
        # -------------------------

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

        # -------------------------
        # OPEN SAVED JOB
        # -------------------------
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

        # -------------------------
        # UPDATE STATUS
        # -------------------------

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

        # -------------------------
        # DELETE SAVED JOB(S)
        # -------------------------

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

        # -------------------------
        # LOGOUT
        # -------------------------
        elif choice == "6":
            break

# ==========================
# MAIN MENU
# ==========================

def main_menu():
    users = load_json(USERS_FILE, {})

    while True:
        print("\n=== AIRANCE - AI Internship Assistant ===")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            users = create_account(users)
        elif choice == "2":
            username = login(users)
            if username:
                user_session(username)
        elif choice == "3":
            print("Goodbye 👋")
            break

if __name__ == "__main__":
    main_menu()