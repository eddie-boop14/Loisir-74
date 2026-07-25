# Photo candidates — sourced but not yet placed

A parking place for freely-licensed photos that have been **found and vetted**
but have **no home on the site yet**. Without this file they exist only in chat
scrollback and get re-searched from scratch every time.

Nothing here is used by the build. This is a shortlist for a human, not a data
source — `Json/<slug>.json` `hero_image` remains the only thing that ships.

**Before using any row below**, re-check the file on Commons (licences and
filenames change), then:

```
# point the fiche at the Commons URL, then self-host + credit it:
python3 scripts/localize_heroes.py --report --only <slug>
python3 scripts/localize_heroes.py --apply  --only <slug>
```

`localize_heroes.py` resolves author + licence from the Commons API itself — do
not hand-copy the credit strings below into a fiche. They are here so a human
can judge fit, not to be pasted.

---

## Vetted, unplaced

| file (Commons) | subject | author · licence | size | why it is still here |
|---|---|---|---|---|
| `Col du Joly @ Les Contamines-Montjoie (51033192917).jpg` | Col du Joly, summer | Guilhem Vellut · CC BY 2.0 | — | Les Contamines station fiche already has a real hero |
| `Col du Joly panorama (hiver 2015).JPG` | Col du Joly, winter | Florian Pépellin · CC BY-SA 3.0 | — | same |
| `Col du Joly (Contamines-Hauteluce).JPG` | Col du Joly / Hauteluce | Florian Pépellin · CC BY-SA 3.0 | — | same |
| `Tête de la Cicle @ Les Contamines-Montjoie (51033091181).jpg` | Tête de la Cicle, lift station in frame | Guilhem Vellut · CC BY 2.0 | — | no fiche for this summit |
| `Flaine.JPG` | Flaine resort, winter | Soubok · CC BY 1.0 | 2048×1536 | Flaine station fiche already has a real hero |
| `La Chèvrerie … Roc d'Enfer.jpg` | Chèvrerie hamlet, Bellevaux | Percheman · **CC0** | — | no Bellevaux-village fiche; station fiche is covered |
| `Sur les pistes.jpg` | Portes du Soleil pistes toward Champéry | Larakrum · CC BY-SA 4.0 | — | generic massif view; shot from the **Swiss** side |
| `Croix d'Hiver et Tête de Geant … from Planachaux` | Portes du Soleil peaks | Paradise Chronicle · CC BY-SA 4.0 | — | same — Planachaux is Champéry (CH) |
| `Morzine summer.jpg` | Morzine + Pointe de Nyon | Endlessride · CC BY-SA 3.0 / GFDL | **640×480** | **too small for a hero** — see wanted list |
| `Chaine des Aravis - panoramio - Björn S..jpg` | Chaîne des Aravis | Björn S. · CC BY-SA 3.0 | 5184×3456 | `col-des-aravis` already has a real hero — it needs its **credit** researched, not a new photo |
| `Télésiège du Belvédère @ Sommet pointe de Merdassier.jpg` | Belvédère chairlift, Merdassier | Rémih · CC BY-SA 4.0 | 5184×3888 | no Merdassier fiche; nearest is `col-de-la-croix-fry` (Manigod) but that is a pass, not this lift |
| `Mont Lachat de Thônes @ Plateau de Beauregard (50882607646).jpg` | Mont Lachat / Plateau de Beauregard | Guilhem Vellut · CC BY 2.0 | 5472×3648 | no Beauregard fiche — the stale `plateau-de-beauregard` page was removed in JOB 4 |
| `La Clusaz Ski Center (FRA) 2020.jpg` | **Tête du Danay @ Espace Nordique des Confins** — the filename is misleading | Guilhem Vellut · CC BY 2.0 | 4240×2539 | `lac-des-confins` already has a credited hero by the same author |
| `Village @ La Clusaz (15184295068).jpg` | La Clusaz village | Guilhem Vellut · CC BY 2.0 | 2976×3968 | `la-clusaz` station fiche already has a credited hero |

## Rejected — do not use

| file | why |
|---|---|
| `La Flégère @ La Chavanne.jpg` | **Name trap.** This is *La Chavanne* at Chamonix-Mont-Blanc (Flégère), **not** *Les Chavannes* at Les Gets. Using it on `telecabine-des-chavannes-les-gets` would recreate the wrong-subject bug that PR #67 fixed. |
| `La Clusaz - Vue depuis la telecabine de la Patinoire - panoramio.jpg` | **Name trap.** A mountain *view from* the lift named after the ice rink — not the ice rink. On `patinoire-la-clusaz` it would show a panorama where a skating rink belongs. (Patrick Nouhailler · CC BY-SA 3.0 · 3456×2592, if a La Clusaz viewpoint fiche is ever created.) |

## Wanted — a real photo would land immediately

| slug | what is needed |
|---|---|
| `telecabine-pleney-morzine` | Le Pleney gondola, or Morzine from Le Pleney, ≥1200px. Currently on the house generic. |

---

## Where a photo can and cannot go

Checked 2026-07-25:

- **Ski station fiches** — all 28 already carry real self-hosted heroes. No gap.
- **Commune hubs** (`chatel/`, `morzine/`, `bellevaux/` …) — no hero slot at all;
  they are card grids fed by member fiches. Would need a feature first.
- **Category hubs** (`telecabines/`, `points-de-vue/`, `stations-de-ski/` …) —
  they *do* have a `--hero-img` CSS slot and it is **empty on every one**. A real
  unused surface, but filling it is a design decision, not a photo swap.
- **Intent pages** — no page-level hero; imagery comes from member fiche cards.
  So fixing a fiche hero improves every intent page and hub that lists it, in all
  12 locales. That is the leverage: fix the fiche, not the page.

## Fiche hero worklist (the real backlog)

434 fiches, of which **only 76 carry a real, credited, self-hosted photo**:

| state | count | meaning |
|---|---|---|
| generic placeholder | 258 | `/img/generique/…` — honest, but not the place |
| hotlinked | 74 | served live from `upload.wikimedia.org`; run `localize_heroes.py --only` |
| real but no credit | 21 | self-hosted with an empty `hero_credit` — a CC-BY breach if the source required it |
| missing entirely | 5 | no `hero_image` at all |
| **needing work** | **358** | |

Heaviest generic categories: `attraction` (85), `sentier` (37), `musee` (30),
`plage` (15), `parc` (12).

These are what keeps `gate_hero_integrity` red (99 violations). The 74 hotlinks
are the cheapest win — they already have a photo, it just is not self-hosted or
credited, and `--only` now allows doing them in small reviewable batches.
