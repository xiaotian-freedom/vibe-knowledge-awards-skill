# vibe-knowledge-awards

**一个把知识科普短片"写出来"而不是"剪出来"的拍摄手册 + 参考实现。**
竖屏 9:16 / 横屏 16:9，无口播，画面踩音乐重拍，音效全部代码合成。

> An agent skill + reference implementation for code-generated knowledge explainer shorts
> (Douyin / TikTok style): beat-synced cuts, procedural SFX, zero stock footage.

---

## 这套东西解决什么问题

大多数知识类短视频的问题不是文案，是**画面不动、切点不踩拍、音效缺席**。这套流程把三件事变成可量化、可复现的：

| 维度 | 目标 | 怎么验 |
|---|---|---|
| 画面在动 | 静帧占比 < 10%，最长静止 < 2s | `scripts/motion_metric.py` |
| 切点踩拍 | 每镜长度按"拍"表达，误差 ≤ 1 帧 | 分镜表 + 节拍表 |
| 音效密度 | 单个事件 ≥ 环境 +5 dB，密集段 ≥ +3 dB 且连续 | 逐窗 RMS |
| 不越界 | 边缘带 0 亮像素 | `scripts/edge_check.py` |
| 平台响度 | -15.5 ~ -16.5 LUFS，TP -1.5 | `ebur128` |

实测一个 120 秒竖屏成片：静帧 **0.0%**、平均帧差 1.99、最长静止 **0s**、-16.6 LUFS。

## 目录

```
.
├── SKILL.md                        # 拍摄手册（Agent 用；人看也够）
├── scripts/
│   ├── motion_metric.py            # 静帧占比 / 最长静止 / 帧差分位
│   ├── edge_check.py               # 逐帧扫边缘带，抓文字越界
│   ├── mux_bed.sh                  # 渲染结果 + BGM + 音效轨 → loudnorm 母版
│   └── count_audio.py              # 合成与动画等长的连续计数音（引擎会节流密集 hit）
└── examples/
    └── vertical-1080x1920.html     # 33 镜 / 224 拍 / 120.8s 的完整参考实现
```

## 依赖

- **huashu-motion**（`om` CLI）：HTML + GSAP + canvas 逐帧渲染，用本机 Chrome
- `ffmpeg` / `ffprobe`
- Python 3 + `numpy`（脚本用）
- 一首可商用的 BGM（Pixabay 等），以及它的 BPM / 相位

## 快速开始

```bash
# 1) 建工程
om new my-film && cd my-film

# 2) 写 index.html：SHOTS 表 + 每镜一个 draw 函数（见 examples/）
#    段长用拍数：{ b: 起始拍, d: 拍数 }
#    BEAT = 60 / BPM

# 3) 自检 → 出音效 → 渲染
om check . && om sound . && om render . --crf 18 --preset medium

# 4) 混 BGM + 响度母版
bash ../scripts/mux_bed.sh out/my-film-v1.mp4 assets/bed.wav out/final.mp4

# 5) 验收
python3 ../scripts/motion_metric.py out/final.mp4
python3 ../scripts/edge_check.py out/final.mp4 --every 1
```

## 三条最贵的经验

1. **文字必须画在屏幕坐标系**（`setTransform(1,0,0,1,0,0)`），形状吃 camera 变换。混着算坐标，一推镜文字就被顶出画面。
2. **切点不要用全屏白闪**。这个频率下（每 2.7–3.7 秒一次）全屏白会闪到眼睛疼；改用「甩镜横移 + 压暗 + 细线扫过 + 缩放回弹」，一样有切割感。
3. **镜数由内容算，不套模板**。事件型（闪电、爆炸）2.5s 一切；机制型（回落、衰减）3.5–4.5s；金句 5–6s。把慢内容剪成快切，观众只记住跳，记不住意思。

## 系列差异化

同一台"视觉机器"不能连续两期复用。只保留四个不变项：栏目 mark、BGM/BPM、段落骨架、片尾预告下一期。
机器、强调色、排版对齐、转场语言，每期全换。

## License

MIT. `examples/` 里的文案与图形为本项目原创示例，可自由改写。
