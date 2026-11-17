/* What the pages do, beyond the shared mood.js, showcase.js and scheme.js:
   1. The topic bar (homepage): choosing a topic shows every piece that belongs to it in each section (and only
      those), counts what is showing, links to the topic's page, and lights the work below the screen in that
      topic's colours. The screen at the top keeps the clip's light: mood.js treats both as rooms (the hero's mood
      follows the clip; the work's mood is set here). The choice lives in the address (#lens=aesthetics).
   2. Filters (Articles, Worlds): show one kind of piece at a time; a Worlds filter can light the page too.
   3. A card pointed at or focused takes its own picture's colours (data-own), never the page's.
   4. Worlds: a picture opens full size in a viewer (arrows step through the pictures showing); videos keep their
      own controls and play by themselves only while on screen, never with reduced motion or a data saver.
   5. Articles: a line along the top shows how far through the article you are.
   Without JavaScript every piece of the homepage selection shows, the bars and filters stay hidden, and videos
   keep their controls. */
(function () {
  var Mood = window.Mood;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  var thrifty = !!(conn && (conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '')));
  var all = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  try {
    // ---- 1. the topic bar
    var bar = document.querySelector('[data-lens]');
    var zone = document.querySelector('[data-lens-room]');
    if (bar && Mood) {
      var buttons = all('[data-lens-pick]', bar);
      var known = Object.create(null);
      buttons.forEach(function (b) { known[b.getAttribute('data-lens-pick')] = b; });
      var sections = all('[data-lens-section]').map(function (el) {
        return {
          pieces: all('.item, .pub, .world, .feature', el),
          groups: all('[data-lens-group]', el),
          count: el.querySelector('[data-lens-count]'),
          empty: el.querySelector('[data-lens-empty]')
        };
      });
      var tiles = all('.topic[data-topic]');
      var go = bar.querySelector('[data-lens-go]'), link = bar.querySelector('[data-lens-link]');
      var status = bar.querySelector('[data-lens-status]');
      var belongs = function (piece, slug) {
        return (' ' + (piece.getAttribute('data-topics') || '') + ' ').indexOf(' ' + slug + ' ') > -1;
      };

      var apply = function (slug, chosen) {
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

        // the work below the screen takes the topic's light; a press shows it at once, wherever the reader is
        var mood = slug === 'all' ? 'default' : 'topic-' + slug;
        if (zone) zone.setAttribute('data-room', mood);
        if (!zone || chosen || zone.classList.contains('is-here')) Mood.rest(mood);

        var b = known[slug];
        if (slug === 'all') { if (go) go.hidden = true; }
        else if (go && link) { link.href = b.getAttribute('data-href'); link.textContent = b.getAttribute('data-title') + ' page →'; go.hidden = false; }
        var g = b.parentNode;
        if (g && g.scrollWidth > g.clientWidth) g.scrollLeft = b.offsetLeft - g.offsetLeft - 16;
        if (status && chosen) status.textContent = 'Showing ' + b.textContent;
        if (chosen) {
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
      window.addEventListener('hashchange', function () {
        var s = fromHash();
        if (s) apply(s, false);
        else if (!location.hash) apply('all', false);          // back to a plain address: back to the homepage selection
      });
      bar.hidden = false;
      apply(fromHash() || 'all', false);
    }
  } catch (e) { if (window.console) console.error(e); }

  try {
    // ---- 2. filters
    all('[data-filters]').forEach(function (group) {
      var choices = all('[data-filter]', group);
      var list = document.querySelector('[data-filterable]');
      if (!list || !choices.length) return;
      var items = Array.prototype.slice.call(list.children);
      group.hidden = false;
      choices.forEach(function (b) {
        b.addEventListener('click', function () {
          var f = b.getAttribute('data-filter');
          choices.forEach(function (t) { t.setAttribute('aria-pressed', String(t === b)); });
          items.forEach(function (p) { p.hidden = !(f === 'all' || p.getAttribute('data-kind') === f); });
          if (Mood && group.hasAttribute('data-filters-light')) Mood.rest(b.getAttribute('data-mood-on') || 'default');
        });
      });
    });
  } catch (e) { if (window.console) console.error(e); }

  try {
    // ---- 3. a card lends only itself its own colours
    all('[data-own]').forEach(function (card) {
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
  } catch (e) { if (window.console) console.error(e); }

  try {
    // ---- 4. Worlds: the full-size viewer
    var box = document.getElementById('lightbox');
    var zooms = all('a.zoom');
    if (box && zooms.length && typeof box.showModal === 'function') {
      var img = box.querySelector('img'), cap = box.querySelector('.lightbox-cap'), cur = null;
      var visible = function () { return zooms.filter(function (a) { return !a.closest('[hidden]'); }); };
      var show = function (a) {
        cur = a;
        var fc = a.closest('figure').querySelector('figcaption');
        img.src = a.getAttribute('href');
        img.alt = a.querySelector('img').alt;
        cap.innerHTML = fc ? fc.innerHTML : '';
      };
      var step = function (d) { var v = visible(), i = v.indexOf(cur); if (v.length) show(v[(i + d + v.length) % v.length]); };
      zooms.forEach(function (a) {
        a.addEventListener('click', function (e) {
          if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button) return;   // "open in a new tab" still works
          e.preventDefault(); show(a); box.showModal();
        });
      });
      box.querySelector('.lightbox-prev').addEventListener('click', function () { step(-1); });
      box.querySelector('.lightbox-next').addEventListener('click', function () { step(1); });
      box.querySelector('.lightbox-close').addEventListener('click', function () { box.close(); });
      box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
      box.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      });
      box.addEventListener('close', function () { img.removeAttribute('src'); if (cur) cur.focus(); });
    }
  } catch (e) { if (window.console) console.error(e); }

  try {
    // ---- 4. Worlds: videos keep their own controls (play, pause, sound off) and play by themselves only while
    //      on screen and while the tab is showing; never with reduced motion or a data saver
    all('video[data-inview]').forEach(function (video) {
      if (reduce.matches || thrifty) return;
      var inView = false, userPaused = false, auto = false;
      video.addEventListener('pause', function () { if (auto) { auto = false; return; } if (inView && !document.hidden) userPaused = true; });
      video.addEventListener('play', function () { userPaused = false; });
      var sync = function () {
        if (inView && !document.hidden && !userPaused && !reduce.matches) {
          var p = video.play();
          if (p && p.catch) p.catch(function () {});
        } else if (!video.paused) { auto = true; video.pause(); }
      };
      document.addEventListener('visibilitychange', sync);
      if (reduce.addEventListener) reduce.addEventListener('change', sync);
      if (!('IntersectionObserver' in window)) { inView = true; sync(); return; }
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { inView = en.isIntersecting; sync(); });
      }, { threshold: 0.25 }).observe(video);
    });
  } catch (e) { if (window.console) console.error(e); }

  try {
    // ---- 5. reading progress on an article
    var line = document.querySelector('.read-progress'), article = document.querySelector('.post article');
    if (line && article) {
      var queued = false;
      var update = function () {
        queued = false;
        var r = article.getBoundingClientRect(), span = r.height - window.innerHeight;
        line.style.transform = 'scaleX(' + (span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1) + ')';
      };
      var ask = function () { if (!queued) { queued = true; requestAnimationFrame(update); } };
      window.addEventListener('scroll', ask, { passive: true });
      window.addEventListener('resize', ask);
      update();
    }
  } catch (e) { if (window.console) console.error(e); }
})();
