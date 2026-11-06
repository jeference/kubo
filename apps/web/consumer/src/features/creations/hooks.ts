"use client";

import { track } from "@kubo/analytics";
import { unwrap } from "@kubo/api-client";
import { qk, useApiClient } from "@kubo/api-client/react";
import { useActorReady } from "@kubo/web-core/session";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { Creation } from "@/features/creations/types";
import { stableUrl } from "@/lib/stable-url";

const GENERATION_POLL_MS = 2000;

function withStableUrls(creation: Creation): Creation {
  return {
    ...creation,
    versions: creation.versions.map((version) => ({
      ...version,
      image_url: stableUrl(version.id, version.image_url),
    })),
  };
}

export function useCreation(id: string) {
  const api = useApiClient();
  const ready = useActorReady();
  return useQuery({
    queryKey: qk.creation(id),
    enabled: ready,
    staleTime: 0,
    select: withStableUrls,
    queryFn: async () =>
      unwrap(
        await api.GET("/api/creations/{creation_id}/", { params: { path: { creation_id: id } } }),
      ),
    refetchInterval: (query) => (query.state.data?.is_generating ? GENERATION_POLL_MS : false),
  });
}

export function useCreations() {
  const api = useApiClient();
  const ready = useActorReady();
  return useQuery({
    queryKey: qk.creations(),
    enabled: ready,
    staleTime: 0,
    queryFn: async () => unwrap(await api.GET("/api/creations/")),
  });
}

function useCreationSetter() {
  const queryClient = useQueryClient();
  return (creation: Creation) => {
    queryClient.setQueryData(qk.creation(creation.id), creation);
    void queryClient.invalidateQueries({ queryKey: qk.creations(), exact: true });
    void queryClient.invalidateQueries({ queryKey: qk.quota() });
  };
}

export interface StartCreationInput {
  text: string;
  style: string;
  photo: File;
}

export function useStartCreation() {
  const api = useApiClient();
  const setCreation = useCreationSetter();
  return useMutation({
    mutationFn: async (input: StartCreationInput) => {
      const form = new FormData();
      form.set("text", input.text);
      form.set("style", input.style);
      form.set("photo", input.photo);
      return unwrap(
        await api.POST("/api/creations/", {
          body: form as never,
          bodySerializer: (body) => body as unknown as FormData,
        }),
      );
    },
    onSuccess: (creation) => {
      setCreation(creation);
      track("prompt_submitted", { style: creation.style });
    },
  });
}

export function useCreationAction(id: string) {
  const api = useApiClient();
  const setCreation = useCreationSetter();
  const path = { params: { path: { creation_id: id } } };

  const retry = useMutation({
    mutationFn: async () => unwrap(await api.POST("/api/creations/{creation_id}/retry/", path)),
    onSuccess: setCreation,
  });
  const edit = useMutation({
    mutationFn: async (body: { version_id: string; instruction: string }) =>
      unwrap(await api.POST("/api/creations/{creation_id}/edits/", { ...path, body })),
    onSuccess: (creation) => {
      setCreation(creation);
      track("edit_requested");
    },
  });
  const cancelEdit = useMutation({
    mutationFn: async (taskId: string) =>
      unwrap(
        await api.POST("/api/creations/{creation_id}/edits/{task_id}/cancel/", {
          params: { path: { creation_id: id, task_id: taskId } },
        }),
      ),
    onSuccess: setCreation,
  });
  const applyVersion = useMutation({
    mutationFn: async (versionId: string) =>
      unwrap(
        await api.POST("/api/creations/{creation_id}/apply-version/", {
          ...path,
          body: { version_id: versionId },
        }),
      ),
    onSuccess: setCreation,
  });

  return { retry, edit, cancelEdit, applyVersion };
}

export function useDeleteCreation() {
  const api = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const result = await api.DELETE("/api/creations/{creation_id}/", {
        params: { path: { creation_id: id } },
      });
      if (!result.response.ok) unwrap(result);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: qk.creations() });
      void queryClient.invalidateQueries({ queryKey: qk.cart() });
    },
  });
}
