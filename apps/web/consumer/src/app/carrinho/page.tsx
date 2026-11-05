"use client";

import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatBRL } from "@kubo/ui/lib/format";
import { Skeleton } from "@kubo/ui/skeleton";
import { Minus, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import { useCart, useRemoveCartItem, useUpdateCartItem } from "@/features/cart/hooks";
import { messageOf } from "@/lib/errors";

export default function CartPage() {
  const { data: cart, isLoading } = useCart();
  const update = useUpdateCartItem();
  const remove = useRemoveCartItem();
  const onError = (error: unknown) => toast.error(messageOf(error));

  if (isLoading || !cart) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-28 w-full" />
      </div>
    );
  }

  const hasAvailable = cart.items.some((item) => !item.unavailable_reason);

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Carrinho</h1>

      {cart.items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            title="Seu carrinho está vazio"
            description="Crie uma peça e adicione aqui."
            action={
              <Button asChild variant="accent">
                <Link href="/">Criar agora</Link>
              </Button>
            }
          />
        </div>
      ) : (
        <>
          <ul className="mt-6 space-y-3">
            {cart.items.map((item) => (
              <li key={item.id} className="flex gap-4 rounded-2xl border border-line p-3">
                <Link href={`/criacoes/${item.creation_id}`} className="shrink-0">
                  {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                  <img
                    src={item.image_url}
                    alt=""
                    className="size-24 rounded-xl bg-sunken object-contain"
                  />
                </Link>
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{item.size_label}</p>
                  <p className="text-sm text-muted">{formatBRL(item.unit_price_cents)} cada</p>
                  {item.unavailable_reason ? (
                    <p className="mt-2 text-sm text-danger" role="alert">
                      {item.unavailable_reason}
                    </p>
                  ) : (
                    <div className="mt-2 inline-flex items-center border border-line">
                      <button
                        type="button"
                        aria-label="Diminuir quantidade"
                        disabled={item.quantity <= 1 || update.isPending}
                        onClick={() =>
                          update.mutate({ id: item.id, quantity: item.quantity - 1 }, { onError })
                        }
                        className="flex size-9 items-center justify-center hover:bg-sunken disabled:opacity-40"
                      >
                        <Minus className="size-4" />
                      </button>
                      <span className="w-8 text-center text-sm tabular-nums">{item.quantity}</span>
                      <button
                        type="button"
                        aria-label="Aumentar quantidade"
                        disabled={item.quantity >= 10 || update.isPending}
                        onClick={() =>
                          update.mutate({ id: item.id, quantity: item.quantity + 1 }, { onError })
                        }
                        className="flex size-9 items-center justify-center hover:bg-sunken disabled:opacity-40"
                      >
                        <Plus className="size-4" />
                      </button>
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-end justify-between">
                  <button
                    type="button"
                    aria-label="Remover do carrinho"
                    onClick={() => remove.mutate(item.id, { onError })}
                    className="flex size-8 items-center justify-center rounded-full text-muted hover:text-danger"
                  >
                    <Trash2 className="size-4" aria-hidden />
                  </button>
                  <p className="font-medium tabular-nums">
                    {item.unavailable_reason ? "" : formatBRL(item.line_total_cents)}
                  </p>
                </div>
              </li>
            ))}
          </ul>

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-line p-4">
            <div>
              <p className="text-sm text-muted">Subtotal</p>
              <p className="text-2xl font-semibold tabular-nums">
                {formatBRL(cart.subtotal_cents)}
              </p>
              <p className="text-xs text-muted">Frete calculado na finalização</p>
            </div>
            <Button asChild={hasAvailable} variant="accent" size="lg" disabled={!hasAvailable}>
              {hasAvailable ? <Link href="/checkout">Finalizar compra</Link> : "Finalizar compra"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
