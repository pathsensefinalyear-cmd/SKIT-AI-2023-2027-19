"""
PathSense Core: Smoothness Index (SI) Algorithm & Hazard Scoring
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Mathematical Formulation:
    SI = 100 - sum_{i=1}^N (alpha * A_i * V * C_i)

Where:
    - N    : Total unique road anomalies detected in a road window (50m or time segment)
    - A_i  : Normalized bounding box area (Box Area / Frame Area)
    - V    : Instantaneous vehicle speed in km/h (GPS-derived)
    - C_i  : Class severity weight (e.g., Pothole=1.2, Alligator Crack=0.8, Longitudinal=0.5)
    - alpha: Calibration tuning parameter (default: 0.45)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class RoadAnomaly:
    track_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    rel_area: float  # Normalized to [0, 1]
    timestamp: float
    speed_kmh: float


class SmoothnessIndexCalculator:
    # Standard class severity weights for Indian Road Damage (RDD2022 taxonomy)
    DEFAULT_CLASS_WEIGHTS = {
        "D40": 1.4,          # Pothole (High severity)
        "pothole": 1.4,
        "D20": 1.0,          # Alligator / fatigue cracking (Moderate-high)
        "alligator_crack": 1.0,
        "D00": 0.6,          # Longitudinal crack (Moderate)
        "longitudinal_crack": 0.6,
        "D10": 0.6,          # Transverse crack (Moderate)
        "transverse_crack": 0.6,
        "unpaved_patch": 1.2,
        "speed_breaker": 0.4, # Natural bump, low damage penalty
    }

    def __init__(self, alpha: float = 0.45, base_score: float = 100.0):
        self.alpha = alpha
        self.base_score = base_score
        self.class_weights = self.DEFAULT_CLASS_WEIGHTS.copy()

    def calculate_relative_area(self, bbox: Tuple[int, int, int, int], frame_shape: Tuple[int, int]) -> float:
        """
        Calculate relative area A_i of bounding box normalized against frame resolution.
        frame_shape: (height, width)
        """
        h_frame, w_frame = frame_shape
        x1, y1, x2, y2 = bbox
        box_w = max(0, x2 - x1)
        box_h = max(0, y2 - y1)
        box_area = box_w * box_h
        frame_area = max(1, w_frame * h_frame)
        return min(1.0, float(box_area) / float(frame_area))

    def compute_segment_si(self, anomalies: List[RoadAnomaly], current_speed_kmh: float) -> Tuple[float, float]:
        """
        Calculates the Smoothness Index (0-100) for a given segment window.
        Returns:
            Tuple[smoothness_index, penalty_sum]
        """
        if not anomalies:
            return self.base_score, 0.0

        # Effective vehicle speed factor (minimum speed clamp at 5 km/h to prevent zero-penalty standstill)
        effective_speed = max(5.0, current_speed_kmh)
        speed_factor = effective_speed / 40.0  # Normalized relative to 40 km/h baseline

        total_penalty = 0.0
        for anom in anomalies:
            weight = self.class_weights.get(anom.class_name, 0.8)
            # Area-speed impact: large potholes hit at high speed cause quadratic hazard increase
            area_impact = anom.rel_area * 10.0  # Scale relative area
            penalty = self.alpha * area_impact * speed_factor * weight * (anom.confidence ** 0.5)
            total_penalty += penalty

        # Cap score between [0, 100]
        smoothness_index = max(0.0, min(self.base_score, self.base_score - total_penalty))
        return round(smoothness_index, 1), round(total_penalty, 2)

    @staticmethod
    def get_road_status(si_score: float) -> Tuple[str, str, str]:
        """
        Returns (Status Label, Hex Color, Alert Level)
        """
        if si_score >= 85.0:
            return "EXCELLENT / SMOOTH", "#22C55E", "LOW"
        elif si_score >= 70.0:
            return "GOOD / MINOR WEAR", "#84CC16", "LOW"
        elif si_score >= 50.0:
            return "FAIR / MODERATE DAMAGE", "#EAB308", "MEDIUM"
        elif si_score >= 30.0:
            return "POOR / HIGH DAMAGE", "#F97316", "HIGH"
        else:
            return "CRITICAL / SEVERE HAZARDS", "#EF4444", "CRITICAL"

    @staticmethod
    def calculate_dynamic_alert_distance(speed_kmh: float, reaction_time_sec: float = 1.2) -> float:
        """
        Speed-adaptive alert distance:
        Calculates safe forward warning distance in meters based on vehicle velocity.
        At 20 km/h -> ~8 meters
        At 40 km/h -> ~18 meters
        At 60 km/h -> ~32 meters
        """
        v_ms = max(0.0, speed_kmh * (1000.0 / 3600.0))
        # Braking deceleration assumption for standard Indian city conditions (a = ~4.5 m/s^2)
        decel = 4.5
        reaction_distance = v_ms * reaction_time_sec
        braking_distance = (v_ms ** 2) / (2.0 * decel)
        total_safety_margin = reaction_distance + braking_distance + 3.0  # 3m safety buffer
        return round(max(5.0, total_safety_margin), 1)
