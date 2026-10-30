"use client";

import { Box, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { CreditsButton } from "@/features/creator/components/credits-button";
import { ImagePickerStep } from "@/features/creator/components/image-picker-step";
import { ModelStep } from "@/features/creator/components/model-step";
import { PromptStep } from "@/features/creator/components/prompt-step";
import { Stepper } from "@/features/creator/components/stepper";
import { useCreatorStore } from "@/features/creator/store";

export function Creator() {
  const step = useCreatorStore((state) => state.step);
  const reset = useCreatorStore((state) => state.reset);

  return (
    <div className="min-h-dvh">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-2 font-display text-xl font-semibold tracking-tight">
            <Box className="size-6 text-accent" strokeWidth={2.2} aria-hidden />
            kubo
          </span>
          <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-medium text-accent">
            protótipo
          </span>
        </div>
        <div className="flex items-center gap-2">
          <CreditsButton />
          {step !== "create" && (
            <Button variant="ghost" size="sm" onClick={reset}>
              <RotateCcw />
              Recomeçar
            </Button>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 pb-16">
        <Stepper />
        <div key={step} className="mt-8 animate-fade-in">
          {step === "create" && <PromptStep />}
          {step === "pick" && <ImagePickerStep />}
          {step === "model" && <ModelStep />}
        </div>
      </main>
    </div>
  );
}
