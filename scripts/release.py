"""Prepara a próxima versão a partir dos commits.

`pnpm release` calcula o número com o `git-cliff`, grava no `pyproject.toml` e
no `uv.lock` e acrescenta a seção da versão ao `CHANGELOG.md`. Nada é commitado:
o diff é revisado e vai num `chore: Versão X`.

Com `--check` (usado pelo workflow de release) só confere que a versão do
`pyproject.toml` não ficou abaixo da calculada dos commits; com `--notes` imprime
a seção da versão atual do `CHANGELOG.md`, que vira a descrição da release.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

PYPROJECT_PATH = Path("pyproject.toml")
CHANGELOG_PATH = Path("CHANGELOG.md")

Version = tuple[int, int, int]


def parse_version(text: str) -> Version:
    major, minor, patch = text.removeprefix("v").split(".")
    return int(major), int(minor), int(patch)


def format_version(version: Version) -> str:
    return ".".join(str(part) for part in version)


def run(*command: str) -> str:
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return result.stdout.strip()


def current_version() -> Version:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return parse_version(data["project"]["version"])


def bumped_version() -> Version:
    """A versão que os commits desde a última tag pedem."""
    return parse_version(run("git-cliff", "--bumped-version"))


def last_tag_version() -> Version | None:
    tags = run("git", "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*")
    versions = [parse_version(tag) for tag in tags.splitlines()]
    return max(versions, default=None)


def write_version(version: Version) -> None:
    text = PYPROJECT_PATH.read_text(encoding="utf-8")
    updated = re.sub(
        r'^version = "[^"]+"',
        f'version = "{format_version(version)}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    PYPROJECT_PATH.write_text(updated, encoding="utf-8", newline="")


def has_changelog_section(version: Version) -> bool:
    if not CHANGELOG_PATH.exists():
        return False
    pattern = rf"^## {re.escape(format_version(version))} \("
    return (
        re.search(pattern, CHANGELOG_PATH.read_text(encoding="utf-8"), re.MULTILINE)
        is not None
    )


def notes() -> int:
    """Imprime a seção da versão atual do CHANGELOG.md, sem o título, para a descrição da release."""
    version = format_version(current_version())
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    match = re.search(
        rf"^## {re.escape(version)} \(.*?\)\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        print(f"O CHANGELOG.md não tem a seção da versão {version}.", file=sys.stderr)
        return 1
    print(match.group(1).strip())
    return 0


def check() -> int:
    current, bumped = current_version(), bumped_version()
    print(f"Versão no pyproject.toml: {format_version(current)}")
    print(f"Versão pedida pelos commits: {format_version(bumped)}")
    if current < bumped:
        print(
            "A versão do pyproject.toml está abaixo da que os commits pedem. "
            "Rode `pnpm release`, revise e commite.",
            file=sys.stderr,
        )
        return 1
    return 0


def prepare() -> int:
    if run("git", "status", "--porcelain"):
        print(
            "A árvore de trabalho tem mudanças. Commite ou guarde antes.",
            file=sys.stderr,
        )
        return 1

    current, bumped, last_tag = current_version(), bumped_version(), last_tag_version()
    version = max(current, bumped)
    if version == last_tag:
        print(f"Nada a lançar: nenhum commit novo desde a v{format_version(version)}.")
        return 0

    if version != current:
        write_version(version)
        run("uv", "lock")

    if not has_changelog_section(version):
        run(
            "git-cliff",
            "--unreleased",
            "--tag",
            f"v{format_version(version)}",
            "--prepend",
            str(CHANGELOG_PATH),
        )

    print(f"Versão {format_version(version)} preparada.")
    print("Revise o diff e commite: `chore: Versão " + format_version(version) + "`.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        sys.exit(check())
    if "--notes" in args:
        sys.exit(notes())
    sys.exit(prepare())
