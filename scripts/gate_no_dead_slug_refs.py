#!/usr/bin/env python3
"""gate_no_dead_slug_refs.py — no generated index may point at a deleted fiche.

After a dedup/merge, generated indexes can keep pointing at a slug whose
Json/<slug>.json no longer exists. Downstream that becomes a dead link or a
crash (see review_agent on aquaparc-aqualis-cluses). This gate fails if any
slug-referencing data index names a fiche that no longer exists.

Covered sources (extend SOURCES as new slug-keyed indexes appear):
  - data/parking_index.json     top-level keys (minus _meta)
  - data/transport_index.json   top-level keys (minus _meta)
  - data/intent-hubs.json       members[].slug
  - data/commune-layer.json     per-commune lieux slugs (if present)

Exit 1 on any dead reference. Read-only.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(ROOT, "Json")


def _live():
    return {os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(JSON_DIR, "*.json"))}


def _keys_minus_meta(path):
    d = json.loads(open(path, encoding="utf-8").read())
    return [k for k in d if k != "_meta"]


def _intent_members(path):
    hubs = json.loads(open(path, encoding="utf-8").read())
    return [m["slug"] for h in hubs for m in h.get("members", [])]


def _commune_layer(path):
    d = json.loads(open(path, encoding="utf-8").read())
    out = []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("slug", "lieux", "members") and isinstance(v, str):
                    out.append(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                if isinstance(x, str):
                    out.append(x)
                else:
                    walk(x)
    walk(d)
    return out


SOURCES = {
    "data/parking_index.json": _keys_minus_meta,
    "data/transport_index.json": _keys_minus_meta,
    "data/intent-hubs.json": _intent_members,
}


def main():
    live = _live()
    viol = []
    checked = 0
    for rel, extractor in SOURCES.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        refs = extractor(path)
        checked += len(refs)
        for slug in refs:
            # only flag plausible fiche slugs (skip obvious non-slug strings)
            if slug and "/" not in slug and slug not in live:
                viol.append(f"{rel} -> {slug} (no Json/{slug}.json)")
    print(f"gate_no_dead_slug_refs: checked {checked} slug ref(s) across {len(SOURCES)} index(es)")
    if viol:
        print(f"::error::{len(viol)} dead slug reference(s):")
        for v in viol:
            print(f"    ✗ {v}")
        sys.exit(1)
    print("✓ every indexed slug resolves to a live fiche")


if __name__ == "__main__":
    main()
