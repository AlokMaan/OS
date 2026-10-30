"""
experiments.py - Batch Experiment Benchmark Runner for AFAS Simulator
Runs 200 simulation runs across 5 workloads x 5 seeds, executes ablations,
sensitivity sweeps, quantum sweeps, and scaling benchmarks, saving CSV & JSON.
"""

import time
import json
import csv
import os
import argparse
from typing import Dict, List, Any
from afas_sim import (
    Process, run_fcfs, run_sjf, run_srtf, run_round_robin, run_priority, run_afas,
    compute_metrics, get_workload_generator
)

def run_all_benchmarks(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "results_all_runs.csv")
    json_file = os.path.join(output_dir, "results.json")
    
    print("=" * 80)
    print("  AFAS DISCRETE-EVENT CPU SCHEDULER: EXPERIMENTAL BENCHMARK SUITE")
    print("=" * 80)
    
    workloads = ["W1", "W2", "W3", "W4", "W5"]
    seeds = [1, 2, 3, 4, 5]
    
    records = []
    
    # 1. Main Policy Benchmark Runs
    print("[1/5] Executing Main Workload Runs (5 Workloads x 5 Seeds x 6 Policies)...")
    for wname in workloads:
        gen = get_workload_generator(wname)
        for seed in seeds:
            procs = gen(seed)
            
            # Policy 1: FCFS
            segs_fcfs = run_fcfs(procs)
            m_fcfs = compute_metrics(procs, segs_fcfs)
            records.append({"workload": wname, "seed": seed, "policy": "FCFS", **m_fcfs})
            
            # Policy 2: SJF
            segs_sjf = run_sjf(procs)
            m_sjf = compute_metrics(procs, segs_sjf)
            records.append({"workload": wname, "seed": seed, "policy": "SJF", **m_sjf})
            
            # Policy 3: SRTF
            segs_srtf = run_srtf(procs)
            m_srtf = compute_metrics(procs, segs_srtf)
            records.append({"workload": wname, "seed": seed, "policy": "SRTF", **m_srtf})
            
            # Policy 4: Round Robin (q=4)
            segs_rr = run_round_robin(procs, quantum=4)
            m_rr = compute_metrics(procs, segs_rr)
            records.append({"workload": wname, "seed": seed, "policy": "RR (q=4)", **m_rr})
            
            # Policy 5: Priority (No aging)
            segs_pri = run_priority(procs)
            m_pri = compute_metrics(procs, segs_pri)
            records.append({"workload": wname, "seed": seed, "policy": "Priority", **m_pri})
            
            # Policy 6: AFAS Default (q=4, wp=0.30, wa=0.40, wr=0.15, wc=0.15)
            segs_afas, _ = run_afas(procs, quantum=4, wp=0.30, wa=0.40, wr=0.15, wc=0.15)
            m_afas = compute_metrics(procs, segs_afas)
            records.append({"workload": wname, "seed": seed, "policy": "AFAS", **m_afas})
            
            # Ablation 1: AFAS no-aging (wa=0)
            segs_no_age, _ = run_afas(procs, quantum=4, wp=0.30, wa=0.0, wr=0.15, wc=0.15)
            m_no_age = compute_metrics(procs, segs_no_age)
            records.append({"workload": wname, "seed": seed, "policy": "AFAS no-aging", **m_no_age})
            
            # Ablation 2: AFAS no-share (wc=0)
            segs_no_share, _ = run_afas(procs, quantum=4, wp=0.30, wa=0.40, wr=0.15, wc=0.0)
            m_no_share = compute_metrics(procs, segs_no_share)
            records.append({"workload": wname, "seed": seed, "policy": "AFAS no-share", **m_no_share})
            
        print(f"  Finished {wname} across 5 seeds.")

    # Write CSV
    if records:
        fieldnames = list(records[0].keys())
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        print(f"  Saved raw simulation runs -> {csv_file} ({len(records)} records)")

    # 2. Compute Aggregates
    print("\n[2/5] Aggregating Summary Metrics across Workloads W1–W5...")
    policies = ["FCFS", "SJF", "SRTF", "RR (q=4)", "Priority", "AFAS", "AFAS no-aging", "AFAS no-share"]
    summary = {}
    
    for pol in policies:
        pol_recs = [r for r in records if r["policy"] == pol]
        summary[pol] = {
            "avg_wt": round(sum(r["avg_wt"] for r in pol_recs) / len(pol_recs), 1),
            "avg_rt": round(sum(r["avg_rt"] for r in pol_recs) / len(pol_recs), 1),
            "p95_rt": round(sum(r["p95_rt"] for r in pol_recs) / len(pol_recs), 1),
            "max_wait_gap": round(sum(r["max_wait_gap"] for r in pol_recs) / len(pol_recs), 1),
            "ctx_switches": round(sum(r["ctx_switches"] for r in pol_recs) / len(pol_recs), 1),
            "jain_fairness": round(sum(r["jain_fairness"] for r in pol_recs) / len(pol_recs), 2),
            "starvation_warnings": round(sum(r["starvation_warnings"] for r in pol_recs) / len(pol_recs), 1)
        }
        
    print("-" * 85)
    print(f"{'Policy':<16} | {'Avg WT':<7} | {'Avg RT':<7} | {'p95 RT':<7} | {'Max Wait':<8} | {'Ctx Sw':<6} | {'Jain':<5} | {'Warn':<5}")
    print("-" * 85)
    for pol in policies:
        s = summary[pol]
        print(f"{pol:<16} | {s['avg_wt']:<7.1f} | {s['avg_rt']:<7.1f} | {s['p95_rt']:<7.1f} | {s['max_wait_gap']:<8.1f} | {s['ctx_switches']:<6.1f} | {s['jain_fairness']:<5.2f} | {s['starvation_warnings']:<5.1f}")
    print("-" * 85)

    # 3. One-at-a-time Sensitivity Sweep (w_p, w_a, w_r, w_c)
    print("\n[3/5] Executing One-at-a-Time Parameter Sensitivity Sweep...")
    weight_vals = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    sensitivity_results = {"wp": {}, "wa": {}, "wr": {}, "wc": {}}
    
    # Sweep over W2, W3, W5
    stress_workloads = ["W2", "W3", "W5"]
    for param in ["wp", "wa", "wr", "wc"]:
        for val in weight_vals:
            w_dict = {"wp": 0.30, "wa": 0.40, "wr": 0.15, "wc": 0.15}
            w_dict[param] = val
            
            run_wts, run_rts, run_maxs = [], [], []
            for wname in stress_workloads:
                gen = get_workload_generator(wname)
                for seed in seeds:
                    procs = gen(seed)
                    segs, _ = run_afas(procs, quantum=4, **w_dict)
                    m = compute_metrics(procs, segs)
                    run_wts.append(m["avg_wt"])
                    run_rts.append(m["avg_rt"])
                    run_maxs.append(m["max_wait_gap"])
                    
            sensitivity_results[param][str(val)] = {
                "avg_wt": round(sum(run_wts) / len(run_wts), 2),
                "avg_rt": round(sum(run_rts) / len(run_rts), 2),
                "max_wait_gap": round(sum(run_maxs) / len(run_maxs), 2)
            }
        print(f"  Finished sweep for {param}.")

    # 4. Time-Quantum Sweep (q = 1, 2, 4, 8, 16, 32)
    print("\n[4/5] Executing Time-Quantum Sweep (q = 1, 2, 4, 8, 16, 32)...")
    quanta = [1, 2, 4, 8, 16, 32]
    quantum_results = {"RR": {}, "AFAS": {}}
    for q in quanta:
        rr_ctx, rr_rt, rr_max = [], [], []
        afas_ctx, afas_rt, afas_max = [], [], []
        for wname in workloads:
            gen = get_workload_generator(wname)
            for seed in seeds:
                procs = gen(seed)
                # RR
                s_rr = run_round_robin(procs, quantum=q)
                m_rr = compute_metrics(procs, s_rr)
                rr_ctx.append(m_rr["ctx_switches"])
                rr_rt.append(m_rr["avg_rt"])
                rr_max.append(m_rr["max_wait_gap"])
                # AFAS
                s_af, _ = run_afas(procs, quantum=q)
                m_af = compute_metrics(procs, s_af)
                afas_ctx.append(m_af["ctx_switches"])
                afas_rt.append(m_af["avg_rt"])
                afas_max.append(m_af["max_wait_gap"])
                
        quantum_results["RR"][str(q)] = {
            "ctx_switches": round(sum(rr_ctx) / len(rr_ctx), 1),
            "avg_rt": round(sum(rr_rt) / len(rr_rt), 1),
            "max_wait_gap": round(sum(rr_max) / len(rr_max), 1)
        }
        quantum_results["AFAS"][str(q)] = {
            "ctx_switches": round(sum(afas_ctx) / len(afas_ctx), 1),
            "avg_rt": round(sum(afas_rt) / len(afas_rt), 1),
            "max_wait_gap": round(sum(afas_max) / len(afas_max), 1)
        }
        print(f"  Finished quantum q={q}.")

    # 5. Decision Runtime Scaling Benchmark (10, 50, 100, 500 tasks)
    print("\n[5/5] Executing Decision Runtime Scaling Benchmark...")
    sizes = [10, 50, 100, 500]
    scaling_results = {}
    
    for n in sizes:
        scaling_results[str(n)] = {}
        # Generate generic synthetic workload
        procs = []
        for i in range(n):
            procs.append(Process(f"P{i+1}", arrival_time=i % 20, burst_time=5 + (i % 15), priority=1 + (i % 10)))
            
        for pol_name, runner in [
            ("FCFS", lambda p: run_fcfs(p)),
            ("RR", lambda p: run_round_robin(p, 4)),
            ("SJF", lambda p: run_sjf(p)),
            ("Priority", lambda p: run_priority(p)),
            ("SRTF", lambda p: run_srtf(p)),
            ("AFAS", lambda p: run_afas(p, 4))
        ]:
            durations = []
            for _ in range(3):
                t0 = time.perf_counter()
                runner(procs)
                t1 = time.perf_counter()
                durations.append((t1 - t0) * 1000.0) # in ms
            scaling_results[str(n)][pol_name] = round(sum(durations) / len(durations), 2)
        print(f"  Scaled N={n:3d} -> AFAS: {scaling_results[str(n)]['AFAS']:.2f} ms | RR: {scaling_results[str(n)]['RR']:.2f} ms")

    # Save to JSON
    full_output = {
        "summary": summary,
        "sensitivity": sensitivity_results,
        "quantum_sweep": quantum_results,
        "scaling": scaling_results
    }
    with open(json_file, "w") as f:
        json.dump(full_output, f, indent=2)
    print(f"\n[COMPLETE] Successfully generated all experimental data -> {json_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFAS Benchmark Runner")
    parser.add_argument("--outdir", default="data", help="Output directory for CSV/JSON")
    args = parser.parse_args()
    run_all_benchmarks(args.outdir)
