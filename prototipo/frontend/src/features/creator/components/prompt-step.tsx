"use client";

import { ImageUp, Sparkles } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useGenerateImages, useUploadImage } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "Um dragão bebê dormindo enrolado",
  "Uma coruja de óculos lendo um livro",
  "Um astronauta acenando",
  "Um cacto sorridente num vasinho",
];

export function PromptStep() {
  const prompt = useCreatorStore((state) => state.prompt);
  const setPrompt = useCreatorStore((state) => state.setPrompt);
  const setView = useCreatorStore((state) => state.setView);
  const generate = useGenerateImages();
  const upload = useUploadImage();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const trimmed = prompt.trim();
  const isSendingPhoto = upload.isPending;

  function submit() {
    if (!trimmed) return;
    generate.mutate(trimmed);
    setView("studio");
  }

  /** A photo skips the image generation and becomes the image of the studio. */
  function sendPhoto(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Envie um arquivo de imagem (JPG, PNG, WEBP).");
      return;
    }
    upload.mutate(file);
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-center font-display text-4xl font-semibold tracking-tight">
        O que você quer criar?
      </h1>
      <p className="mt-3 text-center text-muted">
        Descreva o objeto ou envie uma foto. Antes do 3D, você confere a imagem e pode editá-la.
      </p>

      <Card
        className={cn(
          "relative mt-8 p-2 transition-colors",
          isDragging && "border-accent bg-accent-soft [&_form]:opacity-30",
        )}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
            setIsDragging(false);
          }
        }}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          sendPhoto(event.dataTransfer.files[0]);
        }}
      >
        <form
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) submit();
            }}
            rows={4}
            maxLength={1000}
            autoFocus
            placeholder="Ex.: um gato astronauta sentado na lua, estilo boneco colecionável"
            className="w-full resize-none rounded-xl bg-transparent p-4 text-lg outline-none placeholder:text-muted/70"
          />
          <div className="flex flex-wrap gap-2 px-2">
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setPrompt(example)}
                className="rounded-full border border-line px-3 py-1 text-[13px] text-muted transition-colors hover:border-ink/30 hover:text-ink"
              >
                {example}
              </button>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between gap-2 px-2 pb-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={(event) => {
                sendPhoto(event.target.files?.[0]);
                event.target.value = "";
              }}
            />
            <Button
              type="button"
              variant="outline"
              pending={isSendingPhoto}
              onClick={() => fileInputRef.current?.click()}
              title="Usa a sua foto como imagem do objeto"
            >
              <ImageUp />
              Enviar foto
            </Button>
            <Button type="submit" variant="accent" disabled={!trimmed || isSendingPhoto}>
              <Sparkles />
              Gerar imagem
            </Button>
          </div>
        </form>

        {isDragging && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center rounded-2xl">
            <span className="rounded-full bg-surface px-4 py-2 text-sm font-medium shadow-card">
              Solte a foto aqui
            </span>
          </div>
        )}
      </Card>
    </div>
  );
}
