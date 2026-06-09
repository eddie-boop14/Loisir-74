// studio-dt-importer.js — Tab 7: import selected DataTourisme candidates.
//
// Workflow:
//   1. Tab loads dt-candidates.json (3056 in-scope DT records not yet in catalog)
//   2. User filters by bucket (high/medium), type, commune, or name search
//   3. User multi-selects rows via checkboxes
//   4. Click "Télécharger ZIP" → ZIP with noms-lieux.txt + candidates.csv + README
//   5. Paste noms-lieux.txt into Tab 1 (Recherche/Creator), then run through Tab 5 (Enricher)
//
// Public API:
//   window.StudioDtImporter.mount(rootEl)

(function () {
  'use strict';

  const DATA_URL = 'dt-candidates.json';
  const STORAGE_KEY = 'loisirs74_dt_selection';
  const RENDER_BATCH = 400;  // initial rows; "Show more" appends RENDER_BATCH at a time

  let dataset = null;          // { generated_at, source, count, rows: [...] }
  let selected = new Set();    // dt_ids
  let filtered = [];           // current filtered rows
  let renderedCount = 0;       // how many rows already in the DOM

  function loadSelection() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) selected = new Set(JSON.parse(raw));
    } catch (e) { /* ignore */ }
  }

  function saveSelection() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...selected]));
    } catch (e) { /* ignore */ }
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function norm(s) {
    return (s || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  // ----------------------------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------------------------

  function buildShell(root) {
    root.innerHTML = `
      <div class="help">
        <strong>Étape 7 — Importer DT.</strong> Sélectionne des lieux issus du flux
        DataTourisme #261672 (Apidae). Télécharge le ZIP, ouvre <code>noms-lieux.txt</code>,
        colle les noms dans l'onglet 1 (Recherche), puis passe les fiches générées dans
        l'onglet 5 (Enrichir).
      </div>

      <div id="dt-status" class="card" style="text-align:center;color:var(--ink-mute)">
        Chargement de <code>dt-candidates.json</code>…
      </div>

      <div id="dt-controls" hidden>
        <div class="card">
          <div class="field-row cols2">
            <div class="field">
              <label for="dt-filter-bucket">Priorité</label>
              <select id="dt-filter-bucket">
                <option value="all">Toutes</option>
                <option value="high" selected>Haute (patrimoine / nature / cuisine)</option>
                <option value="medium">Moyenne (activités / prestataires)</option>
              </select>
            </div>
            <div class="field">
              <label for="dt-filter-type">Type</label>
              <select id="dt-filter-type"><option value="">Tous</option></select>
            </div>
          </div>
          <div class="field-row cols2">
            <div class="field">
              <label for="dt-filter-commune">Commune</label>
              <input type="text" id="dt-filter-commune" placeholder="Annecy, Chamonix, Évian…">
            </div>
            <div class="field">
              <label for="dt-filter-name">Nom (contient)</label>
              <input type="text" id="dt-filter-name" placeholder="lac, château, musée…">
            </div>
          </div>
        </div>

        <div class="card" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem">
          <div style="font-size:.85rem;color:var(--ink-soft)">
            <strong id="dt-count-visible">0</strong> visible(s) ·
            <strong id="dt-count-selected">0</strong> sélectionné(s) ·
            <strong id="dt-count-total">0</strong> au total
          </div>
          <div style="display:flex;gap:.4rem;flex-wrap:wrap">
            <button class="btn" id="dt-select-visible" type="button">Sélectionner visibles</button>
            <button class="btn btn-ghost" id="dt-clear-selection" type="button">Vider sélection</button>
            <button class="btn btn-primary" id="dt-download" type="button" disabled>📦 Télécharger ZIP</button>
          </div>
        </div>

        <div id="dt-list" style="display:flex;flex-direction:column;gap:.4rem"></div>
        <div id="dt-pager" style="text-align:center;padding:1rem" hidden>
          <button class="btn" id="dt-show-more" type="button">Afficher plus (<span id="dt-remaining">0</span> restants)</button>
        </div>
      </div>
    `;
  }

  function rowHtml(row) {
    const checked = selected.has(row.id) ? 'checked' : '';
    const desc = row.desc_fr ? `<div class="dt-row-desc">${escapeHtml(row.desc_fr)}</div>` : '';
    const home = row.homepage
      ? `<a href="${escapeHtml(row.homepage)}" target="_blank" rel="noopener" onclick="event.stopPropagation()" style="color:var(--accent);text-decoration:none">↗ site</a>`
      : '';
    return `
      <label class="dt-row" data-id="${escapeHtml(row.id)}" style="display:flex;gap:.6rem;padding:.65rem .85rem;background:var(--surface);border:1px solid var(--line);border-radius:8px;cursor:pointer;align-items:flex-start">
        <input type="checkbox" data-id="${escapeHtml(row.id)}" ${checked} style="margin-top:.25rem;flex-shrink:0">
        <div style="flex:1;min-width:0">
          <div style="display:flex;flex-wrap:wrap;gap:.45rem;align-items:baseline">
            <strong style="font-size:.92rem">${escapeHtml(row.name)}</strong>
            <span style="color:var(--ink-mute);font-size:.78rem">${escapeHtml(row.commune || '?')}</span>
            ${row.postal ? `<span style="color:var(--ink-mute);font-size:.72rem">(${escapeHtml(row.postal)})</span>` : ''}
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;font-size:.7rem;color:var(--ink-mute);margin-top:.2rem">
            <span style="padding:.1rem .4rem;background:var(--surface-2);border-radius:4px;font-weight:600">${escapeHtml(row.type_primary)}</span>
            <span>DT #${escapeHtml(row.id)}</span>
            ${row.creator ? `<span>· ${escapeHtml(row.creator)}</span>` : ''}
            ${home}
          </div>
          ${desc ? `<div style="font-size:.75rem;color:var(--ink-soft);margin-top:.3rem;line-height:1.35">${escapeHtml(row.desc_fr)}</div>` : ''}
        </div>
      </label>
    `;
  }

  function applyFilters() {
    const bucket = document.getElementById('dt-filter-bucket').value;
    const type = document.getElementById('dt-filter-type').value;
    const commune = norm(document.getElementById('dt-filter-commune').value.trim());
    const name = norm(document.getElementById('dt-filter-name').value.trim());

    filtered = dataset.rows.filter(r => {
      if (bucket !== 'all' && r.type_bucket !== bucket) return false;
      if (type && !r.types.includes(type)) return false;
      if (commune && !norm(r.commune).includes(commune)) return false;
      if (name && !norm(r.name).includes(name)) return false;
      return true;
    });

    renderedCount = 0;
    document.getElementById('dt-list').innerHTML = '';
    renderMore();
    updateCounts();
  }

  function renderMore() {
    const slice = filtered.slice(renderedCount, renderedCount + RENDER_BATCH);
    const html = slice.map(rowHtml).join('');
    document.getElementById('dt-list').insertAdjacentHTML('beforeend', html);
    renderedCount += slice.length;

    const remaining = filtered.length - renderedCount;
    const pager = document.getElementById('dt-pager');
    if (remaining > 0) {
      document.getElementById('dt-remaining').textContent = remaining.toString();
      pager.hidden = false;
    } else {
      pager.hidden = true;
    }
  }

  function updateCounts() {
    document.getElementById('dt-count-visible').textContent = filtered.length;
    document.getElementById('dt-count-selected').textContent = selected.size;
    document.getElementById('dt-count-total').textContent = dataset.count;
    document.getElementById('dt-download').disabled = selected.size === 0;
    document.getElementById('dt-download').textContent =
      selected.size > 0
        ? `📦 Télécharger ZIP (${selected.size})`
        : '📦 Télécharger ZIP';
  }

  function populateTypeFilter() {
    const counts = {};
    dataset.rows.forEach(r => {
      counts[r.type_primary] = (counts[r.type_primary] || 0) + 1;
    });
    const types = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const sel = document.getElementById('dt-filter-type');
    types.forEach(([t, c]) => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = `${t} (${c})`;
      sel.appendChild(opt);
    });
  }

  // ----------------------------------------------------------------------------
  // ZIP DOWNLOAD
  // ----------------------------------------------------------------------------

  function csvEscape(v) {
    const s = String(v == null ? '' : v);
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  }

  async function downloadZip() {
    const rows = dataset.rows.filter(r => selected.has(r.id));
    if (rows.length === 0) return;

    const zip = new JSZip();

    // 1. noms-lieux.txt — paste into Tab 1 (Recherche)
    const names = rows.map(r => {
      // "Name (Commune)" disambiguates similarly-named places
      return r.commune ? `${r.name} (${r.commune})` : r.name;
    }).join('\n') + '\n';
    zip.file('noms-lieux.txt', names);

    // 2. candidates.csv — full reference, one row per selected venue
    const header = ['dt_id', 'name', 'commune', 'postal', 'lat', 'lon',
                    'type_primary', 'type_bucket', 'creator', 'homepage',
                    'suggested_slug', 'desc_fr'];
    const csvLines = [header.join(',')];
    rows.forEach(r => {
      csvLines.push(header.map(k => csvEscape(r[k])).join(','));
    });
    zip.file('candidates.csv', csvLines.join('\n') + '\n');

    // 3. README
    const readme = `# Importer DT — sélection du ${new Date().toISOString().slice(0, 10)}

${rows.length} lieux sélectionnés depuis le flux DataTourisme #261672
(Apidae Tourisme, Licence Ouverte 2.0 Etalab).

## Fichiers

- \`noms-lieux.txt\` — un nom par ligne. À coller dans l'onglet 1 (Recherche)
  du studio pour générer une fiche complète par lieu.
- \`candidates.csv\` — métadonnées complètes : GPS, type, OT créateur, homepage,
  slug suggéré, snippet FR DataTourisme. Pour ta référence pendant l'édition.

## Workflow

1. Ouvre l'onglet 1 (Recherche) du studio.
2. Colle le contenu de \`noms-lieux.txt\` dans le champ "Nom du lieu (1 par ligne)".
3. Lance la recherche — le studio génère un JSON conforme par lieu.
4. Passe chaque JSON dans l'onglet 5 (Enrichir) pour la passe AI complète
   (traductions, FAQ, activités enrichies).
5. Ajoute l'attribution DataTourisme manuellement via \`data_sources[]\` si
   le creator/enricher ne l'a pas inclus :
\`\`\`json
{
  "platform": "DataTourisme",
  "platform_url": "https://www.datatourisme.fr",
  "publisher": "Apidae Tourisme",
  "publisher_url": "https://www.apidae-tourisme.com/",
  "creator": "<OT name from candidates.csv 'creator' column>",
  "license": "Licence Ouverte 2.0 (Etalab)",
  "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence",
  "datatourisme_id": "<dt_id>",
  "fields_used": ["seed_metadata"]
}
\`\`\`
`;
    zip.file('_README.md', readme);

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dt-selection-${rows.length}-${new Date().toISOString().slice(0, 10)}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // ----------------------------------------------------------------------------
  // BOOT
  // ----------------------------------------------------------------------------

  function bindEvents(root) {
    const debounce = (fn, ms = 200) => {
      let t;
      return () => { clearTimeout(t); t = setTimeout(fn, ms); };
    };

    document.getElementById('dt-filter-bucket').addEventListener('change', applyFilters);
    document.getElementById('dt-filter-type').addEventListener('change', applyFilters);
    document.getElementById('dt-filter-commune').addEventListener('input', debounce(applyFilters));
    document.getElementById('dt-filter-name').addEventListener('input', debounce(applyFilters));
    document.getElementById('dt-show-more').addEventListener('click', renderMore);

    // event-delegation on the list for checkbox toggles
    document.getElementById('dt-list').addEventListener('change', e => {
      const cb = e.target.closest('input[type="checkbox"][data-id]');
      if (!cb) return;
      const id = cb.dataset.id;
      if (cb.checked) selected.add(id);
      else selected.delete(id);
      saveSelection();
      updateCounts();
    });

    document.getElementById('dt-select-visible').addEventListener('click', () => {
      filtered.forEach(r => selected.add(r.id));
      saveSelection();
      // sync checkboxes already in DOM
      document.querySelectorAll('#dt-list input[type="checkbox"][data-id]')
        .forEach(cb => { cb.checked = selected.has(cb.dataset.id); });
      updateCounts();
    });

    document.getElementById('dt-clear-selection').addEventListener('click', () => {
      selected.clear();
      saveSelection();
      document.querySelectorAll('#dt-list input[type="checkbox"][data-id]')
        .forEach(cb => { cb.checked = false; });
      updateCounts();
    });

    document.getElementById('dt-download').addEventListener('click', downloadZip);
  }

  async function mount(root) {
    if (!root) return;
    loadSelection();
    buildShell(root);

    try {
      const resp = await fetch(DATA_URL, { cache: 'force-cache' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      dataset = await resp.json();
    } catch (e) {
      document.getElementById('dt-status').innerHTML =
        `<strong style="color:var(--bad)">Erreur de chargement</strong><br><span style="font-size:.8rem">${escapeHtml(e.message)}</span>`;
      return;
    }

    document.getElementById('dt-status').remove();
    document.getElementById('dt-controls').hidden = false;
    populateTypeFilter();
    bindEvents(root);
    applyFilters();
  }

  window.StudioDtImporter = { mount };
})();
