# ADR 006: MQTT Event Contract

## Status
Accepted

## Context
External systems require a standardized, production-grade way to consume inspection outcomes without depending on internal vision or domain code structures.

## Decision
Architecture ratifies the MQTT inspection-event transport contract and versioned JSON schema for Milestone M5 as follows:

### 1. Topic Architecture
- **Inspection Events Topic:** `factory/line1/inspection/events`
- **Device Status Topic:** `factory/line1/status` (strictly separated)
- `line1` is the reference line identifier. Uncontrolled arbitrary topic construction and legacy topics (such as `factory/line1/detections`) are not authorized Architecture-v2 contracts. Migration of legacy topics is deferred.

### 2. External Payload Schema v1.0
External inspection event payloads use version `"1.0"` and contain exactly eight required top-level fields:
1. `schema_version`: `string` (Transport Metadata, e.g., `"1.0"`)
2. `event_id`: `string` (Transport Metadata, UUIDv4)
3. `inspection_id`: `string` (Domain Correlation, propagated from `InspectionEvent.inspection_id`)
4. `frame_id`: `string` (Domain Correlation, propagated from `InspectionEvent.frame_id`)
5. `timestamp`: `string` (Domain Correlation, UTC ISO 8601 format `YYYY-MM-DDTHH:MM:SS.ffffffZ` derived from originating `Frame.timestamp`)
6. `status`: `string` (Domain Outcome: `"OK"`, `"DAMAGED"`, or `"INCONCLUSIVE"`)
7. `reason`: `string` (Domain Outcome: `"UNSUPPORTED_MODEL"`). Schema v1.0 requires a non-null `reason` string; `reason: null` is not supported.
8. `evidence`: `array` (Domain Evidence, empty array `[]` under the current conservative reference policy, or portable `Detection` objects containing `class_id`, `class_name`, `confidence`, and `bounding_box` with XYXY original-frame pixel coordinates).

External metadata does not leak into internal domain dataclasses.

### 3. Versioning and Compatibility
- Payloads carry mandatory `schema_version`.
- Minor versions (`"1.1"`) add only optional fields. Breaking changes require major version increments (`"2.0"`).
- Unsupported schema versions must not be interpreted using incompatible assumptions.

### 4. Event Identity and Deduplication
- `inspection_id` is the existing domain inspection identifier.
- `event_id` is a transport-owned UUIDv4 assigned to each logical publication attempt.
- The publisher adapter generates `event_id` once per logical event and preserves it across transport retries of the same payload.
- External consumers perform sliding-window deduplication keyed on `event_id`.
- The baseline provides no cross-restart identity recovery or durable storage guarantees.

### 5. Timestamp Semantics
- Source timestamps originate from `Frame.timestamp` (finite POSIX epoch float in seconds).
- Converted to UTC ISO 8601 with microsecond precision (`YYYY-MM-DDTHH:MM:SS.ffffffZ`).
- Publication time must not replace originating frame time.

### 6. Evidence Representation
- Under current reference policy: `evidence: []`.
- When populated, portable detections carry integer `class_id`, string `class_name`, float `confidence`, and float `bounding_box` in original-frame pixel coordinates `[x1, y1, x2, y2]`.
- Raw images and runtime-native data structures are strictly prohibited from MQTT transport.

### 7. QoS 1 and Delivery Semantics
- Publishing uses MQTT QoS 1 (at-least-once delivery).
- **Publication Completion Semantics:** The following three distinct milestones must be strictly distinguished:
  1. *Local Publish API Acceptance:* Successful submission of a publish request to the local MQTT client API (does not constitute confirmed publication).
  2. *MQTT Protocol Confirmation:* Receipt of protocol-level acknowledgment (such as QoS 1 `PUBACK`) confirming broker receipt.
  3. *Downstream Consumer Processing:* Actual processing by an external consumer. Successful protocol confirmation does not guarantee application-level processing.
- Duplicate delivery is possible; consumer-side deduplication using `event_id` is required.
- No durable message recovery or exactly-once application-processing guarantee is claimed.

### 8. Failure Isolation
- Serialization and publication errors must be surfaced to the calling application layer through explicit failure mechanisms.
- Failures must never alter `InspectionStatus`, alter `InspectionReason`, fabricate `InspectionEvent` instances, convert operational errors into `INCONCLUSIVE`, or be silently absorbed.

### 9. Explicitly Deferred Capabilities
The following capabilities remain strictly deferred:
- Future domain reason evolution
- Damage-specific model capability
- Legacy topic migration
- Durable queues and cross-restart identity recovery
- General retry infrastructure
- MQTT networking and broker implementation
- Background and asynchronous execution
- Multi-line routing frameworks
- Device-status implementation

## Consequences
- Standardized, reliable, and versioned event distribution.
- Clear separation between telemetry and inspection data.
- Strict isolation between domain inspection logic and external transport serialization.
- Consumers remain decoupled from pipeline internals while maintaining robust deduplication and auditing capabilities through explicit versioning and immutable event identifiers.
