# 세션 핸드오프

> 이 파일은 **생성물**이다. `python scripts/session_handoff.py write` 로 만든다.
>
> `--check` 가 잡는 것: **정본(state/policy)이 바뀌었는데 문서가 따라가지 않은 것**.
> `--check` 가 **못** 잡는 것: 이 본문 안의 문장을 손으로 고치는 것.
> 정본이 아닌 본문은 사람이 읽는 설명일 뿐이라 기계가 검증할 수 없다.
> 정본은 `.harness/state.json` 이고, 생성기는 `scripts/session_handoff.py` 다.

다음 세션은 이 파일과 `.harness/state.json` 만 읽으면 된다. 이전 대화 이력은 근거가 아니다.

- 입력 다이제스트: `368e6cd87c30e730bcbe3cfc7bb091efcbc03fde3f11506a994ee02239766408`

## 상태 한 줄 요약

- 활성 작업: **PY311-001** — 계약 `docs/task-contracts/PY311-001.md`
- NORTH STAR: URL과 수집 항목을 받아 사이트를 정찰·대량수집하고 엑셀로 내보내는 범용 웹 크롤링 에이전트 — 문서에 적힌 대로 따라 하면 죽지 않는다 (`GOAL-001`)
- 단계: `VERIFY` / dirty=`False`
- 검증 커밋: `d21566c`
- 작업 도구: **codex/gpt-6.1-sol (reasoning high)**

## 실측 검증 (write 시점에 돌린 결과다)

측정 시점 HEAD: `df62c9a` · 브랜치 `chore/rev5-secintel-dep`

> ⚠ **출처**: 아래 결과는 이 문서를 커밋하기 **전의 작업 트리**에서 돌았다.
> `write` 는 커밋 전에 불리므로 위 해시는 이 문서를 담는 커밋의 **부모**다.
> 그래서 그 커밋을 체크아웃해 `baseline` 을 다시 돌리면 통과 수가 **다를 수 있다** —
> 아래 수는 '이 커밋의 트리'가 아니라 '그 커밋 직전의 작업 트리'의 실측이다.
> 이 문서를 커밋한 다음 다시 생성하면(HEAD 가 바뀐다) 수치가 맞춰진다.

| 항목 | 명령 | 결과 |
|---|---|---|
| baseline | `python -m pytest -q -k "not e2e"` | exit=0 ✅ — 674 passed, 14 deselected, 2 warnings |
| 연속성 | `python scripts/continuity_check.py` | exit=0 ✅ — 연속성 검사 통과 — 포인터와 실제 파일이 일치한다 |
| 도메인 목록 | `python scripts/sync_domain_list.py --check` | exit=0 ✅ — [OK] 도메인 목록 최신 — 15개 |
| Codex 미러 | `python scripts/sync_codex_mirror.py --check` | exit=0 ✅ — 출력 없음 |
| 실행 계약 | `python scripts/sync_agent_contract.py --check` | exit=0 ✅ — 출력 없음 |

## 이번 세션에 한 일

- df62c9a Merge pull request #11 from joonake9644/chore/rev4-sec001-done
- 6fa8588 chore(plan): REV-4 — SEC001-CLOSE 완료 표시
- 897ed3c Merge pull request #10 from joonake9644/chore/sec001-close
- 7859f9b chore(harness): 세션 핸드오프 생성과 SEC001-CLOSE 갭·종료 분류 기록
- 8f9146f chore(harness): SEC-001 인터럽트를 닫고 PY311-001 로 복귀한다 (SEC001-CLOSE)
- d21566c fix(utils): 국제 전화번호 구분자에 NBSP 등 가로 공백을 되살린다 (SEC001-CLOSE)
- 1cc7421 fix(utils): 국제 전화번호 뒤 콜론·줄바꿈 문맥 때문에 PII 경고가 사라지던 결함 (SEC001-CLOSE)
- 776936c chore(plan): REV-3 — SEC001-CLOSE 과제와 순서 블록 추가, 조각 계약
- ad0b845 sec(redteam): 자가 레드팀 발견 2건 수정 (엑셀 수식 주입·Chrome 인자 주입) (#9)
- 97b752b sec(SEC-001): 방어 목적 자가 점검 자산 + PII·비밀파일·자가치유 결함 수정 (#8)
- 735681b Merge pull request #7 from joonake9644/chore/plan-harness-slice-loop
- afa6295 Merge pull request #6 from joonake9644/fix/robots-404

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
