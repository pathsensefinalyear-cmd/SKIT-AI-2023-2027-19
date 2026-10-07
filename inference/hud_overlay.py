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

    # 1. Draw Bounding Boxes with Labels (Anti-Collision Tag Positioning)
    for idx, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        cname = det["class_name"]
        conf = det.get("confidence", 0.0)
        tid = det.get("track_id", idx + 1)
        box_color = CLASS_COLORS.get(cname, CLASS_COLORS["default"])

        # Bounding box border
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=3)
        # Translucent fill
        draw.rectangle([x1, y1, x2, y2], fill=(box_color[0], box_color[1], box_color[2], 40))

        # Compact label text
        short_cname = "POTHOLE" if "pothole" in cname else ("CRACK" if "crack" in cname else cname.upper())
        label_text = f"#{tid} {short_cname} {int(conf * 100)}%"
        tag_w = min(max(70, len(label_text) * 7 + 10), max(80, x2 - x1 + 20))
        tag_h = 18

        # Stagger alternating tags (even indices above box, odd indices below box) to avoid overlapping
        if idx % 2 == 0 or y2 + tag_h + 4 > h - 56:
            tag_y1 = max(54, y1 - tag_h - 2)
            tag_y2 = tag_y1 + tag_h
        else:
            tag_y1 = min(h - 60, y2 + 2)
            tag_y2 = tag_y1 + tag_h

        tag_x2 = min(w - 2, x1 + tag_w)
        # Tag background
        draw.rectangle([x1, tag_y1, tag_x2, tag_y2], fill=(15, 23, 42, 230), outline=box_color, width=1)
        draw.text((x1 + 4, tag_y1 + 2), label_text, fill=(255, 255, 255))

    # 2. Top Header Bar (Dark Translucent Ribbon)
    header_h = 46 if w < 600 else 52
    draw.rectangle([0, 0, w, header_h], fill=(15, 23, 42, 235))
    draw.line([(0, header_h), (w, header_h)], fill=(56, 189, 248), width=2)

    # Top Left: System Title
    draw.text((12, 6), "PATHSENSE AI", fill=(56, 189, 248))
    if w >= 500:
        draw.text((12, 26), f"Edge Vision | {device_name} | {fps:.1f} FPS", fill=(148, 163, 184))

    # Top Right: Smoothness Index (SI) Status Gauge (Responsive Width)
    if w < 500:
        draw.text((w - 110, 8), f"SI: {smoothness_index:.1f}", fill=(255, 255, 255))
        draw.text((w - 110, 24), road_status[:10], fill=(56, 189, 248))
    else:
        meter_w = 260 if w < 800 else 310
        draw.rectangle([w - meter_w, 6, w - 12, header_h - 6], fill=(30, 41, 59, 240), outline=(100, 116, 139), width=1)
        draw.text((w - meter_w + 10, 8), f"ROAD HEALTH: {smoothness_index:.1f}/100", fill=(255, 255, 255))
        draw.text((w - meter_w + 10, 26), f"CONDITION: {road_status}", fill=(56, 189, 248))

    # 3. Bottom Telemetry Bar
    bottom_h = 44 if w < 600 else 54
    draw.rectangle([0, h - bottom_h, w, h], fill=(15, 23, 42, 240))
    draw.line([(0, h - bottom_h), (w, h - bottom_h)], fill=(56, 189, 248), width=1)

    # Bottom Left: Speed & Alert Margin
    draw.text((10, h - bottom_h + 6), f"SPD: {speed_kmh:.1f} km/h", fill=(255, 255, 255))
    if w >= 450:
        draw.text((10, h - bottom_h + 24), f"MARGIN: {alert_distance_m:.1f}m", fill=(148, 163, 184))

    # Bottom Middle/Right: Anomalies Logged
    if w >= 550:
        draw.text((int(w * 0.40), h - bottom_h + 6), f"ANOMALIES: {total_unique_potholes}", fill=(250, 204, 21))
        draw.text((int(w * 0.40), h - bottom_h + 24), "TRACK: ByteTrack", fill=(148, 163, 184))

    gps_x = max(int(w * 0.65), w - 170)
    draw.text((gps_x, h - bottom_h + 6), f"GPS: {lat:.3f}, {lon:.3f}", fill=(255, 255, 255))

    # 4. Central Dynamic Hazard Alert (Responsive Width)
    if hazard_alert:
        banner_w = int(w * 0.92) if w < 600 else int(w * 0.75)
        banner_x1 = (w - banner_w) // 2
        banner_x2 = banner_x1 + banner_w
        banner_y1 = header_h + 10
        banner_y2 = banner_y1 + 38

        draw.rectangle([banner_x1, banner_y1, banner_x2, banner_y2], fill=(220, 38, 38, 230), outline=(254, 202, 202), width=2)
        if w < 500:
            alert_msg = f"[!] HAZARD: POTHOLE AHEAD ({alert_distance_m:.0f}m)"
        else:
            alert_msg = f"[!] HAZARD WARNING: SEVERE ROAD ANOMALY AHEAD ({alert_distance_m:.0f}m MARGIN)"
        draw.text((banner_x1 + 12, banner_y1 + 10), alert_msg, fill=(255, 255, 255))

    return np.array(img)
