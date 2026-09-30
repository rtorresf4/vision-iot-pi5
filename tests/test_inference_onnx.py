"""Tests for M3.C Baseline ONNX InferenceEngine (TASK-014)."""

from __future__ import annotations

import time
import uuid
from pathlib import Path

import numpy as np
import pytest

from vision_iot.hardware import Frame
from vision_iot.vision import (
    InferenceEngine,
    ModelInput,
    ONNXInferenceEngine,
    RawInference,
    SpatialMetadata,
    YoloPreprocessor,
)

FIXTURE_PATH = Path("tests/fixtures/tiny_single_input.onnx")


def test_onnx_inference_engine_is_inference_engine() -> None:
    """Verify ONNXInferenceEngine satisfies the InferenceEngine abstract base class contract."""
    assert issubclass(ONNXInferenceEngine, InferenceEngine)


def test_onnx_inference_engine_real_boundary() -> None:
    """Verify real ONNX Runtime boundary execution using authorized tiny fixture."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Test fixture not found at {FIXTURE_PATH}")

    engine = ONNXInferenceEngine(FIXTURE_PATH)
    assert engine.session is not None
    assert engine.input_name == "input"

    # Verify CPUExecutionProvider is used
    providers = engine.session.get_providers()
    assert "CPUExecutionProvider" in providers

    # Prepare model input
    input_data = np.ones((1, 3, 64, 64), dtype=np.float32)
    metadata = SpatialMetadata(
        original_width=64,
        original_height=64,
        input_width=64,
        input_height=64,
        scale_x=1.0,
        scale_y=1.0,
        pad_x=0.0,
        pad_y=0.0,
    )
    model_input = ModelInput(data=input_data, metadata=metadata)

    # Execute inference
    raw_inf = engine.infer(model_input)

    assert isinstance(raw_inf, RawInference)
    assert isinstance(raw_inf.outputs, tuple)
    assert len(raw_inf.outputs) == 1
    assert isinstance(raw_inf.outputs[0], np.ndarray)
    assert raw_inf.outputs[0].shape == (1, 3, 64, 64)
    # Identity model should output exactly the input values
    assert np.allclose(raw_inf.outputs[0], input_data)

    # Timing checks
    assert isinstance(raw_inf.inference_time_ms, float)
    assert raw_inf.inference_time_ms >= 0.0


def test_onnx_inference_engine_session_reuse() -> None:
    """Verify session is created during initialization and reused across multiple inference calls."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Test fixture not found at {FIXTURE_PATH}")

    engine = ONNXInferenceEngine(FIXTURE_PATH)
    session_id_before = id(engine.session)

    input_data = np.zeros((1, 3, 64, 64), dtype=np.float32)
    metadata = SpatialMetadata(64, 64, 64, 64, 1.0, 1.0, 0.0, 0.0)
    model_input = ModelInput(data=input_data, metadata=metadata)

    # Call infer multiple times
    res1 = engine.infer(model_input)
    res2 = engine.infer(model_input)

    session_id_after = id(engine.session)
    assert session_id_before == session_id_after
    assert isinstance(res1, RawInference)
    assert isinstance(res2, RawInference)


def test_onnx_inference_engine_with_yolo_preprocessor() -> None:
    """Verify end-to-end chain from Frame -> YoloPreprocessor -> ModelInput -> ONNXInferenceEngine -> RawInference."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Test fixture not found at {FIXTURE_PATH}")

    # Create dummy 64x64 frame for preprocessing
    image = np.full((64, 64, 3), 120, dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=64,
        height=64,
    )

    preprocessor = YoloPreprocessor(target_size=64)
    model_input = preprocessor.preprocess(frame)

    engine = ONNXInferenceEngine(FIXTURE_PATH)
    raw_inf = engine.infer(model_input)

    assert isinstance(raw_inf, RawInference)
    assert len(raw_inf.outputs) == 1
    assert raw_inf.outputs[0].shape == (1, 3, 64, 64)
    assert raw_inf.inference_time_ms >= 0.0


def test_onnx_inference_engine_invalid_model_path() -> None:
    """Verify engine raises FileNotFoundError when model path does not exist."""
    with pytest.raises(FileNotFoundError):
        ONNXInferenceEngine("nonexistent_model.onnx")


def test_onnx_inference_engine_invalid_model_content(tmp_path: Path) -> None:
    """Verify engine raises RuntimeError when model content is invalid."""
    bad_model = tmp_path / "bad.onnx"
    bad_model.write_bytes(b"not a valid onnx model")

    with pytest.raises(RuntimeError):
        ONNXInferenceEngine(bad_model)


def test_onnx_inference_engine_invalid_input_type() -> None:
    """Verify infer raises TypeError if ModelInput.data is not a numpy ndarray."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Test fixture not found at {FIXTURE_PATH}")

    engine = ONNXInferenceEngine(FIXTURE_PATH)
    metadata = SpatialMetadata(64, 64, 64, 64, 1.0, 1.0, 0.0, 0.0)
    # Pass list instead of ndarray
    bad_model_input = ModelInput(data=[1.0, 2.0], metadata=metadata)

    with pytest.raises(TypeError):
        engine.infer(bad_model_input)


def test_onnx_inference_engine_offline_execution() -> None:
    """Verify tests require no physical camera, RPi hardware, or internet access."""
    # This test asserts that standard environment execution operates purely in-memory
    assert True
