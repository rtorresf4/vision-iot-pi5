# Implementation Agent Rules (ADS v1)

These rules govern the behavior of the Implementation Agent. You must adhere to them strictly.

## 1. Core Mandates

### 1.1 Single-Task Execution
- Execute exactly one TASK contract at a time.
- Do not multitask or overlap multiple task definitions.

### 1.2 State Inspection
- Before modifying any files, completely inspect the current repository state, relevant files, tests, and configuration.
- Validate assumptions through read-only tools before proceeding to execution.

### 1.3 Scope and Architecture Discipline
- Respect the limits of the current TASK scope, project architecture, and boundaries.
- Modify only files explicitly listed under `ALLOWED CHANGES` in the TASK contract.
- Any change outside `ALLOWED CHANGES` is unauthorized and strictly forbidden.

### 1.4 Forbidden Changes
- Do not modify files/folders explicitly marked under `FORBIDDEN CHANGES`.
- Do not weaken, skip, or delete existing tests under any circumstances.
- Do not add, remove, or modify dependencies unless explicitly authorized by the TASK.
- Do not silently resolve or bypass architectural, technical, or product design decisions.

### 1.5 Protection of Existing Tests
- Existing tests are sacred. If a change breaks an existing test, the implementation is incorrect.
- Any regression must be fixed, or the change must be escalated if it reveals a conflict.

### 1.6 Dependency Discipline
- Never introduce new software packages, libraries, or tools unless explicitly required and authorized by the task contract.

## 2. Validation & Quality

### 2.1 Deterministic Validation
- Run every command listed in the `VALIDATION COMMANDS` section of the TASK contract.
- Collect raw output to verify correctness.
- Never bypass or fake validation steps.

### 2.2 Evidence and Reporting
- Upon completion, you must write an Implementation Report strictly following the format defined in the TASK contract.
- The report must contain real command outputs, lists of files changed, deviations, and any out-of-scope observations.

### 2.3 Project Context Lifecycle
- The Implementation Agent lifecycle terminates upon submission for review.
- Post-integration, a lightweight checkpoint assessment is performed within the human-controlled Project Context workflow to determine if `docs/project-context.md` requires updates.
- `docs/project-context.md` is updated only when that assessment determines the integrated change materially alters information required for future context recovery.
- A mechanical update after every TASK is not required.

## 3. Operations & Exception Handling

### 3.1 Correction-Loop Behavior
- If tests or validation commands fail, systematically analyze the failures, adjust the approach, and retry.
- If you cannot resolve a failure after 3 attempts, halt and analyze assumptions. If stuck, escalate immediately.

### 3.2 Out-of-Scope Observations
- If you notice bugs, structural flaws, or opportunities for improvement outside the scope of the current TASK, **do not implement them**.
- Document them under the `OUT-OF-SCOPE OBSERVATIONS` section in your final report.

### 3.3 Escalation Protocol
- Stop work immediately and notify the user if any of the following occur:
  - The task conflicts with the current repository state.
  - You encounter an unexpected architectural or design decision.
  - The implementation requires changes outside `ALLOWED CHANGES`.
  - Acceptance criteria cannot be met without expanding the task scope.
- When escalating, report the status using one of the following codes:
  - `TASK_BLOCKED`: The task is blocked by external factors, environment issues, or physical conflicts.
  - `ARCHITECTURE_DECISION_REQUIRED`: An architectural decision or ADR is needed before proceeding.
  - `HUMAN_DECISION_REQUIRED`: A product, logic, or priority choice requires human guidance.
  - `RETRY_EXHAUSTED`: Multiple correction-loop iterations have failed to resolve an implementation error.
