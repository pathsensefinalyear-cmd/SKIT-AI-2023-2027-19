"""
PathSense Backend: Google Firebase Cloud Realtime Synchronization Engine
Author: Vedic Baurasi, Soham Manocha, Sharafat Khan, Sourabh Nagar (SKIT Jaipur, CS-AI, 7th Sem)

Features:
    1. Zero-dependency Cloud Sync via Google Firebase Realtime Database REST API.
    2. Offline-First Architecture: Automatically caches telemetry points locally in
       an offline queue when cellular connectivity drops on Indian highways,
       and automatically drains/uploads when internet is restored.
    3. Real-Time Endpoints:
       - /live_vehicle.json : Current vehicle location, speed, SI score for live map tracking.
       - /hazards.json      : Critical pothole events for municipal repair dispatch.
       - /route_history.json: Full audit trail of surveyed roads.
"""

from __future__ import annotations
import os
import sys
import json
import time
import argparse
from typing import Dict, List, Optional, Any
import requests

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class FirebaseCloudSync:
    def __init__(self, config_path: Optional[str] = None):
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = config_path or os.path.join(self.config_dir, "firebase_config.json")
        self.queue_file = os.path.join(os.path.dirname(self.config_dir), "logs", "firebase_offline_queue.json")
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)

        self.config = self._load_config()
        self.database_url = self.config.get("database_url", "").rstrip("/")
        self.is_enabled = self.config.get("enabled", False)
        self.auth_token = self.config.get("auth_token", "")

        self.synced_count = 0
        self.failed_count = 0

    def _load_config(self) -> Dict[str, Any]:
        default_cfg = {
            "project_name": "pathsense-road-ai",
            "database_url": "https://pathsense-road-ai-default-rtdb.firebaseio.com/",
            "auth_token": "",
            "enabled": False,
            "offline_sync_batch_size": 25
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Firebase Sync] Warning: Error reading config ({e}). Using defaults.")
        return default_cfg

    def _get_url(self, path: str) -> str:
        clean_path = path.strip("/")
        url = f"{self.database_url}/{clean_path}.json"
        if self.auth_token:
            url += f"?auth={self.auth_token}"
        return url

    def push_point(self, point_dict: Dict[str, Any]) -> bool:
        """
        Pushes a single telemetry packet to Firebase.
        If offline or cloud disabled, appends to local offline queue.
        """
        if not self.is_enabled or not self.database_url:
            self._queue_offline(point_dict)
            return False

        try:
            # 1. Update Current Live Vehicle State (PUT overwrites latest location)
            live_url = self._get_url("live_vehicle")
            resp_live = requests.put(live_url, json=point_dict, timeout=2.5)

            # 2. If Critical Hazard (SI < 50 or hazard_alert True), log to hazards table
            if point_dict.get("hazard_alert", False) or point_dict.get("smoothness_index", 100) < 50.0:
                hazard_url = self._get_url("hazards")
                requests.post(hazard_url, json=point_dict, timeout=2.5)

            # 3. Append to Historical Route Trail
            history_url = self._get_url("route_history")
            requests.post(history_url, json=point_dict, timeout=2.5)

            self.synced_count += 1
            return True

        except Exception as e:
            # Connectivity dropped — save to offline queue for automatic retry
            self._queue_offline(point_dict)
            self.failed_count += 1
            return False

    def _queue_offline(self, point_dict: Dict[str, Any]):
        queue = []
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, "r", encoding="utf-8") as f:
                    queue = json.load(f)
            except Exception:
                queue = []

        queue.append(point_dict)
        # Cap queue at 1000 items to avoid file bloating
        if len(queue) > 1000:
            queue = queue[-1000:]

        try:
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2)
        except Exception as e:
            print(f"[Firebase Sync] Queue write error: {e}")

    def drain_offline_queue(self) -> int:
        """
        Uploads queued offline packets once internet connectivity is restored.
        """
        if not self.is_enabled or not os.path.exists(self.queue_file):
            return 0

        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                queue = json.load(f)
        except Exception:
            return 0

        if not queue:
            return 0

        print(f"[Firebase Sync] Attempting to drain {len(queue)} offline queued records...")
        successfully_synced = 0
        remaining = []

        for pt in queue:
            try:
                hist_url = self._get_url("route_history")
                r = requests.post(hist_url, json=pt, timeout=3.0)
                if r.status_code in [200, 201]:
                    successfully_synced += 1
                else:
                    remaining.append(pt)
            except Exception:
                remaining.append(pt)
                break  # Stop if network failed again

        # Save remaining failed items
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(remaining, f, indent=2)

        print(f"[Firebase Sync] Successfully synced {successfully_synced} items! Remaining in queue: {len(remaining)}")
        return successfully_synced

    def sync_local_csv(self, csv_path: str) -> int:
        """
        Reads local audit CSV log (e.g. 180 points from SKIT Jaipur) and uploads to Firebase.
        """
        if not os.path.exists(csv_path):
            print(f"[Firebase Sync] Error: CSV file '{csv_path}' not found.")
            return 0

        import pandas as pd
        df = pd.read_csv(csv_path)
        print(f"[Firebase Sync] Preparing to upload {len(df)} records from {csv_path} to Firebase...")

        uploaded = 0
        for _, row in df.iterrows():
            pt = {
                "timestamp": float(row["timestamp"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "speed_kmh": float(row["speed_kmh"]),
                "heading_deg": float(row["heading_deg"]),
                "smoothness_index": float(row["smoothness_index"]),
                "road_status": str(row["road_status"]),
                "anomalies_detected": int(row["anomalies_detected"]),
                "hazard_alert": bool(row["hazard_alert"]),
                "alert_distance_m": float(row["alert_distance_m"])
            }
            if self.push_point(pt):
                uploaded += 1

        print(f"[Firebase Sync] Batch sync finished! Uploaded: {uploaded} / {len(df)} (Queued offline: {len(df) - uploaded})")
        return uploaded

    def get_status(self) -> Dict[str, Any]:
        queue_len = 0
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, "r", encoding="utf-8") as f:
                    queue_len = len(json.load(f))
            except Exception:
                pass

        return {
            "enabled": self.is_enabled,
            "database_url": self.database_url,
            "offline_queued_items": queue_len,
            "total_synced_session": self.synced_count,
            "failed_attempts": self.failed_count
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PathSense Firebase Cloud Sync Manager")
    parser.add_argument("--status", action="store_true", help="Display Firebase connection & queue status")
    parser.add_argument("--sync-csv", type=str, default="logs/pathsense_audit_log.csv", help="Upload local CSV audit log to Firebase")
    parser.add_argument("--drain-queue", action="store_true", help="Retry uploading queued offline records")
    args = parser.parse_args()

    syncer = FirebaseCloudSync()

    if args.status:
        st_data = syncer.get_status()
        print("\n=======================================================")
        print("          PATHSENSE: FIREBASE CLOUD SYNC STATUS         ")
        print("=======================================================")
        print(f"Cloud Sync Enabled : {st_data['enabled']}")
        print(f"Target Database URL: {st_data['database_url']}")
        print(f"Offline Queued Items: {st_data['offline_queued_items']}")
        print(f"Synced this Session: {st_data['total_synced_session']}")
        print("=======================================================\n")
    elif args.drain_queue:
        syncer.drain_offline_queue()
    else:
        syncer.sync_local_csv(args.sync_csv)
