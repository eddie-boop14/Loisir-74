# PROJECT-STATE — Loisirs74.fr

> Living snapshot of where the project stands. If this file and the repo disagree,
> trust the repo — but this is kept honest against `main`.
> **Last verified against HEAD `0297f49e` · 2026-07-22.**

For the *how it's built*, see `ARCHITECTURE.md`. This file is the *where we are* and
*what's next* — the thing a fresh session should read first.

---

## Snapshot (measured, not estimated)

| Metric | Value |
|---|---|
| Fiche JSONs (`Json/*.json`) | **434** |
| Visible locales | **12** (6 prose: fr de en es it nl · 6 facts: ar cs he ja pl pt) |
| Sitemap URLs | **5982** |
| Google Search Console — indexed | ~1,842 (of 5,790 discovered pre-fix; indexation lags, normal) |
| Bing IndexNow — submitted (cumulative) | ~8.3k *(running total of all pings ever, **not** distinct pages — true distinct ≈ 6k)* |
| Hero images: generique / hotlinked / uncredited / no-hero | 257 / 79 / 27 / 5 |

Deploy: push to `main` → CI **build gate** (43 steps) → Netlify. main is **green**.

---

## Recently landed on `main`

| Commit | What |
|---|---|
| `0297f49e` (PR #55) | **Sitemap fix** — folded the 192 Class-B intent pages (16 slugs × 12 locales) into `sitemap.xml` (5790 → 5982). They were built but invisible to the generator's depth-1 discovery. + **hero de-hotlink tooling** (see below). |
| `25eb57b4` (PR #54) | Unbreak main — `# isolation-ok:` tag on the home-selections `VISIBLE` loop (CI-only render-mode-isolation gate had gone red). |
| `41a67774` | Re-baseline protected-placements manifest (`EDMASTER-APPROVED: all`). |
| `f1748982` / `b50acca8` / `07cfdae1` | Intent-nav layer — homepage "Nos sélections" strip, empty-hub → intent-page links, outbound nav + breadcrumb + placement (Stage 1 + 2). |
| `052ac94a` … `dc87c8ae` | 3 new fiches (Lornay, Morette museum, Iris park) + IndexNow ping. |

---

## Open / pending

### Hero image integrity (HANDOFF-hero-integrity) — tooling merged, execution Eddie-gated
- ✅ **Merged:** `scripts/localize_heroes.py` (`--report`/`--apply`), `scripts/gate_hero_integrity.py`, `data/hero-shared-allow.json`.
- ⏳ **`--apply` awaits Eddie's go** (house law: report reviewed first). Needs Pillow (not in every session). Will self-host 60 of 79 hotlinked heroes (WebP + EXIF-strip) with Commons-authoritative credits; `--report`: 60/61 resolve, circuit breaker green at 2%.
- 🚦 **Gate NOT wired into `build-gate.yml`** — red by design (105 violations = pre-fix state) until `--apply` + worklist B land it green. Wire it only then.
- 👤 **Worklist B (Eddie only, code must not guess):**
  - 5 télécabines share one wrong-subject photo (Panoramic Mont-Blanc) → supply correct photos or route to generic.
  - `domaine-du-tornet` (protected + wrong-subject) → correct photo. Highest commercial value.
  - 3 accrobranche + Beunaz pair + mont-veyrier pair → confirm / replace / whitelist in `hero-shared-allow.json`.
  - 21 uncredited local photos → mine (`Photo : Ed Quackasnap #🦆`) / sourced (real credit) / unknown (replace with generic).
  - 5 no-hero fiches (artisan/food producers).
  - `criq-parc` (protected, uncredited) → Eddie decides.
  - `chateau-sires-faucigny-bonneville` — `*_*` credit, no resolvable source; supply attribution or replace.
  - `parc-animalier-grande-jeanne-annecy` — normalise `Photo originale Loisirs 74`; fiche is **protected**, so needs `EDMASTER-APPROVED`.
  - `tramway-du-mont-blanc` — Commons has no author (fails closed); find attribution or replace.

### Intent-nav — Stage 3 NOT started
- Rain-page duplicate: decided **"harvest, then auto-301"**. Port map + FAQPage + multi-`<h2>` into the Class-B template, verify the compiled page is strictly richer than the old Class-A `/que-faire-quand-il-pleut-annecy`, then 301 the 6 old locale variants. **Never 301 before the richer-than verify passes.**
- Soft overlap `cascades-gorges-haute-savoie` vs `plus-belles-cascades-…` — leave, re-check GSC in 60 days.

### Sitemap / indexing follow-ups
- `mentions-legales-loisirs74-phase1` (FR-only, self-canonical, linked site-wide) is the **1 remaining page absent from the sitemap** — the generator only folds multilingual groups. One-line follow-up if wanted.
- After deploy, optionally IndexNow-ping the 192 new intent URLs to skip the crawl wait.
- GSC coverage worth a look: **46 "Introuvable (404)"**, **163 "Explorée, actuellement non indexée"**.

### Longer-standing
- **#12** `google_check` sweep — BLOCKED on Google Cloud key/billing (403).
- **#22** re-source ~14 wrong-subject/uncredited heroes (Angon-class) — overlaps hero worklist B.
- Optional/unrequested: wider DT null-fill; ~305 non-station fiches with only 6-lang tarif; further new-fiche waves (Eddie-gated).

---

## Gotchas (hard-won — read before touching the build)

1. **CI-only gates ≠ `build_all --no-site`.** Several gates run as separate CI steps and are NOT exercised by a local `--no-site` build, so local-green ≠ CI-green. Bit us twice. Before pushing, also run locally: `gate_render_mode_isolation.py`, `gate_acces_pmr.py`, `gate_protected_placements.py`, `gate_intent_nav.py`, `gate_intent_hubs.py`, and (post-hero-apply) `gate_hero_integrity.py`.
2. **`build_all` is slow (~4 min)** — the byte-stable double-build. Run backgrounded.
3. **Protected-placements gate = periodic Eddie sign-off.** ~414 pages carry the partner promo (cheznousalaplage / chaletdutornet). The gate reds on ANY byte drift unless an `EDMASTER-APPROVED:` trailer is in the last 20 commits. Classifier-guarded — **never self-approve**. Re-baseline: `gate_protected_placements.py --write-manifest` + a commit whose message contains `EDMASTER-APPROVED: all`.
4. **Class A ships 6 locales (prose), Class B ships 12.** Derive lang lists from `scripts/locales.py` (VISIBLE=12, PROSE=6, FACTS=6, ar/he=rtl) — never hardcode.
5. **Injector byte-stability.** Hub pages regenerate fresh (injectors tolerate `\s*MARK` strip). The HOMEPAGE is patched chrome, not regenerated → its injector must be an exact-block fixpoint (no `\s*`).
6. **JSON is the spine.** Never hand-edit built HTML; fix the source JSON or the builder, then re-render. Markdown files (handoffs/state) are **not** pipeline inputs.
7. **Localized path segments.** Intent/hub URLs localize the path (`que-faire` → en `what-to-do`, de `was-unternehmen`, cs `co-delat`, pl `co-robic`, pt `o-que-fazer`, …). When globbing/counting pages, account for this — a `que-faire`-only search under-counts by design.

---

## Verify-first checklist for a fresh session
1. `git fetch origin main && git log --oneline -1 origin/main` → expect `0297f49e` (or later).
2. Confirm the latest build-gate run on `main` is **green** (if red, read the failing step — likely a gotcha above, not new breakage).
3. Then pick up: hero `--apply` (on Eddie's go), intent Stage 3, or whatever Eddie names.

---
*© 2026 · Bleu canard édition · Edmaster & Claudius 🦆*
