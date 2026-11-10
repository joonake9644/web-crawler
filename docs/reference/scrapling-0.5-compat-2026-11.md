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
| 일반 Playwright 백엔드 제거: `DynamicFetcher`·`DynamicSession`·`AsyncDynamicSession`·`PlayWrightFetcher`·`scrapling.fetchers.chrome` 삭제 | `scripts/utils.py:424`(`from scrapling.fetchers import DynamicFetcher`), `scripts/preflight.py:91`, 스킬 참조 문서 `antibot-strategies.md`·`fetcher-patterns.md`·`troubleshooting.md`·`SKILL.md`, `docs/crawl-reference.md`, 프로필 2개(`fetcher_type: DynamicFetcher`) | **깨짐** |
| `StealthyFetcher`·`StealthySession` 의 `cdp_url` 제거 → `RemoteSession` | 스킬 문서 일부 | 문서 수정 필요 |
| `capture_xhr`·`captured_xhr` 제거 → `record_requests=True` + `session.network` | 스킬 문서 일부 | 문서 수정 필요 |
| `response.follow()` 가 요청 본문·쿼리를 넘기지 않음 | `scripts/test_e2e_phase4.py:75`(GET 따라가기) | 영향 없음(GET) |
| `robots_txt_obey=True` 조회 실패 시 그 도메인 차단 | 이 저장소는 `scripts/utils.py check_robots()`(protego)를 쓴다 | 영향 없음 |

## 2. 시험 환경 실측

저장소 밖 `~/.cache/web-crawler-dep001/` 에 `uv venv` 로 만들었다. `requirements.txt` 에서 scrapling 줄만 `==0.5.1` 로 바꾼 사본을 설치했다.

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
