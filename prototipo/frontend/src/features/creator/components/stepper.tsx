"use client";

import { Check } from "lucide-react";

import { useCreatorStore } from "@/features/creator/store";
import type { Step } from "@/features/creator/types";
import { cn } from "@/lib/utils";

const STEPS: Array<{ id: Step; label: string }> = [
  { id: "create", label: "Ideia" },
  { id: "pick", label: "Imagem" },
  { id: "model", label: "Modelo 3D" },
];

export function Stepper() {
  const { step, setStep, rounds, modelId } = useCreatorStore();
  const currentIndex = STEPS.findIndex((s) => s.id === step);
  const available: Record<Step, boolean> = {
    create: true,
    pick: rounds.length > 0,
    model: modelId !== null,
  };

  return (
    <nav aria-label="Etapas">
      <ol className="flex items-center gap-2">
        {STEPS.map((s, index) => {
          const isCurrent = index === currentIndex;
          const isDone = index < currentIndex && available[s.id];
          return (
            <li key={s.id} className="flex flex-1 items-center gap-2 last:flex-none">
              <button
                type="button"
                disabled={!available[s.id] || isCurrent}
                onClick={() => setStep(s.id)}
                aria-current={isCurrent ? "step" : undefined}
                className={cn(
                  "flex items-center gap-2 rounded-full py-1 pl-1 pr-3 text-sm transition-colors",
                  isCurrent && "bg-surface font-medium text-ink shadow-sm",
                  !isCurrent && available[s.id] && "text-ink hover:bg-sunken",
                  !available[s.id] && "text-muted/60",
                )}
              >
                <span
                  className={cn(
                    "flex size-6 items-center justify-center rounded-full text-xs font-semibold",
                    isCurrent && "bg-accent text-white",
                    isDone && "bg-ink text-surface",
                    !isCurrent && !isDone && "bg-sunken text-muted",
                  )}
                >
                  {isDone ? <Check className="size-3.5" strokeWidth={3} /> : index + 1}
                </span>
                {s.label}
              </button>
              {index < STEPS.length - 1 && <span className="h-px flex-1 bg-line" aria-hidden />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
