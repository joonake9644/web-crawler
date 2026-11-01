"""scripts/test_chrome_cdp.py — Chrome CDP 실행 인자 안전성"""
from chrome_cdp import _build_chrome_args


def test_url_is_after_switch_terminator():
    # CWE-88: url 이 `--` 뒤에 와야 Chrome 이 스위치로 해석하지 못한다.
    args = _build_chrome_args("/usr/bin/chrome", 9222, "/tmp/p", "https://example.com")
    assert "--" in args, "스위치 종료자 `--` 가 없다"
    assert args.index("--") < args.index("https://example.com"), "url 이 `--` 앞에 있다"


def test_switch_like_url_cannot_inject():
    # `--gpu-launcher=...` 같은 입력이 스위치 자리에 오면 안 된다 — `--` 뒤에 위치해야 한다.
    evil = "--gpu-launcher=touch /tmp/pwned"
    args = _build_chrome_args("/usr/bin/chrome", 9222, "/tmp/p", evil)
    term = args.index("--")
    assert args.index(evil) > term, "스위치형 url 이 종료자 앞에 있어 주입 가능"
    # 종료자 앞에는 우리가 의도한 Chrome 스위치만 있어야 한다.
    assert evil not in args[:term], "악성 url 이 스위치 구역에 들어갔다"


def test_about_blank_still_works():
    # 기본값 about:blank 도 `--` 뒤에서 정상적으로 열린다(회귀).
    args = _build_chrome_args("/usr/bin/chrome", 9222, "/tmp/p", "about:blank")
    assert args[-1] == "about:blank"
    assert args[-2] == "--"
