# ADR 012: Target Repository Structure

## Status
Accepted

## Context
A clear, maintainable repository structure is required to guide future development.

## Decision
Adopt a domain-oriented modular structure (e.g., `src/vision_iot/domain/`, `vision/`, `hardware/`, `infrastructure/`). Migration will be incremental.

## Consequences
- Better separation of concerns.
- Avoids premature over-engineering.
- Guides modular development rather than framework-based structure.
