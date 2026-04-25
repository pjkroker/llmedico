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