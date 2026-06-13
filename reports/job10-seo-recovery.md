# JOB 10 — Post-rebuild SEO recovery (local verification)

GSC-side items (resubmit sitemap, watch indexing) are external and only verifiable after deploy. What we can verify locally:

## Local gates — ALL GREEN

| gate | result |
|---|---|
| hreflang clusters coherent | 0 broken (5 fiches × 6 locales = 30 samples; every page emits the full fr/en/de/it/es/nl/x-default cluster) |
| FR meta_title uniqueness | 0 duplicates (392 fiches, every `i18n.fr.meta_title` distinct) |
| canonical-vs-self URL match | 0 mismatches (every page's `<link rel="canonical">` matches its own URL on the locale's tree) |
| og:locale ↔ html lang consistency | 0 mismatches across sampled pages × 6 locales |
| `/lacs/` + `/plages/` → `/lacs-plages/` 301 | intact in `_redirects` (`/lacs → /lacs-plages`, `/plages → /lacs-plages`) + netlify.toml |
| other legacy 301s | 8 explicit lines preserved (cascade-d-arpenaz, plaine-de-joux, lac-vert + 4 others) |

## Per-fiche meta_title is built from JSON (not from chrome template)

JOB 1's `build_lieu_page.py` reads `i18n.<lang>.meta_title` per locale (with FR fallback), then writes it into `<title>` and `<meta property="og:title">`. The audit's flagged "duplicate-meta_title gaps" came from `localize_lieu.py` reusing the FR title across all locales. That pipeline was retired in JOB 1; the new pipeline gives every locale page its own meta_title where the JSON has one.

Spot-check on `au-fil-rail-jeu-piste-a-servoz-servoz` (one of the JOB 7 samples):

| locale | `<title>` |
|---|---|
| fr | Au Fil du Rail - Jeu de Piste à Servoz · Gratuit · OT Chamonix |
| en | Au Fil du Rail Treasure Hunt at Servoz · Free · OT Chamonix |
| de | Au Fil du Rail – Schnitzeljagd Servoz · Kostenlos · OT Chamonix |
| it | Caccia al tesoro Au Fil du Rail Servoz · Gratuita · OT Chamonix |
| es | Búsqueda del tesoro Au Fil du Rail Servoz · Gratis · OT Chamonix |
| nl | Speurtocht Au Fil du Rail Servoz · Gratis · OT Chamonix |

## External gates (post-deploy, GSC-side)

These can only be verified after the next deploy lands and Googlebot recrawls:

- [ ] Resubmit sitemap in GSC (`https://loisirs74.fr/sitemap.xml` — 2,458 URLs, 0 phantoms post-JOB-4).
- [ ] Verify locale `/en/`, `/de/`, `/it/`, `/es/`, `/nl/` pages indexed with correct language per GSC's Coverage report.
- [ ] Verify hreflang cluster validation passes in GSC's International Targeting report.
- [ ] Verify no redirect chain breaks on the old `/lacs/...` / `/plages/...` URLs — the 301s are in `_redirects` and intact, but GSC needs a recrawl pass to confirm.

## Raw data

`reports/job10-seo-verify.json` — full assertion output.
