# ADR 009: Testing Strategy

## Status
Accepted

## Context
High-quality, reliable software requires a comprehensive testing approach.

## Decision
Testing strategy includes unit, contract, integration, and hardware/E2E tests. Focus on deterministic, hardware-independent tests using doubles/fakes. CI is the quality gate.

## Consequences
- Fast, reliable feedback cycle for core logic.
- Well-defined boundaries via contract tests.
- Hardware-dependent tests are isolated.
