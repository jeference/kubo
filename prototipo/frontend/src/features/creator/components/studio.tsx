"use client";

import { useIsMutating } from "@tanstack/react-query";
import { Box, Loader2, Pause, Pencil, Play, RotateCw } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EditModal } from "@/features/creator/components/edit-modal";
import { PurchasePanel } from "@/features/creator/components/purchase-panel";
import { GENERATE_IMAGES_KEY, useCreateModel, useModelStatus } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import type { StoredImage, StudioTab } from "@/features/creator/types";
import { cn } from "@/lib/utils";

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

const TABS: Array<{ id: StudioTab; label: string }> = [
  { id: "2d", label: "2D" },
  { id: "3d", label: "3D" },
];

export function Studio() {
  const currentImage = useCreatorStore((state) => state.currentImage);
  const modelId = useCreatorStore((state) => state.modelId);
  const activeTab = useCreatorStore((state) => state.activeTab);
  const isGeneratingImage = useIsMutating({ mutationKey: GENERATE_IMAGES_KEY }) > 0;
  // Polled here, not in the 3D tab, so it keeps going on the 2D tab and behind the editor.
  const status = useModelStatus(modelId);
  const createModel = useCreateModel();
  const [isEditing, setIsEditing] = useState(false);

  const glbUrl = status.data?.status === "success" ? status.data.glb_url : null;
  const failed = status.isError || status.data?.status === "error";
  const isBuilding = Boolean(modelId) && !glbUrl && !failed;
  const errorMessage = status.error?.message || status.data?.error;
  const image = isGeneratingImage ? null : currentImage;

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_1fr] lg:gap-12">
      <section className="mx-auto w-full max-w-[560px]">
        {modelId && <TabSwitch isBuilding={isBuilding} />}

        <Card className={cn("relative aspect-square w-full overflow-hidden", modelId && "mt-4")}>
          {modelId && image && (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="absolute right-3 top-3 z-10 flex flex-col items-center gap-0.5 rounded-xl bg-surface/90 px-2.5 py-1.5 text-xs text-accent transition-colors hover:bg-accent-soft"
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
          <PurchasePanel glbUrl={glbUrl} />
        ) : isBuilding ? (
          <BuildingNotice />
        ) : (
          <ImageActions
            image={image}
            onEdit={() => setIsEditing(true)}
            onGenerate={(chosen) => createModel.mutate(chosen)}
            isStartingModel={createModel.isPending}
          />
        )}
      </aside>

      <EditModal open={isEditing} onClose={() => setIsEditing(false)} />
    </div>
  );
}

function TabSwitch({ isBuilding }: { isBuilding: boolean }) {
  const activeTab = useCreatorStore((state) => state.activeTab);
  const setActiveTab = useCreatorStore((state) => state.setActiveTab);

  return (
    <div className="flex animate-fade-in justify-center">
      <div role="tablist" className="flex rounded-full border border-accent/40 p-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={tab.id === activeTab}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex h-8 w-16 items-center justify-center gap-1.5 rounded-full text-sm font-semibold transition-colors",
              tab.id === activeTab ? "bg-accent text-white" : "text-accent hover:bg-accent-soft",
            )}
          >
            {tab.label}
            {tab.id === "3d" && isBuilding && (
              <Loader2 className="size-3 animate-spin" aria-label="Gerando" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

function ImageActions({
  image,
  onEdit,
  onGenerate,
  isStartingModel,
}: {
  image: StoredImage | null;
  onEdit: () => void;
  onGenerate: (image: StoredImage) => void;
  isStartingModel: boolean;
}) {
  const setView = useCreatorStore((state) => state.setView);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-3xl font-semibold tracking-tight">Sua imagem</h2>
        <p className="mt-2 text-muted">
          O modelo 3D será construído a partir dela. Quer mudar algo? Edite a imagem antes de gerar.
        </p>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <Button variant="outline" size="lg" disabled={!image} onClick={onEdit}>
          <Pencil />
          Editar imagem
        </Button>
        <Button
          variant="accent"
          size="lg"
          disabled={!image}
          pending={isStartingModel}
          onClick={() => image && onGenerate(image)}
        >
          <Box />
          Ficou ótimo! Gerar em 3D
        </Button>
      </div>
      <button
        type="button"
        onClick={() => setView("create")}
        className="text-sm text-muted underline-offset-4 hover:text-ink hover:underline"
      >
        Voltar e mudar a descrição
      </button>
    </div>
  );
}

function BuildingNotice() {
  return (
    <div className="animate-fade-in space-y-2">
      <h2 className="font-display text-3xl font-semibold tracking-tight">Criando seu modelo 3D</h2>
      <p className="text-muted">
        Isso leva cerca de um minuto. Enquanto isso, você pode voltar para a aba 2D e ver a imagem.
      </p>
    </div>
  );
}

function Building({ image }: { image: StoredImage }) {
  const startedAt = useCreatorStore((state) => state.modelStartedAt);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  const elapsed = Math.max(0, Math.floor((now - (startedAt ?? now)) / 1000));
  const message =
    PROGRESS_MESSAGES[Math.min(Math.floor(elapsed / 8), PROGRESS_MESSAGES.length - 1)];

  return (
    <div className="flex size-full flex-col items-center justify-center text-center">
      <div className="relative size-64 overflow-hidden rounded-2xl border border-line bg-surface">
        {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
        <img src={image.url} alt="" className="size-full object-contain opacity-80" />
        <div className="absolute inset-x-0 top-0 h-16 animate-scan bg-gradient-to-b from-transparent via-accent/25 to-transparent" />
      </div>
      <p className="mt-5 text-muted">{message}</p>
      <div className="mt-4 h-1 w-56 overflow-hidden rounded-full bg-sunken">
        <div className="h-full w-1/3 animate-indeterminate rounded-full bg-accent" />
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
