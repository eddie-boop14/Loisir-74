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
"""

import os, sys, json, csv, time, math, glob, datetime

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
JSON_DIR = os.environ.get("LOISIRS_JSON_DIR", "Json")
REPORT = os.environ.get("LOISIRS_REPORT", "report.csv")
FORCE = "--force" in sys.argv
TODAY = datetime.date.today().isoformat()

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


def check_one(fiche):
    """Returns the google_check dict for one fiche."""
    q = build_query(fiche)
    place = query_google(q)
    if not place:
        return {"checked": TODAY, "query": q, "match": None,
                "status": "NO_MATCH", "website": None,
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
    return {
        "checked": TODAY,
        "query": q,
        "match": place.get("displayName", {}).get("text"),
        "place_id": place.get("id"),
        "status": place.get("businessStatus", "UNKNOWN"),
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


def main():
    if not API_KEY:
        sys.exit("ERROR: set GOOGLE_MAPS_API_KEY first. See setup notes.")

    files = sorted(glob.glob(os.path.join(JSON_DIR, "*.json")))
    if not files:
        sys.exit(f"ERROR: no .json files found in {JSON_DIR}/")

    print(f"Found {len(files)} fiches. Checking against Google...\n")
    rows = []
    for i, path in enumerate(files, 1):
        with open(path, encoding="utf-8") as f:
            fiche = json.load(f)

        existing = fiche.get("google_check")
        if existing and existing.get("checked") == TODAY and not FORCE:
            gc = existing
            tag = "skip"
        else:
            try:
                gc = check_one(fiche)
            except Exception as e:
                gc = {"checked": TODAY, "status": "ERROR",
                      "query": build_query(fiche), "error": str(e),
                      "website": None, "stored_website": fiche.get("official_site_url")}
            fiche["google_check"] = gc
            with open(path, "w", encoding="utf-8") as f:
                json.dump(fiche, f, ensure_ascii=False, indent=2)
            tag = gc.get("status")
            time.sleep(0.15)  # be gentle on the API

        rows.append((fiche.get("slug", os.path.basename(path)), gc))
        flag = ""
        if gc.get("status") == "CLOSED_PERMANENTLY": flag = "  ❌ CLOSED"
        elif gc.get("status") == "NO_MATCH":          flag = "  ⚠️  no match"
        elif not gc.get("website"):                   flag = "  ⚠️  no website"
        print(f"[{i:>3}/{len(files)}] {fiche.get('slug',''):<45} {tag}{flag}")

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
