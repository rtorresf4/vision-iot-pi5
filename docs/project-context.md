# Project Context: vision-iot-pi5

This document serves as the durable, lightweight checkpoint for the `vision-iot-pi5` project. Its purpose is to allow a new AI-assisted development session to rapidly reconstruct the operational state of the repository without relying on stale chat history.

**This document is an index and operational checkpoint, not a source of architectural truth.**

## 1. Source-of-Truth Hierarchy
If any information in this file conflicts with the following, the files listed below take absolute precedence:
1. `docs/architecture.md` and `docs/adr/` (System Architecture)
2. `.agent/rules/` (ADS Workflow)
3. `.agent/tasks/` (Task Contracts)
4. Repository contents (Code, Tests, Documentation)

## 2. Project & Milestone Status
- **Project Purpose:** Vision-based monitoring system for package/box visible-damage inspection using a fixed camera on a Raspberry Pi 5. One package is inspected per cycle.
- **Current Milestone:** M0 (Initial Baseline & Infrastructure).
- **Project Repository State:** The repository contains the baseline architecture, ADRs, initial detectors implementation, and CI/CD infrastructure.

## 3. Task History
- **TASK-001:** Completed.
- **TASK-002:** Completed.
- **TASK-003:** Completed and integrated.
- **Current Task:** TASK-004 (Project Context & Recovery).
- **Next Planned Task:** Baseline tooling + quality gate implementation.

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

## 6. Process Learnings (TASK-001 through TASK-003)
- **Deterministic Validation:** Evidence of successful command output is mandatory; unsupported agent claims that "validation passed" are insufficient.
- **File Inspection:** New/untracked files must be inspected directly; rely on direct content reading rather than `git diff`.
- **Review Protocol:** The lightweight reviewer used previously did not always strictly adhere to the required protocol vocabulary.
- **Human Gate:** Automated reviews are not exhaustive; critical issues were identified by Human Gate during TASK-003.
- **Escalation:** Architectural escalation was successfully used to resolve ambiguous review findings.

## 7. Known Limitations & Technical Debt
- **Tests:** Many tests are currently placeholders.
- **CI/CD:** `mypy` is currently configured to be non-gating in CI.
- **Implementation Status:** Pre-Architecture-v2 implementation is not fully compliant. The Streamlit dashboard is in a prototype/partial state.
- **Features:** Deferred features must not be assumed implemented.

## 8. Context Recovery Protocol (New Session)
Before proceeding with any work, a new AI session must explicitly inspect:
1. `docs/project-context.md`
2. `GEMINI.md`
3. `docs/architecture.md`
4. relevant `docs/adr/`
5. `.agent/rules/`
6. the current TASK
7. repository and Git state

The repository artifacts remain authoritative according to the source-of-truth hierarchy.
