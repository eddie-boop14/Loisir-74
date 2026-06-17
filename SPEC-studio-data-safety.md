# SPEC — Studio data-safety (non-destructive writes)

| | |
|---|---|
| **Status** | SHIPPED (P0) |
| **Type** | Engineering spec / RFC (expands `STUDIO-ADJUSTMENTS.md` P0) |
| **Repo / HEAD** | github.com/eddie-boop14/Loisir-74 · `aebd297` |
| **Owner** | Edmaster · **Builder** Claude Code · **Spec** Claudius |
| **Related** | `ARCHITECTURE.md`, `STUDIO-ADJUSTMENTS.md` |
| **Blast radius** | All 392 `Json/*.json` — the source of truth |

---

## 0. TL;DR
Studio's editor + enricher export a **whole fiche** built on a load-time snapshot. Drop that over
`main` and any field a monthly sweep / translation ingest wrote *after* load is silently écrasé.
Fix: Studio emits **dotted-path patches** (changed keys only); a single Python ingress
**deep-merges** them into the **freshly-pulled live** JSON; a CI gate **fails the build if any fiche
loses a key**. After this, Studio is *structurally incapable* of clobbering data it didn't touch.

## 1. Problem (confirmed, with evidence)
| Surface | File:line | Behaviour | Verdict |
|---|---|---|---|
| Phototheque | `studio-phototheque.js:368–374` | emits partial patch `{slug, hero_image, hero_credit}` | ✅ safe — the model |
| Editor | `studio-editor.js:552–559` | emits **full `<slug>.json`** via `deepMerge(originalFiche, editorState)` | 🔴 clobbers |
| Enricher | `studio-enricher.js:435,461–464` | emits **full `json/<slug>.json`** from `original` clone | 🔴 clobbers |

`deepMerge` preserves keys **only relative to the load base**. If live moved on (sweep writes
`freshness`, ingest writes `i18n.*`), a full-file drop reverts them. The merge is correct; the
**full-file artifact** is the defect.

**Already-safe ingress to mirror:** `ingest_translations.py` (`set_path` + `merge_payload`,
dotted-path, no-op detection) and `merge_secondary.py` (`merge_into_locale_block`) already merge
*into* the live file. Studio just doesn't use that door.

## 2. Goals / Non-goals
**Goals** — (G1) Studio writes never drop an untouched key. (G2) Single auditable ingress.
(G3) CI proves no silent key loss, repo-wide, every push. (G4) Reuse existing merge code.
**Non-goals** — renderer parity / `studio-render.js` bugs (dead organ); `content/*.md` + `llms-full.txt`
regen (separate job); schema redesign; locale/field deletions (explicit, rare — §4.1).

## 3. Design — the invariant
```
Studio tab ──emits──▶ <slug>.studio-patch.json   (dotted-path, changed keys ONLY)
                              │
                              ▼
   git pull --ff-only main   (FRESH live JSON = merge target)
                              │
        scripts/apply_studio_patch.py  ──set_path──▶ Json/<slug>.json   (in place)
                              │  stamps research_log{by,date,fields}
                              ▼
        build-gate.yml ▶ gate_no_key_drop.py   (FAIL if any key/locale lost vs HEAD~1)
```
**Invariant:** the only bytes a patch can change are the paths it explicitly lists. Everything else
is byte-identical by construction (merge) and proven by CI (gate).

## 4. Contracts

### 4.1 Patch format (dotted-path — matches `ingest_translations.set_path`)
```json
{
  "slug": "musee-chateau-annecy",
  "source": "studio-editor",            // editor | enricher | phototheque
  "base_head": "aebd297",               // HEAD the patch was authored against (or null)
  "patch": {
    "i18n.fr.intro": "Nouveau texte…",
    "hero_image": "/musee-chateau-annecy-hero.jpg",
    "hero_credit": "Coyau · CC BY-SA 3.0 · Wikimedia Commons"
  },
  "delete": []                          // explicit paths to remove; default [] (no deletions)
}
```
- **Values replace wholesale at their path.** Arrays replace whole (no element merge — matches
  editor `deepMerge` array rule). Objects are *not* expressed as objects; descend via dotted paths.
- **`slug` must match an existing `Json/<slug>.json`** (no create-via-patch in v1).
- **Guard:** reject a "patch" that carries a full i18n tree for ≥2 locales or >40 paths → that's a
  disguised full-file dump; fail with a clear message.
- **`base_head`** is `null` when emitted from the browser (Studio can't read git HEAD). The conflict
  tripwire (§4.2) is skipped when it's null; the key-drop gate (§4.4) remains the backstop.

### 4.2 Merge semantics
- Reuse `ingest_translations.set_path(blk, path, value)` to write; reuse its no-op detection.
- **Granularity = path.** Last-write-wins at the leaf only; sibling keys untouched.
- **Conflict surfacing:** if `base_head` ≠ current HEAD, before writing each path, compare the live
  value to the value at `base_head` (`git show base_head:Json/<slug>.json`). If live changed that
  exact path since `base_head`, **print a CONFLICT line** (path, base→live→incoming) and require
  `--allow-conflict` to overwrite. Default: abort on conflict. (This is the human tripwire.)

### 4.3 `scripts/apply_studio_patch.py` (new)
```
usage: apply_studio_patch.py PATCH.json [--dry-run] [--allow-conflict]
```
1. Load + validate patch (§4.1 guard). Malformed → exit 2.
2. Resolve `Json/<slug>.json`; missing → exit 3.
3. For each `patch` path: no-op check → conflict check (§4.2) → `set_path`. Count changed/skipped.
4. Apply `delete[]` (if any) via path-pop; missing path = warn, not fail.
5. Append `research_log` entry `{by:"apply_studio_patch.py", date:<ISO>, fields:[...changed]}`.
6. `--dry-run` prints the diff and writes nothing. Else write `indent=2`, trailing `\n`.
7. Exit 0; print `changed=N skipped=M conflicts=K`. (Conflict abort → exit 4.)

### 4.4 `scripts/gate_no_key_drop.py` (new) → wired into `build-gate.yml`
- For each `Json/*.json`: load current + `git show HEAD~1:Json/<slug>.json` (new file → skip).
- Compute leaf-key sets (top-level keys, `i18n` locale set, each `i18n.<lang>` key set).
- **FAIL** if any key/locale present in HEAD~1 is absent now, unless id ∈ `reports/key-drop-allowlist.txt`.
- New files / intentional deletes handled via allowlist or a documented `--allow-drop`.
- Slots into `build-gate.yml` as a step after checkout (needs `fetch-depth: 2`); read-only, fast.

## 5. Work breakdown
| ID | Task | Files | Status |
|----|------|-------|--------|
| **P0-1** | Editor → patch export | `studio-editor.js` | ✅ done |
| **P0-2** | Enricher → patch export | `studio-enricher.js` | ✅ done |
| **P0-3** | `apply_studio_patch.py` | new | ✅ done |
| **P0-4** | `gate_no_key_drop.py` + wire CI | new + `.github/workflows/build-gate.yml` | ✅ done |
| — | Phototheque aligned to canonical format | `studio-phototheque.js` | ✅ done (single ingress) |
| P1-5 | Regen `studio-consts.js` (6 langs incl nl) | `scripts/build_site.py` → `studio-consts.js` | later |
| P1-6 | Editor/enricher load from **live** catalog | `studio-editor.js`, `studio-enricher.js` | later |
| P2-7 | Build tab = "Aperçu ≠ production" banner | `studio.html` | later |

## 6. Test plan — implemented in `tests/test_apply_studio_patch.py`
- **Unit:** `set_path` roundtrip; no-op skip; array whole-replace; `delete[]` pop; full-file guard
  rejects (>40 paths; ≥2 whole locales); missing-slug → exit 3; dry-run writes nothing.
- **Golden idempotency:** apply the same patch twice → 2nd run `changed=0`.
- **🔒 Clobber regression (the proof):** seed fiche with `freshness.last_checked` → apply an editor
  patch touching only `i18n.fr.intro` → assert `freshness`, `i18n.de`, `partners`, `hero_credit`
  byte-identical. This test *is* the answer to "datas écrasé older shit."
- **Conflict path:** verified against real git history (older `base_head` → exit 4; `--allow-conflict`
  applies).
- **Gate:** removing a key from a fiche → `gate_no_key_drop.py` exits 1; restore → green.

## 7. Rollback & safety
Every item is additive (new scripts; export behind the new code path; gate is read-only). Rollback =
`git revert` the commit; **no data migration, no JSON rewrite**. `--dry-run` is available for
`apply_studio_patch.py` during rollout. The gate supports `--allow-drop` (warn-only) if a first push
ever needs it.

## 8. Sequencing
`P0-3 ∥ P0-4` (independent) → `P0-1, P0-2` (consume the patch format) → ship P0 as one PR (gate = its
acceptance test). Then `P1-5 → P1-6 → P2-7` in a later PR. P0 is mergeable and valuable alone.

## 9. Definition of Done (P0)
- [x] Editor + enricher emit dotted-path patches; unchanged fiche → empty patch.
- [x] `apply_studio_patch.py` is the sole ingress; conflict + dry-run behave per §4.
- [x] Clobber-regression test passes.
- [x] `gate_no_key_drop.py` green in `build-gate.yml`; a deliberate drop goes red.
- [x] `STUDIO-ADJUSTMENTS.md` P0 checkboxes ticked; this spec linked from it.

## 10. Out of scope (pointers)
`studio-render.js` bugs (retired renderer) · `content/*.md` + `llms-full.txt` regen (own job, 87→392) ·
geo-verify ✅ (own spec; reuses `check`/`sweep` `place_id`).

---
*2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés* 🦆
