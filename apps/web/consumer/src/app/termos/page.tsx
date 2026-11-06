import type { Metadata } from "next";

import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = { title: "Termos de Uso" };

export default function TermsPage() {
  return (
    <LegalPage title="Termos de Uso">
      <p>
        Ao usar a Kubo, você concorda com estes termos. Eles valem para a criação de imagens e
        modelos com inteligência artificial e para a compra das peças impressas.
      </p>
      <h2>O que você cria</h2>
      <p>
        As imagens e os modelos são gerados por inteligência artificial e podem não ser únicos:
        outras pessoas podem receber resultados parecidos.
      </p>
      <h2>Fotos e conteúdo enviado</h2>
      <p>
        Ao enviar uma foto, você declara que tem os direitos sobre ela e o consentimento de todas as
        pessoas que aparecem nela. Não envie fotos de terceiros sem autorização.
      </p>
      <p>
        É proibido usar a Kubo para criar conteúdo ilegal, sexual envolvendo menores, que viole
        direitos autorais, marcas ou a imagem de outras pessoas. Podemos recusar ou cancelar pedidos
        com esse tipo de conteúdo, com devolução do valor pago.
      </p>
      <h2>Prévia e peça impressa</h2>
      <p>
        A imagem é uma prévia. A peça é impressa em filamento, com até 4 cores, e pode ter
        diferenças de cor, forma e detalhe em relação a ela.
      </p>
      <h2>Limites de uso</h2>
      <p>
        Há limites diários de geração, e podemos pausar a geração temporariamente em períodos de
        muita procura.
      </p>
      <h2>Pagamento e entrega</h2>
      <p>
        O pagamento é feito por PIX, e o pedido é confirmado quando o pagamento é identificado. O
        prazo informado antes do pagamento soma a produção e o frete.
      </p>
    </LegalPage>
  );
}
