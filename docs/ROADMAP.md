# Roadmap

Phase plan for filling in the remaining 21 stub chapters (~2,100 detailed answers to write).

## Completed phases

- **Phase 0: Scaffold** — Site structure, theme, sidebar, homepage, build system. ✅
- **Phase 1: JavaScript** — All 7 levels, 700 detailed answers. ✅
- **Phase 2: Python** — All 4 levels (Basic, Coding, Advanced, Scenario Based), 400 detailed answers. ✅
- **Phase 3: Backend Core** — Node.js (4 levels, 400), ExpressJS (3 levels, 300), API (4 levels, 400) = 1,100 detailed answers. ✅
- **Phase 4: Frontend** — HTML (3 levels, 300), CSS (3 levels, 303), ReactJS (4 levels, 401) = 1,004 detailed answers. ✅
- **Phase 5: Databases** — MySQL (4 levels, 400) + MongoDB (4 levels, 400) = 800 detailed answers. ✅
  - [x] **MySQL Basic (100 Q)** &mdash; 2026-04-27
  - [x] **MySQL Coding (100 Q)** &mdash; 2026-04-27
  - [x] **MySQL Advanced (100 Q)** &mdash; 2026-04-27
  - [x] **MySQL Scenario Based (100 Q)** &mdash; 2026-04-28
  - [x] **MongoDB Basic (100 Q)** &mdash; 2026-04-28
  - [x] **MongoDB Coding (100 Q)** &mdash; 2026-04-28
  - [x] **MongoDB Advanced (100 Q)** &mdash; 2026-04-28
  - [x] **MongoDB Scenario Based (100 Q)** &mdash; 2026-04-29 &mdash; **Phase 5 complete (800/800)**

## Current phase

### Phase 6: System Design & DevOps
Architectural and infrastructure topics — longest, most essay-like answers.

- [x] **System Design MERN Basic (100 Q)** &mdash; 2026-04-29
- [x] **System Design MERN Advanced (100 Q)** &mdash; 2026-04-29
- [x] **System Design MERN Scenario Based (100 Q)** &mdash; 2026-04-29 &mdash; **System Design MERN topic complete**
- [x] **Infrastructure MERN Basic (100 Q)** &mdash; 2026-05-02
- [x] **Infrastructure MERN Advanced (100 Q)** &mdash; 2026-05-02 &mdash; **Infrastructure MERN topic complete**
- [x] **CI/CD Pipeline Basic (100 Q)** &mdash; 2026-05-02
- [x] **CI/CD Pipeline Coding (100 Q)** &mdash; 2026-05-03
- [x] **CI/CD Pipeline Advanced (100 Q)** &mdash; 2026-05-03
- [x] **CI/CD Pipeline Scenario Based (100 Q)** &mdash; 2026-05-13 &mdash; **🎉 Phase 6 complete (900/900); project 100% complete (4,904/4,904)**

**Total:** 900 answers (final phase). Progress: 500/900 = 56%.

## Ordering rationale

1. **Python** is nearest completion and pairs with JS (same "Part 1").
2. **Backend (Phase 3)** shares mental model with JavaScript already written.
3. **Frontend (Phase 4)** before databases because most learners hit it sooner.
4. **Databases (Phase 5)** before system design because DBs are a dependency.
5. **System design (Phase 6)** last — draws on everything else.

## Scope per session

Realistic throughput per session (based on JS experience):
- **Basic/Tricky/Coding levels** — 25-50 answers per session.
- **Advanced/Scenario levels** — 15-25 answers per session.
- **Advanced Scenario** — 10-20 per session (longest).

For Python Basic specifically: **Q61-100 = 40 answers.** Single-session achievable.

## Session workflow

Every content session should:

1. Read `docs/PROJECT_STATE.md` to confirm what's done/pending.
2. Read `docs/CONTENT_STYLE_GUIDE.md` if unfamiliar with conventions.
3. Load the source questions: `data/questions.json` → `data['data'][topic][level]`.
4. Check existing `content/<slug>.py` for what's already written. Don't duplicate.
5. Write new `ANSWERS` entries.
6. Verify: `python3 -c "import sys; sys.path.insert(0,'content'); import <module>; print(sorted(<module>.ANSWERS.keys()))"`
7. Run build: `python3 scripts/build_chapters.py`.
8. Update `docs/PROJECT_STATE.md` — change row status, bump date.
9. Append to `docs/CHANGELOG.md` with session summary.
10. If packaging is requested, run the zip workflow from `ARCHITECTURE.md`.

---

**Last updated:** 2026-04-29
