import { type ApiClient, createApiClient } from "@kubo/api-client";

import { apiBaseUrl } from "./env";
import { useSession } from "./session";

/** Troca o cookie de refresh por um novo token de acesso, via BFF. */
export async function refreshSession(): Promise<string | null> {
  try {
    const response = await fetch("/bff/auth/refresh", { method: "POST" });
    if (!response.ok) return null;
    const data = (await response.json()) as { access?: string };
    if (!data.access) return null;
    useSession.getState().setAccessToken(data.access);
    return data.access;
  } catch {
    return null;
  }
}

let client: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!client) {
    client = createApiClient({
      baseUrl: apiBaseUrl(),
      getAccessToken: () => useSession.getState().accessToken,
      refreshAccessToken: async () => {
        if (!useSession.getState().accessToken) return null; // Visitante: nada a renovar.
        return refreshSession();
      },
      onAuthError: () => useSession.getState().clear(),
    });
  }
  return client;
}
