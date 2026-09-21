# ADR 007: Execution Model

## Status
Accepted

## Context
Simplicity is paramount to avoid premature complexity.

## Decision
The initial application pipeline is single-process and synchronous. Avoid threads, asyncio, or distributed services unless justified by benchmark evidence.

## Consequences
- Highly predictable and easy to debug.
- Pipeline failures are easily distinguishable.
- Inference failure must not produce a false successful `OK` inspection.
