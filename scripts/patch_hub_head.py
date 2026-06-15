#!/usr/bin/env python3
"""patch_hub_head.py — Task 3b + 3c.

3b. Replace the <title> of every hub index with a ≤60-char template
    per hub × per locale. Keeps category + "Haute-Savoie" + brand.
3c. Insert the full Open Graph tag set on every hub: og:title,
    og:description, og:url, og:type, og:locale, og:site_name, og:image.
    (Currently only og:image was present — 1 OG / hub; one hub had 0.)

Source of truth = the hand-tuned templates below. Idempotent: on rerun,
title is replaced and OG block is upserted by detecting og:title.

Frozen place names per the standing rules: Haute-Savoie, Lac d'Annecy,
Léman, Mont-Blanc kept verbatim across languages.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HUB_LOCALE_SLUGS = {
    "cascades":            {"fr":"cascades","en":"waterfalls","de":"wasserfaelle","it":"cascate","es":"cascadas","nl":"watervallen"},
    "chateaux":            {"fr":"chateaux","en":"castles","de":"schloesser","it":"castelli","es":"castillos","nl":"kastelen"},
    "musees":              {"fr":"musees","en":"museums","de":"museen","it":"musei","es":"museos","nl":"musea"},
    "points-de-vue":       {"fr":"points-de-vue","en":"viewpoints","de":"aussichtspunkte","it":"punti-panoramici","es":"miradores","nl":"uitzichtpunten"},
    "sentiers":            {"fr":"sentiers","en":"trails","de":"wanderwege","it":"sentieri","es":"senderos","nl":"wandelpaden"},
    "telecabines":         {"fr":"telecabines","en":"cable-cars","de":"seilbahnen","it":"funivie","es":"telefericos","nl":"kabelbanen"},
    "voies-vertes":        {"fr":"voies-vertes","en":"greenways","de":"radwege","it":"vie-verdi","es":"vias-verdes","nl":"fietsroutes"},
    "lacs-plages":         {"fr":"lacs-plages","en":"lakes","de":"seen","it":"laghi","es":"lagos","nl":"meren"},
    "bases-de-loisirs":    {"fr":"bases-de-loisirs","en":"leisure-parks","de":"freizeitparks","it":"aree-ricreative","es":"areas-de-ocio","nl":"recreatieparken"},
    "baignade-nautisme":   {"fr":"baignade-nautisme","en":"swimming-watersports","de":"baden-wassersport","it":"nuoto-sport-acquatici","es":"bano-deportes-acuaticos","nl":"zwemmen-watersport"},
    "parcs-jardins":       {"fr":"parcs-jardins","en":"parks-gardens","de":"parks-gaerten","it":"parchi-giardini","es":"parques-jardines","nl":"parken-tuinen"},
    "que-faire":           {"fr":"que-faire","en":"what-to-do","de":"was-unternehmen","it":"cosa-fare","es":"que-hacer","nl":"wat-te-doen"},
    "sensations-plein-air":{"fr":"sensations-plein-air","en":"outdoor-thrills","de":"outdoor-nervenkitzel","it":"brividi-aria-aperta","es":"sensaciones-aire-libre","nl":"buitenavontuur"},
    "sorties-detente":     {"fr":"sorties-detente","en":"outings-relax","de":"ausfluege-erholung","it":"uscite-relax","es":"salidas-relax","nl":"uitstapjes-ontspanning"},
    "sport-jeux":          {"fr":"sport-jeux","en":"sport-games","de":"sport-spiele","it":"sport-giochi","es":"deporte-juegos","nl":"sport-spelen"},
}

# Title templates per hub × locale, ≤60 chars after substitution.
# Pattern: "{Category} en Haute-Savoie · Loisirs 74" in FR variants and
# locale-natural prepositions in other langs.
TITLE = {
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

import html as html_lib


def hub_url(canon, lang, slug):
    if lang == "fr":
        return f"https://loisirs74.fr/{slug}/"
    return f"https://loisirs74.fr/{lang}/{slug}/"


def og_block(canon, lang, slug, title, description):
    """Render the OG meta block. og:image already present on every hub —
    we DO NOT touch it. We insert title/description/url/type/locale/site_name.
    """
    url = hub_url(canon, lang, slug)
    a = lambda s: html_lib.escape(s or "", quote=True)
    return (
        f'<meta property="og:type" content="website"/>\n'
        f'<meta property="og:site_name" content="Loisirs 74"/>\n'
        f'<meta property="og:locale" content="{OG_LOCALE_TAG[lang]}"/>\n'
        f'<meta property="og:url" content="{url}"/>\n'
        f'<meta property="og:title" content="{a(title)}"/>\n'
        f'<meta property="og:description" content="{a(description)}"/>'
    )


def patch_title(html, new_title):
    """Replace <title>…</title> with new_title. Idempotent."""
    return re.sub(
        r'<title>[^<]*</title>',
        f'<title>{html_lib.escape(new_title, quote=False)}</title>',
        html, count=1,
    )


def patch_og(html, og_html):
    """Insert OG block right before the existing <meta property="og:image">
    if it's not already present. Idempotent — detects og:title to skip.
    """
    if 'property="og:title"' in html:
        # Replace prior block: detect by og:title-or-following og:description
        # to keep the block tidy. Conservative approach: find any of our 6
        # tags + 5 lines around and replace as a group.
        pat = re.compile(
            r'(?:<meta property="og:(?:type|site_name|locale|url|title|description)"[^>]*/>\s*){1,6}',
            re.IGNORECASE,
        )
        return pat.sub(lambda _: og_html + '\n', html, count=1)
    # Insert before <meta property="og:image"> when present (every other
    # hub has it), otherwise fall back to inserting right before </head>.
    if 'property="og:image"' in html:
        return re.sub(
            r'(<meta[^>]*property="og:image"[^>]*/>)',
            og_html + r'\n\1',
            html, count=1,
        )
    return html.replace(
        '</head>',
        og_html + '\n<meta property="og:image" content="https://loisirs74.fr/og-image.jpg"/>\n</head>',
        1,
    )


def main():
    LANGS = ["fr","en","de","it","es","nl"]
    title_changed = 0
    og_changed = 0
    long_after = []
    for canon, mp in HUB_LOCALE_SLUGS.items():
        for lang in LANGS:
            slug = mp[lang]
            p = (ROOT if lang == "fr" else ROOT / lang) / slug / "index.html"
            if not p.exists():
                print(f"  ! missing: {p}")
                continue
            html = p.read_text(encoding="utf-8")

            new_title = TITLE[canon][lang]
            if len(new_title) > 60:
                long_after.append((canon, lang, len(new_title), new_title))

            # Pull current description to reuse in og:description
            m = re.search(r'<meta[^>]*content="([^"]+)"[^>]*name="description"', html)
            if not m:
                m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html)
            desc = m.group(1) if m else ""

            new_html = patch_title(html, new_title)
            new_og = og_block(canon, lang, slug, new_title, desc)
            new_html = patch_og(new_html, new_og)

            if new_html != html:
                p.write_text(new_html, encoding="utf-8")
                title_changed += 1
                og_changed += 1
    print(f"\ntitles patched: {title_changed}/90")
    print(f"OG block patched: {og_changed}/90")
    if long_after:
        print(f"\n  ! still >60 chars: {len(long_after)}")
        for c, l, n, t in long_after:
            print(f"    [{l}] {c}: {n}  {t}")


if __name__ == "__main__":
    main()
