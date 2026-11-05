import { Button } from "@kubo/ui/button";
import { EmptyState } from "@kubo/ui/empty-state";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl py-16">
      <EmptyState
        title="Página não encontrada"
        description="O endereço pode estar errado, ou a página não existe mais."
        action={
          <Button asChild variant="accent">
            <Link href="/">Criar algo novo</Link>
          </Button>
        }
      />
    </div>
  );
}
