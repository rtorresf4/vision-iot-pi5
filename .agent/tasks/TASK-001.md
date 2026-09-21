# TASK-001 — Materialize Minimal ADS Foundation

## STATUS

READY

## MILESTONE

M0 — Architecture Baseline

## OBJECTIVE

Materialize the minimum repository-level Agent Development System (ADS) v1 foundation required to execute future implementation tasks safely and consistently with Gemini CLI.

This task establishes project-specific agent instructions, implementation rules, review rules, and the reusable TASK contract template.

No application functionality must be implemented or modified.

## WHY

The project architecture and ADS v1 workflow have already been defined and accepted.

Before implementation work begins, the repository needs a minimal, provider-light mechanism that ensures future agents:

- work from explicit TASK contracts,
- respect architecture and scope boundaries,
- protect existing tests,
- validate their work deterministically,
- provide evidence for review,
- escalate decisions they are not authorized to make,
- and preserve human approval as the final integration gate.

This task bootstraps that mechanism.

## ARCHITECTURE REFERENCES

Architecture v2 is the authoritative architectural baseline for the project.

The architecture documentation has not yet been materialized into the repository and will be handled by a later M0 task.

For TASK-001:

- do not invent or redefine project architecture,
- do not create architecture documentation,
- do not create ADRs,
- do not introduce application contracts or domain abstractions.

ADS v1 governance defined by Project Context is authoritative for this task.

## SCOPE

Create the minimum ADS v1 repository structure:

- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `.agent/tasks/TASK-TEMPLATE.md`

### `GEMINI.md`

Must be a thin Gemini CLI bootstrap.

It should direct Gemini to:

1. repository architecture/ADRs when available,
2. the applicable agent rules,
3. the current TASK contract,
4. deterministic validation evidence,
5. human approval as the final integration gate.

It must not duplicate the full architecture or ADS specification.

### Implementation rules

`.agent/rules/implementation.md` must define at minimum:

- execute exactly one TASK at a time,
- inspect relevant repository state before modifying files,
- respect TASK scope and architecture,
- modify only authorized files,
- forbidden changes,
- protection of existing tests,
- dependency discipline,
- deterministic validation,
- evidence/reporting requirements,
- correction-loop behavior,
- handling of out-of-scope observations,
- escalation behavior.

### Review rules

`.agent/rules/review.md` must define at minimum:

- reviewer independence,
- read-only behavior,
- required review inputs,
- review order,
- finding categories,
- finding severities,
- verdicts,
- evidence requirements,
- test-protection checks,
- scope checks,
- architecture checks,
- review report structure.

### TASK template

`.agent/tasks/TASK-TEMPLATE.md` must provide the reusable contract structure defined in ADS v1.

## OUT OF SCOPE

Do not:

- create or modify `src/`,
- refactor application code,
- modify application behavior,
- modify existing tests,
- modify CI,
- modify README,
- create architecture documentation,
- create ADRs,
- introduce Frame, Detection, InferenceResult, InspectionEvent, or other application contracts,
- create orchestration software,
- create persistent agent memory,
- create additional agents,
- introduce dependencies,
- redesign the Git workflow,
- implement automatic task execution.

## INPUTS / CONTRACTS

Authoritative inputs:

1. This TASK contract.
2. ADS v1 decisions supplied by Project Context.
3. Existing repository state.

Future architecture documents referenced by `GEMINI.md` must be treated as authoritative once they exist.

Source-of-truth priority for future agent work:

1. Architecture / ADRs
2. TASK contract
3. Repository contracts and code
4. External evidence when explicitly required
5. Agent reasoning

## EXPECTED OUTPUT

Exactly the minimal ADS foundation necessary for future tasks:

```text
GEMINI.md

.agent/
├── rules/
│   ├── implementation.md
│   └── review.md
└── tasks/
    └── TASK-TEMPLATE.md
```

The existing `TASK-001.md` bootstrap contract is not part of the implementation output and must not be modified by the Implementation Agent.

## ALLOWED CHANGES

The Implementation Agent may create or modify only:

- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `.agent/tasks/TASK-TEMPLATE.md`

No other repository files are authorized.

## FORBIDDEN CHANGES

Do not modify:

- `.agent/tasks/TASK-001.md`
- `apps/`
- `tests/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- `.github/`
- `README.md`
- `pyproject.toml`
- dependency files
- existing application source files
- architecture files or ADRs

Also forbidden:

- adding dependencies,
- weakening or deleting tests,
- changing architecture,
- expanding TASK scope,
- changing acceptance criteria,
- making unrelated refactors,
- hiding validation failures,
- silently resolving architectural or product decisions.

## ACCEPTANCE CRITERIA

1. `GEMINI.md` exists.
2. `.agent/rules/implementation.md` exists.
3. `.agent/rules/review.md` exists.
4. `.agent/tasks/TASK-TEMPLATE.md` exists.
5. `GEMINI.md` remains a thin provider-specific bootstrap and does not duplicate the full architecture or ADS specification.
6. Implementation rules prevent unauthorized scope expansion, architecture changes, dependency changes, test weakening, and silent decision-making.
7. Review rules define the accepted review order, severities, verdicts, and evidence requirements.
8. Reviewer behavior is explicitly read-only.
9. The TASK template contains all required ADS v1 TASK sections.
10. Human approval is explicitly preserved as the final integration gate.
11. All escalation types are represented:
    - `TASK_BLOCKED`
    - `ARCHITECTURE_DECISION_REQUIRED`
    - `HUMAN_DECISION_REQUIRED`
    - `RETRY_EXHAUSTED`
12. Out-of-scope observations are reported rather than implemented.
13. No application code, existing tests, CI, architecture, README, or dependencies are changed.
14. The resulting documentation is concise and practical enough to use during real implementation work.

## REQUIRED TESTS

No application unit tests are required.

Validation for this task is structural and diff-based.

The Implementation Agent must verify:

- only authorized files were changed,
- required files exist,
- no whitespace errors are present,
- no existing tests or application files were modified.

## VALIDATION COMMANDS

At minimum:

```bash
git status --short
git diff --check
git diff
```

Additional read-only inspection commands are allowed when necessary.

The agent must not commit, merge, rebase, force-push, reset the branch, or integrate the task.

## DEPENDENCIES

No new software dependencies.

Prerequisites:

- clean working tree before TASK bootstrap,
- branch `task/001-ads-foundation`,
- accepted ADS v1 specification.

## BLOCKING CONDITIONS

Stop and escalate instead of guessing if:

- this TASK conflicts with repository state,
- architecture must be invented or changed,
- a required change falls outside ALLOWED CHANGES,
- existing tests would need modification,
- a dependency appears necessary,
- acceptance criteria cannot be satisfied without scope expansion,
- an architectural or product decision is required.

Use one of:

- `TASK_BLOCKED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `HUMAN_DECISION_REQUIRED`
- `RETRY_EXHAUSTED`

as appropriate.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Concise description of what was implemented.

### TESTS ADDED / UPDATED

Expected for TASK-001: none.

If any test was modified, this TASK must not be reported as successfully completed.

### VALIDATION RESULTS

Report each validation command and its result.

Do not hide failures.

### DEVIATIONS

Any deviation from this TASK.

Expected value when correctly completed:

`None`

### BLOCKERS

Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS

Relevant observations discovered during implementation that were intentionally not implemented.
