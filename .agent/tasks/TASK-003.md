# TASK-003 — README Reality Alignment

## STATUS
READY

## MILESTONE
M0 — Architecture Baseline

## OBJECTIVE

Audit and update the repository `README.md` so that it accurately represents the current state of the project.

The README must clearly distinguish between:

- functionality that is currently implemented,
- the accepted Architecture v2 target,
- planned roadmap functionality,
- performance targets that have not yet been benchmarked.

The result must remain useful and attractive as a technical portfolio README without presenting planned or incomplete functionality as already implemented.

---

## WHY

The current repository originated as an early prototype/scaffold and its README may describe intended capabilities as if they were already complete.

Architecture v2 is now materialized in:

- `docs/architecture.md`
- `docs/adr/`

The README must align with both the actual repository state and the accepted architecture.

For a portfolio project, technical credibility is more important than overstating completeness.

---

## ARCHITECTURE REFERENCES

Authoritative architecture sources:

- `docs/architecture.md`
- `docs/adr/README.md`
- `docs/adr/*.md`

ADS governance:

- `GEMINI.md`
- `.agent/rules/implementation.md`

These sources are authoritative and must not be modified by this task.

---

## SCOPE

The Implementation Agent must:

1. Inspect the current `README.md`.
2. Inspect the repository structure and relevant implementation files necessary to determine the actual project state.
3. Compare README claims against:
   - actual implementation,
   - Architecture v2,
   - accepted roadmap.
4. Update `README.md` so that claims are accurate.
5. Preserve a professional portfolio-oriented presentation.
6. Clearly communicate the distinction between current implementation and target architecture.
7. Link or refer readers to `docs/architecture.md` and `docs/adr/` for detailed architectural decisions where appropriate.

The README should provide a useful high-level introduction without duplicating the architecture documentation.

---

## OUT OF SCOPE

This task must NOT:

- implement missing functionality,
- modify application code,
- modify tests,
- modify Architecture v2,
- modify ADRs,
- modify ADS rules,
- modify CI,
- modify deployment configuration,
- add dependencies,
- redesign the project,
- define new architectural decisions,
- fabricate benchmark results,
- fabricate model accuracy results,
- claim hardware validation that has not occurred.

---

## INPUTS / CONTRACTS

### Current architectural baseline

The project is an Edge AI visual inspection portfolio system targeting Raspberry Pi 5.

Accepted target architecture includes:

- fixed-camera package inspection,
- supervised object detection for visible damage,
- local inference,
- Vision / Domain separation,
- runtime-independent inference contracts,
- MQTT event distribution,
- external Streamlit dashboard,
- deterministic testing strategy,
- benchmark-driven runtime selection,
- Raspberry Pi 5 + Linux + virtual environment deployment baseline.

Detailed decisions live in `docs/architecture.md` and `docs/adr/`.

### Current implementation reality

The repository must be inspected directly before editing the README.

Do not assume that an architectural component is implemented merely because it appears in Architecture v2.

Known repository areas that require particular attention include:

- `apps/pi_detector/`
- `apps/streamlit_dashboard/`
- `apps/tools/`
- `apps/sensors/`
- `tests/`
- `training/`
- `deploy/`
- `.github/`

The agent must determine their actual implementation maturity from the repository.

### Truthfulness rules

The README must distinguish language such as:

- **Implemented / Available** — backed by current repository code.
- **Prototype / Partial** — code exists but does not yet satisfy the accepted target architecture.
- **Planned / Target architecture** — accepted design but not yet implemented.
- **Target / Goal** — desired performance or capability not yet demonstrated.

Do not convert targets into measured results.

Do not imply production readiness.

Do not imply successful Raspberry Pi 5 deployment unless supported by repository evidence.

Do not imply measured latency, FPS, accuracy, precision, recall, or mAP unless supported by reproducible benchmark or evaluation evidence.

---

## EXPECTED OUTPUT

Modified:

- `README.md`

Created by the human as task input and not modifiable by the agent:

- `.agent/tasks/TASK-003.md`

No other files should change.

The resulting README should remain concise enough for a GitHub visitor to understand:

1. what the project is,
2. what currently exists,
3. what is still being built,
4. the accepted target architecture,
5. the technology direction,
6. how the project is structured,
7. how to explore the architecture documentation,
8. the roadmap at a useful high level.

---

## ALLOWED CHANGES

The Implementation Agent may modify only:

- `README.md`

The agent may read any repository file required to establish implementation reality.

`.agent/tasks/TASK-003.md` is human-authored task input and must not be modified.

---

## FORBIDDEN CHANGES

The Implementation Agent must not modify:

- `.agent/`
- `GEMINI.md`
- `docs/`
- `apps/`
- `tests/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- `benchmarks/`
- `.github/`
- `pyproject.toml`
- dependency files
- application source code
- configuration files

The agent must not:

- add dependencies,
- change architecture,
- create new architectural decisions,
- implement functionality,
- weaken or delete tests,
- expand task scope,
- modify acceptance criteria,
- fabricate project results,
- present targets as measurements,
- present planned functionality as completed.

---

## ACCEPTANCE CRITERIA

1. `README.md` is the only implementation file modified.
2. The README accurately describes the project's purpose.
3. Current implementation and target architecture are clearly distinguishable.
4. Incomplete or prototype functionality is not presented as complete.
5. Planned functionality is clearly identified as planned, target, or roadmap work.
6. Architecture v2 is represented accurately at a high level.
7. The Vision / Domain separation is not contradicted.
8. The README does not select a final inference runtime before benchmarking.
9. Performance goals are not presented as measured results.
10. Computer-vision quality goals are not presented as measured results.
11. Raspberry Pi 5 deployment is not presented as validated unless repository evidence supports it.
12. The README does not claim production readiness.
13. MQTT and dashboard capabilities are described according to their actual implementation maturity.
14. Existing prototype/scaffold components are described truthfully.
15. Deferred features are not presented as MVP requirements.
16. The README points readers toward the architecture documentation.
17. The README remains suitable for a technical portfolio.
18. The README avoids unnecessary duplication of ADR content.
19. No application code, tests, architecture documents, ADS files, CI, deployment files, or dependencies are modified.
20. No unrelated refactoring or repository cleanup is performed.

---

## REQUIRED TESTS

No application unit tests are required for this documentation-only task.

Validation must verify:

- repository scope,
- README diff,
- consistency with actual repository state,
- consistency with Architecture v2,
- absence of unsupported claims,
- absence of whitespace errors.

---

## VALIDATION COMMANDS

At minimum:

```bash
git status --short
git diff --check
git diff -- README.md
```

The agent must also directly inspect the final `README.md`.

The Implementation Report must explicitly state whether any claims about:

- performance,
- model quality,
- Raspberry Pi deployment,
- production readiness

remain unsupported.

Do not stage, commit, merge, rebase, force-push, reset, or integrate changes.

---

## DEPENDENCIES

- TASK-001 completed and integrated.
- TASK-002 completed and integrated.
- Architecture v2 available in the repository.
- ADS v1 available in the repository.
- Task branch created from clean, human-approved `main`.

No new software dependencies are required.

---

## BLOCKING CONDITIONS

Stop and escalate if:

- repository evidence conflicts with Architecture v2 in a way that requires a new architectural decision,
- determining whether an important README claim is true requires unavailable evidence,
- satisfying the task requires modifying files outside `README.md`,
- satisfying the task requires implementation work,
- an architecture or scope decision is required.

Use the escalation types defined by the ADS:

- `TASK_BLOCKED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `HUMAN_DECISION_REQUIRED`
- `RETRY_EXHAUSTED`

When uncertain about an implementation claim, prefer conservative wording rather than inventing evidence.

---

## DELIVERABLES

Provide the standard Implementation Report containing:

### STATUS
`COMPLETED` or the appropriate escalation status.

### FILES CHANGED
Exact files modified.

### IMPLEMENTATION SUMMARY
Summarize the README corrections and the main categories of claims that were changed.

### TESTS ADDED / UPDATED
Expected: `None`.

### VALIDATION RESULTS
Report all required validation commands and final README inspection.

Explicitly report the result of checking unsupported claims concerning:

- performance,
- model accuracy / CV quality,
- Raspberry Pi 5 deployment,
- production readiness.

### DEVIATIONS
Expected: `None`.

### BLOCKERS
Expected: `None`.

### OUT-OF-SCOPE OBSERVATIONS
Report relevant repository issues discovered during the audit without fixing them.
