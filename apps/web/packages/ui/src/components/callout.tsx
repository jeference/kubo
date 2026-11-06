import type { ReactNode } from "react";

import { cn } from "../lib/utils";

const TONES = {
  /** Observação de apoio: prévia, prazos, letras miúdas. */
  neutral: "bg-sunken text-muted",
  /** Boa notícia ou confirmação: pagamento recebido, e-mail enviado. */
  accent: "bg-accent-soft text-ink",
  danger: "bg-danger/10 text-danger",
};

/** Caixa de aviso dentro do fluxo da página. */
export function Callout({
  tone = "neutral",
  role,
  className,
  children,
}: {
  tone?: keyof typeof TONES;
  role?: "status" | "alert";
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      role={role}
      className={cn("rounded-2xl px-4 py-3 text-sm leading-snug", TONES[tone], className)}
    >
      {children}
    </div>
  );
}
