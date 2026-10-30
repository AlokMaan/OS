# Adaptive Fairness-Aware CPU Scheduling Simulator for Linux (AFAS)
**Dynamic Priority and Starvation Prevention — Project Review 2**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/pytest-12%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview
This project delivers a **user-space discrete-event CPU scheduling simulator** comparing classic textbook policies against an **Adaptive Fairness-Aware Scheduler (AFAS)**. 

AFAS dynamically modulates execution urgency by continuously balancing:
1. **Base Administrative Priority ($P_i$)**
2. **Bounded Waiting-Time Aging ($A_i(t)$)** — saturates at 50 time units to eliminate chronic starvation without inducing priority inversions
3. **Workload Responsiveness Class ($R_i$)** — weights interactive vs batch profiles
4. **Decayed Recent CPU-Share Penalty ($C_i(t)$)** — exponential half-life tracking ($\lambda = 40$)

### Policies Implemented:
* **FCFS:** First-Come, First-Served (non-preemptive)
* **SJF:** Shortest Job First (non-preemptive)
* **SRTF:** Shortest Remaining Time First (preemptive at arrivals)
* **Round Robin:** Cyclic FIFO execution with quantum $q = 4$
* **Priority:** Static priority dispatch without aging (starvation baseline)
* **AFAS (Proposed):** Dynamic multi-attribute scoring with deterministic tie-breaking

---

## 🗂️ Project Directory Structure

```text
afas-simulator/
├── afas_sim.py                     # Core simulation engine, PCB, baselines, AFAS, and metrics
├── test_sim.py                     # 12 automated pytest unit tests (analytical cases & invariants)
├── experiments.py                  # Batch benchmark runner (200 runs across 5 workloads x 5 seeds)
├── charts.py                       # High-resolution publication chart generator
├── interactive_cli.py              # Interactive terminal CLI with ASCII Gantt timeline playback
├── generate_review2_pdf.py         # Automated ReportLab script compiling Review 2 PDF
├── Makefile                        # Unix / Linux build automation
├── run.sh                          # Portable bash helper script
├── requirements.txt                # Python package dependencies
├── OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf # Complete 15-page Review 2 PDF
├── data/
│   ├── results_all_runs.csv        # Raw per-quantum simulation traces (200 records)
│   └── results.json                # Summary metrics, ablations, sensitivity, and scaling data
├── docs/
│   └── OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf
└── figures/
    ├── fig_1_max_wait.png          # Maximum ready-queue wait gap per workload
    ├── fig_2_p95_response.png      # 95th-percentile response time distribution
    ├── fig_3_avg_waiting.png       # Average waiting time across baselines
    ├── fig_4_gantt.png             # Gantt timeline comparison (Priority vs RR vs AFAS)
    ├── fig_5_ablation.png          # Component ablation breakdown (Aging vs Share penalty)
    ├── fig_6_sensitivity.png       # One-at-a-time parameter sensitivity sweep
    ├── fig_7_quantum_sweep.png     # Time-quantum sensitivity (q=1 to 32)
    └── fig_8_runtime_scaling.png   # Algorithmic decision runtime scaling (log-log)
```

---

## 🚀 Linux Setup and Execution Instructions

### 1. Prerequisites (Ubuntu / Debian / CentOS / Fedora / Arch / macOS)
Ensure Python 3.10 or later is installed:
```bash
# Ubuntu / Debian:
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# Fedora / RedHat:
sudo dnf install -y python3 python3-pip

# Arch Linux:
sudo pacman -S python python-pip
```

### 2. Environment Setup
You can use `make`, the helper script `./run.sh`, or standard `pip`:
```bash
# Using helper script:
./run.sh setup

# OR using standard commands:
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Step-by-Step Command Guide

### Step A: Run Automated Unit Tests (12/12 Passing)
Verifies analytical hand-solved textbook cases, engine invariants, and boundary conditions:
```bash
# Using pytest directly:
pytest -v test_sim.py

# Or via Makefile:
make test
```
**Expected Output:**
```text
test_sim.py::test_fcfs_hand_solved PASSED                                [  8%]
test_sim.py::test_sjf_hand_solved PASSED                                 [ 16%]
test_sim.py::test_srtf_hand_solved PASSED                                [ 25%]
test_sim.py::test_round_robin_hand_solved PASSED                         [ 33%]
test_sim.py::test_priority_hand_solved PASSED                            [ 41%]
test_sim.py::test_idle_gap_handling PASSED                               [ 50%]
test_sim.py::test_engine_invariants_all_workloads PASSED                 [ 58%]
test_sim.py::test_deterministic_reproducibility PASSED                   [ 66%]
test_sim.py::test_afas_tie_breaking_order PASSED                         [ 75%]
test_sim.py::test_input_validation_rejections PASSED                     [ 83%]
test_sim.py::test_aging_bounds_and_saturation PASSED                     [ 91%]
test_sim.py::test_afas_starvation_mitigation PASSED                      [100%]
============================== 12 passed in 0.08s ==============================
```

---

### Step B: Run Full Batch Benchmark Suite (200 Simulation Runs)
Executes all 5 synthetic workload families across 5 fixed seeds, ablations, parameter sweeps, and scaling benchmarks:
```bash
python3 experiments.py
# Or:
make experiments
```
* Generates `data/results_all_runs.csv` (complete audit trace).
* Generates `data/results.json` (aggregated summary and ablation statistics).

---

### Step C: Interactive Scheduling Simulator (CLI + ASCII Gantt)
Run the interactive simulator to test individual algorithms or inspect real-time score decomposition:
```bash
python3 interactive_cli.py
# Or:
make cli
```
To run a fast non-interactive trace demo:
```bash
python3 interactive_cli.py --demo
# Or:
make demo
```

---

### Step D: Re-compile All Publication Figures
Compiles high-resolution PNG plots from simulation logs:
```bash
python3 charts.py
# Or:
make charts
```

---

### Step E: Re-compile Formal Review 2 PDF Document
Compiles the complete 15-page formal academic report with embedded charts and tables:
```bash
python3 generate_review2_pdf.py
# Or:
make report
```
* Output file: `OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf`

---

## 📊 Summary of Benchmark Findings

| Policy | Avg Waiting Time ($\downarrow$) | Avg Response Time ($\downarrow$) | 95th% Response ($\downarrow$) | Max Wait Gap ($\downarrow$) | Context Switches | Jain Fairness Index ($\uparrow$) | Starvation Warnings ($\downarrow$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **FCFS** | 79.20 | 79.20 | 122.50 | 126.80 | 19.0 | 0.50 | 12.0 |
| **SJF** | 37.00 | 37.00 | 127.60 | 146.60 | 19.0 | 0.68 | 5.3 |
| **SRTF** | **29.40** | 26.60 | 123.10 | 146.50 | 21.7 | **0.80** | **4.1** |
| **Round Robin ($q=4$)** | 65.60 | 19.30 | **36.10** | **39.20** | 56.8 | 0.78 | 11.0 |
| **Priority (No aging)** | 76.30 | 76.30 | 158.70 | 168.20 | 19.0 | 0.55 | 9.0 |
| **AFAS (Proposed)** | **52.30** | **18.20** | **52.50** | **68.20** | **54.7** | **0.69** | **4.6** |

### Key Analytical Takeaways:
1. **Starvation Prevention:** AFAS slashes maximum ready-queue wait from **168.2 to 68.2 (59% reduction)** compared to static Priority scheduling.
2. **Interactivity:** AFAS achieves the best average response time (**18.2 units**) across all policies while maintaining context switches on par with Round Robin (54.7 vs 56.8).
3. **Ablation Finding:** Disabling aging ($w_a = 0$) causes maximum wait to double to **138.6 (+103%)**, confirming that the bounded aging accumulator is the primary technical lever driving fairness.

---

## 👥 Authors and Academic Affiliation
* **Alok Maan** (24BCB0057)
* **Arshdeep Singh** (24BCE0556)
* **Ankush Hooda** (24BCE0966)
* **Somya Sharma** (24BCT0324)

**Faculty Guide:** Prof. Ezhil Arasi  
**Institution:** School of Computer Science and Engineering, Vellore Institute of Technology (VIT)
