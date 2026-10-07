"""
PathSense Core: Geospatial Telemetry & GPS Tracking
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Handles:
    - GPS coordinates (Lat, Lon, Heading, Speed)
    - Realistic GPS route simulation around SKIT Jaipur / Jagatpura / Ramnagariya
    - Data persistence to CSV & JSON format for Firebase / Folium mapping
"""

import time
import math
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple


@dataclass
class TelemetryPoint:
    timestamp: float
    latitude: float
    longitude: float
    speed_kmh: float
    heading_deg: float
    smoothness_index: float
    road_status: str
    anomalies_detected: int
    hazard_alert: bool
    alert_distance_m: float


class GPSRouteSimulator:
    """
    Simulates a realistic vehicle route around Swami Keshvanand Institute of Technology (SKIT),
    Ramnagariya, and Jagatpura in Jaipur, Rajasthan.
    """
    # Key waypoints around SKIT Jaipur
    WAYPOINTS = [
        (26.8218, 75.8635),  # SKIT Main Gate / Ramnagariya Road
        (26.8232, 75.8648),  # College Campus North Border
        (26.8250, 75.8672),  # Jagatpura Link Road Junction
        (26.8275, 75.8710),  # Mahal Road Crossing
        (26.8240, 75.8735),  # Sector 7 Road (Rough patch with potholes)
        (26.8205, 75.8700),  # Central Spine Road Jagatpura
        (26.8180, 75.8660),  # Ramnagariya Circle
        (26.8218, 75.8635),  # Back to SKIT Entrance
    ]

    def __init__(self, base_speed_kmh: float = 38.0):
        self.base_speed = base_speed_kmh
        self.current_idx = 0
        self.sub_progress = 0.0

    def step(self, delta_sec: float = 0.1) -> Tuple[float, float, float, float]:
        """
        Advances route simulation.
        Returns: (lat, lon, speed_kmh, heading_deg)
        """
        p1 = self.WAYPOINTS[self.current_idx]
        next_idx = (self.current_idx + 1) % len(self.WAYPOINTS)
        p2 = self.WAYPOINTS[next_idx]

        # Calculate distance between points in meters
        dlat = (p2[0] - p1[0]) * 111000.0
        dlon = (p2[1] - p1[1]) * (111000.0 * math.cos(math.radians(p1[0])))
        total_dist = max(1.0, math.sqrt(dlat * dlat + dlon * dlon))

        # Vehicle speed with realistic fluctuations
        t = time.time()
        speed_kmh = max(15.0, self.base_speed + 8.0 * math.sin(t * 0.3) + 4.0 * math.cos(t * 0.8))
        dist_moved = (speed_kmh * 1000.0 / 3600.0) * delta_sec

        self.sub_progress += dist_moved / total_dist
        if self.sub_progress >= 1.0:
            self.sub_progress = 0.0
            self.current_idx = next_idx

        curr_lat = p1[0] + (p2[0] - p1[0]) * self.sub_progress
        curr_lon = p1[1] + (p2[1] - p1[1]) * self.sub_progress

        heading = math.degrees(math.atan2(dlon, dlat)) % 360.0
        return curr_lat, curr_lon, speed_kmh, heading


class TelemetryLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_path = os.path.join(self.log_dir, "pathsense_audit_log.csv")
        self.json_path = os.path.join(self.log_dir, "pathsense_live_feed.json")
        self.history: List[TelemetryPoint] = []

        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", encoding="utf-8") as f:
                f.write("timestamp,latitude,longitude,speed_kmh,heading_deg,smoothness_index,road_status,anomalies_detected,hazard_alert,alert_distance_m\n")

    def _point_to_dict(self, p: TelemetryPoint) -> dict:
        return {
            "timestamp": float(p.timestamp),
            "latitude": float(p.latitude),
            "longitude": float(p.longitude),
            "speed_kmh": float(p.speed_kmh),
            "heading_deg": float(p.heading_deg),
            "smoothness_index": float(p.smoothness_index),
            "road_status": str(p.road_status),
            "anomalies_detected": int(p.anomalies_detected),
            "hazard_alert": bool(p.hazard_alert),
            "alert_distance_m": float(p.alert_distance_m),
        }

    def log(self, point: TelemetryPoint):
        self.history.append(point)
        # Append to CSV
        with open(self.csv_path, "a", encoding="utf-8") as f:
            f.write(f"{float(point.timestamp):.2f},{float(point.latitude):.6f},{float(point.longitude):.6f},"
                    f"{float(point.speed_kmh):.1f},{float(point.heading_deg):.1f},{float(point.smoothness_index):.1f},"
                    f"\"{point.road_status}\",{int(point.anomalies_detected)},{bool(point.hazard_alert)},"
                    f"{float(point.alert_distance_m):.1f}\n")

        # Keep latest state in JSON for real-time frontend consumers / Firebase sync
        latest_data = {
            "current": self._point_to_dict(point),
            "recent_history": [self._point_to_dict(p) for p in self.history[-250:]]
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(latest_data, f, indent=2, default=lambda o: bool(o) if hasattr(o, '__bool__') else str(o))
