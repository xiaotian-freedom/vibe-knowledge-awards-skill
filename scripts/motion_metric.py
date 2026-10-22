"""量化"画面有没有在动"：相邻帧的平均绝对差（灰度）+ 静帧占比。

用途：验收"文字占满、没有动画"这类意见——把成片按 6 fps 采样，比较相邻帧，
输出：平均帧差、静止帧占比（帧差 < 0.3/255）、以及最大连续静止时长。

用法：
    /usr/bin/python3 tools/motion_metric.py <video.mp4> [--fps 6] [--width 480]
"""
from __future__ import annotations

import argparse
import subprocess
import sys

import numpy as np


def frames(path: str, fps: int, width: int) -> np.ndarray:
    cmd = [
        "ffmpeg", "-v", "error", "-i", path,
        "-vf", f"fps={fps},scale={width}:-1,format=gray",
        "-f", "rawvideo", "-",
    ]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    h = int.from_bytes(b"", "little") if False else None
    # 高度由 ffmpeg 决定：从一帧长度反推宽度已知, 高度 = len/frame / width
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip().split(",")
    sw, sh = int(probe[0]), int(probe[1])
    scale_h = int(round(sh * width / sw / 2) * 2)
    n = len(raw) // (width * scale_h)
    return np.frombuffer(raw[: n * width * scale_h], dtype=np.uint8).reshape(n, scale_h, width)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=int, default=6)
    ap.add_argument("--width", type=int, default=480)
    a = ap.parse_args()

    f = frames(a.video, a.fps, a.width).astype(np.float32)
    if len(f) < 2:
        print("帧数不足")
        return 1
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    static = d < 0.3

    # 最长连续静止
    longest = cur = 0
    for s in static:
        cur = cur + 1 if s else 0
        longest = max(longest, cur)

    print(f"片源 {a.video}")
    print(f"采样 {a.fps} fps / {a.width}px 宽，共 {len(f)} 帧")
    print(f"平均帧差 {d.mean():.2f}/255   中位 {np.median(d):.2f}")
    print(f"静止帧占比 {static.mean()*100:.1f}%   最长连续静止 {longest / a.fps:.1f}s")
    print(f"动效强度分位 p10 {np.percentile(d,10):.2f} / p50 {np.percentile(d,50):.2f} / p90 {np.percentile(d,90):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
