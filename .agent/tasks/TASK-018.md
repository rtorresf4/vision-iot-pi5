# TASK-018 — M4.B Inspection Decision Policy Specification

## STATUS

READY

## MILESTONE

M4 — Domain Inspection / M4.B — Inspection Decision Policy Specification

## OBJECTIVE

Produce a bounded, project-owned domain inspection specification defining the intended single-package visible-damage inspection scenario, candidate decision criteria, required model evidence, empirical validation prerequisites, and unresolved architectural or empirical questions.

The specification must establish decision readiness for future domain-policy development without implementing a conclusive inspection policy or claiming unvalidated model capabilities.

## WHY

TASK-017 completed M4.A by establishing the project-owned domain inspection contracts and `UnvalidatedReferenceInspectionLogic`.

The existing pretrained YOLO26n COCO reference model has been validated for inference execution and vision-contract compatibility, but not for detecting package damage.

Consequently, the only currently authorized policy returns `INCONCLUSIVE`, `UNSUPPORTED_MODEL`, and empty evidence.

Before implementing a policy capable of producing justified `OK` or `DAMAGED` decisions, the project must specify what an acceptable or damaged package means, what evidence is required, and how future model capability must be validated.

Architecture has explicitly authorized M4.B as a documentation-only increment.

## ARCHITECTURE REFERENCES

Authoritative references:

- `docs/architecture.md`
- `docs/adr/001-vision-task.md`
- `docs/adr/002-model-strategy.md`
- `docs/adr/004-vision-contracts.md`
- `docs/adr/005-domain-inspection-contract.md`
- `docs/adr/009-testing-strategy.md`
- `docs/project-context.md`
- `.agent/tasks/TASK-017.md`
- Architecture → Project Context Handoff, 2026-10-23: M4.A Closure & M4.B Inspection Decision Policy Specification

Relevant architectural decisions:

- `M4_A_CLOSURE_APPROVED`
- `M4_MILESTONE_INCOMPLETE`
- `M4_B_PLANNING_AUTHORIZED`
- `TASK_018_MATERIALIZATION_AUTHORIZED`
- `PRODUCTION_DOMAIN_POLICY_IMPLEMENTATION_NOT_AUTHORIZED`
- `NO_ADR_CHANGE_REQUIRED_BEFORE_TASK`

The architecture handoff authorizes documentation and inspection-requirement specification only.

No new ADR is authorized or required by this TASK.

## SCOPE

### 1. Inspection scenario

Specify the initial Architecture-v2 inspection scenario:

- Fixed camera.
- One package per inspection cycle.
- Externally visible package damage.
- Local inference.
- Raspberry Pi 5 as the future deployment target.

Document the intended inspected object, visibility assumptions, inspection region, and expected inspection conditions.

Clearly distinguish assumptions from requirements supported by accepted architecture.

Do not broaden the scenario.

### 2. Candidate visible-damage categories

Evaluate relevant candidate defect categories for the initial scenario.

Architectural examples include:

- Visible deformation.
- Tearing or rupture.
- Externally observable structural damage.

For each candidate category, document:

- A concise definition.
- Observable visual characteristics.
- Intended domain meaning.
- Ambiguous cases.
- Exclusions.
- The type of model evidence that could support its recognition.
- Whether its inclusion is an accepted requirement, a proposal, or an unresolved decision.

Do not treat these examples as already approved model classes.

Do not equate pretrained COCO classes with package-defect classes.

### 3. Acceptance criteria

Specify proposed requirements for considering an inspected package acceptable.

Explain the evidence that a future validated model or inspection process would need to provide before a policy could produce `OK`.

Explicitly state that:

- Successful inference is not sufficient.
- An empty detection set is not sufficient.
- The absence of validated defect evidence alone does not prove acceptability.

Do not implement an acceptance policy.

### 4. Damage decision criteria

Specify proposed requirements for producing `DAMAGED`.

Define the relationship between approved defect categories, observable evidence, inspection conditions, and future validated model outputs.

A conclusive damage decision must require evidence supporting a defect that violates an approved inspection criterion.

Do not invent production thresholds or rules.

### 5. Inconclusive inspection conditions

Document circumstances in which available evidence cannot support a justified conclusive decision.

Assess cases including:

- Package not reliably identified.
- Relevant inspection region insufficiently visible.
- Ambiguous visual evidence.
- Contradictory detections.
- Model capability not validated for the inspection objective.

These are specification candidates, not authorization to add `InspectionReason` enum values.

Explicitly distinguish insufficient inspection evidence from operational inference failure.

### 6. Available evidence and model capability

Document the capabilities of existing project-owned vision representations:

`InferenceResult`:

- `frame_id`
- `timestamp`
- `detections`
- `inference_time_ms`

`Detection`:

- `class_id`
- `class_name`
- `confidence`
- `bounding_box`

Identify what these representations can express and which required inspection capabilities have not yet been demonstrated.

Specify testable capability requirements for a future specialized model, such as relevant defect recognition and localization.

Do not assume that a confidence score is itself a calibrated inspection probability.

### 7. Empirical validation prerequisites

Define the types of empirical evidence required before authorizing a future conclusive policy.

Address:

- Labeled reference images.
- Representative acceptable packages.
- Representative damaged packages.
- Ambiguous or unsuitable examples.
- Held-out evaluation data.
- Defect-specific performance.
- False acceptance and false rejection behavior.
- Robustness under intended inspection conditions.

Distinguish inspection accuracy from inference runtime performance.

Do not invent numerical performance thresholds, measured results, validation success, or dataset availability.

### 8. Future policy activation prerequisites

Specify the conditions required before a future policy can produce `OK` or `DAMAGED`.

These must include, as applicable:

- Approved inspection criteria.
- Demonstrated model capability.
- Appropriate empirical evidence.
- Architecture approval of any required contract changes.
- Explicit policy selection by the eventual composition layer.

The specification must not introduce automatic model recognition, policy selection, or a capability registry.

### 9. Milestone relationships

Document the relevant dependencies and responsibilities:

- M5: Event Distribution.
- M6: Application composition / Vertical Slice.
- M7: Dataset and model development.
- M8: Raspberry Pi deployment validation.
- M9: Runtime benchmarking.

M4.B provides inspection requirements useful to M7.

M4.B does not execute any of these milestones.

### 10. Contract sufficiency assessment

Assess whether the currently approved contracts appear sufficient for future conclusive policy development:

- `InspectionStatus`
- `InspectionReason`
- `InspectionEvent`
- `InspectionLogic`
- `InferenceResult`
- `Detection`

Record any demonstrated limitations or unresolved questions.

Do not amend these contracts.

If a normative contract change is required, stop and escalate to Architecture.

### 11. Requirements classification

The specification must visibly distinguish:

1. Accepted architectural requirements.
2. Proposed future inspection criteria.
3. Empirical assumptions or questions pending validation.

Do not silently promote proposals to accepted decisions.

### 12. Documentation consistency

Use terminology consistent with accepted Architecture-v2 documents.

Include explicit references to the relevant ADRs and existing domain contracts.

Keep the deliverable focused, technically reviewable, and suitable as a requirements input for future model-development work.

## OUT OF SCOPE

- Production Python code.
- New domain classes or policies.
- Changes to `InspectionStatus`, `InspectionReason`, `InspectionEvent`, or `InspectionLogic`.
- Changes to `Detection` or `InferenceResult`.
- `OK` or `DAMAGED` policy implementation.
- New model-capability registries.
- Policy factories or automatic selection.
- Generic rules engines.
- New datasets or annotations.
- Model training or fine-tuning.
- Model exports or accuracy benchmarking.
- ONNX/NCNN runtime changes.
- Camera or Raspberry Pi integration.
- MQTT event distribution or serialization.
- Application orchestration.
- Dashboard changes.
- CI, dependencies, or configuration updates.
- ADR modifications.
- Implementation of M5 through M9.
- Formal closure of M4.

## INPUTS / CONTRACTS

Existing authoritative domain API:

```python
InspectionLogic.inspect(
    result: InferenceResult,
    inspection_id: str,
) -> InspectionEvent
```

Existing domain event:

```python
InspectionEvent(
    inspection_id: str,
    frame_id: str,
    timestamp: float,
    status: InspectionStatus,
    reason: InspectionReason,
    evidence: tuple[Detection, ...],
)
```

Current status values:

```text
OK
DAMAGED
INCONCLUSIVE
```

Current reason values:

```text
UNSUPPORTED_MODEL
```

Current conservative policy:

```text
UnvalidatedReferenceInspectionLogic
    -> INCONCLUSIVE
    -> UNSUPPORTED_MODEL
    -> evidence = ()
```

The specification may reference these established contracts but must not modify them.

The implementation of TASK-017 and accepted ADR-005 are authoritative for current domain behavior.

## EXPECTED OUTPUT

Create:

```text
docs/
└── domain-inspection-policy.md
```

The document must contain, at minimum:

1. Purpose and bounded inspection scenario.
2. Target package and visibility assumptions.
3. Candidate visible-damage categories.
4. Proposed package acceptance criteria.
5. Required evidence for `OK`.
6. Required evidence for `DAMAGED`.
7. Conditions requiring `INCONCLUSIVE`.
8. Separation of inconclusive inspections and operational failures.
9. Available vision evidence and limitations.
10. Required specialized model capabilities.
11. Empirical validation prerequisites.
12. Future conclusive-policy activation prerequisites.
13. Relationships and dependencies with M5–M9, especially M7.
14. Existing contract sufficiency assessment.
15. Explicit unresolved questions.
16. Architecture and ADR references.
17. Clear classification of accepted requirements, proposals, and empirical assumptions.

Use a focused technical specification format. Avoid unnecessary documentation scaffolding.

## ALLOWED CHANGES

The Implementation Agent may create or modify ONLY:

- `docs/domain-inspection-policy.md`

The TASK contract `.agent/tasks/TASK-018.md` is materialized separately by Project Context before implementation.

No other path is authorized for implementation.

## FORBIDDEN CHANGES

Do not modify:

- `docs/architecture.md`
- `docs/adr/`
- `docs/project-context.md`
- `docs/reference-model-validation.md`
- `docs/INDUSTRIAL_NOTES.md`
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

Do not create other documents, scripts, modules, tests, data files, or generated artifacts.

## ACCEPTANCE CRITERIA

1. The inspection scenario remains limited to one package under a fixed camera.
2. The target package assumptions are explicit.
3. Relevant visibility constraints are described.
4. Candidate visible-damage categories are documented with definitions, observable characteristics, ambiguities and exclusions.
5. Proposed defect criteria are distinguishable from generic COCO object detections.
6. Proposed acceptance criteria are documented without claiming they are validated.
7. Evidence prerequisites for `OK` are explicit.
8. Evidence prerequisites for `DAMAGED` are explicit.
9. Insufficient-evidence conditions are documented.
10. Inference execution failures remain separate from `INCONCLUSIVE`.
11. Required future model capabilities are stated in testable terms.
12. Existing vision evidence representations and limitations are identified.
13. Required empirical validation evidence is documented.
14. False acceptance and false rejection behavior is addressed.
15. Numerical performance thresholds and validation results are not fabricated.
16. Current domain contracts remain unchanged.
17. `UnvalidatedReferenceInspectionLogic` remains unchanged.
18. No conclusive policy is implemented.
19. No model capability is inferred from COCO class names.
20. Future policy activation requires validated capability and explicit architectural approval where needed.
21. M7 dependencies are explicit.
22. Other milestone responsibilities remain separate.
23. Accepted requirements, proposals and empirical assumptions are clearly distinguished.
24. Unresolved architectural and empirical questions are identified.
25. References to Architecture v2 and ADR-005 are consistent.
26. No unsupported claim of actual package-damage detection is introduced.
27. Only the approved documentation file is created or modified.
28. Existing repository quality gates remain passing.
29. Independent Review Agent returns `PASS`.
30. Human Gate approves the deliverable.

## REQUIRED TESTS

This is a documentation-only TASK.

No new automated production tests are required or authorized.

Required verification consists of:

- Reviewing the specification against all acceptance criteria.
- Checking consistency with ADR-005.
- Checking that existing domain contracts remain unchanged.
- Checking that candidate criteria are not presented as validated production behavior.
- Checking that no numerical performance claims have been invented.
- Running the existing project regression suite and quality gates.
- Verifying exact file-level change scope.

Independent Review must inspect the full document rather than relying only on the Implementation Report.

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

Additionally inspect the complete new specification:

```bash
git diff --no-index -- /dev/null docs/domain-inspection-policy.md
```

The final command is an inspection command for a newly created, untracked file. A nonzero exit status indicating differences is expected and is not a validation failure.

If the file is already tracked, use:

```bash
git diff -- docs/domain-inspection-policy.md
```

Inspect all untracked and modified paths.

Report the actual validation results.

Do not bypass failing checks.

## DEPENDENCIES

- TASK-017 completed and integrated.
- M4.A formally closed by Architecture.
- Accepted ADR-005.
- Architecture handoff of 2026-10-23 authorizing M4.B.
- TASK-018 confirmed as the next available task identifier.
- Repository synchronized with the approved integrated baseline.
- Existing Python development and quality-gate environment.

No new package, model artifact, dataset or hardware dependency is authorized.

## BLOCKING CONDITIONS

Stop and escalate with `ARCHITECTURE_DECISION_REQUIRED` if:

- Proposed criteria conflict with ADR-005.
- An additional domain status or reason becomes necessary.
- Existing event or vision contracts require changes.
- The inspection scenario cannot be specified without broadening the approved scope.
- A normative inspection decision depends on evidence unavailable through the established boundary.
- The specification requires an unapproved model capability, registry, rules engine or configuration contract.
- A conclusive outcome must be inferred directly from pretrained COCO detections.
- A proposal cannot be clearly separated from an accepted architectural requirement.
- The specification requires a new binding architectural decision.

Stop and escalate with `TASK_BLOCKED` if:

- Required reference documentation is unavailable.
- The documentation deliverable cannot be completed within the approved scope.
- Existing quality gates fail for causes outside the authorized change set.

Stop and escalate with `HUMAN_DECISION_REQUIRED` if:

- Modifying an unauthorized file is necessary.
- A repository or workflow operation requires human authorization.
- The expected deliverable conflicts with current repository evidence.

Use `RETRY_EXHAUSTED` when the bounded ADS correction loop reaches its configured limit.

Record unresolved empirical questions without fabricating answers.

Do not silently expand scope.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Summarize the inspection specification, candidate criteria, evidence requirements and validation prerequisites.

### TESTS ADDED / UPDATED

State that no automated tests were added or modified because the TASK is documentation-only.

### VALIDATION RESULTS

Report actual validation command results, including documentation inspection and repository hygiene checks.

### DEVIATIONS

List any deviations from TASK-018.

### BLOCKERS

List unresolved blockers or architectural escalations.

### OUT-OF-SCOPE OBSERVATIONS

Record relevant findings without implementing unauthorized changes.

Do not commit, merge, rebase, push, switch to `main`, or modify Git configuration.

Stop after documentation authoring and validation.

Independent Review and Human Gate are separate ADS stages.
