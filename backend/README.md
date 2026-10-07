# PathSense AI: Backend Production Architecture & REST API

## Academic Project Details
- **Project Title:** PathSense: Real-Time Edge-Vision for Road Condition Mapping
- **Academic Milestone:** 7th Semester B.Tech Minor Project
- **Institution:** Swami Keshvanand Institute of Technology (SKIT), Jaipur
- **Department:** Computer Science & Artificial Intelligence (CS-AI)
- **Team Members (in strict order):**
  1. **Sharafat Khan** (`23ESKCA098`) — Lead Architect & Edge AI
  2. **Soham Manocha** (`23ESKCA102`) — Computer Vision & Dataset Pipeline
  3. **Sourabh Nagar** (`23ESKCA105`) — Backend Engine & Telemetry Sync
  4. **Vedic Baurasi** (`23ESKCA119`) — Dashboard & GIS Heatmap

---

## 1. Architecture Overview

PathSense Backend is built as an asynchronous, high-concurrency Edge & Cloud REST API using **Starlette ASGI**, **Uvicorn**, **SQLite** (local persistent database), and **Firebase Realtime Database** (Option B cloud sync with offline-first queue).

```
   [ Dashcam / Edge Device / User ]
                 │
                 ▼
      [ Starlette ASGI REST API ]  (Port 8000)
       ├── GET  /api/v1/health       (Diagnostics & Team Metadata)
       ├── POST /api/v1/detect       (AI Distress Inference & SI HUD)
       ├── POST /api/v1/telemetry    (GPS Telemetry Ingestion)
       ├── GET  /api/v1/heatmap      (Geospatial Coordinates for Map)
       ├── GET  /api/v1/analytics    (Municipal Road Audit Metrics)
       └── POST /api/v1/sync         (Firebase Cloud Sync Trigger)
                 │
        ┌────────┴────────┐
        ▼                 ▼
 [ SQLite Database ]  [ Firebase Cloud Sync ]
 (logs/pathsense.db)  (logs/firebase_offline_queue.json)
```

---

## 2. Quick Start Commands

### Start the Backend REST API Server:
```powershell
python backend/run_backend.py --port 8000
```
Server runs at: `http://127.0.0.1:8000`

### Run Complete Automated Test Suite:
```powershell
python backend/test_backend.py
```

### Run Cloud Sync Status Check:
```powershell
python -m backend.firebase_sync --status
```

---

## 3. REST API Endpoints Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check, uptime, engine status, and 7th Sem team details. |
| `POST` | `/api/v1/detect` | Accepts road image + speed, runs detection, calculates SI & stopping buffer, returns JSON + annotated HUD. |
| `POST` | `/api/v1/telemetry` | Ingests GPS telemetry packet, writes to SQLite and CSV. |
| `GET` | `/api/v1/heatmap` | Returns all mapped road coordinates, SI scores, and hazard status for Leaflet map. |
| `GET` | `/api/v1/telemetry/recent` | Returns recent 50 telemetry records. |
| `GET` | `/api/v1/analytics` | Returns aggregate metrics (Total logs, Avg SI, Potholes vs Cracks count). |
| `POST` | `/api/v1/sync` | Triggers batch push to Google Firebase Realtime Database. |

---

## 4. Database Schema (`logs/pathsense.db`)

### `telemetry_logs`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp`: TEXT (ISO8601)
- `latitude`, `longitude`: REAL (GPS coordinates)
- `speed_kmh`: REAL (Vehicle speed in km/h)
- `smoothness_index`: REAL (0.0 to 100.0)
- `road_status`: TEXT (EXCELLENT, GOOD, FAIR, POOR, SEVERE)
- `anomalies_detected`: INTEGER
- `hazard_alert`: INTEGER (0 or 1)
- `alert_distance_m`: REAL (Dynamic braking margin)
- `zone_name`: TEXT ('SKIT Campus / Jagatpura', etc.)
- `synced_to_cloud`: INTEGER (0 or 1)

### `anomaly_events`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp`: TEXT
- `track_id`: INTEGER (ByteTrack persistent ID)
- `class_name`: TEXT (pothole, alligator_crack, etc.)
- `confidence`: REAL (0.0 to 1.0)
- `latitude`, `longitude`: REAL
- `severity`: TEXT ('CRITICAL', 'MODERATE', 'LOW')
- `synced_to_cloud`: INTEGER
