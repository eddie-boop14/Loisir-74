# STUDIO-ADJUSTMENTS — dev job list (for Claude Code)

**Repo:** github.com/eddie-boop14/Loisir-74 · **HEAD at audit:** `0ec8940`
**Context:** Studio is kept as a **JSON authoring** tool; its renderer is demoted (see ARCHITECTURE.md).
**Prime directive (Eddie):** *Studio output must never overwrite data it didn't touch.* A full-file
export based on a stale load-base silently écrase newer fields (monthly `freshness`, ingested
translations, future `place_id`). Fix that first; everything else is secondary.

---

## P0 — Non-destructive writes (the actual risk) 🔴

**Problem (confirmed):** `studio-editor.js` (L552–559) and `studio-enricher.js` (L430–464) export a
**full `<slug>.json`** deep-merged against the *loaded* copy. `studio-phototheque.js` (L368–374)
already exports a correct **partial patch**. Full-file artifacts replace the live file wholesale on
commit → any field added upstream since load is lost.

**1. Editor + Enricher emit a PATCH, not a full file.**
- Diff `editorState` vs `originalFiche`; serialize **only changed keys** (deep, per-i18n-locale).
- Output `{slug, <changed keys only>}` — mirror phototheque's shape.
- *Accept:* exporting a fiche you opened and changed nothing → **empty patch** (`{slug}` only).
- *Effort:* ~half day.

**2. Single ingress: `scripts/apply_studio_patch.py` (new).**
- Input: a Studio patch (`*-patch.json` / enricher / editor). Target: the **freshly-pulled live**
  `Json/<slug>.json`.
- **Deep-merge** patch → live (reuse `merge_secondary.py` / `ingest_translations.py` merge logic).
  Per-locale i18n merge; never drop a key absent from the patch.
- Append a `research_log` line `{by: "apply_studio_patch.py", date, fields:[...]}`.
- **No blind `cp` / file-replace anywhere.** This is the only way Studio output enters the repo.
- *Accept:* patch touching `i18n.fr.intro` leaves `freshness`, `i18n.nl`, `partners`, `place_id`
  byte-identical. *Effort:* ~half day.

**3. CI backstop in `build-gate.yml`: no-silent-drop gate.**
- Compare each `Json/*.json` against the previous commit; **fail** if any fiche lost a top-level
  key or an i18n locale (allow explicit deletions via a documented `--allow-drop` flag).
- Catches clobber regardless of source (Studio, manual, agent). *Effort:* ~half day.

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
