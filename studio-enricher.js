// studio-enricher.js — Tab 5: one-shot AI enrichment of an existing fiche.
//
// Workflow:
//   1. Drop an existing Json/<slug>.json
//   2. Optionally drop a hero image (jpg/png)
//   3. Click "Enrichir" → one API call to Claude with the full enrichment goal
//   4. Diff summary appears: per-field old/new with Accept/Reject checkboxes
//   5. Click "Télécharger ZIP" → ZIP with json/<slug>.json + image + README
//
// Reuses Tab 1's API key (localStorage 'loisirs74_api_key') and model selector.
// Reuses JSZip (already loaded by studio.html for Tab 3 build).
//
// Public API:
//   window.StudioEnricher.mount(rootEl)

(function () {
  'use strict';

  const KEY_STORAGE = 'loisirs74_api_key';
  const API_URL = 'https://api.anthropic.com/v1/messages';
  const API_VERSION = '2023-06-01';

  let original = null;        // last loaded JSON (untouched merge base)
  let enriched = null;        // AI-enriched JSON
  let imageBlob = null;       // optional hero image File
  let imageExt = 'jpg';
  let changes = [];           // [{path, oldValue, newValue}]
  let rejected = new Set();   // paths the user unchecked

  const SYSTEM_PROMPT = `# Loisirs 74 — ENRICHER

You are the JSON enricher for Loisirs 74. The user gives you a complete fiche JSON
for a venue. Your job is to PRODUCE a new JSON that is the same fiche, enriched.

ENRICHMENT GOALS (apply all that are relevant):

1. VERIFY current values via web research:
   - Phone, address, postal_code, latitude/longitude
   - Hours, tariffs, opening dates (specifically check for 2026 changes)
   - official_site_url still resolves and matches the venue
   If any are outdated, UPDATE them. If correct, keep as-is.

2. TRANSLATE: if any non-FR locale (i18n.{en,de,it,es}) is missing or contains
   French text (i.e. it's an untranslated FR-mirror), produce a real
   translation. Keep the same i18n field structure. Match the formal voice
   used in the rest of the catalog.

3. EXPAND FAQ: target 6-8 high-quality, distinct Q/A pairs. Keep all existing
   correct ones; ADD new ones for common visitor questions (best time, with
   kids, accessibility, parking, booking required, what to bring).

4. EXPAND activities: target 4-6 cards. Each card has title + body + optional tag.
   No filler — only real, verifiable features of the venue.

5. THICKEN meta_description: target 140-160 characters. Should pitch the
   venue's distinctive value, not just describe.

6. THICKEN body.what_is: target 1200-1800 characters. Use <p> and <strong>
   tags. Cover: what it is, what visitors actually do there, what makes it
   stand out from similar venues in Haute-Savoie, practical highlights.

7. SUGGEST partners (top-level "partners" array): 2-3 nearby legitimate
   businesses (restaurant, café, lodge, commerce) within ~5 km. Each:
   { "tier": "recommended", "name": "...", "type": "...", "description": "...",
     "url": "..." (only if you can verify their site exists) }
   No fabrication. If you can't find good candidates, leave partners empty.

8. UPDATE sources: keep all existing source URLs that still verify;
   add 1-2 new authoritative sources (official site, tourism office,
   wikipedia) if you discovered them while researching.

DO NOT TOUCH:
- slug
- hero_image
- hero_credit
- verify_flags
- research_log
- date_published_human

OUTPUT FORMAT:
Return ONLY a JSON object — no markdown fences, no commentary before or after.
The JSON must have the same top-level keys as the input, plus any added
fields. Validate that:
- All 5 locales (fr/en/de/it/es) are present in i18n
- Each locale has the same sub-keys as i18n.fr
- All non-FR locales contain text in that language (not FR)
- No internal scaffolding leaks (no "Substitut", "Cross-link", "master list",
  "déjà publié", "Tier 1/2/3", "venue #", "à compléter", "TODO", "FIXME").

If you cannot complete an enrichment goal due to lack of verifiable info,
leave that field unchanged rather than fabricate.`;

  // -----------------------------------------------------------------------
  // PATH UTILITIES
  // -----------------------------------------------------------------------

  function pathToArr(path) {
    // Convert "i18n.fr.activities[0].title" → ['i18n','fr','activities',0,'title']
    return path.replace(/\[(\d+)\]/g, '.$1').split('.').map((p) => /^\d+$/.test(p) ? +p : p);
  }

  function deepGet(obj, path) {
    let cur = obj;
    for (const p of pathToArr(path)) {
      if (cur == null) return undefined;
      cur = cur[p];
    }
    return cur;
  }

  function deepSet(obj, path, value) {
    const parts = pathToArr(path);
    let cur = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      const p = parts[i];
      const next = parts[i + 1];
      if (cur[p] == null) cur[p] = typeof next === 'number' ? [] : {};
      cur = cur[p];
    }
    cur[parts[parts.length - 1]] = value;
  }

  // -----------------------------------------------------------------------
  // DIFF — walk old vs new, produce flat list of changes by path
  // -----------------------------------------------------------------------

  // Top-level fields to ignore in the diff (locked by enricher contract)
  const LOCKED_PATHS = new Set([
    'slug', 'hero_image', 'hero_credit',
    'verify_flags', 'research_log', 'date_published_human',
  ]);

  function computeChanges(oldObj, newObj) {
    const out = [];
    walk(oldObj, newObj, '', out);
    return out;
  }

  function walk(oldV, newV, path, out) {
    // Skip locked top-level paths
    if (LOCKED_PATHS.has(path)) return;

    // Same value (deep) → no change
    if (JSON.stringify(oldV) === JSON.stringify(newV)) return;

    // Array → treat as a single change (replace wholesale)
    if (Array.isArray(oldV) || Array.isArray(newV)) {
      out.push({ path: path || '(root)', oldValue: oldV, newValue: newV, kind: 'array' });
      return;
    }

    // Both objects → recurse
    if (oldV && typeof oldV === 'object' && newV && typeof newV === 'object') {
      const keys = new Set([...Object.keys(oldV), ...Object.keys(newV)]);
      for (const k of keys) walk(oldV[k], newV[k], path ? `${path}.${k}` : k, out);
      return;
    }

    // Scalar change
    out.push({ path: path || '(root)', oldValue: oldV, newValue: newV, kind: 'scalar' });
  }

  // -----------------------------------------------------------------------
  // API CALL
  // -----------------------------------------------------------------------

  async function callAPI(jsonObj, hints) {
    const apiKey = localStorage.getItem(KEY_STORAGE) || '';
    if (!apiKey) throw new Error("Configure la clé API dans l'onglet 1 d'abord.");

    const modelEl = document.getElementById('api-model');
    const model = modelEl ? modelEl.value : 'claude-sonnet-4-5';

    let userMsg = 'Voici le JSON existant à enrichir. Retourne le JSON enrichi complet (pas de fences markdown, pas de commentaire).\n\n```json\n' + JSON.stringify(jsonObj, null, 2) + '\n```';
    if (hints && hints.trim()) {
      userMsg += '\n\n## Indices fournis par l\'utilisateur (à prioriser)\n\n' + hints.trim();
    }

    const body = {
      model,
      max_tokens: 32000,
      system: SYSTEM_PROMPT,
      tools: [
        { type: 'web_search_20250305', name: 'web_search' },
      ],
      messages: [{ role: 'user', content: userMsg }],
    };

    setStatus('Appel API en cours… (peut prendre 1-3 minutes)');
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': API_VERSION,
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`API ${res.status}: ${errText.slice(0, 400)}`);
    }

    const data = await res.json();
    // Extract text from the response (could be content[].text array)
    let text = '';
    if (Array.isArray(data.content)) {
      for (const block of data.content) {
        if (block.type === 'text' && block.text) text += block.text;
      }
    }
    if (!text) throw new Error('Réponse API vide.');

    // Strip potential markdown fences (defensive — system prompt says no fences)
    text = text.trim();
    if (text.startsWith('```')) {
      text = text.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '').trim();
    }

    // If the AI added a prose preamble before the JSON ("Based on my
    // research, …"), grab the first balanced { … } block.
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (_) {
      const start = text.indexOf('{');
      if (start < 0) throw new Error('Réponse sans objet JSON.');
      // Walk to the matching closing brace, respecting string quotes
      let depth = 0;
      let inStr = false;
      let esc = false;
      let end = -1;
      for (let i = start; i < text.length; i++) {
        const c = text[i];
        if (esc) { esc = false; continue; }
        if (c === '\\' && inStr) { esc = true; continue; }
        if (c === '"') { inStr = !inStr; continue; }
        if (inStr) continue;
        if (c === '{') depth++;
        else if (c === '}') {
          depth--;
          if (depth === 0) { end = i; break; }
        }
      }
      if (end < 0) throw new Error("Bloc JSON non équilibré dans la réponse.");
      try {
        parsed = JSON.parse(text.slice(start, end + 1));
      } catch (err) {
        throw new Error('JSON enrichi invalide : ' + err.message
          + '\nExtrait (300 chars):\n' + text.slice(start, start + 300));
      }
    }

    if (!parsed.slug || parsed.slug !== jsonObj.slug) {
      throw new Error(`Slug modifié ou absent (attendu: ${jsonObj.slug}, reçu: ${parsed.slug}). L'enricher ne doit pas changer le slug.`);
    }
    // Re-impose locked fields from original
    for (const lockedKey of LOCKED_PATHS) {
      if (jsonObj[lockedKey] !== undefined) parsed[lockedKey] = jsonObj[lockedKey];
    }
    return parsed;
  }

  // -----------------------------------------------------------------------
  // UI
  // -----------------------------------------------------------------------

  function setStatus(text, kind = 'info') {
    const el = document.getElementById('enricher-status');
    if (!el) return;
    el.textContent = text;
    el.style.color = kind === 'err' ? 'var(--bad)' : kind === 'ok' ? 'var(--good)' : 'var(--ink-mute)';
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  }

  function truncate(s, n) {
    s = String(s == null ? '' : s);
    return s.length > n ? s.slice(0, n) + '…' : s;
  }

  function valueRepr(v, maxChars = 400) {
    if (v === null) return '<null>';
    if (v === undefined) return '<undefined>';
    if (typeof v === 'string') return truncate(v, maxChars);
    if (typeof v === 'object') return truncate(JSON.stringify(v, null, 2), maxChars);
    return String(v);
  }

  function renderDiff() {
    const container = document.getElementById('enricher-diff');
    container.innerHTML = '';
    if (!changes.length) {
      container.innerHTML = '<p class="field-help">Aucun changement détecté.</p>';
      return;
    }

    // Group by top-level section so the user can scan
    const groups = {};
    for (const c of changes) {
      const root = c.path.split('.')[0].split('[')[0];
      (groups[root] = groups[root] || []).push(c);
    }
    const order = ['i18n', 'partners', 'sources', 'practical_info', 'price_from', 'price_currency', 'official_site_url', 'booking_url', 'booking_domain', 'schema_org', 'commune', 'postal_code', 'latitude', 'longitude', 'subcategories'];
    const sortedRoots = Object.keys(groups).sort((a, b) => {
      const ai = order.indexOf(a), bi = order.indexOf(b);
      if (ai === -1 && bi === -1) return a.localeCompare(b);
      if (ai === -1) return 1;
      if (bi === -1) return -1;
      return ai - bi;
    });

    for (const root of sortedRoots) {
      const groupChanges = groups[root];
      const det = document.createElement('details');
      det.className = 'card';
      det.open = groupChanges.length <= 6;

      const sum = document.createElement('summary');
      sum.style.cursor = 'pointer';
      sum.style.fontWeight = '700';
      sum.innerHTML = `${escapeHtml(root)} <span style="color:var(--ink-mute);font-weight:500">— ${groupChanges.length} change${groupChanges.length > 1 ? 's' : ''}</span>`;
      det.appendChild(sum);

      for (const c of groupChanges) {
        const row = document.createElement('div');
        row.style.borderTop = '1px solid var(--line)';
        row.style.padding = '.75rem 0';

        // Header: checkbox + path
        const header = document.createElement('label');
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '.5rem';
        header.style.fontFamily = 'var(--mono)';
        header.style.fontSize = '.78rem';
        header.style.marginBottom = '.4rem';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = !rejected.has(c.path);
        checkbox.dataset.path = c.path;
        checkbox.addEventListener('change', () => {
          if (checkbox.checked) rejected.delete(c.path);
          else rejected.add(c.path);
          updateAcceptCount();
        });
        header.appendChild(checkbox);

        const pathSpan = document.createElement('strong');
        pathSpan.style.color = 'var(--ink)';
        pathSpan.textContent = c.path;
        header.appendChild(pathSpan);

        const kindBadge = document.createElement('span');
        kindBadge.style.fontSize = '.6rem';
        kindBadge.style.background = 'var(--surface-2)';
        kindBadge.style.padding = '.05rem .35rem';
        kindBadge.style.borderRadius = '4px';
        kindBadge.textContent = c.kind === 'array' ? 'array' : c.oldValue === undefined ? 'new' : 'changed';
        header.appendChild(kindBadge);

        row.appendChild(header);

        // Old/new side by side
        const grid = document.createElement('div');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = '1fr 1fr';
        grid.style.gap = '.5rem';
        grid.style.fontSize = '.75rem';

        const oldBox = document.createElement('pre');
        oldBox.style.background = 'var(--bad-bg)';
        oldBox.style.color = 'var(--ink)';
        oldBox.style.padding = '.5rem';
        oldBox.style.borderRadius = '6px';
        oldBox.style.whiteSpace = 'pre-wrap';
        oldBox.style.wordBreak = 'break-word';
        oldBox.style.margin = '0';
        oldBox.style.maxHeight = '12rem';
        oldBox.style.overflow = 'auto';
        oldBox.textContent = valueRepr(c.oldValue, 1200);
        grid.appendChild(oldBox);

        const newBox = document.createElement('pre');
        newBox.style.background = 'color-mix(in srgb,var(--good) 14%,transparent)';
        newBox.style.color = 'var(--ink)';
        newBox.style.padding = '.5rem';
        newBox.style.borderRadius = '6px';
        newBox.style.whiteSpace = 'pre-wrap';
        newBox.style.wordBreak = 'break-word';
        newBox.style.margin = '0';
        newBox.style.maxHeight = '12rem';
        newBox.style.overflow = 'auto';
        newBox.textContent = valueRepr(c.newValue, 1200);
        grid.appendChild(newBox);

        row.appendChild(grid);
        det.appendChild(row);
      }

      container.appendChild(det);
    }

    updateAcceptCount();
  }

  function updateAcceptCount() {
    const el = document.getElementById('enricher-accept-count');
    if (!el) return;
    const accepted = changes.length - rejected.size;
    el.textContent = `${accepted} / ${changes.length} acceptés`;
    document.getElementById('enricher-zip-btn').disabled = accepted === 0 && !imageBlob;
  }

  // -----------------------------------------------------------------------
  // BUILD PATCHED JSON (from accepted changes only)
  // -----------------------------------------------------------------------

  function buildAcceptedJSON() {
    // Start from a deep clone of original; apply only non-rejected changes
    const out = JSON.parse(JSON.stringify(original));
    for (const c of changes) {
      if (rejected.has(c.path)) continue;
      if (c.path === '(root)') {
        // Shouldn't happen with our walk, but defensive
        continue;
      }
      // For arrays/objects, the change is wholesale at that path
      deepSet(out, c.path, c.newValue);
    }
    // If user dropped an image, force hero_image to point at it
    if (imageBlob) {
      out.hero_image = `/${out.slug}-hero.${imageExt}`;
      out.hero_credit = null;
    }
    return out;
  }

  // -----------------------------------------------------------------------
  // ZIP EXPORT
  // -----------------------------------------------------------------------

  async function exportZip() {
    if (!enriched) return alert('Pas encore enrichi.');
    if (typeof JSZip === 'undefined') return alert('JSZip non chargé.');
    const zip = new JSZip();
    const patched = buildAcceptedJSON();
    const slug = patched.slug;

    zip.file(`json/${slug}.json`, JSON.stringify(patched, null, 2) + '\n');

    if (imageBlob) {
      zip.file(`${slug}-hero.${imageExt}`, imageBlob);
    }

    const readme = [
      `# Enriched fiche: ${slug}`,
      ``,
      `Generated by Loisirs74 Studio · Enrichir (Tab 5)`,
      `Source JSON: ${slug}.json (before enrichment)`,
      `Model used: ${document.getElementById('api-model')?.value || '?'}`,
      `Changes applied: ${changes.length - rejected.size} of ${changes.length}`,
      `Image included: ${imageBlob ? 'yes (' + slug + '-hero.' + imageExt + ')' : 'no'}`,
      ``,
      `## To integrate`,
      ``,
      `1. Drop json/${slug}.json into the repo's Json/ folder (overwrite).`,
      `2. ${imageBlob ? `Drop ${slug}-hero.${imageExt} into the repo root.` : `No image to drop.`}`,
      `3. Run: python3 scripts/build_lieu_page.py Json/${slug}.json`,
      `4. Run: python3 scripts/localize_lieu.py ${slug}`,
      `5. Run the rest of the pipeline (sync_hub_cards, update_related, build_homepage).`,
      `6. Commit + push.`,
      ``,
      `## Rejected changes (not in this ZIP)`,
      rejected.size ? Array.from(rejected).map((p) => `- ${p}`).join('\n') : '(none)',
      ``,
    ].join('\n');
    zip.file('README.txt', readme);

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    a.href = url;
    a.download = `enriched-${slug}-${date}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setStatus('ZIP téléchargé.', 'ok');
  }

  // -----------------------------------------------------------------------
  // LOAD HANDLERS
  // -----------------------------------------------------------------------

  function loadJSON(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (!parsed.slug) throw new Error('JSON sans champ "slug" — pas une fiche.');
        original = parsed;
        enriched = null;
        changes = [];
        rejected = new Set();
        document.getElementById('enricher-loaded').textContent = `Chargé : ${parsed.slug} (${parsed.commune || '?'})`;
        document.getElementById('enricher-enrich-btn').disabled = false;
        document.getElementById('enricher-diff').innerHTML = '';
        document.getElementById('enricher-zip-btn').disabled = true;
        setStatus(`Fiche chargée : ${parsed.slug}. Optionnellement, glisse une image hero. Puis clic Enrichir.`);
      } catch (err) {
        alert('Erreur de chargement : ' + err.message);
      }
    };
    reader.readAsText(file);
  }

  function loadImage(file) {
    if (!/^image\//.test(file.type)) {
      alert('Pas une image.');
      return;
    }
    imageBlob = file;
    imageExt = (file.name.split('.').pop() || 'jpg').toLowerCase();
    if (!['jpg', 'jpeg', 'png', 'webp'].includes(imageExt)) imageExt = 'jpg';
    const el = document.getElementById('enricher-image-loaded');
    el.textContent = `Image chargée : ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
    updateAcceptCount();
  }

  // -----------------------------------------------------------------------
  // ENRICH ACTION
  // -----------------------------------------------------------------------

  async function runEnrich() {
    if (!original) return alert("Charge d'abord une fiche.");
    const btn = document.getElementById('enricher-enrich-btn');
    btn.disabled = true;
    const hints = document.getElementById('enricher-hints')?.value || '';
    const t0 = Date.now();
    try {
      enriched = await callAPI(original, hints);
      changes = computeChanges(original, enriched);
      rejected = new Set();
      renderDiff();
      setStatus(`Enrichi en ${((Date.now() - t0) / 1000).toFixed(1)}s. ${changes.length} champs modifiés.`, 'ok');
      document.getElementById('enricher-zip-btn').disabled = false;
    } catch (err) {
      setStatus('Erreur : ' + err.message, 'err');
      console.error(err);
    } finally {
      btn.disabled = false;
    }
  }

  // -----------------------------------------------------------------------
  // BATCH MODE — autonomous loop across many fiches
  // -----------------------------------------------------------------------

  let batchAbort = false;
  let batchResults = [];  // [{slug, original, enriched, changes, error, errorStage, errorDetail}]
  let batchQueue = [];    // [slug, slug, …] — slugs the user has selected to enrich
  const batchRows = new Map(); // slug → DOM row reference

  // --- queue building --------------------------------------------------

  function addToQueue(slug) {
    if (!slug || batchQueue.includes(slug)) return;
    batchQueue.push(slug);
    renderQueue();
  }

  function removeFromQueue(slug) {
    batchQueue = batchQueue.filter(s => s !== slug);
    renderQueue();
  }

  function clearQueue() {
    batchQueue = [];
    renderQueue();
  }

  function fillQueueGeneric() {
    batchQueue = catalog.filter(f => !f.real).map(f => f.slug);
    renderQueue();
  }

  function renderQueue() {
    const list = document.getElementById('batch-queue-list');
    const count = document.getElementById('batch-queue-count');
    if (!list || !count) return;
    count.textContent = `${batchQueue.length} fiche${batchQueue.length === 1 ? '' : 's'}`;
    list.innerHTML = '';
    if (!batchQueue.length) {
      list.innerHTML = '<p class="field-help" style="padding:.5rem .65rem;margin:0">File vide. Ajoute des fiches depuis la liste déroulante ou clique « Toutes sans vraie photo ».</p>';
      document.getElementById('batch-start-btn').disabled = true;
      return;
    }
    document.getElementById('batch-start-btn').disabled = false;
    const byCat = {};
    for (const slug of batchQueue) {
      const f = catalog.find(c => c.slug === slug);
      if (!f) continue;
      (byCat[f.category] = byCat[f.category] || []).push(f);
    }
    for (const cat of Object.keys(byCat).sort()) {
      const head = document.createElement('div');
      head.style.cssText = 'font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-mute);padding:.35rem .65rem;background:var(--surface)';
      head.textContent = `${cat} (${byCat[cat].length})`;
      list.appendChild(head);
      for (const f of byCat[cat]) {
        const row = document.createElement('div');
        row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;gap:.5rem;padding:.3rem .65rem;border-top:1px solid var(--line);font-size:.78rem';
        row.innerHTML = `<span><span style="font-family:var(--mono)">${escapeHtml(f.slug)}</span> <span style="color:var(--ink-mute)">— ${escapeHtml(f.name)}${f.real ? '' : ' · générique'}</span></span>`;
        const x = document.createElement('button');
        x.className = 'btn';
        x.style.cssText = 'padding:.2rem .55rem;font-size:.75rem';
        x.textContent = '×';
        x.title = 'Retirer de la file';
        x.addEventListener('click', () => removeFromQueue(f.slug));
        row.appendChild(x);
        list.appendChild(row);
      }
    }
  }

  // --- per-fiche processing -------------------------------------------

  function makeStatusRow(slug, name) {
    const row = document.createElement('div');
    row.dataset.slug = slug;
    row.style.cssText = 'padding:.4rem .65rem;border-bottom:1px solid var(--line);font-size:.78rem;display:grid;grid-template-columns:1fr auto auto auto;gap:.5rem;align-items:center';
    row.innerHTML = `
      <span><span style="font-family:var(--mono)">${escapeHtml(slug)}</span> <span style="color:var(--ink-mute)">— ${escapeHtml(name || '')}</span></span>
      <span class="stage" style="color:var(--ink-mute);font-size:.72rem;min-width:7rem;text-align:right">en file</span>
      <span class="timer" style="color:var(--ink-mute);font-family:var(--mono);font-size:.7rem;min-width:3.5rem;text-align:right"></span>
      <span class="result"></span>`;
    return row;
  }

  function setStage(row, stage, ok) {
    const el = row.querySelector('.stage');
    if (!el) return;
    el.textContent = stage;
    el.style.color = ok === 'err' ? 'var(--bad, #c00)' : ok === 'ok' ? 'var(--good, #0a5a3a)' : 'var(--ink-mute)';
  }

  function setResult(row, html) {
    const el = row.querySelector('.result');
    if (el) el.innerHTML = html;
  }

  function tickTimer(row, t0) {
    const el = row.querySelector('.timer');
    if (!el) return null;
    function update() { el.textContent = ((Date.now() - t0) / 1000).toFixed(0) + 's'; }
    update();
    return setInterval(update, 500);
  }

  async function processOne(slug, row) {
    const t0 = Date.now();
    const timer = tickTimer(row, t0);
    let stage = 'fetch JSON';
    setStage(row, '📥 ' + stage);
    try {
      const r = await fetch('/Json/' + slug + '.json');
      if (!r.ok) throw new Error('HTTP ' + r.status + ' on /Json/' + slug + '.json');
      const txt = await r.text();
      let orig;
      try { orig = JSON.parse(txt); }
      catch (e) { stage = 'parse local JSON'; throw e; }

      stage = 'appel API';
      setStage(row, '🤖 ' + stage);
      console.group(`[enricher] ${slug}`);
      console.log('Original:', orig);
      const enr = await callAPI(orig, '');
      console.log('Enriched:', enr);

      stage = 'diff';
      setStage(row, '📝 ' + stage);
      const ch = computeChanges(orig, enr);
      console.log(`${ch.length} field changes`);
      console.groupEnd();

      if (timer) clearInterval(timer);
      const dt = ((Date.now() - t0) / 1000).toFixed(0);
      row.querySelector('.timer').textContent = dt + 's';
      setStage(row, '✅ terminé', 'ok');
      setResult(row, `<strong>${ch.length}</strong> <span style="color:var(--ink-mute)">champs</span>`);
      // record success
      const existing = batchResults.find(b => b.slug === slug);
      if (existing) Object.assign(existing, { original: orig, enriched: enr, changes: ch, error: null });
      else batchResults.push({ slug, original: orig, enriched: enr, changes: ch });
    } catch (err) {
      if (timer) clearInterval(timer);
      const dt = ((Date.now() - t0) / 1000).toFixed(0);
      row.querySelector('.timer').textContent = dt + 's';
      console.error(`[enricher] ${slug} failed at "${stage}":`, err);
      try { console.groupEnd(); } catch (_) {}
      const msg = String(err && err.message || err);
      setStage(row, '❌ ' + stage, 'err');
      // Full error text — collapsible
      const errId = 'err-' + slug.replace(/[^a-z0-9-]/g, '');
      setResult(row,
        `<details style="font-size:.72rem"><summary style="cursor:pointer;color:var(--bad,#c00)">voir l'erreur</summary>` +
        `<pre style="white-space:pre-wrap;word-break:break-word;background:var(--surface-2);padding:.45rem;border-radius:4px;margin:.3rem 0 0 0;max-height:12rem;overflow:auto">${escapeHtml(msg)}</pre>` +
        `</details>` +
        ` <button class="btn" style="padding:.2rem .55rem;font-size:.72rem;margin-left:.3rem" data-retry-slug="${escapeHtml(slug)}">🔄 réessayer</button>`);
      const existing = batchResults.find(b => b.slug === slug);
      const rec = { slug, error: msg, errorStage: stage };
      if (existing) Object.assign(existing, rec, { original: null, enriched: null, changes: null });
      else batchResults.push(rec);
      // wire retry button (we re-process this slug in-place)
      const retryBtn = row.querySelector(`[data-retry-slug="${slug}"]`);
      if (retryBtn) retryBtn.addEventListener('click', () => {
        retryBtn.disabled = true;
        setResult(row, '');
        processOne(slug, row);
      });
    }
  }

  async function runBatch() {
    if (!batchQueue.length) return alert('La file est vide. Ajoute des fiches d\'abord.');
    const startBtn = document.getElementById('batch-start-btn');
    const stopBtn = document.getElementById('batch-stop-btn');
    const progress = document.getElementById('batch-progress');
    const log = document.getElementById('batch-log');

    batchAbort = false;
    batchResults = [];
    batchRows.clear();
    startBtn.disabled = true;
    stopBtn.disabled = false;
    log.innerHTML = '';

    // Pre-populate rows so the user sees the entire run plan upfront
    for (const slug of batchQueue) {
      const f = catalog.find(c => c.slug === slug);
      const row = makeStatusRow(slug, f ? f.name : '');
      log.appendChild(row);
      batchRows.set(slug, row);
    }

    for (let i = 0; i < batchQueue.length; i++) {
      if (batchAbort) {
        for (const slug of batchQueue.slice(i)) {
          const row = batchRows.get(slug);
          if (row) setStage(row, '⏸ annulé');
        }
        break;
      }
      const slug = batchQueue[i];
      progress.textContent = `Fiche ${i + 1}/${batchQueue.length} : ${slug}…`;
      const row = batchRows.get(slug);
      row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      await processOne(slug, row);
    }

    const okN = batchResults.filter(r => !r.error).length;
    const errN = batchResults.filter(r => r.error).length;
    progress.textContent = `Terminé : ${okN} succès · ${errN} erreur${errN > 1 ? 's' : ''} sur ${batchQueue.length} fiche${batchQueue.length > 1 ? 's' : ''}.`;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    document.getElementById('batch-zip-btn').disabled = okN === 0;
  }

  function stopBatch() {
    batchAbort = true;
    document.getElementById('batch-progress').textContent += ' (arrêt demandé — termine la fiche en cours…)';
  }

  async function exportBatchZip() {
    if (typeof JSZip === 'undefined') return alert('JSZip non chargé.');
    if (!batchResults.length) return alert('Rien à exporter.');
    const zip = new JSZip();
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    let okCount = 0;
    for (const r of batchResults) {
      if (r.error) continue;
      // For batch, accept ALL changes (user hasn't reviewed individually)
      zip.file(`json/${r.slug}.json`, JSON.stringify(r.enriched, null, 2) + '\n');
      okCount++;
    }
    const manifest = [
      `# Batch enrichment — ${date}`, '',
      `${okCount} fiches enrichies, ${batchResults.length - okCount} en erreur.`, '',
      '## Fiches enrichies', '',
      ...batchResults.filter(r => !r.error).map(r => `- ${r.slug} (${r.changes.length} champs)`),
      '', '## Erreurs',
      ...batchResults.filter(r => r.error).map(r => `- ${r.slug} : ${r.error}`),
      '', '## Intégration',
      '1. Place tous les json/*.json dans Json/ du repo.',
      '2. Lance scripts/build_lieu_page.py + localize_lieu.py pour chacun.',
      '3. Rebuild hubs + homepage + commit.', '',
    ].join('\n');
    zip.file('README.txt', manifest);

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch-enriched-${date}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // -----------------------------------------------------------------------
  // MOUNT
  // -----------------------------------------------------------------------

  function mount(root) {
    root.innerHTML = `
      <div class="help">
        <strong>Étape 5 — AI Enricher.</strong> Deux modes :
        <strong>(A) ciblé</strong> — choisis 1 fiche, optionnellement ajoute des indices (URLs, notes), enrichis, revois le diff, télécharge le ZIP.
        <strong>(B) batch</strong> — laisse l'IA tourner sur les fiches du catalogue sans intervention. Chaque fiche enrichie va dans un ZIP global.
      </div>

      <div class="card">
        <div class="card-head">
          <h3>A · Mode ciblé — 1 fiche</h3>
        </div>
        <div class="field">
          <label for="enricher-venue-select">Fiche</label>
          <select id="enricher-venue-select" size="1">
            <option value="">— Chargement du catalogue —</option>
          </select>
          <p class="field-help">Toutes les fiches du catalogue préchargées, groupées par catégorie.</p>
        </div>
        <div class="field">
          <label for="enricher-hints">Indices / URLs / notes pour l'IA <span style="color:var(--ink-mute);font-weight:400">(optionnel)</span></label>
          <textarea id="enricher-hints" rows="3" placeholder="Ex: site officiel à utiliser https://… · horaires 2026 vérifiés sur place: lun-ven 10h-18h · nouveau directeur Pierre Dupont depuis avril 2026 · etc."></textarea>
          <p class="field-help">Tout ce que tu sais et que l'IA doit utiliser. URL d'un site qu'elle n'a pas trouvé, fait à corriger, contexte. Sera passé tel quel dans le prompt.</p>
        </div>
        <p id="enricher-loaded" class="field-help" style="margin-top:.65rem">Aucune fiche sélectionnée</p>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>2. (Optionnel) Image hero personnelle</h3>
          <span class="field-help">Si fournie, remplacera <code>hero_image</code> par <code>/&lt;slug&gt;-hero.&lt;ext&gt;</code> et l'image sera incluse dans le ZIP.</span>
        </div>
        <div id="enricher-drop-image" style="border:2px dashed var(--line);border-radius:10px;padding:1.25rem;text-align:center;cursor:pointer">
          <p style="margin:0;color:var(--ink-mute)">Glisse une image ici (jpg/png/webp), ou
            <label style="color:var(--accent);cursor:pointer;text-decoration:underline">parcourir<input type="file" id="enricher-file-image" accept="image/*" style="display:none"></label>.</p>
        </div>
        <p id="enricher-image-loaded" class="field-help" style="margin-top:.5rem">Aucune image chargée</p>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>3. Enrichir via IA</h3>
          <div class="card-actions">
            <button class="btn btn-primary" id="enricher-enrich-btn" disabled>✨ Enrichir</button>
          </div>
        </div>
        <p id="enricher-status" class="field-help">En attente.</p>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>4. Diff & téléchargement</h3>
          <div class="card-actions">
            <span id="enricher-accept-count" class="field-help">0 / 0 acceptés</span>
            <button class="btn btn-primary" id="enricher-zip-btn" disabled>⬇ Télécharger ZIP</button>
          </div>
        </div>
        <div id="enricher-diff"></div>
      </div>

      <div class="card" style="margin-top:1.5rem;border:2px solid color-mix(in srgb,var(--accent) 25%,var(--line))">
        <div class="card-head">
          <h3>B · Mode batch — file personnalisée</h3>
        </div>
        <p class="field-help" style="margin-bottom:.75rem">Choisis les fiches que tu veux enrichir (une par une depuis la liste, ou raccourci « toutes sans vraie photo »). Le batch tourne en série (1-3 min/fiche). Chaque ligne du journal affiche l'étape en cours, le timer et l'erreur complète si ça casse. <strong>Toutes les modifs sont acceptées</strong> en mode batch (pas de review par fiche).</p>

        <div class="field">
          <label for="batch-picker">Ajouter une fiche à la file</label>
          <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap">
            <select id="batch-picker" style="flex:1;min-width:18rem">
              <option value="">— Chargement du catalogue —</option>
            </select>
            <button class="btn" id="batch-add-btn" disabled>+ Ajouter</button>
            <button class="btn" id="batch-fill-generic-btn" title="Remplit la file avec toutes les fiches sans vraie photo">⚡ Toutes sans vraie photo</button>
            <button class="btn" id="batch-clear-btn">🗑 Vider la file</button>
          </div>
          <p class="field-help">Sélectionne, clique « + Ajouter ». Recommence pour empiler. Les fiches en double sont ignorées.</p>
        </div>

        <div class="field">
          <label style="display:flex;justify-content:space-between;align-items:center">
            <span>File du batch</span>
            <span id="batch-queue-count" style="color:var(--ink-mute);font-weight:400">0 fiche</span>
          </label>
          <div id="batch-queue-list" style="border:1px solid var(--line);border-radius:6px;background:var(--surface-2);max-height:240px;overflow-y:auto">
            <p class="field-help" style="padding:.5rem .65rem;margin:0">File vide. Ajoute des fiches depuis la liste déroulante ou clique « Toutes sans vraie photo ».</p>
          </div>
        </div>

        <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-top:.5rem">
          <button class="btn btn-primary" id="batch-start-btn" disabled>▶ Lancer le batch</button>
          <button class="btn" id="batch-stop-btn" disabled>■ Stop</button>
          <button class="btn" id="batch-zip-btn" disabled>⬇ ZIP du batch</button>
          <span id="batch-progress" class="field-help">En attente.</span>
        </div>

        <div class="field" style="margin-top:.85rem">
          <label>Journal d'exécution</label>
          <div id="batch-log" style="max-height:320px;overflow-y:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface-2)"></div>
          <p class="field-help">Chaque étape s'affiche en temps réel (📥 fetch · 🤖 API · 📝 diff · ✅ terminé · ❌ erreur). Clique « voir l'erreur » pour le message complet, « réessayer » pour relancer cette fiche seule. La console du navigateur (F12) reçoit aussi le JSON original + enrichi pour debug.</p>
        </div>
      </div>
    `;

    // Image drop zone wiring (JSON drop zone removed — catalog list is the only input)
    wireDropZone(root.querySelector('#enricher-drop-image'), root.querySelector('#enricher-file-image'), (f) => loadImage(f));

    root.querySelector('#enricher-enrich-btn').addEventListener('click', runEnrich);
    root.querySelector('#enricher-zip-btn').addEventListener('click', exportZip);

    // Batch mode wiring
    root.querySelector('#batch-start-btn').addEventListener('click', runBatch);
    root.querySelector('#batch-stop-btn').addEventListener('click', stopBatch);
    root.querySelector('#batch-zip-btn').addEventListener('click', exportBatchZip);
    root.querySelector('#batch-add-btn').addEventListener('click', () => {
      const sel = root.querySelector('#batch-picker');
      if (sel && sel.value) addToQueue(sel.value);
    });
    root.querySelector('#batch-fill-generic-btn').addEventListener('click', fillQueueGeneric);
    root.querySelector('#batch-clear-btn').addEventListener('click', clearQueue);
    root.querySelector('#batch-picker').addEventListener('change', (e) => {
      root.querySelector('#batch-add-btn').disabled = !e.target.value;
    });

    // Catalog preload — primary input
    initCatalog(root);
  }

  // -----------------------------------------------------------------------
  // CATALOG PRELOAD (fetch catalog-index.json + searchable list)
  // -----------------------------------------------------------------------

  let catalog = [];
  let catalogFilter = { q: '', category: '' };

  function initCatalog(root) {
    const sel = root.querySelector('#enricher-venue-select');
    const batchSel = root.querySelector('#batch-picker');
    fetch('/catalog-index.json')
      .then(r => r.json())
      .then(data => {
        catalog = data;
        const fillSelect = (target, placeholder) => {
          target.innerHTML = `<option value="">${placeholder}</option>`;
          const byCat = {};
          data.forEach(f => { (byCat[f.category] = byCat[f.category] || []).push(f); });
          Object.keys(byCat).sort().forEach(cat => {
            const group = document.createElement('optgroup');
            group.label = `${cat} (${byCat[cat].length})`;
            byCat[cat].sort((a, b) => a.name.localeCompare(b.name)).forEach(f => {
              const opt = document.createElement('option');
              opt.value = f.slug;
              opt.textContent = `${f.name} — ${f.commune}${f.real ? '' : ' · générique'}`;
              group.appendChild(opt);
            });
            target.appendChild(group);
          });
        };
        fillSelect(sel, '— Sélectionne une fiche —');
        if (batchSel) fillSelect(batchSel, '— Choisis et ajoute à la file —');
        renderQueue();
      })
      .catch(err => {
        sel.innerHTML = '<option value="">Erreur: ' + err.message + '</option>';
        if (batchSel) batchSel.innerHTML = '<option value="">Erreur: ' + err.message + '</option>';
      });

    sel.addEventListener('change', (e) => {
      const slug = e.target.value;
      if (slug) loadFromCatalog(slug);
    });
  }

  function loadFromCatalog(slug) {
    const url = `/Json/${slug}.json`;
    fetch(url)
      .then(r => {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.text();
      })
      .then(txt => {
        const parsed = JSON.parse(txt);
        if (!parsed.slug) throw new Error('JSON sans champ "slug"');
        original = parsed;
        enriched = null;
        changes = [];
        rejected = new Set();
        imageBlob = null;
        document.getElementById('enricher-loaded').textContent = `Chargé du catalogue : ${parsed.slug} (${parsed.commune || '?'})`;
        document.getElementById('enricher-enrich-btn').disabled = false;
        document.getElementById('enricher-diff').innerHTML = '';
        document.getElementById('enricher-zip-btn').disabled = true;
        document.getElementById('enricher-image-loaded').textContent = 'Aucune image chargée';
        setStatus(`Fiche chargée : ${parsed.slug}. Optionnellement glisse une image. Puis clic Enrichir.`);
      })
      .catch(err => {
        setStatus(`Erreur chargement /Json/${slug}.json : ${err.message}`, 'err');
      });
  }

  function wireDropZone(zone, input, onFile) {
    zone.addEventListener('click', (e) => {
      if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') input.click();
    });
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.style.borderColor = 'var(--accent)'; });
    zone.addEventListener('dragleave', () => { zone.style.borderColor = ''; });
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.style.borderColor = '';
      const file = e.dataTransfer.files[0];
      if (file) onFile(file);
    });
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) onFile(file);
    });
  }

  window.StudioEnricher = { mount };
})();
