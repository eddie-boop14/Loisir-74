#!/usr/bin/env python3
"""sync_home_cards.py — make homepage card images derive from Json/, not memory.

WHY
  index.html (and its 11 locale siblings) is hand-authored chrome: no builder
  regenerates its card grid. Only head-links and the intent "Nos sélections"
  strip are patched in. So a card's image keeps whatever was chosen the day it
  was written, even after the fiche it links to gains a real, credited,
  self-hosted hero.

  The result rots silently and in one direction: every photo added to Json/
  makes the homepage staler. On 2026-07-26 eighteen cards were showing a
  generic placeholder while the fiche behind them had a real photo — including
  fiches photographed that same morning.

  This is the same failure mode as the category-hub banner: a surface that is
  authored instead of derived. The fix is to derive it.

WHAT IT DOES
  For every `<a class="card-photo" href=".../<slug>">` on a homepage, rewrite
  the image it contains to the fiche's own hero — src, the <picture> webp
  source when there is one, the width/height pair, and the localized alt.

  The fiche is the single source of truth. Hubs already derive from it and
  match it exactly; the homepage is the only surface that drifts.

WHAT IT WILL NOT DO
  * Never introduces a hotlink. Fiches whose hero is still a remote URL are
    skipped — self-host it first (localize_heroes.py --only <slug>).
  * Never points at a missing file. The .jpg must exist; on a <picture> card
    the .webp sibling must exist too, otherwise the webp <source> would keep
    winning in the browser and silently serve the OLD photo.

  Every skip is reported with its reason. Nothing about this script is allowed
  to be silent — the 2026-08 audit found 162 stale cards across the twelve
  homepages, and 160 of them were being passed over without a word.

HISTORY — why this kept coming back
  The 2026-07 version only ever touched a card that was showing a
  /img/generique/ placeholder AND whose fiche had a real, non-generic,
  self-hosted hero. Three whole classes of drift fell outside that and were
  never reported:
    1. the card carries a bare <img> instead of <picture> — the regex could
       not even see it (37 of 77 cards on the FR homepage);
    2. the fiche's own hero is a /img/generique/ image, so a card showing a
       DIFFERENT generic was left alone — the two surfaces disagreed while
       both looked "fine";
    3. the fiche hero is a hotlink (reported, and still skipped — that one is
       correct, the fix is to self-host).
  Only class 3 ever printed anything, so the job looked done every time.

Idempotent: a second run changes nothing.

Usage:
    python3 scripts/sync_home_cards.py            # report only, writes nothing
    python3 scripts/sync_home_cards.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import siteconfig  # HANDOFF-73 phase 4: per-site domain
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "Json"

# The whole <a class="card-photo"> block, whatever markup it wraps.
# Host comes from siteconfig (HANDOFF-73 phase 4) — the old literal domain
# would have matched nothing on the 73.
CARD_BLOCK = re.compile(
    r'<a class="card-photo" href="' + siteconfig.SITE_URL_RE
    + r'/(?:([a-z]{2})/)?([a-z0-9-]+)">(.*?)</a>',
    re.S,
)
SOURCE_RE = re.compile(r'(<source srcset=")([^"]+)(")')
IMG_SRC_RE = re.compile(r'(<img src=")([^"]+)(")')
WIDTH_RE = re.compile(r'(\swidth=")(\d+)(")')
HEIGHT_RE = re.compile(r'(\sheight=")(\d+)(")')
ALT_RE = re.compile(r'(\salt=")([^"]*)(")')


def load_fiches():
    """slug -> (hero_image, {lang: hero_alt})"""
    out = {}
    for fp in sorted(JSON_DIR.glob("*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        alts = {}
        for lang, block in (d.get("i18n") or {}).items():
            alt = (block or {}).get("hero_alt")
            if isinstance(alt, str) and alt.strip():
                alts[lang] = alt.strip()
        out[d["slug"]] = ((d.get("hero_image") or "").strip(), alts)
    return out


def load_dims():
    fp = ROOT / "data" / "img-dims.json"
    return json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else {}


def homepages():
    yield "fr", ROOT / "index.html"
    for sub in sorted(ROOT.iterdir()):
        if sub.is_dir() and len(sub.name) == 2 and (sub / "index.html").exists():
            yield sub.name, sub / "index.html"


def esc_attr(s):
    """Match the escaping the page already uses for attribute text."""
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#x27;"))


SITE = siteconfig.BASE_URL


def bare(u):
    """Domain-agnostic path. The homepage mixes absolute and relative forms for
    the same file; they are the same picture and must not count as drift."""
    return u[len(SITE):] if u.startswith(SITE) else u


def like(existing, new):
    """Write `new` in whichever style this card already uses, so a card that is
    already correct is never rewritten just to change its URL form."""
    return SITE + new if existing.startswith(SITE) else new


def main():
    ap = argparse.ArgumentParser(description="Sync homepage card images from Json/ heroes.")
    ap.add_argument("--apply", action="store_true", help="write changes (default: report only)")
    args = ap.parse_args()

    fiches = load_fiches()
    dims = load_dims()
    total_changed = 0
    skipped = {"hotlinked hero (self-host first)": set(),
               "hero file missing on disk": set(),
               "webp sibling missing on a <picture> card": set(),
               "no hero in Json": set()}

    for lang, page in homepages():
        html = page.read_text(encoding="utf-8")
        changed = 0

        def repl(m):
            nonlocal changed
            _href_lang, slug, inner = m.groups()
            hero, alts = fiches.get(slug, (None, {}))
            if not hero:
                if slug in fiches:
                    skipped["no hero in Json"].add(slug)
                return m.group(0)
            if hero.startswith(("http://", "https://", "//")):
                skipped["hotlinked hero (self-host first)"].add(slug)
                return m.group(0)
            if not hero.startswith("/img/"):
                return m.group(0)
            if not (ROOT / hero.lstrip("/")).exists():
                skipped["hero file missing on disk"].add(slug)
                return m.group(0)

            webp = re.sub(r"\.(jpg|jpeg|png)$", ".webp", hero)
            has_picture = "<source" in inner
            if has_picture and not (ROOT / webp.lstrip("/")).exists():
                # rewriting only the <img> would leave the webp <source>
                # winning in the browser and serving the OLD photo.
                skipped["webp sibling missing on a <picture> card"].add(slug)
                return m.group(0)

            new = inner
            if has_picture:
                new = SOURCE_RE.sub(
                    lambda s: s.group(1) + (s.group(2) if bare(s.group(2)) == webp
                                            else like(s.group(2), webp)) + s.group(3),
                    new, count=1)
            new = IMG_SRC_RE.sub(
                lambda s: s.group(1) + (s.group(2) if bare(s.group(2)) == hero
                                        else like(s.group(2), hero)) + s.group(3),
                new, count=1)

            wh = dims.get(hero.lstrip("/"))
            if wh and len(wh) == 2:
                new = WIDTH_RE.sub(lambda s: s.group(1) + str(wh[0]) + s.group(3), new, count=1)
                new = HEIGHT_RE.sub(lambda s: s.group(1) + str(wh[1]) + s.group(3), new, count=1)

            alt = alts.get(lang) or alts.get("fr")
            if alt:
                new = ALT_RE.sub(lambda s: s.group(1) + esc_attr(alt) + s.group(3), new, count=1)

            if new == inner:
                return m.group(0)
            changed += 1
            return m.group(0).replace(inner, new, 1)

        new_html = CARD_BLOCK.sub(repl, html)
        if changed and args.apply:
            page.write_text(new_html, encoding="utf-8")
        if changed:
            print(f"  {page.relative_to(ROOT)}: {changed} card(s)")
        total_changed += changed

    verb = "synced" if args.apply else "would sync"
    print(f"sync_home_cards: {verb} {total_changed} card image(s)")
    for reason, slugs in skipped.items():
        if slugs:
            print(f"  skipped — {reason}: {', '.join(sorted(slugs))}")
    if not args.apply and total_changed:
        print("  report only — re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
