# ADR 008: Dashboard

## Status
Accepted

## Context
A dashboard is needed for monitoring, but must not compromise the pipeline.

## Decision
Use Streamlit as an external MQTT consumer. It must not be an architectural dependency of the inspection pipeline.

## Consequences
- Decouples monitoring from critical inference path.
- Clear separation of responsibilities.
- Live video streaming is deferred.
