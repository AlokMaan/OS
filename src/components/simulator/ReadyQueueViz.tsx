import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '@/store/store';
import { getProcessColor } from '@/engine/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function ReadyQueueViz() {
  const { isSimulated, results, selectedPolicies, currentTime, processes } = useAppStore();

  const queueState = useMemo(() => {
    // Use first policy's result
    const policy = selectedPolicies[0];
    if (!policy || !results.has(policy)) return [];

    const r = results.get(policy)!;
    const t = Math.floor(currentTime);

    // Find which processes are in the ready queue at time t
    // A process is "ready" if it has arrived and not yet completed, and is NOT currently running
    const completed = new Set<number>();
    let runningPid = -1;

    for (const block of r.gantt) {
      if (block.pid === -1) continue;
      if (block.end <= t) {
        // Check if this process has remaining bursts after this block
        const totalCPU = r.gantt
          .filter((b) => b.pid === block.pid && b.end <= t)
          .reduce((s, b) => s + (b.end - b.start), 0);
        const proc = processes.find((p) => p.pid === block.pid);
        if (proc && totalCPU >= proc.burst) completed.add(block.pid);
      }
      if (block.start <= t && block.end > t) {
        runningPid = block.pid;
      }
    }

    return processes
      .filter((p) => p.arrival <= t && !completed.has(p.pid) && p.pid !== runningPid)
      .map((p) => ({ pid: p.pid, remaining: p.burst - r.gantt
        .filter((b) => b.pid === p.pid && b.end <= t)
        .reduce((s, b) => s + (b.end - b.start), 0),
      }))
      .filter((p) => p.remaining > 0);
  }, [isSimulated, results, selectedPolicies, currentTime, processes]);

  if (!isSimulated || currentTime <= 0) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">
          Ready Queue at <span className="font-mono text-emerald-400">t = {Math.floor(currentTime)}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {queueState.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground text-xs">Queue empty</div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {queueState.map((item) => (
                <motion.div
                  key={item.pid}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="flex items-center gap-3"
                >
                  <span className="font-mono text-xs w-8 text-muted-foreground">P{item.pid}</span>
                  <div className="flex-1 h-5 bg-muted/50 rounded overflow-hidden">
                    <motion.div
                      className="h-full rounded"
                      style={{ backgroundColor: getProcessColor(item.pid) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, (item.remaining / 20) * 100)}%` }}
                      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                    />
                  </div>
                  <span className="font-mono text-xs text-muted-foreground w-12 text-right">
                    rem: {item.remaining}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
