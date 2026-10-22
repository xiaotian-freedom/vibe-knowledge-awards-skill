#!/usr/bin/env bash
# 把固定 BGM 混进 huashu-motion 的渲染结果。
# 引擎音轨只有音效（OM.music({ off: true })），音乐按系列约定用固定曲；
# 两条混完再过一遍 loudnorm，统一到平台口径。
#
#   bash tools/mux_bed.sh <render.mp4> <bed.wav|mp3> <out.mp4>
set -euo pipefail

VIDEO="${1:?用法: bash tools/mux_bed.sh <render.mp4> <bed.wav> <out.mp4>}"
BED="${2:?缺 BGM 文件}"
OUT="${3:?缺输出路径}"
SFX="${4:-assets/sound.wav}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")

ffmpeg -v error -y -i "$VIDEO" -i "$BED" -i "$SFX" -filter_complex \
  "[1:a]volume=0.80,apad[bed];[2:a]volume=1.0,apad[sfx];\
   [bed][sfx]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,\
   loudnorm=I=-15.5:TP=-1.5:LRA=9[a]" \
  -map 0:v -map "[a]" -t "$DUR" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"

echo "→ $OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
