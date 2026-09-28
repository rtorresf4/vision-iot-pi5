"""Camera acquisition contracts and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

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
