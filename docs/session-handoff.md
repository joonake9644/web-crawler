# 세션 핸드오프

> 이 파일은 **생성물**이다. `python scripts/session_handoff.py write` 로 만든다.
>
> `--check` 가 잡는 것: **정본(state/policy)이 바뀌었는데 문서가 따라가지 않은 것**.
> `--check` 가 **못** 잡는 것: 이 본문 안의 문장을 손으로 고치는 것.
> 정본이 아닌 본문은 사람이 읽는 설명일 뿐이라 기계가 검증할 수 없다.
> 정본은 `.harness/state.json` 이고, 생성기는 `scripts/session_handoff.py` 다.

다음 세션은 이 파일과 `.harness/state.json` 만 읽으면 된다. 이전 대화 이력은 근거가 아니다.

- 입력 다이제스트: `28a4066aba94e2853184f1d873854757ce3b7998973fad506cb23b178df754db`

## 상태 한 줄 요약

- 활성 작업: **PY311-001** — 계약 `docs/task-contracts/PY311-001.md`
- NORTH STAR: URL과 수집 항목을 받아 사이트를 정찰·대량수집하고 엑셀로 내보내는 범용 웹 크롤링 에이전트 — 문서에 적힌 대로 따라 하면 죽지 않는다 (`GOAL-001`)
- 단계: `VERIFY` / dirty=`False`
- 검증 커밋: `497ce5b`
- 작업 도구: **codex/gpt-6.1-sol (reasoning high) · grok-4.7 (xhigh) — opencode-go/deepseek-v4.1-flash#max 는 2회 모두 판정 없이 종료(exit 1)**

## 실측 검증 (write 시점에 돌린 결과다)

측정 시점 HEAD: `497ce5b` · 브랜치 `chore/gaps-001`

> ⚠ **출처**: 아래 결과는 이 문서를 커밋하기 **전의 작업 트리**에서 돌았다.
> `write` 는 커밋 전에 불리므로 위 해시는 이 문서를 담는 커밋의 **부모**다.
> 그래서 그 커밋을 체크아웃해 `baseline` 을 다시 돌리면 통과 수가 **다를 수 있다** —
> 아래 수는 '이 커밋의 트리'가 아니라 '그 커밋 직전의 작업 트리'의 실측이다.
> 이 문서를 커밋한 다음 다시 생성하면(HEAD 가 바뀐다) 수치가 맞춰진다.

| 항목 | 명령 | 결과 |
|---|---|---|
| baseline | `python -m pytest -q -k "not e2e"` | exit=0 ✅ — 711 passed, 14 deselected |
| 연속성 | `python scripts/continuity_check.py` | exit=0 ✅ — 연속성 검사 통과 — 포인터와 실제 파일이 일치한다 |
| 도메인 목록 | `python scripts/sync_domain_list.py --check` | exit=0 ✅ — [OK] 도메인 목록 최신 — 15개 |
| Codex 미러 | `python scripts/sync_codex_mirror.py --check` | exit=0 ✅ — 출력 없음 |
| 실행 계약 | `python scripts/sync_agent_contract.py --check` | exit=0 ✅ — 출력 없음 |

## 이번 세션에 한 일

- 497ce5b chore(gaps-001): 독립 리뷰 결과·갭·종료 분류 기록
- 021c919 test(requirements): certifi 하한을 제약식에서 직접 읽는다 — 표본 밖 rc2·안전한 범위 오판 (독립 리뷰 LOW)
- c7bfa2c docs(gaps-001): 평가 문서 후속 기록과 조각 갭 목록 정리
- 6352199 fix(bootstrap): 이미 설치됨 판정에 설치판·제약식 대조 — 0.4.15 venv 가 자동 갱신되지 않던 경로 (GAPS-001)
- db55f23 test(requirements): certifi 하한을 packaging 의미 검사로 — 마커·rc 하한·중복·만족 불가 범위 거부 (GAPS-001)
- 97fc86d fix(pii): 국제 전화번호가 뒤 숫자 묶음 때문에 15자리를 넘으면 구분자 자리에서 다시 센다 (GAPS-001)
- 0b19722 fix(utils): plain_dynamic 에 retries·retry_delay — 1·2단·옛 3단과 같은 3회 시도, 위장 차단·반환형 고정 시험 (GAPS-001)
- e280c4f chore(plan): GAPS-001 조각 계약 — DEP-002 LOW 갭 정리(3단 재시도·국제 전화 미탐·certifi 검사·bootstrap 판 확인)
- 623a1fd Merge pull request #19 from joonake9644/chore/rev9-dep002-lowgaps
- dc7fe90 chore(plan): REV-9 — DEP-002 LOW 갭 정리(GAPS-001)를 과제로 추가
- a513ecc Merge pull request #18 from joonake9644/chore/rev8-dep002-done
- eb70233 chore(plan): REV-8 — DEP-002 완료 표시

## 남은 것 / 다음 세션

- 활성 계약의 미해결 항목을 먼저 본다: `docs/task-contracts/PY311-001.md`
- UNVERIFIED 로 남아 있는 것은 지어내지 말고 그대로 유지한다.
- 세션 문맥의 정본은 `.harness/state.json` 하나다 — 중간에 멈췄다면 그 파일을 갱신한다 (ADR-001). 정본 밖에 파생 사본을 두지 않는다 (AGENTS.md).

## 다음 세션 즉시 시작

```text
세션 이어받기. 프로젝트: /Users/joonake/Developer/worktrees/web-crawler/rev5-secintel-dep
먼저 docs/session-handoff.md 와 .harness/state.json 을 읽는다.
그리고 baseline 확인: python -m pytest -q -k "not e2e"  (위 표의 통과 수와 같아야 한다)
활성 작업: PY311-001 — 계약 docs/task-contracts/PY311-001.md
```
