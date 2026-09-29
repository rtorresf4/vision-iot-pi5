# TASK-012 — Vision Contract Foundation

## STATUS

READY

## MILESTONE

M3 — Vision Pipeline

## OBJECTIVE

Establish the first stable Architecture-v2 vision-processing contracts between the completed M2 acquisition boundary and future concrete inference-runtime implementations.

Materialize the project-owned contract-level processing chain:

    Frame
      |
      v
    Preprocessor
      |
      v
    ModelInput
      |
      +-- data: np.ndarray
      |
      +-- metadata: SpatialMetadata
      |
      v
    InferenceEngine
      |
      v
    RawInference
      |
      +-- outputs: tuple[np.ndarray, ...]
      |
      +-- inference_time_ms: float

This task establishes contracts only. It must not introduce production preprocessing, concrete inference runtimes, model-specific processing, or postprocessing.

## WHY

M2 — Acquisition is architecturally complete and provides the stable project-owned `Frame` input boundary.

Before introducing ONNX Runtime, NCNN, or any concrete model execution technology, Architecture v2 requires stable project-owned boundaries around preprocessing and inference execution.

This follows the established Architecture-v2 pattern:

    stable contract first
            |
            v
    concrete implementation later

For acquisition:

    FrameSource
        |
        v
    OpenCVFrameSource

For inference:

    InferenceEngine
        |
        v
    future concrete runtime adapter

The purpose of this increment is therefore to establish replaceable, model-independent and runtime-independent contracts without prematurely stabilizing concrete preprocessing, tensor-layout, model-output, or runtime-specific semantics.

During the initial TASK-012 implementation attempt, the Implementation Agent selected flexible `Any` and dictionary representations for `ModelInput` and `RawInference`.

Project Context review determined that those representations were not authorized by the then-current architecture and raised `ARCHITECTURE_DECISION_REQUIRED`.

Architecture subsequently resolved the representation decision.

The accepted M3.A contracts are now:

    ModelInput
        data: np.ndarray
        metadata: SpatialMetadata

    SpatialMetadata
        original_width: int
        original_height: int
        input_width: int
        input_height: int
        scale_x: float
        scale_y: float
        pad_x: float
        pad_y: float

    RawInference
        outputs: tuple[np.ndarray, ...]
        inference_time_ms: float

The previous `Any` / dictionary implementation is not accepted and must be corrected.

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/002-model-strategy.md`
- `docs/adr/003-inference-runtime.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/007-execution-model.md`
- `docs/adr/009-testing-strategy.md`
- `docs/adr/010-benchmarking-strategy.md`
- `docs/adr/012-target-repository-structure.md`
- `docs/project-context.md`
- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- completed acquisition TASK contracts

Architecture has explicitly resolved the M3.A representation decision required by this TASK.

The following architecture-governed documentation clarifications are authorized as part of TASK-012:

- `docs/adr/004-vision-contracts.md` MUST be updated to materialize the accepted `ModelInput`, `SpatialMetadata`, and `RawInference` representations and their intentionally deferred semantics.
- `docs/adr/003-inference-runtime.md` MAY receive only the minimal clarification required to establish that runtime-native output structures do not cross the project-owned `InferenceEngine` boundary and are adapted to `tuple[np.ndarray, ...]`.
- `docs/adr/010-benchmarking-strategy.md` MAY receive only the minimal clarification required to establish the semantics of `RawInference.inference_time_ms` as inference-stage elapsed duration in milliseconds.

No other architecture change is authorized.

These ADR modifications are a human/Architecture-authorized exception to the normal Implementation Agent restriction on architecture artifacts.

The Implementation Agent must not redesign, expand, or reinterpret these ADRs beyond the decisions explicitly described by this TASK.

If implementation requires any additional public-contract decision not established here or in the authoritative architecture artifacts, the agent must stop and escalate rather than invent one.

## SCOPE

The Implementation Agent must:

1. Create the real Architecture-v2 `vision` package under `src/vision_iot/`.

2. Materialize the project-owned `SpatialMetadata` contract.

3. Materialize the project-owned `ModelInput` contract using:

       data: np.ndarray
       metadata: SpatialMetadata

4. Materialize the project-owned `RawInference` contract using:

       outputs: tuple[np.ndarray, ...]
       inference_time_ms: float

5. Materialize the minimal synchronous `Preprocessor` abstraction representing:

       Frame -> ModelInput

6. Materialize the minimal synchronous `InferenceEngine` abstraction representing:

       ModelInput -> RawInference

7. Consume the existing M2 `Frame` contract without modifying it.

8. Preserve the existing `FrameSource`, `FakeFrameSource`, `OpenCVFrameSource`, and `CameraError` acquisition contracts unchanged.

9. Add only minimal deterministic fake/test implementations if they are necessary to demonstrate substitutability and composition.

10. Add focused contract tests demonstrating the deterministic chain:

       Frame
         |
         v
       Preprocessor
         |
         v
       ModelInput
         |
         v
       InferenceEngine
         |
         v
       RawInference

11. Keep all tests independent from physical hardware, model artifacts, inference runtimes, network access, MQTT, dashboards, and training datasets.

12. Preserve the existing blocking quality gate.

13. Keep all abstractions synchronous in accordance with ADR-007.

14. Keep `ModelInput` independent from any specific model or inference runtime.

15. Keep `RawInference` independent from model-specific postprocessing and domain inspection semantics.

16. Materialize only the architecture-governed ADR clarifications explicitly authorized by this TASK.

17. Inspect existing legacy inference code only if useful as evidence. Legacy implementation must not define the new stable Architecture-v2 contracts by default.

## OUT OF SCOPE

The Implementation Agent must NOT implement or introduce:

- ONNX Runtime adapter;
- NCNN adapter;
- TensorFlow/TFLite runtime;
- Ultralytics runtime;
- YOLO model loading;
- YOLO26n integration;
- YOLOv8 migration;
- real model execution;
- production preprocessing;
- resize implementation;
- letterbox implementation;
- normalization implementation;
- universal RGB/BGR policy;
- universal dtype/value-range policy;
- universal tensor-layout policy;
- batch semantics;
- exact model input dimensions;
- universal channel count;
- quantization policy;
- model-specific tensor names;
- model-specific output count;
- model-specific output shapes;
- model-specific output dtype;
- model-specific output names;
- model-specific output parsing;
- confidence filtering;
- NMS;
- `Postprocessor`;
- `Detection`;
- `InferenceResult`;
- `InspectionLogic`;
- `InspectionEvent`;
- `InspectionPipeline`;
- `EventPublisher`;
- MQTT changes;
- dashboard changes;
- camera changes;
- `Frame` changes;
- `FrameSource` changes;
- Raspberry Pi deployment;
- benchmarking implementation;
- training;
- dataset changes;
- concurrency;
- asyncio;
- threads;
- queues;
- background inference workers;
- batching infrastructure;
- runtime registries;
- plugin systems;
- generic ML frameworks;
- dependency-injection frameworks;
- speculative abstraction hierarchies;
- additional empty Architecture-v2 packages;
- additional `SpatialMetadata` fields;
- additional `RawInference` timing fields;
- generic metadata bags;
- generic telemetry containers.

Do not create:

- `application/`;
- `domain/`;
- `infrastructure/`;
- `config/`;

as part of this TASK.

Do not migrate or modify legacy inference implementation under `apps/pi_detector/`.

Future M3.B and M3.C work is explicitly not committed implementation scope for this TASK.

## INPUTS / CONTRACTS

Existing authoritative acquisition input:

- `vision_iot.hardware.Frame`

Existing M2 contracts must remain unchanged:

- `Frame`
- `FrameSource`
- `FakeFrameSource`
- `OpenCVFrameSource`
- `CameraError`

New contracts authorized to materialize:

- `SpatialMetadata`
- `ModelInput`
- `RawInference`
- `Preprocessor`
- `InferenceEngine`

### SpatialMetadata

Project-owned typed contract containing only reversible spatial-transformation information.

Its stable representation is:

    SpatialMetadata
        original_width: int
        original_height: int
        input_width: int
        input_height: int
        scale_x: float
        scale_y: float
        pad_x: float
        pad_y: float

Field semantics:

- `original_width` and `original_height` represent the spatial dimensions of the source `Frame` before preprocessing.
- `input_width` and `input_height` represent the spatial dimensions of the representation produced for model input.
- `scale_x` and `scale_y` represent spatial scaling from original-frame coordinates toward model-input coordinates.
- `pad_x` and `pad_y` represent spatial padding offsets introduced by preprocessing in model-input coordinates.

`SpatialMetadata` exists only to preserve enough spatial transformation information for future postprocessing to map model-space results back into original-frame coordinates.

It must NOT contain:

- RGB/BGR information;
- dtype;
- normalization parameters;
- tensor names;
- model names;
- runtime names;
- YOLO-specific metadata;
- ONNX-specific metadata;
- NCNN-specific metadata;
- confidence thresholds;
- class labels;
- NMS configuration;
- domain inspection information.

It must not become a generic metadata bag.

### ModelInput

Represents the output of preprocessing and the input consumed by an inference engine.

Its stable Architecture-v2 representation is:

    ModelInput
        data: np.ndarray
        metadata: SpatialMetadata

`ModelInput.data` uses NumPy `ndarray` as the project-owned numerical interchange representation.

`Frame.image` and `ModelInput.data` are separate contracts:

    Frame.image
        acquired raster representation

    ModelInput.data
        prepared numerical model input

The `Preprocessor` owns the transformation between them.

This TASK must NOT establish universal semantics for:

- RGB vs BGR;
- dtype;
- value range;
- normalization;
- NCHW vs NHWC;
- batch semantics;
- exact model input dimensions;
- channel count;
- memory contiguity;
- quantization;
- model-specific tensor semantics.

Tests must not accidentally stabilize any of those deferred properties.

### RawInference

Represents output produced directly by an inference runtime before model-specific postprocessing.

Its stable Architecture-v2 representation is:

    RawInference
        outputs: tuple[np.ndarray, ...]
        inference_time_ms: float

`outputs` is an ordered tuple containing one or more raw numerical runtime outputs represented as NumPy `ndarray` values.

The stable contract does NOT define:

- exact output count;
- output tensor shape;
- output dtype;
- output names;
- YOLO output layout;
- detection parsing;
- confidence semantics;
- class semantics;
- bounding-box semantics;
- NMS semantics.

Concrete future `InferenceEngine` adapters are responsible for converting runtime-native output structures into:

    tuple[np.ndarray, ...]

before crossing the project-owned inference boundary.

Runtime-native ONNX, NCNN, Ultralytics, or other framework structures must not become the public Architecture-v2 `RawInference.outputs` contract.

`inference_time_ms` represents the elapsed inference-engine execution duration in milliseconds for the operation that produced the associated outputs.

It is a duration, not a wall-clock timestamp.

`RawInference` must remain independent from domain inspection semantics.

It must NOT contain:

- OK/DAMAGED decisions;
- `InspectionEvent`;
- MQTT information;
- dashboard information;
- final `Detection` objects;
- final `InferenceResult`;
- package-damage business decisions;
- preprocessing timing;
- capture timing;
- postprocessing timing;
- inspection timing;
- publish timing;
- end-to-end timing.

### Preprocessor

Project-owned synchronous abstraction:

    Frame -> ModelInput

This TASK authorizes the abstraction only.

No production preprocessing behavior is authorized.

### InferenceEngine

Project-owned synchronous abstraction:

    ModelInput -> RawInference

Consumers must depend on this project-owned boundary rather than concrete runtime APIs.

No concrete inference runtime is authorized.

## EXPECTED OUTPUT

Conceptually:

    src/
    └── vision_iot/
        ├── hardware/
        │   └── ...                 # unchanged
        │
        └── vision/
            ├── __init__.py
            └── <minimal contract implementation file(s)>

    tests/
        └── <focused M3 vision-contract test file>

The exact internal filename organization inside `vision_iot/vision/` may be chosen only to the minimum extent necessary to materialize the authorized contracts.

Do not create empty speculative modules or packages.

Expected project-owned contracts:

    SpatialMetadata
    ModelInput
    RawInference
    Preprocessor
    InferenceEngine

Minimal deterministic test doubles may exist only if required to prove contract substitutability and composition.

## ALLOWED CHANGES

The Implementation Agent may create or modify only:

- `.agent/tasks/TASK-012.md` — human-controlled TASK contract; the Implementation Agent must not modify it.
- `docs/adr/003-inference-runtime.md` — architecture-governed minimal clarification only as explicitly authorized by this TASK.
- `docs/adr/004-vision-contracts.md` — architecture-governed M3.A contract representation update explicitly required by this TASK.
- `docs/adr/010-benchmarking-strategy.md` — architecture-governed minimal timing clarification only as explicitly authorized by this TASK.
- `src/vision_iot/vision/__init__.py`
- minimal Python implementation file(s) directly under `src/vision_iot/vision/` required to materialize the five authorized contracts;
- one focused M3 contract test file under `tests/`.

The architecture documentation changes listed above were human-authorized before implementation resumed. The Implementation Agent must inspect and preserve them, and must not expand them beyond the authorized decision.

The Implementation Agent must determine the exact new Python filenames before modification and report them.

No existing source file outside `src/vision_iot/vision/` may be modified.

No existing test file may be modified.

Any need to change an existing file outside these areas requires escalation before modification.

## FORBIDDEN CHANGES

Do not modify:

- `src/vision_iot/hardware/`;
- `apps/`;
- `docs/architecture.md`;
- any `docs/adr/` file other than ADR-003, ADR-004, and ADR-010 as explicitly authorized above;
- `docs/project-context.md`;
- `GEMINI.md`;
- `.agent/rules/`;
- completed TASK contracts;
- `pyproject.toml`;
- `requirements.txt`;
- `requirements-ci.txt`;
- `requirements-dev.txt`;
- `Makefile`;
- `.github/`;
- `.pre-commit-config.yaml`;
- deployment files;
- training files;
- model artifacts;
- dataset files;
- MQTT implementation;
- dashboard implementation.

Do not weaken, suppress, bypass, or reconfigure existing quality gates.

## ACCEPTANCE CRITERIA

1. M2 acquisition contracts remain unchanged.
2. A real Architecture-v2 `vision` package exists because it contains actual M3 contracts.
3. `SpatialMetadata` exists as a project-owned typed contract.
4. `SpatialMetadata` contains exactly the eight authorized spatial fields.
5. `ModelInput` exists as a project-owned contract.
6. `ModelInput.data` uses NumPy `ndarray`.
7. `ModelInput.metadata` uses `SpatialMetadata`.
8. `RawInference` exists as a project-owned contract.
9. `RawInference.outputs` uses `tuple[np.ndarray, ...]`.
10. `RawInference.inference_time_ms` uses `float`.
11. `RawInference.inference_time_ms` represents inference-stage elapsed duration in milliseconds rather than a wall-clock timestamp.
12. `Preprocessor` exists as a project-owned synchronous abstraction.
13. `InferenceEngine` exists as a project-owned synchronous abstraction.
14. `Preprocessor` accepts the existing `Frame` boundary.
15. `Preprocessor` produces `ModelInput`.
16. `InferenceEngine` consumes `ModelInput`.
17. `InferenceEngine` produces `RawInference`.
18. `ModelInput` remains independent from one concrete inference runtime.
19. `RawInference` remains independent from domain inspection semantics.
20. Runtime-native output structures do not cross the project-owned `InferenceEngine` boundary.
21. No ONNX-specific object becomes the stable `RawInference` contract.
22. No NCNN-specific object becomes the stable `RawInference` contract.
23. No YOLO-specific object becomes the stable `ModelInput` or `RawInference` contract.
24. No universal RGB/BGR policy is introduced.
25. No universal dtype/value-range policy is introduced.
26. No universal tensor-layout policy is introduced.
27. No exact model input dimensions are introduced.
28. No universal output count, shape, dtype, names, or model-specific interpretation is introduced.
29. `SpatialMetadata` does not become a generic metadata bag.
30. `RawInference` does not become a generic telemetry container.
31. No additional `SpatialMetadata` fields are introduced.
32. No additional `RawInference` timing fields are introduced.
33. No `Detection` contract is introduced.
34. No `InferenceResult` contract is introduced.
35. No `Postprocessor` is introduced.
36. No real model execution occurs.
37. No production preprocessing behavior is introduced.
38. No legacy inference code is migrated or modified.
39. Tests demonstrate the contract-level processing chain without a model.
40. Tests require no physical hardware.
41. Tests require no model artifact.
42. Tests require no network access.
43. No new dependency is added.
44. No concurrency is introduced.
45. No additional Architecture-v2 layers are created speculatively.
46. ADR-004 records the accepted M3.A representation decision.
47. ADR-003 contains only the authorized runtime-boundary clarification if modified.
48. ADR-010 contains only the authorized inference-timing clarification if modified.
49. Black passes.
50. Ruff passes.
51. mypy passes for `apps` and `src`.
52. pytest passes.
53. `make lint` passes.
54. `make test` passes.
55. pre-commit passes.
56. Existing tests remain protected.
57. Final working-tree inspection is clean except for intended TASK changes.
58. All changes remain within the exact ALLOWED CHANGES of this TASK contract.

## REQUIRED TESTS

Add one focused M3 vision-contract test file.

Tests must demonstrate at minimum:

1. `SpatialMetadata` exposes exactly the authorized spatial transformation contract needed by M3.A.

2. `ModelInput.data` is represented using NumPy `ndarray`.

3. `ModelInput.metadata` is represented using `SpatialMetadata`.

4. A minimal deterministic `Preprocessor` implementation/test double can accept an existing `Frame` and return `ModelInput`.

5. `RawInference.outputs` is represented as an ordered tuple of NumPy `ndarray` values.

6. `RawInference.inference_time_ms` represents an inference-stage duration.

7. A minimal deterministic `InferenceEngine` implementation/test double can accept `ModelInput` and return `RawInference`.

8. `RawInference` can represent runtime output without introducing `Detection`, `InferenceResult`, or domain semantics.

9. The complete contract-level chain executes deterministically:

       Frame
         -> Preprocessor
         -> ModelInput
         -> InferenceEngine
         -> RawInference

10. No concrete inference runtime is required.

11. No physical camera or Raspberry Pi is required.

12. No model artifact or download is required.

13. Existing acquisition tests remain passing and unchanged.

Tests may demonstrate both one and multiple ordered raw output arrays if useful.

Tests must NOT establish universal assumptions about:

- RGB/BGR;
- dtype;
- normalization;
- value range;
- tensor layout;
- batch semantics;
- exact tensor dimensions;
- exact output count;
- output shapes;
- output dtype;
- output names;
- YOLO semantics;
- runtime-specific structures.

Tests must not require arbitrary values such as 640x640 to be universal Architecture-v2 invariants.

## VALIDATION COMMANDS

The Implementation Agent must run the following deterministic validation.

Initial scope inspection:

    git status --short
    git diff --check

Focused M3 contract tests:

    pytest -q <focused-M3-contract-test-file>

Blocking quality gates:

    black --check .
    ruff check .
    mypy apps src
    pytest -q

Project validation interfaces:

    make lint
    make test

Pre-commit validation:

    pre-commit run --all-files

Final deterministic inspection:

    git diff --check
    git status --short
    git diff --name-only

Because TASK-012 contains untracked files during implementation, final scope inspection must also account for untracked files shown by `git status --short`; `git diff --name-only` alone is not sufficient.

The Implementation Agent must directly inspect the content/diff of every file created or modified by this TASK, including untracked files.

If validation modifies any file, the modified state must be inspected and the relevant validation commands rerun.

No generated artifact may remain unintentionally in the working tree.

## DEPENDENCIES

Prerequisites:

- TASK-007 completed and integrated.
- TASK-008 completed and integrated.
- TASK-009 completed and integrated.
- TASK-010 completed and integrated.
- TASK-011 completed and integrated.
- M2 Architecture assessment completed.
- M2 declared architecturally complete.
- Post-M2 `docs/project-context.md` checkpoint integrated into `main`.
- TASK-012 branch created from the synchronized post-M2 `main`.
- TASK-012 initial implementation attempt exposed unresolved contract representation semantics.
- Architecture decision for M3.A contract representation completed.
- Required human-authorized ADR clarification materialized before implementation resumed.
- TASK-012 contract amended to incorporate the architecture decision.

No new package dependency is expected or authorized.

Use only:

- Python standard mechanisms;
- existing NumPy baseline as explicitly authorized by ADR-004.

Do not add an inference-runtime dependency merely to define `InferenceEngine`.

## BLOCKING CONDITIONS

The previously unresolved representations of:

    ModelInput.data
    ModelInput.metadata
    RawInference.outputs
    RawInference timing

have now been resolved by Architecture and are no longer open implementation decisions.

The Implementation Agent must STOP before making any additional architectural decision and escalate using:

    ARCHITECTURE_DECISION_REQUIRED

if implementation requires defining or introducing any of the following:

1. RGB/BGR ordering.

2. Universal dtype.

3. Universal value range.

4. NCHW/NHWC or another universal tensor-layout policy.

5. Batch semantics.

6. Exact model input dimensions.

7. Normalization policy.

8. Exact output count as a universal invariant.

9. Output names.

10. Output tensor shapes as universal invariants.

11. Model-specific output semantics.

12. YOLO-specific parsing.

13. Runtime-native output structures as public project contracts.

14. Additional metadata beyond the defined eight-field `SpatialMetadata` spatial transformation contract.

15. Additional `RawInference` timing fields.

16. A concrete inference runtime required to validate the contracts.

17. A new dependency.

18. Existing `Frame` or `FrameSource` contracts must change.

19. A concrete production `Preprocessor` implementation becomes necessary.

20. `Detection`, `Postprocessor`, or `InferenceResult` must be introduced to make the increment meaningful.

21. Existing legacy application code must change.

22. Quality gates require suppression or weakening.

23. Implementation begins requiring a generic ML framework, plugin system, runtime registry, or speculative abstraction hierarchy.

24. Any architecture artifact beyond ADR-003, ADR-004, and ADR-010 must change.

25. ADR-003, ADR-004, or ADR-010 would need changes beyond the architecture decision already authorized by this TASK.

Do not silently extend these contracts.

Use:

    TASK_BLOCKED

for non-architectural implementation/environment blockers that prevent execution of the authorized TASK without requiring a new architecture decision.

Use:

    HUMAN_DECISION_REQUIRED

when a decision explicitly belongs to the human Project Context owner rather than Architecture or implementation.

Use:

    RETRY_EXHAUSTED

only according to the bounded correction/retry rules defined by the ADS workflow.

The Implementation Agent must not silently resolve undefined public contract semantics.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file, including the authorized ADR clarifications.

### IMPLEMENTATION SUMMARY

Concise description of what was implemented.

Explicitly confirm the final representations:

    ModelInput:
        data: np.ndarray
        metadata: SpatialMetadata

    SpatialMetadata:
        original_width: int
        original_height: int
        input_width: int
        input_height: int
        scale_x: float
        scale_y: float
        pad_x: float
        pad_y: float

    RawInference:
        outputs: tuple[np.ndarray, ...]
        inference_time_ms: float

Identify the authoritative architecture artifact that justifies each representation.

Confirm that the previously attempted `Any`, `dict[str, Any]`, and `dict[str, float]` representations were removed.

### TESTS ADDED / UPDATED

List all new tests.

Confirm whether any pre-existing test was modified.

### VALIDATION RESULTS

Report every required validation command and its result, including relevant raw output.

### CONTRACT PRESERVATION

Explicitly confirm whether:

- `Frame` remained unchanged;
- `FrameSource` remained unchanged;
- M2 acquisition implementation remained unchanged;
- no concrete inference runtime was introduced;
- no production preprocessing behavior was introduced;
- no deferred model/runtime semantics were silently stabilized;
- `SpatialMetadata` contains no unauthorized generic metadata;
- `RawInference` contains no unauthorized telemetry fields;
- runtime-native structures do not cross the `InferenceEngine` boundary.

### ARCHITECTURE DOCUMENTATION

Explicitly report:

- the final ADR-004 change;
- whether ADR-003 was clarified and how;
- whether ADR-010 was clarified and how;
- confirmation that no other architecture artifact changed.

### DEVIATIONS

Any deviation from this TASK.

### BLOCKERS

Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS

Relevant observations discovered during implementation that were intentionally not implemented.
