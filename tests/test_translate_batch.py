#!/usr/bin/env python3
"""HANDOFF-25 — translate_batch validation + retry, adversarially tested offline.

Proves the standard-keeper:
  * all 4 validation checks (key parity, frozen nouns, HTML parity,
    length ratio / empty strings) reject bad results;
  * a seeded bad result is retried ONCE and a good retry is written;
  * a twice-failing result is logged to the failures report and the
    field stays ABSENT (null discipline);
  * idempotent: a populated fiche×lang pair is skipped on re-run;
  * --dry-run writes nothing and never needs an API key.

Network/SDK is mocked out; runs offline. pytest or standalone.
"""
import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load():
    spec = importlib.util.spec_from_file_location(
        "translate_batch_t", os.path.join(ROOT, "scripts", "translate_batch.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SRC = {
    "meta_title": "Abbaye d'Aulps · Rates and Hours (Saint-Jean-d'Aulps)",
    "hero": {"lead": "A 900-year-old abbey above the Lac d'Annecy road."},
    "body": {"what_is": "<p>A Cistercian abbey in <strong>Haute-Savoie</strong>.</p>"},
    "faq": [{"q": "Is it open?", "a": "Yes, year-round."}],
}
FROZEN = ["Lac d'Annecy", "Haute-Savoie", "Abbaye d'Aulps", "Saint-Jean-d'Aulps"]


def _good():
    return {
        "meta_title": "Abbaye d'Aulps · Ceny i godziny (Saint-Jean-d'Aulps)",
        "hero": {"lead": "Opactwo sprzed 900 lat przy drodze nad Lac d'Annecy."},
        "body": {"what_is": "<p>Opactwo cysterskie w <strong>Haute-Savoie</strong>.</p>"},
        "faq": [{"q": "Czy jest otwarte?", "a": "Tak, przez cały rok."}],
    }


# ------------------------------------------------------------------ validate()

def test_valid_translation_passes():
    m = _load()
    assert m.validate(SRC, _good(), FROZEN) == []


def test_key_parity_rejects_missing_and_invented():
    m = _load()
    out = _good(); del out["faq"]
    assert any("parity" in v for v in m.validate(SRC, out, FROZEN))
    out = _good(); out["invented_field"] = "boo"
    assert any("parity" in v for v in m.validate(SRC, out, FROZEN))


def test_frozen_noun_loss_rejected():
    m = _load()
    out = _good()
    out["hero"]["lead"] = "Opactwo nad jeziorem Annecy."  # translated the lake!
    assert any("frozen noun" in v and "Lac d'Annecy" in v
               for v in m.validate(SRC, out, FROZEN))


def test_html_parity_and_escaped_tags_rejected():
    m = _load()
    out = _good()
    out["body"]["what_is"] = "Opactwo cysterskie w Haute-Savoie."   # tags dropped
    assert any("HTML" in v for v in m.validate(SRC, out, FROZEN))
    out = _good()
    out["body"]["what_is"] = "&lt;p&gt;Opactwo w <strong>Haute-Savoie</strong>.&lt;/p&gt;"
    assert any("escaped" in v or "HTML" in v for v in m.validate(SRC, out, FROZEN))


def test_length_ratio_and_empty_strings_rejected():
    m = _load()
    out = _good()
    out["meta_title"] = "A"
    out["hero"]["lead"] = "Lac d'Annecy"
    out["body"]["what_is"] = "<p><strong>Haute-Savoie</strong></p>"
    out["faq"] = [{"q": "?", "a": "!"}]
    assert any("ratio" in v for v in m.validate(SRC, out, FROZEN))
    out = _good()
    out["faq"][0]["a"] = ""
    assert any("empty translation" in v for v in m.validate(SRC, out, FROZEN))


# -------------------------------------------------------------- custom_id spec

def test_custom_id_meets_api_spec_for_every_real_slug():
    """Run #2 regression: '<slug>:<lang>' 400'd on the colon AND on 73-char
    slugs. Every generated id must match ^[a-zA-Z0-9_-]{1,64}$ and stay unique
    even when truncation eats the distinguishing suffix."""
    m = _load()
    long_a = "musee-patrimonial-pays-thones-fondateurs-francois-et-lucien-cochat-thones"
    long_b = long_a[:-6] + "annecy"          # same 64-char prefix after truncation
    slugs = ["abbaye-d-aulps", long_a, long_b]
    ids = [m.make_custom_id("pt", i, s) for i, s in enumerate(slugs)]
    for cid in ids:
        assert API_CUSTOM_ID_RE.match(cid), cid
    assert len(set(ids)) == len(ids), "index must keep truncated ids unique"


# --------------------------------------------------------- end-to-end w/ mock

import re as _re
API_CUSTOM_ID_RE = _re.compile(r"^[a-zA-Z0-9_-]{1,64}$")   # the real API constraint


class FakeBatches:
    """Scripted batch API: each create() pops the next results dict (keyed by
    SLUG). Enforces the real custom_id constraint — the original fake was too
    permissive and let the '<slug>:<lang>' 400 (run #2) escape to production."""
    def __init__(self, rounds):
        self.rounds = rounds       # list of {slug: ('ok', text)|('error', why)}
        self.created = []          # requests of each submitted batch

    def create(self, requests):
        seen = set()
        for r in requests:
            cid = r["custom_id"]
            assert API_CUSTOM_ID_RE.match(cid), \
                f"API would 400: custom_id {cid!r} violates ^[a-zA-Z0-9_-]{{1,64}}$"
            assert cid not in seen, f"duplicate custom_id {cid!r}"
            seen.add(cid)
        self.created.append(requests)
        return type("B", (), {"id": f"batch_{len(self.created)}",
                              "processing_status": "in_progress"})()

    def retrieve(self, batch_id):
        counts = type("C", (), {"succeeded": 0, "errored": 0, "expired": 0, "processing": 0})()
        return type("B", (), {"id": batch_id, "processing_status": "ended",
                              "request_counts": counts})()

    def results(self, batch_id):
        idx = int(batch_id.rsplit("_", 1)[1]) - 1
        for req in self.created[idx]:
            cid = req["custom_id"]
            slug = cid.split("-", 2)[2]          # "<lang>-<idx>-<slug>" (untruncated in tests)
            kind, payload = self.rounds[idx][slug]
            if kind == "ok":
                blk = type("T", (), {"type": "text", "text": payload})()
                msg = type("M", (), {"content": [blk]})()
                res = type("R", (), {"type": "succeeded", "message": msg})()
            else:
                res = type("R", (), {"type": payload})()
            yield type("Row", (), {"custom_id": cid, "result": res})()


class FakeClient:
    def __init__(self, rounds):
        self.messages = type("Msgs", (), {})()
        self.messages.batches = FakeBatches(rounds)


def _fixture_repo(m, tmp):
    jd = Path(tmp) / "Json"; jd.mkdir()
    for slug in ("good-one", "bad-then-good", "bad-twice"):
        fiche = {"slug": slug, "commune": "Annecy",
                 "i18n": {"fr": {"name": "Abbaye d'Aulps"}, "en": dict(SRC)}}
        (jd / f"{slug}.json").write_text(
            json.dumps(fiche, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    m.JSON_DIR = jd
    m.STATE_FILE = Path(tmp) / "reports" / "state.json"
    m.FAILURES_MD = Path(tmp) / "reports" / "failures.md"
    m.time.sleep = lambda s: None
    return jd


def test_seeded_bad_result_retried_once_then_logged():
    m = _load()
    with tempfile.TemporaryDirectory() as tmp:
        jd = _fixture_repo(m, tmp)
        good = json.dumps(_good(), ensure_ascii=False)
        bad = json.dumps({"meta_title": "tylko tytuł"}, ensure_ascii=False)  # parity fail
        rounds = [
            {   # round 1: one good, two seeded-bad
                "good-one": ("ok", good),
                "bad-then-good": ("ok", bad),
                "bad-twice": ("ok", bad),
            },
            {   # retry round: one recovers, one fails again
                "bad-then-good": ("ok", good),
                "bad-twice": ("ok", bad),
            },
        ]
        client = FakeClient(rounds)
        args = argparse.Namespace(dry_run=False, force=False)
        ok = m.run_language("pl", args, client)
        assert not ok, "run must report failure when a pair fails twice"

        batches = client.messages.batches
        assert len(batches.created) == 2, "exactly one retry batch"
        retry_slugs = sorted(r["custom_id"].split("-", 2)[2] for r in batches.created[1])
        assert retry_slugs == ["bad-then-good", "bad-twice"]

        d = json.loads((jd / "good-one.json").read_text())
        assert d["i18n"]["pl"]["meta_title"].startswith("Abbaye d'Aulps")
        d = json.loads((jd / "bad-then-good.json").read_text())
        assert "faq" in d["i18n"]["pl"], "recovered retry must be written"
        d = json.loads((jd / "bad-twice.json").read_text())
        assert "pl" not in d.get("i18n", {}), \
            "twice-failed pair must stay ABSENT (null discipline)"
        assert "bad-twice" in m.FAILURES_MD.read_text(encoding="utf-8")


def test_idempotent_rerun_skips_populated_pairs():
    m = _load()
    with tempfile.TemporaryDirectory() as tmp:
        jd = _fixture_repo(m, tmp)
        # populate good-one fully
        p = jd / "good-one.json"
        d = json.loads(p.read_text()); d["i18n"]["pl"] = _good()
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pairs = m.pairs_for_lang("pl")
        slugs = [f["slug"] for f, _ in pairs]
        assert "good-one" not in slugs and len(slugs) == 2
        assert len(m.pairs_for_lang("pl", force=True)) == 3


def test_dry_run_writes_nothing_and_needs_no_key():
    m = _load()
    with tempfile.TemporaryDirectory() as tmp:
        jd = _fixture_repo(m, tmp)
        before = {p.name: p.read_bytes() for p in jd.glob("*.json")}
        args = argparse.Namespace(dry_run=True, force=False)
        assert m.run_language("pl", args, client=None) is True
        assert {p.name: p.read_bytes() for p in jd.glob("*.json")} == before
        assert not m.STATE_FILE.exists()


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
