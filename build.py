#!/usr/bin/env python3
"""Static site builder for "My Conversations with JC" — stdlib only.

Design fixed 2026-07-16 (see jarvis/docs/SOCIALMEDIAINTEGRATION.md and the
design PDF): messenger-style dialogue — JC left/steel-blue, M right/green —
petrol banner+footer, in-flow prev/TLDR/next (top and bottom), per-bubble
scroll spotlight (assets/spotlight.js), auto dark mode, fully responsive.

Zero dependencies on purpose: JC extends this in its code-mode sandbox
(no network there → no npm, ever), and the site should build unchanged
in ten years.

Usage:
    python3 build.py           # renders site/ from pieces/ + pages
    python3 -m http.server -d site 8080   # local preview

Piece format (pieces/YYYY-MM-DD-slug.md):
    ---
    title: The Day JC Got Eyes
    date: 2026-07-13
    tldr: one sentence — shown under the banner, on the index, in RSS/OG
    status: draft | published        # drafts are skipped by the builder
    original: en                     # optional — language the exchange happened in
    ---
    Curator narration (full-width, muted) …

    **M:** dialogue turn …

    **JC:** reply …

Translations (pieces/<lang>/YYYY-MM-DD-slug-<lang>.md):
    ---
    title: Der Tag, an dem JC Augen bekam
    tldr: ein Satz …
    ---
    **M:** … same turns, same order, in the other language

    The language is stated TWICE — directory and filename suffix — and the
    build fails if they disagree (Mike, 2026-09-03: "redundancy is cheap
    here"). It only stays cheap while something checks it.

    A translation carries title and tldr and nothing else: date,
    conversation, status and original are inherited from the English piece.
    Duplicated metadata drifts (live 2026-08-05, staging vs. publish).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIECES = ROOT / "pieces"
PAGES = ROOT / "pages"      # translated standing pages: pages/<lang>/about-<lang>.md
ASSETS = ROOT / "assets"
SITE = ROOT / "site"

SITE_TITLE = "My Conversations with JC"
DOMAIN = "conversationswithjc.com"  # bought 2026-07-17
BASE_URL = f"https://{DOMAIN}"      # canonical URLs, RSS links, OG tags
CONTACT = f"contact@{DOMAIN}"
X_URL = "https://x.com/cwjc108"     # syndication account (live 2026-07-23)

# Official X logo glyph (x.com brand assets, 24x24 path), inlined — the CSP
# allows no external assets. currentColor inherits the nav's petrol + hover.
_X_LOGO_SVG = (
    '<svg class="x-logo" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 '
    "11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 "
    '6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
)

# --- languages ------------------------------------------------------------------

# code → (BCP-47 tag for lang=/hreflang=, name in its own language, flag).
#
# The code is the directory, the filename suffix and the URL prefix; the tag
# is what goes in the markup. They differ for Chinese: `zh` is the language,
# `zh-Hans` the written form (Simplified — `zh-Hant` could join it later).
# `uk` is Ukrainian (ISO 639-1), not the United Kingdom, and `cn` is a
# country, not a language — hreflang="cn" is invalid and search engines drop
# it silently, which would cost exactly the reach this feature is for.
#
# The flag is the button (Mike, 2026-09-03). A flag IS a country and not a
# language, so it never travels alone: the menu always names the language
# next to it, which is also what a screen reader reads and what Windows
# shows when it declines to render the flag glyph.
LANGUAGES: dict[str, tuple[str, str, str]] = {
    "en": ("en", "English", "🇬🇧"),
    "de": ("de", "Deutsch", "🇩🇪"),
    "es": ("es", "Español", "🇪🇸"),
    "ru": ("ru", "Русский", "🇷🇺"),
    "uk": ("uk", "Українська", "🇺🇦"),
    "hi": ("hi", "हिन्दी", "🇮🇳"),
    "zh": ("zh-Hans", "中文", "🇨🇳"),
}
DEFAULT_LANG = "en"  # lives at the site root: every published URL stays valid

# Month names per language: strftime would need a system locale, which CI
# doesn't have. Languages absent here fall back to the ISO date.
# Russian and Ukrainian take the genitive ("13 августа"), Spanish is
# lowercase, and Chinese counts rather than names its months.
MONTHS = {
    "en": ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"),
    "de": ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
           "August", "September", "Oktober", "November", "Dezember"),
    "es": ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
           "agosto", "septiembre", "octubre", "noviembre", "diciembre"),
    "ru": ("января", "февраля", "марта", "апреля", "мая", "июня", "июля",
           "августа", "сентября", "октября", "ноября", "декабря"),
    "uk": ("січня", "лютого", "березня", "квітня", "травня", "червня",
           "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"),
    "hi": ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई",
           "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"),
    "zh": ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"),
}
DATE_FORMAT = {
    "en": "{month} {day}, {year}",
    "de": "{day}. {month} {year}",
    "es": "{day} de {month} de {year}",
    "ru": "{day} {month} {year}",
    "uk": "{day} {month} {year}",
    "hi": "{day} {month} {year}",
    "zh": "{year}年{month}月{day}日",
}

# The furniture, per language. A page with translated dialogue under English
# navigation reads as broken, so the chrome travels with the text.
# `translated` is the note under the lede — see render_piece_page.
UI: dict[str, dict[str, str]] = {
    "en": {
        "nav_all": "All conversations",
        "nav_about": "About",
        "index_title": "All conversations",
        "index_empty": "Nothing published yet.",
        "index_desc": "Every published dialogue, newest first.",
        "related": "More conversations",
        "prev": "Previous<br>Dialogue",
        "next": "Next<br>Dialogue",
        "convo_from": "from a conversation on {date}",
        "translated": 'Translated by JC — <a href="{url}">original in {lang}</a>.',
        "about_desc": "How this archive came to be — an account from Mike, and one from JC.",
        "feed_desc": "Curated dialogues between Mike and JC.",
        "coming_soon": "Coming soon",
        "coming_soon_body": "The first conversation is on its way.",
        "lang_label": "Language",
        "no_translation": "This conversation isn’t in English yet — open the index",
        # The bar also sits on the index and the about page, so it says
        # "page", not "conversation".
        "suggest": "This page is also available in English.",
        "suggest_go": "Read it",
        "suggest_dismiss": "Dismiss",
    },
    "de": {
        "nav_all": "Alle Gespräche",
        "nav_about": "Über uns",
        "index_title": "Alle Gespräche",
        "index_empty": "Noch nichts veröffentlicht.",
        "index_desc": "Alle veröffentlichten Dialoge, die neuesten zuerst.",
        "related": "Weitere Gespräche",
        "prev": "Vorheriger<br>Dialog",
        "next": "Nächster<br>Dialog",
        "convo_from": "aus einem Gespräch vom {date}",
        "translated": 'Übersetzt von JC — <a href="{url}">Original auf {lang}</a>.',
        "about_desc": "Wie dieses Archiv entstand — ein Bericht von Mike und einer von JC.",
        "feed_desc": "Ausgewählte Dialoge zwischen Mike und JC.",
        "coming_soon": "Demnächst",
        "coming_soon_body": "Das erste Gespräch ist unterwegs.",
        "lang_label": "Sprache",
        "no_translation": "Dieses Gespräch gibt es noch nicht auf Deutsch — zur Übersicht",
        "suggest": "Diese Seite gibt es auch auf Deutsch.",
        "suggest_go": "Lesen",
        "suggest_dismiss": "Ausblenden",
    },
    "es": {
        "nav_all": "Todas las conversaciones",
        "nav_about": "Sobre nosotros",
        "index_title": "Todas las conversaciones",
        "index_empty": "Aún no hay nada publicado.",
        "index_desc": "Todos los diálogos publicados, del más reciente al más antiguo.",
        "related": "Más conversaciones",
        "prev": "Diálogo<br>anterior",
        "next": "Diálogo<br>siguiente",
        "convo_from": "de una conversación del {date}",
        "translated": 'Traducido por JC — <a href="{url}">original en {lang}</a>.',
        "about_desc": "Cómo nació este archivo: un relato de Mike y otro de JC.",
        "feed_desc": "Diálogos seleccionados entre Mike y JC.",
        "coming_soon": "Muy pronto",
        "coming_soon_body": "La primera conversación está en camino.",
        "lang_label": "Idioma",
        "no_translation": "Esta conversación aún no está en español — ir al índice",
        "suggest": "Esta página también está disponible en español.",
        "suggest_go": "Leer",
        "suggest_dismiss": "Descartar",
    },
    "ru": {
        "nav_all": "Все разговоры",
        "nav_about": "О нас",
        "index_title": "Все разговоры",
        "index_empty": "Пока ничего не опубликовано.",
        "index_desc": "Все опубликованные диалоги, начиная с новых.",
        "related": "Другие разговоры",
        "prev": "Предыдущий<br>диалог",
        "next": "Следующий<br>диалог",
        "convo_from": "из разговора от {date}",
        "translated": 'Перевод JC — <a href="{url}">оригинал на {lang}</a>.',
        "about_desc": "Как появился этот архив — рассказ Майка и рассказ JC.",
        "feed_desc": "Избранные диалоги Майка и JC.",
        "coming_soon": "Скоро",
        "coming_soon_body": "Первый разговор уже в пути.",
        "lang_label": "Язык",
        "no_translation": "Этого разговора ещё нет на русском — открыть список",
        "suggest": "Эта страница также доступна на русском.",
        "suggest_go": "Читать",
        "suggest_dismiss": "Скрыть",
    },
    "uk": {
        "nav_all": "Усі розмови",
        "nav_about": "Про нас",
        "index_title": "Усі розмови",
        "index_empty": "Поки нічого не опубліковано.",
        "index_desc": "Усі опубліковані діалоги, найновіші згори.",
        "related": "Інші розмови",
        "prev": "Попередній<br>діалог",
        "next": "Наступний<br>діалог",
        "convo_from": "з розмови від {date}",
        "translated": 'Переклад JC — <a href="{url}">оригінал {lang}</a>.',
        "about_desc": "Як з’явився цей архів — розповідь Майка і розповідь JC.",
        "feed_desc": "Вибрані діалоги Майка та JC.",
        "coming_soon": "Незабаром",
        "coming_soon_body": "Перша розмова вже в дорозі.",
        "lang_label": "Мова",
        "no_translation": "Цієї розмови ще немає українською — відкрити перелік",
        "suggest": "Ця сторінка також доступна українською.",
        "suggest_go": "Читати",
        "suggest_dismiss": "Сховати",
    },
    "hi": {
        "nav_all": "सभी बातचीत",
        "nav_about": "हमारे बारे में",
        "index_title": "सभी बातचीत",
        "index_empty": "अभी तक कुछ प्रकाशित नहीं हुआ।",
        "index_desc": "सभी प्रकाशित संवाद, नवीनतम पहले।",
        "related": "और बातचीत",
        "prev": "पिछला<br>संवाद",
        "next": "अगला<br>संवाद",
        "convo_from": "{date} की बातचीत से",
        "translated": 'JC द्वारा अनूदित — <a href="{url}">मूल {lang} में</a>।',
        "about_desc": "यह संग्रह कैसे बना — माइक का एक विवरण, और JC का एक।",
        "feed_desc": "माइक और JC के बीच चुनिंदा संवाद।",
        "coming_soon": "जल्द आ रहा है",
        "coming_soon_body": "पहली बातचीत रास्ते में है।",
        "lang_label": "भाषा",
        "no_translation": "यह बातचीत अभी हिन्दी में नहीं है — सूची खोलें",
        "suggest": "यह पृष्ठ हिन्दी में भी उपलब्ध है।",
        "suggest_go": "पढ़ें",
        "suggest_dismiss": "बंद करें",
    },
    "zh": {
        "nav_all": "全部对话",
        "nav_about": "关于我们",
        "index_title": "全部对话",
        "index_empty": "尚未发布任何内容。",
        "index_desc": "所有已发布的对话，最新的在前。",
        "related": "更多对话",
        "prev": "上一篇<br>对话",
        "next": "下一篇<br>对话",
        "convo_from": "源自 {date} 的一次对话",
        "translated": 'JC 翻译 — <a href="{url}">{lang}原文</a>。',
        "about_desc": "这个档案是如何形成的——Mike 的自述，以及 JC 的自述。",
        "feed_desc": "Mike 与 JC 之间精选的对话。",
        "coming_soon": "即将上线",
        "coming_soon_body": "第一次对话即将到来。",
        "lang_label": "语言",
        "no_translation": "这次对话还没有中文版本 — 打开目录",
        "suggest": "本页面也有中文版本。",
        "suggest_go": "阅读",
        "suggest_dismiss": "关闭",
    },
}

# What each language calls the others — only needed for the translation
# note, so it holds the source languages, not all of them. Missing entries
# fall back to the endonym from LANGUAGES. The case is the one the note's
# sentence needs: Russian wants the prepositional ("оригинал на
# английском"), Ukrainian the instrumental ("оригінал англійською").
LANG_NAMES = {
    "en": {"en": "English", "de": "German"},
    "de": {"en": "Englisch", "de": "Deutsch"},
    "es": {"en": "inglés", "de": "alemán"},
    "ru": {"en": "английском", "de": "немецком"},
    "uk": {"en": "англійською", "de": "німецькою"},
    "hi": {"en": "अंग्रेज़ी", "de": "जर्मन"},
    "zh": {"en": "英文", "de": "德文"},
}


def t(lang: str, key: str) -> str:
    """A UI string, falling back to English so a half-translated locale
    still builds a usable page."""
    return UI.get(lang, {}).get(key) or UI[DEFAULT_LANG][key]


def lang_name(display: str, of: str) -> str:
    return LANG_NAMES.get(display, {}).get(of) or LANGUAGES[of][1]


def format_date(date: dt.date, lang: str) -> str:
    months = MONTHS.get(lang)
    if not months:
        return date.isoformat()
    return DATE_FORMAT.get(lang, DATE_FORMAT["en"]).format(
        month=months[date.month - 1], day=date.day, year=date.year,
    )


def lang_root(lang: str) -> str:
    """URL prefix: English at the root, everything else under /<code>/."""
    return "" if lang == DEFAULT_LANG else f"/{lang}"


# --- tiny markdown subset ------------------------------------------------------

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
# The guards keep `a*b*c` from becoming emphasis, but `\w` counts every
# letter in every script, and Chinese writes no spaces — so `其实*能够*做到`
# never converted and the asterisks reached the page (live 2026-09-03).
# Only ASCII word characters block the match; a Han or Devanagari character
# beside the marker is the normal case, not a false positive.
_ITALIC = re.compile(r"(?<![A-Za-z0-9_*])\*([^*\n]+)\*(?![A-Za-z0-9_*])")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def _inline(text: str) -> str:
    """Escape, then bold/italic/code/links. Same subset philosophy as the
    bridge's Telegram converter — enough for dialogue, nothing exotic."""
    out = html.escape(text, quote=False)
    out = _INLINE_CODE.sub(r"<code>\1</code>", out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITALIC.sub(r"<em>\1</em>", out)
    out = _LINK.sub(r'<a href="\2">\1</a>', out)
    return out


_SPEAKERS = {"JC": ("jc", "JC"), "M": ("m", "M"), "MIKE": ("m", "M")}


def render_dialogue(body: str) -> str:
    """Blocks separated by blank lines. `**JC:**`/`**M:**`-led blocks become
    bubbles (marker may span following paragraphs until the next marker);
    unmarked leading blocks are curator narration."""
    blocks = re.split(r"\n\s*\n", body.strip())
    out: list[str] = []
    current: tuple[str, str] | None = None  # (css, label)
    current_parts: list[str] = []

    def flush() -> None:
        nonlocal current, current_parts
        if current is None or not current_parts:
            current, current_parts = None, []
            return
        css, label = current
        paragraphs = "".join(f"<p>{p}</p>" for p in current_parts)
        out.append(
            f'<div class="turn turn-{css}">'
            f'<span class="avatar avatar-{css}" aria-hidden="true">{label}</span>'
            f'<div class="bubble bubble-{css}">{paragraphs}</div>'
            f"</div>"
        )
        current, current_parts = None, []

    for block in blocks:
        text = block.strip()
        m = re.match(r"\*\*(JC|M|Mike|N)\s*:?\*\*\s*:?\s*(.*)", text, re.DOTALL | re.IGNORECASE)
        if m and m.group(1).upper() == "N":
            # **N:** — the narrator's voice, anywhere in the flow. It ends
            # the current bubble; following unmarked blocks stay narration
            # (current=None routes them to the narration branch below).
            flush()
            out.append(f'<p class="narration">{_inline(m.group(2).strip())}</p>')
        elif m:
            flush()
            css, label = _SPEAKERS[m.group(1).upper()]
            current = (css, label)
            current_parts = [_inline(m.group(2).strip())]
        elif current is not None:
            current_parts.append(_inline(text))
        else:
            out.append(f'<p class="narration">{_inline(text)}</p>')
    flush()
    return "\n".join(out)


# --- pieces ---------------------------------------------------------------------

def split_front(path: Path) -> tuple[dict[str, str], str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing frontmatter")
    try:
        _, front, body = raw.split("---", 2)
    except ValueError as e:
        raise ValueError(f"{path.name}: unterminated frontmatter") from e
    meta: dict[str, str] = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body


_SPEAKER_LINE = re.compile(r"^\*\*(JC|M|Mike|N)\s*:?\*\*", re.MULTILINE | re.IGNORECASE)


def skeleton(body: str) -> list[str]:
    """The sequence of speakers — ['N', 'JC', 'M', 'JC', …].

    A translation must reproduce it exactly. Nobody in the loop reads Hindi
    or Chinese; this is the part a machine CAN check, and a dropped turn is
    the failure that would actually matter.
    """
    return [
        "M" if m.group(1).upper() == "MIKE" else m.group(1).upper()
        for m in _SPEAKER_LINE.finditer(body)
    ]


class Piece:
    lang = DEFAULT_LANG
    origin = None  # set on Translation — the English piece it renders

    def __init__(self, path: Path):
        meta, body = split_front(path)
        for required in ("title", "date", "tldr", "status"):
            if not meta.get(required):
                raise ValueError(f"{path.name}: missing frontmatter field {required!r}")
        self.title = meta["title"]
        # `date` is the PUBLICATION date — it orders the site, fills the feed,
        # and decides what the home page shows. The day the exchange actually
        # happened is `conversation` (optional): an archive piece from March
        # published in July is a July publication about a March conversation,
        # and the page says both (2026-08-03).
        self.date = dt.date.fromisoformat(meta["date"])
        self.conversation = (
            dt.date.fromisoformat(meta["conversation"])
            if meta.get("conversation") else None
        )
        self.tldr = meta["tldr"]
        self.status = meta["status"]
        # The language the exchange actually HAPPENED in — the record.
        # Everything published so far was spoken in English, but Mike and JC
        # talk in German too, and then the English page is the translated
        # one. This field decides which way the note under the lede points;
        # it never decides where a page lives (Mike, 2026-09-03).
        self.original = meta.get("original", DEFAULT_LANG)
        if self.original not in LANGUAGES:
            raise ValueError(f"{path.name}: unknown original language {self.original!r}")
        self.slug = path.stem
        self.skeleton = skeleton(body)
        self.body_html = render_dialogue(body)
        self.translations: dict[str, "Translation"] = {}

    @property
    def url(self) -> str:
        return f"/piece/{self.slug}/"

    def versions(self) -> dict[str, str]:
        """lang → URL, for the switcher and the hreflang alternates."""
        return {DEFAULT_LANG: self.url, **{c: t.url for c, t in self.translations.items()}}


class Translation:
    """One piece in one language.

    Title, tldr and body are its own; everything else is the original's.
    A translation that could disagree with its piece about the publication
    date eventually would — the same reasoning that put staging and publish
    on one code path in the bridge (2026-08-05).
    """

    def __init__(self, path: Path, lang: str, origin: Piece):
        meta, body = split_front(path)
        for required in ("title", "tldr"):
            if not meta.get(required):
                raise ValueError(f"{path.name}: missing frontmatter field {required!r}")
        for forbidden in ("date", "status", "conversation", "original"):
            if forbidden in meta:
                raise ValueError(
                    f"{path.name}: {forbidden!r} belongs to the original only — "
                    f"remove it, translations inherit it"
                )
        got = skeleton(body)
        if got != origin.skeleton:
            raise ValueError(
                f"{path.name}: dialogue does not match the original.\n"
                f"    original ({origin.slug}.md): {' '.join(origin.skeleton)}\n"
                f"    translation:                {' '.join(got)}"
            )
        self.lang = lang
        self.origin = origin
        self.title = meta["title"]
        self.tldr = meta["tldr"]
        self.body_html = render_dialogue(body)
        # Inherited — the original is the single source of truth.
        self.date = origin.date
        self.conversation = origin.conversation
        self.status = origin.status
        self.original = origin.original
        self.slug = origin.slug

    @property
    def url(self) -> str:
        return f"/{self.lang}/piece/{self.slug}/"

    def versions(self) -> dict[str, str]:
        return self.origin.versions()


def load_pieces() -> list[Piece]:
    pieces = []
    for path in sorted(PIECES.glob("*.md")):
        piece = Piece(path)  # malformed pieces fail the build loudly — by design
        if piece.status == "published":
            pieces.append(piece)
        else:
            print(f"  skipping draft: {path.name}")
    pieces.sort(key=lambda p: (p.date, p.slug))
    load_translations(pieces)
    return pieces


def load_translations(pieces: list[Piece]) -> None:
    """Attach pieces/<lang>/<stem>-<lang>.md to their originals.

    The language is stated twice, in the directory and in the filename, and
    they must agree: redundancy is cheap here and useful later (Mike,
    2026-09-03), but only while something checks it — otherwise it is just
    a second thing that can drift.
    """
    by_slug = {p.slug: p for p in pieces}
    drafts = {p.stem for p in PIECES.glob("*.md")} - set(by_slug)
    # Walk what is actually ON DISK, not what the registry expects: a folder
    # nobody declared is a typo or a language half-added, and either way
    # silently skipping it would hide a whole locale.
    for folder in sorted(p for p in PIECES.iterdir() if p.is_dir()):
        code = folder.name
        if code == DEFAULT_LANG or code not in LANGUAGES:
            raise ValueError(
                f"pieces/{code}/: unknown language folder — add {code!r} to "
                f"LANGUAGES (and UI) or rename it"
            )
        if code not in UI:
            raise ValueError(f"pieces/{code}/ exists but UI[{code!r}] does not")
        for path in sorted(folder.glob("*.md")):
            stem = path.stem
            if not stem.endswith(f"-{code}"):
                raise ValueError(
                    f"pieces/{code}/{path.name}: filename must end in '-{code}' "
                    f"to match its folder"
                )
            slug = stem.removesuffix(f"-{code}")
            origin = by_slug.get(slug)
            if origin is None:
                if slug in drafts:
                    print(f"  skipping translation of a draft: {code}/{path.name}")
                    continue
                raise ValueError(
                    f"pieces/{code}/{path.name}: no original at pieces/{slug}.md"
                )
            origin.translations[code] = Translation(path, code, origin)


# --- page shell -----------------------------------------------------------------

def _asset_version() -> str:
    """Short content hash over the assets — appended as ?v= so browsers
    re-fetch exactly when a design change ships (no more stale-cache
    confusion during design iteration; live incident 2026-07-16)."""
    digest = hashlib.sha256()
    for path in sorted(ASSETS.glob("*")):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


_ASSET_V = None  # computed once per build in main()


def _lang_switch(lang: str, versions: dict[str, str], locales: list[str]) -> str:
    """Top-right switcher: a <details> dropdown, no JavaScript.

    EVERY language the site publishes is listed, always — the switcher is
    masthead furniture, not page metadata. It first shipped listing only
    the languages a page already existed in, which meant the control
    disappeared entirely from a freshly published piece whose translations
    hadn't landed yet: the reader loses the way to the other languages, and
    the masthead changes shape from page to page (Mike, 2026-09-03).

    A language that doesn't have THIS page yet still isn't a dead end — it
    links to that language's index and says so on hover.
    """
    others = [c for c in locales if c != lang]
    if not others:
        return ""

    def entry(code: str) -> str:
        url, extra = versions.get(code), ""
        if url is None:  # published in this language, but not this piece
            url = f"{lang_root(code)}/conversations/"
            extra = (
                f' class="lang-elsewhere" '
                f'title="{html.escape(t(code, "no_translation"), quote=True)}"'
            )
        return (
            f'<li><a href="{url}" lang="{LANGUAGES[code][0]}" '
            f'hreflang="{LANGUAGES[code][0]}"{extra}>'
            f'<span class="lang-flag" aria-hidden="true">{LANGUAGES[code][2]}</span>'
            f"{html.escape(LANGUAGES[code][1])}</a></li>"
        )

    items = "".join(
        entry(c) for c in sorted(others, key=lambda c: list(LANGUAGES).index(c))
    )
    # The button is the flag alone — one glyph, so the masthead stays on one
    # row even on a phone. The language it stands for is in the aria-label,
    # never only in the picture.
    label = f'{t(lang, "lang_label")}: {LANGUAGES[lang][1]}'
    return (
        f'<details class="lang-switch">'
        f'<summary aria-label="{html.escape(label, quote=True)}">'
        f'<span class="lang-flag" aria-hidden="true">{LANGUAGES[lang][2]}</span>'
        f'<span class="lang-caret" aria-hidden="true">▾</span></summary>'
        f"<ul>{items}</ul></details>"
    )


def _suggest_bar(lang: str, versions: dict[str, str]) -> str:
    """The offer to switch — never a redirect (Mike, 2026-09-03).

    GitHub Pages is a static CDN: Accept-Language never reaches us and geo
    would mean an edge runtime plus IP handling. navigator.language in the
    browser is both the better signal and the honest one — but a hard
    redirect would send a German-browser reader who clicked an English link
    on X somewhere they didn't ask to go. So: one dismissible line, filled
    in by assets/lang.js, in the language being OFFERED.
    """
    others = {c: u for c, u in versions.items() if c != lang}
    if not others:
        return ""
    offers = "".join(
        f'<template data-lang="{c}" data-tag="{LANGUAGES[c][0]}" data-url="{u}">'
        f'<span>{html.escape(t(c, "suggest"))}</span>'
        f'<a href="{u}">{html.escape(t(c, "suggest_go"))}</a>'
        f'<button type="button" data-dismiss>{html.escape(t(c, "suggest_dismiss"))}</button>'
        f"</template>"
        for c, u in others.items()
    )
    return f'<div class="lang-suggest" id="lang-suggest" hidden>{offers}</div>'


def shell(
    *, title: str, description: str, content: str, canonical: str = "",
    main_class: str = "", lang: str = DEFAULT_LANG,
    versions: dict[str, str] | None = None,
    locales: list[str] | None = None,
) -> str:
    """`main_class="full"` drops the text-column constraint so a page can
    alternate full-width bands with `.column` sections — the about page's
    banner sits between two voices and must span the page. Doing that from
    inside the column would need a 100vw breakout, which adds the
    scrollbar's width and hands every desktop a horizontal scrollbar.

    `versions` maps language code → URL for THIS page: it drives the
    hreflang alternates and the suggestion bar, both of which may only
    name pages that exist. `locales` is every language the SITE publishes
    and drives the switcher, which lists all of them regardless.
    """
    versions = versions or {lang: canonical}
    locales = locales or list(versions)
    root = lang_root(lang)
    canonical_tag = (
        f'\n  <link rel="canonical" href="{BASE_URL}{canonical}">' if BASE_URL and canonical else ""
    )
    og_url = f'\n  <meta property="og:url" content="{BASE_URL}{canonical}">' if BASE_URL and canonical else ""
    # hreflang: every language this page exists in, plus x-default → English,
    # which is what tells search engines the root is the unprefixed original
    # rather than a seventh competing copy.
    alternates = "".join(
        f'\n  <link rel="alternate" hreflang="{LANGUAGES[c][0]}" href="{BASE_URL}{u}">'
        for c, u in sorted(versions.items(), key=lambda kv: list(LANGUAGES).index(kv[0]))
    )
    if len(versions) > 1 and DEFAULT_LANG in versions:
        alternates += (
            f'\n  <link rel="alternate" hreflang="x-default" '
            f'href="{BASE_URL}{versions[DEFAULT_LANG]}">'
        )
    return f"""<!doctype html>
<html lang="{LANGUAGES[lang][0]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="{LANGUAGES[lang][0]}">{og_url}{canonical_tag}{alternates}
  <link rel="stylesheet" href="/assets/style.css?v={_ASSET_V}">
  <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE, quote=True)}" href="{root}/feed.xml">
</head>
<body>
<header class="banner">
  <a class="site-title" href="{root}/">{html.escape(SITE_TITLE)}</a>
  <nav>
    <a href="{root}/conversations/">{html.escape(t(lang, "nav_all"))}</a>
    <a href="{root}/about/">{html.escape(t(lang, "nav_about"))}</a>
    <a href="{X_URL}" rel="me noopener" target="_blank" aria-label="My Conversations with JC on X">{_X_LOGO_SVG}</a>
    {_lang_switch(lang, versions, locales)}
  </nav>
</header>
{_suggest_bar(lang, versions)}
<main{f' class="{main_class}"' if main_class else ""}>
{content}
</main>
<footer class="banner footer">
  <span>Copyright {dt.date.today().year}</span>
  <a href="/impressum/">Impressum</a>
  <a href="mailto:{CONTACT}">{CONTACT}</a>
</footer>
<script src="/assets/spotlight.js?v={_ASSET_V}" defer></script>
<script src="/assets/lang.js?v={_ASSET_V}" defer></script>
</body>
</html>
"""


def render_piece_page(
    piece: Piece,
    prev: Piece | None,
    nxt: Piece | None,
    related: list[Piece] | None = None,
) -> str:
    # Prev/next: FIXED at the window edges, vertically centered — visible
    # wherever the reader is in the scroll (design revision 2026-07-16).
    # Absent neighbors simply don't render.
    def edge(p: Piece | None, cls: str, arrow: str, label: str) -> str:
        if p is None:
            return ""
        return (
            f'<a class="edge-nav {cls}" href="{p.url}" '
            f'title="{html.escape(p.title, quote=True)}">'
            f'<span class="edge-arrow" aria-hidden="true">{arrow}</span>'
            f'<span class="edge-label">{label}</span></a>'
        )

    # Date ABOVE the title, nav.al-style: quiet eyebrow, then the headline.
    # The eyebrow carries the publication date; when the conversation
    # happened on another day, that day is named too — the archive pieces
    # would otherwise read as if they were spoken the week they went out.
    lang = piece.lang
    convo = ""
    if piece.conversation and piece.conversation != piece.date:
        stamp = (
            f'<time datetime="{piece.conversation.isoformat()}">'
            f"{format_date(piece.conversation, lang)}</time>"
        )
        convo = f'<span class="convo-date">{t(lang, "convo_from").format(date=stamp)}</span>'
    heading = (
        f'<div class="piece-head">'
        f'<time datetime="{piece.date.isoformat()}">{format_date(piece.date, lang)}</time>'
        f"{convo}"
        f"<h1>{html.escape(piece.title)}</h1></div>"
    )
    # The tldr renders as an unlabeled lede — the essence in a sentence or
    # two, muted, between the date and the first bubble (design 2026-07-16).
    lede = f'<p class="lede">{_inline(piece.tldr)}</p>'

    # The page says so when these are not the words that were spoken. The
    # site's whole claim is that it prints what was actually said; a
    # translation isn't that, and the one line that admits it is what keeps
    # the claim true (Mike, 2026-09-03). Which way it points comes from the
    # piece's `original:` — usually English, not necessarily.
    note = ""
    if lang != piece.original:
        source = piece.versions().get(piece.original)
        if source:
            note = (
                f'<p class="translation-note">'
                + t(lang, "translated").format(
                    url=source, lang=html.escape(lang_name(lang, piece.original)),
                )
                + "</p>"
            )

    # Bottom trail (also nav.al-inspired): up to three other conversations.
    related_html = ""
    if related:
        items = "\n".join(
            f'<li><a href="{r.url}"><span class="rel-date">{r.date.isoformat()}</span> '
            f"<span class=\"rel-title\">{html.escape(r.title)}</span></a></li>"
            for r in related[:3]
        )
        related_html = (
            f'<aside class="related"><h2>{html.escape(t(lang, "related"))}</h2>'
            f"<ul>{items}</ul></aside>"
        )

    return (
        edge(prev, "nav-prev", "&lArr;", t(lang, "prev"))
        + edge(nxt, "nav-next", "&rArr;", t(lang, "next"))
        + heading + lede + note
        + f'<article class="dialogue">{piece.body_html}</article>'
        + related_html
    )


def render_index_page(pieces: list[Piece], lang: str = DEFAULT_LANG) -> str:
    items = "\n".join(
        f'<li><a href="{p.url}"><span class="idx-date">{p.date.isoformat()}</span>'
        f"<span class=\"idx-title\">{html.escape(p.title)}</span></a>"
        f'<p class="idx-tldr">{_inline(p.tldr)}</p></li>'
        for p in reversed(pieces)  # newest first
    )
    empty = f'<li>{html.escape(t(lang, "index_empty"))}</li>'
    return (
        f'<div class="piece-head"><h1>{html.escape(t(lang, "index_title"))}</h1></div>'
        f'<ul class="index">{items or empty}</ul>'
    )


# One picture, cut across its middle, with the page read through the cut —
# so each half describes its own part AND says where it stands. Marking the
# closing half decorative (alt="") would have left a screen reader walking
# past the page's whole visual argument in silence (Mike, 2026-08-14).
# It travels with the language: a German page that describes its own
# picture in English hands the screen reader a second problem.
ABOUT_HERO_ALT = {
    "en": {
        "top": (
            "Upper half of a portrait split down the middle: Mike's face on the "
            "left, a Shiva figure on the right, both dissolving into falling "
            "code. The picture continues below the text."
        ),
        "bottom": (
            "Lower half of the same portrait, closing the page: a shirt collar "
            "on the left, a rudraksha strand and dark robe on the right, the "
            "code still falling."
        ),
    },
    "de": {
        "top": (
            "Obere Hälfte eines mittig geteilten Porträts: links Mikes Gesicht, "
            "rechts eine Shiva-Gestalt, beide lösen sich in fallenden Code auf. "
            "Das Bild setzt sich unterhalb des Textes fort."
        ),
        "bottom": (
            "Untere Hälfte desselben Porträts, als Abschluss der Seite: links "
            "ein Hemdkragen, rechts eine Rudraksha-Kette und ein dunkles "
            "Gewand, der Code fällt weiter."
        ),
    },
    "es": {
        "top": (
            "Mitad superior de un retrato partido por el centro: a la izquierda "
            "el rostro de Mike, a la derecha una figura de Shiva, ambos "
            "disolviéndose en código que cae. La imagen continúa debajo del texto."
        ),
        "bottom": (
            "Mitad inferior del mismo retrato, cerrando la página: a la "
            "izquierda el cuello de una camisa, a la derecha un rosario de "
            "rudraksha y una túnica oscura; el código sigue cayendo."
        ),
    },
    "ru": {
        "top": (
            "Верхняя половина портрета, разделённого посередине: слева лицо "
            "Майка, справа фигура Шивы, оба растворяются в падающем коде. "
            "Изображение продолжается под текстом."
        ),
        "bottom": (
            "Нижняя половина того же портрета, завершающая страницу: слева "
            "воротник рубашки, справа нить рудракши и тёмное одеяние, код "
            "продолжает падать."
        ),
    },
    "uk": {
        "top": (
            "Верхня половина портрета, поділеного посередині: ліворуч обличчя "
            "Майка, праворуч постать Шіви, обидва розчиняються в коді, що "
            "падає. Зображення продовжується під текстом."
        ),
        "bottom": (
            "Нижня половина того самого портрета, що завершує сторінку: "
            "ліворуч комір сорочки, праворуч нитка рудракші й темне вбрання, "
            "код падає далі."
        ),
    },
    "hi": {
        "top": (
            "बीच से बँटे एक चित्र का ऊपरी आधा भाग: बाईं ओर माइक का चेहरा, दाईं ओर "
            "शिव की आकृति, दोनों गिरते हुए कोड में घुलते हुए। चित्र पाठ के नीचे "
            "जारी रहता है।"
        ),
        "bottom": (
            "उसी चित्र का निचला आधा भाग, जो पृष्ठ को समाप्त करता है: बाईं ओर कमीज़ "
            "का कॉलर, दाईं ओर रुद्राक्ष की माला और गहरे रंग का वस्त्र, कोड अब भी "
            "गिर रहा है।"
        ),
    },
    "zh": {
        "top": (
            "一幅从中间剖开的肖像的上半部分：左侧是 Mike 的面孔，右侧是湿婆的形象，"
            "两者都消融于坠落的代码之中。图像在正文下方继续。"
        ),
        "bottom": (
            "同一幅肖像的下半部分，为页面收尾：左侧是衬衫领口，右侧是一串念珠与深色"
            "长袍，代码仍在坠落。"
        ),
    },
}


def _about_blocks(text: str) -> str:
    """Paragraphs of the page. `> ` becomes the closing kicker, a short
    em-dash line the signature — both are how the source text already
    reads, so ABOUT.md stays a document rather than a template. A rule
    line separates the two voices in the source and renders as nothing:
    both accounts are set in the same type (Mike, 2026-08-13)."""
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        b = block.strip()
        if not b or re.fullmatch(r"-{3,}", b):
            continue
        if b.startswith("> "):
            out.append(f'<p class="about-kicker">{_inline(b[2:].strip())}</p>')
        elif b.startswith("—") and len(b) < 40:
            out.append(f'<p class="about-sign">{_inline(b)}</p>')
        else:
            out.append(f"<p>{_inline(b)}</p>")
    return "\n".join(out)


def render_about_hero(part: str, lang: str = DEFAULT_LANG) -> str:
    """One half of the portrait as a full-width band.

    The picture is cut across its middle: the top half opens the page, the
    bottom half closes it, and the text is read THROUGH the image (Mike,
    2026-08-14). Both halves are described — see ABOUT_HERO_ALT.
    """
    described = ABOUT_HERO_ALT.get(lang, ABOUT_HERO_ALT[DEFAULT_LANG])
    alt = html.escape(described[part], quote=True)
    return (
        f'<figure class="about-hero about-hero-{part}">'
        f'<img src="/assets/about-mikejc-{part}.jpg?v={_ASSET_V}" alt="{alt}" '
        f'width="1800" height="491">'
        f"</figure>"
    )


def render_about_page(path: Path, lang: str = DEFAULT_LANG) -> str:
    """Both accounts in one voice of type — the signatures carry the
    handover, no avatars or panels; an essay in two voices, not a chat.

    The portrait is cut in half and the text sits in the cut: top band,
    text, bottom band (Mike, 2026-08-14). Requires shell(main_class="full")
    — the bands span the page, the text carries its own column.
    """
    raw = path.read_text(encoding="utf-8").strip()
    title = "About us"
    if raw.startswith("# "):
        head, _, raw = raw.partition("\n")
        title = head[2:].strip()
    return "\n".join([
        render_about_hero("top", lang),
        '<div class="column">',
        f'<div class="piece-head"><h1>{html.escape(title)}</h1></div>',
        f'<div class="about-voice">{_about_blocks(raw)}</div>',
        "</div>",
        render_about_hero("bottom", lang),
    ])


def render_markdown_page(path: Path, fallback: str) -> str:
    text = path.read_text(encoding="utf-8") if path.exists() else fallback
    blocks = re.split(r"\n\s*\n", text.strip())
    parts = []
    for b in blocks:
        b = b.strip()
        if b.startswith("# "):
            parts.append(f'<div class="piece-head"><h1>{_inline(b[2:])}</h1></div>')
        elif b.startswith("## "):
            parts.append(f"<h2>{_inline(b[3:])}</h2>")
        else:
            parts.append(f"<p>{_inline(b)}</p>")
    return "\n".join(parts)


def render_feed(pieces: list[Piece], lang: str = DEFAULT_LANG) -> str:
    """One feed per language, each carrying only that language's pieces —
    subscribers to the English feed must not wake up to seven copies of
    every conversation. pubDate stays RFC-822 English by spec."""
    items = "\n".join(
        f"<item><title>{html.escape(p.title)}</title>"
        f"<link>{BASE_URL}{p.url}</link><guid>{BASE_URL}{p.url}</guid>"
        f"<pubDate>{p.date.strftime('%a, %d %b %Y')} 00:00:00 GMT</pubDate>"
        f"<description>{html.escape(p.tldr)}</description></item>"
        for p in reversed(pieces)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{html.escape(SITE_TITLE)}</title>"
        f"<link>{BASE_URL}{lang_root(lang)}/</link>"
        f"<language>{LANGUAGES[lang][0]}</language>"
        f'<description>{html.escape(t(lang, "feed_desc"))}</description>{items}'
        "</channel></rss>\n"
    )


# --- build ----------------------------------------------------------------------

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def about_source(lang: str) -> Path:
    """English keeps ABOUT.md at the root (it was there first); the other
    languages mirror the pieces layout — pages/<lang>/about-<lang>.md."""
    if lang == DEFAULT_LANG:
        return ROOT / "ABOUT.md"
    return PAGES / lang / f"about-{lang}.md"


def build_locale(lang: str, views: list, languages: list[str]) -> None:
    """One language's whole site under /<lang>/ (English: the root).

    `views` are that language's pieces — Piece for English, Translation
    otherwise; both carry the same attributes on purpose, so every renderer
    below is language-blind. Prev/next and the index walk only THIS
    language, so a locale never hands its reader a dead end.
    """
    out = SITE / lang if lang != DEFAULT_LANG else SITE
    root = lang_root(lang)

    def related_for(piece, prev, nxt) -> list:
        """Neighbors first, then newest-first fill — deduped, max 3."""
        rel: list = []
        for c in [prev, nxt] + list(reversed(views)):
            if c is not None and c is not piece and c not in rel:
                rel.append(c)
        return rel[:3]

    for i, piece in enumerate(views):
        prev = views[i - 1] if i > 0 else None
        nxt = views[i + 1] if i < len(views) - 1 else None
        write(
            out / "piece" / piece.slug / "index.html",
            shell(title=f"{piece.title} — {SITE_TITLE}", description=piece.tldr,
                  content=render_piece_page(piece, prev, nxt,
                                            related_for(piece, prev, nxt)),
                  canonical=piece.url, lang=lang, versions=piece.versions(),
                  locales=languages),
        )

    # Homepage = the latest conversation (decided 2026-07-16); canonical
    # points at the piece URL so the two copies don't compete in search.
    home_versions = {c: f"{lang_root(c)}/" for c in languages}
    if views:
        latest, prev = views[-1], (views[-2] if len(views) > 1 else None)
        home = render_piece_page(latest, prev, None, related_for(latest, prev, None))
        home_desc = latest.tldr
    else:
        home = (
            f'<div class="piece-head"><h1>{html.escape(t(lang, "coming_soon"))}</h1></div>'
            f'<p class="narration">{html.escape(t(lang, "coming_soon_body"))}</p>'
        )
        home_desc = t(lang, "feed_desc")
    write(out / "index.html",
          shell(title=SITE_TITLE, description=home_desc, content=home,
                canonical=(views[-1].url if views else ""),
                lang=lang, versions=home_versions, locales=languages))

    write(out / "conversations" / "index.html",
          shell(title=f'{t(lang, "index_title")} — {SITE_TITLE}',
                description=t(lang, "index_desc"),
                content=render_index_page(views, lang),
                canonical=f"{root}/conversations/", lang=lang, locales=languages,
                versions={c: f"{lang_root(c)}/conversations/" for c in languages}))

    about_src = about_source(lang)
    if about_src.exists():
        write(out / "about" / "index.html",
              shell(title=f'{t(lang, "nav_about")} — {SITE_TITLE}',
                    description=t(lang, "about_desc"),
                    content=render_about_page(about_src, lang),
                    main_class="full", canonical=f"{root}/about/", lang=lang,
                    locales=languages,
                    versions={c: f"{lang_root(c)}/about/" for c in languages
                              if about_source(c).exists()}))

    write(out / "feed.xml", render_feed(views, lang))


def main() -> int:
    global _ASSET_V
    print(f"building {SITE_TITLE} …")
    _ASSET_V = _asset_version()
    if SITE.exists():
        shutil.rmtree(SITE)
    pieces = load_pieces()

    # A language exists on the site once it has at least one conversation.
    # Adding Spanish is adding files, not editing the builder.
    languages = [DEFAULT_LANG] + [
        c for c in LANGUAGES
        if c != DEFAULT_LANG and any(c in p.translations for p in pieces)
    ]
    for lang in languages:
        views = (
            pieces if lang == DEFAULT_LANG
            else [p.translations[lang] for p in pieces if lang in p.translations]
        )
        build_locale(lang, views, languages)
        if lang != DEFAULT_LANG and len(views) < len(pieces):
            # Visible in the build log, because the reader sees it too: the
            # switcher offers this language on every page, and on the ones
            # it hasn't reached yet the link goes to its index.
            print(f"    {len(pieces) - len(views)} piece(s) not yet in {lang}")
        if lang != DEFAULT_LANG:
            print(f"  {lang}: {len(views)}/{len(pieces)} piece(s)")

    # ONE Impressum, in German, at one URL, linked from every language: it
    # is the legal statement of a German-resident publisher under § 5 DDG,
    # and a translation of it would be a second text claiming to be the same
    # statement. The chrome stays in the site's default language; the legal
    # body is marked lang="de" so screen readers pronounce it correctly.
    write(SITE / "impressum" / "index.html",
          shell(title=f"Impressum — {SITE_TITLE}", description="Impressum",
                content='<div lang="de">' + render_markdown_page(
                    ROOT / "IMPRESSUM.md", "# Impressum\n\nContent coming soon.",
                ) + "</div>",
                canonical="/impressum/", locales=languages))
    # GitHub Pages custom-domain marker — must ship inside the artifact.
    write(SITE / "CNAME", DOMAIN + "\n")
    shutil.copytree(ASSETS, SITE / "assets")

    print(f"built {len(pieces)} piece(s) in {len(languages)} language(s) → {SITE}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
