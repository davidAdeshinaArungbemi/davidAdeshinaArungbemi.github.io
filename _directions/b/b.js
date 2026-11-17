/* Direction B, "Four lenses".
   1. The lens bar: choosing a topic gives the whole page that topic's colours, shows every piece that belongs
      to it in each section (and only those), counts what is showing, and links to the topic's page. The choice
      lives in the address (#lens=aesthetics), so a link or a reload brings it back. "All" is the usual selection.
   2. A piece pointed at or focused colours only itself (data-own), never the page: the page's colour is the lens. */
(function () {
  var Mood = window.Mood;

  // ---- 1. the lens
  var bar = document.querySelector('[data-lens]');
  if (bar && Mood) {
    var buttons = Array.prototype.slice.call(bar.querySelectorAll('[data-lens-pick]'));
    var known = Object.create(null);
    buttons.forEach(function (b) { known[b.getAttribute('data-lens-pick')] = b; });
    var sections = Array.prototype.slice.call(document.querySelectorAll('[data-lens-section]')).map(function (el) {
      return {
        el: el,
        pieces: Array.prototype.slice.call(el.querySelectorAll('.item, .pub, .world, .feature')),
        groups: Array.prototype.slice.call(el.querySelectorAll('[data-lens-group]')),
        count: el.querySelector('[data-lens-count]'),
        empty: el.querySelector('[data-lens-empty]')
      };
    });
    var tiles = Array.prototype.slice.call(document.querySelectorAll('.topic[data-topic]'));
    var go = bar.querySelector('[data-lens-go]'), link = bar.querySelector('[data-lens-link]');
    var status = bar.querySelector('[data-lens-status]');

    var belongs = function (piece, slug) {
      return (' ' + (piece.getAttribute('data-topics') || '') + ' ').indexOf(' ' + slug + ' ') > -1;
    };

    var apply = function (slug, write) {
      if (!known[slug]) slug = 'all';
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lens-pick') === slug)); });
      sections.forEach(function (s) {
        var shown = 0;
        s.pieces.forEach(function (p) {
          var on = slug === 'all' ? p.hasAttribute('data-home') : belongs(p, slug);
          p.hidden = !on;
          if (on) shown++;
        });
        s.groups.forEach(function (g) { g.hidden = !g.querySelector('.item:not([hidden])'); });
        if (s.count) { s.count.textContent = shown + ' of ' + s.pieces.length; s.count.hidden = false; }
        if (s.empty) s.empty.hidden = shown > 0;
      });
      tiles.forEach(function (t) { t.classList.toggle('is-lens', t.getAttribute('data-topic') === slug); });
      Mood.rest(slug === 'all' ? 'default' : 'topic-' + slug);
      var b = known[slug];
      if (slug === 'all') { if (go) go.hidden = true; }
      else if (go && link) { link.href = b.getAttribute('data-href'); link.textContent = b.getAttribute('data-title') + ' page →'; go.hidden = false; }
      var g = b.parentNode; if (g && g.scrollWidth > g.clientWidth) g.scrollLeft = b.offsetLeft - g.offsetLeft - 16;
      if (status) status.textContent = 'Showing ' + b.textContent;
      if (write) {
        try { history.replaceState(null, '', slug === 'all' ? location.pathname + location.search : '#lens=' + slug); } catch (e) {}
      }
    };

    buttons.forEach(function (b) {
      b.addEventListener('click', function () { apply(b.getAttribute('data-lens-pick'), true); });
    });
    var fromHash = function () {
      var m = /[#&]lens=([a-z0-9-]+)/.exec(location.hash);
      return m ? m[1] : null;
    };
    window.addEventListener('hashchange', function () { var s = fromHash(); if (s) apply(s, false); });
    bar.hidden = false;
    apply(fromHash() || 'all', false);
  }

  var schemeBtn = document.querySelector('[data-scheme-toggle]');
  if (schemeBtn) schemeBtn.hidden = false;

  // ---- 2. a piece lends only itself its own colours
  Array.prototype.forEach.call(document.querySelectorAll('[data-own]'), function (card) {
    var mood = card.getAttribute('data-own'), timer = 0;
    function on() {
      clearTimeout(timer);
      timer = setTimeout(function () { card.setAttribute('data-mood', mood); }, 100);
    }
    function off() {
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (!card.hasAttribute('data-mood')) return;
        var focused = false;
        try { focused = !!card.querySelector(':focus-visible'); } catch (e) {}
        if (card.matches(':hover') || focused) return;
        card.classList.add('is-fading');                       // keeps the fade going after the mood is gone
        card.removeAttribute('data-mood');
        setTimeout(function () { card.classList.remove('is-fading'); }, 1200);
      }, 100);
    }
    card.addEventListener('pointerenter', function (e) { if (e.pointerType !== 'touch') on(); });
    card.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch') off(); });
    card.addEventListener('focusin', on);
    card.addEventListener('focusout', function (e) { if (!card.contains(e.relatedTarget)) off(); });
  });
})();
