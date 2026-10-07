"""
PathSense Backend Automated Test Suite & Verification
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Runs end-to-end unit and integration tests across:
  - SQLite Database engine (ACID transactions, schema, indexing)
  - Starlette REST API endpoints (Health, Telemetry, Heatmap, Detect, Sync)
  - Mathematical Smoothness Index ($SI$) and dynamic stopping distance
  - Firebase offline-first synchronization engine
"""

import os
import sys
import json
import base64
import unittest
from io import BytesIO
from PIL import Image
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import database as db
from backend.api_server import app
from starlette.testclient import TestClient
from core.smoothness_index import SmoothnessIndexCalculator
from backend.firebase_sync import FirebaseCloudSync


class PathSenseBackendTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 65)
        print("    STARTING PATHSENSE BACKEND INTEGRATION & API TEST SUITE     ")
        print("=" * 65)
        cls.client = TestClient(app)

    def test_01_database_initialization_and_crud(self):
        """Verify SQLite tables, telemetry insertion, and anomaly logging."""
        print("[Test 01] Verifying SQLite database engine and schema...")
        db.init_db()

        # Insert sample telemetry
        sample_rec = {
            "latitude": 26.8228,
            "longitude": 75.8745,
            "speed_kmh": 45.0,
            "smoothness_index": 78.5,
            "road_status": "GOOD / MINOR DISTRESS",
            "anomalies_detected": 1,
            "hazard_alert": 0,
            "alert_distance_m": 22.5,
            "zone_name": "SKIT Main Gate Corridor"
        }
        rec_id = db.insert_telemetry(sample_rec)
        self.assertIsInstance(rec_id, int)
        self.assertGreater(rec_id, 0)

        # Query recent records
        recent = db.get_recent_telemetry(limit=5)
        self.assertGreaterEqual(len(recent), 1)
        self.assertEqual(recent[0]["zone_name"], "SKIT Main Gate Corridor")
        print("  --> SQLite CRUD Operations: PASSED [OK]")

    def test_02_api_health_endpoint(self):
        """Verify GET /api/v1/health returns complete academic and system metadata."""
        print("[Test 02] Verifying GET /api/v1/health endpoint...")
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "2.4.0")

        # Verify 7th Sem Academic Team Metadata
        academic = data["academic_context"]
        self.assertEqual(academic["milestone"], "7th Semester Minor Project")
        team = academic["team_members"]
        self.assertEqual(len(team), 4)
        self.assertEqual(team[0]["name"], "Sharafat Khan")
        self.assertEqual(team[1]["name"], "Soham Manocha")
        self.assertEqual(team[2]["name"], "Sourabh Nagar")
        self.assertEqual(team[3]["name"], "Vedic Baurasi")
        print("  --> Health Endpoint & Team Metadata: PASSED [OK]")

    def test_03_api_telemetry_ingest_and_heatmap(self):
        """Verify POST /api/v1/telemetry and GET /api/v1/heatmap."""
        print("[Test 03] Verifying Telemetry Ingest & Heatmap APIs...")
        payload = {
            "latitude": 26.8245,
            "longitude": 75.8720,
            "speed_kmh": 52.0,
            "anomalies_detected": 0
        }
        post_resp = self.client.post("/api/v1/telemetry", json=payload)
        self.assertEqual(post_resp.status_code, 201)
        self.assertEqual(post_resp.json()["status"], "success")

        # Query heatmap
        map_resp = self.client.get("/api/v1/heatmap")
        self.assertEqual(map_resp.status_code, 200)
        map_data = map_resp.json()
        self.assertIn("data", map_data)
        self.assertGreater(len(map_data["data"]), 0)
        print("  --> Telemetry Ingest & Heatmap: PASSED [OK]")

    def test_04_api_detect_endpoint_with_image(self):
        """Verify POST /api/v1/detect processes synthetic base64 image and computes SI."""
        print("[Test 04] Verifying AI Inference & Detection API...")
        # Create a tiny 320x240 synthetic road test image
        test_img = Image.new("RGB", (320, 240), color=(80, 80, 80))
        buf = BytesIO()
        test_img.save(buf, format="JPEG")
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

        detect_payload = {
            "speed_kmh": 38.0,
            "latitude": 26.8240,
            "longitude": 75.8735,
            "image_base64": b64_str,
            "return_hud": True
        }
        resp = self.client.post("/api/v1/detect", json=detect_payload)
        self.assertEqual(resp.status_code, 200)

        result = resp.json()
        self.assertEqual(result["status"], "success")
        self.assertIn("smoothness_index", result)
        self.assertIn("road_status", result)
        self.assertIn("alert_distance_m", result)
        self.assertIsNotNone(result["annotated_hud_base64"])
        print("  --> AI Edge Vision Detection Endpoint: PASSED [OK]")

    def test_05_smoothness_index_mathematics(self):
        """Verify Smoothness Index mathematical formula and dynamic stopping buffer."""
        print("[Test 05] Verifying Smoothness Index & Physics Equations...")
        calc = SmoothnessIndexCalculator()
        si_clean, _ = calc.compute_segment_si([], current_speed_kmh=60.0)
        self.assertEqual(si_clean, 100.0)

        from core.smoothness_index import RoadAnomaly
        anom = RoadAnomaly(track_id=1, class_name="pothole", confidence=0.9, bbox=(100, 100, 200, 200), rel_area=0.05, timestamp=1700000.0, speed_kmh=60.0)
        si_damaged, _ = calc.compute_segment_si([anom], current_speed_kmh=60.0)
        self.assertLess(si_damaged, 100.0)

        # Dynamic stopping distance physics
        dist_30 = SmoothnessIndexCalculator.calculate_dynamic_alert_distance(30.0)
        dist_60 = SmoothnessIndexCalculator.calculate_dynamic_alert_distance(60.0)
        self.assertGreater(dist_60, dist_30)
        print(f"  --> Math Validation: 30 km/h Alert: {dist_30:.1f}m | 60 km/h Alert: {dist_60:.1f}m: PASSED [OK]")

    def test_06_firebase_sync_resilience(self):
        """Verify Firebase sync engine operates cleanly in offline-first mode."""
        print("[Test 06] Verifying Firebase offline queue resilience...")
        syncer = FirebaseCloudSync()
        status = syncer.get_status()
        self.assertIn("enabled", status)
        self.assertIn("offline_queued_items", status)

        # Sync API endpoint
        sync_resp = self.client.post("/api/v1/sync")
        self.assertEqual(sync_resp.status_code, 200)
        print("  --> Firebase Offline-First Sync Engine: PASSED [OK]")


if __name__ == "__main__":
    unittest.main()
