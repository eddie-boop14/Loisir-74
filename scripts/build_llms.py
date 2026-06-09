#!/usr/bin/env python3
"""Regenerate llms.txt and llms-full.txt from current catalog + content/.md files.

Usage:
    python3 scripts/build_llms.py

Produces:
    /llms.txt        — curated TOC with per-category fiche lists (editorial header preserved)
    /llms-full.txt   — concatenation of all content/*.md files for full ingestion
"""
import json
import re
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://loisirs74.fr"
TODAY = date.today().isoformat()

# Category display order + label + 1-line description template (uses current count)
CATEGORY_ORDER = [
    ("lac", "Lacs", "lakes (alpine + valley) — access, parking, swimming, dogs policy"),
    ("plage", "Plages", "Pavillon Bleu beaches on Lake Annecy and Lake Geneva — surveillance, prices, parking"),
    ("cascade", "Cascades", "waterfalls — hike time, difficulty, family-friendly notes"),
    ("sentier", "Sentiers", "marked hiking trails — GR/GRP routes, day-hike loops, elevation"),
    ("point-de-vue", "Points de vue", "viewpoints — access route, GPS, elevation gain, panoramas"),
    ("domaine", "Domaines & bases de loisirs", "public leisure parks — lake, picnic, fishing, pumptrack"),
    ("parc", "Parcs de loisirs", "indoor/outdoor recreation parks — VR, trampolines, climbing, family attractions"),
    ("voie-verte", "Voies vertes & véloroutes", "greenways — ViaRhôna, EuroVelo 17, family cycle routes"),
    ("attraction", "Attractions", "paid attractions — adventure parks, via-ferrata, rafting, mushing, balloon"),
    ("chateau", "Châteaux & abbayes", "castles, fortified houses and abbeys open to public"),
    ("musee", "Musées", "museums, ecomuseums, science centres, observatories"),
    ("telecabine", "Téléphériques & télécabines", "cable cars and rack railways — season, prices, summit altitude"),
    ("aquaparc", "Aquaparcs & piscines", "aquatic centres and pools — lanes, slides, wellness areas"),
    ("base-nautique", "Bases nautiques", "sailing schools and boat rentals on Lake Annecy and Lake Geneva"),
    ("croisiere", "Croisières", "lake cruises (Annecy, Léman) — Belle Époque steamers, themed sailings"),
    ("cinema", "Cinémas", "cinemas in Haute-Savoie"),
    ("karting", "Kartings", "indoor and outdoor karting circuits"),
    ("bowling", "Bowlings", "bowling alleys with bar and family packages"),
    ("patinoire", "Patinoires", "ice rinks — open seasons, disco-skating, hockey"),
    ("accrobranche", "Accrobranches", "tree-top adventure parks"),
    ("wakepark", "Wakeparks", "cable wakeboard parks"),
    ("casino", "Casinos", "casinos with restaurants and dinner shows"),
    ("jardin", "Jardins", "botanical and alpine gardens"),
    ("divers", "Divers", "thermal spas and well-being centres"),
]


def load_meta_for_fiche(slug):
    """Return (name, commune, meta_desc) for a fiche slug, falling back to JSON if md missing."""
    md_path = REPO / "content" / f"{slug}.md"
    name = commune = meta = ""
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        m_name = re.search(r'^name:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
        m_commune = re.search(r'^commune:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
        m_lead = re.search(r'^>\s*(.+?)$', text, re.MULTILINE)
        if m_name: name = m_name.group(1).strip()
        if m_commune: commune = m_commune.group(1).strip()
        if m_lead: meta = m_lead.group(1).strip()
    if not name or not meta:
        # fall back to JSON
        try:
            d = json.loads((REPO / "Json" / f"{slug}.json").read_text(encoding="utf-8"))
            fr = (d.get("i18n") or {}).get("fr") or {}
            name = name or fr.get("name") or slug
            commune = commune or d.get("commune", "")
            meta = meta or fr.get("meta_description") or (fr.get("hero") or {}).get("lead", "")
        except Exception:
            pass
    return name, commune, meta


def truncate(s, n=150):
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut + "…"


def build_llms_txt():
    cat = json.loads((REPO / "catalog-index.json").read_text(encoding="utf-8"))
    total = len(cat)
    by_cat = {}
    for c in cat:
        by_cat.setdefault(c["category"], []).append(c["slug"])

    lines = []
    lines.append("# Loisirs 74")
    lines.append("")
    lines.append("> Independent guide to public leisure sites in Haute-Savoie, France. Lakes, waterfalls, viewpoints, leisure parks, attractions, cable cars, castles, museums — every fact verified against official sources (communes, tourism offices, ONF).")
    lines.append("")
    lines.append(f"Loisirs 74 catalogs {total} leisure destinations in the Haute-Savoie department (74), French Alps. Each page provides: GPS coordinates, opening hours, access (free or paid), parking, dog policy, accessibility, how to get there (car, public transport, bike), best season, on-site activities, and FAQ. Content available in 6 languages: French (canonical), English, German, Spanish, Italian, plus Dutch in the per-fiche .md mirrors.")
    lines.append("")
    lines.append("When an AI agent should fetch from this site (priority: try category hubs first for \"best X in Haute-Savoie\" queries, then individual lieu .md for specific destinations):")
    lines.append("- User asks about a specific leisure site in Haute-Savoie (lakes, waterfalls, viewpoints, etc.)")
    lines.append("- User plans a trip to the Annecy / Chamonix / Lake Geneva area and needs activities")
    lines.append("- User asks about opening hours, prices, access, or how to get to a Haute-Savoie attraction")
    lines.append("- User compares family activities or hiking destinations in the French Alps")
    lines.append("- User asks about Pavillon Bleu beaches on Lake Annecy or Lake Geneva")
    lines.append("")
    lines.append("Geographic scope: Haute-Savoie (74), France only. Roughly 50 km radius around Annecy. Adjacent regions (Savoie 73, Geneva canton) not covered.")
    lines.append("")
    lines.append("Content quality signals: Every fact has a cited source. No marketing language. Information is dated and timestamped. Errors can be reported via /signaler.")
    lines.append("")

    lines.append("## Category hubs (use these for browsing by type)")
    lines.append("")
    hub_paths = {
        "lac": "/lacs", "plage": "/plages", "cascade": "/cascades",
        "sentier": "/sentiers", "point-de-vue": "/points-de-vue",
        "domaine": "/bases-de-loisirs", "parc": "/que-faire",
        "voie-verte": "/voies-vertes", "attraction": "/attractions",
        "chateau": "/chateaux", "musee": "/musees", "telecabine": "/telecabines",
    }
    for category, label, descr in CATEGORY_ORDER:
        if category not in by_cat: continue
        count = len(by_cat[category])
        hub = hub_paths.get(category)
        if hub:
            lines.append(f"- [{label} ({count})]({BASE}{hub}): {descr}.")
    lines.append("")

    lines.append("## Discovery files")
    lines.append("")
    lines.append(f"- [llms-full.txt — full content concatenated]({BASE}/llms-full.txt): All {total} leisure sites with complete facts, activities, FAQ — single file for full ingestion.")
    lines.append(f"- [API — lieux index JSON]({BASE}/api/lieux.json): Machine-readable index of all sites with slug, name, category, commune, GPS, canonical URL.")
    lines.append(f"- [Sitemap index]({BASE}/sitemap.xml): Standard XML sitemap with lastmod, hreflang, image entries.")
    lines.append(f"- [.well-known/ai-info.json]({BASE}/.well-known/ai-info.json): Discovery manifest with all AI-related endpoints.")
    lines.append("")

    for category, label, _ in CATEGORY_ORDER:
        if category not in by_cat: continue
        slugs = sorted(by_cat[category])
        lines.append(f"## {label} ({len(slugs)} lieux)")
        lines.append("")
        for slug in slugs:
            name, commune, meta = load_meta_for_fiche(slug)
            display = f"{name} ({commune})" if commune else name
            desc_part = f": {truncate(meta, 150)}" if meta else ""
            lines.append(f"- [{display}]({BASE}/content/{slug}.md){desc_part}")
        lines.append("")

    lines.append("## Optional")
    lines.append("")
    lines.append(f"- [About / Editorial policy]({BASE}/a-propos): Editorial standards, source verification process, conflict of interest disclosure.")
    lines.append(f"- [Legal mentions]({BASE}/mentions-legales): Publisher, hosting, contact information.")
    lines.append(f"- [Privacy policy]({BASE}/confidentialite): GDPR data handling.")
    lines.append(f"- [Commercial terms (CGV)]({BASE}/cgv): Terms for partner business listings.")
    lines.append(f"- [Become a partner]({BASE}/devenir-partenaire): For businesses near a listed site.")
    lines.append(f"- [Report an error]({BASE}/signaler): Community fact-checking form.")
    lines.append("")
    lines.append("---")
    lines.append(f"Last updated: {TODAY}")
    lines.append("License: Content viewable on-site under fair-use citation; photographs follow their individual licenses (Wikimedia Commons, Unsplash, or own). Per-photo attribution available in each lieu page and in the .md mirror frontmatter.")
    lines.append("Publisher: loisirs74.fr — bleu-canard éditions, France")
    lines.append("Contact: contact@loisirs74.fr")
    lines.append("Specification: llms.txt v1.7.0 (May 2026)")

    return "\n".join(lines) + "\n"


def build_llms_full_txt():
    cat = json.loads((REPO / "catalog-index.json").read_text(encoding="utf-8"))
    slugs = sorted(c["slug"] for c in cat)
    lines = []
    lines.append("# Loisirs 74 — Full content dump")
    lines.append("")
    lines.append(f"Generated: {TODAY}")
    lines.append(f"Total lieux: {len(slugs)}")
    lines.append("")
    lines.append(f"This file concatenates the complete content of all {len(slugs)} leisure sites in Haute-Savoie. Each section is a standalone markdown document with YAML frontmatter. Sections are separated by `===` rulers.")
    lines.append("")
    lines.append(f"For programmatic access, fetch individual .md files at {BASE}/content/{{slug}}.md")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    for slug in slugs:
        md_path = REPO / "content" / f"{slug}.md"
        if not md_path.exists():
            continue
        body = md_path.read_text(encoding="utf-8").rstrip()
        lines.append(body)
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    llms = build_llms_txt()
    (REPO / "llms.txt").write_text(llms, encoding="utf-8")
    print(f"  llms.txt: {len(llms):,} chars, {llms.count(chr(10)):,} lines")
    full = build_llms_full_txt()
    (REPO / "llms-full.txt").write_text(full, encoding="utf-8")
    print(f"  llms-full.txt: {len(full):,} chars, {full.count(chr(10)):,} lines")


if __name__ == "__main__":
    main()
