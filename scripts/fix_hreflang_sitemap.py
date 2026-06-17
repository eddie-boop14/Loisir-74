#!/usr/bin/env python3
"""
Compute canonical hreflang blocks for every multilingual page group from
file existence (not from the existing, partly-buggy on-page blocks), then:
  --apply   normalize <link rel="alternate" hreflang> on FR + locale pages
  --sitemap rebuild sitemap.xml with xhtml:link alternates + locale URLs
Default (no flag): dry-run report + validation only.
"""
import re
import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://loisirs74.fr/"
LANGS = ["en", "de", "it", "es", "nl"]
LINK_RE = re.compile(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">')
RUN_RE = re.compile(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">(?:\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">)*')
NOIDX_RE = re.compile(r'<meta name="robots" content="[^"]*noindex')


def is_noindex(group):
    return bool(NOIDX_RE.search(group["pages"]["fr"][1].read_text(encoding="utf-8")))


def insert_block(html, block):
    """Insert an hreflang block into <head> at a safe anchor."""
    m = re.search(r'<meta charset="[^"]*">', html)
    if m:
        return html[:m.end()] + "\n" + block + html[m.end():]
    m = re.search(r'<head[^>]*>', html)
    if m:
        return html[:m.end()] + "\n" + block + html[m.end():]
    raise RuntimeError("no <head> anchor for hreflang insertion")


def url_to_file(url):
    p = url[len(BASE):]
    if p == "":
        return ROOT / "index.html"
    if p.endswith("/"):
        return ROOT / (p + "index.html")
    return ROOT / (p + ".html")


def link(lang, url):
    return f'<link rel="alternate" hreflang="{lang}" href="{url}">'


def _parse_alternates(html):
    """Extract {lang: href} from <link rel="alternate" hreflang=".." href=".."> tags,
    tolerating any attribute order within the tag."""
    out = {}
    for tag in re.findall(r'<link[^>]*>', html):
        if 'rel="alternate"' not in tag:
            continue
        m_lang = re.search(r'hreflang="([^"]*)"', tag)
        m_href = re.search(r'href="([^"]*)"', tag)
        if m_lang and m_href:
            out[m_lang.group(1)] = m_href.group(1)
    return out


def hub_map():
    """FR hub url -> {lang: locale hub url}, from locale hub indexes' fr-href."""
    m = {}
    for L in LANGS:
        for f in glob.glob(f"{L}/*/index.html"):
            html = Path(f).read_text(encoding="utf-8")
            d = _parse_alternates(html)
            fr = d.get("fr")
            if not fr or not fr.endswith("/"):
                continue
            self_url = BASE + f[:-len("index.html")]
            m.setdefault(fr, {})[L] = self_url
    return m


def build_groups():
    """Each group: {'fr_url':..., 'pages': {lang: (url, file)}}  (lang includes 'fr')."""
    groups = []
    # homepage
    g = {"fr_url": BASE, "pages": {"fr": (BASE, ROOT / "index.html")}}
    for L in LANGS:
        f = ROOT / L / "index.html"
        if f.exists():
            g["pages"][L] = (f"{BASE}{L}/", f)
    groups.append(g)
    # hubs
    hm = hub_map()
    for fr_url, locs in sorted(hm.items()):
        frf = url_to_file(fr_url)
        if not frf.exists():
            continue
        g = {"fr_url": fr_url, "pages": {"fr": (fr_url, frf)}}
        for L in LANGS:
            if L in locs:
                lf = url_to_file(locs[L])
                if lf.exists():
                    g["pages"][L] = (locs[L], lf)
        groups.append(g)
    # lieu pages (by slug/filename)
    for fp in sorted(glob.glob("*.html")):
        if fp == "index.html":
            continue
        slug = fp[:-5]
        fr_url = BASE + slug
        g = {"fr_url": fr_url, "pages": {"fr": (fr_url, ROOT / fp)}}
        for L in LANGS:
            lf = ROOT / L / fp
            if lf.exists():
                g["pages"][L] = (f"{BASE}{L}/{slug}", lf)
        groups.append(g)
    return groups


def canonical_links(g):
    fr_url = g["fr_url"]
    out = [link("fr", fr_url)]
    for L in LANGS:
        if L in g["pages"]:
            out.append(link(L, g["pages"][L][0]))
    out.append(link("x-default", fr_url))
    return out


def main():
    apply = "--apply" in sys.argv
    do_sitemap = "--sitemap" in sys.argv
    groups = build_groups()

    multilingual = [g for g in groups if len(g["pages"]) > 1 and not is_noindex(g)]
    monolingual = [g for g in groups if len(g["pages"]) == 1]
    skipped_noindex = [g for g in groups if is_noindex(g)]
    print(f"skipped noindex groups: {len(skipped_noindex)}")

    # validation: every canonical href -> existing file
    broken = []
    for g in multilingual:
        for ln in canonical_links(g):
            url = re.search(r'href="([^"]*)"', ln).group(1)
            if not url_to_file(url).exists():
                broken.append((g["fr_url"], url))
    print(f"groups: {len(groups)}  multilingual: {len(multilingual)}  monolingual(FR-only): {len(monolingual)}")
    print(f"broken canonical hrefs (point to missing file): {len(broken)}")
    for fr, u in broken[:10]:
        print("   BROKEN", fr, "->", u)

    # how many page files would change
    changed = []
    for g in multilingual:
        canon = "\n".join(canonical_links(g))
        for lang, (url, f) in g["pages"].items():
            html = f.read_text(encoding="utf-8")
            m = RUN_RE.search(html)
            cur = m.group(0) if m else ""
            if cur != canon:
                changed.append(f)
                if apply:
                    if m:
                        html = html[:m.start()] + canon + html[m.end():]
                    else:
                        html = insert_block(html, canon)
                    f.write_text(html, encoding="utf-8")
    print(f"page files needing hreflang normalization: {len(changed)}")
    if apply:
        print("  -> applied.")

    if do_sitemap:
        rebuild_sitemap(groups, multilingual)


def rebuild_sitemap(groups, multilingual):
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    current_set = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    # urls belonging to noindex groups must never be in the sitemap
    noindex_urls = set()
    for g in groups:
        if is_noindex(g):
            for lang, (url, f) in g["pages"].items():
                noindex_urls.add(url)
    # alternates only for indexable multilingual groups
    url_group = {}
    for g in multilingual:
        for lang, (url, f) in g["pages"].items():
            url_group[url] = g
    # preserve existing sitemap urls, add locale variants of indexable groups,
    # drop any noindex urls
    all_urls = set(current_set)
    for g in multilingual:
        for lang, (url, f) in g["pages"].items():
            all_urls.add(url)
    all_urls -= noindex_urls
    # drop stale entries whose target file no longer exists
    stale = {u for u in all_urls if not url_to_file(u).exists()}
    if stale:
        print(f"dropping {len(stale)} stale sitemap urls: {sorted(stale)}")
    all_urls -= stale
    # drop non-canonical duplicates (page canonical points to a different url)
    canon_re = re.compile(r'<link rel="canonical" href="([^"]+)">')
    dupes = set()
    for u in all_urls:
        m = canon_re.search(url_to_file(u).read_text(encoding="utf-8"))
        if m and m.group(1).rstrip("/") != u.rstrip("/"):
            dupes.add(u)
    if dupes:
        print(f"dropping {len(dupes)} non-self-canonical urls: {sorted(dupes)}")
    all_urls -= dupes

    def sort_key(u):
        return (u.count("/"), u)

    # Per-URL <lastmod> from the git commit date of each URL's underlying
    # SOURCE — never a uniform stamp. Source mapping:
    #   /<slug>           → Json/<slug>.json
    #   /<lang>/<slug>    → Json/<slug>.json   (all locales share JSON)
    #   /<hub>/           → max(commit dates of fiches in that hub,
    #                            scripts/build_hubs.py)
    #   /<lang>/<hub>/    → same
    #   /, /<lang>/       → scripts/build_homepage.py + content sources
    # Anything we can't resolve cleanly falls back to the file mtime of
    # the rendered HTML.
    import datetime, subprocess, json as _json
    from collections import defaultdict

    def _git_dates(paths):
        """Return {path: 'YYYY-MM-DD'} for each path's most recent commit."""
        if not paths:
            return {}
        out = {}
        try:
            res = subprocess.run(
                ["git", "log", "--name-only", "--format=COMMIT %cs", "--"] + list(paths),
                cwd=str(ROOT), capture_output=True, text=True, check=True,
            )
        except Exception:
            return {p: None for p in paths}
        current = None
        for line in res.stdout.splitlines():
            if line.startswith("COMMIT "):
                current = line[len("COMMIT "):].strip()
            elif line.strip() and current:
                out.setdefault(line.strip(), current)
        return out

    # Source-paths: every Json/ file + the two build scripts we treat as
    # "structural source" for hubs/homepages.
    json_paths = [str(p.relative_to(ROOT)) for p in (ROOT / "Json").glob("*.json")]
    structural_paths = [
        "scripts/build_hubs.py",
        "scripts/build_homepage.py",
        "scripts/build_all_locales.py",
    ]
    date_map = _git_dates(json_paths + structural_paths)

    # Build hub → list of fiche source paths to take the max over.
    HUB_FILTERS_CAT = {
        "cascades":         ("cascade",),
        "chateaux":         ("chateau",),
        "musees":           ("musee",),
        "points-de-vue":    ("point-de-vue",),
        "sentiers":         ("sentier",),
        "telecabines":      ("telecabine",),
        "voies-vertes":     ("voie-verte",),
        "lacs-plages":      ("lac","plage"),
        "bases-de-loisirs": ("domaine","parc","base-nautique","wakepark","accrobranche"),
        "parcs-jardins":    ("parc","jardin"),
        "baignade-nautisme":("aquaparc","croisiere","base-nautique","wakepark"),
        "sorties-detente":  ("cinema","casino"),
        "sport-jeux":       ("bowling","karting","patinoire"),
    }
    HUB_SLUGS_PER_LANG = {
        "cascades":{"fr":"cascades","en":"waterfalls","de":"wasserfaelle","it":"cascate","es":"cascadas","nl":"watervallen"},
        "chateaux":{"fr":"chateaux","en":"castles","de":"schloesser","it":"castelli","es":"castillos","nl":"kastelen"},
        "musees":{"fr":"musees","en":"museums","de":"museen","it":"musei","es":"museos","nl":"musea"},
        "points-de-vue":{"fr":"points-de-vue","en":"viewpoints","de":"aussichtspunkte","it":"punti-panoramici","es":"miradores","nl":"uitzichtpunten"},
        "sentiers":{"fr":"sentiers","en":"trails","de":"wanderwege","it":"sentieri","es":"senderos","nl":"wandelpaden"},
        "telecabines":{"fr":"telecabines","en":"cable-cars","de":"seilbahnen","it":"funivie","es":"telefericos","nl":"kabelbanen"},
        "voies-vertes":{"fr":"voies-vertes","en":"greenways","de":"radwege","it":"vie-verdi","es":"vias-verdes","nl":"fietsroutes"},
        "lacs-plages":{"fr":"lacs-plages","en":"lakes","de":"seen","it":"laghi","es":"lagos","nl":"meren"},
        "bases-de-loisirs":{"fr":"bases-de-loisirs","en":"leisure-parks","de":"freizeitparks","it":"aree-ricreative","es":"areas-de-ocio","nl":"recreatieparken"},
        "parcs-jardins":{"fr":"parcs-jardins","en":"parks-gardens","de":"parks-gaerten","it":"parchi-giardini","es":"parques-jardines","nl":"parken-tuinen"},
        "baignade-nautisme":{"fr":"baignade-nautisme","en":"swimming-watersports","de":"baden-wassersport","it":"nuoto-sport-acquatici","es":"bano-deportes-acuaticos","nl":"zwemmen-watersport"},
        "sorties-detente":{"fr":"sorties-detente","en":"outings-relax","de":"ausfluege-erholung","it":"uscite-relax","es":"salidas-relax","nl":"uitstapjes-ontspanning"},
        "sport-jeux":{"fr":"sport-jeux","en":"sport-games","de":"sport-spiele","it":"sport-giochi","es":"deporte-juegos","nl":"sport-spelen"},
        "que-faire":{"fr":"que-faire","en":"what-to-do","de":"was-unternehmen","it":"cosa-fare","es":"que-hacer","nl":"wat-te-doen"},
        "sensations-plein-air":{"fr":"sensations-plein-air","en":"outdoor-thrills","de":"outdoor-nervenkitzel","it":"brividi-aria-aperta","es":"sensaciones-aire-libre","nl":"buitenavontuur"},
    }

    # Pre-compute hub URL → date
    hub_date = {}
    for canon, cats in HUB_FILTERS_CAT.items():
        # collect fiche slugs matching this hub
        member_dates = []
        for jp in json_paths:
            try:
                d = _json.loads((ROOT / jp).read_text(encoding="utf-8"))
            except Exception:
                continue
            if d.get("status") in ("draft", "unverified"): continue
            if d.get("category") in cats:
                dt = date_map.get(jp)
                if dt: member_dates.append(dt)
        member_dates.append(date_map.get("scripts/build_hubs.py") or "")
        hub_max = max(d for d in member_dates if d) if any(member_dates) else None
        for lang, slug in HUB_SLUGS_PER_LANG[canon].items():
            url = f"https://loisirs74.fr/{slug}/" if lang == "fr" else f"https://loisirs74.fr/{lang}/{slug}/"
            hub_date[url] = hub_max
    # Curated hubs (que-faire, sensations-plein-air): take build_hubs date as proxy
    for canon in ("que-faire", "sensations-plein-air"):
        for lang, slug in HUB_SLUGS_PER_LANG[canon].items():
            url = f"https://loisirs74.fr/{slug}/" if lang == "fr" else f"https://loisirs74.fr/{lang}/{slug}/"
            hub_date[url] = date_map.get("scripts/build_hubs.py")

    homepage_dates = [date_map.get(p) for p in structural_paths]
    homepage_max = max(d for d in homepage_dates if d) if any(homepage_dates) else None

    def lastmod_for(u):
        # Strip protocol/host
        tail = u.replace("https://loisirs74.fr", "").lstrip("/").rstrip("/")
        # Homepage
        if tail == "" or tail in {"en","de","it","es","nl"}:
            return homepage_max or datetime.date.today().isoformat()
        # Hub index (any locale)
        if u in hub_date and hub_date[u]:
            return hub_date[u]
        # Fiche: /<slug> or /<lang>/<slug>
        parts = tail.split("/")
        if parts[0] in ("en","de","it","es","nl") and len(parts) >= 2:
            slug = parts[1]
        else:
            slug = parts[0]
        src = f"Json/{slug}.json"
        if src in date_map:
            return date_map[src]
        # Fallback: rendered HTML mtime
        f = url_to_file(u)
        if f.exists():
            return datetime.date.fromtimestamp(f.stat().st_mtime).isoformat()
        return datetime.date.today().isoformat()

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u in sorted(all_urls, key=sort_key):
        lm = lastmod_for(u)
        g = url_group.get(u)
        if g and len(g["pages"]) > 1:
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{l}" href="{g["pages"][l][0]}"/>'
                for l in (["fr"] + LANGS) if l in g["pages"]
            )
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{g["fr_url"]}"/>'
            lines.append(f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod><changefreq>weekly</changefreq>{alts}</url>")
        else:
            lines.append(f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod><changefreq>weekly</changefreq></url>")
    lines.append("</urlset>")
    out = "\n".join(lines) + "\n"
    (ROOT / "sitemap.xml").write_text(out, encoding="utf-8")
    print(f"sitemap rebuilt: {len(all_urls)} urls (was {len(current_set)})")


if __name__ == "__main__":
    main()
