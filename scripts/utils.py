"""scripts/utils.py — 크롤링 에이전트 공통 유틸리티"""
import json
import logging
import os
import re
import time
from urllib.parse import urlparse


class BudgetExceeded(Exception):
    """수집 부담 상한을 넘었다. 계속 두드리지 말고 멈춘다.

    부담은 접근과 별개 축이고 여기에도 형사 층이 있다(업무방해). 429 가 반복된다는 것은
    상대가 거절하고 있다는 뜻이지 더 기다리면 될 문제가 아니다.
    """


class RateLimiter:
    """요청 간 대기 + 총량·연속실패 상한.

    delay 하한이 있는 이유: 0 을 넣어 사실상 무제한으로 두드리는 것을 막는다.
    """

    MIN_DELAY = 0.5

    def __init__(self, delay: float = 1.0, min_delay: float = MIN_DELAY,
                 max_requests: int | None = None, max_consecutive_errors: int = 3):
        self.min_delay = max(min_delay, 0.0)
        self.delay = max(delay, self.min_delay)
        self.max_requests = max_requests
        self.max_consecutive_errors = max_consecutive_errors
        self.request_count = 0
        self.consecutive_errors = 0
        self._last_request = 0.0

    def wait(self):
        if self.max_requests is not None and self.request_count >= self.max_requests:
            raise BudgetExceeded(
                f"총 요청 상한({self.max_requests}건)에 도달했습니다. "
                "필요한 만큼만 가져오는 것이 부담 축의 핵심입니다 — "
                "정말 더 필요하면 max_requests 를 명시적으로 올리세요"
            )
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()
        self.request_count += 1

    def backoff(self):
        """HTTP 429/503 등에서 대기 2배. 연속 한도를 넘으면 하드 중단."""
        self.consecutive_errors += 1
        if self.consecutive_errors >= self.max_consecutive_errors:
            raise BudgetExceeded(
                f"연속 {self.consecutive_errors}회 rate limit 응답을 받았습니다. "
                "상대가 거절하고 있는 것이지 더 기다리면 될 문제가 아닙니다 — 중단합니다"
            )
        self.delay *= 2

    def reset_errors(self):
        """요청이 성공했을 때 연속 카운터를 리셋한다."""
        self.consecutive_errors = 0


def validate_url(url: str) -> bool:
    """URL이 유효한 http/https 형식인지 확인."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def sanitize_filename(name: str) -> str:
    """파일명에 사용할 수 없는 문자를 _로 치환."""
    return re.sub(r'[^\w\-]', '_', name)


_SECRET_FILE_MODE = 0o600


def _open_secret_file(filepath: str):
    """소유자만 읽고 쓰는 파일로 연다 — 쿠키·토큰은 로그인 그 자체다 (SEC-001-F3).

    기본 `open(..., "w")` 는 umask 를 따라 대개 0644 가 된다. 같은 기기의 다른 계정·
    프로세스가 세션 쿠키를 읽으면 비밀번호 없이 그 사람으로 로그인할 수 있다.
    생성 모드(`os.open` 의 0o600)는 **새 파일**에만 적용되므로, 이미 0644 로 있던 파일을
    덮어쓰는 경로를 위해 쓰기 전에 `chmod` 로 한 번 더 좁힌다. Windows 는 POSIX 권한 비트가
    없어 chmod 가 읽기전용 플래그만 바꾸므로 그쪽은 사용자 프로필 ACL 에 맡긴다.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    fd = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, _SECRET_FILE_MODE)
    if os.name != "nt":
        os.chmod(filepath, _SECRET_FILE_MODE)
    return os.fdopen(fd, "w", encoding="utf-8")


def save_cookies(cookies: dict, filepath: str):
    """쿠키를 JSON 파일로 저장 (권한 0600)."""
    with _open_secret_file(filepath) as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


def load_cookies(filepath: str, max_age_hours: int = 24) -> dict | None:
    """쿠키 파일 로드. 24시간 초과 시 만료로 None 반환."""
    if not os.path.exists(filepath):
        return None
    age_hours = (time.time() - os.path.getmtime(filepath)) / 3600
    if age_hours > max_age_hours:
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_auth_token(token: str, filepath: str, token_type: str = "bearer"):
    """인증 토큰을 JSON 파일로 저장 (권한 0600)."""
    with _open_secret_file(filepath) as f:
        json.dump({"type": token_type, "token": token}, f)


def load_auth_token(filepath: str, max_age_hours: int = 24) -> dict | None:
    """토큰 파일 로드. 24시간 초과 시 만료로 None 반환."""
    if not os.path.exists(filepath):
        return None
    age_hours = (time.time() - os.path.getmtime(filepath)) / 3600
    if age_hours > max_age_hours:
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


_EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# 전화번호 — 구분자가 있는 형태와 없는 형태를 나눠서 본다.
#
# 예전 패턴 `(\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4})` 은 구분자를 전부 선택으로 둬서, 사실상
# "9~12자리 연속 숫자" 를 전화번호로 봤다. 2026-08-21 실측에서 이게 무너졌다:
#   coupang 30/30 (상품URL 안의 상품ID 8919133357), kurly 23/24 (상품번호 1000763360),
#   FSS 6/36 (atchFileId 16진수 속 9자리). 실제 개인정보는 한 건도 없었다.
# 경고가 이 비율로 틀리면 사람은 PII 경고 자체를 무시하게 된다 — 그게 진짜 손해다.
#
# 그래서:
#   1) 구분자(-, ., 공백)가 실제로 있으면 전화번호로 본다. 한국 번호는 거의 이 형태다.
#   2) 구분자가 없으면 **한국 휴대폰 11자리(01X-XXXX-XXXX)** 만 인정한다. 형식이 명확해서
#      ID 와 헷갈릴 여지가 적다.
# 어느 쪽이든 앞뒤가 숫자면 더 긴 숫자열의 일부이므로 제외한다(`(?<!\d)` / `(?!\d)`) —
# 상품ID·주문번호·pk 가 걸리던 경로가 정확히 이것이었다.
_PHONE_PATTERN = re.compile(
    r'(?<!\d)('
    r'\d{2,4}[-.\s]\d{3,4}[-.\s]\d{4}'   # 구분자 있음: 010-1234-5678 / 02.123.4567
    r'|01\d{9}'                          # 구분자 없음: 한국 휴대폰 11자리만
    r')(?!\d)'
)

# 국제 표기 전화번호 (SEC-001-F2) — 외국인 연락처는 `+국가번호` 로 온다. 위 패턴은
# `+82 2 123 4567`(지역번호 1자리)·`+14155552671`(붙여 쓰기)·`+1 (415) 555-2671` 을 놓쳤다.
#
# F11 규율을 그대로 지킨다 — 넓게 잡고 끝내지 않는다:
#   1) 반드시 `+` 로 시작하고, `+` 앞이 글자·숫자가 아니어야 한다(`q=a+1415…` 같은 URL 쿼리 제외).
#   2) 숫자 개수가 E.164 범위(8~15자리)여야 한다 — `_intl_phone_hit` 가 센다.
#      19자리 instagram pk 에 `+` 가 붙어도 15 를 넘으므로 걸리지 않는다.
#   3) 뒤에 숫자·`:` 가 이어지면 제외한다 — `+09:00` 같은 시간대 오프셋.
_INTL_PHONE_PATTERN = re.compile(
    r'(?<![\w+])\+\d{1,3}(?:[-.\s]?\(?\d{1,4}\)?){1,5}(?![\d:])'
)
_E164_MIN_DIGITS, _E164_MAX_DIGITS = 8, 15


def _intl_phone_hit(value: str) -> bool:
    for match in _INTL_PHONE_PATTERN.finditer(value):
        digits = sum(ch.isdigit() for ch in match.group(0))
        if _E164_MIN_DIGITS <= digits <= _E164_MAX_DIGITS:
            return True
    return False


# 주민등록번호·외국인등록번호 (SEC-001-F2) — 두 번호는 같은 13자리 형식이다(뒤 첫 자리가
# 내국인 1~4, 외국인 5~8). AGENTS.md 는 주민번호를 PII 로 적었지만 값 패턴이 없었다.
# 오탐을 줄이려고 **하이픈을 필수**로 두고 앞 6자리가 실제 날짜(월 01~12, 일 01~31)인지,
# 성별 자리가 1~8 인지까지 본다. 하이픈 없는 13자리는 주문번호·ID 와 구분할 수 없어 잡지 않는다
# — 그 경우는 컬럼명 힌트(`주민번호`·`외국인등록`)가 맡는다.
_REGISTRATION_NO_PATTERN = re.compile(
    r'(?<![\d-])\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])-[1-8]\d{6}(?![\d-])'
)

# 개인을 가리키는 컬럼명. 값이 아니라 '스키마' 를 보는 게 이 경우 더 정확하다 —
# "홍길동" 이라는 값만 봐서는 사람 이름인지 상품명인지 알 수 없지만, 컬럼명이 '작성자' 면 확실하다.
#
# `수신자`/`담당자`/`인수자`/`접수자`/`낙찰자` 는 모두 사람을 직접 가리키는 역할 명사라 명시
# 추가했다. `자`로 끝난다고 일괄 규칙을 만들지는 않는다 — `숫자`/`이자`/`과자`도 `자`로 끝나지만
# 사람이 아니다. 리터럴 나열만 허용한다.
#
# `user_num` 은 `userid`/`user_id` 와 같은 문제다 — 그 사람에게 매겨진 식별번호. 다만 바깥
# `_PII_AGGREGATE_SUFFIXES` 에서 `num` 을 뺀 것과 별개로, 애초에 `user` 단독은 힌트에 없어서
# (`user_agent`/`concurrent_users` 같은 무관한 컬럼까지 잡을 위험) `user_num` 을 리터럴로 추가했다.
_PII_COLUMN_HINTS = (
    "작성자", "이름", "성명", "닉네임", "별명", "아이디", "회원", "구매자", "리뷰어",
    "수신자", "담당자", "인수자", "접수자", "낙찰자",
    "author", "writer", "nickname", "username", "user_name", "userid", "user_id", "user_num",
    "reviewer", "member", "buyer", "customer", "profile",
    # SEC-001-F2 — 신분증·외국인 식별 번호. 값 정규식보다 컬럼명이 오탐이 적다.
    "여권", "passport", "외국인등록", "alien_reg", "주민등록", "주민번호",
    "national_id", "생년월일", "date_of_birth", "birthdate",
)

# 부분 문자열로 보면 오탐이 나는 짧은 약어 — `ssn` 은 `classname`·`lessons` 안에 있다.
# 컬럼명을 `_`·`-`·공백·`.` 으로 자른 **토큰이 정확히 같을 때만** 본다. 리터럴만 둔다.
_PII_COLUMN_TOKENS = ("ssn", "rrn", "dob")
_COLUMN_TOKEN_SPLIT = re.compile(r'[_\-\s.]+')

# 집계·파생 컬럼은 사람이 아니라 사람에 대한 '수치' 다.
# `작성자` 는 개인이지만 `작성자수` 는 개인이 아니다 — 어근이 같아도 다른 것이다.
# 이 구분을 안 하면 경고가 `회원수` 같은 데서 울리고, 그러면 진짜 경고까지 함께 무시된다.
#
# `num` 은 여기 없다 — 뺐다. "count of" 로 읽힐 걸 기대하고 넣었지만, 실제 데이터에서
# `buyer_num`/`member_num` 은 "인원 수" 가 아니라 "그 사람에게 매겨진 식별번호"
# (구매자번호/회원번호) 다. 즉 집계가 아니라 그 자체로 식별자 — 오히려 `num` 이 들어간
# 컬럼일수록 더 의심해야 한다. 반대로 한글 쪽 `수` 는 "받는이" 를 뜻하는 `수신자` 처럼
# 사람을 가리키는 데도 쓰이지만, endswith 이므로 `수신자` 는 걸리지 않는다(끝이 '자').
#
# `score`/`rate`/`ratio`/`avg`/`sum`/`policy` 는 남긴다 — `customer_score` 처럼 개인 단위로
# 매겨지더라도, 그 값 자체가 신원을 드러내지 않는 파생 수치(순위·비율·정책 설명)라는 점에서
# `count`/`total`/`cnt` 와 같은 축에 있다. `num`(식별번호)과는 다른 문제다.
_PII_AGGREGATE_SUFFIXES = (
    "수", "count", "cnt", "total", "score", "policy", "rate", "ratio", "avg", "sum", "id_policy",
)


def detect_pii(data: list[dict]) -> list[str]:
    """수집 데이터에서 PII(개인식별정보)를 감지 — 값 패턴과 컬럼명 양쪽을 본다.

    **전 행을 본다** (SEC-001-F1). 예전에는 앞 50행만 봐서, 51행부터 섞인 개인정보는
    경고 없이 엑셀로 나갔다 — 정렬 순서만 바꿔도 피해 가는 검사는 검사가 아니다.
    대신 값 경고는 (종류, 필드)당 한 줄로 모은다: 처음 나온 행과 총 건수. 행마다 한 줄씩
    쏟아지면 사람은 경고 자체를 무시하게 된다(F11 과 같은 이유).
    """
    warnings = []
    if not data:
        return warnings

    rows = [item for item in data if isinstance(item, dict)]

    # 1) 스키마 — 데이터셋당 한 번. 컬럼명이 개인을 가리키는지. 전 행의 컬럼 합집합.
    columns = {key for item in rows for key in item}
    for column in sorted(columns, key=str):
        lowered = str(column).lower()
        # 집계·파생 접미사로 끝나면 사람이 아니라 사람에 대한 수치다 — 건너뛴다.
        # endswith 여야 한다. substring 검사면 '수신자' 처럼 접미사 글자로 '시작'하는
        # 진짜 개인 컬럼까지 잘못 걸러낸다.
        if lowered.endswith(_PII_AGGREGATE_SUFFIXES):
            continue
        tokens = set(_COLUMN_TOKEN_SPLIT.split(lowered))
        if any(hint in lowered for hint in _PII_COLUMN_HINTS) or tokens & set(_PII_COLUMN_TOKENS):
            warnings.append(
                f"개인식별 컬럼 감지: '{column}' — 개인정보보호법은 영리 여부를 묻지 않는다. "
                "수집·보관 근거를 확인하고, 필요 없으면 이 필드를 빼는 것을 권한다"
            )

    # 2) 값 — 전 행에서 이메일·전화(국내·국제)·주민/외국인등록번호 패턴
    checks = (
        ("이메일 패턴 감지", _EMAIL_PATTERN.search),
        ("전화번호 패턴 감지", lambda v: _PHONE_PATTERN.search(v) or _intl_phone_hit(v)),
        ("주민·외국인등록번호 패턴 감지", _REGISTRATION_NO_PATTERN.search),
    )
    hits: dict[tuple[str, str], list[int]] = {}   # (라벨, 필드) → [처음 행, 건수]
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        for field, value in item.items():
            if not isinstance(value, str):
                continue
            for label, found in checks:
                if found(value):
                    slot = hits.setdefault((label, field), [i + 1, 0])
                    slot[1] += 1
    for (label, field), (first_row, count) in hits.items():
        extra = f" 외 {count - 1}건, 총 {count}건" if count > 1 else ""
        warnings.append(f"{label}: 필드 '{field}' (row {first_row}{extra})")

    return warnings


# ── 소프트블록(가짜 200) 탐지 — insane-search R2 4단계 검증 차용 ──
# WAF는 HTTP 200으로 챌린지/빈 셸을 돌려주는 경우가 많다. status 200 = 성공이 아니라
# "검증 시작"이다. 아래 마커/크기/쿠키 센서를 AND로 보고 수집 직전에 걸러낸다.
_SOFTBLOCK_MARKERS = (
    "sec-if-cpt-container",      # Akamai 챌린지 컨테이너
    "access denied",            # Akamai/edgesuite 거부
    "errors.edgesuite.net",
    "reference #",              # Akamai/edgesuite 에러 페이지
    "pardon our interruption",  # PerimeterX
    "captcha-delivery.com",     # DataDome
    "just a moment...",         # Cloudflare 챌린지
    "cf-browser-verification",
    "attention required",       # Cloudflare 1020
    "verifying you are human",
    "enable javascript and cookies to continue",
)


def detect_softblock(text, status: int = 200, cookies: dict | None = None,
                     selector_hit: bool | None = None, min_size: int = 3000) -> dict:
    """가짜 200(소프트블록) 판별. HTTP 200이라도 본문이 WAF 챌린지면 잡아낸다.

    insane-search의 4단계 AND 검증 차용:
      1) 챌린지 마커 부재  2) 응답 크기 정상  3) 쿠키 센서 정상(_abck=...~-1~ 거부)
      4) success selector 매칭(제공 시 strong, 미제공 시 weak)

    반환: {"blocked": bool, "verdict": str, "signals": [..]}
      verdict ∈ strong_ok | weak_ok | challenge | blocked
    selector_hit 단독 미스만으로는 차단 판정하지 않는다(셀렉터 오타/자가치유와 충돌 방지).
    실제 차단 판정은 마커/크기/쿠키 센서 시그널이 있을 때만.
    """
    text = text or ""
    low = text.lower()

    # HTTP 레벨 차단 (즉시 종료)
    if status in (401, 402, 403):
        return {"blocked": True, "verdict": "blocked", "signals": [f"HTTP {status}"]}

    signals = []
    # 1) 챌린지 마커
    for marker in _SOFTBLOCK_MARKERS:
        if marker in low:
            signals.append(f"challenge marker: {marker}")
    # 2) 응답 크기 (지나치게 작으면 챌린지/빈 셸 의심)
    if len(text) < min_size:
        signals.append(f"response too small: {len(text)}B < {min_size}B")
    # 3) 쿠키 센서 — Akamai _abck 가 '...~-1~' 면 아직 미통과(차단) 상태
    if cookies:
        abck = cookies.get("_abck", "")
        if "~-1~" in abck:
            signals.append("akamai _abck sensor unsolved (~-1~)")

    if signals:
        return {"blocked": True, "verdict": "challenge", "signals": signals}

    # 4) 마커/크기/쿠키 정상 → selector 매칭 여부로 strong/weak 구분
    verdict = "strong_ok" if selector_hit else "weak_ok"
    return {"blocked": False, "verdict": verdict, "signals": []}


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """콘솔 출력용 로거 생성."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# ── 사다리 1·2단 — 위장 없는 표준 호출 ────────────────────────────────────
# Scrapling 기본값은 impersonate="chrome" + stealthy_headers=True 라, 아무것도 안 하면
# 1단이 이미 TLS 지문을 위장하고 가짜 Google referer 까지 붙인다(헤더 16개).
# 안티봇이 없는 사이트에는 위장할 이유가 없다. 두 인자를 함께 끄면 헤더가 4개로 떨어진다.
#
# ⚠ 반드시 '둘 다' 꺼야 한다. 하나만 끄면 헤더는 랜덤 브라우저인데 TLS 지문은 평범한 curl 인
#   불일치 상태가 되어 일관된 위장보다 오히려 더 잘 탐지된다. 부분 적용은 개선이 아니라 악화다.
#
# Fetcher.configure() 는 파서 전용이라 이 기본값을 전역으로 못 바꾼다
# (ValueError: Unknown parser argument: "impersonate"). 그래서 래퍼를 쓴다.
PLAIN_KWARGS = {"impersonate": None, "stealthy_headers": False}


def _apply_plain_kwargs(kw: dict) -> dict:
    """두 인자를 함께 적용한다. 한쪽만 덮으려는 호출은 거부한다.

    부분 적용은 개선이 아니라 악화다 — 헤더는 브라우저라고 말하는데 TLS 지문은 그렇지 않은
    불일치 상태가 되어 일관된 위장보다 더 잘 탐지된다. 그래서 '둘 다' 이거나 '둘 다 아니거나' 만 허용한다.
    """
    overridden = [key for key in PLAIN_KWARGS if key in kw]
    if len(overridden) == 1:
        missing = next(key for key in PLAIN_KWARGS if key not in kw)
        raise ValueError(
            f"{overridden[0]} 만 지정했습니다. {missing} 도 함께 지정하세요 — "
            "한쪽만 바꾸면 불일치 지문이 되어 오히려 더 잘 탐지됩니다"
        )
    for key, value in PLAIN_KWARGS.items():
        kw.setdefault(key, value)
    return kw


def plain_get(url: str, **kw):
    """사다리 1단. 위장 없는 평문 HTTP — 안티봇이 없는 사이트에 쓴다."""
    kw = _apply_plain_kwargs(kw)
    from scrapling.fetchers import Fetcher  # lazy — utils 는 scrapling 을 물지 않는다
    return Fetcher.get(url, **kw)


def plain_session(**kw):
    """사다리 2단. 위장 없는 세션 — 숨은 API 를 직접 호출할 때 쓴다."""
    kw = _apply_plain_kwargs(kw)
    from scrapling.fetchers import FetcherSession  # lazy
    return FetcherSession(**kw)


# 3단은 진짜 브라우저라 헤더가 실제 브라우저의 것이다 — 거기까지는 위장이 아니다.
# 다만 Scrapling 은 `google_search` 를 기본으로 켜서 `Referer: https://www.google.com/` 를
# 붙인다. 오지 않은 곳에서 왔다고 말하는 것이라 헤더가 진짜인 것과는 다른 문제다.
# 1·2단을 평문으로 만든 근거가 바로 그 조작된 출처였고, 3단도 통지 없이 도는 사다리 A 다.
# 게다가 이 저장소 문서는 `google_search` 를 4단 curl_cffi 그리드의 우회 손잡이로 적어 뒀다
# (`antibot-strategies.md`) — 같은 손잡이가 A 에서 조용히 켜져 있으면 안 된다.
DYNAMIC_KWARGS = {"google_search": False}


def plain_dynamic(url: str, **kw):
    """사다리 3단. JS 렌더링이 필요할 때 — 출처는 지어내지 않는다.

    `impersonate`/`stealthy_headers` 짝 강제는 여기 없다. 그건 HTTP 계층 인자이고
    3단은 브라우저가 스스로 헤더를 만든다. 여기서 끄는 것은 **조작된 Referer** 하나다.
    """
    for key, value in DYNAMIC_KWARGS.items():
        kw.setdefault(key, value)
    from scrapling.fetchers import DynamicFetcher  # lazy
    return DynamicFetcher.fetch(url, **kw)


# ── robots.txt — 표지판이지 잠금장치가 아니지만, 무시했다는 사실은 정황이 된다 ──
def _fetch_robots(url: str, timeout: int = 10):
    """robots.txt 를 가져와 (본문, status) 반환. 테스트에서 monkeypatch 한다.

    `urlopen` 은 4xx·5xx 와 풀리지 않은 3xx 를 값이 아니라 `HTTPError` 로 던진다. 그대로 두면
    404 가 '가져오지 못함' 으로 새어 나가 check_robots 의 404 분기에 닿지 못한다(2026-10-17 실측).
    판정은 상태 코드로만 하므로 오류 응답의 본문은 읽지 않는다 — 본문이 잘려도 코드는 남는다.
    """
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    req = Request(url, headers={"User-Agent": "web-crawler-agent"})
    try:
        with urlopen(req, timeout=timeout) as resp:      # noqa: S310 (http/https만 들어온다)
            return resp.read().decode("utf-8", errors="replace"), resp.status
    except HTTPError as exc:
        exc.close()
        return "", exc.code


def check_robots(url: str, user_agent: str = "*") -> dict:
    """robots.txt 를 실제로 읽어 이 URL 수집이 허용되는지 판정.

    반환: {"allowed": bool, "crawl_delay": float|None, "robots_url": str, "error": str|None}

    robots.txt 는 법적 구속력이 없지만, 무시했다는 사실은 "알고도 했다" 의 정황이 된다.
    가져오지 못한 것(error)과 허용된 것(allowed)은 다르다 — 호출자가 구분할 수 있게 둘 다 준다.
    """
    from protego import Protego

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    result = {"allowed": True, "crawl_delay": None, "robots_url": robots_url, "error": None}

    try:
        body, status = _fetch_robots(robots_url)
    except Exception as exc:
        result["error"] = f"robots.txt 를 가져오지 못했습니다: {exc}"
        return result

    if status in (404, 410):
        return result       # 파일 없음 → 제한 없음 (RFC 9309 §2.3.1.3)
    if not 200 <= status < 300:
        # 403 은 WAF 가 막은 것일 수 있고 5xx 는 장애, 3xx 는 풀리지 않은 리다이렉트다 — 허용으로 단정하지 않는다
        result["error"] = f"robots.txt 를 가져오지 못했습니다: HTTP {status}"
        return result
    if not body.strip():
        return result       # 제한 없음

    try:
        parser = Protego.parse(body)
    except Exception as exc:
        result["error"] = f"robots.txt 파싱 실패: {exc}"
        return result

    result["allowed"] = parser.can_fetch(url, user_agent)
    delay = parser.crawl_delay(user_agent)
    result["crawl_delay"] = float(delay) if delay is not None else None
    return result


# ── 값 검증 — 자가치유를 쓰는 이상 선택이 아니다 ──
# adaptive=True 는 "못 찾겠다" 고 말하지 않는다. 늘 무언가는 반환한다.
# 지면이 개편돼 그 자리에 광고가 들어가면 광고를 가져와 엑셀에 '가격: 3,900원' 으로 꽂는다.
# 최종 산출물이 사람이 읽는 엑셀이라 조용한 오답은 크래시보다 나쁘다.
_TYPE_MAP = {"str": str, "int": int, "float": (int, float), "any": object}


def validate_values(data: list[dict], schema: dict) -> list[str]:
    """수집 값이 그럴듯한지 검사. 문제 목록을 반환(빈 리스트 = 통과).

    schema: {"필드명": {"type": "str|int|float|any", "required": bool,
                        "min": float|None, "max": float|None,
                        "max_empty_ratio": float,
                        "allow_uniform": bool}}

    allow_uniform=True 인 필드는 전부 같은 값이어도 중복률 경고를 내지 않는다 —
    카테고리·플래그·정액 배송비처럼 균일한 게 정상인 필드에 쓴다. 이 필드도 타입/범위/
    필수/빈값 검사는 그대로 받는다 — 면제되는 건 중복률 검사 하나뿐이다.
    """
    issues = []
    if not data:
        return ["수집 데이터가 0건입니다 — 계속 시도하지 말고 원인을 확인하세요"]

    total = len(data)
    for field, rule in schema.items():
        expected = _TYPE_MAP.get(rule.get("type", "any"), object)
        values = [row.get(field) for row in data if isinstance(row, dict)]

        if rule.get("required"):
            # "필수" 는 값이 실제로 있어야 한다는 뜻이다 — 빈 문자열은 값이 아니다.
            # 키가 아예 없는 경우(누락)와 셀렉터는 맞았는데 텍스트를 못 가져온 경우(빈 문자열)는
            # 원인이 다르므로 메시지를 나눠 알린다.
            absent = sum(1 for v in values if v is None)
            empty_str = sum(1 for v in values if isinstance(v, str) and not v.strip())
            if absent:
                issues.append(f"필수 필드 '{field}' 가 {absent}/{total}건에서 누락됐습니다")
            if empty_str:
                issues.append(
                    f"필수 필드 '{field}' 가 {empty_str}/{total}건에서 빈 문자열입니다 — "
                    "값은 있으나 비어 있습니다(셀렉터는 매칭됐지만 텍스트를 못 가져왔을 수 있습니다)"
                )

        for i, value in enumerate(values):
            if value is None:
                continue
            if expected is not object and not isinstance(value, expected):
                issues.append(
                    f"필드 '{field}' 타입 불일치 (row {i+1}): "
                    f"{rule.get('type')} 를 기대했으나 {type(value).__name__}"
                )
                break       # 타입 문제는 한 번만 보고 — 전부 같은 원인이다

        numeric = [v for v in values if isinstance(v, (int, float))]
        low, high = rule.get("min"), rule.get("max")
        if numeric and (low is not None or high is not None):
            bad = [v for v in numeric
                   if (low is not None and v < low) or (high is not None and v > high)]
            if bad:
                issues.append(
                    f"필드 '{field}' 범위 이탈 {len(bad)}건 (예: {bad[0]}) — "
                    f"허용 {low}~{high}"
                )

        empty = sum(1 for v in values if v is None or (isinstance(v, str) and not v.strip()))
        limit = rule.get("max_empty_ratio")
        if limit is not None and total and empty / total > limit:
            issues.append(
                f"필드 '{field}' 빈값 비율 {empty}/{total} ({empty/total:.0%}) 가 "
                f"상한 {limit:.0%} 를 넘었습니다 — 셀렉터가 어긋났을 수 있습니다"
            )

        # 균일한 것이 정상인 필드도 있다 — 카테고리, 플래그, 정액 배송비.
        # 그런 필드까지 경고하면 이 검사가 노이즈가 되고, 정작 셀렉터가 광고에 붙은 날
        # 아무도 읽지 않는다. 스키마 작성자가 명시적으로 면제할 수 있게 한다.
        if rule.get("allow_uniform"):
            continue        # 중복률 검사만 건너뛴다 — 나머지 검사는 이미 위에서 적용됐다

        filled = [v for v in values if v not in (None, "")]
        if len(filled) >= 10 and len(set(map(str, filled))) == 1:
            issues.append(
                f"필드 '{field}' 중복률 100% — {len(filled)}건이 전부 동일한 값입니다. "
                "셀렉터가 고정 요소(광고·머리글)를 잡았을 수 있습니다"
            )

    return issues
