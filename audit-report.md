# Audit report — Json/*.json

Scanned **277** fiches from `Json/`.

## Summary

| Category | Hits | Distinct slugs |
|---|---:|---:|
| 1. Scaffolding leaks (CRITICAL) | 7 | 5 |
| 2. Naming-contamination (HIGH) | 23 | 19 |
| 3. Aggregator URL (MEDIUM) | 3 | 3 |
| 4. Schema/i18n (MEDIUM) | 318 | 197 |
| 5. Cross-field (LOW) | 8 | 8 |

**Highest-severity issue:** Category 1 — `Tier 1/2/3` scaffolding leaks in 4 rows across 2 slugs.

---
## 1. Scaffolding / build-note leaks (CRITICAL)

### Blast-radius by label

| Label | Distinct slugs | Sample slugs |
|---|---:|---|
| `argument central/majeur` | 2 | chateau-avully-brenthonne, maison-forte-hautetour-saint-gervais |
| `Tier 1/2/3` | 2 | grp-tour-lac-annecy-annecy, veloroute-vallee-arve-cluses-sallanches |
| `à compléter` | 1 | ecomusee-paysalp-viuz-en-sallaz |

### Per-finding detail

| slug | lang | field | label | context |
|---|---|---|---|---|
| `chateau-avully-brenthonne` | fr | `i18n.fr.body.what_is` | argument central/majeur | …ice POP Mérimée PA00118354).</p><p>Argument central et unique : depuis… |
| `ecomusee-paysalp-viuz-en-sallaz` | fr | `i18n.fr.when_to_visit` | à compléter | … Le Kube) reste le point d'entrée, à compléter selon disponibilité ave… |
| `grp-tour-lac-annecy-annecy` | fr | `i18n.fr.body.what_is` | Tier 1/2/3 | …MR</strong> ni poussettes. . . SEO Tier 1 - requêtes 'GR Pays Tour Lac… |
| `grp-tour-lac-annecy-annecy` | fr | `i18n.fr.when_to_visit` | Tier 1/2/3 | …es 5-8h, 800-1 300 m D+/jour). SEO Tier 1 - requêtes 'tour lac Annecy … |
| `maison-forte-hautetour-saint-gervais` | fr | `i18n.fr.body.what_is` | argument central/majeur | … la gare Mont-Blanc Express.</p><p>Argument central de 2025-2026 : la … |
| `veloroute-vallee-arve-cluses-sallanches` | fr | `i18n.fr.body.what_is` | Tier 1/2/3 | …ours avec passerelle attendue. SEO Tier 1 - requêtes 'vélo Vallée de l… |
| `veloroute-vallee-arve-cluses-sallanches` | fr | `i18n.fr.when_to_visit` | Tier 1/2/3 | …T PMR ET POUSSETTE compatible. SEO Tier 1 - requêtes 'V61 Léman Mont-B… |

---
## 2. Naming-contamination (HIGH)

| slug | lang | field | detail | context |
|---|---|---|---|---|
| `le-semnoz` | * | `(json)` | cross-ref: La Tavola | o a Le Semnoz, al Crêt de Châtillon e alla tavola di orientamento è libero e gra |
| `plage-de-saint-jorioz` | * | `(json)` | cross-ref: Chez Nous à la Plage | nesses": [{"tier": "featured", "name": "Chez Nous à la Plage", "type": "restaura |
| `plage-de-saint-jorioz` | * | `(json)` | cross-ref: cheznousalaplage |  · Fermé le lundi", "url": "https://www.cheznousalaplage.com", "price_range": "1 |
| `sentier-roselieres-saint-jorioz` | * | `(json)` | cross-ref: Chez Nous à la Plage | ers": [{"tier": "recommended", "name": "Chez Nous à la Plage", "type": "restaura |
| `sentier-roselieres-saint-jorioz` | * | `(json)` | cross-ref: cheznousalaplage | que. Fév-1er nov.", "url": "https://www.cheznousalaplage.com/", "cta_text": "Voi |
| `bowling-margencel-margencel` | fr | `body.what_is` | commune-cross-ref: Thonon ×4 (own=Margencel) |  |
| `bowling-sevrier-sevrier` | fr | `body.what_is` | commune-cross-ref: Annecy ×6 (own=Sevrier) |  |
| `cascade-d-angon` | fr | `body.what_is` | commune-cross-ref: Annecy ×3 (own=Talloires-Montmin) |  |
| `ereel-annecy-sillingy` | fr | `body.what_is` | commune-cross-ref: Annecy ×3 (own=Sillingy) |  |
| `grp-littoral-leman-saint-gingolph` | fr | `body.what_is` | commune-cross-ref: Évian ×3 (own=Saint-Gingolph) |  |
| `le-semnoz` | fr | `body.what_is` | commune-cross-ref: Annecy ×5 (own=Viuz-la-Chiésaz) |  |
| `mont-baron` | fr | `body.what_is` | commune-cross-ref: Annecy ×3 (own=Veyrier-du-Lac) |  |
| `plage-d-angon-talloires` | fr | `body.what_is` | commune-cross-ref: Annecy ×3 (own=Talloires-Montmin) |  |
| `plage-de-doussard` | fr | `body.what_is` | commune-cross-ref: Annecy ×4 (own=Doussard) |  |
| `plage-de-duingt` | fr | `body.what_is` | commune-cross-ref: Annecy ×4 (own=Duingt) |  |
| `plage-de-sevrier` | fr | `body.what_is` | commune-cross-ref: Annecy ×6 (own=Sévrier) |  |
| `plage-de-talloires` | fr | `body.what_is` | commune-cross-ref: Annecy ×4 (own=Talloires-Montmin) |  |
| `sentier-bout-du-lac-doussard` | fr | `body.what_is` | commune-cross-ref: Annecy ×5 (own=Doussard) |  |
| `tete-du-parmelan` | fr | `body.what_is` | commune-cross-ref: Annecy ×3 (own=Dingy-Saint-Clair) |  |
| `veloroute-vallee-arve-cluses-sallanches` | fr | `body.what_is` | commune-cross-ref: Sallanches ×3 (own=Cluses) |  |
| `veloroute-vallee-arve-cluses-sallanches` | fr | `body.what_is` | commune-cross-ref: Bonneville ×3 (own=Cluses) |  |
| `viarhona-ev17-bas-chablais-thonon` | fr | `body.what_is` | commune-cross-ref: Yvoire ×3 (own=Thonon-les-Bains) |  |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | fr | `body.what_is` | commune-cross-ref: Thonon ×3 (own=Saint-Gingolph) |  |

---
## 3. Aggregator URL (MEDIUM)

| slug | host | URL |
|---|---|---|
| `cascade-aventure` | `cascadeaventure.wixsite.com` | https://cascadeaventure.wixsite.com/cascade-aventure |
| `centre-aquatique-cluses` | `cluses-montagnes-tourisme.com` | https://www.cluses-montagnes-tourisme.com/equipement/centre-aquatique-intercommunal/ |
| `musee-du-batiment-ville-la-grand` | `museebatiment74.wixsite.com` | https://museebatiment74.wixsite.com/musedubtiment |

---
## 4. Schema / i18n integrity (MEDIUM)

| slug | lang | field | detail |
|---|---|---|---|
| `abbaye-d-aulps` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `abbaye-de-sixt` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `accrobranche-foret-aventures-manigod` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `accrobranche-foret-aventures-manigod` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `acro-aventures-reignier` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `acro-aventures-talloires` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `acroparc-de-bellavallis-bellevaux` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `acroparc-de-bellavallis-bellevaux` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `aire-de-decollage-parapente-plaine-joux` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `aquaparc-aqualis-cluses` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `aquaparc-aqualis-cluses` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `aquaparc-chateau-bleu-annemasse` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `aquaparc-chateau-bleu-annemasse` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `aquaparc-thonon-piscine-olympique-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `aquaparc-thonon-piscine-olympique-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `aquariaz` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `base-de-loisirs-de-la-beunaz` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `base-de-loisirs-des-ilettes` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `base-de-loisirs-du-lac-aux-dames` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `base-de-loisirs-du-lac-bleu` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `base-de-loisirs-du-lac-des-iles` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `base-de-loisirs-du-vuaz-filliere` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `base-de-loisirs-du-vuaz-filliere` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `base-nautique-doussard-doussard` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `base-nautique-doussard-doussard` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `base-nautique-marquisats-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `base-nautique-marquisats-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `base-nautique-sciez-sciez` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `base-nautique-sciez-sciez` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `belvedere-du-mont-baron` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `bowling-aerodrome-annemasse` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `bowling-aerodrome-annemasse` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `bowling-le-bowl-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `bowling-le-bowl-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `bowling-margencel-margencel` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `bowling-margencel-margencel` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `bowling-sevrier-sevrier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `bowling-sevrier-sevrier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `c5-kids-party-ville-la-grand` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `c5-kids-party-ville-la-grand` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `cascade-aventure` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `cascade-d-angon` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-chedde` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-doran` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-l-arpenaz` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-l-arpenaz` | - | `i18n` | missing langs: ['de'] |
| `cascade-de-la-belle-au-bois` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-la-diomaz` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-de-nyon` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-des-brochaux` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-des-fours` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-des-fours` | - | `i18n` | missing langs: ['de'] |
| `cascade-du-chinaillon` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-du-chinaillon` | - | `i18n` | missing langs: ['de'] |
| `cascade-du-dard` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cascade-du-rouget` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `casino-evian-resort-evian` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `casino-evian-resort-evian` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `casino-imperial-palace-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `casino-imperial-palace-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-avully-brenthonne` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-avully-brenthonne` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-beauregard-saint-jeoire` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `chateau-beauregard-saint-jeoire` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-bellegarde-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `chateau-bellegarde-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-chatillon-sur-cluses` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `chateau-chatillon-sur-cluses` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-clermont-genevois` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-clermont-genevois` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-comtes-de-geneve-annecy` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-comtes-de-geneve-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-de-menthon-saint-bernard` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-de-thorens` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-des-rubins-observatoire-des-alpes` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-des-rubins-sallanches` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-des-rubins-sallanches` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-et-donjon-des-seigneurs-de-faverges` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `chateau-la-rochette-lully` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `chateau-la-rochette-lully` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-montrottier-lovagny` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-montrottier-lovagny` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-ripaille-thonon` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-ripaille-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateau-sires-faucigny-bonneville` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `chateau-sires-faucigny-bonneville` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `chateaux-des-allinges` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `cirque-du-fer-a-cheval` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `col-de-la-forclaz` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `col-des-aravis` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `col-des-glieres` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `col-des-pitons-saleve` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `col-des-pitons-saleve` | - | `i18n` | missing langs: ['de'] |
| `cote-2000-aventure` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `croisiere-bateaux-annecy-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `croisiere-bateaux-annecy-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `croisiere-cgn-evian` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `croisiere-cgn-evian` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `croisiere-cgn-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `croisiere-cgn-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `croisiere-cgn-yvoire` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `croisiere-cgn-yvoire` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `domaine-de-guidou` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `domaine-de-rovoree-la-chataigniere` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `domaine-du-tornet` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `ecomusee-paysalp-viuz-en-sallaz` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `ecomusee-paysalp-viuz-en-sallaz` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `ecomusee-peche-et-du-lac-thonon` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `ecomusee-peche-et-du-lac-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `ereel-annecy-sillingy` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `ereel-annecy-sillingy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `espace-tairraz-musee-des-cristaux-chamonix` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `espace-tairraz-musee-des-cristaux-chamonix` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `filenvol-monnetier-mornex` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `filenvol-monnetier-mornex` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `fonderie-paccard-sevrier` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `fonderie-paccard-sevrier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `gorges-du-fier` | - | `top-level` | missing required keys: ['official_site_url', 'price_tiers'] |
| `gr5-grande-traversee-alpes-saint-gingolph` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `gr5-grande-traversee-alpes-saint-gingolph` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `gr96-bornes-aravis-haute-savoie` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `gr96-bornes-aravis-haute-savoie` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `grand-parc-d-andilly` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `grand-parc-d-andilly` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `grotte-et-cascade-de-seythenex` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `grotte-et-cascade-de-seythenex` | - | `i18n` | missing langs: ['de'] |
| `grp-littoral-leman-saint-gingolph` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `grp-littoral-leman-saint-gingolph` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `grp-tour-lac-annecy-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `grp-tour-lac-annecy-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `grp-tour-pays-mont-blanc-sallanches` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `grp-tour-pays-mont-blanc-sallanches` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `ile-de-tortuga-vetraz-monthoux` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `ile-de-tortuga-vetraz-monthoux` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `indiana-ventures-saint-paul-en-chablais` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `jardin-cimes-passy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `jardin-cimes-passy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `jardin-des-cinq-sens` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `jardin-jaysinia-samoens` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `jardin-jaysinia-samoens` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `karting-mk-circuit-scientrier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `karting-mk-circuit-scientrier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `karting-mont-blanc-passy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `karting-mont-blanc-passy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `karting-onlykart-roche-sur-foron` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `karting-onlykart-roche-sur-foron` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `karting-rumilly-rumilly` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `karting-rumilly-rumilly` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `karting-team-bouvier-pringy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `karting-team-bouvier-pringy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `lac-benit` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-blanc` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-cornu` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-de-passy` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-de-vallon` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-des-confins` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-des-dronieres` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `lac-vert-passy` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `le-semnoz` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `leman-forest-saint-gingolph` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `leman-forest-saint-gingolph` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `leman-kid-thonon-les-bains` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `leman-kid-thonon-les-bains` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `les-aigles-du-leman` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `maison-de-barberine-vallorcine` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `maison-de-barberine-vallorcine` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `maison-de-la-memoire-janny-couttet-chamonix` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `maison-de-la-memoire-janny-couttet-chamonix` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `maison-de-la-memoire-paysalp` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `maison-de-la-memoire-paysalp` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `maison-du-lieutenant-servoz` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `maison-du-lieutenant-servoz` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `maison-du-saleve-presilly` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `maison-du-saleve-presilly` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `maison-forte-hautetour-saint-gervais` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `maison-forte-hautetour-saint-gervais` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `mont-baron` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `mont-joly` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `mont-saleve` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `mont-veyrier` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `musee-archeologique-viuz-faverges` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-archeologique-viuz-faverges` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-chateau-annecy` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-chateau-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-cinema-animation-annecy` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-cinema-animation-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-du-batiment-ville-la-grand` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `musee-du-batiment-ville-la-grand` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-du-chablais-thonon-les-bains` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-du-chablais-thonon-les-bains` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-du-mont-blanc-chamonix` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-du-mont-blanc-chamonix` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `musee-montagnard-les-houches` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `musee-montagnard-les-houches` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `museum-des-papillons-et-insectes-faverges` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `museum-des-papillons-et-insectes-faverges` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `palais-de-l-ile-annecy` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `palais-de-l-ile-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `palais-lumiere` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `parc-aventure-mont-blanc-saint-gervais` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `parc-aventure-mont-blanc-saint-gervais` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `parc-de-loisirs-du-pontet` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `parc-de-merlet` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `parc-de-merlet` | - | `i18n` | missing langs: ['de'] |
| `parc-des-dereches` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `parc-des-dronieres` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `parcours-aventure-de-sciez` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `passy-accro-lac` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `patinoire-jean-regis-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `patinoire-jean-regis-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `patinoire-palais-megeve` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `patinoire-palais-megeve` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `patinoire-richard-bozon-chamonix` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `patinoire-richard-bozon-chamonix` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-albigny` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-d-amphion-publier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-d-amphion-publier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-d-angon-talloires` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-d-angon-talloires` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-d-evian-centre-nautique` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-d-evian-centre-nautique` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-d-excenevex` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-d-excenevex` | - | `i18n` | missing langs: ['de'] |
| `plage-de-doussard` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-doussard` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-duingt` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-duingt` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-la-brune-veyrier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-la-brune-veyrier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-la-pinede` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-de-margencel-sechex` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-margencel-sechex` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-menthon-saint-bernard` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-de-messery` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-messery` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-saint-disdille` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-de-saint-gingolph` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-saint-gingolph` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-sciez-sur-leman` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-de-sevrier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-sevrier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-talloires` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-talloires` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-de-tougues-chens` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-de-tougues-chens` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-des-marquisats` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `plage-du-lac-de-montriond` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-du-lac-de-montriond` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-imperial-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-imperial-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plage-municipale-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `plage-municipale-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `plateau-des-glieres` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `pont-de-la-caille` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `sentier-balcon-leman-saleve` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-balcon-leman-saleve` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-bout-du-lac-doussard` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-bout-du-lac-doussard` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-cascades-sixt-fer-a-cheval` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-cascades-sixt-fer-a-cheval` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-decouverte-plateau-glieres-thorens-glieres` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-decouverte-plateau-glieres-thorens-glieres` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-desert-de-plate-passy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-desert-de-plate-passy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-espagnols-pas-du-roc-glieres` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-espagnols-pas-du-roc-glieres` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-maison-saleve-pomier-presilly` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-maison-saleve-pomier-presilly` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-roselieres-saint-jorioz` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-roselieres-saint-jorioz` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `sentier-tournette-montmin` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `sentier-tournette-montmin` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `telecabine-des-chavannes-les-gets` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telecabine-du-jaillet` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telecabine-du-mont-chery-les-gets` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telecabine-panoramic-mont-blanc` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telecabine-panoramic-mont-blanc` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `telecabine-pleney-morzine` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telecabine-super-chatel` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telepherique-aiguille-du-midi` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telepherique-aiguille-du-midi` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `telepherique-des-grands-montets` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `telepherique-du-brevent` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telepherique-du-saleve` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `telepherique-du-saleve` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `tete-du-parmelan` | - | `top-level` | missing required keys: ['featured_businesses', 'official_site_url', 'price_tiers'] |
| `thermes-evian` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `tour-bellecombe-reignier` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `tour-bellecombe-reignier` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `tour-des-langues-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `tour-des-langues-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `tour-du-mont-blanc-les-houches` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `tour-du-mont-blanc-les-houches` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `train-du-montenvers-mer-de-glace` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `train-du-montenvers-mer-de-glace` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `tramway-du-mont-blanc` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `tropicaland-viry` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `tropicaland-viry` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `veloroute-vallee-arve-cluses-sallanches` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `veloroute-vallee-arve-cluses-sallanches` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `viarhona-ev17-bas-chablais-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `viarhona-ev17-bas-chablais-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `villa-du-parc-annemasse` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `villa-du-parc-annemasse` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `vitam-neydens` | - | `top-level` | missing required keys: ['featured_businesses'] |
| `vitam-neydens` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `voie-verte-arve-cluses-thyez` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `voie-verte-arve-cluses-thyez` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `voie-verte-lac-annecy-annecy` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `voie-verte-lac-annecy-annecy` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `voile-cercle-thonon-thonon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `voile-cercle-thonon-thonon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `wakepark-ponton-embarcadere-saint-jorioz` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `wakepark-ponton-embarcadere-saint-jorioz` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |
| `wakepark-tna-cable-park-arenthon` | - | `top-level` | missing required keys: ['featured_businesses', 'price_tiers'] |
| `wakepark-tna-cable-park-arenthon` | - | `i18n` | missing langs: ['de', 'en', 'es', 'it'] |

### Informational — untranslated (FR-mirror) `body.what_is` counts

| lang | fiches mirroring FR |
|---|---:|
| en | 79 |
| de | 79 |
| it | 79 |
| es | 79 |

_(Sparse fiches mirror FR by design until translation pass.)_

---
## 5. Cross-field consistency (LOW)

| slug | field | detail |
|---|---|---|
| `bar-a-jeux-youri-bar-cran-gevrier` | `postal_code` | 74960 != 74000 for Annecy |
| `karting-team-bouvier-pringy` | `postal_code` | 74370 != 74000 for Annecy |
| `la-turbine-sciences-cran-gevrier` | `postal_code` | 74960 != 74000 for Annecy |
| `lancer-de-hache-l-hachez-vous-annecy` | `postal_code` | 74600 != 74000 for Annecy |
| `mont-veyrier` | `postal_code` | 74940 != 74000 for Annecy |
| `plage-albigny` | `postal_code` | 74940 != 74000 for Annecy |
| `plage-de-saint-jorioz` | `is_free/price_from` | is_free=true but price_from=2.6 |
| `plage-imperial-annecy` | `is_free/price_from` | is_free=true but price_from=2026.0 |

---
## Recommendation

**Address Category 1 first.** 7 scaffolding rows across 5 fiches still in visitor copy.
