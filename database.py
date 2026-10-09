"""SQLite storage for saved jobs and the most recently uploaded resume."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

DB_PATH = Path(os.environ.get("RESUME_MATCHER_DB", Path(__file__).with_name("resume_matcher.db")))


@contextmanager
def get_conn(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                company     TEXT,
                location    TEXT,
                url         TEXT,
                description TEXT NOT NULL,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS resume (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                filename    TEXT,
                parsed_json TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


# --- jobs -------------------------------------------------------------------

def add_job(title, company, location, url, description, db_path=DB_PATH) -> int:
    with get_conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO jobs (title, company, location, url, description) VALUES (?, ?, ?, ?, ?)",
            (title.strip(), company.strip(), location.strip(), url.strip(), description.strip()),
        )
        return cur.lastrowid


def update_job(job_id, title, company, location, url, description, db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute(
            "UPDATE jobs SET title=?, company=?, location=?, url=?, description=? WHERE id=?",
            (title.strip(), company.strip(), location.strip(), url.strip(), description.strip(), job_id),
        )


def delete_job(job_id, db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))


def get_jobs(db_path=DB_PATH) -> pd.DataFrame:
    with get_conn(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM jobs ORDER BY created_at DESC, id DESC", conn)


# --- resume -----------------------------------------------------------------

def save_resume(filename: str, parsed: dict, db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO resume (id, filename, parsed_json, uploaded_at) "
            "VALUES (1, ?, ?, CURRENT_TIMESTAMP)",
            (filename, json.dumps(parsed)),
        )


def load_resume(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT filename, parsed_json FROM resume WHERE id = 1").fetchone()
    if row is None:
        return None, None
    return row["filename"], json.loads(row["parsed_json"])


def clear_resume(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM resume")
