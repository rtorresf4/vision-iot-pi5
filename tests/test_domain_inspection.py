"""Tests for M4 Domain Inspection Foundation (TASK-017)."""

from __future__ import annotations

import pytest

from vision_iot.domain import (
    InspectionEvent,
    InspectionLogic,
    InspectionReason,
    InspectionStatus,
    UnvalidatedReferenceInspectionLogic,
)
from vision_iot.vision import BoundingBox, Detection, InferenceResult


def test_inspection_status_values() -> None:
    """Verify InspectionStatus contains exactly OK, DAMAGED, and INCONCLUSIVE."""
    assert InspectionStatus.OK.value == "OK"
    assert InspectionStatus.DAMAGED.value == "DAMAGED"
    assert InspectionStatus.INCONCLUSIVE.value == "INCONCLUSIVE"
    assert set(InspectionStatus) == {
        InspectionStatus.OK,
        InspectionStatus.DAMAGED,
        InspectionStatus.INCONCLUSIVE,
    }


def test_inspection_reason_values() -> None:
    """Verify InspectionReason contains exactly UNSUPPORTED_MODEL."""
    assert InspectionReason.UNSUPPORTED_MODEL.value == "UNSUPPORTED_MODEL"
    assert set(InspectionReason) == {InspectionReason.UNSUPPORTED_MODEL}


def test_inspection_event_fields() -> None:
    """Verify InspectionEvent exposes exactly the six approved fields."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det = Detection(class_id=0, class_name="person", confidence=0.9, bounding_box=box)
    event = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.INCONCLUSIVE,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det,),
    )
    assert event.inspection_id == "insp-1"
    assert event.frame_id == "frame-1"
    assert event.timestamp == 100.0
    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == (det,)


def test_unvalidated_reference_inspection_logic_empty_detections() -> None:
    """Verify reference policy with empty detections produces INCONCLUSIVE / UNSUPPORTED_MODEL / () clearing."""
    result = InferenceResult(
        frame_id="f-empty",
        timestamp=123.45,
        detections=(),
        inference_time_ms=10.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-empty")

    assert event.inspection_id == "insp-empty"
    assert event.frame_id == "f-empty"
    assert event.timestamp == 123.45
    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == ()


def test_unvalidated_reference_inspection_logic_single_detection() -> None:
    """Verify reference policy with one synthetic detection produces conservative inconclusive result."""
    box = BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0)
    det = Detection(class_id=0, class_name="bottle", confidence=0.85, bounding_box=box)
    result = InferenceResult(
        frame_id="f-single",
        timestamp=456.78,
        detections=(det,),
        inference_time_ms=15.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-single")

    assert event.inspection_id == "insp-single"
    assert event.frame_id == "f-single"
    assert event.timestamp == 456.78
    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == ()
    assert event.status not in (InspectionStatus.OK, InspectionStatus.DAMAGED)


def test_unvalidated_reference_inspection_logic_multiple_detections() -> None:
    """Verify reference policy with multiple synthetic detections produces conservative inconclusive result."""
    box1 = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    box2 = BoundingBox(x1=20.0, y1=20.0, x2=30.0, y2=30.0)
    det1 = Detection(class_id=39, class_name="bottle", confidence=0.92, bounding_box=box1)
    det2 = Detection(class_id=41, class_name="cup", confidence=0.78, bounding_box=box2)
    result = InferenceResult(
        frame_id="f-multi",
        timestamp=789.0,
        detections=(det1, det2),
        inference_time_ms=20.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-multi")

    assert event.inspection_id == "insp-multi"
    assert event.frame_id == "f-multi"
    assert event.timestamp == 789.0
    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == ()


@pytest.mark.parametrize("class_id", [0, 15, 39, 99])
def test_unvalidated_reference_inspection_logic_varying_class_ids(class_id: int) -> None:
    """Verify varying class IDs do not alter the inspection outcome."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=5.0, y2=5.0)
    det = Detection(
        class_id=class_id, class_name=f"class_{class_id}", confidence=0.9, bounding_box=box
    )
    result = InferenceResult(
        frame_id="f-class",
        timestamp=10.0,
        detections=(det,),
        inference_time_ms=5.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-class")

    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == ()


@pytest.mark.parametrize("confidence", [0.01, 0.5, 0.99, 1.0])
def test_unvalidated_reference_inspection_logic_varying_confidences(confidence: float) -> None:
    """Verify varying confidence values do not alter the inspection outcome."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=5.0, y2=5.0)
    det = Detection(class_id=0, class_name="object", confidence=confidence, bounding_box=box)
    result = InferenceResult(
        frame_id="f-conf",
        timestamp=20.0,
        detections=(det,),
        inference_time_ms=5.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-conf")

    assert event.status == InspectionStatus.INCONCLUSIVE
    assert event.reason == InspectionReason.UNSUPPORTED_MODEL
    assert event.evidence == ()


def test_inspection_id_and_frame_metadata_preservation() -> None:
    """Verify explicit inspection_id, frame_id, and timestamp are preserved without modification."""
    result = InferenceResult(
        frame_id="origin-frame-xyz",
        timestamp=999888777.66,
        detections=(),
        inference_time_ms=12.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="custom-inspection-id-42")

    assert event.inspection_id == "custom-inspection-id-42"
    assert event.frame_id == "origin-frame-xyz"
    assert event.timestamp == 999888777.66


def test_repeated_calls_determinism() -> None:
    """Verify repeated calls with identical inputs produce equivalent events."""
    box = BoundingBox(x1=5.0, y1=5.0, x2=15.0, y2=15.0)
    det = Detection(class_id=0, class_name="test", confidence=0.8, bounding_box=box)
    result = InferenceResult(
        frame_id="frame-det",
        timestamp=123.0,
        detections=(det,),
        inference_time_ms=10.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event1 = logic.inspect(result, inspection_id="insp-det")
    event2 = logic.inspect(result, inspection_id="insp-det")

    assert event1 == event2


@pytest.mark.parametrize("invalid_id", ["", "   ", "\t", "\n"])
def test_invalid_inspection_id_empty_rejected(invalid_id: str) -> None:
    """Verify empty or whitespace inspection identifiers are rejected with ValueError."""
    result = InferenceResult(
        frame_id="f-1",
        timestamp=1.0,
        detections=(),
        inference_time_ms=1.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    with pytest.raises(ValueError):
        logic.inspect(result, inspection_id=invalid_id)

    with pytest.raises(ValueError):
        InspectionEvent(
            inspection_id=invalid_id,
            frame_id="f-1",
            timestamp=1.0,
            status=InspectionStatus.INCONCLUSIVE,
            reason=InspectionReason.UNSUPPORTED_MODEL,
            evidence=(),
        )


@pytest.mark.parametrize("non_string_id", [None, 123, 45.6, True, ["insp-1"]])
def test_non_string_inspection_id_rejected(non_string_id: object) -> None:
    """Verify non-string inspection identifiers are rejected with TypeError."""
    result = InferenceResult(
        frame_id="f-1",
        timestamp=1.0,
        detections=(),
        inference_time_ms=1.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    with pytest.raises(TypeError):
        logic.inspect(result, inspection_id=non_string_id)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        InspectionEvent(
            inspection_id=non_string_id,  # type: ignore[arg-type]
            frame_id="f-1",
            timestamp=1.0,
            status=InspectionStatus.INCONCLUSIVE,
            reason=InspectionReason.UNSUPPORTED_MODEL,
            evidence=(),
        )


def test_input_inference_result_immutability() -> None:
    """Verify the input InferenceResult and its detections remain completely unmodified."""
    box = BoundingBox(x1=10.0, y1=10.0, x2=20.0, y2=20.0)
    det = Detection(class_id=0, class_name="box", confidence=0.9, bounding_box=box)
    result = InferenceResult(
        frame_id="f-immut",
        timestamp=500.0,
        detections=(det,),
        inference_time_ms=8.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    _ = logic.inspect(result, inspection_id="insp-immut")

    assert result.frame_id == "f-immut"
    assert result.timestamp == 500.0
    assert len(result.detections) == 1
    assert result.detections[0] == det
    assert result.detections[0].confidence == 0.9


def test_inspection_logic_abstraction_compliance() -> None:
    """Verify UnvalidatedReferenceInspectionLogic subclasses InspectionLogic."""
    logic = UnvalidatedReferenceInspectionLogic()
    assert isinstance(logic, InspectionLogic)


def test_reference_policy_never_produces_ok_or_damaged() -> None:
    """Verify the reference policy never produces OK or DAMAGED under any conditions."""
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det = Detection(class_id=0, class_name="anything", confidence=0.99, bounding_box=box)
    result = InferenceResult(
        frame_id="f-never",
        timestamp=100.0,
        detections=(det,),
        inference_time_ms=10.0,
    )
    logic = UnvalidatedReferenceInspectionLogic()
    event = logic.inspect(result, inspection_id="insp-never")

    assert event.status != InspectionStatus.OK
    assert event.status != InspectionStatus.DAMAGED
    assert event.status == InspectionStatus.INCONCLUSIVE
