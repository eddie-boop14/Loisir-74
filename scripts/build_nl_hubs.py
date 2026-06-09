#!/usr/bin/env python3
"""Build /nl/<hub>/index.html for each of the 13 hub categories.

Derives each NL hub from its EN equivalent: lift NL chrome from
/nl/plage-de-doussard.html, translate hub-shell strings (title, h1,
breadcrumbs, free/paid tags), rewrite venue URLs to /nl/<slug>, and
update lang/canonical/og-locale/hreflang to nl.

Also updates the lang-picker on all existing hub variants (FR + 4
other locales) to add a "Nederlands" link.

Usage:
    python3 scripts/build_nl_hubs.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://loisirs74.fr"

# Hub path map: source-EN-path → (NL-path, FR-path, label_FR)
HUBS = [
    ("en/lakes",         "nl/meren",            "lacs",               "Meren"),
    ("en/beaches",       "nl/stranden",         "plages",             "Stranden"),
    ("en/waterfalls",    "nl/watervallen",      "cascades",           "Watervallen"),
    ("en/trails",        "nl/wandelpaden",      "sentiers",           "Wandelpaden"),
    ("en/viewpoints",    "nl/uitzichtpunten",   "points-de-vue",      "Uitzichtpunten"),
    ("en/leisure-parks", "nl/recreatiegebieden","bases-de-loisirs",   "Recreatiegebieden"),
    ("en/attractions",   "nl/attracties",       "attractions",        "Attracties"),
    ("en/cable-cars",    "nl/kabelbanen",       "telecabines",        "Kabelbanen"),
    ("en/castles",       "nl/kastelen",         "chateaux",           "Kastelen"),
    ("en/museums",       "nl/musea",            "musees",             "Musea"),
    ("en/greenways",     "nl/groene-routes",    "voies-vertes",       "Groene routes"),
    ("en/other",         "nl/diversen",         "divers",             "Diversen"),
    ("en/que-faire",     "nl/wat-te-doen",      "que-faire",          "Wat te doen"),
]

# All hub locale-variants for which we must inject the NL link into their lang-picker.
# Built from disk scan once we know the map.
LANG_PATHS_PER_HUB = {
    "lacs":             {"fr":"lacs","en":"lakes","de":"seen","it":"laghi","es":"lagos","nl":"meren"},
    "plages":           {"fr":"plages","en":"beaches","de":"straende","it":"spiagge","es":"playas","nl":"stranden"},
    "cascades":         {"fr":"cascades","en":"waterfalls","de":"wasserfaelle","it":"cascate","es":"cascadas","nl":"watervallen"},
    "sentiers":         {"fr":"sentiers","en":"trails","de":"wanderwege","it":"sentieri","es":"senderos","nl":"wandelpaden"},
    "points-de-vue":    {"fr":"points-de-vue","en":"viewpoints","de":"aussichtspunkte","it":"punti-panoramici","es":"miradores","nl":"uitzichtpunten"},
    "bases-de-loisirs": {"fr":"bases-de-loisirs","en":"leisure-parks","de":"freizeitparks","it":"aree-recreative","es":"areas-de-ocio","nl":"recreatiegebieden"},
    "attractions":      {"fr":"attractions","en":"attractions","de":"attraktionen","it":"attrazioni","es":"atraciones","nl":"attracties"},
    "telecabines":      {"fr":"telecabines","en":"cable-cars","de":"seilbahnen","it":"funivie","es":"telefericos","nl":"kabelbanen"},
    "chateaux":         {"fr":"chateaux","en":"castles","de":"schloesser","it":"castelli","es":"castillos","nl":"kastelen"},
    "musees":           {"fr":"musees","en":"museums","de":"museen","it":"musei","es":"museos","nl":"musea"},
    "voies-vertes":     {"fr":"voies-vertes","en":"greenways","de":"radwege","it":"vie-verdi","es":"vias-verdes","nl":"groene-routes"},
    "divers":           {"fr":"divers","en":"other","de":"sonstiges","it":"altro","es":"otros","nl":"diversen"},
    "que-faire":        {"fr":"que-faire","en":"que-faire","de":"que-faire","it":"que-faire","es":"que-faire","nl":"wat-te-doen"},
}

# NL chrome string mappings (translated FROM EN source)
NL_CHROME = {
    "Lakes &amp; beaches": "Meren &amp; stranden",
    "Lakes & beaches": "Meren & stranden",
    "Beaches": "Stranden",
    "Waterfalls": "Watervallen",
    "Hiking trails": "Wandelpaden",
    "Trails": "Wandelpaden",
    "Viewpoints": "Uitzichtpunten",
    "Leisure parks": "Recreatiegebieden",
    "Attractions": "Attracties",
    "Cable cars": "Kabelbanen",
    "Castles": "Kastelen",
    "Museums": "Musea",
    "Greenways": "Groene routes",
    "Other": "Diversen",
    "Things to do": "Wat te doen",
    "What to do in Haute-Savoie": "Wat te doen in Haute-Savoie",
    "Free": "Gratis",
    "Paid": "Betaald",
    "Home": "Startpagina",
    "Skip to content": "Naar inhoud springen",
    "Choose language": "Kies taal",
    "Loisirs 74": "Loisirs 74",
}

NL_LANG_MENU_LINE = '<a href="https://loisirs74.fr/nl/__NLPATH__/" hreflang="nl">Nederlands</a>'


def lift_nl_chrome():
    src = (ROOT / "nl" / "plage-de-doussard.html").read_text(encoding="utf-8")
    header = re.search(r"<header class=\"site\">.*?</header>", src, re.DOTALL).group(0)
    footer = re.search(r"<footer class=\"site\">.*?</footer>", src, re.DOTALL).group(0)
    return header, footer


def build_hub(en_path, nl_path, fr_path, label):
    src_file = ROOT / en_path / "index.html"
    if not src_file.exists():
        print(f"  SKIP {en_path}: source missing")
        return
    t = src_file.read_text(encoding="utf-8")
    fr_slug = fr_path

    # 1. Global URL prefix: /en/ → /nl/
    t = t.replace("https://loisirs74.fr/en/", "https://loisirs74.fr/nl/")

    # 2. lang attr + og:locale
    t = re.sub(r'<html lang="en"', '<html lang="nl"', t, count=1)
    t = t.replace('og:locale" content="en_US"', 'og:locale" content="nl_NL"')

    # 3. Canonical and hreflang block: point to NL canonical, regen full alts
    paths = LANG_PATHS_PER_HUB[fr_slug]
    nl_url = f'{BASE}/nl/{paths["nl"]}/'
    # Canonical: handle attribute order variation (rel-first OR href-first)
    t = re.sub(
        r'<link[^>]*\brel="canonical"[^>]*/?>',
        f'<link href="{nl_url}" rel="canonical"/>',
        t, count=1
    )
    # Hreflang alternates: strip all and re-insert canonical block
    hreflang_lines = []
    # Use rel-first format so hub_map() discovery regex matches.
    hreflang_lines.append(f'<link rel="alternate" hreflang="fr" href="{BASE}/{paths["fr"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="en" href="{BASE}/en/{paths["en"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="de" href="{BASE}/de/{paths["de"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="it" href="{BASE}/it/{paths["it"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="es" href="{BASE}/es/{paths["es"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="nl" href="{BASE}/nl/{paths["nl"]}/">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/{paths["fr"]}/">')
    hreflang_block = "\n".join(hreflang_lines)
    # Remove any existing hreflang alternate links
    t = re.sub(r'<link[^>]+hreflang="[^"]+"[^>]*/?>\s*', "", t)
    # Re-insert hreflang block right after the canonical
    t = re.sub(
        r'(<link[^>]*\brel="canonical"[^>]*/?>)',
        r'\1\n' + hreflang_block,
        t, count=1
    )

    # 4. Swap chrome: header + footer
    nl_header, nl_footer = lift_nl_chrome()
    # localize lang-picker for THIS hub: insert links to all 5 other-lang hubs
    nl_header_local = nl_header
    # Replace __SLUG__ refs with this hub's nl-path-suffix; localize_lieu uses __SLUG__ in the bootstrap.
    # For hubs the lang-picker links point to <basepath>/<lang>/<lang-path>/ — we'll regenerate the lang-menu entirely.
    lang_menu = "\n".join([
        f'<a href="{BASE}/{paths["fr"]}/" hreflang="fr">Français</a>',
        f'<a href="{BASE}/en/{paths["en"]}/" hreflang="en">English</a>',
        f'<a href="{BASE}/de/{paths["de"]}/" hreflang="de">Deutsch</a>',
        f'<a href="{BASE}/it/{paths["it"]}/" hreflang="it">Italiano</a>',
        f'<a href="{BASE}/es/{paths["es"]}/" hreflang="es">Español</a>',
        f'<a href="{BASE}/nl/{paths["nl"]}/" aria-current="true" hreflang="nl">Nederlands</a>',
    ])
    nl_header_local = re.sub(
        r'<div class="lang-menu">.*?</div></details>',
        f'<div class="lang-menu">{lang_menu}</div></details>',
        nl_header_local, count=1, flags=re.DOTALL
    )
    # Replace the brand link target so it points to /nl/ root
    nl_header_local = nl_header_local.replace('__SLUG__', '')
    t = re.sub(r"<header class=\"site\">.*?</header>", lambda m: nl_header_local, t, count=1, flags=re.DOTALL)
    t = re.sub(r"<footer class=\"site\">.*?</footer>", lambda m: nl_footer, t, count=1, flags=re.DOTALL)

    # 5. Translate hub-shell phrases (chrome inside body)
    for en_str, nl_str in NL_CHROME.items():
        t = t.replace(en_str, nl_str)
    # Free/Paid tags
    t = t.replace('class="card-tag is-gratuit">Free', 'class="card-tag is-gratuit">Gratis')
    t = t.replace('class="card-tag is-payant">Paid', 'class="card-tag is-payant">Betaald')

    # 6. Write
    out_dir = ROOT / nl_path
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(t, encoding="utf-8")
    print(f"  /{nl_path}/index.html  ({len(t):,} chars)")


def patch_existing_hubs_lang_menus():
    """Add Dutch link to lang-picker on the 5 existing hub variants (FR + 4 locales) per category.
    Also updates the "5 languages/langues/Sprachen/lingue/idiomas" count to "6"."""
    SUMMARY_NUM = [
        (r'(<b>\w+</b> · )5( languages)', r'\g<1>6\g<2>'),
        (r'(<b>\w+</b> · )5( langues)', r'\g<1>6\g<2>'),
        (r'(<b>\w+</b> · )5( Sprachen)', r'\g<1>6\g<2>'),
        (r'(<b>\w+</b> · )5( lingue)', r'\g<1>6\g<2>'),
        (r'(<b>\w+</b> · )5( idiomas)', r'\g<1>6\g<2>'),
    ]
    patched = 0
    for fr_slug, paths in LANG_PATHS_PER_HUB.items():
        nl_path = paths["nl"]
        nl_link = NL_LANG_MENU_LINE.replace("__NLPATH__", nl_path)
        for lang, hub_path in paths.items():
            if lang == "nl": continue
            f = ROOT / (hub_path if lang == "fr" else f"{lang}/{hub_path}") / "index.html"
            if not f.exists(): continue
            html = f.read_text(encoding="utf-8")
            if f'/nl/{nl_path}/' in html:
                continue  # already has NL link
            # Inject NL link before </div></details> closing the lang-menu
            new = re.sub(
                r'(<div class="lang-menu">.*?)(\s*</div>\s*</details>)',
                lambda m: m.group(1) + nl_link + m.group(2),
                html, count=1, flags=re.DOTALL
            )
            # Update summary count "5 → 6"
            for pat, repl in SUMMARY_NUM:
                new = re.sub(pat, repl, new, count=1)
            if new != html:
                f.write_text(new, encoding="utf-8")
                patched += 1
    print(f"  language-picker patched on {patched} existing hub files")


def main():
    print("=== Building NL hubs ===")
    for en_path, nl_path, fr_path, label in HUBS:
        build_hub(en_path, nl_path, fr_path, label)
    print()
    print("=== Patching existing hub lang-menus ===")
    patch_existing_hubs_lang_menus()


if __name__ == "__main__":
    main()
