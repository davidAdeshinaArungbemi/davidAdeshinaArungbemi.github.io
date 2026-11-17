/* Loaded in <head>, after the stylesheets and before the page is painted: settles light or dark first,
   so a page never flashes the other one. <html data-default-scheme="dark|light|auto"> says what a first
   visit gets; "auto" follows the device. A button marked data-scheme-toggle switches and remembers the
   choice; the swap is instant, because fading light into dark walks text and ground past each other.
   Without JavaScript the toggle is hidden (shared/proto.css) and the page keeps its default palette.
   (The older pages keep their own assets/theme.js; this file belongs to the new design only.) */
(function () {
  var root = document.documentElement;
  var key = 'scheme' + (root.getAttribute('data-direction') ? '-' + root.getAttribute('data-direction') : '');
  var saved = null;
  try { saved = localStorage.getItem(key); } catch (e) {}
  var dark = window.matchMedia('(prefers-color-scheme: dark)');

  function wanted() {
    if (saved === 'light' || saved === 'dark') return saved;
    var first = root.getAttribute('data-default-scheme');
    if (first === 'light' || first === 'dark') return first;
    return dark.matches ? 'dark' : 'light';
  }
  function paintBar() {                                       // the phone browser's bar takes the ground colour
    var meta = document.querySelector('meta[name="theme-color"][data-follow]');
    if (!meta) return;
    var c = getComputedStyle(root).getPropertyValue('--ground').trim();
    if (c) meta.setAttribute('content', c);
  }
  function apply() { root.setAttribute('data-scheme', wanted()); }
  function swap() {                                           // no fade for a scheme change, anywhere on the page
    root.setAttribute('data-swapping', '');
    apply();
    paintBar();
    requestAnimationFrame(function () { requestAnimationFrame(function () { root.removeAttribute('data-swapping'); }); });
    document.dispatchEvent(new CustomEvent('schemechange'));
  }
  apply();
  paintBar();
  if (dark.addEventListener) dark.addEventListener('change', function () { if (!saved) swap(); });

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('[data-scheme-toggle]');
    if (!btn) return;
    // Name the action, so assistive tech hears which scheme a press gives.
    function label() {
      var text = wanted() === 'dark' ? 'Switch to light' : 'Switch to dark';
      btn.setAttribute('aria-label', text);
      btn.title = text;
    }
    label();
    btn.addEventListener('click', function () {
      saved = wanted() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, saved); } catch (e) {}
      swap();
      label();
    });
  });
})();
