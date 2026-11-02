"use client";

import * as Dialog from "@radix-ui/react-dialog";
import {
  AlertTriangle,
  ChevronLeft,
  CornerDownRight,
  SendHorizontal,
  Sparkles,
} from "lucide-react";
import { type ReactNode, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { useEditImage } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import { cn } from "@/lib/utils";

const MAX_INSTRUCTION = 200;
const SWIPE_THRESHOLD = 20;

export function EditModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Dialog.Root open={open} onOpenChange={(next) => !next && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/70 backdrop-blur-md" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed inset-0 z-50 flex animate-fade-in flex-col bg-black lg:gap-3 lg:bg-transparent lg:p-4 lg:px-24"
        >
          {/* Mounted only while open, so each opening starts on the current image. */}
          <Editor onClose={onClose} />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function Editor({ onClose }: { onClose: () => void }) {
  const versions = useCreatorStore((state) => state.versions);
  const currentImage = useCreatorStore((state) => state.currentImage);
  const modelId = useCreatorStore((state) => state.modelId);
  const applyVersion = useCreatorStore((state) => state.applyVersion);
  const edit = useEditImage();
  const [selectedId, setSelectedId] = useState(currentImage?.id ?? null);
  const [draft, setDraft] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // Phones only: the conversation is a drawer, so the image stays large until it is asked for.
  const [isChatOpen, setIsChatOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const handleStartY = useRef(0);

  const selected = versions.find((v) => v.image.id === selectedId)?.image ?? currentImage;
  const edits = versions.filter((v) => v.instruction !== null);
  const newestFirst = [...versions].reverse();
  const hasChange = selected !== null && selected.id !== currentImage?.id;
  const hasChat = edits.length > 0 || edit.isPending || errorMessage !== null;
  const urlOf = (id: string | null) => versions.find((v) => v.image.id === id)?.image.url;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ block: "end" });
  }, [edits.length, edit.isPending, errorMessage, isChatOpen]);

  function send() {
    const instruction = draft.trim();
    if (!instruction || !selected || edit.isPending) return;
    setDraft("");
    setErrorMessage(null);
    edit.mutate(
      { source: selected, instruction },
      {
        onSuccess: (image) => {
          setSelectedId(image.id);
          if (image.warning) setIsChatOpen(true);
        },
        onError: (error) => {
          setErrorMessage(error.message);
          setDraft(instruction);
          setIsChatOpen(true);
        },
      },
    );
  }

  function cancel() {
    setDraft(edit.variables?.instruction ?? "");
    edit.cancel();
  }

  function done() {
    if (selected && hasChange) applyVersion(selected);
    onClose();
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
        <Button variant="accent" disabled={!hasChange || edit.isPending} onClick={done}>
          Concluir
        </Button>
      </header>

      <div className="mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col lg:grid lg:grid-cols-[3fr_2fr] lg:gap-3">
        <section className="flex min-h-[35dvh] flex-1 flex-col gap-2 pb-2 lg:min-h-0 lg:rounded-2xl lg:bg-surface lg:p-3">
          <div className="relative min-h-0 flex-1">
            {selected && (
              // eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django
              <img
                src={selected.url}
                alt="Versão selecionada"
                className={cn(
                  "size-full object-contain transition-opacity",
                  edit.isPending && "opacity-20",
                )}
              />
            )}
            {edit.isPending && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                <p className="text-sm font-medium text-white lg:text-ink">Editando sua imagem…</p>
                <div className="h-1.5 w-56 overflow-hidden rounded-full bg-white/25 lg:bg-sunken">
                  <div className="h-full w-1/3 animate-indeterminate rounded-full bg-accent" />
                </div>
                <Button variant="outline" size="sm" onClick={cancel}>
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
            {newestFirst.map(({ image }, index) => (
              <button
                key={image.id}
                type="button"
                disabled={edit.isPending}
                aria-label={`Versão ${newestFirst.length - index}`}
                aria-pressed={image.id === selected?.id}
                onClick={() => setSelectedId(image.id)}
                className={cn(
                  "size-12 shrink-0 overflow-hidden rounded-xl border bg-surface transition lg:size-16",
                  image.id === selected?.id
                    ? "border-accent ring-1 ring-accent"
                    : "border-line hover:border-ink/30",
                )}
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
                <img src={image.url} alt="" className="size-full object-cover" />
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
              // Pointers are handled above: `detail` is 0 only for the keyboard.
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
              <div key={version.image.id} className="space-y-3">
                <UserMessage
                  sourceUrl={urlOf(version.sourceId)}
                  instruction={version.instruction ?? ""}
                />
                <div className="flex items-center gap-2 text-sm">
                  <Sparkles className="size-4 text-accent" aria-hidden />
                  Pronto!
                </div>
                {version.image.warning && <Warning>{version.image.warning}</Warning>}
                <button
                  type="button"
                  disabled={edit.isPending}
                  aria-label="Ver esta versão"
                  onClick={() => setSelectedId(version.image.id)}
                  className="block size-28 overflow-hidden rounded-xl border border-line bg-surface transition hover:border-ink/30"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
                  <img src={version.image.url} alt="" className="size-full object-cover" />
                </button>
              </div>
            ))}
            {edit.isPending && edit.variables && (
              <UserMessage
                sourceUrl={edit.variables.source.url}
                instruction={edit.variables.instruction}
              />
            )}
            {errorMessage && <Warning>{errorMessage}</Warning>}
            <div ref={chatEndRef} />
          </div>

          {modelId && hasChange && (
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
              // text-base on phones: iOS zooms the page when focusing a smaller field.
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
                disabled={!draft.trim() || edit.isPending}
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
          {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
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
