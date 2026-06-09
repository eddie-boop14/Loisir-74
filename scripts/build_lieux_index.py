#!/usr/bin/env python3
"""Rebuild lieux.json + api/lieux.json from current Json/*.json files.

These two files are the lightweight indexes consumed by:
  - /studio.html (Tab 1 fiche selector, Tab 6 Photothèque)
  - /index.html and category hubs (card listing fallback)
  - /api/lieux.json (machine-readable manifest for AI/SEO)

Both have historically been kept in sync by piecemeal "batch" scripts
(integrate_combined_batch.py). This script does a clean full rebuild
from Json/ — the single source of truth — so the indexes track the
catalog exactly.

Includes Dutch (nl) URLs and i18n now that /nl/ pages are rendered.
"""
import json
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parent.parent
JSON_DIR = REPO / "Json"
BASE_URL = "https://loisirs74.fr"
LANGS = ("fr", "en", "de", "it", "es", "nl")
TODAY = date.today().isoformat()


def load_all():
    fiches = []
    for p in sorted(JSON_DIR.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        fiches.append(d)
    return fiches


def is_real(hero):
    if not hero:
        return False
    if hero.startswith(("http://", "https://")):
        return True
    name = hero.lstrip("/")
    if name.startswith("generique-"):
        return False
    return (REPO / name).exists()


def build_root_lieux(fiches):
    """Lightweight client-side index: slug, category, multilingual name+commune, GPS, is_free."""
    out = []
    for d in fiches:
        slug = d.get("slug")
        if not slug:
            continue
        i18n_in = d.get("i18n") or {}
        i18n_out = {}
        fr = i18n_in.get("fr") or {}
        fr_name = fr.get("name") or slug
        commune = d.get("commune") or ""
        for L in LANGS:
            block = i18n_in.get(L) or {}
            i18n_out[L] = {
                "name": block.get("name") or fr_name,
                "commune": block.get("commune") or commune,
            }
        is_free = bool((d.get("schema_org") or {}).get("is_free", False))
        out.append({
            "slug": slug,
            "categories": [d.get("category", "?")],
            "i18n": i18n_out,
            "latitude": d.get("latitude"),
            "longitude": d.get("longitude"),
            "is_free": is_free,
        })
    out.sort(key=lambda r: r["slug"])
    return out


def build_api_lieux(fiches):
    """API manifest: slug, name, category, commune, postal_code, GPS, urls (all 6 langs +
    .md mirror), photo state."""
    out = []
    for d in fiches:
        slug = d.get("slug")
        if not slug:
            continue
        fr = (d.get("i18n") or {}).get("fr") or {}
        hero = d.get("hero_image") or ""
        out.append({
            "slug": slug,
            "name": fr.get("name") or slug,
            "category": d.get("category", "?"),
            "commune": d.get("commune", ""),
            "postal_code": str(d.get("postal_code", "") or ""),
            "latitude": d.get("latitude"),
            "longitude": d.get("longitude"),
            "urls": {
                "fr": f"{BASE_URL}/{slug}",
                "en": f"{BASE_URL}/en/{slug}",
                "de": f"{BASE_URL}/de/{slug}",
                "it": f"{BASE_URL}/it/{slug}",
                "es": f"{BASE_URL}/es/{slug}",
                "nl": f"{BASE_URL}/nl/{slug}",
                "markdown": f"{BASE_URL}/content/{slug}.md",
            },
            "photo": {
                "url": hero,
                "type": "real" if is_real(hero) else "placeholder",
            },
        })
    out.sort(key=lambda r: r["slug"])
    return out


def main():
    fiches = load_all()
    print(f"  loaded {len(fiches)} fiche JSONs")

    # Root lieux.json
    root = build_root_lieux(fiches)
    payload = {
        "_comment": f"Auto-generated from Json/*.json on {TODAY}. Contains all {len(root)} published lieux. Used by index.html, category pages, /studio.html (Photothèque + Editor selectors), and related-lieux selector. 6-language i18n incl Dutch.",
        "lieux": root,
    }
    (REPO / "lieux.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"  wrote lieux.json:     {len(root)} entries")

    # api/lieux.json
    api = build_api_lieux(fiches)
    api_payload = {
        "metadata": {
            "name": "Loisirs 74",
            "description": "Independent guide to public leisure sites in Haute-Savoie, France",
            "publisher": "bleu-canard éditions",
            "website": BASE_URL,
            "last_updated": TODAY,
            "license": "Content viewable under fair-use citation. See per-photo licenses.",
            "total_lieux": len(api),
            "languages": ["fr", "en", "de", "it", "es", "nl"],
            "canonical_language": "fr",
            "geographic_scope": {
                "department": "Haute-Savoie",
                "department_code": "74",
                "region": "Auvergne-Rhône-Alpes",
                "country": "France",
                "centroid": {"lat": 45.94, "lon": 6.34},
            },
        },
        "endpoints": {
            "lieux_index": f"{BASE_URL}/api/lieux.json",
            "lieu_markdown": f"{BASE_URL}/content/{{slug}}.md",
            "lieu_html_canonical": f"{BASE_URL}/{{slug}}",
            "sitemap": f"{BASE_URL}/sitemap.xml",
            "llms": f"{BASE_URL}/llms.txt",
            "llms_full": f"{BASE_URL}/llms-full.txt",
        },
        "lieux": api,
    }
    (REPO / "api" / "lieux.json").write_text(
        json.dumps(api_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"  wrote api/lieux.json: {len(api)} entries")

    # Stats: photo state
    real_n = sum(1 for r in api if r["photo"]["type"] == "real")
    placeholder_n = len(api) - real_n
    print(f"  photo state: real={real_n}, placeholder={placeholder_n}")


if __name__ == "__main__":
    main()
