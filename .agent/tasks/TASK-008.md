# TASK-008 — Acquisition Foundation

## STATUS

READY

## MILESTONE

M2 — Acquisition

## BASELINE

TASK-008 starts from the post-TASK-007 recovery checkpoint:

```text
0663cf3  docs: checkpoint project context after TASK-007
472a5a2  Merge branch 'task/007-core-foundation'
a5ef89d  feat: establish core package foundation (TASK-007)
```

Expected implementation branch:

```text
task/008-acquisition-foundation
```

TASK-007 established the minimum installable/importable Architecture-v2
package foundation under:

```text
src/vision_iot/
```

The blocking quality gate already covers both:

```text
apps
src
```

---

## OBJECTIVE

Establish the first project-owned Architecture-v2 acquisition boundary.

This TASK must materialize only:

1. the stable `Frame` data contract;
2. the minimal synchronous `FrameSource` abstraction;
3. a deterministic `FakeFrameSource`;
4. focused hardware-independent tests proving the acquisition boundary.

The intended dependency direction is:

```text
future application / pipeline
            |
            v
       FrameSource
            |
            +----------------+
            |                |
            v                v
    FakeFrameSource    future camera adapter
       (TASK-008)         (DEFERRED)
```

and:

```text
FrameSource
    |
    v
  Frame
```

TASK-008 must NOT introduce a concrete camera implementation.

---

## WHY

Architecture v2 defines the processing flow as:

```text
FrameSource
    -> Frame
    -> Preprocessor
    -> ModelInput
    -> InferenceEngine
    -> RawInference
    -> Postprocessor
    -> InferenceResult
    -> InspectionLogic
    -> InspectionEvent
    -> EventPublisher
```

TASK-007 intentionally stopped before materializing behavioral Architecture-v2
contracts.

The first dependency in this chain is now mature enough to implement.

Establishing `Frame` and `FrameSource` before implementing a real camera adapter
preserves:

- incremental migration;
- the smallest coherent architectural increment;
- stable project-owned contracts;
- deterministic hardware-independent testing;
- separation between project contracts and concrete hardware;
- the synchronous execution baseline;
- avoidance of speculative abstractions;
- avoidance of a big-bang rewrite.

A real camera implementation would combine contract materialization with
OpenCV integration, hardware behavior, and legacy migration and is therefore
explicitly deferred.

---

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/adr/012-target-repository-structure.md`
- `docs/project-context.md`
- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `.agent/tasks/TASK-007.md`

No Architecture-v2 change is authorized by this TASK.

No new ADR is required or authorized.

TASK-008 materializes decisions already accepted by Architecture v2.

If implementation requires a public contract decision not resolved by the
authoritative Architecture/ADR artifacts, the Implementation Agent must stop
and escalate rather than inventing the decision.

---

## ARCHITECTURAL PLACEMENT

The acquisition boundary belongs under:

```text
src/vision_iot/hardware/
```

TASK-008 may create this package because it now contains real
Architecture-v2 contracts/behavior rather than speculative empty scaffolding.

The intended minimum source structure is:

```text
src/
└── vision_iot/
    ├── __init__.py
    └── hardware/
        ├── __init__.py
        └── camera.py
```

No additional Architecture-v2 layer directories may be created.

`src/vision_iot/__init__.py` does not need modification for TASK-008 and is
therefore protected unless an unexpected technical requirement is escalated
before modification.

---

## CONTRACT — Frame

TASK-008 is authorized to materialize the Architecture-v2 `Frame` contract.

Conceptually:

```text
Frame(
    id,
    timestamp,
    image,
    width,
    height
)
```

### Required fields

`Frame` must contain:

- `id`
- `timestamp`
- `image`
- `width`
- `height`

### Required semantics

`Frame` represents one acquired image together with the minimum metadata
required by downstream Architecture-v2 processing.

It must remain independent from:

- YOLO;
- ONNX Runtime;
- NCNN;
- MQTT;
- Streamlit;
- domain inspection status;
- model-specific preprocessing;
- model-specific inference outputs.

`Frame` must NOT contain:

- OK/DAMAGED decisions;
- detections;
- model outputs;
- MQTT information;
- dashboard information;
- inference configuration.

### Image representation constraint

The implementation must first inspect:

```text
docs/adr/004-vision-contracts.md
```

and the relevant Architecture-v2 documentation before choosing the concrete
Python representation of `Frame.image`.

The implementation must use only a representation already justified by the
accepted architecture and existing dependency baseline.

Project Context does NOT authorize a new public image representation decision
in this TASK contract.

Do NOT independently invent a new architectural choice such as a new image
library, serialization format, or materially broader public representation.

If the authoritative architecture does not sufficiently determine a clean
representation for `Frame.image`, stop with:

```text
ARCHITECTURE_DECISION_REQUIRED
```

and explain the unresolved choice.

---

## CONTRACT — FrameSource

TASK-008 is authorized to materialize `FrameSource`.

`FrameSource` is the project-owned acquisition abstraction capable of
producing a `Frame`.

Consumers must depend on this project-owned abstraction rather than a concrete
camera API.

`FrameSource` must NOT expose:

- `cv2.VideoCapture`;
- OpenCV capture objects;
- USB-camera-specific details;
- Raspberry-Pi-specific camera details;
- concrete device identifiers as part of the generic abstraction.

### Execution model

`FrameSource` must follow the synchronous execution model established by
ADR-007.

Do NOT introduce:

- asynchronous APIs;
- threads;
- queues;
- callbacks;
- streaming frameworks;
- concurrency abstractions;
- lifecycle complexity not required by the contract.

The abstraction must remain minimal for one-inspection-at-a-time execution.

---

## TEST INFRASTRUCTURE — FakeFrameSource

TASK-008 is authorized to introduce a minimal deterministic:

```text
FakeFrameSource
```

Its sole purpose is to support deterministic hardware-independent testing of
the `FrameSource` boundary.

It must allow code to consume the `FrameSource` abstraction without requiring:

- Raspberry Pi hardware;
- USB camera hardware;
- OpenCV capture devices;
- network access;
- MQTT;
- model inference.

`FakeFrameSource` is test infrastructure, not a camera simulation framework.

Do NOT introduce:

- mocking frameworks;
- timing simulation;
- complex configurable scenarios;
- queues;
- asynchronous behavior;
- camera failure simulation unless directly required by the authorized
  contract tests;
- generalized fake/simulation infrastructure.

---

## CONTRACTS PERMITTED TO MATERIALIZE

Only:

```text
Frame
FrameSource
```

Additionally authorized solely as deterministic test infrastructure:

```text
FakeFrameSource
```

No other Architecture-v2 behavioral contract is authorized.

---

## CONTRACTS EXPLICITLY DEFERRED

Do NOT materialize:

```text
ModelInput
RawInference
Detection
InferenceResult

Preprocessor
InferenceEngine
Postprocessor

InspectionLogic
InspectionEvent

InspectionPipeline

EventPublisher
MqttPublisher
```

Also defer any additional abstraction not directly required to implement the
authorized `Frame` / `FrameSource` boundary.

---

## CONCRETE CAMERA IMPLEMENTATION DEFERRED

TASK-008 must NOT introduce a real camera adapter.

Do NOT implement or migrate:

```text
OpenCVFrameSource
CameraFrameSource
UsbCamera
cv2.VideoCapture integration
```

or equivalent concrete hardware acquisition behavior.

Existing camera-related code under:

```text
apps/
```

remains legacy / pre-Architecture-v2 code and must remain unchanged.

A future M2 increment may place a concrete camera implementation behind the
`FrameSource` boundary.

That work is not part of TASK-008.

---

## ERROR MODEL

A broader acquisition/camera error model is deferred.

Do NOT introduce a new error hierarchy or public camera error contract unless
the existing authoritative Architecture/ADRs already specify sufficient
semantics and implementation unexpectedly requires it.

Concrete camera failures are outside TASK-008 because no concrete camera
adapter is being implemented.

If public error semantics become necessary, stop and escalate.

---

## SCOPE

TASK-008 must:

1. Create the first real Architecture-v2 acquisition subsystem package:

   ```text
   src/vision_iot/hardware/
   ```

2. Materialize the `Frame` contract according to the accepted Architecture-v2
   contract.

3. Materialize the minimum synchronous `FrameSource` abstraction.

4. Add a minimal deterministic `FakeFrameSource`.

5. Add focused deterministic tests proving:

   - valid `Frame` construction;
   - acquisition through `FrameSource`;
   - substitutability through `FakeFrameSource`;
   - hardware-independent acquisition behavior.

6. Preserve the package foundation established by TASK-007.

7. Keep all new implementation independent from concrete camera hardware.

8. Ensure all new source code passes the existing blocking quality gate.

---

## OUT OF SCOPE

The following are explicitly outside TASK-008:

- concrete camera acquisition;
- OpenCV capture integration;
- Raspberry Pi camera integration;
- USB camera configuration;
- migration/refactoring of existing `apps/` camera code;
- model preprocessing;
- model inference;
- model postprocessing;
- detection contracts;
- inference-result contracts;
- inspection/domain logic;
- inspection orchestration;
- MQTT publishing;
- dashboard changes;
- event distribution;
- asynchronous execution;
- concurrency;
- queues;
- threading;
- streaming frameworks;
- camera failure simulation;
- generalized acquisition frameworks;
- new dependency injection mechanisms;
- new error hierarchy design;
- Architecture/ADR changes;
- dependency changes;
- quality-tool configuration changes;
- unrelated cleanup/refactoring.

---

## ALLOWED CHANGES

Implementation changes are restricted to exactly:

```text
src/vision_iot/hardware/__init__.py
src/vision_iot/hardware/camera.py
tests/test_acquisition.py
```

The human-controlled TASK artifact is also part of this branch:

```text
.agent/tasks/TASK-008.md
```

but the Implementation Agent must NOT modify it.

No other file may be changed without escalation and explicit human approval.

---

## FORBIDDEN CHANGES

Do NOT modify:

```text
apps/
training/
deploy/
models/
data/

docs/architecture.md
docs/adr/
docs/project-context.md
README.md
GEMINI.md

.agent/rules/
.agent/tasks/TASK-001.md
.agent/tasks/TASK-002.md
.agent/tasks/TASK-003.md
.agent/tasks/TASK-004.md
.agent/tasks/TASK-005.md
.agent/tasks/TASK-006.md
.agent/tasks/TASK-007.md
.agent/tasks/TASK-008.md

requirements.txt
requirements-dev.txt
requirements-ci.txt
requirements-train.txt

Makefile
.github/workflows/
.pre-commit-config.yaml
pyproject.toml

src/vision_iot/__init__.py
```

Do NOT modify existing tests.

Do NOT create:

```text
src/vision_iot/application/
src/vision_iot/domain/
src/vision_iot/vision/
src/vision_iot/infrastructure/
src/vision_iot/config/
```

Do NOT create additional acquisition modules/packages beyond the exact allowed
files without escalation.

---

## DEPENDENCY CONSTRAINTS

No dependency may be added, removed, upgraded, downgraded, or reconfigured.

Use only the existing project/runtime/tooling environment and Python standard
mechanisms where appropriate.

In particular, do NOT introduce:

- a new image-processing library;
- a new typing library;
- a dependency-injection framework;
- a mocking framework;
- a validation/modeling framework;
- a camera abstraction library.

If the authorized contracts cannot be implemented cleanly using the existing
dependency baseline, stop and escalate.

---

## REQUIRED TESTS

Add exactly:

```text
tests/test_acquisition.py
```

Tests must be:

- deterministic;
- hardware-independent;
- network-independent;
- model-independent;
- MQTT-independent;
- Raspberry-Pi-independent.

The tests must not require:

- physical camera hardware;
- `/dev/video*`;
- Raspberry Pi hardware;
- MQTT broker;
- model artifacts;
- internet access.

At minimum, tests must demonstrate:

1. a valid `Frame` can be created with:

   ```text
   id
   timestamp
   image
   width
   height
   ```

2. `FakeFrameSource` returns a valid `Frame`;

3. the fake can be consumed through the `FrameSource` abstraction rather than
   requiring knowledge of a concrete camera implementation;

4. acquisition behavior is deterministic and independent of physical
   hardware.

Avoid tests that merely assert private implementation details.

Existing tests are protected and must remain unchanged.

---

## ACCEPTANCE CRITERIA

1. `Frame` exists as a project-owned Architecture-v2 contract.

2. `Frame` exposes:
   - `id`
   - `timestamp`
   - `image`
   - `width`
   - `height`

3. `Frame` contains no model-specific semantics.

4. `Frame` contains no inspection/domain-decision semantics.

5. `Frame` contains no MQTT semantics.

6. `Frame` contains no dashboard semantics.

7. `Frame` contains no inference configuration.

8. The representation selected for `Frame.image` is already justified by the
   accepted architecture/dependency baseline; otherwise implementation
   escalates instead of inventing a new public contract decision.

9. `FrameSource` exists as a project-owned acquisition abstraction.

10. `FrameSource` produces/provides `Frame` instances according to the
    accepted synchronous execution model.

11. `FrameSource` does not expose OpenCV-specific capture objects.

12. `FrameSource` does not expose concrete camera implementation details.

13. No asynchronous acquisition API is introduced.

14. No concurrency/thread/queue abstraction is introduced.

15. A minimal deterministic `FakeFrameSource` exists.

16. `FakeFrameSource` can provide a valid `Frame` without physical hardware.

17. Code/tests can consume the fake through the `FrameSource` abstraction.

18. Tests verify meaningful `Frame` contract behavior.

19. Tests verify meaningful `FrameSource` substitutability.

20. Tests are deterministic.

21. Tests require no physical camera.

22. Tests require no Raspberry Pi hardware.

23. Tests require no network access.

24. Tests require no MQTT broker.

25. Tests require no model artifact.

26. No concrete camera adapter is introduced.

27. Existing code under `apps/` remains unchanged.

28. No inference contract is introduced.

29. No domain contract is introduced.

30. No event-distribution contract is introduced.

31. No pipeline orchestrator is introduced.

32. No additional Architecture-v2 layer is created.

33. No dependency is added, removed, or modified.

34. No quality gate is changed or weakened.

35. Black passes.

36. Ruff passes.

37. mypy passes for `apps` and `src`.

38. pytest passes.

39. `make lint` passes.

40. `make test` passes.

41. pre-commit passes.

42. Existing tests remain unchanged and passing.

43. Architecture v2 and ADRs remain unchanged.

44. All implementation changes remain inside `ALLOWED CHANGES`.

45. Final post-validation working-tree inspection confirms that validation
    generated no unintended tracked or untracked artifacts.

---

## DETERMINISTIC VALIDATION

The Implementation Agent must execute and report actual evidence for:

```bash
git status --short
git diff --check

black --check .
ruff check .
mypy apps src
pytest -q

make lint
make test

pre-commit run --all-files

git diff --name-only
git diff -- src/vision_iot/hardware/__init__.py \
            src/vision_iot/hardware/camera.py \
            tests/test_acquisition.py

git status --short
```

Because new files may be untracked and therefore absent from normal
`git diff`, the Implementation Agent must also directly inspect the complete
contents of:

```text
src/vision_iot/hardware/__init__.py
src/vision_iot/hardware/camera.py
tests/test_acquisition.py
```

The final `git status --short` is a mandatory post-validation check.

Any unintended generated artifact must be reported and removed before
submission, provided removal does not require an out-of-scope repository
change.

If safe removal itself requires an out-of-scope change, stop and escalate.

Editable package installation is not required solely for TASK-008 validation.

Do not modify Git configuration or quality-tool configuration to make
validation pass.

---

## BLOCKING / ESCALATION CONDITIONS

Stop implementation and escalate if:

1. Materializing `Frame.image` requires a public representation decision not
   already resolved by ADR-004 / accepted Architecture-v2 artifacts.

2. `FrameSource` requires asynchronous or concurrent semantics.

3. A new dependency is required.

4. A concrete OpenCV/camera implementation is required to validate the
   contract.

5. Existing code under `apps/` must be modified.

6. Existing tests must be modified, deleted, weakened, or bypassed.

7. A required implementation change falls outside `ALLOWED CHANGES`.

8. Architecture v2 or an ADR must change.

9. Implementation requires `ModelInput`, `RawInference`, `Detection`,
   `InferenceResult`, `Preprocessor`, `InferenceEngine`, `Postprocessor`,
   `InspectionLogic`, `InspectionEvent`, `InspectionPipeline`,
   `EventPublisher`, `MqttPublisher`, or another deferred contract.

10. A broader/public error model must be designed.

11. Quality gates can pass only through suppression, exclusion, or
    configuration weakening.

12. Hardware-dependent tests become necessary.

13. The implementation begins evolving into a general camera framework,
    simulation framework, or speculative abstraction hierarchy.

14. The implementation requires modifying `src/vision_iot/__init__.py`.

15. Validation generates an unintended artifact that cannot safely be removed
    without an out-of-scope change.

Use the existing ADS escalation mechanisms:

```text
TASK_BLOCKED
ARCHITECTURE_DECISION_REQUIRED
HUMAN_DECISION_REQUIRED
RETRY_EXHAUSTED
```

Do not silently expand scope.

---

## DELIVERABLES

Expected implementation deliverables:

```text
src/vision_iot/hardware/__init__.py
src/vision_iot/hardware/camera.py
tests/test_acquisition.py
```

Expected architectural result:

```text
future application / pipeline
            |
            v
       FrameSource
            |
      project boundary
       /           \
      /             \
FakeFrameSource   future camera adapter
   TASK-008           DEFERRED
```

TASK-008 establishes the first real Architecture-v2 behavioral boundary.

It does not implement hardware acquisition itself.

---

## IMPLEMENTATION REPORT

The Implementation Agent must return a report containing exactly:

### STATUS

`COMPLETED` or the appropriate ADS escalation status.

### FILES CHANGED

Every changed/created file.

### IMPLEMENTATION SUMMARY

Concise description of how the authorized acquisition boundary was
materialized.

Explicitly identify:

- the concrete Python representation used for `Frame`;
- the representation used for `Frame.image`;
- why that image representation is already justified by authoritative
  architecture / existing dependency baseline;
- the mechanism used to represent `FrameSource`;
- the behavior of `FakeFrameSource`.

### TESTS ADDED/UPDATED

List new tests and confirm existing tests were not modified.

### VALIDATION RESULTS

Actual evidence for every deterministic validation command.

Include both the initial and final:

```text
git status --short
```

The final status must explicitly confirm whether validation generated any
unexpected artifacts.

### DEVIATIONS

Any deviation encountered during implementation or validation.

Do not report `None` if a process deviation actually occurred and was later
corrected.

### BLOCKERS

Any unresolved blocker/escalation condition.

If none:

```text
None.
```
