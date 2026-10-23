"""
PathSense Backend: Database Seeder — CSV to SQLite Bridge
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Seeds the SQLite database (logs/pathsense.db) from the existing CSV audit log
so that all REST API endpoints (/heatmap, /analytics, /telemetry) serve real data.

Usage:
    python backend/seed_db.py
"""

import os
import sys
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from backend import database as db
from core.smoothness_index import SmoothnessIndexCalculator


def seed_from_csv(csv_path: str = None) -> int:
    """
    Reads the pathsense_audit_log.csv and inserts every record into
    the telemetry_logs SQLite table. Also creates anomaly_events for
    segments with hazard alerts.
    Returns the number of records inserted.
    """
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "logs", "pathsense_audit_log.csv")

    if not os.path.exists(csv_path):
        print(f"[Seeder] CSV file not found: {csv_path}")
        print("[Seeder] Run 'python -m inference.generate_demo_assets' first to generate demo data.")
        return 0

    df = pd.read_csv(csv_path)
    if df.empty:
        print("[Seeder] CSV file is empty.")
        return 0

    # Initialize (create tables if not exist)
    db.init_db()

    # Check if DB already has data
    existing = db.get_recent_telemetry(limit=1)
    if existing:
        print(f"[Seeder] Database already has {len(db.get_heatmap_records())} records.")
        print("[Seeder] Use --force to re-seed (will clear existing data first).")
        return len(db.get_heatmap_records())

    print(f"[Seeder] Seeding SQLite from {len(df)} CSV records...")

    inserted = 0
    anomaly_track_id = 1

    for _, row in df.iterrows():
        # Convert timestamp
        try:
            ts_val = float(row["timestamp"])
            ts_str = datetime.datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            ts_str = str(row["timestamp"])

        si = float(row.get("smoothness_index", 100.0))
        speed = float(row.get("speed_kmh", 40.0))
        status_label, _, _ = SmoothnessIndexCalculator.get_road_status(si)
        alert_dist = float(row.get("alert_distance_m",
                                    SmoothnessIndexCalculator.calculate_dynamic_alert_distance(speed)))

        anomalies = int(row.get("anomalies_detected", 0))
        hazard = bool(row.get("hazard_alert", False))

        # Determine zone name from coordinates
        lat = float(row.get("latitude", 26.8235))
        lon = float(row.get("longitude", 75.8742))
        zone = _determine_zone(lat, lon)

        record = {
            "timestamp": ts_str,
            "latitude": lat,
            "longitude": lon,
            "speed_kmh": speed,
            "smoothness_index": si,
            "road_status": str(row.get("road_status", status_label)),
            "anomalies_detected": anomalies,
            "hazard_alert": 1 if hazard else 0,
            "alert_distance_m": alert_dist,
            "zone_name": zone,
            "synced_to_cloud": 0
        }

        db.insert_telemetry(record)
        inserted += 1

        # Create anomaly events for hazard segments
        if hazard and si < 50.0:
            severity = "CRITICAL" if si < 30 else "MODERATE"
            class_name = "pothole" if si < 40 else "alligator_crack"
            db.insert_anomaly({
                "timestamp": ts_str,
                "track_id": anomaly_track_id,
                "class_name": class_name,
                "confidence": round(min(0.96, 0.70 + (50.0 - si) / 100.0), 2),
                "latitude": lat,
                "longitude": lon,
                "speed_kmh": speed,
                "severity": severity,
                "synced_to_cloud": 0
            })
            anomaly_track_id += 1

    print(f"[Seeder] Successfully seeded {inserted} telemetry records into SQLite!")
    print(f"[Seeder] Anomaly events created: {anomaly_track_id - 1}")
    return inserted


def force_reseed(csv_path: str = None) -> int:
    """Clears the database and re-seeds from CSV."""
    import sqlite3
    db.init_db()
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM telemetry_logs")
    cursor.execute("DELETE FROM anomaly_events")
    conn.commit()
    conn.close()
    print("[Seeder] Cleared existing database records.")

    # Temporarily bypass the existing-data check
    return _seed_fresh(csv_path)


def _seed_fresh(csv_path: str = None) -> int:
    """Internal: always seeds regardless of existing data."""
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "logs", "pathsense_audit_log.csv")

    if not os.path.exists(csv_path):
        print(f"[Seeder] CSV file not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    if df.empty:
        return 0

    db.init_db()
    inserted = 0
    anomaly_track_id = 1

    for _, row in df.iterrows():
        try:
            ts_val = float(row["timestamp"])
            ts_str = datetime.datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            ts_str = str(row["timestamp"])

        si = float(row.get("smoothness_index", 100.0))
        speed = float(row.get("speed_kmh", 40.0))
        status_label, _, _ = SmoothnessIndexCalculator.get_road_status(si)
        alert_dist = float(row.get("alert_distance_m",
                                    SmoothnessIndexCalculator.calculate_dynamic_alert_distance(speed)))
        anomalies = int(row.get("anomalies_detected", 0))
        hazard = bool(row.get("hazard_alert", False))
        lat = float(row.get("latitude", 26.8235))
        lon = float(row.get("longitude", 75.8742))
        zone = _determine_zone(lat, lon)

        record = {
            "timestamp": ts_str,
            "latitude": lat,
            "longitude": lon,
            "speed_kmh": speed,
            "smoothness_index": si,
            "road_status": str(row.get("road_status", status_label)),
            "anomalies_detected": anomalies,
            "hazard_alert": 1 if hazard else 0,
            "alert_distance_m": alert_dist,
            "zone_name": zone,
            "synced_to_cloud": 0
        }
        db.insert_telemetry(record)
        inserted += 1

        if hazard and si < 50.0:
            severity = "CRITICAL" if si < 30 else "MODERATE"
            class_name = "pothole" if si < 40 else "alligator_crack"
            db.insert_anomaly({
                "timestamp": ts_str,
                "track_id": anomaly_track_id,
                "class_name": class_name,
                "confidence": round(min(0.96, 0.70 + (50.0 - si) / 100.0), 2),
                "latitude": lat,
                "longitude": lon,
                "speed_kmh": speed,
                "severity": severity,
                "synced_to_cloud": 0
            })
            anomaly_track_id += 1

    print(f"[Seeder] Seeded {inserted} telemetry + {anomaly_track_id - 1} anomaly records.")
    return inserted


def _determine_zone(lat: float, lon: float) -> str:
    """Maps GPS coordinates to a human-readable zone name around SKIT Jaipur."""
    if lat > 26.826 and lon > 75.870:
        return "Mahal Road / Jagatpura"
    elif lat > 26.824 and lon > 75.872:
        return "Sector 7 Jagatpura (Pothole Zone)"
    elif lat < 26.820 and lon < 75.868:
        return "Ramnagariya Circle"
    elif lat > 26.821 and lat < 26.824 and lon < 75.867:
        return "SKIT Campus / Main Gate"
    else:
        return "SKIT / Jagatpura Link Road"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PathSense Database Seeder: CSV -> SQLite")
    parser.add_argument("--csv", type=str, default=None, help="Path to CSV audit log")
    parser.add_argument("--force", action="store_true", help="Clear existing data and re-seed")
    args = parser.parse_args()

    print("=" * 65)
    print("    PATHSENSE: DATABASE SEEDER (CSV -> SQLite Bridge)          ")
    print("=" * 65)

    if args.force:
        count = force_reseed(args.csv)
    else:
        count = seed_from_csv(args.csv)

    print(f"\nTotal records in database: {count}")
    print("=" * 65)
