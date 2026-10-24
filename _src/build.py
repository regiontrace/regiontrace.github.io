"""Write the policy pages of regiontrace.com from the markdown beside this script. GitHub
Pages leaves out folders whose names start with "_", so this folder stays off the site.

    pip install markdown
    python3 _src/build.py .

writes privacy/index.html, terms/index.html and accessibility/index.html. When a page's
text changes, change its date in PAGES.
"""
import html
import re
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).parent
PAGES = {
    # slug: title, description, adapted from Basecamp's policies, date of the last change
    "privacy": ("Privacy policy", "How Regiontrace collects, uses and protects your information.", True, "October 21, 2026"),
    "terms": ("Terms of use", "The terms for your use of Regiontrace.", True, "October 21, 2026"),
    "accessibility": ("Accessibility statement", "The accessibility of Regiontrace, its known limits and how to report a problem.", False, "October 23, 2026"),
}
CREDIT = ('<p class="credit">Adapted from the <a href="https://github.com/basecamp/policies">Basecamp '
          'open-source policies</a> / <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>')

STYLE = """
  :root {
    --bg: #f7f6f2;
    --ink: #1b1f23;
    --muted: #5b6168;
    --line: #dddbd3;
    --accent: #1f6f6a;
    --accent-soft: #e3eeec;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #14171a;
      --ink: #e8e6e1;
      --muted: #a3a8ad;
      --line: #343a40;
      --accent: #6cc2b9;
      --accent-soft: #1d2b2a;
    }
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font: 17px/1.6 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }
  .wrap { max-width: 720px; margin: 0 auto; padding: 56px 20px 40px; }
  header { display: flex; align-items: center; gap: 12px; }
  header svg { width: 34px; height: 34px; flex: none; }
  .home { display: flex; align-items: center; gap: 12px; color: var(--ink); text-decoration: none; }
  .wordmark { font-size: 22px; font-weight: 650; letter-spacing: -0.01em; }
  .signin { margin-left: auto; padding: 6px 16px; border: 1px solid var(--accent); border-radius: 8px; font-size: 15px; font-weight: 550; text-decoration: none; }
  .signin:hover { background: var(--accent-soft); }
  .skip { position: absolute; left: -9999px; }
  .skip:focus { left: 16px; top: 12px; background: var(--bg); padding: 4px 8px; }
  a { color: var(--accent); text-underline-offset: 3px; }
  a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  h1, h2 { font-family: ui-serif, Georgia, "Times New Roman", serif; font-weight: 500; letter-spacing: -0.01em; }
  h1 { font-size: clamp(32px, 6vw, 44px); line-height: 1.15; margin: 56px 0 8px; }
  h2 { font-size: 26px; line-height: 1.25; margin: 44px 0 12px; }
  h3 { font-size: 17px; font-weight: 650; margin: 28px 0 6px; }
  p { margin: 0 0 16px; }
  ul, ol { margin: 0 0 16px; padding-left: 24px; }
  li { margin: 6px 0; }
  .updated { color: var(--muted); font-size: 15px; margin-bottom: 28px; }
  .toc { margin: 0 0 8px; padding: 14px 20px; background: var(--accent-soft); border-radius: 10px; font-size: 15px; }
  .toc h2 { font-family: inherit; font-size: 15px; font-weight: 650; margin: 0 0 6px; letter-spacing: 0; }
  .toc ol { margin: 0; }
  .toc li { margin: 2px 0; }
  .table { overflow-x: auto; margin: 0 0 16px; }
  table { border-collapse: collapse; width: 100%; font-size: 15px; }
  th, td { text-align: left; vertical-align: top; padding: 8px 10px 8px 0; border-bottom: 1px solid var(--line); }
  th { font-weight: 650; }
  .credit { margin-top: 40px; font-size: 14px; color: var(--muted); }
  footer { margin-top: 48px; font-size: 14px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 18px; }
  footer a { color: var(--muted); }
  footer a[aria-current] { color: var(--ink); text-decoration: none; }
"""

MARK = """<svg viewBox="0 0 32 32" aria-hidden="true">
        <rect x="1.5" y="1.5" width="29" height="29" rx="7" fill="none" stroke="currentColor" stroke-width="2" opacity=".35"/>
        <path d="M6 23 L12 15 L17 19 L25 8" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="25" cy="8" r="2.6" fill="var(--accent)"/>
      </svg>"""


def footer(current: str) -> str:
    here = ' aria-current="page"'
    links = [f'<a href="/{p}/"{here if p == current else ""}>{PAGES[p][0].split()[0]}</a>' for p in PAGES]
    return ('<footer>\n    <span>&copy; 2026 Regiontrace</span>\n    ' + "\n    ".join(links) +
            '\n    <a href="https://www.linkedin.com/company/regiontrace">LinkedIn</a>\n  </footer>')


def page(slug: str) -> str:
    title, description, adapted, updated = PAGES[slug]
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"])
    text = (HERE / f"{slug}.md").read_text()
    body = md.convert(text)
    # the h1 comes from the markdown; the date and the contents go under it
    h1, rest = body.split("</h1>", 1)
    sections = [t for t in md.toc_tokens[0]["children"]] if md.toc_tokens else []
    toc = ""
    if len(sections) > 4:
        items = "\n".join(f'      <li><a href="#{t["id"]}">{html.escape(t["name"], quote=False)}</a></li>' for t in sections)
        toc = f'<nav class="toc" aria-labelledby="contents">\n    <h2 id="contents">Contents</h2>\n    <ol>\n{items}\n    </ol>\n  </nav>\n'
    rest = re.sub(r"<table>(.*?)</table>", r'<div class="table"><table>\1</table></div>', rest, flags=re.S)
    # the contents go between the opening paragraphs and the first section
    if toc:
        i = rest.index("<h2")
        rest, toc = rest[:i] + toc + rest[i:], ""
    url = f"https://regiontrace.com/{slug}/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Regiontrace</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14171a" media="(prefers-color-scheme: dark)">
<style>{STYLE}</style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<div class="wrap">
  <header>
    <a class="home" href="/">
      {MARK}
      <span class="wordmark">Regiontrace</span>
    </a>
    <a class="signin" href="https://model.regiontrace.com/">Sign in</a>
  </header>

  <main id="content">
  {h1}</h1>
  <p class="updated">Last updated: {updated}</p>
  {toc}{rest.strip()}
  {CREDIT if adapted else ""}
  </main>

  {footer(slug)}
</div>
</body>
</html>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for slug in PAGES:
        if (HERE / f"{slug}.md").exists():
            (out / slug).mkdir(parents=True, exist_ok=True)
            (out / slug / "index.html").write_text(page(slug))
            print("wrote", slug)
