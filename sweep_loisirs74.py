#!/usr/bin/env python3
"""
sweep_loisirs74.py — Multi-source freshness & accuracy sweep for loisirs74 fiches.

THREE independent sources, triangulated:
  1. Google Places (New)      -> status, website, phone, hours, rating, name, GPS drift
  2. French registry (free)   -> legal status actif/fermé + closure date  (no key needed)
  3. Official site reachable? -> a dead domain is a strong "gone" signal
     + cheap price-candidate scan to FLAG fiches worth Claude Code's deeper look

It does NOT invent or auto-publish prices. Anything uncertain is written as a
candidate / needs_review and added to an email queue for owner confirmation.

OUTPUTS:
  - writes a "freshness" block into each fiche (provenance: source + date per fact)
  - report.csv      : every fiche, problems sorted to the top
  - email_queue.csv : only the fiches where sources DISAGREE or data is stale
                      (this is the list you actually email — not all 325)

NEEDS: GOOGLE_MAPS_API_KEY in the environment. The French registry needs no key.
"""

import os, sys, json, csv, time, math, glob, re, datetime, urllib.parse, urllib.request

API_KEY   = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
JSON_DIR  = os.environ.get("LOISIRS_JSON_DIR", "Json")
TODAY     = datetime.date.today().isoformat()
FORCE     = "--force" in sys.argv
NO_SITE   = "--no-site" in sys.argv      # skip official-site fetch if you want it faster

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.id","places.displayName","places.formattedAddress","places.businessStatus",
    "places.websiteUri","places.nationalPhoneNumber","places.rating","places.userRatingCount",
    "places.location","places.regularOpeningHours.weekdayDescriptions",
])
REGISTRY_URL = "https://recherche-entreprises.api.gouv.fr/search"

# Categories that are natural/free sites — absence from the business registry is
# NORMAL for these and must NOT be read as "closed".
NATURAL_CATS = {"cascade","cascades","lac","lacs","point-de-vue","points-de-vue",
                "voie-verte","voies-vertes","col","sommet","belvedere"}

PRICE_RE = re.compile(r"(\d{1,3}(?:[.,]\d{1,2})?)\s?€")


# ----------------------------------------------------------------------------- utils
def haversine_m(lat1, lon1, lat2, lon2):
    try:
        R=6371000.0; p1,p2=math.radians(lat1),math.radians(lat2)
        dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
        a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return round(R*2*math.atan2(math.sqrt(a),math.sqrt(1-a)))
    except Exception:
        return None

def name_of(f):  return (f.get("i18n",{}).get("fr",{}).get("name") or f.get("slug","")).strip()
def stamp(value, source): return {"value": value, "source": source, "verified": TODAY}


# ----------------------------------------------------------------------------- sources
def google_lookup(name, commune):
    q=f"{name} {commune} Haute-Savoie France".strip()
    body=json.dumps({"textQuery":q,"languageCode":"fr","regionCode":"FR","maxResultCount":1}).encode()
    req=urllib.request.Request(PLACES_URL,data=body,method="POST")
    req.add_header("Content-Type","application/json")
    req.add_header("X-Goog-Api-Key",API_KEY)
    req.add_header("X-Goog-FieldMask",FIELD_MASK)
    with urllib.request.urlopen(req,timeout=30) as r:
        data=json.loads(r.read().decode())
    pl=(data.get("places") or [None])[0]
    if not pl: return None
    loc=pl.get("location",{})
    return {
        "place_id":pl.get("id"),
        "match":pl.get("displayName",{}).get("text"),
        "status":pl.get("businessStatus","UNKNOWN"),
        "website":pl.get("websiteUri"),
        "phone":pl.get("nationalPhoneNumber"),
        "rating":pl.get("rating"),"rating_count":pl.get("userRatingCount"),
        "lat":loc.get("latitude"),"lng":loc.get("longitude"),
        "hours":(pl.get("regularOpeningHours",{}) or {}).get("weekdayDescriptions"),
    }

def registry_lookup(name, commune, postal):
    """Free French business registry. Returns actif/fermé or None (no match)."""
    params={"q":f"{name} {commune}","per_page":1}
    if postal: params["code_postal"]=str(postal)
    url=REGISTRY_URL+"?"+urllib.parse.urlencode(params)
    try:
        req=urllib.request.Request(url); req.add_header("Accept","application/json")
        with urllib.request.urlopen(req,timeout=30) as r:
            data=json.loads(r.read().decode())
    except Exception as e:
        return {"state":"ERROR","detail":str(e)}
    results=data.get("results") or []
    if not results: return {"state":"NO_MATCH"}
    top=results[0]
    etab=top.get("siege") or (top.get("matching_etablissements") or [{}])[0]
    etat=(etab.get("etat_administratif") or "").upper()   # "A" actif / "F" fermé
    return {
        "state":"ACTIF" if etat=="A" else ("FERME" if etat=="F" else "UNKNOWN"),
        "matched_name":top.get("nom_complet"),
        "siret":etab.get("siret"),
        "closure_date":etab.get("date_fermeture"),
    }

def site_check(url):
    """Is the official site alive? + cheap price candidates to flag for review."""
    if not url: return {"reachable":None,"price_candidates":[]}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"loisirs74-bot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:
            html=r.read(120000).decode("utf-8","ignore")
        cands=sorted(set(PRICE_RE.findall(html)))[:8]
        return {"reachable":True,"price_candidates":cands}
    except Exception as e:
        return {"reachable":False,"error":str(e),"price_candidates":[]}


# ----------------------------------------------------------------------------- core
def triangulate(cat, g, reg, site):
    """Combine the 3 sources into a status + confidence + reason for the email queue."""
    is_natural = (cat or "").lower() in NATURAL_CATS
    g_status   = (g or {}).get("status")
    reg_state  = (reg or {}).get("state")
    reachable  = (site or {}).get("reachable")

    # hard closed signals
    if g_status=="CLOSED_PERMANENTLY":
        return "CLOSED","high","Google marks permanently closed"
    if reg_state=="FERME":
        return "CLOSED","high",f"Registry marks fermé (date {reg.get('closure_date')})"

    # no google match at all
    if g is None:
        return "UNVERIFIED","low","No Google match — check the stored name"

    # disagreements / soft signals -> email candidates
    reasons=[]
    if reg_state=="NO_MATCH" and not is_natural:
        reasons.append("not found in business registry (commercial venue)")
    if reachable is False:
        reasons.append("official site not responding")
    if g_status=="CLOSED_TEMPORARILY":
        reasons.append("Google marks temporarily closed")
    if reasons:
        return "OPERATIONAL","medium","; ".join(reasons)

    return "OPERATIONAL","high",""

def priority(fr):
    s,c=fr["status"],fr["confidence"]
    if s=="CLOSED":        return 0
    if s=="UNVERIFIED":    return 1
    if c=="medium":        return 2
    if fr.get("gps_drift_m") and fr["gps_drift_m"]>300: return 3
    if not fr.get("website"): return 4
    return 9


def sweep_one(f):
    name,commune,postal,cat=name_of(f),f.get("commune"),f.get("postal_code"),f.get("category")
    try:    g=google_lookup(name,commune)
    except Exception as e: g={"error":str(e),"status":"ERROR"}
    reg = registry_lookup(name,commune,postal)
    site= {"reachable":None,"price_candidates":[]} if NO_SITE else site_check(f.get("official_site_url"))

    drift=None
    if g and g.get("lat") is not None and f.get("latitude") is not None:
        drift=haversine_m(float(f["latitude"]),float(f["longitude"]),float(g["lat"]),float(g["lng"]))

    status,conf,reason = triangulate(cat,g,reg,site)
    g=g or {}
    fr={
        "checked":TODAY,"status":status,"confidence":conf,"flag_reason":reason,
        "google_match":g.get("match"),"place_id":g.get("place_id"),
        "google_status":g.get("status"),
        "website":stamp(g.get("website"),"google") if g.get("website") else None,
        "phone":stamp(g.get("phone"),"google") if g.get("phone") else None,
        "hours":stamp(g.get("hours"),"google") if g.get("hours") else None,
        "rating":g.get("rating"),"rating_count":g.get("rating_count"),
        "registry":{"state":reg.get("state"),"siret":reg.get("siret"),
                    "closure_date":reg.get("closure_date")},
        "site_reachable":site.get("reachable"),
        "price_candidates":site.get("price_candidates"),   # NOT published — review only
        "gps_drift_m":drift,
        "needs_price_review": bool(site.get("price_candidates")) and not f.get("price_from"),
    }
    return fr


def main():
    if not API_KEY: sys.exit("ERROR: set GOOGLE_MAPS_API_KEY first.")
    files=sorted(glob.glob(os.path.join(JSON_DIR,"*.json")))
    if not files: sys.exit(f"ERROR: no .json in {JSON_DIR}/")
    print(f"Sweeping {len(files)} fiches across 3 sources...\n")

    rows=[]
    for i,path in enumerate(files,1):
        f=json.load(open(path,encoding="utf-8"))
        prev=f.get("freshness")
        if prev and prev.get("checked")==TODAY and not FORCE:
            fr=prev
        else:
            fr=sweep_one(f)
            f["freshness"]=fr
            json.dump(f,open(path,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
            time.sleep(0.2)
        rows.append((f.get("slug"),name_of(f),f.get("commune"),f.get("official_site_url"),fr))
        tag={"CLOSED":"❌ CLOSED","UNVERIFIED":"⚠️  no match"}.get(fr["status"],fr["confidence"])
        print(f"[{i:>3}/{len(files)}] {f.get('slug',''):<42} {tag}"
              + (f"  ← {fr['flag_reason']}" if fr['flag_reason'] else ""))

    rows.sort(key=lambda r:(priority(r[4]),r[0]))

    with open("report.csv","w",newline="",encoding="utf-8") as fp:
        w=csv.writer(fp)
        w.writerow(["slug","status","confidence","reason","google_match","registry",
                    "site_reachable","website","phone","rating","gps_drift_m","needs_price_review"])
        for slug,name,com,site_url,fr in rows:
            w.writerow([slug,fr["status"],fr["confidence"],fr["flag_reason"],fr.get("google_match"),
                        fr["registry"]["state"],fr.get("site_reachable"),
                        (fr.get("website") or {}).get("value") if fr.get("website") else "",
                        (fr.get("phone") or {}).get("value") if fr.get("phone") else "",
                        fr.get("rating"),fr.get("gps_drift_m"),fr.get("needs_price_review")])

    # email queue = closed/unverified/medium-confidence only (NOT all 325)
    with open("email_queue.csv","w",newline="",encoding="utf-8") as fp:
        w=csv.writer(fp); w.writerow(["slug","name","commune","status","reason","website","phone"])
        for slug,name,com,site_url,fr in rows:
            if fr["status"] in ("CLOSED","UNVERIFIED") or fr["confidence"]=="medium":
                w.writerow([slug,name,com,fr["status"],fr["flag_reason"],
                            (fr.get("website") or {}).get("value") if fr.get("website") else (site_url or ""),
                            (fr.get("phone") or {}).get("value") if fr.get("phone") else ""])

    closed=sum(1 for *_,fr in rows if fr["status"]=="CLOSED")
    unver =sum(1 for *_,fr in rows if fr["status"]=="UNVERIFIED")
    med   =sum(1 for *_,fr in rows if fr["confidence"]=="medium")
    price =sum(1 for *_,fr in rows if fr.get("needs_price_review"))
    print(f"\nDONE. {len(rows)} fiches.")
    print(f"  ❌ {closed} closed   ⚠️ {unver} unverified   ⚠️ {med} need owner confirm")
    print(f"  💶 {price} have price candidates on their site → Claude Code should extract & review")
    print(f"\n  report.csv       (everything, problems first)")
    print(f"  email_queue.csv  ({closed+unver+med} venues to contact — not all {len(rows)})")


if __name__=="__main__":
    main()
