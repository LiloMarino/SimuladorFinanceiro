"""Onde ficam o config.toml, o .env e os logs: no executável, a pasta do usuário."""

import sys
from pathlib import Path

import pytest

from backend.config import paths


def test_source_run_keeps_the_files_in_the_working_directory(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert paths.app_files_dir() == Path()


def test_executable_uses_the_windows_user_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    directory = paths.app_files_dir()

    assert directory == tmp_path / paths.APP_DIR_NAME
    assert directory.is_dir()


def test_executable_uses_application_support_on_macos(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert (
        paths.user_data_dir()
        == tmp_path / "Library" / "Application Support" / paths.APP_DIR_NAME
    )


def test_executable_follows_xdg_on_linux(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert paths.user_data_dir() == tmp_path / paths.APP_DIR_NAME


def test_linux_without_xdg_falls_back_to_dot_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert paths.user_data_dir() == tmp_path / ".config" / paths.APP_DIR_NAME
