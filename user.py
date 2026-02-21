# user.py
import sqlite3
from database import init_db
from config import DB_FILE
import re

init_db()

def create_account(email, username, password):
    if not re.match(r"^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$", password):
        return False, "Password must be 8+ chars, 1 capital, 1 number, 1 special."
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
        conn.commit()
        return True, f"Account created for {username}!"
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    finally:
        conn.close()

def login(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        return True, {"id": user[0], "email": user[1], "username": user[2]}
    else:
        return False, "Invalid email or password."

def save_job(user_id, title, company, location, source, link):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO jobs (title, company, location, source, link, user_id) VALUES (?, ?, ?, ?, ?, ?)",
              (title, company, location, source, link, user_id))
    conn.commit()
    conn.close()

def get_saved_jobs(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, company, location, source, link, status FROM jobs WHERE user_id=?", (user_id,))
    jobs = c.fetchall()
    conn.close()
    return jobs

def update_job_status(job_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_id))
    conn.commit()
    conn.close()