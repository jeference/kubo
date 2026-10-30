"use client";

import { useIsMutating } from "@tanstack/react-query";
import { Box, Check, RefreshCw } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { GENERATE_IMAGES_KEY, useCreateModel, useGenerateImages } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import type { StoredImage } from "@/features/creator/types";
import { cn } from "@/lib/utils";

export function ImagePickerStep() {
  const rounds = useCreatorStore((state) => state.rounds);
  const prompt = useCreatorStore((state) => state.prompt);
  const setPrompt = useCreatorStore((state) => state.setPrompt);
  const generate = useGenerateImages();
  const createModel = useCreateModel();
  const isGenerating = useIsMutating({ mutationKey: GENERATE_IMAGES_KEY }) > 0;
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState(prompt);

  const latest = rounds.at(-1);
  const previous = rounds.slice(0, -1).reverse();
  const allImages = rounds.flatMap((round) => round.images);
  const selected = allImages.find((image) => image.id === selectedId) ?? null;

  function regenerate() {
    const text = draft.trim();
    if (!text) return;
    setPrompt(text);
    generate.mutate(text);
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
      <section>
        <h2 className="font-display text-2xl font-semibold tracking-tight">Escolha uma imagem</h2>
        <p className="mt-1 text-muted">
          O modelo 3D vai ser construído a partir dela. Nenhuma ficou boa? Ajuste a descrição.
        </p>

        <div className="mt-6 grid grid-cols-2 gap-4">
          {isGenerating
            ? Array.from({ length: 4 }, (_, i) => (
                <div key={i} className="skeleton aspect-square rounded-2xl" />
              ))
            : latest?.images.map((image) => (
                <ImageOption
                  key={image.id}
                  image={image}
                  selected={image.id === selectedId}
                  onSelect={() => setSelectedId(image.id)}
                  onConfirm={() => createModel.mutate(image)}
                />
              ))}
        </div>

        {previous.length > 0 && (
          <details className="group mt-8">
            <summary className="cursor-pointer text-sm font-medium text-muted hover:text-ink">
              Rodadas anteriores ({previous.length})
            </summary>
            <div className="mt-4 space-y-5">
              {previous.map((round, index) => (
                <div key={index}>
                  <p className="mb-2 text-sm text-muted">“{round.prompt}”</p>
                  <div className="grid grid-cols-4 gap-3">
                    {round.images.map((image) => (
                      <ImageOption
                        key={image.id}
                        image={image}
                        selected={image.id === selectedId}
                        onSelect={() => setSelectedId(image.id)}
                        onConfirm={() => createModel.mutate(image)}
                        compact
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}
      </section>

      <aside className="lg:sticky lg:top-6 lg:self-start">
        <Card className="space-y-4 p-5">
          <label className="block">
            <span className="text-sm font-medium">Descrição</span>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={4}
              maxLength={1000}
              className="mt-2 w-full resize-none rounded-xl border border-line bg-background p-3 text-sm outline-none focus:border-ink/40"
            />
          </label>
          <Button
            variant="outline"
            className="w-full"
            onClick={regenerate}
            pending={isGenerating}
            disabled={!draft.trim()}
          >
            <RefreshCw />
            {draft.trim() === latest?.prompt ? "Gerar outras opções" : "Gerar com o ajuste"}
          </Button>

          <div className="border-t border-line pt-4">
            <Button
              variant="accent"
              size="lg"
              className="w-full"
              disabled={!selected}
              pending={createModel.isPending}
              onClick={() => selected && createModel.mutate(selected)}
            >
              <Box />
              Gerar modelo 3D
            </Button>
            <p className="mt-2 text-center text-xs text-muted">
              {selected
                ? "O modelo 3D será criado a partir desta imagem."
                : "Clique numa imagem para selecionar."}
            </p>
          </div>
        </Card>
      </aside>
    </div>
  );
}

function ImageOption({
  image,
  selected,
  onSelect,
  onConfirm,
  compact = false,
}: {
  image: StoredImage;
  selected: boolean;
  onSelect: () => void;
  onConfirm: () => void;
  compact?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      onDoubleClick={onConfirm}
      aria-pressed={selected}
      className={cn(
        "group relative aspect-square overflow-hidden rounded-2xl border bg-surface transition",
        compact && "rounded-xl",
        selected
          ? "border-accent ring-2 ring-accent ring-offset-2 ring-offset-background"
          : "border-line hover:border-ink/30",
      )}
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- dynamic media served by Django */}
      <img
        src={image.url}
        alt=""
        className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
      />
      {selected && (
        <span className="absolute right-3 top-3 flex size-7 items-center justify-center rounded-full bg-accent text-white shadow">
          <Check className="size-4" strokeWidth={3} />
        </span>
      )}
    </button>
  );
}
