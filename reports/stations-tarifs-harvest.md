# Tarifs stations — harvest report (PART 1)
Payload: `data/station-tarifs-harvest.json` · generated 2026-07-20
- Stations in payload: **28** — grille 2026-27: **5** · grille 2025-26 (préfixée): **23** · rien publié (prose automne): **0**
- PENDING (à appliquer): **28** · APPLIED (déjà en ligne): **0** · rows refused/skipped: **0**

États par ligne : `∅ → value` = en attente d'apply · `= value (appliqué)` = déjà dans la fiche (post-apply). Un rapport où tout est APPLIED est un état des lieux, pas un no-op. Aucun prix n'est écrit sans source officielle + citation dans le payload.

---

## Grille 2026-27 publiée

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| `chatel` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.skipass-chatel.com/fr/tarifs-hiver *(new)* |
| `chatel` | PENDING | price_from | ∅ → **41.0** | fr,en,de,it,es,nl,pt,cs | https://www.skipass-chatel.com/fr/tarifs-hiver *(new)* |
| `chatel` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.skipass-chatel.com/fr/tarifs-hiver *(new)* |
| `la-chapelle-d-abondance` | PENDING | price_tiers | [0 tiers] → **[5 tiers]** | fr,en,de,it,es,nl,pt,cs | https://skipass.lachapelle74.com/fr/ *(new)* |
| `la-chapelle-d-abondance` | PENDING | price_from | ∅ → **22.0** | fr,en,de,it,es,nl,pt,cs | https://skipass.lachapelle74.com/fr/ *(new)* |
| `la-chapelle-d-abondance` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://skipass.lachapelle74.com/fr/ *(new)* |
| `les-gets` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.lesgets.com/forfaits/ *(new)* |
| `les-gets` | PENDING | price_from | ∅ → **40.0** | fr,en,de,it,es,nl,pt,cs | https://www.lesgets.com/forfaits/ *(new)* |
| `les-gets` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.lesgets.com/forfaits/ *(new)* |
| `megeve` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf *(new)* |
| `megeve` | PENDING | price_from | ∅ → **55.5** | fr,en,de,it,es,nl,pt,cs | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf *(new)* |
| `megeve` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://forfait.megeve.com/hiver/wp-content/uploads/sites/7/2026/05/26-27-Evasion-FR.pdf *(new)* |
| `morzine` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ *(new)* |
| `morzine` | PENDING | price_from | ∅ → **40.0** | fr,en,de,it,es,nl,pt,cs | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ *(new)* |
| `morzine` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.ski-morzine.com/hiver/tarifs/tarifs-morzine-les-gets-hiver/ *(new)* |

---

## Grille 2025-26 seulement (notes préfixées)

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| `avoriaz` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ *(new)* |
| `avoriaz` | PENDING | price_from | ∅ → **44.0** | fr,en,de,it,es,nl,pt,cs | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ *(new)* |
| `avoriaz` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.avoriaz.com/decouvrir/les-incontournables/tarifs-des-forfaits-hiver/ *(new)* |
| `bernex` | PENDING | price_tiers | [0 tiers] → **[5 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.bernexstation.fr/fr/tarifs-hiver *(new)* |
| `bernex` | PENDING | price_from | ∅ → **15.5** | fr,en,de,it,es,nl,pt,cs | https://www.bernexstation.fr/fr/tarifs-hiver *(new)* |
| `bernex` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.bernexstation.fr/fr/tarifs-hiver *(new)* |
| `chamonix-mont-blanc` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass *(new)* |
| `chamonix-mont-blanc` | PENDING | price_from | ∅ → **40.0** | fr,en,de,it,es,nl,pt,cs | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass *(new)* |
| `chamonix-mont-blanc` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://domaineschamonix.montblancnaturalresort.com/fr/billetterie/chamonix-lepass *(new)* |
| `combloux` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.combloux.com/profiter/ski/forfaits-ski/ *(new)* |
| `combloux` | PENDING | price_from | ∅ → **17.5** | fr,en,de,it,es,nl,pt,cs | https://www.combloux.com/profiter/ski/forfaits-ski/ *(new)* |
| `combloux` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.combloux.com/profiter/ski/forfaits-ski/ *(new)* |
| `cordon` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `cordon` | PENDING | price_from | ∅ → **15.5** | fr,en,de,it,es,nl,pt,cs | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `cordon` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.cordon.fr/hiver/domaine-skiable.htm |
| `flaine` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `flaine` | PENDING | price_from | ∅ → **29.5** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `flaine` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `hirmentaz-les-haberes` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin *(new)* |
| `hirmentaz-les-haberes` | PENDING | price_from | ∅ → **27.0** | fr,en,de,it,es,nl,pt,cs | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin *(new)* |
| `hirmentaz-les-haberes` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://hirmentaz-bellevaux.com/tarifs_forfaits.cgi?type=alpin *(new)* |
| `la-clusaz` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html *(new)* |
| `la-clusaz` | PENDING | price_from | ∅ → **42.0** | fr,en,de,it,es,nl,pt,cs | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html *(new)* |
| `la-clusaz` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.laclusaz.com/tarifs-forfait-la-clusaz.html *(new)* |
| `le-grand-bornand` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ *(new)* |
| `le-grand-bornand` | PENDING | price_from | ∅ → **34.3** | fr,en,de,it,es,nl,pt,cs | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ *(new)* |
| `le-grand-bornand` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.legrandbornand.com/quoi-faire/sports-loisirs-bien-etre/sports-dhiver/ski-alpin/tarifs/ *(new)* |
| `le-reposoir` | PENDING | price_tiers | [0 tiers] → **[5 tiers]** | fr,en,de,it,es,nl,pt,cs | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `le-reposoir` | PENDING | price_from | ∅ → **7.0** | fr,en,de,it,es,nl,pt,cs | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `le-reposoir` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | http://www.lereposoir.fr/activites_ete_et_hiver/domaine-skiable-les-3-villages-le-reposoir-194722/ |
| `les-brasses` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf *(new)* |
| `les-brasses` | PENDING | price_from | ∅ → **10.9** | fr,en,de,it,es,nl,pt,cs | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf *(new)* |
| `les-brasses` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://lesbrasses.com/wp-content/uploads/2025/11/Tarifs.pdf *(new)* |
| `les-carroz` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `les-carroz` | PENDING | price_from | ∅ → **48.8** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `les-carroz` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `les-contamines-montjoie` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs *(new)* |
| `les-contamines-montjoie` | PENDING | price_from | ∅ → **44.5** | fr,en,de,it,es,nl,pt,cs | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs *(new)* |
| `les-contamines-montjoie` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.lescontamines.com/hiver/skier/domaine-alpin/tarifs *(new)* |
| `les-houches` | PENDING | price_tiers | [0 tiers] → **[4 tiers]** | fr,en,de,it,es,nl,pt,cs | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais *(new)* |
| `les-houches` | PENDING | price_from | ∅ → **30.0** | fr,en,de,it,es,nl,pt,cs | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais *(new)* |
| `les-houches` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://leshouches.montblancnaturalresort.com/fr/billetterie/forfait-houches-saint-gervais *(new)* |
| `manigod` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf *(new)* |
| `manigod` | PENDING | price_from | ∅ → **28.5** | fr,en,de,it,es,nl,pt,cs | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf *(new)* |
| `manigod` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.manigod.com/medias/documents/Tarifs_ski_Manigod_hiver.pdf *(new)* |
| `mont-saxonnex` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `mont-saxonnex` | PENDING | price_from | ∅ → **2.0** | fr,en,de,it,es,nl,pt,cs | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `mont-saxonnex` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.mont-saxonnex.fr/domaine-skiable/ |
| `morillon` | PENDING | price_tiers | [0 tiers] → **[5 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `morillon` | PENDING | price_from | ∅ → **48.8** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `morillon` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `passy-plaine-joux` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ *(new)* |
| `passy-plaine-joux` | PENDING | price_from | ∅ → **22.5** | fr,en,de,it,es,nl,pt,cs | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ *(new)* |
| `passy-plaine-joux` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.passy-mont-blanc.com/decouvrir-passy/passy-plaine-joux/domaine-skiable-passy-plaine-joux/forfaits-de-ski-passy-plaine-joux/ *(new)* |
| `praz-de-lys-sommand` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://espacedeslys.com/fr/tarifs *(new)* |
| `praz-de-lys-sommand` | PENDING | price_from | ∅ → **5.0** | fr,en,de,it,es,nl,pt,cs | https://espacedeslys.com/fr/tarifs *(new)* |
| `praz-de-lys-sommand` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://espacedeslys.com/fr/tarifs *(new)* |
| `saint-gervais-les-bains` | PENDING | price_tiers | [0 tiers] → **[5 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc *(new)* |
| `saint-gervais-les-bains` | PENDING | price_from | ∅ → **54.0** | fr,en,de,it,es,nl,pt,cs | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc *(new)* |
| `saint-gervais-les-bains` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.ski-saintgervais.com/fr/tarifs-evasion-mont-blanc *(new)* |
| `saint-jean-d-aulps` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ *(new)* |
| `saint-jean-d-aulps` | PENDING | price_from | ∅ → **22.5** | fr,en,de,it,es,nl,pt,cs | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ *(new)* |
| `saint-jean-d-aulps` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.valleedaulps.com/explorer/stations/st-jean-daulps-roc-denfer/forfaits-roc-denfer/ *(new)* |
| `samoens` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `samoens` | PENDING | price_from | ∅ → **45.6** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `samoens` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.grand-massif.com/offres-ski/tarifs-forfaits-ski/ *(new)* |
| `thollon-les-memises` | PENDING | price_tiers | [0 tiers] → **[6 tiers]** | fr,en,de,it,es,nl,pt,cs | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ *(new)* |
| `thollon-les-memises` | PENDING | price_from | ∅ → **15.5** | fr,en,de,it,es,nl,pt,cs | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ *(new)* |
| `thollon-les-memises` | PENDING | price_currency | ∅ → **EUR** | fr,en,de,it,es,nl,pt,cs | https://www.leman-mountains-explore.com/108s/ski/ski-alpin-2/station-de-thollon-les-memises/ *(new)* |

---

## Rien de publié — prose « à l'automne »

| slug | état | field | valeur | prose langs | source |
|---|---|---|---|---|---|
| — | — | — | — | — | (none) |
