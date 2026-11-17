/* Direction C, "Rooms": the map follows the room in view, the phone menu closes after a choice,
   and on the article a thin line along the top shows how far through it you are.
   The colour changes themselves are done by shared/mood.js. */
(function () {
  var doc = document, root = doc.documentElement;

  // ---- the map marks the room in view (shared/mood.js says which one)
  var links = Array.prototype.slice.call(doc.querySelectorAll('.c-map a[href^="#"], .c-sheet a[href^="#"]'));
  doc.addEventListener('roomchange', function (e) {
    var room = e.detail && e.detail.room;
    if (!room || !room.id) return;
    links.forEach(function (a) {
      if (a.getAttribute('href') === '#' + room.id) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
  });

  // ---- a change between light and dark: the ground fades quickly while the text switches at the midpoint,
  //      so text never fades through the same grey as its ground (see html.is-crossing in c.css)
  var schemes = window.cSchemes || {}, lastScheme = schemes[root.getAttribute('data-mood')] || null, fadeTimer = null;
  doc.addEventListener('moodchange', function (e) {
    var sc = schemes[e.detail && e.detail.mood];
    if (!sc) return;
    if (lastScheme === null) lastScheme = sc;
    if (sc !== lastScheme) {
      root.classList.add('is-crossing');
      clearTimeout(fadeTimer);
      fadeTimer = setTimeout(function () { root.classList.remove('is-crossing'); }, 700);
    }
    lastScheme = sc;
  });
  var tc = doc.querySelector('meta[name=theme-color][data-follow]');
  if (tc) tc.setAttribute('content', getComputedStyle(root).getPropertyValue('--ground').trim());

  // ---- the Menu button on narrow screens: a popover, closed by Escape, by a choice, or by clicking away
  var sheet = doc.getElementById('c-sheet'), button = doc.querySelector('.c-menu');
  if (sheet && button) {
    var native = 'popover' in HTMLElement.prototype;
    var close = function () {
      if (native) { try { sheet.hidePopover(); } catch (e) {} }
      else { sheet.classList.remove('is-open'); button.setAttribute('aria-expanded', 'false'); }
    };
    if (native) {
      sheet.addEventListener('toggle', function (e) {
        if (e.newState !== 'open') return;
        var first = sheet.querySelector('a[aria-current]') || sheet.querySelector('a');
        if (first) first.focus();
      });
    } else {                                 // an older browser without popover: the same behaviour by hand
      root.classList.add('no-popover');
      button.removeAttribute('popovertarget');
      button.setAttribute('aria-expanded', 'false');
      button.addEventListener('click', function () {
        var open = !sheet.classList.contains('is-open');
        sheet.classList.toggle('is-open', open);
        button.setAttribute('aria-expanded', String(open));
        if (open) { var a = sheet.querySelector('a'); if (a) a.focus(); }
      });
      doc.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sheet.classList.contains('is-open')) { close(); button.focus(); }
      });
    }
    sheet.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a');
      if (!a) return;
      close();
      var href = a.getAttribute('href') || '';
      var t = href.charAt(0) === '#' && href.length > 1 ? doc.getElementById(href.slice(1)) : null;
      if (t) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
    });
    if (!native) {
      doc.addEventListener('click', function (e) {
        if (sheet.classList.contains('is-open') && !sheet.contains(e.target) && !button.contains(e.target)) close();
      });
    }
  }

  // ---- reading progress on the article
  var bar = doc.querySelector('.c-progress'), article = doc.querySelector('main.post article');
  if (bar && article) {
    var queued = false;
    var update = function () {
      queued = false;
      var r = article.getBoundingClientRect(), span = r.height - window.innerHeight;
      var share = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1;
      bar.style.width = (share * 100).toFixed(1) + '%';
    };
    var ask = function () { if (!queued) { queued = true; requestAnimationFrame(update); } };
    window.addEventListener('scroll', ask, { passive: true });
    window.addEventListener('resize', ask);
    update();
  }
})();
