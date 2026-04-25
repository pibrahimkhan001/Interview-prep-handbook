# Content Style Guide

Canonical patterns for writing answers across topics and levels. Follow these to keep voice and structure consistent.

## Golden rules

1. **Beginner-friendly but not dumbed down.** Assume the reader is new to the topic but technically literate.
2. **Show, don't just tell.** Every answer should have at least one code example or concrete illustration when applicable.
3. **HTML escape rigorously.** Inside `<pre><code>` blocks, `<` must become `&lt;`, `>` must become `&gt;`, `&` must become `&amp;`.
4. **Use raw Python strings.** All answers use `ANSWERS[n] = r'''...'''` — the `r` prefix prevents escape-sequence interpretation.
5. **One primary point per answer.** Don't lecture. Hit the concept, give the example, note the gotcha, move on.

## Depth guidelines per level

### Basic (100-250 words)
- Definition first.
- Key characteristics as short bullet list OR table.
- One clear code example.
- Optional: callout for a common gotcha.

### Tricky (80-120 words)
- The gotcha IS the answer.
- Minimal preamble — just explain the confusing behavior.
- Code that demonstrates the surprise.
- One-line takeaway.

### Coding (code-first, ~100 words of prose)
- Working solution as the first visible content.
- 2-3 sentences explaining the approach.
- Complexity notes (time/space) where relevant.
- Edge cases mentioned briefly.

### Advanced (100-180 words)
- Senior-level conceptual depth.
- Mechanism/internals when relevant (hidden classes, event loop, etc).
- Trade-offs in tabular form when comparing.
- Industry best practices.

### Advanced Coding (code-heavy, ~80 words prose)
- Non-trivial algorithm or architecture.
- Explain the key insight.
- Complexity + alternative approaches.

### Scenario Based (structured, 150-250 words)
- Situation → approach → trade-offs.
- Real code examples with realistic complexity.
- Mention production libraries where relevant.

### Advanced Scenario (architect-level, 200-300 words)
- Multi-layered approach across stack.
- Security, scalability, observability concerns.
- Named real-world libraries/services (Redis, Kafka, Sentry, etc.).
- Trade-offs spelled out, not glossed over.

## HTML structure patterns

### Callouts

```html
<div class="callout callout-tip"><div class="callout-icon">💡</div><div>
<strong>Tip:</strong> Explanation here.
</div></div>

<div class="callout callout-warning"><div class="callout-icon">!</div><div>
<strong>Warning:</strong> What to watch for.
</div></div>

<div class="callout callout-info"><div class="callout-icon">i</div><div>
<strong>Note:</strong> Supplementary info.
</div></div>
```

Use callouts sparingly — at most one per answer, for genuinely important warnings or tips.

### Code blocks

```html
<pre><code>def example(x):
    if x &lt; 0:             # escape: <
        return None
    return x * 2

result = example(5)       # 10</code></pre>
```

Inline code uses `<code>foo</code>`.

### Comparison tables

```html
<table>
  <thead><tr><th></th><th>Option A</th><th>Option B</th></tr></thead>
  <tbody>
    <tr><td>Speed</td><td>Fast</td><td>Slow</td></tr>
    <tr><td>Memory</td><td>Low</td><td>High</td></tr>
  </tbody>
</table>
```

Used whenever the answer compares 2+ things. Usually clearer than prose.

### Lists

- Unordered lists for characteristics, defenses, options, considerations.
- Ordered lists for steps, sequences, prioritized recommendations.
- Bold the key term at the start of each bullet: `<li><strong>Term</strong> — explanation.</li>`

## Typography

- Use smart quotes in prose: `&ldquo;` and `&rdquo;` (not `"`).
- Em dashes as `&mdash;` or just `—` (literal em dash works too).
- Code identifiers always in `<code>`, not quotes: write <code>useState</code>, not "useState".
- Numbers with units: `15 min` not `15min`; `5 MB` not `5MB`.

## Voice

- **Direct.** "Use `structuredClone` for deep copies." Not "You might consider using..."
- **Opinionated when there's a right answer.** "Don't store JWTs in localStorage." Not "There are differing views."
- **Name real tools.** Say "React Query handles this" not "a caching library handles this."
- **Admit complexity.** "Rolling your own is rarely worth it" — honesty builds trust.
- **Avoid filler phrases.** No "It's important to note that...", no "As we can see...", no "Basically...".

## References across levels

When the same concept appears at multiple levels, cross-reference with the question number:

```
Covered in depth in Basic Q12. Adds to what's there:
- (new advanced angle)
```

This keeps answers concise and builds a network of related ideas.

## When referring to the current year

Today is 2026. Write "2026" not "2024". If referencing versioned software (Node 22, React 19), use actual current versions where possible.

## Things to avoid

- ❌ Reproducing substantial content from specific online sources (even if paraphrased, stay high-level).
- ❌ Song lyrics, poetry, copyrighted material of any kind.
- ❌ Personal opinions on politics or contested social issues.
- ❌ `JSON.parse(JSON.stringify(x))` as a recommendation for deep cloning (it fails on cycles, Dates, functions, undefined).
- ❌ `innerHTML` with user data without sanitization.
- ❌ `eval`, `new Function(userInput)`, `document.write`.
- ❌ Recommending localStorage for sensitive tokens/secrets.

## Update protocol

If a new pattern emerges that should be standardized, add it here before applying it widely. Update the "Last updated" marker in `PROJECT_STATE.md` on changes to this file.

---

**Last updated:** 2026-04-17
