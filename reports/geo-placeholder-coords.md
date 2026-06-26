# Geo placeholder-coordinate audit (handoff §C)

_Computed from published Json/*.json — fiches sharing an identical (lat,lng), i.e. a likely commune-centre fallback rather than a real per-venue pin._

- **High-confidence placeholders** (3+ venues on one point): **8 coords / 34 lieux** — this is the handoff's ~"37/9" set.
- **Review (2 venues on one point)**: 12 coords / 24 lieux — mix of fallbacks and genuinely co-located venues.
- **Total**: 20 coords / 58 lieux.

## A. High-confidence placeholders (backfill priority)

### (45.8992, 6.1294) — 10 lieux — Annecy
- `bureau-des-guides-annecy`  · attraction
- `canyoning-neo-canyon`  · attraction
- `canyoning-yaute-canyon`  · attraction
- `escape-game-mysteres-du-lac-annecy`  · attraction
- `grp-tour-lac-annecy-annecy`  · sentier
- `montgolfiere-annecy`  · attraction
- `segway-mobilboard-annecy`  · attraction
- `simulateur-emotion-concept-annecy`  · attraction
- `trampoline-bam-freesports-annecy`  · attraction
- `voie-verte-lac-annecy-annecy`  · voie-verte

### (45.9237, 6.8694) — 5 lieux — Chamonix-Mont-Blanc
- `accrobranche-la-foret-magique-chamonix`  · attraction
- `cinema-le-vox-chamonix`  · cinema
- `paintball-chamonix`  · attraction
- `patinoire-richard-bozon-chamonix`  · patinoire
- `spa-qc-terme-chamonix`  · divers

### (45.9244, 6.7036) — 4 lieux — Passy
- `chiens-de-traineau-granges-de-heidi-passy`  · attraction
- `padel-mont-blanc-padel-passy`  · attraction
- `rafting-ecolorado-passy-samoens`  · attraction
- `via-ferrata-curalla-passy`  · attraction

### (46.3697, 6.4742) — 3 lieux — Thonon-les-Bains
- `aquaparc-thonon-piscine-olympique-thonon`  · aquaparc
- `croisiere-cgn-thonon`  · croisiere
- `voile-cercle-thonon-thonon`  · base-nautique

### (45.8804, 6.3247) — 3 lieux — Thônes
- `atelier-poterie-du-prunier-thones`  · attraction
- `atelier-poterie-ryokan-thones`  · attraction
- `karting-thones`  · karting

### (46.3712, 6.4789) — 3 lieux — Thonon-les-Bains
- `billard-thonon-billard-club`  · attraction
- `padel-tennis-squash-club-thonon`  · attraction
- `rafting-frogs-rafting-dranse`  · attraction

### (45.908, 6.13) — 3 lieux — Annecy
- `atelier-poterie-chez-el-annecy`  · attraction
- `escalade-atome-annecy`  · attraction
- `escape-game-atelier-des-enigmes-annecy`  · attraction

### (46.2719, 6.5511) — 3 lieux — Bellevaux
- `cascade-de-la-diomaz`  · cascade
- `ferme-pedagogique-petit-mont-bellevaux`  · attraction
- `jardin-alpin-de-bellevaux`  · attraction

## B. Two-venue clusters (review — some are real co-locations)

- (45.9166, 6.8702) — Chamonix-Mont-Blanc: `telecabine-panoramic-mont-blanc`, `telepherique-aiguille-du-midi`
- (46.2667, 6.8417) — Châtel: `telecabine-super-chatel`, `tyrolienne-fantasticable-chatel`
- (46.0617, 6.5811) — Cluses: `veloroute-vallee-arve-cluses-sallanches`, `voie-verte-arve-cluses-thyez`
- (46.04015, 6.122339) — Cruseilles: `parc-des-dronieres`, `tactiq-aventure-cruseilles`
- (45.7833, 6.2167) — Doussard: `base-nautique-doussard-doussard`, `sentier-bout-du-lac-doussard`
- (45.9667, 6.05) — La Balme-de-Sillingy, Sillingy: `escalade-space-bloc-sillingy`, `jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy`
- (45.9461, 6.4275) — Le Grand-Bornand: `chiens-de-traineau-nordic-event-74`, `tir-a-l-arc-grandbo-archerie-le-grand-bornand`
- (46.1797, 6.7081) — Morzine: `espace-aquatique-morzine`, `telecabine-pleney-morzine`
- (45.9333, 6.7) — Passy: `jardin-cimes-passy`, `sentier-desert-de-plate-passy`
- (46.3917, 6.8056) — Saint-Gingolph: `grp-littoral-leman-saint-gingolph`, `viarhona-haute-savoie-saint-gingolph-seyssel`
- (45.9622, 6.0617) — Sillingy: `laser-game-lasermaxx-sillingy`, `vr-ereel-annecy-sillingy`
- (46.4011, 6.5886) — Évian-les-Bains: `jardin-pre-curieux-evian`, `montgolfiere-du-mont-blanc-evian`

## C. Flat slug list — high-confidence set (for the backfill pass)

- accrobranche-la-foret-magique-chamonix
- aquaparc-thonon-piscine-olympique-thonon
- atelier-poterie-chez-el-annecy
- atelier-poterie-du-prunier-thones
- atelier-poterie-ryokan-thones
- billard-thonon-billard-club
- bureau-des-guides-annecy
- canyoning-neo-canyon
- canyoning-yaute-canyon
- cascade-de-la-diomaz
- chiens-de-traineau-granges-de-heidi-passy
- cinema-le-vox-chamonix
- croisiere-cgn-thonon
- escalade-atome-annecy
- escape-game-atelier-des-enigmes-annecy
- escape-game-mysteres-du-lac-annecy
- ferme-pedagogique-petit-mont-bellevaux
- grp-tour-lac-annecy-annecy
- jardin-alpin-de-bellevaux
- karting-thones
- montgolfiere-annecy
- padel-mont-blanc-padel-passy
- padel-tennis-squash-club-thonon
- paintball-chamonix
- patinoire-richard-bozon-chamonix
- rafting-ecolorado-passy-samoens
- rafting-frogs-rafting-dranse
- segway-mobilboard-annecy
- simulateur-emotion-concept-annecy
- spa-qc-terme-chamonix
- trampoline-bam-freesports-annecy
- via-ferrata-curalla-passy
- voie-verte-lac-annecy-annecy
- voile-cercle-thonon-thonon
