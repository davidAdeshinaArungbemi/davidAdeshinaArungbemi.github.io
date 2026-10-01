/* Shared page behaviour (loaded with defer):
   - .pins grids get a Pinterest-style masonry: each pin, in order, goes into the shortest column
   - the images page's tabs filter the pins
   - a.zoom opens an image full size; arrows step through the images currently shown
   - videos marked data-inview play only while on screen, never for reduced motion
   - on the homepage, the top nav underlines the section in view */
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;
  var zoomOrder = Array.prototype.slice.call(document.querySelectorAll('a.zoom'));   // before the masonry moves anything

  document.querySelectorAll('.pins').forEach(function (grid) {
    var pins = Array.prototype.slice.call(grid.querySelectorAll('.pin'));
    var min = parseFloat(grid.getAttribute('data-min')) || 240, gap = 16, last = '';
    var ratio = function (pin) {
      var m = pin.querySelector('img, video'), w = +m.getAttribute('width'), h = +m.getAttribute('height');
      return w && h ? h / w : 1;
    };
    var layout = function (force) {
      var n = Math.max(2, Math.floor((grid.clientWidth + gap) / (min + gap)));
      var shown = pins.filter(function (p) { return !p.hidden; });
      var key = n + '|' + shown.length;
      if (!force && key === last) return;
      last = key;
      pins.forEach(function (p) { grid.appendChild(p); });
      grid.querySelectorAll('.pin-col').forEach(function (c) { c.remove(); });
      var cols = [], h = [];
      for (var i = 0; i < n; i++) {
        var c = document.createElement('div'); c.className = 'pin-col';
        grid.appendChild(c); cols.push(c); h.push(0);
      }
      shown.forEach(function (p) {
        var k = h.indexOf(Math.min.apply(null, h));
        cols[k].appendChild(p); h[k] += ratio(p) + 0.25;
      });
      grid.classList.add('is-masonry');
    };
    grid._layout = layout; grid._pins = pins;
    layout(true);
    var timer;
    window.addEventListener('resize', function () { clearTimeout(timer); timer = setTimeout(function () { layout(false); }, 120); });
  });

  // Arriving at images.html#some-piece: scroll to it again now that the columns are built.
  if (location.hash) {
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) target.scrollIntoView();
  }

  var tabs = Array.prototype.slice.call(document.querySelectorAll('.pin-tabs button'));
  var filterGrid = document.querySelector('.pins[data-filterable]');
  if (tabs.length && filterGrid && filterGrid._pins) {
    tabs.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t === b)); });
        filterGrid._pins.forEach(function (p) { p.hidden = !(f === 'all' || p.getAttribute('data-kind') === f); });
        filterGrid._layout(true);
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
