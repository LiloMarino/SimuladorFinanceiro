EXEC=main.py
CPROFILE_OUT = cprofile.prof
LINEPROFILE_OUT = lineprofile.lprof
APP_NAME = SimuladorFinanceiro
BUILD_DIR = build
DIST_DIR = dist
SPEC_FILE = SimuladorFinanceiro.spec

# --------------------------------------------------------------
# Build
# --------------------------------------------------------------
build: build-frontend build-exe

build-frontend:
	@echo "=== Compilando Frontend ==="
	cd frontend && npm run build
	@echo "=== Copiando Frontend para Backend ==="
	python scripts/copy_frontend.py

build-exe:
	@echo "=== Gerando executável (.exe) ==="
	pyinstaller $(SPEC_FILE) --clean --noconfirm

# --------------------------------------------------------------
# Geração inicial do spec (rodar só uma vez)
# --------------------------------------------------------------
spec:
	@echo "=== Gerando arquivo .spec ==="
	pyinstaller $(EXEC) \
		--onefile \
		--name $(APP_NAME) \
		--add-data "backend/static:backend/static" \
		--add-data "backend/templates:backend/templates"

# --------------------------------------------------------------
# Lint
# --------------------------------------------------------------
check: lint typecheck

check-fix:
	ruff check --fix

lint:
	ruff check

lint-fix:
	ruff check --fix
	
typecheck:
	pyright

# --------------------------------------------------------------
# Código de qualidade
# --------------------------------------------------------------
mi:
	radon mi $(EXEC) backend/ -s

cc:
	radon cc $(EXEC) backend/ -s -a
	radon cc $(EXEC) backend/ -s -a -O cc.txt

radon:
	radon cc $(EXEC) backend/ -s -a -j -O cc.json
	radon mi $(EXEC) backend/ -s -j -O mi.json
	radon hal $(EXEC) backend/ -j -O hal.json

# --------------------------------------------------------------
# Formatação
# --------------------------------------------------------------
format:
	ruff format

# --------------------------------------------------------------
# Profiling
# --------------------------------------------------------------
cprofile:
	python -m cProfile -o $(CPROFILE_OUT) $(EXEC)
	snakeviz $(CPROFILE_OUT)

lineprofile:
	LINE_PROFILE=1 python $(EXEC)

lineprofile-view:
	python -m line_profiler $(LINEPROFILE_OUT)

snakeviz:
	snakeviz $(CPROFILE_OUT)

# --------------------------------------------------------------
# Limpeza
# --------------------------------------------------------------

build-clean:
	@echo "=== Limpando arquivos de build ==="
	python -c "import shutil; from pathlib import Path; dirs=['backend/static','backend/templates','build','dist']; [shutil.rmtree(d) if Path(d).exists() else None for d in dirs]"
	@echo "Build limpo!"

clean:
	@echo "=== Limpando artefatos auxiliares ==="
	python -c "import os; from pathlib import Path; files=['*.prof','*.lprof','cc.json','mi.json','hal.json']; [os.remove(f) if Path(f).exists() else None for pattern in files for f in Path('.').glob(pattern)]"