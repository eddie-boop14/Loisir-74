# Translation cost reconciliation — HANDOFF-35 Job B

**STATUS: PRE-AUDIT.** This file holds what code inspection alone could prove.
The line-item actuals come from the paid batches' own per-request usage and
require one click: **Actions → Translate loisirs74 → mode = `audit`** ($0 —
results retrieval is free, nothing is submitted). That run OVERWRITES this
file with the full reconciliation and writes the estimator calibration.

## The symptom

Contract said **$7.61/lang** (pt and cs dry-runs, byte-identical local and CI).
Actuals ≈ **$19/lang**: credit went 20.26 → ~20.00 → 2.30 across the two runs,
≈ $38 for two languages — ~2.5× the contract.

## Audit checklist (handoff order) — what's already proven

### 1. Endpoint — ✓ NOT the leak
`scripts/translate_batch.py` submits via `client.messages.batches.create`
(`POST /v1/messages/batches`) — the Message Batches API, 50% discount applies.
The script's constants ($1.50 in / $7.50 out per MTok) match claude-sonnet-4-6
batch pricing. The Console usage line will confirm batch pricing on the audit.

### 2. Prompt caching — ✗ CONFIRMED LEAK (small)
The shared system prompt carries `cache_control: {type: ephemeral}` — but it
is **~2,719 chars ≈ 780 tokens, below claude-sonnet-4-6's 2048-token minimum
cacheable prefix**. Below that minimum the marker is *silently ignored*: no
error, no cache entry, and every one of the 389 requests re-billed the system
block as plain input. The old `estimate()` priced 388/389 requests' system
block at 0.1× (cache read). Magnitude: ≈ +$0.40/lang — real, but nowhere near
the $11/lang gap. The audit's cache-read column (expected ≈ 0) is the proof.

### 3. Retries — known, quantifiable
- pt: retry round of 2 requests (tag-parity failures) — negligible.
- cs: retry round of **+153 requests ≈ +$3.00** — outside the contract, now
  reported separately by the audit and GATED in code (see rule below).

### 4. Output reality vs estimate — PRIME SUSPECT, audit measures it
The old model assumed `out ≈ in` at chars/3.5. Output is billed at $7.50/MTok
— **5× the input rate** — so any under-count here dominates the bill.
Back-computing from the ~$19/lang actuals: output must have run ≈ 2–3× the
assumption (Czech/Portuguese tokenize worse per char than English, translations
run longer than source, and any thinking tokens bill as output). The audit sums
the real `output_tokens` per request and derives the measured
tokens-per-source-char factor per language — that closes the delta to the cent.

## Fixes already live in this PR

1. **`estimate()` corrected**: system block priced *uncached* below the
   2048-token minimum; per-language output factors (audit-calibrated when
   `reports/translate-cost-calibration.json` exists, deliberately-high
   documented defaults until then); input factor calibrated the same way.
2. **The meter**: every run now records per-batch actual usage + $ in the
   state file and prints `METER` reconciliation lines (main batch, retry
   batch, final vs contract).
3. **Permanent >15% rule**: the dry-run is a contract —
   - before the retry submit: projected total > 1.15× contract → the retry is
     **SKIPPED**, the run exits red (code 2), fields stay absent (recoverable);
   - final total > 1.15× contract → run exits red (code 3) with the paid
     results still written and pushed (`always()` push step).
4. **`--audit` mode + workflow mode `audit`**: $0 reconciliation of every paid
   batch (state-file ids + `batches.list()`, which also catches the pt retry
   batch whose id predates id-persistence), writing this report + calibration.

## Gate for the next language

No `go ja` until:
1. Eddie's `audit` click has replaced this file with line-item actuals and the
   pt/cs delta is explained to the cent;
2. a fresh `dry-run` (now calibration-backed) prints a ja contract we can
   defend within ±15% — enforced mid-run by the abort rule either way.
