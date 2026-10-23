# TASK-019 — M5.A MQTT Inspection Event Contract Specification

## STATUS

READY

## MILESTONE

M5 — Event Distribution / M5.A — MQTT Inspection Event Contract Specification

## OBJECTIVE

Produce a bounded, reviewable specification for the external MQTT inspection-event contract that faithfully represents the existing project-owned `InspectionEvent` without changing domain semantics.

The specification must propose exact topic, payload, versioning, identity, timestamp, evidence, delivery and failure-handling rules for subsequent architectural assessment.

This is a documentation-only increment. Proposed transport decisions must not be treated as accepted until Architecture approves them.

## WHY

M4 has been formally closed by Architecture.

The project now possesses a stable internal inspection event representation, but no Architecture-v2 production event-distribution implementation.

ADR-006 accepts MQTT as the transport and establishes foundational decisions:

- Separate inspection-event and device-status topic categories.
- Versioned inspection-event schema.
- External `event_id` for deduplication.
- UTC ISO 8601 timestamps.
- MQTT QoS 1.
- No image transportation through MQTT.

However, ADR-006 does not yet define a sufficiently precise external inspection-event contract for production implementation.

TASK-019 prepares that specification so a later implementation task will not have to invent external field names, identity semantics, retry behavior or serialization rules.

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/006-mqtt-event-contract.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/project-context.md`
- `docs/domain-inspection-policy.md`
- `.agent/tasks/TASK-017.md`
- `.agent/tasks/TASK-018.md`
- Architecture → Project Context Handoff, 2026-10-23: *M4 Milestone Closure & M5 Event Distribution Planning*

Relevant architectural decisions:

- `M4_CLOSURE_APPROVED`
- `M5_PLANNING_AUTHORIZED`
- `TASK_019_MATERIALIZATION_AUTHORIZED`
- `M5_PRODUCTION_IMPLEMENTATION_NOT_AUTHORIZED`
- `MQTT_EVENT_CONTRACT_REQUIRED`

ADR-006 remains authoritative.

Any proposed clarification requiring a normative ADR amendment must return to Architecture.

No ADR modification is authorized under this TASK.

## SCOPE

### 1. Transport boundary

Document the separation between:

- The internal project-owned `InspectionEvent`.
- The external MQTT inspection-event message.
- The future publisher adapter.
- External consumers.

The external message is a transport representation, not a replacement for the internal domain event.

Specify which responsibilities belong to transport mapping, publishing and consuming systems.

Do not introduce production classes or interfaces.

### 2. MQTT topic contract

Propose one concrete, unambiguous MQTT topic structure for inspection events.

Specify:

- Exact topic format.
- Allowed dynamic segments, if any.
- Segment naming and validation rules.
- Relationship to the separate device-status topic category.
- Expected consumer subscription behavior.

The proposed topic must not silently inherit the legacy `detections` topic used by the prototype.

Do not implement device-status publishing or define an unrelated device-status payload schema.

### 3. Versioned payload schema

Propose a concrete JSON-compatible external inspection-event representation.

Document:

- Exact field names.
- Field types.
- Required versus optional fields.
- Field ownership.
- Allowed value representations.
- Serialization rules.
- Validation requirements.
- A representative illustrative JSON payload.

Clearly identify which fields originate from `InspectionEvent` and which are transport metadata.

Mark the entire proposed schema as pending Architecture approval.

Do not add transport-specific fields to the internal `InspectionEvent`.

### 4. Schema versioning

Propose:

- How schema version is represented.
- Initial version format.
- Compatibility expectations.
- Rules for interpreting unsupported schema versions.
- Responsibilities of publishers and consumers.

Do not introduce a schema-registry service or generic version-negotiation framework.

### 5. Event identity and deduplication

Specify a proposed relationship between:

- `InspectionEvent.inspection_id`
- External `event_id`

Address:

- Ownership of external message identity.
- Identity assignment before initial publication.
- Stability across retries of the same logical event.
- Behavior for repeated delivery under QoS 1.
- Deduplication expectations for consumers.

Do not assume `event_id` and `inspection_id` are identical without an explicit proposal and justification.

Do not introduce a persistence engine or durable delivery queue.

If identity stability cannot be specified without additional lifecycle guarantees, document the limitation and escalate any required architectural decision.

### 6. Timestamp serialization

Specify how the existing:

`InspectionEvent.timestamp: float`

is represented externally as an ADR-006-compliant UTC ISO 8601 timestamp.

The proposal must define:

- Interpretation of the existing source timestamp consistent with accepted contracts.
- UTC representation.
- Precision and formatting.
- Timezone notation.
- Deterministic conversion expectations.
- Invalid or unsupported timestamp behavior.

Do not introduce a new domain timestamp.

Do not substitute publication time for source-frame time without architectural authorization.

If the existing timestamp semantics are insufficient to determine a correct conversion, record the gap explicitly and escalate rather than silently inventing a new invariant.

### 7. Inspection status and reason

Specify the external representation of:

`InspectionStatus`:

- `OK`
- `DAMAGED`
- `INCONCLUSIVE`

`InspectionReason`:

- `UNSUPPORTED_MODEL`

Ensure the current conservative policy can be represented faithfully.

Specify how unsupported status or reason values should be handled.

Unknown values must never be silently interpreted as `OK`.

Do not define additional internal enum members or hypothetical production meanings.

### 8. Evidence representation

Assess whether external consumers require the domain event's:

`evidence: tuple[Detection, ...]`

Make one clear, justified proposal:

- Include a minimal external detection representation; or
- Exclude detailed evidence from the initial external payload.

Explain the consequences for consumers and compatibility with the inspection objective.

If evidence is proposed for inclusion, define the exact representation of any included detection fields and bounding boxes.

Do not serialize arbitrary Python objects, ONNX tensors or runtime-specific data structures.

Do not include raw image data.

Do not change the meaning of empty evidence in the current conservative policy.

### 9. MQTT delivery semantics

Preserve the accepted QoS 1 requirement.

Document:

- At-least-once delivery semantics.
- Possibility of duplicate delivery.
- Relationship between MQTT packet-level behavior and logical event identity.
- Publisher responsibilities.
- Consumer deduplication responsibilities.
- Retry identity stability.
- The absence of an exactly-once guarantee from QoS 1.

Clarify the limitations of non-durable publisher operation where relevant.

Do not promise persistence across process crashes without an explicit Architecture decision.

### 10. Failure behavior

Specify how the future application layer should distinguish:

- Serialization failure.
- Invalid transport payload.
- Publisher or connection failure.
- Publication acknowledgment or completion failure, where applicable.

Failures must not be transformed into `InspectionStatus` values.

Do not introduce new domain reasons or fabricate domain events to represent transport failures.

Do not implement retry loops, queues, workers or a failure-handling framework.

### 11. Deterministic verification expectations

Specify testable expectations for a future serializer and publisher.

Include appropriate cases such as:

- Valid `INCONCLUSIVE / UNSUPPORTED_MODEL` mapping.
- Preservation of domain identity and correlation.
- Consistent external event identity across retries.
- Timestamp conversion.
- Schema version representation.
- Exact status and reason serialization.
- Empty evidence behavior.
- Invalid enum or payload handling.
- Serialization error propagation.
- QoS 1 configuration.
- Duplicate-delivery handling expectations.

Tests must be feasible without a physical Raspberry Pi or production MQTT broker.

Do not create tests or production implementation under TASK-019.

### 12. Existing prototype assessment

Inspect the existing MQTT-related code:

- `apps/pi_detector/mqtt_client.py`
- `apps/pi_detector/main.py`
- `apps/streamlit_dashboard/Home.py`

Use this inspection only to identify potentially relevant historical behavior and migration risks.

Clearly distinguish prototype behavior from Architecture-v2 requirements.

Do not modify, reuse automatically, or promote legacy topics, payloads or implementations into the accepted contract.

### 13. Accepted decisions versus proposals

Clearly distinguish:

- Accepted requirements originating from ADR-006 or other authoritative architecture documents.
- Proposed transport-contract details requiring Architecture approval.
- Explicit unresolved architectural questions.

Do not present proposed field names, identity rules, timestamp assumptions or evidence schemas as already accepted architectural decisions.

### 14. Architectural handoff readiness

Conclude with a decision register summarizing:

- Proposed exact MQTT topic.
- Proposed payload schema and version.
- Proposed `event_id` semantics.
- Proposed timestamp conversion.
- Proposed evidence handling.
- Proposed delivery and failure rules.
- Any remaining unresolved issues.
- Decisions requiring ADR-006 clarification.

The specification must provide Architecture with concrete recommendations, not merely an unranked list of alternatives.

## OUT OF SCOPE

- Production MQTT client implementation.
- Concrete `EventPublisher` code.
- MQTT broker integration.
- Application orchestration.
- Changes to domain or vision contracts.
- New `InspectionStatus` or `InspectionReason` values.
- Device-status publishing.
- Dashboard modifications.
- Retry-loop implementation.
- Durable message queues or persistence.
- Background workers.
- New asynchronous execution mechanisms.
- New dependencies.
- Schema registry infrastructure.
- Cloud integrations.
- Dataset/model development.
- Camera and Raspberry Pi deployment.
- Performance benchmarking.
- ADR modifications.
- Final approval of the proposed MQTT contract.
- Implementation of subsequent M5 increments.

## INPUTS / CONTRACTS

Existing internal domain event:

```python
@dataclass
class InspectionEvent:
    inspection_id: str
    frame_id: str
    timestamp: float
    status: InspectionStatus
    reason: InspectionReason
    evidence: tuple[Detection, ...]
```

Existing status values:

```text
OK
DAMAGED
INCONCLUSIVE
```

Existing reason values:

```text
UNSUPPORTED_MODEL
```

Current reference policy:

```text
UnvalidatedReferenceInspectionLogic
    -> INCONCLUSIVE
    -> UNSUPPORTED_MODEL
    -> evidence = ()
```

Accepted ADR-006 transport constraints:

```text
Transport: MQTT
Topics: inspection events and device status separated
Schema: versioned
External identity: event_id
Timestamp: UTC ISO 8601
QoS: 1
Images in MQTT: prohibited
```

Existing M4 contracts must remain unchanged.

## EXPECTED OUTPUT

Create exactly one document:

```text
docs/
└── mqtt-inspection-event-contract.md
```

Required sections:

1. Purpose and scope.
2. Accepted architecture constraints.
3. Internal-to-external transport boundary.
4. Proposed inspection-event MQTT topic.
5. Proposed JSON payload and field dictionary.
6. Schema versioning and compatibility.
7. External event identity and deduplication.
8. Timestamp conversion and formatting.
9. Inspection status and reason mapping.
10. Evidence inclusion or exclusion.
11. QoS 1 and delivery guarantees.
12. Serialization and publication failure behavior.
13. Legacy MQTT compatibility observations.
14. Future deterministic testing requirements.
15. Decision register and Architecture approval requests.
16. References.

The specification must be sufficiently precise for Architecture to accept, reject or amend the proposed transport contract.

It must not claim that a proposed schema is already approved for production.

## ALLOWED CHANGES

The Implementation Agent may create or modify ONLY:

- `docs/mqtt-inspection-event-contract.md`

The TASK contract `.agent/tasks/TASK-019.md` is created separately by Project Context before implementation.

No other repository files are authorized for modification.

## FORBIDDEN CHANGES

Do not modify:

- `docs/architecture.md`
- `docs/adr/`
- `docs/project-context.md`
- `docs/domain-inspection-policy.md`
- `.agent/rules/`
- `.agent/tasks/`
- `src/`
- `apps/`
- `tests/`
- `deploy/`
- `models/`
- `data/`
- `pyproject.toml`
- `Makefile`
- Requirements files
- CI configuration
- Pre-commit configuration
- Git configuration

No unrelated files or generated artifacts may be created.

## ACCEPTANCE CRITERIA

1. The internal and external event boundaries are explicitly separated.
2. A concrete MQTT inspection-event topic is proposed.
3. The topic format is unambiguous.
4. Inspection and device-status topic categories remain separate.
5. A concrete JSON-compatible versioned payload is proposed.
6. Exact external field names and types are documented.
7. Domain-derived fields and transport metadata are distinguished.
8. Schema versioning and compatibility expectations are specified.
9. External `event_id` ownership is explicitly addressed.
10. The relationship between `event_id` and `inspection_id` is explicit.
11. Logical event identity remains stable across retries under the proposal.
12. Consumer deduplication responsibilities are defined.
13. Timestamp serialization follows ADR-006 or explicitly escalates unresolved source semantics.
14. `OK`, `DAMAGED`, and `INCONCLUSIVE` are representable.
15. `UNSUPPORTED_MODEL` is representable without semantic loss.
16. Unsupported status and reason handling is specified.
17. Evidence inclusion or exclusion is explicitly justified.
18. No raw images or runtime-native objects are proposed for transport.
19. QoS 1 is preserved without claiming exactly-once delivery.
20. Serialization and publication failures remain separate from domain outcomes.
21. Deterministic serializer and publisher testing expectations are documented.
22. Existing prototype MQTT behavior is not silently promoted to the new architecture.
23. No domain or vision contracts are modified.
24. No production MQTT implementation is introduced.
25. No new dependencies, ADRs or configuration changes are introduced.
26. Remaining Architecture decisions are explicit.
27. Proposed transport decisions are not presented as accepted ADR-006 requirements.
28. The document is consistent with the current Architecture-v2 baseline.
29. Only the authorized documentation file is created or modified.
30. Existing repository quality gates pass.
31. Independent Review Agent returns `PASS`.
32. Human Gate approves the deliverable.

## REQUIRED TESTS

TASK-019 is documentation-only.

No new production tests or fixtures are authorized.

Required verification includes:

- Review of the entire proposed external schema.
- Validation against accepted ADR-006 constraints.
- Identity and retry consistency analysis.
- Status and reason fidelity analysis.
- Timestamp semantics review.
- Evidence representation review.
- Duplicate delivery and failure behavior review.
- Legacy-code isolation review.
- Verification of file-level scope.
- Execution of existing quality gates.

Independent Review must inspect the actual proposed contract, not merely the Implementation Report.

## VALIDATION COMMANDS

Run from the repository root with the project virtual environment activated:

```bash
black --check .
ruff check .
mypy apps src
pytest -q
make lint
make test
pre-commit run --all-files
git diff --check
git status --short
```

Inspect the complete new document even when it is untracked:

```bash
git diff --no-index -- /dev/null docs/mqtt-inspection-event-contract.md
```

The final command may return exit status `1` because it displays differences. This is expected and is not itself a validation failure.

Review whitespace explicitly because `git diff --check` does not inspect untracked content:

```bash
grep -n '[[:blank:]]$' docs/mqtt-inspection-event-contract.md || true
```

Report all actual results.

Do not bypass failing checks.

## DEPENDENCIES

- M4 formally closed by Architecture.
- TASK-017 completed and integrated.
- TASK-018 completed and integrated.
- ADR-006 accepted.
- M5.A documentation scope authorized by Architecture.
- TASK-019 confirmed as the next available identifier.
- Repository synchronized with `origin/main`.
- Existing development and quality tools available.

No new production dependency, model or hardware is required.

## BLOCKING CONDITIONS

Stop and escalate with `ARCHITECTURE_DECISION_REQUIRED` if:

- The proposed transport contract conflicts with ADR-006.
- A domain or vision contract change is required.
- `event_id` semantics cannot be specified without an unauthorized architectural mechanism.
- Existing timestamp semantics cannot support the required serialization without introducing a new normative invariant.
- Evidence representation requires modifying `InspectionEvent`.
- Durable delivery or crash recovery becomes a mandatory requirement.
- Asynchronous workers, queues or a new execution model become necessary.
- A new schema registry or generic event framework becomes necessary.
- A final normative transport decision is required before the proposed document can be completed.

Document bounded alternatives as proposals where possible; do not silently make authoritative architectural decisions.

Stop and escalate with `TASK_BLOCKED` if:

- Required repository references are unavailable.
- The deliverable cannot be completed within the authorized file-level scope.
- Existing quality gates fail for reasons outside TASK-019.

Stop and escalate with `HUMAN_DECISION_REQUIRED` if:

- Unauthorized file changes are required.
- Repository operations require human authorization.
- A workflow or task-scope conflict cannot be resolved within existing governance.

Use `RETRY_EXHAUSTED` when the bounded ADS correction loop reaches its configured limit.

Do not expand scope silently.

## DELIVERABLES

The Implementation Agent must return an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Summarize the proposed MQTT topic, payload, identity, timestamp, evidence, delivery and failure semantics.

### TESTS ADDED / UPDATED

Confirm that no production tests were added or modified.

### VALIDATION RESULTS

Report actual command outputs and scope verification.

### DEVIATIONS

Identify deviations from TASK-019.

### BLOCKERS

Identify unresolved blockers or required escalations.

### OUT-OF-SCOPE OBSERVATIONS

Record any relevant legacy MQTT observations or architectural questions without implementing unauthorized changes.

Do not commit, push, merge, rebase, switch branches or modify Git configuration.

Stop after authoring and validating the specification.

Independent Review, Human Gate and Git integration are separate ADS stages.
