#!/usr/bin/env python3
"""One-shot pass that wraps every `<img>` inside an `<article class="card">`
in a `<picture>` element (with webp source) and bakes width/height.

Why a separate pass: `build_homepage.py` extracts card blocks verbatim
from the previous index.html — its section-id mapping is upstream-
broken so we don't invoke it. Hub pages already emit `<picture>` via
`build_hubs.py` (Phase 4 wiring). This pass closes the gap on the 5
locale homepages (and any other HTML where a card still has a plain
`<img>`).

Idempotent: skips `<article>` blocks that already contain `<picture>`.

REWRITTEN 16 Oct 2026 — it never ran, and its idempotency rule was wrong.

It was a one-shot pass, wired into neither build_all nor CI, so every card
added after its single run stayed a bare <img>: 28 local cards on the FR
homepage alone when this was found. Same rot as build_img_dims.py and the 73's
lastmod manifest — a script that is right once and then never again.

And "skip any card that already has a <picture>" froze the 41 that did. When
card-sized variants arrived (build_card_variants.py), picture_tag learned to
emit a 600w srcset — and not one homepage card could ever receive it, because
the homepage is authored chrome no builder regenerates and sync_home_cards only
rewrites src paths by regex. The homepage was the page the variants were FOR
(PageSpeed: 18.8 MB, 8,822 KiB of it oversized local images), and it was the
one page they could not reach.

Now: every LOCAL card image on the twelve homepages is rendered through
picture_tag(), the single canonical renderer, and replaced when it differs.
Idempotent by construction — a second run renders the same bytes and writes
nothing. Remote (hotlinked) images are left exactly as they are: picture_tag
would emit a plain <img> for them anyway, and sync_home_cards owns that
decision. Runs after sync_home_cards, which decides WHICH image a card shows;
this decides HOW it is written.
"""
from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO / "scripts"))
from picture_tag import picture_tag

ARTICLE_RE = re.compile(
    r'(<article class="card"[^>]*>)(.*?)(</article>)',
    re.S,
)

# Inside a card's photo anchor: an existing <picture>…</picture>, or a bare <img>.
IMG_BLOCK_RE = re.compile(r'<picture>.*?</picture>|<img\b[^>]*>', re.S)
PHOTO_RE = re.compile(r'(<a class="card-photo"[^>]*>)(.*?)(</a>)', re.S)


def _src_of(img_attrs: str) -> str:
    m = re.search(r'\bsrc="([^"]+)"', img_attrs)
    return m.group(1) if m else ""


def _alt_of(img_attrs: str) -> str:
    m = re.search(r'\balt="([^"]*)"', img_attrs)
    return _html.unescape(m.group(1)) if m else ""


def _is_local(src: str) -> bool:
    return src.startswith("/") or src.startswith("https://loisirs74.fr/")


def _canonical(block: str) -> str:
    """The card image as picture_tag would write it today, or the block itself
    when it is a hotlink (left for sync_home_cards to own)."""
    m = re.search(r'<img\b([^>]*)>', block)
    if not m:
        return block
    attrs = m.group(1)
    src = _src_of(attrs)
    if not src or not _is_local(src):
        return block
    return picture_tag(src, _alt_of(attrs), eager=False,
                       extra=' referrerpolicy="no-referrer"')


def _upgrade(card: str) -> str:
    def photo(m):
        head, inner, tail = m.groups()
        im = IMG_BLOCK_RE.search(inner)
        if not im:
            return m.group(0)
        new = _canonical(im.group(0))
        return head + inner[:im.start()] + new + inner[im.end():] + tail
    return PHOTO_RE.sub(photo, card)


def homepages():
    import locales
    yield REPO / "index.html"
    for lg in locales.VISIBLE_SECONDARY:
        p = REPO / lg / "index.html"
        if p.exists():
            yield p


def main():
    apply = "--apply" in sys.argv
    touched = rewrites = 0
    for p in homepages():
        txt = p.read_text(encoding="utf-8")
        count = 0

        def article_repl(m):
            nonlocal count
            whole = m.group(0)
            new = _upgrade(whole)
            if new != whole:
                count += 1
            return new

        new = ARTICLE_RE.sub(article_repl, txt)
        if new != txt:
            touched += 1
            rewrites += count
            if apply:
                p.write_text(new, encoding="utf-8")
    verb = "rewrote" if apply else "would rewrite"
    print(f"upgrade_card_pictures: {verb} {rewrites} card image(s) across {touched} homepage(s)")

if __name__ == "__main__":
    main()
