# 조각 SECINTEL-001: 설치 의존성·런타임을 공개 취약점 데이터와 다시 대조해 2026-11 보안 인텔 브리프를 남긴다
- 위험 등급: light
- 핵심 경로: no
- 세션 예산: 1
- 계획 과제: SECINTEL-001
- 허용 경로: .gitignore, docs/security/intel-brief-2026-11-09.md, docs/task-contracts/SECINTEL-001.slice.md, .harness/state.json, docs/session-handoff.md

## 합격 기준
1. `.venv` 에 설치된 패키지 전부(이름·판)와 `requirements.txt` 제약을 OSV(필요하면 GHSA·CISA KEV)와 대조한 결과가 비공개 증거 폴더 `~/Developer/security-evidence/web-crawler/intel-brief-2026-11-09.md` 에 근거(조회 명령·응답 요약·조회 시각)와 함께 있다.
2. 공개 저장소용 요약 `docs/security/intel-brief-2026-11-09.md` 가 있고, 버전 지문·설정 상세·매칭 근거는 담지 않는다(`security-program` 단계 6, 직전 브리프 2026-10-31 과 같은 형식).
3. 나온 취약점마다 등급·영향 경로(이 저장소가 그 코드를 실제로 부르는지)·고칠 과제 후보가 요약에 있다. 취약점이 0건이면 0건과 조회 범위를 적는다.
4. 실행 계약 6종이 모두 exit 0 이다.

## 검사 명령
- `.venv/bin/python -m pytest -q -k "not e2e"`
- `.venv/bin/python scripts/continuity_check.py`
- `.venv/bin/python scripts/sync_domain_list.py --check`
- `.venv/bin/python scripts/sync_codex_mirror.py --check`
- `.venv/bin/python scripts/sync_agent_contract.py --check`
- `.venv/bin/python scripts/session_handoff.py --check`

## 불변 제약
- 취약점을 찾아도 이 조각에서 고치지 않는다. 수정·의존성 판 변경은 사용자 승인으로 새 과제(DEP-001 또는 새 과제)에서 한다.
- `requirements.txt`·`scripts/`·`.venv` 설치 판을 바꾸지 않는다.
- `active_work`(PY311-001)·승인 고정 sha256·ADR 기준점은 바꾸지 않는다.
- 하네스 핵심 파일(`.plan/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, 스킬·훅)은 고치지 않는다(applygo36 ADR-019 하네스 동결, 전역 관문 HCG).
- 대상은 `docs/security/SCOPE.md` 범위 안(이 저장소·소유자 로컬 환경)뿐이다. 제3자 시스템에 도구를 돌리지 않는다.

## 범위 밖(하지 않는 것)
- scrapling 0.5 호환 평가와 런타임 갱신(DEP-001).
- GitHub 저장소 보안 설정 변경(소유자가 직접).
- 코드 정적 분석·모의 침투(SEC-001 범위, 이번은 의존성 인텔만).

## 갭 목록
- LOW: 계획 REV-5 가 브리프 파일 이름을 작성일(2026-11-09)로 정했고 실제 수집은 2026-11-10 이다. 파일 이름은 계획대로 두고 본문에 수집 시각을 적는다.
- HIGH(이 조각에서 고치지 않음, 불변 제약): 간접 의존 certifi 2026.7.22 에 GHSA-6q48-6c7w-9gw2(CRITICAL, 유출된 emSign 중간 CA). 고칠 과제 후보: `requirements.txt` 에 `certifi>=2026.10.19` 하한 + venv 갱신 + 하한 검사(TDD). DEP-001 에 넣으려면 계획 개정(사용자 승인).
- LOW: 구동 Chromium 156.0.8078.4 가 안정판 158.0.8127.18 보다 두 메이저 뒤. DEP-001 런타임 갱신에서 잰다.
- LOW: Chromium·curl_cffi 내장 libcurl 의 Brotli 판(KEV CVE-2026-111497) 미확인.
- LOW: CISA 사이트 피드가 자동 조회를 403 으로 막음 → GitHub 사본(cisagov/kev-data)으로 대체. 다음 수집도 같은 경로.
- LOW(앞 조각 SEC001-CLOSE 에서 넘김): master 기준 체크아웃 엔진 사본 8f3277 표시 결함·로컬 커밋 319dee0 — applygo36 ADR-019 하네스 동결로 정기 점검 대상.
- LOW(앞 조각에서 넘김): `+1 415 555 2671 2026-11-06 접수` 를 국내 패턴이 잡음(경고는 나옴, 제품 영향 없음).
- LOW(앞 조각에서 넘김): 병합된 로컬 브랜치·orca 작업트리 barracuda 정리(사용자 확인 뒤).
- 닫힘(앞 조각에서 넘김): REV-3 과제 SEC001-CLOSE 완료 표시 — REV-4 에서 처리됨.

## 종료 분류
- missing: 없음
- partial: 없음
- contradicts: 없음
- unrequested: 없음
