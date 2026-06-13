#!/usr/bin/env python3
"""Generate a lieu HTML page from a batch JSON, in any supported locale.

Usage:
    python3 scripts/build_lieu_page.py <batch.json> [--lang fr|en|de|it|es|nl] [--out-dir DIR]

Reads JSON shape produced by batch_activites / batch_plages
(i18n.<lang>.{name, meta_title, meta_description, hero, hero_alt, facts,
body, activities, practical_info, how_to_get_there, when_to_visit,
events, faq, schema_amenities}).

For non-FR builds, reads i18n.<lang> with field-level fallback to i18n.fr.
Chrome strings (section headings, CTA labels, breadcrumb, etc.) are
translated via the CHROME table.

Produces a single-file HTML page at <out_dir>/<slug>.html.
"""
import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
BASE_URL = "https://loisirs74.fr"


def esc(s):
    """HTML-escape, treating None as empty."""
    if s is None:
        return ""
    return html_lib.escape(str(s), quote=False)


def attr(s):
    """HTML-escape for attribute values."""
    if s is None:
        return ""
    return html_lib.escape(str(s), quote=True)


def url_q(s):
    """URL-encode for query string."""
    return quote(str(s), safe="")


def load_static_blocks():
    """Read canonical CSS + trailing JS from scripts/static/*.

    Source of truth: scripts/static/style.css and scripts/static/script.html.
    These are NEVER overwritten by a build, which makes the rebuild idempotent
    across cycles (the bug they fix: when CSS was extracted from a live fiche
    page that was also a rebuild target, each cycle appended another copy of
    the partner-logo rule into the next cycle's template).
    """
    static_dir = REPO / "scripts" / "static"
    css = (static_dir / "style.css").read_text(encoding="utf-8")
    js = (static_dir / "script.html").read_text(encoding="utf-8")
    return css, js


CSS, JS = load_static_blocks()


# Map JSON fact keys → French labels for the facts grid
FACT_LABELS = {
    "type": "Type",
    "access": "Accès",
    "tarif": "Tarif",
    "commune": "Commune",
    "parking": "Parking",
    "dogs": "Animaux",
    "stroller": "Poussette / PMR",
    "duration": "Durée",
    "best_season": "Meilleure saison",
    "lac": "Lac",
    "surveillance": "Surveillance",
    "pavillon_bleu_2026": "Pavillon Bleu 2026",
}
FACT_ORDER = [
    "type", "access", "tarif", "lac", "surveillance",
    "pavillon_bleu_2026", "duration", "best_season",
    "parking", "dogs", "stroller", "commune",
]


SUPPORTED_LANGS = ["fr", "en", "de", "it", "es", "nl"]

# Per-locale chrome strings (everything outside JSON content). Keep keys terse;
# T(key) reaches into CHROME[key][_LANG].
CHROME = {
    "html_lang":       {"fr": "fr", "en": "en", "de": "de", "it": "it", "es": "es", "nl": "nl"},
    "og_locale":       {"fr": "fr_FR", "en": "en_US", "de": "de_DE", "it": "it_IT", "es": "es_ES", "nl": "nl_NL"},
    "in_lang":         {"fr": "fr-FR", "en": "en-US", "de": "de-DE", "it": "it-IT", "es": "es-ES", "nl": "nl-NL"},
    "skip":            {"fr": "Aller au contenu", "en": "Skip to content", "de": "Zum Inhalt springen", "it": "Vai al contenuto", "es": "Saltar al contenido", "nl": "Naar inhoud springen"},
    "home":            {"fr": "Accueil", "en": "Home", "de": "Startseite", "it": "Home", "es": "Inicio", "nl": "Startpagina"},
    "lang_label":      {"fr": "FR", "en": "EN", "de": "DE", "it": "IT", "es": "ES", "nl": "NL"},
    "lang_choose":     {"fr": "Choisir la langue", "en": "Choose a language", "de": "Sprache wählen", "it": "Scegli una lingua", "es": "Elegir idioma", "nl": "Kies een taal"},
    "lang_native":     {"fr": "Français", "en": "English", "de": "Deutsch", "it": "Italiano", "es": "Español", "nl": "Nederlands"},
    # Section kickers (small caps eyebrow above each h2)
    "k_glance":        {"fr": "En un coup d&#39;œil", "en": "At a glance", "de": "Auf einen Blick", "it": "In sintesi", "es": "De un vistazo", "nl": "In een oogopslag"},
    "k_activities":    {"fr": "Activités", "en": "Activities", "de": "Aktivitäten", "it": "Attività", "es": "Actividades", "nl": "Activiteiten"},
    "k_practical":     {"fr": "Pratique", "en": "Practical", "de": "Praktisches", "it": "Pratico", "es": "Práctica", "nl": "Praktisch"},
    "k_access":        {"fr": "Accès", "en": "Access", "de": "Anreise", "it": "Accesso", "es": "Acceso", "nl": "Toegang"},
    "k_when":          {"fr": "Quand venir", "en": "When to visit", "de": "Wann besuchen", "it": "Quando visitare", "es": "Cuándo visitar", "nl": "Wanneer bezoeken"},
    "k_partners":      {"fr": "À proximité", "en": "Nearby", "de": "In der Nähe", "it": "Nelle vicinanze", "es": "Cerca", "nl": "In de buurt"},
    "k_photos":        {"fr": "Photos", "en": "Photos", "de": "Fotos", "it": "Foto", "es": "Fotos", "nl": "Foto's"},
    "k_faq":           {"fr": "FAQ", "en": "FAQ", "de": "FAQ", "it": "FAQ", "es": "FAQ", "nl": "FAQ"},
    "k_sources":       {"fr": "Sources", "en": "Sources", "de": "Quellen", "it": "Fonti", "es": "Fuentes", "nl": "Bronnen"},
    # H2 headings
    "h_whatis":        {"fr": "Qu&#39;est-ce que", "en": "What is", "de": "Was ist", "it": "Cos&#39;è", "es": "Qué es", "nl": "Wat is"},
    "h_activities":    {"fr": "Ce qu&#39;on peut y faire", "en": "What you can do here", "de": "Was man hier machen kann", "it": "Cosa si può fare", "es": "Qué se puede hacer", "nl": "Wat je hier kunt doen"},
    "h_practical":     {"fr": "Infos pratiques", "en": "Practical information", "de": "Praktische Informationen", "it": "Informazioni pratiche", "es": "Información práctica", "nl": "Praktische informatie"},
    "h_how":           {"fr": "Comment y aller", "en": "How to get there", "de": "So kommen Sie hin", "it": "Come arrivare", "es": "Cómo llegar", "nl": "Hoe te komen"},
    "h_when":          {"fr": "Quand visiter", "en": "When to visit", "de": "Wann besuchen", "it": "Quando visitare", "es": "Cuándo visitar", "nl": "Wanneer bezoeken"},
    "h_partners":      {"fr": "Où manger, boire, dormir", "en": "Where to eat, drink, stay", "de": "Essen, Trinken, Übernachten", "it": "Dove mangiare, bere, dormire", "es": "Dónde comer, beber, alojarse", "nl": "Waar eten, drinken, overnachten"},
    "h_gallery":       {"fr": "Galerie", "en": "Gallery", "de": "Galerie", "it": "Galleria", "es": "Galería", "nl": "Galerij"},
    "h_faq":           {"fr": "Questions fréquentes", "en": "Frequently asked questions", "de": "Häufige Fragen", "it": "Domande frequenti", "es": "Preguntas frecuentes", "nl": "Veelgestelde vragen"},
    "h_sources":       {"fr": "Sources &amp; vérifications", "en": "Sources &amp; verification", "de": "Quellen &amp; Prüfung", "it": "Fonti &amp; verifiche", "es": "Fuentes &amp; verificaciones", "nl": "Bronnen &amp; verificatie"},
    # Hero / CTAs
    "free_dot":        {"fr": "Gratuit · Accès libre", "en": "Free · Open access", "de": "Kostenlos · Freier Zugang", "it": "Gratis · Accesso libero", "es": "Gratis · Acceso libre", "nl": "Gratis · Vrije toegang"},
    "paid_dot":        {"fr": "Payant · Réservation en ligne", "en": "Paid · Book online", "de": "Kostenpflichtig · Online buchen", "it": "A pagamento · Prenota online", "es": "De pago · Reservar en línea", "nl": "Betaald · Online reserveren"},
    "paid_prefix":     {"fr": "Payant · ", "en": "Paid · ", "de": "Kostenpflichtig · ", "it": "A pagamento · ", "es": "De pago · ", "nl": "Betaald · "},
    "free_word":       {"fr": "Gratuit", "en": "Free", "de": "Kostenlos", "it": "Gratis", "es": "Gratis", "nl": "Gratis"},
    "book":            {"fr": "Réserver", "en": "Book", "de": "Buchen", "it": "Prenota", "es": "Reservar", "nl": "Reserveren"},
    "map_view":        {"fr": "Voir sur la carte", "en": "View on map", "de": "Auf Karte ansehen", "it": "Vedi sulla mappa", "es": "Ver en el mapa", "nl": "Bekijk op kaart"},
    "official_site":   {"fr": "Site officiel", "en": "Official site", "de": "Offizielle Website", "it": "Sito ufficiale", "es": "Sitio oficial", "nl": "Officiële site"},
    "directions":      {"fr": "Itinéraire", "en": "Directions", "de": "Wegbeschreibung", "it": "Indicazioni", "es": "Cómo llegar", "nl": "Route"},
    "maps_open":       {"fr": "Ouvrir dans Maps", "en": "Open in Maps", "de": "In Maps öffnen", "it": "Apri in Maps", "es": "Abrir en Maps", "nl": "Openen in Maps"},
    # How-to mode labels
    "how_car":         {"fr": "En voiture", "en": "By car", "de": "Mit dem Auto", "it": "In auto", "es": "En coche", "nl": "Met de auto"},
    "how_transit":     {"fr": "Transports en commun", "en": "Public transport", "de": "Öffentliche Verkehrsmittel", "it": "Trasporti pubblici", "es": "Transporte público", "nl": "Openbaar vervoer"},
    "how_bike":        {"fr": "À vélo", "en": "By bike", "de": "Mit dem Fahrrad", "it": "In bici", "es": "En bici", "nl": "Met de fiets"},
    "events_label":    {"fr": "Événements", "en": "Events", "de": "Veranstaltungen", "it": "Eventi", "es": "Eventos", "nl": "Evenementen"},
    # Flip-card hints
    "tap_to_read":     {"fr": "Toucher pour lire", "en": "Tap to read", "de": "Tippen zum Lesen", "it": "Tocca per leggere", "es": "Toca para leer", "nl": "Tik om te lezen"},
    "hover_for_site":  {"fr": "Survoler pour voir le site", "en": "Hover to view site", "de": "Bewegen für Website", "it": "Passa sopra per il sito", "es": "Pasa para ver el sitio", "nl": "Hover voor de site"},
    "see_site":        {"fr": "Voir le site", "en": "Visit site", "de": "Website ansehen", "it": "Vedi il sito", "es": "Ver el sitio", "nl": "Bekijk site"},
    # Partner card chrome
    "partner_badge":   {"fr": "Partenaire", "en": "Partner", "de": "Partner", "it": "Partner", "es": "Socio", "nl": "Partner"},
    "partner_nearby":  {"fr": "À proximité", "en": "Nearby", "de": "In der Nähe", "it": "Nelle vicinanze", "es": "Cerca", "nl": "In de buurt"},
    "p_address":       {"fr": "Adresse", "en": "Address", "de": "Adresse", "it": "Indirizzo", "es": "Dirección", "nl": "Adres"},
    "p_phone":         {"fr": "Téléphone", "en": "Phone", "de": "Telefon", "it": "Telefono", "es": "Teléfono", "nl": "Telefoon"},
    "p_email":         {"fr": "Email", "en": "Email", "de": "E-Mail", "it": "Email", "es": "Email", "nl": "E-mail"},
    "p_hours":         {"fr": "Horaires", "en": "Hours", "de": "Öffnungszeiten", "it": "Orari", "es": "Horarios", "nl": "Openingstijden"},
    "become_partner":  {"fr": "Devenir partenaire", "en": "Become a partner", "de": "Partner werden", "it": "Diventa partner", "es": "Convertirse en socio", "nl": "Partner worden"},
    # Default-invite teasers (fall-back partner cards when none configured)
    "invite_resto_t":  {"fr": "Un restaurant", "en": "A restaurant", "de": "Ein Restaurant", "it": "Un ristorante", "es": "Un restaurante", "nl": "Een restaurant"},
    "invite_resto_d":  {"fr": "Vous accueillez les visiteurs de", "en": "Hosting visitors of", "de": "Empfangen Sie Besucher von", "it": "Accogli i visitatori di", "es": "¿Recibe a los visitantes de", "nl": "Verwelkomt u bezoekers van"},
    "invite_resto_d2": {"fr": "Apparaissez ici.", "en": "Appear here.", "de": "Zeigen Sie sich hier.", "it": "Apparite qui.", "es": "Aparezca aquí.", "nl": "Verschijn hier."},
    "invite_com_t":    {"fr": "Une boulangerie, un commerce", "en": "A bakery, a shop", "de": "Bäckerei oder Geschäft", "it": "Una panetteria, un negozio", "es": "Una panadería, un comercio", "nl": "Een bakker, een winkel"},
    "invite_com_d":    {"fr": "Partagez horaires et spécialités avec les visiteurs de", "en": "Share hours and specialties with visitors of", "de": "Teilen Sie Öffnungszeiten und Spezialitäten mit Besuchern von", "it": "Condividi orari e specialità con i visitatori di", "es": "Comparta horarios y especialidades con los visitantes de", "nl": "Deel openingstijden en specialiteiten met bezoekers van"},
    "invite_hosp_t":   {"fr": "Un hébergement proche", "en": "A nearby stay", "de": "Übernachtung in der Nähe", "it": "Un alloggio vicino", "es": "Un alojamiento cercano", "nl": "Een nabijgelegen verblijf"},
    "invite_hosp_d":   {"fr": "Gîte, chambre d&#39;hôtes, camping, location", "en": "Gîte, B&amp;B, campsite, rental", "de": "Ferienhaus, B&amp;B, Campingplatz, Vermietung", "it": "Gîte, B&amp;B, campeggio, affitto", "es": "Gîte, B&amp;B, camping, alquiler", "nl": "Gîte, B&amp;B, camping, verhuur"},
    "in_town":         {"fr": "à", "en": "in", "de": "in", "it": "a", "es": "en", "nl": "in"},
    "qmark":           {"fr": " ?", "en": "?", "de": "?", "it": "?", "es": "?", "nl": "?"},
    # Gallery invite
    "g_been_q":        {"fr": "Vous y êtes allé ?", "en": "Been there?", "de": "Schon dort gewesen?", "it": "Ci sei stato?", "es": "¿Ha estado allí?", "nl": "Bent u er geweest?"},
    "g_invite":        {"fr": "Partagez vos photos — nous les ajoutons à cette page avec votre crédit. Tag #loisirs74 ou écrivez à", "en": "Share your photos — we&#39;ll add them to this page with credit. Tag #loisirs74 or email", "de": "Teilen Sie Ihre Fotos — wir fügen sie mit Bildnachweis hinzu. Tag #loisirs74 oder schreiben Sie an", "it": "Condividi le tue foto — le aggiungiamo con il tuo credito. Tag #loisirs74 o scrivi a", "es": "Comparta sus fotos — las añadimos con crédito. Tag #loisirs74 o escriba a", "nl": "Deel uw foto&#39;s — wij voegen ze met credit toe. Tag #loisirs74 of mail naar"},
    # Sources caveat
    "src_caveat":      {"fr": "Vérifications multi-sources à la date de publication. Les informations peuvent évoluer — confirmez auprès du gestionnaire officiel avant un déplacement.", "en": "Multi-source verification at publication. Information may change — confirm with the official operator before travelling.", "de": "Mehrquellen-Verifizierung zum Veröffentlichungsdatum. Informationen können sich ändern — bestätigen Sie diese vor der Anreise beim offiziellen Betreiber.", "it": "Verifica multi-fonte alla data di pubblicazione. Le informazioni possono cambiare — confermare con il gestore ufficiale prima del viaggio.", "es": "Verificación multi-fuente en la fecha de publicación. La información puede cambiar — confirme con el operador oficial antes de viajar.", "nl": "Multi-bron verificatie bij publicatie. Informatie kan veranderen — bevestig bij de officiële beheerder vóór vertrek."},
    "data_partial":    {"fr": "Données partielles :", "en": "Partial data:", "de": "Teildaten:", "it": "Dati parziali:", "es": "Datos parciales:", "nl": "Gedeeltelijke gegevens:"},
    "via":             {"fr": "via", "en": "via", "de": "via", "it": "via", "es": "vía", "nl": "via"},
    # Footer dates
    "published":       {"fr": "Publié le", "en": "Published", "de": "Veröffentlicht", "it": "Pubblicato il", "es": "Publicado el", "nl": "Gepubliceerd"},
    "updated":         {"fr": "Mis à jour le", "en": "Updated", "de": "Aktualisiert", "it": "Aggiornato il", "es": "Actualizado el", "nl": "Bijgewerkt"},
    # Generic photo overlay text (CSS post-process)
    "generic":         {"fr": "Générique", "en": "Generic", "de": "Generisch", "it": "Generico", "es": "Genérico", "nl": "Algemeen"},
    # Photo email subject prefix
    "photos_subject":  {"fr": "Photos%20—%20", "en": "Photos%20—%20", "de": "Fotos%20—%20", "it": "Foto%20—%20", "es": "Fotos%20—%20", "nl": "Foto%27s%20—%20"},
    # Site footer columns
    "f_tagline":       {"fr": "Guide indépendant des lieux de loisirs en Haute-Savoie. 100% gratuit. 100% vérifié.", "en": "Independent guide to leisure spots in Haute-Savoie. 100% free. 100% verified.", "de": "Unabhängiger Freizeit-Guide für Haute-Savoie. 100% kostenlos. 100% geprüft.", "it": "Guida indipendente ai luoghi di svago in Alta Savoia. 100% gratis. 100% verificato.", "es": "Guía independiente de los lugares de ocio en Alta Saboya. 100% gratis. 100% verificado.", "nl": "Onafhankelijke gids voor vrijetijdsbestedingen in Haute-Savoie. Gratis. Geverifieerd."},
    "f_explore":       {"fr": "Explorer", "en": "Explore", "de": "Entdecken", "it": "Esplora", "es": "Explorar", "nl": "Verkennen"},
    "f_contribute":    {"fr": "Contribuer", "en": "Contribute", "de": "Beitragen", "it": "Contribuisci", "es": "Contribuir", "nl": "Bijdragen"},
    "f_send_photos":   {"fr": "Envoyer des photos", "en": "Send photos", "de": "Fotos senden", "it": "Invia foto", "es": "Enviar fotos", "nl": "Foto&#39;s sturen"},
    "f_report":        {"fr": "Signaler une info", "en": "Report info", "de": "Info melden", "it": "Segnala info", "es": "Reportar info", "nl": "Info melden"},
    "f_become_p":      {"fr": "Devenir partenaire", "en": "Become a partner", "de": "Partner werden", "it": "Diventa partner", "es": "Hacerse socio", "nl": "Partner worden"},
    "f_legal":         {"fr": "Mentions", "en": "Legal", "de": "Rechtliches", "it": "Note legali", "es": "Legal", "nl": "Juridisch"},
    "f_legal_link":    {"fr": "Mentions légales", "en": "Legal notice", "de": "Impressum", "it": "Note legali", "es": "Avisos legales", "nl": "Wettelijke vermeldingen"},
    "f_privacy":       {"fr": "Confidentialité", "en": "Privacy", "de": "Datenschutz", "it": "Privacy", "es": "Privacidad", "nl": "Privacy"},
    "f_cgv":           {"fr": "CGV", "en": "Terms", "de": "AGB", "it": "Termini", "es": "Términos", "nl": "Algemene voorwaarden"},
    "f_copyright":     {"fr": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Tous droits réservés", "en": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · All rights reserved", "de": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Alle Rechte vorbehalten", "it": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Tutti i diritti riservati", "es": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Todos los derechos reservados", "nl": "© 2026 Blue Canard Éditions · Edmaster &amp; Claudius · Alle rechten voorbehouden"},
    "f_promise":       {"fr": "Sans pub. Sans tracking. Sans avis Google.", "en": "No ads. No tracking. No Google reviews.", "de": "Keine Werbung. Kein Tracking. Keine Google-Bewertungen.", "it": "Niente pubblicità. Niente tracking. Niente recensioni Google.", "es": "Sin anuncios. Sin tracking. Sin reseñas de Google.", "nl": "Geen advertenties. Geen tracking. Geen Google reviews."},
}

# Per-locale FACT_LABELS for the facts grid
FACT_LABELS_I18N = {
    "type":        {"fr": "Type", "en": "Type", "de": "Typ", "it": "Tipo", "es": "Tipo", "nl": "Type"},
    "access":      {"fr": "Accès", "en": "Access", "de": "Anreise", "it": "Accesso", "es": "Acceso", "nl": "Toegang"},
    "tarif":       {"fr": "Tarif", "en": "Price", "de": "Preis", "it": "Prezzo", "es": "Precio", "nl": "Prijs"},
    "commune":     {"fr": "Commune", "en": "Town", "de": "Ort", "it": "Comune", "es": "Comuna", "nl": "Gemeente"},
    "parking":     {"fr": "Parking", "en": "Parking", "de": "Parkplatz", "it": "Parcheggio", "es": "Aparcamiento", "nl": "Parkeren"},
    "dogs":        {"fr": "Animaux", "en": "Animals", "de": "Tiere", "it": "Animali", "es": "Animales", "nl": "Dieren"},
    "stroller":    {"fr": "Poussette / PMR", "en": "Stroller / Reduced mobility", "de": "Kinderwagen / Behinderte", "it": "Passeggino / Disabilità", "es": "Cochecito / PMR", "nl": "Kinderwagen / Mindervaliden"},
    "duration":    {"fr": "Durée", "en": "Duration", "de": "Dauer", "it": "Durata", "es": "Duración", "nl": "Duur"},
    "best_season": {"fr": "Meilleure saison", "en": "Best season", "de": "Beste Saison", "it": "Stagione migliore", "es": "Mejor temporada", "nl": "Beste seizoen"},
    "lac":         {"fr": "Lac", "en": "Lake", "de": "See", "it": "Lago", "es": "Lago", "nl": "Meer"},
    "surveillance":{"fr": "Surveillance", "en": "Lifeguarded", "de": "Bewacht", "it": "Sorvegliato", "es": "Vigilado", "nl": "Bewaakt"},
    "pavillon_bleu_2026": {"fr": "Pavillon Bleu 2026", "en": "Blue Flag 2026", "de": "Blaue Flagge 2026", "it": "Bandiera Blu 2026", "es": "Bandera Azul 2026", "nl": "Blauwe Vlag 2026"},
}

# Module-level locale state set by build_page(d, lang).
_LANG = "fr"            # current locale
_LOC = None             # i18n.<lang> block, frozen-merged with FR fallback below
_FR = None              # i18n.fr block (fallback source)
_FALLBACK_FIELDS = set()  # fields where current build fell back to FR
_AVAILABLE_LANGS = ("fr",)  # langs this fiche actually has populated in i18n (for hreflang block)


def T(key):
    """Chrome string lookup with FR-fallback."""
    row = CHROME.get(key, {})
    return row.get(_LANG) or row.get("fr") or ""


def _set_lang(d, lang):
    """Wire module-level state for the current build pass."""
    global _LANG, _LOC, _FR, _FALLBACK_FIELDS, _AVAILABLE_LANGS
    _LANG = lang if lang in SUPPORTED_LANGS else "fr"
    i18n = d.get("i18n", {}) or {}
    _FR = i18n.get("fr") or {}
    _LOC = i18n.get(_LANG) or {}
    _FALLBACK_FIELDS = set()
    _AVAILABLE_LANGS = tuple(L for L in SUPPORTED_LANGS if L in i18n and i18n.get(L))


def L(key, default=""):
    """Locale-field lookup with FR fallback. Empty string / None / [] / {} count as missing."""
    v = _LOC.get(key) if isinstance(_LOC, dict) else None
    if v not in (None, "", [], {}):
        return v
    v = _FR.get(key) if isinstance(_FR, dict) else None
    if v not in (None, "", [], {}):
        _FALLBACK_FIELDS.add(key)
        return v
    return default


def L_body(key, default=""):
    """Locale-body lookup: i18n.<lang>.body.<key>, fall back to i18n.<lang>.<key>,
    fall back to i18n.fr.body.<key>, then i18n.fr.<key>."""
    for src_lang, src in ((_LANG, _LOC), ("fr", _FR)):
        if not isinstance(src, dict):
            continue
        body = src.get("body") if isinstance(src.get("body"), dict) else {}
        v = body.get(key) if body else None
        if v not in (None, "", [], {}):
            if src_lang != _LANG:
                _FALLBACK_FIELDS.add(f"body.{key}")
            return v
        v = src.get(key)
        if v not in (None, "", [], {}):
            if src_lang != _LANG:
                _FALLBACK_FIELDS.add(f"body.{key}")
            return v
    return default


CAT_TO_FR_HUB = {
    # `attraction` retired in the 2026-06 hub overhaul (split across
    # sport-jeux / sensations-plein-air / baignade-nautisme / parcs-jardins /
    # sorties-detente — no 1:1 mapping from old category). Breadcrumb falls
    # back to commune-name span for these.
    "cascade": ("cascades", "Cascades"),
    "chateau": ("chateaux", "Châteaux"),
    # `divers` retired in the 2026-06 hub overhaul → no breadcrumb hub link
    "domaine": ("bases-de-loisirs", "Bases de loisirs"),
    # `lac` + `plage` merged into /lacs-plages/ in the 2026-06 hub overhaul
    "lac": ("lacs-plages", "Lacs & plages"),
    "musee": ("musees", "Musées"),
    "parc": ("bases-de-loisirs", "Bases de loisirs"),
    "plage": ("lacs-plages", "Lacs & plages"),
    "point-de-vue": ("points-de-vue", "Points de vue"),
    "sentier": ("sentiers", "Sentiers"),
    "telecabine": ("telecabines", "Télécabines"),
    "voie-verte": ("voies-vertes", "Voies vertes"),
}


# Per-locale hub-slug map: FR slug → {lang: localized slug}.
# Single source of truth for breadcrumb URL + label in non-FR locales.
# Must stay in sync with scripts/build_hubs.py hub_locale_map() output;
# audit_breadcrumbs.py also relies on these labels.
HUB_LOCALE_SLUGS = {
    "cascades":        {"fr": "cascades",        "en": "waterfalls",     "de": "wasserfaelle",      "it": "cascate",         "es": "cascadas",     "nl": "watervallen"},
    "chateaux":        {"fr": "chateaux",        "en": "castles",        "de": "schloesser",        "it": "castelli",        "es": "castillos",    "nl": "kastelen"},
    "musees":          {"fr": "musees",          "en": "museums",        "de": "museen",            "it": "musei",           "es": "museos",       "nl": "musea"},
    "points-de-vue":   {"fr": "points-de-vue",   "en": "viewpoints",     "de": "aussichtspunkte",   "it": "punti-panoramici","es": "miradores",    "nl": "uitzichtpunten"},
    "sentiers":        {"fr": "sentiers",        "en": "trails",         "de": "wanderwege",        "it": "sentieri",        "es": "senderos",     "nl": "wandelpaden"},
    "telecabines":     {"fr": "telecabines",     "en": "cable-cars",     "de": "seilbahnen",        "it": "funivie",         "es": "telefericos",  "nl": "kabelbanen"},
    "voies-vertes":    {"fr": "voies-vertes",    "en": "greenways",      "de": "radwege",           "it": "vie-verdi",       "es": "vias-verdes",  "nl": "fietsroutes"},
    "lacs-plages":     {"fr": "lacs-plages",     "en": "lakes",          "de": "seen",              "it": "laghi",           "es": "lagos",        "nl": "meren"},
    "bases-de-loisirs":{"fr": "bases-de-loisirs","en": "leisure-parks",  "de": "freizeitparks",     "it": "aree-ricreative", "es": "areas-de-ocio","nl": "recreatieparken"},
}

HUB_LOCALE_LABELS = {
    "cascades":        {"fr": "Cascades",         "en": "Waterfalls",       "de": "Wasserfälle",      "it": "Cascate",          "es": "Cascadas",      "nl": "Watervallen"},
    "chateaux":        {"fr": "Châteaux",         "en": "Castles",          "de": "Schlösser",        "it": "Castelli",         "es": "Castillos",     "nl": "Kastelen"},
    "musees":          {"fr": "Musées",           "en": "Museums",          "de": "Museen",           "it": "Musei",            "es": "Museos",        "nl": "Musea"},
    "points-de-vue":   {"fr": "Points de vue",    "en": "Viewpoints",       "de": "Aussichtspunkte",  "it": "Punti panoramici", "es": "Miradores",     "nl": "Uitzichtpunten"},
    "sentiers":        {"fr": "Sentiers",         "en": "Trails",           "de": "Wanderwege",       "it": "Sentieri",         "es": "Senderos",      "nl": "Wandelpaden"},
    "telecabines":     {"fr": "Télécabines",      "en": "Cable cars",       "de": "Seilbahnen",       "it": "Funivie",          "es": "Teleféricos",   "nl": "Kabelbanen"},
    "voies-vertes":    {"fr": "Voies vertes",     "en": "Greenways",        "de": "Radwege",          "it": "Vie verdi",        "es": "Vías verdes",   "nl": "Fietsroutes"},
    "lacs-plages":     {"fr": "Lacs & plages",    "en": "Lakes",            "de": "Seen",             "it": "Laghi",            "es": "Lagos",         "nl": "Meren"},
    "bases-de-loisirs":{"fr": "Bases de loisirs", "en": "Leisure parks",    "de": "Freizeitparks",    "it": "Aree ricreative",  "es": "Áreas de ocio", "nl": "Recreatieparken"},
}


def primary_hub(d, lang=None):
    """Return (hub_slug, hub_label) for the fiche's primary hub, localized to
    `lang` (defaults to the module-level _LANG set by build_page).

    The breadcrumb URL must point to the locale-rendered hub
    (e.g. /en/castles/, /de/schloesser/), and the label must read in the
    same language as the page chrome — otherwise Googlebot sees a
    contradiction between visible breadcrumb and JSON-LD BreadcrumbList.
    """
    cats = d.get("categories") or ([d.get("category")] if d.get("category") else [])
    L = lang or _LANG
    for c in cats:
        fr_pair = CAT_TO_FR_HUB.get(c)
        if not fr_pair:
            continue
        fr_slug, fr_label = fr_pair
        slug = HUB_LOCALE_SLUGS.get(fr_slug, {}).get(L, fr_slug)
        label = HUB_LOCALE_LABELS.get(fr_slug, {}).get(L, fr_label)
        return (slug, label)
    return None


def hammer_h1(name):
    """Wrap name as hammer-animated h1 with the last word italicised."""
    parts = name.split()
    if not parts:
        return f'<h1 class="hammer">{esc(name)}</h1>'
    spans = []
    for i, w in enumerate(parts):
        if i == len(parts) - 1 and len(parts) > 1:
            spans.append(f'<span class="w"><em>{esc(w)}</em></span>')
        else:
            spans.append(f'<span class="w">{esc(w)}</span>')
    return f'<h1 class="hammer">{" ".join(spans)}</h1>'


def _fact_label(k):
    """Lookup the locale-translated fact-label for key k."""
    row = FACT_LABELS_I18N.get(k)
    if row:
        return row.get(_LANG) or row.get("fr") or FACT_LABELS.get(k, k)
    return FACT_LABELS.get(k, k.replace("_", " ").capitalize())


def facts_block(facts):
    """Render the 'At a glance' grid (locale-aware)."""
    items = []
    seen = set()
    for k in FACT_ORDER:
        if k in facts and facts[k]:
            v = facts[k]
            ok_class = ""
            # Mark positive parking/free as ok (FR sniff still valid — values are
            # source-side strings that we render as-is per fiche)
            if k == "parking" and re.search(r"gratuit|free|kostenlos|gratis", v, re.I):
                ok_class = " ok"
            elif k == "access" and re.search(r"libre|gratuit|free|frei|libero|libre|vrij", v, re.I):
                ok_class = " ok"
            items.append(
                f'<div class="fact"><div class="k">{esc(_fact_label(k))}</div>'
                f'<div class="v{ok_class}">{esc(v)}</div></div>'
            )
            seen.add(k)
    for k, v in facts.items():
        if k in seen or not v:
            continue
        items.append(
            f'<div class="fact"><div class="k">{esc(_fact_label(k))}</div>'
            f'<div class="v">{esc(v)}</div></div>'
        )
    if not items:
        return ""
    return (
        '<section class="block"><div class="wrap"><div class="kicker reveal">'
        f"{T('k_glance')}</div>"
        f'<div class="facts reveal" data-stagger>{"".join(items)}</div></div></section>'
    )


def body_block(name, body):
    """Render the 'What is <name>' section. body is dict with 'what_is' HTML."""
    what_is = body.get("what_is", "") if isinstance(body, dict) else str(body or "")
    if not what_is.strip():
        return ""
    return (
        '<section class="block"><div class="wrap">'
        f'<h2 class="reveal">{T("h_whatis")} {esc(name)}</h2>'
        f'<div class="reveal">{what_is}</div></div></section>'
    )


def flip_hint():
    return (
        '<span class="hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>'
        '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
        f'</svg> {T("tap_to_read")}</span>'
    )


def activities_block(activities):
    """Render flip-card grid."""
    if not activities:
        return ""
    cards = []
    for a in activities:
        title = a.get("title", "")
        tag = a.get("tag", "")
        desc = a.get("description", "")
        tag_html = f'<span class="activity-tag">{esc(tag)}</span>' if tag else ""
        cards.append(
            f'<button type="button" class="activity flip" aria-label="{attr(title)}">'
            f'<div class="flip-inner">'
            f'<div class="flip-front">'
            f'<h4>{esc(title)}{tag_html}</h4>'
            f'<p class="preview">{esc(desc)}</p>'
            f'{flip_hint()}'
            f'</div>'
            f'<div class="flip-back"><h4>{esc(title)}</h4><p>{esc(desc)}</p></div>'
            f'</div></button>'
        )
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_activities")}</div>'
        f'<h2 class="reveal">{T("h_activities")}</h2>'
        f'<div class="activities reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def practical_block(practical, name, commune):
    """Render the 'Infos pratiques' info-table."""
    if not practical:
        return ""
    rows = []
    addr_terms = ("adresse", "address", "adres", "indirizzo", "dirección")
    for entry in practical:
        k = entry.get("k", "")
        v = entry.get("v", "")
        extra = ""
        if any(k.lower().startswith(t) for t in addr_terms):
            q = url_q(f"{name}, {commune}, Haute-Savoie, France")
            extra = (
                f' <a href="https://www.google.com/maps/search/?api=1&query={q}" '
                'target="_blank" rel="noopener" class="inline-link">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
                f'<circle cx="12" cy="10" r="3"/></svg>{T("map_view")}</a>'
            )
        rows.append(
            f'<div class="info-row"><div class="k">{esc(k)}</div>'
            f'<div class="v"><span>{esc(v)}{extra}</span></div></div>'
        )
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_practical")}</div>'
        f'<h2 class="reveal">{T("h_practical")}</h2>'
        f'<div class="info-table reveal">{"".join(rows)}</div></div></section>'
    )


HOW_ICONS = {
    "car": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 17h14M5 17V11l2-6h10l2 6v6M5 17H3M19 17h2M7 17v2h2v-2M15 17v2h2v-2"/>'
        '<circle cx="7" cy="14" r="1"/><circle cx="17" cy="14" r="1"/></svg>'
    ),
    "public_transport": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="4" y="3" width="16" height="14" rx="2"/>'
        '<path d="M4 11h16M8 17v2M16 17v2"/><circle cx="8" cy="14" r="1"/>'
        '<circle cx="16" cy="14" r="1"/></svg>'
    ),
    "bike": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/>'
        '<path d="M6 17l4-9h4l3 9M14 8l-2-4h-2"/></svg>'
    ),
}
HOW_MODE = {
    "car": ("how_car", "driving"),
    "public_transport": ("how_transit", "transit"),
    "bike": ("how_bike", "bicycling"),
}


def how_to_block(how, name, commune):
    """Render the 'How to get there' how-cards (locale-aware)."""
    if not how:
        return ""
    q = url_q(f"{name}, {commune}, Haute-Savoie")
    cards = []
    for key in ("car", "public_transport", "bike"):
        text = how.get(key)
        if not text:
            continue
        chrome_key, travelmode = HOW_MODE[key]
        label = T(chrome_key)
        icon = HOW_ICONS[key]
        cards.append(
            f'<a class="how-card" href="https://www.google.com/maps/dir/?api=1'
            f"&destination={q}&travelmode={travelmode}" + '" '
            f'target="_blank" rel="noopener">'
            f'<div class="icon">{icon}</div>'
            f'<h3>{esc(label)}</h3>'
            f'<p>{esc(text)}</p>'
            f'<span class="open">{T("maps_open")} '
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'
            '</svg></span></a>'
        )
    if not cards:
        return ""
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_access")}</div>'
        f'<h2 class="reveal">{T("h_how")}</h2>'
        f'<div class="how reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def when_to_visit_block(when, events):
    """Render 'When to visit' + optional events (locale-aware)."""
    if not when and not events:
        return ""
    inner = ""
    if when:
        inner += f'<div class="reveal">{esc(when)}</div>'
    if events:
        inner += (
            '<div class="reveal" style="margin-top:1.25rem">'
            f'<strong>{T("events_label")}&nbsp;:</strong> {esc(events)}</div>'
        )
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_when")}</div>'
        f'<h2 class="reveal">{T("h_when")}</h2>'
        f"{inner}</div></section>"
    )


def faq_block(faq):
    if not faq:
        return ""
    items = []
    for entry in faq:
        q = entry.get("q", "")
        a = entry.get("a", "")
        items.append(
            f"<details class=\"faq\"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        )
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_faq")}</div>'
        f'<h2 class="reveal">{T("h_faq")}</h2>'
        f'<div class="faq-grid reveal" data-stagger>{"".join(items)}</div>'
        '</div></section>'
    )


LINK_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
)


def sources_block(sources):
    if not sources:
        return ""
    items = []
    for src in sources:
        if isinstance(src, dict):
            url = src.get("url", "")
            label = src.get("name") or re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        else:
            url = src
            label = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        items.append(
            f'<li>{LINK_ICON}<a href="{attr(url)}" target="_blank" rel="noopener">'
            f"{esc(label)}</a></li>"
        )
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_sources")}</div>'
        f'<h2 class="reveal">{T("h_sources")}</h2>'
        f'<div class="sources reveal"><ul>{"".join(items)}</ul>'
        f'<p class="caveat">{T("src_caveat")}</p></div></div></section>'
    )


def data_credits_block(data_sources):
    """Per-fiche attribution line for content lifted from licensed third-party feeds
    (DataTourisme et al.). Required by Licence Ouverte 2.0 / Etalab."""
    if not data_sources:
        return ""
    captions = []
    for ds in data_sources:
        creator = ds.get("creator") or ""
        creator_url = ds.get("creator_url") or ""
        platform = ds.get("platform") or ""
        publisher = ds.get("publisher") or ""
        license_name = ds.get("license") or ""
        license_url = ds.get("license_url") or ""
        creator_html = (
            f'<a href="{attr(creator_url)}" target="_blank" rel="noopener">{esc(creator)}</a>'
            if creator_url else esc(creator)
        )
        license_html = (
            f'<a href="{attr(license_url)}" target="_blank" rel="noopener">{esc(license_name)}</a>'
            if license_url else esc(license_name)
        )
        via_parts = [p for p in (platform, publisher) if p]
        via = " · ".join(esc(p) for p in via_parts)
        captions.append(
            f'{T("data_partial")} {creator_html} {T("via")} {via} · {license_html}'
        )
    return (
        '<aside class="data-credits reveal"><div class="wrap">'
        '<p class="data-credits-line">'
        + " — ".join(captions)
        + "</p></div></aside>"
    )


PARTNER_TYPE_ICON = {
    "restaurant": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h2c1.1 0 2-.9 2-2V2M5 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
    "commerce":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
    "hebergement":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
}
SVG_ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round">'
             '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>')
SVG_EXT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
           '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>')
SVG_ROTATE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round">'
              '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>'
              '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>')
SVG_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
             'stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>')

def _filled_partner_card(p):
    """Render a partner card.

    tier:partner / tier:recommended → flip card (compact, 3-col grid fit).
    tier:featured → static rich card with always-visible contact info (no flip).
    """
    tier = p.get("tier", "partner")
    badge_text = T("partner_nearby") if tier == "recommended" else T("partner_badge")
    badge_icon = "" if tier == "recommended" else SVG_CHECK
    name = p.get("name", "")
    p_i18n = p.get("i18n", {}) or {}
    desc = (p_i18n.get(_LANG, {}) or {}).get("description") \
        or (p_i18n.get("fr", {}) or {}).get("description") \
        or p.get("description", "")
    url = p.get("url", "#")
    cta = p.get("cta_text") or T("see_site")

    if tier == "featured":
        address = p.get("address", "")
        phone = p.get("phone", "")
        phone_tel = p.get("phone_tel") or (re.sub(r"[^\d+]", "", phone) if phone else "")
        email = p.get("email", "")
        hours = p.get("hours", "")
        logo = p.get("logo", "")
        extras = []
        if address:
            extras.append(f'<div class="partner-row"><span class="label">{T("p_address")}</span><span>{esc(address)}</span></div>')
        if phone:
            href = f"tel:{phone_tel}" if phone_tel else f"tel:{phone.replace(' ', '')}"
            extras.append(f'<div class="partner-row"><span class="label">{T("p_phone")}</span><a href="{attr(href)}">{esc(phone)}</a></div>')
        if email:
            extras.append(f'<div class="partner-row"><span class="label">{T("p_email")}</span><a href="mailto:{attr(email)}">{esc(email)}</a></div>')
        if hours:
            extras.append(f'<div class="partner-row"><span class="label">{T("p_hours")}</span><span>{esc(hours)}</span></div>')
        extras_html = f'<div class="partner-extras">{"".join(extras)}</div>' if extras else ""
        cta_html = (
            f'<a class="cta" href="{attr(url)}" target="_blank" rel="noopener">{esc(cta)} {SVG_EXT}</a>'
            if url and url != "#" else ""
        )
        logo_html = (
            f'<img class="partner-logo" src="{attr(logo)}" alt="Logo {attr(name)}" loading="lazy">'
            if logo else ""
        )
        return (
            f'<article class="partner static tier-featured">'
            f'<span class="badge">{badge_icon} {esc(badge_text)}</span>'
            f'{logo_html}'
            f'<h4>{esc(name)}</h4>'
            f'<p class="desc">{esc(desc)}</p>'
            f'{extras_html}'
            f'{cta_html}'
            f'</article>'
        )

    return (
        f'<button type="button" class="partner flip tier-{attr(tier)}" aria-label="{attr(name)}">'
        '<div class="flip-inner">'
        '<div class="flip-front">'
        f'<span class="badge">{badge_icon} {esc(badge_text)}</span>'
        f'<h4>{esc(name)}</h4>'
        f'<p class="preview">{esc(desc)}</p>'
        f'<span class="hint">{SVG_ROTATE} {T("hover_for_site")}</span>'
        '</div>'
        '<div class="flip-back">'
        f'<h4>{esc(name)}</h4>'
        f'<p>{esc(desc)}</p>'
        f'<a class="cta" href="{attr(url)}" target="_blank" rel="noopener">{esc(cta)} {SVG_EXT}</a>'
        '</div>'
        '</div>'
        '</button>'
    )

def _invite_card(p, slug):
    """Render a tier:invite partner card (locale-aware)."""
    invite_type = p.get("invite_type", "restaurant")
    icon = PARTNER_TYPE_ICON.get(invite_type, PARTNER_TYPE_ICON["restaurant"])
    p_i18n = p.get("i18n", {}) or {}
    loc = p_i18n.get(_LANG) or p_i18n.get("fr") or {}
    title = loc.get("title") or p.get("invite_title", "")
    desc = loc.get("desc") or p.get("invite_desc", "")
    lang_prefix = f"/{_LANG}" if _LANG != "fr" else ""
    return (
        '<article class="partner-invite">'
        f'<div class="invite-icon" aria-hidden="true">{icon}</div>'
        f'<h4>{esc(title)}</h4><p>{esc(desc)}</p>'
        f'<a class="cta" href="https://loisirs74.fr{lang_prefix}/devenir-partenaire?lieu={attr(slug)}">'
        f'{T("become_partner")} {SVG_ARROW}</a>'
        '</article>'
    )

def _default_invites(d):
    """Venue-parameterized invite tiers when JSON has no partners block."""
    name = L("name", "")
    commune = d.get("commune", "")
    in_ = T("in_town")
    here = f"{in_} {commune}" if commune else ""
    q = T("qmark")
    return [
        {"tier":"invite","invite_type":"restaurant","i18n":{_LANG:{
            "title": f"{T('invite_resto_t')} {here}{q}".strip(),
            "desc":  f"{T('invite_resto_d')} {name} ? {T('invite_resto_d2')}"}}},
        {"tier":"invite","invite_type":"commerce","i18n":{_LANG:{
            "title": f"{T('invite_com_t')} {here}{q}".strip(),
            "desc":  f"{T('invite_com_d')} {name}."}}},
        {"tier":"invite","invite_type":"hebergement","i18n":{_LANG:{
            "title": f"{T('invite_hosp_t')}{q}".strip(),
            "desc":  f"{T('invite_hosp_d')} {here}.".strip()}}},
    ]

def partners_block(d):
    """Render the 'À proximité' section. Reads featured_businesses + partners; falls back to venue-parameterized invites."""
    slug = d["slug"]
    featured = d.get("featured_businesses") or []
    partners = d.get("partners") or []
    if not featured and not partners:
        partners = _default_invites(d)
    cards = []
    for p in featured + partners:
        tier = p.get("tier", "invite")
        if tier in ("partner", "recommended", "featured"):
            cards.append(_filled_partner_card(p))
        else:
            cards.append(_invite_card(p, slug))
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_partners")}</div>'
        f'<h2 class="reveal">{T("h_partners")}</h2>'
        f'<div class="partners reveal" data-stagger>{"".join(cards)}</div>'
        '</div></section>'
    )


def gallery_block(name, photos=None):
    """Real-photo tiles when `photos` provided (list of {src, alt, credit}); else 6 placeholders."""
    placeholder = (
        '<div class="tile placeholder"><svg viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" '
        'height="18" rx="2"/><circle cx="9" cy="9" r="2"/>'
        '<path d="M21 15l-5-5L5 21"/></svg></div>'
    )
    if photos:
        parts = []
        for p in photos:
            src = p.get("src", "")
            if not src:
                continue
            url = src if src.startswith(("http://", "https://", "/")) else f"/{src}"
            alt = p.get("alt") or name
            parts.append(
                f'<div class="tile"><img src="{attr(url)}" alt="{attr(alt)}" '
                'loading="lazy" width="600" height="600"></div>'
            )
        tiles = "".join(parts) if parts else placeholder * 6
    else:
        tiles = placeholder * 6
    return (
        '<section class="block"><div class="wrap">'
        f'<div class="kicker reveal">{T("k_photos")}</div>'
        f'<h2 class="reveal">{T("h_gallery")}</h2>'
        f'<div class="gallery reveal" data-stagger>{tiles}</div>'
        '<div class="gallery-invite reveal"><div class="icn">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
        '<circle cx="12" cy="13" r="4"/></svg></div>'
        f'<p><strong>{T("g_been_q")}</strong> {T("g_invite")} '
        f'<a href="mailto:photos@loisirs74.fr?subject={T("photos_subject")}{url_q(name)}">'
        'photos@loisirs74.fr</a></p></div></div></section>'
    )


def clean_eyebrow(badge, is_free):
    """Pick a clean eyebrow label (locale-aware)."""
    if badge:
        if "Pavillon Bleu" in badge:
            return badge
        if "Plage surveillée" in badge:
            return badge
        b = badge.strip()
        if b.upper().startswith("GRATUIT") or b.upper().startswith("FREE"):
            return T("free_dot")
        if len(b) <= 28 and "€" in b and not b.rstrip().endswith(("si", "i", ",", "·")):
            return (T("paid_prefix") if not is_free else "") + b
    return T("free_dot") if is_free else T("paid_dot")


def hero_block(d):
    """Render the hero section (locale-aware)."""
    name = L("name", "")
    hero = L("hero", {}) or {}
    badge = hero.get("badge", "") if isinstance(hero, dict) else ""
    lead = hero.get("lead", "") if isinstance(hero, dict) else ""
    alt = L("hero_alt", name)
    is_free = d.get("schema_org", {}).get("is_free", False)
    booking_url = d.get("booking_url") or d.get("official_site_url") or "#"
    official = d.get("official_site_url") or ""
    commune = d["commune"]
    q = url_q(f'{name}, {commune}, Haute-Savoie, France')

    GENERIC_ON_DISK = {"attraction", "cascade", "chateau", "domaine", "lac",
                       "musee", "parc", "point-de-vue", "sentier", "telecabine", "voie-verte"}
    img = d.get("hero_image") or ""
    if img.startswith("generique-"):
        img_src = f"/{img}"
        gen_cat = img[len("generique-"):].rsplit(".", 1)[0]
        gen_attr = f' data-generique="true" data-generique-cat="{gen_cat}"'
    elif img.startswith(("http://", "https://", "//", "/")):
        img_src = img
        gen_attr = ""
    elif img:
        img_src = f"/{img}"
        gen_attr = ""
    else:
        cat = d.get("category") or "attraction"
        eff_cat = cat if cat in GENERIC_ON_DISK else "attraction"
        img_src = f"/generique-{eff_cat}.jpg"
        gen_attr = f' data-generique="true" data-generique-cat="{eff_cat}"'

    eyebrow_text = clean_eyebrow(badge, is_free)
    cta_buttons = []
    if not is_free and booking_url and booking_url != "#":
        cta_buttons.append(
            f'<a href="{attr(booking_url)}" class="btn btn-primary" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M3 7v3a3 3 0 0 0 0 6v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a3 3 0 0 0 0-6V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/>'
            '<line x1="13" y1="5" x2="13" y2="7"/><line x1="13" y1="11" x2="13" y2="13"/>'
            f'<line x1="13" y1="17" x2="13" y2="19"/></svg>{T("book")}</a>'
        )
    cta_buttons.append(
        f'<a href="https://www.google.com/maps/search/?api=1&query={q}" class="btn btn-ghost" '
        'target="_blank" rel="noopener">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        f'<circle cx="12" cy="10" r="3"/></svg>{T("map_view")}</a>'
    )
    if official:
        cta_buttons.append(
            f'<a href="{attr(official)}" class="btn btn-ghost" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
            '<path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>'
            f'</svg>{T("official_site")}</a>'
        )

    return (
        '<section class="hero"><div class="wrap"><div class="grid">'
        '<div>'
        f'<span class="eyebrow reveal"><span class="dot"></span>{esc(eyebrow_text)}</span>'
        f'{hammer_h1(name)}'
        f'<p class="lede reveal">{esc(lead)}</p>'
        f'<div class="cta-row reveal">{"".join(cta_buttons)}</div>'
        '</div>'
        '<div class="reveal"><div class="hero-img">'
        f'<img src="{attr(img_src)}" alt="{attr(alt)}" width="1600" height="1200" '
        f'fetchpriority="high"{gen_attr}>'
        '</div></div>'
        '</div></div></section>'
    )


def action_bar(d):
    """Sticky bottom action bar (Book / Directions / Official site) — locale-aware."""
    name = L("name", "")
    commune = d["commune"]
    is_free = d.get("schema_org", {}).get("is_free", False)
    booking_url = d.get("booking_url") or d.get("official_site_url")
    official = d.get("official_site_url") or ""
    q = url_q(f'{name}, {commune}, Haute-Savoie')

    actions = []
    if not is_free and booking_url:
        actions.append(
            f'<a class="primary" href="{attr(booking_url)}" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M3 7v3a3 3 0 0 0 0 6v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a3 3 0 0 0 0-6V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/>'
            '<line x1="13" y1="5" x2="13" y2="7"/><line x1="13" y1="11" x2="13" y2="13"/>'
            f'<line x1="13" y1="17" x2="13" y2="19"/></svg><span>{T("book")}</span></a>'
        )
    actions.append(
        f'<a href="https://www.google.com/maps/dir/?api=1&destination={q}" '
        'target="_blank" rel="noopener">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        f'<circle cx="12" cy="10" r="3"/></svg><span>{T("directions")}</span></a>'
    )
    if official:
        actions.append(
            f'<a href="{attr(official)}" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
            '<path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>'
            f'</svg><span>{T("official_site")}</span></a>'
        )
    return (
        '<div class="action-bar" id="actionBar"><div class="wrap">'
        + "".join(actions)
        + '</div></div>'
    )


def build_ldjson(d):
    """Build the WebSite + BreadcrumbList + (TouristAttraction|Place) + FAQPage graph (locale-aware)."""
    slug = d["slug"]
    name = L("name", "")
    commune = d["commune"]
    lat = d.get("latitude")
    lon = d.get("longitude")
    postal = d.get("postal_code", "")
    sch = d.get("schema_org", {})
    is_free = sch.get("is_free", False)
    place_type = sch.get("type") or "TouristAttraction"
    amenities = L("schema_amenities", None) or sch.get("amenities") or []
    price = d.get("price_from")
    booking_url = d.get("booking_url") or d.get("official_site_url") or ""
    faq = L("faq", []) or []
    in_lang = CHROME["in_lang"][_LANG]
    lang_prefix = f"/{_LANG}" if _LANG != "fr" else ""

    page_url = f"{BASE_URL}{lang_prefix}/{slug}"
    site_url = f"{BASE_URL}{lang_prefix}/"
    graph = [
        {
            "@type": "WebSite",
            "@id": f"{BASE_URL}/#website",
            "url": site_url,
            "name": "Loisirs 74",
            "inLanguage": in_lang,
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{page_url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": T("home"), "item": site_url},
                (
                    {"@type": "ListItem", "position": 2,
                     "name": primary_hub(d, _LANG)[1],
                     "item": f"{BASE_URL}{lang_prefix}/{primary_hub(d, _LANG)[0]}/"}
                    if primary_hub(d, _LANG) else
                    {"@type": "ListItem", "position": 2, "name": commune,
                     "item": f"{BASE_URL}{lang_prefix}/#{commune.lower().replace(' ', '-')}"}
                ),
                {"@type": "ListItem", "position": 3, "name": name},
            ],
        },
    ]
    place = {
        "@type": place_type,
        "@id": f"{page_url}#place",
        "name": name,
        "alternateName": L("name_alternates", []),
        "description": L("meta_description", ""),
        "url": page_url,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": commune,
            "postalCode": str(postal),
            "addressRegion": "Haute-Savoie",
            "addressCountry": "FR",
        },
        "isAccessibleForFree": bool(is_free),
        "publicAccess": bool(sch.get("public_access", True)),
        "image": "",
    }
    if lat is not None and lon is not None:
        place["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon}
    if amenities:
        place["amenityFeature"] = [
            {"@type": "LocationFeatureSpecification", "name": str(a), "value": True}
            for a in amenities
        ]
    if not is_free and price is not None and price > 0:
        place["offers"] = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": d.get("price_currency", "EUR"),
            "url": booking_url or page_url,
        }
    graph.append(place)

    if faq:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{page_url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q.get("q", ""),
                 "acceptedAnswer": {"@type": "Answer", "text": q.get("a", "")}}
                for q in faq
            ],
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def build_head(d):
    """Render the <head> section (locale-aware)."""
    slug = d["slug"]
    name = L("name", "")
    title = L("meta_title", "") or f"{name} · Loisirs 74"
    desc = L("meta_description", "")
    lat = d.get("latitude") or 0
    lon = d.get("longitude") or 0
    commune = d["commune"]
    lang_prefix = f"/{_LANG}" if _LANG != "fr" else ""
    page_url = f"{BASE_URL}{lang_prefix}/{slug}"
    fr_url = f"{BASE_URL}/{slug}"
    html_lang = CHROME["html_lang"][_LANG]
    og_loc = CHROME["og_locale"][_LANG]

    # Emit the full 6-lang hreflang cluster. Pages for all locales are
    # produced for every fiche by build_all_locales (with FR-fallback content
    # when a lang block is absent), so the cluster matches what's on disk.
    hreflang_lines = [f'<link rel="alternate" hreflang="fr" href="{fr_url}">']
    for lg in ("en", "de", "it", "es", "nl"):
        hreflang_lines.append(f'<link rel="alternate" hreflang="{lg}" href="{BASE_URL}/{lg}/{slug}">')
    hreflang_lines.append(f'<link rel="alternate" hreflang="x-default" href="{fr_url}">')
    hreflang_block = "\n".join(hreflang_lines)

    # Localize CSS "Générique" overlay
    css = CSS.replace('content: "Générique"', f'content: "{T("generic")}"')

    ldjson = build_ldjson(d)
    hero_alt = L("hero_alt", name)

    return f"""<!doctype html>
<html lang="{html_lang}" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0b0d10" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#fafaf7" media="(prefers-color-scheme: light)">
<title>{esc(title)}</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1c4f62">
<meta name="description" content="{attr(desc)}">
<link rel="canonical" href="{page_url}">
{hreflang_block}
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:type" content="article">
<meta property="og:title" content="{attr(name)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:url" content="{page_url}">
<meta property="og:locale" content="{og_loc}">
<meta property="og:site_name" content="Loisirs 74">
<meta property="og:image:alt" content="{attr(hero_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{attr(name)}">
<meta name="twitter:description" content="{attr(desc)}">
<meta name="geo.region" content="FR-74">
<meta name="geo.placename" content="{attr(commune)}">
<meta name="geo.position" content="{lat};{lon}">
<meta name="ICBM" content="{lat}, {lon}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230a5a3a'/%3E%3Cpath d='M16 44 L26 28 L34 38 L44 22 L48 44 Z' fill='%23fafaf7'/%3E%3C/svg%3E">
<style>{css}</style>
<script type="application/ld+json">{ldjson}</script>
<meta property="og:image" content="{BASE_URL}/og-image.jpg">
<meta name="twitter:image" content="{BASE_URL}/og-image.jpg">
<!-- AI discovery: per-lieu markdown mirror -->
<link rel="alternate" type="text/markdown" href="/content/{slug}.md" title="Markdown version">
<meta name="ai:content-url" content="{BASE_URL}/content/{slug}.md">
<meta name="ai:policy-url" content="{BASE_URL}/.well-known/ai-info.json">
</head>"""


def build_header(d):
    """Sticky site header with brand + lang picker (locale-aware)."""
    slug = d["slug"]
    lang_prefix = f"/{_LANG}" if _LANG != "fr" else ""
    site_url = f"{BASE_URL}{lang_prefix}/"
    hub = primary_hub(d, _LANG)
    if hub:
        hub_slug, hub_label = hub
        crumb_mid = f'<a href="{BASE_URL}{lang_prefix}/{hub_slug}/">{esc(hub_label)}</a>'
    else:
        crumb_mid = f'<span>{esc(d["commune"])}</span>'

    # Lang picker: full 6-lang menu. Current locale gets aria-current.
    pick_links = []
    for lg in ("fr", "en", "de", "it", "es", "nl"):
        prefix = f"/{lg}" if lg != "fr" else ""
        href = f"{BASE_URL}{prefix}/{slug}"
        cur = ' aria-current="true"' if lg == _LANG else ''
        pick_links.append(f'<a href="{href}"{cur} hreflang="{lg}">{CHROME["lang_native"][lg]}</a>')
    pick_html = "\n".join(pick_links)
    name = L("name", "")

    return f"""<body>
<a class="skip" href="#main">{T("skip")}</a>
<header class="site"><div class="wrap">
  <a class="brand" href="{site_url}" aria-label="Loisirs 74"><span class="mark" aria-hidden="true"><img src="/logo.png" alt="" width="30" height="30" style="border-radius:7px;display:block;"></span><span>Loisirs 74</span></a>
  <nav><details class="lang-picker"><summary aria-label="{T("lang_choose")}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20"/></svg>{T("lang_label")}</summary><div class="lang-menu">{pick_html}</div></details></nav>
</div></header>
<main id="main">
<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="{site_url}">{T("home")}</a><span class="sep">/</span>{crumb_mid}<span class="sep">/</span><span aria-current="page">{esc(name)}</span></nav></div>"""


def build_footer_block(date_pub, date_mod):
    return (
        '<div class="wrap"><p class="meta">'
        f'<span>{T("published")} {esc(date_pub)}</span><span class="sep">·</span>'
        f'<span>{T("updated")} {esc(date_mod)}</span></p></div>'
        '</main>'
    )


def site_footer():
    """Locale-aware <footer class='site'>. URLs prefixed by current locale."""
    lp = f"/{_LANG}" if _LANG != "fr" else ""
    return (
        '<footer class="site"><div class="wrap"><div class="foot-grid">'
        f'<div class="foot-col"><a class="brand" href="{BASE_URL}{lp}/" style="margin-bottom:.85rem"><span class="mark" aria-hidden="true"><img src="/logo.png" alt="" width="30" height="30" style="border-radius:7px;display:block;"></span><span>Loisirs 74</span></a><p>{T("f_tagline")}</p></div>'
        f'<div class="foot-col"><h4>{T("f_explore")}</h4><ul><li><a href="{BASE_URL}{lp}/">{T("home")}</a></li></ul></div>'
        f'<div class="foot-col"><h4>{T("f_contribute")}</h4><ul><li><a href="mailto:photos@loisirs74.fr">{T("f_send_photos")}</a></li><li><a href="{BASE_URL}{lp}/signaler">{T("f_report")}</a></li><li><a href="{BASE_URL}{lp}/devenir-partenaire">{T("f_become_p")}</a></li></ul></div>'
        f'<div class="foot-col"><h4>{T("f_legal")}</h4><ul><li><a href="{BASE_URL}{lp}/mentions-legales">{T("f_legal_link")}</a></li><li><a href="{BASE_URL}{lp}/confidentialite">{T("f_privacy")}</a></li><li><a href="{BASE_URL}{lp}/cgv">{T("f_cgv")}</a></li></ul></div>'
        f'</div><div class="foot-bottom"><span class="credit">{T("f_copyright")}</span><span>{T("f_promise")}</span></div></div></footer>'
    )


LAST_FALLBACK_FIELDS = set()  # populated by build_page() for callers wanting coverage info


def build_page(d, lang="fr"):
    """Render the full HTML for fiche `d` in `lang`. Returns html string.
    Fallback-field info (which keys fell back to FR) is exposed via
    module attribute LAST_FALLBACK_FIELDS after each call."""
    global LAST_FALLBACK_FIELDS
    _set_lang(d, lang)
    name = L("name", "")

    out = []
    out.append(build_head(d))
    out.append(build_header(d))
    out.append(hero_block(d))
    out.append(facts_block(L("facts", {}) or {}))
    body_dict = L("body", {}) if isinstance(L("body", {}), dict) else {}
    if not body_dict:
        body_dict = {"what_is": L_body("what_is", "")}
    out.append(body_block(name, body_dict))
    out.append(activities_block(L_body("activities", []) or []))
    out.append(practical_block(L_body("practical_info", []) or [], name, d["commune"]))
    out.append(how_to_block(L_body("how_to_get_there", {}) or {}, name, d["commune"]))
    out.append(when_to_visit_block(L_body("when_to_visit", "") or "",
                                   L_body("events", "") or ""))
    out.append(partners_block(d))
    out.append(gallery_block(name, d.get("gallery_photos")))
    out.append(faq_block(L("faq", []) or []))
    out.append(sources_block(d.get("sources", [])))
    out.append(data_credits_block(d.get("data_sources", [])))
    out.append(build_footer_block(
        d.get("date_published_human", ""),
        d.get("date_modified_human", "")
    ))
    out.append(action_bar(d))
    out.append(site_footer())
    out.append(JS)
    out.append("</body></html>")
    LAST_FALLBACK_FIELDS = set(_FALLBACK_FIELDS)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--lang", default="fr", choices=SUPPORTED_LANGS)
    ap.add_argument("--out-dir", default=None,
                    help="Output dir. Defaults to REPO for fr, REPO/<lang> otherwise.")
    args = ap.parse_args()

    d = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    html = build_page(d, lang=args.lang)
    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO if args.lang == "fr" else REPO / args.lang
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{d['slug']}.html"
    out_path.write_text(html, encoding="utf-8")
    try:
        rel = out_path.relative_to(REPO)
    except ValueError:
        rel = out_path
    fb = f" [fallback:{','.join(sorted(LAST_FALLBACK_FIELDS))}]" if LAST_FALLBACK_FIELDS else ""
    print(f"  {rel}  ({len(html):,} chars){fb}")


if __name__ == "__main__":
    main()
