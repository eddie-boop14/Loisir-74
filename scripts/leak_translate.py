#!/usr/bin/env python3
"""leak_translate.py — HANDOFF i18n-fr-leak JOB 2 driver (FR is the reference).

Translates ONLY the leaked lang-fields listed in reports/i18n-leak-baseline.json,
straight from i18n.fr (never a pivot language), field by field, and writes the
result into i18n.<lang>.<field>. Frozen French names, communes, numbers, €, and
the winter controlled-vocab tokens are preserved verbatim; the shape/tag/frozen
validators from translate_batch are reused and extended with digit/€ + winter
guards. Nothing is applied unless it validates (null discipline).

    --lang de --extract [--limit N | --slugs a,b]  → reports/leak-work-de.json
        (work-list: {slug, name, commune, frozen[], winter_tokens[], fields})
    --lang de --apply                              → validates reports/leak-out-de.json
        and writes i18n.de.<field> for every field that passes; reports failures.

The translation itself (work-list → out-list) is produced in-session (subscription
engine), not by this script — this script only extracts, validates, and applies.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import translate_batch as TB  # noqa: E402  (reuse validators + frozen-noun logic)

JSON_DIR = os.path.join(ROOT, "Json")
BASELINE = os.path.join(ROOT, "reports", "i18n-leak-baseline.json")

# facts sub-keys that are controlled tokens / frozen data, NOT prose — never
# translated (the winter gate enforces their vocab; commune is a frozen name).
FACTS_FROZEN_KEYS = {"winter_access", "winter_infra", "snow_view", "col_chains",
                     "commune"}
DIGIT_RUN = re.compile(r"\d[\d\s.,]*\d|\d")


def digit_groups(text):
    """Multiset of digit sequences with thousands separators (space/dot/comma)
    stripped — so '1 477' and '1.477' compare equal, but a dropped/added number
    is caught."""
    from collections import Counter
    return Counter(re.sub(r"[\s.,]", "", g) for g in DIGIT_RUN.findall(text))


def winter_tokens(fiche):
    facts = ((fiche.get("i18n") or {}).get("fr") or {}).get("facts") or {}
    toks = []
    for k in ("winter_access", "snow_view"):
        v = facts.get(k)
        if isinstance(v, str):
            toks.append(v)
    for v in (facts.get("winter_infra") or []):
        toks.append(v)
    return toks


def work_for(fiche, fields):
    """Build the FR-source payload for exactly the leaked fields of one fiche.
    facts drops its frozen/controlled sub-keys from the translatable payload
    (they are re-attached verbatim at apply time)."""
    fr = (fiche.get("i18n") or {}).get("fr") or {}
    out = {}
    for f in fields:
        v = fr.get(f)
        if v in (None, "", [], {}):
            continue
        if f == "facts" and isinstance(v, dict):
            out[f] = {k: val for k, val in v.items() if k not in FACTS_FROZEN_KEYS}
        else:
            out[f] = v
    return out


def load_baseline_lang(lang):
    base = json.load(open(BASELINE, encoding="utf-8"))
    return {s: d[lang] for s, d in base.items() if lang in d}


def load_fiche(slug):
    return json.load(open(os.path.join(JSON_DIR, slug + ".json"), encoding="utf-8"))


def cmd_extract(lang, limit=None, slugs=None):
    work = load_baseline_lang(lang)
    if slugs:
        work = {s: work[s] for s in slugs if s in work}
    items = []
    for slug in sorted(work):
        fiche = load_fiche(slug)
        fields = work[slug]
        payload = work_for(fiche, fields)
        if not payload:
            continue
        items.append({
            "slug": slug,
            "name": (fiche.get("i18n", {}).get("fr", {}) or {}).get("name") or slug,
            "commune": fiche.get("commune") or "",
            "frozen": TB.fiche_frozen_nouns(fiche),
            "winter_tokens": winter_tokens(fiche),
            "fields": payload,
        })
        if limit and len(items) >= limit:
            break
    outp = os.path.join(ROOT, "reports", f"leak-work-{lang}.json")
    json.dump({"lang": lang, "items": items}, open(outp, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    nfields = sum(len(i["fields"]) for i in items)
    print(f"[leak-tr] {lang}: {len(items)} fiches · {nfields} fields → "
          f"{os.path.relpath(outp, ROOT)} (source = i18n.fr, verbatim)")


def validate_item(fiche, src_fields, out_fields, frozen, wtokens):
    """Return violation list for one fiche's translated fields (empty = PASS)."""
    viol = []
    # per-field shape/tag/frozen/length/empty (reuse translate_batch.validate)
    for f, src in src_fields.items():
        if f not in out_fields:
            viol.append(f"{f}: missing from output")
            continue
        viol += [f"{f}: {v}" for v in TB.validate(src, out_fields[f], frozen)]
    # digit/€ parity across the whole payload
    src_all = "\n".join(TB.strings_of(src_fields))
    out_all = "\n".join(TB.strings_of({f: out_fields.get(f) for f in src_fields}))
    if digit_groups(src_all) != digit_groups(out_all):
        viol.append("digit parity: a number was dropped/added/changed")
    if src_all.count("€") != out_all.count("€"):
        viol.append("€ count changed")
    # winter tokens must survive verbatim if they were in a translated string
    for t in wtokens:
        if t in src_all and t not in out_all:
            viol.append(f"winter token lost: {t!r}")
    return viol


def cmd_apply(lang):
    workp = os.path.join(ROOT, "reports", f"leak-work-{lang}.json")
    outp = os.path.join(ROOT, "reports", f"leak-out-{lang}.json")
    if not os.path.exists(outp):
        sys.exit(f"[leak-tr] no {os.path.relpath(outp, ROOT)} — translate the work-list first")
    work = {i["slug"]: i for i in json.load(open(workp, encoding="utf-8"))["items"]}
    outs = json.load(open(outp, encoding="utf-8"))
    outs = outs.get("items", outs) if isinstance(outs, dict) else outs
    applied = failed = 0
    fail_log = []
    for slug, out_fields in (outs.items() if isinstance(outs, dict) else
                             ((o["slug"], o["fields"]) for o in outs)):
        if slug not in work:
            fail_log.append((slug, ["not in work-list"])); failed += 1; continue
        w = work[slug]
        viol = validate_item(load_fiche(slug), w["fields"], out_fields,
                             w["frozen"], w["winter_tokens"])
        if viol:
            fail_log.append((slug, viol)); failed += 1; continue
        # write into i18n.<lang>.<field>, re-attaching frozen facts sub-keys
        fiche = load_fiche(slug)
        loc = fiche.setdefault("i18n", {}).setdefault(lang, {})
        fr = fiche["i18n"]["fr"]
        for f, val in out_fields.items():
            if f == "facts" and isinstance(val, dict):
                merged = dict(val)
                for k in FACTS_FROZEN_KEYS:
                    if k in (fr.get("facts") or {}):
                        merged[k] = fr["facts"][k]
                loc[f] = {k: merged[k] for k in fr["facts"]} if isinstance(fr.get("facts"), dict) else merged
            else:
                loc[f] = val
        with open(os.path.join(JSON_DIR, slug + ".json"), "w", encoding="utf-8") as fh:
            json.dump(fiche, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        applied += 1
    print(f"[leak-tr] {lang}: applied {applied} fiches, {failed} failed validation")
    for slug, viol in fail_log[:30]:
        print(f"    ✗ {slug}: {viol[0]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lang", required=True)
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--slugs", help="comma-separated slug subset")
    args = ap.parse_args()
    slugs = args.slugs.split(",") if args.slugs else None
    if args.extract:
        cmd_extract(args.lang, limit=args.limit, slugs=slugs)
    elif args.apply:
        cmd_apply(args.lang)
    else:
        ap.print_help(); sys.exit(1)


if __name__ == "__main__":
    main()
