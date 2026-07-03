#!/usr/bin/env python3
"""translate_batch.py — HANDOFF-25: the 21M-char prose job at ~1/20th the cost.

Translates every fiche's EN prose into the facts-first languages
(pl/pt/cs/ja/ar/he) through the Anthropic Message Batches API — 50% off
input AND output vs interactive, ~2,382 requests total, machine-validated
on arrival, written back into Json/<slug>.json under i18n.<lang>.

    ONE language at a time, in sequence:  pl → pt → cs → ja → ar → he
    Each: assemble → (dry-run gate) → submit → poll → validate → write.

USAGE (manual only — NEVER a cron; 2026-07-01's lesson):
    python3 scripts/translate_batch.py --lang pl --dry-run   # count + cost, no submit
    python3 scripts/translate_batch.py --lang pl             # run one language
    python3 scripts/translate_batch.py --lang all            # whole job, language by language
    python3 scripts/translate_batch.py --lang pl --force     # redo already-populated fiches

NEEDS: ANTHROPIC_API_KEY in the environment (Eddie's Anthropic Platform
key — NOT the Google one). Model: claude-sonnet-4-6 (per HANDOFF-25).
Batch pricing $1.50/$7.50 per MTok; the shared instruction block (rules +
frozen-noun glossary) is prompt-cached across all requests in a batch.

RESUMABLE + IDEMPOTENT:
  * a submitted batch id is remembered in reports/translate-batch-state.json —
    re-running resumes polling instead of resubmitting;
  * fiche×lang pairs whose prose fields are already populated are skipped
    (use --force to redo);
  * failed results are auto-retried ONCE in a follow-up batch; still-failing
    pairs are logged to reports/translate-batch-failures.md and the fields
    stay ABSENT (null discipline — never a bad write).

EVERY result is validated before write-back (the standard-keeper):
  1. JSON parses + KEY PARITY with the EN source (no missing, no invented);
  2. FROZEN NOUNS verbatim (core glossary + every commune + the fiche's
     frozen FR name — any term present in the source must survive untouched);
  3. HTML STRUCTURE parity (same tag multiset as source; no &lt;escaped&gt;
     tags — feeds HANDOFF-23's raw-emit correctly);
  4. length ratio 0.4–2.5× source; no empty string where source non-empty.

After a language lands, render + gate it (separate steps, printed as a
reminder): build_fulltree_lang / build_lieu_page rich render (HANDOFF-22),
gate_render_verified sample, the no-escaped-tags check, then ship.
Protected fiches are data-carrying like any other — their placement blocks
are untouched (we only ADD i18n.<lang> prose fields).
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "Json"
STATE_FILE = ROOT / "reports" / "translate-batch-state.json"
FAILURES_MD = ROOT / "reports" / "translate-batch-failures.md"

MODEL = "claude-sonnet-4-6"          # per HANDOFF-25 — do not silently upgrade
MAX_TOKENS = 16000
BATCH_IN_PER_MTOK = 1.50             # $ per MTok, batch (50% off $3.00)
BATCH_OUT_PER_MTOK = 7.50            # $ per MTok, batch (50% off $15.00)

TARGET_LANGS = ["pl", "pt", "cs", "ja", "ar", "he"]
RTL_LANGS = {"ar", "he"}
LANG_NAMES = {"pl": "Polish", "pt": "Portuguese", "cs": "Czech",
              "ja": "Japanese", "ar": "Arabic", "he": "Hebrew"}

# The prose fields (HANDOFF-25 / HANDOFF-22). `hero` is trimmed to `lead`,
# `body` to `what_is`; facts / name / name_alternates / schema_amenities are
# NOT prose and never travel.
PROSE_FIELDS = ["meta_title", "meta_description", "hero", "hero_alt", "body",
                "activities", "practical_info", "how_to_get_there",
                "when_to_visit", "events", "faq"]

# Core frozen nouns — stay VERBATIM untranslated in every language.
# Communes + each fiche's frozen FR name are added programmatically.
CORE_FROZEN = ["Lac d'Annecy", "Léman", "Mont-Blanc", "Aiguille du Midi",
               "Haute-Savoie", "ViaRhôna", "GR®", "Faucigny"]

TAG_RE = re.compile(r"<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)")

# Batches API constraint on custom_id: ^[a-zA-Z0-9_-]{1,64}$
# The original "<slug>:<lang>" form violated it twice (illegal ':' + slugs up
# to 73 chars) — run #2 got a 400 BEFORE the batch was created ($0 spent).
# Uniqueness now comes from the per-batch index; the slug fragment is for
# humans reading logs. The authoritative custom_id → slug mapping travels in
# the state file so a resumed poll can still route results.
CUSTOM_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def make_custom_id(lang, i, slug):
    cid = f"{lang}-{i:04d}-{slug}"[:64]
    if not CUSTOM_ID_RE.match(cid):
        raise ValueError(f"custom_id out of spec: {cid!r}")
    return cid


# --------------------------------------------------------------------- source
def extract_source(fiche):
    """The EN prose payload for one fiche — only fields present in source
    travel; fields absent stay absent (the model is told never to invent)."""
    en = (fiche.get("i18n") or {}).get("en") or {}
    src = {}
    for f in PROSE_FIELDS:
        v = en.get(f)
        if v in (None, "", [], {}):
            continue
        if f == "hero":
            lead = (v or {}).get("lead")
            if lead:
                src["hero"] = {"lead": lead}
        elif f == "body":
            wi = (v or {}).get("what_is")
            if wi:
                src["body"] = {"what_is": wi}
        else:
            src[f] = v
    # HANDOFF-35 Job A: acces_pmr.detail is FR-authored CONTENT (not a frozen
    # name) — the renderer suppresses it off-fr until a translation exists, so
    # it travels in the payload (source text is FR, the one non-EN field) and
    # lands as i18n.<lang>.acces_pmr_detail.
    det = (fiche.get("acces_pmr") or {}).get("detail")
    if isinstance(det, str) and det.strip():
        src["acces_pmr_detail"] = det.strip()
    return src


def all_communes():
    out = set()
    for p in sorted(glob.glob(str(JSON_DIR / "*.json"))):
        c = (json.load(open(p, encoding="utf-8")).get("commune") or "").strip()
        if c:
            out.add(c)
    return sorted(out)


def fiche_frozen_nouns(fiche):
    nouns = list(CORE_FROZEN)
    name = ((fiche.get("i18n") or {}).get("fr") or {}).get("name")
    if name:
        nouns.append(name.strip())
    commune = (fiche.get("commune") or "").strip()
    if commune:
        nouns.append(commune)
    return nouns


def system_prompt(lang, communes):
    """The shared, prompt-cached instruction block (identical across the
    whole batch — keep it byte-stable; per-fiche content goes in the user
    message AFTER the cache breakpoint)."""
    rtl = ("\nThe target language is written right-to-left. Keep Latin-script "
           "proper names and all numbers exactly as-is — the renderer handles "
           "bidi isolation; do not add RLM/LRM marks.") if lang in RTL_LANGS else ""
    return (
        f"You translate tourism prose for loisirs74.fr from English to "
        f"{LANG_NAMES[lang]}.\n"
        "You receive a JSON object; return ONLY the same JSON object with every "
        "string value translated. Rules:\n"
        "1. Keys stay IDENTICAL. Arrays keep the same length and order. Fields "
        "absent in the input stay absent — never invent content.\n"
        "2. These proper nouns stay VERBATIM untranslated wherever they appear: "
        + ", ".join(CORE_FROZEN) + "; every Haute-Savoie commune name ("
        + ", ".join(communes) + "); and the venue's own proper name given with "
        "the input.\n"
        "3. Keep inline HTML tags (<p>, <ul>, <li>, <strong>, <em>, <a>, <br>) "
        "exactly as structured — same tags, same nesting, translate only the "
        "text between them. Never escape tags as &lt;…&gt;.\n"
        "4. Keep numbers, prices (€), times, phone numbers and URLs unchanged.\n"
        "5. Natural, idiomatic prose for travellers — not word-for-word.\n"
        "6. The output must be VALID JSON: any literal double quote inside a "
        "string value must be escaped as \\\" — better, use the target "
        "language's own typographic quotation marks („…“, »…«, «…», 「…」) "
        "for quoted phrases instead of straight quotes.\n"
        "Return ONLY the translated JSON. No markdown fences, no commentary."
        + rtl
    )


def user_prompt(fiche, src):
    name = ((fiche.get("i18n") or {}).get("fr") or {}).get("name") or fiche.get("slug")
    return (f"Venue proper name (verbatim, never translate): {name}\n"
            f"Commune: {fiche.get('commune') or '—'}\n\n"
            + json.dumps(src, ensure_ascii=False, indent=1))


# ----------------------------------------------------------------- validation
def strings_of(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from strings_of(x)
    elif isinstance(v, list):
        for x in v:
            yield from strings_of(x)


def shape_of(v, path=""):
    """Comparable structural signature: dict key-sets, list lengths, leaf types."""
    if isinstance(v, dict):
        return {k: shape_of(x, f"{path}.{k}") for k, x in sorted(v.items())}
    if isinstance(v, list):
        return [shape_of(x, f"{path}[{i}]") for i, x in enumerate(v)]
    return type(v).__name__


def tag_census(text):
    from collections import Counter
    return Counter(t.lower() for t in TAG_RE.findall(text))


def validate(src, out, frozen_nouns):
    """Returns a list of violations; empty list = PASS."""
    viol = []
    if shape_of(src) != shape_of(out):
        viol.append("key/structure parity: translated JSON does not mirror the source "
                    "(missing, invented, reordered-list or retyped fields)")
    src_all = "\n".join(strings_of(src))
    out_all = "\n".join(strings_of(out))
    for noun in frozen_nouns:
        if noun in src_all and noun not in out_all:
            viol.append(f"frozen noun lost: {noun!r}")
    if tag_census(src_all) != tag_census(out_all):
        viol.append("HTML structure parity: tag multiset differs from source")
    if "&lt;" in out_all and "&lt;" not in src_all:
        viol.append("escaped HTML tags (&lt;…&gt;) in output — breaks raw-emit (HANDOFF-23)")
    if src_all:
        ratio = len(out_all) / len(src_all)
        if not (0.4 <= ratio <= 2.5):
            viol.append(f"length ratio {ratio:.2f} outside 0.4–2.5 (truncation/runaway)")
    # no empty string where source non-empty (walk in parallel where shapes match)
    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in a:
                if k in b:
                    walk(a[k], b[k], f"{path}.{k}")
        elif isinstance(a, list) and isinstance(b, list):
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        elif isinstance(a, str) and isinstance(b, str):
            if a.strip() and not b.strip():
                viol.append(f"empty translation at {path}")
    walk(src, out, "")
    return viol


def repair_json_quotes(t):
    """Escape unescaped double quotes INSIDE JSON string values.

    The cs run's disease (140/389 rejected twice): Czech prose is full of
    quoted phrases and the model emitted them as literal '"' inside string
    values — invalid JSON. Heuristic: while inside a string, a '"' only ends
    it if the next non-whitespace char is a JSON delimiter (, } ] :) or EOF;
    any other '"' is content and gets escaped. Conservative by design — if a
    payload still doesn't parse, it fails exactly as before (validators and
    the absent-field discipline are untouched)."""
    out = []
    i, n = 0, len(t)
    in_str = False
    while i < n:
        c = t[i]
        if not in_str:
            if c == '"':
                in_str = True
            out.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            out.append(t[i:i + 2])
            i += 2
            continue
        if c == '"':
            j = i + 1
            while j < n and t[j] in " \t\r\n":
                j += 1
            if j >= n or t[j] in ",}]:":
                in_str = False
                out.append(c)
            else:
                out.append('\\"')       # interior quote → escape
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def parse_result_text(text):
    """The model is told to return bare JSON; strip fences defensively, and
    repair unescaped in-string quotes before giving up (the cs failure class
    — the content is fine, the quoting isn't)."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return json.loads(repair_json_quotes(t))


# ------------------------------------------------------------------ estimate
def est_tokens(text):
    """Rough chars/3.5 heuristic — for the pre-submit bill preview only."""
    return int(len(text) / 3.5) + 1


def estimate(pairs, communes, lang):
    sys_tok = est_tokens(system_prompt(lang, communes))
    in_tok = out_tok = 0
    for fiche, src in pairs:
        body = est_tokens(user_prompt(fiche, src))
        in_tok += body
        out_tok += body          # translation ≈ source size
    # cached system: first request writes (1.25x), the rest read (0.1x)
    n = len(pairs)
    sys_cost_tok = sys_tok * (1.25 + 0.1 * max(0, n - 1))
    usd = ((in_tok + sys_cost_tok) * BATCH_IN_PER_MTOK + out_tok * BATCH_OUT_PER_MTOK) / 1e6
    return n, in_tok + int(sys_cost_tok), out_tok, usd


# --------------------------------------------------------------------- state
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")


# ----------------------------------------------------------------- batch I/O
def get_client():
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        sys.exit("ERROR: set ANTHROPIC_API_KEY (Eddie's Anthropic Platform key).")
    import anthropic
    return anthropic.Anthropic()


def build_requests(pairs, communes, lang):
    """Returns (requests, {custom_id: slug}) — the id_map is the only way to
    route results back to fiches (results arrive in any order)."""
    sys_block = [{"type": "text", "text": system_prompt(lang, communes),
                  "cache_control": {"type": "ephemeral"}}]
    reqs, id_map = [], {}
    for i, (fiche, src) in enumerate(pairs):
        cid = make_custom_id(lang, i, fiche["slug"])
        id_map[cid] = fiche["slug"]
        reqs.append({
            "custom_id": cid,
            "params": {
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "system": sys_block,
                "messages": [{"role": "user", "content": user_prompt(fiche, src)}],
            },
        })
    return reqs, id_map


def submit_batch(client, reqs):
    batch = client.messages.batches.create(requests=reqs)
    print(f"  submitted batch {batch.id} ({len(reqs)} requests)")
    return batch.id


def poll_batch(client, batch_id, interval=60):
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            print(f"  batch {batch_id} ended: {b.request_counts.succeeded} ok, "
                  f"{b.request_counts.errored} errored, {b.request_counts.expired} expired")
            return b
        print(f"  …{b.processing_status}: {b.request_counts.processing} processing")
        time.sleep(interval)


def collect_results(client, batch_id):
    """{custom_id: ('ok', text) | ('error', reason)} — keyed by custom_id,
    NEVER by position (results arrive in any order)."""
    out = {}
    for r in client.messages.batches.results(batch_id):
        rt = r.result.type
        if rt == "succeeded":
            msg = r.result.message
            text = next((b.text for b in msg.content if b.type == "text"), "")
            out[r.custom_id] = ("ok", text)
        else:
            out[r.custom_id] = ("error", rt)
    return out


# ------------------------------------------------------------------ pipeline
def pairs_for_lang(lang, force=False):
    """(fiche, source) for every fiche missing this language's prose."""
    pairs = []
    for p in sorted(glob.glob(str(JSON_DIR / "*.json"))):
        fiche = json.load(open(p, encoding="utf-8"))
        fiche["_path"] = p
        src = extract_source(fiche)
        if not src:
            continue                     # no EN prose to translate
        blk = (fiche.get("i18n") or {}).get(lang) or {}
        if force:
            pairs.append((fiche, src))
            continue
        # HANDOFF-35: send ONLY the still-missing fields. Adding a field to
        # the payload (acces_pmr_detail) must never re-bill the whole prose of
        # an already-translated fiche — a pt/cs mop-up costs cents, not $19.
        missing = {f: v for f, v in src.items() if f not in blk}
        if not missing:
            continue                     # already populated + validated → skip
        pairs.append((fiche, missing))
    return pairs


def write_back(fiche, lang, out):
    p = fiche["_path"]
    d = json.load(open(p, encoding="utf-8"))     # fresh read — never stale state
    d.setdefault("i18n", {}).setdefault(lang, {}).update(out)
    with open(p, "w", encoding="utf-8") as fp:
        json.dump(d, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def log_failures(lang, failures):
    FAILURES_MD.parent.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    lines = []
    if not FAILURES_MD.exists():
        lines.append("# translate_batch — validation failures (fields left absent)\n\n")
    lines.append(f"## {lang} — run {today}\n\n| fiche | violations |\n|---|---|\n")
    for slug, viol in failures:
        lines.append(f"| {slug} | {'; '.join(viol)} |\n")
    lines.append("\n")
    with open(FAILURES_MD, "a", encoding="utf-8") as fp:
        fp.writelines(lines)


def run_language(lang, args, client=None):
    communes = all_communes()
    pairs = pairs_for_lang(lang, force=args.force)
    n, in_tok, out_tok, usd = estimate(pairs, communes, lang)
    print(f"[{lang}] {n} fiche×lang requests · est ~{in_tok/1000:.0f}k in / "
          f"~{out_tok/1000:.0f}k out tokens · est ~${usd:.2f} on {MODEL} batch")
    if not pairs:
        print(f"[{lang}] nothing to do — already populated (use --force to redo)")
        return True
    if args.dry_run:
        print(f"[{lang}] --dry-run: stopping before submit. Eddie sees the bill first.")
        return True

    client = client or get_client()
    state = load_state()
    lang_state = state.get(lang) or {}

    # submit (or resume a pending batch)
    if lang_state.get("batch_id") and not lang_state.get("done"):
        batch_id = lang_state["batch_id"]
        id_map = lang_state.get("id_map") or {}
        print(f"[{lang}] resuming pending batch {batch_id} ({len(id_map)} routed ids)")
    else:
        reqs, id_map = build_requests(pairs, communes, lang)
        batch_id = submit_batch(client, reqs)
        state[lang] = {"batch_id": batch_id, "id_map": id_map,
                       "submitted": datetime.date.today().isoformat()}
        save_state(state)

    poll_batch(client, batch_id)
    results = collect_results(client, batch_id)

    by_slug = {f["slug"]: (f, s) for f, s in pairs}
    written, retry, failed = 0, [], []
    for cid, (kind, payload) in results.items():
        slug = id_map.get(cid)
        if slug not in by_slug:
            continue
        fiche, src = by_slug[slug]
        viol = None
        if kind == "ok":
            try:
                out = parse_result_text(payload)
                viol = validate(src, out, fiche_frozen_nouns(fiche))
            except Exception as e:
                viol = [f"JSON parse: {e}"]
        else:
            viol = [f"batch result: {payload}"]
        if viol:
            retry.append((fiche, src, viol))
        else:
            write_back(fiche, lang, out)
            written += 1

    # one retry round, fresh requests
    if retry:
        print(f"[{lang}] retrying {len(retry)} failed result(s) once…")
        retry_pairs = [(f, s) for f, s, _ in retry]
        rreqs, rid_map = build_requests(retry_pairs, communes, lang)
        cid_of = {slug: cid for cid, slug in rid_map.items()}
        rid = submit_batch(client, rreqs)
        # persist the retry batch id + routing so a later --recover can re-read
        # BOTH batches' results for free (results live ~29 days server-side)
        state = load_state()
        state.setdefault(lang, {})["retry_batch_id"] = rid
        state[lang]["retry_id_map"] = rid_map
        save_state(state)
        poll_batch(client, rid)
        rres = collect_results(client, rid)
        for fiche, src, first_viol in retry:
            kind, payload = rres.get(cid_of.get(fiche["slug"], ""), ("error", "missing"))
            viol = None
            if kind == "ok":
                try:
                    out = parse_result_text(payload)
                    viol = validate(src, out, fiche_frozen_nouns(fiche))
                except Exception as e:
                    viol = [f"JSON parse: {e}"]
            else:
                viol = [f"batch result: {payload}"]
            if viol:
                failed.append((fiche["slug"], first_viol + viol))
            else:
                write_back(fiche, lang, out)
                written += 1

    if failed:
        log_failures(lang, failed)
        print(f"[{lang}] {len(failed)} pair(s) failed twice → logged to "
              f"{FAILURES_MD}, fields left ABSENT")

    state = load_state()
    state.setdefault(lang, {})["done"] = True
    state[lang]["written"] = written
    save_state(state)

    print(f"[{lang}] DONE: {written}/{len(pairs)} written, {len(failed)} logged failures")
    print(f"[{lang}] next (separate steps): rich render (HANDOFF-22) + gates —")
    print(f"    python3 scripts/build_fulltree_lang.py --lang {lang}")
    print(f"    python3 scripts/gate_render_verified.py")
    return not failed


def recover_language(lang, client):
    """ZERO-SPEND recovery (HANDOFF GO-CS follow-up): re-read the batches this
    language already PAID for (results stay retrievable ~29 days) and re-parse
    every still-missing fiche with the hardened parser. No submit ever happens
    here — only results retrieval, which is free. Validation and the
    absent-field discipline are exactly the ones the live run applies."""
    state = load_state()
    lang_state = state.get(lang) or {}
    batches = []          # (batch_id, {custom_id: slug})
    if lang_state.get("retry_batch_id"):
        batches.append((lang_state["retry_batch_id"],
                        {c: s for c, s in (lang_state.get("retry_id_map") or {}).items()}))
    if lang_state.get("batch_id"):
        batches.append((lang_state["batch_id"], lang_state.get("id_map") or {}))
    if not batches:
        sys.exit(f"[{lang}] nothing to recover — no batch ids in state")

    pairs = pairs_for_lang(lang)                 # exactly the still-missing fiches
    by_slug = {f["slug"]: (f, s) for f, s in pairs}
    print(f"[{lang}] recover: {len(by_slug)} fiche(s) still missing; "
          f"re-reading {len(batches)} paid batch(es)")

    def slug_of(cid, id_map):
        if cid in id_map:
            return id_map[cid]
        # the retry batch of the original cs run predates retry_id_map
        # persistence — reconstruct from the custom_id's slug fragment
        # (f"{lang}-{i:04d}-{slug}"[:64]); match by prefix against the
        # missing set, unique or nothing.
        frag = cid.split("-", 2)[-1] if cid.count("-") >= 2 else ""
        hits = [s for s in by_slug if s.startswith(frag) or frag.startswith(s)]
        return hits[0] if len(hits) == 1 else None

    recovered, still = 0, dict(by_slug)
    for batch_id, id_map in batches:
        if not still:
            break
        print(f"  reading results of {batch_id} …")
        results = collect_results(client, batch_id)
        for cid, (kind, payload) in results.items():
            if kind != "ok":
                continue
            slug = slug_of(cid, id_map)
            if slug not in still:
                continue
            fiche, src = still[slug]
            try:
                out = parse_result_text(payload)
            except Exception:
                continue                          # still unparsable — next batch
            if validate(src, out, fiche_frozen_nouns(fiche)):
                continue                          # content violations → stays absent
            write_back(fiche, lang, out)
            del still[slug]
            recovered += 1

    state = load_state()
    state.setdefault(lang, {})["written"] = (lang_state.get("written") or 0) + recovered
    state[lang]["recovered"] = recovered
    save_state(state)
    if still:
        log_failures(lang, [(s, ["unrecoverable after quote-repair (recovery run)"])
                            for s in sorted(still)])
    print(f"[{lang}] RECOVERED {recovered} fiche(s) for $0; "
          f"{len(still)} remain absent: {sorted(still)[:10]}{'…' if len(still) > 10 else ''}")
    return recovered


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lang", required=True,
                    help=f"one of {'/'.join(TARGET_LANGS)}, or 'all' (sequence: {' → '.join(TARGET_LANGS)})")
    ap.add_argument("--dry-run", action="store_true",
                    help="print request count + token/cost estimate and stop (no submit)")
    ap.add_argument("--force", action="store_true",
                    help="redo fiche×lang pairs that are already populated")
    ap.add_argument("--recover", action="store_true",
                    help="ZERO-SPEND: re-read this language's already-paid batch results "
                         "and re-parse the missing fiches with the hardened parser (no submit)")
    args = ap.parse_args()

    langs = TARGET_LANGS if args.lang == "all" else [args.lang]
    for lang in langs:
        if lang not in TARGET_LANGS:
            sys.exit(f"ERROR: unknown target language {lang!r} (expected {TARGET_LANGS})")

    if args.recover:
        client = get_client()
        for lang in langs:
            recover_language(lang, client)
        return

    client = None if args.dry_run else get_client()
    for lang in langs:
        ok = run_language(lang, args, client)
        if not ok and args.lang == "all":
            print(f"stopping the sequence at {lang} — review the failure log first.")
            sys.exit(1)


if __name__ == "__main__":
    main()
