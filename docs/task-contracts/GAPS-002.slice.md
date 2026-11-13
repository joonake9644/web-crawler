# 조각 GAPS-002: preflight 가 메시지 없는 예외에도 죽지 않고, bootstrap 이 재설치 전에 「준비 안 됨」 사유를 보인다
- 위험 등급: light
- 핵심 경로: no
- 세션 예산: 1
- 계획 과제: GAPS-002
- 허용 경로: scripts/preflight.py, scripts/test_preflight.py, scripts/bootstrap.py, scripts/test_bootstrap.py, docs/task-contracts/GAPS-002.slice.md, .gitignore, .harness/state.json, docs/session-handoff.md

## 출발 실측(2026-11-13, master 06ffac0)
- `scripts/preflight.py` 85·98·118·176·193행이 `str(e).splitlines()[0]` 를 쓴다. `check_agent_browser_ready()` 에 빈 `OSError()` 를 넣으면 IndexError 로 죽는다(재현).
- `scripts/bootstrap.py:159` `do_python_deps()` 는 `py_deps_ready()` 가 거짓이면 이유 없이 `pip install -r` 로 간다. `py_deps_ready()` 는 import 실패를 삼키고, `requirements_unsatisfied()` 문제 목록도 화면에 나오지 않는다.

## 설계
- preflight: 모듈 함수 `_first_line(e, limit)` 하나를 두어 `(str(e).splitlines() or [type(e).__name__])[0][:limit]` 를 돌려준다. 다섯 곳과 HTTP 점검이 이것을 쓴다. 각 점검의 판정 등급·이름·자르는 길이·고칠 명령은 그대로다.
- bootstrap: `py_deps_problems()` 가 「준비 안 됨」 사유 목록(import 실패 `import <모듈> 실패: <예외 이름>: <첫 줄>` + `requirements_unsatisfied()`)을 돌려준다. `py_deps_ready()` 는 `not py_deps_problems()` 로 같은 판정을 유지한다. `do_python_deps()` 는 설치로 넘어가기 전에 사유를 한 줄씩 찍는다. `--force` 일 때는 사유 대신 강제 재설치라고 찍는다. 설치 여부·명령은 그대로다.

## 합격 기준
1. 새 시험을 먼저 RED 로 확인한 뒤 GREEN: preflight 다섯 점검이 메시지 없는 예외에서 죽지 않고 원래 판정(FAIL·WARN)과 예외 이름을 기록한다.
2. 새 시험을 먼저 RED 로 확인한 뒤 GREEN: bootstrap 이 준비 안 됨일 때 사유(설치판 불일치·미설치·import 실패)를 출력하고, 준비됨일 때는 [SKIP] 줄만 낸다. `py_deps_ready()` 기존 시험 5건은 그대로 통과한다.
3. 새 시험이 옛 코드(06ffac0)에서 실패하고 새 코드에서 통과한다(실측 기록).
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
- preflight 의 점검 항목·판정 등급·종료 코드 규칙은 바꾸지 않는다. bootstrap 이 언제 `pip install` 을 돌리는지는 바꾸지 않는다.
- `plain_get`·스킬 정본·하네스 파일은 고치지 않는다(applygo36 ADR-019 하네스 동결).

## 범위 밖(하지 않는 것)
- 다른 진단 문구 개편, 설치 단계 추가·삭제, 실제 `pip install` 실행 시험.

## 갭 목록
- LOW(GAPS-001 넘김, 할 일 없음): `troubleshooting.md:47` 은 과거 사고 원인 서술이라 당시 이름을 그대로 둔다(HCG-055 범위 결정).
- LOW(GAPS-001 넘김, 할 일 없음): CISA 사이트 피드가 자동 조회를 403 으로 막는다. GitHub 사본 대체 경로가 이미 있다.
- LOW(GAPS-001 넘김): 구동 Chromium 156.0.8078.4 가 안정판 158 보다 두 메이저 뒤다. patchright 1.65 출시 뒤 상한을 함께 올릴 때 다시 잰다(PY311-001 상시 조건).
- LOW(GAPS-001 넘김): Chromium·curl_cffi 내장 libcurl 의 Brotli 판(KEV CVE-2026-111497) 미확인. 다음 보안 인텔 수집에서 잰다.
- LOW(GAPS-001 넘김): 로컬 브랜치 `chore/plan-harness-v2-1104` 의 커밋 319dee0(하네스 v2 갱신)·엔진 사본 8f3277 표시 결함 — applygo36 ADR-019 하네스 동결로 정기 점검 대상. 원본 체크아웃은 2026-11-12 master 로 옮겼고 그 브랜치는 보존했다.
- LOW(GAPS-001 넘김): 병합된 로컬 브랜치·orca 작업트리 barracuda·작업트리 rev5-secintel-dep·`~/.cache/web-crawler-dep001`·`dep002` 정리(사용자 확인 뒤).
- LOW(GAPS-001 넘김, 독립 리뷰 Grok): `bootstrap.py` 가 「준비 안 됨」 사유를 화면에 찍지 않는다.
- LOW(GAPS-001 넘김, 독립 리뷰 Grok 기록): 점 구분 16자리 `+1234.5678.9012.3456` 이 전화번호 경고를 낸다(설계가 정한 넓히기).
- LOW(GAPS-001 넘김, PREFLIGHT-001 에서 원인 실측): DeepSeek 리뷰어가 판정 없이 종료코드 1 로 끝난다. 이번 오류 로그 원문은 `An active OpenCode Go subscription is required to use OpenCode Go models.` — OpenCode Go 구독이 없어서다. 구독 여부는 사용자 결정이다.
- 닫힘(GAPS-001 뒤 실측): 원본 체크아웃 venv — master 로 옮긴 뒤 `bootstrap.py --core-only` 로 scrapling 0.5.1 갱신, 미충족 0건, 711 통과.
- LOW(PREFLIGHT-001 시작 전 실측): 원본 체크아웃이 master 에 있으면 프로젝트 훅 `shu-guard:main-commit` 이 세션 기본 폴더의 브랜치만 보고, 다른 작업트리의 기능 브랜치 커밋까지 막는다(REV-11 커밋에서 실측). 이번 조각은 원본 체크아웃 기능 브랜치에서 작업해 피한다.
- 닫힘(구현 중 실측, 합격 기준 2 직접 위반): 메시지 없는 예외(`TimeoutError()`)에서 `str(e).splitlines()[0]` 가 IndexError 로 preflight 를 죽였다(옛 코드부터). HTTP 점검 한 곳만 RED 확인 뒤 예외 이름으로 대체해 WARN 으로 고침.
- LOW(구현 중 실측, 범위 밖): 같은 `str(e).splitlines()[0]` 패턴이 다른 점검 5곳(`preflight.py` import·Fetcher 로드·Chromium 실행·agent-browser 2곳)에 남았다. 불변 제약(다른 점검 항목 불변)으로 이번에 고치지 않는다.
- LOW(구현 중 실측, 범위 밖): `plain_get` 은 위장 헤더 13종·Referer 를 보내지 않지만, UA 가 없으면 scrapling 이 고정 브라우저 UA(`__default_useragent__`, Chrome/149 Windows)를 넣는다(로컬 서버 실측). 사다리 1단이 정직한 UA 를 보낼지는 `plain_get` 범위의 별도 결정이다.
- LOW(시작 시 원장 경고): `slice start` 가 GAPS-001 남은 갭 18건이 이 목록에 글자 그대로 없다고 경고했다. 닫힌 항목은 뺐고 남은 LOW 는 위에 고쳐 쓴 문구로 옮겼다(내용 누락 없음).
- 닫힘(독립 리뷰 LOW, Codex·Grok 공통): 503·예외 판정 시험이 옛 코드에서도 통과했다. `plain_get` 호출 확인을 더해 옛 `preflight.py` 에서 6건 모두 실패, 새 코드에서 6건 통과를 실측했다.
- 이번 조각 대상(시작 시점): 위 「같은 `str(e).splitlines()[0]` 패턴 … 5곳」 과 「`bootstrap.py` 가 「준비 안 됨」 사유를 화면에 찍지 않는다」 두 줄. 닫을 때 닫힘으로 바꾼다.

## 종료 분류
