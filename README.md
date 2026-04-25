# Interview Prep Mastery

A standalone, offline-capable learning site covering **4,898 interview questions** across 13 topics and 7 difficulty levels.

## How to use it

1. **Extract** the zip file anywhere on your computer.
2. **Open `index.html`** in any modern browser (Chrome, Firefox, Edge, Safari).
3. Browse chapters from the homepage or the left sidebar.

No build step, no server, no internet required — it's a fully static site.

## What's inside

### Content status (as of this delivery)

| Part | Topic | Detailed answers |
| --- | --- | --- |
| 1 | **JavaScript** (all 7 levels, 700 questions) | ✅ Complete |
| 1 | Python | 🚧 Stubs with question list |
| 2 | HTML, CSS | 🚧 Stubs with question list |
| 3 | Node.js, ExpressJS, API | 🚧 Stubs with question list |
| 4 | ReactJS | 🚧 Stubs with question list |
| 5 | MySQL, MongoDB | 🚧 Stubs with question list |
| 6 | System Design MERN, Infrastructure MERN, CI/CD Pipeline | 🚧 Stubs with question list |

Stub chapters show every question with a "detailed answer coming soon" message, but the question list itself is complete and usable as a study checklist.

### JavaScript chapter depth

Every one of the 700 JavaScript questions includes:
- A direct, beginner-friendly explanation
- Runnable code examples in `<pre><code>` blocks
- Callouts for gotchas, tips, and warnings
- Comparison tables where relevant
- References to production-grade libraries where applicable

Approximate read time: ~10-11 hours to go through every JavaScript chapter.

## Structure

```
interview-prep-guide/
├── index.html                  ← start here
├── assets/
│   ├── styles.css              ← book-style theme with dark mode
│   └── script.js               ← navigation, theme toggle
├── chapters/                   ← 49 chapter HTML pages
│   ├── javascript-basic.html
│   ├── javascript-tricky.html
│   ├── ...
│   └── cicd-pipeline-scenario.html
├── content/                    ← Python modules with detailed answers (source)
│   ├── javascript_basic.py
│   └── ... (7 JavaScript modules)
├── data/
│   └── questions.json          ← all 4,898 parsed questions
└── scripts/                    ← build pipeline
    ├── build_chapters.py
    ├── build_index.py
    └── ...
```

## Rebuilding (optional)

If you want to regenerate the HTML from the source:

```bash
cd interview-prep-guide
python3 scripts/build_chapters.py
python3 scripts/build_index.py
```

Requires Python 3.8+ only — no dependencies.

## Adding more content

To fill in a stub chapter for another topic:

1. Create a file in `content/` named `<topic>_<level>.py` (e.g., `python_basic.py`, `reactjs_advanced.py`).
2. Export a dict `ANSWERS` keyed by 1-based question number → HTML string:

    ```python
    ANSWERS = {}
    ANSWERS[1] = r'''<p>Your answer here with <code>code</code> and examples.</p>'''
    ANSWERS[2] = r'''<p>Next answer...</p>'''
    ```

3. Run `python3 scripts/build_chapters.py` to regenerate.

## Credits

- Fonts: [Inter](https://rsms.me/inter/) (UI) & [JetBrains Mono](https://www.jetbrains.com/mono/) (code) via Google Fonts
- Design inspired by book-style documentation sites
- Built for personal interview preparation
