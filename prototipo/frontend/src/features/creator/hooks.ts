"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { useCreatorStore } from "@/features/creator/store";
import type { Credits, ModelStatus, StoredImage } from "@/features/creator/types";
import { api } from "@/lib/api";

const POLL_INTERVAL_MS = 2_000;

const qk = {
  model: (modelId: string) => ["model", modelId] as const,
  credits: () => ["credits"] as const,
};

export const GENERATE_IMAGES_KEY = ["generate-images"];

/**
 * The prompt step fires this and immediately moves to the picker, which shows skeletons
 * via `useIsMutating(GENERATE_IMAGES_KEY)` — so results are handled here, not per call.
 */
export function useGenerateImages() {
  return useMutation({
    mutationKey: GENERATE_IMAGES_KEY,
    mutationFn: (prompt: string) => api.post<StoredImage[]>("/api/generation/images/", { prompt }),
    onSuccess: (images, prompt) => {
      const store = useCreatorStore.getState();
      store.addSpend(images.reduce((sum, image) => sum + (image.cost ?? 0), 0));
      store.addRound({ prompt, images });
    },
    onError: (error) => {
      toast.error(error.message);
      const store = useCreatorStore.getState();
      if (store.rounds.length === 0) store.setStep("create");
    },
  });
}

export function useUploadImage() {
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("image", file);
      return api.postForm<StoredImage>("/api/generation/images/upload/", form);
    },
  });
}

/** Start the 3D model from a stored image and move to the model step. */
export function useCreateModel() {
  return useMutation({
    mutationFn: (image: StoredImage) =>
      api.post<ModelStatus>("/api/generation/models/", { image_id: image.id }),
    onSuccess: (model, image) => useCreatorStore.getState().startModel(model.id, image),
    onError: (error) => toast.error(error.message),
  });
}

export function useModelStatus(modelId: string | null) {
  return useQuery({
    queryKey: qk.model(modelId ?? ""),
    queryFn: async () => {
      const model = await api.get<ModelStatus>(`/api/generation/models/${modelId}/`);
      // The backend reports the cost only on the poll that finished the task.
      if (model.status === "success") useCreatorStore.getState().addSpend(model.cost);
      return model;
    },
    enabled: Boolean(modelId),
    staleTime: Infinity,
    refetchInterval: (query) => {
      if (query.state.status === "error") return false;
      const status = query.state.data?.status;
      return status === "success" || status === "error" ? false : POLL_INTERVAL_MS;
    },
  });
}

/** Balance and all-time spend straight from the Runware account — fetched fresh on demand. */
export function useCredits(enabled: boolean) {
  return useQuery({
    queryKey: qk.credits(),
    queryFn: () => api.get<Credits>("/api/generation/credits/"),
    enabled,
    staleTime: 0,
  });
}
