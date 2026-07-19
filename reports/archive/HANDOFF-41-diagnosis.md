# HANDOFF-41 — Diagnosis: why ja · ar · he are not rich (pl is)

**Attested live main FIRST:** remote `origin/eddie-boop14/Loisir-74` · branch `main` ·
HEAD `e505f676eab9aab1299d29b29d19dd6c881aa1a5`. Working branch `claude/new-session-eua199`
is even with that SHA.

**Grep-the-SHA verdict (per the charter — never trust a handoff's "done"):**

| lang | fiches with `i18n.<lang>.body` > 200 chars | avg body chars / fiche | verdict |
|------|---:|---:|---|
| fr (source) | 397 / 397 | 1940 | complete |
| en · de · es | 389 / 397 | ~1950 | complete (8 non-content pages) |
| **pl** | **362 / 397** | **1197** | **RICH ✅ (the reference)** |
| **ja** | **45 / 397** | **77** | **EMPTY — body absent on 352 fiches** |
| **ar** | **2 / 397** | **6** | **EMPTY — body absent on 395 fiches** |
| **he** | **281 / 397** | **706** | **SHIPPED BUT SCRAMBLED — see below** |

Correction to the handoff premise: the ja/ar/he HTML **trees are rendered** (441 pages
each). They are thin because the JSON `body` is absent/garbled, not because the render step
skipped the tree. The gap is **translation quality**, not merge/render.

## Root cause (one engine explains all three)

ja/ar/he were run through the **`$0 local MT lane`** (`scripts/translate_local.py`,
engine `argostranslate` en→X, offline, no API) on 2026-07-04 — HANDOFF-37 commits
`d9fe497` (he), `4610c4e` (ja), `7f74125` (ar). They were **never** sent through the
**paid LLM batch** that produced pl's rich prose. Confirmed: `reports/translate-batch-state.json`
holds state only for `pt`, `cs`, `pl` — there is **no batch entry for ja/ar/he**.

argostranslate is not good enough for this content. The scripted validators (frozen-noun
masking, HTML tag census, digit parity, length ratio) are **structural**, not semantic —
they catch a lost `<strong>` or a mangled number, but they pass fluent-looking garbage.
Per-language, that produced three different failure modes:

### ja — held empty (correct null discipline)
argos output failed the validators on most fields: `"output not in target script
(untranslated)"` and `frozen noun lost: "Abbaye d'Aulps" / "Saint-Jean-d'Aulps"`. Flagged
fields stay **ABSENT** by design (`reports/translate-local-flags-ja.json`, 2897 field
records). Nothing garbled shipped — but nothing rich landed either. **The paid patch tier
that would rescue the flagged segments was never submitted.**

### ar — held empty, and one $2 cap can't finish it (correct null discipline)
The flags note is explicit: *"BASE TIER FAILED Layer-B for ar (factual unit corruption in
surviving segments, e.g. 1300 m → '1300 miles'; most output not target-script). Every field
routed to the LLM tiers."* Correctly held (only 2 fiches have any body). The rescue LLM
tier was never run. Note the scale problem below — ar needs more than one $2 pass.

### he — SCRAMBLED CONTENT IS LIVE ON MAIN (the one active correctness problem)
Unlike ja/ar, he's argos output passed the *structural* gates on 281 fiches and **shipped**.
It is garbled on **100% of those 281 fiches**: literal `The The The <strong>…`, untranslated
English runs (`abbey לשעבר Cistercian`), currency corruption (`3.5 $` for `€3.50`). Sample:

> `<p>The The The <strong>Abbaye d'Aulps</strong> (או ABye Sainte-Marie d'Aulps) הוא abbey
> לשעבר Cistercian ממוקם בגובה 807 מ' בעמק Chablais…`

This violates the PROTECTED "never ship scrambled" rule. Because these fields are *populated*
(not flagged), the cheap patch tier will **not** touch them — landing he correctly needs the
garbled fields purged first (so they go absent → flagged → patched) or a full re-translation.

## Job 1 — the $0 patch contracts (run today; no API call, no charge)

`translate_local.py --lang <l> --patch-dry-run`:

| lang | flagged segments | est. tokens (in / out) | est. cost | fits $2 cap? |
|------|---:|---|---:|---|
| ja | 5,693 | ~865.6k / ~457.6k | **~$1.58** | yes |
| he | 1,810 | ~292.5k / ~177.5k | **~$0.59** | yes — **but see caveat** |
| ar | 11,460 (of 21,863 needed) | ~1496.1k / ~500.7k | **~$2.00** | **partial — defers 10,403 segments** |

Caveats that change the money decision:
- **ar** cannot fully land under one $2 cap: full need ≈ **$3.77**. One submit patches the
  11,460 highest-priority segments and leaves 10,403 absent+flagged. Landing ar rich means
  **either raising the cap to ~$4, or two $2 passes**.
- **he's $0.59 is misleading**: it only re-does the 1,810 *flagged* segments. The 281 *shipped
  garbled* bodies are not in that set and would remain garbage. Real cost to make he rich =
  purge the bad populated fields, then patch the resulting (much larger) flagged set — closer
  to ja's order of magnitude, not $0.59.

## Decisions that are Eddie's, not the bot's (money + scope gate)

`--patch-submit` spends real money and the code + handoff both reserve it for Eddie's explicit
go ("Eddie sees the bill first"). Not fired autonomously. Awaiting decision on:

1. **ja** — approve the ~$1.58 Haiku patch submit? (cleanest of the three; held-empty, will
   land rich in one pass.)
2. **he** — approve purge-then-repatch (recommended — stops shipping scrambled), **or** hold
   he empty now (remove the 281 garbled bodies) as an interim fix while awaiting budget?
   Leaving the garble live keeps violating "never ship scrambled".
3. **ar** — raise the per-lang cap to ~$4 for a single full pass, or authorize two $2 passes?

After a lang's patch lands: Layer-B comprehension on rendered samples (mandatory ja/ar/he),
RTL `<bdi>` re-verify at 441-page scale for ar/he, facet md/json regen, IndexNow (scope=lang),
then AXIS mode=baseline re-lock on the complete 12/12 lattice.

*Diagnosis complete. The lattice is 11/12: pl rich; ja/ar held empty (never paid-patched);
he shipping scrambled (needs purge+patch). No silent re-run — the bill is Eddie's to approve.* 🦆
