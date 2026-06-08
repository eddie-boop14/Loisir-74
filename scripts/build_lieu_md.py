#!/usr/bin/env python3
"""Generate a per-fiche AI-consumption markdown from a fiche JSON.

Usage:
    python3 scripts/build_lieu_md.py Json/<slug>.json [--out-dir content]

Produces content/<slug>.md from i18n.fr fields + top-level metadata.
Mirrors the shape of the hand-written exemplar (acro-aventures-talloires.md):
YAML frontmatter, lead quote, sectioned body, FAQ, sources.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE_URL = "https://loisirs74.fr"

CATEGORY_LABEL = {
    "attraction": "Attraction", "musee": "Musée", "chateau": "Château",
    "lac": "Lac", "cascade": "Cascade", "sentier": "Sentier",
    "plage": "Plage", "domaine": "Domaine", "parc": "Parc",
    "aquaparc": "Aquaparc", "cinema": "Cinéma", "telecabine": "Télécabine",
    "karting": "Karting", "bowling": "Bowling", "patinoire": "Patinoire",
    "voie-verte": "Voie verte", "base-nautique": "Base nautique",
    "divers": "Divers", "croisiere": "Croisière", "accrobranche": "Accrobranche",
    "casino": "Casino", "jardin": "Jardin", "wakepark": "Wakepark",
    "point-de-vue": "Point de vue",
}


def strip_html(s):
    """HTML → plain text, preserving paragraph breaks."""
    if not s:
        return ""
    # Replace block breaks with newlines before stripping tags
    s = re.sub(r"</p>\s*<p>", "\n\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<li>", "\n- ", s, flags=re.IGNORECASE)
    s = re.sub(r"</?(p|ul|ol|strong|em|li|div|span)[^>]*>", "", s, flags=re.IGNORECASE)
    s = html.unescape(s)
    return s.strip()


def get_smart(node, key):
    """Look at top level of node, or nested under body."""
    if key in node and node[key]:
        return node[key]
    body = node.get("body") or {}
    if isinstance(body, dict) and key in body and body[key]:
        return body[key]
    return [] if key in ("activities", "faq", "practical_info") else ""


def yaml_str(s):
    """Quote string for YAML frontmatter."""
    if s is None:
        return '""'
    s = str(s)
    if any(ch in s for ch in ":#\n\"'") or s.startswith(" ") or s.endswith(" "):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def frontmatter(d):
    """Emit YAML frontmatter block."""
    slug = d["slug"]
    fr = d.get("i18n", {}).get("fr", {}) or {}
    name = fr.get("name") or d.get("slug")
    category = d.get("category", "")
    cat_label = CATEGORY_LABEL.get(category, category.title())
    commune = d.get("commune", "")
    postal = d.get("postal_code", "")
    department = d.get("department", "Haute-Savoie")
    lat = d.get("latitude")
    lon = d.get("longitude")
    hero = d.get("hero_image", "")
    hero_credit = d.get("hero_credit", "")
    date_mod = d.get("date_modified_human") or d.get("date_published_human", "")

    photo_type = "real"
    if hero and (hero.startswith("/generique-") or hero.startswith("generique-")):
        photo_type = "generic"
    elif not hero:
        photo_type = "none"

    # Parse hero_credit "<author> · <license> · <source>"
    photo_author = photo_license = photo_source = ""
    if hero_credit:
        parts = [p.strip() for p in hero_credit.split("·")]
        if len(parts) >= 1:
            photo_author = parts[0]
        if len(parts) >= 2:
            photo_license = parts[1]
        if len(parts) >= 3:
            photo_source = parts[2]

    lines = [
        "---",
        f"slug: {slug}",
        f"name: {yaml_str(name)}",
        f"category: {category}",
        f"category_label: {yaml_str(cat_label)}",
        f"commune: {yaml_str(commune)}",
        f"postal_code: {yaml_str(postal)}",
        f"department: {yaml_str(department)}",
        f"department_code: \"74\"",
        f"region: \"Auvergne-Rhône-Alpes\"",
        f"country: France",
    ]
    if lat is not None:
        lines.append(f"latitude: {lat}")
    if lon is not None:
        lines.append(f"longitude: {lon}")
    lines.append(f"canonical_url: {BASE_URL}/{slug}")
    lines.append("language: fr")
    if hero:
        lines.append(f"photo_url: {hero}")
        lines.append(f"photo_type: {photo_type}")
        if photo_author:
            lines.append(f"photo_author: {yaml_str(photo_author)}")
        if photo_license:
            lines.append(f"photo_license: {yaml_str(photo_license)}")
        if photo_source:
            lines.append(f"photo_source: {photo_source}")
    if date_mod:
        lines.append(f"last_updated: {date_mod}")
    lines.append(f"source: loisirs74.fr")
    lines.append("---")
    return "\n".join(lines)


def section_en_bref(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    facts = fr.get("facts") or {}
    cat = CATEGORY_LABEL.get(d.get("category", ""), d.get("category", ""))
    commune = d.get("commune", "")
    postal = d.get("postal_code", "")
    dep = d.get("department", "")
    lat = d.get("latitude")
    lon = d.get("longitude")
    lines = ["## En bref", ""]
    lines.append(f"- **Catégorie**: {cat}")
    if commune:
        loc = f"{commune}, {dep}"
        if postal:
            loc += f" ({postal})"
        lines.append(f"- **Commune**: {loc}")
    if lat is not None and lon is not None:
        lines.append(f"- **GPS**: {lat}, {lon}")
    for k, label in [
        ("type", "Type"), ("access", "Accès"), ("tarif", "Tarif"),
        ("parking", "Parking"), ("dogs", "Chiens"),
        ("best_season", "Meilleure saison"), ("duration", "Durée"),
        ("altitude", "Altitude"),
    ]:
        v = facts.get(k)
        if v:
            lines.append(f"- **{label}**: {v}")
    return "\n".join(lines)


def section_presentation(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    body = fr.get("body") or {}
    what = body.get("what_is", "") if isinstance(body, dict) else ""
    text = strip_html(what)
    if not text:
        return ""
    return "## Présentation\n\n" + text


def section_activities(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    acts = get_smart(fr, "activities")
    if not acts:
        return ""
    out = ["## Activités sur place", ""]
    for a in acts:
        if not isinstance(a, dict):
            continue
        title = a.get("title", "").strip()
        desc = a.get("description") or a.get("body") or ""
        desc = strip_html(desc)
        if title:
            out.append(f"### {title}")
            if desc:
                out.append(desc)
            out.append("")
    return "\n".join(out).rstrip()


def section_pratique(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    pi = get_smart(fr, "practical_info")
    if not pi:
        return ""
    out = ["## Infos pratiques", ""]
    for p in pi:
        if not isinstance(p, dict):
            continue
        k = p.get("k") or p.get("key") or ""
        v = p.get("v") or p.get("value") or ""
        v = strip_html(v) if v else ""
        if k:
            out.append(f"- **{k}**: {v}")
    return "\n".join(out)


def section_acces(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    h = fr.get("how_to_get_there") or {}
    if not isinstance(h, dict):
        return ""
    out = ["## Comment y aller", ""]
    parts = [
        ("car", "En voiture"),
        ("public_transport", "Transports en commun"),
        ("bike", "À vélo"),
    ]
    for key, label in parts:
        v = h.get(key)
        if v:
            txt = strip_html(v)
            out.append(f"### {label}")
            out.append(txt)
            out.append("")
    if len(out) <= 2:
        return ""
    return "\n".join(out).rstrip()


def section_quand(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    when = fr.get("when_to_visit", "")
    if not when:
        return ""
    return "## Quand y aller\n\n" + strip_html(when)


def section_faq(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    faq = get_smart(fr, "faq")
    if not faq:
        return ""
    out = ["## Questions fréquentes", ""]
    for q in faq:
        if not isinstance(q, dict):
            continue
        question = q.get("q", "").strip()
        answer = q.get("a", "").strip()
        if question and answer:
            out.append(f"**Q : {question}**")
            out.append("")
            out.append(f"R : {strip_html(answer)}")
            out.append("")
    return "\n".join(out).rstrip()


def section_sources(d):
    slug = d["slug"]
    return f"""---

## Source & licence

- **Page web canonique** : {BASE_URL}/{slug}
- **Versions linguistiques** : [EN]({BASE_URL}/en/{slug}) · [DE]({BASE_URL}/de/{slug}) · [ES]({BASE_URL}/es/{slug}) · [IT]({BASE_URL}/it/{slug})
- **Éditeur** : loisirs74.fr — guide indépendant des lieux de loisirs publics en Haute-Savoie, France
- **Sources** : vérifications croisées via communes, offices de tourisme, ONF, OpenStreetMap, Wikipedia
- **Signaler une erreur** : {BASE_URL}/signaler?lieu={slug}

*Les informations peuvent évoluer ; vérifier auprès de la commune avant un déplacement spécifique.*
"""


def build_md(d):
    fr = d.get("i18n", {}).get("fr", {}) or {}
    name = fr.get("name") or d.get("slug")
    meta_desc = fr.get("meta_description") or (fr.get("hero") or {}).get("lead", "")
    parts = [
        frontmatter(d),
        "",
        f"# {name}",
        "",
        f"> {meta_desc}" if meta_desc else "",
        "",
        section_en_bref(d),
        "",
        section_presentation(d),
        "",
        section_activities(d),
        "",
        section_pratique(d),
        "",
        section_acces(d),
        "",
        section_quand(d),
        "",
        section_faq(d),
        "",
        section_sources(d),
    ]
    # Collapse empty pairs
    text = "\n".join(p for p in parts if p is not None)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--out-dir", default=str(REPO / "content"))
    args = ap.parse_args()
    d = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    md = build_md(d)
    out = Path(args.out_dir) / f"{d['slug']}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"  content/{d['slug']}.md  ({len(md):,} chars)")


if __name__ == "__main__":
    main()
