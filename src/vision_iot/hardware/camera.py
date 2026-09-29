"""Camera acquisition contracts and implementations."""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Frame:
    """Represents one acquired image and minimum downstream metadata."""

    id: str
    timestamp: float
    image: np.ndarray
    width: int
    height: int


class FrameSource(ABC):
    """Abstract acquisition boundary for producing Frame instances."""

    @abstractmethod
    def get_frame(self) -> Frame:
        """Acquire and return a single Frame synchronously."""
        pass


class FakeFrameSource(FrameSource):
    """Deterministic frame source for hardware-independent testing."""

    def __init__(self, frame: Frame) -> None:
        self._frame = frame

    def get_frame(self) -> Frame:
        return self._frame


class CameraError(Exception):
    """Raised when camera acquisition or OpenCV operations fail."""

    pass


class OpenCVFrameSource(FrameSource):
    """OpenCV-backed concrete implementation of FrameSource."""

    def __init__(self, device: int | str = 0) -> None:
        self._device = device
        self._cap: cv2.VideoCapture | None = cv2.VideoCapture(device)
        if self._cap is None or not self._cap.isOpened():
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            raise CameraError(f"Failed to open camera device: {device}")

    def get_frame(self) -> Frame:
        if self._cap is None or not self._cap.isOpened():
            raise CameraError("Camera is not open or has been released.")

        ok, image = self._cap.read()
        if not ok or image is None:
            raise CameraError("Failed to read frame from camera.")

        frame_id = str(uuid.uuid4())
        timestamp = time.time()
        height, width = image.shape[:2]

        return Frame(
            id=frame_id,
            timestamp=timestamp,
            image=image,
            width=width,
            height=height,
        )

    def release(self) -> None:
        """Deterministically release the underlying camera resource."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
