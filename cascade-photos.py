#!/usr/bin/env python3
"""
cascade-photos.py — Loisirs 74
==============================
Assign real hero photos to cascade pages that were on a générique
placeholder, and propagate the photo to every card for that place
(category hub, "à proximité", homepage) in all five locales.

Local files = the owner's own photos (no credit). Wikimedia entries are
hot-linked with an honest hero credit. Idempotent.
"""

import glob
import json
import os
import re

LOCALES = ['de', 'en', 'es', 'it']
CAMERA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 '
          '2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
          '<circle cx="12" cy="13" r="4"/></svg>')

# slug -> (image src, hero-credit text or None for own photos)
PHOTOS = {
    'cascade-de-doran':            ('/cascade-de-doran-hero.jpg', None),
    'cascade-de-la-belle-au-bois': ('/cascade-de-la-belle-au-bois-hero.jpg', None),
    'cascade-des-brochaux': (
        'https://upload.wikimedia.org/wikipedia/commons/e/e0/Cascade_des_Brochaux.jpg',
        'Nouill · CC BY 4.0 · Wikimedia Commons'),
    'cascade-du-chinaillon': (
        'https://upload.wikimedia.org/wikipedia/commons/4/4f/'
        'Le_Chinaillon_%40_Pont_des_Romains_%40_Le_Grand-Bornand_%2851027594708%29.jpg',
        'Guilhem Vellut · CC BY 2.0 · Wikimedia Commons'),
    'grotte-et-cascade-de-seythenex': (
        'https://upload.wikimedia.org/wikipedia/commons/7/7f/Grotte_et_cascade_de_Seythenex_10.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
}

HERO_IMG = re.compile(r'<img\b[^>]*\bfetchpriority="high"[^>]*>')
CARD = re.compile(r'(<a href="([^"]+)" class="card-photo">)(.*?)(</a>)', re.S)
GEN_ALT = re.compile(r'g[ée]n[ée]ri|generic', re.I)


def attr(tag, name):
    m = re.search(r'\b' + name + r'="([^"]*)"', tag)
    return m.group(1) if m else None


def main():
    alts = {}
    for slug in PHOTOS:
        if os.path.exists(f'{slug}.html'):
            m = HERO_IMG.search(open(f'{slug}.html', encoding='utf-8').read())
            if m:
                alts[slug] = attr(m.group(0), 'alt') or ''

    n_hero = n_card = 0

    for slug, (src, credit) in PHOTOS.items():
        wiki = src.startswith('http')
        for loc in [''] + LOCALES:
            p = f'{slug}.html' if loc == '' else f'{loc}/{slug}.html'
            if not os.path.exists(p):
                continue
            t = orig = open(p, encoding='utf-8').read()
            m = HERO_IMG.search(t)
            if not m:
                continue
            old = m.group(0)
            a = [f'src="{src}"', f'alt="{attr(old, "alt") or alts.get(slug, "")}"',
                 f'width="{attr(old, "width") or "1600"}"',
                 f'height="{attr(old, "height") or "1200"}"', 'fetchpriority="high"']
            if wiki:
                a.append('referrerpolicy="no-referrer"')
            t = t[:m.start()] + '<img ' + ' '.join(a) + '>' + t[m.end():]
            m2 = HERO_IMG.search(t)
            after = t.find('</div>', m2.end()) + 6
            mc = re.match(r'\s*<div class="hero-credit"[^>]*>.*?</div>', t[after:], re.S)
            desired = f'<div class="hero-credit">{CAMERA} {credit}</div>' if credit else ''
            if mc:
                t = t[:after] + desired + t[after + len(mc.group(0)):]
            elif desired:
                t = t[:after] + desired + t[after:]
            if t != orig:
                open(p, 'w', encoding='utf-8').write(t)
                n_hero += 1

    def card_repl(m):
        slug = m.group(2).rstrip('/').split('/')[-1]
        if slug not in PHOTOS:
            return m.group(0)
        src = PHOTOS[slug][0]
        wiki = src.startswith('http')
        inner = m.group(3)
        im = re.search(r'<img\b[^>]*>', inner)
        if not im:
            return m.group(0)
        old = im.group(0)
        alt = attr(old, 'alt') or ''
        if not alt or GEN_ALT.search(alt):
            alt = alts.get(slug, alt)
        a = [f'src="{src}"', f'alt="{alt}"', 'loading="lazy"']
        if wiki:
            a.append('referrerpolicy="no-referrer"')
        return m.group(1) + inner[:im.start()] + '<img ' + ' '.join(a) + '>' + inner[im.end():] + m.group(4)

    for f in sorted(glob.glob('**/*.html', recursive=True)):
        if os.path.basename(f) == 'studio.html':
            continue
        t = orig = open(f, encoding='utf-8').read()
        t = CARD.sub(card_repl, t)
        if t != orig:
            open(f, 'w', encoding='utf-8').write(t)
            n_card += 1

    for slug, (src, _) in PHOTOS.items():
        jp = f'Json/{slug}.json'
        if os.path.exists(jp):
            d = json.load(open(jp, encoding='utf-8'))
            if d.get('hero_image') != src:
                d['hero_image'] = src
                open(jp, 'w', encoding='utf-8').write(
                    json.dumps(d, ensure_ascii=False, indent=2) + '\n')

    print(f'heroes set: {n_hero}  |  files with cards updated: {n_card}')


if __name__ == '__main__':
    main()
