import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import katex from 'katex';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

function Latex({ math, display = false }: { math: string; display?: boolean }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (ref.current) {
      katex.render(math, ref.current, { displayMode: display, throwOnError: false });
    }
  }, [math, display]);
  return <span ref={ref} />;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h2 className="text-xl font-bold text-primary border-b border-border/50 pb-2">{title}</h2>
      <div className="space-y-3 text-sm leading-relaxed text-foreground/90">{children}</div>
    </div>
  );
}

export default function DocsPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto space-y-8">
      {/* Title */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Adaptive Fairness-Aware Scheduler <Badge variant="success" className="ml-2 text-xs">AFAS</Badge>
        </h1>
        <p className="text-muted-foreground">Algorithm documentation and usage guide</p>
      </div>

      {/* Formula */}
      <Card>
        <CardHeader><CardTitle>The AFAS Formula</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-4 bg-muted/30 rounded-lg">
            <Latex math="S_i(t) = w_p \cdot P_i + w_a \cdot A_i(t) + w_r \cdot R_i - w_c \cdot C_i(t)" display />
          </div>

          <p>Each process <Latex math="i" /> receives a dynamic score <Latex math="S_i(t)" /> at every scheduling decision point. The process with the highest score is dispatched.</p>

          <div className="space-y-3">
            <h3 className="font-semibold text-base">Component Definitions</h3>

            <div className="space-y-2 pl-4 border-l-2 border-primary/30">
              <div>
                <span className="font-semibold text-primary">Priority</span>: <Latex math="P_i = \text{priority} / 10" /> where priority is an integer in [1, 10]. Higher priority processes get a higher base score.
              </div>
              <div>
                <span className="font-semibold text-emerald-400">Aging</span>: <Latex math="A_i(t) = \min\!\bigl(1,\; \frac{t - \text{lastExit}_i}{50}\bigr)" /> where <Latex math="\text{lastExit}_i" /> is the last time process <Latex math="i" /> left the CPU (defaults to arrival time). This prevents starvation by boosting processes that have been waiting.
              </div>
              <div>
                <span className="font-semibold text-amber-400">Responsiveness</span>: <Latex math="R_i" /> is a class-based constant — <Latex math="\text{Interactive} = 1.0" />, <Latex math="\text{Mixed} = 0.5" />, <Latex math="\text{Batch} = 0.2" />.
              </div>
              <div>
                <span className="font-semibold text-rose-400">CPU Consumption</span>: <Latex math="C_i(t) = \min\!\bigl(1,\; \frac{\text{decayedService}}{40}\bigr)" /> with exponential decay half-life of 40 time units. This penalizes processes that have recently used a lot of CPU.
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weights */}
      <Card>
        <CardHeader><CardTitle>Weight Parameters</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50">
                <th className="text-left py-2 pr-4 font-semibold">Weight</th>
                <th className="text-left py-2 pr-4 font-semibold">Default</th>
                <th className="text-left py-2 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody className="text-muted-foreground">
              <tr className="border-b border-border/30"><td className="py-2 pr-4 font-mono">wp</td><td className="py-2 pr-4 font-mono">0.30</td><td className="py-2">Static priority influence</td></tr>
              <tr className="border-b border-border/30"><td className="py-2 pr-4 font-mono">wa</td><td className="py-2 pr-4 font-mono">0.40</td><td className="py-2">Aging / starvation prevention</td></tr>
              <tr className="border-b border-border/30"><td className="py-2 pr-4 font-mono">wr</td><td className="py-2 pr-4 font-mono">0.15</td><td className="py-2">Process class responsiveness</td></tr>
              <tr><td className="py-2 pr-4 font-mono">wc</td><td className="py-2 pr-4 font-mono">0.15</td><td className="py-2">CPU consumption penalty</td></tr>
            </tbody>
          </table>
          <p className="mt-3 text-xs text-muted-foreground">Weights are automatically normalized to sum to 1.0.</p>
        </CardContent>
      </Card>

      {/* Tie-breaking */}
      <Card>
        <CardHeader><CardTitle>Tie-Breaking Rule</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">When two or more processes have the same score, ties are broken deterministically:</p>
          <ol className="list-decimal list-inside mt-2 text-sm space-y-1 text-muted-foreground">
            <li><span className="font-semibold text-foreground">Highest score</span> wins (descending)</li>
            <li>Earliest <span className="font-semibold text-foreground">arrival time</span> (ascending)</li>
            <li>Lowest <span className="font-semibold text-foreground">PID</span> (ascending)</li>
          </ol>
        </CardContent>
      </Card>

      {/* Pseudocode */}
      <Card>
        <CardHeader><CardTitle>Pseudocode</CardTitle></CardHeader>
        <CardContent>
          <pre className="bg-muted/50 rounded-lg p-4 text-xs font-mono overflow-x-auto leading-relaxed">
{`function AFAS_Schedule(processes, quantum, weights):
    normalize(weights)  // ensure wp + wa + wr + wc = 1.0
    
    while unfinished processes exist:
        ready ← {p : p.arrival ≤ t AND p.remaining > 0}
        
        if ready is empty:
            t ← next arrival time  // idle gap
            continue
        
        for each p in ready:
            P_i ← p.priority / 10
            A_i ← min(1, (t − p.lastExit) / 50)
            R_i ← classWeight(p.class)
            C_i ← min(1, decayedService(p) / 40)
            p.score ← wp·P_i + wa·A_i + wr·R_i − wc·C_i
        
        chosen ← argmax(ready, by=score,
                         tiebreak=[arrival ASC, pid ASC])
        
        run_duration ← min(quantum, chosen.remaining)
        execute chosen for run_duration units
        update chosen.service, chosen.lastExit
        
        if chosen.remaining = 0:
            record completion`}
          </pre>
        </CardContent>
      </Card>

      {/* How to use */}
      <Card>
        <CardHeader><CardTitle>How to Use This Tool</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p><span className="font-semibold text-foreground">1. Configure processes</span> — Add processes manually or load a preset workload (W1–W5). Each process has a PID, arrival time, burst length, priority (1–10), and class.</p>
          <p><span className="font-semibold text-foreground">2. Select policies</span> — Choose which scheduling policies to compare. AFAS is always recommended.</p>
          <p><span className="font-semibold text-foreground">3. Tune parameters</span> — Adjust the time quantum and AFAS weight sliders. Weights auto-normalize.</p>
          <p><span className="font-semibold text-foreground">4. Run simulation</span> — Click the green "Run Simulation" button. View the Gantt chart and use playback controls.</p>
          <p><span className="font-semibold text-foreground">5. Analyze</span> — Visit the Audit Log for decision-level details, Metrics for comparisons, and Experiments for benchmarks.</p>
        </CardContent>
      </Card>

      {/* Comparison Policies */}
      <Card>
        <CardHeader><CardTitle>Comparison Policies</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p><span className="font-semibold text-foreground">FCFS</span> — First Come First Served. Non-preemptive. Simple queue ordering.</p>
          <p><span className="font-semibold text-foreground">SJF</span> — Shortest Job First. Non-preemptive. Minimizes average waiting time for known burst lengths.</p>
          <p><span className="font-semibold text-foreground">SRTF</span> — Shortest Remaining Time First. Preemptive variant of SJF.</p>
          <p><span className="font-semibold text-foreground">RR</span> — Round Robin. Preemptive with fixed time quantum. Fair but may have high context switches.</p>
          <p><span className="font-semibold text-foreground">Priority</span> — Non-preemptive. Higher priority number = higher priority. Susceptible to starvation.</p>
          <p><span className="font-semibold text-foreground">AFAS</span> — Adaptive Fairness-Aware Scheduler. Combines priority, aging, class responsiveness, and CPU consumption decay.</p>
        </CardContent>
      </Card>

      {/* Invariants */}
      <Card>
        <CardHeader><CardTitle>Post-Run Invariants</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>Three invariants are checked after every simulation run:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li><span className="font-semibold text-foreground">Non-Overlap</span> — No two Gantt blocks overlap in time.</li>
            <li><span className="font-semibold text-foreground">Burst Conservation</span> — Total CPU time per process equals its declared burst length.</li>
            <li><span className="font-semibold text-foreground">No Pre-Arrival Execution</span> — No process executes before its arrival time.</li>
          </ol>
          <p className="mt-2">A green "Invariants verified" badge confirms correctness.</p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
