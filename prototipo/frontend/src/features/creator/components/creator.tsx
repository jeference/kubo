"use client";

import { Box, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { CreditsButton } from "@/features/creator/components/credits-button";
import { PromptStep } from "@/features/creator/components/prompt-step";
import { Studio } from "@/features/creator/components/studio";
import { useCreatorStore } from "@/features/creator/store";

export function Creator() {
  const view = useCreatorStore((state) => state.view);
  const reset = useCreatorStore((state) => state.reset);

  return (
    <div className="min-h-dvh">
      <header className="bg-surface shadow-card">
        <div className="flex h-16 items-center justify-between px-6 lg:h-20 lg:px-9">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 font-display text-xl font-semibold tracking-tight lg:text-3xl">
              <Box className="size-6 text-accent lg:size-8" strokeWidth={2.2} aria-hidden />
              kubo
            </span>
            <span className="hidden rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-medium text-accent sm:inline">
              protótipo
            </span>
          </div>
          <div className="flex items-center gap-2">
            <CreditsButton />
            {view !== "create" && (
              <Button variant="ghost" size="sm" aria-label="Recomeçar" onClick={reset}>
                <RotateCcw />
                <span className="hidden sm:inline">Recomeçar</span>
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-6">
        <div key={view} className="animate-fade-in">
          {view === "create" && <PromptStep />}
          {view === "studio" && <Studio />}
        </div>
      </main>
    </div>
  );
}
