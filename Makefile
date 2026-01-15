EXEC=main.py
CPROFILE_OUT = cprofile.prof
LINEPROFILE_OUT = lineprofile.lprof
BUILD_DIR = dist
SPEC_FILE = SimuladorFinanceiro.spec

# --------------------------------------------------------------
# Build & Package
# --------------------------------------------------------------
validate:
	@echo "=== Validando Sistema de Build ==="
	python validate_build.py

build: build-frontend build-exe

build-frontend:
	@echo "=== Compilando Frontend ==="
	cd frontend && npm run build

build-exe:
	@echo "=== Compilando Executável com PyInstaller ==="
	pyinstaller $(SPEC_FILE) --clean --noconfirm

build-clean:
	@echo "=== Limpando arquivos de build ==="
	python -c "import shutil; from pathlib import Path; dirs=['backend/static','backend/templates','build','dist']; [shutil.rmtree(d) if Path(d).exists() else None for d in dirs]"
	@echo "Build limpo!"

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
clean:
	python -c "import os; from pathlib import Path; files=['*.prof','*.lprof','cc.json','mi.json','hal.json']; [os.remove(f) if Path(f).exists() else None for pattern in files for f in Path('.').glob(pattern)]"