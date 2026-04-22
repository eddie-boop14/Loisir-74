#!/usr/bin/env python3
"""
Build en/index.html, de/index.html, it/index.html from the FR index.
Translates: <title>, <meta description>, hero copy, nav labels, filter labels,
FAQ-ish sections, CTAs, footer copy. Preserves: structure, data attributes,
JS logic, schema.org (with language-adjusted WebSite/Organization blocks),
all 50 lieu cards (names and communes stay in French as they are proper nouns).

Run from anywhere.
"""
from pathlib import Path
import re
import sys

SRC = Path('index.html')
OUT_DIR = Path('.')

# Language-specific translations. Keys = French source strings. Values = dict of translations.
# Ordered by rough appearance in the file. Uses unambiguous strings to avoid collisions.
TRANSLATIONS = {
    'Panorama du lac d\'Annecy depuis le sommet du Taillefer, au printemps': {
        'en': 'Panoramic view of Lake Annecy from the summit of Le Taillefer, in spring',
        'de': 'Panoramablick auf den Lac d\'Annecy vom Gipfel des Taillefer im Frühling',
        'it': 'Vista panoramica del lago d\'Annecy dalla cima del Taillefer, in primavera',
    },
    # <title>
    'Loisirs 74 — Guide des lieux publics de Haute-Savoie': {
        'en': 'Loisirs 74 — Guide to public leisure sites in Haute-Savoie',
        'de': 'Loisirs 74 — Führer öffentlicher Freizeitorte Haute-Savoie',
        'it': 'Loisirs 74 — Guida ai luoghi di svago pubblici dell\'Alta Savoia',
    },
    # <meta description>
    'Cinquante lieux de loisirs publics et gratuits en Haute-Savoie : lacs, cascades, voies vertes, parcs, points de vue. Sources officielles, infos vérifiées.': {
        'en': 'Fifty public, free leisure sites in Haute-Savoie: lakes, waterfalls, greenways, parks, viewpoints. Official sources, verified info.',
        'de': 'Fünfzig öffentliche, kostenlose Freizeitorte in der Haute-Savoie: Seen, Wasserfälle, Grünwege, Parks, Aussichtspunkte. Offizielle Quellen, geprüfte Angaben.',
        'it': 'Cinquanta luoghi di svago pubblici e gratuiti in Alta Savoia: laghi, cascate, vie verdi, parchi, belvederi. Fonti ufficiali, informazioni verificate.',
    },
    'Cinquante lieux de loisirs publics et gratuits en Haute-Savoie, documentés à partir de sources officielles.': {
        'en': 'Fifty public, free leisure sites in Haute-Savoie, documented from official sources.',
        'de': 'Fünfzig öffentliche, kostenlose Freizeitorte in der Haute-Savoie, dokumentiert anhand offizieller Quellen.',
        'it': 'Cinquanta luoghi di svago pubblici e gratuiti in Alta Savoia, documentati a partire da fonti ufficiali.',
    },
    # Homepage schema.org name
    '"name": "Lieux de loisirs publics en Haute-Savoie"': {
        'en': '"name": "Public leisure sites in Haute-Savoie"',
        'de': '"name": "Öffentliche Freizeitorte in der Haute-Savoie"',
        'it': '"name": "Luoghi di svago pubblici in Alta Savoia"',
    },
    '"name": "Lieux de Haute-Savoie"': {
        'en': '"name": "Sites in Haute-Savoie"',
        'de': '"name": "Orte in der Haute-Savoie"',
        'it': '"name": "Luoghi in Alta Savoia"',
    },
    'Guide indépendant des lieux de loisirs publics en Haute-Savoie': {
        'en': 'Independent guide to public leisure sites in Haute-Savoie',
        'de': 'Unabhängiger Führer zu öffentlichen Freizeitorten in der Haute-Savoie',
        'it': 'Guida indipendente ai luoghi di svago pubblici in Alta Savoia',
    },
    # Brand aria-label + skip link
    'Aller au contenu': {'en': 'Skip to content', 'de': 'Zum Inhalt springen', 'it': 'Vai al contenuto'},
    'Loisirs 74 · Accueil': {
        'en': 'Loisirs 74 · Home',
        'de': 'Loisirs 74 · Startseite',
        'it': 'Loisirs 74 · Home',
    },
    # Desktop nav
    '>Lacs<': {'en': '>Lakes<', 'de': '>Seen<', 'it': '>Laghi<'},
    '>Cascades<': {'en': '>Waterfalls<', 'de': '>Wasserfälle<', 'it': '>Cascate<'},
    '>Voies vertes<': {'en': '>Greenways<', 'de': '>Grünwege<', 'it': '>Vie verdi<'},
    '>Parcs<': {'en': '>Parks<', 'de': '>Parks<', 'it': '>Parchi<'},
    '>À propos<': {'en': '>About<', 'de': '>Über uns<', 'it': '>Informazioni<'},
    # Nav aria + theme + menu
    'Navigation principale': {'en': 'Main navigation', 'de': 'Hauptnavigation', 'it': 'Navigazione principale'},
    'Changer de langue': {'en': 'Change language', 'de': 'Sprache ändern', 'it': 'Cambia lingua'},
    'Changer de thème (clair/sombre)': {'en': 'Toggle theme (light/dark)', 'de': 'Thema wechseln (hell/dunkel)', 'it': 'Cambia tema (chiaro/scuro)'},
    'Changer de thème': {'en': 'Toggle theme', 'de': 'Thema wechseln', 'it': 'Cambia tema'},
    'Ouvrir le menu': {'en': 'Open menu', 'de': 'Menü öffnen', 'it': 'Apri menu'},
    # Mobile menu
    'Menu mobile': {'en': 'Mobile menu', 'de': 'Mobilmenü', 'it': 'Menu mobile'},
    'Lacs &amp; plans d\'eau': {
        'en': 'Lakes &amp; ponds', 'de': 'Seen &amp; Gewässer', 'it': 'Laghi &amp; specchi d\'acqua',
    },
    'Cascades &amp; gorges': {
        'en': 'Waterfalls &amp; gorges', 'de': 'Wasserfälle &amp; Schluchten', 'it': 'Cascate &amp; gole',
    },
    'Parcs &amp; jardins': {'en': 'Parks &amp; gardens', 'de': 'Parks &amp; Gärten', 'it': 'Parchi &amp; giardini'},
    'Sentiers': {'en': 'Trails', 'de': 'Wanderwege', 'it': 'Sentieri'},
    'Points de vue': {'en': 'Viewpoints', 'de': 'Aussichtspunkte', 'it': 'Belvederi'},
    'À propos du site': {'en': 'About the site', 'de': 'Über die Seite', 'it': 'Informazioni sul sito'},
    # Hero
    'Haute-Savoie &middot; guide indépendant': {
        'en': 'Haute-Savoie &middot; independent guide',
        'de': 'Haute-Savoie &middot; unabhängiger Führer',
        'it': 'Alta Savoia &middot; guida indipendente',
    },
    # Hero H1 — keep "Haute-Savoie" as emphasized italic in all langs
    'Cinquante lieux publics de <em>Haute-Savoie</em>, documentés.': {
        'en': 'Fifty public sites in <em>Haute-Savoie</em>, documented.',
        'de': 'Fünfzig öffentliche Orte in der <em>Haute-Savoie</em>, dokumentiert.',
        'it': 'Cinquanta luoghi pubblici dell\'<em>Alta Savoia</em>, documentati.',
    },
    # Hero lead
    'Lacs, cascades, voies vertes, parcs, points de vue. Accès libre ou presque. Chaque fiche est montée à partir de sources officielles — communes, offices de tourisme, ONF, Natura 2000. Rien d\'inventé.': {
        'en': 'Lakes, waterfalls, greenways, parks, viewpoints. Free access or close to it. Every entry is built from official sources — municipalities, tourist offices, ONF, Natura 2000. Nothing invented.',
        'de': 'Seen, Wasserfälle, Grünwege, Parks, Aussichtspunkte. Freier Zugang oder nahezu. Jeder Eintrag stützt sich auf offizielle Quellen — Gemeinden, Tourismusbüros, ONF, Natura 2000. Nichts erfunden.',
        'it': 'Laghi, cascate, vie verdi, parchi, belvederi. Accesso libero o quasi. Ogni scheda è costruita a partire da fonti ufficiali — comuni, uffici del turismo, ONF, Natura 2000. Nulla di inventato.',
    },
    # Category pill title + pills
    'Par catégorie': {'en': 'By category', 'de': 'Nach Kategorie', 'it': 'Per categoria'},
    'Catégories de lieux': {'en': 'Site categories', 'de': 'Kategorien der Orte', 'it': 'Categorie di luoghi'},
    '>Parcs &amp; jardins</span>': {
        'en': '>Parks &amp; gardens</span>', 'de': '>Parks &amp; Gärten</span>', 'it': '>Parchi &amp; giardini</span>'
    },
    '>Zones humides</span>': {'en': '>Wetlands</span>', 'de': '>Feuchtgebiete</span>', 'it': '>Zone umide</span>'},
    '>Grottes</span>': {'en': '>Caves</span>', 'de': '>Höhlen</span>', 'it': '>Grotte</span>'},
    # Filter
    'Filtrer les lieux': {'en': 'Filter sites', 'de': 'Orte filtern', 'it': 'Filtra luoghi'},
    'Chercher un lieu, une commune…': {
        'en': 'Search a site, a town…',
        'de': 'Ort oder Gemeinde suchen…',
        'it': 'Cerca un luogo, un comune…',
    },
    'Chercher un lieu ou une commune': {
        'en': 'Search a site or a town',
        'de': 'Ort oder Gemeinde suchen',
        'it': 'Cerca un luogo o un comune',
    },
    'Filtrer par catégorie': {'en': 'Filter by category', 'de': 'Nach Kategorie filtern', 'it': 'Filtra per categoria'},
    'Toutes catégories': {'en': 'All categories', 'de': 'Alle Kategorien', 'it': 'Tutte le categorie'},
    'Lacs &amp; plans d\'eau</option>': {
        'en': 'Lakes &amp; ponds</option>', 'de': 'Seen &amp; Gewässer</option>', 'it': 'Laghi &amp; specchi d\'acqua</option>',
    },
    'Cascades</option>': {'en': 'Waterfalls</option>', 'de': 'Wasserfälle</option>', 'it': 'Cascate</option>'},
    'Sentiers</option>': {'en': 'Trails</option>', 'de': 'Wanderwege</option>', 'it': 'Sentieri</option>'},
    'Parcs &amp; jardins</option>': {
        'en': 'Parks &amp; gardens</option>', 'de': 'Parks &amp; Gärten</option>', 'it': 'Parchi &amp; giardini</option>',
    },
    'Points de vue</option>': {'en': 'Viewpoints</option>', 'de': 'Aussichtspunkte</option>', 'it': 'Belvederi</option>'},
    'Voies vertes</option>': {'en': 'Greenways</option>', 'de': 'Grünwege</option>', 'it': 'Vie verdi</option>'},
    'Zones humides</option>': {'en': 'Wetlands</option>', 'de': 'Feuchtgebiete</option>', 'it': 'Zone umide</option>'},
    'Grottes</option>': {'en': 'Caves</option>', 'de': 'Höhlen</option>', 'it': 'Grotte</option>'},
    'Filtrer par état de publication': {
        'en': 'Filter by publication status',
        'de': 'Nach Veröffentlichungsstatus filtern',
        'it': 'Filtra per stato di pubblicazione',
    },
    'Toutes fiches': {'en': 'All entries', 'de': 'Alle Einträge', 'it': 'Tutte le schede'},
    'Fiches publiées': {'en': 'Published entries', 'de': 'Veröffentlichte Einträge', 'it': 'Schede pubblicate'},
    'En préparation</option>': {'en': 'In preparation</option>', 'de': 'In Vorbereitung</option>', 'it': 'In preparazione</option>'},
    '>Effacer<': {'en': '>Clear<', 'de': '>Löschen<', 'it': '>Azzera<'},
    # filter meta counts
    'lieux affichés</span>': {
        'en': 'sites shown</span>',
        'de': 'Orte angezeigt</span>',
        'it': 'luoghi visualizzati</span>',
    },
    '</strong> fiche publiée': {
        'en': '</strong> published',
        'de': '</strong> veröffentlicht',
        'it': '</strong> pubblicata',
    },
    '</strong> en préparation</span>': {
        'en': '</strong> in preparation</span>',
        'de': '</strong> in Vorbereitung</span>',
        'it': '</strong> in preparazione</span>',
    },
    'Lieux de Haute-Savoie': {
        'en': 'Sites in Haute-Savoie',
        'de': 'Orte in der Haute-Savoie',
        'it': 'Luoghi in Alta Savoia',
    },
    # Card labels — statuses
    '● Fiche publiée': {'en': '● Published', 'de': '● Veröffentlicht', 'it': '● Pubblicata'},
    '● En préparation': {'en': '● In preparation', 'de': '● In Vorbereitung', 'it': '● In preparazione'},
    # Card category labels (appear as plain text in .lieu-cat)
    '<span class="lieu-cat-dot"></span>Lac</div>': {
        'en': '<span class="lieu-cat-dot"></span>Lake</div>',
        'de': '<span class="lieu-cat-dot"></span>See</div>',
        'it': '<span class="lieu-cat-dot"></span>Lago</div>',
    },
    '<span class="lieu-cat-dot"></span>Cascade</div>': {
        'en': '<span class="lieu-cat-dot"></span>Waterfall</div>',
        'de': '<span class="lieu-cat-dot"></span>Wasserfall</div>',
        'it': '<span class="lieu-cat-dot"></span>Cascata</div>',
    },
    '<span class="lieu-cat-dot"></span>Voie verte</div>': {
        'en': '<span class="lieu-cat-dot"></span>Greenway</div>',
        'de': '<span class="lieu-cat-dot"></span>Grünweg</div>',
        'it': '<span class="lieu-cat-dot"></span>Via verde</div>',
    },
    '<span class="lieu-cat-dot"></span>Parc</div>': {
        'en': '<span class="lieu-cat-dot"></span>Park</div>',
        'de': '<span class="lieu-cat-dot"></span>Park</div>',
        'it': '<span class="lieu-cat-dot"></span>Parco</div>',
    },
    '<span class="lieu-cat-dot"></span>Point de vue</div>': {
        'en': '<span class="lieu-cat-dot"></span>Viewpoint</div>',
        'de': '<span class="lieu-cat-dot"></span>Aussichtspunkt</div>',
        'it': '<span class="lieu-cat-dot"></span>Belvedere</div>',
    },
    '<span class="lieu-cat-dot"></span>Sentier</div>': {
        'en': '<span class="lieu-cat-dot"></span>Trail</div>',
        'de': '<span class="lieu-cat-dot"></span>Wanderweg</div>',
        'it': '<span class="lieu-cat-dot"></span>Sentiero</div>',
    },
    '<span class="lieu-cat-dot"></span>Zone humide</div>': {
        'en': '<span class="lieu-cat-dot"></span>Wetland</div>',
        'de': '<span class="lieu-cat-dot"></span>Feuchtgebiet</div>',
        'it': '<span class="lieu-cat-dot"></span>Zona umida</div>',
    },
    '<span class="lieu-cat-dot"></span>Grotte</div>': {
        'en': '<span class="lieu-cat-dot"></span>Cave</div>',
        'de': '<span class="lieu-cat-dot"></span>Höhle</div>',
        'it': '<span class="lieu-cat-dot"></span>Grotta</div>',
    },
    # No results
    'Aucun lieu ne correspond': {
        'en': 'No site matches',
        'de': 'Kein Ort passt',
        'it': 'Nessun luogo corrisponde',
    },
    'Essayez un autre terme ou effacez les filtres.': {
        'en': 'Try another term or clear the filters.',
        'de': 'Versuchen Sie einen anderen Begriff oder löschen Sie die Filter.',
        'it': 'Prova un altro termine o azzera i filtri.',
    },
    # Editorial
    'Notre <em>méthode</em>, en dix lignes.': {
        'en': 'Our <em>method</em>, in ten lines.',
        'de': 'Unsere <em>Methode</em>, in zehn Zeilen.',
        'it': 'Il nostro <em>metodo</em>, in dieci righe.',
    },
    'Loisirs 74 existe parce qu\'il manquait un endroit où trouver l\'info juste sur les lieux de loisirs publics de Haute-Savoie. Les PDF des mairies ne sortent jamais sur Google. Les fiches des offices de tourisme se ressemblent. Les blogs généralistes recopient ce qu\'ils trouvent, souvent mal, souvent vieux.': {
        'en': 'Loisirs 74 exists because there was no single place to find accurate info on public leisure sites in Haute-Savoie. Town-hall PDFs never surface on Google. Tourist-office pages all look alike. Generalist blogs copy what they find — often badly, often stale.',
        'de': 'Loisirs 74 gibt es, weil verlässliche Informationen zu öffentlichen Freizeitorten in der Haute-Savoie bislang verstreut waren. Gemeinde-PDFs erscheinen bei Google nicht. Tourismusbüro-Seiten ähneln einander. Allgemein-Blogs kopieren, was sie finden — oft schlecht, oft veraltet.',
        'it': 'Loisirs 74 esiste perché mancava un luogo dove trovare informazioni precise sui siti di svago pubblici dell\'Alta Savoia. I PDF dei comuni non compaiono mai su Google. Le schede degli uffici del turismo si assomigliano tutte. I blog generalisti ricopiano quello che trovano, spesso male, spesso datato.',
    },
    'Au moins trois sources officielles par lieu — commune, OT, ONF, Natura 2000, data.gouv.': {
        'en': 'At least three official sources per site — municipality, tourist office, ONF, Natura 2000, data.gouv.',
        'de': 'Mindestens drei offizielle Quellen pro Ort — Gemeinde, Tourismusbüro, ONF, Natura 2000, data.gouv.',
        'it': 'Almeno tre fonti ufficiali per luogo — comune, ufficio del turismo, ONF, Natura 2000, data.gouv.',
    },
    'Les blogs, Visorando, Komoot, TripAdvisor ne sont pas des sources.': {
        'en': 'Blogs, Visorando, Komoot, TripAdvisor are not sources.',
        'de': 'Blogs, Visorando, Komoot, TripAdvisor sind keine Quellen.',
        'it': 'I blog, Visorando, Komoot, TripAdvisor non sono fonti.',
    },
    'Si un fait n\'est confirmé nulle part, il n\'apparaît pas. Jamais de « généralement ».': {
        'en': 'If a fact isn\'t confirmed anywhere, it doesn\'t appear. Never a "generally".',
        'de': 'Ist eine Angabe nirgends bestätigt, erscheint sie nicht. Nie ein „in der Regel".',
        'it': 'Se un dato non è confermato da nessuna parte, non compare. Mai un "generalmente".',
    },
    'GPS vérifiés sur OpenStreetMap. Dates de publication et de mise à jour visibles.': {
        'en': 'GPS checked on OpenStreetMap. Publication and update dates visible on every page.',
        'de': 'GPS auf OpenStreetMap geprüft. Veröffentlichungs- und Aktualisierungsdaten auf jeder Seite sichtbar.',
        'it': 'GPS verificati su OpenStreetMap. Date di pubblicazione e aggiornamento visibili su ogni pagina.',
    },
    'Qui <em>édite</em> ce site ?': {
        'en': 'Who <em>publishes</em> this site?',
        'de': 'Wer <em>betreibt</em> diese Seite?',
        'it': 'Chi <em>pubblica</em> questo sito?',
    },
    'Loisirs 74 est un projet indépendant de <strong>bleu-canard édition</strong>, sans lien avec les communes, les offices de tourisme ou les gestionnaires mentionnés.': {
        'en': 'Loisirs 74 is an independent project by <strong>bleu-canard édition</strong>, with no affiliation to the municipalities, tourist offices or site managers mentioned.',
        'de': 'Loisirs 74 ist ein unabhängiges Projekt von <strong>bleu-canard édition</strong>, ohne Verbindung zu den genannten Gemeinden, Tourismusbüros oder Betreibern.',
        'it': 'Loisirs 74 è un progetto indipendente di <strong>bleu-canard édition</strong>, senza alcun legame con i comuni, gli uffici del turismo o i gestori menzionati.',
    },
    'Une info obsolète, une erreur ? <a href="/en/contact">Écrivez-nous</a>.': {
        'en': 'Outdated info, a mistake? <a href="/en/contact">Get in touch</a>.',
        'de': 'Veraltete Information, ein Fehler? <a href="/en/contact">Schreiben Sie uns</a>.',
        'it': 'Un\'informazione obsoleta, un errore? <a href="/en/contact">Scriveteci</a>.',
    },
    'Une info obsolète, une erreur ? <a href="/de/contact">Écrivez-nous</a>.': {
        'en': 'Outdated info, a mistake? <a href="/de/contact">Get in touch</a>.',
        'de': 'Veraltete Information, ein Fehler? <a href="/de/contact">Schreiben Sie uns</a>.',
        'it': 'Un\'informazione obsoleta, un errore? <a href="/de/contact">Scriveteci</a>.',
    },
    'Une info obsolète, une erreur ? <a href="/it/contact">Écrivez-nous</a>.': {
        'en': 'Outdated info, a mistake? <a href="/it/contact">Get in touch</a>.',
        'de': 'Veraltete Information, ein Fehler? <a href="/it/contact">Schreiben Sie uns</a>.',
        'it': 'Un\'informazione obsoleta, un errore? <a href="/it/contact">Scriveteci</a>.',
    },
    'Une info obsolète, une erreur ? <a href="/contact">Écrivez-nous</a>.': {
        'en': 'Outdated info, a mistake? <a href="/en/contact">Get in touch</a>.',
        'de': 'Veraltete Information, ein Fehler? <a href="/de/contact">Schreiben Sie uns</a>.',
        'it': 'Un\'informazione obsoleta, un errore? <a href="/it/contact">Scriveteci</a>.',
    },
    # Partner CTA
    'Vous accueillez les visiteurs d\'un de ces <em>lieux</em> ?': {
        'en': 'Do you welcome visitors to one of these <em>sites</em>?',
        'de': 'Empfangen Sie Besucher an einem dieser <em>Orte</em>?',
        'it': 'Accogliete i visitatori di uno di questi <em>luoghi</em>?',
    },
    'Restaurant, gîte, boulangerie, location de vélos, office de tourisme local. Apparaissez sur la page du lieu que vous servez.': {
        'en': 'Restaurant, guesthouse, bakery, bike rental, local tourist office. Appear on the page of the site you serve.',
        'de': 'Restaurant, Gîte, Bäckerei, Fahrradverleih, lokales Tourismusbüro. Erscheinen Sie auf der Seite des Ortes, den Sie bedienen.',
        'it': 'Ristorante, gîte, panetteria, noleggio biciclette, ufficio del turismo locale. Apparite sulla pagina del luogo che servite.',
    },
    '>Restaurant<': {'en': '>Restaurant<', 'de': '>Restaurant<', 'it': '>Ristorante<'},
    '>Hébergement<': {'en': '>Accommodation<', 'de': '>Unterkunft<', 'it': '>Alloggio<'},
    '>Commerce<': {'en': '>Shop<', 'de': '>Geschäft<', 'it': '>Negozio<'},
    '>Location<': {'en': '>Rental<', 'de': '>Verleih<', 'it': '>Noleggio<'},
    'Devenir partenaire\n        <svg': {
        'en': 'Become a partner\n        <svg',
        'de': 'Partner werden\n        <svg',
        'it': 'Diventa partner\n        <svg',
    },
    # Back to top
    'Retour en haut de page': {'en': 'Back to top', 'de': 'Nach oben', 'it': 'Torna su'},
    'Haut de page': {'en': 'Top', 'de': 'Seitenanfang', 'it': 'Inizio pagina'},
    # Footer
    'Le guide indépendant des lieux de loisirs publics en Haute-Savoie. Sources officielles, croisées, datées.': {
        'en': 'The independent guide to public leisure sites in Haute-Savoie. Official sources, cross-checked, dated.',
        'de': 'Der unabhängige Führer zu öffentlichen Freizeitorten in der Haute-Savoie. Offizielle Quellen, abgeglichen, datiert.',
        'it': 'La guida indipendente ai luoghi di svago pubblici dell\'Alta Savoia. Fonti ufficiali, incrociate, datate.',
    },
    'Loisirs 74 est un site indépendant, non-officiel, sans lien avec les communes ou offices de tourisme mentionnés. Les informations proviennent de sources officielles et sont vérifiées à la date de publication, mais peuvent évoluer sans préavis.': {
        'en': 'Loisirs 74 is an independent, unofficial site with no affiliation to the municipalities or tourist offices mentioned. Information comes from official sources, verified at publication date, and may change without notice.',
        'de': 'Loisirs 74 ist eine unabhängige, nicht-offizielle Seite ohne Verbindung zu den genannten Gemeinden oder Tourismusbüros. Die Angaben stammen aus offiziellen Quellen, wurden zum Veröffentlichungsdatum geprüft und können sich ohne Vorankündigung ändern.',
        'it': 'Loisirs 74 è un sito indipendente, non ufficiale, senza legami con i comuni o gli uffici del turismo menzionati. Le informazioni provengono da fonti ufficiali, sono verificate alla data di pubblicazione e possono evolvere senza preavviso.',
    },
    'Explorer': {'en': 'Explore', 'de': 'Entdecken', 'it': 'Esplora'},
    'Le site': {'en': 'The site', 'de': 'Die Seite', 'it': 'Il sito'},
    'À propos': {'en': 'About', 'de': 'Über uns', 'it': 'Informazioni'},
    'Contact</a>': {'en': 'Contact</a>', 'de': 'Kontakt</a>', 'it': 'Contatti</a>'},
    'Devenir partenaire</a>': {
        'en': 'Become a partner</a>',
        'de': 'Partner werden</a>',
        'it': 'Diventa partner</a>',
    },
    'Mentions légales': {'en': 'Legal notice', 'de': 'Impressum', 'it': 'Note legali'},
    'Confidentialité': {'en': 'Privacy', 'de': 'Datenschutz', 'it': 'Privacy'},
    '© 2026 Loisirs 74 · Guide des lieux de détente en Haute-Savoie': {
        'en': '© 2026 Loisirs 74 · Guide to leisure sites in Haute-Savoie',
        'de': '© 2026 Loisirs 74 · Führer zu Freizeitorten in der Haute-Savoie',
        'it': '© 2026 Loisirs 74 · Guida ai luoghi di svago dell\'Alta Savoia',
    },
    '© 2026 bleu-canard édition, Edmaster &amp; Claudius, tout droit réservé': {
        'en': '© 2026 bleu-canard édition, Edmaster &amp; Claudius, all rights reserved',
        'de': '© 2026 bleu-canard édition, Edmaster &amp; Claudius, alle Rechte vorbehalten',
        'it': '© 2026 bleu-canard édition, Edmaster &amp; Claudius, tutti i diritti riservati',
    },
    # Accessibility labels
    'Adresses partenaires et recommandées': {
        'en': 'Partner and recommended addresses',
        'de': 'Partner- und empfohlene Adressen',
        'it': 'Indirizzi partner e consigliati',
    },
    'En un coup d\'œil': {
        'en': 'At a glance', 'de': 'Auf einen Blick', 'it': 'In sintesi',
    },
    # Site content around editorial
    'Engagement éditorial': {
        'en': 'Editorial commitment', 'de': 'Redaktionelles Versprechen', 'it': 'Impegno editoriale',
    },
}

# Paths in attributes/HTML that need language prefix for en/de/it
# (FR has no prefix, the 3 other langs live under /en/, /de/, /it/)
# The search only needs rewriting for intra-site links, NOT external URLs.
PATH_REWRITES = {
    'en': [
        ('href="/"', 'href="/en/"'),
        ('href="/contact"', 'href="/en/contact"'),
        ('href="/devenir-partenaire"', 'href="/en/devenir-partenaire"'),
        ('href="/domaine-du-tornet"', 'href="/en/domaine-du-tornet"'),
        ('href="/mentions-legales-loisirs74-phase1.html"', 'href="/en/mentions-legales-loisirs74-phase1.html"'),
        ('href="/politique-confidentialite-loisirs74-phase1.html"', 'href="/en/politique-confidentialite-loisirs74-phase1.html"'),
        # canonical
        ('<link rel="canonical" href="https://loisirs74.fr/">',
         '<link rel="canonical" href="https://loisirs74.fr/en/">'),
        # schema.org WebSite inLanguage
        ('"inLanguage": "fr-FR"', '"inLanguage": "en-GB"'),
        # OG locale
        ('<meta property="og:locale" content="fr_FR">', '<meta property="og:locale" content="en_GB">'),
        # url on Organization / WebSite objects — keep fr canonical for publisher ID (shared graph)
    ],
    'de': [
        ('href="/"', 'href="/de/"'),
        ('href="/contact"', 'href="/de/contact"'),
        ('href="/devenir-partenaire"', 'href="/de/devenir-partenaire"'),
        ('href="/domaine-du-tornet"', 'href="/de/domaine-du-tornet"'),
        ('href="/mentions-legales-loisirs74-phase1.html"', 'href="/de/mentions-legales-loisirs74-phase1.html"'),
        ('href="/politique-confidentialite-loisirs74-phase1.html"', 'href="/de/politique-confidentialite-loisirs74-phase1.html"'),
        ('<link rel="canonical" href="https://loisirs74.fr/">',
         '<link rel="canonical" href="https://loisirs74.fr/de/">'),
        ('"inLanguage": "fr-FR"', '"inLanguage": "de-DE"'),
        ('<meta property="og:locale" content="fr_FR">', '<meta property="og:locale" content="de_DE">'),
    ],
    'it': [
        ('href="/"', 'href="/it/"'),
        ('href="/contact"', 'href="/it/contact"'),
        ('href="/devenir-partenaire"', 'href="/it/devenir-partenaire"'),
        ('href="/domaine-du-tornet"', 'href="/it/domaine-du-tornet"'),
        ('href="/mentions-legales-loisirs74-phase1.html"', 'href="/it/mentions-legales-loisirs74-phase1.html"'),
        ('href="/politique-confidentialite-loisirs74-phase1.html"', 'href="/it/politique-confidentialite-loisirs74-phase1.html"'),
        ('<link rel="canonical" href="https://loisirs74.fr/">',
         '<link rel="canonical" href="https://loisirs74.fr/it/">'),
        ('"inLanguage": "fr-FR"', '"inLanguage": "it-IT"'),
        ('<meta property="og:locale" content="fr_FR">', '<meta property="og:locale" content="it_IT">'),
    ],
}

# Lang attribute on <html>, aria-current on language switcher, and sitemap/schema URLs
LANG_ATTR = {
    'en': ('<html lang="fr"', '<html lang="en"'),
    'de': ('<html lang="fr"', '<html lang="de"'),
    'it': ('<html lang="fr"', '<html lang="it"'),
}


def build_for_lang(lang, src_html):
    out = src_html

    # 1) html lang
    out = out.replace(LANG_ATTR[lang][0], LANG_ATTR[lang][1])

    # 2) path rewrites — do these FIRST before translations that might disturb hrefs
    #    But: language switcher has hreflang=fr|en|de|it entries that should NOT be touched.
    #    The language switcher hrefs are: "/", "/en/", "/de/", "/it/". Those are preserved because
    #    we only rewrite ones that currently point to / (root) within the FR file.
    #    In FR, the switcher FR entry is href="/" aria-current="true". The others are href="/en/" etc.
    #    So replacing href="/" will catch the BRAND and mobile menu, plus the FR switcher entry.
    #    We need to swap aria-current across switchers before doing href rewrites.

    # a) Move aria-current="true" from FR entry to the target lang entry (desktop + mobile)
    #    FR switcher: <a href="/" aria-current="true" hreflang="fr">FR</a>
    #    target lang: <a href="/en/" hreflang="en">EN</a> (no aria-current)
    out = out.replace(
        f'<a href="/{lang}/" hreflang="{lang}">',
        f'<a href="/{lang}/" aria-current="true" hreflang="{lang}">',
    )
    # Same for the "Français / English / Deutsch / Italiano" mobile labels — they use the same href pattern
    # so the first replace above already handles them.
    # Now remove aria-current from the FR entry since FR is no longer the active lang.
    out = out.replace('<a href="/" aria-current="true" hreflang="fr">', '<a href="/" hreflang="fr">')

    # b) Apply path rewrites
    for old, new in PATH_REWRITES[lang]:
        out = out.replace(old, new)

    # 3) Content translations — order matters : longest / most specific first to avoid
    #    a shorter match shadowing a longer one. Python dicts keep insertion order.
    #    Sort by descending length of the source key to be safe.
    keys_by_len = sorted(TRANSLATIONS.keys(), key=len, reverse=True)
    for src in keys_by_len:
        trans = TRANSLATIONS[src].get(lang)
        if trans is None:
            continue
        out = out.replace(src, trans)

    return out


def main():
    src = SRC.read_text(encoding='utf-8')
    for lang in ('en', 'de', 'it'):
        outdir = OUT_DIR / lang
        outdir.mkdir(exist_ok=True)
        target = outdir / 'index.html'
        html = build_for_lang(lang, src)
        target.write_text(html, encoding='utf-8')
        print(f'✓ {target} ({len(html)} bytes)')


if __name__ == '__main__':
    main()
