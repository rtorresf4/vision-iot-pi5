from __future__ import annotations

import time
import signal
import sys
from pathlib import Path

import cv2
import yaml

from utils import draw_dets, fps_counter
from infer_onnx import OnnxYolo
from mqtt_client import MqttClient


def load_cfg(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    cfg_path = Path(__file__).with_name("config.yaml")
    cfg = load_cfg(cfg_path)

    broker = cfg["broker"]
    model_cfg = cfg["model"]
    video_cfg = cfg["video"]
    base_topic = broker.get("base_topic", "factory/line1")

    mqttc = MqttClient(
        host=broker["host"],
        port=broker["port"],
        client_id=broker["client_id"],
        keepalive=broker.get("keepalive", 60),
        qos=broker.get("qos", 0),
        base_topic=base_topic,
    )
    mqttc.connect_and_loop()

    cap = cv2.VideoCapture(int(video_cfg.get("device", 0)))
    if video_cfg.get("width"):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(video_cfg["width"])) 
    if video_cfg.get("height"):
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(video_cfg["height"])) 
    if not cap.isOpened():
        print("ERROR: Cannot open camera", file=sys.stderr)
        return 2

    model = OnnxYolo(
        model_path=model_cfg["path"],
        conf_thres=float(model_cfg.get("conf_thres", 0.5)),
        iou_thres=float(model_cfg.get("iou_thres", 0.5)),
        imgsz=int(model_cfg.get("imgsz", 640)),
    )

    fps = fps_counter()
    running = True

    def handle_sig(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    while running:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.02)
            continue

        dets = model.predict(frame)
        frame_draw = draw_dets(frame, dets)

        payload = {
            "ts": time.time(),
            "fps": next(fps),
            "pieces_ok": sum(1 for d in dets if d.get("cls") == "ok"),
            "pieces_ng": sum(1 for d in dets if d.get("cls") == "defect"),
            "bboxes": [d.get("xyxy") for d in dets],
            "confs": [round(float(d.get("conf", 0)), 3) for d in dets],
        }
        mqttc.publish("detections", payload, retain=False)

        cv2.imshow("PI5 Detector", frame_draw)
        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    mqttc.publish("status", {"state": "offline", "ts": time.time()}, retain=True, qos=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
