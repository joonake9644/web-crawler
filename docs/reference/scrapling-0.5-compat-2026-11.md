# scrapling 0.5 호환 평가 (DEP-001, 2026-11-10 실측)

- 계획: REV-6 과제 DEP-001 · 조각 시작 커밋 96435ea
- 판정: **비호환 — `scrapling[fetchers]>=0.4.8,<0.5` 상한을 유지한다.** 제품 코드를 고치지 않고는 0.5.1에서 시험이 깨진다.

## 1. 원문 확인

| 출처 | 확인 내용 |
|---|---|
| GitHub 릴리스 v0.5 (2026-10-17) | 「호환이 깨지는 변경이 많다. 판 올림 안내서를 먼저 보라」는 경고가 있다 |
| GitHub 릴리스 v0.5.1 (2026-11-04) | 원격 브라우저 연결이 새 `RemoteSession`·`AsyncRemoteSession` 클래스로 옮겨졌다(호환 깨짐) |
| `docs/migrating-to-v0.5.md` (상류 main) | 아래 표 |

판 올림 안내서의 변경 가운데 이 저장소와 관계있는 것:

| 바뀐 점 | 이 저장소 사용처(`git grep`, `.codex/` 미러 제외) | 영향 |
|---|---|---|
| 일반 Playwright 백엔드 제거: `DynamicFetcher`·`DynamicSession`·`AsyncDynamicSession`·`PlayWrightFetcher`·`scrapling.fetchers.chrome` 삭제 | 코드 import: `scripts/utils.py:424`(`from scrapling.fetchers import DynamicFetcher`), `scripts/preflight.py:91`. 이름만 쓰는 곳: `scripts/domain_profile.py`·`scripts/profile_policy.py`(분류표), 시험 `scripts/test_utils.py` 외. 문서: 스킬 `SKILL.md`·`antibot-strategies.md`·`fetcher-patterns.md`·`troubleshooting.md`, `scripts/scrapling_reference.md`, `README.md`, `docs/agents-reference.md`, `docs/crawl-reference.md`. 프로필 2개(`fetcher_type: DynamicFetcher`) | **깨짐** |
| `StealthyFetcher`·`StealthySession` 의 `cdp_url` 제거 → `RemoteSession` | 0건(`git grep`) | 영향 없음 |
| `capture_xhr`·`captured_xhr` 제거 → `record_requests=True` + `session.network` | 0건(`git grep`) | 영향 없음 |
| `response.follow()` 가 요청 본문·쿼리를 넘기지 않음 | `scripts/test_e2e_phase4.py:75`(GET 따라가기) | 영향 없음(GET) |
| `robots_txt_obey=True` 조회 실패 시 그 도메인 차단 | 이 저장소는 `scripts/utils.py check_robots()`(protego)를 쓴다 | 영향 없음 |

## 2. 시험 환경 실측

저장소 밖 `~/.cache/web-crawler-dep001/` 에 `uv venv` 로 만들었다. `requirements.txt` 에서 scrapling 줄만 `==0.5.1` 로 바꾼 사본을 설치했다. 아래 시험 수는 certifi 하한 검사를 더하기 **전** 실측이다(더한 뒤 현행 범위 스위트는 675 통과).

| 환경 | Python | scrapling | playwright·patchright | `pytest -q -k "not e2e"` |
|---|---|---|---|---|
| py314-s051 | 3.14.7 | 0.5.1 | 1.64.1 · 1.64.4 | **4 실패**, 670 통과, 14 제외(단독 실행. 병렬 실행 때의 오류 1건은 같은 작업트리 `.tmp/pytest` 를 함께 써서 생긴 충돌이었고, 단독 실행에서는 나지 않았다) |
| py311-s051 | 3.11.15 | 0.5.1 | 1.64.1 · 1.64.4 | **4 실패**, 670 통과, 14 제외 |
| py311(현행 범위) | 3.11.15 | 0.4.15 | 1.64.1 · 1.64.4 | 674 통과, 14 제외, 종료 0 |

실패 4건(두 환경 같음), 원인은 모두 `DynamicFetcher`·`DynamicSession` 삭제다:

- `test_doc_contracts.py::test_documented_import_resolves[antibot-strategies.md:scrapling.fetchers.DynamicFetcher]`
- `test_doc_contracts.py::test_documented_import_resolves[fetcher-patterns.md:scrapling.fetchers.DynamicSession]`
- `test_utils.py::test_plain_dynamic_passes_google_search_false`
- `test_utils.py::test_plain_dynamic_allows_explicit_override`

fetcher 경로(0.5.1, 3.14, `from scrapling.fetchers import …`): `Fetcher`·`FetcherSession`·`StealthyFetcher`·`StealthySession`·`RemoteSession` 있음, `DynamicFetcher`·`DynamicSession` 없음. `scripts/preflight.py` 는 「Fetcher 클래스 로드」에서 FAIL(CORE 12 통과·1 실패)한다.

## 3. 판정과 다음 과제 후보

- 상한을 옮기려면 `DynamicFetcher` 경로를 `StealthyFetcher` 로 바꾸는 제품 코드 수정, 스킬·참조 문서와 프로필 2개 갱신, 생성 스크립트 템플릿 점검이 필요하다. 이는 DEP-001 의 「호환 확인까지만」 범위를 넘는다.
- 다음 과제 후보(계획 개정 필요): 「scrapling 0.5 판 올림 — DynamicFetcher 경로 이관(코드·문서·프로필)과 상한 `<0.6`」.

## 4. 같은 과제에서 한 런타임 갱신(로컬 `.venv`, 허용 범위 안)

| 패키지 | 전 | 후 |
|---|---|---|
| playwright | 1.62.0 | 1.64.1 |
| patchright | 1.62.3 | 1.64.4 |
| curl_cffi | 0.16.3 | 0.17.0 |
| certifi | 2026.7.22 | 2026.10.23(새 하한 `>=2026.10.19`) |
| Protego | 0.6.2 | 0.7.0 |
| pytest | 9.1.1 | 9.2.0 |

- `pip check`: 깨진 요구 없음.
- 구동 Chromium(playwright·patchright 둘 다): 156.0.8078.4. 1.64.x 도 `chromium-1248` 을 담는다. 안정판 158 은 허용 범위(`<1.65`) 안에서 따라잡을 수 없다.
- OSV `querybatch`(2026-11-10T04:04:00Z, 설치본 30개): 권고 0건. GHSA-6q48-6c7w-9gw2(certifi)는 닫혔다.
- playwright 1.65.0 은 나왔고 patchright 는 1.64.4 까지다(2026-11-10 `pip index`). 상한 규칙(두 패키지 모두에 나온 뒤에만 함께 올린다)대로 그대로 둔다.

## 5. 판 올림 결과 (DEP-002, 2026-11-10T15:51Z 실측)

위 3절의 다음 과제 후보를 REV-7 과제 DEP-002 로 진행했다. 단 3절의 「`StealthyFetcher` 로 바꾼다」는 택하지 않았다 — `StealthyFetcher` 는 patchright 위장 브라우저(사다리 B, 통지 게이트 대상)라 이음매 위 3단을 대신할 수 없다(조각 계약 「사다리 3단 대체 설계」).

| 무엇 | 결과 |
|---|---|
| 제약 | `scrapling[fetchers]>=0.5.1,<0.6` (하한도 0.5.1 — 0.4 와 섞인 venv 를 막는다) |
| 3단 | `scripts/utils.py plain_dynamic` 을 playwright 직접 호출(위장 없는 Chromium)로 다시 만들었다. 반환형은 scrapling `Response` 그대로, `google_search=True`·모르는 인자는 거부 |
| 분류표·프로필 | `plaindynamic` 키 추가. 프로필 3개 `fetcher_type` 을 `plain_dynamic` 으로. 옛 이름(`DynamicFetcher`·`DynamicSession`)은 매핑으로 계속 3단 |
| 스킬 정본(HCG-055) | `SKILL.md`·`antibot-strategies.md`·`fetcher-patterns.md`·`troubleshooting.md` 에서 옛 이름 지시 제거. 사다리 B 체인은 `DynamicFetcher` 티어를 빼 브라우저 티어가 `StealthyFetcher` 하나. 통지 게이트·안전 문장은 그대로 |
| preflight(3.14.7, 0.5.1) | CORE PASS 12 / FAIL 0 (「Fetcher 클래스 로드 — Fetcher/FetcherSession/StealthyFetcher + utils.plain_dynamic」) |
| `pytest -q -k "not e2e"` | 3.14.7(작업트리 `.venv`)·3.11.15(`~/.cache/web-crawler-dep002/py311`) 모두 **681 통과**, 14 제외, 종료 0 |
| 독립 리뷰 지적 수정 | Codex·DeepSeek·Grok 이 공통으로 짚은 옛 3단과의 의미 차이를 고쳤다 — networkidle 이 끝나지 않아도 그린 문서 반환, `page_action` 뒤 `wait_selector`(attached), status·헤더는 마지막 메인 문서 응답(`all_headers()`, 헤더는 옛 3단이 첫 응답에서 읽던 것과 다르다 — status 와 맞춤), 쿠키는 전체 레코드 튜플. 실제 Chromium·로컬 HTTP 서버 시험 5건(먼저 RED 확인) |

시험 수 변화: 스킬 문서 수정으로 문서에서 뽑는 매개변수 시험이 4 줄었다(680 → 676) — 빠짐 5(열거 `DynamicFetcher`·`DynamicSession`, import `scrapling.fetchers.DynamicFetcher`·`DynamicSession`, 옛 스크롤 예제의 `import time`), 더함 1(열거 `plain_dynamic`). 수집 목록 전후 diff 로 확인했다. 그 뒤 리뷰 지적 시험 5건을 더해 681 이다.

남은 차이:

- 3단은 scrapling `Fetcher.configure(adaptive=…)` 를 읽지 않는다. adaptive 가 필요하면 `Selector(page.html_content, adaptive=True, storage_args=…)` 로 다시 파싱한다(0.5.1 에서 클래스명이 바뀐 요소를 다시 찾는 것 실측, `SKILL.md` 셀렉터 자가 치유 절).
- `scrapling.engines.toolbelt.custom.Response` 는 공개 import 경로가 아니다. 상류가 옮기면 `test_utils.py` 반환형 시험이 먼저 깨진다.
- 실제 외부 사이트 e2e 는 돌리지 않았다(이름만 옮김, 계약 범위 밖).

### 후속(GAPS-001, 2026-11-12)

- 3단 재시도: 위 결과의 `plain_dynamic` 은 한 번만 시도했다(옛 3단·1·2단은 기본 `retries=3`). GAPS-001 에서 `retries=3`·`retry_delay=1` 을 같은 뜻으로 되살렸다 — 시도마다 새 브라우저, 마지막 실패는 그대로 올린다.
- `scrapling.engines.toolbelt.custom.Response` 는 `scripts/test_utils.py` 가 직접 import·`type(page) is Response` 로 고정한다.
- `scripts/bootstrap.py` 가 설치판을 제약식과 대조해, scrapling 0.4.15 가 남은 기존 venv 를 「준비 안 됨」으로 보고 `pip install -r` 을 돌린다(원본 체크아웃 venv 로 실측).
