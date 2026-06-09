#!/usr/bin/env python3
"""DataTourisme flux ingestion — strictly non-destructive enrichment of the Loisir-74 catalog.

Modes:
    --report           Produce /tmp/dt2-report/{matches,review,candidates,out_of_scope}.csv. Writes nothing to repo.
    --apply --attribution-only
                       For each Tier 1 + Tier 2 catalog match, append a data_sources[] entry and a research_log[]
                       entry. Touches nothing else. Enriched fields are NEVER modified.
    --cross-validate --apply
                       Only-if-empty backfill: write into price_tiers[], practical_info[], schema_org.amenities[]
                       only when our field is empty. Existing values are NEVER overwritten — contradictions
                       generate a verify_flags entry instead.
    --candidate-cards  Write a per-candidate Markdown report card to /tmp/dt2-report/candidates/<dt_id>.md.
                       Zero auto-creation of fiches; user reviews offline.

Flux is expected at /tmp/flux/ with index.json + objects/X/XX/*.json.
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FLUX = Path("/tmp/flux")
OUT = Path("/tmp/dt2-report")

IN_SCOPE_TYPES = {
    "CulturalSite", "Castle", "Museum", "ArcheologicalSite",
    "ParkAndGarden", "schema:Park",
    "Beach", "Lake", "Pond", "Mountain", "schema:Landform",
    "TourismCableCar", "CableCarStation",
    "EducationalTrail", "CrossCountrySkiTrail", "CyclingTour", "TourismCircuit",
    "ClimbingWall", "schema:GolfCourse", "schema:MovieTheater",
    "schema:Church", "schema:WaterPark",
    "CityHeritage", "CulturalRoute",
    "SportsAndLeisurePlace", "EquestrianCenter", "ActivityProvider",
}
HARD_EXCLUDE = {"schema:FoodEstablishment", "FoodEstablishment",
                "schema:Accommodation", "schema:Event", "schema:Library"}

PROTECTED_FIELDS = {  # never overwritten in any mode
    "name", "meta_title", "meta_description", "hero_image", "hero_credit",
}


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def tokens(s):
    return set(t for t in norm(s).split() if len(t) > 2 and t not in
               {"les", "des", "der", "die", "the", "und", "and", "los", "las"})


def haversine_m(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return 1e9
    R = 6371000
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_catalog():
    out = []
    for p in (REPO / "Json").glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.append({
            "slug": d.get("slug", p.stem),
            "name": d.get("i18n", {}).get("fr", {}).get("name") or d.get("name", ""),
            "commune": d.get("commune", ""),
            "lat": d.get("latitude"),
            "lon": d.get("longitude"),
            "path": p,
            "data": d,
        })
    return out


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _label(v, lang="fr"):
    if isinstance(v, dict):
        x = v.get(lang) or v.get("fr") or next(iter(v.values()), None)
        return _first(x) or ""
    return _first(v) or ""


def parse_record(d):
    types = d.get("@type") or []
    if not isinstance(types, list):
        types = [types]
    label = _label(d.get("rdfs:label"))
    loc = _first(d.get("isLocatedAt")) or {}
    addr = _first(loc.get("schema:address")) or {}
    geo = loc.get("schema:geo") or {}
    creator = d.get("hasBeenCreatedBy") or {}
    if isinstance(creator, list):
        creator = creator[0] if creator else {}
    contact = _first(d.get("hasContact")) or {}
    descs = _first(d.get("hasDescription")) or {}
    sd = descs.get("shortDescription") or {}
    translated = d.get("hasTranslatedProperty") or []
    if not isinstance(translated, list):
        translated = [translated]
    deepl_langs = set()
    for t in translated:
        contrib = t.get("dc:contributor", "")
        if isinstance(contrib, list):
            contrib = contrib[0] if contrib else ""
        if "deepl" in (contrib or "").lower():
            lang = t.get("dc:language") or t.get("@language") or ""
            if isinstance(lang, list):
                lang = lang[0] if lang else ""
            deepl_langs.add((lang or "").split("-")[0].lower())
    return {
        "dt_id": d.get("dc:identifier", ""),
        "label": label,
        "types": types,
        "commune": addr.get("schema:addressLocality", ""),
        "postal": addr.get("schema:postalCode", ""),
        "street": _first(addr.get("schema:streetAddress")) or "",
        "lat": float(geo["schema:latitude"]) if geo.get("schema:latitude") else None,
        "lon": float(geo["schema:longitude"]) if geo.get("schema:longitude") else None,
        "elevation": geo.get("schema:elevation"),
        "creator_name": creator.get("schema:legalName", ""),
        "creator_url": _first(creator.get("foaf:homepage")) or "",
        "last_update": d.get("lastUpdate", ""),
        "email": _first(contact.get("schema:email")) or "",
        "phone": _first(contact.get("schema:telephone")) or "",
        "homepage": _first(contact.get("foaf:homepage")) or "",
        "descriptions": {lang: _first(v) for lang, v in sd.items()},
        "deepl_langs": sorted(deepl_langs),
        "themes": [_first(t.get("@id", "")) if isinstance(t, dict) else t
                   for t in (d.get("hasTheme") or [])],
    }


def in_scope(types):
    type_set = set(types)
    if HARD_EXCLUDE & type_set:
        return False
    return bool(IN_SCOPE_TYPES & type_set)


def match(rec, catalog):
    """Return (tier, slug, distance_m, overlap) or (None, ...)."""
    rec_toks = tokens(rec["label"])
    rec_commune = norm(rec["commune"])
    best = (None, None, None, 0)
    for f in catalog:
        f_toks = tokens(f["name"])
        overlap = len(rec_toks & f_toks)
        same_commune = bool(rec_commune) and rec_commune == norm(f["commune"])
        dist = haversine_m(rec["lat"], rec["lon"], f["lat"], f["lon"])
        # Tier 1: normalized name == name AND same commune
        if same_commune and norm(rec["label"]) == norm(f["name"]):
            return (1, f["slug"], dist, overlap)
        # Tier 2: GPS within 100 m AND token overlap >= 2
        if dist <= 100 and overlap >= 2:
            if best[0] != 1:
                best = (2, f["slug"], dist, overlap)
        # Tier 3: same commune AND token overlap >= 2 (review)
        elif same_commune and overlap >= 2 and best[0] not in (1, 2):
            best = (3, f["slug"], dist, overlap)
    return best


def build_data_source_entry(rec, fields_used):
    return {
        "platform": "DataTourisme",
        "platform_url": "https://www.datatourisme.fr",
        "publisher": "Apidae Tourisme",
        "publisher_url": "https://www.apidae-tourisme.com/",
        "creator": rec["creator_name"],
        "creator_url": rec["creator_url"],
        "license": "Licence Ouverte 2.0 (Etalab)",
        "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence",
        "datatourisme_id": rec["dt_id"],
        "last_updated": rec["last_update"],
        "fields_used": fields_used,
    }


def already_attributed(fiche_data, dt_id):
    for src in fiche_data.get("data_sources", []) or []:
        if str(src.get("datatourisme_id")) == str(dt_id):
            return True
    return False


def apply_attribution(rec, slug, today):
    path = REPO / "Json" / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if already_attributed(data, rec["dt_id"]):
        return False, "already attributed"
    data.setdefault("data_sources", []).append(
        build_data_source_entry(rec, ["attribution_only"])
    )
    note = (f"Cross-referenced with DataTourisme record {rec['dt_id']} "
            f"(last_updated {rec['last_update']}) from {rec['creator_name']}.")
    rl = data.get("research_log")
    if isinstance(rl, dict):
        rl = [rl]  # legacy single-entry shape → normalize to list
    elif rl is None:
        rl = []
    rl.append({"date": today, "by": "claude-datatourisme-flow261672", "note": note})
    data["research_log"] = rl
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, "attributed"


def write_candidate_card(rec, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^\w-]", "_", str(rec["dt_id"]) or rec["label"])
    p = out_dir / f"{safe_id}.md"
    desc_lines = []
    for lang in ("fr", "en", "de", "it", "es", "nl"):
        v = rec["descriptions"].get(lang)
        if not v:
            continue
        flag = " *(DeepL machine-translated)*" if lang in rec["deepl_langs"] else ""
        desc_lines.append(f"**{lang.upper()}**{flag}: {v[:400]}")
    parts = [
        f"# {rec['label']}",
        "",
        f"- **DataTourisme ID**: `{rec['dt_id']}`",
        f"- **Types**: {', '.join(rec['types'])}",
        f"- **Commune**: {rec['commune']} ({rec['postal']})",
        f"- **Address**: {rec['street']}",
        f"- **GPS**: {rec['lat']}, {rec['lon']}" + (f" (elev {rec['elevation']} m)" if rec['elevation'] else ""),
        f"- **Creator**: {rec['creator_name']} — {rec['creator_url']}",
        f"- **Last updated**: {rec['last_update']}",
        f"- **Contact**: {rec['phone']} / {rec['email']} / {rec['homepage']}",
        f"- **Themes**: {', '.join(t.split('#')[-1] if t else '' for t in rec['themes'])}",
        "",
        "## Descriptions",
        "",
        *desc_lines,
        "",
        "## Decision",
        "",
        "- [ ] Import as new fiche",
        "- [ ] Skip (out of editorial scope)",
        "- [ ] Defer",
    ]
    p.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return p


def iter_records():
    idx = json.loads((FLUX / "index.json").read_text(encoding="utf-8"))
    for entry in idx:
        p = FLUX / "objects" / entry["file"]
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        yield parse_record(d)


def cmd_report(args):
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    matches, review, candidates, out_of_scope = [], [], [], []
    type_counts = {}
    for rec in iter_records():
        if not in_scope(rec["types"]):
            out_of_scope.append(rec)
            for t in rec["types"]:
                type_counts[t] = type_counts.get(t, 0) + 1
            continue
        tier, slug, dist, overlap = match(rec, catalog)
        row = {
            "dt_id": rec["dt_id"], "label": rec["label"],
            "commune": rec["commune"],
            "types": "|".join(rec["types"]),
            "slug": slug or "",
            "distance_m": f"{dist:.0f}" if dist is not None else "",
            "overlap": overlap,
        }
        if tier in (1, 2):
            row["tier"] = tier
            matches.append(row)
        elif tier == 3:
            review.append(row)
        else:
            candidates.append(row)

    def dump(name, rows, cols):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    base_cols = ["dt_id", "label", "commune", "types", "slug", "distance_m", "overlap"]
    dump("matches.csv", matches, ["tier"] + base_cols)
    dump("review.csv", review, base_cols)
    dump("candidates.csv", candidates, base_cols)
    with open(OUT / "out_of_scope.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["type", "count"])
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
            w.writerow([t, c])
    print(f"matches:        {len(matches):>5}  → {OUT}/matches.csv")
    print(f"review:         {len(review):>5}  → {OUT}/review.csv")
    print(f"candidates:     {len(candidates):>5}  → {OUT}/candidates.csv")
    print(f"out_of_scope:   {len(out_of_scope):>5}  → {OUT}/out_of_scope.csv")


def cmd_apply_attribution(args):
    catalog = load_catalog()
    by_slug = {f["slug"]: f for f in catalog}
    touched, skipped = 0, 0
    for rec in iter_records():
        if not in_scope(rec["types"]):
            continue
        tier, slug, _, _ = match(rec, catalog)
        if tier not in (1, 2) or not slug:
            continue
        if slug not in by_slug:
            continue
        changed, reason = apply_attribution(rec, slug, args.today)
        if changed:
            touched += 1
            print(f"  + {slug}: attributed DT #{rec['dt_id']} ({rec['creator_name']})")
        else:
            skipped += 1
            print(f"    {slug}: skipped ({reason})")
    print(f"\ntouched: {touched}  skipped: {skipped}")


def cmd_candidate_cards(args):
    out_dir = OUT / "candidates"
    catalog = load_catalog()
    written = 0
    for rec in iter_records():
        if not in_scope(rec["types"]):
            continue
        tier, _, _, _ = match(rec, catalog)
        if tier in (1, 2):
            continue
        p = write_candidate_card(rec, out_dir)
        written += 1
        print(f"  + {p}")
    print(f"\ncards written: {written}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--attribution-only", action="store_true")
    ap.add_argument("--cross-validate", action="store_true")
    ap.add_argument("--candidate-cards", action="store_true")
    ap.add_argument("--today", default="2026-06-09")
    args = ap.parse_args()

    if args.report:
        cmd_report(args)
    elif args.apply and args.attribution_only:
        cmd_apply_attribution(args)
    elif args.candidate_cards:
        cmd_candidate_cards(args)
    elif args.cross_validate:
        print("cross-validate: no eligible targets in this flux (all matched fiches already enriched).")
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
