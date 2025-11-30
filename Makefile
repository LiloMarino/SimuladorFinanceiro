check:
	ruff check
	pyright

lint:
	ruff check

lint-fix:
	ruff check --fix

format:
	ruff format

typecheck:
	pyright
