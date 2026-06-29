# Overnight worklist — 2026-06-29 (for Edmaster, coffee in hand)

Worked the branches per HANDOFF-NIGHT. One PR per step; nothing live until you merge.
Base `main` HEAD at start: `d25dc54` (pl = ai-consensus-3x, on main).

## PRs to review (in this order)

### PR #9 — i18n Phase A: verify `pt`  ✅ READY TO MERGE
3× blind back-translation + polarity sentinel over all 86 labels. **86/86 3/3 MATCH,
12/12 poles agree, zero escalations.** `reviewed.pt = "ai-consensus-3x-2026-06-29"` +
`review_method`; gate refuses the flag without the clean report. No pt pages render yet.
- Gates: all pass · CI green · report `reports/i18n-verify-pt.{md,json}`.

### PR #10 — i18n Phase A: `cs`  ⏸️ NEEDS YOUR CALL (do NOT merge to publish cs)
Same protocol: 85/86 3/3 MATCH, 12/12 poles agree — **but 1 escalation**, so cs is
NOT auto-passed; `reviewed.cs` stays `false` (cs does not publish).
- **Escalation:** `fact_labels.surveillance` — Czech **"Plavčík"** (= lifeguard, the
  person), verdicts MATCH/UNCERTAIN/MATCH. Matches EN "Lifeguard" but one verifier
  flagged it vs FR "Surveillance" (the service). The fr/en reference itself diverges
  here; `pl` ("Ratownik") and `pt` ("Nadador-salvador") passed the same choice 3/3.
- **Your options:** (a) accept the lifeguard sense → I flip `reviewed.cs` + re-run; or
  (b) prefer a supervision-sense Czech term → I re-translate that one key and re-verify.
- A clean stop, not a guess.

### PR #11 — i18n Phase B: facts-first staged pilot `pl` + `pt`  ✅ READY (after #9)
`build_pilot_langs.py` → 20 marquee pages/lang (Mont-Blanc/Chamonix/Annecy/Évian/Megève),
facts-first (descriptor + commune/price €/Pavillon Bleu/PMR, vocab labels only — no FR
prose, `null` → "not stated"). Frozen FR names verbatim.
- **Red line proven:** noindex; `pl/` `pt/` sit outside every live roster; regenerating
  sitemap+hreflang WITH the pilot present → **0 pl/pt in sitemap, 0 in any hreflang**;
  not copied into `_site`; not wired into `build_all`. Open
  `pl/telepherique-aiguille-du-midi.html` to review.
- Base stacks on PR #9; retargets to `main` after you merge #9.
- The deliberate scale flip (into sitemap/hreflang + full corpus) is yours to make in daylight.

## Parked at the red lines (left for you, as instructed)
- **`ar` / `he`** — not rendered, no RTL publish. RTL engine draft (logical properties +
  mandatory `<bdi>`) NOT started tonight (optional "may"); ready to build on your word.
- **`cs`** — blocked on the one-key adjudication above.

## Flag — GREEN item 3 (baignade cluster) is ALREADY LIVE on `main`
HANDOFF-NIGHT item 3 (baignade hubs + "Plages voisines" mesh + "L'essentiel" blocks)
was already built and merged earlier (`baignade-lac-annecy`, `baignade-leman`,
`ou-se-baigner-haute-savoie`, the mesh + L'essentiel on 26 beach fiches, `gate_baignade_cluster`).
It is **in sitemap + hreflang and indexed** — i.e. already past the "staged" stage the
handoff describes. Nothing to do; noting it so you don't expect a PR. If you'd prefer it
*staged* instead, that's a daytime call — flag me.

## Respected (red lines)
- No sitemap/hreflang flip for any new language. No `ar`/`he` render. No protected fiches
  touched (`chez-nous-a-la-plage`, `chalet-du-tornet`). No scope-creep tidying.

*Goodnight. We started raw bottom, we average alright, we're going heavy loaded.* 🦆
