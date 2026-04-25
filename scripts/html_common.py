"""
HTML generators for shared page chrome: head, header, sidebar, footer.
Reused by all page builders.
"""
import json
import html
from site_data import (
    PARTS, LEVEL_ORDER, LEVEL_SLUGS, LEVEL_TIME_ESTIMATE,
    file_for, slug_for, topic_part
)

DATA_PATH = "/home/claude/interview-prep-guide/data/questions.json"


def load_questions():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    """HTML-escape a string."""
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def head_html(title, description, rel_prefix=""):
    """Generate <head> section."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{rel_prefix}assets/styles.css">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%239a6b1d'/%3E%3Ctext x='50' y='68' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold' font-size='48'%3EIP%3C/text%3E%3C/svg%3E">
</head>
<body>"""


def header_html(rel_prefix=""):
    """Generate site header."""
    return f"""<header class="site-header">
  <div class="site-header__inner">
    <button class="menu-toggle" aria-label="Open menu" type="button">☰ Menu</button>
    <a class="brand" href="{rel_prefix}index.html">
      <span class="brand__mark">IP</span>
      <span class="brand__text">
        <span class="brand__title">Interview Prep Mastery</span>
        <span class="brand__subtitle">Interactive learning guide</span>
      </span>
    </a>
    <nav class="header-nav">
      <a href="{rel_prefix}index.html#roadmap">Roadmap</a>
      <a href="{rel_prefix}index.html#chapters">All chapters</a>
      <button class="theme-toggle" type="button" aria-label="Toggle color scheme">☾ Dark</button>
    </nav>
  </div>
</header>"""


def sidebar_html(current_file=None, rel_prefix=""):
    """Generate sidebar navigation with all parts and chapters."""
    qdata = load_questions()
    by_topic = qdata["data"]

    parts_out = []
    for part in PARTS:
        items = []
        for topic in part["topics"]:
            topic_levels = by_topic.get(topic, {})
            # Topic group heading
            items.append(f'<li style="padding: 0.5rem 0.8rem; color: var(--text); font-weight: 600; font-size: 0.82rem; margin-top: 0.3rem;">{esc(topic)}</li>')
            for level in LEVEL_ORDER:
                if level not in topic_levels:
                    continue
                fname = file_for(topic, level)
                active = "active" if fname == current_file else ""
                count = len(topic_levels[level])
                items.append(
                    f'<li><a class="{active}" href="{rel_prefix}chapters/{fname}">'
                    f'<span class="nav-item__title">{esc(level)}</span>'
                    f'<span class="nav-item__meta">{count} questions · {LEVEL_TIME_ESTIMATE.get(level, "")}</span>'
                    f'</a></li>'
                )
        part_html = f"""
        <div class="nav-part">
          <div class="nav-part__label">{esc(part['label'])}</div>
          <div class="nav-part__title">{esc(part['title'])}</div>
          <ul class="nav-part__list">
            {''.join(items)}
          </ul>
        </div>"""
        parts_out.append(part_html)

    return f"""<aside class="sidebar" aria-label="Site navigation">
  <div class="sidebar__header">Chapter Navigator</div>
  {''.join(parts_out)}
</aside>"""


def footer_html(rel_prefix=""):
    """Generate footer + script tag."""
    return f"""
<script src="{rel_prefix}assets/script.js"></script>
</body>
</html>"""
