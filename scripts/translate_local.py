#!/usr/bin/env python3
"""translate_local.py — HANDOFF-37: the $0 translation lane (ja · ar · he · pl).

Local MT (argostranslate, offline, no API key, no per-char billing) with
scripted proofreading. Supersedes the Haiku-default of HANDOFF-36: Haiku 4.5
is the PATCH tier only, on FLAGGED SEGMENTS, never whole fiches.

The lane, per language:
  1. HTML-safe by construction — every prose string is split on tags and
     entities; only text nodes reach MT; reassembly is positional, so tag
     census and key/shape parity hold BY CONSTRUCTION.
  2. Frozen-noun masking — glossary nouns (CORE_FROZEN + every commune + the
     fiche's FR name) and bare URLs become XQV<n>Z placeholders before MT and
     are restored verbatim after. A placeholder the engine mangled or dropped
     FLAGS the segment (never shipped mangled).
  3. Scripted checks per segment — digit multiset parity (rule 4; catches
     numeral conversion), length ratio 0.3–3.0 on segments ≥ 20 chars.
  4. Whole-field validation — the UNCHANGED translate_batch.validate()
     (key parity, frozen nouns, tag census, ratio, empties). A field with any
     flagged segment stays ABSENT (null discipline) and lands, with its full
     segment table, in reports/translate-local-flags-<lang>.json.
  5. Patch tier (PAID, ≤ $2/lang hard cap) — claude-haiku-4-5 Message Batch on
     the flagged segments only; --patch-dry-run prints the contract, Eddie's
     go is the workflow click; the HANDOFF-35 meter + >15% abort apply.

USAGE (manual only — NEVER a cron):
    python3 scripts/translate_local.py --lang pl --dry-run      # counts, $0
    python3 scripts/translate_local.py --lang pl                # the MT run
    python3 scripts/translate_local.py --lang pl --patch-dry-run  # contract
    python3 scripts/translate_local.py --lang pl --patch-submit   # paid, go'd
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_batch as tb  # noqa: E402 — validators/write-back/meter reused

ROOT = Path(__file__).resolve().parent.parent
FLAGS_FILE = ROOT / "reports" / "translate-local-flags-{lang}.json"

MT_LANGS = ["pl", "ja", "ar", "he"]          # en→X argos models all exist
PATCH_MODEL = "claude-haiku-4-5"             # PATCH tier only (HANDOFF-37)
PATCH_IN_PER_MTOK = 0.50                     # batch: 50% off $1.00
PATCH_OUT_PER_MTOK = 2.50                    # batch: 50% off $5.00
PATCH_CAP_USD = 2.00                         # hard per-lang cap, aborts submit
PATCH_MAX_TOKENS = 1000                      # segments avg 80 chars

# tags + HTML entities are frozen tokens — they NEVER enter MT
TOKEN_RE = re.compile(r"<[^>]+>|&[a-zA-Z]+;|&#[0-9]+;")
URL_RE = re.compile(r"https?://[^\s<>\"]+")
# tolerant unmask: engines sometimes add spaces or case-fold the placeholder
UNMASK_RE = re.compile(r"[Xx]\s?[Qq]\s?[Vv]\s?([0-9]+)\s?[Zz]")


# ------------------------------------------------------------- segmentation
def split_parts(s):
    """[(kind, text)] with kind ∈ {frozen, text}; ''.join(texts) == s exactly.
    Tags/entities are frozen; whitespace-only text is frozen too (MT would
    eat the spacing between adjacent tags)."""
    parts, last = [], 0
    for m in TOKEN_RE.finditer(s):
        if m.start() > last:
            parts.append(("text", s[last:m.start()]))
        parts.append(("frozen", m.group(0)))
        last = m.end()
    if last < len(s):
        parts.append(("text", s[last:]))
    return [("frozen" if k == "text" and not t.strip() else k, t)
            for k, t in parts]


def mask_nouns(text, nouns):
    """Frozen nouns (longest first, so 'Lac d'Annecy' wins over 'Annecy')
    and bare URLs → XQV<n>Z placeholders. Returns (masked, {n: original})."""
    mapping = {}
    counter = [0]

    def sub(m):
        n = str(counter[0])
        counter[0] += 1
        mapping[n] = m.group(0)
        return f"XQV{n}Z"

    pats = [URL_RE.pattern] + [re.escape(n) for n in
                               sorted(set(nouns), key=len, reverse=True)]
    return re.compile("|".join(pats)).sub(sub, text), mapping


def unmask(mt, mapping):
    """Restore placeholders verbatim. Returns (text, missing_ids)."""
    seen = set()

    def sub(m):
        n = m.group(1)
        seen.add(n)
        return mapping.get(n, m.group(0))

    out = UNMASK_RE.sub(sub, mt)
    return out, set(mapping) - seen


def digits_of(s):
    return sorted(re.findall(r"[0-9]", s))


def check_segment(src, out):
    """Scripted proofreading — reasons list, empty = OK."""
    reasons = []
    if digits_of(src) != digits_of(out):
        reasons.append("digit parity broken")
    ss, os_ = len(src.strip()), len(out.strip())
    if ss >= 20 and not (0.3 <= os_ / max(1, ss) <= 3.0):
        reasons.append(f"segment ratio {os_ / max(1, ss):.2f} outside 0.3-3.0")
    if ss and not os_:
        reasons.append("empty translation")
    return reasons


def translate_segment(engine, cache, text, nouns):
    """One text node through mask → MT → unmask → checks.
    Leading/trailing whitespace is OURS, not the engine's — MT engines trim
    it, which would weld text onto the neighbouring tag (`</strong>jest`).
    Returns (translated, reasons)."""
    lead = text[:len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    core = text.strip()
    masked, mapping = mask_nouns(core, nouns)
    if masked in cache:
        mt = cache[masked]
    else:
        mt = engine(masked)
        cache[masked] = mt
    out, missing = unmask(mt, mapping)
    reasons = [f"placeholder lost: {mapping[n][:40]!r}" for n in sorted(missing)]
    reasons += check_segment(core, out)
    return lead + out + trail, reasons


def translate_string(engine, cache, s, nouns, path, records):
    """Whole string value: frozen parts verbatim, text parts through MT.
    Appends one record per part to `records` (the flags-file segment table —
    self-contained for patch-tier reassembly). Returns (translated, n_bad)."""
    out, n_bad = [], 0
    for i, (kind, part) in enumerate(split_parts(s)):
        if kind == "frozen":
            records.append({"path": path, "i": i, "kind": "frozen", "src": part})
            out.append(part)
            continue
        mt, reasons = translate_segment(engine, cache, part, nouns)
        records.append({"path": path, "i": i, "kind": "text", "src": part,
                        "mt": mt, "ok": not reasons, "reasons": reasons})
        if reasons:
            n_bad += 1
        out.append(mt)
    return "".join(out), n_bad


def translate_value(engine, cache, v, nouns, path, records):
    """Mirror the source structure exactly (shape parity by construction)."""
    if isinstance(v, str):
        return translate_string(engine, cache, v, nouns, path, records)
    if isinstance(v, dict):
        out, bad = {}, 0
        for k, x in v.items():
            out[k], b = translate_value(engine, cache, x, nouns,
                                        f"{path}.{k}", records)
            bad += b
        return out, bad
    if isinstance(v, list):
        out, bad = [], 0
        for i, x in enumerate(v):
            t, b = translate_value(engine, cache, x, nouns,
                                   f"{path}[{i}]", records)
            out.append(t)
            bad += b
        return out, bad
    return v, 0                                  # numbers/bools/null verbatim


def rebuild_field(src_value, records, patches, path):
    """Recursively rebuild the translated field from the segment table."""
    if isinstance(src_value, str):
        parts = [r for r in records if r["path"] == path]
        out = []
        for r in sorted(parts, key=lambda r: r["i"]):
            if r["kind"] == "frozen":
                out.append(r["src"])
            elif r.get("ok"):
                out.append(r["mt"])
            elif (r["path"], r["i"]) in patches:
                out.append(patches[(r["path"], r["i"])])
            else:
                return None
        return "".join(out)
    if isinstance(src_value, dict):
        out = {}
        for k, x in src_value.items():
            t = rebuild_field(x, records, patches, f"{path}.{k}")
            if t is None:
                return None
            out[k] = t
        return out
    if isinstance(src_value, list):
        out = []
        for i, x in enumerate(src_value):
            t = rebuild_field(x, records, patches, f"{path}[{i}]")
            if t is None:
                return None
            out.append(t)
        return out
    return src_value


# ------------------------------------------------------------------- engine
class ArgosEngine:
    """argostranslate en→<lang>; downloads/installs the model on first use."""

    def __init__(self, lang):
        import argostranslate.package as pkg
        import argostranslate.translate as trans
        self.lang = lang
        installed = {(p.from_code, p.to_code) for p in pkg.get_installed_packages()}
        if ("en", lang) not in installed:
            print(f"  downloading argos model en→{lang} …")
            pkg.update_package_index()
            target = next(p for p in pkg.get_available_packages()
                          if p.from_code == "en" and p.to_code == lang)
            pkg.install_from_path(target.download())
        self._translate = trans.translate

    def __call__(self, text):
        return self._translate(text, "en", self.lang)


# Pool worker plumbing — each worker loads the model once and stays
# single-threaded (OMP_NUM_THREADS=1) so N workers are truly parallel
# instead of fighting over the same cores.
_POOL_LANG = None


def _pool_init(lang):
    global _POOL_LANG
    import os as _os
    _os.environ.setdefault("OMP_NUM_THREADS", "1")
    _POOL_LANG = lang


def _pool_translate(text):
    import argostranslate.translate as trans
    return text, trans.translate(text, "en", _POOL_LANG)


def collect_unique_masked(pairs, communes):
    """Pass 1 of the pooled run: every unique MASKED text core across the
    corpus (same masking translate_segment applies — the cache key)."""
    uniq = set()
    for fiche, src in pairs:
        nouns = tb.fiche_frozen_nouns(fiche) + communes
        for v in src.values():
            for s in tb.strings_of(v):
                for kind, part in split_parts(s):
                    if kind != "text":
                        continue
                    core = part.strip()
                    if core:
                        uniq.add(mask_nouns(core, nouns)[0])
    return sorted(uniq)


def pooled_cache(lang, pairs, communes, workers=None):
    """Pass 2: translate the unique masked segments on a process pool.
    Returns the preloaded {masked: mt} cache for the assembly pass."""
    import multiprocessing as mp
    import os as _os
    uniq = collect_unique_masked(pairs, communes)
    workers = workers or max(1, (_os.cpu_count() or 2) - 1)
    print(f"[{lang}] {len(uniq)} unique masked segments → "
          f"{workers} worker(s), model loads once per worker")
    cache = {}
    ctx = mp.get_context("spawn")       # safe with torch/ctranslate2 threads
    with ctx.Pool(workers, initializer=_pool_init, initargs=(lang,)) as pool:
        for i, (src_txt, mt) in enumerate(
                pool.imap_unordered(_pool_translate, uniq, chunksize=8), 1):
            cache[src_txt] = mt
            if i % 500 == 0 or i == len(uniq):
                print(f"  …MT {i}/{len(uniq)}", flush=True)
    return cache


# ------------------------------------------------------------------ MT run
def flags_path(lang):
    return Path(str(FLAGS_FILE).format(lang=lang))


def run_mt(lang, engine=None, dry_run=False):
    """The $0 base tier. Returns (written, flagged_fields)."""
    pairs = tb.pairs_for_lang(lang)
    communes = tb.all_communes()
    n_fields = sum(len(src) for _, src in pairs)
    print(f"[{lang}] {len(pairs)} fiches · {n_fields} prose fields · "
          f"engine=argostranslate en→{lang} · cost $0.00")
    if dry_run:
        print(f"[{lang}] --dry-run: stopping before MT. Nothing billed either way.")
        return 0, 0
    if not pairs:
        print(f"[{lang}] nothing to do — already populated")
        return 0, 0

    if engine is None:
        engine = ArgosEngine(lang)      # ensures the model is installed
        cache = pooled_cache(lang, pairs, communes)   # two-phase, parallel
    else:
        cache = {}                      # test path: serial, injected engine
    written = 0
    flagged_fields = []
    for k, (fiche, src) in enumerate(pairs, 1):
        nouns = tb.fiche_frozen_nouns(fiche) + communes
        out, bad_fields = {}, {}
        for field, v in src.items():
            records = []
            tv, n_bad = translate_value(engine, cache, v, nouns, field, records)
            if n_bad:
                bad_fields[field] = {"src": v, "segments": records,
                                     "n_flagged": n_bad}
            else:
                out[field] = tv
        if out:
            sub_src = {f: src[f] for f in out}
            viol = tb.validate(sub_src, out, tb.fiche_frozen_nouns(fiche))
            if viol:
                # construction should make this unreachable — honesty first
                for f in list(out):
                    bad_fields.setdefault(f, {"src": src[f], "segments": [],
                                              "n_flagged": 0})
                    bad_fields[f]["validate_viol"] = viol
                out = {}
        if out:
            tb.write_back(fiche, lang, out)
            written += 1
        for field, rec in bad_fields.items():
            flagged_fields.append({"slug": fiche["slug"], "field": field, **rec})
        if k % 50 == 0:
            print(f"  …{k}/{len(pairs)} fiches ({written} written, "
                  f"{len(flagged_fields)} flagged fields, "
                  f"{len(cache)} cached segments)")

    fp = flags_path(lang)
    fp.parent.mkdir(exist_ok=True)
    fp.write_text(json.dumps({
        "lang": lang, "date": datetime.date.today().isoformat(),
        "engine": f"argostranslate en->{lang}",
        "fields": flagged_fields,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_segs = sum(len(f["segments"]) for f in flagged_fields)
    n_flagged_segs = sum(f["n_flagged"] for f in flagged_fields)
    print(f"[{lang}] MT DONE: {written} fiches written · "
          f"{len(flagged_fields)} fields held back "
          f"({n_flagged_segs} flagged of {n_segs} segments in them) → {fp.name}")
    print(f"[{lang}] spend: $0.00. Patch contract: --patch-dry-run.")
    return written, len(flagged_fields)


# -------------------------------------------------------------- patch tier
def patch_requests(lang, flags):
    """One Haiku request per FLAGGED segment (masked source travels — the
    model keeps XQV<n>Z placeholders and numbers verbatim)."""
    reqs, routing = [], {}
    i = 0
    sysblock = (f"You translate short tourism text segments from English to "
                f"{tb.LANG_NAMES[lang]} for loisirs74.fr. Reply with ONLY the "
                "translated segment - no quotes, no commentary. Any token of "
                "the form XQV<number>Z is a masked proper name: copy every "
                "one through VERBATIM, exactly once, in natural position. "
                "Keep all digits, prices, times and URLs unchanged.")
    for fi, f in enumerate(flags["fields"]):
        for r in f["segments"]:
            if r["kind"] != "text" or r.get("ok"):
                continue
            # Haiku receives the RAW source segment (no masking needed — the
            # whole-field validate() after reassembly proves frozen nouns
            # survived; the scripted digit/ratio checks gate each segment).
            cid = f"{lang}-p{i:05d}"
            routing[cid] = {"fi": fi, "path": r["path"], "i": r["i"]}
            reqs.append({
                "custom_id": cid,
                "params": {
                    "model": PATCH_MODEL,
                    "max_tokens": PATCH_MAX_TOKENS,
                    "system": sysblock,
                    "messages": [{"role": "user", "content": r["src"]}],
                },
            })
            i += 1
    return reqs, routing


def patch_estimate(reqs):
    cal = tb.load_calibration()
    in_per_char = cal.get("input_tokens_per_char") or tb.DEFAULT_IN_PER_CHAR
    sys_chars = len(reqs[0]["params"]["system"]) if reqs else 0
    in_tok = out_tok = 0
    for r in reqs:
        chars = len(r["params"]["messages"][0]["content"])
        in_tok += int((chars + sys_chars) * in_per_char) + 1
        out_tok += int(chars * 0.5) + 1     # short segments; ceiling factor
    usd = (in_tok * PATCH_IN_PER_MTOK + out_tok * PATCH_OUT_PER_MTOK) / 1e6
    return in_tok, out_tok, usd


def run_patch(lang, submit=False):
    fp = flags_path(lang)
    if not fp.exists():
        sys.exit(f"[{lang}] no flags file ({fp.name}) — run the MT tier first")
    flags = json.loads(fp.read_text(encoding="utf-8"))
    reqs, routing = patch_requests(lang, flags)
    in_tok, out_tok, usd = patch_estimate(reqs)
    print(f"[{lang}] PATCH contract: {len(reqs)} flagged segment(s) on "
          f"{PATCH_MODEL} batch · est ~{in_tok/1000:.1f}k in / "
          f"~{out_tok/1000:.1f}k out tok · est ~${usd:.2f} "
          f"(hard cap ${PATCH_CAP_USD:.2f})")
    if not reqs:
        print(f"[{lang}] nothing flagged — no patch needed.")
        return True
    if not submit:
        print(f"[{lang}] --patch-dry-run: stopping before submit. "
              "Eddie sees the bill first.")
        return True
    if usd > PATCH_CAP_USD:
        sys.exit(f"[{lang}] ABORT: contract ${usd:.2f} exceeds the "
                 f"${PATCH_CAP_USD:.2f}/lang patch cap (HANDOFF-37).")

    client = tb.get_client()
    bid = tb.submit_batch(client, reqs)
    flags["patch_batch_id"] = bid
    fp.write_text(json.dumps(flags, ensure_ascii=False, indent=1) + "\n",
                  encoding="utf-8")
    tb.poll_batch(client, bid)
    results, usage = tb.collect_results(client, bid)
    tot = tb.sum_usage(usage.values())
    actual = tb.usage_cost_usd(tot)
    if any(tot.values()):
        print(f"[{lang}] METER patch batch: {tot['input_tokens']:,} in / "
              f"{tot['output_tokens']:,} out tok → ${actual:.2f} actual "
              f"vs ${usd:.2f} contract")

    # route results back into the segment tables
    patched_segs = 0
    for cid, (kind, payload) in results.items():
        route = routing.get(cid)
        if not route or kind != "ok":
            continue
        f = flags["fields"][route["fi"]]
        rec = next(r for r in f["segments"]
                   if r["path"] == route["path"] and r["i"] == route["i"])
        out = payload.strip()
        reasons = check_segment(rec["src"], out)
        # placeholders: Haiku got the raw source, so nouns are plain text —
        # only the scripted checks gate here; frozen-noun survival is proven
        # by the whole-field validate() below.
        if reasons:
            rec["patch_reasons"] = reasons
            continue
        rec["mt"] = out
        rec["ok"] = True
        rec["patched"] = True
        patched_segs += 1

    # reassemble + validate + write every field that is now complete
    by_slug = {}
    for f in flags["fields"]:
        by_slug.setdefault(f["slug"], []).append(f)
    all_pairs = {fc["slug"]: (fc, sc)
                 for fc, sc in tb.pairs_for_lang(lang, force=True)}
    written_fields = still = 0
    for slug, fields in by_slug.items():
        pair = all_pairs.get(slug)
        if not pair:
            continue
        fiche, _src = pair
        out = {}
        for f in fields:
            if f.get("written"):
                continue
            rebuilt = rebuild_field(f["src"], f["segments"], {}, f["field"])
            if rebuilt is None:
                still += 1
                continue
            viol = tb.validate({f["field"]: f["src"]}, {f["field"]: rebuilt},
                               tb.fiche_frozen_nouns(fiche))
            if viol:
                f["patch_viol"] = viol
                still += 1
                continue
            out[f["field"]] = rebuilt
            f["written"] = True
            written_fields += 1
        if out:
            tb.write_back(fiche, lang, out)
    fp.write_text(json.dumps(flags, ensure_ascii=False, indent=1) + "\n",
                  encoding="utf-8")
    print(f"[{lang}] PATCH DONE: {patched_segs} segments patched · "
          f"{written_fields} fields completed+written · {still} still held "
          f"(absent, logged in {fp.name})")
    if any(tot.values()) and tb.over_budget(actual, usd):
        print(f"[{lang}] BUDGET OVERRUN >15% on the patch — RED (HANDOFF-35 rule).")
        sys.exit(3)
    return still == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lang", required=True, help=f"one of {'/'.join(MT_LANGS)}")
    ap.add_argument("--dry-run", action="store_true",
                    help="counts only, no MT, no writes (still $0 either way)")
    ap.add_argument("--patch-dry-run", action="store_true",
                    help="print the Haiku patch contract from the flags file")
    ap.add_argument("--patch-submit", action="store_true",
                    help="PAID (≤$2 cap): Haiku-patch the flagged segments — "
                         "only after Eddie saw the contract")
    args = ap.parse_args()
    if args.lang not in MT_LANGS:
        sys.exit(f"ERROR: unknown MT lang {args.lang!r} (expected {MT_LANGS})")
    if args.patch_dry_run or args.patch_submit:
        run_patch(args.lang, submit=args.patch_submit)
    else:
        run_mt(args.lang, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
