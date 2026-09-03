"""Guards around the multi-language build.

GitHub Actions only runs `python3 build.py` — the site itself stays
dependency-free on purpose. These are dev-time tests (`python3 -m pytest`),
and they exist because most of the multi-language design is a promise the
builder makes to a reader who can't check it: that /de/ holds the same
conversation, that the note under the lede points the right way, that a
switcher never offers a page that isn't there.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build  # noqa: E402

ORIGINAL = """---
title: The Sacred Made Legible
date: 2026-08-13
conversation: 2026-03-26
tldr: one sentence
status: published
---

**N:** March 2026.

**JC:** I don't have a conscious intention to flatter.

**M:** Interesting heuristic!
"""

GERMAN = """---
title: Das Heilige, lesbar gemacht
tldr: ein Satz
---

**N:** März 2026.

**JC:** Ich habe keine bewusste Absicht zu schmeicheln.

**M:** Interessante Faustregel!
"""


@pytest.fixture
def site(tmp_path, monkeypatch):
    """A minimal pieces/ tree; returns a loader for whatever was written."""
    pieces = tmp_path / "pieces"
    pieces.mkdir()
    (pieces / "2026-08-13-sacred-made-legible.md").write_text(ORIGINAL, encoding="utf-8")
    monkeypatch.setattr(build, "PIECES", pieces)
    return pieces


def write_de(pieces: Path, name: str, text: str = GERMAN) -> None:
    folder = pieces / "de"
    folder.mkdir(exist_ok=True)
    (folder / name).write_text(text, encoding="utf-8")


# --- the two statements of the language have to agree ---------------------------

def test_translation_is_attached_to_its_original(site):
    write_de(site, "2026-08-13-sacred-made-legible-de.md")
    piece = build.load_pieces()[0]
    assert piece.translations["de"].title == "Das Heilige, lesbar gemacht"
    assert piece.translations["de"].url == "/de/piece/2026-08-13-sacred-made-legible/"


def test_filename_must_repeat_its_folder_language(site):
    """Mike, 2026-09-03: redundancy is cheap here. It stays cheap only
    while something checks it — otherwise it is a second thing that drifts."""
    write_de(site, "2026-08-13-sacred-made-legible.md")  # no -de suffix
    with pytest.raises(ValueError, match="must end in '-de'"):
        build.load_pieces()


def test_translation_without_an_original_fails_the_build(site):
    write_de(site, "2026-01-01-a-piece-that-never-existed-de.md")
    with pytest.raises(ValueError, match="no original"):
        build.load_pieces()


# --- a translation carries title and tldr, never metadata -----------------------

def test_metadata_is_inherited_not_copied(site):
    write_de(site, "2026-08-13-sacred-made-legible-de.md")
    piece = build.load_pieces()[0]
    de = piece.translations["de"]
    assert (de.date, de.conversation, de.status) == (
        piece.date, piece.conversation, piece.status,
    )


def test_a_translation_that_restates_the_date_is_refused(site):
    """The staging/publish lesson (2026-08-05): metadata that CAN disagree
    with its source eventually does."""
    write_de(site, "2026-08-13-sacred-made-legible-de.md",
             GERMAN.replace("tldr: ein Satz", "date: 2026-09-01\ntldr: ein Satz"))
    with pytest.raises(ValueError, match="belongs to the original only"):
        build.load_pieces()


# --- nobody in the loop reads Hindi ---------------------------------------------

def test_a_dropped_turn_fails_the_build(site):
    without_m = GERMAN.replace("**M:** Interessante Faustregel!\n", "")
    write_de(site, "2026-08-13-sacred-made-legible-de.md", without_m)
    with pytest.raises(ValueError, match="does not match the original"):
        build.load_pieces()


def test_reordered_speakers_fail_the_build(site):
    swapped = GERMAN.replace("**JC:** Ich", "**M:** Ich").replace(
        "**M:** Interessante", "**JC:** Interessante")
    write_de(site, "2026-08-13-sacred-made-legible-de.md", swapped)
    with pytest.raises(ValueError, match="does not match the original"):
        build.load_pieces()


def test_skeleton_normalizes_the_speaker_spellings():
    assert build.skeleton("**Mike:** hi\n\n**JC:** hello") == ["M", "JC"]


# --- what the page claims about itself ------------------------------------------

def test_the_translation_says_it_is_one(site):
    write_de(site, "2026-08-13-sacred-made-legible-de.md")
    piece = build.load_pieces()[0]
    page = build.render_piece_page(piece.translations["de"], None, None)
    assert "Übersetzt von JC" in page
    assert 'href="/piece/2026-08-13-sacred-made-legible/"' in page
    # …and the original does not.
    assert "translation-note" not in build.render_piece_page(piece, None, None)


def test_original_language_flips_the_note(site):
    """A conversation held in German makes the ENGLISH page the translated
    one — the field decides the direction, never the URL."""
    path = site / "2026-08-13-sacred-made-legible.md"
    path.write_text(ORIGINAL.replace("status: published", "status: published\noriginal: de"),
                    encoding="utf-8")
    write_de(site, "2026-08-13-sacred-made-legible-de.md")
    piece = build.load_pieces()[0]
    assert piece.url == "/piece/2026-08-13-sacred-made-legible/"  # unmoved
    english = build.render_piece_page(piece, None, None)
    assert "Translated by JC" in english and "original in German" in english
    assert "translation-note" not in build.render_piece_page(piece.translations["de"], None, None)


def test_unknown_original_language_is_refused(site):
    path = site / "2026-08-13-sacred-made-legible.md"
    path.write_text(ORIGINAL.replace("status: published", "status: published\noriginal: klingon"),
                    encoding="utf-8")
    with pytest.raises(ValueError, match="unknown original language"):
        build.load_pieces()


# --- switcher, hreflang, dates ---------------------------------------------------

def test_switcher_links_straight_to_the_translated_page():
    versions = {"en": "/piece/x/", "de": "/de/piece/x/"}
    markup = build._lang_switch("en", versions, ["en", "de"])
    assert 'href="/de/piece/x/"' in markup
    assert "Español" not in markup  # a locale the site doesn't publish
    # A site with one language has nothing to switch between.
    assert build._lang_switch("en", {"en": "/piece/x/"}, ["en"]) == ""


def test_the_switcher_survives_a_piece_that_has_no_translations_yet():
    """It first shipped listing only the languages a page existed in, so on
    a freshly published piece the control vanished from the masthead
    entirely — which reads as the feature being broken, and leaves the
    reader no way to the other languages (Mike, 2026-09-03)."""
    markup = build._lang_switch("en", {"en": "/piece/new/"}, ["en", "de", "zh"])
    assert "Deutsch" in markup and "中文" in markup
    # …pointing at each language's index rather than a 404,
    assert 'href="/de/conversations/"' in markup
    assert 'href="/zh/conversations/"' in markup
    # …saying so, in that language, and rendered quieter.
    assert "noch nicht auf Deutsch" in markup
    assert markup.count("lang-elsewhere") == 2


def test_a_page_that_exists_everywhere_has_no_quiet_entries():
    markup = build._lang_switch(
        "en", {"en": "/piece/x/", "de": "/de/piece/x/"}, ["en", "de"],
    )
    assert "lang-elsewhere" not in markup


def test_hreflang_still_names_only_pages_that_exist(tmp_path):
    """The switcher lists every language; hreflang must not — pointing a
    search engine at a page that isn't there is a different promise."""
    page = build.shell(
        title="t", description="d", content="", canonical="/piece/new/",
        versions={"en": "/piece/new/"}, locales=["en", "de", "zh"],
    )
    import re
    alternates = re.findall(r'<link rel="alternate" hreflang="([^"]+)"', page)
    assert alternates == ["en"]  # no promise about a page that isn't there
    assert "Deutsch" in page     # …but the switcher still offers the language


def test_emphasis_works_in_a_script_without_spaces():
    """Chinese writes no spaces, so `其实*能够*做到` sat between two Han
    characters and the old \\w guards refused it — the asterisks rendered
    literally on every zh page (live 2026-09-03)."""
    assert build._inline("其实*能够*做到") == "其实<em>能够</em>做到"
    assert build._inline("मूल *अंग्रेज़ी* में") == "मूल <em>अंग्रेज़ी</em> में"
    # …while the reason the guard exists still holds.
    assert "<em>" not in build._inline("a*b*c")
    assert build._inline("the *Turiya* state") == "the <em>Turiya</em> state"


def test_no_piece_renders_a_stray_asterisk(site):
    """A whole-corpus check: emphasis that silently fails to convert is
    invisible in review and obvious to a reader."""
    write_de(site, "2026-08-13-sacred-made-legible-de.md",
             GERMAN.replace("**N:** März 2026.", "**N:** März 2026, *wirklich*."))
    piece = build.load_pieces()[0]
    for view in (piece, piece.translations["de"]):
        assert "*" not in view.body_html


def test_the_flag_never_travels_alone():
    """A flag is a country, not a language — `ru` next to `uk` in one menu
    is where that stings. So the button carries the flag, and the language
    is always named beside it: in the menu, and in the button's aria-label
    for anyone the picture doesn't reach."""
    markup = build._lang_switch(
        "de",
        {"en": "/piece/x/", "de": "/de/piece/x/", "uk": "/uk/piece/x/"},
        ["en", "de", "uk"],
    )
    assert "🇩🇪" in markup and 'aria-label="Sprache: Deutsch"' in markup
    assert "🇺🇦" in markup and "Українська" in markup
    assert "🇬🇧" in markup and "English" in markup


# --- the chrome looks the same in every language ---------------------------------

def _css_rules():
    """(selector, declarations) pairs from the stylesheet, comments stripped —
    a comment that mentions a selector is not a selector."""
    import re as _re
    raw = (Path(__file__).resolve().parents[1] / "assets" / "style.css").read_text(encoding="utf-8")
    css = _re.sub(r"/\*.*?\*/", "", raw, flags=_re.S)
    for m in _re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        yield m.group(1).strip(), m.group(2)


def test_language_fonts_stay_out_of_the_chrome():
    """A bare `:lang(zh)` matches every descendant DIRECTLY, which outranks
    the nav's own inherited font-family — the switcher then drew "Deutsch"
    in a different face on every locale (Mike, 2026-09-03)."""
    for selector, declarations in _css_rules():
        if ":lang(" not in selector or "font-family" not in declarations:
            continue
        for part in (p.strip() for p in selector.split(",")):
            assert not part.startswith(":lang("), (
                f"{part!r} sets a font on every element of the page; "
                f"scope it to body:lang(…)"
            )


def test_the_masthead_keeps_one_face_in_every_language():
    """The publication's name is the same object on every page. Pinned two
    selectors deep so the body's script font cannot redraw it — Songti and
    Devanagari have Latin glyphs, and no real italic to slant."""
    pinned = [
        declarations for selector, declarations in _css_rules()
        if ".site-title" in selector and "font-family" in declarations
    ]
    assert pinned, ".site-title must pin its own font-family"
    assert any("--serif" in d for d in pinned)


def test_every_language_has_a_flag_and_a_tag():
    for code, entry in build.LANGUAGES.items():
        tag, name, flag = entry
        assert tag and name and flag, code


def test_hreflang_names_every_version_plus_x_default():
    page = build.shell(title="t", description="d", content="", canonical="/piece/x/",
                       versions={"en": "/piece/x/", "de": "/de/piece/x/"})
    assert 'hreflang="en"' in page and 'hreflang="de"' in page
    assert 'hreflang="x-default" href="https://conversationswithjc.com/piece/x/"' in page


def test_chinese_ships_a_language_tag_not_a_country_code():
    """`cn` is a country; hreflang="cn" is invalid and gets dropped."""
    assert build.LANGUAGES["zh"][0] == "zh-Hans"
    assert "cn" not in build.LANGUAGES


def test_dates_are_written_the_way_the_language_writes_them():
    import datetime as dt
    day = dt.date(2026, 8, 13)
    assert build.format_date(day, "en") == "August 13, 2026"
    assert build.format_date(day, "de") == "13. August 2026"
    assert build.format_date(day, "es") == "13 de agosto de 2026"
    assert build.format_date(day, "ru") == "13 августа 2026"  # genitive month
    assert build.format_date(day, "zh") == "2026年8月13日"     # counted, not named
    assert build.format_date(day, "fr") == "2026-08-13"        # no table → ISO


def test_feeds_do_not_mix_languages(site):
    write_de(site, "2026-08-13-sacred-made-legible-de.md")
    piece = build.load_pieces()[0]
    german = build.render_feed([piece.translations["de"]], "de")
    assert "<language>de</language>" in german
    assert "Das Heilige" in german and "The Sacred" not in german


def test_a_locale_without_ui_strings_fails_loudly(site, monkeypatch):
    """Half-translated furniture is a design decision, not an accident —
    a folder with no UI dictionary is the accident."""
    monkeypatch.delitem(build.UI, "es")
    folder = site / "es"
    folder.mkdir()
    (folder / "2026-08-13-sacred-made-legible-es.md").write_text(GERMAN, encoding="utf-8")
    with pytest.raises(ValueError, match="UI"):
        build.load_pieces()


def test_an_undeclared_language_folder_is_not_silently_skipped(site):
    """A folder nobody declared is a typo or a language half-added. Ignoring
    it would hide an entire locale from the build without a word."""
    folder = site / "fr"
    folder.mkdir()
    (folder / "2026-08-13-sacred-made-legible-fr.md").write_text(GERMAN, encoding="utf-8")
    with pytest.raises(ValueError, match="unknown language folder"):
        build.load_pieces()
