import type { Metadata } from "next";
import Link from "next/link";

import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = { title: "Ajuda" };

const CONTACT = process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "contato@kubo.example";

export default function HelpPage() {
  return (
    <LegalPage title="Ajuda">
      <h2>Fale com a gente</h2>
      <p>
        Escreva para{" "}
        <a href={`mailto:${CONTACT}`} className="text-accent underline">
          {CONTACT}
        </a>
        . Se for sobre um pedido, informe o número dele.
      </p>
      <h2>Onde está meu pedido?</h2>
      <p>
        Use o link enviado ao seu e-mail ou{" "}
        <Link href="/acompanhar" className="text-accent underline">
          peça um novo link
        </Link>
        .
      </p>
      <h2>Remoção de conteúdo</h2>
      <p>
        Se alguma criação usa a sua imagem ou viola um direito seu, escreva para o mesmo e-mail com
        os detalhes.
      </p>
    </LegalPage>
  );
}
