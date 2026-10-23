# PathSense: Real-Time Edge-Vision for Road Condition Mapping
### An End-to-End AI Dashcam Framework for Pothole Detection, Surface Smoothness Indexing, and Geospatial Infrastructure Auditing

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8%20Medium-00FFFF.svg)](https://ultralytics.com/)
[![Starlette](https://img.shields.io/badge/Backend-Starlette%20ASGI-009688.svg)](https://www.starlette.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57.svg)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Hardware](https://img.shields.io/badge/Edge%20Hardware-NVIDIA%20RTX%202050-76B900.svg)](https://nvidia.com)

---

## 🏛️ Project & Team Information
- **Institution:** Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur, Rajasthan
- **Department:** Computer Science & Artificial Intelligence (CS-AI), 7th Semester
- **Team Members:**
  1. **Sharafat Khan** (`23ESKCA098`) - AI Model Training & Dataset Engineering (RDD2022)
  2. **Soham Manocha** (`23ESKCA102`) - Edge Inference & Cloud-to-Edge Pipeline Optimization
  3. **Sourabh Nagar** (`23ESKCA105`) - Backend REST API, Database Engine & Telemetry Sync
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
6. **Decoupled Backend REST API:** Starlette ASGI + SQLite service (Port 8000) for high-concurrency ingestion and spatial querying.
7. **Geospatial Heatmap:** Streams coordinates to a web dashboard for civilian routing and municipal road audits.

---

## 🏗️ Full-Stack System Architecture

```text
                  [ Dashcam / Video Input / User Upload ]
                                     │
                                     ▼
                      [ Core AI & Edge Inference ]
              ├── detector.py          (YOLOv8 Edge Vision)
              ├── tracker.py           (ByteTrack Deduplication)
              ├── smoothness_index.py  (SI Formulation & Safety Margin)
              └── telemetry.py         (GPS Route & Circuit Simulator)
                                     │
                        ┌────────────┴────────────┐
                        ▼                         ▼
            [ Starlette ASGI REST API ]   [ Local CSV / JSON ]
                   (Port 8000)            (pathsense_audit_log.csv)
            ├── /api/v1/health                    │
            ├── /api/v1/detect                    ▼
            ├── /api/v1/telemetry        [ Firebase Cloud Sync ]
            ├── /api/v1/heatmap          (Offline-First Resilient Queue)
            ├── /api/v1/analytics
            └── /api/v1/sync
                        │
                        ▼
               [ SQLite Database ]
               (logs/pathsense.db)
                        │
                        ▼
          [ Streamlit Geospatial Frontend ]
                   (Port 8501)
          ├── 🗺️ Interactive OpenStreetMap / Satellite GIS Heatmap
          ├── 📹 Dashcam HUD & Live Vision Visualizer
          ├── 📊 Road Quality & Statistical Analytics
          └── 📑 Automated Municipal PWD / JDA Audit Reports
```

---

## 📂 Project Directory Structure

```text
pathsense/
├── start_pathsense.py       # Unified launcher for Full-Stack (Backend + Frontend + DB)
├── run.bat                  # One-click Windows launch script
├── core/
│   ├── detector.py          # YOLOv8 model wrapper + Heuristic edge engine
│   ├── tracker.py           # IoU / ByteTrack deduplication engine
│   ├── smoothness_index.py  # Mathematical Smoothness Index & speed alert logic
│   └── telemetry.py         # GPS coordinates, logging, and SKIT Jaipur simulator
├── backend/
│   ├── api_server.py        # Starlette ASGI high-performance REST API
│   ├── database.py          # SQLite schema, tables, indices, and CRUD functions
│   ├── seed_db.py           # Database seeder (CSV to SQLite bridge)
│   ├── view_db.py           # SQLite database quick CLI inspector
│   ├── run_backend.py       # Standalone backend server runner
│   ├── test_backend.py      # Automated unit & integration test suite (6/6 tests)
│   ├── firebase_sync.py     # Offline-first Firebase Realtime DB sync engine
│   └── firebase_config.json # Firebase connection config
├── inference/
│   ├── hud_overlay.py       # Aerospace-grade Dashcam Heads-Up Display (HUD)
│   ├── live_pipeline.py     # Real-time edge video processing pipeline
│   └── generate_demo_assets.py # Multi-zone SKIT Jaipur audit data synthesizer
├── dashboard/
│   ├── app.py               # Streamlit + Pydeck + Folium geospatial web dashboard
│   └── assets/              # Real-world Indian dashcam reference imagery
├── dataset/
│   └── data.yaml            # YOLOv8 RDD2022 dataset descriptor
├── data_prep/
│   ├── extract_frames.py    # 1-FPS frame extraction from dashcam video
│   ├── inspect_and_setup_dataset.py # Auto-detect and ingest datasets
│   └── rdd2022_converter.py # RDD2022 XML to YOLO format converter
├── train/
│   ├── train_yolo.py        # Cloud GPU training script (Colab/Kaggle/RunPod)
│   └── PathSense_Colab_Training.ipynb # Interactive notebook for model training
├── docs/
│   ├── PROJECT_SYNOPSIS.md  # Official 3-page academic synopsis for faculty
│   ├── LITERATURE_REVIEW.md # 10-paper comparative analysis & research gap
│   └── FACULTY_VIVA_DEFENSE.md # Faculty trap questions & high-scoring answers
├── logs/
│   ├── pathsense.db         # Persistent SQLite Database
│   ├── pathsense_audit_log.csv # Local CSV route log
│   └── pathsense_live_feed.json # Real-time JSON telemetry stream
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## ⚡ Quickstart Guide (Run in 2 Minutes)

### Option A: One-Click Full-Stack Launch (Recommended)
Runs Backend REST API (Port 8000), seeds SQLite database, and starts Frontend Dashboard (Port 8501):
```bash
python start_pathsense.py --mode all
```
*Or on Windows, simply double-click `run.bat`.*

### Option B: Step-by-Step Manual Launch

#### 1. Seed or Verify SQLite Database
```bash
python backend/seed_db.py --force
```

#### 2. Run the Backend REST API Server
```bash
python backend/run_backend.py --port 8000
```
- Health Check: `http://127.0.0.1:8000/api/v1/health`
- Heatmap Data: `http://127.0.0.1:8000/api/v1/heatmap`
- Municipal Analytics: `http://127.0.0.1:8000/api/v1/analytics`

#### 3. Launch the Interactive Web Dashboard
```bash
streamlit run dashboard/app.py
```
Open browser at `http://localhost:8501` to view:
- 🗺️ **Geospatial Condition Heatmap** with color-coded road health points
- 📹 **Dashcam HUD & Live Vision Simulator** with interactive step scrubber
- 📊 **Road Quality Analytics & Damage Distributions**
- 📑 **Municipal Road Repair Audit Report Generator**

#### 4. Run Backend Test Suite
```bash
python backend/test_backend.py
```

---

## 👥 4-Person Team Workload Allocation

| Student Name & Roll No. | Primary Role | Key Modules & Files |
|---|---|---|
| **Sharafat Khan** (`23ESKCA098`) | **AI & Dataset Engineer** | RDD2022 India dataset pipeline, Roboflow labeling, YOLOv8 cloud training (`data_prep/rdd2022_converter.py`, `train/train_yolo.py`) |
| **Soham Manocha** (`23ESKCA102`) | **Edge Systems Engineer** | OpenCV video capture, Edge optimization (ONNX), Telemetry & GPS logging (`core/telemetry.py`, `inference/live_pipeline.py`) |
| **Sourabh Nagar** (`23ESKCA105`) | **Backend & Cloud Engineer** | Starlette ASGI REST API, SQLite database engine, Firebase offline-first sync (`backend/api_server.py`, `backend/database.py`, `backend/seed_db.py`) |
| **Vedic Baurasi** (`23ESKCA119`) | **Geospatial & Lead Architect** | Streamlit web application, OpenStreetMap & Satellite layers, Smoothness Index & ByteTrack (`dashboard/app.py`, `core/smoothness_index.py`, `core/tracker.py`) |

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
