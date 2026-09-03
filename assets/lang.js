/* Language suggestion bar — offers, never redirects.
 *
 * GitHub Pages is a static CDN: Accept-Language never reaches the server and
 * geo-IP would mean an edge runtime plus handling IP addresses. The browser's
 * own navigator.languages is the better signal anyway — it is what the reader
 * chose, not where they happen to sit. But an automatic jump would send a
 * reader who clicked an English link on X somewhere they never asked to go,
 * so the offer is a line they can take or dismiss (Mike, 2026-09-03).
 *
 * Dismissal and use of the switcher are remembered in localStorage — the
 * reader's own explicit choice, no tracking, nothing leaves the browser.
 */
(function () {
  "use strict";

  var KEY = "cwjc:lang-suggest";

  function remembered() {
    try {
      return window.localStorage.getItem(KEY) === "off";
    } catch (e) {
      return false; // private mode, blocked storage — just behave as untouched
    }
  }

  function remember() {
    try {
      window.localStorage.setItem(KEY, "off");
    } catch (e) {
      /* nothing to do — the bar simply reappears next visit */
    }
  }

  // "de-AT" → "de", "zh-Hans-CN" → "zh". Matching on the primary subtag keeps
  // zh-CN/zh-TW/zh-Hans and de-DE/de-CH/de-AT all pointing at one translation.
  function primary(tag) {
    return String(tag || "").toLowerCase().split("-")[0];
  }

  // Using the switcher IS the reader saying they know the languages exist.
  document.addEventListener("click", function (ev) {
    var link = ev.target.closest && ev.target.closest(".lang-switch a");
    if (link) remember();
  });

  var bar = document.getElementById("lang-suggest");
  if (!bar || remembered()) return;

  var here = primary(document.documentElement.lang);
  var offers = {};
  var templates = bar.querySelectorAll("template[data-lang]");
  for (var i = 0; i < templates.length; i++) {
    offers[primary(templates[i].dataset.tag)] = templates[i];
  }

  // Walk the reader's preferences in order. The first that is already this
  // page wins — nothing to offer. The first that we HAVE gets offered.
  var prefs = navigator.languages && navigator.languages.length
    ? navigator.languages
    : [navigator.language];
  var pick = null;
  for (var j = 0; j < prefs.length; j++) {
    var code = primary(prefs[j]);
    if (code === here) return;
    if (offers[code]) {
      pick = offers[code];
      break;
    }
  }
  if (!pick) return;

  bar.appendChild(pick.content.cloneNode(true));
  bar.setAttribute("lang", pick.dataset.tag);
  bar.hidden = false;

  var dismiss = bar.querySelector("[data-dismiss]");
  if (dismiss) {
    dismiss.addEventListener("click", function () {
      bar.hidden = true;
      remember();
    });
  }
  var go = bar.querySelector("a");
  if (go) go.addEventListener("click", remember);
})();
