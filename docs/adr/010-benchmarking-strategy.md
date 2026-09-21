# ADR 010: Benchmarking Strategy

## Status
Accepted

## Context
Performance is key for edge inference.

## Decision
Pipeline benchmarking includes explicit stage timing. Distinguish runtime performance from computer-vision quality (precision/recall/mAP). Benchmark results must include environment/configuration context.

## Consequences
- Performance claims are backed by evidence.
- Allows for informed selection of runtime and model.
