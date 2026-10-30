"use client";

import { ImageUp, PenLine, Sparkles } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCreateModel, useGenerateImages, useUploadImage } from "@/features/creator/hooks";
import { useCreatorStore } from "@/features/creator/store";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "Um dragão bebê dormindo enrolado",
  "Uma coruja de óculos lendo um livro",
  "Um astronauta acenando",
  "Um cacto sorridente num vasinho",
];

export function PromptStep() {
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-center font-display text-4xl font-semibold tracking-tight">
        O que você quer criar?
      </h1>
      <p className="mt-3 text-center text-muted">
        Descreva o objeto ou envie uma foto. Antes do 3D, você escolhe a imagem que mais combina com
        a sua ideia.
      </p>

      <Tabs defaultValue="describe" className="mt-8">
        <div className="flex justify-center">
          <TabsList>
            <TabsTrigger value="describe">
              <PenLine />
              Descrever
            </TabsTrigger>
            <TabsTrigger value="upload">
              <ImageUp />
              Enviar foto
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="describe" className="mt-6">
          <DescribeForm />
        </TabsContent>
        <TabsContent value="upload" className="mt-6">
          <UploadDropzone />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function DescribeForm() {
  const prompt = useCreatorStore((state) => state.prompt);
  const setPrompt = useCreatorStore((state) => state.setPrompt);
  const setStep = useCreatorStore((state) => state.setStep);
  const generate = useGenerateImages();
  const trimmed = prompt.trim();

  function submit() {
    if (!trimmed) return;
    generate.mutate(trimmed);
    setStep("pick");
  }

  return (
    <Card className="p-2">
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
        <div className="flex flex-wrap items-center justify-between gap-3 px-2 pb-2">
          <div className="flex flex-wrap gap-2">
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
          <Button type="submit" variant="accent" disabled={!trimmed}>
            <Sparkles />
            Gerar imagens
          </Button>
        </div>
      </form>
    </Card>
  );
}

function UploadDropzone() {
  const upload = useUploadImage();
  const createModel = useCreateModel();
  const isSending = upload.isPending || createModel.isPending;
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function send(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Envie um arquivo de imagem (JPG, PNG, WEBP).");
      return;
    }
    upload.mutate(file, {
      onSuccess: (image) => createModel.mutate(image),
      onError: (error) => toast.error(error.message),
    });
  }

  return (
    <label
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        send(event.dataTransfer.files[0]);
      }}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-line bg-surface px-6 py-16 text-center transition-colors hover:border-ink/30",
        isDragging && "border-accent bg-accent-soft",
        isSending && "pointer-events-none opacity-60",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="sr-only"
        onChange={(event) => send(event.target.files?.[0])}
      />
      <span className="flex size-12 items-center justify-center rounded-full bg-sunken">
        <ImageUp className="size-6 text-muted" aria-hidden />
      </span>
      <span className="font-medium">
        {isSending ? "Enviando…" : "Arraste uma foto ou clique para escolher"}
      </span>
      <span className="max-w-sm text-sm text-muted">
        Funciona melhor com um único objeto, bem iluminado e com o fundo simples.
      </span>
    </label>
  );
}
