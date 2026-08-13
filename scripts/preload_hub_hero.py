#!/usr/bin/env python3
"""preload_hub_hero.py — let the browser discover the hub banner immediately.

WHY
  The hub/commune banner is painted by a CSS pseudo-element:

      .hub-hero::before { background: var(--hub-hero-img) center 55%/cover … }
      --hub-hero-img: url("/img/generique/generique-cascade.jpg")

  A background image is invisible to the browser's preload scanner. The scanner
  reads the raw HTML and starts fetching what it can see; a URL that only exists
  inside a CSS custom property is not found until the stylesheet has been
  downloaded, parsed, and the rule matched against the element. On these pages
  that banner IS the Largest Contentful Paint element, so the whole LCP waits
  on a discovery step that a plain <img> would never have paid.

  Measured, loisirs74.fr, 24h to 2026-08-13 (Cloudflare RUM, bots excluded):
      LCP  P50 1,162ms · P75 1,713ms · P90 2,680ms · P99 10,884ms
  The P99 was one load of /cascades/ — this exact banner, at 10,884ms. Preload
  moves the fetch to the first moments of the page instead of after the CSS
  round-trip.

WHAT IT DOES
  For every page carrying --hub-hero-img, emit in <head>:

      <link rel="preload" as="image" href="…" fetchpriority="high">

  The href is read from the page's own --hub-hero-img, never restated here, so
  the two can't drift the way an authored copy would.

WHAT IT WILL NOT DO
  * Preload a file that is not on disk. A preload for a missing resource is
    pure waste plus a console warning, and would quietly outlive the image.
  * Preload a banner that is not actually rendered — the page must carry
    class="hub-hero", not merely define the variable.

  This is safe to apply to every breakpoint because --hub-hero-img has no
  @media override anywhere: one page, one banner image, all viewports. If that
  ever changes, this script must learn about it — a preload for an image the
  viewport does not use is bandwidth spent on nothing.

Idempotent: a page already preloading the right image is skipped. A page
preloading a DIFFERENT image is rewritten — that is the repair path, for when
a hub's banner is changed.

Usage:
    python3 scripts/preload_hub_hero.py            # report, writes nothing
    python3 scripts/preload_hub_hero.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ("_site", ".git", "node_modules", "scripts", "reports", "Json", "api", "content")

HERO_VAR_RE = re.compile(r'--hub-hero-img:\s*url\("([^"]+)"\)')
# our own tag, marked so it is never confused with a hand-written preload
PRELOAD_RE = re.compile(
    r'<link rel="preload" as="image" href="([^"]*)" fetchpriority="high"><!--hub-hero-->'
)


def tag(href):
    return (f'<link rel="preload" as="image" href="{href}" fetchpriority="high">'
            f'<!--hub-hero-->')


def main():
    ap = argparse.ArgumentParser(description="Preload the hub banner image sitewide.")
    ap.add_argument("--apply", action="store_true", help="write changes (default: report only)")
    args = ap.parse_args()

    seen = added = repaired = 0
    no_head = missing_file = no_banner = 0
    missing_examples = set()

    for fp in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(fp, ROOT)
        if rel.split(os.sep)[0] in SKIP_DIRS:
            continue
        html = open(fp, encoding="utf-8").read()

        m = HERO_VAR_RE.search(html)
        if not m:
            continue
        if 'class="hub-hero"' not in html:
            no_banner += 1          # defines the variable but paints no banner
            continue
        seen += 1
        href = m.group(1)

        if not os.path.isfile(os.path.join(ROOT, href.lstrip("/"))):
            missing_file += 1
            missing_examples.add(href)
            continue

        existing = PRELOAD_RE.search(html)
        if existing:
            if existing.group(1) == href:
                continue                                   # already correct
            new = PRELOAD_RE.sub(tag(href), html, count=1)
            repaired += 1
        else:
            if "<head>" not in html:
                no_head += 1
                continue
            # first thing in <head>: the scanner reads top-down, and every byte
            # before the preload is a byte of delay on the LCP element.
            new = html.replace("<head>", "<head>\n" + tag(href), 1)
            added += 1

        if args.apply:
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(new)

    verb = "" if args.apply else "would "
    print(f"preload_hub_hero: {seen} banner page(s) · {verb}add {added} · {verb}repair {repaired}")
    if missing_file:
        print(f"  ⚑ skipped — banner image not on disk ({missing_file} page(s)): "
              f"{', '.join(sorted(missing_examples))}")
    if no_head:
        print(f"  skipped (no <head>): {no_head}")
    if no_banner:
        print(f"  skipped (defines --hub-hero-img but renders no .hub-hero): {no_banner}")
    if not args.apply and (added or repaired):
        print("  report only — re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
