"use client";

import { unwrap } from "@kubo/api-client";
import { qk, useApiClient } from "@kubo/api-client/react";
import { useQuery } from "@tanstack/react-query";

const HOUR = 60 * 60 * 1000;

export function useStyles() {
  const api = useApiClient();
  return useQuery({
    queryKey: qk.styles(),
    staleTime: HOUR,
    queryFn: async () => unwrap(await api.GET("/api/catalog/styles/")),
  });
}

export function useSizes() {
  const api = useApiClient();
  return useQuery({
    queryKey: qk.sizes(),
    staleTime: 5 * 60 * 1000,
    queryFn: async () => unwrap(await api.GET("/api/catalog/sizes/")),
  });
}
