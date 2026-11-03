import React from 'react';
import { useAppStore } from '@/store/store';
import { ALL_POLICIES, POLICY_COLORS, POLICY_LABELS } from '@/engine/types';
import type { Policy } from '@/engine/types';
import { cn } from '@/lib/utils';

export default function PolicySelector() {
  const { selectedPolicies, togglePolicy } = useAppStore();

  return (
    <div className="grid grid-cols-2 gap-2">
      {ALL_POLICIES.map((policy) => {
        const selected = selectedPolicies.includes(policy);
        const color = POLICY_COLORS[policy];
        return (
          <button
            key={policy}
            onClick={() => togglePolicy(policy)}
            className={cn(
              'flex flex-col items-start gap-0.5 rounded-lg border-2 px-3 py-2.5 text-left transition-all',
              selected
                ? 'border-current shadow-sm'
                : 'border-border/50 hover:border-border opacity-60 hover:opacity-80',
            )}
            style={{
              color: selected ? color : undefined,
              backgroundColor: selected ? `${color}15` : undefined,
            }}
          >
            <span className="text-sm font-semibold">{policy}</span>
            <span className={cn('text-[10px]', selected ? 'opacity-80' : 'text-muted-foreground')}>
              {POLICY_LABELS[policy].replace(policy + ' ', '').replace('(' , '').replace(')', '')}
            </span>
          </button>
        );
      })}
    </div>
  );
}
