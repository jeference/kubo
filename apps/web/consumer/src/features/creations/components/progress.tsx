"use client";

import { cn } from "@kubo/ui/lib/utils";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";

export type Progress = {
  title: string;
  subtitle: string;
  steps: string[];
  /** O último passo continua mudando, para uma geração lenta não parecer travada. */
  lastStepPhrases: string[];
  secondsPerStep: number;
  secondsPerPhrase: number;
};

// Passos pelo tempo decorrido, não pelo progresso real: o provedor não informa nenhum. Por isso
// mostramos etapas e segundos, nunca uma porcentagem inventada.
export const IMAGE_PROGRESS: Progress = {
  title: "Criando sua imagem",
  subtitle: "Isso leva alguns segundos. Pode sair desta página: sua criação continua aqui.",
  steps: [
    "Entendendo sua ideia",
    "Rascunhando o objeto",
    "Escolhendo as cores",
    "Caprichando nos detalhes",
  ],
  lastStepPhrases: [
    "Caprichando nos detalhes",
    "Ajustando a luz",
    "Conferindo o enquadramento",
    "Quase lá, está ficando bom",
  ],
  secondsPerStep: 3,
  secondsPerPhrase: 4,
};

export const MODEL_PROGRESS: Progress = {
  title: "Criando seu modelo 3D",
  subtitle: "Isso leva até 2 minutos. Pode sair desta página: sua criação continua aqui.",
  steps: [
    "Estudando cada detalhe",
    "Aquecendo o bico da impressora",
    "Empilhando camadas",
    "Dando os últimos retoques",
  ],
  lastStepPhrases: [
    "Dando os últimos retoques",
    "Conferindo cada ângulo",
    "Caprichando no acabamento",
    "Quase lá, está ficando bom",
  ],
  secondsPerStep: 7,
  secondsPerPhrase: 8,
};

/** Segundos desde o início da etapa, informado pelo servidor: sobrevive a recarregar a página. */
export function useElapsedSince(startedAt: string | null | undefined): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  if (!startedAt) return 0;
  return Math.max(0, Math.floor((now - new Date(startedAt).getTime()) / 1000));
}

export function ProgressNotice({ progress, elapsed }: { progress: Progress; elapsed: number }) {
  const { title, subtitle, steps, lastStepPhrases, secondsPerStep, secondsPerPhrase } = progress;
  const lastStep = steps.length - 1;
  const currentStep = Math.min(Math.floor(elapsed / secondsPerStep), lastStep);
  const lastStepSeconds = Math.max(0, elapsed - lastStep * secondsPerStep);
  const phrase =
    lastStepPhrases[Math.floor(lastStepSeconds / secondsPerPhrase) % lastStepPhrases.length];

  return (
    <div className="animate-fade-in space-y-5">
      <div className="space-y-2">
        <h2 className="font-display text-3xl font-semibold tracking-tight">{title}</h2>
        <p className="text-muted lg:text-sm">{subtitle}</p>
      </div>
      <ol className="space-y-3">
        {steps.map((step, index) => {
          const isCurrent = index === currentStep;
          const label = isCurrent && index === lastStep ? phrase : step;
          return (
            <li
              key={step}
              aria-current={isCurrent ? "step" : undefined}
              className={cn(
                "flex items-center gap-3 lg:text-sm",
                isCurrent && "font-medium",
                index > currentStep && "text-muted",
              )}
            >
              {index < currentStep && (
                <CheckCircle2 className="size-5 shrink-0 fill-highlight text-accent" aria-hidden />
              )}
              {isCurrent && (
                <Loader2 className="size-5 shrink-0 animate-spin text-accent" aria-hidden />
              )}
              {index > currentStep && <Circle className="size-5 shrink-0 text-line" aria-hidden />}
              <span key={label} className="animate-fade-in">
                {label}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export function ProgressFrame({ elapsed, children }: { elapsed: number; children: ReactNode }) {
  return (
    <div className="flex size-full flex-col items-center justify-center text-center">
      <div className="relative aspect-square w-3/4 overflow-hidden rounded-2xl border border-line bg-surface">
        {children}
        <div className="absolute inset-x-0 top-0 h-1/4 animate-scan bg-gradient-to-b from-transparent via-accent/25 to-transparent" />
      </div>
      <p className="mt-3 font-mono text-xs text-muted" data-testid="elapsed">
        {elapsed}s
      </p>
    </div>
  );
}
