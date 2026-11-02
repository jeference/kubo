"use client";

import { useIsMutating } from "@tanstack/react-query";
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
} from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

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

// Paced by time, not by the real progress: the provider does not report any.
const BUILD_STEPS = [
  "Estudando cada detalhe",
  "Aquecendo o bico da impressora",
  "Empilhando camadas",
  "Dando os últimos retoques",
];
const SECONDS_PER_STEP = 7;
// The 3D can take from 26 to 92 s: the last step keeps changing so it never looks stuck.
const LAST_STEP_PHRASES = [
  "Dando os últimos retoques",
  "Conferindo cada ângulo",
  "Caprichando no acabamento",
  "Quase lá, está ficando bom",
];
const SECONDS_PER_PHRASE = 8;

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
  const showsActions = !glbUrl && !isBuilding;

  return (
    <div>
      {showsActions && (
        <Button
          variant="outline"
          size="icon"
          aria-label="Voltar e mudar a descrição"
          className="mb-3 flex"
          onClick={() => setView("create")}
        >
          <ArrowLeft />
        </Button>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr] lg:gap-12">
        {/* min-w-0: the 3D canvas has a fixed pixel width and would stop the column shrinking. */}
        <section className="relative mx-auto w-full min-w-0 max-w-[560px]">
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
                className="absolute right-3 top-3 z-10 flex flex-col items-center gap-0.5 rounded-xl bg-surface/90 px-2.5 py-1.5 text-xs text-accent transition-colors hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50"
              >
                <Pencil className="size-4" aria-hidden />
                Editar
              </button>
            )}

            {!image && <div className="skeleton size-full" />}
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

        <aside className="lg:pt-2">
          {glbUrl ? (
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
              "flex h-8 w-16 items-center justify-center rounded-full text-sm font-semibold transition-colors",
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
        <h2 className="font-display text-3xl font-semibold tracking-tight">
          Seu objeto impresso em 3D
        </h2>
        <p className="mt-3 text-2xl font-semibold">A partir de {formatPrice(LOWEST_PRICE)}</p>
        <p className="mt-3 text-muted">
          O modelo 3D será construído a partir desta imagem. Quer mudar algo? Edite a imagem antes
          de gerar.
        </p>
      </div>
      {/* Pinned to the bottom on phones, like Jujubit's buy bar, so it never leaves the screen. */}
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-background p-4 lg:static lg:border-0 lg:bg-transparent lg:p-0">
        <Button
          variant="accent"
          size="lg"
          className="h-14 w-full text-base"
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

/** Seconds since the 3D task started, updated every second. */
function useBuildElapsed() {
  const startedAt = useCreatorStore((state) => state.modelStartedAt);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  return Math.max(0, Math.floor((now - (startedAt ?? now)) / 1000));
}

function BuildingNotice() {
  const elapsed = useBuildElapsed();
  const lastStep = BUILD_STEPS.length - 1;
  const currentStep = Math.min(Math.floor(elapsed / SECONDS_PER_STEP), lastStep);
  const lastStepSeconds = Math.max(0, elapsed - lastStep * SECONDS_PER_STEP);
  const phrase =
    LAST_STEP_PHRASES[Math.floor(lastStepSeconds / SECONDS_PER_PHRASE) % LAST_STEP_PHRASES.length];

  return (
    <div className="animate-fade-in space-y-5">
      <div className="space-y-2">
        <h2 className="font-display text-3xl font-semibold tracking-tight">
          Criando seu modelo 3D
        </h2>
        <p className="text-muted">Isso leva cerca de um minuto.</p>
      </div>
      <ol className="space-y-3">
        {BUILD_STEPS.map((step, index) => {
          const isCurrent = index === currentStep;
          const label = isCurrent && index === lastStep ? phrase : step;
          return (
            <li
              key={step}
              aria-current={isCurrent ? "step" : undefined}
              className={cn(
                "flex items-center gap-3",
                isCurrent && "font-medium",
                index > currentStep && "text-muted",
              )}
            >
              {index < currentStep && (
                <CheckCircle2 className="size-5 shrink-0 text-accent" aria-hidden />
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

function Building({ image }: { image: StoredImage }) {
  const elapsed = useBuildElapsed();

  return (
    <div className="flex size-full flex-col items-center justify-center text-center">
      <div className="relative size-64 overflow-hidden rounded-2xl border border-line bg-surface">
        {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
        <img src={image.url} alt="" className="size-full object-contain opacity-80" />
        <div className="absolute inset-x-0 top-0 h-16 animate-scan bg-gradient-to-b from-transparent via-accent/25 to-transparent" />
      </div>
      <p className="mt-3 font-mono text-xs text-muted" data-testid="elapsed">
        {elapsed}s
      </p>
    </div>
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
      <Button onClick={onRetry} pending={isRetrying}>
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
