# TASK-021 — M5.C Deterministic MQTT Event Serialization Foundation

## STATUS

READY

## MILESTONE

M5 — Event Distribution / M5.C — Deterministic MQTT Event Serialization Foundation

## OBJECTIVE

Implement a deterministic, project-owned inspection-event serializer that converts an existing `InspectionEvent` and an explicitly supplied UUIDv4 `event_id` into UTF-8 JSON bytes conforming to the ratified MQTT inspection-event schema v1.0.

The implementation must be fully testable without MQTT networking, a broker, physical camera hardware or Raspberry Pi.

This task implements only the serialization boundary.

## WHY

M5.A established the proposed external inspection-event contract through TASK-019.

M5.B ratified the contract and clarified source timestamp semantics through TASK-020.

Architecture has formally approved M5.B closure and authorized M5.C.

The project now has the authoritative contracts needed to implement serialization while preserving separation between domain inspection and external message delivery.

This increment provides the deterministic serialization foundation required for a future MQTT publisher.

## ARCHITECTURE REFERENCES

Authoritative documents:

- `docs/architecture.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/006-mqtt-event-contract.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/mqtt-inspection-event-contract.md`
- `docs/project-context.md`

Relevant task history:

- `.agent/tasks/TASK-019.md`
- `.agent/tasks/TASK-020.md`

Architecture handoff:

**M5.B Closure & M5.C Deterministic MQTT Event Serialization Authorization — 2026-10-30**

Formal decisions:

- `M5_B_CLOSURE_APPROVED`
- `TIMESTAMP_CONTRACT_GATE_CLOSED`
- `MQTT_EVENT_CONTRACT_GATE_CLOSED`
- `M5_C_IMPLEMENTATION_AUTHORIZED`
- `TASK_021_MATERIALIZATION_AUTHORIZED`
- `MQTT_PUBLISHER_IMPLEMENTATION_NOT_AUTHORIZED`
- `M5_MILESTONE_INCOMPLETE`

No ADR modifications are authorized.

## SCOPE

### 1. Repository and contract preflight

Before implementation:

1. Confirm the expected task branch and clean working tree.
2. Read the authoritative documentation and existing Python contracts.
3. Inspect `src/vision_iot/` package and export conventions.
4. Inspect the project-owned `InspectionEvent`, `InspectionStatus`, `InspectionReason`, `Detection`, and `BoundingBox` representations.
5. Confirm the ratified schema and timestamp semantics.
6. Confirm that no equivalent Architecture-v2 serializer already exists.

Do not reuse legacy MQTT serialization behavior as an authoritative design.

### 2. Create the infrastructure package

Create:

`src/vision_iot/infrastructure/__init__.py`

Use the existing repository's package conventions.

Expose only the public serializer and its authorized serialization error.

Do not introduce unrelated infrastructure APIs.

### 3. Implement InspectionEventSerializer

Create:

`src/vision_iot/infrastructure/inspection_event_serializer.py`

Implement the approved public API:

```python
from uuid import UUID

class InspectionEventSerializer:
    def serialize(
        self,
        event: InspectionEvent,
        *,
        event_id: UUID,
    ) -> bytes:
        ...
```

Requirements:

- Accept an existing project-owned `InspectionEvent`.
- Require an explicit keyword-only `event_id`.
- Require `event_id` to be a UUIDv4 value.
- Convert the identifier to canonical lowercase hyphenated string format.
- Return UTF-8 JSON bytes.
- Do not generate or modify `event_id`.
- Do not mutate `event`.
- Do not access system time, randomness, networking or persistent storage.
- Do not introduce a serializer abstract base class, factory, registry or plugin framework.

### 4. Schema v1.0

Produce exactly eight required top-level JSON fields, in stable order:

1. `schema_version`
2. `event_id`
3. `inspection_id`
4. `frame_id`
5. `timestamp`
6. `status`
7. `reason`
8. `evidence`

`schema_version` must always equal `"1.0"`.

Preserve the existing domain correlation identifiers.

Do not add metadata fields or expose internal implementation details.

JSON object ordering must be deterministic, but consumers must not depend on field order.

### 5. Deterministic timestamp conversion

Interpret `InspectionEvent.timestamp` according to ADR-004 as POSIX/Unix epoch seconds.

Serialize it as UTC ISO 8601:

`YYYY-MM-DDTHH:MM:SS.ffffffZ`

Requirements:

- Exactly six fractional-second digits.
- UTC conversion independent of the local timezone.
- Deterministic rounding to microsecond resolution.
- Correct handling of rounding across second and calendar boundaries.
- Explicit rejection of NaN and positive/negative infinity.
- Explicit rejection of out-of-range timestamps.
- No substitution with current publication time.
- No use of `inference_time_ms`.
- No claim of nanosecond precision or exact sensor exposure timing.

Do not change `Frame`, `InferenceResult` or `InspectionEvent`.

### 6. Status and reason mapping

Serialize the currently defined `InspectionStatus` members:

- `OK` → `"OK"`
- `DAMAGED` → `"DAMAGED"`
- `INCONCLUSIVE` → `"INCONCLUSIVE"`

Serialize the currently defined `InspectionReason` member:

- `UNSUPPORTED_MODEL` → `"UNSUPPORTED_MODEL"`

Schema v1.0 requires a non-null reason string.

Reject unknown enum members, incorrect types and unsupported values.

Do not coerce arbitrary strings into valid enum members.

Do not replace invalid values with `INCONCLUSIVE`.

Do not introduce new domain consistency rules linking statuses to reasons.

Synthetic events using all three defined statuses are permitted for serialization contract tests; they must not be presented as validated package-damage detection capability.

### 7. Evidence serialization

Always include the `evidence` field.

An empty `InspectionEvent.evidence` tuple must serialize as:

```json
"evidence": []
```

For each existing project-owned `Detection`, produce:

```json
{
  "class_id": 0,
  "class_name": "example",
  "confidence": 0.925,
  "bounding_box": [100.0, 150.0, 300.0, 450.0]
}
```

Requirements:

- Preserve detection order.
- Preserve `class_id` as an integer.
- Preserve `class_name` as a string.
- Preserve confidence as a finite JSON number.
- Preserve bounding-box coordinates in original-frame pixel space.
- Preserve XYXY coordinate ordering.
- Do not normalize coordinates.
- Do not round coordinates to integer pixels.
- Validate existing bounding-box ordering requirements.
- Reject invalid types and non-finite numerical values.
- Reject JSON-incompatible numeric values.

Only use detections contained in `InspectionEvent.evidence`.

Do not pull detections from unrelated inference results.

Do not validate model-specific class taxonomies or introduce confidence thresholds.

### 8. Serialization failure handling

Define one serializer-specific error:

`InspectionEventSerializationError`

The error must belong to the infrastructure serialization boundary, not the domain.

The public serializer should raise this error for expected invalid-input and serialization failures.

Relevant failures include:

- Invalid `InspectionEvent` input.
- Invalid UUID type or UUID version.
- Invalid inspection or frame identifiers.
- Invalid timestamp.
- Unsupported status or reason representations.
- Invalid evidence types or values.
- Invalid bounding-box representations.
- JSON encoding failure.

Do not create a broad transport exception hierarchy.

Do not silently return empty bytes or fabricated default values.

Do not alter the original domain event when an error occurs.

### 9. Deterministic JSON encoding

Use Python standard-library facilities.

Requirements:

- Identical valid inputs produce identical bytes.
- Explicit UTF-8 encoding.
- Stable JSON field ordering.
- JSON must not contain non-standard NaN or Infinity values.
- No random, time-dependent or environment-dependent metadata.
- No MQTT client dependency.
- No unnecessary generalized serialization framework.

### 10. Deterministic unit and contract tests

Create:

`tests/test_inspection_event_serializer.py`

Tests must cover:

1. Exact eight-field schema.
2. Fixed schema version `"1.0"`.
3. UTF-8 byte output.
4. Explicit UUIDv4 mapping.
5. Canonical UUID string representation.
6. Invalid UUID input types.
7. UUID versions other than v4.
8. Preservation of `inspection_id`.
9. Preservation of `frame_id`.
10. Correct POSIX-to-UTC conversion.
11. Six fractional digits.
12. Timezone independence.
13. Fractional-second rounding.
14. Rounding across a second boundary.
15. NaN, Infinity and negative Infinity rejection.
16. Out-of-range timestamp rejection.
17. Serialization of `INCONCLUSIVE`.
18. Structural serialization support for `OK` and `DAMAGED`.
19. `UNSUPPORTED_MODEL` mapping.
20. Non-null reason.
21. Unsupported statuses and reasons.
22. Empty evidence.
23. Single Detection representation.
24. Multiple Detection ordering.
25. XYXY bounding-box order.
26. Non-finite confidence rejection.
27. Non-finite coordinate rejection.
28. Invalid evidence element types.
29. Invalid JSON-compatible field types.
30. Identical inputs producing identical bytes.
31. Preservation of the original `InspectionEvent`.
32. No internally generated event identifier.
33. No network or MQTT dependency.
34. Existing regression tests remain passing.

Use deterministic fixtures and explicit UUID values.

Tests must inspect parsed JSON structures and compare exact byte representations where deterministic encoding matters.

Do not implement a deserializer.

### 11. Explicitly preserve architecture boundaries

The serializer ends at valid JSON bytes.

It must not:

- Publish MQTT messages.
- Generate event identities.
- Perform retry logic.
- Manage broker connections.
- Add device-status messages.
- Run domain inspection.
- Interpret model detections.
- Change domain contracts.
- Introduce asynchronous execution.
- Add persistence or background processing.

## OUT OF SCOPE

- MQTT publisher implementation.
- MQTT client initialization.
- MQTT QoS configuration.
- PUBACK handling.
- Broker connections.
- Retry loops.
- Automatic reconnection.
- Event persistence.
- Durable queues.
- `EventPublisher` abstraction.
- Generic event bus.
- Serializer registry or factory.
- Schema negotiation.
- Reverse deserialization.
- Domain inspection policy changes.
- New inspection statuses or reasons.
- Changes to Frame, Detection, InspectionEvent or other established contracts.
- Changes to ADRs.
- Changes to existing tests.
- Dashboard or legacy application integration.
- Raspberry Pi deployment.
- Runtime benchmarking.
- New external dependencies.

## INPUTS / CONTRACTS

The implementation must use existing project-owned representations:

- `InspectionEvent`
- `InspectionStatus`
- `InspectionReason`
- `Detection`
- `BoundingBox`

Authoritative definitions are in:

- `src/vision_iot/domain/contracts.py`
- `src/vision_iot/domain/__init__.py`
- `src/vision_iot/vision/contracts.py`
- `src/vision_iot/vision/__init__.py`

Use ADR-004 for timestamps, ADR-005 for domain semantics, ADR-006 for the external schema and ADR-007 for synchronous execution.

## EXPECTED OUTPUT

Exactly three new files:

```text
src/
└── vision_iot/
    └── infrastructure/
        ├── __init__.py
        └── inspection_event_serializer.py

tests/
└── test_inspection_event_serializer.py
```

No existing production modules or tests should require modification.

## ALLOWED CHANGES

The Implementation Agent may create or modify ONLY:

1. `src/vision_iot/infrastructure/__init__.py`
2. `src/vision_iot/infrastructure/inspection_event_serializer.py`
3. `tests/test_inspection_event_serializer.py`

No other changes are authorized.

## FORBIDDEN CHANGES

Do not modify:

- `src/vision_iot/domain/**`
- `src/vision_iot/vision/**`
- `src/vision_iot/hardware/**`
- `src/vision_iot/__init__.py`
- `apps/**`
- `deploy/**`
- `models/**`
- `.agent/**`
- `docs/**`
- `.github/**`
- `pyproject.toml`
- `Makefile`
- `requirements*.txt`
- Existing test modules.

Do not modify Git configuration, switch branches, commit, merge, rebase or push.

## ACCEPTANCE CRITERIA

1. Serializer exists in the authorized infrastructure package.
2. Public API matches Architecture authorization.
3. Serializer accepts an existing InspectionEvent.
4. event_id is an explicit keyword-only UUIDv4 argument.
5. Serializer does not generate event identifiers.
6. Serializer returns UTF-8 JSON bytes.
7. Schema version equals `"1.0"`.
8. Exactly eight required top-level fields are present.
9. JSON field ordering and encoding are deterministic.
10. Inspection and frame identifiers are preserved.
11. Timestamp conversion uses UTC POSIX semantics.
12. Exactly six fractional-second digits are emitted.
13. Microsecond rounding is deterministic and handles boundaries.
14. Invalid timestamps are rejected explicitly.
15. Status and reason values are faithful to existing enums.
16. Non-null reason requirement is preserved.
17. Invalid enum values and types are rejected.
18. Empty evidence serializes as an empty array.
19. Detection fields are serialized faithfully.
20. Detection order is preserved.
21. Bounding-box semantics remain XYXY original-frame pixels.
22. Non-finite or invalid evidence values are rejected.
23. Expected serialization failures raise InspectionEventSerializationError.
24. Invalid values are not silently coerced or replaced.
25. Repeated identical inputs produce identical bytes.
26. Input domain events are not mutated.
27. No MQTT network functionality is introduced.
28. No publisher, retry or persistence functionality is introduced.
29. No new production dependencies are added.
30. No unauthorized source, ADR or task changes occur.
31. New deterministic tests pass.
32. Existing regression tests pass.
33. Black, Ruff, mypy and pre-commit pass.
34. Independent Review Agent returns PASS.
35. Human Gate approves the implementation.
36. Integration follows the governed ADS workflow.

## REQUIRED TESTS

Implement deterministic unit and contract tests in:

`tests/test_inspection_event_serializer.py`

No physical hardware, broker, network connection or local ONNX model artifact may be necessary for these tests.

Do not modify existing tests.

## VALIDATION COMMANDS

From the repository root:

```bash
git status -sb

PATH=.venv/bin:$PATH make lint
PATH=.venv/bin:$PATH make test
.venv/bin/pre-commit run --all-files

git diff --check
git diff --stat
git status --short
```

Because new files are initially untracked, directly inspect their contents and check them for whitespace and formatting issues.

Do not treat a clean `git diff --check` as proof that untracked files have been validated.

Do not bypass failing quality gates.

## DEPENDENCIES

- TASK-020 integrated.
- M5.B formally closed by Architecture.
- ADR-004 and ADR-006 ratified.
- TASK-021 identifier available.
- Expected task branch created.
- Python virtual environment and existing quality tooling available.

No additional external runtime dependency is expected.

## BLOCKING CONDITIONS

### ARCHITECTURE_DECISION_REQUIRED

Stop and escalate if:

- Existing InspectionEvent data cannot be represented faithfully.
- A new domain field or enum member is required.
- The approved serializer API is insufficient.
- The serializer would need to generate event IDs.
- Timestamp semantics contradict existing source data.
- Schema v1.0 requires unauthorized modifications.
- Model-specific interpretation becomes necessary.
- An external dependency becomes unavoidable.
- An ADR or domain contract requires changes.
- A broader serialization or publishing framework is necessary.
- Existing quality gates would need to be weakened.

### TASK_BLOCKED

Stop if:

- Required repository files are missing.
- The current branch is not the expected task branch.
- The initial working tree contains unauthorized changes.
- Required validation cannot run due to an unresolved environment issue.

### HUMAN_DECISION_REQUIRED

Stop if a required file-level or workflow decision exceeds the granted Implementation Agent permissions.

### RETRY_EXHAUSTED

Stop if bounded correction attempts cannot resolve failures within authorized scope.

Do not silently expand scope.

## DELIVERABLES

The Implementation Agent must return an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation code.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Describe the serializer API, schema mapping, timestamp conversion, evidence handling and error behavior.

### TESTS ADDED / UPDATED

List the new test cases and their results.

### VALIDATION RESULTS

Provide actual results for all required commands.

### DEVIATIONS

Report any deviations or `None`.

### BLOCKERS

Report any unresolved blockers or `None`.

### OUT-OF-SCOPE OBSERVATIONS

Record relevant issues intentionally left outside TASK-021.

Do not commit or integrate changes.

Stop after validation and reporting.
