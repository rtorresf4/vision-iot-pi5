"""Tests for acquisition foundation (Frame, FrameSource, FakeFrameSource, OpenCVFrameSource, CameraError)."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from vision_iot.hardware import (
    CameraError,
    FakeFrameSource,
    Frame,
    FrameSource,
    OpenCVFrameSource,
)


class MockVideoCapture:
    """Mock for cv2.VideoCapture to test OpenCVFrameSource without hardware."""

    def __init__(self, device: int | str = 0) -> None:
        self.device = device
        self._opened = True
        self.released = False
        self.next_ok = True
        self.next_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def isOpened(self) -> bool:
        return self._opened and not self.released

    def read(self):
        if not self.isOpened():
            return False, None
        return self.next_ok, self.next_frame

    def release(self) -> None:
        self.released = True


class FailingOpenVideoCapture(MockVideoCapture):
    """Mock capturing device that fails to open."""

    def __init__(self, device: int | str = 0) -> None:
        super().__init__(device)
        self._opened = False


class FailingReadVideoCapture(MockVideoCapture):
    """Mock capturing device that succeeds opening but fails on read."""

    def __init__(self, device: int | str = 0) -> None:
        super().__init__(device)
        self.next_ok = False
        self.next_frame = None


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


def test_opencv_frame_source_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful camera opening, acquisition, Frame conversion, width/height derivation, and id/timestamp population."""
    monkeypatch.setattr(cv2, "VideoCapture", MockVideoCapture)

    source = OpenCVFrameSource(device=0)
    frame = source.get_frame()

    assert isinstance(frame, Frame)
    assert isinstance(frame.id, str)
    assert len(frame.id) > 0
    assert isinstance(frame.timestamp, float)
    assert isinstance(frame.image, np.ndarray)
    assert frame.image.ndim == 3
    assert frame.height == frame.image.shape[0] == 480
    assert frame.width == frame.image.shape[1] == 640

    source.release()


def test_opencv_frame_source_open_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that camera-open failure produces CameraError."""
    monkeypatch.setattr(cv2, "VideoCapture", FailingOpenVideoCapture)

    with pytest.raises(CameraError):
        OpenCVFrameSource(device=0)


def test_opencv_frame_source_read_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that frame-read failure produces CameraError."""
    monkeypatch.setattr(cv2, "VideoCapture", FailingReadVideoCapture)

    source = OpenCVFrameSource(device=0)
    with pytest.raises(CameraError):
        source.get_frame()
    source.release()


def test_opencv_frame_source_deterministic_release(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test explicit deterministic camera-resource release."""
    mock_instances = []

    class TrackingMockVideoCapture(MockVideoCapture):
        def __init__(self, device: int | str = 0) -> None:
            super().__init__(device)
            mock_instances.append(self)

    monkeypatch.setattr(cv2, "VideoCapture", TrackingMockVideoCapture)

    source = OpenCVFrameSource(device=0)
    assert len(mock_instances) == 1
    assert not mock_instances[0].released

    source.release()

    assert mock_instances[0].released
