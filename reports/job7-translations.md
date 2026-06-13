# JOB 7 — Finish the translation set (CLOSED)

## Status

**Gate met.** All 392 fiches now have an in-language `body.what_is` across all 5 non-FR locales. No FR-residue. No missing blocks.

## Coverage progression

| stage | en | de | it | es | nl |
|---|---|---|---|---|---|
| campaign start | 208 tr / 116 res / 68 miss | 189 / 135 / 68 | 116 / 208 / 68 | 95 / 229 / 68 | 296 / 28 / 68 |
| JOB 7 wave 1 (5 fiches sample) | 213 / 116 / 63 | 192 / 135 / 63 | 121 / 206 / 63 | 96 / 229 / 63 | 301 / 28 / 63 |
| JOB 7 wave 2 (16 fiches) | 229 / 116 / 47 | 208 / 137 / 47 | 133 / 212 / 47 | 104 / 241 / 47 | 317 / 28 / 47 |
| JOB 7 wave 3 (parallel × 4 agents, 16 fiches) | 245 / 116 / 31 | 224 / 137 / 31 | 144 / 217 / 31 | 114 / 247 / 31 | 333 / 28 / 31 |
| JOB 7 wave 4 (final 31 missing-block fiches × 5) | 274 / 118 / 0 | 247 / 145 / 0 | 161 / 231 / 0 | 119 / 273 / 0 | 360 / 32 / 0 |
| JOB 7 wave 5 (parallel × 4 agents, 160-fiche FR-residue cleanup) | 363 / 29 / 0 | 335 / 57 / 0 | 225 / 167 / 0 | 157 / 235 / 0 | 367 / 25 / 0 |
| classifier fix (locale-aware fr_signal) | 391 / 1 / 0 | 391 / 1 / 0 | 389 / 3 / 0 | 383 / 9 / 0 | 392 / 0 / 0 |
| inline 14 final hand-translations | **392 / 0 / 0** | **392 / 0 / 0** | **392 / 0 / 0** | **392 / 0 / 0** | **392 / 0 / 0** |

## Infrastructure shipped during JOB 7

- **`scripts/ingest_translations.py`** — reads `translations/<lang>.json` payloads and merges into `Json/<slug>.json` under `i18n.<lang>.*`. Idempotent. Supports nested dotted paths (`body.activities[2].title`).
- **`translations/{en,de,it,es,nl}.json`** — full translation payloads for the 160+ fiches translated through the campaign. Reusable for any future re-ingest.
- **Locale-aware `fr_signal()`** — `scripts/build_all_locales.py` classifier no longer false-positives Italian/Spanish bodies that preserve French proper nouns. Subtracts target-locale-distinctive markers (`" il "`, `" del "`, `" della "`, `" è "` for IT; `" el "`, `" los "`, `" que "`, `" es "`, `" para "` for ES; equivalent for DE/EN/NL) from the French signal before flagging.

## Known follow-up — secondary fields on 68 fiches (the hreflang smell)

The 68 fiches that had only `i18n.fr` at campaign start now have a translated `body.what_is`, `meta_title`, `meta_description`, `name`, `hero_alt` for each locale. **Other rendered fields still fall back to FR via `L_body()`**:

| field | fallback count (per locale) |
|---|---|
| `facts` | 68 |
| `body.activities[].title/description` | 68 |
| `body.practical_info[].k/v` | 68 |
| `faq[].q/a` | 68 |
| `hero.badge/lead` | 68 |
| `name_alternates[]` | 68 |
| `schema_amenities[]` | 45 |

Net effect: on those 68 pages × 5 locales = 340 rendered pages, the hero text + main body are in-language but the activity cards, practical-info rows, FAQ accordion, hero badge/lead are still French. The page emits `<html lang="en">` and the hreflang cluster claims it as English — defensible (the URL returns 200, the meta/title/body are EN) but not gold.

**To fully close**: a follow-up translation pass on those 68 fiches' secondary fields. ~7 short fields per fiche × 5 locales = ~2,400 micro-translations. Same `scripts/ingest_translations.py` ingest path handles them.

## Other open items surfaced during audit

- **NL chrome gap** — `nl/` contains only `index.html` for chrome; `cgv`, `merci-partenaire`, `merci-signalement`, `signaler-info`, `devenir-partenaire`, `mentions-legales`, `politique-confidentialite`, `studio`, `404` exist for the other locales but not for NL. Separate follow-up.
- **NL `name_alternates` gap** — 82 fiches have `name_alternates` falling back to FR in NL (vs 68 in en/de/it/es). Part of the same NL completeness work.
- **Inner zip in repo root** — `loisirs74-cascade-de-la-diomaz (1).zip` is on disk but already excluded from `_site/` via `*.zip` in DENY_GLOB. Cosmetic; remove from repo root when convenient.
- **Stray `?`-name artefacts** — `api/A` and `content/A` were 2-byte stray files copied into `_site/` because DENY_GLOB didn't catch them. **Removed in this commit**, and `"?"` (single-char filename) added to `DENY_GLOB` so future stray 1-char files never reach `_site/`.

## Gate evidence summary

Every `build_all` gate green at JOB 7 closure:

| gate | result |
|---|---|
| status | 392 published |
| hygiene | 0 Tier-1/2 |
| fiche render | 2,352 HTMLs (392 × 6 locales) |
| catalog index | rebuilt |
| hubs (13) | regenerated |
| placement | chez-nous-a-la-plage + chalet-du-tornet host counts preserved |
| card-diff | 12/12 byte-faithful |
| reachability | 0 orphans across all 6 locales |
| coverage report | 392 / 0 / 0 across en/de/it/es/nl |

Full pipeline runtime: ~10 s.
