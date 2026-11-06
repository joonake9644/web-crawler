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

<!-- PLAN-ORDER: SEC001-CLOSE -->

- [x] SEC001-CLOSE: SEC-001 인터럽트 종료 — 병합된 #8(97b752b)의 독립 다른-모델 리뷰를 반영하고(지적이 있으면 TDD 로 수정),
  `.harness/policy.json` 의 `interrupt` 를 `none` 으로, `.harness/state.json`·`docs/session-handoff.md` 를 현재 HEAD 기준으로
  갱신해 PY311-001 로 복귀한다. 근거: `docs/task-contracts/SEC-001.md` 「종료 조건」 1~3.

완료 판정(검사 명령): 실행 계약 6종 exit 0, `python scripts/continuity_check.py` 가 interrupt 없음 상태를 통과.

PY311-001 의 상시 조건은 그대로다: 두 패키지 모두 1.65 출시 시 상한을 함께 올린다
(2026-11-06 pypi.org 실측: playwright 최신 1.64.1, patchright 최신 1.64.4 — 둘 다 1.65 미출시 → `<1.65` 유지).

## REV-4 — SEC001-CLOSE 완료 표시 (2026-11-06)

<!-- ADR-BASIS:carry-forward REV-3 sha256:b818f7a8517e2588b09819a8ee57796d824c4da78b3d498ef0d7065e7b84b77a -->

**사유**: 조각 SEC001-CLOSE 는 닫혔는데(원장 seq 173, 사용자 입력 `8980b676a2fd` 「SEC001-CLOSE 종료 승인」, 종료 커밋 7859f9b)
REV-3 과제 줄이 `[ ]` 로 남아 `plan show next` 가 이 과제를 「순서 첫 미완료」로 계속 보인다. 완료를 계획에 반영한다.

**범위·순서·완료 기준은 바꾸지 않는다.** 바뀐 줄은 두 줄뿐이다: SEC001-CLOSE 과제 줄의 `[ ]` → `[x]`, 그리고 REV-2 계승
표지 한 줄을 설명 문장으로 바꾼 것(표지는 한 본문에 하나만 읽히므로 REV-3 표지로 넘겼다). REV-3 제목의 「초안 · 미승인」 글귀는
당시 기록이라 그대로 두며, REV-3 은 사용자 입력 `2cb20cc05c8b` 로 승인됐다.

완료 근거(실측): PR #10 병합 `897ed3c`(2026-11-06 21:30 KST), `.harness/policy.json` `interrupt.status` = `none`,
`.harness/state.json` `dirty` = `false`·독립 리뷰 passed(Codex gpt-6.1-sol high, 3회 중 3회째 PASS), 실행 계약 6종 exit 0(674 passed).

이 판으로 순서 블록의 미완료 과제는 0개가 된다. PY311-001 의 상시 조건(두 패키지 모두 1.65 출시 시 상한을 함께 올림)은 그대로다.
