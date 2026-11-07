#!/usr/bin/env python3
"""inject_hub_photos.py: one real photo on each category hub banner.

THE BRIEF (owner, 2026-11-07)
  Each hub illustrated by one photo of Bénédicte's or the owner's, never a
  generic stock banner when a real one exists.

HOW
  data/hub-photos.json maps a French hub slug (cascades, chateaux…) to an
  image already published on that hub's own fiches, plus its credit. Every
  page with a .hub-hero, in every language, is matched to its French hub
  through its own <link rel="alternate" hreflang="fr">. Localized directory
  names (/en/waterfalls/, /pl/wodospady/) therefore need no table here.
  The page's --hub-hero-img is then pointed at the photo, and a fenced
  credit line is added inside the banner.

  Commune pages also have a .hub-hero, but their French alternate is no
  category hub, so they are left alone. Hubs absent from the JSON keep the
  generic banner.

ORDER
  Runs before preload_hub_hero, which reads --hub-hero-img to emit the LCP
  preload. A preload pointing at the old image would waste the bandwidth it
  exists to save.

Fails if a configured image is missing on disk, because a banner pointing
at a 404 is a blank hero.

Usage:
    python3 scripts/inject_hub_photos.py            # report, writes nothing
    python3 scripts/inject_hub_photos.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import siteconfig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "data" / "hub-photos.json").read_text(encoding="utf-8"))["hubs"]
BASE = siteconfig.BASE_URL.rstrip("/")
VAR_RE = re.compile(r'--hub-hero-img:url\("[^"]*"\)')
FR_ALT_RE = re.compile(r'<link rel="alternate" hreflang="fr" href="([^"]+)"')
# The credit goes straight inside the <section>, not the .wrap: the .wrap is
# positioned, so a credit inside it sat level with the H1 and a long hub
# title would run into it. Anchored to the section, it sits in the top corner.
WRAP_RE = re.compile(r'(<section class="hub-hero">)')
MARK_A, MARK_B = "<!--hub-photo:start-->", "<!--hub-photo:end-->"
FENCE_RE = re.compile(re.escape(MARK_A) + r".*?" + re.escape(MARK_B), re.S)
SKIP_TOP = {"reports", "scripts", "_site", "scratchpad", "tests", "node_modules",
            "incoming-generics", "incoming-benedicte", ".git"}
CREDIT_STYLE = ("position:absolute;top:10px;right:14px;margin:0;font-size:.7rem;"
                "color:rgba(253,250,243,.88);text-shadow:0 1px 6px rgba(15,30,38,.6)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for hub, c in CFG.items():
        if not (ROOT / c["src"].lstrip("/")).is_file():
            raise SystemExit(f"FAIL: hub {hub}: {c['src']} is not on disk")
    seen, changed = {}, 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if os.path.relpath(dirpath, ROOT) == ".":
            dirnames[:] = [d for d in dirnames if d not in SKIP_TOP]
        if "index.html" not in filenames:
            continue
        path = Path(dirpath) / "index.html"
        text = path.read_text(encoding="utf-8")
        if 'class="hub-hero"' not in text or not VAR_RE.search(text):
            continue
        m = FR_ALT_RE.search(text)
        if not m or not m.group(1).startswith(BASE + "/"):
            continue
        hub = m.group(1)[len(BASE) + 1:].strip("/")
        c = CFG.get(hub)
        if not c:
            continue
        new = VAR_RE.sub(f'--hub-hero-img:url("{c["src"]}")', FENCE_RE.sub("", text), count=1)
        credit = (f'{MARK_A}<p class="hub-photo-credit" style="{CREDIT_STYLE}">'
                  f'{html_lib.escape(c["credit"], quote=False)}</p>{MARK_B}')
        new, n = WRAP_RE.subn(lambda mm: mm.group(1) + credit, new, count=1)
        if n != 1:
            raise SystemExit(f"FAIL: {path.relative_to(ROOT)}: no hub-hero section to credit")
        seen[hub] = seen.get(hub, 0) + 1
        if new != text:
            changed += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")
    missing = sorted(set(CFG) - set(seen))
    print(f"hub photos: {sum(seen.values())} hub pages across {len(seen)} hubs, {changed} changed "
          f"[{'applied' if args.apply else 'dry run'}]"
          + (f" · configured but not found: {missing}" if missing else ""))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
