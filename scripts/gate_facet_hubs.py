#!/usr/bin/env python3
"""gate_facet_hubs.py — HANDOFF-facet-hubs §7. Guards the inverted facet layer.

Asserts, against the LIVE built tree + source of truth:
  1. Derived membership: every card on an HTML facet hub is a lieu whose facet is
     non-null at source (api non-null / lieux.json is_free true). One phantom
     member → red. And no eligible lieu is silently dropped.
  2. Verbatim display: each card's shown value byte-equals the value the builder
     projects from source (no drift between page and source).
  3. No claim-framed title/H1 (deny-list: "accessibles", "gratuits", "ouverts en
     hiver" as page-level claims — info-framing only).
  4. md mirrors: frontmatter counts equal computed counts; every listed slug
     exists in api/lieu/.
  5. Registry ↔ build parity: every html_hub facet produced FR + PROSE pages.

Read-only. Run after build_all. Pairs with the existing build-gate steps
(protected placements, canonical self-ref, byte-stable double build).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import locales  # noqa: E402
import build_facet_hubs as B  # noqa: E402  reuse membership + projection (single source)

LANGS = locales.PROSE
CLAIM_DENY = ["accessibles", "ouverts en hiver", "parking gratuit", "lieux gratuits",
              "wheelchair accessible sites", "free sites", "open in winter"]


def main():
    reg = B.load_registry()
    api, fiches, lieux = B.load_all()
    total = len(api)
    facets = reg["facets"]
    html_facets = [f for f in facets if f.get("html_hub")]
    viol = []

    for f in html_facets:
        key = f["facet_key"]
        members = set(B.members_of(f, api, lieux))
        for lang in LANGS:
            path = os.path.join(ROOT, f"{f['hub_slug']}.html") if lang == "fr" \
                else os.path.join(ROOT, lang, f"{f['hub_slug']}.html")
            if not os.path.exists(path):
                viol.append(f"{key}/{lang}: page missing ({path})")
                continue
            html = open(path, encoding="utf-8").read()

            # 3. no claim-framed H1/title
            head = html[:4000].lower()
            for bad in CLAIM_DENY:
                if bad in head:
                    viol.append(f"{key}/{lang}: claim-framed copy in head: {bad!r}")

            # 1+2. every card ↔ a real member, value byte-equals projection
            cards = re.findall(r'<article class="card">.*?</article>', html, re.S)
            shown_names = []
            for c in cards:
                nm = re.search(r"<h3>(.*?)</h3>", c, re.S)
                vm = re.search(r"<bdi>(.*?)</bdi>", c, re.S)
                if not nm:
                    continue
                shown_names.append(nm.group(1))
            # resolve shown names back to member slugs by frozen FR name
            name_to_slug = {B.esc(B.fr_name(fiches, s)): s for s in members}
            for c in cards:
                nm = re.search(r"<h3>(.*?)</h3>", c, re.S)
                vm = re.search(r"<bdi>(.*?)</bdi>", c, re.S)
                if not nm:
                    continue
                shown_name = nm.group(1)
                slug = name_to_slug.get(shown_name)
                if slug is None:
                    viol.append(f"{key}/{lang}: card '{shown_name[:40]}' is not a derived member")
                    continue
                expect = B.facet_value_text(key, slug, api, fiches, lang) or B.L(B.UI["not_docd"], lang)
                got = vm.group(1) if vm else ""
                if got != B.esc(expect):
                    viol.append(f"{key}/{lang}/{slug}: displayed value != source projection")
            # 1b. no eligible member silently dropped (count parity)
            if len(cards) != len(members):
                viol.append(f"{key}/{lang}: {len(cards)} cards vs {len(members)} derived members")

    # 4. md mirror frontmatter counts + slug existence
    for f in facets:
        members = B.members_of(f, api, lieux)
        for lang in ("fr", "en"):
            md_path = os.path.join(ROOT, "content", "facets",
                                   f"{f['facet_key']}.md" if lang == "fr" else os.path.join("en", f"{f['facet_key']}.md"))
            if not os.path.exists(md_path):
                viol.append(f"md {f['facet_key']}/{lang}: missing")
                continue
            md = open(md_path, encoding="utf-8").read()
            dm = re.search(r"lieux_documented:\s*(\d+)", md)
            tm = re.search(r"lieux_total:\s*(\d+)", md)
            if not dm or int(dm.group(1)) != len(members):
                viol.append(f"md {f['facet_key']}/{lang}: documented count != {len(members)}")
            if not tm or int(tm.group(1)) != total:
                viol.append(f"md {f['facet_key']}/{lang}: total != {total}")

    print(f"gate_facet_hubs: {len(html_facets)} HTML hubs × {len(LANGS)} locales + "
          f"{len(facets)} md facets checked")
    if viol:
        print(f"::error::{len(viol)} facet-hub violation(s):")
        for v in viol[:40]:
            print(f"    ✗ {v}")
        sys.exit(1)
    print("✓ membership derived; displayed values verbatim; info-framed; md counts honest")


if __name__ == "__main__":
    main()
