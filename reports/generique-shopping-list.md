# Générique hero-image shopping list

After running `scripts/pick_generique.py`, the catalog now uses 50 distinct
hero variants across all rendered HTML (up from ~9). The hot spot is
**46 fiches still falling back to `generique-attraction.jpg`** — these are
covered by activity types that have no dedicated variant on disk yet.

Source CC0 / public-domain / royalty-free pictures (unsplash.com,
pexels.com, pixabay.com, wikimedia commons CC0) and drop them in
`/home/user/Loisir-74/incoming-generics/` using the filename pattern:

```
{bucket}__cc0_{source-slug}.jpg
```

Examples: `padel__cc0_pexels-12345.jpg`, `plage__cc0_unsplash-john-doe.jpg`.

A follow-up session will resize → optimize → rename → wire up.

## File spec (every drop)

- **Format**: JPEG, sRGB
- **Dimensions**: 1600×1200 (4:3 landscape — matches existing markup)
- **Weight**: 75–300 KB (target ~150 KB at quality 78)
- **License**: CC0 / public domain / royalty-free with no attribution requirement

## Shopping list (by priority × fiche count)

| Suggested filename | Fiches | Subject (what to picture) | Priority |
|---|---:|---|---|
| `generique-plage.jpg` | 15 | Pebble or sand lake beach with mountain backdrop (Lac d'Annecy / Léman aesthetic; no identifiable people) | **High** |
| `generique-via-ferrata.jpg` | 10 | Climber clipped to iron-rung route over alpine cliff | **High** |
| `generique-accrobranche.jpg` | 7 | Tyrolean / zipline through forest canopy, helmeted figure mid-route | **High** |
| `generique-casino.jpg` | 5 | Roulette wheel, slot machines, or chip stacks (no logos / branded venues) | **High** |
| `generique-chiens-traineau.jpg` | 5 | Dog-sled team on snow trail, frontal or 3/4 view | **High** |
| `generique-paintball.jpg` | 3 | Mid-game action shot with marker visible, blurred background | Medium |
| `generique-canyoning.jpg` | 3 | Wetsuit canyon descent or natural waterslide | Medium |
| `generique-rafting.jpg` | 3 | Whitewater raft with paddlers, helmets visible | Medium |
| `generique-tir-a-l-arc.jpg` | 2 | Archer at full draw, target backdrop | Medium |
| `generique-aerostation.jpg` | 2 | Hot-air balloon inflating at dawn or in flight | Medium |
| `generique-ferme-pedagogique.jpg` | 2 | Goats / sheep / horses with hands feeding (no children's faces) | Medium |
| `generique-jardin.jpg` | 4 | Formal botanical garden with paths and parterres | Medium |
| `generique-wakepark.jpg` | 2 | Wakeboarder mid-jump on cable park | Medium |
| `generique-padel.jpg` | 1 | Padel court (glass walls), top-down or wide angle | Low |
| `generique-arcade.jpg` | 2 | Retro arcade cabinets / flippers, neon-lit | Low |
| `generique-saut-elastique.jpg` | 1 | Bungee silhouette mid-jump | Low |
| `generique-bungy-swing.jpg` | 1 | Pendulum swing over canyon | Low |
| `generique-speleologie.jpg` | 1 | Caver with headlamp in chamber | Low |
| `generique-luge-rails.jpg` | 1 | Alpine coaster / mountain luge track | Low |
| `generique-disc-golf.jpg` | 1 | Disc mid-flight to basket | Low |
| `generique-golf.jpg` | 1 | Putting green or driving range | Low |
| `generique-billard.jpg` | 1 | Pool / snooker table, cue stick angle | Low |
| `generique-baignade-bio.jpg` | 1 | Natural plant-filtered bio-pool | Low |

**Total**: ~25 new pictures to fully eliminate the `attraction`-catchall.
Each drop reduces the catchall by N fiches.

## Current variants on disk (already wired up — no action needed)

75 `generique-*.jpg` files at repo root, including:
- **sentier** (10): foret, foret-alpine, fog, arete-alpine, hiver-neige, automne-rouge, automne-orange, sommet-panorama, melezes-automne, detail-pomme-pin
- **voie-verte** (6): foret, famille-kids, cyclistes-lac, cyclistes-riviere, urbaine, base
- **musee** (4): base, classique, grande-galerie, moderne
- **chateau** (3): base, brume, toiture
- **escalade** (4): outdoor-falaise, bloc-outdoor, bouldering, wall
- **karting** (5): outdoor-track, indoor, outdoor-3kids, indoor-motion, outdoor-aerial
- **aquatique** (4): bassin-natation, piscine-couverte, piscine-exterieur, toboggan
- **patinoire** (3): hockey, patins-blancs, skater
- **spa** (4): bien-etre, bols-tibetains, huile-essentielle, jardin-tropical
- **bowling** (2): lanes, strike
- **parapente** (2): decollage, vol
- **escape-game** (3): neon, exit, cadenas
- **VR** (2): immersion, multi-joueurs
- singletons (~13): cascade, lac, lac-coucher-soleil, port-annecy, paddle-aviron-detail, barque-aviron, croisiere, thermes-hammam, lancer-de-hache, laser-game, trampoline-park-saut, bar-jeux, atelier-poterie-mains, cinema, famille-balade, famille-foret, canal-annecy-pont-amours, point-de-vue, telecabine, parc, domaine, attraction

## Verification (current state)

```bash
python3 scripts/pick_generique.py        # idempotent re-run, prints diversity
python3 scripts/build_all.py --no-site   # all 8 gates green
grep -ho 'data-generique-cat="[^"]*"' *.html | sort | uniq -c | sort -rn
```

Expected: 50 distinct values in rendered HTML, top bucket
(`attraction`) at 46 fiches. After every drop wave the attraction count
drops by the bucket size; after full drop ≈ 0.
