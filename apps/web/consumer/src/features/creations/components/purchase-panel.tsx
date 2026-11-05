"use client";

import { track } from "@kubo/analytics";
import { Button } from "@kubo/ui/button";
import { formatBRL } from "@kubo/ui/lib/format";
import { cn } from "@kubo/ui/lib/utils";
import { Minus, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { useAddToCart } from "@/features/cart/hooks";
import { useSizes } from "@/features/catalog/hooks";
import type { Creation } from "@/features/creations/types";
import { messageOf } from "@/lib/errors";

const MAX_QUANTITY = 10;

export function PurchasePanel({ creation }: { creation: Creation }) {
  const router = useRouter();
  const { data: sizes = [] } = useSizes();
  const add = useAddToCart();
  const [chosenId, setChosenId] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [buying, setBuying] = useState(false);

  const blocked = new Set(creation.blocked_size_ids);
  const available = sizes.filter((size) => !blocked.has(size.id));
  const size =
    available.find((option) => option.id === chosenId) ??
    available.find((option) => option.is_default) ??
    available[0];

  if (sizes.length > 0 && available.length === 0) {
    return (
      <div className="space-y-2 rounded-xl border border-line p-4" role="alert">
        <p className="font-medium">Este modelo não pode ser vendido</p>
        <p className="text-sm text-muted">
          A forma dele não permite uma impressão viável nos tamanhos disponíveis. Edite a imagem e
          gere o 3D de novo.
        </p>
      </div>
    );
  }

  function addToCart(buyNow: boolean) {
    if (!size) return;
    setBuying(buyNow);
    track(buyNow ? "buy_now_clicked" : "item_added_to_cart", { size: size.code, quantity });
    add.mutate(
      { creation_id: creation.id, size_id: size.id, quantity },
      {
        onSuccess: (item) => {
          if (buyNow) {
            router.push(`/checkout?item=${item.id}`);
            return;
          }
          toast.success("Adicionado ao carrinho.", {
            action: { label: "Ver carrinho", onClick: () => router.push("/carrinho") },
          });
        },
        onError: (error) => toast.error(messageOf(error)),
      },
    );
  }

  return (
    // Sem animação no celular: o transform moveria os botões fixos enquanto roda.
    <div className="space-y-6 pb-10 lg:animate-fade-in lg:pb-0">
      <div>
        <p className="text-2xl font-semibold lg:text-xl" data-testid="price">
          <span className="rounded-md bg-highlight px-2 py-0.5 text-accent">
            {size ? formatBRL(size.price_cents * quantity) : "…"}
          </span>
        </p>
        <p className="mt-1 text-sm text-muted lg:text-[13px]">Frete calculado na finalização</p>
      </div>

      <fieldset>
        <legend className="text-xs font-semibold uppercase tracking-widest">Tamanho</legend>
        <div className="mt-3 flex flex-wrap gap-2 lg:gap-3">
          {sizes.map((option) => {
            const isBlocked = blocked.has(option.id);
            return (
              <button
                key={option.id}
                type="button"
                aria-pressed={option.id === size?.id}
                disabled={isBlocked}
                title={isBlocked ? "Indisponível para este modelo" : undefined}
                onClick={() => {
                  setChosenId(option.id);
                  track("size_selected", { size: option.code });
                }}
                className={cn(
                  "border px-4 py-2.5 text-sm transition-colors lg:py-2 lg:text-[13.5px]",
                  option.id === size?.id
                    ? "border-ink font-medium text-ink"
                    : "border-line text-ink hover:border-ink/40",
                  isBlocked && "cursor-not-allowed text-muted line-through hover:border-line",
                )}
              >
                {option.label}
              </button>
            );
          })}
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
            className="flex size-11 items-center justify-center transition-colors hover:bg-sunken disabled:opacity-40 lg:size-9"
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
            className="flex size-11 items-center justify-center transition-colors hover:bg-sunken disabled:opacity-40 lg:size-9"
          >
            <Plus className="size-4" />
          </button>
        </div>
      </div>

      <p className="rounded-xl bg-sunken p-3 text-[13px] leading-snug text-muted">
        A prévia é uma aproximação. A peça é impressa em filamento com até 4 cores, então cores e
        detalhes podem ser diferentes da imagem.
      </p>

      {/* Fixos no rodapé do celular. */}
      <div className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-2 gap-3 border-t border-line bg-background p-4 lg:static lg:border-0 lg:bg-transparent lg:p-0">
        <Button
          size="lg"
          className="whitespace-normal px-3 text-sm leading-tight lg:h-11 lg:px-7"
          disabled={!size}
          pending={add.isPending && !buying}
          onClick={() => addToCart(false)}
        >
          Adicionar ao carrinho
        </Button>
        <Button
          variant="accent"
          size="lg"
          className="whitespace-normal px-3 text-sm leading-tight lg:h-11 lg:px-7"
          disabled={!size}
          pending={add.isPending && buying}
          onClick={() => addToCart(true)}
        >
          Comprar agora
        </Button>
      </div>
    </div>
  );
}
