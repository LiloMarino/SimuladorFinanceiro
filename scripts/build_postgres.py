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
import ctypes
import hashlib
import os
import platform
import shutil
import subprocess
import sys
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

# O zip oficial não traz o runtime do Visual C++ que o servidor e o ICU importam. As DLLs
# vêm do wheel `msvc-runtime`, que reempacota sem alteração os arquivos assinados pela
# Microsoft (Visual C++ 2022, versão 14.44), e entram na pasta bin do servidor: o
# Postgres sobe em qualquer Windows, com ou sem o Redistributable instalado
VC_RUNTIME_WHEEL_URL = (
    "https://files.pythonhosted.org/packages/fe/17/"
    "7a1eace5a7c6083bd99db861625c08bb37010dfbe90ed7a0194ae0281689/"
    "msvc_runtime-14.44.35112-cp313-cp313-win_amd64.whl"
)
VC_RUNTIME_WHEEL_SHA256 = (
    "d4f6cf106aaf235f2a90952f9ec7de49e9946323880d051abf9745a6d4bf60bf"
)
VC_RUNTIME_WHEEL_DATA = "msvc_runtime-14.44.35112.data/data/Scripts/"
VC_RUNTIME_WHEEL_LICENSE = "msvc_runtime-14.44.35112.dist-info/licenses/LICENSE"
VC_RUNTIME_DLLS = ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")

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


def fetch_pinned(url: str, sha256: str, source: Path | None = None) -> Path:
    """O arquivo no hash fixado: o informado, o do cache ou o baixado."""
    if source is None:
        source = CACHE_DIR / Path(url).name
        if not source.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Baixando {url}")
            urllib.request.urlretrieve(url, source)
    if sha256_of(source) != sha256:
        raise SystemExit(f"O hash de {source} não é o fixado para {url}.")
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


def bundle_vc_runtime(server: Path) -> None:
    """Copia o runtime do Visual C++ e o texto de licença dele para o servidor."""
    wheel = fetch_pinned(VC_RUNTIME_WHEEL_URL, VC_RUNTIME_WHEEL_SHA256)
    with zipfile.ZipFile(wheel) as archive:
        for name in VC_RUNTIME_DLLS:
            (server / "bin" / name).write_bytes(
                archive.read(VC_RUNTIME_WHEEL_DATA + name)
            )
        (server / "licenses").mkdir(exist_ok=True)
        (server / "licenses" / "vc_runtime_license.txt").write_bytes(
            archive.read(VC_RUNTIME_WHEEL_LICENSE)
        )


def zip_tree(source: Path, destination: Path) -> None:
    """Zip da pasta com as pastas vazias, que o Postgres exige no banco."""
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for directory, _, files in os.walk(source):
            relative = Path(directory).relative_to(source)
            if relative != Path():
                z.write(directory, relative.as_posix())
            for name in files:
                z.write(Path(directory) / name, (relative / name).as_posix())


def unloadable_modules(server: Path) -> list[str]:
    """Os binários de `bin` que o Windows não consegue carregar, com o erro de cada um."""
    if sys.platform != "win32":
        return []
    free_library = ctypes.WinDLL("kernel32").FreeLibrary
    free_library.argtypes = [ctypes.c_void_p]
    failures = []
    for module in sorted((server / "bin").iterdir()):
        if module.suffix.lower() not in (".dll", ".exe"):
            continue
        try:
            loaded = ctypes.WinDLL(str(module))
        except OSError as error:
            failures.append(f"{module.name}: {error}")
        else:
            # O módulo carregado trava o arquivo e a limpeza da pasta temporária
            free_library(loaded._handle)
    return failures


def folder_permissions(folder: Path) -> str:
    result = subprocess.run(
        ["icacls", str(folder)], capture_output=True, text=True, errors="replace"
    )
    return result.stdout or result.stderr


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
        broken = "\n".join(unloadable_modules(server)) or "nenhum"
        raise SystemExit(
            f"initdb falhou (código 0x{code:08X}) no {platform.platform()}:\n"
            f"{result.stdout}\n{result.stderr}\n"
            f"Binários que não carregam:\n{broken}\n"
            f"Permissões da pasta do servidor:\n{folder_permissions(server)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--source-zip", type=Path, help="zip oficial já baixado")
    args = parser.parse_args()

    official_zip = fetch_pinned(POSTGRES_ZIP_URL, POSTGRES_ZIP_SHA256, args.source_zip)
    OUTPUT_DIR.mkdir(exist_ok=True)

    shutil.rmtree(WORK_DIR, ignore_errors=True)
    work = WORK_DIR.resolve()
    try:
        server = work / "server"
        extract_server(official_zip, server)
        bundle_vc_runtime(server)
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
