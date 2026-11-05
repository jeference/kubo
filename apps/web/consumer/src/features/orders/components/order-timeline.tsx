import { ORDER_STATUS, type OrderStatus } from "@kubo/ui/lib/status";
import { cn } from "@kubo/ui/lib/utils";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const STEPS: OrderStatus[] = ["paid", "in_production", "shipped", "delivered"];

export function OrderTimeline({ status }: { status: OrderStatus }) {
  if (status === "refunded" || status === "expired" || status === "pending_payment") {
    return null;
  }
  const current = STEPS.indexOf(status);

  return (
    <ol className="grid gap-3 sm:grid-cols-4" aria-label="Andamento do pedido">
      {STEPS.map((step, index) => {
        const done = index < current || status === "delivered";
        const isCurrent = index === current && status !== "delivered";
        return (
          <li
            key={step}
            aria-current={index === current ? "step" : undefined}
            className={cn(
              "flex items-center gap-2 text-sm sm:flex-col sm:items-start",
              isCurrent && "font-medium",
              !done && !isCurrent && "text-muted",
            )}
          >
            {done && (
              <CheckCircle2 className="size-5 shrink-0 fill-highlight text-accent" aria-hidden />
            )}
            {isCurrent && (
              <Loader2 className="size-5 shrink-0 animate-spin text-accent" aria-hidden />
            )}
            {!done && !isCurrent && <Circle className="size-5 shrink-0 text-line" aria-hidden />}
            {ORDER_STATUS[step].label}
          </li>
        );
      })}
    </ol>
  );
}
