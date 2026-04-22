#!/usr/bin/env python3
"""
patch-footer-darkmode.py

Applies the dark-mode footer fix to every lieu HTML file in a directory tree.
Safe to run multiple times (idempotent — only changes files that still have
the buggy `background:var(--ink)` on footer.site).

Bug : in dark mode, --ink flips to light, so the footer ended up light
      background + light text = invisible.
Fix : lock the footer background to a hardcoded dark color (#0d1a0f)
      so the theme swap can't invert it. Footer text colors are already
      hardcoded light RGBA values, so they stay readable.

Usage from repo root:
    python3 patch-footer-darkmode.py
    python3 patch-footer-darkmode.py --dry-run     # preview only

By default scans : ., en/, de/, it/
"""

import argparse
import sys
from pathlib import Path

OLD = 'footer.site{background:var(--ink);color:rgba(245,241,232,0.72);padding:3rem var(--space) 2rem;margin-top:4rem;line-height:1.75}'
NEW = 'footer.site{background:#0d1a0f;color:rgba(245,241,232,0.72);padding:3rem var(--space) 2rem;margin-top:4rem;line-height:1.75}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='List files that would be changed, do not write')
    ap.add_argument('--root', default='.', help='Root directory to scan (default: current)')
    args = ap.parse_args()

    root = Path(args.root)
    patched, skipped, already_ok = [], [], []

    for html in sorted(root.rglob('*.html')):
        # skip node_modules, .git, hidden folders
        if any(p.startswith('.') or p == 'node_modules' for p in html.parts):
            continue
        text = html.read_text(encoding='utf-8')
        if OLD in text:
            if args.dry_run:
                print(f'[would patch] {html}')
            else:
                html.write_text(text.replace(OLD, NEW), encoding='utf-8')
                print(f'[patched]    {html}')
            patched.append(html)
        elif NEW in text:
            already_ok.append(html)
        else:
            # File has no footer.site block or a different form — leave alone
            skipped.append(html)

    print()
    print(f'Patched        : {len(patched)}')
    print(f'Already fixed  : {len(already_ok)}')
    print(f'Not applicable : {len(skipped)} (no matching footer block)')
    if args.dry_run and patched:
        print('\nDry run only. Re-run without --dry-run to apply.')


if __name__ == '__main__':
    main()

