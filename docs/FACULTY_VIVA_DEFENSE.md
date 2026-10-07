# PathSense: Faculty Viva Voce & Defense Guide
## Minor Project Evaluation | Swami Keshvanand Institute of Technology (SKIT), Jaipur
### Team Presenters: 1. Sharafat Khan (23ESKCA098), 2. Soham Manocha (23ESKCA102), 3. Sourabh Nagar (23ESKCA105), 4. Vedic Baurasi (23ESKCA119) [7th Sem, CS-AI]

---

### Core Strategy for Viva Success:
Professors evaluate whether you built an **End-to-End Engineering System** or merely ran a generic tutorial script. Anchor your answers on three pillars:
1. **Systems Architecture:** Cloud training for heavy models + Edge inference on local hardware.
2. **Domain Adaptation:** Transfer learning with RDD2022 India + localized SKIT/Jaipur campus data.
3. **Engineering Logic:** The custom Smoothness Index (SI) and ByteTrack deduplication.

---

### Key Viva Questions & Bulletproof Answers

#### Q1: "Why did you choose YOLOv8 when newer architectures (like YOLO11 or YOLO26) exist?"
> **Winning Answer:**  
> *"Sir/Ma'am, while newer experimental versions exist, YOLOv8 represents the most battle-tested, production-stable architecture with proven ONNX export runtimes. For a mission-critical edge deployment on our laptop's RTX 2050 (4GB VRAM), YOLOv8 guarantees zero experimental runtime bugs and consistently achieves our target of >30 FPS. Furthermore, the core scientific innovation of PathSense is not simply the vision backbone, but the mathematical Smoothness Index, tracking deduplication, and geospatial mapping engine built on top of it."*

---

#### Q2: "How can your 4GB RTX 2050 laptop train a deep vision model on 10,000 images without Out-Of-Memory (OOM) errors?"
> **Winning Answer:**  
> *"We implemented a decoupled Cloud-to-Edge architecture. We do NOT train on our laptops. Training YOLOv8 Medium with 10,000 high-resolution images is offloaded to Cloud GPUs (e.g., Google Colab T4 / RunPod RTX 4090 with 16–24GB VRAM). Once training converges, we export the optimized lightweight weights (`best.pt` or `best.onnx`, ~40MB) and deploy them locally onto our laptop's RTX 2050, which handles inference easily at 30+ FPS."*

---

#### Q3: "Pothole detection is a common project. What makes your project final-year worthy (10/10)?"
> **Winning Answer:**  
> *"Generic student projects stop at drawing bounding boxes on a pre-recorded MP4 video file. PathSense introduces three major engineering distinctions:  
> 1. **Deduplication:** At 30 FPS, a moving car sees the same pothole for 30–45 consecutive frames. Without tracking, naive systems count one pothole 40 times. We integrated an IoU/ByteTrack tracker to ensure each physical pothole is logged exactly once.  
> 2. **Algorithmic Smoothness Index:** We developed a mathematical formulation correlating bounding box area ($A_i$), anomaly severity ($C_i$), and vehicle velocity ($V$) to compute a continuous 0–100 road health score.  
> 3. **Full-Stack Civic Product:** We feed live coordinates into a database to render an interactive web heatmap for municipal bodies like the Jaipur Development Authority (JDA) to prioritize asphalt repairs."*

---

#### Q4: "If you train on an online dataset, how do you know it will work on the dusty roads of Jaipur?"
> **Winning Answer:**  
> *"We specifically accounted for Domain Shift. Instead of training on generic Western or Japanese datasets, we extracted the India subset of the RDD2022 dataset (~10,000 images of Indian road distress). We then used Transfer Learning and fine-tuned the model with 400–500 custom images captured around SKIT campus and Jagatpura roads using 1-FPS frame extraction. This hyper-specializes the model to the exact asphalt texture, sun glare, and dust conditions of Jaipur."*

---

#### Q5: "How does your system handle shadows or dark water patches without creating false positives?"
> **Winning Answer:**  
> *"We implement two layers of defense:  
> First, during model training, we apply aggressive data augmentations (Mosaic, MixUp, and brightness/contrast shifts) so the neural network learns deep textural features of depth and cracked asphalt edges rather than merely dark pixel clusters.  
> Second, our Smoothness Index is computed over a sliding temporal/spatial window (50 meters). A transient optical shadow may flicker for 1–2 frames, but genuine physical road damage persists across multiple tracked frames. Our tracker requires consecutive confirmation before registering an anomaly."*

---

#### Q6: "Why edge inference in the car instead of streaming the video to a cloud server via 5G?"
> **Winning Answer:**  
> *"Streaming high-definition 1080p video at 30 FPS requires continuous high-bandwidth uplink (>15 Mbps). Cellular connectivity frequently drops or suffers high latency on Indian roads and highways. If a vehicle travels at 60 km/h, network buffering latency of even 500 milliseconds means the car travels 8.3 meters before an alert arrives. Edge inference on the local RTX 2050 processes frames in under 30 milliseconds with zero network dependency. Only lightweight telemetry text (<1 KB) is synced to the cloud."*

---

#### Q7: "What is the difference between the AI and the ML part of your project?"
> **Winning Answer:**  
> *"Machine Learning is the perceptual engine—specifically, the convolutional neural network within YOLOv8 learning visual representations of potholes and alligator cracks from the RDD2022 dataset.  
> Artificial Intelligence is the overarching decision-making system—it ingests those ML bounding box detections, tracks anomalies over time, integrates vehicle dynamics and GPS speed, computes the Smoothness Index, calculates speed-adaptive alert distances, and autonomously updates municipal hazard heatmaps."*
