#!/usr/bin/env python3
"""Tests for the geo-verify lane — SPECgeoverify §6.

Covers the four scripts of the lane:
  * derive_geo_verified.py — the earn-only rule, precedence, idempotency
  * build_lieu_page.py     — the ✅ badge (×6 langs) + destination_place_id pin
  * gate_geo_verified.py   — no orphan / hand-set stamps
  * audit_geo_drift.py     — FIX-COORD / RE-MATCH / NO-MATCH bucketing

Runs with pytest, or standalone: `python3 tests/test_geo_verified.py`.
Integration tests redirect each script at a tmpdir via --json-dir; the real
Json/ is never touched.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def _load(modname):
    path = os.path.join(SCRIPTS, f"{modname}.py")
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


derive = _load("derive_geo_verified")
blp = _load("build_lieu_page")


# ── fixtures ────────────────────────────────────────────────────────────────
def _fiche(slug="fixture-lieu", **over):
    d = {
        "slug": slug,
        "category": "musee",
        "commune": "Annecy",
        "latitude": 45.8992,
        "longitude": 6.1294,
        "i18n": {"fr": {"name": "Abbaye d'Aulps"}},
        "freshness": {"google_match": "Abbaye d'Aulps - Domaine", "gps_drift_m": 6,
                      "place_id": "ChIJ_fresh"},
    }
    d.update(over)
    return d


def _seed(json_dir, fiche):
    with open(os.path.join(json_dir, f"{fiche['slug']}.json"), "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)


def _read(json_dir, slug):
    with open(os.path.join(json_dir, f"{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def _run(script, json_dir, *flags):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script), "--json-dir", json_dir, *flags],
        capture_output=True, text=True,
    )


# ── G1: derive rule (unit, pure) ────────────────────────────────────────────
def test_rule_verified_when_all_three_hold():
    info = derive.derive_one(_fiche(), max_drift=100)
    assert info["verified"] is True
    assert info["reason"] == "verified"


def test_rule_rejected_when_drift_over_threshold():
    d = _fiche(freshness={"google_match": "Abbaye d'Aulps", "gps_drift_m": 250,
                          "place_id": "ChIJx"})
    info = derive.derive_one(d, max_drift=100)
    assert info["verified"] is False
    assert "drift" in info["reason"]


def test_rule_rejected_when_name_weak():
    d = _fiche(i18n={"fr": {"name": "Télécabine des Chavannes"}},
               freshness={"google_match": "Télésiège Express Truc", "gps_drift_m": 5,
                          "place_id": "ChIJx"})
    info = derive.derive_one(d, max_drift=100)
    assert info["verified"] is False
    assert info["reason"].startswith("name-overlap")


def test_rule_rejected_when_no_place_id():
    d = _fiche(freshness={"google_match": "Abbaye d'Aulps", "gps_drift_m": 6})
    info = derive.derive_one(d, max_drift=100)
    assert info["verified"] is False
    assert info["reason"] == "no place_id"


def test_precedence_google_check_over_freshness():
    # google_check says drift 5 (passes); freshness says 999 (would fail).
    d = _fiche(google_check={"place_id": "ChIJ_gc", "gps_drift_m": 5},
               freshness={"google_match": "Abbaye d'Aulps", "gps_drift_m": 999,
                          "place_id": "ChIJ_fresh"})
    info = derive.derive_one(d, max_drift=100)
    assert info["place_id"] == "ChIJ_gc"   # google_check wins
    assert info["drift"] == 5
    assert info["verified"] is True


def test_overlap_directional_not_jaccard():
    # Our short name fully contained in Google's longer name -> 1.0 directional.
    assert derive.name_overlap("Abbaye d'Aulps",
                               "Abbaye d'Aulps - Domaine de Découverte") == 1.0
    # Stop-words ignored.
    assert derive.name_overlap("Col de la Colombière", "Col Colombière") == 1.0


# ── G1: derive integration (idempotency, self-heal, two-tier write) ─────────
def test_derive_writes_then_idempotent():
    with tempfile.TemporaryDirectory() as d:
        _seed(d, _fiche())
        r1 = _run("derive_geo_verified.py", d)
        assert r1.returncode == 0, r1.stderr
        out = _read(d, "fixture-lieu")
        assert out["geo_verified"] is True
        assert out["google_place_id"] == "ChIJ_fresh"
        assert out["geo_verified_drift_m"] == 6
        # Re-run: nothing should change.
        r2 = _run("derive_geo_verified.py", d)
        assert "0 fiche file(s) changed" in r2.stdout, r2.stdout


def test_derive_google_place_id_even_when_unverified():
    # drift 250 -> no badge, but google_place_id still written (powers the pin).
    with tempfile.TemporaryDirectory() as d:
        _seed(d, _fiche(freshness={"google_match": "Abbaye d'Aulps",
                                   "gps_drift_m": 250, "place_id": "ChIJp"}))
        _run("derive_geo_verified.py", d)
        out = _read(d, "fixture-lieu")
        assert out.get("geo_verified") is None
        assert out["google_place_id"] == "ChIJp"


def test_derive_self_heals_stale_stamp():
    # Seed an already-verified fiche, then worsen the drift; re-derive strips it.
    with tempfile.TemporaryDirectory() as d:
        _seed(d, _fiche())
        _run("derive_geo_verified.py", d)
        out = _read(d, "fixture-lieu")
        out["freshness"]["gps_drift_m"] = 5000  # drift blew up
        _seed(d, out)
        _run("derive_geo_verified.py", d)
        healed = _read(d, "fixture-lieu")
        assert "geo_verified" not in healed
        assert "geo_verified_drift_m" not in healed


# ── G2/G3: render (badge ×6 langs, pin param) ───────────────────────────────
def test_badge_renders_only_when_verified_all_langs():
    d = _fiche()
    d["geo_verified"] = True
    d["google_place_id"] = "ChIJ_fresh"
    for lang in ("fr", "en", "de", "it", "es", "nl"):
        html = blp.build_page(d, lang)
        assert 'class="geo-verified' in html, f"badge missing in {lang}"


def test_badge_absent_when_not_verified():
    d = _fiche()  # no geo_verified
    d["google_place_id"] = "ChIJ_fresh"
    html = blp.build_page(d, "fr")
    assert 'class="geo-verified' not in html


def test_destination_place_id_present_when_google_place_id():
    d = _fiche()
    d["google_place_id"] = "ChIJ_pin"
    html = blp.build_page(d, "fr")
    assert "destination_place_id=ChIJ_pin" in html
    assert "query_place_id=ChIJ_pin" in html


def test_path_a_fallback_when_no_place_id():
    d = _fiche()  # no google_place_id
    html = blp.build_page(d, "fr")
    assert "_place_id=" not in html        # neither destination_ nor query_
    assert "/maps/dir/?api=1&destination=" in html  # Path A still present


# ── G4: triage bucketing ────────────────────────────────────────────────────
def test_triage_buckets():
    with tempfile.TemporaryDirectory() as d:
        # FIX-COORD: big drift, strong name, Google coord inside Haute-Savoie.
        _seed(d, _fiche("fixcoord", freshness={},
                        i18n={"fr": {"name": "Lac d'Annecy"}},
                        google_check={"place_id": "ChIJ1", "gps_drift_m": 800,
                                      "match": "Lac d'Annecy",
                                      "google_lat": 45.85, "google_lng": 6.17}))
        # RE-MATCH (weak name): big drift, weak name.
        _seed(d, _fiche("rematch_weak", freshness={},
                        i18n={"fr": {"name": "Plage Municipale"}},
                        google_check={"place_id": "ChIJ2", "gps_drift_m": 900,
                                      "match": "Café du Port",
                                      "google_lat": 45.9, "google_lng": 6.2}))
        # RE-MATCH (out of region): strong name BUT Google coord near Orléans.
        _seed(d, _fiche("rematch_region", freshness={},
                        i18n={"fr": {"name": "Château de Bellegarde"}},
                        google_check={"place_id": "ChIJ3", "gps_drift_m": 350000,
                                      "match": "Château de Bellegarde",
                                      "google_lat": 47.98, "google_lng": 2.44}))
        # NO-MATCH: no signals at all.
        _seed(d, _fiche("nomatch", freshness={}))
        r = _run("audit_geo_drift.py", d, "--report",
                 os.path.join(d, "triage.md"))
        assert r.returncode == 0, r.stderr
        report = open(os.path.join(d, "triage.md"), encoding="utf-8").read()

        def bucket_of(slug):
            for name in ("FIX-COORD", "RE-MATCH", "NO-MATCH"):
                sec = report.split(f"## {name}")[1].split("\n## ")[0]
                if f"| {slug} " in sec:
                    return name
            return None

        assert bucket_of("fixcoord") == "FIX-COORD"
        assert bucket_of("rematch_weak") == "RE-MATCH"
        assert bucket_of("rematch_region") == "RE-MATCH"   # the bbox guard
        assert bucket_of("nomatch") == "NO-MATCH"


# ── G5: gate ────────────────────────────────────────────────────────────────
def test_gate_passes_clean():
    with tempfile.TemporaryDirectory() as d:
        _seed(d, _fiche())
        _run("derive_geo_verified.py", d)        # legitimately derived stamp
        r = _run("gate_geo_verified.py", d)
        assert r.returncode == 0, r.stdout + r.stderr


def test_gate_fails_handset_stamp():
    with tempfile.TemporaryDirectory() as d:
        forged = _fiche("forged", freshness={})  # no place_id / drift
        forged["geo_verified"] = True            # hand-set ✅
        _seed(d, forged)
        r = _run("gate_geo_verified.py", d)
        assert r.returncode == 1
        assert "no google_place_id" in r.stdout


def _all_tests():
    return [v for k, v in sorted(globals().items()) if k.startswith("test_")]


if __name__ == "__main__":
    failed = 0
    for t in _all_tests():
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    total = len(_all_tests())
    print(f"\n{total - failed}/{total} passed")
    sys.exit(1 if failed else 0)
