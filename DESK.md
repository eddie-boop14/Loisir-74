# The owner's desk

The desk is one private page (a claude.ai Artifact) where the owner taps answers,
pastes map pins and drops photos and saved pages. The page stores them in its own
database. Nothing changes on the site until Claude applies them and the owner says
"merge".

Desk: https://claude.ai/artifact/KRyfM9V667poXunmUwQdu8

## Rulings (the owner's words, dated: apply them without asking again)

- **7 Nov 2026, pins:** "I want real pin not from some random coords from a api."
  A pin is a Google Maps link the owner placed and checked himself: a share link
  (`maps.app.goo.gl`), a `/maps/place/` URL or a `?cid=` link. A name search never
  counts. The 271 Google place ids from the automated Places sweep are not pins.
- **7 Nov 2026, live links until pinned:** option 1. A place without his pin
  keeps its current map links. His pin replaces them place by place.
- **7 Nov 2026, discovery distances:** distances are between attractions, never
  from the visitor ("À 12 km d'ici…").
- **Standing rule:** only the owner's word changes a status, and Claude never
  approves its own work. Every change goes to the branch and waits for "merge".

## Card ids (stable: applying twice changes nothing)

| Card | Where it lives | What applying does |
|---|---|---|
| `pin:<slug>` | `answers` | `scripts/desk_apply.py` writes `data/pins.json` (guards in the script) |
| `call:<slug>` | `answers` | recorded in `data/desk-calls.json`; never unpublishes anything by itself |
| `photo:<slug>:<ts>` | `inbox` | Claude places the photos (hero or gallery) with the given credit |
| `save:<ts>` | `inbox` | a saved `.mht` page: Claude reads it, matched by the address saved inside the file, never by its name |
| `note:<ts>` | `inbox` | the owner's words: Claude acts on them and replies on the item |

## "Apply the desk": the run, in order

1. Resync the branch to `main`.
2. Save the answers: ArtifactData `list` of `answers` with `out_dir`, and of `inbox`.
3. `python3 scripts/desk_apply.py --answers <dir>/answers --report <dir>/report.json`
   (dry run), read the report, then run it again with `--apply`.
4. Handle the inbox items: photos, saved pages, notes.
5. Full build (`scripts/build_all.py --no-site`) and gates. Commit, push the branch.
6. `python3 scripts/desk_export.py --out <desk folder>/items.json` and republish
   the desk with that file.
7. Mark each card: `answers` documents get `applied_on` / `refused_why` from the
   report, inbox items get `status: "applied"` and a one-line `reply`.
8. Report in chat: what moved, what was refused and why, what waits for "merge".
