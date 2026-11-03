/* ── Process & Scheduling Types ── */

export type ProcessClass = 'Interactive' | 'Mixed' | 'Batch';

export type Policy = 'FCFS' | 'SJF' | 'SRTF' | 'RR' | 'Priority' | 'AFAS';

export const ALL_POLICIES: Policy[] = ['FCFS', 'SJF', 'SRTF', 'RR', 'Priority', 'AFAS'];

export const POLICY_LABELS: Record<Policy, string> = {
  FCFS: 'First Come First Served',
  SJF: 'Shortest Job First',
  SRTF: 'Shortest Remaining Time',
  RR: 'Round Robin',
  Priority: 'Priority (Non-Preemptive)',
  AFAS: 'AFAS (Adaptive Fairness)',
};

export const POLICY_COLORS: Record<Policy, string> = {
  FCFS: '#8b5cf6',
  SJF: '#3b82f6',
  SRTF: '#06b6d4',
  RR: '#f59e0b',
  Priority: '#ec4899',
  AFAS: '#10b981',
};

export interface ProcessInput {
  pid: number;
  arrival: number;
  burst: number;
  priority: number; // 1–10
  processClass: ProcessClass;
}

export interface GanttBlock {
  pid: number; // -1 for idle
  start: number;
  end: number;
}

export interface ProcessResult {
  pid: number;
  arrival: number;
  burst: number;
  priority: number;
  processClass: ProcessClass;
  completionTime: number;
  turnaroundTime: number;
  waitingTime: number;
  responseTime: number;
}

export interface AFASScoreEntry {
  pid: number;
  wpP: number;
  waA: number;
  wrR: number;
  negWcC: number;
  total: number;
}

export interface AFASDecision {
  time: number;
  chosenPid: number;
  queueSize: number;
  scores: AFASScoreEntry[];
  action: string;
  isAgingPromotion: boolean;
}

export interface SimulationResult {
  policy: Policy;
  gantt: GanttBlock[];
  processResults: ProcessResult[];
  decisions: AFASDecision[];
  contextSwitches: number;
  totalTime: number;
}

export interface Metrics {
  avgWaitingTime: number;
  avgTurnaroundTime: number;
  avgResponseTime: number;
  medianResponseTime: number;
  p95ResponseTime: number;
  maxReadyQueueWait: number;
  contextSwitches: number;
  cpuUtilization: number;
  throughput: number;
  jainsIndex: number;
  starvationWarnings: number;
}

export interface AFASWeights {
  wp: number;
  wa: number;
  wr: number;
  wc: number;
}

export const DEFAULT_WEIGHTS: AFASWeights = {
  wp: 0.30,
  wa: 0.40,
  wr: 0.15,
  wc: 0.15,
};

export const DEFAULT_QUANTUM = 4;

export interface InvariantResult {
  name: string;
  passed: boolean;
  message: string;
}

/* ── Process colors for Gantt ── */
const PROCESS_PALETTE = [
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899',
  '#f43f5e', '#ef4444', '#f97316', '#f59e0b', '#eab308',
  '#84cc16', '#22c55e', '#10b981', '#14b8a6', '#06b6d4',
  '#0ea5e9', '#3b82f6', '#2563eb', '#4f46e5', '#7c3aed',
];

export function getProcessColor(pid: number): string {
  return PROCESS_PALETTE[(pid - 1) % PROCESS_PALETTE.length];
}

/* ── Workload presets enum ── */
export type PresetWorkload = 'W1' | 'W2' | 'W3' | 'W4' | 'W5' | 'Random';

export const PRESET_LABELS: Record<PresetWorkload, string> = {
  W1: 'W1 — Uniform',
  W2: 'W2 — Mixed Bursts',
  W3: 'W3 — Priority Skew',
  W4: 'W4 — Burst Arrivals',
  W5: 'W5 — Share Imbalance',
  Random: 'Random',
};
