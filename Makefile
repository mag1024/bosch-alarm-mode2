.PHONY: install clean format check

dist:
	uv build

clean:
	find . -name '.cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.ruff_cache' -exec rm -rf {} +
	rm -rf build dist *.egg-info

format:
	uv run ruff format

check:
	uv run ruff check --no-fix
