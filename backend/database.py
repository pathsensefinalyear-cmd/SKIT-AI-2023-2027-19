"""
PathSense Backend: SQLite Relational Database Engine
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team Members:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Provides persistent local storage for road telemetry, distress anomalies,
and municipal audit logs with ACID compliance and instant querying.
"""

import os
import sqlite3
import datetime
from typing import Dict, List, Any, Optional, Tuple


DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
DB_PATH = os.path.join(DB_DIR, "pathsense.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection to the local SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes database schema for telemetry and anomalies."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Road Telemetry Table (Time-Series)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        speed_kmh REAL NOT NULL,
        smoothness_index REAL NOT NULL,
        road_status TEXT NOT NULL,
        anomalies_detected INTEGER NOT NULL DEFAULT 0,
        hazard_alert INTEGER NOT NULL DEFAULT 0,
        alert_distance_m REAL NOT NULL,
        zone_name TEXT DEFAULT 'SKIT / Jagatpura',
        synced_to_cloud INTEGER NOT NULL DEFAULT 0
    )
    """)

    # 2. Individual Detected Anomalies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        track_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        speed_kmh REAL NOT NULL,
        severity TEXT NOT NULL,
        synced_to_cloud INTEGER NOT NULL DEFAULT 0
    )
    """)

    # 3. Create indices for high-speed geospatial and timestamp lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_logs (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_coords ON telemetry_logs (latitude, longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_class ON anomaly_events (class_name)")

    conn.commit()
    conn.close()


def insert_telemetry(record: Dict[str, Any]) -> int:
    """Inserts a single road telemetry record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    ts = record.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute("""
    INSERT INTO telemetry_logs (
        timestamp, latitude, longitude, speed_kmh, smoothness_index,
        road_status, anomalies_detected, hazard_alert, alert_distance_m, zone_name, synced_to_cloud
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ts,
        float(record.get("latitude", 26.8235)),
        float(record.get("longitude", 75.8742)),
        float(record.get("speed_kmh", 40.0)),
        float(record.get("smoothness_index", 100.0)),
        str(record.get("road_status", "EXCELLENT / SMOOTH")),
        int(record.get("anomalies_detected", 0)),
        1 if record.get("hazard_alert") else 0,
        float(record.get("alert_distance_m", 25.0)),
        str(record.get("zone_name", "SKIT / Jagatpura")),
        1 if record.get("synced_to_cloud") else 0
    ))

    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id


def insert_anomaly(event: Dict[str, Any]) -> int:
    """Inserts an anomaly event (pothole or crack)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    ts = event.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute("""
    INSERT INTO anomaly_events (
        timestamp, track_id, class_name, confidence, latitude, longitude, speed_kmh, severity, synced_to_cloud
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ts,
        int(event.get("track_id", 1)),
        str(event.get("class_name", "pothole")),
        float(event.get("confidence", 0.85)),
        float(event.get("latitude", 26.8235)),
        float(event.get("longitude", 75.8742)),
        float(event.get("speed_kmh", 40.0)),
        str(event.get("severity", "CRITICAL")),
        1 if event.get("synced_to_cloud") else 0
    ))

    ev_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ev_id


def get_recent_telemetry(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches most recent telemetry records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_heatmap_records() -> List[Dict[str, Any]]:
    """Returns geospatial records specifically for heatmap generation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, timestamp, latitude, longitude, smoothness_index, road_status, speed_kmh, anomalies_detected, hazard_alert
    FROM telemetry_logs
    ORDER BY id ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_analytics_summary() -> Dict[str, Any]:
    """Generates municipal aggregate analytics from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), AVG(smoothness_index), AVG(speed_kmh), SUM(anomalies_detected) FROM telemetry_logs")
    row = cursor.fetchone()
    total_records = row[0] or 0
    avg_si = round(row[1] or 100.0, 1)
    avg_speed = round(row[2] or 0.0, 1)
    total_anomalies = row[3] or 0

    cursor.execute("SELECT COUNT(*) FROM anomaly_events WHERE class_name LIKE '%pothole%'")
    pothole_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM anomaly_events WHERE class_name LIKE '%crack%'")
    crack_count = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_records": total_records,
        "average_smoothness_index": avg_si,
        "average_speed_kmh": avg_speed,
        "total_anomalies": total_anomalies,
        "potholes_logged": pothole_count,
        "cracks_logged": crack_count,
        "database_file": DB_PATH
    }


# Auto-initialize tables when module is imported
init_db()
