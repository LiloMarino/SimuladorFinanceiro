"""
Script para copiar o frontend compilado para o backend.
Este script copia os arquivos do frontend/dist para backend/static e backend/templates.
"""

import shutil
from pathlib import Path


def main():
    # Diretórios base
    project_root = Path(__file__).parent.parent
    frontend_dist = project_root / "frontend" / "dist"
    backend_static = project_root / "backend" / "static"
    backend_templates = project_root / "backend" / "templates"

    # Verifica se o frontend foi compilado
    if not frontend_dist.exists():
        print(
            "❌ Erro: frontend/dist não encontrado. Execute 'npm run build' primeiro."
        )
        return 1

    # Limpa os diretórios de destino se existirem
    print("🧹 Limpando diretórios anteriores...")
    if backend_static.exists():
        shutil.rmtree(backend_static)
    if backend_templates.exists():
        shutil.rmtree(backend_templates)

    # Cria os diretórios de destino
    backend_static.mkdir(parents=True, exist_ok=True)
    backend_templates.mkdir(parents=True, exist_ok=True)

    # Copia o index.html para templates
    print("📄 Copiando index.html para backend/templates...")
    index_src = frontend_dist / "index.html"
    if index_src.exists():
        shutil.copy2(index_src, backend_templates / "index.html")
    else:
        print("⚠️  Aviso: index.html não encontrado no dist")

    # Copia os assets (CSS, JS, imagens, etc.)
    print("📦 Copiando assets para backend/static...")
    assets_src = frontend_dist / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, backend_static / "assets")
    else:
        print("⚠️  Aviso: pasta assets não encontrada no dist")

    # Copia outros arquivos estáticos comuns (favicon, manifests, etc.)
    # Lista de extensões permitidas para arquivos estáticos
    allowed_extensions = {
        ".ico",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".txt",
        ".json",
        ".xml",
        ".webmanifest",
    }

    for item in frontend_dist.iterdir():
        if item.is_file() and item.name != "index.html":
            if item.suffix.lower() in allowed_extensions:
                print(f"📋 Copiando {item.name}...")
                shutil.copy2(item, backend_static / item.name)
            else:
                print(f"⏭️  Ignorando {item.name} (extensão não permitida)")

    print("✅ Frontend copiado com sucesso!")
    print(f"   - Templates: {backend_templates}")
    print(f"   - Static: {backend_static}")
    return 0


if __name__ == "__main__":
    exit(main())
