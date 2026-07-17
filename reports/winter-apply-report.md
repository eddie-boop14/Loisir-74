# Winter facts — APPLY report (JOB B)
Payload: `data/winter-facts-verified.json` · generated 2026-07-16
- Winter nodes touched: **49** · with real changes: **15** · category/vocab skips: **0**

---

## ⚑ SENSITIVE — Eddie sign-off required (access = closed / partial)
These are the highest-stakes lines on the site. Nothing below ships until you approve.

| slug | field | old → new | source |
|---|---|---|---|
| `mont-veyrier` | winter_access | ∅ → **closed** | lac-annecy.com — Boucle du Mont Veyrier (Annecy): route dated 'Du 30/04 au 10/11 tous les jours' (seasonal window, closed outside it) and 'de beau points de vue sur le lac, les Aravis, les Bauges et le Mont-Blanc' |
| `mont-veyrier` | snow_view | ∅ → **mont_blanc** | lac-annecy.com — Boucle du Mont Veyrier (Annecy): route dated 'Du 30/04 au 10/11 tous les jours' (seasonal window, closed outside it) and 'de beau points de vue sur le lac, les Aravis, les Bauges et le Mont-Blanc' |
| `cascade-de-nyon` | winter_access | ∅ → **closed** | en.morzine-avoriaz.com/equipment/nyon-waterfall/ (OT Morzine) — "Opening hours from 30 June to 01 November 2026" (structured Ouverture/opening-period field; no opening outside this window, i.e. closed in winter) |
| `cascade-des-brochaux` | winter_access | ∅ → **closed** | hautesavoiemontblanc-tourisme.com — fiche Sentier des Lindarets à la Cascade des Brochaux (Montriond) — "Du 01/05 au 31/10 tous les jours. Accessible hors période d'enneigement et en fonction des conditions climatiques. [...] Période de pratique conseillée : printemps - été - automne." |
| `cascade-du-dard` | winter_access | ∅ → **partial** | chamonix.fr/fiche-touristique/cascade-du-dard/ (OT Chamonix, champ Ouverture) — "Toute l'année : l'accessibilité dépend des conditions de neige." |
| `debaroule-clusaz` | winter_access | ∅ → **closed** | forfait.laclusaz.com/fr — Débaroule listed exclusively under 'Nos offres été' ('Nouveau / Débaroule / Le jeu préféré de toute la famille, depuis cet été!'), tied to the summer-only Patinoire cable car; no winter operation mentioned anywhere on the operator site |

---

## CONFIRM-grade rows (official sourcing; apply with the batch)

| slug | stage | field | old → new | source |
|---|---|---|---|---|
| `train-du-montenvers-mer-de-glace` | 1 | (no change) | — | CDM: service hivernal; montenverstrain.com: « Le Mont Blanc n'est pas visible depuis Montenvers » → alpes (Drus/Grandes Jorasses) |
| `col-des-aravis` | 1 | (no change) | — | OT Thônes/Combloux: col maintenu ouvert (fermetures rares), vue Mont-Blanc documentée |
| `col-de-la-croix-fry` | 1 | (no change) | — | OT Manigod/Thônes + skidefondbeauregard.com (36 km, face au Mont-Blanc) |
| `plateau-des-glieres` | 1 | (no change) | — | plateaudesglieres.fr/domainenordiquedesglieres.com: RD55 équipements obligatoires, domaine 29 km — route traversante piétonne l'hiver; accès conditionnel météo (inforoute74) |
| `col-des-glieres` | 1 | (no change) | — | idem plateau — même régime RD55 |
| `col-de-la-forclaz` | 1 | (no change) | — | RD42 col réel; pas de régime de fermeture saisonnier documenté (incidents ponctuels) → access null + lien inforoute74 |
| `le-semnoz` | 1 | (no change) | — | OT/haute-savoie-tourisme: table d'orientation Crêt de Châtillon nomme le Mont-Blanc; station ouverte l'hiver (D41) |
| `mont-saleve` | 1 | (no change) | — | telepherique-du-saleve.com + OT Monts du Genevois (itinéraires raquettes) |
| `telepherique-du-saleve` | 1 | (no change) | — | telepherique-du-saleve.com: « views as far as Mont Blanc » |
| `telepherique-aiguille-du-midi` | 1 | (no change) | — | CDM/OT Chamonix — exploitation hivernale, terrasse sommitale face au Mont-Blanc |
| `tramway-du-mont-blanc` | 1 | (no change) | — | CDM: service hivernal vers Bellevue; OT Saint-Gervais: plateau ouvert sur le massif du Mont-Blanc |
| `belvedere-panorama-360-combloux-la-cry` | 1 | (no change) | — | OT Combloux: table d'orientation de la Cry, chaîne du Mont-Blanc nommée |
| `plateau-de-solaison` | 2 | (no change) | — | Mairie Brison/Haute-Savoie Nordic (17–24 km + biathlon); panorama Bornes/Arve → alpes |
| `sentier-espagnols-pas-du-roc-glieres` | 2 | (no change) | — | régime Glières — panorama Aravis/Bornes |
| `mont-joly` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `col-des-pitons-saleve` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `mont-baron` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `telecabine-du-jaillet` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `cascade-des-fours` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `gr96-bornes-aravis-haute-savoie` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `grp-tour-lac-annecy-annecy` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `parcours-patrimoine-se-promener-a-andilly-andilly` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-desert-de-plate-passy` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-geologique-pointe-percee-grand-bornand` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-oiseaux-chatel` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-tournette-montmin` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `tour-du-mont-blanc-les-houches` | 2 | (no change) | — | kill col_chains (piéton/remontée — pas un col routier) |
| `secrets-fees-parcours-decouverte-habere-poche` | 3 | winter_infra | [raquettes, ski_fond] → **[raquettes]** | OT Alpes du Léman, fiche officielle 'Secrets de fées - parcours de découverte' (alpesduleman.com/secrets-de-fees-parcours-de-decouverte.html): "En hiver possibilité de faire les parcours en raquettes." (ski_fond non mentionné pour ce sentier — non retenu) |
| `pointe-de-miribel` | 3 | snow_view | ∅ → **mont_blanc** | OT Alpes du Léman, fiche officielle 'Randonnée : la Pointe de Miribel depuis Villard' (alpesduleman.com/randonnee-la-pointe-de-miribel-depuis-villard.html): "La pointe de Miribel, par temps clair, offre une vue fantastique sur le massif du Mont-Blanc." (vue lac Léman également citée, mais Mont-Blanc retenu comme panorama nommé prioritaire) |
| `tete-du-parmelan` | 3 | winter_access | ∅ → **open** | hautesavoiemontblanc-tourisme.com — Refuge du Parmelan (Dingy-Saint-Clair): 'Accès possible par sentier, à VTT et en hiver à raquettes et ski de randonnée'; hautesavoiemontblanc-tourisme.com — Boucle Parmelan/Villaz: 'panorama... with Mont Blanc in the background' |
| `tete-du-parmelan` | 3 | snow_view | ∅ → **mont_blanc** | hautesavoiemontblanc-tourisme.com — Refuge du Parmelan (Dingy-Saint-Clair): 'Accès possible par sentier, à VTT et en hiver à raquettes et ski de randonnée'; hautesavoiemontblanc-tourisme.com — Boucle Parmelan/Villaz: 'panorama... with Mont Blanc in the background' |
| `belvedere-du-mont-baron` | 3 | snow_view | ∅ → **alpes** | tourisme-haute-savoie.com — Les plus beaux points de vue sur le lac d'Annecy: 'Situé sur la crête entre le Mont Veyrier et le Mont Baron... il permet d'embrasser d'un seul regard toute la région annécienne, avec le lac en contrebas et les massifs alpins à perte de vue' |
| `pont-de-la-caille` | 3 | winter_access | ∅ → **open** | tourisme.fier-et-usses.com — Le Pont de la Caille Charles-Albert: 'Toute l'année : ouvert tous les jours'; haute-savoie-tourisme.org — Le Pont de la Caille Charles-Albert: 'ouvert tous les jours' and 'D'un côté les gorges des Usses et de l'autre un panorama grandiose sur une partie de la chaîne des Aravis' |
| `pont-de-la-caille` | 3 | snow_view | ∅ → **alpes** | tourisme.fier-et-usses.com — Le Pont de la Caille Charles-Albert: 'Toute l'année : ouvert tous les jours'; haute-savoie-tourisme.org — Le Pont de la Caille Charles-Albert: 'ouvert tous les jours' and 'D'un côté les gorges des Usses et de l'autre un panorama grandiose sur une partie de la chaîne des Aravis' |
| `sentier-decouverte-plateau-glieres-thorens-glieres` | 3 | winter_access | ∅ → **open** | tourism.tourisme-faucigny-glieres.fr — 'Snowshoeing and walking itinerary, history discovering Glières Val de Borne': seasonal listing '23/12 to 31/03', described as usable 'in your boots or with snow-shoes' |
| `marais-de-poisy` | 3 | winter_access | ∅ → **open** | en.lac-annecy.com — Marais de Poisy thematic walk: 'All year round daily. Subject to favorable weather.' |
| `parcours-marche-boucle-pedestre-uffin-neydens` | 3 | winter_access | ∅ → **open** | hautesavoiemontblanc-tourisme.com — Parcours de marche : Boucle pédestre d'Uffin (Neydens): 'Toute l'année' |
| `sentier-des-roselieres` | 3 | winter_access | ∅ → **open** | lac-annecy.com — Sentier des Roselières (Saint-Jorioz): 'Praticable toute l'année.' |
| `sentier-renard-morzine` | 3 | winter_infra | ∅ → **[raquettes]** | en.morzine-avoriaz.com/equipment/fox-trail/ (OT Morzine) — "In the winter this path can also be used for showshoeing [sic, snowshoeing]" |
| `aire-de-decollage-parapente-plaine-joux` | 3 | (no change) | — | haute-savoie-tourisme.org/loisirs/lieux-sportifs/sites-d-envol-et-d-atterissage/124385-aire-de-decollage-de-plaine-joux — 'un plateau plein sud, face au Mont-Blanc [...] conditions idéales pour la découverte et la pratique du vol libre' |
