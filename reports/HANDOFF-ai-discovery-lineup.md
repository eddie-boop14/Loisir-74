# HANDOFF — AI-discovery line-up (SHIPPED, corrected)

**Status: DELIVERED.** Jobs A–D merged in PR #69 (`81f7928`, 2026-07-25) on top of `89c1597`.
Kept in-repo because the source handoff carried two factual errors; this is the corrected copy so
the next cold read starts from truth rather than from the draft.

**Rung: hygiene → agent-readiness.** Not a ranking mover. Overkill insurance on the agentic-web
transition, done without risking the one thing that *is* a mover: the AI citation curve.

---

## §0 — THE FIRST GATE, ABOVE EVERYTHING

> **DO NO HARM TO THE CITATION CURVE.**

The AI-citation growth (328 → 380 impressions/day) runs on **crawlable static HTML + JSON-LD**,
fetched by citation bots. No job may reorder, narrow, or `Disallow` any citation path.

**⚑ CORRECTED (C-2) — how citation access is actually enforced.**
The original §0 listed **nine** citation bots as "frozen protected lines". That overstated what
`robots.txt` enforces. Verified against live `89c1597`:

| bot | has its own `robots.txt` group? | how it is actually allowed |
|---|---|---|
| ClaudeBot | **yes** | explicit `Allow: /` |
| PerplexityBot | **yes** | explicit `Allow: /` |
| Google-Extended | **yes** | explicit `Allow: /` |
| OAI-SearchBot | no | **`User-agent: *` wildcard** |
| ChatGPT-User | no | **`User-agent: *` wildcard** |
| Claude-Web | no | **`User-agent: *` wildcard** |
| anthropic-ai | no | **`User-agent: *` wildcard** |
| PerplexityBot-User | no | **`User-agent: *` wildcard** |
| Applebot-Extended | no | **`User-agent: *` wildcard** |

All nine appear in `robots-ai.txt`, but §2 of this same handoff establishes that major crawlers do
not read that file — so for **enforcement**, those six lines are documentation, not policy.

**The curve is safe because of the wildcard, not because those six frozen lines exist.**

Adding explicit groups for them would itself be a change to citation lines, which this gate
forbids without the Edmaster's word. Restraint over tidiness: they were left alone.

---

## §1 — WHAT WAS ALREADY RIGHT (not rebuilt)

```
✓ robots.txt          per-bot AI policy + sitemap autodiscovery
✓ robots-ai.txt       citation-vs-training split, attribution, discovery pointers
✓ _headers            X-Robots-Tag noindex on /content/ + /api/, CDN s-maxage, CORS
✓ .well-known/ai-info.json   full AI policy, discovery map, facet-layer schema
✓ llms.txt / llms-full.txt   120 KB map + 809 KB full dump
✓ /content/{slug}.md         markdown mirrors, fr+en, 8-heading facet structure
✓ /api/lieu/{slug}.json      machine facet tree
```

The enforceable-header move was **already** done by `_headers`. An earlier draft claimed it was
missing; that claim was retracted before work started.

---

## §2 — THE DEFECT THAT WAS FIXED

**Inverted logic in the GPTBot policy, and a file-split that hid it.**

`robots-ai.txt` guarded GPTBot with `Disallow: /content/`, commented as "deny training while still
allowing live citation via HTML". Two problems:

**(a) The reasoning was inverted.** GPTBot is the *training* crawler. Citation runs through
OAI-SearchBot / ChatGPT-User. Allowing citation was never GPTBot's job — the exclusion denies a
training slice, a valid goal, but not what the comment said.

**(b) The rule lived only in `robots-ai.txt`, which no major bot reads.** GPTBot reads
`robots.txt`, where its block was a blanket `Allow: /`. **The enforced policy was: GPTBot may
train on everything.** The nuance was written in a file GPTBot never fetches.

Mitigating: `/content/*` already carried `X-Robots-Tag: noindex`, an *indexing* directive, not a
*training* one — so the exposure was "GPTBot may train on markdown", not "content is leaking".

---

## §3 — JOBS AS DELIVERED

| job | what shipped |
|---|---|
| **A** | `robots.txt` GPTBot block gains `Disallow: /content/` + `Disallow: /api/`, both slash-terminated; inverted comment replaced with the corrected rationale |
| **B** | `robots-ai.txt` self-labels supplementary/non-authoritative; its GPTBot block mirrors `robots.txt` exactly (it had been missing `/api/`), so the two files cannot disagree |
| **C** | `scripts/build_security_txt.py` wired into `build_all.py`; RFC 9116 file with build-computed `Expires` |
| **D** | `ai-info.json` lists `security_txt`; landed after A so `training_allowed: false` is matched by enforcement rather than asserted |

**⚑ Why the trailing slash is mandatory.** robots.txt matching is **prefix**, not path-segment.
Bare `/content` would also match a future `/content-hub/` or `/contenthub.html`. Dormant today
(`content/` is a real directory, no lieu slug begins "content"), but the day someone ships a
`/content-hub/` intent page, a slashless rule silently denies GPTBot a public HTML page.

**⚑ Why `Expires` is floored to midnight UTC.** The draft formula
`datetime.now(timezone.utc) + timedelta(days=364)` carries the current time of day, so two builds
a minute apart emit different bytes — failing this handoff's own *"second build byte-identical"*
gate. Flooring `now` to `00:00:00Z` first makes the output stable for the whole UTC day while
still refreshing daily. **Ratified as the reference implementation; a raw `now()` timestamp is a
defect.** A hardcoded date is worse still: correct the day it is typed, invalid forever after.

---

## §4 — STANDING RULE (recorded, permanent)

> **Never narrow `User-agent: *` in `robots.txt` without re-checking the citation bots.**

Six citation agents — including OAI-SearchBot and ChatGPT-User, the two that cite for ChatGPT —
have **no dedicated group** and depend entirely on the wildcard. Narrowing it would silently cut
them off the curve. Any edit to the `*` group is curve-adjacent and inherits the §0 gate.

A warning comment now sits directly above the wildcard in `robots.txt` so the next editor sees it
without reading this file.

---

## §5 — WATCH-LIST, EXPLICITLY NOT BUILT

| thing | why not now |
|---|---|
| **WebMCP** | exposes callable *actions*; a static directory has none. Revisit if live availability/booking arrives. |
| **ACP** (Agentic Commerce Protocol) | agent-driven checkout; nothing is sold here. |
| **`ai.txt`** | competing proposal, near-zero adoption, overlaps `robots-ai.txt`. Another unread file is clutter, not overkill. |
| **per-page `llms.txt` mirrors** | `/content/{slug}.md` already exists; duplicating is the anti-pattern the specs warn against. |

**The doctrine:** overkill that ships a standardised, consumed, or genuinely-additive artifact —
not a speculative file bots ignore.

---

## §6 — GATES (all passed)

```
gate_protected_placements       before AND after      ✓
gate_render_verified                                  ✓
robots.txt syntax valid                               ✓
§0 citation-bot diff EMPTY      ← the curve gate      ✓ 0 directives changed vs 89c1597
.well-known/security.txt present                      ✓
security.txt Expires is FUTURE  build-generated       ✓ 2027-07-24T00:00:00.000Z, 363 days out
robots Disallow slash-terminated                      ✓ /content/ + /api/, both files
ai-info.json valid JSON                               ✓
second build byte-identical                           ✓
sitemap unchanged (6042)        ← CORRECTED (C-1)     ✓
```

**⚑ CORRECTED (C-1).** The draft asserted `sitemap unchanged (5982)`. The true count at
`89c1597` was **6042**, and it is still 6042 post-build. The draft figure was stale — not a
regression.

---

## §7 — PR HYGIENE NOTE

PR #69 carried both the photo work and this lineup. Harmless here — heroes and robots do not
interact, so reverting one could not corrupt the other. **Standing habit going forward: keep
curve-adjacent changes (robots / headers / AI-discovery) on their own PR**, so a content rollback
can never drag a robots change with it.

---

## §8 — WHAT TO RUN, FREE, AFTER MERGE

**Chrome Lighthouse → Agentic Browsing audit** (v13.3+). Not a file, a *test*. Run it on
`loisirs74.fr`: it checks llms.txt presence, layout stability, agent accessibility. Google's own
definition of "agent-ready", costs nothing, and it measures the overkill rather than just shipping
it. **Not yet run.**

---

## §9 — HONEST SIZING

This moved no rankings and, by design, did not move the citation curve. Its job was to make the
curve **safe and defensible**: the training-deny became real, the two robots files stopped
contradicting each other, one genuine IETF standard was added, and the AI-policy declaration
finally matches enforcement.

**This handoff built the fence, not the beast.** The beast eats from the wildcard and the static
HTML, and is already breaking its own records nightly.

---

© 2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés 🦆
