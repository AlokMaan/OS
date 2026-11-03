import React from 'react';
import { motion } from 'framer-motion';
import { Play, CheckCircle2, XCircle, Shuffle } from 'lucide-react';
import { useAppStore } from '@/store/store';
import { generatePreset } from '@/engine/workloads';
import { PRESET_LABELS } from '@/engine/types';
import type { PresetWorkload } from '@/engine/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import ProcessTable from '@/components/simulator/ProcessTable';
import GanttChart from '@/components/simulator/GanttChart';
import PlaybackControls from '@/components/simulator/PlaybackControls';
import PolicySelector from '@/components/simulator/PolicySelector';
import WeightSliders from '@/components/simulator/WeightSliders';
import ReadyQueueViz from '@/components/simulator/ReadyQueueViz';

const PRESETS: PresetWorkload[] = ['W1', 'W2', 'W3', 'W4', 'W5', 'Random'];
const SEEDS = [1, 2, 3, 4, 5];

export default function SimulatorPage() {
  const {
    setProcesses, runSimulation, isSimulated,
    invariantResults,
  } = useAppStore();
  const [seed, setSeed] = React.useState(1);

  const handlePreset = (preset: PresetWorkload) => {
    const procs = generatePreset(preset, seed);
    setProcesses(procs);
  };

  const allInvariantsPassed = invariantResults.length > 0 && invariantResults.every((i) => i.passed);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Top controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Presets */}
        <div className="flex flex-wrap items-center gap-1.5">
          {PRESETS.map((p) => (
            <Button
              key={p}
              variant="outline"
              size="sm"
              onClick={() => handlePreset(p)}
              className="text-xs h-8"
            >
              {p === 'Random' ? <Shuffle className="h-3 w-3 mr-1" /> : null}
              {PRESET_LABELS[p].split(' — ')[0]}
            </Button>
          ))}
        </div>

        {/* Seed */}
        <Select value={String(seed)} onValueChange={(v) => setSeed(parseInt(v))}>
          <SelectTrigger className="w-24 h-8 text-xs">
            <SelectValue placeholder="Seed" />
          </SelectTrigger>
          <SelectContent>
            {SEEDS.map((s) => (
              <SelectItem key={s} value={String(s)}>Seed {s}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex-1" />

        {/* Invariants badge */}
        {isSimulated && (
          <Badge variant={allInvariantsPassed ? 'success' : 'destructive'} className="gap-1">
            {allInvariantsPassed ? (
              <><CheckCircle2 className="h-3 w-3" /> Invariants verified</>
            ) : (
              <><XCircle className="h-3 w-3" /> Invariant failed</>
            )}
          </Badge>
        )}

        {/* Run button */}
        <Button
          onClick={runSimulation}
          className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2 shadow-lg shadow-emerald-600/20"
        >
          <Play className="h-4 w-4" />
          Run Simulation
        </Button>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Process table */}
        <div className="lg:col-span-2 space-y-4">
          <ProcessTable />
          <GanttChart />
          <PlaybackControls />
          <ReadyQueueViz />
        </div>

        {/* Right: Policy selector + Weight sliders */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Scheduling Policies</CardTitle>
            </CardHeader>
            <CardContent>
              <PolicySelector />
            </CardContent>
          </Card>
          <WeightSliders />
        </div>
      </div>
    </motion.div>
  );
}
