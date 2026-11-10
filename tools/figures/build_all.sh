#!/usr/bin/env bash
#
# 그림 스크립트를 실행해 assets/img/ 아래 SVG를 만든다.
# 보통은 GitHub Actions(.github/workflows/figures.yml)가 실행한다.
# 필요한 패키지: numpy, scipy, matplotlib (calib-03은 opencv-python, calib-05는 open3d도), 한글 글꼴(나눔고딕 등)
# 사용: NOTES_PY=python bash tools/figures/build_all.sh [글 파일명 ...]

set -euo pipefail
cd "$(dirname "$0")"

py="${NOTES_PY:-python3}"

if [[ $# -gt 0 ]]; then scripts=("${@/%/.py}"); else scripts=([a-z]*.py); fi
for s in "${scripts[@]}"; do
  echo "그림 생성: $s"
  "$py" -I -B "$s"
done
