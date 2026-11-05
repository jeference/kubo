import type { ReactNode } from "react";

export function LegalPage({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="mx-auto max-w-3xl space-y-5 text-[15px] leading-relaxed [&_h2]:mt-8 [&_h2]:font-display [&_h2]:text-xl [&_h2]:font-semibold">
      <h1 className="font-display text-3xl font-semibold tracking-tight">{title}</h1>
      {children}
    </article>
  );
}
