import type { ReactNode } from "react";

import { cn } from "../lib/utils";

/** Opção de escolha única em cartão (frete, endereço): bolinha à esquerda, valor à direita. */
export function RadioCard({
  name,
  checked,
  onSelect,
  aside,
  children,
}: {
  name: string;
  checked: boolean;
  onSelect: () => void;
  aside?: ReactNode;
  children: ReactNode;
}) {
  return (
    <label
      className={cn(
        "flex cursor-pointer items-center justify-between gap-3 rounded-2xl border-2 p-4 transition-[background-color,border-color]",
        checked
          ? "border-accent bg-accent-soft"
          : "border-stroke bg-surface hover:border-stroke-hover",
      )}
    >
      <span className="flex items-center gap-3">
        <input
          type="radio"
          name={name}
          checked={checked}
          onChange={onSelect}
          className="size-5 shrink-0 cursor-pointer appearance-none rounded-full border-2 border-stroke-hover bg-surface transition-[border] checked:border-[6px] checked:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        />
        <span>{children}</span>
      </span>
      {aside && <span className="text-sm font-semibold tabular-nums">{aside}</span>}
    </label>
  );
}
