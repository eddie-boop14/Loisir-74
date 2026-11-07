#!/usr/bin/env python3
"""desk_apply.py: the owner's desk answers -> data/pins.json + data/desk-calls.json.

Run when the owner says "apply the desk". Claude first saves the desk's
`answers` collection as JSON files (ArtifactData list, out_dir), then:

    python3 scripts/desk_apply.py --answers <dir>/answers            # report only
    python3 scripts/desk_apply.py --answers <dir>/answers --apply

Each answer is one document whose id names its card, and that id never changes:
    pin:<slug>   {kind:"pin",  slug, pin_url (whatever he pasted), at}
    call:<slug>  {kind:"call", slug, answer: open|closed|unsure, text?, at}

PINS (ruling, 7 Nov 2026: "real pin, not random coords from an API")
  A real pin is a link Google Maps resolves to ONE place: a share link
  (maps.app.goo.gl, goo.gl/maps), a /maps/place/ URL, or a ?cid= link. A name
  search (/maps/search/) is a list of guesses and is refused. Guards, each from
  the OfficialLink playbook:
    - two links in one field: the first real one is the pin;
    - one link given to two places: refused for both, both cards stay open;
    - a link that is already another place's pin: refused;
    - the same link again: unchanged (applying twice changes nothing).
  The link is followed (a plain redirect, with a declared user agent) to the
  place it opens. Google's label for that place is stored ("Lac Blanc, 74400
  Chamonix"): routes go to it. Share links carry no coordinates, and reading
  them out of Google's page would mean scraping it, which we do not do; when a
  /maps/place/ link does carry !3d…!4d… or @lat,lon, those are stored too. A pin outside
  Haute-Savoie's bounding box is refused, because it is almost certainly a
  paste for the wrong place. A pin more than 15 km from the stored position is
  kept but flagged in the report.

CALLS
  The answer is recorded in data/desk-calls.json. Nothing about the place's
  page changes by itself: an answer "closed" is a question for the next run,
  which shows it to Claude rather than unpublishing anything.

Writes a JSON report (--report) listing every answer as applied, unchanged or
refused, with the reason. Claude marks the desk cards from it.
"""
import argparse
import datetime as dt
import json
import math
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINS = ROOT / "data" / "pins.json"
CALLS = ROOT / "data" / "desk-calls.json"
REAL_PIN = re.compile(r"^https?://(?:maps\.app\.goo\.gl/|goo\.gl/maps/|(?:www\.)?google\.[a-z.]+/maps/place/|maps\.google\.[a-z.]+/\?cid=)", re.I)
NAME_SEARCH = re.compile(r"^https?://(?:www\.)?google\.[a-z.]+/maps/search/", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"']+")
BBOX = (45.65, 46.48, 5.78, 7.05)   # Haute-Savoie with a small margin
FAR_KM = 15
UA = "Mozilla/5.0 (loisirs74.fr desk; owner-given pin check)"


def load_answer(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    body = doc.get("data") if isinstance(doc.get("data"), dict) and "kind" not in doc else doc
    body = dict(body)
    body.setdefault("_id", doc.get("id") or path.stem)
    return body


def first_real(text):
    urls = [u.rstrip(").,;") for u in URL_RE.findall(text or "")]
    real = [u for u in urls if REAL_PIN.match(u)]
    if real:
        return real[0], None
    if any(NAME_SEARCH.match(u) for u in urls):
        return None, "a name search, not a pin: open the place itself and copy its Share link"
    return None, "no Google Maps link found"


def follow(url):
    """The place URL a pin link opens, following redirects and Google's consent wall."""
    for _ in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            final = r.geturl()
        q = urllib.parse.parse_qs(urllib.parse.urlparse(final).query)
        if "consent." in final and q.get("continue"):
            url = q["continue"][0]
            continue
        return final
    return url


def coords_from(url):
    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if not m:
        m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    return (round(float(m.group(1)), 6), round(float(m.group(2)), 6)) if m else (None, None)


def label_from(url):
    """Google's own label for the pinned place: the /maps/place/<label>/ segment
    of the URL the share link opens ("Lac Blanc, 74400 Chamonix")."""
    m = re.search(r"/maps/place/([^/?#]+)", url or "")
    return urllib.parse.unquote_plus(m.group(1)).strip() if m else None


def clean(url):
    """A share link without its tracking query (?g_st=…): same place, stable key."""
    return url.split("?")[0] if "maps.app.goo.gl" in url or "goo.gl/maps" in url else url


def km(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def norm(u):
    return u.split("?")[0].rstrip("/") if "maps.app.goo.gl" in u or "goo.gl/maps" in u else u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="folder of saved answers/*.json")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", default=None, help="write the JSON report here")
    ap.add_argument("--no-network", action="store_true", help="skip following links (tests)")
    args = ap.parse_args()

    pins_doc = json.loads(PINS.read_text(encoding="utf-8"))
    pins = pins_doc["pins"]
    held = pins_doc.setdefault("held", {})   # the owner's holds: same link never re-applied
    calls_doc = (json.loads(CALLS.read_text(encoding="utf-8")) if CALLS.exists()
                 else {"_note": "Owner's answers to the desk's call cards (\"Still open?\"), written by scripts/desk_apply.py. A record, not an action: nothing is unpublished from here.", "calls": {}})
    known = {p.stem for p in (ROOT / "Json").glob("*.json")}
    stored = {}
    for s in known:
        d = json.loads((ROOT / "Json" / f"{s}.json").read_text(encoding="utf-8"))
        stored[s] = (d.get("latitude"), d.get("longitude"))

    answers = [load_answer(p) for p in sorted(Path(args.answers).glob("*.json"))]
    report, today = [], dt.date.today().isoformat()

    # pass 1: which pin link each answer gives, to catch one link given twice
    given = {}
    for a in answers:
        if a.get("kind") == "pin":
            url, why = first_real(a.get("pin_url"))
            a["_url"], a["_why"] = url, why
            if url:
                given.setdefault(norm(url), []).append(a.get("slug"))

    for a in answers:
        aid, kind, slug = a["_id"], a.get("kind"), a.get("slug")
        on = str(a.get("at") or today)[:10] if not isinstance(a.get("at"), (int, float)) \
            else dt.datetime.fromtimestamp(a["at"] / 1000, dt.timezone.utc).date().isoformat()
        if slug not in known:
            report.append({"id": aid, "result": "refused", "why": f"unknown place {slug!r}"}); continue
        if kind == "pin":
            url = a["_url"]
            if not url:
                report.append({"id": aid, "result": "refused", "why": a["_why"]}); continue
            if len(set(given[norm(url)])) > 1:
                report.append({"id": aid, "result": "refused",
                               "why": "the same link was given to " + ", ".join(sorted(set(given[norm(url)])))}); continue
            owner = next((s for s, p in pins.items() if s != slug and norm(p.get("url", "")) == norm(url)), None)
            if owner:
                report.append({"id": aid, "result": "refused", "why": f"already the pin of {owner}"}); continue
            hold = held.get(slug)
            if hold and norm(hold.get("url", "")) == norm(url):
                report.append({"id": aid, "result": "unchanged", "note": "on hold: " + hold.get("why", "")}); continue
            cur = pins.get(slug)
            if cur and norm(cur.get("url", "")) == norm(url):
                report.append({"id": aid, "result": "unchanged"}); continue
            lat = lon = None
            resolved = None
            if not args.no_network:
                try:
                    resolved = follow(url)
                    lat, lon = coords_from(resolved)
                except Exception as e:  # noqa: BLE001
                    report.append({"id": aid, "result": "refused", "why": f"the link did not open ({e.__class__.__name__}); copy it again from Google Maps"}); continue
            if lat is not None and not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lon <= BBOX[3]):
                report.append({"id": aid, "result": "refused", "why": f"the pin is outside Haute-Savoie ({lat}, {lon}): probably another place"}); continue
            entry = {"url": clean(url), "given_on": on, "by": "Eddie"}
            if resolved:
                entry["resolved"] = resolved.split("?")[0]
                lab = label_from(resolved)
                if lab:
                    entry["label"] = lab
            if lat is not None:
                entry["lat"], entry["lon"] = lat, lon
            if cur:
                entry["replaces"] = cur["url"]
            note = ""
            slat, slon = stored.get(slug, (None, None))
            if lat is not None and slat is not None and km(lat, lon, slat, slon) > FAR_KM:
                note = f"pin is {km(lat, lon, slat, slon):.0f} km from the old position: check it is the right place"
            elif lat is None and not entry.get("label") and not args.no_network:
                note = "the link opened no place page: map buttons use the link, routes keep the old target"
            pins[slug] = entry
            held.pop(slug, None)   # a new link from him replaces the hold
            report.append({"id": aid, "result": "applied", **({"note": note} if note else {})})
        elif kind == "call":
            ans = (a.get("answer") or "").strip()
            if ans not in ("open", "closed", "unsure"):
                report.append({"id": aid, "result": "refused", "why": "no answer picked"}); continue
            rec = {"answer": ans, "on": on, **({"text": a["text"]} if a.get("text") else {})}
            if calls_doc["calls"].get(slug, {}).get("answer") == ans and calls_doc["calls"][slug].get("text") == rec.get("text"):
                report.append({"id": aid, "result": "unchanged"}); continue
            calls_doc["calls"][slug] = rec
            report.append({"id": aid, "result": "applied"})
        else:
            report.append({"id": aid, "result": "skipped", "why": f"kind {kind!r} is read by Claude, not applied"})

    applied = sum(r["result"] == "applied" for r in report)
    if args.apply and applied:
        pins_doc["pins"] = dict(sorted(pins.items()))
        pins_doc["held"] = dict(sorted(held.items()))
        PINS.write_text(json.dumps(pins_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        calls_doc["calls"] = dict(sorted(calls_doc["calls"].items()))
        CALLS.write_text(json.dumps(calls_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {k: sum(r["result"] == k for r in report) for k in ("applied", "unchanged", "refused", "skipped")}
    print(f"desk apply: {len(answers)} answers · " + " · ".join(f"{v} {k}" for k, v in counts.items())
          + f" [{'applied' if args.apply else 'dry run'}] · {len(pins)} pins")
    for r in report:
        if r["result"] in ("refused",) or r.get("note"):
            print(f"  {r['id']}: {r.get('why') or r.get('note')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
