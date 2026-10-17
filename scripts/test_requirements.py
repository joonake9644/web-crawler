"""requirements.txt 가 '직접 import 하는 것은 직접 선언한다' 원칙을 지키는지 검사."""
from pathlib import Path
import re

import pytest

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


def _declared():
    """주석·빈 줄을 뺀 '패키지명 -> 원문 줄' 매핑."""
    out = {}
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped:
            continue
        name = stripped.split(">=")[0].split("==")[0].split("[")[0].strip().lower()
        out[name] = stripped
    return out


@pytest.mark.parametrize("package", ["scrapling", "playwright", "curl_cffi", "patchright",
                                     "protego", "openpyxl", "pytest"])
def test_direct_imports_are_declared(package):
    assert package in _declared(), (
        f"{package} 를 코드가 직접 쓰는데 requirements.txt 에 선언되지 않았습니다"
    )


def _constraint(package: str) -> str:
    """선언된 줄에서 버전 제약식만 떼어낸다 (패키지명·extras 는 제외).

    `KeyError` 로 죽지 않는다 (2026-10-01 독립 리뷰 [Low]) — 패키지가
    declarations 에서 사라지면 아래 테스트가 **메시지와 함께** 실패해야 한다.
    예외로 죽으면 왜 깨졌는지 읽는 사람이 모른다.
    """
    line = _declared().get(package, "")
    for index, char in enumerate(line):
        if char in "<>=":
            return line[index:].strip()
    return ""


def _version_upper_bound(constraint: str) -> str | None:
    """**버전** 상한만 뽑는다 — 환경 마커의 `<` 로 통과하지 못하게 한다.

    `python_version<"3.14"` 에도 `<` 가 있으므로 substring 검사만 하면
    "버전 상한이 없는데 통과"하는 구멍이 생긴다(독립 리뷰 finding).
    """
    # 환경 마커는 `;` 뒤에 온다(PEP 508). 앞부분만 본다 — `python_version<3.14`
    # 같은 마커의 `<` 를 버전 상한으로 오인하지 않는다 (2026-10-01 독립 리뷰 [Low]).
    specifier = constraint.split(";", 1)[0]
    match = re.search(r"<\s*(\d[\w.]*)", specifier)
    return match.group(1) if match else None


def test_version_upper_bound_ignores_environment_markers():
    """환경 마커의 `<` 를 버전 상한으로 오인하지 않는다 (2026-10-01 독립 리뷰 [Low]).

    `python_version<"3.14"` 는 마커지 상한이 아니다. 이 경로를 실행하는 테스트가
    없어서, 실수로 마커를 인용 없이(`python_version<3.14`) 쓰면 오인할 수 있었다.
    마커는 늘 문자열 리터럴을 요구하므로 실제로는 무해하지만 못 박아 둔다.
    """
    assert _version_upper_bound('>=1.62,<1.64; python_version<"3.14"') == "1.64"
    assert _version_upper_bound('>=1.62; python_version<"3.14"') is None
    assert _version_upper_bound('>=1.62') is None
    # 2026-10-01 독립 리뷰 [Low]: 마커가 **인용 없이** 오면(`python_version<3.14`,
    # 잘못된 PEP 508 이지만 파싱은 된다) `;` 뒤도 버전 제약으로 오인해 "3.14" 를
    # 상한으로 반환했다. `;` 앞만 보게 고쳐 그 경로를 실제로 고정한다.
    assert _version_upper_bound('>=1.62; python_version<3.14') is None


def test_playwright_has_upper_bound():
    """상한은 다음 마이너가 한쪽에만 나왔을 때 독주를 막는 브레이크다(ADR-002).

    결합 그 자체를 강제하지는 못한다 — 제약식이 같아도 해석된 *패치* 버전은
    달라질 수 있다(patchright 만 1.60.1/1.61.2/1.62.3 같은 추가 패치가 있다).
    강제하는 것은 "한쪽만 상한을 올리는 변경"이다. 그건 이 검사가 먼저 잡는다.
    """
    upper = _version_upper_bound(_constraint("playwright"))
    assert upper is not None, (
        f"playwright 에 버전 상한이 없습니다 (제약식={_constraint('playwright')!r}) — "
        "다음 마이너 출시에 patchright 를 두고 독주할 수 있습니다. "
        "requirements.txt 의 두 줄에 같은 상한을 두세요"
    )
    assert _version_upper_bound(_constraint("patchright")) == upper, (
        f"상한이 다릅니다 — playwright={upper} vs patchright="
        f"{_version_upper_bound(_constraint('patchright'))} (ADR-002)"
    )


def test_playwright_and_patchright_constraints_identical():
    """두 줄의 제약식을 같게 둔다 — 한쪽만 고치는 변경을 이게 먼저 잡는다."""
    playwright = _constraint("playwright")
    patchright = _constraint("patchright")
    assert playwright and patchright, (
        f"제약식이 비었습니다 (playwright={playwright!r}, patchright={patchright!r}) — "
        "두 줄 모두에 버전 제약을 적어야 결합이 표현된다 (ADR-002)"
    )
    assert playwright == patchright, (
        f"playwright={playwright!r} 와 patchright={patchright!r} 가 다릅니다 — "
        "두 줄의 제약식을 같게 두세요 (ADR-002)"
    )


_PLAYWRIGHT_DECL = re.compile(r"\s*playwright\s*(?:[<>=!~;\[]|$)", re.IGNORECASE)


def _coupling_comment() -> str:
    """ADR-002 결합 주석 블록(`⚠ playwright 와 patchright` 부터 playwright 선언 줄 앞까지).

    공백을 한 칸으로 정규화해 돌려준다 — 줄바꿈 위치가 바뀌어도 문장 검사가 흔들리지 않는다.
    끝은 시작점 **뒤의** 정확한 `playwright` 선언이다. 선행 공백이 있거나
    `playwright-stealth` 같은 다른 패키지 줄이 끼어도 거기서 잘리지 않는다(2026-10-15 독립 리뷰 [Low]).
    """
    lines = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if "playwright 와 patchright" in l), None)
    end = None
    if start is not None:
        end = next((i for i in range(start + 1, len(lines)) if _PLAYWRIGHT_DECL.match(lines[i])), None)
    assert start is not None and end is not None, (
        "requirements.txt 에서 ADR-002 결합 주석 블록을 찾지 못했습니다"
    )
    block = [l.strip().lstrip("#").strip() for l in lines[start:end] if l.strip().startswith("#")]
    return " ".join(" ".join(block).split())


def test_upper_bound_raise_waits_for_both_packages():
    """상한을 올리는 조건은 '두 패키지 **모두** 다음 마이너가 출시됐을 때'다(ADR-002).

    2026-10-15 pypi.org 실측: playwright 1.64.0 은 2026-10-13 출시, patchright 는
    1.63.0 이 최신이다. 옛 주석 "1.64 가 나오면 두 줄을 함께 올린다" 는 이 상태에서
    상한을 올리라는 뜻으로 읽힌다 — 올리면 playwright 1.64 + patchright 1.63 으로
    갈라져 브레이크가 막으려던 바로 그 분할이 생긴다.
    """
    comment = _coupling_comment()
    upper = _version_upper_bound(_constraint("playwright"))
    assert "1.64 가 나오면 두 줄을 함께 올린다" not in comment, (
        "한쪽만 출시돼도 상한을 올리라고 읽히는 옛 문장이 남아 있습니다 (ADR-002)"
    )
    # 낱말("두 패키지 모두")만 보면 "두 패키지 모두의 상한은 playwright 1.64 출시 즉시
    # 올린다" 도 통과한다(2026-10-15 독립 리뷰 [Low]). 조건 문장 전체를, 현재 상한 값으로 본다.
    for sentence in (f"두 패키지 모두에 {upper} 가 나온 뒤에만 두 줄을 함께 올린다",
                     "한쪽만 나온 동안은 그대로 둔다"):
        assert sentence in comment, (
            f"상한을 올리는 조건 문장 「{sentence}」 이 주석에 없습니다 (ADR-002)"
        )


_RANGE_SPEC = re.compile(r">=\s*(\d+(?:\.\d+)*)\s*,\s*<\s*(\d+)\.([1-9]\d*)")


def _allowed_range(constraint: str) -> tuple[str, str] | None:
    """`>=A,<M.N`(N≥1) 꼴이면 (하한 A, 마지막 허용 마이너 'M.(N-1)'), 그 밖의 꼴은 None.

    다른 꼴을 어림으로 읽지 않는다 — 읽지 못하면 검사가 실패해 사람이 함께 고치게 한다.
    """
    match = _RANGE_SPEC.fullmatch(constraint.split(";", 1)[0].strip())
    if not match:
        return None
    lower, major, minor = match.groups()
    return lower, f"{major}.{int(minor) - 1}"


def _release(version: str) -> tuple[int, ...]:
    """끝의 0 을 뗀 숫자 튜플 — `1.62.0` 과 `1.62` 를 같은 하한으로 본다."""
    parts = [int(p) for p in version.split(".")]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def test_allowed_range_reads_only_the_supported_form():
    """`>=A,<M.N`(N≥1) 꼴만 범위로 읽는다 (2026-10-17 독립 리뷰 [Low] 3건).

    상한이 여럿이거나(`<1.65,<1.64`) 하한이 둘이면 앞부분만 읽어 실제 범위와 다른 주석이
    통과했고, `<2.0` 은 `2.-1` 을 요구했고, `>=1.62.0` 은 `1.62` 와 같은 하한인데 실패했다.
    """
    assert _allowed_range(">=1.62,<1.65") == ("1.62", "1.64")
    assert _allowed_range('>=1.62,<1.70; python_version<"3.14"') == ("1.62", "1.69")
    assert _allowed_range(">=1.62.1,<1.65") == ("1.62.1", "1.64")
    for unsupported in (">=1.62,<2.0", ">=1.62,<1.65,<1.64", ">=1.62,>=1.63,<1.65",
                        ">=1.62,<1.65.1", ">=1.62", "<1.65"):
        assert _allowed_range(unsupported) is None, unsupported
    assert _release("1.62.0") == _release("1.62") != _release("1.62.1")


def test_coupling_comment_states_actual_range():
    """주석의 '허용 범위 A ~ B.x' 가 실제 제약식과 같다(ADR-002 '주석이 거짓말' 재발 방지).

    상한만 올리고 주석의 범위 문장을 두면 주석이 다시 낡은 사실을 말한다 —
    ADR-002 가 처음 고친 결함("(둘 다 1.62.x)")이 바로 그 모양이었다.
    """
    constraint = _constraint("playwright")
    allowed = _allowed_range(constraint)
    assert allowed, (
        f"제약식 {constraint!r} 은 이 검사가 읽는 `>=A,<M.N`(N≥1) 꼴이 아닙니다 — "
        "꼴을 바꿨다면 이 검사도 함께 고치세요 (ADR-002)"
    )
    stated = re.search(r"허용 범위 (\d+(?:\.\d+)*) ~ (\d+\.\d+)\.x", _coupling_comment())
    assert stated, "주석에 「허용 범위 A ~ B.x」 문장이 없습니다 (ADR-002)"
    lower, last_minor = allowed
    assert (_release(stated.group(1)), stated.group(2)) == (_release(lower), last_minor), (
        f"주석의 허용 범위 「{stated.group(0)}」 가 제약식({constraint})과 다릅니다 — "
        f"「허용 범위 {lower} ~ {last_minor}.x」 여야 합니다 (ADR-002)"
    )


def test_scrapling_has_upper_bound():
    """pre-1.0 이고 v0.3 breaking 전력이 있어 상한이 필수다."""
    assert "<0.5" in _declared()["scrapling"], (
        "scrapling 에 상한(<0.5)이 없습니다 — 0.5 가 나오면 생성 스크립트가 일괄로 깨집니다"
    )


def test_protego_comment_is_true():
    """requirements.txt 의 주석이 실제 코드와 일치하는지.

    G3 의 재발 방지 — protego 는 '런타임에서 사용' 이라고 적혀 있으면서 실제로는
    어디서도 import 되지 않은 채 오래 방치됐다. 주석이 이름을 대면 그 이름은 존재해야 한다.
    """
    import utils
    assert hasattr(utils, "check_robots"), (
        "requirements.txt 의 protego 주석이 scripts/utils.py check_robots() 를 가리키는데 "
        "그 함수가 없습니다 — 주석이 사실과 다릅니다"
    )
