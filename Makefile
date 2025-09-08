SHELL := /bin/bash

.PHONY: setup dev lint test run-detector run-dashboard precommit

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	black --check .
	ruff check .
	mypy apps || true

test:
	pytest -q

run-detector:
	python apps/pi_detector/main.py

run-dashboard:
	streamlit run apps/streamlit_dashboard/Home.py

precommit:
	pre-commit run -a
