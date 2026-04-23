// studio-render.js — browser port of render-v3.py. Byte-identical output.
(function() {
"use strict";
// render.mjs — JavaScript port of render-v3.py
// Goal: byte-identical output to Python for any unified JSON + lang.


// ─── Constants (auto-generated, same content as Python) ────────────
const CONSTS = window.STUDIO_CONSTS;
const { SITE_NAME, SITE_DOMAIN, SITE_TAGLINE, LANGS, LOCALE_MAP, LANG_NAMES,
        UI_STRINGS, TEMPLATE_STRINGS, FACTS_LABELS, FREE_WORDS_PATTERNS,
        CATEGORY_HEROES, TRANSLATIONS, ES_ADDITIONS, PATH_REWRITES, LANG_ATTR,
        CAT_LABELS, VALID_CATEGORIES } = CONSTS;

// Compile FREE_WORDS regex per language (Python was re.I → JS 'i' flag)
const FREE_WORDS_RE = {};
for (const [lang, pat] of Object.entries(FREE_WORDS_PATTERNS)) {
  FREE_WORDS_RE[lang] = new RegExp(pat, 'i');
}

// ─── HTML escape, matching Python's html.escape(str(s), quote=True) ─
// Python's html.escape default: & < > " ' → &amp; &lt; &gt; &quot; &#x27;
function e(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

function urlFor(lang, slug) {
  return lang === 'fr' ? `https://${SITE_DOMAIN}/${slug}` : `https://${SITE_DOMAIN}/${lang}/${slug}`;
}

function italicizeLastWord(name) {
  const parts = name.split(' ');
  if (parts.length > 1) {
    return parts.slice(0, -1).join(' ') + ` <em>${e(parts[parts.length - 1])}</em>`;
  }
  return `<em>${e(name)}</em>`;
}

// MD5 hash → used for stable hero pick per slug (must match Python's hashlib.md5)
// MD5 implementation matching Python hashlib.md5(s.encode()).hexdigest()
function md5Hex(s) {
  function toBytes(str) {
    return Array.from(new TextEncoder().encode(str));
  }
  function rotl(n, c) { return (n << c) | (n >>> (32 - c)); }
  function md5(bytes) {
    const n = bytes.length;
    const words = new Array((((n + 8) >> 6) + 1) * 16).fill(0);
    for (let i = 0; i < n; i++) words[i >> 2] |= bytes[i] << ((i % 4) * 8);
    words[n >> 2] |= 0x80 << ((n % 4) * 8);
    words[words.length - 2] = n * 8;
    let a = 0x67452301, b = 0xefcdab89, c = 0x98badcfe, d = 0x10325476;
    const S = [[7,12,17,22],[5,9,14,20],[4,11,16,23],[6,10,15,21]];
    const K = [
      0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,
      0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
      0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8,
      0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
      0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,
      0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
      0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,
      0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391
    ];
    for (let g = 0; g < words.length; g += 16) {
      let [aa, bb, cc, dd] = [a, b, c, d];
      for (let i = 0; i < 64; i++) {
        let f, x;
        if (i < 16) { f = (b & c) | (~b & d); x = i; }
        else if (i < 32) { f = (d & b) | (~d & c); x = (5 * i + 1) % 16; }
        else if (i < 48) { f = b ^ c ^ d; x = (3 * i + 5) % 16; }
        else { f = c ^ (b | ~d); x = (7 * i) % 16; }
        const tmp = d;
        d = c; c = b;
        b = b + rotl((a + f + K[i] + words[g + x]) | 0, S[Math.floor(i / 16)][i % 4]) | 0;
        a = tmp;
      }
      a = (a + aa) | 0; b = (b + bb) | 0; c = (c + cc) | 0; d = (d + dd) | 0;
    }
    function toHex(n) {
      let s = '';
      for (let i = 0; i < 4; i++) s += ((n >> (i * 8)) & 0xff).toString(16).padStart(2, '0');
      return s;
    }
    return toHex(a) + toHex(b) + toHex(c) + toHex(d);
  }
  return md5(toBytes(s));
}

function pickHero(slug, category) {
  const photos = CATEGORY_HEROES[category] || CATEGORY_HEROES['parc'];
  // Python: int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(photos)
  // Need big-int mod. Use BigInt.
  const hex = md5Hex(slug);
  const bigInt = BigInt('0x' + hex);
  const idx = Number(bigInt % BigInt(photos.length));
  return photos[idx];
}

// ─── SCHEMA.ORG ────────────────────────────────────────────────────

function buildSchema(d, lang, canonicalUrl, heroUrl) {
  const faqs = (d.faq || []).map(q => ({
    '@type': 'Question',
    'name': q.q,
    'acceptedAnswer': { '@type': 'Answer', 'text': q.a }
  }));
  const amenities = ((d.schema_org || {}).amenities || []).map(a => ({
    '@type': 'LocationFeatureSpecification',
    'name': a,
    'value': true
  }));
  const placeId = `${canonicalUrl}#place`;

  const homeUrl = lang === 'fr' ? `https://${SITE_DOMAIN}/` : `https://${SITE_DOMAIN}/${lang}/`;

  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': `https://${SITE_DOMAIN}/#website`,
        'url': `https://${SITE_DOMAIN}/`,
        'name': SITE_NAME,
        'description': SITE_TAGLINE,
        'publisher': { '@id': `https://${SITE_DOMAIN}/#publisher` },
        'inLanguage': LOCALE_MAP[lang].replace('_', '-'),
        'potentialAction': {
          '@type': 'SearchAction',
          'target': {
            '@type': 'EntryPoint',
            'urlTemplate': `https://${SITE_DOMAIN}/?q={search_term_string}`
          },
          'query-input': 'required name=search_term_string'
        }
      },
      {
        '@type': 'Organization',
        '@id': `https://${SITE_DOMAIN}/#publisher`,
        'name': SITE_NAME,
        'url': `https://${SITE_DOMAIN}/`,
        'logo': { '@type': 'ImageObject', 'url': `https://${SITE_DOMAIN}/logo.png`, 'width': 512, 'height': 512 },
        'sameAs': []
      },
      {
        '@type': 'BreadcrumbList',
        '@id': `${canonicalUrl}#breadcrumb`,
        'itemListElement': [
          { '@type': 'ListItem', 'position': 1, 'name': UI_STRINGS[lang].home, 'item': homeUrl },
          { '@type': 'ListItem', 'position': 2, 'name': d.commune,
            'item': `https://${SITE_DOMAIN}/${d.commune.toLowerCase().replace(/ /g, '-')}` },
          { '@type': 'ListItem', 'position': 3, 'name': d.name }
        ]
      },
      {
        '@type': 'Article',
        '@id': `${canonicalUrl}#article`,
        'isPartOf': { '@id': `https://${SITE_DOMAIN}/#website` },
        'author': { '@id': `https://${SITE_DOMAIN}/#publisher` },
        'publisher': { '@id': `https://${SITE_DOMAIN}/#publisher` },
        'headline': d.meta_title,
        'datePublished': d.date_published || '2026-04-15T10:00:00+02:00',
        'dateModified': d.date_modified || '2026-04-21T10:00:00+02:00',
        'image': [heroUrl],
        'inLanguage': LOCALE_MAP[lang].replace('_', '-'),
        'mainEntityOfPage': canonicalUrl
      },
      {
        '@type': (d.schema_org || {}).type || 'TouristAttraction',
        '@id': placeId,
        'name': d.name,
        'alternateName': d.name_alternates || [],
        'description': d.hero.lead,
        'url': canonicalUrl,
        'image': heroUrl,
        'address': {
          '@type': 'PostalAddress',
          'streetAddress': d.address_street || '',
          'addressLocality': d.commune,
          'postalCode': d.postal_code || '',
          'addressRegion': d.department || 'Haute-Savoie',
          'addressCountry': 'FR'
        },
        'geo': { '@type': 'GeoCoordinates', 'latitude': d.latitude ?? null, 'longitude': d.longitude ?? null },
        'isAccessibleForFree': (d.schema_org || {}).is_free !== undefined ? d.schema_org.is_free : true,
        'publicAccess': (d.schema_org || {}).public_access !== undefined ? d.schema_org.public_access : true,
        'amenityFeature': amenities,
        'openingHoursSpecification': {
          '@type': 'OpeningHoursSpecification',
          'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
          'opens': '00:00',
          'closes': '23:59'
        }
      },
      { '@type': 'FAQPage', '@id': `${canonicalUrl}#faq`, 'mainEntity': faqs }
    ]
  };
  // Python uses json.dumps(..., ensure_ascii=False, indent=2) — JS JSON.stringify mimics that
  return JSON.stringify(schema, null, 2);
}

// ─── RENDER HELPERS ─────────────────────────────────────────────────

function renderFacts(facts, lang) {
  const labels = FACTS_LABELS[lang];
  const rows = [
    [labels.type, facts.type],
    [labels.access, facts.access],
    [labels.commune, facts.commune],
    [labels.difficulty, facts.difficulty],
    [labels.duration, facts.duration],
    [labels.parking, facts.parking],
    [labels.dogs, facts.dogs],
    [labels.stroller, facts.stroller],
    [labels.best_season, facts.best_season]
  ];
  const freeRe = FREE_WORDS_RE[lang];
  const out = [];
  for (const [k, v] of rows) {
    if (!v) continue;
    const free = freeRe.test(v) ? ' free' : '';
    out.push(`<div class="fact"><span class="fact-key">${e(k)}</span><span class="fact-val${free}">${e(v)}</span></div>`);
  }
  return out.join('\n    ');
}

function renderActivities(acts) {
  const out = [];
  for (const a of acts || []) {
    const tag = a.tag ? `<span class="activity-tag">${e(a.tag)}</span>` : '';
    out.push(`  <div class="activity"><div class="activity-head"><h4>${e(a.title)}</h4>${tag}</div><p>${e(a.description)}</p></div>`);
  }
  return out.join('\n');
}

function renderInfoTable(rows) {
  const out = [];
  for (const r of rows || []) {
    if (r.v === null || r.v === undefined) continue;
    out.push(`  <div class="info-row"><div class="k">${e(r.k)}</div><div class="v">${e(r.v)}</div></div>`);
  }
  return out.join('\n');
}

function renderHow(how, lang) {
  const labels = {
    car: UI_STRINGS[lang].by_car,
    public_transport: UI_STRINGS[lang].by_transit,
    bike: UI_STRINGS[lang].by_bike
  };
  const out = [];
  for (const [key, label] of Object.entries(labels)) {
    if (how[key]) out.push(`<h3>${e(label)}</h3>\n<p>${e(how[key])}</p>`);
  }
  return out.join('\n\n');
}

function renderPartners(d, lang) {
  let partners = d.partners || [];
  if (!partners.length) {
    partners = [
      { tier: 'invite', invite_icon: '🍽️', invite_type: 'restaurant',
        invite_title: 'Un restaurant, un bar ?',
        invite_desc: `Vous êtes à ${d.commune} ou à proximité ? Apparaissez ici auprès des visiteurs.` },
      { tier: 'invite', invite_icon: '🥐', invite_type: 'commerce',
        invite_title: 'Une boulangerie, un commerce ?',
        invite_desc: 'Partagez vos horaires et spécialités avec les visiteurs du lieu.' },
      { tier: 'invite', invite_icon: '🏡', invite_type: 'hebergement',
        invite_title: 'Un hébergement proche ?',
        invite_desc: 'Gîte, chambre d\'hôtes, camping, location. Partagez vos disponibilités.' }
    ];
  }

  const becomePartner = UI_STRINGS[lang].become_partner;
  const html = [];
  for (const p of partners) {
    const tier = p.tier || 'invite';
    if (tier === 'partner') {
      html.push(`    <article class="partner-card tier-partner">
      <span class="partner-badge"><svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>Partenaire</span>
      <h4>${e(p.name)}</h4>
      <p>${e(p.description)}</p>
      <a href="${e(p.url)}" class="cta" target="_blank" rel="noopener">${e(p.cta_text || 'Voir le site →')}</a>
    </article>`);
    } else if (tier === 'featured') {
      html.push(`    <article class="partner-card tier-featured">
      <span class="partner-badge">Mis en avant</span>
      <h4>${e(p.name)}</h4>
      <p>${e(p.description)}</p>
      <a href="${e(p.url)}" class="cta" target="_blank" rel="noopener">${e(p.cta_text || 'Voir le site →')}</a>
      <div class="partner-sponsor-tag">Contenu sponsorisé</div>
    </article>`);
    } else {
      const inviteType = p.invite_type || 'partenaire';
      html.push(`    <article class="partner-card tier-invite">
      <div class="partner-invite-icon" aria-hidden="true">${e(p.invite_icon || '📍')}</div>
      <div class="partner-invite-title">${e(p.invite_title || 'Devenez partenaire')}</div>
      <div class="partner-invite-desc">${e(p.invite_desc || 'Faites connaître votre établissement auprès des visiteurs.')}</div>
      <a href="/devenir-partenaire?lieu=${e(d.slug)}&type=${e(inviteType)}" class="partner-invite-cta">${becomePartner}</a>
    </article>`);
    }
  }
  return html.join('\n\n');
}

function renderGallery(d, lang) {
  const photos = d.gallery_photos || [];
  const placeholderSvg = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/></svg>';

  const tiles = [];
  for (let slot = 1; slot <= 6; slot++) {
    if (slot <= photos.length && photos[slot - 1].src) {
      const photo = photos[slot - 1];
      const credit = photo.credit;
      const creditHtml = credit ? `<div class="gallery-credit">📷 ${e(credit)}</div>` : '';
      tiles.push(`    <div class="gallery-tile has-photo" data-slot="${slot}">
      <img src="${e(photo.src)}" alt="${e(photo.alt || '')}" loading="lazy" width="600" height="600">
      ${creditHtml}
    </div>`);
    } else {
      tiles.push(`    <div class="gallery-tile placeholder" data-slot="${slot}">
      ${placeholderSvg}
    </div>`);
    }
  }

  const visited = UI_STRINGS[lang].visited;
  const shareLead = UI_STRINGS[lang].share_photos;
  const shareTail = UI_STRINGS[lang].share_tail;
  const name = e(d.name);

  return `<div class="gallery-wrap reveal">
  <div class="gallery">
${tiles.join('\n')}
  </div>
  <div class="gallery-invite">
    <div class="gallery-invite-icon" aria-hidden="true">📸</div>
    <div class="gallery-invite-body">
      <strong>${visited} ${name}&nbsp;?</strong>
      <p>${shareLead} <a href="mailto:photos@loisirs74.fr?subject=Photos%20—%20${name}">photos@loisirs74.fr</a>. ${shareTail}</p>
    </div>
  </div>
</div>`;
}

function renderFaq(faqs) {
  return (faqs || []).map(q =>
    `<details class="faq-item"><summary>${e(q.q)}</summary><div>${e(q.a)}</div></details>`
  ).join('\n');
}

function buildSourcesBlock(srcs, lang) {
  if (!srcs || !srcs.length) return '';
  const labels = {
    fr: ['Sources', 'Vérifications multi-sources à la date de publication. Les informations peuvent évoluer — pensez à confirmer auprès du gestionnaire officiel avant un déplacement spécifique.'],
    en: ['Sources', 'Cross-checked across multiple sources at publication date. Information may change — confirm with the official operator before a specific visit.'],
    de: ['Quellen', 'Multi-Quellen-Prüfung zum Veröffentlichungsdatum. Angaben können sich ändern — vor einem konkreten Besuch beim offiziellen Betreiber bestätigen.'],
    it: ['Fonti', 'Verifiche multi-fonte alla data di pubblicazione. Le informazioni possono cambiare — confermare presso il gestore ufficiale prima di una visita specifica.'],
    es: ['Fuentes', 'Verificación multi-fuente en la fecha de publicación. La información puede cambiar — confirmar con el gestor oficial antes de una visita concreta.']
  };
  const [title, note] = labels[lang] || labels.fr;
  const out = [`<div class="sources"><strong>${title}</strong><ul>`];
  for (const s of srcs) {
    out.push(`  <li><a href="${e(s.url)}" target="_blank" rel="noopener">${e(s.name)}</a></li>`);
  }
  out.push('</ul>');
  out.push(`<p style="margin-top:0.85rem;font-size:0.78rem;color:var(--muted);">${note}</p>`);
  out.push('</div>');
  return out.join('\n');
}

function renderCrumb(d, lang) {
  const communeSlug = d.commune.toLowerCase().replace(/ /g, '-');
  const base = lang === 'fr' ? '' : `/${lang}`;
  const homeLabels = { fr: "Fil d'Ariane", en: 'Breadcrumb', de: 'Brotkrümel', it: 'Fil di Arianna', es: 'Miga de pan' };
  return `<nav class="crumb" aria-label="${e(homeLabels[lang] || 'Breadcrumb')}">
  <a href="${base}/">${e(UI_STRINGS[lang].home)}</a><span class="sep">›</span>
  <a href="${base}/${communeSlug}">${e(d.commune)}</a><span class="sep">›</span>
  <span aria-current="page">${e(d.name)}</span>
</nav>`;
}

function renderLangSwitchDesktop(slug, active) {
  return LANGS.map(l =>
    `        <a href="${urlFor(l, slug)}"${l === active ? ' aria-current="true"' : ''} hreflang="${l}">${l.toUpperCase()}</a>`
  ).join('\n');
}

function renderLangSwitchMobile(slug, active) {
  return LANGS.map(l =>
    `    <a href="${urlFor(l, slug)}"${l === active ? ' aria-current="true"' : ''} hreflang="${l}">${e(LANG_NAMES[l])}</a>`
  ).join('\n');
}

function renderHreflangs(slug) {
  const out = LANGS.map(l => `<link rel="alternate" hreflang="${l}" href="${urlFor(l, slug)}">`);
  out.push(`<link rel="alternate" hreflang="x-default" href="${urlFor('fr', slug)}">`);
  return out.join('\n');
}

// ─── FLATTEN + LOCALIZE ─────────────────────────────────────────────

function flatten(unified, lang) {
  if (!('i18n' in unified)) return unified; // legacy flat format
  if (!(lang in unified.i18n)) {
    throw new Error(`Lieu "${unified.slug || '?'}" has no i18n block for lang=${lang}`);
  }
  const flat = { ...unified };
  delete flat.i18n;
  delete flat.partners;
  Object.assign(flat, unified.i18n[lang]);
  flat.lang = lang;

  if ('schema_amenities' in flat) {
    flat.schema_org = flat.schema_org || {};
    flat.schema_org.amenities = flat.schema_amenities;
    delete flat.schema_amenities;
  }

  const flatPartners = [];
  for (const p of unified.partners || []) {
    const fp = { ...p };
    delete fp.i18n;
    const plang = (p.i18n || {})[lang] || (p.i18n || {}).fr || {};
    if (p.tier === 'invite') {
      fp.invite_title = plang.title || '';
      fp.invite_desc = plang.desc || '';
    } else {
      fp.description = plang.description || '';
      fp.cta_text = plang.cta_text || 'Voir le site →';
    }
    flatPartners.push(fp);
  }
  flat.partners = flatPartners;
  return flat;
}

function localizeTemplate(htmlStr, lang) {
  if (lang === 'fr') return htmlStr;
  let out = htmlStr;
  const keys = Object.keys(TEMPLATE_STRINGS).sort((a, b) => b.length - a.length);
  for (const src of keys) {
    const trans = TEMPLATE_STRINGS[src][lang];
    if (trans === undefined) continue;
    out = out.split(src).join(trans);  // replaceAll equivalent, matches Python's str.replace
  }
  return out;
}

// ─── ASSEMBLY (buildPage) ──────────────────────────────────────────

// Escape regex specials in a string — used when we need to re.sub on a runtime-built pattern
function escRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function buildPage(d, template, lang) {
  let tpl = template;
  const canonical = urlFor(lang, d.slug);

  // Hero selection
  let heroUrl, heroSrcLocal;
  if (d.hero_image) {
    heroUrl = d.hero_image.startsWith('http') ? d.hero_image : `https://${SITE_DOMAIN}/${d.hero_image}`;
    heroSrcLocal = d.hero_image;
  } else {
    heroUrl = pickHero(d.slug, d.category || 'parc');
    heroSrcLocal = heroUrl;
  }

  const heroAlt = d.hero_alt || `${UI_STRINGS[lang].hero_alt_default}${d.name}`;

  // HEAD
  tpl = tpl.replace(/<html lang="\w+"/, `<html lang="${lang}"`);
  tpl = tpl.replace(/<title>[\s\S]*?<\/title>/, `<title>${e(d.meta_title)}</title>`);
  tpl = tpl.replace(/<meta name="description" content=".*?">/, `<meta name="description" content="${e(d.meta_description)}">`);
  tpl = tpl.replace(/<link rel="canonical" href=".*?">/, `<link rel="canonical" href="${canonical}">`);
  tpl = tpl.replace(
    /<link rel="alternate" hreflang="fr"[\s\S]*?<link rel="alternate" hreflang="x-default" href=".*?">/,
    renderHreflangs(d.slug)
  );

  // OG
  const ogAltLocales = LANGS.filter(l => l !== lang)
    .map(l => `<meta property="og:locale:alternate" content="${LOCALE_MAP[l]}">`)
    .join('\n');
  const ogTitleShort = d.meta_title.split(' · ')[0];
  const og = `<meta property="og:type" content="article">
<meta property="og:title" content="${e(ogTitleShort)}">
<meta property="og:description" content="${e(d.meta_description)}">
<meta property="og:url" content="${canonical}">
<meta property="og:site_name" content="${SITE_NAME}">
<meta property="og:locale" content="${LOCALE_MAP[lang]}">
${ogAltLocales}
<meta property="og:image" content="${heroUrl}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${e(heroAlt)}">
<meta property="article:published_time" content="${d.date_published || '2026-04-15T10:00:00+02:00'}">
<meta property="article:modified_time" content="${d.date_modified || '2026-04-21T10:00:00+02:00'}">
<meta property="article:author" content="${SITE_NAME}">
<meta property="article:section" content="Haute-Savoie">
<meta property="article:tag" content="${e(d.name)}">
<meta property="article:tag" content="${e(d.commune)}">
<meta property="article:tag" content="Loisirs Haute-Savoie">`;
  tpl = tpl.replace(
    /<meta property="og:type"[\s\S]*?<meta property="article:tag" content="Loisirs Haute-Savoie">/,
    og
  );

  const tw = `<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${e(ogTitleShort)}">
<meta name="twitter:description" content="${e(d.meta_description)}">
<meta name="twitter:image" content="${heroUrl}">
<meta name="twitter:image:alt" content="${e(heroAlt)}">`;
  tpl = tpl.replace(
    /<meta name="twitter:card"[\s\S]*?<meta name="twitter:image:alt" content=".*?">/,
    tw
  );

  if (d.latitude && d.longitude) {
    const geo = `<meta name="geo.region" content="FR-74">
<meta name="geo.placename" content="${e(d.commune)}">
<meta name="geo.position" content="${d.latitude};${d.longitude}">
<meta name="ICBM" content="${d.latitude}, ${d.longitude}">`;
    tpl = tpl.replace(
      /<meta name="geo.region"[\s\S]*?<meta name="ICBM" content=".*?">/,
      geo
    );
  }

  tpl = tpl.replace(
    /<link rel="preload" as="image" href=".*?" fetchpriority="high">/,
    `<link rel="preload" as="image" href="${heroSrcLocal}" fetchpriority="high">`
  );

  tpl = tpl.replace(
    /<script type="application\/ld\+json">[\s\S]*?<\/script>/,
    `<script type="application/ld+json">\n${buildSchema(d, lang, canonical, heroUrl)}\n</script>`
  );

  // Lang switchers — preserve opening tag & trailing close
  tpl = tpl.replace(
    /(<div class="lang-switch"[^>]*>)([\s\S]*?)(<\/div>)/,
    `$1\n${renderLangSwitchDesktop(d.slug, lang)}\n      $3`
  );
  tpl = tpl.replace(
    /(<div class="mobile-lang">)([\s\S]*?)(<\/div>)/,
    `$1\n${renderLangSwitchMobile(d.slug, lang)}\n  $3`
  );

  // Breadcrumb
  tpl = tpl.replace(/<nav class="crumb"[\s\S]*?<\/nav>/, renderCrumb(d, lang));

  // Hero
  const heroHtml = `<header class="hero">
  <div class="hero-img">
    <div class="hero-badge">${e(d.hero.badge)}</div>
    <img src="${e(heroSrcLocal)}" alt="${e(heroAlt)}" width="1600" height="900" fetchpriority="high">
  </div>
  <h1 class="hero-title">${italicizeLastWord(d.name)}</h1>
  <p class="hero-lead">${e(d.hero.lead)}</p>
</header>`;
  tpl = tpl.replace(/<header class="hero">[\s\S]*?<\/header>/, heroHtml);

  // Facts
  const ui = UI_STRINGS[lang];
  tpl = tpl.replace(
    /<section class="facts reveal"[^>]*>[\s\S]*?<\/section>/,
    `<section class="facts reveal" aria-label="${e(ui.facts_label)}">\n  <div class="facts-grid">\n    ${renderFacts(d.facts, lang)}\n  </div>\n</section>`
  );

  // Article body
  const body = d.body;
  const name = e(d.name);
  const eventsPara = body.events ? `<p>${e(body.events)}</p>` : '';
  const articleHtml = `<article class="body">

<h2 id="quest-ce-que">${e(ui.h_what_is)} ${name}${e(ui.h_what_is_suffix)}</h2>
${body.what_is}

<h2 id="activites" class="reveal">${e(ui.h_activities)}</h2>
<div class="activities reveal">
${renderActivities(body.activities || [])}
</div>

<h2 id="infos-pratiques" class="reveal">${e(ui.h_practical)}</h2>
<div class="info-table reveal">
${renderInfoTable(body.practical_info || [])}
</div>

<h2 id="acces" class="reveal">${e(ui.h_access)}</h2>
${renderHow(body.how_to_get_there || {}, lang)}

<h2 id="quand-venir" class="reveal">${e(ui.h_when)}</h2>
${body.when_to_visit || ''}

${eventsPara}

<h2 id="ou-manger" class="reveal">${e(ui.h_where_eat)}</h2>

<div class="partners-wrap reveal" aria-label="${e(ui.partners_aria)}">
  <div class="partners-head">
    <span class="partners-hint">${ui.partners_hint}</span>
    <div class="partners-ctrls" role="group" aria-label="${e(ui.partners_ctrls)}">
      <button type="button" class="partners-prev" aria-label="${e(ui.partners_prev)}"><svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg></button>
      <button type="button" class="partners-next" aria-label="${e(ui.partners_next)}"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>
    </div>
  </div>
  <div class="partners" id="partners-scroll">

${renderPartners(d, lang)}

  </div>
</div>

<h2 id="photos" class="reveal">${e(ui.h_photos)} ${name}</h2>
${renderGallery(d, lang)}

<h2 id="faq" class="reveal">${e(ui.h_faq)}</h2>
${renderFaq(d.faq || [])}

${buildSourcesBlock(d.sources || [], lang)}

<div class="meta">
  ${e(ui.meta_published)} ${d.date_published_human || '15 avril 2026'} <span class="sep">·</span> 
  ${e(ui.meta_modified)} ${d.date_modified_human || '21 avril 2026'} <span class="sep">·</span> 
  <a href="/contact?subject=${e(ui.report_subject)}${name}">${e(ui.meta_report)}</a>
</div>

</article>`;

  tpl = tpl.replace(/<article class="body">[\s\S]*?<\/article>\s*(?=<!-- TOC -->)/, articleHtml + '\n\n');

  // Final : localize remaining FR template strings
  tpl = localizeTemplate(tpl, lang);

  return tpl;
}

// ─── PUBLIC API ─────────────────────────────────────────────────────

function renderLieu(unified, template, lang) {
  if (!LANGS.includes(lang)) throw new Error(`Unknown lang: ${lang}`);
  const d = flatten(unified, lang);
  return buildPage(d, template, lang);
}

// ─── INDEX (homepage) BUILDER ──────────────────────────────────────

function accentStrip(s) {
  // Python: unicodedata.NFD + filter combining marks
  // JS equivalent: NFD normalize + strip diacritic range U+0300–U+036F
  return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function renderCard(lieu, lang) {
  const slug = lieu.slug;
  const cats = lieu.categories;
  const i18n = lieu.i18n[lang];
  const name = i18n.name;
  const commune = i18n.commune;
  const primaryCat = cats[0];
  const catLabel = CAT_LABELS[lang][primaryCat];
  const dataName = e(accentStrip(`${name} ${commune}`));
  const dataCommune = e(accentStrip(commune));
  const dataCat = e(cats.join(' '));
  const href = lang === 'fr' ? `/${slug}` : `/${lang}/${slug}`;
  return `<article class="lieu" data-cat="${dataCat}" data-name="${dataName}" data-commune="${dataCommune}">
  <div class="lieu-cat"><span class="lieu-cat-dot"></span>${e(catLabel)}</div>
  <h3 class="lieu-name"><a href="${href}">${e(name)}</a></h3>
  <div class="lieu-commune">${e(commune)}</div>
  <div class="lieu-foot"><span class="lieu-arrow" aria-hidden="true">→</span></div>
</article>`;
}

function renderCardsBlock(lieux, lang) {
  return lieux.map(l => renderCard(l, lang)).join('\n\n');
}

function renderIndexJsonld(lieux, lang) {
  const langCode = { fr: 'fr-FR', en: 'en-GB', de: 'de-DE', it: 'it-IT', es: 'es-ES' }[lang];
  const indexUrl = lang === 'fr' ? 'https://loisirs74.fr/' : `https://loisirs74.fr/${lang}/`;
  const lieuUrl = (slug) => lang === 'fr' ? `https://loisirs74.fr/${slug}` : `https://loisirs74.fr/${lang}/${slug}`;

  const items = lieux.map((l, i) => ({
    '@type': 'ListItem',
    'position': i + 1,
    'url': lieuUrl(l.slug),
    'name': l.i18n[lang].name
  }));

  const collectionId = lang === 'fr' ? 'https://loisirs74.fr/#collection' : `https://loisirs74.fr/${lang}/#collection`;
  const listId = lang === 'fr' ? 'https://loisirs74.fr/#lieux-list' : `https://loisirs74.fr/${lang}/#lieux-list`;

  const graph = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': 'https://loisirs74.fr/#website',
        'url': 'https://loisirs74.fr/',
        'name': 'Loisirs 74',
        'description': 'Guide indépendant des lieux de loisirs publics en Haute-Savoie',
        'publisher': { '@id': 'https://loisirs74.fr/#publisher' },
        'inLanguage': langCode,
        'potentialAction': {
          '@type': 'SearchAction',
          'target': { '@type': 'EntryPoint', 'urlTemplate': `${indexUrl}?q={search_term_string}` },
          'query-input': 'required name=search_term_string'
        }
      },
      {
        '@type': 'Organization',
        '@id': 'https://loisirs74.fr/#publisher',
        'name': 'Loisirs 74',
        'url': 'https://loisirs74.fr/',
        'logo': { '@type': 'ImageObject', 'url': 'https://loisirs74.fr/logo.png', 'width': 512, 'height': 512 }
      },
      {
        '@type': 'CollectionPage',
        '@id': collectionId,
        'url': indexUrl,
        'name': 'Lieux de loisirs publics en Haute-Savoie',
        'description': 'Lieux publics, gratuits ou quasi-gratuits, documentés à partir de sources officielles.',
        'isPartOf': { '@id': 'https://loisirs74.fr/#website' },
        'inLanguage': langCode,
        'mainEntity': { '@id': listId }
      },
      {
        '@type': 'ItemList',
        '@id': listId,
        'name': 'Lieux publiés — Haute-Savoie',
        'numberOfItems': lieux.length,
        'itemListOrder': 'https://schema.org/ItemListOrderAscending',
        'itemListElement': items
      }
    ]
  };
  return JSON.stringify(graph, null, 2);
}

function validateManifest(manifest) {
  if (!manifest.lieux) throw new Error('lieux.json missing "lieux" array.');
  if (!Array.isArray(manifest.lieux)) throw new Error('lieux.json "lieux" must be an array.');

  const seen = new Set();
  for (let i = 0; i < manifest.lieux.length; i++) {
    const l = manifest.lieux[i];
    const where = `lieux[${i}]`;
    for (const k of ['slug', 'categories', 'i18n']) {
      if (!(k in l)) throw new Error(`${where} missing "${k}"`);
    }
    if (seen.has(l.slug)) throw new Error(`Duplicate slug : "${l.slug}"`);
    seen.add(l.slug);

    if (!l.categories.length) throw new Error(`${where} (${l.slug}) has empty categories.`);
    const bad = l.categories.filter(c => !VALID_CATEGORIES.includes(c));
    if (bad.length) throw new Error(`${where} (${l.slug}) : unknown category ${bad}. Valid : ${VALID_CATEGORIES}`);

    for (const lang of ['fr', 'en', 'de', 'it', 'es']) {
      if (!l.i18n[lang]) throw new Error(`${where} (${l.slug}) : missing i18n["${lang}"]`);
      for (const field of ['name', 'commune']) {
        if (!l.i18n[lang][field]) throw new Error(`${where} (${l.slug}) : missing i18n["${lang}"]["${field}"]`);
      }
    }
  }
  return manifest.lieux;
}

// ─── TRANSLATOR (FR index → en/de/it/es indexes) ───────────────────

function translateIndex(srcHtml, lang) {
  let out = srcHtml;

  // 1) html lang
  const [frLang, toLang] = LANG_ATTR[lang];
  out = out.replace(frLang, toLang);

  // 2) move aria-current to target lang entry, strip from FR
  out = out.split(`<a href="/${lang}/" hreflang="${lang}">`).join(`<a href="/${lang}/" aria-current="true" hreflang="${lang}">`);
  out = out.split('<a href="/" aria-current="true" hreflang="fr">').join('<a href="/" hreflang="fr">');

  // 3) path rewrites
  for (const [from, to] of PATH_REWRITES[lang]) {
    out = out.split(from).join(to);
  }

  // 4) translations — longest first to avoid shadowing
  const allKeys = new Set(Object.keys(TRANSLATIONS));
  if (lang === 'es') {
    for (const k of Object.keys(ES_ADDITIONS)) allKeys.add(k);
  }
  const sortedKeys = Array.from(allKeys).sort((a, b) => b.length - a.length);

  for (const src of sortedKeys) {
    let trans;
    if (lang === 'es') {
      trans = ES_ADDITIONS[src];
      if (trans === undefined) trans = (TRANSLATIONS[src] || {})[lang];
    } else {
      trans = (TRANSLATIONS[src] || {})[lang];
    }
    if (trans === undefined || trans === null) continue;
    out = out.split(src).join(trans);
  }

  return out;
}

// ─── INDEX BUILD (main function) ────────────────────────────────────
/**
 * buildIndexes — returns an object mapping output paths to their final HTML.
 * {
 *   'index.html': '...',
 *   'en/index.html': '...',
 *   'de/index.html': '...',
 *   'it/index.html': '...',
 *   'es/index.html': '...',
 * }
 */
function buildIndexes(manifest, indexTemplate) {
  const lieux = validateManifest(manifest);

  const cardsPattern = /<!--CARDS_START-->[\s\S]*?<!--CARDS_END-->/;
  const jsonldPattern = /<script type="application\/ld\+json">[\s\S]*?<\/script>/;

  // --- FR ---
  if (!indexTemplate.includes('<!--CARDS_START-->') || !indexTemplate.includes('<!--CARDS_END-->')) {
    throw new Error('index.html missing <!--CARDS_START--> / <!--CARDS_END--> markers');
  }
  const frStart = indexTemplate.indexOf('<!--CARDS_START-->') + '<!--CARDS_START-->'.length;
  const frEnd = indexTemplate.indexOf('<!--CARDS_END-->');
  const frCardsHtml = '\n' + renderCardsBlock(lieux, 'fr') + '\n\n    ';
  let frOut = indexTemplate.slice(0, frStart) + frCardsHtml + indexTemplate.slice(frEnd);
  const frJsonldBlock = `<script type="application/ld+json">\n${renderIndexJsonld(lieux, 'fr')}\n</script>`;
  frOut = frOut.replace(jsonldPattern, frJsonldBlock);

  const results = { 'index.html': frOut };

  // --- EN/DE/IT/ES : translate the FR rendered output, then swap cards + jsonld ---
  for (const lang of ['en', 'de', 'it', 'es']) {
    // Translate using the ORIGINAL FR TEMPLATE (not frOut), so paths rewrite correctly
    let langHtml = translateIndex(indexTemplate, lang);

    // Swap cards
    const cardsReplacement = `<!--CARDS_START-->\n${renderCardsBlock(lieux, lang)}\n\n    <!--CARDS_END-->`;
    langHtml = langHtml.replace(cardsPattern, cardsReplacement);

    // Swap JSON-LD
    const langJsonldBlock = `<script type="application/ld+json">\n${renderIndexJsonld(lieux, lang)}\n</script>`;
    langHtml = langHtml.replace(jsonldPattern, langJsonldBlock);

    results[`${lang}/index.html`] = langHtml;
  }

  return results;
}

// ─── SITEMAP BUILDER ────────────────────────────────────────────────

function sitemapUrl(lang, suffix) {
  if (lang === 'fr') return `https://loisirs74.fr/${suffix}` || 'https://loisirs74.fr/';
  return `https://loisirs74.fr/${lang}/${suffix}` || `https://loisirs74.fr/${lang}/`;
}

function sitemapAlternates(pathSuffix) {
  const lines = [];
  for (const l of LANGS) {
    const href = pathSuffix
      ? (l === 'fr' ? `https://loisirs74.fr/${pathSuffix}` : `https://loisirs74.fr/${l}/${pathSuffix}`)
      : (l === 'fr' ? 'https://loisirs74.fr/' : `https://loisirs74.fr/${l}/`);
    lines.push(`    <xhtml:link rel="alternate" hreflang="${l}" href="${href}"/>`);
  }
  const xdefault = pathSuffix ? `https://loisirs74.fr/${pathSuffix}` : 'https://loisirs74.fr/';
  lines.push(`    <xhtml:link rel="alternate" hreflang="x-default" href="${xdefault}"/>`);
  return lines.join('\n');
}

function sitemapUrlBlock(lang, pathSuffix, lastmod, changefreq, priority) {
  const loc = pathSuffix
    ? (lang === 'fr' ? `https://loisirs74.fr/${pathSuffix}` : `https://loisirs74.fr/${lang}/${pathSuffix}`)
    : (lang === 'fr' ? 'https://loisirs74.fr/' : `https://loisirs74.fr/${lang}/`);
  return `  <url>
    <loc>${loc}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
${sitemapAlternates(pathSuffix)}
  </url>`;
}

function sitemapStatic(slug, priority, changefreq, lastmod) {
  return `  <url>
    <loc>https://loisirs74.fr/${slug}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

/**
 * buildSitemap — returns XML string for sitemap.xml
 */
function buildSitemap(manifest, today = null) {
  const lieux = manifest.lieux || [];
  const date = today || new Date().toISOString().slice(0, 10);

  const homepagePriority = { fr: '1.0', en: '0.9', de: '0.9', it: '0.9', es: '0.9' };
  const lieuPriority = { fr: '0.8', en: '0.7', de: '0.7', it: '0.7', es: '0.7' };

  const out = [];
  out.push('<?xml version="1.0" encoding="UTF-8"?>');
  out.push('<!--');
  out.push('  Loisirs 74 — sitemap.xml');
  out.push('  Auto-generated by build-sitemap.py — do not hand-edit.');
  out.push('  Every page has 5 languages (fr/en/de/it/es) with hreflang alternates + x-default.');
  out.push(`  Last regenerated : ${date}`);
  out.push('-->');
  out.push('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"');
  out.push('        xmlns:xhtml="http://www.w3.org/1999/xhtml">');
  out.push('');

  out.push('  <!-- ============================================================= -->');
  out.push('  <!-- HOMEPAGES (5 langues)                                          -->');
  out.push('  <!-- ============================================================= -->');
  out.push('');
  for (const lang of LANGS) {
    out.push(sitemapUrlBlock(lang, '', date, 'weekly', homepagePriority[lang]));
    out.push('');
  }

  out.push('  <!-- ============================================================= -->');
  out.push('  <!-- LIEUX PUBLIÉS (5 langues chacun)                               -->');
  out.push('  <!-- ============================================================= -->');
  out.push('');
  for (const lieu of lieux) {
    out.push(`  <!-- ${lieu.slug} -->`);
    for (const lang of LANGS) {
      out.push(sitemapUrlBlock(lang, lieu.slug, date, 'monthly', lieuPriority[lang]));
      out.push('');
    }
  }

  out.push('  <!-- ============================================================= -->');
  out.push('  <!-- PAGES STATIQUES                                                -->');
  out.push('  <!-- ============================================================= -->');
  const statics = [
    ['devenir-partenaire', '0.5', 'monthly'],
    ['mentions-legales-loisirs74-phase1', '0.3', 'yearly'],
    ['politique-confidentialite-loisirs74-phase1', '0.3', 'yearly']
  ];
  for (const [slug, priority, changefreq] of statics) {
    out.push(sitemapStatic(slug, priority, changefreq, date));
    out.push('');
  }

  out.push('</urlset>');
  return out.join('\n');
}



// Expose to browser globals (window)
window.renderLieu = renderLieu;
window.buildIndexes = buildIndexes;
window.buildSitemap = buildSitemap;
window.LANGS = LANGS;

})();
