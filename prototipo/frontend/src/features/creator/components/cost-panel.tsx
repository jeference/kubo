"use client";

import { Coins } from "lucide-react";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useCreatorStore } from "@/features/creator/store";
import { formatUsd } from "@/lib/utils";

/** Running cost of the testing session, as reported by Runware (`includeCost`). */
export function CostPanel() {
  const costs = useCreatorStore((state) => state.costs);
  const total = costs.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="flex h-9 items-center gap-2 rounded-full border border-line bg-surface px-3 font-mono text-[12px] text-muted transition-colors hover:text-ink"
        >
          <Coins className="size-4" aria-hidden />
          {formatUsd(total)}
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-72">
        <p className="text-sm font-medium">Custo nesta sessão</p>
        {costs.length === 0 ? (
          <p className="mt-2 text-sm text-muted">Nenhuma chamada paga ainda.</p>
        ) : (
          <ul className="mt-2 max-h-64 space-y-1 overflow-y-auto text-sm">
            {costs.map((entry, index) => (
              <li key={index} className="flex justify-between gap-4">
                <span className="text-muted">{entry.label}</span>
                <span className="font-mono text-[12px]">{formatUsd(entry.value)}</span>
              </li>
            ))}
          </ul>
        )}
        <div className="mt-3 flex justify-between border-t border-line pt-2 text-sm font-medium">
          <span>Total</span>
          <span className="font-mono text-[12px]">{formatUsd(total)}</span>
        </div>
      </PopoverContent>
    </Popover>
  );
}
