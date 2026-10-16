"""Shared `picture_tag()` helper. Emits `<picture><source webp>` with a
JPG fallback when the hero is a local jpg that has a webp sibling, and
a plain `<img>` otherwise (URL heroes, jpg without webp). Always
bakes real width/height to kill CLS — looked up from
`data/img-dims.json` (built by `scripts/build_img_dims.py`).
"""
from __future__ import annotations
import siteconfig  # HANDOFF-73: per-site identity

import html as _html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_DIMS: dict[str, list[int]] = {}


def _load_dims():
    p = ROOT / "data" / "img-dims.json"
    if p.exists():
        _DIMS.update(json.loads(p.read_text(encoding="utf-8")))


_load_dims()


def _attr(s):
    return _html.escape(str(s or ""), quote=True)


def _local_rel(img_src):
    """Return the repo-relative path of `img_src` if it points to a local
    file that exists on disk, else None.

    Accepts either an absolute URL on the production host or a root-
    relative path. Anything else (http://, data:, //) → None.
    """
    if not img_src:
        return None
    for pre in (siteconfig.BASE_URL + "/", "/"):
        if img_src.startswith(pre):
            rel = img_src[len(pre):].lstrip("/")
            if rel and (ROOT / rel).exists():
                return rel
            return None
    return None


# Card-sized derivatives written by scripts/build_card_variants.py. A card is
# never wider than ~290 CSS px (measured: 272 on mobile, 289.6 across the widest
# desktop grid), so 600 covers 2x DPR and still gives ~2x on a 3x phone (a 900
# tier was measured and dropped — see build_card_variants). Only offered on the
# LAZY path: the fiche hero is the LCP element in a ~480 CSS px column and keeps
# its single 1600 px file, where a srcset would only invite the browser to pick
# something smaller for the one image that must not be soft.
_CARD_WIDTHS = (600,)

# A card's slot, straight from the stylesheet it has to match:
#   <=680px  .carousel > .card { flex:0 0 70vw; max-width:17rem }
#   >680px   4 columns of (1216 - 3*19.2)/4 in a 1280px .wrap
# 70vw slightly overstates the mobile slot above a 388 px viewport, which is the
# safe direction to be wrong in: the browser fetches one size too large rather
# than one too small.
_CARD_SIZES = "(max-width: 680px) 70vw, 290px"


def _card_srcset(rel, url_base):
    """`srcset` of the variants that exist on disk for this image, widest last.
    Empty when the generator has not produced any — a source already at or below
    600 px gets none, and the tag falls back to the single full-size file."""
    parts = []
    for w in _CARD_WIDTHS:
        if (ROOT / f"{os.path.splitext(rel)[0]}-{w}.webp").exists():
            parts.append(f"{os.path.splitext(url_base)[0]}-{w}.webp {w}w")
    return parts


def picture_tag(img_src, alt, *, eager=False, extra=""):
    """Render a <picture> if a webp sibling exists for this local jpg,
    else a plain <img>.

    `eager` → fetchpriority="high" (LCP hero); default → loading="lazy"
    decoding="async" for below-fold cards.
    `extra` is verbatim attribute markup appended to the <img>.
    """
    rel = _local_rel(img_src)
    loading_attr = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    wh = ""
    if rel and rel in _DIMS:
        w, h = _DIMS[rel]
        wh = f' width="{w}" height="{h}"'
    img = f'<img src="{_attr(img_src)}" alt="{_attr(alt)}"{wh}{loading_attr}{extra}>'
    if rel and rel.lower().endswith(".jpg"):
        webp_rel = rel[:-4] + ".webp"
        if (ROOT / webp_rel).exists():
            webp_src = img_src[:-4] + ".webp"
            srcset, sizes = _attr(webp_src), ""
            if not eager:
                variants = _card_srcset(rel, img_src)
                if variants:
                    full_w = _DIMS.get(webp_rel, _DIMS.get(rel, [0]))[0]
                    cand = variants + ([f"{_attr(webp_src)} {full_w}w"] if full_w else [])
                    srcset = ", ".join(cand)
                    sizes = f' sizes="{_CARD_SIZES}"'
            return (f'<picture><source srcset="{srcset}"{sizes} '
                    f'type="image/webp">{img}</picture>')
    return img
