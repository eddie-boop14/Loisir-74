# ARCHITECTURE — Loisirs74.fr

> The map of the machine. If your mental model and this file disagree, trust the repo —
> but this is kept honest against `main`. Last verified against HEAD `0ec8940` (2026-06-16).

## One sentence
A flat, static, multilingual leisure guide for Haute-Savoie, built from `Json/*.json` by a
Python pipeline, gated in CI, pushed to `main`, deployed by Netlify, and refreshed by
scheduled GitHub Actions.

## The one law
**JSON is the spine.** `Json/<slug>.json` is the single source of truth. Everything else —
HTML, hubs, sitemap, llms.txt, schema — is *generated* from it. Never hand-edit built HTML;
fix the source JSON or the builder, then re-render. Markdown files in the repo are
handoffs/reports, **not** pipeline inputs.

---

## Data model
- `Json/<slug>.json` — one per lieu (~392). Holds slug, category, commune, lat/long, i18n
  block (6 langs), hero_image, hero_credit, status, sources, freshness, partners, etc.
- `lieux.json` / `catalog-index.json` — generated catalog spines used by hubs + Studio.
- `dt-candidates.json` — 3056 DATAtourisme candidates not yet in the catalog (ingest queue).
- `photo-credits.json` — per-slug hero author/license/credit.

## Build pipeline (Python — the live renderer)
Entry point: `scripts/build_all.py` (Netlify build command). Chain:
1. `build_all_locales.py` → `build_lieu_page.build_page(d, lang)` — renders every fiche ×6 langs.
2. `build_catalog_index.py` — regenerates the catalog.
3. `build_hubs.py` — regenerates the ~15 category hubs from JSON.
4. `build_communes.py` — commune pages.
5. (optional) `build_site.py` — publishable `_site/` tree **+ generates `studio-consts.js`,
   sitemap, llms.txt**. Also: `build_homepage.py`, `fix_hreflang_sitemap.py`,
   `build_catalog_index.py`, transport/parking indexes.

Errors are fixed at **source JSON or builder script**, then re-rendered. Never patch output.

## CI / automation (GitHub Actions)
| Workflow | Trigger | Does |
|---|---|---|
| `build-gate.yml` | every push to `main` + PRs | `build_all.py` with gates: status, hygiene (0 scaffolding leaks), full 2352-HTML render, catalog, hubs, **placement gate (protects chez-nous-a-la-plage + chalet-du-tornet hosts)**, **partner-card byte-diff gate**, reachability (0 orphans ×6 langs), byte-stable double-build. Red = deploy blocked. |
| `check-loisirs74.yml` | manual + monthly (1st, 06:00) | `check_loisirs74.py` — Google Places per fiche: `place_id`, location, hours; **haversine drift** vs fiche coords. Commits report + updates. |
| `sweep-loisirs74.yml` | manual + monthly (1st, 07:00) | `sweep_loisirs74.py` — triangulates each fiche vs Google Places + French business registry + official site fetch; writes `freshness` block into JSON. |
| `review-agent.yml` | manual + weekly (Mon, 06:00) | `review_agent.py` — AI verdicts → `reports/review-verdicts.json` (artifact, **human-gated, never auto-applied**). |
| `watch-station-tarifs.yml` | manual + 1st of sept–fév + avril | `watch_sources.py` (generic watcher, stations = client #1) — diffs official tarif pages vs `reports/watch/` snapshots → dated report with witnesses. **Detection-only: never writes a fiche**; ≥10 % fetch failures trips the breaker (red run, no retry). |

Doctrine bots : **watchers detect, humans apply — no exceptions.** Une ligne CHANGED
d'un watcher est un travail pour la voie supervisée report→verify→apply, jamais une
écriture automatique.

Local audits (read-only, run on demand): `audit_venue_locations.py` (commune/centroid/envelope),
`audit_hygiene.py`, `audit_breadcrumbs.py`, `audit_hero_themes.py`, `audit_venues_external.py`.

## Deploy
Push to `main` (Eddie, from Samsung) → Netlify builds via `build_all.py` → live.
`netlify.toml`, `_headers`, `_redirects`. GSC + Bing verified.

## Discovery / AI surface
`robots.txt`, `robots-ai.txt`, `.well-known/ai-info.json`, `sitemap.xml` (2652 URLs, real
lastmod), `llms.txt` + `llms-full.txt`. **Known drift:** `llms.txt` still says 5 langs / 393
— regenerate to 6 langs (incl. nl) / 392.

## Studio (browser authoring toolkit) — and its drift
`studio.html` + 7 JS modules, 100% client-side. Tabs: research, picker, build, editor,
enricher, **phototheque** (Wikimedia+Openverse, pulls Commons credit), **dt-importer**.
- **Role:** authors/enriches **JSON**, which the Python pipeline then renders.
- **Drift / caution:** `studio-render.js` is a port of `render-v3.py` — **which no longer
  exists**. Its `studio-consts.js` is stale (5 langs, no nl) and it doesn't emit the
  Itinéraire/map link. **Do not ship Studio's Build-tab HTML as production.** The Python
  pipeline is the renderer. (See `STUDIO-ADJUSTMENTS.md`.)

> **Studio ingress rule.** Studio output enters the repo **only** as a dotted-path patch
> applied via `scripts/apply_studio_patch.py`. A full `<slug>.json` from Studio must **never**
> be written to `Json/` directly — that reverts any value updated upstream since load (sweep
> `freshness`, ingested locales, `place_id`). The key-drop gate catches lost *keys*; it cannot
> catch reverted *values*. **The ingress is the wall; the gate is the backstop.**
> (See `SPEC-studio-data-safety.md`.)

## Protected — never touch without explicit go
`chez-nous-a-la-plage` and `chalet-du-tornet` (the restaurant partners) and any partner
block (e.g. Chez Nous block inside `criq-parc`). Guarded by the placement + card-diff CI
gates. Byte-faithful.

## Geo-verify (planned, ~70% present)
`check`/`sweep` already capture `place_id` + Google location + drift monthly. Remaining:
persist `google_place_id` + `geo_verified` + `geo_verified_date` into JSON on small-drift
matches; render a ✅ badge; use `place_id` in the Itinéraire link (kills the pin bug at root);
Studio handles the human-verify tail.

---
*2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés* 🦆
