# 보안 인텔 브리프 — web-crawler (2026-10-31, 실측)

스택(설치본, `.venv` importlib.metadata): Python 3.14.7 · scrapling 0.4.15 · playwright 1.62.0 · patchright 1.62.3 · curl_cffi 0.16.3 · protego 0.6.2 · openpyxl 3.1.5 · pytest 9.1.1

## 1. OSV 생태계 대조(설치본 버전)
설치본 7개 전부 **알려진 취약점 0건**(api.osv.dev querybatch).

## 2. 감시 저장소 GHSA(상류)
curl_cffi 3건 — 우리 0.16.3 판정:
- GHSA-3vpc-4p9p-47hc (libcurl, `<=0.6.4`) → 해당 없음
- GHSA-qw2m-4pqf-rmpp (리다이렉트 SSRF, `<=v0.15.0b4`) → 해당 없음
- GHSA-6hxm-c8cx-7jq3 (동기 WebSocket 메시지 누적, medium, 2026-10-26) → **해당 없음**: 우리는 curl_cffi를 HTTP(`requests as cffi`)로만 씀. 저장소의 WebSocket 참조는 chrome_cdp의 CDP 표준 ws(별개)
Scrapling·playwright 저장소 GHSA 0건.

## 3. CISA KEV(알려진 악용) — 스택 매칭
Chromium/V8 65건(총 1766, 최신 2026-10-30). 우리 크롤러가 Chromium을 구동(사다리 3·5·6)하므로 관련.
→ 상시 방어: 구동 Chromium을 최신으로 유지(`scrapling install`/`playwright install` 재실행). 신뢰 못 할 페이지 렌더링 시 위험 커짐.

## 4. 설정 실측
- `web-crawler` 저장소 **Dependabot 경보 꺼짐**(gh api 403) → 켜기 권고(싼 방어, B05/B22).

## 5. 환경 메모
- Python 3.14.7: scrapling·playwright 분류자 상한은 3.13. 동작은 함(실측)이나 공식 미지원 버전 — 상류가 3.13 고정 가정을 깨는 변경을 내면 영향 가능.

## 판정
설치 의존성에 알려진 취약점 없음(양호). **상시 관리 2건**: ① 구동 Chromium 최신 유지 ② Dependabot 경보 켜기.
다음 수집: 7일 뒤(브리프 신선도 게이트) 또는 lockfile 변경 시.
