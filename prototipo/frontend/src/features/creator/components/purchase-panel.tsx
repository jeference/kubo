"use client";

import { Download, Minus, Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { DEFAULT_SIZE, formatPrice, SIZES } from "@/features/creator/lib/sizes";
import { useCreatorStore } from "@/features/creator/store";
import { cn } from "@/lib/utils";

const MAX_QUANTITY = 10;

function showUnavailable() {
  // On top, because the default spot would cover the buttons pinned to the bottom on phones.
  toast.info("A compra ainda não está disponível neste protótipo.", { position: "top-center" });
}

/** Visual only: nothing here reaches the backend yet. */
export function PurchasePanel({ glbUrl }: { glbUrl: string }) {
  const reset = useCreatorStore((state) => state.reset);
  const [sizeId, setSizeId] = useState<string>(DEFAULT_SIZE.id);
  const [quantity, setQuantity] = useState(1);
  const size = SIZES.find((s) => s.id === sizeId) ?? DEFAULT_SIZE;

  return (
    // No animation on phones: its transform would move the pinned buttons while it runs.
    <div className="space-y-6 pb-10 lg:animate-fade-in lg:pb-0">
      <div>
        <h2 className="font-display text-3xl font-semibold tracking-tight">
          Seu objeto impresso em 3D
        </h2>
        <p className="mt-3 text-2xl font-semibold" data-testid="price">
          {formatPrice(size.price * quantity)}
        </p>
        <p className="mt-1 text-sm text-muted">Frete calculado na finalização</p>
      </div>

      <fieldset>
        <legend className="text-xs font-semibold uppercase tracking-widest">Tamanho</legend>
        <div className="mt-3 flex flex-wrap gap-2">
          {SIZES.map((option) => (
            <button
              key={option.id}
              type="button"
              aria-pressed={option.id === sizeId}
              onClick={() => setSizeId(option.id)}
              className={cn(
                "border px-4 py-2.5 text-sm transition-colors",
                option.id === sizeId
                  ? "border-ink font-medium text-ink"
                  : "border-line text-ink hover:border-ink/40",
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </fieldset>

      <div>
        <p className="text-xs font-semibold uppercase tracking-widest">Quantidade</p>
        <div className="mt-3 inline-flex items-center border border-line">
          <button
            type="button"
            aria-label="Diminuir quantidade"
            disabled={quantity <= 1}
            onClick={() => setQuantity(quantity - 1)}
            className="flex size-11 items-center justify-center transition-colors hover:bg-sunken disabled:opacity-40"
          >
            <Minus className="size-4" />
          </button>
          <span className="w-9 text-center text-sm tabular-nums" aria-live="polite">
            {quantity}
          </span>
          <button
            type="button"
            aria-label="Aumentar quantidade"
            disabled={quantity >= MAX_QUANTITY}
            onClick={() => setQuantity(quantity + 1)}
            className="flex size-11 items-center justify-center transition-colors hover:bg-sunken disabled:opacity-40"
          >
            <Plus className="size-4" />
          </button>
        </div>
      </div>

      {/* Pinned to the bottom on phones, like Jujubit's buy bar. */}
      <div className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-2 gap-3 border-t border-line bg-background p-4 lg:static lg:border-0 lg:bg-transparent lg:p-0">
        <Button
          size="lg"
          className="whitespace-normal px-3 text-sm leading-tight lg:px-7 lg:text-[15px]"
          onClick={showUnavailable}
        >
          Adicionar ao carrinho
        </Button>
        <Button
          variant="accent"
          size="lg"
          className="whitespace-normal px-3 text-sm leading-tight lg:px-7 lg:text-[15px]"
          onClick={showUnavailable}
        >
          Comprar agora
        </Button>
      </div>

      <div className="flex flex-wrap gap-2 border-t border-line pt-4">
        <Button variant="ghost" size="sm" asChild>
          <a href={glbUrl} download>
            <Download />
            Baixar GLB
          </a>
        </Button>
        <Button variant="ghost" size="sm" onClick={reset}>
          <Plus />
          Criar outro objeto
        </Button>
      </div>
    </div>
  );
}
