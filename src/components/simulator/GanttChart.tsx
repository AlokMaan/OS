import React, { useMemo, useState } from 'react';
import { useAppStore } from '@/store/store';
import { POLICY_LABELS, getProcessColor } from '@/engine/types';
import type { Policy, GanttBlock } from '@/engine/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const ROW_HEIGHT = 40;
const LABEL_WIDTH = 100;
const TOP_PADDING = 10;
const BOTTOM_AXIS = 30;

export default function GanttChart() {
  const { results, selectedPolicies, isSimulated, maxTime, currentTime } = useAppStore();
  const [hoveredBlock, setHoveredBlock] = useState<{ policy: Policy; block: GanttBlock; x: number; y: number } | null>(null);

  const policies = useMemo(
    () => selectedPolicies.filter((p) => results.has(p)),
    [selectedPolicies, results],
  );

  if (!isSimulated || policies.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Gantt Chart</CardTitle></CardHeader>
        <CardContent>
          <div className="text-center py-16 text-muted-foreground text-sm">
            Run a simulation to see the Gantt chart.
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalHeight = TOP_PADDING + policies.length * ROW_HEIGHT + BOTTOM_AXIS;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Gantt Chart</CardTitle>
      </CardHeader>
      <CardContent className="p-4 overflow-x-auto">
        <div className="relative min-w-[600px]">
          <svg
            width="100%"
            viewBox={`0 0 800 ${totalHeight}`}
            className="select-none"
            style={{ minHeight: totalHeight }}
          >
            <defs>
              <pattern id="idlePattern" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="6" className="stroke-muted-foreground/20" strokeWidth="1.5" />
              </pattern>
            </defs>

            {policies.map((policy, rowIdx) => {
              const r = results.get(policy)!;
              const y = TOP_PADDING + rowIdx * ROW_HEIGHT;
              const chartWidth = 800 - LABEL_WIDTH - 20;
              const scale = maxTime > 0 ? chartWidth / maxTime : 1;

              return (
                <g key={policy}>
                  {/* Row label */}
                  <text
                    x={4}
                    y={y + ROW_HEIGHT / 2 + 4}
                    className="fill-foreground text-[11px] font-medium"
                  >
                    {policy}
                  </text>

                  {/* Row background */}
                  <rect
                    x={LABEL_WIDTH}
                    y={y + 4}
                    width={chartWidth}
                    height={ROW_HEIGHT - 8}
                    rx={4}
                    className="fill-muted/30"
                  />

                  {/* Gantt blocks */}
                  {r.gantt.map((block, bIdx) => {
                    const bx = LABEL_WIDTH + block.start * scale;
                    const bw = (block.end - block.start) * scale;
                    const isIdle = block.pid === -1;
                    const color = isIdle ? undefined : getProcessColor(block.pid);

                    return (
                      <g key={bIdx}>
                        <rect
                          x={bx}
                          y={y + 6}
                          width={Math.max(bw - 1, 1)}
                          height={ROW_HEIGHT - 12}
                          rx={3}
                          fill={isIdle ? 'url(#idlePattern)' : color}
                          opacity={isIdle ? 0.5 : 0.85}
                          className="transition-opacity cursor-pointer hover:opacity-100"
                          onMouseEnter={(e) => {
                            const rect = (e.target as SVGRectElement).getBoundingClientRect();
                            setHoveredBlock({ policy, block, x: rect.x + rect.width / 2, y: rect.y });
                          }}
                          onMouseLeave={() => setHoveredBlock(null)}
                        />
                        {/* PID label if block is wide enough */}
                        {!isIdle && bw > 20 && (
                          <text
                            x={bx + bw / 2}
                            y={y + ROW_HEIGHT / 2 + 4}
                            textAnchor="middle"
                            className="fill-white text-[9px] font-mono font-bold pointer-events-none"
                          >
                            P{block.pid}
                          </text>
                        )}
                        {/* Context-switch marker */}
                        {bIdx > 0 && !isIdle && r.gantt[bIdx - 1].pid !== block.pid && r.gantt[bIdx - 1].pid !== -1 && (
                          <line
                            x1={bx}
                            y1={y + 4}
                            x2={bx}
                            y2={y + ROW_HEIGHT - 4}
                            className="stroke-amber-400/60"
                            strokeWidth={1.5}
                            strokeDasharray="2,2"
                          />
                        )}
                      </g>
                    );
                  })}
                </g>
              );
            })}

            {/* Time axis */}
            {(() => {
              const axisY = TOP_PADDING + policies.length * ROW_HEIGHT + 4;
              const chartWidth = 800 - LABEL_WIDTH - 20;
              const scale = maxTime > 0 ? chartWidth / maxTime : 1;
              const tickInterval = Math.max(1, Math.ceil(maxTime / 20));
              const ticks: number[] = [];
              for (let t = 0; t <= maxTime; t += tickInterval) ticks.push(t);
              if (ticks[ticks.length - 1] !== maxTime) ticks.push(maxTime);

              return (
                <g>
                  <line
                    x1={LABEL_WIDTH}
                    y1={axisY}
                    x2={LABEL_WIDTH + chartWidth}
                    y2={axisY}
                    className="stroke-border"
                    strokeWidth={1}
                  />
                  {ticks.map((t) => (
                    <g key={t}>
                      <line
                        x1={LABEL_WIDTH + t * scale}
                        y1={axisY}
                        x2={LABEL_WIDTH + t * scale}
                        y2={axisY + 5}
                        className="stroke-muted-foreground"
                        strokeWidth={1}
                      />
                      <text
                        x={LABEL_WIDTH + t * scale}
                        y={axisY + 16}
                        textAnchor="middle"
                        className="fill-muted-foreground text-[9px] font-mono"
                      >
                        {t}
                      </text>
                    </g>
                  ))}
                </g>
              );
            })()}

            {/* Current time indicator */}
            {currentTime > 0 && currentTime <= maxTime && (() => {
              const chartWidth = 800 - LABEL_WIDTH - 20;
              const scale = maxTime > 0 ? chartWidth / maxTime : 1;
              const cx = LABEL_WIDTH + currentTime * scale;
              return (
                <line
                  x1={cx}
                  y1={TOP_PADDING}
                  x2={cx}
                  y2={TOP_PADDING + policies.length * ROW_HEIGHT}
                  className="stroke-red-500"
                  strokeWidth={2}
                  strokeDasharray="4,3"
                />
              );
            })()}
          </svg>

          {/* Tooltip */}
          {hoveredBlock && (
            <div
              className="fixed z-50 px-3 py-2 rounded-lg bg-card border border-border shadow-lg text-xs font-mono pointer-events-none"
              style={{
                left: hoveredBlock.x,
                top: hoveredBlock.y - 50,
                transform: 'translateX(-50%)',
              }}
            >
              {hoveredBlock.block.pid === -1 ? (
                <span className="text-muted-foreground">Idle: {hoveredBlock.block.start}–{hoveredBlock.block.end}</span>
              ) : (
                <div className="space-y-0.5">
                  <div className="font-semibold" style={{ color: getProcessColor(hoveredBlock.block.pid) }}>
                    P{hoveredBlock.block.pid}
                  </div>
                  <div className="text-muted-foreground">
                    t={hoveredBlock.block.start}–{hoveredBlock.block.end} (dur: {hoveredBlock.block.end - hoveredBlock.block.start})
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
