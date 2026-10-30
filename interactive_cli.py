"""
interactive_cli.py - Interactive Command-Line Interface for AFAS Simulator
Run algorithms interactively, inspect decision traces, and display ASCII Gantt charts.
"""

import sys
import argparse
from typing import List
from afas_sim import (
    Process, run_fcfs, run_sjf, run_srtf, run_round_robin, run_priority, run_afas,
    compute_metrics, get_workload_generator, validate_workload
)

def print_ascii_gantt(segments, span_scale=1):
    """Renders a formatted ASCII Gantt chart in terminal."""
    if not segments:
        print("[No execution segments recorded]")
        return
        
    print("\n" + "=" * 65)
    print("  ASCII EXECUTION TIMELINE (GANTT CHART)")
    print("=" * 65)
    
    # Top timeline blocks
    bar_str = "|"
    time_str = "0"
    
    for s in segments:
        dur = s.end - s.start
        width = max(len(s.pid) + 2, dur * 2)
        label = f" {s.pid} ".center(width, " ")
        bar_str += label + "|"
        time_str += str(s.end).rjust(width + 1)
        
    print(bar_str)
    print(time_str)
    print("=" * 65 + "\n")

def print_metrics_table(m: dict):
    print("---------------------------------------------------------")
    print("  SIMULATION PERFORMANCE EVALUATION")
    print("---------------------------------------------------------")
    print(f"  Average Waiting Time (WT)      : {m.get('avg_wt', 0):.2f}")
    print(f"  Average Turnaround Time (TAT)  : {m.get('avg_tat', 0):.2f}")
    print(f"  Average Response Time (RT)     : {m.get('avg_rt', 0):.2f}")
    print(f"  Median Response Time           : {m.get('median_rt', 0):.1f}")
    print(f"  95th-Percentile Response Time  : {m.get('p95_rt', 0):.1f}")
    print(f"  Maximum Ready-Queue Wait Gap   : {m.get('max_wait_gap', 0):.1f}")
    print(f"  Simulated Context Switches     : {m.get('ctx_switches', 0)}")
    print(f"  CPU Utilization                : {m.get('utilization', 0)*100:.1f} %")
    print(f"  Throughput (proc/time unit)    : {m.get('throughput', 0):.4f}")
    print(f"  Jain's Fairness Index          : {m.get('jain_fairness', 0):.2f} / 1.00")
    print(f"  Starvation Warnings (>40 units): {m.get('starvation_warnings', 0)}")
    print("---------------------------------------------------------")

def run_interactive():
    print("==================================================================")
    print("  ADAPTIVE FAIRNESS-AWARE CPU SCHEDULER (AFAS) - INTERACTIVE CLI")
    print("==================================================================")
    
    # 1. Select Workload
    print("\nSelect Workload:")
    print("  [1] W1 - Uniform Batch (Balanced Baseline, Offered Load ~0.89)")
    print("  [2] W2 - Mixed Bursts (Interactive vs Batch, Offered Load ~4.70)")
    print("  [3] W3 - Priority Skew (Starvation Stress Test, Offered Load ~2.50)")
    print("  [4] W4 - Burst Arrivals (Cluster Surges at t=0,40,80, Load ~2.40)")
    print("  [5] W5 - Share Imbalance (3 Huge Jobs vs 12 Small Jobs, Load ~3.00)")
    print("  [6] Custom 4-Process Hand-Solved Verification Workload")
    
    choice = input("\nEnter choice [1-6] (default=3): ").strip() or "3"
    
    if choice in ("1", "2", "3", "4", "5"):
        wname = f"W{choice}"
        seed_str = input("Enter pseudo-random seed [1-5] (default=1): ").strip() or "1"
        seed = int(seed_str)
        procs = get_workload_generator(wname)(seed=seed)
        print(f"\nLoaded Workload {wname} (Seed {seed}) with {len(procs)} processes.")
    else:
        procs = [
            Process("P1", arrival_time=0, burst_time=5, priority=5, workload_class="mixed"),
            Process("P2", arrival_time=1, burst_time=3, priority=5, workload_class="mixed"),
            Process("P3", arrival_time=2, burst_time=8, priority=5, workload_class="mixed"),
            Process("P4", arrival_time=3, burst_time=6, priority=5, workload_class="mixed"),
        ]
        print(f"\nLoaded Custom 4-Process Textbook Workload.")
        
    # 2. Select Policy
    print("\nSelect Scheduling Policy:")
    print("  [1] AFAS (Adaptive Fairness-Aware Dynamic Scheduler - Proposed)")
    print("  [2] FCFS (First-Come, First-Served)")
    print("  [3] SJF (Shortest Job First - Non-preemptive)")
    print("  [4] SRTF (Shortest Remaining Time First - Preemptive)")
    print("  [5] Round Robin (Preemptive Cyclic FIFO)")
    print("  [6] Priority (Static Urgency - No Aging Baseline)")
    print("  [7] Run ALL and Compare Side-by-Side")
    
    pol_choice = input("\nEnter choice [1-7] (default=1): ").strip() or "1"
    
    if pol_choice == "1":
        q_str = input("Enter time quantum (default=4): ").strip() or "4"
        trace_str = input("Show step-by-step decision score decomposition? (y/n, default=y): ").strip().lower() or "y"
        show_trace = trace_str == "y"
        
        print("\n[Executing AFAS Dynamic Scheduling]...")
        segs, log = run_afas(procs, quantum=int(q_str), trace=show_trace)
        metrics = compute_metrics(procs, segs)
        if len(procs) <= 15:
            print_ascii_gantt(segs)
        print_metrics_table(metrics)
        
    elif pol_choice == "2":
        segs = run_fcfs(procs)
        if len(procs) <= 15: print_ascii_gantt(segs)
        print_metrics_table(compute_metrics(procs, segs))
    elif pol_choice == "3":
        segs = run_sjf(procs)
        if len(procs) <= 15: print_ascii_gantt(segs)
        print_metrics_table(compute_metrics(procs, segs))
    elif pol_choice == "4":
        segs = run_srtf(procs)
        if len(procs) <= 15: print_ascii_gantt(segs)
        print_metrics_table(compute_metrics(procs, segs))
    elif pol_choice == "5":
        q_str = input("Enter time quantum (default=4): ").strip() or "4"
        segs = run_round_robin(procs, quantum=int(q_str))
        if len(procs) <= 15: print_ascii_gantt(segs)
        print_metrics_table(compute_metrics(procs, segs))
    elif pol_choice == "6":
        segs = run_priority(procs)
        if len(procs) <= 15: print_ascii_gantt(segs)
        print_metrics_table(compute_metrics(procs, segs))
    elif pol_choice == "7":
        print("\n" + "=" * 80)
        print(f"{'Policy':<16} | {'Avg WT':<7} | {'Avg RT':<7} | {'p95 RT':<7} | {'Max Wait':<8} | {'Ctx Sw':<6} | {'Jain':<5} | {'Warn':<5}")
        print("=" * 80)
        
        runners = [
            ("FCFS", lambda p: run_fcfs(p)),
            ("SJF", lambda p: run_sjf(p)),
            ("SRTF", lambda p: run_srtf(p)),
            ("Round Robin", lambda p: run_round_robin(p, 4)),
            ("Priority", lambda p: run_priority(p)),
            ("AFAS (Proposed)", lambda p: run_afas(p, 4)[0])
        ]
        for name, fn in runners:
            segs = fn(procs)
            m = compute_metrics(procs, segs)
            print(f"{name:<16} | {m['avg_wt']:<7.1f} | {m['avg_rt']:<7.1f} | {m['p95_rt']:<7.1f} | {m['max_wait_gap']:<8.1f} | {m['ctx_switches']:<6.1f} | {m['jain_fairness']:<5.2f} | {m['starvation_warnings']:<5.1f}")
        print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFAS Interactive CLI")
    parser.add_argument("--demo", action="store_true", help="Run quick automated demo comparison")
    args = parser.parse_args()
    
    if args.demo:
        procs = get_workload_generator("W3")(seed=1)
        segs, _ = run_afas(procs, quantum=4, trace=True)
        print_metrics_table(compute_metrics(procs, segs))
    else:
        run_interactive()
