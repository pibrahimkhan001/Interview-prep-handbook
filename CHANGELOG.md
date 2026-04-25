# CHANGELOG.md

> Session-by-session log of concrete additions, changes, and fixes.
> Most recent first. Append a new entry at the top of "Sessions" for each session.

---

## Sessions

### 2026-04-17 — Session 5: Context scaffolding + Python kickoff

**Infrastructure**
- Created `PROJECT_STATE.md` — single source of truth for completion status.
- Created `STYLE_GUIDE.md` — voice, depth targets per level, HTML conventions, topic-specific guidance, definition of "done".
- Created `CHANGELOG.md` — this file.
- Created `ARCHITECTURE.md` — file layout, build pipeline, content module format, how to extend.

**Content**
- Started `content/python_basic.py`:
  - Added answers Q1–30 covering: language overview, installation, data types, strings, arithmetic, collections (lists, tuples, dicts, sets), functions, return, exceptions, loops, range, modules, imports, input, `==` vs `is`, comments, list comprehensions, sorting, lambdas, classes, `self`, instances, class/instance variables, inheritance.

**Build & delivery**
- Rebuilt `chapters/python-basic.html` (now populated, not a stub).
- Packaged `interview-prep-guide.zip` (final deliverable).

---

### Prior sessions (rolled up)

#### Sessions 1–4 — JavaScript complete + site scaffold

**Site infrastructure**
- Parsed Excel source (`/mnt/project/Ibrahim_Interview_Prep.xlsx`) → `data/questions.json` (4,898 questions across 13 topics × up to 7 levels).
- Built static site scaffold: `assets/styles.css` (book theme, light/dark mode), `assets/script.js` (theme toggle, mobile sidebar), `index.html` (homepage with roadmap + chapter grid).
- Built generator pipeline: `scripts/site_data.py` (Parts → Topics → Levels taxonomy), `scripts/html_common.py` (shared HTML fragments), `scripts/build_chapters.py`, `scripts/build_index.py`.
- 49 chapter HTML pages generated — 7 populated, 42 stubs.

**JavaScript content — all 700 answers**
- `javascript_basic.py` — 100 Q
- `javascript_tricky.py` — 100 Q
- `javascript_coding.py` — 100 Q
- `javascript_advanced.py` — 100 Q
- `javascript_advanced_coding.py` — 100 Q
- `javascript_scenario.py` — 100 Q (realigned Q70–76 in session 4 after discovering off-by-one key shift)
- `javascript_advanced_scenario.py` — 100 Q

**Fixes**
- Fixed `build_chapters.py` to handle dict-of-HTML content format (was expecting list-of-dicts).
- Cleaned up stale draft files (`js_basic_01_10.py` through `js_basic_41_50.py`) after merging into canonical module.
- Realigned scenario-based Q70–76 keys with their questions (renumbered `[70]→[72]`, `[72]→[73]`, etc.; wrote fresh answers for Q70 and Q71).

**Deliverables**
- Packaged `interview-prep-guide.zip` (928 KB, 72 files) with README.md.
