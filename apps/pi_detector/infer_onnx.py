import numpy as np
import cv2
try:
    import onnxruntime as ort
except Exception:
    ort = None

class OnnxYolo:
    def __init__(self, model_path, conf_thres=0.5, iou_thres=0.5, imgsz=640):
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.imgsz = imgsz
        if ort is None:
            raise RuntimeError("onnxruntime not available. Install it or switch to TFLite.")
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name

    def _preprocess(self, img):
        h, w = img.shape[:2]
        scale = self.imgsz / max(h, w)
        nh, nw = int(h*scale), int(w*scale)
        resized = cv2.resize(img, (nw, nh))
        padded = np.full((self.imgsz, self.imgsz, 3), 114, dtype=np.uint8)
        padded[:nh, :nw] = resized
        x = padded.transpose(2,0,1)[None].astype(np.float32) / 255.0
        return x, scale

    def predict(self, img):
        x, scale = self._preprocess(img)
        out = self.session.run(None, {self.input_name: x})[0]
        # Simplified parser; adapt to your exported YOLOv8 model outputs
        dets = []
        for row in out[0]:
            conf = float(row[4])
            if conf < self.conf_thres:
                continue
            x1,y1,x2,y2 = row[:4]
            dets.append({'cls':'defect','conf':conf,'xyxy':[x1/scale,y1/scale,x2/scale,y2/scale]})
        return dets
