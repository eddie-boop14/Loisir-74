# Phase 2 — flags for Eddie review

**Date**: 2026-06-14
**Scope**: every fiche where Phase 2 derivation could not assign a value without guessing

## Summary

- Phase 2a (`schema_org.is_free`): **6 fiches flagged** (out of 19 missing). 13 derived cleanly + committed in `e7836920`.
- Phase 2b (`type`): **0 flagged** (pass 1 had 18; pass 2 resolved all of them with richer description-keyword rules). 392 / 392 assigned + committed in `c2e3dceb`.

## 2a — `schema_org.is_free` flags (need decision per fiche)

All 6 share the same shape: the `facts.access` text describes a **situation** (private property, on-appointment, club-dependent) rather than a price. The derivation script wrote nothing — `is_free` remains absent on these 6.

For each fiche below: pick `True` (treat as free since no entry fee mentioned) or `False` (treat as paid since visit is conditional).

| slug | name | `facts.access` hint | `facts.tarif` hint | options |
|---|---|---|---|---|
| `chateau-buffavent-lully` | Château de Buffavent | "Visible de l'extérieur (propriété privée)" | "Pas de visite intérieure" | `True` / `False` |
| `chateau-croix-scionzier` | Château de la Croix | "Visible de l'extérieur (propriété privée)" | "Pas de visite intérieure" | `True` / `False` |
| `chateau-thenieres-ballaison` | Château de Thénières | "Vue extérieure (siège CCBC)" | "Pas de visite intérieure régulière" | `True` / `False` |
| `musee-art-sacre-saint-gervais-bains` | Musée d'art Sacré | "Sur rendez-vous · visites guidées" | "" | `True` / `False` |
| `musee-poterie-savoyarde-filliere` | Musée de la Poterie Savoyarde | "Visite guidée obligatoire · sur RDV" | "Voir 04 50 62 01 90" | `True` / `False` |
| `port-clerges-base-nautique-thonon-bains` | Port des Clerges - Base Nautique | "Selon club / activité" | "" | `True` / `False` |

### Recommended quick decision rule

- **3 châteaux private/exterior-only** (`chateau-buffavent-lully`, `chateau-croix-scionzier`, `chateau-thenieres-ballaison`): if exterior view is free from a public road → `is_free=True`. If access requires private-property crossing or paid event → `is_free=False`.
- **`musee-art-sacre-saint-gervais-bains`** and **`musee-poterie-savoyarde-filliere`**: both on-appointment. Convention on the site so far is "guided visit on RDV" = paid (donation/honoraires expected). Default → `is_free=False`.
- **`port-clerges-base-nautique-thonon-bains`**: club-dependent prices. The port itself is public-access → `is_free=True`; the activities inside have separate fees (handled via `tariff_kind=seasonal` if Eddie prefers).

Tell me the verdict per row and I will apply in a Phase 2 patch commit before moving to Phase 3.

## 2b — `type` flags

**None.** Both passes resolved all 392 fiches. Distribution:

| type | n |
|---|---:|
| `nature` | 89 |
| `patrimoine` | 75 |
| `aquatique` | 71 |
| `divertissement` | 54 |
| `sensations` | 44 |
| `parc` | 38 |
| `bien-etre` | 3 |

### Edge cases resolved (no Eddie decision needed, just FYI)

A few fiches landed in a type that's defensible but not the only choice. Listing them so you can verify:

| slug | type | rationale |
|---|---|---|
| `spa-vitam-bien-etre-neydens` | `aquatique` | major aquaparc footprint (25 m pool, 9 slides) dominates the bien-être component, per Phase 4 brief ("Vitam → pool photo"). |
| `golf-practice-belvedere-saint-martin-bellevue` | `sensations` | outdoor sport — pass 2 description-keyword rule |
| `disc-golf-indiana-ventures-samoens` | `sensations` | outdoor sport activity |
| `segway-mobilboard-annecy` | `sensations` | guided gyropode tour, novelty experience |
| `ulm-leman-cervens` | `sensations` | baptême de l'air, aerial |
| `acro-aventures-*` / `parcours-aventure-*` / `indiana-ventures-*` | `parc` | accrobranche parks — match the architecture brief's parc bucket |
| `criq-parc` / `full-land-annecy` | `parc` | indoor/outdoor playgrounds, "parc de jeux" |
| `padel-*` / `billard-*` / `bar-a-jeux-*` / `atelier-poterie-*` | `divertissement` | indoor games / workshops |

## Gate (Phase 2 spec)

- ✅ All writes confined to `Json/` and `reports/`
- ✅ Phase 2a and 2b committed separately (`e7836920` + `c2e3dceb`)
- ✅ No build changes (`scripts/build_hubs.py` and `scripts/build_all.py` untouched in Phase 2)
- ⏸ **Phase 3 does not start** until Eddie reviews this report and assigns values to the 6 flagged `is_free` cases.