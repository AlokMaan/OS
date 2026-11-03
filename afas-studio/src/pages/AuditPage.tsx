import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Download, ArrowUpDown } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { useAppStore } from '@/store/store';
import { getProcessColor } from '@/engine/types';
import type { AFASDecision } from '@/engine/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { downloadCSV, fmt } from '@/lib/utils';

const PAGE_SIZE = 50;

export default function AuditPage() {
  const { results, isSimulated, setCurrentTime } = useAppStore();
  const [filter, setFilter] = useState('');
  const [page, setPage] = useState(0);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  const decisions = useMemo<AFASDecision[]>(() => {
    if (!results.has('AFAS')) return [];
    return results.get('AFAS')!.decisions;
  }, [results]);

  const filtered = useMemo(() => {
    if (!filter) return decisions;
    const pid = parseInt(filter);
    if (!isNaN(pid)) return decisions.filter((d) => d.chosenPid === pid);
    return decisions.filter((d) => d.action.toLowerCase().includes(filter.toLowerCase()));
  }, [decisions, filter]);

  const paged = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  const selectedDecision = selectedIdx !== null ? decisions[selectedIdx] : null;

  const scoreChartData = useMemo(() => {
    if (!selectedDecision) return [];
    return selectedDecision.scores.map((s) => ({
      pid: `P${s.pid}`,
      'wp·P': Math.max(0, s.wpP),
      'wa·A': Math.max(0, s.waA),
      'wr·R': Math.max(0, s.wrR),
      '-wc·C': Math.abs(s.negWcC),
      total: s.total,
    }));
  }, [selectedDecision]);

  if (!isSimulated || !results.has('AFAS')) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-24 text-muted-foreground">
        <p className="text-lg">Run a simulation with AFAS policy enabled to see the audit log.</p>
      </motion.div>
    );
  }

  const handleExport = () => {
    const rows = decisions.map((d) => ({
      time: d.time,
      chosenPid: d.chosenPid,
      queueSize: d.queueSize,
      action: d.action,
      isAgingPromotion: d.isAgingPromotion,
      ...d.scores.find((s) => s.pid === d.chosenPid),
    }));
    downloadCSV(rows as Record<string, unknown>[], 'afas-audit-log.csv');
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Decision table */}
        <div className="xl:col-span-2 space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Filter by PID or action..."
                value={filter}
                onChange={(e) => { setFilter(e.target.value); setPage(0); }}
                className="pl-9 h-9"
              />
            </div>
            <Badge variant="secondary" className="font-mono">{filtered.length} decisions</Badge>
            <Button variant="outline" size="sm" onClick={handleExport} className="gap-1.5">
              <Download className="h-3.5 w-3.5" /> CSV
            </Button>
          </div>

          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-14">t</TableHead>
                    <TableHead className="w-16">PID</TableHead>
                    <TableHead className="w-12">|Q|</TableHead>
                    <TableHead className="w-16">wp·P</TableHead>
                    <TableHead className="w-16">wa·A</TableHead>
                    <TableHead className="w-16">wr·R</TableHead>
                    <TableHead className="w-16">-wc·C</TableHead>
                    <TableHead className="w-16">Score</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paged.map((d, i) => {
                    const globalIdx = page * PAGE_SIZE + i;
                    const chosenScore = d.scores.find((s) => s.pid === d.chosenPid);
                    return (
                      <TableRow
                        key={globalIdx}
                        className={`cursor-pointer transition-colors ${
                          selectedIdx === globalIdx ? 'bg-primary/10' : ''
                        } ${d.isAgingPromotion ? 'bg-amber-500/10' : ''}`}
                        onClick={() => {
                          setSelectedIdx(globalIdx);
                          setCurrentTime(d.time);
                        }}
                      >
                        <TableCell className="font-mono text-xs">{d.time}</TableCell>
                        <TableCell>
                          <span className="font-mono text-xs font-semibold" style={{ color: getProcessColor(d.chosenPid) }}>
                            P{d.chosenPid}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-xs">{d.queueSize}</TableCell>
                        <TableCell className="font-mono text-xs">{fmt(chosenScore?.wpP ?? 0, 3)}</TableCell>
                        <TableCell className="font-mono text-xs">{fmt(chosenScore?.waA ?? 0, 3)}</TableCell>
                        <TableCell className="font-mono text-xs">{fmt(chosenScore?.wrR ?? 0, 3)}</TableCell>
                        <TableCell className="font-mono text-xs">{fmt(chosenScore?.negWcC ?? 0, 3)}</TableCell>
                        <TableCell className="font-mono text-xs font-semibold">{fmt(chosenScore?.total ?? 0, 3)}</TableCell>
                        <TableCell>
                          <Badge
                            variant={d.isAgingPromotion ? 'warning' : d.action === 'COMPLETED' ? 'success' : 'secondary'}
                            className="text-[10px]"
                          >
                            {d.isAgingPromotion ? 'AGING_PROMOTION' : d.action}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}>
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page + 1} of {totalPages}
              </span>
              <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>
                Next
              </Button>
            </div>
          )}
        </div>

        {/* Score decomposition */}
        <div>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Score Decomposition</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDecision ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={scoreChartData} layout="vertical" margin={{ left: 10, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                      <YAxis type="category" dataKey="pid" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" width={35} />
                      <RechartsTooltip
                        contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 11 }}
                      />
                      <Bar dataKey="wp·P" stackId="a" fill="#6366f1" />
                      <Bar dataKey="wa·A" stackId="a" fill="#10b981" />
                      <Bar dataKey="wr·R" stackId="a" fill="#f59e0b" />
                      <Bar dataKey="-wc·C" stackId="a" fill="#f43f5e" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  Click a decision row to see its score breakdown.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
