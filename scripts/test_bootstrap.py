"""bootstrap 「이미 설치됨」 판정이 설치판까지 보는지 검사(GAPS-001, DEP-001 넘김 갭).

import 만 보면 scrapling 0.4.15 venv 도 준비됨으로 판정해 `pip install -r` 을 건너뛴다.
판 올림(DEP-002) 뒤 기존 venv 가 자동으로 새 하한으로 올라가지 않던 경로가 이것이다.
"""
import importlib.metadata as md
import sys

import bootstrap


def _fake_versions(monkeypatch, overrides):
    real = md.version

    def _version(name):
        key = name.lower().replace("_", "-")
        if key in overrides:
            value = overrides[key]
            if value is None:
                raise md.PackageNotFoundError(name)
            return value
        return real(name)

    monkeypatch.setattr(md, "version", _version)


def test_current_venv_is_ready():
    assert bootstrap.py_deps_ready()


def test_installed_version_below_constraint_is_not_ready(monkeypatch):
    _fake_versions(monkeypatch, {"scrapling": "0.4.15"})
    assert not bootstrap.py_deps_ready()


def test_missing_distribution_is_not_ready(monkeypatch):
    _fake_versions(monkeypatch, {"certifi": None})
    assert not bootstrap.py_deps_ready()


def test_without_packaging_is_not_ready(monkeypatch):
    monkeypatch.setitem(sys.modules, "packaging", None)
    monkeypatch.setitem(sys.modules, "packaging.requirements", None)
    assert not bootstrap.py_deps_ready()


def test_requirement_whose_marker_does_not_apply_is_ignored(monkeypatch, tmp_path):
    (tmp_path / "requirements.txt").write_text(
        "scrapling[fetchers]>=0.5.1,<0.6  # 주석\n"
        "no-such-package-gaps001>=1 ; python_version < '3'\n",
        encoding="utf-8")
    monkeypatch.setattr(bootstrap, "REPO", tmp_path)
    assert bootstrap.py_deps_ready()


# ---- GAPS-002: 다시 설치하기 전에 「준비 안 됨」 사유를 보인다 ----
import builtins  # noqa: E402
import subprocess  # noqa: E402


def _fake_pip(monkeypatch):
    calls = []

    def _run(cmd):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(bootstrap, "run", _run)
    return calls


def test_reason_for_version_mismatch_is_shown(monkeypatch, capsys):
    calls = _fake_pip(monkeypatch)
    _fake_versions(monkeypatch, {"scrapling": "0.4.15"})
    assert bootstrap.do_python_deps(False, False) == (True, None)
    out = capsys.readouterr().out
    assert "준비 안 됨: scrapling 0.4.15 가" in out
    assert len(calls) == 1


def test_reason_for_missing_distribution_is_shown(monkeypatch, capsys):
    calls = _fake_pip(monkeypatch)
    _fake_versions(monkeypatch, {"certifi": None})
    bootstrap.do_python_deps(False, False)
    assert "준비 안 됨: certifi 미설치" in capsys.readouterr().out
    assert len(calls) == 1


def test_reason_for_import_failure_is_shown(monkeypatch, capsys):
    calls = _fake_pip(monkeypatch)
    real = builtins.__import__

    def _import(name, *a, **kw):
        if name == "msgspec":
            raise ImportError("msgspec 없음")
        return real(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", _import)
    bootstrap.do_python_deps(False, False)
    assert "준비 안 됨: import msgspec 실패 — ImportError: msgspec 없음" in capsys.readouterr().out
    assert len(calls) == 1


def test_ready_env_prints_skip_only(monkeypatch, capsys):
    calls = _fake_pip(monkeypatch)
    assert bootstrap.do_python_deps(False, False) == (True, None)
    out = capsys.readouterr().out
    assert "[SKIP] 이미 설치됨" in out
    assert "준비 안 됨" not in out
    assert calls == []


def test_force_says_forced_reinstall(monkeypatch, capsys):
    calls = _fake_pip(monkeypatch)
    bootstrap.do_python_deps(True, False)
    out = capsys.readouterr().out
    assert "--force: 준비 여부와 관계없이 다시 설치" in out
    assert "준비 안 됨" not in out
    assert len(calls) == 1
