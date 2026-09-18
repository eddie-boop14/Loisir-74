# POST-MORTEM — loisirs74.fr loses 96% of Google in one day

**Written:** 2026-08-31 · **Last updated:** 2026-09-18 (§2.5 corrected: 610 pages left the index on 5 Sept)
**Status:** most-likely cause identified and fixed; causation inferred, not proven; **no recovery after three weeks** — position flat at ~45 (was 10.7), and 610 pages left the index on 5 Sept
**Sister incident:** loisirs73.fr collapsed three days earlier, *different cause*, documented in §7

---

## 1 · WHAT HAPPENED

On **27 August 2026** loisirs74.fr fell off Google. Not gradually — in a day.

| date | impressions | clicks | avg. position |
|---|---|---|---|
| Aug 23 | 5,505 | 103 | 9.3 |
| Aug 24 | 4,702 | 83 | 9.6 |
| Aug 25 | 5,082 | 90 | 10.1 |
| **Aug 26** | **5,095** | **90** | **10.7** ← last normal day |
| **Aug 27** | **210** | **3** | **29.4** |
| Aug 28 | 143 | 5 | 33.8 |
| Aug 29 | 178 | 2 | **37.5** |

Google AI citations fell with it: ~600/day → **11**. The live 24-hour view on Aug 31 read **66 impressions**.

The worst detail is not the size of the drop. It is that **average position kept degrading for three consecutive days** — 10.7 → 29.4 → 33.8 → 37.5. It had not bottomed out.

The site had been stable at position ~9–10 for three months, growing from 64 impressions/day in late May to a peak of **8,106 on Aug 9**.

---

## 2 · WHERE WE LOOKED, AND WHAT EACH TEST KILLED

This is recorded in the order it happened, mistakes included, because the order is the lesson.

### 2.1 Seasonality — **wrong, and stated too confidently**

The first read was end-of-summer demand decay: the site sells Alpine leisure, French holidays were ending, and impressions had softened from the Aug 9 peak with **position holding at 9.0–10.1**. Falling impressions with flat rank genuinely does mean falling demand.

That analysis was correct *for Aug 9–25* and was then wrongly extended over the Aug 27 cliff. **Seasonality cannot move average position 19 places overnight.** The moment the Aug 26–27 data arrived, the seasonality story was dead and should have been dropped immediately.

### 2.2 GSC data latency — **ruled out by an overlap check**

A collapse on the *last day of an export* is usually incomplete data. Tested properly: re-export and compare the days both files share.

```
Aug 21  old=4643 pos 10.5   new=4643 pos 10.5   IDENTICAL
Aug 22  old=4839 pos  9.8   new=4839 pos  9.8   IDENTICAL
…all five overlapping days identical, and Aug 27 stayed at 210 in later pulls
```

Finalised days were byte-identical, and the cliff persisted across three subsequent exports. Real.

### 2.3 Our own deployment — **audited, then exonerated by evidence**

A merge to `main` landed **Aug 26**, one day before the cliff. That is exactly the correlation you must not wave away because it is inconvenient.

Audited: all 58 self-hosted hero images return 200, every page type returns 200, `robots.txt` allows all, fiches carry `index,follow` with correct self-canonicals. Nothing broken. But self-certification is not evidence — §3 is what actually cleared it.

### 2.4 The POA "citation layer" (W3 + W4, shipped Aug 21) — **audited four ways, clean**

W3 made `.reveal` content visible without JavaScript; W4 moved a critical CSS copy into `<head>` and pushed the full sheet plus the JSON-LD to end-of-`<body>`. Both landed six days before the cliff and touched every page — a strong suspect.

1. **Rendered output.** The pilot page was pulled at three points (before W3/W4, after W4, live) and rendered in headless Chromium with JS on and off. All three identical: 45 `.reveal` elements, 39 at opacity ~0, 11,311 characters of text. The only difference was the intended `html.js` class stamp.
2. **Metadata across 40 sampled pages.** Title, description, canonical, robots, h1, JSON-LD count, hreflang count — **zero** differences across the W4 commit.
3. **Structured data.** 34/35 sampled pages parse clean; types intact (`WebSite`, `BreadcrumbList`, `TouristAttraction`, `FAQPage`). The lone failure is `studio.html`, noindex and robots-disallowed.
4. **Charset.** Commune pages declare `<meta charset>` at byte 1282, past the 1024 limit — but it was **already at 1220 before W3**, and Netlify sends `charset=UTF-8` in the HTTP header, which takes precedence.

Verdict: not the cause. One pre-existing finding surfaced and remains open — see §6.

### 2.5 Technical surface — **all clean**

- `robots.txt`: `User-agent: * / Allow: /`. Only thank-you pages, studio internals, and GPTBot-scoped training paths are disallowed.
- Googlebot fetches every runtime script (`duck.js`, `nearme.js`, `l74sort.js`) with **200**. No `Disallow` touches `/scripts/`, CSS, or any content directory. CSS is inline.
- **Cloaking test:** both sites return **byte-identical** responses to a Googlebot user-agent and to a browser, on the homepage and `robots.txt`.
- **Manual actions:** *Aucun problème détecté* on both properties.
- **Indexing:** 5,366 pages in the index and *rising* through Aug 21. The HTTPS report — running to **Aug 30** — shows **0 problems** and validated pages climbing (579 → 687) straight through the crash. Google never disengaged.
- **Deindexing — ruled out for the crash itself, then it happened anyway nine days later.**
  This entry said "ruled out outright" from 2 Sept until 18 Sept. That was true of the
  window it described and false about the site by the time anyone read it again. Both
  halves are kept here, in order, because the correction is the finding.

  **What the crash looked like** (coverage export of 2 Sept, the first whose data reaches
  the crash days; coverage lags ~5 days, so its last row is Aug 28):

  | date | indexed | not indexed | impressions |
  |---|---|---|---|
  | Aug 21 | 5,366 | 894 | 4,643 |
  | Aug 26 | 5,387 | 906 | 5,095 |
  | **Aug 27** | **5,387** | 906 | **210** |
  | **Aug 28** | **5,387** | 906 | **143** |

  On Aug 28, with traffic down 97%, Google still held **5,387 pages — flat, and 21 higher
  than a week earlier.** Every issue bucket moved by noise or improved (404s 59 → 55;
  "duplicate, Google chose a different canonical" 1 → 0; noindex flat at 16, all
  deliberate — thank-you pages, CGV, `signaler-info`, `studio`). The collapse itself was a
  **demotion, not a removal**: Google kept every page, kept reading them, stopped serving
  them. That is the signature of algorithmic ranking enforcement rather than a technical
  fault, and it corroborates §3 independently of Bing. **That part still stands.**

  **What happened on 5 September** (coverage export of 18 Sept):

  | date | indexed | not indexed |
  |---|---|---|
  | Sep 4 | 5,441 | 898 |
  | **Sep 5** | **4,831** | **1,547** |

  **610 pages left the index in a single day**, and one bucket absorbed them:
  *Explorée, actuellement non indexée* went **289 → 909 (+620)** while everything else
  stayed flat (canonical 128, noindex 16, redirect errors 8, duplicates 2; redirects
  403 → 438, 404s 52 → 46). So the demotion held for five weeks and then turned into a
  removal — five days after the link fixes shipped, which is close enough to invite a
  causal reading and not close enough to support one.

  **Which pages.** The drilldown for that exact bucket, pulled 14 Sept, is almost entirely
  the non-French trees — `/pt/abbaye-de-sixt`, `/pt/trilhos/`, `/ar/stelsia-casino-megeve`,
  `/pl/co-robic/leman-cote-francais/`, `/de/was-unternehmen/…`, `/en/croisiere-cgn-evian`.
  That sample was taken when the bucket held 288 rows; the 620 that fell afterwards are
  *inferred* to be more of the same and a fresh drilldown would settle it. If the
  inference holds, the verdict is not a penalty but an assessment: **435 venues rendered
  into 12 locales is not, to Google, 6,254 pages of value.**

  **The lesson about this document, not about the site:** a post-mortem written while the
  incident is still running states findings with a shelf life. "Ruled out outright" was
  the strongest claim in §2, and it aged out in thirteen days. Anything here that rests on
  a bounded observation window should be read with its date attached.

---

## 3 · THE TEST THAT BROKE IT OPEN: BING

Bing Webmaster Tools covers the same site, same HTML, same crawl access, same days.

| | Aug 21–26 avg | Aug 27–29 avg | change |
|---|---|---|---|
| **Google impressions** | 4,978/day | 177/day | **−96%** |
| **Bing impressions** | 436/day | 418/day | **−4%** (noise) |

On Aug 27 — the exact day Google collapsed — Bing recorded **431 impressions**, dead on its own trend. Aug 28: 496. Aug 29: 328. Bing AI citations dipped modestly (124/135/126 → 74/54/94) and stayed inside a range that had swung from 9 to 166 all month.

**If anything were broken — markup, rendering, redirects, structured data, the Aug 26 deploy — Bing would have seen it too.** It didn't.

That single comparison eliminated every technical hypothesis at once and reframed the question from *"what did we break?"* to *"what does Google enforce that Bing does not?"*

---

## 3bis · CLOUDFLARE: THE DASHBOARD THAT LIED, AND THE REAL-USER CONFIRMATION

Cloudflare Web Analytics deserves its own section because it did two jobs, and
the first one nearly hid the problem.

### It lied by omission — a bot flood masked the drop

The headline barely moved: 4.73k page views (Aug 4–25) → 4.65k (Aug 16–30).
Flat. Except the composition had inverted completely:

| | Aug 4–25 | Aug 16–30 |
|---|---|---|
| China | 400 | **2,650** |
| "Unknown" browser | 520 | **2,610** |
| Desktop / Mobile | 1,410 / 3,250 | **3,220 / 1,380** ⟵ inverted |
| Direct / Google | 1,040 / 2,560 | **2,970 / 1,060** |

The new window was *shorter* (14 days vs 21) yet China went 400 → 2,650, with
page views exactly equal to visits — **1.00 pages per visit**, Unknown browser,
Unknown OS, Desktop, arriving direct or from `m.baidu.com`. A scraper, not
people. It is still running: in the Aug 28–31 window it walked
`/devenir-partenaire` across every locale.

**Read the headline and you would conclude nothing happened.** Strip the bots
and human traffic had already fallen a third before the cliff even landed. Any
future reading of this dashboard has to be France-first; the totals are noise.

### Then it confirmed the collapse in real visits, not impressions

GSC measures impressions. Cloudflare measures humans arriving. They agree:

| window | Google referrals/day | France page views/day |
|---|---|---|
| Aug 4–25 | 122 | 135 |
| Aug 16–30 | 76 | 91 |
| Aug 24–31 | 38 | 56 |
| **Aug 28–31** | **4** | **31** |

**Google referrals −97%. Real French page views −77%.** Independent of Search
Console, on different infrastructure, measuring a different thing. The collapse
is not a reporting artefact in any dataset.

### What it also bought

The first Cloudflare export (Aug 4–25) is what triggered the hero work: its
Core Web Vitals debug view put every poor-LCP element on a hotlinked
`upload.wikimedia.org` hero — 11.0 s on the Seythenex cascade. Self-hosting 58
of them moved LCP "good" from 94% to 96%. That fix came from this data and
nothing else.

---

## 4 · WHAT WE FOUND

### 4.1 A promotional link footprint passing full PageRank

The "À proximité" partner-card module shipped **7,374 outbound links across 2,016 pages to 506 commercial hosts** — hotels, Accor, restaurants, fromageries, activity operators — every one carrying `rel="noopener"` and nothing else.

| tier | cards | distinct hosts | what they are |
|---|---|---|---|
| `featured` | 52 | 2 | the publisher's own two businesses |
| `recommended` | 1,088 | 504 | imported tourism data |

Google's link spam policy asks for promotional links to be qualified with `rel="sponsored"` or `nofollow`. Unqualified at this scale, the pattern reads as a link network. Enforcement is **algorithmic** — SpamBrain devalues the linking site with **no manual action issued**, which is precisely why Search Console stayed green while the site sank.

**And Bing is markedly more tolerant of link patterns than Google.** That is the one mechanism found that explains the divergence in §3.

### 4.2 A false statement in our own codebase

The engine described the two `featured` placements as *"paid, contractual"*. **Nothing on either site is paid.** Those two domains are the publisher's own businesses; the 1,088 `recommended` cards came from a tourism data import. The wording was inherited and wrong, and it distorted the early analysis by framing this as a paid-link problem rather than a promotional-scale problem.

`rel="sponsored"` remains correct regardless: it marks advertising, not only payment, and promoting your own businesses across 426 pages is advertising.

### 4.3 Scope was initially understated by 14×

The first fix used a **domain allowlist** and caught 528 links on 426 pages — the two owned hosts. The actual promotional footprint was **7,374 links on 2,016 pages**. A domain list was the wrong shape of rule.

---

## 5 · WHAT WE DID

### 5.1 The fix — structural, not a list

`scripts/mark_sponsored_links.py`, a derived post-pass modelled on `inject_analytics.py`, marks by **two independent rules**:

1. **Structural** — every `<a>` inside a partner card (`<article|button class="partner…">`), host-agnostic, so a new card cannot escape by using a new domain.
2. **Host** — every `<a>` to a host in `site.config.json → promo_link_domains` (the publisher's own properties), wherever it appears.

A post-pass rather than a template edit because cards are emitted by several builders; a template-by-template fix silently misses the next builder added.

**What is deliberately NOT marked:** the venue's own official site, offices de tourisme, mairies, `patrimoines.savoie.fr`, `reserves-naturelles.org`, `ffrandonnee.fr`, `etalab.gouv.fr`, Wikimedia credits. These are the evidence layer the engine exists to earn and they keep passing their vote. The split is exact — on one page `lac-annecy.com` retains **6 followed links** (fact-source, official-site button) and only its promotional card copy is marked.

`scripts/gate_sponsored_links.py` fails CI if a promotional link ever ships unqualified, and **imports its detection from the marking pass** so check and fix cannot drift.

### 5.2 The four crawl-and-honesty fixes (31 Aug)

Shipped together after the link work, on the reasoning that each is correct on
its own merits whether or not it touches the collapse.

| fix | before | after |
|---|---|---|
| **Reveal opacity trap** | 39 of 45 content blocks at `opacity:0` for a JS-rendering client that never scrolls | **0 of 45.** The reveal is motion-only now — `transform` still slides content in, `opacity` is never animated, so text is visible to any client regardless of scroll |
| **Shadowed sitemap URLs** | 132 directory URLs advertised while 301ing to their station page | dropped; sitemap 6,210 → **6,078** |
| **Phantom `SearchAction`** | 10 homepages declared a sitelinks searchbox for a search that does not exist | removed; JSON-LD re-parses on every file |
| **Cross-link exchange** | 10,464 followed anchors into the sibling (74), 3,072 back (73) | **24** and **1,380**, every one `rel=nofollow`; footer bulk gone, reader-facing cards kept |

The opacity fix is the one worth dwelling on. W3 made content visible to
*non-rendering* AI fetchers, which was half the problem and the less important
half: Googlebot **does** render JS, so it stamped `html.js`, switched the no-JS
escape off, and looked at a page whose blocks were transparent. Six days of
work aimed at machine readers had left the one machine reader that pays the
bills looking at nothing. Measured in headless Chromium, JS on, no scroll.

### 5.3 Everything else shipped in the same window

| change | why |
|---|---|
| Tier classifier rewritten | bare `fond` read "Fonderie" as cross-country ski; `(16-75 ans)` read as senior; "Moins de 3 ans" priced as Adult in six languages. 40 of 515 labels reclassified. |
| 58 Wikimedia heroes self-hosted | Cloudflare CWV put every poor-LCP element on hotlinked heroes (11.0 s on the Seythenex cascade). LCP "good" 94% → **96%**. |
| `lastmod` manifest repaired | CI had been red since **Aug 18** — the Abbaye d'Abondance fiche shipped without a manifest entry. Also refreshed 87 stale dates. |
| loisirs73 analytics | every page shipped a Cloudflare beacon with an **empty token** — cost with no data. |

### 5.4 Mistakes made during this investigation

Recorded because a post-mortem that only documents the system is half a post-mortem.

1. **Diagnosed seasonality with too much confidence** and told the publisher there was nothing to fix. Their instinct that something was wrong was right, twice, before the evidence was.
2. **Walked past the smoking gun on the 73.** The revert commit `c9d4d3f0` was printed in the first commit listing, read as "a redirect issue, already fixed", and never opened. It was the cause. The mistake was anchoring on same-day causation and not considering a multi-day lag.
3. **Pushed to `main` without checking CI**, which had been red since Aug 18.
4. **Broke CI with the first sponsored-link commit** — the marking pass ran *after* the byte-comparison gates, so the card-diff gate compared an unmarked card against a marked snapshot and failed all 12 slug × locale pairs, each off by exactly 19 bytes (`" sponsored nofollow"`). Fixed by moving the pass before the gates.
5. **Shipped 1,050+ wrongly-nofollowed internal links.** The structural rule swept up the invite card's own CTA to `/devenir-partenaire`, written as an absolute URL. Nofollowing internal navigation is strictly worse than doing nothing. Fixed with a self-host guard shared by the pass and the gate.
6. **Understated the promotional scope by 14×.** A domain allowlist caught 528 links; the real footprint was 7,374 across 2,016 pages. A list was the wrong shape of rule — it had to be structural.
7. **Clobbered a divergent engine file — twice.** Copying the 74's `siteconfig.py` onto the 73 dropped `SISTER_PROXIMITY_KM` and `BBOX`, wiping sister cards from 830 pages. Later, copying `build_lieu_page.py` the same way destroyed 236 lines of 73-only code (`_sister_rel_cards`, `modifier_faq`, `full_faq`). Both caught in diff review before pushing. **These two engines have genuinely diverged; copying files between them is not safe and must not be done again.**
8. **Left the Cloudflare evidence out of the first draft of this document.** It had informed two findings and was cited only in the provenance line. Corrected in §3bis after the publisher caught it.
9. **Wrote "deindexing — ruled out outright" into §2.5 while the incident was still running.** It was the strongest claim in §2 and it survived thirteen days: on 5 Sept, 610 pages left the index. The observation was sound for its window (Aug 21–28) and the wording was not — "ruled out" describes a closed question, and this one was open. Corrected in §2.5, which now keeps both halves in order. **The general fault: a finding drawn from a bounded window was stated as a permanent property of the site.** Anything in this document resting on a date range should be read with that range attached.
10. **Suggested Cloudflare Bot Fight Mode for the Chinese scraper.** It needs the domain proxied through Cloudflare. loisirs74.fr resolves on Netlify DNS (`dns1–4.p05.nsone.net` — NS1, which is what Netlify DNS is built on), loisirs73.fr on Namecheap, and even officiallink.org — a Cloudflare *zone* — returns no `cf-ray`, so it is DNS-only too. **None of the three is proxied; the advice was unavailable on all of them.** Cloudflare Web Analytics is a JS beacon and works from any host, which is why the numbers arrive and the blocking does not. The §3bis reading rule (filter Country ≠ China) remains the only real answer.
11. **Diagnosed a Cloudflare zero as a token mismatch without checking the token.** officiallink.org showed 0 page views 8 hours after its Web Analytics site was created; the reasoning — a fresh site entry mints a fresh token while the page keeps the old one — was sound, matched `inject_analytics.py`'s own documented failure mode, and was wrong. The tokens were identical. Installation was clean throughout: no CSP, beacon 200, snippet correctly placed before `</body>`. The actual answer was arithmetic — 8 hours of collection at ~2 visits/day is 0.67 expected visits, so **zero was a coin flip**. A plausible mechanism is not a diagnosis until the cheap check that would refute it has been run.

---

## 6 · WHAT IS STILL OPEN

### 6.0 · Three weeks after the fixes: the verdict so far (18 Sept)

Position was the metric named below, and it has now had three weeks to answer.
It has not.

| | position | impressions | clicks/day |
|---|---|---|---|
| Aug 26 — last normal day | **10.7** | 5,095 | 90 |
| Sep 3 — worst | 63.4 | 300 | 4 |
| **Sep 5–11 mean** | **45.1** (range 40.9–50.5) | ~100 | **~2** |

The fixes stopped the slide — 63.4 back to the forties, held for ten days — and
did not reverse it. **Flat at 45 is the honest reading.** Google AI citations are
flat too, about 11/day against roughly 600 before.

One confound named explicitly, because §2.1 got this wrong twice: impressions
fell 106 → 66 over Sep 7–11, which looks like fresh punishment and is not. Bing
fell 618 → 485 across the same days, and Bing is untouched by any of this. Both
engines declining together is end-of-season demand for a Haute-Savoie leisure
site in mid-September. **The control says it, not the author.**

Bing meanwhile keeps widening the gap: ~9 clicks/day against Google's ~2, ~550
impressions/day against ~100, and an AI-citation record of **372 on 14 Sept**.
Its query base also broadened from one topic to four — Lac Blanc still dominant
at 48% citation share, joined by Aiguille du Midi and the Mont Blanc trains,
**including German-language queries at up to 81.8% share**. Those are the same
`/de/` pages Google dropped from its index on 5 Sept (§2.5). Same corpus, same
week, opposite verdicts from two engines.

**Causation is unproven, and will stay that way.** The promotional-link
footprint is the only mechanism found that explains why Google fell 96% while
Bing moved 4%, and it was a real policy violation that had to be fixed
regardless — but it stays correlational until rankings move, and after three
weeks they have not.

The reason it cannot be proven is structural, and worth stating so nobody
re-opens this expecting a confirmation that does not exist. **Algorithmic
actions are never announced.** A *manual* action — a human reviewer at Google
applying a penalty — produces a Search Console message, an entry in the Manual
Actions report, and a reconsideration request button. An *algorithmic* one
(SpamBrain, the link spam updates, a core update) produces nothing at all: no
message, no flag, no report entry, no indication that any system acted, and no
notification if it lifts. So *Aucun problème détecté* on 31 Aug was true and
uninformative in the same breath — it ruled out a manual action and ruled out
nothing else.

The asymmetry is worth naming because it is backwards from what intuition
expects: **the loud failure mode is the recoverable one.** A manual action comes
with a description of the problem and a human who re-reviews. The silent one has
no description, no appeal, and no confirmation — you change what you believe
caused it and wait. It also means the evidence here is as good as this class of
incident ever gets, not a weak substitute for a proof that was available and
skipped: the link footprint remains the best-supported explanation, and a core
update rolling out at the end of August remains the standing alternative.

**Nothing in Google's tooling would have warned us — before, during, or after.**
The only detection system in play was the owner watching the curve and saying
*something is off, I think I made a fall*. That was the alarm, and it fired
correctly twice before it was believed (§2.1). Any future monitoring has to
assume the same: the graph is the alert, because there is no other.

**The 11 commune pages are still unreachable.** The sitemap no longer advertises
their redirecting URLs, which stops the crawl waste — but the underlying routing
problem stands. `chamonix-mont-blanc`, `chatel`, `combloux`, `la-clusaz`,
`le-grand-bornand`, `les-gets`, `les-houches`, `megeve`, `morzine`,
`saint-gervais-les-bains` and `samoens` each exist as both a flat station page
and a commune directory; Netlify lets the flat file win, so 11 × 12 locales =
**132 pages of distinct content Google can never fetch**. Fixing it means moving
the commune page to a non-colliding path — a URL change, deliberately not taken
mid-incident.

**620 translated pages are out of the index and the decision is yours, not
technical.** §2.5 records the drop. Nothing is broken — Google crawled the
`/pt/`, `/ar/`, `/pl/`, `/de/` and `/en/` pages and judged them not worth
indexing. There are three honest responses and no obviously right one: leave it
(they cost nothing to keep and Bing's AI is citing the German ones at 81.8%
share); thin the roster to the locales that earn (Spain 124 and Italy 110 clicks
in August were real); or deepen the translations so they stop reading as the same
facts twelve times. **Do not decide this from inside the incident** — it is a
product question wearing an SEO costume, and the reassessment is still running.

**4,193 followed links point at parameter URLs.** Every fiche carries a partner
CTA to `/devenir-partenaire?lieu=<slug>` — 4,193 links across 707 pages, no
`rel`, correctly canonicalised so nothing duplicates in the index (they are most
of the 128 in *Autre page avec balise canonique correcte*). Harmless for ranking;
it spends crawl budget on parameter URLs that all resolve to one page, on a site
where 909 real pages sit in *crawled, not indexed*. A `rel="nofollow"` on that
CTA, or moving `lieu` to a fragment, closes it without touching the UX.

**68.4 MB of hero images ship at camera resolution.** 188 hero `.webp`, median
299 KB, the largest **6240×4160 at 3.9 MB**, displayed in a box ~600px wide.
August self-hosted them — which fixed the hotlinking — and shipped the originals.
Cloudflare's 7–14 Sept window puts LCP at 94% good, P75 1,376ms, but every
flagged element is that hero and P99 is **6,804ms**. The markup is already
correct (`fetchpriority="high"`, `aspect-ratio:4/3` reserving space, no lazy
hero), so this is purely file weight: resizing to ~1600px would take 68 MB to
roughly 8–12 MB. Unlike everything else here it has nothing to do with the
reassessment — it is pure user experience, and it is the largest single
performance win available.

**CLS is 23% poor in the field and unreproduced.** Same Cloudflare window:
`#main` shifting 0.19–0.97 and `a.brand` at 0.96 — the latter on *both* sites,
which points at the sticky header. Served the built tree locally and drove
headless Chromium with CPU throttling, latency emulation and a 390px viewport on
two flagged pages: **CLS 0 every time.** That null is not evidence of health —
the hero never became the LCP element under emulation, so the test was not
faithful to the field. Recorded as unexplained rather than dressed up.

**The Apidae cards are still there, deliberately.** Nofollowing already took the
link risk to zero; deleting 1,088 cards buys no further protection and would
change 2,000 pages while we are trying to read whether the link fix worked. One
variable at a time.

**A scraper is still walking the site, and it is accelerating.** Chinese,
`m.baidu.com` and direct, ~1.0 pages per visit. It ran ~243 visits/day over
Aug 28–31; over **Sep 1–2 it was 403 of 450 visits — 90% of everything the
dashboard showed**, with 402 "direct", 385 "Unknown" browser AND "Unknown" OS,
and 96% desktop. Cloudflare Web Analytics is a JS beacon, so headless Chrome
gets counted as traffic.

It is analytics noise and crawl-budget waste, not a ranking problem — but it is
noise loud enough to make the dashboard unreadable, so the reading rule from
§3bis is now permanent: **filter Country ≠ China before reading any total, and
filter Referer = `www.google.com` to compare against GSC.** Nothing else in
that dashboard maps onto a Search Console number.

That comparison, done on the Sep 1–2 window, is itself a confirmation: **Google
sent 4 visits in 24 hours**, against GSC's ~143–210 impressions/day at ~1.77%
CTR = 2.5–3.7 clicks. The two tools agree exactly. In the same window Bing sent
11 and Ecosia (Bing's index) 9 — **20 against Google's 4, a 5:1 inversion** on
an independent measurement, on different infrastructure, from the one in §3.
Cloudflare's Bot Fight Mode would drop most of the scraper if the noise ever
costs more than it does today.

---

## 7 · THE SISTER INCIDENT — loisirs73.fr, Aug 24, DIFFERENT CAUSE

Worth recording because the two collapses looked identical and were not.

loisirs73.fr launched Aug 10, ramped to 550–880 impressions/day, and crashed on **Aug 24** to 26 impressions with position going 14.5 → 50.7 → 61.6 → 80.7.

The cause is documented in the repo's own gate, written after the fact:

> On 2026-08-19, 816 rules of the first shape shipped with all 33 gates green and **took every fiche on loisirs73.fr off the internet — 129 lieux × 12 locales, ERR_TOO_MANY_REDIRECTS, on the canonical URL as much as the phantom.**

Trailing-slash collapse rules were added at **09:08** and reverted at **22:28** — **13 hours 20 minutes** during which roughly 1,548 pages served infinite redirect loops. Netlify matches paths regardless of trailing slash, so `/x/ → /x` is a rule pointing at itself. Googlebot crawled during the window; the index reflected it five days later.

**The 73 was also still hiding its own content, and nobody noticed for four
days.** The `opacity:0` reveal trap (§5.2) was repaired on the 74 on 31 Aug and
not carried across. Measured on the 73's build before the fix: **846 pages
carrying 29,956 `.reveal` blocks and 3,078 `.hammer` word-spans — 33,034 elements
shipping transparent** until an IntersectionObserver fired. On one fiche, 47 of
70. Fixed 4 Sept with the same six-rule change, written against the 73's own
stylesheet rather than copied (see mistake 7), and verified in headless Chromium
with a negative control so the check was known to be able to fail: the pre-fix
page reported 47 hidden of 70 animated, the shipped build 0 of 70.

Found while reading a Cloudflare Web Vitals export about a different metric
entirely. Its CLS figure rested on six page views and was noise; the defect
underneath it was not.

**The 73 has no promotional link problem at all** — zero partner cards, and its outbound links are editorial citations that must keep their vote. Two sites, two unrelated causes, three days apart.

---

## 8 · GUARDS ADDED SO THIS CLASS OF FAILURE FAILS LOUDLY

| gate | catches |
|---|---|
| `gate_sponsored_links.py` | any promotional link shipping able to pass PageRank |
| `gate_cross_site_links.py` (both) | a link to the sibling site shipping able to pass PageRank |
| `gate_redirect_selfloop.py` (**both**, 2 Sept) | a redirect rule pointing at itself modulo a trailing slash |

All three are read-only and wired into CI on the repo they protect. The sponsored gate shares its detection with the marking pass by import, so gate and fix cannot drift.

**The self-loop gate now runs on the 74 as well, which never had the bug.** That is the point: the 74 runs the same platform and the same `_redirects` file, with 552 rules; the only thing it lacked was the guard. A lesson that cost the sister site 1,548 pages should not have to be paid for twice. Its version derives the self-host from `siteconfig.DOMAIN` rather than hardcoding it — the 73's does hardcode, which is the older habit the engine/content split exists to end. It ships with `tests/test_gate_redirect_selfloop.py`, which fires it on the six shapes that cause the loop (including the unforced variant, which only *defers* it) and clears six that must not trip, among them a `loisirs74.fr.evil.com` lookalike host. **A guard written after an incident is worth nothing until it has been shown to fire on the thing that caused it.**

The common property of both incidents is worth stating plainly: **the page looked perfect, every existing gate was green, and Search Console reported no problem.** Failures this quiet have to be made loud in CI, because nothing outside the build will tell you.

---

*Written after the fact from git history, GSC and Bing exports, Cloudflare analytics, and live testing. Numbers are as measured; where causation is inferred rather than proven, it says so.*
