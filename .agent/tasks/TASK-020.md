# TASK-020 — M5.B MQTT Contract Ratification & Timestamp Boundary Clarification

## STATUS

READY

## MILESTONE

M5 — Event Distribution / M5.B — MQTT Contract Ratification & Timestamp Boundary Clarification

## OBJECTIVE

Ratify the Architecture-approved MQTT inspection-event contract and establish authoritative source timestamp semantics for the existing Architecture-v2 acquisition boundary.

Update the relevant existing ADRs and align the MQTT specification without modifying production code, public Python contracts, tests, dependencies or runtime behavior.

This is a strictly documentation-only increment.

## WHY

TASK-019 completed M5.A and produced a concrete MQTT inspection-event contract proposal.

Architecture formally closed M5.A and conditionally accepted the MQTT contract on 2026-10-30.

Production serialization remains blocked until:

1. ADR-006 contains the approved external MQTT contract.
2. The source Frame timestamp semantics are verified against integrated acquisition implementations.
3. The corresponding acquisition/vision contract ADR establishes compatible normative timestamp semantics.
4. The MQTT specification reflects all approved decisions, including the non-null `reason` requirement.

M5.B closes these normative documentation gates before the first production serialization task.

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/006-mqtt-event-contract.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/mqtt-inspection-event-contract.md`
- `docs/project-context.md`
- `.agent/tasks/TASK-019.md`
- Architecture handoff dated 2026-10-30: **M5.A Completion, MQTT Contract Ratification & Next Increment**

Applicable Architecture decisions:

- `M5_A_CLOSURE_APPROVED`
- `MQTT_CONTRACT_CONDITIONALLY_ACCEPTED`
- `ADR_006_UPDATE_REQUIRED`
- `TIMESTAMP_SOURCE_SEMANTICS_REQUIRED`
- `ACQUISITION_ADR_REVIEW_REQUIRED`
- `M5_B_DOCUMENTATION_TASK_AUTHORIZED`
- `M5_PRODUCTION_IMPLEMENTATION_NOT_YET_AUTHORIZED`

Approved or conditionally approved proposals:

- PROP-MQTT-01: Topic hierarchy.
- PROP-MQTT-02: Schema v1.0, with clarification.
- PROP-MQTT-03: External event identity.
- PROP-MQTT-04: Source timestamp semantics, conditional.
- PROP-MQTT-05: Evidence serialization.
- PROP-MQTT-06: QoS 1 and failure semantics, with clarification.

Do not introduce new architectural decisions beyond those explicitly authorized.

## SCOPE

### 1. Mandatory source timestamp audit

Before modifying documentation, inspect:

- `src/vision_iot/hardware/camera.py`
- `src/vision_iot/hardware/__init__.py`
- `src/vision_iot/vision/contracts.py`
- `src/vision_iot/vision/postprocessing.py`
- `src/vision_iot/domain/contracts.py`
- `src/vision_iot/domain/inspection.py`
- `tests/test_acquisition.py`
- Relevant vision and domain timestamp propagation tests.
- Existing ADRs defining acquisition, vision, domain and timing semantics.

Identify every integrated Architecture-v2 `Frame` producer and determine whether its timestamp semantics are compatible with the approved baseline.

Known preliminary evidence:

- `OpenCVFrameSource.get_frame()` calls `time.time()` after successful `VideoCapture.read()`.
- `FakeFrameSource` receives a preconstructed `Frame` and returns it unchanged.
- Test fixtures may supply deterministic synthetic timestamp values.
- `Postprocessor` and domain inspection preserve source timestamp correlation.
- `time.perf_counter()` is used for inference duration measurement, not frame capture time.

Independently verify these observations against repository contents.

Document the audit outcome in the Implementation Report, identifying inspected producers and any exceptions.

If an incompatible production source is found, stop with `ARCHITECTURE_DECISION_REQUIRED`.

### 2. Clarify Frame timestamp semantics in ADR-004

If the audit confirms compatibility, minimally update:

`docs/adr/004-vision-contracts.md`

Establish that:

- `Frame.timestamp` is a finite floating-point POSIX/Unix epoch timestamp expressed in seconds, including fractional seconds.
- It records the acquisition time assigned by the source.
- The existing OpenCV source samples system wall-clock time following a successful frame read; this must not be described as an exact hardware exposure timestamp.
- Producers implementing `FrameSource` are responsible for supplying compatible source timestamps.
- `FakeFrameSource` preserves its injected frame and does not generate timestamps.
- Synthetic timestamps used by isolated tests are fixtures for contract and correlation checks, not evidence of a separate production timestamp epoch.
- The numerical value is propagated without reinterpretation through `InferenceResult` and `InspectionEvent`.
- The timestamp is distinct from inference execution duration measured using `inference_time_ms`.
- Publication time must not replace originating frame time.

Do not require existing dataclass validation, new fields, new timestamp classes or producer modifications.

The documentation must not claim runtime enforcement that the current code does not implement.

### 3. Ratify the MQTT topic contract in ADR-006

Approve the Architecture-v2 reference topic:

`factory/line1/inspection/events`

Keep device status separate:

`factory/line1/status`

Clarify that:

- `line1` is the reference configuration.
- Uncontrolled arbitrary topic construction is not authorized.
- The legacy `factory/line1/detections` topic is not the Architecture-v2 inspection-event contract.
- Legacy migration is deferred.
- Dynamic topic discovery and multi-line routing frameworks are not required.

### 4. Ratify external JSON schema v1.0

ADR-006 must define exactly eight required top-level fields:

1. `schema_version`
2. `event_id`
3. `inspection_id`
4. `frame_id`
5. `timestamp`
6. `status`
7. `reason`
8. `evidence`

The initial schema version is `"1.0"`.

Specify the field types and ownership.

The schema is external transport metadata and domain serialization; it must not modify `InspectionEvent`.

No additional required top-level fields are authorized.

### 5. Ratify versioning and compatibility

Document:

- Version `"1.0"` as the initial contract.
- Backward-compatible optional additions may be introduced through minor versions.
- Breaking type, name or semantic changes require a major version.
- Unsupported schema versions must not be interpreted using incompatible assumptions.
- Unknown statuses must never default to `OK`.

Do not introduce a schema registry, negotiation service or migration framework.

### 6. Ratify event identity

Define:

- `inspection_id` as the existing domain inspection identifier.
- `event_id` as the transport-owned logical publication identifier.
- UUIDv4 as the initial external event identifier format.
- Generation before the first publication attempt.
- Reuse of the same `event_id`, schema version and serialized payload across retries of the same logical publication.
- Consumer-level deduplication keyed by `event_id`.
- Separation between application event identity and MQTT packet identifiers.

Explicitly state that the initial baseline provides no cross-restart identity recovery, durable storage guarantee or exactly-once application processing.

### 7. Ratify UTC timestamp serialization

Once acquisition semantics are confirmed, document:

- Source: the originating `Frame.timestamp`.
- Unit and epoch: POSIX/Unix seconds, including fractional seconds.
- External representation: UTC ISO 8601.
- Exact format: `YYYY-MM-DDTHH:MM:SS.ffffffZ`.
- No local timezone offset adjustment.
- No substitution with publication time.
- Explicit rejection of non-finite or unrepresentable timestamps at the future serialization boundary.
- No interpretation of monotonic durations or device ticks as calendar timestamps.

Use a mathematically correct illustrative conversion.

Do not implement conversion code during this task.

### 8. Ratify inspection status and reason

Current status values:

- `OK`
- `DAMAGED`
- `INCONCLUSIVE`

Current supported reason:

- `UNSUPPORTED_MODEL`

Schema v1.0 requires a non-null `reason` string.

`reason: null` is NOT approved in schema v1.0.

The existing internal domain contract remains unchanged.

Future conclusive outcome reason semantics remain deferred to a separate ADR-005-governed domain-contract decision.

Unknown or unsupported values must fail explicitly instead of being silently mapped.

Do not imply that the conservative current policy produces conclusive classifications.

### 9. Ratify evidence representation

The external `evidence` field is a required array.

Under the current conservative reference policy:

`evidence: []`

For future authorized evidence, portable detections contain:

- `class_id`
- `class_name`
- `confidence`
- `bounding_box`

Bounding boxes are four-element numerical arrays in original-frame pixel coordinates:

`[x1, y1, x2, y2]`

Preserve:

- XYXY ordering.
- Floating-point coordinates.
- Detection ordering.
- Existing project-owned `Detection` semantics.

Only serialize detections contained in `InspectionEvent.evidence`.

Do not populate empty evidence by copying unrelated inference detections.

Reject non-finite or invalid JSON numeric representations.

Do not authorize any new defect class or damage decision.

Prohibit raw images and runtime-native data structures.

### 10. Ratify MQTT QoS 1 semantics

Define:

- QoS 1 as the required publishing quality of service.
- Possible duplicate delivery.
- Consumer responsibility for application-level deduplication.
- Distinction between client publish API acceptance, MQTT publication confirmation and downstream consumer processing.
- No exactly-once application-processing promise.
- No durable message recovery guarantee.
- No automatic general-purpose retry framework requirement.

### 11. Ratify failure isolation

Serialization and publication errors must be surfaced to the calling application layer through an explicit failure mechanism.

Such failures must never:

- Change `InspectionStatus`.
- Change `InspectionReason`.
- Fabricate `InspectionEvent` instances.
- Convert operational failures into `INCONCLUSIVE`.
- Be silently absorbed.

Do not prescribe a broad exception hierarchy or unauthorized infrastructure.

### 12. Align the existing MQTT specification

Update:

`docs/mqtt-inspection-event-contract.md`

Ensure it reflects Architecture's ratified decisions rather than presenting approved positions as unresolved proposals.

Specifically:

- Clarify which decisions are accepted.
- Identify completed timestamp ratification, if successfully established.
- Require non-null `reason` in schema v1.0.
- Remove any implication that `reason: null` is supported in the initial schema.
- Preserve the deferral of future reason-contract evolution.
- Align the example payload, identity, evidence, versioning, QoS and failure semantics with ADR-006.
- Preserve explicit deferrals and prototype isolation.

ADR-006 is authoritative where its normative contents conflict with earlier provisional wording.

### 13. Document deferred capabilities

Keep the following explicitly outside the current approved baseline:

- Future domain reason evolution.
- Damage-specific model capability.
- Legacy migration.
- Durable queues.
- Cross-restart identity recovery.
- General retry infrastructure.
- MQTT networking implementation.
- Background and asynchronous execution.
- Multi-line routing frameworks.
- Device-status implementation.

## OUT OF SCOPE

Do not implement or modify:

- Production MQTT serialization.
- MQTT publishing or client integration.
- `EventPublisher` implementations.
- Broker connections.
- Retry loops or recovery frameworks.
- Production Python source files.
- Public dataclass or interface contracts.
- Existing automated tests.
- New runtime validations.
- Dependencies or project configuration.
- CI workflows or quality gates.
- Device status.
- Streamlit dashboard.
- Domain inspection decisions.
- Model training or inference behavior.
- Pipeline orchestration.
- Raspberry Pi deployment.
- Benchmarking.

Do not create a new ADR.

Do not change ADR-005 or ADR-007.

Do not mark M5 as completed.

## INPUTS / CONTRACTS

### Mandatory authoritative inputs

- `.agent/tasks/TASK-020.md`
- `GEMINI.md`
- `.agent/rules/implementation.md`
- `docs/architecture.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/006-mqtt-event-contract.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/mqtt-inspection-event-contract.md`
- `src/vision_iot/hardware/camera.py`
- `src/vision_iot/vision/contracts.py`
- `src/vision_iot/vision/postprocessing.py`
- `src/vision_iot/domain/contracts.py`
- `src/vision_iot/domain/inspection.py`
- `tests/test_acquisition.py`

Read additional existing Frame producer and timestamp propagation files if necessary for audit completeness.

### Existing contract constraints

- `Frame.timestamp: float`
- `InferenceResult.timestamp: float`
- `InspectionEvent.timestamp: float`
- `InspectionStatus`
- `InspectionReason`
- `InspectionEvent.evidence`
- Existing synchronous `FrameSource` and inspection boundaries.

No API changes are authorized.

## EXPECTED OUTPUT

Exactly three modified documentation files:

```text
docs/
├── adr/
│   ├── 004-vision-contracts.md
│   └── 006-mqtt-event-contract.md
└── mqtt-inspection-event-contract.md
```

The files must form a coherent and non-contradictory normative documentation baseline.

No new production files or tests are expected.

## ALLOWED CHANGES

The Implementation Agent may modify ONLY:

1. `docs/adr/004-vision-contracts.md`
2. `docs/adr/006-mqtt-event-contract.md`
3. `docs/mqtt-inspection-event-contract.md`

No other files may be created, modified, deleted or renamed.

## FORBIDDEN CHANGES

Forbidden paths include:

- `src/**`
- `apps/**`
- `tests/**`
- `models/**`
- `deploy/**`
- `.github/**`
- `.agent/**`
- `pyproject.toml`
- `Makefile`
- `requirements*.txt`
- `docs/architecture.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/007-execution-model.md`
- `docs/project-context.md`

Do not modify Git configuration, switch branches, commit, merge, rebase or push.

## ACCEPTANCE CRITERIA

1. All integrated Architecture-v2 Frame producers are identified and inspected.
2. Actual source timestamp behavior is described accurately.
3. FakeFrameSource's injected-frame behavior is correctly distinguished from production clock generation.
4. Synthetic test timestamps are not mistaken for production clock semantics.
5. OpenCVFrameSource's timestamp sampling point is accurately documented.
6. Any incompatible source semantics cause explicit escalation.
7. ADR-004 establishes compatible POSIX epoch timestamp semantics.
8. ADR-004 preserves originating frame correlation.
9. No new timestamp fields or dataclass changes are introduced.
10. Inference duration remains explicitly distinct from frame timestamp.
11. ADR-006 includes the ratified inspection-event topic.
12. Device-status and inspection topics are separated.
13. The legacy detections topic is not treated as the Architecture-v2 event contract.
14. Schema version `"1.0"` is explicit.
15. Exactly eight required top-level fields are defined.
16. Field types and ownership are unambiguous.
17. External metadata does not leak into internal domain contracts.
18. Version compatibility rules are explicit.
19. UUIDv4 event identity is specified.
20. Stable identity and payload across retries are specified.
21. Consumer deduplication responsibility is specified.
22. No cross-restart durability guarantee is claimed.
23. External timestamp format is explicitly UTC ISO 8601 with six fractional digits.
24. POSIX epoch conversion is justified by the acquisition audit.
25. Non-finite or unrepresentable timestamp handling is explicit.
26. Current status mapping is complete.
27. Schema v1.0 requires a non-null reason string.
28. `UNSUPPORTED_MODEL` maps faithfully.
29. Future reason nullability remains deferred.
30. Evidence arrays and detection mapping are defined.
31. Bounding-box coordinate semantics remain unchanged.
32. No unrelated inference detections are fabricated as evidence.
33. QoS 1 and duplicate-delivery limitations are accurate.
34. Publication completion levels are distinguished.
35. Operational errors are surfaced without changing domain outcomes.
36. The MQTT specification aligns with ratified ADR-006.
37. Deferred capabilities remain clearly excluded.
38. No production behavior changes occur.
39. No unauthorized files are changed.
40. Existing quality gates pass.
41. Independent Review Agent returns PASS.
42. Human Gate approves the final deliverable.

## REQUIRED TESTS

This task is documentation-only.

Do not create or modify automated tests.

Independently inspect existing tests for timestamp behavior and provenance.

Run the complete existing lint, test and pre-commit quality gates.

Report any difference between documented normative requirements and current runtime enforcement.

## VALIDATION COMMANDS

From the repository root:

```bash
git status -sb
git diff --check
git diff --stat

PATH=.venv/bin:$PATH make lint
PATH=.venv/bin:$PATH make test
.venv/bin/pre-commit run --all-files

git diff --check
git status --short
```

Verify that exactly the three authorized documentation files are modified.

Inspect updated ADR content and the MQTT specification directly.

Do not bypass failing checks.

## DEPENDENCIES

- TASK-019 integrated into `main`.
- M5.A formally closed by Architecture.
- MQTT contract conditionally accepted by Architecture.
- TASK-020 identifier available.
- Current repository baseline clean.
- No conflicting uncommitted changes.
- Existing quality environment available.

## BLOCKING CONDITIONS

### ARCHITECTURE_DECISION_REQUIRED

Stop and escalate if:

- Any integrated Architecture-v2 production Frame producer uses incompatible timestamp semantics.
- POSIX source time cannot be established without changing public contracts or production behavior.
- ADR-004 cannot be clarified without contradicting an accepted contract.
- The approved external schema cannot faithfully represent current domain outcomes.
- Non-null reason conflicts with existing supported domain behavior.
- The selected topic or identity contract is incompatible with an established requirement.
- Correct publication would require persistence, additional fields, asynchronous operation or new dependencies.
- Documentation alignment requires changing an accepted architectural decision.

Do not silently reinterpret timestamps or broaden the task scope.

### TASK_BLOCKED

Stop if:

- Required repository files are unavailable.
- The expected branch or TASK contract is missing.
- The working tree contains unauthorized changes.
- Required validation cannot be completed due to an unresolved environmental blocker.

### HUMAN_DECISION_REQUIRED

Stop if:

- A required choice exceeds the task's granted authority but does not constitute a defined architectural conflict.
- Unauthorized file changes would be necessary.

### RETRY_EXHAUSTED

Stop if:

- Repeated bounded correction attempts cannot resolve a validation or documentation failure within the authorized scope.

## DELIVERABLES

Return an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created, modified or deleted file.

### IMPLEMENTATION SUMMARY

Describe the ADR-004 clarification, ADR-006 ratification and MQTT specification alignment.

### TIMESTAMP AUDIT

Identify each inspected Frame producer, its timestamp source and its compatibility conclusion.

Distinguish actual production behavior from synthetic test fixtures.

### TESTS ADDED / UPDATED

Expected: None.

### VALIDATION RESULTS

Report all validation commands and actual outcomes.

### DEVIATIONS

Report deviations or `None`.

### BLOCKERS

Report unresolved blockers or `None`.

### OUT-OF-SCOPE OBSERVATIONS

Record relevant findings that were deliberately not implemented.

Do not commit or integrate changes.

Stop after returning the Implementation Report.
