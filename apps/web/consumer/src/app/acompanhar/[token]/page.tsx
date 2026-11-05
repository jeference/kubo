"use client";

import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatDate } from "@kubo/ui/lib/format";
import { ORDER_STATUS } from "@kubo/ui/lib/status";
import { Skeleton } from "@kubo/ui/skeleton";
import { StatusBadge } from "@kubo/ui/status-badge";
import Link from "next/link";
import { use } from "react";

import { OrderSummary } from "@/features/orders/components/order-summary";
import { OrderTimeline } from "@/features/orders/components/order-timeline";
import { useTracking } from "@/features/orders/hooks";

export default function TrackingPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const { data: order, isLoading, isError } = useTracking(token);

  if (isError) {
    return (
      <div className="mx-auto max-w-xl py-8">
        <EmptyState
          title="Link inválido"
          description="Peça um novo link com o e-mail usado na compra."
          action={
            <Button asChild variant="accent">
              <Link href="/acompanhar">Pedir novo link</Link>
            </Button>
          }
        />
      </div>
    );
  }
  if (isLoading || !order) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <Skeleton className="h-8 w-56" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const badge = ORDER_STATUS[order.status];
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-display text-3xl font-semibold tracking-tight">
            Pedido {order.number}
          </h1>
          <StatusBadge label={badge.label} tone={badge.tone} />
        </div>
        <p className="mt-1 text-sm text-muted">
          Feito em {formatDate(order.created_at)}. Entrega em {order.address_masked}.
        </p>
      </div>
      <OrderTimeline status={order.status} />
      <OrderSummary
        items={order.items}
        subtotalCents={order.subtotal_cents}
        shippingCents={order.shipping_cents}
        totalCents={order.total_cents}
        shippingLabel={order.shipping_service_name}
        deliveryDays={order.delivery_days}
        shipment={order.shipment}
      />
    </div>
  );
}
