# JOB 8 — Sweep signals → state machine

> ## ⚠️ INVALID RUN — do not act on the 42 flags below
>
> The 2026-07-01 run executed after the Google Cloud free trial expired
> (billing email 2026-06-26): the Places API key was dead, **every Google call
> errored**, and the checker overwrote verified data with the error state
> (commits `ad73fc07` + `8ac6ba1d`, reverted by HANDOFF-24 Job 1). The 42
> "official site not responding" flags all landed on the **same day** —
> including Pathé Annecy, Casino Evian and the Palais Lumière — which means the
> reachability checker failed, not the venues. **No demotion or flag from this
> run is actionable.** The signals were produced by a broken checker, and the
> underlying fiche data has been restored to its pre-run verified state.
>
> The scripts now carry the error≠data rule and a mass-failure circuit breaker
> (HANDOFF-24 Job 2) so a dead API key can never rewrite fiches again.

Run at 2026-07-01. Source signals: `freshness` (sweep_loisirs74.py) + `google_check` (check_loisirs74.py).

## Summary

| action | count |
|---|---|
| demoted to draft (new) | 0 |
| flagged for review (kept published) | 42 |
| skipped (already draft) | 0 |

## Flagged for review (kept published — seasonal / temporary signals)

| slug | reason |
|---|---|
| ancien-remparts-chateau-lullin-lullin | freshness: official site not responding (checked 2026-07-01) |
| aquaparc-thonon-piscine-olympique-thonon | freshness: official site not responding (checked 2026-07-01) |
| base-nautique-evian-bains | freshness: official site not responding (checked 2026-07-01) |
| base-nautique-sciez-sciez | freshness: official site not responding (checked 2026-07-01) |
| boucle-pedestre-detective-nature-jonzier-epagny | freshness: official site not responding (checked 2026-07-01) |
| casino-evian-resort-evian | freshness: official site not responding (checked 2026-07-01) |
| centre-aquatique-cluses | freshness: official site not responding (checked 2026-07-01) |
| cinema-le-france-thonon | freshness: official site not responding (checked 2026-07-01) |
| cinema-pathe-annecy | freshness: official site not responding (checked 2026-07-01) |
| cinema-pathe-archamps-imax | freshness: official site not responding (checked 2026-07-01) |
| col-de-la-colombiere | freshness: official site not responding (checked 2026-07-01) |
| ecomusee-bois-foret-thones | freshness: official site not responding (checked 2026-07-01) |
| ecomusee-peche-et-du-lac-thonon | freshness: official site not responding (checked 2026-07-01) |
| espace-tairraz-musee-des-cristaux-chamonix | freshness: official site not responding (checked 2026-07-01) |
| full-land-annecy | freshness: official site not responding (checked 2026-07-01) |
| jardin-parc-des-jardins-de-haute-savoie-la-balme-de-sillingy | freshness: official site not responding (checked 2026-07-01) |
| la-foret-enchantee-sillingy | freshness: official site not responding (checked 2026-07-01) |
| lac-des-dronieres | freshness: official site not responding (checked 2026-07-01) |
| laser-game-evolution-ville-la-grand | freshness: official site not responding (checked 2026-07-01) |
| maison-de-la-memoire-janny-couttet-chamonix | freshness: official site not responding (checked 2026-07-01) |
| musee-du-chablais-thonon-les-bains | freshness: official site not responding (checked 2026-07-01) |
| musee-montagnard-les-houches | freshness: official site not responding (checked 2026-07-01) |
| musee-nature-gruffy | freshness: official site not responding (checked 2026-07-01) |
| paintball-zone-74-perrignier | freshness: official site not responding (checked 2026-07-01) |
| palais-lumiere | freshness: official site not responding (checked 2026-07-01) |
| parc-jean-beauquis-ambilly | freshness: official site not responding (checked 2026-07-01) |
| patinoire-la-clusaz | freshness: official site not responding (checked 2026-07-01) |
| plage-d-amphion-publier | freshness: official site not responding (checked 2026-07-01) |
| plage-d-evian-centre-nautique | freshness: official site not responding (checked 2026-07-01) |
| plage-de-duingt | freshness: official site not responding (checked 2026-07-01) |
| plage-de-margencel-sechex | freshness: official site not responding (checked 2026-07-01) |
| plage-de-saint-disdille | freshness: official site not responding (checked 2026-07-01) |
| plage-de-saint-gingolph | freshness: official site not responding (checked 2026-07-01) |
| plage-municipale-thonon | freshness: official site not responding (checked 2026-07-01) |
| sentier-cascades-sixt-fer-a-cheval | freshness: official site not responding (checked 2026-07-01) |
| sentier-pedestre-eterlou-chatel | freshness: official site not responding (checked 2026-07-01) |
| sentier-pedestre-sonore-sur-traces-contrebandiers-circuit-familles-chatel | freshness: official site not responding (checked 2026-07-01) |
| simulateur-warmup-academy-margencel | freshness: official site not responding (checked 2026-07-01) |
| telecabine-du-jaillet | freshness: official site not responding (checked 2026-07-01) |
| telecabine-panoramic-mont-blanc | freshness: official site not responding (checked 2026-07-01) |
| train-du-montenvers-mer-de-glace | freshness: official site not responding (checked 2026-07-01) |
| tyrolienne-fantasticable-chatel | freshness: official site not responding (checked 2026-07-01) |

