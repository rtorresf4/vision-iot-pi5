# TASK-013 — M3.B Reference Vision Preprocessing

## Status

READY_FOR_IMPLEMENTATION

## Milestone

M3 — Vision Pipeline

Sub-increment:

M3.B — Reference Vision Preprocessing

## Objective

Implement the first concrete production `Preprocessor` for the initial YOLO26n
reference path.

The implementation must prove the existing Architecture-v2 boundary:

```text
Frame
  |
  v
concrete reference Preprocessor
  |
  v
ModelInput
```

using the already-established project-owned contracts.

This TASK ends at `ModelInput`.

It must not introduce inference execution, model loading, postprocessing, or
domain behavior.

---

## Architectural Authority

This TASK is governed by the currently accepted Architecture-v2 documentation,
including the architecture-authorized M3.B update already materialized in:

```text
docs/adr/002-model-strategy.md
```

ADR-002 defines the concrete preprocessing semantics for the initial YOLO
reference path.

The existing generic contracts remain governed by their existing architecture
decisions and must not be changed merely to accommodate this concrete
implementation.

### Critical architecture rule

The ADR-002 preprocessing semantics are behavior of the concrete reference
`Preprocessor` only.

They must NOT be encoded as additional universal invariants of:

- `Frame`;
- `Preprocessor`;
- `ModelInput`;
- `SpatialMetadata`.

In particular, this TASK must not redefine generic Architecture-v2 contracts
to universally require:

- BGR or RGB frame ordering;
- `float32`;
- `[0.0, 1.0]` values;
- CHW layout;
- a batch dimension;
- `640x640`;
- three channels.

---

## Pre-existing Architecture-Governed Change

Before TASK-013 implementation began, Project Context and Architecture
materialized an authorized update to:

```text
docs/adr/002-model-strategy.md
```

That modification is already present in the TASK working tree.

The Implementation Agent:

- MUST preserve that change;
- MUST NOT rewrite, reinterpret, revert, or extend it;
- MUST NOT claim it as an implementation-generated architecture decision.

The ADR modification is part of the final TASK-013 change set because it is
required to make the M3.B architecture authoritative, but its content is
human/architecture-governed.

---

## Existing Contracts

The implementation must use the existing contracts without modification.

### Frame

Provided by the existing hardware/acquisition subsystem.

The concrete OpenCV reference execution path provides the source representation
expected by this reference preprocessor.

This does NOT redefine generic `Frame.image` color ordering.

### Preprocessor

Existing synchronous boundary:

```python
Frame -> ModelInput
```

### ModelInput

Existing representation:

```text
ModelInput
    data: np.ndarray
    metadata: SpatialMetadata
```

### SpatialMetadata

Existing representation:

```text
SpatialMetadata
    original_width: int
    original_height: int
    input_width: int
    input_height: int
    scale_x: float
    scale_y: float
    pad_x: float
    pad_y: float
```

No fields may be added or changed by this TASK.

---

## Required Concrete Preprocessing Behavior

Implement one clearly model/reference-specific concrete `Preprocessor`.

Preferred class name:

```text
YoloPreprocessor
```

A different name is allowed only if it is equally explicit that the
implementation is specific to the YOLO reference path.

Do NOT use a generic name such as:

```text
DefaultPreprocessor
```

### Target size

The preprocessor must support a configurable square model-input size.

Default reference size:

```text
640x640
```

Configuration must remain minimal and local to the concrete preprocessor.

Do not introduce the Architecture-v2 configuration subsystem.

### Spatial transformation

The implementation must:

1. preserve source aspect ratio;
2. resize the source image accordingly;
3. letterbox-pad the resized image to the configured square target.

Conceptually:

```text
source image
    |
    v
aspect-ratio-preserving resize
    |
    v
letterbox padding
    |
    v
configured square model input
```

The source image must NOT be independently stretched along X and Y merely to
reach the target dimensions.

### Letterbox padding

Use padding value:

```text
114
```

per image channel.

Padding must be deterministic.

Where integer rounding causes an odd total padding amount, the implementation
must deterministically distribute the actual integer padding required to reach
the configured target dimensions.

`SpatialMetadata` must describe the actual offset applied before inference.

### Color transformation

For the OpenCV reference execution path:

```text
BGR -> RGB
```

This is concrete reference-path behavior only.

It must NOT redefine generic `Frame.image` semantics.

### Numerical representation

The concrete reference preprocessor must produce:

```text
dtype:
    np.float32

value transformation:
    [0, 255] -> [0.0, 1.0]
```

for valid `uint8` reference input.

### Tensor layout

Transform:

```text
HWC -> CHW
```

and add a leading batch dimension.

Reference output representation:

```text
(1, 3, input_height, input_width)
```

For the default configuration:

```text
(1, 3, 640, 640)
```

These are concrete `YoloPreprocessor` semantics, not generic `ModelInput`
invariants.

---

## SpatialMetadata Semantics

`SpatialMetadata` must be populated from the transformation ACTUALLY performed.

Do not merely store an ideal theoretical scale computed before integer resize
rounding.

Given actual resized dimensions:

```text
resized_width
resized_height
```

metadata must represent the effective spatial transformation.

Conceptually:

```text
scale_x = resized_width / original_width
scale_y = resized_height / original_height
```

and:

```text
pad_x
pad_y
```

must represent the actual spatial offset introduced before the resized image
inside the final letterboxed model input.

The metadata must allow future postprocessing to conceptually reverse:

```text
model-space coordinate
    |
    v
remove padding
    |
    v
undo effective scaling
    |
    v
original-frame coordinate
```

Integer resize rounding and actual applied padding must therefore be reflected
in the metadata.

Do NOT add fields to `SpatialMetadata`.

If the existing representation proves insufficient to correctly describe the
actual transform:

```text
ARCHITECTURE_DECISION_REQUIRED
```

and implementation must stop.

---

## Implementation Placement

Expected implementation module:

```text
src/vision_iot/vision/preprocessing.py
```

The concrete implementation should remain small and focused.

Do not introduce:

- preprocessing base classes beyond the existing `Preprocessor`;
- registries;
- factories unless demonstrably required by existing code;
- plugin systems;
- model registries;
- generalized preprocessing frameworks;
- speculative abstraction hierarchies.

The concrete preprocessor should be exported through:

```text
src/vision_iot/vision/__init__.py
```

consistent with the existing package API pattern.

---

## Dependency Constraints

No new dependency is authorized.

The implementation may use the existing:

```text
NumPy
OpenCV
```

baseline.

OpenCV may be used for:

- resize;
- color conversion;
- border/padding.

Do NOT add:

- Ultralytics;
- ONNX Runtime;
- NCNN;
- Pillow solely for preprocessing;
- torchvision;
- another image-processing library;
- a new configuration framework.

---

## Testing Requirements

Create dedicated concrete-preprocessor tests.

Expected test module:

```text
tests/test_preprocessing.py
```

Tests must be:

- deterministic;
- hardware-independent;
- runtime-independent;
- model-file-independent;
- network-independent.

Use synthetic NumPy images.

No physical camera is required.

No Raspberry Pi is required.

No model artifact is required.

No inference runtime is required.

### Required cases

At minimum cover:

#### 1. Square source

Representative case:

```text
source: 640x640
target: 640x640
```

Verify:

- no spatial distortion;
- no unnecessary letterbox spatial offset;
- correct output shape;
- correct effective metadata.

#### 2. Landscape source

Representative case:

```text
source: 1280x720
target: 640x640
```

Verify:

- aspect ratio preserved;
- expected vertical letterboxing;
- correct effective `scale_x`;
- correct effective `scale_y`;
- correct `pad_x`;
- correct `pad_y`;
- correct final output shape.

#### 3. Portrait source

Representative case:

```text
source: 720x1280
target: 640x640
```

Verify:

- aspect ratio preserved;
- expected horizontal letterboxing;
- correct effective `scale_x`;
- correct effective `scale_y`;
- correct `pad_x`;
- correct `pad_y`;
- correct final output shape.

#### 4. Numerical representation

Verify:

```text
dtype == np.float32
```

and valid `uint8` image data is transformed into the expected:

```text
[0.0, 1.0]
```

range.

#### 5. Tensor representation

Verify:

```text
shape == (1, 3, input_height, input_width)
```

for the configured target.

Verify the default reference behavior where appropriate:

```text
(1, 3, 640, 640)
```

#### 6. Color conversion

Use a tiny deterministic synthetic image whose channel values make channel
ordering unambiguous.

Verify the concrete reference behavior:

```text
BGR -> RGB
```

Do not encode this as a universal `Frame` invariant.

#### 7. Padding behavior

Verify deterministic letterbox padding and the reference padding value:

```text
114
```

taking the subsequent `[0,255] -> [0.0,1.0]` conversion into account when
asserting final `ModelInput.data`.

#### 8. Effective spatial metadata

Include coverage where integer resize rounding matters.

Verify that `scale_x`, `scale_y`, `pad_x`, and `pad_y` correspond to the
dimensions and offsets actually applied, rather than only an ideal
pre-rounding scale.

---

## Contract Preservation

Existing generic contract tests must remain conceptually generic.

Do NOT modify:

```text
tests/test_vision_contracts.py
```

to encode concrete YOLO preprocessing behavior.

The concrete implementation must produce the existing `ModelInput` type.

The following production contract file must remain unchanged:

```text
src/vision_iot/vision/contracts.py
```

TASK-013 must not change:

- `Frame`;
- `Preprocessor`;
- `ModelInput`;
- `SpatialMetadata`;
- `InferenceEngine`;
- `RawInference`.

---

## ALLOWED CHANGES

The complete allowed TASK-013 file scope is:

```text
docs/adr/002-model-strategy.md
.agent/tasks/TASK-013.md
src/vision_iot/vision/preprocessing.py
src/vision_iot/vision/__init__.py
tests/test_preprocessing.py
```

Notes:

- `docs/adr/002-model-strategy.md` already contains the architecture-governed
  modification and must only be preserved by the Implementation Agent.
- `.agent/tasks/TASK-013.md` is the human-governed TASK contract and must not be
  modified by the Implementation Agent.
- `src/vision_iot/vision/preprocessing.py` and
  `tests/test_preprocessing.py` may be created.
- `src/vision_iot/vision/__init__.py` may be modified only as required to
  expose the concrete reference preprocessor.

No other file may be modified, created, deleted, renamed, or generated as part
of TASK-013.

---

## Explicitly Protected / Forbidden Areas

Among others, the following are protected:

```text
src/vision_iot/vision/contracts.py
tests/test_vision_contracts.py

src/vision_iot/hardware/
src/vision_iot/application/
src/vision_iot/domain/
src/vision_iot/infrastructure/
src/vision_iot/config/

apps/
training/
deploy/
models/
data/

requirements*.txt
pyproject.toml
Makefile
.github/workflows/
.pre-commit-config.yaml

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
```

Existing generated local cache files are not TASK artifacts and must not be
added to version control.

---

## Explicit Non-Goals

TASK-013 must NOT introduce or implement:

- `ONNXInferenceEngine`;
- `NCNNInferenceEngine`;
- ONNX Runtime integration;
- model loading;
- real model execution;
- runtime input binding;
- runtime output conversion;
- new `RawInference` behavior;
- `Postprocessor`;
- `Detection`;
- `InferenceResult`;
- YOLO output parsing;
- confidence filtering;
- NMS;
- `InspectionLogic`;
- `InspectionEvent`;
- `InspectionPipeline`;
- MQTT behavior;
- dashboard behavior;
- dataset/training work;
- deployment work;
- Raspberry Pi-specific behavior;
- legacy application migration;
- generalized preprocessing framework;
- preprocessing registry;
- model registry;
- plugin architecture;
- full configuration subsystem;
- new dependencies.

Existing code under:

```text
apps/pi_detector/
```

may be inspected as non-authoritative implementation evidence only.

It must not be modified and must not automatically define the new
Architecture-v2 implementation.

---

## Acceptance Criteria

TASK-013 is complete only when all of the following are true:

1. A concrete YOLO-reference `Preprocessor` exists.

2. It implements the existing `Preprocessor` abstract boundary.

3. It consumes the existing `Frame` representation.

4. It produces the existing `ModelInput` representation.

5. Default target size is `640x640`.

6. Target size is minimally configurable as a square model input.

7. Source aspect ratio is preserved.

8. Deterministic letterbox padding is applied.

9. Reference padding value is `114` per channel.

10. OpenCV reference input is converted BGR -> RGB.

11. Output data is `np.float32`.

12. Valid `uint8` reference input is scaled from `[0,255]` to `[0.0,1.0]`.

13. Layout is converted HWC -> CHW.

14. A leading batch dimension is added.

15. Reference output shape is
    `(1, 3, input_height, input_width)`.

16. `SpatialMetadata` represents the actual effective resize and actual padding
    applied after integer rounding.

17. Square, landscape, and portrait source behavior is covered.

18. Color conversion is covered deterministically.

19. Padding behavior is covered deterministically.

20. Integer-rounding/effective-metadata behavior is covered.

21. Tests use synthetic NumPy images.

22. No physical camera is required.

23. No model artifact is required.

24. No inference runtime is required.

25. No network access is required.

26. Generic vision contracts remain unchanged.

27. Generic vision contract tests remain unchanged.

28. No concrete `InferenceEngine` is introduced.

29. No postprocessing contract or implementation is introduced.

30. No legacy application code is modified.

31. No new dependency is introduced.

32. Existing tests remain passing.

33. Existing quality gates remain unchanged.

34. No file outside the explicit ALLOWED CHANGES scope is changed or created by
    the TASK.

---

## Blocking / Escalation Conditions

STOP implementation and escalate instead of extending scope if any of the
following occurs:

1. `Frame` requires modification.

2. `ModelInput` requires modification.

3. `SpatialMetadata` requires modification.

4. `Preprocessor` contract requires modification.

5. Additional stable spatial metadata is required.

6. BGR must become a universal `Frame` invariant.

7. YOLO preprocessing semantics must become universal `ModelInput` invariants.

8. A real model artifact is required for deterministic preprocessing tests.

9. ONNX Runtime is required.

10. A new dependency is required.

11. Legacy application code must be modified.

12. `Postprocessor`, `Detection`, or `InferenceResult` becomes necessary.

13. Existing quality gates require weakening, suppression, or configuration
    changes.

14. Implementation begins introducing a generalized preprocessing framework,
    registry, plugin architecture, model registry, or speculative abstraction
    hierarchy.

15. Correct implementation would require changing a file outside the explicit
    ALLOWED CHANGES scope.

Use the existing ADS escalation mechanisms:

```text
TASK_BLOCKED
ARCHITECTURE_DECISION_REQUIRED
HUMAN_DECISION_REQUIRED
RETRY_EXHAUSTED
```

Do not silently expand scope.

---

## Required Validation

The Implementation Agent must run and report deterministic evidence for:

```bash
pytest -q tests/test_preprocessing.py
black --check .
ruff check .
mypy apps src
pytest -q
make lint
make test
pre-commit run --all-files
git diff --check
```

After all validation, run again:

```bash
git status --short
```

The final status must be inspected for:

- unintended modifications;
- unintended untracked files;
- generated artifacts;
- scope violations.

Validation success does not override architectural or TASK scope violations.

---

## Implementation Report

When implementation is complete, report:

### Files

- files created;
- files modified;
- confirmation that no files outside ALLOWED CHANGES were changed.

### Behavior

- concrete preprocessor class name;
- target-size configuration;
- resize/letterbox strategy;
- color conversion;
- dtype and normalization;
- tensor layout and batch behavior;
- effective `SpatialMetadata` calculation.

### Tests

- focused preprocessing test count;
- focused preprocessing test result;
- full test-suite result.

### Quality Gates

Report results for every required validation command.

### Architecture Preservation

Explicitly confirm:

- `Frame` unchanged;
- `Preprocessor` contract unchanged;
- `ModelInput` unchanged;
- `SpatialMetadata` unchanged;
- `InferenceEngine` unchanged;
- `RawInference` unchanged;
- `tests/test_vision_contracts.py` unchanged;
- ADR-002 architecture-governed change preserved;
- no new dependency;
- no inference runtime;
- no postprocessing;
- no legacy application migration.

### Final Repository State

Include:

```bash
git status --short
```

and identify every remaining changed/untracked path.

Do not commit, merge, rebase, push, or alter Git configuration.

Human Gate remains required before integration.
