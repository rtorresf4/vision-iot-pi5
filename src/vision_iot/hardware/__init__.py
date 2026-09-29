"""Hardware acquisition subsystem."""

from vision_iot.hardware.camera import (
    CameraError,
    FakeFrameSource,
    Frame,
    FrameSource,
    OpenCVFrameSource,
)

__all__ = [
    "Frame",
    "FrameSource",
    "FakeFrameSource",
    "OpenCVFrameSource",
    "CameraError",
]
