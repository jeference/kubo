# Pockella: referência técnica da API (engenharia reversa)

> Complemento do [pockella.md](pockella.md). Observado em 05/11/2026 como visitante anônimo e, na [seção 2](#2-identidade-e-sessão), com a conta do Jeferson:
> - tráfego real capturado no Chrome via DevTools Protocol;
> - leitura dos chunks JavaScript carregados pelo site.
>
> Os payloads são reais. Assinaturas, tokens e parte dos IDs estão truncados (`…`).
>
> **Legenda:** "Observado" saiu do tráfego. "Só no código" foi lido no JavaScript e não foi exercitado.

## Sumário

1. [Visão geral da arquitetura](#1-visão-geral-da-arquitetura)
2. [Identidade e sessão](#2-identidade-e-sessão)
3. [Design 2D](#3-design-2d)
4. [Escolha, build 3D e modelo](#4-escolha-build-3d-e-modelo)
5. [Classificador de assunto](#5-classificador-de-assunto)
6. [Catálogo, ofertas e carrinho](#6-catálogo-ofertas-e-carrinho)
7. [Checkout](#7-checkout)
8. [Arquivos gerados](#8-arquivos-gerados)
9. [Códigos de erro](#9-códigos-de-erro)
10. [Limites](#10-limites)
11. [Passagem de modelos da Meshy](#11-passagem-de-modelos-da-meshy)
12. [Rastreamento e terceiros](#12-rastreamento-e-terceiros)

---

## 1. Visão geral da arquitetura

```
Navegador (Next.js na Vercel, www.pockella.com; borda gru1, função sfo1)
 │
 ├─ www.pockella.com/api/*                     ← API própria (JSON / multipart)
 │     ├─ POST /designs                        foto → classificador → 4 designs (202) ou 422/429
 │     ├─ POST /designs/{id}/original          foto original, guardada à parte
 │     ├─ GET  /designs/{id}                   polling (~3 s)
 │     ├─ GET  /designs?product=…              "Meus designs"
 │     ├─ POST /designs/{id}/select            escolhe o design e inicia o 3D
 │     ├─ GET  /designs/{id}/model             302 → model-web.glb (bobblehead)
 │     ├─ GET  /designs/{id}/concepts/{i}?from=assets.meshy.ai   proxy de imagens da Meshy
 │     ├─ GET/POST /cart                       carrinho no servidor
 │     ├─ POST /checkout                       cria o carrinho Shopify e devolve a URL
 │     ├─ GET  /products, /products/{handle}, /offers, /waitlist
 │     └─ POST /consent, /meta/events
 │
 ├─ v3b.fal.media/files/…                      imagens 2D originais (fal.ai), públicas
 ├─ fzftrxakkhlqfqcofyoy.storage.supabase.co    Supabase Storage, URLs S3 assinadas de 15 min
 ├─ auth.pockella.com                           Supabase Auth (código por e-mail, Google)
 ├─ www.pockella.com/ingest/*                   proxy de PostHog e Statsig
 └─ checkout.pockella.com                       checkout Shopify (loja meshy-creative-lab)
```

Pipeline observado:

```
foto ──► POST /designs ──► classificador (resposta em ~4 s)
            │  422 subject_unsupported ──► fim, nada gerado
            ▼  202 {designId, subject, productHandle}
         4 imagens 1024×1024 em paralelo (fal.ai ou Meshy, conforme o produto)
            │  cliente escolhe 1
            ▼
         POST /select ──► status "building" ──► "ready" (72–117 s)
            ├─ figura chibi, chaveiro, ímã, quadro: modelUrl continua null
            └─ bobblehead: modelUrl = /api/designs/{id}/model
```

---

## 2. Identidade e sessão

| Item | Valor | Observação |
|---|---|---|
| Cookie `pk_guest` | httpOnly, 69 caracteres, validade de **1 ano** | Identifica o convidado. O Meshy Shop usava um token de 3 dias no `localStorage`. |
| Cookie `shop_stable_id` | UUID, 1 ano | Enviado no checkout como `stableId` |
| Cookie `pk_region` | `other` | Não sei o que muda com outros valores |
| Cookie `shop_locale` | `pt-BR` | |
| `localStorage` | `pk_consent`, `pk_feedback_prompt`, `pk_support_nudge`, Statsig, PostHog, Crisp | Nada de design ou carrinho |

**Login:** Supabase em `auth.pockella.com`, com chave publicável `sb_publishable_…`. Rotas próprias: `/api/auth/providers`, `/api/auth/claim`, `/api/auth/failures` e `/api/auth/signout`.

| Item | Observado |
|---|---|
| Entrada | Google (feita pelo Jeferson, com a captura desligada). O código por e-mail não foi testado. |
| Cookies da sessão | `sb-auth-auth-token.0` e `sb-auth-auth-token.1`; o `pk_guest` continua |
| Designs do convidado | Passaram para a conta: o design criado antes do login apareceu em "Meus designs" e sumiu depois de sair. Deve ser o `claim`, mas a chamada não foi capturada. |
| Sair | `POST /api/auth/signout` → `{"data":{"signedOut":true}}`. Depois disso, `/api/designs` e `/api/cart` voltaram vazios |
| Checkout | O mesmo `POST /api/checkout`, agora com `ads.attribution` (`referrerHost: accounts.google.com`), e o e-mail da conta já chega preenchido no checkout da Shopify |

---

## 3. Design 2D

**Criar:** `POST /api/designs`, multipart, responde **202**.

```json
{"data":{"designId":"48b4ee77-…","status":"prototyping","candidateCount":4,
         "productHandle":"chibi-figure","subject":"single_person"}}
```

Logo depois, o front envia de novo a foto em `POST /api/designs/{id}/original` → `{"data":{"stored":true}}`. Nas fotos recusadas (422), essa segunda chamada não acontece.

**Acompanhar:** `GET /api/designs/{id}`, a cada ~3 s.

```json
{"data":{
  "id":"48b4ee77-…","productHandle":"chibi-figure","pipeline":"chibi-figure-v2","status":"prototyping",
  "candidates":[
    {"index":0,"status":"succeeded","progress":100,"url":"https://v3b.fal.media/files/b/0ab14863/9FiR….jpg","startedAt":"2026-11-05T19:07:09.764Z"},
    {"index":1,"status":"in_progress","progress":0,"url":null,"startedAt":"…"}, …],
  "selectedIndex":null,"previewUrl":null,"buildProgress":0,"modelUrl":null,"modelPending":false,
  "error":null,"createdAt":"2026-11-05T19:07:09.764Z","expiresAt":"2026-11-06T19:07:09.771Z",
  "buildStartedAt":null,"buildFinishedAt":null}}
```

- Cada candidato termina por conta própria. A URL aparece primeiro no **fal.ai** e, segundos depois, é trocada pela cópia no Supabase (`…/designs/{id}/concepts/{i}.jpg`).
- `expiresAt` fica 24 h depois da criação e é renovado no `select`.
- **Lista:** `GET /api/designs?product=chibi-figure&product=chibi-figure-2-people&product=chibi-figure-person-and-pet&product=chibi-pet` devolve `{id, productHandle, status, thumbUrl, createdAt}`.
- **Cancelar (só no código):** `POST /api/designs/{id}/cancel`. **Pré-preencher foto:** `POST /api/designs/prefill-photo`.

### Pipelines e tempos

| Produto (`productHandle`) | `pipeline` | Origem das imagens | 4 prontos |
|---|---|---|---|
| `chibi-figure` | `chibi-figure-v2` | fal.ai | ~11 s |
| `chibi-pet` | `chibi-figure-v2` | fal.ai | ~11 s |
| `chibi-figure-2-people` | `chibi-figure-two-people` | fal.ai | ~11 s |
| `chibi-figure-person-and-pet` | `chibi-figure-person-and-pet` | fal.ai | ~11 s |
| `bobblehead-figure` | `realistic-big-head-figure-v24` | fal.ai | ~13 s |
| `fridge-magnet` | `fridge-magnet` | fal.ai | ~10 s |
| `custom-3d-keychain` | `keychain` | `assets.meshy.ai` | ~25 s |
| `3d-relief-photo-frame` | `3d-relief-photo-frame` | `assets.meshy.ai`, via `/api/designs/{id}/concepts/{i}?from=assets.meshy.ai` (PNG) | ~33 s |

Tempo medido entre `createdAt` e o primeiro polling com os 4 candidatos em `succeeded`. Um design de cada.

---

## 4. Escolha, build 3D e modelo

**Escolher:** `POST /api/designs/{id}/select {"candidateIndex":0}` responde com o design em `status: "building"`. O candidato escolhido passa a apontar para `…/designs/{id}/preview.jpg`, **idêntico byte a byte ao original do fal.ai**.

**Durante e depois:**

| Momento | `status` | `buildProgress` | `modelUrl` |
|---|---|---|---|
| Logo após o select | `building` | 0 | `null` |
| ~30 s | `building` | 39–52 | `null` |
| Fim (figura, 117 s) | `ready` | 100 | **`null`** |
| Fim (bobblehead, 72 s) | `ready` | 100 | `/api/designs/{id}/model` |

`buildFinishedAt` é atualizado durante o build, como um sinal de vida, e não só no fim.

**Modelo do bobblehead:** `GET /api/designs/{id}/model` → **302** → `…/pockella/designs/{id}/model-web.glb?X-Amz-…` (`model/gltf-binary`, 2.835.220 bytes).

| Campo do GLB | Valor |
|---|---|
| `asset.generator` | `glTF-Transform v4.5.0` |
| Extensões obrigatórias | `EXT_meshopt_compression`, `EXT_texture_webp`, `KHR_mesh_quantization` |
| Malha | 1 primitiva, `NORMAL, POSITION, TEXCOORD_0`, 224.705 vértices, 416.546 triângulos |
| Material | `roughnessFactor 0.8`, `metallicFactor 0`, 1 textura base |
| Textura | WebP 2048×2048, 563 KB |

---

## 5. Classificador de assunto

A resposta do `POST /api/designs` já traz o assunto. Quando ele não é vendido:

```json
HTTP 422
{"error":{"code":"subject_unsupported","message":"We do not make this kind of figure yet.",
  "details":{"subject":"three_or_more_people",
             "accepts":["single_person","pet_animal","two_people","person_and_pet"]}}}
```

| Caso | `subject` | Efeito |
|---|---|---|
| Cachorro na página de pessoa | `pet_animal` | `productHandle` trocado para `chibi-pet` já no 202 |
| Pelúcia na página de pet | `pet_animal` | Aceita |
| Torre Eiffel | `no_person_or_pet` | 422 |
| Beatles | `three_or_more_people` | 422, tela "Recorte e nós fazemos" |

**Taxonomia (só no código):**

```js
["single_person","pet_animal","two_people","person_and_pet",
 "three_or_more_people","multiple_pets","group_with_pets","no_person_or_pet"]
// com limites por assunto, p. ex.
three_or_more_people: { people:{min:3,open:true}, pets:{min:0,open:false} }
group_with_pets:      { people:{min:1,open:true}, pets:{min:1,open:true} }
```

**Lista de espera:** `GET /api/waitlist?productId=figure&subject=three_or_more_people` → `{"data":{"joined":false}}`. O cadastro (`POST /api/waitlist`, com e-mail) não foi testado.

---

## 6. Catálogo, ofertas e carrinho

**Catálogo:** `GET /api/products?locale=pt-BR` devolve os 8 produtos com `handle`, `title`, `description`, `optionNames` e `variants[] {id, title, price, compareAtPrice, imageUrl, options}`. Os preços vêm em BRL.

| `handle` | Variantes | `compareAtPrice` |
|---|---|---|
| `chibi-figure` | 6/8/10/12 cm | R$ 218 / 385 / 607 / 885 (preço 190 / 357 / 579 / 858) |
| `chibi-pet` | 4/6/8 cm | — |
| `chibi-figure-2-people` | 6/8 cm | — |
| `chibi-figure-person-and-pet` | 6/8/10/12 cm | — |
| `bobblehead-figure` | 6/8/10/12 cm | — |
| `custom-3d-keychain` | Gloss/Original × Onyx/Ruby/Rust/Teal | — |
| `fridge-magnet` | 6/8 cm | — |
| `3d-relief-photo-frame` | 2 tamanhos × 2 molduras × 8 fundos (32) | R$ 329, **abaixo** do preço |

Os IDs de variante são os do Meshy Shop (p. ex. `gid://shopify/ProductVariant/53942368239932`, o pet de 4 cm).

**Oferta:** `GET /api/offers?locale=pt-BR`

```json
{"data":{"welcome":{"amount":{"amount":"28.00","currencyCode":"BRL"},"approximate":true},
         "freeShipping":false,"remembered":false,"linkRemembered":false}}
```

**Carrinho:** `POST /api/cart?locale=pt-BR`

```json
> {"designId":"48b4ee77-…","variantId":"gid://shopify/ProductVariant/53200594764092","quantity":1}
< {"data":{"items":[{"id":"dc2e1718-…","designId":"48b4ee77-…","productHandle":"chibi-figure",
     "title":"Chibi Figure","pageTemplate":"figure","variantTitle":"6cm",
     "thumbUrl":"https://…supabase.co/…/preview.jpg?…","price":{"amount":"190.0","currencyCode":"BRL"},
     "quantity":1,"addedAt":"2026-11-05T19:11:52.392Z"}],
   "count":1,"subtotal":{"amount":"190.00","currencyCode":"BRL"}}}
```

---

## 7. Checkout

**1. Criar:** `POST /api/checkout`

```json
> {"fromCart":true,"attemptId":"62161104-…","locale":"pt-BR","phDistinctId":"01a1ad19-…",
   "stableId":"9e2f8a5a-…","ads":{"fbp":"fb.1.…"},"functional":true,"linkConsent":true}
< {"data":{"checkoutUrl":"https://checkout.pockella.com/pt-br/cart/c/hWNI…?key=…"}}
```

O servidor monta o carrinho na Shopify. O navegador não fala mais com a Storefront API, ao contrário do Meshy Shop.

**2. Atributos da linha** (vistos na `Proposal` do checkout):

```json
[{"name":"_design_id","value":"48b4ee77-…"},
 {"name":"_product_handle","value":"chibi-figure"},
 {"name":"_checkout_attempt_id","value":"62161104-…"},
 {"name":"_preview_image_url","value":"https://www.pockella.com/api/designs/48b4ee77-…/preview.jpg"},
 {"name":"_asset_model_zip_url","value":"https://www.pockella.com/api/designs/48b4ee77-…/assets.zip?sig=d9e8…&v=53200594764092"},
 {"name":"_checkout_thumbnail_url","value":"https://cdn.shopify.com/s/files/1/0973/4019/5132/files/0_5ae8….jpg?v=…"}]
```

**O link `assets.zip` assinado chega ao navegador antes do pagamento. Não o abri.**

**3. Desconto:** cupom `WELCOME5`, `fixedAmount 5.0 USD`, aplicado em `CART` (R$ 27,86 no Brasil). A Shopify o aplica sem ação do cliente.

**4. Frete:** "Standard Shipping", R$ 26,00 (SP) e US$ 5,00 (NY), com 1 item.

**Extensão de checkout:** `creative-lab-thank-you` (app `353871593473`).

---

## 8. Arquivos gerados

| Arquivo | Onde | Observação |
|---|---|---|
| Foto enviada | `…/pockella/uploads/{designId}/source.jpg` | Miniatura em "Meus designs" |
| Designs (figura, bobblehead, ímã) | `v3b.fal.media/files/b/…/….jpg` e cópia em `…/designs/{id}/concepts/{i}.jpg` | 1024×1024 JPEG. As URLs do fal.ai são públicas e sem expiração aparente |
| Designs (chaveiro, quadro) | `/api/designs/{id}/concepts/{i}?from=assets.meshy.ai` | PNG, 0,6 a 1,4 MB, `cache-control: private, no-store` |
| `preview.jpg` | `…/designs/{id}/preview.jpg` | Cópia do design escolhido |
| `model-web.glb` | `…/designs/{id}/model-web.glb` | Só no bobblehead (seção 4) |
| Pacote de produção | `/api/designs/{id}/assets.zip?sig=…` | Não aberto |

As URLs do Supabase são S3 assinadas (`X-Amz-Expires=900`, 15 min) e são reemitidas a cada polling.

---

## 9. Códigos de erro

**Observados**

| HTTP | `code` | Quando | Tela |
|---|---|---|---|
| 422 | `subject_unsupported` | Assunto fora da lista | "Precisamos de uma pessoa ou um pet na foto" ou "Recorte e nós fazemos" |
| 429 | `allowance_exhausted` | 10º design do dia | "Você usou os designs gratuitos de hoje..." |

**Só no código**

| Código | Tratamento |
|---|---|
| `rate_limited` | "Isso foi rápido. Espere um pouco e tente de novo." |
| `capacity_unavailable` (motivo `daily_capacity` → "closed", senão "busy") | "A oficina está ocupada agora, então não podemos começar um novo design." |
| `photo_rejected`, `invalid_request` | "InvalidPhoto" |
| `subject_blocked` | Tela de bloqueio com lista de espera |
| `concept_expired`, `expired` | "DesignConceptExpired", "DesignExpired" |
| `duplicate_blocked` (no navegador) | "Você já criou um design com essa foto." |
| `unauthorized`, `forbidden`, `not_found`, `conflict`, `internal` | Mensagens genéricas |

---

## 10. Limites

| Limite | Valor | Onde | Evidência |
|---|---|---|---|
| Designs por dia | Bloqueio na 12ª tentativa, nas duas sessões | **Servidor** | Navegador 1: 9 aceitos + 2 recusados. Navegador 2: 1 de convidado + 9 logado + 1 recusado |
| Recusas do classificador | Não determinado se contam | Servidor | As duas contagens admitem as duas leituras |
| Chave da cota do convidado | O cookie, não o IP | Servidor | Navegador novo, mesma rede, cota nova |
| Classificador por produto | Chaveiro e quadro devolvem `subject: null` | Servidor | Observado; o ímã é classificado |
| Imagens por design | 4 | Servidor | `candidateCount` |
| Formatos | `.png, .jpg, .jpeg, .webp, image/*` | Atributo `accept` | Observado |
| Mesma foto | Bloqueada | Navegador | Só no código |
| Capacidade global | `daily_capacity` | Servidor | Só no código |
| Validade do design | 24 h (`expiresAt`) | Servidor | Observado o campo, não o efeito |

**Não testado:** o horário de renovação e se sair da conta dá uma cota nova de convidado.

---

## 11. Passagem de modelos da Meshy

**Lado da Meshy** (chunk do app `meshy.ai`, só no código):

```js
let K = "https://www.pockella.com", G = "/products/chibi-figure",
    V = { skl_8ba1d0686c0efba321f59ee9: {path: G}, skl_2aa28fb3e164ed0b4ad931a2: {path: G} };
function T(token, path = G) {
  const r = new URL(path, K);
  r.searchParams.set("handoff", token);
  r.searchParams.set("source", "meshy");
  return r.toString();
}
// flags relacionadas: pro_3398_shop_to_pockella, pro_2853_shop_top_nav, creative_lab_shop_surface
// no produto chibi do Creative Lab: pockellaHandoff: true
```

**Lado da Pockella** (script inline nas páginas `/products/*`): lê `?handoff=`, remove o parâmetro da URL e mostra "Trazendo seu modelo do Meshy". Mensagens previstas: `ImportStillBuilding`, `ImportOwnedElsewhere` ("já foi trazido para o Pockella em outro navegador"), `ImportTokenInvalid` ("Esse link do Meshy expirou") e `ImportUnavailable`.

**Pedidos antigos:** a página `/account/orders` aponta para `https://www.meshy.ai/shop/orders` os pedidos feitos antes de `2026-10-12`.

---

## 12. Rastreamento e terceiros

| Serviço | Como aparece |
|---|---|
| Meta | Pixel (`connect.facebook.net`, `fbq`) e eventos pelo servidor em `POST /api/meta/events` (`ViewContent`, `AddToCart`, `InitiateCheckout`), com `fbp` |
| PostHog | Por proxy: `/ingest/e/`, `/ingest/i/v0/e/`, `/ingest/array/phc_…/config.js`, surveys |
| Statsig | Por proxy: `/ingest/statsig/initialize`, `/rgstr`. `feature_gates` vazio para o convidado |
| Crisp | Chat de suporte (`client.crisp.chat`), pré-carregado com consentimento funcional |
| Judge.me | Fotos das avaliações (`review-images.judgeme.com/meshy-creative-lab/`) |
| Vercel | Hospedagem, Blob Storage e scripts de analytics no código |
| Sentry | Só no código |

Consentimento: `POST /api/consent` a cada mudança, com categorias Analytics, Publicidade e Funcionais. Aceitei todas logo na primeira visita, então não sei o que carrega antes do aceite. A política de privacidade diz que o envio de eventos pelo servidor à Meta depende de consentimento.
