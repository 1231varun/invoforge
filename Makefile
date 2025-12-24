# InvoForge Makefile
# Run 'make help' to see available commands

.PHONY: help install install-dev test test-cov lint format clean run

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only (fast)
	pytest tests/unit -v

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

lint:  ## Run linter
	ruff check .

lint-fix:  ## Run linter and auto-fix issues
	ruff check --fix .

format:  ## Format code
	ruff format .

format-check:  ## Check code formatting (CI mode)
	ruff format --check .

check:  ## Run all checks (lint + format + tests)
	ruff check .
	ruff format --check .
	pytest tests/ -v

run:  ## Run development server
	python run.py

build:  ## Build standalone executable
	python build_app.py

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

