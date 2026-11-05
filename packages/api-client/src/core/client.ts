import createClient, { type Client, type Middleware } from "openapi-fetch";

import type { paths } from "@kubo/api-types";

import { normalizeError } from "./errors";

export interface ApiClientConfig {
  baseUrl: string;
  /** Token de acesso em memória, ou null para visitantes. */
  getAccessToken?: () => string | null;
  /** Renova o token pelo cookie, via BFF. Devolve o novo token ou null. */
  refreshAccessToken?: () => Promise<string | null>;
  /** Chamado quando a requisição continua 401 depois de renovar. */
  onAuthError?: () => void;
  fetchFn?: typeof fetch;
}

/** Marca a repetição depois de renovar: nunca é enviada duas vezes. */
const RETRIED = "x-kubo-retried";
/** Sem este cabeçalho, o cookie de visitante não autoriza escrita (proteção contra CSRF). */
export const CLIENT_HEADER = "X-Kubo-Client";

/**
 * Cliente tipado pelos `paths` gerados: caminho, parâmetros e respostas são inferidos, então
 * uma URL ou propriedade errada é erro de compilação.
 */
export type ApiClient = Client<paths>;

/** Devolve `data` no sucesso e lança um `ApiError` normalizado no erro. */
export function unwrap<D>(result: { data?: D; error?: unknown; response: Response }): D {
  if (!result.response.ok) {
    throw normalizeError(result.response.status, result.error ?? result.data ?? null);
  }
  return result.data as D;
}

function authMiddleware(config: ApiClientConfig, doFetch: typeof fetch): Middleware {
  // Cópia antes do envio, para o corpo continuar disponível na repetição.
  const pending = new Map<string, Request>();

  return {
    onRequest({ request, id }) {
      request.headers.set(CLIENT_HEADER, "web");
      const token = config.getAccessToken?.();
      if (token && !request.headers.has("Authorization")) {
        request.headers.set("Authorization", `Bearer ${token}`);
      }
      pending.set(id, request.clone());
      return request;
    },
    async onResponse({ request, response, id }) {
      const stashed = pending.get(id);
      pending.delete(id);

      if (response.status !== 401) return undefined;
      if (request.headers.has(RETRIED) || !config.refreshAccessToken) return undefined;

      const token = await config.refreshAccessToken().catch(() => null);
      if (!token) {
        config.onAuthError?.();
        return undefined;
      }
      const retry = stashed ?? request;
      retry.headers.set("Authorization", `Bearer ${token}`);
      retry.headers.set(RETRIED, "1");
      return doFetch(retry);
    },
  };
}

export function createApiClient(config: ApiClientConfig): ApiClient {
  const doFetch = config.fetchFn ?? ((input, init) => fetch(input, init));
  const client = createClient<paths>({
    baseUrl: config.baseUrl,
    fetch: (request) => doFetch(request),
  });
  client.use(authMiddleware(config, doFetch));
  return client;
}
