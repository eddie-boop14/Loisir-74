#!/usr/bin/env python3
"""shrink_heroes.py — hero images at display size, not camera size.

THE PROBLEM THIS EXISTS FOR
  August self-hosted the heroes, which fixed the hotlinking and the LCP it was
  causing. It shipped the camera originals: 188 hero .webp at 68.4 MB (median
  299 KB, largest 6240x4160 at 3.9 MB) plus 189 .jpg fallbacks at 131.5 MB —
  200 MB, 61 % of img/, for pictures that render in a box about 480 CSS px wide.

  Cloudflare Web Vitals, 7-14 Sept, bots excluded: LCP 94 % good and P75
  1,376 ms, but every element in the poor tail is the hero, and P99 is 6,804 ms.
  The markup was never at fault — fetchpriority="high", aspect-ratio:4/3
  reserving space, no lazy hero. It is purely pixels nobody can see.

WHY 1600
  .hero-img sits in .hero .grid (1.15fr 1fr) inside .wrap (max-width 64rem), so
  the hero column is ~480 CSS px; 2x DPR needs ~960. 1600 is comfortably above
  that on both axes and still an order of magnitude under a 26-megapixel
  original. This never upscales, and re-running it is a no-op.

WHY IT DOES NOT SIMPLY RE-ENCODE EVERYTHING
  Dimensions are only half the weight: 78 files are over 1600 px (101 MB), but
  another 264 sit inside 1600 px and still hold 95 MB because they were saved at
  near-lossless quality. Re-encoding those blindly is wrong in both directions —
  measured on a sample, two jpgs dropped 69-70 %, two moved 4-5 % (so the quality
  loss buys nothing), and two webp files came out LARGER than the originals.

  So a file whose pixels do not change is encoded to memory first and written
  only if the result is at least MIN_GAIN smaller. A file whose pixels DO change
  — resized or rotated — is always written, because the old bytes no longer
  describe the right image.

ORIENTATION
  exif_transpose runs before the resize, then EXIF is dropped, so the stored
  pixels are the displayed pixels and no downstream tool has to honour a tag.
  One file needed it for real: chateau-des-rubins-sallanches-hero.jpg carried
  orientation 6 while its .webp twin carried none, so the pair disagreed — the
  jpg upright, the webp on its side. Browsers take the <source> webp, so the
  sideways one was the one on the site. Where a jpg declares a rotation its
  webp twin is rotated to match, which fixes that page as a side effect.

  EVERY ORIENTATION IS READ BEFORE ANY FILE IS WRITTEN. The first version read
  each jpg's tag lazily inside the loop, and since "…-hero.jpg" sorts before
  "…-hero.webp", the jpg had already been rewritten (EXIF stripped) by the time
  its twin asked — so the webp saw no tag and stayed sideways. The answer to
  "which way up is this pair?" has to be computed from the untouched inputs.

Usage:
    python3 scripts/shrink_heroes.py            # report, writes nothing
    python3 scripts/shrink_heroes.py --apply

2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés
"""
import argparse
import glob
import os
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_EDGE = 1600
Q_WEBP = 82
Q_JPEG = 82
MIN_GAIN = 0.10   # a pixels-unchanged re-encode must save >=10 % or it is skipped
# Pillow's EXIF orientation tag -> the transpose that makes stored == displayed.
ORIENT = {3: Image.ROTATE_180, 6: Image.ROTATE_270, 8: Image.ROTATE_90}


def jpeg_orientation(path):
    """The rotation a jpg asks for, or None. Read from the jpg only: it is the
    format that carries the tag, and its webp twin must follow it."""
    try:
        with Image.open(path) as im:
            o = im.getexif().get(274)
    except Exception:                       # noqa: BLE001 — unreadable EXIF is not an error
        return None
    return ORIENT.get(o)


def _encode(im, path):
    """Encode to memory at our quality. Returns the bytes."""
    import io
    buf = io.BytesIO()
    if path.endswith(".webp"):
        im.save(buf, "WEBP", quality=Q_WEBP, method=6)
    else:
        im.convert("RGB").save(buf, "JPEG", quality=Q_JPEG,
                               progressive=True, optimize=True)
    return buf.getvalue()


def process(path, rotate, apply):
    """Return (before, after, note). after == before when nothing was written."""
    before = os.path.getsize(path)
    with Image.open(path) as src:
        im = ImageOps.exif_transpose(src) or src
        moved = im.size != src.size          # exif_transpose actually turned it

        if rotate is not None and im.width >= im.height:
            # The jpg twin declares a rotation this file has not had applied.
            im = im.transpose(rotate)
            moved = True

        resized = max(im.size) > MAX_EDGE
        if resized:
            im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

        data = _encode(im, path)

    if moved or resized:
        note = "rotated" if moved else "resized"
    elif len(data) <= before * (1 - MIN_GAIN):
        note = "re-encoded"
    else:
        return before, before, None          # leave it alone

    if apply:
        with open(path, "wb") as fh:
            fh.write(data)
    return before, len(data), note


def main():
    ap = argparse.ArgumentParser(description="Resize hero images to display size.")
    ap.add_argument("--apply", action="store_true", help="write (default: report only)")
    ap.add_argument("--max-edge", type=int, default=MAX_EDGE)
    args = ap.parse_args()
    globals()["MAX_EDGE"] = args.max_edge

    heroes = sorted(glob.glob(os.path.join(ROOT, "img", "**", "*-hero.*"), recursive=True))
    heroes = [p for p in heroes if p.lower().endswith((".webp", ".jpg"))]
    if not heroes:
        print("shrink_heroes: no hero images found"); return 1

    # Snapshot every jpg's declared rotation BEFORE writing anything — see the
    # docstring. Reading it lazily makes the result depend on filename order.
    orientations = {os.path.splitext(p)[0]: jpeg_orientation(os.path.splitext(p)[0] + ".jpg")
                    for p in heroes}

    before = after = 0
    touched = rotated = skipped = 0
    for path in heroes:
        rot = orientations[os.path.splitext(path)[0]]
        b, a, note = process(path, rot, args.apply)
        before += b
        after += a
        if note is None:
            skipped += 1
            continue
        touched += 1
        if note == "rotated":
            rotated += 1
            print(f"  ⟳ rotated so stored == displayed: {os.path.relpath(path, ROOT)}")

    verb = "" if args.apply else "would "
    print(f"shrink_heroes: {len(heroes)} file(s) · {verb}rewrite {touched} · "
          f"left alone {skipped}")
    if rotated:
        print(f"  {rotated} rotated so stored pixels == displayed pixels")
    print(f"  {before/1048576:.1f} MB {'→' if args.apply else 'would become'} "
          f"{after/1048576:.1f} MB ({100*(before-after)/before:.0f}% smaller)")
    if not args.apply:
        print("  report only — re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
