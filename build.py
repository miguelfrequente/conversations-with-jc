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
    ---
    Curator narration (full-width, muted) …

    **M:** dialogue turn …

    **JC:** reply …
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
ASSETS = ROOT / "assets"
SITE = ROOT / "site"

SITE_TITLE = "My Conversations with JC"
DOMAIN = "conversationswithjc.com"  # bought 2026-07-17
BASE_URL = f"https://{DOMAIN}"      # canonical URLs, RSS links, OG tags
CONTACT = f"contact@{DOMAIN}"

# --- tiny markdown subset ------------------------------------------------------

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
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
        m = re.match(r"\*\*(JC|M|Mike)\s*:?\*\*\s*:?\s*(.*)", text, re.DOTALL | re.IGNORECASE)
        if m:
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

class Piece:
    def __init__(self, path: Path):
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
        for required in ("title", "date", "tldr", "status"):
            if not meta.get(required):
                raise ValueError(f"{path.name}: missing frontmatter field {required!r}")
        self.title = meta["title"]
        self.date = dt.date.fromisoformat(meta["date"])
        self.tldr = meta["tldr"]
        self.status = meta["status"]
        self.slug = path.stem
        self.body_html = render_dialogue(body)

    @property
    def url(self) -> str:
        return f"/piece/{self.slug}/"


def load_pieces() -> list[Piece]:
    pieces = []
    for path in sorted(PIECES.glob("*.md")):
        piece = Piece(path)  # malformed pieces fail the build loudly — by design
        if piece.status == "published":
            pieces.append(piece)
        else:
            print(f"  skipping draft: {path.name}")
    pieces.sort(key=lambda p: (p.date, p.slug))
    return pieces


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


def shell(*, title: str, description: str, content: str, canonical: str = "") -> str:
    canonical_tag = (
        f'\n  <link rel="canonical" href="{BASE_URL}{canonical}">' if BASE_URL and canonical else ""
    )
    og_url = f'\n  <meta property="og:url" content="{BASE_URL}{canonical}">' if BASE_URL and canonical else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:type" content="article">{og_url}{canonical_tag}
  <link rel="stylesheet" href="/assets/style.css?v={_ASSET_V}">
  <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE, quote=True)}" href="/feed.xml">
</head>
<body>
<header class="banner">
  <a class="site-title" href="/">{html.escape(SITE_TITLE)}</a>
  <nav>
    <a href="/conversations/">All conversations</a>
  </nav>
</header>
<main>
{content}
</main>
<footer class="banner footer">
  <span>Copyright {dt.date.today().year}</span>
  <a href="/impressum/">Impressum</a>
  <a href="mailto:{CONTACT}">{CONTACT}</a>
</footer>
<script src="/assets/spotlight.js?v={_ASSET_V}" defer></script>
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
    heading = (
        f'<div class="piece-head">'
        f'<time datetime="{piece.date.isoformat()}">{piece.date.strftime("%B %d, %Y")}</time>'
        f"<h1>{html.escape(piece.title)}</h1></div>"
    )
    # The tldr renders as an unlabeled lede — the essence in a sentence or
    # two, muted, between the date and the first bubble (design 2026-07-16).
    lede = f'<p class="lede">{_inline(piece.tldr)}</p>'

    # Bottom trail (also nav.al-inspired): up to three other conversations.
    related_html = ""
    if related:
        items = "\n".join(
            f'<li><a href="{r.url}"><span class="rel-date">{r.date.isoformat()}</span> '
            f"<span class=\"rel-title\">{html.escape(r.title)}</span></a></li>"
            for r in related[:3]
        )
        related_html = (
            '<aside class="related"><h2>More conversations</h2>'
            f"<ul>{items}</ul></aside>"
        )

    return (
        edge(prev, "nav-prev", "&lArr;", "Previous<br>Dialogue")
        + edge(nxt, "nav-next", "&rArr;", "Next<br>Dialogue")
        + heading + lede
        + f'<article class="dialogue">{piece.body_html}</article>'
        + related_html
    )


def render_index_page(pieces: list[Piece]) -> str:
    items = "\n".join(
        f'<li><a href="{p.url}"><span class="idx-date">{p.date.isoformat()}</span>'
        f"<span class=\"idx-title\">{html.escape(p.title)}</span></a>"
        f'<p class="idx-tldr">{_inline(p.tldr)}</p></li>'
        for p in reversed(pieces)  # newest first
    )
    return f'<div class="piece-head"><h1>All conversations</h1></div><ul class="index">{items or "<li>Nothing published yet.</li>"}</ul>'


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


def render_feed(pieces: list[Piece]) -> str:
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
        f"<title>{html.escape(SITE_TITLE)}</title><link>{BASE_URL}/</link>"
        f"<description>Curated dialogues between Mike and JC.</description>{items}"
        "</channel></rss>\n"
    )


# --- build ----------------------------------------------------------------------

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    global _ASSET_V
    print(f"building {SITE_TITLE} …")
    _ASSET_V = _asset_version()
    if SITE.exists():
        shutil.rmtree(SITE)
    pieces = load_pieces()

    def related_for(piece: Piece, prev: Piece | None, nxt: Piece | None) -> list[Piece]:
        """Neighbors first, then newest-first fill — deduped, max 3."""
        out: list[Piece] = []
        for c in [prev, nxt] + list(reversed(pieces)):
            if c is not None and c is not piece and c not in out:
                out.append(c)
        return out[:3]

    for i, piece in enumerate(pieces):
        prev = pieces[i - 1] if i > 0 else None
        nxt = pieces[i + 1] if i < len(pieces) - 1 else None
        write(
            SITE / "piece" / piece.slug / "index.html",
            shell(title=f"{piece.title} — {SITE_TITLE}", description=piece.tldr,
                  content=render_piece_page(piece, prev, nxt,
                                            related_for(piece, prev, nxt)),
                  canonical=piece.url),
        )

    # Homepage = the latest conversation (decided 2026-07-16); canonical
    # points at the piece URL so the two copies don't compete in search.
    if pieces:
        latest, prev = pieces[-1], (pieces[-2] if len(pieces) > 1 else None)
        home = render_piece_page(latest, prev, None,
                                 related_for(latest, prev, None))
        home_desc = latest.tldr
    else:
        home = '<div class="piece-head"><h1>Coming soon</h1></div><p class="narration">The first conversation is on its way.</p>'
        home_desc = "Curated dialogues between Mike and JC."
    write(SITE / "index.html",
          shell(title=SITE_TITLE, description=home_desc, content=home,
                canonical=(pieces[-1].url if pieces else "")))

    write(SITE / "conversations" / "index.html",
          shell(title=f"All conversations — {SITE_TITLE}",
                description="Every published dialogue, newest first.",
                content=render_index_page(pieces)))
    write(SITE / "impressum" / "index.html",
          shell(title=f"Impressum — {SITE_TITLE}", description="Impressum",
                content=render_markdown_page(ROOT / "IMPRESSUM.md", "# Impressum\n\nContent coming soon.")))
    write(SITE / "feed.xml", render_feed(pieces))
    # GitHub Pages custom-domain marker — must ship inside the artifact.
    write(SITE / "CNAME", DOMAIN + "\n")
    shutil.copytree(ASSETS, SITE / "assets")

    print(f"built {len(pieces)} piece(s) → {SITE}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
