# TASK-010 — OpenCV Acquisition Adapter

## STATUS

READY

## MILESTONE

M2 — Acquisition

## OBJECTIVE

Implement the first concrete OpenCV-backed `FrameSource` for Architecture v2.

The adapter must acquire exactly one image per synchronous acquisition operation
and expose it through the existing project-owned acquisition contracts:

    OpenCV / camera
          |
          v
    OpenCVFrameSource
          |
          v
      FrameSource
          |
          v
        Frame

This task ends at acquisition.

It must not introduce preprocessing, inference, inspection logic, event
distribution, dashboard behavior, or pipeline orchestration.

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
- `.agent/tasks/TASK-008.md`

Existing `Frame`, `FrameSource`, and `FakeFrameSource` contracts established by
TASK-008 must be preserved.

## EXISTING FRAME CONTRACT

`Frame.image` uses `numpy.ndarray`.

Established minimum semantics:

    image.ndim == 3
    image.shape[0] == Frame.height
    image.shape[1] == Frame.width

The following remain intentionally deferred and MUST NOT become new stable
`Frame` requirements in this task:

- RGB vs BGR ordering;
- exact channel count;
- dtype;
- value range;
- normalization;
- model tensor layout;
- memory contiguity;
- mutability;
- ownership/copy semantics.

## ALLOWED CHANGES

Only the following files may be created or modified:

- `.agent/tasks/TASK-010.md`
- `src/vision_iot/hardware/camera.py`
- `src/vision_iot/hardware/__init__.py`
- `tests/test_acquisition.py`

No other repository file is authorized for modification.

The TASK contract is human-controlled. The Implementation Agent must not modify
`.agent/tasks/TASK-010.md`.

## REQUIRED IMPLEMENTATION

The implementation must:

1. Add one concrete OpenCV-backed implementation of `FrameSource` named
   `OpenCVFrameSource`.

2. Preserve the existing `Frame`, `FrameSource`, and `FakeFrameSource`
   contracts.

3. Accept the minimum camera/device identifier required to construct the
   OpenCV capture boundary.

4. Keep camera configuration local and minimal. Do not introduce a generalized
   configuration subsystem.

5. Acquire exactly one frame for each synchronous `get_frame()` operation.

6. Convert successful acquisition into the existing `Frame` contract.

7. Populate:

       id
       timestamp
       image
       width
       height

8. Derive `Frame.width` and `Frame.height` from the actual acquired image:

       image.shape[1]
       image.shape[0]

   Requested or configured camera dimensions must not be treated as the
   authoritative dimensions of the returned `Frame`.

9. Generate `Frame.id` using a simple standard-library mechanism suitable for
   future correlation.

10. Populate `Frame.timestamp` using a simple local standard-library time
    source compatible with the existing float contract.

11. Preserve the OpenCV-acquired image representation as long as it satisfies
    the established `Frame.image` contract.

12. Do not perform color conversion solely to establish an RGB/BGR contract.

13. Isolate direct `cv2.VideoCapture` interaction inside the concrete adapter.

14. Provide deterministic release of the underlying camera resource.

15. Keep acquisition synchronous.

## ACQUISITION ERROR SEMANTICS

A single minimal project-owned acquisition exception is authorized if required.

Use:

    CameraError

if a project-owned error is necessary.

It may represent inability to perform the camera acquisition operation,
including:

- camera/device cannot be opened;
- frame cannot be read.

Do not introduce more than one acquisition-specific exception.

Do not create an exception hierarchy.

Do not change the public `FrameSource` contract to add error-specific behavior.

If more complex public error semantics appear necessary, stop and escalate.

## RESOURCE LIFECYCLE

The OpenCV camera resource must be releasable deterministically.

Keep lifecycle behavior minimal.

Do not introduce:

- background workers;
- threads;
- asyncio;
- queues;
- connection pools;
- automatic reconnection;
- long-running capture services.

If deterministic cleanup requires modification of the existing public
`FrameSource` contract, stop and escalate.

## TESTING REQUIREMENTS

Tests must remain deterministic and hardware-independent.

Normal tests and CI must not require:

- a physical camera;
- Raspberry Pi hardware;
- `/dev/video*`;
- camera drivers.

Use the smallest available test seam around the OpenCV capture boundary.

Existing pytest facilities such as monkeypatching or small dependency injection
are permitted.

Do not add a mocking-framework dependency.

Tests must cover at minimum:

1. successful camera opening;
2. successful frame acquisition;
3. successful conversion to `Frame`;
4. width derived from the actual returned image;
5. height derived from the actual returned image;
6. populated `Frame.id`;
7. populated `Frame.timestamp`;
8. camera-open failure produces `CameraError`;
9. frame-read failure produces `CameraError`;
10. deterministic camera-resource release;
11. no physical hardware is required.

Existing TASK-008 acquisition tests must remain passing and must not be
weakened.

Tests must verify externally relevant behavior rather than unnecessary OpenCV
implementation details.

## LEGACY CODE BOUNDARY

The following existing files may be inspected as implementation evidence:

- `apps/tools/check_camera.py`
- `apps/tools/capture_dataset.py`
- `apps/pi_detector/main.py`

They are not Architecture-v2 contracts.

They must not be modified, migrated, deleted, or refactored by this task.

Existing applications must not be redirected to `OpenCVFrameSource`.

## FORBIDDEN CHANGES

Do not modify:

- `apps/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- `README.md`
- `docs/architecture.md`
- `docs/adr/`
- `docs/project-context.md`
- `GEMINI.md`
- `.agent/rules/`
- completed `.agent/tasks/`
- `requirements*.txt`
- `pyproject.toml`
- `Makefile`
- `.github/workflows/`
- `.pre-commit-config.yaml`

Do not create:

- `src/vision_iot/application/`
- `src/vision_iot/domain/`
- `src/vision_iot/vision/`
- `src/vision_iot/infrastructure/`
- `src/vision_iot/config/`

## FORBIDDEN ABSTRACTIONS

Do not introduce:

- `CameraManager`;
- `CaptureService`;
- `DeviceRegistry`;
- `CameraFactory`;
- camera plugin systems;
- provider registries;
- generic hardware frameworks;
- generalized camera configuration contracts;
- streaming abstractions;
- concurrency abstractions.

One concrete adapter is sufficient.

## DEFERRED CONTRACTS

Do not materialize:

- `ModelInput`
- `RawInference`
- `Detection`
- `InferenceResult`
- `Preprocessor`
- `InferenceEngine`
- `Postprocessor`
- `InspectionLogic`
- `InspectionEvent`
- `InspectionPipeline`
- `EventPublisher`
- `MqttPublisher`

## DEPENDENCY CONSTRAINTS

No new dependency is authorized.

Use the existing OpenCV and NumPy dependency baseline.

Do not introduce:

- additional camera libraries;
- mocking frameworks;
- dependency-injection frameworks;
- configuration frameworks;
- image abstraction libraries.

The repository has already confirmed `opencv-python` in the existing
`requirements.txt` and `requirements-ci.txt` baseline.

## QUALITY GATE

The existing blocking quality gate remains authoritative:

    black --check .
    ruff check .
    mypy apps src
    pytest -q
    make lint
    make test
    pre-commit run --all-files

No quality configuration change is authorized.

Do not add broad typing suppressions to accommodate OpenCV.

If OpenCV typing materially conflicts with the existing mypy gate, stop and
escalate.

## FOCUSED VALIDATION

Run:

    pytest -q tests/test_acquisition.py

in addition to the full quality gate.

## ACCEPTANCE CRITERIA

1. `OpenCVFrameSource` exists as a concrete `FrameSource`.
2. Existing `FrameSource` is not redesigned.
3. Existing `Frame` is not redesigned.
4. Existing `FakeFrameSource` behavior remains unchanged.
5. Consumers do not need to interact directly with `cv2.VideoCapture`.
6. One synchronous `get_frame()` operation acquires exactly one image.
7. Successful acquisition returns a valid `Frame`.
8. `Frame.image` is a NumPy ndarray satisfying the accepted ADR-004 contract.
9. `Frame.image.ndim == 3`.
10. `Frame.width == Frame.image.shape[1]`.
11. `Frame.height == Frame.image.shape[0]`.
12. Width and height are derived from the actual acquired image.
13. `Frame.id` is populated using a standard-library mechanism.
14. `Frame.timestamp` is populated using a local standard-library time source.
15. No RGB/BGR invariant is added to the stable `Frame` contract.
16. No exact channel-count invariant is added.
17. No dtype invariant is added.
18. No value-range invariant is added.
19. No normalization behavior is introduced.
20. Camera-open failure produces the single project-owned `CameraError`.
21. Frame-read failure produces the single project-owned `CameraError`.
22. No broad acquisition exception hierarchy is introduced.
23. Underlying camera resources can be released deterministically.
24. The adapter remains synchronous.
25. No threads are introduced.
26. No asyncio is introduced.
27. No queues or background capture loops are introduced.
28. Tests require no physical camera or Raspberry Pi.
29. Tests cover successful acquisition.
30. Tests cover camera-open failure.
31. Tests cover frame-read failure.
32. Tests cover deterministic resource release.
33. Existing TASK-008 acquisition tests remain passing and are not weakened.
34. Existing legacy code under `apps/` remains unchanged.
35. No preprocessing behavior is introduced.
36. No inference behavior is introduced.
37. No domain behavior is introduced.
38. No MQTT or dashboard behavior is introduced.
39. No generalized configuration subsystem is introduced.
40. No camera framework/factory/registry abstraction is introduced.
41. No new dependency is added.
42. Black passes.
43. Ruff passes.
44. mypy passes for `apps` and `src`.
45. pytest passes.
46. `make lint` passes.
47. `make test` passes.
48. pre-commit passes.
49. Architecture v2 and existing ADRs remain unchanged.
50. All repository changes remain within `ALLOWED CHANGES`.
51. Final working-tree inspection shows no unintended validation artifacts.

## BLOCKING / ESCALATION CONDITIONS

Stop implementation and return the appropriate ADS escalation if:

1. `FrameSource` must change.
2. `Frame` must change.
3. RGB/BGR must become a stable `Frame` contract decision.
4. dtype, value range, exact channel count, mutability, ownership, or memory
   layout must become stable `Frame` semantics.
5. A new dependency is required.
6. More than one acquisition-specific exception appears necessary.
7. A broad acquisition exception hierarchy appears necessary.
8. Deterministic cleanup requires changing `FrameSource`.
9. Tests require physical hardware.
10. Existing code under `apps/` must be modified.
11. A deferred Architecture-v2 contract is required.
12. A generalized configuration subsystem becomes necessary.
13. Quality gates require suppression or weakening.
14. Implementation begins turning into a general camera framework.

Use the existing ADS escalation mechanisms:

    TASK_BLOCKED
    ARCHITECTURE_DECISION_REQUIRED
    HUMAN_DECISION_REQUIRED
    RETRY_EXHAUSTED

Do not silently expand scope.

## IMPLEMENTATION AGENT REPORT

The Implementation Agent must report:

- `STATUS`
- files changed;
- implementation summary;
- acceptance-criteria evidence;
- validation commands and results;
- deviations, if any;
- escalation, if any;
- final `git status --short`.

After all validation commands, inspect the working tree again.

No generated or unintended artifacts may remain.
