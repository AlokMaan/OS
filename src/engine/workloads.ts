/**
 * Preset workload generators.
 * All use mulberry32 for deterministic reproducibility.
 */

import type { ProcessInput, ProcessClass, PresetWorkload } from './types';
import { mulberry32, randInt, randChoice } from './prng';

function gen(
  seed: number,
  count: number,
  burstRange: [number, number],
  arrivalSpread: number,
  classes: ProcessClass[],
  priorityRange: [number, number] = [1, 10],
): ProcessInput[] {
  const rng = mulberry32(seed);
  const procs: ProcessInput[] = [];
  for (let i = 0; i < count; i++) {
    procs.push({
      pid: i + 1,
      arrival: randInt(rng, 0, arrivalSpread),
      burst: randInt(rng, burstRange[0], burstRange[1]),
      priority: randInt(rng, priorityRange[0], priorityRange[1]),
      processClass: randChoice(rng, classes),
    });
  }
  return procs;
}

/** W1 — Uniform: all similar bursts, even arrival spread, balanced classes. */
function generateW1(seed: number): ProcessInput[] {
  return gen(seed, 8, [4, 8], 10, ['Interactive', 'Mixed', 'Batch']);
}

/** W2 — Mixed Bursts: huge variance in burst lengths. */
function generateW2(seed: number): ProcessInput[] {
  return gen(seed, 8, [1, 30], 12, ['Interactive', 'Mixed', 'Batch']);
}

/** W3 — Priority Skew: most processes are low priority, a few are high. */
function generateW3(seed: number): ProcessInput[] {
  const rng = mulberry32(seed);
  const procs: ProcessInput[] = [];
  for (let i = 0; i < 8; i++) {
    const isHigh = rng() < 0.25;
    procs.push({
      pid: i + 1,
      arrival: randInt(rng, 0, 10),
      burst: randInt(rng, 3, 15),
      priority: isHigh ? randInt(rng, 8, 10) : randInt(rng, 1, 3),
      processClass: randChoice(rng, ['Interactive', 'Mixed', 'Batch'] as ProcessClass[]),
    });
  }
  return procs;
}

/** W4 — Burst Arrivals: processes arrive in tight clusters. */
function generateW4(seed: number): ProcessInput[] {
  const rng = mulberry32(seed);
  const procs: ProcessInput[] = [];
  const burstTimes = [0, 0, 0, 10, 10, 10, 20, 20];
  for (let i = 0; i < 8; i++) {
    procs.push({
      pid: i + 1,
      arrival: burstTimes[i] + randInt(rng, 0, 2),
      burst: randInt(rng, 2, 12),
      priority: randInt(rng, 1, 10),
      processClass: randChoice(rng, ['Interactive', 'Mixed', 'Batch'] as ProcessClass[]),
    });
  }
  return procs;
}

/** W5 — Share Imbalance: mostly Batch with one Interactive process. */
function generateW5(seed: number): ProcessInput[] {
  const rng = mulberry32(seed);
  const procs: ProcessInput[] = [];
  for (let i = 0; i < 8; i++) {
    procs.push({
      pid: i + 1,
      arrival: randInt(rng, 0, 8),
      burst: randInt(rng, 5, 20),
      priority: randInt(rng, 2, 8),
      processClass: i === 0 ? 'Interactive' : 'Batch',
    });
  }
  return procs;
}

/** Random workload with configurable parameters. */
export function generateRandom(seed: number, count = 8): ProcessInput[] {
  return gen(seed, count, [1, 25], 15, ['Interactive', 'Mixed', 'Batch']);
}

export function generatePreset(preset: PresetWorkload, seed: number): ProcessInput[] {
  switch (preset) {
    case 'W1':
      return generateW1(seed);
    case 'W2':
      return generateW2(seed);
    case 'W3':
      return generateW3(seed);
    case 'W4':
      return generateW4(seed);
    case 'W5':
      return generateW5(seed);
    case 'Random':
      return generateRandom(seed);
  }
}

/** Generate a workload with N processes for scaling experiments. */
export function generateScaling(seed: number, n: number): ProcessInput[] {
  return gen(seed, n, [1, 20], n * 2, ['Interactive', 'Mixed', 'Batch']);
}
