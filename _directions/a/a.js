/* Direction A: the dock marks the section in view, the phone menu closes once a place is chosen,
   and on an article a line along the top shows how far through it you are. */
(function () {
  var menu = document.getElementById('a-menu');
  if (menu) menu.addEventListener('click', function (e) {
    if (e.target.closest('a') && menu.hidePopover) menu.hidePopover();
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.a-dock a[href^="#"]'));
  if (links.length && 'IntersectionObserver' in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) { l.removeAttribute('aria-current'); });
        var a = byId[en.target.id];
        if (a) a.setAttribute('aria-current', 'location');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['top'].concat(Object.keys(byId)).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) watch.observe(el);
    });
  }

  var bar = document.querySelector('.read-progress'), article = document.querySelector('.post article');
  if (bar && article) {
    var queued = false;
    var update = function () {
      queued = false;
      var r = article.getBoundingClientRect(), span = r.height - window.innerHeight;
      bar.style.transform = 'scaleX(' + (span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1) + ')';
    };
    var ask = function () { if (!queued) { queued = true; requestAnimationFrame(update); } };
    window.addEventListener('scroll', ask, { passive: true });
    window.addEventListener('resize', ask);
    update();
  }
})();
