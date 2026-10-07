"""
PathSense Data Prep: RDD2022 XML to YOLO Format Converter
Author: Vedic Baurasi & Soham Manocha (SKIT Jaipur, CS-AI)

Converts standard Pascal VOC XML files from the official RDD2022 India dataset into
standard YOLO format (.txt files with normalized bounding boxes: <class_id> <x_center> <y_center> <width> <height>).

Classes:
    0: D00 (Longitudinal Crack)
    1: D10 (Transverse Crack)
    2: D20 (Alligator Crack)
    3: D40 (Pothole)
"""

import os
import xml.etree.ElementTree as ET
import shutil
import argparse
from typing import Dict, Tuple


CLASS_MAPPING: Dict[str, int] = {
    "D00": 0,  # Longitudinal Crack
    "D10": 1,  # Transverse Crack
    "D20": 2,  # Alligator Crack
    "D40": 3,  # Pothole
}


def convert_xml_to_yolo(xml_file: str, out_txt_file: str) -> int:
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        return 0

    size_elem = root.find("size")
    if size_elem is None:
        return 0

    width = float(size_elem.find("width").text)
    height = float(size_elem.find("height").text)

    if width <= 0 or height <= 0:
        return 0

    yolo_lines = []
    for obj in root.findall("object"):
        cls_name = obj.find("name").text
        if cls_name not in CLASS_MAPPING:
            continue

        class_id = CLASS_MAPPING[cls_name]
        bndbox = obj.find("bndbox")
        xmin = float(bndbox.find("xmin").text)
        ymin = float(bndbox.find("ymin").text)
        xmax = float(bndbox.find("xmax").text)
        ymax = float(bndbox.find("ymax").text)

        # Calculate normalized YOLO coordinates [0, 1]
        x_center = ((xmin + xmax) / 2.0) / width
        y_center = ((ymin + ymax) / 2.0) / height
        box_w = (xmax - xmin) / width
        box_h = (ymax - ymin) / height

        # Clamp values
        x_center = max(0.0, min(1.0, x_center))
        y_center = max(0.0, min(1.0, y_center))
        box_w = max(0.0, min(1.0, box_w))
        box_h = max(0.0, min(1.0, box_h))

        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}")

    if yolo_lines:
        with open(out_txt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(yolo_lines) + "\n")
        return len(yolo_lines)

    return 0


def generate_data_yaml(output_dir: str):
    yaml_content = f"""# PathSense: Road Damage Detection Dataset Configuration
# RDD2022 India Subset + Custom SKIT Jaipur Road Annotations

path: {os.path.abspath(output_dir)}
train: images/train
val: images/val

# Classes
names:
  0: longitudinal_crack  # D00
  1: transverse_crack    # D10
  2: alligator_crack     # D20
  3: pothole             # D40
"""
    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print(f"[PathSense Data Prep] Generated YOLO data config at '{yaml_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RDD2022 XML annotations to YOLO TXT")
    parser.add_argument("--xml_dir", type=str, default="rdd2022_india/xmls", help="Directory with VOC XML files")
    parser.add_argument("--out_dir", type=str, default="dataset/yolo_labels", help="Directory to save YOLO txt files")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    generate_data_yaml("dataset")
    print(f"[PathSense Data Prep] RDD2022 Converter ready. Place Indian XML annotations in '{args.xml_dir}'.")
