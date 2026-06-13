DROP FOLDER for user-sourced générique pictures.

Drop CC0 / public-domain JPGs here using this filename pattern:
  {bucket}__cc0_{source-slug}.jpg

Examples:
  padel__cc0_pexels-12345.jpg
  plage__cc0_unsplash-john-doe.jpg
  via-ferrata__cc0_pixabay-9876.jpg

The double underscore (__) separates the bucket name from the provenance.
A later session will:
  1. Resize to 1600x1200 (4:3 landscape)
  2. Optimize to <300 KB at quality 78
  3. Rename to generique-{bucket}.jpg
  4. Write photo-credits.json entry from filename provenance
  5. Update scripts/pick_generique.py to route fiches in this bucket to it
  6. Re-run picker + build

This folder is excluded from the published _site/ via DENY_GLOB
in scripts/build_site.py.
