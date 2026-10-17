# 세션 핸드오프

> 이 파일은 **생성물**이다. `python scripts/session_handoff.py write` 로 만든다.
>
> `--check` 가 잡는 것: **정본(state/policy)이 바뀌었는데 문서가 따라가지 않은 것**.
> `--check` 가 **못** 잡는 것: 이 본문 안의 문장을 손으로 고치는 것.
> 정본이 아닌 본문은 사람이 읽는 설명일 뿐이라 기계가 검증할 수 없다.
> 정본은 `.harness/state.json` 이고, 생성기는 `scripts/session_handoff.py` 다.

다음 세션은 이 파일과 `.harness/state.json` 만 읽으면 된다. 이전 대화 이력은 근거가 아니다.

- 입력 다이제스트: `016b46606cb93a7f479a9d9ffed7aeddd6826b453936290198cb34cc7ee9d35a`

## 상태 한 줄 요약

- 활성 작업: **PY311-001** — 계약 `docs/task-contracts/PY311-001.md`
- NORTH STAR: URL과 수집 항목을 받아 사이트를 정찰·대량수집하고 엑셀로 내보내는 범용 웹 크롤링 에이전트 — 문서에 적힌 대로 따라 하면 죽지 않는다 (`GOAL-001`)
- 단계: `POST_CHECK` / dirty=`False`
- 검증 커밋: `0888b37`
- 작업 도구: **codex/gpt-6.1-sol (reasoning high)**

## 실측 검증 (write 시점에 돌린 결과다)

측정 시점 HEAD: `0888b37` · 브랜치 `chore/py311-raise-1.65`

> ⚠ **출처**: 아래 결과는 이 문서를 커밋하기 **전의 작업 트리**에서 돌았다.
> `write` 는 커밋 전에 불리므로 위 해시는 이 문서를 담는 커밋의 **부모**다.
> 그래서 그 커밋을 체크아웃해 `baseline` 을 다시 돌리면 통과 수가 **다를 수 있다** —
> 아래 수는 '이 커밋의 트리'가 아니라 '그 커밋 직전의 작업 트리'의 실측이다.
> 이 문서를 커밋한 다음 다시 생성하면(HEAD 가 바뀐다) 수치가 맞춰진다.

| 항목 | 명령 | 결과 |
|---|---|---|
| baseline | `python -m pytest -q -k "not e2e"` | exit=0 ✅ — 590 passed, 14 deselected |
| 연속성 | `python scripts/continuity_check.py` | exit=0 ✅ — 연속성 검사 통과 — 포인터와 실제 파일이 일치한다 |
| 도메인 목록 | `python scripts/sync_domain_list.py --check` | exit=0 ✅ — [OK] 도메인 목록 최신 — 14개 |
| Codex 미러 | `python scripts/sync_codex_mirror.py --check` | exit=0 ✅ — 출력 없음 |
| 실행 계약 | `python scripts/sync_agent_contract.py --check` | exit=0 ✅ — 출력 없음 |

## 이번 세션에 한 일

- 0888b37 fix(test): 허용 범위 검사가 지원하는 제약식 꼴만 읽게 한다 (PY311-001)
- d26873c fix(requirements): 두 패키지 모두 1.64 출시로 상한을 함께 <1.65 로 올린다 (PY311-001)
- b704f13 chore(harness): 세션 종료 — REV-2 리뷰 기록과 핸드오프를 반영한다 (PY311-001)
- 0df4765 chore(plan): REV-2 로 ADR 기준점을 명시해 구형 계획 WARN 을 닫는다 (PY311-001)
- 27093fd Merge pull request #3 from joonake9644/chore/harness-integrity-20261003
- 1064aba chore(harness): 세션 종료 — 1.64 재측정 리뷰 기록과 핸드오프를 반영한다 (PY311-001)
- 0f69926 fix(requirements): 상한 상향 조건을 '두 패키지 모두 출시'로 못 박는다 (PY311-001)
- e75e3ee fix(harness): reject synthetic native hook approvals
- 1aea763 fix(harness): verify approval and ADR provenance
- 331c7ca Merge pull request #2 from joonake9644/chore/harness-004-claude-md-map
- 0dc1eb8 chore(harness): 세션 종료 — 상태를 닫고 핸드오프를 생성한다 (HARNESS-004)
- a72ca27 docs(harness): CLAUDE.md 를 200줄 미만 지도로 줄이고 안전 규칙을 이관한다 (HARNESS-004)

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
