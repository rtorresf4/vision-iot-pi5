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

### M3.C ONNX InferenceEngine Baseline Decisions
- ONNX Runtime provides the first concrete `InferenceEngine` implementation (`ONNXInferenceEngine`).
- The engine receives an existing local ONNX model artifact explicitly.
- The engine creates, owns, and reuses one ONNX Runtime session initialized during engine instantiation.
- The baseline supports exactly one model input.
- The runtime input name is obtained from session/model metadata rather than becoming part of `ModelInput`.
- Runtime outputs are adapted into the existing ordered `tuple[np.ndarray, ...]` `RawInference.outputs` representation.
- `CPUExecutionProvider` is the baseline execution provider.
- Runtime/model-specific output interpretation is excluded from the engine.

## Consequences
- The production runtime will be selected based on benchmark evidence.
- ONNX and NCNN are not pre-declared as the final winner.
- Runtime-specific output structures remain isolated behind concrete `InferenceEngine` adapters.
