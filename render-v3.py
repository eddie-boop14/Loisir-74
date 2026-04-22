#!/usr/bin/env python3
"""
render.py v3 — Generate state-of-the-art lieu pages with:
- Category-based Unsplash hero rotation (stable per slug)
- Partner carousel with 3 tiers (partner / featured / invite)
- Gallery with user-submission placeholders + real photos when provided
- Full schema.org, OG, Twitter, hreflang

Usage:
    python3 render-v3.py <input.json> [--template template.html]
                        [--output out.html] [--lang fr]
"""

import json
import sys
import argparse
import re
import hashlib
from pathlib import Path
from html import escape

# ─────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────

SITE_NAME = "Loisirs 74"
SITE_DOMAIN = "loisirs74.fr"
SITE_TAGLINE = "Guide indépendant des lieux de loisirs publics en Haute-Savoie"
LANGS = ["fr", "en", "de", "it"]
LOCALE_MAP = {"fr": "fr_FR", "en": "en_GB", "de": "de_DE", "it": "it_IT"}
LANG_NAMES = {"fr": "Français", "en": "English", "de": "Deutsch", "it": "Italiano"}

# Category-based hero photos — 5 Unsplash URLs per category.
# Stable pick by slug hash so same slug always gets same hero.
# All chosen for consistent aesthetic: soft, nature-focused, no people, moody.
CATEGORY_HEROES = {
    "parc": [
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600&q=80",  # forest trees
        "https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?w=1600&q=80",  # green canopy
        "https://images.unsplash.com/photo-1476231682828-37e571bc172f?w=1600&q=80",  # golden park
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1600&q=80",  # forest path
        "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1600&q=80",  # sunbeam forest
    ],
    "lac": [
        "https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=1600&q=80",  # mountain lake
        "https://images.unsplash.com/photo-1439853949127-fa647821eba0?w=1600&q=80",  # calm lake
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1600&q=80",  # alpine lake
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600&q=80",  # misty lake
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1600&q=80",  # still lake
    ],
    "cascade": [
        "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=1600&q=80",  # waterfall close
        "https://images.unsplash.com/photo-1508182314998-3bd49473002f?w=1600&q=80",  # cascade silk
        "https://images.unsplash.com/photo-1467932577107-3ec6f2ffaac2?w=1600&q=80",  # falls moss
        "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=1600&q=80",  # water flow
        "https://images.unsplash.com/photo-1504827867406-7d23d1ccb98e?w=1600&q=80",  # rapids
    ],
    "voie-verte": [
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600&q=80",  # tree-lined path
        "https://images.unsplash.com/photo-1536257104079-aa99c6460a5a?w=1600&q=80",  # bike path
        "https://images.unsplash.com/photo-1558981852-426c6c22a060?w=1600&q=80",  # greenway
        "https://images.unsplash.com/photo-1528184039930-bd03972bd974?w=1600&q=80",  # forest road
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600&q=80",  # country path
    ],
    "pumptrack": [
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1600&q=80",  # bmx track
        "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1600&q=80",  # cycle abstract
        "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=1600&q=80",  # mountain bike
        "https://images.unsplash.com/photo-1520114878144-6123749968dd?w=1600&q=80",  # skate
        "https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=1600&q=80",  # asphalt curve
    ],
    "point-de-vue": [
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1600&q=80",  # mountain view
        "https://images.unsplash.com/photo-1464207687429-7505649dae38?w=1600&q=80",  # valley vista
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&q=80",  # peak panorama
        "https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=1600&q=80",  # ridge view
        "https://images.unsplash.com/photo-1542224566-6e85f2e6772f?w=1600&q=80",  # alpine vista
    ],
    "grotte": [
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=1600&q=80",  # cave mouth
        "https://images.unsplash.com/photo-1570303345338-e1f0eddf4946?w=1600&q=80",  # cave interior
        "https://images.unsplash.com/photo-1526614180703-827d23e7c8b2?w=1600&q=80",  # rock formation
        "https://images.unsplash.com/photo-1516132006923-6cf348e5dee2?w=1600&q=80",  # underground
        "https://images.unsplash.com/photo-1551981802-ce82a6b0b0fe?w=1600&q=80",  # cavern light
    ],
    "sentier": [
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600&q=80",  # forest path
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&q=80",  # mountain trail
        "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=1600&q=80",  # hiking
        "https://images.unsplash.com/photo-1551632811-561732d1e306?w=1600&q=80",  # alpine path
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1600&q=80",  # scenic trail
    ],
}


def pick_hero(slug, category):
    """Stable pick by slug hash — same slug always gets same hero."""
    photos = CATEGORY_HEROES.get(category, CATEGORY_HEROES["parc"])
    idx = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(photos)
    return photos[idx]


# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────

def e(s):
    return escape(str(s)) if s is not None else ""


def url_for(lang, slug):
    return f"https://{SITE_DOMAIN}/{slug}" if lang == "fr" else f"https://{SITE_DOMAIN}/{lang}/{slug}"


def italicize_last_word(name):
    parts = name.split(" ")
    if len(parts) > 1:
        return " ".join(parts[:-1]) + f" <em>{e(parts[-1])}</em>"
    return f"<em>{e(name)}</em>"


# ─────────────────────────────────────────────────────────────────────
# SCHEMA.ORG
# ─────────────────────────────────────────────────────────────────────

def build_schema(d, lang, canonical_url, hero_url):
    faqs = [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in d.get("faq", [])]
    amenities = [{"@type": "LocationFeatureSpecification", "name": a, "value": True}
                 for a in d.get("schema_org", {}).get("amenities", [])]
    place_id = f"{canonical_url}#place"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"https://{SITE_DOMAIN}/#website",
                "url": f"https://{SITE_DOMAIN}/",
                "name": SITE_NAME,
                "description": SITE_TAGLINE,
                "publisher": {"@id": f"https://{SITE_DOMAIN}/#publisher"},
                "inLanguage": LOCALE_MAP[lang].replace("_", "-"),
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": {"@type": "EntryPoint", "urlTemplate": f"https://{SITE_DOMAIN}/?q={{search_term_string}}"},
                    "query-input": "required name=search_term_string",
                },
            },
            {
                "@type": "Organization",
                "@id": f"https://{SITE_DOMAIN}/#publisher",
                "name": SITE_NAME,
                "url": f"https://{SITE_DOMAIN}/",
                "logo": {"@type": "ImageObject", "url": f"https://{SITE_DOMAIN}/logo.png", "width": 512, "height": 512},
                "sameAs": [],
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"https://{SITE_DOMAIN}/"},
                    {"@type": "ListItem", "position": 2, "name": d["commune"],
                     "item": f"https://{SITE_DOMAIN}/{d['commune'].lower().replace(' ', '-')}"},
                    {"@type": "ListItem", "position": 3, "name": d["name"]},
                ],
            },
            {
                "@type": "Article",
                "@id": f"{canonical_url}#article",
                "isPartOf": {"@id": f"https://{SITE_DOMAIN}/#website"},
                "author": {"@id": f"https://{SITE_DOMAIN}/#publisher"},
                "publisher": {"@id": f"https://{SITE_DOMAIN}/#publisher"},
                "headline": d["meta_title"],
                "datePublished": d.get("date_published", "2026-04-15T10:00:00+02:00"),
                "dateModified": d.get("date_modified", "2026-04-21T10:00:00+02:00"),
                "image": [hero_url],
                "inLanguage": LOCALE_MAP[lang].replace("_", "-"),
                "mainEntityOfPage": canonical_url,
            },
            {
                "@type": d.get("schema_org", {}).get("type", "TouristAttraction"),
                "@id": place_id,
                "name": d["name"],
                "alternateName": d.get("name_alternates", []),
                "description": d["hero"]["lead"],
                "url": canonical_url,
                "image": hero_url,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": d.get("address_street", ""),
                    "addressLocality": d["commune"],
                    "postalCode": d.get("postal_code", ""),
                    "addressRegion": d.get("department", "Haute-Savoie"),
                    "addressCountry": "FR",
                },
                "geo": {"@type": "GeoCoordinates", "latitude": d.get("latitude"), "longitude": d.get("longitude")},
                "isAccessibleForFree": d.get("schema_org", {}).get("is_free", True),
                "publicAccess": d.get("schema_org", {}).get("public_access", True),
                "amenityFeature": amenities,
                "openingHoursSpecification": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "opens": "00:00", "closes": "23:59",
                },
            },
            {"@type": "FAQPage", "@id": f"{canonical_url}#faq", "mainEntity": faqs},
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────────────
# RENDER PARTS
# ─────────────────────────────────────────────────────────────────────

def render_facts(facts):
    rows = [("Type", facts.get("type")), ("Accès", facts.get("access")), ("Commune", facts.get("commune")),
            ("Difficulté", facts.get("difficulty")), ("Durée", facts.get("duration")),
            ("Parking", facts.get("parking")), ("Chiens", facts.get("dogs")),
            ("Poussette", facts.get("stroller")), ("Meilleure saison", facts.get("best_season"))]
    out = []
    for k, v in rows:
        if not v: continue
        free = " free" if re.search(r"(libre|gratuit)", v, re.I) else ""
        out.append(f'<div class="fact"><span class="fact-key">{e(k)}</span><span class="fact-val{free}">{e(v)}</span></div>')
    return "\n    ".join(out)


def render_activities(acts):
    out = []
    for a in acts or []:
        tag = f'<span class="activity-tag">{e(a["tag"])}</span>' if a.get("tag") else ""
        out.append(f'  <div class="activity"><div class="activity-head"><h4>{e(a["title"])}</h4>{tag}</div><p>{e(a["description"])}</p></div>')
    return "\n".join(out)


def render_info_table(rows):
    out = []
    for r in rows or []:
        if r.get("v") is None: continue
        out.append(f'  <div class="info-row"><div class="k">{e(r["k"])}</div><div class="v">{e(r["v"])}</div></div>')
    return "\n".join(out)


def render_how(how):
    out = []
    labels = {"car": "En voiture", "public_transport": "En transports en commun", "bike": "À vélo"}
    for key, label in labels.items():
        if how.get(key):
            out.append(f"<h3>{e(label)}</h3>\n<p>{e(how[key])}</p>")
    return "\n\n".join(out)


def render_partners(d):
    """Render the partners carousel. Expects d['partners'] = list of {tier, name, description, url, cta_text, invite_icon, invite_type}."""
    partners = d.get("partners", [])
    if not partners:
        # default empty state — just invite cards
        partners = [
            {"tier": "invite", "invite_icon": "🍽️", "invite_type": "restaurant",
             "invite_title": "Un restaurant, un bar ?",
             "invite_desc": f"Vous êtes à {d['commune']} ou à proximité ? Apparaissez ici auprès des visiteurs."},
            {"tier": "invite", "invite_icon": "🥐", "invite_type": "commerce",
             "invite_title": "Une boulangerie, un commerce ?",
             "invite_desc": "Partagez vos horaires et spécialités avec les visiteurs du lieu."},
            {"tier": "invite", "invite_icon": "🏡", "invite_type": "hebergement",
             "invite_title": "Un hébergement proche ?",
             "invite_desc": "Gîte, chambre d'hôtes, camping, location. Partagez vos disponibilités."},
        ]

    html = []
    for p in partners:
        tier = p.get("tier", "invite")
        if tier == "partner":
            html.append(f"""    <article class="partner-card tier-partner">
      <span class="partner-badge"><svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>Partenaire</span>
      <h4>{e(p["name"])}</h4>
      <p>{e(p["description"])}</p>
      <a href="{e(p["url"])}" class="cta" target="_blank" rel="noopener">{e(p.get("cta_text", "Voir le site →"))}</a>
    </article>""")
        elif tier == "featured":
            html.append(f"""    <article class="partner-card tier-featured">
      <span class="partner-badge">Mis en avant</span>
      <h4>{e(p["name"])}</h4>
      <p>{e(p["description"])}</p>
      <a href="{e(p["url"])}" class="cta" target="_blank" rel="noopener">{e(p.get("cta_text", "Voir le site →"))}</a>
      <div class="partner-sponsor-tag">Contenu sponsorisé</div>
    </article>""")
        else:  # invite
            invite_type = p.get("invite_type", "partenaire")
            html.append(f"""    <article class="partner-card tier-invite">
      <div class="partner-invite-icon" aria-hidden="true">{e(p.get("invite_icon", "📍"))}</div>
      <div class="partner-invite-title">{e(p.get("invite_title", "Devenez partenaire"))}</div>
      <div class="partner-invite-desc">{e(p.get("invite_desc", "Faites connaître votre établissement auprès des visiteurs."))}</div>
      <a href="/devenir-partenaire?lieu={e(d['slug'])}&type={e(invite_type)}" class="partner-invite-cta">Devenir partenaire →</a>
    </article>""")
    return "\n\n".join(html)


def render_gallery(d):
    """Render 6 tiles: real photos where provided, placeholders otherwise, + invite card below."""
    photos = d.get("gallery_photos", [])
    placeholder_svg = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/></svg>'

    tiles = []
    for slot in range(1, 7):
        if slot <= len(photos) and photos[slot-1].get("src"):
            photo = photos[slot-1]
            credit = photo.get("credit")
            credit_html = f'<div class="gallery-credit">📷 {e(credit)}</div>' if credit else ""
            tiles.append(f"""    <div class="gallery-tile has-photo" data-slot="{slot}">
      <img src="{e(photo["src"])}" alt="{e(photo.get("alt", ""))}" loading="lazy" width="600" height="600">
      {credit_html}
    </div>""")
        else:
            tiles.append(f"""    <div class="gallery-tile placeholder" data-slot="{slot}">
      {placeholder_svg}
    </div>""")

    return f"""<div class="gallery-wrap reveal">
  <div class="gallery">
{chr(10).join(tiles)}
  </div>
  <div class="gallery-invite">
    <div class="gallery-invite-icon" aria-hidden="true">📸</div>
    <div class="gallery-invite-body">
      <strong>Vous avez visité {e(d["name"])}&nbsp;?</strong>
      <p>Partagez vos photos&nbsp;: tag <code>#loisirs74</code> sur Instagram ou envoyez-les à <a href="mailto:photos@loisirs74.fr?subject=Photos%20—%20{e(d['name'])}">photos@loisirs74.fr</a>. Nous sélectionnons les meilleures et les créditons à votre nom.</p>
    </div>
  </div>
</div>"""


def render_faq(faqs):
    return "\n".join(
        f'<details class="faq-item"><summary>{e(q["q"])}</summary><div>{e(q["a"])}</div></details>'
        for q in faqs or []
    )


def render_sources(srcs):
    out = ['<div class="sources reveal">', "<strong>Sources &amp; crédibilité</strong>", "<ul>"]
    for s in srcs or []:
        out.append(f'  <li>{e(s["name"])} — <a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["url"])}</a></li>')
    out.extend(["</ul>", "<p style=\"margin-top:0.85rem;font-size:0.78rem;color:var(--muted);\">Vérifications multi-sources à la date de publication. Les informations peuvent évoluer — pensez à confirmer auprès du gestionnaire officiel avant un déplacement spécifique.</p>", "</div>"])
    return "\n".join(out)


def render_crumb(d, lang):
    commune_slug = d["commune"].lower().replace(" ", "-")
    base = "" if lang == "fr" else f"/{lang}"
    return (f'<nav class="crumb" aria-label="Fil d\'Ariane">\n'
            f'  <a href="{base}/">Accueil</a><span class="sep">›</span>\n'
            f'  <a href="{base}/{commune_slug}">{e(d["commune"])}</a><span class="sep">›</span>\n'
            f'  <span aria-current="page">{e(d["name"])}</span>\n'
            f"</nav>")


def render_lang_switch_desktop(slug, active):
    return "\n".join(
        f'        <a href="{url_for(l, slug)}"{" aria-current=\"true\"" if l == active else ""} hreflang="{l}">{l.upper()}</a>'
        for l in LANGS
    )


def render_lang_switch_mobile(slug, active):
    return "\n".join(
        f'    <a href="{url_for(l, slug)}"{" aria-current=\"true\"" if l == active else ""} hreflang="{l}">{e(LANG_NAMES[l])}</a>'
        for l in LANGS
    )


def render_hreflangs(slug):
    out = [f'<link rel="alternate" hreflang="{l}" href="{url_for(l, slug)}">' for l in LANGS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{url_for("fr", slug)}">')
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────
# ASSEMBLY
# ─────────────────────────────────────────────────────────────────────

def build_page(d, template_path, lang="fr"):
    tpl = Path(template_path).read_text(encoding="utf-8")
    canonical = url_for(lang, d["slug"])

    # Pick hero — real photo if provided in d['hero_image'], else category placeholder
    if d.get("hero_image"):
        hero_url = d["hero_image"] if d["hero_image"].startswith("http") else f"https://{SITE_DOMAIN}/{d['hero_image']}"
        hero_src_local = d["hero_image"]
    else:
        hero_url = pick_hero(d["slug"], d.get("category", "parc"))
        hero_src_local = hero_url

    hero_alt = d.get("hero_alt") or f"Photo d'illustration — {d['name']}"

    # HEAD
    tpl = re.sub(r'<html lang="\w+"', f'<html lang="{lang}"', tpl, count=1)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{e(d['meta_title'])}</title>", tpl, count=1, flags=re.S)
    tpl = re.sub(r'<meta name="description" content=".*?">',
                 f'<meta name="description" content="{e(d["meta_description"])}">', tpl, count=1)
    tpl = re.sub(r'<link rel="canonical" href=".*?">',
                 f'<link rel="canonical" href="{canonical}">', tpl, count=1)
    tpl = re.sub(r'<link rel="alternate" hreflang="fr".*?<link rel="alternate" hreflang="x-default" href=".*?">',
                 render_hreflangs(d["slug"]), tpl, count=1, flags=re.S)

    og = f"""<meta property="og:type" content="article">
<meta property="og:title" content="{e(d['meta_title'].split(' · ')[0])}">
<meta property="og:description" content="{e(d['meta_description'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="{LOCALE_MAP[lang]}">
<meta property="og:locale:alternate" content="en_GB">
<meta property="og:locale:alternate" content="de_DE">
<meta property="og:locale:alternate" content="it_IT">
<meta property="og:image" content="{hero_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(hero_alt)}">
<meta property="article:published_time" content="{d.get('date_published', '2026-04-15T10:00:00+02:00')}">
<meta property="article:modified_time" content="{d.get('date_modified', '2026-04-21T10:00:00+02:00')}">
<meta property="article:author" content="{SITE_NAME}">
<meta property="article:section" content="Haute-Savoie">
<meta property="article:tag" content="{e(d['name'])}">
<meta property="article:tag" content="{e(d['commune'])}">
<meta property="article:tag" content="Loisirs Haute-Savoie">"""
    tpl = re.sub(r'<meta property="og:type".*?<meta property="article:tag" content="Loisirs Haute-Savoie">',
                 og, tpl, count=1, flags=re.S)

    tw = f"""<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(d['meta_title'].split(' · ')[0])}">
<meta name="twitter:description" content="{e(d['meta_description'])}">
<meta name="twitter:image" content="{hero_url}">
<meta name="twitter:image:alt" content="{e(hero_alt)}">"""
    tpl = re.sub(r'<meta name="twitter:card".*?<meta name="twitter:image:alt" content=".*?">',
                 tw, tpl, count=1, flags=re.S)

    if d.get("latitude") and d.get("longitude"):
        lat, lon = d["latitude"], d["longitude"]
        geo = f"""<meta name="geo.region" content="FR-74">
<meta name="geo.placename" content="{e(d['commune'])}">
<meta name="geo.position" content="{lat};{lon}">
<meta name="ICBM" content="{lat}, {lon}">"""
        tpl = re.sub(r'<meta name="geo.region".*?<meta name="ICBM" content=".*?">',
                     geo, tpl, count=1, flags=re.S)

    tpl = re.sub(r'<link rel="preload" as="image" href=".*?" fetchpriority="high">',
                 f'<link rel="preload" as="image" href="{hero_src_local}" fetchpriority="high">', tpl, count=1)

    tpl = re.sub(r'<script type="application/ld\+json">.*?</script>',
                 f'<script type="application/ld+json">\n{build_schema(d, lang, canonical, hero_url)}\n</script>',
                 tpl, count=1, flags=re.S)

    # HEADER lang switchers
    tpl = re.sub(
        r'(<div class="lang-switch"[^>]*>)(.*?)(</div>)',
        lambda m: m.group(1) + "\n" + render_lang_switch_desktop(d["slug"], lang) + "\n      " + m.group(3),
        tpl, count=1, flags=re.S,
    )
    tpl = re.sub(
        r'(<div class="mobile-lang">)(.*?)(</div>)',
        lambda m: m.group(1) + "\n" + render_lang_switch_mobile(d["slug"], lang) + "\n  " + m.group(3),
        tpl, count=1, flags=re.S,
    )

    # BREADCRUMB
    tpl = re.sub(r'<nav class="crumb".*?</nav>', render_crumb(d, lang), tpl, count=1, flags=re.S)

    # HERO
    hero_html = f"""<header class="hero">
  <div class="hero-img">
    <div class="hero-badge">{e(d["hero"]["badge"])}</div>
    <img src="{e(hero_src_local)}" alt="{e(hero_alt)}" width="1600" height="900" fetchpriority="high">
  </div>
  <h1 class="hero-title">{italicize_last_word(d["name"])}</h1>
  <p class="hero-lead">{e(d["hero"]["lead"])}</p>
</header>"""
    tpl = re.sub(r'<header class="hero">.*?</header>', hero_html, tpl, count=1, flags=re.S)

    # FACTS
    tpl = re.sub(
        r'<section class="facts reveal"[^>]*>.*?</section>',
        f'<section class="facts reveal" aria-label="En un coup d\'œil">\n'
        f'  <div class="facts-grid">\n    {render_facts(d["facts"])}\n  </div>\n</section>',
        tpl, count=1, flags=re.S,
    )

    # ARTICLE BODY
    body = d["body"]
    article_html = f"""<article class="body">

<h2 id="quest-ce-que">Qu'est-ce que {e(d["name"])} ?</h2>
{body["what_is"]}

<h2 id="activites" class="reveal">Ce qu'on peut y faire</h2>
<div class="activities reveal">
{render_activities(body.get("activities", []))}
</div>

<h2 id="infos-pratiques" class="reveal">Infos pratiques</h2>
<div class="info-table reveal">
{render_info_table(body.get("practical_info", []))}
</div>

<h2 id="acces" class="reveal">Comment y aller</h2>
{render_how(body.get("how_to_get_there", {}))}

<h2 id="quand-venir" class="reveal">Quand venir ?</h2>
{body.get("when_to_visit", "")}

{'<p>' + e(body["events"]) + '</p>' if body.get("events") else ""}

<h2 id="ou-manger" class="reveal">Où manger, boire, dormir à proximité</h2>

<div class="partners-wrap reveal" aria-label="Adresses partenaires et recommandées">
  <div class="partners-head">
    <span class="partners-hint">← Faites défiler pour découvrir →</span>
    <div class="partners-ctrls" role="group" aria-label="Contrôles du carrousel">
      <button type="button" class="partners-prev" aria-label="Précédent"><svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg></button>
      <button type="button" class="partners-next" aria-label="Suivant"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>
    </div>
  </div>
  <div class="partners" id="partners-scroll">

{render_partners(d)}

  </div>
</div>

<h2 id="photos" class="reveal">Photos de {e(d["name"])}</h2>
{render_gallery(d)}

<h2 id="faq" class="reveal">Questions fréquentes</h2>
{render_faq(d.get("faq", []))}

{render_sources(d.get("sources", []))}

<div class="meta">
  Publié le {d.get("date_published_human", "15 avril 2026")} <span class="sep">·</span> 
  Dernière mise à jour le {d.get("date_modified_human", "21 avril 2026")} <span class="sep">·</span> 
  <a href="/contact?subject=Signaler%20une%20erreur%20—%20{e(d['name'])}">Signaler une info obsolète</a>
</div>

</article>"""

    tpl = re.sub(r'<article class="body">.*?</article>\s*(?=<!-- TOC -->)', article_html + "\n\n", tpl, count=1, flags=re.S)
    return tpl


# ─────────────────────────────────────────────────────────────────────
# VALIDATE + MAIN
# ─────────────────────────────────────────────────────────────────────

REQUIRED = ["slug", "name", "commune", "category", "meta_title", "meta_description",
            "hero", "facts", "body", "faq", "sources"]


def validate(d):
    missing = [f for f in REQUIRED if f not in d]
    if missing: raise ValueError(f"Missing: {missing}")
    if len(d["meta_title"]) > 70: print(f"⚠ meta_title long ({len(d['meta_title'])} chars)", file=sys.stderr)
    if len(d["meta_description"]) > 160: print(f"⚠ meta_description long ({len(d['meta_description'])} chars)", file=sys.stderr)
    if len(d.get("sources", [])) < 3: print(f"⚠ {len(d.get('sources',[]))} sources (min 3)", file=sys.stderr)
    if d.get("sparse_data"): print("⚠ sparse_data=true", file=sys.stderr)
    for f in d.get("verify_flags", []): print(f"⚠ Verify: {f}", file=sys.stderr)
    if d.get("category") not in CATEGORY_HEROES:
        print(f"⚠ Unknown category '{d.get('category')}' — falling back to 'parc' hero", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json")
    ap.add_argument("--template", default="loisirs74-template-v3.html")
    ap.add_argument("--output", default=None)
    ap.add_argument("--lang", default="fr", choices=LANGS)
    args = ap.parse_args()
    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    validate(data)
    out = args.output or f"{data['slug']}.html"
    Path(out).write_text(build_page(data, args.template, lang=args.lang), encoding="utf-8")
    print(f"✓ Wrote {out}")


if __name__ == "__main__":
    main()

