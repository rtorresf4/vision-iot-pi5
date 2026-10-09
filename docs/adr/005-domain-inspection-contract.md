# ADR 005: Domain Inspection Contract

## Status
Accepted

## Context

Inspection decisions must be separated from computer-vision inference
results.

The vision subsystem produces project-owned `InferenceResult` objects
containing model detections. These detections are numerical and semantic
outputs from a computer-vision model, not authoritative domain inspection
decisions.

The initial reference model is pretrained YOLO26n with COCO classes. Its
successful execution does not establish package-damage detection
capability.

The domain layer must therefore distinguish justified inspection outcomes
from cases where inference has completed but the available evidence is
insufficient.

## Decision

The domain layer owns inspection decisions.

The project-owned inspection outcomes are:

- `OK`
- `DAMAGED`
- `INCONCLUSIVE`

`OK` means sufficient evidence, evaluated under an approved inspection
policy, establishes that the package satisfies the applicable acceptance
criteria.

`DAMAGED` means sufficient evidence, evaluated under an approved
inspection policy, establishes that the package violates an applicable
damage criterion.

`INCONCLUSIVE` means that a valid inference result has been evaluated,
but the available evidence cannot justify `OK` or `DAMAGED`.

An inference execution failure is not an `INCONCLUSIVE` inspection.
Failures must not be interpreted as `OK` and remain a separate
operational concern.

The initial domain representations are:

- `InspectionStatus`
- `InspectionReason`
- `InspectionEvent`
- `InspectionLogic`

`InspectionEvent` contains:

- `inspection_id: str`
- `frame_id: str`
- `timestamp: float`
- `status: InspectionStatus`
- `reason: InspectionReason`
- `evidence: tuple[Detection, ...]`

`inspection_id` is supplied explicitly by the caller.

`frame_id` and `timestamp` preserve the corresponding values from the
originating `InferenceResult`.

`timestamp` refers to the originating Frame timestamp, not the time
at which domain evaluation completes.

`evidence` contains only detections explicitly supporting the domain
inspection decision. Unvalidated model detections are not automatically
promoted to inspection evidence.

`InspectionEvent` is an internal domain representation, independent of
MQTT serialization and transport.

The synchronous domain inspection boundary is:

`InspectionLogic.inspect(InferenceResult, inspection_id) -> InspectionEvent`

The initial concrete reference inspection policy is explicitly selected
for the unvalidated package-damage capability of the pretrained COCO
reference model.

For this policy, every valid `InferenceResult` produces:

- `status = INCONCLUSIVE`
- `reason = UNSUPPORTED_MODEL`
- `evidence = ()`

This behavior is independent of the number of COCO detections and their
confidence values.

The policy must not interpret the absence of detections as evidence of
an undamaged package or infer damage from unrelated COCO classes.

The model's suitability for package-damage inspection is not inferred
from `InferenceResult`. Policy selection belongs to the caller or
future application composition layer.

Future policies capable of emitting `OK` or `DAMAGED` require explicit
domain rules and justified model capability before implementation.

## Consequences

- Preserves separation between vision detections and inspection
  decisions.
- Prevents unsupported `OK` or `DAMAGED` results.
- Distinguishes insufficient evidence from operational inference
  failure.
- Provides stable inspection and Frame correlation.
- Establishes a deterministic domain boundary testable without model
  execution or physical hardware.
- Keeps the internal domain event independent of MQTT transport.
- Allows future evidence-backed inspection policies without changing
  the existing computer-vision contracts.
- Defers package-damage decision rules until the required model
  capabilities and acceptance criteria are established.
