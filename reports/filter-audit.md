# Filter audit STEP 1 — read-only

## Methodology

For each of 14 hubs with filters, extracted: filter select options, data source the JS reads at filter time, and compared with DOM data attrs + JSON fiche fields.

## Result table

| HUB | FILTER | OPT VAL | OPT LABEL | SOURCE | STATUS | COUNT |
|---|---|---|---|---|---|---|
| `baignade-nautisme` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 3 |
| `baignade-nautisme` | `filt-commune` | `Annemasse` | Annemasse | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Arenthon` | Arenthon | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Ayse` | Ayse | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Châtel` | Châtel | sec.dataset.commune | FAIL: no JSON match | 0 |
| `baignade-nautisme` | `filt-commune` | `Cluses` | Cluses | sec.dataset.commune | OK | 2 |
| `baignade-nautisme` | `filt-commune` | `Combloux` | Combloux | sec.dataset.commune | FAIL: no JSON match | 0 |
| `baignade-nautisme` | `filt-commune` | `Doussard` | Doussard | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `La Clusaz` | La Clusaz | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Publier` | Publier | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Saint-Jorioz` | Saint-Jorioz | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Sciez` | Sciez | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Seynod` | Seynod | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 3 |
| `baignade-nautisme` | `filt-commune` | `Yvoire` | Yvoire | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | OK | 1 |
| `baignade-nautisme` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=23 JSON_paid=21 |
| `baignade-nautisme` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | FAIL: no gratuit tag | DOM_free=0 JSON_free=0 |
| `baignade-nautisme` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=1 JSON_seasonal=1 |
| `bases-de-loisirs` | `filt-commune` | `Andilly` | Andilly | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 3 |
| `bases-de-loisirs` | `filt-commune` | `Arenthon` | Arenthon | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Arâches-la-Frasse` | Arâches-la-Frasse | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Bellevaux` | Bellevaux | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Cervens` | Cervens | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Châtel` | Châtel | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Cruseilles` | Cruseilles | sec.dataset.commune | OK | 2 |
| `bases-de-loisirs` | `filt-commune` | `Doussard` | Doussard | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Fillière` | Fillière | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `La Balme-de-Sillingy` | La Balme-de-Sillingy | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `La Chapelle-d'Abondance` | La Chapelle-d'Abondanc | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `La Clusaz` | La Clusaz | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Le Grand-Bornand` | Le Grand-Bornand | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Les Contamines-Montjoie` | Les Contamines-Montjoi | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Les Gets` | Les Gets | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Magland` | Magland | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Manigod` | Manigod | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Megève` | Megève | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Monnetier-Mornex` | Monnetier-Mornex | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Morillon` | Morillon | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Neydens` | Neydens | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Perrignier` | Perrignier | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Présilly` | Présilly | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Reignier-Ésery` | Reignier-Ésery | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Gingolph` | Saint-Gingolph | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Jean-de-Sixt` | Saint-Jean-de-Sixt | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Jorioz` | Saint-Jorioz | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Paul-en-Chablais` | Saint-Paul-en-Chablais | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Saint-Sixt` | Saint-Sixt | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Samoëns` | Samoëns | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Sciez` | Sciez | sec.dataset.commune | OK | 2 |
| `bases-de-loisirs` | `filt-commune` | `Sillingy` | Sillingy | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Sixt-Fer-à-Cheval` | Sixt-Fer-à-Cheval | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Talloires-Montmin` | Talloires-Montmin | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 4 |
| `bases-de-loisirs` | `filt-commune` | `Thônes` | Thônes | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Vallorcine` | Vallorcine | sec.dataset.commune | FAIL: no JSON match | 0 |
| `bases-de-loisirs` | `filt-commune` | `Ville-la-Grand` | Ville-la-Grand | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Viry` | Viry | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Vétraz-Monthoux` | Vétraz-Monthoux | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Yvoire` | Yvoire | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | OK | 1 |
| `bases-de-loisirs` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=53 JSON_paid=24 |
| `bases-de-loisirs` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=20 JSON_free=16 |
| `bases-de-loisirs` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=12 JSON_seasonal=7 |
| `cascades` | `filt-commune` | `Bellevaux` | Bellevaux | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Faverges-Seythenex` | Faverges-Seythenex | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Le Grand-Bornand` | Le Grand-Bornand | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Lovagny` | Lovagny | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Megève` | Megève | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Montriond` | Montriond | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 3 |
| `cascades` | `filt-commune` | `Servoz` | Servoz | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-commune` | `Sixt-Fer-à-Cheval` | Sixt-Fer-à-Cheval | sec.dataset.commune | OK | 2 |
| `cascades` | `filt-commune` | `Talloires-Montmin` | Talloires-Montmin | sec.dataset.commune | OK | 1 |
| `cascades` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=2 JSON_paid=3 |
| `cascades` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=13 JSON_free=13 |
| `cascades` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=1 JSON_seasonal=1 |
| `chateaux` | `filt-commune` | `Allinges` | Allinges | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | FAIL: no JSON match | 0 |
| `chateaux` | `filt-commune` | `Bonneville` | Bonneville | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Brenthonne` | Brenthonne | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Châtillon-sur-Cluses` | Châtillon-sur-Cluses | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Clermont` | Clermont | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Faverges-Seythenex` | Faverges-Seythenex | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Fillière` | Fillière | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Lovagny` | Lovagny | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Lully` | Lully | sec.dataset.commune | OK | 2 |
| `chateaux` | `filt-commune` | `Menthon-Saint-Bernard` | Menthon-Saint-Bernard | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Reignier-Ésery` | Reignier-Ésery | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Saint-Jean-d'Aulps` | Saint-Jean-d'Aulps | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Saint-Jeoire` | Saint-Jeoire | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Sixt-Fer-à-Cheval` | Sixt-Fer-à-Cheval | sec.dataset.commune | OK | 1 |
| `chateaux` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 4 |
| `chateaux` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=7 JSON_paid=11 |
| `chateaux` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=10 JSON_free=10 |
| `chateaux` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=9 JSON_seasonal=8 |
| `lacs-plages` | `filt-lac` | `annecy` | Lac d'Annecy | sec.dataset.lac (DOM has: EMPTY) | FAIL: NO data-lac in DOM | 0 |
| `lacs-plages` | `filt-lac` | `leman` | Lac Léman | sec.dataset.lac (DOM has: EMPTY) | FAIL: NO data-lac in DOM | 0 |
| `lacs-plages` | `filt-lac` | `petits` | Petits lacs de montagn | sec.dataset.lac (DOM has: EMPTY) | FAIL: NO data-lac in DOM | 0 |
| `lacs-plages` | `filt-access` | `paid` | Payant | paidOf[slug] from PINS | FAIL: PINS all paid=false | PINS_paid=0 JSON_paid=4 |
| `lacs-plages` | `filt-access` | `free` | Gratuit | paidOf[slug] from PINS | OK | PINS_free=20 JSON_free=27 |
| `lacs-plages` | `filt-access` | `seasonal` | - | paidOf[slug] from PINS | FAIL: not in PINS | JSON_seasonal=8 |
| `musees` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 4 |
| `musees` | `filt-commune` | `Annemasse` | Annemasse | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 3 |
| `musees` | `filt-commune` | `Faverges-Seythenex` | Faverges-Seythenex | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Les Houches` | Les Houches | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Présilly` | Présilly | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Sciez` | Sciez | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Servoz` | Servoz | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Sevrier` | Sevrier | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Thônes` | Thônes | sec.dataset.commune | OK | 2 |
| `musees` | `filt-commune` | `Vallorcine` | Vallorcine | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Ville-la-Grand` | Ville-la-Grand | sec.dataset.commune | OK | 1 |
| `musees` | `filt-commune` | `Viuz-en-Sallaz` | Viuz-en-Sallaz | sec.dataset.commune | OK | 3 |
| `musees` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | OK | 2 |
| `musees` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=15 JSON_paid=29 |
| `musees` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=10 JSON_free=12 |
| `musees` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=25 JSON_seasonal=25 |
| `parcs-jardins` | `filt-commune` | `Andilly` | Andilly | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 2 |
| `parcs-jardins` | `filt-commune` | `Bellevaux` | Bellevaux | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `La Balme-de-Sillingy` | La Balme-de-Sillingy | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Les Houches` | Les Houches | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Monnetier-Mornex` | Monnetier-Mornex | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Neydens` | Neydens | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Rumilly` | Rumilly | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Saint-Gingolph` | Saint-Gingolph | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Saint-Jorioz` | Saint-Jorioz | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Samoëns` | Samoëns | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Sciez` | Sciez | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Sillingy` | Sillingy | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Vallorcine` | Vallorcine | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Vaulx` | Vaulx | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Ville-la-Grand` | Ville-la-Grand | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Viry` | Viry | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Vétraz-Monthoux` | Vétraz-Monthoux | sec.dataset.commune | OK | 1 |
| `parcs-jardins` | `filt-commune` | `Yvoire` | Yvoire | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | FAIL: no JSON match | 0 |
| `parcs-jardins` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=15 JSON_paid=11 |
| `parcs-jardins` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=9 JSON_free=6 |
| `parcs-jardins` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=7 JSON_seasonal=6 |
| `points-de-vue` | `filt-commune` | `Abondance` | Abondance | sec.dataset.commune | FAIL: no JSON match | 0 |
| `points-de-vue` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 2 |
| `points-de-vue` | `filt-commune` | `Brizon` | Brizon | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 3 |
| `points-de-vue` | `filt-commune` | `Collonges-sous-Salève` | Collonges-sous-Salève | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Cruseilles` | Cruseilles | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Dingy-Saint-Clair` | Dingy-Saint-Clair | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Doussard` | Doussard | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Fillière` | Fillière | sec.dataset.commune | OK | 2 |
| `points-de-vue` | `filt-commune` | `La Clusaz` | La Clusaz | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Le Reposoir` | Le Reposoir | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Manigod` | Manigod | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Monnetier-Mornex` | Monnetier-Mornex | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Poisy` | Poisy | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Publier` | Publier | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Saint-Jorioz` | Saint-Jorioz | sec.dataset.commune | FAIL: no JSON match | 0 |
| `points-de-vue` | `filt-commune` | `Talloires-Montmin` | Talloires-Montmin | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Taninges` | Taninges | sec.dataset.commune | FAIL: no DOM section | 0 |
| `points-de-vue` | `filt-commune` | `Veyrier-du-Lac` | Veyrier-du-Lac | sec.dataset.commune | OK | 2 |
| `points-de-vue` | `filt-commune` | `Villard` | Villard | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Viuz-la-Chiésaz` | Viuz-la-Chiésaz | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-commune` | `Étrembières` | Étrembières | sec.dataset.commune | OK | 1 |
| `points-de-vue` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=5 JSON_paid=5 |
| `points-de-vue` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=23 JSON_free=22 |
| `points-de-vue` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=1 JSON_seasonal=1 |
| `sensations-plein-air` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 4 |
| `sensations-plein-air` | `filt-commune` | `Arâches-la-Frasse` | Arâches-la-Frasse | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Bellevaux` | Bellevaux | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Cervens` | Cervens | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `Châtel` | Châtel | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Doussard` | Doussard | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `La Chapelle-d'Abondance` | La Chapelle-d'Abondanc | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `La Clusaz` | La Clusaz | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `Le Grand-Bornand` | Le Grand-Bornand | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `Les Gets` | Les Gets | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Magland` | Magland | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Manigod` | Manigod | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `Megève` | Megève | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 4 |
| `sensations-plein-air` | `filt-commune` | `Présilly` | Présilly | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Reignier-Ésery` | Reignier-Ésery | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | OK | 3 |
| `sensations-plein-air` | `filt-commune` | `Saint-Jean-de-Sixt` | Saint-Jean-de-Sixt | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Saint-Paul-en-Chablais` | Saint-Paul-en-Chablais | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Samoëns` | Samoëns | sec.dataset.commune | OK | 2 |
| `sensations-plein-air` | `filt-commune` | `Sciez` | Sciez | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Sixt-Fer-à-Cheval` | Sixt-Fer-à-Cheval | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Talloires-Montmin` | Talloires-Montmin | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Thônes` | Thônes | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Vallorcine` | Vallorcine | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | OK | 1 |
| `sensations-plein-air` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=33 JSON_paid=34 |
| `sensations-plein-air` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=5 JSON_free=9 |
| `sensations-plein-air` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=5 JSON_seasonal=5 |
| `sentiers` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Cruseilles` | Cruseilles | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Doussard` | Doussard | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Les Houches` | Les Houches | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Présilly` | Présilly | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Saint-Gingolph` | Saint-Gingolph | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Saint-Jorioz` | Saint-Jorioz | sec.dataset.commune | OK | 2 |
| `sentiers` | `filt-commune` | `Saint-Pierre-en-Faucigny` | Saint-Pierre-en-Faucig | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Sixt-Fer-à-Cheval` | Sixt-Fer-à-Cheval | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Talloires-Montmin` | Talloires-Montmin | sec.dataset.commune | OK | 1 |
| `sentiers` | `filt-commune` | `Thorens-Glières` | Thorens-Glières | sec.dataset.commune | OK | 2 |
| `sentiers` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=2 JSON_paid=1 |
| `sentiers` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=34 JSON_free=36 |
| `sentiers` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=4 JSON_seasonal=4 |
| `sorties-detente` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 4 |
| `sorties-detente` | `filt-commune` | `Annemasse` | Annemasse | sec.dataset.commune | OK | 2 |
| `sorties-detente` | `filt-commune` | `Archamps` | Archamps | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-commune` | `Bonneville` | Bonneville | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-commune` | `La Roche-sur-Foron` | La Roche-sur-Foron | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-commune` | `Neydens` | Neydens | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sorties-detente` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sorties-detente` | `filt-commune` | `Sallanches` | Sallanches | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | OK | 2 |
| `sorties-detente` | `filt-commune` | `Thônes` | Thônes | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sorties-detente` | `filt-commune` | `Évian-les-Bains` | Évian-les-Bains | sec.dataset.commune | OK | 1 |
| `sorties-detente` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=17 JSON_paid=13 |
| `sorties-detente` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=1 JSON_free=1 |
| `sorties-detente` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=4 JSON_seasonal=4 |
| `sport-jeux` | `filt-commune` | `Allinges` | Allinges | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 3 |
| `sport-jeux` | `filt-commune` | `Annemasse` | Annemasse | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Anthy-sur-Léman` | Anthy-sur-Léman | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Argonay` | Argonay | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Fillinges` | Fillinges | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `La Clusaz` | La Clusaz | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `La Roche-sur-Foron` | La Roche-sur-Foron | sec.dataset.commune | OK | 2 |
| `sport-jeux` | `filt-commune` | `Le Grand-Bornand` | Le Grand-Bornand | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Margencel` | Margencel | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Marnaz` | Marnaz | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Megève` | Megève | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Metz-Tessy` | Metz-Tessy | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Neydens` | Neydens | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Passy` | Passy | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Perrignier` | Perrignier | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Poisy` | Poisy | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Publier` | Publier | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Rumilly` | Rumilly | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Saint-Martin-Bellevue` | Saint-Martin-Bellevue | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Scientrier` | Scientrier | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Sevrier` | Sevrier | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Sillingy` | Sillingy | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Sévrier` | Sévrier | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Thônes` | Thônes | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Ville-la-Grand` | Ville-la-Grand | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-commune` | `Viry` | Viry | sec.dataset.commune | OK | 1 |
| `sport-jeux` | `filt-commune` | `Vétraz-Monthoux` | Vétraz-Monthoux | sec.dataset.commune | FAIL: no JSON match | 0 |
| `sport-jeux` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=52 JSON_paid=17 |
| `sport-jeux` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | FAIL: no gratuit tag | DOM_free=0 JSON_free=0 |
| `sport-jeux` | `filt-access` | `seasonal` | Selon saison | .card-tag.is-seasonal DOM | OK (patched JS) | DOM_seasonal=1 JSON_seasonal=0 |
| `telecabines` | `filt-commune` | `Chamonix-Mont-Blanc` | Chamonix-Mont-Blanc | sec.dataset.commune | OK | 2 |
| `telecabines` | `filt-commune` | `Châtel` | Châtel | sec.dataset.commune | OK | 1 |
| `telecabines` | `filt-commune` | `Les Gets` | Les Gets | sec.dataset.commune | OK | 2 |
| `telecabines` | `filt-commune` | `Megève` | Megève | sec.dataset.commune | OK | 1 |
| `telecabines` | `filt-commune` | `Morzine` | Morzine | sec.dataset.commune | OK | 1 |
| `telecabines` | `filt-commune` | `Saint-Gervais-les-Bains` | Saint-Gervais-les-Bain | sec.dataset.commune | OK | 1 |
| `telecabines` | `filt-commune` | `Étrembières` | Étrembières | sec.dataset.commune | FAIL: no JSON match | 0 |
| `telecabines` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | OK | DOM_paid=12 JSON_paid=8 |
| `telecabines` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | FAIL: no gratuit tag | DOM_free=0 JSON_free=0 |
| `voies-vertes` | `filt-commune` | `Abondance` | Abondance | sec.dataset.commune | OK | 1 |
| `voies-vertes` | `filt-commune` | `Annecy` | Annecy | sec.dataset.commune | OK | 1 |
| `voies-vertes` | `filt-commune` | `Cluses` | Cluses | sec.dataset.commune | OK | 2 |
| `voies-vertes` | `filt-commune` | `Saint-Gingolph` | Saint-Gingolph | sec.dataset.commune | OK | 1 |
| `voies-vertes` | `filt-commune` | `Thonon-les-Bains` | Thonon-les-Bains | sec.dataset.commune | FAIL: no DOM section | 0 |
| `voies-vertes` | `filt-access` | `paid` | Payant | .card-tag.is-payant DOM | FAIL: no payant tag | DOM_paid=0 JSON_paid=0 |
| `voies-vertes` | `filt-access` | `free` | Gratuit | .card-tag.is-gratuit DOM | OK | DOM_free=5 JSON_free=5 |

## Broken filters

### baignade-nautisme (3 broken)

- `filt-commune` / `Châtel` (Châtel) — **FAIL: no JSON match** (0)
- `filt-commune` / `Combloux` (Combloux) — **FAIL: no JSON match** (0)
- `filt-access` / `free` (Gratuit) — **FAIL: no gratuit tag** (DOM_free=0 JSON_free=0)

### bases-de-loisirs (17 broken)

- `filt-commune` / `Arâches-la-Frasse` (Arâches-la-Frasse) — **FAIL: no JSON match** (0)
- `filt-commune` / `Cervens` (Cervens) — **FAIL: no JSON match** (0)
- `filt-commune` / `Chamonix-Mont-Blanc` (Chamonix-Mont-Blanc) — **FAIL: no JSON match** (0)
- `filt-commune` / `La Chapelle-d'Abondance` (La Chapelle-d'Abondanc) — **FAIL: no JSON match** (0)
- `filt-commune` / `La Clusaz` (La Clusaz) — **FAIL: no JSON match** (0)
- `filt-commune` / `Le Grand-Bornand` (Le Grand-Bornand) — **FAIL: no JSON match** (0)
- `filt-commune` / `Les Gets` (Les Gets) — **FAIL: no JSON match** (0)
- `filt-commune` / `Magland` (Magland) — **FAIL: no JSON match** (0)
- `filt-commune` / `Megève` (Megève) — **FAIL: no JSON match** (0)
- `filt-commune` / `Perrignier` (Perrignier) — **FAIL: no JSON match** (0)
- `filt-commune` / `Présilly` (Présilly) — **FAIL: no JSON match** (0)
- `filt-commune` / `Reignier-Ésery` (Reignier-Ésery) — **FAIL: no JSON match** (0)
- `filt-commune` / `Saint-Jean-de-Sixt` (Saint-Jean-de-Sixt) — **FAIL: no JSON match** (0)
- `filt-commune` / `Sixt-Fer-à-Cheval` (Sixt-Fer-à-Cheval) — **FAIL: no JSON match** (0)
- `filt-commune` / `Talloires-Montmin` (Talloires-Montmin) — **FAIL: no JSON match** (0)
- `filt-commune` / `Thônes` (Thônes) — **FAIL: no JSON match** (0)
- `filt-commune` / `Vallorcine` (Vallorcine) — **FAIL: no JSON match** (0)

### chateaux (1 broken)

- `filt-commune` / `Annecy` (Annecy) — **FAIL: no JSON match** (0)

### lacs-plages (5 broken)

- `filt-lac` / `annecy` (Lac d'Annecy) — **FAIL: NO data-lac in DOM** (0)
- `filt-lac` / `leman` (Lac Léman) — **FAIL: NO data-lac in DOM** (0)
- `filt-lac` / `petits` (Petits lacs de montagn) — **FAIL: NO data-lac in DOM** (0)
- `filt-access` / `paid` (Payant) — **FAIL: PINS all paid=false** (PINS_paid=0 JSON_paid=4)
- `filt-access` / `seasonal` (-) — **FAIL: not in PINS** (JSON_seasonal=8)

### parcs-jardins (9 broken)

- `filt-commune` / `La Balme-de-Sillingy` (La Balme-de-Sillingy) — **FAIL: no JSON match** (0)
- `filt-commune` / `Les Houches` (Les Houches) — **FAIL: no JSON match** (0)
- `filt-commune` / `Rumilly` (Rumilly) — **FAIL: no JSON match** (0)
- `filt-commune` / `Saint-Jorioz` (Saint-Jorioz) — **FAIL: no JSON match** (0)
- `filt-commune` / `Sciez` (Sciez) — **FAIL: no JSON match** (0)
- `filt-commune` / `Vallorcine` (Vallorcine) — **FAIL: no JSON match** (0)
- `filt-commune` / `Vaulx` (Vaulx) — **FAIL: no JSON match** (0)
- `filt-commune` / `Yvoire` (Yvoire) — **FAIL: no JSON match** (0)
- `filt-commune` / `Évian-les-Bains` (Évian-les-Bains) — **FAIL: no JSON match** (0)

### points-de-vue (3 broken)

- `filt-commune` / `Abondance` (Abondance) — **FAIL: no JSON match** (0)
- `filt-commune` / `Saint-Jorioz` (Saint-Jorioz) — **FAIL: no JSON match** (0)
- `filt-commune` / `Taninges` (Taninges) — **FAIL: no DOM section** (0)

### sorties-detente (3 broken)

- `filt-commune` / `Neydens` (Neydens) — **FAIL: no JSON match** (0)
- `filt-commune` / `Saint-Gervais-les-Bains` (Saint-Gervais-les-Bain) — **FAIL: no JSON match** (0)
- `filt-commune` / `Thônes` (Thônes) — **FAIL: no JSON match** (0)

### sport-jeux (18 broken)

- `filt-commune` / `Allinges` (Allinges) — **FAIL: no JSON match** (0)
- `filt-commune` / `Anthy-sur-Léman` (Anthy-sur-Léman) — **FAIL: no JSON match** (0)
- `filt-commune` / `Argonay` (Argonay) — **FAIL: no JSON match** (0)
- `filt-commune` / `Fillinges` (Fillinges) — **FAIL: no JSON match** (0)
- `filt-commune` / `Le Grand-Bornand` (Le Grand-Bornand) — **FAIL: no JSON match** (0)
- `filt-commune` / `Marnaz` (Marnaz) — **FAIL: no JSON match** (0)
- `filt-commune` / `Metz-Tessy` (Metz-Tessy) — **FAIL: no JSON match** (0)
- `filt-commune` / `Neydens` (Neydens) — **FAIL: no JSON match** (0)
- `filt-commune` / `Perrignier` (Perrignier) — **FAIL: no JSON match** (0)
- `filt-commune` / `Poisy` (Poisy) — **FAIL: no JSON match** (0)
- `filt-commune` / `Publier` (Publier) — **FAIL: no JSON match** (0)
- `filt-commune` / `Saint-Martin-Bellevue` (Saint-Martin-Bellevue) — **FAIL: no JSON match** (0)
- `filt-commune` / `Sillingy` (Sillingy) — **FAIL: no JSON match** (0)
- `filt-commune` / `Sévrier` (Sévrier) — **FAIL: no JSON match** (0)
- `filt-commune` / `Thonon-les-Bains` (Thonon-les-Bains) — **FAIL: no JSON match** (0)
- `filt-commune` / `Ville-la-Grand` (Ville-la-Grand) — **FAIL: no JSON match** (0)
- `filt-commune` / `Vétraz-Monthoux` (Vétraz-Monthoux) — **FAIL: no JSON match** (0)
- `filt-access` / `free` (Gratuit) — **FAIL: no gratuit tag** (DOM_free=0 JSON_free=0)

### telecabines (2 broken)

- `filt-commune` / `Étrembières` (Étrembières) — **FAIL: no JSON match** (0)
- `filt-access` / `free` (Gratuit) — **FAIL: no gratuit tag** (DOM_free=0 JSON_free=0)

### voies-vertes (2 broken)

- `filt-commune` / `Thonon-les-Bains` (Thonon-les-Bains) — **FAIL: no DOM section** (0)
- `filt-access` / `paid` (Payant) — **FAIL: no payant tag** (DOM_paid=0 JSON_paid=0)
