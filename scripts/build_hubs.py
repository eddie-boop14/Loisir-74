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
    "seasonal":        {"fr": "Selon saison", "en": "Seasonal", "de": "Saisonal", "it": "Stagionale", "es": "Por temporada", "nl": "Seizoensgebonden"},
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


# ---------------------------------------------------------------------------
# Phase 4 — description-driven photo picker
# ---------------------------------------------------------------------------

# Minimal FR stopword list — purely structural words that carry no fiche
# signal. Kept short and predictable for idempotency.
_STOPWORDS_FR = {
    "de","la","le","les","du","des","et","en","un","une","à","au","aux",
    "avec","pour","sur","par","ou","est","sont","dans","plus","aussi",
    "très","que","qui","se","il","elle","ce","ces","cette","son","sa",
    "ses","si","mais","donc","car","ne","pas","au","aux","si","non","oui",
    "comme","tout","tous","toutes","toute","quelque","entre","sous","vers",
    "depuis","après","avant","être","avoir","fait","faire","peut","aussi",
    "ainsi","leur","leurs","puis","encore","déjà",
}


def _load_photo_index():
    p = ROOT / "data" / "photo-index.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _fiche_words(d):
    """Extract description keywords from a fiche's FR text fields."""
    fr = d.get("i18n", {}).get("fr", {}) or {}
    parts = [fr.get("name", "") or "",
             fr.get("meta_description", "") or "",
             fr.get("short_intro", "") or ""]
    facts = fr.get("facts", {}) or {}
    for v in facts.values():
        if v:
            parts.append(str(v))
    text = " ".join(parts).lower()
    words = re.findall(r"[a-zà-ÿ]+", text)
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS_FR}


def pick_photo(d, photo_index, used_in_hub):
    """Phase 4 picker. Returns (src, score, basename, reason).

    src         — URL or '/'-prefixed path for the <img src>
    score       — integer keyword overlap; None for real (non-generic) heros
    basename    — filename only (for data-photo and assignments report)
    reason      — short tag: "real URL hero" | "real local hero" |
                  "best unused score" | "cycling — all used"

    The rule:
      1. If the fiche has a non-generic hero (URL or /<slug>-hero.jpg),
         keep it. Real photos beat any picker output.
      2. Otherwise filter the library to photos whose primary type
         matches the fiche's type, plus the 'fallback' bucket.
      3. Score each candidate by |fiche_words ∩ photo_keywords|.
      4. Pick the highest score not already used in this hub.
      5. If every candidate is used, return the highest score (cycling).
    """
    hero = (d.get("hero_image") or "").strip()
    # Real URL hero
    if hero.startswith(("http://", "https://")):
        return (hero, None, hero.rsplit("/", 1)[-1], "real URL hero")
    # Real local hero (e.g. /<slug>-hero.jpg)
    if hero.startswith("/") and "generique-" not in hero:
        return (f"https://loisirs74.fr{hero}", None, hero.lstrip("/").rsplit("/", 1)[-1], "real local hero")

    if not photo_index:
        # No index → fall through to the legacy generique path. Caller
        # will compute img_src from d.hero_image (existing behaviour).
        return (None, None, "", "no photo-index loaded")

    fiche_type = d.get("type") or ""
    candidates = [fn for fn, meta in photo_index.items()
                  if meta.get("type") == fiche_type or meta.get("type") == "fallback"]
    if not candidates:
        candidates = list(photo_index.keys())

    words = _fiche_words(d)
    scores = {fn: len(words & set(photo_index[fn].get("keywords", []))) for fn in candidates}
    # Deterministic tie-break by filename
    ranked = sorted(candidates, key=lambda fn: (-scores[fn], fn))

    for fn in ranked:
        if fn not in used_in_hub:
            used_in_hub.add(fn)
            return (f"https://loisirs74.fr/{fn}", scores[fn], fn, "best unused score")

    # All candidates exhausted — RESET the pool and pick the best for
    # THIS fiche. Cycling this way keeps per-fiche relevance while
    # spreading repeats evenly across the hub. Cap on repeats is
    # ceil(hub_fiches / candidate_count) per the gate spec.
    used_in_hub.clear()
    best = ranked[0]
    used_in_hub.add(best)
    return (f"https://loisirs74.fr/{best}", scores[best], best, "cycling — pool reset")


def acces_value(d):
    """Return the canonical access value for `data-acces` from JSON.

    Phase 3 single source of truth: schema_org.tariff_kind + is_free.
    Returns one of 'seasonal' | 'gratuit' | 'payant' | ''. The empty
    string means the field is intentionally absent (caller can skip
    the data-acces attribute or render it empty).
    """
    so = d.get("schema_org", {}) or {}
    if so.get("tariff_kind") == "seasonal":
        return "seasonal"
    if so.get("is_free") is True:
        return "gratuit"
    if so.get("is_free") is False:
        return "payant"
    return ""


def fiche_card_html(d, lang, slug, picked_photo=None):
    """Render one card. URL = https://loisirs74.fr[/lang]/slug; title + desc from i18n.

    `picked_photo`, when provided, overrides the fiche's hero_image as
    the displayed card photo. Carries (src, score, basename, reason) from
    pick_photo() so the card emits data-photo=basename verbatim.
    """
    i18n = d.get("i18n", {}) or {}
    loc = i18n.get(lang) or {}
    fr = i18n.get("fr") or {}
    name = loc.get("name") or fr.get("name") or slug
    desc = loc.get("meta_description") or fr.get("meta_description") or ""
    desc = desc.strip()[:280]  # cap
    # tariff_kind takes precedence over is_free for the visual tag.
    # "seasonal" → "Selon saison" (mixed-access lieux: site libre · visites guidées payantes)
    # otherwise → is_free True/False → Gratuit/Payant
    so = d.get("schema_org", {}) or {}
    if so.get("tariff_kind") == "seasonal":
        tag_class = "is-seasonal"
        tag_text = CHROME["seasonal"][lang]
    else:
        is_free = bool(so.get("is_free", False))
        tag_class = "is-gratuit" if is_free else "is-payant"
        tag_text = CHROME["free" if is_free else "paid"][lang]
    commune = d.get("commune", "")

    # Hero image: picker-overridden when provided (Phase 4), otherwise
    # fall back to the fiche's hero_image (Phase 3 behaviour).
    if picked_photo is not None and picked_photo[0]:
        img_src = picked_photo[0]
    else:
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

    # Phase 3: emit data-* attributes derived from JSON. Single source of
    # truth = the fiche JSON. Empty values mean "field intentionally
    # absent" — never invented, never inferred at render time.
    # commune is lowercased per the architecture brief; the section-level
    # data-commune attribute keeps original casing for the legacy filter.
    data_commune = (commune or "").lower()
    data_acces   = acces_value(d)
    data_lac     = d.get("lake") or ""
    data_type    = d.get("type") or ""
    # data-photo: basename of the chosen card photo. Phase 4 uses the
    # picker's own basename (so URL-encoding from img_src never leaks
    # into the attribute); Phase 3 fallback derives from img_src.
    if picked_photo is not None and picked_photo[2]:
        data_photo = picked_photo[2]
    elif img_src:
        data_photo = img_src.rsplit("/", 1)[-1]
    else:
        data_photo = ""

    return (
        f'<article class="card"'
        f' data-commune="{a(data_commune)}"'
        f' data-acces="{a(data_acces)}"'
        f' data-lac="{a(data_lac)}"'
        f' data-type="{a(data_type)}"'
        f' data-photo="{a(data_photo)}">\n'
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


def build_main_block(fiches, lang, hub_name=None, photo_index=None, assignments=None):
    """Render the <main>…</main> content for a hub: commune-grouped cards.

    When `hub_name` is "lacs-plages", each commune-section also carries
    `data-lac="annecy|leman|petits"` derived from each fiche's `lake`
    field (the JSON source of truth). All fiches in a commune share the
    same lake by construction, so reading the first one is sufficient.

    Phase 4: when `photo_index` is provided, `pick_photo()` selects the
    card photo per fiche from the keyword-scored library, tracking
    `used_in_hub` to maximise diversity within the hub. `assignments`
    (optional list) captures (hub, slug, type, photo, score, reason)
    rows for the post-build report. Picks are computed once per hub
    (FR-locale-invariant) so all 6 locale variants render the same
    photo per card — same fiche, same picture across the site.
    """
    used_in_hub = set()
    picks = {}
    if photo_index:
        # Deterministic iteration order = render order (commune asc,
        # then FR name asc). Ensures byte-identical output across runs.
        ordered = sorted(
            fiches,
            key=lambda x: (
                (x[1].get("commune") or "?").lower(),
                (x[1].get("i18n", {}).get("fr", {}).get("name") or x[0]).lower(),
            ),
        )
        for slug, d in ordered:
            pick = pick_photo(d, photo_index, used_in_hub)
            picks[slug] = pick
            if assignments is not None and hub_name and lang == "fr":
                assignments.append((hub_name, slug, d.get("type") or "",
                                    pick[2], pick[1], pick[3]))

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
        # Lake attribute for lacs-plages only — derived from JSON `lake` field.
        lac_attr = ""
        if hub_name == "lacs-plages":
            first_lake = entries[0][1].get("lake")
            if first_lake:
                lac_attr = f' data-lac="{first_lake}"'
        parts.append(f'<div class="commune-section" data-commune="{commune}"{lac_attr}>')
        parts.append(f'<div class="commune-head"><h3>{commune}</h3>'
                     f'<span class="commune-count">{n} {word}</span></div>')
        parts.append('<div class="carousel">')
        for slug, d in entries:
            parts.append(fiche_card_html(d, lang, slug, picked_photo=picks.get(slug)))
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


# Localized label for the empty-value default option of filt-commune.
TOUTES_LES_COMMUNES = {
    "fr": "Toutes les communes", "en": "All towns", "de": "Alle Gemeinden",
    "it": "Tutti i comuni", "es": "Todos los municipios", "nl": "Alle gemeenten",
}


def patch_filt_commune(html, communes, lang):
    """Replace the <select id="filt-commune"> options with exactly the
    communes present in the rendered card set (sorted alphabetically).
    Eliminates ghost commune options structurally.

    Preserves the first "all communes" option with its locale label.
    """
    sel_re = re.compile(r'(<select id="filt-commune">)(.*?)(</select>)', re.DOTALL)
    m = sel_re.search(html)
    if not m:
        return html
    default_label = TOUTES_LES_COMMUNES.get(lang, TOUTES_LES_COMMUNES["fr"])
    opts = [f'<option value="">{default_label}</option>']
    for c in sorted(communes, key=lambda c: (c.lower(), c)):
        opts.append(f'<option value="{c}">{c}</option>')
    return sel_re.sub(lambda _: m.group(1) + ''.join(opts) + m.group(3), html, count=1)


def patch_filt_access_free_toggle(html, has_free):
    """If has_free is False, hide the Gratuit/Free button via the `hidden`
    attribute (preserves DOM for idempotency). Otherwise ensure it's visible.

    Locale-agnostic: we only toggle the `hidden` attribute on the button
    that carries data-v="free".
    """
    # Match the free button with possibly a `hidden` attr already.
    btn_re = re.compile(r'<button(?P<attrs>[^>]*)data-v="free"(?P<rest>[^>]*)>')

    def repl(m):
        attrs = (m.group('attrs') or '') + (m.group('rest') or '')
        # Strip any prior hidden token (idempotency).
        attrs = re.sub(r'\s*\bhidden\b\s*', ' ', attrs).strip()
        if not has_free:
            return f'<button {attrs} data-v="free" hidden>' if attrs else f'<button data-v="free" hidden>'
        return f'<button {attrs} data-v="free">' if attrs else f'<button data-v="free">'

    return btn_re.sub(repl, html, count=1)


# Replacement filter <script> for lacs-plages: drops PINS+paidOf, reads
# .card-tag.is-payant/.is-gratuit/.is-seasonal from the rendered DOM (the
# same mechanism the other 13 hubs use, where card tags come from the
# JSON catalog via fiche_card_html). The lake match reads sec.dataset.lac
# which is now emitted by build_main_block for lacs-plages.
LACS_PLAGES_FILTER_JS = """// FILTERS (lake + commune + access + sort) — card-tag mechanism
(function(){
  const SG="lieu affiché",PL="lieux affichés";
  const lacSel=document.getElementById('filt-lac');
  const communeSel=document.getElementById('filt-commune');
  const accessGroup=document.getElementById('filt-access');
  const sortSel=document.getElementById('filt-sort');
  const countN=document.getElementById('count-n');
  const countLabel=document.getElementById('count-label');
  const emptyState=document.getElementById('empty-state');
  let curLac='',curCommune='',curAccess='all',curSort='commune';
  function applyFilters(){
    let total=0;
    document.querySelectorAll('.commune-section').forEach(sec=>{
      const lacMatch=!curLac||sec.dataset.lac===curLac;
      const communeMatch=!curCommune||sec.dataset.commune===curCommune;
      let vis=0;
      sec.querySelectorAll('.card').forEach(card=>{
        const isPaid=!!card.querySelector('.card-tag.is-payant')||!!card.querySelector('.card-tag.is-seasonal');
        const isFree=!!card.querySelector('.card-tag.is-gratuit')||!!card.querySelector('.card-tag.is-seasonal');
        const am=curAccess==='all'||(curAccess==='free'&&isFree)||(curAccess==='paid'&&isPaid);
        const show=lacMatch&&communeMatch&&am;
        card.classList.toggle('hidden',!show);
        if(show){vis++;total++;}
      });
      sec.classList.toggle('hidden',vis===0);
    });
    if(countN)countN.textContent=total;
    if(countLabel)countLabel.textContent=total===1?SG:PL;
    if(emptyState)emptyState.style.display=total===0?'block':'none';
  }
  function applySort(){ if(curSort!=='alpha')return;
    document.querySelectorAll('.commune-section .carousel').forEach(c=>{Array.from(c.querySelectorAll('.card')).sort((a,b)=>(a.querySelector('a.title')?.textContent||'').localeCompare(b.querySelector('a.title')?.textContent||'')).forEach(x=>c.appendChild(x));}); }
  if(lacSel)lacSel.addEventListener('change',e=>{curLac=e.target.value;applyFilters();});
  if(communeSel)communeSel.addEventListener('change',e=>{curCommune=e.target.value;applyFilters();});
  if(accessGroup)accessGroup.addEventListener('click',e=>{if(e.target.tagName==='BUTTON'){accessGroup.querySelectorAll('button').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');curAccess=e.target.dataset.v;applyFilters();}});
  if(sortSel)sortSel.addEventListener('change',e=>{curSort=e.target.value;applySort();});
  applyFilters();
})();"""


def patch_lacs_plages_filter_js(html):
    """Replace the legacy PINS-based filter JS in lacs-plages with the
    card-tag mechanism. Idempotent: detects whether the new variant is
    already in place by looking for the `const SG="lieu affiché"`
    declaration outside any PINS context.
    """
    # The legacy block starts with the `// FILTERS (lake + commune ...)`
    # comment and ends just before the very next `</script>` of the page.
    legacy_re = re.compile(
        r'// FILTERS \(lake \+ commune \+ access \+ sort\)\s*\n'
        r'\(function\(\)\{.*?\n\}\)\(\);',
        re.DOTALL,
    )
    return legacy_re.sub(lambda _: LACS_PLAGES_FILTER_JS, html, count=1)


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
    "que-faire":         {"fr":"Que faire ?","en":"What to do","de":"Was unternehmen","it":"Cosa fare","es":"Qué hacer","nl":"Wat te doen"},
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
    photo_index = _load_photo_index()
    assignments = []  # Phase 4: capture (hub, slug, type, photo, score, reason)
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
        # Communes actually present in the rendered card set (source of
        # truth for filt-commune options). Used by patch_filt_commune to
        # eliminate ghost options structurally.
        communes_in_hub = {fiches[s].get("commune") for s in union_slugs if fiches[s].get("commune")}
        # Does the hub have any free fiche? Drives whether the Gratuit
        # access-toggle button is rendered hidden. Seasonal counts as
        # free-eligible (the JS filter treats seasonal as both).
        has_free = any(
            fiches[s].get("schema_org", {}).get("is_free") is True
            or fiches[s].get("schema_org", {}).get("tariff_kind") == "seasonal"
            for s in union_slugs
        )
        for lang in ("fr",) + LOCALES:
            hub_name = locale_names.get(lang)
            if not hub_name: continue
            dir_path = (ROOT if lang == "fr" else ROOT / lang) / hub_name
            if not dir_path.exists():
                print(f"  ! [{lang}] {hub_name}/ does not exist; skipping")
                continue
            p = dir_path / "index.html"
            html = p.read_text(encoding="utf-8")
            new_main = build_main_block(union, lang, hub_name=fr_hub,
                                        photo_index=photo_index,
                                        assignments=assignments)
            new_html = splice_main(html, new_main)
            # Filter chrome patches (apply to every hub, every locale).
            new_html = patch_filt_commune(new_html, communes_in_hub, lang)
            new_html = patch_filt_access_free_toggle(new_html, has_free)
            # lacs-plages: replace the legacy PINS-based JS with the
            # card-tag mechanism. Idempotent — re-running is a no-op.
            if fr_hub == "lacs-plages":
                new_html = patch_lacs_plages_filter_js(new_html)
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

    # Phase 4: emit the photo-assignment report so Eddie can spot-check
    # the picks. Sorted by (hub, slug) for deterministic output.
    if assignments:
        from collections import Counter
        per_hub_photo = defaultdict(Counter)
        for hub, slug, typ, photo, score, reason in assignments:
            per_hub_photo[hub][photo] += 1
        max_repeat = {hub: c.most_common(1)[0][1] for hub, c in per_hub_photo.items()}
        lines = [
            "# Phase 4 — photo assignments (gate artifact)",
            "",
            f"**Date**: 2026-06-14",
            f"**Total assignments**: {len(assignments)} (one per (hub × slug) on the FR canonical hub)",
            "",
            "## Per-hub diversity",
            "",
            "| hub | fiches | distinct photos | max repeat of one photo |",
            "|---|---:|---:|---:|",
        ]
        for hub in sorted(per_hub_photo):
            n_fiches = sum(per_hub_photo[hub].values())
            n_distinct = len(per_hub_photo[hub])
            lines.append(f"| `{hub}` | {n_fiches} | {n_distinct} | {max_repeat[hub]} |")
        lines += [
            "",
            "## Per-fiche assignments",
            "",
            "| hub | slug | type | photo | score | reason |",
            "|---|---|---|---|---:|---|",
        ]
        for row in sorted(assignments):
            hub, slug, typ, photo, score, reason = row
            score_s = str(score) if score is not None else "—"
            lines.append(f"| `{hub}` | `{slug}` | `{typ}` | `{photo}` | {score_s} | {reason} |")
        (ROOT / "reports" / "photo-assignments.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"\nwrote reports/photo-assignments.md  ({len(assignments)} rows)")


if __name__ == "__main__":
    main()
