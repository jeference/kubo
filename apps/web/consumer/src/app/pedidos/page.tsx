"use client";

import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatBRL, formatDate } from "@kubo/ui/lib/format";
import { ORDER_STATUS } from "@kubo/ui/lib/status";
import { Skeleton } from "@kubo/ui/skeleton";
import { StatusBadge } from "@kubo/ui/status-badge";
import Link from "next/link";

import { useOrders } from "@/features/orders/hooks";

export default function OrdersPage() {
  const { data, isLoading } = useOrders();

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Pedidos</h1>
      {isLoading && <Skeleton className="mt-6 h-28 w-full" />}
      {data && data.results.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="Nenhum pedido por aqui"
            description="Comprou em outro navegador? Recupere o link pelo seu e-mail."
            action={
              <Button asChild variant="accent">
                <Link href="/acompanhar">Acompanhar pedido</Link>
              </Button>
            }
          />
        </div>
      )}
      {data && data.results.length > 0 && (
        <ul className="mt-6 space-y-3">
          {data.results.map((order) => {
            const badge = ORDER_STATUS[order.status];
            return (
              <li key={order.id}>
                <Link
                  href={`/pedidos/${order.id}`}
                  className="flex items-center gap-4 rounded-2xl border border-line p-3 transition-colors hover:border-ink/30"
                >
                  {order.thumbnail_url && (
                    // eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica
                    <img
                      src={order.thumbnail_url}
                      alt=""
                      className="size-16 rounded-xl bg-sunken object-contain"
                    />
                  )}
                  <span className="min-w-0 flex-1">
                    <span className="block font-medium">{order.number}</span>
                    <span className="block text-sm text-muted">
                      {formatDate(order.created_at)}, {order.item_count}{" "}
                      {order.item_count === 1 ? "peça" : "peças"}
                    </span>
                  </span>
                  <span className="flex flex-col items-end gap-1">
                    <StatusBadge label={badge.label} tone={badge.tone} />
                    <span className="text-sm font-medium tabular-nums">
                      {formatBRL(order.total_cents)}
                    </span>
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
