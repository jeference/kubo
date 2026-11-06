"use client";

import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import { formatDate } from "@kubo/ui/lib/format";
import { CREATION_STATUS } from "@kubo/ui/lib/status";
import { Skeleton } from "@kubo/ui/skeleton";
import { StatusBadge } from "@kubo/ui/status-badge";
import { useSession } from "@kubo/web-core/session";
import { ImageIcon, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import { useCreations, useDeleteCreation } from "@/features/creations/hooks";
import { messageOf } from "@/lib/errors";

export function CreationList() {
  const { data, isLoading } = useCreations();
  const remove = useDeleteCreation();
  const status = useSession((state) => state.status);

  function confirmDelete(id: string) {
    if (!window.confirm("Excluir esta criação? Pedidos já feitos não são afetados.")) return;
    remove.mutate(id, {
      onSuccess: () => toast.success("Criação excluída."),
      onError: (error) => toast.error(messageOf(error)),
    });
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex items-center justify-between gap-3">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Minhas criações</h1>
        <Button asChild variant="primary">
          <Link href="/">
            <Plus />
            Nova
          </Link>
        </Button>
      </div>

      {status === "anonymous" && (
        <p className="mt-3 text-sm text-muted">
          Estas criações ficam neste navegador.{" "}
          <Link href="/cadastro" className="text-accent underline">
            Crie uma conta
          </Link>{" "}
          para vê-las em outros dispositivos.
        </p>
      )}

      {isLoading && (
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <Skeleton key={index} className="aspect-square w-full" />
          ))}
        </div>
      )}

      {data && data.results.length === 0 && (
        <div className="mt-8">
          <EmptyState
            title="Nenhuma criação ainda"
            description="Descreva uma ideia ou envie uma foto para começar."
            action={
              <Button asChild variant="primary">
                <Link href="/">Criar agora</Link>
              </Button>
            }
          />
        </div>
      )}

      {data && data.results.length > 0 && (
        <ul className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {data.results.map((creation) => {
            const badge = CREATION_STATUS[creation.status];
            return (
              <li
                key={creation.id}
                className="group relative overflow-hidden rounded-2xl border border-line bg-surface shadow-card transition-colors hover:border-accent"
              >
                <Link href={`/criacoes/${creation.id}`} className="block">
                  <div className="flex aspect-square items-center justify-center bg-sunken">
                    {creation.thumbnail_url ? (
                      // eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica
                      <img
                        src={creation.thumbnail_url}
                        alt=""
                        className="size-full object-contain"
                      />
                    ) : (
                      <ImageIcon className="size-8 text-muted" aria-hidden />
                    )}
                  </div>
                  <div className="space-y-1.5 p-3">
                    <StatusBadge label={badge.label} tone={badge.tone} />
                    <p className="truncate text-sm">{creation.text || "A partir de uma foto"}</p>
                    <p className="text-xs text-muted">{formatDate(creation.created_at)}</p>
                  </div>
                </Link>
                <Button
                  variant="floating"
                  size="icon-sm"
                  aria-label="Excluir criação"
                  onClick={() => confirmDelete(creation.id)}
                  className="absolute right-2 top-2 text-muted hover:text-danger"
                >
                  <Trash2 aria-hidden />
                </Button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
