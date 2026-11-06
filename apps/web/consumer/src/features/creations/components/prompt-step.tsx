"use client";

import { Button } from "@kubo/ui/button";
import { Checkbox } from "@kubo/ui/checkbox";
import { Textarea } from "@kubo/ui/input";
import { cn } from "@kubo/ui/lib/utils";
import { Popover, PopoverContent, PopoverTrigger } from "@kubo/ui/popover";
import { ChevronDown, ImagePlus, Sparkles, X } from "lucide-react";
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
  const canSubmit = photo !== null && rightsAccepted;

  function submit() {
    if (!photo || !canSubmit || start.isPending) return;
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
      <h1 className="text-center font-display text-3xl font-semibold tracking-tight sm:text-4xl">
        O que você quer criar?
      </h1>

      <form
        className="mt-4 space-y-3 sm:mt-6"
        onSubmit={(event) => {
          event.preventDefault();
          submit();
        }}
      >
        <StyleSelect styles={styles} value={styleId} onChange={setStyleId} />

        <div
          className={cn(
            "relative rounded-3xl bg-sunken bg-[radial-gradient(rgb(var(--ink)/0.16)_1px,transparent_1px)] p-3 transition-colors [background-size:18px_18px]",
            isDragging && "bg-accent-soft ring-2 ring-accent",
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
          <div className="flex justify-center py-2 sm:py-5">
            <PhotoPicker
              file={photo}
              onPick={() => fileInputRef.current?.click()}
              onRemove={() => setPhoto(null)}
            />
          </div>
          <Textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) submit();
            }}
            rows={2}
            maxLength={1000}
            autoFocus
            aria-label="O que você quer criar?"
            placeholder="Opcional: peça uma mudança, como “com um chapéu de mago”"
            className="p-4 lg:text-base"
          />

          {isDragging && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <span className="rounded-full bg-surface px-4 py-2 text-sm font-medium shadow-card">
                Solte a foto aqui
              </span>
            </div>
          )}
        </div>

        {photo && (
          <Checkbox
            className="rounded-2xl bg-sunken p-3"
            checked={rightsAccepted}
            onChange={(event) => setRightsAccepted(event.target.checked)}
          >
            Tenho direitos sobre esta foto e o consentimento de quem aparece nela. Veja os{" "}
            <Link href="/termos" className="underline" target="_blank">
              Termos de Uso
            </Link>
            .
          </Checkbox>
        )}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={!canSubmit}
          pending={start.isPending}
          className="h-12 w-full text-base sm:h-14"
        >
          <Sparkles />
          Gerar
        </Button>
      </form>
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
      <PopoverTrigger asChild>
        <Button aria-label={`Estilo ${selected.label}`} className="pl-1.5 pr-4">
          <StyleSample src={selected.thumbnail} className="size-8 rounded-full" />
          Estilo {selected.label}
          <ChevronDown className="text-muted" aria-hidden />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-2">
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
                "flex w-full items-center gap-3 rounded-xl p-1.5 text-left transition-colors",
                option.id === value
                  ? "bg-accent-soft ring-2 ring-inset ring-accent"
                  : "hover:bg-sunken",
              )}
            >
              <StyleSample src={option.thumbnail} className="size-16 rounded-lg" />
              <span>
                <span className="block text-sm font-semibold">Estilo {option.label}</span>
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
    <img src={src} alt="" className={cn("shrink-0 border border-line object-cover", className)} />
  );
}

function PhotoPicker({
  file,
  onPick,
  onRemove,
}: {
  file: File | null;
  onPick: () => void;
  onRemove: () => void;
}) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!file) {
      setUrl(null);
      return;
    }
    const objectUrl = URL.createObjectURL(file);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  return (
    // A altura da tela define o tamanho, para o formulário inteiro caber sem rolar até o Gerar.
    <div className="relative size-[clamp(5.5rem,calc(100svh-30rem),13rem)] sm:size-[clamp(5.5rem,calc(100svh-31.5rem),13rem)]">
      <button
        type="button"
        onClick={onPick}
        aria-label={file ? "Trocar foto" : "Enviar foto"}
        title="Criamos a imagem do objeto a partir da sua foto"
        className="flex size-full flex-col items-center justify-center gap-3 overflow-hidden rounded-3xl border border-line bg-surface text-sm font-medium transition-colors hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        {url ? (
          // eslint-disable-next-line @next/next/no-img-element -- prévia local do arquivo do cliente
          <img src={url} alt="Foto enviada" className="size-full object-cover" />
        ) : (
          <>
            <ImagePlus className="size-7" aria-hidden />
            Envie sua foto
          </>
        )}
      </button>
      {file && (
        <Button
          variant="floating"
          size="icon-sm"
          onClick={onRemove}
          aria-label="Remover foto"
          className="absolute -right-2 -top-2"
        >
          <X aria-hidden />
        </Button>
      )}
    </div>
  );
}
