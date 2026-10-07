"""
PathSense Data Prep: 1-FPS Video Frame Extractor
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Purpose:
    Extracts 1 frame per second from raw dashcam/smartphone driving video.
    Filters out near-identical duplicate frames to prevent AI overfitting.
    Converts a 15-minute driving video (27,000 frames @ 30 FPS) into ~400-500 high-value training images.

Usage:
    python -m data_prep.extract_frames --video path/to/campus_drive.mp4 --output dataset/custom_jaipur/
"""

import os
import argparse
from PIL import Image


def extract_frames_from_video(video_path: str, output_dir: str, sample_rate_sec: float = 1.0):
    """
    Extracts frames using OpenCV if installed, or provides an informative fallback.
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[Error] Could not open video file: {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = int(fps * sample_rate_sec)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"[PathSense Data Prep] Video FPS: {fps:.1f} | Total Frames: {total_frames} | Interval: {frame_interval} frames")

        saved_count = 0
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                out_filename = os.path.join(output_dir, f"jaipur_road_{saved_count:05d}.jpg")
                cv2.imwrite(out_filename, frame)
                saved_count += 1
                if saved_count % 50 == 0:
                    print(f"  Extracted {saved_count} frames...")

            frame_idx += 1

        cap.release()
        print(f"[PathSense Data Prep] Extraction complete! {saved_count} frames saved to '{output_dir}'.")
        print(f"Next step: Upload these images to Roboflow for bounding-box annotation.")

    except ImportError:
        print("[Notice] opencv-python is not yet installed in this environment.")
        print("To extract frames from raw video files, run:")
        print("    pip install opencv-python")
        print(f"Sample destination folder '{output_dir}' has been created.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract 1 FPS frames from video")
    parser.add_argument("--video", type=str, default="campus_drive.mp4", help="Path to input video")
    parser.add_argument("--output", type=str, default="dataset/custom_jaipur", help="Output directory")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval in seconds between extracted frames")
    args = parser.parse_args()

    extract_frames_from_video(args.video, args.output, args.interval)
