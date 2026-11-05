"use client";

import { Button } from "@kubo/ui/button";
import { Card } from "@kubo/ui/card";
import { cn } from "@kubo/ui/lib/utils";
import { Popover, PopoverContent, PopoverTrigger } from "@kubo/ui/popover";
import { ChevronDown, ImageUp, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { useStyles } from "@/features/catalog/hooks";
import { useStartCreation } from "@/features/creations/hooks";
import { messageOf } from "@/lib/errors";

const MAX_PHOTO_BYTES = 10 * 1024 * 1024;
const FALLBACK_STYLES = [{ id: "free", label: "Livre", thumbnail: "/styles/free.webp" }];
const HINTS: Record<string, string> = {
  free: "Figura detalhada, fiel ao que você pedir.",
  pixar: "Personagem de animação 3D, com olhos grandes e expressivos.",
  "mini-pop": "Boneco de vinil de cabeça enorme. Objetos viram bonecos.",
  chibi: "Personagem de anime de cabeça grande. Animais e objetos viram personagens.",
};

type Style = { id: string; label: string; thumbnail: string };

export function PromptStep() {
  const router = useRouter();
  const start = useStartCreation();
  const { data: styles = FALLBACK_STYLES } = useStyles();
  const [prompt, setPrompt] = useState("");
  const [styleId, setStyleId] = useState("free");
  const [photo, setPhoto] = useState<File | null>(null);
  const [rightsAccepted, setRightsAccepted] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const trimmed = prompt.trim();
  const canSubmit = (Boolean(trimmed) || Boolean(photo)) && (!photo || rightsAccepted);

  function submit() {
    if (!canSubmit || start.isPending) return;
    start.mutate(
      { text: trimmed, style: styleId, photo, rightsAccepted },
      {
        onSuccess: (creation) => router.push(`/criacoes/${creation.id}`),
        onError: (error) => toast.error(messageOf(error)),
      },
    );
  }

  function attachPhoto(file: File | undefined) {
    if (!file) return;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
      toast.error("Envie uma foto em PNG, JPG ou WEBP.");
      return;
    }
    if (file.size > MAX_PHOTO_BYTES) {
      toast.error("A foto deve ter no máximo 10 MB.");
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
            <StyleSelect styles={styles} value={styleId} onChange={setStyleId} />
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
            aria-label="O que você quer criar?"
            placeholder={
              photo
                ? "Opcional: peça uma mudança, como “com um chapéu de mago”"
                : "Ex.: um gato astronauta sentado na lua"
            }
            className="w-full resize-none rounded-xl bg-transparent p-4 text-lg outline-none placeholder:text-muted/70"
          />
          {photo && (
            <label className="mx-2 mt-1 flex items-start gap-2 rounded-xl bg-sunken p-3 text-[13px] leading-snug">
              <input
                type="checkbox"
                checked={rightsAccepted}
                onChange={(event) => setRightsAccepted(event.target.checked)}
                className="mt-0.5 size-4 accent-[rgb(var(--accent))]"
              />
              <span>
                Tenho direitos sobre esta foto e o consentimento de quem aparece nela. Veja os{" "}
                <Link href="/termos" className="underline" target="_blank">
                  Termos de Uso
                </Link>
                .
              </span>
            </label>
          )}
          <div className="mt-4 flex items-center justify-between gap-2 px-2 pb-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              aria-label="Enviar foto"
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
            <Button type="submit" variant="accent" disabled={!canSubmit} pending={start.isPending}>
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

function StyleSelect({
  styles,
  value,
  onChange,
}: {
  styles: Style[];
  value: string;
  onChange: (id: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const selected = styles.find((option) => option.id === value) ?? styles[0];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        aria-label={`Estilo ${selected.label}`}
        className="flex items-center gap-2 rounded-xl border border-line py-1.5 pl-1.5 pr-3 text-sm font-medium transition-colors hover:border-ink/30"
      >
        <StyleSample src={selected.thumbnail} className="size-7" />
        Estilo {selected.label}
        <ChevronDown className="size-4 text-muted" />
      </PopoverTrigger>
      <PopoverContent className="w-80 p-1.5">
        <div role="listbox" aria-label="Estilo">
          {styles.map((option) => (
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
              <StyleSample src={option.thumbnail} className="size-16" />
              <span>
                <span className="block text-sm font-medium">Estilo {option.label}</span>
                <span className="block text-[13px] text-muted">{HINTS[option.id]}</span>
              </span>
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

function StyleSample({ src, className }: { src: string; className: string }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- miniatura estática pequena
    <img
      src={src}
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
        // eslint-disable-next-line @next/next/no-img-element -- prévia local do arquivo do cliente
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
