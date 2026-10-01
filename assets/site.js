/* Shared page behaviour (loaded with defer):
   - videos marked data-inview play only while on screen, never for reduced motion
   - on the homepage, the top nav underlines the section in view
   - on the images page, a.zoom opens the image full size (arrows/buttons move between images) */
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

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

  var box = document.getElementById('lightbox');
  var zooms = Array.prototype.slice.call(document.querySelectorAll('a.zoom'));
  if (box && zooms.length && typeof box.showModal === 'function') {
    var img = box.querySelector('img'), cap = box.querySelector('.lightbox-cap'), current = 0;
    var show = function (n) {
      current = (n + zooms.length) % zooms.length;
      var a = zooms[current], fc = a.closest('figure').querySelector('figcaption');
      img.src = a.getAttribute('href');
      img.alt = a.querySelector('img').alt;
      cap.innerHTML = fc ? fc.innerHTML : '';
    };
    zooms.forEach(function (a, n) {
      a.addEventListener('click', function (e) { e.preventDefault(); show(n); box.showModal(); });
    });
    box.querySelector('.lightbox-prev').addEventListener('click', function () { show(current - 1); });
    box.querySelector('.lightbox-next').addEventListener('click', function () { show(current + 1); });
    box.querySelector('.lightbox-close').addEventListener('click', function () { box.close(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') show(current + 1);
      if (e.key === 'ArrowLeft') show(current - 1);
    });
    box.addEventListener('close', function () { img.removeAttribute('src'); zooms[current].focus(); });
  }
})();
