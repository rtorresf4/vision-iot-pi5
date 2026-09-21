# Vision + IoT on Raspberry Pi 5 (Technical Prototype)

> **Goal:** A foundational architectural prototype targeting Raspberry Pi 5 (8GB) for supervised object detection in a fixed-camera, single-package inspection scenario.
>
> This repository serves as a **technical prototype** and **educational portfolio**, documenting an architectural baseline for an industrial-style vision pipeline. It is not intended for production deployment.

---

## 🎯 Project Status
This project is currently in the **baseline architectural phase**.

**Current Implementation:**
- Base structure for inference using ONNX Runtime.
- MQTT event distribution infrastructure.
- Systemd service templates for deployment.
- Prototype CI pipeline (linting, type-checking, basic tests).
- Prototype dashboard for monitoring (pre-Architecture-v2 baseline).

**Target Architecture (v2):**
- Supervised object detection for visible defect identification.
- Reference Model: YOLO26n (ONNX baseline, NCNN as optimized candidate).
- Pipeline: Fixed-camera inspection, one package per inspection.

**Deferred / Future Extensions:**
- IoT sensor integration (DHT22, PIR telemetry).
- Advanced dashboard features (live video/Streamlit-WebRTC, SQLite historical tracking).

---

## 🏗️ System Architecture
The project follows a layered architecture (Hardware, Vision, Domain, Infrastructure).

For detailed design decisions and the current architectural baseline, please refer to:
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/adr/README.md`](docs/adr/README.md)

*Note: The system is designed for modularity. While a pre-Architecture-v2 prototype exists, development is ongoing to align it with the target v2 architecture.*

---

## 🛠️ Tech Stack
- **Hardware:** Raspberry Pi 5 (8GB), USB webcam.
- **Software:** Python, OpenCV, ONNX Runtime.
- **Model Strategy:**
  - Initial reference model: YOLO26n.
  - Baseline runtime: ONNX.
  - Optimized candidate: NCNN (production runtime undecided pending Pi 5 benchmarking).
- **Deployment:** systemd services, Makefile, pre-commit hooks.
- **CI/CD:** Prototype GitHub Actions (lint, type-check, tests).

---

## 🚀 Quick Start

### Setup on Ubuntu VM / Development Machine
```bash
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip ffmpeg
git clone https://github.com/<YOUR_USERNAME>/vision-iot-pi5.git
cd vision-iot-pi5
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Setup on Raspberry Pi 5
```bash
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip cmake ffmpeg mosquitto mosquitto-clients
git clone https://github.com/<YOUR_USERNAME>/vision-iot-pi5.git
cd vision-iot-pi5
python3 -m venv ~/vision
source ~/vision/bin/activate
python -m pip install --upgrade pip wheel
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

## 🧪 Cómo probar en tu PC (sin Raspberry Pi)

### 1) Preparar entorno
- Crear entorno e instalar deps:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  make setup
  make dev   # opcional (linter/formatter/hooks)
  ```

### 2) Comprobar la cámara
- Probar detección de dispositivos y resoluciones comunes (recomendado MJPG):
  ```bash
  make check-camera
  ```
- Si todo bien, capturar un pequeño lote con previsualización:
  ```bash
  make capture-ok
  make capture-defect
  ```
- Resultado:
  - Imágenes en `data/ok/` y `data/defect/`
  - Metadatos en `data/metadata.csv`

Consejos:
- Si `video0` falla, prueba `--device 1` en `apps/tools/check_camera.py`.
- 720p (1280x720) suele ir más fluido que 1080p en CPU.
- Cierra apps que usen la webcam (Zoom/Teams/Chrome) si no abre.

### 3) Probar el dashboard + MQTT local
1. Instala un broker local (Ubuntu/Debian):
   ```bash
   sudo apt update && sudo apt install -y mosquitto mosquitto-clients
   sudo systemctl enable --now mosquitto
   ```
2. Arranca el dashboard:
   ```bash
   make run-dashboard
   ```
3. Simula detecciones (publicación cada 1s):
   ```bash
   make sim-detections
   ```
4. Verás las métricas en el dashboard. Para parar el simulador: Ctrl+C.

### 4) (Opcional) Probar el detector en PC
- Coloca un modelo ONNX en `models/yolov8n.onnx` (o ajusta la ruta en `apps/pi_detector/config.yaml`).
- Conecta tu webcam y ejecuta:
  ```bash
  make run-detector
  ```
- El detector publicará resultados a MQTT en `factory/line1/detections`.

### 5) Calidad de código
```bash
make lint
make test
```

### Troubleshooting rápido
- Cámara no abre: revisa `make check-camera`, FOURCC `--fourcc MJPG` y permisos; prueba otro puerto USB.
- Dashboard no muestra datos: confirma que Mosquitto está activo (`sudo systemctl status mosquitto`) y que `make sim-detections` no lanza errores de conexión.
- Alto uso de CPU: reduce resolución a 640×480 en las herramientas y en la configuración.

---

## 🖥️ Recommended IDE — Visual Studio Code

It is recommended to install **Visual Studio Code from the official `.deb` package**, not the Snap Store, for better performance and compatibility.

### Install VS Code (.deb)
```bash
wget -O code.deb https://update.code.visualstudio.com/latest/linux-deb-x64/stable
sudo apt install ./code.deb
```

After installation, run with:
```bash
code
```

### Suggested Extensions
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Jupyter** (ms-toolsai.jupyter)
- **Remote - SSH** (ms-vscode-remote.remote-ssh)
- **Prettier - Code Formatter** (esbenp.prettier-vscode)
- **GitLens** (eamodio.gitlens)
- **Docker** (ms-azuretools.vscode-docker) (optional for future)

> Pro tip: mention in your portfolio that you used **Ubuntu 22.04 + VS Code (with Python, Pylance, Remote SSH)** → it shows a professional development workflow.

---

## 📦 Repository Structure
```
apps/
  pi_detector/         # Inference pipeline (ONNX) + MQTT publisher
  streamlit_dashboard/ # Prototype/partial monitoring dashboard
  sensors/             # IoT sensor integration (Deferred)
  tools/               # Dataset capture tool
deploy/
  systemd/             # Hardened systemd services
  scripts/             # Install/run scripts
docs/
  INDUSTRIAL_NOTES.md  # Supporting notes (Legacy)
models/                # Models (.onnx)
data/                  # Images, labels, metadata.csv
training/              # Training configs
tests/                 # Pytest tests
```

---

## 🧪 Continuous Integration
This repo includes a prototype **GitHub Actions workflow** (`.github/workflows/ci.yml`) that:
- Runs `ruff`, `black`, `mypy` for basic code quality.
- Executes unit tests (`pytest`).
- Builds on **Ubuntu latest** with Python 3.11.

> ✅ Demonstrates professional workflows.

---

## 📊 Performance Targets
*The following are benchmark goals for the final implementation, not currently achieved results.*

- **Detection performance:** Target mAP50 ≥ 0.80 on validation set.
- **Runtime speed:** Target ≥ 15 FPS @ 640×480 on Raspberry Pi 5.
- **Latency:** Target < 150 ms per frame end-to-end.
- **IoT reliability:** Target ≥ 99% MQTT message delivery, auto-reconnect < 5s.

---

## 📝 Educational Narrative
Each sprint is documented with:
- **What I did** → concrete steps.
- **Results** → initial screenshots, metrics, plots (as available).
- **Lessons learned** → insights, trade-offs, mistakes.

This repository serves as a **technical prototype** and a **teaching resource**.

---

## 🏭 Roadmap
- ✅ Architecture baseline (this repo).
- ⏳ Dataset capture (ongoing).
- ⏳ Model training & export (YOLO26n + Colab).
- ⏳ Inference on Pi5 (FPS & latency benchmarking).
- ⏳ Final demo video.

---

## 📜 License
MIT — free to use, modify, and share.
