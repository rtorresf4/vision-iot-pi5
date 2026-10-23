# M4.B Domain Inspection Policy Specification

## Status & Scope

- **Milestone:** M4 — Domain Inspection / M4.B — Inspection Decision Policy Specification
- **Status:** Specification Draft (Documentation-Only)
- **Authoritative Reference:** ADR-005 (`docs/adr/005-domain-inspection-contract.md`), Architecture v2 (`docs/architecture.md`), TASK-018
- **Scope:** Defines the intended single-package visible-damage inspection scenario, candidate decision criteria, required model evidence, empirical validation prerequisites, and unresolved architectural or empirical questions.
- **Implementation Status:** Documentation-only increment. No production domain policy, model capability, or contract changes are implemented by this specification.

---

## 1. Requirements Classification Legend

To prevent ambiguity and maintain strict alignment with Architecture v2, every requirement, proposal, and assumption in this specification is categorized using one of three classifications:

1. **[ACCEPTED REQUIREMENT]:** Established and authorized by Architecture v2 or accepted ADRs (e.g., ADR-005 domain inspection contracts, separation of vision inference from domain inspection).
2. **[PROPOSED CRITERION]:** Candidate requirements, categories, or rules intended for architectural review, dataset design, and future policy development but not yet approved for production execution.
3. **[PENDING EMPIRICAL VALIDATION]:** Assumptions, model capability requirements, or performance expectations requiring empirical data, labeled reference datasets, and offline evaluation before activation.

---

## 2. Purpose and Bounded Inspection Scenario

### 2.1 Operational Context
- **[ACCEPTED REQUIREMENT]:** The `vision-iot-pi5` system performs edge-based visual inspection of packages on a production or conveyor line.
- **[ACCEPTED REQUIREMENT]:** The initial Architecture-v2 inspection scenario is strictly bounded to:
  - A fixed camera positioned above or adjacent to the inspection zone.
  - Exactly one target package per inspection cycle.
  - Externally visible package damage.
  - Local inference executed on a Raspberry Pi 5 target hardware environment (or local development/validation host).
  - Synchronous evaluation of an `InferenceResult` into an `InspectionEvent` via project-owned `InspectionLogic`.

### 2.2 Inspection Lifecycle Boundary
- **[ACCEPTED REQUIREMENT]:** Computer vision inference (`InferenceResult`, containing `Detection` bounding boxes and confidence scores) produces project-owned detection representations, not authoritative domain decisions (ADR-005).
- **[ACCEPTED REQUIREMENT]:** Domain inspection logic evaluates an `InferenceResult` to produce an `InspectionEvent` with status `OK`, `DAMAGED`, or `INCONCLUSIVE`.
- **[ACCEPTED REQUIREMENT]:** The current production domain policy is exclusively `UnvalidatedReferenceInspectionLogic`, which evaluates all valid inference results as `INCONCLUSIVE` with reason `UNSUPPORTED_MODEL` and empty evidence `()`.

---

## 3. Target Package and Visibility Assumptions

### 3.1 Package Assumptions
- **[PROPOSED CRITERION]:** The inspected object is a standard corrugated cardboard shipping box or sealed package presented within the fixed camera's field of view.
- **[PENDING EMPIRICAL VALIDATION]:** Packages exhibit bounded orientation variance, consistent scale relative to the frame resolution, and uniform illumination suitable for computer vision feature extraction.

### 3.2 Visibility and Environmental Assumptions
- **[PROPOSED CRITERION]:** The entire primary face of the package intended for inspection is fully visible within the frame during the inspection trigger window.
- **[PENDING EMPIRICAL VALIDATION]:** Occlusion by handling personnel, conveyor hardware, or debris is minimal or absent during active inspection frames.
- **[PENDING EMPIRICAL VALIDATION]:** Background clutter outside the package boundary does not confound localized defect detection.

---

## 4. Candidate Visible-Damage Categories

To prepare for future model training and policy design (M7), candidate defect categories are evaluated below. None of these categories are currently supported by validated model capabilities.

### 4.1 Candidate Category 1: Visible Deformation / Crushing
- **Definition:** Significant structural indentation, corner collapse, or major geometrical distortion of the package envelope.
- **Observable Characteristics:** Asymmetric bounding box geometry, anomalous surface angle transitions, or shadow patterns indicating surface depression.
- **Domain Meaning:** Proposed indicator of envelope distortion; establishing actual internal protection failure requires empirical validation beyond visual surface observation alone (**[PENDING EMPIRICAL VALIDATION]**).
- **Ambiguous Cases:** Natural folds in unsealed flaps, non-standard box designs (e.g., trapezoidal specialty packaging), or optical shadow artifacts.
- **Exclusions:** Minor surface scuffs or printing irregularities that do not alter envelope geometry.
- **Required Model Evidence:** Bounding box localization of deformed regions with calibrated spatial regression.
- **Classification:** **[PROPOSED CRITERION]**.

### 4.2 Candidate Category 2: Tearing, Puncture, or Rupture
- **Definition:** Breaks in the outer linerboard of the corrugated box exposing fluting or internal contents, or open punctures through the package wall.
- **Observable Characteristics:** High-contrast edge discontinuities, irregular dark regions representing voids/tears, or exposed corrugated fluting texture.
- **Domain Meaning:** Proposed indicator of linerboard continuity loss; establishing material integrity loss requires empirical validation beyond visual edge detection alone (**[PENDING EMPIRICAL VALIDATION]**).
- **Ambiguous Cases:** Dark printed graphics, tape adhesive lines, or shipping labels overlapping package edges.
- **Exclusions:** Cleanly cut manufacturer ventilation holes or printed barcode areas.
- **Required Model Evidence:** Accurate bounding box localization enclosing the tear boundary.
- **Classification:** **[PROPOSED CRITERION]**.

### 4.3 Candidate Category 3: Visible Staining / Suspected Moisture Indicators
- **Definition:** Extensive dark discoloration, surface mottling, or irregular contrast patches on the outer linerboard.
- **Observable Characteristics:** Large regional patches of altered reflectance, saturation, or irregular wetting margins.
- **Domain Meaning:** Proposed indicator of surface discoloration; establishing water exposure, substrate softening, or mechanical weakening requires empirical validation beyond visual staining observation alone (**[PENDING EMPIRICAL VALIDATION]**).
- **Ambiguous Cases:** Natural kraft paper shade variations, shadows, or moisture-proof wax coatings.
- **Exclusions:** Standard manufacturer branding or ink stamps.
- **Required Model Evidence:** Segmentation or bounding box localization covering the affected substrate region.
- **Classification:** **[PROPOSED CRITERION]**.

---

## 5. Proposed Package Acceptance Criteria (`OK`)

### 5.1 Acceptance Requirements
- **[PROPOSED CRITERION]:** A package is considered acceptable (`OK`) only when sufficient evidence establishes that the package is present, correctly framed, and free from any approved visible damage categories.
- **[ACCEPTED REQUIREMENT]:** Successful inference execution is **not** sufficient to produce an `OK` decision (ADR-005).
- **[ACCEPTED REQUIREMENT]:** An empty detection set (`evidence = ()`) is **not** sufficient to prove acceptability, because an empty set may arise from a missing package, occlusion, poor lighting, or an unvalidated model.
- **[ACCEPTED REQUIREMENT]:** The absence of validated defect evidence alone does not automatically justify `OK`. Establishing `OK` requires positive evidence of package presence and inspection-region suitability, which remains an unresolved prerequisite.

---

## 6. Required Evidence for `DAMAGED`

### 6.1 Damage Decision Requirements
- **[PROPOSED CRITERION]:** A conclusive `DAMAGED` decision requires:
  1. Positive detection and localization of at least one approved defect category (e.g., tear, crush, puncture) by a validated vision model.
  2. Detection confidence exceeding a validated operational threshold.
  3. Evidence establishing that the detected defect belongs to the target package rather than background infrastructure or adjacent items.
  - Note: `Detection.bounding_box` alone does not provide a validated package-region representation or guarantee package association. Establishing package boundaries and defect-to-package mapping remains an unresolved requirement (**[PENDING EMPIRICAL VALIDATION]**).
  - Evidence tuple (`evidence`) must contain the specific `Detection` objects supporting the damage determination.

---

## 7. Conditions Requiring `INCONCLUSIVE`

### 7.1 Inconclusive Circumstances
- **[ACCEPTED REQUIREMENT]:** An inspection must result in `INCONCLUSIVE` whenever available evidence is insufficient to justify `OK` or `DAMAGED` (ADR-005).
- **[PROPOSED CRITERION]:** Specific triggers for `INCONCLUSIVE` include:
  - Package not reliably identified or centered within the inspection region.
  - Primary inspection surface partially occluded or poorly illuminated.
  - Ambiguous visual evidence where model confidence falls below decision thresholds.
  - Model capabilities not yet validated for the inspection objective (e.g., current COCO reference model).
  - Note: Multi-frame temporal stability or detection sequence evaluation is deferred, as the existing domain contract evaluates a single `InferenceResult` per invocation.

---

## 8. Separation of Inconclusive Inspections and Operational Failures

- **[ACCEPTED REQUIREMENT]:** Inference execution failure (e.g., runtime crash, out-of-memory error, missing model file, camera acquisition timeout) is **not** an `INCONCLUSIVE` inspection (ADR-005).
- **[ACCEPTED REQUIREMENT]:** Operational failures must be handled at the acquisition or application orchestration layer and must never be masked as an inspection result (`OK`, `DAMAGED`, or `INCONCLUSIVE`).

---

## 9. Available Vision Evidence and Current Limitations

### 9.1 Existing Contracts (`InferenceResult` and `Detection`)
- **[ACCEPTED REQUIREMENT]:** The `InferenceResult` contract provides:
  - `frame_id: str`
  - `timestamp: float`
  - `detections: tuple[Detection, ...]`
  - `inference_time_ms: float`
- **[ACCEPTED REQUIREMENT]:** The `Detection` contract provides:
  - `class_id: int`
  - `class_name: str`
  - `confidence: float`
  - `bounding_box: BoundingBox` (`xyxy` format in original frame space)

### 9.2 Current Model Limitations
- **[ACCEPTED REQUIREMENT]:** The initial reference model (`models/yolo26n.onnx`) is a pretrained COCO object detector. It detects general object classes (e.g., persons, vehicles, common items), not package defects.
- **[ACCEPTED REQUIREMENT]:** COCO class names and confidence scores must **not** be interpreted as package damage evidence.
- **[ACCEPTED REQUIREMENT]:** Model outputs from the reference YOLO26n model do not satisfy the evidence requirements for conclusive domain decisions.

---

## 10. Required Specialized Model Capabilities

- **[PROPOSED CRITERION]:** Before a conclusive policy can be implemented, a specialized or fine-tuned model must demonstrate:
  1. **Defect-Specific Taxonomy:** Direct training on approved package-damage classes rather than generic COCO classes.
  2. **Localization Precision:** Reliable bounding-box regression for physical defects (tears, crushing) with quantified IoU accuracy.
  3. **Package Region Association:** Ability to distinguish package boundaries and confirm that localized defect detections belong to the inspected package rather than background infrastructure.
  4. **Generalization:** Robust performance across varied lighting, box textures, and slight orientation changes.
  5. **Inference Latency Bounds:** Execution within acceptable timing constraints on Raspberry Pi 5 hardware (evaluated in M8/M9).

---

## 11. Empirical Validation Prerequisites

- **[PENDING EMPIRICAL VALIDATION]:** Prior to authorizing any future conclusive policy, empirical validation must be performed using:
  - A representative, held-out evaluation dataset containing annotated images of both acceptable packages and damaged packages across all approved categories.
  - Explicit measurement of false acceptance rate (FA) and false rejection rate (FR).
  - Evaluation of model robustness against lighting variations, camera vibration, and background clutter.
- **[ACCEPTED REQUIREMENT]:** Inspection accuracy and computer-vision performance metrics must not be fabricated or assumed without empirical test results.

---

## 12. Future Conclusive-Policy Activation Prerequisites

Activation of a future domain policy capable of emitting `OK` or `DAMAGED` requires:
1. **[ACCEPTED REQUIREMENT]:** Architectural approval of explicit inspection criteria and domain rules.
2. **[PROPOSED CRITERION]:** Completion of dataset collection and model fine-tuning (M7).
3. **[PENDING EMPIRICAL VALIDATION]:** Successful empirical validation of model capabilities, package association accuracy, and error rates.
4. **[ACCEPTED REQUIREMENT]:** Formal ADR update or architecture review if domain contracts require amendment.
5. **[ACCEPTED REQUIREMENT]:** Explicit policy instantiation and selection by the application composition layer (M6), ensuring domain logic remains decoupled from policy selection.

---

## 13. Milestone Relationships and Dependencies

- **M4 (Domain Inspection):** Establishes domain contracts and policy specification (M4.A/M4.B).
- **M5 (Event Distribution):** Responsible for serializing `InspectionEvent` domains into MQTT transport payloads. M4.B does not define MQTT serialization.
- **M6 (Application Composition / Vertical Slice):** Orchestrates frame acquisition, vision inference, domain inspection, and event publishing into a cohesive application runner. M4.B does not implement application wiring.
- **M7 (Dataset and Model Development):** Directly depends on the defect categories and evidence requirements defined in M4.B to guide image collection, annotation, and model training.
- **M8 (Raspberry Pi Deployment):** Validates target hardware performance and deployment packaging. M4.B is platform-independent.
- **M9 (Benchmark and Runtime Selection):** Evaluates inference throughput and latency. M4.B defines inspection logic requirements, not execution benchmarking.

---

## 14. Existing Contract Sufficiency Assessment

- **[PENDING EMPIRICAL VALIDATION]:** The existing domain contracts established in TASK-017 (`InspectionStatus`, `InspectionReason`, `InspectionEvent`, `InspectionLogic`, `InferenceResult`, `Detection`) are assessed as **provisional** and subject to future architectural evaluation. Their sufficiency for all future conclusive policies is not yet an accepted architectural requirement.
- **[ACCEPTED REQUIREMENT]:** The technical ability of `evidence: tuple[Detection, ...]` on `InspectionEvent` to represent defect detections is distinct from the complex evidence required to justify an `OK` decision (which cannot rely on the absence of detections alone).
- **[ACCEPTED REQUIREMENT]:** No contract changes are required or authorized by M4.B.

---

## 15. Unresolved Architectural and Empirical Questions

1. **[PENDING EMPIRICAL VALIDATION]:** What is the minimum required training dataset size and class distribution balance for reliable defect localization on Raspberry Pi 5 hardware?
2. **[PROPOSED CRITERION]:** How should multi-defect frames (e.g., a crushed box with a simultaneous tear) be represented within `InspectionEvent.evidence` and reasoned about by the domain policy?
3. **[PENDING EMPIRICAL VALIDATION]:** What confidence score calibration methods (if any) are required to map raw model confidences to reliable domain inspection thresholds?
4. **[PROPOSED CRITERION]:** How can package boundary identification and defect-to-package association be reliably established using existing detection contracts without introducing a dedicated package-region representation?
5. **[PROPOSED CRITERION]:** Can multi-frame temporal stability or sequence evidence be evaluated under the current synchronous `InspectionLogic.inspect()` interface, or does temporal evaluation require an architectural extension?
6. **[PROPOSED CRITERION]:** Are additional evidence fields required on `InspectionEvent` to justify `OK` decisions explicitly (e.g., package presence confirmation), or is absence of defect evidence combined with framing assumptions sufficient upon empirical validation?

---

## 16. Architecture and ADR References

- `docs/architecture.md` (Architecture v2 Overview)
- `docs/adr/001-vision-task.md` (Supervised Object Detection scope)
- `docs/adr/002-model-strategy.md` (YOLO26n reference model and output semantics)
- `docs/adr/004-vision-contracts.md` (Generic vision contracts: Frame, ModelInput, InferenceResult)
- `docs/adr/005-domain-inspection-contract.md` (Domain inspection contracts and UnvalidatedReferenceInspectionLogic)
- `docs/adr/009-testing-strategy.md` (Multilevel testing strategy)
- `docs/project-context.md` (Project operational checkpoint)
