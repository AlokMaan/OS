"""
afas_sim.py - Adaptive Fairness-Aware CPU Scheduling Simulator for Linux
Core simulation engine, process models, baseline policies, and metric calculators.
"""

import math
import copy
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int  # 1 (lowest) to 10 (highest)
    workload_class: str = "mixed"  # "interactive", "mixed", or "batch"
    
    # Dynamic simulation state
    remaining_burst: int = field(init=False)
    last_cpu_time: int = field(init=False)
    decayed_cpu_service: float = 0.0
    last_decay_time: int = field(init=False)
    start_time: Optional[int] = None
    finish_time: Optional[int] = None
    first_response_time: Optional[int] = None

    def __post_init__(self):
        self.remaining_burst = self.burst_time
        self.last_cpu_time = self.arrival_time
        self.last_decay_time = self.arrival_time

@dataclass
class Segment:
    pid: str
    start: int
    end: int

@dataclass
class DecisionRecord:
    timestamp: int
    chosen_pid: str
    ready_count: int
    wp_P: float
    wa_A: float
    wr_R: float
    wc_C: float
    total_score: float
    action: str

def validate_workload(processes: List[Process]) -> None:
    """Validates workload records and raises ValueError on constraint violations."""
    if not processes:
        raise ValueError("Workload cannot be empty.")
    
    pids = set()
    for p in processes:
        if not p.pid or p.pid in pids:
            raise ValueError(f"Duplicate or invalid process identifier: '{p.pid}'")
        pids.add(p.pid)
        
        if p.arrival_time < 0:
            raise ValueError(f"Process {p.pid} has negative arrival time: {p.arrival_time}")
        if p.burst_time <= 0:
            raise ValueError(f"Process {p.pid} has non-positive burst time: {p.burst_time}")
        if not (1 <= p.priority <= 10):
            raise ValueError(f"Process {p.pid} has priority outside [1, 10]: {p.priority}")
        if p.workload_class not in ("interactive", "mixed", "batch"):
            raise ValueError(f"Process {p.pid} has unknown workload class: '{p.workload_class}'")

def verify_engine_invariants(processes: List[Process], segments: List[Segment]) -> None:
    """Checks the three formal execution invariants."""
    if not processes:
        return
        
    # Invariant 1: Non-overlapping segments
    for i in range(len(segments) - 1):
        if segments[i].end > segments[i+1].start:
            raise AssertionError(f"Invariant 1 violated: Segment overlap between {segments[i]} and {segments[i+1]}")

    # Invariant 2 & 3: Burst conservation and Temporal causality
    proc_map = {p.pid: p for p in processes}
    burst_accum = {p.pid: 0 for p in processes}
    
    for seg in segments:
        p = proc_map[seg.pid]
        if seg.start < p.arrival_time:
            raise AssertionError(f"Invariant 3 violated: Process {p.pid} executed at {seg.start} before arrival {p.arrival_time}")
        burst_accum[seg.pid] += (seg.end - seg.start)

    for pid, executed in burst_accum.items():
        expected = proc_map[pid].burst_time
        if executed != expected:
            raise AssertionError(f"Invariant 2 violated: Process {pid} executed for {executed} units, expected {expected}")

# ================= BASELINE POLICIES =================

def run_fcfs(processes: List[Process]) -> List[Segment]:
    """First-Come, First-Served (FCFS) non-preemptive baseline."""
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    segments = []
    current_time = 0
    uncompleted = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
    
    while uncompleted:
        ready = [p for p in uncompleted if p.arrival_time <= current_time]
        if not ready:
            current_time = uncompleted[0].arrival_time
            continue
            
        chosen = ready[0]  # Already sorted by arrival then pid
        segments.append(Segment(chosen.pid, current_time, current_time + chosen.burst_time))
        current_time += chosen.burst_time
        uncompleted.remove(chosen)
        
    verify_engine_invariants(processes, segments)
    return segments

def run_sjf(processes: List[Process]) -> List[Segment]:
    """Shortest Job First (SJF) non-preemptive baseline."""
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    segments = []
    current_time = 0
    uncompleted = sorted(procs, key=lambda p: p.arrival_time)
    
    while uncompleted:
        ready = [p for p in uncompleted if p.arrival_time <= current_time]
        if not ready:
            current_time = uncompleted[0].arrival_time
            continue
            
        # Shortest burst, tie-break by arrival then PID
        ready.sort(key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        chosen = ready[0]
        segments.append(Segment(chosen.pid, current_time, current_time + chosen.burst_time))
        current_time += chosen.burst_time
        uncompleted.remove(chosen)
        
    verify_engine_invariants(processes, segments)
    return segments

def run_srtf(processes: List[Process]) -> List[Segment]:
    """Shortest Remaining Time First (SRTF) preemptive baseline."""
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    segments: List[Segment] = []
    current_time = 0
    uncompleted = procs
    
    while uncompleted:
        ready = [p for p in uncompleted if p.arrival_time <= current_time]
        if not ready:
            current_time = min(p.arrival_time for p in uncompleted)
            continue
            
        ready.sort(key=lambda p: (p.remaining_burst, p.arrival_time, p.pid))
        chosen = ready[0]
        
        # Calculate time until next arrival that could preempt
        future_arrivals = [p.arrival_time for p in uncompleted if p.arrival_time > current_time]
        next_arrival = min(future_arrivals) if future_arrivals else None
        
        if next_arrival is not None:
            time_slice = min(chosen.remaining_burst, next_arrival - current_time)
        else:
            time_slice = chosen.remaining_burst
            
        time_slice = max(1, time_slice)
        
        # Merge segments if same process continues
        if segments and segments[-1].pid == chosen.pid and segments[-1].end == current_time:
            segments[-1].end += time_slice
        else:
            segments.append(Segment(chosen.pid, current_time, current_time + time_slice))
            
        current_time += time_slice
        chosen.remaining_burst -= time_slice
        if chosen.remaining_burst == 0:
            uncompleted.remove(chosen)
            
    verify_engine_invariants(processes, segments)
    return segments

def run_round_robin(processes: List[Process], quantum: int = 4) -> List[Segment]:
    """Round Robin (RR) preemptive cyclic FIFO scheduling."""
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    procs.sort(key=lambda p: (p.arrival_time, p.pid))
    
    segments: List[Segment] = []
    current_time = 0
    ready_queue: List[Process] = []
    inactive = list(procs)
    
    while ready_queue or inactive:
        # Move newly arrived processes to ready queue
        newly_arrived = [p for p in inactive if p.arrival_time <= current_time]
        for p in newly_arrived:
            ready_queue.append(p)
            inactive.remove(p)
            
        if not ready_queue:
            current_time = min(p.arrival_time for p in inactive)
            continue
            
        curr_proc = ready_queue.pop(0)
        time_slice = min(quantum, curr_proc.remaining_burst)
        
        if segments and segments[-1].pid == curr_proc.pid and segments[-1].end == current_time:
            segments[-1].end += time_slice
        else:
            segments.append(Segment(curr_proc.pid, current_time, current_time + time_slice))
            
        current_time += time_slice
        curr_proc.remaining_burst -= time_slice
        
        # Newly arrived processes during execution join BEFORE the preempted job
        newly_arrived = [p for p in inactive if p.arrival_time <= current_time]
        for p in newly_arrived:
            ready_queue.append(p)
            inactive.remove(p)
            
        if curr_proc.remaining_burst > 0:
            ready_queue.append(curr_proc)
            
    verify_engine_invariants(processes, segments)
    return segments

def run_priority(processes: List[Process]) -> List[Segment]:
    """Non-preemptive Priority scheduling without aging (starvation baseline)."""
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    segments = []
    current_time = 0
    uncompleted = sorted(procs, key=lambda p: p.arrival_time)
    
    while uncompleted:
        ready = [p for p in uncompleted if p.arrival_time <= current_time]
        if not ready:
            current_time = uncompleted[0].arrival_time
            continue
            
        # Priority descending, tie-break by arrival then PID
        ready.sort(key=lambda p: (-p.priority, p.arrival_time, p.pid))
        chosen = ready[0]
        segments.append(Segment(chosen.pid, current_time, current_time + chosen.burst_time))
        current_time += chosen.burst_time
        uncompleted.remove(chosen)
        
    verify_engine_invariants(processes, segments)
    return segments

# ================= AFAS ADAPTIVE SCHEDULING ENGINE =================

def compute_afas_score(
    p: Process, 
    current_time: int, 
    wp: float, 
    wa: float, 
    wr: float, 
    wc: float
) -> Tuple[float, float, float, float, float]:
    """
    Computes S_i(t) and returns (total_score, weighted_P, weighted_A, weighted_R, weighted_C).
    Weights are already simplex-normalized.
    """
    # 1. Base Priority term: P_i = Priority / 10 in [0.1, 1.0]
    norm_P = p.priority / 10.0
    
    # 2. Bounded Waiting-Age term: A_i(t) = min(1.0, wait_time / 50.0)
    wait_time = max(0, current_time - p.last_cpu_time)
    norm_A = min(1.0, wait_time / 50.0)
    
    # 3. Workload class responsiveness factor:
    class_map = {"interactive": 1.0, "mixed": 0.5, "batch": 0.2}
    norm_R = class_map.get(p.workload_class, 0.5)
    
    # 4. Decayed Recent CPU-Share Penalty:
    # Update exponential decay up to current_time (half-life = 40)
    delta_t = current_time - p.last_decay_time
    decay_factor = math.pow(0.5, delta_t / 40.0)
    effective_service = p.decayed_cpu_service * decay_factor
    norm_C = min(1.0, effective_service / 40.0)
    
    weighted_P = wp * norm_P
    weighted_A = wa * norm_A
    weighted_R = wr * norm_R
    weighted_C = wc * norm_C
    
    score = weighted_P + weighted_A + weighted_R - weighted_C
    return score, weighted_P, weighted_A, weighted_R, weighted_C

def run_afas(
    processes: List[Process],
    quantum: int = 4,
    wp: float = 0.30,
    wa: float = 0.40,
    wr: float = 0.15,
    wc: float = 0.15,
    trace: bool = False
) -> Tuple[List[Segment], List[DecisionRecord]]:
    """
    Adaptive Fairness-Aware Scheduler (AFAS) dynamic priority engine.
    Returns (execution_segments, decision_audit_log).
    """
    validate_workload(processes)
    procs = [copy.deepcopy(p) for p in processes]
    
    # Normalize weights to sum to 1.0
    w_sum = wp + wa + wr + wc
    if w_sum <= 0:
        wp, wa, wr, wc = 0.25, 0.25, 0.25, 0.25
        w_sum = 1.0
    wp_n, wa_n, wr_n, wc_n = wp / w_sum, wa / w_sum, wr / w_sum, wc / w_sum
    
    segments: List[Segment] = []
    audit_log: List[DecisionRecord] = []
    current_time = 0
    ready_queue: List[Process] = []
    inactive = list(procs)
    
    while ready_queue or inactive:
        # Transfer arrived tasks to ready queue
        newly_arrived = [p for p in inactive if p.arrival_time <= current_time]
        for p in newly_arrived:
            ready_queue.append(p)
            inactive.remove(p)
            
        if not ready_queue:
            current_time = min(p.arrival_time for p in inactive)
            continue
            
        # Compute scores for all ready tasks
        scored_candidates = []
        for p in ready_queue:
            score, wP, wA, wR, wC = compute_afas_score(p, current_time, wp_n, wa_n, wr_n, wc_n)
            # Tie-break tuple: (-score, arrival_time, pid)
            scored_candidates.append((score, wP, wA, wR, wC, p))
            
        # Select task with max score deterministically
        scored_candidates.sort(key=lambda item: (-item[0], item[5].arrival_time, item[5].pid))
        best_score, best_wP, best_wA, best_wR, best_wC, chosen_proc = scored_candidates[0]
        
        slice_time = min(quantum, chosen_proc.remaining_burst)
        
        # Record decision audit record
        action_msg = f"DISPATCH {chosen_proc.pid} (slice {slice_time})"
        if best_wA >= 0.30 and chosen_proc.priority <= 3:
            action_msg += " [AGING_PROMOTION]"
            
        audit_log.append(DecisionRecord(
            timestamp=current_time,
            chosen_pid=chosen_proc.pid,
            ready_count=len(ready_queue),
            wp_P=round(best_wP, 4),
            wa_A=round(best_wA, 4),
            wr_R=round(best_wR, 4),
            wc_C=round(best_wC, 4),
            total_score=round(best_score, 4),
            action=action_msg
        ))
        
        if trace:
            print(f"t={current_time:3d} | Chosen: {chosen_proc.pid:4s} | "
                  f"Scores: P={best_wP:.3f}, A={best_wA:.3f}, R={best_wR:.3f}, -C={-best_wC:.3f} "
                  f"=> Total={best_score:.3f} | {action_msg}")
        
        # Append execution segment (merge contiguous if same pid)
        if segments and segments[-1].pid == chosen_proc.pid and segments[-1].end == current_time:
            segments[-1].end += slice_time
        else:
            segments.append(Segment(chosen_proc.pid, current_time, current_time + slice_time))
            
        # Update process execution state
        ready_queue.remove(chosen_proc)
        
        # Decay past service and add newly consumed burst
        delta_decay = current_time - chosen_proc.last_decay_time
        chosen_proc.decayed_cpu_service = (chosen_proc.decayed_cpu_service * math.pow(0.5, delta_decay / 40.0)) + slice_time
        chosen_proc.last_decay_time = current_time + slice_time
        
        current_time += slice_time
        chosen_proc.remaining_burst -= slice_time
        chosen_proc.last_cpu_time = current_time
        
        # Check newly arrived processes during slice
        newly_arrived = [p for p in inactive if p.arrival_time <= current_time]
        for p in newly_arrived:
            ready_queue.append(p)
            inactive.remove(p)
            
        if chosen_proc.remaining_burst > 0:
            ready_queue.append(chosen_proc)
            
    verify_engine_invariants(processes, segments)
    return segments, audit_log

# ================= METRIC ENGINE =================

def compute_metrics(processes: List[Process], segments: List[Segment]) -> Dict[str, Any]:
    """Computes comprehensive OS scheduling metrics for an execution trace."""
    if not processes:
        return {}
        
    proc_map = {p.pid: p for p in processes}
    first_start = {p.pid: None for p in processes}
    completion_time = {p.pid: None for p in processes}
    
    # Calculate intervals where process was in ready queue
    # A process is in ready queue from arrival to completion, EXCEPT when executing on CPU
    cpu_intervals = {p.pid: [] for p in processes}
    for seg in segments:
        if first_start[seg.pid] is None:
            first_start[seg.pid] = seg.start
        completion_time[seg.pid] = seg.end
        cpu_intervals[seg.pid].append((seg.start, seg.end))
        
    waiting_times = []
    turnaround_times = []
    response_times = []
    max_wait_gaps = []
    starvation_warnings = 0
    service_ratios = []
    
    for p in processes:
        pid = p.pid
        ct = completion_time[pid]
        tat = ct - p.arrival_time
        wt = tat - p.burst_time
        rt = first_start[pid] - p.arrival_time
        
        turnaround_times.append(tat)
        waiting_times.append(wt)
        response_times.append(rt)
        service_ratios.append(p.burst_time / tat if tat > 0 else 1.0)
        
        # Calculate ready-queue wait gaps (idle gaps between executions)
        gaps = []
        prev_end = p.arrival_time
        for (s_start, s_end) in cpu_intervals[pid]:
            gap = s_start - prev_end
            if gap > 0:
                gaps.append(gap)
                if gap > 40:
                    starvation_warnings += 1
            prev_end = s_end
            
        max_gap = max(gaps) if gaps else 0
        max_wait_gaps.append(max_gap)
        
    # Context switches: segment transitions where process changes
    ctx_switches = 0
    for i in range(len(segments) - 1):
        if segments[i].pid != segments[i+1].pid:
            ctx_switches += 1
            
    # Span & Utilization
    start_sim = min(p.arrival_time for p in processes)
    end_sim = max(seg.end for seg in segments) if segments else 0
    span = max(1, end_sim - start_sim)
    busy_time = sum(seg.end - seg.start for seg in segments)
    utilization = min(1.0, busy_time / span)
    throughput = len(processes) / span
    
    # Percentiles for Response Time (nearest-rank)
    sorted_rt = sorted(response_times)
    n = len(sorted_rt)
    median_rt = sorted_rt[n // 2]
    p95_idx = min(n - 1, math.ceil(0.95 * n) - 1)
    p95_rt = sorted_rt[p95_idx]
    
    # Jain Fairness Index: J = (sum x)^2 / (n * sum x^2) on service_ratios
    sum_x = sum(service_ratios)
    sum_x2 = sum(x**2 for x in service_ratios)
    jain_index = (sum_x**2) / (n * sum_x2) if sum_x2 > 0 else 1.0
    
    return {
        "avg_wt": round(sum(waiting_times) / n, 2),
        "avg_tat": round(sum(turnaround_times) / n, 2),
        "avg_rt": round(sum(response_times) / n, 2),
        "median_rt": round(float(median_rt), 1),
        "p95_rt": round(float(p95_rt), 1),
        "max_wait_gap": round(max(max_wait_gaps) if max_wait_gaps else 0.0, 1),
        "ctx_switches": ctx_switches,
        "utilization": round(utilization, 2),
        "throughput": round(throughput, 4),
        "jain_fairness": round(jain_index, 2),
        "starvation_warnings": starvation_warnings
    }

# ================= WORKLOAD GENERATORS =================

def generate_w1_uniform(seed: int = 1) -> List[Process]:
    """W1: Uniform Batch (Offered Load ~0.89). Arrival gap = 9, burst 6-10."""
    rng = random.Random(seed + 100)
    procs = []
    classes = ["interactive", "mixed", "batch"]
    for i in range(20):
        arr = i * 9
        burst = rng.randint(6, 10)
        pri = rng.randint(3, 7)
        wclass = rng.choice(classes)
        procs.append(Process(f"P{i+1}", arr, burst, pri, wclass))
    return procs

def generate_w2_mixed(seed: int = 1) -> List[Process]:
    """W2: Mixed Bursts (Offered Load ~4.70). 70% short interactive, 30% long batch."""
    rng = random.Random(seed + 200)
    procs = []
    for i in range(20):
        arr = rng.randint(0, 60)
        if rng.random() < 0.70:
            burst = rng.randint(2, 5)
            wclass = "interactive"
            pri = rng.randint(6, 10)
        else:
            burst = rng.randint(25, 45)
            wclass = "batch"
            pri = rng.randint(1, 5)
        procs.append(Process(f"P{i+1}", arr, burst, pri, wclass))
    procs.sort(key=lambda p: (p.arrival_time, int(p.pid[1:])))
    return procs

def generate_w3_priority_skew(seed: int = 1) -> List[Process]:
    """W3: Priority Skew (Offered Load ~2.50). 6 low-pri batch at t=0-5, 18 high-pri arriving."""
    rng = random.Random(seed + 300)
    procs = []
    # 6 low-pri batch
    for i in range(6):
        arr = rng.randint(0, 5)
        burst = rng.randint(10, 20)
        pri = rng.randint(1, 2)
        procs.append(Process(f"P{i+1}", arr, burst, pri, "batch"))
    # 18 high-pri interactive arriving steadily
    for i in range(6, 24):
        arr = (i - 5) * 5 + rng.randint(-1, 1)
        burst = rng.randint(5, 9)
        pri = rng.randint(8, 10)
        procs.append(Process(f"P{i+1}", max(0, arr), burst, pri, "interactive"))
    procs.sort(key=lambda p: (p.arrival_time, int(p.pid[1:])))
    return procs

def generate_w4_burst_arrivals(seed: int = 1) -> List[Process]:
    """W4: Burst Arrivals (Offered Load ~2.40). 3 clusters of 7 jobs at t=0, 40, 80."""
    rng = random.Random(seed + 400)
    procs = []
    cluster_centers = [0, 40, 80]
    idx = 1
    for center in cluster_centers:
        for _ in range(7):
            arr = center + rng.randint(0, 3)
            burst = rng.randint(3, 15)
            pri = rng.randint(2, 9)
            wclass = rng.choice(["interactive", "mixed", "batch"])
            procs.append(Process(f"P{idx}", arr, burst, pri, wclass))
            idx += 1
    procs.sort(key=lambda p: (p.arrival_time, int(p.pid[1:])))
    return procs

def generate_w5_share_imbalance(seed: int = 1) -> List[Process]:
    """W5: Share Imbalance (Offered Load ~3.00). 3 huge batch jobs competing with 12 light jobs."""
    rng = random.Random(seed + 500)
    procs = []
    # 3 long high-pri batch
    for i in range(3):
        arr = rng.randint(0, 10)
        burst = rng.randint(60, 90)
        pri = rng.randint(8, 10)
        procs.append(Process(f"P{i+1}", arr, burst, pri, "batch"))
    # 12 light interactive jobs
    for i in range(3, 15):
        arr = rng.randint(0, 100)
        burst = rng.randint(2, 6)
        pri = rng.randint(4, 7)
        procs.append(Process(f"P{i+1}", arr, burst, pri, "interactive"))
    procs.sort(key=lambda p: (p.arrival_time, int(p.pid[1:])))
    return procs

def get_workload_generator(name: str):
    """Maps name to generator function."""
    mapping = {
        "W1": generate_w1_uniform,
        "W2": generate_w2_mixed,
        "W3": generate_w3_priority_skew,
        "W4": generate_w4_burst_arrivals,
        "W5": generate_w5_share_imbalance
    }
    if name not in mapping:
        raise ValueError(f"Unknown workload identifier: {name}")
    return mapping[name]
