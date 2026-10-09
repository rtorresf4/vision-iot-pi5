"""Concrete reference domain inspection policies."""

from __future__ import annotations

from vision_iot.domain.contracts import (
    InspectionEvent,
    InspectionLogic,
    InspectionReason,
    InspectionStatus,
)
from vision_iot.vision import InferenceResult


class UnvalidatedReferenceInspectionLogic(InspectionLogic):
    """Concrete reference inspection policy returning inconclusive unsupported model events."""

    def inspect(
        self,
        result: InferenceResult,
        inspection_id: str,
    ) -> InspectionEvent:
        """Evaluate InferenceResult conservatively against unvalidated model constraints."""
        if not isinstance(inspection_id, str):
            raise TypeError(f"Expected inspection_id to be str, got {type(inspection_id)}")
        if not inspection_id.strip():
            raise ValueError("Inspection identifier cannot be empty or whitespace")

        return InspectionEvent(
            inspection_id=inspection_id,
            frame_id=result.frame_id,
            timestamp=result.timestamp,
            status=InspectionStatus.INCONCLUSIVE,
            reason=InspectionReason.UNSUPPORTED_MODEL,
            evidence=(),
        )
