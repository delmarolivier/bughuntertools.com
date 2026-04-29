#!/usr/bin/env python3
"""
convert-articles.py
Convert bughuntertools.com src/pages/articles/*/index.astro to
src/content/articles/<slug>.md Markdown files with frontmatter.

Each index.astro has the shape:
  ---
  import BaseLayout from ...;
  const title = '...';
  const description = '...';
  const date = 'YYYY-MM-DD';
  const html = `<article>...</article>`;
  ---
  <BaseLayout ...>
    <Fragment set:html={html} />
  </BaseLayout>

The body (html const) is extracted and embedded in the .md file as HTML
(Markdown supports inline HTML; Astro will render it).

Category assignment is based on slug pattern:
  CVE / RCE / vuln slugs           → security-news
  bug-bounty / kit / starter       → bug-bounty
  tools / best / pricing / burp    → tools
  research / guide / setup / lab / planner / securityclaw → research
"""

import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_SRC = REPO_ROOT / "src" / "pages" / "articles"
ARTICLES_DEST = REPO_ROOT / "src" / "content" / "articles"

# Category inference based on slug keywords
CATEGORY_RULES = [
    # tools
    (["security-testing-tools", "burp-suite", "pricing", "pentest-tool"],
     "tools"),
    # bug-bounty
    (["bug-bounty", "starter-kit", "bounty"],
     "bug-bounty"),
    # research
    (["security-lab", "setup-guide", "automated-penetration", "guide",
      "securityclaw", "planner", "scanner", "why-your-security",
      "roundup", "security-roundup"],
     "research"),
    # security-news (catch-all for CVE / RCE / vuln articles)
    (["cve", "rce", "exploit", "vuln", "zero-day", "patch",
      "n8n", "vllm", "vscode", "linkedin", "mshtml", "roguepilot",
      "firefox", "gcp", "dell", "adobe", "beyondtrust", "chainlit",
      "microsoft", "n8n"],
     "security-news"),
]

def infer_category(slug: str) -> str:
    s = slug.lower()
    for keywords, cat in CATEGORY_RULES:
        if any(kw in s for kw in keywords):
            return cat
    return "security-news"  # default


def extract_const(source: str, name: str) -> str | None:
    """
    Extract the value of a JS const from the frontmatter.
    Handles single-quoted, double-quoted, and backtick template literals.
    For backtick literals, captures everything up to the closing backtick
    (which may be on a different line).
    """
    # Single or double quoted string
    m = re.search(rf"const {name}\s*=\s*'((?:[^'\\]|\\.)*)'\s*;", source, re.DOTALL)
    if m:
        return m.group(1).replace("\\'", "'")

    m = re.search(rf'const {name}\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', source, re.DOTALL)
    if m:
        return m.group(1).replace('\\"', '"')

    # Template literal (backtick) — used for `html`
    m = re.search(rf"const {name}\s*=\s*`(.*?)`\s*;?\s*(?=---|\Z)", source, re.DOTALL)
    if m:
        return m.group(1)

    return None


def escape_yaml_string(s: str) -> str:
    """Wrap a string in double quotes for YAML, escaping internal quotes."""
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def convert_article(slug: str) -> dict:
    src_file = ARTICLES_SRC / slug / "index.astro"
    if not src_file.exists():
        return {"slug": slug, "ok": False, "error": "source file not found"}

    source = src_file.read_text(encoding="utf-8")

    # Extract frontmatter block (between the first pair of ---)
    fm_match = re.match(r"^---\n(.*?)\n---", source, re.DOTALL)
    if not fm_match:
        return {"slug": slug, "ok": False, "error": "no frontmatter block found"}

    frontmatter = fm_match.group(1)

    title = extract_const(frontmatter, "title")
    description = extract_const(frontmatter, "description")
    date = extract_const(frontmatter, "date")
    html_body = extract_const(frontmatter, "html")

    if not title:
        return {"slug": slug, "ok": False, "error": "could not extract title"}
    if not description:
        return {"slug": slug, "ok": False, "error": "could not extract description"}
    if not date:
        # Try to extract date from article body "Published: Month DD, YYYY"
        body_date_match = re.search(
            r'Published:\s*([A-Za-z]+ \d{1,2},?\s*\d{4})',
            html_body or source
        )
        if body_date_match:
            try:
                raw = body_date_match.group(1).replace(',', '').strip()
                parsed = datetime.strptime(raw, "%B %d %Y")
                date = parsed.strftime("%Y-%m-%d")
            except ValueError:
                pass
    if not date:
        return {"slug": slug, "ok": False, "error": "could not extract date"}
    if html_body is None:
        return {"slug": slug, "ok": False, "error": "could not extract html body"}

    category = infer_category(slug)

    # Build the .md file
    lines = [
        "---",
        f"title: {escape_yaml_string(title)}",
        f"description: {escape_yaml_string(description)}",
        f"date: {date}",
        f"category: {category}",
        "---",
        "",
        html_body.strip(),
        "",
    ]
    md_content = "\n".join(lines)

    dest_file = ARTICLES_DEST / f"{slug}.md"
    dest_file.write_text(md_content, encoding="utf-8")

    return {"slug": slug, "ok": True, "category": category, "date": date}


def main():
    ARTICLES_DEST.mkdir(parents=True, exist_ok=True)

    # Remove .gitkeep if present (we'll have real files now)
    gitkeep = ARTICLES_DEST / ".gitkeep"
    if gitkeep.exists():
        gitkeep.unlink()

    slugs = sorted(
        d.name for d in ARTICLES_SRC.iterdir()
        if d.is_dir() and (d / "index.astro").exists()
    )

    print(f"Converting {len(slugs)} articles...")
    ok = []
    errors = []

    for slug in slugs:
        result = convert_article(slug)
        if result["ok"]:
            ok.append(result)
            print(f"  ✅ {slug} → {result['category']} ({result['date']})")
        else:
            errors.append(result)
            print(f"  ❌ {slug}: {result['error']}", file=sys.stderr)

    print(f"\nDone: {len(ok)} converted, {len(errors)} failed.")
    if errors:
        print("Failures:", [e["slug"] for e in errors], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
