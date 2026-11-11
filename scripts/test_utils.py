"""scripts/test_utils.py"""
import json
import os
import time
import pytest
from unittest.mock import patch
from utils import (
    RateLimiter,
    detect_pii,
    load_cookies,
    save_cookies,
    load_auth_token,
    save_auth_token,
    setup_logger,
    validate_url,
    sanitize_filename,
)


def test_rate_limiter_enforces_delay():
    # delay 하한(0.5) 이 있으므로 그 이상 값으로 검증한다 — P2-3
    limiter = RateLimiter(delay=0.5)
    start = time.time()
    limiter.wait()
    limiter.wait()
    elapsed = time.time() - start
    assert elapsed >= 0.5


def test_rate_limiter_backoff_on_429():
    # delay 하한(0.5) 이하 값은 하한으로 올라가므로 하한 이상 값으로 검증한다 — P2-3
    limiter = RateLimiter(delay=0.5)
    limiter.backoff()
    assert limiter.delay == 1.0  # doubled


def test_validate_url_valid():
    assert validate_url("https://example.com/products") is True
    assert validate_url("http://example.com") is True


def test_validate_url_invalid():
    assert validate_url("not-a-url") is False
    assert validate_url("") is False
    assert validate_url("ftp://example.com") is False


def test_sanitize_filename():
    assert sanitize_filename("example.com") == "example_com"
    assert sanitize_filename("a/b:c*d") == "a_b_c_d"


def test_save_and_load_cookies(tmp_path):
    cookies = {"session": "abc123", "token": "xyz"}
    filepath = tmp_path / "cookies.json"
    save_cookies(cookies, str(filepath))
    loaded = load_cookies(str(filepath))
    assert loaded == cookies


def test_load_cookies_expired(tmp_path):
    cookies = {"session": "abc123"}
    filepath = tmp_path / "cookies.json"
    save_cookies(cookies, str(filepath))
    # Simulate 25 hours old
    old_time = time.time() - (25 * 3600)
    os.utime(str(filepath), (old_time, old_time))
    loaded = load_cookies(str(filepath))
    assert loaded is None  # expired (24h policy)


def test_save_and_load_auth_token(tmp_path):
    token = "eyJhbGciOiJIUzI1NiJ9.test_payload.signature"
    filepath = tmp_path / "token.json"
    save_auth_token(token, str(filepath), token_type="bearer")
    loaded = load_auth_token(str(filepath))
    assert loaded == {"type": "bearer", "token": token}


def test_load_auth_token_expired(tmp_path):
    filepath = tmp_path / "token.json"
    save_auth_token("expired_token", str(filepath))
    old_time = time.time() - (25 * 3600)
    os.utime(str(filepath), (old_time, old_time))
    loaded = load_auth_token(str(filepath))
    assert loaded is None


def test_setup_logger():
    logger = setup_logger("test_crawler")
    assert logger.name == "test_crawler"


def test_detect_pii_email():
    from utils import detect_pii
    data = [{"name": "홍길동", "contact": "hong@email.com"}]
    warnings = detect_pii(data)
    assert len(warnings) > 0
    assert "이메일" in warnings[0]


def test_detect_pii_phone():
    from utils import detect_pii
    data = [{"name": "홍길동", "phone": "010-1234-5678"}]
    warnings = detect_pii(data)
    assert len(warnings) > 0


def test_detect_pii_clean():
    from utils import detect_pii
    data = [{"name": "상품A", "price": "10000"}]
    warnings = detect_pii(data)
    assert len(warnings) == 0


# ── S1: 사다리 1·2단 위장 끄기 ──

from utils import PLAIN_KWARGS, plain_get, plain_session


def test_plain_kwargs_has_both_arguments():
    """부분 적용은 악화다 — 두 인자가 항상 함께 있어야 한다."""
    assert PLAIN_KWARGS == {"impersonate": None, "stealthy_headers": False}


def test_plain_get_passes_both_arguments(monkeypatch):
    captured = {}

    class _FakeFetcher:
        @staticmethod
        def get(url, **kw):
            captured["url"] = url
            captured["kw"] = kw
            return "response"

    monkeypatch.setattr("scrapling.fetchers.Fetcher", _FakeFetcher)

    assert plain_get("https://example.com") == "response"
    assert captured["url"] == "https://example.com"
    assert captured["kw"]["impersonate"] is None
    assert captured["kw"]["stealthy_headers"] is False


def test_plain_get_allows_explicit_override(monkeypatch):
    """호출자가 명시적으로 덮을 수는 있다 — 단 둘을 함께 덮어야 한다."""
    captured = {}

    class _FakeFetcher:
        @staticmethod
        def get(url, **kw):
            captured.update(kw)
            return "response"

    monkeypatch.setattr("scrapling.fetchers.Fetcher", _FakeFetcher)

    plain_get("https://example.com", impersonate="chrome", stealthy_headers=True)
    assert captured["impersonate"] == "chrome"
    assert captured["stealthy_headers"] is True


def test_plain_session_passes_both_arguments(monkeypatch):
    captured = {}

    class _FakeSession:
        def __init__(self, **kw):
            captured.update(kw)

    monkeypatch.setattr("scrapling.fetchers.FetcherSession", _FakeSession)

    plain_session()
    assert captured["impersonate"] is None
    assert captured["stealthy_headers"] is False


def test_plain_helpers_do_not_import_scrapling_at_module_level():
    """utils 는 scrapling 을 물지 않는다 — import 는 함수 안에서 lazy 하게.

    AST 의 최상위 노드만 본다. 문자열 검색은 두 방향으로 틀린다 —
    파일 뒤쪽에 덧붙은 코드를 놓치고, 메서드 안의 정당한 lazy import 를 오탐한다.
    """
    import ast
    from pathlib import Path

    import utils

    tree = ast.parse(Path(utils.__file__).read_text(encoding="utf-8"))
    for node in tree.body:              # 최상위만 — 함수/클래스 내부는 보지 않는다
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        offenders = [n for n in names if n.startswith("scrapling")]
        assert not offenders, f"utils 모듈 최상단에서 scrapling 을 import 하고 있습니다: {offenders}"


def test_plain_get_rejects_partial_override():
    """한쪽만 끄거나 켜는 것은 악화다 — 조용히 허용하지 않는다."""
    with pytest.raises(ValueError, match="impersonate"):
        plain_get("https://example.com", stealthy_headers=True)
    with pytest.raises(ValueError, match="stealthy_headers"):
        plain_get("https://example.com", impersonate="chrome")


def test_plain_session_rejects_partial_override():
    with pytest.raises(ValueError, match="stealthy_headers"):
        plain_session(impersonate="chrome")


# ── P2-1: robots.txt ──
from utils import check_robots


def _fake_fetch(body, status=200):
    def _fetch(url, timeout=10):
        return body, status
    return _fetch


def test_robots_allows_when_not_disallowed(monkeypatch):
    monkeypatch.setattr("utils._fetch_robots", _fake_fetch("User-agent: *\nAllow: /"))
    result = check_robots("https://example.com/list")
    assert result["allowed"] is True
    assert result["robots_url"] == "https://example.com/robots.txt"


def test_robots_blocks_disallowed_path(monkeypatch):
    monkeypatch.setattr("utils._fetch_robots",
                        _fake_fetch("User-agent: *\nDisallow: /private"))
    assert check_robots("https://example.com/private/x")["allowed"] is False
    assert check_robots("https://example.com/public/x")["allowed"] is True


def test_robots_blocks_everything(monkeypatch):
    monkeypatch.setattr("utils._fetch_robots", _fake_fetch("User-agent: *\nDisallow: /"))
    assert check_robots("https://example.com/anything")["allowed"] is False


def test_robots_reports_crawl_delay(monkeypatch):
    monkeypatch.setattr("utils._fetch_robots",
                        _fake_fetch("User-agent: *\nCrawl-delay: 5"))
    assert check_robots("https://example.com/")["crawl_delay"] == 5.0


def test_robots_missing_file_allows(monkeypatch):
    """robots.txt 가 404 면 제한이 없는 것으로 본다 (표준 동작)."""
    monkeypatch.setattr("utils._fetch_robots", _fake_fetch("", 404))
    assert check_robots("https://example.com/")["allowed"] is True


def test_robots_network_error_is_reported_not_swallowed(monkeypatch):
    """가져오지 못한 것과 허용된 것은 다르다 — 사용자가 구분할 수 있어야 한다."""
    def _boom(url, timeout=10):
        raise OSError("connection refused")
    monkeypatch.setattr("utils._fetch_robots", _boom)
    result = check_robots("https://example.com/")
    assert result["error"] is not None
    assert result["allowed"] is True     # 차단 근거가 없으므로 막지는 않는다


@pytest.fixture
def robots_server(monkeypatch):
    """robots.txt 를 정해진 상태 코드로 돌려주는 로컬 서버 — `_fetch_robots` 를 가짜로 바꾸지 않는다.

    위 테스트들은 `_fetch_robots` 를 `(본문, 404)` 를 돌려주는 가짜로 바꿔서, 실제 `urlopen` 이
    404 에서 값이 아니라 `HTTPError` 를 던진다는 사실을 한 번도 지나가지 않았다(2026-10-17 실측:
    books.toscrape.com·www.shu.ac.kr 의 404 가 '확인 못 함' 으로 보고됨).
    """
    import threading
    import urllib.request
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    # 프록시 환경변수가 있으면 urlopen 이 로컬 서버 대신 프록시로 간다(2026-10-17 독립 리뷰 [Low]).
    # 전역 opener 를 프록시 없는 것으로 바꿔 두고 monkeypatch 가 원복한다.
    monkeypatch.setattr(urllib.request, "_opener",
                        urllib.request.build_opener(urllib.request.ProxyHandler({})))

    reply = {"status": 200, "body": "", "length_delta": 0}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = reply["body"].encode("utf-8")
            self.send_response(reply["status"])
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body) + reply["length_delta"]))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def serve(status, body="", length_delta=0):
        reply.update(status=status, body=body, length_delta=length_delta)
        return f"http://127.0.0.1:{server.server_address[1]}/list"

    yield serve
    server.shutdown()
    server.server_close()


@pytest.mark.parametrize("status", [404, 410])
def test_robots_real_missing_file_allows_without_error(robots_server, status):
    """파일이 없다(404·410)는 응답은 '제한 없음' 이다 — '확인 못 함' 이 아니다 (RFC 9309 §2.3.1.3)."""
    result = check_robots(robots_server(status, "Not Found"))
    assert result["error"] is None, result["error"]
    assert result["allowed"] is True


@pytest.mark.parametrize("status", [404, 410])
def test_robots_real_missing_file_ignores_broken_error_body(robots_server, status):
    """파일 없음은 상태 코드로 판정한다 — 오류 본문이 잘려도 '확인 못 함' 으로 되돌아가지 않는다
    (2026-10-17 독립 리뷰 [Low]: Content-Length 가 1 크면 IncompleteRead 로 error 가 됐다)."""
    result = check_robots(robots_server(status, "Not Found", length_delta=1))
    assert result["error"] is None, result["error"]
    assert result["allowed"] is True


@pytest.mark.parametrize("status", [301, 302, 401, 403, 500, 503])
def test_robots_real_other_errors_stay_unverified(robots_server, status):
    """403 은 WAF 가 막은 것일 수 있고 5xx 는 서버 장애다 — 허용으로 단정하지 않고 '확인 못 함' 으로 남긴다.

    풀리지 않은 3xx(Location 없음) 도 같다. urlopen 은 이것도 HTTPError 로 던지는데, 4xx 만 보던
    판정이 이를 '제한 없음' 으로 통과시켰다(2026-10-17 독립 리뷰 [Medium], master 에서는 error 였다).
    """
    result = check_robots(robots_server(status, "nope"))
    assert result["error"] is not None
    assert str(status) in result["error"]


def test_robots_real_disallow_is_enforced(robots_server):
    """실제 경로로도 200 본문을 읽어 판정한다 — 로컬 서버가 테스트 대역이 아닌지 확인하는 대조군."""
    result = check_robots(robots_server(200, "User-agent: *\nDisallow: /list"))
    assert result["error"] is None
    assert result["allowed"] is False


# ── P2-2: PII 스키마 감지 ──
def test_pii_detects_author_column_names():
    warnings = detect_pii([{"작성자": "홍길동", "평점": 5}])
    assert any("작성자" in w for w in warnings)


def test_pii_detects_english_author_columns():
    for column in ("author", "writer", "nickname", "user_name", "reviewer"):
        warnings = detect_pii([{column: "someone"}])
        assert warnings, f"컬럼명 '{column}' 을 감지하지 못했습니다"


def test_pii_detects_korean_identity_columns():
    for column in ("이름", "닉네임", "아이디", "회원명"):
        warnings = detect_pii([{column: "값"}])
        assert warnings, f"컬럼명 '{column}' 을 감지하지 못했습니다"


def test_pii_schema_warning_reported_once_per_column():
    """행마다 반복하지 않는다 — 스키마는 데이터셋당 한 번이다."""
    data = [{"작성자": f"user{i}"} for i in range(30)]
    author_warnings = [w for w in detect_pii(data) if "작성자" in w]
    assert len(author_warnings) == 1


def test_pii_ignores_innocent_columns():
    assert detect_pii([{"상품명": "사과", "가격": 1000}]) == []


def test_pii_still_detects_values():
    """기존 값 기반 감지는 그대로 동작한다."""
    assert detect_pii([{"메모": "문의는 a@b.com 으로"}])


# ── P2-2 픽스: 집계·파생 컬럼 오탐 제거 ──
@pytest.mark.parametrize("column", [
    "작성자", "이름", "닉네임", "아이디", "회원명", "구매자",
    "author", "writer", "nickname", "user_name", "reviewer", "member",
])
def test_pii_still_flags_genuine_identity_columns(column):
    """집계 접미사 제외 로직을 넣은 뒤에도 진짜 개인 컬럼은 그대로 잡혀야 한다 — 회귀 방지."""
    warnings = detect_pii([{column: "값"}])
    assert warnings, f"컬럼명 '{column}' 을 감지하지 못했습니다"


@pytest.mark.parametrize("column", [
    "회원수", "구매자수", "작성자수",
    "buyer_count", "author_count", "member_count",
    "customer_satisfaction_score", "profile_view_count", "username_policy",
])
def test_pii_ignores_aggregate_columns(column):
    """어근이 같아도 집계·파생 컬럼은 사람이 아니라 사람에 대한 수치다."""
    warnings = detect_pii([{column: "x"}])
    assert warnings == [], f"집계 컬럼 '{column}' 이 잘못 감지되었습니다: {warnings}"


@pytest.mark.parametrize("column", [
    "상품명", "가격", "제목", "내용", "카테고리", "브랜드", "평점", "등록일",
])
def test_pii_still_ignores_unrelated_columns(column):
    """집계 접미사 제외 로직이 무관한 컬럼에 영향을 주지 않는다."""
    assert detect_pii([{column: "x"}]) == []


def test_pii_flags_team_members_as_group_of_people():
    """`team_members` 는 집계 접미사로 끝나지 않고, 개인(들)을 직접 가리키는 컬럼이다 —
    `member_count` 처럼 사람에 대한 숫자가 아니라 원본 개인정보(이름 목록 등)일 수 있으므로
    계속 감지 대상으로 둔다 (팀장이 이 판단을 명시적으로 요청함 — 어느 쪽이든 근거를 남길 것)."""
    warnings = detect_pii([{"team_members": "Alice, Bob"}])
    assert warnings, "team_members 는 사람 목록을 가리키므로 감지되어야 합니다"


# ── P2-2 픽스 2: 식별번호(`_num`)가 집계로 오인돼 빠지던 문제 ──
@pytest.mark.parametrize("column", [
    "buyer_num", "member_num", "reviewer_num", "user_num", "회원번호", "구매자번호",
])
def test_pii_flags_identifying_number_columns(column):
    """`num` 은 "인원 수" 가 아니라 "그 사람에게 매겨진 식별번호" 로 읽힐 수 있다 —
    `buyer_num`/`회원번호` 는 집계가 아니라 그 자체로 식별자이므로 감지되어야 한다."""
    warnings = detect_pii([{column: "x"}])
    assert warnings, f"식별번호 컬럼 '{column}' 을 감지하지 못했습니다"


@pytest.mark.parametrize("column", [
    "buyer_count", "member_count", "회원수", "구매자수",
])
def test_pii_still_ignores_real_aggregate_columns(column):
    """`_num` 회귀 수정이 진짜 집계 컬럼(`_count`/`수`)까지 다시 걸리게 하면 안 된다."""
    assert detect_pii([{column: "x"}]) == []


# ── P2-2 픽스 2: 사람을 가리키는 역할 명사 추가 (아이디는 이미 있었음) ──
@pytest.mark.parametrize("column", [
    "수신자", "담당자", "인수자", "접수자", "낙찰자",
])
def test_pii_detects_role_noun_columns(column):
    """작성자/구매자 외에도 사람을 직접 가리키는 역할 명사는 감지해야 한다."""
    warnings = detect_pii([{column: "x"}])
    assert warnings, f"역할 명사 컬럼 '{column}' 을 감지하지 못했습니다"


@pytest.mark.parametrize("column", [
    "숫자", "이자", "과자",
])
def test_pii_does_not_flag_unrelated_ja_ending_words(column):
    """'자' 로 끝나는 단어를 일괄로 잡지 않는다 — 리터럴 나열만 허용한다."""
    assert detect_pii([{column: "x"}]) == []


# ── P2-3: 부담 상한 ──
from utils import BudgetExceeded, RateLimiter


def test_delay_floor_is_enforced():
    """0 이나 음수로 사실상 무제한 요청을 내는 것을 막는다."""
    assert RateLimiter(delay=0).delay >= 0.5
    assert RateLimiter(delay=-1).delay >= 0.5


def test_backoff_still_doubles():
    limiter = RateLimiter(delay=1.0)
    limiter.backoff()
    assert limiter.delay == 2.0


def test_backoff_stops_after_consecutive_limit():
    """429 가 계속 오면 상대가 거절하고 있는 것이다 — 무한 백오프는 답이 아니다."""
    limiter = RateLimiter(delay=1.0, max_consecutive_errors=3)
    limiter.backoff()
    limiter.backoff()
    with pytest.raises(BudgetExceeded) as exc:
        limiter.backoff()
    assert "연속" in str(exc.value)


def test_success_resets_consecutive_counter():
    limiter = RateLimiter(delay=1.0, max_consecutive_errors=3)
    limiter.backoff()
    limiter.backoff()
    limiter.reset_errors()
    limiter.backoff()          # 리셋됐으므로 아직 여유가 있다
    assert limiter.delay == 8.0


def test_total_request_cap():
    limiter = RateLimiter(delay=0.5, max_requests=3)
    for _ in range(3):
        limiter.wait()
    with pytest.raises(BudgetExceeded) as exc:
        limiter.wait()
    assert "총 요청" in str(exc.value)


def test_no_cap_by_default():
    limiter = RateLimiter(delay=0.5)
    for _ in range(10):
        limiter.wait()
    assert limiter.request_count == 10


# ── S4: 값 검증 ──
from utils import validate_values

PRICE_SCHEMA = {
    "상품명": {"type": "str", "required": True, "max_empty_ratio": 0.1},
    "가격": {"type": "int", "required": True, "min": 1, "max": 100_000_000},
}


def test_valid_data_passes():
    data = [{"상품명": "사과", "가격": 3900}, {"상품명": "배", "가격": 5000}]
    assert validate_values(data, PRICE_SCHEMA) == []


def test_missing_required_field():
    issues = validate_values([{"상품명": "사과"}], PRICE_SCHEMA)
    assert any("가격" in i for i in issues)


def test_wrong_type():
    issues = validate_values([{"상품명": "사과", "가격": "삼천구백원"}], PRICE_SCHEMA)
    assert any("가격" in i and "타입" in i for i in issues)


def test_out_of_range():
    issues = validate_values([{"상품명": "사과", "가격": 0}], PRICE_SCHEMA)
    assert any("범위" in i for i in issues)


def test_empty_ratio_exceeded():
    data = [{"상품명": "", "가격": 100} for _ in range(9)] + [{"상품명": "사과", "가격": 100}]
    issues = validate_values(data, PRICE_SCHEMA)
    assert any("빈값" in i for i in issues)


def test_duplicate_ratio_flagged():
    """전부 같은 값이면 셀렉터가 엉뚱한 고정 요소를 잡은 것이다."""
    data = [{"상품명": "광고", "가격": 3900} for _ in range(20)]
    issues = validate_values(data, PRICE_SCHEMA)
    assert any("중복" in i for i in issues)


def test_empty_dataset_is_reported():
    assert validate_values([], PRICE_SCHEMA)


# ── S4 fix round 1: ITEM 1 — allow_uniform 면제 ──
UNIFORM_SCHEMA = {
    "카테고리": {"type": "str", "allow_uniform": True, "max_empty_ratio": 0.1},
}


def test_uniform_column_flags_without_opt_out():
    """카테고리처럼 균일해도 되는 필드조차, 면제를 안 걸면 여전히 경고한다 — 기본 동작 확인용."""
    data = [{"카테고리": "과일"} for _ in range(20)]
    issues = validate_values(data, {"카테고리": {"type": "str"}})
    assert any("중복" in i for i in issues)


def test_uniform_column_clean_with_opt_out():
    """allow_uniform=True 면 20건이 전부 같은 카테고리여도 조용하다."""
    data = [{"카테고리": "과일"} for _ in range(20)]
    assert validate_values(data, UNIFORM_SCHEMA) == []


def test_allow_uniform_only_exempts_the_duplicate_check():
    """allow_uniform 은 중복률 검사만 면제한다 — 같은 필드의 다른 검사는 그대로 걸려야 한다."""
    schema = {
        "카테고리": {"type": "str", "required": True, "max_empty_ratio": 0.1,
                    "allow_uniform": True},
    }
    data = [{"카테고리": ""} for _ in range(20)]
    issues = validate_values(data, schema)
    assert any("빈" in i for i in issues)          # 빈값 관련 검사는 여전히 걸린다
    assert not any("중복" in i for i in issues)     # 중복률 검사만 조용하다


# ── S4 fix round 1: ITEM 2 — required 가 빈 문자열도 누락으로 본다 ──
def test_required_flags_all_empty_strings_without_max_empty_ratio():
    """max_empty_ratio 를 안 걸어도, required=True 면 빈 문자열만 있는 필드는 잡혀야 한다."""
    data = [{"상품명": ""} for _ in range(10)]
    schema = {"상품명": {"type": "str", "required": True}}
    issues = validate_values(data, schema)
    assert issues
    assert any("상품명" in i for i in issues)


def test_required_treats_whitespace_only_as_empty():
    data = [{"상품명": "   "} for _ in range(10)]
    schema = {"상품명": {"type": "str", "required": True}}
    issues = validate_values(data, schema)
    assert issues


def test_required_passes_when_genuinely_populated():
    """중복률 검사와 뒤섞이지 않도록 값을 다양하게 둔다 — required 단독 동작만 본다."""
    data = [{"상품명": f"상품{i}"} for i in range(10)]
    schema = {"상품명": {"type": "str", "required": True}}
    assert validate_values(data, schema) == []


def test_required_missing_key_still_flagged():
    """기존 None 기반 케이스(키 자체가 없음)는 그대로 잡힌다 — 회귀 방지."""
    issues = validate_values([{"상품명": "사과"}], PRICE_SCHEMA)
    assert any("가격" in i for i in issues)


# ── 2026-08-21 실사이트 회귀 테스트에서 확인된 두 결함을 고정 ──
#   F1  3단 DynamicFetcher 가 조작된 Referer 를 보낸다 (google_search 기본 ON)
#   F11 전화번호 패턴이 구분자 없는 ID·URL 숫자열을 잡는다

from utils import DYNAMIC_KWARGS, plain_dynamic


# F1 — 사다리 A 는 3단에서도 출처를 지어내지 않는다

def test_dynamic_kwargs_disables_fabricated_referer():
    """google_search 는 Referer: https://www.google.com/ 를 붙인다 — 사다리 A 에서는 끈다.

    1·2단을 평문으로 만든 근거가 '조작된 출처' 였다. 3단도 통지 없이 도는 칸이므로 같은 기준이다.
    """
    assert DYNAMIC_KWARGS["google_search"] is False


# DEP-002 — scrapling 0.5 는 DynamicFetcher(일반 Playwright 백엔드)를 없앴다. 남은 브라우저 백엔드는
# 위장(patchright) StealthyFetcher 뿐이고 그건 이음매 아래 사다리 B 다. 3단은 playwright 를 직접 불러
# 이음매 위에 남긴다.

class _FakeResponse:
    status = 200
    status_text = "OK"

    def all_headers(self):
        return {"content-type": "text/html"}

    class request:
        method = "GET"

        @staticmethod
        def all_headers():
            return {"user-agent": "real-browser"}


class _FakePage:
    def __init__(self, log):
        self.log = log
        self.url = "https://example.com/final"

    def goto(self, url, **kw):
        if self.log.get("fail_goto", 0) > 0:                      # 재시도 시험(GAPS-001)
            self.log["fail_goto"] -= 1
            raise RuntimeError(f"탐색 실패 {self.log['fail_goto']}")
        self.log["goto"] = (url, kw)
        self.log.setdefault("order", []).append("goto")
        return _FakeResponse()

    def on(self, event, handler):
        self.log.setdefault("handlers", []).append(event)

    def wait_for_load_state(self, state, **kw):
        self.log.setdefault("load_states", []).append(state)

    def locator(self, selector):
        log = self.log

        class _First:
            def wait_for(self, **kw):
                log["wait_selector"] = (selector, kw)
                log.setdefault("order", []).append("wait_selector")

        class _Locator:
            first = _First()

        return _Locator()

    def content(self):
        return "<html><body><p class='v'>렌더됨</p></body></html>"


class _FakeContext:
    def __init__(self, log):
        self.log = log

    def new_page(self):
        self.log["page"] = _FakePage(self.log)
        return self.log["page"]

    def cookies(self):
        return [{"name": "sid", "value": "1"}]


class _FakeBrowser:
    def __init__(self, log):
        self.log = log

    def new_context(self, **kw):
        self.log["context_kw"] = kw
        return _FakeContext(self.log)

    def close(self):
        self.log["closed"] = True


def _fake_sync_playwright(log):
    class _Chromium:
        @staticmethod
        def launch(**kw):
            log["launch"] = kw
            log["launches"] = log.get("launches", 0) + 1
            return _FakeBrowser(log)

    class _P:
        chromium = _Chromium()

    class _CM:
        def __enter__(self):
            return _P()

        def __exit__(self, *exc):
            log["exited"] = True
            return False

    return lambda: _CM()


def _forbid_stealth(monkeypatch):
    """3단 시험 동안 위장 백엔드를 모두 막는다 — patchright 모듈 import 와 scrapling 위장 fetcher(GAPS-001)."""
    import sys
    import scrapling.fetchers as sf

    def _boom(*a, **k):
        raise AssertionError("3단이 위장 백엔드(patchright)를 불렀다 — 이음매를 넘었다")
    monkeypatch.setattr("patchright.sync_api.sync_playwright", _boom)
    # scrapling 위장 fetcher 는 첫 접근 때 patchright 를 불러오므로 모듈을 막기 전에 갈아 끼운다.
    monkeypatch.setattr(sf.StealthyFetcher, "fetch", _boom)
    monkeypatch.setattr(sf, "StealthySession", _boom)
    for name in [m for m in sys.modules if m == "patchright" or m.startswith("patchright.")]:
        monkeypatch.setitem(sys.modules, name, None)                # 이미 불린 모듈도 다시 못 쓴다
    monkeypatch.setitem(sys.modules, "patchright", None)


def test_plain_dynamic_uses_plain_playwright_and_returns_scrapling_response(monkeypatch):
    log = {}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    _forbid_stealth(monkeypatch)
    actions = []

    page = plain_dynamic("https://example.com", network_idle=True,
                         page_action=lambda p: (actions.append(p), log["order"].append("action")),
                         wait_selector="p.v")

    assert log["launch"]["headless"] is True
    url, goto_kw = log["goto"]
    assert url == "https://example.com"
    assert goto_kw["wait_until"] == "load"
    assert "networkidle" in log["load_states"]                     # 기다려 보되 실패로 치지 않는다
    assert "referer" not in {k.lower() for k in goto_kw}           # 출처를 지어내지 않는다
    assert log["context_kw"].get("extra_http_headers") in (None, {})  # 위장 헤더 없음
    assert log["wait_selector"] == ("p.v", {"state": "attached", "timeout": 30_000})
    assert actions == [log["page"]]
    assert log["order"] == ["goto", "action", "wait_selector"]     # 옛 3단 순서
    assert log["closed"] is True
    assert page.status == 200
    assert page.url == "https://example.com/final"
    assert page.css("p.v::text").get() == "렌더됨"


def test_plain_dynamic_waits_for_load_without_network_idle(monkeypatch):
    log = {}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    plain_dynamic("https://example.com")
    assert log["goto"][1]["wait_until"] == "load"
    assert "networkidle" not in log.get("load_states", [])


def test_plain_dynamic_refuses_fabricated_referer(monkeypatch):
    """google_search=True 는 Referer: https://www.google.com/ 를 지어내는 손잡이다 — 3단에서는 거부한다."""
    log = {}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    with pytest.raises(ValueError, match="google_search"):
        plain_dynamic("https://example.com", google_search=True)
    assert "launch" not in log                                   # 브라우저를 띄우기 전에 거부


def test_plain_dynamic_rejects_unknown_arguments(monkeypatch):
    """옛 DynamicFetcher 인자(예: solve_cloudflare)를 조용히 버리지 않는다."""
    log = {}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    with pytest.raises(TypeError):
        plain_dynamic("https://example.com", solve_cloudflare=True)
    assert "launch" not in log


# GAPS-001 설계 1 — 1·2단(scrapling 정적 요청)과 옛 3단은 기본 3회 시도한다. 3단만 1회면 후퇴다.

def test_plain_dynamic_retries_until_success(monkeypatch):
    log = {"fail_goto": 2}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    page = plain_dynamic("https://example.com", retry_delay=0)
    assert log["launches"] == 3                                    # 시도마다 새 브라우저
    assert page.status == 200


def test_plain_dynamic_raises_last_error_after_retries(monkeypatch):
    log = {"fail_goto": 10}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    with pytest.raises(RuntimeError, match="탐색 실패 7"):          # 실패를 숨기지 않는다
        plain_dynamic("https://example.com", retry_delay=0)
    assert log["launches"] == 3                                    # 기본 retries=3 = 총 시도 수


def test_plain_dynamic_retries_one_means_single_attempt(monkeypatch):
    log = {"fail_goto": 10}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    with pytest.raises(RuntimeError):
        plain_dynamic("https://example.com", retries=1, retry_delay=0)
    assert log["launches"] == 1


def test_plain_dynamic_waits_retry_delay_between_attempts(monkeypatch):
    log = {"fail_goto": 1}
    slept = []
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    monkeypatch.setattr("utils.time.sleep", slept.append)
    plain_dynamic("https://example.com", retry_delay=2)
    assert slept == [2]


# GAPS-001 설계 5 — 3단 시험의 위장 차단은 patchright 모듈 전체와 scrapling 위장 fetcher 까지 막는다.

def test_forbid_stealth_blocks_patchright_import_and_stealthy_fetchers(monkeypatch):
    import scrapling.fetchers as sf
    _forbid_stealth(monkeypatch)
    with pytest.raises(ImportError):
        import patchright  # noqa: F401
    with pytest.raises(AssertionError, match="위장"):
        sf.StealthyFetcher.fetch("https://example.com")
    with pytest.raises(AssertionError, match="위장"):
        sf.StealthySession()


# GAPS-001 설계 6 — 3단 반환형은 scrapling 비공개 경로의 Response 다. 상류가 옮기면 여기서 먼저 깨진다.

def test_plain_dynamic_returns_private_scrapling_response_class(monkeypatch):
    from scrapling.engines.toolbelt.custom import Response
    log = {}
    monkeypatch.setattr("playwright.sync_api.sync_playwright", _fake_sync_playwright(log))
    page = plain_dynamic("https://example.com")
    assert type(page) is Response
    assert callable(page.css) and callable(page.xpath)


def test_plain_dynamic_renders_local_js_page(tmp_path):
    """실제 Chromium 으로 JS 가 그린 요소를 읽는다(외부 네트워크 없음)."""
    html = tmp_path / "page.html"
    html.write_text(
        "<html><body><div id='root'></div><script>"
        "document.getElementById('root').innerHTML = \"<span class='item'>JS로 그림</span>\";"
        "</script></body></html>", encoding="utf-8")
    page = plain_dynamic(html.as_uri())
    assert page.css("span.item::text").get() == "JS로 그림"


# DEP-002 독립 리뷰(Codex·DeepSeek·Grok 공통) — 옛 3단(scrapling 0.4.15 DynamicFetcher)과 같은 의미를
# 지킨다: networkidle 이 끝나지 않아도 그린 문서를 돌려주고, page_action 뒤에 wait_selector(attached)를
# 기다리며, status·헤더는 마지막 문서 응답에서, 쿠키는 전체 레코드로 돌려준다.

@pytest.fixture
def local_site():
    import http.server
    import threading
    import time as _time

    pages = {
        "/never-idle": (200, [], "<html><body><p class='ok'>그림</p>"
                                 "<script>fetch('/hold')</script></body></html>"),
        "/start": (200, [("X-Page", "start")],
                   "<html><body><a id='go' href='/error'>go</a></body></html>"),
        "/error": (503, [("X-Page", "error")], "<html><body><p>점검 중</p></body></html>"),
        "/cookies": (200, [("Set-Cookie", "sid=root; Path=/"),
                           ("Set-Cookie", "sid=scoped; Path=/scope")],
                     "<html><body><p>쿠키</p></body></html>"),
    }

    class _H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/hold":
                _time.sleep(10)                      # 끝나지 않는 요청(분석·롱폴링 흉내)
                return
            status, headers, body = pages.get(self.path, (404, [], "없음"))
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _H)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_plain_dynamic_returns_rendered_page_when_network_never_idles(local_site):
    page = plain_dynamic(f"{local_site}/never-idle", network_idle=True, timeout=1500)
    assert page.status == 200
    assert page.css("p.ok::text").get() == "그림"


def test_plain_dynamic_runs_page_action_before_wait_selector(tmp_path):
    html = tmp_path / "click.html"
    html.write_text(
        "<html><body><button id='more'>더 보기</button><script>"
        "document.getElementById('more').onclick = () => setTimeout(() => {"
        "  const s = document.createElement('span'); s.className = 'late'; s.textContent = '늦게';"
        "  document.body.appendChild(s); }, 100);"
        "</script></body></html>", encoding="utf-8")
    page = plain_dynamic(html.as_uri(), wait_selector="span.late", timeout=3000,
                         page_action=lambda p: p.click("#more"))
    assert page.css("span.late::text").get() == "늦게"


def test_plain_dynamic_wait_selector_accepts_hidden_element(tmp_path):
    """옛 기본값은 attached 다 — 숨은 요소(예: script#__NEXT_DATA__)도 기다릴 수 있어야 한다."""
    html = tmp_path / "hidden.html"
    html.write_text("<html><body><div id='hidden' style='display:none'>숨김</div></body></html>",
                    encoding="utf-8")
    page = plain_dynamic(html.as_uri(), wait_selector="#hidden", timeout=1500)
    assert page.css("#hidden::text").get() == "숨김"


def test_plain_dynamic_reports_final_document_status(local_site):
    """page_action 이 다른 문서로 옮기면 status·헤더도 그 문서의 것이다 — 503 을 200 으로 보고하지 않는다."""
    def _go(p):
        with p.expect_navigation():
            p.click("#go")

    page = plain_dynamic(f"{local_site}/start", page_action=_go)
    assert page.url.endswith("/error")
    assert page.status == 503
    assert page.headers.get("x-page") == "error"


def test_plain_dynamic_keeps_full_cookie_records_and_set_cookie_header(local_site):
    page = plain_dynamic(f"{local_site}/cookies")
    paths = sorted(c["path"] for c in page.cookies if c["name"] == "sid")
    assert paths == ["/", "/scope"]
    assert "sid=" in (page.headers.get("set-cookie") or "")


# F11 — 전화번호 패턴이 ID·URL 을 잡지 않는다

@pytest.mark.parametrize("value", [
    "https://www.coupang.com/vp/products/8919133357",   # 상품ID 10자리 (30/30 오탐)
    "1000763360",                                       # kurly 상품번호 (23/24 오탐)
    "atchFileId=3af8fa2cf6e043d986f6d764664126ec",      # FSS 16진수 속 9자리 (6/36 오탐)
    "주문번호 20260821000123",                           # 14자리
    "3967600242987725422",                              # instagram pk 19자리
])
def test_phone_pattern_does_not_flag_ids_and_urls(value):
    """실측 오탐 — 세 도메인에서 ID·URL 만으로 경고가 쏟아졌고 실제 PII 는 0건이었다."""
    warnings = detect_pii([{"참조": value}])
    assert not any("전화번호" in w for w in warnings), f"오탐: {value!r} → {warnings}"


@pytest.mark.parametrize("value", [
    "010-1234-5678",
    "010.1234.5678",
    "010 1234 5678",
    "02-123-4567",
    "연락처는 031-888-9999 입니다",
])
def test_phone_pattern_still_flags_real_numbers(value):
    """구분자가 있는 실제 번호는 그대로 잡는다 — 오탐을 줄이려다 놓치면 안 된다."""
    warnings = detect_pii([{"메모": value}])
    assert any("전화번호" in w for w in warnings), f"놓침: {value!r}"


@pytest.mark.parametrize("value", ["01012345678", "01098765432"])
def test_phone_pattern_flags_bare_mobile_number(value):
    """구분자 없는 11자리 휴대폰은 형식이 명확하므로 잡는다."""
    warnings = detect_pii([{"메모": value}])
    assert any("전화번호" in w for w in warnings), f"놓침: {value!r}"


# ── SEC-001: 자가 침투 점검에서 나온 결함 (docs/security/engagement-loop.md) ──
# 공격자 관점: "51번째 행부터 개인정보를 넣으면 경고가 안 뜬다", "쿠키 파일을 같은 기기의
# 다른 계정이 읽는다", "외국 번호·외국인등록번호는 패턴이 없다". 셋 다 내 코드의 결함이다.

def test_pii_value_scan_covers_rows_after_50():
    """SEC-001-F1 — 값 검사가 앞 50행만 보면 51행 이후의 PII 는 경고 없이 엑셀로 나간다."""
    data = [{"메모": f"상품 {i}"} for i in range(200)]
    data[120]["메모"] = "문의 hong@example.com"
    data[199]["메모"] = "연락처 010-1234-5678"
    warnings = detect_pii(data)
    assert any("이메일" in w and "row 121" in w for w in warnings), warnings
    assert any("전화번호" in w and "row 200" in w for w in warnings), warnings


def test_pii_schema_scan_covers_columns_first_seen_after_50():
    """SEC-001-F1 — 스키마도 같다. 51행부터 생기는 '작성자' 컬럼을 놓치면 안 된다."""
    data = [{"상품명": f"p{i}"} for i in range(80)]
    data[79]["작성자"] = "홍길동"
    assert any("작성자" in w for w in detect_pii(data))


def test_pii_value_warnings_are_aggregated_per_field():
    """전수 검사로 바꾸면서 경고가 행마다 쏟아지면 사람은 경고를 무시한다 — 필드당 1줄."""
    data = [{"contact": f"user{i}@example.com"} for i in range(1000)]
    email_warnings = [w for w in detect_pii(data) if "이메일" in w]
    assert len(email_warnings) == 1, email_warnings
    assert "row 1" in email_warnings[0] and "1000" in email_warnings[0]


@pytest.mark.parametrize("value", [
    "+14155552671",            # E.164 붙여 쓰기
    "+1 (415) 555-2671",       # 미국 표기
    "+82 2 123 4567",          # 한국 지역번호(국제 표기) — 기존 패턴이 못 잡음
    "+81-3-1234-5678",         # 일본
    "Tel: +44 7911 123456",    # 영국 휴대폰
])
def test_pii_flags_international_phone_numbers(value):
    """SEC-001-F2 — 외국인 연락처(국제 표기)를 놓치던 구멍."""
    warnings = detect_pii([{"메모": value}])
    assert any("전화번호" in w for w in warnings), f"놓침: {value!r}"


@pytest.mark.parametrize("value", [
    "+14155552671: 평일 상담",          # 번호 바로 뒤 콜론 — `+09:00` 방지 규칙에 걸려 놓쳤다
    "+14155552671\n2026-11-06",        # 줄바꿈 뒤 날짜까지 한 매치로 먹어 15자리를 넘겼다
    "+1 415 555 2671 2026-11-06 접수",  # 같은 줄 뒤 날짜
    "연락처: +44 20 7946 0958:내선 3",  # 번호 뒤 콜론
    "+82 2 123 4567",    # NBSP(&nbsp;) 구분 — 줄바꿈만 빼야지 가로 공백까지 빼면 안 된다
    "+1 (415) 555-2671",      # NBSP + 괄호
    "+82 2 123 4567",    # 좁은 NBSP
    "+82　2　123　4567",    # 전각 공백
])
def test_pii_international_phone_survives_trailing_context(value):
    """SEC001-CLOSE — 독립 리뷰(2026-11-06, Codex) MEDIUM: 번호 뒤 문맥 때문에 경고가 사라졌다."""
    warnings = detect_pii([{"메모": value}])
    assert any("전화번호" in w for w in warnings), f"놓침: {value!r}"


@pytest.mark.parametrize("value", [
    "+3967600242987725422 문의",        # 15자리 초과 ID 뒤 문맥 — 잘라서 앞부분만 번호로 보면 안 된다
    "+12345 67890123456789",           # 짧은 앞부분 + 긴 숫자열
    "+09:00:00",                       # 시간대 오프셋 변형
])
def test_pii_international_phone_trimming_keeps_id_guard(value):
    """뒤 문맥을 잘라 판정하더라도 숫자열 한가운데서 자르면 안 된다(F11 ID 오탐 규율)."""
    warnings = detect_pii([{"참조": value}])
    assert not any("전화번호" in w for w in warnings), f"오탐: {value!r} → {warnings}"


@pytest.mark.parametrize("value", [
    "C++ 17",                          # 숫자가 짧다
    "score +12345",                    # 8자리 미만
    "q=a+14155552671",                 # 앞이 글자 — URL 쿼리 속 숫자
    "+3967600242987725422",            # 15자리 초과 — E.164 범위 밖(ID)
    "2026-10-31T22:00:00+09:00",       # 시간대 오프셋
    "+1.5%",
])
def test_pii_international_phone_does_not_flag_non_numbers(value):
    """국제 번호를 넓히면서 F11(ID·URL 오탐) 규율을 깨면 안 된다."""
    warnings = detect_pii([{"참조": value}])
    assert not any("전화번호" in w for w in warnings), f"오탐: {value!r} → {warnings}"


@pytest.mark.parametrize("value", [
    "900101-1234567",          # 주민등록번호 형식
    "등록번호 850615-5123456",  # 외국인등록번호(성별 자리 5~8)
])
def test_pii_flags_resident_or_alien_registration_numbers(value):
    """SEC-001-F2 — AGENTS.md 는 주민번호를 PII 로 적었는데 값 패턴이 없었다."""
    warnings = detect_pii([{"메모": value}])
    assert any("등록번호" in w for w in warnings), f"놓침: {value!r} → {warnings}"


@pytest.mark.parametrize("value", [
    "20261031-1234567",        # 주문번호(앞 8자리)
    "901301-1234567",          # 13월 — 날짜가 아니다
    "900101-9234567",          # 성별 자리 9
    "900101-12345678",         # 뒤가 8자리
])
def test_pii_registration_number_does_not_flag_lookalikes(value):
    warnings = detect_pii([{"참조": value}])
    assert not any("등록번호" in w for w in warnings), f"오탐: {value!r} → {warnings}"


@pytest.mark.parametrize("column", [
    "passport_no", "passport_number", "여권번호", "외국인등록번호", "alien_reg_no",
    "alien_registration", "주민등록번호", "주민번호", "national_id", "생년월일",
    "date_of_birth", "ssn", "applicant_ssn", "rrn",
])
def test_pii_flags_foreign_identity_document_columns(column):
    """SEC-001-F2 — 여권·외국인등록·주민번호 컬럼. 값 정규식보다 컬럼명이 오탐이 적다."""
    warnings = detect_pii([{column: "x"}])
    assert warnings, f"신분증 컬럼 '{column}' 을 감지하지 못했습니다"


@pytest.mark.parametrize("column", [
    "classname", "lessons", "passport_count", "current_url", "birth_rate",
])
def test_pii_identity_document_hints_do_not_overmatch(column):
    """`ssn`/`rrn` 은 부분 문자열로 보면 classname·lessons 에 걸린다 — 토큰 일치만."""
    assert detect_pii([{column: "x"}]) == [], column


@pytest.mark.skipif(os.name == "nt", reason="POSIX 권한 비트 검사")
def test_save_cookies_file_is_owner_only(tmp_path):
    """SEC-001-F3 — 세션 쿠키는 로그인과 같다. 0644 로 두면 같은 기기의 다른 계정이 읽는다."""
    filepath = tmp_path / "cookies.json"
    save_cookies({"session": "abc"}, str(filepath))
    assert os.stat(filepath).st_mode & 0o077 == 0, oct(os.stat(filepath).st_mode)


@pytest.mark.skipif(os.name == "nt", reason="POSIX 권한 비트 검사")
def test_save_auth_token_file_is_owner_only(tmp_path):
    filepath = tmp_path / "token.json"
    save_auth_token("secret", str(filepath))
    assert os.stat(filepath).st_mode & 0o077 == 0, oct(os.stat(filepath).st_mode)


@pytest.mark.skipif(os.name == "nt", reason="POSIX 권한 비트 검사")
def test_save_cookies_tightens_existing_world_readable_file(tmp_path):
    """이미 0644 로 만들어진 파일을 덮어쓸 때도 권한을 좁힌다 — 생성 모드만으로는 안 된다."""
    filepath = tmp_path / "cookies.json"
    filepath.write_text("{}")
    os.chmod(filepath, 0o644)
    save_cookies({"session": "abc"}, str(filepath))
    assert os.stat(filepath).st_mode & 0o077 == 0
    assert load_cookies(str(filepath)) == {"session": "abc"}


def test_plain_dynamic_documented_arguments_match_signature():
    """문서가 말하는 3단 인자 목록이 실제 시그니처와 같다(GAPS-001) — 인자를 더하고 문서를 잊지 않게."""
    import inspect
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    accepted = {n for n in inspect.signature(plain_dynamic).parameters if n not in ("url", "google_search")}
    crawl = (root / "docs" / "crawl-reference.md").read_text(encoding="utf-8")
    line = next(l for l in crawl.splitlines() if l.startswith("| JS 렌더링 실패"))
    assert set(re.findall(r"`(\w+)`", line.split("받는 인자는", 1)[1])) == accepted
    ref = (root / "scripts" / "scrapling_reference.md").read_text(encoding="utf-8")
    section = ref.split("### 파라미터", 1)[1].split("반환값:", 1)[0]
    listed = set(re.findall(r"^- `(\w+)=", section, re.M)) - {"google_search"}
    assert listed == accepted
