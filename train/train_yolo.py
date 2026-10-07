"""
PathSense Model Training: YOLOv8 on Cloud GPUs (Google Colab / Kaggle / RunPod)
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Why Cloud Training?
    - Training YOLOv8 Medium with 10,000+ Indian road damage images at full 640x640 resolution
      demands ~12-16GB VRAM.
    - Cloud GPUs (NVIDIA T4 on Colab or RTX 4090 on RunPod) prevent Out-Of-Memory (OOM) crashes
      and complete training in 2-4 hours.
    - Exported lightweight .pt or .onnx weights are then deployed locally on the laptop RTX 2050 for edge inference.

Usage (in Google Colab / Kaggle):
    python train/train_yolo.py --data dataset/data.yaml --model yolov8m.pt --epochs 100 --imgsz 640 --batch 16
"""

import os
import argparse


def train_yolov8(
    data_yaml: str,
    base_model: str = "yolov8m.pt",
    epochs: int = 100,
    imgsz: int = 640,
    batch_size: int = 16,
    device: str = "0",
    project_name: str = "pathsense_training"
):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[Error] ultralytics is not installed in this environment.")
        print("Install it with: pip install ultralytics")
        return

    print("=================================================================")
    print("      PATHSENSE: CLOUD TRAINING PIPELINE (YOLOv8 Medium)         ")
    print("=================================================================")
    print(f"Base Weights: {base_model}")
    print(f"Dataset YAML: {data_yaml}")
    print(f"Target Epochs: {epochs} | Image Resolution: {imgsz}x{imgsz}")
    print(f"Batch Size: {batch_size} | Device: {device}")
    print("=================================================================")

    # 1. Load Pre-trained Base Architecture
    model = YOLO(base_model)

    # 2. Train with Domain Augmentations for Indian Roads
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        device=device,
        project=project_name,
        name="rdd2022_india_finetuned",
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        mosaic=1.0,           # Mosaic augmentation handles varying pothole scales
        mixup=0.15,           # Mixup helps robust texture feature learning
        degrees=10.0,         # Tilt variation from dashcam vibration
        fliplr=0.5,           # Horizontal flip for lane symmetry
        save=True,
        save_period=10,
        val=True,
        plots=True
    )

    print("\n[PathSense] Training completed successfully!")

    # 3. Validation Metrics
    metrics = model.val()
    print(f"mAP@50    : {metrics.box.map50:.4f}")
    print(f"mAP@50-95 : {metrics.box.map:.4f}")

    # 4. Export to High-Speed ONNX Engine for Edge Deployment
    print("\n[PathSense] Exporting model to ONNX for RTX 2050 Edge Inference...")
    export_path = model.export(format="onnx", dynamic=True, half=True)
    print(f"ONNX Model saved to: {export_path}")
    print("Download 'best.pt' and 'best.onnx' to your local laptop 'models/' directory!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PathSense YOLOv8 Cloud Training")
    parser.add_argument("--data", type=str, default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8m.pt", help="Base model weights")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--device", type=str, default="0", help="GPU device ID (0) or 'cpu'")
    args = parser.parse_args()

    train_yolov8(
        data_yaml=args.data,
        base_model=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch,
        device=args.device
    )
