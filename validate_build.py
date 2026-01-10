"""
Script de validação do sistema de build.

Verifica se todos os componentes necessários para o build estão presentes
e configurados corretamente.
"""

import sys
from pathlib import Path


def check_file_exists(path: Path, description: str) -> bool:
    """Verifica se um arquivo existe."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (NOT FOUND)")
        return False


def check_command_available(command: str) -> bool:
    """Verifica se um comando está disponível."""
    import shutil

    if shutil.which(command):
        print(f"✓ Comando '{command}' está disponível")
        return True
    else:
        print(f"✗ Comando '{command}' NÃO está disponível")
        return False


def main():
    """Valida a configuração do build."""
    print("=" * 70)
    print(" Validação do Sistema de Build")
    print("=" * 70)
    print()

    all_ok = True
    project_root = Path(__file__).parent

    # Verificar arquivos principais
    print("[1] Verificando arquivos principais...")
    all_ok &= check_file_exists(project_root / "build.py", "Script de build")
    all_ok &= check_file_exists(
        project_root / "SimuladorFinanceiro.spec", "Spec PyInstaller"
    )
    all_ok &= check_file_exists(project_root / "Makefile", "Makefile")
    all_ok &= check_file_exists(project_root / "main.py", "Script principal")
    all_ok &= check_file_exists(project_root / "BUILD.md", "Documentação de build")
    print()

    # Verificar estrutura do frontend
    print("[2] Verificando estrutura do frontend...")
    frontend_dir = project_root / "frontend"
    all_ok &= check_file_exists(frontend_dir / "package.json", "package.json")
    all_ok &= check_file_exists(frontend_dir / "vite.config.ts", "Vite config")
    print()

    # Verificar estrutura do backend
    print("[3] Verificando estrutura do backend...")
    backend_dir = project_root / "backend"
    all_ok &= check_file_exists(backend_dir / "routes" / "__init__.py", "Routes init")
    all_ok &= check_file_exists(
        backend_dir / "routes" / "frontend.py", "Frontend route"
    )
    print()

    # Verificar comandos disponíveis
    print("[4] Verificando comandos disponíveis...")
    all_ok &= check_command_available("python")
    all_ok &= check_command_available("node")
    all_ok &= check_command_available("npm")
    print()

    # Verificar se PyInstaller está instalado
    print("[5] Verificando PyInstaller...")
    try:
        import PyInstaller

        print(f"✓ PyInstaller instalado")
    except ImportError:
        # Tenta verificar via comando
        if check_command_available("pyinstaller"):
            print("✓ PyInstaller disponível via comando")
        else:
            print("✗ PyInstaller NÃO está instalado")
            print("  Execute: pip install pyinstaller")
            all_ok = False
    print()

    # Resultado final
    print("=" * 70)
    if all_ok:
        print(" ✓ VALIDAÇÃO COMPLETA: Sistema pronto para build!")
        print()
        print(" Para compilar o projeto, execute:")
        print("   make build")
        print()
        print(" Ou em etapas:")
        print("   make build-frontend  # Compila o frontend")
        print("   make build-exe       # Gera o executável")
    else:
        print(" ✗ VALIDAÇÃO FALHOU: Alguns componentes estão faltando")
        print()
        print(" Instale as dependências:")
        print("   pip install -r requirements.txt")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
