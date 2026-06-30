#!/usr/bin/env python3
"""locales.py — the locale roster, derived (HANDOFF-10 Job 1).

The single place that reads data/languages.json and exposes the exact rosters
the builders used to hardcode. Every builder, the picker, and hreflang import
from here instead of repeating a `LANGS = [...]` literal, so adding a language
is a data edit + render — not a five-file hunt (the same drift class as a stale
doc).

Derived rosters (order preserved from data/languages.json):
  PUBLISHED         ('fr','en','de','it','es','nl')  — the live originals; full
                    trees, in sitemap + hreflang + picker.
  SECONDARY         ('en','de','it','es','nl')        — PUBLISHED minus the root
                    locale (fr renders at the site root, the others under /<lang>/).
  STAGED_INDEXABLE  ('pl','pt','cs')                  — indexable pilot: own
                    sitemap URLs, self-canonical, NEVER picker/hreflang.
  HELD              ('ar','he')                        — vocab-verified, render-blocked.

ENDONYM / DIR are per-language maps (endonym = the language's own name, never a
flag; dir = ltr|rtl). endonyms(langs) returns an ordered {lang: endonym} subset
for the picker / lang_native chrome.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(ROOT, "data", "languages.json")
_DATA = json.loads(open(_PATH, encoding="utf-8").read())

LANGUAGES = _DATA["languages"]  # insertion-ordered (declared order)


def _by_status(*statuses):
    return tuple(l for l, v in LANGUAGES.items() if v.get("status") in statuses)


PUBLISHED = _by_status("published")
SECONDARY = tuple(l for l in PUBLISHED if not LANGUAGES[l].get("root"))
STAGED_INDEXABLE = _by_status("staged-indexable")
STAGED = _by_status("staged")
HELD = _by_status("held")

ENDONYM = {l: v["endonym"] for l, v in LANGUAGES.items()}
DIR = {l: v.get("dir", "ltr") for l, v in LANGUAGES.items()}
STATUS = {l: v.get("status") for l, v in LANGUAGES.items()}


def endonyms(langs):
    """Ordered {lang: endonym} for the given roster (picker / lang_native)."""
    return {l: ENDONYM[l] for l in langs}


def status(lang):
    return STATUS.get(lang)
