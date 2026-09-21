# ADR 002: Initial Model Strategy

## Status
Accepted

## Context
A starting point for the computer vision model is required, balancing pre-existing knowledge with project-specific customization.

## Decision
The initial reference model is YOLO26n using pretrained weights, followed by project-specific fine-tuning.

## Consequences
- Enables rapid startup using established architecture.
- The model remains replaceable in the future.
- Architecture must not couple project contracts directly to Ultralytics-specific output structures.
