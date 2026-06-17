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
    """A hero is 'real' only when:
    - it's an external URL (Wikimedia/Commons etc.), OR
    - it's a local per-fiche photo (/img/<hub>/<slug>-hero.jpg or
      /<slug>-hero.jpg) AND the file actually exists on disk.
    Generic placeholders (generique-*.jpg) and broken local refs both → False.

    2026-06-15: local images now live under /img/<hub>/. Both the legacy
    leading-slash format and the new /img/-prefixed format resolve via
    `lstrip("/")` + path-exists check, so this function works for both.
    """
    if not hero:
        return False
    if hero.startswith(("http://", "https://")):
        return True
    name = hero.lstrip("/")
    basename = name.rsplit("/", 1)[-1]
    if basename.startswith("generique-"):
        return False
    return os.path.exists(os.path.join(ROOT, name))


def main():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "Json", "*.json"))):
        d = json.load(open(path))
        slug = d.get("slug")
        if not slug:
            continue
        # JOB 6: draft fiches are not in the public catalog.
        # 'unverified' (source-audit) is held out of the index exactly like draft.
        if d.get("status") in ("draft", "unverified"):
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
