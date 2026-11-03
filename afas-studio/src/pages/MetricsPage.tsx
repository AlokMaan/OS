import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Info, AlertTriangle } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts';
import { useAppStore } from '@/store/store';
import { POLICY_COLORS } from '@/engine/types';
import type { Policy, Metrics } from '@/engine/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { fmt, cn } from '@/lib/utils';

const METRIC_INFO: Record<string, { label: string; tip: string; key: keyof Metrics; lowerBetter?: boolean }> = {
  avgWT: { label: 'Avg WT', tip: 'Average Waiting Time — lower is better', key: 'avgWaitingTime', lowerBetter: true },
  avgTAT: { label: 'Avg TAT', tip: 'Average Turnaround Time — lower is better', key: 'avgTurnaroundTime', lowerBetter: true },
  avgRT: { label: 'Avg RT', tip: 'Average Response Time — lower is better', key: 'avgResponseTime', lowerBetter: true },
  medRT: { label: 'Med RT', tip: 'Median Response Time', key: 'medianResponseTime', lowerBetter: true },
  p95RT: { label: 'p95 RT', tip: '95th percentile Response Time via linear interpolation', key: 'p95ResponseTime', lowerBetter: true },
  maxWait: { label: 'Max Wait', tip: 'Maximum wait time in ready queue', key: 'maxReadyQueueWait', lowerBetter: true },
  cs: { label: 'Ctx Sw', tip: 'Context Switches — lower is better', key: 'contextSwitches', lowerBetter: true },
  cpuUtil: { label: 'CPU Util', tip: 'CPU Utilization — higher is better', key: 'cpuUtilization' },
  tp: { label: 'Throughput', tip: 'Processes completed per time unit', key: 'throughput' },
  jain: { label: "Jain's FI", tip: "Jain's Fairness Index (1.0 = perfectly fair)", key: 'jainsIndex' },
  starv: { label: 'Starvation', tip: 'Processes with waiting time > 40 units', key: 'starvationWarnings', lowerBetter: true },
};

const METRIC_KEYS = Object.keys(METRIC_INFO);

export default function MetricsPage() {
  const { results, metricsMap, isSimulated, selectedPolicies } = useAppStore();

  const policies = useMemo(
    () => selectedPolicies.filter((p) => metricsMap.has(p)),
    [selectedPolicies, metricsMap],
  );

  const bestValues = useMemo(() => {
    const best: Record<string, { value: number; policy: Policy }> = {};
    for (const mk of METRIC_KEYS) {
      const info = METRIC_INFO[mk];
      let bestVal = info.lowerBetter ? Infinity : -Infinity;
      let bestPol = policies[0];
      for (const p of policies) {
        const m = metricsMap.get(p)!;
        const v = m[info.key] as number;
        if (info.lowerBetter ? v < bestVal : v > bestVal) {
          bestVal = v;
          bestPol = p;
        }
      }
      best[mk] = { value: bestVal, policy: bestPol };
    }
    return best;
  }, [policies, metricsMap]);

  const barData = useMemo(() => {
    return ['avgWT', 'avgTAT', 'avgRT'].map((mk) => {
      const info = METRIC_INFO[mk];
      const row: Record<string, unknown> = { metric: info.label };
      for (const p of policies) {
        row[p] = Number(fmt(metricsMap.get(p)![info.key] as number));
      }
      return row;
    });
  }, [policies, metricsMap]);

  const radarData = useMemo(() => {
    const keys = ['avgWT', 'avgRT', 'cpuUtil', 'jain', 'tp'];
    // Normalize each metric to 0-1 across policies
    return keys.map((mk) => {
      const info = METRIC_INFO[mk];
      const values = policies.map((p) => metricsMap.get(p)![info.key] as number);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const range = max - min || 1;
      const row: Record<string, unknown> = { metric: info.label };
      for (const p of policies) {
        const raw = metricsMap.get(p)![info.key] as number;
        // For lower-is-better, invert so higher is better on radar
        row[p] = info.lowerBetter ? 1 - (raw - min) / range : (raw - min) / range;
      }
      return row;
    });
  }, [policies, metricsMap]);

  if (!isSimulated || policies.length === 0) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-24 text-muted-foreground">
        <p className="text-lg">Run a simulation to see metrics and comparisons.</p>
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Metric cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {policies.map((policy) => {
          const m = metricsMap.get(policy)!;
          return (
            <Card key={policy} className={cn(policy === 'AFAS' && 'border-emerald-500/50')}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: POLICY_COLORS[policy] }} />
                  <CardTitle className="text-sm">{policy}</CardTitle>
                  {m.starvationWarnings > 0 && (
                    <Badge variant="destructive" className="text-[10px] gap-1">
                      <AlertTriangle className="h-3 w-3" /> {m.starvationWarnings}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-3">
                  {['avgWT', 'avgTAT', 'avgRT', 'cpuUtil', 'tp', 'jain'].map((mk) => {
                    const info = METRIC_INFO[mk];
                    const val = m[info.key] as number;
                    const isBest = bestValues[mk]?.policy === policy;
                    return (
                      <div key={mk} className="space-y-1">
                        <div className="flex items-center gap-1">
                          <span className="text-[10px] text-muted-foreground">{info.label}</span>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="h-2.5 w-2.5 text-muted-foreground cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-[200px] text-xs">{info.tip}</TooltipContent>
                          </Tooltip>
                        </div>
                        <span className={cn(
                          'font-mono text-sm font-semibold block',
                          isBest && 'text-emerald-400',
                        )}>
                          {info.key === 'cpuUtilization' ? `${fmt(val * 100)}%` : fmt(val)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Comparison table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Full Comparison</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Policy</TableHead>
                {METRIC_KEYS.map((mk) => (
                  <TableHead key={mk} className="text-center">
                    <Tooltip>
                      <TooltipTrigger className="cursor-help text-xs">{METRIC_INFO[mk].label}</TooltipTrigger>
                      <TooltipContent className="text-xs">{METRIC_INFO[mk].tip}</TooltipContent>
                    </Tooltip>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {policies.map((policy) => {
                const m = metricsMap.get(policy)!;
                return (
                  <TableRow key={policy} className={cn(policy === 'AFAS' && 'border-l-2 border-l-emerald-500')}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: POLICY_COLORS[policy] }} />
                        <span className="font-medium text-sm">{policy}</span>
                      </div>
                    </TableCell>
                    {METRIC_KEYS.map((mk) => {
                      const info = METRIC_INFO[mk];
                      const val = m[info.key] as number;
                      const isBest = bestValues[mk]?.policy === policy;
                      return (
                        <TableCell key={mk} className={cn('text-center font-mono text-xs', isBest && 'bg-emerald-500/10 text-emerald-400 font-semibold')}>
                          {info.key === 'cpuUtilization' ? `${fmt(val * 100)}%` : fmt(val)}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Charts */}
      <Tabs defaultValue="bar">
        <TabsList>
          <TabsTrigger value="bar">Bar Comparison</TabsTrigger>
          <TabsTrigger value="radar">Radar</TabsTrigger>
          <TabsTrigger value="process">Per-Process</TabsTrigger>
        </TabsList>

        <TabsContent value="bar">
          <Card>
            <CardContent className="pt-6">
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="metric" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                    <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 11 }} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    {policies.map((p) => (
                      <Bar key={p} dataKey={p} fill={POLICY_COLORS[p]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="radar">
          <Card>
            <CardContent className="pt-6 flex justify-center">
              <div className="h-80 w-full max-w-lg">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                    <PolarRadiusAxis tick={false} domain={[0, 1]} />
                    {policies.map((p) => (
                      <Radar key={p} name={p} dataKey={p} stroke={POLICY_COLORS[p]} fill={POLICY_COLORS[p]} fillOpacity={0.15} />
                    ))}
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="process">
          <Card>
            <CardContent className="p-0">
              {policies.map((policy) => {
                const r = results.get(policy)!;
                return (
                  <div key={policy} className="mb-4 last:mb-0">
                    <div className="px-4 py-2 bg-muted/30 border-b border-border/50">
                      <span className="text-sm font-semibold" style={{ color: POLICY_COLORS[policy] }}>{policy}</span>
                    </div>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>PID</TableHead>
                          <TableHead>Arrival</TableHead>
                          <TableHead>Burst</TableHead>
                          <TableHead>CT</TableHead>
                          <TableHead>TAT</TableHead>
                          <TableHead>WT</TableHead>
                          <TableHead>RT</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {r.processResults.map((pr) => (
                          <TableRow key={pr.pid}>
                            <TableCell className="font-mono text-xs">P{pr.pid}</TableCell>
                            <TableCell className="font-mono text-xs">{pr.arrival}</TableCell>
                            <TableCell className="font-mono text-xs">{pr.burst}</TableCell>
                            <TableCell className="font-mono text-xs">{pr.completionTime}</TableCell>
                            <TableCell className="font-mono text-xs">{pr.turnaroundTime}</TableCell>
                            <TableCell className={cn('font-mono text-xs', pr.waitingTime > 40 && 'text-rose-400')}>
                              {pr.waitingTime}
                            </TableCell>
                            <TableCell className="font-mono text-xs">{pr.responseTime}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
