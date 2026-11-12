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
    monkeypatch.setattr(utils, "plain_get", lambda url, **kw: _Page(status))
    preflight.check_http_fetch()
    assert _statuses() == [(expected, "HTTP fetch (httpbin)")]


def test_http_check_exception_is_warn(monkeypatch):
    def _raise(url, **kw):
        raise OSError("연결 거부")

    monkeypatch.setattr(utils, "plain_get", _raise)
    preflight.check_http_fetch()
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
