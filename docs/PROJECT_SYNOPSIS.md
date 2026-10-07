# STUDENT MINOR PROJECT PROPOSAL & SYNOPSIS
## Academic Session 2026 | Seventh Semester (CS-AI)

---

### 1. Title Page & Administrative Metadata
- **Project Title:** PathSense: Real-Time Edge-Vision for Road Condition Mapping
- **Academic Program:** Bachelor of Technology in Computer Science & Artificial Intelligence (CS-AI)
- **Institution:** Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur, Rajasthan
- **Project Team Members:**
  1. **Sharafat Khan** (Enrollment No: `23ESKCA098`, Branch: CS-AI)
  2. **Soham Manocha** (Enrollment No: `23ESKCA102`, Branch: CS-AI)
  3. **Sourabh Nagar** (Enrollment No: `23ESKCA105`, Branch: CS-AI)
  4. **Vedic Baurasi** (Enrollment No: `23ESKCA119`, Branch: CS-AI)
- **Assigned Faculty Supervisor:** Department of Computer Science & Engineering / AI

---

### 2. Project Summary (Abstract)
Current consumer navigation systems (e.g., Google Maps) effectively identify vehicular traffic congestion and travel duration but present a critical blind spot: they completely ignore physical road surface distress and quality. Drivers frequently navigate onto pothole-ridden or unpaved corridors that cause severe mechanical suspension damage and road accidents. **PathSense** addresses this challenge by introducing an end-to-end edge-computing artificial intelligence framework. A standard vehicle dashcam captures live forward roadway feeds; an optimized YOLOv8 deep learning network detects road anomalies in real-time; and a custom mathematical **Smoothness Index (SI)** scores roadway segments on a 0–100 scale based on anomaly area, frequency, and vehicle velocity. Georeferenced telemetry is logged and visualized on a dynamic geospatial web heatmap for both civilian navigation and automated municipal road infrastructure audits.

---

### 3. Problem Statement & Research Motivation
1. **Infrastructure Degradation:** Indian roadways suffer rapid degradation from extreme seasonal monsoon rains, overloaded commercial transport, and temperature cycles.
2. **Safety & Economic Hazards:** Ministry of Road Transport and Highways (MoRTH) data records between 1,480 and 1,850 annual fatalities attributed directly to road potholes and unpaved depressions.
3. **The Navigation Blind Spot:** Existing mapping applications route vehicles purely on transit time rather than ride quality.
4. **Inefficient Municipal Audits:** Municipal bodies (e.g., Jaipur Development Authority, PWD) currently depend on slow, labor-intensive manual inspections, delaying critical asphalt patch repairs by months.

---

### 4. Measurable Objectives
1. **Real-Time Edge Detection:** Deploy a vision-based deep neural network achieving $>30$ Frames Per Second (FPS) inference speed on standard mobile/laptop GPUs (NVIDIA RTX 2050) with detection mean Average Precision $\text{mAP@50} \ge 0.70$.
2. **Anomaly Deduplication:** Integrate an IoU/Centroid tracker (ByteTrack) to track continuous roadway anomalies across successive 30 FPS video frames, eliminating redundant duplicate penalties.
3. **Mathematical Smoothness Index Formulation:** Establish a dynamic, speed-scaled roadway health index ($SI \in [0, 100]$) correlating vehicle velocity ($V$), relative bounding box area ($A_i$), and anomaly severity weights ($C_i$).
4. **Geospatial Infrastructure Auditing:** Synthesize GPS telemetry and Smoothness Indices to generate interactive, color-coded road quality heatmaps.
5. **Speed-Adaptive Hazard Alerting:** Provide forward driver collision alerts with dynamic warning distances scaled to vehicle braking reaction parameters.

---

### 5. Proposed Methodology & Architecture (The Zero-Compromise Pipeline)

```
[Dashcam / Webcam 1080p Feed]
              │
              ▼
[OpenCV Video Stream Preprocessing (30 FPS)]
              │
              ▼
[YOLOv8 Edge Object Detector (Exported ONNX / PyTorch Engine)]
  ├── Pothole (D40)
  ├── Alligator Fatigue Cracking (D20)
  └── Longitudinal / Transverse Cracks (D00 / D10)
              │
              ▼
[ByteTrack Multi-Object Tracker & Deduplicator]
              │
              ▼
[Dynamic Smoothness Index (SI) & Hazard Safety Calculator]
  SI = 100 - Σ (α * A_i * V * C_i)
              │
              ▼
[Geospatial Telemetry Logger (GPS Lat/Lon + Velocity)]
              │
              ▼
[Streamlit & Folium Interactive Web Dashboard (JDA / Public Map)]
```

#### Phase 1: Hybrid Dataset & Domain Adaptation
- **Foundational Training:** The multi-national Road Damage Dataset 2022 (**RDD2022**), utilizing strictly the India subset containing ~10,000 annotated images of Indian asphalt and local damage morphologies.
- **Local Fine-Tuning:** 400–500 targeted video frames captured around the SKIT Jaipur campus, Mahal Road, and Jagatpura, manually annotated via Roboflow to eliminate domain shift.

#### Phase 2: Cloud-to-Edge System Architecture
- **Cloud Heavy Training:** Model training is offloaded to Cloud GPUs (Google Colab / Kaggle T4 / RunPod RTX 4090) utilizing PyTorch and Ultralytics YOLOv8 Medium at $640 \times 640$ resolution for 100 epochs.
- **Edge Inference:** The optimized weights (`best.pt` / `best.onnx`) are deployed onto consumer laptop GPUs (NVIDIA RTX 2050 4GB) using OpenCV, ensuring real-time local processing without dependency on intermittent mobile internet connectivity.

#### Phase 3: The Smoothness Index Formulation
$$\text{SI} = 100 - \sum_{i=1}^N \left(\alpha \cdot A_i \cdot \frac{V}{40.0} \cdot C_i \cdot \sqrt{\text{Conf}_i}\right)$$
- $N$: Unique anomalies within road segment.
- $A_i$: Normalized box area $\frac{\text{Box Area}}{\text{Frame Area}}$.
- $V$: Instantaneous vehicle velocity in km/h.
- $C_i$: Anomaly severity weight ($1.4$ for Pothole, $1.0$ for Alligator Cracks, $0.6$ for Longitudinal Cracks).
- $\alpha$: Environmental tuning factor ($0.45$).

---

### 6. Scope & Delimitations
- **In-Scope:** Real-time visual detection of surface damage, tracking, continuous road condition scoring, speed-scaled alert distance computation, and geospatial web map rendering.
- **Out-of-Scope (Delimitations):** Automated vehicle steering or active braking intervention (the system operates strictly as an Advanced Driver Assistance & Auditing advisory system). Operation in severe zero-visibility monsoon downpours or unilluminated night conditions without headlights is excluded from initial deployment.

---

### 7. Expected Outcomes & Deliverables
1. **Production-Ready Python Software Suite:** Complete modular pipeline spanning data preparation, model training, edge inference, and web dashboard.
2. **Fine-Tuned YOLOv8 Model Weights:** High-accuracy weights specifically adapted to Indian roadways.
3. **Interactive Geospatial Dashboard:** Web-based condition heatmap with route playback and municipal CSV/GeoJSON reporting.
4. **Academic Research Paper Draft:** Comprehensive manuscript ready for submission to IEEE/Springer student conferences.
