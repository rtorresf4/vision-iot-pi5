"""Vision processing contracts and abstract base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from vision_iot.hardware import Frame


@dataclass
class SpatialMetadata:
    """Represents spatial transformation metadata for reversing preprocessing operations."""

    original_width: int
    original_height: int
    input_width: int
    input_height: int
    scale_x: float
    scale_y: float
    pad_x: float
    pad_y: float


@dataclass
class ModelInput:
    """Represents preprocessed data and reversible spatial metadata for inference."""

    data: np.ndarray
    metadata: SpatialMetadata


@dataclass
class RawInference:
    """Represents raw output and stage timing produced directly by an inference runtime."""

    outputs: tuple[np.ndarray, ...]
    inference_time_ms: float


class Preprocessor(ABC):
    """Abstract base class for transforming acquired Frames into ModelInputs."""

    @abstractmethod
    def preprocess(self, frame: Frame) -> ModelInput:
        """Transform a Frame into ModelInput synchronously."""
        pass


class InferenceEngine(ABC):
    """Abstract base class for executing inference on ModelInputs to produce RawInference."""

    @abstractmethod
    def infer(self, model_input: ModelInput) -> RawInference:
        """Execute inference on ModelInput synchronously and return RawInference."""
        pass
