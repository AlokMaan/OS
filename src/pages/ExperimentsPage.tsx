import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Play, Download, Loader2 } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  LineChart, Line,
} from 'recharts';
import { simulate } from '@/engine/scheduler';
import { computeMetrics } from '@/engine/metrics';
import { generatePreset, generateScaling } from '@/engine/workloads';
import { ALL_POLICIES, POLICY_COLORS, DEFAULT_WEIGHTS } from '@/engine/types';
import type { Policy, Metrics, AFASWeights, PresetWorkload } from '@/engine/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { downloadCSV, downloadJSON, fmt, cn } from '@/lib/utils';

const WORKLOADS: PresetWorkload[] = ['W1', 'W2', 'W3', 'W4', 'W5'];
const SEEDS = [1, 2, 3, 4, 5];
const QUANTUM = 4;

interface BenchmarkResults {
  aggregated: Record<string, Record<string, number>>; // policy → metric → mean
  ablation: { name: string; avgWT: number; jainsIndex: number }[];
  weightSensitivity: Record<string, { x: number; avgWT: number; jainsIndex: number }[]>;
  quantumSweep: { q: number; RR: number; AFAS: number }[];
  runtimeScaling: { n: number; time: number }[];
}

export default function ExperimentsPage() {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);
  const [results, setResults] = useState<BenchmarkResults | null>(null);

  const runBenchmark = useCallback(async () => {
    setRunning(true);
    setProgress(0);

    const policies = ALL_POLICIES;
    const total = WORKLOADS.length * SEEDS.length * policies.length + 30 + 40 + 32 + 6; // approx
    setTotalTasks(total);
    let done = 0;

    const tick = () => { done++; setProgress(done); };

    // Helper to yield to UI
    const yieldToUI = () => new Promise<void>((r) => setTimeout(r, 0));

    // ── Aggregated metrics ──
    const metricsAccum: Record<string, Record<string, number[]>> = {};
    for (const policy of policies) {
      metricsAccum[policy] = {};
      ['avgWaitingTime', 'avgTurnaroundTime', 'avgResponseTime', 'jainsIndex', 'cpuUtilization', 'contextSwitches', 'starvationWarnings'].forEach(
        (k) => (metricsAccum[policy][k] = []),
      );
    }

    for (const wl of WORKLOADS) {
      for (const seed of SEEDS) {
        const procs = generatePreset(wl, seed);
        for (const policy of policies) {
          const r = simulate(policy, procs, QUANTUM, DEFAULT_WEIGHTS);
          const m = computeMetrics(r);
          for (const k of Object.keys(metricsAccum[policy])) {
            metricsAccum[policy][k].push(m[k as keyof Metrics] as number);
          }
          tick();
        }
        await yieldToUI();
      }
    }

    const aggregated: Record<string, Record<string, number>> = {};
    for (const policy of policies) {
      aggregated[policy] = {};
      for (const k of Object.keys(metricsAccum[policy])) {
        const vals = metricsAccum[policy][k];
        aggregated[policy][k] = vals.reduce((a, b) => a + b, 0) / vals.length;
      }
    }

    // ── Ablation ──
    const ablationConfigs: { name: string; weights: AFASWeights }[] = [
      { name: 'Full AFAS', weights: DEFAULT_WEIGHTS },
      { name: 'No Aging', weights: { ...DEFAULT_WEIGHTS, wa: 0 } },
      { name: 'No Share', weights: { ...DEFAULT_WEIGHTS, wr: 0 } },
    ];

    const ablation = ablationConfigs.map((cfg) => {
      let totalWT = 0, totalJain = 0, count = 0;
      for (const wl of WORKLOADS) {
        for (const seed of SEEDS) {
          const procs = generatePreset(wl, seed);
          const r = simulate('AFAS', procs, QUANTUM, cfg.weights);
          const m = computeMetrics(r);
          totalWT += m.avgWaitingTime;
          totalJain += m.jainsIndex;
          count++;
          tick();
        }
      }
      return { name: cfg.name, avgWT: totalWT / count, jainsIndex: totalJain / count };
    });
    await yieldToUI();

    // ── Weight sensitivity ──
    const weightSensitivity: Record<string, { x: number; avgWT: number; jainsIndex: number }[]> = {};
    const weightKeys = ['wp', 'wa', 'wr', 'wc'] as const;
    for (const wKey of weightKeys) {
      weightSensitivity[wKey] = [];
      for (let v = 0; v <= 1.0; v += 0.1) {
        const w: AFASWeights = { wp: 0.25, wa: 0.25, wr: 0.25, wc: 0.25 };
        const remainder = 1.0 - v;
        const otherKeys = weightKeys.filter((k) => k !== wKey);
        for (const ok of otherKeys) w[ok] = remainder / 3;
        w[wKey] = v;

        let totalWT = 0, totalJain = 0, count = 0;
        for (const seed of [1, 2, 3]) {
          const procs = generatePreset('W2', seed);
          const r = simulate('AFAS', procs, QUANTUM, w);
          const m = computeMetrics(r);
          totalWT += m.avgWaitingTime;
          totalJain += m.jainsIndex;
          count++;
        }
        weightSensitivity[wKey].push({ x: Number(v.toFixed(1)), avgWT: totalWT / count, jainsIndex: totalJain / count });
        tick();
      }
      await yieldToUI();
    }

    // ── Quantum sweep ──
    const quantumSweep: { q: number; RR: number; AFAS: number }[] = [];
    for (let q = 1; q <= 32; q++) {
      let rrWT = 0, afasWT = 0, count = 0;
      for (const seed of [1, 2]) {
        const procs = generatePreset('W2', seed);
        const rr = simulate('RR', procs, q, DEFAULT_WEIGHTS);
        const af = simulate('AFAS', procs, q, DEFAULT_WEIGHTS);
        rrWT += computeMetrics(rr).avgWaitingTime;
        afasWT += computeMetrics(af).avgWaitingTime;
        count++;
      }
      quantumSweep.push({ q, RR: rrWT / count, AFAS: afasWT / count });
      tick();
    }
    await yieldToUI();

    // ── Runtime scaling ──
    const runtimeScaling: { n: number; time: number }[] = [];
    for (const n of [10, 20, 50, 100, 200, 500]) {
      const procs = generateScaling(1, n);
      const start = performance.now();
      simulate('AFAS', procs, QUANTUM, DEFAULT_WEIGHTS);
      const elapsed = performance.now() - start;
      runtimeScaling.push({ n, time: Number(elapsed.toFixed(2)) });
      tick();
    }

    setResults({ aggregated, ablation, weightSensitivity, quantumSweep, runtimeScaling });
    setRunning(false);
  }, []);

  const handleExport = () => {
    if (!results) return;
    downloadJSON(results, 'afas-benchmark-results.json');
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Controls */}
      <div className="flex items-center gap-4">
        <Button
          onClick={runBenchmark}
          disabled={running}
          className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2"
        >
          {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {running ? 'Running...' : 'Run Benchmark'}
        </Button>
        {results && (
          <Button variant="outline" size="sm" onClick={handleExport} className="gap-1.5">
            <Download className="h-3.5 w-3.5" /> Export JSON
          </Button>
        )}
        {running && (
          <div className="flex-1 flex items-center gap-3">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-emerald-500 rounded-full"
                animate={{ width: `${totalTasks > 0 ? (progress / totalTasks) * 100 : 0}%` }}
              />
            </div>
            <Badge variant="secondary" className="font-mono text-xs">{progress}/{totalTasks}</Badge>
          </div>
        )}
      </div>

      {!results && !running && (
        <div className="text-center py-24 text-muted-foreground">
          <p className="text-lg">Click "Run Benchmark" to execute W1–W5 × seeds 1–5 × all policies.</p>
          <p className="text-sm mt-2">Includes ablation, weight sensitivity, quantum sweep, and runtime scaling experiments.</p>
        </div>
      )}

      {results && (
        <Tabs defaultValue="aggregated">
          <TabsList className="flex-wrap">
            <TabsTrigger value="aggregated">Aggregated</TabsTrigger>
            <TabsTrigger value="ablation">Ablation</TabsTrigger>
            <TabsTrigger value="weights">Weight Sensitivity</TabsTrigger>
            <TabsTrigger value="quantum">Quantum Sweep</TabsTrigger>
            <TabsTrigger value="scaling">Runtime Scaling</TabsTrigger>
          </TabsList>

          <TabsContent value="aggregated">
            <Card>
              <CardHeader><CardTitle className="text-base">Mean Metrics (W1–W5 × Seeds 1–5)</CardTitle></CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Policy</TableHead>
                      <TableHead>Avg WT</TableHead>
                      <TableHead>Avg TAT</TableHead>
                      <TableHead>Avg RT</TableHead>
                      <TableHead>Jain's FI</TableHead>
                      <TableHead>CPU Util</TableHead>
                      <TableHead>Ctx Sw</TableHead>
                      <TableHead>Starvation</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ALL_POLICIES.map((p) => {
                      const a = results.aggregated[p];
                      return (
                        <TableRow key={p} className={cn(p === 'AFAS' && 'border-l-2 border-l-emerald-500')}>
                          <TableCell><span className="font-semibold" style={{ color: POLICY_COLORS[p] }}>{p}</span></TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.avgWaitingTime)}</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.avgTurnaroundTime)}</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.avgResponseTime)}</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.jainsIndex, 3)}</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.cpuUtilization * 100)}%</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.contextSwitches, 1)}</TableCell>
                          <TableCell className="font-mono text-xs">{fmt(a.starvationWarnings, 1)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ablation">
            <Card>
              <CardHeader><CardTitle className="text-base">AFAS Ablation Study</CardTitle></CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={results.ablation} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                      <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                      <RechartsTooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 11 }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Bar dataKey="avgWT" name="Avg WT" fill="#6366f1" />
                      <Bar dataKey="jainsIndex" name="Jain's FI" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="weights">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {['wp', 'wa', 'wr', 'wc'].map((wKey) => (
                <Card key={wKey}>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">{wKey} Sensitivity</CardTitle></CardHeader>
                  <CardContent>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={results.weightSensitivity[wKey]} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                          <XAxis dataKey="x" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                          <YAxis yAxisId="left" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                          <RechartsTooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 10 }} />
                          <Legend wrapperStyle={{ fontSize: 10 }} />
                          <Line yAxisId="left" type="monotone" dataKey="avgWT" name="Avg WT" stroke="#6366f1" strokeWidth={2} dot={{ r: 2 }} />
                          <Line yAxisId="right" type="monotone" dataKey="jainsIndex" name="Jain's FI" stroke="#10b981" strokeWidth={2} dot={{ r: 2 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="quantum">
            <Card>
              <CardHeader><CardTitle className="text-base">Quantum Sweep (q = 1..32)</CardTitle></CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={results.quantumSweep} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="q" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" label={{ value: 'Quantum', position: 'insideBottomRight', offset: -5, fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" label={{ value: 'Avg WT', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                      <RechartsTooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 11 }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Line type="monotone" dataKey="RR" name="Round Robin" stroke={POLICY_COLORS.RR} strokeWidth={2} dot={{ r: 2 }} />
                      <Line type="monotone" dataKey="AFAS" name="AFAS" stroke={POLICY_COLORS.AFAS} strokeWidth={2} dot={{ r: 2 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="scaling">
            <Card>
              <CardHeader><CardTitle className="text-base">Runtime Scaling (N = 10..500)</CardTitle></CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={results.runtimeScaling} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="n" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" scale="log" domain={['auto', 'auto']} label={{ value: 'Processes (N)', position: 'insideBottomRight', offset: -5, fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" scale="log" domain={['auto', 'auto']} label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                      <RechartsTooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 11 }} />
                      <Line type="monotone" dataKey="time" name="AFAS Runtime" stroke={POLICY_COLORS.AFAS} strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </motion.div>
  );
}
