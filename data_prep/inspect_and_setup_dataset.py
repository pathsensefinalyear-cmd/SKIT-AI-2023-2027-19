"""
PathSense Dataset Ingestion & Auto-Configuration Utility
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Automatically detects, extracts, inspects, and validates labeled datasets
(YOLO .txt, Pascal VOC .xml, Roboflow zip) and generates `dataset/data.yaml`.
"""

import os
import sys
import glob
import zipfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"


def extract_zip_if_needed(source_path: Path, target_dir: Path) -> Path:
    """Extracts a zip file into target directory if it's an archive."""
    if source_path.is_file() and source_path.suffix.lower() in [".zip"]:
        dest = target_dir / source_path.stem
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[Extractor] Extracting '{source_path.name}' to '{dest}'...")
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(dest)
        print(f"[Extractor] Extraction complete.")
        return dest
    return source_path


def detect_dataset_format(search_root: Path) -> Dict[str, any]:
    """
    Scans a folder to discover whether it contains:
    - YOLO format (.txt label files)
    - Pascal VOC format (.xml files)
    - Image extensions (.jpg, .jpeg, .png)
    """
    img_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = []
    xml_files = []
    txt_files = []

    for path in search_root.rglob("*"):
        if path.is_file():
            ext = path.suffix.lower()
            if ext in img_extensions:
                images.append(path)
            elif ext == ".xml":
                xml_files.append(path)
            elif ext == ".txt" and path.name.lower() not in ["classes.txt", "readme.txt", "license.txt"]:
                txt_files.append(path)

    format_type = "unknown"
    if txt_files:
        format_type = "yolo"
    elif xml_files:
        format_type = "voc"

    return {
        "format": format_type,
        "image_count": len(images),
        "xml_count": len(xml_files),
        "txt_count": len(txt_files),
        "images": images,
        "xml_files": xml_files,
        "txt_files": txt_files,
        "root": search_root
    }


def parse_classes_from_voc(xml_files: List[Path]) -> List[str]:
    """Finds all unique class names across XML files."""
    unique_classes = set()
    sample_files = xml_files[:500]  # Sample first 500 for speed
    for xf in sample_files:
        try:
            tree = ET.parse(xf)
            for obj in tree.findall("object"):
                name = obj.find("name")
                if name is not None and name.text:
                    unique_classes.add(name.text.strip())
        except Exception:
            continue
    return sorted(list(unique_classes))


def generate_data_yaml(dest_yaml: Path, dataset_path: Path, class_names: List[str]):
    """Generates a standardized Ultralytics YOLOv8 data.yaml file."""
    yaml_content = f"""# PathSense YOLOv8 Dataset Configuration
# Generated automatically by PathSense Dataset Pipeline
# Academic Minor Project - SKIT Jaipur, CS-AI (7th Sem)

path: {dataset_path.as_posix()}
train: images/train
val: images/val
test: images/test

# Classes ({len(class_names)})
names:
"""
    for idx, cname in enumerate(class_names):
        yaml_content += f"  {idx}: {cname}\n"

    dest_yaml.write_text(yaml_content, encoding="utf-8")
    print(f"[Config] Generated YOLO configuration at: {dest_yaml}")


def inspect_dataset(target_path_str: Optional[str] = None):
    print("=" * 65)
    print("      PATHSENSE: DATASET INSPECTION & INTEGRATION PIPELINE       ")
    print("=" * 65)

    downloads_dir = Path(os.path.expanduser("~")) / "Downloads"

    if target_path_str:
        candidate_path = Path(target_path_str).resolve()
    else:
        # Check Downloads for recent zip files or datasets
        zip_candidates = list(downloads_dir.glob("*.zip"))
        if zip_candidates:
            # Sort by last modified
            zip_candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            candidate_path = zip_candidates[0]
            print(f"[Auto-Detection] Found latest zip in Downloads: {candidate_path.name}")
        else:
            candidate_path = DATASET_DIR

    if not candidate_path.exists():
        print(f"[Error] Path '{candidate_path}' does not exist.")
        return

    # Extract if zip
    target_dir = extract_zip_if_needed(candidate_path, DATASET_DIR)

    # Detect dataset format
    analysis = detect_dataset_format(target_dir)

    print("\n--- DATASET AUDIT SUMMARY ---")
    print(f"Target Directory: {target_dir}")
    print(f"Detected Format : {analysis['format'].upper()}")
    print(f"Total Images    : {analysis['image_count']}")
    print(f"YOLO Labels     : {analysis['txt_count']}")
    print(f"VOC XML Files   : {analysis['xml_count']}")

    if analysis['format'] == "voc":
        classes = parse_classes_from_voc(analysis['xml_files'])
        print(f"Discovered VOC Classes: {classes}")
        print("\n[Recommendation] Ready for Pascal VOC -> YOLO conversion via `data_prep/rdd2022_converter.py`.")
        yaml_path = DATASET_DIR / "data.yaml"
        generate_data_yaml(yaml_path, target_dir, classes if classes else ["D00", "D10", "D20", "D40"])

    elif analysis['format'] == "yolo":
        # Check for classes.txt or data.yaml
        classes = ["Longitudinal Crack", "Transverse Crack", "Alligator Crack", "Pothole"]
        classes_txt = target_dir / "classes.txt"
        if classes_txt.exists():
            classes = [line.strip() for line in classes_txt.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(f"Classes: {classes}")
        yaml_path = DATASET_DIR / "data.yaml"
        generate_data_yaml(yaml_path, target_dir, classes)
        print("\n[Status] Dataset is in native YOLO format and ready for training!")

    else:
        print("\n[Notice] No standard YOLO/VOC annotation files were found in this directory.")
        print("Please ensure your dataset contains images with corresponding .txt or .xml labels.")

    print("=" * 65)


if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    inspect_dataset(path_arg)
