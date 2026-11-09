# 장현수 기술노트

센서, 통신, 시간 동기화, 센서 캘리브레이션, 실차 데이터 취득을 다루는 기술 글 사이트. 주소: https://hsjang545.github.io/notes/

소개(이력) 사이트 `hsjang545.github.io`와 별도 저장소다. [Jekyll Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) 7.6 테마를 쓰고 GitHub Actions가 빌드한다.

## 글 쓰기와 게시

| 할 일 | 방법 |
| --- | --- |
| 목차 확인 | `docs/curriculum.md` |
| 작성 규칙 | `docs/style.md` (앞부분 형식, 공개 금지 기준, 수식·도식 문법) |
| 초안 쓰기 | `_drafts/<접두사>-<번호>-<슬러그>.md`. `_drafts/`는 Git에서 제외되어 공개 저장소에 올라가지 않는다 |
| 게시 | 검토한 초안을 `_posts/YYYY-MM-DD-<슬러그>.md`로 옮기고 `date`를 맞춘 뒤 커밋·푸시 |
| 그림 | `assets/img/<슬러그>/`에 두고 `![설명](/assets/img/<슬러그>/파일.png)` |

게시 전 확인: `<!-- 확인 필요 -->` 해결, `<!-- 경험 -->` 자리 채우거나 지우기, 초안의 `[[sync-04]]` 같은 글 번호 링크를 `{% post_url 2026-11-10-sync-04-linuxptp-ubuntu %}`로 교체.

## 명령

```bash
bash tools/check-private.sh      # 공개 금지어 검사 (.private/forbidden.txt 필요)
bash tools/preview.sh            # Docker로 초안 포함 미리보기: http://127.0.0.1:4000/notes/
bash tools/preview.sh --build    # 빌드와 내부 링크 검사만
git add -A && git commit -m "내용" && git push   # 배포
```

`main`에 푸시하면 GitHub Actions가 공개 금지어 검사 → 빌드 → 링크 검사를 통과한 경우에만 배포한다.

이 폴더는 구글드라이브에 있다. `tools/preview.sh`는 `%LOCALAPPDATA%\hsjang545-notes`로 복사해 Docker(ruby:3.4)에서 빌드하므로 드라이브에 캐시가 쌓이지 않는다. Docker Desktop이 켜져 있어야 한다. `.git`도 드라이브로 동기화되므로 한 번에 PC 한 대에서만 작업한다.

## 공개하지 않는 것

고객사·협력사·과제명, 차량, 사용 장비 모델명, 장착 위치, 차량 내부 신호, 실제 IP, 특허 출원 전 내용. 금지어 목록 자체도 비공개라 저장소에 두지 않는다.

- 로컬: `.private/forbidden.txt` (Git 제외)
- CI: 저장소 secret `FORBIDDEN_PATTERNS`에 같은 내용
