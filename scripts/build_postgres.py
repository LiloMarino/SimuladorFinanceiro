"""Gera os arquivos do Postgres embarcado no executável do Windows.

Uso: `pnpm build:postgres` (o release roda o mesmo comando antes do PyInstaller).
Baixa o zip oficial de binários, confere o hash, extrai só o que o servidor precisa
e roda o `initdb` uma vez: o computador do jogador recebe o banco vazio pronto e
nunca roda o `initdb`.

Saída em `postgres_dist/`, empacotada pelo `SimuladorFinanceiro.spec`:
  postgres.zip      binários mínimos e textos de licença
  cluster.zip       banco vazio inicializado
  postgres.version  versão dos binários (ex.: 18.6)

`--source-zip` aproveita um zip já baixado, que passa pela mesma conferência de hash.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

# Versão e hash fixos: subir a versão é uma mudança deste arquivo, revisada em commit
POSTGRES_VERSION = "18.6"
POSTGRES_ZIP_URL = (
    "https://get.enterprisedb.com/postgresql/"
    f"postgresql-{POSTGRES_VERSION}-1-windows-x64-binaries.zip"
)
POSTGRES_ZIP_SHA256 = "fbe23da234ee31547bf8a36d29dfd81e82b849df2d2b78d2eecb43d360252f8c"

CACHE_DIR = Path(".cache/postgres")

# O initdb se relança com token restrito, sem o grupo Administradores: a pasta de
# trabalho herda a permissão da pasta pai (legível por Usuários), porque o `tempfile`
# só dá acesso a SYSTEM, Administradores e ao proprietário
WORK_DIR = Path(".cache/postgres_work")
OUTPUT_DIR = Path("postgres_dist")

# Executáveis necessários além das DLLs; o resto de `bin` são ferramentas de manutenção
SERVER_EXECUTABLES = {"postgres.exe", "initdb.exe", "pg_ctl.exe"}

# Textos de licença do zip, que acompanham os binários redistribuídos
LICENSE_FILES = ("server_license.txt", "commandlinetools_3rd_party_licenses.txt")

# Localidade embutida no Postgres: independe do Windows de quem gera e de quem joga,
# e o fuso é o do mercado simulado
INITDB_ARGS = (
    "-U",
    "postgres",
    "-A",
    "trust",
    "-E",
    "UTF8",
    "--locale=C",
    "--locale-provider=builtin",
    "--builtin-locale=C.UTF-8",
    "-c",
    "timezone=America/Sao_Paulo",
    "-c",
    "log_timezone=America/Sao_Paulo",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_official_zip(source: Path | None) -> Path:
    """O zip oficial na versão fixada: o informado, o do cache ou o baixado."""
    if source is None:
        source = CACHE_DIR / Path(POSTGRES_ZIP_URL).name
        if not source.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Baixando {POSTGRES_ZIP_URL}")
            urllib.request.urlretrieve(POSTGRES_ZIP_URL, source)
    if sha256_of(source) != POSTGRES_ZIP_SHA256:
        raise SystemExit(
            f"O hash de {source} não é o fixado para o Postgres {POSTGRES_VERSION}."
        )
    return source


def extract_server(official_zip: Path, target: Path) -> None:
    """Extrai para `target` só o servidor e as licenças, na estrutura bin/lib/share."""
    with zipfile.ZipFile(official_zip) as archive:
        for entry in archive.infolist():
            # O primeiro componente é a pasta raiz do zip ("pgsql")
            _, *path = entry.filename.split("/")
            if entry.is_dir() or not path:
                continue
            area, name = path[0], path[-1]
            is_server_file = (
                area == "bin"
                and len(path) == 2
                and (name in SERVER_EXECUTABLES or name.lower().endswith(".dll"))
            )
            if len(path) == 1 and name in LICENSE_FILES:
                destination = target / "licenses" / name
            elif is_server_file or area in ("lib", "share"):
                destination = target.joinpath(*path)
            else:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry) as source, destination.open("wb") as file:
                shutil.copyfileobj(source, file)


def zip_tree(source: Path, destination: Path) -> None:
    """Zip da pasta com as pastas vazias, que o Postgres exige no banco."""
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for directory, _, files in os.walk(source):
            relative = Path(directory).relative_to(source)
            if relative != Path():
                z.write(directory, relative.as_posix())
            for name in files:
                z.write(Path(directory) / name, (relative / name).as_posix())


def run_initdb(server: Path, data: Path) -> None:
    result = subprocess.run(
        [str(server / "bin" / "initdb.exe"), "-D", str(data), *INITDB_ARGS],
        capture_output=True,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        # O código em hexadecimal identifica o travamento quando a saída vem vazia
        # (0xC0000135 é DLL não encontrada, 0xC0000142 é falha ao iniciar)
        code = result.returncode & 0xFFFFFFFF
        raise SystemExit(
            f"initdb falhou (código 0x{code:08X}):\n{result.stdout}\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--source-zip", type=Path, help="zip oficial já baixado")
    args = parser.parse_args()

    official_zip = fetch_official_zip(args.source_zip)
    OUTPUT_DIR.mkdir(exist_ok=True)

    shutil.rmtree(WORK_DIR, ignore_errors=True)
    work = WORK_DIR.resolve()
    try:
        server = work / "server"
        extract_server(official_zip, server)
        run_initdb(server, work / "cluster")
        zip_tree(server, OUTPUT_DIR / "postgres.zip")
        zip_tree(work / "cluster", OUTPUT_DIR / "cluster.zip")
    finally:
        shutil.rmtree(WORK_DIR, ignore_errors=True)

    (OUTPUT_DIR / "postgres.version").write_text(POSTGRES_VERSION, encoding="utf-8")
    for file in sorted(OUTPUT_DIR.iterdir()):
        print(f"{file}: {file.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
