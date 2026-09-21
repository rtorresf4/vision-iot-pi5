# TASK-XXX — [Task Title]

## STATUS

DRAFT / READY / IN_PROGRESS / COMPLETED / BLOCKED / ARCHITECTURE_DECISION_REQUIRED / HUMAN_DECISION_REQUIRED / RETRY_EXHAUSTED

## MILESTONE

[Milestone Name]

## OBJECTIVE

[Concise, high-level description of what this task aims to achieve. State the end goal clearly.]

## WHY

[Context and business/technical justification for why this work is necessary now.]

## ARCHITECTURE REFERENCES

[Link to or reference specific architecture documents, ADRs, or designs that govern this task. Note if no new architecture is being introduced.]

## SCOPE

[Detailed breakdown of the specific requirements, sub-tasks, or logic that must be implemented.]

## OUT OF SCOPE

[Explicit list of what MUST NOT be implemented, modified, or investigated as part of this task.]

## INPUTS / CONTRACTS

[List of authoritative inputs, APIs, interfaces, schemas, or existing codebase files that serve as the foundation or boundary for this task.]

## EXPECTED OUTPUT

[Visual or structural tree of expected files, classes, or outputs to be created or modified.]

## ALLOWED CHANGES

[Strict, exhaustive list of file paths or patterns that the agent is permitted to create or modify. Any changes outside these files are unauthorized.]

## FORBIDDEN CHANGES

[Explicit list of directories, files, or configurations that must NEVER be modified under this task.]

## ACCEPTANCE CRITERIA

[Numbered list of verifiable, concrete criteria that the implementation must satisfy to be deemed complete.]

## REQUIRED TESTS

[Specific unit, integration, or regression tests that must be added or updated to verify the implementation.]

## VALIDATION COMMANDS

[Exact commands that must be run to deterministically validate the implementation (e.g., test runners, linter, type checker).]

```bash
# Add validation commands here
```

## DEPENDENCIES

[Any prerequisite tasks, system packages, or configuration required before this task can be executed.]

## BLOCKING CONDITIONS

[Conditions under which the agent must stop and escalate instead of guessing, including instructions on which escalation code to use (TASK_BLOCKED, ARCHITECTURE_DECISION_REQUIRED, HUMAN_DECISION_REQUIRED, RETRY_EXHAUSTED).]

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS
`COMPLETED` or the appropriate escalation status.

### FILES CHANGED
List every created or modified file.

### IMPLEMENTATION SUMMARY
Concise description of what was implemented.

### TESTS ADDED / UPDATED
List of new or modified tests.

### VALIDATION RESULTS
Report each validation command and its result (including raw output/logs).

### DEVIATIONS
Any deviation from this TASK.

### BLOCKERS
Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS
Relevant observations discovered during implementation that were intentionally not implemented.
