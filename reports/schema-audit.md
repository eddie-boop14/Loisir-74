# Phase 1 — Schema audit (read-only)

**Date**: 2026-06-14
**Scope**: 392 non-draft fiches in `Json/`
**Status**: REPORT — no JSON or HTML mutated

## Bottom line

| field | present | null-ish | missing key | distinct values |
|---|---:|---:|---:|---:|
| `commune`              | 392 | 0 | 0 | 120 |
| `category`             | 392 | 0 | 0 | 24 |
| `slug`                 | 392 | 0 | 0 | 392 |
| `latitude` / `longitude` | 392 | 0 | 0 | n/a |
| `status`               | 392 | 0 | 0 | 1 (all `published`) |
| `hero_image`           | 392 | 0 | 0 | 173 distinct sources |
| `schema_org.is_free`   | 373 | 0 | **19** | 2 (True / False) |
| `schema_org.tariff_kind` | 66 | 0 | 326 | 1 (`seasonal`; missing = not-seasonal, by design) |
| `lake`                 | 31 | 0 | 361 | 3 (`annecy`/`leman`/`petits`; missing = non-lac/plage, by design) |
| `subcategories`        | 110 | 0 | 282 | 14 |
| `hero_credit`          | 148 | **237** | 7 | 36 |
| `gallery_photos`       | 14 | 378 | 0 | n/a |
| **`type`**             | **0** | 0 | **392** | **0 — field does not yet exist** |
| `schema_org.publicAccess` | 0 | 0 | 392 | 0 — never populated, can be removed |

## Why each field matters

### Fields that filters already need

- **`commune`** — filt-commune source on every hub. ✅ Complete.
- **`category`** — drives hub membership (cascade → /cascades/, etc.). ✅ Complete. 24 distinct values — biggest buckets: `attraction` (95, generic catch-all), `musee` (50), `sentier` (40), `point-de-vue` (27), `chateau` (25), `domaine` (18), `cascade` (16), `lac` (16).
- **`schema_org.is_free`** — Gratuit / Payant tag source. **19 fiches missing.** Current build defaults missing to False (Payant) — was the user-reported "Jardins de l'Europe shows Payant" class of bug. Phase 2 must populate or flag.
- **`schema_org.tariff_kind`** — Seasonal tag source. Missing = not seasonal (by design). ✅ Working as intended.
- **`lake`** — Just added on 31 lac/plage fiches. Missing on 361 = irrelevant for non-lac fiches. ✅ Complete for its domain.
- **`status`** — Draft filter. All 392 visible = published. ✅ Working as intended.

### Fields the Phase 3/4 architecture asks for

- **`type`** — the brief explicitly asks for a normalized type field driving `data-type` + photo selection. **Does not yet exist on any fiche.** Phase 2 must introduce it with a controlled vocabulary.

### Fields safe to leave alone or remove

- **`subcategories`** — only used by the sport-jeux hub filter rule. Missing on 282 fiches. Not a card-level filter input — does not need filling for filter correctness.
- **`schema_org.publicAccess`** — empty on every fiche. Dead field. Can be removed in a future cleanup, not Phase 2 priority.
- **`hero_credit`** — 237 fiches null. Not a filter input. Affects nothing user-visible. Out of scope for filter/badge work.
- **`gallery_photos`** — only 14 fiches have one. Not a filter input.

## The 19 fiches missing `schema_org.is_free`

These default to Payant in the current renderer — a known badge bug. Phase 2 must derive or set null.

- `bourg-et-ruines-chateau-chaumont-chaumont` — access hint: "Site libre · visites guidées payantes"
- `casino-saint-julien-saint-julien-en-genevois` — access hint: "Entrée libre · 18 ans révolus"
- `chateau-buffavent-lully` — access hint: "Visible de l'extérieur (propriété privée)"
- `chateau-croix-scionzier` — access hint: "Visible de l'extérieur (propriété privée)"
- `chateau-sonnaz-thonon-bains` — access hint: "Musée payant · OT libre"
- `chateau-thenieres-ballaison` — access hint: "Vue extérieure (siège CCBC)"
- `chemin-alpage-parcours-decouverte-habere-lullin` — access hint: "Accès libre · gratuit"
- `debaroule-clusaz` — access hint: "Avec forfait piéton / Pass Découverte"
- `ferme-ecomusee-clos-parchet-samoens` — access hint: "Payant · sur réservation OT"
- `grand-casino-annemasse-annemasse` — access hint: "Entrée libre · 18 ans révolus"
- `musee-art-et-folklore-regional-fessy` — access hint: "Payant"
- `musee-art-sacre-saint-gervais-bains` — access hint: "Sur rendez-vous · visites guidées"
- `musee-ermitage-calvaire-megeve` — access hint: "Entrée libre"
- `musee-nature-gruffy` — access hint: "Payant"
- `musee-paysan-un-site-paysalp-culture-patrimoine-viuz-en-sallaz` — access hint: "Payant"
- `musee-poterie-savoyarde-filliere` — access hint: "Visite guidée obligatoire · sur RDV"
- `notre-histoire-musee-rumilly-rumilly` — access hint: "Payant (mercredi gratuit)"
- `port-clerges-base-nautique-thonon-bains` — access hint: "Selon club / activité"
- `secrets-fees-parcours-decouverte-habere-poche` — access hint: "Accès libre · Livret payant"

## Category × hub mapping (membership truth-table)

| category | n | hubs it maps to |
|---|---:|---|
| `attraction` | 95 | (no hub — orphan unless in subcategories) |
| `musee` | 50 | musees |
| `sentier` | 40 | sentiers |
| `point-de-vue` | 27 | points-de-vue |
| `chateau` | 25 | chateaux |
| `domaine` | 18 | bases-de-loisirs |
| `cascade` | 16 | cascades |
| `lac` | 16 | lacs-plages |
| `parc` | 15 | bases-de-loisirs, parcs-jardins |
| `plage` | 15 | lacs-plages |
| `aquaparc` | 11 | baignade-nautisme |
| `cinema` | 11 | sorties-detente |
| `karting` | 8 | sport-jeux |
| `telecabine` | 8 | telecabines |
| `casino` | 5 | sorties-detente |
| `patinoire` | 5 | sport-jeux |
| `voie-verte` | 5 | voies-vertes |
| `base-nautique` | 4 | bases-de-loisirs, baignade-nautisme |
| `bowling` | 4 | sport-jeux |
| `divers` | 4 | — |
| `croisiere` | 4 | baignade-nautisme |
| `accrobranche` | 2 | bases-de-loisirs |
| `jardin` | 2 | parcs-jardins |
| `wakepark` | 2 | bases-de-loisirs, baignade-nautisme |

## Photo library inventory

**Total `generique-*.jpg` photos in repo root: 77**

### Per-family count vs per-hub fiche demand

| photo family | photos | best-fit hub | hub fiches | implied cycling |
|---|---:|---|---:|---:|
| `sentier-*`     | 11 | sentiers     | 40 | 3.6× |
| `voie-*`        |  6 | voies-vertes |  5 | 0.8× (headroom) |
| `karting-*`     |  5 | sport-jeux/karting | 5 | 1.0× |
| `aquatique-*`   |  4 | baignade-nautisme | 21 | 5.3× |
| `escalade-*`    |  4 | bases-de-loisirs / via-ferrata | ~7 | 1.7× |
| `musee-*` + base| 5  | musees       | 50 | **10×** ⚠ |
| `spa-*`         |  4 | spa fiches   | ~10 | 2.5× |
| `chateau-*`     |  3 | chateaux     | 25 | **8.3×** ⚠ |
| `escape-game-*` |  3 | sport-jeux/escape | ~8 | 2.7× |
| `patinoire-*`   |  3 | sport-jeux/patinoire | 5 | 1.7× |
| `lac-*` + base  |  2 | lacs-plages  | 31 | **15.5×** ⚠⚠ |
| `bowling-*`     |  2 | sport-jeux/bowling | 5 | 2.5× |
| `famille-*`     |  2 | family-adjacent fiches | many | high |
| `ferme-*`       |  2 | fermes pédagogiques | 4 | 0.5× ✓ |
| `cascade.jpg` (single) | 1 | cascades | 16 | **16×** ⚠⚠ |

**Diversity bottlenecks** (Phase 4 will hit these walls):
- `lacs-plages`: 31 fiches against 3 lake/water photos → fundamental supply problem
- `chateaux`: 25 vs 3 photos
- `musees`: 50 vs 5 photos
- `cascades`: 16 vs 1 photo

These hubs cannot achieve full per-card diversity from the current bank. Two options for Phase 4: (a) expand the library, (b) accept measured cycling with the description-based picker (which we already built into the report on `generic-hero-audit.md`).

## Phase 2 proposal — for Eddie review

### 2a — fill `schema_org.is_free` on the 19 missing fiches

Derivation logic:

1. Scan `i18n.fr.facts.access` / `facts.Accès` / `facts.tarif` / `facts.Tarif` for explicit tokens:
   - `libre`, `gratuit`, `entrée libre`, `accès libre` → `is_free=True`
   - `payant`, `tarif:`, `€`, `adulte`, `enfant` → `is_free=False`
   - both classes of tokens → `tariff_kind="seasonal"`, `is_free` stays unset
2. If neither signal is present → write `null` and add the slug to `reports/schema-completion-pending.md` for Eddie review.

### 2b — introduce `type` field with controlled vocabulary

Proposed vocab (7 values, mutually exclusive, every fiche gets exactly one):

| `type` | covers categories | rough fiche count |
|---|---|---:|
| `aquatique` | aquaparc, croisiere, base-nautique, wakepark, lac, plage, cascade (water) | 80 |
| `patrimoine` | chateau, musee | 75 |
| `nature` | sentier, point-de-vue, voie-verte, jardin, telecabine | 110 |
| `parc` | parc, domaine, accrobranche | 65 |
| `sensations` | parapente, bungee, tyrolienne, via-ferrata, escalade, canyoning, rafting, devalkart | 35 |
| `divertissement` | cinema, casino, bowling, karting, patinoire, escape-game, laser-game, vr | 35 |
| `bien-etre` | spa, thermes | ~15 |

Total = ~415; with overlaps, real fiche assignment ~392. **For Eddie**: approve the names (en français?) and the grouping before Phase 2 writes anything.

### 2c — derivation logic for `type`

```python
CATEGORY_TO_TYPE = {
    "cascade": "aquatique", "lac": "aquatique", "plage": "aquatique",
    "aquaparc": "aquatique", "croisiere": "aquatique",
    "base-nautique": "aquatique", "wakepark": "aquatique",
    "chateau": "patrimoine", "musee": "patrimoine",
    "sentier": "nature", "point-de-vue": "nature",
    "voie-verte": "nature", "jardin": "nature", "telecabine": "nature",
    "parc": "parc", "domaine": "parc", "accrobranche": "parc",
    "cinema": "divertissement", "casino": "divertissement",
    "bowling": "divertissement", "karting": "divertissement",
    "patinoire": "divertissement",
    # attraction → fallback to subcategory or "sensations" if subcat matches
}
```

For `category == "attraction"` (95 fiches), inspect `subcategories` / name to pick `sensations` / `divertissement` / `bien-etre`. Where ambiguous, write null and flag.

## Gate (Phase 1 spec): report committed. No code written.

No `Json/` files were modified during this audit. Only `reports/schema-audit.md` was created/updated. Waiting on Eddie approval of the Phase 2 proposal above before any writes.