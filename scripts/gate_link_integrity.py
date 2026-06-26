#!/usr/bin/env python3
"""gate_link_integrity.py — fail if any internal link in _site/ 404s.

The whole bug class behind "575 broken local heros" and "32 FR commune pages
dead": a page links to /<path> but build_site never copied <path> into _site/.
Invisible until a user (or Google) clicks it. This gate parses the ACTUALLY
SERVED tree and asserts every internal href/src resolves to a real file (or a
_redirects rule), so an allowlist omission turns the build red instead of
shipping dead links.

Resolution (mirrors the clean-URL scheme):
  /                     -> _site/index.html
  /x/   (trailing /)    -> _site/x/index.html
  /x.ext (has ext)      -> _site/x.ext
  /x    (clean, no ext) -> _site/x.html  OR  _site/x/index.html
A target also counts as valid if it matches a source in _redirects.

Skips: external hosts, mailto:/tel:/#/data:/javascript:, protocol-relative //.

Run after build_site. Read-only. Exit 1 on any broken internal link.

Usage:
    python3 scripts/gate_link_integrity.py
"""
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "_site")
HOST = "loisirs74.fr"

LINK_RE = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)


def load_allowlist():
    """Known pre-existing broken internal targets (legal/footer/utility i18n
    debt) — allowed so the gate can ship and catch NEW (commune/img-class)
    regressions without blocking on a separate cleanup. One path per line."""
    allow = set()
    ap = os.path.join(ROOT, "reports", "link-integrity-allowlist.txt")
    if os.path.exists(ap):
        for line in open(ap, encoding="utf-8"):
            line = line.split("#", 1)[0].strip()
            if line:
                allow.add(line)
    return allow


def load_redirect_sources():
    srcs = set()
    rp = os.path.join(ROOT, "_redirects")
    if os.path.exists(rp):
        for line in open(rp, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts:
                srcs.add(parts[0].rstrip("/") or "/")
                # also the splat/base form
                srcs.add(parts[0].split("*")[0].rstrip("/") or "/")
    return srcs


def to_path(url):
    """Internal URL -> normalized path, or None if external/non-navigational."""
    u = url.strip()
    if not u or u[0] == "#":
        return None
    if u.startswith(("mailto:", "tel:", "data:", "javascript:", "//")):
        return None
    if u.startswith("http://") or u.startswith("https://"):
        m = re.match(r"https?://([^/]+)(/.*)?$", u)
        if not m or m.group(1).replace("www.", "") != HOST:
            return None  # external
        u = m.group(2) or "/"
    if not u.startswith("/"):
        return None  # relative asset (rare); skip
    return u.split("#")[0].split("?")[0]


def candidates(path):
    p = path
    if p == "/" or p == "":
        return [os.path.join(SITE, "index.html")]
    rel = p.lstrip("/")
    if rel.endswith("/"):
        return [os.path.join(SITE, rel, "index.html")]
    last = rel.rsplit("/", 1)[-1]
    if "." in last:
        return [os.path.join(SITE, rel)]
    return [os.path.join(SITE, rel + ".html"),
            os.path.join(SITE, rel, "index.html")]


def main():
    if not os.path.isdir(SITE):
        print("::error::_site/ not built — run build_site.py first")
        sys.exit(1)
    redirects = load_redirect_sources()
    allow = load_allowlist()

    missing = defaultdict(list)   # target_path -> [pages linking it]
    checked = 0
    pages = 0
    for dirpath, _, files in os.walk(SITE):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            pages += 1
            fp = os.path.join(dirpath, fn)
            page_rel = os.path.relpath(fp, SITE)
            html = open(fp, encoding="utf-8", errors="ignore").read()
            seen = set()
            for raw in LINK_RE.findall(html):
                path = to_path(raw)
                if path is None or path in seen:
                    continue
                seen.add(path)
                checked += 1
                if path.rstrip("/") in redirects or (path.rstrip("/") or "/") in redirects:
                    continue
                if path in allow or path.rstrip("/") in allow:
                    continue
                if not any(os.path.exists(c) for c in candidates(path)):
                    missing[path].append(page_rel)

    print(f"gate_link_integrity: {pages} pages, {checked} internal links checked")
    if not missing:
        print("✓ every internal link resolves to a file in _site/ (or a redirect)")
        sys.exit(0)

    total = sum(len(v) for v in missing.values())
    print(f"::error::{len(missing)} broken internal target(s) across {total} link(s):")
    for tgt, pglist in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:40]:
        ex = ", ".join(sorted(set(pglist))[:3])
        print(f"    ✗ {tgt}   ({len(pglist)} pages, e.g. {ex})")
    if len(missing) > 40:
        print(f"    … and {len(missing) - 40} more targets")
    print("\nFix the build_site copy allowlist (or the link). This is the "
          "img-404 / commune-404 bug class.")
    sys.exit(1)


if __name__ == "__main__":
    main()
