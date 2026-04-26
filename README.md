# Interview Prep Handbook

A standalone, offline-capable learning site covering **4,904 interview questions** across 13 topics and 7 difficulty levels.

🌐 **Live site:** https://pibrahimkhan001.github.io/interview-prep-handbook/

## How to use it

**Online:** just visit the live site link above — works on phone, tablet, or desktop.

**Offline / local:**
1. Clone or download this repo.
2. Open `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
3. Browse chapters from the homepage or the left sidebar.

No build step, no server, no internet required — it's a fully static site.

## Progress

**2,803 / 4,904 detailed answers** (~57%) across **28 of 49 chapters**.

| Part | Topic | Status |
| --- | --- | --- |
| 1 | **JavaScript** (7 levels, 700 Q) | ✅ Complete |
| 1 | **Python** (4 levels, 400 Q) | ✅ Complete |
| 2 | **HTML** (3 levels, 300 Q) | ✅ Complete |
| 2 | **CSS** (3 levels, 303 Q) | ✅ Complete |
| 3 | **Node.js** (4 levels, 400 Q) | ✅ Complete |
| 3 | **ExpressJS** (3 levels, 300 Q) | ✅ Complete |
| 3 | **API** (4 levels, 400 Q) | ✅ Complete |
| 4 | ReactJS (4 levels, 401 Q) | ⏳ In progress |
| 5 | MySQL, MongoDB (8 levels, 800 Q) | 📋 Stubs |
| 6 | System Design, Infrastructure, CI/CD (9 levels, 900 Q) | 📋 Stubs |

Stub chapters show every question with a "detailed answer coming soon" message, but the question list itself is complete and usable as a study checklist.

### Answer depth

Every detailed answer includes:
- A direct, beginner-friendly explanation calibrated to the difficulty level
- Runnable code examples in `<pre><code>` blocks
- Callouts for gotchas, tips, and warnings
- Comparison tables where relevant
- References to 2026-current libraries and best practices

Approximate read time for completed chapters: ~40-45 hours.

## Structure

```
interview-prep-handbook/
├── index.html                  ← start here
├── README.md                   ← this file
├── DEPLOYMENT.md               ← how to push to GitHub & enable Pages
├── assets/
│   ├── styles.css              ← book-style theme with dark mode
│   └── script.js               ← navigation, theme toggle
├── chapters/                   ← 49 chapter HTML pages
│   ├── javascript-basic.html
│   ├── ...
│   └── cicd-pipeline-scenario.html
├── content/                    ← Python source modules with detailed answers
│   ├── javascript_*.py         (7 files, 700 answers)
│   ├── python_*.py             (4 files, 400 answers)
│   ├── html_*.py               (3 files, 300 answers)
│   ├── css_*.py                (3 files, 303 answers)
│   ├── nodejs_*.py             (4 files, 400 answers)
│   ├── expressjs_*.py          (3 files, 300 answers)
│   └── api_*.py                (4 files, 400 answers)
├── data/
│   └── questions.json          ← all 4,904 parsed questions
├── docs/                       ← project documentation
│   ├── PROJECT_STATE.md
│   ├── ROADMAP.md
│   ├── CHANGELOG.md
│   ├── ARCHITECTURE.md
│   └── CONTENT_STYLE_GUIDE.md
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
