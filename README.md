# PathSense: Real-Time Edge-Vision for Road Condition Mapping
### An End-to-End AI Dashcam Framework for Pothole Detection, Surface Smoothness Indexing, and Geospatial Infrastructure Auditing

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8%20Medium-00FFFF.svg)](https://ultralytics.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Hardware](https://img.shields.io/badge/Edge%20Hardware-NVIDIA%20RTX%202050-76B900.svg)](https://nvidia.com)

---

## 🏛️ Project & Team Information
- **Institution:** Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur, Rajasthan
- **Department:** Computer Science & Artificial Intelligence (CS-AI), 6th Semester
- **Team Members:**
  1. **Sharafat Khan** (`23ESKCA098`) - AI Model Training & Dataset Engineering (RDD2022)
  2. **Soham Manocha** (`23ESKCA102`) - Edge Inference & Cloud-to-Edge Pipeline Optimization
  3. **Sourabh Nagar** (`23ESKCA105`) - Full-Stack Geospatial Dashboard & OpenStreetMap Integration
  4. **Vedic Baurasi** (`23ESKCA119`) - System Architecture, Smoothness Index Algorithm & ByteTrack Tracking

---

## 🚀 The Core Problem & Our Solution
Standard navigation applications (like Google Maps) indicate route congestion and arrival times, but have a **critical blind spot**: they ignore physical road quality. Drivers frequently encounter damaged routes with craters that destroy suspensions or cause accidents.

**PathSense** bridges this gap:
1. **Live Dashcam Capture:** A vehicle-mounted dashcam captures the roadway in front of the vehicle.
2. **YOLOv8 Edge Vision:** Detects potholes, alligator cracks, and longitudinal distress in real time at $>30$ FPS.
3. **ByteTrack Deduplication:** Tracks anomalies across consecutive frames, preventing duplicate counts for the same pothole.
4. **Smoothness Index (SI):** Calculates a mathematical score ($0–100$) for each 50m road segment:
   $$\text{SI} = 100 - \sum_{i=1}^N \left(\alpha \cdot A_i \cdot V \cdot C_i\right)$$
5. **Speed-Adaptive Alerts:** Warns drivers dynamically (e.g., $8\text{m}$ at $20\text{ km/h}$, $32\text{m}$ at $60\text{ km/h}$).
6. **Geospatial Heatmap:** Streams coordinates to a web dashboard for civilian routing and municipal road audits.

---

## 📂 Project Directory Structure

```text
pathsense/
├── core/
│   ├── detector.py          # YOLOv8 model wrapper + Heuristic edge engine
│   ├── tracker.py           # IoU / ByteTrack deduplication engine
│   ├── smoothness_index.py  # Mathematical Smoothness Index & speed alert logic
│   └── telemetry.py         # GPS coordinates, logging, and SKIT Jaipur simulator
├── inference/
│   ├── hud_overlay.py       # Aerospace-grade Dashcam Heads-Up Display (HUD)
│   ├── live_pipeline.py     # Real-time edge video processing pipeline
│   └── generate_demo_assets.py # Multi-zone SKIT Jaipur audit data synthesizer
├── dashboard/
│   └── app.py               # Streamlit + Pydeck + Folium geospatial web dashboard
├── data_prep/
│   ├── extract_frames.py    # 1-FPS frame extraction from dashcam video
│   └── rdd2022_converter.py # RDD2022 XML to YOLO format converter
├── train/
│   └── train_yolo.py        # Cloud GPU training script (Colab/Kaggle/RunPod)
├── docs/
│   ├── PROJECT_SYNOPSIS.md  # Official 3-page academic synopsis for faculty
│   ├── LITERATURE_REVIEW.md # 10-paper comparative analysis & research gap
│   └── FACULTY_VIVA_DEFENSE.md # Faculty trap questions & high-scoring answers
├── logs/                    # Audit logs (CSV & JSON)
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## ⚡ Quickstart Guide (Run in 2 Minutes)

### 1. Install Dependencies
```bash
cd pathsense
pip install -r requirements.txt
```

### 2. Synthesize Demo Audit Route (SKIT Jaipur Circuit)
Generates 180 telemetry points across Ramnagariya, Jagatpura, and SKIT roads:
```bash
python -m inference.generate_demo_assets
```

### 3. Run the Live Edge Dashcam Simulation
Runs edge inference with the HUD overlay, vehicle speed emulator, and Smoothness Index calculation:
```bash
python -m inference.live_pipeline --duration 10 --fps 15
```

### 4. Launch the Interactive Geospatial Web Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to view:
- 🗺️ **Geospatial Condition Heatmap** with color-coded road health points
- 📹 **Dashcam HUD & Live Vision Simulator** with interactive step scrubber
- 📊 **Road Quality Analytics & Damage Distributions**
- 📑 **Municipal Road Repair Audit Report Generator**

---

## 👥 4-Person Team Workload Allocation

| Student Name & Roll No. | Primary Role | Key Modules & Files |
|---|---|---|
| **Sharafat Khan** (`23ESKCA098`) | **AI & Dataset Engineer** | RDD2022 India dataset pipeline, Roboflow labeling, YOLOv8 cloud training (`data_prep/rdd2022_converter.py`, `train/train_yolo.py`) |
| **Soham Manocha** (`23ESKCA102`) | **Edge Systems Engineer** | OpenCV video capture, Edge optimization (ONNX), Telemetry & GPS logging (`core/telemetry.py`, `inference/live_pipeline.py`) |
| **Sourabh Nagar** (`23ESKCA105`) | **Geospatial & Web Engineer** | Streamlit web application, OpenStreetMap & Satellite Hybrid layers, Municipal reports (`dashboard/app.py`, `inference/hud_overlay.py`) |
| **Vedic Baurasi** (`23ESKCA119`) | **Lead Architect & Logic Engineer** | System design, Mathematical Smoothness Index formulation, ByteTrack deduplication (`core/smoothness_index.py`, `core/tracker.py`) |

---

## 💰 Budget Breakdown (Est. ~₹300 Per Teammate)
- **100% Free Resources:** Google Colab / Kaggle Cloud GPUs, OpenStreetMap / Folium, Streamlit, Firebase Free Spark tier.
- **Shared Hardware/Logistics:**
  - Car/Scooty Smartphone Dashboard Mount: ~₹400
  - Fuel for Data Collection Drives around Jaipur: ~₹800
  - **Total Shared Cost:** ~₹1,200 ($\approx$ **₹300 per person** across a 4-person team).

---

## 📚 Academic Citation & Benchmark
- **Base Dataset:** Global Road Damage Detection Challenge (RDD2022 - India subset), ~10,000 annotated images.
- **Object Classes:** `D00` (Longitudinal), `D10` (Transverse), `D20` (Alligator Fatigue Cracking), `D40` (Potholes).
