#!/usr/bin/env python3
"""build_pilot_langs.py — STAGED facts-first pilot for new (vocab-verified) langs.

HANDOFF-06 Phase B, the safe way. Renders a ~20-page marquee pilot per
new language whose `reviewed` flag in data/i18n-labels.json is non-false AND
which is not one of the 6 already-live locales AND not RTL (ar/he need the RTL
engine — Phase C). Each page is FACTS-FIRST:

  descriptor (from `category` → descriptors_by_type) + a card of ONLY
  language-independent / enum facts (Pavillon Bleu, PMR status, free/paid,
  price €, official link) labelled from the vocab. No FR free-text prose is
  ever shown, so no FR fallback can leak. `null` → "not stated".

CRITICAL ISOLATION (so it can never disturb the 6 ranking languages):
  - pages carry <meta name="robots" content="noindex,nofollow"> (staging).
  - written to <lang>/<slug>.html for langs OUTSIDE every live roster
    (build_site LOCALES, check_reachability ALL_LANGS, fix_hreflang_sitemap
    LANGS are all en/de/it/es/nl) → not deployed, not in sitemap, not in
    hreflang, not reachability-checked.
  - NOT wired into build_all. Run manually; commit as review artifacts.

Frozen FR proper nouns verbatim. Protected fiches never rendered.
"""
import html as _h
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS = json.loads(open(os.path.join(ROOT, "data", "i18n-labels.json"), encoding="utf-8").read())
LIVE6 = {"fr", "en", "de", "it", "es", "nl"}
RTL = set(LABELS["_meta"].get("rtl", []))
PROTECTED = {"chez-nous-a-la-plage", "chalet-du-tornet"}

# ~20 marquee pilot fiches (Mont-Blanc / Chamonix / Annecy / Évian / Megève set).
PILOT = [
    "telepherique-aiguille-du-midi", "telepherique-du-brevent",
    "telepherique-des-grands-montets", "train-du-montenvers-mer-de-glace",
    "tramway-du-mont-blanc", "musee-du-mont-blanc-chamonix",
    "espace-tairraz-musee-des-cristaux-chamonix", "patinoire-richard-bozon-chamonix",
    "cascade-d-angon", "gorges-du-fier", "musee-chateau-annecy",
    "palais-de-l-ile-annecy", "plage-imperial-annecy", "jardins-europe-annecy",
    "le-semnoz", "mont-saleve", "telepherique-du-saleve",
    "plage-d-evian-centre-nautique", "casino-evian-resort-evian",
    "patinoire-palais-megeve",
]

CATEGORY_DESCRIPTOR = {
    "plage": "plage", "lac": "lac", "cascade": "cascade", "chateau": "chateau",
    "musee": "musee", "telecabine": "telecabine", "point-de-vue": "point_de_vue",
    "sentier": "sentier", "parc": "parc", "voie-verte": "voie_verte",
    "base-nautique": "base_loisirs", "eglise": "eglise",
}


def V(section, key, lang):
    return LABELS.get(section, {}).get(key, {}).get(lang, "")


def esc(s):
    return _h.escape(str(s or ""), quote=True)


def fact_rows(d, lang):
    """Only language-independent / enum facts, each with a vocab label."""
    rows = []
    so = d.get("schema_org", {}) or {}
    facts = d.get("i18n", {}).get("fr", {}).get("facts", {}) or {}
    # commune — a place name (language-independent)
    commune = d.get("commune") or facts.get("commune")
    if commune:
        rows.append((V("fact_labels", "commune", lang), esc(commune)))
    # price / free-paid — from structured signals only, never the FR prose
    price_from = d.get("price_from")
    cur = {"EUR": "€"}.get(d.get("price_currency"), d.get("price_currency") or "")
    is_free = so.get("is_free")
    if isinstance(price_from, (int, float)) and price_from > 0:
        rows.append((V("fact_labels", "tarif", lang), f"{price_from:.2f}".replace(".", ",") + "\u00a0" + cur))
    elif is_free is True:
        rows.append((V("fact_labels", "tarif", lang), V("fact_values", "gratuit", lang)))
    elif is_free is False:
        rows.append((V("fact_labels", "tarif", lang), V("fact_values", "payant", lang)))
    # Pavillon Bleu — show only the positive marker
    if str(facts.get("pavillon_bleu_2026", "")).strip().upper() == "OUI":
        rows.append((V("fact_labels", "pavillon_bleu", lang), V("fact_values", "oui", lang)))
    # PMR — enum status; null => "not stated"
    ap = d.get("acces_pmr")
    if isinstance(ap, dict):
        st = ap.get("status")
        valkey = {"accessible": "pmr_accessible", "partiel": "pmr_partiel",
                  "non_accessible": "pmr_non"}.get(st, "pmr_non_renseigne")
        rows.append((V("fact_labels", "acces_pmr", lang), V("fact_values", valkey, lang)))
    return rows


CSS = ("*{box-sizing:border-box}body{margin:0;font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;"
       "background:#FAF7F0;color:#22302f;line-height:1.55}.wrap{max-width:680px;margin:0 auto;padding:18px}"
       ".staging{background:#fff3cd;border:1px solid #ffe69c;color:#7a5b00;border-radius:8px;"
       "padding:6px 12px;font-size:12px;font-weight:600;margin-bottom:14px}"
       "h1{font-size:25px;margin:.2em 0}.desc{color:#1F6E78;font-weight:600;margin:.2em 0 1em}"
       "dl.facts{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;background:#fff;border:1px solid #e3ddd0;"
       "border-radius:12px;padding:14px 16px}dt{color:#5b6b6a;font-size:14px}dd{margin:0;font-weight:600;text-align:right}"
       "a.site{display:inline-block;margin-top:12px;color:#1F6E78;font-weight:600}"
       "footer{margin-top:26px;padding-top:12px;border-top:1px solid #e3ddd0;font-size:12px;color:#5b6b6a}")


def render(d, lang):
    name = d.get("i18n", {}).get("fr", {}).get("name") or d["slug"]   # frozen FR name, verbatim
    commune = d.get("commune", "")
    desc_key = CATEGORY_DESCRIPTOR.get(d.get("category"))
    descriptor = V("descriptors_by_type", desc_key, lang) if desc_key else ""
    rows = fact_rows(d, lang)
    facts_html = "".join(f"<dt>{esc(lbl)}</dt><dd>{val}</dd>" for lbl, val in rows if lbl)
    site = d.get("official_site_url")
    site_html = (f'<a class="site" href="{esc(site)}" rel="nofollow noopener" target="_blank">'
                 f'{esc(V("ui_chrome", "site_officiel", lang))} ↗</a>') if site else ""
    method = LABELS["_meta"].get("review_method", {}).get(lang, "")
    schema = {"@context": "https://schema.org", "@type": "TouristAttraction",
              "name": name, "inLanguage": lang,
              "address": {"@type": "PostalAddress", "addressLocality": commune,
                          "addressRegion": "Haute-Savoie", "addressCountry": "FR"}}
    if d.get("latitude") and d.get("longitude"):
        schema["geo"] = {"@type": "GeoCoordinates", "latitude": d["latitude"], "longitude": d["longitude"]}
    title = f"{name} · {commune} — loisirs74"
    meta_desc = (descriptor + (", " if descriptor else "") + commune + " (Haute-Savoie).").strip()
    return f"""<!doctype html><html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="robots" content="noindex,nofollow">
<meta name="description" content="{esc(meta_desc)}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>{CSS}</style></head><body><div class="wrap">
<div class="staging">⚠ STAGING — {esc(lang)} pilot · not indexed · awaiting review</div>
<h1>{esc(name)}</h1>
{f'<p class="desc">{esc(descriptor)}</p>' if descriptor else ''}
<dl class="facts">{facts_html}</dl>
{site_html}
<footer>© 2026 · Bleu canard édition · Edmaster &amp; Claudius 🦆<br>
Facts-first pilot · labels: {esc(method)}</footer>
</div></body></html>"""


def main():
    reviewed = LABELS["_meta"].get("reviewed", {})
    eligible = [l for l, r in reviewed.items()
                if r and r is not False and l not in LIVE6 and l not in RTL]
    print(f"eligible pilot langs: {eligible}")
    n = 0
    for lang in eligible:
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        for slug in PILOT:
            if slug in PROTECTED:
                continue
            fp = os.path.join(ROOT, "Json", f"{slug}.json")
            if not os.path.exists(fp):
                print(f"  [skip] {slug} (no fiche)"); continue
            d = json.loads(open(fp, encoding="utf-8").read())
            out = os.path.join(ROOT, lang, f"{slug}.html")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(render(d, lang))
            n += 1
    print(f"build_pilot_langs: {n} staged page(s) across {len(eligible)} lang(s) "
          f"({len(PILOT)} marquee slugs)")


if __name__ == "__main__":
    main()
