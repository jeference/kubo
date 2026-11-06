# PRD: MVP da Kubo

| | |
|---|---|
| **Status** | Rascunho para validação |
| **Data** | 04/11/2026, revisado em 05/11/2026 (compra direto do 2D) |
| **Documento irmão** | [Arquitetura do MVP](ARQUITETURA.md) |

> **Como ler as marcações.** **P0** é obrigatório para lançar. **P1** é importante, mas pode entrar logo depois do lançamento. **[Proposta]** é um valor ou escolha inicial que ainda precisa de validação. O restante é decisão tomada.

---

## 1. Visão geral

A Kubo transforma uma foto em um objeto físico, impresso em 3D. O cliente envia uma imagem, pede uma mudança se quiser, vê o resultado em 2D, ajusta conversando com a IA e compra a peça a partir da imagem. A peça é impressa e enviada para a casa dele.

**O cliente não vê um modelo 3D antes de comprar.** Como na Pockella, a compra abre assim que a imagem fica pronta. O modelo 3D é feito depois do pagamento, na preparação de impressão, que está fora do MVP.

A plataforma terá dois lados: o **app do cliente** e, no futuro, o **app dos parceiros**, que imprimem e enviam os pedidos. O cliente compra da Kubo e não vê quem imprimiu.

**O MVP entrega o app do cliente, do primeiro prompt até o pedido pago.** **Este app não tem nenhuma funcionalidade de operação:** tratar pedidos, baixar arquivos, atualizar status e informar rastreio pertencem ao app de parceiros. Os dados já ficam organizados para ele.

### Problema

Quem quer uma peça personalizada hoje precisa saber modelar em 3D, contratar um modelador ou recorrer a serviços com prazo longo e pouco controle sobre o resultado. Os concorrentes analisados provam que a demanda existe, mas deixam espaços abertos:

- **Jujubit:** tem prompt, foto e edição por chat, mas o cliente não aprova o 2D antes do 3D, e a entrega leva semanas a partir do exterior.
- **Meshy Shop:** aprova o 2D antes do 3D, mas aceita só foto, não permite ajustes e vende apenas pessoas e pets, com previsão de cerca de 21 dias na tela.
- **Pockella**, a loja da Meshy que substituiu a Meshy Shop: vende a figura direto do 2D, em cerca de 15 s, mas aceita só foto, não permite ajustes e envia do exterior.

### O que o MVP precisa provar

1. Pessoas completam o fluxo de criação e **pagam** por uma peça personalizada.
2. O custo de IA por venda é sustentável, mesmo com geração aberta sem login.
3. Os pedidos pagos podem ser produzidos e enviados com qualidade aceitável.

---

## 2. Objetivos e não-objetivos

### Objetivos

- Permitir gerar e comprar sem criar conta, com o menor atrito possível.
- Manter no produto real a experiência de criação validada no protótipo.
- Tornar persistente tudo que hoje se perde ao recarregar a página.
- Cobrar com segurança e dar ao cliente visibilidade do pedido.
- Registrar prompts, imagens, modelos, custos e eventos desde o primeiro dia.
- Deixar dados e estrutura prontos para o app dos parceiros, sem construí-lo agora.

### Não-objetivos

- **Qualquer modelo 3D no app do cliente:** sem geração 3D, visualizador 3D ou estimativa de custo pela malha antes da compra.
- **Tudo que acontece depois do pagamento e exige automação:** geração do modelo 3D, validação e reparo da malha, redução a 4 cores, arquivo de impressão, atribuição automática a parceiros.
- App de parceiros e repasse financeiro a parceiros.
- **Qualquer funcionalidade de operação neste app:** ela fica toda no app de parceiros.
- Troca de cor pelo cliente.
- Assinaturas, créditos pagos, cupons e programas de desconto.
- Galeria pública, Remix, compartilhamento e páginas de template.
- Venda internacional e aplicativo nativo.

---

## 3. Personas

| Persona | Quem é | O que precisa |
|---|---|---|
| **Visitante** | Chegou por curiosidade ou para presentear alguém. Não quer criar conta | Criar e comprar rápido, pelo celular, e entender o preço cedo |
| **Cliente com conta** | Voltou, ou quer acessar suas criações em outro dispositivo | Ver criações e pedidos em um só lugar |
| **Operação Kubo** (futuro, no app de parceiros) | Equipe que trata os pedidos | Ver pedidos pagos, baixar os arquivos, atualizar status e rastreio, cancelar e reembolsar |
| **Parceiro** (futuro, no app de parceiros) | Empresa ou pessoa que imprime | Ver pedidos atribuídos, baixar arquivos, informar produção e envio |

---

## 4. Escopo

| Área | Dentro do MVP | Fora do MVP |
|---|---|---|
| **Criação** | Foto com pedido de alteração opcional, 4 estilos, imagem 2D, edição por chat com versões | Criar só a partir de texto, modelo e visualizador 3D, 4 opções por geração, desenho livre, modo Duo |
| **Continuidade** | Retomar criação ao recarregar, "Minhas criações", excluir | Galeria pública, Remix, templates |
| **Compra** | Tamanho, quantidade, carrinho, Comprar agora, cotação de frete, PIX, acompanhamento do pedido | Cartão, cupons, assinatura, venda de arquivo, realidade aumentada |
| **Conta** | Opcional, com transferência de criações e pedidos ao entrar | Login social |
| **Operação** | Nada neste app | Pedidos, arquivos, status, rastreio, cancelamento, reembolso, preços, atribuição e arquivo de impressão: tudo no app de parceiros |

### O que reaproveitamos dos concorrentes

| Funcionalidade | Inspiração | Como entra na Kubo |
|---|---|---|
| Gerar e comprar sem login | Jujubit e Meshy Shop | Igual: sessão de visitante e checkout de convidado |
| Pedido ligado ao e-mail do checkout | Meshy Shop | Igual, com link de acompanhamento por e-mail |
| Comprar direto do 2D | Pockella | Igual: a compra abre assim que a imagem fica pronta, sem esperar nem pagar por um 3D |
| Edição por chat com versões | Jujubit | Igual, com cota própria (a Jujubit não limita) |
| Estilos | Jujubit | 4 estilos ajustados contra as referências |
| Cota reservada e debitada só no sucesso | Jujubit | Igual, valendo também para edição |
| Retomar tarefas em andamento | Meshy Shop | Igual |
| Botões de compra fixos no celular | Jujubit | Igual, sempre com o preço ao lado |
| Unir histórico ao entrar | Jujubit | Igual (a Meshy Shop não faz) |

### O que evitamos de propósito

| Problema observado | Decisão na Kubo |
|---|---|
| Barra de progresso falsa, parada em 90% | Mensagens de etapa e tempo decorrido, sem porcentagem inventada |
| Preço que muda depois do 3D (Meshy Shop) | Preço fixo por tamanho, visível junto com a imagem |
| Aviso de que a peça pode variar em um só produto (Pockella) | O aviso aparece em toda tela de compra |
| Mensagem genérica em recusa de conteúdo | Explicar o motivo e o que fazer |
| Links de produção expostos ao navegador antes do pagamento | Arquivos de produção só no servidor |
| Pop-ups e contadores de urgência | Fora do produto |

---

## 5. Jornadas

### 5.1 Criar e comprar (caminho principal)

| # | Tela | O cliente faz | O sistema faz |
|---|---|---|---|
| 1 | **Início** | Escolhe o estilo. Escreve o que quer, envia uma foto, ou os dois | Cria a sessão de visitante, se ainda não existir |
| 2 | **Gerando imagem** | Aguarda | Mostra etapas e tempo decorrido. Pode recarregar sem perder a criação |
| 3 | **Comprar** | Vê a imagem e, ao lado, escolhe tamanho e quantidade. Pode **Editar** a imagem antes | Mostra o preço e informa que a peça pode diferir da imagem. Mantém a criação salva |
| 4 | **Editar** (opcional) | Pede ajustes pelo chat, compara versões, cancela ou conclui | Gera uma nova versão a partir da escolhida. A versão concluída passa a ser a imagem da compra |
| 5 | **Carrinho** | Revê itens ou segue direto com **Comprar agora** | Mantém o carrinho entre visitas |
| 6 | **Checkout** | Informa e-mail, nome, CPF, telefone e endereço. Escolhe o frete | Preenche o endereço pelo CEP (P1), cota o frete e mostra o total |
| 7 | **Pagamento** | Paga o PIX por QR Code ou copia e cola | Mostra o prazo de 30 minutos e aguarda a confirmação |
| 8 | **Pedido confirmado** | Vê o número e o prazo | Envia e-mail com link de acompanhamento |
| 9 | **Acompanhar** | Consulta o status e o rastreio | Mostra Recebido → Em produção → Enviado → Entregue |

### 5.2 Estados de exceção

| Situação | O que o cliente vê | O que acontece |
|---|---|---|
| Falha na geração | Mensagem clara e **Tentar de novo** | Cota devolvida |
| Conteúdo recusado | O motivo em linguagem simples, junto da criação, e sugestão de ajuste | Cota devolvida, recusa registrada |
| Cota do dia esgotada | Quanto falta para renovar e, se fizer sentido, convite para criar conta | Nada é enviado ao provedor |
| Geração pausada pelo teto de gasto | Aviso de alta demanda, sem culpar o cliente | Alerta interno é gerado |
| Fechou a página durante a geração | Ao voltar, retoma de onde parou | A tarefa continua no servidor |
| Frete indisponível | Aviso para tentar de novo em instantes | Checkout não avança sem frete válido |
| Frete mudou ao fechar o pedido | Novo valor, com pedido de confirmação | Pedido só é criado após a confirmação |
| Tamanho desativado entre o carrinho e o fechamento | Aviso para escolher outro tamanho | Pedido não é criado |
| PIX expirado | Aviso e botão para gerar um novo PIX, por até 24 horas. Depois disso, volta ao carrinho | Pedido expira, o carrinho permanece |
| Pagamento em atraso, após a expiração | Pedido confirmado normalmente | Alerta interno é gerado para conferência |
| PIX pago em duplicidade | Pedido confirmado normalmente | Alerta interno é gerado para devolver o valor excedente |

### 5.3 Depois do pagamento

O pedido pago fica registrado com tudo congelado, e o cliente o vê como **Recebido**. Os status seguintes (Em produção, Enviado, Entregue) e o rastreio aparecem para o cliente assim que são informados pelo app de parceiros, fora deste app.

---

## 6. Requisitos funcionais

### 6.1 Criação

| ID | Requisito | Prioridade |
|---|---|---|
| RF-CRI-01 | Criar a partir de uma foto, que é obrigatória, com pedido de alteração opcional (até 1.000 caracteres) | P0 |
| RF-CRI-02 | Aceitar PNG, JPG e WEBP de até 10 MB [Proposta], corrigindo a orientação da foto | P0 |
| RF-CRI-03 | Oferecer os estilos Livre, Pixar, Mini Pop e Chibi, com miniatura | P0 |
| RF-CRI-04 | Gerar uma imagem por solicitação, em fundo claro | P0 |
| RF-CRI-05 | Abrir a compra assim que a imagem fica pronta, sem etapa de 3D | P0 |
| RF-CRI-06 | Editar por chat (até 200 caracteres por instrução), a partir de qualquer versão | P0 |
| RF-CRI-07 | Mostrar o histórico de versões, cancelar a edição ou concluir com a versão escolhida | P0 |
| RF-CRI-08 | Manter nos itens do carrinho a imagem com que foram adicionados, mesmo depois de uma edição | P0 |
| RF-CRI-09 | Avisar quando uma edição perder o fundo claro | P1 |
| RF-CRI-12 | Mostrar etapas e tempo decorrido durante cada espera | P0 |
| RF-CRI-13 | Retomar qualquer criação e tarefa em andamento após recarregar | P0 |

### 6.2 Minhas criações

| ID | Requisito | Prioridade |
|---|---|---|
| RF-HIS-01 | Listar as criações do visitante ou da conta, com miniatura e status | P0 |
| RF-HIS-02 | Abrir uma criação no ponto em que parou | P0 |
| RF-HIS-03 | Excluir uma criação, mantendo intactos os dados de pedidos | P0 |

### 6.3 Compra

| ID | Requisito | Prioridade |
|---|---|---|
| RF-COM-01 | Escolher entre os tamanhos ativos e quantidade de 1 a 10 | P0 |
| RF-COM-02 | Mostrar o preço por tamanho e o total em reais | P0 |
| RF-COM-04 | Adicionar ao carrinho ou seguir direto com Comprar agora | P0 |
| RF-COM-05 | Manter o carrinho da sessão ou da conta | P0 |
| RF-COM-06 | Finalizar sem conta, informando e-mail, nome, CPF, telefone e endereço | P0 |
| RF-COM-07 | Cotar o frete por CEP, com valor e prazo por serviço | P0 |
| RF-COM-08 | Somar ao prazo de entrega o prazo de produção da Kubo | P0 |
| RF-COM-09 | Pagar com PIX, com QR Code, copia e cola e prazo visível | P0 |
| RF-COM-10 | Confirmar o pagamento sem o cliente precisar recarregar a página | P0 |
| RF-COM-11 | Exigir o aceite dos termos e da política de trocas ao fechar o pedido | P0 |
| RF-COM-12 | Preencher o endereço pelo CEP | P1 |

### 6.4 Pedido

| ID | Requisito | Prioridade |
|---|---|---|
| RF-PED-01 | Acompanhar o pedido sem login, por link enviado ao e-mail | P0 |
| RF-PED-02 | Reenviar o link de acompanhamento, sem revelar se o e-mail existe | P0 |
| RF-PED-03 | Mostrar status, itens, valores, endereço de entrega e rastreio | P0 |
| RF-PED-04 | Listar os pedidos na conta | P0 |
| RF-PED-05 | Enviar e-mail na confirmação e a cada mudança de status do pedido | P0 |

### 6.5 Conta (opcional)

| ID | Requisito | Prioridade |
|---|---|---|
| RF-CON-01 | Cadastrar com e-mail e senha, verificando o e-mail por código | P0 |
| RF-CON-02 | Entrar, sair e recuperar a senha por código | P0 |
| RF-CON-03 | Transferir para a conta as criações e o carrinho da sessão ao entrar | P0 |
| RF-CON-04 | Vincular à conta os pedidos feitos com o e-mail verificado | P0 |
| RF-CON-05 | Editar os dados do perfil | P1 |
| RF-CON-06 | Solicitar a exclusão da conta e dos dados | P0 |

### 6.6 Páginas institucionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-INS-01 | Publicar Termos de Uso, Política de Privacidade e Política de Trocas e Devoluções | P0 |
| RF-INS-02 | Publicar página de ajuda com canal de contato | P0 |
| RF-INS-03 | Incluir na página inicial seções de exemplos, como funciona e perguntas frequentes | P1 |

---

## 7. Regras de negócio

### Geração e custo

| ID | Regra |
|---|---|
| RN-01 | **O 2D é gerado com GPT Image 2, via Runware**, como no protótipo. O MVP não gera 3D. |
| RN-02 | A cota é reservada ao iniciar a tarefa e debitada só no sucesso. Falhas e recusas devolvem a cota. |
| RN-03 | A cota vale separadamente para geração 2D e edição. |
| RN-04 | Limites iniciais por dia e por sessão: **10 gerações 2D e 15 edições** [Proposta]. Contas têm o mesmo limite. A contagem renova à meia-noite de Brasília. |
| RN-05 | Cada sessão tem no máximo 2 tarefas em andamento [Proposta]. |
| RN-06 | Como a cota por sessão é burlável, há também **limite por IP e teto global de gasto diário**. Teto inicial de US$ 30 por dia [Proposta]. |
| RN-07 | Ao atingir o teto global, novas gerações são pausadas e um alerta interno é gerado. Compras seguem funcionando. |
| RN-08 | Cancelar uma edição oculta o resultado. Se o provedor já tiver processado a tarefa, o custo é registrado e a cota é consumida. |
| RN-09 | Concluir uma edição troca a imagem atual da criação. Itens já no carrinho continuam com a imagem com que foram adicionados. |

### Preço, frete e pagamento

| ID | Regra |
|---|---|
| RN-10 | O preço depende só do tamanho e aparece junto com a imagem. |
| RN-11 | Tabela de preços: 4 cm R$ 59,90 · 6 cm R$ 99,90 · 8 cm R$ 144,90 · 10 cm R$ 189,90 · 12 cm R$ 229,90. |
| RN-12 | **Tamanho é a maior dimensão da peça** [Proposta]. |
| RN-13 | **Compra só com a imagem:** o cliente compra sem ver um modelo 3D. O 3D é feito depois do pagamento, na preparação de impressão. |
| RN-14 | Sem malha antes da compra, não há como medir o custo de cada peça. **O preço de cada tamanho precisa cobrir as peças mais pesadas** [Proposta, a calibrar com impressões reais]. |
| RN-15 | O frete é cotado por CEP e recalculado no servidor ao fechar o pedido. Se mudar, o cliente confirma o novo valor. |
| RN-16 | O prazo mostrado é a soma do prazo de produção com o do frete. Prazo de produção inicial de 7 dias úteis [Proposta]. |
| RN-17 | Preço, frete, imagem, prompt e endereço ficam congelados no pedido. Mudanças posteriores não os alteram. |
| RN-18 | O PIX expira em 30 minutos. Sem pagamento, o pedido expira e o carrinho permanece. |
| RN-19 | No lançamento, o único meio de pagamento é o PIX. |
| RN-20 | O pedido só é confirmado por notificação do gateway, conferida junto a ele. Nada informado pelo navegador confirma pagamento. |

### Pedido e pós-venda

| ID | Regra |
|---|---|
| RN-21 | O pedido fica ligado ao e-mail do checkout. Ele só passa para uma conta depois que aquele e-mail é verificado. |
| RN-22 | O reembolso pela API do gateway é sempre do **valor integral da cobrança**. Por isso, todo reembolso é do pedido inteiro. Até o app de parceiros existir, ele é feito direto no painel do gateway, e o pedido é atualizado automaticamente. |
| RN-23 | Política de cancelamento e troca [Proposta, depende do jurídico]: cancelamento sem custo enquanto o pedido não estiver em produção; reposição ou reembolso em caso de defeito ou dano, informado em até 7 dias após a entrega, com fotos. |
| RN-24 | O cliente nunca vê quem produziu a peça. Parceiros, quando existirem, não verão e-mail nem CPF do cliente. |

### Conteúdo e dados

| ID | Regra |
|---|---|
| RN-26 | Recusas do provedor viram mensagens amigáveis. Passar pelo filtro do provedor não significa que o conteúdo é permitido. |
| RN-27 | Um pedido com conteúdo que viole direitos de terceiros pode ser recusado e reembolsado. A ferramenta para isso fica no app de parceiros. |
| RN-28 | **Arquivos ligados a pedidos nunca são apagados automaticamente.** |
| RN-29 | O arquivo de produção não é enviado ao navegador do cliente. |

---

## 8. Dados a preservar

Mesmo sem o app de parceiros, o MVP guarda desde o primeiro dia:

| Dado | Por que importa |
|---|---|
| Texto do cliente, estilo, foto enviada e prompt final enviado ao modelo | Reproduzir, ajustar prompts e investigar problemas |
| Todas as versões de imagem, com origem e instrução de edição | Histórico e base para gerar o 3D na produção |
| Modelo de IA, versão do prompt, custo, tempo e erro de cada tarefa | Custo por venda e confiabilidade |
| Pedidos com tudo congelado no momento da compra | Produção, atendimento e contabilidade |
| Evento imutável a cada mudança de status | Auditoria e métricas de funil |
| Lançamentos financeiros imutáveis | Conciliação e repasse futuro a parceiros |
| Parceiro, atribuição e tarefa de produção por item | Entrada do app de parceiros sem refazer a base |

A retenção de arquivos tem prazos próprios, porque fotos e rostos são dados pessoais. Os prazos propostos estão na [arquitetura](ARQUITETURA.md#15-storage-e-acesso) e dependem de validação jurídica.

---

## 9. Métricas

**Métrica principal:** taxa de conversão de quem inicia uma criação em pedido pago.

| Grupo | Métrica |
|---|---|
| **Funil** | Prompt enviado → 2D gerado → tamanho escolhido → item no carrinho → checkout iniciado → PIX gerado → pago |
| **Custo** | Custo de IA por criação e por venda; custo total por dia |
| **Confiabilidade** | Taxa de falha e de recusa por etapa; tarefas presas |
| **Tempo** | Tempo por etapa (p50 e p95) |
| **Abuso** | Sessões e IPs no limite; dias com teto atingido |
| **Pós-venda** | Pedidos por status; taxa de reembolso |

Não há metas numéricas ainda: as primeiras semanas servem para formar a linha de base.

---

## 10. Riscos e condições de lançamento

### Riscos

| Risco | Impacto | Como tratamos |
|---|---|---|
| **Vender sem saber se dá para imprimir.** O cliente compra uma imagem, e o 3D só é feito depois do pagamento. Nada foi impresso, e a preparação de impressão ficou fora do MVP | **Crítico:** pedidos parados ou reembolsados | Teste real, da imagem à peça impressa, como condição de lançamento |
| **A peça difere da imagem.** O cliente não vê o 3D antes de pagar, o modelo pode mudar a forma, a impressão FDM tem até 4 cores, e o limite de cores nas imagens não é garantido (15 de 18 imagens no Mini Pop e 14 de 18 no Chibi, contadas a olho) | Alto: frustração e pedidos de reembolso | Aviso claro no produto e nos termos, e revisão antes de produzir |
| **Abuso da geração aberta** | Alto: gasto sem venda | Cotas, limite por IP e teto global |
| **Margem incorreta.** O preço é fixo por tamanho, e nenhuma peça é medida antes da compra. Uma peça maciça, ou a purga das 4 cores, pode custar mais que o previsto | Alto: venda com prejuízo, sem ninguém perceber | Calibrar a tabela com impressões reais e acompanhar o custo de cada pedido |
| **Peça muito pequena.** 4 cm em FDM com várias cores pode não ser viável | Médio | Testar antes de lançar. Tamanhos inviáveis ficam inativos |
| **Pedido pago sem tratamento.** Este app não tem operação: sem o app de parceiros, nenhuma tela do sistema mostra pedidos, entrega os arquivos ou registra o rastreio, e o cliente fica parado em "Recebido" | **Crítico** | O app de parceiros é o próximo passo depois do app do cliente, e vendas reais só começam com a operação pronta |
| **Só PIX reduz a conversão** em compras de maior valor | Médio | Medir o abandono no pagamento. O gateway também oferece cartão |
| **Provedor único de IA** | Médio | Toda integração fica isolada, permitindo trocar de provedor |

### Pontos jurídicos (validar com advogado)

Estas notas são pontos de leitura, não aconselhamento jurídico.

- **Fotos de pessoas e menores:** tratamento sob a LGPD, consentimento e envio de dados ao exterior.
- **Termos da Runware (29/09/2026):**
  - O cliente da API é dono dos resultados, e o uso comercial é permitido.
  - Proíbem reproduzir "a identidade ou a semelhança" de uma pessoa viva sem consentimento, o que atinge diretamente o fluxo de fotos.
  - A responsabilidade por entradas e indenizações recai sobre quem usa o serviço, e a Runware não guarda resultados a longo prazo.
- **Políticas do GPT Image 2 acessado via Runware:** ainda não analisadas.
- **Direito de arrependimento em peça personalizada:** vale conferir a redação da política de trocas à luz do Código de Defesa do Consumidor.
- **Nota fiscal e tributação da venda:** a emissão fica fora do sistema no MVP, mas precisa estar resolvida antes da primeira venda.
- **Propriedade intelectual:** personagens e marcas, com fluxo de remoção.
- **Nomes e imagens dos estilos:** "Mini Pop" é o nome usado pela Jujubit, e a origem das miniaturas atuais não foi confirmada.

### Condições para lançar

- [ ] Amostras reais impressas a partir de imagens geradas, em cada tamanho oferecido, com tamanhos inviáveis desativados.
- [ ] **Operação do app de parceiros pronta**, construída depois de concluído o app do cliente.
- [ ] Definido como a imagem vira peça: geração 3D, reparo, cores e fatiamento.
- [ ] Tabela de preços conferida com o custo das impressões.
- [ ] Prazo de produção confirmado.
- [ ] Revisão jurídica concluída, com termos, privacidade e trocas publicados.
- [ ] Emissão de nota fiscal definida.
- [ ] Contas de produção ativas e verificadas: gateway de pagamento, frete, e-mail, armazenamento.
- [ ] Teste completo em produção, com compra real via PIX e reembolso.
- [ ] Teto de gasto e alertas testados.

---

## 11. Depois do MVP

**O próximo passo definido é o app de parceiros**, começando quando o app do cliente estiver pronto.

1. **App de parceiros, incluindo toda a operação** (lista abaixo).

Os demais itens têm ordem sugerida, a confirmar com os dados do MVP:

2. **Preparação de impressão:** escolha do provedor 3D, geração do modelo a partir da imagem do pedido, validação, reparo, redução a 4 cores e arquivo de impressão.
3. **Cartão de crédito:** o gateway já oferece, com parcelamento.
4. **Troca de cor pelo cliente:** depende de inspecionar um 3MF real.
5. **Atribuição automática de pedidos e repasse a parceiros.**
6. **Crescimento:** galeria, Remix, templates, cupons e 4 opções por geração.

### O que o app de parceiros precisa cobrir

**Para a operação da Kubo:**

- Listar e filtrar pedidos por status, data e e-mail.
- Ver no pedido a imagem comprada, o prompt, o estilo, o tamanho e o endereço.
- Baixar a imagem de cada item e, quando existir, o modelo, com registro de acesso.
- Avançar o status do pedido e registrar transportadora e rastreio.
- Cancelar e reembolsar o pedido inteiro, com motivo.
- Gerenciar preços e tamanhos ativos.
- Consultar criações e tarefas, com custo, tempo e erro.
- Ver alertas de pagamento sem pedido, pagamento em duplicidade e teto de gasto atingido.
- Atender solicitações de remoção de conteúdo.

**Para os parceiros:**

- Ver os pedidos atribuídos, baixar arquivos e informar produção e envio.

### Atenção aos fornecedores

**Sobre a preparação de impressão:** Tripo e Meshy têm cláusulas sobre usuários finais, fotos de pessoas e revenda que exigem autorização por escrito, e a Meshy vende o mesmo tipo de produto. Veja o [comparativo de fornecedores](fornecedores-3d/comparativo/Endpoints%20Tripo%20AI%20e%20Meshy.md).

---

## 12. Glossário

| Termo | Significado |
|---|---|
| **Criação** | O projeto do cliente: entrada e versões de imagem |
| **Versão** | Cada imagem 2D de uma criação |
| **Prévia** | A imagem 2D que o cliente compra |
| **Modelo 3D** | Modelo feito a partir da imagem do pedido, depois do pagamento (fora do MVP) |
| **Visitante** | Cliente sem conta, identificado por uma sessão no navegador |
| **Cota** | Limite diário de gerações por sessão ou conta |
| **Teto de gasto** | Limite diário de gasto com IA em toda a plataforma |
| **Operação** | Equipe interna da Kubo que trata os pedidos, pelo app de parceiros |
| **Parceiro** | Quem imprime e envia. Invisível para o cliente |
| **FDM** | Impressão 3D por filamento derretido |
| **PIX copia e cola** | Código de pagamento que o cliente cola no app do banco |

### Fontes dos estudos

- [Estudo da Jujubit](concorrencia/jujubit/jujubit.md) e [estudo de estilos](concorrencia/jujubit/estilos/README.md)
- [Estudo da Meshy Shop](concorrencia/meshy-shop/meshy-shop.md)
- [Estudo da Pockella](concorrencia/pockella/pockella.md), a loja que substituiu a Meshy Shop
- [Termos comerciais dos fornecedores 3D](fornecedores-3d/comparativo/commercial_terms.md)
- [Protótipo](../prototipo/README.md)
