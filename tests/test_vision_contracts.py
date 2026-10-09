"""Tests for M3 Vision Contract Foundation (TASK-012)."""

from __future__ import annotations

import time
import uuid

import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision import (
    BoundingBox,
    Detection,
    InferenceEngine,
    InferenceResult,
    ModelInput,
    Postprocessor,
    Preprocessor,
    RawInference,
    SpatialMetadata,
)


class DummyPreprocessor(Preprocessor):
    """Minimal deterministic test double for Preprocessor contract."""

    def preprocess(self, frame: Frame) -> ModelInput:
        metadata = SpatialMetadata(
            original_width=frame.width,
            original_height=frame.height,
            input_width=100,
            input_height=100,
            scale_x=1.0,
            scale_y=1.0,
            pad_x=0.0,
            pad_y=0.0,
        )
        # Neutral test data array (non-model-specific)
        data = np.zeros((100, 100))
        return ModelInput(data=data, metadata=metadata)


class DummyInferenceEngine(InferenceEngine):
    """Minimal deterministic test double for InferenceEngine contract."""

    def infer(self, model_input: ModelInput) -> RawInference:
        # Neutral test outputs tuple of ndarrays
        outputs = (np.zeros((1, 2)),)
        inference_time_ms = 5.0
        return RawInference(outputs=outputs, inference_time_ms=inference_time_ms)


def test_spatial_metadata_representation() -> None:
    """Verify SpatialMetadata exposes exactly the eight authorized spatial fields."""
    meta = SpatialMetadata(
        original_width=100,
        original_height=200,
        input_width=50,
        input_height=50,
        scale_x=0.5,
        scale_y=0.25,
        pad_x=10.0,
        pad_y=20.0,
    )
    assert meta.original_width == 100
    assert meta.original_height == 200
    assert meta.input_width == 50
    assert meta.input_height == 50
    assert meta.scale_x == 0.5
    assert meta.scale_y == 0.25
    assert meta.pad_x == 10.0
    assert meta.pad_y == 20.0


def test_model_input_representation() -> None:
    """Verify ModelInput represents ndarray data and SpatialMetadata."""
    data = np.zeros((50, 50))
    metadata = SpatialMetadata(
        original_width=100,
        original_height=100,
        input_width=50,
        input_height=50,
        scale_x=0.5,
        scale_y=0.5,
        pad_x=0.0,
        pad_y=0.0,
    )
    model_input = ModelInput(data=data, metadata=metadata)

    assert isinstance(model_input.data, np.ndarray)
    assert isinstance(model_input.metadata, SpatialMetadata)
    assert model_input.metadata.original_width == 100


def test_raw_inference_representation() -> None:
    """Verify RawInference represents tuple of ndarray outputs and inference duration in ms."""
    outputs = (np.zeros((2, 2)), np.ones((1,)))
    inference_time_ms = 10.0
    raw_inf = RawInference(outputs=outputs, inference_time_ms=inference_time_ms)

    assert isinstance(raw_inf.outputs, tuple)
    assert all(isinstance(arr, np.ndarray) for arr in raw_inf.outputs)
    assert len(raw_inf.outputs) == 2
    assert raw_inf.inference_time_ms == 10.0


def test_preprocessor_contract() -> None:
    """Verify Preprocessor test double accepts Frame and returns ModelInput."""
    image = np.zeros((200, 300))
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=300,
        height=200,
    )
    preprocessor = DummyPreprocessor()
    model_input = preprocessor.preprocess(frame)

    assert isinstance(model_input, ModelInput)
    assert isinstance(model_input.metadata, SpatialMetadata)
    assert model_input.metadata.original_width == 300
    assert model_input.metadata.original_height == 200


def test_inference_engine_contract() -> None:
    """Verify InferenceEngine test double consumes ModelInput and returns RawInference."""
    model_input = ModelInput(
        data=np.zeros((50, 50)),
        metadata=SpatialMetadata(100, 100, 50, 50, 0.5, 0.5, 0.0, 0.0),
    )
    engine = DummyInferenceEngine()
    raw_inf = engine.infer(model_input)

    assert isinstance(raw_inf, RawInference)
    assert isinstance(raw_inf.outputs, tuple)
    assert isinstance(raw_inf.inference_time_ms, float)
    assert raw_inf.inference_time_ms == 5.0


def test_deterministic_vision_chain() -> None:
    """Verify complete contract-level processing chain from Frame to RawInference."""
    image = np.zeros((150, 150))
    frame = Frame(
        id="test-frame-1",
        timestamp=1600000000.0,
        image=image,
        width=150,
        height=150,
    )

    preprocessor = DummyPreprocessor()
    engine = DummyInferenceEngine()

    model_input = preprocessor.preprocess(frame)
    raw_inf = engine.infer(model_input)

    assert isinstance(model_input, ModelInput)
    assert isinstance(raw_inf, RawInference)
    assert isinstance(model_input.data, np.ndarray)
    assert model_input.metadata.original_width == 150
    assert model_input.metadata.original_height == 150
    assert isinstance(raw_inf.outputs, tuple)
    assert len(raw_inf.outputs) >= 1
    assert raw_inf.inference_time_ms == 5.0


class DummyPostprocessor(Postprocessor):
    """Minimal deterministic test double for Postprocessor contract."""

    def process(
        self,
        raw_inference: RawInference,
        frame: Frame,
        metadata: SpatialMetadata,
    ) -> InferenceResult:
        bbox = BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0)
        detection = Detection(
            class_id=0,
            class_name="dummy_class",
            confidence=0.95,
            bounding_box=bbox,
        )
        return InferenceResult(
            frame_id=frame.id,
            timestamp=frame.timestamp,
            detections=(detection,),
            inference_time_ms=raw_inference.inference_time_ms,
        )


def test_bounding_box_representation() -> None:
    """Verify BoundingBox exposes floating-point xyxy coordinates."""
    box = BoundingBox(x1=1.5, y1=2.5, x2=10.0, y2=20.0)
    assert box.x1 == 1.5
    assert box.y1 == 2.5
    assert box.x2 == 10.0
    assert box.y2 == 20.0


def test_detection_representation() -> None:
    """Verify Detection represents class ID, name, confidence, and bounding box."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det = Detection(
        class_id=1,
        class_name="defect",
        confidence=0.88,
        bounding_box=box,
    )
    assert det.class_id == 1
    assert det.class_name == "defect"
    assert det.confidence == 0.88
    assert det.bounding_box == box


def test_inference_result_representation() -> None:
    """Verify InferenceResult represents frame ID, timestamp, detections, and inference time."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=5.0, y2=5.0)
    det = Detection(class_id=0, class_name="ok", confidence=0.9, bounding_box=box)
    result = InferenceResult(
        frame_id="frame-123",
        timestamp=1234567890.0,
        detections=(det,),
        inference_time_ms=12.5,
    )
    assert result.frame_id == "frame-123"
    assert result.timestamp == 1234567890.0
    assert len(result.detections) == 1
    assert result.detections[0] == det
    assert result.inference_time_ms == 12.5


def test_postprocessor_contract() -> None:
    """Verify Postprocessor abstract boundary and test double execution."""
    image = np.zeros((100, 100))
    frame = Frame(id="f-1", timestamp=100.0, image=image, width=100, height=100)
    metadata = SpatialMetadata(100, 100, 100, 100, 1.0, 1.0, 0.0, 0.0)
    raw_inf = RawInference(outputs=(np.zeros((1,)),), inference_time_ms=8.5)

    postprocessor = DummyPostprocessor()
    result = postprocessor.process(raw_inf, frame, metadata)

    assert isinstance(result, InferenceResult)
    assert result.frame_id == "f-1"
    assert result.timestamp == 100.0
    assert result.inference_time_ms == 8.5
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "dummy_class"
    assert result.detections[0].bounding_box.x1 == 10.0
