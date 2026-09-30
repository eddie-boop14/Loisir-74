#!/usr/bin/env python3
"""gate_wikimedia_thumbs.py — a hotlinked Commons original is a 9 MB thumbnail.

Measured 30 Sept 2026, from Commons' own imageinfo API: the 12 Wikimedia files
this site hotlinks weighed 54.4 MB. The worst was 11.15 MB at 5575x3717, and
domaine-du-tornet's was 8.98 MB at 4864x3648 — rendered by the homepage in a
card 270 CSS px wide. PageSpeed put the homepage's total payload at 18.8 MB and
attributed 9.2 MB of it to that single <img>.

Commons serves scaled derivatives of the SAME file, so nothing about the licence
or the credit changes:

    .../commons/7/7f/NAME.jpg  ->  .../commons/thumb/7/7f/NAME.jpg/960px-NAME.jpg

960 because a fiche hero sits in a ~480 CSS px column (2x DPR needs ~960) and a
card in 270. Across the eleven files wider than that, 54.4 MB became 2.8 MB.

WIDTHS ARE NOT FREE-FORM. Commons rejects arbitrary sizes with
`400 Use thumbnail sizes listed on https://w.wiki/GHai`; probing found 500, 960,
1280 and 1920 served and 320/480/640/800/1000/1024/1280.../2560 among those
refused. Requesting a width LARGER than the original also fails, which is why
this gate carries exceptions rather than demanding thumbs everywhere.

Offline and deterministic: it reads Json/ and nothing else.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(ROOT, "Json")

BARE = re.compile(r"https://upload\.wikimedia\.org/wikipedia/commons/(?!thumb/)[^\"\\\s]+")

# Originals already no bigger than the 960 px derivative we would ask for, so a
# thumb URL would 404. Each carries the width and weight that earned the pass.
ALLOWED_ORIGINALS = {
    # url: (intrinsic width, bytes, why)
    "https://upload.wikimedia.org/wikipedia/commons/3/3c/Plage_d%27Albigny_%C3%A0_Annecy.jpg":
        (769, 107_520, "769 px wide, 105 KiB — smaller than the 960 px thumb"),
}


def main():
    problems = []
    for path in sorted(glob.glob(os.path.join(JSON_DIR, "*.json"))):
        text = open(path, encoding="utf-8").read()
        for url in BARE.findall(text):
            if url in ALLOWED_ORIGINALS:
                continue
            problems.append((os.path.basename(path), url))

    if problems:
        print("[wikimedia] gate: FAIL — hotlinked Commons ORIGINALS "
              f"({len(problems)}); use a 960px thumb URL:")
        for slug, url in problems:
            print(f"    ✗ {slug}: {url}")
        print("    .../commons/<a>/<ab>/NAME  ->  .../commons/thumb/<a>/<ab>/NAME/960px-NAME")
        print("    If the original is narrower than 960 px the thumb 404s — add it to")
        print("    ALLOWED_ORIGINALS with its measured width and weight instead.")
        sys.exit(1)

    n = sum(len(re.findall(r"upload\.wikimedia\.org", open(p, encoding="utf-8").read()))
            for p in glob.glob(os.path.join(JSON_DIR, "*.json")))
    print(f"[wikimedia] gate: ✓ {n} Commons references, "
          f"{len(ALLOWED_ORIGINALS)} documented original(s)")


if __name__ == "__main__":
    main()
