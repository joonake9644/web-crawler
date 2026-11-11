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
