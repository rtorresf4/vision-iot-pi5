# TASK-016 — M3.E Reference Model Compatibility Validation

## STATUS

READY

## MILESTONE

M3 — Vision Pipeline
M3.E — Reference Model Compatibility Validation

## OBJECTIVE

Validate the existing Architecture-v2 reference vision components together against a real, reproducibly exported YOLO26n ONNX artifact.

The required execution path is:

```text
Synthetic Frame
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
      |
      v
YoloPostprocessor
      |
      v
InferenceResult
```

The original `Frame` and associated `SpatialMetadata` must also be supplied to `YoloPostprocessor`.

TASK-016 is a compatibility-validation increment.

It must not introduce new production architecture, modify generic contracts, or implement application-level orchestration.

## WHY

TASK-012 through TASK-015 established the generic vision contracts and concrete reference preprocessing, inference, and postprocessing implementations.

Their deterministic tests establish component-level correctness.

They do not demonstrate that the selected YOLO26n ONNX export is compatible with the implemented reference path.

Architecture has therefore authorized M3.E to obtain empirical evidence using a real reference model artifact.

M3 remains INCOMPLETE until Architecture reviews the integrated M3.E evidence and explicitly authorizes milestone closure.

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/002-model-strategy.md`
- `docs/adr/003-inference-runtime.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/009-testing-strategy.md`
- `docs/adr/010-benchmarking-strategy.md`
- Architecture → Project Context handoff dated 2026-10-09, Post-M3.D Assessment.

The selected reference strategy remains:

```text
Model: YOLO26n
Format: ONNX
Export mode: nms=None
Output: raw one-to-many detection
Confidence filtering: YoloPostprocessor
NMS: external, class-aware
Coordinate restoration: SpatialMetadata
```

No ADR changes are authorized.

## SCOPE

### 1. Reference artifact acquisition

Obtain a real pretrained YOLO26n ONNX artifact using a reproducible procedure.

Use the reference export strategy established by ADR-002:

- YOLO26n pretrained weights.
- ONNX export.
- Explicit `nms=None`.
- Reference input size 640 × 640.
- Single-item batch configuration.

Use a separate model-preparation environment when Ultralytics or export-specific dependencies are required.

Do not add model-export dependencies to the Architecture-v2 production environment.

Do not replace the selected model with another YOLO generation or another export mode.

The local reference artifact may be stored at:

`models/yolo26n.onnx`

The artifact must not be committed to Git.

### 2. Artifact provenance

Document:

1. Exact pretrained model identity.
2. Model source.
3. Ultralytics export version.
4. Export command and parameters.
5. Explicit `nms=None` selection.
6. Export image size.
7. Export batch configuration.
8. ONNX opset version, where applicable.
9. Artifact filename.
10. SHA-256 checksum.
11. Actual ONNX input metadata.
12. Actual ONNX output metadata.
13. ONNX Runtime version.
14. Execution provider.
15. Reproduction and validation commands.

Do not invent or assume empirical values.

Record actual observations from the exported artifact.

### 3. Explicit compatibility validation

Create:

`tests/reference_model_compatibility.py`

This file must be an explicitly invoked validation script, not an ordinary pytest-discovered test.

The script must:

- Accept an explicit local ONNX artifact path.
- Fail clearly when the artifact is absent.
- Never download or export models automatically.
- Use the existing concrete vision components.
- Construct a deterministic synthetic BGR `Frame`.
- Execute `YoloPreprocessor`.
- Retain `SpatialMetadata`.
- Execute `ONNXInferenceEngine` using the real ONNX artifact.
- Obtain `RawInference`.
- Execute `YoloPostprocessor`.
- Obtain `InferenceResult`.
- Validate the required structural and semantic invariants.
- Report inspectable results.
- Return a nonzero exit status on failure.

Do not create a production orchestration abstraction.

### 4. Input interface validation

Inspect the real ONNX model input metadata.

Confirm:

- Exactly one numerical input.
- BCHW-compatible layout.
- Reference batch size of one.
- Three input channels.
- 640 × 640 reference dimensions.
- Numerical dtype compatible with `YoloPreprocessor`.
- Successful input binding through the existing `ONNXInferenceEngine`.

Do not modify preprocessing to accommodate an incompatible model.

### 5. Output interface validation

Inspect the real ONNX output metadata and actual inference output.

The selected reference representation is:

```text
Output tensor count: 1
Shape: (1, 4 + nc, 8400)
Layout: batch, channels, candidates
Boxes: xywh
Coordinate space: model input
Class scores: one per class per candidate
Separate objectness: absent
Class IDs: zero-based
Confidence: maximum class score
External NMS: required
```

Compare the observed artifact with these assumptions.

Do not treat model-specific output semantics as generic `RawInference` invariants.

If the real artifact differs materially, stop and request an Architecture decision.

### 6. Reference class mapping

Establish the real model class count and class ordering.

Provide `YoloPostprocessor` with an explicit mapping consistent with the artifact.

The mapping must not be invented or inferred solely from tensor shape.

Do not introduce damaged-package classes or domain inspection semantics.

Do not require training or fine-tuning.

### 7. Integrated execution validation

The validation must demonstrate:

- Successful model loading.
- Successful input binding.
- Successful ONNX inference.
- Compatible `RawInference` output.
- Successful reference postprocessing.
- A valid `InferenceResult`.
- Correct `frame_id`.
- Correct timestamp propagation.
- Exact propagation of `inference_time_ms`.
- A tuple of project-owned detections.
- Valid class IDs and names for any detections.
- Valid confidence values for any detections.
- Original-frame coordinate bounds for any detections.
- No runtime-specific objects in the generic result.

Zero detections are acceptable.

Do not assert that the synthetic image produces a specific class, confidence, or number of detections.

### 8. Evidence documentation

Create:

`docs/reference-model-validation.md`

Document the reproducible artifact preparation procedure and actual validation results.

Distinguish clearly between:

- Export environment.
- Architecture-v2 runtime environment.
- Model metadata inspection.
- Integrated execution evidence.
- Deterministic regression results.

Do not claim successful compatibility until the real-model validation has executed successfully.

## OUT OF SCOPE

- New generic vision contracts.
- Modifications to completed M3 components.
- New production pipeline or service.
- `VisionPipeline`.
- `InspectionPipeline`.
- Runtime factories or registries.
- Model registries.
- Automatic model downloads.
- Model hot reload.
- Model version switching.
- New production dependencies.
- Ultralytics runtime integration.
- Training or fine-tuning.
- Dataset creation.
- Model accuracy evaluation.
- Domain OK/DAMAGED decisions.
- `InspectionLogic`.
- `InspectionEvent`.
- MQTT.
- Dashboard integration.
- Raspberry Pi deployment.
- Physical camera validation.
- NCNN.
- Alternative execution providers.
- Runtime benchmarking.
- Changes to the legacy YOLOv8 path.
- Changes to CI or existing quality gates.

## ALLOWED CHANGES

The Implementation Agent may create or modify only:

- `.agent/tasks/TASK-016.md`
- `tests/reference_model_compatibility.py`
- `docs/reference-model-validation.md`

This list is exhaustive.

The real ONNX artifact may be generated locally under the existing ignored `models/*.onnx` path but must remain untracked.

Temporary export-environment files and generated export artifacts must remain outside the tracked repository.

Any required tracked-file change outside the authorized paths requires escalation.

## FORBIDDEN CHANGES

Protected files include:

- `docs/architecture.md`
- `docs/project-context.md`
- `docs/adr/`
- `.agent/rules/`
- `.agent/tasks/TASK-001.md` through `TASK-015.md`
- `src/vision_iot/`
- `apps/`
- `deploy/`
- `training/`
- `pyproject.toml`
- `requirements.txt`
- `requirements-dev.txt`
- `Makefile`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.github/workflows/`
- Existing automated tests.

Do not weaken or bypass any existing quality gate.

## ACCEPTANCE CRITERIA

1. A real YOLO26n ONNX reference artifact is obtained reproducibly.
2. The export mode is unambiguously established as `nms=None`.
3. Model provenance and export configuration are documented.
4. Artifact SHA-256 is recorded.
5. Actual ONNX input and output metadata are recorded.
6. Actual class count and ordering are established.
7. Input metadata is compatible with `YoloPreprocessor`.
8. The artifact loads through `ONNXInferenceEngine`.
9. Real inference produces valid `RawInference`.
10. Actual output representation matches the accepted ADR-002 assumptions.
11. `YoloPostprocessor` consumes the real output successfully.
12. The integrated execution produces a valid `InferenceResult`.
13. Frame identity and timestamp are preserved.
14. Inference execution timing is preserved unchanged.
15. Any detections satisfy the generic vision contracts.
16. The validation is explicitly invoked and requires no network access at execution time.
17. Ordinary deterministic tests remain independent of the real model.
18. No new production component or dependency is introduced.
19. No generic contract is modified.
20. No tracked file outside `ALLOWED CHANGES` is modified.
21. Existing deterministic tests and quality gates pass.
22. Independent Review Agent returns PASS.
23. Human Gate approves integration.

## VALIDATION COMMANDS

Run from the repository root with the project virtual environment active.

Deterministic quality gate:

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

Real-model validation, explicitly invoked:

```bash
python tests/reference_model_compatibility.py --model models/yolo26n.onnx
```

The Implementation Report must include the outcome of every command.

The real-model validation must not be silently skipped.

If the real model is unavailable, report the blocker rather than claiming completion.

## DEPENDENCIES

Completed prerequisites:

- TASK-012 — Generic Vision Contracts.
- TASK-013 — Reference Vision Preprocessing.
- TASK-014 — Baseline ONNX InferenceEngine.
- TASK-015 — Postprocessing Boundary.

Architecture gate:

- Post-M3.D assessment ACCEPTED.
- M3.E authorized.
- No new ADR required.

Runtime dependencies already available:

- NumPy.
- OpenCV.
- ONNX Runtime.

Export-specific dependencies must remain isolated.

## STOP AND ESCALATE CONDITIONS

Use `ARCHITECTURE_DECISION_REQUIRED` when:

- The real YOLO26n artifact cannot be obtained reproducibly.
- Export mode cannot be established.
- Multiple model inputs are required.
- Input layout or dtype conflicts with preprocessing.
- Output count, shape, or layout conflicts with ADR-002.
- Box coordinate semantics differ.
- Class-score or objectness semantics differ.
- External class-aware NMS is incompatible with the artifact.
- Class mapping cannot be established consistently.
- Existing postprocessing cannot consume the real output.
- Generic contracts must change.
- Completed M3 production components require behavioral changes.
- A new production dependency becomes necessary.
- Existing quality gates would need to be weakened.
- A new production orchestration abstraction appears necessary.
- Validation requires expanding into domain, MQTT, deployment, or hardware scope.

Use `TASK_BLOCKED` when:

- The local reference artifact is missing and cannot be prepared within the authorized procedure.
- The required validation cannot execute due to an environmental limitation.

Use `HUMAN_DECISION_REQUIRED` when:

- A tracked-file change outside `ALLOWED CHANGES` is required for a non-architectural reason.
- A task-compliant implementation choice has material consequences not resolved by the task contract.

The Implementation Agent must not silently redesign the reference model strategy.

## ADS WORKFLOW

1. Materialize the TASK contract.
2. Create the dedicated task branch.
3. Execute the Implementation Agent.
4. Run deterministic validation.
5. Run explicit real-model compatibility validation.
6. Execute independent Review Agent.
7. Apply bounded corrections if required.
8. Present evidence at Human Gate.
9. Integrate only after approval.
10. Update the Project Context checkpoint.
11. Return an M3 completion-assessment handoff to Architecture.

## DELIVERABLES

The Implementation Agent must provide:

### STATUS

`COMPLETED`, `TASK_BLOCKED`, `ARCHITECTURE_DECISION_REQUIRED`, or `HUMAN_DECISION_REQUIRED`.

### FILES CHANGED

Complete list of created or modified files.

### ARTIFACT PROVENANCE

Model source, export configuration, versions, checksum, and metadata.

### IMPLEMENTATION SUMMARY

Description of the explicit compatibility-validation mechanism.

### VALIDATION EVIDENCE

Observed ONNX interface, integrated execution results, and all quality-gate outcomes.

### DEVIATIONS

Any deviation from the authorized contract.

### BLOCKERS

Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS

Relevant findings intentionally left outside the implementation.
