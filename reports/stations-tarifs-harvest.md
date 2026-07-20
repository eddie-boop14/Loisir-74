# Tarifs stations — harvest report (PART 1)
Payload: `data/station-tarifs-harvest.json` · generated 2026-07-20
- Stations in payload: **28** — grille 2026-27: **5** · grille 2025-26 (préfixée): **23** · rien publié (prose automne): **0**
- PENDING (à appliquer): **28** · APPLIED (déjà en ligne): **0** · rows refused/skipped: **0**

États par ligne : `∅ → value` = en attente d'apply · `= value (appliqué)` = déjà dans la fiche (post-apply). Un rapport où tout est APPLIED est un état des lieux, pas un no-op. Aucun prix n'est écrit sans source officielle + citation dans le payload.

---

## Grille 2026-27 publiée

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| `chatel` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.skipass-chatel.com/fr/tarifs-hiver |
| `chatel` | APPLIED | price_from | = **41.0** | pl,ja,ar,he | https://www.skipass-chatel.com/fr/tarifs-hiver |
| `chatel` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.skipass-chatel.com/fr/tarifs-hiver |
| `la-chapelle-d-abondance` | APPLIED | price_tiers | = **[5 tiers]** | pl,ja,ar,he | https://skipass.lachapelle74.com/fr/ |
| `la-chapelle-d-abondance` | APPLIED | price_from | = **22.0** | pl,ja,ar,he | https://skipass.lachapelle74.com/fr/ |
| `la-chapelle-d-abondance` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://skipass.lachapelle74.com/fr/ |
| `les-gets` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.lesgets.com/forfaits/ |
| `les-gets` | APPLIED | price_from | = **40.0** | pl,ja,ar,he | https://www.lesgets.com/forfaits/ |
| `les-gets` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.lesgets.com/forfaits/ |
| `megeve` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf |
| `megeve` | APPLIED | price_from | = **55.5** | pl,ja,ar,he | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf |
| `megeve` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf |
| `morzine` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ |
| `morzine` | APPLIED | price_from | = **40.0** | pl,ja,ar,he | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ |
| `morzine` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ |

---

## Grille 2025-26 seulement (notes préfixées)

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| `avoriaz` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ |
| `avoriaz` | APPLIED | price_from | = **44.0** | pl,ja,ar,he | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ |
| `avoriaz` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ |
| `bernex` | APPLIED | price_tiers | = **[5 tiers]** | pl,ja,ar,he | https://www.bernexstation.fr/fr/tarifs-hiver |
| `bernex` | APPLIED | price_from | = **15.5** | pl,ja,ar,he | https://www.bernexstation.fr/fr/tarifs-hiver |
| `bernex` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.bernexstation.fr/fr/tarifs-hiver |
| `chamonix-mont-blanc` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass |
| `chamonix-mont-blanc` | APPLIED | price_from | = **40.0** | pl,ja,ar,he | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass |
| `chamonix-mont-blanc` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass |
| `combloux` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.combloux.com/profiter/ski/forfaits-ski/ |
| `combloux` | APPLIED | price_from | = **17.5** | pl,ja,ar,he | https://www.combloux.com/profiter/ski/forfaits-ski/ |
| `combloux` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.combloux.com/profiter/ski/forfaits-ski/ |
| `cordon` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `cordon` | APPLIED | price_from | = **15.5** | pl,ja,ar,he | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `cordon` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `flaine` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `flaine` | APPLIED | price_from | = **29.5** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `flaine` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `hirmentaz-les-haberes` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin |
| `hirmentaz-les-haberes` | APPLIED | price_from | = **27.0** | pl,ja,ar,he | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin |
| `hirmentaz-les-haberes` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin |
| `la-clusaz` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html |
| `la-clusaz` | APPLIED | price_from | = **42.0** | pl,ja,ar,he | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html |
| `la-clusaz` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html |
| `le-grand-bornand` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ |
| `le-grand-bornand` | APPLIED | price_from | = **34.3** | pl,ja,ar,he | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ |
| `le-grand-bornand` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ |
| `le-reposoir` | APPLIED | price_tiers | = **[5 tiers]** | pl,ja,ar,he | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `le-reposoir` | APPLIED | price_from | = **7.0** | pl,ja,ar,he | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `le-reposoir` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `les-brasses` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf |
| `les-brasses` | APPLIED | price_from | = **10.9** | pl,ja,ar,he | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf |
| `les-brasses` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf |
| `les-carroz` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `les-carroz` | APPLIED | price_from | = **48.8** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `les-carroz` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `les-contamines-montjoie` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs |
| `les-contamines-montjoie` | APPLIED | price_from | = **44.5** | pl,ja,ar,he | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs |
| `les-contamines-montjoie` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs |
| `les-houches` | APPLIED | price_tiers | = **[4 tiers]** | pl,ja,ar,he | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais |
| `les-houches` | APPLIED | price_from | = **30.0** | pl,ja,ar,he | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais |
| `les-houches` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais |
| `manigod` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf |
| `manigod` | APPLIED | price_from | = **28.5** | pl,ja,ar,he | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf |
| `manigod` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf |
| `mont-saxonnex` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `mont-saxonnex` | APPLIED | price_from | = **2.0** | pl,ja,ar,he | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `mont-saxonnex` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `morillon` | APPLIED | price_tiers | = **[5 tiers]** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `morillon` | APPLIED | price_from | = **48.8** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `morillon` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `passy-plaine-joux` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ |
| `passy-plaine-joux` | APPLIED | price_from | = **22.5** | pl,ja,ar,he | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ |
| `passy-plaine-joux` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ |
| `praz-de-lys-sommand` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://espacedeslys.com/fr/tarifs |
| `praz-de-lys-sommand` | APPLIED | price_from | = **5.0** | pl,ja,ar,he | https://espacedeslys.com/fr/tarifs |
| `praz-de-lys-sommand` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://espacedeslys.com/fr/tarifs |
| `saint-gervais-les-bains` | APPLIED | price_tiers | = **[5 tiers]** | pl,ja,ar,he | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc |
| `saint-gervais-les-bains` | APPLIED | price_from | = **54.0** | pl,ja,ar,he | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc |
| `saint-gervais-les-bains` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc |
| `saint-jean-d-aulps` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ |
| `saint-jean-d-aulps` | APPLIED | price_from | = **22.5** | pl,ja,ar,he | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ |
| `saint-jean-d-aulps` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ |
| `samoens` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `samoens` | APPLIED | price_from | = **45.6** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `samoens` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ |
| `thollon-les-memises` | APPLIED | price_tiers | = **[6 tiers]** | pl,ja,ar,he | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ |
| `thollon-les-memises` | APPLIED | price_from | = **15.5** | pl,ja,ar,he | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ |
| `thollon-les-memises` | APPLIED | price_currency | = **EUR** | pl,ja,ar,he | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ |

---

## Rien de publié — prose « à l'automne »

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| — | — | — | — | — | (none) |
