"use client";

import { Coins } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useCredits } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import { cn, formatUsd } from "@/lib/utils";

/** Runware credits: balance and all-time spend come from the account, session spend from the UI. */
export function CreditsButton() {
  const [open, setOpen] = useState(false);
  const sessionSpend = useCreatorStore((state) => state.sessionSpend);
  const credits = useCredits(open);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="focus-visible:outline-highlight">
          <Coins />
          Créditos
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-72 p-4">
        <p className="text-sm font-medium">Créditos Runware</p>

        {credits.isError ? (
          <div className="mt-3 space-y-2 text-sm">
            <p className="text-muted">Não foi possível consultar a Runware.</p>
            <Button variant="outline" size="sm" onClick={() => credits.refetch()}>
              Tentar de novo
            </Button>
          </div>
        ) : (
          <dl className="mt-3 space-y-3">
            <Row label="Saldo restante" value={credits.data?.balance} highlight />
            <Row label="Consumo total" value={credits.data?.total_spent} />
          </dl>
        )}
        <dl className="mt-3 border-t border-line pt-3">
          <Row label="Nesta sessão" value={sessionSpend} />
        </dl>

        <p className="mt-3 text-xs text-muted">
          Valores em dólar. A sessão conta desde que a página foi aberta.
        </p>
      </PopoverContent>
    </Popover>
  );
}

function Row({
  label,
  value,
  highlight = false,
}: {
  label: string;
  /** Undefined while loading. */
  value: number | undefined;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className={cn("font-mono", highlight ? "text-lg font-semibold" : "text-sm")}>
        {value === undefined ? (
          <span className="skeleton inline-block h-4 w-20 rounded" />
        ) : (
          formatUsd(value)
        )}
      </dd>
    </div>
  );
}
