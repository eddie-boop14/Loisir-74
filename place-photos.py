#!/usr/bin/env python3
"""
place-photos.py — Loisirs 74
============================
Assign real hero photos to place pages that were on a générique
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
    'plage-des-marquisats': (
        'https://upload.wikimedia.org/wikipedia/commons/b/b2/Annecy-8.jpg',
        'Dingy · CC BY-SA 3.0 · Wikimedia Commons'),
    'plage-de-sciez-sur-leman': (
        'https://upload.wikimedia.org/wikipedia/commons/a/a1/Sciez-regate.jpg',
        'SciezChablais · CC BY-SA 4.0 · Wikimedia Commons'),
    'plage-de-saint-disdille': (
        'https://upload.wikimedia.org/wikipedia/commons/6/67/Plage_thonon.jpg',
        'Dmnt44 · CC BY-SA 4.0 · Wikimedia Commons'),
    'plage-d-excenevex': (
        'https://upload.wikimedia.org/wikipedia/commons/c/cd/'
        'Rive_du_L%C3%A9man_%C3%A0_Excenevex_%28juin_2019%29.JPG',
        'Florian Pépellin · CC BY-SA 4.0 · Wikimedia Commons'),
    'plage-de-la-pinede': (
        'https://upload.wikimedia.org/wikipedia/commons/e/e2/'
        'Thonon-les-Bains._Promenade_du_L%C3%A9man._2015-06-21.jpg',
        'Espirat · CC BY-SA 4.0 · Wikimedia Commons'),
    'les-aigles-du-leman': (
        'https://upload.wikimedia.org/wikipedia/commons/8/80/'
        'Female_falcon_handler_with_eagle_%2825513995343%29.jpg',
        'Thomas Quine · CC BY 2.0 · Wikimedia Commons'),
    'acro-aventures-reignier': (
        'https://upload.wikimedia.org/wikipedia/commons/b/b8/Accrobranche_floreval_2.jpg',
        'LP1968 · CC BY-SA 4.0 · Wikimedia Commons'),
    'parcours-aventure-de-sciez': (
        'https://upload.wikimedia.org/wikipedia/commons/b/b8/Accrobranche_floreval_2.jpg',
        'LP1968 · CC BY-SA 4.0 · Wikimedia Commons'),
    'passy-accro-lac': (
        'https://upload.wikimedia.org/wikipedia/commons/b/b8/Accrobranche_floreval_2.jpg',
        'LP1968 · CC BY-SA 4.0 · Wikimedia Commons'),
    'tramway-du-mont-blanc': (
        'https://upload.wikimedia.org/wikipedia/commons/e/e3/Tramway_Mont-Blanc.jpg',
        'Frédéric Bonifas · GFDL · Wikimedia Commons'),
    'telepherique-du-brevent': (
        'https://upload.wikimedia.org/wikipedia/commons/2/2a/Brevent_cable_car.jpg',
        'Victoria Lunyak · CC BY-SA 4.0 · Wikimedia Commons'),
    'telecabine-des-chavannes-les-gets': (
        'https://upload.wikimedia.org/wikipedia/commons/8/82/'
        'T%C3%A9l%C3%A9cabine_Panoramic_Mont-Blanc_Pointe_Helbronner.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
    'telecabine-du-jaillet': (
        'https://upload.wikimedia.org/wikipedia/commons/8/82/'
        'T%C3%A9l%C3%A9cabine_Panoramic_Mont-Blanc_Pointe_Helbronner.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
    'telecabine-du-mont-chery-les-gets': (
        'https://upload.wikimedia.org/wikipedia/commons/8/82/'
        'T%C3%A9l%C3%A9cabine_Panoramic_Mont-Blanc_Pointe_Helbronner.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
    'telecabine-pleney-morzine': (
        'https://upload.wikimedia.org/wikipedia/commons/8/82/'
        'T%C3%A9l%C3%A9cabine_Panoramic_Mont-Blanc_Pointe_Helbronner.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
    'telecabine-super-chatel': (
        'https://upload.wikimedia.org/wikipedia/commons/8/82/'
        'T%C3%A9l%C3%A9cabine_Panoramic_Mont-Blanc_Pointe_Helbronner.jpg',
        'Rémih · CC BY-SA 4.0 · Wikimedia Commons'),
    'domaine-de-rovoree-la-chataigniere': (
        'https://upload.wikimedia.org/wikipedia/commons/f/f8/'
        'Embarcad%C3%A8re_du_Domaine_de_La_Ch%C3%A2taigni%C3%A8re.jpg',
        'Chrbenoit · CC BY-SA 4.0 · Wikimedia Commons'),
    'belvedere-du-mont-baron': (
        'https://upload.wikimedia.org/wikipedia/commons/d/d1/Chemin_mont_Veyrier_mont_Baron.jpg',
        'Myrabella · CC BY-SA 3.0 · Wikimedia Commons'),
    'mont-joly': (
        'https://upload.wikimedia.org/wikipedia/commons/5/54/'
        'Meg%C3%A8ve%2C_depuis_la_cha%C3%AEne_du_Mont-Joly.jpg',
        'CBougault · CC BY-SA 4.0 · Wikimedia Commons'),
    'col-des-pitons-saleve': (
        'https://upload.wikimedia.org/wikipedia/commons/6/68/'
        'La_Tour_des_Pitons%2C_point_culminant_du_Sal%C3%A8ve_%281379m%29.JPG',
        'Martial GAILLARD-GRENADIER · CC BY-SA 3.0 · Wikimedia Commons'),
    'base-de-loisirs-du-lac-des-iles': (
        'https://upload.wikimedia.org/wikipedia/commons/b/bd/'
        'Les_ARAVIS_depuis_le_LAC_DE_PASSY_-_panoramio.jpg',
        'CEDRIC BRUN · CC BY 3.0 · Wikimedia Commons'),
    'cote-2000-aventure': (
        'https://upload.wikimedia.org/wikipedia/commons/d/de/Seilpark_Gantrisch_-_03.jpg',
        'David Haberthür · CC BY 2.0 · Wikimedia Commons'),
    'indiana-ventures-saint-paul-en-chablais': (
        'https://upload.wikimedia.org/wikipedia/commons/2/21/La_plage_de_La_Beunaz.jpg',
        'Saint-Paul-en-Chablais · CC BY-SA 4.0 · Wikimedia Commons'),
    'parc-des-dereches': (
        'https://upload.wikimedia.org/wikipedia/commons/7/70/'
        'Horse_riding_in_the_valley_of_the_Edigan_River.jpg',
        'Obakeneko · CC BY 3.0 · Wikimedia Commons'),
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
