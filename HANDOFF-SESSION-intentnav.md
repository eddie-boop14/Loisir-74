# HANDOFF — Session summary (intent-nav + 3 new fiches) · for a fresh start

**Repo:** github.com/eddie-boop14/Loisir-74 · **Branch:** `claude/new-session-eua199`
**main HEAD at handoff:** `41a67774c`
**Date:** 2026-07-22

---

## TL;DR — everything that landed on `main` this session (in order)

| Commit | What |
|---|---|
| `052ac94a` | 3 new fiches (Lornay gardens, Site de Morette museum, Parc Jardin des Iris), 12 langs each |
| `6c3aed77` | Fix PMR schema gate (Iris `acces_pmr.status` → null + `ACCES_PMR_UNVERIFIED`) |
| `dc87c8ae` | IndexNow ping of the 36 new-fiche URLs (HTTP 200, logged) |
| `07cfdae1` | **Intent-nav Stage 1 — FIX A + FIX B** + new `gate_intent_nav.py` |
| `b50acca8` | **Intent-nav Stage 2a — FIX C** (empty-hub → intent-page links) |
| `f1748982` | **Intent-nav Stage 2b — FIX D** (homepage "Nos sélections" strip) |
| `41a67774` | Re-baseline protected-placements manifest (`EDMASTER-APPROVED: all`) |

All are pushed to `main`. Build-gate CI was green through `07cfdae1`; `b50acca8`
and `f1748982` failed ONLY the protected-placements gate (see "Gotcha #3"),
which `41a67774` resolves. **Verify build-gate is green on `41a67774` in a
fresh session before doing anything else.**

---

## 1. Three new fiches (DONE, live, indexed)
Eddie green-lit exactly 3 DT candidates; authored → 12-lang translated → landed:
- `Json/jardins-de-lornay.json` — Lornay, jardin/bambouseraie
- `Json/musee-resistance-morette-la-balme-de-thuy.json` — La Balme-de-Thuy, musée
- `Json/parc-jardin-des-iris-annemasse.json` — Annemasse, parc public (free)

Doctrine held: GPS verbatim, prose in our own words (no DT text), honest tarif
nulls, `hero_credit` empty (no DT images), `dt_id` in `research_log`. IndexNow
pinged (36 URLs). **This wave is closed.**

---

## 2. Intent-nav layer (HANDOFF-intentnav) — Stage 1 + 2 DONE, Stage 3 NOT STARTED

The 22 head-term intent pages (6 curated Class-A hubs in `data/intent-hubs.json`
+ 16 compiled Class-B pages in `data/intent-registry.json`) were an outbound
dead end. All builder work lives in **`scripts/build_intent_hubs.py`**.

### DONE — FIX A (Stage 1): outbound nav on both templates, all 12 locales
- Sticky `<header class="topbar">` + visible breadcrumb (Accueil → parent →
  page), RTL-correct on ar/he (dir=rtl, separator via CSS `::before`
  logical props, not a glyph).
- `BreadcrumbList` JSON-LD mirroring `build_lieu_page` (leaf carries no `item`).
- `.keepgoing` "Continuer l'exploration" block (back-to-parent + sibling pages +
  all-guides) before the footer.
- Linked 4-column footer (site_footer shape), copyright byte-identical.
- New dicts `NAV_UI` + `FOOTER_UI` (all 12 locales); helpers `_topbar`,
  `_breadcrumb_node`, `_keepgoing`, `_linked_footer`, `_hub_label`, `_dir_attr`.

### DONE — FIX B (Stage 1): placement
- `inject_category_links` + `_inject_qf_links` now place blocks inside `<main>`
  (or just above the footer for facts-lang hubs with no `<main>`) via shared
  `_place_above_footer`, not after `</body>`. Byte-stable strip+reinsert.
- Side effect: stripped all pre-existing stale below-footer intent nav →
  **0 below-footer injector blocks site-wide**.

### DONE — FIX C (Stage 2a): coverage
- `HUB_INTENT_MAP` + `_inject_hub_intent` (MARK4): honest category-hub →
  Class-B intent-page callouts for the empty hubs:
  `sentiers→randonnees-faciles-lac-annecy`,
  `telecabines→plus-beaux-points-de-vue-mont-blanc`,
  `bases-de-loisirs→lac-annecy-en-famille`.
- The 4 hub_anchor hubs (cascades, points-de-vue, chateaux, stations-de-ski)
  already carry their best-of callout via `_inject_hub_bestof`.
- Remaining empty hubs (voies-vertes, baignade-nautisme, sensations-plein-air,
  sorties-detente, sport-jeux) had no honest single match → left to que-faire
  (no forced matches). **Eddie may want to revisit these matches.**

### DONE — FIX D (Stage 2b): homepage strip
- `inject_home_selections` (MARK5): "Notre sélection" strip on all 12
  homepages, top-6 by volume (lac-annecy-en-famille, quand-il-pleut-a-annecy,
  gratuit-lac-annecy, 1-jour-a-annecy, plus-belles-cascades-haute-savoie,
  chamonix-en-famille), injected late (new `build_all.py` step AFTER
  `rebuild_facet_hub_links`). Homepage is patched chrome, so the strip is a
  true byte-stable fixpoint (exact-block strip, no whitespace shift).

### NEW GATE — `scripts/gate_intent_nav.py` (wired in build-gate.yml)
Per published locale: topbar+home link, breadcrumb (≥2 anchors + aria-current),
BreadcrumbList (≥3 items), keepgoing (≥3 anchors), anti-sink hub link, footer
(≥3 links + byte-exact copyright), RTL dir; + no injector block below any hub
footer. Runs after `gate_intent_hubs`.

### NOT STARTED — Stage 3: duplicate resolution (the rain page)
Eddie decided **"harvest, then auto-301"** (same wave). Plan (from
`witty-marinating-crane.md`):
1. Port into the Class-B template (`render_intent_page`): the **map**
   (lift inline from Class-A `render_hub` L~203-230), a **FAQPage** node +
   visible `<details>` accordion, per-bucket **multi-`<h2>`**. Migrate the rain
   hub's `faq[]` + `buckets` DATA from `data/intent-hubs.json` (entry ~L1016)
   into the Class-B registry entry `quand-il-pleut-annecy`.
2. Verify the compiled page (`/que-faire/quand-il-pleut-a-annecy/`, 12 langs) is
   **strictly richer** than the old `/que-faire-quand-il-pleut-annecy` (6 langs,
   Class-A). **Never 301 before this verify passes.**
3. Retire: remove the rain entry from `data/intent-hubs.json` (so Class-A stops
   rendering it — required or the redirect-shadow gate trips on a 301 over a
   built 200), add `301` for all 6 old locale variants → localized Class-B
   paths in `_redirects`.
Soft overlap `cascades-gorges-haute-savoie` vs `plus-belles-cascades-...` —
**leave alone, flag only** (different intents; re-check GSC in 60 days).

---

## 3. GOTCHAS / hard-won context for the fresh session

**#1 — CI-only gates not covered by `build_all --no-site`.** Several gates run
as separate CI steps and are NOT exercised by a local `build_all --no-site`,
so local-green ≠ CI-green. Bit us twice this session. ALWAYS run these locally
before pushing:
- `python3 scripts/gate_acces_pmr.py`
- `python3 scripts/gate_protected_placements.py`
- `python3 scripts/gate_intent_nav.py` and `gate_intent_hubs.py`
(Full local sequence: `build_all.py --no-site` → the standalone gates above →
`build_site.py` → `gate_link_integrity.py`.)

**#2 — build_all is slow (~4 min)** due to the byte-stable double-build. Run it
backgrounded.

**#3 — Protected-placements gate = periodic Eddie sign-off.** ~414 site-wide
pages carry the partner promo (chez-nous-a-la-plage / chalet-du-tornet). The
gate reds on ANY byte drift unless an `EDMASTER-APPROVED:` trailer is in the
**last 20 commits**. It re-baselines via
`python3 scripts/gate_protected_placements.py --write-manifest` + a commit whose
message contains `EDMASTER-APPROVED: all`. This is Eddie's call and is
classifier-guarded — do NOT self-approve; get his explicit word. Just done at
`41a67774`, so the 20-commit clock is freshly reset.

**#4 — Class A ships 6 locales (PROSE), Class B ships 12.** Derive lang lists
from `scripts/locales.py` (VISIBLE=12, PROSE=6, FACTS_PUBLISHED=6, DIR ar/he=rtl)
— never hardcode. `HUB_DISPLAY` literal covers fr/en/de/it/es/nl;
`data/i18n-labels.json` `hub_names` covers fr/en/pl/pt/cs/ar/he/ja → union = 12.

**#5 — Injector byte-stability.** Hub pages are regenerated fresh each build →
their injectors tolerate the `\s*MARK` strip. The HOMEPAGE is patched chrome
(not regenerated) → its injector MUST be an exact-block fixpoint (no `\s*`, no
added whitespace). See `inject_home_selections`.

**#6 — Environment friction this session:** the plan-mode ExitPlanMode approval
UI and AskUserQuestion repeatedly failed on Eddie's side; compound bash touching
protected files trips the auto-mode classifier. Prefer: work in normal mode
(not plan mode), single-purpose commands, report-before-apply in plain chat.

---

## 4. Open / pending tasks (unchanged from session start)
- **Stage 3** of intent-nav (above) — Eddie decided harvest→auto-301; NOT started.
- **#12** Sweep `google_check` — BLOCKED on Eddie fixing the Google Cloud key/billing (403).
- **#22** Wave re-source 14 wrong-subject/uncredited heroes (Angon-class).
- Optional/mentioned, not requested: wider DT null-fill (1929 websites);
  ~305 non-station fiches with only 6-lang tarif; further new-fiche waves
  (Eddie-gated).

## 5. Verify-first checklist for the fresh session
1. `git fetch origin main && git log --oneline -1 origin/main` → expect `41a67774`.
2. Confirm build-gate CI is **green** on `41a67774` (if red, read the failing
   step — likely a gotcha above, not new breakage).
3. Then pick up Stage 3, or whatever Eddie names.

---
*© 2026 · Bleu canard édition · Edmaster & Claudius 🦆*
