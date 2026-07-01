#!/usr/bin/env python3
"""gate_prose_html.py — fail the build if any rendered page prints ESCAPED prose
HTML tags (HANDOFF-23).

Authored-as-HTML prose fields (when_to_visit, events, body.what_is) must render
raw; when they were HTML-escaped on output, ~15 fiches printed literal
`<p>/<ul>/<li>/<strong>` on-screen. build_lieu_page.prose() now emits those
fields raw when they carry tags (and escapes plain text). This gate is the
tripwire so the class can't silently return: no built page may contain
`&lt;(p|ul|ol|li|strong|em)&gt;` — the signature of a wrongly-escaped prose tag.

Read-only. Scans the rendered prose trees (repo root + locale subdirs + facts
trees), skipping source, exports and build output.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_TOP = {"_site", "scripts", "reports", "Json", "api", "content",
            ".well-known", ".git", "data", "node_modules", "img"}
LEAK = re.compile(r'&lt;(p|ul|ol|li|strong|em)&gt;')


def main():
    bad = []
    for p in ROOT.rglob("*.html"):
        parts = p.relative_to(ROOT).parts
        if parts[0] in SKIP_TOP:
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        hits = LEAK.findall(txt)
        if hits:
            bad.append((str(p.relative_to(ROOT)), len(hits)))
    if bad:
        total = sum(n for _, n in bad)
        print(f"gate_prose_html: {len(bad)} page(s) print ESCAPED prose HTML tags "
              f"({total} leaks) — authored-HTML prose must render raw (HANDOFF-23):")
        for f, n in sorted(bad, key=lambda x: -x[1])[:25]:
            print(f"  {f}: {n}")
        sys.exit(1)
    print("gate_prose_html: 0 escaped prose HTML tags in rendered pages "
          "(authored-HTML prose renders raw; plain text stays escaped)")


if __name__ == "__main__":
    main()
