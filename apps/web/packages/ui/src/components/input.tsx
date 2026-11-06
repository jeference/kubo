import * as React from "react";

import { cn } from "../lib/utils";

/** Campo branco com o mesmo contorno dos botões, que fica roxo ao focar. */
const FIELD =
  "w-full rounded-2xl border-2 border-stroke bg-surface px-4 text-base outline-none transition-colors placeholder:text-muted/70 hover:border-stroke-hover focus:border-accent disabled:cursor-not-allowed disabled:bg-sunken disabled:text-muted aria-[invalid=true]:border-danger lg:text-sm";

/** text-base no celular: o iOS dá zoom ao focar campos menores. */
const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => (
    <input type={type} className={cn(FIELD, "flex h-12", className)} ref={ref} {...props} />
  ),
);
Input.displayName = "Input";

const Textarea = React.forwardRef<HTMLTextAreaElement, React.ComponentProps<"textarea">>(
  ({ className, ...props }, ref) => (
    <textarea className={cn(FIELD, "block resize-none py-3", className)} ref={ref} {...props} />
  ),
);
Textarea.displayName = "Textarea";

export { Input, Textarea };
