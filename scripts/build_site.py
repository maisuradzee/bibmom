#!/usr/bin/env python3
"""Build a safe, static NOEMA website from the approved publication index.

Only Markdown files referenced by data/research.json and located inside
research/published/ are rendered. Drafts are never copied into the public site.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import markdown


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TAGS = {
    "a", "blockquote", "br", "code", "del", "div", "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "li", "ol", "p", "pre", "span", "strong",
    "table", "tbody", "td", "th", "thead", "tr", "ul",
}
VOID_TAGS = {"br", "hr"}
SAFE_CLASSES = re.compile(r"^[A-Za-z0-9 _-]{1,160}$")
SAFE_IDS = re.compile(r"^[A-Za-z0-9_:-]{1,120}$")
SAFE_ALIGN = re.compile(r"^text-align:\s*(left|right|center);?$", re.I)


def safe_href(value: str) -> bool:
    """Allow normal web links, mailto, fragments, and local relative links."""
    candidate = value.strip()
    if not candidate or candidate.startswith(("//", "\\\\")) or "\\" in candidate:
        return False
    parsed = urlsplit(candidate)
    if parsed.scheme:
        return parsed.scheme.lower() in {"http", "https", "mailto"}
    return not parsed.netloc


class SafeHTML(HTMLParser):
    """Small allow-list sanitizer for rendered, repository-controlled Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED_TAGS:
            return
        clean: list[tuple[str, str]] = []
        for name, raw_value in attrs:
            value = raw_value or ""
            if name == "class" and SAFE_CLASSES.fullmatch(value):
                clean.append((name, value))
            elif name == "id" and SAFE_IDS.fullmatch(value):
                clean.append((name, value))
            elif tag == "a" and name == "href" and safe_href(value):
                clean.append((name, value))
            elif tag == "a" and name == "title":
                clean.append((name, value[:300]))
            elif tag in {"td", "th"} and name == "style" and SAFE_ALIGN.fullmatch(value):
                clean.append((name, value))
            elif tag in {"td", "th"} and name in {"colspan", "rowspan"} and value.isdigit():
                clean.append((name, value))
            elif tag == "ol" and name == "start" and value.isdigit():
                clean.append((name, value))

        rendered_attrs = "".join(
            f' {name}="{html.escape(value, quote=True)}"' for name, value in clean
        )
        self.parts.append(f"<{tag}{rendered_attrs}>")
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag not in self.stack:
            return
        while self.stack:
            current = self.stack.pop()
            self.parts.append(f"</{current}>")
            if current == tag:
                break

    def handle_data(self, data: str) -> None:
        self.parts.append(html.escape(data, quote=False))

    def render(self, fragment: str) -> str:
        self.feed(fragment)
        self.close()
        while self.stack:
            self.parts.append(f"</{self.stack.pop()}>")
        return "".join(self.parts)


def render_markdown(source: str) -> str:
    rendered = markdown.markdown(
        source,
        extensions=["extra", "toc", "sane_lists"],
        output_format="html5",
    )
    return SafeHTML().render(rendered)


def load_public_items(root: Path) -> list[dict[str, str]]:
    index_path = root / "data" / "research.json"
    public_roots = {
        "published": (root / "research" / "published").resolve(),
        "preliminary": (root / "research" / "preprints").resolve(),
    }
    data = json.loads(index_path.read_text(encoding="utf-8"))

    if data.get("project") != "NOEMA" or data.get("schema_version") != 1:
        raise ValueError("research.json has an unsupported project/schema version")
    items = data.get("research")
    if not isinstance(items, list):
        raise ValueError("research.json: research must be an array")

    seen_ids: set[str] = set()
    seen_outputs: set[str] = set()
    output: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("research.json: each research entry must be an object")
        required = ("id", "title", "date", "category", "summary", "file", "status")
        for field in required:
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"research.json: missing non-empty field {field!r}")
        status = item["status"]
        if status not in {"preliminary", "published"}:
            raise ValueError(f"{item['id']}: public status must be preliminary or published")
        public_root = public_roots[status]
        public_prefix = f"research/{'preprints' if status == 'preliminary' else 'published'}/"
        if item["id"] in seen_ids:
            raise ValueError(f"research.json: duplicate id {item['id']!r}")
        seen_ids.add(item["id"])

        relative = item["file"]
        if "\\" in relative or not relative.startswith(public_prefix) or not relative.endswith(".md"):
            raise ValueError(f"{item['id']}: file must be a Markdown file inside {public_prefix}")
        source_path = (root / relative).resolve()
        if public_root not in source_path.parents or not source_path.is_file():
            raise ValueError(f"{item['id']}: source file is missing or escapes {public_prefix}")

        slug = source_path.stem
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}", slug):
            raise ValueError(f"{item['id']}: unsafe output file name {slug!r}")
        if slug in seen_outputs:
            raise ValueError(f"{item['id']}: duplicate article output name {slug!r}")
        seen_outputs.add(slug)

        output_item = {key: value for key, value in item.items() if key not in {"file", "url"}}
        output_item["url"] = f"./research/articles/{slug}.html"
        output.append(output_item)

    return output


def build_site(root: Path, output: Path) -> dict[str, int]:
    root = root.resolve()
    output = output.resolve()
    if output == root or output in root.parents:
        raise ValueError("output directory must not replace or contain the source repository")

    items = load_public_items(root)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    shutil.copy2(root / "index.html", output / "index.html")
    shutil.copytree(root / "assets", output / "assets")
    (output / "data").mkdir(parents=True)
    (output / "research" / "articles").mkdir(parents=True)

    public_index = {
        "project": "NOEMA",
        "schema_version": 1,
        "research": items,
    }
    (output / "data" / "research.json").write_text(
        json.dumps(public_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    schema_path = root / "data" / "research.schema.json"
    if schema_path.is_file():
        shutil.copy2(schema_path, output / "data" / "research.schema.json")

    for item in items:
        url = item["url"]
        slug = Path(url).stem
        source_relative = next(
            entry["file"]
            for entry in json.loads((root / "data" / "research.json").read_text(encoding="utf-8"))["research"]
            if entry["id"] == item["id"]
        )
        source_path = (root / source_relative).resolve()
        content_html = render_markdown(source_path.read_text(encoding="utf-8"))
        title = html.escape(item["title"], quote=True)
        description = html.escape(item["summary"][:280], quote=True)
        category = html.escape(item["category"], quote=True)
        date = html.escape(item["date"], quote=True)
        if item["status"] == "preliminary":
            status_label = "წინასწარი კვლევა · AI-ით დამუშავებული · დამოუკიდებელი რეცენზია არ დასრულებულა"
            status_class = "preliminary"
        else:
            status_label = "გამოქვეყნებული კვლევა"
            status_class = "published"

        page = f"""<!doctype html>
<html lang="ka">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#101820">
  <meta name="robots" content="index,follow">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'">
  <title>{title} — NOEMA</title>
  <link rel="stylesheet" href="../../assets/styles.css">
  <link rel="stylesheet" href="../../assets/articles.css">
</head>
<body class="article-page">
  <header class="article-header">
    <a class="brand" href="../../index.html" aria-label="NOEMA მთავარი გვერდი"><span class="brand-mark">N</span><span>NOEMA</span></a>
    <a class="article-back" href="../../index.html#research">კვლევების არქივი ↗</a>
  </header>
  <main class="article-main">
    <div class="article-status article-status--{status_class}">{status_label}</div>
    <div class="article-meta">{category} <span>·</span> {date}</div>
    <article class="article-content">{content_html}</article>
    <div class="article-bottom"><a class="text-link" href="../../index.html#research">← დაბრუნება კვლევების არქივში</a></div>
  </main>
  <footer class="site-footer"><a class="brand" href="../../index.html"><span class="brand-mark">N</span><span>NOEMA</span></a><span>დამოუკიდებელი კვლევა · 2026</span><span>Built to question.</span></footer>
</body>
</html>
"""
        (output / "research" / "articles" / f"{slug}.html").write_text(page, encoding="utf-8")

    (output / ".nojekyll").write_text("", encoding="utf-8")
    published_count = sum(item["status"] == "published" for item in items)
    preliminary_count = sum(item["status"] == "preliminary" for item in items)
    return {
        "published_articles": published_count,
        "preliminary_articles": preliminary_count,
        "generated_html_pages": len(items),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="NOEMA repository root")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for the public site")
    args = parser.parse_args()
    result = build_site(args.root, args.output)
    print(
        "NOEMA site build OK: "
        f"{result['published_articles']} published, "
        f"{result['preliminary_articles']} preliminary, "
        f"{result['generated_html_pages']} generated HTML page(s)"
    )


if __name__ == "__main__":
    main()
