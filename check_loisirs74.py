#!/usr/bin/env python3
"""
check_loisirs74.py — Verifie chaque fiche loisirs74 contre Google Maps.

PRIMARY:  Is the place still operational?  Does it have a website?
BONUS:    Google rating, review count, opening hours, GPS drift vs stored coords.

- Reads every .json in ./Json
- Adds a "google_check" block to each fiche (NEVER touches your existing data)
- Writes report.csv, sorted so problems float to the top:
    CLOSED places first, then places with NO website, then everything else.
- Resumable: re-running skips fiches already checked today (use --force to redo).

Needs ONE thing from you: a Google Maps API key in the env var GOOGLE_MAPS_API_KEY.

ERROR ≠ DATA (HANDOFF-24). Every check ends in exactly one of three outcomes:
  OK               — the API answered with fresh data          → may update fields
  CONFIRMED_ABSENT — the API answered: place gone / no match   → may update fields
  CHECK_FAILED     — quota, auth, network: a fact about *us*,
                     not the place                             → keeps ALL previous
                     values; writes only last_check + check_failed.
Mass-failure circuit breaker: if more than FAIL_RATE_LIMIT of the calls in a
run fail, the whole run ABORTS before a single fiche is written and exits
non-zero. (2026-07-01: a dead API key produced a 100%-failure run that
overwrote 397 fiches — the breaker makes that impossible.)
"""

import os, sys, json, csv, time, math, glob, datetime

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
JSON_DIR = os.environ.get("LOISIRS_JSON_DIR", "Json")
REPORT = os.environ.get("LOISIRS_REPORT", "report.csv")
FORCE = "--force" in sys.argv
TODAY = datetime.date.today().isoformat()
FAIL_RATE_LIMIT = 0.10   # >10% of calls failing aborts the run, zero writes

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.businessStatus", "places.websiteUri",
    "places.rating", "places.userRatingCount",
    "places.location", "places.regularOpeningHours.weekdayDescriptions",
])


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lng points."""
    try:
        R = 6371000.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))
    except Exception:
        return None


def query_google(text_query):
    """Call Google Places Text Search. Returns the top place dict or None."""
    import urllib.request
    body = json.dumps({"textQuery": text_query, "languageCode": "fr",
                       "regionCode": "FR", "maxResultCount": 1}).encode()
    req = urllib.request.Request(PLACES_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Goog-Api-Key", API_KEY)
    req.add_header("X-Goog-FieldMask", FIELD_MASK)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    places = data.get("places") or []
    return places[0] if places else None


def build_query(fiche):
    name = (fiche.get("i18n", {}).get("fr", {}).get("name")
            or fiche.get("slug", "")).strip()
    commune = (fiche.get("commune") or "").strip()
    return f"{name} {commune} Haute-Savoie France".strip()


def failed_check(prev, query, reason):
    """CHECK_FAILED — the call failed, so we learned nothing about the place.
    Keep every previously-verified value; record only that the check failed.
    `checked` keeps its old date (last SUCCESSFUL check), so a same-day rerun
    retries instead of skipping."""
    gc = dict(prev or {})
    gc.setdefault("query", query)
    gc["last_check"] = TODAY
    gc["check_failed"] = reason
    gc["outcome"] = "CHECK_FAILED"
    return gc


def check_one(fiche):
    """Returns the google_check dict for one fiche.
    Raises on any API/network failure — the caller classifies that as
    CHECK_FAILED and must not let it touch existing data."""
    q = build_query(fiche)
    place = query_google(q)
    if not place:
        return {"checked": TODAY, "query": q, "match": None,
                "status": "NO_MATCH", "outcome": "CONFIRMED_ABSENT",
                "website": None,
                "rating": None, "rating_count": None,
                "hours": None, "gps_drift_m": None,
                "stored_website": fiche.get("official_site_url")}

    loc = place.get("location", {})
    glat, glng = loc.get("latitude"), loc.get("longitude")
    drift = None
    if glat is not None and fiche.get("latitude") is not None:
        drift = haversine_m(float(fiche["latitude"]), float(fiche["longitude"]),
                            float(glat), float(glng))
    hours = (place.get("regularOpeningHours", {}) or {}).get("weekdayDescriptions")
    status = place.get("businessStatus", "UNKNOWN")
    return {
        "checked": TODAY,
        "query": q,
        "match": place.get("displayName", {}).get("text"),
        "place_id": place.get("id"),
        "status": status,
        "outcome": "CONFIRMED_ABSENT" if status == "CLOSED_PERMANENTLY" else "OK",
        "website": place.get("websiteUri"),
        "stored_website": fiche.get("official_site_url"),
        "rating": place.get("rating"),
        "rating_count": place.get("userRatingCount"),
        "hours": hours,
        "google_lat": glat, "google_lng": glng,
        "gps_drift_m": drift,
    }


# ---- priority for sorting the report: smaller number = more urgent ----
def priority(gc):
    s = gc.get("status")
    if s == "CLOSED_PERMANENTLY": return 0
    if s == "NO_MATCH":           return 1
    if s == "CLOSED_TEMPORARILY": return 2
    if not gc.get("website"):     return 3   # operational but no website found
    if (gc.get("gps_drift_m") or 0) > 300:   return 4   # big GPS mismatch
    return 9


def abort_run(failed, attempted):
    """Mass-failure circuit breaker tripped: nothing was written."""
    print(f"\n🔴 CIRCUIT BREAKER: {failed}/{attempted} calls failed "
          f"(> {int(FAIL_RATE_LIMIT*100)}% limit).")
    print("A mass failure is a fact about the checker (dead key, quota, network),")
    print("not about the venues. ZERO fiches were written. Fix the key and rerun.")
    sys.exit(2)


def main():
    if not API_KEY:
        sys.exit("ERROR: set GOOGLE_MAPS_API_KEY first. See setup notes.")

    files = sorted(glob.glob(os.path.join(JSON_DIR, "*.json")))
    if not files:
        sys.exit(f"ERROR: no .json files found in {JSON_DIR}/")

    print(f"Found {len(files)} fiches. Checking against Google...\n")
    # Phase 1 — check everything IN MEMORY. Nothing touches disk until the
    # whole run has passed the mass-failure circuit breaker.
    fail_budget = max(1, int(len(files) * FAIL_RATE_LIMIT))
    failed = attempted = 0
    results = []   # (path, fiche, gc, fresh) — fresh means checked this run
    for i, path in enumerate(files, 1):
        with open(path, encoding="utf-8") as f:
            fiche = json.load(f)

        existing = fiche.get("google_check")
        if existing and existing.get("checked") == TODAY and not FORCE:
            gc, fresh, tag = existing, False, "skip"
        else:
            attempted += 1
            fresh = True
            try:
                gc = check_one(fiche)
                tag = gc.get("status")
            except Exception as e:
                failed += 1
                gc = failed_check(existing, build_query(fiche), str(e))
                tag = "CHECK_FAILED"

        results.append((path, fiche, gc, fresh))
        flag = ""
        if gc.get("outcome") == "CHECK_FAILED":       flag = "  🔌 check failed (kept previous data)"
        elif gc.get("status") == "CLOSED_PERMANENTLY": flag = "  ❌ CLOSED"
        elif gc.get("status") == "NO_MATCH":          flag = "  ⚠️  no match"
        elif not gc.get("website"):                   flag = "  ⚠️  no website"
        print(f"[{i:>3}/{len(files)}] {fiche.get('slug',''):<45} {tag}{flag}")

        if failed > fail_budget:
            abort_run(failed, attempted)
        if fresh:
            time.sleep(0.15)  # be gentle on the API

    if attempted and failed / attempted > FAIL_RATE_LIMIT:
        abort_run(failed, attempted)

    # Phase 2 — breaker passed: now (and only now) write the fiches.
    rows = []
    for path, fiche, gc, fresh in results:
        if fresh:
            fiche["google_check"] = gc
            with open(path, "w", encoding="utf-8") as f:
                json.dump(fiche, f, ensure_ascii=False, indent=2)
                f.write("\n")   # repo convention: fiches end with a newline
        rows.append((fiche.get("slug", os.path.basename(path)), gc))
    if failed:
        print(f"\n⚠️  {failed}/{attempted} checks failed (under the breaker limit): "
              "those fiches kept ALL previous values, only last_check/check_failed were stamped.")

    rows.sort(key=lambda r: (priority(r[1]), r[0]))
    with open(REPORT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["slug", "status", "google_match", "website_found",
                    "stored_website", "rating", "reviews", "gps_drift_m", "hours"])
        for slug, gc in rows:
            w.writerow([
                slug, gc.get("status"), gc.get("match"),
                gc.get("website"), gc.get("stored_website"),
                gc.get("rating"), gc.get("rating_count"),
                gc.get("gps_drift_m"),
                " | ".join(gc.get("hours") or []),
            ])

    closed = sum(1 for _, g in rows if g.get("status") == "CLOSED_PERMANENTLY")
    nomatch = sum(1 for _, g in rows if g.get("status") == "NO_MATCH")
    noweb = sum(1 for _, g in rows if g.get("status") not in
                ("CLOSED_PERMANENTLY", "NO_MATCH") and not g.get("website"))
    print(f"\nDONE. {len(rows)} fiches checked.")
    print(f"  ❌ {closed} permanently closed")
    print(f"  ⚠️  {nomatch} no Google match (check the name)")
    print(f"  ⚠️  {noweb} operational but no website found")
    print(f"\nFull report → {REPORT} (problems sorted to the top)")


if __name__ == "__main__":
    main()
