#!/usr/bin/env python3
"""inject_motion.py: one small motion standard on every page that has cards.

THE BRIEF (owner, 2026-11-07)
  "Alive", not "look at my animation". Cards lift slightly on hover, photos
  zoom 2-3 %, pins move a little, content fades in gently. Nothing more.

WHAT WAS THERE
  Fiche pages already matched it: their cards lift 3 px, their photos zoom
  3 %, and headings slide in on scroll (.reveal, which honours reduced
  motion). Hubs, communes and the homepages did twice as much: a 6 px lift
  and a 6 % zoom, authored in each page's own CSS, with no reduced-motion
  guard on hover.

WHAT THIS ADDS (one fenced <style>, just before </head>)
  - .card hover: 3 px lift and 3 % photo zoom everywhere. It comes later in
    the head than the authored rules, at equal specificity, so it wins.
  - Pin icons on place cards rise 2 px when their card is hovered. The site
    has no map, so these are the only pins there are.
  - prefers-reduced-motion: no hover transform, no transition, on every card
    type (place cards, homepage hero cards, category tiles).
  It deliberately adds NO opacity fade. A content block that starts at
  opacity 0 stays invisible whenever its script fails, which already
  happened on loisirs73.fr.

  The duck (duck.js) is not touched.

Usage:
    python3 scripts/inject_motion.py            # report, writes nothing
    python3 scripts/inject_motion.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK_A, MARK_B = "<!--motion:start-->", "<!--motion:end-->"
FENCE_RE = re.compile(re.escape(MARK_A) + r".*?" + re.escape(MARK_B), re.S)
SKIP_TOP = {"reports", "scripts", "_site", "scratchpad", "tests", "node_modules",
            "incoming-generics", "incoming-benedicte", ".git"}
CSS = (
    ".card:hover{transform:translateY(-3px)}"
    ".card:hover .card-photo img{transform:scale(1.03)}"
    ".card .card-commune svg{transition:transform .3s ease}"
    ".card:hover .card-commune svg{transform:translateY(-2px)}"
    "@media (prefers-reduced-motion:reduce){"
    ".card,.card .card-photo img,.card .card-commune svg,.hh-card,.glance-tile{transition:none!important}"
    ".card:hover,.card:hover .card-photo img,.card:hover .card-commune svg,.hh-card:hover,"
    ".glance-tile:hover{transform:none!important}}"
)
BLOCK = f"{MARK_A}<style>{CSS}</style>{MARK_B}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    total = changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if os.path.relpath(dirpath, ROOT) == ".":
            dirnames[:] = [d for d in dirnames if d not in SKIP_TOP]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = Path(dirpath) / fn
            text = path.read_text(encoding="utf-8")
            stripped = FENCE_RE.sub("", text)
            if 'class="card' not in stripped or stripped.count("</head>") != 1:
                new = stripped
            else:
                total += 1
                i = stripped.index("</head>")
                new = stripped[:i] + BLOCK + stripped[i:]
            if new != text:
                changed += 1
                if args.apply:
                    path.write_text(new, encoding="utf-8")
    print(f"motion: {total} pages with cards, {changed} changed "
          f"[{'applied' if args.apply else 'dry run'}]")


if __name__ == "__main__":
    sys.exit(main())
