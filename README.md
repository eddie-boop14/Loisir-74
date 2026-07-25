Loisirs 74
An independent leisure guide for Haute-Savoie, France — 426 places, 12 languages,
6 026 static pages, every fact traced to an official source.
🌐 loisirs74.fr
Lakes, waterfalls, viewpoints, ski resorts, cable cars, castles, museums, greenways. No
aggregator data, no scraped reviews, no invented opening hours.
The rule everything else follows
JSON is the source of truth. The build derives everything else.
Nothing in the rendered site is written by hand. A wrong comma on a page is fixed in
Json/<slug>.json or in a builder script, then re-rendered — never patched in the HTML.
The same rule governs the guide's honesty: if a fact cannot be verified against an official
source, it stays null and is flagged. Never guessed, never inferred, never filled from a
reseller. A missing opening time is a gap. A wrong one sends someone to a locked door.
What a place page carries
GPS · opening hours · price tiers · free/paid · parking · public transport · accessibility (PMR)
· dog policy · best season · winter access · on-site activities · FAQ — with a French canonical
and hreflang alternates across all twelve locales.
Sources: communes, offices de tourisme, ONF, IGN, FFRandonnée, Natura 2000, DATAtourisme,
data.gouv.fr, OpenStreetMap, Wikimedia Commons. Tripadvisor, GetYourGuide, Visorando and blogs
are not valid sources and never enter the corpus.
French place names are frozen verbatim in every language — Lac d'Annecy, Léman,
Mont-Blanc, Aiguille du Midi, Haute-Savoie, ViaRhôna, GR®, and all commune names.
Twelve languages, two render modes
mode
locales
what ships
prose
fr en de it es nl
full editorial text, FAQ, activities
facts-first
pl pt cs ar he ja
verified facts, no generated prose
French is canonical at the repo root; the other eleven render into <lang>/. ar and he ship
RTL.
The roster lives in data/languages.json and is derived through scripts/locales.py.
Never hardcode the locale count — a CI gate fails the build if you do.
Pages are queries, not documents
Beyond the 426 place pages, the site renders a compiled layer where membership is computed,
never hand-listed:
16 intent pages — Lac d'Annecy en famille, Quand il pleut à Annecy,
Canicule : où trouver la fraîcheur, Léman côté français … each defined by a deterministic
predicate over the corpus in data/intent-registry.json
8 facet hubs — parking, transport, PMR access, free entry, winter
~16 thematic and ~22 commune hubs
Add a place, and every page it qualifies for updates on the next build. No editor maintains a
list. Each compiled page renders its own selection criteria, so a reader can see why something
is on it.
Build
Bash
Flat static output. No server, no database, no client-side data fetching — pages are complete
HTML before a browser ever asks. Deployed on Netlify.
Every push to main runs a CI build gate: schema, hygiene, full render, locale completeness,
i18n leak detection, reachability, protected-asset guards, and a byte-stable double build —
two consecutive builds must produce identical output. 32 gates in scripts/gate_*.py, 8
workflows in .github/workflows/.
Two safety rails apply to every automated job: any write touching more than 10 % of the corpus
aborts with zero writes, and an API failure is recorded as CHECK_FAILED — never as
CONFIRMED_ABSENT. An error is not data.
Layout
Code
Contributing
Spotted a wrong detail? Use Signaler une info on any page, or open an issue. Corrections to
verified facts need a source link — commune, office de tourisme, or operator.
Partner enquiries: Devenir partenaire.
Editing through the Studio toolkit? Output enters the repo only as a dotted-path patch via
scripts/apply_studio_patch.py. Never drop a whole <slug>.json into Json/ — see the Studio
ingress rule in ARCHITECTURE.md.
Status
Active development on main. Treat the live repo as truth over any document, including this
one. Numbers here were verified at the commit that introduced them and drift is the normal
state of a growing catalogue.
Full pipeline, scheduled refresh agents and Studio internals: ARCHITECTURE.md.
Licence
Site content © Bleu canard édition. Open data sources keep their own licences — DATAtourisme
under Etalab Open License, photography credited per photo-credits.json, Wikimedia Commons per
each file's terms.
2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés 🦆