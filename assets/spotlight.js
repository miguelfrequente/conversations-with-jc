// Scroll spotlight, v2 (design feedback 2026-07-16):
//   · If the whole page fits the viewport → no fading at all. The effect
//     only earns its place when there is scroll to narrate.
//   · On longer pieces, a READING BAND stays sharp — every bubble inside
//     it holds full alpha; bubbles scrolled past (above) or not yet
//     reached (below) fade. At the top of the page the band extends to
//     the top edge; at maximum scroll it extends to the bottom, so the
//     opening and the finale are never dimmed when the reader is there.
// Progressive enhancement: without JS the html.js class never lands and
// everything renders at full opacity.
(function () {
  document.documentElement.classList.add("js");

  var turns = Array.prototype.slice.call(document.querySelectorAll(".dialogue .turn"));
  if (!turns.length) return;

  function refocus() {
    var vh = window.innerHeight;
    var doc = document.documentElement;
    var maxScroll = doc.scrollHeight - vh;

    // Short piece: everything fits (allow a little slack) → all sharp.
    if (maxScroll <= 40) {
      for (var i = 0; i < turns.length; i++) turns[i].classList.add("in-focus");
      return;
    }

    // Reading band, widened at the extremes of the scroll range.
    var y = window.scrollY || doc.scrollTop;
    var atTop = y <= 10;
    var atBottom = y >= maxScroll - 10;
    var bandTop = atTop ? 0 : vh * 0.20;
    var bandBottom = atBottom ? vh : vh * 0.62;

    for (var j = 0; j < turns.length; j++) {
      var r = turns[j].getBoundingClientRect();
      var inBand = r.bottom > bandTop && r.top < bandBottom;
      turns[j].classList.toggle("in-focus", inBand);
    }
  }

  // Substack-style header: hide on downward scroll, reveal on ANY upward
  // scroll (and always near the top).
  var header = document.querySelector("header.banner");
  var lastY = window.scrollY || 0;

  function updateHeader() {
    if (!header) return;
    var y = window.scrollY || document.documentElement.scrollTop;
    var dy = y - lastY;
    if (y < 80 || dy < -4) header.classList.remove("nav-hidden");
    else if (dy > 4) header.classList.add("nav-hidden");
    lastY = y;
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      refocus();
      updateHeader();
      ticking = false;
    });
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  refocus();
})();
