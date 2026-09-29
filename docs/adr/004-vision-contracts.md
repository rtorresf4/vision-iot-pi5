# ADR 004: Vision Contracts

## Status
Accepted

## Context
Framework-specific output structures can cause tight coupling and maintenance issues.

## Decision
The project will own stable, internal contracts for vision processing
(`Frame`, `ModelInput`, `SpatialMetadata`, `RawInference`, `Detection`,
`InferenceResult`) rather than exposing framework-specific structures.
Bounding boxes use original-frame coordinates.

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
transformation information for future postprocessing to map model-space
results back into original-frame coordinates.

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

The following output semantics remain intentionally deferred:

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

## Consequences
- Protects layer boundaries.
- Improves maintainability and substitutability of components.
- NumPy provides the project-owned numerical interchange representation at
  the preprocessing and inference boundaries without exposing runtime-native
  structures.
- Spatial transformation metadata is explicit and typed rather than stored in
  an arbitrary metadata dictionary.
- Concrete preprocessing semantics remain deferred until justified by a
  concrete preprocessing/model increment.
- Concrete inference runtimes remain replaceable behind `InferenceEngine`.
