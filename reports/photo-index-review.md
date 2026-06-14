# Phase 4 — photo-index review (Eddie gate)

**Date**: 2026-06-14
**Status**: built — awaiting Eddie keyword review before `pick_photo()` wires in

## What this is

`data/photo-index.json` maps each of the 77 `generique-*.jpg` photos in the library to:

- `keywords`: tokens derived from the filename + semantic associations (e.g. `piscine` → also `eau`, `aquatique`, `natation`)
- `type`: the dominant Phase 2b vocab value (one of `aquatique`/`patrimoine`/`nature`/`parc`/`sensations`/`divertissement`/`bien-etre`)

The picker in Phase 4 step 3 will score each fiche's description against these keyword sets and pick the highest-scoring unused photo. Get the keywords right here once → the picker is right forever.

## Per-type counts (Phase 4 diversity headroom)

| primary type | photos in library | hub demand (Phase 3 distribution / 6 locales) |
|---|---:|---:|
| aquatique      | 12 | 90 (lacs-plages + baignade-nautisme + cascades) |
| patrimoine     | 8 | 75 (chateaux + musees) |
| nature         | 19 | 96 (sentiers + points-de-vue + voies-vertes + telecabines + jardin) |
| parc           | 6 | 44 (parc + accrobranche + ferme) |
| sensations     | 6 | 48 |
| divertissement | 20 | 62 |
| bien-etre      | 5 | 3 |

## Review checklist

1. Open `data/photo-index.json`
2. For each photo, check: do the keywords describe what's visually in the photo?
3. Common things to verify:
   - `generique-aquatique-piscine-couverte.jpg`: keywords include `indoor` + `couverte` + `piscine` + `aquatique`. ✓ Vitam description has these → will match.
   - `generique-famille-foret.jpg`: keywords include `famille` + `foret` + `enfants` + `nature`. ✗ shouldn't match Vitam (no forest in description).
   - `generique-ferme-chevre.jpg`: keywords include `ferme` + `chevre` + `animal` + `pédagogique`. ✓ should match `ferme-pedagogique-petit-mont-bellevaux`.
4. To add/remove keywords or fix the primary type, edit `data/photo-index.json` directly. Re-running this script overwrites it from filename + semantic table.

## All photos (filename → keywords → type)

| filename | type | keywords |
|---|---|---|
| `generique-aquatique-bassin-natation.jpg` | `aquatique` | `aquaparc`, `aquatique`, `bassin`, `eau`, `natation`, `piscine` |
| `generique-aquatique-piscine-couverte.jpg` | `aquatique` | `aquaparc`, `aquatique`, `baignade`, `couvert`, `couverte`, `eau`, `indoor`, `intérieur`, `intérieure`, `nager`, `natation`, `piscine` |
| `generique-aquatique-piscine-exterieur.jpg` | `aquatique` | `aquaparc`, `aquatique`, `baignade`, `eau`, `exterieur`, `extérieur`, `extérieure`, `nager`, `natation`, `outdoor`, `piscine`, `plein-air` |
| `generique-aquatique-toboggan.jpg` | `aquatique` | `aquaparc`, `aquatique`, `eau`, `fun`, `glissade`, `jeux`, `piscine`, `toboggan` |
| `generique-atelier-poterie-mains.jpg` | `patrimoine` | `argile`, `artisanat`, `atelier`, `créatif`, `céramique`, `mains`, `poterie`, `stage`, `tour`, `workshop` |
| `generique-attraction.jpg` | `None` | `attraction`, `fallback`, `générique` |
| `generique-bar-jeux.jpg` | `divertissement` | `bar`, `divertissement`, `jeux`, `ludique`, `social` |
| `generique-barque-aviron.jpg` | `aquatique` | `aviron`, `barque`, `calme`, `eau`, `lac`, `rame`, `sport-eau` |
| `generique-bowling-lanes.jpg` | `divertissement` | `allées`, `bowling`, `jeux`, `lanes`, `quilles` |
| `generique-bowling-strike.jpg` | `divertissement` | `allées`, `bowling`, `jeux`, `quilles`, `strike` |
| `generique-canal-annecy-pont-amours.jpg` | `aquatique` | `amours`, `annecy`, `canal`, `eau`, `lac`, `pierre`, `pont`, `romantique`, `urbain`, `vieille-ville`, `vieux`, `ville` |
| `generique-cascade.jpg` | `aquatique` | `cascade`, `chute`, `eau`, `gorges`, `nature`, `ruisseau` |
| `generique-chateau-brume.jpg` | `patrimoine` | `brume`, `chateau`, `château`, `fog`, `historique`, `monument`, `mystique`, `médiéval`, `patrimoine`, `ruines`, `vestiges` |
| `generique-chateau-toiture.jpg` | `patrimoine` | `ancien`, `chateau`, `château`, `fortifié`, `historique`, `monument`, `médiéval`, `patrimoine`, `toiture` |
| `generique-chateau.jpg` | `patrimoine` | `chateau`, `château`, `historique`, `monument`, `médiéval`, `patrimoine` |
| `generique-cinema.jpg` | `divertissement` | `cinema`, `cinéma`, `film`, `projection`, `salle`, `écran` |
| `generique-croisiere.jpg` | `aquatique` | `bateau`, `croisiere`, `lac`, `navigation` |
| `generique-domaine.jpg` | `parc` | `domaine`, `paysage`, `étendue` |
| `generique-escalade-bloc-outdoor.jpg` | `sensations` | `bloc`, `bouldering`, `escalade`, `extérieur`, `grimpe`, `outdoor`, `plein-air`, `sport`, `vertige` |
| `generique-escalade-bouldering.jpg` | `sensations` | `bloc`, `bouldering`, `escalade`, `grimpe`, `indoor`, `sport`, `vertige` |
| `generique-escalade-outdoor-falaise.jpg` | `sensations` | `escalade`, `extérieur`, `falaise`, `grimpe`, `outdoor`, `plein-air`, `rocher`, `sport`, `vertige` |
| `generique-escalade-wall.jpg` | `sensations` | `escalade`, `grimpe`, `indoor`, `mur`, `salle`, `sport`, `vertige`, `wall` |
| `generique-escape-game-cadenas.jpg` | `divertissement` | `cadenas`, `enigme`, `escape`, `game`, `indoor`, `jeu`, `jeux`, `mystère`, `serrure`, `énigme` |
| `generique-escape-game-exit.jpg` | `divertissement` | `enigme`, `escape`, `exit`, `game`, `indoor`, `jeu`, `jeux`, `mystère`, `sortie`, `énigme`, `évasion` |
| `generique-escape-game-neon.jpg` | `divertissement` | `cyber`, `enigme`, `escape`, `futuriste`, `game`, `indoor`, `jeu`, `jeux`, `lumière`, `mystère`, `neon`, `énigme` |
| `generique-famille-balade.jpg` | `parc` | `balade`, `enfant`, `enfants`, `famille`, `kids`, `marche`, `petits`, `promenade` |
| `generique-famille-foret.jpg` | `parc` | `arbres`, `bois`, `enfant`, `enfants`, `famille`, `foret`, `forêt`, `kids`, `nature`, `petits`, `sapin` |
| `generique-ferme-chevre.jpg` | `parc` | `animal`, `animaux`, `chevre`, `chèvre`, `ferme`, `pédagogique`, `rural` |
| `generique-ferme-chevres.jpg` | `parc` | `animal`, `animaux`, `chevres`, `chèvres`, `ferme`, `pédagogique`, `rural` |
| `generique-karting-indoor-motion.jpg` | `divertissement` | `couvert`, `indoor`, `intérieur`, `kart`, `karting`, `motion`, `mouvement`, `piste`, `salle`, `sport`, `vitesse` |
| `generique-karting-indoor.jpg` | `divertissement` | `couvert`, `indoor`, `intérieur`, `kart`, `karting`, `piste`, `salle`, `sport`, `vitesse` |
| `generique-karting-outdoor-3kids.jpg` | `divertissement` | `3kids`, `enfants`, `extérieur`, `famille`, `kart`, `karting`, `kids`, `outdoor`, `piste`, `plein-air`, `sport`, `vitesse` |
| `generique-karting-outdoor-aerial.jpg` | `divertissement` | `aerial`, `aérienne`, `extérieur`, `kart`, `karting`, `outdoor`, `piste`, `plein-air`, `sport`, `vitesse`, `vue` |
| `generique-karting-outdoor-track.jpg` | `divertissement` | `extérieur`, `kart`, `karting`, `outdoor`, `piste`, `plein-air`, `sport`, `track`, `vitesse` |
| `generique-lac-coucher-soleil.jpg` | `aquatique` | `baignade`, `coucher`, `eau`, `lac`, `plage`, `rive`, `soleil` |
| `generique-lac.jpg` | `aquatique` | `baignade`, `eau`, `lac`, `plage`, `rive` |
| `generique-lancer-de-hache.jpg` | `divertissement` | `axe`, `de`, `défi`, `hache`, `jeux`, `lancer` |
| `generique-laser-game.jpg` | `divertissement` | `game`, `indoor`, `jeu`, `jeux`, `laser`, `lumière`, `équipe` |
| `generique-musee-classique.jpg` | `patrimoine` | `classique`, `collection`, `culture`, `ecomusee`, `exposition`, `musee`, `musée`, `patrimoine`, `traditionnel`, `écomusée` |
| `generique-musee-grande-galerie.jpg` | `patrimoine` | `collection`, `culture`, `exposition`, `galerie`, `grande`, `musee`, `musée`, `patrimoine`, `salle`, `vaste` |
| `generique-musee-moderne.jpg` | `patrimoine` | `art`, `collection`, `contemporain`, `culture`, `design`, `exposition`, `moderne`, `musee`, `musée`, `patrimoine` |
| `generique-musee.jpg` | `patrimoine` | `collection`, `culture`, `exposition`, `musee`, `musée`, `patrimoine` |
| `generique-paddle-aviron-detail.jpg` | `aquatique` | `aviron`, `barque`, `detail`, `eau`, `lac`, `paddle`, `rame`, `sport-eau`, `sup` |
| `generique-parapente-decollage.jpg` | `sensations` | `altitude`, `ciel`, `decollage`, `décollage`, `envol`, `libre`, `parapente`, `sensations`, `vol` |
| `generique-parapente-vol.jpg` | `sensations` | `altitude`, `ciel`, `libre`, `parapente`, `sensations`, `vol` |
| `generique-parc.jpg` | `parc` | `jardin`, `nature`, `parc`, `public`, `vert` |
| `generique-patinoire-hockey.jpg` | `divertissement` | `glace`, `hockey`, `patin`, `patinoire`, `sport` |
| `generique-patinoire-patins-blancs.jpg` | `divertissement` | `art`, `blancs`, `figure`, `glace`, `patin`, `patinoire`, `patins`, `sport` |
| `generique-patinoire-skater.jpg` | `divertissement` | `glace`, `patin`, `patinoire`, `skater`, `sport` |
| `generique-point-de-vue.jpg` | `nature` | `de`, `point`, `vue` |
| `generique-port-annecy.jpg` | `aquatique` | `annecy`, `bateaux`, `embarcadère`, `lac`, `port`, `vieille-ville`, `ville` |
| `generique-sentier-arete-alpine.jpg` | `nature` | `alpine`, `altitude`, `arete`, `arête`, `balade`, `chemin`, `crête`, `haute-savoie`, `marche`, `montagne`, `randonnée`, `sentier`, `sommet` |
| `generique-sentier-automne-orange.jpg` | `nature` | `automne`, `balade`, `chemin`, `feuillage`, `feuilles`, `marche`, `orange`, `randonnée`, `saison`, `sentier` |
| `generique-sentier-automne-rouge.jpg` | `nature` | `automne`, `balade`, `chemin`, `feuillage`, `feuilles`, `marche`, `randonnée`, `rouge`, `saison`, `sentier` |
| `generique-sentier-detail-pomme-pin.jpg` | `nature` | `balade`, `chemin`, `detail`, `marche`, `pin`, `pomme`, `randonnée`, `sentier` |
| `generique-sentier-fog.jpg` | `nature` | `balade`, `brouillard`, `brume`, `chemin`, `fog`, `marche`, `mystique`, `randonnée`, `sentier` |
| `generique-sentier-foret-alpine.jpg` | `nature` | `alpine`, `altitude`, `arbres`, `balade`, `bois`, `chemin`, `foret`, `forêt`, `haute-savoie`, `marche`, `montagne`, `nature`, `randonnée`, `sapin`, `sentier` |
| `generique-sentier-foret.jpg` | `nature` | `arbres`, `balade`, `bois`, `chemin`, `foret`, `forêt`, `marche`, `nature`, `randonnée`, `sapin`, `sentier` |
| `generique-sentier-hiver-neige.jpg` | `nature` | `balade`, `chemin`, `froid`, `hiver`, `marche`, `neige`, `randonnée`, `raquettes`, `saison`, `sentier` |
| `generique-sentier-melezes-automne.jpg` | `nature` | `arbres`, `automne`, `balade`, `chemin`, `feuillage`, `feuilles`, `marche`, `melezes`, `mélèzes`, `randonnée`, `saison`, `sentier` |
| `generique-sentier-sommet-panorama.jpg` | `nature` | `altitude`, `balade`, `chemin`, `marche`, `montagne`, `panorama`, `point-de-vue`, `randonnée`, `sentier`, `sommet`, `vue` |
| `generique-sentier.jpg` | `nature` | `balade`, `chemin`, `marche`, `randonnée`, `sentier` |
| `generique-spa-bien-etre.jpg` | `bien-etre` | `bien`, `bien-être`, `détente`, `etre`, `relax`, `spa`, `wellness` |
| `generique-spa-bols-tibetains.jpg` | `bien-etre` | `bien-être`, `bols`, `détente`, `méditation`, `relax`, `sonore`, `spa`, `tibetains`, `tibétains`, `wellness`, `zen` |
| `generique-spa-huile-essentielle.jpg` | `bien-etre` | `bien-être`, `détente`, `essentielle`, `huile`, `massage`, `parfum`, `relax`, `spa`, `wellness` |
| `generique-spa-jardin-tropical.jpg` | `bien-etre` | `bien-être`, `botanique`, `détente`, `exotique`, `fleurs`, `jardin`, `paradis`, `parc`, `relax`, `serre`, `spa`, `tropical`, `wellness` |
| `generique-telecabine.jpg` | `nature` | `altitude`, `cable`, `montagne`, `telecabine`, `télécabine`, `téléphérique` |
| `generique-thermes-hammam.jpg` | `bien-etre` | `bain`, `eau-chaude`, `hammam`, `thermal`, `thermes`, `vapeur` |
| `generique-trampoline-park-saut.jpg` | `divertissement` | `enfants`, `fun`, `indoor`, `park`, `saut`, `trampoline` |
| `generique-voie-verte-cyclistes-lac.jpg` | `nature` | `baignade`, `cyclisme`, `cyclistes`, `eau`, `lac`, `piste`, `plage`, `rive`, `route`, `verte`, `voie`, `vélo` |
| `generique-voie-verte-cyclistes-riviere.jpg` | `nature` | `cyclisme`, `cyclistes`, `piste`, `riviere`, `route`, `verte`, `voie`, `vélo` |
| `generique-voie-verte-famille-kids.jpg` | `nature` | `enfant`, `enfants`, `famille`, `kids`, `petits`, `piste`, `route`, `verte`, `voie`, `vélo` |
| `generique-voie-verte-foret.jpg` | `nature` | `arbres`, `bois`, `foret`, `forêt`, `nature`, `piste`, `route`, `sapin`, `verte`, `voie`, `vélo` |
| `generique-voie-verte-urbaine.jpg` | `nature` | `centre`, `piste`, `route`, `urbain`, `urbaine`, `verte`, `ville`, `voie`, `vélo` |
| `generique-voie-verte.jpg` | `nature` | `piste`, `route`, `verte`, `voie`, `vélo` |
| `generique-vr-immersion.jpg` | `divertissement` | `casque`, `expérience`, `futur`, `immersion`, `réalité`, `virtuelle`, `vr` |
| `generique-vr-multi-joueurs.jpg` | `divertissement` | `casque`, `collectif`, `futur`, `immersion`, `joueurs`, `multi`, `players`, `réalité`, `virtuelle`, `vr`, `équipe` |

## Gate (Phase 4 step 1)

- ✅ `data/photo-index.json` written
- ✅ Review checklist + per-photo keywords listed above
- ⏸ **Step 2 (wiring `pick_photo()` into build_all) does not start until Eddie has reviewed and corrected any keyword assignments here.**

Reply "go" once reviewed (or list specific photo fixes) and I will wire the picker.