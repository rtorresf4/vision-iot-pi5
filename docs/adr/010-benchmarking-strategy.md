# ADR 010: Benchmarking Strategy

## Status
Accepted

## Context
Performance is key for edge inference.

## Decision
Pipeline benchmarking includes explicit stage timing. Distinguish runtime performance from computer-vision quality (precision/recall/mAP). Benchmark results must include environment/configuration context.

Inference-stage timing is represented at the vision inference boundary by:

    RawInference.inference_time_ms

`inference_time_ms` represents the elapsed inference-engine execution duration in milliseconds for the operation that produced the associated raw outputs. It is a duration, not a wall-clock timestamp.

Other pipeline-stage timings remain separate and must not be accumulated into `RawInference`.

## Consequences
- Performance claims are backed by evidence.
- Allows for informed selection of runtime and model.
- Inference latency has an explicit unit and stage-specific meaning.
