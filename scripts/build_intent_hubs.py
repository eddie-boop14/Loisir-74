#!/usr/bin/env python3
"""build_intent_hubs.py — registry-driven intent-hub pages (answer-first SEO).

Reads the curated registry data/intent-hubs.json. For each hub it selects the
member lieux listed there, pulls their DISPLAYED facts LIVE from each fiche's
i18n.<lang>.facts (never re-derived, never price_from), and renders an
answer-first page + Leaflet map + ItemList/FAQPage schema, FR + 5 locales.

Editorial that can't be re-derived (cost bucket, rive, tag, highlight, answer,
FAQ) lives in the registry — the single curation surface. Displayed values come
from the fiche. null facts render "voir fiche", never a value.

Each hub is linked from its category hub (so reachability stays 0-orphan); flat
<slug>.html (FR) + <lang>/<slug>.html. Canonicals/hreflang/sitemap are added by
fix_hreflang_sitemap.py downstream. No timestamps/random → byte-stable.
"""
import html as _html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from build_hubs import hub_locale_map, HUB_DISPLAY  # noqa: E402
import locales  # noqa: E402

REGISTRY = os.path.join(ROOT, "data", "intent-hubs.json")
JSON_DIR = os.path.join(ROOT, "Json")
BASE = "https://loisirs74.fr"
LANGS = locales.PUBLISHED

FACT_LABELS = {
    "access":      {"fr": "Accès", "en": "Access", "de": "Zugang", "it": "Accesso", "es": "Acceso", "nl": "Toegang"},
    "tarif":       {"fr": "Tarif", "en": "Price", "de": "Preis", "it": "Tariffa", "es": "Tarifa", "nl": "Tarief"},
    "best_season": {"fr": "Saison", "en": "Season", "de": "Saison", "it": "Stagione", "es": "Temporada", "nl": "Seizoen"},
    "duration":    {"fr": "Durée d'accès", "en": "Access time", "de": "Zugangsdauer", "it": "Durata d'accesso", "es": "Duración de acceso", "nl": "Toegangstijd"},
    "commune":     {"fr": "Commune", "en": "Town", "de": "Gemeinde", "it": "Comune", "es": "Municipio", "nl": "Gemeente"},
    "stroller":    {"fr": "Poussette", "en": "Stroller", "de": "Kinderwagen", "it": "Passeggino", "es": "Carrito", "nl": "Kinderwagen"},
}
UI = {
    "see_fiche":  {"fr": "Voir la fiche →", "en": "See details →", "de": "Zum Steckbrief →", "it": "Vedi la scheda →", "es": "Ver la ficha →", "nl": "Bekijk fiche →"},
    "voir_fiche": {"fr": "voir fiche", "en": "see details", "de": "siehe Steckbrief", "it": "vedi scheda", "es": "ver ficha", "nl": "zie fiche"},
    "faq":        {"fr": "Questions fréquentes", "en": "Frequently asked questions", "de": "Häufige Fragen", "it": "Domande frequenti", "es": "Preguntas frecuentes", "nl": "Veelgestelde vragen"},
    "verified":   {"fr": "📍 vérifiée", "en": "📍 verified", "de": "📍 geprüft", "it": "📍 verificata", "es": "📍 verificada", "nl": "📍 geverifieerd"},
    "also":       {"fr": "À lire aussi", "en": "See also", "de": "Siehe auch", "it": "Da leggere anche", "es": "Ver también", "nl": "Zie ook"},
    "guides":     {"fr": "Les guides par lac", "en": "Guides by lake", "de": "Guides nach See", "it": "Guide per lago", "es": "Guías por lago", "nl": "Gidsen per meer"},
    "see_guide":  {"fr": "Voir le guide →", "en": "See the guide →", "de": "Zum Guide →", "it": "Vedi la guida →", "es": "Ver la guía →", "nl": "Bekijk de gids →"},
}

# Populated by main() so render_hub can resolve linked_hubs by slug.
_ALL_HUBS = {}
RIVE = {
    "Nord": {"fr": "Nord", "en": "North", "de": "Nord", "it": "Nord", "es": "Norte", "nl": "Noord"},
    "Sud": {"fr": "Sud", "en": "South", "de": "Süd", "it": "Sud", "es": "Sur", "nl": "Zuid"},
    "Est": {"fr": "Est", "en": "East", "de": "Ost", "it": "Est", "es": "Este", "nl": "Oost"},
    "Ouest": {"fr": "Ouest", "en": "West", "de": "West", "it": "Ovest", "es": "Oeste", "nl": "West"},
}
TAGS_BUILTIN = {
    "seasonal": {"fr": "Saisonnier", "en": "Seasonal", "de": "Saisonal", "it": "Stagionale", "es": "De temporada", "nl": "Seizoensgebonden"},
    "quick":    {"fr": "Arrêt court", "en": "Quick stop", "de": "Kurzer Halt", "it": "Sosta breve", "es": "Parada corta", "nl": "Korte stop"},
    "rando":    {"fr": "Randonnée", "en": "Hike", "de": "Wanderung", "it": "Escursione", "es": "Senderismo", "nl": "Wandeling"},
}

CSS = """:root{--cream:#FAF7F0;--teal:#1F6E78;--teal2:#155059;--ink:#22302f;--ink2:#5b6b6a;--line:#e3ddd0}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--cream);line-height:1.55}
.wrap{max-width:760px;margin:0 auto;padding:18px}
.kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);font-weight:700}
h1{font-size:26px;line-height:1.2;margin:.3em 0}
.lead{font-size:16px;color:var(--ink2)}
.answer{background:#fff;border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:12px;padding:14px 16px;margin:16px 0}
.answer b{color:var(--teal2)}
.pill{display:inline-block;background:#eef4f2;border:1px solid #d6e6e2;color:var(--teal2);border-radius:999px;padding:2px 10px;font-size:13px;font-weight:600;margin:2px 4px 2px 0}
#map{height:300px;border-radius:12px;border:1px solid var(--line);margin:14px 0}
h2{font-size:13px;letter-spacing:.1em;text-transform:uppercase;margin:26px 0 10px}
.cards{display:grid;gap:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.ch{display:flex;align-items:center;justify-content:space-between;gap:8px}
.ch h3{margin:0;font-size:17px}
.rive{font-size:12px;font-weight:700;color:var(--teal2);background:#eef4f2;border:1px solid #d6e6e2;border-radius:999px;padding:2px 9px}
.tag{font-size:11px;font-weight:700;border-radius:999px;padding:2px 9px}
.tag.quick{color:#1d6b3a;background:#e7f3ea;border:1px solid #c6e3cf}
.tag.rando{color:#8a4b1e;background:#f6ecde;border:1px solid #e6cfb0}
.meta{color:var(--ink2);font-size:13px;margin:2px 0 6px}
.chip{display:inline-block;background:#f3ecdc;border:1px solid #e6d8b8;color:#8a6a1e;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:700;margin-left:4px}
.hi{margin:6px 0 10px;font-size:14px}
.facts{display:grid;gap:6px}
.f{display:flex;justify-content:space-between;font-size:13px;border-bottom:1px dashed var(--line);padding:3px 0;gap:10px}
.f span{color:var(--ink2);flex:0 0 auto}.f b{font-weight:600;text-align:right}
.fiche{display:inline-block;margin-top:10px;color:var(--teal);font-weight:600;text-decoration:none;font-size:14px}
.q{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}
.q summary{font-weight:600;cursor:pointer}.q p{color:var(--ink2);margin:8px 0 2px}
.note{font-size:12px;color:var(--ink2);margin-top:8px}
footer{margin-top:30px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink2);text-align:center}"""


def L(d, lang):
    """Resolve an i18n dict to lang with FR fallback."""
    if not isinstance(d, dict):
        return d
    return d.get(lang) or d.get("fr") or ""


def esc(s):
    return _html.escape(str(s or ""), quote=True)


def fiche_facts(fiche, lang):
    i = fiche.get("i18n", {})
    return (i.get(lang, {}).get("facts") or i.get("fr", {}).get("facts") or {})


def fiche_name(fiche, lang):
    i = fiche.get("i18n", {})
    return i.get(lang, {}).get("name") or i.get("fr", {}).get("name") or fiche.get("slug")


def url_for(slug, lang):
    return f"{BASE}/{slug}" if lang == "fr" else f"{BASE}/{lang}/{slug}"


def render_card(hub, m, fiche, lang):
    name = fiche_name(fiche, lang)
    facts = fiche_facts(fiche, lang)
    head_right = ""
    if m.get("rive"):
        head_right = f'<span class="rive">{esc(L(RIVE.get(m["rive"], {"fr": m["rive"]}), lang))}</span>'
    elif m.get("tag") in ("quick", "rando"):
        cls = m["tag"]
        head_right = f'<span class="tag {cls}">{esc(L(TAGS_BUILTIN[cls], lang))}</span>'
    # commune + geo-verified badge + seasonal chip
    bits = [esc(facts.get("commune") or fiche.get("commune") or "")]
    if fiche.get("geo_verified"):
        bits.append(esc(L(UI["verified"], lang)))
    meta = " · ".join(b for b in bits if b)
    chip = ""
    if m.get("tag") == "seasonal":
        chip = f' <span class="chip">{esc(L(TAGS_BUILTIN["seasonal"], lang))}</span>'
    hi = ""
    if m.get("hi"):
        hv = L(m["hi"], lang)
        if hv:
            hi = f'<p class="hi">{esc(hv)}</p>'
    # facts rows
    rows = []
    for fs in hub["facts_shown"]:
        field = fs["field"]
        label = esc(L(FACT_LABELS.get(field, fs.get("label", {})), lang) or L(fs.get("label", {}), lang))
        val = facts.get(field)
        if not val:
            if fs.get("mode") == "if_present":
                continue
            val_html = f'<a class="fiche" style="margin:0;font-size:13px" href="{url_for(fiche["slug"], lang)}">{esc(L(UI["voir_fiche"], lang))}</a>'
        else:
            val_html = esc(val)
        rows.append(f'<div class="f"><span>{label}</span><b>{val_html}</b></div>')
    facts_html = '<div class="facts">' + "".join(rows) + "</div>" if rows else ""
    return (
        '<article class="card">\n'
        f'  <div class="ch"><h3>{esc(name)}</h3>{head_right}</div>\n'
        f'  <div class="meta">{meta}{chip}</div>\n'
        f'  {hi}{facts_html}\n'
        f'  <a class="fiche" href="{url_for(fiche["slug"], lang)}">{esc(L(UI["see_fiche"], lang))}</a>\n'
        '</article>'
    )


def schema_block(hub, members_fiches, lang):
    items = []
    for i, (m, f) in enumerate(members_fiches, 1):
        items.append({"@type": "ListItem", "position": i,
                      "name": fiche_name(f, lang), "url": url_for(f["slug"], lang) + "/"})
    itemlist = {"@type": "ItemList", "name": L(hub["h1"], lang), "itemListElement": items}
    faq = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": L(q["q"], lang),
         "acceptedAnswer": {"@type": "Answer", "text": L(q["a"], lang)}}
        for q in hub.get("faq", [])]}
    graph = {"@context": "https://schema.org", "@graph": [itemlist, faq]}
    return json.dumps(graph, ensure_ascii=False)


def render_hub(hub, lang, fiches):
    members_fiches = [(m, fiches[m["slug"]]) for m in hub["members"] if m["slug"] in fiches]
    # group by bucket, preserving registry order
    by_bucket = {}
    for m, f in members_fiches:
        by_bucket.setdefault(m["bucket"], []).append((m, f))

    sections = []
    for b in hub["buckets"]:
        grp = by_bucket.get(b["key"], [])
        if not grp:
            continue
        label = f'{esc(L(b["label"], lang))} · {len(grp)}'
        cards = "".join(render_card(hub, m, f, lang) for m, f in grp)
        sections.append(f'<h2 style="color:{b["color"]}">{label}</h2>\n<div class="cards">{cards}</div>')

    pills = "".join(f'<span class="pill">{esc(p)}</span>' for p in (L(hub.get("pills", {}), lang) or []))
    faq_html = "".join(
        f'<details class="q"><summary>{esc(L(q["q"], lang))}</summary><p>{esc(L(q["a"], lang))}</p></details>'
        for q in hub.get("faq", []))

    # map data
    if hub.get("map"):
        colors = {b["key"]: b["color"] for b in hub["buckets"]}
        pts = []
        for m, f in members_fiches:
            lat, lng = f.get("latitude"), f.get("longitude")
            if lat is None or lng is None:
                continue
            facts = fiche_facts(f, lang)
            pts.append({"name": fiche_name(f, lang),
                        "commune": facts.get("commune") or f.get("commune") or "",
                        "url": url_for(f["slug"], lang),
                        "color": colors.get(m["bucket"], "#155059"),
                        "lat": lat, "lng": lng})
        map_data = json.dumps(pts, ensure_ascii=False)
        map_script = (
            f'<script>var B={map_data};'
            "var map=L.map('map',{scrollWheelZoom:false});"
            "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap'}).addTo(map);"
            "var g=[];B.forEach(function(b){var m=L.circleMarker([b.lat,b.lng],{radius:8,color:'#155059',fillColor:b.color,fillOpacity:.95,weight:2}).addTo(map);"
            "m.bindPopup('<b>'+b.name+'</b><br>'+b.commune+'<br><a href=\"'+b.url+'\">'+"
            f"{json.dumps(L(UI['see_fiche'], lang))}+'</a>');g.push([b.lat,b.lng]);}});"
            "if(g.length)map.fitBounds(L.latLngBounds(g).pad(.15));</script>")
        head_leaflet = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
                        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>')
        map_div = '<div id="map"></div>'
    else:
        map_script = map_div = head_leaflet = ""

    # linked-hub cards (a master hub points at sub-hubs by slug)
    linked_html = ""
    linked = [_ALL_HUBS[s] for s in hub.get("linked_hubs", []) if s in _ALL_HUBS]
    if linked:
        cards = "".join(
            '<article class="card"><div class="ch"><h3>' + esc(L(lh["h1"], lang)) + '</h3>'
            f'<span class="rive">{len(lh.get("members", []))}</span></div>'
            f'<a class="fiche" href="{url_for(lh["slug"], lang)}">{esc(L(UI["see_guide"], lang))}</a></article>'
            for lh in linked)
        linked_html = (f'<h2 style="color:var(--teal)">{esc(L(UI["guides"], lang))}</h2>'
                       f'<div class="cards">{cards}</div>')

    foot = L(hub.get("footer_note", {}), lang)
    foot_html = f'<p class="note">{esc(foot)}</p>' if foot else ""

    return f"""<!doctype html><html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(L(hub["title"], lang))}</title>
<meta name="description" content="{esc(L(hub["description"], lang))}">
{head_leaflet}
<script type="application/ld+json">{schema_block(hub, members_fiches, lang)}</script>
<style>{CSS}</style></head><body><div class="wrap">

<div class="kicker">{esc(L(hub.get("kicker", {}), lang))}</div>
<h1>{esc(L(hub["h1"], lang))}</h1>
<p class="lead">{L(hub["lead"], lang)}</p>

<div class="answer">{L(hub["answer"], lang)}
<div style="margin-top:8px">{pills}</div></div>

{linked_html}

{map_div}

{"".join(sections)}
{foot_html}

<h2 style="color:var(--teal)">{esc(L(UI["faq"], lang))}</h2>
{faq_html}

<footer>© 2026 · Bleu canard édition · Edmaster &amp; Claudius · Tous droits réservés 🦆</footer>
</div>
{map_script}
</body></html>"""


MARK_A, MARK_B = "<!--intent-hubs:start-->", "<!--intent-hubs:end-->"


def inject_category_links(hub_links_by_cat, lang):
    """Add a reachable link to each intent hub from its category hub page."""
    import re
    for cat, links in hub_links_by_cat.items():
        slug = (hub_locale_map(cat).get(lang) or cat) if lang != "fr" else cat
        path = os.path.join(ROOT, slug, "index.html") if lang == "fr" else os.path.join(ROOT, lang, slug, "index.html")
        if not os.path.exists(path):
            continue
        html = open(path, encoding="utf-8").read()
        # strip prior block AND any whitespace before it (idempotent — no
        # accumulating newlines across rebuilds → byte-stable)
        html = re.sub(r"\s*" + re.escape(MARK_A) + r".*?" + re.escape(MARK_B), "", html, flags=re.S)
        block = (MARK_A + '<nav class="intent-hubs" style="max-width:760px;margin:18px auto;padding:0 18px">'
                 + "".join(f'<a href="{u}" style="display:inline-block;margin:2px 8px 2px 0;color:#1F6E78;font-weight:600">{esc(t)} →</a>'
                          for u, t in links)
                 + '</nav>' + MARK_B)
        html = html.replace("</body>", "\n" + block + "</body>", 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)


def main():
    global _ALL_HUBS
    hubs = json.loads(open(REGISTRY, encoding="utf-8").read())
    _ALL_HUBS = {h["slug"]: h for h in hubs}
    # load member fiches once
    need = {m["slug"] for h in hubs for m in h["members"]}
    fiches = {}
    for slug in need:
        fp = os.path.join(JSON_DIR, f"{slug}.json")
        if os.path.exists(fp):
            fiches[slug] = json.loads(open(fp, encoding="utf-8").read())
    written = 0
    for lang in LANGS:
        cat_links = {}
        for hub in hubs:
            html = render_hub(hub, lang, fiches)
            out = os.path.join(ROOT, f"{hub['slug']}.html") if lang == "fr" \
                else os.path.join(ROOT, lang, f"{hub['slug']}.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(html)
            written += 1
            cat_links.setdefault(hub["category_hub"], []).append(
                (url_for(hub["slug"], lang), L(hub["h1"], lang)))
        inject_category_links(cat_links, lang)
    print(f"build_intent_hubs: {len(hubs)} hub(s) × {len(LANGS)} locales = {written} pages; "
          f"category links injected")


if __name__ == "__main__":
    main()
