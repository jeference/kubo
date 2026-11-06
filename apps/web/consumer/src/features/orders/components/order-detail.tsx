"use client";

import { ApiError } from "@kubo/api-client";
import { Callout } from "@kubo/ui/callout";
import { Card } from "@kubo/ui/card";
import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatDate } from "@kubo/ui/lib/format";
import { ORDER_STATUS } from "@kubo/ui/lib/status";
import { Skeleton } from "@kubo/ui/skeleton";
import { StatusBadge } from "@kubo/ui/status-badge";
import Link from "next/link";
import { useEffect, useRef } from "react";
import { toast } from "sonner";

import { OrderSummary } from "@/features/orders/components/order-summary";
import { OrderTimeline } from "@/features/orders/components/order-timeline";
import { PixPayment } from "@/features/orders/components/pix-payment";
import { useOrder, usePayOrder } from "@/features/orders/hooks";
import { messageOf } from "@/lib/errors";

/** Hub do pedido: o status decide o que aparece, inclusive o pagamento PIX. */
export function OrderDetail({ id }: { id: string }) {
  const { data: order, isLoading, isError } = useOrder(id);
  const pay = usePayOrder(id);
  const triedPay = useRef(false);
  const payMutate = pay.mutate;

  // Sem PIX válido em um pedido aguardando: gera. Só uma tentativa automática.
  const needsCharge =
    order?.status === "pending_payment" && (!order.charge || order.charge.status !== "pending");
  useEffect(() => {
    if (needsCharge && !triedPay.current) {
      triedPay.current = true;
      payMutate(undefined, { onError: (error) => toast.error(messageOf(error)) });
    }
  }, [needsCharge, payMutate]);

  if (isError) {
    return (
      <div className="mx-auto max-w-xl py-8">
        <EmptyState
          title="Pedido não encontrado"
          description="Use o link enviado ao seu e-mail, ou entre na sua conta."
          action={
            <Button asChild variant="primary">
              <Link href="/acompanhar">Acompanhar pedido</Link>
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
  const isPaidOrLater = !["pending_payment", "expired"].includes(order.status);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-display text-3xl font-semibold tracking-tight">
            Pedido {order.number}
          </h1>
          <StatusBadge label={badge.label} tone={badge.tone} />
        </div>
        <p className="mt-1 text-sm text-muted">Feito em {formatDate(order.created_at)}</p>
      </div>

      {order.status === "paid" && (
        <Callout tone="accent" role="status" className="p-4 text-base">
          <strong>Recebemos seu pagamento!</strong> Enviamos o link de acompanhamento para{" "}
          {order.customer_email}.
        </Callout>
      )}

      {order.status === "pending_payment" && order.charge?.status === "pending" && (
        <PixPayment charge={order.charge} />
      )}
      {needsCharge && !pay.isError && <Skeleton className="h-72 w-full" />}
      {needsCharge && pay.isError && (
        <Card className="space-y-3 p-5 text-center" role="alert">
          <p>Não conseguimos gerar o PIX agora.</p>
          <Button
            variant="primary"
            pending={pay.isPending}
            onClick={() =>
              pay.mutate(undefined, { onError: (error) => toast.error(messageOf(error)) })
            }
          >
            Tentar de novo
          </Button>
        </Card>
      )}

      {order.status === "expired" && (
        <Card className="space-y-3 p-5" role="alert">
          <p className="font-semibold">O prazo do PIX terminou</p>
          <p className="text-sm text-muted">Nada foi cobrado. Seus itens continuam no carrinho.</p>
          {order.can_renew_payment ? (
            <Button
              variant="primary"
              pending={pay.isPending}
              onClick={() =>
                pay.mutate(undefined, {
                  onError: (error) => {
                    toast.error(messageOf(error));
                    if (error instanceof ApiError && error.code === "order_too_old") {
                      window.location.assign("/carrinho");
                    }
                  },
                })
              }
            >
              Gerar novo PIX
            </Button>
          ) : (
            <Button asChild variant="primary">
              <Link href="/carrinho">Voltar ao carrinho</Link>
            </Button>
          )}
        </Card>
      )}

      {order.status === "refunded" && (
        <Callout role="status" className="p-4 text-base text-ink">
          Este pedido foi reembolsado. O valor volta para a conta usada no PIX.
        </Callout>
      )}

      {isPaidOrLater && <OrderTimeline status={order.status} />}

      <OrderSummary
        items={order.items}
        subtotalCents={order.subtotal_cents}
        shippingCents={order.shipping_cents}
        totalCents={order.total_cents}
        shippingLabel={order.shipping_service_name}
        deliveryDays={order.delivery_days}
        shipment={order.shipment}
      />

      <Card className="p-5 text-sm">
        <h2 className="font-display text-lg font-semibold">Entrega</h2>
        <p className="mt-2">{order.customer_name}</p>
        <p className="text-muted">
          {order.street}, {order.address_number}
          {order.complement ? `, ${order.complement}` : ""}
          <br />
          {order.neighborhood}, {order.city}/{order.state}
          <br />
          CEP {order.postal_code.slice(0, 5)}-{order.postal_code.slice(5)}
        </p>
        <p className="mt-2 text-muted">CPF {order.cpf_masked}</p>
      </Card>
    </div>
  );
}
