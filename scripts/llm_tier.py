#!/usr/bin/env python3
"""llm_tier.py — the in-session LLM translation lane (HANDOFF-41).

The paid Anthropic Batch lane (translate_local.py --patch-submit) runs only in
the Translate GitHub Action, keyed by the repo secret. When that lane cannot be
reached, this driver lets a capable LLM (the session model / subagents) BE the
translation engine while reusing every guarantee of the local lane:

  * segmentation, HTML-safe splitting and frozen-noun masking are UNCHANGED
    (imported straight from translate_local) — the LLM only ever sees masked
    English text cores and must return them translated, XQV<n>Z tokens verbatim;
  * write-back goes through run_mt(engine=...), so translate_batch.validate()
    (key parity, frozen nouns, tag census, digit/ratio) gates every field
    exactly as the argos/Haiku lanes — a field with any bad segment stays
    ABSENT (null discipline), logged to reports/translate-local-flags-<lang>.json.

Three subcommands, all $0 to the Anthropic Platform (the LLM is the session):

  extract <lang>   collect_unique_masked → scratchpad/segments-<lang>.json
                   (the work-list handed to the translator subagents)
  purge-he         drop the 281 garbled argos he prose fields so they re-enter
                   pairs_for_lang (HANDOFF-41: he shipped scrambled, re-do it)
  apply <lang>     replay scratchpad/cache-<lang>.json {masked: translated}
                   through run_mt → validate + write i18n.<lang> back
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_local as tl          # noqa: E402
import translate_batch as tb          # noqa: E402

# HANDOFF-41: the pipeline's looks_french() short-circuit exists to keep FRENCH
# text out of the argos en→X engine (it would ship French back verbatim). But
# the in-session LLM tier reads French natively, so we DISABLE the short-circuit:
# French source segments are masked, translated, and validated like any other.
# This pulls the ~4,100 FR-source segments/lang (EN-mirrors-FR fiches) into scope.
tl.looks_french = lambda _masked: False

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "scratchpad"
SCRATCH.mkdir(exist_ok=True)

# he prose keys written by the argos lane that must be purged before re-translate
HE_PURGE_FIELDS = ["meta_title", "meta_description", "hero", "hero_alt", "body",
                   "activities", "practical_info", "how_to_get_there",
                   "when_to_visit", "events", "faq", "acces_pmr_detail"]


def cmd_extract(lang):
    pairs = tb.pairs_for_lang(lang)
    communes = tb.all_communes()
    uniq = tl.collect_unique_masked(pairs, communes)
    out = SCRATCH / f"segments-{lang}.json"
    out.write_text(json.dumps(uniq, ensure_ascii=False, indent=0) + "\n",
                   encoding="utf-8")
    n_fields = sum(len(src) for _, src in pairs)
    print(f"[{lang}] {len(pairs)} fiches · {n_fields} missing prose fields · "
          f"{len(uniq)} unique masked segments → {out.name}")


def cmd_purge_he():
    pairs = tb.pairs_for_lang("he", force=True)   # every fiche, populated or not
    purged = 0
    for fiche, _src in pairs:
        blk = (fiche.get("i18n") or {}).get("he") or {}
        present = [f for f in HE_PURGE_FIELDS if f in blk]
        if present:
            tl.purge_fields(fiche, "he", present)
            purged += 1
    print(f"[he] purged garbled argos prose from {purged} fiche(s) "
          f"(fields: {', '.join(HE_PURGE_FIELDS)})")


def cmd_apply(lang):
    cache_file = SCRATCH / f"cache-{lang}.json"
    if not cache_file.exists():
        sys.exit(f"[{lang}] no cache file {cache_file.name} — translate first")
    cache = json.loads(cache_file.read_text(encoding="utf-8"))
    misses = {"n": 0}

    def engine(masked):
        v = cache.get(masked)
        if v is None:
            misses["n"] += 1
            return masked        # miss → English core; fails script check → held
        return v

    tl.run_mt(lang, engine=engine)
    if misses["n"]:
        print(f"[{lang}] WARNING: {misses['n']} segment(s) had no cached "
              f"translation — held as absent (extend the cache and re-apply).")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: llm_tier.py <extract|purge-he|apply> [lang]")
    cmd = sys.argv[1]
    if cmd == "extract":
        cmd_extract(sys.argv[2])
    elif cmd == "purge-he":
        cmd_purge_he()
    elif cmd == "apply":
        cmd_apply(sys.argv[2])
    else:
        sys.exit(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
