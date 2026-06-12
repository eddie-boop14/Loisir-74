#!/usr/bin/env python3
"""Rebuild every fiche HTML for every supported locale, from Json/ only.

Usage:
    python3 scripts/build_all_locales.py [--only-lang <lang>] [--out-dir <dir>]

Writes a translation-coverage report to scripts/translation-coverage-report.json
with, per locale: pages built, fields that fell back to FR, body-language
heuristic (truly-translated / FR-residue), and a slug-level breakdown.
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import build_lieu_page as B  # noqa: E402

LANGS = ["fr", "en", "de", "it", "es", "nl"]


def fr_signal(text):
    """Heuristic: True if `text` looks French. Used to flag FR-residue bodies."""
    if not text:
        return False
    s = text[:600].lower()
    fr_markers = sum(
        1 for w in [" la ", " le ", " les ", " une ", " un ", " des ", " du ",
                    " de la ", " est ", " sont ", " aux ", " pour ", " avec ",
                    " sur ", " dans "] if w in s
    )
    return fr_markers >= 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-lang", choices=LANGS, default=None)
    ap.add_argument("--out-dir", default=str(REPO))
    ap.add_argument("--report-path", default=str(REPO / "scripts" / "translation-coverage-report.json"))
    args = ap.parse_args()
    out_base = Path(args.out_dir)
    langs = [args.only_lang] if args.only_lang else LANGS

    json_paths = sorted(glob.glob(str(REPO / "Json" / "*.json")))
    print(f"Building {len(json_paths)} fiches × {len(langs)} locales = {len(json_paths)*len(langs)} pages")

    report = {
        "total_fiches": len(json_paths),
        "per_lang": {},
        "fr_residue_slugs": {L: [] for L in langs if L != "fr"},
        "fallback_slugs": {L: [] for L in langs if L != "fr"},
    }

    for lang in langs:
        out_dir = out_base if lang == "fr" else out_base / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        built = 0
        translated_body = 0
        fr_body = 0
        missing_body = 0
        fields_fallback = {}  # field -> count
        fallback_pages = 0

        for jp in json_paths:
            d = json.loads(Path(jp).read_text(encoding="utf-8"))
            slug = d["slug"]
            html = B.build_page(d, lang=lang)
            fb = set(B.LAST_FALLBACK_FIELDS)
            (out_dir / f"{slug}.html").write_text(html, encoding="utf-8")
            built += 1
            if fb and lang != "fr":
                fallback_pages += 1
                report["fallback_slugs"][lang].append(slug)
                for f in fb:
                    fields_fallback[f] = fields_fallback.get(f, 0) + 1

            if lang != "fr":
                i = d.get("i18n", {}).get(lang, {}) or {}
                body = i.get("body", {}) if isinstance(i.get("body"), dict) else {}
                wi = body.get("what_is", "") or i.get("what_is", "")
                if not wi:
                    missing_body += 1
                elif fr_signal(wi):
                    fr_body += 1
                    report["fr_residue_slugs"][lang].append(slug)
                else:
                    translated_body += 1

        report["per_lang"][lang] = {
            "pages_built": built,
            "fallback_pages": fallback_pages,
            "fields_fallback_counts": fields_fallback,
            "body_truly_translated": translated_body if lang != "fr" else built,
            "body_fr_residue": fr_body,
            "body_missing": missing_body,
        }
        print(f"  [{lang}] built={built}  body_tr={translated_body if lang!='fr' else built}  body_fr-residue={fr_body}  body_missing={missing_body}  fallback_pages={fallback_pages}")

    Path(args.report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {args.report_path}")


if __name__ == "__main__":
    main()
