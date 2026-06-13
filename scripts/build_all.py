#!/usr/bin/env python3
"""build_all.py — single canonical build entry point (JOB 3).

Renders every fiche page, the catalog index, and the placement-protection
report — all from Json/ in one idempotent pass, with no HTML mutation by
downstream scripts.

Pipeline (sequential — order is the dependency order, no cycles):

  1. Render 392 × 6 = 2352 fiche HTMLs from Json/<slug>.json via
     scripts.build_lieu_page.build_page(d, lang).  Writes:
       <ROOT>/<slug>.html              for fr
       <ROOT>/<lang>/<slug>.html       for en/de/it/es/nl
     and writes scripts/translation-coverage-report.json.
  2. Rebuild scripts/catalog-index.json from Json/.
  3. Compute the protected-placement report (chez-nous-a-la-plage,
     chalet-du-tornet) vs reports/featured-placements-baseline.md.
  4. Optional: build_site.py builds the publishable _site/ tree
     (skip with --no-site).

Idempotency: two consecutive runs produce byte-identical outputs.

Usage:
    python3 scripts/build_all.py [--no-site] [--no-coverage] [--check-only]

`--check-only` re-asserts the placement gate without rebuilding.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def run(label, fn):
    print(f"==> {label}")
    fn()


# ---- 1. fiche pages ---------------------------------------------------------

def render_all_fiches():
    """Delegate to build_all_locales (which calls build_lieu_page.build_page
    per fiche × locale and writes the translation-coverage report)."""
    import build_all_locales  # noqa: E402
    # Re-invoke its main() via argv override so the CLI defaults apply.
    sys_argv = sys.argv[:]
    sys.argv = ["build_all_locales.py"]
    try:
        build_all_locales.main()
    finally:
        sys.argv = sys_argv


# ---- 2. catalog index -------------------------------------------------------

def rebuild_catalog_index():
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / "build_catalog_index.py")],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if out.returncode != 0:
        print(out.stdout); print(out.stderr, file=sys.stderr)
        raise RuntimeError("build_catalog_index failed")
    print(out.stdout.strip() or "(catalog rebuilt)")


# ---- 3. protected-placement gate --------------------------------------------

PROT = {
    "chez-nous-a-la-plage": re.compile(r"Chez Nous à la Plage", re.I),
    "chalet-du-tornet":     re.compile(r"Chalet du Tornet", re.I),
}


def parse_baseline_hosts():
    """Read reports/featured-placements-baseline.md, return {slug: set(hosts)}."""
    md = (ROOT / "reports" / "featured-placements-baseline.md").read_text(encoding="utf-8")
    out = {n: set() for n in PROT}
    cur = None
    for line in md.split("\n"):
        if line.startswith("## chez-nous"): cur = "chez-nous-a-la-plage"; continue
        if line.startswith("## chalet"):    cur = "chalet-du-tornet"; continue
        if cur and line.startswith("| ") and "|---|" not in line and "host fiche" not in line:
            host = line.split("|")[1].strip()
            if host:
                out[cur].add(host)
    return out


def scan_current_placements():
    """Return {slug: set(host_slugs_with_card)} for the protected fiches."""
    hits = {n: set() for n in PROT}
    for p in list(ROOT.glob("*.html")) + [f for L in ("en","de","it","es","nl") for f in (ROOT / L).glob("*.html") if (ROOT / L).exists()]:
        slug = p.stem
        try:
            html = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for name, pat in PROT.items():
            if name == "chalet-du-tornet" and slug == "domaine-du-tornet":
                continue
            if pat.search(html):
                hits[name].add(slug)
    return hits


def placement_gate(strict=True):
    """Compare baseline vs current. If any baseline host lost the card → FAIL."""
    baseline = parse_baseline_hosts()
    current = scan_current_placements()
    failed = False
    for name, base_hosts in baseline.items():
        cur_hosts = current[name]
        lost = base_hosts - cur_hosts
        gained = cur_hosts - base_hosts
        status = "OK" if not lost else "FAIL"
        if lost: failed = True
        print(f"  {name:<28} baseline={len(base_hosts):<3} current={len(cur_hosts):<3} -{len(lost)} +{len(gained)}   {status}")
        if lost:
            for h in sorted(lost):
                print(f"      LOST: {h}")
    if failed and strict:
        raise SystemExit("placement gate FAILED — protected fiche dropped a host")
    return not failed


# ---- 4. snapshot byte-faithfulness ------------------------------------------

CARD_RE = re.compile(
    r'(<article[^>]*class="partner[^"]*"[^>]*>.*?</article>)',
    re.DOTALL,
)


def card_diff_gate(strict=True):
    """Compare each rebuilt card against reports/protected-cards/<slug>/<lang>.html.
    Verifies byte-faithfulness across all 12 (slug × locale) snapshots."""
    snaps = ROOT / "reports" / "protected-cards"
    failed = False
    for slug in PROT:
        for lang in ("fr", "en", "de", "it", "es", "nl"):
            snap = snaps / slug / f"{lang}.html"
            if not snap.exists():
                continue
            wanted = re.sub(r"^<!--.*?-->\n", "", snap.read_text(encoding="utf-8")).strip()
            # Find a representative host with the card in the relevant locale
            search_dirs = [ROOT] if lang == "fr" else [ROOT / lang]
            sample = None
            for d in search_dirs:
                if not d.exists():
                    continue
                for p in sorted(d.glob("*.html")):
                    if p.stem == "domaine-du-tornet" and slug == "chalet-du-tornet":
                        continue
                    html = p.read_text(encoding="utf-8")
                    if PROT[slug].search(html):
                        for card in CARD_RE.findall(html):
                            if PROT[slug].search(card):
                                sample = card.strip()
                                break
                        if sample:
                            break
                if sample:
                    break
            if sample is None:
                print(f"  {slug}/{lang}: no rebuilt card to compare")
                continue
            match = (sample == wanted)
            verdict = "byte-faithful" if match else f"DRIFT ({len(sample)} vs {len(wanted)} bytes)"
            print(f"  {slug:<22} {lang}: {verdict}")
            if not match:
                failed = True
    if failed and strict:
        raise SystemExit("card-diff gate FAILED — protected card drifted from snapshot")
    return not failed


# ---- 5. idempotency assertion (optional, --check-only) ----------------------

def assert_idempotent():
    """Render twice into a temp dir, byte-compare. (~20s on the 392 corpus.)"""
    import shutil, tempfile
    tmp1 = Path(tempfile.mkdtemp(prefix="build_all_idem_"))
    tmp2 = Path(tempfile.mkdtemp(prefix="build_all_idem_"))
    try:
        import build_all_locales
        for tmp in (tmp1, tmp2):
            sys_argv = sys.argv[:]
            sys.argv = ["build_all_locales.py", "--out-dir", str(tmp)]
            try:
                build_all_locales.main()
            finally:
                sys.argv = sys_argv
        # diff
        diffs = list(subprocess.run(
            ["diff", "-r", str(tmp1), str(tmp2)],
            capture_output=True, text=True
        ).stdout.split("\n"))
        diffs = [d for d in diffs if d.strip()]
        if diffs:
            print(f"NOT IDEMPOTENT: {len(diffs)} differences:")
            for d in diffs[:5]:
                print(f"  {d}")
            raise SystemExit(1)
        print("  idempotent (two runs byte-identical)")
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)


# ---- main -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-site", action="store_true",
                    help="Skip the build_site step")
    ap.add_argument("--check-only", action="store_true",
                    help="Re-run gates against the current tree (no rebuild)")
    ap.add_argument("--idempotency", action="store_true",
                    help="Build twice into temp dirs and assert byte-identical")
    args = ap.parse_args()

    if args.check_only:
        run("placement gate (no rebuild)", placement_gate)
        run("card-diff gate (no rebuild)", card_diff_gate)
        return

    if args.idempotency:
        run("idempotency assertion", assert_idempotent)
        return

    run("render fiche pages", render_all_fiches)
    run("rebuild catalog index", rebuild_catalog_index)
    run("placement gate vs baseline", placement_gate)
    run("card-diff gate vs snapshot", card_diff_gate)
    if not args.no_site:
        run("build _site/", lambda: subprocess.check_call(
            [sys.executable, str(SCRIPTS / "build_site.py")], cwd=str(ROOT)))


if __name__ == "__main__":
    main()
