#!/usr/bin/env python3
"""Tests for the source-existence audit — SPECsourceexistenceaudit §6.

Anchored on the two real cases plus the classifier contract:
  * B&B-name-collision (vacation rental on a trail) → URL-WRONG-ENTITY
  * name-matched entity with huge geo drift → SLUG-COMMUNE-SUSPECT
  * blocklist domain → URL-WRONG-ENTITY ; allowlist/own-site → VERIFIED
  * no URL / unreachable AND no source found → UNVERIFIED, proposed_source null
    (no-fabrication: the job never invents a URL)
  * protected fiches are never in the --apply flag set
  * gate: a held (unverified) slug present in an index → red

Network is monkeypatched out; runs offline. pytest or standalone.
"""
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


aud = _load("audit_sources")
COMMUNES = ["Annecy", "Évian-les-Bains", "Cruseilles", "Chamonix-Mont-Blanc", "Thonon-les-Bains"]


def _mock_fetch(records):
    """Replace aud.fetch with a dict-backed stub keyed by URL."""
    def fake(url, no_fetch=False):
        return records.get(url, {"url": url, "ok": False, "http": None,
                                 "error": "mock-miss", "title": "", "desc": "",
                                 "site_name": "", "final_url": "", "text": ""})
    aud.fetch = fake


def _fiche(slug, **over):
    d = {"slug": slug, "category": "sentier", "commune": "Cruseilles",
         "official_site_url": "https://example.org/", "i18n": {"fr": {"name": "Lieu Test"}}}
    d.update(over)
    return d


# ── entity-match: the B&B class ─────────────────────────────────────────────
def test_bnb_name_collision_is_wrong_entity():
    url = "https://balconduleman.example/"
    _mock_fetch({url: {"url": url, "ok": True, "http": 200, "final_url": url,
                       "title": "Location d'appartements et chalet à Thollon | Vue Léman",
                       "desc": "Locations de vacances, appartements près d'Evian",
                       "site_name": "", "text": "locations de vacances appartements chalet"}})
    d = _fiche("sentier-balcon", official_site_url=url, category="sentier",
               i18n={"fr": {"name": "Sentier du Balcon du Léman"}})
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "URL-WRONG-ENTITY", r
    assert r["proposed_source"] is None


def test_blocklist_domain_is_wrong_entity_without_fetch():
    d = _fiche("x", official_site_url="https://www.booking.com/hotel/fr/xyz.html")
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "URL-WRONG-ENTITY"
    assert "booking.com" in r["domain"]


# ── slug/commune suspect via geo drift ──────────────────────────────────────
def test_namematch_but_huge_drift_is_slug_commune_suspect():
    url = "https://montgolfieres-du-mont-blanc.example/"
    _mock_fetch({url: {"url": url, "ok": True, "http": 200, "final_url": url,
                       "title": "Vol Montgolfière Mont-Blanc, Annecy, Haute-Savoie",
                       "desc": "Vol en montgolfière", "site_name": "", "text": "annecy montgolfiere"}})
    d = _fiche("montgolfiere-evian", category="attraction", commune="Évian-les-Bains",
               official_site_url=url, i18n={"fr": {"name": "Montgolfières du Mont-Blanc"}},
               google_check={"gps_drift_m": 65000})
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "SLUG-COMMUNE-SUSPECT", r


# ── allowlist / own-site → VERIFIED with a named corroborator ────────────────
def test_official_allowlist_is_verified():
    url = "https://www.ffrandonnee.fr/randonnee/gr-balcon"
    _mock_fetch({url: {"url": url, "ok": True, "http": 200, "final_url": url,
                       "title": "GR Balcon du Léman — FFRandonnée", "desc": "", "site_name": "",
                       "text": "randonnee"}})
    d = _fiche("trail", official_site_url=url, i18n={"fr": {"name": "Balcon du Léman"}})
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "VERIFIED"
    assert r["proposed_source"] == url      # named corroborator, not invented


def test_ownsite_namematch_is_verified():
    url = "https://musee-alpin-chamonix.example/"
    _mock_fetch({url: {"url": url, "ok": True, "http": 200, "final_url": url,
                       "title": "Musée Alpin de Chamonix", "desc": "", "site_name": "",
                       "text": "musee alpin"}})
    d = _fiche("musee-alpin", category="musee", commune="Chamonix-Mont-Blanc",
               official_site_url=url, i18n={"fr": {"name": "Musée Alpin Chamonix"}})
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "VERIFIED"


# ── no-fabrication ──────────────────────────────────────────────────────────
def test_no_url_is_unverified_no_proposed():
    d = _fiche("orphan", official_site_url=None)
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "UNVERIFIED"
    assert r["proposed_source"] is None


def test_unreachable_url_is_unverified_no_proposed():
    url = "https://dead.example/"
    _mock_fetch({url: {"url": url, "ok": False, "http": 503, "error": "HTTPError",
                       "title": "", "desc": "", "site_name": "", "text": ""}})
    d = _fiche("dead", official_site_url=url)
    r = aud.classify(d, COMMUNES)
    assert r["verdict"] == "UNVERIFIED"
    assert r["proposed_source"] is None


# ── protected fiches never flagged ──────────────────────────────────────────
def test_protected_set_covers_partner_hosts_and_fiche():
    fiches = [
        {"slug": "domaine-du-tornet", "partners": []},
        {"slug": "plage-host", "partners": [{"name": "Chez Nous à la Plage"}]},
        {"slug": "climb-host", "featured_businesses": [{"name": "Chalet du Tornet"}]},
        {"slug": "normal", "partners": [{"name": "Some Café"}]},
    ]
    prot = aud.protected_slugs(fiches)
    assert prot == {"domaine-du-tornet", "plage-host", "climb-host"}
    # mirror main()'s flaggable predicate: protected never flagged
    results = [{"slug": s, "verdict": "UNVERIFIED", "protected": s in prot}
               for s in ("plage-host", "normal")]
    flaggable = [r for r in results if r["verdict"] != "VERIFIED" and not r["protected"]]
    assert [r["slug"] for r in flaggable] == ["normal"]


# ── gate ────────────────────────────────────────────────────────────────────
def test_gate_red_when_held_fiche_indexed():
    gate = _load("gate_published_verified")
    with tempfile.TemporaryDirectory() as base:
        jd = os.path.join(base, "Json"); os.makedirs(jd)
        json.dump({"slug": "held-one", "status": "unverified"},
                  open(os.path.join(jd, "held-one.json"), "w"))
        json.dump({"slug": "ok-one", "status": "published"},
                  open(os.path.join(jd, "ok-one.json"), "w"))
        # a catalog that wrongly still lists the held fiche
        json.dump([{"slug": "held-one"}, {"slug": "ok-one"}],
                  open(os.path.join(base, "catalog-index.json"), "w"))
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gate_published_verified.py"),
                            "--json-dir", jd, "--root", base], capture_output=True, text=True)
        assert r.returncode == 1
        assert "held-one" in r.stdout


def test_gate_green_when_held_fiche_absent():
    gate_path = os.path.join(SCRIPTS, "gate_published_verified.py")
    with tempfile.TemporaryDirectory() as base:
        jd = os.path.join(base, "Json"); os.makedirs(jd)
        json.dump({"slug": "held-one", "status": "unverified"},
                  open(os.path.join(jd, "held-one.json"), "w"))
        json.dump([{"slug": "ok-one"}], open(os.path.join(base, "catalog-index.json"), "w"))
        import subprocess
        r = subprocess.run([sys.executable, gate_path, "--json-dir", jd, "--root", base],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout


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
