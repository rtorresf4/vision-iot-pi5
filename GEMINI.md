# Gemini CLI Repository Instructions

Welcome, Gemini CLI! You are working in the `vision-iot-pi5` repository.

## Agent Development System (ADS) v1 Core Guidelines

Before executing any implementation or review tasks in this repository, you must adhere strictly to the following directives:

1. **Authoritative Task Contracts:**
   - Always locate, read, and strictly follow the current active task contract in the `.agent/tasks/` folder (e.g., `.agent/tasks/TASK-XXX.md`).
   - Do not begin any implementation work without an active and approved task contract.

2. **Rules of Engagement:**
   - **Implementation:** For implementing changes, strictly follow the rules in [.agent/rules/implementation.md](.agent/rules/implementation.md).
   - **Review:** For reviewing pull requests, code changes, or task completion, strictly follow the rules in [.agent/rules/review.md](.agent/rules/review.md).

3. **Repository Architecture & ADRs:**
   - Refer to system architecture documentation and Architectural Decision Records (ADRs) when they become available in the repository (e.g., under the `docs/` folder).
   - Do not invent, redefine, or diverge from the established project architecture.

4. **Deterministic Validation:**
   - Every task contract specifies explicit `VALIDATION COMMANDS` and `REQUIRED TESTS`.
   - You must run these commands and ensure they pass before declaring a task complete.
   - All validation output and command results must be documented in the final implementation report.

5. **Human Approval & Integration Gate:**
   - You do not have authority to merge, rebase, force-push, reset, or integrate changes.
   - Your final output must always be an implementation or review report, leaving human approval as the final integration gate.
