# PRD: MVP da Kubo

| | |
|---|---|
| **Status** | Rascunho para validação |
| **Data** | 04/11/2026 |
| **Documento irmão** | [Arquitetura do MVP](ARQUITETURA.md) |

> **Como ler as marcações.** **P0** é obrigatório para lançar. **P1** é importante, mas pode entrar logo depois do lançamento. **[Proposta]** é um valor ou escolha inicial que ainda precisa de validação. O restante é decisão tomada.

---

## 1. Visão geral

A Kubo transforma uma ideia ou uma foto em um objeto físico, impresso em 3D. O cliente descreve o que quer ou envia uma imagem, vê o resultado em 2D, ajusta conversando com a IA, confere o modelo em 3D e compra a peça, que é impressa e enviada para a casa dele.

A plataforma terá dois lados: o **app do cliente** e, no futuro, o **app dos parceiros**, que imprimem e enviam os pedidos. O cliente compra da Kubo e não vê quem imprimiu.

**O MVP entrega o app do cliente, do primeiro prompt até o pedido pago.** **Este app não tem nenhuma funcionalidade de operação:** tratar pedidos, baixar arquivos, atualizar status e informar rastreio pertencem ao app de parceiros. Os dados já ficam organizados para ele.

### Problema

Quem quer uma peça personalizada hoje precisa saber modelar em 3D, contratar um modelador ou recorrer a serviços com prazo longo e pouco controle sobre o resultado. Os concorrentes analisados provam que a demanda existe, mas deixam espaços abertos:

- **Jujubit:** tem prompt, foto e edição por chat, mas o cliente não aprova o 2D antes do 3D, e a entrega leva semanas a partir do exterior.
- **Meshy Shop:** aprova o 2D antes do 3D, mas aceita só foto, não permite ajustes e vende apenas pessoas e pets, com previsão de cerca de 21 dias na tela.

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

- **Tudo que acontece depois do pagamento e exige automação:** geração do modelo final, validação e reparo da malha, redução a 4 cores, arquivo de impressão, atribuição automática a parceiros.
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
| **Criação** | Texto e foto, 4 estilos, 2D com aprovação, edição por chat com versões, 3D, visualizador 2D/3D | 4 opções por geração, desenho livre, modo Duo |
| **Continuidade** | Retomar criação ao recarregar, "Minhas criações", excluir | Galeria pública, Remix, templates |
| **Compra** | Tamanho, quantidade, carrinho, Comprar agora, cotação de frete, PIX, acompanhamento do pedido | Cartão, cupons, assinatura, venda de arquivo, realidade aumentada |
| **Conta** | Opcional, com transferência de criações e pedidos ao entrar | Login social |
| **Operação** | Nada neste app | Pedidos, arquivos, status, rastreio, cancelamento, reembolso, preços, atribuição e arquivo de impressão: tudo no app de parceiros |

### O que reaproveitamos dos concorrentes

| Funcionalidade | Inspiração | Como entra na Kubo |
|---|---|---|
| Gerar e comprar sem login | Jujubit e Meshy Shop | Igual: sessão de visitante e checkout de convidado |
| Pedido ligado ao e-mail do checkout | Meshy Shop | Igual, com link de acompanhamento por e-mail |
| Aprovar o 2D antes do 3D | Meshy Shop | Igual: já é o fluxo do protótipo e evita gastar 3D em imagem rejeitada |
| Edição por chat com versões | Jujubit | Igual, com cota própria (a Jujubit não limita) |
| Estilos | Jujubit | 4 estilos ajustados contra as referências |
| Cota reservada e debitada só no sucesso | Jujubit | Igual, valendo também para 3D e edição |
| Retomar tarefas em andamento | Meshy Shop | Igual |
| Alternância 2D/3D no visualizador | Jujubit | Igual: já existe no protótipo |
| Botões de compra fixos no celular | Jujubit | Igual, sempre com o preço ao lado |
| Unir histórico ao entrar | Jujubit | Igual (a Meshy Shop não faz) |

### O que evitamos de propósito

| Problema observado | Decisão na Kubo |
|---|---|
| Barra de progresso falsa, parada em 90% | Mensagens de etapa e tempo decorrido, sem porcentagem inventada |
| Preço que muda depois do 3D (Meshy Shop) | Preço por tamanho visível desde o 2D |
| Modelo cinza, sem textura, entregue sem aviso (Jujubit) | Verificar a textura antes de exibir o modelo |
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
| 3 | **Validar 2D** | Vê a imagem, o preço "a partir de" e escolhe entre **Editar** e **Ficou ótimo! Gerar em 3D** | Mantém a criação salva |
| 4 | **Editar** (opcional) | Pede ajustes pelo chat, compara versões, cancela ou conclui | Gera uma nova versão a partir da escolhida. Avisa se a edição descartará um 3D já existente |
| 5 | **Gerando 3D** | Aguarda | Mostra a imagem com animação e as etapas |
| 6 | **Comprar** | Alterna 2D/3D, gira o modelo, escolhe tamanho e quantidade | Mostra o preço, desabilita tamanhos bloqueados pela trava de margem e informa que a peça pode diferir da prévia |
| 7 | **Carrinho** | Revê itens ou segue direto com **Comprar agora** | Mantém o carrinho entre visitas |
| 8 | **Checkout** | Informa e-mail, nome, CPF, telefone e endereço. Escolhe o frete | Preenche o endereço pelo CEP (P1), cota o frete e mostra o total |
| 9 | **Pagamento** | Paga o PIX por QR Code ou copia e cola | Mostra o prazo de 30 minutos e aguarda a confirmação |
| 10 | **Pedido confirmado** | Vê o número e o prazo | Envia e-mail com link de acompanhamento |
| 11 | **Acompanhar** | Consulta o status e o rastreio | Mostra Recebido → Em produção → Enviado → Entregue |

### 5.2 Estados de exceção

| Situação | O que o cliente vê | O que acontece |
|---|---|---|
| Falha na geração | Mensagem clara e **Tentar de novo** | Cota devolvida |
| Conteúdo recusado | O motivo em linguagem simples, junto da criação, e sugestão de ajuste | Cota devolvida, recusa registrada |
| Cota do dia esgotada | Quanto falta para renovar e, se fizer sentido, convite para criar conta | Nada é enviado ao provedor |
| Geração pausada pelo teto de gasto | Aviso de alta demanda, sem culpar o cliente | Alerta interno é gerado |
| Modelo sem textura | Não é exibido. Nova tentativa automática e, se falhar, erro comum | Falha registrada |
| Todos os tamanhos bloqueados para o modelo | Aviso de que este modelo não pode ser vendido e convite para ajustar a imagem | Bloqueio registrado para calibração |
| Fechou a página durante a geração | Ao voltar, retoma de onde parou | A tarefa continua no servidor |
| Frete indisponível | Aviso para tentar de novo em instantes | Checkout não avança sem frete válido |
| Frete mudou ao fechar o pedido | Novo valor, com pedido de confirmação | Pedido só é criado após a confirmação |
| Tamanho bloqueado entre o carrinho e o fechamento | Aviso para escolher outro tamanho | Pedido não é criado |
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
| RF-CRI-01 | Criar a partir de texto (até 1.000 caracteres), foto, ou foto com pedido de alteração | P0 |
| RF-CRI-02 | Aceitar PNG, JPG e WEBP de até 10 MB [Proposta], corrigindo a orientação da foto | P0 |
| RF-CRI-03 | Oferecer os estilos Livre, Pixar, Mini Pop e Chibi, com miniatura | P0 |
| RF-CRI-04 | Gerar uma imagem por solicitação, em fundo claro | P0 |
| RF-CRI-05 | Exigir a aprovação do 2D antes de gerar o 3D | P0 |
| RF-CRI-06 | Editar por chat (até 200 caracteres por instrução), a partir de qualquer versão | P0 |
| RF-CRI-07 | Mostrar o histórico de versões, cancelar a edição ou concluir com a versão escolhida | P0 |
| RF-CRI-08 | Avisar que concluir uma edição descarta o 3D atual | P0 |
| RF-CRI-09 | Avisar quando uma edição perder o fundo claro | P1 |
| RF-CRI-10 | Gerar o 3D a partir da imagem aprovada | P0 |
| RF-CRI-11 | Visualizar em 2D e 3D, com rotação, pausa e layout para celular | P0 |
| RF-CRI-12 | Mostrar etapas e tempo decorrido durante cada espera | P0 |
| RF-CRI-13 | Retomar qualquer criação e tarefa em andamento após recarregar | P0 |
| RF-CRI-14 | Exigir a declaração de direitos e consentimento ao enviar foto | P0 |
| RF-CRI-15 | Verificar se o modelo gerado tem textura antes de exibi-lo | P0 |
| RF-CRI-16 | Permitir zoom no visualizador. Ainda não implementado: o protótipo removeu o zoom de propósito, para o cliente não inspecionar a malha | P1 |

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
| RF-COM-03 | Desabilitar, por modelo, os tamanhos bloqueados pela trava de margem | P0 |
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
| RN-01 | **O 2D é gerado com GPT Image 2 e o 3D com Trellis 2, ambos via Runware**, como no protótipo. |
| RN-02 | A cota é reservada ao iniciar a tarefa e debitada só no sucesso. Falhas e recusas devolvem a cota. |
| RN-03 | A cota vale separadamente para geração 2D, edição e 3D. |
| RN-04 | Limites iniciais por dia e por sessão: **10 gerações 2D, 15 edições e 6 modelos 3D** [Proposta]. Contas têm o mesmo limite. A contagem renova à meia-noite de Brasília. |
| RN-05 | Cada sessão tem no máximo 1 modelo 3D e 2 tarefas no total em andamento [Proposta]. |
| RN-06 | Como a cota por sessão é burlável, há também **limite por IP e teto global de gasto diário**. Teto inicial de US$ 30 por dia [Proposta]. |
| RN-07 | Ao atingir o teto global, novas gerações são pausadas e um alerta interno é gerado. Compras seguem funcionando. |
| RN-08 | Cancelar uma edição oculta o resultado. Se o provedor já tiver processado a tarefa, o custo é registrado e a cota é consumida. |
| RN-09 | Concluir uma edição descarta o 3D atual da experiência do cliente, mas o registro é mantido. |

### Preço, frete e pagamento

| ID | Regra |
|---|---|
| RN-10 | O preço depende só do tamanho e aparece desde a validação do 2D. |
| RN-11 | A tabela atual do protótipo é de exemplo e **precisa ser substituída antes do lançamento**. |
| RN-12 | **Tamanho é a maior dimensão da peça** [Proposta]. |
| RN-13 | **Trava de margem:** ao concluir o 3D, o sistema estima o custo do modelo em cada tamanho e bloqueia aqueles em que a margem fica abaixo do mínimo configurado. |
| RN-14 | A estimativa é conservadora. Se o cálculo falhar, vale o pior caso, e nunca o custo zero. |
| RN-15 | O frete é cotado por CEP e recalculado no servidor ao fechar o pedido. Se mudar, o cliente confirma o novo valor. |
| RN-16 | O prazo mostrado é a soma do prazo de produção com o do frete. Prazo de produção inicial de 7 dias úteis [Proposta]. |
| RN-17 | Preço, frete, imagem, modelo, prompt e endereço ficam congelados no pedido. Mudanças posteriores não os alteram. |
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
| RN-25 | Quem envia uma foto declara ter direitos sobre ela e o consentimento das pessoas retratadas. |
| RN-26 | Recusas do provedor viram mensagens amigáveis. Passar pelo filtro do provedor não significa que o conteúdo é permitido. |
| RN-27 | Um pedido com conteúdo que viole direitos de terceiros pode ser recusado e reembolsado. A ferramenta para isso fica no app de parceiros. |
| RN-28 | **Arquivos ligados a pedidos nunca são apagados automaticamente.** |
| RN-29 | A prévia não oferece download. O arquivo de produção não é enviado ao navegador do cliente. |

---

## 8. Dados a preservar

Mesmo sem o app de parceiros, o MVP guarda desde o primeiro dia:

| Dado | Por que importa |
|---|---|
| Texto do cliente, estilo, foto enviada e prompt final enviado ao modelo | Reproduzir, ajustar prompts e investigar problemas |
| Todas as versões de imagem, com origem e instrução de edição | Histórico e base para a produção |
| Todos os modelos 3D, inclusive os descartados | Comparar qualidade e gerar o modelo final no futuro |
| Modelo de IA, versão do prompt, custo, tempo e erro de cada tarefa | Custo por venda e confiabilidade |
| Estimativa de volume e custo de cada modelo | Calibrar preços com impressões reais |
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
| **Funil** | Prompt enviado → 2D gerado → 2D aprovado → 3D gerado → item no carrinho → checkout iniciado → PIX gerado → pago |
| **Custo** | Custo de IA por criação, por 3D e por venda; custo total por dia |
| **Confiabilidade** | Taxa de falha e de recusa por etapa; modelos sem textura; tarefas presas |
| **Tempo** | Tempo por etapa (p50 e p95) |
| **Abuso** | Sessões e IPs no limite; dias com teto atingido |
| **Pós-venda** | Pedidos por status; taxa de reembolso |

Não há metas numéricas ainda: as primeiras semanas servem para formar a linha de base.

---

## 10. Riscos e condições de lançamento

### Riscos

| Risco | Impacto | Como tratamos |
|---|---|---|
| **Vender sem saber se dá para imprimir.** As malhas do Trellis são abertas, nada foi impresso, e a preparação de impressão ficou fora do MVP | **Crítico:** pedidos parados ou reembolsados | Teste real de impressão como condição de lançamento |
| **A peça difere da prévia.** A prévia é texturizada, a impressão FDM tem até 4 cores, e o limite de cores nas imagens não é garantido (15 de 18 imagens no Mini Pop e 14 de 18 no Chibi, contadas a olho) | Alto: frustração e pedidos de reembolso | Aviso claro no produto e nos termos, e revisão antes de produzir |
| **Abuso da geração aberta** | Alto: gasto sem venda | Cotas, limite por IP e teto global |
| **Margem incorreta.** A tabela é de exemplo, e o cálculo de volume não foi validado com fatiador ou impressão real. Na impressão em 4 cores, a purga pode pesar mais que a geometria | Alto: venda com prejuízo, sem ninguém perceber | Calibrar com impressões reais, comparar estimado e real |
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
- **Licença do Trellis 2:** o repositório oficial traz licença MIT, mas o site do projeto diz que seus materiais não se destinam a uso comercial. É preciso confirmar o alcance desse aviso.
- **Políticas do GPT Image 2 acessado via Runware:** ainda não analisadas.
- **Direito de arrependimento em peça personalizada:** vale conferir a redação da política de trocas à luz do Código de Defesa do Consumidor.
- **Nota fiscal e tributação da venda:** a emissão fica fora do sistema no MVP, mas precisa estar resolvida antes da primeira venda.
- **Propriedade intelectual:** personagens e marcas, com fluxo de remoção.
- **Nomes e imagens dos estilos:** "Mini Pop" é o nome usado pela Jujubit, e a origem das miniaturas atuais não foi confirmada.

### Condições para lançar

- [ ] Amostras reais de modelos do Trellis impressas em cada tamanho oferecido, com tamanhos inviáveis desativados.
- [ ] **Operação do app de parceiros pronta**, construída depois de concluído o app do cliente.
- [ ] Definido como o modelo é transformado em peça (reparo, cores e fatiamento).
- [ ] Tabela de preços real e parâmetros de custo calibrados com as impressões.
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

2. **Preparação de impressão:** escolha do provedor do modelo final, validação, reparo, redução a 4 cores e arquivo de impressão.
3. **Cartão de crédito:** o gateway já oferece, com parcelamento.
4. **Troca de cor pelo cliente:** depende de inspecionar um 3MF real.
5. **Atribuição automática de pedidos e repasse a parceiros.**
6. **Crescimento:** galeria, Remix, templates, cupons e 4 opções por geração.

### O que o app de parceiros precisa cobrir

**Para a operação da Kubo:**

- Listar e filtrar pedidos por status, data e e-mail.
- Ver no pedido a imagem aprovada, o prompt, o estilo, o tamanho e o endereço.
- Baixar a imagem e o modelo de cada item, com registro de acesso.
- Avançar o status do pedido e registrar transportadora e rastreio.
- Cancelar e reembolsar o pedido inteiro, com motivo.
- Gerenciar preços, tamanhos ativos e parâmetros de custo.
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
| **Criação** | O projeto do cliente: entrada, versões de imagem e modelos 3D |
| **Versão** | Cada imagem 2D de uma criação |
| **Prévia** | O modelo 3D do Trellis mostrado ao cliente |
| **Modelo final** | Modelo preparado para impressão (fora do MVP) |
| **Visitante** | Cliente sem conta, identificado por uma sessão no navegador |
| **Cota** | Limite diário de gerações por sessão ou conta |
| **Teto de gasto** | Limite diário de gasto com IA em toda a plataforma |
| **Trava de margem** | Bloqueio de tamanhos em que o custo estimado deixa a margem abaixo do mínimo |
| **Operação** | Equipe interna da Kubo que trata os pedidos, pelo app de parceiros |
| **Parceiro** | Quem imprime e envia. Invisível para o cliente |
| **FDM** | Impressão 3D por filamento derretido |
| **PIX copia e cola** | Código de pagamento que o cliente cola no app do banco |

### Fontes dos estudos

- [Estudo da Jujubit](concorrencia/jujubit/jujubit.md) e [estudo de estilos](concorrencia/jujubit/estilos/README.md)
- [Estudo da Meshy Shop](concorrencia/meshy-shop/meshy-shop.md)
- [Termos comerciais dos fornecedores 3D](fornecedores-3d/comparativo/commercial_terms.md)
- [Protótipo](../prototipo/README.md)
