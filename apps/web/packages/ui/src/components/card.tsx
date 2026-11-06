import { Slot } from "@radix-ui/react-slot";
import * as React from "react";

import { cn } from "../lib/utils";

/** Painel branco arredondado: toda caixa de conteúdo da plataforma é um Card. */
const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { asChild?: boolean }
>(({ className, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "div";
  return (
    <Comp
      ref={ref}
      className={cn("rounded-2xl border border-line bg-surface shadow-card", className)}
      {...props}
    />
  );
});
Card.displayName = "Card";

export { Card };
