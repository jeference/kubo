import * as React from "react";

import { cn } from "../lib/utils";

/** Opção de escolha única em pílula (tamanho, filtro). O selecionado ganha o anel roxo. */
const Chip = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { selected: boolean }
>(({ className, selected, type = "button", ...props }, ref) => (
  <button
    ref={ref}
    type={type}
    aria-pressed={selected}
    className={cn(
      "inline-flex min-h-11 items-center justify-center rounded-full border-2 px-5 text-sm transition-[background-color,border-color,transform] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] disabled:pointer-events-none disabled:opacity-50 lg:min-h-10",
      selected
        ? "border-accent bg-accent-soft font-semibold text-ink"
        : "border-stroke bg-surface text-ink hover:border-stroke-hover",
      className,
    )}
    {...props}
  />
));
Chip.displayName = "Chip";

/** Grupo de chips com rótulo, como um fieldset. */
function ChipGroup({
  label,
  className,
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <fieldset className={className}>
      <legend className="text-sm font-semibold">{label}</legend>
      <div className="mt-2.5 flex flex-wrap gap-2">{children}</div>
    </fieldset>
  );
}

export { Chip, ChipGroup };
