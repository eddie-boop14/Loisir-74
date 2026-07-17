# HANDOFF — session close (stations Waves 1-2 + JOB B winter apply)

**Attested at close:** HEAD `daa85c41` (= `main`, tree clean, branch `claude/new-session-eua199`) ·
418 fiches · **19 stations ×12 langs** · 99 winter nodes, **27 carrying applied values** ·
winter-candidates **32/53 confirmed** · 10 IndexNow pings logged (last: 120 URLs, HTTP 200).
**Code re-attests before acting on anything below.**

## SHIPPED this session (all live on loisirs74.fr)
1. **Stations Wave-1 (9)** — new `station` category + `stations-de-ski` hub (12 locales):
   La Clusaz, Le Grand-Bornand, Manigod, Chamonix-Mont-Blanc, Megève, Les Gets, Morzine,
   Avoriaz, Flaine. 120 URLs → IndexNow 200.
2. **Stations Wave-2 (10)** — Saint-Gervais-les-Bains, Les Contamines-Montjoie, Combloux,
   Samoëns, Les Carroz, Morillon, Châtel, Saint-Jean-d'Aulps, Praz de Lys–Sommand,
   La Chapelle-d'Abondance. Hub = 19 cards. 120 URLs → IndexNow 200.
3. **JOB B winter apply** — 33 verified winter-fact rows applied via new
   `scripts/apply_winter_facts.py` (--report → Eddie ⚑ → --apply); **inforoute74 escape
   hatch** built (season_card fr/en + facet md + facet JSON `inforoute`;
   `gate_winter_schema` rule 4b enforces). Colombière = Fermé + inforoute74;
   Montenvers = Panorama alpin (NOT Mont-Blanc). Protected placements byte-identical.

## STANDING LAWS (unchanged, non-negotiable)
- Official sources only; prices null until verified; nulls stay honest; flags carried into
  `verify_flags`; domain totals attributed to the DOMAINE, never the village.
- Frozen FR names verbatim in all 12 langs. Partner carrying pages **byte-frozen —
  PROTECT AT ALL COSTS** (`gate_protected_placements`).
- IndexNow is hand-fired only (`indexnow_ping.py --send`), never cron.
- Dedupe before authoring: le-semnoz stayed point-de-vue; Le Salève + Sixt skipped as
  stations for the same reason.

## QUEUED (Eddie's call, in rough rank order)
1. **Stations Wave-3 (small/Léman)** — Bernex, Thollon-les-Mémises, Hirmentaz-Les Habères,
   Mont-Saxonnex, Le Reposoir… Pipeline is proven; specs + exemplar live in the session
   scratchpad pattern (re-create from `Json/la-clusaz.json` as exemplar if scratchpad gone).
2. **Winter Stage-3 verified pass** — the 21 unconfirmed candidates stay null by design
   (Morzine/Châtel set, mont-joly, parmelan, veyrier/baron/miribel/loex sightlines,
   inforoute-dependent statuses). Needs a fresh official-source verification payload;
   apply with the SAME `apply_winter_facts.py` (payload format is reusable).
3. **Optional freshness re-ping** — 33 winter fiches changed content (≈396 URLs if pinged
   ×12). Not required by JOB B; hand-fire if wanted.
4. **Station photos** — all 19 stations ride generic heroes (`generique-ski-*` etc.);
   an Eddie photo batch or Wikimedia pass would upgrade them (`pick_generique.py` owns heroes).
5. **stations-de-ski hub prose** — FR catcher exists; hub-intro + FAQ prose (like the other
   category hubs) was deliberately deferred at bootstrap.
6. **`station` category winter card** — `station` ∉ WINTER_NODES (deliberate: no ski_alpin
   key in the vocab). Extending the node set = a separate Eddie decision (JOB B §5).
7. **google_check lane** — every new station fiche has `google_check.checked: null`
   ("à exécuter par la lane google_check").

## OPERATIONAL LESSONS (cost real work this session)
- **Container reclaim wiped a full uncommitted pass** (Wave-1, ~2h of agents). Rule now:
  **commit + push the FR-source checkpoint BEFORE any long translation wait.** Wave-2 hit
  a session limit mid-run and lost nothing because of this.
- Translation agents: **split 11 langs into halves** (en/de/it/es/nl/pl + pt/cs/ar/he/ja) —
  a single agent hits the 64k output cap.
- Validator idioms: number-preservation check must be separator/script-tolerant and allow
  decade/"100%" idioms (`scratchpad/splice_stations.py` pattern, `DECADE_OK`).
- `build_all.py` + full gate battery ≈ >2 min: run gates in a separate command or raise the
  Bash timeout.

## KEY TOOLING (all in repo, reusable)
`scripts/apply_winter_facts.py` (payload applier, --report/--apply) ·
`scripts/indexnow_ping.py` (hand-fired) · gate battery = 26 CI gates
(`.github/workflows/build-gate.yml`) + `gate_i18n_leak` + `gate_i18n_labels` +
`check_reachability` → the "28 green" bar · deploy-poll + IndexNow pattern:
`scratchpad/deploy_indexnow_w2.sh` shape (poll 200 ×3 probes → --send → commit log).

*North star unchanged: every line carries its source; the Département stays the live
referee; nulls are honest until a verified pass fills them.*

**© 2026 · Bleu canard édition · Edmaster & Claudius · Tous droits réservés 🦆**
