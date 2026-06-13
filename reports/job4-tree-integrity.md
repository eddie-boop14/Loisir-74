# JOB 4 — Tree & sitemap integrity

Run on `main` post-JOB-3 + hub regeneration.

## (1) Per-locale page counts vs canonical Json/

| locale | fiche HTMLs | non-fiche chrome | total | missing fiches |
|---|---|---|---|---|
| fr | 392 | 10 | 402 | 0 |
| en | 392 | 8 | 400 | 0 |
| de | 392 | 8 | 400 | 0 |
| it | 392 | 8 | 400 | 0 |
| es | 392 | 8 | 400 | 0 |
| nl | 392 | 1 | 393 | 0 |

✓ Every locale renders every canonical fiche. NL chrome gap (only `index`) is a known JOB 7 follow-up.

## (2) Sitemap integrity

- `sitemap.xml`: 2,458 `<loc>` entries.
- Phantom URLs (sitemap claims, disk lacks): **0**.
- Unlisted-on-disk: 28 — all intentional chrome exclusions (cgv, merci-*, signaler, mentions-legales, politique-confidentialite, studio across 5 locales, 404). Plus `en/plateau-de-beauregard.html` was a true stale orphan; removed in this commit.

Raw diff: `reports/job4-sitemap-diff.json`.

## (3) Reachability BFS — **CLOSED, zero orphans**

| locale | hubs reached | content nodes | reachable | orphans |
|---|---|---|---|---|
| fr | 15 | 407 | 407 | **0** |
| en | 15 | 407 | 407 | **0** |
| de | 15 | 407 | 407 | **0** |
| it | 15 | 407 | 407 | **0** |
| es | 15 | 407 | 407 | **0** |
| nl | 15 | 407 | 407 | **0** |

### Path to zero

| step | FR orphans | per-locale orphans |
|---|---|---|
| pre-hub regen (initial scan) | 70 | 84 |
| `build_hubs.py` (13 hubs, union mode) | 3 | 18 |
| + locale homepage "All categories" nav | 3 | 3 |
| + fix 3 casinos miscategorized as `attraction` → `casino` in JSON | **0** | **0** |

### How regen avoids regression

`build_hubs.py` runs in **union mode**: for each hub, the new card grid is the union of (a) every fiche currently linked from the existing hub HTML (preserves all hand-curated cross-references like `musee-chateau-annecy` in `chateaux/`) and (b) every fiche whose `category` matches the hub's filter rule. Result: no fiche ever dropped, missing ones always added.

Hubs regenerated (13 of 15 — `que-faire` and `sensations-plein-air` are curated cross-cuts left untouched):

| hub | prev fiches | post-regen | added |
|---|---|---|---|
| cascades | 16 | 16 | 0 |
| chateaux | 20 | 26 | 6 |
| musees | 24 | 50 | 26 |
| points-de-vue | 28 | 29 | 1 |
| sentiers | 15 | 40 | 25 |
| telecabines | 12 | 12 | 0 |
| voies-vertes | 5 | 5 | 0 |
| lacs-plages | 31 | 31 | 0 |
| bases-de-loisirs | 76 | 85 | 9 |
| parcs-jardins | 25 | 31 | 6 |
| baignade-nautisme | 24 | 24 | 0 |
| sorties-detente | 19 | 22 | 3 (the 3 casinos after JSON fix) |
| sport-jeux | 53 | 53 | 0 |

### Homepage patch

5 locale homepages (`en/`, `de/`, `it/`, `es/`, `nl/`) lacked nav links to `voies-vertes` (greenways/radwege/vie-verdi/vias-verdes/fietsroutes) and `sorties-detente` (outings-relax/ausfluege-erholung/uscite-relax/salidas-relax/uitstapjes-ontspanning). Patched with an idempotent `<section class="all-categories">` block before `</main>` listing every hub. FR homepage already had them; not touched.

### JSON data fix

3 casinos had `category="attraction"` in Json/ (likely an early-import default):
- `casino-saint-julien-saint-julien-en-genevois`
- `grand-casino-annemasse-annemasse`
- `stelsia-casino-megeve`

Corrected to `category="casino"` — the `sorties-detente` filter then picks them up automatically.

## Findings vs. audit

> Audit: "nl tree has 408 pages vs en 416, 2 missing from sitemap."

| audit claim | reality |
|---|---|
| nl = 408, en = 416 | both 400/393 fiches+chrome; per-locale fiche counts identical at 392 |
| 2 missing from sitemap | 1 stale orphan (`en/plateau-de-beauregard.html`, purged) + 28 intentional chrome exclusions |
| reachability green | initial scan: 70 FR orphans (35× audit estimate) — caused by hub drift + homepage nav gaps + JSON categorization. Now 0 across all 6 locales. |

## Open JOB 1 gate (standing reminder)

The salvage commit (`6dbb1ea2`) recomputed `scripts/translation-coverage-report.json`. Numbers:

| lang | body translated | FR-text in lang block | missing block |
|---|---|---|---|
| en | 208 | 116 | 68 |
| de | 189 | 135 | 68 |
| it | 118 | 206 | 68 |
| es | 95 | 229 | 68 |
| nl | 296 | 28 | 68 |

JOB 1's gate is technically closed (file exists, 90/90 samples passed). Per your standing instruction, **JOB 5 must not begin until you've reviewed these numbers and signed off on the residue split**.
