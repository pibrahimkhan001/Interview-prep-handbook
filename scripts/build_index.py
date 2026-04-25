"""Generate the homepage (index.html) with roadmap, stats, and chapter directory."""
import sys
sys.path.insert(0, "/home/claude/interview-prep-guide/scripts")

from html_common import (
    head_html, header_html, sidebar_html, footer_html,
    load_questions, esc
)
from site_data import PARTS, LEVEL_ORDER, LEVEL_TIME_ESTIMATE, file_for, LEVEL_DESCRIPTIONS

OUT = "/home/claude/interview-prep-guide/index.html"


def build():
    qdata = load_questions()
    by_topic = qdata["data"]

    # Totals
    total_questions = sum(
        sum(len(qs) for qs in levels.values())
        for levels in by_topic.values()
    )
    total_topics = len(by_topic)
    total_levels = len(LEVEL_ORDER)
    total_chapters = sum(len(levels) for levels in by_topic.values())

    # Build part directory sections
    directory_blocks = []
    for part in PARTS:
        topic_blocks = []
        for topic in part["topics"]:
            topic_levels = by_topic.get(topic, {})
            if not topic_levels:
                continue
            cards = []
            for level in LEVEL_ORDER:
                if level not in topic_levels:
                    continue
                fname = file_for(topic, level)
                count = len(topic_levels[level])
                desc = LEVEL_DESCRIPTIONS.get(level, "")
                cards.append(f"""
                <a class="card" href="chapters/{esc(fname)}">
                  <div class="card__eyebrow">{esc(topic)} · {esc(level)}</div>
                  <div class="card__title">{esc(topic)} — {esc(level)}</div>
                  <div class="card__desc">{esc(desc)}</div>
                  <div class="card__meta"><span>{count} questions</span><span>{esc(LEVEL_TIME_ESTIMATE.get(level, ""))}</span></div>
                </a>""")
            topic_blocks.append(f"""
            <div style="margin-bottom: 2.5rem;">
              <h3 style="font-size: 1.3rem; margin-bottom: 1rem; color: var(--text);">{esc(topic)}</h3>
              <div class="card-grid">{''.join(cards)}</div>
            </div>""")
        directory_blocks.append(f"""
        <section class="part-directory" id="part-{part['id']}">
          <div class="part-directory__header">
            <div class="part-directory__eyebrow">{esc(part['label'])}</div>
            <h2 class="part-directory__title">{esc(part['title'])}</h2>
            <p class="part-directory__desc">{esc(part['desc'])}</p>
          </div>
          {''.join(topic_blocks)}
        </section>""")

    # Roadmap blocks (short summary cards for each part)
    roadmap_cards = []
    for part in PARTS:
        topic_count = sum(1 for t in part["topics"] if t in by_topic)
        chapter_count = sum(len(by_topic.get(t, {})) for t in part["topics"])
        roadmap_cards.append(f"""
        <a class="card" href="#part-{part['id']}">
          <div class="card__eyebrow">{esc(part['label'])}</div>
          <div class="card__title">{esc(part['title'])}</div>
          <div class="card__desc">{esc(part['desc'])}</div>
          <div class="card__meta"><span>{topic_count} topic{'s' if topic_count != 1 else ''}</span><span>{chapter_count} chapters</span></div>
        </a>""")

    # Assemble
    html = f"""{head_html(
        "Interview Prep Mastery — Structured Web Development Interview Guide",
        "A structured, beginner-friendly interview preparation guide covering JavaScript, Python, HTML, CSS, React, Node.js, databases, system design, and DevOps with thousands of detailed questions and answers."
    )}
{header_html()}
<div class="layout">
{sidebar_html(current_file="__home__")}
<main class="main" id="main">

  <section class="hero">
    <div class="hero__eyebrow">A structured roadmap for interview-ready engineers</div>
    <h1 class="hero__title">Interview Prep Mastery</h1>
    <p class="hero__lede">
      Learn web development from fundamentals to advanced system design through
      a curated library of {total_questions:,}+ interview questions and answers. Every topic includes
      beginner-friendly explanations, working code examples, architectural diagrams,
      and real-world trade-off discussions.
    </p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="chapters/{file_for('JavaScript', 'Basic')}">Start with JavaScript Basics →</a>
      <a class="btn btn--secondary" href="#chapters">Browse the full curriculum</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="stat__value">{total_questions:,}</div><div class="stat__label">Detailed Q&amp;A</div></div>
      <div class="stat"><div class="stat__value">{total_topics}</div><div class="stat__label">Topics covered</div></div>
      <div class="stat"><div class="stat__value">{total_chapters}</div><div class="stat__label">Chapters</div></div>
      <div class="stat"><div class="stat__value">Beginner</div><div class="stat__label">To advanced</div></div>
    </div>
  </section>

  <section class="section" id="who">
    <div class="section__eyebrow">Who this is for</div>
    <h2 class="section__title">Designed for engineers preparing for real interviews</h2>
    <p class="section__lede">
      Whether you are looking for your first developer role, transitioning stacks, or preparing
      for senior-level system design rounds — the material progresses from first principles
      all the way up to architect-grade reasoning.
    </p>
    <div class="card-grid">
      <div class="card"><div class="card__title">Junior developers</div><div class="card__desc">Lock in the fundamentals of JavaScript, HTML, CSS, and databases before your first technical interview.</div></div>
      <div class="card"><div class="card__title">MERN stack candidates</div><div class="card__desc">MongoDB, Express, React, and Node — plus the system design knowledge needed to reason about them together.</div></div>
      <div class="card"><div class="card__title">Python full-stack engineers</div><div class="card__desc">Deep Python topics alongside web fundamentals — everything from list comprehensions to concurrency patterns.</div></div>
      <div class="card"><div class="card__title">Senior engineers</div><div class="card__desc">Advanced scenario-based questions, DevOps pipelines, and Infrastructure design for architect-level interviews.</div></div>
    </div>
  </section>

  <section class="section" id="roadmap">
    <div class="section__eyebrow">Learning journey</div>
    <h2 class="section__title">A step-by-step path from fundamentals to architect-grade thinking</h2>
    <p class="section__lede">
      The curriculum is organized into six parts. Start at Part 1 if you are new, or jump directly
      to the topic you need. Every chapter stands on its own, but the sequence is designed to build
      intuition progressively.
    </p>
    <div class="card-grid">
      {''.join(roadmap_cards)}
    </div>
  </section>

  <section class="section" id="how">
    <div class="section__eyebrow">How to study</div>
    <h2 class="section__title">How to get the most out of this guide</h2>
    <p class="section__lede">
      Passive reading is the slow path. Here is the study loop that interview-winning candidates follow.
    </p>
    <div class="card-grid">
      <div class="card"><div class="card__eyebrow">Step 1</div><div class="card__title">Attempt first, read second</div><div class="card__desc">Before expanding the answer, spend 60 seconds thinking through the question yourself. Active recall cements learning.</div></div>
      <div class="card"><div class="card__eyebrow">Step 2</div><div class="card__title">Trace the examples</div><div class="card__desc">For every code snippet, mentally execute it line by line. Predict the output before you read the explanation.</div></div>
      <div class="card"><div class="card__eyebrow">Step 3</div><div class="card__title">Explain it aloud</div><div class="card__desc">If you cannot explain a concept in your own words without looking, you do not fully understand it yet.</div></div>
      <div class="card"><div class="card__eyebrow">Step 4</div><div class="card__title">Revisit tricky topics</div><div class="card__desc">Spaced repetition works. Bookmark tough questions and return after a day, a week, and a month.</div></div>
    </div>
  </section>

  <section id="chapters" class="section" style="border-bottom: none;">
    <div class="section__eyebrow">Chapter directory</div>
    <h2 class="section__title">Browse every chapter</h2>
    <p class="section__lede">
      The full curriculum in one page. Click any chapter to jump straight into the questions.
    </p>
  </section>
  {''.join(directory_blocks)}

</main>
</div>
{footer_html()}
"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote homepage: {OUT}")


if __name__ == "__main__":
    build()
