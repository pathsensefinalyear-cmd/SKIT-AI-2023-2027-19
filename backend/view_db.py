"""
PathSense: SQLite Database Quick Viewer Utility
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Run via:
    python backend/view_db.py
"""

import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "pathsense.db")


def view_database():
    if not os.path.exists(DB_PATH):
        print(f"[Error] Database file not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("           PATHSENSE SQLITE DATABASE INSPECTION VIEWER             ")
    print("=" * 80)
    print(f"Database Location: {os.path.abspath(DB_PATH)}")
    print(f"Database Size    : {os.path.getsize(DB_PATH)} bytes")
    print("-" * 80)

    # Telemetry Logs Count
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs")
    tel_count = cursor.fetchone()[0]

    # Anomalies Count
    cursor.execute("SELECT COUNT(*) FROM anomaly_events")
    anom_count = cursor.fetchone()[0]

    print(f"Summary: {tel_count} Telemetry Records | {anom_count} Anomaly Events")
    print("-" * 80)
    print("RECENT TELEMETRY RECORDS (Last 10 Rows):")
    print("-" * 80)
    print(f"{'ID':<4} | {'Timestamp':<19} | {'GPS (Lat, Lon)':<22} | {'Speed':<8} | {'SI Score':<8} | {'Road Condition'}")
    print("-" * 80)

    cursor.execute("""
    SELECT id, timestamp, latitude, longitude, speed_kmh, smoothness_index, road_status
    FROM telemetry_logs
    ORDER BY id DESC LIMIT 10
    """)
    rows = cursor.fetchall()

    for r in rows:
        rid, ts, lat, lon, spd, si, status = r
        coords = f"{lat:.4f}, {lon:.4f}"
        print(f"{rid:<4} | {ts:<19} | {coords:<22} | {spd:<5.1f}kmh | {si:<6.1f} | {status}")

    print("=" * 80)
    conn.close()


if __name__ == "__main__":
    view_database()
