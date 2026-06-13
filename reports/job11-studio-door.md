# JOB 11 — Studio behind a door

Studio + DataTourisme Tab 7 working files are now **dev-only**. They live in the repo for local use but never deploy to the public site.

## What moved

`scripts/build_site.py` adds the following to its `DENY` set so they're excluded from `_site/`:

```
studio.html
studio-consts.js
studio-dt-importer.js
studio-editor.js
studio-enricher.js
studio-phototheque.js
studio-render.js
studio-templates.js
dt-candidates.json
```

`netlify.toml`: the per-file cache rules targeting those paths have been removed (the paths no longer ship, so the rules were dead code that would just confuse future readers).

## Gate evidence

| asset | repo root | _site/ |
|---|---|---|
| `studio.html` | present | **absent** |
| `studio-*.js` (7 modules) | present | **absent** (all 7) |
| `dt-candidates.json` (1.8 MB) | present | **absent** |

`_site/` file count: 3240 → 3226. Studio asset surface area on the public site: 0.

## Local development unchanged

Open `studio.html` with a `file://` URL or via any local static server pointed at the repo root. The Studio still loads `studio-*.js` + `dt-candidates.json` from the same directory. Same workflow you had before — just no longer reachable through `loisirs74.fr`.

## Defence-in-depth

The JOB 2 robots.txt `Disallow: /studio*` + `<meta name="robots" content="noindex">` rules are still in place. They're now belt-and-suspenders (the files don't exist in `_site/` to be crawled) but they protect against future regressions if a build script ever readmits a studio asset.

The CI `build-gate.yml` workflow also asserts the `_site/` leak-surface stays closed and uploads `_site/` as an artifact, so any reintroduction would be visible in PR review.

## Production check (post-deploy)

After the next Netlify deploy:

```
curl -I https://loisirs74.fr/studio       # expect 404
curl -I https://loisirs74.fr/studio.html  # expect 404
curl -I https://loisirs74.fr/dt-candidates.json  # expect 404
```
