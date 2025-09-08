# Industrial-Ready Notes

This repository is structured and tooled for *edge* computer vision on Raspberry Pi 5 with a focus on reliability and reproducibility.

## What recruiters should notice
- Reproducible envs: split requirements (`requirements.txt`, `requirements-ci.txt`, `requirements-train.txt`).
- CI pipeline: lint, type checks, tests on GitHub Actions.
- systemd services with hardening to survive reboots and network hiccups.
- MQTT LWT and reconnect logic for operational robustness.
- Config-driven runtime (`apps/pi_detector/config.yaml`).

## Automotive/industrial awareness (Siemens/Bosch/BMW/Audi/Mercedes/NVIDIA)
- Telemetry & health: status topic with LWT; ready to extend with HW temps and FPS to a dedicated topic.
- Performance/latency: budgeted via FPS counter; compatible with INT8 quantization (TFLite) and alternative backends (ncnn, ONNX Runtime).
- Safety mindset: non-safety-critical demo, but code shows separation of concerns, logging, and graceful shutdown (SIGTERM) as a nod to ISO 26262 discipline.
- Portability to NVIDIA Jetson (Orin Nano): keep MQTT topics and config identical; swap the inference backend to TensorRT for higher FPS.
- Observability: logs are structured and CI enforces code quality gates.

## Next steps (roadmap)
- Add SQLite writer in the dashboard for historical trend analysis.
- Add `streamlit-webrtc` for low-latency video.
- Provide an ONNX/TFLite model card with measured mAP/FPS on Pi5 and PC.
