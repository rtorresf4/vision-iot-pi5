# Vision + IoT on Raspberry Pi 5 (Educational Portfolio)

> **Goal:** Build an **edge AI system** on a Raspberry Pi 5 (8GB) that detects defects in industrial parts in real time, integrates IoT sensors, and streams results to an interactive dashboard.
>
> This repository is designed both as a **technical prototype** and as an **educational portfolio**, showing not only the *code* but also the *thought process* behind each design choice.

---

## 🎯 Project Objectives
- Implement a **lightweight object detection model** (YOLOv8n exported to ONNX/TFLite).
- Integrate **IoT sensors** (temperature, motion) via MQTT.
- Develop a **Streamlit dashboard** for live video, KPIs, and alerts.
- Train a **custom dataset** (OK vs Defective parts).
- Deliver a **robust industrial-ready prototype** documented for recruiters and engineers.

---

## 🏗️ System Architecture
```
[USB Camera] → [Raspberry Pi 5: OpenCV + YOLOv8n (ONNX/TFLite)]
    ├─ Detection results → MQTT → [Streamlit Dashboard]
    └─ Telemetry (CPU temp, FPS, health)

[Sensors: DHT22, PIR] → MQTT → Dashboard
```

**MQTT Topics:**
- `factory/line1/detections` → detection results (JSON per frame).
- `factory/line1/telemetry` → system telemetry (CPU, memory, temp).
- `factory/line1/sensors` → IoT data (temperature, humidity, motion).
- `factory/line1/status` → LWT for online/offline.

---

## 🛠️ Tech Stack
- **Hardware:** Raspberry Pi 5 (8GB), USB webcam, DHT22 sensor, PIR sensor.
- **Software:** Python, OpenCV, ONNX Runtime / TFLite, MQTT (Mosquitto), Streamlit.
- **ML Training:** Ultralytics YOLOv8, Google Colab / local GPU.
- **Deployment:** systemd services (with hardening), Makefile, pre-commit hooks.
- **CI/CD:** GitHub Actions (lint, type-check, tests).

---

## 🚀 Quick Start

### Setup on Raspberry Pi 5
```bash
sudo apt update && sudo apt install -y git python3-venv python3-pip cmake ffmpeg mosquitto mosquitto-clients
git clone https://github.com/<YOUR_USERNAME>/vision-iot-pi5.git
cd vision-iot-pi5
python3 -m venv ~/vision && source ~/vision/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Run detector
```bash
make run-detector
```

### Run dashboard
```bash
make run-dashboard
```

### Capture dataset
```bash
python apps/tools/capture_dataset.py --label ok
python apps/tools/capture_dataset.py --label defect --every 5
```

---

## 📦 Repository Structure
```
apps/
  pi_detector/         # Inference pipeline (ONNX/TFLite) + MQTT publisher
  streamlit_dashboard/ # Live KPIs and video
  sensors/             # IoT sensor integration
  tools/               # Dataset capture tool
deploy/
  systemd/             # Hardened systemd services
  scripts/             # Install/run scripts
docs/
  INDUSTRIAL_NOTES.md  # Notes for recruiters (industrial-ready)
models/                # YOLO models (.onnx, .tflite)
data/                  # Images, labels, metadata.csv
training/              # Training configs + Colab notebook placeholder
tests/                 # Pytest tests
```

---

## 🧪 Continuous Integration
This repo includes a **GitHub Actions workflow** (`.github/workflows/ci.yml`) that:
- Runs `ruff`, `black`, `mypy` to ensure code quality.
- Executes unit tests (`pytest`).
- Builds on **Ubuntu latest** with Python 3.11.

> ✅ Demonstrates professional workflows (important for industrial/automotive companies).

---

## 📊 Metrics to Deliver
- **Detection performance:** mAP50 ≥ 0.80 on validation set.
- **Runtime speed:** ≥ 15 FPS @ 640×480 on Raspberry Pi 5.
- **Latency:** < 150 ms per frame end-to-end.
- **IoT reliability:** ≥ 99% MQTT message delivery, auto-reconnect < 5s.

---

## 📝 Educational Narrative
Each sprint will be documented with:
- **What I did** → concrete steps.
- **Results** → screenshots, metrics, plots.
- **Lessons learned** → insights, trade-offs, mistakes.

This transforms the repository into both a **working prototype** and a **teaching resource**.

---

## 🏭 Industrial-Ready Highlights
- Config-driven runtime (`apps/pi_detector/config.yaml`).
- Robust MQTT client with LWT + exponential backoff.
- Hardened `systemd` services (`ProtectSystem`, `PrivateTmp`, etc.).
- Separate requirements for runtime, CI, and training.
- Capture tool for building **custom datasets**.

See [`docs/INDUSTRIAL_NOTES.md`](docs/INDUSTRIAL_NOTES.md) for recruiter-focused notes (Siemens, Bosch, BMW, Audi, Mercedes, NVIDIA).

---

## 📈 Roadmap
- ✅ Industrial-ready baseline (this repo).
- ⏳ Dataset capture (ongoing).
- ⏳ Model training & export (Colab + YOLOv8).
- ⏳ Dashboard enhancements (streamlit-webrtc, SQLite history).
- ⏳ Final demo video + LinkedIn/Medium post.

---

## 📜 License
MIT — free to use, modify, and share.
