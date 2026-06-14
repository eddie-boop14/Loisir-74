# Generic hero remapping audit (corrected)

**Date**: 2026-06-14
**Scope**: 392 published fiches
**Status**: REPORT — no JSON or HTML mutated yet

## Summary

- On real hero (URL or `/<slug>-hero.jpg`): **116**
- On `/generique-*.jpg`:                    **276**
- **Proposed remappings: 169** (out of 276 on-generic)

## Available generic photo bank (75 photos)

- `generique-aquatique-bassin-natation.jpg`
- `generique-aquatique-piscine-couverte.jpg`
- `generique-aquatique-piscine-exterieur.jpg`
- `generique-aquatique-toboggan.jpg`
- `generique-atelier-poterie-mains.jpg`
- `generique-attraction.jpg`
- `generique-bar-jeux.jpg`
- `generique-barque-aviron.jpg`
- `generique-bowling-lanes.jpg`
- `generique-bowling-strike.jpg`
- `generique-canal-annecy-pont-amours.jpg`
- `generique-cascade.jpg`
- `generique-chateau-brume.jpg`
- `generique-chateau-toiture.jpg`
- `generique-chateau.jpg`
- `generique-cinema.jpg`
- `generique-croisiere.jpg`
- `generique-domaine.jpg`
- `generique-escalade-bloc-outdoor.jpg`
- `generique-escalade-bouldering.jpg`
- `generique-escalade-outdoor-falaise.jpg`
- `generique-escalade-wall.jpg`
- `generique-escape-game-cadenas.jpg`
- `generique-escape-game-exit.jpg`
- `generique-escape-game-neon.jpg`
- `generique-famille-balade.jpg`
- `generique-famille-foret.jpg`
- `generique-karting-indoor-motion.jpg`
- `generique-karting-indoor.jpg`
- `generique-karting-outdoor-3kids.jpg`
- `generique-karting-outdoor-aerial.jpg`
- `generique-karting-outdoor-track.jpg`
- `generique-lac-coucher-soleil.jpg`
- `generique-lac.jpg`
- `generique-lancer-de-hache.jpg`
- `generique-laser-game.jpg`
- `generique-musee-classique.jpg`
- `generique-musee-grande-galerie.jpg`
- `generique-musee-moderne.jpg`
- `generique-musee.jpg`
- `generique-paddle-aviron-detail.jpg`
- `generique-parapente-decollage.jpg`
- `generique-parapente-vol.jpg`
- `generique-parc.jpg`
- `generique-patinoire-hockey.jpg`
- `generique-patinoire-patins-blancs.jpg`
- `generique-patinoire-skater.jpg`
- `generique-point-de-vue.jpg`
- `generique-port-annecy.jpg`
- `generique-sentier-arete-alpine.jpg`
- `generique-sentier-automne-orange.jpg`
- `generique-sentier-automne-rouge.jpg`
- `generique-sentier-detail-pomme-pin.jpg`
- `generique-sentier-fog.jpg`
- `generique-sentier-foret-alpine.jpg`
- `generique-sentier-foret.jpg`
- `generique-sentier-hiver-neige.jpg`
- `generique-sentier-melezes-automne.jpg`
- `generique-sentier-sommet-panorama.jpg`
- `generique-sentier.jpg`
- `generique-spa-bien-etre.jpg`
- `generique-spa-bols-tibetains.jpg`
- `generique-spa-huile-essentielle.jpg`
- `generique-spa-jardin-tropical.jpg`
- `generique-telecabine.jpg`
- `generique-thermes-hammam.jpg`
- `generique-trampoline-park-saut.jpg`
- `generique-voie-verte-cyclistes-lac.jpg`
- `generique-voie-verte-cyclistes-riviere.jpg`
- `generique-voie-verte-famille-kids.jpg`
- `generique-voie-verte-foret.jpg`
- `generique-voie-verte-urbaine.jpg`
- `generique-voie-verte.jpg`
- `generique-vr-immersion.jpg`
- `generique-vr-multi-joueurs.jpg`

## User-requested examples (sanity check)

| slug | user wants | currently | proposed | reason |
|---|---|---|---|---|
| `acroparc-de-bellavallis-bellevaux` | accrobranche | `/generique-parc.jpg` | **`generique-famille-foret.jpg`** | accrobranche/forest-park |
| `jardin-alpin-de-bellevaux` | parc | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `ferme-pedagogique-petit-mont-bellevaux` | ferme | `generique-escape-game-cadenas.jpg` | **`generique-famille-balade.jpg`** | ferme pédagogique |
| `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy` | parc/plant | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin |
| `spa-vitam-bien-etre-neydens` | indoor pool / spa | `generique-attraction.jpg` | **`generique-spa-bien-etre.jpg`** | spa/bien-être |

## Proposed remappings by reason

### musée (22 fiches)

| slug | current | proposed |
|---|---|---|
| `espace-tairraz-musee-des-cristaux-chamonix` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** |
| `la-turbine-sciences-cran-gevrier` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** |
| `maison-de-barberine-vallorcine` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `maison-du-lieutenant-servoz` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `maison-fromage-abondance-abondance` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-ailes-anciennes-excenevex` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-archeologique-viuz-faverges` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-art-et-folklore-regional-fessy` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-cordonnerie-alby-sur-cheran` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-du-batiment-ville-la-grand` | `generique-musee-grande-galerie.jpg` | **`generique-musee.jpg`** |
| `musee-du-mont-blanc-chamonix` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-faune-bellevaux` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-horlogerie-et-decolletage-cluses` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** |
| `musee-montagnard-les-houches` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-nature-gruffy` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-patrimonial-pays-thones-fondateurs-francois-et-lucien-cochat-thones` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-poterie-savoyarde-filliere` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** |
| `musee-prehistoire-geologie-sciez` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `musee-ski-ancien-chapelle-abondance` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `museum-des-papillons-et-insectes-faverges` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |
| `notre-histoire-musee-rumilly-rumilly` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** |
| `palais-de-l-ile-annecy` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** |

### sentier (12 fiches)

| slug | current | proposed |
|---|---|---|
| `chemin-alpage-parcours-decouverte-habere-lullin` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier.jpg`** |
| `debaroule-clusaz` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `gr96-bornes-aravis-haute-savoie` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** |
| `grp-littoral-leman-saint-gingolph` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `grp-tour-lac-annecy-annecy` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `grp-tour-pays-mont-blanc-sallanches` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** |
| `itineraire-pedestre-bords-arve-gaillard-a-arthaz-gaillard` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `sentier-desert-de-plate-passy` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `sentier-espagnols-pas-du-roc-glieres` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** |
| `sentier-maison-saleve-pomier-presilly` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** |
| `suivez-mouche-alby-sur-cheran` | `generique-sentier-foret.jpg` | **`generique-sentier.jpg`** |
| `tour-du-mont-blanc-les-houches` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** |

### château (10 fiches)

| slug | current | proposed |
|---|---|---|
| `ancien-remparts-chateau-lullin-lullin` | `generique-musee-classique.jpg` | **`generique-chateau-toiture.jpg`** |
| `chateau-comtal-saint-julien-en-genevois` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-toiture.jpg`** |
| `chateau-croix-scionzier` | `generique-chateau.jpg` | **`generique-chateau-toiture.jpg`** |
| `chateau-fonbonne-et-herbularius-evian-bains` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-toiture.jpg`** |
| `chateau-sonnaz-thonon-bains` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** |
| `chateau-thenieres-ballaison` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** |
| `cinema-cine-chateau-bonneville` | `generique-cinema.jpg` | **`generique-chateau-toiture.jpg`** |
| `musee-chateau-annecy` | `generique-musee-classique.jpg` | **`generique-chateau-toiture.jpg`** |
| `parc-chateau-taninges` | `generique-parc.jpg` | **`generique-chateau-toiture.jpg`** |
| `tour-bellecombe-reignier` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** |

### lac/plage (9 fiches)

| slug | current | proposed |
|---|---|---|
| `plage-d-amphion-publier` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-duingt` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-messery` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-saint-gingolph` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-sevrier` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-talloires` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-de-tougues-chens` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-du-lac-de-montriond` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |
| `plage-imperial-annecy` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** |

### point de vue/sommet (8 fiches)

| slug | current | proposed |
|---|---|---|
| `golf-practice-belvedere-saint-martin-bellevue` | `generique-attraction.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `sentier-decouverte-plateau-glieres-thorens-glieres` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `sentier-geologique-pointe-percee-grand-bornand` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `telecabine-panoramic-mont-blanc` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `telepherique-aiguille-du-midi` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `telepherique-du-saleve` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `thiou-a-annecy-annecy` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** |
| `train-du-montenvers-mer-de-glace` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** |

### accrobranche/forest-park (7 fiches)

| slug | current | proposed |
|---|---|---|
| `accrobranche-foret-aventures-manigod` | `generique-attraction.jpg` | **`generique-famille-foret.jpg`** |
| `accrobranche-la-foret-magique-chamonix` | `generique-attraction.jpg` | **`generique-famille-foret.jpg`** |
| `acroparc-de-bellavallis-bellevaux` | `generique-parc.jpg` | **`generique-famille-foret.jpg`** |
| `chatel-accrobranche-1600-chatel` | `generique-domaine.jpg` | **`generique-famille-foret.jpg`** |
| `leman-forest-saint-gingolph` | `generique-parc.jpg` | **`generique-famille-foret.jpg`** |
| `parc-aventure-mont-blanc-saint-gervais` | `generique-attraction.jpg` | **`generique-famille-foret.jpg`** |
| `tactiq-aventure-cruseilles` | `generique-domaine.jpg` | **`generique-famille-foret.jpg`** |

### sentier famille (7 fiches)

| slug | current | proposed |
|---|---|---|
| `balade-pedestre-tour-lac-mole-tour` | `generique-sentier-automne-orange.jpg` | **`generique-famille-balade.jpg`** |
| `boucle-pedestre-detective-nature-jonzier-epagny` | `generique-sentier-hiver-neige.jpg` | **`generique-famille-balade.jpg`** |
| `sentier-morclan-chatel` | `generique-sentier-sommet-panorama.jpg` | **`generique-famille-balade.jpg`** |
| `sentier-pedestre-a-decouverte-village-vernaz-vernaz` | `generique-sentier-automne-orange.jpg` | **`generique-famille-balade.jpg`** |
| `sentier-pedestre-eterlou-chatel` | `generique-sentier-hiver-neige.jpg` | **`generique-famille-balade.jpg`** |
| `sentier-pedestre-sens-et-decouverte-animaux-ferme-copponex` | `generique-sentier-foret.jpg` | **`generique-famille-balade.jpg`** |
| `sentier-roselieres-saint-jorioz` | `generique-sentier-foret.jpg` | **`generique-famille-balade.jpg`** |

### musée patrimoine/écomusée (7 fiches)

| slug | current | proposed |
|---|---|---|
| `ecomusee-bois-foret-thones` | `generique-musee.jpg` | **`generique-musee-classique.jpg`** |
| `ecomusee-lac-annecy-sevrier` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** |
| `ecomusee-paysalp-viuz-en-sallaz` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** |
| `ecomusee-peche-et-du-lac-thonon` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** |
| `ferme-ecomusee-clos-parchet-samoens` | `generique-musee-grande-galerie.jpg` | **`generique-musee-classique.jpg`** |
| `maison-de-la-memoire-paysalp` | `generique-musee.jpg` | **`generique-musee-classique.jpg`** |
| `musee-paysan-un-site-paysalp-culture-patrimoine-viuz-en-sallaz` | `generique-musee-grande-galerie.jpg` | **`generique-musee-classique.jpg`** |

### aquaparc (5 fiches)

| slug | current | proposed |
|---|---|---|
| `aquaparc-chateau-bleu-annemasse` | `generique-aquatique-piscine-exterieur.jpg` | **`generique-aquatique-toboggan.jpg`** |
| `aquaparc-thonon-piscine-olympique-thonon` | `generique-aquatique-piscine-exterieur.jpg` | **`generique-aquatique-toboggan.jpg`** |
| `espace-aquatique-la-clusaz` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** |
| `piscine-ile-bleue-seynod` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** |
| `piscine-jean-regis-annecy` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** |

### chiens de traineau (5 fiches)

| slug | current | proposed |
|---|---|---|
| `chiens-de-traineau-a-ton-etoile-la-chapelle-dabondance` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** |
| `chiens-de-traineau-evasion-nordique-les-carroz` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** |
| `chiens-de-traineau-granges-de-heidi-passy` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** |
| `chiens-de-traineau-la-patte-nordic-les-gets` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** |
| `chiens-de-traineau-nordic-event-74` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** |

### escape game (5 fiches)

| slug | current | proposed |
|---|---|---|
| `escape-game-atelier-des-enigmes-annecy` | `generique-escape-game-cadenas.jpg` | **`generique-escape-game-neon.jpg`** |
| `escape-game-break-out-sevrier` | `generique-escape-game-exit.jpg` | **`generique-escape-game-neon.jpg`** |
| `escape-game-issue-secrete-anthy-sur-leman` | `generique-escape-game-cadenas.jpg` | **`generique-escape-game-neon.jpg`** |
| `escape-game-la-grande-evasion-annecy` | `generique-escape-game-cadenas.jpg` | **`generique-escape-game-neon.jpg`** |
| `escape-game-mysteres-du-lac-annecy` | `generique-escape-game-exit.jpg` | **`generique-escape-game-neon.jpg`** |

### karting (5 fiches)

| slug | current | proposed |
|---|---|---|
| `karting-mk-circuit-scientrier` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** |
| `karting-mont-blanc-passy` | `generique-karting-outdoor-3kids.jpg` | **`generique-karting-outdoor-track.jpg`** |
| `karting-rumilly-rumilly` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** |
| `karting-team-bouvier-pringy` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** |
| `karting-thones` | `generique-karting-indoor-motion.jpg` | **`generique-karting-indoor.jpg`** |

### via ferrata (5 fiches)

| slug | current | proposed |
|---|---|---|
| `via-ferrata-jallouvre-le-grand-bornand` | `generique-escalade-wall.jpg` | **`generique-escalade-outdoor-falaise.jpg`** |
| `via-ferrata-pollet-villard-la-clusaz` | `generique-escalade-wall.jpg` | **`generique-escalade-outdoor-falaise.jpg`** |
| `via-ferrata-saix-de-miolene-abondance` | `generique-escalade-bouldering.jpg` | **`generique-escalade-outdoor-falaise.jpg`** |
| `via-ferrata-sixt-fer-a-cheval` | `generique-escalade-bloc-outdoor.jpg` | **`generique-escalade-outdoor-falaise.jpg`** |
| `via-ferrata-thones` | `generique-escalade-bouldering.jpg` | **`generique-escalade-outdoor-falaise.jpg`** |

### sentier automne (4 fiches)

| slug | current | proposed |
|---|---|---|
| `au-fil-rail-jeu-piste-a-servoz-servoz` | `generique-sentier-automne-orange.jpg` | **`generique-sentier-melezes-automne.jpg`** |
| `boucles-coteau-publier` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-melezes-automne.jpg`** |
| `chemin-art-nature-andilly-andilly` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-melezes-automne.jpg`** |
| `parcours-patrimoine-se-promener-a-andilly-andilly` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-melezes-automne.jpg`** |

### base nautique (4 fiches)

| slug | current | proposed |
|---|---|---|
| `base-nautique-doussard-doussard` | `generique-paddle-aviron-detail.jpg` | **`generique-port-annecy.jpg`** |
| `base-nautique-evian-bains` | `generique-domaine.jpg` | **`generique-port-annecy.jpg`** |
| `base-nautique-marquisats-annecy` | `generique-paddle-aviron-detail.jpg` | **`generique-port-annecy.jpg`** |
| `port-clerges-base-nautique-thonon-bains` | `generique-domaine.jpg` | **`generique-port-annecy.jpg`** |

### parc (4 fiches)

| slug | current | proposed |
|---|---|---|
| `cinema-le-parc-la-roche-sur-foron` | `generique-cinema.jpg` | **`generique-parc.jpg`** |
| `escalade-la-crique-annecy` | `generique-escalade-bouldering.jpg` | **`generique-parc.jpg`** |
| `parc-de-peche-domaine-du-moulin-authier` | `generique-domaine.jpg` | **`generique-parc.jpg`** |
| `via-ferrata-parc-thermal-saint-gervais` | `generique-escalade-bloc-outdoor.jpg` | **`generique-parc.jpg`** |

### jardin (4 fiches)

| slug | current | proposed |
|---|---|---|
| `jardin-cimes-passy` | `generique-attraction.jpg` | **`generique-parc.jpg`** |
| `jardin-les-jardins-secrets-vaulx` | `generique-spa-bols-tibetains.jpg` | **`generique-parc.jpg`** |
| `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy` | `generique-attraction.jpg` | **`generique-parc.jpg`** |
| `jardin-pre-curieux-evian` | `generique-attraction.jpg` | **`generique-parc.jpg`** |

### patinoire (4 fiches)

| slug | current | proposed |
|---|---|---|
| `patinoire-jean-regis-annecy` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** |
| `patinoire-morzine` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** |
| `patinoire-palais-megeve` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** |
| `patinoire-richard-bozon-chamonix` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** |

### château ruines (3 fiches)

| slug | current | proposed |
|---|---|---|
| `bourg-et-ruines-chateau-chaumont-chaumont` | `generique-musee-moderne.jpg` | **`generique-chateau-brume.jpg`** |
| `ruines-chateau-habere-lullin-habere-lullin` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-brume.jpg`** |
| `ruines-chateau-st-michel-houches` | `generique-musee-classique.jpg` | **`generique-chateau-brume.jpg`** |

### croisière (3 fiches)

| slug | current | proposed |
|---|---|---|
| `croisiere-bateaux-annecy-annecy` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** |
| `croisiere-cgn-evian` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** |
| `croisiere-cgn-yvoire` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** |

### VR / simulator (3 fiches)

| slug | current | proposed |
|---|---|---|
| `ereel-annecy-sillingy` | `generique-parc.jpg` | **`generique-vr-immersion.jpg`** |
| `simulateur-warmup-academy-margencel` | `generique-attraction.jpg` | **`generique-vr-immersion.jpg`** |
| `vr-ereel-annecy-sillingy` | `generique-escape-game-exit.jpg` | **`generique-vr-immersion.jpg`** |

### canyoning/rafting (3 fiches)

| slug | current | proposed |
|---|---|---|
| `rafting-ecolorado-passy-samoens` | `generique-attraction.jpg` | **`generique-cascade.jpg`** |
| `rafting-frogs-rafting-dranse` | `generique-attraction.jpg` | **`generique-cascade.jpg`** |
| `rafting-rando-rafting-samoens` | `generique-attraction.jpg` | **`generique-cascade.jpg`** |

### bar à jeux (2 fiches)

| slug | current | proposed |
|---|---|---|
| `arcade-art-of-pinball-poisy` | `generique-attraction.jpg` | **`generique-bar-jeux.jpg`** |
| `bar-a-jeux-youri-bar-cran-gevrier` | `generique-escape-game-exit.jpg` | **`generique-bar-jeux.jpg`** |

### centre nautique (2 fiches)

| slug | current | proposed |
|---|---|---|
| `base-nautique-sciez-sciez` | `generique-port-annecy.jpg` | **`generique-aquatique-piscine-couverte.jpg`** |
| `plage-d-evian-centre-nautique` | `generique-lac-coucher-soleil.jpg` | **`generique-aquatique-piscine-couverte.jpg`** |

### spa/bien-être (2 fiches)

| slug | current | proposed |
|---|---|---|
| `escalade-space-bloc-sillingy` | `generique-escalade-wall.jpg` | **`generique-spa-bien-etre.jpg`** |
| `spa-vitam-bien-etre-neydens` | `generique-attraction.jpg` | **`generique-spa-bien-etre.jpg`** |

### jardin alpin/botanique (2 fiches)

| slug | current | proposed |
|---|---|---|
| `jardin-alpin-de-bellevaux` | `generique-attraction.jpg` | **`generique-parc.jpg`** |
| `jardin-jaysinia-samoens` | `generique-attraction.jpg` | **`generique-parc.jpg`** |

### cascade (2 fiches)

| slug | current | proposed |
|---|---|---|
| `sentier-cascades-sixt-fer-a-cheval` | `generique-sentier-hiver-neige.jpg` | **`generique-cascade.jpg`** |
| `via-ferrata-berard-vallorcine` | `generique-escalade-wall.jpg` | **`generique-cascade.jpg`** |

### thermes (2 fiches)

| slug | current | proposed |
|---|---|---|
| `spa-qc-terme-chamonix` | `generique-attraction.jpg` | **`generique-thermes-hammam.jpg`** |
| `thermes-saint-gervais-mont-blanc` | `generique-attraction.jpg` | **`generique-thermes-hammam.jpg`** |

### spéléo (2 fiches)

| slug | current | proposed |
|---|---|---|
| `speleo-bureau-montagne-saleve` | `generique-attraction.jpg` | **`generique-sentier-foret-alpine.jpg`** |
| `speleo-grotte-de-balme-magland` | `generique-attraction.jpg` | **`generique-sentier-foret-alpine.jpg`** |

### voie verte (2 fiches)

| slug | current | proposed |
|---|---|---|
| `veloroute-vallee-arve-cluses-sallanches` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte.jpg`** |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte.jpg`** |

### wakepark (2 fiches)

| slug | current | proposed |
|---|---|---|
| `wakepark-ponton-embarcadere-saint-jorioz` | `generique-attraction.jpg` | **`generique-paddle-aviron-detail.jpg`** |
| `wakepark-tna-cable-park-arenthon` | `generique-attraction.jpg` | **`generique-paddle-aviron-detail.jpg`** |

### baignade biotope (1 fiches)

| slug | current | proposed |
|---|---|---|
| `baignade-biotope-combloux` | `generique-attraction.jpg` | **`generique-aquatique-bassin-natation.jpg`** |

### bowling (1 fiches)

| slug | current | proposed |
|---|---|---|
| `bowling-sevrier-sevrier` | `generique-bowling-strike.jpg` | **`generique-bowling-lanes.jpg`** |

### bureau des guides (1 fiches)

| slug | current | proposed |
|---|---|---|
| `bureau-des-guides-annecy` | `generique-escalade-bloc-outdoor.jpg` | **`generique-sentier-arete-alpine.jpg`** |

### ferme pédagogique (1 fiches)

| slug | current | proposed |
|---|---|---|
| `ferme-pedagogique-petit-mont-bellevaux` | `generique-escape-game-cadenas.jpg` | **`generique-famille-balade.jpg`** |

### réserve naturelle (1 fiches)

| slug | current | proposed |
|---|---|---|
| `jardin-alpin-des-montets-vallorcine` | `generique-attraction.jpg` | **`generique-sentier-foret-alpine.jpg`** |

### lancer de hache (1 fiches)

| slug | current | proposed |
|---|---|---|
| `lancer-de-hache-l-hachez-vous-annecy` | `generique-bar-jeux.jpg` | **`generique-lancer-de-hache.jpg`** |

### musée cinéma (1 fiches)

| slug | current | proposed |
|---|---|---|
| `musee-cinema-philippe-piccot-douvaine` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** |

### sentier panorama (1 fiches)

| slug | current | proposed |
|---|---|---|
| `parcours-marche-boucle-pedestre-uffin-neydens` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-sommet-panorama.jpg`** |

### trampoline park (1 fiches)

| slug | current | proposed |
|---|---|---|
| `trampoline-park-elevation-indoor-neydens` | `generique-escalade-outdoor-falaise.jpg` | **`generique-trampoline-park-saut.jpg`** |

### tropical (1 fiches)

| slug | current | proposed |
|---|---|---|
| `tropicaland-viry` | `generique-parc.jpg` | **`generique-spa-jardin-tropical.jpg`** |

### voie verte lac (1 fiches)

| slug | current | proposed |
|---|---|---|
| `voie-verte-lac-annecy-annecy` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte-cyclistes-lac.jpg`** |

### voile (1 fiches)

| slug | current | proposed |
|---|---|---|
| `voile-cercle-thonon-thonon` | `generique-paddle-aviron-detail.jpg` | **`generique-port-annecy.jpg`** |
