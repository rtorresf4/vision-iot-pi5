# ADR 004: Vision Contracts

## Status
Accepted

## Context
Framework-specific output structures can cause tight coupling and maintenance issues.

## Decision
The project will own stable, internal contracts for vision processing (Frame, ModelInput, RawInference, Detection, InferenceResult) rather than exposing framework-specific structures. Bounding boxes use original-frame coordinates.

## Consequences
- Protects layer boundaries.
- Improves maintainability and substitutability of components.
