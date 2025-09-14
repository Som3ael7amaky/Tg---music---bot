# roles.py
import sqlite3
from typing import Optional

DB = "roles.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        user_id INTEGER PRIMARY KEY,
        role TEXT
    )
    """)
    conn.commit()
    conn.close()

def set_role(user_id: int, role: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("REPLACE INTO roles (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

def remove_role(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM roles WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_role(user_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def list_roles():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT user_id, role FROM roles")
    rows = c.fetchall()
    conn.close()
    return rows