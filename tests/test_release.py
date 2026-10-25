"""O título e as notas da release saem da seção da versão no CHANGELOG.md, com ou sem nome."""

from pathlib import Path

import pytest

from scripts import release

NAMED = """# Changelog

## 3.0.0 Governo & Política (25/10/2026)

Resumo da versão.

### Novidades

- Adicionada a eleição

## 2.3.0 (24/10/2026)

### Novidades

- Adicionado o preset
"""


@pytest.fixture
def changelog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "CHANGELOG.md"
    monkeypatch.setattr(release, "CHANGELOG_PATH", path)
    return path


def at_version(monkeypatch: pytest.MonkeyPatch, version: release.Version) -> None:
    monkeypatch.setattr(release, "current_version", lambda: version)


def test_title_carries_the_name_of_the_version(
    changelog: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    changelog.write_text(NAMED, encoding="utf-8")
    at_version(monkeypatch, (3, 0, 0))

    assert release.title() == 0
    assert capsys.readouterr().out.strip() == "v3.0.0 Governo & Política"


def test_title_is_the_bare_number_without_a_name(
    changelog: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    changelog.write_text(NAMED, encoding="utf-8")
    at_version(monkeypatch, (2, 3, 0))

    assert release.title() == 0
    assert capsys.readouterr().out.strip() == "v2.3.0"


def test_notes_of_a_named_version_stop_at_the_next_section(
    changelog: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    changelog.write_text(NAMED, encoding="utf-8")
    at_version(monkeypatch, (3, 0, 0))

    assert release.notes() == 0
    notes = capsys.readouterr().out
    assert notes.startswith("Resumo da versão.")
    assert "Adicionada a eleição" in notes
    assert "Adicionado o preset" not in notes


def test_section_is_found_with_or_without_a_name(
    changelog: Path,
) -> None:
    changelog.write_text(NAMED, encoding="utf-8")

    assert release.has_changelog_section((3, 0, 0))
    assert release.has_changelog_section((2, 3, 0))
    assert not release.has_changelog_section((3, 1, 0))


def test_missing_section_is_reported(
    changelog: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    changelog.write_text(NAMED, encoding="utf-8")
    at_version(monkeypatch, (9, 9, 9))

    assert release.title() == 1
    assert release.notes() == 1


def test_prepending_keeps_one_header_and_a_blank_line_between_sections(
    changelog: Path,
) -> None:
    changelog.write_text(
        "# Changelog\n\nIntro\n\n## 3.0.0 Nome (25/10/2026)\n\n- Novo\n"
        "# Changelog\n\nIntro\n\n## 2.3.0 (24/10/2026)\n\n- Antigo\n",
        encoding="utf-8",
    )

    release.keep_single_header()

    assert changelog.read_text(encoding="utf-8") == (
        "# Changelog\n\nIntro\n\n## 3.0.0 Nome (25/10/2026)\n\n- Novo\n\n"
        "## 2.3.0 (24/10/2026)\n\n- Antigo\n"
    )
