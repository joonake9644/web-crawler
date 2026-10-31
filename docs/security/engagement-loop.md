# 가상 침투 훈련 루프 (runbook)

한 바퀴 = 아래 7단계. 각 단계의 산출물은 작업 계약(`docs/task-contracts/SEC-*.md`)에 남긴다.
범위는 [`SCOPE.md`](SCOPE.md), 역할·프레이밍은 [`AUTHORIZATION.md`](AUTHORIZATION.md).

| # | 단계 | 이 저장소에서 하는 일 | 산출물 |
|---|---|---|---|
| 1 | 인벤토리 | 입력(수집 데이터·URL), 비밀(쿠키·토큰 파일), 출력(엑셀·JSON), 문서가 시키는 코드, 의존성 | 표면 목록 |
| 2 | 위협 모델 | 표면마다 "공격자가 무엇을 하면 방어가 빠지는가" — 예: 51행부터 PII 넣기, 0644 쿠키 읽기 | 가설 목록 |
| 3 | 통제된 테스트 (RED) | 가설을 **로컬 테스트로** 재현한다. 수정 전 코드에서 FAIL 을 실측 | RED 로그 |
| 4 | finding 기록 | `AUTHORIZATION.md` §5 형식 | finding 표 |
| 5 | 수정 (GREEN) | 최소 수정. 오탐 규율(F11 등 기존 주석) 유지 | 커밋 |
| 6 | 회귀 | 테스트를 `-k "not e2e"` 스위트에 남긴다 → CI 가 막는다 | 테스트 이름 |
| 7 | 재검사·종료 | 실행 계약 6종 exit 0, 독립 리뷰, 상태 `retested-closed` | 실측 출력 |

## 실행 명령 (venv 안)

```text
python -m pytest -q -k "not e2e"
python scripts/continuity_check.py
python scripts/sync_domain_list.py --check
python scripts/sync_codex_mirror.py --check
python scripts/sync_agent_contract.py --check
python scripts/session_handoff.py --check
```

## 의존성 인텔 (주기)

7일마다 또는 `requirements.txt` 변경 시: 설치본 버전을 OSV(`api.osv.dev`)·GHSA·CISA KEV 와 대조해
`docs/security/intel-brief-<날짜>.md` 로 남긴다. 첫 기록: [`intel-brief-2026-10-31.md`](intel-brief-2026-10-31.md).

## 소유자의 웹 앱에 적용할 때 (이 저장소 밖)

폼·API 가 있는 소유자 앱이면 3단계에서 표준 도구를 **소유자 URL(스테이징·프리뷰)** 에만 쓴다:
OWASP ZAP(자동 스캔) · Nuclei(템플릿 스캔, CI 연동) · sqlmap(SQLi) · ffuf(숨은 경로) ·
자체 부하 스크립트(rate limit · Turnstile · BotID 가 실제로 막는지). 그 앱의 `SCOPE.md` 에 URL 을 먼저 적는다.

## 이 루프의 첫 실행

SEC-001 (2026-10-31) — [`docs/task-contracts/SEC-001.md`](../task-contracts/SEC-001.md).
