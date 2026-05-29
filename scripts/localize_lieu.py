#!/usr/bin/env python3
"""
Localize a FR lieu page (output of build_lieu_page.py) into en/de/it/es,
reproducing the deployed convention: fully-translated chrome + French body.

Header and footer are page-independent chrome and are lifted verbatim from a
known-good locale page (TEMPLATE_SLUG), with the lang-menu slug swapped.
Everything else is deterministic string/URL rewriting.
"""
import re
import sys
from pathlib import Path

ROOT = Path("/home/user/Loisir-74")
LANGS = ["en", "de", "it", "es"]
LI = {"en": 0, "de": 1, "it": 2, "es": 3}
TEMPLATE_SLUG = "plage-de-doussard"  # has known-good locale pages to lift header/footer from

OG_LOCALE = {"en": "en_US", "de": "de_DE", "it": "it_IT", "es": "es_ES"}
INLANG = {"en": "en-US", "de": "de-DE", "it": "it-IT", "es": "es-ES"}
HOME = {"en": "Home", "de": "Startseite", "it": "Home", "es": "Inicio"}
SKIP = {"en": "Skip to content", "de": "Zum Inhalt springen", "it": "Vai al contenuto", "es": "Saltar al contenido"}
GENERIC = {"en": "Generic", "de": "Generisch", "it": "Generico", "es": "Genérico"}
PUBLISHED = {"en": "Published", "de": "Veröffentlicht", "it": "Pubblicato il", "es": "Publicado el"}
UPDATED = {"en": "Updated", "de": "Aktualisiert", "it": "Aggiornato il", "es": "Actualizado el"}
FREEWORD = {"en": "Free", "de": "Kostenlos", "it": "Gratis", "es": "Gratis"}
PAIDWORD = {"en": "Paid", "de": "Kostenpflichtig", "it": "A pagamento", "es": "De pago"}

KICKER = {
    "Activités": ["Activities", "Aktivitäten", "Attività", "Actividades"],
    "Pratique": ["Practical", "Praktisches", "Pratico", "Práctica"],
    "Accès": ["Access", "Anreise", "Accesso", "Acceso"],
    "Quand venir": ["When to visit", "Wann besuchen", "Quando visitare", "Cuándo visitar"],
    "À proximité": ["Nearby", "In der Nähe", "Nelle vicinanze", "Cerca"],
    "Photos": ["Photos", "Fotos", "Foto", "Fotos"],
    "Sources": ["Sources", "Quellen", "Fonti", "Fuentes"],
    "En un coup d&#39;œil": ["At a glance", "Auf einen Blick", "In sintesi", "De un vistazo"],
}
H2 = {
    "Ce qu&#39;on peut y faire": ["What you can do here", "Was man hier machen kann", "Cosa si può fare", "Qué se puede hacer"],
    "Infos pratiques": ["Practical information", "Praktische Informationen", "Informazioni pratiche", "Información práctica"],
    "Comment y aller": ["How to get there", "So kommen Sie hin", "Come arrivare", "Cómo llegar"],
    "Quand visiter": ["When to visit", "Wann besuchen", "Quando visitare", "Cuándo visitar"],
    "Où manger, boire, dormir": ["Where to eat, drink, stay", "Essen, Trinken, Übernachten", "Dove mangiare, bere, dormire", "Dónde comer, beber, alojarse"],
    "Galerie": ["Gallery", "Galerie", "Galleria", "Galería"],
    "Questions fréquentes": ["Frequently asked questions", "Häufige Fragen", "Domande frequenti", "Preguntas frecuentes"],
    "Sources &amp; vérifications": ["Sources &amp; verification", "Quellen &amp; Prüfung", "Fonti &amp; verifiche", "Fuentes &amp; verificaciones"],
}
WHATIS = ["What is ", "Was ist ", "Cos&#39;è ", "Qué es "]
LABELS = {
    "Type": ["Type", "Typ", "Tipo", "Tipo"],
    "Accès": ["Access", "Anreise", "Accesso", "Acceso"],
    "Tarif": ["Price", "Preis", "Prezzo", "Precio"],
    "Tarifs": ["Rates", "Preise", "Prezzi", "Precios"],
    "Durée": ["Duration", "Dauer", "Durata", "Duración"],
    "Meilleure saison": ["Best season", "Beste Saison", "Stagione migliore", "Mejor temporada"],
    "Parking": ["Parking", "Parkplatz", "Parcheggio", "Aparcamiento"],
    "Animaux": ["Animals", "Tiere", "Animali", "Animales"],
    "Poussette / PMR": ["Stroller / Reduced mobility", "Kinderwagen / Behinderte", "Passeggino / Disabilità", "Cochecito / PMR"],
    "Commune": ["Town", "Ort", "Comune", "Comuna"],
    "Adresse": ["Address", "Adresse", "Indirizzo", "Dirección"],
    "Coordonnées": ["Coordinates", "Koordinaten", "Coordinate", "Coordenadas"],
    "Saison": ["Season", "Saison", "Stagione", "Temporada"],
    "Horaires": ["Hours", "Öffnungszeiten", "Orari", "Horarios"],
    "Réservation": ["Booking", "Reservierung", "Prenotazione", "Reserva"],
    "Accessibilité": ["Accessibility", "Barrierefreiheit", "Accessibilità", "Accesibilidad"],
    "Contact": ["Contact", "Kontakt", "Contatti", "Contacto"],
    # stay FR: Lac, Lac / Plan d'eau, Surveillance, Surveillance MNS, Pavillon Bleu 2026
}

_hf_cache = {}
def header_footer(lang):
    if lang in _hf_cache:
        return _hf_cache[lang]
    src = (ROOT / lang / f"{TEMPLATE_SLUG}.html").read_text(encoding="utf-8")
    header = re.search(r"<header class=\"site\">.*?</header>", src, re.DOTALL).group(0)
    footer = re.search(r"<footer class=\"site\">.*?</footer>", src, re.DOTALL).group(0)
    _hf_cache[lang] = (header, footer)
    return header, footer


def localize(fr_html, lang, slug):
    i = LI[lang]
    t = fr_html
    # 1. global internal-URL prefix
    t = t.replace("https://loisirs74.fr/", f"https://loisirs74.fr/{lang}/")
    # mailto unaffected (no https:// prefix)
    # 2. fix hreflang block (was mangled by global prefix)
    hreflang_block = "\n".join([
        f'<link rel="alternate" hreflang="fr" href="https://loisirs74.fr/{slug}">',
        f'<link rel="alternate" hreflang="en" href="https://loisirs74.fr/en/{slug}">',
        f'<link rel="alternate" hreflang="de" href="https://loisirs74.fr/de/{slug}">',
        f'<link rel="alternate" hreflang="it" href="https://loisirs74.fr/it/{slug}">',
        f'<link rel="alternate" hreflang="es" href="https://loisirs74.fr/es/{slug}">',
        f'<link rel="alternate" hreflang="x-default" href="https://loisirs74.fr/{slug}">',
    ])
    t = re.sub(
        r'<link rel="alternate" hreflang="fr" href="[^"]*">\s*<link rel="alternate" hreflang="x-default" href="[^"]*">',
        hreflang_block, t, count=1)
    # 3. lang attr, og:locale, jsonld inLanguage
    t = t.replace('<html lang="fr"', f'<html lang="{lang}"', 1)
    t = t.replace('<meta property="og:locale" content="fr_FR">', f'<meta property="og:locale" content="{OG_LOCALE[lang]}">', 1)
    t = t.replace('"inLanguage": "fr-FR"', f'"inLanguage": "{INLANG[lang]}"')
    # 4. header + footer block-swap (page-independent chrome, slug-swapped)
    header, footer = header_footer(lang)
    header = header.replace(TEMPLATE_SLUG, slug)
    t = re.sub(r"<header class=\"site\">.*?</header>", lambda m: header, t, count=1, flags=re.DOTALL)
    t = re.sub(r"<footer class=\"site\">.*?</footer>", lambda m: footer, t, count=1, flags=re.DOTALL)
    # 5. skip link (outside header)
    t = t.replace(">Aller au contenu<", f">{SKIP[lang]}<", 1)
    # 6. breadcrumb home text + jsonld home name
    t = t.replace(">Accueil</a>", f">{HOME[lang]}</a>", 1)
    t = t.replace('"name": "Accueil"', f'"name": "{HOME[lang]}"')
    # 7. section chrome
    for fr, locs in KICKER.items():
        t = t.replace(f'<div class="kicker reveal">{fr}</div>', f'<div class="kicker reveal">{locs[i]}</div>')
    for fr, locs in H2.items():
        t = t.replace(f'<h2 class="reveal">{fr}<', f'<h2 class="reveal">{locs[i]}<')
    t = t.replace('<h2 class="reveal">Qu&#39;est-ce que ', f'<h2 class="reveal">{WHATIS[i]}')
    for fr, locs in LABELS.items():
        t = t.replace(f'<div class="k">{fr}</div>', f'<div class="k">{locs[i]}</div>')
    # 8. eyebrow free/paid word
    t = t.replace(f'· Gratuit</span>', f'· {FREEWORD[lang]}</span>')
    t = t.replace(f'· Payant</span>', f'· {PAIDWORD[lang]}</span>')
    # 9. dates + CSS label
    t = t.replace("Publié le ", f"{PUBLISHED[lang]} ")
    t = t.replace("Mis à jour le ", f"{UPDATED[lang]} ")
    t = t.replace('content: "Générique"', f'content: "{GENERIC[lang]}"')
    return t


def main():
    slugs = sys.argv[1:]
    for slug in slugs:
        fr = (ROOT / f"{slug}.html").read_text(encoding="utf-8")
        for lang in LANGS:
            out = localize(fr, lang, slug)
            (ROOT / lang).mkdir(exist_ok=True)
            (ROOT / lang / f"{slug}.html").write_text(out, encoding="utf-8")
        print(f"  ✓ {slug}: en/de/it/es")


if __name__ == "__main__":
    main()
