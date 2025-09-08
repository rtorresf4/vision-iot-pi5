from __future__ import annotations

import argparse
import csv
import signal
import sys
import time
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Capture images from a camera into class-labeled folders (OK/defect).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--label", required=True, choices=["ok", "defect"], help="Class label")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data"),
        help="Output dataset root folder (creates <out>/<label>)",
    )
    p.add_argument("--device", type=int, default=0, help="Camera index")
    p.add_argument("--width", type=int, default=640, help="Capture width")
    p.add_argument("--height", type=int, default=480, help="Capture height")
    p.add_argument(
        "--every",
        type=int,
        default=1,
        help="Save one frame every N frames (throttle saves)",
    )
    p.add_argument("--max", type=int, default=0, help="Stop after saving this many (0=∞)")
    p.add_argument(
        "--show",
        action="store_true",
        help="Display a preview window (press q to quit)",
    )
    return p.parse_args()


def ensure_dirs(root: Path, label: str) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    lbl_dir = root / label
    lbl_dir.mkdir(parents=True, exist_ok=True)
    return root, lbl_dir


def open_camera(device: int, width: int, height: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(int(device))
    if width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    if height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
    return cap


def save_frame(path: Path, frame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), frame)


def append_metadata(csv_path: Path, rel_path: str, label: str, ts: float, w: int, h: int) -> None:
    new_file = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        wtr = csv.writer(f)
        if new_file:
            wtr.writerow(["path", "label", "timestamp", "width", "height"])
        wtr.writerow([rel_path, label, f"{ts:.3f}", w, h])


def main() -> int:
    args = parse_args()

    # Prepare folders and metadata file
    root, lbl_dir = ensure_dirs(args.out, args.label)
    meta_csv = root / "metadata.csv"

    # Handle Ctrl+C gracefully
    stop = False

    def _sigint(_sig, _frm):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _sigint)

    cap = open_camera(args.device, args.width, args.height)
    if not cap.isOpened():
        print("ERROR: Cannot open camera", file=sys.stderr)
        return 2

    print(
        f"Capturing to '{lbl_dir}' (label={args.label}, every={args.every}, max={args.max or '∞'})"
    )
    saved = 0
    frame_idx = 0
    win_name = "capture_dataset" if args.show else None

    if args.show:
        cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win_name, args.width, args.height)

    try:
        while not stop:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("WARN: Failed to read frame; retrying...")
                time.sleep(0.01)
                continue

            frame_idx += 1
            if args.show:
                cv2.imshow(win_name, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            if frame_idx % max(1, args.every) != 0:
                continue

            ts = time.time()
            fname = f"{int(ts*1000)}_{frame_idx:06d}.jpg"
            out_path = lbl_dir / fname
            save_frame(out_path, frame)

            h, w = frame.shape[:2]
            rel = out_path.relative_to(root)
            append_metadata(meta_csv, str(rel), args.label, ts, w, h)

            saved += 1
            if saved % 10 == 0:
                print(f"Saved {saved} images to {lbl_dir}")
            if args.max and saved >= args.max:
                break
    finally:
        cap.release()
        if args.show:
            cv2.destroyAllWindows()

    print(f"Done. Total saved: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

