#!/usr/bin/env python3
"""Generate a FR lieu HTML page from a batch JSON.

Usage:
    python3 scripts/build_lieu_page.py <batch.json> [<out_dir>]

Reads JSON shape produced by batch_activites / batch_plages
(i18n.fr.{name, meta_title, meta_description, hero, hero_alt, facts,
body, activities, practical_info, how_to_get_there, when_to_visit,
events, faq, schema_amenities}).

Produces a single-file HTML page at <out_dir>/<slug>.html using the
existing les-aigles-du-leman.html CSS+JS boilerplate verbatim.
"""
import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "les-aigles-du-leman.html"
BASE_URL = "https://loisirs74.fr"


def esc(s):
    """HTML-escape, treating None as empty."""
    if s is None:
        return ""
    return html_lib.escape(str(s), quote=False)


def attr(s):
    """HTML-escape for attribute values."""
    if s is None:
        return ""
    return html_lib.escape(str(s), quote=True)


def url_q(s):
    """URL-encode for query string."""
    return quote(str(s), safe="")


def extract_static_blocks():
    """Pull CSS <style> block and trailing <script> from the template."""
    tpl = TEMPLATE.read_text(encoding="utf-8")
    style_match = re.search(r"<style>(.*?)</style>", tpl, re.DOTALL)
    css = style_match.group(1) if style_match else ""
    # Trailing script (right before </body> equivalents — pages end with </script>)
    script_match = re.search(r"<script>\(\(\)=>\{.*?</script>", tpl, re.DOTALL)
    js = script_match.group(0) if script_match else "<script></script>"
    return css, js


CSS, JS = extract_static_blocks()


# Map JSON fact keys → French labels for the facts grid
FACT_LABELS = {
    "type": "Type",
    "access": "Accès",
    "tarif": "Tarif",
    "commune": "Commune",
    "parking": "Parking",
    "dogs": "Animaux",
    "stroller": "Poussette / PMR",
    "duration": "Durée",
    "best_season": "Meilleure saison",
    "lac": "Lac",
    "surveillance": "Surveillance",
    "pavillon_bleu_2026": "Pavillon Bleu 2026",
}
FACT_ORDER = [
    "type", "access", "tarif", "lac", "surveillance",
    "pavillon_bleu_2026", "duration", "best_season",
    "parking", "dogs", "stroller", "commune",
]


def hammer_h1(name):
    """Wrap name as hammer-animated h1 with the last word italicised."""
    parts = name.split()
    if not parts:
        return f'<h1 class="hammer">{esc(name)}</h1>'
    spans = []
    for i, w in enumerate(parts):
        if i == len(parts) - 1 and len(parts) > 1:
            spans.append(f'<span class="w"><em>{esc(w)}</em></span>')
        else:
            spans.append(f'<span class="w">{esc(w)}</span>')
    return f'<h1 class="hammer">{" ".join(spans)}</h1>'


def facts_block(facts):
    """Render the 'En un coup d'œil' grid."""
    items = []
    seen = set()
    for k in FACT_ORDER:
        if k in facts and facts[k]:
            v = facts[k]
            ok_class = ""
            # Mark positive parking/free as ok
            if k == "parking" and re.search(r"gratuit", v, re.I):
                ok_class = " ok"
            elif k == "access" and re.search(r"libre|gratuit", v, re.I):
                ok_class = " ok"
            items.append(
                f'<div class="fact"><div class="k">{esc(FACT_LABELS[k])}</div>'
                f'<div class="v{ok_class}">{esc(v)}</div></div>'
            )
            seen.add(k)
    # Catch any extra fact keys not in FACT_ORDER
    for k, v in facts.items():
        if k in seen or not v:
            continue
        label = FACT_LABELS.get(k, k.replace("_", " ").capitalize())
        items.append(
            f'<div class="fact"><div class="k">{esc(label)}</div>'
            f'<div class="v">{esc(v)}</div></div>'
        )
    return (
        '<section class="block"><div class="wrap"><div class="kicker reveal">'
        "En un coup d&#39;œil</div>"
        f'<div class="facts reveal" data-stagger>{"".join(items)}</div></div></section>'
    )


def body_block(name, body):
    """Render the 'Qu'est-ce que <name>' section. body is dict with 'what_is' HTML."""
    what_is = body.get("what_is", "") if isinstance(body, dict) else str(body)
    return (
        '<section class="block"><div class="wrap">'
        f'<h2 class="reveal">Qu&#39;est-ce que {esc(name)}</h2>'
        f'<div class="reveal">{what_is}</div></div></section>'
    )


FLIP_HINT = (
    '<span class="hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>'
    '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
    "</svg> Toucher pour lire</span>"
)


def activities_block(activities):
    """Render flip-card grid."""
    if not activities:
        return ""
    cards = []
    for a in activities:
        title = a.get("title", "")
        tag = a.get("tag", "")
        desc = a.get("description", "")
        tag_html = f'<span class="activity-tag">{esc(tag)}</span>' if tag else ""
        cards.append(
            f'<button type="button" class="activity flip" aria-label="{attr(title)}">'
            f'<div class="flip-inner">'
            f'<div class="flip-front">'
            f'<h4>{esc(title)}{tag_html}</h4>'
            f'<p class="preview">{esc(desc)}</p>'
            f'{FLIP_HINT}'
            f'</div>'
            f'<div class="flip-back"><h4>{esc(title)}</h4><p>{esc(desc)}</p></div>'
            f'</div></button>'
        )
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Activités</div>'
        '<h2 class="reveal">Ce qu&#39;on peut y faire</h2>'
        f'<div class="activities reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def practical_block(practical, name, commune):
    """Render the 'Infos pratiques' info-table."""
    if not practical:
        return ""
    rows = []
    for entry in practical:
        k = entry.get("k", "")
        v = entry.get("v", "")
        # If the row is Adresse, append a 'voir sur la carte' link
        extra = ""
        if k.lower().startswith("adresse"):
            q = url_q(f"{name}, {commune}, Haute-Savoie, France")
            extra = (
                f' <a href="https://www.google.com/maps/search/?api=1&query={q}" '
                'target="_blank" rel="noopener" class="inline-link">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
                '<circle cx="12" cy="10" r="3"/></svg>Voir sur la carte</a>'
            )
        rows.append(
            f'<div class="info-row"><div class="k">{esc(k)}</div>'
            f'<div class="v"><span>{esc(v)}{extra}</span></div></div>'
        )
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Pratique</div>'
        '<h2 class="reveal">Infos pratiques</h2>'
        f'<div class="info-table reveal">{"".join(rows)}</div></div></section>'
    )


HOW_ICONS = {
    "car": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 17h14M5 17V11l2-6h10l2 6v6M5 17H3M19 17h2M7 17v2h2v-2M15 17v2h2v-2"/>'
        '<circle cx="7" cy="14" r="1"/><circle cx="17" cy="14" r="1"/></svg>'
    ),
    "public_transport": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="4" y="3" width="16" height="14" rx="2"/>'
        '<path d="M4 11h16M8 17v2M16 17v2"/><circle cx="8" cy="14" r="1"/>'
        '<circle cx="16" cy="14" r="1"/></svg>'
    ),
    "bike": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/>'
        '<path d="M6 17l4-9h4l3 9M14 8l-2-4h-2"/></svg>'
    ),
}
HOW_LABELS = {
    "car": ("En voiture", "driving"),
    "public_transport": ("Transports en commun", "transit"),
    "bike": ("À vélo", "bicycling"),
}


def how_to_block(how, name, commune):
    """Render the 'Comment y aller' how-cards."""
    if not how:
        return ""
    q = url_q(f"{name}, {commune}, Haute-Savoie")
    cards = []
    for key in ("car", "public_transport", "bike"):
        text = how.get(key)
        if not text:
            continue
        label, travelmode = HOW_LABELS[key]
        icon = HOW_ICONS[key]
        cards.append(
            f'<a class="how-card" href="https://www.google.com/maps/dir/?api=1'
            f"&destination={q}&travelmode={travelmode}" + '" '
            f'target="_blank" rel="noopener">'
            f'<div class="icon">{icon}</div>'
            f'<h3>{esc(label)}</h3>'
            f'<p>{esc(text)}</p>'
            f'<span class="open">Ouvrir dans Maps '
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'
            '</svg></span></a>'
        )
    if not cards:
        return ""
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Accès</div>'
        '<h2 class="reveal">Comment y aller</h2>'
        f'<div class="how reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def when_to_visit_block(when, events):
    """Render 'Quand visiter' + optional events."""
    if not when and not events:
        return ""
    inner = ""
    if when:
        inner += f'<div class="reveal">{esc(when)}</div>'
    if events:
        inner += (
            '<div class="reveal" style="margin-top:1.25rem">'
            f'<strong>Événements&nbsp;:</strong> {esc(events)}</div>'
        )
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Quand venir</div>'
        '<h2 class="reveal">Quand visiter</h2>'
        f"{inner}</div></section>"
    )


def faq_block(faq):
    if not faq:
        return ""
    items = []
    for entry in faq:
        q = entry.get("q", "")
        a = entry.get("a", "")
        items.append(
            f"<details class=\"faq\"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        )
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">FAQ</div>'
        '<h2 class="reveal">Questions fréquentes</h2>'
        f'<div class="faq-grid reveal" data-stagger>{"".join(items)}</div>'
        '</div></section>'
    )


LINK_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
)


def sources_block(sources):
    if not sources:
        return ""
    items = []
    for src in sources:
        if isinstance(src, dict):
            url = src.get("url", "")
            label = src.get("name") or re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        else:
            url = src
            label = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        items.append(
            f'<li>{LINK_ICON}<a href="{attr(url)}" target="_blank" rel="noopener">'
            f"{esc(label)}</a></li>"
        )
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Sources</div>'
        '<h2 class="reveal">Sources &amp; vérifications</h2>'
        f'<div class="sources reveal"><ul>{"".join(items)}</ul>'
        '<p class="caveat">Vérifications multi-sources à la date de publication. '
        "Les informations peuvent évoluer — confirmez auprès du gestionnaire "
        "officiel avant un déplacement.</p></div></div></section>"
    )


PARTNER_TYPE_ICON = {
    "restaurant": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h2c1.1 0 2-.9 2-2V2M5 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
    "commerce":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
    "hebergement":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
}
SVG_ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round">'
             '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>')
SVG_EXT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
           '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>')
SVG_ROTATE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round">'
              '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>'
              '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>')
SVG_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
             'stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>')

def _filled_partner_card(p):
    """Render a tier:partner or tier:recommended partner card (flip card)."""
    tier = p.get("tier", "partner")
    badge_text = "Partenaire" if tier == "partner" else "Recommandé"
    badge_icon = SVG_CHECK if tier == "partner" else ""
    name = p.get("name", "")
    desc = p.get("i18n", {}).get("fr", {}).get("description", "")
    url = p.get("url", "#")
    cta = p.get("cta_text") or "Voir le site"
    return (
        f'<button type="button" class="partner flip tier-{attr(tier)}" aria-label="{attr(name)}">'
        '<div class="flip-inner">'
        '<div class="flip-front">'
        f'<span class="badge">{badge_icon} {esc(badge_text)}</span>'
        f'<h4>{esc(name)}</h4>'
        f'<p class="preview">{esc(desc)}</p>'
        f'<span class="hint">{SVG_ROTATE} Survoler pour voir le site</span>'
        '</div>'
        '<div class="flip-back">'
        f'<h4>{esc(name)}</h4>'
        f'<p>{esc(desc)}</p>'
        f'<a class="cta" href="{attr(url)}" target="_blank" rel="noopener">{esc(cta)} {SVG_EXT}</a>'
        '</div>'
        '</div>'
        '</button>'
    )

def _invite_card(p, slug):
    """Render a tier:invite partner card."""
    invite_type = p.get("invite_type", "restaurant")
    icon = PARTNER_TYPE_ICON.get(invite_type, PARTNER_TYPE_ICON["restaurant"])
    fr = p.get("i18n", {}).get("fr", {})
    title = fr.get("title") or p.get("invite_title", "")
    desc = fr.get("desc") or p.get("invite_desc", "")
    return (
        '<article class="partner-invite">'
        f'<div class="invite-icon" aria-hidden="true">{icon}</div>'
        f'<h4>{esc(title)}</h4><p>{esc(desc)}</p>'
        f'<a class="cta" href="https://loisirs74.fr/devenir-partenaire?lieu={attr(slug)}">'
        f'Devenir partenaire {SVG_ARROW}</a>'
        '</article>'
    )

def _default_invites(d):
    """Venue-parameterized invite tiers when JSON has no partners block."""
    name = d.get("i18n", {}).get("fr", {}).get("name", "ce lieu")
    commune = d.get("commune", "")
    here = f"à {commune}" if commune else ""
    return [
        {"tier":"invite","invite_type":"restaurant","i18n":{"fr":{
            "title": f"Un restaurant {here} ?".strip(),
            "desc": f"Vous accueillez les visiteurs de {name} ? Apparaissez ici."}}},
        {"tier":"invite","invite_type":"commerce","i18n":{"fr":{
            "title": f"Une boulangerie, un commerce {here} ?".strip(),
            "desc": f"Partagez horaires et spécialités avec les visiteurs de {name}."}}},
        {"tier":"invite","invite_type":"hebergement","i18n":{"fr":{
            "title": f"Un hébergement proche ?",
            "desc": f"Gîte, chambre d'hôtes, camping, location {here}.".strip()}}},
    ]

def partners_block(d):
    """Render the 'À proximité' section from d['partners'] or fall back to venue-parameterized invites."""
    slug = d["slug"]
    partners = d.get("partners") or _default_invites(d)
    cards = []
    for p in partners:
        tier = p.get("tier", "invite")
        if tier in ("partner", "recommended"):
            cards.append(_filled_partner_card(p))
        else:
            cards.append(_invite_card(p, slug))
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">À proximité</div>'
        '<h2 class="reveal">Où manger, boire, dormir</h2>'
        f'<div class="partners reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def gallery_block(name):
    """6 placeholder tiles + invite."""
    tile = (
        '<div class="tile placeholder"><svg viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" '
        'height="18" rx="2"/><circle cx="9" cy="9" r="2"/>'
        '<path d="M21 15l-5-5L5 21"/></svg></div>'
    )
    tiles = tile * 6
    return (
        '<section class="block"><div class="wrap">'
        '<div class="kicker reveal">Photos</div>'
        '<h2 class="reveal">Galerie</h2>'
        f'<div class="gallery reveal" data-stagger>{tiles}</div>'
        '<div class="gallery-invite reveal"><div class="icn">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
        '<circle cx="12" cy="13" r="4"/></svg></div>'
        '<p><strong>Vous y êtes allé ?</strong> Partagez vos photos — nous les '
        'ajoutons à cette page avec votre crédit. Tag #loisirs74 ou écrivez à '
        f'<a href="mailto:photos@loisirs74.fr?subject=Photos%20—%20{url_q(name)}">'
        'photos@loisirs74.fr</a></p></div></div></section>'
    )


def clean_eyebrow(badge, is_free):
    """Pick a clean eyebrow label.

    Many batch badges are truncated mid-word (e.g. "19 € croisière 1h, 22 € croisi").
    Use the batch badge only when it's a clean signal like "Pavillon Bleu 2026"
    or "Plage surveillée · Gratuit". Otherwise fall back to a generic label.
    """
    if badge:
        if "Pavillon Bleu" in badge:
            return badge
        if "Plage surveillée" in badge:
            return badge
        b = badge.strip()
        if b.upper().startswith("GRATUIT"):
            return "Gratuit · Accès libre"
        # Short, complete tariff like "15 €" or "8 € la partie" — accept.
        if len(b) <= 28 and "€" in b and not b.rstrip().endswith(("si", "i", ",", "·")):
            return ("Payant · " if not is_free else "") + b
    return "Gratuit · Accès libre" if is_free else "Payant · Réservation en ligne"


def hero_block(d):
    """Render the hero section.

    The hero image source:
      - If hero_image looks like 'generique-*.jpg', use a local generic asset
        and mark with data-generique.
      - Else, use /<hero_image> (root-level relative URL).
    """
    fr = d["i18n"]["fr"]
    name = fr["name"]
    hero = fr.get("hero", {})
    badge = hero.get("badge", "")
    lead = hero.get("lead", "")
    alt = fr.get("hero_alt", name)
    is_free = d.get("schema_org", {}).get("is_free", False)
    booking_url = d.get("booking_url") or d.get("official_site_url") or "#"
    official = d.get("official_site_url") or ""
    commune = d["commune"]
    q = url_q(f'{name}, {commune}, Haute-Savoie, France')

    GENERIC_ON_DISK = {"attraction", "cascade", "chateau", "domaine", "lac",
                       "musee", "parc", "point-de-vue", "sentier", "telecabine", "voie-verte"}
    img = d.get("hero_image") or ""
    if img.startswith("generique-"):
        img_src = f"/{img}"
        gen_cat = img[len("generique-"):].rsplit(".", 1)[0]
        gen_attr = f' data-generique="true" data-generique-cat="{gen_cat}"'
    elif img:
        img_src = f"/{img}"
        gen_attr = ""
    else:
        cat = d.get("category") or "attraction"
        eff_cat = cat if cat in GENERIC_ON_DISK else "attraction"
        img_src = f"/generique-{eff_cat}.jpg"
        gen_attr = f' data-generique="true" data-generique-cat="{eff_cat}"'

    eyebrow_text = clean_eyebrow(badge, is_free)
    cta_buttons = []
    if not is_free and booking_url and booking_url != "#":
        cta_buttons.append(
            f'<a href="{attr(booking_url)}" class="btn btn-primary" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M3 7v3a3 3 0 0 0 0 6v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a3 3 0 0 0 0-6V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/>'
            '<line x1="13" y1="5" x2="13" y2="7"/><line x1="13" y1="11" x2="13" y2="13"/>'
            '<line x1="13" y1="17" x2="13" y2="19"/></svg>Réserver</a>'
        )
    cta_buttons.append(
        f'<a href="https://www.google.com/maps/search/?api=1&query={q}" class="btn btn-ghost" '
        'target="_blank" rel="noopener">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/></svg>Voir sur la carte</a>'
    )
    if official:
        cta_buttons.append(
            f'<a href="{attr(official)}" class="btn btn-ghost" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
            '<path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>'
            '</svg>Site officiel</a>'
        )

    return (
        '<section class="hero"><div class="wrap"><div class="grid">'
        '<div>'
        f'<span class="eyebrow reveal"><span class="dot"></span>{esc(eyebrow_text)}</span>'
        f'{hammer_h1(name)}'
        f'<p class="lede reveal">{esc(lead)}</p>'
        f'<div class="cta-row reveal">{"".join(cta_buttons)}</div>'
        '</div>'
        '<div class="reveal"><div class="hero-img">'
        f'<img src="{attr(img_src)}" alt="{attr(alt)}" width="1600" height="1200" '
        f'fetchpriority="high"{gen_attr}>'
        '</div></div>'
        '</div></div></section>'
    )


def action_bar(d):
    """Sticky bottom action bar (Réserver / Itinéraire / Site officiel)."""
    fr = d["i18n"]["fr"]
    name = fr["name"]
    commune = d["commune"]
    is_free = d.get("schema_org", {}).get("is_free", False)
    booking_url = d.get("booking_url") or d.get("official_site_url")
    official = d.get("official_site_url") or ""
    q = url_q(f'{name}, {commune}, Haute-Savoie')

    actions = []
    if not is_free and booking_url:
        actions.append(
            f'<a class="primary" href="{attr(booking_url)}" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M3 7v3a3 3 0 0 0 0 6v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a3 3 0 0 0 0-6V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/>'
            '<line x1="13" y1="5" x2="13" y2="7"/><line x1="13" y1="11" x2="13" y2="13"/>'
            '<line x1="13" y1="17" x2="13" y2="19"/></svg><span>Réserver</span></a>'
        )
    actions.append(
        f'<a href="https://www.google.com/maps/dir/?api=1&destination={q}" '
        'target="_blank" rel="noopener">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/></svg><span>Itinéraire</span></a>'
    )
    if official:
        actions.append(
            f'<a href="{attr(official)}" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
            '<path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>'
            '</svg><span>Site officiel</span></a>'
        )
    return (
        '<div class="action-bar" id="actionBar"><div class="wrap">'
        + "".join(actions)
        + '</div></div>'
    )


def build_ldjson(d):
    """Build the WebSite + BreadcrumbList + (TouristAttraction|Place) + FAQPage graph."""
    fr = d["i18n"]["fr"]
    slug = d["slug"]
    name = fr["name"]
    commune = d["commune"]
    lat = d.get("latitude")
    lon = d.get("longitude")
    postal = d.get("postal_code", "")
    sch = d.get("schema_org", {})
    is_free = sch.get("is_free", False)
    place_type = sch.get("type") or ("TouristAttraction" if not is_free else "TouristAttraction")
    amenities = fr.get("schema_amenities") or sch.get("amenities") or []
    price = d.get("price_from")
    booking_url = d.get("booking_url") or d.get("official_site_url") or ""

    page_url = f"{BASE_URL}/{slug}"
    graph = [
        {
            "@type": "WebSite",
            "@id": f"{BASE_URL}/#website",
            "url": f"{BASE_URL}/",
            "name": "Loisirs 74",
            "inLanguage": "fr-FR",
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{page_url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": commune,
                 "item": f"{BASE_URL}/#{commune.lower().replace(' ', '-')}"},
                {"@type": "ListItem", "position": 3, "name": name},
            ],
        },
    ]
    place = {
        "@type": place_type,
        "@id": f"{page_url}#place",
        "name": name,
        "alternateName": fr.get("name_alternates", []),
        "description": fr.get("meta_description", ""),
        "url": page_url,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": commune,
            "postalCode": str(postal),
            "addressRegion": "Haute-Savoie",
            "addressCountry": "FR",
        },
        "isAccessibleForFree": bool(is_free),
        "publicAccess": bool(sch.get("public_access", True)),
        "image": "",
    }
    if lat is not None and lon is not None:
        place["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon}
    if amenities:
        place["amenityFeature"] = [
            {"@type": "LocationFeatureSpecification", "name": str(a), "value": True}
            for a in amenities
        ]
    if not is_free and price is not None and price > 0:
        place["offers"] = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": d.get("price_currency", "EUR"),
            "url": booking_url or page_url,
        }
    graph.append(place)

    if fr.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "@id": f"{page_url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q.get("q", ""),
                 "acceptedAnswer": {"@type": "Answer", "text": q.get("a", "")}}
                for q in fr["faq"]
            ],
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def build_head(d):
    """Render the <head> section."""
    fr = d["i18n"]["fr"]
    slug = d["slug"]
    name = fr["name"]
    title = fr.get("meta_title") or f"{name} · Loisirs 74"
    desc = fr.get("meta_description", "")
    lat = d.get("latitude") or 0
    lon = d.get("longitude") or 0
    commune = d["commune"]
    page_url = f"{BASE_URL}/{slug}"

    ldjson = build_ldjson(d)

    return f"""<!doctype html>
<html lang="fr" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0b0d10" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#fafaf7" media="(prefers-color-scheme: light)">
<title>{esc(title)}</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1c4f62">
<meta name="description" content="{attr(desc)}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="fr" href="{page_url}">
<link rel="alternate" hreflang="x-default" href="{page_url}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:type" content="article">
<meta property="og:title" content="{attr(name)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:url" content="{page_url}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Loisirs 74">
<meta property="og:image:alt" content="{attr(fr.get('hero_alt', name))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{attr(name)}">
<meta name="twitter:description" content="{attr(desc)}">
<meta name="geo.region" content="FR-74">
<meta name="geo.placename" content="{attr(commune)}">
<meta name="geo.position" content="{lat};{lon}">
<meta name="ICBM" content="{lat}, {lon}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230a5a3a'/%3E%3Cpath d='M16 44 L26 28 L34 38 L44 22 L48 44 Z' fill='%23fafaf7'/%3E%3C/svg%3E">
<style>{CSS}</style>
<script type="application/ld+json">{ldjson}</script>
<meta property="og:image" content="{BASE_URL}/og-image.jpg">
<meta name="twitter:image" content="{BASE_URL}/og-image.jpg">
<!-- AI discovery: per-lieu markdown mirror -->
<link rel="alternate" type="text/markdown" href="/content/{slug}.md" title="Markdown version">
<meta name="ai:content-url" content="{BASE_URL}/content/{slug}.md">
<meta name="ai:policy-url" content="{BASE_URL}/.well-known/ai-info.json">
</head>"""


def build_header(d):
    """Sticky site header with brand + lang picker (FR-only batch → minimal lang menu)."""
    slug = d["slug"]
    return f"""<body>
<a class="skip" href="#main">Aller au contenu</a>
<header class="site"><div class="wrap">
  <a class="brand" href="{BASE_URL}/" aria-label="Loisirs 74"><span class="mark" aria-hidden="true"><img src="/logo.png" alt="" width="30" height="30" style="border-radius:7px;display:block;"></span><span>Loisirs 74</span></a>
  <nav><details class="lang-picker"><summary aria-label="Choisir la langue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20"/></svg>FR</summary><div class="lang-menu"><a href="{BASE_URL}/{slug}" aria-current="true" hreflang="fr">Français</a></div></details></nav>
</div></header>
<main id="main">
<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="{BASE_URL}/">Accueil</a><span class="sep">/</span><span>{esc(d['commune'])}</span><span class="sep">/</span><span aria-current="page">{esc(d['i18n']['fr']['name'])}</span></nav></div>"""


def build_footer_block(date_pub, date_mod):
    return (
        '<div class="wrap"><p class="meta">'
        f'<span>Publié le {esc(date_pub)}</span><span class="sep">·</span>'
        f'<span>Mis à jour le {esc(date_mod)}</span></p></div>'
        '</main>'
    )


SITE_FOOTER = (
    '<footer class="site"><div class="wrap"><div class="foot-grid">'
    '<div class="foot-col"><a class="brand" href="https://loisirs74.fr/" style="margin-bottom:.85rem"><span class="mark" aria-hidden="true"><img src="/logo.png" alt="" width="30" height="30" style="border-radius:7px;display:block;"></span><span>Loisirs 74</span></a><p>Guide indépendant des lieux de loisirs en Haute-Savoie. 100% gratuit. 100% vérifié.</p></div>'
    '<div class="foot-col"><h4>Explorer</h4><ul><li><a href="https://loisirs74.fr/">Accueil</a></li></ul></div>'
    '<div class="foot-col"><h4>Contribuer</h4><ul><li><a href="mailto:photos@loisirs74.fr">Envoyer des photos</a></li><li><a href="https://loisirs74.fr/signaler">Signaler une info</a></li><li><a href="https://loisirs74.fr/devenir-partenaire">Devenir partenaire</a></li></ul></div>'
    '<div class="foot-col"><h4>Mentions</h4><ul><li><a href="https://loisirs74.fr/mentions-legales">Mentions légales</a></li><li><a href="https://loisirs74.fr/confidentialite">Confidentialité</a></li><li><a href="https://loisirs74.fr/cgv">CGV</a></li></ul></div>'
    '</div><div class="foot-bottom"><span class="credit">© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Tous droits réservés</span><span>Sans pub. Sans tracking. Sans avis Google.</span></div></div></footer>'
)


def build_page(d):
    fr = d["i18n"]["fr"]
    out = []
    out.append(build_head(d))
    out.append(build_header(d))
    out.append(hero_block(d))
    out.append(facts_block(fr.get("facts", {})))
    out.append(body_block(fr["name"], fr.get("body", {})))
    out.append(activities_block(fr.get("activities", [])))
    out.append(practical_block(fr.get("practical_info", []), fr["name"], d["commune"]))
    out.append(how_to_block(fr.get("how_to_get_there", {}), fr["name"], d["commune"]))
    out.append(when_to_visit_block(fr.get("when_to_visit", ""), fr.get("events", "")))
    out.append(partners_block(d))
    out.append(gallery_block(fr["name"]))
    out.append(faq_block(fr.get("faq", [])))
    out.append(sources_block(d.get("sources", [])))
    out.append(build_footer_block(
        d.get("date_published_human", ""),
        d.get("date_modified_human", "")
    ))
    out.append(action_bar(d))
    out.append(SITE_FOOTER)
    out.append(JS)
    out.append("</body></html>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--out-dir", default=str(REPO))
    args = ap.parse_args()

    d = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    html = build_page(d)
    out_path = Path(args.out_dir) / f"{d['slug']}.html"
    out_path.write_text(html, encoding="utf-8")
    try:
        rel = out_path.relative_to(REPO)
    except ValueError:
        rel = out_path
    print(f"  {rel}  ({len(html):,} chars)")


if __name__ == "__main__":
    main()
