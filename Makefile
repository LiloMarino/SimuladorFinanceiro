EXEC=main.py
CPROFILE_OUT = cprofile.prof
LINEPROFILE_OUT = lineprofile.lprof
BUILD_DIR = dist
SPEC_FILE = SimuladorFinanceiro.spec

# --------------------------------------------------------------
# Build & Package
# --------------------------------------------------------------
build: build-frontend build-exe

build-frontend:
	@echo "=== Compilando Frontend ==="
	python build.py

build-exe:
	@echo "=== Compilando Executável com PyInstaller ==="
	pyinstaller $(SPEC_FILE) --clean --noconfirm

build-clean:
	@echo "=== Limpando arquivos de build ==="
	@if exist "backend\static" rmdir /S /Q backend\static
	@if exist "backend\templates" rmdir /S /Q backend\templates
	@if exist "build" rmdir /S /Q build
	@if exist "dist" rmdir /S /Q dist
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
	set LINE_PROFILE=1 && python $(EXEC)

lineprofile-view:
	python -m line_profiler $(LINEPROFILE_OUT)

snakeviz:
	snakeviz $(CPROFILE_OUT)

# --------------------------------------------------------------
# Limpeza
# --------------------------------------------------------------
clean:
	del /Q *.prof *.lprof 2>nul
	del cc.json 2>nul
	del mi.json 2>nul
	del hal.json 2>nul