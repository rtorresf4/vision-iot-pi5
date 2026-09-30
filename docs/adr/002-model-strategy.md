# ADR 002: Initial Model Strategy

## Status
Accepted

## Context

A starting point for the computer vision model is required, balancing
pre-existing knowledge with project-specific customization while preserving
the ability to replace models and inference runtimes independently.

The initial reference path also requires deterministic preprocessing behavior
so that acquired frames can be transformed into model inputs without making
model-specific assumptions part of the generic Architecture-v2 vision
contracts.

The reference model output representation must also be explicit so that
model-specific postprocessing can be implemented deterministically without
inferring tensor semantics from legacy code, framework conventions, or
runtime-specific structures.

## Decision

The initial reference model is YOLO26n using pretrained weights, followed by
project-specific fine-tuning.

For the reference YOLO preprocessing path, the concrete Preprocessor uses the
following behavior:

- preserve the source image aspect ratio during resize;
- apply letterbox padding to reach the configured model-input dimensions;
- use a configurable square model input, with `640x640` as the default
  reference size;
- for the OpenCV reference execution path, convert the acquired image from
  BGR to RGB before model input preparation;
- convert the image data to `float32`;
- scale image values from `[0, 255]` to `[0.0, 1.0]`;
- convert image layout from HWC to CHW;
- add a leading batch dimension;
- produce the reference representation
  `(1, 3, input_height, input_width)`;
- use the conventional YOLO letterbox padding value `114` per image channel;
- populate the existing `SpatialMetadata` contract from the actual spatial
  transformation performed, including the effective resize scale and padding
  offsets.

These preprocessing rules define the concrete initial YOLO reference path.
They do not redefine the generic Architecture-v2 contracts.

In particular:

- `Frame.image` does not universally require BGR ordering;
- `ModelInput` does not universally require `float32`;
- `ModelInput` does not universally require values in `[0.0, 1.0]`;
- `ModelInput` does not universally require CHW layout;
- `ModelInput` does not universally require a batch dimension;
- `ModelInput` does not universally require `640x640` spatial dimensions;
- `ModelInput` does not universally require three channels.

`Frame`, `Preprocessor`, `ModelInput`, and `SpatialMetadata` retain their
existing generic Architecture-v2 contracts.

The reference preprocessing implementation is therefore replaceable without
changing those contracts.

### Reference YOLO26n ONNX Output

The initial YOLO26n ONNX reference artifact uses:

    nms=None

This produces the raw one-to-many detection output and keeps model-specific
postprocessing outside the exported model graph.

The reference output consists of exactly one tensor with shape:

    (N, nc + 4, 8400)

where:

- `N` is the batch dimension;
- `nc` is the number of model classes;
- the first four channels contain bounding-box values;
- the remaining `nc` channels contain one class score per class per candidate;
- `8400` is the candidate dimension for the selected reference representation.

The tensor layout is:

    (batch, channels, candidates)

For the current reference path, preprocessing produces a single-item batch.
This single-item batch behavior is specific to the reference path and is not
a generic `RawInference` invariant.

The first four channels represent bounding boxes as:

    xywh

in model-input coordinate space, where `x` and `y` represent the box center
and `w` and `h` represent box width and height.

The remaining `nc` channels contain the per-class scores for each candidate.
There is no separate objectness channel in the selected reference
representation.

For each candidate, the concrete reference postprocessor determines:

    class_id = argmax(class_scores)
    confidence = max(class_scores)

`class_id` is therefore the zero-based index of the selected class score
within the model class-score vector.

The corresponding human-readable class name is obtained from an explicit
class mapping supplied to the concrete reference postprocessor.

The reference postprocessor must not discover class names implicitly through
the Ultralytics runtime, training YAML, network access, or repository
scanning.

### Reference YOLO26n Postprocessing

Because the selected reference export uses `nms=None`, confidence filtering
and external non-maximum suppression are required.

These operations belong to the concrete `YoloPostprocessor`, not to
`InferenceEngine` or `RawInference`.

The concrete reference postprocessing path is responsible for:

- validating the selected reference raw tensor representation;
- extracting candidate bounding boxes and class scores;
- selecting the predicted class and confidence for each candidate;
- applying the configured confidence threshold;
- converting raw `xywh` boxes into model-space `xyxy` boxes;
- applying class-aware non-maximum suppression;
- restoring coordinates into original-frame space using `SpatialMetadata`;
- clipping restored coordinates to the original Frame bounds;
- mapping retained class IDs to explicitly supplied class names.

The confidence threshold and NMS IoU threshold are concrete reference
postprocessor configuration.

Class-aware NMS must not suppress detections belonging to different predicted
classes solely because their boxes overlap.

For clarity and efficiency, reference NMS operates in model-input coordinate
space before coordinate restoration.

The concrete postprocessor restores model-space coordinates using the
effective transformation recorded in `SpatialMetadata`. It must not recompute
theoretical preprocessing geometry.

These output and postprocessing semantics apply only to the initial YOLO26n
ONNX reference path.

They do not establish generic `RawInference` invariants. In particular, the
generic Architecture-v2 contracts do not require:

- exactly one output tensor;
- shape `(N, nc + 4, 8400)`;
- `(batch, channels, candidates)` layout;
- `xywh` raw bounding boxes;
- `8400` candidates;
- YOLO class-score semantics;
- absence of a separate objectness value;
- confidence filtering;
- external NMS.

The model also remains independent from the inference runtime. Runtime
selection and integration are governed separately and are not defined by this
ADR.

## Consequences

- Enables rapid startup using an established object-detection architecture.
- Provides deterministic preprocessing behavior for the initial reference
  model path.
- Establishes deterministic output semantics for the initial YOLO26n ONNX
  reference artifact.
- Keeps inference execution separate from model-specific postprocessing.
- Keeps confidence filtering, class-aware NMS, and coordinate restoration
  independently testable using synthetic numerical inputs.
- Enables preprocessing and postprocessing to be tested independently from
  model execution and physical hardware.
- Preserves the distinction between acquired-frame representation and
  model-input representation.
- Preserves model replaceability because reference-model preprocessing and
  postprocessing semantics are not promoted to generic contract invariants.
- Preserves runtime replaceability because preprocessing and postprocessing do
  not depend on a concrete inference engine.
- `SpatialMetadata` must describe the spatial transformation actually
  performed rather than assumed target geometry.
- Alternative models may provide different concrete `Preprocessor` and
  `Postprocessor` implementations while continuing to satisfy the same
  generic Architecture-v2 boundaries.
- Architecture must not couple project contracts directly to
  Ultralytics-specific input or output structures.
- A future change to the reference YOLO26n export representation requires
  architecture reassessment before it replaces the selected `nms=None`
  baseline.
