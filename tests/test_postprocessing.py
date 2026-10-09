"""Tests for YoloPostprocessor (TASK-015)."""

from __future__ import annotations

import numpy as np
import pytest

from vision_iot.hardware import Frame
from vision_iot.vision import (
    InferenceResult,
    RawInference,
    SpatialMetadata,
    YoloPostprocessor,
)


def _create_synthetic_raw_inference(
    tensor: np.ndarray, inference_time_ms: float = 15.0
) -> RawInference:
    return RawInference(outputs=(tensor,), inference_time_ms=inference_time_ms)


def _create_synthetic_frame(
    image: np.ndarray | None = None,
    frame_id: str = "frame-test-001",
    timestamp: float = 1700000000.0,
) -> Frame:
    if image is None:
        image = np.zeros((480, 640, 3), dtype=np.uint8)
    return Frame(
        id=frame_id,
        timestamp=timestamp,
        image=image,
        width=image.shape[1],
        height=image.shape[0],
    )


def test_no_retained_candidates() -> None:
    """1. Test no retained candidates when all confidences are below threshold."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # Set all class scores very low (e.g., 0.0)
    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["object"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert isinstance(result, InferenceResult)
    assert len(result.detections) == 0


def test_one_valid_candidate() -> None:
    """2. Test one valid candidate above confidence threshold."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # Candidate 0: box [100, 100, 50, 50] (xywh), score 0.9 for class 0
    tensor[0, 0, 0] = 100.0  # cx
    tensor[0, 1, 0] = 100.0  # cy
    tensor[0, 2, 0] = 50.0  # w
    tensor[0, 3, 0] = 50.0  # h
    tensor[0, 4, 0] = 0.9  # class 0 score

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["item"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    det = result.detections[0]
    assert det.class_id == 0
    assert det.class_name == "item"
    assert det.confidence == pytest.approx(0.9)
    assert det.bounding_box.x1 == pytest.approx(75.0)
    assert det.bounding_box.y1 == pytest.approx(75.0)
    assert det.bounding_box.x2 == pytest.approx(125.0)
    assert det.bounding_box.y2 == pytest.approx(125.0)


def test_confidence_below_threshold() -> None:
    """3. Test candidate with confidence below threshold is filtered out."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 50.0
    tensor[0, 3, 0] = 50.0
    tensor[0, 4, 0] = 0.4  # Below threshold 0.5

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["item"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 0


def test_class_selection() -> None:
    """4. Test class selection via argmax across multiple classes."""
    # 2 classes: nc = 2 -> channels = 4 + 2 = 6
    tensor = np.zeros((1, 6, 8400), dtype=np.float32)
    tensor[0, 0, 10] = 200.0
    tensor[0, 1, 10] = 200.0
    tensor[0, 2, 10] = 40.0
    tensor[0, 3, 10] = 40.0
    tensor[0, 4, 10] = 0.2  # class 0 score
    tensor[0, 5, 10] = 0.85  # class 1 score (max)

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["cat", "dog"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    det = result.detections[0]
    assert det.class_id == 1
    assert det.class_name == "dog"
    assert det.confidence == pytest.approx(0.85)


def test_multiple_classes() -> None:
    """5. Test detection of multiple distinct classes."""
    tensor = np.zeros((1, 6, 8400), dtype=np.float32)
    # Candidate 0: class 0
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 30.0
    tensor[0, 3, 0] = 30.0
    tensor[0, 4, 0] = 0.9  # class 0
    tensor[0, 5, 0] = 0.1

    # Candidate 1: class 1
    tensor[0, 0, 1] = 300.0
    tensor[0, 1, 1] = 300.0
    tensor[0, 2, 1] = 40.0
    tensor[0, 3, 1] = 40.0
    tensor[0, 4, 1] = 0.1
    tensor[0, 5, 1] = 0.8  # class 1

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["classA", "classB"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 2
    class_names = {d.class_name for d in result.detections}
    assert class_names == {"classA", "classB"}


def test_xywh_to_xyxy_conversion() -> None:
    """6. Test xywh to xyxy bounding-box conversion."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # cx=100, cy=200, w=40, h=60 -> x1=80, y1=170, x2=120, y2=230
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 200.0
    tensor[0, 2, 0] = 40.0
    tensor[0, 3, 0] = 60.0
    tensor[0, 4, 0] = 0.95

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["box"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    assert box.x1 == pytest.approx(80.0)
    assert box.y1 == pytest.approx(170.0)
    assert box.x2 == pytest.approx(120.0)
    assert box.y2 == pytest.approx(230.0)


def test_same_class_nms_suppression() -> None:
    """7. Test overlapping same-class boxes are suppressed according to IoU threshold."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # Box 1: high confidence (0.95)
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 50.0
    tensor[0, 3, 0] = 50.0
    tensor[0, 4, 0] = 0.95

    # Box 2: heavily overlapping, lower confidence (0.80)
    tensor[0, 0, 1] = 105.0
    tensor[0, 1, 1] = 105.0
    tensor[0, 2, 1] = 50.0
    tensor[0, 3, 1] = 50.0
    tensor[0, 4, 1] = 0.80

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(
        class_names=["target"], confidence_threshold=0.5, iou_threshold=0.45
    )
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    assert result.detections[0].confidence == pytest.approx(0.95)


def test_cross_class_nms_independence() -> None:
    """8. Test overlapping different-class boxes are not cross-class suppressed."""
    tensor = np.zeros((1, 6, 8400), dtype=np.float32)
    # Box 1: class 0, confidence 0.9
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 50.0
    tensor[0, 3, 0] = 50.0
    tensor[0, 4, 0] = 0.90
    tensor[0, 5, 0] = 0.10

    # Box 2: identical coordinates, class 1, confidence 0.95
    tensor[0, 0, 1] = 100.0
    tensor[0, 1, 1] = 100.0
    tensor[0, 2, 1] = 50.0
    tensor[0, 3, 1] = 50.0
    tensor[0, 4, 1] = 0.10
    tensor[0, 5, 1] = 0.95

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(
        class_names=["clsA", "clsB"], confidence_threshold=0.5, iou_threshold=0.45
    )
    result = postprocessor.process(raw_inf, frame, metadata)

    # Both should be retained because they belong to different classes
    assert len(result.detections) == 2
    classes = {d.class_name for d in result.detections}
    assert classes == {"clsA", "clsB"}


def test_coordinate_restoration_no_padding() -> None:
    """9. Test coordinate restoration with scale=1.0 and no padding."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 200.0
    tensor[0, 1, 0] = 150.0
    tensor[0, 2, 0] = 100.0
    tensor[0, 3, 0] = 80.0
    tensor[0, 4, 0] = 0.9

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(
        original_width=640,
        original_height=480,
        input_width=640,
        input_height=640,
        scale_x=1.0,
        scale_y=1.0,
        pad_x=0.0,
        pad_y=0.0,
    )

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    # model space: x1=150, y1=110, x2=250, y2=190
    assert box.x1 == pytest.approx(150.0)
    assert box.y1 == pytest.approx(110.0)
    assert box.x2 == pytest.approx(250.0)
    assert box.y2 == pytest.approx(190.0)


def test_coordinate_restoration_vertical_padding() -> None:
    """10. Test coordinate restoration with vertical letterbox padding."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 320.0
    tensor[0, 1, 0] = 320.0
    tensor[0, 2, 0] = 200.0
    tensor[0, 3, 0] = 200.0
    tensor[0, 4, 0] = 0.9

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    # scale_x = 0.5, scale_y = 0.5, pad_x = 0.0, pad_y = 80.0
    metadata = SpatialMetadata(
        original_width=640,
        original_height=640,
        input_width=640,
        input_height=640,
        scale_x=0.5,
        scale_y=0.5,
        pad_x=0.0,
        pad_y=80.0,
    )

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    # model box: x1=220, y1=220, x2=420, y2=420
    # orig_x1 = (220 - 0) / 0.5 = 440
    # orig_y1 = (220 - 80) / 0.5 = 280
    assert box.x1 == pytest.approx(440.0)
    assert box.y1 == pytest.approx(280.0)


def test_coordinate_restoration_horizontal_padding() -> None:
    """11. Test coordinate restoration with horizontal letterbox padding."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 320.0
    tensor[0, 1, 0] = 320.0
    tensor[0, 2, 0] = 200.0
    tensor[0, 3, 0] = 200.0
    tensor[0, 4, 0] = 0.9

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    # scale_x = 0.5, scale_y = 0.5, pad_x = 80.0, pad_y = 0.0
    metadata = SpatialMetadata(
        original_width=640,
        original_height=640,
        input_width=640,
        input_height=640,
        scale_x=0.5,
        scale_y=0.5,
        pad_x=80.0,
        pad_y=0.0,
    )

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    # orig_x1 = (220 - 80) / 0.5 = 280
    # orig_y1 = (220 - 0) / 0.5 = 440
    assert box.x1 == pytest.approx(280.0)
    assert box.y1 == pytest.approx(440.0)


def test_restoration_integer_rounded_geometry() -> None:
    """12. Test restoration using effective integer-rounded preprocessing geometry."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 40.0
    tensor[0, 3, 0] = 40.0
    tensor[0, 4, 0] = 0.95

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(
        original_width=1000,
        original_height=750,
        input_width=640,
        input_height=640,
        scale_x=0.64,
        scale_y=0.64,
        pad_x=0.0,
        pad_y=64.0,
    )

    postprocessor = YoloPostprocessor(class_names=["item"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    # model: x1=80, y1=80, x2=120, y2=120
    # orig_x1 = 80 / 0.64 = 125.0
    # orig_y1 = (80 - 64) / 0.64 = 25.0
    assert box.x1 == pytest.approx(125.0)
    assert box.y1 == pytest.approx(25.0)


def test_clipping_to_original_frame_bounds() -> None:
    """13. Test clipping final coordinates to original frame bounds."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # Box extending outside image bounds
    tensor[0, 0, 0] = 320.0
    tensor[0, 1, 0] = 320.0
    tensor[0, 2, 0] = 800.0
    tensor[0, 3, 0] = 800.0
    tensor[0, 4, 0] = 0.99

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()  # 640x480
    metadata = SpatialMetadata(
        original_width=640,
        original_height=480,
        input_width=640,
        input_height=640,
        scale_x=1.0,
        scale_y=1.0,
        pad_x=0.0,
        pad_y=0.0,
    )

    postprocessor = YoloPostprocessor(class_names=["item"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert len(result.detections) == 1
    box = result.detections[0].bounding_box
    assert box.x1 >= 0.0
    assert box.y1 >= 0.0
    assert box.x2 <= 640.0
    assert box.y2 <= 480.0


def test_frame_id_propagation() -> None:
    """14. Test frame ID is propagated correctly to InferenceResult."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame(frame_id="custom-frame-id-999")
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert result.frame_id == "custom-frame-id-999"


def test_frame_timestamp_propagation() -> None:
    """15. Test frame timestamp is propagated correctly to InferenceResult."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame(timestamp=1699999999.5)
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert result.timestamp == 1699999999.5


def test_inference_time_propagation_unchanged() -> None:
    """16. Test inference_time_ms is propagated unchanged."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    raw_inf = _create_synthetic_raw_inference(tensor, inference_time_ms=23.45)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    result = postprocessor.process(raw_inf, frame, metadata)

    assert result.inference_time_ms == 23.45


def test_invalid_output_count_fails() -> None:
    """17. Test invalid output count (not 1) raises ValueError."""
    raw_inf = RawInference(outputs=(), inference_time_ms=10.0)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"])
    with pytest.raises(ValueError, match="Expected exactly 1 raw output tensor"):
        postprocessor.process(raw_inf, frame, metadata)


def test_incompatible_output_shape_fails() -> None:
    """18. Test incompatible output tensor shape/layout raises ValueError."""
    # Wrong dimensions (2D instead of 3D)
    bad_tensor = np.zeros((5, 8400), dtype=np.float32)
    raw_inf = RawInference(outputs=(bad_tensor,), inference_time_ms=10.0)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"])
    with pytest.raises(ValueError, match="3 dimensions"):
        postprocessor.process(raw_inf, frame, metadata)


def test_class_mapping_applied_correctly() -> None:
    """19. Test class mapping (dict and list) is applied correctly."""
    tensor = np.zeros((1, 6, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 40.0
    tensor[0, 3, 0] = 40.0
    tensor[0, 4, 0] = 0.1
    tensor[0, 5, 0] = 0.9  # class 1

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    # Test list mapping
    postprocessor_list = YoloPostprocessor(class_names=["zero", "one"], confidence_threshold=0.5)
    res_list = postprocessor_list.process(raw_inf, frame, metadata)
    assert res_list.detections[0].class_name == "one"

    # Test dict mapping
    postprocessor_dict = YoloPostprocessor(
        class_names={0: "zero", 1: "custom_one"}, confidence_threshold=0.5
    )
    res_dict = postprocessor_dict.process(raw_inf, frame, metadata)
    assert res_dict.detections[0].class_name == "custom_one"


def test_source_frame_image_not_modified() -> None:
    """20. Test source Frame.image is not modified or reprocessed during postprocessing."""
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    tensor[0, 0, 0] = 100.0
    tensor[0, 1, 0] = 100.0
    tensor[0, 2, 0] = 40.0
    tensor[0, 3, 0] = 40.0
    tensor[0, 4, 0] = 0.9

    raw_inf = _create_synthetic_raw_inference(tensor)
    original_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    image_copy = original_image.copy()
    frame = Frame(id="f-img", timestamp=100.0, image=original_image, width=640, height=480)
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["obj"], confidence_threshold=0.5)
    postprocessor.process(raw_inf, frame, metadata)

    np.testing.assert_array_equal(frame.image, image_copy)


def test_invalid_tensor_channels() -> None:
    """21. Test that tensor with channel count not matching 4 + nc raises ValueError."""
    # 2 classes -> expected 4 + 2 = 6 channels. Supply 5 channels.
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame()
    metadata = SpatialMetadata(640, 480, 640, 640, 1.0, 1.0, 0.0, 0.0)

    postprocessor = YoloPostprocessor(class_names=["cls0", "cls1"])
    with pytest.raises(ValueError, match="Expected exactly 6 channels"):
        postprocessor.process(raw_inf, frame, metadata)


def test_invalid_class_mappings() -> None:
    """22. Test that invalid class mappings raise ValueError or TypeError."""
    with pytest.raises(ValueError, match="Class names list cannot be empty"):
        YoloPostprocessor(class_names=[])

    with pytest.raises(ValueError, match="Class names dictionary cannot be empty"):
        YoloPostprocessor(class_names={})

    with pytest.raises(ValueError, match="contiguous zero-based integers"):
        YoloPostprocessor(class_names={1: "a", 2: "b"})

    with pytest.raises(TypeError, match="Expected class_names to be a list or dict"):
        YoloPostprocessor(class_names="not_a_collection")  # type: ignore


def test_invalid_thresholds() -> None:
    """23. Test that invalid confidence or IoU thresholds raise ValueError."""
    with pytest.raises(ValueError, match="Confidence threshold must be between 0.0 and 1.0"):
        YoloPostprocessor(class_names=["obj"], confidence_threshold=1.5)

    with pytest.raises(ValueError, match="IoU threshold must be between 0.0 and 1.0"):
        YoloPostprocessor(class_names=["obj"], iou_threshold=-0.1)


def test_nms_before_clipping_regression() -> None:
    """24. Regression test demonstrating model-space NMS before clipping/restoration.

    Two boxes have model-space IoU <= iou_threshold (surviving model-space NMS),
    but after clipping to original frame bounds, their clipped IoU > iou_threshold
    (which would cause suppression if NMS were incorrectly executed post-clipping).
    """
    tensor = np.zeros((1, 5, 8400), dtype=np.float32)
    # Box 1 (higher confidence 0.95): model xywh [525, 150, 250, 100] -> model xyxy [400, 100, 650, 200]
    tensor[0, 0, 0] = 525.0
    tensor[0, 1, 0] = 150.0
    tensor[0, 2, 0] = 250.0
    tensor[0, 3, 0] = 100.0
    tensor[0, 4, 0] = 0.95

    # Box 2 (lower confidence 0.80): model xywh [690, 150, 420, 100] -> model xyxy [480, 100, 900, 200]
    tensor[0, 0, 1] = 690.0
    tensor[0, 1, 1] = 150.0
    tensor[0, 2, 1] = 420.0
    tensor[0, 3, 1] = 100.0
    tensor[0, 4, 1] = 0.80

    raw_inf = _create_synthetic_raw_inference(tensor)
    frame = _create_synthetic_frame(frame_id="reg-test", timestamp=100.0)
    metadata = SpatialMetadata(
        original_width=640,
        original_height=480,
        input_width=640,
        input_height=640,
        scale_x=1.0,
        scale_y=1.0,
        pad_x=0.0,
        pad_y=0.0,
    )

    postprocessor = YoloPostprocessor(
        class_names=["obj"], confidence_threshold=0.5, iou_threshold=0.45
    )
    result = postprocessor.process(raw_inf, frame, metadata)

    # Both detections must survive because model-space IoU (0.34) <= 0.45.
    # If NMS ran post-clipping, clipped IoU (0.666) > 0.45 would suppress box 2.
    assert len(result.detections) == 2
    assert result.detections[0].confidence == pytest.approx(0.95)
    assert result.detections[1].confidence == pytest.approx(0.80)
