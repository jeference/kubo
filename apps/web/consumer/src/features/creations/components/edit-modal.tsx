"use client";

import { Button } from "@kubo/ui/button";
import { cn } from "@kubo/ui/lib/utils";
import * as Dialog from "@radix-ui/react-dialog";
import {
  AlertTriangle,
  ChevronLeft,
  CornerDownRight,
  SendHorizontal,
  Sparkles,
} from "lucide-react";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { useCreationAction } from "@/features/creations/hooks";
import type { Creation, EditTask } from "@/features/creations/types";
import { messageOf } from "@/lib/errors";

const MAX_INSTRUCTION = 200;
const SWIPE_THRESHOLD = 20;
const BACKGROUND_LOST =
  "O fundo saiu do branco, o que pode piorar o modelo 3D. Escolha outra versão ou peça para voltar ao fundo branco.";
const REFUSED =
  "Essa edição esbarrou nas regras de conteúdo. Personagens e marcas conhecidos, nudez e violência costumam ser recusados. Tente descrever de outro jeito.";
const FAILED = "Não conseguimos editar agora. Tente de novo.";

export function EditModal({
  creation,
  open,
  onClose,
}: {
  creation: Creation;
  open: boolean;
  onClose: () => void;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={(next) => !next && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/70 backdrop-blur-md" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed inset-0 z-50 flex animate-fade-in flex-col bg-black lg:gap-3 lg:bg-transparent lg:p-4 lg:px-24"
        >
          {/* Montado só enquanto aberto: cada abertura começa na imagem atual. */}
          <Editor creation={creation} onClose={onClose} />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function Editor({ creation, onClose }: { creation: Creation; onClose: () => void }) {
  const actions = useCreationAction(creation.id);
  const versions = creation.versions;
  const [selectedId, setSelectedId] = useState(creation.current_version_id);
  const [draft, setDraft] = useState("");
  // No celular, a conversa é uma gaveta: a imagem fica grande até o cliente pedir.
  const [isChatOpen, setIsChatOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const handleStartY = useRef(0);
  const knownVersions = useRef(versions.length);

  const selected = versions.find((version) => version.id === selectedId) ?? versions.at(-1) ?? null;
  const edits = versions.filter((version) => version.origin === "edit");
  const newestFirst = [...versions].reverse();
  const activeTask = creation.edit_tasks.find((task) => task.is_active) ?? null;
  const lastTask: EditTask | undefined = creation.edit_tasks[0];
  const taskFailed = lastTask?.status === "failed";
  const isBusy = Boolean(activeTask) || actions.edit.isPending;
  const hasChange = selected !== null && selected.id !== creation.current_version_id;
  const hasChat = edits.length > 0 || isBusy || taskFailed;
  const urlOf = (id: string | null | undefined) =>
    versions.find((version) => version.id === id)?.image_url;

  // Versão nova chegou pelo polling: passa a mostrá-la.
  useEffect(() => {
    if (versions.length > knownVersions.current) {
      const newest = versions.at(-1);
      if (newest) setSelectedId(newest.id);
      if (newest?.background_lost) setIsChatOpen(true);
    }
    knownVersions.current = versions.length;
  }, [versions]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ block: "end" });
  }, [edits.length, isBusy, taskFailed, isChatOpen]);

  function send() {
    const instruction = draft.trim();
    if (!instruction || !selected || isBusy) return;
    setDraft("");
    actions.edit.mutate(
      { version_id: selected.id, instruction },
      {
        onError: (error) => {
          toast.error(messageOf(error));
          setDraft(instruction);
        },
      },
    );
  }

  function cancel() {
    if (!activeTask) return;
    setDraft(activeTask.instruction);
    actions.cancelEdit.mutate(activeTask.id, {
      onError: (error) => toast.error(messageOf(error)),
    });
  }

  function done() {
    if (!selected || !hasChange) return;
    actions.applyVersion.mutate(selected.id, {
      onSuccess: onClose,
      onError: (error) => toast.error(messageOf(error)),
    });
  }

  return (
    <>
      <header className="mx-auto flex w-full max-w-6xl shrink-0 items-center justify-between px-4 py-3 lg:p-0">
        <div className="flex items-center gap-3 text-white">
          <Dialog.Close
            aria-label="Voltar"
            className="flex size-9 items-center justify-center rounded-full bg-white/20 transition-colors hover:bg-white/30"
          >
            <ChevronLeft className="size-5" />
          </Dialog.Close>
          <Dialog.Title className="font-display text-lg font-semibold">Editar imagem</Dialog.Title>
        </div>
        <Button
          variant="accent"
          disabled={!hasChange || isBusy}
          pending={actions.applyVersion.isPending}
          onClick={done}
        >
          Concluir
        </Button>
      </header>

      <div className="mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col lg:grid lg:grid-cols-[3fr_2fr] lg:gap-3">
        <section className="flex min-h-[35dvh] flex-1 flex-col gap-2 pb-2 lg:min-h-0 lg:rounded-2xl lg:bg-surface lg:p-3">
          <div className="relative min-h-0 flex-1">
            {selected && (
              // eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica, URL assinada
              <img
                src={selected.image_url}
                alt="Versão selecionada"
                className={cn(
                  "size-full object-contain transition-opacity",
                  isBusy && "opacity-20",
                )}
              />
            )}
            {isBusy && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                <p className="text-sm font-medium text-white lg:text-ink">Editando sua imagem…</p>
                <div className="h-1.5 w-56 overflow-hidden rounded-full bg-white/25 lg:bg-sunken">
                  <div className="h-full w-1/3 animate-indeterminate rounded-full bg-accent" />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!activeTask}
                  pending={actions.cancelEdit.isPending}
                  onClick={cancel}
                >
                  Cancelar
                </Button>
              </div>
            )}
          </div>
          <div
            className={cn(
              "flex shrink-0 gap-2 overflow-x-auto px-3 py-0.5 lg:p-0.5",
              versions.length < 2 && "hidden lg:flex",
            )}
          >
            {newestFirst.map((version) => (
              <button
                key={version.id}
                type="button"
                disabled={isBusy}
                aria-label={`Versão ${version.number}`}
                aria-pressed={version.id === selected?.id}
                onClick={() => setSelectedId(version.id)}
                className={cn(
                  "size-12 shrink-0 overflow-hidden rounded-xl border bg-surface transition lg:size-16",
                  version.id === selected?.id
                    ? "border-accent ring-1 ring-accent"
                    : "border-line hover:border-ink/30",
                )}
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                <img src={version.image_url} alt="" className="size-full object-cover" />
              </button>
            ))}
          </div>
        </section>

        <section className="flex min-h-0 flex-col gap-3 rounded-t-2xl bg-background p-4 lg:rounded-2xl">
          {hasChat && (
            <button
              type="button"
              aria-label={isChatOpen ? "Ocultar conversa" : "Mostrar conversa"}
              aria-expanded={isChatOpen}
              onPointerDown={(event) => {
                handleStartY.current = event.clientY;
              }}
              onPointerUp={(event) => {
                const moved = event.clientY - handleStartY.current;
                setIsChatOpen(Math.abs(moved) > SWIPE_THRESHOLD ? moved < 0 : !isChatOpen);
              }}
              // Ponteiros são tratados acima: `detail` é 0 só no teclado.
              onClick={(event) => event.detail === 0 && setIsChatOpen(!isChatOpen)}
              className="-mt-3 flex h-6 shrink-0 touch-none items-center justify-center lg:hidden"
            >
              <span className="h-1 w-9 rounded-full bg-ink/25" />
            </button>
          )}

          <div
            className={cn(
              "min-h-0 space-y-4 overflow-y-auto pr-1 lg:max-h-none lg:flex-1",
              isChatOpen ? "max-h-[38dvh]" : "hidden lg:block",
            )}
          >
            {edits.map((version) => (
              <div key={version.id} className="space-y-3">
                <UserMessage sourceUrl={urlOf(version.parent_id)} instruction={version.instruction} />
                <div className="flex items-center gap-2 text-sm">
                  <Sparkles className="size-4 text-accent" aria-hidden />
                  Pronto!
                </div>
                {version.background_lost && <Warning>{BACKGROUND_LOST}</Warning>}
                <button
                  type="button"
                  disabled={isBusy}
                  aria-label="Ver esta versão"
                  onClick={() => setSelectedId(version.id)}
                  className="block size-28 overflow-hidden rounded-xl border border-line bg-surface transition hover:border-ink/30"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                  <img src={version.image_url} alt="" className="size-full object-cover" />
                </button>
              </div>
            ))}
            {activeTask && (
              <UserMessage
                sourceUrl={urlOf(activeTask.source_version_id)}
                instruction={activeTask.instruction}
              />
            )}
            {taskFailed && !activeTask && (
              <Warning>{lastTask?.is_refused ? REFUSED : FAILED}</Warning>
            )}
            <div ref={chatEndRef} />
          </div>

          {creation.model && hasChange && (
            <p className="text-xs text-muted">
              Ao concluir, o modelo 3D atual será descartado e você poderá gerar outro.
            </p>
          )}
          <div className="flex shrink-0 items-end gap-2 rounded-xl bg-surface p-3 lg:block">
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  send();
                }
              }}
              rows={1}
              maxLength={MAX_INSTRUCTION}
              aria-label="Descreva sua ideia"
              placeholder="Descreva sua ideia…"
              // text-base no celular: o iOS dá zoom ao focar campos menores.
              className="max-h-24 min-w-0 flex-1 resize-none bg-transparent py-1 text-base outline-none [field-sizing:content] placeholder:text-muted/70 lg:min-h-10 lg:w-full lg:py-0 lg:text-sm"
            />
            <div className="flex shrink-0 items-center justify-end gap-2 lg:mt-1">
              <span className="rounded-full bg-sunken px-2 py-0.5 text-xs tabular-nums text-muted">
                {draft.length}/{MAX_INSTRUCTION}
              </span>
              <Button
                variant="accent"
                size="sm"
                aria-label="Enviar"
                disabled={!draft.trim() || isBusy}
                onClick={send}
              >
                <SendHorizontal />
              </Button>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}

function UserMessage({
  sourceUrl,
  instruction,
}: {
  sourceUrl: string | undefined;
  instruction: string;
}) {
  return (
    <div className="flex flex-col items-end gap-2">
      {sourceUrl && (
        <div className="flex items-center gap-2 text-muted">
          <CornerDownRight className="size-3.5" aria-hidden />
          {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
          <img
            src={sourceUrl}
            alt=""
            className="size-14 rounded-lg border border-line bg-surface object-cover"
          />
        </div>
      )}
      <p className="max-w-[85%] break-words rounded-xl bg-accent-soft px-3 py-2 text-sm">
        {instruction}
      </p>
    </div>
  );
}

function Warning({ children }: { children: ReactNode }) {
  return (
    <p className="flex items-start gap-2 text-sm text-danger" role="alert">
      <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden />
      {children}
    </p>
  );
}
