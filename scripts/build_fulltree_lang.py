#!/usr/bin/env python3
"""build_fulltree_lang.py — promote a render-verified language to a PUBLISHED
full tree (HANDOFF-16 Phase 2 / HANDOFF-10 Job 3).

A new language has only the 86-key label vocabulary translated, never the fiche
prose — so its full tree is FACTS-FIRST end to end: every fiche, the 15 category
hubs under localized slugs, the commune pages, and the homepage, all built from
language-independent facts + the vocabulary, wrapped in real published chrome
(self-canonical, the 7-language hreflang cluster, the endonym picker, breadcrumb).
No FR prose can leak because no prose is ever shown.

Run: python3 scripts/build_fulltree_lang.py pl
"""
import glob
import html as _h
import json
import os
import re
import unicodedata
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locales  # noqa: E402
import assets  # noqa: E402
import build_hubs as H  # noqa: E402  (hub_locale_map, HUB_FILTERS)
import build_pilot_langs as P  # noqa: E402  (V, esc, fact_rows, CATEGORY_DESCRIPTOR)

BASE = "https://loisirs74.fr"
PROTECTED = {"chez-nous-a-la-plage", "chalet-du-tornet"}
COMMUNE_MIN = 4  # a commune gets its own page at >= this many fiches

# Localized hub slugs for new languages (ASCII-folded, URL-clean). The 6 live
# slugs are derived from their rendered trees via build_hubs.hub_locale_map.
HUB_SLUGS = {
    "pl": {
        "cascades": "wodospady", "chateaux": "zamki", "lacs-plages": "jeziora-plaze",
        "musees": "muzea", "parcs-jardins": "parki-ogrody", "points-de-vue": "punkty-widokowe",
        "sentiers": "szlaki", "telecabines": "koleje-gondolowe", "voies-vertes": "zielone-szlaki",
        "baignade-nautisme": "kapiel-sporty-wodne", "bases-de-loisirs": "parki-rekreacyjne",
        "que-faire": "co-robic", "sensations-plein-air": "emocje-plenerowe",
        "sorties-detente": "relaksujace-wycieczki", "sport-jeux": "sport-zabawa",
    },
}

esc = P.esc
V = P.V

# Commune pages exactly mirror the 6's published set (so cross-language hreflang +
# the picker resolve), derived from the live commune directories at the FR root.
_HUB_DIR_NAMES = set(H.HUB_FILTERS)
_SYS_DIRS = {"api", "content", "scripts", "Json", "reports", "_site", "node_modules",
             ".git", ".well-known", "data", "studio"}
PUB_COMMUNES = set()  # populated in main()


def load_fiches():
    out = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "Json", "*.json"))):
        d = json.loads(open(fp, encoding="utf-8").read())
        slug = d.get("slug") or os.path.basename(fp)[:-5]
        if slug in PROTECTED or d.get("status") not in (None, "published"):
            continue
        d["slug"] = slug
        out.append(d)
    return out


def slug_map(hub):
    """{lang: localized hub slug} for the 6 (derived) + every new lang in HUB_SLUGS."""
    m = dict(H.hub_locale_map(hub))  # fr + en/de/it/es/nl
    for lang, slugs in HUB_SLUGS.items():
        if hub in slugs:
            m[lang] = slugs[hub]
    return m


def url_for(lang, path):
    """Absolute URL for a path in a published locale (fr at root). `path` carries
    its own trailing slash convention — fiches are file URLs (no slash), hubs/
    communes/homepage are directory URLs (trailing slash), matching the live 6 so
    fix_hreflang_sitemap's hub_map (which requires fr-href to end in '/') folds the
    facts tree into the clusters + sitemap."""
    prefix = BASE + ("/" if lang == "fr" else f"/{lang}/")
    return f"{prefix}{path}" if path else (f"{BASE}/" if lang == "fr" else f"{BASE}/{lang}/")


def hreflang_block(equiv):
    """equiv: {lang: path-without-lang-prefix}. Emit the cluster + x-default(fr)."""
    order = list(locales.VISIBLE)
    lines = []
    for lg in order:
        lines.append(f'<link rel="alternate" hreflang="{lg}" href="{url_for(lg, equiv[lg])}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{url_for("fr", equiv["fr"])}">')
    return "\n".join(lines)


def picker(lang, equiv, labels):
    """The endonym language picker — links to this page's equivalent per language."""
    items = []
    for lg in locales.VISIBLE:
        endo = locales.ENDONYM[lg]
        cur = ' aria-current="true"' if lg == lang else ""
        items.append(f'<a href="{url_for(lg, equiv[lg])}" hreflang="{lg}"{cur}>{esc(endo)}</a>')
    return ('<nav class="lang"><details><summary>'
            f'{esc(labels.get("toutes_categories",""))[:0]}🌐 {esc(locales.ENDONYM[lang])}</summary>'
            '<div class="lang-menu">' + "".join(items) + "</div></details></nav>")


CSS = (P.CSS +
       "header.site{display:flex;align-items:center;justify-content:space-between;gap:12px;"
       "max-width:1040px;margin:0 auto;padding:12px 18px}header.site a.brand{font-weight:800;color:#1F6E78;"
       "text-decoration:none;font-size:18px}nav.lang summary{cursor:pointer;list-style:none;font-weight:600;"
       "font-size:14px;color:#1F6E78}nav.lang details{position:relative}nav.lang .lang-menu{position:absolute;"
       "inset-inline-end:0;background:#fff;border:1px solid #e3ddd0;border-radius:10px;padding:6px;display:flex;"
       "flex-direction:column;min-width:140px;box-shadow:0 6px 24px rgba(0,0,0,.08);z-index:9}"
       "nav.lang .lang-menu a{padding:6px 10px;border-radius:7px;color:#22302f;text-decoration:none;font-size:14px}"
       "nav.lang .lang-menu a[aria-current]{background:#eef6f4;color:#1F6E78;font-weight:700}"
       "nav.crumb{max-width:1040px;margin:0 auto;padding:0 18px 4px;font-size:13px;color:#5b6b6a}"
       "nav.crumb a{color:#1F6E78;text-decoration:none}"
       ".grid{max-width:1040px;margin:0 auto;padding:8px 18px 28px;display:grid;gap:14px;"
       "grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}"
       ".card{background:#fff;border:1px solid #e3ddd0;border-radius:12px;padding:14px 16px;text-decoration:none;color:inherit;display:block}"
       ".card h3{font-size:16px;margin:0 0 2px;color:#22302f}.card .c-desc{color:#1F6E78;font-weight:600;font-size:13px}"
       ".card .c-meta{color:#5b6b6a;font-size:13px;margin-top:6px}"
       ".hubs{max-width:1040px;margin:0 auto;padding:8px 18px 28px;display:grid;gap:10px;"
       "grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}.hubs a{background:#fff;border:1px solid #e3ddd0;"
       "border-radius:10px;padding:12px 14px;text-decoration:none;color:#1F6E78;font-weight:700}"
       "h2.sec{max-width:1040px;margin:18px auto 2px;padding:0 18px;font-size:21px}")


def shell(lang, title, meta_desc, canonical, hreflang, body, schema):
    duck = assets.script_tag("duck.js")
    labels_pick = picker(lang, _SHELL_EQUIV[0], _LABELS)
    brand = esc(V("ui_chrome", "accueil", lang)) or "loisirs74"
    return f"""<!doctype html><html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical}">
{hreflang}
<meta name="description" content="{esc(meta_desc)}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>{CSS}</style></head><body>
<header class="site"><a class="brand" href="{url_for(lang, '')}">loisirs74</a>{labels_pick}</header>
{body}
<footer><div class="wrap">© 2026 · Bleu canard édition · Edmaster &amp; Claudius 🦆</div></footer>
{duck}
</body></html>"""


# picker() needs the current page's equivalents; we stash them per-render.
_SHELL_EQUIV = [None]
_LABELS = {}


def with_equiv(equiv):
    _SHELL_EQUIV[0] = equiv


def card(d, lang):
    name = d.get("i18n", {}).get("fr", {}).get("name") or d["slug"]
    desc_key = P.CATEGORY_DESCRIPTOR.get(d.get("category"))
    descriptor = V("descriptors_by_type", desc_key, lang) if desc_key else ""
    commune = d.get("commune", "")
    meta = " · ".join(x for x in (descriptor, commune) if x)
    return (f'<a class="card" href="{url_for(lang, d["slug"])}">'
            f'<h3>{esc(name)}</h3>'
            f'{f"<div class=c-desc>{esc(descriptor)}</div>" if descriptor else ""}'
            f'<div class="c-meta">{esc(commune)}</div></a>')


def render_fiche(d, lang):
    name = d.get("i18n", {}).get("fr", {}).get("name") or d["slug"]
    commune = d.get("commune", "")
    desc_key = P.CATEGORY_DESCRIPTOR.get(d.get("category"))
    descriptor = V("descriptors_by_type", desc_key, lang) if desc_key else ""
    rows = P.fact_rows(d, lang)
    facts_html = "".join(f"<dt>{esc(lbl)}</dt><dd>{val}</dd>" for lbl, val in rows if lbl)
    site = d.get("official_site_url")
    site_html = (f'<a class="site" href="{esc(site)}" rel="nofollow noopener" target="_blank">'
                 f'{esc(V("ui_chrome", "site_officiel", lang))} ↗</a>') if site else ""
    equiv = {lg: d["slug"] for lg in locales.VISIBLE}
    with_equiv(equiv)
    cslug = commune_slug(commune) if commune else ""
    crumb_commune = (f'<a href="{url_for(lang, cslug + "/")}">{esc(commune)}</a> / '
                     if cslug in PUB_COMMUNES else (f"{esc(commune)} / " if commune else ""))
    crumb = (f'<nav class="crumb"><a href="{url_for(lang, "")}">'
             f'{esc(V("ui_chrome", "accueil", lang))}</a> / {crumb_commune}{esc(name)}</nav>')
    body = (crumb + '<div class="wrap">'
            f'<h1>{esc(name)}</h1>'
            f'{f"<p class=desc>{esc(descriptor)}</p>" if descriptor else ""}'
            f'<dl class="facts">{facts_html}</dl>{site_html}</div>')
    schema = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": name,
              "inLanguage": lang, "address": {"@type": "PostalAddress", "addressLocality": commune,
              "addressRegion": "Haute-Savoie", "addressCountry": "FR"}}
    if d.get("latitude") and d.get("longitude"):
        schema["geo"] = {"@type": "GeoCoordinates", "latitude": d["latitude"], "longitude": d["longitude"]}
    title = f"{name} · {commune} — loisirs74"
    meta = (descriptor + (", " if descriptor else "") + commune + " (Haute-Savoie).").strip()
    return shell(lang, title, meta, url_for(lang, d["slug"]),
                 hreflang_block(equiv), body, schema)


def render_hub(hub, members, lang):
    sm = slug_map(hub)
    equiv = {lg: sm.get(lg, hub) + "/" for lg in locales.VISIBLE}
    with_equiv(equiv)
    label = V("hub_names", hub, lang) or hub
    crumb = (f'<nav class="crumb"><a href="{url_for(lang, "")}">'
             f'{esc(V("ui_chrome", "accueil", lang))}</a> / {esc(label)}</nav>')
    cards = "".join(card(m, lang) for m in members)
    body = crumb + f'<h2 class="sec">{esc(label)}</h2><div class="grid">{cards}</div>'
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": label,
              "inLanguage": lang, "numberOfItems": len(members)}
    return shell(lang, f"{label} — Haute-Savoie · loisirs74",
                 f"{label} · Haute-Savoie ({len(members)}).",
                 url_for(lang, equiv[lang]), hreflang_block(equiv), body, schema)


def commune_slug(commune):
    s = _h.unescape(commune or "").replace("œ", "oe").replace("Œ", "OE")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def render_commune(commune, members, lang):
    cslug = commune_slug(commune)
    equiv = {lg: cslug + "/" for lg in locales.VISIBLE}
    with_equiv(equiv)
    whattodo = V("ui_chrome", "accueil", lang)  # fallback; communes use a generic header
    title_h1 = f"{esc(commune)}"
    crumb = (f'<nav class="crumb"><a href="{url_for(lang, "")}">'
             f'{esc(V("ui_chrome", "accueil", lang))}</a> / {esc(commune)}</nav>')
    cards = "".join(card(m, lang) for m in members)
    body = crumb + f'<h2 class="sec">{title_h1}</h2><div class="grid">{cards}</div>'
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": commune,
              "inLanguage": lang, "numberOfItems": len(members)}
    return shell(lang, f"{commune} — Haute-Savoie · loisirs74",
                 f"{commune} · Haute-Savoie ({len(members)}).",
                 url_for(lang, cslug + "/"), hreflang_block(equiv), body, schema)


def render_home(hubs_present, lang):
    equiv = {lg: "" for lg in locales.VISIBLE}
    with_equiv(equiv)
    hub_links = "".join(
        f'<a href="{url_for(lang, slug_map(hub).get(lang, hub) + "/")}">{esc(V("hub_names", hub, lang) or hub)}</a>'
        for hub in hubs_present)
    body = (f'<h2 class="sec">{esc(V("ui_chrome", "toutes_categories", lang))}</h2>'
            f'<div class="hubs">{hub_links}</div>')
    schema = {"@context": "https://schema.org", "@type": "WebSite", "name": "loisirs74",
              "inLanguage": lang, "url": url_for(lang, "")}
    return shell(lang, f"loisirs74 — Haute-Savoie ({locales.ENDONYM[lang]})",
                 f"Haute-Savoie · {locales.ENDONYM[lang]}.",
                 url_for(lang, ""), hreflang_block(equiv), body, schema)


_FICHE_HREF = re.compile(r'href="https://loisirs74\.fr/([a-z0-9-]+)"')


def curated_members(hub, by_slug):
    """Curated cross-cut hubs (que-faire, sensations-plein-air) carry no category
    filter — their members are the fiche slugs linked from the canonical FR hub."""
    p = os.path.join(ROOT, hub, "index.html")
    if not os.path.exists(p):
        return []
    html = open(p, encoding="utf-8").read()
    seen, out = set(), []
    for s in _FICHE_HREF.findall(html):
        if s in by_slug and s not in seen:
            seen.add(s)
            out.append(by_slug[s])
    return out


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)


def published_communes():
    """The commune slug set the 6 already publish (live dirs at the FR root)."""
    out = set()
    for name in os.listdir(ROOT):
        p = os.path.join(ROOT, name)
        if (os.path.isdir(p) and name not in _HUB_DIR_NAMES and name not in _SYS_DIRS
                and name not in locales.LANGUAGES and os.path.exists(os.path.join(p, "index.html"))):
            out.add(name)
    return out


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "pl"
    assert locales.status(lang) == "published", \
        f"{lang} must be status:published in data/languages.json before full-tree render"
    global PUB_COMMUNES
    PUB_COMMUNES = published_communes()
    fiches = load_fiches()
    out = os.path.join(ROOT, lang)
    n_f = n_h = n_c = 0

    # fiches
    for d in fiches:
        write(os.path.join(out, d["slug"] + ".html"), render_fiche(d, lang))
        n_f += 1

    # hubs (15) under localized slugs
    by_slug = {d["slug"]: d for d in fiches}
    hubs_present = []
    for hub, filt in H.HUB_FILTERS.items():
        members = [d for d in fiches if filt(d)]
        if not members:                      # curated cross-cut → FR hub's members
            members = curated_members(hub, by_slug)
        if not members:
            continue
        members.sort(key=lambda d: (d.get("commune", ""), d["slug"]))
        sm = slug_map(hub)
        write(os.path.join(out, sm.get(lang, hub), "index.html"), render_hub(hub, members, lang))
        hubs_present.append(hub)
        n_h += 1

    # communes — exactly the 6's published set, so cross-hreflang resolves
    by_slug_commune = {}
    for d in fiches:
        c = d.get("commune")
        if c:
            by_slug_commune.setdefault(commune_slug(c), (c, []))[1].append(d)
    missing = []
    for cslug in sorted(PUB_COMMUNES):
        entry = by_slug_commune.get(cslug)
        if not entry:
            missing.append(cslug); continue
        commune, members = entry
        members.sort(key=lambda d: d["slug"])
        write(os.path.join(out, cslug, "index.html"), render_commune(commune, members, lang))
        n_c += 1
    if missing:
        print(f"  [warn] {len(missing)} published commune(s) had no fiche match: {missing}")

    # homepage
    write(os.path.join(out, "index.html"), render_home(hubs_present, lang))

    print(f"build_fulltree_lang[{lang}]: {n_f} fiches + {n_h} hubs + {n_c} communes + 1 homepage")


if __name__ == "__main__":
    main()
