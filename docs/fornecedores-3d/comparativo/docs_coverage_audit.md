# Tripo AI and Meshy API documentation: independent coverage audit (master checklist, snapshot 2026-11-01)

Method note: everything below comes from raw `curl` downloads and regex or script extraction over the saved files, not from sidebars or summaries. No authenticated calls were made and no request was sent to an API host, apart from one probe of `https://api.tripo3d.ai/docs` and one of `https://api.meshy.ai/openapi.json` while hunting for specs (both returned 404). Raw files: `C:\Users\Jeferson\AppData\Local\Temp\claude\e--Projetos-Kubo\f92f0908-55d6-47bf-b409-44d25c3943a1\scratchpad\audit_raw`. Helper scripts: `C:\Users\Jeferson\AppData\Local\Temp\claude\e--Projetos-Kubo\f92f0908-55d6-47bf-b409-44d25c3943a1\scratchpad\audit_scripts`. The other researchers' notes were not read.

## What is the machine-readable index of all doc pages, for each provider?

### Takeaway
Tripo has three official doc sets on three hosts, and its current one (`developers.tripo3d.ai`) has a sitemap and `llms.txt` that both miss pages: the true route table is only in the JS bundle, which adds an unlisted page, `mesh-edit`. Meshy has a sitemap, `llms.txt`, `llms-full.txt` and an OpenAPI 3.1 spec that agree on its stable v1 pages. The spec leaves out Text to Motion and Creative Lab, and none of the four mentions the unlisted "API v2" migration pages.

**Completeness verdict**

| Scope | Verdict | Basis | What could be missing |
|---|---|---|---|
| Tripo current docs pages (`developers.tripo3d.ai/en/docs/*`) | **Verified complete** for this bundle snapshot | The router only serves IDs in `PUBLIC_DOC_IDS` (44) + `UNLISTED_DOC_IDS` (1), plus aliases, and everything else returns 404 | Pages added after this bundle hash |
| Tripo legacy VitePress pages (`docs.tripo3d.ai`) | **Verified complete** | `__VP_HASH_MAP__` lists 40 EN pages, all fetched with 200 | Nothing known |
| Tripo legacy SPA docs (`platform.tripo3d.ai/docs/:name`) | **Verified complete** | Module map in the bundle lists 24 `.md` modules | Nothing known |
| Tripo endpoints | **Best effort** | Regex over all pages, the bundle's endpoint data, SDKs and the CLI | Undocumented server routes; five SDK or changelog routes have no reference page |
| Meshy stable pages (`docs.meshy.ai`) | **Verified complete for listed pages; unlisted pages exist** | Sitemap, `llms.txt` and bundle routes cross-checked | Other flag-gated pages not named in the one nav chunk examined |
| Meshy v1 endpoints | **Verified complete against the docs** | All 83 spec operations matched in page text; non-spec families confirmed by `llms.txt` | Undocumented routes such as `/openapi/v1/showcases` |
| Meshy API v2 endpoints | **Best effort** | Only the two migration pages are readable; the `/en/api/v2/*` reference URLs redirect to v1 pages | Per-endpoint v2 reference detail, and whether v2 is generally available |

### Cited Findings

**Tripo: URLs tried**

| URL | Result |
|---|---|
| `https://platform.tripo3d.ai/` + `robots.txt`, `sitemap.xml`, `sitemap-0.xml`, `sitemap_index.xml`, `sitemap-index.xml`, `llms.txt`, `llms-full.txt`, `openapi.json`, `openapi.yaml`, `swagger.json`, `api-docs`, `docs`, `docs/`, `docs/llms.txt`, `docs/sitemap.xml`, `docs/openapi.json`, `docs/llms-full.txt` | All 200 but all the same 689-byte SPA shell, so **none is a real file** |
| `https://platform.tripo3d.ai/assets/index-DQsHt00E.js` and `index-hOS3rg9a.js` | **Worked**: route table and map of 24 doc modules |
| `https://docs.tripo3d.ai/` | **Worked** (200, VitePress 1.6.4): `__VP_SITE_DATA__` sidebar and `__VP_HASH_MAP__` embedded in HTML |
| `https://docs.tripo3d.ai/robots.txt`, `sitemap.xml`, `llms.txt` | 404 |
| `https://www.tripo3d.ai/robots.txt`, `sitemap.xml`, `llms.txt` | 200, but marketing site: no API page URLs matched in the sitemap |
| `https://www.tripo3d.ai/llms-full.txt` | 404 |
| `https://www.tripo3d.ai/api` | Redirects to `https://developers.tripo3d.ai/en` (**this is how the current docs host was found**) |
| `https://api.tripo3d.ai/docs` | 404 |
| `https://developers.tripo3d.ai/robots.txt`, `sitemap.xml`, `llms.txt` | **Worked**. Sitemap: 1,177 URLs = 107 paths x 11 locales |
| `https://developers.tripo3d.ai/llms-full.txt`, `en/llms.txt`, `en/llms-full.txt`, `sitemap-0.xml`, `sitemap-index.xml`, `sitemap_index.xml`, `openapi.json`, `openapi.yaml`, `swagger.json`, `en/openapi.json`, `api/openapi.json`, `docs/openapi.json` | 404. **No OpenAPI spec found for Tripo** |
| `https://developers.tripo3d.ai/en/docs/<id>.md` | **Worked** for all 45 docs pages (raw Markdown) |
| `https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js`, `DocsPage-BEfudI-g.js` | **Worked**: `PUBLIC_DOC_IDS`, `UNLISTED_DOC_IDS`, endpoint data |
| `https://developers.tripo3d.com/sitemap.xml`, `llms.txt` (China site) | **Worked** |

- `robots.txt` on the current host points to the sitemap and to `llms.txt` — [robots.txt](https://developers.tripo3d.ai/robots.txt)
- The sitemap and `PUBLIC_DOC_IDS` match exactly (44 pages, no difference either way), so the sitemap is generated from the public list, and `mesh-edit` sits outside it in `UNLISTED_DOC_IDS=["mesh-edit"]` — [bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js); [sitemap](https://developers.tripo3d.ai/sitemap.xml)
- `llms.txt` lists 42 of those 44: it omits `plugins` and `openai-compat-images`, and also `mesh-edit` — [llms.txt](https://developers.tripo3d.ai/llms.txt)
- The `/en` and `/zh` page sets give identical `/v3` and `/v2` path lists when extracted separately — [zh docs example](https://developers.tripo3d.ai/zh/docs/introduction)

**Meshy: URLs tried**

| URL | Result |
|---|---|
| `https://docs.meshy.ai/robots.txt` | **Worked** |
| `https://docs.meshy.ai/sitemap.xml` | **Worked**: 2,756 URLs = 115 paths across 24 locales (`lastmod` 2026-10-30) |
| `https://docs.meshy.ai/llms.txt` | **Worked** (21.8 KB, index of 42 API `.md` pages) |
| `https://docs.meshy.ai/llms-full.txt` | **Worked** (1.14 MB, 30,905 lines) |
| `https://docs.meshy.ai/openapi.json`, `openapi.yaml` | **Worked** (OpenAPI 3.1.0, "Meshy API" 1.0.0, 83 operations, server `https://api.meshy.ai/openapi`) |
| `https://docs.meshy.ai/api/<slug>.md` | **Worked** for all 42 API pages. `https://docs.meshy.ai/api.md` is 404 |
| `https://docs.meshy.ai/sitemap-0.xml`, `sitemap_index.xml`, `sitemap-index.xml`, `swagger.json`, `api-docs`, `docs`, `docs/llms.txt`, `docs/sitemap.xml`, `docs/openapi.json`, `docs/llms-full.txt` | 404 |
| `https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js` | **Worked**: flag-gated `ApiV2` nav, version-switch logic |
| `https://www.meshy.ai/robots.txt`, `sitemap.xml`, `llms.txt` | 200 (marketing). `llms.txt` carries **old-style doc links** such as `docs.meshy.ai/#text-to-3d-beta` |
| `https://www.meshy.ai/llms-full.txt` | 404 |
| `https://api.meshy.ai/openapi.json` | 404 |

- Meshy's own `llms.txt` names the spec as the machine-readable contract and says "The Creative Lab and Text to Motion endpoints are **not** in the OpenAPI spec" — [llms.txt](https://docs.meshy.ai/llms.txt)
- Sitemap and `llms.txt` agree: `/en/api/*` is 43 URLs = the 42 `llms.txt` pages + the `/api` landing page; no path exists only in a non-English locale — [sitemap](https://docs.meshy.ai/sitemap.xml); [llms.txt](https://docs.meshy.ai/llms.txt)
- 113 paths are in all 24 locales; the 2 Cascadeur plugin paths are in 22 — [sitemap](https://docs.meshy.ai/sitemap.xml)
- Locales: cs de en es fr hi id it ja ko ms nl ph pl pt-BR pt-PT ru sv th tr uk vi zh zh-Hant — [sitemap](https://docs.meshy.ai/sitemap.xml)

### Inferences
- A sitemap-only or `llms.txt`-only audit of either provider would report false completeness: it would miss `POST /v3/mesh/edit` at Tripo and the whole Meshy `/openapi/v2/` family.

### Gaps
- Only the JS chunks referenced by the `/en/api` and quick-start pages were scanned on Meshy, so further flag-gated slugs could sit in chunks not fetched.
- Bundle file names contain content hashes and will rotate on the next deploy, so those citation URLs may go stale.

## What is the full list of doc page URLs for each provider, grouped by section?

### Takeaway
Tripo: 45 current English docs pages (44 listed + 1 unlisted), 40 legacy VitePress pages and 24 legacy SPA modules. Meshy: 114 English pages under `/en/` (43 API + 71 webapp) plus 2 unlisted API v2 migration pages, and the landing page.

### Cited Findings

**Tripo current docs.** Prefix `https://developers.tripo3d.ai/en/docs/`; append `.md` for raw text; `/zh/` mirrors. Source: [sitemap](https://developers.tripo3d.ai/sitemap.xml), [bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js)

| Section | Pages |
|---|---|
| Getting started | `introduction`, `quick-start`, `authentication`, `changelog` |
| Integrations | `sdk`, `plugins`*, `comfyui-nodes`, `cli`, `codex-plugin` |
| Concepts | `task-lifecycle`, `models-and-versions`, `billing` |
| 3D generation, H series | `generation-text-to-model/standard`, `generation-image-to-model/standard`, `generation-multiview-to-model/standard` |
| 3D generation, P series | `generation-text-to-model/p`, `generation-image-to-model/p`, `generation-multiview-to-model/p` |
| Gaussian splat | `generation-image-to-splat` |
| Image generation | `generation-text-to-image`, `generation-image-to-image`, `generation-image-to-multiview`, `generation-edit-multiview` |
| Model processing | `models-texture`, `models-convert`, `models-import` |
| Mesh operations | `mesh-segment`, `mesh-smartsegment`, `mesh-complete`, `mesh-uv`, `mesh-decimate`, **`mesh-edit`** (unlisted) |
| Animation | `animations-rig-check`, `animations-rig`, `animations-retarget` |
| Common | `task-query`, `task-batch-query`, `files`, `files-presign`, `account` |
| Guides | `error-handling`, `rate-limits`, `webhooks`, `migration-v2-to-v3`, `openai-compat-images`* |

`*` = in the sitemap but not `llms.txt`.

- Aliases: `generation-text-to-model`, `generation-image-to-model` and `generation-multiview-to-model` resolve to their `/standard` page (`DOC_ALIASES`) — [bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js)
- Non-docs English pages on the same host: `models` (6), `pricing`, `terms`, `support`, `collaboration-program`, `blog` (4), `cookbook` (8), `showcase` (38), `events` (2). No HTML `/v3` path was matched in the pricing page — [sitemap](https://developers.tripo3d.ai/sitemap.xml)
- China site has two extra pages, `docs/b2b-payment` and `docs/invoice-guide`, and `mesh-edit` also returns 200 there — [China sitemap](https://developers.tripo3d.com/sitemap.xml); [mesh-edit](https://developers.tripo3d.com/en/docs/mesh-edit)
- Bundle-labelled but dead slugs: `models-refine` ("Refine Model (deprecated)") and `models-stylize` ("Stylize (deprecated)") return 404 — [bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js); [models-refine](https://developers.tripo3d.ai/en/docs/models-refine)
- Also probed and 404: `tasks`, `generation-image-to-depth`, `files-upload-credentials`, `models-edit`, `mesh-local-edit`, `playground` — [example](https://developers.tripo3d.ai/en/docs/generation-image-to-depth)

**Tripo legacy VitePress docs.** Prefix `https://docs.tripo3d.ai/`, `.html`, zh under `/zh/`; "Tripo OpenAPI docs", documents V2. Source: [site](https://docs.tripo3d.ai/)

| Section | Pages |
|---|---|
| get-started | `introduction`, `quick-start`, `overview`, `pricing`, `errors-and-error-handling`, `rate-limits`, `changelog` |
| file-upload | `upload-in-sts`, `quick-upload-directly` |
| task-query | `get-your-task-result` |
| image-generation | `basic-text-to-image`, `advanced-image-generation`, `multiview-image` |
| model-generation | `image-to-model-p1-20260311`, `image-to-model-v3-0-v3-1`, `image-to-model-v2-0-v2-5`, `image-to-model-turbo-v1-0-20250506`, `image-to-model-v1-4-20240625`, `text-to-model-p1-20260311`, `text-to-model-v3-0-v3-1`, `text-to-model-v2-0-v2-5`, `text-to-model-turbo-v1-0-20250506`, `text-to-model-v1-4-20240625`, `multiview-to-model-p1-20260311`, `multiview-to-model-v3-0-v3-1`, `multiview-to-model-v2-0-v2-5`, `import-model` |
| texture | `texture-model-v3-0-20250812`, `texture-model-v2-5-20250123` |
| mesh-editing | `mesh-segmentation-v1-0-20250506`, `mesh-completion-v1-0-20250506`, `smart-low-poly-p-v2-0-20251225` |
| animation | `pre-rig-check-v2-0-20250506`, `rig-v2-5-20260210`, `rig-v2-0-20250506`, `rig-v1-0-20240301`, `retarget` |
| export | `conversion` |
| other | `support-faq` |
| root | `index` |

**Tripo legacy SPA docs.** Route `https://platform.tripo3d.ai/docs/:name` — [bundle](https://platform.tripo3d.ai/assets/index-hOS3rg9a.js)

| Section | Modules |
|---|---|
| endpoint | `animation`, `editing`, `general`, `generate-image`, `generate-multiview-image`, `generation`, `import-model`, `post-process`, `schema`, `task`, `texture`, `upload-sts`, `upload`, `wallet` |
| get-started | `changelog`, `introduction`, `quick-start` |
| guide | `code-examples`, `error-handling`, `prompt` |
| other | `billing`, `faq`, `limit` |
| test | `test` (549-byte stub) |

- That SPA's main bundle carries a "Tripo API V2 is being retired" banner linking to the V3 migration guide — [bundle](https://platform.tripo3d.ai/assets/index-DQsHt00E.js)

**Meshy API pages.** Prefix `https://docs.meshy.ai/en/api/`; `.md` at `https://docs.meshy.ai/api/<slug>.md`. Source: [llms.txt](https://docs.meshy.ai/llms.txt)

| Section | Pages |
|---|---|
| Getting started | `quick-start`, `developer-platform`, `authentication`, `errors`, `pricing`, `rate-limits`, `task-lifecycle`, `asset-retention`, `deprecations`, `webhooks`, `metadata`, `ai`, `changelog` |
| 3D generation | `text-to-3d`, `image-to-3d`, `multi-image-to-3d` |
| Post-processing | `remesh`, `convert`, `resize`, `uv-unwrap`, `retexture`, `rigging`, `animation`, `text-to-motion` |
| 2D generation | `text-to-image`, `image-to-image` |
| 3D printing | `multi-color-print`, `analyze-printability`, `repair-printability`, `auto-split` |
| Creative Lab | `creative-lab-keychain`, `-fridge-magnet`, `-figure`, `-vinyl-figure`, `-brick-figure`, `-lamp`, `-keycap`, `-fidget-collapsible`, `-fidget-pixel` |
| Account | `balance`, `usage` |
| Reference | `animation-library` |
| Landing | `https://docs.meshy.ai/en/api` |

**Meshy API v2 pages (not in the sitemap, `llms.txt` or `llms-full.txt`)**
- [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2) and [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference) both return 200 as HTML; their `.md` versions are 404.
- `/en/api/v2`, `/quick-start`, `/tasks`, `/errors`, `/rate-limits`, `/webhooks`, `/metadata` and `/asset-retention` redirect to the v1 equivalents for an anonymous request. The `/api/v2/tasks` URL lands on `task-lifecycle` — [chunk](https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js); [example](https://docs.meshy.ai/en/api/v2/tasks)
- The chunk gates the nav on an `ApiV2` flag and names these v2 page slugs: `text-to-3d`, `image-to-3d`, `multi-image-to-3d`, `remesh`, `convert`, `resize`, `uv-unwrap`, `rigging`, `animation`, `text-to-motion`, `retexture`, `text-to-image`, `image-to-image`, `multi-color-print`, `analyze-printability`, `repair-printability`, `auto-split`, `balance`, `usage` — [chunk](https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js)

**Meshy webapp pages (71).** Prefix `https://docs.meshy.ai/en/webapp/`. Source: [sitemap](https://docs.meshy.ai/sitemap.xml)

| Section | Pages |
|---|---|
| Top level | `3d-agent`, `changelog`, `concepts`, `getting-started`, `glossary`, `image-to-3d`, `pricing`, `text-to-3d` |
| `3d-printing-platforms/` | `introduction`, `bambu-studio`, `creality-print`, `elegoo-slicer`, `flash-studio`, `lychee-slicer`, `orcaslicer`, `snapmaker`, `ultimaker-cura`, `xtool-studio` |
| `guides/3d-model/` | `ai-texturing`, `auto-split`, `batch-images-to-3d`, `remesh`, `rigging`, `unwrap-uv` |
| `guides/` other | `animate`, `prompting`, `texture-edit`, `choosing/generation-method`, `choosing/integration`, `choosing/post-processing`, `image/ai-image-generation`, `platform/asset-management`, `platform/export-formats`, `scene-video/scene-compose`, `scene-video/video-generation`, `use-cases/3d-printing`, `use-cases/game-assets` |
| `plugins/` | `3dsmax/*` (3), `blender/*` (7), `cascadeur/*` (2), `codex/introduction`, `godot/*` (3), `hermes-agent/introduction`, `maya/*` (3), `omniverse/*` (2), `openclaw/introduction`, `roblox/*` (2), `unity/*` (3), `unreal/*` (4), `zbrush/*` (2) |

Other Meshy URL behavior:
- [`/en/api/playground`](https://docs.meshy.ai/en/api/playground) redirects to `developer-platform`, though the changelog still links it.
- [`/en/api/text-to-texture`](https://docs.meshy.ai/en/api/text-to-texture) returns 500, while `text-to-voxel`, `showcases`, `showcase` and `oauth` return 404.

### Inferences
- The `/en/api/text-to-texture` 500 is probably a stale route for the retired API, since the deprecations page lists that API as retired, but this was not confirmed.

### Gaps
- The content of individual Meshy `/en/api/v2/<endpoint>` pages could not be read, since they are flag-gated.

## What is the flat master list of every HTTP endpoint and every Tripo task `type`?

### Takeaway
Tripo V3 has 28 operations documented in the current page set, plus 5 further V3 routes mentioned elsewhere without a reference page. Meshy has 83 spec operations, plus 90 non-spec v1 operations when Creative Lab is expanded per stage, for 173 v1 operations; a preview `/openapi/v2/` family sits on top.

### Cited Findings

#### Tripo V3 (base `https://openapi.tripo3d.ai/v3`; China `https://openapi.tripo3d.com/v3`)
Sources: page `**Endpoint:**` lines and the [DocsPage bundle](https://developers.tripo3d.ai/assets/DocsPage-BEfudI-g.js) `method`/`path` data, with the China base from the [V2 to V3 skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md). Page IDs are under `https://developers.tripo3d.ai/en/docs/`.

| # | Method + path | Page | Source of proof |
|---|---|---|---|
| 1 | `POST /v3/generation/text-to-model` | `generation-text-to-model/standard`, `/p` | Endpoint line + bundle |
| 2 | `POST /v3/generation/image-to-model` | `generation-image-to-model/standard`, `/p` | Endpoint line + bundle |
| 3 | `POST /v3/generation/multiview-to-model` | `generation-multiview-to-model/standard`, `/p` | Endpoint line + bundle |
| 4 | `POST /v3/generation/image-to-splat` | `generation-image-to-splat` | Endpoint line + bundle |
| 5 | `POST /v3/generation/text-to-image` | `generation-text-to-image` | Endpoint line + bundle |
| 6 | `POST /v3/generation/image-to-image` | `generation-image-to-image` | Endpoint line + bundle |
| 7 | `POST /v3/generation/image-to-multiview` | `generation-image-to-multiview` | Endpoint line + bundle |
| 8 | `POST /v3/generation/edit-multiview` | `generation-edit-multiview` | Endpoint line + bundle |
| 9 | `POST /v3/models/texture` | `models-texture` | Endpoint line + bundle |
| 10 | `POST /v3/models/convert` | `models-convert` | Endpoint line + bundle |
| 11 | `POST /v3/models/import` | `models-import` | Endpoint line + bundle |
| 12 | `POST /v3/animations/rig-check` | `animations-rig-check` | Endpoint line + bundle |
| 13 | `POST /v3/animations/rig` | `animations-rig` | Endpoint line + bundle |
| 14 | `POST /v3/animations/retarget` | `animations-retarget` | Endpoint line + bundle |
| 15 | `POST /v3/mesh/segment` | `mesh-segment` | Endpoint line + bundle |
| 16 | `POST /v3/mesh/smartsegment` | `mesh-smartsegment` | Endpoint line + bundle |
| 17 | `POST /v3/mesh/complete` | `mesh-complete` | Endpoint line + bundle |
| 18 | `POST /v3/mesh/decimate` | `mesh-decimate` | Endpoint line + bundle |
| 19 | `POST /v3/mesh/uv` | `mesh-uv` | Endpoint line + bundle |
| 20 | `POST /v3/mesh/edit` | [`mesh-edit`](https://developers.tripo3d.ai/en/docs/mesh-edit.md) (**unlisted**) | Endpoint line + bundle |
| 21 | `GET /v3/tasks/{task_id}` | `task-query` | Endpoint line + bundle |
| 22 | `POST /v3/tasks/list` | `task-batch-query` | Endpoint line + bundle |
| 23 | `POST /v3/files` | `files` | Endpoint line + bundle |
| 24 | `POST /v3/files/presign` | `files-presign` | Endpoint line + bundle |
| 25 | `GET /v3/account/balance` | `account` | Endpoint line + bundle |
| 26 | `GET /v3/account/usage` | [`account`](https://developers.tripo3d.ai/en/docs/account.md) | **Body only** (no Endpoint line, no bundle entry) |
| 27 | `POST /v3/openai/images/generations` | `openai-compat-images` | Endpoint line + bundle |
| 28 | `POST /v3/openai/images/edits` | [`openai-compat-images`](https://developers.tripo3d.ai/en/docs/openai-compat-images.md) | **Body only** |

Outbound, not an API route: `POST https://<your-endpoint>` with events `task.completed`, `task.failed` and `balance.low` — [webhooks](https://developers.tripo3d.ai/en/docs/webhooks.md)

**V3 routes without a reference page**

| Route | Where it appears | Status per source |
|---|---|---|
| `POST /v3/generation/image-to-depth` | [SDK route matrix](https://developers.tripo3d.ai/en/docs/sdk.md) (Python only) and [`tripo3d/client.py`](https://github.com/Tripo-Developer/tripo-python-sdk) | Live status unknown, page 404 |
| `POST /v3/files/upload-credentials` | [Changelog](https://developers.tripo3d.ai/en/docs/changelog.md), [migration skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md), Java internal descriptor | Described as usable by the skill, page 404 |
| `POST /v3/models/refine` | [Changelog](https://developers.tripo3d.ai/en/docs/changelog.md), [migration guide](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) | **Conflict**: [SDK page](https://developers.tripo3d.ai/en/docs/sdk.md) says retired, [bundle](https://developers.tripo3d.ai/assets/index-D5Z6j8UU.js) label says deprecated, [rate limits](https://developers.tripo3d.ai/en/docs/rate-limits.md) still names refine |
| `POST /v3/models/stylize` | [Changelog](https://developers.tripo3d.ai/en/docs/changelog.md), [migration guide](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) | **Conflict**: same as refine |
| `POST /v3/generation/smartsegment` | Java SDK `GatewayDenylist.java` only | **SDK-only**; meaning not verified, and no docs mention |

No cancel, delete or task-list-by-filter route was found in the V3 docs. The migration skill says task cancel and list "never existed in V2 either" — [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)

#### Tripo V2 (base `https://api.tripo3d.ai/v2/openapi`; China `https://api.tripo3d.com/v2/openapi`; see the retirement dates in the next section)

| Method + path | Source |
|---|---|
| `POST /task` | [Legacy quick start](https://docs.tripo3d.ai/get-started/quick-start.html); [SPA module](https://platform.tripo3d.ai/assets/task-B2vcs7xa.js) |
| `GET /task/{task_id}` | [Legacy quick start](https://docs.tripo3d.ai/get-started/quick-start.html) |
| `POST /upload` | [Migration guide](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md); [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `POST /upload/sts` | [SPA module](https://platform.tripo3d.ai/assets/upload-sts-XXIAuI4A.js) |
| `POST /upload/sts/token` | [SPA module](https://platform.tripo3d.ai/assets/upload-sts-XXIAuI4A.js) |
| `POST /upload/temporary_token` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) only |
| `POST /task/batch` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) only |
| `GET /task/watch/:id` (WebSocket), `/task/watch/all[/:since]` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) only |
| `GET /user/balance` | [SPA wallet module](https://platform.tripo3d.ai/assets/wallet-C0HLJP2u.js) |
| `GET /user/wallet/balance` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md). **Conflicts** with the row above |
| `POST /user/wallet/usage/detail` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) only |
| `/provider/bailian/v1/submit`, `/query` (China, Bailian/DashScope) | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md): "separate product surface" |

Legacy theme config confirms `/task`, `/task/:task_id`, `/upload/sts` and `/upload/sts/token` — [legacy theme](https://docs.tripo3d.ai/assets/chunks/theme.QCUCtqai.js)

#### Tripo task `type` values

**V2 request `type`** (required body field on `POST /v2/openapi/task`)

| Value | V3 route | Where it appears |
|---|---|---|
| `text_to_model` | `/v3/generation/text-to-model` | [Legacy pages](https://docs.tripo3d.ai/model-generation/text-to-model-v3-0-v3-1.html); [migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) |
| `image_to_model` | `/v3/generation/image-to-model` | [Legacy pages](https://docs.tripo3d.ai/model-generation/image-to-model-v3-0-v3-1.html) |
| `multiview_to_model` | `/v3/generation/multiview-to-model` | [Legacy pages](https://docs.tripo3d.ai/model-generation/multiview-to-model-v3-0-v3-1.html) |
| `text_to_image` | `/v3/generation/text-to-image` | [Legacy page](https://docs.tripo3d.ai/image-generation/basic-text-to-image.html) |
| `generate_image` | `/v3/generation/image-to-image` | [Legacy page](https://docs.tripo3d.ai/image-generation/advanced-image-generation.html) |
| `generate_multiview_image` | `/v3/generation/image-to-multiview` | [Legacy page](https://docs.tripo3d.ai/image-generation/multiview-image.html) |
| `edit_multiview_image` | `/v3/generation/edit-multiview` | [Legacy page](https://docs.tripo3d.ai/image-generation/multiview-image.html) |
| `texture_model` | `/v3/models/texture` | [Legacy page](https://docs.tripo3d.ai/texture/texture-model-v3-0-20250812.html) |
| `refine_model` | `/v3/models/refine` | [SPA `generation` module](https://platform.tripo3d.ai/assets/generation-FO0UWqad.js); [migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) |
| `stylize_model` | `/v3/models/stylize` | [SPA `post-process` module](https://platform.tripo3d.ai/assets/post-process-BRpTjnot.js); [migration](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) |
| `convert_model` | `/v3/models/convert` | [Legacy page](https://docs.tripo3d.ai/export/conversion.html) |
| `import_model` | `/v3/models/import` | [Legacy page](https://docs.tripo3d.ai/model-generation/import-model.html) |
| `animate_prerigcheck` | `/v3/animations/rig-check` | [Legacy page](https://docs.tripo3d.ai/animation/pre-rig-check-v2-0-20250506.html) |
| `animate_rig` | `/v3/animations/rig` | [Legacy page](https://docs.tripo3d.ai/animation/rig-v2-5-20260210.html) |
| `animate_retarget` | `/v3/animations/retarget` | [Legacy page](https://docs.tripo3d.ai/animation/retarget.html) |
| `mesh_segmentation` | `/v3/mesh/segment` | [Legacy page](https://docs.tripo3d.ai/mesh-editing/mesh-segmentation-v1-0-20250506.html) |
| `mesh_completion` | `/v3/mesh/complete` | [Legacy page](https://docs.tripo3d.ai/mesh-editing/mesh-completion-v1-0-20250506.html) |
| `highpoly_to_lowpoly` | `/v3/mesh/decimate` | [Legacy page](https://docs.tripo3d.ai/mesh-editing/smart-low-poly-p-v2-0-20251225.html) |
| `classification` | none (retired) | [Skill §7](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `render_video` | none (retired) | [Skill §7](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `render_image` | none ("no V3 route") | [Skill §7](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |

Conflict: the legacy changelog 1.8.0 names a task type `smart_low_poly`, while the page's required value is `highpoly_to_lowpoly` — [changelog](https://docs.tripo3d.ai/get-started/changelog.html); [page](https://docs.tripo3d.ai/mesh-editing/smart-low-poly-p-v2-0-20251225.html)

**V3 response `type`** (V3 has "no `type` field in the body"; a value comes back in task data — [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)). Values found by regex in current-page examples:
- `text_to_model`, `image_to_model`, `multiview_to_model`, `text_to_image`, `image_to_image`, `image_to_multiview`, `image_to_splat`
- `texture_model`, `convert_model`, `import_model`
- `animate_prerigcheck`, `animate_rig`, `animate_retarget`
- `mesh_segmentation`, `mesh_completion`, `highpoly_to_lowpoly`, `mesh_uv`, `smartsegment_image`

Sources: the page for each route under [docs](https://developers.tripo3d.ai/en/docs/introduction); `smartsegment_image` from [mesh-smartsegment](https://developers.tripo3d.ai/en/docs/mesh-smartsegment.md). `edit_multiview` appears in backticks in the multiview-to-model page and `mesh_edit` in the CLI [chain table](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz).

Webhook envelope `type` values (not task types): `task.completed`, `task.failed`, `balance.low` — [webhooks](https://developers.tripo3d.ai/en/docs/webhooks.md)

#### Meshy v1 and stable (base `https://api.meshy.ai`)

**In the OpenAPI spec: 83 operations** — [openapi.json](https://docs.meshy.ai/openapi.json). Each row below is a 5-operation set (`POST` create, `GET` list, `GET /{id}`, `DELETE /{id}`, `GET /{id}/stream`), and all paths carry the `/openapi` prefix.

| Family | Base path | Page |
|---|---|---|
| Text to 3D | `/openapi/v2/text-to-3d` | [text-to-3d](https://docs.meshy.ai/api/text-to-3d.md) |
| Image to 3D | `/openapi/v1/image-to-3d` | [image-to-3d](https://docs.meshy.ai/api/image-to-3d.md) |
| Multi-Image to 3D | `/openapi/v1/multi-image-to-3d` | [multi-image-to-3d](https://docs.meshy.ai/api/multi-image-to-3d.md) |
| Retexture | `/openapi/v1/retexture` | [retexture](https://docs.meshy.ai/api/retexture.md) |
| Remesh | `/openapi/v1/remesh` | [remesh](https://docs.meshy.ai/api/remesh.md) |
| Convert | `/openapi/v1/convert` | [convert](https://docs.meshy.ai/api/convert.md) |
| Resize | `/openapi/v1/resize` | [resize](https://docs.meshy.ai/api/resize.md) |
| UV Unwrap | `/openapi/v1/uv-unwrap` | [uv-unwrap](https://docs.meshy.ai/api/uv-unwrap.md) |
| Rigging | `/openapi/v1/rigging` | [rigging](https://docs.meshy.ai/api/rigging.md) |
| Animation | `/openapi/v1/animations` | [animation](https://docs.meshy.ai/api/animation.md) |
| Text to Image | `/openapi/v1/text-to-image` | [text-to-image](https://docs.meshy.ai/api/text-to-image.md) |
| Image to Image | `/openapi/v1/image-to-image` | [image-to-image](https://docs.meshy.ai/api/image-to-image.md) |
| Multi-Color Print | `/openapi/v1/print/multi-color` | [multi-color-print](https://docs.meshy.ai/api/multi-color-print.md) |
| Auto Split | `/openapi/v1/print/split` | [auto-split](https://docs.meshy.ai/api/auto-split.md) |
| Repair Printability | `/openapi/v1/print/repair` | [repair-printability](https://docs.meshy.ai/api/repair-printability.md) |
| Analyze Printability | `/openapi/v1/print/analyze` | [analyze-printability](https://docs.meshy.ai/api/analyze-printability.md) |

That is 16 x 5 = 80, plus three single operations:
- `GET /openapi/v1/animations/library` — [animation-library](https://docs.meshy.ai/api/animation-library.md)
- `GET /openapi/v1/balance` — [balance](https://docs.meshy.ai/api/balance.md)
- `GET /openapi/v1/usage/tasks` — [usage](https://docs.meshy.ai/api/usage.md)

Mechanical cross-check: every spec operation matched a method + path mention in the page text or `llms-full.txt`, and no operation is flagged `deprecated` in the spec, though 21 `deprecated: true` flags exist on other items — [openapi.json](https://docs.meshy.ai/openapi.json)

**Not in the spec, documented on pages: 90 operations when expanded**

| Family | Operations | Page |
|---|---|---|
| Text to Motion | `POST /openapi/v1/text-to-motion`; `GET` list; `GET /:id`; `GET /:id/stream`; `DELETE /:id` (5) | [text-to-motion](https://docs.meshy.ai/api/text-to-motion.md) |
| Creative Lab, two-stage: `keychain`, `fridge-magnet`, `figure`, `vinyl-figure`, `brick-figure`, `lamp`, `keycap`, `fidget-pixel` | Under `/openapi/creative-lab/<product>/v1`: `POST /prototype`; `POST /build`; `GET /(prototype\|build)/:id`; `DELETE /(prototype\|build)/:id`; `GET /(prototype\|build)/:id/stream`; `GET /(prototype\|build)` (6 headings = 10 operations; x 8 = 80) | [keychain](https://docs.meshy.ai/api/creative-lab-keychain.md), [fridge-magnet](https://docs.meshy.ai/api/creative-lab-fridge-magnet.md), [figure](https://docs.meshy.ai/api/creative-lab-figure.md), [vinyl-figure](https://docs.meshy.ai/api/creative-lab-vinyl-figure.md), [brick-figure](https://docs.meshy.ai/api/creative-lab-brick-figure.md), [lamp](https://docs.meshy.ai/api/creative-lab-lamp.md), [keycap](https://docs.meshy.ai/api/creative-lab-keycap.md), [fidget-pixel](https://docs.meshy.ai/api/creative-lab-fidget-pixel.md) |
| Creative Lab, single-stage: `fidget-collapsible` | `POST /openapi/creative-lab/fidget-collapsible/v1`; `GET` list; `GET /:id`; `GET /:id/stream`; `DELETE /:id` (5) | [fidget-collapsible](https://docs.meshy.ai/api/creative-lab-fidget-collapsible.md) |

Counting note: 83 + 5 + 80 + 5 = **173 operations** when expanded per stage, or 141 when counting doc headings. Per-product headings were read directly for keychain and fidget-pixel; for the other six the same pattern is confirmed by the regex matches on `POST .../prototype`, `POST .../build`, `GET`, and `DELETE`.

**Deprecated alias:** `/v2/text-to-3d` without `/openapi` still works, returning `Deprecation` and `Link` headers; removal date to be announced — [changelog](https://docs.meshy.ai/api/changelog.md); [deprecations](https://docs.meshy.ai/api/deprecations.md)

**Other documented surfaces:**
- `/openapi/v2` base also exists for reads of Text to 3D — [text-to-3d](https://docs.meshy.ai/api/text-to-3d.md)
- Outbound webhooks are managed in the Developer Platform UI; no webhook management route was found — [webhooks](https://docs.meshy.ai/api/webhooks.md)
- `X-Meshy-Metadata` request header — [metadata](https://docs.meshy.ai/api/metadata.md)

#### Meshy API v2 (preview, unlisted)

"Preview" is my reading of a `PreviewStrip` component in the docs chunk; the pages I read do not use a status label.

Stated explicitly on the pages — [Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2); [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference):
- `GET /openapi/v2/tasks/{id}`
- `GET /openapi/v2/tasks?type=<type>`
- `GET /openapi/v2/tasks/{id}/stream`
- `DELETE /openapi/v2/tasks/{id}`
- `POST /openapi/v2/image-to-3d`
- `POST /openapi/v2/text-to-3d`, with its own read routes returning a different shape; the preview-and-refine flow "is deprecated and keeps working for existing integrations"
- `GET /openapi/v2/usage/tasks`
- `/openapi/v2/convert`, `/openapi/v2/resize`, `/openapi/v2/multi-image-to-3d`, `/openapi/v2/remesh`, `/openapi/v2/retexture`, `/openapi/v2/text-to-image`, each seen as a literal in the pages

Stated as a rule: "Every /openapi/v1 endpoint that creates a task has a v2 version at the same path under /openapi/v2/, and so do Balance, Usage, and Animation Library", "Per-endpoint read routes ... don't exist on v2", and "Creative Lab and the other v1 endpoints have no v2 version" — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

Other v2 facts: webhooks gain a payload version set on the Webhooks page and a `Meshy-Webhook-Version` header; results move under `output` with `input` echoed — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

### Inferences
- From that rule, these v2 create or read paths should also exist but were not seen as literals: `POST /openapi/v2/{uv-unwrap, rigging, animations, text-to-motion, print/multi-color, print/analyze, print/repair, print/split, image-to-image}`, `GET /openapi/v2/balance`, `GET /openapi/v2/animations/library`. These are derived and should be labelled as such.
- That would make the v2 surface one create route per task family plus the four shared task routes and Text to 3D reads, with the v1 surface still in place. No source gives a v1 end date.
- Tripo's `mesh/edit` page exists but is deliberately left out of the index, and the CLI comment says it "stays hidden" until it is "listed and live", so it should be treated as not generally available.

### Gaps
- Whether Meshy API v2 is live for all accounts is unconfirmed. The site gates its nav on an `ApiV2` flag and renders a `PreviewStrip`, but I did not find its message text, and calling the API to test it is out of scope.
- `smartsegment_image` is the only literal `type` on the SmartSegment page, even though the page accepts image or GLB input; a GLB-input `type` may exist.
- `image_to_multiview`, `edit_multiview` and `mesh_edit` response `type` strings have only partial evidence: example or code literal, not a full enumeration. No official enum of V3 `type` values was found.
- The regex could not match paths written relatively in body text. Mitigated for Tripo by also extracting `**Endpoint:**` lines, which show relative paths.

## What do the changelogs say was added, changed or deprecated, especially in the last 12 months (Nov 2025 to Oct 2026)?

### Takeaway
Tripo moved its API to V3 in April 2026 and scheduled V2 to stop accepting requests at 2026-10-31 16:00 UTC, which has already passed as of today. Meshy shipped 13 new endpoint families (counting Creative Lab once, with nine products), the `meshy-7.1` and `meshy-t2.5` models and several retirements, and has an unlisted API v2 that appears to be in preview.

### Cited Findings

#### Tripo: sunset dates
- **V2 end of updates and support:** "Starting October 1, 2026, 00:00 UTC+8 (September 30, 2026, 16:00 UTC)" — [platform bundle banner](https://platform.tripo3d.ai/assets/index-DQsHt00E.js)
- **V2 retirement:** "Starting November 1, 2026, 00:00 UTC+8 (October 31, 2026, 16:00 UTC) ... all V2 API endpoints will stop accepting requests" — [platform bundle banner](https://platform.tripo3d.ai/assets/index-DQsHt00E.js). The SDK page says the V2 API is "scheduled to shut down on 2026-10-31" and Python SDK 0.x stops working after it — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md)
- `chat_image_1` retires 2026-10-23, `chat_image_1.5` retires 2026-12-01 — [changelog](https://developers.tripo3d.ai/en/docs/changelog.md); [models](https://developers.tripo3d.ai/en/docs/models-and-versions.md)
- Rig `v2.0-20250506` deprecated in 1.9.7 (2026-06-03), replaced by `v2.5-20260210` — [SPA changelog](https://platform.tripo3d.ai/assets/changelog-CvHlgjEX.js); "no longer exists" in V3 — [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- Model versions `v1.3-20240522`, `v1.4-20240625`, `v2.0-20240919` and `Turbo-v1.0-20250506` are "retired versions (already erroring on V2)" — [skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md). **Conflict:** legacy pages for v1.4 and Turbo remain online, and the [ComfyUI nodes page](https://developers.tripo3d.ai/en/docs/comfyui-nodes.md) still mentions `v1.4-20240625` and `v2.0-20240919`.

#### Tripo: timeline

| Date | Change | Source |
|---|---|---|
| 2026-10 | Rig `v3.0-20260909` (opt-in); `rig_type=others`; `spec` adds `actorcore`, `unity`, `unreal`, `vrm`; rig-check accepts GLB/FBX/OBJ/STL; new retarget algorithm | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-10 | Retopology `model=v3.0` (35/40 credits), `smart_uv`; **new `POST /v3/mesh/uv`** (20 credits) | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-09 | Texture `v3.5-20260815`; `texture_version`; `texture_quality=fast`; `delight` | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-09 | `chat_image_2.5_flare`, `chat_image_2.5_sunburst`; `quality`, `background`; custom sizes | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-08 | `P2-20260801` with `quad`; correction: `credits_consumed`, `balance`, `frozen` are decimals | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-08-17 | 1.9.8: `animate_retarget` preset whitelist tied to rig version | [SPA changelog](https://platform.tripo3d.ai/assets/changelog-CvHlgjEX.js) |
| 2026-06-03 | 1.9.7: `texture_quality=extreme`; tiered texture pricing; rig v2.0 deprecated | [SPA changelog](https://platform.tripo3d.ai/assets/changelog-CvHlgjEX.js) |
| 2026-04 | **API v3.0**: dedicated endpoints replacing the universal task endpoint; base URL simplified; `POST /v3/tasks/list`, `POST /v3/files/upload-credentials`, `GET /v3/account/usage` | [changelog](https://developers.tripo3d.ai/en/docs/changelog.md) |
| 2026-04-14 | 1.9.6: `generate_multiview_image`, `edit_multiview_image` task types | [legacy changelog](https://docs.tripo3d.ai/get-started/changelog.html) |
| 2026-03-11 | 1.9.5: Tripo v3.1, `P1-20260311`, Rig v2.5 | [legacy changelog](https://docs.tripo3d.ai/get-started/changelog.html) |
| 2026-03-09 | 1.9.4: image handling fix; autofix; credit usage in task response | [legacy changelog](https://docs.tripo3d.ai/get-started/changelog.html) |
| 2025-12-30 | 1.9.3: v3.0 speed and texture improvements; v2.0 low-poly model | [legacy changelog](https://docs.tripo3d.ai/get-started/changelog.html) |
| 2025-11-04 | 1.9.2: multiview-to-model on v3.0 | [legacy changelog](https://docs.tripo3d.ai/get-started/changelog.html) |

Changelog gaps, found mechanically: `image-to-splat`, `smartsegment`, `files/presign`, `openai/images/*` and `mesh/edit` have **no entry** in the current changelog, because the path regex matched them on other pages only — [changelog](https://developers.tripo3d.ai/en/docs/changelog.md). Also, the legacy VitePress changelog stops at 1.9.6, while the SPA copy continues to 1.9.8 — [legacy](https://docs.tripo3d.ai/get-started/changelog.html); [SPA](https://platform.tripo3d.ai/assets/changelog-CvHlgjEX.js)

#### Meshy: model and feature status (from [deprecations](https://docs.meshy.ai/api/deprecations.md))

| Item | State | Deprecated | Retirement |
|---|---|---|---|
| `meshy-7.1`, `meshy-6`, `meshy-6-lite`, `meshy-t2.5`, `meshy-t2` | Active | N/A | N/A |
| `meshy-7` | Deprecated | 2026-09-18 | To be announced |
| `/v2/text-to-3d` without `/openapi` | Deprecated | 2026-09-29 | To be announced |
| `meshy-5` | Retired | 2026-09-11 | 2026-10-10 |
| `meshy-t1`, `model_type: "lowpoly"` | Retired | 2026-07-13 | 2026-10-30 |
| Shared test-mode API key | Retired | 2026-09-16 | 2026-09-16 |
| `meshy-4` | Retired | N/A | 2026-03-20 |
| `meshy-3` | Retired | 2025-01-14 | July 2025 |
| Text to Voxel API | Retired | 2025-10-01 | 2025-10-01 |
| Text to Texture API | Retired | 2025-07-01 | 2025-07-01 |

Deprecated parameters: `texture_image_url` on Rigging (2026-10-23), `ultra_mode` (2026-09-18), `hd_texture` (2026-07-21), Remesh convert and resize parameters (2026-05-22), `symmetry_mode` (2026-05-11), `art_style` (2026-01-22), `is_a_t_pose` (2025-12-04) — [deprecations](https://docs.meshy.ai/api/deprecations.md). `video_url` on Text to 3D deprecated 2025-12-22 — [changelog](https://docs.meshy.ai/api/changelog.md).

`latest` resolves to `meshy-7.1`, except Retexture, whose newest is `meshy-7` — [deprecations](https://docs.meshy.ai/api/deprecations.md); [llms.txt](https://docs.meshy.ai/llms.txt)

#### Meshy: timeline of new endpoints and models (all from the [changelog](https://docs.meshy.ai/api/changelog.md))

| Date | Addition |
|---|---|
| 2026-10-30 | `keep_texture` on Auto Split; meshy-t1 retired |
| 2026-10-26 | Deprecations page |
| 2026-10-21 | `X-Meshy-Metadata` header |
| 2026-10-15 | `meshy-t2.5` |
| 2026-10-14 | `model_url` up to 400 MB |
| 2026-10-10 | meshy-5 retired; Balance adds `monthly_credits`, `permanent_credits`, `monthly_resets_at` |
| 2026-10-06 | Printability thin-wall checks |
| 2026-09-28 | Rate limit headers; `printer_brand` on Multi-Color Print |
| 2026-09-18 | `meshy-7.1`, `geometry_resolution` |
| 2026-09-15 | `gpt-image-2-5-flare`, `gpt-image-2-5-sunburst` |
| 2026-09-11 | `meshy-6-lite`; `DELETE` on an `IN_PROGRESS` task now returns 409 |
| 2026-09-09 | **Auto Split API** |
| 2026-09-05 | **Creative Lab Fidget Pixel** |
| 2026-09-04 | **`GET /openapi/v1/animations/library`**, **Creative Lab Collapsible Fidget** |
| 2026-09-02 | `action_ids` on Animation |
| 2026-08-28 | **Usage API** |
| 2026-08-26 | `motion_task_id` on Animation |
| 2026-08-21 | **Text to Motion API** |
| 2026-08-13 and 08-12 | `meshy-7`; Smart Topology on Text to 3D |
| 2026-07-27 | **Creative Lab Brick Figure** |
| 2026-07-22 | **Creative Lab Keycap** |
| 2026-07-21 | `texture_resolution` (8K) |
| 2026-07-20 | **Creative Lab Vinyl Figure** |
| 2026-07-13 | Smart Topology on Image to 3D with `meshy-t1` and `meshy-t2` |
| 2026-06-15 | **UV Unwrap API** |
| 2026-06-01 | **Creative Lab**: Keychain, Fridge Magnet, Figure, Lamp |
| 2026-05-22 | **Convert API, Resize API** |
| 2026-05-07 | **Analyze Printability, Repair Printability APIs** |
| 2026-04-27 | `consumed_credits` on all tasks |
| 2026-04-02 | **Multi-Color Print API**; 3MF `target_formats` |
| 2026-03-20 | meshy-4 retired |
| 2026-01-19 and 01-26 | `latest` resolves to Meshy 6; Meshy-6 on Multi-Image |
| 2025-12-31 | **Text to Image, Image to Image APIs**; API Playground |
| 2025-12-22 | `video_url` deprecated |
| 2025-11-24 | `save_pre_remeshed_model` |
| 2025-11-06 | `latest` for Meshy-6-preview on Refine, Image to 3D, Multi-Image, Retexture |

The changelog records no entry for API v2: searching it found only the `/v2/text-to-3d` path deprecation — [changelog](https://docs.meshy.ai/api/changelog.md). The v2 reference does say the `/openapi`-less path "is deprecated" and points to the changelog — [v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)

### Inferences
- Since V2 retirement was scheduled for 2026-10-31 16:00 UTC, an integration written today should treat all V2 endpoints and `type` values as historical. This rests on the published schedule, not a live test.

### Gaps
- Actual post-sunset V2 behavior was not tested, per the no-API-calls constraint, and no source confirmed the shutdown executed on schedule.
- Whether `chat_image_1` really retired on 2026-10-23 is unconfirmed: the models page still words it "retiring 2026-10-23".
- No date or status for Meshy API v2 general availability, or for any v1 sunset, was found.
- The Tripo changelog has no explicit dated announcement of refine and stylize retirement.

## What is officially offered around the API but outside the main reference?

### Takeaway
Both providers offer MCP servers, CLIs, DCC plugins and agent skills. Tripo has five official REST SDKs; Meshy's API docs list no REST SDK, and neither provider's docs offer a current sandbox or test key.

### Cited Findings

**Tripo**
- **SDKs:** [JS `@vastai/tripo-sdk` v0.5.0](https://github.com/Tripo-Developer/tripo-js-sdk), [Python `tripo3d` v1.0.0](https://github.com/Tripo-Developer/tripo-python-sdk), [Go v0.5.0](https://github.com/Tripo-Developer/tripo-go-sdk), [Rust `tripo3d-sdk` v0.5.0](https://github.com/Tripo-Developer/tripo-rust-sdk), [Java, source build at `7b6a68d`](https://github.com/Tripo-Developer/tripo-java-sdk) — pinned on the [SDK page](https://developers.tripo3d.ai/en/docs/sdk.md)
- **CLI:** `npm i -g tripo-cli` (0.9.0 on npm); also runs as an MCP server through `tripo mcp`; resumable batch processing — [cli](https://developers.tripo3d.ai/en/docs/cli.md); [npm](https://registry.npmjs.org/tripo-cli/latest)
- **MCP server:** "Official MCP server for Tripo", last pushed 2025-04-14 — [tripo-mcp](https://github.com/Tripo-Developer/tripo-mcp)
- **Plugins:** Unity 1.0.1, Unreal 1.0, Blender 0.7.3, Godot 0.02, Cocos Creator 1.0.0, ComfyUI 1.1.21, each with a download link — [plugins](https://developers.tripo3d.ai/en/docs/plugins.md)
- **ComfyUI nodes:** the reference covers 11 nodes in ComfyUI-Tripo 1.3.0, **conflicting** with 1.1.21 on the plugins page; the source link goes to `VAST-AI-Research/ComfyUI-Tripo`, while the org listing shows [Tripo-Developer/ComfyUI-Tripo](https://github.com/Tripo-Developer/ComfyUI-Tripo) — [comfyui-nodes](https://developers.tripo3d.ai/en/docs/comfyui-nodes.md)
- **Blender extension source:** [tripo-3d-for-blender](https://github.com/Tripo-Developer/tripo-3d-for-blender)
- **Codex plugin:** "Tripo 3D" plugin in Codex — [codex-plugin](https://developers.tripo3d.ai/en/docs/codex-plugin.md)
- **Other org repos (not documented on the pages):** [Hermes plugin](https://github.com/Tripo-Developer/tripo-hermes-plugin), [DeepSeek Harness plugin](https://github.com/Tripo-Developer/Tripo3D-Plugin-dsh), [Echo3D Bridge](https://github.com/Tripo-Developer/Tripo-Echo3D-Bridge)
- **Migration skill:** downloadable `SKILL.md` for coding agents, moving V2 code to V3; it is the most detailed V2 inventory found — [SKILL.md](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)
- **OpenAI-compatible Images API:** base `https://openapi.tripo3d.ai/v3/openai` — [openai-compat-images](https://developers.tripo3d.ai/en/docs/openai-compat-images.md)
- **Batch:** `POST /v3/tasks/list` is a batched **read** only; no batch-create API was found. The CLI offers client-side batch — [task-batch-query](https://developers.tripo3d.ai/en/docs/task-batch-query.md); [cli](https://developers.tripo3d.ai/en/docs/cli.md)
- **Test mode, sandbox:** no hits for "sandbox", "test key" or "test mode" across the 44 pages — [docs](https://developers.tripo3d.ai/en/docs/introduction)
- **Slicer integrations:** no hits for "slicer" or "bambu" in the 44 pages; Bambu Lab, Creality and Anycubic appear only as partner links on the [landing page](https://developers.tripo3d.ai/en)
- **Status page:** [tripo3d.statuspage.io](https://tripo3d.statuspage.io/)

**Meshy**
- **MCP server:** `@meshy-ai/meshy-mcp-server`, 8 client installs — [ai](https://docs.meshy.ai/api/ai.md); [repo](https://github.com/meshy-dev/meshy-mcp-server)
- **CLI:** `npm i -g meshy-cli`, used by agent plugins — [repo](https://github.com/meshy-dev/meshy-cli); mentioned in [llms-full.txt](https://docs.meshy.ai/llms-full.txt)
- **Agent skills:** [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent); [DeepSeek Harness skills](https://github.com/meshy-dev/meshy-dsh)
- **DCC connectors:** [meshy-dcc-core](https://github.com/meshy-dev/meshy-dcc-core), [meshy-dcc-adapters](https://github.com/meshy-dev/meshy-dcc-adapters)
- **Plugins:** Blender, Unity, Unreal, Godot, Maya, 3ds Max, Cascadeur, Omniverse, Roblox, ZBrush, Codex, Hermes Agent, OpenClaw — [plugins example](https://docs.meshy.ai/en/webapp/plugins/blender/introduction); [sitemap](https://docs.meshy.ai/sitemap.xml)
- **Slicer integrations:** Bambu Studio, Creality Print, Elegoo Slicer, Flash Studio, Lychee, OrcaSlicer, Snapmaker, Cura, xTool Studio — [intro](https://docs.meshy.ai/en/webapp/3d-printing-platforms/introduction). The MCP tool `meshy_send_to_slicer` is also listed — [ai](https://docs.meshy.ai/api/ai.md)
- **Playground and dashboards:** Developer Platform, no-code endpoint testing and logs — [developer-platform](https://docs.meshy.ai/api/developer-platform.md)
- **Test mode:** the shared key was **retired 2026-09-16**, and requests sending it return 401 — [changelog](https://docs.meshy.ai/api/changelog.md). **Stale:** [`llms.txt`](https://docs.meshy.ai/llms.txt) still describes the Authentication page as covering a "test-mode key", while [the page itself](https://docs.meshy.ai/api/authentication.md) has no hits for "test".
- **Batch:** a webapp-only guide exists; no batch API route was found — [batch-images-to-3d](https://docs.meshy.ai/en/webapp/guides/3d-model/batch-images-to-3d)
- **Cookbook:** [meshy-cookbook](https://github.com/meshy-dev/meshy-cookbook)
- **SDK claim conflict:** [www.meshy.ai/llms.txt](https://www.meshy.ai/llms.txt) says "SDKs available for Python, JavaScript, and Unity", yet no REST SDK repo is in the [meshy-dev org list](https://api.github.com/orgs/meshy-dev/repos?per_page=100&sort=updated), and the API pages have no "SDK" hits in quick start or AI integration. The cookbook has helper modules at `shared/python/meshy.py` and `shared/typescript/meshy.ts`.
- **Status page:** [status.meshy.ai](https://status.meshy.ai) — [llms.txt](https://docs.meshy.ai/llms.txt)

### Inferences
- `tripo-mcp` was last pushed in April 2025, before the V3 launch, while `tripo mcp` in the CLI is current, so the CLI is likely the maintained MCP route. Its code had no matches to the V3 route regex, but this was not otherwise verified.

### Gaps
- Plugin version currency was taken from doc pages, with no independent check.
- Plugin ZIPs and non-listed repos were not inspected for routes.

## Which endpoints appear in official SDK repos but not the docs, or the reverse?

### Takeaway
Tripo and Meshy each have a small set of SDK-only routes, and most are explained: `mesh/edit` turned out to be an unlisted doc page, while `image-to-depth` and Meshy's `showcases` have no reference page. Going the other way, Tripo's OpenAI-compatible routes are not in the SDK matrix, and Meshy has no REST SDK to compare.

### Cited Findings

Scope: repo HEAD as of 2026-11-01, downloaded as tarballs and grepped but never executed. Repos: 10 under [Tripo-Developer](https://github.com/Tripo-Developer), 6 under [meshy-dev](https://github.com/meshy-dev), plus the [tripo-cli 0.9.0 npm tarball](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz). VAST-AI-Research holds research repos like TripoSR, with no API SDK found in its [org list](https://api.github.com/orgs/VAST-AI-Research/repos?per_page=100&sort=updated). `meshyai` and `MeshyAI` orgs returned 404; [Meshy-AI](https://github.com/Meshy-AI) only has a `.github` repo.

**SDK or tool only (label: SDK-only)**

| Route | Found in | Docs status | Notes |
|---|---|---|---|
| `POST /v3/generation/image-to-depth` | [Python SDK](https://github.com/Tripo-Developer/tripo-python-sdk) `tripo3d/client.py`, `docs/API.md` | Only named in the [SDK matrix](https://developers.tripo3d.ai/en/docs/sdk.md); no reference page | Parameters undocumented on the site |
| `POST /v3/generation/smartsegment` | [Java SDK](https://github.com/Tripo-Developer/tripo-java-sdk) `GatewayDenylist.java` | None | The docs name `/v3/mesh/smartsegment` |
| `POST /v3/models/refine`, `POST /v3/models/stylize` | [Java SDK](https://github.com/Tripo-Developer/tripo-java-sdk) `EndpointDescriptor.java`, `docs/API.md` | Changelog and migration only | SDK page: "Java still has legacy methods; Python's `refine_model` and `stylize_model` raise an error without sending a request" — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md) |
| `POST /v3/files/upload-credentials` | [Java SDK](https://github.com/Tripo-Developer/tripo-java-sdk) `EndpointDescriptor.java` | Changelog + SDK page note; no reference page | SDK page: "internal ... descriptor has no public client flow" — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md) |
| `POST /v3/mesh/edit` | [tripo-cli](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) `dist/knowledge/chains.js`, `dist/commands/mcp-full.js` | **Unlisted page** [mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md) | CLI comment: "has a reference page that is still left out of the docs index, and cn returned 4001 when last checked. The step stays hidden; set TRIPO_EXPERIMENTAL_MESH_EDIT=1 to opt in" |
| `<consoleApi>/cli/device/code`, `/cli/device/token` | [tripo-cli](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz) `dist/core/device-auth.js` | None | Device login on the console API, not the public API |
| `GET /openapi/v1/showcases` | [meshy-cli](https://github.com/meshy-dev/meshy-cli) `src/client/endpoints/showcases.ts` | **Absent** from spec, `llms-full.txt` and sitemap; `/en/api/showcases` is 404 | Code comment: "Enterprise showcase search ... may be billed (1 credit per request per the official docs)", which I could not confirm in the public docs |
| `/openapi/v1/oauth/device_authorization`, `/openapi/v1/oauth/token` | [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) and [meshy-cli](https://github.com/meshy-dev/meshy-cli) tests | **Absent** from public docs | CLI browser sign-in; methods not verified |
| `/openapi/v1/text-to-texture` | [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) `CHANGELOG.md` | Retired | Text to Texture retired 2025-07-01 — [deprecations](https://docs.meshy.ai/api/deprecations.md) |

False positives excluded after checking: `/upload/image` in ComfyUI-Tripo `web/tripo_import.js` looks like ComfyUI's own route; `/models` and `/task` in the Hermes plugin's `dashboard/plugin_api.py` look like the plugin's own dashboard API; `/openapi/v1/text-to-3d/abc` in `meshy-cli` `tests/transport.test.ts` is a test fixture; `/tasks/task_*` are test IDs.

**Also out of scope for the public API:** `https://platform.tripo3d.ai` console routes `/v2/platform/usage/history/recharge`, `/alert/credit-threshold`, `/payment` and `/usage/wallet` — [recharge chunk](https://platform.tripo3d.ai/assets/index-B7o9ks_G.js); [billing chunk](https://platform.tripo3d.ai/assets/index-CnuRGrkO.js). These are console-internal strings and not offered as API.

**Docs but not in SDKs (reverse direction)**
- **Tripo, per the official matrix:** Python lacks SmartSegment. JS, Go and Rust lack image-to-depth. Java lacks text-to-image, image-to-image, edit-multiview, SmartSegment, Smart UV and image-to-depth — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md). The grep agrees: Java's `GatewayDenylist.java` holds the text-to-image, image-to-image, edit-multiview and smartsegment routes, `/v3/mesh/uv` and image-to-depth did not appear in the Java output, image-to-depth appeared in Python only, and smartsegment did not appear in Python.
- **Tripo, not in the matrix at all:** `POST /v3/openai/images/generations`, `POST /v3/openai/images/edits` and `POST /v3/mesh/edit` — [sdk](https://developers.tripo3d.ai/en/docs/sdk.md). JS, Go and Rust READMEs do mention `/v3/openai` as a string.
- **Meshy:** there is no official REST SDK to compare. Route strings aggregated across the six meshy-dev repos include print, Creative Lab, UV Unwrap and Text to Motion, but I did not check coverage per repo — [meshy-mcp-server](https://github.com/meshy-dev/meshy-mcp-server); [meshy-cli](https://github.com/meshy-dev/meshy-cli).

### Inferences
- The tripo-cli comment suggests that `mesh/edit` may not be live in the China region, though the page returns 200 on the China host; this comes from one code comment with an undated check.

### Gaps
- SDKs were checked at repo HEAD, not at the locked versions on the SDK page; results could differ slightly.
- The Tripo route grep ran on strings only, so a dynamically built path could be missed.
- Java `GatewayDenylist.java` semantics were inferred from its name and its match with the matrix, not from reading its logic.
- Meshy's `showcases` documentation may exist behind login or for Enterprise accounts; that could not be checked without an account.
