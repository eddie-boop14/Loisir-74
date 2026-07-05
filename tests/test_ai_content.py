#!/usr/bin/env python3
"""Tests for the AI content layer — SPECaicontentlayer §6.

Covers the generator (build_ai_content.py) and the gate (gate_ai_content.py):
  * per-lieu md: frontmatter + body, geo fields, NO research_log, idempotent
  * llms-full.txt: header total + section rulers == corpus
  * llms.txt: total + per-category counts == corpus
  * gate: red on a missing md (404) or a tampered count

Runs with pytest, or standalone: `python3 tests/test_ai_content.py`.
Everything runs in a tmpdir; the real corpus is never touched.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def _load(modname):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(SCRIPTS, f"{modname}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bac = _load("build_ai_content")


def _fiche(slug="fixture-lieu", **over):
    d = {
        "slug": slug, "category": "chateau", "commune": "Annecy",
        "postal_code": "74000", "latitude": 45.8992, "longitude": 6.1294,
        "hero_image": "https://example.org/x.jpg",
        "hero_credit": "Jane Doe · CC BY-SA 4.0 · Wikimedia Commons",
        "date_modified_human": "14 mai 2026",
        "geo_verified": True, "google_place_id": "ChIJ_test",
        "research_log": [{"date": "2026-01-01", "by": "seed", "note": "secret"}],
        "i18n": {"fr": {
            "name": "Château Fixture",
            "meta_description": "Un château de test au bord du lac.",
            "hero": {"lead": "Château de test avec vue."},
            "facts": {"type": "Château", "access": "Payant", "parking": "Gratuit",
                      "dogs": "Non admis", "best_season": "Été", "duration": "1 h"},
            "body": {"what_is": "<p>Le <strong>Château</strong> est beau.</p><p>Deux.</p>"},
            "activities": [{"title": "Visiter", "description": "Voir les salles."}],
            "practical_info": [{"k": "Adresse", "v": "1 rue du Test"}],
            "how_to_get_there": {"car": "Par la D1.", "public_transport": None, "bike": None},
            "when_to_visit": "Toute l'année.",
            "events": "Concerts l'été.",
            "faq": [{"q": "Tarif ?", "a": "7 €."}],
        }},
    }
    d.update(over)
    return d


def _seed(json_dir, fiche):
    with open(os.path.join(json_dir, f"{fiche['slug']}.json"), "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)


def _gen(json_dir, content_dir, root, *flags):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "build_ai_content.py"),
         "--json-dir", json_dir, "--content-dir", content_dir, "--root", root, *flags],
        capture_output=True, text=True)


def _gate(json_dir, content_dir, root):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "gate_ai_content.py"),
         "--json-dir", json_dir, "--content-dir", content_dir, "--root", root],
        capture_output=True, text=True)


# ── unit: render_md ─────────────────────────────────────────────────────────
def test_md_shape_and_geo_no_research_log():
    md = bac.render_md(_fiche())
    assert md.startswith("---\nslug: fixture-lieu\n")
    assert 'name: "Château Fixture"' in md
    assert "geo_verified: true" in md
    assert 'google_place_id: "ChIJ_test"' in md
    assert "# Château Fixture" in md
    # HANDOFF-39 facet canon: the eight anchors, byte-verbatim, in order
    body = md.split("---", 2)[2]
    anchors = [ln for ln in body.split("\n") if ln.startswith("##")]
    assert anchors == bac.FACET_HEADINGS["fr"]
    assert "research_log" not in md and "secret" not in md
    assert md.endswith("\n")


def test_md_unverified_geo_false():
    md = bac.render_md(_fiche(geo_verified=False, google_place_id=None))
    assert "geo_verified: false" in md
    assert "google_place_id: null" in md


def test_md_facet_lanes_and_en_canon():
    # HANDOFF-39: facts lines only — the old prose body never leaks in
    md = bac.render_md(_fiche())
    assert "<p>" not in md and "<strong>" not in md
    assert "## Présentation" not in md and "## En bref" not in md
    assert "- Parking" not in md            # Parking is a section, not a bullet
    assert "Gratuit" in md                   # facts.parking rendered under ## Parking
    # unknown lanes: fixture has no tarif/price data and no acces_pmr
    assert "Non renseigné" in md
    # EN file: EN canon anchors + frozen FR name verbatim
    md_en = bac.render_md(_fiche(), "en")
    body = md_en.split("---", 2)[2]
    anchors = [ln for ln in body.split("\n") if ln.startswith("##")]
    assert anchors == bac.FACET_HEADINGS["en"]
    assert "# Château Fixture" in md_en
    assert "Not specified" in md_en


def test_iso_date_french():
    assert bac.iso_date("14 mai 2026") == "2026-05-14"
    assert bac.iso_date("1er juin 2026") == "2026-06-01"
    assert bac.iso_date("3 août 2025") == "2025-08-03"


def test_photo_fields_parse_and_generic():
    assert bac.photo_fields(_fiche())[:1] == ("real",)
    assert bac.photo_fields(_fiche())[1:] == ("Jane Doe", "CC BY-SA 4.0", "Wikimedia Commons")
    gen = _fiche(hero_image="/img/generique-chateau.jpg",
                 hero_credit="Photo générique — à remplacer")
    assert bac.photo_fields(gen) == ("generic", None, None, None)


def test_idempotent():
    d = _fiche()
    assert bac.render_md(d) == bac.render_md(d)


# ── integration: generate + gate ────────────────────────────────────────────
def test_full_generation_and_gate():
    with tempfile.TemporaryDirectory() as base:
        jd = os.path.join(base, "Json"); cd = os.path.join(base, "content")
        os.makedirs(jd); os.makedirs(cd)
        for i in range(3):
            _seed(jd, _fiche(f"lieu-{i}"))
        _seed(jd, _fiche("lieu-sparse", i18n={"fr": {"name": "Sparse"}}))  # minimal
        r = _gen(jd, cd, base)
        assert r.returncode == 0, r.stderr

        # every fiche has an md (no 404s)
        for s in ("lieu-0", "lieu-1", "lieu-2", "lieu-sparse"):
            assert os.path.exists(os.path.join(cd, f"{s}.md"))

        # llms-full header + rulers == 4
        full = open(os.path.join(base, "llms-full.txt"), encoding="utf-8").read()
        assert "Total lieux: 4" in full
        assert len(re.findall(r"^={80}$", full, re.M)) == 4
        assert "research_log" not in full

        # llms.txt total + category counts == 4
        idx = open(os.path.join(base, "llms.txt"), encoding="utf-8").read()
        assert "catalogs 4 leisure" in idx
        assert sum(int(x) for x in re.findall(r"\((\d+)\s+lieux\)", idx)) == 4

        # idempotent: a second run changes nothing
        r2 = _gen(jd, cd, base, "--check")
        assert r2.returncode == 0, r2.stdout + r2.stderr

        # gate passes
        assert _gate(jd, cd, base).returncode == 0


def test_gate_red_on_missing_md():
    with tempfile.TemporaryDirectory() as base:
        jd = os.path.join(base, "Json"); cd = os.path.join(base, "content")
        os.makedirs(jd); os.makedirs(cd)
        _seed(jd, _fiche("lieu-0"))
        _gen(jd, cd, base)
        os.remove(os.path.join(cd, "lieu-0.md"))     # advertised → 404
        r = _gate(jd, cd, base)
        assert r.returncode == 1
        assert "missing" in r.stdout


def test_gate_red_on_count_drift():
    with tempfile.TemporaryDirectory() as base:
        jd = os.path.join(base, "Json"); cd = os.path.join(base, "content")
        os.makedirs(jd); os.makedirs(cd)
        _seed(jd, _fiche("lieu-0"))
        _gen(jd, cd, base)
        p = os.path.join(base, "llms-full.txt")
        open(p, "w", encoding="utf-8").write(
            open(p, encoding="utf-8").read().replace("Total lieux: 1", "Total lieux: 99"))
        r = _gate(jd, cd, base)
        assert r.returncode == 1


def _all_tests():
    return [v for k, v in sorted(globals().items()) if k.startswith("test_")]


if __name__ == "__main__":
    failed = 0
    for t in _all_tests():
        try:
            t(); print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1; print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    total = len(_all_tests())
    print(f"\n{total - failed}/{total} passed")
    sys.exit(1 if failed else 0)
