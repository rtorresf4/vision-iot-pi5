"""Tests for M3 Vision Contract Foundation (TASK-012)."""

from __future__ import annotations

import time
import uuid

import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision import (
    InferenceEngine,
    ModelInput,
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
