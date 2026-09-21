# TASK-002 — Materialize Architecture v2 and Initial ADRs

## STATUS

READY

## MILESTONE

M0 — Architecture Baseline

## OBJECTIVE

Materialize the accepted Architecture v2 baseline of `vision-iot-pi5` as concise, version-controlled repository documentation.

Create:

- the main system architecture document,
- the initial set of Architecture Decision Records (ADRs) representing the decisions already accepted during Architecture v2 design.

This task documents existing decisions. It must not redesign, reinterpret, or extend the architecture.

## WHY

Architecture v2 has already been designed and accepted outside the repository.

Future implementation tasks and agents require a stable repository-owned architectural source of truth so that architectural constraints do not depend on conversational context.

After this task, implementation and review agents must be able to determine:

- what the system is intended to do,
- the architectural boundaries,
- the main processing pipeline,
- the ownership of project contracts,
- the initial inference strategy,
- the MQTT/event model,
- the testing and benchmarking strategy,
- the deployment baseline,
- the target repository structure,
- and which capabilities are intentionally deferred.

## ARCHITECTURE REFERENCES

The authoritative input for this task is the accepted Architecture v2 specification supplied in this TASK under `INPUTS / CONTRACTS`.

Do not invent architectural decisions beyond those explicitly provided here.

The ADS governance defined by:

- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`

also applies.

## SCOPE

Create the following architecture documentation:

- `docs/architecture.md`
- `docs/adr/README.md`
- ADR files under `docs/adr/` representing the accepted Architecture v2 decisions D1–D12.

The architecture documentation must be concise, implementation-oriented, and suitable as authoritative context for future implementation agents.

### Main architecture document

`docs/architecture.md` must describe at minimum:

- system purpose,
- initial inspection scenario,
- architectural principles,
- layered architecture,
- main processing flow,
- ownership and direction of dependencies,
- stable project-owned contracts,
- domain decision boundary,
- MQTT integration boundary,
- dashboard role,
- testing strategy,
- benchmarking strategy,
- deployment baseline,
- target repository structure,
- implementation milestones,
- explicitly deferred capabilities.

It should reference ADRs rather than duplicating their full rationale.

### ADR index

`docs/adr/README.md` must provide a concise index of the Architecture v2 ADRs and their status.

### ADRs

Materialize decisions D1–D12 as individual ADRs or as the minimum clear ADR decomposition that preserves every accepted decision without changing its meaning.

Each ADR must include at minimum:

- Title
- Status
- Context
- Decision
- Consequences

All materialized decisions are `Accepted`.

## OUT OF SCOPE

Do not:

- modify application code,
- create `src/`,
- modify existing tests,
- modify CI,
- modify README,
- modify deployment files,
- modify training code,
- modify model artifacts,
- add dependencies,
- implement any architecture described here,
- redesign Architecture v2,
- introduce new architectural decisions,
- select a final production inference runtime before benchmarking,
- introduce concurrency,
- implement MQTT changes,
- implement dashboard changes,
- create application contracts,
- create schemas in code,
- create new ADS rules,
- modify existing ADS rules,
- modify TASK-001 or TASK-TEMPLATE.

## INPUTS / CONTRACTS

The following Architecture v2 decisions are authoritative and must be materialized without changing their meaning.

### System purpose and initial scenario

`vision-iot-pi5` is an Edge AI visual inspection system intended as a portfolio-quality implementation demonstrating computer vision, embedded Linux / edge deployment, IoT integration, and software engineering practices.

The initial controlled scenario is:

- fixed camera,
- one package or box per inspection,
- visible package damage detection,
- supervised object detection,
- initially generic `damage` detection,
- local inference on Raspberry Pi 5.

The system must remain evolvable without prematurely introducing complexity.

### Layered architecture

The accepted logical layers are:

1. Hardware
2. Vision
3. Domain
4. Infrastructure

Dependencies must preserve separation of concerns.

Hardware owns frame acquisition and physical-device interaction.

Vision owns preprocessing, model execution, and postprocessing.

Domain owns inspection decisions and business meaning.

Infrastructure owns external communication and integration concerns such as MQTT.

### Main processing flow

The accepted conceptual flow is:

```text
FrameSource
    ↓
Preprocessor
    ↓
InferenceEngine
    ↓
Postprocessor
    ↓
InferenceResult
    ↓
InspectionLogic
    ↓
InspectionEvent
    ↓
EventPublisher
    ↓
MQTT
    ↓
Dashboard / External Consumers
```

The dashboard is an external consumer and is not part of the critical inference path.

### D1 — Vision task

Use supervised object detection with damage localization.

The initial task is not image-level classification and not unsupervised anomaly detection.

### D2 — Initial model strategy

The initial reference model is YOLO26n using pretrained weights followed by project-specific fine-tuning.

The model must remain replaceable.

The architecture must not couple project contracts directly to Ultralytics-specific output structures.

### D3 — Inference runtime strategy

Define a runtime-agnostic `InferenceEngine` boundary.

Initial runtime strategy:

- ONNX is the baseline portability path.
- NCNN is an optimized candidate for Raspberry Pi 5.
- The production runtime must be selected using benchmark evidence on the Raspberry Pi 5.

Do not declare ONNX or NCNN the final production winner before benchmarking.

### D4 — Vision contracts

The project owns stable contracts rather than exposing framework-specific structures across layers.

Conceptual contracts include:

#### Frame

Contains at minimum:

- id,
- timestamp,
- image,
- width,
- height.

#### ModelInput

Represents the preprocessed model input together with metadata required to translate inference output back to the original frame.

#### RawInference

Internal Vision-layer representation of raw runtime/model output.

It is not a public domain contract.

#### Detection

Contains at minimum:

- class_id,
- class_name,
- confidence,
- bounding_box.

Bounding boxes exposed by the stable contract use original-frame coordinates.

#### InferenceResult

Contains at minimum:

- frame_id,
- timestamp,
- detections,
- inference_time_ms.

`InferenceResult` does not decide whether an inspection is `OK` or `DAMAGED`.

### D5 — Domain inspection contract

Inspection decisions belong to the Domain layer.

Conceptual `InspectionEvent` contains at minimum:

- inspection_id,
- timestamp,
- frame_id,
- status,
- defects,
- processing_time_ms.

Initial inspection statuses:

- `OK`
- `DAMAGED`

An inference failure must never be interpreted as `OK`.

### D6 — MQTT event contract

Accepted topic structure:

```text
vision-iot/{device_id}/inspection/events
vision-iot/{device_id}/status
```

A telemetry namespace is reserved for future use.

Inspection events use a versioned schema containing at minimum:

- schema_version,
- event_id,
- device_id,
- inspection_id,
- timestamp,
- status,
- defects,
- processing_time_ms.

Rules:

- timestamps use UTC ISO 8601,
- publish both `OK` and `DAMAGED` inspections,
- inspection events use QoS 1,
- inspection events are not retained,
- device status is retained,
- initial device statuses are `ONLINE`, `OFFLINE`, and `ERROR`,
- `event_id` supports consumer-side deduplication,
- images are not transported through MQTT in the initial architecture.

### D7 — Execution model

The initial application pipeline is:

- single process,
- synchronous,
- intentionally simple.

Do not introduce threads, asyncio, multiprocessing, or distributed services until benchmark evidence or a concrete requirement justifies them.

Pipeline failures must remain distinguishable.

An inference failure must not produce a false successful `OK` inspection.

### D8 — Dashboard

The initial dashboard uses Streamlit.

It is an external MQTT consumer and must not be an architectural dependency of the inspection pipeline.

Initial dashboard responsibilities include presenting:

- device status,
- total inspections,
- OK inspections,
- damaged inspections,
- defect rate,
- recent inspections,
- defect confidence information,
- processing/inference latency information.

Live video is not required for the MVP.

### D9 — Testing strategy

Testing is organized into:

1. Unit tests
2. Contract tests
3. Integration tests
4. Hardware / End-to-End tests

The majority of tests should be deterministic and hardware-independent.

Use fakes/test doubles for hardware and infrastructure boundaries where appropriate.

Golden images may be used for deterministic vision-pipeline validation.

Contract tests protect stable boundaries.

CI is the real software quality gate.

Hardware-dependent and performance validation may run separately from normal CI.

### D10 — Benchmarking strategy

Benchmark the pipeline with explicit stage timing for:

- capture,
- preprocessing,
- inference,
- postprocessing,
- inspection logic,
- publishing,
- end-to-end processing.

Report performance using appropriate measurements including:

- P50 latency,
- P95 latency,
- throughput,
- CPU usage,
- RAM usage,
- model/runtime artifact size.

Computer-vision quality metrics such as precision, recall, and mAP are evaluated separately from runtime performance.

Benchmark results must include enough environment/configuration context to be reproducible.

No performance claim should be presented as achieved without benchmark evidence.

### D11 — Deployment baseline

Initial deployment target:

- Raspberry Pi 5,
- host Linux,
- Python virtual environment.

Docker is intentionally excluded from the initial deployment baseline.

The deployment architecture should remain compatible with a future `systemd`-managed service, but the existing repository service configuration must be reviewed before being treated as authoritative.

Configuration must remain external to application code.

Models must be independently versionable from application source.

The dashboard and MQTT broker are not required to execute on the Raspberry Pi.

### D12 — Target repository structure

The target structure is conceptually:

```text
src/
└── vision_iot/
    ├── application/
    ├── domain/
    ├── vision/
    ├── hardware/
    ├── infrastructure/
    └── config/

apps/
└── dashboard/

training/
tools/
tests/
config/
models/
data/
benchmarks/
deploy/
docs/
└── adr/

.github/
pyproject.toml
README.md
```

This is a target structure, not authorization to create empty directories or abstractions prematurely.

Migration from the existing repository must be incremental rather than a rewrite.

### Implementation milestones

Accepted implementation sequence:

- M0 — Architecture Baseline
- M1 — Core Foundation
- M2 — Acquisition
- M3 — Vision Pipeline
- M4 — Domain Inspection
- M5 — Event Distribution
- M6 — Vertical Slice
- M7 — Dataset / Training
- M8 — Raspberry Pi Deployment
- M9 — Benchmark and Runtime Selection
- M10 — Portfolio Hardening

### Explicitly deferred capabilities

The following are intentionally deferred unless a later TASK and architectural decision introduce them:

- DHT22 integration,
- PIR integration,
- advanced telemetry,
- live video dashboard streaming,
- images transported through MQTT,
- cloud integration,
- Docker,
- Kubernetes,
- microservices,
- concurrency,
- complex persistence,
- fleet management,
- OTA updates,
- React frontend,
- production anomaly-detection pipeline,
- multiclass defect taxonomy before supporting data exists,
- advanced observability infrastructure.

An AI reasoning layer may be explored later as an experimental capability but must never be required for the critical inspection path.

## EXPECTED OUTPUT

The implementation should result in architecture documentation equivalent to:

```text
docs/
├── architecture.md
└── adr/
    ├── README.md
    ├── 001-vision-task.md
    ├── 002-model-strategy.md
    ├── 003-inference-runtime.md
    ├── 004-vision-contracts.md
    ├── 005-domain-inspection-contract.md
    ├── 006-mqtt-event-contract.md
    ├── 007-execution-model.md
    ├── 008-dashboard.md
    ├── 009-testing-strategy.md
    ├── 010-benchmarking-strategy.md
    ├── 011-deployment-baseline.md
    └── 012-target-repository-structure.md
```

Equivalent concise naming is acceptable if D1–D12 remain clearly traceable.

No implementation code is expected.

## ALLOWED CHANGES

The Implementation Agent may create or modify only:

- `docs/architecture.md`
- `docs/adr/README.md`
- `docs/adr/*.md`

No other files are authorized.

The existing `.agent/tasks/TASK-002.md` contract is human-authored input and must not be modified by the Implementation Agent.

## FORBIDDEN CHANGES

Do not modify:

- `.agent/`
- `GEMINI.md`
- `apps/`
- `tests/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- `.github/`
- `README.md`
- `pyproject.toml`
- dependency files
- application source files

Also forbidden:

- adding dependencies,
- changing Architecture v2 decisions,
- introducing new architectural decisions,
- implementing architecture,
- weakening tests,
- expanding TASK scope,
- changing acceptance criteria,
- making unrelated refactors,
- declaring unbenchmarked performance,
- selecting a final inference runtime without benchmark evidence.

## ACCEPTANCE CRITERIA

1. `docs/architecture.md` exists.
2. `docs/adr/README.md` exists.
3. Accepted decisions D1–D12 are represented and clearly traceable.
4. All Architecture v2 decisions are documented without changing their accepted meaning.
5. The main architecture document describes the system, layers, processing flow, boundaries, contracts, testing, benchmarking, deployment, repository direction, milestones, and deferred capabilities.
6. Architecture documentation clearly separates Vision responsibilities from Domain inspection decisions.
7. `InferenceResult` does not contain an `OK` / `DAMAGED` decision.
8. Inference/runtime implementation details do not leak into stable cross-layer contracts.
9. Runtime selection remains benchmark-driven; no final ONNX-vs-NCNN winner is declared.
10. MQTT topics, event semantics, QoS/retention rules, timestamp convention, status model, and image exclusion are documented.
11. Initial execution remains single-process and synchronous.
12. Dashboard remains an external consumer rather than a critical-path dependency.
13. Testing levels and deterministic/hardware-independent testing principles are documented.
14. Benchmarking distinguishes runtime performance from computer-vision quality.
15. Raspberry Pi 5 + host Linux + virtual environment remains the initial deployment baseline.
16. Docker remains excluded from the initial deployment baseline.
17. Repository migration is described as incremental rather than a rewrite.
18. Deferred capabilities are explicitly documented.
19. No application code, tests, CI, README, ADS rules, dependencies, or deployment files are changed.
20. Documentation is concise enough to be practical context for future agents.

## REQUIRED TESTS

No application unit tests are required.

Validation is documentation-, structure-, and diff-based.

The Implementation Agent must verify:

- only authorized documentation files were created or modified,
- D1–D12 are all represented,
- required architecture topics are present,
- no existing application/test/CI/ADS files were modified,
- no whitespace errors are present.

## VALIDATION COMMANDS

At minimum:

```bash
git status --short
git diff --check
git diff
```

Because newly created untracked files are not shown by normal `git diff`, the agent must also directly inspect all created architecture files and report them explicitly.

Do not stage files solely to make them visible to `git diff`.

Additional read-only inspection commands are allowed.

The agent must not commit, merge, rebase, force-push, reset the branch, or integrate the task.

## DEPENDENCIES

No new software dependencies.

Prerequisites:

- TASK-001 completed,
- ADS v1 foundation available,
- Architecture v2 accepted,
- clean task branch based on the latest human-approved `main`.

## BLOCKING CONDITIONS

Stop and escalate instead of guessing if:

- Architecture v2 contains an unresolved contradiction,
- materialization requires a new architectural decision,
- an accepted decision cannot be represented without changing its meaning,
- required changes fall outside `ALLOWED CHANGES`,
- existing application/test/ADS files would need modification,
- a dependency appears necessary,
- acceptance criteria cannot be satisfied without scope expansion.

Use one of:

- `TASK_BLOCKED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `HUMAN_DECISION_REQUIRED`
- `RETRY_EXHAUSTED`

as appropriate.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Summarize how Architecture v2 and D1–D12 were materialized.

### TESTS ADDED / UPDATED

Expected:

`None`

If an existing test was modified, this TASK must not be reported as successfully completed.

### VALIDATION RESULTS

Report each validation command and its result.

Explicitly report how newly created untracked files were inspected.

Do not hide validation failures.

### DEVIATIONS

Any deviation from this TASK.

Expected when correctly completed:

`None`

### BLOCKERS

Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS

Relevant observations discovered during documentation work that were intentionally not implemented.
