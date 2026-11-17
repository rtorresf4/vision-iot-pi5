# ADR 007: Execution Model

## Status
Accepted

## Context
Simplicity is paramount to avoid premature complexity.

## Decision
The initial application pipeline is single-process and synchronous. Avoid threads, asyncio, or distributed services unless justified by benchmark evidence.

The initial application pipeline remains single-process and synchronous. A concrete infrastructure MQTT client may use one library-managed network-processing thread solely to maintain MQTT protocol traffic and receive connection/publication acknowledgments. The application-facing publisher remains synchronous. This exception does not authorize concurrent inspection processing, application worker pools, asynchronous application orchestration, background delivery queues or generalized retry infrastructure. The MQTT client network thread must have explicit lifecycle ownership and shutdown.

## Consequences
- Highly predictable and easy to debug.
- Pipeline failures are easily distinguishable.
- Inference failure must not produce a false successful `OK` inspection.
