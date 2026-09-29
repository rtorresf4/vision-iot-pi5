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
- **Completed Milestones:** M1 (Core Foundation) and M2 (Acquisition).
- **Current Milestone:** M3 (Vision Pipeline).
- **M2 Architecture Status:** Architecturally complete. No additional M2 implementation task is required before M3.
- **Hardware Validation Status:** Physical Raspberry Pi / USB camera validation remains required before making hardware/deployment claims, but it does not block M3 development.
- **Project Repository State:** The repository contains the baseline Architecture-v2 documentation and ADRs, the installable `vision_iot` Python package foundation, the complete M2 acquisition boundary, existing legacy/prototype applications, and CI/CD infrastructure with blocking quality gates covering both `apps` and `src`.

## 3. Task History

- **TASK-001:** Completed.
- **TASK-002:** Completed.
- **TASK-003:** Completed and integrated.
- **TASK-004:** Completed and integrated.
- **TASK-005:** Completed and integrated.
- **TASK-006:** Completed and integrated.
- **TASK-007:** Completed and integrated. Established the Architecture-v2 core Python package foundation and extended the blocking quality gate to `src`.
- **TASK-008:** Completed and integrated. Established the initial M2 acquisition boundary with `Frame`, `FrameSource`, and deterministic `FakeFrameSource`.
- **TASK-009:** Completed and integrated. Corrected the pre-existing Ruff/isort import-sorting conflict by retaining Ruff as the single import-sorting authority.
- **TASK-010:** Completed and integrated. Added the concrete `OpenCVFrameSource`, project-owned `CameraError`, deterministic explicit camera release, and hardware-independent OpenCV acquisition tests while preserving the existing `Frame` and `FrameSource` contracts.
- **TASK-011:** Completed and integrated. Aligned Black, Ruff, and mypy development/pre-commit versions after TASK-010 exposed inconsistent quality-tool versions. Stable validation across local quality gates and pre-commit was restored.
- **Next Recommended Work:** Begin M3 with the Architecture-approved Vision Contract Foundation increment. Materialize the project-owned `Preprocessor`, `ModelInput`, `InferenceEngine`, and `RawInference` contracts before introducing a concrete inference runtime. Live execution state and active task contracts must continue to be derived directly from Git history and `.agent/tasks/`.

## 4. Architecture v2 Snapshot (High-Level)

- Based on `docs/architecture.md` and `docs/adr/`.
- **Core Components:** Vision inference pipeline, MQTT event bus, Streamlit dashboard.
- **Acquisition Boundary:** M2 is architecturally complete. The established acquisition boundary consists of `Frame`, `FrameSource`, deterministic `FakeFrameSource`, concrete `OpenCVFrameSource`, project-owned `CameraError`, and deterministic explicit camera release.
- **Acquisition Isolation:** Concrete OpenCV acquisition is isolated behind the project-owned `FrameSource` boundary. Downstream Architecture-v2 components must not depend directly on `cv2.VideoCapture`.
- **Frame Representation:** `Frame.image` uses a NumPy `ndarray` with a three-dimensional `(height, width, channels)` image-shaped layout. The first two dimensions correspond to `Frame.height` and `Frame.width`. Color ordering, exact channel count, dtype, value range, normalization, model tensor representation, contiguity, mutability, and ownership/copy semantics remain intentionally deferred; ADR-004 is authoritative.
- **Vision Pipeline Transition:** The next Architecture-v2 boundary is `Frame -> Preprocessor -> ModelInput -> InferenceEngine -> RawInference`.
- **M3 Contract Foundation:** The first M3 increment is limited to the project-owned `Preprocessor`, `ModelInput`, `InferenceEngine`, and `RawInference` contracts, with minimal deterministic test doubles where necessary to demonstrate substitutability and composition.
- **Deferred Vision Semantics:** Undefined public representations or semantics for `ModelInput.data`, `ModelInput.metadata`, `RawInference.outputs`, or `RawInference.timing` must not be guessed. If existing authoritative architecture artifacts do not determine a required representation, implementation must stop and escalate to Architecture.
- **Runtime Boundary:** No concrete ONNX, NCNN, TensorFlow/TFLite, Ultralytics, or other inference runtime belongs in the first M3 contract-foundation increment.
- **Deferred Components:** DHT22/PIR sensor integration is deferred.
- **Runtime Strategy:** YOLO26n is the initial reference model; ONNX is the baseline runtime/artifact path; NCNN is an optimized candidate. Production runtime selection is benchmark-driven.
- **Contract-Based Design:** Architecture-v2 uses project-owned stable internal contracts rather than exposing framework-specific structures. Detailed definitions are authoritative in `docs/architecture.md` and ADRs.

## 5. ADS Workflow Summary

- Based on `.agent/rules/`.
- **Workflow:** TASK Contract -> Implementation Agent -> Deterministic Validation -> Review Agent -> bounded correction loop -> Human Gate -> Integration.
- **Gate:** Human approval is required for all integration steps.
- **Rules:** Implementation Agent must strictly follow task contracts, ensure deterministic validation, and not modify out-of-scope files.
- **Architecture Escalation:** Undefined public contract semantics must be escalated rather than inferred from legacy code, framework conventions, current dependencies, or implementation convenience.

## 6. Process Learnings

- **Deterministic Validation:** Evidence of successful command output is mandatory; unsupported agent claims that "validation passed" are insufficient.
- **File Inspection:** New/untracked files must be inspected directly; rely on direct content reading rather than `git diff` alone.
- **Review Protocol:** Independent review must use the required ADS verdict and finding vocabulary defined by `.agent/rules/review.md`.
- **Human Gate:** Automated reviews are not exhaustive; Human Gate has identified implementation scope creep, architecture gaps, and unnecessary API expansion despite green automated validation.
- **Architecture Escalation:** Existing dependencies or implementation convenience do not implicitly authorize a public/internal contract representation. TASK-008 correctly escalated the unresolved `Frame.image` representation, resulting in an explicit ADR-004 decision before implementation proceeded.
- **Validation Artifacts:** Validation commands can generate or modify repository files (observed with setuptools `*.egg-info` and pre-commit auto-fixes); working-tree and staged state must therefore be inspected after validation and before commit.
- **Tooling Stability:** Multiple tools must not hold conflicting responsibility for the same automatic transformation. TASK-009 removed the standalone isort pre-commit hook after a deterministic Ruff/isort import-sorting cycle was reproduced. Ruff remains the single import-sorting authority.
- **Tool Version Alignment:** Local/CI and pre-commit quality-tool versions must not drift into contradictory behavior. TASK-011 aligned Black, Ruff, and mypy versions after TASK-010 exposed a reproducible Ruff formatting/import-sorting disagreement.
- **Environment & Git Configuration:** Agents must not modify local/global/repository Git configuration as a workaround for environment/tooling issues; such issues must be escalated to the human environment owner.
- **Scope Discipline:** When a task exposes a defect outside its authorized scope, preserve the task state, repair the defect through a separately governed task, and then resume the original task on the corrected baseline.
- **Minimal Public API:** Passing tests do not justify unnecessary lifecycle or convenience APIs. TASK-010 removed an unnecessary context-manager API and retained only deterministic explicit camera release required by the architecture.
- **Recovery Safety:** When restoring interrupted task work, preserve a recoverable backup until the restored implementation has passed deterministic validation, independent review, Human Gate, integration, and remote push.

## 7. Known Limitations & Technical Debt

- **Tests:** Test coverage remains intentionally limited to the currently established Architecture-v2 foundations and existing legacy/prototype behavior.
- **Quality Gate:** Black, Ruff, mypy, and pytest are blocking validation gates locally and in CI. Ruff is the single authority for import sorting in the pre-commit workflow, and development/pre-commit quality-tool versions have been aligned.
- **Hardware Validation:** `OpenCVFrameSource` is covered by deterministic hardware-independent tests, but physical Raspberry Pi / USB camera validation remains pending. This does not block M3, but must be completed before relevant hardware/deployment claims are made.
- **Vision Pipeline:** M3 production preprocessing, concrete inference runtime integration, postprocessing, detections, and final inference results are not implemented yet.
- **Implementation Status:** Pre-Architecture-v2 implementation is not fully compliant. The Streamlit dashboard remains in a prototype/partial state, and legacy inference code under `apps/pi_detector/` must not be treated as the authoritative definition of new Architecture-v2 contracts.
- **Deferred Semantics:** Deferred `Frame.image`, `ModelInput`, and `RawInference` semantics must not be inferred or stabilized without authoritative architecture support.
- **Features:** DHT22/PIR integration and other explicitly deferred capabilities remain outside the current milestone.

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
