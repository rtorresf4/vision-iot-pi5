# ADR 011: Deployment Baseline

## Status
Accepted

## Context
A stable, standard deployment environment is required for RPi 5.

## Decision
Deployment baseline: Raspberry Pi 5, host Linux, Python virtual environment. Docker is excluded from the MVP.

## Consequences
- Simplifies initial deployment setup.
- Models and configuration are managed independently of application code.
- Deployment remains compatible with future systemd-managed services.
