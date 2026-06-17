// studio-phototheque.js — Tab 6: pick a better hero photo for any existing fiche.
//
// Workflow:
//   1. On mount, fetch /catalog-index.json
//   2. Render a searchable list of all fiches with current hero thumb + flag
//      "Sur générique" / "Photo réelle"
//   3. Click a fiche → expand inline: parallel Wikimedia + Openverse search,
//      plus a drag-drop slot for a local custom photo
//   4. Pick a photo (Wikimedia, Openverse, or local) → ZIP download with the
//      image file + a small JSON patch describing the hero_image + hero_credit
//      change.
//
// Reuses JSZip (loaded by studio.html for Tab 3).
//
// Public API:
//   window.StudioPhototheque.mount(rootEl)

(function () {
  'use strict';

  const CATALOG_URL = '/catalog-index.json';

  let catalog = [];           // Loaded from CATALOG_URL
  let activeSlug = null;
  // Photothèque only ever shows fiches on generic placeholders — venues with
  // a real photo are skipped (no need to "pick" a random Wikimedia/Openverse
  // result when a real one already exists). Use the Editor (Tab 4) to replace
  // an existing real hero.
  let filter = { q: '', category: '' };

  // ---------------------------------------------------------------------
  // PHOTO SEARCH BACKENDS
  // ---------------------------------------------------------------------

  async function searchWikimedia(name, commune, max = 6) {
    const url = new URL('https://commons.wikimedia.org/w/api.php');
    Object.entries({
      action: 'query', generator: 'search',
      gsrsearch: `${name} ${commune} filetype:bitmap`,
      gsrnamespace: '6', gsrlimit: String(max),
      prop: 'imageinfo', iiprop: 'url|extmetadata', iiurlwidth: '400',
      format: 'json', origin: '*',
    }).forEach(([k, v]) => url.searchParams.set(k, v));
    try {
      const r = await fetch(url);
      if (!r.ok) return [];
      const j = await r.json();
      if (!j.query?.pages) return [];
      return Object.values(j.query.pages)
        .filter(p => p.imageinfo?.[0])
        .map(p => {
          const info = p.imageinfo[0];
          const meta = info.extmetadata || {};
          const license = meta.LicenseShortName?.value || 'unknown';
          const author = (meta.Artist?.value || '').replace(/<[^>]*>/g, '').trim().slice(0, 60);
          return {
            source: 'Wikimedia Commons',
            thumb: info.thumburl || info.url,
            full: info.url,
            credit: `${author || 'unknown'} · ${license} · Wikimedia Commons`,
            license,
          };
        });
    } catch (err) {
      console.error('Wikimedia error:', err);
      return [];
    }
  }

  async function searchOpenverse(name, commune, max = 6) {
    const url = new URL('https://api.openverse.org/v1/images/');
    url.searchParams.set('q', `${name} ${commune}`);
    url.searchParams.set('page_size', String(max));
    url.searchParams.set('license', 'cc0,by,by-sa,pdm');  // commercial-friendly only
    url.searchParams.set('format', 'json');
    try {
      const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
      if (!r.ok) return [];
      const j = await r.json();
      if (!Array.isArray(j.results)) return [];
      return j.results.map(p => {
        const author = p.creator || 'unknown';
        const license = (p.license || '').toUpperCase() + (p.license_version ? ' ' + p.license_version : '');
        const sourceName = p.source || 'Openverse';
        return {
          source: 'Openverse · ' + sourceName,
          thumb: p.thumbnail || p.url,
          full: p.url,
          credit: `${author} · ${license} · ${sourceName} (via Openverse)`,
          license: p.license || 'unknown',
        };
      });
    } catch (err) {
      console.error('Openverse error:', err);
      return [];
    }
  }

  // ---------------------------------------------------------------------
  // CATALOG LIST
  // ---------------------------------------------------------------------

  function fiches() {
    // Default view: only fiches still on generic placeholders (the "to do"
    // list). When the user picks a category, show ALL fiches in it — including
    // ones that already have a real hero — so the existing photo is visible
    // and the user can decide whether to replace it.
    let list = filter.category
      ? catalog.filter(f => f.category === filter.category)
      : catalog.filter(f => !f.real);
    if (filter.q) {
      const q = filter.q.toLowerCase();
      list = list.filter(f =>
        f.slug.includes(q) ||
        f.name.toLowerCase().includes(q) ||
        f.commune.toLowerCase().includes(q));
    }
    // Sort: fiches on generic first (the ones needing attention), then real-photo fiches
    list.sort((a, b) => (a.real === b.real ? 0 : a.real ? 1 : -1));
    return list;
  }

  function renderList() {
    const wrap = document.getElementById('phototheque-list');
    wrap.innerHTML = '';
    const list = fiches();
    const count = document.getElementById('phototheque-count');
    if (count) count.textContent = `${list.length} fiches`;

    for (const f of list) {
      const row = document.createElement('div');
      row.className = 'card phototheque-row';
      row.dataset.slug = f.slug;
      row.style.padding = '.65rem';

      const head = document.createElement('div');
      head.style.display = 'grid';
      head.style.gridTemplateColumns = '48px 1fr auto';
      head.style.gap = '.65rem';
      head.style.alignItems = 'center';
      head.style.cursor = 'pointer';

      // Current hero thumb
      const thumb = document.createElement('div');
      thumb.style.width = '48px';
      thumb.style.height = '48px';
      thumb.style.borderRadius = '6px';
      thumb.style.overflow = 'hidden';
      thumb.style.background = 'var(--surface-2)';
      thumb.style.border = '1px solid var(--line)';
      thumb.style.flexShrink = '0';
      if (f.hero) {
        const img = document.createElement('img');
        img.src = f.hero;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.onerror = () => { thumb.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--ink-mute);font-size:.6rem">⚠</div>'; };
        thumb.appendChild(img);
      }
      head.appendChild(thumb);

      // Info
      const info = document.createElement('div');
      info.style.minWidth = '0';
      info.innerHTML = `
        <div style="font-weight:700;font-size:.9rem;line-height:1.25">${escapeHtml(f.name)}</div>
        <div style="font-size:.72rem;color:var(--ink-mute);margin-top:.15rem">
          <code>${escapeHtml(f.slug)}</code> · ${escapeHtml(f.commune || '?')} · ${escapeHtml(f.category)}
        </div>`;
      head.appendChild(info);

      // Status pill
      const pill = document.createElement('span');
      pill.className = 'status ' + (f.real ? 'status-done' : 'status-todo');
      pill.textContent = f.real ? 'photo réelle' : 'générique';
      head.appendChild(pill);

      row.appendChild(head);

      // Expandable detail panel (rendered on click)
      const detail = document.createElement('div');
      detail.style.display = 'none';
      detail.style.marginTop = '.75rem';
      detail.style.paddingTop = '.75rem';
      detail.style.borderTop = '1px solid var(--line)';
      row.appendChild(detail);

      head.addEventListener('click', () => {
        const expanded = detail.style.display === 'block';
        // Close any other open row
        document.querySelectorAll('.phototheque-row').forEach(r => {
          const d = r.querySelector('div[style*="display: block"]');
          if (d) d.style.display = 'none';
        });
        if (expanded) {
          detail.style.display = 'none';
          activeSlug = null;
        } else {
          detail.style.display = 'block';
          activeSlug = f.slug;
          openDetail(f, detail);
        }
      });

      wrap.appendChild(row);
    }
  }

  // ---------------------------------------------------------------------
  // DETAIL PANEL (Wikimedia + Openverse + custom upload)
  // ---------------------------------------------------------------------

  function openDetail(f, panel) {
    panel.innerHTML = `
      <div class="cols" style="margin-top:0">
        <div class="col">
          <div class="col-head">
            <h4>Wikimedia Commons</h4>
            <span class="badge" id="ph-wm-${f.slug}-status">recherche…</span>
          </div>
          <div class="grid" id="ph-wm-${f.slug}-grid"></div>
        </div>
        <div class="col">
          <div class="col-head">
            <h4>Openverse</h4>
            <span class="badge" id="ph-ov-${f.slug}-status">recherche…</span>
          </div>
          <div class="grid" id="ph-ov-${f.slug}-grid"></div>
        </div>
      </div>

      <div class="card" style="margin-top:.85rem;background:var(--surface-2)">
        <div class="card-head">
          <h3 style="font-size:.85rem">Ou : image perso</h3>
        </div>
        <div id="ph-drop-${f.slug}" style="border:2px dashed var(--line);border-radius:8px;padding:1rem;text-align:center;cursor:pointer;font-size:.8rem;color:var(--ink-mute)">
          Glisse une image ici, ou
          <label style="color:var(--accent);cursor:pointer;text-decoration:underline">parcourir<input type="file" accept="image/*" id="ph-file-${f.slug}" style="display:none"></label>
        </div>
        <p class="field-help" id="ph-local-${f.slug}" style="margin-top:.5rem">Aucune image perso.</p>
      </div>

      <div style="margin-top:.85rem;display:flex;gap:.5rem;align-items:center;justify-content:flex-end;flex-wrap:wrap">
        <p class="field-help" id="ph-selected-${f.slug}" style="margin:0;flex:1">Aucune photo sélectionnée.</p>
        <button class="btn btn-primary" id="ph-zip-${f.slug}" disabled>⬇ Télécharger ZIP</button>
      </div>
    `;

    const slug = f.slug;
    let selected = null;        // {source, thumb, full, credit} for picked online photo
    let localBlob = null;       // user-dropped image
    let localExt = 'jpg';

    // Run both searches in parallel
    runSearch(f, 'wm', searchWikimedia);
    runSearch(f, 'ov', searchOpenverse);

    function runSearch(f, prefix, fn) {
      fn(f.name, f.commune, 6).then(results => {
        const status = document.getElementById(`ph-${prefix}-${f.slug}-status`);
        const grid = document.getElementById(`ph-${prefix}-${f.slug}-grid`);
        if (!grid) return;
        if (!results.length) {
          status.textContent = 'aucun résultat';
          return;
        }
        status.textContent = `${results.length} résultats`;
        for (const r of results) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'thumb';
          btn.title = r.credit;
          btn.innerHTML = `
            <img src="${attr(r.thumb)}" alt="" loading="lazy" onerror="this.style.display='none'">
            <div class="credit">${escapeHtml(r.credit)}</div>
          `;
          btn.addEventListener('click', () => {
            // Toggle selection
            document.querySelectorAll(`#ph-${prefix}-${f.slug}-grid .thumb,#ph-${prefix === 'wm' ? 'ov' : 'wm'}-${f.slug}-grid .thumb`).forEach(t => t.classList.remove('selected'));
            btn.classList.add('selected');
            selected = r;
            localBlob = null;  // online wins over local once picked
            document.getElementById(`ph-local-${slug}`).textContent = 'Aucune image perso.';
            updateStatus();
          });
          grid.appendChild(btn);
        }
      });
    }

    // Local drop handling
    const drop = document.getElementById(`ph-drop-${slug}`);
    const fileInput = document.getElementById(`ph-file-${slug}`);
    drop.addEventListener('click', (e) => {
      if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') fileInput.click();
    });
    drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.style.borderColor = 'var(--accent)'; });
    drop.addEventListener('dragleave', () => { drop.style.borderColor = 'var(--line)'; });
    drop.addEventListener('drop', (e) => {
      e.preventDefault();
      drop.style.borderColor = 'var(--line)';
      const file = e.dataTransfer.files[0];
      if (file) loadLocal(file);
    });
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) loadLocal(file);
    });

    function loadLocal(file) {
      if (!/^image\//.test(file.type)) return alert('Pas une image.');
      localBlob = file;
      localExt = (file.name.split('.').pop() || 'jpg').toLowerCase();
      if (!['jpg', 'jpeg', 'png', 'webp'].includes(localExt)) localExt = 'jpg';
      // Clear any online selection
      document.querySelectorAll(`#ph-wm-${slug}-grid .thumb,#ph-ov-${slug}-grid .thumb`).forEach(t => t.classList.remove('selected'));
      selected = null;
      document.getElementById(`ph-local-${slug}`).textContent = `Image perso : ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
      updateStatus();
    }

    function updateStatus() {
      const sel = document.getElementById(`ph-selected-${slug}`);
      const btn = document.getElementById(`ph-zip-${slug}`);
      if (localBlob) {
        sel.textContent = `Sélection : image perso (${localBlob.name})`;
        btn.disabled = false;
      } else if (selected) {
        sel.innerHTML = `Sélection : <strong>${escapeHtml(selected.source)}</strong> · ${escapeHtml(selected.credit.slice(0, 80))}`;
        btn.disabled = false;
      } else {
        sel.textContent = 'Aucune photo sélectionnée.';
        btn.disabled = true;
      }
    }

    document.getElementById(`ph-zip-${slug}`).addEventListener('click', async () => {
      if (typeof JSZip === 'undefined') return alert('JSZip non chargé.');
      const zip = new JSZip();

      let heroImageRef, heroCredit, imageBytes, imageExt;

      if (localBlob) {
        imageBytes = await localBlob.arrayBuffer();
        imageExt = localExt;
        heroImageRef = `/${slug}-hero.${imageExt}`;
        heroCredit = null;
      } else if (selected) {
        // Fetch the full-res image
        try {
          const r = await fetch(selected.full);
          if (!r.ok) throw new Error('HTTP ' + r.status);
          imageBytes = await r.arrayBuffer();
          // Try to infer extension from full URL
          const m = selected.full.match(/\.(jpe?g|png|webp|gif)(?:\?|$)/i);
          imageExt = m ? m[1].toLowerCase().replace('jpeg', 'jpg') : 'jpg';
          heroImageRef = `/${slug}-hero.${imageExt}`;
          heroCredit = selected.credit;
        } catch (err) {
          return alert("Téléchargement de l'image échoué : " + err.message);
        }
      } else {
        return alert("Aucune sélection.");
      }

      zip.file(`${slug}-hero.${imageExt}`, imageBytes);
      // Canonical dotted-path patch (SPEC studio-data-safety §4.1) so the single
      // Python ingress applies it. `source_url` is provenance only — kept at top
      // level (apply_studio_patch reads `patch`), never written into the fiche.
      const patchDoc = {
        slug,
        source: 'studio-phototheque',
        base_head: null,
        source_url: selected ? selected.full : null,
        patch: {
          hero_image: heroImageRef,
          hero_credit: heroCredit,
        },
        delete: [],
      };
      zip.file(`${slug}.studio-patch.json`, JSON.stringify(patchDoc, null, 2) + '\n');
      const readme = [
        `# Photo patch: ${slug}`,
        ``,
        `From Loisirs74 Studio · Photothèque (Tab 6).`,
        `Source: ${selected ? selected.source : 'local upload'}`,
        `Credit: ${heroCredit || '(none / local file)'}`,
        ``,
        `## Integration`,
        `1. git pull --ff-only`,
        `2. Drop ${slug}-hero.${imageExt} into the repo root.`,
        `3. Run: python3 scripts/apply_studio_patch.py ${slug}.studio-patch.json`,
        `        (preview with --dry-run; never cp a full file over Json/)`,
        `4. Run: python3 scripts/build_all.py --no-site   (re-render + gates)`,
        `5. Commit + push.`,
      ].join('\n');
      zip.file('README.txt', readme);

      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      a.href = url;
      a.download = `photo-${slug}-${date}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ---------------------------------------------------------------------
  // UTIL
  // ---------------------------------------------------------------------

  function attr(s) {
    return String(s == null ? '' : s).replace(/"/g, '&quot;');
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // ---------------------------------------------------------------------
  // MOUNT
  // ---------------------------------------------------------------------

  function mount(root) {
    root.innerHTML = `
      <div class="help">
        <strong>Étape 6 — Photothèque.</strong> Par défaut : fiches encore sur photo générique. Pick une catégorie dans le sélecteur ci-dessous pour voir TOUTES les fiches de cette catégorie — y compris celles qui ont déjà une vraie photo (vignette visible, badge "photo réelle"). Recherche parallèle Wikimedia Commons + Openverse, ou glisse ta propre photo. Clic vignette → ZIP avec image + patch JSON.
      </div>

      <div class="card">
        <div class="card-head">
          <h3>Fiches</h3>
          <span class="field-help" id="phototheque-count">…</span>
        </div>
        <div class="field-row cols2" style="margin-bottom:0">
          <div class="field">
            <label>Recherche</label>
            <input type="text" id="phototheque-q" placeholder="slug, nom, commune…">
          </div>
          <div class="field">
            <label>Catégorie (pick → voir toutes, photo réelle incluse)</label>
            <select id="phototheque-category">
              <option value="">Toutes (génériques seulement)</option>
            </select>
          </div>
        </div>
      </div>

      <div id="phototheque-list"></div>
      <p class="field-help" id="phototheque-loading">Chargement du catalogue…</p>
    `;

    fetch(CATALOG_URL)
      .then(r => r.json())
      .then(data => {
        catalog = data;
        document.getElementById('phototheque-loading').remove();
        // Populate category dropdown
        const cats = Array.from(new Set(catalog.map(c => c.category))).sort();
        const sel = document.getElementById('phototheque-category');
        for (const c of cats) {
          const opt = document.createElement('option');
          opt.value = c; opt.textContent = c;
          sel.appendChild(opt);
        }
        renderList();
      })
      .catch(err => {
        const el = document.getElementById('phototheque-loading');
        if (el) {
          el.textContent = `Erreur chargement catalog-index.json : ${err.message}. Lance "python3 scripts/build_catalog_index.py" pour le générer.`;
          el.style.color = 'var(--bad)';
        }
      });

    root.querySelector('#phototheque-q').addEventListener('input', (e) => {
      filter.q = e.target.value.trim();
      renderList();
    });
    root.querySelector('#phototheque-category').addEventListener('change', (e) => {
      filter.category = e.target.value;
      renderList();
    });
  }

  window.StudioPhototheque = { mount };
})();
