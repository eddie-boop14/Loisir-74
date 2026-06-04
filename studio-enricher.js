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

  async function callAPI(jsonObj) {
    const apiKey = localStorage.getItem(KEY_STORAGE) || '';
    if (!apiKey) throw new Error("Configure la clé API dans l'onglet 1 d'abord.");

    const modelEl = document.getElementById('api-model');
    const model = modelEl ? modelEl.value : 'claude-sonnet-4-5';

    const body = {
      model,
      max_tokens: 32000,
      system: SYSTEM_PROMPT,
      tools: [
        { type: 'web_search_20250305', name: 'web_search' },
      ],
      messages: [
        {
          role: 'user',
          content: 'Voici le JSON existant à enrichir. Retourne le JSON enrichi complet (pas de fences markdown, pas de commentaire).\n\n```json\n' + JSON.stringify(jsonObj, null, 2) + '\n```',
        },
      ],
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

    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (err) {
      throw new Error('JSON enrichi invalide : ' + err.message + '\nRéponse brute (300 premiers chars):\n' + text.slice(0, 300));
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
    const t0 = Date.now();
    try {
      enriched = await callAPI(original);
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
  // MOUNT
  // -----------------------------------------------------------------------

  function mount(root) {
    root.innerHTML = `
      <div class="help">
        <strong>Étape 5 — Enrichir.</strong> Choisis une fiche du catalogue, optionnellement glisse une image hero,
        clic <em>Enrichir</em>. L'IA vérifie via web search, traduit les locales manquantes, étoffe les FAQ/activités/body,
        propose des partenaires. Tu revois chaque champ (accepter/refuser), puis télécharges le ZIP à transmettre au repo.
      </div>

      <div class="card">
        <div class="card-head">
          <h3>1. Choisir une fiche du catalogue</h3>
          <span class="field-help" id="enricher-catalog-status">Chargement du catalogue…</span>
        </div>
        <div class="field-row cols2" style="margin-bottom:.5rem">
          <div class="field">
            <label>Recherche</label>
            <input type="text" id="enricher-catalog-q" placeholder="slug, nom, commune…">
          </div>
          <div class="field">
            <label>Catégorie</label>
            <select id="enricher-catalog-category">
              <option value="">Toutes</option>
            </select>
          </div>
        </div>
        <div style="max-height:380px;overflow-y:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface-2)" id="enricher-catalog-list"></div>
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
    `;

    // Image drop zone wiring (JSON drop zone removed — catalog list is the only input)
    wireDropZone(root.querySelector('#enricher-drop-image'), root.querySelector('#enricher-file-image'), (f) => loadImage(f));

    root.querySelector('#enricher-enrich-btn').addEventListener('click', runEnrich);
    root.querySelector('#enricher-zip-btn').addEventListener('click', exportZip);

    // Catalog preload — primary input
    initCatalog(root);
  }

  // -----------------------------------------------------------------------
  // CATALOG PRELOAD (fetch catalog-index.json + searchable list)
  // -----------------------------------------------------------------------

  let catalog = [];
  let catalogFilter = { q: '', category: '' };

  function initCatalog(root) {
    const status = root.querySelector('#enricher-catalog-status');
    fetch('/catalog-index.json')
      .then(r => r.json())
      .then(data => {
        catalog = data;
        status.textContent = `${catalog.length} fiches`;
        const cats = Array.from(new Set(catalog.map(c => c.category))).sort();
        const sel = root.querySelector('#enricher-catalog-category');
        for (const c of cats) {
          const opt = document.createElement('option');
          opt.value = c; opt.textContent = c;
          sel.appendChild(opt);
        }
        renderCatalogList(root);
      })
      .catch(err => {
        status.textContent = `erreur catalog-index.json : ${err.message}`;
        status.style.color = 'var(--bad)';
      });

    root.querySelector('#enricher-catalog-q').addEventListener('input', (e) => {
      catalogFilter.q = e.target.value.trim().toLowerCase();
      renderCatalogList(root);
    });
    root.querySelector('#enricher-catalog-category').addEventListener('change', (e) => {
      catalogFilter.category = e.target.value;
      renderCatalogList(root);
    });
  }

  function renderCatalogList(root) {
    const wrap = root.querySelector('#enricher-catalog-list');
    wrap.innerHTML = '';
    let list = catalog;
    if (catalogFilter.category) list = list.filter(f => f.category === catalogFilter.category);
    if (catalogFilter.q) list = list.filter(f =>
      f.slug.includes(catalogFilter.q) ||
      f.name.toLowerCase().includes(catalogFilter.q) ||
      f.commune.toLowerCase().includes(catalogFilter.q));
    if (!list.length) {
      wrap.innerHTML = '<p class="field-help" style="padding:.85rem">Aucun résultat.</p>';
      return;
    }
    for (const f of list.slice(0, 200)) {
      const row = document.createElement('button');
      row.type = 'button';
      row.style.display = 'grid';
      row.style.gridTemplateColumns = '36px 1fr auto';
      row.style.gap = '.55rem';
      row.style.alignItems = 'center';
      row.style.width = '100%';
      row.style.padding = '.5rem .65rem';
      row.style.background = 'transparent';
      row.style.border = '0';
      row.style.borderBottom = '1px solid var(--line)';
      row.style.cursor = 'pointer';
      row.style.textAlign = 'left';
      row.onmouseover = () => row.style.background = 'var(--surface)';
      row.onmouseout = () => row.style.background = 'transparent';

      const thumb = document.createElement('div');
      thumb.style.width = '36px';
      thumb.style.height = '36px';
      thumb.style.borderRadius = '5px';
      thumb.style.overflow = 'hidden';
      thumb.style.background = 'var(--bg)';
      thumb.style.border = '1px solid var(--line)';
      if (f.hero) {
        const img = document.createElement('img');
        img.src = f.hero;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.onerror = () => { thumb.innerHTML = ''; };
        thumb.appendChild(img);
      }
      row.appendChild(thumb);

      const info = document.createElement('div');
      info.style.minWidth = '0';
      info.innerHTML = `
        <div style="font-weight:600;font-size:.85rem">${escapeHtml(f.name)}</div>
        <div style="font-size:.7rem;color:var(--ink-mute);font-family:var(--mono)">${escapeHtml(f.slug)} · ${escapeHtml(f.commune)} · ${escapeHtml(f.category)}</div>`;
      row.appendChild(info);

      const pill = document.createElement('span');
      pill.className = 'status ' + (f.real ? 'status-done' : 'status-todo');
      pill.style.fontSize = '.55rem';
      pill.textContent = f.real ? 'photo' : 'générique';
      row.appendChild(pill);

      row.addEventListener('click', () => loadFromCatalog(f.slug));
      wrap.appendChild(row);
    }
    if (list.length > 200) {
      const more = document.createElement('p');
      more.className = 'field-help';
      more.style.padding = '.5rem .85rem';
      more.textContent = `… +${list.length - 200} fiches. Affine la recherche.`;
      wrap.appendChild(more);
    }
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
