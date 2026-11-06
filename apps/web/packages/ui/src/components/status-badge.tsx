import type { StatusTone } from "@kubo/design-tokens";

import { cn } from "../lib/utils";

const TONES: Record<StatusTone, string> = {
  neutral: "bg-sunken text-ink",
  progress: "bg-accent-soft text-accent",
  success: "bg-success/10 text-success",
  danger: "bg-danger/10 text-danger",
};

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold",
        TONES[tone],
      )}
    >
      {label}
    </span>
  );
}
