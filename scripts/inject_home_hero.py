#!/usr/bin/env python3
"""inject_home_hero.py: "What shall we do today?" block on the 12 homepages.

WHAT IT RENDERS
  Inside the existing hero, under the headline and lede (which stay: they are
  the page's H1 and its search wording):

      Qu'est-ce qu'on fait aujourd'hui ?
      [ Un lieu, une commune… ex. Annecy          ]   ← live search
      [ Quand il pleut ]  [ Sorties gratuites ]  [ Lieux accessibles ]
        24 lieux…           175 lieux…            20 lieux…

  The owner's mock-up, applied ON TOP of the homepage, never instead of it:
  the 329 links below the hero are how the fiches are reached, and the
  reachability gate depends on them.

HONEST BY CONSTRUCTION
  - Each card links to a page that exists in that language, or the build
    fails. The rain and accessibility cards go to the département-wide intent
    hubs. The free card goes to sorties-gratuites-haute-savoie where that
    language has it, otherwise to the Lake Annecy free-places hub.
  - Every count is read at build time from the target page itself: the
    distinct fiches it links inside <main>. No number is typed by hand.
  - The search filters /catalog-index.json (the 435 published lieux, loaded
    on first focus) by name and commune. Results link to the fiche in the
    page's language. Enter opens the first result.

  Colors are locked hex, no CSS vars: a cream panel with dark text, like the
  sister card. A var-driven color in the hero zone has been invisible in one
  of the modes twice already.

  Static markup, no element appears after load: nothing can shift the layout
  (CLS). The results list is absolutely positioned and only opens on input.

Usage:
    python3 scripts/inject_home_hero.py            # report, writes nothing
    python3 scripts/inject_home_hero.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import glob
import html as html_lib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import siteconfig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "data" / "home-hero.json").read_text(encoding="utf-8"))
REGISTRY = {p["id"]: p for p in json.loads(
    (ROOT / "data" / "intent-registry.json").read_text(encoding="utf-8"))["pages"]}
CATALOG = {c["slug"] for c in json.loads((ROOT / "catalog-index.json").read_text(encoding="utf-8"))}
BASE = siteconfig.BASE_URL.rstrip("/")
MARK_A, MARK_B = "<!--home-hero:start-->", "<!--home-hero:end-->"
FENCE_RE = re.compile(re.escape(MARK_A) + r".*?" + re.escape(MARK_B), re.S)
HERO_RE = re.compile(r'<div class="wrap hero-content">.*?<p class="lede">.*?</p>', re.S)


def esc(t):
    return html_lib.escape(t, quote=False)


def lang_prefix(lang):
    return "" if lang == "fr" else f"{lang}/"


def intent_file(intent_id, lang):
    entry = REGISTRY[intent_id]
    sub = entry["sub"].get(lang) or entry["sub"]["fr"]
    hits = [p for p in glob.glob(str(ROOT / lang_prefix(lang) / "*" / sub / "index.html"))
            if Path(p).parent.parent.parent == ROOT / lang_prefix(lang).rstrip("/")
            or (lang == "fr" and Path(p).parent.parent.parent == ROOT)]
    return Path(hits[0]) if len(hits) == 1 else None


def target(card, lang):
    """The page this card opens in this language, as a file path."""
    if "page" in card:
        p = ROOT / lang_prefix(lang) / f"{card['page']}.html"
        if p.is_file():
            return p
        return intent_file(card["intent_fallback"], lang)
    return intent_file(card["intent"], lang)


def url_of(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-len('index.html')]}"
    return f"{BASE}/{rel[:-len('.html')]}"


def count_lieux(path):
    s = path.read_text(encoding="utf-8")
    m = re.search(r"<main.*?</main>", s, re.S)
    found = set()
    for href in re.findall(r'href="([^"#?]+)', m.group(0) if m else s):
        slug = href.rstrip("/").split("/")[-1].removesuffix(".html")
        if slug in CATALOG:
            found.add(slug)
    return len(found)


CSS = (
    ".hh{position:relative;z-index:12;margin:26px 0 0;max-width:760px;background:#fdfaf3;"
    "color:#1c1814;border-radius:22px;padding:22px 20px 20px;box-shadow:0 10px 34px rgba(0,0,0,.18)}"
    ".hh-q{font-size:clamp(1.35rem,4.6vw,2rem);line-height:1.15;font-weight:700;"
    "letter-spacing:-.01em;margin:0 0 14px;color:#1c1814}"
    ".hh form{position:relative;margin:0}"
    ".hh-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}"
    ".hh input{box-sizing:border-box;width:100%;padding:15px 20px;border-radius:999px;"
    "border:2px solid #d8cdb8;background:#fff;color:#1c1814;font:inherit;font-size:1.05rem;"
    "box-shadow:0 6px 20px rgba(20,51,58,.12)}"
    ".hh input::placeholder{color:#7a6c58}"
    ".hh input:focus{outline:none;border-color:#1f6e78}"
    ".hh-res{list-style:none;margin:8px 0 0;padding:6px;background:#fff;border:1px solid #e3d9c6;"
    "border-radius:16px;position:absolute;left:0;right:0;z-index:30;max-height:340px;overflow:auto;"
    "box-shadow:0 14px 36px rgba(0,0,0,.18)}"
    ".hh-res a{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;"
    "border-radius:10px;color:#1c1814;text-decoration:none}"
    ".hh-res a:hover,.hh-res a:focus{background:#f1ead9;outline:none}"
    ".hh-res span{color:#6b5d4b;font-size:.85em;white-space:nowrap}"
    ".hh-none{padding:10px 12px;color:#6b5d4b}"
    ".hh-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:16px}"
    ".hh-card{display:block;background:#fff;border-radius:16px;overflow:hidden;color:#1c1814;"
    "text-decoration:none;box-shadow:0 4px 16px rgba(0,0,0,.08);transition:transform .2s ease}"
    ".hh-card:hover,.hh-card:focus-visible{transform:translateY(-3px);outline:none}"
    ".hh-band{height:46px}"
    ".hh-rain{background:linear-gradient(135deg,#7dd3fc,#0369a1)}"
    ".hh-free{background:linear-gradient(135deg,#bbf7d0,#15803d)}"
    ".hh-acc{background:linear-gradient(135deg,#fde68a,#d97706)}"
    ".hh-card b{display:block;padding:10px 14px 2px;font-size:1rem}"
    ".hh-card small{display:block;padding:0 14px 12px;color:#5b4f40;font-size:.85rem;line-height:1.35}"
    "@media (prefers-reduced-motion:reduce){.hh-card{transition:none}}"
)

# The search: loads /catalog-index.json once, matches every typed word against
# name + commune (accents ignored), names first, 8 results max.
JS = (
    "(function(){var f=document.getElementById('hh-in'),box=document.getElementById('hh-res'),"
    "form=document.getElementById('hh-form');if(!f||!box||!form)return;var P=f.getAttribute('data-prefix'),"
    "NONE=f.getAttribute('data-none'),data=null,pending=null;"
    "function norm(s){return(s||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase()}"
    "function esc(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
    "function load(){if(pending)return pending;pending=fetch('/catalog-index.json').then(function(r){return r.json()})"
    ".then(function(j){data=j.map(function(x){return{s:x.slug,n:x.name,c:x.commune||'',kn:norm(x.name),kc:norm(x.commune)}});return data})"
    ".catch(function(){pending=null;return[]});return pending}"
    "function render(){var q=norm(f.value.trim());if(q.length<2||!data){box.hidden=true;box.innerHTML='';return}"
    "var w=q.split(/\\s+/),a=[],b=[];data.forEach(function(d){var k=d.kn+' '+d.kc;"
    "if(w.every(function(x){return k.indexOf(x)>=0})){(w.every(function(x){return d.kn.indexOf(x)>=0})?a:b).push(d)}});"
    "var out=a.concat(b).slice(0,8);box.innerHTML=out.length?out.map(function(d){return'<li><a href=\"'+P+d.s+'\">'"
    "+esc(d.n)+'<span>'+esc(d.c)+'</span></a></li>'}).join(''):'<li class=\"hh-none\">'+esc(NONE)+'</li>';box.hidden=false}"
    "f.addEventListener('focus',load);f.addEventListener('input',function(){load().then(render)});"
    "f.addEventListener('keydown',function(e){if(e.key==='Escape'){box.hidden=true}});"
    "form.addEventListener('submit',function(e){e.preventDefault();var a=box.querySelector('a');if(a)location.href=a.href})"
    "})();"
)


def render(lang):
    c = CFG["copy"].get(lang) or CFG["copy"]["fr"]
    cards = []
    for key, cls in (("rain", "hh-rain"), ("free", "hh-free"), ("acc", "hh-acc")):
        path = target(CFG["cards"][key], lang)
        if path is None:
            raise SystemExit(f"FAIL: no target page for card {key!r} in {lang}")
        n = count_lieux(path)
        if n == 0:
            raise SystemExit(f"FAIL: card {key!r} in {lang}: {path} links no fiche")
        cards.append(
            f'<a class="hh-card" href="{html_lib.escape(url_of(path))}">'
            f'<div class="hh-band {cls}" aria-hidden="true"></div>'
            f'<b>{esc(c[key + "_t"])}</b><small>{esc(c[key + "_d"].replace("{n}", str(n)))}</small></a>')
    prefix = f"/{lang_prefix(lang)}"
    return (
        f'{MARK_A}<style>{CSS}</style><div class="hh">'
        f'<p class="hh-q">{esc(c["q"])}</p>'
        f'<form id="hh-form" role="search" autocomplete="off">'
        f'<label class="hh-sr" for="hh-in">{esc(c["label"])}</label>'
        f'<input id="hh-in" type="search" placeholder="{html_lib.escape(c["ph"])}" '
        f'data-prefix="{prefix}" data-none="{html_lib.escape(c["none"])}">'
        f'<ul id="hh-res" class="hh-res" hidden aria-live="polite"></ul></form>'
        f'<div class="hh-cards">{"".join(cards)}</div></div>'
        f'<script>{JS}</script>{MARK_B}'
    )


def homepages():
    yield "fr", ROOT / "index.html"
    for lang in CFG["copy"]:
        if lang != "fr" and (ROOT / lang / "index.html").is_file():
            yield lang, ROOT / lang / "index.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    changed = total = 0
    for lang, path in homepages():
        total += 1
        text = path.read_text(encoding="utf-8")
        stripped = FENCE_RE.sub("", text)
        m = list(HERO_RE.finditer(stripped))
        if len(m) != 1:
            raise SystemExit(f"FAIL: {path.relative_to(ROOT)}: hero anchor found {len(m)} times")
        i = m[0].end()
        new = stripped[:i] + render(lang) + stripped[i:]
        if new != text:
            changed += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")
    print(f"home hero: {total} homepages, {changed} changed "
          f"[{'applied' if args.apply else 'dry run'}]")


if __name__ == "__main__":
    main()
