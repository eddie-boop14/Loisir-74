# Venue location audit

Scanned 325 fiches. Local cross-check only (no external API access in this sandbox).


## Summary

| Level | Count | Distinct slugs |
|---|---:|---:|
| ERR | 1 | 1 |
| WARN | 8 | 6 |
| INFO | 10 | 10 |

## By signal

| Signal | Count |
|---|---:|
| `coord-vs-commune` | 10 |
| `slug-vs-commune` | 4 |
| `addr-vs-commune` | 4 |
| `no-coords` | 1 |


## ERR — 1 rows

| slug | signal | detail |
|---|---|---|
| `parc-de-peche-domaine-du-moulin-authier` | no-coords | lat=0.0, lng=0.0 |

## WARN — 8 rows

| slug | signal | detail |
|---|---|---|
| `chateau-chatillon-sur-cluses` | addr-vs-commune | address mentions 'Cluses', commune is 'Châtillon-sur-Cluses' |
| `chateau-chatillon-sur-cluses` | slug-vs-commune | slug suggests 'Cluses', commune is 'Châtillon-sur-Cluses' |
| `escalade-la-crique-annecy` | addr-vs-commune | address mentions 'Annecy', commune is 'Saint-Jorioz' |
| `escalade-la-crique-annecy` | slug-vs-commune | slug suggests 'Annecy', commune is 'Saint-Jorioz' |
| `mont-joly` | addr-vs-commune | address mentions 'Megève', commune is 'Saint-Gervais-les-Bains' |
| `rafting-ecolorado-passy-samoens` | slug-vs-commune | slug suggests 'Samoëns', commune is 'Passy' |
| `veloroute-vallee-arve-cluses-sallanches` | slug-vs-commune | slug suggests 'Sallanches', commune is 'Cluses' |
| `viarhona-haute-savoie-saint-gingolph-seyssel` | addr-vs-commune | address mentions 'Thonon-les-Bains', commune is 'Saint-Gingolph' |

## INFO — 10 rows

| slug | signal | detail |
|---|---|---|
| `aquariaz` | coord-vs-commune | lat/lng 5.2 km from commune centroid |
| `cascade-des-fours` | coord-vs-commune | lat/lng 5.5 km from commune centroid |
| `chateau-la-rochette-lully` | coord-vs-commune | lat/lng 6.3 km from commune centroid |
| `karting-team-bouvier-pringy` | coord-vs-commune | lat/lng 7.6 km from commune centroid |
| `lac-blanc` | coord-vs-commune | lat/lng 6.3 km from commune centroid |
| `lac-de-vallon` | coord-vs-commune | lat/lng 6.2 km from commune centroid |
| `mont-joly` | coord-vs-commune | lat/lng 7.5 km from commune centroid |
| `sentier-maison-saleve-pomier-presilly` | coord-vs-commune | lat/lng 6.2 km from commune centroid |
| `telepherique-des-grands-montets` | coord-vs-commune | lat/lng 7.1 km from commune centroid |
| `tropicaland-viry` | coord-vs-commune | lat/lng 5.6 km from commune centroid |