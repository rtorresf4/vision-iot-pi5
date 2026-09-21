# ADR 006: MQTT Event Contract

## Status
Accepted

## Context
External systems require a standardized way to consume inspection data.

## Decision
Use specific MQTT topics for inspection events and device status. Inspection events use a versioned schema, include `event_id` for deduplication, and follow specific rules (UTC ISO 8601, QoS 1, no image transportation in MQTT).

## Consequences
- Standardized, reliable event distribution.
- Clear separation between telemetry and inspection data.
- Dashboard remains decoupled from inspection pipeline internals.
