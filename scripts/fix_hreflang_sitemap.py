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

    # GSC freshness signal — Google uses <lastmod> to prioritise recrawl
    # of pages that have changed. Today's date is a safe default for a
    # site that's regenerated frequently; per-URL granularity would
    # require a per-page timestamp source we don't currently keep.
    import datetime
    lastmod = datetime.date.today().isoformat()

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u in sorted(all_urls, key=sort_key):
        g = url_group.get(u)
        if g and len(g["pages"]) > 1:
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{l}" href="{g["pages"][l][0]}"/>'
                for l in (["fr"] + LANGS) if l in g["pages"]
            )
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{g["fr_url"]}"/>'
            lines.append(f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq>{alts}</url>")
        else:
            lines.append(f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq></url>")
    lines.append("</urlset>")
    out = "\n".join(lines) + "\n"
    (ROOT / "sitemap.xml").write_text(out, encoding="utf-8")
    print(f"sitemap rebuilt: {len(all_urls)} urls (was {len(current_set)})")


if __name__ == "__main__":
    main()
