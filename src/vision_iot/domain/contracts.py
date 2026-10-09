"""Domain inspection contracts and abstract base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from vision_iot.vision import Detection, InferenceResult


class InspectionStatus(str, Enum):
    """Enumeration of valid domain inspection statuses."""

    OK = "OK"
    DAMAGED = "DAMAGED"
    INCONCLUSIVE = "INCONCLUSIVE"


class InspectionReason(str, Enum):
    """Enumeration of valid domain inspection reasons."""

    UNSUPPORTED_MODEL = "UNSUPPORTED_MODEL"


@dataclass
class InspectionEvent:
    """Represents a project-owned domain inspection event."""

    inspection_id: str
    frame_id: str
    timestamp: float
    status: InspectionStatus
    reason: InspectionReason
    evidence: tuple[Detection, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.inspection_id, str):
            raise TypeError(f"Expected inspection_id to be str, got {type(self.inspection_id)}")
        if not self.inspection_id.strip():
            raise ValueError("Inspection identifier cannot be empty or whitespace")


class InspectionLogic(ABC):
    """Abstract base class for domain inspection logic."""

    @abstractmethod
    def inspect(
        self,
        result: InferenceResult,
        inspection_id: str,
    ) -> InspectionEvent:
        """Inspect an InferenceResult synchronously and return an InspectionEvent."""
        pass
