# 세션 핸드오프

> 이 파일은 **생성물**이다. `python scripts/session_handoff.py write` 로 만든다.
>
> `--check` 가 잡는 것: **정본(state/policy)이 바뀌었는데 문서가 따라가지 않은 것**.
> `--check` 가 **못** 잡는 것: 이 본문 안의 문장을 손으로 고치는 것.
> 정본이 아닌 본문은 사람이 읽는 설명일 뿐이라 기계가 검증할 수 없다.
> 정본은 `.harness/state.json` 이고, 생성기는 `scripts/session_handoff.py` 다.

다음 세션은 이 파일과 `.harness/state.json` 만 읽으면 된다. 이전 대화 이력은 근거가 아니다.

- 입력 다이제스트: `dba1109f2f3b4a0e9bfa935aca13a25c08cb2199f82ec84fe6419d7aab531079`

## 상태 한 줄 요약

- 활성 작업: **PY311-001** — 계약 `docs/task-contracts/PY311-001.md`
- NORTH STAR: URL과 수집 항목을 받아 사이트를 정찰·대량수집하고 엑셀로 내보내는 범용 웹 크롤링 에이전트 — 문서에 적힌 대로 따라 하면 죽지 않는다 (`GOAL-001`)
- 단계: `VERIFY` / dirty=`False`
- 검증 커밋: `497ce5b`
- 작업 도구: **codex/gpt-6.1-sol (reasoning high) · grok-4.7 (xhigh) — opencode-go/deepseek-v4.1-flash#max 는 판정 없이 종료(exit 1, 「An active OpenCode Go subscription is required」)**

## 실측 검증 (write 시점에 돌린 결과다)

측정 시점 HEAD: `2aa7727` · 브랜치 `chore/rev15-safety-tools`

> ⚠ **출처**: 아래 결과는 이 문서를 커밋하기 **전의 작업 트리**에서 돌았다.
> `write` 는 커밋 전에 불리므로 위 해시는 이 문서를 담는 커밋의 **부모**다.
> 그래서 그 커밋을 체크아웃해 `baseline` 을 다시 돌리면 통과 수가 **다를 수 있다** —
> 아래 수는 '이 커밋의 트리'가 아니라 '그 커밋 직전의 작업 트리'의 실측이다.
> 이 문서를 커밋한 다음 다시 생성하면(HEAD 가 바뀐다) 수치가 맞춰진다.

| 항목 | 명령 | 결과 |
|---|---|---|
| baseline | `python -m pytest -q -k "not e2e"` | exit=1 ❌ — 6 failed, 734 passed, 14 deselected |
| 연속성 | `python scripts/continuity_check.py` | exit=0 ✅ — 연속성 검사 통과 — 포인터와 실제 파일이 일치한다 |
| 도메인 목록 | `python scripts/sync_domain_list.py --check` | exit=1 ❌ — [FAIL] 생성 블록이 어긋났습니다 (CLAUDE.md, README.md, .gitignore). `python scrip |
| Codex 미러 | `python scripts/sync_codex_mirror.py --check` | exit=0 ✅ — 출력 없음 |
| 실행 계약 | `python scripts/sync_agent_contract.py --check` | exit=0 ✅ — 출력 없음 |

## 이번 세션에 한 일

- 2aa7727 Merge pull request #27 from joonake9644/chore/rev14-gaps002-done
- 5cc6081 chore(plan): REV-14 — GAPS-002 완료 표시
- 31a4754 Merge pull request #26 from joonake9644/chore/gaps-002
- 7301c62 test(bootstrap): 미설치 사유 시험도 pip 1회 확인 — 독립 리뷰 LOW 반영, 종료 분류·인계서
- 7940778 fix(preflight,bootstrap): 빈 메시지 예외에도 진단이 죽지 않고, 재설치 전 「준비 안 됨」 사유를 보인다
- 17e0d3e chore(plan): GAPS-002 조각 계약 — preflight 예외 처리 5곳·bootstrap 사유 표시
- 06ffac0 Merge pull request #25 from joonake9644/chore/rev13-preflight-bootstrap-gaps
- 6f8d0ef chore(plan): REV-13 — preflight 예외 처리 5곳·bootstrap 사유 표시 과제(GAPS-002) 추가
- 6798421 Merge pull request #24 from joonake9644/chore/rev12-preflight-done
- a0a4b2a chore(plan): REV-12 — PREFLIGHT-001 완료 표시
- 316f95d Merge pull request #23 from joonake9644/chore/preflight-001
- e922a87 test(preflight): 판정 시험이 plain_get 호출까지 확인 — 독립 리뷰 LOW 반영, 종료 분류·인계서

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
