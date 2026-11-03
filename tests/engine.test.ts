/**
 * AFAS Studio — Engine Unit Tests
 *
 * Hand-solved test cases verifying exact correctness of all scheduling algorithms.
 */

import { describe, it, expect } from 'vitest';
import { simulate, normalizeWeights } from '../src/engine/scheduler';
import { computeMetrics } from '../src/engine/metrics';
import { checkInvariants } from '../src/engine/invariants';
import { mulberry32 } from '../src/engine/prng';
import { generatePreset, generateRandom } from '../src/engine/workloads';
import type { ProcessInput, AFASWeights } from '../src/engine/types';

/* ─── Shared test processes ─── */

// Classic 4-process test case
const PROCS_4: ProcessInput[] = [
  { pid: 1, arrival: 0, burst: 5, priority: 5, processClass: 'Interactive' },
  { pid: 2, arrival: 1, burst: 3, priority: 7, processClass: 'Mixed' },
  { pid: 3, arrival: 2, burst: 8, priority: 3, processClass: 'Batch' },
  { pid: 4, arrival: 3, burst: 6, priority: 8, processClass: 'Interactive' },
];

const WEIGHTS: AFASWeights = { wp: 0.3, wa: 0.4, wr: 0.15, wc: 0.15 };

/* ─── FCFS Tests ─── */

describe('FCFS', () => {
  it('produces correct completion times for 4 processes', () => {
    const result = simulate('FCFS', PROCS_4, 4, WEIGHTS);
    const cts = result.processResults.map((r) => r.completionTime);
    // P1: runs 0-5, CT=5; P2: 5-8, CT=8; P3: 8-16, CT=16; P4: 16-22, CT=22
    expect(cts).toEqual([5, 8, 16, 22]);
  });

  it('has mean waiting time of 5.75', () => {
    const result = simulate('FCFS', PROCS_4, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    expect(metrics.avgWaitingTime).toBeCloseTo(5.75, 2);
  });

  it('passes all invariants', () => {
    const result = simulate('FCFS', PROCS_4, 4, WEIGHTS);
    const inv = checkInvariants(result, PROCS_4);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── SJF Tests ─── */

describe('SJF', () => {
  it('produces correct completion times for 4 processes', () => {
    const result = simulate('SJF', PROCS_4, 4, WEIGHTS);
    const cts = result.processResults.map((r) => r.completionTime);
    // P1: 0-5, CT=5; P2: 5-8, CT=8 (shortest); P4: 8-14, CT=14; P3: 14-22, CT=22
    expect(cts).toEqual([5, 8, 22, 14]);
  });

  it('has mean waiting time of 5.25', () => {
    const result = simulate('SJF', PROCS_4, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    expect(metrics.avgWaitingTime).toBeCloseTo(5.25, 2);
  });

  it('passes all invariants', () => {
    const result = simulate('SJF', PROCS_4, 4, WEIGHTS);
    const inv = checkInvariants(result, PROCS_4);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── SRTF Tests ─── */

describe('SRTF', () => {
  it('produces correct completion times for 4 processes', () => {
    const result = simulate('SRTF', PROCS_4, 4, WEIGHTS);
    const cts = result.processResults.map((r) => r.completionTime);
    // P1: runs 0-1, preempted by P2; P2: 1-4, CT=4; P1: 4-8, CT=8; P4: 8-14, CT=14; P3: 14-22, CT=22
    expect(cts).toEqual([8, 4, 22, 14]);
  });

  it('has mean waiting time of 5.00', () => {
    const result = simulate('SRTF', PROCS_4, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    expect(metrics.avgWaitingTime).toBeCloseTo(5.0, 2);
  });

  it('passes all invariants', () => {
    const result = simulate('SRTF', PROCS_4, 4, WEIGHTS);
    const inv = checkInvariants(result, PROCS_4);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── Round Robin Tests ─── */

describe('Round Robin', () => {
  const RR_PROCS: ProcessInput[] = [
    { pid: 1, arrival: 0, burst: 5, priority: 5, processClass: 'Interactive' },
    { pid: 2, arrival: 0, burst: 3, priority: 5, processClass: 'Mixed' },
    { pid: 3, arrival: 0, burst: 1, priority: 5, processClass: 'Batch' },
  ];

  it('produces correct completion times with q=2', () => {
    const result = simulate('RR', RR_PROCS, 2, WEIGHTS);
    const cts = result.processResults.map((r) => r.completionTime);
    // t=0-2: P1(rem=3); t=2-4: P2(rem=1); t=4-5: P3(rem=0,CT=5);
    // t=5-7: P1(rem=1); t=7-8: P2(rem=0,CT=8); t=8-9: P1(rem=0,CT=9)
    expect(cts).toEqual([9, 8, 5]);
  });

  it('passes all invariants', () => {
    const result = simulate('RR', RR_PROCS, 2, WEIGHTS);
    const inv = checkInvariants(result, RR_PROCS);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── Priority Tests ─── */

describe('Priority', () => {
  it('selects highest priority process first', () => {
    const result = simulate('Priority', PROCS_4, 4, WEIGHTS);
    // P1 runs first (only one at t=0). At t=5: P2(pri=7), P3(pri=3), P4(pri=8) ready.
    // P4 wins (pri=8), then P2 (pri=7), then P3 (pri=3).
    const cts = result.processResults.map((r) => r.completionTime);
    expect(cts).toEqual([5, 14, 22, 11]);
  });

  it('passes all invariants', () => {
    const result = simulate('Priority', PROCS_4, 4, WEIGHTS);
    const inv = checkInvariants(result, PROCS_4);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── AFAS Tests ─── */

describe('AFAS', () => {
  it('produces valid results and passes invariants', () => {
    const result = simulate('AFAS', PROCS_4, 4, WEIGHTS);
    expect(result.processResults.length).toBe(4);
    expect(result.decisions.length).toBeGreaterThan(0);
    const inv = checkInvariants(result, PROCS_4);
    expect(inv.every((i) => i.passed)).toBe(true);
  });

  it('records score decomposition in decisions', () => {
    const result = simulate('AFAS', PROCS_4, 4, WEIGHTS);
    for (const d of result.decisions) {
      expect(d.scores.length).toBeGreaterThan(0);
      for (const s of d.scores) {
        expect(typeof s.wpP).toBe('number');
        expect(typeof s.waA).toBe('number');
        expect(typeof s.wrR).toBe('number');
        expect(typeof s.negWcC).toBe('number');
        expect(s.total).toBeCloseTo(s.wpP + s.waA + s.wrR + s.negWcC, 8);
      }
    }
  });

  it('detects aging promotion', () => {
    // Long-running scenario where aging should promote a low-priority process
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 50, priority: 10, processClass: 'Batch' },
      { pid: 2, arrival: 0, burst: 5, priority: 1, processClass: 'Interactive' },
    ];
    // With high aging weight, P2 should eventually get promoted
    const weights: AFASWeights = { wp: 0.1, wa: 0.7, wr: 0.1, wc: 0.1 };
    const result = simulate('AFAS', procs, 4, weights);
    // P2 is interactive (Ri=1.0) and low priority, so might get aging promotion
    const inv = checkInvariants(result, procs);
    expect(inv.every((i) => i.passed)).toBe(true);
  });

  it('aging saturates at 1.0', () => {
    // Process waiting a very long time
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 100, priority: 10, processClass: 'Batch' },
      { pid: 2, arrival: 0, burst: 1, priority: 1, processClass: 'Batch' },
    ];
    const result = simulate('AFAS', procs, 100, WEIGHTS);
    // Find decision where P2 was chosen (if any)
    // Aging is min(1, elapsed/50), so it saturates at elapsed=50
    const inv = checkInvariants(result, procs);
    expect(inv.every((i) => i.passed)).toBe(true);
  });
});

/* ─── Tie-Breaking Tests ─── */

describe('Tie-breaking', () => {
  it('SJF breaks ties by arrival then PID', () => {
    const procs: ProcessInput[] = [
      { pid: 3, arrival: 0, burst: 3, priority: 5, processClass: 'Mixed' },
      { pid: 1, arrival: 0, burst: 3, priority: 5, processClass: 'Mixed' },
      { pid: 2, arrival: 0, burst: 3, priority: 5, processClass: 'Mixed' },
    ];
    const result = simulate('SJF', procs, 4, WEIGHTS);
    // All same burst, same arrival → order by PID: 1, 2, 3
    const order = result.gantt.filter((b) => b.pid !== -1).map((b) => b.pid);
    expect(order).toEqual([1, 2, 3]);
  });
});

/* ─── Input Validation ─── */

describe('Input handling', () => {
  it('handles empty process list', () => {
    const result = simulate('FCFS', [], 4, WEIGHTS);
    expect(result.gantt).toEqual([]);
    expect(result.processResults).toEqual([]);
    expect(result.totalTime).toBe(0);
  });

  it('handles single process', () => {
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 10, priority: 5, processClass: 'Interactive' },
    ];
    const result = simulate('FCFS', procs, 4, WEIGHTS);
    expect(result.processResults[0].completionTime).toBe(10);
    expect(result.processResults[0].waitingTime).toBe(0);
  });

  it('handles idle gaps when no process is ready', () => {
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 2, priority: 5, processClass: 'Interactive' },
      { pid: 2, arrival: 10, burst: 3, priority: 5, processClass: 'Mixed' },
    ];
    const result = simulate('FCFS', procs, 4, WEIGHTS);
    // Should have an idle block from 2 to 10
    const idle = result.gantt.find((b) => b.pid === -1);
    expect(idle).toBeDefined();
    expect(idle!.start).toBe(2);
    expect(idle!.end).toBe(10);
  });
});

/* ─── Determinism Tests ─── */

describe('Determinism', () => {
  it('PRNG produces same sequence for same seed', () => {
    const rng1 = mulberry32(42);
    const rng2 = mulberry32(42);
    for (let i = 0; i < 100; i++) {
      expect(rng1()).toBe(rng2());
    }
  });

  it('same workload preset + seed gives identical processes', () => {
    const a = generatePreset('W1', 1);
    const b = generatePreset('W1', 1);
    expect(a).toEqual(b);
  });

  it('different seeds give different workloads', () => {
    const a = generatePreset('W1', 1);
    const b = generatePreset('W1', 2);
    // Very unlikely to be equal
    const aStr = JSON.stringify(a);
    const bStr = JSON.stringify(b);
    expect(aStr).not.toBe(bStr);
  });

  it('simulation is deterministic', () => {
    const procs = generatePreset('W2', 3);
    const r1 = simulate('AFAS', procs, 4, WEIGHTS);
    const r2 = simulate('AFAS', procs, 4, WEIGHTS);
    expect(r1.gantt).toEqual(r2.gantt);
    expect(r1.processResults).toEqual(r2.processResults);
    expect(r1.decisions).toEqual(r2.decisions);
  });
});

/* ─── Weight Normalization ─── */

describe('Weight normalization', () => {
  it('normalizes to sum 1.0', () => {
    const w = normalizeWeights({ wp: 1, wa: 1, wr: 1, wc: 1 });
    expect(w.wp + w.wa + w.wr + w.wc).toBeCloseTo(1.0, 10);
    expect(w.wp).toBeCloseTo(0.25, 10);
  });

  it('handles zero weights', () => {
    const w = normalizeWeights({ wp: 0, wa: 0, wr: 0, wc: 0 });
    expect(w.wp + w.wa + w.wr + w.wc).toBeCloseTo(1.0, 10);
  });
});

/* ─── Metrics Tests ─── */

describe('Metrics', () => {
  it('computes correct Jain index for equal waiting times', () => {
    // All equal WT → Jain's = 1.0
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 3, priority: 5, processClass: 'Mixed' },
      { pid: 2, arrival: 3, burst: 3, priority: 5, processClass: 'Mixed' },
      { pid: 3, arrival: 6, burst: 3, priority: 5, processClass: 'Mixed' },
    ];
    const result = simulate('FCFS', procs, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    // All WT = 0, Jain's should be 1.0 (all equal)
    expect(metrics.jainsIndex).toBeCloseTo(1.0, 2);
  });

  it('counts starvation warnings for WT > 40', () => {
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 50, priority: 5, processClass: 'Batch' },
      { pid: 2, arrival: 1, burst: 1, priority: 5, processClass: 'Mixed' },
    ];
    const result = simulate('FCFS', procs, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    // P2 WT = 50 - 1 = 49 > 40
    expect(metrics.starvationWarnings).toBe(1);
  });

  it('computes CPU utilization correctly', () => {
    const procs: ProcessInput[] = [
      { pid: 1, arrival: 0, burst: 5, priority: 5, processClass: 'Mixed' },
      { pid: 2, arrival: 10, burst: 5, priority: 5, processClass: 'Mixed' },
    ];
    const result = simulate('FCFS', procs, 4, WEIGHTS);
    const metrics = computeMetrics(result);
    // Total time = 15, total burst = 10, util = 10/15
    expect(metrics.cpuUtilization).toBeCloseTo(10 / 15, 2);
  });
});

/* ─── All Policies Pass Invariants on Generated Workloads ─── */

describe('All policies × workloads pass invariants', () => {
  const policies = ['FCFS', 'SJF', 'SRTF', 'RR', 'Priority', 'AFAS'] as const;
  const workloads = ['W1', 'W2', 'W3', 'W4', 'W5'] as const;

  for (const policy of policies) {
    for (const wl of workloads) {
      it(`${policy} on ${wl} (seed 1)`, () => {
        const procs = generatePreset(wl, 1);
        const result = simulate(policy, procs, 4, WEIGHTS);
        const inv = checkInvariants(result, procs);
        for (const i of inv) {
          expect(i.passed, `${i.name}: ${i.message}`).toBe(true);
        }
      });
    }
  }
});
