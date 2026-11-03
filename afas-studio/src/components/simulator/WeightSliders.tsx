import React from 'react';
import { RotateCcw, Info } from 'lucide-react';
import { useAppStore } from '@/store/store';
import { DEFAULT_WEIGHTS, DEFAULT_QUANTUM } from '@/engine/types';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

const WEIGHT_INFO = {
  wp: { label: 'Priority (wp)', tip: 'Weight for static priority component Pi = priority/10' },
  wa: { label: 'Aging (wa)', tip: 'Weight for aging component. Prevents starvation by boosting long-waiting processes' },
  wr: { label: 'Responsiveness (wr)', tip: 'Weight for process class. Interactive=1.0, Mixed=0.5, Batch=0.2' },
  wc: { label: 'CPU Usage (wc)', tip: 'Penalty for recent CPU consumption. Decays with half-life of 40 time units' },
};

export default function WeightSliders() {
  const { weights, setWeights, resetWeights, quantum, setQuantum } = useAppStore();

  const handleWeightChange = (key: keyof typeof weights, value: number) => {
    const newWeights = { ...weights, [key]: value };
    // Normalize to sum 1.0
    const sum = newWeights.wp + newWeights.wa + newWeights.wr + newWeights.wc;
    if (sum > 0) {
      newWeights.wp = newWeights.wp / sum;
      newWeights.wa = newWeights.wa / sum;
      newWeights.wr = newWeights.wr / sum;
      newWeights.wc = newWeights.wc / sum;
    }
    setWeights(newWeights);
  };

  return (
    <div className="space-y-4">
      {/* Time Quantum */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            Time Quantum
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent>Time slice for Round Robin and AFAS policies</TooltipContent>
            </Tooltip>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <Slider
              value={[quantum]}
              min={1}
              max={32}
              step={1}
              onValueChange={([v]) => setQuantum(v)}
              className="flex-1"
            />
            <span className="font-mono text-sm font-semibold min-w-[32px] text-right">
              {quantum}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* AFAS Weights */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">AFAS Weights</CardTitle>
            <Button variant="ghost" size="sm" onClick={resetWeights} className="h-7 gap-1.5 text-xs">
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {(Object.keys(WEIGHT_INFO) as Array<keyof typeof WEIGHT_INFO>).map((key) => (
            <div key={key} className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs flex items-center gap-1.5">
                  {WEIGHT_INFO[key].label}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-[220px]">{WEIGHT_INFO[key].tip}</TooltipContent>
                  </Tooltip>
                </Label>
                <span className="font-mono text-xs text-emerald-400 font-semibold">
                  {weights[key].toFixed(2)}
                </span>
              </div>
              <Slider
                value={[weights[key]]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={([v]) => handleWeightChange(key, v)}
              />
            </div>
          ))}
          <div className="text-center text-xs text-muted-foreground font-mono pt-1">
            Sum: {(weights.wp + weights.wa + weights.wr + weights.wc).toFixed(2)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
