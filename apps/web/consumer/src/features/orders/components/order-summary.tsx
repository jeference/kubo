import type { Schemas } from "@kubo/api-client";
import { formatBRL } from "@kubo/ui/lib/format";

type Shipment = Schemas["ShipmentInfo"] | null;

export function OrderSummary({
  items,
  subtotalCents,
  shippingCents,
  totalCents,
  shippingLabel,
  deliveryDays,
  shipment,
}: {
  items: Schemas["OrderItem"][];
  subtotalCents: number;
  shippingCents: number;
  totalCents: number;
  shippingLabel: string;
  deliveryDays: number;
  shipment: Shipment;
}) {
  return (
    <div className="space-y-4 rounded-2xl border border-line p-5">
      <h2 className="font-display text-lg font-semibold">Itens</h2>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.id} className="flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
            <img
              src={item.image_url}
              alt=""
              className="size-16 rounded-lg bg-sunken object-contain"
            />
            <span className="min-w-0 flex-1 text-sm">
              {item.size_label}
              <span className="block text-muted">Quantidade: {item.quantity}</span>
            </span>
            <span className="text-sm tabular-nums">{formatBRL(item.line_total_cents)}</span>
          </li>
        ))}
      </ul>
      <dl className="space-y-1.5 border-t border-line pt-3 text-sm">
        <div className="flex justify-between">
          <dt className="text-muted">Subtotal</dt>
          <dd className="tabular-nums">{formatBRL(subtotalCents)}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted">Frete ({shippingLabel})</dt>
          <dd className="tabular-nums">{formatBRL(shippingCents)}</dd>
        </div>
        <div className="flex justify-between pt-1.5 font-semibold">
          <dt>Total</dt>
          <dd className="tabular-nums">{formatBRL(totalCents)}</dd>
        </div>
      </dl>
      <p className="text-sm text-muted">
        Prazo: até {deliveryDays} dias úteis depois do pagamento, com a produção.
      </p>
      {shipment?.tracking_code && (
        <p className="rounded-xl bg-accent-soft p-3 text-sm">
          {shipment.carrier}: rastreio <strong>{shipment.tracking_code}</strong>
        </p>
      )}
    </div>
  );
}
