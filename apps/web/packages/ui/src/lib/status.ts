import type { StatusTone } from "@kubo/design-tokens";

export type OrderStatus =
  | "pending_payment"
  | "paid"
  | "in_production"
  | "shipped"
  | "delivered"
  | "expired"
  | "refunded";

export type CreationStatus = "generating_image" | "image_failed" | "ready";

/** `Record` exaustivo: um status novo sem rótulo é erro de compilação. */
export const ORDER_STATUS: Record<OrderStatus, { label: string; tone: StatusTone }> = {
  pending_payment: { label: "Aguardando pagamento", tone: "neutral" },
  paid: { label: "Recebido", tone: "progress" },
  in_production: { label: "Em produção", tone: "progress" },
  shipped: { label: "Enviado", tone: "progress" },
  delivered: { label: "Entregue", tone: "success" },
  expired: { label: "Expirado", tone: "danger" },
  refunded: { label: "Reembolsado", tone: "danger" },
};

export const CREATION_STATUS: Record<CreationStatus, { label: string; tone: StatusTone }> = {
  generating_image: { label: "Gerando imagem", tone: "progress" },
  image_failed: { label: "Não deu certo", tone: "danger" },
  ready: { label: "Pronta para comprar", tone: "success" },
};
