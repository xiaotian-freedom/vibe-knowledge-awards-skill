#!/usr/bin/env python3
"""计数音：合成一段 2.6s 的连续增长音，并混进 assets/sound.wav。

用法：
  /usr/bin/python3 tools/count_audio.py            # 生成 assets/count.wav
  /usr/bin/python3 tools/count_audio.py --mix 85.86  # 混入 sound.wav（秒）
"""
import sys, wave, math, array

SR = 48000
DUR = 2.60
OUT = "assets/count.wav"


def synth():
    n = int(SR * DUR)
    buf = [0.0] * n
    # 底：一层很轻的上升气流，保证不出现断点
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.25) * min(1.0, (DUR - t) / 0.3)
        buf[i] += 0.06 * env * math.sin(2 * math.pi * (220 + 180 * t / DUR) * t)
    # 点击：每 1/12 秒一下，音高随进度上升
    step = 1.0 / 12
    k = 0
    while k * step < DUR:
        t0 = k * step
        f = 900 * (1 + 0.85 * (t0 / DUR))
        start = int(t0 * SR)
        ln = int(0.045 * SR)
        for i in range(ln):
            if start + i >= n:
                break
            t = i / SR
            env = math.exp(-t * 90)
            buf[start + i] += 0.5 * env * math.sin(2 * math.pi * f * t)
        k += 1
    # 轻微削峰
    peak = max(1e-6, max(abs(v) for v in buf))
    g = min(1.0, 0.72 / peak)
    return [v * g for v in buf]


def write_wav(path, samples):
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    out = array.array("h")
    for v in samples:
        s = int(max(-1.0, min(1.0, v)) * 32767)
        out.append(s)
        out.append(s)
    w.writeframes(out.tobytes())
    w.close()


def mix(offset_s):
    src = wave.open(OUT, "rb")
    add = array.array("h")
    add.frombytes(src.readframes(src.getnframes()))
    src.close()

    dst = wave.open("assets/sound.wav", "rb")
    sr = dst.getframerate()
    ch = dst.getnchannels()
    base = array.array("h")
    base.frombytes(dst.readframes(dst.getnframes()))
    dst.close()
    assert sr == SR and ch == 2, (sr, ch)

    off = int(offset_s * SR) * 2  # stereo frames
    for i, v in enumerate(add):
        j = off + i
        if j >= len(base):
            break
        base[j] = max(-32768, min(32767, base[j] + v))

    out = wave.open("assets/sound.wav", "wb")
    out.setnchannels(2)
    out.setsampwidth(2)
    out.setframerate(sr)
    out.writeframes(base.tobytes())
    out.close()
    print(f"mixed {len(add)//2/SR:.2f}s into assets/sound.wav at {offset_s:.2f}s")


if __name__ == "__main__":
    samples = synth()
    write_wav(OUT, samples)
    print(f"wrote {OUT}  {DUR:.2f}s")
    if "--mix" in sys.argv:
        mix(float(sys.argv[sys.argv.index("--mix") + 1]))
