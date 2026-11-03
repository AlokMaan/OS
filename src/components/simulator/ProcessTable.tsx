import React, { useMemo, useState, useCallback } from 'react';
import { Plus, Trash2, Upload } from 'lucide-react';
import { useAppStore } from '@/store/store';
import { getProcessColor } from '@/engine/types';
import type { ProcessClass, ProcessInput } from '@/engine/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn, parseCSV } from '@/lib/utils';

const CLASSES: ProcessClass[] = ['Interactive', 'Mixed', 'Batch'];

export default function ProcessTable() {
  const { processes, addProcess, removeProcess, updateProcess, setProcesses } = useAppStore();
  const [errors, setErrors] = useState<Record<string, string>>({});

  const nextPid = useMemo(() => {
    if (processes.length === 0) return 1;
    return Math.max(...processes.map((p) => p.pid)) + 1;
  }, [processes]);

  const validate = useCallback(
    (pid: number, field: string, value: number): string | null => {
      if (field === 'burst' && value <= 0) return 'Burst must be > 0';
      if (field === 'priority' && (value < 1 || value > 10)) return 'Priority must be 1-10';
      if (field === 'arrival' && value < 0) return 'Arrival must be >= 0';
      if (field === 'pid') {
        if (value <= 0) return 'PID must be > 0';
        if (processes.some((p) => p.pid === value && p.pid !== pid)) return 'PID must be unique';
      }
      return null;
    },
    [processes],
  );

  const handleChange = (pid: number, field: keyof ProcessInput, rawValue: string | number) => {
    const key = `${pid}-${field}`;
    if (field === 'processClass') {
      updateProcess(pid, { processClass: rawValue as ProcessClass });
      return;
    }
    const value = typeof rawValue === 'string' ? parseInt(rawValue, 10) : rawValue;
    if (isNaN(value)) return;
    const err = validate(pid, field, value);
    if (err) {
      setErrors((prev) => ({ ...prev, [key]: err }));
    } else {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
      updateProcess(pid, { [field]: value });
    }
  };

  const handleAdd = () => {
    addProcess({
      pid: nextPid,
      arrival: 0,
      burst: 5,
      priority: 5,
      processClass: 'Mixed',
    });
  };

  const handleImportCSV = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const text = ev.target?.result as string;
        try {
          const parsed = parseCSV(text);
          const valid: ProcessInput[] = parsed
            .filter((r) => r.burst > 0)
            .map((r) => ({
              pid: r.pid,
              arrival: Math.max(0, r.arrival),
              burst: Math.max(1, r.burst),
              priority: Math.max(1, Math.min(10, r.priority)),
              processClass: (['Interactive', 'Mixed', 'Batch'].includes(r.processClass) ? r.processClass : 'Mixed') as ProcessClass,
            }));
          if (valid.length > 0) setProcesses(valid);
        } catch {
          /* ignore parse errors */
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Process Table</CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleImportCSV} className="gap-1.5">
              <Upload className="h-3.5 w-3.5" />
              CSV
            </Button>
            <Button variant="outline" size="sm" onClick={handleAdd} className="gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              Add
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {processes.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground text-sm">
            No processes. Click "Add" to create one.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12"></TableHead>
                <TableHead className="w-20">PID</TableHead>
                <TableHead className="w-24">Arrival</TableHead>
                <TableHead className="w-20">Burst</TableHead>
                <TableHead className="w-24">Priority</TableHead>
                <TableHead className="w-32">Class</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {processes.map((p) => (
                <TableRow key={p.pid}>
                  <TableCell>
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getProcessColor(p.pid) }}
                    />
                  </TableCell>
                  <TableCell>
                    <span className="font-mono text-sm">P{p.pid}</span>
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={p.arrival}
                      min={0}
                      onChange={(e) => handleChange(p.pid, 'arrival', e.target.value)}
                      error={!!errors[`${p.pid}-arrival`]}
                      className="h-8 w-16 font-mono text-sm"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={p.burst}
                      min={1}
                      onChange={(e) => handleChange(p.pid, 'burst', e.target.value)}
                      error={!!errors[`${p.pid}-burst`]}
                      className="h-8 w-16 font-mono text-sm"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={p.priority}
                      min={1}
                      max={10}
                      onChange={(e) => handleChange(p.pid, 'priority', e.target.value)}
                      error={!!errors[`${p.pid}-priority`]}
                      className="h-8 w-16 font-mono text-sm"
                    />
                  </TableCell>
                  <TableCell>
                    <Select
                      value={p.processClass}
                      onValueChange={(v) => handleChange(p.pid, 'processClass', v)}
                    >
                      <SelectTrigger className="h-8 w-28 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CLASSES.map((c) => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeProcess(p.pid)}
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        {Object.keys(errors).length > 0 && (
          <div className="px-4 pb-3 text-xs text-destructive">
            {Object.values(errors)[0]}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
