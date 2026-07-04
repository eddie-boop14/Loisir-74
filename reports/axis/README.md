# AXIS — Agent Experience Index for loisirs74.fr (HANDOFF-38)

**Score: 97/100** (clean run, 2026-07-04, 6/6 scenarios, 0 failures).
Yardstick: `@netlify/axis` 1.17.0, claude-code adapter, scenarios in
`axis-scenarios/` (read-only, production, partner placements untouchable).

## The two first runs (both salvaged from CI logs at $0 — see this folder)

| run | mode | avg | why |
|---|---|---|---|
| 1 · 06:59 | baseline | 84 | **Anthropic credit balance hit $0 mid-run** — structured-data + planning died with "Credit balance is too low", judge scored their goals 0. Not a site defect. |
| 2 · 22:56 | run | **97** | clean — the honest number |

Both runs' report pushes then failed on a workflow bug (shallow checkout vs
stale report branch — fixed in this PR). Actual spend: $1.38 + $1.52 ≈ **$2.91**.

## Clean-run scenario board (axis | goal/env/service/agent)

| scenario | score | dims | note |
|---|---|---|---|
| fact-extraction | 98 | 100/100/94/94 | price 2,60 € + PMR found from the site |
| comparison | 98 | 100/100/95/95 | two real beaches, accurate facts, reasoned pick |
| multilingual-cs | 98 | 100/100/95/96 | /cs/ navigated, answered in Czech, 15 s |
| structured-data | 98 | 100/100/93/95 | full JSON-LD @graph + GPS one-shot via raw fetch |
| ai-discovery | 97 | 100/100/90/96 | llms.txt → declared resource → true fact |
| planning | 93 | 88/100/95/96 | 3 real venues + correct prices; judge: used homepage hub but not **category hubs** (6/10 on that check) |

## Top 3 agent blockers found (measure first — no fixes shipped, Edmaster prioritizes)

1. **Guessed-URL 404**: the agent speculatively fetched `/plages-lac-annecy`
   (a very reasonable semantic guess) and got a 404 before recovering.
   *Proposed fix (one line each):* `_redirects` 301s for the obvious
   agent-guess aliases (`/plages-lac-annecy → /baignade-lac-annecy`, and the
   same class for cascades/châteaux hubs).
2. **`api/lieux.json` ECONNRESET** (transient, cost ~27 s + the only service
   dip to 90): one reset on first fetch, retry succeeded.
   *Proposed fix:* likely edge/CDN flake — verify Netlify caching headers on
   `/api/*` (long `s-maxage`) so agents hit cache, not origin.
3. **Search-first discovery is the slow path** (15–21 s per WebSearch when
   the agent didn't start from llms.txt): the fastest runs all started from
   site resources. *Proposed fix:* advertise `llms.txt` + `/api/lieux.json`
   in `robots.txt` comments and the homepage `<head>` (rel="alternate"), so
   agents find the fast lane before searching.

Plus the planning judge's real finding: **category-hub navigation wasn't the
agent's natural route** — worth a "Par catégorie" block higher on the
homepage if Eddie wants the 93 → 98.

## Regression yardstick

`reports/axis/baseline/` is locked by workflow mode=`baseline` (run 1's lock
died with its runner — one re-click after this PR merges re-locks it, ~$1.5).
Every future run compares against it; the score is re-earned, never assumed.
