# Project Context: vision-iot-pi5

This document serves as the durable, lightweight checkpoint for the `vision-iot-pi5` project. Its purpose is to allow a new AI-assisted development session to rapidly reconstruct the operational state of the repository without relying on stale chat history.

**This document is an index and operational checkpoint, not a source of architectural truth.**

**It is not the authoritative source of live workflow execution state. Current execution state must be derived from repository evidence, including Git state, Git history, and relevant TASK artifacts.**

## 1. Source-of-Truth Hierarchy
If any information in this file conflicts with the following, the files listed below take absolute precedence:
1. `docs/architecture.md` and `docs/adr/` (System Architecture)
2. `.agent/rules/` (ADS Workflow)
3. `.agent/tasks/` (Task Contracts)
4. Repository contents (Code, Tests, Documentation)

## 2. Project & Milestone Status
- **Project Purpose:** Vision-based monitoring system for package/box visible-damage inspection using a fixed camera on a Raspberry Pi 5. One package is inspected per cycle.
- **Current Milestone:** M2 (Acquisition), with the first acquisition-foundation increment completed and integrated.
- **Project Repository State:** The repository contains the baseline architecture and ADRs, the Architecture-v2 core Python package foundation under `src/vision_iot`, the first acquisition boundary (`Frame`, `FrameSource`, and `FakeFrameSource`), initial detectors/apps implementation, and CI/CD infrastructure with blocking quality gates covering both `apps` and `src`.

## 3. Task History
- **TASK-001:** Completed.
- **TASK-002:** Completed.
- **TASK-003:** Completed and integrated.
- **TASK-004:** Completed and integrated.
- **TASK-005:** Completed and integrated.
- **TASK-006:** Completed and integrated.
- **TASK-007:** Completed and integrated.
- **TASK-008:** Completed and integrated. Established the first M2 acquisition boundary with `Frame`, `FrameSource`, and deterministic `FakeFrameSource`. No concrete camera adapter was introduced.
- **TASK-009:** Completed and integrated. Corrected a pre-existing quality-gate conflict between Ruff and isort by retaining Ruff as the single import-sorting authority.
- **Next Recommended Work:** Continue M2 planning from Architecture v2 and accepted ADRs. The next acquisition increment must be defined through the architecture/task workflow rather than inferred from this checkpoint. Live execution state and active task contracts must be derived directly from Git history and `.agent/tasks/`.

## 4. Architecture v2 Snapshot (High-Level)
- Based on `docs/architecture.md` and `docs/adr/`.
- **Core Components:** Vision inference pipeline, MQTT event bus, Streamlit dashboard.
- **Acquisition Boundary:** `Frame`, `FrameSource`, and `FakeFrameSource` are established. A concrete camera adapter remains deferred to a subsequent architecture increment.
- **Frame Representation:** `Frame.image` uses a NumPy `ndarray` with a three-dimensional `(height, width, channels)` image-shaped layout. The first two dimensions correspond to `Frame.height` and `Frame.width`. Color ordering, exact channel count, dtype, value range, normalization, model tensor representation, contiguity, mutability, and ownership/copy semantics remain intentionally deferred; ADR-004 is authoritative.
- **Deferred Components:** DHT22/PIR sensor integration is deferred.
- **Runtime Strategy:** YOLO26n is the initial reference model; ONNX is the baseline runtime/artifact path; NCNN is an optimized candidate. Production runtime selection is benchmark-driven.
- **Contract-Based Design:** Architecture-v2 uses project-owned stable internal contracts rather than exposing framework-specific structures. Detailed definitions are authoritative in `docs/architecture.md` and ADRs.

## 5. ADS Workflow Summary
- Based on `.agent/rules/`.
- **Workflow:** TASK Contract -> Implementation Agent -> Deterministic Validation -> Review Agent -> bounded correction loop -> Human Gate -> Integration.
- **Gate:** Human approval is required for all integration steps.
- **Rules:** Implementation Agent must strictly follow task contracts, ensure deterministic validation, and not modify out-of-scope files.

## 6. Process Learnings
- **Deterministic Validation:** Evidence of successful command output is mandatory; unsupported agent claims that "validation passed" are insufficient.
- **File Inspection:** New/untracked files must be inspected directly; rely on direct content reading rather than `git diff`.
- **Review Protocol:** The lightweight reviewer used previously did not always strictly adhere to the required protocol vocabulary.
- **Human Gate:** Automated reviews are not exhaustive; Human Gate has identified both implementation scope creep and architecture gaps despite green automated validation.
- **Architecture Escalation:** Existing dependencies or implementation convenience do not implicitly authorize a public/internal contract representation. TASK-008 correctly escalated the unresolved `Frame.image` representation, resulting in an explicit ADR-004 decision before implementation proceeded.
- **Validation Artifacts:** Validation commands can generate or modify repository files (observed with setuptools `*.egg-info` and pre-commit auto-fixes); working-tree and staged state must therefore be inspected after validation and before commit.
- **Tooling Stability:** Multiple tools must not hold conflicting responsibility for the same automatic transformation. TASK-009 removed the standalone isort pre-commit hook after a deterministic Ruff/isort import-sorting cycle was reproduced. Ruff is now the single import-sorting authority.
- **Environment & Git Configuration:** Agents must not modify local/global/repository Git configuration as a workaround for environment/tooling issues; such issues must be escalated to the human environment owner.
- **Scope Discipline:** When a task exposes a defect outside its authorized scope, preserve the task state, repair the defect through a separately governed task, and then resume the original task on the corrected baseline.

## 7. Known Limitations & Technical Debt
- **Tests:** Test coverage remains intentionally limited to the currently established Architecture-v2 foundations and existing legacy/prototype behavior.
- **Quality Gate:** Black, Ruff, mypy, and pytest are blocking validation gates locally and in CI. Ruff is the single authority for import sorting in the pre-commit workflow.
- **Acquisition:** The acquisition contract and deterministic fake source exist, but no concrete camera adapter is implemented yet.
- **Implementation Status:** Pre-Architecture-v2 implementation is not fully compliant. The Streamlit dashboard is in a prototype/partial state.
- **Features:** Deferred features and deferred `Frame.image` semantics must not be assumed implemented.

## 8. Context Recovery Protocol (New Session)
Before proceeding with any work, a new AI session must reconstruct its environment using the following two-part protocol:

### 8.1 Durable Recovery Context Reconstruction
To restore durable project knowledge, explicitly inspect the following authoritative project artifacts:
1. `docs/project-context.md` (This document)
2. `GEMINI.md`
3. `docs/architecture.md`
4. Relevant `docs/adr/` files
5. `.agent/rules/`

### 8.2 Live Execution-State Reconstruction
To determine the current operational status, explicitly inspect:
1. Git/repository state (e.g., `git status`, `git branch`)
2. Relevant `TASK` artifacts (`.agent/tasks/`)

Use `docs/project-context.md` only as a durable recovery snapshot and navigation/index mechanism. Repository artifacts remain authoritative according to the source-of-truth hierarchy.
