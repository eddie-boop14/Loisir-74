#!/usr/bin/env python3
"""build_hubs.py — regenerate the 9 basic category hubs from Json/, all locales.

For each canonical category (cascade, chateau, musee, point-de-vue, sentier,
telecabine, voie-verte, lac/plage, domaine/parc) we own a hub directory in FR
and a mirror per locale. Each hub's `<main>` block is rebuilt: every fiche
matching the filter rule is rendered as a commune-grouped card.

We DO NOT touch:
  - thematic hubs (baignade-nautisme, sport-jeux, sorties-detente,
    sensations-plein-air, parcs-jardins, que-faire) — they're curated
    cross-cuts that build_hubs would not be able to reproduce faithfully.
    Orphans falling under those hubs remain known JOB 7 fodder.
  - anything outside <main>…</main> — the intro copy, filters, FAQ, footer,
    JSON-LD are all preserved byte-faithfully.

Idempotent: two consecutive runs produce identical files.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture_tag import picture_tag
LOCALES = ("en", "de", "it", "es", "nl")

# Filter rules per hub. Basic + thematic hubs that can be derived from
# category/subcategories deterministically.
# Curated cross-cuts for the détente/wellness/hands-on identity. Source of truth
# for the non-cinema/casino members of sorties-detente, so membership is declared
# here instead of being scraped from baked HTML. Cross-listing is intentional
# (a lieu may also appear in its own category hub — e.g. the two musées below).
CURATED_SORTIES = {
    # ateliers (hands-on)
    "atelier-poterie-chez-el-annecy",
    "atelier-poterie-du-prunier-thones",
    "atelier-poterie-ryokan-thones",
    # wellness
    "spa-qc-terme-chamonix",
    "spa-vitam-bien-etre-neydens",
    "thermes-saint-gervais-mont-blanc",
    # cross-cuts (kept in their own category; cross-listed here)
    "thermes-evian",                     # category=chateau (Anciens Thermes) — cross-list, not recategorised
    "musee-poterie-savoyarde-filliere",  # category=musee — sibling of the poterie ateliers
    "maison-fromage-abondance-abondance",  # category=musee — cheese atelier/visit
    # artisan/terroir batch 2 (category=divers; draft until COORDS/HERO/hours cleared)
    "cooperative-reblochon-le-farto-thones",
    "atelier-chocolat-faverges-seythenex",
    "distillerie-des-aravis-la-clusaz",
    "brasserie-artisanale-du-leman-allinges",
    "cooperative-fruitiere-mont-saleve-cruseilles",
}

HUB_FILTERS = {
    "cascades":         lambda d: d.get("category") == "cascade",
    "chateaux":         lambda d: d.get("category") == "chateau",
    "musees":           lambda d: d.get("category") == "musee",
    "points-de-vue":    lambda d: d.get("category") == "point-de-vue",
    "sentiers":         lambda d: d.get("category") == "sentier",
    "telecabines":      lambda d: d.get("category") == "telecabine",
    "voies-vertes":     lambda d: d.get("category") == "voie-verte",
    "lacs-plages":      lambda d: d.get("category") in ("lac", "plage"),
    "bases-de-loisirs": lambda d: d.get("category") in ("domaine", "parc", "base-nautique", "wakepark", "accrobranche"),
    # Thematic but deterministic
    "parcs-jardins":    lambda d: d.get("category") in ("parc", "jardin"),
    "baignade-nautisme":lambda d: d.get("category") in ("aquaparc", "croisiere", "base-nautique", "wakepark"),
    "sorties-detente":  lambda d: d.get("category") in ("cinema", "casino") or d.get("slug") in CURATED_SORTIES,
    "sport-jeux":       lambda d: d.get("category") in ("bowling", "karting", "patinoire") or
                                  (isinstance(d.get("subcategories"), list) and
                                   any(s in ("sport","sport-jeux","jeu","arcade") for s in d.get("subcategories"))),
    # Curated cross-cuts: the FR hub holds the canonical curation. We
    # preserve it verbatim (filter returns False) and let build_main_block
    # re-emit the cards through fiche_card_html(d, lang, slug) so every
    # locale gets locale-prefixed URLs. Without this the non-FR hubs were
    # left frozen with FR-canonical card hrefs (audit 2026-06-13).
    "sensations-plein-air": lambda d: False,
    "que-faire":            lambda d: False,
}

# Chrome translations for the card grid
CHROME = {
    "lieu_singular":   {"fr": "lieu", "en": "place", "de": "Ort", "it": "luogo", "es": "lugar", "nl": "plek"},
    "lieu_plural":     {"fr": "lieux", "en": "places", "de": "Orte", "it": "luoghi", "es": "lugares", "nl": "plekken"},
    "free":            {"fr": "Gratuit", "en": "Free", "de": "Kostenlos", "it": "Gratis", "es": "Gratis", "nl": "Gratis"},
    "paid":            {"fr": "Payant", "en": "Paid", "de": "Kostenpflichtig", "it": "A pagamento", "es": "De pago", "nl": "Betaald"},
    "seasonal":        {"fr": "Selon saison", "en": "Seasonal", "de": "Saisonal", "it": "Stagionale", "es": "Por temporada", "nl": "Seizoensgebonden"},
    "google_maps":     {"fr": "Google Maps", "en": "Google Maps", "de": "Google Maps", "it": "Google Maps", "es": "Google Maps", "nl": "Google Maps"},
    "official_site":   {"fr": "Site officiel", "en": "Official site", "de": "Offizielle Website", "it": "Sito ufficiale", "es": "Sitio oficial", "nl": "Officiële site"},
}


def hub_locale_map(hub_dir):
    """Pull locale hub names from the FR hub's hreflang block."""
    p = ROOT / hub_dir / "index.html"
    h = p.read_text(encoding="utf-8")
    m = {"fr": hub_dir}
    for mt in re.finditer(
        r'<link rel="alternate" hreflang="([^"]+)" href="https://loisirs74\.fr/(?:([a-z]+)/)?([a-z-]+)/?"',
        h
    ):
        lang, prefix, name = mt.group(1), mt.group(2), mt.group(3)
        if lang in ("en","de","it","es","nl"):
            m[lang] = name
    return m


# ---------------------------------------------------------------------------
# Phase 4 — description-driven photo picker
# ---------------------------------------------------------------------------

# Minimal FR stopword list — purely structural words that carry no fiche
# signal. Kept short and predictable for idempotency.
_STOPWORDS_FR = {
    "de","la","le","les","du","des","et","en","un","une","à","au","aux",
    "avec","pour","sur","par","ou","est","sont","dans","plus","aussi",
    "très","que","qui","se","il","elle","ce","ces","cette","son","sa",
    "ses","si","mais","donc","car","ne","pas","au","aux","si","non","oui",
    "comme","tout","tous","toutes","toute","quelque","entre","sous","vers",
    "depuis","après","avant","être","avoir","fait","faire","peut","aussi",
    "ainsi","leur","leurs","puis","encore","déjà",
}


def _load_photo_index():
    p = ROOT / "data" / "photo-index.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _fiche_words(d):
    """Extract description keywords from a fiche's FR text fields."""
    fr = d.get("i18n", {}).get("fr", {}) or {}
    parts = [fr.get("name", "") or "",
             fr.get("meta_description", "") or "",
             fr.get("short_intro", "") or ""]
    facts = fr.get("facts", {}) or {}
    for v in facts.values():
        if v:
            parts.append(str(v))
    text = " ".join(parts).lower()
    words = re.findall(r"[a-zà-ÿ]+", text)
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS_FR}


def pick_photo(d, photo_index, used_in_hub):
    """Hub-card photo selector.

    2026-06-15: simplified per the architecture decision — `pick_photo`
    now ALWAYS defers to `hero_image` from the fiche JSON. The single
    source of truth for which photo a fiche carries is
    `scripts/pick_generique.py` → `Json/<slug>.json.hero_image`.

    The previous Phase 4 description-keyword scoring + `used_in_hub`
    diversity tracking has been removed because it silently overrode
    `pick_generique.py`'s deliberate family routing on hub cards (a
    re-routed fiche would show its new hero on the catalog index and
    its own fiche page, but a different one on the hub card). That
    contradiction is gone.

    Signature kept stable (photo_index, used_in_hub still accepted) so
    callers in `build_main_block` continue to work; both args are now
    ignored. The returned tuple shape (src, score, basename, reason)
    is also preserved for the assignments-report capture.
    """
    hero = (d.get("hero_image") or "").strip()
    if not hero:
        return (None, None, "", "no hero in JSON")
    # Absolute URL hero (Wikimedia, Unsplash, etc.)
    if hero.startswith(("http://", "https://")):
        return (hero, None, hero.rsplit("/", 1)[-1], "json hero (url)")
    # Local path hero ("/<slug>-hero.jpg" or "/generique-X.jpg")
    if hero.startswith("/"):
        return (f"https://loisirs74.fr{hero}", None,
                hero.lstrip("/").rsplit("/", 1)[-1], "json hero (local)")
    # Bare filename (e.g. "generique-aquatique-toboggan.jpg")
    return (f"https://loisirs74.fr/{hero}", None, hero, "json hero (bare)")


# ---------------------------------------------------------------------------
# Hub <head> patching — title trim + OG block + meta description
# Source of truth for meta descriptions: data/hub-meta-descriptions.json
# (90 entries, 120-160 chars, frozen FR place names, QA-gated by Eddie)
# ---------------------------------------------------------------------------

HUB_TITLE = {
    "cascades": {
        "fr": "Cascades & gorges de Haute-Savoie · Loisirs 74",
        "en": "Waterfalls & gorges of Haute-Savoie · Loisirs 74",
        "de": "Wasserfälle & Schluchten · Haute-Savoie · Loisirs 74",
        "it": "Cascate & gole della Haute-Savoie · Loisirs 74",
        "es": "Cascadas y gargantas de Haute-Savoie · Loisirs 74",
        "nl": "Watervallen & kloven · Haute-Savoie · Loisirs 74",
    },
    "chateaux": {
        "fr": "Châteaux de Haute-Savoie · Loisirs 74",
        "en": "Castles of Haute-Savoie · Loisirs 74",
        "de": "Schlösser der Haute-Savoie · Loisirs 74",
        "it": "Castelli della Haute-Savoie · Loisirs 74",
        "es": "Castillos de Haute-Savoie · Loisirs 74",
        "nl": "Kastelen van Haute-Savoie · Loisirs 74",
    },
    "musees": {
        "fr": "Musées de Haute-Savoie · Loisirs 74",
        "en": "Museums of Haute-Savoie · Loisirs 74",
        "de": "Museen in Haute-Savoie · Loisirs 74",
        "it": "Musei della Haute-Savoie · Loisirs 74",
        "es": "Museos de Haute-Savoie · Loisirs 74",
        "nl": "Musea van Haute-Savoie · Loisirs 74",
    },
    "points-de-vue": {
        "fr": "Points de vue de Haute-Savoie · Loisirs 74",
        "en": "Viewpoints of Haute-Savoie · Loisirs 74",
        "de": "Aussichtspunkte · Haute-Savoie · Loisirs 74",
        "it": "Punti panoramici · Haute-Savoie · Loisirs 74",
        "es": "Miradores de Haute-Savoie · Loisirs 74",
        "nl": "Uitzichtpunten · Haute-Savoie · Loisirs 74",
    },
    "sentiers": {
        "fr": "Sentiers de randonnée · Haute-Savoie · Loisirs 74",
        "en": "Hiking trails · Haute-Savoie · Loisirs 74",
        "de": "Wanderwege · Haute-Savoie · Loisirs 74",
        "it": "Sentieri escursionistici · Haute-Savoie · Loisirs 74",
        "es": "Senderos · Haute-Savoie · Loisirs 74",
        "nl": "Wandelpaden · Haute-Savoie · Loisirs 74",
    },
    "telecabines": {
        "fr": "Télécabines de Haute-Savoie · Loisirs 74",
        "en": "Cable cars of Haute-Savoie · Loisirs 74",
        "de": "Seilbahnen in Haute-Savoie · Loisirs 74",
        "it": "Funivie della Haute-Savoie · Loisirs 74",
        "es": "Teleféricos · Haute-Savoie · Loisirs 74",
        "nl": "Kabelbanen · Haute-Savoie · Loisirs 74",
    },
    "voies-vertes": {
        "fr": "Voies vertes de Haute-Savoie · Loisirs 74",
        "en": "Greenways of Haute-Savoie · Loisirs 74",
        "de": "Grüne Wege · Haute-Savoie · Loisirs 74",
        "it": "Vie verdi della Haute-Savoie · Loisirs 74",
        "es": "Vías verdes · Haute-Savoie · Loisirs 74",
        "nl": "Fietsroutes · Haute-Savoie · Loisirs 74",
    },
    "lacs-plages": {
        "fr": "Lacs & plages de Haute-Savoie · Loisirs 74",
        "en": "Lakes & beaches · Haute-Savoie · Loisirs 74",
        "de": "Seen & Strände · Haute-Savoie · Loisirs 74",
        "it": "Laghi & spiagge · Haute-Savoie · Loisirs 74",
        "es": "Lagos & playas · Haute-Savoie · Loisirs 74",
        "nl": "Meren & stranden · Haute-Savoie · Loisirs 74",
    },
    "bases-de-loisirs": {
        "fr": "Bases de loisirs · Haute-Savoie · Loisirs 74",
        "en": "Leisure parks · Haute-Savoie · Loisirs 74",
        "de": "Freizeitparks · Haute-Savoie · Loisirs 74",
        "it": "Aree ricreative · Haute-Savoie · Loisirs 74",
        "es": "Áreas de ocio · Haute-Savoie · Loisirs 74",
        "nl": "Recreatieparken · Haute-Savoie · Loisirs 74",
    },
    "baignade-nautisme": {
        "fr": "Baignade & nautisme · Haute-Savoie · Loisirs 74",
        "en": "Swimming & watersports · Haute-Savoie · Loisirs 74",
        "de": "Baden & Wassersport · Haute-Savoie · Loisirs 74",
        "it": "Nuoto & sport acquatici · Haute-Savoie · Loisirs 74",
        "es": "Baño & deportes acuáticos · Haute-Savoie · Loisirs 74",
        "nl": "Zwemmen & watersport · Haute-Savoie · Loisirs 74",
    },
    "parcs-jardins": {
        "fr": "Parcs & jardins de Haute-Savoie · Loisirs 74",
        "en": "Parks & gardens of Haute-Savoie · Loisirs 74",
        "de": "Parks & Gärten · Haute-Savoie · Loisirs 74",
        "it": "Parchi & giardini · Haute-Savoie · Loisirs 74",
        "es": "Parques & jardines · Haute-Savoie · Loisirs 74",
        "nl": "Parken & tuinen · Haute-Savoie · Loisirs 74",
    },
    "que-faire": {
        "fr": "Que faire en Haute-Savoie · Loisirs 74",
        "en": "What to do in Haute-Savoie · Loisirs 74",
        "de": "Was tun in der Haute-Savoie · Loisirs 74",
        "it": "Cosa fare in Haute-Savoie · Loisirs 74",
        "es": "Qué hacer en Haute-Savoie · Loisirs 74",
        "nl": "Wat te doen in Haute-Savoie · Loisirs 74",
    },
    "sensations-plein-air": {
        "fr": "Sensations plein air · Haute-Savoie · Loisirs 74",
        "en": "Outdoor thrills · Haute-Savoie · Loisirs 74",
        "de": "Outdoor-Nervenkitzel · Haute-Savoie · Loisirs 74",
        "it": "Brividi all'aria aperta · Haute-Savoie · Loisirs 74",
        "es": "Sensaciones al aire libre · Haute-Savoie · Loisirs 74",
        "nl": "Buitenavontuur · Haute-Savoie · Loisirs 74",
    },
    "sorties-detente": {
        "fr": "Sorties & détente · Haute-Savoie · Loisirs 74",
        "en": "Outings & relax · Haute-Savoie · Loisirs 74",
        "de": "Ausflüge & Erholung · Haute-Savoie · Loisirs 74",
        "it": "Uscite & relax · Haute-Savoie · Loisirs 74",
        "es": "Salidas & relax · Haute-Savoie · Loisirs 74",
        "nl": "Uitstapjes & ontspanning · Haute-Savoie · Loisirs 74",
    },
    "sport-jeux": {
        "fr": "Sports & jeux · Haute-Savoie · Loisirs 74",
        "en": "Sports & games · Haute-Savoie · Loisirs 74",
        "de": "Sport & Spiele · Haute-Savoie · Loisirs 74",
        "it": "Sport & giochi · Haute-Savoie · Loisirs 74",
        "es": "Deportes & juegos · Haute-Savoie · Loisirs 74",
        "nl": "Sport & spelen · Haute-Savoie · Loisirs 74",
    },
}

OG_LOCALE_TAG = {
    "fr": "fr_FR", "en": "en_US", "de": "de_DE",
    "it": "it_IT", "es": "es_ES", "nl": "nl_NL",
}


def _load_hub_meta_descriptions():
    p = ROOT / "data" / "hub-meta-descriptions.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _attr_escape(s):
    """Escape for HTML attribute (quote=True)."""
    import html as _html
    return _html.escape(s or "", quote=True)


def patch_hub_head(html, canon, lang, slug, descriptions):
    """Replace <title>, <meta name="description">, and the OG block with
    the canonical sources of truth: HUB_TITLE constant + hub-meta-
    descriptions.json. Idempotent.
    """
    import html as _html

    new_title = HUB_TITLE.get(canon, {}).get(lang)
    if not new_title:
        return html  # safety: leave alone if no template

    new_desc = descriptions.get(canon, {}).get(lang)

    # 1) title
    html = re.sub(
        r'<title>[^<]*</title>',
        f'<title>{_html.escape(new_title, quote=False)}</title>',
        html, count=1,
    )

    # 2) meta description — replace the existing one (any attribute order)
    # Idempotency: use subn to detect whether the tag WAS present (count==0
    # means no tag found). Comparing strings would incorrectly fall through
    # when the existing tag already has the same content as the new one,
    # which would then duplicate the tag on every rebuild. Also collapse
    # any pre-existing duplicate copies into one.
    if new_desc:
        esc = _attr_escape(new_desc)
        new_meta = f'<meta content="{esc}" name="description"/>'
        desc_re = re.compile(r'<meta[^>]*name="description"[^>]*/>')
        n = len(desc_re.findall(html))
        if n == 0:
            # No description tag — insert right after the canonical <link>
            html = re.sub(
                r'(<link[^>]*rel="canonical"[^>]*/>)',
                r'\1\n' + new_meta, html, count=1,
            )
        elif n == 1:
            html = desc_re.sub(new_meta, html, count=1)
        else:
            # Multiple copies (drift from earlier builds) — collapse to one
            html = desc_re.sub(new_meta, html, count=1)
            html = desc_re.sub('', html)

    # 3) OG block (og:type, og:site_name, og:locale, og:url, og:title,
    # og:description). og:image stays where it is. Idempotent — replace
    # an existing block of our 6 tags or insert before og:image.
    url = f"https://loisirs74.fr/{slug}/" if lang == "fr" else f"https://loisirs74.fr/{lang}/{slug}/"
    og_html = (
        f'<meta property="og:type" content="website"/>\n'
        f'<meta property="og:site_name" content="Loisirs 74"/>\n'
        f'<meta property="og:locale" content="{OG_LOCALE_TAG[lang]}"/>\n'
        f'<meta property="og:url" content="{url}"/>\n'
        f'<meta property="og:title" content="{_attr_escape(new_title)}"/>\n'
        f'<meta property="og:description" content="{_attr_escape(new_desc or "")}"/>'
    )
    if 'property="og:title"' in html:
        # Replace existing 1-6 of our managed OG tags as one block
        block_re = re.compile(
            r'(?:<meta property="og:(?:type|site_name|locale|url|title|description)"[^>]*/>\s*){1,6}',
            re.IGNORECASE,
        )
        html = block_re.sub(lambda _: og_html + '\n', html, count=1)
    elif 'property="og:image"' in html:
        html = re.sub(
            r'(<meta[^>]*property="og:image"[^>]*/>)',
            og_html + r'\n\1',
            html, count=1,
        )
    else:
        # No OG at all (FR que-faire used to be in this state) —
        # inject everything including og:image before </head>.
        html = html.replace(
            '</head>',
            og_html + '\n<meta property="og:image" content="https://loisirs74.fr/og-image.jpg"/>\n</head>',
            1,
        )
    return html


def acces_value(d):
    """Return the canonical access value for `data-acces` from JSON.

    Phase 3 single source of truth: schema_org.tariff_kind + is_free.
    Returns one of 'seasonal' | 'gratuit' | 'payant' | ''. The empty
    string means the field is intentionally absent (caller can skip
    the data-acces attribute or render it empty).
    """
    so = d.get("schema_org", {}) or {}
    if so.get("tariff_kind") == "seasonal":
        return "seasonal"
    if so.get("is_free") is True:
        return "gratuit"
    if so.get("is_free") is False:
        return "payant"
    return ""


def fiche_card_html(d, lang, slug, picked_photo=None):
    """Render one card. URL = https://loisirs74.fr[/lang]/slug; title + desc from i18n.

    `picked_photo`, when provided, overrides the fiche's hero_image as
    the displayed card photo. Carries (src, score, basename, reason) from
    pick_photo() so the card emits data-photo=basename verbatim.
    """
    i18n = d.get("i18n", {}) or {}
    loc = i18n.get(lang) or {}
    fr = i18n.get("fr") or {}
    name = loc.get("name") or fr.get("name") or slug
    desc = loc.get("meta_description") or fr.get("meta_description") or ""
    desc = desc.strip()[:280]  # cap
    # tariff_kind takes precedence over is_free for the visual tag.
    # "seasonal" → "Selon saison" (mixed-access lieux: site libre · visites guidées payantes)
    # otherwise → is_free True/False → Gratuit/Payant
    so = d.get("schema_org", {}) or {}
    if so.get("tariff_kind") == "seasonal":
        tag_class = "is-seasonal"
        tag_text = CHROME["seasonal"][lang]
    else:
        is_free = bool(so.get("is_free", False))
        tag_class = "is-gratuit" if is_free else "is-payant"
        tag_text = CHROME["free" if is_free else "paid"][lang]
    commune = d.get("commune", "")

    # Hero image: picker-overridden when provided (Phase 4), otherwise
    # fall back to the fiche's hero_image (Phase 3 behaviour).
    if picked_photo is not None and picked_photo[0]:
        img_src = picked_photo[0]
    else:
        hero = d.get("hero_image") or ""
        if hero.startswith(("http://", "https://", "//")):
            img_src = hero
        elif hero.startswith("/"):
            img_src = f"https://loisirs74.fr{hero}"
        elif hero:
            img_src = f"https://loisirs74.fr/{hero}"
        else:
            cat = d.get("category") or "attraction"
            img_src = f"https://loisirs74.fr/img/generique/generique-{cat}.jpg"

    alt = (loc.get("hero_alt") or fr.get("hero_alt") or name)
    lang_prefix = f"/{lang}" if lang != "fr" else ""
    fiche_url = f"https://loisirs74.fr{lang_prefix}/{slug}"
    official = d.get("official_site_url") or ""
    lat = d.get("latitude"); lon = d.get("longitude")
    from urllib.parse import quote
    # Name+commune first → Maps resolves to the real POI; a stored coord can be
    # a centroid/label point and pins off-venue. Coords = last-resort fallback.
    if name and commune:
        maps_url = f"https://www.google.com/maps/search/?api=1&amp;query={quote(name + ', ' + commune + ', Haute-Savoie, France')}"
    elif lat is not None and lon is not None:
        maps_url = f"https://www.google.com/maps/search/?api=1&amp;query={lat},{lon}"
    else:
        maps_url = f"https://www.google.com/maps/search/?api=1&amp;query={quote((name or '') + ', ' + (commune or '') + ', Haute-Savoie, France')}"

    actions = [
        f'<a href="{maps_url}" rel="noopener" target="_blank">{CHROME["google_maps"][lang]}</a>'
    ]
    if official:
        actions.append(
            f'<a href="{official}" rel="noopener" target="_blank">{CHROME["official_site"][lang]}</a>'
        )

    import html as html_lib
    e = lambda s: html_lib.escape(str(s or ""), quote=False)
    a = lambda s: html_lib.escape(str(s or ""), quote=True)

    # Phase 3: emit data-* attributes derived from JSON. Single source of
    # truth = the fiche JSON. Empty values mean "field intentionally
    # absent" — never invented, never inferred at render time.
    # commune is lowercased per the architecture brief; the section-level
    # data-commune attribute keeps original casing for the legacy filter.
    data_commune = (commune or "").lower()
    data_acces   = acces_value(d)
    data_lac     = d.get("lake") or ""
    data_type    = d.get("type") or ""
    # data-photo: basename of the chosen card photo. Phase 4 uses the
    # picker's own basename (so URL-encoding from img_src never leaks
    # into the attribute); Phase 3 fallback derives from img_src.
    if picked_photo is not None and picked_photo[2]:
        data_photo = picked_photo[2]
    elif img_src:
        data_photo = img_src.rsplit("/", 1)[-1]
    else:
        data_photo = ""

    card_img_extra = ' referrerpolicy="no-referrer"'
    return (
        f'<article class="card"'
        f' data-commune="{a(data_commune)}"'
        f' data-acces="{a(data_acces)}"'
        f' data-lac="{a(data_lac)}"'
        f' data-type="{a(data_type)}"'
        f' data-photo="{a(data_photo)}">\n'
        f'<a class="card-photo" href="{fiche_url}">\n'
        f'{picture_tag(img_src, alt, eager=False, extra=card_img_extra)}\n'
        f'<span class="card-tag {tag_class}">{tag_text}</span>\n'
        '</a>\n'
        '<div class="card-body">\n'
        f'<div class="card-commune"><span>{e(commune)}</span></div>'
        f'<a class="title" href="{fiche_url}">{e(name)}</a>\n'
        f'<p class="card-desc">{e(desc)}</p>\n'
        '<div class="card-actions">\n'
        + '\n'.join(actions) + '\n'
        '</div>\n'
        '</div>\n'
        '</article>'
    )


def build_main_block(fiches, lang, hub_name=None, photo_index=None, assignments=None):
    """Render the <main>…</main> content for a hub: commune-grouped cards.

    When `hub_name` is "lacs-plages", each commune-section also carries
    `data-lac="annecy|leman|petits"` derived from each fiche's `lake`
    field (the JSON source of truth). All fiches in a commune share the
    same lake by construction, so reading the first one is sufficient.

    Phase 4: when `photo_index` is provided, `pick_photo()` selects the
    card photo per fiche from the keyword-scored library, tracking
    `used_in_hub` to maximise diversity within the hub. `assignments`
    (optional list) captures (hub, slug, type, photo, score, reason)
    rows for the post-build report. Picks are computed once per hub
    (FR-locale-invariant) so all 6 locale variants render the same
    photo per card — same fiche, same picture across the site.
    """
    used_in_hub = set()
    picks = {}
    if photo_index:
        # Deterministic iteration order = render order (commune asc,
        # then FR name asc). Ensures byte-identical output across runs.
        ordered = sorted(
            fiches,
            key=lambda x: (
                (x[1].get("commune") or "?").lower(),
                (x[1].get("i18n", {}).get("fr", {}).get("name") or x[0]).lower(),
            ),
        )
        for slug, d in ordered:
            pick = pick_photo(d, photo_index, used_in_hub)
            picks[slug] = pick
            if assignments is not None and hub_name and lang == "fr":
                assignments.append((hub_name, slug, d.get("type") or "",
                                    pick[2], pick[1], pick[3]))

    by_commune = defaultdict(list)
    for slug, d in fiches:
        by_commune[d.get("commune", "?")].append((slug, d))
    # Alphabetic order of communes; cards inside commune ordered by name
    parts = ['<main>\n<div class="wrap">']
    for commune in sorted(by_commune, key=lambda c: (c.lower(), c)):
        entries = sorted(by_commune[commune],
                         key=lambda x: (x[1].get("i18n", {}).get("fr", {}).get("name", x[0]).lower()))
        n = len(entries)
        word = CHROME["lieu_singular"][lang] if n == 1 else CHROME["lieu_plural"][lang]
        # Lake attribute for lacs-plages only — derived from JSON `lake` field.
        lac_attr = ""
        if hub_name == "lacs-plages":
            first_lake = entries[0][1].get("lake")
            if first_lake:
                lac_attr = f' data-lac="{first_lake}"'
        parts.append(f'<div class="commune-section" data-commune="{commune}"{lac_attr}>')
        parts.append(f'<div class="commune-head"><h3>{commune}</h3>'
                     f'<span class="commune-count">{n} {word}</span></div>')
        parts.append('<div class="carousel">')
        for slug, d in entries:
            parts.append(fiche_card_html(d, lang, slug, picked_photo=picks.get(slug)))
        parts.append('</div>')
        parts.append('</div>')
    parts.append('</div>\n</main>')
    return "\n".join(parts)


def splice_main(html, new_main):
    """Replace existing <main>…</main> with new_main. Preserve all else."""
    m_re = re.compile(r'<main\b[^>]*>.*?</main>', re.DOTALL)
    if m_re.search(html):
        return m_re.sub(lambda _: new_main, html, count=1)
    # No existing <main>: insert before </body>
    return html.replace("</body>", new_main + "\n</body>", 1)


# Localized label for the empty-value default option of filt-commune.
TOUTES_LES_COMMUNES = {
    "fr": "Toutes les communes", "en": "All towns", "de": "Alle Gemeinden",
    "it": "Tutti i comuni", "es": "Todos los municipios", "nl": "Alle gemeenten",
}


def patch_filt_commune(html, communes, lang):
    """Replace the <select id="filt-commune"> options with exactly the
    communes present in the rendered card set (sorted alphabetically).
    Eliminates ghost commune options structurally.

    Preserves the first "all communes" option with its locale label.
    """
    sel_re = re.compile(r'(<select id="filt-commune">)(.*?)(</select>)', re.DOTALL)
    m = sel_re.search(html)
    if not m:
        return html
    default_label = TOUTES_LES_COMMUNES.get(lang, TOUTES_LES_COMMUNES["fr"])
    opts = [f'<option value="">{default_label}</option>']
    for c in sorted(communes, key=lambda c: (c.lower(), c)):
        opts.append(f'<option value="{c}">{c}</option>')
    return sel_re.sub(lambda _: m.group(1) + ''.join(opts) + m.group(3), html, count=1)


def patch_filt_access_free_toggle(html, has_free):
    """If has_free is False, hide the Gratuit/Free button via the `hidden`
    attribute (preserves DOM for idempotency). Otherwise ensure it's visible.

    Locale-agnostic: we only toggle the `hidden` attribute on the button
    that carries data-v="free".
    """
    # Match the free button with possibly a `hidden` attr already.
    btn_re = re.compile(r'<button(?P<attrs>[^>]*)data-v="free"(?P<rest>[^>]*)>')

    def repl(m):
        attrs = (m.group('attrs') or '') + (m.group('rest') or '')
        # Strip any prior hidden token (idempotency).
        attrs = re.sub(r'\s*\bhidden\b\s*', ' ', attrs).strip()
        if not has_free:
            return f'<button {attrs} data-v="free" hidden>' if attrs else f'<button data-v="free" hidden>'
        return f'<button {attrs} data-v="free">' if attrs else f'<button data-v="free">'

    return btn_re.sub(repl, html, count=1)


# -- Phase 5 ---------------------------------------------------------
# Per-hub filter JS variants. Each hub keeps its own block reflecting
# the filters present on that hub (lacs-plages adds the lake filter; the
# other 13 hubs share the common shape). They all converge on ONE rule:
# they read data-* attributes from cards (and section.dataset.lac for the
# lake filter). No PINS, no paidOf, no .card-tag class queries, no slug
# arrays. The JSON → build → data-* → filter chain is closed.


def _filter_js_common_body(has_lac, sg_label, pl_label):
    """Return the (function(){...})() body used by every hub.

    `has_lac=True` adds the lake selector + a lacMatch term to applyFilters
    (lacs-plages variant). `sg_label`/`pl_label` are the singular/plural
    count labels in the page's locale.
    """
    lac_decls = (
        "  const lacSel=document.getElementById('filt-lac');\n"
        "  let curLac='';\n"
    ) if has_lac else ""
    lac_listener = (
        "  if(lacSel)lacSel.addEventListener('change',e=>{curLac=e.target.value;applyFilters();});\n"
    ) if has_lac else ""
    lac_match_line = (
        "      const lacMatch=!curLac||sec.dataset.lac===curLac;\n"
    ) if has_lac else "      const lacMatch=true;\n"
    return (
        "(function(){\n"
        f'  const SG="{sg_label}",PL="{pl_label}";\n'
        + lac_decls +
        "  const communeSel=document.getElementById('filt-commune');\n"
        "  const accessGroup=document.getElementById('filt-access');\n"
        "  const sortSel=document.getElementById('filt-sort');\n"
        "  const countN=document.getElementById('count-n');\n"
        "  const countLabel=document.getElementById('count-label');\n"
        "  const emptyState=document.getElementById('empty-state');\n"
        "  let curCommune='',curAccess='all',curSort='commune';\n"
        "  function applyFilters(){\n"
        "    let total=0;\n"
        "    document.querySelectorAll('.commune-section').forEach(sec=>{\n"
        + lac_match_line +
        "      let vis=0;\n"
        "      sec.querySelectorAll('.card').forEach(card=>{\n"
        "        const communeMatch=!curCommune||card.dataset.commune===curCommune.toLowerCase();\n"
        "        const acc=card.dataset.acces;\n"
        "        const am=curAccess==='all'||(curAccess==='free'&&(acc==='gratuit'||acc==='seasonal'))||(curAccess==='paid'&&(acc==='payant'||acc==='seasonal'));\n"
        "        const show=lacMatch&&communeMatch&&am;\n"
        "        card.classList.toggle('hidden',!show);\n"
        "        if(show){vis++;total++;}\n"
        "      });\n"
        "      sec.classList.toggle('hidden',vis===0);\n"
        "    });\n"
        "    if(countN)countN.textContent=total;\n"
        "    if(countLabel)countLabel.textContent=total===1?SG:PL;\n"
        "    if(emptyState)emptyState.style.display=total===0?'block':'none';\n"
        "  }\n"
        "  function applySort(){ if(curSort!=='alpha')return;\n"
        "    document.querySelectorAll('.commune-section .carousel').forEach(c=>{Array.from(c.querySelectorAll('.card')).sort((a,b)=>(a.querySelector('a.title')?.textContent||'').localeCompare(b.querySelector('a.title')?.textContent||'')).forEach(x=>c.appendChild(x));}); }\n"
        + lac_listener +
        "  if(communeSel)communeSel.addEventListener('change',e=>{curCommune=e.target.value;applyFilters();});\n"
        "  if(accessGroup)accessGroup.addEventListener('click',e=>{if(e.target.tagName==='BUTTON'){accessGroup.querySelectorAll('button').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');curAccess=e.target.dataset.v;applyFilters();}});\n"
        "  if(sortSel)sortSel.addEventListener('change',e=>{curSort=e.target.value;applySort();});\n"
        "  applyFilters();\n"
        "})();"
    )


# Singular / plural localized labels for the X lieux affichés count.
COUNT_LABELS = {
    "fr": ("lieu affiché",         "lieux affichés"),
    "en": ("place shown",          "places shown"),
    "de": ("Ort angezeigt",        "Orte angezeigt"),
    "it": ("luogo visualizzato",   "luoghi visualizzati"),
    "es": ("lugar mostrado",       "lugares mostrados"),
    "nl": ("plek weergegeven",     "plekken weergegeven"),
}


def build_filter_js_for_hub(hub_name, lang):
    """Return the per-hub filter JS body (no <script> wrapper)."""
    sg, pl = COUNT_LABELS.get(lang, COUNT_LABELS["fr"])
    has_lac = (hub_name == "lacs-plages")
    return _filter_js_common_body(has_lac=has_lac, sg_label=sg, pl_label=pl)


# Marker comment lives on the FR canonical hub so we can detect prior
# Phase 5 emissions and re-write idempotently.
_LACS_PLAGES_COMMENT = "// FILTERS (lake + commune + access + sort) — card-tag mechanism"
_STANDARD_COMMENT    = "// FILTERS (commune + access + sort) — card-tag mechanism"


def patch_hub_filter_js(html, hub_name, lang):
    """Replace the inline filter `<script>` block on this hub with the
    Phase 5 data-* variant. Idempotent: detects an existing applyFilters
    IIFE and swaps it for the new body; runs as no-op if no filter
    script is present (curated hubs without filters).
    """
    new_body = build_filter_js_for_hub(hub_name, lang)
    comment = _LACS_PLAGES_COMMENT if hub_name == "lacs-plages" else _STANDARD_COMMENT
    # Match every variant of the existing filter block on every hub:
    #   // FILTERS (commune + access + sort)
    #   // FILTERS (commune + access + sort) — card-tag mechanism
    #   // FILTERS (lake + commune + access + sort) — card-tag mechanism
    block_re = re.compile(
        r'// FILTERS \([^)]*\)(?:\s*—\s*card-tag mechanism)?\s*\n'
        r'\(function\(\)\{.*?applyFilters.*?\}\)\(\);',
        re.DOTALL,
    )
    if block_re.search(html):
        return block_re.sub(lambda _: comment + "\n" + new_body, html, count=1)
    return html


def load_all_json():
    """Load every Json/<slug>.json. JOB 6: skip draft fiches so they don't
    appear in any hub."""
    out = {}
    for p in sorted((ROOT / "Json").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        # 'unverified' (source-audit) is kept out of hubs exactly like draft.
        if d.get("status") in ("draft", "unverified"):
            continue
        out[p.stem] = d
    return out


def existing_hub_fiches(html_path, exclude_chrome):
    """Pull all internal fiche slugs currently linked from this hub HTML.
    These are the curated cross-references we must preserve."""
    if not html_path.exists():
        return set()
    h = html_path.read_text(encoding="utf-8")
    # Strip locale prefix for matching
    slugs = set()
    for m in re.finditer(r'href="https://loisirs74\.fr/(?:[a-z]+/)?([a-z0-9-]+)/?"', h):
        slugs.add(m.group(1))
    return slugs - exclude_chrome


# Per-locale label for the "all categories" footer nav added when a homepage
# lacks links to one or more hubs.
ALL_CATS_LABEL = {
    "fr": "Toutes les catégories", "en": "All categories", "de": "Alle Kategorien",
    "it": "Tutte le categorie", "es": "Todas las categorías", "nl": "Alle categorieën",
}
# Display name per locale per hub (slug)
HUB_DISPLAY = {
    "cascades":          {"fr":"Cascades","en":"Waterfalls","de":"Wasserfälle","it":"Cascate","es":"Cascadas","nl":"Watervallen"},
    "chateaux":          {"fr":"Châteaux","en":"Castles","de":"Schlösser","it":"Castelli","es":"Castillos","nl":"Kastelen"},
    "musees":            {"fr":"Musées","en":"Museums","de":"Museen","it":"Musei","es":"Museos","nl":"Musea"},
    "points-de-vue":     {"fr":"Points de vue","en":"Viewpoints","de":"Aussichtspunkte","it":"Punti panoramici","es":"Miradores","nl":"Uitzichtpunten"},
    "sentiers":          {"fr":"Sentiers","en":"Trails","de":"Wanderwege","it":"Sentieri","es":"Senderos","nl":"Wandelpaden"},
    "telecabines":       {"fr":"Télécabines","en":"Cable cars","de":"Seilbahnen","it":"Funivie","es":"Teleféricos","nl":"Kabelbanen"},
    "voies-vertes":      {"fr":"Voies vertes","en":"Greenways","de":"Radwege","it":"Vie verdi","es":"Vías verdes","nl":"Fietsroutes"},
    "lacs-plages":       {"fr":"Lacs & plages","en":"Lakes","de":"Seen","it":"Laghi","es":"Lagos","nl":"Meren"},
    "bases-de-loisirs":  {"fr":"Bases de loisirs","en":"Leisure parks","de":"Freizeitparks","it":"Aree ricreative","es":"Áreas de ocio","nl":"Recreatieparken"},
    "parcs-jardins":     {"fr":"Parcs & jardins","en":"Parks & gardens","de":"Parks & Gärten","it":"Parchi & giardini","es":"Parques & jardines","nl":"Parken & tuinen"},
    "baignade-nautisme": {"fr":"Baignade & nautisme","en":"Swimming & watersports","de":"Baden & Wassersport","it":"Nuoto & sport acquatici","es":"Baño & deportes acuáticos","nl":"Zwemmen & watersport"},
    "sorties-detente":   {"fr":"Sorties & détente","en":"Outings & relax","de":"Ausflüge & Erholung","it":"Uscite & relax","es":"Salidas & relax","nl":"Uitstapjes & ontspanning"},
    "sport-jeux":        {"fr":"Sports & jeux","en":"Sports & games","de":"Sport & Spiele","it":"Sport & giochi","es":"Deportes & juegos","nl":"Sport & spelen"},
    "sensations-plein-air": {"fr":"Sensations plein air","en":"Outdoor thrills","de":"Outdoor-Nervenkitzel","it":"Brividi all'aria aperta","es":"Sensaciones al aire libre","nl":"Buitenavontuur"},
    "que-faire":         {"fr":"Que faire ?","en":"What to do","de":"Was unternehmen","it":"Cosa fare","es":"Qué hacer","nl":"Wat te doen"},
}
ALL_BASE_HUBS = list(HUB_DISPLAY.keys())


# Homepage "Sorties & détente" section — curated lead order (real heroes first),
# cards lifted from the locale sorties-detente hub so the homepage can't drift.
CURATED_SORTIES_LEAD = [
    "casino-imperial-palace-annecy", "spa-qc-terme-chamonix",
    "thermes-saint-gervais-mont-blanc", "thermes-evian",
    "atelier-poterie-du-prunier-thones", "cinema-pathe-annecy",
]
SORTIES_SUBLINE = {
    "fr": "Cinémas, casinos, spas et thermes, ateliers — la journée continue, même à l'abri.",
    "en": "Cinemas, casinos, spas and thermal baths, workshops — the day goes on, even indoors.",
    "de": "Kinos, Casinos, Spas und Thermen, Ateliers — der Tag geht weiter, auch im Trockenen.",
    "it": "Cinema, casinò, spa e terme, atelier — la giornata continua, anche al coperto.",
    "es": "Cines, casinos, spas y termas, talleres — el día continúa, incluso a cubierto.",
    "nl": "Bioscopen, casino's, spa's en thermen, ateliers — de dag gaat door, ook binnen.",
}
SEEALL_SVG = ('<svg fill="none" stroke="currentColor" stroke-linecap="round" '
              'stroke-linejoin="round" stroke-width="1.5" viewbox="0 0 24 24">'
              '<line x1="5" x2="19" y1="12" y2="12"></line>'
              '<polyline points="12 5 19 12 12 19"></polyline></svg>')


def _hub_cards_by_slug(hub_html):
    """slug -> its <article class="card">…</article> block from a built hub."""
    out = {}
    for m in re.finditer(r'<article class="card"[^>]*>.*?</article>', hub_html, re.S):
        block = m.group(0)
        sm = (re.search(r'href="https://loisirs74\.fr/(?:[a-z]{2}/)?([a-z0-9-]+)"\s+class="card-photo"', block)
              or re.search(r'class="card-photo"\s+href="https://loisirs74\.fr/(?:[a-z]{2}/)?([a-z0-9-]+)"', block))
        if sm:
            out[sm.group(1)] = block
    return out


def patch_hub_h1(html, fr_hub, lang):
    """Single-source the hub <h1> from HUB_DISPLAY (the same string as title/nav),
    so the homepage, nav, title and h1 read identically per locale. Idempotent."""
    import html as _html
    disp = HUB_DISPLAY.get(fr_hub, {}).get(lang)
    if not disp:
        return html
    return re.sub(r'<h1([^>]*)>.*?</h1>',
                  lambda m: f'<h1{m.group(1)}>{_html.escape(disp, quote=False)}</h1>',
                  html, count=1, flags=re.S)


def patch_homepage_sorties(lang):
    """Inject (or replace) the homepage 'Sorties & détente' section in the rain
    band. Cards are lifted from the locale sorties-detente hub (URLs already
    locale-prefixed → the homepage can't drift from the hub), data-* filter
    attrs stripped to the homepage card shape. Replaces the FR ghost (ViaRhôna +
    casino); adds the section to the 5 locales (absent today). Idempotent."""
    import html as _html
    base = ROOT if lang == "fr" else ROOT / lang
    home = base / "index.html"
    if not home.exists():
        return False
    html = home.read_text(encoding="utf-8")
    hub_slug = hub_locale_map("sorties-detente").get(lang) or "sorties-detente"
    hub_path = base / hub_slug / "index.html"
    if not hub_path.exists():
        return False
    by_slug = _hub_cards_by_slug(hub_path.read_text(encoding="utf-8"))
    cards = []
    for slug in CURATED_SORTIES_LEAD:
        block = by_slug.get(slug)
        if block:
            cards.append(re.sub(r'<article class="card"[^>]*>', '<article class="card">', block, count=1))
    if not cards:
        return False
    prefix = f"/{lang}" if lang != "fr" else ""
    hub_url = f"https://loisirs74.fr{prefix}/{hub_slug}/"
    h2 = _html.escape(HUB_DISPLAY["sorties-detente"][lang], quote=False)
    subline = _html.escape(SORTIES_SUBLINE.get(lang, SORTIES_SUBLINE["fr"]), quote=False)
    sa = re.search(r'<a class="see-all"[^>]*>(.*?)<svg', html, re.S)
    see_label = sa.group(1).strip() if sa else "Voir tout"
    section = (
        '<section class="cat" id="sorties">\n<div class="wrap">\n<div class="cat-head">\n'
        f'<div class="cat-head-left">\n<h2>{h2}</h2>\n<p class="cat-sub">{subline}</p>\n</div>\n'
        f'<a class="see-all" href="{hub_url}">{see_label}\n{SEEALL_SVG}\n</a>\n</div>\n'
        '<div class="carousel">\n' + "\n".join(cards) + '\n</div>\n</div>\n</section>'
    )
    # remove any existing #sorties (FR ghost / prior run), collapsing the
    # surrounding blank lines to a single newline so the pass is idempotent.
    html = re.sub(r'\n*<section class="cat" id="sorties">.*?</section>\n*', '\n', html, flags=re.S)
    if '<section class="all-categories"' in html:
        html = html.replace('<section class="all-categories"', section + '\n<section class="all-categories"', 1)
    elif '</main>' in html:
        html = html.replace('</main>', section + '\n</main>', 1)
    else:
        html = re.sub(r'<footer', section + '\n<footer', html, count=1)
    home.write_text(html, encoding="utf-8")
    return True


def patch_homepage_nearme(lang):
    """Ensure the locale homepage loads /scripts/nearme.js — the script that
    powers the "◎ Près de moi" proximity button (#nearMe). The button ships in
    the homepage chrome, but only l74sort.js (sort-only, no geolocation) was
    included, so the button was bound to nothing. Inject nearme.js right after
    l74sort.js (or before </body>). Idempotent."""
    base = ROOT if lang == "fr" else ROOT / lang
    home = base / "index.html"
    if not home.exists():
        return False
    html = home.read_text(encoding="utf-8")
    if 'src="/scripts/nearme.js"' in html:
        return False
    tag = '<script src="/scripts/nearme.js" defer></script>'
    l74 = '<script src="/scripts/l74sort.js"></script>'
    if l74 in html:
        html = html.replace(l74, l74 + "\n" + tag, 1)
    elif "</body>" in html:
        html = html.replace("</body>", tag + "\n</body>", 1)
    else:
        return False
    home.write_text(html, encoding="utf-8")
    return True


def patch_homepage_completeness(lang):
    """Ensure the locale homepage links to every hub directory that exists on
    disk. If some are missing from the existing nav, add a low-prominence
    'All categories' nav block before </main>. Idempotent."""
    base = ROOT if lang == "fr" else ROOT / lang
    home = base / "index.html"
    if not home.exists(): return False
    html = home.read_text(encoding="utf-8")
    # Build per-locale name → slug lookup
    locale_slugs = {}
    for fr_hub in ALL_BASE_HUBS:
        names = hub_locale_map(fr_hub)
        slug = names.get(lang) or fr_hub
        if (base / slug / "index.html").exists():
            locale_slugs[fr_hub] = slug
    # Which slugs are already linked?
    linked = set(re.findall(rf'href="https://loisirs74\.fr/{lang+"/" if lang!="fr" else ""}([a-z-]+)/?"', html))
    missing = [(fr_hub, slug) for fr_hub, slug in locale_slugs.items() if slug not in linked]
    if not missing: return False
    # Build an "all categories" nav and insert before </main>
    lang_prefix = f"/{lang}" if lang != "fr" else ""
    label = ALL_CATS_LABEL[lang]
    lis = []
    for fr_hub, slug in sorted(locale_slugs.items()):
        disp = HUB_DISPLAY[fr_hub][lang]
        lis.append(f'<li><a href="https://loisirs74.fr{lang_prefix}/{slug}/">{disp}</a></li>')
    nav = (
        '<section class="all-categories" aria-label="' + label + '">'
        f'<div class="wrap"><h2>{label}</h2>'
        '<ul class="all-categories-grid">'
        + ''.join(lis) +
        '</ul></div></section>'
    )
    # Remove a prior copy if present (idempotency)
    html = re.sub(r'<section class="all-categories"[^>]*>.*?</section>', '', html, flags=re.DOTALL)
    # Insert before </main> if present; otherwise before footer
    if '</main>' in html:
        html = html.replace('</main>', nav + '\n</main>', 1)
    else:
        html = html.replace('<footer', nav + '\n<footer', 1)
    home.write_text(html, encoding="utf-8")
    return True


CHROME_SLUGS = {
    "cgv","mentions-legales","mentions-legales-loisirs74-phase1",
    "signaler","signaler-info","devenir-partenaire","confidentialite",
    "politique-confidentialite-loisirs74-phase1","merci-partenaire",
    "merci-signalement","studio","404","index",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated FR hub names")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    fiches = load_all_json()
    photo_index = _load_photo_index()
    hub_descriptions = _load_hub_meta_descriptions()
    assignments = []  # Phase 4: capture (hub, slug, type, photo, score, reason)
    # Hub names (FR + locales) of EVERY hub on disk, so we don't treat them as fiches
    all_hub_names = set()
    for fr_hub in HUB_FILTERS:
        all_hub_names.update(hub_locale_map(fr_hub).values())
    # Also include any other dirs with index.html (thematic hubs we don't rebuild)
    for d in ROOT.iterdir():
        if d.is_dir() and (d / "index.html").exists() and d.name not in {
            "_site","__pycache__","reports","scripts","Json","api","content",
            ".well-known","en","de","it","es","nl"
        }:
            all_hub_names.add(d.name)
    excludes = CHROME_SLUGS | all_hub_names

    regen = 0
    summary = []
    for fr_hub, filt in HUB_FILTERS.items():
        if only and fr_hub not in only: continue
        locale_names = hub_locale_map(fr_hub)
        # Build the union: existing curated slugs ∪ slugs matching the filter.
        existing = existing_hub_fiches(ROOT / fr_hub / "index.html", excludes)
        existing_in_json = {s for s in existing if s in fiches}
        matched_slugs = {s for s, d in fiches.items() if filt(d)}
        union_slugs = existing_in_json | matched_slugs
        added = sorted(matched_slugs - existing_in_json)
        union = [(s, fiches[s]) for s in sorted(union_slugs)]
        # Communes actually present in the rendered card set (source of
        # truth for filt-commune options). Used by patch_filt_commune to
        # eliminate ghost options structurally.
        communes_in_hub = {fiches[s].get("commune") for s in union_slugs if fiches[s].get("commune")}
        # Does the hub have any free fiche? Drives whether the Gratuit
        # access-toggle button is rendered hidden. Seasonal counts as
        # free-eligible (the JS filter treats seasonal as both).
        has_free = any(
            fiches[s].get("schema_org", {}).get("is_free") is True
            or fiches[s].get("schema_org", {}).get("tariff_kind") == "seasonal"
            for s in union_slugs
        )
        for lang in ("fr",) + LOCALES:
            hub_name = locale_names.get(lang)
            if not hub_name: continue
            dir_path = (ROOT if lang == "fr" else ROOT / lang) / hub_name
            if not dir_path.exists():
                print(f"  ! [{lang}] {hub_name}/ does not exist; skipping")
                continue
            p = dir_path / "index.html"
            html = p.read_text(encoding="utf-8")
            new_main = build_main_block(union, lang, hub_name=fr_hub,
                                        photo_index=photo_index,
                                        assignments=assignments)
            new_html = splice_main(html, new_main)
            # Filter chrome patches (apply to every hub, every locale).
            new_html = patch_filt_commune(new_html, communes_in_hub, lang)
            new_html = patch_filt_access_free_toggle(new_html, has_free)
            # Phase 5: per-hub filter JS reads card data-* attributes
            # only. Per-hub variant kept (lacs-plages has filt-lac, the
            # other 13 don't). Idempotent.
            new_html = patch_hub_filter_js(new_html, fr_hub, lang)
            # Hub head: title (≤60 chars), meta description (120-160 from
            # data/hub-meta-descriptions.json), OG block (7 tags). All
            # idempotent. Single source of truth for descriptions = the
            # JSON file under data/.
            new_html = patch_hub_head(new_html, fr_hub, lang, hub_name, hub_descriptions)
            # JOB §5a: single-source the <h1> from HUB_DISPLAY (== title/nav),
            # fixing de/nl/en drift across all 15 hubs.
            new_html = patch_hub_h1(new_html, fr_hub, lang)
            if new_html != html:
                p.write_text(new_html, encoding="utf-8")
                regen += 1
        summary.append((fr_hub, len(existing_in_json), len(union_slugs), len(added)))
    print(f"\n{'hub':<22} {'prev':<6} {'cur':<6} {'added':<6}")
    for h, prev, cur, added in summary:
        print(f"  {h:<22} {prev:<6} {cur:<6} +{added:<5}")
    print(f"\nregenerated: {regen}/{len(HUB_FILTERS)*6}")

    # Step 2: patch each locale homepage so every hub directory on disk is
    # linked. Closes the orphan gap that came from voies-vertes /
    # sorties-detente being absent from the locale-homepage nav.
    print("\npatching homepages: Sorties & détente section + hub-completeness:")
    for lang in ("fr",) + LOCALES:
        sortie = patch_homepage_sorties(lang)
        changed = patch_homepage_completeness(lang)
        nearme = patch_homepage_nearme(lang)
        bits = []
        if sortie: bits.append("+sorties")
        if changed: bits.append("+all-categories nav")
        if nearme: bits.append("+nearme.js")
        print(f"  [{lang}] {' '.join(bits) if bits else 'already complete'}")

    # Phase 4: emit the photo-assignment report so Eddie can spot-check
    # the picks. Sorted by (hub, slug) for deterministic output.
    if assignments:
        from collections import Counter
        per_hub_photo = defaultdict(Counter)
        for hub, slug, typ, photo, score, reason in assignments:
            per_hub_photo[hub][photo] += 1
        max_repeat = {hub: c.most_common(1)[0][1] for hub, c in per_hub_photo.items()}
        lines = [
            "# Phase 4 — photo assignments (gate artifact)",
            "",
            f"**Date**: 2026-06-14",
            f"**Total assignments**: {len(assignments)} (one per (hub × slug) on the FR canonical hub)",
            "",
            "## Per-hub diversity",
            "",
            "| hub | fiches | distinct photos | max repeat of one photo |",
            "|---|---:|---:|---:|",
        ]
        for hub in sorted(per_hub_photo):
            n_fiches = sum(per_hub_photo[hub].values())
            n_distinct = len(per_hub_photo[hub])
            lines.append(f"| `{hub}` | {n_fiches} | {n_distinct} | {max_repeat[hub]} |")
        lines += [
            "",
            "## Per-fiche assignments",
            "",
            "| hub | slug | type | photo | score | reason |",
            "|---|---|---|---|---:|---|",
        ]
        for row in sorted(assignments):
            hub, slug, typ, photo, score, reason = row
            score_s = str(score) if score is not None else "—"
            lines.append(f"| `{hub}` | `{slug}` | `{typ}` | `{photo}` | {score_s} | {reason} |")
        (ROOT / "reports" / "photo-assignments.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"\nwrote reports/photo-assignments.md  ({len(assignments)} rows)")


if __name__ == "__main__":
    main()
