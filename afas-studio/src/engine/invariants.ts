/**
 * Post-simulation invariant checks.
 *
 * Three invariants enforced after every run:
 *   1. Non-overlap — no two Gantt blocks overlap.
 *   2. Burst conservation — total CPU time per process equals its burst.
 *   3. No execution before arrival — every block starts ≥ process arrival.
 */

import type { ProcessInput, SimulationResult, InvariantResult } from './types';

export function checkInvariants(
  result: SimulationResult,
  inputs: ProcessInput[],
): InvariantResult[] {
  const results: InvariantResult[] = [];

  // 1. Non-overlap
  {
    const blocks = result.gantt.filter((b) => b.pid !== -1);
    let passed = true;
    let msg = 'No overlapping Gantt blocks detected.';
    const sorted = [...blocks].sort((a, b) => a.start - b.start || a.end - b.end);
    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i].start < sorted[i - 1].end) {
        passed = false;
        msg = `Overlap: block [${sorted[i - 1].start},${sorted[i - 1].end}) and [${sorted[i].start},${sorted[i].end})`;
        break;
      }
    }
    results.push({ name: 'Non-Overlap', passed, message: msg });
  }

  // 2. Burst conservation
  {
    const cpuMap = new Map<number, number>();
    for (const b of result.gantt) {
      if (b.pid === -1) continue;
      cpuMap.set(b.pid, (cpuMap.get(b.pid) ?? 0) + (b.end - b.start));
    }
    let passed = true;
    let msg = 'Total CPU time per process matches burst length.';
    for (const p of inputs) {
      const actual = cpuMap.get(p.pid) ?? 0;
      if (Math.abs(actual - p.burst) > 1e-9) {
        passed = false;
        msg = `PID ${p.pid}: expected burst ${p.burst}, got ${actual}`;
        break;
      }
    }
    results.push({ name: 'Burst Conservation', passed, message: msg });
  }

  // 3. No execution before arrival
  {
    const arrMap = new Map<number, number>();
    for (const p of inputs) arrMap.set(p.pid, p.arrival);
    let passed = true;
    let msg = 'No process executes before its arrival time.';
    for (const b of result.gantt) {
      if (b.pid === -1) continue;
      const arr = arrMap.get(b.pid);
      if (arr !== undefined && b.start < arr) {
        passed = false;
        msg = `PID ${b.pid}: executes at t=${b.start} but arrives at t=${arr}`;
        break;
      }
    }
    results.push({ name: 'No Pre-Arrival Execution', passed, message: msg });
  }

  return results;
}
