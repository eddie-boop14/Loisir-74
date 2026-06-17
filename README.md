# Loisirs 74

**Independent multilingual leisure guide for Haute-Savoie, France.**
Lakes, waterfalls, viewpoints, leisure parks, cable cars, castles, museums — every fact
verified against official sources (communes, tourism offices, ONF, IGN, Natura 2000).

🌐 **Live:** [loisirs74.fr](https://loisirs74.fr) · 392 destinations · 6 languages (FR · EN · DE · IT · ES · NL)

---

## What this is
A flat, static site built from structured JSON. Each destination page carries GPS, opening
hours, access (free/paid), parking, dog policy, accessibility, how to get there (car / public
transport / bike), best season, on-site activities, and an FAQ — in six languages, with a
French canonical and `hreflang` alternates.

Editorial rules: official sources only, no aggregators, no fabricated data. Unknown hard
facts are left null and flagged rather than guessed. French place names are frozen verbatim
across all languages (Lac d'Annecy, Léman, Mont-Blanc, Haute-Savoie, …).

## How it's built
JSON is the single source of truth. A Python pipeline renders everything; nothing is
hand-edited in the built HTML.

```bash
python3 scripts/build_all.py        # render all fiches ×6 langs, hubs, catalog, communes
python3 scripts/build_all.py --no-site   # build + gates, skip the _site/ tree
```

Every push to `main` runs a CI **build gate** (status, hygiene, full render, reachability,
byte-stable double-build, protected-asset guards) before Netlify deploys. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full pipeline, the scheduled refresh workflows,
and how the browser authoring tool (Studio) fits.

## Repo layout (high level)
```
Json/            source of truth — one <slug>.json per lieu
scripts/         build pipeline + audits (Python)
<lang>/          generated HTML per locale (en/ de/ it/ es/ nl/; FR at root)
studio.html      browser authoring toolkit (+ studio-*.js modules)
.github/workflows/  build gate + monthly/weekly refresh agents
sitemap.xml, robots.txt, robots-ai.txt, llms.txt, .well-known/
```

## Status
Active. Catalogue and tooling evolve on `main`; treat the live repo as truth over any doc.

## Contributing / corrections
Spotted a wrong detail on a destination? Use the **"Signaler une info"** link on any page,
or open an issue. Partner enquiries: **"Devenir partenaire."**

## License & attribution
Site content © Bleu canard édition. Open data sources retain their own licenses
(e.g. DATAtourisme — Etalab Open License; photo credits per `photo-credits.json`).
Generated and maintained as **Edmaster & Claudius**.

---
*2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés* 🦆
