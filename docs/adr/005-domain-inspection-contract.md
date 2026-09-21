# ADR 005: Domain Inspection Contract

## Status
Accepted

## Context
Inspection decisions must be separated from inference results.

## Decision
Domain layer owns inspection decisions. `InspectionEvent` will be used to report `OK` or `DAMAGED` statuses. Inference failures must never be interpreted as `OK`.

## Consequences
- Clean separation between inference and domain logic.
- Robust handling of inspection outcomes.
