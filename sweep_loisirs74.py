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

ERROR ≠ DATA (HANDOFF-24). Every Google lookup ends in exactly one of three
outcomes:
  OK               — the API answered with fresh data          → may update fields
  CONFIRMED_ABSENT — the API answered: place gone / no match   → may update fields
  CHECK_FAILED     — quota, auth, network: a fact about *us*,
                     not the place                             → keeps the WHOLE
                     previous freshness block; writes only last_check + check_failed.
Mass-failure circuit breaker: if more than FAIL_RATE_LIMIT of the Google calls
in a run fail, the whole run ABORTS before a single fiche is written and exits
non-zero. (2026-07-01: a dead API key produced a 100%-failure run that
overwrote 397 fiches — the breaker makes that impossible.)

Reachability discipline: a failed site fetch is only an OBSERVATION. A venue
is written site_reachable=false only after a SECOND failed fetch on a LATER
day (site_unreachable_confirmed). And if >FAIL_RATE_LIMIT of the site fetches
in one run fail, the whole reachability signal for the run is discarded as a
checker failure (42 venues don't go dark the same morning — 2026-07-01 again).
A registry error likewise keeps the previous registry block.
"""

import os, sys, json, csv, time, math, glob, re, datetime, urllib.parse, urllib.request

API_KEY   = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
JSON_DIR  = os.environ.get("LOISIRS_JSON_DIR", "Json")
TODAY     = datetime.date.today().isoformat()
FORCE     = "--force" in sys.argv
NO_SITE   = "--no-site" in sys.argv      # skip official-site fetch if you want it faster
FAIL_RATE_LIMIT = 0.10   # >10% failed Google calls aborts; >10% failed site fetches
                         # discards the run's reachability signal

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
    """Triangulate the 3 sources into status + confidence + reason.

    Google is the SOLE status oracle. Registry can only CONFIRM what
    Google found — it cannot close anything by itself. Natural categories
    (cascades, lakes, viewpoints, ...) ignore the registry entirely.
    Registry NO_MATCH is meaningless without SIRET context and is never
    a flag.
    """
    is_natural = (cat or "").lower() in NATURAL_CATS
    g_status   = (g or {}).get("status")
    reg_state  = (reg or {}).get("state") if not is_natural else None
    reachable  = (site or {}).get("reachable")

    # No Google match at all → can't verify (registry can't fill this gap)
    if g is None or g_status in (None, "ERROR"):
        return "UNVERIFIED", "low", "No Google match — check the stored name"

    # Google is the status oracle. Only Google can close a venue.
    if g_status == "CLOSED_PERMANENTLY":
        # Registry agreement raises confidence on the closure
        if reg_state == "FERME":
            closure = reg.get("closure_date") or "unknown date"
            return "CLOSED", "high", f"Google + registry agree (fermé {closure})"
        return "CLOSED", "medium", "Google marks permanently closed (registry didn't confirm)"

    # Everything else is operational. Registry / site signals only adjust
    # confidence or add review flags — never close.
    reasons = []
    confidence = "high"

    if g_status == "CLOSED_TEMPORARILY":
        reasons.append("Google marks temporarily closed")
        confidence = "medium"

    # Registry as a noise-aware confirmer:
    # - ACTIF: silent agreement, keeps high confidence
    # - FERME while Google operational: stale SIRET noise — flag for review
    # - NO_MATCH: meaningless without SIRET context; DROPPED entirely
    # - None/ERROR/UNKNOWN: no signal
    # Natural categories never consult the registry.
    if not is_natural and reg_state == "FERME":
        closure = reg.get("closure_date") or "unknown date"
        reasons.append(
            f"Registry shows fermé ({closure}) but Google says operational — "
            "likely stale SIRET match, verify")
        confidence = "medium"

    if reachable is False:
        reasons.append("Official site not responding")
        if confidence == "high":
            confidence = "medium"

    return "OPERATIONAL", confidence, "; ".join(reasons)

def priority(fr):
    s,c=fr.get("status"),fr.get("confidence")
    if s=="CLOSED":        return 0
    if s=="UNVERIFIED":    return 1
    if c=="medium":        return 2
    if fr.get("gps_drift_m") and fr["gps_drift_m"]>300: return 3
    if not fr.get("website"): return 4
    return 9


def observe_one(f):
    """Phase 1 — network only. Gathers raw observations for one fiche;
    nothing is classified or written until the whole run has passed the
    mass-failure circuit breaker.

    On a Google failure we learn NOTHING about the place, so we skip the
    other sources too: the fiche's update will be a pure no-op merge."""
    name,commune,postal=name_of(f),f.get("commune"),f.get("postal_code")
    try:
        g=google_lookup(name,commune)          # dict, or None = API answered: no match
    except Exception as e:
        return {"google":None,"google_failed":str(e),"registry":None,"site":None}
    reg = registry_lookup(name,commune,postal) # errors internally → {"state":"ERROR"}
    site= {"reachable":None,"price_candidates":[]} if NO_SITE else site_check(f.get("official_site_url"))
    return {"google":g,"google_failed":None,"registry":reg,"site":site}


def build_freshness(f, prev, obs, site_run_broken):
    """Phase 2 — classify one fiche's observations into its freshness block.

    ERROR ≠ DATA: CHECK_FAILED keeps every previous value. Only an answered
    API (OK / CONFIRMED_ABSENT) may change content-bearing fields."""
    prev = prev or {}

    # -- Google failed → the whole update is a no-op merge -------------------
    if obs["google_failed"] is not None:
        fr = dict(prev)
        fr["last_check"] = TODAY
        fr["check_failed"] = f"google: {obs['google_failed']}"
        fr["outcome"] = "CHECK_FAILED"
        return fr

    g, reg, site = obs["google"], obs["registry"], obs["site"]
    cat = f.get("category")

    # -- registry: an errored lookup keeps the previous registry block -------
    registry_failed = (reg or {}).get("state") == "ERROR"
    if registry_failed:
        registry_block = dict(prev.get("registry") or
                              {"state": None, "siret": None, "closure_date": None})
        reg_for_triangulation = {"state": registry_block.get("state"),
                                 "closure_date": registry_block.get("closure_date")}
    else:
        registry_block = {"state": reg.get("state"), "siret": reg.get("siret"),
                          "closure_date": reg.get("closure_date")}
        reg_for_triangulation = reg

    # -- reachability: observation now, verdict only on a 2nd bad day --------
    raw_reach = (site or {}).get("reachable")
    prev_reach = prev.get("site_reachable")
    prev_unreach_on = prev.get("site_last_unreachable")
    site_check_failed = None
    unreach_confirmed = False
    last_unreach = None
    if raw_reach is False and site_run_broken:
        # >10% of this run's fetches failed: the checker is broken, not the web
        reach = prev_reach
        last_unreach = prev_unreach_on
        unreach_confirmed = bool(prev.get("site_unreachable_confirmed"))
        site_check_failed = ("run-level breaker: >10% of site fetches failed "
                             "this run — observation discarded")
    elif raw_reach is False:
        last_unreach = TODAY
        if prev_unreach_on and prev_unreach_on < TODAY:
            reach = False               # second failed fetch on a later day
            unreach_confirmed = True
        else:
            reach = prev_reach          # first sighting: remember it, don't flag
    elif raw_reach is True:
        reach = True
    else:                               # no URL / --no-site: keep what we knew
        reach = prev_reach
        last_unreach = prev_unreach_on
        unreach_confirmed = bool(prev.get("site_unreachable_confirmed"))

    drift=None
    if g and g.get("lat") is not None and f.get("latitude") is not None:
        drift=haversine_m(float(f["latitude"]),float(f["longitude"]),float(g["lat"]),float(g["lng"]))

    status,conf,reason = triangulate(cat, g, reg_for_triangulation,
                                     {"reachable": reach})
    outcome = ("CONFIRMED_ABSENT"
               if (g is None or (g or {}).get("status") == "CLOSED_PERMANENTLY")
               else "OK")
    g=g or {}
    fr={
        "checked":TODAY,"status":status,"confidence":conf,"flag_reason":reason,
        "outcome":outcome,
        "google_match":g.get("match"),"place_id":g.get("place_id"),
        "google_status":g.get("status"),
        "website":stamp(g.get("website"),"google") if g.get("website") else None,
        "phone":stamp(g.get("phone"),"google") if g.get("phone") else None,
        "hours":stamp(g.get("hours"),"google") if g.get("hours") else None,
        "rating":g.get("rating"),"rating_count":g.get("rating_count"),
        "registry":registry_block,
        "site_reachable":reach,
        "price_candidates":(site or {}).get("price_candidates") or [],  # NOT published — review only
        "gps_drift_m":drift,
        "needs_price_review": bool((site or {}).get("price_candidates")) and not f.get("price_from"),
    }
    if last_unreach:
        fr["site_last_unreachable"] = last_unreach
    if unreach_confirmed:
        fr["site_unreachable_confirmed"] = True
    if registry_failed:
        fr["registry_check_failed"] = (reg or {}).get("detail") or "registry lookup error"
    if site_check_failed:
        fr["site_check_failed"] = site_check_failed
    return fr


def abort_run(failed, attempted):
    """Mass-failure circuit breaker tripped: nothing was written."""
    print(f"\n🔴 CIRCUIT BREAKER: {failed}/{attempted} Google calls failed "
          f"(> {int(FAIL_RATE_LIMIT*100)}% limit).")
    print("A mass failure is a fact about the checker (dead key, quota, network),")
    print("not about the venues. ZERO fiches were written. Fix the key and rerun.")
    sys.exit(2)


def main():
    if not API_KEY: sys.exit("ERROR: set GOOGLE_MAPS_API_KEY first.")
    files=sorted(glob.glob(os.path.join(JSON_DIR,"*.json")))
    if not files: sys.exit(f"ERROR: no .json in {JSON_DIR}/")
    print(f"Sweeping {len(files)} fiches across 3 sources...\n")

    # Phase 1 — observe everything IN MEMORY; abort before any write if the
    # Google failure rate trips the breaker.
    fail_budget=max(1,int(len(files)*FAIL_RATE_LIMIT))
    g_failed=attempted=0
    staged=[]   # (path, fiche, prev, obs)  obs=None → skipped (already checked today)
    for i,path in enumerate(files,1):
        f=json.load(open(path,encoding="utf-8"))
        prev=f.get("freshness")
        if prev and prev.get("checked")==TODAY and not FORCE:
            staged.append((path,f,prev,None))
            print(f"[{i:>3}/{len(files)}] {f.get('slug',''):<42} skip")
            continue
        attempted+=1
        obs=observe_one(f)
        if obs["google_failed"] is not None:
            g_failed+=1
            print(f"[{i:>3}/{len(files)}] {f.get('slug',''):<42} 🔌 CHECK_FAILED ({obs['google_failed']})")
            if g_failed>fail_budget:
                abort_run(g_failed,attempted)
        else:
            print(f"[{i:>3}/{len(files)}] {f.get('slug',''):<42} observed")
        staged.append((path,f,prev,obs))
        time.sleep(0.2)
    if attempted and g_failed/attempted>FAIL_RATE_LIMIT:
        abort_run(g_failed,attempted)

    # Run-level reachability breaker: if >10% of the fetches failed, the
    # checker (or the runner's network) is broken — 42 venues don't go dark
    # the same morning. Discard the whole run's reachability signal.
    site_obs=[o for _,_,_,o in staged
              if o and o["google_failed"] is None and (o["site"] or {}).get("reachable") is not None]
    site_down=sum(1 for o in site_obs if o["site"]["reachable"] is False)
    site_run_broken=bool(site_obs) and site_down/len(site_obs)>FAIL_RATE_LIMIT
    if site_run_broken:
        print(f"\n⚠️  reachability breaker: {site_down}/{len(site_obs)} site fetches failed "
              "— discarding this run's reachability observations (checker failure, not the web)")

    # Phase 2 — breaker passed: classify + write.
    rows=[]
    for path,f,prev,obs in staged:
        if obs is None:
            fr=prev
        else:
            fr=build_freshness(f,prev,obs,site_run_broken)
            f["freshness"]=fr
            with open(path,"w",encoding="utf-8") as fp:
                json.dump(f,fp,ensure_ascii=False,indent=2)
                fp.write("\n")   # repo convention: fiches end with a newline
        rows.append((f.get("slug"),name_of(f),f.get("commune"),f.get("official_site_url"),fr))
        tag={"CLOSED":"❌ CLOSED","UNVERIFIED":"⚠️  no match"}.get(fr.get("status"),fr.get("confidence"))
        if fr.get("outcome")=="CHECK_FAILED": tag="🔌 kept previous data"
        print(f"[   ] {f.get('slug',''):<42} {tag}"
              + (f"  ← {fr.get('flag_reason')}" if fr.get('flag_reason') else ""))
    if g_failed:
        print(f"\n⚠️  {g_failed}/{attempted} Google checks failed (under the breaker limit): "
              "those fiches kept their WHOLE previous freshness block, "
              "only last_check/check_failed were stamped.")

    rows.sort(key=lambda r:(priority(r[4]),r[0]))

    with open("report.csv","w",newline="",encoding="utf-8") as fp:
        w=csv.writer(fp)
        w.writerow(["slug","status","confidence","reason","google_match","registry",
                    "site_reachable","website","phone","rating","gps_drift_m","needs_price_review"])
        for slug,name,com,site_url,fr in rows:
            w.writerow([slug,fr.get("status"),fr.get("confidence"),fr.get("flag_reason"),fr.get("google_match"),
                        (fr.get("registry") or {}).get("state"),fr.get("site_reachable"),
                        (fr.get("website") or {}).get("value") if fr.get("website") else "",
                        (fr.get("phone") or {}).get("value") if fr.get("phone") else "",
                        fr.get("rating"),fr.get("gps_drift_m"),fr.get("needs_price_review")])

    # email queue = closed/unverified/medium-confidence only (NOT all 325)
    with open("email_queue.csv","w",newline="",encoding="utf-8") as fp:
        w=csv.writer(fp); w.writerow(["slug","name","commune","status","reason","website","phone"])
        for slug,name,com,site_url,fr in rows:
            if fr.get("status") in ("CLOSED","UNVERIFIED") or fr.get("confidence")=="medium":
                w.writerow([slug,name,com,fr.get("status"),fr.get("flag_reason"),
                            (fr.get("website") or {}).get("value") if fr.get("website") else (site_url or ""),
                            (fr.get("phone") or {}).get("value") if fr.get("phone") else ""])

    closed=sum(1 for *_,fr in rows if fr.get("status")=="CLOSED")
    unver =sum(1 for *_,fr in rows if fr.get("status")=="UNVERIFIED")
    med   =sum(1 for *_,fr in rows if fr.get("confidence")=="medium")
    price =sum(1 for *_,fr in rows if fr.get("needs_price_review"))
    print(f"\nDONE. {len(rows)} fiches.")
    print(f"  ❌ {closed} closed   ⚠️ {unver} unverified   ⚠️ {med} need owner confirm")
    print(f"  💶 {price} have price candidates on their site → Claude Code should extract & review")
    print(f"\n  report.csv       (everything, problems first)")
    print(f"  email_queue.csv  ({closed+unver+med} venues to contact — not all {len(rows)})")


if __name__=="__main__":
    main()
