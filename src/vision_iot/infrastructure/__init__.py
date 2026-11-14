"""Infrastructure package for vision_iot."""

from __future__ import annotations

from vision_iot.infrastructure.inspection_event_serializer import (
    InspectionEventSerializationError,
    InspectionEventSerializer,
)

__all__ = [
    "InspectionEventSerializationError",
    "InspectionEventSerializer",
]
