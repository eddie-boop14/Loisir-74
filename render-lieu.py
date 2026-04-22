#!/usr/bin/env python3
"""
render-lieu.sh equivalent in Python — renders all 4 language versions
of a lieu in one command.

Usage from the repo root:
    python3 render-lieu.py domaine-du-tornet
    python3 render-lieu.py cascade-d-angon --json-dir Json --template loisirs74-template-v3.html

It looks for:
    <json_dir>/<slug>.fr.json
    <json_dir>/<slug>.en.json
    <json_dir>/<slug>.de.json
    <json_dir>/<slug>.it.json

And outputs:
    ./<slug>.html           (FR master)
    ./en/<slug>.html
    ./de/<slug>.html
    ./it/<slug>.html

Skips any language whose JSON is missing, with a warning. Fails on FR missing
(FR is the master — if it doesn't exist, the lieu doesn't exist).
"""

import argparse
import subprocess
import sys
from pathlib import Path

LANGS = ("fr", "en", "de", "it")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="The lieu slug (e.g. 'domaine-du-tornet')")
    ap.add_argument("--json-dir", default="Json", help="Where the JSON files live (default: Json/)")
    ap.add_argument("--template", default="loisirs74-template-v3.html")
    ap.add_argument("--render", default="render-v3.py", help="Path to render-v3.py")
    ap.add_argument("--only", nargs="+", choices=LANGS,
                    help="Render only these languages (default: all 4)")
    args = ap.parse_args()

    langs_to_render = args.only if args.only else LANGS
    json_dir = Path(args.json_dir)

    # Hard fail if FR master missing and FR is in the list
    fr_json = json_dir / f"{args.slug}.fr.json"
    if "fr" in langs_to_render and not fr_json.exists():
        print(f"✗ FR master missing: {fr_json}", file=sys.stderr)
        print("  The French version is the master — produce it first.", file=sys.stderr)
        sys.exit(1)

    rendered, skipped, failed = [], [], []

    for lang in langs_to_render:
        json_path = json_dir / f"{args.slug}.{lang}.json"
        if not json_path.exists():
            print(f"⚠ Skipped {lang}: {json_path} not found")
            skipped.append(lang)
            continue

        cmd = [
            sys.executable, args.render,
            str(json_path),
            "--template", args.template,
            "--lang", lang,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ {lang} failed:\n{result.stderr}", file=sys.stderr)
            failed.append(lang)
        else:
            # render-v3.py prints "✓ Wrote <path>" — forward it
            print(result.stdout.strip())
            rendered.append(lang)

    # Summary
    print()
    print(f"Rendered : {', '.join(rendered) or '—'}")
    if skipped:
        print(f"Skipped  : {', '.join(skipped)}")
    if failed:
        print(f"Failed   : {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

