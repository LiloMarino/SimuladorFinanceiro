"""Prepara a próxima versão a partir dos commits.

`pnpm release` calcula o número com o `git-cliff`, grava no `pyproject.toml`, no
`uv.lock` e no `docs/openapi.json` e acrescenta a seção da versão ao `CHANGELOG.md`. Nada é commitado:
o diff é revisado e vai num `chore: Versão X`.

Com `--message-file PATH` a versão ganha nome e resumo: a 1ª linha do arquivo entra
no título da seção do changelog e as demais viram o parágrafo que a abre.

Com `--check` (usado pelo workflow de release) só confere que a versão do
`pyproject.toml` não ficou abaixo da calculada dos commits; com `--notes` imprime
a seção da versão atual do `CHANGELOG.md`, que vira a descrição da release; com
`--title` imprime o título da release: `v3.0.0 Nome` ou só `v3.0.0` sem nome.
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


def heading_pattern(version: Version) -> str:
    """O título da seção da versão: `## 3.0.0 (data)`, com um nome opcional antes da data."""
    number = re.escape(format_version(version))
    return rf"^## {number}(?: (?P<name>.+?))? \(\d{{2}}/\d{{2}}/\d{{4}}\)$"


def has_changelog_section(version: Version) -> bool:
    if not CHANGELOG_PATH.exists():
        return False
    return (
        re.search(
            heading_pattern(version),
            CHANGELOG_PATH.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        is not None
    )


def keep_single_header() -> None:
    """O `--prepend` do git-cliff repete o cabeçalho a cada versão; o arquivo guarda um só, no topo."""
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    first = text.index("## ")
    repeated = re.compile(r"^# Changelog\n.*?(?=^## )", re.MULTILINE | re.DOTALL)
    merged = text[:first] + repeated.sub("\n", text[first:])
    # Uma linha em branco separa cada seção da anterior
    CHANGELOG_PATH.write_text(
        re.sub(r"(?<=[^\n])\n(?=## )", "\n\n", merged), encoding="utf-8", newline=""
    )


def notes() -> int:
    """Imprime a seção da versão atual do CHANGELOG.md, sem o título, para a descrição da release."""
    version = current_version()
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    match = re.search(
        heading_pattern(version) + r"\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        print(
            f"O CHANGELOG.md não tem a seção da versão {format_version(version)}.",
            file=sys.stderr,
        )
        return 1
    print(match.group("body").strip())
    return 0


def title() -> int:
    """Imprime o título da release: `v3.0.0 Nome`, ou só `v3.0.0` quando a versão não tem nome."""
    version = current_version()
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    match = re.search(heading_pattern(version), text, re.MULTILINE)
    if match is None:
        print(
            f"O CHANGELOG.md não tem a seção da versão {format_version(version)}.",
            file=sys.stderr,
        )
        return 1
    name = match.group("name")
    number = f"v{format_version(version)}"
    print(f"{number} {name}" if name else number)
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


def prepare(message_file: Path | None) -> int:
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
        # O OpenAPI lê a versão do pyproject.toml já gravado
        run(sys.executable, "-m", "scripts.openapi")

    if not has_changelog_section(version):
        message = (
            ["--with-tag-message", message_file.read_text(encoding="utf-8").strip()]
            if message_file is not None
            else []
        )
        run(
            "git-cliff",
            "--unreleased",
            "--tag",
            f"v{format_version(version)}",
            *message,
            "--prepend",
            str(CHANGELOG_PATH),
        )
        keep_single_header()

    print(f"Versão {format_version(version)} preparada.")
    print("Revise o diff e commite: `chore: Versão " + format_version(version) + "`.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        sys.exit(check())
    if "--notes" in args:
        sys.exit(notes())
    if "--title" in args:
        sys.exit(title())
    message_path = (
        Path(args[args.index("--message-file") + 1])
        if "--message-file" in args
        else None
    )
    sys.exit(prepare(message_path))
