# 조각 PREFLIGHT-001: preflight HTTP 점검이 사다리 1단 `plain_get` 으로 요청해 지어낸 Referer·위장 기본값을 보내지 않는다
- 위험 등급: light
- 핵심 경로: no
- 세션 예산: 1
- 계획 과제: PREFLIGHT-001
- 허용 경로: scripts/preflight.py, scripts/test_preflight.py, docs/task-contracts/PREFLIGHT-001.slice.md, .gitignore, .harness/state.json, docs/session-handoff.md

## 출발 실측(2026-11-12, master c7fa19e, scrapling 0.5.1)
- `scripts/preflight.py:127` `check_http_fetch()` 는 `Fetcher().get("https://httpbin.org/html")` 를 부른다. scrapling 기본값(위장 TLS·위장 헤더)을 그대로 쓰므로, 원본 체크아웃 bootstrap 로그에 `(referer: https://www.google.com/)` 가 찍혔다.
- `Fetcher()` 인스턴스를 만들면 「This logic is deprecated now …」 경고가 난다. `utils.plain_get` 은 인스턴스를 만들지 않고 `Fetcher.get` 을 부른다.
- preflight 용 시험 파일이 없다.

## 설계
- 점검 주소를 모듈 상수 `HTTP_CHECK_URL = "https://httpbin.org/html"` 로 뺀다(시험이 로컬 서버로 바꿔 끼울 수 있게).
- `check_http_fetch()` 는 `from utils import plain_get` 후 `plain_get(HTTP_CHECK_URL)` 를 부른다. 판정(200=PASS, 그 밖·예외=WARN)·메시지·`--no-network` 동작은 그대로다.

## 합격 기준
1. 새 `scripts/test_preflight.py` 의 시험을 먼저 RED 로 확인한 뒤 GREEN: ① `check_http_fetch()` 가 `utils.plain_get` 을 `HTTP_CHECK_URL` 로 부르고 `scrapling.fetchers.Fetcher` 인스턴스를 만들지 않는다 ② 로컬 HTTP 서버(외부 네트워크 없음)로 받은 실제 요청 헤더에 `Referer` 가 없다.
2. 판정 회귀 시험: 200 → PASS, 503 → WARN, 예외 → WARN.
3. 네트워크가 되는 환경에서 `scripts/preflight.py --core-only` 출력에 `referer: https://www.google.com/` 과 「deprecated」 경고가 없다(실측 기록).
4. 아래 검사 명령이 모두 exit 0 이다.

## 검사 명령
- `.venv/bin/python -m pytest -q -k "not e2e"`
- `.venv/bin/python scripts/continuity_check.py`
- `.venv/bin/python scripts/sync_domain_list.py --check`
- `.venv/bin/python scripts/sync_codex_mirror.py --check`
- `.venv/bin/python scripts/sync_agent_contract.py --check`
- `.venv/bin/python scripts/session_handoff.py --check`
- `.venv/bin/python scripts/preflight.py --core-only --no-network`
- `/Users/joonake/.cache/web-crawler-dep002/py311/bin/python -m pytest -q -k "not e2e"`

## 불변 제약
- preflight 는 설치하지 않고 확인만 한다. 다른 점검 항목과 종료 코드 규칙은 바꾸지 않는다.
- `plain_get`·`PLAIN_KWARGS` 와 스킬 정본·하네스 파일은 고치지 않는다(applygo36 ADR-019 하네스 동결).

## 범위 밖(하지 않는 것)
- 점검 주소(httpbin) 변경, 사다리·통지 게이트 동작 변경, 실제 수집 시험.

## 갭 목록
- LOW(GAPS-001 넘김, 할 일 없음): `troubleshooting.md:47` 은 과거 사고 원인 서술이라 당시 이름을 그대로 둔다(HCG-055 범위 결정).
- LOW(GAPS-001 넘김, 할 일 없음): CISA 사이트 피드가 자동 조회를 403 으로 막는다. GitHub 사본 대체 경로가 이미 있다.
- LOW(GAPS-001 넘김): 구동 Chromium 156.0.8078.4 가 안정판 158 보다 두 메이저 뒤다. patchright 1.65 출시 뒤 상한을 함께 올릴 때 다시 잰다(PY311-001 상시 조건).
- LOW(GAPS-001 넘김): Chromium·curl_cffi 내장 libcurl 의 Brotli 판(KEV CVE-2026-111497) 미확인. 다음 보안 인텔 수집에서 잰다.
- LOW(GAPS-001 넘김): 로컬 브랜치 `chore/plan-harness-v2-1104` 의 커밋 319dee0(하네스 v2 갱신)·엔진 사본 8f3277 표시 결함 — applygo36 ADR-019 하네스 동결로 정기 점검 대상. 원본 체크아웃은 2026-11-12 master 로 옮겼고 그 브랜치는 보존했다.
- LOW(GAPS-001 넘김): 병합된 로컬 브랜치·orca 작업트리 barracuda·작업트리 rev5-secintel-dep·`~/.cache/web-crawler-dep001`·`dep002` 정리(사용자 확인 뒤).
- LOW(GAPS-001 넘김, 독립 리뷰 Grok): `bootstrap.py` 가 「준비 안 됨」 사유를 화면에 찍지 않는다.
- LOW(GAPS-001 넘김, 독립 리뷰 Grok 기록): 점 구분 16자리 `+1234.5678.9012.3456` 이 전화번호 경고를 낸다(설계가 정한 넓히기).
- LOW(GAPS-001 넘김): DeepSeek 리뷰어가 2회 판정 없이 종료코드 1 로 끝났다(오류 메시지 없음).
- 닫힘(GAPS-001 뒤 실측): 원본 체크아웃 venv — master 로 옮긴 뒤 `bootstrap.py --core-only` 로 scrapling 0.5.1 갱신, 미충족 0건, 711 통과.
- LOW(PREFLIGHT-001 시작 전 실측): 원본 체크아웃이 master 에 있으면 프로젝트 훅 `shu-guard:main-commit` 이 세션 기본 폴더의 브랜치만 보고, 다른 작업트리의 기능 브랜치 커밋까지 막는다(REV-11 커밋에서 실측). 이번 조각은 원본 체크아웃 기능 브랜치에서 작업해 피한다.

## 종료 분류
