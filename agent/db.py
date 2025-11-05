# agent/db.py
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path.home() / ".activity_tracker" / "activity.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_schema = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    type TEXT NOT NULL,          -- "window", "website", "terminal", "idle"
    title TEXT,
    detail TEXT,
    duration INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_ts ON events(ts);
"""

_lock = threading.Lock()

@contextmanager
def conn():
    with _lock:
        con = sqlite3.connect(str(DB_PATH), timeout=30)
        try:
            yield con
            con.commit()
        finally:
            con.close()

def init_db():
    with conn() as c:
        c.executescript(_schema)

def insert_event(ts, typ, title=None, detail=None, duration=0):
    with conn() as c:
        c.execute(
            "INSERT INTO events (ts, type, title, detail, duration) VALUES (?, ?, ?, ?, ?)",
            (int(ts), typ, title, detail, int(duration))
        )
        return c.lastrowid

def update_last_event_duration(event_id, duration):
    """Atualiza a duração de um evento existente"""
    with conn() as c:
        c.execute(
            "UPDATE events SET duration = ? WHERE id = ?",
            (int(duration), event_id)
        )

def fetch_events(start_ts=None, end_ts=None, limit=1000):
    q = "SELECT id, ts, type, title, detail, duration FROM events"
    params = []
    if start_ts is not None or end_ts is not None:
        q += " WHERE"
        conds = []
        if start_ts is not None:
            conds.append(" ts >= ? ")
            params.append(int(start_ts))
        if end_ts is not None:
            conds.append(" ts <= ? ")
            params.append(int(end_ts))
        q += " AND ".join(conds)
    q += " ORDER BY ts ASC LIMIT ?"
    params.append(limit)
    with conn() as c:
        cur = c.execute(q, params)
        return cur.fetchall()
