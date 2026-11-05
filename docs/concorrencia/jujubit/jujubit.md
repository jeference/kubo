# Jujubit (jujubit.ai): mapeamento completo

> Estudo de um concorrente direto do Kubo, feito em 31/10/2026 usando o site de verdade: um Chrome controlado por script no PC do Jeferson, sem login. Numa segunda sessão, no mesmo dia, refiz a exploração **logado** com uma conta grátis; o que só aparece com login está na [seção 13](#13-com-login-conta-e-assinatura). Em 02/11/2026, uma terceira sessão percorreu o site em layout de celular ([seção 8](#8-mobile)).
>
> Testei:
> - **42 gerações reais**, de ~35 categorias diferentes, até **estourar o limite diário**;
> - 15 edições por chat;
> - o carrinho e o checkout (parei antes de pagar);
> - a assinatura, os templates, a Inspiration com Remix, o login e a versão mobile.
>
> Também capturei e decodifiquei o tráfego da API e li o JavaScript do site.
>
> - Os prints estão em [prints/desktop/](prints/desktop/) e [prints/mobile/](prints/mobile/).
> - A **referência técnica completa** (endpoints, payloads de entrada e saída, protobuf do chat, códigos de erro) está em [jujubit-api.md](jujubit-api.md).

## Resumo em 10 pontos

1. **O que é:** uma loja Shopify que vende figuras impressas em 3D (resina, pintadas) criadas pelo próprio cliente com IA. Também vende chaveiros, *phone grips*, keycaps e luminárias. O rodapé diz "Powered by Tripo AI".
2. **Fluxo central:** estilo → foto e/ou texto e/ou desenho → **Generate** → imagem 2D (~35 s) → modelo 3D (~2 a 2,5 min no total) → tamanho → carrinho.
   - É um botão só. A imagem 2D **não precisa ser aprovada** antes do 3D: as duas saem juntas.
3. **Não exige login para gerar.** O histórico fica salvo por um `anonymousId` e sobrevive ao recarregar a página.
   - Cota de **40 gerações por dia** (há um teste A/B com 25), com **até 6 simultâneas**. A cota só desconta gerações bem-sucedidas.
   - **Edições não consomem cota e não têm limite visível**, mesmo depois de a cota diária acabar (seção 11).
4. **Quem gera o 3D é a Tripo.** Todos os 40 GLB dizem `generator: https://tripo3d.ai`. Têm materiais PBR e 3 texturas 2048².
   - **Free Style:** ~1,15 milhão de faces (~36 MB).
   - **Estilos:** ~290 mil faces (~11 MB).
5. **A imagem 2D é a referência da compra.** O item vai para o carrinho com a URL da imagem 2D, e a promessa é *"Free Pro Refinement: Based on Your 2D Image"*: artistas refazem e ajustam o modelo à mão antes de imprimir.
6. **Os estilos mandam no resultado.** Há 7 estilos (Free Style, TRPG, Mini Pop, Anime 1:7, Classic Chibi, Classic Realism, Pixar Style), mais dezenas de templates. Cada estilo é um *workflow* de backend com prompt e parâmetros próprios.
7. **A edição é por chat.** "Edit" abre um chat de edição da imagem ("Make the cape bright red"). A edição leva ~35 s, mantém o personagem idêntico e guarda versões. "Done" refaz o 3D automaticamente.
8. **Preço por tamanho**, de 4 cm a 15 cm: de US$ 29,99 a US$ 449,99, com 15% de desconto quase permanente. O tamanho de 6 cm (US$ 69,99) vem pré-selecionado. Duo (2 personagens) custa o dobro.
9. **Monetização extra:** assinatura em 3 planos, Basic (grátis), Pro (US$ 19,90/mês) e Premium (US$ 99,90/mês), cobrada fora da Shopify, pela Airwallex (seção 13). Também há cupons, *buy more save more*, venda do arquivo 3D (GLB/OBJ/STL), cartão-presente e tamanho sob orçamento (até 30 cm).
10. **Prazo:** 8 a 12 dias úteis de produção (modelagem manual + impressão), mais 5 a 25 dias de envio desde a China ou Hong Kong. Não há reembolso por arrependimento.

---

## 1. Estrutura do site

| Menu | Conteúdo |
|---|---|
| **CREATE** | `/products/customize-your-own`: o criador (produto "JuJuBit Customized Figurine – Create Your Own") |
| **TEMPLATES** | Trending, New, TRPG, Chibi, Occasions, Other Products, More Services. São ~30 produtos-template (Pirate, Cyberpunk, Vampire, Pet, Big Head, Special Force…). |
| **CATEGORIES** | Figurines, Keychains, MagSafe Grips, Crystal Bracelets, Ring Holders, FDM Lamps, Keycaps, Photo Boards, **TRIPO x JUJUBIT** |
| **HOW IT WORKS** | Tracking, Contact, FAQs, Refund & Exchange, Blog |
| **ABOUT US** | Join Us, Wholesale, Campus Challenge |
| **INSPIRATION** | Galeria de criações com **Remix** |
| Topo | Log In, busca, conta, carrinho (gaveta lateral) e um botão laranja "✦ CREATE" |

O tom comercial é agressivo:
- Faixa de anúncios rotativa (Halloween até 65% off, frete grátis acima de US$ 99).
- Pop-up de e-mail com 15% off logo na entrada.
- Selos de 15% OFF em todas as imagens.
- Reviews da Judge.me (4,38★, ~1.500 avaliações).
- Bloco verde "Why choose us?" (privacidade, pagamento, garantia de entrega).

---

## 2. O criador (Create)

![Criador](prints/desktop/02-create-clean.jpg)

A página tem duas colunas. À esquerda fica uma galeria de imagens de marketing do estilo selecionado. À direita, o painel do criador, com abas **Create | Gallery**.

### 2.1 Controles

| Controle | Comportamento observado |
|---|---|
| **Estilo** (dropdown) | Free Style, TRPG, Mini Pop, Anime 1:7, Classic Chibi, Classic Realism, Pixar Style. Trocar o estilo troca a galeria da esquerda e, depois de gerar, o produto e o título exibidos (ex.: "Custom TRPG Miniature…"). |
| **Solo / Duo** | Alterna entre 1 e 2 personagens. O canvas continua o mesmo, com um único upload: o Duo só avisa o modelo de que são duas pessoas e trava o "Character" em 2 na compra, a preço dobrado. |
| **Basic / Pro** | Basic mostra o upload e o prompt. Pro acrescenta a barra de ferramentas **Album** (abre o seletor de arquivos), **Text** (abre o editor de prompt) e **Paint** (desenho à mão livre no canvas). O modo escolhido fica salvo depois de recarregar. |
| **Upload your picture** | Aceita PNG, WEBP e JPG. A foto aparece no canvas pontilhado, com uma lixeira para remover. |
| **Add Your Prompt** | Abre um modal com textarea, **limite de 200 caracteres**, contador e botões ✕ e ✓. |
| **Generate** | Fica desabilitado (laranja claro) até haver foto, texto ou desenho. |
| **Upgrade** | Faixa "More Generations & Better Quality", que abre o modal da assinatura PRO. |

![Estilos](prints/desktop/04-style-dropdown.jpg)
![Modo Pro](prints/desktop/08-pro-tools.jpg)
![Editor de prompt](prints/desktop/10-text-tool.jpg)
![Paint](prints/desktop/13b-paint-drawn.jpg)
![Foto enviada](prints/desktop/27-uploaded.jpg)

**O que fica salvo ao recarregar a página:** o modo Basic/Pro e o histórico de gerações. **O que se perde:** o estilo (volta para Free Style), o prompt e o canvas. Trocar entre as abas Create e Gallery sem recarregar mantém tudo.

### 2.2 Geração: o que o usuário vê

Ao clicar em **Generate**, o painel muda sozinho para a aba **Gallery**. À esquerda aparecem um toggle **2D | 3D** e uma barra de progresso com mensagens. À direita aparece o formulário de compra (tamanho, personagens, quantidade, carrinho).

![Gerando](prints/desktop/14-generate-anon.jpg)

Linha do tempo medida (de 157 a 175 s no total):

| Tempo | Mensagem | Observação |
|---|---|---|
| 0–15 s | "Preparing your image…" | |
| 15–33 s | "Analyzing your canvas…" | |
| ~33 s | "Generating your 2D image…" | **A imagem 2D aparece** e fica visível no lugar do 3D enquanto ele é construído |
| 35–50 s | "Preparing your 3D design…" | A barra volta a 0% |
| 50–65 s | "Building the 3D structure…" | |
| 65–88 s | "Refining the details…" | |
| 88–115 s | "Finalizing your 3D model…" | |
| 115–155 s | "Almost there – adding the final touches…" | A barra fica perto de 90–95% por ~40 s |
| ~157 s | "Loading 3D Model…" | Download do GLB (11–35 MB) |

![2D durante o 3D](prints/desktop/28-chibi-20.jpg)

**A barra de progresso é estimada**, não vem do servidor. O servidor só manda eventos de etapa: início, 2D pronto, 3D iniciado, pronto. O front anima a barra de forma suave e desacelera perto de 90%, o que disfarça a espera.

### 2.3 Resultado

![3D](prints/desktop/15-after-150s.jpg)
![2D](prints/desktop/16-2d-view.jpg)

- **Toggle 2D/3D:** o 2D é a "foto" da miniatura pintada, com fundo branco ou claro e vista 3/4. O 3D abre num `<model-viewer>` do Google:
  - gira sozinho (*auto-rotate*);
  - permite girar arrastando;
  - **não tem zoom**;
  - tem AR habilitado (webxr, scene-viewer, quick-look), que aparece só no celular;
  - usa *tone mapping* neutro e não tem sombra.
- **Botão Edit** no canto do visualizador, explicado na seção 2.4.
- **History (n):** miniaturas das gerações, com selo **NEW** na mais recente e lixeira em cada uma. Clicar numa miniatura carrega aquela versão.
- O título do produto à direita muda de acordo com o estilo.

![Rotação](prints/desktop/30b-dragged.jpg)
![Histórico](prints/desktop/23-history.jpg)

### 2.4 Edição por chat (Edit) e Remix

![Editor](prints/desktop/19-edit.jpg)

"Edit" abre o modal **Edit Image**:
- À esquerda, a imagem grande e a faixa de versões.
- À direita, um chat com o campo "Describe your idea…" (200 caracteres), o botão **+ Add reference images** e o botão enviar.

Teste feito: *"Make the cape bright red"*.
- Levou ~35 s ("Preparing your image…" → "Analyzing your canvas…"), com um botão **Cancel**.
- Resultado: a mesma figura, só com a capa vermelha. O chat mostra a mensagem do usuário, "Generate Successfully!" e a miniatura nova. A nova versão entra na faixa.
- **Done** fecha o editor e **regera o 3D automaticamente** (mais ~2 min). A geração editada entra no histórico.

![Edição em andamento](prints/desktop/21b-edit-progress.jpg)
![Edição pronta](prints/desktop/21c-edit-done.jpg)
![3D da edição](prints/desktop/22b-after-done-150s.jpg)

O **Remix**, na Inspiration, abre o mesmo editor, só que aplicado a uma peça da galeria, com o botão "Save".

### 2.5 Resultados dos testes de geração

| Entrada | Estilo / workflow | Resultado |
|---|---|---|
| Texto *"A dwarf warrior with a big red beard holding an axe"* + um círculo desenhado | TRPG | Miniatura de RPG excelente, com base cenográfica (grama, pedras). O desenho foi ignorado. 238 mil triângulos. |
| Foto de uma raposa de cerâmica | Classic Chibi (`chibi_new_duo`) | **Virou uma "garota-raposa" chibi**: o estilo pesa mais que a fidelidade à foto. Sem base. 298 mil triângulos. |
| Texto *"A grandmother and her grandson baking cookies together"* | Free Style + Duo (`TEST_creative_real`, `figureMode: dual`) | Cena completa com mesa, base de madeira e os dois personagens. |
| Texto *"A coffee mug shaped like a smiling cactus"* | Free Style (`TEST_creative_real`) | Objeto fiel, com fundo claro e vista 3/4. **1,17 milhão de triângulos, GLB de 35 MB.** |

![Duo](prints/desktop/36-duo-end.jpg)
![Objeto](prints/desktop/46-mug-end.jpg)

---

## 3. Compra

### 3.1 Formulário (aba Gallery)

- O selo "Limited Offer 15% OFF" aparece com o preço riscado.
- "Shipping calculated at checkout" e "*Free Pro Refinement: Based on Your 2D Image."
- **SIZE:** os nomes mudam por estilo. No TRPG: "6cm Standard Hero", "4cm Scout / Creature Mini" etc. No Free Style: "6cm Best Fit", "4cm Mini Collectible", "15cm Display Centerpiece" etc. **O de 6 cm vem pré-selecionado** e aparece primeiro, antes do de 4 cm.
- **CHARACTER:** 1 ou 2. O valor é travado conforme o Solo/Duo usado na geração.
- **QUANTITY**, **Add To Cart** (preto) e **Buy Now** (laranja, com o selo "15% OFF").
- "Member Benefits: 20% OFF" com o botão Upgrade.

### 3.2 Tabela de preços (variantes Shopify do Create Your Own)

| Tamanho | 1 personagem | 2 personagens |
|---|---|---|
| 4 cm | US$ 29,99 | US$ 59,99 |
| 5 cm | US$ 49,99 | US$ 99,99 |
| **6 cm (padrão)** | **US$ 69,99** | US$ 139,99 |
| 7 cm | US$ 99,99 | US$ 199,99 |
| 8 cm | US$ 129,99 | US$ 259,99 |
| 10 cm | US$ 169,99 | US$ 339,99 |
| 12 cm (só Free Style) | US$ 349,99 | US$ 700,00 |
| 15 cm (só Free Style) | US$ 449,99 | US$ 900,00 |
| Custom size (sob orçamento, até 30 cm) | US$ 300 de sinal | — |

Os estilos TRPG e Chibi oferecem só de 4 a 10 cm, pelos mesmos preços. O carrinho aplica **15% de desconto automático** (cupom `CREATE15%OFF`). Há ainda a promoção *Buy 1 → 15%, 2 → 35%, 3 → 50%, 4 → 65%*, que vale sobre o item mais barato.

### 3.3 Carrinho e checkout

![Carrinho](prints/desktop/31-cart-drawer.jpg)

- **Gaveta lateral** com:
  - barra "Add $73.50 more to enjoy Free Shipping" (meta de US$ 99);
  - miniatura da imagem 2D, tamanho, personagens, preço e economia;
  - "You Save" com um **contador regressivo** ("Ends in 0:10:03").
- **Propriedades ocultas do item no carrinho:**
  - `Generated Image` (URL do PNG 2D)
  - `_workflow`
  - `_figure_mode`
  - `_Record ID`
  - `_Created From: jjb_canvas_v2`
  - `_Generated_model`, que veio **vazio**: o pedido referencia a imagem 2D, não o 3D.
- **Checkout Shopify padrão:**
  - Express checkout, contato (e-mail) e endereço (entrega no Brasil, com estados).
  - Pagamento: cartão, PayPal e mais 11 métodos.
  - O resumo mostra "Generated Image: <url>" e o cupom aplicado.
  - Frete só aparece depois do endereço. Pela FAQ: US$ 12,99 nos EUA e grátis acima de US$ 99.

---

## 4. Contas, cotas e assinatura

- **Gerar não exige login.** O site cria um `anonymousId`, e a cota diária é `{"limit":40,"used":n,"remaining":…}`.
  - Edições e regerações aparentemente não contaram (6 gerações mais 1 edição deram `used: 3`).
  - Ao fazer login, o endpoint `/activity/tasks/merge` junta o histórico anônimo à conta.
- **Login:** Shopify Customer Accounts, com "Continue with Google" ou e-mail com código, sem senha. O que muda com login está na [seção 13](#13-com-login-conta-e-assinatura).
- **Assinatura:** o modal visto sem login só mostra o Pro. A página de planos (`/pages/vip-program`) mostra também o **Premium (US$ 99,90/mês)** e o plano anual (seção 13.2).
- **JuJuBit Membership PRO, US$ 19,90/mês** ("Pays for itself in 1 order"):
  - até US$ 220 em cupons (US$ 20 off sem mínimo, mais 2× 20% off até US$ 100);
  - 100 gerações por dia e 3 simultâneas;
  - geração mais rápida e de "maior qualidade";
  - *digital crafting* grátis e suporte prioritário.

![PRO](prints/desktop/33-upgrade.jpg)

---

## 5. Templates, Inspiration e outros produtos

- **Templates:** ~30 páginas de produto, cada uma com marketing próprio ("Mini Pop: your photo → real figurine", "Pirate Legend", "Cyberpunk"…), mas **o mesmo componente criador**, com o estilo pré-selecionado. Na prática, são landing pages de SEO e anúncio por nicho.
- **Inspiration:** grade de criações filtrável (For You, TTRPG, Pop, Anime). Cada item abre um modal com:
  - 2D/3D;
  - título e descrição;
  - preço com "Buy Now";
  - **✦ Remix**, que edita por chat a partir daquela peça.
- **TRIPO x JUJUBIT:** o cliente cola um **link de modelo da Tripo** e recebe a peça impressa (figura, chaveiro, keycap, ímã), de US$ 29,99 a US$ 170,99.
- **3D Model Services:**
  - download do arquivo (GLB/OBJ/STL) por US$ 7,99;
  - "Model Refinement" por US$ 15,99;
  - "Special Inquiry" por US$ 520.
- Também vende cartão-presente (US$ 50), miniaturas prontas de RPG (US$ 24,99), luminárias FDM, keycaps e pulseiras de cristal.

![Templates](prints/desktop/40-templates.jpg)
![Inspiration](prints/desktop/43-inspiration-item.jpg)
![Remix](prints/desktop/44-remix.jpg)

---

## 6. Políticas (FAQ, How it Works, Refund)

- **Produção:**
  - modelagem manual: 3–5 dias úteis;
  - impressão: 5–7 dias;
  - trânsito: 2–5 dias;
  - alfândega: 1–2 dias;
  - entrega: 2–5 dias.
- **Envio:** EUA em 5–12 dias úteis, internacional em 10–25, expresso em ~5–7 (pago, US$ 29,99). Despacho a partir da China ou de Hong Kong, e reviews reclamam da demora.
- **Material:** resina de alta qualidade, sempre **pintada**. Versão sem pintura só por pedido ao suporte.
- **Cancelamento:** até 4 horas após o pedido, se a produção ainda não começou. A FAQ se contradiz em outro trecho.
- **Reembolso:** não há por arrependimento. Item danificado, defeituoso ou errado é trocado se o problema for informado em até 7 dias, com fotos.
- **IA e direitos:**
  - *"Tripo AI generates design previews"*.
  - O cliente "é dono" do design, mas concede à Jujubit **direito perpétuo e gratuito** de usar, reproduzir e promover.
  - É exigido ter direito sobre a foto enviada.
- **Reviews** apontam a cor final às vezes diferente da prévia (jaleco branco que veio cinza) e reclamam de comunicação e prazo. Mas muitos dizem que a peça ficou "melhor que a prévia 3D", graças ao acabamento humano.

---

## 7. Arquitetura técnica (resumo)

> Os detalhes completos estão em **[jujubit-api.md](jujubit-api.md)**: cada endpoint com payloads reais de entrada e saída, o stream SSE da geração, o schema protobuf e a sequência decodificada do chat de edição, os códigos de erro e onde cada limite é aplicado.

| Peça | Detalhe |
|---|---|
| Loja | Shopify (tema próprio), checkout Shopify, Judge.me, Klaviyo, Google Ads/GA4, pixel da OpenAI |
| Criador | App em JavaScript (`jjb-create-canvas.js`, ~600 KB) embutido na página de produto, com **feature flags e testes A/B** |
| Upload | `POST /apps/ai/activity/uploads/presign` gera uma URL S3 pré-assinada (válida por 5 min), seguida de `PUT` direto no S3 (`jujubit-shop-creation`, us-west-1). **Mesmo só com texto, o canvas é enviado** como imagem (JPG). |
| Cota | `GET /apps/ai/membership/quota?anonymousId=…` (logado: por conta, sem parâmetro) |
| Assinatura (logado) | `GET /membership/me`, `/coupons`, `/billing`, `GET/PATCH /membership/profile`, `POST /membership/checkouts` → página hospedada da **Airwallex** (seção 13; detalhes em [jujubit-api.md §13](jujubit-api.md#13-conta-e-assinatura-com-login)) |
| Geração | `POST /apps/ai/activity/tasks`, que responde em **streaming SSE** até o fim. Eventos: `task_start`, `asset_start {workflow, figureMode}`, `asset_2d_done {imageUrl}`, `asset_3d_start`, `asset_done {imageUrl, modelUrl}`, `task_done`, `task_limit`, mais `ping` de keep-alive. |
| Histórico | `GET /activity/tasks?activityType=canvas&pageSize=10&cursor=…`, `GET /activity/tasks/{id}`, `DELETE /activity/assets/{id}`, `POST /activity/assets/{id}/retry`, `POST /activity/tasks/merge`, `POST /activity/tasks/import-preset` (Remix) |
| Edição | Agente conversacional em `csa.jujubit.ai/chat/v1/chat.WebChatService/{Send,Stream}`, via **gRPC-web + protobuf** (gateway Kong), autenticado por um JWT do **Supabase** obtido em `POST /apps/ai/auth/chat-token`. Cada edição gera uma imagem nova, **um 3D novo** e **3 sugestões** de próxima edição. |
| Imagem 2D | PNG 1024×1024, em `appcdn.jujubit.ai/llm/image/…` ou `…/agent-runtime/artifacts/…` (um pipeline de "agente" no Free Style). Há um teste A/B `creative_use_gpt-image-2`, que sugere o **GPT Image 2** no Free Style. |
| 3D | **Tripo**, com GLB em `appcdn.jujubit.ai/llm/model/<hash>.glb` (CloudFront + S3). Materiais PBR (cor, metal/rugosidade, normal; 3 texturas 2048²). Teste A/B `tripo_face_limit_v2` para os estilos estilizados. Workflows "realistas" usam `faceLimit = 1.200.000`. |
| Workflows (amostra) | `chibi`, `chibi_new`, `chibi_new_duo`, `scale_1_7`, `board_game`, `TEST_creative_real`, `special_force2`, `ninja`, `piratecore`, `Big_Head_Portrait`, `voxel`, `low_poly`, `Ghibli`, `Dark_Gothic1`, `semi_realistic_pet_figurine`, `dnd_aetherra_world_*`… |
| Flags A/B vistas | `edit_generation`, `soft_material_preview`, `model_studio_preview`, `checkout_img_preview`, `generating_leave_confirm`, `hide_freestyle_small_sizes`, `split_image_with_prompt`, `membership_paywall_visual`, `canvas_trust_info`, `discount_badge_removal`, `inspiration_page`, `independent_site_free_generation_limit` (40 ou 25) |

---

## 8. Mobile

Sessão de 02/11/2026, em Chrome com emulação de celular: 390×844, toque e identificação de iPhone. **Não é um aparelho real**, então o tempo e o AR não valem como medida. Os prints estão em [prints/mobile/](prints/mobile/).

Não refiz as telas que dependem de limite (6 simultâneas e cota diária), a pedido do Jeferson, nem as montagens de categorias.

**Resumo:** é o mesmo componente empilhado em uma coluna, sem recurso exclusivo. O fluxo inteiro funciona no celular, inclusive Paint com o dedo, edição por chat e checkout.

| Ponto | Mobile |
|---|---|
| **Entrada** | O pop-up de 15% off ocupa a maior parte da primeira tela |
| **Cabeçalho** | Logo, Log In (ou o selo Upgrade, com login), carrinho, menu e o botão laranja CREATE |
| **Menu** | Tela cheia: Create, Templates, Categories, Contact Us, About Us, Inspiration e Account |
| **Criador** | Na maioria das aberturas, a página já vem rolada até o criador, com a galeria de marketing acima da tela |
| **Ferramentas** | No modo Pro, Album, Text, Paint e Generate ficam na mesma linha. O Paint aceita desenho com o dedo. |
| **Prompt** | O editor abre sobre a tela, com contador de 200 caracteres e botões ✕ e ✓ |
| **Geração** | A tela passa sozinha para a aba Gallery. Na única medição, o 3D ficou pronto em 127 s, um pouco abaixo dos 157 a 175 s do desktop. |
| **Compra** | **Add To Cart** e **Buy Now** ficam fixos na parte de baixo da tela, com a faixa "Member Benefits: 20% OFF" e o botão Upgrade. Durante a geração, os dois ficam desabilitados. |
| **Histórico** | Linha horizontal com rolagem, logo abaixo do visualizador |
| **Editor** | Tela cheia e fundo preto. A imagem fica no centro, as versões logo abaixo, e o chat numa gaveta que sobe de baixo. |
| **Carrinho** | Gaveta de largura quase total, com a barra de frete grátis e o contador regressivo |
| **Checkout** | Shopify responsivo, com PayPal e Google Pay no topo. O e-mail abre vazio. |
| **Inspiration** | O item abre numa gaveta, com "Buy Now" e **Remix** |
| **Assinatura** | Sem login, o Upgrade abre uma gaveta com o Pro. Com login, leva à página de planos. |
| **Airwallex** | Uma coluna, com e-mail e nome já preenchidos, e cartão, Google Pay e Apple Pay |

**Problemas de UX que vi:**
- **O botão do chat de suporte fica sobre o conteúdo.** Hoje ele cobre o início da faixa de Upgrade no criador e o título do produto na tela de compra. Em 31/10, cobria o campo de prompt (print abaixo). Nessa posição ele não deixa o site inutilizável, mas está sempre no caminho.
- **O título e o preço do produto ficam abaixo do histórico.** Na primeira tela do resultado, o cliente vê o 3D e os botões de compra, mas ainda não vê o preço.
- **Texto em chinês na interface:** os botões de carrinho da Inspiration têm o rótulo de acessibilidade 加入购物车 ("adicionar ao carrinho"). Não aparece na tela, mas é o que um leitor de tela leria.

**AR:** a emulação não mostrou botão de AR (`canActivateAR: false`). Como isso depende do aparelho, continua sem confirmação.

**Do início ao resultado**

<img src="prints/mobile/00-popup-15off.jpg" width="190" alt="Pop-up de 15% off"> <img src="prints/mobile/01-home.jpg" width="190" alt="Home"> <img src="prints/mobile/03-menu.jpg" width="190" alt="Menu"> <img src="prints/mobile/02-create-clean.jpg" width="190" alt="Criador">

<img src="prints/mobile/04-style-dropdown.jpg" width="190" alt="Estilos"> <img src="prints/mobile/08-pro-tools.jpg" width="190" alt="Modo Pro"> <img src="prints/mobile/10-text-tool.jpg" width="190" alt="Editor de prompt"> <img src="prints/mobile/13b-paint-drawn.jpg" width="190" alt="Paint">

<img src="prints/mobile/27-uploaded.jpg" width="190" alt="Foto enviada"> <img src="prints/mobile/14-generate-anon.jpg" width="190" alt="Gerando"> <img src="prints/mobile/28-chibi-20.jpg" width="190" alt="2D durante o 3D"> <img src="prints/mobile/15-after-150s.jpg" width="190" alt="3D">

<img src="prints/mobile/30b-dragged.jpg" width="190" alt="Rotação"> <img src="prints/mobile/16-2d-view.jpg" width="190" alt="2D"> <img src="prints/mobile/23-history.jpg" width="190" alt="Histórico">

A tela de resultado inteira está em [15b-resultado-inteira.jpg](prints/mobile/15b-resultado-inteira.jpg).

**Edição por chat**

<img src="prints/mobile/19-edit.jpg" width="190" alt="Editor"> <img src="prints/mobile/21b-edit-progress.jpg" width="190" alt="Edição em andamento"> <img src="prints/mobile/21c-edit-done.jpg" width="190" alt="Edição pronta"> <img src="prints/mobile/21d-edit-chat.jpg" width="190" alt="Chat aberto">

<img src="prints/mobile/22b-after-done-150s.jpg" width="190" alt="3D da edição">

O "Done" mostrou o 3D em ~7 s porque ele já estava pronto, o que confirma a geração em segundo plano descrita na seção 11.

**Outros casos e compra**

<img src="prints/mobile/35-duo-controle.jpg" width="190" alt="Controle Duo"> <img src="prints/mobile/36-duo-end.jpg" width="190" alt="Duo"> <img src="prints/mobile/46-mug-end.jpg" width="190" alt="Objeto"> <img src="prints/mobile/82-policy-rejected.jpg" width="190" alt="Recusa por política">

<img src="prints/mobile/31-cart-drawer.jpg" width="190" alt="Carrinho"> <img src="prints/mobile/32-checkout.jpg" width="190" alt="Checkout"> <img src="prints/mobile/33-upgrade.jpg" width="190" alt="Upgrade"> <img src="prints/mobile/34-login.jpg" width="190" alt="Login">

**Templates, Inspiration e Remix**

<img src="prints/mobile/40-templates.jpg" width="190" alt="Templates"> <img src="prints/mobile/42-inspiration.jpg" width="190" alt="Inspiration"> <img src="prints/mobile/43-inspiration-item.jpg" width="190" alt="Item da Inspiration"> <img src="prints/mobile/44-remix.jpg" width="190" alt="Remix">

**Com login**

<img src="prints/mobile/104-home-logado.jpg" width="190" alt="Home com login"> <img src="prints/mobile/105-menu-logado.jpg" width="190" alt="Menu com login"> <img src="prints/mobile/106-criador-logado.jpg" width="190" alt="Criador com login"> <img src="prints/mobile/100-vip-plans.jpg" width="190" alt="Planos">

<img src="prints/mobile/101-vip-membership.jpg" width="190" alt="Painel do membro"> <img src="prints/mobile/102-airwallex-checkout.jpg" width="190" alt="Checkout da assinatura">

**Print da primeira sessão (31/10/2026)**

<img src="prints/mobile/51-mobile-creator.jpg" width="190" alt="Criador em 31/10, com o chat sobre o prompt">

**O que isso sugere para o Kubo:**
- **Reservar espaço para botões flutuantes.** O chat da Jujubit está sempre cobrindo alguma coisa.
- **Botões de compra fixos no rodapé funcionam bem**, mas o preço precisa aparecer junto deles.
- **Chat em gaveta é um bom modelo para a edição no celular:** a imagem fica grande, e o histórico só aparece quando o usuário pede.

---

## 9. Pontos fortes e fracos (UX)

**Fortes**
- **Zero atrito para começar:** gera sem login, com uma cota generosa.
- **Um único botão faz tudo** (2D e 3D), e a imagem 2D aparece cedo (~35 s), o que alivia a espera do 3D.
- **A edição por chat preserva a identidade** e regera o 3D sozinha. É exatamente o "ajuste" que o Kubo quer.
- Estilos e templates garantem um resultado "imprimível e bonito" (bases, poses, proporções de miniatura) e alimentam o marketing por nicho.
- Histórico com versões, Remix a partir da galeria e AR no celular.
- O pedido usa **a imagem 2D como contrato**, e um humano refina o 3D. Isso reduz a pressão sobre a qualidade da prévia automática.

**Fracos**
- Barra de progresso falsa, que fica parada em 90–95% por ~40 s.
- Sem zoom no 3D, e GLBs pesados (até 35 MB) para uma prévia.
- O estilo distorce a foto (a raposa virou uma menina-raposa), sem aviso.
- O desenho no canvas foi ignorado quando havia texto.
- Ao recarregar, perde estilo, prompt e canvas.
- Muitos pop-ups, selos e contadores de urgência.
- O tamanho de 6 cm vem pré-selecionado em vez do mais barato (escolha "nudge").
- Prazo longo e envio internacional demorado. Políticas contraditórias sobre cancelamento.

---

## 10. O que isso sugere para o Kubo

1. **Fluxo de 1 clique, com o 2D primeiro.** O Jujubit nem pede aprovação da imagem: mostra o 2D cedo e segue para o 3D. Vale testar no protótipo uma opção "gerar imagem + 3D direto", mantendo o ajuste depois.
2. **Edição por chat em vez de regerar.** Editar a imagem atual ("muda a cor da capa") preserva o objeto. Isso é melhor do que o "Gerar com o ajuste" atual do protótipo, que cria uma imagem nova do zero. Modelos de edição de imagem na Runware (FLUX Kontext/edit, Seedream, Nano Banana etc.) permitiriam isso.
3. **A imagem 2D como contrato** e acabamento humano/automático depois da compra. Bate com o plano do Kubo (prévia barata, Tripo depois), e o Jujubit prova que dá para vender assim.
4. **O Jujubit usa a Tripo já na prévia** (não o Trellis), com malhas de até 1,2 milhão de faces, e investe no 2D por estilo. A qualidade percebida vem muito do **2D estilizado com base de miniatura**.
5. **Templates e estilos como produto:** cada estilo é um prompt e um parâmetro de backend, mais uma landing page. É um caminho barato de crescimento.
6. **Detalhes que valem copiar:**
   - histórico com versões e lixeira;
   - toggle 2D/3D;
   - mensagens de etapa durante a espera;
   - cota anônima, com o histórico unido ao fazer login;
   - variantes de tamanho com preço claro.
7. **Detalhes a evitar:** progresso falso parado em 90%, prévia sem zoom, estilo distorcendo a foto sem avisar, e excesso de urgência e pop-ups.
8. **Limites e custo (seções 11 e 12):**
   - Reservar a cota no início e só debitar no sucesso é um bom padrão.
   - A Jujubit deixa as edições livres, e cada uma ainda gera um 3D. No Kubo, edição e 3D deveriam ter uma cota (ou um custo) próprios.
   - Verificar a textura do GLB, ou ter um fallback, para não entregar modelos cinzas.
   - Mostrar mensagens amigáveis em recusas de política, em vez do erro técnico cru.

---

## 11. Limites de geração (teste de estresse)

Fiz 42 gerações em lotes de 4 a 7 enviados de uma vez, até a cota acabar. Depois fiz 15 edições seguidas, com a cota já zerada.

| Limite | Como funciona na prática |
|---|---|
| **6 simultâneas** | Controlado só pelo front. Com 6 tarefas "gerando", o botão **Generate** vira **"Generating…"** desabilitado, e o 7º envio simplesmente não acontece. Não aparece aviso. Num lote, isso aconteceu já no 5º, porque registros antigos ainda contavam como "gerando". |
| **40 por dia** | A cota é `{limit, used, frozen, remaining}`. Uma tarefa em andamento fica **reservada** (`frozen`) e só vira `used` se der certo. **Falhas não descontam** (o Pikachu recusado não contou). |
| **Ao estourar** | Com 2 restantes, mandei 3: o 3º foi aceito pela interface e **recusado pelo servidor em ~1 s** (erro `1028`). O card mostra *"Today's limit reached. Upgrade to Pro for 100 daily generations."* com um botão **Upgrade**. Com a cota zerada, o botão Generate **continua habilitado**: cada clique cria uma tarefa que falha na hora. |
| **Edições** | **Não consomem a cota e continuam funcionando depois de ela acabar.** Fiz 15 sem bloqueio. Cada edição leva ~40 s e **ainda gera um 3D novo em segundo plano**, ou seja, também custa Tripo para a Jujubit. É a brecha mais visível do modelo. |
| **Retry** | Em falhas por cota, o botão vira "Upgrade". Em falhas por política, a tela mostra o erro técnico cru e um "Retry". |
| **Excluir histórico** | Lixeira em cada item, com um `confirm()` nativo: *"Delete this history record?"*. |

![6 em andamento: botão Generating… desabilitado](prints/desktop/80-limit-concurrent-generating.jpg)
![Limite diário atingido](prints/desktop/81-limit-daily-reached.jpg)
![Recusa por política, com mensagem crua](prints/desktop/82-policy-rejected.jpg)

**Atualização de 02/11/2026:** a recusa do Pikachu mudou. Sem mostrar o erro técnico, a tela diz *"We couldn't generate from this image. Please try a different one"*, com o botão **try another image**. A API agora responde `errorCode: 1001`, com o mesmo texto `image_policy_rejected`. Vi isso uma vez, no layout de celular, então não sei se o desktop mudou também.

**O editor é um agente, não um simples "img2img".** Quando a instrução é ambígua, ele pergunta em vez de gerar. Mandei sem querer 5 cores numa frase e ele respondeu *"I see five colors in your message… Which one should I use for the camera's main body color?"*. Depois de cada edição, o servidor também manda 3 sugestões de próxima edição (ex.: *"Make the camera's silver metal finish matte…"*), que não vi aparecerem na interface.

![Agente pedindo esclarecimento](prints/desktop/83-edit-agent-question.jpg)

**Em 02/11/2026, o agente não repetiu a pergunta.** A instrução *"Change the jacket color to red, blue, green, yellow, purple"* gerou direto uma jaqueta com uma cor em cada parte. Ou seja, a pergunta não é garantida, e por isso esse print não tem versão mobile.

---

## 12. Comportamento por categoria (40 gerações)

Todas com o mesmo fluxo (texto, sem foto). As folhas abaixo mostram, para cada uma, a **imagem 2D gerada | o 3D renderizado do GLB**, com o workflow, o número de faces e o tamanho.

![Categorias 1](prints/desktop/90-categorias-1.jpg)
![Categorias 2](prints/desktop/90-categorias-2.jpg)
![Categorias 3](prints/desktop/90-categorias-3.jpg)
![Categorias 4](prints/desktop/90-categorias-4.jpg)

| Categoria | Testes | Resultado |
|---|---|---|
| **Objetos sólidos simples** | caneca-cacto, cupcake, hambúrguer, vaso geométrico, peça de xadrez, cacto no vaso, bola em troféu, chave, tênis | **Excelente.** O 3D é praticamente a imagem. É o ponto forte. |
| **Animais e bichos fofos** | gato dormindo, coruja, ursinho, capivara de chapéu (**prompt em português, entendido**), preguiça porta-celular | Muito bom. Formas orgânicas fechadas funcionam. |
| **Veículos e máquinas** | carro conversível 1950, trem de madeira, câmera vintage, veleiro | Bom. Detalhes finos (frisos, lentes, cordas do barco) ficam "derretidos". |
| **Estruturas finas / vazadas** | bicicleta, Torre Eiffel | O **2D já adiciona uma base/suporte** (a bicicleta vem num pedestal) para viabilizar o 3D. Os raios e a treliça viram superfícies grossas ou somem. |
| **Arquitetura / cenas** | castelo na rocha, farol, diorama de cafeteria | O castelo e o farol ficam bons. O **diorama perde quase todo o interior**: sobram as paredes do fundo, uma mesa e um vaso. |
| **Texto** | "KUBO" em letras 3D, caneca "Bom dia" | As letras grandes saem bem. **Texto pequeno na superfície se degrada** (o "Bom dia" sai cortado no 3D). |
| **Joias / detalhe fino** | anel de prata com pedra | Bom no geral, e a filigrana vira relevo raso. |
| **Pessoas e personagens (Free Style)** | astronauta, avó e neto (Duo) | A forma é boa. **O astronauta veio sem cor**: a textura saiu cinza uniforme. |
| **Estilos de personagem** | TRPG (anão, arqueira élfica), Mini Pop (médico), Pixar (pescador), Anime 1:7 (magical girl), Chibi (foto da raposa) | Personagens muito bons, com proporções "de colecionável" e base de miniatura no TRPG. **A magical girl também veio sem cor.** |
| **Anatomia / técnico** | coração anatômico | Bom. |
| **Propriedade intelectual** | Pikachu, Mickey Mouse | **Pikachu: bloqueado** (`1007 image_policy_rejected`), sem consumir cota. **Mickey: não bloqueado, mas "desviado"**: a IA de imagem gerou uma placa preta com "Mickey Mouse / Micked Mouse" escrito, e o 3D virou duas plaquinhas. Uma falha silenciosa. |
| **Armas** | "A pistol" | Não bloqueado. A IA gerou uma **pistola de brinquedo com ponta laranja** (higienização no prompt). |

**Números**
- **40 sucessos, 1 bloqueio por política, 2 bloqueios por cota.**
- Tempo da criação ao GLB pronto: **110–216 s** (mediana ~150 s), com até 6 em paralelo.
- **2 de 40 (5%) vieram sem textura**: a cor base é um cinza uniforme, embora o GLB tenha as 3 texturas. O usuário recebe um 3D sem cor, sem nenhum aviso.
- O Free Style usa sempre `faceLimit 1.200.000` (GLB de 33–39 MB). Os estilos ficam em ~290 mil faces (10–12 MB).
- Todos os modelos vêm normalizados (maior eixo = 1,0) e são uma malha única.

---

## 13. Com login: conta e assinatura

Segunda sessão, em 31/10/2026, com a conta Google do Jeferson no plano grátis (Basic). Comparei com tudo o que foi visto sem login.

**Resumo:** o **criador é idêntico** com e sem login: as mesmas ferramentas, os mesmos estilos e nenhum download de GLB. O login acrescenta três coisas:
- **cota amarrada à conta**, controlada pelo servidor;
- uma **página de assinatura com painel do membro**;
- a **cobrança da assinatura por fora da Shopify**, pela Airwallex.

Não existe área de "minhas criações". As criações continuam só na aba Gallery do criador.

### 13.1 O que muda ao fazer login

| Item | Sem login | Com login |
|---|---|---|
| **Identidade** | `anonymousId`, gerado e guardado pelo navegador | `customerId` da Shopify mais o `anonymousId`. O servidor **ignora o `anonymousId` enviado** e usa o cliente autenticado pela Shopify. |
| **Cota diária** | 40 por `anonymousId`. Basta trocar de navegador para ter outra cota. | 40 **por conta** no Basic, com 100 no Pro e 200 no Premium. A cota volta a zero às **13h (horário de Brasília)**, que é meia-noite no fuso da loja (UTC+8, China). |
| **Histórico** | Por navegador | A cada abertura do criador, `merge` junta o histórico anônimo **daquele navegador** à conta. As 42 gerações feitas sem login no Chrome de teste **não** apareceram na conta, porque o merge só leva o `anonymousId` do navegador atual. |
| **Botão Upgrade no criador** | Abre um modal com o Pro | Pelo teste A/B `membership_entry_redirect`, leva à página cheia `/pages/vip-program?tab=plans&entry_page=generate_create`, com os 3 planos. |
| **Cabeçalho** | Ícone de conta leva ao login | Selo "Upgrade" (classe `--basic`) e ícone de conta, que leva à conta Shopify |
| **Chat de edição** | Token pedido com o `anonymousId` | Token pedido com o `customerId` |
| **Inspiration** | Remix e Buy Now | Igual: não há curtir, publicar nem coleção. |

**Conta Shopify** (`shopify.com/{loja}/account`): é a página padrão da Shopify, com duas abas:
- **Orders:** sem pedidos, e com uma vitrine de produtos;
- **Profile:** nome, e-mail, endereços, "Sign out" e "Sign out of all devices".

Nada ali é personalizado para o produto 3D.

### 13.2 Página de assinatura: `/pages/vip-program`

Tem duas abas: **PLANS** e **MEMBERSHIP**. A aba de planos também abre sem login. A de membro mostra os dados da conta.

![Planos](prints/desktop/100-vip-plans.jpg)

| | **Basic** | **Pro** (Most Popular) | **Premium** |
|---|---|---|---|
| Mensal | Grátis | US$ 19,90 | US$ 99,90 |
| Anual | — | US$ 191,04 no 1º ano (−20%), depois US$ 238,80 | US$ 959,04 no 1º ano, depois US$ 1.198,80 |
| Gerações por dia | 40 ("Limited time") | 100 | 200 |
| Simultâneas | "Up to 3" | "Up to 3" | "Up to 3" |
| Desconto por pedido | — | US$ 20 em 1 pedido por mês | US$ 50 em 1 pedido por mês |
| Cupons de 20% (teto de US$ 100 cada) | — | 2 por mês | 4 por mês |
| Desconto geral | 10% ou mais ("Limited time") | 10% ou mais | 10% ou mais |
| Outros | *Free digital crafting* ("Limited time") e velocidade normal | Geração mais rápida, "maior qualidade" e suporte prioritário | Igual ao Pro |
| "Coming soon" | — | Cupons de frete grátis e templates exclusivos | Os mesmos, mais presente de aniversário |

Observações:
- **A página diz "até 3 gerações simultâneas" para todos os planos**, mas sem login o front deixou rodar **6** (seção 11). O limite de simultâneas não é aplicado no servidor.
- **Vários benefícios do Basic têm o selo "Limited time"**, inclusive as 40 gerações por dia. Isso prepara o terreno para reduzir o plano grátis (lembrando o teste A/B com 25).

**Aba MEMBERSHIP: o painel do membro**

![Painel do membro](prints/desktop/101-vip-membership.jpg)

- **Nome e e-mail.** O nome pode ser editado num pop-up; o e-mail não ("used for sign-in and order updates").
- **Cartão do plano:** "Basic — Members save $20+", com o botão **Upgrade**.
- **Orders:** link para os pedidos na Shopify.
- **Cupons:** cupons disponíveis e expirados.
- **Daily generations:** barra "Used: 1 / 40" e "Resets daily at 1:00 PM".
- **Billing history:** histórico de cobranças. É ali que se desliga a renovação automática.

### 13.3 Assinar: checkout da Airwallex

"Get Pro" cria uma sessão de cobrança no backend e redireciona para a **página hospedada da Airwallex** (`checkout.airwallex.com`). Essa página é separada do checkout Shopify, que só é usado para os pedidos.

![Checkout da assinatura](prints/desktop/102-airwallex-checkout.jpg)

- **Resumo:** "Inscrever-se para JuJuBit Pro Membership", **US$ 19,90 hoje**, "cobrado mensal, antecipadamente", com o próximo pagamento em 30/11.
- **Dados:** o e-mail e o nome já vêm preenchidos da conta. O endereço é pedido para calcular o imposto.
- **Pagamento:** cartão (Visa, Mastercard, UnionPay), Google Pay ou Apple Pay. A página fica em português.
- **Depois de pagar**, o usuário volta para `/pages/checkout-succeed`. A página mostra "Confirming your payment…" e consulta o status da sessão até a confirmação.
- **Parei antes de pagar.** A sessão aberta expira sozinha em ~1 h, sem cobrança.

### 13.4 Regras da assinatura (FAQ da página)

- **Cupons:** só um cupom de membro por pedido. Ele não soma com outros códigos nem com descontos automáticos, e os cupons não usados expiram na renovação mensal.
- **Anual:** 20% de desconto só no 1º ano e uma vez por conta. Os benefícios mensais (cupons e descontos) renovam todo mês, mesmo no plano anual.
- **Cancelamento:** basta desligar a renovação automática. Os benefícios continuam até o fim do período pago, e não há reembolso do período corrente.
- **Upgrade:** é proporcional. O valor não usado vira crédito, o ciclo recomeça na data do upgrade e o desconto do 1º ano não vale.
- **Downgrade:** não existe downgrade, nem troca de anual para mensal.
- **Falha no pagamento:** a cobrança é tentada de novo. O membro mantém o que já pagou, mas não recebe benefícios novos enquanto estiver em atraso, e volta ao Basic quando o período pago acaba.

### 13.5 O que isso sugere para o Kubo

- **A cota precisa estar amarrada à conta no servidor.** A cota anônima da Jujubit é contornável: basta trocar de navegador. A cota por conta é a que de fato vale.
- **Assinatura e pedidos podem ter cobranças separadas.** A Jujubit cobra a assinatura recorrente pela Airwallex e deixa o carrinho e o pedido no checkout normal da loja.
- **Um painel único do membro** com plano, uso diário, cupons e histórico de cobrança é simples e fácil de entender.
- **A escada de planos é por volume de geração** (40, 100, 200 por dia) mais descontos em pedidos. A assinatura funciona como um programa de fidelidade de quem compra, não só como acesso à IA.

---

### Como este estudo foi feito / limites

- Um Chrome separado (perfil temporário), controlado com puppeteer; prints e rede capturados por script.
- O tráfego gRPC-web foi capturado com um *hook* de `fetch` e decodificado com o schema protobuf do próprio bundle.
- Na primeira sessão não fiz login. Na segunda, o Jeferson fez login numa janela de teste do Edge, também controlada por script, e eu explorei a área logada (seção 13).
- A terceira sessão (02/11/2026) refez as telas em emulação de celular, com um perfil temporário novo: 4 gerações e 2 edições sem login. A parte logada usou outro perfil, para o histórico de teste não ser juntado à conta, e sem captura de rede. Não houve pagamento: o checkout da loja e o da assinatura foram só abertos, sem nada digitado.
  - Não fiz nenhum pagamento: abri o checkout da assinatura só para ver a página.
  - Não vi frete real nem um pedido de verdade.
  - Nos prints da área logada, o nome e o e-mail foram ocultados, inclusive nos de celular.
- Todas as gerações (42) e edições (15) usaram a cota gratuita anônima de um único `anonymousId`. Nada foi comprado; o carrinho anônimo ficou com 2 itens.
- Durante o teste de exclusão apaguei, sem querer, um item de edição de teste do histórico.
- Os nomes de modelos de IA vêm de evidência indireta:
  - **Tripo:** confirmado pelo metadado `generator` dos GLB e pela FAQ.
  - **GPT Image 2:** só pelo nome de um teste A/B no código.
