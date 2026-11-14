"""Tests for M5.C Deterministic MQTT Event Serialization Foundation (TASK-021)."""

from __future__ import annotations

import json
from uuid import UUID, uuid1, uuid4

import pytest

from vision_iot.domain import InspectionEvent, InspectionReason, InspectionStatus
from vision_iot.infrastructure import (
    InspectionEventSerializationError,
    InspectionEventSerializer,
)
from vision_iot.vision import BoundingBox, Detection


def test_serializer_basic_success() -> None:
    """Verify basic successful serialization of an InspectionEvent into schema v1.0 JSON bytes."""
    serializer = InspectionEventSerializer()
    box = BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0)
    det = Detection(class_id=1, class_name="defect", confidence=0.95, bounding_box=box)
    event = InspectionEvent(
        inspection_id="insp-001",
        frame_id="frame-001",
        timestamp=1793363696.789123,
        status=InspectionStatus.INCONCLUSIVE,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det,),
    )
    event_id = UUID("419da5c6-6120-47c2-942e-e0d7fe7ba790")

    data = serializer.serialize(event, event_id=event_id)
    assert isinstance(data, bytes)

    parsed = json.loads(data.decode("utf-8"))

    # Exactly 8 required top-level fields in order
    assert list(parsed.keys()) == [
        "schema_version",
        "event_id",
        "inspection_id",
        "frame_id",
        "timestamp",
        "status",
        "reason",
        "evidence",
    ]

    assert parsed["schema_version"] == "1.0"
    assert parsed["event_id"] == "419da5c6-6120-47c2-942e-e0d7fe7ba790"
    assert parsed["inspection_id"] == "insp-001"
    assert parsed["frame_id"] == "frame-001"
    assert parsed["timestamp"] == "2026-10-30T12:34:56.789123Z"
    assert parsed["status"] == "INCONCLUSIVE"
    assert parsed["reason"] == "UNSUPPORTED_MODEL"
    assert parsed["evidence"] == [
        {
            "class_id": 1,
            "class_name": "defect",
            "confidence": 0.95,
            "bounding_box": [10.0, 20.0, 30.0, 40.0],
        }
    ]


def test_uuid_validation() -> None:
    """Verify that event_id must be a UUIDv4 and invalid types/versions are rejected."""
    serializer = InspectionEventSerializer()
    event = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )

    # Non-UUID type
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event, event_id="419da5c6-6120-47c2-942e-e0d7fe7ba790")  # type: ignore[arg-type]

    # UUIDv1 instead of UUIDv4
    v1_uuid = uuid1()
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event, event_id=v1_uuid)


def test_timestamp_formatting_rounding_and_edge_cases() -> None:
    """Verify POSIX to UTC ISO 8601 formatting, rounding, boundary rollovers, and negative timestamps."""
    serializer = InspectionEventSerializer()

    # Test exact timestamp
    event = InspectionEvent(
        inspection_id="insp-ts",
        frame_id="frame-ts",
        timestamp=1793363696.123456,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    data = serializer.serialize(event, event_id=uuid4())
    parsed = json.loads(data.decode("utf-8"))
    assert parsed["timestamp"] == "2026-10-30T12:34:56.123456Z"

    # Test rounding across second boundary
    event_boundary = InspectionEvent(
        inspection_id="insp-bound",
        frame_id="frame-bound",
        timestamp=1793363696.9999999,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    data_bound = serializer.serialize(event_boundary, event_id=uuid4())
    parsed_bound = json.loads(data_bound.decode("utf-8"))
    assert parsed_bound["timestamp"] == "2026-10-30T12:34:57.000000Z"

    # Test negative POSIX timestamp (pre-1970)
    event_negative = InspectionEvent(
        inspection_id="insp-neg",
        frame_id="frame-neg",
        timestamp=-1.123456,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    data_neg = serializer.serialize(event_negative, event_id=uuid4())
    parsed_neg = json.loads(data_neg.decode("utf-8"))
    assert parsed_neg["timestamp"] == "1969-12-31T23:59:58.876544Z"


def test_invalid_timestamps() -> None:
    """Verify rejection of NaN, infinity, non-numeric types, and out-of-range timestamps."""
    serializer = InspectionEventSerializer()

    # NaN
    event_nan = InspectionEvent(
        inspection_id="insp-inv",
        frame_id="frame-inv",
        timestamp=float("nan"),
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_nan, event_id=uuid4())

    # Infinity
    event_inf = InspectionEvent(
        inspection_id="insp-inv",
        frame_id="frame-inv",
        timestamp=float("inf"),
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_inf, event_id=uuid4())

    # Boolean timestamp
    event_bool = InspectionEvent(
        inspection_id="insp-inv",
        frame_id="frame-inv",
        timestamp=True,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_bool, event_id=uuid4())

    # Out of range timestamp
    event_oor = InspectionEvent(
        inspection_id="insp-inv",
        frame_id="frame-inv",
        timestamp=1e20,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_oor, event_id=uuid4())


def test_numeric_overflow_protection_hg06() -> None:
    """Verify that extremely large integers causing numeric overflow (e.g., 10**400) produce InspectionEventSerializationError (HG-06)."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()

    # 1. Overflow timestamp
    event_overflow_ts = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=10**400,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_overflow_ts, event_id=event_id)

    # 2. Overflow confidence
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det_overflow_conf = Detection(
        class_id=0,
        class_name="test",
        confidence=10**400,
        bounding_box=box,
    )
    event_overflow_conf = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det_overflow_conf,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_overflow_conf, event_id=event_id)

    # 3. Overflow bounding box coordinate
    overflow_box = BoundingBox(x1=0.0, y1=0.0, x2=10**400, y2=10.0)
    det_overflow_coord = Detection(
        class_id=0,
        class_name="test",
        confidence=0.9,
        bounding_box=overflow_box,
    )
    event_overflow_coord = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det_overflow_coord,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_overflow_coord, event_id=event_id)


def test_strict_enum_validation_hg01() -> None:
    """Verify that raw strings masquerading as enums are strictly rejected (HG-01)."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det = Detection(class_id=0, class_name="test", confidence=0.9, bounding_box=box)

    # Raw string for status instead of InspectionStatus enum
    event_raw_status = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status="OK",  # type: ignore[arg-type]
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_raw_status, event_id=event_id)

    # Raw string for reason instead of InspectionReason enum
    event_raw_reason = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason="UNSUPPORTED_MODEL",  # type: ignore[arg-type]
        evidence=(det,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_raw_reason, event_id=event_id)


def test_domain_identifiers_validation_hg02() -> None:
    """Verify strict validation of inspection_id and frame_id without coercion (HG-02)."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()

    # Numeric frame_id should be rejected
    event_num_frame = InspectionEvent(
        inspection_id="insp-1",
        frame_id=12345,  # type: ignore[arg-type]
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_num_frame, event_id=event_id)

    # Valid string frame_id preserved without coercion
    event_str_frame = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-abc",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )
    data = serializer.serialize(event_str_frame, event_id=event_id)
    parsed = json.loads(data.decode("utf-8"))
    assert parsed["frame_id"] == "frame-abc"


def test_bounding_box_type_validation_hg03() -> None:
    """Verify that malformed or non-BoundingBox evidence bounding box objects are rejected (HG-03)."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()

    # None as bounding box
    det_none_box = Detection(
        class_id=0,
        class_name="test",
        confidence=0.9,
        bounding_box=None,  # type: ignore[arg-type]
    )
    event_none_box = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det_none_box,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_none_box, event_id=event_id)

    # Dict or tuple instead of BoundingBox
    det_dict_box = Detection(
        class_id=0,
        class_name="test",
        confidence=0.9,
        bounding_box={"x1": 0.0, "y1": 0.0, "x2": 10.0, "y2": 10.0},  # type: ignore[arg-type]
    )
    event_dict_box = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det_dict_box,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_dict_box, event_id=event_id)


def test_evidence_container_validation_hg04() -> None:
    """Verify that evidence must be a tuple and lists are strictly rejected (HG-04)."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()
    box = BoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    det = Detection(class_id=0, class_name="test", confidence=0.9, bounding_box=box)

    event_list_evidence = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=[det],  # type: ignore[arg-type]
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_list_evidence, event_id=event_id)


def test_invalid_evidence_detections_and_coordinates() -> None:
    """Verify rejection of non-Detection items, non-finite coordinates, and bad bounding box order."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()

    # Non-Detection item in tuple
    event_bad_item = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=("not-a-detection",),  # type: ignore[arg-type]
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_bad_item, event_id=event_id)

    # NaN coordinate
    nan_box_det = Detection(
        class_id=0,
        class_name="test",
        confidence=0.9,
        bounding_box=BoundingBox(x1=float("nan"), y1=0.0, x2=10.0, y2=10.0),
    )
    event_nan_coord = InspectionEvent(
        inspection_id="insp-1",
        frame_id="frame-1",
        timestamp=100.0,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(nan_box_det,),
    )
    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize(event_nan_coord, event_id=event_id)


def test_determinism_and_immutability() -> None:
    """Verify that identical inputs produce identical bytes and original event is not mutated."""
    serializer = InspectionEventSerializer()
    box = BoundingBox(x1=5.0, y1=5.0, x2=15.0, y2=15.0)
    det = Detection(class_id=0, class_name="part", confidence=0.99, bounding_box=box)
    event = InspectionEvent(
        inspection_id="insp-det",
        frame_id="frame-det",
        timestamp=1793363696.555555,
        status=InspectionStatus.OK,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(det,),
    )
    event_id = UUID("419da5c6-6120-47c2-942e-e0d7fe7ba790")

    orig_inspection_id = event.inspection_id
    orig_frame_id = event.frame_id
    orig_timestamp = event.timestamp
    orig_status = event.status
    orig_reason = event.reason
    orig_evidence_len = len(event.evidence)

    data1 = serializer.serialize(event, event_id=event_id)
    data2 = serializer.serialize(event, event_id=event_id)

    assert data1 == data2

    assert event.inspection_id == orig_inspection_id
    assert event.frame_id == orig_frame_id
    assert event.timestamp == orig_timestamp
    assert event.status == orig_status
    assert event.reason == orig_reason
    assert len(event.evidence) == orig_evidence_len


def test_invalid_input_types() -> None:
    """Verify rejection of non-InspectionEvent objects."""
    serializer = InspectionEventSerializer()
    event_id = uuid4()

    with pytest.raises(InspectionEventSerializationError):
        serializer.serialize("not-an-event", event_id=event_id)  # type: ignore[arg-type]
