"use client";

import { Button } from "@kubo/ui/button";
import { Card } from "@kubo/ui/card";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatBRL } from "@kubo/ui/lib/format";
import { QuantityStepper } from "@kubo/ui/quantity-stepper";
import { Skeleton } from "@kubo/ui/skeleton";
import { Lock, Trash2 } from "lucide-react";
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
              <Button asChild variant="primary">
                <Link href="/">Criar agora</Link>
              </Button>
            }
          />
        </div>
      ) : (
        <>
          <ul className="mt-6 space-y-3">
            {cart.items.map((item) => (
              <Card asChild key={item.id} className="flex gap-4 p-3">
                <li>
                  <Link href={`/criacoes/${item.creation_id}`} className="shrink-0">
                    {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                    <img
                      src={item.image_url}
                      alt=""
                      className="size-24 rounded-2xl bg-sunken object-contain"
                    />
                  </Link>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold">{item.size_label}</p>
                    <p className="text-sm text-muted">{formatBRL(item.unit_price_cents)} cada</p>
                    {item.unavailable_reason ? (
                      <p className="mt-2 text-sm text-danger" role="alert">
                        {item.unavailable_reason}
                      </p>
                    ) : (
                      <QuantityStepper
                        className="mt-2"
                        size="sm"
                        value={item.quantity}
                        max={10}
                        disabled={update.isPending}
                        onChange={(quantity) =>
                          update.mutate({ id: item.id, quantity }, { onError })
                        }
                      />
                    )}
                  </div>
                  <div className="flex flex-col items-end justify-between">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Remover do carrinho"
                      onClick={() => remove.mutate(item.id, { onError })}
                      className="hover:text-danger"
                    >
                      <Trash2 aria-hidden />
                    </Button>
                    <p className="font-semibold tabular-nums">
                      {item.unavailable_reason ? "" : formatBRL(item.line_total_cents)}
                    </p>
                  </div>
                </li>
              </Card>
            ))}
          </ul>

          <Card className="mt-6 flex flex-wrap items-center justify-between gap-4 p-5">
            <div>
              <p className="text-sm text-muted">Subtotal</p>
              <p className="text-2xl font-semibold tabular-nums">
                {formatBRL(cart.subtotal_cents)}
              </p>
              <p className="text-xs text-muted">Frete calculado na finalização</p>
            </div>
            <Button asChild={hasAvailable} variant="primary" size="lg" disabled={!hasAvailable}>
              {hasAvailable ? (
                <Link href="/checkout">
                  <Lock aria-hidden />
                  Finalizar compra
                </Link>
              ) : (
                <>
                  <Lock aria-hidden />
                  Finalizar compra
                </>
              )}
            </Button>
          </Card>
        </>
      )}
    </div>
  );
}
