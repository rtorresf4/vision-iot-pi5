"""Concrete ONNX Runtime implementation of InferenceEngine (M3.C)."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import onnxruntime as ort

from vision_iot.vision.contracts import InferenceEngine, ModelInput, RawInference


class ONNXInferenceEngine(InferenceEngine):
    """Concrete inference engine using ONNX Runtime and CPUExecutionProvider."""

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {self.model_path}")

        try:
            self.session = ort.InferenceSession(
                str(self.model_path), providers=["CPUExecutionProvider"]
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create ONNX Runtime session from {self.model_path}: {e}"
            ) from e

        inputs = self.session.get_inputs()
        if len(inputs) != 1:
            raise ValueError(f"Baseline engine supports exactly 1 model input, found {len(inputs)}")

        self.input_name = inputs[0].name

    def infer(self, model_input: ModelInput) -> RawInference:
        """Execute synchronous inference on ModelInput using ONNX Runtime session."""
        data = model_input.data
        if not isinstance(data, np.ndarray):
            raise TypeError(f"ModelInput.data must be a numpy ndarray, got {type(data)}")

        start_time = time.perf_counter()
        try:
            raw_outputs = self.session.run(None, {self.input_name: data})
        except Exception as e:
            raise RuntimeError(f"Inference execution failed: {e}") from e
        end_time = time.perf_counter()

        inference_time_ms = (end_time - start_time) * 1000.0
        outputs = tuple(np.array(out, copy=False) for out in raw_outputs)

        return RawInference(outputs=outputs, inference_time_ms=inference_time_ms)
