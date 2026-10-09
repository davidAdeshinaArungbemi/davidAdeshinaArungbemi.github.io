/* Shared page behaviour (loaded with defer):
   - .pins grids get a Pinterest-style masonry: each pin, in order, goes into the shortest column
   - tab buttons filter the Worlds grid or the Articles list by data-kind
   - a.zoom opens an image full size; arrows step through the images currently shown
   - videos marked data-inview play only while on screen, never for reduced motion
   - on the homepage, the top nav underlines the section in view
   - on an article, a thin line along the top shows how far through it you are */
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;
  var zoomOrder = Array.prototype.slice.call(document.querySelectorAll('a.zoom'));   // before the masonry moves anything

  document.querySelectorAll('.pins').forEach(function (grid) {
    var pins = Array.prototype.slice.call(grid.querySelectorAll('.pin'));
    var min = parseFloat(grid.getAttribute('data-min')) || 240, gap = 16, last = '';
    var ratio = function (pin) {
      var m = pin.querySelector('img, video');
      if (!m) return 0;
      var w = +m.getAttribute('width'), h = +m.getAttribute('height');
      return w && h ? h / w : 1;
    };
    var place = function (shown, n, size) {
      pins.forEach(function (p) { grid.appendChild(p); });
      grid.querySelectorAll('.pin-col').forEach(function (c) { c.remove(); });
      var cols = [], h = [];
      for (var i = 0; i < n; i++) {
        var c = document.createElement('div'); c.className = 'pin-col';
        grid.appendChild(c); cols.push(c); h.push(0);
      }
      // Each pin goes into the shortest column, except the last few: for those, try every way of
      // dealing them out and keep the one with the most even bottom edge.
      var shortest = function (t) { return t.indexOf(Math.min.apply(null, t)); };
      var tail = Math.min(4, shown.length), head = shown.length - tail, where = [];
      for (var j = 0; j < head; j++) { var k = shortest(h); where.push(k); h[k] += size[j]; }
      var bottom = function (pick) {
        var t = h.slice();
        pick.forEach(function (k, j) { t[k] += size[head + j]; });
        return Math.max.apply(null, t);
      };
      var g = h.slice(), best = [];
      for (j = head; j < shown.length; j++) { k = shortest(g); best.push(k); g[k] += size[j]; }
      var lowest = bottom(best);
      for (var code = 0; code < Math.pow(n, tail); code++) {
        var pick = [], x = code;
        for (var t = 0; t < tail; t++) { pick.push(x % n); x = Math.floor(x / n); }
        var b = bottom(pick);
        if (b < lowest - 8) { lowest = b; best = pick; }
      }
      shown.forEach(function (p, j) { cols[j < head ? where[j] : best[j - head]].appendChild(p); });
      grid.classList.add('is-masonry');
    };
    var layout = function (force) {
      var n = Math.max(2, Math.floor((grid.clientWidth + gap) / (min + gap)));
      var shown = pins.filter(function (p) { return !p.hidden; });
      var key = n + '|' + shown.length;
      if (!force && key === last) return;
      last = key;
      // First guess each pin's height from its image's shape. Once the columns exist, measure the
      // real heights (captions differ in length) and place again. The image's share is computed
      // rather than measured, so it is right before the image has loaded.
      place(shown, n, shown.map(function (p) { return ratio(p) + 0.25; }));
      place(shown, n, shown.map(function (p) {
        var m = p.querySelector('img, video');
        return m ? p.offsetHeight - m.offsetHeight + ratio(p) * m.offsetWidth + 22 : p.offsetHeight + 22;
      }));
    };
    grid._layout = layout; grid._pins = pins;
    layout(true);
    var timer;
    window.addEventListener('resize', function () { clearTimeout(timer); timer = setTimeout(function () { layout(false); }, 120); });
  });

  // Arriving at images.html#some-piece: scroll to it again now that the columns are built.
  var toHash = function () {
    var target = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) target.scrollIntoView();
  };
  toHash();
  // Text wraps differently once the web fonts arrive, so measure and place once more.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () {
    document.querySelectorAll('.pins.is-masonry').forEach(function (grid) { grid._layout(true); });
    toHash();
  });

  // Tabs filter either a masonry grid (Worlds) or a plain list (Articles) by data-kind
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.pin-tabs button'));
  var filterGrid = document.querySelector('.pins[data-filterable]');
  var filterList = document.querySelector('.rows[data-filterable]');
  var items = filterGrid && filterGrid._pins ? filterGrid._pins
            : filterList ? Array.prototype.slice.call(filterList.children) : null;
  if (tabs.length && items) {
    tabs.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t === b)); });
        items.forEach(function (p) { p.hidden = !(f === 'all' || p.getAttribute('data-kind') === f); });
        if (filterGrid && filterGrid._layout) filterGrid._layout(true);
      });
    });
  }

  var box = document.getElementById('lightbox');
  if (box && zoomOrder.length && typeof box.showModal === 'function') {
    var img = box.querySelector('img'), cap = box.querySelector('.lightbox-cap'), cur = null;
    var visible = function () { return zoomOrder.filter(function (a) { var p = a.closest('.pin'); return !(p && p.hidden); }); };
    var show = function (a) {
      cur = a;
      var fc = a.closest('figure').querySelector('figcaption');
      img.src = a.getAttribute('href');
      img.alt = a.querySelector('img').alt;
      cap.innerHTML = fc ? fc.innerHTML : '';
    };
    var step = function (d) { var v = visible(), i = v.indexOf(cur); show(v[(i + d + v.length) % v.length]); };
    zoomOrder.forEach(function (a) {
      a.addEventListener('click', function (e) { e.preventDefault(); show(a); box.showModal(); });
    });
    box.querySelector('.lightbox-prev').addEventListener('click', function () { step(-1); });
    box.querySelector('.lightbox-next').addEventListener('click', function () { step(1); });
    box.querySelector('.lightbox-close').addEventListener('click', function () { box.close(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });
    box.addEventListener('close', function () { img.removeAttribute('src'); if (cur) cur.focus(); });
  }

  if (!reduceMotion) {
    document.querySelectorAll('video[data-inview]').forEach(function (video) {
      if (!hasIO) { video.play(); return; }
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
          else video.pause();
        });
      }, { threshold: 0.25 }).observe(video);
    });
  }

  var bar = document.querySelector('.read-progress'), article = document.querySelector('.post article');
  if (bar && article) {
    var progress = function () {
      var r = article.getBoundingClientRect(), span = r.height - window.innerHeight;
      bar.style.transform = 'scaleX(' + (span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1) + ')';
    };
    window.addEventListener('scroll', progress, { passive: true });
    window.addEventListener('resize', progress);
    progress();
  }

  var links = Array.prototype.slice.call(document.querySelectorAll('.topnav a[href^="#"]'));
  if (hasIO && links.length) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var nav = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) { l.removeAttribute('aria-current'); });
        var a = byId[en.target.id];
        if (a) a.setAttribute('aria-current', 'location');
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    ['top'].concat(Object.keys(byId)).forEach(function (id) { var el = document.getElementById(id); if (el) nav.observe(el); });
  }
})();
