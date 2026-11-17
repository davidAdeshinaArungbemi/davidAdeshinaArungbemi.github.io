/* The homepage showcase: one clip at a time, moving to the next on its own.

   Markup (kit.showcase writes it; each direction's stylesheet decides how it looks):
     <section data-showcase data-colour="page|self">
       <div data-showcase-stage>
         [<canvas data-showcase-ambient>]                       soft light behind the screen, optional
         <figure data-slide data-src="clip.mp4" data-mood="name" data-seconds="12" data-title="…" [hidden]>
           <div class="showcase-media"><img class="showcase-poster" src="poster.jpg" alt="what the clip shows"></div>
           <figcaption data-showcase-hold>… the piece's name, linked, and one line …</figcaption>
         </figure> …
       </div>
       <div data-showcase-hold>  prev / toggle / next buttons, and one <a data-showcase-pick href="the piece"> per slide </div>
       <p data-showcase-status class="visually-hidden" aria-live="polite"></p>
     </section>

   What it does
   - Only the current clip has a <video>, made when the clip is shown and released when it leaves,
     so one clip at a time is loaded and playing. Posters are ordinary images.
   - It plays only while most of the screen is in view and the tab is visible.
   - After data-seconds of playing it moves to the next clip. The count waits while the pointer rests on the
     caption or the controls, and while keyboard focus is inside, so nothing changes under a reader.
     A mouse click doesn't hold it.
   - Pause stops both the clip and the moving on. Previous, next and the picks choose a clip.
   - Nothing starts by itself with reduced motion set, or when the visitor's browser asks to save data:
     the first poster shows and Play starts the clip.
   - If the browser refuses to autoplay it shows Play. A clip that fails or stalls keeps its poster and
     the showcase moves on after that clip's time.
   - Without JavaScript the first slide's poster and caption show, and the picks are plain links to the pieces.
     The carousel roles and "1 of 3" labels are added here, so they only exist when the carousel works. */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  var thrifty = !!(conn && (conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '')));
  var STALL = 9000;                                      // ms a clip may take to start before it counts as failed

  function keyboardFocus(el) {
    try { return el.matches(':focus-visible'); } catch (e) { return true; }
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-showcase]'), function (box) {
    var slides = Array.prototype.slice.call(box.querySelectorAll('[data-slide]'));
    if (!slides.length) return;
    var picks = Array.prototype.slice.call(box.querySelectorAll('[data-showcase-pick]'));
    var toggle = box.querySelector('[data-showcase-toggle]');
    var status = box.querySelector('[data-showcase-status]');
    var ambient = box.querySelector('[data-showcase-ambient]');
    var ctx = ambient && ambient.getContext ? ambient.getContext('2d') : null;

    var index = 0, video = null;
    var userPaused = reduce.matches || thrifty;          // the visitor's choice (or their settings): stays until they press Play
    var inView = false, hover = false, focused = false, clock = 0, last = 0, ticking = false;

    box.classList.add('is-live');
    box.setAttribute('aria-roledescription', 'carousel');
    slides.forEach(function (s, i) {
      s.hidden = false;
      s.setAttribute('role', 'group');
      s.setAttribute('aria-roledescription', 'slide');
      s.setAttribute('aria-label', (i + 1) + ' of ' + slides.length);
      setCurrent(s, i === 0);
    });
    if (picks[0]) picks[0].setAttribute('aria-current', 'true');
    var pickList = box.querySelector('.showcase-picks');
    if (pickList) pickList.setAttribute('aria-label', 'Choose a clip');

    function setCurrent(slide, on) {
      slide.classList.toggle('is-current', on);
      if ('inert' in slide) slide.inert = !on; else slide.setAttribute('aria-hidden', String(!on));
    }
    function seconds() { return parseFloat(slides[index].getAttribute('data-seconds')) || 12; }
    function failed() { return slides[index].classList.contains('is-failed'); }
    function shouldPlay() { return !userPaused && inView && !document.hidden; }
    function held() { return hover || focused; }

    function release(v, slide) {
      if (!v) return;
      v.pause();
      clearTimeout(v._stall);
      setTimeout(function () {                            // after the cross-fade, let go of the file
        if (v === video) return;                          // it came back in the meantime
        if (!slide.classList.contains('is-current')) slide.classList.remove('is-playing');
        v.removeAttribute('src');
        try { v.load(); } catch (e) {}
        if (v.parentNode) v.parentNode.removeChild(v);
      }, 850);
    }

    function make(slide) {
      Array.prototype.forEach.call(slide.querySelectorAll('.showcase-video'), function (old) {   // one still leaving
        old.removeAttribute('src');
        if (old.parentNode) old.parentNode.removeChild(old);
      });
      slide.classList.remove('is-playing');
      var v = document.createElement('video');
      v.muted = true; v.defaultMuted = true; v.loop = true; v.playsInline = true;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
      v.setAttribute('aria-hidden', 'true');              // the poster image beside it carries the description
      v.tabIndex = -1;
      v.preload = 'auto';
      v.disableRemotePlayback = true;
      v.className = 'showcase-video';
      v.addEventListener('playing', function () {
        clearTimeout(v._stall);
        if (v === video) slide.classList.add('is-playing');
      });
      v.addEventListener('error', function () { if (v === video) fail(); });
      v._stall = setTimeout(function () { if (v === video && v.readyState < 3) fail(); }, STALL);
      var start = parseFloat(slide.getAttribute('data-start')) || 0;
      v.src = slide.getAttribute('data-src') + (start ? '#t=' + start : '');
      slide.querySelector('.showcase-media').appendChild(v);
      return v;
    }

    function fail() {                                    // keep the poster; the count runs as if the clip had played
      var slide = slides[index];
      slide.classList.add('is-failed');
      var v = video; video = null;
      release(v, slide);
      sync();
    }

    function play() {
      if (failed()) return;
      if (!video) video = make(slides[index]);
      var v = video, p = v.play();
      if (p && p.catch) p.catch(function (err) {
        if (v !== video) return;
        if (err && err.name === 'NotAllowedError') { userPaused = true; sync(); }   // autoplay refused: offer Play
        else if (err && err.name !== 'AbortError') fail();
      });
    }

    function sync() {
      if (shouldPlay()) play(); else if (video) video.pause();
      var playing = !userPaused;
      if (toggle) {
        toggle.setAttribute('data-state', playing ? 'playing' : 'paused');
        toggle.setAttribute('aria-label', playing ? 'Pause the showcase' : 'Play the showcase');
        toggle.title = playing ? 'Pause' : 'Play';
      }
      box.classList.toggle('is-paused', !playing);
      if (playing && inView && !ticking) { ticking = true; last = performance.now(); requestAnimationFrame(tick); }
    }

    function tick(now) {
      if (userPaused || !inView || document.hidden) { ticking = false; return; }
      var dt = Math.min(250, now - last); last = now;
      var running = failed() || (video && !video.paused && video.readyState > 2);
      if (running && !held() && !reduce.matches) clock += dt / 1000;
      var share = Math.min(1, clock / seconds());
      box.style.setProperty('--progress', share.toFixed(3));
      if (video && running && ctx && now - (tick.painted || 0) > 160) { tick.painted = now; light(video); }
      if (share >= 1 && slides.length > 1) show(index + 1, false);
      requestAnimationFrame(tick);
    }

    function light(source) {                             // a few blurred pixels of the picture, drawn behind the screen
      if (!ctx) return;
      try { ctx.drawImage(source, 0, 0, ambient.width, ambient.height); } catch (e) {}
    }
    function lightFrom(slide) {
      var poster = slide.querySelector('.showcase-poster');
      if (!poster || !ctx) return;
      if (poster.complete) light(poster);
      else poster.addEventListener('load', function () { if (slides[index] === slide && !slide.classList.contains('is-playing')) light(poster); }, { once: true });
    }

    function show(next, manual) {
      next = (next + slides.length) % slides.length;
      if (next === index && (video || failed())) return;
      var old = slides[index], oldVideo = video;
      video = null;
      if (next !== index) { release(oldVideo, old); setCurrent(old, false); }
      index = next; clock = 0;
      box.style.setProperty('--progress', '0');
      var slide = slides[index];
      slide.classList.remove('is-failed');                // give it another go
      setCurrent(slide, true);
      picks.forEach(function (p, i) { if (i === index) p.setAttribute('aria-current', 'true'); else p.removeAttribute('aria-current'); });
      lightFrom(slide);
      if (manual && status) status.textContent = 'Clip ' + (index + 1) + ' of ' + slides.length + ': ' + (slide.getAttribute('data-title') || '');
      box.dispatchEvent(new CustomEvent('showcase:change', { bubbles: true, detail: { index: index, mood: slide.getAttribute('data-mood'), manual: !!manual } }));
      sync();
    }

    // ---- controls
    var prev = box.querySelector('[data-showcase-prev]'), nextBtn = box.querySelector('[data-showcase-next]');
    if (prev) prev.addEventListener('click', function () { show(index - 1, true); });
    if (nextBtn) nextBtn.addEventListener('click', function () { show(index + 1, true); });
    if (toggle) toggle.addEventListener('click', function () { userPaused = !userPaused; sync(); });
    picks.forEach(function (p, i) {
      p.setAttribute('role', 'button');     // with the script running these choose a clip; without it they are links to the pieces
      p.addEventListener('click', function (e) {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button) return;   // "open in a new tab" still works
        e.preventDefault();
        show(i, true);
      });
      p.addEventListener('keydown', function (e) { if (e.key === ' ') { e.preventDefault(); show(i, true); } });
    });
    box.addEventListener('keydown', function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      if (e.target.closest && e.target.closest('a[href]:not([data-showcase-pick])')) return;
      e.preventDefault();
      show(index + (e.key === 'ArrowRight' ? 1 : -1), true);
      if (e.target.hasAttribute && e.target.hasAttribute('data-showcase-pick') && picks[index]) picks[index].focus({ preventScroll: true });
    });

    // ---- hold the count while someone is reading or reaching for a control
    Array.prototype.forEach.call(box.querySelectorAll('[data-showcase-hold]'), function (z) {
      z.addEventListener('pointerenter', function (e) { if (e.pointerType !== 'touch') hover = true; });
      z.addEventListener('pointerleave', function () { hover = false; });
    });
    box.addEventListener('focusin', function (e) { focused = keyboardFocus(e.target); });
    box.addEventListener('focusout', function (e) { if (!box.contains(e.relatedTarget)) focused = false; });

    // ---- only while it can be seen
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          inView = en.isIntersecting && (en.intersectionRatio >= 0.35 || en.intersectionRect.height >= window.innerHeight * 0.5);
          sync();
        });
      }, { threshold: [0, 0.35, 0.6, 1] }).observe(box.querySelector('[data-showcase-stage]') || box);
    } else { inView = true; }
    document.addEventListener('visibilitychange', sync);
    if (reduce.addEventListener) reduce.addEventListener('change', function () { if (reduce.matches) { userPaused = true; sync(); } });

    // start: announce the first clip's mood, light the screen from its poster
    lightFrom(slides[0]);
    box.dispatchEvent(new CustomEvent('showcase:change', { bubbles: true, detail: { index: 0, mood: slides[0].getAttribute('data-mood'), manual: false } }));
    sync();
  });
})();
