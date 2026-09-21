# ADR 003: Inference Runtime Strategy

## Status
Accepted

## Context
Performance on the Raspberry Pi 5 is critical. A flexible approach to runtime is needed until benchmarks are completed.

## Decision
Define a runtime-agnostic `InferenceEngine` boundary. Use ONNX as the initial portability baseline, with NCNN as an optimized candidate for RPi 5.

## Consequences
- The production runtime will be selected based on benchmark evidence.
- ONNX and NCNN are not pre-declared as the final winner.
