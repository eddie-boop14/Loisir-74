# Remote branch cleanup — merged-and-safe list for one-tap deletion

**Attested**: 2026-07-03, after `git fetch --all --prune` against origin @ main `cb95b51`
(post-#33 merge). 40 remote branches besides `main`. `claude/pl-prose-batch1` is
**already gone** (deleted days ago — confirmed absent from the remote).

**Nothing was deleted by this task.** Every verdict below is evidence-based;
the evidence type is stated per group. Deletion is Edmaster's tap.

## ✅ SAFE — tip reachable from main (proven merged, 21 branches)

`git branch -r --merged origin/main`: every commit on these branches is in main.

| branch | last commit | landed as |
|---|---|---|
| claude/i18n-pilot | 2026-06-29 | content merged (PR #11 closed; tip reachable) |
| claude/i18n-verify-pt | 2026-06-29 | PR #9 |
| claude/duck-cache-bust | 2026-06-30 | PR #17 |
| claude/i18n-cs-pilot | 2026-06-30 | PR #14 |
| claude/i18n-locale-roster | 2026-06-30 | PR #16 |
| claude/i18n-pilot-indexable | 2026-06-30 | PR #15 |
| claude/i18n-router-arhe | 2026-06-30 | PR #13 |
| claude/i18n-verify-cs | 2026-06-30 | PR #10 |
| claude/ja-pipeline | 2026-06-30 | PR #19 |
| claude/publish-pl-fulltree | 2026-06-30 | PR #21 |
| claude/render-verify-gate | 2026-06-30 | PR #20 |
| claude/rtl-engine-phase-c | 2026-06-30 | PR #18 |
| claude/handoff-15-leftovers | 2026-07-01 | PR #27 |
| claude/handoff-23-raw-emit | 2026-07-01 | PR #26 |
| claude/new-session-u0n5va | 2026-07-01 | PR #25 |
| claude/close-pt | 2026-07-02 | PR #30 |
| claude/fix-batch-custom-id | 2026-07-02 | PR #28 |
| claude/one-standard | 2026-07-02 | PR #31 |
| claude/pt-prose-batch | 2026-07-02 | PR #29 |
| claude/indexnow | 2026-07-03 | PR #33 |
| claude/meta-uniqueness | 2026-07-03 | PR #32 |

## ✅ SAFE — rebase/squash-merged PRs, content patch-equivalent in main (3)

Tips not reachable (rebase-merge), but each branch's single unique commit is
patch-equivalent in main (`git cherry`) AND its PR is MERGED on GitHub.

| branch | last commit | landed as |
|---|---|---|
| claude/lane-isolation-gate | 2026-06-30 | PR #22 |
| claude/publish-langs-visible-nav | 2026-06-30 | PR #23 |
| claude/rich-prose-lang-infra | 2026-06-30 | PR #24 |

## ✅ SAFE — GitHub says MERGED; history since rebuilt (1)

| branch | last commit | landed as |
|---|---|---|
| claude/apply-source-audit | 2026-06-18 | PR #8, MERGED 2026-06-22 |

Its commits are no longer patch-equivalent because main's history was rebuilt
after late June, but GitHub's merge record is the proof.

## ⚠️ SAFE-BY-ARTIFACT — the June stack (13): features verifiably in main, but these branches are the only archive of that history

Stacked working branches from 2026-06-21→26, no PRs on record, commits not
patch-equivalent (same history-rebuild as above). For each, the signature
artifact EXISTS in today's main (spot-checked 2026-07-03):

| branch | proof in main |
|---|---|
| fix/canonical-sitewide | `scripts/gate_canonical_selfref.py` in CI |
| fix/sorties-detente-fullfix | `CURATED_SORTIES` in build_hubs.py |
| feat/sorties-homepage-polish | HUB_DISPLAY-sourced h1 in build_hubs.py |
| feat/nl-batch1-gorges | Pont du Diable nl `what_is` present in Json |
| feat/pont-du-diable-i18n-bodies | Pont du Diable de/it/es/nl bodies in Json |
| feat/pont-du-diable-publish | `Json/gorges-du-pont-du-diable.json` published |
| feat/sorties-detente-batch2 | artisan fiches in Json (draft, as designed) |
| fix/dedupe-roselieres | 6 roselières 301s in `_redirects` |
| fix/key-drop-allowlist-body-flag | superseded — key-drop gate evolved past `_body_flag` |
| feat/builder-audit | `scripts/gate_venue_centroid.py` in CI |
| feat/geo-backfill | `scripts/gate_geo_verified.py` in CI |
| fix/clear-wrong-place-ids | geo-verified pipeline in CI |
| fix/geolocation-restore | `scripts/nearme.js` + homepage include |

Verdict: **deletable** — main carries everything they produced. But because the
history rebuild orphaned their commits, deleting them erases the last archive
of the pre-rebuild June history. If you want the archaeology, tag one
(`git tag archive/june-stack fix/geolocation-restore` holds the whole stack —
it contains all 13 as ancestors) before tapping delete.

## ✋ KEEP / YOUR CALL (2)

| branch | why |
|---|---|
| claude/redirects-fix | **KEEP** — open PR #34 (the /contact redirect fix) |
| claude/overnight-report | your call — 1 commit (the 2026-06-29 overnight PR-map report), PR #12 closed WITHOUT merging; the only branch on the remote holding a commit that is nowhere else. Delete if that report is no longer wanted. |

## Tally

- One-tap safe now: **25** (21 + 3 + 1)
- Safe-by-artifact (optionally tag first): **13**
- Keep: **1** (open PR) · Your call: **1** (unmerged docs report)
- Already gone: `claude/pl-prose-batch1` ✓
