#!/usr/bin/env python3
"""build_card_variants.py — card-sized derivatives, because a card is 290 px.

shrink_heroes capped every hero at 1600 px, which is right for a FICHE HERO:
it sits in a ~480 CSS px column, so 2x DPR wants ~960. Nobody sized the CARDS,
and the cards are where most of the bytes are spent. Measured from the stylesheet
rather than guessed:

    mobile  (<=680px)  .carousel > .card { flex:0 0 70vw; max-width:17rem }
                       -> at most 272 CSS px
    desktop (>680px)   .carousel { repeat(auto-fill, minmax(15rem,1fr)) }
                       inside .wrap { max-width:1280px; padding clamp(…,2rem) }
                       -> 1216 px of content, gap 1.2rem, 4 columns max
                       -> (1216 - 3*19.2) / 4 = 289.6 CSS px

So a card is never wider than ~290 CSS px and is being served a 1600 px file —
5.5x the pixels in each dimension, ~30x the area. PageSpeed measured the homepage
at 18.8 MB total with 8,822 KiB of that attributable to oversized local images.

WIDTH: 600 only. It covers 2x DPR on a 290 px card exactly, and on a 3x phone it
still delivers ~2.07x — imperceptible on a small photo. A 900 px tier was built,
measured and dropped: 467 more files and 56.6 MB of repo weight (on a 247 MB
img/, cloned by every CI run and every deploy) to serve a density difference
nobody can see at that size. Adding it back is one tuple and a re-run.

WEBP ONLY, deliberately. The markup is
`<picture><source srcset=…webp><img src=…jpg></picture>`, so every browser that
understands srcset also takes the webp `<source>`; the jpg exists for browsers
that have neither. Generating jpg variants too would double the files to serve a
population that cannot use srcset anyway. This is the same fact that bit the hero
re-encode from the other side: browsers take the <source>, so the webp is the
file that ships.

NEVER UPSCALES, and never writes a variant that does not pay. A source already
at or below the target width is skipped — a "variant" the same size as the
original is pure duplication. A re-encode that saves less than MIN_GAIN is also
skipped, the rule shrink_heroes learned when blind re-encoding made some webp
files LARGER than the originals.

Idempotent AND cheap to re-run, because build_all runs it on every build:
data/card-variants.json records the sha1 of the source each variant was made
from. A stem whose source hash matches and whose variant exists is skipped
WITHOUT decoding — hashing 247 MB takes about a second, re-encoding it at
method=6 takes ten minutes. A replaced hero changes its hash and is redone.

    python3 scripts/build_card_variants.py [--apply] [--report]
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"

WIDTHS = (600,)
Q_WEBP = 82
MIN_GAIN = 0.10          # a variant must save >=10% over the file it replaces
VARIANT_SUFFIXES = tuple(f"-{w}.webp" for w in WIDTHS)


def is_variant(p: Path) -> bool:
    return p.name.endswith(VARIANT_SUFFIXES)


def sources():
    """One source per STEM, originals only, never a variant of one.

    `hero.jpg` and `hero.webp` are the same picture and both derive the same
    `hero-600.webp`, so iterating files encodes 401 of the 583 stems twice and
    the winner is whichever happened to run last — 1,772 encodes for 983 files,
    and output that depends on directory order. Deduplicate by stem and prefer
    the JPG: it is the file shrink_heroes wrote from the camera original, so
    re-encoding it compounds one generation of loss instead of two."""
    best: dict[str, Path] = {}
    for p in sorted(IMG.rglob("*")):
        if p.suffix.lower() not in (".jpg", ".webp") or is_variant(p):
            continue
        stem = os.path.splitext(str(p))[0]
        if stem not in best or p.suffix.lower() == ".jpg":
            best[stem] = p
    return [best[k] for k in sorted(best)]


def encode(im: Image.Image, width: int) -> bytes | None:
    """Resize to `width` and encode to webp in memory. None if it would upscale."""
    if im.width <= width:
        return None
    h = round(im.height * width / im.width)
    out = io.BytesIO()
    im.resize((width, h), Image.LANCZOS).save(out, "WEBP", quality=Q_WEBP, method=6)
    return out.getvalue()


MANIFEST = ROOT / "data" / "card-variants.json"


def _sha(p: Path) -> str:
    import hashlib
    return hashlib.sha1(p.read_bytes()).hexdigest()[:16]


def main():
    import json
    apply = "--apply" in sys.argv
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    new_manifest = {}
    written = skipped = cached = 0
    before = after = 0
    for src in sources():
        rel_stem = os.path.relpath(os.path.splitext(str(src))[0], ROOT)
        h = _sha(src)
        targets = [Path(f"{os.path.splitext(str(src))[0]}-{w}.webp") for w in WIDTHS]
        # Fast path: same source as last time and its variants are on disk.
        if manifest.get(rel_stem) == h and all(t.exists() for t in targets):
            new_manifest[rel_stem] = h
            cached += 1
            continue
        try:
            with Image.open(src) as im:
                im.load()
                base = os.path.splitext(str(src))[0]
                for w in WIDTHS:
                    dst = Path(f"{base}-{w}.webp")
                    data = encode(im, w)
                    if data is None:
                        skipped += 1
                        continue
                    # Only pay for a variant that actually saves over the file a
                    # browser would otherwise have taken (the webp sibling if one
                    # exists, else this file).
                    sib = Path(base + ".webp")
                    ref = sib if sib.exists() else src
                    ref_size = ref.stat().st_size
                    if len(data) > ref_size * (1 - MIN_GAIN):
                        skipped += 1
                        if dst.exists() and apply:
                            dst.unlink()          # a variant that no longer pays
                        continue
                    before += ref_size
                    after += len(data)
                    written += 1
                    if apply:
                        dst.write_bytes(data)
            new_manifest[rel_stem] = h
        except Exception as e:                       # noqa: BLE001
            print(f"  !! {src}: {e}", file=sys.stderr)
    if apply:
        MANIFEST.write_text(json.dumps(dict(sorted(new_manifest.items())), indent=0) + "\n",
                            encoding="utf-8")
    verb = "wrote" if apply else "would write"
    print(f"card variants: {verb} {written}, skipped {skipped}, unchanged {cached}")
    if written:
        print(f"  a card now costs {after / written / 1024:.0f} KiB instead of "
              f"{before / written / 1024:.0f} KiB on average "
              f"(-{100 * (before - after) // before}%)")

if __name__ == "__main__":
    main()
