from __future__ import annotations

import argparse
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass
class ProbeResult:
    device: int
    opened: bool
    backend: str
    fourcc_set: str | None
    frame_size: tuple[int, int] | None
    res_tests: list[tuple[int, int, bool, tuple[int, int] | None]]  # (w,h,ok,actual)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="List and probe cameras via OpenCV (UVC).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--device", type=int, default=None, help="Only probe this device index")
    p.add_argument(
        "--max-devices", type=int, default=6, help="Scan indices [0..N-1] if --device not set"
    )
    p.add_argument(
        "--probe-res",
        action="store_true",
        help="Try a set of common resolutions and report success",
    )
    p.add_argument(
        "--res-list",
        type=str,
        default="640x480,800x600,1280x720,1920x1080",
        help="Comma-separated list of WxH to try when --probe-res",
    )
    p.add_argument(
        "--fourcc",
        type=str,
        default="MJPG",
        help="Preferred pixel format to request (e.g., MJPG, YUYV). Leave blank to skip",
    )
    p.add_argument("--show", action="store_true", help="Show a preview frame if available")
    p.add_argument("--snap", type=Path, default=None, help="Save a snapshot JPEG if available")
    p.add_argument(
        "--read-timeout-ms",
        type=int,
        default=2000,
        help="Attempt to cap read/open timeouts (if backend supports it)",
    )
    return p.parse_args()


def parse_res_list(s: str) -> Iterable[tuple[int, int]]:
    for tok in s.split(","):
        tok = tok.strip().lower()
        if "x" in tok:
            w, h = tok.split("x", 1)
            try:
                yield int(w), int(h)
            except ValueError:
                continue


def backend_name(cap: cv2.VideoCapture) -> str:
    try:
        # OpenCV Python API doesn’t expose backend name directly everywhere; best effort.
        return str(cap.getBackendName()) if hasattr(cap, "getBackendName") else "unknown"
    except Exception:
        return "unknown"


def set_fourcc(cap: cv2.VideoCapture, fourcc: str | None) -> str | None:
    if not fourcc:
        return None
    f = fourcc.strip().upper()
    if len(f) != 4:
        return None
    try:
        code = cv2.VideoWriter_fourcc(*f)
        cap.set(cv2.CAP_PROP_FOURCC, code)
        return f
    except Exception:
        return None


def grab_frame(cap: cv2.VideoCapture):
    ok, frame = cap.read()
    return frame if ok else None


def _set_timeouts(cap: cv2.VideoCapture, read_timeout_ms: int) -> None:
    # Best-effort: only works on newer OpenCV/backends
    try:
        if hasattr(cv2, "CAP_PROP_OPEN_TIMEOUT_MSEC"):
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, int(read_timeout_ms))
    except Exception:
        pass
    try:
        if hasattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC"):
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, int(read_timeout_ms))
    except Exception:
        pass


def probe_device(
    idx: int,
    probe_res: bool,
    res_list: Iterable[tuple[int, int]],
    fourcc: str | None,
    read_timeout_ms: int,
) -> ProbeResult:
    cap = cv2.VideoCapture(idx)
    _set_timeouts(cap, read_timeout_ms)
    opened = cap.isOpened()
    res_tests: list[tuple[int, int, bool, tuple[int, int] | None]] = []
    fr_size = None
    fourcc_set = None
    try:
        if not opened:
            return ProbeResult(
                idx, False, backend="unknown", fourcc_set=None, frame_size=None, res_tests=[]
            )

        backend = backend_name(cap)
        fourcc_set = set_fourcc(cap, fourcc)

        # Try to read a frame at default size
        frame = grab_frame(cap)
        if frame is not None:
            h, w = frame.shape[:2]
            fr_size = (w, h)

        if probe_res:
            for w, h in res_list:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(w))
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(h))
                test = grab_frame(cap)
                if test is None:
                    res_tests.append((w, h, False, None))
                else:
                    hh, ww = test.shape[:2]
                    res_tests.append((w, h, True, (ww, hh)))

        return ProbeResult(
            idx,
            True,
            backend=backend,
            fourcc_set=fourcc_set,
            frame_size=fr_size,
            res_tests=res_tests,
        )
    finally:
        cap.release()


def show_and_snap(idx: int, snap: Path | None) -> None:
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        print(f"[video{idx}] cannot open for preview")
        return
    ok, frame = cap.read()
    if not ok or frame is None:
        print(f"[video{idx}] failed to grab frame for preview")
    else:
        h, w = frame.shape[:2]
        print(f"[video{idx}] preview frame: {w}x{h}")
        cv2.imshow(f"video{idx} preview (press any key)", frame)
        cv2.waitKey(0)
        if snap:
            snap.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(snap), frame)
            print(f"Snapshot saved to {snap}")
    cap.release()
    cv2.destroyAllWindows()


def main() -> int:
    args = parse_args()
    targets = [args.device] if args.device is not None else list(range(max(0, args.max_devices)))
    res_list = list(parse_res_list(args.res_list))

    print("Scanning cameras...")
    found = []
    for idx in targets:
        r = probe_device(
            idx,
            probe_res=args.probe_res,
            res_list=res_list,
            fourcc=args.fourcc or None,
            read_timeout_ms=getattr(args, "read_timeout_ms", 2000),
        )
        if not r.opened:
            print(f"- /dev/video{idx}: not available")
            continue
        found.append(idx)
        print(f"- /dev/video{idx}: OPEN (backend={r.backend}, fourcc_set={r.fourcc_set or 'n/a'})")
        if r.frame_size:
            w, h = r.frame_size
            print(f"  default frame: {w}x{h}")
        if args.probe_res and r.res_tests:
            for w, h, ok, actual in r.res_tests:
                if ok and actual:
                    aw, ah = actual
                    print(f"  try {w}x{h}: OK -> {aw}x{ah}")
                else:
                    print(f"  try {w}x{h}: FAIL")

    if args.show or args.snap:
        # Use first found device (or the specified one)
        if args.device is not None and args.device in (found or [args.device]):
            show_and_snap(args.device, args.snap)
        elif found:
            show_and_snap(found[0], args.snap)
        else:
            print("No available devices to preview.")

    if not found:
        print("No cameras found. If you expected one, try another USB port or check permissions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
