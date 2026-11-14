"""Deterministic MQTT inspection event serializer implementation."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime, timedelta
from uuid import UUID

from vision_iot.domain import InspectionEvent, InspectionReason, InspectionStatus
from vision_iot.vision import BoundingBox, Detection


class InspectionEventSerializationError(Exception):
    """Raised when an inspection event cannot be serialized into JSON bytes."""

    pass


class InspectionEventSerializer:
    """Serializes InspectionEvents into deterministic UTF-8 JSON bytes conforming to schema v1.0."""

    def serialize(
        self,
        event: InspectionEvent,
        *,
        event_id: UUID,
    ) -> bytes:
        """Serialize an InspectionEvent and explicit UUIDv4 event_id into schema v1.0 JSON bytes."""
        if not isinstance(event, InspectionEvent):
            raise InspectionEventSerializationError(
                f"Expected InspectionEvent instance, got {type(event)}"
            )

        if not isinstance(event_id, UUID):
            raise InspectionEventSerializationError(
                f"Expected event_id to be UUID, got {type(event_id)}"
            )
        if event_id.version != 4:
            raise InspectionEventSerializationError(
                f"Expected UUID version 4 for event_id, got version {event_id.version}"
            )

        # Validate domain identifiers without coercion
        if not isinstance(event.inspection_id, str) or not event.inspection_id.strip():
            raise InspectionEventSerializationError(
                f"Expected inspection_id to be non-empty str, got {type(event.inspection_id)}"
            )
        if not isinstance(event.frame_id, str):
            raise InspectionEventSerializationError(
                f"Expected frame_id to be str, got {type(event.frame_id)}"
            )

        # Validate and convert timestamp with overflow protection
        if not isinstance(event.timestamp, int | float) or isinstance(event.timestamp, bool):
            raise InspectionEventSerializationError(
                f"Expected timestamp to be numeric, got {type(event.timestamp)}"
            )
        try:
            if math.isnan(event.timestamp) or math.isinf(event.timestamp):
                raise InspectionEventSerializationError(
                    f"Timestamp cannot be NaN or infinity: {event.timestamp}"
                )
            usecs = round(float(event.timestamp) * 1_000_000)
            secs, subsecs = divmod(usecs, 1_000_000)
            dt = datetime.fromtimestamp(secs, tz=UTC) + timedelta(microseconds=subsecs)
        except (OverflowError, ValueError, OSError, TypeError) as e:
            if isinstance(e, InspectionEventSerializationError):
                raise
            raise InspectionEventSerializationError(
                f"Out of range or invalid timestamp: {event.timestamp}"
            ) from e

        timestamp_str = dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"

        # Validate and map status (strict enum instances only)
        if not isinstance(event.status, InspectionStatus):
            raise InspectionEventSerializationError(
                f"Expected InspectionStatus instance, got {type(event.status)}"
            )
        status_str = event.status.value

        # Validate and map reason (strict enum instances only, non-null)
        if event.reason is None:
            raise InspectionEventSerializationError("Reason cannot be null in schema v1.0")
        if not isinstance(event.reason, InspectionReason):
            raise InspectionEventSerializationError(
                f"Expected InspectionReason instance, got {type(event.reason)}"
            )
        reason_str = event.reason.value

        # Validate evidence container (tuple strictly required)
        if not isinstance(event.evidence, tuple):
            raise InspectionEventSerializationError(
                f"Expected evidence to be tuple, got {type(event.evidence)}"
            )

        serialized_evidence = []
        for det in event.evidence:
            if not isinstance(det, Detection):
                raise InspectionEventSerializationError(
                    f"Expected Detection instance in evidence, got {type(det)}"
                )

            if not isinstance(det.class_id, int) or isinstance(det.class_id, bool):
                raise InspectionEventSerializationError(
                    f"Expected class_id to be int, got {type(det.class_id)}"
                )

            if not isinstance(det.class_name, str):
                raise InspectionEventSerializationError(
                    f"Expected class_name to be str, got {type(det.class_name)}"
                )

            if not isinstance(det.confidence, int | float) or isinstance(det.confidence, bool):
                raise InspectionEventSerializationError(
                    f"Expected confidence to be numeric, got {type(det.confidence)}"
                )
            try:
                if math.isnan(det.confidence) or math.isinf(det.confidence):
                    raise InspectionEventSerializationError(
                        f"Confidence cannot be NaN or infinity: {det.confidence}"
                    )
                conf_val = float(det.confidence)
            except (OverflowError, ValueError, TypeError) as e:
                if isinstance(e, InspectionEventSerializationError):
                    raise
                raise InspectionEventSerializationError(
                    f"Invalid or unrepresentable confidence value: {det.confidence}"
                ) from e

            box = det.bounding_box
            if not isinstance(box, BoundingBox):
                raise InspectionEventSerializationError(
                    f"Expected BoundingBox instance, got {type(box)}"
                )

            serialized_coords = []
            for coord_name, val in [
                ("x1", box.x1),
                ("y1", box.y1),
                ("x2", box.x2),
                ("y2", box.y2),
            ]:
                if not isinstance(val, int | float) or isinstance(val, bool):
                    raise InspectionEventSerializationError(
                        f"Expected bounding box coordinate {coord_name} to be numeric, got {type(val)}"
                    )
                try:
                    if math.isnan(val) or math.isinf(val):
                        raise InspectionEventSerializationError(
                            f"Bounding box coordinate {coord_name} cannot be NaN or infinity: {val}"
                        )
                    serialized_coords.append(float(val))
                except (OverflowError, ValueError, TypeError) as e:
                    if isinstance(e, InspectionEventSerializationError):
                        raise
                    raise InspectionEventSerializationError(
                        f"Invalid or unrepresentable coordinate {coord_name}: {val}"
                    ) from e

            if (
                serialized_coords[0] > serialized_coords[2]
                or serialized_coords[1] > serialized_coords[3]
            ):
                raise InspectionEventSerializationError(
                    f"Invalid bounding box coordinate ordering (xyxy required): {serialized_coords}"
                )

            serialized_evidence.append(
                {
                    "class_id": int(det.class_id),
                    "class_name": str(det.class_name),
                    "confidence": conf_val,
                    "bounding_box": serialized_coords,
                }
            )

        payload = {
            "schema_version": "1.0",
            "event_id": str(event_id),
            "inspection_id": event.inspection_id,
            "frame_id": event.frame_id,
            "timestamp": timestamp_str,
            "status": status_str,
            "reason": reason_str,
            "evidence": serialized_evidence,
        }

        try:
            json_str = json.dumps(payload, allow_nan=False, ensure_ascii=False)
        except (ValueError, TypeError) as e:
            raise InspectionEventSerializationError(
                f"Failed to encode inspection event to JSON: {e}"
            ) from e

        return json_str.encode("utf-8")
