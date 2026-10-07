"""
PathSense Utilities: Generate Demo Audit Route & Realistic Telemetry
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Generates a complete, multi-segment audit dataset across SKIT Campus & Jagatpura roads,
creating realistic variations of:
  - Smooth newly paved stretches (SI 90-100)
  - Minor crack sections (SI 70-85)
  - Moderate patch repairs (SI 50-70)
  - Severe pothole clusters near Sector 7 & Ramnagariya Circle (SI 20-45)
"""

import os
import sys
import time
import math
import random
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.telemetry import TelemetryPoint, TelemetryLogger
from core.smoothness_index import SmoothnessIndexCalculator


def generate_full_skit_drive_log(output_dir: str = "logs", num_points: int = 180):
    logger = TelemetryLogger(log_dir=output_dir)
    # Remove old log if regenerating fresh demo drive
    if os.path.exists(logger.csv_path):
        os.remove(logger.csv_path)
    logger._init_csv()

    # Route around SKIT Jaipur
    # 1. SKIT Main Gate (Ramnagariya)
    # 2. Campus North Road
    # 3. Jagatpura Link Road
    # 4. Mahal Road (Paved stretch)
    # 5. Sector 7 Jagatpura (Severe pothole cluster)
    # 6. Central Spine Road
    # 7. Ramnagariya Circle (Rough patch)
    base_lat = 26.8220
    base_lon = 75.8640
    current_time = time.time() - (num_points * 1.5)
    
    unique_anomalies = 0

    print(f"[PathSense Demo Generator] Synthesizing full Jaipur drive ({num_points} telemetry segments)...")
    for i in range(num_points):
        # Progress parameter along loop [0, 2*pi]
        theta = (i / float(num_points)) * 2.0 * math.pi

        # Route coordinates around SKIT (approx 2.5 km circuit)
        lat = base_lat + 0.007 * math.sin(theta) + 0.001 * math.sin(3 * theta)
        lon = base_lon + 0.009 * (1.0 - math.cos(theta)) + 0.001 * math.cos(2 * theta)
        speed_kmh = 35.0 + 12.0 * math.sin(theta * 1.5) + random.uniform(-2.5, 2.5)
        heading = (math.degrees(theta) + 90.0) % 360.0

        # Create localized road condition zones:
        # Zone A: Sector 7 rough patch (around theta in [3.0, 4.2])
        # Zone B: Ramnagariya Circle pothole cluster (around theta in [5.0, 5.8])
        # Other zones: Well-maintained university & link roads
        if 3.0 <= theta <= 4.2:
            # Severe pothole sector
            smoothness_index = random.uniform(22.0, 48.0)
            road_status = "CRITICAL / SEVERE HAZARDS" if smoothness_index < 35 else "POOR / HIGH DAMAGE"
            hazard_alert = True
            if random.random() < 0.45:
                unique_anomalies += random.randint(1, 2)
        elif 5.0 <= theta <= 5.8:
            # Moderate wear / alligator cracking
            smoothness_index = random.uniform(52.0, 68.0)
            road_status = "FAIR / MODERATE DAMAGE"
            hazard_alert = random.random() < 0.3
            if random.random() < 0.3:
                unique_anomalies += 1
        elif 1.2 <= theta <= 1.8:
            # Minor longitudinal cracks
            smoothness_index = random.uniform(72.0, 84.0)
            road_status = "GOOD / MINOR WEAR"
            hazard_alert = False
        else:
            # Smooth newly asphalted road
            smoothness_index = random.uniform(88.0, 99.5)
            road_status = "EXCELLENT / SMOOTH"
            hazard_alert = False

        alert_distance = SmoothnessIndexCalculator.calculate_dynamic_alert_distance(speed_kmh)

        pt = TelemetryPoint(
            timestamp=float(current_time + i * 1.5),
            latitude=float(lat),
            longitude=float(lon),
            speed_kmh=float(round(speed_kmh, 1)),
            heading_deg=float(round(heading, 1)),
            smoothness_index=float(round(smoothness_index, 1)),
            road_status=str(road_status),
            anomalies_detected=int(unique_anomalies),
            hazard_alert=bool(hazard_alert),
            alert_distance_m=float(alert_distance)
        )
        logger.log(pt)

    print(f"[PathSense Demo Generator] Completed! {num_points} route records written to {logger.csv_path}")
    print(f"Total Unique Potholes/Cracks logged: {unique_anomalies}")


if __name__ == "__main__":
    generate_full_skit_drive_log()
