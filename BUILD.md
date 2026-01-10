# 🔨 Guia de Build do Simulador Financeiro

Este documento descreve como compilar o projeto e gerar um executável standalone.

## 📋 Pré-requisitos

### Software Necessário

1. **Python 3.12+** com pip
2. **Node.js 20+** com npm
3. **Make** (incluído no Git Bash no Windows)

### Instalar Dependências

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Instalar dependências do frontend (opcional, build.py faz automaticamente)
cd frontend
npm install
cd ..
```

## 🚀 Build Completo (Recomendado)

Para compilar tanto o frontend quanto gerar o executável em um único comando:

```bash
make build
```

Este comando executa:
1. `python build.py` - Compila o frontend React e copia para backend/static
2. `pyinstaller SimuladorFinanceiro.spec` - Gera o executável

## 📦 Build por Etapas

### 1. Compilar Frontend

Para compilar apenas o frontend React:

```bash
make build-frontend
```

Ou diretamente:

```bash
python build.py
```

Isso irá:
- Instalar dependências do frontend (se necessário)
- Compilar o React app com Vite
- Copiar os arquivos compilados para:
  - `backend/static/` - Arquivos estáticos (JS, CSS, imagens)
  - `backend/templates/` - index.html

### 2. Gerar Executável

Para gerar apenas o executável (após compilar o frontend):

```bash
make build-exe
```

Ou diretamente:

```bash
pyinstaller SimuladorFinanceiro.spec --clean --noconfirm
```

## 📂 Arquivos Gerados

Após o build completo, você encontrará:

```
dist/
└── SimuladorFinanceiro/
    ├── SimuladorFinanceiro.exe  ← EXECUTÁVEL PRINCIPAL
    ├── _internal/               ← Dependências e bibliotecas
    │   ├── backend/
    │   │   ├── static/         ← Frontend compilado
    │   │   └── templates/
    │   └── ...
    └── ...
```

## ▶️ Executar o Aplicativo

### Modo Desenvolvimento (sem build)

```bash
# Terminal 1: Rodar backend
python main.py

# Terminal 2: Rodar frontend (em outra janela)
cd frontend
npm run dev
```

### Modo Produção (executável)

1. Navegue até `dist/SimuladorFinanceiro/`
2. Execute `SimuladorFinanceiro.exe`
3. O aplicativo iniciará o backend e abrirá automaticamente
4. Acesse no navegador: http://localhost:5000

## 🧹 Limpar Build

Para remover todos os arquivos de build:

```bash
make build-clean
```

Isso remove:
- `backend/static/`
- `backend/templates/`
- `build/`
- `dist/`

## 🛠️ Configuração Avançada

### Modificar o Build

#### Configurar PyInstaller

Edite `SimuladorFinanceiro.spec` para:
- Adicionar/remover arquivos incluídos
- Modificar ícone do executável
- Ajustar imports ocultos
- Configurar modo console/windowed

#### Configurar Build do Frontend

Edite `build.py` para:
- Mudar comandos de build
- Adicionar etapas de pós-processamento
- Customizar cópia de arquivos

### Troubleshooting

#### Erro: "Frontend dist não encontrado"
- Certifique-se de que Node.js e npm estão instalados
- Execute `npm install` no diretório `frontend/`

#### Erro: "PyInstaller não encontrado"
- Execute `pip install pyinstaller`

#### Executável não inicia
- Verifique se todos os arquivos em `dist/SimuladorFinanceiro/` estão presentes
- Execute em modo console para ver erros: edite `.spec` e defina `console=True`

#### Arquivos estáticos não carregam
- Verifique se `backend/static/` e `backend/templates/` existem
- Execute `make build-frontend` novamente

## 📝 Notas Importantes

1. **Sempre compile o frontend antes de gerar o executável**
   - O PyInstaller empacota o que está em `backend/static/` e `backend/templates/`
   
2. **Arquivos de configuração**
   - `secret.key`, `config.toml`, e `db.sqlite3` são gerados em runtime
   - Não são incluídos no executável

3. **Banco de dados**
   - O executável usa SQLite por padrão
   - Configure via `config.toml` para usar PostgreSQL

4. **Distribuição**
   - Distribua a pasta `dist/SimuladorFinanceiro/` completa
   - Não distribua apenas o `.exe`, pois ele depende dos arquivos em `_internal/`

## 🎯 Exemplo de Workflow Completo

```bash
# 1. Clonar o repositório
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Build completo
make build

# 4. Executar
cd dist/SimuladorFinanceiro
./SimuladorFinanceiro.exe
```

## 📊 Estrutura de Diretórios Após Build

```
SimuladorFinanceiro/
├── frontend/
│   ├── dist/              ← Saída temporária do Vite
│   └── ...
├── backend/
│   ├── static/            ← Gerado pelo build.py (gitignored)
│   ├── templates/         ← Gerado pelo build.py (gitignored)
│   └── ...
├── dist/
│   └── SimuladorFinanceiro/  ← Executável e dependências (gitignored)
├── build/                 ← Arquivos temporários PyInstaller (gitignored)
├── build.py               ← Script de build do frontend
├── SimuladorFinanceiro.spec  ← Configuração PyInstaller
├── Makefile               ← Comandos de build
└── main.py                ← Ponto de entrada
```
