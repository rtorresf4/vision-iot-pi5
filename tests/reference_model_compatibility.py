#!/usr/bin/env python3
"""Reference model compatibility validation script for YOLO26n ONNX artifact (TASK-016)."""

from __future__ import annotations

import argparse
import sys
import time
import uuid

import cv2
import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision import (
    InferenceResult,
    ModelInput,
    ONNXInferenceEngine,
    RawInference,
    YoloPostprocessor,
    YoloPreprocessor,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate YOLO26n ONNX reference model compatibility."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/yolo26n.onnx",
        help="Path to local YOLO26n ONNX model artifact",
    )
    args = parser.parse_args()

    model_path = args.model
    print(f"[INFO] Initializing reference model compatibility validation using model: {model_path}")

    # 1. Instantiate concrete components
    preprocessor = YoloPreprocessor(target_size=640)

    # 80 COCO class names
    coco_classes = [f"class_{i}" for i in range(80)]
    postprocessor = YoloPostprocessor(
        class_names=coco_classes,
        confidence_threshold=0.25,
        iou_threshold=0.45,
    )

    # 2. Construct synthetic BGR frame (720x1280)
    height, width = 720, 1280
    image = np.full((height, width, 3), 114, dtype=np.uint8)
    cv2.rectangle(image, (200, 150), (600, 500), (0, 255, 0), -1)

    frame_id = f"synth-frame-{uuid.uuid4()}"
    timestamp = time.time()
    frame = Frame(
        id=frame_id,
        timestamp=timestamp,
        image=image,
        width=width,
        height=height,
    )

    print(f"[INFO] Created synthetic Frame: id={frame.id}, shape={frame.image.shape}")

    # 3. Preprocess Frame -> ModelInput
    try:
        model_input = preprocessor.preprocess(frame)
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}", file=sys.stderr)
        return 1

    print(
        f"[INFO] Preprocessed ModelInput shape: {model_input.data.shape}, dtype: {model_input.data.dtype}"
    )
    assert isinstance(model_input, ModelInput)
    assert model_input.data.shape == (1, 3, 640, 640)

    # 4. Instantiate ONNXInferenceEngine (fails clearly if model absent)
    try:
        engine = ONNXInferenceEngine(model_path)
    except Exception as e:
        print(f"[ERROR] Failed to load ONNX model from {model_path}: {e}", file=sys.stderr)
        return 1

    print(
        f"[INFO] Loaded ONNXInferenceEngine session successfully. Input name: {engine.input_name}"
    )

    # 5. Execute inference ModelInput -> RawInference
    try:
        raw_inference = engine.infer(model_input)
    except Exception as e:
        print(f"[ERROR] Inference execution failed: {e}", file=sys.stderr)
        return 1

    print(
        f"[INFO] RawInference obtained. Outputs count: {len(raw_inference.outputs)}, inference_time_ms: {raw_inference.inference_time_ms:.2f}ms"
    )
    assert isinstance(raw_inference, RawInference)
    assert len(raw_inference.outputs) == 1
    out_tensor = raw_inference.outputs[0]
    print(f"[INFO] Output tensor shape: {out_tensor.shape}, dtype: {out_tensor.dtype}")
    assert out_tensor.shape == (1, 84, 8400)

    # 6. Execute postprocessing RawInference -> InferenceResult
    try:
        inference_result = postprocessor.process(raw_inference, frame, model_input.metadata)
    except Exception as e:
        print(f"[ERROR] Postprocessing failed: {e}", file=sys.stderr)
        return 1

    print(
        f"[INFO] Postprocessing completed successfully. Result detections count: {len(inference_result.detections)}"
    )
    assert isinstance(inference_result, InferenceResult)
    assert inference_result.frame_id == frame.id
    assert inference_result.timestamp == frame.timestamp
    assert inference_result.inference_time_ms == raw_inference.inference_time_ms

    for idx, det in enumerate(inference_result.detections):
        print(
            f"  Detection {idx}: class_id={det.class_id}, class_name={det.class_name}, confidence={det.confidence:.4f}, box=({det.bounding_box.x1:.1f}, {det.bounding_box.y1:.1f}, {det.bounding_box.x2:.1f}, {det.bounding_box.y2:.1f})"
        )

    print("[SUCCESS] Reference model compatibility validation completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
