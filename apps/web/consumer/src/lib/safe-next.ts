/** Só caminhos internos: impede redirecionamento para outro site. */
export function safeNext(value: string | null, fallback = "/criacoes"): string {
  return value && value.startsWith("/") && !value.startsWith("//") ? value : fallback;
}
