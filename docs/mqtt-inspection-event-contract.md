# MQTT Inspection Event Contract (Ratified Specification - M5.B)

## Status & Scope

- **Milestone:** M5 — Event Distribution / M5.B — MQTT Contract Ratification & Timestamp Boundary Clarification
- **Status:** Ratified Specification (Architecture Approved)
- **Authoritative Reference:** ADR-006 (`docs/adr/006-mqtt-event-contract.md`), ADR-004 (`docs/adr/004-vision-contracts.md`), ADR-005 (`docs/adr/005-domain-inspection-contract.md`), Architecture v2 (`docs/architecture.md`)
- **Scope:** Specifies the ratified external MQTT inspection-event transport contract, versioned JSON payload schema v1.0, topic hierarchy, identity mapping, UTC ISO 8601 timestamp conversion, evidence representation, delivery semantics, and failure handling rules.
- **Implementation Status:** Ratified normative documentation baseline. Production publisher and serialization implementations remain scheduled for subsequent milestones.

---

## 1. Purpose and Scope

### 1.1 Context and Motivation
Following Milestone M4 (Domain Inspection) and the formal review and conditional acceptance of M5.A proposals, Architecture has ratified the external MQTT inspection-event transport contract (ADR-006) and established authoritative source timestamp semantics (ADR-004).

This document establishes the normative specification for transmitting inspection outcomes to external consumers, monitoring systems, and dashboards over MQTT.

---

## 2. Accepted Architecture Constraints

The following constraints are formally ratified under ADR-006 and core architecture documents:

1. **Transport Protocol:** MQTT protocol compliant with OASIS standard specifications.
2. **Topic Separation:** Inspection events (`factory/line1/inspection/events`) and device status telemetry (`factory/line1/status`) must be published on strictly separated topic hierarchies.
3. **Schema Versioning:** External inspection event payloads must carry explicit schema versioning metadata (initial schema version: `"1.0"`).
4. **External Deduplication Identity:** Messages must include an external `event_id` (UUIDv4) field to support consumer deduplication.
5. **Timestamp Standard:** Timestamps must be represented as UTC ISO 8601 strings derived from originating POSIX epoch frame timestamps.
6. **Quality of Service:** MQTT QoS 1 (at-least-once delivery) is required.
7. **Image Prohibition:** Raw image binaries, camera streams, and runtime-native data structures must never be transmitted over MQTT.
8. **Domain Decoupling:** Transport serialization and publishing mechanisms must remain entirely distinct from domain inspection logic (`InspectionLogic`).

---

## 3. Internal-to-External Transport Boundary

A clear boundary separates internal domain events from external transport messages:

```
┌──────────────────────────────┐
│  Inference Pipeline / Vision │
└──────────────┬───────────────┘
               │ InferenceResult (timestamp: float)
               ▼
┌──────────────────────────────┐
│  Domain Inspection Logic     │
│  (InspectionLogic.inspect)   │
└──────────────┬───────────────┘
               │ InspectionEvent (Internal Domain Dataclass)
               ▼
┌──────────────────────────────┐
│  Publisher Adapter (Future)  │ ◄─── [Transport Boundary]
│  - Generates event_id        │
│  - Formats UTC timestamp     │
│  - Serializes JSON payload   │
└──────────────┬───────────────┘
               │ MQTT QoS 1 Publish (Versioned JSON v1.0)
               ▼
┌──────────────────────────────┐
│  MQTT Broker / Consumers     │
└──────────────────────────────┘
```

- **Internal Domain Event (`InspectionEvent`):** A Python dataclass owned by the domain layer (`vision_iot.domain.contracts`), containing pure domain types (`InspectionStatus`, `InspectionReason`, tuples of `Detection`).
- **External MQTT Message:** A versioned, self-contained JSON byte payload transmitted over the MQTT broker.
- **Publisher Adapter:** The designated component responsible for mapping internal `InspectionEvent` instances into the external JSON schema, generating transport metadata (`event_id`), formatting timestamps, and managing MQTT client publication.

---

## 4. Ratified MQTT Topic Contract

### 4.1 Topic Structure
- **Inspection Events Topic:** `factory/line1/inspection/events`
- **Device Status Topic:** `factory/line1/status`

### 4.2 Topic Naming Rules
- **Base Prefix:** `factory/{line_id}` (reference line identifier: `line1`).
- **Category Segment:** `inspection`
- **Sub-Category Segment:** `events`
- **Complete Default Topic:** `factory/line1/inspection/events`

### 4.3 Subscription and Consumption Expectations
- Consumers subscribing to inspection events must subscribe to `factory/line1/inspection/events`.
- Device status messages must never be published to or consumed from the inspection events topic.
- Legacy prototype topics (such as `factory/line1/detections`) are not Architecture-v2 contracts. Migration of legacy topics is deferred.

---

## 5. Ratified JSON Payload and Field Dictionary

### 5.1 Versioned Payload Schema (JSON v1.0)
External inspection event payloads contain exactly eight required top-level fields:

```json
{
  "schema_version": "1.0",
  "event_id": "419da5c6-6120-47c2-942e-e0d7fe7ba790",
  "inspection_id": "insp-20261030-001234",
  "frame_id": "frame-987654",
  "timestamp": "2026-10-30T12:34:56.789123Z",
  "status": "INCONCLUSIVE",
  "reason": "UNSUPPORTED_MODEL",
  "evidence": []
}
```

### 5.2 Field Dictionary

| Field Name | Type | Ownership | Description |
| :--- | :--- | :--- | :--- |
| `schema_version` | `string` | Transport Metadata | Identifies schema version (`"1.0"`). |
| `event_id` | `string` (UUIDv4) | Transport Metadata | Globally unique identifier assigned once to the logical publication attempt for consumer deduplication (stable across transport retries of the same payload). |
| `inspection_id` | `string` | Domain Correlation | Propagated directly from `InspectionEvent.inspection_id`. |
| `frame_id` | `string` | Domain Correlation | Propagated directly from `InspectionEvent.frame_id`. |
| `timestamp` | `string` (ISO 8601) | Domain Correlation | Originating frame timestamp (`Frame.timestamp`, POSIX epoch float in seconds) converted to UTC ISO 8601 format with microsecond precision and `Z` suffix. |
| `status` | `string` (`Enum`) | Domain Outcome | External representation of `InspectionStatus`: `"OK"`, `"DAMAGED"`, or `"INCONCLUSIVE"`. |
| `reason` | `string` (`Enum`) | Domain Outcome | External representation of `InspectionReason`: `"UNSUPPORTED_MODEL"`. Schema v1.0 requires a non-null `reason` string (`reason: null` is not supported). |
| `evidence` | `array` | Domain Evidence | Collection of supporting detections. Empty array `[]` under the current conservative reference policy. |

---

## 6. Schema Versioning and Compatibility

### 6.1 Version Representation
- Payloads carry a mandatory top-level `schema_version` string field (`"1.0"`).

### 6.2 Compatibility Rules
- **Backward Compatibility:** Minor versions (`"1.1"`) add only optional fields.
- **Breaking Changes:** Structural renames, type changes, or semantic shifts require major version increments (`"2.0"`).
- **Unsupported Versions:** Consumers encountering an unsupported schema version must log a warning, discard or route safely, and never crash or misinterpret payload data.

---

## 7. External Event Identity and Deduplication

### 7.1 Separation of `inspection_id` and `event_id`
- **`inspection_id`**: Owned by the domain inspection trigger.
- **`event_id`**: Owned by the transport publisher adapter (UUIDv4).

### 7.2 Identity Stability Across Retries
- For a single in-memory publication attempt session of a logical `InspectionEvent`, the publisher adapter must generate `event_id` once and preserve it across transport retries under QoS 1.
- Transport identity (`event_id`) is strictly distinct from `inspection_id` and MQTT packet identifiers. No cross-restart durability or state persistence is claimed.

### 7.3 Consumer Deduplication
- External consumers maintain a sliding-window deduplication cache keyed on `event_id`.

---

## 8. Timestamp Conversion and Formatting

### 8.1 Source Timestamp Semantics (ADR-004)
- `Frame.timestamp` is a finite floating-point POSIX/Unix epoch timestamp expressed in seconds, including fractional seconds, recorded at acquisition.
- `OpenCVFrameSource` samples system wall-clock time (`time.time()`) following a successful frame read.

### 8.2 Conversion Rules
- The publisher adapter converts the float timestamp into a UTC ISO 8601 string representation: `YYYY-MM-DDTHH:MM:SS.ffffffZ`.
- Example: `1793363696.789123` -> `"2026-10-30T12:34:56.789123Z"`.
- Originating frame timestamps must never be replaced by publication wall-clock time.

---

## 9. Inspection Status and Reason Mapping

### 9.1 Status Representation
- `InspectionStatus.OK` -> `"OK"`
- `InspectionStatus.DAMAGED` -> `"DAMAGED"`
- `InspectionStatus.INCONCLUSIVE` -> `"INCONCLUSIVE"`

### 9.2 Reason Representation
- `InspectionReason.UNSUPPORTED_MODEL` -> `"UNSUPPORTED_MODEL"`
- Schema v1.0 requires a non-null `reason` string. `reason: null` is not supported. Future domain reason evolution is deferred.

### 9.3 Invalid or Unknown Values
- Corrupt or unrecognized status/reason values must raise a serialization exception rather than defaulting or emitting malformed strings.

---

## 10. Evidence Representation

### 10.1 Conservative Policy Baseline
- `evidence: []` under current reference policy.

### 10.2 Future Portable Detection Representation
When future conclusive policies are authorized, portable detections carry:
- `class_id` (`int`)
- `class_name` (`string`)
- `confidence` (`float`)
- `bounding_box` (`[x1, y1, x2, y2]` in original-frame pixel coordinates)

Raw images and runtime-native data structures are strictly prohibited.

---

## 11. MQTT Delivery Guarantees (QoS 1)

### 11.1 At-Least-Once Semantics & Publication Completion
- MQTT publishing requires QoS 1.
- **Publication Completion Semantics:** The following three distinct publication milestones must be strictly distinguished:
  1. *Local Publish API Acceptance:* Successful acceptance of a publish request by the local MQTT client API (does not constitute confirmed publication).
  2. *MQTT Protocol Confirmation:* MQTT protocol-level acknowledgment (such as QoS 1 `PUBACK`) confirming broker receipt.
  3. *Downstream Consumer Processing:* Actual processing by an external consumer. Successful protocol confirmation does not guarantee application-level processing.
- Duplicate deliveries are handled via consumer-side `event_id` deduplication.
- No durable message recovery or exactly-once application-processing guarantee is claimed.

---

## 12. Serialization and Publication Failure Behavior

### 12.1 Failure Isolation
- Serialization and publication errors must be surfaced to the calling application layer through explicit failure mechanisms.
- Failures must never alter `InspectionStatus`, alter `InspectionReason`, fabricate `InspectionEvent` instances, convert operational errors into `INCONCLUSIVE`, or be silently absorbed.

---

## 13. Summary of Ratified Decisions

| Decision ID | Area | Ratified Position |
| :--- | :--- | :--- |
| **PROP-MQTT-01** | Topic Hierarchy | `factory/line1/inspection/events` (separate from `factory/line1/status`) |
| **PROP-MQTT-02** | Payload Schema | Version `"1.0"` JSON with exactly 8 required top-level fields |
| **PROP-MQTT-03** | Event Identity | `event_id` (UUIDv4) stable across retries of the same logical publication |
| **PROP-MQTT-04** | Timestamp Format | UTC ISO 8601 string (`YYYY-MM-DDTHH:MM:SS.ffffffZ`) derived from POSIX epoch `Frame.timestamp` |
| **PROP-MQTT-05** | Evidence Strategy | Empty array `[]` under current policy; portable detection dictionaries for future conclusive policies |
| **PROP-MQTT-06** | Failure Isolation | Explicit error propagation without modifying domain inspection status or reasons |

---

## 14. References

- `docs/architecture.md` — Architecture v2 Overview
- `docs/adr/004-vision-contracts.md` — Vision Contracts (ADR-004)
- `docs/adr/005-domain-inspection-contract.md` — Domain Inspection Contract (ADR-005)
- `docs/adr/006-mqtt-event-contract.md` — MQTT Event Contract (ADR-006)
- `docs/adr/007-execution-model.md` — Execution Model (ADR-007)
- `docs/adr/009-testing-strategy.md` — Testing Strategy (ADR-009)
