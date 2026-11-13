# 세션 핸드오프

> 이 파일은 **생성물**이다. `python scripts/session_handoff.py write` 로 만든다.
>
> `--check` 가 잡는 것: **정본(state/policy)이 바뀌었는데 문서가 따라가지 않은 것**.
> `--check` 가 **못** 잡는 것: 이 본문 안의 문장을 손으로 고치는 것.
> 정본이 아닌 본문은 사람이 읽는 설명일 뿐이라 기계가 검증할 수 없다.
> 정본은 `.harness/state.json` 이고, 생성기는 `scripts/session_handoff.py` 다.

다음 세션은 이 파일과 `.harness/state.json` 만 읽으면 된다. 이전 대화 이력은 근거가 아니다.

- 입력 다이제스트: `7be220b8aea992228237df6908fcd75967e6926fadc89cead7ae06793447a7ec`

## 상태 한 줄 요약

- 활성 작업: **PY311-001** — 계약 `docs/task-contracts/PY311-001.md`
- NORTH STAR: URL과 수집 항목을 받아 사이트를 정찰·대량수집하고 엑셀로 내보내는 범용 웹 크롤링 에이전트 — 문서에 적힌 대로 따라 하면 죽지 않는다 (`GOAL-001`)
- 단계: `VERIFY` / dirty=`False`
- 검증 커밋: `497ce5b`
- 작업 도구: **codex/gpt-6.1-sol (reasoning high) · grok-4.7 (xhigh) — opencode-go/deepseek-v4.1-flash#max 는 판정 없이 종료(exit 1, 「An active OpenCode Go subscription is required」)**

## 실측 검증 (write 시점에 돌린 결과다)

측정 시점 HEAD: `316f95d` · 브랜치 `chore/rev12-preflight-done`

> ⚠ **출처**: 아래 결과는 이 문서를 커밋하기 **전의 작업 트리**에서 돌았다.
> `write` 는 커밋 전에 불리므로 위 해시는 이 문서를 담는 커밋의 **부모**다.
> 그래서 그 커밋을 체크아웃해 `baseline` 을 다시 돌리면 통과 수가 **다를 수 있다** —
> 아래 수는 '이 커밋의 트리'가 아니라 '그 커밋 직전의 작업 트리'의 실측이다.
> 이 문서를 커밋한 다음 다시 생성하면(HEAD 가 바뀐다) 수치가 맞춰진다.

| 항목 | 명령 | 결과 |
|---|---|---|
| baseline | `python -m pytest -q -k "not e2e"` | exit=0 ✅ — 717 passed, 14 deselected |
| 연속성 | `python scripts/continuity_check.py` | exit=0 ✅ — 연속성 검사 통과 — 포인터와 실제 파일이 일치한다 |
| 도메인 목록 | `python scripts/sync_domain_list.py --check` | exit=0 ✅ — [OK] 도메인 목록 최신 — 15개 |
| Codex 미러 | `python scripts/sync_codex_mirror.py --check` | exit=0 ✅ — 출력 없음 |
| 실행 계약 | `python scripts/sync_agent_contract.py --check` | exit=0 ✅ — 출력 없음 |

## 이번 세션에 한 일

- 316f95d Merge pull request #23 from joonake9644/chore/preflight-001
- e922a87 test(preflight): 판정 시험이 plain_get 호출까지 확인 — 독립 리뷰 LOW 반영, 종료 분류·인계서
- f204e89 fix(preflight): 메시지 없는 예외도 HTTP 점검 WARN 으로 — IndexError 로 죽던 경로
- 929f6b6 fix(preflight): HTTP 점검을 사다리 1단 plain_get 으로 — 지어낸 Referer·위장 헤더·deprecated 인스턴스 제거
- 9b7bb51 chore(plan): PREFLIGHT-001 조각 계약 — preflight HTTP 점검을 plain_get 으로
- c7fa19e Merge pull request #22 from joonake9644/chore/rev11-preflight-plainget
- 2cd22b8 chore(plan): REV-11 — preflight HTTP 점검을 plain_get 으로 바꾸는 과제(PREFLIGHT-001) 추가
- 6760b8a Merge pull request #21 from joonake9644/chore/rev10-gaps001-done
- ba3c171 chore(plan): REV-10 — GAPS-001 완료 표시
- 33e21da Merge pull request #20 from joonake9644/chore/gaps-001
- e9c7d22 chore(harness): GAPS-001 독립 리뷰 기록과 세션 핸드오프 생성
- 497ce5b chore(gaps-001): 독립 리뷰 결과·갭·종료 분류 기록

## 남은 것 / 다음 세션

- 활성 계약의 미해결 항목을 먼저 본다: `docs/task-contracts/PY311-001.md`
- UNVERIFIED 로 남아 있는 것은 지어내지 말고 그대로 유지한다.
- 세션 문맥의 정본은 `.harness/state.json` 하나다 — 중간에 멈췄다면 그 파일을 갱신한다 (ADR-001). 정본 밖에 파생 사본을 두지 않는다 (AGENTS.md).

## 다음 세션 즉시 시작

```text
세션 이어받기. 프로젝트: /Users/joonake/Developer/projects/web-crawler
먼저 docs/session-handoff.md 와 .harness/state.json 을 읽는다.
그리고 baseline 확인: python -m pytest -q -k "not e2e"  (위 표의 통과 수와 같아야 한다)
활성 작업: PY311-001 — 계약 docs/task-contracts/PY311-001.md
```
