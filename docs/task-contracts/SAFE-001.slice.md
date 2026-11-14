# 조각 SAFE-001: 내려받은 파일(xlsx·pdf·docx·csv)까지 개인정보를 검사하고, 상태가 바뀌는 화면은 수집 전에 알린다
- 위험 등급: full
- 핵심 경로: yes
- 세션 예산: 1
- 계획 과제: SAFE-001
- 허용 경로: scripts/utils.py, scripts/test_utils.py, scripts/test_pii_files.py, requirements.txt, .claude/skills/web-crawler/SKILL.md, .codex/skills/web-crawler/SKILL.md, docs/task-contracts/SAFE-001.slice.md, .gitignore, .harness/state.json, docs/session-handoff.md

## 출발 실측(2026-11-14, master 9e73ea2)
- `detect_pii(data)` 는 **수집 표의 행(dict 리스트)만** 본다. 내려받은 파일의 내용은 보지 않는다.
- DIR-003 그룹웨어 시험에서 「출입국 변동신고 대상자 명단.xlsx」(유학생 개인정보 가능성)를 내려받았으나 PII 경고는 표의 「작성부서/담당자」 컬럼 1건뿐이었다(F8). 파일 안은 검사되지 않았다.
- 스킬에는 「열람만으로 상태가 바뀌는 화면(미확인 문서함·일괄 확인 버튼)」을 수집 전에 가려내라는 안내가 없다(F10). 이번 시험에서는 메인이 임의로 보류했다.

## 설계
- `scripts/utils.py` 에 `detect_pii_in_files(paths)` 를 더한다 — 파일을 글자/행으로 바꿔 기존 `detect_pii` 판정을 그대로 태운다. 값은 로깅하지 않고 (종류, 파일)당 한 줄 경고만 남긴다(기존 규칙과 같다).
  - xlsx: 이미 있는 `openpyxl`(헤더를 컬럼명으로, 각 행을 dict 로). csv·txt: stdlib. pdf: `pdfminer.six`. docx: `python-docx`.
  - **가벼운 추출기만 쓴다 — markitdown 의 `onnxruntime`·`magika` 같은 ML 의존성은 넣지 않는다**(오늘 실측: markitdown[xlsx,pdf,docx] 가 약 30개 의존성·onnxruntime 을 끌어온다).
  - 추출 실패(암호화·손상 등)는 삼키지 말고 「검사 못 함」으로 그 파일을 경고한다 — 통과로 두지 않는다.
- 명단 형태 보강: 컬럼 헤더가 약해도(예: 열 이름이 없거나 모호해도) 사람 이름 값이 한 열에 여러 행 쌓이면 경고한다. 기존 판정은 약화하지 않고 넓히기만 한다.
- `SKILL.md` Step 2-A 에 「열람·조회만으로 서버 상태가 바뀔 수 있는 화면(미확인 수신함·일괄 확인/승인 버튼 등)은 수집 전에 사용자에게 알리고 고르게 한다」를 더하고, `python scripts/sync_codex_mirror.py` 로 미러를 재생성한다.

## 합격 기준(먼저 RED 로 확인한 뒤 GREEN)
1. `detect_pii_in_files([이름·주민번호 컬럼이 있는 임시 xlsx])` 가 그 파일을 가리키는 PII 경고를 돌려주고, PII 없는 파일·빈 리스트는 경고가 없다.
2. xlsx·csv·pdf·docx 네 형식에서 각각 글자를 뽑아 검사한다(형식별 시험). 추출 못 하는 파일은 「검사 못 함」 경고가 난다.
3. 컬럼 헤더가 약한 명단(이름 값이 한 열에 여러 행)이 경고된다. 기존 `detect_pii` 시험은 그대로 통과한다(판정 약화 없음).
4. `detect_pii_in_files` 와 추출 경로가 `onnxruntime`·`magika` 를 import 하지 않는다(시험으로 확인).
5. `SKILL.md` Step 2-A 에 상태 변경 화면 통지 규칙이 있고 `scripts/sync_codex_mirror.py --check` 가 exit 0 이다.

## 검사 명령(slice close 때 CLI 가 직접 실행)
- `.venv/bin/python -m pytest -q -k "not e2e"`
- `.venv/bin/python scripts/continuity_check.py`
- `.venv/bin/python scripts/sync_domain_list.py --check`
- `.venv/bin/python scripts/sync_codex_mirror.py --check`
- `.venv/bin/python scripts/sync_agent_contract.py --check`
- `.venv/bin/python scripts/session_handoff.py --check`
- `.venv/bin/python scripts/preflight.py --core-only --no-network`
- `/Users/joonake/.cache/web-crawler-dep002/py311/bin/python -m pytest -q -k "not e2e"`

## 불변 제약
- `detect_pii` 기존 판정을 약화하지 않는다(넓히기만). 파일 안의 값을 화면·로그에 출력하지 않는다.
- ML 의존성(onnxruntime·magika 등)을 더하지 않는다. `plain_get`·`PLAIN_KWARGS`·스킬 정본 외 하네스 파일은 고치지 않는다(applygo36 ADR-019).
- 새 의존성은 `requirements.txt` 에만 더하고 playwright·patchright 결합(ADR-002)은 건드리지 않는다.

## 범위 밖(하지 않는 것)
- CAPTCHA 자동 풀이·우회. Accept 헤더·검색 검증(ACC-001). 벤치마크(BENCH-001). 쿠키 도우미·확장자 보존(SAFE-002). 실제 수집 재실행.

## 갭 목록(진행 중 기록, 등급: BLOCKING / HIGH / MEDIUM / LOW / UNREQ)
- LOW(GAPS-002 넘김): `test_rate_limiter_enforces_delay` 가 벽시계 경계(0.499…<0.5)로 드물게 실패. 단조 시계로 바꾸는 것은 별도 조각.
- LOW(GAPS-002 넘김): `plain_get` 은 UA 를 안 보내면 scrapling 이 고정 브라우저 UA 를 넣는다. 사다리 1단 정직 UA 는 별도 결정.
- LOW(GAPS-001 넘김): 병합된 로컬 브랜치·작업트리·`~/.cache/web-crawler-dep001`·`dep002` 정리(사용자 확인 뒤).
- LOW(DIR-003): DeepSeek 리뷰어 OpenCode Go 구독 없음으로 판정 없이 종료.
- MEDIUM(DIR-003 F4, SAFE-002 로 이관): 새 도메인 프로필이 `.gitignore` 밖·`sync_domain_list` 어긋남. news.unn.net 정식 커밋은 SAFE-002/DOC-001.

## 종료 분류(missing / partial / contradicts / unrequested)
- missing:
- partial:
- contradicts:
- unrequested:
