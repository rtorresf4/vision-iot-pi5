"""Tests for M3.B Reference Vision Preprocessing (TASK-013)."""

from __future__ import annotations

import time
import uuid

import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision import ModelInput, YoloPreprocessor


def test_yolo_preprocessor_square() -> None:
    """Verify square source preprocessing (640x640 to 640x640)."""
    image = np.full((640, 640, 3), 100, dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=640,
        height=640,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    assert isinstance(model_input, ModelInput)
    assert model_input.data.shape == (1, 3, 640, 640)
    assert model_input.metadata.original_width == 640
    assert model_input.metadata.original_height == 640
    assert model_input.metadata.input_width == 640
    assert model_input.metadata.input_height == 640
    assert model_input.metadata.scale_x == 1.0
    assert model_input.metadata.scale_y == 1.0
    assert model_input.metadata.pad_x == 0.0
    assert model_input.metadata.pad_y == 0.0


def test_yolo_preprocessor_landscape() -> None:
    """Verify landscape source preprocessing (1280x720 to 640x640)."""
    image = np.full((720, 1280, 3), 100, dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=1280,
        height=720,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    assert model_input.data.shape == (1, 3, 640, 640)
    meta = model_input.metadata
    assert meta.original_width == 1280
    assert meta.original_height == 720
    assert meta.input_width == 640
    assert meta.input_height == 640
    # Scale: 640 / 1280 = 0.5 for both dimensions
    assert meta.scale_x == 0.5
    assert meta.scale_y == 0.5
    # Resized height: 720 * 0.5 = 360. Padding top/bottom: (640 - 360) / 2 = 140.
    assert meta.pad_x == 0.0
    assert meta.pad_y == 140.0


def test_yolo_preprocessor_portrait() -> None:
    """Verify portrait source preprocessing (720x1280 to 640x640)."""
    image = np.full((1280, 720, 3), 100, dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=720,
        height=1280,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    assert model_input.data.shape == (1, 3, 640, 640)
    meta = model_input.metadata
    assert meta.original_width == 720
    assert meta.original_height == 1280
    assert meta.input_width == 640
    assert meta.input_height == 640
    # Scale: 640 / 1280 = 0.5 for both dimensions
    assert meta.scale_x == 0.5
    assert meta.scale_y == 0.5
    # Resized width: 720 * 0.5 = 360. Padding left/right: (640 - 360) / 2 = 140.
    assert meta.pad_x == 140.0
    assert meta.pad_y == 0.0


def test_yolo_preprocessor_numerical_and_tensor() -> None:
    """Verify output dtype is float32 and value range is [0.0, 1.0]."""
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=100,
        height=100,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    assert model_input.data.dtype == np.float32
    assert np.all(model_input.data >= 0.0)
    assert np.all(model_input.data <= 1.0)
    assert model_input.data.shape == (1, 3, 640, 640)


def test_yolo_preprocessor_color_conversion() -> None:
    """Verify BGR to RGB color conversion for reference path."""
    # Create a 1x1 image with distinct B, G, R values: B=10, G=100, R=200
    image = np.array([[[10, 100, 200]]], dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=1,
        height=1,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    # In CHW format after BGR->RGB conversion, channel 0 is R (200), channel 1 is G (100), channel 2 is B (10)
    data = model_input.data
    r_val = data[0, 0, 0, 0]  # R channel
    g_val = data[0, 1, 0, 0]  # G channel
    b_val = data[0, 2, 0, 0]  # B channel

    assert np.isclose(r_val, 200.0 / 255.0, atol=1e-5)
    assert np.isclose(g_val, 100.0 / 255.0, atol=1e-5)
    assert np.isclose(b_val, 10.0 / 255.0, atol=1e-5)


def test_yolo_preprocessor_padding_behavior() -> None:
    """Verify letterbox padding uses value 114 per channel (normalized to 114/255)."""
    image = np.zeros((720, 1280, 3), dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=1280,
        height=720,
    )
    preprocessor = YoloPreprocessor(target_size=640)
    model_input = preprocessor.preprocess(frame)

    # Check padding region (top-left corner: row 0, col 0 is in the top padding band)
    expected_pad_val = 114.0 / 255.0
    assert np.isclose(model_input.data[0, 0, 0, 0], expected_pad_val, atol=1e-5)
    assert np.isclose(model_input.data[0, 1, 0, 0], expected_pad_val, atol=1e-5)
    assert np.isclose(model_input.data[0, 2, 0, 0], expected_pad_val, atol=1e-5)


def test_yolo_preprocessor_effective_spatial_metadata() -> None:
    """Verify spatial metadata reflects exact effective integer-rounded resize and padding geometry."""
    orig_w = 643
    orig_h = 481
    target = 640

    image = np.zeros((orig_h, orig_w, 3), dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=orig_w,
        height=orig_h,
    )
    preprocessor = YoloPreprocessor(target_size=target)
    model_input = preprocessor.preprocess(frame)

    meta = model_input.metadata

    # Independently derived expected geometry
    r = min(target / orig_w, target / orig_h)
    expected_new_w = int(round(orig_w * r))
    expected_new_h = int(round(orig_h * r))
    expected_dw = target - expected_new_w
    expected_dh = target - expected_new_h
    expected_left = expected_dw // 2
    expected_top = expected_dh // 2

    expected_scale_x = float(expected_new_w) / orig_w
    expected_scale_y = float(expected_new_h) / orig_h
    expected_pad_x = float(expected_left)
    expected_pad_y = float(expected_top)

    assert meta.original_width == orig_w
    assert meta.original_height == orig_h
    assert meta.input_width == target
    assert meta.input_height == target
    assert np.isclose(meta.scale_x, expected_scale_x, atol=1e-5)
    assert np.isclose(meta.scale_y, expected_scale_y, atol=1e-5)
    assert np.isclose(meta.pad_x, expected_pad_x, atol=1e-5)
    assert np.isclose(meta.pad_y, expected_pad_y, atol=1e-5)

    # Demonstrate that integer resize rounding causes scale_x and scale_y to differ
    assert not np.isclose(meta.scale_x, meta.scale_y, atol=1e-4)


def test_yolo_preprocessor_custom_target_size() -> None:
    """Verify custom target size configuration works correctly."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    frame = Frame(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        image=image,
        width=100,
        height=100,
    )
    preprocessor = YoloPreprocessor(target_size=320)
    model_input = preprocessor.preprocess(frame)

    assert model_input.data.shape == (1, 3, 320, 320)
    assert model_input.metadata.input_width == 320
    assert model_input.metadata.input_height == 320
