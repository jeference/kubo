"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import type { CatalogModel, Run } from "@/features/model-comparison/types";
import { api, ApiError } from "@/lib/api";

const POLL_INTERVAL_MS = 5_000;

export function useCatalog() {
  return useQuery({
    queryKey: ["comparison-models"],
    queryFn: () => api.get<CatalogModel[]>("/api/comparison/models/"),
    staleTime: Infinity,
  });
}

type CreateVariables = { file: File; models: string[] };

export function useCreateRun() {
  return useMutation({
    mutationFn: ({ file, models }: CreateVariables) => {
      const form = new FormData();
      form.append("image", file);
      models.forEach((model) => form.append("models", model));
      return api.postForm<Run>("/api/comparison/runs/", form);
    },
  });
}

export function useRun(runId: string | null) {
  return useQuery({
    queryKey: ["comparison-run", runId],
    queryFn: () => api.get<Run>(`/api/comparison/runs/${runId}/`),
    enabled: Boolean(runId),
    staleTime: Infinity,
    // The backend downloads finished models during the poll, so keep going in a hidden tab.
    refetchIntervalInBackground: true,
    refetchInterval: (query) => {
      // A failed poll loses nothing: only an unknown run stops it.
      const { error, data } = query.state;
      if (error instanceof ApiError && error.status === 404) return false;
      const pending = !data || data.models.some((model) => model.status === "processing");
      return pending ? POLL_INTERVAL_MS : false;
    },
  });
}
