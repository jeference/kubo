/** Minimal fetch wrapper. Requests go to /api/* and Next proxies them to Django. */

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
  ) {
    super(message);
  }
}

type ErrorBody = { detail?: string; code?: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, init);
  } catch {
    throw new ApiError(0, "Não foi possível conectar ao servidor.");
  }
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const error = (body ?? {}) as ErrorBody;
    throw new ApiError(
      response.status,
      error.detail ?? "Algo deu errado. Tente de novo.",
      error.code,
    );
  }
  return body as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, json?: unknown, options?: { signal?: AbortSignal }) =>
    request<T>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: json === undefined ? undefined : JSON.stringify(json),
      signal: options?.signal,
    }),
  postForm: <T>(path: string, form: FormData) => request<T>(path, { method: "POST", body: form }),
};
