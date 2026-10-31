---
name: authorized-defensive-security
description: 소유자 자산에 대한 승인된 방어 보안 점검(자가 침투 테스트·레드팀 시뮬레이션·취약점 분석)을 할 때 사용한다. "보안 점검해줘", "취약점 찾아줘", "모의 침투", "레드팀", "self-pentest", "공격해보고 막아줘" 같은 요청에 트리거된다. 결과는 언제나 찾기 → 고치기 → 회귀 테스트다.
---

# 승인된 방어 보안 점검

## 먼저 읽는다 (순서대로)

1. `docs/security/SCOPE.md` — 범위 안/밖. **범위 밖이면 멈추고 묻는다.**
2. `docs/security/AUTHORIZATION.md` — 역할·프레이밍 규칙·보고 형식·가드레일.
3. `docs/security/engagement-loop.md` — 7단계 루프와 실행 명령.

## 반드시 지킨다

- 모든 finding 은 **RED(수정 전 FAIL 실측) → 최소 수정(GREEN) → 회귀 테스트** 로 닫는다.
  RED 를 확인하지 않은 테스트는 아무것도 검증하지 않은 것이다.
- 공격자 관점은 "무엇을 테스트할지" 고르는 데만 쓴다. 제3자를 겨냥하는 독립 공격 도구는 만들지 않는다.
- 스캐너(ZAP·Nuclei·sqlmap·ffuf)는 `SCOPE.md` 에 적힌 소유자 URL 에만, 소유자가 직접 실행한다.
- 실제 비밀값·개인정보는 보고서에서 가린다.
- 작업은 `docs/task-contracts/SEC-<번호>.md` 계약으로 남기고 `.harness/policy.json` 에 등록한다
  (진행 중인 다른 작업이 있으면 `interrupt` 로, `return_to` 는 그 작업).
- 완료 선언은 `AGENTS.md` 실행 계약 6종이 모두 exit 0 인 출력을 본 뒤에만 한다.

## 다른 프로젝트로 옮길 때

이 스킬 폴더와 `docs/security/AUTHORIZATION.md`·`engagement-loop.md` 를 복사하고,
`SCOPE.md` 만 그 프로젝트의 자산·URL 로 다시 쓴다. 실행 명령 표는 그 프로젝트의 테스트 명령으로 바꾼다.
