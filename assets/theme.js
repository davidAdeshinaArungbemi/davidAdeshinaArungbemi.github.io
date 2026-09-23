/* Loaded in <head>, before the page is painted: applies the saved
   light/dark choice first, so pages never flash the other theme. */
(function () {
  var root = document.documentElement;
  var COLORS = { light: '#F4F1EA', dark: '#111315' };
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) {}
  if (stored === 'dark' || stored === 'light') root.setAttribute('data-theme', stored);

  function current() {
    return root.getAttribute('data-theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  // Keep the browser's address-bar colour in step with a manual choice.
  function syncBrowserColour() {
    var t = root.getAttribute('data-theme');
    if (!t) return;
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) { m.setAttribute('content', COLORS[t]); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    syncBrowserColour();
    var btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      syncBrowserColour();
    });
  });
})();
