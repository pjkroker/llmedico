.PHONY: test clean lint

VENV := ../.venv
PYTHON := $(VENV)/bin/python

test:
	$(PYTHON) -m pytest tests -v

clean:
	rm -rf .pytest_cache __pycache__

lint:
	$(PYTHON) -m ruff .
