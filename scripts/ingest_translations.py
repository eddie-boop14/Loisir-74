#!/usr/bin/env python3
"""ingest_translations.py — JOB 7. Apply a translation payload into Json/.

Payload shape (one file per locale, at translations/<lang>.json):

  {
    "<slug>": {
      "name": "...",
      "name_alternates": ["..."],
      "meta_title": "...",
      "meta_description": "...",
      "hero_alt": "...",
      "body.what_is": "<p>...</p>",
      "body.activities[<i>].title": "...",
      "body.activities[<i>].description": "...",
      "body.practical_info[<i>].k": "...",
      "body.practical_info[<i>].v": "...",
      "body.how_to_get_there.car": "...",
      "body.how_to_get_there.public_transport": "...",
      "body.how_to_get_there.bike": "...",
      "body.when_to_visit": "...",
      "faq[<i>].q": "...",
      "faq[<i>].a": "..."
    },
    ...
  }

For each slug × locale:
  - merges the payload into the existing i18n.<lang> block (creates the
    block if missing).
  - preserves any existing translated content not in the payload.
  - writes a research_log entry recording the ingest.

Idempotent: re-running with the same payload produces no JSON changes.

CLI:
    python3 scripts/ingest_translations.py             # ingest all 5 locales
    python3 scripts/ingest_translations.py --only en   # only one locale
    python3 scripts/ingest_translations.py --dry-run   # show what would change
"""
import argparse
import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "Json"
TRANS_DIR = ROOT / "translations"
LANGS = ("en", "de", "it", "es", "nl")
TODAY = datetime.date.today().isoformat()


def set_path(obj, dotted, value):
    """Set obj at dotted path (supports body.activities[2].title style).
    Creates dicts and pads lists as needed."""
    tokens = re.findall(r"[^.\[\]]+|\[\d+\]", dotted)
    cur = obj
    for i, tok in enumerate(tokens[:-1]):
        nxt = tokens[i + 1]
        if tok.startswith("["):
            idx = int(tok[1:-1])
            while len(cur) <= idx:
                cur.append({})
            cur = cur[idx]
        else:
            if tok not in cur or not isinstance(cur[tok], (dict, list)):
                cur[tok] = [] if nxt.startswith("[") else {}
            cur = cur[tok]
    last = tokens[-1]
    if last.startswith("["):
        idx = int(last[1:-1])
        while len(cur) <= idx:
            cur.append(None)
        cur[idx] = value
    else:
        cur[last] = value


def merge_payload(blk, payload):
    """Mutate blk in place with payload's dotted-path values. Return True if changed."""
    changed = False
    for path, value in payload.items():
        # Detect a no-op
        try:
            cur = blk
            for tok in re.findall(r"[^.\[\]]+|\[\d+\]", path):
                if tok.startswith("["):
                    cur = cur[int(tok[1:-1])]
                else:
                    cur = cur[tok]
            if cur == value:
                continue
        except (KeyError, IndexError, TypeError):
            pass
        set_path(blk, path, value)
        changed = True
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=LANGS, help="Ingest only one locale")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    langs = [args.only] if args.only else list(LANGS)

    total_changed = 0
    per_lang = {}
    for lang in langs:
        f = TRANS_DIR / f"{lang}.json"
        if not f.exists():
            print(f"  [{lang}] no payload at translations/{lang}.json — skip")
            per_lang[lang] = 0
            continue
        payload = json.loads(f.read_text(encoding="utf-8"))
        n_changed = 0
        for slug, fields in payload.items():
            jp = JSON_DIR / f"{slug}.json"
            if not jp.exists():
                print(f"  [{lang}] {slug}: JSON not found — skip")
                continue
            d = json.loads(jp.read_text(encoding="utf-8"))
            i18n = d.setdefault("i18n", {})
            blk = i18n.setdefault(lang, {})
            if not isinstance(blk, dict):
                blk = {}; i18n[lang] = blk
            if merge_payload(blk, fields):
                if not args.dry_run:
                    rl = d.setdefault("research_log", [])
                    if not any(r.get("note", "").startswith(f"Translation ingest [{lang}]") and r.get("date") == TODAY for r in rl):
                        rl.append({
                            "date": TODAY,
                            "by": "scripts/ingest_translations.py",
                            "note": f"Translation ingest [{lang}]: {len(fields)} field(s) updated.",
                        })
                    jp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                n_changed += 1
        per_lang[lang] = n_changed
        print(f"  [{lang}] {n_changed} fiches updated")
        total_changed += n_changed

    print(f"\ntotal fiches updated: {total_changed}")
    if args.dry_run:
        print("(dry-run — no JSON was written)")


if __name__ == "__main__":
    main()
