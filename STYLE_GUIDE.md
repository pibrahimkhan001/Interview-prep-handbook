# STYLE_GUIDE.md

> Conventions for writing detailed answers. Keeps tone consistent across topics and sessions.

---

## 🎙️ Voice

- **Beginner-friendly but not dumbed down.** Someone learning the language for the first time should understand; someone with experience shouldn't feel patronized.
- **Concrete over abstract.** Show the code, then explain what it does and why it matters.
- **No filler.** Every sentence should carry weight. Cut "it is important to note that", "basically", "essentially", "in other words".
- **Second person sparingly.** Prefer neutral framing ("The `useEffect` hook runs after render") over "you" ("You use `useEffect` to...").
- **Direct answers first.** Don't bury the lede under preamble. State the thing, then explain.
- **Name real libraries and tools.** "Use Zod for validation" beats "use a validation library". Readers remember concrete options.

---

## 📏 Depth Targets per Level

Word counts below are _per answer_, not per question. Code blocks don't count toward word count.

| Level | Target length | Structure |
| --- | --- | --- |
| **Basic** | 150–250 words | Definition → key points → code example → gotchas/callout |
| **Tricky** | 80–150 words | Focused on the gotcha; minimal preamble |
| **Coding** | 60–120 words | Code first; brief explanation; complexity + edge cases |
| **Advanced** | 100–180 words | Senior-level depth; compare alternatives; name trade-offs |
| **Advanced Coding** | 80–150 words | Code + algorithm explanation + complexity + when it matters |
| **Scenario** | 150–250 words | Situation → approach → code sample → trade-offs |
| **Advanced Scenario** | 180–300 words | Architect-level; multi-layered; reference real libraries and patterns |

**When to go shorter:** if the topic is genuinely small (e.g., "What are comments?"), don't pad. 50 words is fine.

**When to go longer:** if the concept has multiple orthogonal facets that all matter (e.g., "Explain the event loop"), split into subsections or a table instead of bloating prose.

---

## 🏗️ HTML Conventions in Answer Strings

All answers are HTML snippets stored as Python raw strings (`r'''...'''`). They render inside a `<div class="qa__answer">` container.

### Standard building blocks

```html
<p>Explanation paragraph with <code>inline code</code>.</p>

<pre><code>// Multi-line code example
const x = 42;</code></pre>

<ul>
  <li><strong>Point one</strong> — short elaboration.</li>
  <li><strong>Point two</strong> — short elaboration.</li>
</ul>

<table>
  <thead><tr><th>Column</th><th>Other</th></tr></thead>
  <tbody>
    <tr><td>A</td><td>B</td></tr>
  </tbody>
</table>
```

### Callouts

Three variants — use sparingly (max one per answer).

```html
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>Tip content here — concise, one or two sentences.</div>
</div>

<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div>Warning about common pitfalls or anti-patterns.</div>
</div>

<div class="callout callout-info">
  <div class="callout-icon">?</div>
  <div>Additional context or a "go deeper" pointer.</div>
</div>
```

### Entity escaping inside `<pre><code>`

**Critical:** inside `<pre><code>` blocks, these characters must be escaped:

| Raw | Use |
| --- | --- |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |

Forgetting this breaks the page silently (tags get parsed as HTML). When in doubt, check that `<div>`, `=>`, `&&`, and `||` render correctly.

### What NOT to use

- `<br>` tags — use paragraphs.
- Inline `style=` attributes — styling lives in `assets/styles.css`.
- `<h1>`, `<h2>` — the chapter shell provides headings; answers start at `<p>` or `<ul>`.
- Emojis in content — the site design is clean and sober.
- Horizontal rules (`<hr>`) — use a new paragraph instead.

---

## 💻 Code Example Standards

- **Runnable if possible.** Snippets shouldn't need 10 lines of setup to understand.
- **Comments clarify intent**, not mechanics. `// Deduplicate users by email` is useful; `// Loop over array` isn't.
- **Modern syntax.** ES2020+ for JavaScript, Python 3.10+ idioms (match statements, structural typing, type hints where relevant).
- **Realistic names.** `user`, `order`, `config` over `foo`, `bar`, `baz`.
- **Keep under ~20 lines.** Longer snippets belong in multiple blocks with prose between them.
- **Output hints inline.** `// "Ana"` or `# → 42` after expressions to show results.

---

## 🧩 Topic-Specific Guidance

### JavaScript (reference — already complete)
Established the pattern. Uses modern ES syntax, shows both imperative and declarative approaches, names real libraries (React, Zod, TanStack Query, etc.).

### Python
- Use type hints where they clarify. Don't force them on trivial examples.
- Prefer f-strings over `%` or `.format()` in modern examples.
- Show Pythonic idioms (comprehensions, `enumerate`, `zip`, `with` statements, unpacking).
- Name real libraries: `requests`, `pydantic`, `pytest`, `black`, `ruff`, `fastapi`, `sqlalchemy`.
- PEP 8 naming: `snake_case` for functions/variables, `PascalCase` for classes.

### HTML
- Semantic elements front and center (`<article>`, `<nav>`, `<main>`, `<section>`).
- Accessibility is integral, not a footnote — mention ARIA where relevant.
- Mobile-first thinking; mention `viewport` meta and responsive patterns.

### CSS
- Modern layout (flexbox, grid, container queries) over floats.
- Custom properties for theming examples.
- Logical properties (`margin-inline-start`) for i18n awareness.
- Name actual values (`clamp(1rem, 2vw, 1.5rem)`), not hand-wavy descriptions.

### Node.js / ExpressJS
- Modern Node (v20+); `import` not `require` where possible.
- Async/await over callbacks.
- Streams for large data; error-first handling patterns.

### React
- Function components + hooks only (no class components unless specifically asked).
- Name libraries readers will actually use (React Router, React Query, Zustand, dnd-kit).
- Show the minimum viable example, then note production-grade alternatives.

### API
- Reference the REST maturity model where relevant; call out GraphQL / gRPC trade-offs.
- OpenAPI and JSON Schema mentioned for contracts.
- Auth patterns: JWT, OAuth2, session cookies — always name the security implications.

### Databases (MySQL, MongoDB)
- Include actual `EXPLAIN` output or index notes for query questions.
- Show the Mongo pipeline stage names (`$match`, `$group`, `$lookup`).
- Mention migration tooling (Liquibase, Flyway, mongoose migrations).

### System Design / Infrastructure / CI/CD
- Start from the problem; propose a design; list scaling & failure modes.
- Name actual services (Redis, Kafka, CloudFront, k8s, Argo CD) — readers build mental maps from names.
- Ballpark capacity numbers where useful ("100k RPS", "5 ms p99").

---

## ✅ Definition of "Done" for a Level

A level's module is complete when:

1. `ANSWERS` dict has exactly 100 keys (or the question count from `data/questions.json` for that topic/level).
2. `sorted(ANSWERS.keys()) == list(range(1, N + 1))` — no gaps, no off-by-one.
3. Every answer passes a **self-check**: does it answer the actual question? (Mis-aligned keys have bitten us before.)
4. Every answer has at least one `<pre><code>` block unless the question is genuinely theoretical.
5. No unescaped `<` or `&` inside code blocks.
6. The chapter builds without Python errors.
7. Rendered HTML size is in the 100–200 KB range. Below 80 KB means answers are probably too thin.

---

## 🔁 Revision Rules

- **Never rewrite for style alone** once a level is "done" — leaves a trail of churn in diffs and wastes session budget.
- **Do rewrite** if an answer is factually wrong or misaligned with its question.
- If the style of older answers feels off when writing newer ones, adjust the newer ones — don't retrofit the old.
