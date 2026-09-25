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
- **Current Milestone:** M1 (Core Foundation).
- **Project Repository State:** The repository contains the baseline architecture, ADRs, the Architecture-v2 core Python package foundation under src/vision_iot, initial detectors/apps implementation, and CI/CD infrastructure with blocking quality gates covering both apps and src.

## 3. Task History
- **TASK-001:** Completed.
- **TASK-002:** Completed.
- **TASK-003:** Completed and integrated.
- **TASK-004:** Completed and integrated.
- **TASK-005:** Completed and integrated.
- **TASK-006:** Completed and integrated.
- **TASK-007:** Completed and integrated.
- **Next Recommended Work:** Plan further M1 tasks from Architecture v2 and accepted ADRs. Live execution state and active task contracts must be derived directly from Git history and `.agent/tasks/`.

## 4. Architecture v2 Snapshot (High-Level)
- Based on `docs/architecture.md` and `docs/adr/`.
- **Core Components:** Vision inference pipeline, MQTT event bus, Streamlit dashboard.
- **Deferred Components:** DHT22/PIR sensor integration is deferred.
- **Runtime Strategy:** YOLO26n is the initial reference model; ONNX is the baseline runtime/artifact path; NCNN is an optimized candidate. Production runtime selection is benchmark-driven.
- **Contract-Based Design:** Established repository/Architecture-v2 contracts; detailed definitions are in `docs/architecture.md` and ADRs.

## 5. ADS Workflow Summary
- Based on `.agent/rules/`.
- **Workflow:** TASK Contract -> Implementation Agent -> Deterministic Validation -> Review Agent -> bounded correction loop -> Human Gate -> Integration.
- **Gate:** Human approval is required for all integration steps.
- **Rules:** Implementation Agent must strictly follow task contracts, ensure deterministic validation, and not modify out-of-scope files.

## 6. Process Learnings
- **Deterministic Validation:** Evidence of successful command output is mandatory; unsupported agent claims that "validation passed" are insufficient.
- **File Inspection:** New/untracked files must be inspected directly; rely on direct content reading rather than `git diff`.
- **Review Protocol:** The lightweight reviewer used previously did not always strictly adhere to the required protocol vocabulary.
- **Human Gate:** Automated reviews are not exhaustive; critical issues were identified by Human Gate during TASK-003.
- **Escalation:** Architectural escalation was successfully used to resolve ambiguous review findings.
- **Validation Artifacts:** Validation commands can generate untracked repository artifacts (observed with setuptools `*.egg-info` after editable installation); therefore working-tree status must be checked after validation.
- **Environment & Git Configuration:** Agents must not modify local/global/repository Git configuration as a workaround for environment/tooling issues; such issues must be escalated to the human environment owner.

## 7. Known Limitations & Technical Debt
- **Tests:** Many tests are currently placeholders.
- **Quality Gate:** Black, Ruff, mypy, and pytest are blocking validation gates locally and in CI.
- **Implementation Status:** Pre-Architecture-v2 implementation is not fully compliant. The Streamlit dashboard is in a prototype/partial state.
- **Features:** Deferred features must not be assumed implemented.

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
