BIG PATCH 2026-05-14
═══════════════════════════════════════════════════════════════

Contents:

1. Json/         — 85 lieu JSONs
                   (merge of all 76 from this session + extras from your /Json/)
                   Upload this folder to GitHub root, REPLACES your /Json/

2. Root HTMLs   — 71 files
   de/ en/ es/ it/ — lang variants
   
   These patches do TWO things:
   - For lieux with photos in your repo: hero <img> now points to /<slug>-hero.jpg
   - For lieux with broken Wikimedia URLs: hero <img> src cleared (renders as
     a neutral gray placeholder via CSS, no broken-image icon)

WHY: Site was showing broken Wikimedia photos because:
  - Many fallback URLs in studio returned 404 or wrong photos
  - Same Cascade d'Arpenaz photo was loading on Doran, Diomaz, etc.
  - Result: a forest of broken image icons across the site

NEXT STEPS:
  1. Unzip this patch
  2. Drag the Json/ folder into your GitHub /Json/ (replaces all)
  3. Drag the root *.html files + de/, en/, es/, it/ folders into root
  4. Commit
  5. Netlify rebuilds → broken images gone
