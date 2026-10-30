"use client";

import { ArrowLeft, Download, Pause, Play, Plus, RotateCw } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useCreateModel, useModelStatus } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import type { StoredImage } from "@/features/creator/types";

const ModelViewer = dynamic(
  () => import("@/features/creator/components/model-viewer").then((m) => m.ModelViewer),
  { ssr: false, loading: () => <div className="skeleton size-full" /> },
);

const PROGRESS_MESSAGES = [
  "Lendo a imagem…",
  "Esculpindo a forma…",
  "Refinando os detalhes…",
  "Pintando a superfície…",
  "Quase lá…",
];

export function ModelStep() {
  const modelId = useCreatorStore((state) => state.modelId);
  const baseImage = useCreatorStore((state) => state.baseImage);
  const status = useModelStatus(modelId);
  const retry = useCreateModel();

  if (!baseImage) return null;

  const failed = status.isError || status.data?.status === "error";
  if (failed) {
    return (
      <Card className="mx-auto max-w-md space-y-4 p-8 text-center">
        <p className="font-display text-xl font-semibold">Não conseguimos gerar o modelo</p>
        <p className="text-sm text-muted">
          {status.error?.message || status.data?.error || "Tente de novo em instantes."}
        </p>
        <div className="flex justify-center gap-2">
          <BackButton variant="outline" />
          <Button onClick={() => retry.mutate(baseImage)} pending={retry.isPending}>
            <RotateCw />
            Tentar de novo
          </Button>
        </div>
      </Card>
    );
  }

  if (status.data?.status !== "success") {
    return <Generating key={modelId} image={baseImage} />;
  }

  return <ModelResult glbUrl={status.data.glb_url} image={baseImage} />;
}

/** Back to wherever the image came from: the picker, or the start for uploaded photos. */
function BackButton({ variant }: { variant: "outline" | "ghost" }) {
  const rounds = useCreatorStore((state) => state.rounds);
  const setStep = useCreatorStore((state) => state.setStep);
  return (
    <Button
      variant={variant}
      className={variant === "ghost" ? "w-full" : undefined}
      onClick={() => setStep(rounds.length > 0 ? "pick" : "create")}
    >
      <ArrowLeft />
      Escolher outra imagem
    </Button>
  );
}

function Generating({ image }: { image: StoredImage }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const started = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000);
    return () => clearInterval(timer);
  }, []);
  const message =
    PROGRESS_MESSAGES[Math.min(Math.floor(elapsed / 8), PROGRESS_MESSAGES.length - 1)];

  return (
    <div className="mx-auto flex max-w-md flex-col items-center text-center">
      <div className="relative size-64 overflow-hidden rounded-2xl border border-line bg-surface">
        {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
        <img src={image.url} alt="" className="size-full object-contain opacity-80" />
        <div className="absolute inset-x-0 top-0 h-16 animate-scan bg-gradient-to-b from-transparent via-accent/25 to-transparent" />
      </div>
      <p className="mt-6 font-display text-xl font-semibold">Criando seu modelo 3D</p>
      <p className="mt-1 text-muted">{message}</p>
      <div className="mt-5 h-1 w-56 overflow-hidden rounded-full bg-sunken">
        <div className="h-full w-1/3 animate-indeterminate rounded-full bg-accent" />
      </div>
      <p className="mt-3 font-mono text-xs text-muted">{elapsed}s</p>
    </div>
  );
}

function ModelResult({ glbUrl, image }: { glbUrl: string; image: StoredImage }) {
  const reset = useCreatorStore((state) => state.reset);
  const [autoRotate, setAutoRotate] = useState(true);

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
      <section>
        <h2 className="font-display text-2xl font-semibold tracking-tight">Seu modelo 3D</h2>
        <p className="mt-1 text-muted">Arraste para girar, role para aproximar.</p>

        <Card className="relative mt-6 h-[560px] overflow-hidden">
          <Button
            variant="outline"
            size="icon"
            className="absolute right-4 top-4 z-10"
            onClick={() => setAutoRotate((value) => !value)}
            aria-label={autoRotate ? "Pausar rotação" : "Girar automaticamente"}
          >
            {autoRotate ? <Pause /> : <Play />}
          </Button>
          <ModelViewer url={glbUrl} autoRotate={autoRotate} />
        </Card>
      </section>

      <aside className="lg:sticky lg:top-6 lg:self-start">
        <Card className="space-y-5 p-5">
          <div>
            <p className="text-sm font-medium">Imagem de origem</p>
            {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
            <img
              src={image.url}
              alt=""
              className="mt-2 aspect-square w-28 rounded-xl border border-line object-contain"
            />
          </div>

          <div className="space-y-2 border-t border-line pt-4">
            <Button variant="outline" className="w-full" asChild>
              <a href={glbUrl} download>
                <Download />
                Baixar GLB
              </a>
            </Button>
            <BackButton variant="ghost" />
            <Button variant="ghost" className="w-full" onClick={reset}>
              <Plus />
              Criar outro objeto
            </Button>
          </div>
        </Card>
      </aside>
    </div>
  );
}
