# Winter facts — APPLY report (JOB B)
Payload: `data/winter-facts-verified.json` · generated 2026-07-16
- Winter nodes touched: **33** · with real changes: **24** · category/vocab skips: **0**

---

## ⚑ SENSITIVE — Eddie sign-off required (access = closed / partial)
These are the highest-stakes lines on the site. Nothing below ships until you approve.

| slug | field | old → new | source |
|---|---|---|---|
| `cirque-du-fer-a-cheval` | winter_infra | [raquettes, ski_nordique] → **[ski_fond, ski_nordique, raquettes]** | Mairie Sixt/valleeduhautgiffre: ouverture partielle, domaine nordique (boucle 11 km); table d'orientation sur site: château de glace |

---

## CONFIRM-grade rows (official sourcing; apply with the batch)

| slug | stage | field | old → new | source |
|---|---|---|---|---|
| `train-du-montenvers-mer-de-glace` | 1 | winter_access | ∅ → **open** | CDM: service hivernal; montenverstrain.com: « Le Mont Blanc n'est pas visible depuis Montenvers » → alpes (Drus/Grandes Jorasses) |
| `train-du-montenvers-mer-de-glace` | 1 | col_chains | ∅ → **False** | CDM: service hivernal; montenverstrain.com: « Le Mont Blanc n'est pas visible depuis Montenvers » → alpes (Drus/Grandes Jorasses) |
| `col-des-aravis` | 1 | winter_access | ∅ → **open** | OT Thônes/Combloux: col maintenu ouvert (fermetures rares), vue Mont-Blanc documentée |
| `col-de-la-croix-fry` | 1 | winter_access | ∅ → **open** | OT Manigod/Thônes + skidefondbeauregard.com (36 km, face au Mont-Blanc) |
| `col-de-la-croix-fry` | 1 | winter_infra | [ski_fond] → **[ski_fond, ski_nordique, raquettes]** | OT Manigod/Thônes + skidefondbeauregard.com (36 km, face au Mont-Blanc) |
| `plateau-des-glieres` | 1 | winter_access | ∅ → **open** | plateaudesglieres.fr/domainenordiquedesglieres.com: RD55 équipements obligatoires, domaine 29 km — route traversante piétonne l'hiver; accès conditionnel météo (inforoute74) |
| `plateau-des-glieres` | 1 | winter_infra | [raquettes, ski_nordique, ski_fond, chiens_traineau, luge] → **[ski_fond, ski_nordique, raquettes, chiens_traineau, luge]** | plateaudesglieres.fr/domainenordiquedesglieres.com: RD55 équipements obligatoires, domaine 29 km — route traversante piétonne l'hiver; accès conditionnel météo (inforoute74) |
| `col-des-glieres` | 1 | winter_access | ∅ → **open** | idem plateau — même régime RD55 |
| `col-des-glieres` | 1 | snow_view | ∅ → **alpes** | idem plateau — même régime RD55 |
| `col-de-la-forclaz` | 1 | (no change) | — | RD42 col réel; pas de régime de fermeture saisonnier documenté (incidents ponctuels) → access null + lien inforoute74 |
| `le-semnoz` | 1 | winter_access | ∅ → **open** | OT/haute-savoie-tourisme: table d'orientation Crêt de Châtillon nomme le Mont-Blanc; station ouverte l'hiver (D41) |
| `le-semnoz` | 1 | winter_infra | [raquettes, ski_fond, luge] → **[ski_fond, ski_nordique, ski_rando, raquettes, luge]** | OT/haute-savoie-tourisme: table d'orientation Crêt de Châtillon nomme le Mont-Blanc; station ouverte l'hiver (D41) |
| `le-semnoz` | 1 | col_chains | ∅ → **False** | OT/haute-savoie-tourisme: table d'orientation Crêt de Châtillon nomme le Mont-Blanc; station ouverte l'hiver (D41) |
| `mont-saleve` | 1 | (no change) | — | telepherique-du-saleve.com + OT Monts du Genevois (itinéraires raquettes) |
| `telepherique-du-saleve` | 1 | (no change) | — | telepherique-du-saleve.com: « views as far as Mont Blanc » |
| `telepherique-aiguille-du-midi` | 1 | winter_access | ∅ → **open** | CDM/OT Chamonix — exploitation hivernale, terrasse sommitale face au Mont-Blanc |
| `tramway-du-mont-blanc` | 1 | winter_access | ∅ → **open** | CDM: service hivernal vers Bellevue; OT Saint-Gervais: plateau ouvert sur le massif du Mont-Blanc |
| `tramway-du-mont-blanc` | 1 | col_chains | ∅ → **False** | CDM: service hivernal vers Bellevue; OT Saint-Gervais: plateau ouvert sur le massif du Mont-Blanc |
| `belvedere-panorama-360-combloux-la-cry` | 1 | (no change) | — | OT Combloux: table d'orientation de la Cry, chaîne du Mont-Blanc nommée |
| `plateau-de-solaison` | 2 | winter_access | ∅ → **open** | Mairie Brison/Haute-Savoie Nordic (17–24 km + biathlon); panorama Bornes/Arve → alpes |
| `plateau-de-solaison` | 2 | winter_infra | [raquettes, ski_nordique, ski_fond, ski_rando, luge] → **[ski_fond, ski_nordique, raquettes, luge]** | Mairie Brison/Haute-Savoie Nordic (17–24 km + biathlon); panorama Bornes/Arve → alpes |
| `sentier-espagnols-pas-du-roc-glieres` | 2 | snow_view | ∅ → **alpes** | régime Glières — panorama Aravis/Bornes |
| `mont-joly` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `col-des-pitons-saleve` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `mont-baron` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `telecabine-du-jaillet` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `cascade-des-fours` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `gr96-bornes-aravis-haute-savoie` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `grp-tour-lac-annecy-annecy` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `parcours-patrimoine-se-promener-a-andilly-andilly` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-desert-de-plate-passy` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-geologique-pointe-percee-grand-bornand` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-oiseaux-chatel` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `sentier-tournette-montmin` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
| `tour-du-mont-blanc-les-houches` | 2 | col_chains | ∅ → **False** | kill col_chains (piéton/remontée — pas un col routier) |
