PYTHON := python3
VENV_DIR := .venv
VENV_PY := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
SCENARIO ?= still
METHODS ?= all

.PHONY: venv install run freeze clean-venv test evaluate plots

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip

install: venv
	$(VENV_PIP) install -r requirements.txt

run:
	$(VENV_PY) main.py

test:
	$(VENV_PY) -m unittest discover -s tests -p "test_*.py"

evaluate:
	$(VENV_PY) scripts/offline_evaluate.py --video "$(VIDEO)" --scenario "$(SCENARIO)" --methods "$(METHODS)" $(if $(GT),--ground-truth "$(GT)",) $(if $(RUN_ID),--run-id "$(RUN_ID)",)

plots:
	$(VENV_PY) scripts/generate_figures.py --run-dir "$(RUN_DIR)"

freeze:
	$(VENV_PIP) freeze > requirements.txt

clean-venv:
	rm -rf $(VENV_DIR)
