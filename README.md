# 장현수 기술노트

센서, 통신, 시간 동기화, 센서 캘리브레이션, 실차 데이터 취득을 다루는 기술 글 사이트. 주소: https://hsjang545.github.io/notes/

소개(이력) 사이트 [hsjang545.github.io](https://github.com/hsjang545/hsjang545.github.io)와 별도 저장소다. [Jekyll Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) 7.6 테마를 쓰고 GitHub Actions가 빌드한다.

## 작업 방식

사이트 파일은 로컬(구글드라이브 포함)에 두지 않고 GitHub에서만 관리한다. 고칠 때는 GitHub 웹 편집기(저장소 화면에서 `.` 키) 또는 Codespaces를 쓴다.

| 할 일 | 위치 |
| --- | --- |
| 목차, 글 초안, 공개 금지어 목록 | 비공개 저장소 [hsjang545/notes-drafts](https://github.com/hsjang545/notes-drafts) |
| 작성 규칙 | `docs/style.md` (앞부분 형식, 공개 금지 기준, 수식·도식·그림 문법) |
| 게시 | 검토한 초안을 이 저장소 `_posts/YYYY-MM-DD-<슬러그>.md`로 만들어 커밋 |
| 그림 | 스크립트 `tools/figures/<글 파일명>.py`를 커밋하면 Actions `그림 생성`이 `assets/img/<글 파일명>/`의 SVG를 다시 만들어 커밋하고 배포한다 |

게시 전 확인: HTML 주석(출처·확인 필요·경험 자리) 모두 삭제, 초안의 `[[sync-04]]` 같은 글 번호 링크를 `{% post_url 2026-11-14-sync-04-linuxptp-ubuntu %}`로 교체, 과제를 특정할 수 있는 구성·수치 제거.

## 배포

`main`에 커밋하면 GitHub Actions(`Build and Deploy`)가 다음을 통과한 경우에만 배포한다. 실패하면 Actions 탭에서 원인을 본다.

1. 공개 금지어 검사(`tools/check-private.sh`): `_posts`, `_tabs`, `_data`, `_config.yml`, `docs`, `README.md`에 금지어가 있거나 `_posts`에 HTML 주석이 남아 있으면 실패
2. Jekyll 빌드
3. 내부 링크·이미지 검사(html-proofer)

## 공개하지 않는 것

고객사·협력사·과제명, 차량, 사용 장비 모델명, 장착 위치, 차량 내부 신호, 실제 IP, 공개 전 논문·특허 내용. 금지어 목록 자체도 비공개라 이 저장소에 두지 않는다. 원본은 `hsjang545/notes-drafts`의 `forbidden.txt`, CI는 저장소 secret `FORBIDDEN_PATTERNS`를 쓴다. 목록을 고치면 secret도 같이 바꾼다.

```bash
grep -vE '^\s*(#|$)' forbidden.txt | gh secret set FORBIDDEN_PATTERNS -R hsjang545/notes
```
