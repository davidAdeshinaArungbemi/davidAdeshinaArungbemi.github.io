/* The page's colours follow what is being shown.

   A "mood" is a named set of colours (the stylesheet holds them as [data-mood="name"] rules).
   This script only decides which mood <html> wears, and the stylesheet fades between them.

     [data-peek="name"]   pointing at this element, or keyboard focus inside it, lends the page that mood
                          until the pointer or focus leaves
     [data-room="name"]   while this section crosses the middle of the screen, the page rests in its mood
     showcase             a showcase marked data-colour="page" sets the resting mood to its current
                          clip's; data-colour="self" colours only the showcase

   Script API:  Mood.rest(name)   set the resting mood        Mood.peek(name or null)
   Events on document:  "moodchange" (detail { mood, resting })
                        "roomchange" (detail { room }), and the room in view gets the class is-here

   Guards against flicker: a peek waits a moment before it applies, so sweeping the pointer across a
   list does not strobe; the stylesheet's fade then starts from wherever the colours currently are.
   With JavaScript off none of this runs and the page keeps its default mood. */
(function () {
  var root = document.documentElement;
  var smooth = !!(window.CSS && CSS.registerProperty);      // can the browser fade custom properties?
  var IN = smooth ? 110 : 320, OUT = smooth ? 240 : 420;     // waits before a peek starts / ends, in ms
  var resting = root.getAttribute('data-mood') || 'default';
  var peeking = null, applied = resting, timer = null;

  function apply() {
    var want = peeking || resting;
    if (want === applied) return;
    applied = want;
    root.setAttribute('data-mood', want);
    document.dispatchEvent(new CustomEvent('moodchange', { detail: { mood: want, resting: resting } }));
  }
  function rest(name) { if (!name) return; resting = name; apply(); }
  function keyboardPeek() {                                  // a peek held by keyboard focus outlasts the pointer
    var f = document.activeElement;
    if (!f || !f.closest) return null;
    try { if (!f.matches(':focus-visible')) return null; } catch (e) {}
    var el = f.closest('[data-peek]');
    return el ? el.getAttribute('data-peek') : null;
  }
  function peek(name) {
    clearTimeout(timer);
    timer = setTimeout(function () { peeking = name || keyboardPeek(); apply(); }, name ? IN : OUT);
  }
  window.Mood = { rest: rest, peek: peek, current: function () { return applied; }, resting: function () { return resting; } };

  // ---- pointing and focus
  function target(e) { return e.target && e.target.closest ? e.target.closest('[data-peek]') : null; }
  document.addEventListener('pointerover', function (e) {
    if (e.pointerType === 'touch') return;
    var el = target(e);
    if (el) peek(el.getAttribute('data-peek'));
    else if (peeking) peek(null);                            // the element that lent its mood may have gone
  });
  document.addEventListener('pointerout', function (e) {
    if (e.pointerType === 'touch') return;
    var el = target(e);
    if (el && !(e.relatedTarget && el.contains(e.relatedTarget))) peek(null);
  });
  document.addEventListener('focusin', function (e) {
    var el = target(e);
    var keyboard = true;
    try { keyboard = e.target.matches(':focus-visible'); } catch (err) {}
    if (el && keyboard) peek(el.getAttribute('data-peek'));
  });
  document.addEventListener('focusout', function (e) { if (target(e)) peek(null); });

  // ---- the section in view
  var rooms = Array.prototype.slice.call(document.querySelectorAll('[data-room]'));
  var room = null;
  if (rooms.length && 'IntersectionObserver' in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        room = en.target;
        rest(room.getAttribute('data-room'));
        rooms.forEach(function (r) { r.classList.toggle('is-here', r === room); });
        document.dispatchEvent(new CustomEvent('roomchange', { detail: { room: room } }));
      });
    }, { rootMargin: '-50% 0px -50% 0px' });                 // a line across the middle of the screen
    rooms.forEach(function (r) { seen.observe(r); });
  }

  // ---- the showcase's current clip
  document.addEventListener('showcase:change', function (e) {
    var box = e.target, mood = e.detail && e.detail.mood;
    if (!mood) return;
    if (box.getAttribute('data-colour') === 'self') { box.setAttribute('data-mood', mood); return; }
    var holder = box.closest('[data-room]');
    if (holder) {                                             // the showcase is one room among several
      holder.setAttribute('data-room', mood);
      if (room === holder || room === null) rest(mood);
    } else if (!(rooms.length && room)) {                     // never override a room the reader is in
      rest(mood);
    }
  });

  // ---- phones and tablets: the browser's own bar takes the page's ground colour once a fade ends
  var meta = document.querySelector('meta[name="theme-color"][data-follow]');
  if (meta) {
    var paint = function () { var c = getComputedStyle(root).getPropertyValue('--ground').trim(); if (c) meta.setAttribute('content', c); };
    var later;
    var soon = function () { clearTimeout(later); later = setTimeout(paint, 1000); };
    document.addEventListener('moodchange', soon);
    document.addEventListener('schemechange', soon);
    paint();
  }
})();
