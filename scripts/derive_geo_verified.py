#!/usr/bin/env python3
"""Derive the geo_verified ✅ stamp from already-persisted Google signals.

`place_id` + `gps_drift_m` are written by the sweep (-> `freshness`) and by the
dedicated Google-Maps check (-> `google_check`). This script DERIVES, never
hand-sets, the following top-level fields on `Json/<slug>.json`:

  google_place_id       canonical place_id, deduped (google_check > freshness)
  geo_verified          true iff place_id AND drift<=max AND name-match strong
  geo_verified_date     run date (audit trail)
  geo_verified_source   "google_places"
  geo_verified_drift_m  the drift at verification time (audit trail)

Two tiers, on purpose:

  * `google_place_id` is written for EVERY fiche that carries a place_id. It
    powers the Itinéraire `destination_place_id` pin-fix, which routes Maps to
    the canonical POI and is therefore *independent of drift* — a fiche with a
    bad stored coordinate still gets a correct pin. This is the broad win.

  * `geo_verified` is the stricter, earn-only badge: the stored coordinate is
    itself trustworthy (close to Google AND the matched place is really this
    place). This is the narrow, honest ✅.

Rule (threshold tunable via --max-drift):

  geo_verified = place_id present
              AND gps_drift_m <= max_drift   (default 100 m ≈ "on the venue /
                                              its parking"; 51–150 m is the grey
                                              band, so 100 keeps the stamp
                                              meaningful)
              AND name-match is strong: accent-insensitive *directional* token
                  overlap — the fraction of the fiche-name tokens (minus
                  stop-words) that appear in Google's matched name — >= 0.6.
                  Directional, not Jaccard: Google's name is often longer
                  ("Abbaye d'Aulps - Domaine de Découverte de la Vallée…"), and
                  we only care that *our* name is contained, not that theirs is
                  short.

Precedence (§4.1 of SPECgeoverify): prefer `google_check` (dedicated Google
run) over `freshness` (3-source triangulation) for place_id + gps_drift_m. If
only one is present, use it.

Idempotent: re-run with no signal change writes nothing. Self-correcting: a
fiche that no longer earns the stamp has its geo_verified* fields stripped, so
the badge can never go stale.

No-clobber: ONLY the derived keys above are ever written. latitude/longitude,
i18n, and every curated field are left untouched. The frozen FR place name is
read, never written.

Usage:
    python3 scripts/derive_geo_verified.py                 # write + report
    python3 scripts/derive_geo_verified.py --dry-run       # report only
    python3 scripts/derive_geo_verified.py --max-drift 150 # looser threshold
    python3 scripts/derive_geo_verified.py --report-rejected  # +near-miss dump
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

JSON_DIR = "Json"
TODAY = datetime.date.today().isoformat()
DEFAULT_MAX_DRIFT = 100
NAME_OVERLAP_MIN = 0.6
VERIFIED_SOURCE = "google_places"

# Accent-insensitive token stop-words: French articles/prepositions + a few EN.
# These carry no discriminating signal for a place name, so they're dropped
# before computing overlap (otherwise "Col de la Colombière" vs "Col Colombière"
# would be unfairly penalised by the missing "de la").
STOP = {
    "de", "la", "le", "les", "du", "des", "d", "l", "a", "au", "aux",
    "et", "en", "sur", "sous", "the", "of", "and",
}


def get_path(d, *path):
    """Nested dict lookup; returns None if any hop is missing."""
    cur = d
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def norm_tokens(s):
    """Accent-insensitive, lower-case alphanumeric tokens, minus stop-words."""
    if not s:
        return set()
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    toks = re.findall(r"[a-z0-9]+", s.lower())
    return {t for t in toks if t not in STOP}


def name_overlap(fiche_name, google_match):
    """Directional token coverage: fraction of fiche-name tokens present in the
    Google match name. 1.0 = our whole name is contained in theirs."""
    a = norm_tokens(fiche_name)
    b = norm_tokens(google_match)
    if not a:
        return 0.0
    return len(a & b) / len(a)


def fiche_name(d):
    """The canonical (frozen) place name: i18n.fr.name, then en, then slug.
    Mirrors build_lieu_page's L('name'); read-only here."""
    i18n = d.get("i18n", {}) or {}
    return (get_path(i18n, "fr", "name")
            or get_path(i18n, "en", "name")
            or d.get("slug"))


def resolve_signals(d):
    """Return (place_id, drift_m, google_match) with google_check > freshness
    precedence for place_id/drift, and google_match from whichever source has
    it (freshness carries it in practice)."""
    place_id = (get_path(d, "google_check", "place_id")
                or get_path(d, "freshness", "place_id"))
    drift = get_path(d, "google_check", "gps_drift_m")
    if drift is None:
        drift = get_path(d, "freshness", "gps_drift_m")
    match = (get_path(d, "freshness", "google_match")
             or get_path(d, "google_check", "google_match")
             or get_path(d, "google_check", "match"))
    return place_id, drift, match


def derive_one(d, max_drift):
    """Compute the desired derived state for a fiche. Returns a dict:
        {place_id, verified(bool), drift, overlap, match, name, reason}
    Pure — does not mutate d."""
    place_id, drift, match = resolve_signals(d)
    name = fiche_name(d)
    overlap = name_overlap(name, match) if match else 0.0

    verified = bool(place_id) and drift is not None and drift <= max_drift \
        and overlap >= NAME_OVERLAP_MIN

    if not place_id:
        reason = "no place_id"
    elif drift is None:
        reason = "no gps_drift_m"
    elif drift > max_drift:
        reason = f"drift {drift}m > {max_drift}m"
    elif not match:
        reason = "no google_match name"
    elif overlap < NAME_OVERLAP_MIN:
        reason = f"name-overlap {overlap:.2f} < {NAME_OVERLAP_MIN}"
    else:
        reason = "verified"

    return {
        "place_id": place_id, "verified": verified, "drift": drift,
        "overlap": overlap, "match": match, "name": name, "reason": reason,
    }


def apply_derived(d, info):
    """Mutate d to match the derived state. Returns list of field names touched
    (empty if already in the desired state — that's the idempotent no-op)."""
    touched = []

    # 1. google_place_id — written for every fiche that has a place_id.
    if info["place_id"]:
        if d.get("google_place_id") != info["place_id"]:
            d["google_place_id"] = info["place_id"]
            touched.append("google_place_id")
    elif "google_place_id" in d:
        del d["google_place_id"]
        touched.append("google_place_id")

    # 2. geo_verified bundle — earn-only; stripped when not earned (self-heal).
    verified_fields = ("geo_verified", "geo_verified_date",
                       "geo_verified_source", "geo_verified_drift_m")
    if info["verified"]:
        desired = {
            "geo_verified": True,
            # keep the existing date if the stamp already stands (don't churn
            # the audit date on every re-run); set it only when newly verified.
            "geo_verified_date": d.get("geo_verified_date") if d.get("geo_verified") is True else TODAY,
            "geo_verified_source": VERIFIED_SOURCE,
            "geo_verified_drift_m": info["drift"],
        }
        if desired["geo_verified_date"] is None:
            desired["geo_verified_date"] = TODAY
        for k, v in desired.items():
            if d.get(k) != v:
                d[k] = v
                touched.append(k)
    else:
        for k in verified_fields:
            if k in d:
                del d[k]
                touched.append(k)

    return touched


def stamp_log(d, touched, max_drift):
    rl = d.setdefault("research_log", [])
    verified = d.get("geo_verified") is True
    note = (f"derive_geo_verified: geo_verified={'true' if verified else 'false'} "
            f"(max_drift={max_drift}m).")
    rl.append({
        "date": TODAY,
        "by": "derive_geo_verified.py",
        "note": note,
        "fields": touched,
    })


def main():
    ap = argparse.ArgumentParser(description="Derive geo_verified from Google signals.")
    ap.add_argument("--max-drift", type=int, default=DEFAULT_MAX_DRIFT,
                    help=f"Max gps_drift_m to earn the stamp (default {DEFAULT_MAX_DRIFT}).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report only; write nothing.")
    ap.add_argument("--report-rejected", action="store_true",
                    help="Also list fiches with place_id & drift<=max that "
                         "failed ONLY on name-overlap (threshold eyeballing).")
    ap.add_argument("--json-dir", default=JSON_DIR)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.json_dir, "*.json")))
    if not files:
        print(f"::error::no fiches under {args.json_dir}/", file=sys.stderr)
        sys.exit(1)

    n_verified = 0
    n_pid = 0
    n_written = 0
    rejected_close = []   # place_id & drift<=max but name-overlap too weak
    verified_slugs = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        info = derive_one(d, args.max_drift)
        if info["place_id"]:
            n_pid += 1
        if info["verified"]:
            n_verified += 1
            verified_slugs.append(d.get("slug"))
        # near-miss: had a real shot (place_id + close enough) but name was weak
        if (info["place_id"] and info["drift"] is not None
                and info["drift"] <= args.max_drift
                and not info["verified"]
                and info["reason"].startswith("name-overlap")):
            rejected_close.append((d.get("slug"), info["name"], info["match"],
                                   info["drift"], info["overlap"]))

        touched = apply_derived(d, info)
        if touched:
            stamp_log(d, touched, args.max_drift)
            n_written += 1
            if not args.dry_run:
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump(d, fh, ensure_ascii=False, indent=2)
                    fh.write("\n")

    tag = "[dry-run] " if args.dry_run else ""
    print(f"{tag}derive_geo_verified (max_drift={args.max_drift}m):")
    print(f"  {len(files)} fiches scanned")
    print(f"  {n_pid} carry a place_id -> google_place_id written (pin-fix set)")
    print(f"  {n_verified} earn geo_verified:true  ✅")
    print(f"  {n_written} fiche file(s) {'would change' if args.dry_run else 'changed'}")

    if args.report_rejected and rejected_close:
        print(f"\n  rejected-but-close ({len(rejected_close)}): place_id + "
              f"drift<={args.max_drift}m, failed ONLY on name-overlap<{NAME_OVERLAP_MIN} —")
        print(f"  eyeball whether {NAME_OVERLAP_MIN} over-rejects generic names:")
        for slug, name, match, drift, ov in sorted(rejected_close, key=lambda r: r[4], reverse=True):
            print(f"    {ov:.2f}  drift={drift:>3}m  {name!r}  ~  {match!r}  [{slug}]")
    elif args.report_rejected:
        print(f"\n  rejected-but-close: none "
              f"(every place_id fiche within {args.max_drift}m also name-matched).")


if __name__ == "__main__":
    main()
