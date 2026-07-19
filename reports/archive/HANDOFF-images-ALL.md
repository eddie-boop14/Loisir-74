# HANDOFF → Claude Code · Image generics, ALL batches (1–6)
**Repo:** `Loisir-74-main` · source of truth `Json/*.json` · prepared by Claudius for Edmaster

60 new generic photos, 49 pre-selections. Two data files do the work:
- `rename-manifest-ALL.json` — list of `[uploaded_file, new_name, subject]` (60 rows)
- `preselections-ALL.json` — `{ slug: "generique-*.jpg" }` (49 entries)

---

## JOB 1 — Add the 60 new generic photos
For each row in `rename-manifest-ALL.json`: rename the uploaded `1000060XXX.jpg` to the
given `generique-*.jpg` and drop it in the **repo root** (alongside the other `generique-*.jpg`).
Mapping was verified by viewing every file — display order was NOT trusted.

**One conversion:** `1000060318.png` → `generique-ski-piste.jpg` — re-encode PNG to JPG
(quality ~85), don't just rename the extension.

New generics by theme (batch 2–6, on top of batch 1's 19):
paintball ×4, padel ×3, tennis ×3, kids/aire-de-jeux ×5, lancer-hache ×1, cible ×2,
jardin/parc ×6, ski ×3, snowboard ×2, neige/forêt ×4, télésiège ×1, bateaux/voile ×3,
wakeboard ×1, montgolfière ×1, parachutisme ×1, plaine ×1.

---

## JOB 2 — Apply the 49 pre-selections
For each entry in `preselections-ALL.json`, set `hero_image = "/<value>"` in
`Json/<slug>.json` (leading slash — renderer wants an absolute path). Idempotent: only
that field changes.

Coverage: via-ferrata ×8, rafting ×3, spéléo ×2, tir-à-l'arc ×2, tyrolienne ×1, segway ×1,
mine/grotte ×1 (batch 1) + paintball ×3, padel ×3, lancer-hache ×1, montgolfière ×2,
wake ×2, croisière/voile/port ×6, jardins ×7, kids ×7 (batch 2–6).

> If Edmaster sends an exported `image-assignments.json` from the picker, **it supersedes**
> this file — apply that instead (same format, his confirmed + adjusted set).

---

## PALETTE-ONLY (not auto-assigned — Edmaster places these in the picker)
No clean slug match, or assigning blindly would risk a wrong-season/wrong-place hero:
- **ski ×3, snowboard ×2, télésiège ×1, neige/forêt ×4** — no alpine-ski lieux match by slug;
  a snow photo on a summer venue is the error to avoid. Available in the palette.
- **cible ×2** (industrial wall, AIM matchbox) — fallback for tir/archery, not primary heroes.
- **parachutisme ×1** (`generique-parachutisme.jpg`, file 304) — this is a **parachute**, NOT a
  montgolfière. Only use on a parachutisme lieu; do not let it land on a balloon page.
- **plaine ×1** (`generique-plaine-verte.jpg`, file 313) — generic green field, **not alpine**;
  low priority.

## DROPPED (do not add)
- `1000060301.jpg` (basketball) — visible **Unsplash+ watermark**, unusable.
- `1000060346.jpg` (Spider-Man / Captain America) — copyrighted Marvel characters.

---

## FLAGS (confirm with Edmaster — do not auto-fix)
- **`escalade-la-crique-annecy`** still on `generique-parc.jpg` (park photo on a climbing wall).
  Excluded from the kids match. Right fix = an **escalade** generic already in the repo
  (`generique-escalade-bloc-outdoor.jpg` / `-wall.jpg` / `-outdoor-falaise.jpg` / `-bouldering.jpg`).
- **`jardin-des-cinq-sens`, `jardins-europe-annecy`** — NOT pre-assigned: already carry real
  (credited) photos. Left alone.
- **101 fiches** with real Wikimedia/CC photos are hidden in the picker; a few have
  cross-wired credits (e.g. `cascade-d-angon` credits "Cascade du Rouget") — separate
  data-quality pass, not part of this job.

---

## RE-RENDER
```
python3 scripts/build_all_locales.py
python3 scripts/build_hubs.py
python3 scripts/build_catalog_index.py
python3 scripts/build_site.py
```
Acceptance: the 49 pre-selected fiches show their new hero across all 6 languages; the 60
new files are present in `_site/`; no fiche references a `generique-*.jpg` that isn't on disk.
