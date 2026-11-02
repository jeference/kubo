"use client";

import { useIsMutating, useMutationState } from "@tanstack/react-query";
import {
  ArrowLeft,
  Box,
  CheckCircle2,
  Circle,
  Loader2,
  Pause,
  Pencil,
  Play,
  RotateCw,
  Sparkles,
} from "lucide-react";
import dynamic from "next/dynamic";
import { type ReactNode, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EditModal } from "@/features/creator/components/edit-modal";
import { PurchasePanel } from "@/features/creator/components/purchase-panel";
import { GENERATE_IMAGES_KEY, useCreateModel, useModelStatus } from "@/features/creator/hooks";
import { formatPrice, LOWEST_PRICE } from "@/features/creator/lib/sizes";
import { useCreatorStore } from "@/features/creator/store";
import type { StoredImage, StudioTab } from "@/features/creator/types";
import { cn } from "@/lib/utils";

const ModelViewer = dynamic(
  () => import("@/features/creator/components/model-viewer").then((m) => m.ModelViewer),
  { ssr: false, loading: () => <div className="skeleton size-full" /> },
);

type Progress = {
  title: string;
  subtitle: string;
  steps: string[];
  /** The last step keeps changing, so a slow generation never looks stuck. */
  lastStepPhrases: string[];
  secondsPerStep: number;
  secondsPerPhrase: number;
};

// Paced by time, not by the real progress: the provider does not report any.
const IMAGE_PROGRESS: Progress = {
  title: "Criando sua imagem",
  subtitle: "Isso leva alguns segundos.",
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

const MODEL_PROGRESS: Progress = {
  title: "Criando seu modelo 3D",
  subtitle: "Isso leva cerca de um minuto.",
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

const TABS: Array<{ id: StudioTab; label: string }> = [
  { id: "2d", label: "2D" },
  { id: "3d", label: "3D" },
];

export function Studio() {
  const currentImage = useCreatorStore((state) => state.currentImage);
  const modelId = useCreatorStore((state) => state.modelId);
  const activeTab = useCreatorStore((state) => state.activeTab);
  const setView = useCreatorStore((state) => state.setView);
  const isGeneratingImage = useIsMutating({ mutationKey: GENERATE_IMAGES_KEY }) > 0;
  const status = useModelStatus(modelId);
  const createModel = useCreateModel();
  const [isEditing, setIsEditing] = useState(false);

  const glbUrl = status.data?.status === "success" ? status.data.glb_url : null;
  const failed = status.isError || status.data?.status === "error";
  const isBuilding = Boolean(modelId) && !glbUrl && !failed;
  const errorMessage = status.error?.message || status.data?.error;
  const image = isGeneratingImage ? null : currentImage;
  const showsActions = !glbUrl && !isBuilding && !isGeneratingImage;

  return (
    <div>
      {/* The first column is exactly the image, so the gap to the panel is always the same.
          The image follows the window width like Jujubit's, and the height so it is seen whole. */}
      <div className="grid gap-y-6 lg:grid-cols-[min(900px,42vw,max(400px,calc(100dvh-10rem)))_minmax(0,675px)] lg:justify-center lg:gap-x-[min(4vw,72px)]">
        {showsActions && (
          <Button
            variant="outline"
            size="icon"
            aria-label="Voltar e mudar a descrição"
            className="-mb-3 justify-self-start lg:col-span-2"
            onClick={() => setView("create")}
          >
            <ArrowLeft />
          </Button>
        )}

        {/* min-w-0: the 3D canvas has a fixed pixel width and would stop the column shrinking. */}
        <section className="relative mx-auto w-full min-w-0 max-w-[560px] lg:max-w-none">
          {glbUrl && <TabSwitch />}

          <Card
            className={cn("relative aspect-square w-full overflow-hidden", glbUrl && "lg:mt-4")}
          >
            {!isBuilding && image && (
              <button
                type="button"
                aria-label="Editar imagem"
                disabled={createModel.isPending}
                onClick={() => setIsEditing(true)}
                className="absolute right-3 top-3 z-10 flex flex-col items-center gap-0.5 rounded-xl bg-surface/90 px-2.5 py-1.5 text-xs text-accent transition-colors hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50 lg:px-3 lg:py-2"
              >
                <Pencil className="size-4 lg:size-[22px]" aria-hidden />
                Editar
              </button>
            )}

            {!image && <GeneratingImage />}
            {image && activeTab === "2d" && (
              // eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django
              <img src={image.url} alt="Imagem 2D do objeto" className="size-full object-contain" />
            )}
            {image && activeTab === "3d" && isBuilding && <Building image={image} />}
            {image && activeTab === "3d" && failed && (
              <BuildError
                message={errorMessage}
                onRetry={() => createModel.mutate(image)}
                isRetrying={createModel.isPending}
              />
            )}
            {activeTab === "3d" && glbUrl && <Viewer glbUrl={glbUrl} />}
          </Card>
        </section>

        {/* The panel starts below the top of the image, about as far as Jujubit's. The tabs and their margin
            (50px) only sit above the image once the model is ready. */}
        <aside className={cn("lg:pt-[60px]", glbUrl && "lg:pt-[110px]")}>
          {isGeneratingImage ? (
            <GeneratingImageNotice />
          ) : glbUrl ? (
            <PurchasePanel />
          ) : isBuilding ? (
            <BuildingNotice />
          ) : (
            <ImageActions
              image={image}
              onGenerate={(chosen) => createModel.mutate(chosen)}
              isStartingModel={createModel.isPending}
            />
          )}
        </aside>
      </div>

      <EditModal open={isEditing} onClose={() => setIsEditing(false)} />
    </div>
  );
}

function TabSwitch() {
  const activeTab = useCreatorStore((state) => state.activeTab);
  const setActiveTab = useCreatorStore((state) => state.setActiveTab);

  return (
    // On phones it sits inside the image, on the corner opposite the edit button.
    <div className="absolute left-3 top-3 z-10 flex animate-fade-in lg:static lg:justify-center">
      <div role="tablist" className="flex rounded-full border border-accent/40 bg-surface/90 p-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={tab.id === activeTab}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex h-8 w-16 items-center justify-center rounded-full text-sm font-semibold transition-colors lg:h-7 lg:w-14 lg:text-xs",
              tab.id === activeTab ? "bg-accent text-white" : "text-accent hover:bg-accent-soft",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function ImageActions({
  image,
  onGenerate,
  isStartingModel,
}: {
  image: StoredImage | null;
  onGenerate: (image: StoredImage) => void;
  isStartingModel: boolean;
}) {
  return (
    <div className="space-y-6 pb-10 lg:pb-0">
      <div>
        <p className="text-2xl font-semibold lg:text-xl">
          A partir de{" "}
          <span className="rounded-md bg-highlight px-2 py-0.5 text-accent">
            {formatPrice(LOWEST_PRICE)}
          </span>
        </p>
        <p className="mt-3 text-muted lg:text-sm">
          O modelo 3D será construído a partir desta imagem. Quer mudar algo? Edite a imagem antes
          de gerar.
        </p>
      </div>
      {/* Pinned to the bottom on phones, like Jujubit's buy bar, so it never leaves the screen. */}
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-background p-4 lg:static lg:border-0 lg:bg-transparent lg:p-0">
        <Button
          variant="accent"
          size="lg"
          className="h-14 w-full text-base lg:h-12 lg:text-[15px]"
          disabled={!image}
          pending={isStartingModel}
          onClick={() => image && onGenerate(image)}
        >
          <Box />
          Ficou ótimo! Gerar em 3D
        </Button>
      </div>
    </div>
  );
}

/** Seconds since `startedAt`, updated every second. */
function useElapsedSince(startedAt: number | null) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  return Math.max(0, Math.floor((now - (startedAt ?? now)) / 1000));
}

function useImageElapsed() {
  const submittedAt = useMutationState({
    filters: { mutationKey: GENERATE_IMAGES_KEY, status: "pending" },
    select: (mutation) => mutation.state.submittedAt,
  });
  return useElapsedSince(submittedAt.at(-1) ?? null);
}

function useModelElapsed() {
  return useElapsedSince(useCreatorStore((state) => state.modelStartedAt));
}

function GeneratingImageNotice() {
  return <ProgressNotice progress={IMAGE_PROGRESS} elapsed={useImageElapsed()} />;
}

function BuildingNotice() {
  return <ProgressNotice progress={MODEL_PROGRESS} elapsed={useModelElapsed()} />;
}

function ProgressNotice({ progress, elapsed }: { progress: Progress; elapsed: number }) {
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

function ProgressFrame({ elapsed, children }: { elapsed: number; children: ReactNode }) {
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

function GeneratingImage() {
  return (
    <ProgressFrame elapsed={useImageElapsed()}>
      <div className="skeleton flex size-full items-center justify-center">
        <Sparkles className="size-10 animate-pulse text-accent/60" aria-hidden />
      </div>
    </ProgressFrame>
  );
}

function Building({ image }: { image: StoredImage }) {
  return (
    <ProgressFrame elapsed={useModelElapsed()}>
      {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
      <img src={image.url} alt="" className="size-full object-contain opacity-80" />
    </ProgressFrame>
  );
}

function BuildError({
  message,
  onRetry,
  isRetrying,
}: {
  message: string | undefined;
  onRetry: () => void;
  isRetrying: boolean;
}) {
  return (
    <div className="flex size-full flex-col items-center justify-center gap-4 p-8 text-center">
      <p className="font-display text-xl font-semibold">Não conseguimos gerar o modelo</p>
      <p className="text-sm text-muted">{message || "Tente de novo em instantes."}</p>
      <Button variant="accent" onClick={onRetry} pending={isRetrying}>
        <RotateCw />
        Tentar de novo
      </Button>
    </div>
  );
}

function Viewer({ glbUrl }: { glbUrl: string }) {
  const [autoRotate, setAutoRotate] = useState(true);

  return (
    <>
      <Button
        variant="outline"
        size="icon"
        className="absolute bottom-3 right-3 z-10"
        onClick={() => setAutoRotate((value) => !value)}
        aria-label={autoRotate ? "Pausar rotação" : "Girar automaticamente"}
      >
        {autoRotate ? <Pause /> : <Play />}
      </Button>
      <ModelViewer url={glbUrl} autoRotate={autoRotate} />
    </>
  );
}
