# TASK-005 — Project Context Lifecycle Governance

## STATUS

READY

## MILESTONE

M0 — Architecture Baseline

## OBJECTIVE

Correct the lifecycle governance of the Project Context & Recovery mechanism introduced by TASK-004.

The recovery mechanism must clearly separate:

* durable recovery context, stored in `docs/project-context.md`,
* live execution state, derived from Git and TASK artifacts.

`docs/project-context.md` must remain a lightweight recovery snapshot and must not act as an authoritative workflow-state database.

The ADS rules must define how this recovery snapshot is maintained after integration so that volatile task state is not duplicated unnecessarily.

## WHY

TASK-004 introduced and successfully validated the Project Context & Recovery mechanism.

During its Human Gate and post-integration recovery test, a lifecycle issue was discovered:

`docs/project-context.md` had already been integrated into `main` but still identified TASK-004 as the current task.

This demonstrated that persisting volatile workflow state such as `Current Task` creates two independent representations of execution state:

1. Git / TASK artifacts,
2. the recovery checkpoint.

Those representations can become inconsistent immediately after task integration.

The architectural assessment classified this as:

* ADS governance,
* operational documentation lifecycle,

and not as a change to Architecture v2.

The consolidated decision is:

> `docs/project-context.md` stores durable recovery context; Git and TASK artifacts define live execution state. After integration, Project Context performs a lightweight checkpoint refresh only when the integrated change materially changes the recovery snapshot.

TASK-005 materializes this governance decision.

## ARCHITECTURE REFERENCES

Authoritative architecture:

* `docs/architecture.md`
* `docs/adr/`

ADS governance:

* `GEMINI.md`
* `.agent/rules/implementation.md`
* `.agent/rules/review.md`

Recovery mechanism:

* `docs/project-context.md`

Relevant task history:

* `.agent/tasks/TASK-001.md`
* `.agent/tasks/TASK-002.md`
* `.agent/tasks/TASK-003.md`
* `.agent/tasks/TASK-004.md`

Architecture v2 must not be changed by this task.

No ADR is required.

## GOVERNANCE DECISION

The following decision is authoritative for TASK-005:

### Durable recovery state

`docs/project-context.md` stores information useful for reconstructing project context across AI-assisted development sessions.

It is a recovery snapshot and navigation/index mechanism.

It is not the authoritative source of live workflow execution state.

### Live execution state

Current execution state must be derived from repository evidence, including as applicable:

* Git state,
* Git history,
* TASK artifacts,
* repository contents.

A persisted `Current Task` field in `docs/project-context.md` must not be treated as authoritative live state.

### Recommended future work

The recovery snapshot may identify **Next Recommended Work** when useful.

This represents recovery guidance, not an assertion that a particular TASK is currently active.

### Lifecycle

After task integration, Project Context performs a lightweight checkpoint assessment.

`docs/project-context.md` is refreshed only when the integrated change materially changes information required for future context recovery.

A mechanical update after every TASK is not required.

## SCOPE

The Implementation Agent must:

1. Update `docs/project-context.md` so that it no longer stores `Current Task` as authoritative persisted workflow state.

2. Replace or reformulate `Next Planned Task` so that future work is represented as recovery guidance, for example `Next Recommended Work`, rather than live execution state.

3. Update the Context Recovery Protocol so that determining current execution state explicitly requires inspection of Git and relevant TASK artifacts.

4. Make a minimal ADS governance update defining the lifecycle of `docs/project-context.md`.

5. Establish that after integration a lightweight checkpoint assessment determines whether the recovery snapshot materially changed.

6. Establish that `docs/project-context.md` is updated only when that assessment determines a refresh is necessary.

7. Preserve the repository as the authoritative source of project truth.

8. Preserve the existing Architecture v2 and ADS principles.

## OUT OF SCOPE

This task must NOT:

* change Architecture v2,
* create or modify ADRs,
* implement application functionality,
* modify application code,
* modify tests,
* modify CI/tooling,
* modify dependencies,
* implement baseline tooling or quality gates,
* implement the future technical TASK,
* redesign the Git workflow,
* introduce automated orchestration,
* introduce persistent agent memory,
* create a workflow-state database,
* create scripts for automatically determining the current task,
* rewrite the ADS beyond the minimum lifecycle clarification,
* retroactively rewrite TASK-001 through TASK-004.

## INPUTS / CONTRACTS

The implementation must preserve the following source-of-truth model:

### Architecture

Authoritative:

* `docs/architecture.md`
* `docs/adr/`

### ADS governance

Authoritative:

* `.agent/rules/`

### Task contracts

Authoritative for task-specific execution:

* `.agent/tasks/`

### Live execution state

Derived from repository evidence rather than duplicated into the recovery snapshot.

Relevant evidence includes:

* Git state,
* Git history,
* TASK artifacts,
* repository contents.

### Recovery context

`docs/project-context.md` provides durable context and navigation for new AI-assisted development sessions.

It must defer to the authoritative sources above whenever conflicts exist.

## EXPECTED OUTPUT

Modified:

* `docs/project-context.md`
* the minimum necessary file or files under `.agent/rules/`

Created by the human as task input and immutable during execution:

* `.agent/tasks/TASK-005.md`

No application code or architecture documentation should change.

## ALLOWED CHANGES

The Implementation Agent may modify only:

* `docs/project-context.md`
* `.agent/rules/implementation.md`
* `.agent/rules/review.md`

Only the minimum `.agent/rules/` changes required to materialize the lifecycle decision are authorized.

The Implementation Agent must not modify:

* `.agent/tasks/TASK-005.md`

## FORBIDDEN CHANGES

Do not modify:

* `docs/architecture.md`
* `docs/adr/`
* `GEMINI.md`
* `.agent/tasks/`
* `README.md`
* `apps/`
* `src/`
* `tests/`
* `training/`
* `deploy/`
* `models/`
* `data/`
* `benchmarks/`
* `.github/`
* `pyproject.toml`
* dependency files
* application configuration

Also forbidden:

* adding dependencies,
* changing Architecture v2,
* creating or modifying ADRs,
* implementing baseline tooling,
* changing application behavior,
* weakening or deleting tests,
* expanding TASK scope,
* changing acceptance criteria,
* inventing current repository state,
* making `project-context.md` authoritative over Git or TASK artifacts,
* introducing unnecessary automation.

## ACCEPTANCE CRITERIA

1. `docs/project-context.md` remains a lightweight recovery checkpoint.

2. It explicitly states that it is not the authoritative source of live workflow execution state.

3. `Current Task` is no longer persisted as authoritative state in the recovery snapshot.

4. Current execution state is explicitly derived from Git and relevant TASK artifacts during recovery.

5. Any future-work indication in the recovery snapshot is represented as guidance such as `Next Recommended Work`, not live execution state.

6. The Context Recovery Protocol explicitly requires inspection of Git state.

7. The Context Recovery Protocol explicitly requires inspection of relevant TASK artifacts when determining current execution state.

8. ADS governance defines a post-integration checkpoint assessment.

9. The post-integration assessment determines whether the integrated change materially affects the durable recovery snapshot.

10. `docs/project-context.md` is updated only when the recovery snapshot materially changes.

11. A mechanical `project-context.md` update after every TASK is not required.

12. The governance change does not make Implementation or Review Agents responsible for silently integrating post-task changes.

13. Human approval remains the final integration gate.

14. Repository artifacts remain authoritative according to the established source-of-truth hierarchy.

15. Architecture v2 is unchanged.

16. No ADR is created or modified.

17. TASK-001 through TASK-004 are not retroactively modified.

18. No application code is modified.

19. No tests are modified.

20. No CI/tooling or dependencies are modified.

21. The resulting governance remains concise enough for practical use during AI-assisted development.

22. The resulting recovery protocol can reconstruct live task state without relying on a persisted `Current Task` field.

## REQUIRED TESTS

No application tests are required because this is a governance/documentation task.

Manual consistency validation is required against:

* `docs/project-context.md`,
* `.agent/rules/`,
* `GEMINI.md`,
* Architecture v2,
* TASK-004,
* current Git/repository state.

The final state must demonstrate that a new AI-assisted session can distinguish:

* durable project context,
* live execution state,
* recommended future work.

## VALIDATION COMMANDS

Run at minimum:

```bash
git status --short
git diff --check
git diff -- docs/project-context.md .agent/rules/
```

Additionally inspect the complete final contents of every modified file.

Verify explicitly that:

```bash
grep -n "Current Task" docs/project-context.md
```

does not expose a persisted authoritative `Current Task` field.

Also verify that the recovery protocol contains explicit guidance to inspect Git and relevant TASK artifacts for live execution state.

The Implementation Report must include the actual validation evidence.

## DEPENDENCIES

* TASK-001 completed and integrated.
* TASK-002 completed and integrated.
* TASK-003 completed and integrated.
* TASK-004 implemented, reviewed, human-approved, integrated, and recovery-tested.
* Project Context lifecycle decision consolidated after TASK-004 Human Gate.

No new software dependencies are required.

## BLOCKING CONDITIONS

Stop and escalate if:

* implementing the lifecycle rule requires changing Architecture v2,
* an ADR becomes necessary,
* the governance decision conflicts materially with existing ADS rules,
* satisfying the task requires modifying files outside `ALLOWED CHANGES`,
* live execution state cannot be reconstructed without introducing a new state mechanism,
* acceptance criteria require a broader ADS redesign.

Use the existing ADS escalation types:

* `TASK_BLOCKED`
* `ARCHITECTURE_DECISION_REQUIRED`
* `HUMAN_DECISION_REQUIRED`
* `RETRY_EXHAUSTED`

Do not resolve these conditions by silently expanding the task.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

Exact list of modified files.

### IMPLEMENTATION SUMMARY

Explain:

* how live execution state was separated from durable recovery context,
* how the recovery protocol changed,
* how the post-integration checkpoint lifecycle is represented in ADS governance.

### TESTS ADDED / UPDATED

Expected:

`None`

### VALIDATION RESULTS

Provide actual evidence for every required validation command and direct inspection of modified files.

Explicitly confirm:

* Architecture v2 unchanged,
* ADRs unchanged,
* TASK history unchanged,
* application code/tests unchanged,
* live state is no longer duplicated as authoritative `Current Task` state.

### DEVIATIONS

Expected:

`None`

### BLOCKERS

Expected:

`None`

### OUT-OF-SCOPE OBSERVATIONS

Report relevant observations discovered during implementation without implementing them.
