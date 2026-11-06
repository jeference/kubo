import { Minus, Plus } from "lucide-react";

import { cn } from "../lib/utils";

const STEP =
  "flex size-9 items-center justify-center rounded-full text-ink transition-[background-color,transform] hover:bg-sunken active:scale-90 disabled:pointer-events-none disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

/** Contador em pílula com botões redondos de menos e mais. */
export function QuantityStepper({
  value,
  onChange,
  min = 1,
  max,
  disabled = false,
  size = "default",
  className,
}: {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max: number;
  disabled?: boolean;
  size?: "default" | "sm";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-full border-2 border-stroke bg-surface p-0.5",
        size === "sm" && "[&_button]:size-7",
        className,
      )}
    >
      <button
        type="button"
        aria-label="Diminuir quantidade"
        disabled={disabled || value <= min}
        onClick={() => onChange(value - 1)}
        className={STEP}
      >
        <Minus className="size-4" aria-hidden />
      </button>
      <span
        className={cn(
          "text-center font-semibold tabular-nums",
          size === "sm" ? "w-7 text-sm" : "w-9",
        )}
        aria-live="polite"
      >
        {value}
      </span>
      <button
        type="button"
        aria-label="Aumentar quantidade"
        disabled={disabled || value >= max}
        onClick={() => onChange(value + 1)}
        className={STEP}
      >
        <Plus className="size-4" aria-hidden />
      </button>
    </div>
  );
}
