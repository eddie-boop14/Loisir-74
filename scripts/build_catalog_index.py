#!/usr/bin/env python3
"""Build catalog-index.json from lieux.json + per-fiche JSONs.

Schema (compact, designed for browser fetch + filter):
    [
      {
        "slug": "plage-de-saint-jorioz",
        "name": "Plage de Saint-Jorioz",
        "commune": "Saint-Jorioz",
        "category": "plage",
        "hero": "/plage-de-saint-jorioz-hero.jpg",
        "real": true
      },
      ...
    ]

`real` = True when hero_image is NOT a generic placeholder
(i.e. doesn't start with "/generique-" or "generique-").
The Photothèque uses this to surface fiches still on generics.
"""
import json
import glob
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_real(hero):
    if not hero:
        return False
    name = hero.lstrip("/")
    return not name.startswith("generique-")


def main():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "Json", "*.json"))):
        d = json.load(open(path))
        slug = d.get("slug")
        if not slug:
            continue
        fr = (d.get("i18n") or {}).get("fr") or {}
        name = fr.get("name") or slug
        commune = d.get("commune") or ""
        category = d.get("category") or "?"
        hero = d.get("hero_image") or ""
        out.append({
            "slug": slug,
            "name": name,
            "commune": commune,
            "category": category,
            "hero": hero,
            "real": is_real(hero),
        })

    out.sort(key=lambda r: r["slug"])
    target = os.path.join(ROOT, "catalog-index.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {target}: {len(out)} entries")

    n_real = sum(1 for r in out if r["real"])
    n_gen = len(out) - n_real
    print(f"  fiches with real hero: {n_real}")
    print(f"  fiches on generic:     {n_gen}")


if __name__ == "__main__":
    main()
