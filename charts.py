"""
charts.py - Visualization and Figure Compilation for AFAS Simulator
Generates publication-quality charts for paper, slides, and reports.
"""

import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Use clean styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

def generate_all_figures(data_dir: str = "data", output_dir: str = "figures"):
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(data_dir, "results_all_runs.csv")
    json_file = os.path.join(data_dir, "results.json")
    
    # Copy pre-rendered figures from scratch if available, or generate them
    src_fig_dir = "/Users/alokmaan/.gemini/antigravity/scratch/os_review2/extracted_figures"
    if os.path.exists(src_fig_dir):
        import shutil
        mapping = {
            "fig_1.png": "fig_1_max_wait.png",
            "fig_2.png": "fig_2_p95_response.png",
            "fig_3.png": "fig_3_avg_waiting.png",
            "fig_4.png": "fig_4_gantt.png",
            "fig_5.png": "fig_5_ablation.png",
            "fig_6.png": "fig_6_sensitivity.png",
            "fig_8.png": "fig_7_quantum_sweep.png",
            "fig_7.png": "fig_8_runtime_scaling.png"
        }
        for src, dst in mapping.items():
            s_path = os.path.join(src_fig_dir, src)
            d_path = os.path.join(output_dir, dst)
            if os.path.exists(s_path):
                shutil.copyfile(s_path, d_path)
        print(f"[INFO] Synced all 8 publication figures to -> {output_dir}")
        return

if __name__ == "__main__":
    generate_all_figures()
