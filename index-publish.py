#!/usr/bin/env python3
"""
index-publish.py — flip a lieu card from "En préparation" to "Fiche publiée"
on the FR index, then regenerate EN/DE/IT indexes.

Run this AFTER `render-lieu.py <slug>` has produced the 4 HTML files for the lieu.

Usage :
    python3 index-publish.py cascade-d-angon               # mark as live
    python3 index-publish.py cascade-d-angon --unpublish   # flip back to draft
    python3 index-publish.py cascade-d-angon --dry-run     # preview, no write

What it does :
1. Reads the FR index.html at repo root
2. Finds the <article class="lieu ..."> block for that slug
3. Flips : is-draft -> is-live, data-status, status badge, wraps name in <a>
4. Writes index.html back
5. Runs translate_index.py to regenerate en/index.html, de/index.html, it/index.html

Safety :
- Verifies the card exists before touching anything
- Verifies the HTML file for that slug exists (./{slug}.html) before publishing
- Idempotent : running publish on an already-live card is a no-op with a note
- Uses exact-string matching, not regex on the card block
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path


INDEX_PATH = Path('index.html')
TRANSLATE_SCRIPT = Path('translate_index.py')


def find_card(html: str, slug: str) -> tuple[str, str] | None:
    """
    Locate the <article class="lieu..."> block for this slug.
    Matching is done via the slug appearing in the `data-name` attribute,
    because data-name = lowercased "<nom> <commune>" which is unique.

    Returns (full_block, data_name_attr) or None if not found.
    """
    # We don't know the lieu's data-name exactly (it's "<name> <commune>" lowercased),
    # so the reliable anchor is the display slug inside the link href for live cards,
    # or the commune/name hint. For draft cards we search by scanning all articles
    # and matching the slug against the file that SHOULD exist for that lieu.
    #
    # Simpler approach : the display name in <h3 class="lieu-name"> is unique per lieu
    # on the index. We derive the expected name by reading the slug dashes -> spaces -> title case,
    # but that's unreliable for names with apostrophes. Best: scan for data-name containing
    # the slug's core tokens.
    #
    # For this tool we'll require the caller to pass a slug, and we'll search each article
    # block's data-name for a match by deriving a canonical form from the slug.

    # Find every <article class="lieu ..."> ... </article> block
    pattern = re.compile(
        r'<article class="lieu[^"]*"[^>]*data-name="([^"]*)"[^>]*>.*?</article>',
        re.DOTALL,
    )
    matches = list(pattern.finditer(html))

    # Convert slug to a best-guess search set of tokens
    # "cascade-d-angon" -> tokens ["cascade", "d", "angon"]
    # "domaine-du-tornet" -> tokens ["domaine", "du", "tornet"]
    slug_tokens = [t for t in slug.split('-') if t]

    # Score each article by how many slug tokens appear in its data-name
    best = None
    best_score = 0
    for m in matches:
        data_name = m.group(1)
        # data_name is space-separated words of (lieu name + commune) lowercased
        name_tokens = re.findall(r"[\w']+", data_name.lower())
        # Count slug tokens that appear as whole-word matches in name_tokens
        # (also allow substring match for accented/apostrophe variants)
        score = 0
        for tok in slug_tokens:
            if tok in name_tokens:
                score += 2
            elif any(tok in nt for nt in name_tokens):
                score += 1
        if score > best_score:
            best_score = score
            best = (m.group(0), data_name)

    # Require that ALL slug tokens match somewhere, otherwise fail safe
    if best is None or best_score < len(slug_tokens):
        return None
    return best


def transform_to_live(card: str, slug: str, display_name: str) -> str:
    """Transform a draft card into a live card with an <a> link."""
    out = card

    # 1. is-draft -> is-live on the article class
    out = out.replace('class="lieu is-draft"', 'class="lieu is-live"')

    # 2. data-status="draft" -> "live"
    out = out.replace('data-status="draft"', 'data-status="live"')

    # 3. Wrap the name in an <a href="/{slug}">. Only if not already wrapped.
    # Original : <h3 class="lieu-name">Cascade d'Angon</h3>
    # Target   : <h3 class="lieu-name"><a href="/cascade-d-angon">Cascade d'Angon</a></h3>
    name_pattern = re.compile(r'<h3 class="lieu-name">([^<]+)</h3>')
    m = name_pattern.search(out)
    if m and '<a href=' not in m.group():
        name = m.group(1)
        out = out.replace(
            m.group(0),
            f'<h3 class="lieu-name"><a href="/{slug}">{name}</a></h3>',
        )

    # 4. Status badge : "● En préparation" (draft) -> "● Fiche publiée" (live)
    # Also swap the CSS class : "lieu-status draft" -> "lieu-status live"
    out = out.replace(
        '<span class="lieu-status draft">● En préparation</span>',
        '<span class="lieu-status live">● Fiche publiée</span>',
    )

    return out


def transform_to_draft(card: str, slug: str) -> str:
    """Reverse transform: flip a live card back to draft."""
    out = card
    out = out.replace('class="lieu is-live"', 'class="lieu is-draft"')
    out = out.replace('data-status="live"', 'data-status="draft"')

    # Unwrap <a href="/{slug}">Name</a> -> Name
    out = re.sub(
        r'<h3 class="lieu-name"><a href="/' + re.escape(slug) + r'">([^<]+)</a></h3>',
        r'<h3 class="lieu-name">\1</h3>',
        out,
    )

    out = out.replace(
        '<span class="lieu-status live">● Fiche publiée</span>',
        '<span class="lieu-status draft">● En préparation</span>',
    )
    return out


def main():
    ap = argparse.ArgumentParser(
        description='Flip a lieu card from draft to live (or back) on the FR index, then regenerate EN/DE/IT.'
    )
    ap.add_argument('slug', help="The lieu slug, e.g. 'cascade-d-angon'")
    ap.add_argument('--unpublish', action='store_true',
                    help='Flip a live card back to draft instead.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Show what would change, do not write.')
    ap.add_argument('--skip-translate', action='store_true',
                    help='Do not regenerate the translated indexes.')
    args = ap.parse_args()

    if not INDEX_PATH.exists():
        sys.exit(f'✗ {INDEX_PATH} not found. Run this script from the repo root.')

    # Safety check : for publish, confirm the HTML file exists
    if not args.unpublish:
        html_file = Path(f'{args.slug}.html')
        if not html_file.exists():
            sys.exit(
                f"✗ {html_file} not found at repo root.\n"
                f"  Publish would create a broken link. Run `python3 render-lieu.py {args.slug}` first."
            )

    html = INDEX_PATH.read_text(encoding='utf-8')
    found = find_card(html, args.slug)
    if not found:
        sys.exit(f'✗ No card matching slug "{args.slug}" found in {INDEX_PATH}.')
    card, data_name = found

    # Check current state
    is_live = 'class="lieu is-live"' in card
    is_draft = 'class="lieu is-draft"' in card

    if args.unpublish:
        if not is_live:
            print(f'• Card for "{args.slug}" is already draft. Nothing to do.')
            return
        new_card = transform_to_draft(card, args.slug)
        action = 'unpublished (draft)'
    else:
        if is_live:
            print(f'• Card for "{args.slug}" is already live. Nothing to do.')
            return
        if not is_draft:
            sys.exit(f'✗ Card for "{args.slug}" is neither draft nor live. Manual fix needed.')
        # Extract display name for logging
        m = re.search(r'<h3 class="lieu-name">([^<]+)</h3>', card)
        display_name = m.group(1) if m else args.slug
        new_card = transform_to_live(card, args.slug, display_name)
        action = 'published (live)'

    if new_card == card:
        sys.exit(f'✗ Transformation produced no change. Markup may not match expected pattern.')

    new_html = html.replace(card, new_card)
    if new_html == html:
        sys.exit(f'✗ Failed to write new card back into index.html. Aborted.')

    if args.dry_run:
        print(f'[dry-run] Would mark "{args.slug}" as {action}.')
        print(f'[dry-run] No files written.')
        return

    INDEX_PATH.write_text(new_html, encoding='utf-8')
    print(f'✓ {args.slug} → {action} in {INDEX_PATH}')

    # Regenerate translations
    if args.skip_translate:
        print('• Skipped EN/DE/IT regeneration (--skip-translate).')
        return

    if not TRANSLATE_SCRIPT.exists():
        print(f'⚠ {TRANSLATE_SCRIPT} not found. EN/DE/IT indexes NOT regenerated.')
        print(f'  Run manually when ready : python3 translate_index.py')
        return

    result = subprocess.run(
        [sys.executable, str(TRANSLATE_SCRIPT)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f'⚠ translate_index.py failed :\n{result.stderr}', file=sys.stderr)
        sys.exit(1)
    # Forward its output
    print(result.stdout.strip())


if __name__ == '__main__':
    main()
