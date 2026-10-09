"""Concrete YOLO26n reference postprocessing implementation."""

from __future__ import annotations

import numpy as np

from vision_iot.hardware import Frame
from vision_iot.vision.contracts import (
    BoundingBox,
    Detection,
    InferenceResult,
    Postprocessor,
    RawInference,
    SpatialMetadata,
)


class YoloPostprocessor(Postprocessor):
    """Concrete reference postprocessor for YOLO26n ONNX outputs (nms=None)."""

    def __init__(
        self,
        class_names: dict[int, str] | list[str],
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
    ) -> None:
        if not isinstance(confidence_threshold, int | float) or not (
            0.0 <= confidence_threshold <= 1.0
        ):
            raise ValueError(
                f"Confidence threshold must be between 0.0 and 1.0, got {confidence_threshold}"
            )
        if not isinstance(iou_threshold, int | float) or not (0.0 <= iou_threshold <= 1.0):
            raise ValueError(f"IoU threshold must be between 0.0 and 1.0, got {iou_threshold}")

        if isinstance(class_names, list):
            if not class_names:
                raise ValueError("Class names list cannot be empty")
            self._class_names = dict(enumerate(class_names))
        elif isinstance(class_names, dict):
            if not class_names:
                raise ValueError("Class names dictionary cannot be empty")
            sorted_keys = sorted(class_names.keys())
            expected_keys = list(range(len(class_names)))
            if sorted_keys != expected_keys:
                raise ValueError(
                    f"Class mapping keys must be contiguous zero-based integers starting from 0, got {sorted_keys}"
                )
            self._class_names = dict(class_names)
        else:
            raise TypeError(f"Expected class_names to be a list or dict, got {type(class_names)}")

        self._nc = len(self._class_names)
        self._confidence_threshold = float(confidence_threshold)
        self._iou_threshold = float(iou_threshold)

    def process(
        self,
        raw_inference: RawInference,
        frame: Frame,
        metadata: SpatialMetadata,
    ) -> InferenceResult:
        """Transform raw inference outputs into InferenceResult using spatial metadata."""
        if len(raw_inference.outputs) != 1:
            raise ValueError(
                f"Expected exactly 1 raw output tensor, got {len(raw_inference.outputs)}"
            )

        output = raw_inference.outputs[0]
        if output.ndim != 3:
            raise ValueError(
                f"Expected raw output tensor to have 3 dimensions (batch, channels, candidates), got {output.ndim}"
            )

        if output.shape[0] != 1:
            raise ValueError(f"Expected batch dimension of 1, got {output.shape[0]}")

        expected_channels = 4 + self._nc
        if output.shape[1] != expected_channels:
            raise ValueError(
                f"Expected exactly {expected_channels} channels (4 box + {self._nc} classes), got {output.shape[1]}"
            )

        if output.shape[2] != 8400:
            raise ValueError(f"Expected 8400 candidates, got {output.shape[2]}")

        # Squeeze batch dimension: shape (4 + nc, 8400)
        tensor = output[0]
        boxes_raw = tensor[:4, :]  # shape (4, 8400)
        scores_raw = tensor[4:, :]  # shape (nc, 8400)

        num_candidates = tensor.shape[1]
        detections_by_class: dict[int, list[tuple[float, BoundingBox]]] = {}

        for i in range(num_candidates):
            candidate_scores = scores_raw[:, i]
            class_id = int(np.argmax(candidate_scores))
            confidence = float(candidate_scores[class_id])

            if confidence < self._confidence_threshold:
                continue

            # Raw box format: xywh in model input space
            cx = float(boxes_raw[0, i])
            cy = float(boxes_raw[1, i])
            w = float(boxes_raw[2, i])
            h = float(boxes_raw[3, i])

            # Convert xywh to model-space xyxy
            x1 = cx - w / 2.0
            y1 = cy - h / 2.0
            x2 = cx + w / 2.0
            y2 = cy + h / 2.0

            model_box = BoundingBox(
                x1=min(x1, x2),
                y1=min(y1, y2),
                x2=max(x1, x2),
                y2=max(y1, y2),
            )

            if class_id not in detections_by_class:
                detections_by_class[class_id] = []
            detections_by_class[class_id].append((confidence, model_box))

        # Apply class-aware NMS in model-input space before coordinate restoration and clipping
        retained_model_detections: list[tuple[int, float, BoundingBox]] = []
        for class_id, class_dets in detections_by_class.items():
            # Sort by confidence descending
            class_dets.sort(key=lambda x: x[0], reverse=True)
            suppressed = [False] * len(class_dets)

            for idx in range(len(class_dets)):
                if suppressed[idx]:
                    continue
                conf_a, box_a = class_dets[idx]
                retained_model_detections.append((class_id, conf_a, box_a))

                for jdx in range(idx + 1, len(class_dets)):
                    if suppressed[jdx]:
                        continue
                    _, box_b = class_dets[jdx]
                    if self._compute_iou(box_a, box_b) > self._iou_threshold:
                        suppressed[jdx] = True

        # Coordinate restoration and clipping for retained model-space detections
        final_detections: list[Detection] = []
        for class_id, conf, model_box in retained_model_detections:
            # Restore coordinates to original frame space using SpatialMetadata
            orig_x1 = (model_box.x1 - metadata.pad_x) / metadata.scale_x
            orig_y1 = (model_box.y1 - metadata.pad_y) / metadata.scale_y
            orig_x2 = (model_box.x2 - metadata.pad_x) / metadata.scale_x
            orig_y2 = (model_box.y2 - metadata.pad_y) / metadata.scale_y

            # Ensure x1 <= x2 and y1 <= y2
            final_x1 = min(orig_x1, orig_x2)
            final_y1 = min(orig_y1, orig_y2)
            final_x2 = max(orig_x1, orig_x2)
            final_y2 = max(orig_y1, orig_y2)

            # Clip to original frame bounds
            final_x1 = max(0.0, min(final_x1, float(metadata.original_width)))
            final_y1 = max(0.0, min(final_y1, float(metadata.original_height)))
            final_x2 = max(0.0, min(final_x2, float(metadata.original_width)))
            final_y2 = max(0.0, min(final_y2, float(metadata.original_height)))

            bbox = BoundingBox(x1=final_x1, y1=final_y1, x2=final_x2, y2=final_y2)
            class_name = self._class_names[class_id]

            final_detections.append(
                Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=conf,
                    bounding_box=bbox,
                )
            )

        # Sort final detections by confidence descending
        final_detections.sort(key=lambda d: d.confidence, reverse=True)

        return InferenceResult(
            frame_id=frame.id,
            timestamp=frame.timestamp,
            detections=tuple(final_detections),
            inference_time_ms=raw_inference.inference_time_ms,
        )

    @staticmethod
    def _compute_iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
        """Compute intersection over union (IoU) between two bounding boxes."""
        inter_x1 = max(box_a.x1, box_b.x1)
        inter_y1 = max(box_a.y1, box_b.y1)
        inter_x2 = min(box_a.x2, box_b.x2)
        inter_y2 = min(box_a.y2, box_b.y2)

        inter_w = max(0.0, inter_x2 - inter_x1)
        inter_h = max(0.0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h

        area_a = max(0.0, box_a.x2 - box_a.x1) * max(0.0, box_a.y2 - box_a.y1)
        area_b = max(0.0, box_b.x2 - box_b.x1) * max(0.0, box_b.y2 - box_b.y1)

        union_area = area_a + area_b - inter_area
        if union_area <= 0.0:
            return 0.0

        return inter_area / union_area
