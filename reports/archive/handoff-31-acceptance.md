# HANDOFF-31 — One site, one standard: acceptance record

**Date**: 2026-07-02 · **Branch**: `claude/one-standard` (off `main` @ 0892e2a — matches the handoff attestation)

## What changed

The six facts-first languages (pl/pt/cs/ja/ar/he) no longer render through
`build_fulltree_lang`'s parallel mini-shell. One render path for 12 languages:

| Surface | Template now used | Notes |
|---|---|---|
| fiches (392/lang) | `build_lieu_page.build_page` | strict-prose mode: missing prose OMITTED, never FR; head description composed from reviewed vocabulary |
| hubs (15/lang) | `build_hubs.render_facts_hub_page` | FR canonical shell (same CSS/filters/footer/scripts) + the same card grid; hub-catcher/intro/FAQ prose omitted |
| communes (33/lang) | `build_communes.render_page` (parameterized) | same chrome lift + reciprocal backlinks as the six |
| homepage | `scripts/build_homepage_lang.py` | the EN locale homepage (the structural twin all five non-FR locales share), transformed per lang: STR weather dict, hero, sections, cards, footer |

`build_fulltree_lang.py` shrank from 485 to ~190 lines of pure orchestration —
its `shell()`, CSS strings and card/hub/commune/home mini-templates are deleted.
The misleading "pt: facts" label is gone: the summary line now reports
`N rich / M strict-facts`, both through the real template; `render_mode` in
`data/languages.json` still gates the prose-isolation contract and stays.

Chrome strings for the 6 langs come from reviewed sources only:
`data/i18n-labels.json`, `data/rich-chrome-langs.json`, and the NEW
`data/site-chrome-langs.json` (~115 strings/lang — homepage STR dict, hub
filter bar, commune chrome, category labels, near-me labels). The new file was
produced per the HANDOFF-22 lane (AI-translated UI microcopy, en/fr reference
embedded) — **flagged for Edmaster review**. No fiche prose was invented:
prose ships only via the batch pipeline.

## Side-by-side vs EN twins (char count, sections, features)

| Page | en | pt | he |
|---|---|---|---|
| homepage | 158,111 (100%) | 165,347 (105%) | 144,585 (91%) |
| hub (waterfalls/cascatas/cascades) | 72,365 (100%) | 68,733 (95%) | 65,271 (90%) |
| fiche (cascade-du-rouget) | 83,050 (100%) | 79,618 (96%) | 58,213 (70%)* |
| commune (annecy) | 111,710 (100%) | 113,380 (101%) | 104,416 (93%) |

Same section skeleton (homepage: hero + 11 cat sections; fiche: same block
list minus prose blocks), same `<style>` chrome byte-for-byte, weather STR
dict + Near-me + duck + filters + language picker + full footer present on
every page. \*he fiche = zero prose until its batch lands (strict rule) —
the gap is exactly the omitted prose sections, chrome is at parity.
Hub pages omit hub-catcher/hub-intro/hub-FAQ (~2.8K chars of SEO prose,
untranslated → omitted, never FR).

## RTL (Layer A, 20-page sample per lang)

- **ar: 20/20 PASS** · **he: 20/20 PASS** (`render_verify.py`, RV_SAMPLE=20)
- checks: `dir="rtl"` applied, no horizontal overflow, no U+FFFD tofu,
  frozen FR name + commune + price rendered and `<bdi>`-isolated.
- fixes shipped for the rich template under RTL: `<bdi>` on glance fact
  values, skip-link parked inline-start (was a 10,000px leftward scroll
  expansion), hammer-h1 word spans kept LTR (frozen FR names were
  rendering word-reversed).
- RTL homepage/hub/commune spot-check (ar+he × 3): `dir=rtl`, 0 overflow, 0 tofu.

## Gates

- full `build_all` green twice: reachability 0 orphans; placement gate OK;
  card-diff 12/12 byte-faithful; link integrity **5,366 pages / 220,572
  links / 0 broken** (facts trees grew the link graph from ~163K);
  render-mode isolation, i18n labels, duck-quacks, locale-status,
  canonical-selfref, no-key-drop, bot-commit-sanity, ingest --check all green;
  offline test suite green.
- one real 404 class found & fixed: stale EN homepage cards (fiche Json
  deleted) are now dropped from generated facts homepages.
- FR-prose leak found & fixed: free-text FR `duration` values
  ("5–10 min depuis parking (été)") no longer pass the vocabulary filter —
  this also cleans the already-shipped pt pages.

## Protected placements

- `git diff origin/main` on the 12 protected pages (2 fiches × 6 locales):
  **empty — byte-identical**.
- `cheznousalaplage.com` carriers in facts trees: **0** (protected fiches
  excluded from facts trees by design).
- `chaletdutornet.com` in facts trees: only as the official-site link of the
  *non-protected* Domaine du Tornet fiche — mirroring the six exactly.

## Netlify credit hygiene (same PR)

- `netlify.toml` ignore rule: pushes touching only `reports/`, `docs/` or
  `*.md` no longer trigger a production build (semantics verified against
  sample file lists; empty diff also skips).
- **Batching note**: 259 deploys burned 3,885 credits this cycle (77 left) —
  merging queued PRs in batches instead of one-by-one directly divides the
  deploy count.
- **FLAG — Edmaster decision, not auto-fixed**: disable or cap Netlify
  auto-recharge. Nobody spends Eddie's money silently; that rule covers
  Netlify too. Nothing was changed on the Netlify account.

## Out of scope / carried

- The committed six-locale HTML on main lags the builders (stale `?v=`
  hashes from PR #30's duck.js, pre-raw-emit escaped-tag pages). Every CI/
  Netlify build regenerates them; deliberately NOT bundled into this PR so
  the diff stays exactly HANDOFF-31.
- `claude/pl-prose-batch1` still needs manual deletion (git proxy blocker).
- Netlify "Redirect rules" check failure: pre-existing (failed identically
  on merged #28).
