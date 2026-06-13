# Audit — SET A + hub chain integrity per locale

**Date**: 2026-06-13
**Scope**: SET A (26 slugs × 5 non-FR locales = 130 fiche-langs) + per-locale chain index → hub → card → fiche.

## TL;DR

- **SET A**: 100 % clean. All 130 fiche-langs render in target locale, breadcrumbs are locale-correct, no FR residue.
- **Hub chain**: 13 of 15 hubs work correctly across all 5 non-FR locales. **2 hubs are broken** — `sensations-plein-air` and `que-faire` link every card to the FR canonical URL instead of the locale URL.
- **Index → hub**: 14 of 15 hubs are linked from each locale's `index.html`. `que-faire` is orphan from the homepage in every locale (FR included).

## SET A audit — 130 fiche-langs

| check | result |
|---|---|
| Files exist (26 × 5 locales) | 130/130 |
| Locale-text sentinel pass | 128/130 ✓ + 2 false-positive (IT proper noun "de la Grange", ES bilingual cognates) — visually verified, all 130 fully translated |
| Visible breadcrumb present | 130/130 |
| Breadcrumb hrefs use correct locale prefix `/{lang}/` | 130/130 |
| Breadcrumb hub label localized | 130/130 |
| Hero image renders | 130/130 |

**Verdict**: SET A closure (commit `c01a0ba2`) is solid. No remediation needed.

## Hub directory structure per locale

All 5 non-FR locales have 15 hub directories under localized slugs:

| canonical (FR) | en | de | it | es | nl |
|---|---|---|---|---|---|
| cascades | waterfalls | wasserfaelle | cascate | cascadas | watervallen |
| chateaux | castles | schloesser | castelli | castillos | kastelen |
| musees | museums | museen | musei | museos | musea |
| points-de-vue | viewpoints | aussichtspunkte | punti-panoramici | miradores | uitzichtpunten |
| sentiers | trails | wanderwege | sentieri | senderos | wandelpaden |
| telecabines | cable-cars | seilbahnen | funivie | telefericos | kabelbanen |
| voies-vertes | greenways | radwege | vie-verdi | vias-verdes | fietsroutes |
| lacs-plages | lakes | seen | laghi | lagos | meren |
| bases-de-loisirs | leisure-parks | freizeitparks | aree-recreative | areas-de-ocio | recreatieparken |
| baignade-nautisme | swimming-watersports | baden-wassersport | nuoto-sport-acquatici | bano-deportes-acuaticos | zwemmen-watersport |
| parcs-jardins | parks-gardens | parks-gaerten | parchi-giardini | parques-jardines | parken-tuinen |
| que-faire | **que-faire** | **que-faire** | **que-faire** | **que-faire** | **que-faire** |
| sensations-plein-air | outdoor-thrills | outdoor-nervenkitzel | brividi-aria-aperta | sensaciones-aire-libre | buitenavontuur |
| sorties-detente | outings-relax | ausfluege-erholung | uscite-relax | salidas-relax | uitstapjes-ontspanning |
| sport-jeux | sport-games | sport-spiele | sport-giochi | deporte-juegos | sport-spelen |

⚠️ `que-faire` slug is **not localized** in any locale — kept as French in the URL across all 6 locales. Not a navigation bug, but inconsistent with the rest of the hub-slug strategy. Track for a future polishing pass.

## Hub → Card chain (cards linking from each hub-index)

Each cell = `<correct-locale-links>/W<wrong-locale-links>` where `W>0` means clicking a card takes user to the wrong locale's fiche.

| hub | en | de | it | es | nl |
|---|---:|---:|---:|---:|---:|
| cascades | 32/W0 | 32/W0 | 32/W0 | 32/W0 | 32/W0 |
| chateaux | 52/W0 | 52/W0 | 52/W0 | 52/W0 | 52/W0 |
| musees | 100/W0 | 100/W0 | 100/W0 | 100/W0 | 100/W0 |
| points-de-vue | 58/W0 | 58/W0 | 58/W0 | 58/W0 | 58/W0 |
| sentiers | 80/W0 | 80/W0 | 80/W0 | 80/W0 | 80/W0 |
| telecabines | 24/W0 | 24/W0 | 24/W0 | 24/W0 | 24/W0 |
| voies-vertes | 10/W0 | 10/W0 | 10/W0 | 10/W0 | 10/W0 |
| lacs-plages | 62/W0 | 62/W0 | 62/W0 | 62/W0 | 62/W0 |
| bases-de-loisirs | 170/W0 | 170/W0 | 170/W0 | 170/W0 | 170/W0 |
| baignade-nautisme | 48/W0 | 48/W0 | 48/W0 | 48/W0 | 48/W0 |
| parcs-jardins | 62/W0 | 62/W0 | 62/W0 | 62/W0 | 62/W0 |
| **que-faire** | **80/W76** | **80/W76** | **80/W76** | **80/W76** | **80/W76** |
| **sensations-plein-air** | **0/W86** | **0/W86** | **0/W86** | **0/W86** | **0/W86** |
| sorties-detente | 44/W0 | 44/W0 | 44/W0 | 44/W0 | 44/W0 |
| sport-jeux | 106/W0 | 106/W0 | 106/W0 | 106/W0 | 106/W0 |

### Bug 1 — `sensations-plein-air` hub (outdoor-thrills / outdoor-nervenkitzel / etc.)

**Severity**: High. 86 wrong-locale card links per locale × 5 locales = **430 wrong navigations**.

In every non-FR locale's `sensations-plein-air` hub index, every fiche card href is the FR canonical URL:

```html
<!-- /en/outdoor-thrills/index.html — WRONG -->
<a href="https://loisirs74.fr/accrobranche-foret-aventures-manigod">…</a>

<!-- Expected -->
<a href="https://loisirs74.fr/en/accrobranche-foret-aventures-manigod">…</a>
```

A user browsing the English outdoor-thrills hub clicks a card and lands on the **French** fiche instead of the English one. Same for de/it/es/nl.

### Bug 2 — `que-faire` hub

**Severity**: Medium. 76 wrong-locale card links per non-FR locale × 5 = **380 wrong navigations**.

Half-correct: 80 of ~156 cards point to the right locale, the other 76 point to FR. The hub appears to have been partially regenerated — likely the 80 correct cards came from a later locale-aware pass, the 76 wrong ones are stale.

### Bug 3 — `que-faire` hub not linked from any homepage

The 15-hub-link target in every `index.html` is 14/15. `que-faire` is missing from FR, EN, DE, IT, ES, NL homepages — reachable only via direct URL or sitemap. Not a 404, but an orphan from primary navigation.

## Root cause hypothesis

JOB B (`b9e5942d` + `7ff27236`, breadcrumb fix) threaded locale-correct slug/label through `primary_hub(d, lang)` for fiche pages but did **not** touch the **hub-index regeneration** code path (`scripts/build_hubs.py` or equivalent). The hub-index pages are produced by a separate routine that still emits FR canonical hrefs for the `sensations-plein-air` and (partially) `que-faire` listings. The other 13 hubs were correctly rebuilt in an earlier locale-aware pass.

## Recommended next actions (not done in this audit — read-only)

1. Open `scripts/build_hubs.py` (or whichever script writes hub index pages) and find the card-link emitter for `sensations-plein-air` + `que-faire`. Apply the same `lang`-threaded URL pattern used in the 13 working hubs.
2. Add a `que-faire` link to the homepage hub strip in every locale.
3. Decide whether to localize the `que-faire` slug (e.g. `/en/what-to-do/`, `/de/was-machen/`) or keep FR-canonical across all locales. If localized, also fix the directory layout + sitemap.
4. Re-run `build_all.py --no-site` after fix → 0 wrong-locale W counts everywhere.

## Verification commands

```bash
# Hub-chain audit re-run
python3 -c "$(cat <<'PY'
import re; from pathlib import Path
ROOT=Path('/home/user/Loisir-74')
hubs={'sensations-plein-air':{'en':'outdoor-thrills','de':'outdoor-nervenkitzel',
'it':'brividi-aria-aperta','es':'sensaciones-aire-libre','nl':'buitenavontuur'},
'que-faire':{l:'que-faire' for l in 'en de it es nl'.split()}}
for hub,m in hubs.items():
    for L,slug in m.items():
        txt=(ROOT/L/slug/'index.html').read_text()
        urls=re.findall(r'href="https://loisirs74\.fr/([^"]+)"',txt)
        wrong=sum(1 for u in urls if not u.endswith('/') and u.split('/')[0] not in {L,'cgv','confidentialite','devenir-partenaire','mentions-legales','signaler','signaler-info'})
        print(f'  [{L}] {hub}: {wrong} wrong-locale card links')
PY
)"
```

Expected (post-fix): every line ends in `0 wrong-locale card links`.
