# ADR 004: Vision Contracts

## Status
Accepted

## Context
Framework-specific output structures can cause tight coupling and maintenance issues.

## Decision
The project will own stable, internal contracts for vision processing
(`Frame`, `ModelInput`, `RawInference`, `Detection`, `InferenceResult`) rather
than exposing framework-specific structures. Bounding boxes use original-frame
coordinates.

`Frame.image` uses a NumPy `ndarray` as the internal acquired-image
representation. Acquisition frames use three-dimensional image-shaped arrays
with `(height, width, channels)` layout. The first two dimensions correspond
to the original acquired-frame dimensions:

- `image.shape[0] == Frame.height`
- `image.shape[1] == Frame.width`

`Frame.width` and `Frame.height` therefore describe the spatial dimensions of
the original acquired frame.

The following `Frame.image` properties are intentionally deferred until a
subsequent architecture increment demonstrates that they are required:

- color ordering (for example RGB or BGR);
- exact channel count;
- dtype;
- value range;
- normalization;
- model tensor layout and `ModelInput` representation;
- memory contiguity;
- mutability;
- ownership and copy semantics.

## Consequences
- Protects layer boundaries.
- Improves maintainability and substitutability of components.
