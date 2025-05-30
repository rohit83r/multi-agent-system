# utils/memory.py
from datetime import datetime
import sqlite3
import json
from threading import Lock

DB_FILE = 'memory.db'
_lock = Lock()

def _init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_agent ON logs(agent)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
        conn.commit()

_init_db()

def log_to_memory(agent, data):
    with _lock:  # ensure thread-safe writes
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO logs (timestamp, agent, data) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat() + "Z", agent, json.dumps(data))
            )
            conn.commit()

def fetch_all_logs():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        return c.fetchall()

def fetch_logs_by_agent(agent):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM logs WHERE agent = ? ORDER BY timestamp DESC", (agent,))
        return c.fetchall()

def fetch_logs_by_time_range(start_time, end_time):
    """
    Fetch logs between ISO8601 timestamps start_time and end_time.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT * FROM logs WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC",
            (start_time, end_time)
        )
        return c.fetchall()
