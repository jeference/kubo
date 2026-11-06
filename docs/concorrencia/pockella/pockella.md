# Pockella (pockella.com): mapeamento completo

> Estudo de um concorrente direto do Kubo, feito em 05/11/2026 usando o site de verdade: um Chrome controlado por script no PC do Jeferson, em português e com preços do Brasil.
>
> **Sem login (navegador 1, desktop):**
> - **11 fotos enviadas:** 9 viraram designs (36 imagens) e 2 foram recusadas pelo classificador, até **estourar o limite diário**;
> - os **7 produtos**, inclusive 2 que o menu não mostra;
> - **2 modelos 3D** (figura chibi e bobblehead) e o arquivo de prévia do bobblehead;
> - o carrinho e o checkout, com frete para Brasil e EUA (parei antes de pagar);
> - o FAQ, os termos, a privacidade e o login.
>
> **Com login e no celular (navegador 2):**
> - 1 design como convidado novo e, depois do login do Jeferson com Google, **9 designs e 1 recusa** na conta, todos em emulação de iPhone, até o limite;
> - 1 bobblehead em 3D, a compra, o carrinho, o checkout e o frete no mobile, e a saída da conta ([seção 11](#11-com-login-conta-cota-e-pedidos)).
>
> Também capturei o tráfego da API e li o JavaScript do site.
>
> - Os prints estão em [prints/desktop/](prints/desktop/) e [prints/mobile/](prints/mobile/).
> - A **referência técnica** (endpoints, payloads, códigos de erro) está em [pockella-api.md](pockella-api.md).
> - O que **não** testei está na [última seção](#como-este-estudo-foi-feito--limites).

## Resumo em 10 pontos

1. **O que é:** a nova loja de consumidor da Meshy, que substitui o [Meshy Shop](../meshy-shop/meshy-shop.md). O site diz isso no FAQ ("a loja própria da Meshy [...] administrada pela MESHY LLC"), e a página de pedidos avisa que pedidos feitos na meshy.ai antes de **12/10/2026** ficaram lá. A loja Shopify é a mesma (mesmos IDs de variante), mas o site, a API, o login e o pipeline de geração são novos.
2. **Fluxo central:** foto → **classificador** (~4 s) → **4 designs 2D** (~15 s) → cliente escolhe um → tamanho → checkout. Na figura chibi **não há prévia 3D**: o cliente compra vendo só a imagem 2D, e o 3D é gerado em segundo plano "para a oficina". Só o bobblehead mantém "Faça este em 3D — você vai ver antes de comprar".
3. **O 2D saiu da Meshy e foi para o fal.ai.** As imagens da figura chibi, do bobblehead e do ímã vêm de `v3b.fal.media`, com pipelines próprios (`chibi-figure-v2`, `realistic-big-head-figure-v24`). O chaveiro e o quadro em relevo ainda usam imagens de `assets.meshy.ai`. O 3D não aparece no navegador para a figura, e a política de privacidade fala em "3D model files generated through the Meshy platform".
4. **O classificador agora vem antes de gastar.** Torre Eiffel e Beatles foram recusados em 4 s, antes de qualquer imagem, com mensagens claras e, para grupos, a sugestão "Recorte e nós fazemos". Um cachorro enviado na página de pessoa virou "pet" já no início, com o preço certo. Era a principal falha do Meshy Shop. Ele ainda erra: **uma pelúcia passou como pet**.
5. **Catálogo maior:** figura chibi em 4 combinações (pessoa, pet, duas pessoas, **pessoa + pet**), **bobblehead**, chaveiro de pet e, fora do menu, **ímã de geladeira** e **quadro em relevo 3D**.
6. **Preço:** figura de pessoa de **R$ 190** (6 cm) a R$ 858 (12 cm), pet de R$ 229 a R$ 808, duas pessoas R$ 273–496, pessoa + pet R$ 218–885, bobblehead R$ 218–885, chaveiro R$ 218, ímã R$ 223–279, quadro R$ 334–362. São ~1% acima do Meshy Shop. Frete de **R$ 26** para o Brasil e US$ 5 para os EUA, como antes.
7. **Desconto em dobro na vitrine:** a figura de pessoa aparece com R$ 218 riscado e R$ 190, ao lado de "Cerca de R$ 28 de desconto no seu primeiro pedido". No checkout, o cupom **WELCOME5** (US$ 5 fixos, R$ 27,86) sai **de novo** dos R$ 190. Uma figura de 6 cm entregue no Brasil fica em **R$ 188,14**.
8. **Sem login, com limite:** o convidado gera cerca de 9 a 10 designs por dia, somando todos os produtos, e depois recebe `429 allowance_exhausted`. A cota segue o navegador (cookie `pk_guest`, de 1 ano), não o IP. Com login, a loja quase não muda: o limite é parecido, os designs do convidado passam para a conta, e o checkout já vem com o e-mail.
9. **A prévia 3D do bobblehead é um GLB aberto** (`model-web.glb`, 2,8 MB, 416 mil triângulos, textura WebP 2048², compressão meshopt), e não mais o `.meshy` cifrado do Meshy Shop.
10. **Para o Kubo:** a Meshy agora opera uma marca de consumidor completa, em 25 idiomas e com preços em reais, e resolveu sozinha várias falhas que o estudo anterior apontou. O fluxo "comprar só com o 2D" é a decisão mais diferente da do Kubo e merece discussão (seção 10). Os termos da Pockella **proíbem "competitive analysis"** (s. 2.4 iv), o que vale registrar.

---

## 1. Estrutura do site

| Menu | Conteúdo |
|---|---|
| **Todos** | Produtos (Figura chibi — Pessoas, Figura chibi — Duas pessoas, Chaveiro do animal de estimação, Figura Bobblehead), Explorar (Avaliações reais, Ajuda), dois cartões ("Novidade", "Mais vendido") |
| **Rastrear pedido** | `/account/orders`: pede login com o e-mail do checkout e aponta pedidos antigos para meshy.ai |
| **Ajuda** | `/faq`: Criando, Pedido e pagamento, Envio e entrega, Refazimentos e reembolsos |
| Topo | Faixa de desconto, carrinho (gaveta), Entrar, Cadastrar-se, idioma (25 idiomas), "Fale conosco" (chat Crisp, resposta por e-mail) |

Rotas de produto: `/products/chibi-figure?subject=single_person`, `chibi-figure-2-people`, `chibi-pet`, `chibi-figure-person-and-pet`, `bobblehead-figure`, `custom-3d-keychain`, `fridge-magnet` e `3d-relief-photo-frame`. As duas últimas, e as páginas de pet e de pessoa + pet, não aparecem no menu, mas existem, estão no catálogo da API e aceitam pedidos.

A marca é "**Pockella** by Meshy", com o mesmo tom de presente do Meshy Shop ("Lembranças, feitas obsessivamente", "Aprove ou a gente refaz"). A Meshy aparece em três lugares: o "by Meshy" ao lado do logo, a pergunta do FAQ "A Pockella faz parte da Meshy?" e um aviso de boas-vindas para quem vem do app ("Bem-vindos, amigos do Meshy!").

![Home](prints/desktop/01-home.jpg)
![Menu](prints/desktop/02-menu.jpg)

**Primeira visita:** um aviso de cookies com opt-in por categoria (Analytics, Publicidade da Meta "e creditar o criador que indicou você", Funcionais) cobre parte da primeira tela. A menção a "criador que indicou você" sugere um programa de afiliados ou criadores, que não vi em nenhum outro lugar.

![Primeira visita](prints/desktop/00-home-primeira-visita.jpg)

**Avaliações:** vêm do Judge.me, da loja `meshy-creative-lab`, e são "Traduzido automaticamente". O chaveiro mostra "5,0 (11)". Ao contrário do Meshy Shop, agora há um serviço de avaliações de terceiros.

---

## 2. O criador

![Figura chibi](prints/desktop/03-chibi.jpg)

Mesma estrutura de duas colunas do Meshy Shop: galeria de exemplos à esquerda, upload à direita, e as abas **Criar um design | Meus designs (n)**.

### 2.1 Controles

| Controle | Comportamento observado |
|---|---|
| **Adicionar uma foto** | PNG, JPG ou WEBP. **No desktop, escolher a foto já dispara a geração**, sem confirmação. No Meshy Shop isso só acontecia no mobile. |
| **Parar este design** | Aparece durante a geração. É a forma de desfazer um envio errado. |
| **Mesma foto duas vezes** | Bloqueada no navegador: "Você já criou um design com essa foto. Adicione outra para criar de novo." (só no código) |
| **Nome do pet** | Só no chaveiro, opcional |
| **Assunto** (`?subject=`) | Vem da URL, mas o classificador decide o produto antes de gerar (seção 4) |
| **Dica do bobblehead** | "Uma foto de corpo inteiro da pessoa em pé funciona melhor." |

### 2.2 Design 2D

O texto é o mesmo do Meshy Shop: *"Isso leva cerca de um minuto."* Na prática foi bem mais rápido.

| Produto | Origem das imagens | 4 designs prontos (API) | Tela pronta |
|---|---|---|---|
| Figura chibi (pessoa, pet, casal, pessoa + pet) | fal.ai | ~11 s | 14–17 s |
| Bobblehead | fal.ai | ~13 s | ~17 s |
| Ímã | fal.ai | ~10 s | 14 s |
| Chaveiro | Meshy | ~25 s | 30 s |
| Quadro em relevo | Meshy | ~33 s | 37 s |

O Meshy Shop levava de 26 a 48 s. A barra de progresso agora anda (2%, 9%, 14%, 22%...).

![Gerando](prints/desktop/06-gerando-designs.jpg)
![Quatro designs](prints/desktop/07-quatro-designs.jpg)

São sempre **4 designs de 1024×1024**, com o primeiro já selecionado. Os designs ficam em "Meus designs", e o servidor marca cada um com `expiresAt` de **24 horas**. Não esperei para ver o que acontece depois.

### 2.3 Figura chibi: compra sem 3D

O botão não é mais "Faça este em 3D", e sim **"Pedir este"**, com o texto: *"Escolha uma e você já pode pedir na hora. Nós esculpimos em 3D para a oficina enquanto você finaliza a compra."*

![Compra da figura](prints/desktop/09-compra.jpg)

- Ao clicar, o servidor já começa o 3D (`status: building`), e a tela de compra abre na hora.
- A imagem da tela de compra (`preview.jpg`) é **idêntica, byte a byte, ao design 2D** gerado no fal.ai.
- O 3D terminou em **117 s** (`status: ready`), mas `modelUrl` continuou vazio: **o cliente nunca vê nem recebe o modelo**.
- Tela de compra: **Tipo**, tamanho (o menor vem selecionado), quantidade, preço com R$ 218 riscado, faixa de desconto, "Finalizar compra" e "Adicionar ao carrinho".
- Não há data de chegada. O Meshy Shop mostrava "Compre hoje — chega em 22 de nov.".

**O seletor "Tipo"** lista Uma pessoa, Um pet, Duas pessoas e Uma pessoa e um pet. Ele não muda o produto do design atual: troca para outro design seu daquele tipo (a rede mostrou o design do casal sendo carregado). Cada design tem o tipo fixado pelo classificador.

![Seletor de tipo](prints/desktop/39-pelucia-como-pet.jpg)

### 2.4 Bobblehead: o único com prévia 3D

![Bobblehead: designs](prints/desktop/38-bobblehead-designs.jpg)

"Faça este em 3D — você vai ver antes de comprar." O 3D ficou pronto em **72 s**, e a tela mostra um visualizador (`<canvas>`) com o modelo girando, mais o mesmo aviso do Meshy Shop: *"Refinado à mão, só para você. Um modelador profissional refina manualmente sua figura com base neste design [...] e possa variar um pouco em relação à prévia."*

![Bobblehead: gerando 3D](prints/desktop/08-bobblehead-gerando-3d.jpg)
![Bobblehead: prévia 3D](prints/desktop/10-bobblehead-3d.jpg)

**Arquivo da prévia:** `model-web.glb`, servido do Supabase por URL assinada:

| Item | Valor |
|---|---|
| Tamanho | 2,8 MB |
| Malha | 1 malha, **416.546 triângulos**, 224.705 vértices |
| Textura | 1 material, WebP **2048×2048**, `roughness 0.8`, `metallic 0` |
| Compressão | `EXT_meshopt_compression`, `KHR_mesh_quantization`, `EXT_texture_webp` |
| Gerador | `glTF-Transform v4.5.0` (pós-processado; o motor 3D de origem não aparece) |

O nome sugere uma versão "para web" de um modelo maior, que vai para a produção no `assets.zip` (seção 3.4).

### 2.5 Chaveiro, ímã e quadro

| Produto | Opções na compra | Preço |
|---|---|---|
| **Chaveiro de pet** | Add-on (Gloss, Original) e cor do couro (Onyx, Ruby, Rust, Teal) | R$ 218 |
| **Ímã de geladeira** | 6 cm ou 8 cm | R$ 223 / R$ 279 |
| **Quadro em relevo 3D** | 8×10 ou 10×12 pol., moldura (Natural Wood, Black Walnut), 8 cores de fundo | R$ 334 / R$ 362 (a tela de compra mostrou R$ 335) |

Os três seguem o fluxo "Pedir este", sem prévia 3D. O FAQ do quadro diz que ele aceita mais de um pet ou pessoa com pet: "ninguém é cortado".

![Chaveiro: compra](prints/desktop/35-chaveiro-compra.jpg)
![Quadro: compra](prints/desktop/37b-quadro-compra.jpg)

---

## 3. Compra

### 3.1 Preços (API da loja, mercado Brasil)

| Produto | Tamanho | Brasil | EUA | Meshy Shop (BR, 01/11) |
|---|---|---|---|---|
| **Figura: 1 pessoa** | 6 / 8 / 10 / 12 cm | R$ 190 / 357 / 579 / 858 | US$ 34 / 64 / 104 / 154 | R$ 188 / 354 / 575 / 851 |
| **Figura: 1 pet** | 4 / 6 / 8 cm | R$ 229 / 418 / 808 | US$ 41 / 75 / 145 | R$ 227 / 415 / 801 |
| **Figura: 2 pessoas** | 6 / 8 cm | R$ 273 / 496 | US$ 49 / 89 | R$ 271 / 492 |
| **Figura: pessoa + pet** | 6 / 8 / 10 / 12 cm | R$ 218 / 385 / 607 / 885 | US$ 39 / 69 / 109 / 159 | Não vendia |
| **Bobblehead** | 6 / 8 / 10 / 12 cm | R$ 218 / 385 / 607 / 885 | US$ 39 (6 cm) | Não existia |
| **Chaveiro de pet** | Único (~6 cm de relevo) | R$ 218 | US$ 39 | R$ 216 |
| **Ímã** | 6 / 8 cm | R$ 223 / 279 | — | Não existia |
| **Quadro em relevo** | 8×10 / 10×12 pol. | R$ 334 / 362 | — | Não existia |

- A diferença para o Meshy Shop é de ~1%, compatível com câmbio. Os IDs de variante são os mesmos.
- **Pessoa + pet custa menos que o pet sozinho:** R$ 218 contra R$ 229 no menor tamanho.
- Só a figura de pessoa tem "preço de" (R$ 218 riscado). O quadro tem um "preço de" **menor** que o preço (R$ 329 contra R$ 334), e o site não o exibe.

### 3.2 Carrinho e checkout

![Carrinho](prints/desktop/11-carrinho.jpg)
![Checkout](prints/desktop/12-checkout.jpg)

- **Gaveta lateral** igual à do Meshy Shop, mas o carrinho agora fica **no servidor** (`/api/cart`), ligado ao cookie do convidado.
- **Checkout Shopify** em `checkout.pockella.com`, com o mesmo aviso: *"Seu pedido será adicionado à conta Pockella do e-mail usado na compra — se ainda não existir uma, vamos criá-la."*
- **Pagamento:** cartão, PayPal, WeChat Pay e "+80" métodos, entre eles **Pix**. O rodapé do site cita Visa, Mastercard, Amex, Shop Pay, Apple Pay, Google Pay e PayPal.
- **Países:** 24 no seletor, embora o FAQ diga "enviamos para o mundo todo".

### 3.3 Frete e desconto (com endereço fictício)

| Destino | Forma | Subtotal | WELCOME5 | Frete | Total |
|---|---|---|---|---|---|
| Brasil (SP) | Standard Shipping | R$ 190,00 | − R$ 27,86 | **R$ 26,00** | **R$ 188,14** |
| EUA (NY) | Standard Shipping | US$ 34,00 | − US$ 5,00 | **US$ 5,00** | **US$ 34,00** |

O cupom WELCOME5 já entra no checkout sem o cliente digitar nada ("autoaplicado"). É um desconto fixo de US$ 5, convertido para a moeda local. Somado ao preço riscado da vitrine, quem compra a figura de pessoa vê dois descontos de ~R$ 28, mas só um deles é real.

![Frete Brasil](prints/desktop/13-frete-br.jpg)

### 3.4 O que vai junto com o pedido

O item chega à Shopify com estes atributos ocultos:
- `_design_id` e `_product_handle`;
- `_preview_image_url`: `pockella.com/api/designs/{id}/preview.jpg`;
- `_asset_model_zip_url`: `pockella.com/api/designs/{id}/assets.zip?sig=…&v={variante}`, o pacote de produção;
- `_checkout_thumbnail_url` (cópia na CDN da Shopify) e `_checkout_attempt_id`.

São bem menos campos que no Meshy Shop: sem link de fornecedor, sem foto 3×4, sem URLs de imagem com validade até 2126. Mas o **link assinado do pacote de produção continua chegando ao navegador antes do pagamento**. Não abri esse link, pelo mesmo motivo do estudo anterior.

O checkout tem uma extensão Shopify chamada `creative-lab-thank-you`, herdada da loja da Meshy.

---

## 4. O classificador de assunto

A mudança mais importante em relação ao Meshy Shop: **o classificador roda no envio da foto, antes de qualquer geração**, e devolve o assunto na própria resposta de `POST /api/designs`.

| Foto | Página | Resposta | Resultado |
|---|---|---|---|
| Einstein | Pessoa | `single_person` | Vendido como "Uma pessoa" |
| Casal | Duas pessoas | `two_people` | Vendido como "Duas pessoas" |
| Mulher e cachorro | Pessoa + pet | `person_and_pet` | Vendido como "Uma pessoa e um pet" |
| Cachorro | **Pessoa** | `pet_animal` → produto `chibi-pet` | Gerado e vendido como pet, **com o preço de pet desde o início** |
| Pelúcia (ursinho de pano) | Pet | `pet_animal` | **Aceita como pet, por engano** |
| Mulher em foto antiga | Bobblehead | aceito | Vendido como bobblehead |
| Torre Eiffel | Pessoa | **422** `no_person_or_pet` | Recusado em 4 s: "Precisamos de uma pessoa ou um pet na foto" |
| Beatles (4 pessoas) | Duas pessoas | **422** `three_or_more_people` | Recusado em 4 s: "Recorte e nós fazemos", com lista de espera |

![Sem pessoa ou pet](prints/desktop/16-sem-pessoa-ou-pet.jpg)
![Recorte e lista de espera](prints/desktop/17-recorte-e-lista.jpg)

**O que mudou desde o Meshy Shop:**
- o veredito vem antes de gastar com 2D e 3D, e não mais depois de mais de 1 minuto de 3D;
- o preço não muda no meio do caminho: o cachorro na página de pessoa já nasce como pet;
- a recusa explica o motivo e oferece uma saída (recortar a foto ou entrar na lista de espera);
- "pessoa + pet", que era lista de espera, virou produto.

**O que continua:** o classificador erra em casos de borda. A pelúcia virou pet, assim como a xícara virou pessoa no Meshy Shop.

**Nem todo produto passa por ele:** o chaveiro e o quadro devolvem `subject: null` (seção 11.3). O ímã é classificado.

O código conhece 8 assuntos: `single_person`, `pet_animal`, `two_people`, `person_and_pet`, `three_or_more_people`, `multiple_pets`, `group_with_pets` e `no_person_or_pet`. Os quatro últimos não são vendidos na figura.

---

## 5. Limites

| Limite | Como funciona na prática |
|---|---|
| **Limite diário** | No navegador 1, 9 fotos aceitas (36 imagens) e 2 recusadas; a 12ª tentativa recebeu **429** `allowance_exhausted`: "You have used today's free designs. Come back tomorrow, or order one you already made." No navegador 2 (seção 11), o bloqueio também veio na 12ª tentativa. |
| **Compartilhado entre produtos** | Os designs somaram figura, bobblehead, chaveiro, ímã e quadro |
| **Recusas do classificador** | Não dá para saber se contam. As duas contagens batem com "11 tentativas, contando recusas" e também com "9 para convidado e 10 para conta, sem contar recusas". |
| **Por navegador** | Um navegador novo, no mesmo PC e na mesma rede, recebeu uma cota nova. A cota segue o cookie, não o IP. |
| **Ao estourar** | Aviso fixo na página e um toast: "Você usou os designs gratuitos de hoje. Seus designs salvos ficam aqui — volte amanhã para obter mais.", com o link "Ver os designs que você já tem". **Não há mais o link para o Creative Lab.** |
| **3D** | Só no bobblehead, sob demanda, ou depois de "Pedir este". Não vi limite próprio. |
| **Outros, só no código** | `rate_limited` ("Isso foi rápido. Espere um pouco"), `capacity_unavailable` com motivo `daily_capacity` ("A oficina está ocupada agora"), ou seja, um teto global de capacidade |

![Limite](prints/desktop/14-limite.jpg)

---

## 6. A relação com a Meshy

| Sinal | O que mostra |
|---|---|
| FAQ e rodapé | "A Pockella é a loja própria da Meshy [...] administrada pela MESHY LLC", "© 2026 MESHY LLC" |
| Página de pedidos | "Fez o pedido na meshy.ai antes de 12 de outubro de 2026? Esse pedido está em meshy.ai/shop/orders." |
| Termos | Datados de 10/10/2026, "Pockella is operated by Meshy LLC", com o mesmo endereço em Sunnyvale |
| Loja Shopify | A mesma do Meshy Shop: IDs de variante iguais, avaliações em `judgeme.com/meshy-creative-lab/`, extensão `creative-lab-thank-you` |
| Passagem de modelos | O app da Meshy tem um link `pockella.com/products/chibi-figure?handoff=<token>&source=meshy`, e a Pockella recebe com "Trazendo seu modelo do Meshy". Não exercitei, porque exige conta Meshy. |
| Geração | 2D no fal.ai (figura, bobblehead, ímã) e na Meshy (chaveiro, quadro). A privacidade cita "3D model files generated through the Meshy platform". |

**O Meshy Shop continua no ar** em `meshy.ai/shop` (as páginas respondem, sem redirecionar), mas não refiz o fluxo lá. A data de corte sugere que os pedidos novos vão para a Pockella.

**Arquitetura nova:** Next.js na Vercel, API própria em `/api/*`, banco, autenticação e arquivos no Supabase, imagens no fal.ai. O Meshy Shop rodava dentro do app inteiro da Meshy. Não há um único arquivo JavaScript em comum entre os dois sites.

---

## 7. Políticas: FAQ contra termos

Agora o FAQ e os termos estão bem mais alinhados que no Meshy Shop. Li os termos como leigo.

![FAQ](prints/desktop/23-faq.jpg)

| Tema | FAQ e site | Termos (10/10/2026) |
|---|---|---|
| **Cancelamento** | "Envie uma mensagem em até 24 horas e a gente vai alterar ou cancelar." | Igual: cancelamento por e-mail em até 24 h. Mas *"Orders cannot be modified once submitted"*, enquanto o FAQ diz "alterar ou cancelar". |
| **Não gostou** | "Não é reembolsável por simples mudança de ideia. Se não ficar parecida com eles, a gente refaz — por nossa conta." | Sem devolução por mudança de ideia ou por não gostar do design aprovado. Defeito material ou peça diferente do design: avisar em até **30 dias**, e o remédio "may depend on the Print Partner's policies". |
| **Chegou danificado** | "A gente imprime uma reposição na hora. Não precisa devolver nada." | Reposição ou reembolso "as determined in Our reasonable discretion" |
| **Quem fabrica** | "Feito sob encomenda, conferido à mão" | Um "Print Partner" independente fabrica e envia, e é "responsible for their quality". Recebe o arquivo 3D, nome, endereço e e-mail. |
| **Sua foto** | Não vi a resposta de "O que acontece com a minha foto?" no texto da página | Licença **perpétua, irrevogável e sublicenciável** para a Pockella e os fornecedores. Conteúdo e designs ficam "only for a limited period". **Não encontrei cláusula de treino de IA** com os dados do cliente, ao contrário dos termos gerais da Meshy (s. 2.9). |
| **Disputas** | — | Arbitragem na AAA/ICDR, lei da Califórnia |
| **Uso** | — | Proíbe engenharia reversa do código-fonte, **"competitive analysis"** e usar os resultados para treinar IA |

A privacidade (05/11/2026, o mesmo dia do estudo) descreve o pixel da Meta com envio de eventos pelo servidor e o pré-carregamento do chat Crisp.

---

## 8. Arquitetura técnica (resumo)

> Os detalhes estão em **[pockella-api.md](pockella-api.md)**.

| Peça | Detalhe |
|---|---|
| Front | Next.js (Turbopack) na Vercel, região `gru1` (São Paulo) na borda |
| API | Rotas próprias em `www.pockella.com/api/*`: `designs`, `cart`, `checkout`, `offers`, `products`, `waitlist`, `coupon`, `auth/*` |
| Identidade | Cookie `pk_guest` (httpOnly, 1 ano). Login por código no e-mail ou Google, via Supabase em `auth.pockella.com` |
| Design | `POST /api/designs` (multipart, 202) e polling a cada ~3 s em `GET /api/designs/{id}`. Pipelines: `chibi-figure-v2`, `chibi-figure-two-people`, `chibi-figure-person-and-pet`, `realistic-big-head-figure-v24`, `keychain`, `fridge-magnet`, `3d-relief-photo-frame` |
| Escolha e 3D | `POST /api/designs/{id}/select {candidateIndex}` inicia o build. Bobblehead: `GET /api/designs/{id}/model` → 302 para `model-web.glb` no Supabase |
| Arquivos | Supabase Storage (`…/pockella/uploads`, `…/designs/{id}/concepts`, `preview.jpg`, `model-web.glb`), URLs assinadas de 15 min. Originais do fal.ai em `v3b.fal.media` (públicos) |
| Loja | Mesma Shopify do Meshy Shop. Catálogo e carrinho pela API própria, checkout em `checkout.pockella.com` |
| Rastreamento | Bem mais enxuto que o Meshy Shop: pixel da Meta com eventos também pelo servidor (`/api/meta/events`), PostHog e Statsig por proxy próprio (`/ingest`) e chat Crisp. Sem Google, TikTok, Snap, Criteo etc. |

---

## 9. Pontos fortes e fracos (UX)

**Fortes**
- **Classifica antes de gastar** e explica a recusa, com saída (recortar, lista de espera).
- **Muito rápido:** 4 designs em ~15 s, e a compra abre na hora.
- **Preço certo desde o começo**, porque o produto é decidido antes de gerar.
- **Catálogo maior** sobre o mesmo motor: pessoa + pet, bobblehead, ímã e quadro.
- **Zero atrito**, como antes: gera e compra sem conta, com carrinho no servidor e cookie de 1 ano.
- **Rastreamento enxuto** e cookies com opt-in.
- **Políticas mais coerentes** entre FAQ e termos.

**Fracos**
- **Compra sem ver o 3D** na figura chibi. A prévia é só a imagem 2D, e o modelo real pode ficar diferente dela. O aviso "pode variar" só aparece no bobblehead.
- **Desconto em dobro na vitrine:** R$ 218 riscado mais "R$ 28 de desconto", e só o cupom é real.
- **O classificador ainda erra**, como na pelúcia vendida como pet.
- **A geração começa ao escolher a foto** também no desktop: uma foto errada gasta uma das 9 tentativas, a menos que o cliente clique em "Parar este design" a tempo.
- **Design inventado:** o ímã ganhou folhas, ossos e patas de fundo, e um dos designs do quadro mudou a pose do cachorro (sentado de frente). Na figura antiga, a mulher do "pessoa + pet" ganhou óculos e cabelo de senhora.
- **O "chibi" de pet ainda não é chibi:** o cachorro saiu como miniatura realista, como no Meshy Shop.
- **O bobblehead quase não tem cabeça grande:** os 4 designs têm proporções próximas do normal, e um inventou um "V" com a mão.
- **Preços incoerentes:** pessoa + pet mais barato que o pet sozinho, e o quadro a R$ 334 na vitrine e R$ 335 na compra.
- **Sem data de chegada** na tela de compra.

### Resultados 2D

![Casos em 2D](prints/desktop/90-casos-2d.jpg)

| Foto | Resultado |
|---|---|
| Einstein | Muito parecido e consistente nas 4 opções |
| Casal | Fiel às duas pessoas. A cor das calças muda entre os designs |
| Mulher e cachorro (P&B) | Mantém os dois e colore a foto. A mulher envelhece e ganha óculos em alguns designs |
| Cachorro | Fiel, mas realista, não chibi |
| Pelúcia | Fiel à pelúcia, aceita como "pet" |
| Mulher em foto antiga (bobblehead) | Rosto parecido, corpo inteiro inventado. Cabeça pouco aumentada |
| Gato (chaveiro) | Fiel. A cor da moldura muda entre os designs, independente da cor do couro escolhida depois |
| Cachorro (ímã) | Fiel ao cachorro, com fundos decorativos inventados |
| Cachorro (quadro) | Recorte limpo, mas um design inventa outra pose |

---

## 10. O que isso sugere para o Kubo

1. **A Meshy corrigiu o que o estudo anterior apontou.** Classificar antes de gastar, preço certo cedo e recusa explicada: tudo isso já está na Pockella. Não deu para confirmar se as recusas contam na cota (11.2). O Kubo deve adotar o mesmo, e o diferencial terá de vir de outro lugar.
2. **"Comprar só com o 2D" é a decisão a discutir.** A Pockella tirou o 3D da frente do cliente na figura: a compra abre na hora, e o 3D (~2 min) roda em segundo plano. O Kubo prevê aprovar o 2D e depois mostrar o 3D antes de pagar. As duas leituras possíveis:
   - a favor do caminho da Pockella: menos espera e menos custo de 3D em quem não compra;
   - contra: o cliente compra algo que nunca viu em 3D, e a malha real (aberta, no caso do Trellis) pode diferir da imagem.
   Um meio-termo seria **começar o 3D em segundo plano assim que o cliente escolhe o design**, enquanto ele escolhe o tamanho.
3. **Velocidade virou padrão.** A Pockella entrega 4 designs em ~15 s. Vale medir o tempo do GPT Image 2 no Runware frente a isso, e decidir entre 1 e 4 opções com esse número na mão.
4. **Produtos em relevo são uma porta para o FDM.** O ímã e o quadro em relevo são peças quase planas, que imprimem com muito menos risco que uma figura em pé. Pode valer um teste no Kubo antes das figuras de 12 cm.
5. **Não mostrar "preço de" artificial.** A vitrine da Pockella mostra dois descontos de ~R$ 28 quando só existe um. É o tipo de coisa que gera reclamação no Brasil, e o Kubo deve evitar.
6. **Não mandar links de produção ao navegador**, de novo: o `assets.zip` assinado chega ao convidado antes do pagamento.
7. **A pressão da Meshy aumentou.** Agora é uma marca de consumidor completa, em 25 idiomas, com preços em reais e Pix no checkout. O preço de referência no Brasil continua em **R$ 188 entregue** para uma figura de 6 cm.
8. **Dependência de provedor:** a Meshy é concorrente direta no produto final e, pelos termos da Pockella, proíbe análise competitiva no site dela. Isso reforça a sugestão do estudo anterior de não depender só da Meshy no 3D. O Kubo já segue esse caminho com o Trellis 2 via Runware.
9. **Onde o Kubo ainda diferencia:**
   - **prazo:** produção local, contra envio internacional "em 7–10 dias" mais transporte;
   - **assunto:** a Pockella continua vendendo só pessoas e pets na figura (o quadro aceita grupos de pets);
   - **controle:** a Pockella não tem prompt, estilo nem edição;
   - **prévia:** mostrar o 3D antes de pagar, se o Kubo mantiver essa etapa, vira um argumento.

### Comparação rápida

| | **Jujubit** | **Meshy Shop** | **Pockella** |
|---|---|---|---|
| Entrada | Foto, texto e desenho | Só foto | Só foto (nome do pet no chaveiro) |
| Saídas por tentativa | 1 imagem e 1 3D | 4 imagens, 3D sob demanda | 4 imagens; 3D só no bobblehead |
| Prévia 3D antes de pagar | Sim | Sim | **Só no bobblehead** |
| Classificador | Não | Depois do 3D | **Antes de gerar** |
| Tempo até poder comprar | ~2,5 min | ~30 s + ~1 min | **~15 s** |
| Edição | Chat | Não há | Não há |
| Produtos | Figuras e mais | Figura e chaveiro | Figura (4 tipos), bobblehead, chaveiro, ímã, quadro |
| Motor 2D | — | Não visível | **fal.ai** (figura, bobblehead, ímã); Meshy (chaveiro, quadro) |
| Arquivo da prévia | GLB aberto | `.meshy` cifrado | Só imagem; GLB aberto no bobblehead |
| Limite grátis | 40 por dia | 8 fotos por dia (convidado), 10 (conta) | **~9–10 designs por dia**, por navegador ou conta |
| Checkout logado | — | E-mail vazio | **E-mail preenchido** |
| Figura de ~6 cm | US$ 69,99 | US$ 34 | US$ 34 (R$ 190) |
| Frete | US$ 12,99 nos EUA | US$ 5 nos EUA, R$ 26 no Brasil | Igual ao Meshy Shop |

---

## 11. Com login: conta, cota e pedidos

Segunda sessão, no mesmo dia, num **navegador novo** (outro perfil temporário). O Jeferson entrou com o Google, e a captura de rede ficou desligada durante o login.

**Resumo:** como no Meshy Shop, **a loja quase não muda com login**. O criador, os preços e a compra são os mesmos. Mudam três coisas:
- os designs ficam na conta, e os do convidado passam para ela;
- o checkout já abre com o e-mail da conta;
- a página de pedidos mostra os pedidos da conta.

A conta não tem perfil, endereços, favoritos nem cupons. O menu só mostra o e-mail, **Pedidos** e **Sair**.

![Menu da conta](prints/desktop/31-menu-conta.jpg)
![Pedidos com login](prints/desktop/30b-pedidos-logado.jpg)

O design de convidado transferido para a conta está em [31b-meus-designs-logado.jpg](prints/desktop/31b-meus-designs-logado.jpg).

### 11.1 O que muda ao fazer login

| Item | Sem login | Com login |
|---|---|---|
| **Identidade** | Cookie `pk_guest` | Cookies `sb-auth-auth-token.0` e `.1` (Supabase), além do `pk_guest` |
| **Formas de entrar** | — | Código por e-mail ou Google |
| **Designs** | No convidado | Na conta. **O design criado como convidado no mesmo navegador passou para a conta.** Ao sair, "Meus designs" e o carrinho ficaram vazios. |
| **Carrinho** | No servidor, do convidado | No servidor, da conta. Vazio depois de sair |
| **Cota** | ~9–10 por dia | Parecida (11.2) |
| **Checkout** | E-mail vazio | **E-mail preenchido**. No Meshy Shop, o campo abria vazio mesmo logado. |
| **Pedidos** | Pede login | "Nenhum pedido ainda. Quando você pedir uma lembrança, ela vai aparecer aqui." |
| **Cabeçalho** | Entrar e Cadastrar-se | Inicial do nome ("J") com o menu da conta |

A transferência dos designs deve ser feita pela rota `/api/auth/claim`, que existe no código. A chamada aconteceu durante o login, com a captura desligada, então não a vi.

### 11.2 Cota: o que medi

| Navegador | Tentativas | Resultado |
|---|---|---|
| 1, só convidado | 9 aceitas + 2 recusadas | 12ª bloqueada |
| 2, convidado novo | 1 aceita | — |
| 2, já logado | +9 aceitas + 1 recusada | 12ª bloqueada |

- **O navegador novo ganhou uma cota nova** no mesmo PC e na mesma rede: a cota do convidado segue o cookie, não o IP.
- **Não dá para afirmar se a conta tem uma cota maior.** As duas sessões pararam na 12ª tentativa. Isso bate com "11 tentativas por dia, contando recusas" e também com "9 para convidado e 10 para conta, sem contar recusas, somando o design de convidado transferido".
- Não testei se sair da conta devolve uma cota nova de convidado, porque isso seria contornar o limite.

### 11.3 Os casos novos

| Caso | Resultado |
|---|---|
| Einstein, casal, mulher e cachorro, gato (pet), mulher em foto antiga | Iguais aos da sessão sem login, em 13 a 18 s |
| Gato no ímã | Classificado como `pet_animal` |
| Gato no quadro e cachorro no chaveiro | `subject: null`: **esses dois produtos não passam pelo classificador** |
| Torre Eiffel | Recusada de novo em ~5 s |
| Chaveiro com o nome "Thor" | O nome não apareceu em nenhum dos 4 designs. Não sei se o script preencheu o campo certo antes do envio, que dispara sozinho. |

---

## 12. Versão mobile

Chrome em emulação de celular: 390×844, toque e identificação de iPhone. **Não é um aparelho real.** As páginas públicas foram vistas no navegador 1, sem login; a geração, o 3D e a compra, no navegador 2, com a conta.

| Ponto | Mobile |
|---|---|
| **Início da geração** | Igual ao desktop: **escolher a foto já dispara a geração**, com um círculo de progresso sobre a própria foto |
| **Tempo** | 13 a 18 s para a figura, 28 s para o chaveiro, iguais ao desktop |
| **Cabeçalho** | Menu, logo, carrinho, "Cadastrar-se" (ou a inicial da conta) e idioma. A faixa de desconto ocupa duas linhas |
| **Página do produto** | Galeria em carrossel no topo, título, preço e "Envie uma foto para começar" |
| **Designs** | Grade 2×2, com título e "Pedir este" logo abaixo. Em "Meus designs", miniaturas em linha horizontal |
| **Compra** | Imagem grande, tamanho, preço e "Finalizar compra" sem precisar rolar muito |
| **Bobblehead 3D** | 76 s, com o visualizador no lugar da imagem |
| **Checkout** | Shopify responsivo, com Shop Pay, PayPal e Google Pay no topo, e-mail preenchido e o mesmo frete de R$ 26 |
| **Limite** | Toast amarelo no rodapé e aviso fixo abaixo do botão |
| **Chat** | O botão flutuante do Crisp cobre parte do botão "Adicionar ao carrinho" |

### Criar, comprar e pagar

<img src="prints/mobile/03-chibi.jpg" width="190" alt="Figura"> <img src="prints/mobile/40-envio-ja-gera.jpg" width="190" alt="Envio já gera"> <img src="prints/mobile/41-gerando-designs.jpg" width="190" alt="Gerando"> <img src="prints/mobile/42-quatro-designs.jpg" width="190" alt="Quatro designs">

<img src="prints/mobile/46-compra-logado.jpg" width="190" alt="Compra"> <img src="prints/mobile/47-carrinho-logado.jpg" width="190" alt="Carrinho"> <img src="prints/mobile/48-checkout-email-preenchido.jpg" width="190" alt="Checkout"> <img src="prints/mobile/49-frete-br.jpg" width="190" alt="Frete">

### Bobblehead, chaveiro, recusa e limite

<img src="prints/mobile/50-bobblehead-gerando-3d.jpg" width="190" alt="Bobblehead gerando"> <img src="prints/mobile/51-bobblehead-3d.jpg" width="190" alt="Bobblehead 3D"> <img src="prints/mobile/43-chaveiro-designs.jpg" width="190" alt="Chaveiro"> <img src="prints/mobile/44-sem-pessoa-ou-pet.jpg" width="190" alt="Sem pessoa ou pet">

<img src="prints/mobile/45-limite-logado.jpg" width="190" alt="Limite logado"> <img src="prints/mobile/14-limite.jpg" width="190" alt="Limite"> <img src="prints/mobile/52-menu-conta.jpg" width="190" alt="Menu da conta"> <img src="prints/mobile/18-login.jpg" width="190" alt="Login">

### Páginas públicas

<img src="prints/mobile/01-home.jpg" width="190" alt="Home"> <img src="prints/mobile/02-menu.jpg" width="190" alt="Menu"> <img src="prints/mobile/05-bobblehead.jpg" width="190" alt="Bobblehead"> <img src="prints/mobile/04-chaveiro.jpg" width="190" alt="Chaveiro">

<img src="prints/mobile/07-quatro-designs.jpg" width="190" alt="Meus designs"> <img src="prints/mobile/09-compra.jpg" width="190" alt="Compra"> <img src="prints/mobile/11-carrinho.jpg" width="190" alt="Carrinho"> <img src="prints/mobile/23-faq.jpg" width="190" alt="FAQ">

A tela de compra inteira está em [09b-compra-inteira.jpg](prints/mobile/09b-compra-inteira.jpg), e a home inteira em [01b-home-inteira.jpg](prints/mobile/01b-home-inteira.jpg). Os prints [08-bobblehead-3d.jpg](prints/mobile/08-bobblehead-3d.jpg) e [30-rastrear-pedido.jpg](prints/mobile/30-rastrear-pedido.jpg) são da sessão sem login.

### O que isso sugere para o Kubo

- **Juntar o histórico ao entrar, como a Pockella faz.** É o comportamento que o PRD já prevê, e ele resolve a falha que o Meshy Shop tinha.
- **Preencher o e-mail no checkout de quem está logado.** Parece óbvio, mas o Meshy Shop não fazia.
- **Cota por cookie é fácil de contornar.** Um navegador novo ganha outra cota. Se o custo de IA pesar, o Kubo precisa de mais de um sinal (cookie, IP, dispositivo) ou de exigir login a partir de certo uso.

---

## 13. Outras telas

| Tela | Observação |
|---|---|
| **Login** | "Bem-vindo à Pockella. Entre para salvar seus designs e pedidos — ou continue comprando como convidado." Só **código por e-mail** e **Google**. O Meshy Shop oferecia 7 formas, com Apple, Facebook, Discord e GitHub. |
| **Rastrear pedido** | Login com o e-mail do checkout, mais o aviso sobre pedidos antigos na meshy.ai |
| **Fale conosco** | Chat Crisp que só recolhe pergunta e e-mail: "responderemos por e-mail" |
| **Idioma** | 25 idiomas, entre eles português do Brasil e de Portugal |

![Login](prints/desktop/18-login.jpg)
![Rastrear pedido](prints/desktop/30-rastrear-pedido.jpg)

Outros prints: [página de pessoa + pet](prints/desktop/03b-chibi-pessoa-pet.jpg), [casal](prints/desktop/32-casal-designs.jpg), [pessoa + pet na compra](prints/desktop/33-pessoa-pet-compra.jpg), [chaveiro: designs](prints/desktop/34-chaveiro-designs.jpg), [ímã: designs](prints/desktop/36-ima-designs.jpg) e [compra](prints/desktop/36b-ima-compra.jpg), [quadro: designs](prints/desktop/37-quadro-designs.jpg), [página do ímã](prints/desktop/05b-ima.jpg), [página do quadro](prints/desktop/05c-quadro.jpg), [frete EUA](prints/desktop/13b-frete-us.jpg), [chat](prints/desktop/24-fale-conosco.jpg).

---

### Como este estudo foi feito / limites

- Dois Chromes separados (perfis temporários), controlados com puppeteer; prints e rede capturados por script. No segundo, o Jeferson fez o login com o Google, com a captura desligada.
- **Dados da conta:** o e-mail está mascarado nos prints, e o campo de e-mail do checkout está borrado. Os designs de teste continuam na conta, porque não apaguei nada.
- **Fotos de teste:** as mesmas do estudo de estilos da Jujubit (Einstein, mulher em foto antiga, casal, cachorro, gato, pelúcia, Torre Eiffel) e duas novas de domínio público do Wikimedia Commons: uma mulher com cachorro (c. 1915) e os Beatles (1964).
- **Não fiz nenhum pagamento.** No checkout, usei sobrenome e endereços fictícios, sem dados de pagamento, só para ver o frete. Ficaram um carrinho de convidado com uma figura, no navegador 1, e um checkout aberto da conta, com uma figura e o e-mail preenchido pela própria loja. Nenhum virou pedido.
- **Termos do site:** a s. 2.4 dos termos da Pockella proíbe usar o serviço para "competitive analysis" e para engenharia reversa do código-fonte. Este estudo usou o site como um cliente usaria e leu o JavaScript que o navegador recebe, como nos estudos anteriores. Fica registrado para a decisão de continuar ou não esse tipo de estudo.

**O que deixei de fazer de propósito:**
- **Não abri o link do `assets.zip`**, que é o pacote de produção.
- **O segundo navegador foi pedido pelo Jeferson** para testar a conta e o mobile depois do limite. Não saí da conta para tentar outra cota de convidado.
- **Não entrei na lista de espera** nem enviei a foto recortada.

**O que ficou de fora:**
- O que acontece com os designs depois das 24 horas de `expiresAt`, e o horário de renovação da cota.
- O 3D da figura chibi: o servidor diz que ficou pronto, mas o arquivo não chega ao navegador, então não tenho números de malha dele.
- O motor 3D usado. O GLB do bobblehead foi pós-processado e não traz o gerador original.
- O pedido real e a peça física.
- O login por código no e-mail (só o Google foi usado) e a chamada `/api/auth/claim`.
- Se o nome do pet entra no chaveiro.
- A passagem de modelos do app da Meshy para a Pockella, que exige conta Meshy.
- Moderação de conteúdo impróprio, de figura pública e de personagem protegido: o Einstein passou, e não testei o Mickey desta vez.
- Aparelho real: o mobile foi emulado.
- A frequência de erro do classificador: são poucos casos, escolhidos para forçar os limites.

**Evidência indireta:**
- **2D no fal.ai:** as URLs `v3b.fal.media` nas respostas de `/api/designs/{id}`, idênticas byte a byte à prévia guardada no Supabase.
- **3D na Meshy:** só a frase da política de privacidade e as imagens de `assets.meshy.ai` no chaveiro e no quadro. Para a figura e o bobblehead, não há prova de qual motor gera o 3D.
- **Transferência dos designs para a conta:** o design de convidado apareceu na conta e sumiu ao sair; a rota `/api/auth/claim` está no código, mas a chamada não foi capturada.
