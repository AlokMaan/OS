/**
 * AFAS Studio — CPU Scheduling Engine
 *
 * Implements six scheduling policies:
 *   FCFS, SJF (non-preemptive), SRTF, RR, Priority (non-preemptive), AFAS.
 *
 * All functions are pure — no side-effects, deterministic output.
 */

import type {
  ProcessInput,
  GanttBlock,
  ProcessResult,
  SimulationResult,
  AFASDecision,
  AFASScoreEntry,
  AFASWeights,
  Policy,
  ProcessClass,
} from './types';

/* ──────────────────────── Helpers ──────────────────────── */

/** Merge adjacent Gantt blocks with the same PID. */
function mergeGantt(blocks: GanttBlock[]): GanttBlock[] {
  if (blocks.length === 0) return [];
  const merged: GanttBlock[] = [{ ...blocks[0] }];
  for (let i = 1; i < blocks.length; i++) {
    const last = merged[merged.length - 1];
    if (blocks[i].pid === last.pid && blocks[i].start === last.end) {
      last.end = blocks[i].end;
    } else {
      merged.push({ ...blocks[i] });
    }
  }
  return merged;
}

/** Build ProcessResult array from completion data. */
function buildResults(
  procs: ProcessInput[],
  ct: number[],
  firstRun: number[],
): ProcessResult[] {
  return procs.map((p, i) => ({
    pid: p.pid,
    arrival: p.arrival,
    burst: p.burst,
    priority: p.priority,
    processClass: p.processClass,
    completionTime: ct[i],
    turnaroundTime: ct[i] - p.arrival,
    waitingTime: ct[i] - p.arrival - p.burst,
    responseTime: firstRun[i] - p.arrival,
  }));
}

/** Normalize AFAS weights to sum to 1.0. */
export function normalizeWeights(w: AFASWeights): AFASWeights {
  const sum = w.wp + w.wa + w.wr + w.wc;
  if (sum === 0) return { wp: 0.25, wa: 0.25, wr: 0.25, wc: 0.25 };
  return {
    wp: w.wp / sum,
    wa: w.wa / sum,
    wr: w.wr / sum,
    wc: w.wc / sum,
  };
}

/* ──────────────────── FCFS ──────────────────── */

function simulateFCFS(procs: ProcessInput[]): SimulationResult {
  const n = procs.length;
  // Sort by arrival, then PID for tie-break
  const indices = Array.from({ length: n }, (_, i) => i);
  indices.sort((a, b) => {
    if (procs[a].arrival !== procs[b].arrival) return procs[a].arrival - procs[b].arrival;
    return procs[a].pid - procs[b].pid;
  });

  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(0);
  const gantt: GanttBlock[] = [];
  let t = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  for (const idx of indices) {
    const p = procs[idx];
    if (t < p.arrival) {
      gantt.push({ pid: -1, start: t, end: p.arrival });
      t = p.arrival;
    }
    if (prevPid !== -1 && prevPid !== p.pid) contextSwitches++;
    prevPid = p.pid;
    firstRun[idx] = t;
    gantt.push({ pid: p.pid, start: t, end: t + p.burst });
    t += p.burst;
    ct[idx] = t;
  }

  return {
    policy: 'FCFS',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions: [],
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── SJF (Non-Preemptive) ──────────────────── */

function simulateSJF(procs: ProcessInput[]): SimulationResult {
  const n = procs.length;
  const remaining = procs.map((p) => p.burst);
  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(-1);
  const gantt: GanttBlock[] = [];
  let t = 0;
  let completed = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  while (completed < n) {
    // Ready processes
    let bestIdx = -1;
    let bestBurst = Infinity;
    for (let i = 0; i < n; i++) {
      if (remaining[i] > 0 && procs[i].arrival <= t) {
        if (
          procs[i].burst < bestBurst ||
          (procs[i].burst === bestBurst && procs[i].arrival < procs[bestIdx].arrival) ||
          (procs[i].burst === bestBurst &&
            procs[i].arrival === procs[bestIdx].arrival &&
            procs[i].pid < procs[bestIdx].pid)
        ) {
          bestIdx = i;
          bestBurst = procs[i].burst;
        }
      }
    }

    if (bestIdx === -1) {
      // Advance to next arrival
      let nextArr = Infinity;
      for (let i = 0; i < n; i++) {
        if (remaining[i] > 0 && procs[i].arrival > t) {
          nextArr = Math.min(nextArr, procs[i].arrival);
        }
      }
      if (nextArr === Infinity) break;
      gantt.push({ pid: -1, start: t, end: nextArr });
      t = nextArr;
      continue;
    }

    if (prevPid !== -1 && prevPid !== procs[bestIdx].pid) contextSwitches++;
    prevPid = procs[bestIdx].pid;
    firstRun[bestIdx] = t;
    gantt.push({ pid: procs[bestIdx].pid, start: t, end: t + procs[bestIdx].burst });
    t += procs[bestIdx].burst;
    remaining[bestIdx] = 0;
    ct[bestIdx] = t;
    completed++;
  }

  return {
    policy: 'SJF',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions: [],
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── SRTF (Preemptive SJF) ──────────────────── */

function simulateSRTF(procs: ProcessInput[]): SimulationResult {
  const n = procs.length;
  const remaining = procs.map((p) => p.burst);
  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(-1);
  const gantt: GanttBlock[] = [];
  let t = 0;
  let completed = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  while (completed < n) {
    // Find best ready process by shortest remaining
    let bestIdx = -1;
    let bestRem = Infinity;
    for (let i = 0; i < n; i++) {
      if (remaining[i] > 0 && procs[i].arrival <= t) {
        if (
          remaining[i] < bestRem ||
          (remaining[i] === bestRem && bestIdx >= 0 && procs[i].arrival < procs[bestIdx].arrival) ||
          (remaining[i] === bestRem &&
            bestIdx >= 0 &&
            procs[i].arrival === procs[bestIdx].arrival &&
            procs[i].pid < procs[bestIdx].pid)
        ) {
          bestIdx = i;
          bestRem = remaining[i];
        }
      }
    }

    if (bestIdx === -1) {
      let nextArr = Infinity;
      for (let i = 0; i < n; i++) {
        if (remaining[i] > 0 && procs[i].arrival > t) nextArr = Math.min(nextArr, procs[i].arrival);
      }
      if (nextArr === Infinity) break;
      gantt.push({ pid: -1, start: t, end: nextArr });
      t = nextArr;
      continue;
    }

    if (prevPid !== -1 && prevPid !== procs[bestIdx].pid) contextSwitches++;
    prevPid = procs[bestIdx].pid;
    if (firstRun[bestIdx] === -1) firstRun[bestIdx] = t;

    // Run until next arrival or completion
    let nextEvent = t + remaining[bestIdx];
    for (let i = 0; i < n; i++) {
      if (remaining[i] > 0 && procs[i].arrival > t && procs[i].arrival < nextEvent) {
        nextEvent = procs[i].arrival;
      }
    }

    const dur = nextEvent - t;
    gantt.push({ pid: procs[bestIdx].pid, start: t, end: nextEvent });
    remaining[bestIdx] -= dur;
    t = nextEvent;

    if (remaining[bestIdx] === 0) {
      ct[bestIdx] = t;
      completed++;
    }
  }

  return {
    policy: 'SRTF',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions: [],
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── Round Robin ──────────────────── */

function simulateRR(procs: ProcessInput[], quantum: number): SimulationResult {
  const n = procs.length;
  const remaining = procs.map((p) => p.burst);
  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(-1);
  const gantt: GanttBlock[] = [];
  let t = 0;
  let completed = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  // Ready queue holds indices
  const queue: number[] = [];
  const inQueue = new Array<boolean>(n).fill(false);

  // Sort by arrival then PID for initial ordering
  const arrivalOrder = Array.from({ length: n }, (_, i) => i);
  arrivalOrder.sort((a, b) => {
    if (procs[a].arrival !== procs[b].arrival) return procs[a].arrival - procs[b].arrival;
    return procs[a].pid - procs[b].pid;
  });

  let nextToArrive = 0;

  // Add processes arriving at t=0
  const addArrivals = (time: number) => {
    while (nextToArrive < n && procs[arrivalOrder[nextToArrive]].arrival <= time) {
      const idx = arrivalOrder[nextToArrive];
      if (!inQueue[idx] && remaining[idx] > 0) {
        queue.push(idx);
        inQueue[idx] = true;
      }
      nextToArrive++;
    }
  };

  addArrivals(t);

  while (completed < n) {
    if (queue.length === 0) {
      // Find next arrival
      let nextArr = Infinity;
      for (let i = 0; i < n; i++) {
        if (remaining[i] > 0 && procs[i].arrival > t) nextArr = Math.min(nextArr, procs[i].arrival);
      }
      if (nextArr === Infinity) break;
      gantt.push({ pid: -1, start: t, end: nextArr });
      t = nextArr;
      // Reset nextToArrive to scan again from the beginning
      nextToArrive = 0;
      for (let i = 0; i < n; i++) inQueue[i] = remaining[i] <= 0;
      addArrivals(t);
      continue;
    }

    const idx = queue.shift()!;
    inQueue[idx] = false;

    if (prevPid !== -1 && prevPid !== procs[idx].pid) contextSwitches++;
    prevPid = procs[idx].pid;
    if (firstRun[idx] === -1) firstRun[idx] = t;

    const runFor = Math.min(quantum, remaining[idx]);
    gantt.push({ pid: procs[idx].pid, start: t, end: t + runFor });
    remaining[idx] -= runFor;
    t += runFor;

    // Add new arrivals that came during this burst (before re-enqueuing current)
    addArrivals(t);

    if (remaining[idx] === 0) {
      ct[idx] = t;
      completed++;
    } else {
      queue.push(idx);
      inQueue[idx] = true;
    }
  }

  return {
    policy: 'RR',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions: [],
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── Priority (Non-Preemptive) ──────────────────── */

function simulatePriority(procs: ProcessInput[]): SimulationResult {
  const n = procs.length;
  const done = new Array<boolean>(n).fill(false);
  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(-1);
  const gantt: GanttBlock[] = [];
  let t = 0;
  let completed = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  while (completed < n) {
    let bestIdx = -1;
    let bestPri = -1;
    for (let i = 0; i < n; i++) {
      if (!done[i] && procs[i].arrival <= t) {
        if (
          procs[i].priority > bestPri ||
          (procs[i].priority === bestPri &&
            bestIdx >= 0 &&
            procs[i].arrival < procs[bestIdx].arrival) ||
          (procs[i].priority === bestPri &&
            bestIdx >= 0 &&
            procs[i].arrival === procs[bestIdx].arrival &&
            procs[i].pid < procs[bestIdx].pid)
        ) {
          bestIdx = i;
          bestPri = procs[i].priority;
        }
      }
    }

    if (bestIdx === -1) {
      let nextArr = Infinity;
      for (let i = 0; i < n; i++) {
        if (!done[i] && procs[i].arrival > t) nextArr = Math.min(nextArr, procs[i].arrival);
      }
      if (nextArr === Infinity) break;
      gantt.push({ pid: -1, start: t, end: nextArr });
      t = nextArr;
      continue;
    }

    if (prevPid !== -1 && prevPid !== procs[bestIdx].pid) contextSwitches++;
    prevPid = procs[bestIdx].pid;
    firstRun[bestIdx] = t;
    gantt.push({ pid: procs[bestIdx].pid, start: t, end: t + procs[bestIdx].burst });
    t += procs[bestIdx].burst;
    ct[bestIdx] = t;
    done[bestIdx] = true;
    completed++;
  }

  return {
    policy: 'Priority',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions: [],
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── AFAS ──────────────────── */

const CLASS_R: Record<ProcessClass, number> = {
  Interactive: 1.0,
  Mixed: 0.5,
  Batch: 0.2,
};

function simulateAFAS(
  procs: ProcessInput[],
  quantum: number,
  weights: AFASWeights,
): SimulationResult {
  const n = procs.length;
  const w = normalizeWeights(weights);
  const remaining = procs.map((p) => p.burst);
  const ct = new Array<number>(n).fill(0);
  const firstRun = new Array<number>(n).fill(-1);
  const gantt: GanttBlock[] = [];
  const decisions: AFASDecision[] = [];

  // Per-process AFAS state
  const lastExit = procs.map((p) => p.arrival); // when process last left CPU
  const service = new Array<number>(n).fill(0); // accumulated service
  const lastServiceUpdate = procs.map((p) => p.arrival);

  let t = 0;
  let completed = 0;
  let contextSwitches = 0;
  let prevPid = -1;

  while (completed < n) {
    // Collect ready indices
    const ready: number[] = [];
    for (let i = 0; i < n; i++) {
      if (remaining[i] > 0 && procs[i].arrival <= t) ready.push(i);
    }

    if (ready.length === 0) {
      let nextArr = Infinity;
      for (let i = 0; i < n; i++) {
        if (remaining[i] > 0 && procs[i].arrival > t) nextArr = Math.min(nextArr, procs[i].arrival);
      }
      if (nextArr === Infinity) break;
      gantt.push({ pid: -1, start: t, end: nextArr });
      t = nextArr;
      continue;
    }

    // Compute scores
    const scores: (AFASScoreEntry & { idx: number })[] = ready.map((idx) => {
      const p = procs[idx];
      const Pi = p.priority / 10;
      const Ai = Math.min(1, (t - lastExit[idx]) / 50);
      const Ri = CLASS_R[p.processClass];

      // Decay service to current time
      const elapsed = t - lastServiceUpdate[idx];
      const decayed = elapsed > 0 ? service[idx] * Math.pow(2, -elapsed / 40) : service[idx];
      const Ci = Math.min(1, decayed / 40);

      const wpP = w.wp * Pi;
      const waA = w.wa * Ai;
      const wrR = w.wr * Ri;
      const negWcC = -(w.wc * Ci);
      const total = wpP + waA + wrR + negWcC;

      return { idx, pid: p.pid, wpP, waA, wrR, negWcC, total };
    });

    // Sort: highest score → earliest arrival → lowest PID
    scores.sort((a, b) => {
      if (Math.abs(b.total - a.total) > 1e-12) return b.total - a.total;
      if (procs[a.idx].arrival !== procs[b.idx].arrival)
        return procs[a.idx].arrival - procs[b.idx].arrival;
      return a.pid - b.pid;
    });

    const chosen = scores[0];
    const chosenIdx = chosen.idx;

    // Aging promotion: chosen has lower base priority than someone else in the queue
    const maxPriInQueue = Math.max(...ready.map((i) => procs[i].priority));
    const isAgingPromotion = ready.length > 1 && procs[chosenIdx].priority < maxPriInQueue;

    if (firstRun[chosenIdx] === -1) firstRun[chosenIdx] = t;
    if (prevPid !== -1 && prevPid !== chosen.pid) contextSwitches++;
    prevPid = chosen.pid;

    // Dispatch for min(quantum, remaining)
    const runDur = Math.min(quantum, remaining[chosenIdx]);
    gantt.push({ pid: chosen.pid, start: t, end: t + runDur });

    // Update service with decay then add
    const sinceUpdate = t - lastServiceUpdate[chosenIdx];
    service[chosenIdx] =
      (sinceUpdate > 0
        ? service[chosenIdx] * Math.pow(2, -sinceUpdate / 40)
        : service[chosenIdx]) + runDur;
    lastServiceUpdate[chosenIdx] = t + runDur;

    remaining[chosenIdx] -= runDur;

    const action =
      remaining[chosenIdx] === 0
        ? 'COMPLETED'
        : isAgingPromotion
          ? 'AGING_PROMOTION'
          : 'QUANTUM_EXPIRED';

    decisions.push({
      time: t,
      chosenPid: chosen.pid,
      queueSize: ready.length,
      scores: scores.map((s) => ({
        pid: s.pid,
        wpP: s.wpP,
        waA: s.waA,
        wrR: s.wrR,
        negWcC: s.negWcC,
        total: s.total,
      })),
      action,
      isAgingPromotion,
    });

    lastExit[chosenIdx] = t + runDur;
    t += runDur;

    if (remaining[chosenIdx] === 0) {
      ct[chosenIdx] = t;
      completed++;
    }
  }

  return {
    policy: 'AFAS',
    gantt: mergeGantt(gantt),
    processResults: buildResults(procs, ct, firstRun),
    decisions,
    contextSwitches,
    totalTime: t,
  };
}

/* ──────────────────── Public API ──────────────────── */

export function simulate(
  policy: Policy,
  processes: ProcessInput[],
  quantum: number,
  weights: AFASWeights,
): SimulationResult {
  if (processes.length === 0) {
    return { policy, gantt: [], processResults: [], decisions: [], contextSwitches: 0, totalTime: 0 };
  }
  switch (policy) {
    case 'FCFS':
      return simulateFCFS(processes);
    case 'SJF':
      return simulateSJF(processes);
    case 'SRTF':
      return simulateSRTF(processes);
    case 'RR':
      return simulateRR(processes, quantum);
    case 'Priority':
      return simulatePriority(processes);
    case 'AFAS':
      return simulateAFAS(processes, quantum, weights);
  }
}


