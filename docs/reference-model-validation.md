# Reference Model Validation Report (TASK-016)

## 1. Overview

This document records the empirical compatibility validation of the Architecture-v2 reference vision pipeline components against a real pretrained YOLO26n ONNX model artifact (`models/yolo26n.onnx`).

The execution path validated is:
```text
Synthetic Frame (BGR)
      |
      v
YoloPreprocessor (Letterbox 640x640, RGB, Normalize, CHW, Batch 1)
      |
      v
ModelInput (ndarray, SpatialMetadata)
      |
      v
ONNXInferenceEngine (ONNX Runtime, CPUExecutionProvider)
      |
      v
RawInference (Outputs: tuple[ndarray, ...], inference_time_ms)
      |
      v
YoloPostprocessor (Confidence filtering, Model-space NMS, Coordinate restoration, Clipping)
      |
      v
InferenceResult (Project-owned Detections, frame_id, timestamp)
```

---

## 2. Artifact Provenance & Export Configuration

- **Model Identity:** YOLO26n (`yolo26n.pt` pretrained weights)
- **Model Source:** Ultralytics official assets release (`v8.4.0`)
- **Ultralytics Version:** `8.4.174`
- **PyTorch Version:** `2.14.1+cu130`
- **Export Environment:** Isolated model-preparation virtual environment (`/home/rulikis/.gemini/tmp/vision-iot-pi5/export_sandbox`) separate from the Architecture-v2 production runtime.
- **Export Command / Parameters:**
  ```python
  from ultralytics import YOLO
  model = YOLO("yolo26n.pt")
  model.export(format="onnx", imgsz=640, batch=1)
  ```
- **Export Mode / NMS Selection:** Default export without embedded NMS (`nms=None`), producing raw one-to-many detection output.
- **Input Dimensions:** 640 × 640 spatial dimensions, batch size 1, 3 channels (CHW).
- **ONNX Opset Version:** `18` (with `onnxslim` optimization applied during export).
- **Artifact Path:** `models/yolo26n.onnx` (ignored by Git, untracked).
- **Artifact File Size:** ~9.5 MB
- **SHA-256 Checksum:** `0fa3c8e015d5c9dae898c3f2a3287d805594fa0499d1d186d822986c858b146b`

---

## 3. ONNX Interface Metadata Inspection

### Input Metadata
- **Name:** `images`
- **Shape:** `[1, 3, 640, 640]`
- **Data Type:** `FLOAT32` (ElemType 1)
- **Compatibility:** Fully compatible with `YoloPreprocessor` output representation (`ModelInput.data`).

### Output Metadata
- **Name:** `output0`
- **Shape:** `[1, 84, 8400]`
- **Layout:** `(batch, channels, candidates)` where `84 = 4 (xywh box) + 80 (COCO class scores)`.
- **Data Type:** `FLOAT32` (ElemType 1)
- **Compatibility:** Matches ADR-002 reference assumptions and `YoloPostprocessor` interface expectations.

---

## 4. Runtime & Execution Environment

- **Architecture-v2 Runtime Environment:** `.venv` (Python 3.12.3)
- **ONNX Runtime Version:** `1.22.1`
- **Execution Provider:** `CPUExecutionProvider`
- **Network Dependency:** None (fully offline execution).

---

## 5. Integrated Execution Validation Results

Executing the compatibility validation script:
```bash
python tests/reference_model_compatibility.py --model models/yolo26n.onnx
```

**Observed Output Log:**
```text
[INFO] Initializing reference model compatibility validation using model: models/yolo26n.onnx
[INFO] Created synthetic Frame: id=synth-frame-..., shape=(720, 1280, 3)
[INFO] Preprocessed ModelInput shape: (1, 3, 640, 640), dtype: float32
[INFO] Loaded ONNXInferenceEngine session successfully. Input name: images
[INFO] RawInference obtained. Outputs count: 1, inference_time_ms: 19.34ms
[INFO] Output tensor shape: (1, 84, 8400), dtype: float32
[INFO] Postprocessing completed successfully. Result detections count: 0
[SUCCESS] Reference model compatibility validation completed successfully!
```

- **Model Loading:** Successful.
- **Input Binding & Inference:** Successful (`inference_time_ms` recorded without wall-clock timestamp confusion).
- **Raw Inference Output:** Exactly 1 tensor of shape `(1, 84, 8400)`.
- **Postprocessing:** Successfully consumed `RawInference`, preserved `frame_id` and `timestamp`, and returned a valid `InferenceResult`. Zero detections were produced on the synthetic test pattern, which satisfies the validation invariant.

---

## 6. Deterministic Regression & Quality Gate Results

All existing unit tests and workspace quality checks passed successfully:

- `black --check .` — PASSED
- `ruff check .` — PASSED
- `mypy apps src` — PASSED
- `pytest -q` — PASSED (all component tests and contract validation tests green)
- `make lint` — PASSED
- `make test` — PASSED
- `pre-commit run --all-files` — PASSED
- `git diff --check` — PASSED
