"""scripts/bootstrap.py — 신규 환경 설치 (단계별, 이미 설치된 건 skip)

단계: (1) Python deps → (2) Browser deps(Chromium) → (3) agent-browser → (4) preflight 검증.
각 단계는 이미 충족되면 건너뛴다. 실패하면 '다음에 실행할 정확한 명령'을 보여준다.

가능하면 venv 안의 python으로 실행한다. Windows는 scripts/setup.ps1 이 venv를 만들고
이 스크립트를 venv python으로 호출한다.

사용법:
    python scripts/bootstrap.py                # full(표준): deps + browser + agent-browser + preflight
    python scripts/bootstrap.py --core-only    # agent-browser 제외 (표준 설치는 full)
    python scripts/bootstrap.py --skip-browser # 브라우저가 이미 있는 환경에서 빠른 재검증
    python scripts/bootstrap.py --force        # 이미 있어도 강제 재설치
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

IS_WIN = os.name == "nt"
REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def log(msg=""):
    print(msg, flush=True)


def stage(title):
    log(f"\n=== {title} ===")


def _cmd(name):
    if IS_WIN:
        return shutil.which(name + ".cmd") or shutil.which(name)
    return shutil.which(name)


def run(cmd):
    log("  $ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd)


def _py_disp():
    """디버그 명령에 쓸 보기 좋은 python 경로 (repo 안 venv면 상대경로)."""
    try:
        rel = Path(PY).relative_to(REPO)
        return (".\\" + str(rel)) if IS_WIN else ("./" + str(rel))
    except ValueError:
        return PY


# ---------------- 상태 점검 ----------------
_READY_IMPORTS = ("scrapling.fetchers", "openpyxl", "playwright", "curl_cffi", "patchright", "browserforge", "msgspec")


def py_deps_problems():
    """「준비 안 됨」 사유 목록(GAPS-002). 비어 있으면 준비됨이다.

    import 가 하나라도 실패하면 설치판 대조는 하지 않는다(옛 py_deps_ready 와 같은 판정 순서).
    """
    problems = []
    for mod in _READY_IMPORTS:
        try:
            __import__(mod)
        except Exception as e:
            first = (str(e).splitlines() or [""])[0][:80]
            problems.append(f"import {mod} 실패 — {type(e).__name__}" + (f": {first}" if first else ""))
    if problems:
        return problems
    return requirements_unsatisfied()


def py_deps_ready():
    return not py_deps_problems()


def requirements_unsatisfied():
    """requirements.txt 선언 중 설치판이 제약식에 맞지 않는 것(GAPS-001).

    import 만 보면 scrapling 0.4.15 venv 도 준비됨으로 판정해 `pip install -r` 을 건너뛰었다.
    환경 마커가 이 환경에 해당하지 않는 선언은 건너뛴다. packaging 을 쓸 수 없으면 판정할 수
    없으므로 「맞지 않음」으로 보고 설치를 돌린다.
    """
    import importlib.metadata as md
    try:
        from packaging.requirements import Requirement
    except Exception:
        return ["packaging 없음 — 설치판을 대조할 수 없다"]
    problems = []
    text = (REPO / "requirements.txt").read_text(encoding="utf-8").replace("\\\n", " ")
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        try:
            req = Requirement(line)
        except Exception:
            problems.append(f"해석 실패: {line}")
            continue
        if req.marker is not None and not req.marker.evaluate():
            continue
        try:
            installed = md.version(req.name)
        except md.PackageNotFoundError:
            problems.append(f"{req.name} 미설치")
            continue
        if not req.specifier.contains(installed, prereleases=True):
            problems.append(f"{req.name} {installed} 가 {req.specifier} 에 맞지 않음")
    return problems


def scrapling_exe():
    d = Path(PY).parent
    cand = d / ("scrapling.exe" if IS_WIN else "scrapling")
    if cand.exists():
        return str(cand)
    return _cmd("scrapling")


def browsers_ready():
    # 1) scrapling 센티넬
    try:
        import scrapling
        if (Path(scrapling.__file__).parent / ".scrapling_dependencies_installed").exists():
            return True
    except Exception:
        pass
    # 2) ms-playwright 에 chromium 빌드 존재
    cands = []
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        cands.append(Path(os.environ["PLAYWRIGHT_BROWSERS_PATH"]))
    home = Path(os.path.expanduser("~"))
    cands += [home / "AppData/Local/ms-playwright", home / ".cache/ms-playwright",
              home / "Library/Caches/ms-playwright"]
    for c in cands:
        try:
            if c.exists() and any(x.name.startswith("chromium") for x in c.iterdir()):
                return True
        except Exception:
            pass
    return False


def agent_browser_ready():
    p = _cmd("agent-browser")
    if not p:
        return False
    try:
        return subprocess.run([p, "--version"], capture_output=True, text=True, timeout=30).returncode == 0
    except Exception:
        return False


# ---------------- 단계 ----------------
def do_python_deps(force, verbose_pip):
    stage("1/4 Python deps")
    if force:
        log("  --force: 준비 여부와 관계없이 다시 설치")
    else:
        problems = py_deps_problems()
        if not problems:
            log("  [SKIP] 이미 설치됨 (scrapling[fetchers] 등 import·설치판 제약 확인)")
            return True, None
        for problem in problems:
            log(f"  준비 안 됨: {problem}")
    req = REPO / "requirements.txt"
    debug = f"{_py_disp()} -m pip install -r requirements.txt --progress-bar off -v"
    log("  최초 1회는 수 분 걸릴 수 있음 (scrapling[fetchers]: playwright/patchright/curl_cffi 등 휠 다운로드).")
    log("  진행이 한동안 안 보여도 정상입니다(의존성 해석·대용량 다운로드 중). 상세 로그를 보려면 --verbose-pip.")
    log(f"  지연/실패 시 직접 실행해 진행 확인:  {debug}")
    cmd = [PY, "-m", "pip", "install", "-r", str(req), "--progress-bar", "off"]
    if verbose_pip:
        cmd.append("-v")
    r = run(cmd)
    if r.returncode != 0:
        return False, debug
    return True, None


def do_browser_deps(skip, force):
    stage("2/4 Browser deps (Chromium)")
    if skip:
        log("  [SKIP] --skip-browser")
        return True, None
    if not force and browsers_ready():
        log("  [SKIP] Chromium 이미 있음 (ms-playwright 또는 scrapling 센티넬 감지)")
        return True, None
    log("  최초 1회만 오래 걸림 (Chromium 다운로드 ~150MB). 이미 받은 경우 빠르게 끝남.")
    log("  참고: scrapling install 이 내부적으로 playwright install chromium 을 수행 — 따로 또 안 해도 됨.")
    exe = scrapling_exe()
    if exe:
        r = run([exe, "install"])
        nxt = f'"{exe}" install'
    else:
        # 폴백: scrapling install 이 하는 일과 동일 (python -m scrapling 은 동작 안 하므로 playwright 직접 호출)
        r = run([PY, "-m", "playwright", "install", "chromium"])
        nxt = f"{PY} -m playwright install chromium"
    if r.returncode != 0:
        return False, nxt
    return True, None


def do_agent_browser(core_only, force):
    stage("3/4 agent-browser (표준 정찰 도구)")
    if core_only:
        log("  [SKIP] --core-only (단, 표준 설치는 agent-browser 포함 full)")
        return True, None
    if not force and agent_browser_ready():
        log("  [SKIP] agent-browser 이미 설치됨")
        return True, None
    npm = _cmd("npm")
    npm_fix = "npm.cmd install -g agent-browser" if IS_WIN else "npm install -g agent-browser"
    if not npm:
        return False, npm_fix + "  (먼저 Node.js: https://nodejs.org/)"
    log("  CLI 글로벌 설치 + Chrome 셋업 (최초 1회, Chrome for Testing 다운로드 가능).")
    if run([npm, "install", "-g", "agent-browser"]).returncode != 0:
        return False, npm_fix
    ab = _cmd("agent-browser")
    ab_fix = "agent-browser.cmd install" if IS_WIN else "agent-browser install"
    if not ab:
        return False, ab_fix
    if run([ab, "install"]).returncode != 0:
        return False, ab_fix
    return True, None


def do_workdirs():
    """수집 결과가 쌓일 로컬 작업 디렉터리를 미리 만든다.

    export_excel/progress 가 기록 시점에 makedirs 하므로 기능상 필수는 아니다.
    갓 clone한 트리에서 "결과가 어디로 가는지" 눈에 보이게 하려는 목적.
    output/ 은 통째로 gitignore라 이 폴더는 커밋되지 않는다.
    """
    (REPO / "output").mkdir(exist_ok=True)
    log(f"  [OK] 작업 디렉터리: {REPO / 'output'}")


def do_preflight(core_only):
    stage("4/4 Preflight 검증")
    cmd = [PY, str(REPO / "scripts" / "preflight.py")]
    if core_only:
        cmd.append("--core-only")
    return run(cmd).returncode


def main():
    ap = argparse.ArgumentParser(description="신규 환경 설치 (단계별, skip 지원)")
    ap.add_argument("--core-only", action="store_true", help="agent-browser 제외 (표준은 full)")
    ap.add_argument("--skip-browser", action="store_true", help="브라우저 설치 생략(이미 있는 환경)")
    ap.add_argument("--force", action="store_true", help="이미 있어도 강제 재설치")
    ap.add_argument("--verbose-pip", action="store_true", help="pip 설치 시 상세 로그(-v) — 지연 시 진행 확인용")
    args = ap.parse_args()

    log("=== web-crawler 설치 부트스트랩 ===")
    if sys.prefix == sys.base_prefix:
        log("  [WARN] venv 밖에서 실행 중. Windows는 'scripts\\setup.ps1' 권장(venv 자동 생성).")
    log(f"  python: {PY}")

    do_workdirs()

    results, times, nexts = {}, {}, []
    for key, fn in [
        ("Python deps", lambda: do_python_deps(args.force, args.verbose_pip)),
        ("Browser deps", lambda: do_browser_deps(args.skip_browser, args.force)),
        ("agent-browser", lambda: do_agent_browser(args.core_only, args.force)),
    ]:
        t0 = time.time()
        ok, nxt = fn()
        times[key] = time.time() - t0
        results[key] = ok
        if not ok:
            log(f"  [FAIL] {key}")
            if nxt:
                nexts.append((key, nxt))

    pf = do_preflight(args.core_only)

    stage("설치 요약")
    for key in ["Python deps", "Browser deps", "agent-browser"]:
        log(f"  [{'OK' if results[key] else 'FAIL'}] {key}  ({times[key]:.1f}s)")
    log(f"  preflight exit = {pf}  (0=전체통과 / 1=core통과·agent-browser미완료 / 2=core실패)")

    if nexts:
        log("\n다음에 실행할 명령:")
        for key, nxt in nexts:
            log(f"  - {key}: {nxt}")

    if pf == 0 and all(results.values()):
        log("\n[OK] 설치 완료 — 수집 환경 준비됨.")
        return 0
    if pf == 2 or not results["Python deps"] or not results["Browser deps"]:
        log("\n[FAIL] core 설치 미완료. 위 명령 실행 후 'python scripts/preflight.py' 로 재검증.")
        return 2
    log("\n[INCOMPLETE] core는 준비됐으나 agent-browser 미완료 → 전체 설치 미완료(표준 정찰 도구).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
