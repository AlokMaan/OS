import { create } from 'zustand';
import { simulate } from '@/engine/scheduler';
import { computeMetrics } from '@/engine/metrics';
import { checkInvariants } from '@/engine/invariants';
import type {
  ProcessInput,
  Policy,
  AFASWeights,
  SimulationResult,
  Metrics,
  InvariantResult,
} from '@/engine/types';
import { DEFAULT_WEIGHTS, DEFAULT_QUANTUM } from '@/engine/types';

/* ── localStorage helpers ── */

function loadJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (raw) return JSON.parse(raw) as T;
  } catch { /* ignore */ }
  return fallback;
}

function saveJSON(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch { /* ignore */ }
}

/* ── Default processes ── */

const DEFAULT_PROCESSES: ProcessInput[] = [
  { pid: 1, arrival: 0, burst: 5, priority: 5, processClass: 'Interactive' },
  { pid: 2, arrival: 1, burst: 3, priority: 7, processClass: 'Mixed' },
  { pid: 3, arrival: 2, burst: 8, priority: 3, processClass: 'Batch' },
  { pid: 4, arrival: 3, burst: 6, priority: 8, processClass: 'Interactive' },
];

/* ── Store ── */

export interface AppState {
  processes: ProcessInput[];
  setProcesses: (p: ProcessInput[]) => void;
  addProcess: (p: ProcessInput) => void;
  removeProcess: (pid: number) => void;
  updateProcess: (pid: number, updates: Partial<ProcessInput>) => void;

  selectedPolicies: Policy[];
  togglePolicy: (p: Policy) => void;
  setSelectedPolicies: (p: Policy[]) => void;

  quantum: number;
  setQuantum: (q: number) => void;
  weights: AFASWeights;
  setWeights: (w: AFASWeights) => void;
  resetWeights: () => void;

  results: Map<Policy, SimulationResult>;
  metricsMap: Map<Policy, Metrics>;
  invariantResults: InvariantResult[];
  isSimulated: boolean;

  currentTime: number;
  setCurrentTime: (t: number) => void;
  isPlaying: boolean;
  setIsPlaying: (p: boolean) => void;
  playbackSpeed: number;
  setPlaybackSpeed: (s: number) => void;
  maxTime: number;

  runSimulation: () => void;
  resetSimulation: () => void;

  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  /* ── Processes ── */
  processes: loadJSON<ProcessInput[]>('afas-processes', DEFAULT_PROCESSES),
  setProcesses: (p) => {
    set({ processes: p, isSimulated: false });
    saveJSON('afas-processes', p);
  },
  addProcess: (p) => {
    const next = [...get().processes, p];
    set({ processes: next, isSimulated: false });
    saveJSON('afas-processes', next);
  },
  removeProcess: (pid) => {
    const next = get().processes.filter((pr) => pr.pid !== pid);
    set({ processes: next, isSimulated: false });
    saveJSON('afas-processes', next);
  },
  updateProcess: (pid, updates) => {
    const next = get().processes.map((pr) => (pr.pid === pid ? { ...pr, ...updates } : pr));
    set({ processes: next, isSimulated: false });
    saveJSON('afas-processes', next);
  },

  /* ── Policies ── */
  selectedPolicies: loadJSON<Policy[]>('afas-policies', ['FCFS', 'AFAS']),
  togglePolicy: (p) => {
    const cur = get().selectedPolicies;
    let next: Policy[];
    if (cur.includes(p)) {
      if (cur.length <= 1) return; // keep at least one
      next = cur.filter((x) => x !== p);
    } else {
      next = [...cur, p];
    }
    set({ selectedPolicies: next, isSimulated: false });
    saveJSON('afas-policies', next);
  },
  setSelectedPolicies: (p) => {
    set({ selectedPolicies: p, isSimulated: false });
    saveJSON('afas-policies', p);
  },

  /* ── Parameters ── */
  quantum: loadJSON<number>('afas-quantum', DEFAULT_QUANTUM),
  setQuantum: (q) => {
    set({ quantum: q, isSimulated: false });
    saveJSON('afas-quantum', q);
  },
  weights: loadJSON<AFASWeights>('afas-weights', DEFAULT_WEIGHTS),
  setWeights: (w) => {
    set({ weights: w, isSimulated: false });
    saveJSON('afas-weights', w);
  },
  resetWeights: () => {
    set({ weights: DEFAULT_WEIGHTS, isSimulated: false });
    saveJSON('afas-weights', DEFAULT_WEIGHTS);
  },

  /* ── Results ── */
  results: new Map(),
  metricsMap: new Map(),
  invariantResults: [],
  isSimulated: false,

  /* ── Playback ── */
  currentTime: 0,
  setCurrentTime: (t) => set({ currentTime: t }),
  isPlaying: false,
  setIsPlaying: (p) => set({ isPlaying: p }),
  playbackSpeed: 1,
  setPlaybackSpeed: (s) => set({ playbackSpeed: s }),
  maxTime: 0,

  /* ── Actions ── */
  runSimulation: () => {
    const { processes, selectedPolicies, quantum, weights } = get();
    if (processes.length === 0) return;

    const results = new Map<Policy, SimulationResult>();
    const metricsMap = new Map<Policy, Metrics>();
    let maxTime = 0;

    for (const policy of selectedPolicies) {
      const result = simulate(policy, processes, quantum, weights);
      results.set(policy, result);
      metricsMap.set(policy, computeMetrics(result));
      if (result.totalTime > maxTime) maxTime = result.totalTime;
    }

    const firstResult = results.values().next().value;
    const invariantResults = firstResult ? checkInvariants(firstResult, processes) : [];

    set({
      results,
      metricsMap,
      invariantResults,
      isSimulated: true,
      currentTime: 0,
      isPlaying: false,
      maxTime,
    });
  },
  resetSimulation: () => {
    set({
      results: new Map(),
      metricsMap: new Map(),
      invariantResults: [],
      isSimulated: false,
      currentTime: 0,
      isPlaying: false,
      maxTime: 0,
    });
  },

  /* ── Theme ── */
  theme: loadJSON<'dark' | 'light'>('afas-theme', 'dark'),
  toggleTheme: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark';
    set({ theme: next });
    saveJSON('afas-theme', next);
    if (next === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  },
}));
