import type { Metadata } from "next";

import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = { title: "Política de Privacidade" };

export default function PrivacyPage() {
  return (
    <LegalPage title="Política de Privacidade">
      <h2>O que coletamos</h2>
      <ul className="list-disc space-y-1 pl-5">
        <li>O que você envia para criar: texto, fotos e instruções de edição.</li>
        <li>As imagens e os modelos gerados.</li>
        <li>Dados da compra: nome, e-mail, CPF, telefone e endereço.</li>
        <li>Dados técnicos, como o IP guardado de forma cifrada, para evitar abusos.</li>
      </ul>
      <h2>Para que usamos</h2>
      <p>
        Para gerar suas criações, produzir e entregar seus pedidos, atender você, cumprir obrigações
        legais e proteger o serviço contra abusos.
      </p>
      <h2>Com quem compartilhamos</h2>
      <p>
        Com os fornecedores necessários para o serviço: geração de imagens e modelos por
        inteligência artificial, pagamento, frete, armazenamento e e-mail. Alguns ficam no exterior,
        então seus dados, inclusive fotos, podem ser processados fora do Brasil.
      </p>
      <h2>Por quanto tempo guardamos</h2>
      <p>
        Fotos enviadas em criações sem pedido são apagadas em até 90 dias. Criações que você excluir
        são apagadas em até 30 dias, exceto as ligadas a um pedido. Dados de pedidos ficam guardados
        pelo prazo exigido por lei.
      </p>
      <h2>Seus direitos</h2>
      <p>
        Você pode pedir acesso, correção ou exclusão dos seus dados pela página de ajuda. Quem tem
        conta pode excluí-la diretamente em Minha conta.
      </p>
    </LegalPage>
  );
}
