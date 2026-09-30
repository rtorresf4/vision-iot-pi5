# TASK-014 — M3.C Baseline ONNX InferenceEngine

## Status

READY_FOR_IMPLEMENTATION

## Milestone

M3 — Vision Pipeline  
M3.C — Baseline ONNX InferenceEngine

## Objective

Implement the first concrete Architecture-v2 `InferenceEngine` using ONNX Runtime.

The task establishes the bounded runtime path:

```text
ModelInput
    |
    v
ONNXInferenceEngine
    |
    v
RawInference
```

The implementation must prove that the existing generic inference boundary can execute a real local ONNX model while keeping ONNX Runtime-specific structures isolated behind the project-owned `InferenceEngine` contract.

M3.C begins at `ModelInput` and ends at `RawInference`.

It does not interpret model outputs.

---

## Architectural Basis

This task materializes the post-M3.B architecture decision for M3.C.

Authoritative architecture decisions:

- `InferenceEngine` remains the existing synchronous project-owned inference boundary.
- `ONNXInferenceEngine` is the first concrete `InferenceEngine`.
- ONNX Runtime is the baseline runtime.
- The engine consumes the existing `ModelInput`.
- The engine returns the existing `RawInference`.
- The engine receives an existing local ONNX model artifact explicitly.
- The engine owns one ONNX Runtime inference session.
- The session is created during engine initialization and reused across `infer()` calls.
- The baseline supports exactly one model input.
- The runtime input name is obtained from ONNX session/model metadata.
- ONNX-specific input information must not be added to `ModelInput`.
- `ModelInput.data` is passed as the numerical model input.
- `SpatialMetadata` is not an ONNX execution concern.
- Runtime outputs must be adapted into the existing ordered `tuple[np.ndarray, ...]` representation before crossing the engine boundary.
- Runtime/model output semantics remain opaque.
- `RawInference.inference_time_ms` measures synchronous model execution duration only.
- Model/session initialization is excluded from `inference_time_ms`.
- `CPUExecutionProvider` is the baseline execution provider.
- Postprocessing and YOLO output interpretation remain deferred.

ADR-003 is the primary architectural owner of the runtime decisions introduced by M3.C.

ADR-010 already owns the established inference-stage timing semantics and must remain unchanged unless an architecture escalation explicitly authorizes otherwise.

---

## Required Architecture Documentation Change

Update:

```text
docs/adr/003-inference-runtime.md
```

with the minimum clarification necessary to make the following M3.C decisions authoritative:

- ONNX Runtime provides the first concrete `InferenceEngine` implementation.
- The engine receives an existing local ONNX artifact.
- The engine creates, owns, and reuses one ONNX Runtime session.
- The baseline supports exactly one model input.
- The runtime input name is obtained from session/model metadata rather than becoming part of `ModelInput`.
- Runtime outputs are adapted into the existing ordered `tuple[np.ndarray, ...]` `RawInference.outputs` representation.
- `CPUExecutionProvider` is the baseline execution provider.
- Runtime/model-specific output interpretation is excluded from the engine.

Do not add model-specific parsing to ADR-003.

Do not modify ADR-010, ADR-004, or ADR-002.

---

## Concrete Implementation

Implement a concrete class conceptually named:

```text
ONNXInferenceEngine
```

inside:

```text
src/vision_iot/vision/inference_onnx.py
```

It must implement the existing:

```text
InferenceEngine
```

contract.

The expected public usage is conceptually:

```python
engine = ONNXInferenceEngine(model_path=...)
raw_inference = engine.infer(model_input)
```

Do not introduce a generalized runtime framework.

---

## Model Artifact Responsibility

`ONNXInferenceEngine` receives an existing local ONNX model artifact.

Its responsibility begins with:

```text
existing local ONNX artifact
```

and includes only the minimum lifecycle required to create and use an ONNX Runtime session.

The engine must not:

- download models;
- access the network;
- discover models remotely;
- automatically choose model versions;
- search arbitrary model directories;
- export models;
- depend on Ultralytics for model acquisition;
- manage training artifacts;
- introduce a model registry;
- introduce a model repository abstraction.

---

## Session Lifecycle

The required lifecycle is:

```text
construct engine
    |
    v
load supplied local ONNX artifact
    |
    v
create ONNX Runtime session
    |
    v
reuse session across infer() calls
```

Session creation must occur during engine initialization.

The model/session must not be reloaded for every inference call.

Session initialization must not be included in `RawInference.inference_time_ms`.

No hot reload, model swapping, automatic reload, model cache, rollback, remote storage, or session-management subsystem is required.

---

## ONNX Input Binding

M3.C supports exactly one ONNX model input.

The engine may inspect session metadata to obtain its input name.

Conceptually:

```python
input_name = session.get_inputs()[0].name
```

The input name must not be added to:

- `ModelInput`;
- `SpatialMetadata`;
- any new generic Architecture-v2 contract.

`ModelInput.data` must be supplied as the numerical ONNX model input.

If the loaded model exposes an input structure incompatible with the single-input baseline, the implementation must fail clearly rather than guess bindings.

---

## Preprocessing Boundary

`ONNXInferenceEngine` must not reproduce preprocessing.

It must not perform:

- resize;
- letterbox;
- BGR-to-RGB conversion;
- normalization;
- HWC-to-CHW conversion;
- batch creation.

Those responsibilities belong to `YoloPreprocessor`.

The strict boundary remains:

```text
YoloPreprocessor
    |
    v
ModelInput
    |
    v
ONNXInferenceEngine
```

The engine must not require `SpatialMetadata` to execute inference.

---

## RawInference Boundary

The existing contract remains unchanged:

```text
RawInference
    outputs: tuple[np.ndarray, ...]
    inference_time_ms: float
```

Runtime outputs must be converted into:

```text
tuple[np.ndarray, ...]
```

before crossing the `InferenceEngine` boundary.

Output ordering must preserve the ordering returned/requested from the runtime/model interface.

M3.C must not establish:

- expected output count;
- expected output tensor shapes;
- expected output dtype;
- output names as generic contracts;
- YOLO output layout;
- detection semantics;
- confidence semantics;
- class semantics;
- bounding-box semantics.

ONNX Runtime-specific output structures must not cross the engine boundary.

---

## Timing

`RawInference.inference_time_ms` must measure synchronous ONNX model execution.

The timed region must correspond to the model execution operation, conceptually:

```text
start monotonic high-resolution timer
session.run(...)
stop timer
```

Use an appropriate standard-library monotonic high-resolution duration clock.

`time.perf_counter()` is acceptable.

Convert the resulting duration to milliseconds.

The measurement must not include:

- engine construction;
- model discovery;
- model loading;
- ONNX session creation;
- preprocessing;
- postprocessing;
- inspection logic;
- MQTT publication.

Do not introduce benchmarking infrastructure.

---

## Execution Provider

The M3.C baseline execution provider is:

```text
CPUExecutionProvider
```

Do not introduce:

- CUDA provider configuration;
- TensorRT;
- OpenVINO;
- accelerator discovery;
- provider auto-selection;
- provider registries;
- generalized provider configuration APIs.

Production runtime/provider selection remains benchmark-driven.

---

## Error Boundary

Model/session initialization failures must fail clearly.

Do not introduce a generalized inference/runtime exception hierarchy.

Do not invent project-owned exception families such as:

```text
ModelLoadError
SessionError
RuntimeProviderError
TensorError
InferenceExecutionError
```

without architecture approval.

Ordinary clear runtime exception propagation is acceptable within the existing architecture.

---

## Deterministic ONNX Test Fixture

Automated M3.C tests must exercise the real ONNX Runtime boundary using a tiny deterministic ONNX model fixture.

Authorized fixture location:

```text
tests/fixtures/tiny_single_input.onnx
```

The fixture exists solely to validate:

```text
ModelInput
    -> ONNXInferenceEngine
    -> RawInference
```

The fixture must:

- be as small as practical;
- expose exactly one numerical input;
- perform a trivial deterministic numerical operation;
- expose numerical output;
- require no external data;
- execute quickly using `CPUExecutionProvider`;
- have predictable output values;
- contain no YOLO-specific output semantics.

The fixture must not:

- be a production YOLO model;
- contain production weights;
- require downloading;
- require internet access;
- require training;
- require camera hardware;
- require Raspberry Pi hardware.

Do not add `onnx` or another production/development dependency solely to generate the test fixture.

If the fixture cannot be produced or used deterministically without an additional dependency or unauthorized repository change:

```text
ARCHITECTURE_DECISION_REQUIRED
```

Do not silently add the dependency.

---

## Testing Requirements

Add deterministic tests in:

```text
tests/test_inference_onnx.py
```

At minimum, tests must provide evidence that:

1. `ONNXInferenceEngine` satisfies the existing `InferenceEngine` boundary.
2. A valid local ONNX artifact initializes the engine.
3. The engine uses `CPUExecutionProvider`.
4. The session is created during initialization.
5. The session is reused across multiple inference calls.
6. `ModelInput.data` is supplied to the ONNX model.
7. Inference executes synchronously.
8. A runtime output is returned as `tuple[np.ndarray, ...]`.
9. Output ordering is preserved where the test seam covers multiple outputs.
10. Returned numerical values match the deterministic fixture.
11. `RawInference.inference_time_ms` is populated.
12. `inference_time_ms` is non-negative.
13. Session/model initialization is outside the measured inference operation.
14. Invalid model/session initialization fails clearly.
15. An incompatible multiple-input model/session structure fails clearly where practical.
16. No preprocessing is repeated by the engine.
17. No output interpretation is performed.
18. Tests require no physical camera.
19. Tests require no Raspberry Pi.
20. Tests require no internet access.
21. Tests require no production YOLO weights.

At least one deterministic test must exercise the real ONNX Runtime boundary.

Pure mocks alone are insufficient.

Small test doubles or pytest facilities may additionally be used for lifecycle, call-count, failure-path, or timing-boundary tests.

Do not add a mocking-framework dependency.

---

## Dependencies

`onnxruntime` is already declared in the integrated repository runtime and CI requirements.

No dependency-file modification is authorized by TASK-014.

In particular, do not modify:

```text
requirements.txt
requirements-ci.txt
requirements-dev.txt
requirements-train.txt
pyproject.toml
```

Do not add:

```text
onnx
ultralytics
ncnn
tensorflow
torch
```

or any other dependency.

If an additional dependency becomes genuinely necessary:

```text
ARCHITECTURE_DECISION_REQUIRED
```

---

## ALLOWED CHANGES

Only the following paths may be created or modified:

```text
.agent/tasks/TASK-014.md
docs/adr/003-inference-runtime.md
src/vision_iot/vision/inference_onnx.py
src/vision_iot/vision/__init__.py
tests/test_inference_onnx.py
tests/fixtures/tiny_single_input.onnx
```

No other repository path may be modified without escalation and explicit authorization.

---

## Protected Artifacts

The following are explicitly protected during TASK-014:

```text
docs/architecture.md
docs/project-context.md

docs/adr/002-model-strategy.md
docs/adr/004-vision-contracts.md
docs/adr/010-benchmarking-strategy.md

src/vision_iot/vision/contracts.py
src/vision_iot/vision/preprocessing.py
src/vision_iot/hardware/

tests/test_vision_contracts.py
tests/test_preprocessing.py

requirements.txt
requirements-ci.txt
requirements-dev.txt
requirements-train.txt
pyproject.toml

Makefile
.github/workflows/
.pre-commit-config.yaml

apps/
training/
deploy/
models/
data/

.agent/rules/
.agent/tasks/TASK-001.md
.agent/tasks/TASK-002.md
.agent/tasks/TASK-003.md
.agent/tasks/TASK-004.md
.agent/tasks/TASK-005.md
.agent/tasks/TASK-006.md
.agent/tasks/TASK-007.md
.agent/tasks/TASK-008.md
.agent/tasks/TASK-009.md
.agent/tasks/TASK-010.md
.agent/tasks/TASK-011.md
.agent/tasks/TASK-012.md
.agent/tasks/TASK-013.md
```

Existing tests must not be weakened, removed, or rewritten to accommodate the new implementation.

---

## Explicit Non-Goals

TASK-014 must not introduce:

- changes to `ModelInput`;
- changes to `InferenceEngine`;
- changes to `RawInference`;
- changes to `SpatialMetadata`;
- preprocessing changes;
- model export;
- model download;
- model discovery;
- model registry;
- model manager;
- model repository abstraction;
- model loader abstraction;
- runtime factory;
- runtime registry;
- engine registry;
- provider registry;
- session manager;
- generalized ML runtime framework;
- multiple-input generic model support;
- ONNX-specific fields in generic contracts;
- Postprocessor;
- Detection;
- InferenceResult;
- YOLO output parsing;
- confidence filtering;
- NMS;
- bounding-box decoding;
- coordinate restoration;
- class mapping;
- application orchestration;
- MQTT integration;
- dashboard integration;
- dataset changes;
- training changes;
- deployment changes;
- Raspberry Pi-specific behavior;
- camera behavior;
- legacy application migration;
- benchmarking infrastructure;
- accelerator support.

---

## Legacy Boundary

Existing inference code under:

```text
apps/pi_detector/
```

may be inspected as evidence only.

It must not automatically define M3.C behavior.

Do not migrate legacy:

- preprocessing;
- YOLO parsing;
- output assumptions;
- orchestration.

No legacy application file may be modified by TASK-014.

---

## Blocking / Escalation Conditions

STOP implementation and escalate if any of the following becomes necessary:

1. `ModelInput` must change.
2. `InferenceEngine` must change.
3. `RawInference` must change.
4. `SpatialMetadata` must change.
5. The reference/baseline model requires multiple ONNX inputs.
6. Runtime outputs cannot be represented by the existing `tuple[np.ndarray, ...]`.
7. ONNX-specific information must be added to `ModelInput`.
8. YOLO output parsing becomes necessary for runtime execution.
9. `Postprocessor`, `Detection`, or `InferenceResult` becomes necessary.
10. A generalized runtime registry/factory/framework becomes necessary.
11. Any new dependency is required.
12. Deterministic testing requires a large or production model artifact.
13. Tests require network access.
14. Tests require Raspberry Pi hardware.
15. Tests require camera hardware.
16. Existing contracts require runtime-specific modification.
17. Quality gates require broad suppression or weakening.
18. Global typing policy must change.
19. Model/session lifecycle requires architecture beyond one engine-owned reusable session.
20. An allowed-change boundary must be exceeded.

Use the existing ADS escalation mechanisms.

Do not silently expand scope.

---

## Acceptance Criteria

TASK-014 is complete only when:

1. `ONNXInferenceEngine` exists.
2. It implements the existing `InferenceEngine`.
3. It consumes existing `ModelInput`.
4. It returns existing `RawInference`.
5. It loads an explicitly supplied existing local ONNX artifact.
6. It creates and owns an ONNX Runtime session.
7. The session is reused across inference calls.
8. Exactly one model input is supported.
9. The runtime input name is obtained from runtime/model metadata.
10. No ONNX-specific input information is added to `ModelInput`.
11. `ModelInput.data` is passed to ONNX Runtime without repeating preprocessing.
12. Inference executes synchronously.
13. Runtime outputs become ordered `tuple[np.ndarray, ...]`.
14. ONNX Runtime-specific structures do not cross the engine boundary.
15. `inference_time_ms` measures synchronous model execution duration.
16. Model/session initialization is excluded from `inference_time_ms`.
17. `CPUExecutionProvider` is used as the baseline provider.
18. At least one deterministic test exercises the real ONNX Runtime boundary.
19. Normal tests require no production YOLO model.
20. Normal tests require no network access.
21. Normal tests require no physical camera.
22. Normal tests require no Raspberry Pi.
23. No preprocessing behavior is duplicated.
24. No postprocessing behavior is introduced.
25. No YOLO output semantics are introduced.
26. No `Detection` contract is introduced.
27. No `InferenceResult` contract is introduced.
28. No NMS/confidence/class/bbox interpretation is introduced.
29. No generalized runtime/model-management framework is introduced.
30. Existing generic contracts remain unchanged.
31. Existing M3.B tests remain unchanged and passing.
32. ADR-003 reflects the accepted M3.C runtime decisions.
33. No unauthorized dependency changes are introduced.
34. All required quality gates pass.

---

## Required Validation

Run and provide evidence for:

```bash
pytest -q tests/test_inference_onnx.py
black --check .
ruff check .
mypy apps src
pytest -q
make lint
make test
pre-commit run --all-files
git diff --check
```

After validation, inspect repository state because validation and pre-commit hooks may modify files:

```bash
git status --short
git diff --stat
git diff --check
```

Only TASK-014 authorized paths may remain modified or untracked.

---

## Review Requirements

After implementation and deterministic validation:

1. Run an independent Review Agent.
2. Reviewer must inspect the TASK contract, ADR-003, implementation, tests, fixture, and repository diff.
3. Reviewer must verify scope compliance and protected artifacts.
4. Reviewer must verify that at least one test crosses the real ONNX Runtime boundary.
5. Reviewer must verify that runtime-specific objects do not escape through `RawInference`.
6. Reviewer must verify that preprocessing and output interpretation have not leaked into the engine.
7. Reviewer must use the ADS verdict vocabulary:

```text
PASS
CHANGES_REQUESTED
BLOCKED
```

Finding severity must use:

```text
BLOCKER
MUST_FIX
SUGGESTION
```

A `PASS` review does not replace the Human Gate.

---

## Human Gate

Integration requires explicit human approval after:

- implementation;
- deterministic validation;
- independent review;
- correction loop if required.

Do not merge automatically.

---

## Post-Task Boundary

Successful TASK-014 integration establishes:

```text
Frame
    |
    v
YoloPreprocessor
    |
    v
ModelInput
    |
    v
ONNXInferenceEngine
    |
    v
RawInference
```

TASK-014 does not authorize the next postprocessing increment.

After integration, return to Architecture for authoritative post-M3.C assessment before materializing any M3.D task.
