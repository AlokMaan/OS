"""
test_sim.py - Automated Pytest Unit and Regression Test Suite for AFAS Simulator
Validates analytical hand-solved baselines, engine invariants, and boundary conditions.
"""

import pytest
from afas_sim import (
    Process, Segment, validate_workload, verify_engine_invariants,
    run_fcfs, run_sjf, run_srtf, run_round_robin, run_priority, run_afas,
    compute_metrics, get_workload_generator
)

# 1. Analytical Hand-Solved Case: P1(0, 5), P2(1, 3), P3(2, 8), P4(3, 6)
@pytest.fixture
def textbook_workload():
    return [
        Process("P1", arrival_time=0, burst_time=5, priority=5, workload_class="mixed"),
        Process("P2", arrival_time=1, burst_time=3, priority=5, workload_class="mixed"),
        Process("P3", arrival_time=2, burst_time=8, priority=5, workload_class="mixed"),
        Process("P4", arrival_time=3, burst_time=6, priority=5, workload_class="mixed"),
    ]

def test_fcfs_hand_solved(textbook_workload):
    """Verifies FCFS against analytical hand solution: CT = [5, 8, 16, 22], Mean WT = 5.75."""
    segments = run_fcfs(textbook_workload)
    metrics = compute_metrics(textbook_workload, segments)
    
    # Calculate completion times from segments
    ct = {p.pid: None for p in textbook_workload}
    for s in segments:
        ct[s.pid] = s.end
        
    assert ct["P1"] == 5
    assert ct["P2"] == 8
    assert ct["P3"] == 16
    assert ct["P4"] == 22
    assert pytest.approx(metrics["avg_wt"], 0.01) == 5.75

def test_sjf_hand_solved(textbook_workload):
    """Verifies Non-preemptive SJF against analytical hand solution: CT = [5, 8, 22, 14], Mean WT = 5.25."""
    segments = run_sjf(textbook_workload)
    metrics = compute_metrics(textbook_workload, segments)
    
    ct = {p.pid: None for p in textbook_workload}
    for s in segments:
        ct[s.pid] = s.end
        
    assert ct["P1"] == 5
    assert ct["P2"] == 8
    assert ct["P3"] == 22
    assert ct["P4"] == 14
    assert pytest.approx(metrics["avg_wt"], 0.01) == 5.25

def test_srtf_hand_solved(textbook_workload):
    """Verifies Preemptive SRTF against analytical hand solution: CT = [8, 4, 22, 14], Mean WT = 5.00."""
    segments = run_srtf(textbook_workload)
    metrics = compute_metrics(textbook_workload, segments)
    
    ct = {p.pid: None for p in textbook_workload}
    for s in segments:
        ct[s.pid] = s.end
        
    assert ct["P1"] == 8
    assert ct["P2"] == 4
    assert ct["P3"] == 22
    assert ct["P4"] == 14
    assert pytest.approx(metrics["avg_wt"], 0.01) == 5.00

def test_round_robin_hand_solved():
    """Verifies Round Robin (q=2) on 3 processes arriving at 0: P1(0,4), P2(0,3), P3(0,2)."""
    procs = [
        Process("P1", arrival_time=0, burst_time=4, priority=5),
        Process("P2", arrival_time=0, burst_time=3, priority=5),
        Process("P3", arrival_time=0, burst_time=2, priority=5)
    ]
    segments = run_round_robin(procs, quantum=2)
    metrics = compute_metrics(procs, segments)
    
    ct = {p.pid: None for p in procs}
    for s in segments:
        ct[s.pid] = s.end
        
    # Schedule: P1(0-2), P2(2-4), P3(4-6, finishes), P1(6-8, finishes), P2(8-9, finishes)
    assert ct["P3"] == 6
    assert ct["P1"] == 8
    assert ct["P2"] == 9
    # WT: P1: 8-4=4, P2: 9-3=6, P3: 6-2=4 => Mean WT = (4+6+4)/3 = 4.67
    assert metrics["ctx_switches"] == 4

def test_priority_hand_solved():
    """Verifies static Priority scheduling dispatches strictly in priority order."""
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=0, burst_time=3, priority=9),
        Process("P3", arrival_time=0, burst_time=4, priority=6)
    ]
    segments = run_priority(procs)
    order = [s.pid for s in segments]
    assert order == ["P2", "P3", "P1"]

def test_idle_gap_handling():
    """Verifies policies handle workloads with idle gaps between process arrivals."""
    procs = [
        Process("P1", arrival_time=0, burst_time=4, priority=5),
        Process("P2", arrival_time=15, burst_time=3, priority=5)
    ]
    for runner in [run_fcfs, run_sjf, run_srtf, run_round_robin, run_priority]:
        segs = runner(procs)
        verify_engine_invariants(procs, segs)
        assert segs[0].end == 4
        assert segs[1].start == 15
        assert segs[1].end == 18
        
    afas_segs, _ = run_afas(procs)
    verify_engine_invariants(procs, afas_segs)
    assert afas_segs[0].end == 4
    assert afas_segs[1].start == 15

def test_engine_invariants_all_workloads():
    """Checks Invariants 1, 2, and 3 across all 25 workload instances for AFAS and baselines."""
    for wname in ["W1", "W2", "W3", "W4", "W5"]:
        gen = get_workload_generator(wname)
        for seed in range(1, 6):
            procs = gen(seed)
            # Run AFAS and Round Robin
            afas_segs, _ = run_afas(procs, quantum=4)
            verify_engine_invariants(procs, afas_segs)
            rr_segs = run_round_robin(procs, quantum=4)
            verify_engine_invariants(procs, rr_segs)

def test_deterministic_reproducibility():
    """Checks that identical random seed and workload produce 100% identical AFAS schedules."""
    gen = get_workload_generator("W3")
    procs1 = gen(seed=42)
    procs2 = gen(seed=42)
    
    segs1, log1 = run_afas(procs1, quantum=4)
    segs2, log2 = run_afas(procs2, quantum=4)
    
    assert len(segs1) == len(segs2)
    for s1, s2 in zip(segs1, segs2):
        assert s1.pid == s2.pid and s1.start == s2.start and s1.end == s2.end
    assert len(log1) == len(log2)

def test_afas_tie_breaking_order():
    """Verifies deterministic tie-breaking hierarchy: higher score, earlier arrival, lower PID."""
    procs = [
        Process("P_B", arrival_time=0, burst_time=4, priority=5, workload_class="mixed"),
        Process("P_A", arrival_time=0, burst_time=4, priority=5, workload_class="mixed")
    ]
    # At t=0, both have identical score and arrival => lower PID P_A must execute first
    segs, log = run_afas(procs, quantum=4)
    assert segs[0].pid == "P_A"
    assert segs[1].pid == "P_B"

def test_input_validation_rejections():
    """Checks that malformed workloads raise appropriate ValueError exceptions."""
    with pytest.raises(ValueError):
        validate_workload([])  # Empty
    with pytest.raises(ValueError):
        validate_workload([Process("P1", arrival_time=-1, burst_time=5, priority=5)])  # Negative arrival
    with pytest.raises(ValueError):
        validate_workload([Process("P1", arrival_time=0, burst_time=0, priority=5)])  # Zero burst
    with pytest.raises(ValueError):
        validate_workload([
            Process("P1", arrival_time=0, burst_time=5, priority=5),
            Process("P1", arrival_time=2, burst_time=4, priority=5)
        ])  # Duplicate PID
    with pytest.raises(ValueError):
        validate_workload([Process("P1", arrival_time=0, burst_time=5, priority=12)])  # Priority > 10
    with pytest.raises(ValueError):
        validate_workload([Process("P1", arrival_time=0, burst_time=5, priority=5, workload_class="invalid")])

def test_aging_bounds_and_saturation():
    """Checks that the waiting age term saturates at 1.0 when wait time exceeds 50 units."""
    p = Process("P_low", arrival_time=0, burst_time=10, priority=1, workload_class="batch")
    from afas_sim import compute_afas_score
    
    # At t=0: wait=0 => A=0.0
    _, _, wA_0, _, _ = compute_afas_score(p, current_time=0, wp=0.25, wa=0.25, wr=0.25, wc=0.25)
    assert pytest.approx(wA_0, 0.001) == 0.0
    
    # At t=25: wait=25 => A = 25/50 = 0.5 => wA = 0.25 * 0.5 = 0.125
    _, _, wA_25, _, _ = compute_afas_score(p, current_time=25, wp=0.25, wa=0.25, wr=0.25, wc=0.25)
    assert pytest.approx(wA_25, 0.001) == 0.125
    
    # At t=50: wait=50 => A = 1.0 => wA = 0.25
    _, _, wA_50, _, _ = compute_afas_score(p, current_time=50, wp=0.25, wa=0.25, wr=0.25, wc=0.25)
    assert pytest.approx(wA_50, 0.001) == 0.25
    
    # At t=100: wait=100 => A still saturated at 1.0 => wA = 0.25
    _, _, wA_100, _, _ = compute_afas_score(p, current_time=100, wp=0.25, wa=0.25, wr=0.25, wc=0.25)
    assert pytest.approx(wA_100, 0.001) == 0.25

def test_afas_starvation_mitigation():
    """Verifies AFAS significantly bounds maximum wait compared to static Priority on W3 skew."""
    gen = get_workload_generator("W3")
    procs = gen(seed=1)
    
    pri_segs = run_priority(procs)
    pri_metrics = compute_metrics(procs, pri_segs)
    
    afas_segs, _ = run_afas(procs, quantum=4)
    afas_metrics = compute_metrics(procs, afas_segs)
    
    # AFAS must achieve lower max wait gap than Priority on the skewed workload
    assert afas_metrics["max_wait_gap"] < pri_metrics["max_wait_gap"]
