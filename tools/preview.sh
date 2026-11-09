#!/usr/bin/env bash
#
# Docker로 사이트를 빌드해 미리 본다. Ruby를 설치하지 않아도 된다.
# 구글드라이브 안에서 빌드하면 캐시와 _site가 동기화되므로, 드라이브 밖 작업 폴더로 복사해 빌드한다.
#
# 사용: bash tools/preview.sh            # 초안 포함 빌드 후 http://127.0.0.1:4000/notes/ 로 서비스
#       bash tools/preview.sh --build    # 빌드와 링크 검사만 하고 끝낸다

set -euo pipefail

src="$(cd "$(dirname "$0")/.." && pwd)"
work="${LOCALAPPDATA:-$HOME/.cache}/hsjang545-notes"
work_unix="$(cygpath -u "$work" 2>/dev/null || echo "$work")"
mkdir -p "$work_unix"

# .git, _site, 캐시는 빼고 복사한다. 지운 파일도 반영되도록 소스 쪽 파일 목록 기준으로 덮어쓴다.
tar -C "$src" --exclude=.git --exclude=_site --exclude=.jekyll-cache --exclude=vendor -cf - . | tar -C "$work_unix" -xf -
find "$work_unix/_drafts" "$work_unix/_posts" -name '*.md' 2>/dev/null | while read -r f; do
  rel="${f#"$work_unix"/}"
  [[ -e "$src/$rel" ]] || rm -f "$f"
done

mount="$(cygpath -w "$work_unix" 2>/dev/null || echo "$work_unix")"
image="ruby:3.4"
gems="hsjang545-notes-gems"

if [[ "${1:-}" == "--build" ]]; then
  MSYS_NO_PATHCONV=1 docker run --rm -v "$mount:/srv" -v "$gems:/usr/local/bundle" -w /srv "$image" \
    bash -c 'bundle install --quiet && JEKYLL_ENV=production bundle exec jekyll build --drafts --future -d _site/notes && bundle exec htmlproofer _site --disable-external --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"'
else
  MSYS_NO_PATHCONV=1 docker run --rm -it -p 4000:4000 -v "$mount:/srv" -v "$gems:/usr/local/bundle" -w /srv "$image" \
    bash -c 'bundle install --quiet && bundle exec jekyll serve --drafts --future -H 0.0.0.0 --force_polling'
fi
