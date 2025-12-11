check: lint typecheck

check-fix:
	ruff check --fix

lint:
	ruff check

lint-fix:
	ruff check --fix
	
typecheck:
	pyright

mi:
	radon mi main.py backend/ -s

cc:
	radon cc main.py backend/ -s -a
	radon cc main.py backend/ -s -a -O cc.txt

radon:
	radon cc main.py backend/ -s -a -j -O cc.json
	radon mi main.py backend/ -s -j -O mi.json
	radon hal main.py backend/ -j -O hal.json

format:
	ruff format

clean:
	del cc.json
	del mi.json
	del hal.json