"use client";

import { ImagePlus, TriangleAlert } from "lucide-react";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useCatalog, useCreateRun, useRun } from "@/features/model-comparison/hooks";
import type { RunModel } from "@/features/model-comparison/types";
import { formatUsd } from "@/lib/utils";

const ModelViewer = dynamic(
  () => import("@/features/creator/components/model-viewer").then((m) => m.ModelViewer),
  { ssr: false, loading: () => <div className="skeleton size-full" /> },
);

const number = new Intl.NumberFormat("pt-BR");
const megabytes = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

function formatSettings(settings: Record<string, unknown>): string {
  return Object.entries(settings)
    .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
    .join(" · ");
}

/** TEMPORARY: local page to compare 3D models. See comparison/__init__.py in the backend. */
export function ComparisonPage() {
  const router = useRouter();
  const runId = useSearchParams().get("run");
  const run = useRun(runId);

  return (
    <div className="min-h-screen">
      <div
        role="note"
        className="sticky top-0 z-10 flex items-center justify-center gap-2 bg-amber-300 px-4 py-2 text-center text-sm font-semibold text-amber-950"
      >
        <TriangleAlert className="size-4 shrink-0" aria-hidden />
        Página temporária: só para testes locais. Não faz parte do produto.
      </div>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <h1 className="font-display text-2xl font-semibold">Comparação de modelos 3D</h1>

        <NewRunForm onCreated={(id) => router.replace(`?run=${id}`)} />

        {run.isError && !run.data && <p className="text-sm text-danger">{run.error.message}</p>}
        {runId && run.isPending && <div className="skeleton h-40 rounded-2xl" />}
        {run.data && (
          <section className="space-y-4">
            <div className="flex flex-wrap items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element -- local media, known size */}
              <img
                src={run.data.image_url}
                alt="Imagem de entrada"
                className="size-28 rounded-xl border border-line bg-white object-contain"
              />
              <RunTotal models={run.data.models} />
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {run.data.models.map((model) => (
                <ModelCard key={model.key} model={model} />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function NewRunForm({ onCreated }: { onCreated: (runId: string) => void }) {
  const catalog = useCatalog();
  const createRun = useCreateRun();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  // Tracks what was unchecked, so every model starts selected once the catalog loads.
  const [unchecked, setUnchecked] = useState<ReadonlySet<string>>(new Set());

  const selected = (catalog.data ?? []).filter((model) => !unchecked.has(model.key));
  const estimate = selected.reduce((sum, model) => sum + model.estimated_cost, 0);

  function toggle(key: string) {
    setUnchecked((current) => {
      const next = new Set(current);
      if (!next.delete(key)) next.add(key);
      return next;
    });
  }

  function submit() {
    if (!file) return;
    createRun.mutate(
      { file, models: selected.map((model) => model.key) },
      {
        onSuccess: (run) => onCreated(run.id),
        onError: (error) => toast.error(error.message),
      },
    );
  }

  return (
    <Card className="space-y-4 p-5">
      <div className="flex flex-wrap items-center gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="sr-only"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <Button type="button" variant="outline" onClick={() => fileInputRef.current?.click()}>
          <ImagePlus />
          Escolher imagem
        </Button>
        <span className="text-sm text-muted">{file?.name ?? "Nenhuma imagem escolhida"}</span>
      </div>

      {catalog.isError && (
        <p className="text-sm text-danger">Não foi possível carregar a lista de modelos.</p>
      )}
      <fieldset className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <legend className="sr-only">Modelos</legend>
        {catalog.data?.map((model) => (
          <label
            key={model.key}
            className="flex cursor-pointer items-start gap-2 rounded-xl border border-line p-3 text-sm hover:bg-sunken"
          >
            <input
              type="checkbox"
              className="mt-0.5 accent-accent"
              checked={!unchecked.has(model.key)}
              onChange={() => toggle(model.key)}
            />
            <span>
              <span className="block font-medium">{model.label}</span>
              <span className="font-mono text-xs text-muted">
                ~{formatUsd(model.estimated_cost)}
              </span>
            </span>
          </label>
        ))}
      </fieldset>

      <Button
        disabled={!file || selected.length === 0}
        pending={createRun.isPending}
        onClick={submit}
      >
        Gerar {selected.length} {selected.length === 1 ? "modelo" : "modelos"} (~
        {formatUsd(estimate)})
      </Button>
    </Card>
  );
}

function RunTotal({ models }: { models: RunModel[] }) {
  const reported = models.filter((model) => model.cost !== null);
  const total = reported.reduce((sum, model) => sum + (model.cost ?? 0), 0);
  const pending = models.filter((model) => model.status === "processing").length;

  return (
    <div>
      <p className="text-sm text-muted">Custo real desta comparação</p>
      <p className="font-mono text-2xl font-semibold">{formatUsd(total)}</p>
      <p className="text-xs text-muted">
        Custo informado em {reported.length} de {models.length} modelos
        {pending > 0 && `, ${pending} ainda gerando`}
      </p>
    </div>
  );
}

function ModelCard({ model }: { model: RunModel }) {
  return (
    <Card className="overflow-hidden">
      <div className="flex items-start justify-between gap-3 p-4">
        <h2 className="font-medium">{model.label}</h2>
        <ModelCost model={model} />
      </div>

      <div className="h-80 bg-sunken">
        {model.status === "success" && <ModelViewer url={model.glb_url} autoRotate={false} />}
        {model.status === "processing" && (
          <div className="skeleton grid size-full place-items-center text-sm text-muted">
            Gerando…
          </div>
        )}
        {model.status === "error" && (
          <div className="grid size-full place-items-center p-6 text-center text-sm text-danger">
            {model.error || "Falha ao gerar o modelo."}
          </div>
        )}
      </div>

      <div className="space-y-1 p-4 text-xs text-muted">
        {model.status === "success" && (
          <p>
            {model.seconds !== null && `~${number.format(model.seconds)} s`}
            {model.triangles !== null && ` · ${number.format(model.triangles)} triângulos`}
            {model.file_bytes !== null && ` · ${megabytes.format(model.file_bytes / 1_000_000)} MB`}
          </p>
        )}
        <p className="font-mono">{formatSettings(model.settings)}</p>
      </div>
    </Card>
  );
}

function ModelCost({ model }: { model: RunModel }) {
  const estimate = `~${formatUsd(model.estimated_cost)} estimado`;
  return (
    <div className="text-right">
      {model.cost !== null ? (
        <>
          <p className="font-mono text-lg font-semibold">{formatUsd(model.cost)}</p>
          <p className="text-xs text-muted">{estimate}</p>
        </>
      ) : model.status === "processing" ? (
        <p className="font-mono text-sm text-muted">{estimate}</p>
      ) : (
        <>
          <p className="text-sm font-medium">Custo não informado</p>
          <p className="text-xs text-muted">{estimate}</p>
        </>
      )}
    </div>
  );
}
