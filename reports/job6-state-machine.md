# JOB 6 — State machine: status field on every fiche

## Status distribution

| status | count | meaning |
|---|---|---|
| published | **392** | rendered to public site, indexed in sitemap, listed in hubs/catalog |
| verified | 0 | reserved — JOB 8's freshness sweep will use this when a fresh sweep confirms a fiche post-ingest but before official publish |
| draft | 0 | not published; HTMLs removed from every tree; not in sitemap/hubs/catalog |

## Migration rule (this round)

```python
def derive_status(d):
    fr = (d.get("i18n", {}) or {}).get("fr") or {}
    name = fr.get("name")
    if not name or len(str(name).strip()) < 3:
        return "draft"
    return "published"
```

Purely additive: every fiche that was shipping continues to ship. The `sparse_data: true` flag was NOT used as a draft signal — it was an early-import marker that was never cleared even when fiches got fully enriched (1700-char bodies, 3-4 verify_flags, fully published). 2 stale `sparse_data: true` flags cleared in this commit as housekeeping.

## What the state machine enforces (build_all integration)

When a fiche's `status` becomes `draft`:

| step | behavior |
|---|---|
| `build_all_locales` | skips the fiche, deletes any existing `<slug>.html` from root + 5 locale trees |
| `build_catalog_index` | omits from `catalog-index.json` |
| `build_hubs` | omits from every hub's card grid |
| `build_site` (`_site/Json/`) | omits the JSON from public export |
| `build_site` (`_site/content/<slug>.md`) | omits the markdown mirror |
| `build_site` (`_site/sitemap.xml`) | filters out URLs whose target no longer exists |

All 6 mechanisms verified by demote-restore round trip on `ancien-remparts-chateau-lullin-lullin`:
- demote → 6 HTMLs removed (FR + 5 locales), 0 orphans post-rebuild
- restore → all 6 HTMLs re-rendered, fiche back in all surfaces

## Build_all status gate

`scripts/build_all.py` runs `status_gate()` as the very first step. Any fiche
without an explicit `status` field fails the build with exit 1. Forces the
state machine to be honored on every commit.

## Surprises

- 2 fiches had `sparse_data: true` from early DataTourisme import provenance
  but had since been fully enriched (1700-char bodies, all 6 locales,
  schema_amenities, partners). Treating `sparse_data` as the draft signal
  would have silently deleted 12 published HTMLs. Stale flags cleared:
  - `ecomusee-bois-foret-thones`
  - `thermes-saint-gervais-mont-blanc`

## What this enables for JOB 8

JOB 8 (freshness sweep wired to state machine) can now:
- Detect dead `official_site_url` → demote fiche to `draft` with one line: `d["status"] = "draft"; save()`
- Detect business closure signal (Google Maps "Permanently closed") → same.
- Detect fresh-confirmed → upgrade `verified` → `published` with research_log entry.

The next build pass automatically propagates the demotion to every surface.
