import { QueryClient } from "@tanstack/react-query";

import { ApiError } from "../core/errors";

/** Erros determinísticos do cliente não mudam ao repetir. */
const NON_RETRYABLE = new Set([400, 401, 403, 404, 409, 422]);

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) => {
          if (error instanceof ApiError && NON_RETRYABLE.has(error.status)) return false;
          return failureCount < 2;
        },
      },
      mutations: { retry: false },
    },
  });
}
