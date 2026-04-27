# Roadmap

Phase plan for filling in the remaining 21 stub chapters (~2,100 detailed answers to write).

## Completed phases

- **Phase 0: Scaffold** — Site structure, theme, sidebar, homepage, build system. ✅
- **Phase 1: JavaScript** — All 7 levels, 700 detailed answers. ✅
- **Phase 2: Python** — All 4 levels (Basic, Coding, Advanced, Scenario Based), 400 detailed answers. ✅
- **Phase 3: Backend Core** — Node.js (4 levels, 400), ExpressJS (3 levels, 300), API (4 levels, 400) = 1,100 detailed answers. ✅

## Current phase

### Phase 4: Frontend (HTML / CSS / React)

Frontend chapters round out the browser-facing half of full-stack interviews. HTML and CSS complete; React next.

- [x] HTML Basic (100 Q, completed 2026-04-20)
- [x] HTML Coding (100 Q, completed 2026-04-25)
- [x] HTML Advanced (100 Q, completed 2026-04-26)
- [x] CSS Basic (102 Q, completed 2026-04-26)
- [x] CSS Coding (100 Q, completed 2026-04-26)
- [x] CSS Advanced (101 Q, completed 2026-04-26)
- [x] **React JS Basic (101 Q)** &mdash; 2026-04-26
- [x] **React JS Coding (100 Q)** &mdash; 2026-04-27
- [x] **React JS Advanced (100 Q)** &mdash; 2026-04-27
- [x] **React JS Scenario Based (100 Q)** &mdash; 2026-04-27 &mdash; **Phase 4 complete (1,004/1,004)**

**Target:** 401 more answers to finish frontend.

## Future phases (in priority order)

### Phase 5: Databases (Part 5)
MySQL and MongoDB parallel each other nicely — many questions are about analogous concepts in different DB families.

- MYSQL Basic, Coding, Advanced, Scenario Based (400 Q) &mdash; **MySQL Basic ← next**
- MongoDB Basic, Coding, Advanced, Scenario Based (400 Q)

**Total:** 800 answers.

### Phase 6: System Design & DevOps (Part 6)
Architectural and infrastructure topics — longest, most essay-like answers.

- System Design MERN Basic, Advanced, Scenario Based (300 Q)
- Infrastructure MERN Basic, Advanced (200 Q)
- CI/CD Pipeline Basic, Coding, Advanced, Scenario Based (400 Q)

**Total:** 900 answers.

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

**Last updated:** 2026-04-18
