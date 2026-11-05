# Meshy Shop: referência técnica da API (engenharia reversa)

> Complemento do [meshy.md](meshy.md). Observado em 01/11/2026 como visitante anônimo e, na [seção 13](#13-sessão-logada), em 02/11/2026 com uma conta grátis:
> - tráfego real capturado no Chrome via DevTools Protocol;
> - leitura dos chunks JavaScript carregados pelo site.
>
> Os payloads são reais. Tokens, IDs de convidado e de conta e assinaturas estão truncados (`…`). As seções 1 a 12 descrevem a rota de convidado, salvo indicação.
>
> **Legenda:** "Observado" saiu do tráfego. "Só no código" foi lido no JavaScript e não foi exercitado.

## Sumário

1. [Visão geral da arquitetura](#1-visão-geral-da-arquitetura)
2. [Identidade, headers e envelope de resposta](#2-identidade-headers-e-envelope-de-resposta)
3. [Design 2D](#3-design-2d)
4. [Build 3D e veredito de assunto](#4-build-3d-e-veredito-de-assunto)
5. [Histórico e retomada](#5-histórico-e-retomada)
6. [Chaveiro](#6-chaveiro)
7. [Catálogo e preços (Shopify)](#7-catálogo-e-preços-shopify)
8. [Checkout](#8-checkout)
9. [Arquivos gerados](#9-arquivos-gerados)
10. [Códigos de status e de erro](#10-códigos-de-status-e-de-erro)
11. [Limites e onde são aplicados](#11-limites-e-onde-são-aplicados)
12. [Flags e catálogo interno](#12-flags-e-catálogo-interno)
13. [Sessão logada](#13-sessão-logada)

---

## 1. Visão geral da arquitetura

```
Navegador (Next.js, app de meshy.ai, rota /shop)
 │
 ├─ www.meshy.ai/meshyd-api/web/public/creative-lab/*      ← API de convidado (JSON / multipart)
 │     ├─ POST /guest-session                    token de convidado
 │     ├─ POST /figure/design                    foto → 4 designs (202)
 │     ├─ POST /figure/build                     design → 3D (202)
 │     ├─ GET  /figure/tasks/{id}                polling (~3 s)
 │     ├─ GET  /figure/resumable-tasks           tarefas em andamento
 │     ├─ GET  /assets?products=…                3D salvos
 │     ├─ POST /generator/generate-images        chaveiro
 │     ├─ POST /checkout-token                   pacote de URLs para o pedido
 │     └─ GET  /orders/settle-check              há pedido para estas tarefas?
 │
 ├─ api.meshy.ai/misc/cdn-images|cdn-models/…    URLs assinadas curtas → 302 → assets.meshy.ai
 ├─ assets.meshy.ai                              imagens e model.meshy (URLs assinadas)
 ├─ www.meshy.ai/resource/decrypt/loader-worker.min.js   worker que abre o .meshy
 │
 ├─ meshy-creative-lab.myshopify.com/api/2026-04/graphql.json   Storefront API: preços, cartCreate
 └─ checkout.pockella.com/checkouts/…            checkout Shopify com a marca Pockella
```

Pipeline, inferido das respostas:

```
foto ──► figure-prototype (stage "prototype") ──► 4 imagens 1024×1024
                                                       │ cliente escolhe 1
            imagem escolhida ──► figure-build (stage "build", phase "image-to-3d-texture")
                                   │  texture_ai_model: "blueberry" (Meshy 7)
                                   ├─ subject_type, em 0–7 s, com o build ainda em andamento
                                   └─ model.meshy + preview.png
```

---

## 2. Identidade, headers e envelope de resposta

**Sessão de convidado.** Sem corpo, responde com:

```http
POST /meshyd-api/web/public/creative-lab/guest-session
X-Meshy-Stable-Id: 90251b4a-…
```
```json
{"code":"OK","requestId":"Root=1-…","result":{
  "expiresAt":1793833803834,
  "guestId":"guest_1cbc76c7-bde8-5108-…",
  "token":"DyB8pKqAQ…"}}
```

- O token vale **3 dias** e fica em `localStorage["creative-lab:guest-token"]`. O front renova 1 minuto antes de vencer (só no código).
- `guestId` tem formato de UUID **v5**, gerado a partir de um nome. Não testei a partir de quê.

**Headers das chamadas de convidado (observado)**
```
X-Meshy-Guest-Token: DyB8pKqAQ…
X-Meshy-Stable-Id:   90251b4a-…      ← cookie statsig-stable-id
X-Device-Id:         c9a79454-…      ← localStorage meshy_device_id
```
Os cookies `client_ip` e `geo_country=BR` também seguem junto. O segundo coincide com o mercado usado nos preços.

**Envelope padrão**
```json
{ "code": "OK", "requestId": "Root=1-6ae7c6cb-…", "result": { … } }
```
Em erro, `code` traz o nome do erro e `result` pode ser só uma string (seção 10).

**Variante logada:** observada na [seção 13](#13-sessão-logada). O helper do front escolhe a rota conforme `asGuest`.

---

## 3. Design 2D

**Criar:** `POST /figure/design`, multipart, responde **202**.

```json
{"code":"OK","result":{
  "task_id":"01a19960-8e1f-…",
  "mode":"figure-prototype","status":"PENDING","progress":0,"stage":"prototype",
  "imageIds":["01a19960-8dcf-….jpg"],
  "original_image_url":"https://api.meshy.ai/misc/cdn-images/guest_…/uploads/….jpg?sign=1793664000-…"}}
```

O corpo multipart não é legível na captura. O `content-length` foi de 165.182 bytes para uma foto de 165.000, ou seja, sobram 182 bytes para o limite do multipart e um campo. Tudo indica que **só a imagem vai no pedido, sem prompt ou opção do cliente**. O `?subject=` da URL não aparece na chamada.

**Acompanhar:** `GET /figure/tasks/{id}`, a cada ~3,2 s. `IN_PROGRESS` tem o mesmo formato; ao terminar:

```json
{"code":"OK","result":{
  "task_id":"01a19960-8e1f-…","mode":"figure-prototype","status":"SUCCEEDED",
  "progress":0,"stage":"prototype",
  "imageIds":["….jpg"],"original_image_url":"…",
  "candidates":[
    {"id":"01a19960-db34-….jpg","url":"https://api.meshy.ai/misc/cdn-images/…?sign=…","width":1024,"height":1024},
    {"id":"01a19960-da84-….jpg","url":"…","width":1024,"height":1024},
    {"id":"01a19960-d4bc-….jpg","url":"…","width":1024,"height":1024},
    {"id":"01a19960-ed10-….jpg","url":"…","width":1024,"height":1024}]}}
```

**`progress` ficou em `0` em todas as respostas observadas, inclusive em `SUCCEEDED`.** A barra da tela é estimada pelo front.

**Tempo:** de ~26 a 48 s em 8 tarefas, sequenciais.

---

## 4. Build 3D e veredito de assunto

**Criar:** `POST /figure/build`, JSON, responde **202**.

```json
{"imageIds":["01a19960-db34-….jpg"],"parentId":"01a19960-8e1f-…"}
```
```json
{"code":"OK","result":{
  "task_id":"01a19963-f211-…","mode":"figure-build","status":"PENDING","progress":0,"stage":"build",
  "imageIds":["01a19960-db34-….jpg"],
  "parentId":"01a19960-8e1f-…",
  "texture_ai_model":"blueberry"}}
```

**Durante o build**, o polling já traz o veredito e a miniatura do checkout:
```json
{"task_id":"…","mode":"figure-build","status":"IN_PROGRESS","progress":0,"stage":"build",
 "texture_ai_model":"blueberry",
 "checkout_thumbnail_url":"https://cdn.shopify.com/s/files/1/0973/4019/5132/files/….jpg?v=…",
 "subject_type":"pet_animal"}
```

**Ao terminar:**
```json
{"status":"SUCCEEDED",
 "model_url":"https://api.meshy.ai/misc/cdn-models/guest_…/tasks/…/output/model.meshy?sign=…",
 "thumbnail_url":"https://api.meshy.ai/misc/cdn-images/guest_…/tasks/…/output/preview.png?sign=…",
 "subject_type":"pet_animal"}
```

### Veredito e tempos medidos

| Caso | `subject_type` | 1ª vez visto após o POST | Duração total | Compra |
|---|---|---|---|---|
| Cachorro | `pet_animal` | 3 s | 57 s | Sim |
| Cachorro na página de pessoa | `pet_animal` | 3 s | ~63 s | Sim, preço trocado |
| Einstein | `single_person` | 3 s | 66 s | Sim |
| Mulher | `single_person` | 3 s | ~75 s | Sim |
| Xícara com carinha | `single_person` | 3 s | 66 s | Sim |
| 3 homens e um cachorro | `person_with_pet` | 0 s | 73 s | Não, lista de espera |
| 4 pessoas | `multiple_people` | 0 s | 84 s | Não |
| Torre Eiffel | `other` | 7 s | 275 s | Não |

A duração vem de `updatedAt − createdAt` em `/assets`; nos casos com `~`, do tempo observado na tela. O polling de 3 s limita a precisão da 1ª coluna. Os valores de 0 s indicam que o veredito pode ter vindo da fase anterior ou no próprio início do build.

**O veredito não interrompe o build.** Os casos bloqueados terminam em `SUCCEEDED`, com modelo.

### Regra de venda (só no código)

```js
// Mapa de assunto para produto, condicionado às flags petOrderEnabled e twoPeopleOrderEnabled
{ single_person: "chibi-figure", pet_animal: "chibi-pet", two_people: "chibi-figure-2-people" }
```
Se o assunto não está no mapa ou não corresponde ao item do carrinho, o checkout lança:
```
Creative Lab figure checkout blocked: subject verdict "…" is not for sale (on sale: …)
Creative Lab figure checkout blocked: subject verdict "…" maps to "…" but the cart carries a "…" variant
```

`person_with_pet` está mapeado para uma lista de espera (`creative_lab_figurine_person_and_pet`), o que explica o botão da tela.

**Mensagens da tela:**
- `FigureSubjectBlockedTitle`: "Não conseguimos fazer este ainda"
- `FigureSubjectBlockedBodyWithPetAndTwoPeople`: "No momento, a figura é feita a partir de uma pessoa, de um pet ou de duas pessoas. Tente uma foto que se encaixe em uma dessas opções, com os rostos bem nítidos."

---

## 5. Histórico e retomada

`GET /figure/resumable-tasks`: tarefas em andamento, que o front retoma ao abrir a página.
```json
{"code":"OK","result":{"items":[{"task_id":"…","mode":"figure-build","status":"IN_PROGRESS","stage":"build","parentId":"…"}]}}
```

`GET /assets?pageSize=24&products=chibi-figure&sortBy=-created_at&status=SUCCEEDED&status=PENDING&status=IN_PROGRESS`: 3D salvos.
```json
{"code":"OK","result":{"total":1,"items":[{
  "id":"01a19963-f211-…","name":"Chibi Figure","userId":"guest_…",
  "status":"SUCCEEDED","progress":0,"product":"chibi-figure",
  "mode":"figure-build","phase":"image-to-3d-texture",
  "createdAt":1793574826515,"updatedAt":1793574883300,
  "parentTaskId":"01a19960-8e1f-…","parentTaskMode":"figure-prototype",
  "thumbnailUrl":"https://assets.meshy.ai/guest_…/preview.png?Expires=4947091200&…",
  "checkoutThumbnailUrl":"https://cdn.shopify.com/…",
  "modelUrls":{"glb":"https://api.meshy.ai/misc/cdn-models/…/model.meshy?sign=…"}}]}}
```

- A chave `modelUrls.glb` aponta para um arquivo `model.meshy`. O nome da chave não reflete o formato entregue.
- **Cancelar (só no código):** `POST …/tasks/{id}/cancel`.

---

## 6. Chaveiro

Usa outra família de rotas, com `product_type=pet-badge`:

| Chamada | Observado |
|---|---|
| `GET /generator/resumable-tasks?product_type=pet-badge` | `{"items":[]}` |
| `GET /assets?…&products=keychain&…` | `{"items":[],"total":0}` |
| `POST /generator/generate-images?product_type=pet-badge` | **402**: limite (seção 10) |

**Campos multipart (só no código):** `image`, `num_images`, `prompt_variant`, `remove_background`, `add_name` e `name_text`. Na query, `product_type` e `aspect_ratio`.

Sem login, o limite bloqueou antes do primeiro design. A resposta de sucesso, vista com login, está na [seção 13](#13-sessão-logada).

---

## 7. Catálogo e preços (Shopify)

**Storefront API:** `POST https://meshy-creative-lab.myshopify.com/api/2026-04/graphql.json`, com token público no header `X-Shopify-Storefront-Access-Token`. Operações usadas pela página: `ShopFloorPrices`, `GetProductOptionsEn`, `GetProduct`, `GetProductMarketPrices` e `CartCreate`.

Os preços vêm do mercado, com `@inContext(country: $country)` usando `geo_country`.

| Handle | Título | `vendor` | Variantes |
|---|---|---|---|
| `chibi-figure` | Chibi Figure | 速哇3D摄影 | 6, 8, 10, 12 cm |
| `chibi-pet` | Chibi Pet | 速哇3D摄影 | 4, 6, 8 cm |
| `chibi-figure-2-people` | Chibi Figure for Two | 速哇3D摄影 | 6, 8 cm |
| `custom-3d-keychain` | Custom 3D Keychain | 青岛艾利万格互联网信息科技有限公司 | Gloss/Original × Onyx/Ruby/Rust/Teal |

Preços em [meshy.md §3.1](meshy.md#31-preços-variantes-da-shopify-consultadas-em-br-e-us). A razão BRL/USD ficou em ~5,53 nas variantes comparadas.

---

## 8. Checkout

**1. Pacote de URLs:** `POST /checkout-token {"taskId":"…"}`

```json
{"code":"OK","result":{
  "token":"tsp4Joq-…",
  "subjectType":"pet_animal",
  "checkoutThumbnailUrl":"https://cdn.shopify.com/…",
  "colorImageUrl":"https://assets.meshy.ai/…/preview.png?Expires=4947091200&…",
  "designImageUrl":"https://assets.meshy.ai/…/uploads/….jpg?Expires=4947091200&…",
  "originalImageUrl":"https://assets.meshy.ai/…/uploads/….jpg?Expires=4947091200&…",
  "photo3x4Url":"https://www.meshy.ai/s/…",
  "supplierShortUrl":"https://www.meshy.ai/s/…",
  "bundleZipShortUrl":"https://www.meshy.ai/s/…"}}
```

- `Expires=4947091200` corresponde ao ano **2126**. Vale para a foto original e o design.
- **Os links `supplierShortUrl` e `bundleZipShortUrl` chegam ao convidado antes do pagamento. Não os abri.**
- **Só no código:** se não houver link curto, o front monta o do fornecedor como `/creative-lab/figurine?figurine_supplier=true&token=…`, em locale `zh` por padrão, e o do pacote como `/public/creative-lab/supplier-bundle?token=…&scope=…`.

**2. Carrinho:** mutation `CartCreate`, com a linha:
```json
{"merchandiseId":"gid://shopify/ProductVariant/53942368239932","quantity":1,"attributes":[
  {"key":"_meshy_checkout_token","value":"tsp4Joq-…"},
  {"key":"_product_type","value":"chibi_figure"},
  {"key":"_meshy_device","value":"desktop"},
  {"key":"_checkout_attempt_id","value":"94b81f62-…"},
  {"key":"_fbp","value":"fb.1.…"},
  {"key":"_color_image_url","value":"https://assets.meshy.ai/…"},
  {"key":"_checkout_thumbnail_url","value":"https://cdn.shopify.com/…"},
  {"key":"_original_image_url","value":"https://assets.meshy.ai/…"},
  {"key":"_design_2d_url","value":"https://assets.meshy.ai/…"},
  {"key":"_photo_3x4_url","value":"https://www.meshy.ai/s/…"},
  {"key":"_meshy_supplier_url","value":"https://www.meshy.ai/s/…"},
  {"key":"_meshy_bundle_zip_url","value":"https://www.meshy.ai/s/…"}]}
```
**Atributos opcionais (só no código):** `_grayscale_image_url`, `_parameters_json`, `_model_3d_url`, `_meshy_supplier_preview_url`, `_fbc`.

A resposta traz `checkoutUrl: https://checkout.pockella.com/pt-br/cart/c/…`.

**3. Depois:** `GET /orders/settle-check?task_ids=…` responde `{"latest_order_created_at":null}` enquanto não há pedido.

**Carrinho local:** `localStorage["meshy-shop-cart"]` (Zustand persistido), com `lines[]`, `pendingCheckouts`, `settledOrderTimes`, `owner: "guest"` e `vaults`. Cada linha guarda `merchandiseId`, `taskId`, `subjectProductHandles` e o preço.

---

## 9. Arquivos gerados

| Arquivo | Onde | Observação |
|---|---|---|
| Foto enviada e designs | `api.meshy.ai/misc/cdn-images/guest_…/uploads/{id}.jpg?sign=<epoch>-<hash>` | `sign` expira em `1793664000` nas amostras; a mesma imagem tem URL de longa duração em `assets.meshy.ai` |
| `preview.png` | `…/tasks/{id}/output/preview.png` | Render do 3D |
| `model.meshy` | `api.meshy.ai/misc/cdn-models/…` → **302** → `assets.meshy.ai/…` (CloudFront assinado) | `application/octet-stream`, 4.935.508 bytes no primeiro caso |
| Miniatura do checkout | `cdn.shopify.com/s/files/1/0973/4019/5132/files/{id}.jpg` | O design escolhido é copiado para a Shopify já no início do build |

**`model.meshy`:** o site carrega `www.meshy.ai/resource/decrypt/loader-worker.min.js`, e os modelos de exemplo do catálogo também usam essa extensão. **Não decifrei o arquivo**, portanto não tenho faces, texturas nem metadados, ao contrário dos GLB do Jujubit.

---

## 10. Códigos de status e de erro

**Status de tarefa observados:** `PENDING`, `IN_PROGRESS`, `SUCCEEDED`, `FAILED`.

**Erros observados**

| HTTP | `code` | `result` | Quando |
|---|---|---|---|
| 402 | `CreativeLabFreeDesignsExhausted` | `figure free design limit reached` | 9º design da figura |
| 402 | `PetKeychainFreeDesignsExhausted` | `pet-badge free design limit reached` | 1º design do chaveiro, com a cota já usada na figura |
| 400 | `ImageDecodeFailed` | `Invalid image file` | Arquivo que não é imagem, com login; não conta na cota |

**Falha de tarefa observada:** `status: "FAILED"` com `task_error: {"code":"provider_content_refused","message":"422"}`, na imagem do Mickey, com login (seção 13).

**Erros no código, não exercitados**

| Código | Tratamento na tela |
|---|---|
| `LimitExceeded` ou 429 (convidado) | Toast `GuestDailyLimitReached`: "Você atingiu o limite de designs gratuitos de hoje. Faça login para continuar criando ou volte amanhã." |
| `TooManyPendingTasks`, `GenerationCooldown` | Tratamento próprio; há um `cooldownRemaining: 10` depois de iniciar o design no fluxo do generator |
| 429 (outros) | `TaskAlreadyInProgress` |
| `NsfwContent`, `ForbiddenForNSFW` | Modal de moderação `nsfw` |
| `ForbiddenForPublicFigure` | Modal `public_figure` |
| `ForbiddenForIntellectualProperty` | Modal `ip`, com `rawData.ipDetections` |
| `ModerationUnavailable` | Toast de erro |
| 400 | `InvalidImage`, ou a mensagem do servidor |

Na prática, o bloqueio observado no 9º design não usou a mensagem de login: a tela mostrou "Você já usou os designs gratuitos de hoje..." com o link para o Creative Lab.

---

## 11. Limites e onde são aplicados

| Limite | Valor | Onde | Evidência |
|---|---|---|---|
| Designs por dia, convidado | 8 fotos, somando todos os produtos | **Servidor** | 402 no 9º; 402 no chaveiro com 0 designs dele |
| Imagens por design | 4 | Servidor | `candidates` |
| Builds 3D | Nenhum encontrado | — | 7 builds aceitos depois do limite |
| Tamanho da foto | 10 MB, informado no Creative Lab | Não testado | Texto da página |
| Formatos | `.png, .jpg, .jpeg, .webp` | Atributo `accept` do input | Observado |
| Cota com login | 10 designs de figura por dia, mais 16 para o chaveiro | **Servidor** | `GET /web/v1/creative-lab/start-design-quota` (seção 13) |

**Não testado:** o que identifica o convidado para a cota, e se ela renova no mesmo horário da cota logada. Não testei trocar de perfil, porque seria contornar o limite.

**Custo em créditos para comparação** ([relatório de endpoints](../../../fornecedores-3d/comparativo/Endpoints%20Tripo%20AI%20e%20Meshy.md), API `/openapi/creative-lab/figure/v1`): 6 por imagem e 30 por build. A página do Creative Lab mostra "6 x 4 = 24" para os 4 designs. Se o custo interno seguisse a mesma tabela, o que é suposição:
- 1 tentativa completa custaria 54 créditos (24 + 30);
- as 8 fotos grátis, 192 créditos;
- um 3D bloqueado, 30 créditos sem chance de venda.

---

## 12. Flags e catálogo interno

**Flags relacionadas à loja (só no código):** `creative_lab_shop_surface`, `pro_2853_shop_top_nav`, `pro_3398_shop_to_pockella`.

**Definição do produto chibi no catálogo interno:**
```js
{ kind:"chibi", presetType:"figurine", displayName:"Chibi Figure",
  shopifyProductHandle:"chibi-figure",
  subjectProductHandles:{ pet_animal:"chibi-pet", two_people:"chibi-figure-2-people" },
  checkoutProductType:"chibi_figure", showCompareAtPrice:false, pockellaHandoff:true,
  supplierPagePath:"/creative-lab/figurine?figurine_supplier=true",
  proPositions:{ ar:"figurine_ar", download:"figurine_download", multicolor:"figurine_multicolor" } }
```

**Modelos no código:** `MESHY_7: "blueberry"`, `MESHY_6: "avocado"`, além de `blueberry-20260902` (Meshy 7.1) e `blueberry-2stage`.

**Filamentos:** o catálogo interno associa SKUs de filamento a acabamentos apenas no produto **Pet Keepsake**, do Creative Lab (`marble_white: 13103`, `alabaster: 11100`, `fawn: 11401`, `espresso: 11802`, `graphite: 11101`). Esse produto não está à venda na loja. É a única menção a filamento que encontrei, e pode interessar ao Kubo por ser FDM.

**Rotas relacionadas do Creative Lab:** `/creative-lab/share/[product]/[taskid]`, `/creative-lab/ar/[taskid]`, `/creative-lab/orders/[id]`.

---

## 13. Sessão logada

Observado em 02/11/2026, com uma conta `free`.

**Rotas e headers.** A conta usa `/web/shop/creative-lab/*` no lugar de `/web/public/creative-lab/*`, com os mesmos caminhos depois disso:

```
Authorization: Bearer …
X-Device-Id:   …
```

Sem `X-Meshy-Guest-Token` nem `X-Meshy-Stable-Id` nessas chamadas. O `creative-lab:guest-token` continua no `localStorage` depois do login. Um item de convidado que já estava no carrinho ainda usou `POST /web/public/creative-lab/checkout-token`, sem `Authorization`, e foi aceito.

| Chamada | Observado |
|---|---|
| `POST /web/shop/creative-lab/figure/design` | 202 |
| `POST /web/shop/creative-lab/figure/build` | 202, mesmo corpo do convidado |
| `GET /web/shop/creative-lab/figure/tasks/{id}` | Polling |
| `GET /web/shop/creative-lab/figure/resumable-tasks` | Designs prontos e tarefas em andamento. Um design sai da lista quando o 3D dele termina ou quando é recusado. |
| `GET /web/shop/creative-lab/assets?...` | 3D salvos |
| `POST /web/shop/creative-lab/generator/generate-images?product_type=pet-badge` | 202 |
| `GET /web/shop/creative-lab/generator/tasks/{id}` | Polling do chaveiro |
| `POST /web/shop/creative-lab/checkout-token` | Mesmas chaves do convidado, com `supplierShortUrl` e `bundleZipShortUrl`. `photo3x4Url` faltou no item do casal. **Não abri os links.** |
| `GET /web/v1/creative-lab/orders?pageNum=1&pageSize=20&sortBy=-created_at` | `{"result":[],"total":0}` |
| `GET /web/v1/customer` | 404 `customer not found`, numa conta sem pedido |

**Cota:** `GET /web/v1/creative-lab/start-design-quota`

```json
{"code":"OK","result":{
  "limit":10,"used":0,"remaining":10,
  "reset_at":"2026-11-03T00:00:00Z",
  "free_image_limit":0,"free_image_used":0,"free_image_remaining":0,
  "pet_keychain_free_limit":16,"pet_keychain_free_used":0,"pet_keychain_free_remaining":16,
  "free_products":{"pet-badge":{"limit":16,"used":0,"remaining":16}}}}
```

- `used` sobe no início da tarefa e **desce quando ela é recusada**.
- 3D não altera `used`.
- `pet_keychain_free_used` ficou em `0` depois de um chaveiro pronto, até o fim da sessão. Não sei por quê.
- **Só no código:** o bloqueio na tela (`isQuotaExhausted`) só vale para os planos `free` e `starter`. O padrão é 10 quando o servidor não informa o limite. Com plano pago, não testei.

**Créditos:** `GET /web/v1/me/credits` mostrou o mesmo `freeCreditBalance` do início ao fim, depois de 8 tentativas de design e 5 modelos 3D.

**Recusa:** `GET …/figure/tasks/{id}`, cerca de 1 min depois do envio:

```json
{"task_id":"01a19c29-…","mode":"figure-prototype","status":"FAILED","progress":0,"stage":"prototype",
 "imageIds":["….jpg"],"original_image_url":"…",
 "task_error":{"code":"provider_content_refused","message":"422"}}
```

A tela mostrou "Não deu certo. Tente outra foto.". O código também mapeia `provider_content_refused` e `moderation_blocked` para mensagens próprias no Workspace, fora da loja.

**Chaveiro, ao terminar:** `GET …/generator/tasks/{id}` tem outro formato, sem `candidates`:

```json
{"task_id":"01a19c26-…","status":"SUCCEEDED","progress":0,"original_image_url":"…",
 "images":[{"url":"…","width":1024,"height":1024}, …],
 "depth_maps":[]}
```

Foram 4 imagens, em 58 s. Não há chamada de build.

**3D com login**

| Caso | `subject_type` | 1ª vez visto após o POST | Duração | `texture_ai_model` | Compra |
|---|---|---|---|---|---|
| Mulher | `single_person` | 3 s | 51 s | `blueberry` | Sim |
| Einstein (mobile) | `single_person` | 6 s | 89 s | `blueberry` | Sim |
| 4 pessoas (mobile) | `multiple_people` | 0 s | 80 s | `blueberry` | Não |
| 3 homens e um cachorro (mobile) | `person_with_pet` | 0 s | 99 s | `blueberry` | Não, lista de espera |
| Casal | `two_people` | 3 s | **300 s** | **`avocado`** | Sim |

A duração foi medida entre o horário embutido no `task_id` (UUID v7) e o primeiro polling com `SUCCEEDED`. Antes do veredito final, o `subject_type` pode vir como `other`, como no casal.

**Checkout:** o `CartCreate` leva só `lines` e `attributes`, **sem `buyerIdentity`**. O campo de e-mail abre vazio em `checkout.pockella.com`, mesmo logado. O atributo de topo `href` guarda a página de origem (`/shop/figure?design={taskId}`), e `_meshy_device` vale `desktop` ou `mobile`.

**Chamadas gerais da conta, em toda página da loja:** `me/info`, `me/tier`, `me/credits`, `me/quests`, `me/invitations`, `me/referral-status`, `offers`, `placements/resolve` e `/web/v2/print-tasks/latest`, além de várias consultas de preço de planos que a loja não mostra. Ou seja, a loja carrega o aplicativo inteiro da Meshy.

**Risco da conta:** `POST /web/v1/me/abuse-check` respondeu `{"riskLevel":"high"}` em todas as páginas abertas com login (39 de 39). Nada foi bloqueado por isso na sessão. Não sei o que causa esse valor, nem o efeito dele. O navegador controlado por script pode influenciar, portanto não vale como característica do produto.
