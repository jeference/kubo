const DJANGO_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const env = {
  /** Origem do Django. O Next reescreve /api/* para cá; código de servidor chama direto. */
  djangoUrl: DJANGO_URL,
} as const;

/** O navegador fala sempre com a mesma origem, então não há CORS. */
export function apiBaseUrl(): string {
  return typeof window === "undefined" ? DJANGO_URL : window.location.origin;
}
