import { Check } from "lucide-react";
import * as React from "react";

import { cn } from "../lib/utils";

/** Caixa arredondada com o texto ao lado: o rótulo inteiro é clicável. */
const Checkbox = React.forwardRef<
  HTMLInputElement,
  Omit<React.ComponentProps<"input">, "type"> & { children: React.ReactNode }
>(({ className, children, ...props }, ref) => (
  <label
    className={cn("flex cursor-pointer items-start gap-2.5 text-[13px] leading-snug", className)}
  >
    <span className="relative mt-px flex size-5 shrink-0">
      <input
        ref={ref}
        type="checkbox"
        className="peer size-5 cursor-pointer appearance-none rounded-[7px] border-2 border-stroke-hover bg-surface transition-colors checked:border-accent checked:bg-accent hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        {...props}
      />
      <Check
        className="pointer-events-none absolute inset-0 m-auto size-3.5 text-white opacity-0 transition-opacity peer-checked:opacity-100"
        strokeWidth={3.5}
        aria-hidden
      />
    </span>
    <span>{children}</span>
  </label>
));
Checkbox.displayName = "Checkbox";

export { Checkbox };
