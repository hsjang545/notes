#!/usr/bin/env bash
#
# 공개 금지어 검사. 글과 설정에 비공개 정보가 들어가면 실패한다.
# 금지어 목록 자체도 비공개이므로 저장소에 두지 않는다.
#   로컬: .private/forbidden.txt (한 줄에 정규식 하나, # 주석 가능). 원본은 비공개 저장소 hsjang545/notes-drafts의 forbidden.txt
#   CI:   GitHub Actions secret FORBIDDEN_PATTERNS (같은 형식)
#
# 사용: bash tools/check-private.sh [검사할 경로...]   (기본: _posts _tabs _data _config.yml docs README.md, 있으면 _drafts)

set -euo pipefail

cd "$(dirname "$0")/.."

patterns_file=$(mktemp)
trap 'rm -f "$patterns_file"' EXIT

if [[ -n "${FORBIDDEN_PATTERNS:-}" ]]; then
  printf '%s\n' "$FORBIDDEN_PATTERNS" >"$patterns_file"
elif [[ -f .private/forbidden.txt ]]; then
  cp .private/forbidden.txt "$patterns_file"
else
  echo "금지어 목록이 없다: FORBIDDEN_PATTERNS 환경변수나 .private/forbidden.txt가 필요하다." >&2
  exit 2
fi

# 목록과 무관하게 항상 막는 것: 비밀번호·토큰·개인키 형태
cat >>"$patterns_file" <<'ALWAYS'
-----BEGIN [A-Z ]*PRIVATE KEY-----
(password|passwd|비밀번호)[[:space:]]*[:=][[:space:]]*[^[:space:]<]+
gh[pousr]_[A-Za-z0-9]{30,}
ALWAYS

# 주석과 빈 줄 제거
sed -i -e 's/[[:space:]]*#.*$//' -e '/^[[:space:]]*$/d' "$patterns_file"

if [[ $# -gt 0 ]]; then
  targets=("$@")
else
  targets=(_posts _tabs _data _config.yml docs README.md)
  [[ -d _drafts ]] && targets+=(_drafts)
fi

# 아직 없는 경로(글이 하나도 없을 때의 _posts 등)는 뺀다.
existing=()
for t in "${targets[@]}"; do [[ -e "$t" ]] && existing+=("$t"); done
targets=("${existing[@]}")

if grep -rniE -f "$patterns_file" --include='*.md' --include='*.yml' --include='*.yaml' --include='*.html' "${targets[@]}"; then
  echo "공개 금지어가 발견됐다. 위 줄을 고친 뒤 다시 실행한다." >&2
  exit 1
fi
# 게시 글에는 HTML 주석이 남으면 안 된다. 초안의 출처·확인 필요·경험 자리 주석은 페이지 소스에 그대로 나간다.
if [[ -d _posts ]] && grep -rln --include='*.md' -e '<!--' _posts; then
  echo "게시 글(_posts)에 HTML 주석이 남아 있다. 출처·확인 필요·경험 주석을 지운 뒤 다시 실행한다." >&2
  exit 1
fi
echo "공개 금지어 검사 통과"
