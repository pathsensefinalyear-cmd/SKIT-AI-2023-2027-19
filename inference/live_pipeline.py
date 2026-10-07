"""
PathSense Inference: Live Edge Dashcam Processing Pipeline
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Usage:
    python -m inference.live_pipeline --mode demo --fps 25 --duration 20
    python -m inference.live_pipeline --video my_dashcam.mp4
    python -m inference.live_pipeline --camera 0
"""

from __future__ import annotations
import os
import sys
import time
import argparse
from typing import Optional, Tuple, List, Dict, Any
import numpy as np
from PIL import Image, ImageDraw

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.detector import RoadAnomalyDetector
from core.tracker import RoadAnomalyTracker
from core.smoothness_index import SmoothnessIndexCalculator, RoadAnomaly
from core.telemetry import GPSRouteSimulator, TelemetryLogger, TelemetryPoint
from inference.hud_overlay import draw_hud


def generate_synthetic_road_frame(width: int = 1280, height: int = 720, step_count: int = 0) -> np.ndarray:
    """
    Generates a realistic synthetic road perspective with asphalt texture,
    lane markings, and horizon line for testing and demo purposes.
    """
    img = Image.new("RGB", (width, height), (35, 42, 54))
    draw = ImageDraw.Draw(img)

    # Sky & Horizon (Top 45%)
    horizon_y = int(height * 0.45)
    draw.rectangle([0, 0, width, horizon_y], fill=(135, 170, 205))

    # Distant urban horizon / Jaipur landscape skyline
    draw.rectangle([0, horizon_y - 30, width, horizon_y], fill=(90, 110, 130))

    # Road surface (Dark Asphalt)
    draw.polygon([(int(width * 0.42), horizon_y), (int(width * 0.58), horizon_y),
                  (width + 100, height), (-100, height)], fill=(45, 48, 55))

    # Left and Right road shoulders (Sandy Indian roadside / curb)
    draw.polygon([(0, horizon_y), (int(width * 0.42), horizon_y), (-100, height), (0, height)], fill=(160, 140, 110))
    draw.polygon([(int(width * 0.58), horizon_y), (width, horizon_y), (width, height), (width + 100, height)], fill=(160, 140, 110))

    # Center Dashed Lane Markings (animated movement)
    offset = (step_count * 8) % 60
    for y in range(horizon_y + 10 + offset, height, 60):
        # Perspective scaling
        progress = (y - horizon_y) / (height - horizon_y)
        w_dash = max(3, int(progress * 16))
        h_dash = max(6, int(progress * 35))
        center_x = width // 2
        draw.rectangle([center_x - w_dash // 2, y, center_x + w_dash // 2, y + h_dash], fill=(235, 235, 240))

    return np.array(img)


class LiveDashcamPipeline:
    def __init__(self, model_path: Optional[str] = None, output_dir: str = "logs"):
        self.detector = RoadAnomalyDetector(model_path=model_path)
        self.tracker = RoadAnomalyTracker(iou_threshold=0.35)
        self.si_calculator = SmoothnessIndexCalculator(alpha=0.45)
        self.gps_sim = GPSRouteSimulator(base_speed_kmh=42.0)
        self.logger = TelemetryLogger(log_dir=output_dir)

    def process_frame(
        self,
        frame_rgb: np.ndarray,
        timestamp: float,
        simulated_time: Optional[float] = None
    ) -> Tuple[np.ndarray, TelemetryPoint]:
        # 1. Edge Object Detection
        raw_detections = self.detector.detect(frame_rgb, simulated_time=simulated_time)

        # 2. IoU Tracking & Deduplication
        tracked_detections = self.tracker.update(raw_detections)

        # 3. Telemetry & Vehicle Dynamics
        lat, lon, speed_kmh, heading = self.gps_sim.step(delta_sec=0.1)

        # 4. Prepare RoadAnomaly objects for Smoothness Index computation
        frame_shape = (frame_rgb.shape[0], frame_rgb.shape[1])
        anomaly_objects = []
        for det in tracked_detections:
            rel_area = self.si_calculator.calculate_relative_area(det["bbox"], frame_shape)
            anomaly_objects.append(RoadAnomaly(
                track_id=det["track_id"],
                class_name=det["class_name"],
                confidence=det["confidence"],
                bbox=det["bbox"],
                rel_area=rel_area,
                timestamp=timestamp,
                speed_kmh=speed_kmh
            ))

        # 5. Compute Smoothness Index (SI)
        smoothness_index, penalty = self.si_calculator.compute_segment_si(anomaly_objects, speed_kmh)
        road_status, status_hex, alert_level = self.si_calculator.get_road_status(smoothness_index)
        alert_distance = self.si_calculator.calculate_dynamic_alert_distance(speed_kmh)
        hazard_active = bool((alert_level in ["HIGH", "CRITICAL"]) or (len(anomaly_objects) > 0 and smoothness_index < 75.0))

        # 6. Log Telemetry
        point = TelemetryPoint(
            timestamp=float(timestamp),
            latitude=float(lat),
            longitude=float(lon),
            speed_kmh=float(speed_kmh),
            heading_deg=float(heading),
            smoothness_index=float(smoothness_index),
            road_status=str(road_status),
            anomalies_detected=int(self.tracker.total_unique_count),
            hazard_alert=bool(hazard_active),
            alert_distance_m=float(alert_distance)
        )
        self.logger.log(point)

        # 7. Render Aerospace-grade HUD onto frame
        hud_frame = draw_hud(
            frame_np=frame_rgb,
            detections=tracked_detections,
            smoothness_index=smoothness_index,
            road_status=road_status,
            status_color_hex=status_hex,
            speed_kmh=speed_kmh,
            alert_distance_m=alert_distance,
            hazard_alert=hazard_active,
            fps=32.4,
            lat=lat,
            lon=lon,
            total_unique_potholes=self.tracker.total_unique_count
        )

        return hud_frame, point

    def run_simulation(self, total_seconds: float = 15.0, target_fps: int = 25):
        print(f"[PathSense] Starting Live Dashcam Edge Simulation ({total_seconds}s @ {target_fps} FPS)...")
        total_frames = int(total_seconds * target_fps)
        start_time = time.time()

        for f_idx in range(total_frames):
            sim_time = f_idx / float(target_fps)
            frame = generate_synthetic_road_frame(step_count=f_idx)
            hud_frame, pt = self.process_frame(frame, timestamp=start_time + sim_time, simulated_time=sim_time)

            if f_idx % 20 == 0 or f_idx == total_frames - 1:
                print(f"  Frame {f_idx:03d}/{total_frames} | Speed: {pt.speed_kmh:.1f} km/h | "
                      f"SI: {pt.smoothness_index:5.1f} | Status: {pt.road_status:20s} | Unique Anomalies: {pt.anomalies_detected}")

        print(f"[PathSense] Simulation completed! Audit logs saved to {self.logger.csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PathSense Live Edge Pipeline")
    parser.add_argument("--mode", type=str, default="demo", choices=["demo", "camera", "video"], help="Pipeline execution mode")
    parser.add_argument("--duration", type=float, default=12.0, help="Simulation duration in seconds")
    parser.add_argument("--fps", type=int, default=25, help="Simulation frame rate")
    args = parser.parse_args()

    pipeline = LiveDashcamPipeline()
    pipeline.run_simulation(total_seconds=args.duration, target_fps=args.fps)
