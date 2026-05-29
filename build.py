#!/usr/bin/env python3
"""Build index.html from tutorial.md (source of truth)."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import markdown
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "tutorial.md"
OUTPUT = ROOT / "index.html"
STYLESHEET = ROOT / "assets" / "tutorial.css"
SCAFFOLD_HTML = ROOT / "tutorial-scaffold.html"

INTERNAL_SECTION = re.compile(r"^## Page build notes\b", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONT_MATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
PRE_BLOCK = re.compile(r"<pre>(.*?)</pre>", re.DOTALL)


def slugify(value: str, separator: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", separator, value)


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, text[match.end() :]


def strip_internal_sections(text: str) -> str:
    match = INTERNAL_SECTION.search(text)
    if match:
        text = text[: match.start()].rstrip()
    return HTML_COMMENT.sub("", text).strip() + "\n"


def ensure_stylesheet() -> None:
    """Extract MarkView CSS from tutorial-scaffold.html if assets/tutorial.css is missing."""
    if STYLESHEET.exists() or not SCAFFOLD_HTML.exists():
        return

    html = SCAFFOLD_HTML.read_text(encoding="utf-8")
    start = html.index("<style>") + len("<style>")
    end = html.index("</style>", start)
    css = html[start:end].strip()
    lines = [line[4:] if line.startswith("    ") else line for line in css.splitlines()]
    STYLESHEET.parent.mkdir(exist_ok=True)
    STYLESHEET.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def postprocess_body(html: str) -> str:
    html = PRE_BLOCK.sub(
        r'<div class="markview-code-block-wrapper"><pre>\1</pre></div>',
        html,
    )
    html = html.replace("<img ", '<img loading="lazy" ')
    # Clickable checklists (visual only — state is not saved)
    html = re.sub(
        r'<input type="checkbox"\s+disabled\s*/?>',
        '<input type="checkbox">',
        html,
    )
    return html


def render_markdown(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=[
            TocExtension(slugify=slugify, separator="-", toc_depth=6),
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.sane_lists",
            "markdown.extensions.nl2br",
            "pymdownx.tasklist",
        ],
        extension_configs={
            "pymdownx.tasklist": {
                "custom_checkbox": False,
            },
        },
        output_format="html5",
    )


def build_html(meta: dict[str, str], body_html: str) -> str:
    title = meta.get("title", "Ghidra-ReAGS Quick Start")
    version = meta.get("version", "0.0.0")
    date = meta.get("date", "")
    status = meta.get("status", "draft")

    indented = "\n".join(
        f"    {line}" if line.strip() else line for line in body_html.splitlines()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="dark">
  <title>{title}</title>
  <meta name="description" content="Step-by-step guide: extract AGS game scripts with AGSUnpacker and decompile them in Ghidra 10.4 with ReAGS.">
  <link rel="stylesheet" href="assets/tutorial.css">
</head>
<body class="markdown-export" data-theme="dark">
  <header class="site-header">
    <div class="wrap">
      <div id="google_translate_element" class="site-translate"></div>
      <h1>{title}</h1>
      <p class="meta">Version {version} · {date} · {status}</p>
    </div>
  </header>
  <div id="markview-container" class="markdown-body code-block-scroll" style="max-width:1000px">
{indented}
  </div>
  <footer class="site-footer">
    <p>Built from <code>tutorial.md</code> · v{version} · {date} · <a href="https://github.com/selloa">selloa</a></p>
  </footer>
  <script>
  function googleTranslateElementInit() {{
    new google.translate.TranslateElement(
      {{
        pageLanguage: 'en',
        includedLanguages: 'en,de,fr,es,it,pt,ru,ja,ko,zh-CN',
        layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL,
      }},
      'google_translate_element'
    );
  }}
  </script>
  <script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
</body>
</html>
"""


def main() -> int:
    if not SOURCE.exists():
        print(f"Error: source file not found: {SOURCE}", file=sys.stderr)
        return 1

    ensure_stylesheet()
    if not STYLESHEET.exists():
        print(f"Error: stylesheet not found: {STYLESHEET}", file=sys.stderr)
        return 1

    raw = SOURCE.read_text(encoding="utf-8")
    meta, content = parse_front_matter(raw)
    content = strip_internal_sections(content)

    body_html = postprocess_body(render_markdown(content))
    html = build_html(meta, body_html)
    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} (from {SOURCE.name}, v{meta.get('version', '?')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
