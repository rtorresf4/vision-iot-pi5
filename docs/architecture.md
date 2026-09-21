# Architecture v2: vision-iot-pi5

## System Purpose and Scenario
`vision-iot-pi5` is an Edge AI visual inspection system designed as a portfolio-quality implementation.
Initial scenario: fixed camera, single package inspection, visible damage detection (supervised object detection), generic `damage` detection, local inference on Raspberry Pi 5.

## Architectural Principles
- **Separation of Concerns:** Rigidly enforced via layered architecture.
- **Contract-Based:** Stable project-owned contracts protect layer boundaries.
- **Simplicity:** Single-process, synchronous pipeline by default.
- **Benchmark-Driven:** Inference runtime and performance tuning guided by empirical evidence.
- **Maintainability:** Modular, evolvable structure with clear ADR documentation.

## Layered Architecture
1. **Hardware:** Frame acquisition, physical-device interaction.
2. **Vision:** Preprocessing, model execution, postprocessing.
3. **Domain:** Inspection logic, business rules (`OK`/`DAMAGED` decisions).
4. **Infrastructure:** External communication (MQTT), integrations.

See ADRs for detailed rationale.

## Main Processing Flow
```text
FrameSource -> Preprocessor -> InferenceEngine -> Postprocessor -> InferenceResult -> InspectionLogic -> InspectionEvent -> EventPublisher -> MQTT -> Dashboard / Consumers
```
The dashboard is an external consumer, not part of the critical inference path.

## Dependencies and Boundaries
- Dependencies flow inwards/downwards (Hardware -> Vision -> Domain -> Infrastructure).
- Project-owned stable contracts (Frame, ModelInput, RawInference, Detection, InferenceResult, InspectionEvent) define boundary interfaces.
- MQTT acts as the integration boundary for external consumers.

## Strategy and Baseline
- **Testing:** Multilevel (Unit, Contract, Integration, H/W). Focus on deterministic, hardware-independent tests.
- **Benchmarking:** Explicit stage-timing. Distinguishes runtime performance from computer-vision quality.
- **Deployment:** Raspberry Pi 5, host Linux, Python virtual environment. No Docker in MVP.

## Repository Structure
Target structure is modularized by domain, not framework:
`src/vision_iot/` containing `application/`, `domain/`, `vision/`, `hardware/`, `infrastructure/`, `config/`.
See ADR-012 for the full plan.

## Implementation Milestones
- M0 — Architecture Baseline
- M1 — Core Foundation
- M2 — Acquisition
- M3 — Vision Pipeline
- M4 — Domain Inspection
- M5 — Event Distribution
- M6 — Vertical Slice
- M7 — Dataset / Training
- M8 — Raspberry Pi Deployment
- M9 — Benchmark and Runtime Selection
- M10 — Portfolio Hardening

## Explicitly Deferred Capabilities
- DHT22/PIR integration, cloud integration, Docker/K8s, microservices, concurrency, live video streaming, complex persistence, fleet management, OTA, React frontend, multiclass taxonomy.

---
See [ADR index](adr/README.md) for detailed Architecture Decision Records.
