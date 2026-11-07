#!/usr/bin/env python3
"""desk_export.py: the repo's state -> items.json, the owner's desk cards.

Run after every desk_apply and every build that changes places. The desk page
(a private Artifact) fetches items.json from beside itself, so republishing
this one file refreshes every card without touching the page's code.

    python3 scripts/desk_export.py --out <folder>/items.json

What it carries:
  places  every published place, ordered by demand (data/desk-demand.json):
          name, commune, category, photo status, position, and its pin. The
          position is the owner's pin when there is one, else the stored one.
          `search` is a Google Maps name search: the owner opens it to FIND the
          place, then pastes the place's own share link (a search is never a
          pin).
  calls   places Google Maps listed as closed when last checked
          (google_check.status CLOSED_TEMPORARILY / CLOSED_PERMANENTLY), each
          with the owner's answer when he has given one.

Pin statuses: "pinned" (his pin is in data/pins.json), "none".
Photo statuses: needs | unknown | own | commons (see the desk legend).
"""
import argparse
import datetime as dt
import json
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSED = {"CLOSED_TEMPORARILY": "temporarily closed", "CLOSED_PERMANENTLY": "permanently closed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pins = json.loads((ROOT / "data" / "pins.json").read_text(encoding="utf-8"))["pins"]
    calls_doc = ROOT / "data" / "desk-calls.json"
    answered = json.loads(calls_doc.read_text(encoding="utf-8"))["calls"] if calls_doc.exists() else {}
    demand = json.loads((ROOT / "data" / "desk-demand.json").read_text(encoding="utf-8"))["score"]
    markers = json.loads((ROOT / "data" / "own-photos.json").read_text(encoding="utf-8"))["credit_markers"]

    places, calls = [], []
    for f in sorted((ROOT / "Json").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("status") not in ("published", "verified"):
            continue
        slug = d["slug"]
        name = ((d.get("i18n") or {}).get("fr") or {}).get("name") or slug
        commune = d.get("commune") or ""
        hero, credit = d.get("hero_image") or "", d.get("hero_credit") or ""
        if any(m in credit for m in markers):
            photo = "own"
        elif not hero or "generique" in hero:
            photo = "needs"
        elif hero.startswith("/") and not credit:
            photo = "unknown"
        else:
            photo = "commons"
        pin = pins.get(slug) if (pins.get(slug) or {}).get("by") == "Eddie" else None
        lat, lon = d.get("latitude"), d.get("longitude")
        if pin and pin.get("lat") is not None:
            lat, lon = pin["lat"], pin["lon"]
        q = urllib.parse.quote(f"{name}, {commune}".strip(", "))
        places.append({
            "s": slug, "n": name, "c": commune, "k": d.get("category") or "",
            "st": photo, "cr": credit[:80],
            "lat": round(lat, 5) if lat is not None else None,
            "lon": round(lon, 5) if lon is not None else None,
            "pin": {"url": pin["url"], "on": pin.get("given_on")} if pin else None,
            "search": f"https://www.google.com/maps/search/?api=1&query={q}",
            "fame": demand.get(slug, 0),
        })
        gc = d.get("google_check") or {}
        if isinstance(gc, dict) and gc.get("status") in CLOSED:
            calls.append({
                "id": f"call:{slug}", "s": slug, "n": name, "c": commune,
                "said": CLOSED[gc["status"]], "checked": (gc.get("checked") or "")[:10],
                "answer": answered.get(slug),
                "fame": demand.get(slug, 0),
            })
    places.sort(key=lambda p: (-p["fame"], p["n"]))
    calls.sort(key=lambda c: (-c["fame"], c["n"]))
    out = {"generated_on": dt.date.today().isoformat(), "places": places, "calls": calls}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"desk export: {len(places)} places ({sum(1 for p in places if p['pin'])} pinned) · "
          f"{len(calls)} calls -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
