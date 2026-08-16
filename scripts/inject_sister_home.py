#!/usr/bin/env python3
"""inject_sister_home.py — the sister-site line on the 12 homepages.

WHY
  The phase-2 sister machinery promises "one line in the footer bottom, in
  all 12 languages". build_lieu_page delivers it on every fiche (5,208
  pages) — but the homepages are hand-authored chrome that no builder
  regenerates, so arming the `sister` block put the line everywhere EXCEPT
  the page people actually check. Meanwhile loisirs73.fr shows its
  loisirs74 backlink on its own homepage. This closes the asymmetry.

WHAT IT RENDERS
  The exact line the fiche footers already carry, appended inside the
  homepage's <div class="foot-bottom"> after the © span:

      Même exigence en Savoie : <a href="https://loisirs73.fr">Loisirs 73</a>

  Wording comes from build_lieu_page.CHROME["f_sister"] — the reviewed
  12-language strings that already ship — with the same punctuation rules
  (French space-colon; Japanese no lead space). Nothing is retranslated.
  Colors are hardcoded light-on-dark, the footer's own dark-mode recipe:
  the homepage footer zone is dark in every render mode, and a var-driven
  color is exactly what made the footer invisible once before.

CONFIG-DRIVEN, BOTH WAYS
  siteconfig.SISTER present  → the fenced line is inserted or repaired.
  siteconfig.SISTER absent   → the fenced line is REMOVED. Disarming the
  config must disarm every surface, or the flip stops being one flip.

Idempotent: marker-fenced, byte-stable on re-run.

Usage:
    python3 scripts/inject_sister_home.py            # report, writes nothing
    python3 scripts/inject_sister_home.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import html as html_lib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import siteconfig  # noqa: E402
import build_lieu_page as BL  # noqa: E402  reuse the reviewed f_sister strings

ROOT = Path(__file__).resolve().parent.parent
MARK_A, MARK_B = "<!--sister-home:start-->", "<!--sister-home:end-->"
FENCE_RE = re.compile(re.escape(MARK_A) + r".*?" + re.escape(MARK_B), re.S)


def esc(s):
    return html_lib.escape(str(s), quote=True)


def homepages():
    yield "fr", ROOT / "index.html"
    for sub in sorted(ROOT.iterdir()):
        if sub.is_dir() and len(sub.name) == 2 and (sub / "index.html").exists():
            yield sub.name, sub / "index.html"


def line_for(lang, sis):
    label = BL.CHROME["f_sister"].get(lang) or BL.CHROME["f_sister"]["fr"]
    dept = esc(sis.get("dept") or "")
    # Same rules as build_lieu_page.sister_link_html: French puts a space
    # before the colon, Japanese takes no space before the département name.
    lead = "" if lang == "ja" else " "
    colon = " : " if lang == "fr" else ": "
    return (f'{MARK_A}<span class="sister" style="color:rgba(245,241,232,.72)">'
            f'{label}{lead}{dept}{colon}'
            f'<a href="{esc(sis["url"])}" style="color:#9fd3e0;font-weight:600;'
            f'text-decoration:none">{esc(sis["name"])}</a></span>{MARK_B}')


def main():
    ap = argparse.ArgumentParser(description="Sister-site line on the homepages.")
    ap.add_argument("--apply", action="store_true", help="write changes (default: report only)")
    args = ap.parse_args()

    sis = getattr(siteconfig, "SISTER", None)
    armed = bool(sis and sis.get("url") and sis.get("name"))

    changed = removed = ok = no_anchor = 0
    for lang, page in homepages():
        html = page.read_text(encoding="utf-8")
        has = FENCE_RE.search(html)

        if not armed:
            if has:
                new = FENCE_RE.sub("", html)
                removed += 1
                if args.apply:
                    page.write_text(new, encoding="utf-8")
            continue

        want = line_for(lang, sis)
        if has:
            if has.group(0) == want:
                ok += 1
                continue
            new = FENCE_RE.sub(want, html, count=1)
        else:
            m = re.search(r'(<div class="foot-bottom">.*?)(</div>)', html, re.S)
            if not m:
                no_anchor += 1
                continue
            new = html[:m.end(1)] + "\n" + want + "\n" + html[m.end(1):]
        changed += 1
        if args.apply:
            page.write_text(new, encoding="utf-8")

    verb = "" if args.apply else "would "
    state = "armed" if armed else "DISARMED (no sister block in site.config.json)"
    print(f"inject_sister_home [{state}]: {verb}write {changed} · already correct {ok} "
          f"· {verb}remove {removed}")
    if no_anchor:
        print(f"  ⚑ no <div class=\"foot-bottom\"> anchor on {no_anchor} homepage(s) — not injected")
    if not args.apply and (changed or removed):
        print("  report only — re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
