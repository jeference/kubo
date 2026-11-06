/**
 * URLs assinadas mudam a cada resposta. Sem isto, cada polling baixaria de novo as imagens.
 * Mantém a URL de cada arquivo enquanto ela ainda é válida (a assinatura dura 5 minutos).
 */
const REUSE_MS = 4 * 60 * 1000;
const seen = new Map<string, { url: string; at: number }>();

export function stableUrl(id: string, url: string): string {
  if (!url) return url;
  const entry = seen.get(id);
  const now = Date.now();
  if (entry && now - entry.at < REUSE_MS) return entry.url;
  seen.set(id, { url, at: now });
  return url;
}
