"""Reference vision preprocessing implementation for YOLO reference path (M3.B)."""

from __future__ import annotations

import cv2
import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision.contracts import ModelInput, Preprocessor, SpatialMetadata


class YoloPreprocessor(Preprocessor):
    """Concrete reference preprocessor for YOLO model path using letterbox padding and BGR->RGB conversion."""

    def __init__(self, target_size: int = 640) -> None:
        self.target_size = target_size

    def preprocess(self, frame: Frame) -> ModelInput:
        """Transform an acquired Frame into a ModelInput with YOLO letterboxing, color conversion, normalization, and CHW layout."""
        image = frame.image
        original_height, original_width = image.shape[:2]

        # 1. Color conversion: BGR -> RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 2. Aspect-ratio-preserving resize and letterbox padding
        target = self.target_size
        r = min(target / original_width, target / original_height)
        new_unpad_w = int(round(original_width * r))
        new_unpad_h = int(round(original_height * r))

        dw = target - new_unpad_w
        dh = target - new_unpad_h

        left = dw // 2
        right = dw - left
        top = dh // 2
        bottom = dh - top

        if (original_width, original_height) != (new_unpad_w, new_unpad_h):
            resized = cv2.resize(
                image_rgb, (new_unpad_w, new_unpad_h), interpolation=cv2.INTER_LINEAR
            )
        else:
            resized = image_rgb

        padded = cv2.copyMakeBorder(
            resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )

        # 3. Numerical representation and tensor layout transformation
        # [0, 255] -> [0.0, 1.0], float32, HWC -> CHW, add batch dimension
        data = padded.astype(np.float32) / 255.0
        data = data.transpose(2, 0, 1)
        data = np.expand_dims(data, axis=0)

        # 4. Effective spatial metadata calculation
        metadata = SpatialMetadata(
            original_width=original_width,
            original_height=original_height,
            input_width=target,
            input_height=target,
            scale_x=float(new_unpad_w) / original_width,
            scale_y=float(new_unpad_h) / original_height,
            pad_x=float(left),
            pad_y=float(top),
        )

        return ModelInput(data=data, metadata=metadata)
