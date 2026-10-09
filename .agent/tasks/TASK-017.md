# TASK-017 — M4.A Domain Inspection Foundation

## STATUS

READY

## MILESTONE

M4 — Domain Inspection / M4.A — Domain Inspection Foundation

## OBJECTIVE

Establish the first project-owned domain inspection boundary and a deterministic conservative reference policy that converts valid `InferenceResult` instances into `InspectionEvent` instances without claiming unsupported package-damage detection capabilities.

## WHY

M3 established and validated the vision pipeline, including real-model compatibility with pretrained YOLO26n ONNX.

However, successful model execution and COCO detections do not establish package-damage inspection capability.

Architecture resolved `DOMAIN_INSPECTION_SEMANTICS_REQUIRED` and authorized M4.A to introduce a domain layer that distinguishes vision observations from justified inspection decisions.

The initial reference policy must explicitly report insufficient inspection evidence rather than manufacturing `OK` or `DAMAGED` outcomes.

## ARCHITECTURE REFERENCES

- `docs/architecture.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/004-vision-contracts.md` (resolve actual repository filename)
- `docs/adr/009-testing-strategy.md` (resolve actual repository filename)
- Architecture handoff dated 2026-10-09: *M4 Domain Semantics Gate Closure & M4.A Implementation Authorization*
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`

ADR-005 is authoritative and has already been materialized in commit `df46aec`.

No new architectural decisions are authorized under this TASK.

## SCOPE

### 1. Domain package

Create `src/vision_iot/domain/` as the first Architecture-v2 domain subsystem.

Follow existing project conventions for dataclasses, abstract base classes, explicit typing and public exports.

Do not create empty subpackages or unrelated infrastructure.

### 2. InspectionStatus

Define a strictly constrained enumeration containing exactly:

- `OK`
- `DAMAGED`
- `INCONCLUSIVE`

Do not add other inspection statuses.

### 3. InspectionReason

Define a strictly constrained reason representation with exactly one initially supported value:

- `UNSUPPORTED_MODEL`

This reason indicates that the configured model capability has not been validated for the package-damage inspection objective.

It does not indicate inference execution failure.

### 4. InspectionEvent

Define a project-owned domain data contract containing exactly:

- `inspection_id: str`
- `frame_id: str`
- `timestamp: float`
- `status: InspectionStatus`
- `reason: InspectionReason`
- `evidence: tuple[Detection, ...]`

Use existing project-owned `Detection` from the vision contracts.

Do not add transport metadata, model identifiers, confidence summaries, evaluation timestamps or other fields.

Enforce the minimum meaningful domain invariants without introducing a generic validation framework.

### 5. InspectionLogic

Define a synchronous abstract domain boundary:

```python
class InspectionLogic(ABC):
    @abstractmethod
    def inspect(
        self,
        result: InferenceResult,
        inspection_id: str,
    ) -> InspectionEvent:
        ...
```

Follow existing repository conventions.

### 6. UnvalidatedReferenceInspectionLogic

Implement one concrete domain policy named `UnvalidatedReferenceInspectionLogic`.

For every valid `InferenceResult` and non-empty string `inspection_id`, return:

```python
InspectionEvent(
    inspection_id=inspection_id,
    frame_id=result.frame_id,
    timestamp=result.timestamp,
    status=InspectionStatus.INCONCLUSIVE,
    reason=InspectionReason.UNSUPPORTED_MODEL,
    evidence=(),
)
```

The implementation must not interpret detections as package-defect evidence.

It must not inspect class IDs, confidence values, detection counts or bounding-box geometry to derive an inspection outcome.

The policy must be selected explicitly by its caller. Do not introduce automatic model-capability detection or policy selection.

### 7. Public exports

Expose the approved domain contracts and concrete policy through `src/vision_iot/domain/__init__.py`, following the explicit import and `__all__` conventions used by the existing vision and hardware packages.

### 8. Validation

Reject an empty or non-string `inspection_id` clearly.

Preserve the originating `InferenceResult.frame_id` and `InferenceResult.timestamp` without modification.

Keep domain event evidence empty for the unsupported-model policy.

Do not reinterpret existing M3 vision contract invariants.

## OUT OF SCOPE

- Real package-damage classification.
- Emission of `OK` or `DAMAGED` by the reference policy.
- Inference failure handling.
- Additional statuses or reasons.
- Confidence calibration.
- Model training, fine-tuning or dataset preparation.
- Camera acquisition or hardware integration.
- ONNX Runtime or YOLO processing changes.
- MQTT publication or serialization.
- Dashboard development.
- Application-level orchestration.
- Raspberry Pi deployment.
- NCNN integration.
- Benchmarking.
- Generic rules engines or model registries.
- Event persistence.
- Modifications to existing vision contracts.
- New production dependencies.
- Any implementation of M4.B.

## INPUTS / CONTRACTS

Existing authoritative vision representations:

```python
from vision_iot.vision import Detection, InferenceResult
```

`InferenceResult` contains:

```python
frame_id: str
timestamp: float
detections: tuple[Detection, ...]
inference_time_ms: float
```

The domain layer may consume these project-owned representations.

It must not depend on runtime-specific inference objects.

## EXPECTED OUTPUT

```text
src/vision_iot/domain/
├── __init__.py
├── contracts.py
└── inspection.py

tests/
└── test_domain_inspection.py
```

Expected public concepts:

- `InspectionStatus`
- `InspectionReason`
- `InspectionEvent`
- `InspectionLogic`
- `UnvalidatedReferenceInspectionLogic`

No other public domain API is required.

## ALLOWED CHANGES

The Implementation Agent may create or modify ONLY:

- `src/vision_iot/domain/__init__.py`
- `src/vision_iot/domain/contracts.py`
- `src/vision_iot/domain/inspection.py`
- `tests/test_domain_inspection.py`

The TASK contract itself is created and governed separately by Project Context.

Any modification outside these four paths requires escalation.

## FORBIDDEN CHANGES

Do not modify:

- `docs/architecture.md`
- `docs/adr/`
- `docs/project-context.md`
- `.agent/rules/`
- Existing `.agent/tasks/`
- `src/vision_iot/vision/`
- `src/vision_iot/hardware/`
- `src/vision_iot/infrastructure/`
- `apps/`
- `deploy/`
- `models/`
- `data/`
- Existing tests
- `pyproject.toml`
- Requirements files
- `Makefile`
- CI configuration
- Pre-commit configuration
- Git configuration

Do not create unrelated files or directories.

## ACCEPTANCE CRITERIA

1. The domain package exists and follows established repository conventions.
2. `InspectionStatus` contains exactly `OK`, `DAMAGED` and `INCONCLUSIVE`.
3. `InspectionReason` contains exactly `UNSUPPORTED_MODEL`.
4. `InspectionEvent` exposes exactly the six approved fields.
5. `InspectionLogic` defines the synchronous `inspect` boundary.
6. `UnvalidatedReferenceInspectionLogic` implements that boundary.
7. Every valid result evaluated by the reference policy produces `INCONCLUSIVE`.
8. The reason is always `UNSUPPORTED_MODEL`.
9. Supporting evidence is always an empty tuple.
10. Empty detections never produce `OK`.
11. Non-empty detections never produce `DAMAGED`.
12. Different class IDs do not change the inspection outcome.
13. Different confidence values do not change the inspection outcome.
14. `inspection_id` is supplied explicitly and preserved.
15. Empty or non-string inspection identifiers are rejected.
16. `frame_id` is preserved from `InferenceResult`.
17. `timestamp` is preserved from `InferenceResult`.
18. Identical inputs produce equivalent events.
19. The original `InferenceResult` and its detections are not modified.
20. No inference runtime, hardware or network execution occurs.
21. Existing M3 vision contracts remain unchanged.
22. No additional public domain abstractions are introduced.
23. All required deterministic tests pass.
24. Existing regression tests pass.
25. All configured quality gates pass.
26. Independent Review Agent returns `PASS`.
27. Human Gate approves the implementation before integration.

## REQUIRED TESTS

Create deterministic tests in `tests/test_domain_inspection.py`.

At minimum:

1. Exact `InspectionStatus` values.
2. Exact `InspectionReason` values.
3. Exact `InspectionEvent` field set.
4. Empty detections produce `INCONCLUSIVE / UNSUPPORTED_MODEL / ()`.
5. One synthetic detection produces the same conservative result.
6. Multiple synthetic detections produce the same conservative result.
7. Changing class IDs does not alter the result.
8. Changing confidence values does not alter the result.
9. Explicit `inspection_id` is preserved.
10. `frame_id` and `timestamp` are preserved.
11. Repeated calls with identical inputs produce equivalent events.
12. Empty inspection identifiers are rejected.
13. Non-string inspection identifiers are rejected.
14. The input result and its detections remain unchanged.
15. The concrete policy satisfies the `InspectionLogic` abstraction.
16. Public domain exports are available.
17. The reference policy never produces `OK` or `DAMAGED`.

Use synthetic `InferenceResult`, `Detection` and `BoundingBox` instances.

Do not use a real ONNX model, camera, MQTT broker, network service or physical Raspberry Pi.

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

Additionally verify that no unauthorized tracked or untracked files have been introduced.

Report the actual command outputs, including failures and corrections.

Do not bypass failing hooks.

## DEPENDENCIES

- TASK-012 through TASK-016 completed and integrated.
- M3 formally closed by Architecture.
- ADR-005 clarification integrated into `main`.
- M4.A explicitly authorized by Architecture.
- Existing Python project environment and quality tools.
- No additional dependencies authorized.

## BLOCKING CONDITIONS

Stop and escalate with `ARCHITECTURE_DECISION_REQUIRED` if:

- Existing `InferenceResult` or `Detection` contracts appear insufficient.
- Additional inspection statuses or reasons seem necessary.
- The implementation would need to infer model capability implicitly.
- COCO detections would need to be interpreted as package-damage evidence.
- The domain contract would need transport-specific fields.
- An additional evaluation timestamp or new timestamp semantics are proposed.
- The implementation requires a generic rule engine or model registry.
- New production dependencies are required.
- The approved ADR-005 conflicts with the intended implementation.

Stop and escalate with `TASK_BLOCKED` if:

- Required files or project dependencies are unavailable.
- The development environment cannot execute required validation.
- Existing quality gates fail for reasons outside authorized scope.

Stop and escalate with `HUMAN_DECISION_REQUIRED` if:

- Unauthorized file modifications are required.
- Git operations would alter protected branches or repository configuration.
- A decision beyond the Implementation Agent's authority is necessary.

Use `RETRY_EXHAUSTED` if the bounded correction loop reaches its configured limit without satisfying acceptance criteria.

Do not silently expand scope.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Describe the domain contracts and conservative reference policy.

### TESTS ADDED / UPDATED

List all new deterministic test cases.

### VALIDATION RESULTS

Provide actual command results and relevant raw output.

### DEVIATIONS

List any deviations from the authorized TASK.

### BLOCKERS

List unresolved blockers.

### OUT-OF-SCOPE OBSERVATIONS

Record relevant findings without implementing unauthorized changes.

Do not commit, merge, rebase, force-push, switch to `main`, or modify Git configuration.

Stop after implementation and validation. Independent review and Human Gate are separate ADS stages.
