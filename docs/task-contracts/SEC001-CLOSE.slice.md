# 조각 SEC001-CLOSE: SEC-001 인터럽트를 독립 리뷰 반영 후 닫고 PY311-001 로 복귀한다
- 위험 등급: light
- 핵심 경로: yes
- 세션 예산: 1
- 계획 과제: SEC001-CLOSE
- 허용 경로: .harness/policy.json, .harness/state.json, docs/session-handoff.md, docs/task-contracts/SEC-001.md, docs/task-contracts/SEC001-CLOSE.slice.md, scripts/utils.py, scripts/test_utils.py

## 합격 기준
1. 병합된 #8(97b752b) 독립 다른-모델 리뷰 결과가 `docs/task-contracts/SEC-001.md` 에 기록되고, 메인이 재현한 HIGH·MEDIUM 지적은 RED→GREEN 으로 고쳐졌다.
2. `.harness/policy.json` 의 `interrupt.status` 가 `none` 이다.
3. `.harness/state.json` 의 `session_end.independent_review` 가 이번 리뷰(모델·판정)를 가리킨다.
4. 실행 계약 6종이 모두 exit 0 이다.

## 검사 명령
- `.venv/bin/python -m pytest -q -k "not e2e"`
- `.venv/bin/python scripts/continuity_check.py`
- `.venv/bin/python scripts/sync_domain_list.py --check`
- `.venv/bin/python scripts/sync_codex_mirror.py --check`
- `.venv/bin/python scripts/sync_agent_contract.py --check`
- `.venv/bin/python scripts/session_handoff.py --check`

## 불변 제약
- `active_work`(PY311-001)·승인 고정 sha256·ADR 기준점은 바꾸지 않는다.
- 하네스 핵심 파일(`.plan/`, `.claude/settings.json`, `CLAUDE.md`, `AGENTS.md`, 스킬·훅)은 고치지 않는다(전역 관문 HCG).
- 리뷰는 첫 리뷰 1회 + 재확인 최대 2회.

## 범위 밖(하지 않는 것)
- 체크아웃 사본 `.plan/bin/plan.mjs` 판 차이 정리(로컬 브랜치 chore/plan-harness-v2-1104 의 319dee0) — 하네스 변경 관문 대상, 별도 승인.
- 병합된 로컬 브랜치·orca 작업트리 정리.
- PY311-001 상한 변경(1.65 미출시).

## 갭 목록

## 종료 분류
