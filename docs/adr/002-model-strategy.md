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

The model also remains independent from the inference runtime. Runtime
selection and integration are governed separately and are not defined by this
ADR.

## Consequences

- Enables rapid startup using an established object-detection architecture.
- Provides deterministic preprocessing behavior for the initial reference
  model path.
- Enables preprocessing to be tested independently from model execution and
  physical hardware.
- Preserves the distinction between acquired-frame representation and
  model-input representation.
- Preserves model replaceability because reference-model preprocessing
  semantics are not promoted to generic `ModelInput` invariants.
- Preserves runtime replaceability because preprocessing does not depend on a
  concrete inference engine.
- `SpatialMetadata` must describe the spatial transformation actually
  performed rather than assumed target geometry.
- Alternative models may provide different concrete `Preprocessor`
  implementations while continuing to satisfy the same generic
  `Preprocessor -> ModelInput` boundary.
- Architecture must not couple project contracts directly to
  Ultralytics-specific input or output structures.
