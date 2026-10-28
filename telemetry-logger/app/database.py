"""SQLite storage for telemetry readings.

One table, no ORM magic: a sensor reading is a row with a sensor id,
a numeric value, a unit and a timestamp. The database file lives next
to the app so the whole system stays local and portable.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "telemetry.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sensor_time "
            "ON readings (sensor_id, recorded_at)"
        )


def insert_reading(sensor_id: str, value: float, unit: str, recorded_at: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO readings (sensor_id, value, unit, recorded_at)"
            " VALUES (?, ?, ?, ?)",
            (sensor_id, value, unit, recorded_at),
        )
        return cur.lastrowid


def fetch_recent(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM readings ORDER BY recorded_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_sensor_history(sensor_id: str, limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM readings WHERE sensor_id = ?"
            " ORDER BY recorded_at ASC LIMIT ?",
            (sensor_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_stats() -> dict:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        sensors = conn.execute(
            "SELECT sensor_id, unit, COUNT(*) AS count,"
            " MIN(value) AS min_value, MAX(value) AS max_value,"
            " AVG(value) AS avg_value"
            " FROM readings GROUP BY sensor_id, unit"
            " ORDER BY sensor_id"
        ).fetchall()
        latest = conn.execute(
            "SELECT * FROM readings WHERE id IN"
            " (SELECT MAX(id) FROM readings GROUP BY sensor_id)"
            " ORDER BY sensor_id"
        ).fetchall()
    return {
        "total_readings": total,
        "sensors": [dict(row) for row in sensors],
        "latest": [dict(row) for row in latest],
    }
