"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRef } from "react";
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
 * The prompt step fires this and immediately moves to the studio, which shows a skeleton
 * via `useIsMutating(GENERATE_IMAGES_KEY)` — so results are handled here, not per call.
 */
export function useGenerateImages() {
  return useMutation({
    mutationKey: GENERATE_IMAGES_KEY,
    mutationFn: (prompt: string) => api.post<StoredImage[]>("/api/generation/images/", { prompt }),
    onMutate: () => useCreatorStore.getState().dropModel(),
    onSuccess: (images) => {
      const store = useCreatorStore.getState();
      store.addSpend(images.reduce((sum, image) => sum + (image.cost ?? 0), 0));
      const [first] = images;
      if (first) store.startImage(first);
    },
    onError: (error) => {
      toast.error(error.message);
      useCreatorStore.getState().setView("create");
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
    onSuccess: (image) => {
      const store = useCreatorStore.getState();
      store.startImage(image);
      store.setView("studio");
    },
    onError: (error) => toast.error(error.message),
  });
}

type EditVariables = { source: StoredImage; instruction: string };

/** Edit an image by instruction. `cancel` drops the request and leaves no error behind. */
export function useEditImage() {
  const controller = useRef<AbortController | null>(null);
  const mutation = useMutation({
    mutationFn: ({ source, instruction }: EditVariables) => {
      controller.current = new AbortController();
      return api.post<StoredImage>(
        `/api/generation/images/${source.id}/edit/`,
        { instruction },
        { signal: controller.current.signal },
      );
    },
    onSuccess: (image, { source, instruction }) => {
      const store = useCreatorStore.getState();
      store.addSpend(image.cost);
      store.addEdit(image, instruction, source.id);
    },
  });
  return {
    ...mutation,
    cancel: () => {
      controller.current?.abort();
      mutation.reset();
    },
  };
}

/** Start the 3D model from the current image and open the 3D tab. */
export function useCreateModel() {
  return useMutation({
    mutationFn: (image: StoredImage) =>
      api.post<ModelStatus>("/api/generation/models/", { image_id: image.id }),
    onSuccess: (model) => useCreatorStore.getState().startModel(model.id),
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
