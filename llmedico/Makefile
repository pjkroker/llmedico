.PHONY: test clean lint

VENV := ../.venv
PYTHON := $(VENV)/bin/python

test:
	$(PYTHON) -m pytest tests -v

clean:
	rm -rf .pytest_cache __pycache__
	rm -rf ./data/output/*

lint:
	$(PYTHON) -m ruff .

install-deps:
	pip install -e ../llm_caller
	pip install -e ../pyjdoctor
	pip install -e ../se_helpers

install: install-deps
	pip install -e .