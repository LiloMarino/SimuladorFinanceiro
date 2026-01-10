"""
Build script for compiling frontend and preparing for PyInstaller packaging.

This script:
1. Builds the React frontend using npm/pnpm
2. Copies the built files to backend/static and backend/templates
3. Prepares the application for PyInstaller compilation
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Diretórios
PROJECT_ROOT = Path(__file__).parent.resolve()
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
BACKEND_DIR = PROJECT_ROOT / "backend"
BACKEND_STATIC_DIR = BACKEND_DIR / "static"
BACKEND_TEMPLATES_DIR = BACKEND_DIR / "templates"


def run_command(command: list[str], cwd: Path | None = None) -> bool:
    """Executa um comando e retorna True se bem-sucedido."""
    try:
        print(f"[INFO] Executando: {' '.join(command)}")
        result = subprocess.run(
            command, cwd=cwd, check=True, capture_output=False, text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Comando falhou com código {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"[ERRO] Comando não encontrado: {command[0]}")
        return False


def clean_build_dirs() -> None:
    """Remove diretórios de build anteriores."""
    print("[INFO] Limpando diretórios de build anteriores...")
    for directory in [BACKEND_STATIC_DIR, BACKEND_TEMPLATES_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"[INFO] Removido: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Criado: {directory}")


def build_frontend() -> bool:
    """
    Compila o frontend React com Vite.
    
    Tenta usar npm primeiro, se falhar tenta pnpm como fallback.
    Isso permite suporte para projetos que usam qualquer gerenciador.
    """
    print("\n[INFO] === Compilando Frontend ===")

    # Verifica se o diretório do frontend existe
    if not FRONTEND_DIR.exists():
        print(f"[ERRO] Diretório do frontend não encontrado: {FRONTEND_DIR}")
        return False

    # Instala dependências se necessário
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[INFO] Instalando dependências do frontend...")
        if not run_command(["npm", "install"], cwd=FRONTEND_DIR):
            print("[WARN] npm install falhou, tentando com pnpm...")
            if not run_command(["pnpm", "install"], cwd=FRONTEND_DIR):
                print("[ERRO] Falha ao instalar dependências do frontend")
                return False

    # Compila o frontend
    print("[INFO] Compilando frontend com Vite...")
    if not run_command(["npm", "run", "build"], cwd=FRONTEND_DIR):
        print("[WARN] npm run build falhou, tentando com pnpm...")
        if not run_command(["pnpm", "run", "build"], cwd=FRONTEND_DIR):
            print("[ERRO] Falha ao compilar o frontend")
            return False

    # Verifica se o dist foi criado
    if not FRONTEND_DIST_DIR.exists():
        print(f"[ERRO] Diretório dist não foi criado: {FRONTEND_DIST_DIR}")
        return False

    print("[INFO] ✓ Frontend compilado com sucesso!")
    return True


def copy_frontend_to_backend() -> bool:
    """Copia os arquivos do frontend compilado para o backend."""
    print("\n[INFO] === Copiando Frontend para Backend ===")

    # Copia o index.html para templates
    index_html = FRONTEND_DIST_DIR / "index.html"
    if not index_html.exists():
        print(f"[ERRO] index.html não encontrado em: {index_html}")
        return False

    shutil.copy2(index_html, BACKEND_TEMPLATES_DIR / "index.html")
    print(f"[INFO] Copiado index.html para {BACKEND_TEMPLATES_DIR}")

    # Copia todos os assets (js, css, imagens, etc) para static
    for item in FRONTEND_DIST_DIR.iterdir():
        if item.name == "index.html":
            continue  # Já copiamos para templates

        if item.is_dir():
            # Copia diretórios inteiros
            dest = BACKEND_STATIC_DIR / item.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            print(f"[INFO] Copiado diretório {item.name}/ para static/")
        else:
            # Copia arquivos individuais
            shutil.copy2(item, BACKEND_STATIC_DIR / item.name)
            print(f"[INFO] Copiado {item.name} para static/")

    print("[INFO] ✓ Frontend copiado com sucesso!")
    return True


def main() -> int:
    """Função principal do script de build."""
    print("=" * 70)
    print(" Build Script - Simulador Financeiro")
    print("=" * 70)

    # Limpa diretórios de build
    clean_build_dirs()

    # Compila o frontend
    if not build_frontend():
        print("\n[ERRO] ✗ Build do frontend falhou!")
        return 1

    # Copia o frontend para o backend
    if not copy_frontend_to_backend():
        print("\n[ERRO] ✗ Falha ao copiar frontend para backend!")
        return 1

    print("\n" + "=" * 70)
    print(" ✓ Build concluído com sucesso!")
    print("=" * 70)
    print(f"\nArquivos estáticos em: {BACKEND_STATIC_DIR}")
    print(f"Templates em: {BACKEND_TEMPLATES_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
