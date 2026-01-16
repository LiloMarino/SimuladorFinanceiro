# Build do Simulador Financeiro

Este documento descreve como compilar o Simulador Financeiro em um executável único usando PyInstaller.

## Pré-requisitos

- Python 3.12+
- Node.js e npm (para compilar o frontend)
- Dependências Python instaladas: `pip install -r requirements.txt`
- Make (Linux/Mac) ou alternativa para Windows (ver seção de compatibilidade)

## Compatibilidade de Plataforma

Este sistema de build foi projetado principalmente para **Linux/Mac**. 

### Windows

Para usuários Windows, há duas opções:

1. **Usar WSL (Windows Subsystem for Linux)** - Recomendado
   - Instale o WSL2 e uma distribuição Linux (Ubuntu recomendado)
   - Execute todos os comandos dentro do WSL

2. **Executar comandos manualmente**:
   ```powershell
   # Compilar frontend
   cd frontend
   npm run build
   cd ..
   
   # Copiar frontend
   python scripts/copy_frontend.py
   
   # Gerar executável
   pyinstaller SimuladorFinanceiro.spec --clean --noconfirm
   ```

## Como Compilar

### 1. Compilação Completa (Recomendado)

Para compilar tudo de uma vez (frontend + backend em um executável):

```bash
make build
```

Este comando irá:
1. Compilar o frontend React/TypeScript com Vite
2. Copiar os arquivos compilados para `backend/static` e `backend/templates`
3. Gerar o executável usando PyInstaller

### 2. Compilação em Etapas

Você também pode executar cada etapa separadamente:

```bash
# Apenas compilar o frontend
make build-frontend

# Apenas gerar o executável (requer frontend já compilado)
make build-exe
```

## Estrutura do Build

Após a compilação:

- `dist/SimuladorFinanceiro.exe` - O executável final (Windows)
- `dist/SimuladorFinanceiro` - O executável final (Linux/Mac)
- `backend/static/` - Arquivos estáticos do frontend (CSS, JS, imagens)
- `backend/templates/` - Template HTML do frontend (index.html)

## Como Executar

Após compilar, simplesmente execute o arquivo gerado:

```bash
# Windows
.\dist\SimuladorFinanceiro.exe

# Linux/Mac
./dist/SimuladorFinanceiro
```

O executável irá:
1. Iniciar o servidor backend FastAPI na porta 8000
2. Servir o frontend automaticamente em http://127.0.0.1:8000
3. Abrir o console mostrando os logs da aplicação

## Limpeza

Para limpar os arquivos de build:

```bash
# Limpar apenas arquivos de build (dist, build, backend/static, backend/templates)
make build-clean

# Limpar apenas artefatos auxiliares (*.prof, *.lprof, etc.)
make clean
```

## Gerando o Arquivo .spec (Avançado)

O arquivo `SimuladorFinanceiro.spec` já está incluído no repositório. Se você precisar regenerá-lo:

```bash
make spec
```

**Nota:** Você só precisa fazer isso uma vez ou quando houver mudanças significativas na estrutura do projeto.

## Troubleshooting

### Frontend não aparece no executável

Certifique-se de que:
1. O frontend foi compilado: `cd frontend && npm run build`
2. Os arquivos foram copiados: `python scripts/copy_frontend.py`
3. As pastas `backend/static` e `backend/templates` existem e contêm os arquivos

### Erro ao executar o .exe

1. Verifique se todas as dependências estão em `requirements.txt`
2. Tente recompilar com `make build-clean && make build`
3. Verifique os logs no console para mais detalhes

### PyInstaller não encontrado

Instale as dependências:
```bash
pip install -r requirements.txt
```

## Notas Técnicas

### Como Funciona

1. **Frontend**: O Vite compila o React/TypeScript em arquivos estáticos otimizados em `frontend/dist`
2. **Copy Script**: `scripts/copy_frontend.py` copia esses arquivos para `backend/static` e `backend/templates`
3. **Backend**: FastAPI serve os arquivos estáticos e o index.html, detectando automaticamente se está rodando no executável ou em modo desenvolvimento
4. **PyInstaller**: Empacota tudo (Python + frontend) em um único executável usando o arquivo `.spec`

### Rotas da Aplicação

Quando compilado:
- `/api/*` - Rotas da API do backend
- `/socket.io/*` - WebSocket para tempo real
- `/assets/*` - Arquivos estáticos (JS, CSS, imagens)
- `/` e qualquer outra rota - Serve o `index.html` para o SPA router funcionar

### Modo Desenvolvimento vs Produção

O código detecta automaticamente se está rodando no executável:

```python
if getattr(sys, "frozen", False):
    # Executável PyInstaller
    base_path = Path(sys._MEIPASS)
else:
    # Desenvolvimento
    base_path = Path(__file__).parent.parent.parent
```

Em desenvolvimento, você pode usar `vite dev` para o frontend com hot-reload, e o proxy configurado no `vite.config.ts` redireciona as chamadas da API para o backend Python.
