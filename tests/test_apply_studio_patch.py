#!/usr/bin/env python3
"""Tests for apply_studio_patch.py — SPEC §6.

The headline test is `test_clobber_regression`: it proves a Studio editor patch
touching only one path cannot revert a field a monthly sweep wrote afterwards.
That test IS the answer to "datas écrasé older shit."

Runs with pytest, or standalone: `python3 tests/test_apply_studio_patch.py`.
Uses LOISIRS_JSON_DIR to redirect the ingress at a tmpdir — the real Json/ is
never touched.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "apply_studio_patch.py")


def _fiche():
    """A minimal but representative live fiche, with a sweep-written field."""
    return {
        "slug": "fixture-lieu",
        "category": "musee",
        "hero_image": "/fixture-hero.jpg",
        "hero_credit": "Someone · CC BY-SA · Wikimedia Commons",
        "partners": [{"name": "Chez Nous"}],
        "freshness": {"last_checked": "2026-07-01", "source": "sweep"},
        "research_log": [{"date": "2026-06-01", "by": "seed", "note": "created"}],
        "i18n": {
            "fr": {"name": "Musée Fixture", "intro": "Ancien texte FR."},
            "de": {"name": "Fixture Museum", "intro": "Alter DE-Text."},
        },
    }


def _run(json_dir, patch_obj, *flags):
    patch_path = os.path.join(json_dir, "_patch.json")
    with open(patch_path, "w", encoding="utf-8") as f:
        json.dump(patch_obj, f)
    env = dict(os.environ, LOISIRS_JSON_DIR=json_dir)
    return subprocess.run(
        [sys.executable, SCRIPT, patch_path, *flags],
        capture_output=True, text=True, env=env,
    )


def _seed(json_dir, fiche=None):
    fiche = fiche or _fiche()
    with open(os.path.join(json_dir, f"{fiche['slug']}.json"), "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)
    return fiche


def _read(json_dir, slug):
    with open(os.path.join(json_dir, f"{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def test_clobber_regression():
    """🔒 Editor patch on i18n.fr.intro must NOT revert sweep's freshness, nor
    touch i18n.de / partners / hero_credit."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        r = _run(d, {
            "slug": "fixture-lieu", "source": "studio-editor", "base_head": None,
            "patch": {"i18n.fr.intro": "Nouveau texte FR."},
        })
        assert r.returncode == 0, r.stderr
        out = _read(d, "fixture-lieu")
        assert out["i18n"]["fr"]["intro"] == "Nouveau texte FR."
        # The whole point:
        assert out["freshness"] == {"last_checked": "2026-07-01", "source": "sweep"}
        assert out["i18n"]["de"] == {"name": "Fixture Museum", "intro": "Alter DE-Text."}
        assert out["partners"] == [{"name": "Chez Nous"}]
        assert out["hero_credit"] == "Someone · CC BY-SA · Wikimedia Commons"
        assert out["i18n"]["fr"]["name"] == "Musée Fixture"  # sibling key untouched


def test_noop_skip():
    """Setting a path to its current value is skipped, no research_log churn."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        r = _run(d, {
            "slug": "fixture-lieu", "source": "studio-editor", "base_head": None,
            "patch": {"i18n.fr.intro": "Ancien texte FR."},
        })
        assert r.returncode == 0, r.stderr
        assert "changed=0" in r.stdout
        out = _read(d, "fixture-lieu")
        assert len(out["research_log"]) == 1  # no stamp added for a no-op


def test_idempotency():
    """Applying the same real change twice → 2nd run changes nothing."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        patch = {"slug": "fixture-lieu", "source": "studio-editor", "base_head": None,
                 "patch": {"i18n.fr.intro": "V2."}}
        r1 = _run(d, patch)
        assert "changed=1" in r1.stdout, r1.stdout
        r2 = _run(d, patch)
        assert "changed=0" in r2.stdout, r2.stdout


def test_array_whole_replace():
    """An array path replaces the whole array (no element merge)."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        r = _run(d, {
            "slug": "fixture-lieu", "source": "studio-enricher", "base_head": None,
            "patch": {"partners": [{"name": "New Partner A"}, {"name": "B"}]},
        })
        assert r.returncode == 0, r.stderr
        assert _read(d, "fixture-lieu")["partners"] == [{"name": "New Partner A"}, {"name": "B"}]


def test_delete_pop():
    """delete[] removes a leaf; a missing delete path warns, not fails."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        r = _run(d, {
            "slug": "fixture-lieu", "source": "studio-editor", "base_head": None,
            "patch": {}, "delete": ["i18n.de.intro", "nonexistent.path"],
        })
        assert r.returncode == 0, r.stderr
        out = _read(d, "fixture-lieu")
        assert "intro" not in out["i18n"]["de"]
        assert "deleted=1" in r.stdout


def test_full_file_guard_too_many_paths():
    """A patch with >40 paths is rejected as a disguised full-file dump (exit 2)."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        big = {f"i18n.fr.k{i}": i for i in range(41)}
        r = _run(d, {"slug": "fixture-lieu", "source": "studio-editor",
                     "base_head": None, "patch": big})
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "full-file dump" in r.stderr


def test_full_file_guard_two_whole_locales():
    """Replacing entire i18n.<lang> objects for >=2 locales is rejected (exit 2)."""
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        r = _run(d, {
            "slug": "fixture-lieu", "source": "studio-editor", "base_head": None,
            "patch": {"i18n.fr": {"name": "x"}, "i18n.de": {"name": "y"}},
        })
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "whole i18n" in r.stderr


def test_missing_slug_target():
    """slug with no Json/<slug>.json → exit 3 (no create-via-patch)."""
    with tempfile.TemporaryDirectory() as d:
        r = _run(d, {"slug": "ghost", "source": "studio-editor",
                     "base_head": None, "patch": {"x": 1}})
        assert r.returncode == 3, (r.returncode, r.stderr)


def test_dry_run_writes_nothing():
    with tempfile.TemporaryDirectory() as d:
        _seed(d)
        before = _read(d, "fixture-lieu")
        r = _run(d, {"slug": "fixture-lieu", "source": "studio-editor",
                     "base_head": None, "patch": {"i18n.fr.intro": "DRY"}}, "--dry-run")
        assert r.returncode == 0, r.stderr
        assert "dry-run" in r.stdout
        assert _read(d, "fixture-lieu") == before  # unchanged on disk


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
    print(f"\n{len(_all_tests()) - failed}/{len(_all_tests())} passed")
    sys.exit(1 if failed else 0)
