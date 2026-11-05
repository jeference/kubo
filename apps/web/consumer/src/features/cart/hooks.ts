"use client";

import { unwrap } from "@kubo/api-client";
import { qk, useApiClient } from "@kubo/api-client/react";
import { useActorReady } from "@kubo/web-core/session";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useCart() {
  const api = useApiClient();
  const ready = useActorReady();
  return useQuery({
    queryKey: qk.cart(),
    enabled: ready,
    queryFn: async () => unwrap(await api.GET("/api/cart/")),
  });
}

export function useAddToCart() {
  const api = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: { creation_id: string; size_id: string; quantity: number }) =>
      unwrap(await api.POST("/api/cart/items/", { body })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: qk.cart() }),
  });
}

export function useUpdateCartItem() {
  const api = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, quantity }: { id: string; quantity: number }) =>
      unwrap(
        await api.PATCH("/api/cart/items/{item_id}/", {
          params: { path: { item_id: id } },
          body: { quantity },
        }),
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: qk.cart() }),
  });
}

export function useRemoveCartItem() {
  const api = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const result = await api.DELETE("/api/cart/items/{item_id}/", {
        params: { path: { item_id: id } },
      });
      if (!result.response.ok) unwrap(result);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: qk.cart() }),
  });
}
