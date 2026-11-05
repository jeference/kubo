"use client";

import { unwrap } from "@kubo/api-client";
import { qk, useApiClient } from "@kubo/api-client/react";
import { useActorReady } from "@kubo/web-core/session";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

const PIX_POLL_MS = 3000;
const ACTIVE_ORDER_POLL_MS = 30_000;
const FINAL_STATUSES = new Set(["delivered", "refunded", "expired"]);

export function useOrders() {
  const api = useApiClient();
  const ready = useActorReady();
  return useQuery({
    queryKey: qk.orders(),
    enabled: ready,
    staleTime: 0,
    queryFn: async () => unwrap(await api.GET("/api/orders/")),
  });
}

export function useOrder(id: string) {
  const api = useApiClient();
  const ready = useActorReady();
  return useQuery({
    queryKey: qk.order(id),
    enabled: ready,
    staleTime: 0,
    queryFn: async () =>
      unwrap(await api.GET("/api/orders/{order_id}/", { params: { path: { order_id: id } } })),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "pending_payment") return PIX_POLL_MS;
      if (!status || FINAL_STATUSES.has(status)) return false;
      return ACTIVE_ORDER_POLL_MS;
    },
  });
}

export function usePayOrder(id: string) {
  const api = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST("/api/orders/{order_id}/pay/", { params: { path: { order_id: id } } }),
      ),
    onSuccess: (order) => {
      queryClient.setQueryData(qk.order(id), order);
      void queryClient.invalidateQueries({ queryKey: qk.orders(), exact: true });
    },
  });
}

export function useTracking(token: string) {
  const api = useApiClient();
  return useQuery({
    queryKey: qk.tracking(token),
    queryFn: async () =>
      unwrap(await api.GET("/api/orders/track/{token}/", { params: { path: { token } } })),
    refetchInterval: (query) =>
      query.state.data && !FINAL_STATUSES.has(query.state.data.status)
        ? ACTIVE_ORDER_POLL_MS
        : false,
  });
}
