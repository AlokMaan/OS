#!/usr/bin/env bash
# run.sh - Portable runner for AFAS CPU Simulator on Linux / macOS

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Detect Python runner (virtualenv -> uv -> system python)
if [ -d "$DIR/.venv" ]; then
    PY="$DIR/.venv/bin/python3"
elif command -v uv >/dev/null 2>&1; then
    PY="uv run --with pytest,numpy,matplotlib,reportlab,pillow python3"
else
    PY="python3"
fi

ACTION="${1:-help}"

case "$ACTION" in
    setup)
        echo "--> Setting up Python virtual environment..."
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip
        .venv/bin/pip install -r requirements.txt
        echo "--> Environment ready! Run: source .venv/bin/activate"
        ;;
    test)
        echo "--> Running 12 verification unit tests..."
        $PY -m pytest -v test_sim.py
        ;;
    experiments)
        echo "--> Running batch experiment suite (200 simulation runs)..."
        $PY experiments.py
        ;;
    charts)
        echo "--> Generating publication figures..."
        $PY charts.py
        ;;
    cli)
        echo "--> Launching interactive CLI..."
        $PY interactive_cli.py
        ;;
    demo)
        echo "--> Running automated AFAS trace demonstration..."
        $PY interactive_cli.py --demo
        ;;
    report)
        echo "--> Compiling Review 2 PDF document..."
        $PY generate_review2_pdf.py
        ;;
    all)
        echo "--> Running full pipeline: test -> experiments -> charts -> report..."
        $PY -m pytest -v test_sim.py
        $PY experiments.py
        $PY charts.py
        $PY generate_review2_pdf.py
        echo "--> All done! Output PDF: $DIR/OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf"
        ;;
    *)
        echo "Usage: ./run.sh [setup|test|experiments|charts|cli|demo|report|all]"
        echo ""
        echo "Commands:"
        echo "  setup        - Install dependencies into .venv"
        echo "  test         - Run unit test suite (12 tests)"
        echo "  experiments  - Run 200 simulation runs across 5 workloads"
        echo "  charts       - Compile all 8 publication figures"
        echo "  cli          - Interactive terminal simulator"
        echo "  demo         - Fast console trace demo"
        echo "  report       - Compile formal PDF report"
        echo "  all          - Execute full build pipeline"
        ;;
esac
