# 조각 GAPS-001: DEP-002 가 넘긴 LOW 갭 중 「고친다」 6건을 TDD 로 고치고, 나머지 7건은 사유와 함께 옮긴다
- 위험 등급: full
- 핵심 경로: no
- 세션 예산: 1
- 계획 과제: GAPS-001
- 허용 경로: scripts/utils.py, scripts/test_utils.py, scripts/test_requirements.py, scripts/bootstrap.py, scripts/test_bootstrap.py, docs/crawl-reference.md, scripts/scrapling_reference.md, docs/reference/scrapling-0.5-compat-2026-11.md, docs/task-contracts/GAPS-001.slice.md, .gitignore, .harness/state.json, docs/session-handoff.md

## 출발 실측(2026-11-12, master 623a1fd)
- DEP-002 계약 「갭 목록」의 LOW 는 13건이다(REV-8 보고의 「14건」은 잘못 센 것).
- 3단 재시도: 1·2단(scrapling `Fetcher`·`FetcherSession`)과 옛 3단(0.4 `DynamicFetcher`)은 기본 `retries=3`(총 시도 수, `retry_delay=1`초, 마지막 실패는 다시 올림)이다. 새 3단 `plain_dynamic` 은 한 번만 시도한다. `docs/crawl-reference.md:270` 「네트워크 타임아웃 → 3회 재시도 후 스킵」은 1~2단에는 맞고 3단에는 틀리다.
- 국제 전화번호: 갭 이름은 「오탐」이었으나 실측해 보니 **미탐**이다. `_INTL_PHONE_PATTERN` 이 번호 뒤의 숫자(날짜 등)까지 먹어 숫자가 15자리를 넘으면 `_intl_phone_hit` 가 놓친다. `+1 415 555 2671 2026-11-06` 은 국내 패턴이 우연히 잡고, `+44 7911 123456 12 34 56` 은 `detect_pii` 가 `[]` 를 돌려준다(경고 없음).
- certifi 하한 검사(`scripts/test_requirements.py:227`)는 정규식으로 `>=` 숫자만 읽는다. 환경 마커로 무력화된 줄, `rc` 사전 릴리스 하한, 여러 번 선언은 거르지 못한다.
- `scripts/bootstrap.py py_deps_ready()` 는 import 만 보고 판을 보지 않는다. scrapling 0.4.15 venv 도 「준비됨」으로 판정해 `pip install -r` 을 건너뛴다.
- `scripts/test_utils.py:723 _forbid_stealth` 는 `patchright.sync_api.sync_playwright` 하나만 막는다.
- `scripts/utils.py:436` 이 쓰는 비공개 경로 `scrapling.engines.toolbelt.custom.Response` 를 직접 고정하는 시험이 없다.

## 설계
1. **3단 재시도(문서를 동작에 맞추지 않고 동작을 1·2단·옛 3단에 맞춘다).** 재시도를 빼면 옛 3단보다 후퇴하기 때문이다. `plain_dynamic(url, *, retries=3, retry_delay=1, …)` 의 뜻은 scrapling 정적 요청과 같다. 총 시도 수는 `max(1, retries)` 이고, 한 번의 시도는 브라우저 실행부터 응답 생성까지다. 실패한 시도마다 경고 로그를 남기고 `retry_delay` 초를 쉰다. 마지막 실패는 그대로 다시 올린다(실패를 숨기지 않는다). 인자 검사(`google_search=True`·모르는 인자)는 시도 전에 거부하고 재시도하지 않는다. 받는 인자 목록 두 곳(`docs/crawl-reference.md:269`, `scripts/scrapling_reference.md` 3절)에 `retries`·`retry_delay` 를 더한다. `crawl-reference.md:270` 문장은 1~3단 모두에 맞게 된다.
2. **국제 전화번호.** 패턴이 잡은 덩어리 전체가 15자리를 넘을 때도 `+국가번호` 부터 앞쪽 숫자 묶음을 하나씩 늘려 가며, 8~15자리가 되는 지점이 있으면 잡는다. `+` 앞이 글자·숫자가 아니어야 한다는 F11 규율과 E.164 범위는 그대로다.
3. **certifi 하한 검사.** 정규식 대신 `packaging.requirements.Requirement` 로 의미를 본다. 이어진 줄(`\`)을 합치고, certifi 선언이 정확히 1개이며, 환경 마커가 없고, `SpecifierSet` 이 2026.10.19 미만의 판(`2026.10.18`, `2026.10.19rc1` 등, 사전 릴리스 포함)을 하나도 허용하지 않아야 통과한다.
4. **bootstrap 판 확인.** `py_deps_ready()` 가 import 다음에 `requirements.txt` 각 선언(환경 마커 평가 포함)의 설치판을 `importlib.metadata` 로 읽어 제약식과 대조한다. 하나라도 어긋나면 준비 안 됨으로 판정해 `pip install -r` 을 돌린다. `packaging` 을 import 할 수 없으면 준비 안 됨으로 본다.
5. **`_forbid_stealth`.** `patchright` 모듈 import 와 `scrapling.fetchers.StealthyFetcher`·`StealthySession` 사용까지 막는다.
6. **`Response` 경로 고정.** `scrapling.engines.toolbelt.custom.Response` import 와, `plain_dynamic` 반환값이 그 클래스의 인스턴스인지를 직접 확인하는 시험을 더한다.

## 합격 기준
1. 설계 1: 가짜 playwright 시험(`retry_delay=0`)을 먼저 RED 로 확인한 뒤 GREEN 이다. 확인하는 것은 「앞 2회 실패 뒤 3회째 성공 → 응답 반환·브라우저 실행 3회」, 「모두 실패 → `retries` 회 뒤 마지막 예외 전파」, 「`retries=1` 이면 1회」, 「`google_search=True` 는 브라우저 실행 0회」다. 문서 두 곳의 인자 목록이 함수 시그니처와 같다.
2. 설계 2: `+44 7911 123456 12 34 56` 과 `+1 415 555 2671 2026-11-06 접수` 에서 `_intl_phone_hit` 가 참이 되는 시험이 RED 에서 GREEN 이 된다. 기존 PII 시험(URL 쿼리 `a+1415…` 제외 등)은 모두 통과한다.
3. 설계 3·4: 우회 형태(마커·`rc` 하한·중복 선언·이어진 줄, 0.4.15 설치판)를 넣은 시험이 RED 에서 GREEN 이 되고, 실제 `requirements.txt` 와 현재 venv 에서는 통과한다.
4. 설계 5·6: 고정 시험은 지금 통과하는 것이 정상이다. 그래서 RED 는 대상을 일부러 가린 상태로 확인한다. 설계 5 는 `_forbid_stealth` 아래서 `import patchright`·`StealthyFetcher.fetch` 가 막히는지 보는 시험이 지금 코드에서 실패하는 것으로, 설계 6 은 `sys.modules` 에서 상류 경로를 가렸을 때 실패하는 것으로 확인한 뒤 GREEN 이다.
5. 실행 계약 6종과 3.11 환경 `pytest -q -k "not e2e"` 가 모두 exit 0 이다.

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
- 사다리 3단은 이음매 위에 남는다. 재시도는 같은 `plain_dynamic` 을 다시 부를 뿐이며, 다음 칸(사다리 B)으로 자동으로 넘어가지 않는다. 0건 중단 규칙은 그대로다.
- PII 검출은 넓히기만 한다. 지금 잡는 값을 놓치게 바꾸지 않는다.
- playwright·patchright 제약식 바이트 동일(ADR-002), 상한 `<1.65`, `requirements.txt` 는 바꾸지 않는다.
- 스킬 정본 `.claude/skills/web-crawler/**`·`.codex/` 미러·하네스 엔진·`.plan/`·훅·`CLAUDE.md`·`AGENTS.md` 는 고치지 않는다(applygo36 ADR-019 하네스 동결). 스킬 정본 수정이 필요해지면 멈추고 HCG 관문을 거친다.

## 범위 밖(하지 않는 것)
- 실제 외부 사이트 수집 시험.
- 사다리 B·통지 게이트 동작 변경.
- 저장소 밖 브랜치·작업트리·시험 환경 정리.

## 갭 목록
- 닫힘(DEP-002 넘김, 설계 1): `page_action`·`wait_selector` 예외 전파와 옛 `retries=3` 없음 — 예외 전파는 유지하고 `retries`·`retry_delay` 를 되살렸다. `docs/crawl-reference.md` 「네트워크 타임아웃 → 3회 재시도」가 1~3단 모두에 맞는다.
- 닫힘(DEP-002 넘김, 설계 2): `+1 415 555 2671 2026-11-06 접수` 를 국내 패턴이 잡음 — 실제로는 국제 경로 미탐이었다(`+44 7911 123456 12 34 56` 경고 없음). 구분자 자리에서 다시 센다.
- 닫힘(DEP-002 넘김, 설계 3): certifi 하한 검사가 환경 마커·사전 릴리스·여러 줄 선언 우회를 잡지 못한다 — packaging 의미 검사로 바꿨다.
- 닫힘(DEP-002 넘김, 설계 4): `scripts/bootstrap.py` 는 import 가 되면 `pip install -r` 을 건너뛴다 — 설치판·제약식을 대조한다.
- 닫힘(DEP-002 넘김, 설계 5): 시험 `_forbid_stealth` 는 `patchright.sync_api.sync_playwright` 만 막는다 — patchright 모듈 전체와 `StealthyFetcher`·`StealthySession` 까지 막는다.
- 닫힘(DEP-002 넘김, 설계 6): `scrapling.engines.toolbelt.custom.Response` 는 공개 import 경로가 아니다 — 직접 고정 시험을 더했다.
- 닫힘(DEP-002 넘김): `scripts/profile_policy.py` 매핑의 `plaindynamic` 키는 DEP-002 에서 더해졌다(`profile_policy.py:67`).
- LOW(DEP-002 넘김, 할 일 없음): `troubleshooting.md:47` 은 과거 사고 원인 서술이라 당시 이름을 그대로 둔다(HCG-055 범위 결정).
- LOW(SECINTEL-001 넘김, 할 일 없음): CISA 사이트 피드가 자동 조회를 403 으로 막는다. GitHub 사본(cisagov/kev-data) 대체 경로가 이미 있다.
- LOW(SECINTEL-001 넘김): 구동 Chromium 156.0.8078.4 가 안정판 158 보다 두 메이저 뒤다. patchright 1.65 출시 뒤 상한을 함께 올릴 때 다시 잰다(PY311-001 상시 조건).
- LOW(SECINTEL-001 넘김): Chromium·curl_cffi 내장 libcurl 의 Brotli 판(KEV CVE-2026-111497)은 아직 확인하지 않았다. 다음 보안 인텔 수집에서 잰다.
- LOW(앞 조각 넘김): master 기준 체크아웃 엔진 사본 8f3277 표시 결함·로컬 커밋 319dee0 — applygo36 ADR-019 하네스 동결로 정기 점검 대상.
- LOW(앞 조각 넘김): 병합된 로컬 브랜치·orca 작업트리 barracuda·작업트리 rev5-secintel-dep·`~/.cache/web-crawler-dep001`·`dep002` 정리(사용자 확인 뒤).
- LOW(DEP-002 뒤 실측): 원본 체크아웃 venv 가 아직 scrapling 0.4.15 다. 설계 4 로 `bootstrap.py` 가 「준비 안 됨」(`scrapling 0.4.15 가 <0.6,>=0.5.1 에 맞지 않음`)으로 판정하므로, 병합 뒤 원본에서 `python scripts/bootstrap.py` 를 한 번 돌리면 갱신된다.
- 닫힘(독립 리뷰 LOW, Codex·Grok 공통): certifi 하한 검사가 고정 표본만 봐서 `>=2026.10.19rc2` 를 통과시키고 `>=2026.10.24,<2027` 을 거부했다 — 하한을 제약식에서 직접 읽도록 고침(021c919, RED 2건 확인).
- LOW(독립 리뷰, Grok): `bootstrap.py` 가 「준비 안 됨」 사유(`requirements_unsatisfied()`)를 화면에 찍지 않고 `pip install -r` 로 간다. 판정은 맞고 사유 표시만 없다.
- LOW(독립 리뷰, Grok 기록): 점 구분 16자리 `+1234.5678.9012.3456` 이 이제 전화번호 경고를 낸다(구분자 자리 절단 — 설계 2 가 정한 넓히기, 숫자열 한가운데는 자르지 않음).
- LOW(독립 리뷰 실행): DeepSeek(opencode-go/deepseek-v4.1-flash#max)은 두 번 모두 파일을 읽은 뒤 판정 줄 없이 종료코드 1 로 끝났다(오류 메시지 없음). 리뷰는 Codex·Grok 2명 PASS 로 갈음했다.

## 종료 분류
- missing: 없음
- partial: 없음
- contradicts: 없음
- unrequested: 없음
