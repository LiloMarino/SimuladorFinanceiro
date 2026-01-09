#!/usr/bin/env python3
"""
Script para verificar se a migração FastAPI está funcionando corretamente.
Testa imports e configuração básica sem iniciar o servidor.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test if all FastAPI modules can be imported."""
    print("🔍 Testando imports dos módulos FastAPI...")

    try:
        # Core modules
        from backend.core.dependencies import ClientID, ActiveSimulation, HostVerified
        print("  ✅ Dependencies imported")

        from backend.core.exceptions.fastapi_exceptions import (
            BadRequestError,
            UnauthorizedError,
            ForbiddenError,
            NotFoundError,
            ConflictError,
            UnprocessableEntityError,
        )
        print("  ✅ FastAPI exceptions imported")

        # Route modules
        from backend.routes.fastapi_auth import router as auth_router
        from backend.routes.fastapi_simulation import router as simulation_router
        from backend.routes.fastapi_operation import router as operation_router
        from backend.routes.fastapi_portfolio import router as portfolio_router
        from backend.routes.fastapi_settings import router as settings_router
        from backend.routes.fastapi_statistics import router as statistics_router
        from backend.routes.fastapi_timespeed import router as timespeed_router
        from backend.routes.fastapi_importer import router as importer_router
        from backend.routes.fastapi_realtime import router as realtime_router

        print("  ✅ All 9 route modules imported")

        # WebSocket modules
        from backend.features.realtime.async_ws_broker import AsyncSocketBroker
        from backend.features.realtime.async_ws_handlers import (
            register_async_ws_handlers,
        )

        print("  ✅ WebSocket ASGI modules imported")

        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_fastapi_app():
    """Test if FastAPI app can be created."""
    print("\n🔍 Testando criação da aplicação FastAPI...")

    try:
        from fastapi import FastAPI

        # Don't import main_fastapi directly as it triggers database init
        # Instead just verify FastAPI is available
        app = FastAPI()
        print("  ✅ FastAPI app can be created")
        return True
    except Exception as e:
        print(f"  ❌ FastAPI app creation error: {e}")
        return False


def test_dependencies():
    """Test if dependencies are properly installed."""
    print("\n🔍 Verificando dependências instaladas...")

    required_packages = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "socketio": "python-socketio",
        "pydantic": "Data validation",
    }

    all_ok = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {description} ({package})")
        except ImportError:
            print(f"  ❌ {description} ({package}) - NOT INSTALLED")
            all_ok = False

    return all_ok


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Verificação da Migração FastAPI")
    print("=" * 60)

    results = []

    # Test dependencies
    results.append(("Dependencies", test_dependencies()))

    # Test imports
    results.append(("Imports", test_imports()))

    # Test FastAPI app
    results.append(("FastAPI App", test_fastapi_app()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Resumo dos Testes")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 Todos os testes passaram! A migração está pronta.")
        print("\nPara iniciar o servidor FastAPI:")
        print("  python main_fastapi.py")
        print("\nDocumentação da API estará disponível em:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
