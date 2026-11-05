import type { Metadata } from "next";

import { LegalPage } from "@/components/legal-page";

export const metadata: Metadata = { title: "Trocas e devoluções" };

export default function ReturnsPage() {
  return (
    <LegalPage title="Trocas e devoluções">
      <h2>Cancelamento</h2>
      <p>
        Você pode cancelar sem custo enquanto o pedido não entrar em produção. Fale com a gente pela
        página de ajuda, informando o número do pedido.
      </p>
      <h2>Defeito ou dano</h2>
      <p>
        Se a peça chegar com defeito ou danificada, avise em até 7 dias depois da entrega, com fotos.
        Fazemos a reposição ou devolvemos o valor pago.
      </p>
      <h2>Diferenças em relação à prévia</h2>
      <p>
        A prévia é uma aproximação. A peça é impressa em filamento com até 4 cores, e pequenas
        diferenças de cor e detalhe são esperadas.
      </p>
      <h2>Reembolso</h2>
      <p>O reembolso é feito por PIX, na conta usada no pagamento, sempre do valor total do pedido.</p>
    </LegalPage>
  );
}
