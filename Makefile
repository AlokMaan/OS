# Makefile for AFAS Discrete-Event CPU Scheduling Simulator
# Operating Systems Project Review - 2

PY ?= $(shell if [ -d ".venv" ]; then echo ".venv/bin/python3"; elif command -v uv >/dev/null 2>&1; then echo "uv run --with pytest,numpy,matplotlib,reportlab,pillow python3"; else echo "python3"; fi)

.PHONY: help setup test experiments charts cli demo report all clean

help:
	@echo "=================================================================="
	@echo "  Adaptive Fairness-Aware CPU Scheduling Simulator (AFAS)"
	@echo "=================================================================="
	@echo "Available commands:"
	@echo "  make setup        - Create virtualenv and install dependencies"
	@echo "  make test         - Run 12 automated verification tests (pytest)"
	@echo "  make experiments  - Run full benchmark suite (200 simulation runs)"
	@echo "  make charts       - Generate all 8 publication-grade figures"
	@echo "  make cli          - Launch interactive scheduling simulator"
	@echo "  make demo         - Run quick automated scheduling demo trace"
	@echo "  make report       - Recompile formal Review 2 PDF document"
	@echo "  make all          - Execute test, experiments, charts, and report"
	@echo "  make clean        - Remove caches and temporary files"
	@echo "=================================================================="

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "[SUCCESS] Environment configured. Activate with: source .venv/bin/activate"

test:
	$(PY) -m pytest -v test_sim.py

experiments:
	$(PY) experiments.py

charts:
	$(PY) charts.py

cli:
	$(PY) interactive_cli.py

demo:
	$(PY) interactive_cli.py --demo

report:
	$(PY) generate_review2_pdf.py

all: test experiments charts report
	@echo "=================================================================="
	@echo "[SUCCESS] All tests, experiments, charts, and reports compiled!"
	@echo "PDF report available at: ./OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf"
	@echo "=================================================================="

clean:
	rm -rf __pycache__ .pytest_cache .venv
