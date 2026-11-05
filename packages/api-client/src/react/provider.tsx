"use client";

import { createContext, createElement, useContext, type ReactNode } from "react";

import type { ApiClient } from "../core/client";

const ApiClientContext = createContext<ApiClient | null>(null);

export function ApiClientProvider({
  client,
  children,
}: {
  client: ApiClient;
  children: ReactNode;
}) {
  return createElement(ApiClientContext.Provider, { value: client }, children);
}

export function useApiClient(): ApiClient {
  const client = useContext(ApiClientContext);
  if (!client) throw new Error("useApiClient precisa estar dentro de <ApiClientProvider>.");
  return client;
}
