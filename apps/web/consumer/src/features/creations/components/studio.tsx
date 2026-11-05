"use client";

import { Button } from "@kubo/ui/button";
import { Card } from "@kubo/ui/card";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatBRL } from "@kubo/ui/lib/format";
import { cn } from "@kubo/ui/lib/utils";
import { Skeleton } from "@kubo/ui/skeleton";
import { ArrowLeft, Box, Pause, Pencil, Play, RotateCw, Sparkles } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { useSizes } from "@/features/catalog/hooks";
import { EditModal } from "@/features/creations/components/edit-modal";
import {
  IMAGE_PROGRESS,
  MODEL_PROGRESS,
  ProgressFrame,
  ProgressNotice,
  useElapsedSince,
} from "@/features/creations/components/progress";
import { PurchasePanel } from "@/features/creations/components/purchase-panel";
import { useCreation, useCreationAction } from "@/features/creations/hooks";
import type { Creation } from "@/features/creations/types";
import { messageOf } from "@/lib/errors";

const ModelViewer = dynamic(
  () => import("@/features/creations/components/model-viewer").then((m) => m.ModelViewer),
  { ssr: false, loading: () => <div className="skeleton size-full" /> },
);

type StudioTab = "2d" | "3d";
const TABS: Array<{ id: StudioTab; label: string }> = [
  { id: "2d", label: "2D" },
  { id: "3d", label: "3D" },
];

/** Hub da criação: o que aparece depende só do status vindo do servidor. */
export function Studio({ id }: { id: string }) {
  const { data: creation, isLoading, isError } = useCreation(id);

  if (isError) {
    return (
      <div className="mx-auto max-w-xl py-12">
        <EmptyState
          title="Criação não encontrada"
          description="Ela pode ter sido excluída, ou foi feita em outro navegador. Entre na sua conta para ver as criações de outros dispositivos."
          action={
            <Button asChild variant="accent">
              <Link href="/">Criar algo novo</Link>
            </Button>
          }
        />
      </div>
    );
  }
  if (isLoading || !creation) {
    return (
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-2">
        <Skeleton className="aspect-square w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  return <StudioContent creation={creation} />;
}

function StudioContent({ creation }: { creation: Creation }) {
  const router = useRouter();
  const actions = useCreationAction(creation.id);
  const { status } = creation;
  const isGeneratingImage = status === "generating_image";
  const isBuilding = status === "generating_model";
  const isReady = status === "ready";
  const image = creation.versions.find((v) => v.id === creation.current_version_id) ?? null;
  const glbUrl = isReady ? (creation.model?.glb_url ?? null) : null;
  const canEdit = status === "awaiting_approval" || isReady;
  const elapsed = useElapsedSince(creation.active_started_at);

  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<StudioTab>(
    isReady || isBuilding || status === "model_failed" ? "3d" : "2d",
  );

  // Cada mudança de etapa leva à aba que importa naquele momento.
  useEffect(() => {
    setActiveTab(isReady || isBuilding || status === "model_failed" ? "3d" : "2d");
  }, [status, isBuilding, isReady]);

  const showsBack = status === "awaiting_approval" || status === "image_failed";

  function run(mutate: () => Promise<unknown>) {
    mutate().catch((error) => toast.error(messageOf(error)));
  }

  return (
    <div>
      {/* A primeira coluna é exatamente a imagem: a distância até o painel é sempre a mesma. */}
      <div className="grid gap-y-6 lg:grid-cols-[min(900px,42vw,max(400px,calc(100dvh-10rem)))_minmax(0,675px)] lg:justify-center lg:gap-x-[min(4vw,72px)]">
        {showsBack && (
          <Button
            variant="outline"
            size="icon"
            aria-label="Voltar e começar outra criação"
            className="-mb-3 justify-self-start lg:col-span-2"
            onClick={() => router.push("/")}
          >
            <ArrowLeft />
          </Button>
        )}

        {/* min-w-0: o canvas 3D tem largura fixa em pixels e impediria a coluna de encolher. */}
        <section className="relative mx-auto w-full min-w-0 max-w-[560px] lg:max-w-none">
          {glbUrl && <TabSwitch active={activeTab} onChange={setActiveTab} />}

          <Card
            className={cn("relative aspect-square w-full overflow-hidden", glbUrl && "lg:mt-4")}
          >
            {canEdit && image && (
              <button
                type="button"
                aria-label="Editar imagem"
                onClick={() => setIsEditing(true)}
                className="absolute right-3 top-3 z-10 flex flex-col items-center gap-0.5 rounded-xl bg-surface/90 px-2.5 py-1.5 text-xs text-accent transition-colors hover:bg-accent-soft lg:px-3 lg:py-2"
              >
                <Pencil className="size-4 lg:size-[22px]" aria-hidden />
                Editar
              </button>
            )}

            {isGeneratingImage && (
              <ProgressFrame elapsed={elapsed}>
                <div className="skeleton flex size-full items-center justify-center">
                  <Sparkles className="size-10 animate-pulse text-accent/60" aria-hidden />
                </div>
              </ProgressFrame>
            )}
            {status === "image_failed" && (
              <FailureMessage
                title="Não conseguimos criar a imagem"
                creation={creation}
                onRetry={() => run(() => actions.retry.mutateAsync())}
                isRetrying={actions.retry.isPending}
              />
            )}
            {image && activeTab === "2d" && status !== "image_failed" && (
              // eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica, URL assinada
              <img
                src={image.image_url}
                alt="Imagem 2D do objeto"
                className="size-full object-contain"
              />
            )}
            {image && activeTab === "3d" && isBuilding && (
              <ProgressFrame elapsed={elapsed}>
                {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                <img src={image.image_url} alt="" className="size-full object-contain opacity-80" />
              </ProgressFrame>
            )}
            {activeTab === "3d" && status === "model_failed" && (
              <FailureMessage
                title="Não conseguimos gerar o modelo"
                creation={creation}
                onRetry={() => run(() => actions.retry.mutateAsync())}
                isRetrying={actions.retry.isPending}
                onBack={() => run(() => actions.back.mutateAsync())}
              />
            )}
            {activeTab === "3d" && glbUrl && <Viewer glbUrl={glbUrl} />}
          </Card>
        </section>

        {/* O painel começa abaixo do topo da imagem; as abas só existem com o modelo pronto. */}
        <aside className={cn("lg:pt-[60px]", glbUrl && "lg:pt-[110px]")}>
          {isGeneratingImage && <ProgressNotice progress={IMAGE_PROGRESS} elapsed={elapsed} />}
          {isBuilding && <ProgressNotice progress={MODEL_PROGRESS} elapsed={elapsed} />}
          {isReady && <PurchasePanel creation={creation} />}
          {status === "awaiting_approval" && (
            <ImageActions
              onGenerate={() => run(() => actions.approve.mutateAsync())}
              isStarting={actions.approve.isPending}
              hasModel={Boolean(creation.model)}
            />
          )}
        </aside>
      </div>

      <EditModal creation={creation} open={isEditing} onClose={() => setIsEditing(false)} />
    </div>
  );
}

function TabSwitch({
  active,
  onChange,
}: {
  active: StudioTab;
  onChange: (tab: StudioTab) => void;
}) {
  return (
    // No celular, fica dentro da imagem, no canto oposto ao botão de editar.
    <div className="absolute left-3 top-3 z-10 flex animate-fade-in lg:static lg:justify-center">
      <div role="tablist" className="flex rounded-full border border-accent/40 bg-surface/90 p-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={tab.id === active}
            onClick={() => onChange(tab.id)}
            className={cn(
              "flex h-8 w-16 items-center justify-center rounded-full text-sm font-semibold transition-colors lg:h-7 lg:w-14 lg:text-xs",
              tab.id === active ? "bg-accent text-white" : "text-accent hover:bg-accent-soft",
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
  onGenerate,
  isStarting,
  hasModel,
}: {
  onGenerate: () => void;
  isStarting: boolean;
  hasModel: boolean;
}) {
  const { data: sizes = [] } = useSizes();
  const lowest = sizes.length ? Math.min(...sizes.map((size) => size.price_cents)) : null;

  return (
    <div className="space-y-6 pb-10 lg:pb-0">
      <div>
        <p className="text-2xl font-semibold lg:text-xl">
          A partir de{" "}
          <span className="rounded-md bg-highlight px-2 py-0.5 text-accent">
            {lowest === null ? "…" : formatBRL(lowest)}
          </span>
        </p>
        <p className="mt-3 text-muted lg:text-sm">
          O modelo 3D será construído a partir desta imagem. Quer mudar algo? Edite a imagem antes
          de gerar.
        </p>
      </div>
      {/* Fixo no rodapé do celular: nunca sai da tela. */}
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-background p-4 lg:static lg:border-0 lg:bg-transparent lg:p-0">
        <Button
          variant="accent"
          size="lg"
          className="h-14 w-full text-base lg:h-12 lg:text-[15px]"
          pending={isStarting}
          onClick={onGenerate}
        >
          <Box />
          {hasModel ? "Ver modelo 3D" : "Ficou ótimo! Gerar em 3D"}
        </Button>
      </div>
    </div>
  );
}

function FailureMessage({
  title,
  creation,
  onRetry,
  isRetrying,
  onBack,
}: {
  title: string;
  creation: Creation;
  onRetry: () => void;
  isRetrying: boolean;
  onBack?: () => void;
}) {
  const refused = creation.error?.code === "content_refused";
  return (
    <div
      className="flex size-full flex-col items-center justify-center gap-4 p-8 text-center"
      role="alert"
    >
      <p className="font-display text-xl font-semibold">{title}</p>
      <p className="text-sm text-muted">
        {creation.error?.message || "Tente de novo em instantes."}
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {refused ? (
          <Button asChild variant="accent">
            <Link href="/">Descrever de outro jeito</Link>
          </Button>
        ) : (
          <Button variant="accent" onClick={onRetry} pending={isRetrying}>
            <RotateCw />
            Tentar de novo
          </Button>
        )}
        {onBack && (
          <Button variant="outline" onClick={onBack}>
            Voltar à imagem
          </Button>
        )}
      </div>
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
