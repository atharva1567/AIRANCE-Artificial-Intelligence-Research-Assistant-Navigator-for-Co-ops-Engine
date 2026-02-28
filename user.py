# user.py

import sqlite3
import re
from database import init_db
from config import DB_FILE

init_db()

PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$"

def create_account(email, username, password):
    if not re.match(PASSWORD_REGEX, password):
        return False, "Password must be 8+ chars, 1 capital, 1 number, 1 special."

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
            (email, username, password)
        )
        conn.commit()
        return True, f"Account created for {username}!"
    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            return False, "Email already exists."
        if "username" in str(e):
            return False, "Username already exists."
        return False, "Account could not be created."
    finally:
        conn.close()


def login(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute(
        "SELECT id, email, username, password FROM users WHERE email=? AND password=?",
        (email, password)
    )
    user = c.fetchone()
    conn.close()
    return user
