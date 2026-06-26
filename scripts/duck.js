/* duck.js — Bleu canard édition easter egg 🦆
   Drops ONE duck at a random spot on each page load (1-in-4 it peeks from an edge 👀).
   Click → quack: wiggle + "Coin coin !" bubble + a tiny synthesized quack.
   Decorative only: aria-hidden intent, never blocks content, respects reduced-motion,
   and self-disables on the protected partner fiches (belt + braces with the build exclude).
   No image asset, no dependency, no layout shift, no storage. */
(function () {
  // Never on protected partner fiches.
  var BLOCK = ['/chez-nous-a-la-plage', '/chalet-du-tornet'];
  var path = location.pathname || '';
  for (var i = 0; i < BLOCK.length; i++) { if (path.indexOf(BLOCK[i]) !== -1) return; }
  if (window.__bcDuck) return; window.__bcDuck = 1;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', place);
  } else { place(); }

  function place() {
    if (document.getElementById('bc-duck')) return;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

    var d = document.createElement('button');
    d.id = 'bc-duck';
    d.type = 'button';
    d.setAttribute('aria-label', 'Coin coin');
    d.title = 'Coin coin\u00A0!';
    d.textContent = '\uD83E\uDD86'; // 🦆

    var s = d.style;
    s.position = 'fixed';
    s.zIndex = '40';
    s.border = '0';
    s.background = 'transparent';
    s.cursor = 'pointer';
    s.padding = '6px';
    s.lineHeight = '1';
    s.fontSize = (18 + Math.random() * 10).toFixed(0) + 'px';
    s.opacity = '0';
    s.transform = 'translateZ(0)';
    s.transition = 'opacity .6s ease, transform .25s ease';
    s.filter = 'drop-shadow(0 1px 2px rgba(0,0,0,.25))';
    s.webkitTapHighlightColor = 'transparent';

    var top = 8 + Math.random() * 80;   // 8%–88% of viewport height (clears the header)
    var left = 4 + Math.random() * 88;  // 4%–92% of viewport width
    if (Math.random() < 0.25) {         // peek from a random edge 👀
      var edge = Math.floor(Math.random() * 4);
      if (edge === 0) { s.top = '-6px'; s.left = left + '%'; }
      else if (edge === 1) { s.bottom = '-6px'; s.left = left + '%'; }
      else if (edge === 2) { s.left = '-6px'; s.top = top + '%'; }
      else { s.right = '-6px'; s.top = top + '%'; }
    } else { s.top = top + '%'; s.left = left + '%'; }

    d.addEventListener('click', quack);
    document.body.appendChild(d);
    requestAnimationFrame(function () { s.opacity = '0.9'; });

    function quack() {
      if (!reduce) {
        s.transform = 'rotate(-12deg) scale(1.25)';
        setTimeout(function () { s.transform = ''; }, 220);
      }
      bubble('Coin coin\u00A0!');
      try {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        var c = new AC(), o = c.createOscillator(), g = c.createGain();
        o.type = 'sawtooth';
        o.frequency.setValueAtTime(420, c.currentTime);
        o.frequency.exponentialRampToValueAtTime(180, c.currentTime + 0.18);
        g.gain.setValueAtTime(0.07, c.currentTime);
        g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + 0.2);
        o.connect(g); g.connect(c.destination);
        o.start(); o.stop(c.currentTime + 0.2);
      } catch (e) { /* audio blocked — visual is enough */ }
    }

    function bubble(t) {
      var b = document.createElement('span');
      b.textContent = t;
      var r = d.getBoundingClientRect(), bs = b.style;
      bs.position = 'fixed'; bs.zIndex = '41';
      bs.left = Math.min(window.innerWidth - 90, Math.max(6, r.left)) + 'px';
      bs.top = Math.max(6, r.top - 26) + 'px';
      bs.background = '#1F6E78'; bs.color = '#fff';
      bs.font = '600 12px -apple-system,system-ui,Segoe UI,Roboto,sans-serif';
      bs.padding = '3px 8px'; bs.borderRadius = '10px';
      bs.pointerEvents = 'none';
      bs.transition = 'opacity .8s ease, transform .8s ease';
      document.body.appendChild(b);
      requestAnimationFrame(function () { bs.opacity = '0'; bs.transform = 'translateY(-8px)'; });
      setTimeout(function () { b.remove(); }, 900);
    }
  }
})();
