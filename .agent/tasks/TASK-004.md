# TASK-004 — Project Context & Recovery

## STATUS
READY

## OBJECTIVE
Create a minimal project-context recovery mechanism that allows a new AI-assisted development session to reconstruct the operational state of `vision-iot-pi5` from the repository without relying on previous chat history.

## WHY
Long AI-assisted development conversations may become impractical or lose historical granularity.

The repository must therefore contain enough durable context for a new session to understand:
- what the project is,
- which sources are authoritative,
- the current milestone and task state,
- the accepted architecture at a high level,
- how the ADS workflow operates,
- relevant known issues and process learnings,
- and how to resume work safely.

The repository remains the source of truth. The recovery document must act as an index and operational checkpoint, not as a duplicate architecture specification.

## ARCHITECTURE REFERENCES
- `docs/architecture.md`
- `docs/adr/`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `GEMINI.md`
- `.agent/tasks/TASK-001.md`
- `.agent/tasks/TASK-002.md`
- `.agent/tasks/TASK-003.md`

## SCOPE
Create:

- `docs/project-context.md`

The document must provide a compact recovery checkpoint containing:

1. Project purpose.
2. Source-of-truth hierarchy.
3. Current project/milestone state.
4. Completed tasks.
5. Current task.
6. Next planned task.
7. Compact Architecture v2 snapshot.
8. Compact ADS workflow summary.
9. Important process learnings discovered during TASK-001 through TASK-003.
10. Known technical debt / repository limitations relevant to future work.
11. A Context Recovery Protocol for a new AI-assisted development session.

## OUT OF SCOPE
- Changing Architecture v2.
- Creating or modifying ADRs.
- Changing ADS rules.
- Modifying application code.
- Modifying tests.
- Modifying CI/tooling.
- Modifying dependencies.
- Implementing TASK-005.
- Creating new architectural abstractions.
- Rewriting existing architecture documentation.
- Attempting to preserve the full chat history.

## INPUTS / CONTRACTS
The new document must be derived from the current repository state and existing authoritative project artifacts.

Architecture details must defer to:
- `docs/architecture.md`
- `docs/adr/`

ADS details must defer to:
- `.agent/rules/`

Task history must defer to:
- `.agent/tasks/`
- Git history where necessary.

The recovery document must not become a competing source of architectural truth.

## EXPECTED OUTPUT
A single new document:

`docs/project-context.md`

It should allow a new AI session to rapidly determine:
- what the project is,
- where authoritative information lives,
- what has already been completed,
- what work is currently active,
- what comes next,
- what known limitations exist,
- and which files must be inspected before continuing development.

## ALLOWED CHANGES
- `docs/project-context.md`

No other repository file may be modified by the Implementation Agent.

`TASK-004.md` is human-authored and immutable during task execution.

## FORBIDDEN CHANGES
The Implementation Agent must not:
- modify `TASK-004.md`,
- modify Architecture or ADRs,
- modify ADS rules,
- modify `GEMINI.md`,
- modify README,
- modify code or tests,
- modify CI or deployment configuration,
- introduce dependencies,
- invent completed work,
- present planned capabilities as implemented,
- duplicate detailed architecture or ADR content unnecessarily.

## ACCEPTANCE CRITERIA
1. `docs/project-context.md` exists.
2. It clearly identifies the repository as the durable source of project truth.
3. It defines the source-of-truth hierarchy.
4. It identifies the current milestone as M0.
5. TASK-001, TASK-002, and TASK-003 are identified as completed.
6. TASK-004 is identified as the current task.
7. Baseline tooling + quality gate is identified as the next planned task.
8. Architecture v2 is summarized without replacing `docs/architecture.md` or the ADRs.
9. The ADS workflow is summarized without replacing `.agent/rules/`.
10. It records that deterministic validation evidence takes precedence over an agent's unsupported claim that validation passed.
11. It records that untracked files require explicit inspection because normal `git diff` does not include them.
12. It records that the lightweight reviewer used during previous tasks did not always respect the required review protocol vocabulary.
13. It records that Human Gate identified issues missed by automated review during TASK-003.
14. It records that architecture escalation was successfully used to resolve ambiguous review findings.
15. It identifies relevant known repository limitations, including placeholder tests and the current non-gating `mypy` CI behavior.
16. Existing pre-Architecture-v2 implementation is not represented as fully conforming to Architecture v2.
17. The existing Streamlit dashboard is represented as prototype/partial rather than a completed Architecture-v2 dashboard.
18. Deferred features are not represented as active implemented capabilities.
19. The document contains a clear Context Recovery Protocol for new AI sessions.
20. The recovery protocol requires inspection of repository/Git state before continuing work.
21. The document does not claim production readiness or unverified performance/model-quality results.
22. Only `docs/project-context.md` is modified by the Implementation Agent.

## REQUIRED TESTS
No software tests are required because this is a documentation/governance task.

Manual consistency review against:
- Architecture v2
- ADRs
- ADS rules
- existing TASK files
- current Git/repository state

is required.

## VALIDATION COMMANDS
Run:

`git status --short`

`git diff --check`

`git diff -- docs/project-context.md`

Additionally inspect the complete final contents of:

`docs/project-context.md`

Because a newly created file may be untracked and therefore absent from normal `git diff`, its contents must be inspected directly before reporting validation success.

## DEPENDENCIES
- TASK-001 completed.
- TASK-002 completed.
- TASK-003 completed and integrated into `main`.

## BLOCKING CONDITIONS
Stop and report `TASK_BLOCKED` if:
- authoritative repository artifacts materially contradict each other,
- the current project state cannot be determined from repository evidence,
- fulfilling the task would require modifying Architecture/ADRs/ADS,
- or additional architectural decisions are required.

Do not resolve such contradictions by inventing a new project decision.

## DELIVERABLES
1. `docs/project-context.md`
2. Implementation Report containing:
   - STATUS
   - FILES CHANGED
   - IMPLEMENTATION SUMMARY
   - TESTS ADDED/UPDATED
   - VALIDATION RESULTS
   - DEVIATIONS
   - BLOCKERS
