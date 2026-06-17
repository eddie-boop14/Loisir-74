# STUDIO-ADJUSTMENTS — dev job list (for Claude Code)

**Repo:** github.com/eddie-boop14/Loisir-74 · **HEAD at audit:** `0ec8940`
**Context:** Studio is kept as a **JSON authoring** tool; its renderer is demoted (see ARCHITECTURE.md).
**Prime directive (Eddie):** *Studio output must never overwrite data it didn't touch.* A full-file
export based on a stale load-base silently écrase newer fields (monthly `freshness`, ingested
translations, future `place_id`). Fix that first; everything else is secondary.

---

## P0 — Non-destructive writes (the actual risk) ✅ SHIPPED

> Full engineering spec + contracts: [`SPEC-studio-data-safety.md`](SPEC-studio-data-safety.md).
> All three Studio tabs now emit dotted-path patches consumed by one Python ingress, with a CI
> gate proving no fiche ever silently loses a key.

**Problem (confirmed):** `studio-editor.js` (L552–559) and `studio-enricher.js` (L430–464) exported a
**full `<slug>.json`** deep-merged against the *loaded* copy. `studio-phototheque.js` (L368–374)
already exported a partial patch. Full-file artifacts replaced the live file wholesale on commit →
any field added upstream since load was lost.

**1. Editor + Enricher emit a PATCH, not a full file.** ✅
- Editor `saveJSON` now diffs `editorState` vs `originalFiche` (`diffToPatch`/`walkDiff`) → dotted
  paths, arrays whole-replace, removed keys → `delete[]`. Enricher emits its accepted per-path
  `changes` directly. Both output `{slug, source, base_head, patch, delete}`.
- *Accept met:* exporting an unchanged fiche → empty patch (alert: "rien à exporter").

**2. Single ingress: `scripts/apply_studio_patch.py` (new).** ✅
- Reuses `ingest_translations.set_path`; no-op detection; full-file-dump guard (>40 paths / ≥2 whole
  locales rejected); optional conflict tripwire vs `base_head`; `--dry-run`. Stamps `research_log`.
- *Accept met:* patch touching `i18n.fr.intro` leaves `freshness`, `i18n.de`, `partners`,
  `hero_credit` byte-identical (clobber-regression test in `tests/test_apply_studio_patch.py`).

**3. CI backstop in `build-gate.yml`: no-silent-drop gate.** ✅
- `scripts/gate_no_key_drop.py` compares every `Json/*.json` against a baseline; fails on any
  dropped top-level key, locale, or per-locale key. Intentional removals →
  `reports/key-drop-allowlist.txt` or `--allow-drop`.
- *Verified:* green on the live tree; a deliberate key removal exits 1.

> **Ingress-only rule.** Studio output enters the repo **only** as a dotted-path patch via
> `scripts/apply_studio_patch.py`; never write a full `<slug>.json` into `Json/` directly. The
> gate catches dropped *keys*, not reverted *values* — the ingress is the wall, the gate is the
> backstop. (Full statement in `ARCHITECTURE.md` / `SPEC-studio-data-safety.md`.)

---

## P1 — Kill the stale base that makes clobber likely 🟠

**4. Regenerate `studio-consts.js` from `build_site.py`** to current truth: **6 langs incl. `nl`**,
current categories/heroes. Stale consts (5 langs today) = stale previews and edits made on a wrong base.
*Accept:* `STUDIO_CONSTS.LANGS` = `[fr,en,de,it,es,nl]`. *Effort:* ~1h (confirm the generator emits nl).

**5. Editor/Enricher load from LIVE, not a bundle.** Phototheque already fetches `/catalog-index.json`
at mount — good. Ensure editor + enricher fetch the **current** `Json/<slug>.json` (or catalog) at edit
time, so the merge base is fresh. *Accept:* opening a fiche shows the same data as live `main`.

---

## P2 — Renderer demotion (C) 🟡

**6. Mark Studio Build/preview as PREVIEW-ONLY.** Banner in the Build tab:
*"Aperçu ≠ production. Rendu final = pipeline Python (build_all.py)."* Stop shipping Studio HTML.
*Effort:* ~30 min.

### DO NOT
- ❌ Do **not** fix `studio-render.js` hero_credit / image-path bugs. It's the dead organ
  (port of the deleted `render-v3.py`); the Python pipeline is the renderer. Don't polish what we're retiring.
- ❌ Do **not** let any Studio export overwrite a live `Json/<slug>.json` directly.

---

## Related pipeline tasks (NOT Studio — logged so they're not lost)
- **`llms.txt` is stale:** says *5 langs / 393*. Fix the generator in `build_site.py` → **6 langs incl. nl**,
  count 392. (Contradicts the sitemap, which already emits nl.)
- ~~Verify `build_lieu_page.py` renders `hero_credit`~~ — **DONE.** `.hero-credit` renders at
  `build_lieu_page.py:1144`. Musée CC photos are safe to render once credits are filled.

---

## Suggested order
P0-1 → P0-2 → P0-3 (data safety closed) → P1-4 → P1-5 → P2-6 → related tasks.
After P0, Studio is safe to use even with a stale base — it can only ever *add/replace the keys you edited*.

---
*2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés* 🦆
