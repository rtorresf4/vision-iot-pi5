# ADR 003: Inference Runtime Strategy

## Status
Accepted

## Context
Performance on the Raspberry Pi 5 is critical. A flexible approach to runtime is needed until benchmarks are completed.

## Decision
Define a runtime-agnostic `InferenceEngine` boundary. Use ONNX as the initial portability baseline, with NCNN as an optimized candidate for RPi 5.

Runtime-native output structures must not cross the project-owned `InferenceEngine` boundary. Concrete runtime adapters convert their native outputs into the Architecture-v2 `RawInference.outputs` representation:

    tuple[np.ndarray, ...]

This keeps downstream vision processing independent from ONNX, NCNN, Ultralytics, or other runtime-specific output structures.

## Consequences
- The production runtime will be selected based on benchmark evidence.
- ONNX and NCNN are not pre-declared as the final winner.
- Runtime-specific output structures remain isolated behind concrete `InferenceEngine` adapters.
