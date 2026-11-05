"use client";

import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <div className="mx-auto max-w-xl py-16">
      <EmptyState
        title="Algo deu errado"
        description="Não conseguimos carregar esta página. Tente de novo em instantes."
        action={
          <Button variant="accent" onClick={reset}>
            Tentar de novo
          </Button>
        }
      />
    </div>
  );
}
