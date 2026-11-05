"use client";

import { ApiClientProvider, createQueryClient } from "@kubo/api-client/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode, useState } from "react";

import { getApiClient } from "./api";
import { SessionBootstrap } from "./components/session-bootstrap";

/** Núcleo comum aos apps web. Cada app compõe por cima o que é seu. */
export function CoreProviders({ children }: Readonly<{ children: ReactNode }>) {
  const [queryClient] = useState(() => createQueryClient());
  const [apiClient] = useState(() => getApiClient());

  return (
    <QueryClientProvider client={queryClient}>
      <ApiClientProvider client={apiClient}>
        <SessionBootstrap />
        {children}
      </ApiClientProvider>
    </QueryClientProvider>
  );
}
