# Tripo AI developer API: complete endpoint and task-type inventory (as read on 2026-11-01)

**Evidence labels used throughout**

- **[DOC]** current international docs, `developers.tripo3d.ai/en/docs/*` (raw Markdown is at the same URL + `.md`).
- **[PRICE]** official pricing and model pages, `developers.tripo3d.ai/en/pricing` and `/en/models/*`.
- **[MIG]** official migration guide `SKILL.md`, hosted on the docs site and linked from the v2-to-v3 page. It says it was verified against server code in 2026-07, so it predates P2, Rig v3.0 and others.
- **[LEGACY]** older v2 docs at `docs.tripo3d.ai`. Historical unless a current page confirms them.
- **[CN]** China site `developers.tripo3d.com`.
- **[SDK]** official SDK source: secondary, "only in SDK".
- **[CLI]** official `tripo-cli` npm package v0.9.0 (package metadata points to `vast-enterprise/Tripo-API-CLI`): secondary, "only in CLI".
- **not documented** means I looked in the pages listed under coverage and did not find it.

No real API calls were made and no account was created. Nothing here was tested live.

---

## What is the complete list of HTTP endpoints?

### Takeaway
The current API is **v3**, base URL `https://openapi.tripo3d.ai/v3` (international) or `https://openapi.tripo3d.com/v3` (China), with one dedicated endpoint per capability instead of the old `POST /task` plus `type`. I count 27 documented v3 HTTP routes, one further route only in the SDK (`image-to-depth`), one route named in the changelog and migration guide but with no reference page (`upload-credentials`), and two routes that the mapping tables still list but the SDK page calls retired (`refine`, `stylize`). **The v2 API, including its WebSocket watch, was scheduled to shut down on 2026-10-31, the day before this research.**

### Cited Findings

**Where the docs live**
- `platform.tripo3d.ai/docs` is now an empty JavaScript shell: the HTML body is only `<div id="app">`, and every path I tried on that host (`/llms.txt`, `/sitemap.xml`, `/openapi.json`) returned the same shell. — [platform docs](https://platform.tripo3d.ai/docs). The migration guide calls platform.tripo3d.ai "deprecated" as a key console. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- `www.tripo3d.ai/api` redirects to `developers.tripo3d.ai/en`, the current portal. — [redirect target](https://developers.tripo3d.ai/en)
- `developers.tripo3d.ai` publishes an index and a sitemap, and `developers.tripo3d.com` publishes a full concatenated corpus. — [llms.txt](https://developers.tripo3d.ai/llms.txt); [sitemap](https://developers.tripo3d.ai/sitemap.xml); [CN llms-full.txt](https://developers.tripo3d.com/llms-full.txt)
- No OpenAPI spec was found: `developers.tripo3d.ai` advertises none in its llms.txt or sitemap, and `platform.tripo3d.ai/openapi.json` returned the JS shell.

**Base URL, auth, envelope**
- Base URL `https://openapi.tripo3d.ai/v3`; auth header `Authorization: Bearer {api_key}`. — [DOC intro](https://developers.tripo3d.ai/en/docs/introduction)
- China base URL `https://openapi.tripo3d.com/v3`. Keys work only in their own region. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Success `{"code":0,"data":{...}}`; error `{"code","status":"error","message","suggestion","request_id"}`. — [DOC intro](https://developers.tripo3d.ai/en/docs/introduction). MIG shows creation responses with extra fields `{"code":0,"status":"success","data":{"task_id","type","status":"queued"}}`, while the reference pages show only `task_id`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- API keys start with `tsk_`; client IDs start with `tcli_` and do not authenticate. — [LEGACY FAQ](https://docs.tripo3d.ai/other/support-faq.html)

**v3 routes that have their own documentation page**

| # | Method + path (under `https://openapi.tripo3d.ai`) | Purpose | Doc |
|---|---|---|---|
| 1 | `POST /v3/generation/text-to-model` | Text to 3D (H or P series) | [H](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-text-to-model/p) |
| 2 | `POST /v3/generation/image-to-model` | Single image to 3D | [H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-image-to-model/p) |
| 3 | `POST /v3/generation/multiview-to-model` | 2 to 4 views to 3D | [H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/p) |
| 4 | `POST /v3/generation/image-to-splat` | Image to Gaussian splat | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-splat) |
| 5 | `POST /v3/generation/text-to-image` | Text to image | [doc](https://developers.tripo3d.ai/en/docs/generation-text-to-image) |
| 6 | `POST /v3/generation/image-to-image` | Image edit, fusion, style | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-image) |
| 7 | `POST /v3/generation/image-to-multiview` | One image to four views | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-multiview) |
| 8 | `POST /v3/generation/edit-multiview` | Edit generated views | [doc](https://developers.tripo3d.ai/en/docs/generation-edit-multiview) |
| 9 | `POST /v3/models/texture` | (Re)texture a model | [doc](https://developers.tripo3d.ai/en/docs/models-texture) |
| 10 | `POST /v3/models/convert` | Export format and mesh options | [doc](https://developers.tripo3d.ai/en/docs/models-convert) |
| 11 | `POST /v3/models/import` | Import external model | [doc](https://developers.tripo3d.ai/en/docs/models-import) |
| 12 | `POST /v3/mesh/segment` | Split into parts | [doc](https://developers.tripo3d.ai/en/docs/mesh-segment) |
| 13 | `POST /v3/mesh/smartsegment` | End-to-end segmentation incl. auto modeling | [doc](https://developers.tripo3d.ai/en/docs/mesh-smartsegment) |
| 14 | `POST /v3/mesh/complete` | Complete parts, repair missing regions | [doc](https://developers.tripo3d.ai/en/docs/mesh-complete) |
| 15 | `POST /v3/mesh/decimate` | Retopology / low poly | [doc](https://developers.tripo3d.ai/en/docs/mesh-decimate) |
| 16 | `POST /v3/mesh/uv` | Smart UV re-unwrap | [doc](https://developers.tripo3d.ai/en/docs/mesh-uv) |
| 17 | `POST /v3/animations/rig-check` | Check riggability | [doc](https://developers.tripo3d.ai/en/docs/animations-rig-check) |
| 18 | `POST /v3/animations/rig` | Auto rig | [doc](https://developers.tripo3d.ai/en/docs/animations-rig) |
| 19 | `POST /v3/animations/retarget` | Apply preset animations | [doc](https://developers.tripo3d.ai/en/docs/animations-retarget) |
| 20 | `GET /v3/tasks/{task_id}` | Query one task | [doc](https://developers.tripo3d.ai/en/docs/task-query) |
| 21 | `POST /v3/tasks/list` | Query up to 100 tasks | [doc](https://developers.tripo3d.ai/en/docs/task-batch-query) |
| 22 | `POST /v3/files` | Multipart upload, returns `file_token` | [doc](https://developers.tripo3d.ai/en/docs/files) |
| 23 | `POST /v3/files/presign` | Presigned PUT URL for large files | [doc](https://developers.tripo3d.ai/en/docs/files-presign) |
| 24 | `GET /v3/account/balance` | Balance and frozen credits | [doc](https://developers.tripo3d.ai/en/docs/account) |
| 25 | `GET /v3/account/usage` | Per-task usage rows | [doc](https://developers.tripo3d.ai/en/docs/account) |
| 26 | `POST /v3/openai/images/generations` | OpenAI-compatible text to image | [doc](https://developers.tripo3d.ai/en/docs/openai-compat-images) |
| 27 | `POST /v3/openai/images/edits` | OpenAI-compatible image edit | [doc](https://developers.tripo3d.ai/en/docs/openai-compat-images) |

The OpenAI-compatible page is in the sitemap but not in the rendered sidebar or llms.txt. — [sitemap](https://developers.tripo3d.ai/sitemap.xml); [llms.txt](https://developers.tripo3d.ai/llms.txt)

**Routes outside the reference pages**

| Route | Status | Evidence |
|---|---|---|
| `POST /v3/generation/image-to-depth` | **Only in SDK.** The docs SDK matrix lists it for Python only; no reference page (the guessed doc URL returned 404) and no price. Python params: `input`, `kind` (`gray` server default, or `color`), `process_res` (126 to 2016, server default 504); output `depth_image_url`. | [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk); [SDK client](https://raw.githubusercontent.com/Tripo-Developer/tripo-python-sdk/v1.0.0/tripo3d/client.py); [SDK API.md](https://raw.githubusercontent.com/Tripo-Developer/tripo-python-sdk/v1.0.0/docs/API.md) |
| `POST /v3/files/upload-credentials` | **No reference page.** Listed as new in the changelog. MIG: 30-minute STS credentials plus `file_token`. The SDK page says Java's internal descriptor "has no public client flow". | [DOC changelog](https://developers.tripo3d.ai/en/docs/changelog); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk) |
| `POST /v3/models/refine` | **Retired.** Still in the migration and changelog tables, but "Refine and stylize are retired and are not listed as supported"; Python SDK methods raise without sending a request. | [DOC migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3); [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk) |
| `POST /v3/models/stylize` | **Retired**, same as above. Former styles: lego, voxel, voronoi, minecraft, keyring, fridge_magnet, keycap. | [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |

**Webhooks (outbound; Tripo calls you)**
- `POST https://<your-endpoint>`; configured in the console under Settings → Webhooks. No API for registering endpoints and no per-task callback parameter appears in the docs. Events: `task.completed`, `task.failed` (failed or cancelled), `balance.low`. — [DOC webhooks](https://developers.tripo3d.ai/en/docs/webhooks)
- Body fields `id`, `type`, `created_at`, `data`. Headers `Tripo-Webhook-Id`, `Tripo-Webhook-Delivery` (dedupe key), `Tripo-Webhook-Event`, `Tripo-Webhook-Signature`. — [DOC webhooks](https://developers.tripo3d.ai/en/docs/webhooks)
- Signature: `t=<unix>,v1=<hex>`, HMAC-SHA256 of `t + "." + rawBody` with the `whsec_…` secret; optional 5-minute replay window. Respond 2xx within about 5 s; non-2xx or timeouts are retried automatically (retry count and schedule not documented). — [DOC webhooks](https://developers.tripo3d.ai/en/docs/webhooks)

**WebSocket task watching**
- **Not available on v3.** `GET /task/watch/:id` and `GET /task/watch/all[/:since]` existed on v2 (`wss://api.tripo3d.ai/v2/openapi/task/watch/{id}`, frames `{"event":"update|finalized","data":…}`) and are "gone"; the replacement is polling plus webhooks. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

**Legacy v2 surface (base `https://api.tripo3d.ai/v2/openapi`)**
- "The v2 API is scheduled to shut down on 2026-10-31, after which Python SDK 0.x will stop working." — [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk). The migration page still says "v2 and v3 can run in parallel". — [DOC migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3)
- Routes: `POST /task`; `GET /task/{id}`; `POST /task/batch`; `GET /task/watch/:id`; `GET /task/watch/all[/:since]`; `POST /upload`; `POST /upload/sts`; `POST /upload/temporary_token`; `POST /upload/sts/token`; `GET /user/wallet/balance`; `POST /user/wallet/usage/detail`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

### Inferences
- Any integration should target v3 only, since the published shutdown date has passed. Whether v2 actually stopped responding was not tested.
- `POST /v3/files/upload-credentials` should be treated as unsupported for new work, since the current docs steer to `presign` and give it no page.

### Gaps
- **Task cancellation:** `cancelled` is a documented status ("cancelled by user"), but no cancel endpoint is documented. — [DOC task query](https://developers.tripo3d.ai/en/docs/task-query)
- **List all tasks, delete a task or file:** not documented. `POST /v3/tasks/list` takes explicit IDs only.
- **Public OpenAPI spec:** not found.

---

## What is the complete list of task `type` values?

### Takeaway
In v3, `type` is no longer sent in the request; it only appears on the response, naming the task. There are 21 documented or SDK-evidenced values below. Note `stylize_model`, `refine_model`, `classification`, `render_video`, `render_image` and `animate_model` have no supported v3 route.

### Cited Findings

| `type` in response | Endpoint | Status | Source |
|---|---|---|---|
| `text_to_model` | text-to-model | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard) |
| `image_to_model` | image-to-model | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard) |
| `multiview_to_model` | multiview-to-model | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard) |
| `image_to_splat` | image-to-splat | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-splat) |
| `text_to_image` | text-to-image | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-text-to-image) |
| `image_to_image` (v2: `generate_image`) | image-to-image | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-image) |
| `image_to_multiview` (v2: `generate_multiview_image`) | image-to-multiview | Current | [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-multiview) |
| `edit_multiview` (v2: `edit_multiview_image`) | edit-multiview | Current; value named in the multiview-to-model page | [DOC](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard) |
| `texture_model` | models/texture | Current | [DOC](https://developers.tripo3d.ai/en/docs/models-texture) |
| `convert_model` | models/convert | Current | [DOC](https://developers.tripo3d.ai/en/docs/models-convert) |
| `import_model` | models/import | Current | [DOC](https://developers.tripo3d.ai/en/docs/models-import) |
| `mesh_segmentation` | mesh/segment | Current | [DOC](https://developers.tripo3d.ai/en/docs/mesh-segment) |
| `mesh_completion` | mesh/complete | Current | [DOC](https://developers.tripo3d.ai/en/docs/mesh-complete) |
| `highpoly_to_lowpoly` | mesh/decimate | Current | [DOC](https://developers.tripo3d.ai/en/docs/mesh-decimate) |
| `mesh_uv` | mesh/uv | Current | [DOC](https://developers.tripo3d.ai/en/docs/mesh-uv) |
| `smartsegment_image` | mesh/smartsegment, `seg_type=image` | Current | [DOC](https://developers.tripo3d.ai/en/docs/mesh-smartsegment) |
| `smartsegment_model` | mesh/smartsegment, `seg_type=model` | Value appears only in the CLI docs | [CLI process.md, npm package tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) |
| `animate_prerigcheck` | animations/rig-check | Current | [DOC](https://developers.tripo3d.ai/en/docs/animations-rig-check) |
| `animate_rig` | animations/rig | Current | [DOC](https://developers.tripo3d.ai/en/docs/animations-rig) |
| `animate_retarget` | animations/retarget | Current | [DOC](https://developers.tripo3d.ai/en/docs/animations-retarget) |
| `image_to_depth` (name assumed from the SDK method; not shown as a response value) | image-to-depth | Only in SDK | [SDK API.md](https://raw.githubusercontent.com/Tripo-Developer/tripo-python-sdk/v1.0.0/docs/API.md) |

**Retired or dead**
- `refine_model`, `stylize_model`: retired. — [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk)
- `classification`, `render_video`: "none — retired". `render_image`: "none — no V3 route". `animate_model`: dead in v2 (error 2016), superseded by rig-check, rig, retarget. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Doc examples are inconsistent in the CN host: its image-to-model and convert examples show `"type":"text_to_model"`; the international pages show the correct value. — [CN image-to-model](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard); [DOC image-to-model](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard)

### Inferences
- `smart_low_poly` is both a generation parameter and the legacy changelog's name for the mesh task; the wire type for the mesh task is `highpoly_to_lowpoly`.

### Gaps
- `image_to_depth` response `type`: not confirmed by any response example I read.

---

## What are the parameters, outputs and prices for each endpoint?

### Takeaway
1 credit = US$0.01. An H-series image-to-3D task costs 20 credits without texture and 30 with standard texture, plus stacked add-ons; `face_limit` carries no listed surcharge on generation. P2 costs 100 to 130 credits per task, P1 30 to 50 for its base tiers. Failed and cancelled tasks are not charged.

### Cited Findings

#### Billing rules
- "1 credit = $0.01 USD"; top-ups via Stripe from $1. — [PRICE](https://developers.tripo3d.ai/en/pricing). China: 1 credit = ¥0.07 CNY, Alipay. — [CN pricing](https://developers.tripo3d.com/en/pricing)
- Credits are frozen at creation, deducted on success, returned on failure or cancellation. — [DOC billing](https://developers.tripo3d.ai/en/docs/billing)
- `credits_consumed`, `balance`, `frozen` are decimals with up to two places (VIP discounts can make fractional values), so do not parse as integers. — [DOC changelog](https://developers.tripo3d.ai/en/docs/changelog)
- MIG advises not hardcoding credit costs and reading `credits_consumed` instead. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Credits never expire; Studio and API billing are separate. Both come from the legacy FAQ only. — [LEGACY FAQ](https://docs.tripo3d.ai/other/support-faq.html)

#### 3D generation: prices

| Model / input | No texture | Standard | Detailed (HD) | Extreme (8K) | Source |
|---|---|---|---|---|---|
| H3.1 text | 10 | 20 | 30 | 40 | [v3.1 page](https://developers.tripo3d.ai/en/models/v3-1) |
| H3.1 image or multiview | 20 | 30 | 40 | 50 | [v3.1 page](https://developers.tripo3d.ai/en/models/v3-1) |
| P2, every input | 100 | 110 | 120 | 130 | [P2 page](https://developers.tripo3d.ai/en/models/p2) |
| P1 text | 30 | 40 | see note | see note | [pricing bundle](https://developers.tripo3d.ai/assets/PricingPage-WUV2iHaa.js); [LEGACY pricing](https://docs.tripo3d.ai/get-started/pricing.html) |
| P1 image or multiview | 40 | 50 | see note | see note | same |

- H-series add-ons, stacked on base: HD texture +10, 8K texture +20, HD geometry (`geometry_quality=detailed`) +20, quad +5, smart low-poly +10, generate parts +20. — [PRICE](https://developers.tripo3d.ai/en/pricing). The pricing page's H tab prices apply to H2/H3 in general per the legacy table; the v3.1 model page confirms them for v3.1 specifically. — [LEGACY pricing](https://docs.tripo3d.ai/get-started/pricing.html); [v3.1 page](https://developers.tripo3d.ai/en/models/v3-1)
- P1 note: the P tab is rendered client-side, so these values were read from the page's own JS bundle (`noTexP1`, `stdTexP1`, `noTexP2`, `stdTexP2`). Its footnote: "P2 base is 100 credits; texture add-ons match P1 (standard +10)." — [site bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js). Conflict: the legacy page says "P1 pricing is all-in per task". — [LEGACY pricing](https://docs.tripo3d.ai/get-started/pricing.html)
- No `face_limit` surcharge is listed for generation on any pricing page. — [PRICE](https://developers.tripo3d.ai/en/pricing)
- P2 with `quad=true`: the changelog lists no quad surcharge; the CLI says "no add-ons". — [DOC changelog](https://developers.tripo3d.ai/en/docs/changelog); [CLI generate.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)
- Typical speed for H3.1: about 40 s without texture, about 120 s with texture. — [v3.1 page](https://developers.tripo3d.ai/en/models/v3-1)

#### 3D generation: parameter matrix
Sources: [text H](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard), [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard), [multiview H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard), [text P](https://developers.tripo3d.ai/en/docs/generation-text-to-model/p), [image P](https://developers.tripo3d.ai/en/docs/generation-image-to-model/p), [multiview P](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/p).

| Parameter | Type / default | Values and rules | Text | Image | Multiview | H | P |
|---|---|---|---|---|---|---|---|
| `prompt` | string, required | Up to 1024 chars | Yes | | | Yes | Yes |
| `negative_prompt` | string, optional | Up to 255 chars | Yes | | | Yes | Yes |
| `input` | string, required | Exactly one of `file_token`, public URL, or `task_id` of a `text_to_image`/`image_to_image` task. PNG, JPEG, WebP; max 20 MB; recommended at least 256×256 px | | Yes | | Yes | Yes |
| `inputs` | object[] or string[], required | View-key objects (`front`, `left`, `back`, `right`; value is URL, `file_token`, `{url}`, `{file_token}`, or `{object:{bucket,key}}`), or exactly 4 positional strings with `""` to skip, or `[{"task_id":…}]` from `image_to_multiview`/`edit_multiview`. Front required, at least 2 images | | | Yes | Yes | Yes |
| `model` | string, **required on the international docs** | H: `v3.1-20260211`, `v3.0-20250812`, `v2.5-20250123`. P: `P1-20260311`, `P2-20260801` | Yes | Yes | Yes | Yes | Yes |
| `model_seed` | integer, optional | Same seed plus same input gives an identical mesh | Yes | Yes | Yes | Yes | Yes |
| `image_seed` | integer, optional | Seed for the internal text-to-image stage | Yes | | | Yes | Yes |
| `enable_image_autofix` | boolean, `false` | Optimizes the input image first | | Yes | | Yes | Yes |
| `texture_alignment` | string, `original_image` | `original_image`, `geometry` | | Yes | Yes | Yes | Yes |
| `orientation` | string, `default` | `default`, `align_image`; only with `texture=true` | | Yes | Yes | Yes | Yes |
| `face_limit` | integer, optional | See limits below; adaptive if omitted | Yes | Yes | Yes | Yes | Yes |
| `texture` | boolean, `true` | `false` gives bare geometry | Yes | Yes | Yes | Yes | Yes |
| `pbr` | boolean, `true` | `base_color`, `metallic`, `roughness`, `normal`; `true` forces `texture=true` | Yes | Yes | Yes | Yes | Yes |
| `texture_seed` | integer, optional | Keep `model_seed`, vary this for new textures on the same geometry | Yes | Yes | Yes | Yes | Yes |
| `texture_quality` | string, `standard` | `fast` (only texture v3.5, else error 1004; same size and credits as standard), `standard`, `detailed`, `extreme` (8K) | Yes | Yes | Yes | Yes | Yes |
| `texture_version` | string, derived | `v3.5-20260815`, `v3.0-20250812` (default for v3.x and P), `v2.5-20250123` (default for v2.5) | Yes | Yes | Yes | Yes | Yes |
| `delight` | boolean, `true` | Removes baked lighting; read only by texture v3.5 | Yes | Yes | Yes | Yes | Yes |
| `geometry_quality` | string, `standard` | `standard`, `detailed` (Ultra); model at least v3.0 | Yes | Yes | Yes | Yes | |
| `auto_size` | boolean, `false` | Scale to real-world size in meters | Yes | Yes | Yes | Yes (v3.0+) | Yes |
| `quad` | boolean, `false` | Forces FBX; 10,000 faces if no `face_limit`. H: v3.0+. P: **P2 only**; `quad=true` on P1 returns 400 | Yes | Yes | Yes | Yes (v3.0+) | P2 |
| `smart_low_poly` | boolean, `false` | Hand-crafted-style low poly; complex inputs may fail; takes precedence over parts | Yes | Yes | Yes | Yes (v3.0+) | |
| `generate_parts` | boolean, `false` | Needs `texture=false` and `pbr=false`, else 1004; `quad` is ignored | Yes | Yes | Yes | Yes (v3.0+) | |
| `compress` | string, optional | `geometry` (meshopt) | Yes | Yes | Yes | Yes (v3.0+) | |
| `export_orientation` | string, `+x` | `+x`, `-x`, `-y`, `+y`. Docs warn it can produce wrongly oriented post-processing results with `status: success`; convert at the last step instead | Yes | Yes | Yes | Yes | Yes |
| `export_uv` | boolean, `true` | `false` for faster generation, smaller file | Yes | Yes | Yes | Yes | Yes |

- **Output:** `output.model_url`, `output.rendered_image_url`. Examples show `.glb`, and no output-format parameter exists on generation. — [DOC image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard). MIG: v2's `pbr_model`, `model`, `base_model` merged into one `model_url`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- **Conflict on `model`:** the international pages mark it required, and MIG says omitting it returns 400/1004 with "No default". The China host page says optional with default `v3.1-20260211`, and the `/en/models/v3-1` page carries a "Default" tag. — [DOC image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [CN image H](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard); [v3.1 page](https://developers.tripo3d.ai/en/models/v3-1)
- **Extra fields only in MIG** (no reference-page entry): `priority` (1 to 3, entitlement-gated, error 2013), `parameters`, `return_multiview`, `render_sequence`, `render_video`, `check_printable` ("entitlement-gated"), `style_image`, plus aliases `model_version`, `image_autofix`, `file`, `files`, `original_model_task_id`. MIG also says unknown extra fields are forwarded rather than rejected. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- P1 rejects `quad`, `smart_low_poly`, `generate_parts`, `geometry_quality` if present at all, even explicit `false`, on the international service. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

#### `POST /v3/generation/image-to-splat`
- Params: `input` (`file_token` or URL; PNG, JPEG, WebP; max 20 MB), `model_seed`. Output `model_url` (`.splat`). Fixed **30 credits**, about 4 minutes. — [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-splat)
- Not a mesh: no texture, rig or convert downstream. — [CLI generate.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)

#### `POST /v3/generation/text-to-image` and `image-to-image`

| Parameter | Text | Image | Rules |
|---|---|---|---|
| `model` | default `seedream_v4` | default `seedream_v5` | `seedream_v5`, `seedream_v4` (text only), `banana`, `banana_pro`, `banana2`, `chat_image_1` (retiring 2026-10-23), `chat_image_1.5` (retiring 2026-12-01), `chat_image_2`, `chat_image_2.5_flare`, `chat_image_2.5_sunburst` |
| `prompt` | required | conditional (required with no template) | Recommended up to 300 Chinese characters or 600 English words; negative after `--no` |
| `input` | | required | URL, `file_token` or `task_id`. `jpeg`, `png` recommended (`webp` rejected on some routes); max 20 MB; max 36 MP; min 14 px; aspect 1/3 to 3 |
| `inputs` | | optional | Max 4 (seedream), 10 (banana), 16 (chat_image); referenced as `image[1]`, `image[2]` |
| `size` | yes | yes | Varies by model, see below; default `2048x2048` |
| `quality` | yes | yes | `chat_image_2`: low, medium, high. 2.5: also xhigh, max. Any other model returns an error; default low |
| `background` | yes | yes | 2.5 only: auto, opaque, transparent (needs PNG) |
| `aspect_ratio` | yes | yes | Banana only: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9; banana2 adds 1:8, 1:4, 4:1, 8:1 |
| `output_format` | yes | yes | `png` (default), `jpeg` |
| `watermark` | yes | | Default false; seedream only. Banana always embeds an invisible watermark |
| `template` | `asset_extraction`, `character_completion`, `t_pose`, `variants`, `figure` | `t_pose`, `character_completion`, `3d_enhance`, `variants`, `figure` | Generation templates |

Sources: [text-to-image](https://developers.tripo3d.ai/en/docs/generation-text-to-image); [image-to-image](https://developers.tripo3d.ai/en/docs/generation-image-to-image). Output `generated_image_url`.

- Sizes: seedream_v5 is `2K`/`3K` or WxH at 3.69 to 10.40 MP, aspect 1:16 to 16:1. seedream_v4 is `2K`/`4K` or WxH at about 3.69 to 16.78 MP. banana has fixed sizes only. banana_pro is `1K`/`2K`/`4K` or WxH. banana2 is `0.5K`/`1K`/`2K`/`4K`. chat_image_2 and 2.5 accept presets or custom WxH (edges up to 3840, multiples of 16, long edge up to 3x short, 655,360 to 8,294,400 px). These appear in tabs on the rendered page and are absent from the `.md` version. — [rendered text-to-image](https://developers.tripo3d.ai/en/docs/generation-text-to-image)
- Note: MIG says the prompt limit for image generation is 1800 chars. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

| Image model (credits) | up to 1K | 2K | 4K |
|---|---|---|---|
| `seedream_v5` / `seedream_v4` | 5 | 5 | 5 |
| `banana` | 5 | n/a | n/a |
| `banana2` | 10 | 10 | 15 |
| `banana_pro` | 15 | 15 | 20 |
| `chat_image_1` (retiring 2026-10-23) | 5 | n/a | n/a |
| `chat_image_1.5` (retiring 2026-12-01) | 10 | n/a | n/a |
| `chat_image_2`, `chat_image_2.5_*` (low, medium) | 10 | 10 | 15 |
| `chat_image_2` · high, `2.5_*` · high | 20 | 25 | 40 |
| `2.5_*` · xhigh | 25 | 30 | 45 |
| `2.5_*` · max | 30 | 50 | 50 |

— [PRICE](https://developers.tripo3d.ai/en/pricing). When `size` is auto, the 2K tier applies. — [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/generation/image-to-multiview` and `edit-multiview`
- image-to-multiview: `input` (`file_token` or URL; PNG, JPEG, WebP). Output `generate_multiview_image.{front,left,back,right}_view_url`. **10 credits.** — [DOC](https://developers.tripo3d.ai/en/docs/generation-image-to-multiview); [PRICE](https://developers.tripo3d.ai/en/pricing)
- edit-multiview: `input` (a successful image-to-multiview task ID), `prompts` (1 to 4 items of `{prompt` up to 1024 chars, `view` front/left/back/right`}`). **5 credits per edited image.** — [DOC](https://developers.tripo3d.ai/en/docs/generation-edit-multiview); [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/openai/images/generations` and `/edits`
- Base `https://openapi.tripo3d.ai/v3/openai`. Models only `gpt-image-2`, `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`. Params `model`, `prompt`, `image`/`images` (edits), `size`, `quality`, `background`, `output_format`, `n` (must be 1), `response_format` (`url` only), `stream` (not supported), `mask` (PNG with alpha, up to 20 MiB; input capped at 10 MiB). — [DOC](https://developers.tripo3d.ai/en/docs/openai-compat-images)
- Synchronous: 20 to 80 s typically; after 240 s a 400 `generation_in_progress` with the task ID in `X-Tripo-Task-Id`. Same credits as native. — [DOC](https://developers.tripo3d.ai/en/docs/openai-compat-images)

#### `POST /v3/models/texture`
Params: `input` (task ID, `file_token`, URL; GLB, GLTF, FBX, OBJ, STL; max 150 MB); `model` (default `v3.0-20250812`; `v3.5-20260815`; `v2.5-20250123`); `texture_prompt` (`text` with optional `style_image`, or `image`, or `images` with front required and at least 2 views); `pbr` (true); `texture_seed`; `texture_alignment`; `texture_quality`; `part_names`; `compress`; `bake` (true); `delight` (true, v3.5 only). Output `model_url`, `rendered_image_url`. — [DOC](https://developers.tripo3d.ai/en/docs/models-texture)

Credits: fast 10, standard 10, HD 20, 8K 30. — [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/models/convert`

| Parameter | Default | Values and rules | Triggers 10-credit price? |
|---|---|---|---|
| `input` | required | Task ID or `file_token` per the intro line; the bullets also list URL. GLB, GLTF, FBX, OBJ, STL; max 150 MB | |
| `format` | required | `GLTF`, `FBX`, `USDZ`, `OBJ`, `STL`, `3MF` | |
| `quad` | false | "will force the output format to FBX" | Yes |
| `force_symmetry` | false | Only with `quad` | |
| `face_limit` | keep original | Range not stated | Yes |
| `flatten_bottom` | false | Flatten bottom of model | Yes |
| `flatten_bottom_threshold` | 0.01 | Depth | Yes |
| `texture_size` | 4096 | Diffuse size in px | Yes |
| `texture_format` | JPEG | JPEG, PNG, WEBP, BMP, DPX, HDR, OPEN_EXR, TARGA, TIFF | Yes |
| `bake` | true | Bake advanced materials | |
| `pack_uv` | false | Unified UV layout | |
| `export_vertex_colors` | false | OBJ and GLTF only | |
| `pivot_to_center_bottom` | false | Pivot to bottom center | Yes |
| `scale_factor` | 1 | Scale multiplier | Yes |
| `with_animation` | true | Skeleton and animation | |
| `animate_in_place` | false | | |
| `part_names` | | Parts to export | |
| `export_orientation` | `+x` | `+x`, `-x`, `-y`, `+y` | |
| `fbx_preset` | `blender` | `blender`, `3dsmax`, `mixamo`, `bake_scale` | |

— [DOC convert](https://developers.tripo3d.ai/en/docs/models-convert). Basic 5 credits, advanced 10 credits when any non-default value of the marked parameters is used. — [PRICE](https://developers.tripo3d.ai/en/pricing). Output `model_url`, `rendered_image_url`. — [DOC convert](https://developers.tripo3d.ai/en/docs/models-convert)

- MIG adds `assemble_animation`, not on the reference page. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Legacy notes (not repeated on the current page): OBJ, STL, 3MF "Not supported with rigged models"; "GLTF and STL don't support storing quad faces", and quad will still retopologize but store triangles; textures are not retained for STL; a second conversion after a first supports only `format`; default `face_limit` 10000. — [LEGACY conversion](https://docs.tripo3d.ai/export/conversion.html). The quad note differs from the current page's flat "force FBX" line, and the default `face_limit` differs from the current page's "original face count is preserved".

#### `POST /v3/models/import`
Param `input` (`file_token` or URL; GLB, GLTF, FBX, OBJ, STL; max 150 MB). Output `model_url`, `rendered_image_url`, `normalize_scale`, `normalize_translation`. Tripo normalizes imported models and "the platform's output keeps the normalized result". The same fields come back on post-processing tasks whose input is a file or URL. — [DOC import](https://developers.tripo3d.ai/en/docs/models-import). Credits: not on the current pricing page; "Free" on the legacy one. — [PRICE](https://developers.tripo3d.ai/en/pricing); [LEGACY pricing](https://docs.tripo3d.ai/get-started/pricing.html)

#### `POST /v3/mesh/decimate` (Retopology)
Params: `input`; `model` (`v3.0`, `v2.0` default, `v1.0`; legacy `P-…` values normalized per MIG); `face_limit` (conditional); `quad`; `smart_uv` (v3.0 only, else 400/1004, no extra cost, no atlas image); `bake` (true, not v1.0); `part_names` (not v1.0). Output `model_url`, `rendered_image_url`. — [DOC](https://developers.tripo3d.ai/en/docs/mesh-decimate); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

- v3.0 `face_limit`: 500 to 20,000 triangles, 500 to 10,000 quads; omit for adaptive. — [DOC changelog](https://developers.tripo3d.ai/en/docs/changelog). v2.0 same window. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Credits: v3.0 triangle 35, v3.0 quad 40, v2.0 30, v1.0 10. — [PRICE](https://developers.tripo3d.ai/en/pricing). Legacy states +5 for quad on the mesh task; the current page is silent for v2.0 and v1.0. — [LEGACY smart low poly](https://docs.tripo3d.ai/mesh-editing/smart-low-poly-p-v2-0-20251225.html)

#### `POST /v3/mesh/segment`
Params: `input`; `model` (`v1.0-20250506` default, geometry-based; `v2.0-20260430` Beta, semantic); `segmentation_granularity` (v2: simple, balanced, detailed); `split_by_connectivity` (v2, true); `ref_image` (v2; overrides the previous two). Output `model_url`, `rendered_image_url`. **40 credits.** — [DOC](https://developers.tripo3d.ai/en/docs/mesh-segment); [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/mesh/complete`
Params: `input` (a `mesh/segment` task ID only); `model` (`v1.0-20250506`); `part_names`; `completion_mode` (`ai_completion` default; `quick_cap` = "Fast sealing of open boundaries without AI generation"). Output `model_url`, `rendered_image_url`. **50 credits default, 30 quick cap.** — [DOC](https://developers.tripo3d.ai/en/docs/mesh-complete); [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/mesh/smartsegment`
Params: `seg_type` (required: `image`, or `model` for GLB only); `input` (`file_token` or URL); `granularity` (coarse, medium default, fine); `hint`; `transform` (required for `model`: 16-float column-major matrix). Output `prompt`, `mask_url`, `seg_model_url`, `seg_task_id`, `model_task_id`. **85 credits image, 55 model.** — [DOC](https://developers.tripo3d.ai/en/docs/mesh-smartsegment); [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/mesh/uv`
Params: `input` (max 80,000 equivalent triangles; larger tasks fail and refund); `model` (`default`); `bake` (true); `export_orientation`; `compress`. Output `model_url`, `uv_render_url`. **20 credits.** — [DOC](https://developers.tripo3d.ai/en/docs/mesh-uv); [PRICE](https://developers.tripo3d.ai/en/pricing)

#### `POST /v3/animations/rig-check`, `rig`, `retarget`
- rig-check: `input` (GLB, FBX, OBJ, STL; max 150 MB). Output `riggable`, `rig_type`. **Free.** — [DOC](https://developers.tripo3d.ai/en/docs/animations-rig-check); [PRICE](https://developers.tripo3d.ai/en/pricing)
- rig: `input`; `model` (`v1.0-20240301` default, `v2.5-20260210`, `v3.0-20260909`); `rig_type` (biped default, quadruped, hexapod, octopod, avian, serpentine, aquatic; `others` needs v3.0); `spec` (tripo default, mixamo; actorcore, unity, unreal, vrm need v3.0; biped only); `out_format` (glb, fbx). Output `model_url`. **25 credits.** — [DOC](https://developers.tripo3d.ai/en/docs/animations-rig); [rig page](https://developers.tripo3d.ai/en/models/rig)
- retarget: `input` (rigged task ID); `animation` or `animations` (up to 5); `out_format`; `export_with_geometry` (true); `animate_in_place` (false); `bake_animation` (deprecated, ignored). 16 presets for v2.5/v3.0 rigs and 90+ biped presets for v1.0 rigs. **10 credits per animation.** — [DOC](https://developers.tripo3d.ai/en/docs/animations-retarget); [animation page](https://developers.tripo3d.ai/en/models/animation)

#### Tasks, files and account
- `GET /v3/tasks/{task_id}` returns `task_id`, `type`, `status`, `progress`, `error_code`, `error_message`, `output`, `credits_consumed`, `created_at`, `completed_at`. — [DOC](https://developers.tripo3d.ai/en/docs/task-query)
- `POST /v3/tasks/list`: `task_ids` (max 100); returns `tasks` map and `missed`. — [DOC](https://developers.tripo3d.ai/en/docs/task-batch-query)
- `POST /v3/files`: multipart `file`; returns `file_token`. Images JPEG, PNG up to 20 MB. Models GLB, GLTF, FBX, OBJ, STL up to 150 MB. — [DOC](https://developers.tripo3d.ai/en/docs/files)
- `POST /v3/files/presign`: `format` (`jpeg`, `jpg`, `png`, `webp`, `bmp`, `tiff`; `glb`, `gltf`, `fbx`, `obj`, `stl`, `3mf`, `usdz`); returns `presigned_url`, `file_token`, `expires_in`, then HTTP PUT without auth; recommended above 60 MB. — [DOC](https://developers.tripo3d.ai/en/docs/files-presign)
- `GET /v3/account/balance`: `balance`, `frozen`. `GET /v3/account/usage`: rows of `task_id`, `type`, `credits_consumed`, `created_at`. — [DOC](https://developers.tripo3d.ai/en/docs/account). Pagination `?limit=&offset=` (limit up to 200) is in MIG only. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Upload conflicts: MIG says `POST /v3/files` allows up to 200 MB and also webp, bmp, tiff, 3mf, usdz; the docs and Python SDK say 150 MB. MIG and the Python SDK call the presign field `upload_url`; the docs call it `presigned_url`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [SDK API.md](https://raw.githubusercontent.com/Tripo-Developer/tripo-python-sdk/v1.0.0/docs/API.md); [DOC](https://developers.tripo3d.ai/en/docs/files-presign)

### Inferences
- Image-to-3D with H3.1, standard PBR texture, is 30 credits (US$0.30), and with bare geometry 20 credits (US$0.20). With `geometry_quality=detailed` and `texture_quality=detailed` it is 60 credits (US$0.60). Computed from the published add-ons.
- A preview with bare geometry on H3.1 followed by a higher-quality regeneration costs each as a separate full task, since refine is retired and no upgrade-pricing mechanism is documented.
- P1 detailed and 8K prices would be 50/60 (text) and 60/70 (image/multiview) if P2's add-ons "match P1" as the footnote says. No page prints those P1 numbers.

### Gaps
- Exact resolution of `standard` and `detailed` output textures: not documented on current pages. Only `extreme` = 8K is stated. A legacy page describes `detailed` as a 4K upscale in one combination. — [LEGACY Turbo page](https://docs.tripo3d.ai/model-generation/image-to-model-turbo-v1-0-20250506.html)
- Range of `face_limit` on convert: not documented. A ComfyUI node exposes -1 to 500,000 but the page says this does not represent per-version limits for generation nodes. — [DOC ComfyUI](https://developers.tripo3d.ai/en/docs/comfyui-nodes)
- When `face_limit` is required on decimate (marked "Conditional"), and the v1.0 range: not documented.
- `image-to-depth` price: not documented.

---

## Which model versions exist, and what differs by version?

### Takeaway
Current 3D model IDs are `v3.1-20260211`, `v3.0-20250812`, `v2.5-20250123` (H series), `P2-20260801` and `P1-20260311` (P series). Turbo, v1.x and v2.0 are retired. H-series reaches 2,000,000 triangles; P-series tops out at 50,000.

### Cited Findings

| Model ID | Tripo's description | Max faces | Texture default | Notes | Source |
|---|---|---|---|---|---|
| `v3.1-20260211` | "latest high-precision"; recommended use includes "3D printing & flexible manufacturing" | 1,500,000 triangles; 2,000,000 with Ultra; quad 150,000 | `v3.0-20250812` | | [models](https://developers.tripo3d.ai/en/docs/models-and-versions); [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard) |
| `v3.0-20250812` | Previous generation | 1,000,000; 2,000,000 Ultra; quad 150,000 | `v3.0-20250812` | | same |
| `v2.5-20250123` | Legacy | 500,000; no Ultra | `v2.5-20250123` | `geometry_quality`, `texture_quality`, `auto_size`, `quad`, `smart_low_poly`, `generate_parts`, `compress` are valid only at v3.0 and above | same |
| `P2-20260801` | Native quad topology | 48 to 50,000 triangles; 48 to 25,000 quads | `v3.0-20250812` | Recommended starting face counts: 150 simple, 250 complex | [P2 page](https://developers.tripo3d.ai/en/models/p2); [image P](https://developers.tripo3d.ai/en/docs/generation-image-to-model/p) |
| `P1-20260311` | Low-poly | 50 to 20,000 (MIG: 48 to 20,000 international) | `v3.0-20250812` | No quad, parts, smart low poly, geometry quality | [models](https://developers.tripo3d.ai/en/docs/models-and-versions); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |

- With `smart_low_poly`, face limits are fixed: triangle 500 to 20,000, quad 500 to 10,000. — [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard)
- Retired: `v1.3-20240522`, `v1.4-20240625`, `v2.0-20240919`, `Turbo-v1.0-20250506`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md). The legacy host still has pages for Turbo and v1.4. — [LEGACY Turbo](https://docs.tripo3d.ai/model-generation/image-to-model-turbo-v1-0-20250506.html)
- Other model families: texture `v3.5-20260815`, `v3.0-20250812` (default), `v2.5-20250123`; rig `v3.0-20260909`, `v2.5-20260210`, `v1.0-20240301` (default; `v2.0-20250506` rejected); segmentation `v1.0-20250506` (default), `v2.0-20260430` Beta; completion `v1.0-20250506`; retopology `v3.0`, `v2.0` (default), `v1.0`. — [texture page](https://developers.tripo3d.ai/en/models/texture); [DOC rig](https://developers.tripo3d.ai/en/docs/animations-rig); [DOC segment](https://developers.tripo3d.ai/en/docs/mesh-segment); [DOC complete](https://developers.tripo3d.ai/en/docs/mesh-complete); [DOC decimate](https://developers.tripo3d.ai/en/docs/mesh-decimate); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Docs recommend pinning a specific version in production. — [models](https://developers.tripo3d.ai/en/docs/models-and-versions)

### Inferences
- The competitor configuration you described (`faceLimit` 300k or 1.2M, image-to-3D, PBR GLB) falls inside the H-series limits: 300k fits v3.1, v3.0 and v2.5 at standard quality, and 1.2M fits v3.1 at standard quality or v3.0 with Ultra. It does not fit the P series.

### Gaps
- Whether texture v3.5 will become a default: not documented. The rig and texture pages only state that defaults are unchanged for now.

---

## What are the error codes, statuses, URL expiry and input limits?

### Takeaway
There are five documented task statuses and a request-level error table. **The output URL lifetime is genuinely contradictory across official sources (60 seconds, 5 minutes, about 24 hours)**, while the current docs say only "temporary", so a safe integration has to assume short life and download immediately.

### Cited Findings

**Task statuses**
- `queued`, `running`, `success`, `failed`, `cancelled`. Internal `banned` and `expired` are reported as `failed`; legacy responses should be treated as terminal; `unknown` may occur and should not be treated as terminal. — [DOC lifecycle](https://developers.tripo3d.ai/en/docs/task-lifecycle); [DOC task query](https://developers.tripo3d.ai/en/docs/task-query)
- Recommended polling: every 1 to 2 s, with a timeout (example 5 minutes). — [DOC lifecycle](https://developers.tripo3d.ai/en/docs/task-lifecycle)

**Request-level error codes** — [DOC errors](https://developers.tripo3d.ai/en/docs/error-handling)

| Code | HTTP | Meaning |
|---|---|---|
| 2 | 401 | Authentication missing or invalid |
| 1000, 1001 | 500 | Unknown / fatal server error |
| 1002 | 401 | Authentication failed |
| 1003 | 400 | Malformed body |
| 1004 | 400 | Invalid or missing parameter |
| 1007 | 429 | Rate limit exceeded |
| 2000 | 429 | Concurrency limit (see `Retry-After`) |
| 2001 | 404 | Task not found |
| 2002 | 400 | Unsupported task type |
| 2003 | 400 | Empty input file |
| 2004 | 400 | Unsupported file type |
| 2008 | 400 | Content policy violation |
| 2010 | 403 | Insufficient credits |
| 2015 | 400 | Version deprecated |
| 2018 | 400 | Model too complex to remesh |
| 4001 | 404 | Endpoint not found |

- "These request-level `code` values differ from a failed task's `error_code`; the same number can mean something else." — [DOC errors](https://developers.tripo3d.ai/en/docs/error-handling). For example, on tasks 2008 = moderation and 2018 = timed out in queue. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Legacy-only codes: 1005, 2005, 2006, 2007, 2009, 2011 to 2014, 2016, 2017, 2019. — [LEGACY errors](https://docs.tripo3d.ai/get-started/errors-and-error-handling.html). MIG also mentions 2021/2022 size limits. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

**Rate and concurrency limits**
- Headers `X-RateLimit-Limit`, `-Remaining`, `-Reset`; rate limits are per API key. — [DOC limits](https://developers.tripo3d.ai/en/docs/rate-limits)
- Concurrency by account and category: H generation 10; P generation 5; **image generation 1**; animation 10; model processing 5; mesh operations 10. Can be raised via support. — [DOC limits](https://developers.tripo3d.ai/en/docs/rate-limits)
- Per-minute quotas (about 200 generations/min, 10 uploads/min) are in MIG only. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

**Output URL expiry: conflict**

| Claim | Source |
|---|---|
| "Generated model URLs are temporary"; do not store as a permanent asset (no duration) | [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk) |
| "signed and valid ~24 hours in both V2 and V3" | [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| "by default expires after five minutes" | [LEGACY task query](https://docs.tripo3d.ai/task-query/get-your-task-result.html) |
| "the download link is valid for 60 seconds" | [LEGACY FAQ](https://docs.tripo3d.ai/other/support-faq.html) |
| "Output URLs expire in ~5 minutes" | [CLI common-errors.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) |

- Re-querying the task gives fresh URLs. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk)
- `task` must be queried with the same API key that created it, per legacy docs. — [LEGACY task query](https://docs.tripo3d.ai/task-query/get-your-task-result.html)
- Download domain (international): `tripo-data.rg1.data.tripo3d.com`. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

**Input limits summary**
- Generation images: PNG, JPEG, WebP; max 20 MB; recommended at least 256×256. — [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard)
- Base64 / `data:` input is rejected; request body limit 20 MB. — [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Model inputs: GLB, GLTF, FBX, OBJ, STL; max 150 MB. — [DOC import](https://developers.tripo3d.ai/en/docs/models-import)
- Note: `POST /v3/files` lists images as JPEG and PNG only, while generation accepts WebP. — [DOC files](https://developers.tripo3d.ai/en/docs/files)
- `file_token` lifetime: not guaranteed; "do not rely on" `expires_in`. — [DOC presign](https://developers.tripo3d.ai/en/docs/files-presign). "File tokens are short-lived" per the CLI, and v2 tokens were 24 h per MIG. — [CLI common-errors.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz); [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

### Inferences
- Because the sources disagree and the most authoritative current page gives no number, only the behaviour (download immediately, store your own copy, re-query for a fresh URL) is safe to rely on.

### Gaps
- Task and file retention on Tripo's side: not documented. The legacy FAQ literally contains the placeholder "Tripo will retain user inputs and generated data for XXX". — [LEGACY FAQ](https://docs.tripo3d.ai/other/support-faq.html)
- Rate limit values per endpoint: not published in the reference pages.

---

## What 3D-print-relevant capabilities are documented?

### Takeaway
High-poly output, STL and 3MF export, flatten-bottom, pivot and scale are all real, documented API features. **A watertight, manifold or solid guarantee is not documented anywhere in the API reference, and no printability check is publicly documented** beyond one line naming an entitlement-gated `check_printable` field in the migration guide. "Watertight" appears only as descriptive text in the CLI, whose print preset sends no watertight parameter.

### Cited Findings

| Capability | Status | Detail | Source |
|---|---|---|---|
| High poly 300k to 1.2M | **Documented** | v3.1 up to 1.5M standard; 2M with `geometry_quality=detailed`. v3.0 up to 1M; 2M Ultra. v2.5 up to 500k | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard) |
| Quad output | **Documented** | H v3.0+ up to 150k; P2 up to 25k; decimate and convert also offer it. Forces FBX on generation and convert | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [P2 page](https://developers.tripo3d.ai/en/models/p2); [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| GLB | **Documented** | Default output in examples (`model_pbr.glb`); no output-format parameter on generation | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard) |
| STL | **Documented, via convert** | "`STL` — 3D printing, geometry only" | [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| 3MF | **Documented, via convert; color claim conflicts** | International: "3D with single color", and "STL / 3MF — 3D printing, geometry only". CN page: "3D printing with color". Legacy: "only exports geometry". CLI: "The API's 3MF output is single color… Build the multi-color 3MF in your slicer" | [convert](https://developers.tripo3d.ai/en/docs/models-convert); [CN convert](https://developers.tripo3d.com/en/docs/models-convert); [LEGACY](https://docs.tripo3d.ai/export/conversion.html); [CLI print.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) |
| OBJ, FBX, USDZ, GLTF | **Documented, via convert** | Plus `export_vertex_colors` on OBJ and GLTF only | [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| PLY | **Not in the API** | Marketing names PLY for the Studio converter; the API `format` list omits it | [llms.txt](https://www.tripo3d.ai/llms.txt); [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Color printing route | CLI only | Texture on, then OBJ with vertex colors | [CLI print.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) |
| Pivot | **Documented** | `pivot_to_center_bottom` on convert only (10-credit tier) | [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Flat base | **Documented** | `flatten_bottom`, `flatten_bottom_threshold` on convert (10-credit tier) | [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Real-world size | **Partly** | `auto_size` scales to meters at generation; `scale_factor` is a multiplier on convert. No target-height or millimeter parameter documented | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Size of imported models | **Documented caveat** | Normalized; "the platform's output keeps the normalized result"; recover via `normalize_scale` | [import](https://developers.tripo3d.ai/en/docs/models-import) |
| Watertight / manifold / solid | **Not documented** | No parameter or guarantee in API reference pages (searched all downloaded pages for watertight, manifold, printab, solid, hollow, wall thick) | Search across [sidebar pages](https://developers.tripo3d.ai/en/docs/introduction) |
| "Watertight" wording | CLI only, descriptive | "Print asset: watertight output, STL, and a flat bottom". The preset actually sends only `texture=false`, `pbr=false`, then convert with `format=STL`, `flatten_bottom=true` | [DOC CLI](https://developers.tripo3d.ai/en/docs/cli); [CLI scenarios.js](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) |
| Printability tooling | **Named, not documented** | `check_printable` "entitlement-gated"; no description, output or price; not in the CLI or Python API doc | [MIG](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| Mesh repair | **Partly** | `mesh/complete` "repair missing regions", `quick_cap` seals open boundaries, but input must be a `mesh/segment` task. CLI recipe for holes: segment, complete, convert to STL (40 + 30 to 50 + 5 to 10 credits) | [complete](https://developers.tripo3d.ai/en/docs/mesh-complete); [CLI print.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz); [PRICE](https://developers.tripo3d.ai/en/pricing) |
| Geometry quality history | Legacy changelog | v3.0: "elimination of double-layer surface artifacts", reduced gaps or holes. v3.1: "up to 2M polygons for 3D printing" | [LEGACY changelog](https://docs.tripo3d.ai/get-started/changelog.html) |
| Low poly / remesh | **Documented** | `smart_low_poly`; P series; `mesh/decimate` capped at 20k triangles or 10k quads, so it cannot produce a high-poly remesh | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [changelog](https://developers.tripo3d.ai/en/docs/changelog) |
| Segmentation | **Documented** | `generate_parts` at generation (bare geometry only), `mesh/segment`, `mesh/smartsegment`; `part_names` on convert to export chosen parts | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [segment](https://developers.tripo3d.ai/en/docs/mesh-segment); [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Base / plinth generation | **Not documented** | No parameter adds a stand. `flatten_bottom` only flattens | [convert](https://developers.tripo3d.ai/en/docs/models-convert) |
| Style options | **Retired for 3D** | `stylize_model` retired. The old generation `style` parameter is absent from current pages. For images only, `template` includes `figure`, `t_pose`, `variants`, `character_completion`, `asset_extraction`, `3d_enhance`. No chibi option documented | [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk); [LEGACY changelog](https://docs.tripo3d.ai/get-started/changelog.html); [text-to-image](https://developers.tripo3d.ai/en/docs/generation-text-to-image); [image-to-image](https://developers.tripo3d.ai/en/docs/generation-image-to-image) |
| PBR on/off | **Documented** | `pbr` default true and forces `texture`; set both false for bare geometry; texture-only without PBR is possible with `pbr=false` | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard) |
| Multi-view input | **Documented** | 2 to 4 views, front required, or chained from a multiview task | [multiview H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard) |
| Seeds | **Documented** | `model_seed` gives "identical 3D mesh" with same input; `texture_seed`; `image_seed` (text) | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [text H](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard) |
| Reference image generation chain | **Documented** | `input` can be a `text_to_image`/`image_to_image` `task_id`; multiview `inputs` can reference a multiview task | [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [multiview H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard) |
| Regenerate higher quality from earlier 3D task | **Not available as such** | Refine is retired. Post-processing tasks take a 3D `task_id`, but none is documented as regenerating geometry at higher quality. New generation from the same image is a new task | [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk); [texture](https://developers.tripo3d.ai/en/docs/models-texture) |
| Retexture an existing mesh | **Documented** | `models/texture` with `task_id`, keeping geometry; docs "strongly recommend" re-supplying the reference image | [texture](https://developers.tripo3d.ai/en/docs/models-texture) |

**Kubo-flow facts (no recommendation)**
- Preview and final can both be `image-to-model` calls from the same stored image with different `model`, `face_limit`, `texture_quality`, each billed as a new task. — [image H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard); [PRICE](https://developers.tripo3d.ai/en/pricing)
- CLI's print recipe says "Textures are wasted credits for printing". — [CLI print.md](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)
- Legacy FAQ: inputs and generated models are not used for training. — [LEGACY FAQ](https://docs.tripo3d.ai/other/support-faq.html)

### Inferences
- Because no manifold guarantee is documented, mesh validity would have to be checked independently after download. This is an inference from the absence of documentation, not a finding about real output quality.
- Whether the same `model_seed` gives matching geometry at different `face_limit` values or between model versions is unknown. The docs promise identity only for "the same seed with the same input".
- A 2048² texture output, as the competitor uses, would need `convert` with `texture_size=2048` (advanced, 10 credits) if the generation output differs. The default standard output size is not documented, so this may not be needed.

### Gaps
- Actual watertightness rate of outputs: not documented and not testable under this assignment's no-API-call rule.
- `check_printable`: behaviour, availability and output not documented.
- Maximum print-ready file size or polygon count limit for STL/3MF conversion: not documented.
- Whether high-poly (1.2M) STL conversion has limits such as the 150 MB input cap on task-ID inputs: not documented.

---

## What did this inventory actually cover?

### Takeaway
**The full current navigation was verified**: all 43 pages linked from the rendered sidebar of `developers.tripo3d.ai` were downloaded, plus the sitemap-only OpenAI-compatible page. Coverage is not 100% read depth, however: four auxiliary pages were only partly read or searched, and the migration guide and legacy host were read selectively, as listed below.

### Cited Findings

**Navigation verification**
- Sidebar link list extracted from the rendered [mesh-decimate page](https://developers.tripo3d.ai/en/docs/mesh-decimate) and compared with downloaded files: no missing pages. Extras beyond the sidebar: `openai-compat-images` (in [sitemap](https://developers.tripo3d.ai/sitemap.xml)); `b2b-payment` and `invoice-guide` (China only, in [CN sitemap](https://developers.tripo3d.com/sitemap.xml)).
- Guessed URLs returned 404: `generation-image-to-depth`, `models-refine`, `models-stylize`, `files-upload-credentials`, `account-usage`, `task-cancel`, on the [docs host](https://developers.tripo3d.ai/en/docs/introduction).

**Read in full (`developers.tripo3d.ai/en/docs/*`, raw Markdown; for changelog, billing, introduction, models-and-versions and the two image-to-model pages, the full text was read from the CN corpus and the international differences from a diff)**
files, files-presign, account, task-query, task-batch-query, task-lifecycle, webhooks, error-handling, rate-limits, changelog, billing, introduction, models-and-versions, migration-v2-to-v3, models-texture, models-convert, models-import, mesh-decimate, mesh-segment, mesh-complete, mesh-smartsegment, mesh-uv, animations-rig-check, animations-rig, animations-retarget, generation-image-to-splat, generation-image-to-multiview, generation-edit-multiview, generation-text-to-image, generation-image-to-image, generation-image-to-model/standard, generation-image-to-model/p.

**Read by diff and parameter extraction against the image-to-model pages, not line by line**
generation-text-to-model/standard, generation-text-to-model/p, generation-multiview-to-model/standard, generation-multiview-to-model/p.

**Partly read or searched only**
- `sdk`: intro, route matrix, upgrade and troubleshooting read; language code samples skimmed.
- `cli`: command table, presets, agent notes read; rest searched by keyword.
- `quick-start`, `authentication`: first portions read.
- `openai-compat-images`: read through the first request example.
- `comfyui-nodes`, `plugins`, `codex-plugin`: keyword search only (these describe wrappers, not API surface).

**Other official pages read**
- [Pricing](https://developers.tripo3d.ai/en/pricing) (rendered text, plus P and Splat tabs from its JS bundle); [CN pricing](https://developers.tripo3d.com/en/pricing).
- [models index](https://developers.tripo3d.ai/en/models), [v3-1](https://developers.tripo3d.ai/en/models/v3-1), [p2](https://developers.tripo3d.ai/en/models/p2), [texture](https://developers.tripo3d.ai/en/models/texture), [rig](https://developers.tripo3d.ai/en/models/rig), [animation](https://developers.tripo3d.ai/en/models/animation), [support](https://developers.tripo3d.ai/en/support) (FAQ answers collapsed, so only titles were visible).
- [Migration SKILL.md](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md): read sections 0 to 5.3 and Appendix A common fields, A.1, A.5, A.6, part of A.7, B.3 to B.6. Webhook section 6, section 7 onward, and other appendix tables were seen through keyword search only.
- Rendered HTML cross-check of 5 pages: mesh-decimate, generation-text-to-image, generation-image-to-image, generation-image-to-model/standard, models-convert. This matters because the `.md` versions drop tabbed content, such as per-model image sizes.
- CN host: all pages downloaded and diffed for image-to-model, models-and-versions, changelog, billing, introduction, convert, decimate. `llms-full.txt` was read for the sections covering billing, changelog, intro, models and image-to-model.

**Legacy host `docs.tripo3d.ai` read**
[changelog](https://docs.tripo3d.ai/get-started/changelog.html), [errors](https://docs.tripo3d.ai/get-started/errors-and-error-handling.html), [rate limits](https://docs.tripo3d.ai/get-started/rate-limits.html), [task result](https://docs.tripo3d.ai/task-query/get-your-task-result.html), [upload STS](https://docs.tripo3d.ai/file-upload/upload-in-sts.html), [quick upload](https://docs.tripo3d.ai/file-upload/quick-upload-directly.html), [FAQ](https://docs.tripo3d.ai/other/support-faq.html), [conversion](https://docs.tripo3d.ai/export/conversion.html), [overview](https://docs.tripo3d.ai/get-started/overview.html), [pricing](https://docs.tripo3d.ai/get-started/pricing.html), [intro](https://docs.tripo3d.ai/get-started/introduction.html), Turbo and v1.4 image pages (Turbo truncated at about 4,500 characters), [smart low poly](https://docs.tripo3d.ai/mesh-editing/smart-low-poly-p-v2-0-20251225.html); H3 image page by keyword only.

**SDK and CLI cross-checks (secondary)**
[Python SDK API.md](https://raw.githubusercontent.com/Tripo-Developer/tripo-python-sdk/v1.0.0/docs/API.md) and `client.py` (keyword and `image_to_depth` only); [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) (`print.md` in full; `process.md`, `make.md`, `generate.md`, `common-errors.md`, `scenarios.js` by keyword). The package was unpacked as data and never executed. The docs now point SDKs to the `Tripo-Developer` GitHub org rather than `VAST-AI-Research`. — [DOC SDK](https://developers.tripo3d.ai/en/docs/sdk)

**Could not read, or did not read**

| Page | Reason |
|---|---|
| `platform.tripo3d.ai/docs/*` | Client-side shell; HTML has no content, and its bundle only references `/docs/introduction` and `/docs/termsAndPrivacy` routes. Treated as superseded, not verified as empty when run in a browser |
| [Support FAQ answers](https://developers.tripo3d.ai/en/support) | Collapsed client-side; only questions were visible |
| [Terms](https://developers.tripo3d.ai/en/terms), [Privacy](https://www.tripo3d.ai/privacy) | Out of scope; not read. Commercial licensing of outputs is therefore not covered here |
| Blog, cookbook, showcase | Not read; not API reference. Cookbook titles in the sitemap are about games, not printing |
| `/zh/` pages | Not read; English versions used |
| Legacy pages downloaded, not read: advanced and basic image generation, multiview image, retarget, rig v2.5, texture v3.0, import, mesh completion, mesh segmentation, pre-rig check, image-to-model v2.x; not downloaded: text and multiview version pages, P1 pages, rig v1.0 and v2.0, texture v2.5 | Superseded by v3 docs; prioritized out |
| `/en/models/p1` | Referenced by the CLI docs; not in the sitemap and not fetched |

### Inferences
- The endpoint list is high-confidence for what Tripo documents publicly, because three independent lists agree: sidebar, sitemap, and the docs' SDK route matrix. Undocumented or entitlement-gated features may exist beyond it, as `image-to-depth` and `check_printable` show.

### Gaps
- Nothing was validated against the live API, so conflicts noted above (URL expiry, `model` default, upload limits, presign field name, 3MF color, quad versus format on convert) remain unresolved.
- Doc pages have no per-page revision dates; the changelog's latest entry is 2026-10.
