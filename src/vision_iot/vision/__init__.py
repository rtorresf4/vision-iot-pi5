"""Vision processing subsystem contracts."""

from vision_iot.vision.contracts import (
    BoundingBox,
    Detection,
    InferenceEngine,
    InferenceResult,
    ModelInput,
    Postprocessor,
    Preprocessor,
    RawInference,
    SpatialMetadata,
)
from vision_iot.vision.inference_onnx import ONNXInferenceEngine
from vision_iot.vision.postprocessing import YoloPostprocessor
from vision_iot.vision.preprocessing import YoloPreprocessor

__all__ = [
    "SpatialMetadata",
    "ModelInput",
    "RawInference",
    "BoundingBox",
    "Detection",
    "InferenceResult",
    "Preprocessor",
    "InferenceEngine",
    "Postprocessor",
    "YoloPreprocessor",
    "ONNXInferenceEngine",
    "YoloPostprocessor",
]
