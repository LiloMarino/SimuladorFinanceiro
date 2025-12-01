check: lint typecheck

lint:
	ruff check
	
typecheck:
	pyright

check-fix:
	ruff check --fix

lint-fix:
	ruff check --fix

format:
	ruff format

