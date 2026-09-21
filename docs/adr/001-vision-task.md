# ADR 001: Vision Task

## Status
Accepted

## Context
The system requires a clear scope for the computer vision functionality to remain maintainable and focused.

## Decision
Use supervised object detection with damage localization as the initial vision task.

## Consequences
- The system will detect and localize defects within frames.
- It will not use image-level classification or unsupervised anomaly detection for the MVP.
