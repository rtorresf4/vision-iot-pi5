# ADR 004: Vision Contracts

## Status
Accepted

## Context
Framework-specific output structures can cause tight coupling and maintenance issues.

## Decision
The project will own stable, internal contracts for vision processing
(`Frame`, `ModelInput`, `SpatialMetadata`, `RawInference`, `BoundingBox`,
`Detection`, `InferenceResult`, `Postprocessor`) rather than exposing
framework-specific structures.

### Frame

`Frame.image` uses a NumPy `ndarray` as the internal acquired-image
representation. Acquisition frames use three-dimensional image-shaped arrays
with `(height, width, channels)` layout. The first two dimensions correspond
to the original acquired-frame dimensions:

- `image.shape[0] == Frame.height`
- `image.shape[1] == Frame.width`

`Frame.width` and `Frame.height` therefore describe the spatial dimensions of
the original acquired frame.

The following `Frame.image` properties remain intentionally deferred until a
subsequent architecture increment demonstrates that they are required:

- color ordering (for example RGB or BGR);
- exact channel count;
- dtype;
- value range;
- normalization;
- memory contiguity;
- mutability;
- ownership and copy semantics.

### ModelInput

`ModelInput` represents numerical model input after preprocessing.

Its stable Architecture-v2 representation is:

    ModelInput
        data: np.ndarray
        metadata: SpatialMetadata

`ModelInput.data` uses a NumPy `ndarray` as the project-owned numerical
interchange representation.

`Frame.image` and `ModelInput.data` are separate contracts. `Frame.image`
represents an acquired raster, while `ModelInput.data` represents numerical
model input prepared by a `Preprocessor`.

The following `ModelInput.data` semantics remain intentionally deferred:

- RGB vs BGR;
- dtype;
- value range;
- normalization;
- NCHW vs NHWC;
- batch semantics;
- exact model input dimensions;
- channel count;
- memory contiguity;
- quantization;
- model-specific tensor semantics.

### SpatialMetadata

`ModelInput.metadata` uses the project-owned `SpatialMetadata` contract:

    SpatialMetadata
        original_width: int
        original_height: int
        input_width: int
        input_height: int
        scale_x: float
        scale_y: float
        pad_x: float
        pad_y: float

The fields represent:

- `original_width` and `original_height`: spatial dimensions of the source
  `Frame` before preprocessing;
- `input_width` and `input_height`: spatial dimensions of the representation
  produced for model input;
- `scale_x` and `scale_y`: spatial scaling applied from original-frame
  coordinates toward model-input coordinates;
- `pad_x` and `pad_y`: spatial padding offset introduced by preprocessing in
  model-input coordinates.

`SpatialMetadata` exists only to preserve enough reversible spatial
transformation information for postprocessing to map model-space results back
into original-frame coordinates.

It must not become a generic metadata container. It does not define or carry:

- RGB/BGR information;
- dtype;
- normalization parameters;
- tensor names;
- model names;
- runtime names;
- YOLO-specific metadata;
- ONNX-specific metadata;
- NCNN-specific metadata;
- confidence thresholds;
- class labels;
- NMS configuration;
- domain inspection information.

### RawInference

`RawInference` represents inference-runtime output before model-specific
postprocessing.

Its stable Architecture-v2 representation is:

    RawInference
        outputs: tuple[np.ndarray, ...]
        inference_time_ms: float

`RawInference.outputs` is an ordered tuple of NumPy `ndarray` values. It
supports one or multiple raw numerical outputs without exposing
runtime-specific output containers.

The following are not generic `RawInference` semantics:

- number of outputs;
- output tensor shapes;
- output dtype;
- output names;
- model-specific output layout;
- detection parsing;
- confidence semantics;
- class semantics;
- bounding-box semantics;
- NMS semantics.

Concrete `InferenceEngine` adapters are responsible for converting
runtime-native output structures into `tuple[np.ndarray, ...]` before those
outputs cross the project-owned inference boundary.

`RawInference.inference_time_ms` represents the elapsed inference-engine
execution duration, in milliseconds, for the operation that produced the
associated outputs. It is a duration, not a wall-clock timestamp.

`RawInference` must remain independent from domain inspection semantics.

### BoundingBox

`BoundingBox` is the project-owned representation of a detected spatial
region.

Its stable Architecture-v2 representation is:

    BoundingBox
        x1: float
        y1: float
        x2: float
        y2: float

The coordinates represent left, top, right, and bottom in original `Frame`
pixel-coordinate space.

The contract uses floating-point coordinates so postprocessing does not
discard precision through premature integer rounding.

The required ordering invariants are:

    x1 <= x2
    y1 <= y2

Bounding boxes crossing the `Postprocessor` boundary must be clipped to the
original Frame bounds:

    0 <= x1 <= original_width
    0 <= x2 <= original_width
    0 <= y1 <= original_height
    0 <= y2 <= original_height

The stable generic representation is original-frame `xyxy` pixel coordinates.

Normalized coordinates, center-based coordinates, and width/height box
representations are not alternative generic Architecture-v2 `BoundingBox`
forms.

### Detection

`Detection` represents one project-owned computer-vision detection.

Its stable Architecture-v2 representation is:

    Detection
        class_id: int
        class_name: str
        confidence: float
        bounding_box: BoundingBox

The fields represent:

- `class_id`: the model/project class identifier represented as an integer;
- `class_name`: the human-readable label associated with `class_id`;
- `confidence`: the confidence assigned to the retained detection by the
  concrete model-specific postprocessor;
- `bounding_box`: the project-owned bounding box in original Frame
  coordinates.

The generic `Detection` contract does not prescribe how every future model
derives its confidence value.

`Detection` is a computer-vision result, not a domain inspection result.

It must not contain:

- inspection status;
- OK/DAMAGED decisions;
- MQTT fields;
- event identifiers;
- runtime/provider information;
- model-tensor coordinates;
- runtime-native objects;
- model-native structures.

### InferenceResult

`InferenceResult` is the project-owned output of the vision subsystem.

Its stable Architecture-v2 representation is:

    InferenceResult
        frame_id: str
        timestamp: float
        detections: tuple[Detection, ...]
        inference_time_ms: float

`frame_id` and `timestamp` preserve correlation with the source `Frame`.

`detections` contains the stable project-owned detections produced by
postprocessing.

`inference_time_ms` preserves the corresponding
`RawInference.inference_time_ms` value. It remains inference-engine execution
time and does not include postprocessing latency.

`InferenceResult` contains vision results only.

It must not contain:

- OK/DAMAGED decisions;
- `InspectionEvent`;
- inspection identifiers;
- MQTT topics or payloads;
- domain defect decisions.

Those responsibilities belong to the domain inspection layer.

### Postprocessor

`Postprocessor` is the synchronous project-owned boundary responsible for
transforming raw model execution results into stable project-owned vision
results.

Its Architecture-v2 boundary is:

    Postprocessor.process(
        raw_inference: RawInference,
        frame: Frame,
        metadata: SpatialMetadata,
    ) -> InferenceResult

The inputs retain separate responsibilities:

- `RawInference` owns runtime outputs and inference timing;
- `Frame` owns frame identity and timestamp;
- `SpatialMetadata` owns reversible preprocessing geometry.

The `Postprocessor` uses the source `Frame` for correlation context only. It
must not modify or reprocess `Frame.image`.

Concrete model-specific postprocessors are responsible for interpreting the
model outputs required to produce the generic project-owned result.

The generic `Postprocessor` contract does not establish:

- model-specific output tensor count;
- model-specific output tensor shape or layout;
- model-specific class-score representation;
- model-specific confidence derivation;
- model-specific NMS behavior;
- runtime-specific output names or structures.

Coordinate restoration from model-output coordinates into original-frame
coordinates belongs to postprocessing.

`SpatialMetadata` is authoritative for reversing the spatial transformation
performed during preprocessing. Postprocessing must not require downstream
domain code to understand resize or letterbox geometry.

`Frame`, `SpatialMetadata`, and `RawInference` remain unchanged by this
contract.

## Consequences
- Protects layer boundaries.
- Improves maintainability and substitutability of components.
- NumPy provides the project-owned numerical interchange representation at
  the preprocessing and inference boundaries without exposing runtime-native
  structures.
- Spatial transformation metadata is explicit and typed rather than stored in
  an arbitrary metadata dictionary.
- Stable computer-vision results use project-owned `BoundingBox`, `Detection`,
  and `InferenceResult` representations.
- Bounding boxes crossing the vision boundary use original-frame `xyxy`
  pixel coordinates.
- Model-specific output interpretation remains isolated behind concrete
  `Postprocessor` implementations.
- Frame correlation, spatial transformation metadata, and raw runtime results
  retain separate ownership rather than being duplicated across contracts.
- Domain inspection semantics remain outside the vision contracts.
- Concrete inference runtimes remain replaceable behind `InferenceEngine`.
- Concrete preprocessing and postprocessing implementations may vary without
  redefining the generic Architecture-v2 contracts.
