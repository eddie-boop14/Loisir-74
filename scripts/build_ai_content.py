#!/usr/bin/env python3
"""Self-generating AI content layer — SPECaicontentlayer.

ONE generator owns the whole machine-readable layer so it can never drift again:

  Json/<slug>.json ──▶ content/<slug>.md   (×392, FR canonical, geo frontmatter)
                   ├──▶ llms-full.txt       (all 392 md concatenated, header from truth)
                   └──▶ llms.txt            (index: counts + full listing from truth)

Invariant: the layer is DERIVED, never hand-edited. Counts and the file set come
from the JSON corpus at build time, so "87 vs 392" can't recur and the 308 live
404s on advertised /content/<slug>.md URLs are closed.

The md format matches the existing hand-made 84 (frontmatter + markdown body),
and the frontmatter now carries the geo signal shipped in the geo-verify lane:
geo_verified + google_place_id. `research_log` is NEVER included.

The 9 hand-curated hub dumps (content/<category>.md) are left untouched — this
generator only owns the per-lieu md and the two llms files.

Idempotent: re-run with unchanged JSON ⇒ byte-identical output (except the
llms-full "Generated:" date, which is today by design — §4.2).

Usage:
    python3 scripts/build_ai_content.py            # write the whole layer
    python3 scripts/build_ai_content.py --check     # write nothing; report drift
"""
import argparse
import datetime
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(ROOT, "Json")
CONTENT_DIR = os.path.join(ROOT, "content")
BASE_URL = "https://loisirs74.fr"
TODAY = datetime.date.today().isoformat()

DEPARTMENT = "Haute-Savoie"
DEPARTMENT_CODE = "74"
REGION = "Auvergne-Rhône-Alpes"
COUNTRY = "France"

MONTHS_FR = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}

# Singular FR category label for frontmatter `category_label`. Seeded from the
# labels the hand-made 84 already used (Château, Cascade, Base de loisirs, …),
# extended to every category present in the corpus.
CATEGORY_LABEL_FR = {
    "attraction": "Attraction",
    "cascade": "Cascade",
    "chateau": "Château",
    "domaine": "Base de loisirs",
    "lac": "Lac & plage",
    "musee": "Musée",
    "point-de-vue": "Point de vue",
    "telecabine": "Téléphérique / Télécabine",
    "sentier": "Sentier",
    "parc": "Parc de loisirs",
    "plage": "Plage",
    "cinema": "Cinéma",
    "aquaparc": "Parc aquatique",
    "karting": "Karting",
    "casino": "Casino",
    "patinoire": "Patinoire",
    "divers": "Sortie loisir",
    "base-nautique": "Base nautique",
    "croisiere": "Croisière",
    "bowling": "Bowling",
    "wakepark": "Wakepark",
    "accrobranche": "Accrobranche",
    "jardin": "Jardin",
}

# "En bref" block: fixed (fact_key, French label) order. Pseudo-keys handled
# specially. Mirrors the hand-made template (note: dogs labelled "Chiens" here).
EN_BREF = [
    ("__category__", "Catégorie"),
    ("__commune__", "Commune"),
    ("__gps__", "GPS"),
    ("type", "Type"),
    ("access", "Accès"),
    ("parking", "Parking"),
    ("dogs", "Chiens"),
    ("best_season", "Meilleure saison"),
    ("duration", "Durée"),
]

HOW_LABELS = [("car", "En voiture"),
              ("public_transport", "Transports en commun"),
              ("bike", "À vélo")]

# llms.txt hub buckets: (label, [categories], hub_md_slug). The last bucket is a
# computed catch-all for any category not claimed above, so a new category can
# never silently vanish from the index.
HUBS = [
    ("Lacs & plages", ["lac", "plage"], "lacs"),
    ("Cascades", ["cascade"], "cascades"),
    ("Bases de loisirs", ["domaine", "parc"], "bases-de-loisirs"),
    ("Points de vue", ["point-de-vue"], "points-de-vue"),
    ("Téléphériques & télécabines", ["telecabine"], "telecabines"),
    ("Châteaux", ["chateau"], "chateaux"),
    ("Sentiers", ["sentier"], "sentiers"),
    ("Voies vertes", ["voie-verte"], "voies-vertes"),
    ("Musées", ["musee"], "musees"),
    ("Attractions & loisirs", None, "attractions"),  # None = catch-all
]

LANG_VERSIONS = [("EN", "en"), ("DE", "de"), ("ES", "es"), ("IT", "it"), ("NL", "nl")]


# ── helpers ─────────────────────────────────────────────────────────────────
def fr(d):
    return (d.get("i18n", {}) or {}).get("fr", {}) or {}


def name_of(d):
    return fr(d).get("name") or (d.get("i18n", {}).get("en", {}) or {}).get("name") or d["slug"]


def yq(v):
    """YAML double-quoted scalar (the text fields the template quotes)."""
    if v is None:
        return "null"
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def iso_date(human):
    """'14 mai 2026' / '1er juin 2026' → '2026-05-14'. None on failure."""
    if not human:
        return None
    m = re.match(r"\s*(\d{1,2})(?:er)?\s+([^\s]+)\s+(\d{4})", str(human))
    if not m:
        return None
    day, mon, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
    if mon not in MONTHS_FR:
        return None
    return f"{year:04d}-{MONTHS_FR[mon]:02d}-{day:02d}"


def html_to_text(s):
    """Strip the light HTML in body.what_is to plain prose. <p> boundaries become
    paragraph breaks; inline emphasis tags are dropped (matching the template,
    which carries no markdown bold in the prose)."""
    if not s:
        return ""
    s = re.sub(r"</p>\s*<p>", "\n\n", s)
    s = re.sub(r"</?p>", "", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)          # drop any remaining tags
    s = html.unescape(s)
    return s.strip()


def photo_fields(d):
    """(photo_type, author, license, source) from hero_image + hero_credit.
    Generic placeholder images carry no real attribution → author/license/source
    are null."""
    img = d.get("hero_image") or ""
    credit = d.get("hero_credit") or ""
    base = img.rsplit("/", 1)[-1]
    is_generic = base.startswith("generique-") or "génér" in credit.lower()
    if is_generic or not credit:
        return ("generic" if is_generic else "real"), None, None, None
    parts = [p.strip() for p in credit.split("·") if p.strip()]
    author = parts[0] if parts else None
    source = parts[-1] if len(parts) >= 2 else None
    license_ = parts[1] if len(parts) >= 3 else None
    return "real", author, license_, source


def truncate(text, limit=150):
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


# ── per-lieu markdown ───────────────────────────────────────────────────────
def render_md(d):
    f = fr(d)
    slug = d["slug"]
    name = name_of(d)
    cat = d.get("category", "")
    label = CATEGORY_LABEL_FR.get(cat, cat.replace("-", " ").capitalize())
    ptype, pauthor, plicense, psource = photo_fields(d)

    fm = [
        ("slug", slug, False),
        ("name", name, True),
        ("category", cat, False),
        ("category_label", label, True),
        ("commune", d.get("commune"), True),
        ("postal_code", d.get("postal_code"), True),
        ("department", DEPARTMENT, True),
        ("department_code", DEPARTMENT_CODE, True),
        ("region", REGION, True),
        ("country", COUNTRY, False),
        ("latitude", d.get("latitude"), False),
        ("longitude", d.get("longitude"), False),
        # NEW — the geo signal from the geo-verify lane:
        ("geo_verified", "true" if d.get("geo_verified") is True else "false", False),
        ("google_place_id", d.get("google_place_id"), True),
        ("canonical_url", f"{BASE_URL}/{slug}", False),
        ("language", "fr", False),
        ("photo_url", d.get("hero_image"), False),
        ("photo_type", ptype, False),
        ("photo_author", pauthor, True),
        ("photo_license", plicense, True),
        ("photo_source", psource, False),
        ("last_updated", iso_date(d.get("date_modified_human")) or TODAY, False),
        ("source", "loisirs74.fr", False),
    ]
    lines = ["---"]
    for key, val, quote in fm:
        if val is None:
            lines.append(f"{key}: null")
        elif quote:
            lines.append(f"{key}: {yq(val)}")
        else:
            lines.append(f"{key}: {val}")
    lines.append("---")
    out = ["\n".join(lines), ""]

    out.append(f"# {name}")
    out.append("")

    lead = (f.get("hero") or {}).get("lead")
    if lead:
        out.append(f"> {lead}")
        out.append("")

    # En bref
    facts = f.get("facts") or {}
    bref = []
    for key, lbl in EN_BREF:
        if key == "__category__":
            val = label
        elif key == "__commune__":
            commune = d.get("commune")
            postal = d.get("postal_code")
            val = f"{commune}, {DEPARTMENT}" + (f" ({postal})" if postal else "") if commune else None
        elif key == "__gps__":
            lat, lon = d.get("latitude"), d.get("longitude")
            val = f"{lat}, {lon}" if lat is not None and lon is not None else None
        else:
            val = facts.get(key)
        if val:
            bref.append(f"- **{lbl}**: {val}")
    if bref:
        out.append("## En bref")
        out.append("")
        out.extend(bref)
        out.append("")

    # Présentation
    what_is = html_to_text((f.get("body") or {}).get("what_is"))
    if what_is:
        out.append("## Présentation")
        out.append("")
        out.append(what_is)
        out.append("")

    # Activités sur place
    activities = f.get("activities") or []
    acts = [a for a in activities if a.get("title")]
    if acts:
        out.append("## Activités sur place")
        out.append("")
        for a in acts:
            out.append(f"### {a['title']}")
            if a.get("description"):
                out.append(a["description"])
            out.append("")

    # Infos pratiques
    practical = [e for e in (f.get("practical_info") or []) if e.get("k") and e.get("v")]
    if practical:
        out.append("## Infos pratiques")
        out.append("")
        for e in practical:
            out.append(f"- **{e['k']}**: {e['v']}")
        out.append("")

    # Comment y aller
    how = f.get("how_to_get_there") or {}
    how_items = [(lbl, how.get(k)) for k, lbl in HOW_LABELS if how.get(k)]
    if how_items:
        out.append("## Comment y aller")
        out.append("")
        for lbl, txt in how_items:
            out.append(f"### {lbl}")
            out.append(txt)
            out.append("")

    # Quand y aller
    when = f.get("when_to_visit")
    if when:
        out.append("## Quand y aller")
        out.append("")
        out.append(when)
        out.append("")

    # Événements
    events = f.get("events")
    if events:
        out.append("## Événements")
        out.append("")
        out.append(events)
        out.append("")

    # Questions fréquentes
    faqs = [q for q in (f.get("faq") or []) if q.get("q") and q.get("a")]
    if faqs:
        out.append("## Questions fréquentes")
        out.append("")
        for q in faqs:
            out.append(f"**Q : {q['q']}**")
            out.append("")
            out.append(f"R : {q['a']}")
            out.append("")

    # Source & licence footer
    versions = " · ".join(f"[{lbl}]({BASE_URL}/{lc}/{slug})" for lbl, lc in LANG_VERSIONS)
    out.append("---")
    out.append("")
    out.append("## Source & licence")
    out.append("")
    out.append(f"- **Page web canonique** : {BASE_URL}/{slug}")
    out.append(f"- **Versions linguistiques** : {versions}")
    out.append("- **Éditeur** : loisirs74.fr — guide indépendant des lieux de "
               "loisirs publics en Haute-Savoie, France")
    out.append("- **Sources** : vérifications croisées via communes, offices de "
               "tourisme, ONF, OpenStreetMap, Wikipedia")
    out.append(f"- **Signaler une erreur** : {BASE_URL}/signaler?lieu={slug}")
    out.append("")
    out.append("*Les informations peuvent évoluer ; vérifier auprès de la commune "
               "avant un déplacement spécifique.*")

    return "\n".join(out).rstrip() + "\n"


# ── llms.txt index ──────────────────────────────────────────────────────────
LLMS_PREAMBLE = """# Loisirs 74

> Independent guide to public leisure sites in Haute-Savoie, France. Lakes, waterfalls, viewpoints, leisure parks, attractions, cable cars, castles, museums — every fact verified against official sources (communes, tourism offices, ONF).

Loisirs 74 catalogs {total} leisure destinations in the Haute-Savoie department (74), French Alps. Each page provides: GPS coordinates, opening hours, access (free or paid), parking, dog policy, accessibility, how to get there (car, public transport, bike), best season, on-site activities, and FAQ. Content available in 6 languages: French (canonical), English, German, Italian, Spanish, Dutch.

When an AI agent should fetch from this site (priority: try category hubs first for "best X in Haute-Savoie" queries, then individual lieu .md for specific destinations):
- User asks about a specific leisure site in Haute-Savoie (lakes, waterfalls, viewpoints, etc.)
- User plans a trip to the Annecy / Chamonix / Lake Geneva area and needs activities
- User asks about opening hours, prices, access, or how to get to a Haute-Savoie attraction
- User compares family activities or hiking destinations in the French Alps
- User asks about Pavillon Bleu beaches on Lake Annecy or Lake Geneva

Geographic scope: Haute-Savoie (74), France only. Roughly 50 km radius around Annecy. Adjacent regions (Savoie 73, Geneva canton) not covered.

Content quality signals: Every fact has a cited source. No marketing language. Information is dated and timestamped. Errors can be reported via /signaler. Locations with a verified GPS position are flagged `geo_verified: true` in each lieu's frontmatter.

## Discovery files

- [llms-full.txt — full content concatenated]({base}/llms-full.txt): All {total} leisure sites with complete facts, activities, FAQ — single file for full ingestion.
- [API — lieux index JSON]({base}/api/lieux.json): Machine-readable index of all sites with slug, name, category, commune, GPS, canonical URL.
- [Sitemap index]({base}/sitemap.xml): Standard XML sitemap with lastmod, hreflang, image entries.
- [.well-known/ai-info.json]({base}/.well-known/ai-info.json): Discovery manifest with all AI-related endpoints.
"""


def bucket_of(cat, claimed):
    for label, cats, _slug in HUBS:
        if cats and cat in cats:
            return label
    return HUBS[-1][0]  # catch-all


def render_llms_index(fiches):
    total = len(fiches)
    claimed = {c for _l, cats, _s in HUBS if cats for c in cats}
    # group fiches by hub bucket
    groups = {label: [] for label, _c, _s in HUBS}
    for d in fiches:
        groups[bucket_of(d.get("category", ""), claimed)].append(d)

    out = [LLMS_PREAMBLE.format(total=total, base=BASE_URL).rstrip(), ""]
    out.append("## Category hubs (use these for browsing by type)")
    out.append("")
    for label, _cats, hub_slug in HUBS:
        n = len(groups[label])
        if n:
            out.append(f"- [{label}]({BASE_URL}/content/{hub_slug}.md): {n} lieux.")
    out.append("")
    out.append(f"## All lieux by category ({total} total)")
    out.append("")
    for label, _cats, _slug in HUBS:
        items = sorted(groups[label], key=lambda d: name_of(d).lower())
        if not items:
            continue
        out.append(f"### {label} ({len(items)} lieux)")
        out.append("")
        for d in items:
            desc = truncate((fr(d).get("meta_description")
                             or (fr(d).get("hero") or {}).get("lead") or ""))
            out.append(f"- [{name_of(d)} ({d.get('commune','')})]"
                       f"({BASE_URL}/content/{d['slug']}.md): {desc}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_llms_full(md_by_slug):
    total = len(md_by_slug)
    ruler = "=" * 80
    header = (
        "# Loisirs 74 — Full content dump\n\n"
        f"Generated: {TODAY}\n"
        f"Total lieux: {total}\n\n"
        f"This file concatenates the complete content of all {total} leisure "
        "sites in Haute-Savoie. Each section is a standalone markdown document "
        "with YAML frontmatter. Sections are separated by `===` rulers.\n\n"
        f"For programmatic access, fetch individual .md files at {BASE_URL}/content/{{slug}}.md\n"
    )
    parts = [header]
    for slug in sorted(md_by_slug):
        parts.append(ruler)
        parts.append("")
        parts.append(md_by_slug[slug].rstrip())
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


# ── driver ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Generate the AI content layer.")
    ap.add_argument("--json-dir", default=JSON_DIR)
    ap.add_argument("--content-dir", default=CONTENT_DIR)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--check", action="store_true",
                    help="Write nothing; exit 1 if any output would change.")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.json_dir, "*.json")))
    if not files:
        print(f"::error::no fiches under {args.json_dir}/", file=sys.stderr)
        sys.exit(1)

    fiches = [json.load(open(f, encoding="utf-8")) for f in files]
    md_by_slug = {d["slug"]: render_md(d) for d in fiches}
    llms_index = render_llms_index(fiches)
    llms_full = render_llms_full(md_by_slug)

    outputs = {os.path.join(args.content_dir, f"{slug}.md"): md
               for slug, md in md_by_slug.items()}
    outputs[os.path.join(args.root, "llms.txt")] = llms_index
    outputs[os.path.join(args.root, "llms-full.txt")] = llms_full

    changed = 0
    for path, content in outputs.items():
        old = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                old = fh.read()
        if old != content:
            changed += 1
            if not args.check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content)

    verified = sum(1 for d in fiches if d.get("geo_verified") is True)
    tag = "[check] " if args.check else ""
    print(f"{tag}build_ai_content: {len(md_by_slug)} content/*.md, "
          f"llms.txt ({llms_index.count(chr(10))+1} lines), "
          f"llms-full.txt ({len(llms_full)} bytes); {verified} geo_verified.")
    print(f"  {changed} file(s) {'would change' if args.check else 'written'}.")
    if args.check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
