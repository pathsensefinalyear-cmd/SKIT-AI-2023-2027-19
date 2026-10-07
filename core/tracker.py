"""
PathSense Core: Anomaly Object Tracking & Deduplication (IoU / Centroid Tracker)
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Purpose:
    Deduplicates detected road anomalies across continuous video frames (30 FPS).
    Prevents a single pothole seen across 30-45 frames from skewing the Smoothness Index penalty.
"""

from typing import List, Tuple, Dict, Optional


def box_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    boxA_area = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxB_area = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    union_area = float(boxA_area + boxB_area - inter_area)
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


class RoadAnomalyTracker:
    def __init__(self, iou_threshold: float = 0.35, max_disappeared_frames: int = 15):
        self.iou_threshold = iou_threshold
        self.max_disappeared_frames = max_disappeared_frames
        self.next_track_id = 1
        
        # Track storage: track_id -> dict
        # { 'bbox': (x1, y1, x2, y2), 'class_name': str, 'confidence': float, 'disappeared': int, 'history_count': int }
        self.tracks: Dict[int, Dict] = {}
        self.total_unique_count = 0

    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        detections: list of dicts with keys:
            ['bbox': (x1, y1, x2, y2), 'class_name': str, 'confidence': float]
        
        Returns updated detections enriched with 'track_id' and 'is_new' flag.
        """
        output_results = []

        if not self.tracks:
            for det in detections:
                tid = self.next_track_id
                self.next_track_id += 1
                self.tracks[tid] = {
                    "bbox": det["bbox"],
                    "class_name": det["class_name"],
                    "confidence": det["confidence"],
                    "disappeared": 0,
                    "history_count": 1,
                }
                self.total_unique_count += 1
                det_copy = dict(det)
                det_copy["track_id"] = tid
                det_copy["is_new"] = True
                output_results.append(det_copy)
            return output_results

        track_ids = list(self.tracks.keys())
        matched_tracks = set()
        matched_detections = set()

        # Compute IoU matrix between existing tracks and incoming detections
        for d_idx, det in enumerate(detections):
            best_iou = 0.0
            best_tid = None
            for tid in track_ids:
                if tid in matched_tracks:
                    continue
                # Same class matching preference
                if self.tracks[tid]["class_name"] != det["class_name"]:
                    continue
                iou = box_iou(self.tracks[tid]["bbox"], det["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_tid = tid

            if best_iou >= self.iou_threshold and best_tid is not None:
                matched_tracks.add(best_tid)
                matched_detections.add(d_idx)
                # Update existing track
                self.tracks[best_tid]["bbox"] = det["bbox"]
                self.tracks[best_tid]["confidence"] = max(self.tracks[best_tid]["confidence"], det["confidence"])
                self.tracks[best_tid]["disappeared"] = 0
                self.tracks[best_tid]["history_count"] += 1
                
                det_copy = dict(det)
                det_copy["track_id"] = best_tid
                det_copy["is_new"] = False
                output_results.append(det_copy)

        # Handle unmatched detections (new potholes/cracks)
        for d_idx, det in enumerate(detections):
            if d_idx not in matched_detections:
                tid = self.next_track_id
                self.next_track_id += 1
                self.tracks[tid] = {
                    "bbox": det["bbox"],
                    "class_name": det["class_name"],
                    "confidence": det["confidence"],
                    "disappeared": 0,
                    "history_count": 1,
                }
                self.total_unique_count += 1
                det_copy = dict(det)
                det_copy["track_id"] = tid
                det_copy["is_new"] = True
                output_results.append(det_copy)

        # Handle unmatched tracks (temporarily missed or left camera view)
        for tid in track_ids:
            if tid not in matched_tracks:
                self.tracks[tid]["disappeared"] += 1

        # Purge dead tracks
        dead_tracks = [tid for tid, tr in self.tracks.items() if tr["disappeared"] > self.max_disappeared_frames]
        for tid in dead_tracks:
            del self.tracks[tid]

        return output_results
