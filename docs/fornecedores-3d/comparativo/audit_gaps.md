# Tripo AI and Meshy API: closing the coverage-audit gaps (as read 2026-11-01)

**Labels.** **[documented]** = on an official docs page. **[only in SDK]** = only in official SDK, CLI or plugin code, or in the docs page's table of SDK routes where no reference page exists. **[not documented]** = I looked in the pages named and did not find it; where a fact comes from the docs site's JavaScript rather than page text, this is stated.

**Method.** Tripo and Meshy docs pages were downloaded fresh with `curl` on 2026-11-01. The two Meshy v2 pages were byte-identical to the earlier audit copies, so the audit's text extraction was reused. Hidden code tabs (the v2 side of each v1/v2 example) were read separately from the page's embedded data. SDK evidence uses the audit's earlier repository copies, which were not re-downloaded. No request was sent to `api.tripo3d.ai`, `openapi.tripo3d.ai` or `api.meshy.ai`, and no account was created.

---

## 1. Tripo `POST /v3/mesh/edit`

### Takeaway
It redoes one box-shaped region of a 3D model with the P2 pipeline. **The page documents no text prompt or instruction parameter**: the only inputs that steer it are a 3D bounding box and an optional reference image. The page states no status (preview, gated or generally available) and no credit cost, and the pricing page does not list it.

### Cited Findings

**Purpose [documented]**
- Page title "Mesh Local Edit": "Locally retry or refine a 3D mesh region defined by a 2×3 bounding box. Uses P2 model pipeline (wire model P2-20260801)." — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- Base URL `https://openapi.tripo3d.ai/v3`, endpoint `POST /mesh/edit`. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)

**All parameters [documented]** — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)

| Parameter | Type | Required | Default | Rules quoted or summarized from the page |
|---|---|---|---|---|
| `input` | string | Required | | "Choose exactly one" of: a `task_id` from "a previous 3D generation task (`text_to_model`, `image_to_model`, or `multiview_to_model`)"; a `file_token` from the File Upload API; or a public direct URL. GLB, GLTF, FBX, OBJ, STL; max 150 MB |
| `model` | string | Optional | `P2-20260801` | "Only `P2-20260801` is supported." |
| `bbox` | number[][] | Required | | "Required 2×3 axis-aligned bounding box in model space, e.g. `[[-1, -1, -1], [1, 1, 1]]`. Each value must be a finite number." |
| `face_limit` | integer | Optional | | "Optional output face limit. Minimum 100 when provided." |
| `ref_image` | string | Optional | | "Optional reference image (file_token or URL) for semantic guidance." |
| `compress` | string | Optional | | `geometry` = meshopt compression |

**Response [documented]** — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- Create: `{"code":0,"data":{"task_id":"..."}}`.
- Task result: `type: "mesh_edit"`, `status`, `progress`, `output.model_url`, `output.rendered_image_url`, `created_at`, `completed_at`. The page's example shows no `credits_consumed`.

**Restrictions**
- [documented] Only `P2-20260801`; `bbox` is required; `face_limit` is at least 100; max 150 MB. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- [documented, looks copied from another page] The page says `texture_quality`, `geometry_quality`, `auto_size`, `quad`, `smart_low_poly`, `generate_parts` and `compress` "are only valid when `model ≥ v3.0-20250812`". Only `compress` is a parameter of this endpoint, and the only accepted model is P2. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)

**Credit cost: [not documented]**
- The page gives no cost. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- The pricing page HTML has no mesh-edit row. The label `mesh_edit: "Mesh Local Edit"` exists in the site's main script, but the pricing page's own script does not reference it. — [pricing](https://developers.tripo3d.ai/en/pricing); [site script](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js); [pricing script](https://developers.tripo3d.ai/assets/PricingPage-WUV2iHaa.js)
- The Tripo CLI and plugin mark it as billed, with no amount. [only in SDK] — [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) (`dist/commands/mcp-full.js`: `tripo_mesh_edit: { billed: true }`); [tripo-hermes-plugin](https://github.com/Tripo-Developer/tripo-hermes-plugin) (`skills/tripo-3d/references/tools.md`)

**Status**
- [not documented] The page text has no preview, beta, gated or generally-available wording. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- [not documented; site JavaScript only] The site's router keeps the page apart from the public list: `UNLISTED_DOC_IDS=["mesh-edit"]`. — [site script](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js)
- [only in SDK] The CLI's own comment reads: "`/v3/mesh/edit` has a reference page that is still left out of the docs index, and cn returned 4001 when last checked. The step stays hidden; set TRIPO_EXPERIMENTAL_MESH_EDIT=1 to opt in. Flip this default once the endpoint is listed and live." — [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) (`dist/knowledge/chains.js`)
- [only in SDK] The same package's changelog points the other way for the MCP tool: "`tripo_mesh_edit` is available without `TRIPO_EXPERIMENTAL_MESH_EDIT`, matching the hosted server. The CLI `mesh edit` command stays experimental." — [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) (`CHANGELOG.md`)

**Editing by instruction**
- [documented] The page has no `prompt`, `instruction` or similar text parameter. Semantic guidance is limited to `ref_image`. — [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md)
- [only in SDK] The hosted-tool description adds that the box "bounds the region to redo", and the plugin guide says "the rest of the mesh is kept". The docs page does not say this. — [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) (`dist/commands/mcp-tools.generated.js`); [tripo-hermes-plugin](https://github.com/Tripo-Developer/tripo-hermes-plugin) (`skills/tripo-3d/references/workflows.md`)

### Inferences
- A chat product could not pass the user's sentence to this endpoint as documented. It would have to turn the request into a `bbox` itself, and the only content guidance it could pass is a reference image.
- Availability is best described as "has a reference page, deliberately unlisted, status not stated". The two CLI statements together suggest the route exists on at least the hosted international service, but nothing here was tested.

### Gaps
- Whether the input model must have been generated with P2, or can come from any generation model or upload, beyond the `input` description above: not documented.
- Whether texture is preserved, whether the output is textured, how `bbox` relates to model scale, and how the region is blended: not documented.
- Credit cost, rate-limit bucket and any changelog entry: not documented. The current changelog has no `mesh/edit` entry. — [changelog](https://developers.tripo3d.ai/en/docs/changelog.md)

---

## 2. Tripo `account/usage`, `openai/images/edits`, the five routes without pages, and the definitive V3 list

### Takeaway
The 27 versus 28 difference is exactly one route: **`POST /v3/mesh/edit`** is in the audit's count and not in the inventory's. Otherwise the two lists match. Definitive count: **28 V3 operations with reference documentation**, plus **5 further V3 paths with no reference page**. Of those five, 2 are described by Tripo as usable or supported somewhere (`image-to-depth`, `upload-credentials`), 2 are retired per the SDK page (`refine`, `stylize`) and 1 appears only in one Java SDK file (`generation/smartsegment`).

### Cited Findings

#### `GET /v3/account/usage`
- [documented] Described on the Account page as "Usage returns per-task consumption history", with a `curl` example, but that page's `**Endpoint:**` line names only `GET /account/balance`. — [account](https://developers.tripo3d.ai/en/docs/account.md)
- [documented] The Billing page has its own "View Usage" section, `GET /v3/account/usage`. It documents the fields `task_id`, `type`, `credits_consumed` and `created_at`. — [billing](https://developers.tripo3d.ai/en/docs/billing.md)
- [documented] Listed as a new V3 capability ("Query usage details"). — [changelog](https://developers.tripo3d.ai/en/docs/changelog.md)
- [documented] The OpenAI-compatible page points to Account or Task Query for spend. — [openai-compat-images](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- **Parameters: conflict.** The Account and Billing pages show none. The official migration skill gives `GET /v3/account/usage?limit=50&offset=0` with "limit ≤200" and adds a `status` field to each row. — [migration skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md). The Python SDK matches the skill: `get_usage(limit=50, offset=0)` returning `task_id, type, status, created_at, credits_consumed`. [only in SDK] — [tripo-python-sdk](https://github.com/Tripo-Developer/tripo-python-sdk) (`docs/API.md`)
- **Credit cost:** [not documented]. No page states a charge for this read.

#### `POST /v3/openai/images/edits`
- [documented] Named in the body of the OpenAI-compatible page as "image to image (multipart or JSON)". The page's `**Endpoint:**` line names only `generations`. — [openai-compat-images](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- [documented] Models: only `gpt-image-2`, `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`. Anything else, including `chat_image_*` and dated snapshots, returns 404 `model_not_found`. — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- [documented] Parameters — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md):

| Parameter | Required | Rule |
|---|---|---|
| `model` | Required | One of the three above |
| `prompt` | Required | |
| `image` | Conditional | Edits only, multipart. `image` or `image[]`, one part per input image |
| `images` | Conditional | Edits only, JSON. Each entry has exactly one of `image_url` (https URL, or base64 data URL up to 10 MiB) or `file_id` (a `file_token` from `POST /v3/files`) |
| `mask` | Optional | Inpainting mask on the first input image. PNG with alpha, sent as a file part; fully transparent pixels mark the region to redraw. Same dimensions as the input, up to 20 MiB. "The mask guides the model semantically rather than clipping pixels" |
| `size` | Optional | Default `1024x1024`; `auto` and omitted both resolve to `1024x1024`; each edge a multiple of 16 px |
| `quality` | Optional | Default `low`; `gpt-image-2`: low, medium, high; 2.5: also xhigh, max |
| `background` | Optional | auto, opaque, transparent; effective on 2.5 only; transparent needs `output_format=png` |
| `output_format` | Optional | Default `png`; or `jpeg`; webp is rejected |
| `n` | Optional | Must be 1 |
| `response_format` | Optional | Only `url`; `b64_json` returns 400 |
| `stream` | Optional | Not supported |

- [documented] Input image cap is 10 MiB, uploaded or as a data URL. — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- [documented] Response: `created`, `data[].url` (signed CDN URL), echoed `size`, `quality`, `output_format`, `background`, and `tripo.task_id`, also sent as the `X-Tripo-Task-Id` header. No `usage` block. — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- [documented] Cost: "Identical to Text to Image and Image to Image — same credits, same content moderation, same concurrency limits." No separate number on this page. — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- [documented] Timing: blocks until ready, typically 20 to 80 s. After 240 s it returns 400 `generation_in_progress`: "the task has not failed and was charged once", so poll `GET /v3/tasks/{task_id}`. — [same page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)

#### Routes without a reference page

| Route | Reference page | Status per source | Label |
|---|---|---|---|
| `POST /v3/files/upload-credentials` | **None** ([`files-upload-credentials`](https://developers.tripo3d.ai/en/docs/files-upload-credentials) returned 404) | Changelog: "Get direct file upload credentials". Skill: "30-min STS creds + `file_token`", but "the simpler replacement" is presign. SDK page: Java's "internal `/v3/files/upload-credentials` descriptor has no public client flow and is not counted". Not in the SDK route table | [documented] as a mention only, with no parameters — [changelog](https://developers.tripo3d.ai/en/docs/changelog.md); [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [sdk](https://developers.tripo3d.ai/en/docs/sdk.md) |
| `POST /v3/generation/image-to-depth` | **None** ([`generation-image-to-depth`](https://developers.tripo3d.ai/en/docs/generation-image-to-depth) returned 404) | SDK route table: "Generate a depth image", Python only. Python call: `image_to_depth("./cat.png", kind="gray", process_res=504)`. No price found. The site script has a task label for `image_to_depth`, and the audit's search of the docs found no other mention | [only in SDK] — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md); [tripo-python-sdk](https://github.com/Tripo-Developer/tripo-python-sdk) (`docs/API.md`); [site script](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js) |
| `POST /v3/generation/smartsegment` | **None** ([`generation-smartsegment`](https://developers.tripo3d.ai/en/docs/generation-smartsegment) returned 404) | Only a constant in the Java SDK's `GatewayDenylist`, described as "ModelGateway / image-generation gateway routes intentionally excluded from this SDK". The same list holds the documented `/v3/mesh/smartsegment`. Nothing says it is callable | [only in SDK] — [tripo-java-sdk](https://github.com/Tripo-Developer/tripo-java-sdk) (`src/main/java/ai/tripo3d/sdk/internal/contract/GatewayDenylist.java`) |
| `POST /v3/models/refine` | **None** ([`models-refine`](https://developers.tripo3d.ai/en/docs/models-refine) and its `.md` returned 404) | SDK page: "Refine and stylize are retired and are not listed as supported". Python raises without sending a request. Skill: "effectively dead in V2 already". **Stale mentions remain:** changelog and migration tables still map to it, rate limits still names "refine", site script labels the dead page "Refine Model (deprecated)" | [documented] as retired, with conflicting leftovers — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md); [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [changelog](https://developers.tripo3d.ai/en/docs/changelog.md); [migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md); [rate limits](https://developers.tripo3d.ai/en/docs/rate-limits.md); [site script](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js) |
| `POST /v3/models/stylize` | **None** ([`models-stylize`](https://developers.tripo3d.ai/en/docs/models-stylize) returned 404) | Same SDK-page statement. Skill still lists "same 7 styles" and a mapping. Changelog and migration tables still map to it; site script labels it "Stylize (deprecated)" | [documented] as retired, with conflicting leftovers — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md); [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md); [changelog](https://developers.tripo3d.ai/en/docs/changelog.md); [migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md); [site script](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js) |

#### Reconciling 27 and 28
- The inventory's table lists 27 routes and has no `mesh/edit` row; the audit's lists 28 with `mesh/edit` as row 20. The other 27 match one for one. — tripo_endpoints.md; docs_coverage_audit.md (local notes)
- Separately, the SDK page's route table has 26 rows. It adds `image-to-depth` and omits `mesh/edit` and both `openai/images/*` routes. — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md)

#### Definitive flat list of V3 operations
Base `https://openapi.tripo3d.ai`. Page IDs are under [`developers.tripo3d.ai/en/docs/`](https://developers.tripo3d.ai/en/docs/introduction).

**A. Reference documentation exists (28)**

| # | Operation | Page |
|---|---|---|
| 1 | `POST /v3/generation/text-to-model` | [H](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-text-to-model/p) |
| 2 | `POST /v3/generation/image-to-model` | [H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-image-to-model/p) |
| 3 | `POST /v3/generation/multiview-to-model` | [H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/p) |
| 4 | `POST /v3/generation/image-to-splat` | [page](https://developers.tripo3d.ai/en/docs/generation-image-to-splat) |
| 5 | `POST /v3/generation/text-to-image` | [page](https://developers.tripo3d.ai/en/docs/generation-text-to-image) |
| 6 | `POST /v3/generation/image-to-image` | [page](https://developers.tripo3d.ai/en/docs/generation-image-to-image) |
| 7 | `POST /v3/generation/image-to-multiview` | [page](https://developers.tripo3d.ai/en/docs/generation-image-to-multiview) |
| 8 | `POST /v3/generation/edit-multiview` | [page](https://developers.tripo3d.ai/en/docs/generation-edit-multiview) |
| 9 | `POST /v3/models/texture` | [page](https://developers.tripo3d.ai/en/docs/models-texture) |
| 10 | `POST /v3/models/convert` | [page](https://developers.tripo3d.ai/en/docs/models-convert) |
| 11 | `POST /v3/models/import` | [page](https://developers.tripo3d.ai/en/docs/models-import) |
| 12 | `POST /v3/mesh/segment` | [page](https://developers.tripo3d.ai/en/docs/mesh-segment) |
| 13 | `POST /v3/mesh/smartsegment` | [page](https://developers.tripo3d.ai/en/docs/mesh-smartsegment) |
| 14 | `POST /v3/mesh/complete` | [page](https://developers.tripo3d.ai/en/docs/mesh-complete) |
| 15 | `POST /v3/mesh/decimate` | [page](https://developers.tripo3d.ai/en/docs/mesh-decimate) |
| 16 | `POST /v3/mesh/uv` | [page](https://developers.tripo3d.ai/en/docs/mesh-uv) |
| 17 | `POST /v3/mesh/edit` (**unlisted page**, status not stated) | [page](https://developers.tripo3d.ai/en/docs/mesh-edit.md) |
| 18 | `POST /v3/animations/rig-check` | [page](https://developers.tripo3d.ai/en/docs/animations-rig-check) |
| 19 | `POST /v3/animations/rig` | [page](https://developers.tripo3d.ai/en/docs/animations-rig) |
| 20 | `POST /v3/animations/retarget` | [page](https://developers.tripo3d.ai/en/docs/animations-retarget) |
| 21 | `GET /v3/tasks/{task_id}` | [page](https://developers.tripo3d.ai/en/docs/task-query) |
| 22 | `POST /v3/tasks/list` | [page](https://developers.tripo3d.ai/en/docs/task-batch-query) |
| 23 | `POST /v3/files` | [page](https://developers.tripo3d.ai/en/docs/files) |
| 24 | `POST /v3/files/presign` | [page](https://developers.tripo3d.ai/en/docs/files-presign) |
| 25 | `GET /v3/account/balance` | [page](https://developers.tripo3d.ai/en/docs/account.md) |
| 26 | `GET /v3/account/usage` (no own Endpoint line) | [account](https://developers.tripo3d.ai/en/docs/account.md), [billing](https://developers.tripo3d.ai/en/docs/billing.md) |
| 27 | `POST /v3/openai/images/generations` | [page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md) |
| 28 | `POST /v3/openai/images/edits` (no own Endpoint line) | [page](https://developers.tripo3d.ai/en/docs/openai-compat-images.md) |

**B. No reference page (5, not counted above):** `POST /v3/files/upload-credentials`, `POST /v3/generation/image-to-depth`, `POST /v3/generation/smartsegment`, `POST /v3/models/refine` (retired), `POST /v3/models/stylize` (retired). Sources are in the table above.

### Inferences
- The likely price for `openai/images/edits` follows from the page's "same credits" line plus the native price table: 1024x1024 at `low` would be the `chat_image_2` up-to-1K tier, listed in the earlier inventory as 10 credits ([pricing](https://developers.tripo3d.ai/en/pricing)). The mapping between `gpt-image-*` and `chat_image_*` names is implied by the page's error example, not stated as a table.
- "Retired" is the current official wording for refine and stylize. The newest-looking source (SDK page, which names current SDK versions) outweighs the older tables, but Tripo does not say which page wins.

### Gaps
- Whether the five section B routes respond today: not testable under this assignment.
- Pagination limits and any charge for `GET /v3/account/usage` on a current reference page: not documented; the limit appears only in the skill and SDK.
- What `POST /v3/generation/smartsegment` does: not documented anywhere I could read.

---

## 3. Meshy API v2

### Takeaway
**Neither migration page gives API v2 a status: the words preview, beta, gated and generally available do not describe v2 anywhere in their text, and no v1 end date is given.** Both pages are written as if v2 can be used now ("we strongly recommend trying v2 with your API key"), but both are `noindex, nofollow`, absent from every index, and the docs site code shows "Preview" elements behind a flag. v2 is mainly a change of shape: one set of task routes, results under `output`, full task object on create, and a new error object. Prices are not restated in a table, and the differences that are stated are small.

### Cited Findings

#### Status

- **Text on the pages:** no status label. The strongest available wording is: "Every v2 endpoint is under https://api.meshy.ai/openapi/v2/", and "Before you change any code, we strongly recommend trying v2 with your API key to get familiar with it." No plan, entitlement or sign-up requirement is stated. [documented] — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2)
- A case-insensitive search of both raw pages found the following only in other senses: "preview" (Text to 3D preview step), "Beta" (the Ask AI button), "invite" (a Discord link). "generally available", "GA", "gated", "early access", "waitlist" and "sunset" had no match. — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)
- Both pages carry `<meta name="robots" content="noindex, nofollow">`. [not documented as a status; page metadata only] — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)
- API v2 is absent from `llms-full.txt` (0 matches for "API v2" or "migrate-to-v2"), and the current OpenAPI spec has no `/v2/tasks` path. — [llms-full.txt](https://docs.meshy.ai/llms-full.txt); [openapi.json](https://docs.meshy.ai/openapi.json)
- [not documented; site JavaScript only] The docs script shows a `PreviewStrip` region with a badge on `/api/v2` and migration pages, a `V1Strip.PreviewText` strip on v1 pages, and a version switch whose v2 option has a `Preview` note. All render only when the `ApiV2` flag is on (`return!!e?.ApiV2`). Only those key names were found, not the displayed sentences. — [docs chunk](https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js)
- Anonymous requests to `/en/api/v2/image-to-3d`, `/errors`, `/tasks` and `/repair-printability` get a 302 to the v1 equivalent, although the reference page links to several `/en/api/v2/*` URLs. — [example](https://docs.meshy.ai/en/api/v2/image-to-3d); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)
- **Conflict that bears directly on status:** the reference recommends one-call Text to 3D through `should_texture`, but the OpenAPI spec says of that same field: "Not generally available yet: ignored unless the one-call textured path is enabled for your account. Use `mode: preview`, then `mode: refine`." The public Text to 3D page does not mention `should_texture`. The Deprecations page does not list preview and refine as deprecated. — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference); [openapi.json](https://docs.meshy.ai/openapi.json); [text-to-3d](https://docs.meshy.ai/api/text-to-3d.md); [deprecations](https://docs.meshy.ai/api/deprecations.md)

#### General response and error changes [documented]
All from [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2) and [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference).

| Area | v1 | v2 |
|---|---|---|
| Results | Top level (`model_urls`, `thumbnail_url`, `texture_urls`, `image_urls`), or `result.*` on Rigging, Animation, Text to Motion | Under `output`; `output` is null until success |
| Request echo | Some top-level fields | `input`, holding only what you sent, with no defaults or values Meshy chose; unknown parameters left out; data URIs replaced; signed URL queries removed. `null` when no copy exists, for example tasks before June 2026 |
| Create response | `{"result":"<id>"}` | Full task object with `id`. HTTP 202, new `Location` header, `Retry-After` as a hint for the first poll |
| Lists | Bare array | `{"data":[...],"has_more":...}`, newest first, no total count |
| Empty values | `0`, `""`, or missing | `null`; every listed field always present; arrays are never null, except `dimensions_mm` |
| Errors | `{"message":...}` | `{"type","code","message","doc_url"}`, same object as `task_error`. HTTP codes do not change; branch on `code` |
| Removed fields | | `art_style`, `object_prompt`, `style_prompt`, `negative_prompt`, `printability._version`. `alpha_thumbnail_url` stays only on Text to 3D |
| Validation | Some mismatches returned 400 | On Image and Multi-Image to 3D, `remove_lighting` and `image_enhancement` are ignored with `meshy-6-lite`, and on Image to 3D with Smart Topology too; Retexture ignores `remove_lighting` with `meshy-6-lite`. Unknown parameters are still ignored, on both versions |
| New model aliases | | `meshy-standard-latest` (Image, Multi-Image, Retexture, Text to 3D); `meshy-smart-topology-latest` (Image, Text to 3D). "The v1 endpoints don't accept them." |

#### Endpoint by endpoint [documented]
Same two sources unless noted.

**Image to 3D, Multi-Image to 3D**
- `POST /openapi/v2/image-to-3d`, `POST /openapi/v2/multi-image-to-3d`.
- Without `target_formats`: **GLB only**. v1 returned GLB, OBJ, FBX, STL, USDZ.
- `ai_model` alone picks the model; `model_type` is ignored. A v1 `"model_type":"smart-topology"` without `ai_model` runs Meshy T2.5; on v2 that same request silently uses `latest`, so send `meshy-smart-topology-latest` or `meshy-t2.5`.
- `texture_prompt` plus `texture_image_url` together: 400 on v2; v1 used `texture_prompt`.
- Ignored without error: `hd_texture` (use `texture_resolution`), `ultra_mode` (use `geometry_resolution`; "no Ultra charge" when ignored), `is_a_t_pose` (use `pose_mode: t-pose`, which "can differ"), `symmetry_mode`, `surface_mode`, `alpha_thumbnail`.
- `thumbnail_url` is already a transparent PNG.
- **Print size:** STL and 3MF are scaled down to at most 150 mm on the longest side, keeping proportions. Other formats keep the size.

**Text to 3D (replacement for preview and refine)**
- Quoted: "`mode`, which splits the work into a preview and a refine, is deprecated. It keeps working for integrations that already use it."
- One call: omit `mode`, send `should_texture`. `true` gives task type `text-to-3d` and "costs the same as a preview plus a refine". `false` gives a mesh only and "costs the same as a preview"; `enable_pbr` with it returns 400.
- If `mode` is also sent, `should_texture` is ignored and the two-step flow runs.
- `ai_model`: `latest`, `meshy-standard-latest`, `meshy-7.1`, `meshy-6`, `meshy-6-lite`, or a Smart Topology model. `meshy-7` returns 400.
- `geometry_resolution` `2k`, `4k` need `meshy-7.1`, or `latest` when it resolves to 7.1. `ultra_mode` is ignored. `count` above 1 returns 400.
- "You can't refine a one-call task." To inspect a mesh first, send `should_texture: false`, then use Retexture with its `id` as `input_task_id`.
- Create path does not change. The create response is now the full task object and keeps `result` for compatibility. Most errors change to the new object. "Its route already runs on v2, so these changes to its responses and errors apply to your current Text to 3D code."
- Both texture inputs: 400. Ignored: `negative_prompt`, `art_style`, `symmetry_mode`, `texture_richness`. Not returned: `negative_prompt`, `art_style`, `texture_richness`, `video_url`.
- Stays as before: default formats GLB, OBJ, FBX, STL, USDZ (3MF on request), no print size cap, `model_type` still accepted.
- Reads: `/openapi/v2/tasks` gives the common shape; the Text to 3D routes keep results at top level and also include `input` and `output`.

**Multi-Color, Repair, Analyze, Auto Split (`print/*`), plus UV Unwrap, Rigging, Animation, Text to Motion**
- "These endpoints keep their v1 requests", apart from listed ignored parameters, and their responses change to the v2 task object.
- Repair and Analyze "check wall thickness by default, for an FDM print 150 mm tall". Send `printer_type` and a size to set your own. `intended_print` is always present on Repair and is top-level, not under `output`.
- Analyze "is still free". A create can already return `SUCCEEDED` with results if the same model, printer and size were analyzed, so check `status` before polling.
- Auto Split "always applies the cap". `prompt_ignored` is top-level from the create response.
- Multi-Color keeps the size of a `model_url` upload; its 3MF follows the size rules.
- Rigging ignores `texture_image_url`. `result.*` moves to `output.*`.

**Convert, Resize**
- "The requests work as on v1, and Convert still requires `target_formats`."
- Resize also takes `origin_at` without a size, moving only the origin.
- Tasks that take a Resize as input use the resized model.
- Convert keeps the size of a `model_url` upload in every format. Resize tasks are not capped themselves.
- Neither returns `thumbnail_url`.

**Remesh**
- Accepted parameters: `input_task_id` or `model_url`, `topology`, `target_polycount`, `decimation_mode`, `target_formats`. Without `target_formats`, returns GLB.
- `resize_height`, `resize_longest_side`, `origin_at`, `auto_size`, `convert_format_only` return **400 even when null or false**.
- v1's single call becomes a chain of Remesh, Resize, Convert.
- `model_url` uploads come back as one centered mesh. Rigs, animations and morph targets are dropped.

**Retexture**
- Rename `text_style_prompt` to `texture_prompt`, `image_style_url` to `texture_image_url`. Old names alone return 400; both inputs together return 400.
- `enable_original_uv` is replaced by `uv_mode`: `auto` (default, keeps UVs if their box covers at least 5% of the UV square), `regenerate` (v1 default), `preserve`.
- GLB only unless `target_formats` is set. `art_style`, `name` and `alpha_thumbnail` are ignored.
- Accepts `meshy-standard-latest`.

**Text to Image, Image to Image**
- `remove_background` is replaced by `background`. **Transparent PNG by default**, and a generated scene is removed too. Send `"background":"opaque"` to keep it. Opaque with `generate_multi_view: true` returns 400. "Credits don't change."

**Tasks**
- Four routes for every task type except Creative Lab, including tasks created on v1 (IDs are kept).
- List: `type` optional; `type=text-to-3d` matches all three Text to 3D types. `page_num` 1 to 255; `page_size` default 10, max 100; `sort_by`.
- Stream: repeats latest state every 10 s, closes on finish or after about 21 minutes.
- Delete: same as v1 (200 empty, refunds `PENDING`, 409 for `IN_PROGRESS`).
- Type values: `image-to-3d`, `multi-image-to-3d`, `text-to-3d-preview`, `text-to-3d-refine`, `text-to-3d`, `retexture`, `remesh`, `convert`, `resize`, `uv-unwrap`, `rig`, `animate`, `text-to-motion`, `text-to-image`, `image-to-image`, `print-multi-color`, `print-repair`, `print-split`, `print-analyze`.
- 404 codes: `route_not_found`, `task_not_found` (also for Creative Lab IDs), `input_task_not_found`.

**Usage, Balance, Animation Library**
- `GET /openapi/v2/usage/tasks` "takes the same parameters and returns the same records and errors as v1, wrapped in `{"data": [...], "has_more": ...}`".
- "Balance and Animation Library return the same bodies as v1."

**Webhooks**
- The payload version is **per webhook**, set on the Webhooks page, independent of the API version that created the task. Existing webhooks stay on v1; "A webhook you add on the Webhooks page starts on v2 unless you pick v1."
- Header `Meshy-Webhook-Version` on every delivery. v2 body is the task object, except `progress` is 50, 100 or 0.
- Creative Lab deliveries keep the v1 body and header, even on a v2 webhook.
- "Send test" adds `Meshy-Webhook-Test: true`. Switching does not resend past deliveries.

**Creative Lab**
- "Creative Lab and the other v1 endpoints have no v2 version, so those calls stay on v1."

#### Pricing and retention [documented]
- No full pricing table on either page, and no general statement that all prices match. The current Pricing page does not mention v2. — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference); [pricing](https://docs.meshy.ai/api/pricing.md)
- Stated cost facts — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference):
  - Remesh with formats costs 5 on both versions.
  - A v1 Remesh with a resize or origin move cost 5; **the v2 chain costs 7** (Remesh 5, Resize 1, Convert 1).
  - `convert_format_only` becomes one Convert at 1 credit instead of 5.
  - Text and Image to Image: "Credits don't change."
  - One-call Text to 3D costs the same as preview plus refine.
  - Analyze "is still free".
  - An ignored `ultra_mode` has no Ultra charge.
- Retention: `expires_at` "is 3 days after `finished_at`". It is null until success and "always null for Text to 3D tasks and Enterprise accounts". For Text to 3D on other accounts, "null doesn't mean Meshy keeps the files. Meshy still deletes them 3 days after the task finishes." v1 also set it on failed tasks. This matches the 3-day limit on the public page. — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference); [asset retention](https://docs.meshy.ai/api/asset-retention.md)
- Rate limits: "v1 and v2 share the same rate limits." — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

#### v1 deprecation timeline
- **None stated.** No retirement date for v1 appears on either page. The steps say "Later, remove the v1 code and the switch", and a switch back to v1 is offered. — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2)
- The Deprecations page has no entry for v1 as a whole. Its nearest item is the legacy path without `/openapi`, removal date to be announced. — [deprecations](https://docs.meshy.ai/api/deprecations.md); [changelog](https://docs.meshy.ai/api/changelog.md)

#### Definitive list of v2 routes
Base `https://api.meshy.ai`.

**A. Literally on the pages [documented]** — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

| Operation | How it appears |
|---|---|
| `GET /openapi/v2/tasks/{id}` | Method and path |
| `GET /openapi/v2/tasks?type=<type>` | Method and path |
| `GET /openapi/v2/tasks/{id}/stream` | Method and path |
| `DELETE /openapi/v2/tasks/{id}` | Method and path |
| `POST /openapi/v2/image-to-3d` | Method and path |
| `POST /openapi/v2/text-to-3d` | Method and path |
| `GET /openapi/v2/usage/tasks` | Method and path |
| `POST /openapi/v2/multi-image-to-3d` | `curl -X POST` in a hidden v2 code tab |
| `POST /openapi/v2/retexture` | `curl -X POST` in a hidden v2 code tab |
| `POST /openapi/v2/remesh` | `curl -X POST` in a hidden v2 code tab |
| `POST /openapi/v2/resize` | `curl -X POST` in a hidden v2 code tab |
| `POST /openapi/v2/convert` | `curl -X POST` in a hidden v2 code tab |
| `POST /openapi/v2/text-to-image` | `curl -X POST` in a hidden v2 code tab |
| `/openapi/v2/text-to-3d/{id}` | Path, called a read route; method not printed |

**B. Follow only from the stated rule [documented rule, path not printed]** "Every /openapi/v1 endpoint that creates a task has a v2 version at the same path under /openapi/v2/, and so do Balance, Usage, and Animation Library." — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)
- `POST /openapi/v2/image-to-image`
- `POST /openapi/v2/uv-unwrap`
- `POST /openapi/v2/rigging`
- `POST /openapi/v2/animations`
- `POST /openapi/v2/text-to-motion`
- `POST /openapi/v2/print/multi-color`
- `POST /openapi/v2/print/analyze`
- `POST /openapi/v2/print/repair`
- `POST /openapi/v2/print/split`
- `GET /openapi/v2/balance`
- `GET /openapi/v2/animations/library`

**C. Text to 3D own read routes, from the stable spec and the reference's description** The reference says Text to 3D "keeps its own routes", and refers to "its list, its stream". Exact forms come from the spec: `GET /openapi/v2/text-to-3d`, `GET /openapi/v2/text-to-3d/{id}`, `DELETE /openapi/v2/text-to-3d/{id}`, `GET /openapi/v2/text-to-3d/{id}/stream`. — [openapi.json](https://docs.meshy.ai/openapi.json); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

**D. Explicitly do not exist** Per-endpoint reads such as `GET /openapi/v2/image-to-3d/{id}` (404 `route_not_found`), and any Creative Lab v2 route. — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

**Count:** 13 literal routes with a known method in table A (7 printed with a method, 6 as `curl -X POST`), 11 rule-only routes in B, and 4 Text to 3D reads in C, one of which is the method-less row in table A. Total 28 routes.

### Inferences
- "Preview, behind a docs-site flag" is the best reading of the evidence, and it comes from code key names, not from any sentence Meshy shows to a reader in the pages I could read. A final report should say "status not stated on the pages" and report the flag separately.
- Whether the docs flag also limits the API itself is unknown. The page's call to try v2 "with your API key" names no restriction, which is consistent with the API being open while the docs are hidden, but that is not proof.
- The `should_texture` conflict may simply mean the spec was written before the migration page, or that the feature rolls out per account. Neither source says which.
- The earlier gap about "On v2, Repair Printability ... always run the thin-wall check" is closed: it refers to this v2 family. The reference says "by default", while [Task Lifecycle](https://docs.meshy.ai/api/task-lifecycle.md) says "always". A minor wording difference.
- The earlier gap about the Text to 3D task object missing `expires_at` is also closed by the retention quote above.

### Gaps
- The displayed text of the `PreviewStrip` and `V1Strip` banners: not found (see the last section).
- Parameter-level v2 reference pages per endpoint: redirected to v1 for an anonymous reader.
- Which accounts can call v2 today: not documented, and calling the API is out of scope.
- A v1 retirement date: not documented.

---

## 4. Meshy `/openapi/v1/showcases` and `/openapi/v1/oauth/*`

### Takeaway
Both are **only in SDK and undocumented** in the current public docs: a paid Enterprise community-model search, and the login routes used by Meshy's own CLI and agent tools.

### Cited Findings
- **`GET /openapi/v1/showcases` [only in SDK]:** "Search community showcase models (Enterprise tier; every request is billed)". Parameters in code: `page_size`, `sort_by`, `search`, `format`, `showcase_type`. — [meshy-cli](https://github.com/meshy-dev/meshy-cli) (`src/cmd/showcases.ts`, `src/client/endpoints/showcases.ts`)
- **`POST /openapi/v1/oauth/token` and `POST /openapi/v1/oauth/device_authorization` [only in SDK]:** OAuth 2.0 with PKCE for the browser-based `meshy auth login`, plus a device flow (`meshy auth login --device`). — [meshy-cli](https://github.com/meshy-dev/meshy-cli) (`src/internal/oauth.ts`, `src/internal/device.ts`, `README.md`); [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) (`tests/auth-contract.test.mjs`)
- **Conflict:** the CLI comments cite "1 credit per request per the official docs" and say "the docs spell the second value `animated`", yet no such docs are public now. [not documented] — [meshy-cli](https://github.com/meshy-dev/meshy-cli) (`src/client/endpoints/showcases.ts`)
- **Absence check [not documented]:** on fresh downloads, `/showcases` and `/oauth` have 0 matches in `llms-full.txt`, and "showcases" or "oauth" have 0 matches in `openapi.json`. `/en/api/showcases` and `/en/api/oauth` return 404. — [llms-full.txt](https://docs.meshy.ai/llms-full.txt); [openapi.json](https://docs.meshy.ai/openapi.json); [showcases](https://docs.meshy.ai/en/api/showcases); [oauth](https://docs.meshy.ai/en/api/oauth)

### Inferences
- The CLI's mention of "official docs" suggests a showcases page existed or exists somewhere gated, possibly for Enterprise users. I found no such page.

### Gaps
- Whether these routes accept ordinary API keys or third-party clients: not documented.

---

## What I could not read, and why

- **Displayed text of Meshy's `PreviewStrip` and `V1Strip` banners and the switch's "Preview" note.** Only key names are in the [docs chunk](https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js). The translated strings are not in the anonymous page data or in the scripts I fetched, and the strip renders only when the `ApiV2` flag is on, which an anonymous `curl` does not trigger.
- **Meshy `/en/api/v2/<endpoint>` pages** such as [image-to-3d](https://docs.meshy.ai/en/api/v2/image-to-3d). They return 302 to v1 pages for an anonymous request, so per-endpoint v2 parameter detail is unavailable beyond the two migration pages.
- **Meshy migration skill** at `https://docs.meshy.ai/downloads/meshy-v2-migration.zip`. A header-only request returned 200 (`application/zip`, 101,438 bytes), but I did not download it. It is outside the two pages assigned, and the page asks AI agents to get the user's consent first. It claims "every v1 to v2 mapping", so it could turn the rule-only routes into literal ones if the user agrees to it being read.
- **Live behavior of any route.** Not tested, as instructed. That covers `mesh/edit` availability, the section B Tripo routes, and Meshy v2 access.
- **Current SDK repository state.** SDK and CLI evidence comes from the audit's earlier copies, not re-downloaded today, and those citations point to the repository or package with the file path in parentheses rather than to a pinned line.
- **Tripo `.md` pages for dead slugs** (`models-refine`, `models-stylize`, `generation-image-to-depth`, `files-upload-credentials`, `generation-smartsegment`). All return 404, so no reference page exists to read.
