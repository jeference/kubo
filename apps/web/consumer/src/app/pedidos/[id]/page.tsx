import type { Metadata } from "next";

import { OrderDetail } from "@/features/orders/components/order-detail";

export const metadata: Metadata = { title: "Seu pedido", robots: { index: false } };

export default async function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <OrderDetail id={id} />;
}
