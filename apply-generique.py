#!/usr/bin/env python3
"""
apply-generique.py
==================

Loisirs 74 — apply a category-specific générique (fallback) image to
every card and hero that currently shows a placeholder or empty <img>.

Sources of truth:
  - lieux.json (87 lieux, each has a slug + categories[])
  - /generique-<category>.jpg     ← the 9 fallback files at project root

The rule the user asked for:
  "I want pictures on every single card, every index, hub,
   à proximité card if they exist. I want a generic photo for the ones
   I have not got wikimedia/real yet. One générique per category,
   used across card / index / hub / à proximité, marked as générique."

What this script does:
  1. Loads slug → primary_category from lieux.json.
  2. Walks every hub index (root + 5 langs × 8 categories).
     For each card with <div class="placeholder">…</div>, find the slug
     in the card's link and swap it for the right générique <img>.
  3. Walks every lieu HTML (root + 5 langs).
     - If <img src="..." …alt="…"> in .hero-img is empty, fill it.
     - In the "À proximité" section, swap every placeholder for
       the right générique by slug.
  4. Tags every générique image with data-generique="true" so the
     CSS shows a small "Générique" hint in the corner and so any
     future replace-script can find them in one query.

Idempotent: re-running on an already-patched tree is a no-op.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

# 1. category → générique image filename (at site root).
GENERIQUE = {
    'lac':          '/generique-lac.jpg',
    'cascade':      '/generique-cascade.jpg',
    'chateau':      '/generique-chateau.jpg',
    'musee':        '/generique-musee.jpg',
    'point-de-vue': '/generique-point-de-vue.jpg',
    'domaine':      '/generique-domaine.jpg',
    'attraction':   '/generique-attraction.jpg',
    'parc':         '/generique-parc.jpg',
    'telecabine':   '/generique-telecabine.jpg',
}

# 2. category → human label (used in alt text in 5 languages).
ALT_TEXT = {
    'fr': {
        'lac':          "Image générique — Lac",
        'cascade':      "Image générique — Cascade",
        'chateau':      "Image générique — Château",
        'musee':        "Image générique — Musée",
        'point-de-vue': "Image générique — Point de vue",
        'domaine':      "Image générique — Base de loisirs",
        'attraction':   "Image générique — Attraction",
        'parc':         "Image générique — Parc",
        'telecabine':   "Image générique — Télécabine",
    },
    'en': {
        'lac':          "Generic image — Lake",
        'cascade':      "Generic image — Waterfall",
        'chateau':      "Generic image — Castle",
        'musee':        "Generic image — Museum",
        'point-de-vue': "Generic image — Viewpoint",
        'domaine':      "Generic image — Leisure park",
        'attraction':   "Generic image — Attraction",
        'parc':         "Generic image — Park",
        'telecabine':   "Generic image — Cable car",
    },
    'de': {
        'lac':          "Generisches Bild — See",
        'cascade':      "Generisches Bild — Wasserfall",
        'chateau':      "Generisches Bild — Schloss",
        'musee':        "Generisches Bild — Museum",
        'point-de-vue': "Generisches Bild — Aussichtspunkt",
        'domaine':      "Generisches Bild — Freizeitpark",
        'attraction':   "Generisches Bild — Attraktion",
        'parc':         "Generisches Bild — Park",
        'telecabine':   "Generisches Bild — Seilbahn",
    },
    'it': {
        'lac':          "Immagine generica — Lago",
        'cascade':      "Immagine generica — Cascata",
        'chateau':      "Immagine generica — Castello",
        'musee':        "Immagine generica — Museo",
        'point-de-vue': "Immagine generica — Punto panoramico",
        'domaine':      "Immagine generica — Area ricreativa",
        'attraction':   "Immagine generica — Attrazione",
        'parc':         "Immagine generica — Parco",
        'telecabine':   "Immagine generica — Funivia",
    },
    'es': {
        'lac':          "Imagen genérica — Lago",
        'cascade':      "Imagen genérica — Cascada",
        'chateau':      "Imagen genérica — Castillo",
        'musee':        "Imagen genérica — Museo",
        'point-de-vue': "Imagen genérica — Mirador",
        'domaine':      "Imagen genérica — Área de ocio",
        'attraction':   "Imagen genérica — Atracción",
        'parc':         "Imagen genérica — Parque",
        'telecabine':   "Imagen genérica — Teleférico",
    },
}


# 3. Load slug → primary category from lieux.json.
def load_slug_category() -> dict[str, str]:
    """Primary category is the first one in the list; fall back to 'domaine'."""
    with open(ROOT / 'lieux.json', encoding='utf-8') as f:
        data = json.load(f)
    out = {}
    for lieu in data['lieux']:
        cats = lieu.get('categories', [])
        out[lieu['slug']] = cats[0] if cats else 'domaine'
    return out


# 4. Detect which language a path belongs to.
def detect_lang(path: Path) -> str:
    parts = path.parts
    for p in parts:
        if p in ('en', 'de', 'it', 'es'):
            return p
    return 'fr'


# 5. The générique-img HTML for a given category + language.
def generique_img(category: str, lang: str, eager: bool = False) -> str:
    """
    Build an <img> tag that:
      - points to /generique-<cat>.jpg
      - is tagged data-generique="true" so we can find it later
      - has multilingual alt
      - is lazy by default, eager for hero (one per page)
    """
    src = GENERIQUE.get(category, GENERIQUE['domaine'])
    alt = ALT_TEXT.get(lang, ALT_TEXT['fr']).get(
        category, ALT_TEXT.get(lang, ALT_TEXT['fr'])['domaine']
    )
    loading = 'eager' if eager else 'lazy'
    fetchprio = ' fetchpriority="high"' if eager else ''
    return (
        f'<img src="{src}" alt="{alt}" '
        f'loading="{loading}"{fetchprio} '
        f'data-generique="true" data-generique-cat="{category}">'
    )


# 6. Slug extraction from card link.
SLUG_FROM_HREF_RE = re.compile(
    r'href="(?:https?://loisirs74\.fr)?/(?:en/|de/|it/|es/)?'
    r'(?:[a-z-]+/)?'                # optional category prefix (en/lakes/, etc.)
    r'([a-z0-9-]+)"\s*(?:[^>]*?)?'
    r'\s*class="card-photo"',
    re.IGNORECASE,
)


# 7. Walk hub indexes and replace card placeholders.
PLACEHOLDER_BLOCK_RE = re.compile(
    r'(<a href="(?P<href>[^"]+)"\s+class="card-photo">\s*)'
    r'<div class="placeholder">.*?</div>',
    re.DOTALL,
)


def slug_from_href(href: str) -> str | None:
    """Strip protocol/lang/category prefix → bare slug."""
    h = href.rstrip('/')
    # remove https://loisirs74.fr if present
    h = re.sub(r'^https?://[^/]+', '', h)
    # split, take last non-empty segment
    parts = [p for p in h.split('/') if p]
    if not parts:
        return None
    last = parts[-1]
    # if the last part is a known hub directory, this isn't a lieu link
    if last in (
        'lacs', 'cascades', 'chateaux', 'musees', 'attractions',
        'bases-de-loisirs', 'points-de-vue', 'telecabines',
        'lakes', 'waterfalls', 'castles', 'museums',
        'leisure-parks', 'viewpoints', 'cable-cars',
        'seen', 'wasserfaelle', 'schloesser', 'museen',
        'attraktionen', 'freizeitparks', 'assichtspunkte', 'seilbahnen',
        'laghi', 'cascate', 'casteli', 'musei',
        'attrazioni', 'aree-recreative', 'punti-punoramici', 'funivie',
        'lagos', 'cascadas', 'castillos', 'museos',
        'atraciones', 'areas-de-ocio', 'miradores', 'telefericos',
    ):
        return None
    return last


def patch_hub_card_placeholders(html: str, lang: str, slug_cat: dict[str, str]) -> tuple[str, int]:
    """
    Replace <a class="card-photo"><div class="placeholder">…</div></a>
    with <a class="card-photo"><img générique></a> using the slug → category
    derived from the link.

    Returns (new_html, n_replaced).
    """
    n = 0

    def replace(m: re.Match) -> str:
        nonlocal n
        href = m.group('href')
        slug = slug_from_href(href)
        if not slug:
            return m.group(0)  # not a lieu link, skip
        cat = slug_cat.get(slug)
        if not cat:
            return m.group(0)  # unknown slug, skip
        n += 1
        return m.group(1) + generique_img(cat, lang, eager=False)

    new_html = PLACEHOLDER_BLOCK_RE.sub(replace, html)
    return new_html, n


# 8. Replace hero <img src=""> (empty) with générique for that lieu.
EMPTY_HERO_IMG_RE = re.compile(
    r'<img\s+src=""(\s+alt="[^"]*")\s+width="\d+"\s+height="\d+"\s+fetchpriority="high">',
    re.IGNORECASE,
)


def patch_lieu_hero(html: str, slug: str, lang: str, slug_cat: dict[str, str]) -> tuple[str, bool]:
    cat = slug_cat.get(slug)
    if not cat:
        return html, False
    if not EMPTY_HERO_IMG_RE.search(html):
        return html, False

    src = GENERIQUE.get(cat, GENERIQUE['domaine'])
    alt_default = ALT_TEXT.get(lang, ALT_TEXT['fr'])[cat]

    def replace(m: re.Match) -> str:
        # keep the page's own alt= if present (and not empty); else use ours
        alt_attr = m.group(1).strip()  # e.g. alt="Lac Cornu…"
        alt_match = re.search(r'alt="([^"]*)"', alt_attr)
        alt = alt_match.group(1) if alt_match and alt_match.group(1) else alt_default
        return (
            f'<img src="{src}" alt="{alt}" '
            f'width="1600" height="1200" fetchpriority="high" '
            f'data-generique="true" data-generique-cat="{cat}">'
        )

    html = EMPTY_HERO_IMG_RE.sub(replace, html, count=1)

    # When we swap in a générique, the previous Wikimedia credit attribution
    # (e.g. "Guilhem Vellut · CC BY 2.0 · Wikimedia Commons") is now FALSE.
    # Strip the hero-credit div entirely on those pages — the CSS marker
    # shows "Générique" instead, which is honest.
    html = re.sub(
        r'<div class="hero-credit">.*?</div>',
        '',
        html,
        count=1,
        flags=re.DOTALL,
    )

    return html, True


# 9. CSS hint marker — add a small "Générique" tag in the corner.
GENERIQUE_CSS = """
/* ===== GÉNÉRIQUE FALLBACK MARKER =====
   When an image is using the category-level générique fallback
   (data-generique="true"), the image's parent gets a small
   "Générique" tag in the corner. This is intentional — it lets
   us see at a glance which images are still placeholders waiting
   for a real photo. */
[data-generique="true"] {
  /* placement only; the marker is on the parent via ::after */
}
.card-photo:has(> img[data-generique="true"])::after,
.hero-img:has(> img[data-generique="true"])::after,
.hero-bg:has(> img[data-generique="true"])::after {
  content: "Générique";
  position: absolute;
  bottom: .45rem;
  right: .45rem;
  background: rgba(13, 26, 15, 0.78);
  color: #f0dfc0;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.18rem 0.5rem;
  border-radius: 3px;
  pointer-events: none;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 2;
}
.card-photo, .hero-img, .hero-bg {
  position: relative;
}
"""


def inject_generique_css(html: str) -> tuple[str, bool]:
    """Inject the CSS rule once per file, just before </style> of the first <style> block."""
    if 'GÉNÉRIQUE FALLBACK MARKER' in html:
        return html, False  # already injected
    # add to the first </style>
    idx = html.find('</style>')
    if idx == -1:
        return html, False
    new_html = html[:idx] + GENERIQUE_CSS + html[idx:]
    return new_html, True


# 10. Main runner.
def main():
    slug_cat = load_slug_category()
    print(f'Loaded {len(slug_cat)} slug → category mappings')
    print()

    n_files = 0
    n_card_placeholders = 0
    n_heroes_filled = 0
    n_css_injected = 0

    # Walk every .html file: root, de/, en/, es/, it/, and hub dirs.
    for html_path in ROOT.rglob('*.html'):
        # Skip non-site files
        rel = html_path.relative_to(ROOT)
        if rel.parts[0] in ('node_modules', 'content', 'api'):
            continue
        if html_path.name in ('404.html',):
            continue

        text = html_path.read_text(encoding='utf-8')
        original = text
        lang = detect_lang(html_path)

        # a. Hub card placeholders (works on all index.html in category dirs
        #    AND on root index.html AND on any lieu page's à-proximité section,
        #    because they all use the same <a class="card-photo"><div class="placeholder">… markup).
        text, n_cards = patch_hub_card_placeholders(text, lang, slug_cat)
        n_card_placeholders += n_cards

        # b. Lieu hero (only on actual lieu pages — those are named <slug>.html
        #    in root or in /<lang>/. Hub indexes are index.html under a dir.)
        if html_path.name != 'index.html':
            # bare slug = filename without .html
            slug = html_path.stem
            text, hero_changed = patch_lieu_hero(text, slug, lang, slug_cat)
            if hero_changed:
                n_heroes_filled += 1

        # c. Inject CSS marker (every page that got at least one replacement,
        #    OR any page with markup that could benefit — easier to be uniform).
        text, css_added = inject_generique_css(text)
        if css_added and (text != original or n_cards or html_path.name != 'index.html'):
            n_css_injected += 1
        elif css_added and text == original:
            # we added CSS but no images need it — revert to avoid bloat
            text = original

        if text != original:
            html_path.write_text(text, encoding='utf-8')
            n_files += 1

    print(f'Files modified:           {n_files}')
    print(f'Card placeholders → img:  {n_card_placeholders}')
    print(f'Empty heroes filled:      {n_heroes_filled}')
    print(f'CSS marker injected in:   {n_css_injected} files')


if __name__ == '__main__':
    main()
