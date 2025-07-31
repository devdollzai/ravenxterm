.PHONY: fmt lint test run build clean

fmt:
	black .
	isort .

lint:
	black . --check
	isort . --check
	flake8 .
	mypy .

test:
	pytest

run:
	python -m app

build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
