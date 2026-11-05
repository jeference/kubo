import type { components } from "@kubo/api-types";

export type EventName = components["schemas"]["NameEnum"];

/** Evento do funil. Falha nunca atrapalha o cliente. Sem dados pessoais nas propriedades. */
export function track(name: EventName, properties: Record<string, string | number> = {}): void {
  if (typeof window === "undefined") return;
  void fetch("/api/events/", {
    method: "POST",
    keepalive: true,
    headers: { "Content-Type": "application/json", "X-Kubo-Client": "web" },
    body: JSON.stringify({ name, properties }),
  }).catch(() => undefined);
}
