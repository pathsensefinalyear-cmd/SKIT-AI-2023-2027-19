"""
PathSense Visuals: Edge Dashcam HUD (Heads-Up Display) & Telemetry Overlay
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Renders real-time telemetry, bounding boxes, Smoothness Index gauge,
dynamic speed-based hazard alerts, and GPS coordinates onto dashcam video frames.
Supports both OpenCV (cv2) and PIL (Pillow) rendering engines.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# Bounding Box Color Palette
CLASS_COLORS = {
    "pothole": (239, 68, 68),            # Vibrant Red
    "alligator_crack": (249, 115, 22),    # Amber/Orange
    "longitudinal_crack": (6, 182, 212),  # Cyan
    "transverse_crack": (168, 85, 247),   # Purple
    "default": (234, 179, 8)              # Yellow
}


def draw_hud(
    frame_np: np.ndarray,
    detections: List[Dict],
    smoothness_index: float,
    road_status: str,
    status_color_hex: str,
    speed_kmh: float,
    alert_distance_m: float,
    hazard_alert: bool,
    fps: float,
    lat: float,
    lon: float,
    total_unique_potholes: int,
    device_name: str = "RTX 2050 (Edge)"
) -> np.ndarray:
    """
    Renders high-tech HUD overlay on an image array (RGB format).
    Returns annotated RGB image array.
    """
    img = Image.fromarray(frame_np)
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = img.size

    # 1. Draw Bounding Boxes with Labels
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cname = det["class_name"]
        conf = det.get("confidence", 0.0)
        tid = det.get("track_id", "?")
        box_color = CLASS_COLORS.get(cname, CLASS_COLORS["default"])

        # Bounding box border
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=3)
        # Translucent fill
        draw.rectangle([x1, y1, x2, y2], fill=(box_color[0], box_color[1], box_color[2], 40))

        # Box label tag
        label_text = f"#{tid} {cname.upper()} {int(conf * 100)}%"
        # Tag background
        draw.rectangle([x1, max(0, y1 - 22), min(w, x1 + 180), y1], fill=(20, 24, 33, 220))
        draw.text((x1 + 6, max(2, y1 - 18)), label_text, fill=(255, 255, 255))

    # 2. Top Header Bar (Dark Translucent Ribbon)
    draw.rectangle([0, 0, w, 52], fill=(15, 23, 42, 225))
    draw.line([(0, 52), (w, 52)], fill=(56, 189, 248), width=2)

    # Top Left: System Title & Hardware badge
    draw.text((15, 8), "PATHSENSE AI", fill=(56, 189, 248))
    draw.text((15, 28), f"Edge Vision Engine | {device_name} | {fps:.1f} FPS", fill=(148, 163, 184))

    # Top Right: Smoothness Index (SI) Status Gauge
    si_label = f"ROAD HEALTH: {smoothness_index:.1f}/100"
    draw.rectangle([w - 320, 6, w - 15, 46], fill=(30, 41, 59, 240), outline=(100, 116, 139), width=1)
    draw.text((w - 310, 10), si_label, fill=(255, 255, 255))
    draw.text((w - 310, 28), f"CONDITION: {road_status}", fill=(56, 189, 248))

    # 3. Bottom Telemetry Bar
    draw.rectangle([0, h - 56, w, h], fill=(15, 23, 42, 235))
    draw.line([(0, h - 56), (w, h - 56)], fill=(56, 189, 248), width=1)

    # Bottom Left: Speed & Alert Safety Margin
    draw.text((15, h - 48), f"SPEED: {speed_kmh:.1f} km/h", fill=(255, 255, 255))
    draw.text((15, h - 28), f"SAFE ALERT DISTANCE: {alert_distance_m:.1f} m", fill=(148, 163, 184))

    # Bottom Middle: Pothole Counter
    draw.text((int(w * 0.42), h - 48), f"ANOMALIES LOGGED: {total_unique_potholes}", fill=(250, 204, 21))
    draw.text((int(w * 0.42), h - 28), "DEDUPLICATION: ACTIVE (ByteTrack)", fill=(148, 163, 184))

    # Bottom Right: GPS Geospatial Coordinates
    gps_str = f"GPS: {lat:.5f} N, {lon:.5f} E"
    draw.text((w - 280, h - 48), gps_str, fill=(255, 255, 255))
    draw.text((w - 280, h - 28), "ZONE: SKIT / Jagatpura (Jaipur)", fill=(56, 189, 248))

    # 4. Central Dynamic Hazard Alert (flashing banner when hazard detected)
    if hazard_alert:
        banner_w = int(w * 0.72)
        banner_x1 = (w - banner_w) // 2
        banner_x2 = banner_x1 + banner_w
        banner_y1 = 64
        banner_y2 = 110

        draw.rectangle([banner_x1, banner_y1, banner_x2, banner_y2], fill=(220, 38, 38, 230), outline=(254, 202, 202), width=2)
        alert_msg = f"[!] HAZARD WARNING: SEVERE ROAD ANOMALY AHEAD ({alert_distance_m:.0f}m MARGIN)"
        draw.text((banner_x1 + 25, banner_y1 + 14), alert_msg, fill=(255, 255, 255))

    return np.array(img)
