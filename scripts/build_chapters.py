"""
Generate chapter pages for all (topic, level) combinations.

For each chapter:
  - If detailed answers exist in content/ folder (as Python module), render full Q&A.
  - Otherwise, render a stub listing the questions with a "detailed answers coming soon" note.
"""
import os
import sys
import importlib.util

sys.path.insert(0, "/home/claude/interview-prep-guide/scripts")

from html_common import (
    head_html, header_html, sidebar_html, footer_html,
    load_questions, esc
)
from site_data import (
    PARTS, LEVEL_ORDER, LEVEL_TIME_ESTIMATE, LEVEL_DESCRIPTIONS,
    file_for, slug_for, topic_part
)

OUT_DIR = "/home/claude/interview-prep-guide/chapters"
CONTENT_DIR = "/home/claude/interview-prep-guide/content"


def load_detailed_content(topic, level):
    """Try to load detailed answers module for a (topic, level) pair.
    Returns list of dicts: [{q, a, diagram?}] or None if not available."""
    slug = slug_for(topic, level).replace("-", "_")
    module_path = os.path.join(CONTENT_DIR, f"{slug}.py")
    if not os.path.exists(module_path):
        return None
    spec = importlib.util.spec_from_file_location(slug, module_path)
    if not spec or not spec.loader:
        return None
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "ANSWERS", None)
    except Exception as e:
        print(f"  [warn] Failed to load {module_path}: {e}")
        return None


def neighbors(topic, level, by_topic):
    """Return (prev, next) chapter links for navigation."""
    # Build ordered list of all (topic, level) pairs
    ordered = []
    for part in PARTS:
        for t in part["topics"]:
            if t in by_topic:
                for l in LEVEL_ORDER:
                    if l in by_topic[t]:
                        ordered.append((t, l))
    idx = ordered.index((topic, level))
    prev = ordered[idx - 1] if idx > 0 else None
    nxt = ordered[idx + 1] if idx < len(ordered) - 1 else None
    return prev, nxt


def nav_link_html(pair, direction):
    if not pair:
        return '<div></div>'
    t, l = pair
    cls = "chapter-nav__prev" if direction == "prev" else "chapter-nav__next"
    label = "← Previous" if direction == "prev" else "Next →"
    return f"""<a class="{cls}" href="{esc(file_for(t, l))}">
      <span class="chapter-nav__dir">{label}</span>
      <span class="chapter-nav__title">{esc(t)} — {esc(l)}</span>
    </a>"""


def render_qa_block(i, q, a=None, diagram=None):
    """Render a single Q&A block."""
    # Anchor id
    anchor = f"q{i}"
    question_html = esc(q)
    if a:
        # a is expected to be HTML (may contain <p>, <pre>, etc.)
        answer_html = a
    else:
        answer_html = (
            '<p style="color: var(--text-muted); font-style: italic;">'
            'Detailed explanation coming soon. In the meantime, try researching this question on your own — '
            'teaching yourself is the most effective study method.</p>'
        )
    diagram_html = diagram if diagram else ""
    return f"""
<article class="qa" id="{anchor}">
  <div class="qa__number">Question {i}</div>
  <h3 class="qa__question">{question_html}</h3>
  <div class="qa__answer">
    {answer_html}
    {diagram_html}
  </div>
</article>"""


def build_chapter(topic, level, questions, by_topic):
    """Generate a single chapter HTML file."""
    fname = file_for(topic, level)
    out_path = os.path.join(OUT_DIR, fname)

    detailed = load_detailed_content(topic, level)
    has_details = detailed is not None and len(detailed) > 0

    # Build Q&A blocks
    # detailed is a dict keyed by 1-based question number; values are HTML strings
    qa_blocks = []
    for i, q in enumerate(questions, start=1):
        answer_html = None
        if has_details and i in detailed:
            answer_html = detailed[i]
        qa_blocks.append(render_qa_block(i, q, answer_html, None))

    # Build TOC
    toc_items = []
    for i, q in enumerate(questions, start=1):
        short_q = q if len(q) < 90 else q[:87] + "..."
        toc_items.append(
            f'<li><a href="#q{i}"><span class="toc__num">{i}.</span>{esc(short_q)}</a></li>'
        )

    # Prev/next navigation
    prev, nxt = neighbors(topic, level, by_topic)

    # Part info for breadcrumb
    part = topic_part(topic)
    part_label = esc(part["title"]) if part else ""

    # Header status message
    status_html = ""
    if not has_details:
        status_html = """
        <div class="callout callout--info" style="margin-top: 1.2rem;">
          <div class="callout__title">Listing mode</div>
          <p style="margin: 0;">This chapter shows the full question list. Detailed beginner-friendly explanations with code examples and diagrams will be added progressively. Use the questions below as a study checklist — research each one, write your own answer, then verify.</p>
        </div>"""

    html = f"""{head_html(
        f"{topic} — {level} · Interview Prep Mastery",
        f"{len(questions)} {level.lower()} interview questions on {topic}, with detailed explanations and examples."
    , rel_prefix="../")}
{header_html(rel_prefix="../")}
<div class="layout">
{sidebar_html(current_file=fname, rel_prefix="../")}
<main class="main" id="main">

  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb__sep">›</span>
    <a href="../index.html#part-{part['id']}">{part_label}</a>
    <span class="breadcrumb__sep">›</span>
    <span>{esc(topic)} — {esc(level)}</span>
  </nav>

  <header class="chapter-header">
    <div class="chapter-label">{esc(topic)} · {esc(level)}</div>
    <h1 class="chapter-title">{esc(level)} {esc(topic)} Interview Questions</h1>
    <p class="chapter-lede">{esc(LEVEL_DESCRIPTIONS.get(level, ''))}</p>
    <div class="chapter-meta">
      <div class="chapter-meta__item"><span class="chapter-meta__label">Questions</span><span class="chapter-meta__value">{len(questions)}</span></div>
      <div class="chapter-meta__item"><span class="chapter-meta__label">Level</span><span class="chapter-meta__value">{esc(level)}</span></div>
      <div class="chapter-meta__item"><span class="chapter-meta__label">Estimated reading</span><span class="chapter-meta__value">{esc(LEVEL_TIME_ESTIMATE.get(level, ''))}</span></div>
    </div>
    {status_html}
  </header>

  <section class="prose">

    <div class="toc" id="toc">
      <div class="toc__title">All questions in this chapter</div>
      <ul class="toc__list">
        {''.join(toc_items)}
      </ul>
    </div>

    {''.join(qa_blocks)}

    <nav class="chapter-nav" aria-label="Chapter navigation">
      {nav_link_html(prev, 'prev')}
      {nav_link_html(nxt, 'next')}
    </nav>

  </section>

</main>
</div>
{footer_html(rel_prefix="../")}
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def build_all():
    qdata = load_questions()
    by_topic = qdata["data"]
    os.makedirs(OUT_DIR, exist_ok=True)

    count = 0
    detailed_count = 0
    for part in PARTS:
        for topic in part["topics"]:
            if topic not in by_topic:
                continue
            for level in LEVEL_ORDER:
                if level not in by_topic[topic]:
                    continue
                questions = by_topic[topic][level]
                detailed = load_detailed_content(topic, level)
                tag = "[DETAILED]" if detailed else "[stub   ]"
                if detailed:
                    detailed_count += 1
                build_chapter(topic, level, questions, by_topic)
                count += 1
                print(f"  {tag} {file_for(topic, level)}  ({len(questions)} Q)")

    print(f"\nBuilt {count} chapter pages  ({detailed_count} with detailed answers)")


if __name__ == "__main__":
    build_all()
