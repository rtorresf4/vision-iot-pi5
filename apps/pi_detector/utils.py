import time, cv2

def fps_counter():
    last = time.time()
    while True:
        now = time.time()
        dt = now - last
        last = now
        yield 1.0 / dt if dt > 0 else 0.0

def draw_dets(frame, dets):
    for d in dets:
        x1,y1,x2,y2 = map(int, d['xyxy'])
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(frame, f"{d['cls']} {d['conf']:.2f}", (x1, max(0,y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
    return frame
