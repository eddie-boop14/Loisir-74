# Translation lane policy — HANDOFF-37 (permanent)

**The lane, per language (ja · ar · he · pl):**

| tier | engine | cost | when |
|---|---|---|---|
| base | argostranslate (local MT, offline) | **$0** | always — claims the land |
| patch | claude-haiku-4-5 batch, **flagged segments only** | ≤ **$2/lang** hard cap | flags exist + Eddie saw the contract |
| upgrade | Haiku full re-run (~$7) or Sonnet (~$20) of body prose | per contract | **upgrade-on-evidence only** (below) |

**Ship gate per language:** Layer-A render assertions + Layer-B comprehension on
rendered samples (mandatory for ja/ar/he). PASS → publish rich + IndexNow click.
FAIL → the language HOLDS on strict-facts (never ships scrambled) until the paid
full lane is approved.

**Upgrade-on-evidence (permanent):** per language, after **3–4 weeks of GSC**:
- real impressions → optional Haiku/Sonnet re-run of body prose for fluency
  (dry-run contract + Eddie's go, as ever);
- no demand → the $0 version keeps the land claimed. **Money chases proof.**

GSC reads are Eddie's; no cron, no automation ever. Machine-grade prose is
acceptable; scrambled never (Edmaster's bar, standing).

**Scripted proofreading (what "flagged" means):** a segment is held back when
the MT engine mangled a frozen-name placeholder, changed the digit multiset
(prices/times/dates), blew the length ratio, or returned empty. Held fields
stay ABSENT (null discipline, facts-fallback renders) and live with their full
segment tables in `reports/translate-local-flags-<lang>.json` until patched.
