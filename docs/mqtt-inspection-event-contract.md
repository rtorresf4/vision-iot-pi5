# M5.A MQTT Inspection Event Contract Specification

## Status & Scope

- **Milestone:** M5 — Event Distribution / M5.A — MQTT Inspection Event Contract Specification
- **Status:** Specification Proposal (Documentation-Only)
- **Authoritative Reference:** ADR-006 (`docs/adr/006-mqtt-event-contract.md`), ADR-005 (`docs/adr/005-domain-inspection-contract.md`), Architecture v2 (`docs/architecture.md`), TASK-019
- **Scope:** Proposes the external MQTT inspection-event transport contract, versioned JSON payload schema, topic hierarchy, identity mapping, timestamp conversion, evidence representation, delivery semantics, and failure handling rules for architectural review.
- **Implementation Status:** Documentation-only increment. No production MQTT publisher code, serialization adapters, broker integration, or test suites are implemented by this specification.

---

## 1. Purpose and Scope

### 1.1 Context and Motivation
Following the formal closure of Milestone M4 (Domain Inspection), the project requires a production-grade event distribution contract to transmit inspection outcomes to external consumers, monitoring systems, and dashboards.

While ADR-006 establishes high-level foundational decisions—such as MQTT transport, separate inspection-event and device-status topics, versioned schemas, external `event_id` deduplication, UTC ISO 8601 timestamps, QoS 1, and the prohibition of raw image transmission—it does not define the precise external field names, type conventions, retry identity stability, or serialization failure rules required for implementation.

TASK-019 establishes this comprehensive specification. Its purpose is to provide Architecture with a concrete, reviewable proposal that bridges the gap between the internal project-owned `InspectionEvent` and external MQTT message distribution, without altering domain semantics or introducing unauthorized runtime code.

---

## 2. Accepted Architecture Constraints

The following constraints are formally accepted under ADR-006 and other core architecture documents and are treated as non-negotiable baselines:

1. **Transport Protocol:** MQTT protocol compliant with OASIS standard specifications.
2. **Topic Separation:** Inspection events and device status telemetry must be published on strictly separated topic hierarchies.
3. **Schema Versioning:** External inspection event payloads must carry explicit schema versioning metadata.
4. **External Deduplication Identity:** Messages must include an external `event_id` field to support consumer deduplication.
5. **Timestamp Standard:** Timestamps must be represented as UTC ISO 8601 strings.
6. **Quality of Service:** MQTT QoS 1 (at-least-once delivery) is required.
7. **Image Prohibition:** Raw image binaries, camera streams, and runtime-native data structures must never be transmitted over MQTT.
8. **Domain Decoupling:** Transport serialization and publishing mechanisms must remain entirely distinct from domain inspection logic (`InspectionLogic`).

---

## 3. Internal-to-External Transport Boundary

To maintain strict architectural layering (Architecture v2), a clear boundary separates internal domain events from external transport messages:

```
┌──────────────────────────────┐
│  Inference Pipeline / Vision │
└──────────────┬───────────────┘
               │ InferenceResult
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
│  - Serializes timestamp      │
│  - Serializes JSON payload   │
└──────────────┬───────────────┘
               │ MQTT QoS 1 Publish (Versioned JSON)
               ▼
┌──────────────────────────────┐
│  MQTT Broker / Consumers     │
└──────────────────────────────┘
```

- **Internal Domain Event (`InspectionEvent`):** A Python dataclass owned by the domain layer (`vision_iot.domain.contracts`), containing pure domain types (`InspectionStatus`, `InspectionReason`, tuples of `Detection`). It is independent of serialization format, network protocols, and transport metadata.
- **External MQTT Message:** A versioned, self-contained JSON byte payload transmitted over the MQTT broker.
- **Publisher Adapter:** A future application component responsible for mapping internal `InspectionEvent` instances into the external JSON schema, generating transport metadata (`event_id`), formatting timestamps, and managing MQTT client publication.

---

## 4. Proposed Inspection-Event MQTT Topic

### 4.1 Topic Structure
To support clean separation from device status telemetry (`factory/line1/status`), the following topic hierarchy is proposed for architectural evaluation:

- **Inspection Events Topic:** `factory/line1/inspection/events`
- **Device Status Topic:** `factory/line1/status` (existing convention)

### 4.2 Topic Naming Rules
- **Base Prefix:** `factory/{line_id}` (default line identifier: `line1`).
- **Category Segment:** `inspection`
- **Sub-Category Segment:** `events`
- **Complete Default Topic:** `factory/line1/inspection/events`

### 4.3 Subscription and Consumption Expectations
- Consumers subscribing to inspection events must subscribe to `factory/line1/inspection/events` (or wildcard subscriptions such as `factory/+/inspection/events` for multi-line deployments).
- Device status messages (`factory/line1/status`) must never be published to or consumed from the inspection events topic.
- *Note on Legacy Topics:* Legacy prototype topics (such as `factory/line1/detections`) represent historical implementation behavior and are not accepted Architecture-v2 contracts. Any transition from legacy topics to the proposed inspection events topic is a conditional future action requiring Architecture approval and coordinated integration planning.

---

## 5. Proposed JSON Payload and Field Dictionary

### 5.1 Versioned Payload Schema (JSON)
The external inspection event payload is a structured JSON object containing schema metadata, transport identifiers, domain correlation fields, inspection outcomes, and optional evidence.

```json
{
  "schema_version": "1.0",
  "event_id": "419da5c6-6120-47c2-942e-e0d7fe7ba790",
  "inspection_id": "insp-20251030-001234",
  "frame_id": "frame-987654",
  "timestamp": "2025-10-30T12:34:56.789123Z",
  "status": "INCONCLUSIVE",
  "reason": "UNSUPPORTED_MODEL",
  "evidence": []
}
```

### 5.2 Field Dictionary

| Field Name | Type | Ownership | Description |
| :--- | :--- | :--- | :--- |
| `schema_version` | `string` | Transport Metadata | Identifies the schema version of the published payload (e.g., `"1.0"`). |
| `event_id` | `string` (UUIDv4) | Transport Metadata | Globally unique identifier assigned once to the logical publication attempt for consumer deduplication (stable across transport retries of the same payload). |
| `inspection_id` | `string` | Domain Correlation | Propagated directly from `InspectionEvent.inspection_id`, correlating the event with the inspection trigger. |
| `frame_id` | `string` | Domain Correlation | Propagated directly from `InspectionEvent.frame_id`, identifying the originating video frame. |
| `timestamp` | `string` (ISO 8601) | Domain Correlation | Originating frame timestamp converted (conditionally proposed) to UTC ISO 8601 format with microsecond precision and `Z` suffix. |
| `status` | `string` (`Enum`) | Domain Outcome | External representation of `InspectionStatus`: `"OK"`, `"DAMAGED"`, or `"INCONCLUSIVE"`. |
| `reason` | `string` (`Enum` or `null`) | Domain Outcome | External representation of `InspectionReason`: `"UNSUPPORTED_MODEL"`. (Note: Allowing `null` for future conclusive policies like `OK` is a schema proposal requiring Architecture approval). |
| `evidence` | `array` | Domain Evidence | Collection of supporting detections. Empty array `[]` under the initial conservative reference policy. |

---

## 6. Schema Versioning and Compatibility

### 6.1 Version Representation
- Payloads carry a mandatory top-level `schema_version` string field.
- The initial schema version is `"1.0"`.

### 6.2 Compatibility Rules
- **Backward Compatibility:** Future minor versions (e.g., `"1.1"`) must add only optional fields, allowing older consumers to process messages successfully without parsing new fields.
- **Breaking Changes:** Structural renames, type changes, or semantic shifts require incrementing the major version (e.g., `"2.0"`).
- **Unsupported Versions:** Consumers encountering an unsupported schema version (e.g., a major version higher than supported) must log a warning, route the message to a dead-letter handler or discard it safely, and must never crash or misinterpret the payload data.

---

## 7. External Event Identity and Deduplication

### 7.1 Separation of `inspection_id` and `event_id`
- **`inspection_id`**: Owned by the domain inspection trigger. Represents the logical inspection task requested by the application layer. Multiple publication attempts or retries of the same inspection outcome share the same `inspection_id`.
- **`event_id`**: Owned by the transport publisher adapter. A newly generated UUIDv4 assigned to identify one logical external publication attempt.

### 7.2 Identity Stability Across Retries
- **Logical Retries:** If a publisher adapter retries publishing a message due to temporary network failure or broker disconnection under QoS 1, `event_id` must remain stable.
- **Proposed Rule:** For a single in-memory publication attempt session of a logical `InspectionEvent`, the publisher adapter **must generate `event_id` once** when constructing the initial payload and preserve that exact `event_id` across transport retries of that payload. This ensures that consumer deduplication caches correctly identify retries of the exact same message transmission. Transport identity (`event_id`) is strictly distinct from `inspection_id` and MQTT packet identifiers. There is no promise of durable storage, crash recovery, or persistence of `event_id` across process restarts.

### 7.3 Consumer Deduplication
- External consumers are expected to maintain a sliding-window deduplication cache keyed on `event_id` to discard duplicate deliveries arising from MQTT QoS 1 retransmissions.

---

## 8. Timestamp Conversion and Formatting

### 8.1 Source Timestamp Representation
- The internal domain event records `InspectionEvent.timestamp: float`, which reflects observed implementation behavior from `InferenceResult` (representing POSIX epoch seconds with fractional sub-second precision). However, the internal domain dataclass definition does not carry an explicit normative definition of timezone or epoch.

### 8.2 Conversion Rules (Conditional Proposal)
- As a concrete conditional proposal requiring Architecture approval, the publisher adapter will convert the float timestamp into a UTC ISO 8601 string representation.
- **Format:** `YYYY-MM-DDTHH:MM:SS.ffffffZ` (always terminating in `Z` to denote UTC).
- **Mathematically Verified Example:** `1761827696.789123` -> `"2025-10-30T12:34:56.789123Z"`.
- **Restricted Substitution:** The publisher adapter must **never** replace the originating frame timestamp with the current wall-clock publication time. Preserving the original frame timestamp ensures correct temporal alignment and auditing.

### 8.3 Unresolved Timestamp Semantics Escalation
- The internal domain timestamp (`InspectionEvent.timestamp: float`) is a numeric value preserving originating frame correlation, but POSIX epoch interpretation is a proposed conversion prerequisite, not an accepted universal invariant.
- Architecture must explicitly confirm the source timestamp semantics before production serialization is authorized.
- No alternate epoch, publication timestamp substitution, or new internal contract representation is authorized under this specification.
- Any requirement for nanosecond-precision hardware ticks or explicit timezone anchoring requires formal architectural escalation.

---

## 9. Inspection Status and Reason Mapping

### 9.1 Status Representation
The internal `InspectionStatus` enumeration maps directly to uppercase string values:
- `InspectionStatus.OK` -> `"OK"`
- `InspectionStatus.DAMAGED` -> `"DAMAGED"`
- `InspectionStatus.INCONCLUSIVE` -> `"INCONCLUSIVE"`

### 9.2 Reason Representation
The internal `InspectionReason` enumeration maps directly to uppercase string values:
- `InspectionReason.UNSUPPORTED_MODEL` -> `"UNSUPPORTED_MODEL"`
- *Note on Nullability:* The current internal contract (`src/vision_iot/domain/contracts.py`) defines `reason: InspectionReason` with the established non-optional value `UNSUPPORTED_MODEL`. The current conservative reference policy serializes `UNSUPPORTED_MODEL` without semantic loss. Proposing `reason: null` for future conclusive policies (such as `OK`) is a schema proposal requiring Architecture approval and subsequent domain-contract assessment.

### 9.3 Invalid or Unknown Values
- If an unhandled, corrupt, or unrecognized status or reason value is encountered during serialization, the serializer must raise a serialization exception rather than emitting malformed or defaulted strings.
- Unknown or unrecognized values received by consumers must never be silently interpreted as `OK`.

---

## 10. Evidence Inclusion or Exclusion

### 10.1 Conservative Policy Baseline
- Under the current conservative reference policy (`UnvalidatedReferenceInspectionLogic`), every inspection event yields `evidence = ()`.
- Consequently, the external JSON payload serializes `evidence` as an empty array `[]`.

### 10.2 Future Evidence Representation Strategy (Provisional)
When future conclusive policies are authorized and implemented (Milestone M7), if evidence (`tuple[Detection, ...]`) is included in the external payload, each detection must be serialized into a structured dictionary containing only portable numerical and textual attributes:

```json
"evidence": [
  {
    "class_id": 0,
    "class_name": "package_defect",
    "confidence": 0.925,
    "bounding_box": [100.0, 150.0, 300.0, 450.0]
  }
]
```

- **Prohibited Data:** Raw image tensors, NumPy arrays, OpenCV window handles, and runtime-native objects must never be included in the `evidence` array.
- **Loss Considerations:** If detailed evidence is excluded entirely in favor of summary counts, consumers lose spatial bounding box coordinates required for downstream defect visualization. The proposed schema permits empty arrays or structured detections, keeping evidence payload size lightweight.

---

## 11. MQTT Delivery Guarantees (QoS 1)

### 11.1 At-Least-Once Semantics
- In accordance with ADR-006, MQTT publishing must use **QoS 1**.
- QoS 1 guarantees that the message is delivered to the broker at least once, but introduces the possibility of duplicate message delivery if publisher acknowledgments are lost or delayed.

### 11.2 Duplicate Delivery Handling
- MQTT QoS 1 does not provide exactly-once delivery.
- Consumers must rely on the message `event_id` field to perform idempotent deduplication.
- Publishers operating without durable message queues (single-process non-persistent runtime) cannot guarantee message survival across sudden process crashes or power interruptions; non-durable publication limitations must be accounted for in production deployment architectures.

---

## 12. Serialization and Publication Failure Behavior

### 12.1 Failure Separation Principle
Transport and serialization failures must be strictly isolated from domain inspection outcomes.
- **Serialization Failures:** Errors occurring during JSON encoding or schema validation must be explicitly raised as transport exceptions (or returned via an explicit error propagation channel) to be handled and logged by the calling application layer. They must never be silently absorbed nor translated into inspection statuses (`OK`, `DAMAGED`, `INCONCLUSIVE`).
- **Transport / Connectivity Failures:** MQTT broker disconnection, publish timeout, or acknowledgment failure after exhausting connection retry attempts must be surfaced as explicit transport errors to the application layer.
- **Rule:** Transport and serialization failures must **never** be translated into `InspectionStatus` values nor trigger the fabrication of unauthorized domain events. No unauthorized exception hierarchy, background retry framework, durable queue, or asynchronous mechanism is specified.

---

## 13. Legacy MQTT Compatibility Observations

Inspection of legacy prototype code (`apps/pi_detector/mqtt_client.py` and `apps/pi_detector/main.py`) reveals several legacy behaviors that represent historical implementation behavior rather than accepted Architecture-v2 contracts:
- **Legacy Topic:** Prototype published unvalidated bounding boxes to `factory/line1/detections`. Architecture-v2 separates detection telemetry from domain inspection events (`factory/line1/inspection/events`).
- **Unversioned Payloads:** Prototype payloads included raw floating-point timestamps (`"ts"`) and ad-hoc detection lists without schema versioning or external deduplication IDs.
- **Absence of Domain Layer:** Prototype emitted raw model detections directly without passing through `InspectionLogic` or evaluating `InspectionStatus` / `InspectionReason`.

Migration from legacy topics and payloads to the proposed versioned contract is a future conditional action requiring Architecture approval and coordinated integration planning.

---

## 14. Future Deterministic Testing Requirements

Future implementation tasks introducing the serialization adapter and publisher must include deterministic unit and contract tests satisfying the following criteria (executable without physical hardware or a live MQTT broker):

1. **Serialization Roundtrip:** Verify that an `InspectionEvent` with `OK`, `DAMAGED`, or `INCONCLUSIVE` status serializes into the exact expected JSON structure.
2. **Unsupported Model Reason Mapping:** Verify correct serialization of `INCONCLUSIVE` status and `UNSUPPORTED_MODEL` reason with empty evidence `[]`.
3. **Identity Stability:** Verify that the generated `event_id` remains identical across simulated retry publication calls for the same logical event.
4. **Timestamp Formatting:** Verify correct conditional conversion of POSIX float timestamps to UTC ISO 8601 strings with `Z` suffix.
5. **Evidence Serialization:** Verify correct serialization of detection tuples into JSON bounding-box arrays when evidence is present, and empty arrays `[]` when evidence is empty.
6. **Error Handling:** Verify that invalid enum values or serialization exceptions raise appropriate transport errors without altering domain state.

---

## 15. Decision Register and Architecture Approval Requests

| Decision ID | Area | Proposed Position | Status | Action Required by Architecture |
| :--- | :--- | :--- | :--- | :--- |
| **PROP-MQTT-01** | Topic Hierarchy | `factory/line1/inspection/events` | Proposed | Approve inspection event topic naming convention. |
| **PROP-MQTT-02** | Payload Schema | Version `"1.0"` JSON with `schema_version`, `event_id`, `inspection_id`, `frame_id`, `timestamp`, `status`, `reason`, `evidence`. | Proposed | Approve schema fields, types, and naming. |
| **PROP-MQTT-03** | Event Identity | `event_id` (UUIDv4) generated once per logical event by publisher adapter; stable across transport retries of the same payload. | Proposed | Approve identity assignment and retry stability rule. |
| **PROP-MQTT-04** | Timestamp Format | UTC ISO 8601 string (`YYYY-MM-DDTHH:MM:SS.ffffffZ`) conditionally proposed from originating frame timestamp; requires explicit normalization definition. | Proposed | Approve conditional POSIX-to-UTC timestamp conversion rule. |
| **PROP-MQTT-05** | Evidence Strategy | Empty array `[]` under current policy; portable detection dictionaries (`class_id`, `class_name`, `confidence`, `bounding_box`) for future conclusive policies. | Proposed | Approve evidence inclusion/exclusion strategy. |
| **PROP-MQTT-06** | Failure Isolation | Serialization and publication failures must be explicitly raised to the application layer and never translated into domain inspection statuses. | Proposed | Approve failure propagation and separation rule. |

---

## 16. References

- `docs/architecture.md` — Architecture v2 Overview
- `docs/adr/005-domain-inspection-contract.md` — Domain Inspection Contract (ADR-005)
- `docs/adr/006-mqtt-event-contract.md` — MQTT Event Contract (ADR-006)
- `docs/adr/007-execution-model.md` — Execution Model (ADR-007)
- `docs/adr/009-testing-strategy.md` — Testing Strategy (ADR-009)
- `docs/project-context.md` — Project Operational Context
- `docs/domain-inspection-policy.md` — Domain Inspection Policy Specification
- `.agent/tasks/TASK-019.md` — Task Contract for M5.A MQTT Inspection Event Contract Specification
