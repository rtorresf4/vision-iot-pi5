"""Tests for acquisition foundation (Frame, FrameSource, FakeFrameSource)."""

from __future__ import annotations

import numpy as np

from vision_iot.hardware import FakeFrameSource, Frame, FrameSource


def test_frame_construction() -> None:
    """Test that Frame can be constructed with required contract fields and ADR-004 image properties."""
    height, width = 100, 200
    img = np.zeros((height, width, 3), dtype=np.uint8)
    frame = Frame(id="test-1", timestamp=1234567890.0, image=img, width=width, height=height)

    assert frame.id == "test-1"
    assert frame.timestamp == 1234567890.0
    assert isinstance(frame.image, np.ndarray)
    assert frame.image.ndim == 3
    assert frame.image.shape[0] == frame.height
    assert frame.image.shape[1] == frame.width
    assert frame.width == width
    assert frame.height == height


def test_fake_frame_source() -> None:
    """Test FakeFrameSource returns a valid known Frame."""
    height, width = 480, 640
    img = np.zeros((height, width, 3), dtype=np.uint8)
    expected_frame = Frame(
        id="known-frame-1", timestamp=100.0, image=img, width=width, height=height
    )
    source = FakeFrameSource(expected_frame)

    frame = source.get_frame()
    assert frame is expected_frame
    assert frame.id == "known-frame-1"
    assert isinstance(frame.image, np.ndarray)
    assert frame.image.ndim == 3
    assert frame.image.shape[0] == frame.height
    assert frame.image.shape[1] == frame.width


def test_frame_source_substitutability() -> None:
    """Test that FakeFrameSource can be consumed through the FrameSource abstraction."""

    def consume_source(src: FrameSource) -> Frame:
        return src.get_frame()

    height, width = 480, 640
    img = np.zeros((height, width, 3), dtype=np.uint8)
    expected_frame = Frame(id="sub-frame", timestamp=200.0, image=img, width=width, height=height)
    source: FrameSource = FakeFrameSource(expected_frame)
    frame = consume_source(source)

    assert frame is expected_frame
    assert isinstance(frame.image, np.ndarray)
    assert frame.image.ndim == 3
    assert frame.image.shape[0] == frame.height
    assert frame.image.shape[1] == frame.width


def test_repeated_acquisition_determinism() -> None:
    """Test repeated acquisition is deterministic and hardware-independent."""
    height, width = 10, 10
    img = np.zeros((height, width, 3), dtype=np.uint8)
    expected_frame = Frame(id="det-frame", timestamp=300.0, image=img, width=width, height=height)
    source = FakeFrameSource(expected_frame)

    frame1 = source.get_frame()
    frame2 = source.get_frame()

    assert frame1 is expected_frame
    assert frame2 is expected_frame
    assert frame1 == frame2
    assert isinstance(frame1.image, np.ndarray)
    assert frame1.image.ndim == 3
    assert frame1.image.shape[0] == frame1.height
    assert frame1.image.shape[1] == frame1.width
