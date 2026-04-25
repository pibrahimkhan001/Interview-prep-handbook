# Architecture

How the site is built. Read this before changing the build system.

## Overview

Static site generator. Python reads question data from JSON, combines with detailed-answer Python modules, renders 49 HTML chapter pages + 1 homepage. No server, no runtime dependencies for the output.

## Data flow

```
Excel source              ┐
(Ibrahim_Interview_        │  extract_questions.py
 Prep.xlsx)                ▼
                    data/questions.json        ← 4,904 questions, flat JSON
                           │
                           │  build_chapters.py
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  site_data.py       content/*.py       html_common.py
  (topic/level       (ANSWERS dict      (template
   metadata,          per chapter)       helpers)
   part grouping)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    chapters/*.html           ← 49 rendered pages
                    
        build_index.py ──→ index.html         ← homepage
```

## Key files

### `scripts/site_data.py`
Metadata source. Defines:
- `TOPICS` — ordered topic list with display names and part assignments
- `LEVELS` — ordered level list with estimated reading times and slug mappings
- `PARTS` — five parts grouping topics (Core Languages, Web Fundamentals, etc.)
- `slug_for(topic, level)` → e.g., `"JavaScript" + "Advanced Scenario Based" → "javascript-advanced-scenario"`

### `scripts/html_common.py`
Template helpers:
- `render_page_shell(...)` — full HTML wrapper with header, sidebar, footer
- `render_sidebar(active_slug)` — chapter nav grouped by part
- `render_qa_block(index, question, answer_html, code)` — single Q&A card
- Handles the breadcrumb, theme toggle button, font links

### `scripts/build_chapters.py`
Main build. For each (topic, level):
1. Compute slug: `slug_for(topic, level)` with `-` → `_` for module name
2. Try to import `content/<slug>.py`. If absent, render stub chapter with question list + "coming soon" message. If present, pull `ANSWERS` dict.
3. Load all questions from `data/questions.json` for that topic/level.
4. For each question `i` (1-indexed): if `i in ANSWERS`, render detailed Q&A with `ANSWERS[i]` HTML; else render question only.
5. Write `chapters/<slug>.html`.

### `scripts/build_index.py`
Renders the homepage: intro, roadmap visual, chapter grid grouped by part.

## Content module contract

Every detailed-content module exports one top-level name:

```python
# content/<slug>.py
"""<Topic> · <Level> · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}
ANSWERS[1]   = r'''<p>...</p><pre><code>...</code></pre>'''
ANSWERS[2]   = r'''<p>...</p>'''
# ...
ANSWERS[100] = r'''<p>...</p>'''
```

- **Keys** are 1-based question numbers (matching the order in `questions.json`).
- **Values** are raw HTML strings (Python raw strings with `r'''...'''`).
- **Partial modules are OK** — keys without entries render as "coming soon" within an otherwise-detailed chapter.

## Slug rules (critical — easy to get wrong)

| Topic string | Slug |
| --- | --- |
| `JavaScript` | `javascript` |
| `Node.Js` | `nodejs` |
| `ExpressJS` | `expressjs` |
| `ReactJS` | `reactjs` |
| `MYSQL` | `mysql` |
| `MongoDB` | `mongodb` |
| `System Design MERN Stack` | `system-design-mern` |
| `Infrastructure MERN Stack` | `infrastructure-mern` |
| `CI/CD Pipeline` | `cicd-pipeline` |

| Level string | Slug |
| --- | --- |
| `Basic` | `basic` |
| `Tricky` | `tricky` |
| `Coding` | `coding` |
| `Advanced` | `advanced` |
| `Advanced Coding` | `advanced-coding` |
| `Scenario Based` | `scenario` |
| `Advanced Scenario Based` | `advanced-scenario` |

**Module filename = `<topic-slug>_<level-slug>.py` with all hyphens converted to underscores.**
Example: `javascript-advanced-scenario` → `javascript_advanced_scenario.py`.

## HTML output conventions

- Each Q&A is rendered inside `<article class="qa">` with `class="qa__question"` and `class="qa__answer"` children.
- Questions numbered with `<span class="qa__num">NN.</span>` prefix.
- Code blocks: `<pre><code>...</code></pre>` (no language classes — site doesn't have syntax highlighting yet).
- Callouts: `<div class="callout callout-{tip|warning|info}">` with `<div class="callout-icon">` + content div.
- Internal links between chapters: relative paths `../chapters/slug.html`.
- Asset links: `../assets/styles.css` and `../assets/script.js`.

## Theme system

- CSS variables scoped on `:root[data-theme="dark"]` vs `:root` (light default).
- `script.js` persists choice to `localStorage.theme`; reads `prefers-color-scheme` as initial default.
- `<script>` in `<head>` sets `data-theme` before CSS renders to prevent FOUC.

## Rebuild workflow

```bash
cd /home/claude/interview-prep-guide
python3 scripts/build_chapters.py    # regenerates all 49 chapter HTMLs
python3 scripts/build_index.py       # regenerates index.html
```

Both are idempotent and take < 2 seconds. Safe to run repeatedly.

## Adding a new topic/level chapter

1. Check `data/questions.json` has questions for that `(topic, level)` pair. If source data is missing a combination, the chapter won't be generated regardless of content module presence.
2. Create `content/<topic-slug>_<level-slug>.py` (see slug rules above).
3. Populate `ANSWERS` dict with 1-indexed keys.
4. Run `python3 scripts/build_chapters.py`.
5. Verify: `ls -lh chapters/<slug>.html` should show a substantially larger file than stub chapters (~120 KB+ typical).

## Packaging for delivery

```bash
cd /home/claude
find interview-prep-guide -name __pycache__ -type d -exec rm -rf {} +
zip -rq interview-prep-guide.zip interview-prep-guide/ -x "*.pyc" "*/__pycache__/*"
cp interview-prep-guide.zip /mnt/user-data/outputs/
```

Then call `present_files` with the output path.

---

**Last updated:** 2026-04-17
