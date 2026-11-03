/**
 * Metrics computation from simulation results.
 */

import type { ProcessResult, Metrics, SimulationResult } from './types';

/** Linear interpolation percentile (exclusive definition). */
function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  if (sorted.length === 1) return sorted[0];
  const rank = (p / 100) * (sorted.length - 1);
  const lo = Math.floor(rank);
  const hi = Math.ceil(rank);
  const frac = rank - lo;
  return sorted[lo] + frac * (sorted[hi] - sorted[lo]);
}

/** Median via linear interpolation. */
function median(sorted: number[]): number {
  return percentile(sorted, 50);
}

/**
 * Jain's Fairness Index computed over per-process normalized waiting time.
 * J = (Σ xi)^2 / (n · Σ xi^2)
 * where xi = WT_i / burst_i (normalized service — WT-based).
 * Perfect fairness = 1.0, worst = 1/n.
 */
function jainsIndex(results: ProcessResult[]): number {
  if (results.length <= 1) return 1.0;
  const xs = results.map((r) => (r.burst > 0 ? r.waitingTime / r.burst : 0));
  const sumX = xs.reduce((a, b) => a + b, 0);
  const sumX2 = xs.reduce((a, b) => a + b * b, 0);
  if (sumX2 === 0) return 1.0;
  return (sumX * sumX) / (results.length * sumX2);
}

export function computeMetrics(result: SimulationResult): Metrics {
  const pr = result.processResults;
  const n = pr.length;

  if (n === 0) {
    return {
      avgWaitingTime: 0,
      avgTurnaroundTime: 0,
      avgResponseTime: 0,
      medianResponseTime: 0,
      p95ResponseTime: 0,
      maxReadyQueueWait: 0,
      contextSwitches: 0,
      cpuUtilization: 0,
      throughput: 0,
      jainsIndex: 1,
      starvationWarnings: 0,
    };
  }

  const wts = pr.map((r) => r.waitingTime);
  const tats = pr.map((r) => r.turnaroundTime);
  const rts = pr.map((r) => r.responseTime);
  const sortedRTs = [...rts].sort((a, b) => a - b);

  const totalBurst = pr.reduce((s, r) => s + r.burst, 0);
  const totalTime = result.totalTime;
  const cpuUtil = totalTime > 0 ? totalBurst / totalTime : 0;

  return {
    avgWaitingTime: wts.reduce((a, b) => a + b, 0) / n,
    avgTurnaroundTime: tats.reduce((a, b) => a + b, 0) / n,
    avgResponseTime: rts.reduce((a, b) => a + b, 0) / n,
    medianResponseTime: median(sortedRTs),
    p95ResponseTime: percentile(sortedRTs, 95),
    maxReadyQueueWait: Math.max(...wts),
    contextSwitches: result.contextSwitches,
    cpuUtilization: cpuUtil,
    throughput: totalTime > 0 ? n / totalTime : 0,
    jainsIndex: jainsIndex(pr),
    starvationWarnings: wts.filter((w) => w > 40).length,
  };
}
