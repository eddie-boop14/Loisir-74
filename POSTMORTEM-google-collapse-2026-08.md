# POST-MORTEM — loisirs74.fr loses 96% of Google in one day

**Written:** 2026-08-31 · **Status:** cause identified with high confidence, fix shipped, recovery unverified
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
- **Indexing:** 5,366 pages in the index and *rising* through Aug 21. The HTTPS report — the freshest Google data available, running to **Aug 30** — shows **0 problems** and validated pages climbing (579 → 687) straight through the crash. Google never disengaged.

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

### 5.2 Everything else shipped in the same window

| change | why |
|---|---|
| Tier classifier rewritten | bare `fond` read "Fonderie" as cross-country ski; `(16-75 ans)` read as senior; "Moins de 3 ans" priced as Adult in six languages. 40 of 515 labels reclassified. |
| 58 Wikimedia heroes self-hosted | analytics put every poor-LCP element on hotlinked heroes (11.0 s on the Seythenex cascade). LCP "good" 94% → **96%**. |
| `lastmod` manifest repaired | CI had been red since **Aug 18** — the Abbaye d'Abondance fiche shipped without a manifest entry. Also refreshed 87 stale dates. |
| loisirs73 analytics | every page shipped a Cloudflare beacon with an **empty token** — cost with no data. |

### 5.3 Mistakes made during this investigation

Recorded because a post-mortem that only documents the system is half a post-mortem.

1. **Diagnosed seasonality with too much confidence** and told the publisher there was nothing to fix. Their instinct that something was wrong was right, twice, before the evidence was.
2. **Walked past the smoking gun on the 73.** The revert commit `c9d4d3f0` was printed in the first commit listing, read as "a redirect issue, already fixed", and never opened. It was the cause. The mistake was anchoring on same-day causation and not considering a multi-day lag.
3. **Pushed to `main` without checking CI**, which had been red since Aug 18.
4. **Broke CI with the first sponsored-link commit** — the marking pass ran *after* the byte-comparison gates, so the card-diff gate compared an unmarked card against a marked snapshot and failed all 12 slug × locale pairs, each off by exactly 19 bytes (`" sponsored nofollow"`). Fixed by moving the pass before the gates.
5. **Shipped 1,050+ wrongly-nofollowed internal links.** The structural rule swept up the invite card's own CTA to `/devenir-partenaire`, written as an absolute URL. Nofollowing internal navigation is strictly worse than doing nothing. Fixed with a self-host guard shared by the pass and the gate.
6. **Clobbered a divergent engine file.** Copying the 74's `siteconfig.py` onto the 73 silently dropped `SISTER_PROXIMITY_KM` and `BBOX`, wiping sister cards from 830 pages. Caught in diff review before pushing; restored and patched surgically.

---

## 6 · WHAT IS STILL OPEN

- **Causation is unproven.** The link footprint is the only mechanism found that explains the Google/Bing divergence, and it is a real policy violation that had to be fixed regardless — but it remains correlational until rankings move. **Position is the metric to watch**, not impressions: if it climbs from 37 back toward 10, this was it.
- ~~**Googlebot sees most of the page at opacity 0.**~~ **FIXED 2026-08-31.** The reveal is now motion-only: `transform` still slides content in, `opacity` is never animated. Measured in headless Chromium, JS on, no scroll: 39 of 45 blocks hidden → **0**. Original finding kept below for the record.
  -  39 of 45 content blocks sit at `opacity: 0` for a JS-rendering client that does not scroll. W3 fixed this for non-rendering AI fetchers only; Googlebot renders JS, stamps `html.js`, and the no-JS escape switches off. **Pre-existing — identical before W3/W4, so not the cause** — but arguably the more consequential half of the problem.
- **11 commune pages unreachable — PARTLY ADDRESSED 2026-08-31.** The 132 shadowed URLs no longer appear in the sitemap (6,210 → 6,078), so we have stopped telling Google to crawl a redirect. The underlying routing problem stands: `chamonix-mont-blanc`, `chatel`, `combloux`, `la-clusaz`, `le-grand-bornand`, `les-gets`, `les-houches`, `megeve`, `morzine`, `saint-gervais-les-bains`, `samoens` exist as both a flat station page and a commune directory. Netlify lets the flat file win, so every commune directory 301s to its station page — 11 × 12 locales = **132 pages of distinct content Google can never fetch**, with both URLs advertised in the sitemap.
- ~~**A phantom `SearchAction`.**~~ **FIXED 2026-08-31** — removed from all 10 homepages that carried it; JSON-LD re-parses everywhere.
  - Original: All 12 homepages declare a sitelinks searchbox pointing at `/?q={search_term_string}`. There is no search on the site.
- **The sitewide cross-link exchange — CUT 2026-08-31.** ~10,440 followed footer links into loisirs73.fr, reciprocated 1,692 times. Sitewide + reciprocal + same owner is an excessive link exchange with structurally zero upside: PageRank between two sites one person owns cannot make either rank. Footer line off; homepage card and 30 km proximity cards kept with `rel=nofollow`. 74: 10,464 anchors → 24. 73: 3,072 → 1,380. `gate_cross_site_links.py` added on both.
- **Apidae card removal deferred, deliberately.** Nofollowing already takes the link risk to zero; deleting the cards buys no further protection and would change 2,000 pages while we are trying to read whether the fix worked. One variable at a time.

---

## 7 · THE SISTER INCIDENT — loisirs73.fr, Aug 24, DIFFERENT CAUSE

Worth recording because the two collapses looked identical and were not.

loisirs73.fr launched Aug 10, ramped to 550–880 impressions/day, and crashed on **Aug 24** to 26 impressions with position going 14.5 → 50.7 → 61.6 → 80.7.

The cause is documented in the repo's own gate, written after the fact:

> On 2026-08-19, 816 rules of the first shape shipped with all 33 gates green and **took every fiche on loisirs73.fr off the internet — 129 lieux × 12 locales, ERR_TOO_MANY_REDIRECTS, on the canonical URL as much as the phantom.**

Trailing-slash collapse rules were added at **09:08** and reverted at **22:28** — **13 hours 20 minutes** during which roughly 1,548 pages served infinite redirect loops. Netlify matches paths regardless of trailing slash, so `/x/ → /x` is a rule pointing at itself. Googlebot crawled during the window; the index reflected it five days later.

**The 73 has no promotional link problem at all** — zero partner cards, and its outbound links are editorial citations that must keep their vote. Two sites, two unrelated causes, three days apart.

---

## 8 · GUARDS ADDED SO THIS CLASS OF FAILURE FAILS LOUDLY

| gate | catches |
|---|---|
| `gate_sponsored_links.py` | any promotional link shipping able to pass PageRank |
| `gate_redirect_selfloop.py` (73) | a redirect rule pointing at itself modulo a trailing slash |

Both are read-only, both are wired into CI on the repo they protect. The sponsored gate shares its detection with the marking pass by import.

The common property of both incidents is worth stating plainly: **the page looked perfect, every existing gate was green, and Search Console reported no problem.** Failures this quiet have to be made loud in CI, because nothing outside the build will tell you.

---

*Written after the fact from git history, GSC and Bing exports, Cloudflare analytics, and live testing. Numbers are as measured; where causation is inferred rather than proven, it says so.*
