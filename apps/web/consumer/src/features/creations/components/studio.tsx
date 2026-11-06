"use client";

import { Button } from "@kubo/ui/button";
import { Card } from "@kubo/ui/card";
import { EmptyState } from "@kubo/ui/empty-state";
import { Skeleton } from "@kubo/ui/skeleton";
import { ArrowLeft, Pencil, RotateCw, Sparkles } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { EditModal } from "@/features/creations/components/edit-modal";
import {
  IMAGE_PROGRESS,
  ProgressFrame,
  ProgressNotice,
  useElapsedSince,
} from "@/features/creations/components/progress";
import { PurchasePanel } from "@/features/creations/components/purchase-panel";
import { useCreation, useCreationAction } from "@/features/creations/hooks";
import type { Creation } from "@/features/creations/types";
import { messageOf } from "@/lib/errors";

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
  const isReady = status === "ready";
  const image = creation.versions.find((v) => v.id === creation.current_version_id) ?? null;
  const elapsed = useElapsedSince(creation.active_started_at);

  const [isEditing, setIsEditing] = useState(false);

  function run(mutate: () => Promise<unknown>) {
    mutate().catch((error) => toast.error(messageOf(error)));
  }

  return (
    <div>
      {/* A primeira coluna é exatamente a imagem: a distância até o painel é sempre a mesma. */}
      <div className="grid gap-y-6 lg:grid-cols-[min(900px,42vw,max(400px,calc(100dvh-10rem)))_minmax(0,675px)] lg:justify-center lg:gap-x-[min(4vw,72px)]">
        {!isGeneratingImage && (
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

        <section className="relative mx-auto w-full min-w-0 max-w-[560px] lg:max-w-none">
          <Card className="relative aspect-square w-full overflow-hidden">
            {isReady && image && (
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
            {isReady && image && (
              // eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica, URL assinada
              <img
                src={image.image_url}
                alt="Imagem 2D do objeto"
                className="size-full object-contain"
              />
            )}
          </Card>
        </section>

        {/* O painel começa abaixo do topo da imagem. */}
        <aside className="lg:pt-[60px]">
          {isGeneratingImage && <ProgressNotice progress={IMAGE_PROGRESS} elapsed={elapsed} />}
          {isReady && <PurchasePanel creation={creation} />}
        </aside>
      </div>

      <EditModal creation={creation} open={isEditing} onClose={() => setIsEditing(false)} />
    </div>
  );
}

function FailureMessage({
  title,
  creation,
  onRetry,
  isRetrying,
}: {
  title: string;
  creation: Creation;
  onRetry: () => void;
  isRetrying: boolean;
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
      </div>
    </div>
  );
}
