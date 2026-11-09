#!/usr/bin/env bash
#
# 모든 그림 스크립트를 다시 실행해 assets/img/ 아래 SVG를 만든다.
# 파이썬 환경: %LOCALAPPDATA%\hsjang545-notes-venv (numpy, scipy, matplotlib. calib-03은 opencv-python, calib-05는 open3d도 필요)
#   만들기: py -3 -m venv "%LOCALAPPDATA%\hsjang545-notes-venv" 후 pip install numpy scipy matplotlib
# 사용: bash tools/figures/build_all.sh [글 파일명 ...]

set -euo pipefail
cd "$(dirname "$0")"

py="${NOTES_PY:-${LOCALAPPDATA:-}/hsjang545-notes-venv/Scripts/python.exe}"
[[ -x "$py" ]] || py="${LOCALAPPDATA:-}/hsjang545-notes-venv/bin/python"

if [[ $# -gt 0 ]]; then scripts=("${@/%/.py}"); else scripts=([a-z]*.py); fi
for s in "${scripts[@]}"; do
  echo "그림 생성: $s"
  "$py" -I -B "$s"
done
