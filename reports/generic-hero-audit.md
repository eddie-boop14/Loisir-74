# Generic hero remapping — diversified by description + adjacency-aware

**Date**: 2026-06-14
**Status**: REPORT — no JSON or HTML mutated yet

## Summary

- Fiches on `/generique-*.jpg`: **276**
- **Proposed changes**: 170
- Unchanged (current is best pick): 106
- Adjacent-duplicate cards on hubs:
  - before: **19**
  - after:  **3**

## Algorithm

For each fiche, a ranked candidate list is built from the fiche's description, name, facts, and category (top = most descriptive match). The assignment pass processes fiches in **most-constrained-first** order (largest in-bucket sibling count) and picks the highest-ranked candidate not already used by an in-bucket sibling. A bucket = (hub, commune): siblings = the other fiches that will sit in the same commune-section within the same hub.

Vitam carries two equally good candidates (indoor pool + spa) so its neighbour decides.

## User-requested examples

| slug | current | proposed | reason |
|---|---|---|---|
| `acroparc-de-bellavallis-bellevaux` | `generique-parc.jpg` | **`generique-famille-balade.jpg`** | accrobranche · mention famille/enfants |
| `jardin-alpin-de-bellevaux` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `ferme-pedagogique-petit-mont-bellevaux` | `generique-escape-game-cadenas.jpg` | **`generique-famille-balade.jpg`** | ferme pédagogique (closest) |
| `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `spa-vitam-bien-etre-neydens` | `generique-attraction.jpg` | **`generique-aquatique-piscine-couverte.jpg`** | vitam · grand bassin couvert |

## All proposed changes

| slug | current | proposed | reason |
|---|---|---|---|
| `accrobranche-foret-aventures-manigod` | `generique-attraction.jpg` | **`generique-famille-foret.jpg`** | accrobranche en forêt |
| `accrobranche-la-foret-magique-chamonix` | `generique-attraction.jpg` | **`generique-famille-balade.jpg`** | accrobranche · mention famille/enfants |
| `acroparc-de-bellavallis-bellevaux` | `generique-parc.jpg` | **`generique-famille-balade.jpg`** | accrobranche · mention famille/enfants |
| `ancien-remparts-chateau-lullin-lullin` | `generique-musee-classique.jpg` | **`generique-chateau-brume.jpg`** | château · ruines/atmosphère |
| `aquaparc-aqualis-cluses` | `generique-aquatique-toboggan.jpg` | **`generique-aquatique-bassin-natation.jpg`** | bassin natation |
| `aquaparc-chateau-bleu-annemasse` | `generique-aquatique-piscine-exterieur.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `aquaparc-thonon-piscine-olympique-thonon` | `generique-aquatique-piscine-exterieur.jpg` | **`generique-aquatique-toboggan.jpg`** | aquaparc · toboggans |
| `arcade-art-of-pinball-poisy` | `generique-attraction.jpg` | **`generique-bar-jeux.jpg`** | bar à jeux |
| `au-fil-rail-jeu-piste-a-servoz-servoz` | `generique-sentier-automne-orange.jpg` | **`generique-sentier-melezes-automne.jpg`** | sentier · mélèzes/automne |
| `baignade-biotope-combloux` | `generique-attraction.jpg` | **`generique-aquatique-bassin-natation.jpg`** | baignade biotope |
| `balade-pedestre-tour-lac-mole-tour` | `generique-sentier-automne-orange.jpg` | **`generique-sentier-melezes-automne.jpg`** | sentier · mélèzes/automne |
| `bar-a-jeux-youri-bar-cran-gevrier` | `generique-escape-game-exit.jpg` | **`generique-bar-jeux.jpg`** | bar à jeux |
| `base-de-loisirs-du-vuaz-filliere` | `generique-parc.jpg` | **`generique-famille-foret.jpg`** | parc animalier |
| `base-de-loisirs-orange-montisel-saint-sixt` | `generique-domaine.jpg` | **`generique-attraction.jpg`** | fallback |
| `base-nautique-evian-bains` | `generique-domaine.jpg` | **`generique-paddle-aviron-detail.jpg`** | base nautique · paddle/aviron |
| `boucle-pedestre-detective-nature-jonzier-epagny` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier-melezes-automne.jpg`** | sentier · mélèzes/automne |
| `boucles-coteau-publier` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-sommet-panorama.jpg`** | sentier · panorama/sommet |
| `bourg-et-ruines-chateau-chaumont-chaumont` | `generique-musee-moderne.jpg` | **`generique-chateau-brume.jpg`** | château · ruines/atmosphère |
| `bowling-sevrier-sevrier` | `generique-bowling-strike.jpg` | **`generique-bowling-lanes.jpg`** | bowling · lanes |
| `bureau-des-guides-annecy` | `generique-escalade-bloc-outdoor.jpg` | **`generique-sentier-arete-alpine.jpg`** | guides · alpinisme |
| `canyoning-escape-canyon` | `generique-attraction.jpg` | **`generique-escape-game-exit.jpg`** | escape · sortie |
| `centre-aquatique-forme-d-o-chatel` | `generique-attraction.jpg` | **`generique-aquatique-toboggan.jpg`** | aquatique · toboggan |
| `chateau-comtal-saint-julien-en-genevois` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-brume.jpg`** | château · ruines/atmosphère |
| `chateau-croix-scionzier` | `generique-chateau.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `chateau-fonbonne-et-herbularius-evian-bains` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-toiture.jpg`** | château médiéval |
| `chateau-sonnaz-thonon-bains` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `chateau-thenieres-ballaison` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** | château médiéval |
| `chatel-accrobranche-1600-chatel` | `generique-domaine.jpg` | **`generique-famille-foret.jpg`** | accrobranche défaut |
| `chemin-alpage-parcours-decouverte-habere-lullin` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `chemin-art-nature-andilly-andilly` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-melezes-automne.jpg`** | sentier · mélèzes/automne |
| `chiens-de-traineau-a-ton-etoile-la-chapelle-dabondance` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** | chiens de traineau · neige |
| `chiens-de-traineau-evasion-nordique-les-carroz` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** | chiens de traineau · neige |
| `chiens-de-traineau-granges-de-heidi-passy` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** | chiens de traineau · neige |
| `chiens-de-traineau-la-patte-nordic-les-gets` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** | chiens de traineau · neige |
| `chiens-de-traineau-nordic-event-74` | `generique-attraction.jpg` | **`generique-sentier-hiver-neige.jpg`** | chiens de traineau · neige |
| `cinema-cine-chateau-bonneville` | `generique-cinema.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `cinema-le-parc-la-roche-sur-foron` | `generique-cinema.jpg` | **`generique-parc.jpg`** | parc |
| `croisiere-bateaux-annecy-annecy` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** | croisière |
| `croisiere-cgn-evian` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** | croisière |
| `croisiere-cgn-yvoire` | `generique-port-annecy.jpg` | **`generique-croisiere.jpg`** | croisière |
| `debaroule-clusaz` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier-foret-alpine.jpg`** | sentier · forêt alpine |
| `domaine-de-guidou` | `generique-domaine.jpg` | **`generique-attraction.jpg`** | fallback |
| `ecomusee-lac-annecy-sevrier` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** | musée patrimoine/écomusée |
| `ecomusee-paysalp-viuz-en-sallaz` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** | musée patrimoine/écomusée |
| `ecomusee-peche-et-du-lac-thonon` | `generique-musee-moderne.jpg` | **`generique-musee-classique.jpg`** | musée patrimoine/écomusée |
| `escalade-ablok-argonay` | `generique-escalade-bloc-outdoor.jpg` | **`generique-attraction.jpg`** | fallback |
| `escalade-atome-annecy` | `generique-escalade-bouldering.jpg` | **`generique-attraction.jpg`** | fallback |
| `escalade-climb-up-annecy` | `generique-escalade-bloc-outdoor.jpg` | **`generique-attraction.jpg`** | fallback |
| `escalade-cortigrimpe-metz-tessy` | `generique-escalade-outdoor-falaise.jpg` | **`generique-attraction.jpg`** | fallback |
| `escalade-la-crique-annecy` | `generique-escalade-bouldering.jpg` | **`generique-parc.jpg`** | parc |
| `escalade-space-bloc-sillingy` | `generique-escalade-wall.jpg` | **`generique-spa-bien-etre.jpg`** | spa · bien-être |
| `escape-game-break-out-sevrier` | `generique-escape-game-exit.jpg` | **`generique-escape-game-neon.jpg`** | escape défaut |
| `escape-game-issue-secrete-anthy-sur-leman` | `generique-escape-game-cadenas.jpg` | **`generique-escape-game-neon.jpg`** | escape défaut |
| `escape-game-la-grande-evasion-annecy` | `generique-escape-game-cadenas.jpg` | **`generique-escape-game-exit.jpg`** | escape · sortie |
| `escape-game-mysteres-du-lac-annecy` | `generique-escape-game-exit.jpg` | **`generique-escape-game-neon.jpg`** | escape défaut |
| `espace-aquatique-la-clusaz` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** | aquaparc · toboggans |
| `espace-tairraz-musee-des-cristaux-chamonix` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** | musée défaut |
| `ferme-ecomusee-clos-parchet-samoens` | `generique-musee-grande-galerie.jpg` | **`generique-musee-classique.jpg`** | musée patrimoine/écomusée |
| `ferme-pedagogique-les-paturettes-rumilly` | `generique-famille-balade.jpg` | **`generique-famille-foret.jpg`** | parc animalier |
| `ferme-pedagogique-petit-mont-bellevaux` | `generique-escape-game-cadenas.jpg` | **`generique-famille-balade.jpg`** | ferme pédagogique (closest) |
| `golf-practice-belvedere-saint-martin-bellevue` | `generique-attraction.jpg` | **`generique-sentier-sommet-panorama.jpg`** | point de vue · sommet/panorama |
| `gr96-bornes-aravis-haute-savoie` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `grp-littoral-leman-saint-gingolph` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `grp-tour-lac-annecy-annecy` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `grp-tour-pays-mont-blanc-sallanches` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `itineraire-pedestre-chemin-bords-dranse-chatel` | `generique-sentier-hiver-neige.jpg` | **`generique-famille-balade.jpg`** | sentier · famille |
| `jardin-alpin-de-bellevaux` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `jardin-alpin-des-montets-vallorcine` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `jardin-cimes-passy` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin |
| `jardin-jaysinia-samoens` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `jardin-les-jardins-secrets-vaulx` | `generique-spa-bols-tibetains.jpg` | **`generique-parc.jpg`** | jardin |
| `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `jardin-pre-curieux-evian` | `generique-attraction.jpg` | **`generique-parc.jpg`** | jardin alpin/botanique |
| `karting-indoor-urban-kartin-la-roche` | `generique-karting-indoor.jpg` | **`generique-karting-indoor-motion.jpg`** | karting · indoor motion |
| `karting-mk-circuit-scientrier` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** | karting · piste outdoor |
| `karting-mont-blanc-passy` | `generique-karting-outdoor-3kids.jpg` | **`generique-karting-outdoor-track.jpg`** | karting · piste outdoor |
| `karting-rumilly-rumilly` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** | karting · piste outdoor |
| `karting-team-bouvier-pringy` | `generique-karting-outdoor-aerial.jpg` | **`generique-karting-outdoor-track.jpg`** | karting · piste outdoor |
| `la-turbine-sciences-cran-gevrier` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** | musée défaut |
| `lancer-de-hache-l-hachez-vous-annecy` | `generique-bar-jeux.jpg` | **`generique-lancer-de-hache.jpg`** | lancer de hache |
| `leman-forest-saint-gingolph` | `generique-parc.jpg` | **`generique-famille-balade.jpg`** | accrobranche · mention famille/enfants |
| `maison-de-la-memoire-paysalp` | `generique-musee.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `maison-du-saleve-presilly` | `generique-musee.jpg` | **`generique-musee-classique.jpg`** | musée patrimoine/écomusée |
| `maison-fromage-abondance-abondance` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `mine-lappiaz-morzine` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `musee-ailes-anciennes-excenevex` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-archeologique-viuz-faverges` | `generique-musee-classique.jpg` | **`generique-musee-grande-galerie.jpg`** | musée grande galerie |
| `musee-art-sacre-saint-gervais-bains` | `generique-musee.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-chateau-annecy` | `generique-musee-classique.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `musee-cinema-philippe-piccot-douvaine` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-cordonnerie-alby-sur-cheran` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-departemental-sapeurs-pompiers-haute-savoie-sciez` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-du-batiment-ville-la-grand` | `generique-musee-grande-galerie.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-du-mont-blanc-chamonix` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-faune-bellevaux` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-horlogerie-et-decolletage-cluses` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-montagnard-les-houches` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-nature-gruffy` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-patrimonial-pays-thones-fondateurs-francois-et-lucien-cochat-thones` | `generique-musee-classique.jpg` | **`generique-musee-moderne.jpg`** | musée moderne/art |
| `musee-paysan-un-site-paysalp-culture-patrimoine-viuz-en-sallaz` | `generique-musee-grande-galerie.jpg` | **`generique-musee.jpg`** | musée défaut |
| `musee-prehistoire-geologie-sciez` | `generique-musee-classique.jpg` | **`generique-musee-grande-galerie.jpg`** | musée grande galerie |
| `museum-des-papillons-et-insectes-faverges` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `notre-histoire-musee-rumilly-rumilly` | `generique-musee-moderne.jpg` | **`generique-musee.jpg`** | musée défaut |
| `palais-de-l-ile-annecy` | `generique-musee-classique.jpg` | **`generique-musee.jpg`** | musée défaut |
| `parc-aventure-mont-blanc-saint-gervais` | `generique-attraction.jpg` | **`generique-famille-foret.jpg`** | accrobranche défaut |
| `parc-chateau-taninges` | `generique-parc.jpg` | **`generique-chateau-toiture.jpg`** | château |
| `parc-de-peche-domaine-du-moulin-authier` | `generique-domaine.jpg` | **`generique-parc.jpg`** | parc |
| `parcours-marche-boucle-pedestre-uffin-neydens` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier-sommet-panorama.jpg`** | sentier · panorama/sommet |
| `parcours-patrimoine-se-promener-a-andilly-andilly` | `generique-sentier-automne-rouge.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `patinoire-morzine` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** | patinoire défaut |
| `patinoire-richard-bozon-chamonix` | `generique-patinoire-hockey.jpg` | **`generique-patinoire-skater.jpg`** | patinoire défaut |
| `piscine-ile-bleue-seynod` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** | aquaparc · toboggans |
| `piscine-jean-regis-annecy` | `generique-aquatique-piscine-couverte.jpg` | **`generique-aquatique-toboggan.jpg`** | aquaparc · toboggans |
| `plage-d-amphion-publier` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-de-duingt` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-de-messery` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-de-saint-gingolph` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-de-sevrier` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-de-tougues-chens` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-du-lac-de-montriond` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `plage-imperial-annecy` | `generique-lac.jpg` | **`generique-lac-coucher-soleil.jpg`** | plage |
| `port-clerges-base-nautique-thonon-bains` | `generique-domaine.jpg` | **`generique-paddle-aviron-detail.jpg`** | base nautique · paddle/aviron |
| `rafting-ecolorado-passy-samoens` | `generique-attraction.jpg` | **`generique-cascade.jpg`** | eaux vives · cascade |
| `rafting-frogs-rafting-dranse` | `generique-attraction.jpg` | **`generique-cascade.jpg`** | eaux vives · cascade |
| `rafting-rando-rafting-samoens` | `generique-attraction.jpg` | **`generique-cascade.jpg`** | eaux vives · cascade |
| `ruines-chateau-habere-lullin-habere-lullin` | `generique-musee-grande-galerie.jpg` | **`generique-chateau-brume.jpg`** | château · ruines/atmosphère |
| `ruines-chateau-st-michel-houches` | `generique-musee-classique.jpg` | **`generique-chateau-brume.jpg`** | château · ruines/atmosphère |
| `sentier-bout-du-lac-doussard` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-cascades-sixt-fer-a-cheval` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-desert-de-plate-passy` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-espagnols-pas-du-roc-glieres` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-maison-saleve-pomier-presilly` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-morclan-chatel` | `generique-sentier-sommet-panorama.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-pedestre-a-decouverte-village-vernaz-vernaz` | `generique-sentier-automne-orange.jpg` | **`generique-sentier-melezes-automne.jpg`** | sentier · mélèzes/automne |
| `sentier-pedestre-eterlou-chatel` | `generique-sentier-hiver-neige.jpg` | **`generique-famille-balade.jpg`** | sentier · famille |
| `sentier-pedestre-interpretation-lac-plagnes-abondance` | `generique-sentier-hiver-neige.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `sentier-pedestre-sens-et-decouverte-animaux-ferme-copponex` | `generique-sentier-foret.jpg` | **`generique-famille-balade.jpg`** | sentier · famille |
| `sentier-roselieres-saint-jorioz` | `generique-sentier-foret.jpg` | **`generique-famille-balade.jpg`** | sentier · famille |
| `simulateur-emotion-concept-annecy` | `generique-spa-bols-tibetains.jpg` | **`generique-attraction.jpg`** | fallback |
| `simulateur-warmup-academy-margencel` | `generique-attraction.jpg` | **`generique-vr-immersion.jpg`** | VR · immersion |
| `spa-qc-terme-chamonix` | `generique-attraction.jpg` | **`generique-thermes-hammam.jpg`** | thermes |
| `spa-vitam-bien-etre-neydens` | `generique-attraction.jpg` | **`generique-aquatique-piscine-couverte.jpg`** | vitam · grand bassin couvert |
| `speleo-bureau-montagne-saleve` | `generique-attraction.jpg` | **`generique-sentier-foret-alpine.jpg`** | spéléo · grotte |
| `speleo-grotte-de-balme-magland` | `generique-attraction.jpg` | **`generique-sentier-foret-alpine.jpg`** | spéléo · grotte |
| `suivez-mouche-alby-sur-cheran` | `generique-sentier-foret.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `tactiq-aventure-cruseilles` | `generique-domaine.jpg` | **`generique-famille-foret.jpg`** | accrobranche en forêt |
| `telecabine-panoramic-mont-blanc` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** | point de vue · sommet/panorama |
| `telepherique-aiguille-du-midi` | `generique-point-de-vue.jpg` | **`generique-telecabine.jpg`** | télécabine |
| `telepherique-du-saleve` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** | point de vue · sommet/panorama |
| `thermes-saint-gervais-mont-blanc` | `generique-attraction.jpg` | **`generique-thermes-hammam.jpg`** | thermes |
| `thiou-a-annecy-annecy` | `generique-point-de-vue.jpg` | **`generique-sentier-sommet-panorama.jpg`** | point de vue · sommet/panorama |
| `tour-bellecombe-reignier` | `generique-chateau-brume.jpg` | **`generique-chateau-toiture.jpg`** | château médiéval |
| `tour-du-mont-blanc-les-houches` | `generique-sentier-foret-alpine.jpg` | **`generique-sentier.jpg`** | sentier défaut |
| `trampoline-park-elevation-indoor-neydens` | `generique-escalade-outdoor-falaise.jpg` | **`generique-trampoline-park-saut.jpg`** | trampoline park |
| `tyrolienne-fantasticable-chatel` | `generique-parapente-vol.jpg` | **`generique-attraction.jpg`** | fallback |
| `ulm-leman-cervens` | `generique-parapente-vol.jpg` | **`generique-attraction.jpg`** | fallback |
| `veloroute-vallee-arve-cluses-sallanches` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte-cyclistes-riviere.jpg`** | voie verte · rivière |
| `via-ferrata-berard-vallorcine` | `generique-escalade-wall.jpg` | **`generique-cascade.jpg`** | cascade |
| `via-ferrata-jallouvre-le-grand-bornand` | `generique-escalade-wall.jpg` | **`generique-escalade-outdoor-falaise.jpg`** | via ferrata · falaise |
| `via-ferrata-parc-thermal-saint-gervais` | `generique-escalade-bloc-outdoor.jpg` | **`generique-parc.jpg`** | parc |
| `via-ferrata-pollet-villard-la-clusaz` | `generique-escalade-wall.jpg` | **`generique-escalade-outdoor-falaise.jpg`** | via ferrata · falaise |
| `via-ferrata-saix-de-miolene-abondance` | `generique-escalade-bouldering.jpg` | **`generique-escalade-outdoor-falaise.jpg`** | via ferrata · falaise |
| `via-ferrata-sixt-fer-a-cheval` | `generique-escalade-bloc-outdoor.jpg` | **`generique-escalade-outdoor-falaise.jpg`** | via ferrata · falaise |
| `via-ferrata-thones` | `generique-escalade-bouldering.jpg` | **`generique-escalade-outdoor-falaise.jpg`** | via ferrata · falaise |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte.jpg`** | voie verte défaut |
| `voie-verte-lac-annecy-annecy` | `generique-voie-verte-famille-kids.jpg` | **`generique-voie-verte-cyclistes-lac.jpg`** | voie verte · lac |
| `voile-cercle-thonon-thonon` | `generique-paddle-aviron-detail.jpg` | **`generique-port-annecy.jpg`** | voile |
| `vr-ereel-annecy-sillingy` | `generique-escape-game-exit.jpg` | **`generique-vr-multi-joueurs.jpg`** | VR · multi-joueurs |
| `wakepark-ponton-embarcadere-saint-jorioz` | `generique-attraction.jpg` | **`generique-paddle-aviron-detail.jpg`** | wakepark |
| `wakepark-tna-cable-park-arenthon` | `generique-attraction.jpg` | **`generique-paddle-aviron-detail.jpg`** | wakepark |