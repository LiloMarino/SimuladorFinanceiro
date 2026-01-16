# Resumo da Implementação do Sistema de Build PyInstaller

## O que foi implementado

Build único com PyInstaller que empacota backend (FastAPI) e frontend (React/Vite) em um executável standalone.

## Arquivos Modificados/Criados

### 1. `backend/core/utils/__init__.py` (MODIFICADO)
- Adicionada função `resource_path()` para resolver caminhos em dev e no executável PyInstaller.

### 2. `backend/routes/frontend.py` (NOVO)
- Router dedicado para servir o SPA: monta `/assets`, serve `index.html` em `/` e catch-all (exceto `/api`, `/socket.io`, `/assets`).

### 3. `backend/routes/__init__.py` (MODIFICADO)
- Mantém apenas registro de routers e handlers; delega o frontend para `register_frontend_routes`.

### 4. `frontend/vite.config.ts` (MODIFICADO)
- Build sai direto em `backend/static/` (incluindo `index.html`); sem etapas extras de cópia ou scripts Python.

### 5. `Makefile` (MODIFICADO)
- `build-frontend` usa `pnpm run build` (sem Python) e remove referências a `templates`.
- `build-clean` limpa apenas `backend/static`, `build`, `dist`.

### 6. `SimuladorFinanceiro.spec` (MODIFICADO)
- Empacota apenas `backend/static` como dado adicional (sem `templates`).

### 7. `.gitignore` (MODIFICADO)
- Ignora `backend/static/` (gerado). Removida entrada para `backend/templates/`.

### 8. `docs/BUILD.md` (MODIFICADO)
- Documentação alinhada ao fluxo sem pasta `templates` e sem script de cópia.

## Fluxo de Build

```
make build
    ├─> cd frontend && pnpm run build         # Gera backend/static/ (index.html + assets)
    └─> pyinstaller SimuladorFinanceiro.spec --clean --noconfirm
            └─> Gera dist/SimuladorFinanceiro[.exe] com backend + frontend embutidos
```

## Como o Executável Funciona

1. **Detecção de Ambiente** via `resource_path`:
   ```python
   def resource_path(relative: str) -> Path:
       if getattr(sys, "frozen", False):
           return Path(sys._MEIPASS) / relative
       return Path(relative).resolve()
   ```

2. **Servimento de Arquivos**:
   - `/assets/*` → `backend/static/assets/`
   - `/` e `/{qualquer}` (exceto `/api`, `/socket.io`, `/assets`) → `backend/static/index.html`

3. **Inicialização**:
   - Uvicorn em `127.0.0.1:8000`
   - SPA React servido diretamente do executável

## Compatibilidade de Plataforma

- **Linux/Mac**: `make build`
- **Windows**: usar PowerShell/WSL conforme preferência

## Testes Realizados

- ✅ Linting e formatação
- ✅ Build PyInstaller com frontend empacotado

## Uso

```bash
make build            # frontend + exe
make build-frontend   # só frontend (gera backend/static)
make build-exe        # só exe (frontend já gerado)
make build-clean      # limpa backend/static, build, dist
```

## Notas Finais

- Executável standalone; sem dependência de Python para rodar.
- Frontend é apenas arquivos estáticos em `backend/static` (sem pasta templates).
- SPA routing preservado; APIs continuam em `/api/*`.
