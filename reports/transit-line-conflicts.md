# Transit prose ↔ feed line-number conflicts

> Generated 2026-06-15 by scripts/build_transport_index.py · master to-do #5b.
> **Human review only — never auto-rewritten.** A script must not pick a winner
> between the curated prose and the operators' live GTFS feed.

46 fiche(s) whose curated how_to_get_there.public_transport prose cites a
bus/line number that the GTFS feed does **not** show on any stop within range
(1200 m). Either the prose is stale (line renumbered/rerouted) or the
feed's nearest stop simply isn't the one the prose means. Resolve by hand.

| Fiche | Prose lines | Feed lines nearby | Unconfirmed |
|---|---|---|---|
| abbaye-de-sixt | 95 | N-CMG, Y02, Y94 | 95 |
| acro-aventures-talloires | 61 | F1, F2 | 61 |
| alpine-coaster-les-planards-chamonix | 01, 14 | 01, 02, 03, 04, 21, N1 | 14 |
| aquariaz | 351 | Y91, Y92 | 351 |
| baignade-biotope-combloux | Y82, Y83 | Y83 | Y82 |
| bar-a-jeux-youri-bar-cran-gevrier | 5 | 2, 27 | 5 |
| base-de-loisirs-du-lac-bleu | 91 | N-CMG, Y02, Y94 | 91 |
| base-de-loisirs-du-vuaz-filliere | 81, 82 | 82 | 81 |
| cascade-aventure | 21 | N-BAB | 21 |
| cascade-de-la-belle-au-bois | 31 | Y82, Y83 | 31 |
| cascade-du-rouget | 6 | N-CMG, Y02, Y94 | 6 |
| chateau-clermont-genevois | 41 | Y13, Y22 | 41 |
| chateau-des-rubins-observatoire-des-alpes | 1 | Y81, Y83, Y84, Y85, Y86 | 1 |
| col-des-aravis | 1 | N-ARAVISBUS | 1 |
| ecomusee-peche-et-du-lac-thonon | 143 | Y03, Y91 | 143 |
| ereel-annecy-sillingy | 7 | 10, 24, 30 | 7 |
| escalade-cortigrimpe-metz-tessy | 6 | 21, 25 | 6 |
| escape-game-break-out-sevrier | 11 | 15, Y51 | 11 |
| espace-aquatique-la-clusaz | 1 | N-ARAVISBUS | 1 |
| fonderie-paccard-sevrier | 51 | 15 | 51 |
| golf-practice-belvedere-saint-martin-bellevue | 16 | 80 | 16 |
| ile-de-tortuga-vetraz-monthoux | 1 | 5, 8 | 1 |
| k2-parapente-doussard | 51 | Y51 | 51 |
| la-turbine-sciences-cran-gevrier | 5 | 12 | 5 |
| lac-des-confins | 61 | N-ARAVISBUS | 61 |
| leman-kid-thonon-les-bains | L2 | Y03, Y91 | L2 |
| mont-baron | 1, 20 | 20, 26, Y62 | 1 |
| mont-veyrier | 20 | 82, Y63 | 20 |
| musee-archeologique-viuz-faverges | 51 | Y51 | 51 |
| musee-chateau-annecy | 4 | 13, 15, 26, 27, S4, Y51 | 4 |
| musee-du-batiment-ville-la-grand | 4 | 6, 7, TANGO | 4 |
| museum-des-papillons-et-insectes-faverges | 51 | Y51 | 51 |
| palais-de-l-ile-annecy | 4 | 13, 15, 26, 27, S4, Y51 | 4 |
| parc-de-loisirs-du-pontet | 71 | Y84 | 71 |
| parc-des-dereches | 31, 32 | N-BAB, Y91, Y92 | 31, 32 |
| passy-accro-lac | 82, 83 | Y85 | 82, 83 |
| patinoire-la-clusaz | 62 | N-ARAVISBUS | 62 |
| plage-albigny | 2 | 13, 26, 5, Y62 | 2 |
| plage-de-la-pinede | 1 | Y03, Y91 | 1 |
| plage-des-marquisats | 15AB, 6 | 13, 15, 27, S4, Y51 | 15AB, 6 |
| telecabine-des-chavannes-les-gets | 60 | N-BAB, Y91, Y92 | 60 |
| telecabine-du-jaillet | 1 | Y82, Y83 | 1 |
| telecabine-du-mont-chery-les-gets | 60 | Y92 | 60 |
| telepherique-du-saleve | 4, 8 | 4 | 8 |
| via-ferrata-pollet-villard-la-clusaz | 61 | N-ARAVISBUS | 61 |
| vitam-neydens | 272, L1 | 4 | 272, L1 |

