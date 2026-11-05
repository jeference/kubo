import * as React from "react";

import { cn } from "../lib/utils";

/** text-base no celular: o iOS dá zoom ao focar campos menores. */
const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-11 w-full rounded-xl border border-line bg-surface px-3.5 text-base outline-none transition-colors placeholder:text-muted/70 focus:border-accent disabled:cursor-not-allowed disabled:bg-sunken disabled:text-muted aria-[invalid=true]:border-danger lg:text-sm",
        className,
      )}
      ref={ref}
      {...props}
    />
  ),
);
Input.displayName = "Input";

export { Input };
