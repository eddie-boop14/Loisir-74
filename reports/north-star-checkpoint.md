# 🧭 North-Star checkpoint — does the multilingual bet earn clicks?

_© 2026 · Bleu canard édition · set 2026-06-30 · **answer ~2026-07-21**_

> Ship toward rankings, not polish. The machine (verify→gate→router) is real and built.
> Before pouring more language engineering in, we answer ONE question with evidence.

## The question
**Did the Latin pilot (pl / pt / cs) earn clicks?**

## The pilot under test
- 60 staged pages: `pl/`, `pt/`, `cs/` × 20 marquee fiches (Mont-Blanc / Chamonix / Annecy / Évian / Megève).
- Facts-first, vocab-verified labels (pl/pt: ai-consensus-3×; cs: ai-consensus-3× after the surveillance fix).
- Currently **noindex + absent from sitemap/hreflang** (staged, zero blast radius on the live 6 langs).

## ✅ The clock-starting flip — DONE (HANDOFF-11)
The 60 pilot pages are now **indexable**: `index,follow` + self-canonical, listed in `sitemap.xml`
(own URLs only), deployed to `_site` — and kept **OUT of the 6 live languages' hreflang clusters**
(grep-proven 0 leaks). Reproducible from the renderer's `INDEXABLE` flag; the 6 are byte-untouched.

- **Clock starts: at the MERGE of the flip PR (#15).** Expected ~2026-06-30.
- **GSC read date: merge-date + 21 days** (≈ **2026-07-21** if merged ~2026-06-30; adjust if the merge slips).

## The decision gate — answer ~2026-07-21
Pull GSC for the pl/pt/cs pilot URLs: **impressions · average position · clicks**.

- **YES (it ranks / clicks):** the multilingual bet is validated →
  - **Phase C (RTL engine for ar/he) becomes a confident go**, with the native spot-check lined up.
  - **Scale-flip pl/pt/cs** into sitemap + hreflang + the full corpus (daylight, reviewed).
- **NO (flat):** do **not** build the RTL engine yet. Diagnose first on the cheap 60 pages —
  render? hreflang? real demand? pilot too thin? Better to learn it here than after the RTL build.

## Priority order until the verdict exists
1. **Baignade cluster** — ✅ already live on main (hub + Plages-voisines mesh + L'essentiel; the #1 GSC move).
2. **Combloux un-defer** — ✅ already live on main (riding the biotope breakout, #1 page by impressions).
3. **Pilot ranking watch** — the open item; this checkpoint.
4. **Everything multilingual after** — Phase C does NOT start before the 2026-07-21 verdict.

*The machine is real. Now it has to win. The pilot's GSC result is the next milestone — not the next language.* 🦆
