# Meshy (meshy.ai) developer API: complete endpoint inventory (as read 2026-11-01)

Evidence labels used throughout:

- **[D]**: documented on an API doc page (`docs.meshy.ai/api/...`).
- **[OA]**: appears only in the official OpenAPI spec (https://docs.meshy.ai/openapi.json), not on the doc page. Official, but undescribed or thinly described.
- **[SDK]**: seen only in the official `meshy-dev/meshy-mcp-server` GitHub repo. Secondary cross-check.
- **[WEB]**: documented for the Meshy web app only (`docs.meshy.ai/webapp/...`). This does not prove API behaviour.
- **[SITE]**: marketing page (`www.meshy.ai/api`, `www.meshy.ai/pricing`).
- **Not documented**: I looked for it in the sources in the coverage section and did not find it.

Doc pages are cited by canonical URL. Their text was read from `llms-full.txt`, which [Meshy says](https://docs.meshy.ai/api/ai) is regenerated on every docs build, so it matches the HTML docs.

---

## What is the complete list of HTTP endpoints (method + path + version + base URL)?

### Takeaway

Meshy documents **173 concrete HTTP operations**. 83 are in the OpenAPI spec, 5 are Text to Motion and 85 are Creative Lab (the last two groups are documented on pages only). Nearly all are async task families with the same five routes: create, get, list, delete, SSE stream. There are dedicated 3D-print routes (`/print/analyze`, `/print/repair`, `/print/multi-color`, `/print/split`) plus 9 "Creative Lab" print-product APIs.

### Cited Findings

**Base URL and conventions**

- Base URL is `https://api.meshy.ai/openapi` — [OpenAPI](https://docs.meshy.ai/openapi.json); the [API overview](https://docs.meshy.ai/en/api) gives `https://api.meshy.ai` with `/openapi/...` in each path.
- Auth is `Authorization: Bearer msy_...`. All endpoints are JSON REST. A `POST` that creates a task returns `202 {"result":"<task_id>"}` — [Authentication](https://docs.meshy.ai/api/authentication), [Errors](https://docs.meshy.ai/api/errors).
- The OpenAPI spec's own scope note says it leaves out Creative Lab and Text to Motion, and also "Endpoints still in development, partner-specific surfaces (creative-lab, d5), and legacy `/v1`,`/v2` path aliases" — [OpenAPI info.description](https://docs.meshy.ai/openapi.json).
- The legacy `/v2/text-to-3d` path (no `/openapi` prefix) is deprecated with no removal date. It returns `Deprecation` and `Link` headers — [Changelog Sep 29 2026](https://docs.meshy.ai/api/changelog), [Deprecations](https://docs.meshy.ai/api/deprecations).

**Standard task families**

Each row has all five routes: `POST <path>`, `GET <path>` (list), `GET <path>/:id`, `DELETE <path>/:id`, `GET <path>/:id/stream`. Paths are relative to `https://api.meshy.ai`.

| Family | Path | Version | Doc |
|---|---|---|---|
| Text to 3D (preview and refine share one POST) | `/openapi/v2/text-to-3d` | v2 | https://docs.meshy.ai/api/text-to-3d |
| Image to 3D | `/openapi/v1/image-to-3d` | v1 | https://docs.meshy.ai/api/image-to-3d |
| Multi-Image to 3D | `/openapi/v1/multi-image-to-3d` | v1 | https://docs.meshy.ai/api/multi-image-to-3d |
| Retexture | `/openapi/v1/retexture` | v1 | https://docs.meshy.ai/api/retexture |
| Remesh | `/openapi/v1/remesh` | v1 | https://docs.meshy.ai/api/remesh |
| Convert | `/openapi/v1/convert` | v1 | https://docs.meshy.ai/api/convert |
| Resize | `/openapi/v1/resize` | v1 | https://docs.meshy.ai/api/resize |
| UV Unwrap | `/openapi/v1/uv-unwrap` | v1 | https://docs.meshy.ai/api/uv-unwrap |
| Rigging | `/openapi/v1/rigging` | v1 | https://docs.meshy.ai/api/rigging |
| Animation (plus library route below) | `/openapi/v1/animations` | v1 | https://docs.meshy.ai/api/animation |
| Text to Motion (not in OpenAPI) | `/openapi/v1/text-to-motion` | v1 | https://docs.meshy.ai/api/text-to-motion |
| Text to Image | `/openapi/v1/text-to-image` | v1 | https://docs.meshy.ai/api/text-to-image |
| Image to Image | `/openapi/v1/image-to-image` | v1 | https://docs.meshy.ai/api/image-to-image |
| Multi-Color Print | `/openapi/v1/print/multi-color` | v1 | https://docs.meshy.ai/api/multi-color-print |
| Analyze Printability | `/openapi/v1/print/analyze` | v1 | https://docs.meshy.ai/api/analyze-printability |
| Repair Printability | `/openapi/v1/print/repair` | v1 | https://docs.meshy.ai/api/repair-printability |
| Auto Split | `/openapi/v1/print/split` | v1 | https://docs.meshy.ai/api/auto-split |

**Non-task endpoints**

| Method + path | Purpose | Cost | Doc |
|---|---|---|---|
| `GET /openapi/v1/animations/library` | Preset animation catalog with filters | Free | https://docs.meshy.ai/api/animation |
| `GET /openapi/v1/balance` | Credit balance | Free | https://docs.meshy.ai/api/balance |
| `GET /openapi/v1/usage/tasks` | Usage export (Studio and Enterprise teams only, otherwise `403`) | Free | https://docs.meshy.ai/api/usage |

**Creative Lab (print-product APIs; not in OpenAPI)**

Product-scoped and versioned per product. The two-stage products each have 10 concrete routes:

- `POST .../v1/prototype`
- `POST .../v1/build`
- `GET .../v1/{prototype|build}` (list)
- `GET .../v1/{prototype|build}/:id`
- `DELETE .../v1/{prototype|build}/:id`
- `GET .../v1/{prototype|build}/:id/stream`

The stage in the path must match the task, otherwise `404`.

| Product | Prefix | Doc |
|---|---|---|
| Keychain | `/openapi/creative-lab/keychain/v1` | https://docs.meshy.ai/api/creative-lab-keychain |
| Fridge Magnet | `/openapi/creative-lab/fridge-magnet/v1` | https://docs.meshy.ai/api/creative-lab-fridge-magnet |
| Figure (chibi) | `/openapi/creative-lab/figure/v1` | https://docs.meshy.ai/api/creative-lab-figure |
| Vinyl Figure | `/openapi/creative-lab/vinyl-figure/v1` | https://docs.meshy.ai/api/creative-lab-vinyl-figure |
| Brick Figure | `/openapi/creative-lab/brick-figure/v1` | https://docs.meshy.ai/api/creative-lab-brick-figure |
| Lamp | `/openapi/creative-lab/lamp/v1` | https://docs.meshy.ai/api/creative-lab-lamp |
| Keycap | `/openapi/creative-lab/keycap/v1` | https://docs.meshy.ai/api/creative-lab-keycap |
| Fidget Pixel | `/openapi/creative-lab/fidget-pixel/v1` | https://docs.meshy.ai/api/creative-lab-fidget-pixel |
| Collapsible Fidget (single stage: `POST`, list `GET`, `GET /:id`, `DELETE /:id`, `GET /:id/stream`, directly under the prefix) | `/openapi/creative-lab/fidget-collapsible/v1` | https://docs.meshy.ai/api/creative-lab-fidget-collapsible |

**Other documented data URL**

- `https://api.meshy.ai/web/public/animations/resources` is named as a public JSON catalog of animations — [Animation Library](https://docs.meshy.ai/api/animation-library). It is under `/web/public`, not `/openapi`. I did not call it.

**Retired or absent**

- Text to Voxel API: retired Oct 1 2025, no replacement — [Deprecations](https://docs.meshy.ai/api/deprecations).
- Text to Texture API: retired Jul 1 2025, replaced by Retexture — [Deprecations](https://docs.meshy.ai/api/deprecations).
- Webhooks have **no management API**. They are created only on the Developer Platform page — [Webhooks](https://docs.meshy.ai/api/webhooks). The OpenAPI spec defines no webhook operations — [OpenAPI](https://docs.meshy.ai/openapi.json).
- Web-app features with no API endpoint in the sources read: 3D Agent, Scene Compose, Video Generation, Texture Edit brush, Batch Images to 3D, slicer "Send to Printer", DXF export — [webapp docs](https://docs.meshy.ai/webapp/guides/choosing/integration), [Export formats](https://docs.meshy.ai/webapp/guides/platform/export-formats), [3D printing platforms](https://docs.meshy.ai/webapp/3d-printing-platforms/introduction).
- Slicer integration from code exists only as a local MCP tool. `meshy_send_to_slicer` finds locally installed slicers and "doesn't call the Meshy API" — [AI integration](https://docs.meshy.ai/api/ai).

**Count check**

- OpenAPI lists 83 operations (17 families minus Text to Motion = 16 × 5 = 80, plus library, balance, usage) — [OpenAPI](https://docs.meshy.ai/openapi.json). I enumerated these programmatically.
- Documentation headings total 142 with the `(prototype|build)` routes collapsed and Text to 3D POST counted twice (preview, refine). This reconciles with 83 + 5 + 53 + 1 — [llms-full.txt](https://docs.meshy.ai/llms-full.txt).

### Inferences

- With the Creative Lab routes expanded by stage, the total is 83 + 5 + (8 × 10) + 5 = 173. This is my arithmetic. Meshy does not publish a total.

### Gaps

- **"On v2" for printability.** [Task Lifecycle](https://docs.meshy.ai/api/task-lifecycle) says "On v2, Repair Printability and Analyze Printability always run the thin-wall check. On v1, they run it when you send a printer type or a print size." No v2 print route appears in OpenAPI, on the print pages, in the changelog, or in the MCP server printing source [SDK]. A v2 print path is **not documented** beyond that sentence.
- **Enterprise-only endpoints.** [meshy.ai/api](https://www.meshy.ai/api) advertises "Access to enterprise-only API endpoints" without naming them [SITE]. The OpenAPI note also mentions a partner surface "d5" and in-development endpoints. All **not documented** publicly, so this inventory cannot be proven to be 100% of what exists. It is 100% of what the public docs list.

---

## For each endpoint: purpose, parameters, response, formats, cost and doc URL

### Takeaway

Generation endpoints share a large parameter set whose validity depends on `ai_model`. Prices are flat per request, with add-ons only for texture resolution, Ultra geometry and animation count. Every create is async. Some request fields exist only in OpenAPI (notably `seed` and `negative_prompt` on Text to 3D) and have no page documentation.

### Cited Findings

#### Routes shared by every standard family

Exceptions are noted per family.

- **`GET <path>/:id`** returns the task object. Sends `Retry-After` while the task is `PENDING` or `IN_PROGRESS` — [Rate limits](https://docs.meshy.ai/api/rate-limits).
- **`GET <path>`** (list): `page_num` (default 1), `page_size` (default 10, max 100), `sort_by` (`+created_at` or `-created_at`) — [Text to 3D](https://docs.meshy.ai/api/text-to-3d). Text to Image and Image to Image list **both** task types — [Text to Image](https://docs.meshy.ai/api/text-to-image). API tasks do not appear in web-app My Assets — [Rigging](https://docs.meshy.ai/api/rigging).
- **`DELETE <path>/:id`**: `PENDING` is deleted and refunded. `IN_PROGRESS` returns `409 Conflict` and keeps running. A final-status task is deleted with no refund. Returns `200` with an empty body — [Text to 3D](https://docs.meshy.ai/api/text-to-3d), [Changelog Sep 11 2026](https://docs.meshy.ai/api/changelog).
- **`GET <path>/:id/stream`** is SSE. `event: message` carries the full task object, `event: error` carries `{status_code, message}`. A stream can close before the task ends, so reconnect or poll — [Text to 3D](https://docs.meshy.ai/api/text-to-3d), [Task Lifecycle](https://docs.meshy.ai/api/task-lifecycle).
- **Creative Lab DELETE differs**: it **cancels**. `PENDING` is refunded, `IN_PROGRESS` is canceled **without refund**, a final-status task returns `400`, success returns `204` — [Keychain](https://docs.meshy.ai/api/creative-lab-keychain). I checked the same "Cancels" and `204` wording on all 9 Creative Lab pages.
- **Common task-object fields**: `id`, `type`, `status`, `progress`, `created_at`, `started_at`, `finished_at`, `preceding_tasks`, `task_error`, `consumed_credits`, and usually `expires_at`. Timestamps are Unix ms — [llms.txt](https://docs.meshy.ai/llms.txt).
- **Optional header on all creates**: `X-Meshy-Metadata` (W3C Baggage, max 64 pairs and 8,192 bytes). Studio and Enterprise only; ignored elsewhere and by Creative Lab — [Metadata](https://docs.meshy.ai/api/metadata).

#### Text to 3D: `POST /openapi/v2/text-to-3d`

https://docs.meshy.ai/api/text-to-3d. Two steps on one endpoint: preview generates an untextured mesh, refine textures it.

**Cost**: preview 20 (`meshy-7.1`, `meshy-6`), 5 (`meshy-6-lite`, `meshy-t2`, `meshy-t2.5`), plus 5 for Ultra geometry. Refine 10 (2K or 4K), 15 (8K) — [Pricing](https://docs.meshy.ai/api/pricing).

*Preview parameters (`mode: "preview"`)*

| Param | Type | Req | Default | Allowed / notes |
|---|---|---|---|---|
| `mode` | string | yes | | `preview` |
| `prompt` | string | yes | | up to 800 chars, else `400` |
| `model_type` | string | | `standard` | `standard`, `smart-topology` (Meshy then ignores `should_remesh` and `decimation_mode`, triangle only) |
| `ai_model` | string | | `latest` | Standard: `meshy-6-lite`, `meshy-6`, `meshy-7.1`, `latest` (= 7.1), `meshy-7` (deprecated). Smart Topology: `meshy-t2`, `meshy-t2.5` (default) |
| `geometry_resolution` | string | | `standard` | `standard`, `2k` (Ultra at 2048³; needs `meshy-7.1`, `latest` or `meshy-7`), `4k` (Ultra at 4096³; needs `meshy-7.1` or `latest`). Other models `400`. Refine with this param `400` |
| `ultra_mode` | bool | | false | deprecated; `true` = `"2k"` |
| `should_remesh` | bool | | true for `meshy-6-lite`, false for others | "For the highest-quality 3D model, send false" |
| `topology` | string | | `triangle` | only when remeshing: `quad`, `triangle`. `quad` with Smart Topology `400` |
| `decimation_mode` | int | | | only when remeshing: 1 ultra, 2 high, 3 medium, 4 low. Overrides `target_polycount` |
| `target_polycount` | int | | see below | remesh on standard models: 100 to 300000 (default 30000). `meshy-t2`: 100 to 15000 (default 4000). `meshy-t2.5`: 100 to 30000 (default 15000). Out of range `400`. Result "can differ from the target" |
| `symmetry_mode` | string | | `auto` | deprecated, "doesn't affect the output" |
| `pose_mode` | string | | `""` | `a-pose`, `t-pose`, `""` |
| `is_a_t_pose` | bool | | false | deprecated |
| `art_style` | string | | `realistic` | deprecated, ignored |
| `moderation` | bool | | false | screens `prompt`; harmful content returns `400`, no task |
| `target_formats` | string[] | | all except 3mf | `glb`, `obj`, `fbx`, `stl`, `usdz`, `3mf`. Listing formats can shorten the task. `3mf` only when requested |
| `alpha_thumbnail` | bool | | false | adds `alpha_thumbnail_url` |
| `auto_size` | bool | | false | AI vision estimates real-world height and resizes |
| `origin_at` | string | | `bottom` | only with `auto_size`: `bottom`, `center` |

*Refine parameters (`mode: "refine"`)*

| Param | Type | Req | Default | Allowed / notes |
|---|---|---|---|---|
| `mode` | string | yes | | `refine` |
| `preview_task_id` | string | yes | | must be a `SUCCEEDED` preview |
| `enable_pbr` | bool | | false | adds metallic, roughness, normal. Emission only with `meshy-6` and not at 8K |
| `texture_resolution` | string | | `2k` | `2k`, `4k`, `8k`. 4K and 8K need `meshy-6`, `meshy-7.1` or `latest`. Preview with this param `400` |
| `hd_texture` | bool | | false | deprecated; `true` = `"4k"` |
| `texture_prompt` | string | | | up to 800 chars; wins over `texture_image_url` if both are sent |
| `texture_image_url` | string | | | public URL or data URI; JPG, JPEG, PNG, WebP, ≤20 MB |
| `ai_model` | string | | inherited from preview | `meshy-6-lite`, `meshy-6`, `meshy-7.1`, `latest`, `meshy-7` (deprecated) |
| `moderation` | bool | | false | screens the texture inputs |
| `remove_lighting` | bool | | true | effective only on `meshy-6`; accepted and ignored on 7.1 and `latest`; `400` with `meshy-6-lite` |
| `target_formats`, `alpha_thumbnail`, `auto_size`, `origin_at` | | | | as preview |

*OpenAPI-only request fields on this endpoint [OA]* — [OpenAPI TextTo3DRequest](https://docs.meshy.ai/openapi.json):

- `seed` (int64, min 0, "RNG seed; randomized when 0")
- `negative_prompt` (max 800, "What to avoid")
- `name` (max 100)
- `texture_richness` (`none`, `low`, `medium`, `high`; default `high`)
- `should_texture` ("Not generally available yet: ignored unless the one-call textured path is enabled for your account")
- `experimental` object (`turbo`, `enable_tsr`, `optimize_texture_seams`; "Subject to change")

*Response object*:

- `type` (`text-to-3d-preview` or `text-to-3d-refine`)
- `model_urls`: `glb`, `fbx`, `usdz`, `obj`, `mtl`, `stl`, `3mf`. A format not generated has no key
- `prompt`, `texture_prompt`, `geometry_resolution` (absent for standard), `texture_image_url`
- `thumbnail_url`, `alpha_thumbnail_url`, `video_url` (deprecated)
- `texture_urls[]`: `base_color`, `metallic`, `normal`, `roughness`, `emission`
- plus the common fields

#### Image to 3D: `POST /openapi/v1/image-to-3d`

https://docs.meshy.ai/api/image-to-3d.

**Cost** — [Pricing](https://docs.meshy.ai/api/pricing):

| Option | `meshy-7.1`, `latest`, `meshy-6` | `meshy-6-lite` | `meshy-t2`, `meshy-t2.5` |
|---|---|---|---|
| Mesh only | 20 | 5 | 5 |
| + 2K texture | 30 | 15 | 15 |
| + 4K texture | 30 | not supported | 15 |
| + 8K texture | 35 | not supported | 20 |
| Ultra surcharge (`2k` or `4k` geometry) | +5 (7.1 only) | not supported | not supported |

| Param | Type | Req | Default | Allowed / notes |
|---|---|---|---|---|
| `image_url` | string | one of | | public URL or data URI; JPG, JPEG, PNG, WebP, ≤20 MB |
| `input_task_id` | string | one of | | a `SUCCEEDED` API Text to Image or Image to Image task that produced **exactly one** image. Wins over `image_url` |
| `model_type` | string | | `standard` | `standard`, `smart-topology` (ignores `should_remesh`, `save_pre_remeshed_model`, `decimation_mode`; triangle only) |
| `ai_model` | string | | `latest` | `latest`, `meshy-7.1`, `meshy-6`, `meshy-6-lite`, `meshy-7` (deprecated); `meshy-t2`, `meshy-t2.5` (Smart Topology default) |
| `geometry_resolution` | string | | `standard` | `standard`, `2k`, `4k`; same model rules as Text to 3D |
| `ultra_mode` | bool | | false | deprecated |
| `should_texture` | bool | | true | false returns an untextured mesh |
| `enable_pbr` | bool | | false | needs `should_texture: true`, else `400`. Emission only with `meshy-6` and not at 8K |
| `texture_resolution` | string | | `2k` | `2k`, `4k`, `8k`. 4K and 8K `400` on `meshy-6-lite` |
| `hd_texture` | bool | | false | deprecated |
| `texture_prompt` | string | | | up to 800 chars; wins over `texture_image_url` |
| `texture_image_url` | string | | | URL or data URI; same format and size limits |
| `should_remesh` | bool | | true for `meshy-6-lite`, false for others | "For the highest-quality 3D model, set it to false" |
| `topology` | string | | `triangle` | `quad`, `triangle` when remeshing |
| `decimation_mode` | int | | | 1 to 4; overrides `target_polycount` |
| `save_pre_remeshed_model` | bool | | false | adds `model_urls.pre_remeshed_glb` |
| `target_polycount` | int | | 30000 | same three ranges as Text to 3D |
| `symmetry_mode` | string | | `auto` | deprecated, no effect |
| `pose_mode` | string | | `""` | `a-pose`, `t-pose`, `""` |
| `is_a_t_pose` | bool | | false | deprecated |
| `surface_mode` | string | | | deprecated, no effect; `organic`, `hard`, others `400` |
| `image_enhancement` | bool | | true | false keeps the exact look of the input. Only `meshy-6`, `meshy-7.1`, `latest`; else `400` |
| `remove_lighting` | bool | | true | effective on `meshy-6` only; ignored on 7.1; `400` with `meshy-6-lite` or Smart Topology |
| `moderation` | bool | | false | screens `image_url`, `texture_image_url`, `texture_prompt` |
| `target_formats` | string[] | | all except 3mf | `glb`, `obj`, `fbx`, `stl`, `usdz`, `3mf` |
| `auto_size` | bool | | false | AI height estimate |
| `origin_at` | string | | `bottom` | with `auto_size` |
| `alpha_thumbnail` | bool | | false | |
| `multi_view_thumbnails` | bool | | false | adds `thumbnail_urls` (front, right, back, left; 512×512 PNG; about 5 s extra) |

*OpenAPI-only [OA]*: `name` (max 100), `experimental`. — [OpenAPI ImageTo3DRequest](https://docs.meshy.ai/openapi.json). **`seed` is not in the Image to 3D request**, on either the page or OpenAPI.

*Response*: `type: image-to-3d`, `model_urls` (`glb`, `fbx`, `obj`, `usdz`, `mtl`, `stl`, `3mf`, `pre_remeshed_glb`), `thumbnail_url`, `alpha_thumbnail_url`, `thumbnail_urls`, `texture_prompt`, `texture_image_url`, `geometry_resolution`, `expires_at`, `texture_urls[]`, plus the common fields.

#### Multi-Image to 3D: `POST /openapi/v1/multi-image-to-3d`

https://docs.meshy.ai/api/multi-image-to-3d. 1 to 4 images of one object.

**Cost**: mesh 20 (`meshy-7.1`, `meshy-6`) or 5 (`meshy-6-lite`). With 2K or 4K texture 30; with 8K 35. `meshy-6-lite` with 2K texture 15 (4K and 8K not supported). Ultra +5. Smart Topology not supported — [Pricing](https://docs.meshy.ai/api/pricing).

Parameters are the same as Image to 3D, with these differences:

- `image_urls` (array, 1 to 4; first image is the front view on 7.1) **or** `input_task_id` (Text to Image or Image to Image task, including multi-view, with 1 to 4 images).
- `ai_model`: `latest`, `meshy-7.1`, `meshy-6`, `meshy-6-lite`, `meshy-7` (deprecated). No Smart Topology, no `model_type`, no `surface_mode`.
- `moderation` screens each input image, `texture_image_url` or each `texture_image_urls` image, and `texture_prompt`.
- [OA] only: `name` (max 100) — [OpenAPI MultiImageTo3DRequest](https://docs.meshy.ai/openapi.json).
- `geometry_resolution`: only `standard` or `2k`. `4k` returns `400`.
- Extra `texture_image_urls` (1 to 4 views, independent of `image_urls`, needs `meshy-7.1`, `latest` or `meshy-7`, cannot combine with `texture_image_url` or `texture_prompt`).
- `target_polycount` 100 to 300000, default 30000.

Same output fields as Image to 3D, plus `texture_image_urls`.

#### Retexture: `POST /openapi/v1/retexture`

https://docs.meshy.ai/api/retexture.

**Cost**: 10 (2K or 4K), 15 (8K) — [Pricing](https://docs.meshy.ai/api/pricing).

| Param | Type | Req | Default | Allowed / notes |
|---|---|---|---|---|
| `input_task_id` | string | one of | | Text to 3D, Image to 3D, Remesh, Retexture etc. `SUCCEEDED` API task; textures its GLB |
| `model_url` | string | one of | | GLB, glTF, OBJ, FBX, STL; ≤400 MB by URL, ≤100 MB as data URI (`application/octet-stream`). Over 100 MB: ≤10M faces, binary FBX 7.1+, no Draco |
| `text_style_prompt` | string | one of three | | up to 800 chars |
| `image_style_url` | string | one of three | | URL or data URI; JPG, JPEG, PNG, WebP ≤20 MB; wins over the text prompt |
| `multiview_image_urls` | string[] | one of three | | 1 to 4 views; first is front; **needs explicit `ai_model: "meshy-7"`**, even `latest` returns `400`; cannot combine with the other two |
| `ai_model` | string | | `latest` | `meshy-6-lite`, `meshy-6`, `meshy-7`, `latest` (= Meshy **7**; `meshy-7.1` is rejected per [llms.txt](https://docs.meshy.ai/llms.txt)) |
| `enable_original_uv` | bool | | false | keep existing UV layout |
| `enable_pbr` | bool | | false | emission only on `meshy-6`, not at 8K |
| `texture_resolution` | string | | `2k` | `2k`, `4k`, `8k`; 4K and 8K `400` on `meshy-6-lite` |
| `hd_texture` | bool | | false | deprecated |
| `remove_lighting` | bool | | true | applied on `meshy-6` at 2K or 4K only; `400` on `meshy-6-lite` |
| `target_formats` | string[] | | all except 3mf | `glb`, `obj`, `fbx`, `stl`, `usdz`, `3mf` |
| `alpha_thumbnail` | bool | | false | |

*OpenAPI-only [OA]*: `name`, `art_style` (`realistic` or `cartoon`, default `realistic`) — [OpenAPI RetextureRequest](https://docs.meshy.ai/openapi.json).

*Response*: `type: retexture`, `model_urls` (`glb`, `fbx`, `obj`, `usdz`, `mtl`, `stl`, `3mf`), `text_style_prompt`, `image_style_url`, `multiview_image_urls`, `thumbnail_url`, `alpha_thumbnail_url`, `expires_at`, `texture_urls[]`. No `moderation` parameter is documented on this endpoint.

Errors: `model_missing_uv`, `model_insufficient_uv` — [Errors](https://docs.meshy.ai/api/errors).

#### Remesh: `POST /openapi/v1/remesh`

https://docs.meshy.ai/api/remesh. **Cost**: 5.

| Param | Type | Req | Default | Allowed / notes |
|---|---|---|---|---|
| `input_task_id` | string | one of | | Text to 3D, Image to 3D, Retexture, Remesh etc. Wins over `model_url` |
| `model_url` | string | one of | | GLB, glTF, OBJ, FBX, STL; same size rules as Retexture |
| `target_formats` | string[] | | `["glb"]` | `glb`, `fbx`, `obj`, `usdz`, `blend`, `stl`, `3mf` |
| `topology` | string | | `triangle` | `quad`, `triangle` |
| `target_polycount` | int | | 30000 | **100 to 300000**, else `400` |
| `decimation_mode` | int | | | 1 to 4; overrides `target_polycount` |
| `resize_height`, `resize_longest_side` | number | | 0 | deprecated, use Resize; meters |
| `auto_size` | bool | | false | deprecated |
| `origin_at` | string | | `bottom` | deprecated |
| `convert_format_only` | bool | | | deprecated, use Convert |
| `alpha_thumbnail` | bool | | false | |

*Response*: `type: remesh`, `model_urls` (`glb`, `fbx`, `obj`, `usdz`, `blend`, `stl`, `3mf`), `thumbnail_url`, `alpha_thumbnail_url`. Remesh preserves textures for uploaded models — [Changelog Nov 4 2025](https://docs.meshy.ai/api/changelog).

#### Convert: `POST /openapi/v1/convert`

https://docs.meshy.ai/api/convert. **Cost**: 1.

- `input_task_id` or `model_url` (same input rules as Remesh).
- `target_formats` (required, at least one): `glb`, `fbx`, `obj`, `usdz`, `blend`, `stl`, `3mf`.
- Output: `type: convert`, `model_urls` for requested formats only.

#### Resize: `POST /openapi/v1/resize`

https://docs.meshy.ai/api/resize. **Cost**: 1.

- `input_task_id` or `model_url`.
- Exactly one of: `resize_height` (meters, >0), `resize_longest_side` (meters, >0), `auto_size` (bool).
- `origin_at` (`bottom` default, `center`).
- Output: `type: resize`. With `input_task_id` always GLB. With `model_url`, GLB, OBJ, FBX and STL keep their format; `.gltf` and data URI return GLB.

#### UV Unwrap: `POST /openapi/v1/uv-unwrap`

https://docs.meshy.ai/api/uv-unwrap. **Cost**: 5.

- `input_task_id` (GLB output required) or `model_url` (`.glb` only).
- **Mesh limit 40,000 faces**, else `400`. Output is always triangles.
- Output: `type: uv-unwrap`, `model_urls.glb` only (grey placeholder material), `thumbnail_url`, `expires_at`.

#### Rigging: `POST /openapi/v1/rigging`

https://docs.meshy.ai/api/rigging. **Cost**: 5.

- `input_task_id` or `model_url` (`.glb` only; textured humanoid; face points to +Z; **max 380,000 triangles**).
- `height_meters` (default 1.7).
- `texture_image_url` (deprecated; PNG ≤20 MB).
- [OA] only: `animation_type` (`biped` default, `quadruped`), `name` — [OpenAPI RiggingRequest](https://docs.meshy.ai/openapi.json).
- Extra error: `422` when pose estimation fails.
- Output: `type: rig`; `result.rigged_character_fbx_url`, `result.rigged_character_glb_url`; `result.basic_animations` (`walking_glb_url`, `walking_fbx_url`, `walking_armature_glb_url`, `running_glb_url`, `running_fbx_url`, `running_armature_glb_url`).

#### Animation: `POST /openapi/v1/animations`

https://docs.meshy.ai/api/animation. **Cost**: 3 per action, up to 10 actions per request — [Pricing](https://docs.meshy.ai/api/pricing).

- `rig_task_id` (required).
- Exactly one of `action_id` (int), `action_ids` (1 to 10, no repeats, merged into one file), `motion_task_id` (Text to Motion task, biped rig only; not in OpenAPI's `AnimationRequest`).
- `post_process` object: `operation_type` (`change_fps`, `fbx2usdz`, `extract_armature`), `fps` (24, 25, 30, 60; default 30).
- Output: `type: animate`; `result.animation_glb_url`, `animation_fbx_url`, `processed_usdz_url`, `processed_armature_fbx_url`, `processed_animation_fps_fbx_url`.

**`GET /openapi/v1/animations/library`**: free, unpaged. Filters `search`, `category` (`WalkAndRun`, `BodyMovements`, `DailyActions`, `Fighting`, `Dancing`), `sub_category`, `action_ids` (up to 200). Returns `action_id`, `name`, `key`, `category`, `sub_category`, `preview_url`.

#### Text to Motion: `POST /openapi/v1/text-to-motion`

https://docs.meshy.ai/api/text-to-motion.

- **Cost**: `prime` 10, `swift` 3.
- `prompt` (required, ≤400 chars), `mode` (`prime` default gives FBX, `swift` gives BVH), `duration` (required, 2 to 10 s in 0.5 steps).
- Moderation flag returns `403`.
- Output: `type: text-to-motion`; `result.motion_url`, `motion_format`, `duration_ms`, `mode`.

#### Text to Image: `POST /openapi/v1/text-to-image`

https://docs.meshy.ai/api/text-to-image. **Cost by model**: `nano-banana` 3, `nano-banana-2` 6, `nano-banana-2-lite` 3, `nano-banana-pro` 9, GPT Image models 9 — [Pricing](https://docs.meshy.ai/api/pricing).

| Param | Req | Default | Allowed / notes |
|---|---|---|---|
| `ai_model` | yes | | `nano-banana`, `nano-banana-2`, `nano-banana-2-lite`, `nano-banana-pro` (Pro plan or above, else `402`), `gpt-image-2`, `gpt-image-2-5-flare`, `gpt-image-2-5-sunburst` |
| `prompt` | yes | | no documented length limit |
| `generate_multi_view` | | false | not with `aspect_ratio`, else `400` |
| `pose_mode` | | | `a-pose`, `t-pose`. Behaviour varies by model: `nano-banana` is upgraded to `nano-banana-pro`; 3:4 forced on nano-banana models |
| `aspect_ratio` | | `1:1` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`; `3:2` and `2:3` on GPT Image only |
| `remove_background` | | false | returns transparent RGBA PNG |

Output: `type: text-to-image`, `ai_model`, `prompt`, `image_urls[]` (1, or about 3 when multi-view), `expires_at`.

#### Image to Image: `POST /openapi/v1/image-to-image`

https://docs.meshy.ai/api/image-to-image. **Cost**: same as Text to Image, except GPT Image models 12.

- `ai_model` (required, same list), `prompt` (required).
- `input_task_id` or `reference_image_urls` (1 to 5; JPG, JPEG, PNG, WebP; ≤20 MB; ≥32×32; URL or data URI).
- `generate_multi_view`, `aspect_ratio`, `remove_background` as in Text to Image.
- Output as in Text to Image, with `type: image-to-image`.

#### Multi-Color Print: `POST /openapi/v1/print/multi-color`

https://docs.meshy.ai/api/multi-color-print. **Cost**: 10.

| Param | Req | Default | Allowed / notes |
|---|---|---|---|
| `input_task_id` | one of | | reads the task's GLB; ≤8,000,000 faces, else `400` (Remesh first) |
| `model_url` | one of | | `.glb` or `.fbx` by URL ≤400 MB; base64 GLB data URI ≤100 MB; over 100 MB ≤8M faces |
| `max_colors` | | 4 | 1 to 16 |
| `style` | | `realistic` | `realistic` (samples texture; needs single base color texture and UVs on every part), `cartoon` (flat regions, smaller file; accepts vertex colors) |
| `max_depth` | | 4 | 3 to 6; `realistic` only |
| `printer_brand` | | `bambu` | `bambu`, `anycubic`, `creality`, `elegoo`, `flashforge`, `prusa`, `qidi`, `snapmaker`, `ankermake`. Writes a slicer preset for that brand's default printer, 0.4 mm nozzle |

Output: `type: print-multi-color`, `model_urls.3mf`. An untextured model is rejected (`model_missing_texture`).

#### Analyze Printability: `POST /openapi/v1/print/analyze`

https://docs.meshy.ai/api/analyze-printability. **Cost**: free.

| Param | Req | Notes |
|---|---|---|
| `input_task_id` | one of | Image to 3D, Multi-Image, Text to 3D, Remesh, Retexture on Meshy 6 or newer; or a Repair task |
| `model_url` | one of | `.glb`, `.gltf`, `.obj`, `.fbx`, `.stl` by URL ≤400 MB; data URI only GLB or glTF ≤100 MB |
| `printer_type` | | `fdm` (1.0 mm wall), `sla` (0.8 mm), `full_color` (2.0 mm) |
| `intended_print_height_mm` | | 1 to 1000; GLB input only; exclusive with next |
| `intended_print_longest_side_mm` | | 1 to 1000; every format |

Output: `type: print-analyze`, `printability`:

- `_version`, `status` (`healthy`, `warning`, `error`, `unknown`), `issue_count`, `error_count`, `warning_count`, `evaluated_at`.
- `metrics`: `is_watertight`, `volume` (m³), `non_manifold_edges`, `degenerate_faces`, `holes`.
- With a wall check, `intended_print` (`printer_type`, `height_mm`, `longest_side_mm`, `wall_thickness_mm`, `dimensions_mm`) and `thin_walls` (`thin_area_ratio`, `has_thin_walls`, `status`; error when over 5% of the surface is too thin).

Error thresholds: more than 8 holes, volume ≤0, more than 50 non-manifold edges.

#### Repair Printability: `POST /openapi/v1/print/repair`

https://docs.meshy.ai/api/repair-printability. **Cost**: 10.

- `input_task_id` (includes Analyze tasks; reuses their printer and size) or `model_url` (same formats as Analyze).
- `alpha_thumbnail`, `printer_type`, `intended_print_height_mm`, `intended_print_longest_side_mm`.
- Fixes non-manifold edges, degenerate faces, holes and "returns a watertight version ready to print". Thickens walls only when over 5% of the surface is too thin. Keeps original scale.
- **Removes textures** (`texture_urls` is always empty). Send the result to Retexture to add them back.
- Output: `type: print-repair`, `model_urls` with only the key matching the input format (`glb`, `gltf`, `fbx`, `obj`, `stl`; always GLB with `input_task_id`), `thumbnail_url`, `alpha_thumbnail_url`, `intended_print`, `print_repair_report` (`route`, `applied`, `faces_before`, `faces_after`, `thin_area_ratio_before`, `thin_area_ratio_after`).

#### Auto Split: `POST /openapi/v1/print/split`

https://docs.meshy.ai/api/auto-split. **Cost**: 10.

| Param | Req | Default | Allowed / notes |
|---|---|---|---|
| `input_task_id` | yes | | Image to 3D, Multi-Image, Text to 3D, Retexture, Remesh, Convert, Resize from Meshy 6 or 7 only. Smart Topology and uploaded-model tasks not supported. ≤8M faces. No `model_url` |
| `mode` | | `auto` | `auto`, `by_parts`, `by_color` (image-generated inputs only) |
| `prompt` | for `by_*` | | up to 600 chars, 1 to 10 named parts |
| `target_formats` | | `["glb"]` | `glb`, `obj`, `fbx`, `stl`, `usdz`, `blend`, `3mf`. STL fuses parts into one solid |
| `layout` | | `assembled` | `assembled`, `on_plate` |
| `keep_texture` | | false | keeps texture, about twice as slow, same price; `textured_split_refused` on failure. STL and 3MF hold geometry only |
| `connectors` | | false | mortise and tenon |
| `connector_type` | | `cube` | `cube`, `cylinder` |
| `connector_size` | | 0.5 | 0.1 to 0.8 |
| `connector_height` | | 0.1 | 0.1 to 0.8 |

Output: `type: print-split`, `model_urls`, `thumbnail_url`, `texture_urls`, `alpha_thumbnail_url`, `prompt_ignored`, `part_count`, `expires_at`. `by_*` modes have a limit of 12 requests per minute per account, and `503` when temporarily unavailable.

#### Balance and Usage

- `GET /openapi/v1/balance` returns `balance`, `monthly_credits`, `permanent_credits`, `monthly_resets_at` — [Balance](https://docs.meshy.ai/api/balance).
- `GET /openapi/v1/usage/tasks` — [Usage](https://docs.meshy.ai/api/usage):
  - Parameters: `page_num` (1 to 255), `page_size` (1 to 100), `sort_by`, `start_time` and `end_time` (RFC 3339, window ≤366 days, default last 30 days), `endpoints` (comma list: `text-to-3d`, `text-to-3d-preview`, `text-to-3d-refine`, `image-to-3d`, `multi-image-to-3d`, `retexture`, `remesh`, `convert`, `resize`, `uv-unwrap`, `rig`, `animate`, `text-to-motion`, `text-to-image`, `image-to-image`, `print-multi-color`, `print-repair`, `print-analyze`, `print-split`), `status`.
  - Records: `task_id`, `endpoint`, `status`, `created_at`, `finished_at`, `consumed_credits`, `api_key_name`, `api_key_suffix`, `metadata`.
  - Creative Lab tasks are excluded.

#### Creative Lab create parameters

All prototype images: `image_url` (required; URL or data URI; JPG, JPEG, PNG, WebP ≤20 MB), `name` (≤100 chars). Prices from [Pricing](https://docs.meshy.ai/api/pricing). Common task fields include `name`, `expires_at` (3 days after `finished_at`). `started_at` and `finished_at` are `null` until set — [Keychain](https://docs.meshy.ai/api/creative-lab-keychain).

| Product | Cost (prototype → build) | Prototype extras | Build parameters | Output |
|---|---|---|---|---|
| [Keychain](https://docs.meshy.ai/api/creative-lab-keychain) | 6 → 30 | `name_text` (≤10 chars), `remove_background` | `input_task_id`*, `name`, `options`: `badge_shape` (`circle` default, `rounded-rect`, `hexagon`, `shield`, `star`), `size_mm` (40, ≤400), `relief_height_mm` (2.2, 0 to 20), `relief_offset_mm` (0), `base_thickness_mm` (0.1), `has_closed_back` (true), `relief_curve` (`linear`, `gamma`, `s-curve`), `curve_param` (1.0, ≤10), `invert_depth`, `smoothing` (0.24, 0 to 10), `relief_scale` (1.0), `depth_threshold` (0.1, 0 to 1), `remove_background` (true), `export_resolution` (512, 64 to 512); `output.format` (`glb`, `obj`, `zip`) | Prototype `image_urls`. Build `model_urls` with one of `glb`, `obj` (zip), `bundle_zip` |
| [Fridge Magnet](https://docs.meshy.ai/api/creative-lab-fridge-magnet) | 6 → 30 | `remove_background` | Same `options` as Keychain; defaults differ: `badge_shape` `rounded-rect`, `size_mm` 60, `relief_height_mm` 3.3, `base_thickness_mm` 2.0 | Same as Keychain |
| [Figure](https://docs.meshy.ai/api/creative-lab-figure) | 6 → 30 | `remove_background` | `input_task_id`*, `name` only | `model_urls.glb`, `obj`, `mtl`; `thumbnail_url`; `texture_urls[0].base_color` |
| [Vinyl Figure](https://docs.meshy.ai/api/creative-lab-vinyl-figure) | 6 → 30 | `remove_background` | as Figure | as Figure |
| [Brick Figure](https://docs.meshy.ai/api/creative-lab-brick-figure) | 6 → 30 | `remove_background` | as Figure | as Figure |
| [Lamp](https://docs.meshy.ai/api/creative-lab-lamp) | 30 → 6 | `image_subject` (`character` default, `landscape`), `remove_background` | `options`: `diameter_mm` (150, 50 to 400), `thickness_mm` (1, ≤10), `cut_amount_percent` (1, 1 to 100), `light_source_preset` (`bambu_mh001_60mm` default, `none`), `fixture_offset_x_mm` and `fixture_offset_z_mm` (0, ±80), `rotate_x_deg`, `rotate_y_deg`, `rotate_z_deg` (0, ±360), `include_result_json`; `output.format` (`stl` default, `zip`) | Prototype `image_urls`, `model_urls.glb`, `thumbnail_url`. Build `model_urls.lamp_stl`, `base_stl` or `bundle_zip` |
| [Keycap](https://docs.meshy.ai/api/creative-lab-keycap) | 12 → 50 | `remove_background`; image ≥32 px per side, ≤178,956,970 px total | `input_task_id`*, `candidate_id`*, `name`, `options`: `base_model` (only `cherry-mx-1x1-r1`), `head_size_mm` (23, 10 to 40), `vertical_offset_mm` (0, ±5) | Prototype `image_urls`, `candidate_ids`. Build `model_urls.glb`, `obj_zip`, `process_image_urls` (`head_design`, `composite`, `base_canvas`); real-world mm, Y-up, front +Z |
| [Fidget Pixel](https://docs.meshy.ai/api/creative-lab-fidget-pixel) | 6 → 30 | `type`* (`person`, `other`) | `options`: `shape` (`square` default, `hex`), `grid_size` (32 default, 16), `piece_size_mm` (8 default, 6, 10; 10 not with hex), `color_count` (8, 1 to 8), `piece_height_mm` (15, 10 to 80); `output.format` (`3mf` only) | Build `model_urls.3mf` (multi-color) |
| [Collapsible Fidget](https://docs.meshy.ai/api/creative-lab-fidget-collapsible) | 6 (single stage) | none | `image_url`*, `name` only; no geometry settings | `model_urls.stl` always, `glb` when preview rendered; STL has no color |

*required.

**Processing times** (median, production traffic, September 2026) — [Task Lifecycle](https://docs.meshy.ai/api/task-lifecycle):

- Image to 3D mesh only: 7.1 75 s; `meshy-6` 90 s; `meshy-6-lite` 40 s; `meshy-t2` 4 s.
- Image to 3D with 2K: 2 min, 3 min, 75 s, 60 s respectively. With 4K: 2.5 min, 3.5 min, not supported, 80 s. With 8K: 3.5 min, 4 min, not supported, 2.5 min.
- PBR adds 30 to 60 s. Ultra adds up to 1 min.
- Remesh 2 min, UV Unwrap 35 s, Convert 7 s, Resize 15 s.
- Analyze 1 to 10 s, Multi-Color 30 s, Repair 10 to 100 s, Auto Split 70 to 170 s.
- `meshy-t2.5` is not in the timing table.

### Inferences

- `enable_pbr` appears to carry no surcharge. The [Pricing](https://docs.meshy.ai/api/pricing) tables have no PBR line, and [llms.txt](https://docs.meshy.ai/llms.txt) lists the "Textured model from one photo" recipe with `enable_pbr: true` at 30 credits. Meshy does not state "no surcharge" in words.

### Gaps

- `seed`, `negative_prompt`, `texture_richness` and `experimental.*`: spec-only descriptions, no behaviour, no pricing, no guarantee. The MCP server's generation source has no `seed` or `negative_prompt` [SDK] — [meshy-mcp-server](https://github.com/meshy-dev/meshy-mcp-server/tree/main/src/tools).
- `nano-banana-2-1` is priced at 4 credits in [Pricing](https://docs.meshy.ai/api/pricing), but it is absent from the Text to Image and Image to Image pages and from the OpenAPI enum.
- The Text to 3D task object on the page and in OpenAPI's `TextTo3DTask` does not list `expires_at`, although [Asset Retention](https://docs.meshy.ai/api/asset-retention) says URLs stop working at a task's `expires_at`.
- Request size limit for a `prompt` on Text to Image and Image to Image: not documented.

---

## Which AI model versions are available, and which parameters and prices differ by version?

### Takeaway

The current 3D models are `meshy-7.1` (`latest`), `meshy-6`, `meshy-6-lite`, `meshy-t2` and `meshy-t2.5`. `meshy-7` is deprecated but is still `latest` on Retexture. `meshy-3`, `meshy-4`, `meshy-5` and `meshy-t1` are retired.

### Cited Findings

Status — [Deprecations](https://docs.meshy.ai/api/deprecations):

| Model | State | Notes |
|---|---|---|
| `meshy-7.1` | Active | `latest` on Text to 3D, Image to 3D, Multi-Image |
| `meshy-7` | Deprecated Sep 18 2026, retirement TBA | `latest` on Retexture; same price as 7.1 |
| `meshy-6` | Active | |
| `meshy-6-lite` | Active | successor to `meshy-5` |
| `meshy-t2.5` | Active | Smart Topology default; added Oct 15 2026 |
| `meshy-t2` | Active | Smart Topology |
| `meshy-5` | Retired Oct 10 2026 | sending it returns `400` — [Changelog](https://docs.meshy.ai/api/changelog) |
| `meshy-t1`, `model_type: lowpoly` | Retired Oct 30 2026 | |
| `meshy-4` | Retired Mar 20 2026 | |
| `meshy-3` | Retired Jul 2025 | |

Differences by version — [Text to 3D](https://docs.meshy.ai/api/text-to-3d), [Image to 3D](https://docs.meshy.ai/api/image-to-3d), [Retexture](https://docs.meshy.ai/api/retexture), [Pricing](https://docs.meshy.ai/api/pricing):

| Capability | `meshy-7.1`, `latest` | `meshy-6` | `meshy-6-lite` | `meshy-t2` | `meshy-t2.5` |
|---|---|---|---|---|---|
| Mesh price (Text or Image to 3D) | 20 | 20 | 5 | 5 | 5 |
| Ultra geometry (+5) | `2k`, `4k` (Multi-Image `2k` only) | no | no | no | no |
| Default `should_remesh` | false | false | true | ignored | ignored |
| `target_polycount` | 100 to 300k (when remeshing) | same | same | 100 to 15k, default 4k | 100 to 30k, default 15k |
| Topology | quad or triangle when remeshing | same | same | triangle only | triangle only |
| 4K and 8K texture | yes | yes | no | yes on Image to 3D (15 and 20 credits) | yes on Image to 3D (15 and 20 credits) |
| Emission map with PBR | no | yes, except 8K | no | no | no |
| `remove_lighting` effect | accepted, ignored | effective | `400` | `400` on Image to 3D (ignored on a refine of a T2 preview without `ai_model`) | same as `meshy-t2` |
| `image_enhancement` | yes | yes | `400` | `400` | `400` |
| Multi-Image to 3D | yes | yes | yes | no | no |
| Auto Split input | yes | yes | yes | no | no |
| Retexture `ai_model` | not accepted (use `meshy-7`) | yes | yes | n/a | n/a |

Other model notes:

- At 8K, PBR maps are generated at 4K — [Changelog Jul 21 2026](https://docs.meshy.ai/api/changelog).
- Image models: `nano-banana`, `nano-banana-2`, `nano-banana-2-lite`, `nano-banana-pro`, `gpt-image-2`, `gpt-image-2-5-flare`, `gpt-image-2-5-sunburst` — [Text to Image](https://docs.meshy.ai/api/text-to-image).
- Set a specific model for consistent output; `latest` output "changes when a new model is released" — [Deprecations](https://docs.meshy.ai/api/deprecations).
- Retirement dates are announced at least one month ahead — [Deprecations](https://docs.meshy.ai/api/deprecations).
- Web-app prices differ from API prices. Example: Remesh and Rigging are 0 credits in the app, 5 in the API — [webapp Pricing](https://docs.meshy.ai/webapp/pricing), [API Pricing](https://docs.meshy.ai/api/pricing).

### Inferences

- The Ultra options are positioned for print use: the web app labels Ultra 2K "High-precision 3D printing and high-poly game assets" — [webapp Image to 3D](https://docs.meshy.ai/webapp/image-to-3d) [WEB]. That is a web-app positioning statement, not an API guarantee.

### Gaps

- The OpenAPI field text says Ultra "requires account entitlement" — [OpenAPI](https://docs.meshy.ai/openapi.json). The doc pages do not define what the entitlement is. The web-app docs say Ultra is on paid plans [WEB].
- `meshy-t2.5` timing is not documented.

---

## Error codes, task statuses, asset retention, and input limits (URL vs data URI)

### Takeaway

Five task statuses, four failure categories with named codes, automatic refund on failure. Download URLs are signed and expire at the task's `expires_at`, 3 days by default per the API docs. Image inputs are JPG, JPEG, PNG or WebP up to 20 MB by URL or data URI; model inputs up to 400 MB by URL or 100 MB by data URI.

### Cited Findings

**Statuses** — [Task Lifecycle](https://docs.meshy.ai/api/task-lifecycle):

- `PENDING`, `IN_PROGRESS`, `SUCCEEDED`, `FAILED`, `CANCELED`. The last three are final.
- `IN_PROGRESS` can go back to `PENDING`, with `progress` restarting — [llms.txt](https://docs.meshy.ai/llms.txt).
- The page says only Creative Lab tasks use `CANCELED`, while most standard task objects also list it.
- Wait at least 60 minutes from `created_at`. Recommended timeouts: POST 60 s (120 s for `model_url` over 100 MB), GET 30 s, poll by `Retry-After` or 5 s.
- There is no idempotency key. Do not auto-resend a create after a timeout — [llms.txt](https://docs.meshy.ai/llms.txt).

**HTTP errors** — [Errors](https://docs.meshy.ai/api/errors):

- `200`, `202`.
- `400`.
- `401`.
- `402` (no credits; Free plan task creation).
- `403` (IP allowlist `ip_not_authorized`, IP Filtering, plan; `This model type does not support this operation` for bas-relief input on post-process endpoints).
- `404`.
- `409` (DELETE on `IN_PROGRESS`).
- `422` (Rigging pose estimation — [Rigging](https://docs.meshy.ai/api/rigging)).
- `429`.
- `5xx`.

Error body is `{"message": ...}`.

**Task errors** — [Errors](https://docs.meshy.ai/api/errors):

- `task_error` has `type`, `message`, `code`, `doc_url`.
- Types: `invalid_input`, `timeout`, `service_unavailable`, `server_error`.
- Codes: `image_too_complex`, `model_missing_uv`, `model_insufficient_uv`, `model_missing_texture`, `textured_split_refused`, `invalid_input`, `moderation_blocked`, `moderation_unavailable`, `timeout`, `queue_timeout`, `format_conversion_failed`.
- Also `provider_content_refused` on Auto Split — [Auto Split](https://docs.meshy.ai/api/auto-split).
- `image_too_complex` triggers include dense piles, lattices, complex buildings and several objects in one image.
- Failed tasks are refunded.
- Credits are charged at creation — [llms.txt](https://docs.meshy.ai/llms.txt).

**Rate limits** — [Rate limits](https://docs.meshy.ai/api/rate-limits):

| Plan | RPS | Concurrent tasks | Priority |
|---|---|---|---|
| Pro | 20 | 10 | Default |
| Premium | 20 | 30 | Higher than Pro |
| Ultra | 20 | 100 | Highest |
| Studio | 20 | 60 (20 on some earlier Studio plans) | Higher than Pro |
| Enterprise | 100 | 100 default, or custom | Highest |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`. Concurrency `429` messages start with `NoMorePendingTasks` or `NoMoreConcurrentTasks`. Also `x-api-version` response header — [Changelog Oct 28 2025](https://docs.meshy.ai/api/changelog).

**Webhooks** — [Webhooks](https://docs.meshy.ai/api/webhooks):

- Set up in the dashboard. 5 active, 10 total. HTTPS only. All active webhooks receive all API task updates.
- Respond below 400 within about 25 s.
- Retries: up to 4 for `IN_PROGRESS`, up to 9 for a final status. 20 consecutive failed updates can deactivate the webhook.
- Payload is the task object with `progress` 50, 100 or 0. Deliveries can arrive out of order or duplicated.
- **Signature or HMAC verification: not documented** on that page.

**Retention and expiry**

- "at most **3 days**"; Enterprise indefinite. URLs on `assets.meshy.ai` are signed (`?Expires=…&Signature=…`) and stop at `expires_at`. Refetching returns the same URL. Expired URLs sent back as `model_url` give `400 failed to download model file`. `input_task_id` works while Meshy keeps the source task, then `404 Task not found` — [Asset Retention](https://docs.meshy.ai/api/asset-retention).
- **Conflict**: the marketing pages say "14 days on Studio and 3 days on other non-Enterprise plans" — [meshy.ai/api](https://www.meshy.ai/api), [meshy.ai/pricing](https://www.meshy.ai/pricing) [SITE]. The docs do not mention Studio's 14 days.

**Input limits**

- Images: JPG, JPEG, PNG, WebP; ≤20 MB; public URL or `data:image/...;base64,` — [Image to 3D](https://docs.meshy.ai/api/image-to-3d).
- Minimum 32×32 on Image to Image — [Image to Image](https://docs.meshy.ai/api/image-to-image).
- Keycap page adds ≥32 px per side, ≤178,956,970 pixels, EXIF orientation applied, format detected from data, redirects followed — [Keycap](https://docs.meshy.ai/api/creative-lab-keycap). Those detailed limits are only stated on Creative Lab pages, and I am not asserting them for Image to 3D.
- Models: GLB, glTF, OBJ, FBX, STL (varies); ≤400 MB by URL; ≤100 MB as data URI. Over 100 MB: ≤10M faces (8M for Multi-Color), binary FBX 7.1+, no Draco — [Changelog Oct 14 2026](https://docs.meshy.ai/api/changelog), [Remesh](https://docs.meshy.ai/api/remesh).
- Face-count caps by endpoint: UV Unwrap 40k; Rigging 380k triangles; Multi-Color and Auto Split 8M — [UV Unwrap](https://docs.meshy.ai/api/uv-unwrap), [Rigging](https://docs.meshy.ai/api/rigging), [Multi-Color](https://docs.meshy.ai/api/multi-color-print), [Auto Split](https://docs.meshy.ai/api/auto-split).

**Account and access**

- Paid plan needed for API keys — [Quickstart](https://docs.meshy.ai/api/quick-start).
- `402` on Free for most task creates — [Errors](https://docs.meshy.ai/api/errors).
- Credits are prepaid — [Pricing](https://docs.meshy.ai/api/pricing).
- Keys can have a monthly credit limit and an IP allowlist of up to 50 entries — [Authentication](https://docs.meshy.ai/api/authentication).
- The shared test-mode key is retired since Sep 16 2026 — [Changelog](https://docs.meshy.ai/api/changelog). (The [llms.txt](https://docs.meshy.ai/llms.txt) index blurb still says "test-mode key".)
- Plan prices on [meshy.ai/pricing](https://www.meshy.ai/pricing) rendered in BRL for my request: Pro R$ 107.9/month, Premium R$ 216/month, Studio R$ 380 billed monthly [SITE]. USD prices and credit-pack prices were not visible in what I read.

### Inferences

- Because the docs and marketing pages disagree on Studio retention, a report writer should present 3 days as the documented minimum and flag the 14-day claim as needing vendor confirmation. Enterprise retention is consistent across both sources.

### Gaps

- USD price per credit: not found in the API docs. [Pricing](https://docs.meshy.ai/api/pricing) sends the reader to subscription settings and sales.
- Exact input-resolution minimum for Image to 3D: not documented on that page.
- Maximum data URI request body size for images beyond the 20 MB rule: not documented.
- The Ultra plan appears in [Rate limits](https://docs.meshy.ai/api/rate-limits) and in the raw HTML of [meshy.ai/pricing](https://www.meshy.ai/pricing) ("Meshy AI Ultra Plan" in page metadata), but my WebFetch summary of the visible plan cards listed only Free, Starter, Pro, Premium, Studio, Enterprise. Its price and credits were not captured.

---

## Capabilities that matter for a 3D-print marketplace

### Takeaway

Documented maximum `target_polycount` is **300,000**, so a 1.2M-face target cannot be requested. Unremeshed and Ultra output face counts are not stated. Printing tooling is broad: free analysis, watertight repair with wall thickening, multi-color 3MF for 9 printer brands, part splitting, real-world resize. Watertightness is promised for Repair output, not for raw generation output.

### Cited Findings

| Topic | Finding | Status |
|---|---|---|
| `target_polycount` | Remesh path and standard models 100 to 300000, default 30000; `meshy-t2` 100 to 15000; `meshy-t2.5` 100 to 30000; out of range returns `400`; result "can differ" — [Image to 3D](https://docs.meshy.ai/api/image-to-3d), [Remesh](https://docs.meshy.ai/api/remesh) | Documented |
| 300k faces | Available as a target: `should_remesh: true`, `target_polycount: 300000` on Text or Image to 3D, or Remesh with 300000 | Documented |
| 1.2M faces | No parameter accepts it. Face count of unremeshed output (`should_remesh: false`, the default on 7.1 and 6) and of Ultra `2k` or `4k`: **not documented** | Not documented |
| High-poly evidence | Multi-Color and Auto Split accept up to 8M faces and tell you to Remesh if over — [Multi-Color](https://docs.meshy.ai/api/multi-color-print). Web-app docs say "film assets can reach millions" (generic glossary) and show a too-many-faces error at 8M when texturing — [concepts](https://docs.meshy.ai/webapp/concepts), [AI texturing](https://docs.meshy.ai/webapp/guides/3d-model/ai-texturing) [WEB] | Limits only, not a generation output spec |
| `decimation_mode` | 1 ultra, 2 high, 3 medium, 4 low; "adaptive"; face counts per level not documented — [Image to 3D](https://docs.meshy.ai/api/image-to-3d) | Levels documented, counts not documented |
| Topology | `quad` (quad-dominant) or `triangle` (decimated), only when remeshing; Smart Topology triangle only; UV Unwrap output always triangles | Documented |
| Pre-remesh backup | `save_pre_remeshed_model: true` adds `model_urls.pre_remeshed_glb` (Image to 3D and Multi-Image only) | Documented |
| Export STL, OBJ, GLB, FBX, USDZ, 3MF | `target_formats` on Text to 3D, Image to 3D, Multi-Image, Retexture. 3MF only when requested. `mtl` comes with textured OBJ — [Image to 3D](https://docs.meshy.ai/api/image-to-3d) | Documented |
| BLEND export | Only via Remesh, Convert or Auto Split `target_formats`; `model_urls.blend` — [Convert](https://docs.meshy.ai/api/convert) | Documented |
| DXF | Web app only — [Export formats](https://docs.meshy.ai/webapp/guides/platform/export-formats) [WEB]; not in any API `target_formats` | Web only |
| 3MF color | A normal 3MF has geometry only; color comes from Multi-Color Print or split parts — [Export formats](https://docs.meshy.ai/webapp/guides/platform/export-formats) [WEB]. Auto Split 3MF "geometry only" even with `keep_texture` — [Auto Split](https://docs.meshy.ai/api/auto-split). The web page's "split parts" color and the API's "geometry only" wording do not fully agree | Partly conflicting |
| Multi-color printing | `POST /print/multi-color`: 1 to 16 colors, `realistic` or `cartoon`, preset for 9 printer brands, 10 credits; output 3MF. Needs a textured model — [Multi-Color](https://docs.meshy.ai/api/multi-color-print) | Documented |
| `origin_at` | `bottom` or `center`; on generation only with `auto_size`; on Resize with any mode — [Resize](https://docs.meshy.ai/api/resize) | Documented |
| Real-world size | `auto_size` (AI estimate) on generation. `POST /resize` with `resize_height` or `resize_longest_side` in **meters** or `auto_size`. `resize_*` on Remesh is deprecated — [Resize](https://docs.meshy.ai/api/resize) | Documented |
| Size units in files | USDZ uses metres since Oct 12 2026 — [Changelog](https://docs.meshy.ai/api/changelog). Print checks read an STL's longest side "as millimeters" — [Analyze](https://docs.meshy.ai/api/analyze-printability). Whether Convert output STL or 3MF is in mm or m: **not documented** | Partly documented |
| Watertight, manifold, solid | **No guarantee on generation.** "Meshy can generate print-ready models, but they need some post-processing first" — [3D printing workflow](https://docs.meshy.ai/webapp/guides/use-cases/3d-printing) [WEB]. Repair "returns a watertight version ready to print" — [Repair](https://docs.meshy.ai/api/repair-printability). Auto Split "every part prints solid" — [Auto Split](https://docs.meshy.ai/api/auto-split) | Repair and Split only |
| Printability checks | `POST /print/analyze` free: watertight, volume, holes, non-manifold, degenerate, thin walls per printer and size — [Analyze](https://docs.meshy.ai/api/analyze-printability) | Documented |
| Wall thickness | API: FDM 1.0 mm, SLA 0.8 mm, full-color 2.0 mm — [Repair](https://docs.meshy.ai/api/repair-printability). Web guide: FDM 1.2, SLA or DLP 0.5, SLS 0.8 — [3D printing workflow](https://docs.meshy.ai/webapp/guides/use-cases/3d-printing). **The two tables differ** | Conflict |
| Repair and texture | Repair removes textures; `texture_urls` always empty; re-add with Retexture — [Repair](https://docs.meshy.ai/api/repair-printability) | Documented |
| Multi-color vs repair order | Repair output has no color, so Multi-Color rejects it until retextured — [Errors `model_missing_texture`](https://docs.meshy.ai/api/errors) | Documented |
| Split for printing | Auto Split: parts, connectors, build-plate layout, 3MF with separate parts; Meshy 6 and 7 inputs only — [Auto Split](https://docs.meshy.ai/api/auto-split) | Documented |
| Slicer integration | MCP tool `meshy_send_to_slicer` runs locally, no API call — [AI integration](https://docs.meshy.ai/api/ai). Web app sends to 9 slicers — [3D printing platforms](https://docs.meshy.ai/webapp/3d-printing-platforms/introduction) [WEB]. **No REST slicer endpoint.** `printer_brand` writes a preset into the 3MF | Documented |
| `should_remesh` | Default true on `meshy-6-lite`, false otherwise; ignored on Smart Topology | Documented |
| `enable_pbr` | Metallic, roughness, normal; emission only `meshy-6` | Documented |
| Textures at benchmark (2048²) | `texture_resolution: "2k"` = 2048×2048 base color; 4K, 8K also. Resolution of PBR maps at 2K or 4K: not stated; at 8K they are 4K — [Changelog Jul 21 2026](https://docs.meshy.ai/api/changelog) | Partly documented |
| `symmetry_mode` | Deprecated May 11 2026, accepted and ignored — [Deprecations](https://docs.meshy.ai/api/deprecations) | Documented |
| `pose_mode` | `a-pose`, `t-pose`, `""` | Documented |
| Moderation | `moderation` (default **false**) on Text to 3D, Image to 3D, Multi-Image: blocked requests return `400`, no task. Filters can also fail a task (`moderation_blocked`, `moderation_unavailable`) — [Errors](https://docs.meshy.ai/api/errors). Text to Motion and Auto Split prompts `403`. Creative Lab has NSFW `400` and team "IP Filtering" `403` — [Keychain](https://docs.meshy.ai/api/creative-lab-keychain) | Documented |
| Retexture for later editing | By `text_style_prompt`, `image_style_url` or `multiview_image_urls`, on `input_task_id` or own `model_url`. `enable_original_uv` keeps UVs — [Retexture](https://docs.meshy.ai/api/retexture) | Documented |
| Partial or brush editing | Texture Edit brush tool is web-app only — [Texture Edit](https://docs.meshy.ai/webapp/guides/texture-edit) [WEB]; no API endpoint | Web only |
| Seed reproducibility | Text to 3D `seed` only in OpenAPI ("RNG seed; randomized when 0") [OA]. No seed on Image to 3D. Determinism guarantee: **not documented** | OA only / not documented |
| Regenerate from earlier task ID | Text to 3D refine takes `preview_task_id` (textures the same mesh; no geometry regeneration). Image to 3D takes `input_task_id` only from Text to Image or Image to Image tasks. Retexture and Remesh take a prior model task. Rerunning geometry at higher quality from a prior Image to 3D task ID: **no such parameter documented** | Documented / not documented |
| Input image preservation | `image_enhancement: false` keeps the exact input look (not `meshy-6-lite` or Smart Topology); `remove_lighting` — [Image to 3D](https://docs.meshy.ai/api/image-to-3d) | Documented |
| Separate physical products | Creative Lab keychains, magnets, figures, lamps, keycaps, fidgets, some with mm parameters — see table above. Figure, Vinyl and Brick pages return GLB and OBJ only | Documented |

**Cost ladder for the Kubo flow, from [Pricing](https://docs.meshy.ai/api/pricing)** (Image to 3D, credits per request):

| Step | Option | Credits |
|---|---|---|
| Text to 2D image | `nano-banana` or `nano-banana-2-lite` / `nano-banana-2` / `nano-banana-pro` | 3 / 6 / 9 |
| Edit 2D image | `nano-banana` / GPT Image | 3 / 12 |
| Cheap preview 3D | `meshy-6-lite` or `meshy-t2` or `meshy-t2.5`, mesh only | 5 |
| Cheap preview 3D, textured 2K | same models | 15 |
| Final 3D | `meshy-7.1` with 2K or 4K texture | 30 |
| Final 3D, Ultra geometry | above + `geometry_resolution` `2k` or `4k` | 35 |
| Final 3D, 8K texture, Ultra | | 40 |
| Remesh to 300k if a set count is needed | | 5 |
| Analyze / Repair / Resize / Convert / Multi-Color / Split | | 0 / 10 / 1 / 1 / 10 / 10 |

### Inferences

These are my reasoning, not Meshy statements:

- The Jujubit 1.2M tier has no equivalent request parameter at Meshy. Whether `should_remesh: false` or Ultra exceeds 1.2M faces by itself cannot be determined from the docs. It would need a test or a vendor answer, and I ran no API calls.
- For a "cheap preview, then higher quality after purchase, from the same input image" flow, the documented path is a **new** Image to 3D task using the stored image (or an in-retention Text or Image to Image `input_task_id`). Nothing documented ties it to the preview's shape, and no seed exists on that endpoint, so the final geometry may not match the preview. The web docs rate Image to 3D's "Consistency across generations" as High, relative to other methods — [generation method](https://docs.meshy.ai/webapp/guides/choosing/generation-method) [WEB]. That is not a guarantee.
- A purchased model cannot be regenerated or post-processed by `input_task_id` after retention ends, so the buyer's source image and model files would need to be stored on Kubo's side — [Asset Retention](https://docs.meshy.ai/api/asset-retention).
- A chain for a sized, repaired print file looks like Analyze → Repair (GLB) → Resize → Convert (STL or 3MF). Only each step's input acceptance is documented. Repair output is accepted as Analyze input. For Resize and Convert, the pages say `input_task_id` is "the Meshy task" without restricting type. Scale surviving Convert is not documented.
- For color prints, Repair then Retexture then Multi-Color follows from the documented rules, but the effect of Retexture on a repaired mesh's watertightness is not documented.

### Gaps

- Face count of generated models by model and geometry tier: not documented anywhere I read. The only example figure is "about 25,000 faces" on a Text to 3D sample in the [web docs](https://docs.meshy.ai/webapp/text-to-3d) [WEB].
- Watertight rate of raw output: not documented.
- Whether `decimation_mode: 1` (ultra) exceeds the 300k target range: not documented.
- PBR GLB benchmark parity (2048² PBR maps in one GLB): the base color resolution and the PBR map set are documented. Map-size equality at 2K is not explicitly stated.
- Print-specific slicer profile contents beyond "default printer, 0.4 mm nozzle": not documented.

---

## Coverage: what was read and what was not

### Takeaway

I verified the full API sidebar and read every API page at least for its parameters and outputs. The main unread items are the web-app plugin pages, the Cookbook and Blog links, and a public animation JSON, plus enterprise-only or partner routes that are not published. I do not claim 100% of what Meshy has, only 100% of the listed API navigation.

### Cited Findings

**Navigation verified**: sidebar from the [API overview](https://docs.meshy.ai/en/api) (via WebFetch), [llms.txt](https://docs.meshy.ai/llms.txt) index, and [sitemap.xml](https://docs.meshy.ai/sitemap.xml) English URLs. All match. All 115 English URLs are in `llms-full.txt` except `/en/api`, which I fetched separately. Non-English sitemap entries are translations and were not read.

**Machine-readable sources read**

- https://docs.meshy.ai/llms.txt (full)
- https://docs.meshy.ai/openapi.json (programmatic dump of all operations, all POST request properties, schema keys; selected field descriptions)
- https://docs.meshy.ai/llms-full.txt (basis for the pages below)
- https://docs.meshy.ai/sitemap.xml

**Live `.md` spot-check**: pricing, asset-retention and image-to-3d `.md` downloads returned `200`, and sample strings matched `llms-full.txt`. I did not do a byte-level comparison.

**API pages read in full** (excluding code samples; long JSON examples truncated):

- https://docs.meshy.ai/api/authentication
- https://docs.meshy.ai/api/errors
- https://docs.meshy.ai/api/pricing
- https://docs.meshy.ai/api/rate-limits
- https://docs.meshy.ai/api/task-lifecycle
- https://docs.meshy.ai/api/asset-retention
- https://docs.meshy.ai/api/deprecations
- https://docs.meshy.ai/api/webhooks
- https://docs.meshy.ai/api/metadata
- https://docs.meshy.ai/api/changelog
- https://docs.meshy.ai/api/text-to-3d
- https://docs.meshy.ai/api/image-to-3d
- https://docs.meshy.ai/api/balance
- https://docs.meshy.ai/api/usage
- https://docs.meshy.ai/api/animation-library
- https://docs.meshy.ai/api/creative-lab-keychain (DELETE and stream sections were read separately or omitted as noted below)

**API pages read with a filter** that removed code samples, JSON examples, the repeated 401/402/429 failure labels and the stream section; DELETE was checked by a script across all pages:

- https://docs.meshy.ai/api/multi-image-to-3d
- https://docs.meshy.ai/api/remesh
- https://docs.meshy.ai/api/convert
- https://docs.meshy.ai/api/resize
- https://docs.meshy.ai/api/uv-unwrap
- https://docs.meshy.ai/api/retexture
- https://docs.meshy.ai/api/rigging
- https://docs.meshy.ai/api/animation
- https://docs.meshy.ai/api/text-to-motion
- https://docs.meshy.ai/api/text-to-image
- https://docs.meshy.ai/api/image-to-image
- https://docs.meshy.ai/api/multi-color-print
- https://docs.meshy.ai/api/analyze-printability
- https://docs.meshy.ai/api/repair-printability
- https://docs.meshy.ai/api/auto-split

**API pages read partially**

- https://docs.meshy.ai/api/ai: all except install snippets and FAQ detail.
- https://docs.meshy.ai/api/quick-start: first section.
- https://docs.meshy.ai/api/developer-platform: first part (through Usage dashboard).
- Creative Lab, header + create parameters + returns + output fields only; **failure modes read only as a list of status codes, and stream/get/list bodies not read**:
  - https://docs.meshy.ai/api/creative-lab-fridge-magnet
  - https://docs.meshy.ai/api/creative-lab-figure
  - https://docs.meshy.ai/api/creative-lab-vinyl-figure
  - https://docs.meshy.ai/api/creative-lab-brick-figure
  - https://docs.meshy.ai/api/creative-lab-lamp
  - https://docs.meshy.ai/api/creative-lab-keycap
  - https://docs.meshy.ai/api/creative-lab-fidget-collapsible
  - https://docs.meshy.ai/api/creative-lab-fidget-pixel

**Web-app pages read** (context only, not API evidence):

- Full or nearly full: https://docs.meshy.ai/webapp/guides/use-cases/3d-printing, https://docs.meshy.ai/webapp/guides/platform/export-formats, https://docs.meshy.ai/webapp/pricing, https://docs.meshy.ai/webapp/guides/3d-model/remesh, https://docs.meshy.ai/webapp/3d-printing-platforms/introduction, https://docs.meshy.ai/webapp/guides/choosing/generation-method, https://docs.meshy.ai/webapp/guides/choosing/integration.
- Excerpts only (grep or first lines): https://docs.meshy.ai/webapp/image-to-3d, https://docs.meshy.ai/webapp/text-to-3d, https://docs.meshy.ai/webapp/glossary, https://docs.meshy.ai/webapp/concepts, https://docs.meshy.ai/webapp/guides/texture-edit, https://docs.meshy.ai/webapp/guides/3d-model/ai-texturing.

**Marketing pages** (WebFetch summaries, then raw HTML grep for retention and price strings): https://www.meshy.ai/api, https://www.meshy.ai/pricing.

**Secondary, labelled [SDK]**: [meshy-dev/meshy-mcp-server `src/tools`](https://github.com/meshy-dev/meshy-mcp-server/tree/main/src/tools): file list; `generation.ts`, `printing.ts` and `creative-lab.ts` searched for `seed`, `negative_prompt`, and print paths. Not read end to end.

### Inferences

- None beyond those stated in the sections above.

### Gaps

**Not read**

- https://docs.meshy.ai/webapp/plugins/* (Blender, Unity, Unreal, Maya, 3ds Max, Godot, Roblox, Omniverse, ZBrush, Cascadeur, Codex, Hermes Agent, OpenClaw) and the individual slicer pages under `/webapp/3d-printing-platforms/*`. Reason: DCC or slicer plugin docs, out of API scope. They are in `llms-full.txt` if needed. The Blender plugin's model-analysis and cleanup pages might add print context.
- Other web-app guides (3D Agent, getting started, web changelog except grep hits, rigging, animate, unwrap UV, auto split, batch, image generation, prompting, asset management, scene compose, video generation, game assets). Reason: out of API scope.
- The "Cookbook" and "Blog" links in the docs top navigation. Reason: outside the docs and API reference; they were not in the sitemap English list I enumerated.
- `https://api.meshy.ai/web/public/animations/resources`. Reason: the brief forbids real API calls, so the action catalog (`action_id` list) was not retrieved.
- https://status.meshy.ai and https://help.meshy.ai. Reason: not API reference.

**Could not read**

- `https://docs.meshy.ai/api.md` returned `404`. I read the overview at `/en/api` via WebFetch instead, as a summary. The other pages read through WebFetch (only the two marketing pages and this overview) are summarized, not verbatim, apart from the raw HTML strings noted above.

**Not publicly documented**

- Enterprise-only endpoints, partner surface "d5", in-development endpoints, and `v2` print routes (see first section).
