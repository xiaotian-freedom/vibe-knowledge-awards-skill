"""边框越界检查：逐秒抽帧，看画面最外圈有没有"亮到像文字"的像素。

排版越界（字被切掉半截、贴边）在成片里表现为：紧贴边缘的 8px 带内出现高亮像素。
粒子/网格是低透明度的，不会触发；文字、图形块才会。

用法：
    /usr/bin/python3 tools/edge_check.py <video.mp4> [--every 1] [--band 8]
输出：触发的秒数列表（空 = 没有越界），以及最亮的那一帧。
"""
from __future__ import annotations

import argparse
import subprocess

import numpy as np


def frame_at(path: str, t: float, w: int = 960) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1",
         "-vf", f"scale={w}:-2,format=gray", "-f", "rawvideo", "-"],
        capture_output=True, check=True,
    ).stdout
    h = len(raw) // w
    return np.frombuffer(raw, dtype=np.uint8).reshape(h, w)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--every", type=float, default=1.0)
    ap.add_argument("--band", type=int, default=8)
    ap.add_argument("--thresh", type=int, default=150, help="视为亮的灰度阈值")
    ap.add_argument("--pct", type=float, default=0.5, help="边缘带内亮像素占比报警阈值（%）")
    a = ap.parse_args()

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
        capture_output=True, text=True, check=True).stdout.strip())

    bad, worst = [], (0.0, -1.0)
    t = 0.0
    while t < dur:
        f = frame_at(a.video, t)
        b = a.band
        edge = np.concatenate([
            f[:b, :].ravel(), f[-b:, :].ravel(), f[:, :b].ravel(), f[:, -b:].ravel()
        ])
        pct = float((edge > a.thresh).mean() * 100)
        if pct > worst[1]:
            worst = (t, pct)
        if pct > a.pct:
            bad.append((round(t, 2), round(pct, 2)))
        t += a.every

    print(f"片源 {a.video}  时长 {dur:.1f}s  抽帧 {int(dur / a.every)} 张")
    print(f"最亮边缘帧: {worst[0]:.1f}s → {worst[1]:.2f}% 亮像素（阈值 {a.pct}%）")
    if bad:
        print(f"⚠️ 可能越界 {len(bad)} 帧：")
        for t, p in bad[:20]:
            print(f"   {t:6.1f}s  {p:5.2f}%")
        return 1
    print("✅ 边缘带内没有文字级亮像素，排版未越界")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
