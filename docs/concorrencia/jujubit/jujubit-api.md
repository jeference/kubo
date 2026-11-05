# Jujubit: referência técnica da API (engenharia reversa)

> Complemento do [jujubit.md](jujubit.md). Tudo aqui foi observado em 31/10/2026, como visitante anônimo:
> - tráfego real capturado no Chrome via DevTools Protocol;
> - leitura do bundle `jjb-create-canvas.js` (~600 KB);
> - decodificação do protobuf do chat com o schema embutido no próprio bundle.
>
> Os payloads são reais. Tokens e IDs sensíveis estão truncados (`…`).

## Sumário

1. [Visão geral da arquitetura](#1-visão-geral-da-arquitetura)
2. [Identidade, headers e envelope de resposta](#2-identidade-headers-e-envelope-de-resposta)
3. [Cota: `GET /membership/quota`](#3-cota)
4. [Upload do canvas: presign + PUT S3](#4-upload-do-canvas)
5. [Geração: `POST /activity/tasks` (SSE)](#5-geração-post-activitytasks-sse)
6. [Histórico: listar, buscar, excluir, retry, track, merge, import-preset](#6-histórico)
7. [Chat de edição: gRPC-web + protobuf](#7-chat-de-edição-grpc-web--protobuf)
8. [Carrinho (Shopify Ajax API)](#8-carrinho-shopify-ajax-api)
9. [Arquivos gerados: imagem 2D e GLB](#9-arquivos-gerados)
10. [Códigos de status e de erro](#10-códigos-de-status-e-de-erro)
11. [Limites e onde são aplicados](#11-limites-e-onde-são-aplicados)
12. [Feature flags, experimentos e workflows](#12-feature-flags-experimentos-e-workflows)
13. [Conta e assinatura (com login)](#13-conta-e-assinatura-com-login)

---

## 1. Visão geral da arquitetura

```
Navegador (Shopify theme + app Preact "jjb-create-canvas")
 │
 ├─ jujubit.ai/apps/ai/*              → App Proxy da Shopify → backend de IA da Jujubit (JSON / SSE)
 │     ├─ /membership/quota              cota diária
 │     ├─ /activity/uploads/presign      URL S3 pré-assinada
 │     ├─ /activity/tasks                cria tarefa (SSE) / lista histórico
 │     ├─ /activity/tasks/{id}           consulta tarefa
 │     ├─ /activity/assets/{id}          exclui / retry / track
 │     └─ /auth/chat-token               JWT (Supabase) para o chat
 │
 ├─ s3.us-west-1.amazonaws.com/jujubit-shop-creation   ← PUT direto do canvas (JPG/PNG)
 │
 ├─ csa.jujubit.ai/chat/v1/chat.WebChatService/{Send|Stream}
 │     gateway Kong → serviço de chat (gRPC-web, protobuf). É o "agente" de edição.
 │
 ├─ appcdn.jujubit.ai (CloudFront + S3)
 │     ├─ /agent-runtime/artifacts/{uuid}   PNG 2D (Free Style / edições)
 │     ├─ /llm/image/{data}-{id}.png        PNG 2D (estilos)
 │     └─ /llm/model/{md5}.glb              GLB gerado pela Tripo
 │
 └─ jujubit.ai/cart/*.js                → Shopify Ajax Cart (item com propriedades da geração)
```

Pipeline de uma geração, inferido dos eventos SSE e dos metadados:

```
canvas (foto/texto/desenho) ──► imagem 2D (modelo de imagem; GPT Image 2 em teste no Free Style)
                               └─► checagem de política ("image_policy_rejected")
                     imagem 2D ──► Tripo image-to-3D (faceLimit 300k ou 1,2M) ──► GLB PBR
```

---

## 2. Identidade, headers e envelope de resposta

**Identidade:** não há login para gerar.
- O tema cria um `anonymousId` no `localStorage`, com a chave `_anonymous_id` e um valor como `jatbqvae12k-1793450482783` (`<random36>-<epochMs>`).
- Esse ID vai no corpo ou na query de **todas** as chamadas `/apps/ai/*`.
- Logado, vai também o `customerId` da Shopify (`window.theme.customerId`). O helper `Mt()` (via `jjbUtils.getIdentity()`) retorna `{customerId, anonymousId}`.
- Ao logar, `POST /activity/tasks/merge {customerId, anonymousId}` transfere o histórico anônimo para a conta. O front chama isso **a cada abertura do criador**, e a resposta é `{"mergedCount":0}` quando não há nada novo.
- **Logado, o servidor não confia na identidade enviada.** Isso foi testado em 31/10/2026:
  - `quota` sem parâmetros, ou com o `anonymousId` de **outro** navegador, devolve a cota da conta;
  - `activity/tasks` com outro `anonymousId` devolve o histórico da conta.
  - Ou seja, o backend identifica o cliente pelo App Proxy da Shopify, que assina a requisição e informa o cliente logado. Os IDs no corpo só valem para visitantes.
- Se o `localStorage` estiver vazio, o `anonymousId` reaproveita o cookie `_shopify_y`, e só então é gerado um aleatório.

**Helper de requisição (`At`)**
- Método padrão `POST` e timeout de **15 min** (`6e5*1.5`).
- Headers:
  ```
  Content-Type: application/json
  X-Statsig-Stable-Id: 16a499ea-2bda-4a98-…        ← ID do Statsig (experimentos A/B)
  ```
- Base: `https://jujubit.ai/apps/ai`. Em modo de teste usa `/apps/ai-test`.

**Envelope JSON padrão das respostas**
```json
{ "success": true, "code": 0, "data": { … } }
```
- Headers de resposta: `x-request-id`, `x-trace-id`, `access-control-allow-origin: *`.

---

## 3. Cota

`GET /apps/ai/membership/quota?anonymousId={id}`

```json
{"success":true,"code":0,"data":{"limit":40,"used":38,"frozen":0,"remaining":2}}
```

| Campo | Significado |
|---|---|
| `limit` | Limite diário: 40 para visitante ou conta grátis. O teste A/B `independent_site_free_generation_limit` pode reduzir para 25. PRO tem 100. |
| `used` | Gerações **concluídas com sucesso** hoje |
| `frozen` | Gerações **em andamento**, já reservadas |
| `remaining` | `limit − used − frozen` |

O front consulta a cota a cada ~10 s e a cada ação. **Falhas não consomem a cota**: a reserva é liberada.

- **Logado,** a cota é da conta: 40 no Basic, 100 no Pro e 200 no Premium. Pode-se chamar sem parâmetros (seção 13).
- **A cota volta a zero à meia-noite no fuso da loja** (UTC+8). No Brasil, isso aparece como "Resets daily at 1:00 PM".
- O front também guarda um contador local, `localStorage.jjb_create_daily_usage = {"date":"2026-10-31","count":2}`. É só para a interface.

---

## 4. Upload do canvas

O canvas (foto, desenho ou só fundo) **é sempre enviado como imagem**, mesmo quando só há texto.

**4.1 `POST /apps/ai/activity/uploads/presign`**
```json
// request
{"anonymousId":"jatbqvae12k-1793450482783","contentType":"image/jpeg"}

// response
{"success":true,"code":0,"data":{
  "uploadUrl":"https://s3.us-west-1.amazonaws.com/jujubit-shop-creation/uploads/shopifyimgsave/canvas-input/1793455990153_eece2e1c-….jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=…&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=…",
  "fileUrl":"https://jujubit-shop-creation.s3.us-west-1.amazonaws.com/uploads/shopifyimgsave/canvas-input/1793455990153_eece2e1c-….jpg",
  "method":"PUT",
  "headers":{"Content-Type":"image/jpeg"},
  "expiresIn":300}}
```

**4.2 `PUT {uploadUrl}`**: o corpo é o binário da imagem, com `Content-Type: image/jpeg` ou `image/png`. O front tenta até 3 vezes. A `fileUrl` vira o `canvasSnapshotUrl` da tarefa.

---

## 5. Geração: `POST /activity/tasks` (SSE)

**Request**
```json
{
  "activityType": "canvas",
  "anonymousId": "jatbqvae12k-1793450482783",
  "extra": {
    "workflow": "TEST_creative_real",
    "figureMode": "single",
    "canvasSnapshotUrl": "https://jujubit-shop-creation.s3.us-west-1.amazonaws.com/uploads/shopifyimgsave/canvas-input/1793455990153_eece2e1c-….jpg",
    "useImg2Img": true,
    "prompt": "A cactus in a terracotta pot",
    "source": "canvas",
    "faceLimit": 1200000
  }
}
```

| Campo `extra` | Valores vistos | Observação |
|---|---|---|
| `workflow` | `TEST_creative_real` (Free Style), `board_game` (TRPG), `graduation_funkopop_new_duo` (Mini Pop), `graduation_pixar_new_duo` (Pixar), `scale_1_7_new` (Anime 1:7), `chibi_new_duo` (Classic Chibi)… | Define o prompt e o estilo no servidor |
| `figureMode` | `single` \| `dual` | Solo / Duo |
| `canvasSnapshotUrl` | URL S3 | Foto, desenho ou canvas vazio |
| `useImg2Img` | `true` | O canvas entra como referência de imagem |
| `prompt` | até 200 caracteres | Português funciona |
| `source` | `canvas` \| `preset` \| `edit` | |
| `faceLimit` | `1200000` (workflows "realistas") ou o padrão do workflow (~300k) | Repassado à Tripo |

**Response:** `Content-Type: text/event-stream`. A conexão fica aberta até o fim (~2–3 min), com `ping` periódico. Sucesso real:

```
event: task_start
data: {"taskId":"4094870","status":1}

event: asset_start
data: {"assetId":"4110430","assetType":"template","status":1,"extra":{"workflow":"TEST_creative_real","figureMode":"single"}}

event: ping
data: {}

event: asset_2d_done                       ← ~30–35 s
data: {"assetId":"4110430","assetType":"template","status":2,"extra":{"traceId":"ab32eb2d…","imageUrl":"https://appcdn.jujubit.ai/agent-runtime/artifacts/7113bc47-…","workflow":"TEST_creative_real","figureMode":"single"}}

event: asset_3d_start
data: {"assetId":"4110430","assetType":"template","status":3,"extra":{ …mesmo imageUrl… }}

event: ping                                ← ~1 a cada 10 s
data: {}

event: asset_done                          ← ~110–215 s
data: {"assetId":"4110430","assetType":"template","status":4,"extra":{"traceId":"ab32eb2d…","imageUrl":"https://appcdn.jujubit.ai/agent-runtime/artifacts/7113bc47-…","modelUrl":"https://appcdn.jujubit.ai/llm/model/629d8650919fe39e366bd94abf3df519.glb","workflow":"TEST_creative_real","figureMode":"single"}}

event: task_done
data: {"taskId":"4094870","status":2}
```

**Falha por política de conteúdo** (prompt "Pikachu"; não consome cota):
```
event: asset_done
data: {"assetId":"4110067","assetType":"template","status":5,"extra":{…},"errorCode":1007,"errorMessage":"runtime run failed: image_policy_rejected image request was rejected by safety policy"}

event: task_done
data: {"taskId":"4094507","status":4}
```

**Falha por cota diária** (recusada em ~1 s):
```
event: asset_done
data: {"assetId":"4110434","assetType":"template","status":5,"extra":{…},"errorCode":1028,"errorMessage":"Today's limit reached. Upgrade to Pro for 100 daily generations."}

event: task_done
data: {"taskId":"4094874","status":4}
```

Também existe o evento `task_limit` no código do front, mas ele não apareceu nos testes.

---

## 6. Histórico

### 6.1 Listar: `GET /activity/tasks?anonymousId={id}&activityType=canvas&pageSize=10[&cursor=…]`
```json
{"success":true,"code":0,"data":{
  "tasks":[ …Task… ],
  "nextCursor":"db:2026-10-31 14:20:05.678689|4094972",
  "hasMore":true,
  "totalTasksNum":52, "totalAssetsNum":…, "allTotalTasksNum":…, "allTotalAssetsNum":…}}
```
A paginação é por cursor (`<timestamp>|<taskId>`).

**Task de geração**
```json
{
 "taskId": "4094873", "activityType": "canvas", "sceneKey": "default", "status": 2,
 "extra": {
  "prompt": "A vintage camera", "source": "canvas", "workflow": "TEST_creative_real",
  "faceLimit": 1200000, "figureMode": "single", "useImg2Img": true,
  "canvasSnapshotUrl": "https://jujubit-shop-creation.s3.us-west-1.amazonaws.com/uploads/shopifyimgsave/canvas-input/1793455995007_00da96a9-….jpg"
 },
 "assets": [{
   "assetId": "4110433", "messageId": null, "assetType": "template", "status": 4,
   "errorCode": null, "errorMessage": null,
   "extra": {
    "traceId": "81d1f414…",
    "imageUrl": "https://appcdn.jujubit.ai/agent-runtime/artifacts/c5aa476f-…",
    "modelUrl": "https://appcdn.jujubit.ai/llm/model/73e1fe0bdfd2538ab018b8250258e599.glb",
    "workflow": "TEST_creative_real", "figureMode": "single"
   }
 }],
 "createdAt": "2026-10-31T14:13:15.819Z", "updatedAt": "2026-10-31T14:16:14.246Z"
}
```

**Task criada por edição** (vem do chat; repare em `source: edit`, `conversationId`, `messageId` e `sourceImageUrl`)
```json
{
 "taskId": "4095040", "activityType": "canvas", "status": 2,
 "extra": {"source":"edit","workflow":"TEST_creative_real","conversationId":135287,
           "sourceImageUrl":"https://appcdn.jujubit.ai/agent-runtime/artifacts/a91a3173-…"},
 "assets": [{"assetId":"4110600","messageId":"3248115","assetType":"template","status":4,
   "extra":{"source":"edit","imageUrl":"https://appcdn.jujubit.ai/agent-runtime/artifacts/11ade88c-…",
            "modelUrl":"https://appcdn.jujubit.ai/llm/model/124a65c4dbd2c2a54624768def7552f1.glb",
            "workflow":"TEST_creative_real","conversationId":135287,
            "sourceImageUrl":"https://appcdn.jujubit.ai/agent-runtime/artifacts/a91a3173-…"}}],
 "createdAt": "2026-10-31T14:28:29.480Z", "updatedAt": "2026-10-31T14:31:23.669Z"
}
```

### 6.2 Buscar uma: `GET /activity/tasks/{taskId}?anonymousId={id}`
Retorna `data` com o mesmo formato de Task. Sem SSE, o front faz **polling** por aqui ao recarregar a página com tarefas em andamento.

### 6.3 Excluir: `DELETE /activity/assets/{assetId}`
```json
// request body
{"anonymousId":"jatbqvae12k-1793450482783"}
// response
{"success":true,"code":0,"data":null}
```
Na interface, aparece antes um `confirm()` nativo: *"Delete this history record?"*.

### 6.4 Outros (vistos no código)

| Chamada | Corpo | Uso |
|---|---|---|
| `POST /activity/assets/{assetId}/retry` | `{anonymousId, customerId?}`, com resposta em SSE | Botão **Retry** em falhas que não são de cota |
| `POST /activity/assets/{assetId}/track` | `{anonymousId, event}` (`keepalive`) | Telemetria por item |
| `POST /activity/tasks/merge` | `{customerId, anonymousId}` | Une o histórico anônimo à conta após o login |
| `POST /activity/tasks/import-preset` | `{anonymousId, …preset}` | **Remix** de uma peça da Inspiration |
| `POST /auth/chat-token` | `{anonymousId}` ou `{customerId}` | JWT do chat (seção 7.1) |

---

## 7. Chat de edição: gRPC-web + protobuf

### 7.1 Autenticação

`POST /apps/ai/auth/chat-token`
```json
// request
{"anonymousId":"jatbqvae12k-1793450482783"}
// response
{"success":true,"code":0,"data":{
  "access_token":"eyJhbGciOiJI…",      ← JWT HS256 emitido pelo Supabase
  "token_type":"Bearer",
  "expires_in":2592000,                 ← 30 dias
  "user_id":"f96a0dff-4047-4853-b69e-ea2d217acc0a"}}
```

- Payload do JWT: `{"sub":"f96a0dff-…","role":"authenticated","iss":"supabase","aud":"authenticated","iat":…,"exp":…}`.
- Fica salvo nos cookies `jjb_creation_chat_token` e `jjb_creation_chat_token_identity = ["live","anonymous","<anonymousId>"]`.
- Em `401` ou gRPC status `16`, o front descarta o token e pede outro.
- **Logado,** o corpo é só `{"customerId":"31357…"}`, mesmo havendo `anonymousId`. A resposta tem o mesmo formato, com outro `user_id` do Supabase.

### 7.2 Transporte

- `POST https://csa.jujubit.ai/chat/v1/chat.WebChatService/{Send|Stream}`, atrás do gateway Kong (headers `x-kong-*`).
- Headers da requisição:
  ```
  Authorization: Bearer <jwt>
  Content-Type: application/grpc-web+proto
  X-Grpc-Web: 1
  ```
- **Frames:** 1 byte de flag (`0x00` = mensagem, `0x80` = trailer) + 4 bytes de tamanho (big-endian) + protobuf. O trailer é texto (`grpc-status: 0\r\n`). Limite de 16 MB por frame.
- **`Send`** é unário: um `WebEnvelope` de ida e um de volta.
- **`Stream`** é server-streaming: envia um `WebChatStreamRequest {client_id: uuid}` e fica aberto recebendo `WebEnvelope`s:
  - `ack` de conexão;
  - mensagens do agente;
  - `heartbeat` a cada 30 s.

### 7.3 Schema protobuf (extraído do bundle; o original está em formato protobufjs JSON)

```proto
message WebEnvelope {
  string unique_id = 1;        // UUID gerado pelo cliente
  string trace_id = 2;
  int64  timestamp = 3;        // epoch ms
  string version = 4;          // "v0.1"
  int32  type = 5;             // 1 = normal, 2 = fim de geração (sem payload)
  string acked_unique_id = 6;  // ID do envelope confirmado
  SyncRequest sync = 9;
  ChatMessage chat = 10;
  Heartbeat heartbeat = 11;
  Ack ack = 12;
  ReconnectNotice reconnect = 13;
  DisconnectNotice disconnect = 14;
  SyncSingleMessageRequest sync_single = 15;
  SyncResult sync_result = 16;
  ResolveConversationRequest resolve_conversation = 17;
  ResolveConversationResponse resolve_conversation_result = 18;
}
message ResolveConversationRequest  { int64 asset_id = 1; string workflow = 2; string source = 3; }
message ResolveConversationResponse { int64 conversation_id = 1; string code = 2; }
message SyncRequest { int64 message_id = 1; int64 conversation_id = 2; int32 direction = 3; }
message SyncResult  { repeated ChatMessage messages = 1; string reply_to = 2; }
message SyncSingleMessageRequest { int64 message_id = 1; }
message ChatMessage {
  int64 conversation_id = 1; int64 window_id = 2;
  int32 role = 3;              // 1 = usuário, 2 = agente
  int32 type = 4;              // 2 = mensagem do usuário, 8 = resposta de geração, 5 = cancel, 10 = retry
  MessageBody body = 5; int64 ref_message_id = 6; int64 good_tpl_id = 7;
  int32 send_state = 8;        // 1 = concluída
  string app_version = 9; int64 message_id = 10; string entry_source = 11;
  string send_message_id = 12; MessageMetadata metadata = 13; int32 vote_type = 14;
  int64 generate_at = 15; int32 status = 16;
}
message MessageBody { repeated MessageBodyItem items = 1; }
message MessageBodyItem {
  string type = 1;   // "text" | "image" | "image_2d" | "thinking" | "generating" | "generating_3d" | "model" | "option" | …
  string text = 2; ImageItem image = 3; ModelItem model = 4; int64 good_tpl_id = 5;
  bool skip_in_context = 6; int64 asset_id = 7; string action_type = 8;
  repeated string option_value = 9; repeated string options = 10;
  repeated TemplateItem templates = 11; repeated AssetItem assets = 12;
  repeated CardItem card_list = 13; string error_code = 14;
}
message ImageItem { string url = 1; ImageSize size = 2; int32 type = 3; }
message ImageSize { int64 width = 1; int64 height = 2; }
message ModelItem { ImageItem image_2d = 1; string phr_model = 2; }   // phr_model = URL do GLB
message MessageMetadata {
  int64 created_at = 1; int64 conversation_id = 2; int64 ref_message_id = 3; int64 good_tpl_id = 4;
  int64 window_id = 5; int32 role = 6; AssetInfo asset = 7;
  int64 estimated_time = 8;    // segundos (60)
  bool hide_after_paid = 9;
}
message AssetInfo { int64 id = 1; int64 price = 2; int64 origin_price = 3; int64 discount_end_at = 4; }  // price em centavos
message TemplateItem { int64 id = 1; string image = 2; string video = 3; string prompt = 4; repeated string activities = 5; int64 sort_order = 6; string description = 7; }
message AssetItem { int64 id = 1; string image_url = 2; }
message CardItem { string image = 1; int64 price = 2; CardButton button = 3; int64 tpl_id = 4; int64 activity_price = 5; bool activity_price_null = 6; repeated CardSpec default_select_spec = 7; }
message CardButton { string text = 1; string action_type = 2; }
message CardSpec { int64 id = 1; string type = 2; string value = 3; }
message Heartbeat { int64 client_timestamp = 1; }
message Ack { int32 type = 2; }
message ReconnectNotice { int64 delay_ms = 1; }
message DisconnectNotice { string reason = 1; }
message CancelRequest { int64 message_id = 1; }
message CancelResponse { bool success = 1; }
message WebChatStreamRequest { string client_id = 1; }
```

### 7.4 Sequência real de uma edição (decodificada)

A edição foi *"Add a red scarf"* sobre uma câmera; o agente interpretou como um laço vermelho.

**1) Ao abrir o editor, `Send` com `resolve_conversation`** (encontra ou cria a conversa daquele asset)
```json
→ {"unique_id":"25955309-…","trace_id":"25955309-…","timestamp":"1793456904598","version":"v0.1","type":1,
   "resolve_conversation":{"asset_id":"4110542","workflow":"TEST_creative_real","source":"edit"}}
← {"unique_id":"69254bf2-…","trace_id":"9f516770…","timestamp":"1793456905200","version":"v0.1","type":1,
   "acked_unique_id":"25955309-…",
   "resolve_conversation_result":{"conversation_id":"135287","code":"asset_4110542"}}
   + trailer "grpc-status: 0"
```

**2) `Send` com `sync`** (carrega o histórico da conversa)
```json
→ {"unique_id":"c9193c07-…","version":"v0.1","type":1,"sync":{"conversation_id":"135287"}}
← {"acked_unique_id":"c9193c07-…","sync_result":{"messages":[
     {"conversation_id":"135287","window_id":"777903","role":1,"type":2,
      "body":{"items":[{"type":"text","text":"Make the main color blue"},
                       {"type":"image","image":{"url":"https://appcdn.jujubit.ai/agent-runtime/artifacts/c5aa476f-…","type":1}}]},
      "send_state":1,"message_id":"3247918", …},
     {"conversation_id":"135287","role":2,"type":8,
      "body":{"items":[
        {"type":"model","model":{"image_2d":{"url":"https://appcdn.jujubit.ai/agent-runtime/artifacts/7085b0d4-…","type":1},
                                 "phr_model":"https://appcdn.jujubit.ai/llm/model/660e7d134b931e88ae80571a2982663f.glb"}},
        {"type":"option","option_value":[
          "Make the silver top and bottom trim blue too, while keeping the lens black.",
          "Keep the blue body, but give it a smoother matte finish.",
          "Simplify the tiny markings and fine grooves while keeping the camera's shape and blue color."]}]},
      "send_state":1,"message_id":"3247919",
      "metadata":{"asset":{"id":"904902","price":"2999"},"estimated_time":"60", …},"status":1},
     … ]}}
```

**3) `Send` com `chat`** (a mensagem do usuário, sempre com a imagem-base)
```json
→ {"unique_id":"fb4c13af-…","trace_id":"fb4c13af-…","timestamp":"1793456909041","version":"v0.1","type":1,
   "chat":{"conversation_id":"135287","role":1,"type":2,
           "body":{"items":[{"type":"text","text":"Add a red scarf"},
                            {"type":"image","image":{"url":"https://appcdn.jujubit.ai/agent-runtime/artifacts/a91a3173-…","type":1}}]},
           "entry_source":"shopify_creation","send_message_id":"fb4c13af-…"}}
← {"acked_unique_id":"fb4c13af-…","ack":{"type":1}}        ← só confirma; o resultado chega pelo Stream
```

**4) `Stream`** (aberto no carregamento da página): o que o agente envia, em ordem

| t | Envelope recebido |
|---|---|
| 0 s | `ack {type:1}`, `acked_unique_id:"connected"` |
| +0 s | Eco da mensagem do usuário (`role:1`, com `message_id:"3248114"`) |
| +0 s | `role:2`, item `{"type":"thinking","text":"Waiting for execution..."}`, `metadata.estimated_time:"60"` |
| +0 s | `{"type":"thinking","text":"Understanding your idea..."}` |
| +10 s | `{"type":"thinking","text":"Designing your image..."}` |
| +10 s | `type:8`, item `{"type":"generating"}` |
| +40 s | `type:8`, itens `{"type":"image","image":{"url":".../11ade88c-…"}}` + `{"type":"generating_3d"}`, `metadata.asset:{id:"904992",price:"2999"}` |
| +40 s | `WebEnvelope {type:2}` (sinal de fim da etapa de imagem) |
| +44 s | Mesma mensagem com `send_state:1` e **3 sugestões** `{"type":"option","option_value":["Make the red bow flatter and more securely attached to the camera body.","Give the brown camera grip a smoother finish while keeping the red bow.","Make the camera's silver metal finish matte, keeping the brown grip and red bow."]}` |
| a cada 30 s | `heartbeat {}` |
| ~3 min | O 3D fica pronto. Ele entra no histórico (`/activity/tasks`) como task `source:"edit"` com `modelUrl`, e a mensagem passa a ter `{"type":"model","model":{image_2d, phr_model}}`. |

**5) `Send` com `sync_single`**, para reconciliar uma mensagem específica:
```json
→ {"unique_id":"978a3ba9-…","version":"v0.1","type":1,"sync_single":{"message_id":"3248115"}}
← {"chat":{ …mensagem 3248115 completa… }}
```

**Pergunta de esclarecimento:** quando a mensagem é ambígua, o agente responde só com texto e opções, sem gerar nada. Visto ao enviar 5 cores numa frase só: *"I see five colors in your message—orange, gold, pink, teal, and silver. Which one should I use for the camera's main body color?"*. O front detecta isso por `role 2` + item `text` + item `option` sem `image`/`model`.

**Validação no cliente (`Fc`):** texto ≤ 200 caracteres, **≤ 3 imagens de referência**, todas já enviadas (status `ready`), e pelo menos texto ou uma imagem.

---

## 8. Carrinho (Shopify Ajax API)

`POST /cart/add.js`
```json
{"items":[{"id":62485711716723,"quantity":1,"properties":{
  "_figure_mode":"single",
  "_Generated_model":"",
  "Generated Image":"https://appcdn.jujubit.ai/agent-runtime/artifacts/5812707b-…",
  "_workflow":"TEST_creative_real",
  "_Created From":"jjb_canvas_v2",
  "_Record ID":"4110523"}}]}
```
A resposta é o item da Shopify:
- `variant_title: "6cm Best Fit / 1"`, `sku: "FIG-POD-6CM-1"`;
- `price: 6999`, `final_price: 5950`;
- `discounts: [{amount:1049, title:"CREATE15%OFF"}]`;
- `product_type: "Art Toy"`, `vendor: "JuJuBit"`.

Propriedades com `_` ficam ocultas para o cliente. **`_Generated_model` vai vazio:** o pedido referencia a imagem 2D, e só no fluxo "TRIPO x JUJUBIT" o GLB vai junto (`n.source==="tripo"`).

`POST /cart/update.js` grava atributos de rastreio no carrinho:
```json
{"attributes":{"_identityId":"013bef89…","_statsig_stable_id":"16a499ea-…","_ga_client_id":"1135087967.…","_ga_session_id":"1793454201"}}
```

---

## 9. Arquivos gerados

| Arquivo | Formato | Medido |
|---|---|---|
| Imagem 2D | PNG 1024×1024 RGB (sem alfa, fundo claro) | 0,5–0,9 MB |
| GLB, estilos (`board_game`, `chibi_new_duo`, `scale_1_7_new`, `graduation_*`) | glTF 2.0, `generator: https://tripo3d.ai`, 1 malha / 1 material PBR | **~280–300 mil triângulos, 10–12 MB** |
| GLB, Free Style (`TEST_creative_real`, `faceLimit: 1200000`) | idem | **~1,12–1,20 milhão de triângulos, 33–39 MB** |
| Texturas do GLB | baseColor JPEG 2048², metallicRoughness JPEG 2048², normal PNG 2048² | ~4,5 MB no total |

- Os modelos são normalizados com o maior eixo = 1,0 (de −0,5 a 0,5).
- CDN: CloudFront (`x-amz-cf-pop: GRU3-P12`, em São Paulo), `accept-ranges: bytes`, `access-control-allow-origin: *`.
- O front pré-carrega o GLB (`prefetch`) assim que recebe o `modelUrl`.
- O viewer suporta decoders Draco e Meshopt, mas os GLBs vistos não usam compressão.

---

## 10. Códigos de status e de erro

**`asset.status`** (enum `se` no front)

| Valor | Nome | Significado |
|---|---|---|
| 1 | `IMAGE_GENERATING` | Gerando a imagem 2D |
| 2 | `IMAGE_GENERATED` | 2D pronta |
| 3 | `MODEL_GENERATING` | Gerando o 3D |
| 4 | `MODEL_GENERATED` | Concluído |
| 5 | `FAILED` | Falhou (ver `errorCode`) |

**`task.status`:** 1 = em andamento, 2 = concluída, 4 = falhou.

| `errorCode` | Mensagem do servidor | O que a UI mostra |
|---|---|---|
| **1001** | — | "We couldn't generate from this image. Please try a different one" + "try another image" |
| **1007** | `runtime run failed: image_policy_rejected image request was rejected by safety policy` | **A mensagem crua do servidor** + botão Retry |
| **1001** (visto em 02/11/2026) | Mesmo texto, `runtime run failed: image_policy_rejected…` | *"We couldn't generate from this image. Please try a different one"* + botão **try another image**. Visto uma vez, no layout de celular |
| **1028** | `Today's limit reached. Upgrade to Pro for 100 daily generations.` | A mensagem + botão **Upgrade** (com cota zerada). Se ainda houver cota: "You've unlocked more generations. Try again." |
| outros | `errorMessage` ou nada | "Taking longer than expected. Please try again." |
| (3D) | — | "Failed to load 3D model. Please retry." |

---

## 11. Limites e onde são aplicados

| Limite | Valor | Onde é aplicado | Comportamento observado |
|---|---|---|---|
| Gerações simultâneas | **6** (`un=6`) | **Só no front** | Com 6 "gerando", o botão vira **"Generating…"** desabilitado. O alerta "You can run up to 6 generation tasks at the same time…" fica para chamadas em lote. |
| Gerações por dia (grátis) | **40** (A/B: 25) | **Servidor** (`frozen` reserva na hora) | O front **não bloqueia** com cota zerada. O servidor recusa em ~1 s com `1028`. Uma tarefa enviada quando `used+frozen = limit` falha na hora. |
| Gerações por dia (PRO) | 100 | Servidor | — |
| Edições no chat | **sem limite visto** (11 seguidas, depois de esgotar a cota diária) | — | **Edições não consomem a cota diária**, e cada uma gera também um 3D novo. Só um custo para a Jujubit. |
| Prompt | 200 caracteres | Front | Contador "n/200" |
| Imagens de referência na edição | 3 | Front | — |
| Upload | PNG, WEBP, JPG/JPEG | Front | "Please upload a PNG, WebP, JPG, or JPEG image." |
| Política de conteúdo | personagens de IP famosos (bloqueou **Pikachu**) | Servidor | `1007`, sem consumir cota. **"Mickey Mouse" passou**, mas virou uma placa com o texto "Mickey Mouse". "A pistol" passou e virou uma pistola de brinquedo com ponta laranja. |
| Cota anônima | por `anonymousId` | Servidor | Limpar o `localStorage` gera outro ID, e portanto outra cota (não testei). |

---

## 12. Feature flags, experimentos e workflows

- **Statsig** controla os experimentos (header `X-Statsig-Stable-Id`).
- **Flags vistas** (`nome: {variante: id}`):
  - `creative_use_gpt-image-2:workflow_id {TEST_creative_real, TEST_creative_online_real_v2_gi2}`: troca do modelo de imagem do Free Style para o GPT Image 2.
  - `tripo_face_limit_v2:face_limit`: varia o `faceLimit` dos workflows estilizados.
  - `independent_site_free_generation_limit:basicDailyLimit {40, 25}`.
  - `edit_generation`, `soft_material_preview`, `model_studio_preview`, `checkout_img_preview`, `generating_leave_confirm`, `hide_freestyle_small_sizes`, `split_image_with_prompt`, `compress_image_2`, `membership_create_entry`, `membership_entry_redirect`, `membership_paywall_visual`, `discount_badge_removal`, `canvas_trust_info`, `canvas_template_display` (control/test_1/test_2: este último permite escolher **até 3 estilos de uma vez**), `workflow_slider`, `show_vip_banner`, `add_inspiration`, `inspiration_page`, `generate_progress_animation`.
- **Workflows com `faceLimit` fixo em 1,2 M:** `TEST_creative_real`, `TEST_creative_real_gpt`, `TEST_creative_online_real_v2(_gi2)`, `special_force2`, `western_american2/3`, `ninja`, `piratecore`, `Big_Head_Portrait`, `graduation_highquality_new_duo`.
- **Workflows com `faceLimit` sob experimento:** `board_game`, `chibi`, `chibi_new`, `scale_1_7`, `graduation_pixar_new_duo`, `graduation_funkopop_new_duo`, `dnd_aetherra_world_user/biology`, `semi_realistic_pet_figurine`, `voxel`, `low_poly`, `helmet_doll`, `Ghibli`, `Dark_Gothic1`, `Holmes`, `healing_angel`, `CLASSIC_CHIBI_HEAD`, `fuggler_ugly_cute`.
- **Telemetria:** `window.zlog.track` → `monorepo-monitor-server.jujubit.ai/v1/events:batch`, além de GA4, Google Ads, Meta, TikTok, Pinterest, Reddit, Snap, Bing e o pixel da OpenAI (`oaiq`).

---

## 13. Conta e assinatura (com login)

Capturado em 31/10/2026, com uma conta Basic logada. Todas as chamadas vão para `https://jujubit.ai/apps/ai/membership/*` e usam o mesmo envelope `{success, code, data}`.
- **Nenhuma leva `customerId` ou `anonymousId`:** o servidor identifica o cliente pelo App Proxy da Shopify (seção 2).
- Os IDs abaixo foram truncados.

### 13.1 Estado no HTML (`window.theme`)

Com login, o tema injeta no HTML de toda página:
- `customerId`, `customerFirstName`, `customerLastName`, `customerName` e `customerEmail`;
- `isVip`;
- o estado da assinatura:

```json
theme.membershipState = {
  "plan":"BASIC", "status":"BASIC", "paidThrough":null, "billingCycle":null,
  "subscriptionId":null, "priceId":null, "cancelAtPeriodEnd":false,
  "membershipSource":"PAID", "giftId":null, "giftEndsAt":null,
  "renewalScheduledAt":null, "renewalStatus":"NONE",
  "syncRevision":"95108fa1…"
}
```

`giftId` e `giftEndsAt` indicam que existe (ou vai existir) **assinatura de presente**.

### 13.2 Endpoints

| Chamada | Resposta (`data`) | Uso |
|---|---|---|
| `GET /membership/me` | ver abaixo | Plano e situação da cobrança |
| `GET /membership/quota` | `{"limit":40,"used":1,"frozen":0,"remaining":39}` | Cota da conta, sem parâmetros |
| `GET /membership/coupons?includeExpired=true` | `[]` | Cupons disponíveis e expirados |
| `GET /membership/billing?pageSize=20` | `{"items":[],"nextCursor":null}` | Histórico de cobranças, paginado por cursor |
| `GET /membership/profile` | `{"firstName":"Jeferson","lastName":"Feitosa"}` | Nome no painel |
| `PATCH /membership/profile` `{firstName, lastName}` | o perfil salvo | Pop-up "Name" (`jjb-membership-profile-popup.js`). O e-mail não pode ser editado. |
| `POST /membership/checkouts` | sessão de cobrança | "Get Pro" / "Get Premium" |
| `GET /membership/checkouts/{id}` | a mesma sessão | Consultada por `/pages/checkout-succeed` até confirmar |

`GET /membership/me`
```json
{"plan":"BASIC","billingCycle":null,"billingStatus":"NONE","membershipStatus":"BASIC",
 "cancelAtPeriodEnd":false,"currentPeriodStartsAt":null,"currentPeriodEndsAt":null,
 "paidThrough":null,"membershipSource":"PAID","giftId":null,"giftEndsAt":null,
 "renewalSignupId":null,"renewalScheduledAt":null,"renewalStatus":"NONE",
 "renewalPlan":null,"renewalBillingCycle":null,"resumeVisible":false,
 "interop":{"sourceSystem":"NONE","restrictedReason":null,"currentPlatformAction":"REPURCHASE_ALLOWED"}}
```

- **`interop.sourceSystem`** sugere que a assinatura pode vir de outra plataforma, por exemplo de um app ou da Tripo.
- **`currentPlatformAction`** diz se pode recomprar por aqui.
- **`resumeVisible`** controla o botão de retomar a assinatura depois de cancelada.

### 13.3 Criar a cobrança da assinatura

`POST /apps/ai/membership/checkouts`
```json
// request
{"idempotencyKey":"6a39b37c-…",                    ← UUID; o front reaproveita por 5 min
 "plan":"PRO",                                     ← PRO | PREMIUM
 "billingCycle":"MONTH",                           ← MONTH | YEAR
 "successUrl":"https://exn11x-id.myshopify.com/pages/checkout-succeed?source=h_25bdc8db-…&plan=PRO",
 "uiMode":"HOSTED",                                ← página hospedada (sem clientSecret)
 "analytics":{"statsigStableId":"35691a8e-…","gaClientId":"710286054.…",
              "gaSessionId":"1793477154","entryPage":"membership"}}
// response
{"success":true,"code":0,"data":{
  "id":"0e5ae20c-…", "status":"ACTIVE",
  "url":"https://checkout.airwallex.com/pay?s=eyJraWQi…",   ← JWT de escopo "billing:checkouts", exp 1 h
  "clientSecret":null, "uiMode":"HOSTED",
  "expiresAt":"2026-10-31T21:08:12+0000",
  "mode":"SUBSCRIPTION", "currency":"USD",
  "chargeCents":1990,                                       ← valor cobrado agora
  "creditCents":0}}                                         ← crédito pró-rata (em upgrades)
```

**Fluxo:**
1. O front (`membership-checkout-runtime.js`) monta `analytics`, a partir de GA4 e Statsig.
2. Ele guarda a intenção em `sessionStorage.jjb_membership_checkout_intents_v1` (TTL de 5 min, para não criar duas sessões), além de `jjb_membership_checkout_id`.
3. Também guarda em `localStorage.jjb_membership_checkout_source_<source>` a URL de volta.
4. Por fim, faz `location.assign(url)`, passando pelo redirecionador `jujubit.ai/url?q=…`.
5. A **Airwallex** (`checkout.airwallex.com`, Cloudflare na frente) cria um *payment intent* em modo `recurring` e um cliente `cus_…`, e lista os meios: cartão, Google Pay e Apple Pay.
6. Ao pagar, o cliente volta ao `successUrl`. A página `checkout-succeed` faz polling de `GET /membership/checkouts/{id}` até o status mudar.
7. O backend (via webhook da Airwallex, presumivelmente) atualiza `membershipState`.

### 13.4 Experimentos do funil da assinatura (em `jjb-utils.js`)

| Experimento | Grupos | Efeito |
|---|---|---|
| `membership_entry_redirect` | 93 (false) / 94 (true) | `true`: o "Upgrade" vai para `/pages/vip-program?tab=plans&entry_page=…` em vez de abrir o pop-up. Origens: `generate_create`, `generate_gallery`, `cart_half`, `cart_whole`, `40_generate`, `25_generate`. |
| `membership_cart_entry` | 85 / 86 | Entrada da assinatura no carrinho |
| `membership_paywall_visual` | 101 / 102 | Paywall "legacy" × "visual" |

Esses experimentos podem ser forçados com `localStorage._statsig_override` em hosts de teste (`127.0.0.1`, `shopifypreview.com`) ou com `localStorage._shop_mode = "test"`.
