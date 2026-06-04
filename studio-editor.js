// studio-editor.js — Editor tab for the Studio.
// Loads an existing Json/<slug>.json, presents a form for editing FR fields,
// shows a live preview using studio-render.js, and exports the modified JSON
// as a downloadable file. Non-FR locales and untouched keys are preserved.
//
// Public API:
//   window.StudioEditor.mount(rootEl)  — boots the editor into the given DOM container

(function () {
  'use strict';

  // --------------------------------------------------------------------------
  // STATE
  // --------------------------------------------------------------------------

  let originalFiche = null;   // last loaded JSON, untouched (merge base)
  let editorState = null;     // working copy mutated by form changes
  let previewDebounce = null;

  const PREVIEW_DEBOUNCE_MS = 250;

  // --------------------------------------------------------------------------
  // FORM SPEC — declarative section/field list
  // Each field has: path (dot.notation into i18n.fr or top), type, label, [help]
  // --------------------------------------------------------------------------

  const SECTIONS = [
    {
      title: 'Identité',
      help: 'Slug en lecture seule — voir la note dans le plan pour renommer.',
      fields: [
        { path: 'slug',                 label: 'Slug',          type: 'readonly' },
        { path: 'i18n.fr.name',         label: 'Nom (FR)',      type: 'text' },
        { path: 'commune',              label: 'Commune',       type: 'text' },
        { path: 'postal_code',          label: 'Code postal',   type: 'text' },
        { path: 'category',             label: 'Catégorie',     type: 'text', help: 'attraction / domaine / divers / ...' },
      ],
    },
    {
      title: 'Coordonnées',
      fields: [
        { path: 'latitude',             label: 'Latitude',      type: 'number', step: '0.0001' },
        { path: 'longitude',            label: 'Longitude',     type: 'number', step: '0.0001' },
      ],
    },
    {
      title: 'SEO',
      fields: [
        { path: 'i18n.fr.meta_title',       label: 'Meta title',       type: 'text' },
        { path: 'i18n.fr.meta_description', label: 'Meta description', type: 'textarea', rows: 3 },
      ],
    },
    {
      title: 'Liens',
      fields: [
        { path: 'official_site_url',    label: 'Site officiel',          type: 'url' },
        { path: 'booking_url',          label: 'URL de réservation',     type: 'url' },
        { path: 'booking_domain',       label: 'Domaine de réservation', type: 'text' },
      ],
    },
    {
      title: 'Tarification',
      fields: [
        { path: 'schema_org.is_free',   label: 'Gratuit',         type: 'checkbox' },
        { path: 'price_from',           label: 'Prix à partir de', type: 'number', step: '0.01' },
        { path: 'price_currency',       label: 'Devise',           type: 'text' },
      ],
    },
    {
      title: 'Hero',
      fields: [
        { path: 'hero_image',           label: 'Image hero (chemin /xxx.jpg)', type: 'text' },
        { path: 'hero_credit',          label: 'Crédit photo',                 type: 'text' },
      ],
    },
    {
      title: 'Corps (FR)',
      fields: [
        { path: 'i18n.fr.body.what_is',       label: "Qu'est-ce que (HTML autorisé)", type: 'textarea', rows: 10 },
        { path: 'i18n.fr.when_to_visit',      label: 'Quand y aller',                 type: 'textarea', rows: 5 },
        { path: 'i18n.fr.hero.badge',         label: 'Badge hero',                    type: 'text' },
        { path: 'i18n.fr.hero.lead',          label: 'Accroche hero',                 type: 'textarea', rows: 3 },
      ],
    },
    {
      title: 'Infos pratiques (FR)',
      help: 'Adresse, téléphone, horaires, tarifs, accessibilité… Le k est le libellé, le v la valeur.',
      array: 'i18n.fr.practical_info',
      itemFields: [
        { path: 'k', label: 'Libellé', type: 'text', placeholder: 'Adresse / Téléphone / Horaires…' },
        { path: 'v', label: 'Valeur',  type: 'textarea', rows: 2 },
      ],
    },
    {
      title: 'Activités (FR)',
      help: 'Cards affichées sur la fiche.',
      array: 'i18n.fr.activities',
      itemFields: [
        { path: 'title', label: 'Titre',    type: 'text' },
        { path: 'tag',   label: 'Tag',      type: 'text', placeholder: 'optional, ex: "Point fort"' },
        { path: 'body',  label: 'Description', type: 'textarea', rows: 3 },
      ],
    },
    {
      title: 'FAQ (FR)',
      array: 'i18n.fr.faq',
      itemFields: [
        { path: 'q', label: 'Question', type: 'text' },
        { path: 'a', label: 'Réponse',  type: 'textarea', rows: 3 },
      ],
    },
    {
      title: 'Sources',
      array: 'sources',
      itemFields: [
        { path: '',  label: 'URL', type: 'url' },  // empty path = item is a scalar string
      ],
      isStringArray: true,
    },
    {
      title: 'Partenaires',
      array: 'partners',
      itemFields: [
        { path: 'tier',        label: 'Tier',         type: 'text', placeholder: 'featured / recommended' },
        { path: 'name',        label: 'Nom',          type: 'text' },
        { path: 'type',        label: 'Type',         type: 'text', placeholder: 'restaurant / commerce / hébergement…' },
        { path: 'description', label: 'Description',  type: 'textarea', rows: 2 },
        { path: 'url',         label: 'URL',          type: 'url' },
      ],
    },
  ];

  // --------------------------------------------------------------------------
  // PATH UTILITIES (dot-notation get/set with array creation)
  // --------------------------------------------------------------------------

  function getPath(obj, path) {
    if (!path) return obj;
    const parts = path.split('.');
    let cur = obj;
    for (const p of parts) {
      if (cur == null) return undefined;
      cur = cur[p];
    }
    return cur;
  }

  function setPath(obj, path, value) {
    const parts = path.split('.');
    let cur = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      const p = parts[i];
      if (cur[p] == null || typeof cur[p] !== 'object') cur[p] = {};
      cur = cur[p];
    }
    cur[parts[parts.length - 1]] = value;
  }

  // --------------------------------------------------------------------------
  // FIELD RENDERERS
  // --------------------------------------------------------------------------

  function fieldInput(field, value, onChange) {
    const wrap = document.createElement('div');
    wrap.className = 'field';

    const label = document.createElement('label');
    label.textContent = field.label;
    wrap.appendChild(label);

    let input;
    if (field.type === 'textarea') {
      input = document.createElement('textarea');
      input.rows = field.rows || 4;
      input.value = value == null ? '' : String(value);
    } else if (field.type === 'checkbox') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!value;
    } else if (field.type === 'readonly') {
      input = document.createElement('input');
      input.type = 'text';
      input.value = value == null ? '' : String(value);
      input.readOnly = true;
      input.style.opacity = '.7';
      input.title = "Renommer un slug est hors scope de l'éditeur.";
    } else {
      input = document.createElement('input');
      input.type = field.type === 'url' ? 'url' : field.type === 'number' ? 'number' : 'text';
      if (field.step) input.step = field.step;
      if (field.placeholder) input.placeholder = field.placeholder;
      input.value = value == null ? '' : String(value);
    }

    input.addEventListener('input', () => {
      let v;
      if (field.type === 'checkbox') v = input.checked;
      else if (field.type === 'number') v = input.value === '' ? null : parseFloat(input.value);
      else v = input.value;
      onChange(v);
    });

    wrap.appendChild(input);

    if (field.help) {
      const help = document.createElement('p');
      help.className = 'field-help';
      help.textContent = field.help;
      wrap.appendChild(help);
    }
    return wrap;
  }

  // --------------------------------------------------------------------------
  // ARRAY RENDERER (practical_info / activities / faq / sources / partners)
  // --------------------------------------------------------------------------

  function renderArrayEditor(section, container) {
    const arr = getPath(editorState, section.array);
    if (!Array.isArray(arr)) {
      // Initialize as empty array if missing
      setPath(editorState, section.array, []);
    }
    const items = getPath(editorState, section.array);

    container.innerHTML = '';

    items.forEach((item, idx) => {
      const row = document.createElement('div');
      row.className = 'card array-row';
      row.draggable = true;
      row.dataset.idx = idx;

      const head = document.createElement('div');
      head.className = 'card-head';
      const title = document.createElement('h3');
      title.style.fontSize = '.85rem';
      title.textContent = `#${idx + 1}`;
      head.appendChild(title);

      const actions = document.createElement('div');
      actions.className = 'card-actions';

      const upBtn = document.createElement('button');
      upBtn.type = 'button';
      upBtn.className = 'btn btn-ghost';
      upBtn.textContent = '↑';
      upBtn.disabled = idx === 0;
      upBtn.onclick = () => {
        if (idx === 0) return;
        const a = items.splice(idx, 1)[0];
        items.splice(idx - 1, 0, a);
        renderArrayEditor(section, container);
        schedulePreview();
      };
      actions.appendChild(upBtn);

      const downBtn = document.createElement('button');
      downBtn.type = 'button';
      downBtn.className = 'btn btn-ghost';
      downBtn.textContent = '↓';
      downBtn.disabled = idx === items.length - 1;
      downBtn.onclick = () => {
        if (idx === items.length - 1) return;
        const a = items.splice(idx, 1)[0];
        items.splice(idx + 1, 0, a);
        renderArrayEditor(section, container);
        schedulePreview();
      };
      actions.appendChild(downBtn);

      const delBtn = document.createElement('button');
      delBtn.type = 'button';
      delBtn.className = 'btn btn-ghost';
      delBtn.textContent = '✕';
      delBtn.onclick = () => {
        items.splice(idx, 1);
        renderArrayEditor(section, container);
        schedulePreview();
      };
      actions.appendChild(delBtn);

      head.appendChild(actions);
      row.appendChild(head);

      if (section.isStringArray) {
        const f = section.itemFields[0];
        const fi = fieldInput(f, item, (v) => {
          items[idx] = v;
          schedulePreview();
        });
        row.appendChild(fi);
      } else {
        section.itemFields.forEach((f) => {
          const v = item && typeof item === 'object' ? item[f.path] : undefined;
          const fi = fieldInput(f, v, (val) => {
            if (typeof items[idx] !== 'object' || items[idx] == null) items[idx] = {};
            items[idx][f.path] = val;
            schedulePreview();
          });
          row.appendChild(fi);
        });
      }
      container.appendChild(row);
    });

    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'btn';
    addBtn.textContent = '+ Ajouter';
    addBtn.onclick = () => {
      if (section.isStringArray) items.push('');
      else items.push({});
      renderArrayEditor(section, container);
      schedulePreview();
    };
    container.appendChild(addBtn);
  }

  // --------------------------------------------------------------------------
  // SECTION RENDERER
  // --------------------------------------------------------------------------

  function renderSection(section, container) {
    const wrap = document.createElement('details');
    wrap.className = 'card';
    wrap.open = true;

    const summary = document.createElement('summary');
    summary.style.cursor = 'pointer';
    summary.style.fontWeight = '700';
    summary.style.fontSize = '.95rem';
    summary.textContent = section.title;
    wrap.appendChild(summary);

    if (section.help) {
      const help = document.createElement('p');
      help.className = 'field-help';
      help.style.marginTop = '.5rem';
      help.textContent = section.help;
      wrap.appendChild(help);
    }

    if (section.array) {
      const arrContainer = document.createElement('div');
      wrap.appendChild(arrContainer);
      renderArrayEditor(section, arrContainer);
    } else {
      section.fields.forEach((f) => {
        const v = getPath(editorState, f.path);
        const fi = fieldInput(f, v, (val) => {
          if (f.type === 'readonly') return;
          setPath(editorState, f.path, val);
          schedulePreview();
        });
        wrap.appendChild(fi);
      });
    }

    container.appendChild(wrap);
  }

  // --------------------------------------------------------------------------
  // FORM TOP LEVEL
  // --------------------------------------------------------------------------

  function renderForm() {
    const formEl = document.getElementById('editor-form');
    formEl.innerHTML = '';
    if (!editorState) {
      formEl.innerHTML = '<p class="field-help">Déposer un fichier <code>Json/&lt;slug&gt;.json</code> pour commencer.</p>';
      return;
    }
    SECTIONS.forEach((s) => renderSection(s, formEl));
  }

  // --------------------------------------------------------------------------
  // PREVIEW PIPELINE (uses studio-render.js)
  // --------------------------------------------------------------------------

  function schedulePreview() {
    if (previewDebounce) clearTimeout(previewDebounce);
    previewDebounce = setTimeout(updatePreview, PREVIEW_DEBOUNCE_MS);
  }

  function updatePreview() {
    const iframe = document.getElementById('editor-preview');
    if (!iframe || !editorState) return;
    iframe.srcdoc = renderMiniPreview(editorState);
  }

  // Minimal self-contained preview. Mirrors the key visual blocks of the
  // production renderer (build_lieu_page.py) without trying to be byte-identical.
  // Shows: hero (name + commune + lead), facts row, body, activities, practical_info,
  // FAQ, sources. Enough to sanity-check edits.
  function renderMiniPreview(d) {
    const fr = (d.i18n && d.i18n.fr) || {};
    const name = fr.name || d.slug || '(sans nom)';
    const commune = d.commune || '';
    const lead = (fr.hero && fr.hero.lead) || fr.meta_description || '';
    const badge = (fr.hero && fr.hero.badge) || '';
    const body = (fr.body && fr.body.what_is) || '';
    const acts = fr.activities || [];
    const pi = fr.practical_info || [];
    const faq = fr.faq || [];
    const partners = d.partners || [];
    const sources = d.sources || [];
    const heroSrc = d.hero_image || '/generique-attraction.jpg';
    const isFree = d.schema_org && d.schema_org.is_free;
    const price = d.price_from;
    const cur = d.price_currency || 'EUR';

    return `<!doctype html><html lang="fr"><head><meta charset="utf-8">
<style>
  :root{--ink:#0b0d10;--ink-soft:#3a3f47;--ink-mute:#6a727d;--line:#e3e3dc;--bg:#fafaf7;--surface:#fff;--surface-2:#f3f3ee;--accent:#0a5a3a;--accent-ink:#fff;--radius:14px}
  *,*::before,*::after{box-sizing:border-box}body,h1,h2,h3,p,ul{margin:0}ul{padding-left:0;list-style:none}
  body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;font-size:15px}
  .wrap{max-width:64rem;margin:0 auto;padding:1rem 1.5rem}
  .hero{padding:1.5rem 0 1rem}
  .badge{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-mute);background:var(--surface);border:1px solid var(--line);padding:.25rem .55rem;border-radius:999px;margin-bottom:.5rem}
  h1{font-size:clamp(1.75rem,1.2rem+2vw,2.5rem);letter-spacing:-.02em;font-weight:800;line-height:1.1;margin-bottom:.5rem}
  .commune{color:var(--ink-mute);font-size:.9rem;margin-bottom:.85rem}
  .lead{color:var(--ink-soft);font-size:1.05rem;max-width:36rem;margin-bottom:1rem}
  .hero-img{aspect-ratio:4/3;background:var(--surface-2);border-radius:var(--radius);overflow:hidden;border:1px solid var(--line);margin-bottom:1rem}
  .hero-img img{width:100%;height:100%;object-fit:cover;display:block}
  .facts{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.5rem}
  .fact{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:.45rem .65rem;font-size:.8rem;color:var(--ink-soft)}
  .fact strong{color:var(--ink)}
  section.block{padding:1.25rem 0;border-top:1px solid var(--line)}
  h2{font-size:1.35rem;letter-spacing:-.01em;font-weight:800;margin-bottom:1rem}
  .kicker{font-size:.75rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem}
  .what-is{color:var(--ink-soft);max-width:42rem}
  .what-is p{margin-bottom:.85rem}
  .what-is strong{color:var(--ink)}
  .acts{display:grid;grid-template-columns:1fr;gap:.75rem}
  @media(min-width:600px){.acts{grid-template-columns:1fr 1fr}}
  .act{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem}
  .act h4{font-size:.95rem;font-weight:700;margin-bottom:.25rem;display:flex;justify-content:space-between;gap:.5rem}
  .act .tag{font-size:.65rem;background:var(--surface-2);color:var(--ink-soft);padding:.1rem .4rem;border-radius:6px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
  .act p{color:var(--ink-soft);font-size:.9rem;margin:0}
  .info-table{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}
  .info-row{display:grid;grid-template-columns:1fr;gap:.2rem;padding:.85rem 1.1rem;border-top:1px solid var(--line)}
  .info-row:first-child{border-top:0}
  @media(min-width:600px){.info-row{grid-template-columns:11rem 1fr;gap:1rem}}
  .info-row .k{font-size:.75rem;font-weight:700;color:var(--ink-mute);text-transform:uppercase;letter-spacing:.04em}
  .info-row .v{color:var(--ink-soft);font-size:.9rem;white-space:pre-line}
  details.faq{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:.85rem 1.1rem;margin-bottom:.4rem}
  details.faq summary{cursor:pointer;font-weight:700;font-size:.95rem;color:var(--ink)}
  details.faq>p{margin-top:.5rem;color:var(--ink-soft);font-size:.9rem}
  .partners{display:grid;grid-template-columns:1fr;gap:.5rem}
  @media(min-width:600px){.partners{grid-template-columns:1fr 1fr 1fr}}
  .partner{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:.85rem}
  .partner h4{font-size:.9rem;font-weight:700;margin-bottom:.25rem}
  .partner .desc{font-size:.8rem;color:var(--ink-soft)}
  .partner .tier{font-size:.6rem;background:var(--accent);color:var(--accent-ink);padding:.05rem .35rem;border-radius:4px;font-weight:700;text-transform:uppercase;display:inline-block;margin-bottom:.25rem}
  .partner.recommended .tier{background:var(--surface-2);color:var(--ink-soft)}
  .sources ul{display:flex;flex-direction:column;gap:.35rem;font-size:.8rem}
  .sources a{color:var(--accent);word-break:break-all}
  .preview-banner{background:#fff3cd;color:#664d03;padding:.5rem 1rem;font-size:.75rem;border-bottom:1px solid #ffe69c;text-align:center}
</style></head><body>
<div class="preview-banner">⚠ Aperçu simplifié — la fiche finale est rendue par <code>scripts/build_lieu_page.py</code>.</div>
<div class="wrap">
  <header class="hero">
    ${badge ? `<span class="badge">${esc(badge)}</span>` : ''}
    <h1>${esc(name)}</h1>
    ${commune ? `<div class="commune">📍 ${esc(commune)}</div>` : ''}
    ${lead ? `<p class="lead">${esc(lead)}</p>` : ''}
    <div class="hero-img"><img src="${esc(heroSrc)}" alt="${esc(name)}" onerror="this.style.display='none'"></div>
    <div class="facts">
      ${isFree ? '<span class="fact"><strong>Gratuit</strong></span>' : ''}
      ${(!isFree && price) ? `<span class="fact">Dès <strong>${price} ${esc(cur)}</strong></span>` : ''}
      ${commune ? `<span class="fact">Commune : <strong>${esc(commune)}</strong></span>` : ''}
      ${d.latitude && d.longitude ? `<span class="fact">📍 ${d.latitude.toFixed(4)}, ${d.longitude.toFixed(4)}</span>` : ''}
      ${d.official_site_url ? `<span class="fact">🌐 <a href="${esc(d.official_site_url)}" target="_blank" rel="noopener">site officiel</a></span>` : ''}
    </div>
  </header>

  ${body ? `<section class="block"><div class="kicker">Présentation</div><h2>Qu'est-ce que ${esc(name)}</h2><div class="what-is">${body}</div></section>` : ''}

  ${acts.length ? `<section class="block"><div class="kicker">À faire</div><h2>Ce qu'on peut y faire</h2><div class="acts">${acts.map(a => `
    <div class="act">
      <h4>${esc(a.title || '')}${a.tag ? `<span class="tag">${esc(a.tag)}</span>` : ''}</h4>
      <p>${esc(a.body || a.description || '')}</p>
    </div>`).join('')}</div></section>` : ''}

  ${pi.length ? `<section class="block"><div class="kicker">Pratique</div><h2>Infos pratiques</h2><div class="info-table">${pi.map(p => `
    <div class="info-row"><div class="k">${esc(p.k || '')}</div><div class="v">${esc(p.v || '')}</div></div>`).join('')}</div></section>` : ''}

  ${faq.length ? `<section class="block"><div class="kicker">FAQ</div><h2>Questions fréquentes</h2>${faq.map(q => `
    <details class="faq"><summary>${esc(q.q || '')}</summary><p>${esc(q.a || '')}</p></details>`).join('')}</section>` : ''}

  ${partners.length ? `<section class="block"><div class="kicker">À proximité</div><h2>Partenaires</h2><div class="partners">${partners.map(p => `
    <div class="partner ${(p.tier || 'recommended') === 'featured' ? '' : 'recommended'}">
      ${p.tier ? `<span class="tier">${esc(p.tier)}</span>` : ''}
      <h4>${esc(p.name || '')}</h4>
      ${p.type ? `<div style="font-size:.7rem;color:var(--ink-mute);text-transform:uppercase">${esc(p.type)}</div>` : ''}
      <p class="desc">${esc(p.description || '')}</p>
      ${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener" style="font-size:.75rem;color:var(--accent)">→ visiter</a>` : ''}
    </div>`).join('')}</div></section>` : ''}

  ${sources.length ? `<section class="block sources"><div class="kicker">Sources</div><h2>Sources & vérifications</h2><ul>${sources.map(s => `
    <li><a href="${esc(s)}" target="_blank" rel="noopener">${esc(s)}</a></li>`).join('')}</ul></section>` : ''}
</div>
</body></html>`;

    function esc(s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
  }

  // --------------------------------------------------------------------------
  // LOAD / SAVE
  // --------------------------------------------------------------------------

  function loadFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (!parsed.slug) throw new Error('JSON sans champ "slug" — pas une fiche.');
        originalFiche = parsed;
        editorState = JSON.parse(JSON.stringify(parsed));  // deep clone for editing
        renderForm();
        updateHeader();
        updatePreview();
      } catch (err) {
        alert('Erreur de chargement : ' + err.message);
      }
    };
    reader.readAsText(file);
  }

  function updateHeader() {
    const h = document.getElementById('editor-status');
    if (!h) return;
    if (!editorState) {
      h.textContent = 'Aucune fiche chargée';
      return;
    }
    const name = getPath(editorState, 'i18n.fr.name') || editorState.slug;
    h.innerHTML = `<strong>${escapeHtml(name)}</strong> · <code>${escapeHtml(editorState.slug)}.json</code>`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  }

  function saveJSON() {
    if (!editorState) return alert('Aucune fiche à enregistrer.');
    // Deep-merge editorState into originalFiche so keys not touched by the form
    // (research_log, verify_flags, non-FR locales) are preserved exactly.
    const merged = deepMerge(originalFiche, editorState);
    const blob = new Blob([JSON.stringify(merged, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (editorState.slug || 'lieu') + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function deepMerge(base, override) {
    // base = originalFiche; override = editorState
    // For most keys, override wins. For i18n, merge per-lang so untouched locales survive.
    if (base == null) return override;
    if (Array.isArray(override)) return override;  // arrays are replaced wholesale
    if (typeof override !== 'object') return override;
    const out = { ...base };
    Object.keys(override).forEach((k) => {
      if (k === 'i18n' && base.i18n) {
        out.i18n = { ...base.i18n };
        Object.keys(override.i18n).forEach((lang) => {
          out.i18n[lang] = deepMerge(base.i18n[lang] || {}, override.i18n[lang]);
        });
      } else if (override[k] != null && typeof override[k] === 'object' && !Array.isArray(override[k])) {
        out[k] = deepMerge(base[k] || {}, override[k]);
      } else {
        out[k] = override[k];
      }
    });
    return out;
  }

  // --------------------------------------------------------------------------
  // MOUNT
  // --------------------------------------------------------------------------

  function mount(root) {
    root.innerHTML = `
      <div class="help">
        <strong>Étape 4 — Éditeur.</strong> Charge un fichier <code>Json/&lt;slug&gt;.json</code> existant, modifie les champs FR
        (liens, infos pratiques, activités, FAQ…), prévisualise, télécharge le JSON corrigé. Place-le dans <code>Json/</code>
        et commit. Pour rafraîchir les locales, lance <code>python3 scripts/localize_lieu.py &lt;slug&gt;</code>.
      </div>

      <div class="card" id="editor-loader">
        <div class="card-head">
          <h3>1. Charger une fiche</h3>
          <div class="card-actions">
            <button class="btn btn-primary" id="editor-save-btn">⬇ Télécharger JSON modifié</button>
          </div>
        </div>
        <div id="editor-drop" style="border:2px dashed var(--line);border-radius:10px;padding:1.5rem;text-align:center;cursor:pointer">
          <p style="margin:0;color:var(--ink-mute)">Glisse un fichier <code>.json</code> ici, ou <label style="color:var(--accent);cursor:pointer;text-decoration:underline">parcourir<input type="file" id="editor-file-input" accept="application/json,.json" style="display:none"></label>.</p>
        </div>
        <p id="editor-status" class="field-help" style="margin-top:.65rem">Aucune fiche chargée</p>
      </div>

      <div style="display:grid;grid-template-columns:1fr;gap:1rem" id="editor-panes">
        <div id="editor-form-pane">
          <div id="editor-form"></div>
        </div>
        <div id="editor-preview-pane">
          <div class="card" style="padding:.5rem">
            <div class="card-head" style="margin:0 .5rem .5rem;align-items:center">
              <h3 style="font-size:.85rem">Aperçu (FR)</h3>
              <div class="card-actions">
                <button class="btn btn-ghost" id="editor-preview-refresh" type="button">↻</button>
              </div>
            </div>
            <iframe id="editor-preview" style="width:100%;height:70vh;border:1px solid var(--line);border-radius:8px;background:#fff" sandbox="allow-same-origin"></iframe>
          </div>
        </div>
      </div>

      <style>
        @media(min-width:1200px) {
          #editor-panes { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; }
          #editor-preview-pane { position: sticky; top: 1rem; align-self: start; }
        }
        .array-row[draggable=true] { cursor: grab; }
        .array-row[draggable=true]:active { cursor: grabbing; }
      </style>
    `;

    // Drop zone
    const drop = root.querySelector('#editor-drop');
    const fileInput = root.querySelector('#editor-file-input');
    drop.addEventListener('click', (e) => {
      if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') fileInput.click();
    });
    drop.addEventListener('dragover', (e) => {
      e.preventDefault();
      drop.style.borderColor = 'var(--accent)';
    });
    drop.addEventListener('dragleave', () => {
      drop.style.borderColor = '';
    });
    drop.addEventListener('drop', (e) => {
      e.preventDefault();
      drop.style.borderColor = '';
      const file = e.dataTransfer.files[0];
      if (file) loadFile(file);
    });
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) loadFile(file);
    });

    root.querySelector('#editor-save-btn').addEventListener('click', saveJSON);
    root.querySelector('#editor-preview-refresh').addEventListener('click', updatePreview);

    renderForm();
    updateHeader();
  }

  // Expose
  window.StudioEditor = { mount };
})();
