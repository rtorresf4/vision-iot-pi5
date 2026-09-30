# TASK-015 — M3.D Postprocessing Boundary

## STATUS

READY

## MILESTONE

M3 — Vision Pipeline  
M3.D — Postprocessing Boundary

## OBJECTIVE

Establish the Architecture-v2 postprocessing boundary and implement the first
concrete YOLO26n reference postprocessor.

The task must transform the authoritative raw YOLO26n ONNX reference output
into stable project-owned computer-vision results without leaking
model-specific, runtime-specific, or domain inspection semantics into the
generic vision contracts.

The completed reference path for this increment is:

    RawInference
        +
    Frame
        +
    SpatialMetadata
        |
        v
    YoloPostprocessor
        |
        v
    InferenceResult
        |
        v
    Detection[]

M3.D ends at `InferenceResult`.

## WHY

M3.A established the generic preprocessing and inference contracts.

M3.B implemented the concrete reference YOLO preprocessing path.

M3.C implemented the baseline ONNX inference engine while intentionally
keeping model-output interpretation outside `InferenceEngine`.

Architecture has now closed the M3.D YOLO26n ONNX output-representation gate.

The selected reference artifact uses:

    YOLO26n -> ONNX -> nms=None

and therefore produces raw one-to-many detection output requiring
project-owned model-specific postprocessing.

M3.D is required to convert that raw model output into stable,
runtime-independent and model-independent project-owned detections before
domain inspection logic is introduced.

## ARCHITECTURE REFERENCES

Authoritative architecture:

- `docs/architecture.md`
- `docs/adr/002-model-strategy.md`
- `docs/adr/003-inference-runtime.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/010-benchmarking-strategy.md`

Primary ownership for this task:

- ADR-004 defines the generic `BoundingBox`, `Detection`,
  `InferenceResult`, and `Postprocessor` contracts.
- ADR-002 defines the concrete YOLO26n ONNX reference-output and
  postprocessing semantics.

No new architecture is introduced by this task.

The Implementation Agent must implement the architecture already established
by the ADRs and must not reinterpret or extend it.

## SCOPE

### 1. Generic postprocessing contracts

Materialize the Architecture-v2 generic contracts in
`src/vision_iot/vision/contracts.py`.

Add:

    BoundingBox
        x1: float
        y1: float
        x2: float
        y2: float

    Detection
        class_id: int
        class_name: str
        confidence: float
        bounding_box: BoundingBox

    InferenceResult
        frame_id: str
        timestamp: float
        detections: tuple[Detection, ...]
        inference_time_ms: float

Add the synchronous generic boundary:

    Postprocessor.process(
        raw_inference: RawInference,
        frame: Frame,
        metadata: SpatialMetadata,
    ) -> InferenceResult

The implementation must preserve the exact ownership and semantics established
by ADR-004.

Existing contracts must remain compatible.

In particular, do not change the representation or semantics of:

- `Frame`
- `ModelInput`
- `SpatialMetadata`
- `RawInference`
- `Preprocessor`
- `InferenceEngine`

### 2. Concrete YoloPostprocessor

Create the first concrete reference postprocessor in:

    src/vision_iot/vision/postprocessing.py

Implement:

    YoloPostprocessor

It must implement the generic `Postprocessor` contract.

The concrete implementation may understand only the authoritative YOLO26n
ONNX reference representation established by ADR-002.

### 3. Reference raw-output validation

The reference postprocessor must validate that the supplied
`RawInference` is structurally compatible with the selected reference
representation.

At minimum:

    len(raw_inference.outputs) == 1

and the output tensor must be structurally compatible with:

    (N, 4 + nc, 8400)

where `nc` is derived from the explicit class mapping supplied to the
postprocessor.

For the current reference path, the concrete implementation may require the
single-item batch produced by the existing reference `YoloPreprocessor`.

It must fail clearly when the supplied raw representation is incompatible.

Do not introduce a generic model-schema validation framework.

### 4. Reference YOLO26n candidate interpretation

Interpret the single reference output tensor using:

    layout:
        (batch, channels, candidates)

    channels:
        4 + nc

    first 4 channels:
        xywh bounding box

    remaining nc channels:
        per-class scores

    candidate count:
        8400

There is no separate objectness channel.

For each candidate:

    class_id = argmax(class_scores)

    confidence = max(class_scores)

Do not apply historical YOLO parsing formulas involving:

    objectness * class_probability

### 5. Confidence filtering

The concrete `YoloPostprocessor` must apply a configurable confidence
threshold.

The threshold is concrete postprocessor configuration.

It must not be added to:

- `RawInference`
- `Detection`
- `InferenceResult`
- `SpatialMetadata`

Do not introduce a generic filtering abstraction.

### 6. Bounding-box conversion

Interpret the raw box representation as:

    xywh

where:

- `x` = center x;
- `y` = center y;
- `w` = box width;
- `h` = box height.

These values are in model-input coordinate space.

Convert retained boxes to model-space:

    x1
    y1
    x2
    y2

before producing the stable project-owned representation.

### 7. Class-aware NMS

Implement deterministic class-aware non-maximum suppression.

The IoU threshold must be configurable on the concrete
`YoloPostprocessor`.

Detections belonging to different predicted classes must not suppress one
another solely because their boxes overlap.

NMS belongs only to the concrete reference postprocessing path.

Do not introduce abstractions such as:

- `NmsEngine`
- `SuppressionStrategy`
- `DetectionFilterPipeline`
- `PostprocessingRegistry`

Do not add Ultralytics, PyTorch, torchvision, or another dependency solely
for NMS.

Use the existing numerical dependency baseline.

For the reference path, NMS should operate in model-input coordinate space
before coordinate restoration.

### 8. Coordinate restoration

Restore retained model-space boxes into original-frame coordinates using the
existing `SpatialMetadata`.

Use the effective transformation recorded by preprocessing:

    original_x = (model_x - pad_x) / scale_x

    original_y = (model_y - pad_y) / scale_y

`SpatialMetadata` is authoritative.

Do not recompute theoretical resize or letterbox geometry.

The resulting `BoundingBox` must use original-frame floating-point `xyxy`
pixel coordinates.

Clip final coordinates to:

    0 <= x1, x2 <= original_width
    0 <= y1, y2 <= original_height

Preserve:

    x1 <= x2
    y1 <= y2

Do not prematurely round coordinates to integers.

### 9. Class mapping

`YoloPostprocessor` must receive an explicit class mapping through minimal
constructor configuration.

The mapping must provide the relationship between zero-based model class IDs
and class names.

The postprocessor must not discover class names through:

- Ultralytics runtime;
- training YAML;
- network access;
- repository scanning;
- model registry.

Do not introduce a configuration subsystem as part of this task.

### 10. InferenceResult construction

The concrete postprocessor must produce:

    InferenceResult(
        frame_id=frame.id,
        timestamp=frame.timestamp,
        detections=...,
        inference_time_ms=raw_inference.inference_time_ms,
    )

`inference_time_ms` must be propagated unchanged.

It remains inference-engine execution time only.

Do not include postprocessing time in this field.

The source `Frame` is used for correlation context.

The postprocessor must not modify or reprocess `Frame.image`.

### 11. Package exports

Update the vision package exports only as required to expose the new
Architecture-v2 contracts and concrete reference postprocessor consistently
with the existing package style.

Do not introduce a new public API structure or registry.

## OUT OF SCOPE

The following are explicitly outside TASK-015:

- `InspectionLogic`;
- OK/DAMAGED decisions;
- defect/business rules;
- `InspectionEvent`;
- MQTT;
- `EventPublisher`;
- dashboard integration;
- orchestration/full application pipeline;
- camera execution;
- Raspberry Pi validation;
- ONNX Runtime execution tests;
- production YOLO26n model execution;
- committing production YOLO26n weights or ONNX artifacts;
- model downloading;
- training;
- fine-tuning;
- dataset work;
- model export workflow;
- NCNN;
- runtime benchmarking;
- runtime/provider selection;
- embedded-NMS export;
- NMS-free YOLO26 output;
- support for multiple YOLO output representations;
- arbitrary batching;
- generic model-schema validation;
- generic NMS abstraction;
- model registry;
- postprocessor registry;
- plugin framework;
- configuration subsystem;
- changes to acquisition;
- changes to preprocessing behavior;
- changes to ONNX inference behavior;
- postprocessing latency instrumentation.

Do not migrate or repair the legacy `apps/pi_detector` path as part of this
task.

Legacy YOLOv8 code is not architectural evidence for TASK-015.

## INPUTS / CONTRACTS

Authoritative existing contracts:

    Frame
        id: str
        timestamp: float
        image: np.ndarray
        width: int
        height: int

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

Authoritative reference YOLO26n ONNX output:

    export mode:
        nms=None

    output count:
        1

    shape:
        (N, nc + 4, 8400)

    layout:
        batch, channels, candidates

    boxes:
        xywh in model-input coordinates

    class representation:
        one score per class per candidate

    objectness:
        no separate objectness channel

    class_id:
        zero-based argmax index of the class-score vector

    confidence:
        selected maximum class score

    confidence filtering:
        YoloPostprocessor

    NMS:
        external, class-aware, owned by YoloPostprocessor

    coordinate restoration:
        YoloPostprocessor using SpatialMetadata

Existing implementation references:

- `src/vision_iot/vision/contracts.py`
- `src/vision_iot/vision/preprocessing.py`
- `src/vision_iot/vision/inference_onnx.py`
- `src/vision_iot/vision/__init__.py`
- `tests/test_vision_contracts.py`
- `tests/test_preprocessing.py`
- `tests/test_inference_onnx.py`

## EXPECTED OUTPUT

Expected source structure after TASK-015:

    src/vision_iot/vision/
        __init__.py
        contracts.py
        inference_onnx.py
        preprocessing.py
        postprocessing.py

    tests/
        test_vision_contracts.py
        test_preprocessing.py
        test_inference_onnx.py
        test_postprocessing.py

Expected new generic contracts:

    BoundingBox
    Detection
    InferenceResult
    Postprocessor

Expected concrete implementation:

    YoloPostprocessor

No additional production modules are expected.

## ALLOWED CHANGES

The Implementation Agent may create or modify only:

- `.agent/tasks/TASK-015.md`
- `src/vision_iot/vision/contracts.py`
- `src/vision_iot/vision/postprocessing.py`
- `src/vision_iot/vision/__init__.py`
- `tests/test_vision_contracts.py`
- `tests/test_postprocessing.py`

This list is exhaustive.

Any required change outside these paths requires escalation before modification.

## FORBIDDEN CHANGES

The following are protected under TASK-015:

- `docs/architecture.md`
- `docs/project-context.md`
- all files under `docs/adr/`
- `.agent/rules/`
- `.agent/tasks/TASK-001.md` through `.agent/tasks/TASK-014.md`
- `src/vision_iot/hardware/`
- `src/vision_iot/vision/preprocessing.py`
- `src/vision_iot/vision/inference_onnx.py`
- all existing tests except `tests/test_vision_contracts.py`
- `requirements*.txt`
- `pyproject.toml`
- `Makefile`
- `.pre-commit-config.yaml`
- `.github/workflows/`
- `apps/`
- `training/`
- `deploy/`
- `models/`
- `data/`

The Implementation Agent must not weaken or bypass any existing quality gate.

## ACCEPTANCE CRITERIA

1. `BoundingBox` exists as a project-owned generic contract with floating-point
   `x1`, `y1`, `x2`, and `y2` fields.

2. `Detection` exists as a project-owned generic contract containing exactly
   the architecture-authorized detection information:
   `class_id`, `class_name`, `confidence`, and `bounding_box`.

3. `InferenceResult` exists as a project-owned generic vision result containing
   `frame_id`, `timestamp`, `detections`, and `inference_time_ms`.

4. `Postprocessor` exists as a synchronous generic boundary with the
   architecture-authorized `RawInference + Frame + SpatialMetadata ->
   InferenceResult` responsibility.

5. Existing `Frame`, `ModelInput`, `SpatialMetadata`, `RawInference`,
   `Preprocessor`, and `InferenceEngine` representations and semantics remain
   compatible.

6. `YoloPostprocessor` implements `Postprocessor`.

7. `YoloPostprocessor` supports only the authoritative YOLO26n ONNX
   `nms=None` reference representation required by TASK-015.

8. The reference raw output is validated as exactly one output tensor
   structurally compatible with `(N, 4 + nc, 8400)`.

9. The current reference implementation handles the single-item batch required
   by the existing reference preprocessing path without redesigning generic
   contracts for arbitrary batching.

10. Raw boxes are interpreted as model-space `xywh`.

11. Per-class scores are interpreted without assuming a separate objectness
    channel.

12. `class_id` is selected from the class-score vector and confidence equals
    the corresponding selected maximum class score.

13. Confidence filtering is implemented by `YoloPostprocessor` using minimal
    concrete configuration.

14. Class-aware NMS is implemented by `YoloPostprocessor` using minimal
    concrete IoU-threshold configuration.

15. Overlapping detections of the same class are suppressible according to the
    configured IoU threshold.

16. Overlapping detections of different classes do not suppress one another
    solely due to overlap.

17. No new production dependency is introduced for NMS or parsing.

18. Coordinate restoration uses `SpatialMetadata.scale_x`, `scale_y`,
    `pad_x`, and `pad_y` as authoritative transformation information.

19. Final bounding boxes are floating-point original-frame `xyxy` coordinates
    clipped to the original frame bounds.

20. Class names come only from an explicit class mapping supplied to the
    concrete postprocessor.

21. `InferenceResult.frame_id` and `timestamp` are propagated from the source
    `Frame`.

22. `InferenceResult.inference_time_ms` equals
    `RawInference.inference_time_ms` without adding postprocessing duration.

23. `Frame.image` is not modified or reprocessed by postprocessing.

24. No runtime-native, YOLO-native, ONNX-native, NMS-specific, or domain
    inspection structures leak into the generic result contracts.

25. Existing preprocessing and inference tests continue to pass unchanged.

26. All required deterministic validation commands pass.

27. No file outside `ALLOWED CHANGES` is modified.

## REQUIRED TESTS

Tests must remain deterministic and hardware-independent.

### Generic contract tests

Update `tests/test_vision_contracts.py` to verify the new generic contracts
without introducing YOLO-specific assumptions into generic contract tests.

At minimum verify:

- `BoundingBox` construction and field representation;
- `Detection` construction;
- `InferenceResult` construction;
- `Postprocessor` abstract/synchronous contract;
- existing generic contract behavior remains valid.

### Concrete YoloPostprocessor tests

Create `tests/test_postprocessing.py`.

Use synthetic:

- `Frame`;
- `SpatialMetadata`;
- `RawInference`;
- NumPy output tensors.

Do not execute ONNX Runtime.

Do not require a real YOLO model.

Synthetic reference tensors must match:

    (1, 4 + nc, 8400)

Keep tensors sparse and understandable.

Tests must cover at minimum:

1. no retained candidates;
2. one valid candidate;
3. confidence below threshold;
4. class selection;
5. multiple classes;
6. `xywh -> xyxy` conversion;
7. overlapping same-class boxes are suppressed according to IoU threshold;
8. overlapping different-class boxes are not cross-class suppressed;
9. coordinate restoration with no padding;
10. coordinate restoration with vertical letterbox padding;
11. coordinate restoration with horizontal letterbox padding;
12. restoration using effective integer-rounded preprocessing geometry;
13. clipping to original frame bounds;
14. frame ID propagation;
15. frame timestamp propagation;
16. inference-time propagation unchanged;
17. invalid output count fails clearly;
18. incompatible output shape/layout fails clearly;
19. class mapping is applied correctly;
20. source `Frame.image` is not modified.

Tests must not encode domain inspection semantics.

## VALIDATION COMMANDS

Run all commands from the repository root with the project virtual environment
active.

```bash
pytest -q tests/test_vision_contracts.py tests/test_postprocessing.py

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

The Implementation Report must include the result of every validation command.

If a validation command modifies files, the agent must inspect the resulting
working tree and re-run the affected validation before reporting completion.

## DEPENDENCIES

Prerequisites:

- TASK-012 — Vision Contract Foundation: completed and integrated.
- TASK-013 — Reference Vision Preprocessing: completed and integrated.
- TASK-014 — Baseline ONNX InferenceEngine: completed and integrated.
- M3.D architecture gate: closed.
- ADR-002 updated with authoritative YOLO26n ONNX reference-output semantics.
- ADR-004 updated with generic postprocessing contracts.

Existing numerical dependencies are sufficient.

No new production dependency is authorized or expected.

## BLOCKING CONDITIONS

The Implementation Agent must stop instead of guessing if any of the following
occurs.

Use `ARCHITECTURE_DECISION_REQUIRED` if:

- implementation appears to require changing `Frame`;
- implementation appears to require changing `ModelInput`;
- implementation appears to require changing `SpatialMetadata`;
- implementation appears to require changing `RawInference`;
- implementation appears to require changing `InferenceEngine`;
- the authoritative YOLO26n output representation appears inconsistent or
  insufficient;
- implementation requires supporting another YOLO output layout;
- confidence semantics become ambiguous;
- objectness semantics become ambiguous;
- NMS ownership or required behavior becomes ambiguous;
- class-ID interpretation becomes ambiguous;
- additional frame/model correlation metadata appears necessary;
- generic `Detection` appears to require model-specific fields;
- a new production dependency appears necessary;
- implementation requires a production YOLO model to establish normal unit
  test semantics;
- implementation requires architectural changes outside ADR-002/ADR-004
  decisions.

Use `TASK_BLOCKED` if:

- an authorized prerequisite artifact is missing;
- the repository cannot execute the required deterministic validation for an
  environmental reason that the agent cannot resolve within scope.

Use `HUMAN_DECISION_REQUIRED` if:

- multiple task-compliant implementation choices exist and selecting between
  them would materially affect public behavior beyond what the architecture
  establishes;
- protected files would need modification for reasons not covered by the
  existing architecture.

The agent must not:

- weaken tests;
- weaken lint/type-check gates;
- bypass pre-commit;
- modify Git configuration;
- expand `ALLOWED CHANGES`;
- silently repair unrelated repository issues.

If implementation cannot remain within the authorized scope, stop and
escalate.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS
`COMPLETED` or the appropriate escalation status.

### FILES CHANGED
List every created or modified file.

### IMPLEMENTATION SUMMARY
Concise description of what was implemented.

### TESTS ADDED / UPDATED
List of new or modified tests.

### VALIDATION RESULTS
Report each validation command and its result (including raw output/logs).

### DEVIATIONS
Any deviation from this TASK.

### BLOCKERS
Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS
Relevant observations discovered during implementation that were intentionally
not implemented.
