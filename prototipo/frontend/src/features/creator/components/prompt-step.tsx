"use client";

import { ChevronDown, ImageUp, Sparkles, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useGenerateImages, useUploadImage } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import type { Style } from "@/features/creator/types";
import { cn } from "@/lib/utils";

const STYLES: { id: Style; label: string; hint: string }[] = [
  { id: "free", label: "Estilo Livre", hint: "Figura detalhada, fiel ao que você pedir." },
  {
    id: "pixar",
    label: "Estilo Pixar",
    hint: "Personagem de animação 3D, com olhos grandes e expressivos.",
  },
  {
    id: "mini-pop",
    label: "Estilo Mini Pop",
    hint: "Boneco de vinil de cabeça enorme. Objetos viram bonecos.",
  },
  {
    id: "chibi",
    label: "Estilo Chibi",
    hint: "Personagem de anime de cabeça grande. Animais e objetos viram personagens.",
  },
];

export function PromptStep() {
  const prompt = useCreatorStore((state) => state.prompt);
  const setPrompt = useCreatorStore((state) => state.setPrompt);
  const style = useCreatorStore((state) => state.style);
  const setStyle = useCreatorStore((state) => state.setStyle);
  const photo = useCreatorStore((state) => state.photo);
  const setPhoto = useCreatorStore((state) => state.setPhoto);
  const setView = useCreatorStore((state) => state.setView);
  const generate = useGenerateImages();
  const upload = useUploadImage();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const trimmed = prompt.trim();

  function submit() {
    if (photo) {
      upload.mutate({ file: photo, prompt: trimmed, style });
    } else if (trimmed) {
      generate.mutate({ prompt: trimmed, style });
    } else {
      return;
    }
    setView("studio");
  }

  function attachPhoto(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Envie um arquivo de imagem (JPG, PNG, WEBP).");
      return;
    }
    setPhoto(file);
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-center font-display text-4xl font-semibold tracking-tight">
        O que você quer criar?
      </h1>

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
          attachPhoto(event.dataTransfer.files[0]);
        }}
      >
        <form
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <div className="px-2 pt-2">
            <StyleSelect value={style} onChange={setStyle} />
          </div>
          {photo && <AttachedPhoto file={photo} onRemove={() => setPhoto(null)} />}
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) submit();
            }}
            rows={photo ? 2 : 4}
            maxLength={1000}
            autoFocus
            placeholder={
              photo
                ? "Opcional: peça uma mudança, como “com um chapéu de mago”"
                : "Ex.: um gato astronauta sentado na lua"
            }
            className="w-full resize-none rounded-xl bg-transparent p-4 text-lg outline-none placeholder:text-muted/70"
          />
          <div className="mt-4 flex items-center justify-between gap-2 px-2 pb-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={(event) => {
                attachPhoto(event.target.files?.[0]);
                event.target.value = "";
              }}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              title="Criamos a imagem do objeto a partir da sua foto"
            >
              <ImageUp />
              {photo ? "Trocar foto" : "Enviar foto"}
            </Button>
            <Button type="submit" variant="accent" disabled={!trimmed && !photo}>
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

function StyleSelect({ value, onChange }: { value: Style; onChange: (style: Style) => void }) {
  const [open, setOpen] = useState(false);
  const selected = STYLES.find((option) => option.id === value) ?? STYLES[0];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        aria-label={selected.label}
        className="flex items-center gap-2 rounded-xl border border-line py-1.5 pl-1.5 pr-3 text-sm font-medium transition-colors hover:border-ink/30"
      >
        <StyleSample id={selected.id} className="size-7" />
        {selected.label}
        <ChevronDown className="size-4 text-muted" />
      </PopoverTrigger>
      <PopoverContent className="w-80 p-1.5">
        <div role="listbox" aria-label="Estilo">
          {STYLES.map((option) => (
            <button
              key={option.id}
              type="button"
              role="option"
              aria-selected={option.id === value}
              onClick={() => {
                onChange(option.id);
                setOpen(false);
              }}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg p-1.5 text-left transition-colors",
                option.id === value ? "bg-accent-soft" : "hover:bg-ink/5",
              )}
            >
              <StyleSample id={option.id} className="size-16" />
              <span>
                <span className="block text-sm font-medium">{option.label}</span>
                <span className="block text-[13px] text-muted">{option.hint}</span>
              </span>
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

function StyleSample({ id, className }: { id: Style; className: string }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- small static sample
    <img
      src={`/styles/${id}.webp`}
      alt=""
      className={cn("shrink-0 rounded-md border border-line object-cover", className)}
    />
  );
}

function AttachedPhoto({ file, onRemove }: { file: File; onRemove: () => void }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    const objectUrl = URL.createObjectURL(file);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  return (
    <div className="relative ml-4 mt-4 size-24">
      {url && (
        // eslint-disable-next-line @next/next/no-img-element -- local preview of the user's file
        <img
          src={url}
          alt="Foto enviada"
          className="size-full rounded-xl border border-line object-cover"
        />
      )}
      <button
        type="button"
        onClick={onRemove}
        aria-label="Remover foto"
        className="absolute -right-2 -top-2 flex size-6 items-center justify-center rounded-full border border-line bg-surface text-muted transition-colors hover:text-ink"
      >
        <X className="size-3.5" />
      </button>
    </div>
  );
}
