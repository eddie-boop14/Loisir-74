# DATAtourisme null-fill - match report

"This feed fills official URLs, geo, and official classements. It cannot fill price, booking, or photo credits - absent from DATAtourisme. The completeness gap closed here is the factual-reference layer, not the commercial layer."

Source: `dt-ara-74-candidates.json` - 3012 leisure POIs (dept 74) - generated 2026-07-21

- **Strong** (fuzzy >=0.9 + commune exact + GPS <=150 m): **93** - **Weak** (suggested, never auto): **156**
- Proposed fills on strong matches: **official_site_url** 3 live (+1 dead skipped) - **geo** 0 - **classement** 0

---

## Strong matches with a proposed null-fill

| fiche | dt name | maj | fuzzy | dist | field -> value | check |
|---|---|---|---|---|---|---|
| `lac-vert-passy` | Lac Vert | 2025-10-29 | 1.00 | 144 m | official_site_url -> https://www.passy-mont-blanc.com/ | live 200/3xx |
| `plage-de-sciez-sur-leman` | Plage de Sciez-sur-Léman | 2026-02-03 | 1.00 | 78 m | official_site_url -> http://www.destination-leman.com/ | live 200/3xx |
| `parc-des-dronieres` | Le Parc des Dronières | 2026-04-11 | 1.00 | 0 m | official_site_url -> http://www.cruseilles.fr/<>http://www.montsdugen… | DEAD - skip |
| `lac-cornu` | Lac Cornu | 2022-11-30 | 1.00 | 93 m | official_site_url -> http://www.chamoniarde.com/ | live 200/3xx |

_dt_id provenance logged per fill on --apply._

---

## Weak (SUGGESTED - never auto-filled, Eddie reviews)

| fiche | dt name | commune | fuzzy | dt_id |
|---|---|---|---|---|
| `ecomusee-bois-foret-thones` | Ecomusée du Bois et de la Forêt | Thônes | 1.00 | 8f41a828-8a4 |
| `la-turbine-sciences-cran-gevrier` | La Turbine sciences | Annecy | 1.00 | e4d74081-03b |
| `telepherique-du-brevent` | Téléphérique du Brévent | Chamonix-Mont-Blanc | 1.00 | 7e86609f-500 |
| `chateau-ripaille-thonon` | Château de Ripaille | Thonon-les-Bains | 1.00 | 5a8e98d7-eb0 |
| `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy` | Le Parc des Jardins de Haute-Savoie | La Balme-de-Sillingy | 1.00 | 375600ed-a92 |
| `morillon` | Morillon | Morillon | 1.00 | 4f22325e-945 |
| `base-de-loisirs-des-ilettes` | Base de loisirs des Ilettes | Sallanches | 1.00 | fea3da2c-50c |
| `cinema-cine-leman-thonon` | Ciné Léman | Thonon-les-Bains | 1.00 | b01f0160-ec9 |
| `jardin-les-jardins-secrets-vaulx` | Jardins Secrets | Vaulx | 1.00 | 2df1c3a7-7bd |
| `jardin-jaysinia-samoens` | Jardin botanique alpin La Jaÿsinia | Samoëns | 1.00 | 64efa50b-450 |
| `telepherique-aiguille-du-midi` | Téléphérique de l'Aiguille du Midi | Chamonix-Mont-Blanc | 1.00 | 308f6c1c-86f |
| `ecomusee-peche-et-du-lac-thonon` | Ecomusée de la Pêche et du Lac | Thonon-les-Bains | 1.00 | d27dbec7-aab |
| `cascade-du-dard` | Cascade du Dard | Chamonix-Mont-Blanc | 1.00 | add08f92-7c0 |
| `chateau-et-donjon-des-seigneurs-de-faverges` | Le Donjon des Seigneurs de Faverges | Faverges-Seythenex | 1.00 | 3270685a-ecd |
| `grand-parc-d-andilly` | Le Grand Parc d'Andilly | Andilly | 1.00 | 0a07b0ef-c90 |
| `plage-de-la-pinede` | Plage de la Pinède | Thonon-les-Bains | 1.00 | a6790360-69e |
| `parc-animalier-grande-jeanne-annecy` | Parc animalier de la Grande Jeanne | Annecy | 1.00 | 0a04f9a0-209 |
| `les-aigles-du-leman` | Les Aigles du Léman | Sciez | 1.00 | a48c5bcd-087 |
| `piscine-jean-regis-annecy` | Piscine Jean Régis | Annecy | 1.00 | 8b2c1694-8f8 |
| `tramway-du-mont-blanc` | Tramway du Mont-Blanc | Saint-Gervais-les-Bains | 1.00 | 1b9ecd24-1ee |
| `filenvol-monnetier-mornex` | Filenvol | Monnetier-Mornex | 1.00 | 6e297bef-787 |
| `chateau-la-rochette-lully` | Château de La Rochette | Lully | 1.00 | 676662e9-1ec |
| `base-de-loisirs-du-lac-bleu` | Base de loisirs du Lac Bleu | Morillon | 1.00 | 1d4bcadb-769 |
| `plage-de-la-brune-veyrier` | Plage de La Brune | Veyrier-du-Lac | 1.00 | 763cb610-292 |
| `sentier-des-roselieres` | Sentier des Roselières | Saint-Jorioz | 1.00 | e1b694df-df1 |
| `plage-de-tougues-chens` | Plage de Tougues | Chens-sur-Léman | 1.00 | 5c673ba8-1d8 |
| `parc-des-dereches` | Parc des Dérêches | Morzine | 1.00 | 70463e22-0f4 |
| `via-ferrata-curalla-passy` | Via ferrata de Curalla | Passy | 1.00 | a112c763-993 |
| `telecabine-panoramic-mont-blanc` | Télécabine Panoramic Mont-Blanc | Chamonix-Mont-Blanc | 1.00 | b861749c-6da |
| `plage-albigny` | Plage d'Albigny | Annecy | 1.00 | a5d41057-01b |
| `plage-imperial-annecy` | Plage de l'Impérial | Annecy | 1.00 | 71adbbed-999 |
| `chateau-de-menthon-saint-bernard` | Château de Menthon-Saint-Bernard | Menthon-Saint-Bernard | 1.00 | bf54d185-2cd |
| `maison-de-la-pomme-biscantin-serraval` | Maison de la pomme et du biscantin | Serraval | 1.00 | a2a338d2-641 |
| `bowling-aerodrome-annemasse` | Bowling de l'aérodrome | Annemasse | 1.00 | 741ee3af-155 |
| `telecabine-pleney-morzine` | Télécabine du Pléney | Morzine | 1.00 | 8f7bbb16-ab3 |
| `gorges-du-pont-du-diable` | Les Gorges du Pont du Diable | La Vernaz | 1.00 | 02086ae7-d85 |
| `voie-verte-lac-annecy-annecy` | Voie Verte du Lac d'Annecy | Annecy | 1.00 | 3b12063a-1a8 |
| `chateau-clermont-genevois` | Château de Clermont | Clermont | 1.00 | ebd727df-d18 |
| `via-ferrata-parc-thermal-saint-gervais` | Via Ferrata du Parc Thermal | Saint-Gervais-les-Bains | 1.00 | ee17d741-9be |
| `cinema-cine-chateau-bonneville` | Ciné-Château | Bonneville | 1.00 | 7e8eb626-45f |
| `base-de-loisirs-orange-montisel-saint-sixt` | Base de loisirs Orange Montisel | Saint-Sixt | 1.00 | 7103eb17-86d |
| `laser-game-evolution-ville-la-grand` | Laser Game Evolution Annemasse | Ville-la-Grand | 1.00 | 1465ebb9-6e5 |
| `plage-d-excenevex` | Plage d'Excenevex | Excenevex | 1.00 | e3de8751-6bd |
| `base-nautique-marquisats-annecy` | Base nautique des Marquisats | Annecy | 1.00 | 0417c7f3-c2b |
| `marais-de-poisy` | Marais de Poisy | Poisy | 1.00 | 58089ea4-9c0 |
| `musee-du-mont-blanc-chamonix` | Le Mont Blanc | Chamonix-Mont-Blanc | 1.00 | 440fd543-0b4 |
| `lac-blanc` | Lac Blanc | Chamonix-Mont-Blanc | 1.00 | 1502fa32-fd1 |
| `chateau-chatillon-sur-cluses` | Châtillon sur Cluses | Châtillon-sur-Cluses | 1.00 | ca84f83a-5d7 |
| `gorges-du-fier` | Les Gorges du Fier | Lovagny | 1.00 | 463e088f-d23 |
| `cascade-de-nyon` | Cascade de Nyon | Morzine | 1.00 | 40676dd2-679 |
| `plage-de-messery` | Plage de Messery | Messery | 1.00 | 277f2636-c33 |
| `plage-du-lac-de-montriond` | Plage du lac de Montriond | Montriond | 1.00 | 8364f022-baa |
| `telecabine-du-mont-chery-les-gets` | Télécabine du Mont Chery Eté | Les Gets | 0.91 | e8251b3e-7b4 |
| `centre-nautique-guy-chatel-ayse` | Centre Nautique "Guy Châtel" de la CCF | Ayse | 0.91 | 1aa752cf-c2b |
| `cooperative-reblochon-le-farto-thones` | Coopérative du Reblochon Fermier | Thônes | 0.91 | 504004c6-6e8 |
| `jardin-pre-curieux-evian` | Les jardins de l'eau du Pré Curieux | Évian-les-Bains | 0.90 | 82ec29c4-d8e |
| `centre-aquatique-cluses` | Centre aquatique Intercommunal | Cluses | 0.90 | ddb38ecf-2da |
| `paintball-chamonix` | Paintball Cham | Chamonix-Mont-Blanc | 0.88 | baebb04c-c56 |
| `plage-de-talloires` | Village de Talloires | Talloires-Montmin | 0.88 | e61d45b9-c9d |
| `patinoire-richard-bozon-chamonix` | Patinoire R. Bozon | Chamonix-Mont-Blanc | 0.85 | 15c15707-c22 |
| `base-de-loisirs-du-lac-aux-dames` | Base de loisirs des Lacs aux Dames en  | Samoëns | 0.85 | 970d1e63-84f |
| `plage-du-lac-de-montriond` | Pêche au lac de Montriond | Montriond | 0.84 | 667c8c89-b9c |
| `padel-mont-blanc-padel-passy` | Mont-Blanc Padel | Passy | 0.84 | 1fda1e45-5d5 |
| `aire-de-decollage-parapente-plaine-joux` | Aire de décollage de Plaine-Joux | Passy | 0.84 | aed213ce-907 |
| `maison-de-la-memoire-janny-couttet-chamonix` | Maison de la Mémoire et du Patrimoine  | Chamonix-Mont-Blanc | 0.84 | e4875c6e-fc4 |
| `plage-de-menthon-saint-bernard` | Plage municipale de Menthon-Saint-Bern | Menthon-Saint-Bernard | 0.83 | 1c5d1996-f13 |
| `patinoire-richard-bozon-chamonix` | Piscine Richard Bozon | Chamonix-Mont-Blanc | 0.82 | 72ee26e2-b01 |
| `parc-animalier-grande-jeanne-annecy` | Falaise de la Grande Jeanne | Annecy | 0.82 | 252bd6c0-851 |
| `centre-aquatique-sallanches-mont-blanc` | Espace Bien-Être centre aquatique de S | Sallanches | 0.82 | 343c741b-724 |
| `chateau-montrottier-lovagny` | Golf de Montrottier | Lovagny | 0.81 | d306ed1b-1a2 |
| `base-de-loisirs-du-lac-aux-dames` | Base de loisirs des Lacs aux Dames en  | Samoëns | 0.81 | c0546a63-5f1 |
| `lac-des-dronieres` | Pêche au lac des Dronières | Cruseilles | 0.81 | e50159ed-3ff |
| `maison-de-barberine-vallorcine` | Canyon de Barberine | Vallorcine | 0.81 | afeae88d-cdb |
| `musee-cinema-philippe-piccot-douvaine` | Musée Philippe Piccot | Douvaine | 0.81 | 743582b1-519 |
| `escape-game-atelier-des-enigmes-annecy` | L'Atelier des Énigmes | Annecy | 0.81 | f9276f6b-d06 |
| `boucle-pedestre-detective-nature-jonzier-epagny` | Boucle pédestre : détective nature | Jonzier-Épagny | 0.81 | a6d91c7c-ef0 |
| `grotte-et-cascade-de-seythenex` | Tyrolienne de la cascade de Seythenex | Faverges-Seythenex | 0.81 | cd1bde83-817 |
| `cinema-pathe-archamps-imax` | Cinéma Pathé Archamps | Archamps | 0.80 | 8690b09e-926 |
| `espace-aquatique-morzine` | Espace Aquatique | Morzine | 0.80 | 15206f09-66a |
| `cinema-cine-actuel-studio6-annemasse` | Cinéma Studio 6 | Annemasse | 0.80 | 42ffd82e-0a7 |

_(+76 more weak suggestions omitted)_
