"""preflight HTTP 점검이 사다리 1단 `utils.plain_get` 으로 요청하는지 검사(PREFLIGHT-001).

옛 점검은 `Fetcher()` 인스턴스(deprecated 경고)로 scrapling 기본값을 그대로 써서
위장 TLS·위장 헤더와 지어낸 `Referer: https://www.google.com/` 를 보냈다.
모든 시험은 외부 네트워크 없이 돈다 — Fetcher 인스턴스 생성을 막고, 실제 요청은 로컬 서버로만 보낸다.
"""
import http.server
import threading

import pytest

import preflight
import utils


class _Page:
    def __init__(self, status):
        self.status = status


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    monkeypatch.setattr(preflight, "_results", [])
    from scrapling.fetchers import Fetcher

    def _no_instance(self, *a, **kw):
        raise AssertionError("Fetcher 인스턴스를 만들면 안 된다(deprecated, 위장 기본값)")

    monkeypatch.setattr(Fetcher, "__init__", _no_instance)


def _statuses():
    return [(status, name) for group, status, name in preflight._results if group == "CORE"]


def test_http_check_calls_plain_get_with_check_url(monkeypatch):
    calls = []

    def _fake_plain_get(url, **kw):
        calls.append((url, kw))
        return _Page(200)

    monkeypatch.setattr(utils, "plain_get", _fake_plain_get)
    preflight.check_http_fetch()
    assert calls == [("https://httpbin.org/html", {})]
    assert preflight.HTTP_CHECK_URL == "https://httpbin.org/html"


@pytest.mark.parametrize("status,expected", [(200, "PASS"), (503, "WARN")])
def test_http_check_verdict_by_status(monkeypatch, status, expected):
    calls = []
    monkeypatch.setattr(utils, "plain_get", lambda url, **kw: calls.append(url) or _Page(status))
    preflight.check_http_fetch()
    assert calls == ["https://httpbin.org/html"]
    assert _statuses() == [(expected, "HTTP fetch (httpbin)")]


@pytest.mark.parametrize("error", [OSError("연결 거부"), TimeoutError()])
def test_http_check_exception_is_warn(monkeypatch, error):
    calls = []

    def _raise(url, **kw):
        calls.append(url)
        raise error

    monkeypatch.setattr(utils, "plain_get", _raise)
    preflight.check_http_fetch()
    assert calls == ["https://httpbin.org/html"]
    assert _statuses() == [("WARN", "HTTP fetch (httpbin)")]


def test_http_check_sends_no_referer_to_real_server(monkeypatch):
    seen = []

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(dict(self.headers))
            body = b"<html><body><h1>ok</h1></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/html"
        monkeypatch.setattr(preflight, "HTTP_CHECK_URL", url, raising=False)
        preflight.check_http_fetch()
    finally:
        server.shutdown()
        server.server_close()
    assert len(seen) == 1, f"로컬 서버가 받은 요청 수: {len(seen)}"
    names = {k.lower() for k in seen[0]}
    assert "referer" not in names, seen[0]
    assert _statuses() == [("PASS", "HTTP fetch (httpbin)")]


# ---- GAPS-002: 메시지 없는 예외에도 죽지 않고 원래 판정과 예외 이름을 남긴다 ----
import builtins  # noqa: E402


def _fail_import(monkeypatch, target, error):
    real = builtins.__import__

    def _import(name, *a, **kw):
        if name == target:
            raise error
        return real(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", _import)


def _all(group):
    return [(status, name) for g, status, name in preflight._results if g == group]


def test_import_check_survives_message_less_error(monkeypatch, capsys):
    _fail_import(monkeypatch, "openpyxl", ImportError())
    assert preflight.check_imports() is False
    assert ("FAIL", "import openpyxl") in _statuses()
    assert "import openpyxl — ImportError" in capsys.readouterr().out


def test_fetcher_load_check_survives_message_less_error(monkeypatch, capsys):
    _fail_import(monkeypatch, "scrapling.fetchers", ImportError())
    assert preflight.check_fetchers() is False
    assert _statuses() == [("FAIL", "Fetcher 클래스 로드")]
    assert "Fetcher 클래스 로드 — ImportError" in capsys.readouterr().out


def test_chromium_check_survives_message_less_error(monkeypatch, capsys):
    import playwright.sync_api as sync_api

    def _boom():
        raise RuntimeError()

    monkeypatch.setattr(sync_api, "sync_playwright", _boom)
    assert preflight.check_chromium_launch() is False
    assert _statuses() == [("FAIL", "Playwright Chromium 실행")]
    assert "Playwright Chromium 실행 — RuntimeError" in capsys.readouterr().out


def _agent_browser_raises(monkeypatch):
    monkeypatch.setattr(preflight, "_cmd", lambda name: "/fake/agent-browser")

    def _run(*a, **kw):
        raise OSError()

    monkeypatch.setattr(preflight, "_run", _run)


def test_agent_browser_version_check_survives_message_less_error(monkeypatch, capsys):
    _agent_browser_raises(monkeypatch)
    assert preflight.check_agent_browser() is False
    assert _all("AGENT-BROWSER") == [("FAIL", "agent-browser --version")]
    assert "agent-browser --version — OSError" in capsys.readouterr().out


def test_agent_browser_ready_check_survives_message_less_error(monkeypatch, capsys):
    _agent_browser_raises(monkeypatch)
    preflight.check_agent_browser_ready()
    assert _all("AGENT-BROWSER") == [("WARN", "agent-browser 동작")]
    assert "agent-browser 동작 — OSError" in capsys.readouterr().out


def test_message_keeps_first_line_and_limit(monkeypatch, capsys):
    message = "첫 줄 " + "가" * 200
    _fail_import(monkeypatch, "openpyxl", ImportError(message + "\n둘째 줄"))
    preflight.check_imports()
    out = capsys.readouterr().out
    assert f"  [FAIL] import openpyxl — {message[:80]}\n" in out
    assert "둘째 줄" not in out
