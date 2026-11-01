# SCOPE.md — 승인 범위 (소유자 확인)

- 소유자: joonake / GitHub `joonake9644`
- 작성일: 2026-10-31
- 작업: 방어 목적 자가 점검(레드팀 시뮬레이션) + 취약점 분석·수정
- 지시문: [`AUTHORIZATION.md`](AUTHORIZATION.md) · 절차: [`engagement-loop.md`](engagement-loop.md)

## 범위 안 (In scope)

- 저장소 `github.com/joonake9644/web-crawler` 의 소스·테스트·문서·설정 (모든 브랜치)
- 소유자 로컬 환경: 이 저장소의 `.venv`, `.tmp/`, `output/`(소유자 수집 결과), `fingerprints/`
- 소유자 로컬에서 띄우는 테스트 서버(`127.0.0.1` 의 `ThreadingHTTPServer` 등)와 그 픽스처
- 소유자 계정의 GitHub 저장소 설정(Dependabot·Actions) — **변경은 소유자가 직접** 한다

## 범위 밖 (Out of scope)

- 제3자 사이트·API·계정을 **침투 테스트 도구의 대상**으로 삼는 것
  (ZAP·Nuclei·sqlmap·ffuf·부하 스크립트 등을 남의 URL 에 돌리지 않는다)
- 실제 개인정보가 담긴 수집 결과를 저장소 밖으로 내보내는 것
- 위 목록에 없는 자산

> 크롤링 대상 사이트를 **수집**하는 일은 이 문서의 범위가 아니다. 그건 기존 규칙
> (`ACCEPTABLE_USE.md`, `AGENTS.md` 통지 게이트·동의 기록·robots 확인)이 따로 다룬다.

## 허용 (Allowed)

- 소스 리뷰: PII 누출, 비밀 파일 권한, 입력 검증, 경로·명령 주입, 의존성 취약점
- 로컬 재현 테스트(RED) → 수정(GREEN) → 회귀 테스트 추가
- 의존성 취약점 대조(OSV·GHSA·CISA KEV) 결과를 `docs/security/intel-brief-*.md` 로 기록

## 금지 (Forbidden)

- 소유자가 통제하지 않는 시스템 공격
- 익스플로잇·실제 자격증명을 이 작업 밖으로 게시
- CAPTCHA 자동 풀이, 로그인 자격증명 저장 (기존 하드룰 그대로)
