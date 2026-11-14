# PY311-001 계획 승인

**승인일**: 2026-09-28
**승인자**: 저장소 소유자 (세션 시작 지시 "이어서 작업 시작해" 에 따른 자동 모드 진행)

## 설치하는 것

1. `requirements.txt` 의 playwright·patchright 제약을 **바이트 동일**하게 만든다 (ADR-002).
2. `scripts/test_requirements.py` 에 상한 존재 검사와 결합 동일성 검사를 추가한다.
3. `requirements.txt:23` 의 거짓 주장("(둘 다 1.62.x)")을 실측과 일치시킨다.

## 왜 이걸 하는가 (실측 근거)

`.context/CONTEXT.md` 가 2026-09-27 에 남긴 미해결 위험은 "로컬 3.14 vs CI 3.11 이
검증되지 않았다" 였다. 이 세션에서 3.11.15 환경을 직접 만들어 6개 계약 명령을 전부 돌렸다
(3.11.15 기준 573 passed, 5개 검사 전부 exit 0). **이 축은 측정 가능했고 측정하니 멀쩡했다.**

그런데 그 과정에서 `playwright` / `patchright` / `protego` 가 두 환경에서 **서로 다른 버전**으로
설치돼 있음을 발견했다. 파이썬 버전 문제가 아니라 **의존 해석이 인터프리터마다 다르다**는 뜻이다.
그리고 그 두 줄의 결합 규칙은 주석에만 있었다(ADR-002).

## 의도적으로 하지 않는 것

- protego 상한 추가 — 근거 없음.
- pytest 상한 추가 — 3.11/3.14 양쪽 9.1.1 로 같음을 실측했다. 문제는 없다.
- ubuntu/x86_64 검증 — 이 세션은 macOS/arm64 이라 측정 불가. UNVERIFIED 로 남긴다.

## 검증할 것

RED 확인을 먼저 로그로 남긴다. `test_playwright_has_upper_bound` 는 현재 파일에서
상한이 없어서 **반드시 먼저 깨져야 한다**. 깨지지 않으면 그 테스트는 검증력이 없다.

## UNVERIFIED

- ubuntu/x86_64 러너 통과 여부. 측정하지 않았다.
- NORTH STAR 문장의 담당자 승인 (기존 상태 유지).

## REV-2 — ADR 기준점 명시 (2026-10-16)

(REV-2 당시 ADR 기준점 계승 표지: REV-1 sha256 da7eb99e50c39feb1b823cbdfa0f4ffaadaa2e65d455ef71c481ed75b5d91ba4 — REV-3 에서 아래 표지로 넘겼다)

**승인**: 저장소 소유자 — 원문 「권장 작업 진행이죠」 (권장 순서 1번 "REV-1 내용 그대로 ADR 기준점만 추가해 재승인" 에 대한 답)
**사유**: `plan check` 의 유일한 WARN "REV-1는 구형 계획으로 ADR 기준점(adr_basis)이 없다" 를 닫는다.

**범위·순서·완료 기준은 바꾸지 않는다.** 위 REV-1 본문을 그대로 계승하고, 이 계획이
전제로 삼는 결정을 기준점으로 명시만 한다.

| 결정 | 이 계획과의 관계 |
|---|---|
| ADR-001-harness-lean-install | 하네스 경량 설치 — 계획·연속성 검사의 전제 (원장 seq 5 사용자 확정 "영향 없음") |
| ADR-002-playwright-patchright-coupling | 이 계획의 직접 근거 (REV-1 트리거) |

REV-1 이후 실측으로 바뀐 사실(계획 변경 아님, 근거는 `docs/task-contracts/PY311-001.md`):
- ubuntu/x86_64 러너 통과 — 2026-10-01 PR #1 CI 로 실측되어 위 UNVERIFIED 첫 항목은 닫혔다.
- playwright 1.64.0 출시(2026-10-13)·patchright 1.63.0 최신(2026-10-15 실측) — 상한 `<1.64` 유지.

## REV-3 — SEC-001 인터럽트 종료를 과제로 명시 (2026-11-06, 초안 · 미승인)

(REV-3 당시 ADR 기준점 계승 표지: REV-2 sha256 3b255792aedfea981a54bc721145c41cc9a9e2139d93e2eddd06ff70e726c80c — REV-4 에서 아래 표지로 넘겼다)

**사유**: 조각 하네스(사용자 결정 D3)는 최신 승인 계획의 과제에만 조각을 묶는다. REV-2 에는 과제 줄·순서 블록이
없어(`plan show next` → 「순서 첫 미완료 0개」) 어떤 조각도 시작할 수 없다. 정본(`.harness/policy.json`)에 남은
유일한 미완 항목인 SEC-001 인터럽트 종료를 과제로 적는다.

**REV-1·REV-2 의 범위·완료 기준은 바꾸지 않는다.** 위 본문을 그대로 계승하고, 바뀐 줄은 REV-1 계승 표지 한 줄을
설명 문장으로 바꾼 것뿐이다(표지는 한 본문에 하나만 읽히므로 REV-2 표지로 넘겼다).

(REV-3 당시 순서 블록: SEC001-CLOSE — REV-5 에서 아래 순서 블록으로 넘겼다)

- [x] SEC001-CLOSE: SEC-001 인터럽트 종료 — 병합된 #8(97b752b)의 독립 다른-모델 리뷰를 반영하고(지적이 있으면 TDD 로 수정),
  `.harness/policy.json` 의 `interrupt` 를 `none` 으로, `.harness/state.json`·`docs/session-handoff.md` 를 현재 HEAD 기준으로
  갱신해 PY311-001 로 복귀한다. 근거: `docs/task-contracts/SEC-001.md` 「종료 조건」 1~3.

완료 판정(검사 명령): 실행 계약 6종 exit 0, `python scripts/continuity_check.py` 가 interrupt 없음 상태를 통과.

PY311-001 의 상시 조건은 그대로다: 두 패키지 모두 1.65 출시 시 상한을 함께 올린다
(2026-11-06 pypi.org 실측: playwright 최신 1.64.1, patchright 최신 1.64.4 — 둘 다 1.65 미출시 → `<1.65` 유지).

## REV-4 — SEC001-CLOSE 완료 표시 (2026-11-06)

(REV-4 당시 ADR 기준점 계승 표지: REV-3 sha256 b818f7a8517e2588b09819a8ee57796d824c4da78b3d498ef0d7065e7b84b77a — REV-5 에서 아래 표지로 넘겼다)

**사유**: 조각 SEC001-CLOSE 는 닫혔는데(원장 seq 173, 사용자 입력 `8980b676a2fd` 「SEC001-CLOSE 종료 승인」, 종료 커밋 7859f9b)
REV-3 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 「순서 첫 미완료」로 계속 보인다. 완료를 계획에 반영한다.

**범위·순서·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: SEC001-CLOSE 과제 줄의 `[ ]` → `[x]`, 그리고 REV-2 계승
표지 한 줄을 설명 문장으로 바꾼 것(표지는 한 본문에 하나만 읽히므로 REV-3 표지로 넘겼다). REV-3 제목의 「초안 · 미승인」 글귀는
당시 기록이라 그대로 두며, REV-3 은 사용자 입력 `2cb20cc05c8b` 로 승인됐다.

완료 근거(실측): PR #10 병합 `897ed3c`(2026-11-06 21:30 KST), `.harness/policy.json` `interrupt.status` = `none`,
`.harness/state.json` `dirty` = `false`·독립 리뷰 passed(Codex gpt-6.1-sol high, 3회 중 3회째 PASS), 실행 계약 6종 exit 0(674 passed).

이 판으로 순서 블록의 미완료 과제는 0개가 된다. PY311-001 의 상시 조건(두 패키지 모두 1.65 출시 시 상한을 함께 올림)은 그대로다.

## REV-5 — 보안 인텔 재수집과 scrapling 0.5 평가를 과제로 추가 (2026-11-09)

(REV-5 당시 ADR 기준점 계승 표지: REV-4 sha256 96dfafd915cb5c06a5d435e178ac92f341c7ba24632b76478d15b2f67822712e — REV-6 에서 아래 표지로 넘겼다)

**사유**: REV-4 로 순서 블록의 미완료 과제가 0개가 되어(`plan show next` → 「순서 첫 미완료 0개」) 어떤 조각도 시작할 수 없다.
사용자가 다음 과제를 골랐다(입력 「보안 인텔 재수집과 scrapling 0.5 평가를 REV-5 과제로 넣는 개정안 만들어」, 2026-11-09).
순서는 사용자가 정한 대로 보안 인텔 재수집 → scrapling 0.5 평가다. 앞 과제에서 취약점이 나오면 뒤 과제의 급한 정도가 달라진다.

**REV-1~REV-4 의 범위·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: REV-3 순서 블록과 REV-3 계승 표지를 설명 문장으로
바꾼 것(순서 블록과 계승 표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다). 완료된 SEC001-CLOSE 는 순서에 그대로 둔다.

출발 실측(2026-11-09, pypi.org JSON·`.venv` `pip list`·`docs/security/intel-brief-2026-10-31.md`):

| 항목 | 값 |
|------|-----|
| 마지막 보안 인텔 브리프 | 2026-10-31, 「다음 수집: 7일 뒤」 → 2026-11-07 신선도 기준 지남 |
| scrapling | 제약 `>=0.4.8,<0.5`(`requirements.txt:19`), 로컬 0.4.15(2026-08-23), PyPI 최신 0.5.1(2026-11-04) |
| playwright · patchright | 제약 `>=1.62,<1.65`(바이트 동일, ADR-002), 로컬 1.62.0 · 1.62.3, 범위 안 최신 1.64.1 · 1.64.4, 둘 다 1.65 미출시 |
| curl_cffi | 제약 `>=0.16`, 로컬 0.16.3, PyPI 최신 0.17.0(2026-10-26) |

(REV-5 당시 순서 블록: SEC001-CLOSE,SECINTEL-001,DEP-001 — REV-7 에서 아래 순서 블록으로 넘겼다)

- [x] SECINTEL-001: 보안 인텔 재수집 — 설치 의존성·런타임을 공개 취약점 데이터(OSV 등)와 다시 대조하고,
  `docs/security/intel-brief-2026-11-09.md`(공개 저장소라 결과 요약만)와 비공개 증거 폴더 상세 브리프를 남긴다.
  취약점이 나오면 고치지 않고 등급·영향 경로·고칠 과제를 보고한다(수정은 사용자 승인으로 새 과제). 근거: 전역 스킬 `security-program`, `docs/security/SCOPE.md`.
- [x] DEP-001: scrapling 0.5 호환 평가와 런타임 범위 안 갱신 — 0.5 의 바뀐 점을 원문(변경 기록·릴리스 노트)으로 확인하고,
  0.5.1 을 따로 만든 환경(3.14 로컬·3.11 CI 판)에 설치해 스위트와 이 저장소가 쓰는 fetcher 경로를 돌린다. 결과에 따라 상한을 옮기거나(TDD: 상한 검사 먼저 RED)
  `<0.5` 유지 근거를 기록한다. 같은 과제에서 로컬 venv 를 허용 범위 안 최신(playwright·patchright 1.64.x, curl_cffi 0.17.x)으로 맞추되
  playwright·patchright 제약식의 바이트 동일(ADR-002)은 깨지 않는다.

완료 판정(검사 명령, 두 과제 공통): 실행 계약 6종 exit 0(`AGENTS.md` 「제품 변경 전」). DEP-001 은 추가로 3.11 환경의 `pytest -q -k "not e2e"` exit 0.

하지 않는 것: playwright·patchright 상한 `<1.65` 변경(PY311-001 상시 조건 그대로), scrapling 0.5 의 새 기능 도입(호환 확인까지만), 하네스 파일 변경(applygo36 ADR-019 하네스 동결).

## REV-6 — SECINTEL-001 완료 표시와 DEP-001 에 certifi 하한 추가 (2026-11-10)

(REV-6 당시 ADR 기준점 계승 표지: REV-5 sha256 1c334bbd01c035cf91df1361b1668f474ca34890e1e73a67988c39d4471910fa — REV-7 에서 아래 표지로 넘겼다)

**사유**: ① 조각 SECINTEL-001 이 닫혔는데(사용자 입력 `290a5db2c3f7` 「SECINTEL-001 종료 승인」, PR #13 병합 `99218be`) REV-5 과제 줄이
`[ ]` 로 남아 `plan show next` 가 이 과제를 계속 1번으로 보인다. ② 그 조각이 찾은 취약점(간접 의존 certifi 2026.7.22,
GHSA-6q48-6c7w-9gw2 = PYSEC-2026-4320, GHSA DB 등급 CRITICAL, 고친 판 2026.10.19)을 고칠 자리를 사용자가 DEP-001 로 정했다
(입력 「SECINTEL-001 완료 표시하고 certifi 하한을 DEP-001에 넣는 REV-6 개정안 만들어」, 2026-11-10).

**순서는 바꾸지 않는다**(SEC001-CLOSE → SECINTEL-001 → DEP-001). 바뀐 줄은 두 줄뿐이다: SECINTEL-001 과제 줄의 `[ ]` → `[x]`,
그리고 REV-4 계승 표지를 설명 문장으로 바꾼 것(표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다).

SECINTEL-001 완료 근거(실측): 공개 요약 `docs/security/intel-brief-2026-11-09.md`, 비공개 상세 `~/Developer/security-evidence/web-crawler/intel-brief-2026-11-09.md`,
`plan slice close` 검사 6건 통과·종료 분류 4칸 0, 실행 계약 6종 exit 0(674 passed).

DEP-001 에 더하는 범위(REV-5 의 DEP-001 문장은 그대로 두고 아래를 더한다):

- `requirements.txt` 에 `certifi>=2026.10.19` 하한을 둔다(지금은 curl_cffi 가 끌어오는 간접 의존이라 제약이 없다).
  TDD: 하한 검사(`scripts/test_requirements.py`)를 먼저 써서 지금 파일에서 RED 를 확인한 뒤 줄을 넣는다.
- 로컬 venv 의 certifi 를 그 하한 이상으로 갱신하고, OSV 일괄 조회로 설치본 취약점 0건을 다시 확인한다.

DEP-001 완료 판정에 더한다: `scripts/test_requirements.py` 의 certifi 하한 검사 통과, 갱신 뒤 OSV 일괄 조회에서 certifi 권고 0건.

## REV-7 — DEP-001 완료 표시와 scrapling 0.5 판 올림 과제 추가 (2026-11-10)

(REV-7 당시 ADR 기준점 계승 표지: REV-6 sha256 9908100761ae5dc12b99252f44569f8415e95e31ee6825a4b44d884f684320e7 — REV-8 에서 아래 표지로 넘겼다)

**사유**: ① 조각 DEP-001 이 닫혔는데(사용자 입력 `723efaff5977` 「DEP-001 종료 승인」, PR #15 병합 `2a60a8a`) REV-5 과제 줄이
`[ ]` 로 남아 `plan show next` 가 이 과제를 계속 1번으로 보인다. ② 그 조각이 scrapling 0.5 를 비호환으로 판정했고(상한 `<0.5` 유지),
사용자가 판 올림을 다음 과제로 정했다(입력 「DEP-001 완료 표시하고 scrapling 0.5 판 올림 과제를 넣는 REV-7 개정안 만들어」, 2026-11-10).

**REV-1~REV-6 의 범위·완료 기준은 바꾸지 않는다.** 바뀐 줄은 세 줄뿐이다: DEP-001 과제 줄의 `[ ]` → `[x]`, REV-5 순서 블록과
REV-6 계승 표지를 설명 문장으로 바꾼 것(순서 블록과 계승 표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다). 완료된 과제는 순서에 그대로 둔다.

DEP-001 완료 근거(실측): 평가 `docs/reference/scrapling-0.5-compat-2026-11.md`, `requirements.txt` `certifi>=2026.10.19`·scrapling `<0.5` 유지 근거,
`plan slice close` 검사 7건 통과·종료 분류 4칸 0, 실행 계약 6종과 3.11 `pytest -q -k "not e2e"` exit 0(675 passed), 독립 리뷰 3명 PASS,
OSV 설치본 30개 권고 0건.

출발 실측(2026-11-10, DEP-001 평가 문서·`git grep`):

| 무엇 | 실측 |
|:-----|:-----|
| scrapling | 제약 `>=0.4.8,<0.5`, 로컬 0.4.15, PyPI 최신 0.5.1(2026-11-04) |
| 0.5 에서 깨지는 곳 | 코드 import `scripts/utils.py:424`(`plain_dynamic`)·`scripts/preflight.py:91`, 0.5.1 시험 4건 실패(3.14·3.11 같음) |
| 이름만 쓰는 곳 | `scripts/profile_policy.py`·`scripts/domain_profile.py`(분류표), 스킬 정본 `.claude/skills/web-crawler/`(SKILL.md·references 3개), `scripts/scrapling_reference.md`, `README.md`, `docs/agents-reference.md`, `docs/crawl-reference.md`, 프로필 3개(`fetcher_type` 2개·notes 1개) |
| 사다리 위치 | `dynamicfetcher`·`dynamicsession` = 사다리 A 3단 `js_render`(이음매 위). `StealthyFetcher` 는 이음매 아래 사다리 B(통지 게이트 대상) |

(REV-7 당시 순서 블록: SEC001-CLOSE,SECINTEL-001,DEP-001,DEP-002 — REV-9 에서 아래 순서 블록으로 넘겼다)

- [x] DEP-002: scrapling 0.5 판 올림 — 0.5 에서 없어진 `DynamicFetcher`·`DynamicSession` 경로를 옮기고 상한을 `>=0.5.1,<0.6` 으로 올린다.
  먼저 사다리 3단 대체 설계(아래 불변 조건을 지키는 방법)를 조각 계약에 적어 사용자 승인을 받는다. 그다음 TDD 로 상한 검사(`test_scrapling_has_upper_bound`)를
  먼저 RED 로 바꾸고, 코드(`plain_dynamic`·`preflight`·분류표)·시험·스킬 정본 문서(미러는 `sync_codex_mirror.py` 로 재생성)·참조 문서·프로필을 옮긴다.
  옛 프로필이 쓰는 옛 이름(`DynamicFetcher` 등)은 `profile_policy.py` 의 옛 이름 매핑으로 계속 읽는다.

불변 조건: 사다리 3단(일반 JS 렌더)은 **이음매 위에 남는다** — 3단을 `StealthyFetcher`(위장 백엔드)로 바꿔 통지 게이트 없이 이음매를 넘지 않는다
(`AGENTS.md` 「안전 — 하드룰」 첫 줄). playwright·patchright 제약식 바이트 동일(ADR-002)과 상한 `<1.65` 는 그대로다.

완료 판정(검사 명령): 실행 계약 6종 exit 0, 3.11 환경 `pytest -q -k "not e2e"` exit 0, scrapling 0.5.x 설치 환경에서 `scripts/preflight.py` CORE FAIL 0,
코드·스킬 정본·문서에서 `from scrapling.fetchers import DynamicFetcher`·`DynamicSession` 0건(옛 이름 매핑 제외).

하지 않는 것: scrapling 0.5 새 기능(`RemoteSession`·`record_requests`·`pierce_shadow` 등) 도입, playwright·patchright 상한 변경, 하네스 파일 변경(applygo36 ADR-019 하네스 동결).
스킬 정본 `.claude/skills/web-crawler/` 수정이 전역 관문(HCG) 대상이면 관문 보고와 승인을 거친다.

## REV-8 — DEP-002 완료 표시 (2026-11-11)

(REV-8 당시 ADR 기준점 계승 표지: REV-7 sha256 f056cdcf1da5b59d58d1aa86600fe3f642abfcab62eddd52269ffaa545851d67 — REV-9 에서 아래 표지로 넘겼다)

**사유**: 조각 DEP-002 가 닫혔는데(원장 seq 229, 사용자 입력 `9c52d03c0832` 「DEP-002 종료 승인」, 종료 커밋 bf66e99, PR #17 병합 `f633f83`)
REV-7 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 계속 1번으로 보인다. 완료를 계획에 반영한다
(사용자 입력 「DEP-002 완료 표시하는 REV-8 개정안 만들어」, 2026-11-11).

**범위·순서·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: DEP-002 과제 줄의 `[ ]` → `[x]`, 그리고 REV-6 계승 표지를
설명 문장으로 바꾼 것(표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다). REV-7 순서 블록은 그대로 둔다.

DEP-002 완료 근거(실측): `requirements.txt` `scrapling[fetchers]>=0.5.1,<0.6`, 사다리 3단 `scripts/utils.py plain_dynamic` 을 playwright 직접 호출
(위장 없는 Chromium)로 다시 만듦, 스킬 정본 수정은 전역 관문 HCG-055 승인 범위 안, `plan slice close` 검사 8건 통과·종료 분류 4칸 0,
실행 계약 6종과 3.11 `pytest -q -k "not e2e"` exit 0(3.14.7·3.11.15 모두 681 passed), scrapling 0.5.1 환경 `scripts/preflight.py` CORE FAIL 0,
독립 리뷰 3명(Codex·DeepSeek·Grok) 1회차 공통 MEDIUM 을 고친 뒤 재확인 PASS. 결과 기록은 `docs/reference/scrapling-0.5-compat-2026-11.md` 5절.

이 판으로 순서 블록의 미완료 과제는 0개가 된다. 다음 과제는 사용자가 정해 새 개정으로 넣는다. PY311-001 의 상시 조건
(두 패키지 모두 1.65 출시 시 playwright·patchright 상한을 함께 올림)은 그대로다. DEP-002 조각에서 넘긴 LOW 갭 14건은
`docs/task-contracts/DEP-002.slice.md` 「갭 목록」에 있고, 다음 조각이나 정리 슬롯에서 다룬다.

## REV-9 — DEP-002 LOW 갭 정리를 과제로 추가 (2026-11-11)

(REV-9 당시 ADR 기준점 계승 표지: REV-8 sha256 055c7f63bf35079e7b5d07e1eb2e7cf6097f17e738530192d9a3f167c1aba321 — REV-10 에서 아래 표지로 넘겼다)

**사유**: REV-8 로 순서 블록의 미완료 과제가 0개가 되어(`plan show next` → 「순서 첫 미완료 0개」) 어떤 조각도 시작할 수 없다.
사용자가 다음 과제를 골랐다(입력 「DEP-002 LOW 갭 정리를 다음 과제로 넣는 REV-9 개정안 만들어」, 2026-11-11).

**REV-1~REV-8 의 범위·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: REV-7 순서 블록과 REV-8 계승 표지를 설명 문장으로
바꾼 것(순서 블록과 계승 표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다). 완료된 과제는 순서에 그대로 둔다.

출발 실측(2026-11-11, `docs/task-contracts/DEP-002.slice.md` 「갭 목록」 LOW 13건, master `a513ecc`):

| 갭(계약 줄) | 실측 | 이번 과제 |
|:-----|:-----|:-----|
| 3단 예외 전파·`retries` 없음(57) | `docs/crawl-reference.md:270` 「네트워크 타임아웃 → 3회 재시도 후 스킵」이 3단 `plain_dynamic` 동작(재시도 없음, 예외 전파)과 다르다 | 고친다 |
| 국제 전화번호 오탐(52) | `detect_pii([{'t':'+1 415 555 2671 2026-11-06 접수'}])` → 「전화번호 패턴 감지」 | 고친다 |
| certifi 하한 검사 우회(46) | `scripts/test_requirements.py:227` 가 환경 마커·사전 릴리스·여러 줄 선언을 거르지 못한다 | 고친다 |
| 기존 venv 자동 갱신 없음(47) | `scripts/bootstrap.py py_deps_ready()` 는 import 만 보고 판 하한을 보지 않는다(0.4.15 venv 도 준비됨으로 판정) | 고친다 |
| `_forbid_stealth` 범위(58) | `scripts/test_utils.py:723` 이 `patchright.sync_api.sync_playwright` 만 막는다 | 고친다 |
| 비공개 `Response` 경로(55) | `scripts/utils.py:436` `scrapling.engines.toolbelt.custom` 을 직접 고정하는 시험이 없다(실제 Chromium 시험이 간접으로만 깨진다) | 고친다 |
| `plaindynamic` 키(54) | `scripts/profile_policy.py:67` 에 있다 | 닫힘 기록만 |
| `troubleshooting.md:47`(59) | HCG-055 범위 결정으로 당시 이름 유지 | 할 일 없음, 기록만 |
| Chromium 156 대 158(48) | patchright 1.65 미출시 → PY311-001 상시 조건 | 넘김 |
| Brotli 판 미확인(49) | 다음 보안 인텔 수집에서 잰다 | 넘김 |
| CISA 피드 403(50) | GitHub 사본 대체 경로가 이미 있다 | 할 일 없음, 기록만 |
| 엔진 사본 결함·로컬 커밋 319dee0(51) | applygo36 ADR-019 하네스 동결 | 넘김(정기 점검) |
| 병합 브랜치·작업트리 정리(53) | 저장소 밖 정리, 사용자 확인 필요 | 넘김(사용자 확인 뒤) |

(REV-9 당시 순서 블록: SEC001-CLOSE,SECINTEL-001,DEP-001,DEP-002,GAPS-001 — REV-11 에서 아래 순서 블록으로 넘겼다)

- [x] GAPS-001: DEP-002 LOW 갭 정리 — 위 표에서 「고친다」 6건을 고친다. 3단 재시도는 조각 계약에 문서를 동작에 맞출지
  `plain_dynamic` 에 재시도를 더할지 정해 사용자 승인을 받은 뒤 진행한다(0건 중단 규칙·사다리 A 경계는 그대로). 나머지 5건은 TDD 로
  시험을 먼저 RED 로 확인한 뒤 고친다. 「닫힘·할 일 없음·넘김」 7건은 조각 계약 갭 목록에 사유와 함께 옮긴다.

완료 판정(검사 명령): 실행 계약 6종 exit 0, 3.11 환경 `pytest -q -k "not e2e"` exit 0, 「고친다」 6건마다 RED 를 먼저 확인한 시험(또는 문서 계약 시험) 통과.

하지 않는 것: 스킬 정본 `.claude/skills/web-crawler/` 수정(필요해지면 전역 관문 HCG 를 거친다), 사다리 B·통지 게이트 동작 변경,
playwright·patchright 상한 변경, 하네스 파일 변경(applygo36 ADR-019 하네스 동결), 저장소 밖 브랜치·작업트리 정리.

## REV-10 — GAPS-001 완료 표시 (2026-11-12)

(REV-10 당시 ADR 기준점 계승 표지: REV-9 sha256 21c40e6e15416c83adef2069dea67df29014e7ea74b4e0bc5a50c7264d69c3a8 — REV-11 에서 아래 표지로 넘겼다)

**사유**: 조각 GAPS-001 이 닫혔는데(원장 seq 242, 사용자 입력 `89928b4d462d` 「GAPS-001 종료 승인」, 종료 커밋 e9c7d22, PR #20 병합 `33e21da`)
REV-9 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 계속 1번으로 보인다. 완료를 계획에 반영한다
(사용자 입력 「GAPS-001 완료 표시하는 REV-10 개정안 만들어」, 2026-11-12).

**범위·순서·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: GAPS-001 과제 줄의 `[ ]` → `[x]`, 그리고 REV-8 계승 표지를
설명 문장으로 바꾼 것(표지는 한 본문에 첫 하나만 읽히므로 이 절로 넘겼다). REV-9 순서 블록은 그대로 둔다.

GAPS-001 완료 근거(실측): 「고친다」 6건 모두 RED 확인 뒤 GREEN — `plain_dynamic` `retries=3`·`retry_delay=1`(1·2단·옛 3단과 같은 뜻),
국제 전화번호 미탐 수정, certifi 하한 packaging 의미 검사, `bootstrap.py` 설치판·제약식 대조, `_forbid_stealth` 확장, 비공개 `Response` 경로 고정.
`plan slice close` 검사 8건 통과·종료 분류 4칸 0, 3.14.7·3.11.15 모두 711 passed, 독립 리뷰 Codex·Grok PASS(공통 LOW 1건 수정,
DeepSeek 은 2회 판정 없이 종료 — 계약 갭 목록에 기록).

이 판으로 순서 블록의 미완료 과제는 0개가 된다. 다음 과제는 사용자가 정해 새 개정으로 넣는다. 넘긴 LOW 갭은
`docs/task-contracts/GAPS-001.slice.md` 「갭 목록」에 있다. PY311-001 의 상시 조건(두 패키지 모두 1.65 출시 시 상한을 함께 올림)은 그대로다.

## REV-11 — preflight HTTP 점검을 사다리 1단 `plain_get` 으로 바꾸는 과제 추가 (2026-11-12)

(REV-11 당시 ADR 기준점 계승 표지: REV-10 sha256 94578e3ee87512768db33f7ccc394466ddf4b085108d4c767699446c68e0de2e — REV-12 에서 아래 표지로 넘겼다)

**사유**: REV-10 으로 순서 블록의 미완료 과제가 0개가 되었다. 원본 체크아웃 venv 를 bootstrap 으로 갱신하는 중에
preflight 가 지어낸 출처를 붙인 요청을 보내는 것을 실측했고, 사용자가 이를 다음 과제로 골랐다
(입력 「preflight HTTP 점검을 plain_get으로 바꾸는 과제를 넣는 REV-11 개정안 만들어」, 2026-11-12).

**REV-1~REV-10 의 범위·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: REV-9 순서 블록과 REV-9 계승 표지를 설명 문장으로
바꾼 것이다(둘 다 한 본문에서 첫 하나만 읽히므로 REV-11 절로 옮겼다). 끝난 과제도 순서 블록에 남긴다.

출발 실측(2026-11-12, master `6760b8a`, scrapling 0.5.1):

| 항목 | 출발 실측 값 |
|:--------|:--------|
| 호출 | `scripts/preflight.py:127` `check_http_fetch()` 가 `Fetcher().get("https://httpbin.org/html")` — scrapling 기본값 그대로 |
| 나간 요청 | 원본 체크아웃 bootstrap(`--core-only`) 로그: `Fetched (200) <GET https://httpbin.org/html> (referer: https://www.google.com/)` — 지어낸 출처 |
| 경고 | `Fetcher()` 인스턴스 생성이 「This logic is deprecated now … Use \`Fetcher.configure()\` instead」 경고를 낸다(인스턴스 없이 `Fetcher.get` 을 부르는 `plain_get` 은 내지 않는다) |
| 다른 호출처 | 시험 밖 `scripts/*.py` 에서 scrapling 기본값으로 직접 요청하는 곳은 이 한 곳(`git grep`) |
| 시험 | preflight 용 시험 파일이 없다 |

(REV-11 당시 순서 블록: SEC001-CLOSE → SECINTEL-001 → DEP-001 → DEP-002 → GAPS-001 → PREFLIGHT-001 — REV-13 에서 아래 새 블록으로 옮겼다)

- [x] PREFLIGHT-001: preflight HTTP 점검을 사다리 1단으로 — `check_http_fetch()` 가 `utils.plain_get` 을 부르게 바꿔
  위장 기본값(`impersonate`·`stealthy_headers`, 지어낸 Referer)을 끄고 `Fetcher()` 인스턴스 경고를 없앤다. TDD: 네트워크 없이
  `plain_get` 경유와 요청 인자(위장 끔)를 확인하는 시험을 먼저 RED 로 본 뒤 고친다. 판정(200=PASS, 그 밖·예외=WARN)과
  `--no-network` 동작은 그대로다.

완료 판정(검사 명령): 실행 계약 6종 exit 0, 3.11 환경 `pytest -q -k "not e2e"` exit 0, `scripts/preflight.py --core-only --no-network`
CORE FAIL 0, 네트워크가 되는 환경에서 `scripts/preflight.py --core-only` 로그에 `referer: https://www.google.com/` 이 없다.

하지 않는 것: preflight 의 다른 점검 항목 변경, 스킬 정본 수정, 사다리·통지 게이트 동작 변경, 하네스 파일 변경(applygo36 ADR-019 하네스 동결).

## REV-12 — PREFLIGHT-001 완료 표시 (2026-11-13)

(REV-12 당시 ADR 기준점 계승 표지: REV-11 sha256 d35feccf7687a1a04686e562f1879b1d69fca32731ba795ba60e5d0461ed9716 — REV-13 에서 아래 표지로 넘겼다)

**사유**: 조각 PREFLIGHT-001 이 닫혔는데(사용자 입력 `440947457398` 「PREFLIGHT-001 종료 승인」, 종료 커밋 e922a87, PR #23 병합 `316f95d`)
REV-11 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 계속 다음 과제로 보인다. 완료를 계획에 반영한다
(사용자 입력 「PREFLIGHT-001 완료 표시하는 REV-12 개정안 만들어」, 2026-11-13).

**범위·순서·완료 기준은 그대로 둔다.** 고친 줄은 두 줄이다: PREFLIGHT-001 과제 줄의 `[ ]` → `[x]`, 그리고 REV-11 절의 계승 표지를
설명 문장으로 바꾼 것(한 본문에서 첫 표지 하나만 읽히므로 이 절로 옮겼다). REV-11 순서 블록은 손대지 않는다.

PREFLIGHT-001 완료 근거(실측): `check_http_fetch()` 가 `utils.plain_get(HTTP_CHECK_URL)` 로 요청한다. 새 `scripts/test_preflight.py` 6건은
옛 `preflight.py` 에서 6건 모두 단언 실패, 새 코드에서 6건 통과. 로컬 서버가 받은 요청 헤더는 `Host`·`Accept-Encoding`·`User-Agent` 셋뿐이고
Referer 가 없다. 네트워크 실행 `preflight.py --core-only` 로그는 `(referer: None)`·`[PASS] HTTP fetch (httpbin) — status 200`, deprecated 0줄.
메시지 없는 예외에서 IndexError 로 죽던 경로도 WARN 으로 고쳤다(HTTP 점검 한 곳). `plan slice close` 검사 8건 통과·종료 분류 4칸 0,
3.14·3.11 모두 717 passed, 독립 리뷰 Codex·Grok PASS(공통 LOW 1건 수정, DeepSeek 은 OpenCode Go 구독 없음으로 판정 없이 종료).

이 판으로 순서 블록의 미완료 과제는 다시 0개다. 다음 과제는 사용자가 정해 새 개정으로 넣는다. 넘긴 LOW 갭은
`docs/task-contracts/PREFLIGHT-001.slice.md` 「갭 목록」에 있다. PY311-001 의 상시 조건(두 패키지 모두 1.65 출시 시 상한을 함께 올림)은 그대로다.

## REV-13 — preflight 예외 처리 5곳과 bootstrap 「준비 안 됨」 사유 표시를 과제로 추가 (2026-11-13)

(REV-13 당시 ADR 기준점 계승 표지: REV-12 sha256 bdda30f4e4726a41c9ca6b86102bb35079a2e4bc2c88eb865a1498bfb752f6b4 — REV-14 에서 아래 표지로 넘겼다)

**사유**: REV-12 로 순서 블록의 미완료 과제가 0개가 되었다. PREFLIGHT-001·GAPS-001 이 넘긴 LOW 갭 가운데 제품 경로의 작은 결함 두 가지를
사용자가 다음 과제로 골랐다(입력 「preflight 남은 예외 처리 5곳과 bootstrap 사유 표시를 고치는 과제를 넣는 REV-13 개정안 만들어」, 2026-11-13).

**REV-1~REV-12 의 범위·완료 기준은 그대로 둔다.** 고친 줄은 두 줄이다: REV-11 순서 블록과 REV-12 계승 표지를 설명 문장으로 바꾼 것이다
(둘 다 한 본문에서 첫 하나만 읽히므로 이 절로 옮겼다). 끝난 과제도 새 순서 블록에 남긴다.

출발 실측(2026-11-13, master `6798421`):

| 대상 | REV-13 출발 시점 값 |
|:---|:---|
| preflight 예외 처리 | `scripts/preflight.py` 85·98·118·176·193행이 `str(e).splitlines()[0]` 를 그대로 쓴다. 메시지 없는 예외가 오면 IndexError 로 preflight 가 죽는다 — `check_agent_browser_ready()` 에 빈 `OSError()` 를 넣어 재현했다. HTTP 점검 한 곳은 PREFLIGHT-001 에서 예외 이름으로 대체해 고쳤다 |
| bootstrap 사유 | `scripts/bootstrap.py:159` `do_python_deps()` 는 `py_deps_ready()` 가 거짓이면 이유 없이 `pip install -r` 로 넘어간다. `py_deps_ready()` 는 import 실패를 삼키고, `requirements_unsatisfied()` 가 돌려준 문제 목록도 화면에 나오지 않는다 |

(REV-13 순서 블록: SEC001-CLOSE → SECINTEL-001 → DEP-001 → DEP-002 → GAPS-001 → PREFLIGHT-001 → GAPS-002 — REV-15 에서 아래 새 블록으로 옮겼다. 이 일곱 과제는 모두 완료다.)

- [x] GAPS-002: preflight·bootstrap 진단 출력 보강 — ① `scripts/preflight.py` 남은 5곳이 메시지 없는 예외에서도 죽지 않고
  각 점검의 원래 판정(FAIL 또는 WARN)과 예외 이름을 기록한다. ② `scripts/bootstrap.py` 가 Python 의존성을 다시 설치하기 전에
  「준비 안 됨」 사유(import 실패 모듈·예외, `requirements_unsatisfied()` 문제 목록)를 화면에 찍는다. TDD: 각 동작을 먼저 RED 로 본 뒤 고친다.

GAPS-002 완료 판정(검사 명령): 실행 계약 6종과 3.11 환경 `pytest -q -k "not e2e"` 가 모두 exit 0, `scripts/preflight.py --core-only --no-network`
CORE FAIL 0, 새 시험이 옛 코드에서 실패하고 새 코드에서 통과한다.

하지 않는 것: 점검 항목·판정 등급·종료 코드 규칙 변경, 설치 동작(언제 `pip install` 을 돌리는지) 변경, 스킬 정본 수정,
하네스 파일 변경(applygo36 ADR-019 하네스 동결).

## REV-14 — GAPS-002 완료 표시 (2026-11-14)

(REV-14 당시 ADR 기준점 계승 표지: REV-13 sha256 471ca041f809ee1546516e9fbc51aa02d2ca46ebe6c35a796245544ec29e468e — REV-15 에서 아래 표지로 넘겼다)

**사유**: 조각 GAPS-002 가 닫혔는데(사용자 입력 `c4ea93ed7707` 「GAPS-002 종료 승인」, 종료 커밋 7301c62, PR #26 병합 `31a4754`)
REV-13 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 계속 다음 과제로 보인다. 완료를 계획에 반영한다
(사용자 입력 `77cfa7581119` 「GAPS-002 완료 표시하는 REV-14 개정안 만들어」, 2026-11-14).

**범위·순서·완료 기준은 그대로 둔다.** 이번 판에서 고친 줄은 두 줄이다: GAPS-002 과제 줄의 `[ ]` → `[x]`, 그리고 REV-13 절의 계승 표지를
설명 문장으로 바꾼 것(한 본문에서 첫 표지 하나만 읽히므로 이 절로 옮겼다). REV-13 순서 블록은 손대지 않는다.

GAPS-002 완료 근거(실측): `scripts/preflight.py` 다섯 점검(import·Fetcher 로드·Chromium 실행·agent-browser 2곳)이 `_first_line()` 을 거쳐
메시지 없는 예외에도 원래 판정(FAIL·WARN)과 예외 이름을 남긴다. `scripts/bootstrap.py` 는 `py_deps_problems()` 사유를 재설치 전에
「준비 안 됨: …」 한 줄씩 찍고, 준비 판정과 pip 호출 시점은 옛 코드와 같다. 새 시험 11건은 옛 코드에서 9건 실패(2건은 회귀 보호),
새 코드에서 모두 통과. `plan slice close` 검사 8건 통과·종료 분류 4칸 0, 독립 리뷰 Codex·Grok PASS(Grok LOW 1건 수정,
DeepSeek 은 OpenCode Go 구독 없음으로 판정 없이 종료).

REV-14 기준으로 순서 블록에 남은 미완료 과제는 없다. 다음 과제는 사용자가 정해 새 개정으로 넣는다. 넘긴 LOW 갭은
`docs/task-contracts/GAPS-002.slice.md` 「갭 목록」에 있고, 닫을 때 한 번 실패한 `test_rate_limiter_enforces_delay`(벽시계 경계,
0.499…초 < 0.5초, 재실행 5회 통과)는 다음 조각 갭 목록에 옮긴다. PY311-001 의 상시 조건(두 패키지 모두 1.65 출시 시 상한을 함께 올림)은 그대로다.

## REV-15 — 실사용 시험 결함 보강과 무료 최신 도구 도입 (2026-11-14)

<!-- ADR-BASIS:carry-forward REV-14 sha256:52266ae588273748a194e1276c60e416b0be55de5af7900ddf9bba2187b9801f -->

**사유**: DIR-003(실사용 시험) 지시로 한국대학신문(유학생 기사 10건)·그룹웨어(3일 공문 5건)를 실제 수집하며
결함 12건을 실측했다. 사용자가 「부족한 점을 체크리스트로 원장에 넣고, 무료 최신 도구로 상용 수준까지 고도화」를
지시했다(2026-11-14). 아래 7개 과제가 그 체크리스트다. 무료 도구는 오늘 임시 환경에서 효과를 실측한 것만 넣었다
(trafilatura 본문 일치율 0.60~0.94, markitdown xlsx·pdf 변환 성공).

**REV-1~REV-14 의 범위·완료 기준은 그대로 둔다.** 이번 판에서 바꾼 것: REV-13 순서 블록과 REV-14 계승 표지를
설명 문장으로 옮기고(각각 한 본문에서 첫 하나만 읽힌다), 아래에 새 순서 블록과 과제를 더했다. 끝난 과제도 새 블록에 남긴다.

실사용 실측 요약(2026-11-14, master `2aa7727`):

| 결함 | 실측한 것 | 담은 과제 |
|:-----|:----------|:----------|
| F1·F2 | `plain_get` 가 `Accept` 를 안 보내 news.unn.net 이 검색어를 무시하고 전체 268,032 건을 줬고, 검증은 그 틀린 결과를 통과시켰다 | ACC-001 |
| F8 | 개인정보 감지가 내려받은 파일 내용을 안 봐 유학생 명단 첨부를 놓쳤다 | SAFE-001 |
| F10 | 열람만으로 상태가 바뀌는 화면을 가려내는 안내가 없다 | SAFE-001 |
| F7·F11 | 첨부 확장자가 지워지고, 쿠키를 도메인별로 옮기는 도우미가 없다 | SAFE-002 |
| F12 | 프로필 16개가 모두 사다리 A — 사다리 B 실효성 측정 0건 | BOT-001 |
| F3·F5·F9 | 검색어 의미·이름→주소·로그인 파일 저장 템플릿이 스킬에 없다 | DOC-001 |

<!-- PLAN-ORDER: SEC001-CLOSE,SECINTEL-001,DEP-001,DEP-002,GAPS-001,PREFLIGHT-001,GAPS-002,SAFE-001,ACC-001,BENCH-001,CAP-001,EXTRACT-001,SAFE-002,BOT-001,DOC-001 -->

- [ ] SAFE-001: 내려받은 파일까지 개인정보를 검사한다 — markitdown 으로 xlsx·pdf·docx 를 글자로 바꿔 `detect_pii` 에
  넣는 도우미(오늘 유학생 명단 첨부를 놓친 F8)와 이름 열·명단 형태 감지 규칙 보강. 열람만으로 상태가 바뀌는 화면
  (미확인 문서함·일괄 확인)을 수집 전에 알리는 규칙을 스킬 Step 2-A 에 넣는다(F10). TDD.
- [ ] ACC-001: `plain_get`·`plain_session` 이 정직한 `Accept: text/html,…` 를 보내게 하고(없으면 검색어를 무시하고 전체
  목록을 주던 F1), 검색 결과에 검색 조건이 실제로 적용됐는지 확인하는 검사를 더한다(F2). 위장 헤더는 더하지 않는다. TDD.
- [ ] BENCH-001: 상용 대비 성능을 숫자로 재는 재현 벤치마크와 완료 게이트를 만든다 — 고정 대상(로컬 샌드박스 +
  안전한 공개 사이트 + 공개 봇탐지·CAPTCHA 감지 시험 페이지)에 차원별 점수(추출 정확도·필드 채움률·사다리 단계별
  성공률·안티봇 시험 통과율·CAPTCHA 감지율·견고성[재시도·0건 보호])를 매기는 `scripts/benchmark.py` 와 루브릭을
  만든다. 「상용 대비 N%」는 이 루브릭 점수로 정의한다(절대값이 아니라 정의된 기준). 목표 점수(사용자 정의, 기본 90점)
  미달이면 BOT-001·EXTRACT-001 조각을 닫지 못하게 완료 게이트에 건다. CAPTCHA 는 감지율·수동 핸드오프 성공률만
  잰다(자동 풀이 측정 아님). TDD.
- [ ] CAP-001: CAPTCHA 감지 → 사람 개입 수동 핸드오프를 매끄럽게 한다. 챌린지를 만나면 멈추고 사용자가 브라우저에서
  직접 푼 뒤 그 세션으로 수집을 잇는 흐름(지금 되는 방식)을 도우미·스킬 절차로 정리한다. 자동 풀이·우회는 범위 밖(하드룰). TDD.
- [ ] EXTRACT-001: 본문 자동 추출을 trafilatura 로 더한다 — 사이트별 셀렉터가 없을 때 기사·공문 본문·제목·날짜를 추출
  (오늘 한국대학신문 일치율 0.60~0.94 실측). 셀렉터가 있으면 그대로 쓰고 trafilatura 는 폴백·검증용. TDD.
- [ ] SAFE-002: agent-browser 상태에서 대상 도메인 쿠키만 골라 `output/<도메인>/cookies.json` 으로 옮기는 `utils`
  도우미(F11)와, 첨부 저장 시 확장자를 보존하는 수정(F7). TDD.
- [ ] BOT-001: 사다리 B(4·5·6단) 지문·스텔스 실효성을 공개 봇탐지 시험 페이지·로컬 차단 페이지로 측정하고, 걸리는 항목만
  최신화한다. 무료 대안 camoufox(5단 후보)를 같은 시험으로 비교한다. 통지 게이트가 4단 진입 전에 실제로 멈추는지 회귀
  시험으로 잠근다(F12). CAPTCHA 자동 풀이·우회는 범위 밖.
- [ ] DOC-001: 스킬·참조 문서 보강 — 「로그인 세션 + 파일·PDF 저장」 수집 템플릿(F9), 검색 인자 의미가 사이트마다
  다르니 수집 뒤 관련성 재확인(F3), 이름→주소 후보 확인 절차(F5). 코드 동작 변경 없음.

REV-15 완료 판정: 각 과제를 조각(slice)으로 TDD 로 닫는다. 실행 계약 6종과 3.11 환경 `pytest -q -k "not e2e"` 가 모두
exit 0 이고, 새 시험이 옛 코드에서 실패하고 새 코드에서 통과한다.

하지 않는 것: **CAPTCHA 자동 풀이·우회(reCAPTCHA/hCaptcha 를 프로그램으로 푸는 것) — AGENTS.md 안전 하드룰 유지.**
설치 동작(언제 `pip install` 하는지) 변경, 스킬 정본 임의 변경, 하네스 파일 변경(applygo36 ADR-019 하네스 동결).
