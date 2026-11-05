import type { Metadata } from "next";
import { Suspense } from "react";

import { CheckoutForm } from "@/features/checkout/components/checkout-form";

export const metadata: Metadata = { title: "Finalizar compra", robots: { index: false } };

export default function CheckoutPage() {
  return (
    <Suspense>
      <CheckoutForm />
    </Suspense>
  );
}
