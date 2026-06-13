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
LOCALES = ("en", "de", "it", "es", "nl")

# Filter rules per hub. Basic + thematic hubs that can be derived from
# category/subcategories deterministically.
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
    "sorties-detente":  lambda d: d.get("category") in ("cinema", "casino"),
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


def fiche_card_html(d, lang, slug):
    """Render one card. URL = https://loisirs74.fr[/lang]/slug; title + desc from i18n."""
    i18n = d.get("i18n", {}) or {}
    loc = i18n.get(lang) or {}
    fr = i18n.get("fr") or {}
    name = loc.get("name") or fr.get("name") or slug
    desc = loc.get("meta_description") or fr.get("meta_description") or ""
    desc = desc.strip()[:280]  # cap
    is_free = bool(d.get("schema_org", {}).get("is_free", False))
    tag_class = "is-gratuit" if is_free else "is-payant"
    tag_text = CHROME["free" if is_free else "paid"][lang]
    commune = d.get("commune", "")

    # Hero image: generique-* under root, others under /<file>
    hero = d.get("hero_image") or ""
    if hero.startswith(("http://", "https://", "//")):
        img_src = hero
    elif hero.startswith("/"):
        img_src = f"https://loisirs74.fr{hero}"
    elif hero:
        img_src = f"https://loisirs74.fr/{hero}"
    else:
        cat = d.get("category") or "attraction"
        img_src = f"https://loisirs74.fr/generique-{cat}.jpg"

    alt = (loc.get("hero_alt") or fr.get("hero_alt") or name)
    lang_prefix = f"/{lang}" if lang != "fr" else ""
    fiche_url = f"https://loisirs74.fr{lang_prefix}/{slug}"
    official = d.get("official_site_url") or ""
    lat = d.get("latitude"); lon = d.get("longitude")
    if lat is not None and lon is not None:
        maps_url = f"https://www.google.com/maps/search/?api=1&amp;query={lat},{lon}"
    else:
        from urllib.parse import quote
        maps_url = f"https://www.google.com/maps/search/?api=1&amp;query={quote(name + ', ' + commune + ', Haute-Savoie')}"

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

    return (
        '<article class="card">\n'
        f'<a class="card-photo" href="{fiche_url}">\n'
        f'<img alt="{a(alt)}" loading="lazy" referrerpolicy="no-referrer" src="{a(img_src)}"/>\n'
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


def build_main_block(fiches, lang):
    """Render the <main>…</main> content for a hub: commune-grouped cards."""
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
        parts.append(f'<div class="commune-section" data-commune="{commune}">')
        parts.append(f'<div class="commune-head"><h3>{commune}</h3>'
                     f'<span class="commune-count">{n} {word}</span></div>')
        parts.append('<div class="carousel">')
        for slug, d in entries:
            parts.append(fiche_card_html(d, lang, slug))
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


def load_all_json():
    """Load every Json/<slug>.json. JOB 6: skip draft fiches so they don't
    appear in any hub."""
    out = {}
    for p in sorted((ROOT / "Json").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("status") == "draft":
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
}
ALL_BASE_HUBS = list(HUB_DISPLAY.keys())


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
        for lang in ("fr",) + LOCALES:
            hub_name = locale_names.get(lang)
            if not hub_name: continue
            dir_path = (ROOT if lang == "fr" else ROOT / lang) / hub_name
            if not dir_path.exists():
                print(f"  ! [{lang}] {hub_name}/ does not exist; skipping")
                continue
            p = dir_path / "index.html"
            html = p.read_text(encoding="utf-8")
            new_main = build_main_block(union, lang)
            new_html = splice_main(html, new_main)
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
    print("\npatching locale homepages for hub-completeness:")
    for lang in ("fr",) + LOCALES:
        changed = patch_homepage_completeness(lang)
        print(f"  [{lang}] {'+all-categories nav' if changed else 'already complete'}")


if __name__ == "__main__":
    main()
