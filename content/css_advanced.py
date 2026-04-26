"""Detailed answers for CSS Advanced questions."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p>These three values of the <code>display</code> property control how an element flows in the document and how it interacts with width, height, and surrounding content.</p>

<table>
  <tr><th></th><th><code>block</code></th><th><code>inline</code></th><th><code>inline-block</code></th></tr>
  <tr><td>Layout</td><td>Stacks vertically; full container width</td><td>Flows with text horizontally</td><td>Flows like inline; sized like block</td></tr>
  <tr><td><code>width</code> / <code>height</code></td><td>Respected</td><td>Ignored</td><td>Respected</td></tr>
  <tr><td>Vertical margin / padding</td><td>Pushes other elements</td><td>Visible but doesn&rsquo;t push siblings</td><td>Pushes other elements</td></tr>
  <tr><td>New line before/after</td><td>Yes</td><td>No</td><td>No</td></tr>
  <tr><td>Default for</td><td><code>&lt;div&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;h1&gt;</code></td><td><code>&lt;span&gt;</code>, <code>&lt;a&gt;</code>, <code>&lt;strong&gt;</code></td><td>(none by default)</td></tr>
</table>

<p><strong>Why each exists:</strong></p>
<ul>
  <li><strong>Block</strong> elements own their entire row &mdash; structural elements like sections, paragraphs, and headings.</li>
  <li><strong>Inline</strong> elements participate in the text flow without breaking lines &mdash; words, links, emphasis. They can&rsquo;t have explicit dimensions because that would break the line-box model.</li>
  <li><strong>Inline-block</strong> is the hybrid &mdash; participates in horizontal text flow (like inline) but accepts width/height (like block). Useful for navigation items, buttons, or anything that should sit beside other content but have specific dimensions.</li>
</ul>

<pre><code>nav a {
  display: inline-block;
  width: 120px;
  height: 40px;
  text-align: center;
  vertical-align: middle;     /* aligns to baseline by default */
}</code></pre>

<p><strong>The whitespace gotcha</strong> with <code>inline-block</code>: HTML whitespace between elements becomes visible space in the rendered layout. This was the historical reason developers reached for <code>float</code> &mdash; clean whitespace. Modern fixes:</p>
<pre><code>/* Method 1: zero font-size on parent */
.menu { font-size: 0; }
.menu a { font-size: 1rem; }       /* restore in children */

/* Method 2: use Flexbox instead — modern and clean */
.menu { display: flex; gap: 1rem; }</code></pre>

<p>In 2026, <code>inline-block</code> is rarely the right answer. Use <strong>Flexbox</strong> for one-dimensional layouts (rows or columns) and <strong>Grid</strong> for two-dimensional layouts &mdash; they handle alignment, gaps, and wrapping with no whitespace surprises and far cleaner code.</p>
'''

ANSWERS[2] = r'''
<p>The CSS box model describes every element as four nested boxes: <strong>content</strong> &rarr; <strong>padding</strong> &rarr; <strong>border</strong> &rarr; <strong>margin</strong>. Understanding it is essential because total rendered size depends on which boxes you&rsquo;re measuring.</p>

<table>
  <tr><th>Layer</th><th>Purpose</th><th>Affects layout space?</th></tr>
  <tr><td>Content</td><td>Holds text, image, or child elements</td><td>Yes</td></tr>
  <tr><td>Padding</td><td>Inner spacing between content and border</td><td>Yes</td></tr>
  <tr><td>Border</td><td>The line surrounding padding</td><td>Yes</td></tr>
  <tr><td>Margin</td><td>Outer spacing separating from neighbors</td><td>Yes (but transparent)</td></tr>
</table>

<p><strong>The default mode (<code>box-sizing: content-box</code>) surprises beginners:</strong></p>
<pre><code>.box {
  width: 200px;
  padding: 20px;
  border: 5px solid black;
}
/* Rendered total width = 200 + 40 + 10 = 250px */</code></pre>

<p>Setting <code>width: 200px</code> doesn&rsquo;t produce a 200px-wide box &mdash; padding and border are added on top. This breaks intuitive sizing math.</p>

<p><strong>The fix that everyone uses now &mdash; <code>border-box</code>:</strong></p>
<pre><code>*, *::before, *::after {
  box-sizing: border-box;
}

.box {
  width: 200px;
  padding: 20px;
  border: 5px solid black;
}
/* Rendered total width = exactly 200px; content shrinks to fit */</code></pre>

<p>With <code>border-box</code>, <code>width</code> and <code>height</code> include padding and border &mdash; what you see is what you set. This single rule eliminates a major class of layout bugs and is in essentially every modern CSS reset.</p>

<p><strong>Margin collapse</strong> &mdash; the box model&rsquo;s most surprising feature. When two block-level siblings stack vertically, their adjacent margins don&rsquo;t add &mdash; the larger value wins:</p>
<pre><code>.first  { margin-bottom: 30px; }
.second { margin-top:    20px; }
/* Vertical gap between them = 30px, NOT 50px */</code></pre>

<p>Margin collapse only happens between block-level siblings vertically. It doesn&rsquo;t happen with: inline elements, flex items, grid items, padding (which never collapses), or any direction other than vertical. To prevent collapse, create a "block formatting context" (BFC) on the parent: <code>display: flex</code>, <code>display: grid</code>, or <code>overflow: hidden</code>.</p>

<p><strong>Logical properties</strong> for international layouts: <code>padding-block</code>, <code>padding-inline</code>, <code>margin-block-start</code>, etc. mirror correctly for right-to-left languages without separate stylesheets.</p>
'''

ANSWERS[3] = r'''
<p>Both apply styles based on context, but they target different things. <strong>Pseudo-classes</strong> match elements in specific states or positions; <strong>pseudo-elements</strong> create or target sub-parts of elements that don&rsquo;t exist as their own DOM nodes.</p>

<table>
  <tr><th></th><th>Pseudo-class</th><th>Pseudo-element</th></tr>
  <tr><td>Syntax</td><td>Single colon (<code>:</code>)</td><td>Double colon (<code>::</code>)</td></tr>
  <tr><td>What it targets</td><td>An existing element in a state</td><td>A virtual sub-element</td></tr>
  <tr><td>Example</td><td><code>a:hover</code>, <code>li:first-child</code></td><td><code>p::first-letter</code>, <code>div::before</code></td></tr>
</table>

<p><strong>Common pseudo-classes:</strong></p>
<pre><code>a:hover    { color: red; }                  /* mouse over */
input:focus { outline: 2px solid blue; }    /* keyboard focus */
li:first-child { font-weight: bold; }       /* first sibling */
li:nth-child(odd) { background: #f5f5f5; }  /* every other */
input:checked + label { color: green; }     /* checked checkbox */
a:not([href]) { color: gray; }              /* without href */
.card:has(img) { padding: 0; }              /* contains an img */
button:user-invalid { border-color: red; }  /* invalid AFTER user input */</code></pre>

<p><strong>Common pseudo-elements:</strong></p>
<pre><code>p::first-letter { font-size: 3em; float: left; }
p::first-line   { font-weight: bold; }
input::placeholder { color: #999; font-style: italic; }
::selection     { background: yellow; }       /* selected text */
li::marker      { color: red; }                /* list bullets */

/* Generated content with ::before and ::after */
.required::after {
  content: " *";
  color: red;
}
.quote::before { content: open-quote; }
.quote::after  { content: close-quote; }</code></pre>

<p><strong>The <code>::before</code> and <code>::after</code> superpower</strong> &mdash; they let you add visual content without modifying HTML:</p>
<pre><code>/* Decorative arrow */
.btn::after { content: " &rarr;"; }

/* Required field indicator */
label.required::after { content: " *"; color: red; }

/* Counter-based numbering */
ol { counter-reset: section; }
ol li::before {
  counter-increment: section;
  content: counter(section, decimal-leading-zero) ". ";
  font-weight: bold;
}</code></pre>

<p><strong>Modern selectors worth knowing</strong> (2026 baseline):</p>
<table>
  <tr><th>Selector</th><th>Purpose</th></tr>
  <tr><td><code>:is(a, b, c)</code></td><td>Match if any selector matches; lowest specificity wins</td></tr>
  <tr><td><code>:where(...)</code></td><td>Like <code>:is()</code> but always specificity 0</td></tr>
  <tr><td><code>:has(child)</code></td><td>Parent selector &mdash; match parents containing X</td></tr>
  <tr><td><code>:user-invalid</code></td><td>Invalid only after user has interacted</td></tr>
</table>

<p><code>:has()</code> finally answers the long-standing "parent selector" question that CSS lacked for 25 years. <code>:where()</code> with zero specificity is great for design system base styles that should be easily overridden.</p>
'''

ANSWERS[4] = r'''
<p>CSS Grid is a two-dimensional layout system &mdash; it lets you control rows and columns simultaneously. Unlike Flexbox (1D), Grid handles complex page layouts where items align both horizontally and vertically.</p>

<p><strong>The minimum viable grid:</strong></p>
<pre><code>&lt;div class="grid"&gt;
  &lt;div&gt;1&lt;/div&gt;&lt;div&gt;2&lt;/div&gt;&lt;div&gt;3&lt;/div&gt;
  &lt;div&gt;4&lt;/div&gt;&lt;div&gt;5&lt;/div&gt;&lt;div&gt;6&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;     /* three equal columns */
    gap: 1rem;
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>fr</code> unit</strong> represents a fraction of available space &mdash; <code>1fr 1fr</code> means two equal columns; <code>2fr 1fr</code> means the first column gets twice the space. <code>fr</code> is the layout primitive that makes Grid math feel natural.</p>

<p><strong>Defining columns and rows:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>grid-template-columns</code></td><td>Sets column tracks (e.g. <code>200px 1fr 200px</code>)</td></tr>
  <tr><td><code>grid-template-rows</code></td><td>Sets row tracks (often left as <code>auto</code>)</td></tr>
  <tr><td><code>grid-template-areas</code></td><td>Named regions for declarative layouts</td></tr>
  <tr><td><code>gap</code></td><td>Space between cells (replaces <code>row-gap</code> + <code>column-gap</code>)</td></tr>
  <tr><td><code>repeat(N, ...)</code></td><td>Repeat a track pattern N times</td></tr>
  <tr><td><code>minmax(min, max)</code></td><td>Track size with bounds</td></tr>
  <tr><td><code>auto-fit</code> / <code>auto-fill</code></td><td>Automatic responsive columns</td></tr>
</table>

<p><strong>Responsive auto-fit</strong> &mdash; the modern workhorse:</p>
<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
/* Cards reflow naturally — 4+ columns on wide screens, 1 on phones */</code></pre>

<p><strong>Named template areas</strong> &mdash; declarative page layouts:</p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "aside  main"
    "footer footer";
  min-height: 100vh;
}
header { grid-area: header; }
aside  { grid-area: aside;  }
main   { grid-area: main;   }
footer { grid-area: footer; }</code></pre>

<p>The CSS reads like a visual diagram &mdash; HTML order is independent of visual placement. Reorder areas in the template, the layout shifts; the markup stays semantic.</p>

<p><strong>Spanning cells</strong>:</p>
<pre><code>.featured {
  grid-column: 1 / 3;     /* span columns 1 to 2 */
  grid-row: 1 / 3;         /* span two rows */
}
.full-width {
  grid-column: 1 / -1;    /* span all columns (-1 = last edge) */
}</code></pre>

<p><strong>Flexbox vs Grid:</strong> use Flexbox when content drives the layout (a row of variable-length tags); use Grid when the structure is the priority (a dashboard with named regions). They&rsquo;re complementary &mdash; most modern pages use Grid for the page-level layout and Flexbox for component-level rows.</p>
'''

ANSWERS[5] = r'''
<p>Flexbox is a one-dimensional layout system &mdash; designed for laying out items in a single row or column with control over alignment, distribution, and wrapping. The flex container has a <strong>main axis</strong> (horizontal in row mode) and a <strong>cross axis</strong> (perpendicular).</p>

<pre><code>.flex-container {
  display: flex;
  /* default: flex-direction: row */
  /* default: flex-wrap: nowrap */
  /* default: justify-content: flex-start */
  /* default: align-items: stretch */
}</code></pre>

<p><strong>Container properties</strong> (set on the parent):</p>
<table>
  <tr><th>Property</th><th>Controls</th></tr>
  <tr><td><code>flex-direction</code></td><td>Main axis: <code>row</code>, <code>row-reverse</code>, <code>column</code>, <code>column-reverse</code></td></tr>
  <tr><td><code>flex-wrap</code></td><td><code>nowrap</code> (default) or <code>wrap</code> &mdash; allow items to flow to next line</td></tr>
  <tr><td><code>justify-content</code></td><td>Main axis alignment: start, end, center, space-between, space-evenly</td></tr>
  <tr><td><code>align-items</code></td><td>Cross axis alignment: stretch, start, end, center, baseline</td></tr>
  <tr><td><code>align-content</code></td><td>Cross axis distribution when wrapping (multi-line)</td></tr>
  <tr><td><code>gap</code></td><td>Space between items (replaces margin tricks)</td></tr>
</table>

<p><strong>Item properties</strong> (set on flex children):</p>
<table>
  <tr><th>Property</th><th>Controls</th></tr>
  <tr><td><code>flex-grow</code></td><td>How much to grow if extra space (0 = no, 1+ = yes)</td></tr>
  <tr><td><code>flex-shrink</code></td><td>How much to shrink if not enough space</td></tr>
  <tr><td><code>flex-basis</code></td><td>Preferred size before grow/shrink</td></tr>
  <tr><td><code>flex</code></td><td>Shorthand: <code>grow shrink basis</code> (e.g. <code>1 1 200px</code>)</td></tr>
  <tr><td><code>order</code></td><td>Visual reordering without changing HTML</td></tr>
  <tr><td><code>align-self</code></td><td>Override container&rsquo;s <code>align-items</code> for one item</td></tr>
</table>

<p><strong>The famous <code>flex: 1</code></strong> shorthand expands to <code>flex: 1 1 0%</code> &mdash; equal-share growth from a zero base. Multiple items with <code>flex: 1</code> divide remaining space equally regardless of content size.</p>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Center anything (the canonical pattern) */
.center {
  display: flex;
  justify-content: center;     /* horizontal */
  align-items: center;          /* vertical */
}

/* Push last item to the right (logo + nav + button) */
.header {
  display: flex;
  justify-content: space-between;
}

/* Sidebar (fixed) + main (fluid) */
.layout {
  display: flex;
  gap: 2em;
}
.sidebar { flex: 0 0 250px; }   /* fixed 250px */
.main    { flex: 1; min-width: 0; }    /* fills the rest */

/* Equal-width responsive cards */
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}
.cards &gt; * {
  flex: 1 1 250px;       /* min 250px, grow equally, wrap when needed */
}</code></pre>

<p><strong>The <code>min-width: 0</code> gotcha</strong> &mdash; flex items default to <code>min-width: auto</code> based on content, which can cause overflow when the content is wide (e.g. a long URL). Override with <code>min-width: 0</code> to allow proper shrinking. Same applies to <code>min-height</code> in column flex containers.</p>

<p>Flex is for one dimension &mdash; pick row or column. For two-dimensional layouts (rows AND columns aligned), use Grid. The two systems compose well: most apps use Grid for the page shell and Flex for individual rows.</p>
'''

ANSWERS[6] = r'''
<p>The classic responsive Grid pattern uses <code>repeat(auto-fit, minmax(...))</code> &mdash; columns reflow automatically as the viewport changes, no media queries required.</p>

<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}</code></pre>

<p><strong>Reading the formula:</strong></p>
<ul>
  <li><strong><code>auto-fit</code></strong> &mdash; create as many columns as fit at the minimum width.</li>
  <li><strong><code>minmax(280px, 1fr)</code></strong> &mdash; each column is at least 280px; if there&rsquo;s extra space, columns share it equally up to filling the row.</li>
  <li><strong>Result:</strong> 4+ columns on wide screens, 3 on tablets, 2 on small tablets, 1 on phones &mdash; computed by the browser, not your media queries.</li>
</ul>

<p><strong><code>auto-fit</code> vs <code>auto-fill</code></strong> &mdash; subtle but important:</p>
<table>
  <tr><th></th><th><code>auto-fit</code></th><th><code>auto-fill</code></th></tr>
  <tr><td>With few items</td><td>Items stretch to fill the row</td><td>Items keep their min size; empty space remains</td></tr>
  <tr><td>Visual result</td><td>Cards expand</td><td>Cards stay narrow with empty trailing tracks</td></tr>
  <tr><td>Use when</td><td>Galleries, card grids that should fill space</td><td>Fixed-grid layouts where consistent sizes matter more</td></tr>
</table>

<p><strong>Combining with media queries</strong> for breakpoint-specific tweaks:</p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .layout {
    grid-template-columns: 200px 1fr;     /* sidebar appears on tablet+ */
  }
}

@media (min-width: 1200px) {
  .layout {
    grid-template-columns: 250px 1fr 250px;   /* two sidebars on wide */
  }
}</code></pre>

<p><strong>Container queries</strong> (2026 baseline) make this even more powerful &mdash; cards respond to <em>their parent container&rsquo;s</em> width, not the viewport. Same component renders differently in a sidebar (narrow) versus the main column (wide):</p>

<pre><code>.card {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 200px 1fr; gap: 1em; }
}</code></pre>

<p><strong>Naming containers</strong> for clarity in deeply-nested layouts:</p>
<pre><code>.sidebar { container-type: inline-size; container-name: sidebar; }

@container sidebar (min-width: 300px) {
  .widget { padding: 2em; }
}</code></pre>

<p>Container queries fundamentally change responsive design: components are responsive by themselves, not at the page level. A card is no longer responsible for asking "what&rsquo;s the viewport?" but rather "what&rsquo;s my container?" &mdash; vastly improving reusability.</p>
'''

ANSWERS[7] = r'''
<p>CSS custom properties (also called CSS variables) let you store and reuse values throughout a stylesheet. Unlike Sass variables (compile-time), they&rsquo;re live at runtime &mdash; readable and writable from JavaScript, queryable in DevTools, and they cascade and inherit like any other CSS property.</p>

<pre><code>:root {
  --color-primary: #0066cc;
  --color-secondary: #ff6b35;
  --spacing: 1rem;
  --radius: 8px;
  --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn {
  background: var(--color-primary);
  padding: var(--spacing);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}</code></pre>

<p><strong>Why <code>:root</code>?</strong> It&rsquo;s the highest scope &mdash; variables defined there are available everywhere. You can also scope variables to specific elements:</p>

<pre><code>.theme-dark {
  --color-primary: #4a90e2;
  --color-bg: #1a1a1a;
}

/* Children of .theme-dark inherit these overrides */
.theme-dark .btn { background: var(--color-primary); }   /* dark blue */</code></pre>

<p><strong>Fallback values</strong> for safety:</p>
<pre><code>.box {
  background: var(--bg-color, white);
  /* Uses white if --bg-color is undefined */
}

/* Nested fallbacks */
color: var(--brand-color, var(--text-color, black));</code></pre>

<p><strong>Reading and writing from JavaScript:</strong></p>
<pre><code>// Read
const root = document.documentElement;
const color = getComputedStyle(root).getPropertyValue("--color-primary");

// Write
root.style.setProperty("--color-primary", "#22c55e");
/* All elements using var(--color-primary) update instantly */</code></pre>

<p>This dynamic capability is what makes custom properties more powerful than Sass variables. Theme switching, dark mode, and runtime customization all just work.</p>

<p><strong>Theme switching pattern:</strong></p>
<pre><code>:root {
  --bg: white;
  --fg: #333;
}

[data-theme="dark"] {
  --bg: #1a1a1a;
  --fg: #f0f0f0;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {     /* OS preference if user hasn't chosen */
    --bg: #1a1a1a;
    --fg: #f0f0f0;
  }
}

body {
  background: var(--bg);
  color: var(--fg);
  transition: background 0.2s, color 0.2s;
}</code></pre>

<p><strong>The <code>@property</code> rule</strong> (2026 baseline) registers typed custom properties &mdash; enabling animation between values that aren&rsquo;t simple colors or lengths:</p>

<pre><code>@property --gradient-angle {
  syntax: "&lt;angle&gt;";
  inherits: false;
  initial-value: 0deg;
}

.box {
  --gradient-angle: 0deg;
  background: linear-gradient(var(--gradient-angle), red, blue);
  transition: --gradient-angle 1s;
}
.box:hover { --gradient-angle: 360deg; }   /* now ANIMATES smoothly */</code></pre>

<p>Without <code>@property</code>, the gradient angle would jump instantly &mdash; the browser doesn&rsquo;t know how to interpolate between two values of an untyped variable. Registering the type unlocks proper animation.</p>

<p>For design systems: define a small set of variables for primary colors, spacing scale, typography scale, shadows, and radii. Components reference variables only &mdash; never raw values. Theme changes become trivially easy.</p>
'''

ANSWERS[8] = r'''
<p>CSS preprocessors are languages that compile to CSS. They add features that were missing from CSS (variables, nesting, mixins, functions) and produce a regular CSS file as output. The most popular are <strong>Sass</strong> (and its <code>.scss</code> syntax), <strong>Less</strong>, and <strong>Stylus</strong>.</p>

<pre><code>// Sass example (.scss syntax)
$primary: #0066cc;
$radius: 8px;

@mixin button($color) {
  background: $color;
  color: white;
  padding: 0.5em 1em;
  border-radius: $radius;
  &amp;:hover {
    background: darken($color, 10%);
  }
}

.btn-primary {
  @include button($primary);
}

.card {
  padding: 1em;
  background: white;

  // Nested rules
  .card-title {
    font-size: 1.2em;
    margin-bottom: 0.5em;
  }

  &amp;:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}</code></pre>

<p><strong>Why preprocessors mattered historically:</strong></p>
<table>
  <tr><th>Feature</th><th>Pre-CSS3 problem solved</th></tr>
  <tr><td>Variables</td><td>Reusing values without copy-paste</td></tr>
  <tr><td>Nesting</td><td>Reducing selector repetition</td></tr>
  <tr><td>Mixins</td><td>Reusable rule blocks with parameters</td></tr>
  <tr><td>Functions</td><td>Color manipulation, math operations</td></tr>
  <tr><td>Imports</td><td>Splitting CSS without HTTP overhead</td></tr>
  <tr><td>Loops</td><td>Generating repetitive rules programmatically</td></tr>
</table>

<p><strong>What CSS now has natively (2026):</strong></p>
<ul>
  <li><strong>Custom properties</strong> &mdash; replaced Sass variables (and added runtime mutation).</li>
  <li><strong>Native nesting</strong> &mdash; <code>&amp;</code> works without a preprocessor.</li>
  <li><strong>Color functions</strong> &mdash; <code>color-mix()</code>, <code>oklch()</code>, relative color syntax.</li>
  <li><strong>Math via <code>calc()</code>, <code>min()</code>, <code>max()</code>, <code>clamp()</code></strong>.</li>
  <li><strong>Cascade layers (<code>@layer</code>)</strong> &mdash; explicit specificity ordering.</li>
  <li><strong>Container queries</strong> &mdash; component-level responsive design.</li>
</ul>

<pre><code>/* 2026 native CSS — looks remarkably like Sass */
.card {
  padding: var(--spacing);
  background: white;

  .card-title {
    font-size: 1.2em;
    margin-bottom: 0.5em;
  }

  &amp;:hover {
    box-shadow: var(--shadow-md);
  }
}</code></pre>

<p><strong>Why preprocessors still have a place:</strong></p>
<ul>
  <li><strong>Mixins with logic</strong> &mdash; conditional rules and complex generation; harder in pure CSS.</li>
  <li><strong>Loops</strong> &mdash; generating utility classes (e.g. spacing-1 through spacing-12).</li>
  <li><strong>Functions like <code>darken()</code></strong> &mdash; though native <code>color-mix(in srgb, var(--c), black 10%)</code> covers most cases now.</li>
  <li><strong>Build-time optimization</strong> &mdash; tree-shaking, autoprefixer, asset hashing.</li>
  <li><strong>Existing codebases</strong> &mdash; migration cost is real.</li>
</ul>

<p>For new projects in 2026, vanilla CSS is increasingly viable. Tools like <strong>PostCSS</strong> with select plugins (autoprefixer, postcss-preset-env) often replace full preprocessors. Frameworks like <strong>Tailwind</strong> (utility-first) and <strong>Lightning CSS</strong> (PostCSS&rsquo;s faster sibling) push the ecosystem toward less preprocessing.</p>
'''

ANSWERS[9] = r'''
<p>The CSS cascade is the algorithm browsers use to resolve conflicts when multiple rules target the same element. Three factors determine which rule wins, in order: <strong>origin/importance</strong>, <strong>specificity</strong>, and <strong>source order</strong>.</p>

<p><strong>1. Origin and importance</strong> &mdash; user-agent (browser default) &lt; user (browser settings) &lt; author (your CSS) &lt; <code>!important</code> reverses each level. Modern CSS adds <strong>cascade layers</strong> (<code>@layer</code>) that sit between origin and specificity.</p>

<p><strong>2. Specificity</strong> &mdash; calculated from the selector. Higher specificity wins. Format: <code>(inline, IDs, classes/attributes/pseudo-classes, elements/pseudo-elements)</code>.</p>

<table>
  <tr><th>Selector</th><th>Specificity</th></tr>
  <tr><td><code>*</code></td><td>(0, 0, 0, 0)</td></tr>
  <tr><td><code>p</code></td><td>(0, 0, 0, 1)</td></tr>
  <tr><td><code>p span</code></td><td>(0, 0, 0, 2)</td></tr>
  <tr><td><code>.error</code></td><td>(0, 0, 1, 0)</td></tr>
  <tr><td><code>p.error</code></td><td>(0, 0, 1, 1)</td></tr>
  <tr><td><code>p:hover</code></td><td>(0, 0, 1, 1)</td></tr>
  <tr><td><code>[data-x="y"]</code></td><td>(0, 0, 1, 0)</td></tr>
  <tr><td><code>#header</code></td><td>(0, 1, 0, 0)</td></tr>
  <tr><td><code>style="..."</code></td><td>(1, 0, 0, 0)</td></tr>
  <tr><td><code>!important</code></td><td>overrides everything in same origin</td></tr>
</table>

<p><strong>Calculating specificity</strong> &mdash; compare left-to-right. <code>.x.y.z</code> (0,0,3,0) beats <code>p#main</code> (0,1,0,1)? No &mdash; (0,1,0,1) wins because IDs (column 2) outrank classes (column 3) regardless of count.</p>

<pre><code>/* Three styles, three specificities */
.error           { color: red;   }   /* (0,0,1,0) */
p.error          { color: blue;  }   /* (0,0,1,1) — wins over .error */
#alerts .error   { color: green; }   /* (0,1,1,0) — wins all */</code></pre>

<p><strong>3. Source order</strong> &mdash; if specificity ties, the rule that appears later wins. This is why <code>!important</code> overrides should go later in the file.</p>

<p><strong>Modern selectors and specificity:</strong></p>
<table>
  <tr><th>Selector</th><th>Specificity</th></tr>
  <tr><td><code>:is(a, .b)</code></td><td>Highest of arguments &mdash; matches as <code>.b</code> here</td></tr>
  <tr><td><code>:where(a, .b)</code></td><td>Always 0 &mdash; useful for low-specificity base styles</td></tr>
  <tr><td><code>:not(.b)</code></td><td>Same as <code>.b</code> &mdash; takes inner specificity</td></tr>
  <tr><td><code>:has(.b)</code></td><td>Same as <code>.b</code></td></tr>
</table>

<p><strong>Cascade layers</strong> (2026 baseline) override specificity entirely:</p>
<pre><code>@layer reset, base, components, utilities;

@layer base { p { color: gray; } }              /* normal specificity */
@layer components { p.error { color: red; } }   /* normal specificity */

/* utilities layer ALWAYS wins over components, regardless of specificity */
@layer utilities {
  .text-blue { color: blue !important; }
}</code></pre>

<p>Layer order is established at declaration; later layers always win over earlier layers regardless of specificity. This dramatically reduces the need for <code>!important</code> in design systems.</p>

<p><strong>Avoiding specificity wars:</strong></p>
<ul>
  <li>Prefer single-class selectors. <code>.btn-primary</code> over <code>nav .button.primary</code>.</li>
  <li>Use cascade layers to organize architecture (reset, base, components, utilities).</li>
  <li>Use <code>:where()</code> for low-specificity defaults.</li>
  <li>Reserve <code>!important</code> for utility classes only.</li>
</ul>
'''

ANSWERS[10] = r'''
<p>CSS inheritance means certain properties pass from parent elements to their children automatically. Set <code>color</code> on <code>body</code>, and every child without an explicit color inherits it. This dramatically reduces boilerplate &mdash; you don&rsquo;t need to set typography on every element.</p>

<p><strong>Properties that inherit by default</strong> are mostly typography-related:</p>
<ul>
  <li><code>color</code>, <code>font-family</code>, <code>font-size</code>, <code>font-weight</code>, <code>font-style</code>.</li>
  <li><code>line-height</code>, <code>letter-spacing</code>, <code>word-spacing</code>, <code>text-align</code>, <code>text-transform</code>.</li>
  <li><code>direction</code>, <code>visibility</code>, <code>cursor</code>, <code>list-style</code>.</li>
  <li>Custom properties (<code>--my-var</code>) inherit too &mdash; this is what makes theming work.</li>
</ul>

<p><strong>Properties that DO NOT inherit by default</strong> are layout/box-model:</p>
<ul>
  <li><code>margin</code>, <code>padding</code>, <code>border</code>, <code>width</code>, <code>height</code>.</li>
  <li><code>background</code>, <code>display</code>, <code>position</code>, <code>top</code>/<code>left</code>/etc.</li>
  <li><code>opacity</code>, <code>z-index</code>, <code>flex</code>, <code>grid</code> properties.</li>
</ul>

<p><strong>Force or prevent inheritance</strong> with the four global keywords:</p>
<table>
  <tr><th>Keyword</th><th>Effect</th></tr>
  <tr><td><code>inherit</code></td><td>Take the parent&rsquo;s computed value</td></tr>
  <tr><td><code>initial</code></td><td>Reset to the property&rsquo;s spec default</td></tr>
  <tr><td><code>unset</code></td><td>Inherit if inheritable, otherwise initial</td></tr>
  <tr><td><code>revert</code></td><td>Roll back to the user-agent (browser default) value</td></tr>
</table>

<pre><code>.box {
  /* Force the border (which doesn't normally inherit) to inherit */
  border-color: inherit;
}

.reset-button {
  /* Strip ALL custom styling */
  all: unset;     /* equivalent to setting every property to 'unset' */
  cursor: pointer;
}</code></pre>

<p>The <code>all</code> shorthand sets every property at once &mdash; useful for stripping styles from inputs or buttons.</p>

<p><strong>How inheritance works with custom properties:</strong></p>
<pre><code>:root { --primary: blue; }

.card {
  /* The variable cascades down through every descendant */
}
.card .button {
  background: var(--primary);    /* finds 'blue' from :root */
}

/* Override at any level — children inherit the override */
.theme-orange {
  --primary: orange;   /* descendants of .theme-orange now get orange */
}</code></pre>

<p>This is why CSS variables are uniquely powerful for theming &mdash; one override at any DOM level cascades through everything below.</p>

<p><strong>Common inheritance gotchas:</strong></p>
<ul>
  <li><strong>Form controls don&rsquo;t inherit typography</strong> by default &mdash; <code>&lt;input&gt;</code>, <code>&lt;button&gt;</code>, <code>&lt;select&gt;</code> use the OS font. Reset with <code>font: inherit;</code> on form elements.</li>
  <li><strong>Anchors don&rsquo;t inherit color</strong> in older browsers &mdash; modern browsers do via <code>:link</code> defaults.</li>
  <li><strong>SVG <code>fill</code> doesn&rsquo;t inherit from <code>color</code></strong> &mdash; use <code>fill: currentColor</code> to bridge them.</li>
</ul>

<p><strong>Architectural advice:</strong> set base typography on <code>body</code>; let the cascade do the work. Override only when the design demands it. Modern CSS reset stylesheets do this aggressively &mdash; they ensure consistent inheritance baselines so designers don&rsquo;t have to fight browser defaults.</p>
'''

ANSWERS[11] = r'''
<p>The cleanest sticky header uses <code>position: sticky</code> with <code>top: 0</code> &mdash; the header scrolls with the page until it reaches the top, then locks in place. No JavaScript, correct fallbacks, no offset padding required.</p>

<pre><code>.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  border-bottom: 1px solid #eee;
  padding: 1em;
}</code></pre>

<p><strong>Sticky vs Fixed:</strong></p>
<table>
  <tr><th></th><th><code>position: sticky</code></th><th><code>position: fixed</code></th></tr>
  <tr><td>Layout</td><td>Takes natural space, then sticks at threshold</td><td>Removed from flow always</td></tr>
  <tr><td>Need to offset content?</td><td>No</td><td>Yes (<code>padding-top</code> equal to header height)</td></tr>
  <tr><td>Containing block</td><td>Nearest scrollable ancestor</td><td>Viewport</td></tr>
  <tr><td>Behavior on long parent</td><td>Sticks within parent&rsquo;s scroll area</td><td>Always at viewport position</td></tr>
</table>

<p><strong>The <code>position: sticky</code> requirements:</strong></p>
<ul>
  <li><strong>A directional offset</strong> (<code>top</code>, <code>bottom</code>, <code>left</code>, or <code>right</code>) is mandatory; otherwise the element behaves as <code>relative</code>.</li>
  <li><strong>The parent must be scrollable</strong> &mdash; or a higher ancestor. Sticky operates within its containing block&rsquo;s scroll area.</li>
  <li><strong>No ancestor with <code>overflow: hidden</code>, <code>auto</code>, or <code>scroll</code></strong> &mdash; or sticky operates within that ancestor (often invisibly). This is the most common reason "sticky doesn&rsquo;t work."</li>
</ul>

<p><strong>The "stuck" detection pattern</strong> &mdash; trigger style changes when the header sticks:</p>

<pre><code>&lt;div class="sentinel"&gt;&lt;/div&gt;
&lt;header class="site-header"&gt;...&lt;/header&gt;

&lt;script&gt;
  const observer = new IntersectionObserver(
    ([entry]) =&gt; {
      document.querySelector(".site-header")
        .classList.toggle("is-stuck", !entry.isIntersecting);
    },
    { threshold: 1 },
  );
  observer.observe(document.querySelector(".sentinel"));
&lt;/script&gt;

&lt;style&gt;
  .sentinel { height: 1px; }
  .site-header { transition: padding 0.2s, box-shadow 0.2s; }
  .site-header.is-stuck {
    padding: 0.5em 1em;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }
&lt;/style&gt;</code></pre>

<p>An invisible 1px sentinel above the header tracks visibility &mdash; when it scrolls out of view, the header has stuck. The IntersectionObserver pattern is far more efficient than scroll listeners (which fire 60+ times per second).</p>

<p><strong>Anchor link gotcha</strong> &mdash; sticky headers cover the top of anchor link targets. Fix with <code>scroll-margin-top</code>:</p>
<pre><code>section[id] {
  scroll-margin-top: 70px;       /* approximately header height */
}
:target {
  /* (optional) highlight the targeted section briefly */
  animation: highlight 1s;
}</code></pre>

<p><strong>Compact header on scroll pattern</strong> &mdash; popular Material Design technique. Combine sticky positioning + IntersectionObserver detection + transitions on padding/font-size to shrink the header as the user scrolls. The "is-stuck" class triggers the compact style.</p>

<p>For modern apps, <code>position: sticky</code> is preferred over <code>fixed</code>. It composes naturally with the document flow, doesn&rsquo;t need offset hacks, and respects parent containers properly.</p>
'''

ANSWERS[12] = r'''
<p>Media queries apply CSS conditionally based on the device or context &mdash; viewport width, resolution, color scheme, motion preferences, hover capability, and more. They&rsquo;re the foundation of responsive design and accessibility-aware styling.</p>

<pre><code>/* Apply only when viewport is at least 768px wide */
@media (min-width: 768px) {
  .container { display: flex; }
}

/* Combine conditions with 'and' */
@media (min-width: 768px) and (orientation: landscape) {
  .hero { height: 60vh; }
}

/* Multiple conditions with 'or' (comma-separated) */
@media (max-width: 600px), (orientation: portrait) {
  .nav { flex-direction: column; }
}

/* Negation with 'not' */
@media not (hover: hover) {
  /* Touch devices — no hover capability */
  .card .actions { display: flex; }
}</code></pre>

<p><strong>Common media features for responsive design:</strong></p>
<table>
  <tr><th>Feature</th><th>Tests</th></tr>
  <tr><td><code>min-width</code> / <code>max-width</code></td><td>Viewport width</td></tr>
  <tr><td><code>min-height</code> / <code>max-height</code></td><td>Viewport height</td></tr>
  <tr><td><code>orientation</code></td><td><code>portrait</code> or <code>landscape</code></td></tr>
  <tr><td><code>aspect-ratio</code></td><td>Viewport ratio</td></tr>
  <tr><td><code>resolution</code></td><td>Pixel density (e.g. <code>2dppx</code> for retina)</td></tr>
</table>

<p><strong>User preference queries</strong> (essential for accessibility):</p>
<pre><code>@media (prefers-color-scheme: dark) {
  :root { --bg: #1a1a1a; --fg: #f0f0f0; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-contrast: more) {
  body { color: black; background: white; }
  a { text-decoration: underline; }
}

@media (prefers-reduced-data: reduce) {
  /* Skip optional images, animations */
  .decorative { display: none; }
}</code></pre>

<p>Always include <code>prefers-reduced-motion</code> handling &mdash; some users have vestibular disorders triggered by motion. WCAG 2.3 specifies this as a requirement.</p>

<p><strong>Hover and pointer queries</strong> &mdash; touch vs mouse:</p>
<pre><code>@media (hover: hover) {
  /* Mouse — hover effects safe */
  .card:hover { transform: scale(1.05); }
}

@media (pointer: coarse) {
  /* Touch — make tap targets bigger */
  button { min-height: 44px; min-width: 44px; }
}</code></pre>

<p><strong>Modern range syntax</strong> (2026 baseline) is more readable:</p>
<pre><code>/* Old */
@media (min-width: 768px) and (max-width: 1199px) { ... }

/* New */
@media (768px &lt;= width &lt;= 1199px) { ... }</code></pre>

<p><strong>Container queries</strong> (also 2026 baseline) complement media queries &mdash; respond to a parent&rsquo;s size rather than the viewport:</p>
<pre><code>.card { container-type: inline-size; }

@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}</code></pre>

<p>Components become responsive based on where they&rsquo;re placed, not the page width. Same component, different presentations &mdash; sidebar narrow, main column wide. Container queries are the biggest improvement to responsive CSS in years.</p>

<p><strong>Best practices:</strong> mobile-first (start with default styles for small screens, add complexity with <code>min-width</code>); avoid pixel-exact breakpoints; use <code>em</code>/<code>rem</code> in queries to respect user font-size preferences (e.g. <code>(min-width: 48em)</code>).</p>
'''

ANSWERS[13] = r'''
<p>Mobile-first design means writing baseline CSS for the smallest screens, then progressively enhancing for larger viewports with media queries. The opposite (desktop-first) starts with desktop styles and uses <code>max-width</code> to shrink &mdash; harder to maintain as devices proliferate.</p>

<pre><code>/* Mobile-first: baseline = mobile */
.layout {
  display: block;
  padding: 1em;
}

@media (min-width: 768px) {
  /* Tablet enhancements */
  .layout {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 2em;
    padding: 2em;
  }
}

@media (min-width: 1200px) {
  /* Desktop enhancements */
  .layout {
    grid-template-columns: 250px 1fr 250px;
    max-width: 1400px;
    margin: 0 auto;
  }
}</code></pre>

<p><strong>Why mobile-first wins in 2026:</strong></p>

<table>
  <tr><th>Mobile-first</th><th>Desktop-first</th></tr>
  <tr><td>Baseline serves the most constrained device</td><td>Baseline serves the most capable device</td></tr>
  <tr><td>Mobile users (most traffic) get optimized CSS</td><td>Mobile users download desktop CSS first, override</td></tr>
  <tr><td>Adds complexity at larger sizes</td><td>Hides complexity at smaller sizes</td></tr>
  <tr><td>Aligns with progressive enhancement philosophy</td><td>Aligns with graceful degradation philosophy</td></tr>
  <tr><td>Better Core Web Vitals (smaller initial CSS)</td><td>Worse mobile performance</td></tr>
  <tr><td>Maps cleanly to <code>min-width</code> queries</td><td>Requires <code>max-width</code> queries with edge cases</td></tr>
</table>

<p><strong>Progressive enhancement approach:</strong></p>
<ol>
  <li><strong>Single column, full-width on mobile</strong> &mdash; the simplest case.</li>
  <li><strong>Tablet (768px+)</strong> &mdash; introduce sidebars, multi-column layouts.</li>
  <li><strong>Desktop (1200px+)</strong> &mdash; max-widths, sidebars, complex grids.</li>
  <li><strong>Wide desktop (1600px+)</strong> &mdash; constrain to readable widths.</li>
</ol>

<p><strong>Modern alternative: intrinsic responsive design</strong> &mdash; layouts that adapt without breakpoints:</p>
<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
/* Adapts from 1 column to N columns based on available space — no media queries */</code></pre>

<p><strong>Fluid typography with <code>clamp()</code></strong> &mdash; size scales smoothly with viewport:</p>
<pre><code>h1 {
  font-size: clamp(1.5rem, 4vw + 1rem, 3.5rem);
  /* min: 1.5rem, scales with viewport, max: 3.5rem */
}</code></pre>

<p>One line replaces multiple media queries for typography. Pair with logical max-widths (<code>max-width: 65ch</code> for readable text) for layouts that "just work" across viewports.</p>

<p><strong>Container queries</strong> (2026) push this further: components respond to their parent&rsquo;s width, not the viewport. The same card looks one way in a sidebar, another in the main column &mdash; without the page knowing or caring.</p>

<p><strong>Common breakpoints</strong> (no fixed standard &mdash; pick what fits the design):</p>
<ul>
  <li>Mobile: 0-599px (default; no query needed)</li>
  <li>Tablet: 600-899px (<code>@media (min-width: 600px)</code>)</li>
  <li>Small desktop: 900-1199px (<code>@media (min-width: 900px)</code>)</li>
  <li>Desktop: 1200px+ (<code>@media (min-width: 1200px)</code>)</li>
  <li>Wide: 1600px+ (<code>@media (min-width: 1600px)</code>)</li>
</ul>

<p>Use <code>em</code> units in queries instead of <code>px</code> &mdash; they respect user font-size preferences. <code>(min-width: 48em)</code> = 768px at default font size, but scales up if the user has bumped their browser default.</p>
'''

ANSWERS[14] = r'''
<p>CSS animations let you change properties over time using <code>@keyframes</code> rules. Unlike transitions (which animate between two states triggered by an event), animations run on a schedule defined by keyframes &mdash; multiple steps, looping, delays, and complex sequences.</p>

<pre><code>.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}</code></pre>

<p>The <code>@keyframes</code> rule defines named timing markers; the <code>animation</code> property tells an element to use them.</p>

<p><strong>Keyframes &mdash; describing the animation:</strong></p>
<pre><code>@keyframes pulse {
  0%   { transform: scale(1);   opacity: 1; }
  50%  { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1);   opacity: 1; }
}

/* from/to are aliases for 0%/100% */
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}</code></pre>

<p><strong>Animation properties &mdash; the eight knobs:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>animation-name</code></td><td>Which keyframes to run</td></tr>
  <tr><td><code>animation-duration</code></td><td>How long each cycle takes</td></tr>
  <tr><td><code>animation-timing-function</code></td><td>Curve: <code>linear</code>, <code>ease</code>, <code>ease-in-out</code>, <code>cubic-bezier(...)</code></td></tr>
  <tr><td><code>animation-delay</code></td><td>Time before starting</td></tr>
  <tr><td><code>animation-iteration-count</code></td><td><code>1</code>, <code>3</code>, <code>infinite</code></td></tr>
  <tr><td><code>animation-direction</code></td><td><code>normal</code>, <code>reverse</code>, <code>alternate</code></td></tr>
  <tr><td><code>animation-fill-mode</code></td><td><code>forwards</code> keeps end state; <code>backwards</code> applies start state during delay</td></tr>
  <tr><td><code>animation-play-state</code></td><td><code>running</code> or <code>paused</code></td></tr>
</table>

<p><strong>Shorthand:</strong> <code>animation: name duration timing-function delay iteration-count direction fill-mode play-state</code>.</p>

<p><strong>Performance &mdash; animate the right properties:</strong></p>
<table>
  <tr><th>Property type</th><th>Cost</th><th>Examples</th></tr>
  <tr><td>Compositor (cheap)</td><td>GPU-accelerated</td><td><code>transform</code>, <code>opacity</code>, <code>filter</code></td></tr>
  <tr><td>Paint (medium)</td><td>Repaints layer</td><td><code>color</code>, <code>background-color</code>, <code>box-shadow</code></td></tr>
  <tr><td>Layout (expensive)</td><td>Recalculates layout</td><td><code>width</code>, <code>height</code>, <code>top</code>, <code>margin</code></td></tr>
</table>

<p>For 60fps animations, stick to <code>transform</code> and <code>opacity</code>. Animating <code>width</code> triggers layout recalculation on every frame &mdash; expensive on complex pages.</p>

<p><strong>Looping with alternate direction</strong> for breathing/pulsing effects:</p>
<pre><code>.heartbeat {
  animation: pulse 1s ease-in-out infinite alternate;
}
@keyframes pulse {
  from { transform: scale(1); }
  to   { transform: scale(1.05); }
}
/* Goes 1 → 1.05 → 1 → 1.05 forever, smoothly */</code></pre>

<p><strong>Staggered animations</strong> with <code>animation-delay</code>:</p>
<pre><code>.dots span:nth-child(1) { animation-delay: 0s; }
.dots span:nth-child(2) { animation-delay: 0.1s; }
.dots span:nth-child(3) { animation-delay: 0.2s; }</code></pre>

<p>Each child starts slightly later, creating wave or cascade effects.</p>

<p><strong>Always respect <code>prefers-reduced-motion</code>:</strong></p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}</code></pre>

<p>This puts a global ceiling on motion intensity for users with vestibular disorders. Required for WCAG 2.3 compliance.</p>

<p><strong>Modern features (2026):</strong> <code>scroll-driven animations</code> link animation progress to scroll position; <code>view transitions</code> animate between page states; <code>@property</code> enables animating typed custom properties (gradient angles, color stops).</p>
'''

ANSWERS[15] = r'''
<p>Both transitions and animations interpolate between values over time, but they have fundamentally different triggers, capabilities, and use cases.</p>

<table>
  <tr><th></th><th>Transitions</th><th>Animations</th></tr>
  <tr><td>Trigger</td><td>State change (hover, class toggle, attribute change)</td><td>Schedule on page load (or via class change)</td></tr>
  <tr><td>States</td><td>Two: from current value to new value</td><td>Many: defined in <code>@keyframes</code></td></tr>
  <tr><td>Looping</td><td>No (manually retrigger)</td><td>Built-in via <code>iteration-count</code></td></tr>
  <tr><td>Granularity</td><td>One step</td><td>Multiple keyframes (0%, 25%, 50%, etc.)</td></tr>
  <tr><td>Pause / play control</td><td>No</td><td>Yes (<code>animation-play-state</code>)</td></tr>
  <tr><td>Specifying intermediate</td><td>Implicit (browser interpolates)</td><td>Explicit (you define keyframes)</td></tr>
  <tr><td>Definition</td><td>One declaration</td><td><code>@keyframes</code> block + properties</td></tr>
</table>

<p><strong>Transition example &mdash; smooth hover:</strong></p>
<pre><code>.btn {
  background: blue;
  transition: background 0.3s ease;
}
.btn:hover {
  background: darkblue;
}
/* Transition triggered by :hover state */</code></pre>

<p><strong>Animation example &mdash; continuous spin:</strong></p>
<pre><code>.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
/* Runs immediately on load, loops forever */</code></pre>

<p><strong>When to use which:</strong></p>
<ul>
  <li><strong>Transition</strong> &mdash; smooth state changes triggered by user action: hover effects, focus states, expand/collapse, enter/leave (with <code>view transitions</code>).</li>
  <li><strong>Animation</strong> &mdash; complex sequences, looping motion, page-load reveals, loading indicators, attention-grabbers.</li>
</ul>

<p><strong>The hybrid approach</strong> &mdash; class toggles trigger animations:</p>
<pre><code>.modal {
  opacity: 0;
  transform: scale(0.9);
}
.modal.is-open {
  animation: enter 0.3s ease forwards;
}
@keyframes enter {
  from { opacity: 0; transform: scale(0.9); }
  to   { opacity: 1; transform: scale(1); }
}</code></pre>

<p>Adding <code>.is-open</code> via JavaScript triggers the animation. <code>animation-fill-mode: forwards</code> keeps the end state.</p>

<p><strong>Choosing which:</strong></p>
<ul>
  <li>Two-state change (off &harr; on)? Transition.</li>
  <li>Triggered by a state pseudo-class (<code>:hover</code>, <code>:focus</code>, <code>:checked</code>)? Transition.</li>
  <li>Loops forever? Animation.</li>
  <li>Multiple intermediate steps? Animation.</li>
  <li>Plays on page load? Animation.</li>
  <li>Need to pause/resume? Animation.</li>
</ul>

<p><strong>Performance note:</strong> both transitions and animations run on the same engine. The properties you animate matter more than the technique &mdash; <code>transform</code> and <code>opacity</code> are GPU-accelerated; <code>width</code>, <code>top</code>, etc. trigger layout. Stick to compositor-friendly properties for either.</p>

<p><strong>2026 modern feature: <code>view-transition</code></strong> bridges the gap &mdash; it animates between two states (transition-like trigger) but with full keyframe-style control. Replaces complex enter/leave animations with a single API.</p>
'''

ANSWERS[16] = r'''
<p>Hover effects on buttons combine <code>transition</code> for smoothness with optional keyframe animations for richer interactions. The pattern: declare transitions on the base, change properties on <code>:hover</code>, optionally trigger an animation for click feedback.</p>

<pre><code>.btn {
  background: #0066cc;
  color: white;
  padding: 0.75em 1.5em;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  /* Apply transition to the BASE selector — animates BOTH directions */
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.btn:hover {
  background: #004999;
  transform: translateY(-2px);              /* lift effect */
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.btn:active {
  transform: translateY(0);                  /* press down */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}</code></pre>

<p><strong>Common interactive patterns:</strong></p>

<p><strong>1. Slide-in shine effect</strong> &mdash; pseudo-element sweeps across:</p>
<pre><code>.btn-shine {
  position: relative;
  overflow: hidden;
}
.btn-shine::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg,
    transparent 0%,
    rgba(255,255,255,0.3) 50%,
    transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.5s;
}
.btn-shine:hover::before {
  transform: translateX(100%);
}</code></pre>

<p><strong>2. Border draw</strong> &mdash; outline expands on hover:</p>
<pre><code>.btn-outline {
  background: transparent;
  border: 2px solid currentColor;
  position: relative;
  overflow: hidden;
  z-index: 0;
}
.btn-outline::before {
  content: "";
  position: absolute;
  inset: 0;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
  z-index: -1;
}
.btn-outline:hover {
  color: white;
}
.btn-outline:hover::before {
  transform: scaleX(1);
  transform-origin: left;
}</code></pre>

<p>The <code>::before</code> fills the button on hover with origin-shift, creating a wipe-from-left effect.</p>

<p><strong>3. Ripple effect (Material Design)</strong> &mdash; click animation:</p>
<pre><code>.btn-ripple {
  position: relative;
  overflow: hidden;
}
.btn-ripple::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  transform: translate(-50%, -50%);
  transition: width 0.4s, height 0.4s;
}
.btn-ripple:active::after {
  width: 200%;
  height: 200%;
  transition: width 0s, height 0s;     /* reset for next click */
}</code></pre>

<p><strong>Animation triggered on hover</strong> &mdash; for richer effects:</p>
<pre><code>.btn-bounce:hover {
  animation: bounce 0.5s ease;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-10px); }
}</code></pre>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Apply <code>transition</code> to the base selector</strong>, not <code>:hover</code> &mdash; this makes the effect smooth in BOTH directions (entering AND leaving the hover state).</li>
  <li><strong>Use <code>transform</code> and <code>opacity</code></strong> for performance &mdash; GPU-accelerated.</li>
  <li><strong>Use <code>:focus-visible</code> for keyboard accessibility</strong> &mdash; show focus rings only when navigating by keyboard, not mouse.</li>
  <li><strong>Add <code>:active</code> states</strong> for click feedback &mdash; users feel responsiveness on touch devices.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; disable transforms for users who&rsquo;ve opted out of motion.</li>
  <li><strong>Keep durations short</strong> &mdash; 150-300ms feels responsive; longer feels sluggish.</li>
</ul>
'''

ANSWERS[17] = r'''
<p>The <code>position</code> property removes elements from the normal document flow and reanchors them to a different reference frame. The five values produce dramatically different layouts.</p>

<table>
  <tr><th>Value</th><th>In normal flow?</th><th>Anchored to</th><th>Use case</th></tr>
  <tr><td><code>static</code></td><td>Yes (default)</td><td>Document flow</td><td>Default behavior</td></tr>
  <tr><td><code>relative</code></td><td>Yes (offset from natural position)</td><td>Itself</td><td>Containing block for absolute children; small nudges</td></tr>
  <tr><td><code>absolute</code></td><td>No (removed from flow)</td><td>Nearest non-static ancestor</td><td>Tooltips, dropdowns, overlays</td></tr>
  <tr><td><code>fixed</code></td><td>No</td><td>Viewport</td><td>Persistent UI: modals, fab buttons, sticky headers (legacy)</td></tr>
  <tr><td><code>sticky</code></td><td>Yes (until threshold, then sticks)</td><td>Nearest scrolling ancestor</td><td>Sticky table headers, sidebars, navigation</td></tr>
</table>

<p><strong>The crucial requirement:</strong> <code>top</code>, <code>right</code>, <code>bottom</code>, <code>left</code> only work on <strong>positioned elements</strong> &mdash; not on the default <code>static</code>.</p>

<pre><code>.normal { /* position: static; default — top/left ignored */ }

.nudged {
  position: relative;
  top: 5px;
  left: 10px;
  /* Renders 5px down and 10px right of natural position */
  /* Original space is preserved */
}

.tooltip {
  position: absolute;
  top: 100%;       /* below parent */
  left: 50%;
  transform: translateX(-50%);
  /* Anchored to nearest positioned ancestor */
}

.modal {
  position: fixed;
  inset: 0;        /* shorthand for top/right/bottom/left: 0 */
  /* Anchored to viewport — stays during scroll */
}

.sticky-nav {
  position: sticky;
  top: 0;
  /* Scrolls with page until hitting top, then sticks */
}</code></pre>

<p><strong>Containing block rules</strong> &mdash; what does <code>top: 0</code> measure from?</p>
<ul>
  <li><strong>Static / relative:</strong> the element&rsquo;s natural position.</li>
  <li><strong>Absolute:</strong> the nearest <em>positioned</em> ancestor (<code>relative</code>, <code>absolute</code>, <code>fixed</code>, <code>sticky</code>). If none, the initial containing block (the viewport).</li>
  <li><strong>Fixed:</strong> the viewport.</li>
  <li><strong>Sticky:</strong> the nearest scroll container.</li>
</ul>

<p><strong>The <code>position: relative</code> as anchor pattern</strong> &mdash; commonly used to scope absolute positioning:</p>
<pre><code>.card {
  position: relative;       /* doesn&rsquo;t actually move; just creates an anchor */
}
.card .badge {
  position: absolute;
  top: -10px;
  right: -10px;
  /* Now positioned relative to .card, not page */
}</code></pre>

<p><strong>The <code>inset</code> shorthand</strong> (2026 baseline) sets all four offsets at once:</p>
<pre><code>.fullscreen {
  position: fixed;
  inset: 0;                  /* same as top:0; right:0; bottom:0; left:0; */
}
.centered-overlay {
  position: absolute;
  inset: 0;
  margin: auto;              /* requires width and height */
  width: 300px;
  height: 200px;
}</code></pre>

<p>Setting <code>inset: 0</code> + <code>margin: auto</code> centers an absolutely-positioned element with explicit dimensions &mdash; cleaner than <code>top: 50%; left: 50%; transform: translate(-50%, -50%)</code>.</p>

<p><strong>Stacking and z-index</strong> &mdash; positioned elements participate in stacking. Without <code>z-index</code>, later in DOM = higher in stack. With <code>z-index</code>, higher number = higher in stack <em>within the same stacking context</em>.</p>

<p><strong>Anchor positioning</strong> (modern, 2026): <code>position-anchor</code> + <code>anchor()</code> functions enable positioning relative to a specific element by name &mdash; no <code>position: relative</code> required on a wrapper. Game-changer for tooltips and dropdowns.</p>
'''

ANSWERS[18] = r'''
<p>A CSS-only dropdown menu uses <code>:hover</code> on a parent to reveal a child menu. Modern variants use <code>:focus-within</code> for keyboard accessibility, or <code>&lt;details&gt;</code>/<code>&lt;summary&gt;</code> for click-to-open behavior.</p>

<pre><code>&lt;nav class="navbar"&gt;
  &lt;ul&gt;
    &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
    &lt;li class="dropdown"&gt;
      &lt;a href="#"&gt;Products &#9662;&lt;/a&gt;
      &lt;ul class="submenu"&gt;
        &lt;li&gt;&lt;a href="#"&gt;Product A&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Product B&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Product C&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/li&gt;
    &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
  &lt;/ul&gt;
&lt;/nav&gt;

&lt;style&gt;
  .navbar &gt; ul {
    display: flex;
    gap: 1.5em;
    list-style: none;
    padding: 0;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  .navbar a {
    display: block;
    padding: 1em;
    color: #333;
    text-decoration: none;
  }
  .navbar a:hover { background: #f0f8ff; }

  .dropdown {
    position: relative;
  }

  .submenu {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 200px;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    list-style: none;
    padding: 0.5em 0;
    margin: 0;
    border-radius: 0 0 8px 8px;

    /* Hidden by default */
    opacity: 0;
    visibility: hidden;
    transform: translateY(-5px);
    transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
  }

  /* Show on hover OR when focus enters the dropdown (keyboard) */
  .dropdown:hover .submenu,
  .dropdown:focus-within .submenu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }
&lt;/style&gt;</code></pre>

<p><strong>Key techniques:</strong></p>
<ul>
  <li><strong><code>position: relative</code> on the dropdown <code>li</code></strong> makes it the anchor for the submenu.</li>
  <li><strong><code>position: absolute; top: 100%</code></strong> positions the submenu directly below the parent.</li>
  <li><strong><code>opacity</code> + <code>visibility</code></strong> &mdash; using both lets you transition smoothly. <code>display: none</code> can&rsquo;t be transitioned.</li>
  <li><strong><code>:focus-within</code></strong> &mdash; opens the menu when a child receives keyboard focus (essential for keyboard accessibility).</li>
</ul>

<p><strong>Click-to-open with <code>&lt;details&gt;</code></strong> &mdash; native, accessible, no JavaScript:</p>
<pre><code>&lt;details class="dropdown"&gt;
  &lt;summary&gt;Products&lt;/summary&gt;
  &lt;ul&gt;
    &lt;li&gt;&lt;a href="#"&gt;Product A&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="#"&gt;Product B&lt;/a&gt;&lt;/li&gt;
  &lt;/ul&gt;
&lt;/details&gt;

&lt;style&gt;
  details.dropdown {
    position: relative;
    list-style: none;
  }
  details.dropdown summary {
    cursor: pointer;
    padding: 1em;
    list-style: none;
  }
  details.dropdown ul {
    position: absolute;
    top: 100%;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    list-style: none;
    padding: 0.5em 0;
    min-width: 200px;
  }
&lt;/style&gt;</code></pre>

<p>This pattern works perfectly without JavaScript &mdash; clicking the summary toggles open/closed state. Pair sibling <code>details</code> elements with the same <code>name</code> attribute to create accordion-like behavior (only one open at a time).</p>

<p><strong>Modern alternative: Popover API</strong> (2026 baseline):</p>
<pre><code>&lt;button popovertarget="menu"&gt;Products&lt;/button&gt;
&lt;ul id="menu" popover&gt;
  &lt;li&gt;&lt;a href="#"&gt;A&lt;/a&gt;&lt;/li&gt;
&lt;/ul&gt;</code></pre>

<p>The Popover API gives proper modal behavior, top-layer rendering, dismiss-on-Escape, and focus management for free. Combined with CSS Anchor Positioning, it&rsquo;s the cleanest path to accessible dropdowns.</p>

<p>For production accessibility (ARIA roles, keyboard arrows, type-to-search), libraries like Radix UI Menu or Headless UI handle the full pattern correctly &mdash; CSS-only dropdowns work for simple navigation but fall short on rich menus.</p>
'''

ANSWERS[19] = r'''
<p>CSS combinators define relationships between selectors &mdash; how one element relates to another in the DOM. Four combinators exist, each matching a different positional relationship.</p>

<table>
  <tr><th>Combinator</th><th>Selector</th><th>Matches</th></tr>
  <tr><td>Descendant (space)</td><td><code>.parent .child</code></td><td>Any descendant at any depth</td></tr>
  <tr><td>Child (<code>&gt;</code>)</td><td><code>.parent &gt; .child</code></td><td>Direct children only</td></tr>
  <tr><td>Adjacent sibling (<code>+</code>)</td><td><code>h2 + p</code></td><td>The very next sibling, if it matches</td></tr>
  <tr><td>General sibling (<code>~</code>)</td><td><code>h2 ~ p</code></td><td>Any later sibling that matches</td></tr>
</table>

<p><strong>Descendant combinator</strong> &mdash; the most common but least specific:</p>
<pre><code>article p { color: gray; }
/* Matches any &lt;p&gt; inside &lt;article&gt;, no matter how deep */</code></pre>

<p><strong>Child combinator</strong> &mdash; only direct children:</p>
<pre><code>.menu &gt; li { background: blue; }

&lt;ul class="menu"&gt;
  &lt;li&gt;Direct (matches)&lt;/li&gt;
  &lt;li&gt;
    &lt;ul&gt;
      &lt;li&gt;Nested (does NOT match)&lt;/li&gt;
    &lt;/ul&gt;
  &lt;/li&gt;
&lt;/ul&gt;</code></pre>

<p>Useful for menus, lists, and any case where you want to style only the top level without leaking into nested children.</p>

<p><strong>Adjacent sibling combinator</strong> &mdash; the immediate following sibling:</p>
<pre><code>h2 + p {
  font-size: 1.1em;
  color: #555;
}
/* Matches a &lt;p&gt; that comes IMMEDIATELY after an &lt;h2&gt; */</code></pre>

<p>Common pattern: lead paragraphs after headings, label spacing after inputs.</p>

<p><strong>General sibling combinator</strong> &mdash; any following sibling at the same level:</p>
<pre><code>h2 ~ p {
  margin-left: 2em;
}
/* Matches every &lt;p&gt; that comes AFTER an &lt;h2&gt;, with possibly other elements between */</code></pre>

<p><strong>Real-world use case &mdash; CSS-only checkbox toggle:</strong></p>
<pre><code>&lt;input type="checkbox" id="toggle"&gt;
&lt;label for="toggle"&gt;Show details&lt;/label&gt;
&lt;div class="details"&gt;Hidden details&lt;/div&gt;

&lt;style&gt;
  .details { display: none; }

  /* When the checkbox is :checked, the sibling .details becomes visible */
  #toggle:checked ~ .details {
    display: block;
  }
&lt;/style&gt;</code></pre>

<p>The <code>~</code> combinator pairs perfectly with the <code>:checked</code> pseudo-class to make CSS-only togglable UI &mdash; no JavaScript required.</p>

<p><strong>Combining combinators</strong> &mdash; chains of relationships:</p>
<pre><code>nav &gt; ul &gt; li &gt; a {
  /* Direct chain: nav, then ul, then li, then a */
  text-transform: uppercase;
}

article h2 + p::first-line {
  /* p that is right after h2 inside article — first line of it */
  font-weight: bold;
}</code></pre>

<p><strong>Modern selectors enhance combinators:</strong></p>
<table>
  <tr><th>Selector</th><th>Purpose</th></tr>
  <tr><td><code>:has(.child)</code></td><td>Parent selector &mdash; element that contains <code>.child</code></td></tr>
  <tr><td><code>:is(a, b)</code></td><td>Match if any of multiple selectors matches</td></tr>
  <tr><td><code>:where(...)</code></td><td>Like <code>:is()</code> but specificity always 0</td></tr>
</table>

<pre><code>/* Card that contains an image */
.card:has(img) { padding: 0; }

/* Article preceded by a card */
.card:has(+ article) { margin-bottom: 2em; }

/* Match h2 OR h3 OR h4 inside article */
article :is(h2, h3, h4) { color: navy; }</code></pre>

<p><code>:has()</code> is the most powerful addition &mdash; it lets you style ancestors based on descendants, finally answering 25 years of "I wish CSS had a parent selector."</p>
'''

ANSWERS[20] = r'''
<p>The <code>z-index</code> property controls vertical stacking &mdash; which elements render in front of others when they overlap. Higher values appear on top. But it only works <em>within stacking contexts</em>, which makes the system more nuanced than "just set z-index higher."</p>

<p><strong>Basic rule:</strong> <code>z-index</code> works only on <strong>positioned elements</strong> (<code>relative</code>, <code>absolute</code>, <code>fixed</code>, <code>sticky</code>). On <code>static</code>-positioned elements, it&rsquo;s ignored.</p>

<pre><code>.overlay {
  position: fixed;       /* required for z-index */
  inset: 0;
  z-index: 1000;
}</code></pre>

<p><strong>Stacking contexts</strong> &mdash; elements form their own "stacking universe" that you can&rsquo;t escape from with z-index. A child with <code>z-index: 9999</code> can&rsquo;t pop above a sibling of the parent context.</p>

<p><strong>What creates a stacking context:</strong></p>
<ul>
  <li>The root element (<code>&lt;html&gt;</code>).</li>
  <li>Positioned elements with a non-<code>auto</code> <code>z-index</code>.</li>
  <li>Elements with <code>opacity</code> less than 1.</li>
  <li>Elements with <code>transform</code>, <code>filter</code>, <code>perspective</code>, <code>clip-path</code>, <code>mask</code>, or <code>backdrop-filter</code>.</li>
  <li>Elements with <code>isolation: isolate</code>.</li>
  <li>Flex/Grid items with <code>z-index</code> that isn&rsquo;t <code>auto</code>.</li>
  <li>Elements with <code>position: fixed</code> or <code>sticky</code>.</li>
  <li>Elements with <code>contain: paint</code> or <code>contain: layout</code>.</li>
</ul>

<p><strong>The classic confusion:</strong></p>
<pre><code>.parent {
  opacity: 0.99;     /* creates a stacking context! */
}
.parent .child {
  position: relative;
  z-index: 99999;    /* trapped inside parent's context */
}
.elsewhere {
  position: relative;
  z-index: 10;       /* will appear ABOVE .child if .parent's context is below */
}</code></pre>

<p>The child&rsquo;s <code>z-index: 99999</code> doesn&rsquo;t escape <code>.parent</code>&rsquo;s stacking context. Inside the parent, the child stacks high; relative to the rest of the page, it&rsquo;s constrained to <code>.parent</code>&rsquo;s level. This is the source of most "my modal isn&rsquo;t showing on top!" bugs.</p>

<p><strong>Stacking order within a context</strong> (back to front):</p>
<ol>
  <li>The stacking context&rsquo;s background and borders.</li>
  <li>Children with negative <code>z-index</code>, lowest first.</li>
  <li>In-flow non-positioned block-level descendants.</li>
  <li>In-flow non-positioned floats.</li>
  <li>In-flow non-positioned inline-level descendants.</li>
  <li>Positioned descendants with <code>z-index: auto</code> or <code>0</code>, in source order.</li>
  <li>Positioned descendants with positive <code>z-index</code>, lowest first.</li>
</ol>

<p><strong>The <code>isolation</code> property</strong> &mdash; explicitly create a stacking context without other side effects:</p>
<pre><code>.card {
  isolation: isolate;
  /* Creates stacking context without using transform or opacity hacks */
}</code></pre>

<p>Useful when you want to scope <code>z-index</code> values within a component without affecting the surrounding cascade.</p>

<p><strong>Stacking conventions for design systems:</strong></p>
<table>
  <tr><th>Layer</th><th>Typical z-index</th></tr>
  <tr><td>Base content</td><td>0 / auto</td></tr>
  <tr><td>Sticky header</td><td>10</td></tr>
  <tr><td>Dropdown menus</td><td>100</td></tr>
  <tr><td>Tooltip</td><td>500</td></tr>
  <tr><td>Modal overlay</td><td>1000</td></tr>
  <tr><td>Toast notifications</td><td>2000</td></tr>
</table>

<p><strong>Best practices:</strong> define a small set of named z-index tokens (CSS custom properties); avoid one-off huge values like <code>99999</code>; use cascade layers to organize component layers; use the new top layer (Popover API, native dialog) for content that should always be on top &mdash; it bypasses z-index entirely.</p>
'''

ANSWERS[21] = r'''
<p>Parallax scrolling creates depth by moving foreground and background elements at different speeds during scroll. Two approaches: pure CSS via <code>background-attachment: fixed</code>, or modern <code>scroll-driven animations</code> with full control.</p>

<p><strong>Classic background-attachment trick:</strong></p>
<pre><code>.parallax-section {
  background-image: url("/landscape.jpg");
  background-attachment: fixed;       /* the magic */
  background-size: cover;
  background-position: center;
  height: 100vh;
}</code></pre>

<p>The fixed background stays put while the foreground scrolls past, creating the illusion of depth. Simple, works in all browsers, but limited &mdash; you can&rsquo;t control the speed differential, and <code>fixed</code> backgrounds have known performance issues on mobile (they can disable hardware acceleration).</p>

<p><strong>Modern approach: scroll-driven animations</strong> (2026 baseline in Chromium; Firefox/Safari adoption progressing):</p>

<pre><code>&lt;div class="parallax-container"&gt;
  &lt;div class="parallax-bg"&gt;&lt;/div&gt;
  &lt;div class="content"&gt;Foreground content scrolling normally&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .parallax-container {
    position: relative;
    height: 100vh;
    overflow: hidden;
  }
  .parallax-bg {
    position: absolute;
    inset: 0;
    background: url("/scene.jpg") center / cover;

    /* Animate Y position as parent scrolls past */
    animation: parallax linear;
    animation-timeline: view();
    animation-range: cover;
  }

  @keyframes parallax {
    from { transform: translateY(-30%); }
    to   { transform: translateY(30%); }
  }
&lt;/style&gt;</code></pre>

<p><strong>The scroll-driven animation pieces:</strong></p>
<ul>
  <li><strong><code>animation-timeline: view()</code></strong> &mdash; binds animation progress to the element&rsquo;s position relative to the viewport (rather than time).</li>
  <li><strong><code>animation-range: cover</code></strong> &mdash; the animation runs from when the element enters viewport to when it exits.</li>
  <li><strong>The keyframes define the visual</strong> &mdash; transform from -30% to 30% as scroll progresses.</li>
</ul>

<p><strong>Other scroll-timeline keywords:</strong></p>
<table>
  <tr><th>Value</th><th>Trigger</th></tr>
  <tr><td><code>view()</code></td><td>Element enters/exits viewport</td></tr>
  <tr><td><code>scroll()</code></td><td>Container scroll position</td></tr>
  <tr><td><code>scroll(root)</code></td><td>Root document scroll</td></tr>
</table>

<p><strong>JavaScript fallback</strong> for older browsers (or finer control):</p>
<pre><code>const bg = document.querySelector(".parallax-bg");
const container = document.querySelector(".parallax-container");

window.addEventListener("scroll", () =&gt; {
  const rect = container.getBoundingClientRect();
  const speed = 0.5;
  bg.style.transform = `translateY(${rect.top * speed}px)`;
}, { passive: true });</code></pre>

<p><strong>Performance considerations:</strong></p>
<ul>
  <li><strong>Animate <code>transform</code> only</strong> &mdash; GPU-accelerated, won&rsquo;t cause layout thrashing.</li>
  <li><strong>Use <code>will-change: transform</code></strong> on parallax elements to hint the browser to optimize the layer.</li>
  <li><strong>Throttle scroll listeners</strong> with <code>requestAnimationFrame</code> &mdash; native scroll fires at 60+fps and can overwhelm slower JS.</li>
  <li><strong>Test on mobile</strong> &mdash; many parallax effects feel laggy or break iOS&rsquo;s natural rubber-banding scroll.</li>
</ul>

<p><strong>Accessibility</strong> &mdash; respect <code>prefers-reduced-motion</code>:</p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  .parallax-bg {
    animation: none;
    transform: none;
  }
}</code></pre>

<p>Parallax can trigger nausea for users with vestibular disorders. Always provide a non-animated fallback. For critical content, ensure the parallax is decorative only &mdash; nothing important should depend on the motion to be understood.</p>
'''

ANSWERS[22] = r'''
<p>The <code>calc()</code> function performs math in CSS values &mdash; mixing units (e.g. percent + pixels), referencing custom properties, computing widths against viewport sizes. It&rsquo;s essential for layouts that don&rsquo;t fit cleanly into a single unit system.</p>

<pre><code>.sidebar {
  /* Full viewport height minus the header */
  height: calc(100vh - 60px);
}

.column {
  /* Full width minus margins */
  width: calc(100% - 2em);
}

.image {
  /* Container width minus padding, capped at 800px */
  max-width: calc(100% - 4em);
}</code></pre>

<p><strong>Operators:</strong></p>
<table>
  <tr><th>Op</th><th>Notes</th></tr>
  <tr><td><code>+</code></td><td>Addition (requires spaces around it)</td></tr>
  <tr><td><code>-</code></td><td>Subtraction (requires spaces around it)</td></tr>
  <tr><td><code>*</code></td><td>Multiplication (one side must be unitless)</td></tr>
  <tr><td><code>/</code></td><td>Division (right side must be unitless)</td></tr>
</table>

<p><strong>Whitespace matters</strong> for <code>+</code> and <code>-</code>:</p>
<pre><code>width: calc(100% - 20px);   /* CORRECT */
width: calc(100%-20px);     /* WRONG — parsed as a single value */
width: calc(100% -20px);    /* WRONG — parsed as 100% then -20px (invalid) */</code></pre>

<p><strong>Mixing units</strong> &mdash; the original superpower:</p>
<pre><code>.responsive-text {
  font-size: calc(1rem + 0.5vw);
  /* Base 1rem, scales slightly with viewport */
}

.gutter {
  margin-left: calc(50% - 600px);
  /* Centers a 1200px container without container queries */
}</code></pre>

<p><strong>Custom properties + calc()</strong> &mdash; design system math:</p>
<pre><code>:root {
  --base: 0.5rem;
}
.padded { padding: calc(var(--base) * 2); }   /* 1rem */
.spaced { margin: calc(var(--base) * 4); }    /* 2rem */</code></pre>

<p>Centralize a base spacing unit; multiply for spacing scales. This is essentially how Tailwind&rsquo;s spacing system works.</p>

<p><strong>Modern math functions</strong> (2026 baseline) extend <code>calc()</code>:</p>
<table>
  <tr><th>Function</th><th>Returns</th></tr>
  <tr><td><code>min(a, b, ...)</code></td><td>Smallest value</td></tr>
  <tr><td><code>max(a, b, ...)</code></td><td>Largest value</td></tr>
  <tr><td><code>clamp(min, val, max)</code></td><td>Value bounded by min and max</td></tr>
  <tr><td><code>round(...)</code></td><td>Rounding</td></tr>
  <tr><td><code>mod(...)</code></td><td>Modulo</td></tr>
  <tr><td><code>abs(...)</code></td><td>Absolute value</td></tr>
</table>

<p><strong>Fluid typography with <code>clamp()</code>:</strong></p>
<pre><code>h1 {
  font-size: clamp(1.5rem, 4vw + 1rem, 3.5rem);
  /* min: 1.5rem, scales with viewport, max: 3.5rem */
}</code></pre>

<p><code>clamp()</code> in one line replaces multiple media queries for typography. Reads almost like English: "minimum X, ideally Y, never more than Z."</p>

<p><strong>Responsive container with <code>min()</code>:</strong></p>
<pre><code>.container {
  width: min(100%, 1200px);
  margin: 0 auto;
  /* Full width on mobile; capped at 1200px on desktop */
}

.section {
  padding-inline: max(1rem, 5%);
  /* At least 1rem padding; 5% on wider screens */
}</code></pre>

<p>These functions feel like having a tiny CSS layout solver. They eliminate huge classes of media queries.</p>

<p><strong>Browser computes at runtime</strong> &mdash; <code>calc()</code> values resolve when the browser computes layout, so percentages refer to the parent at that moment. Computed values change responsively as the parent resizes.</p>

<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>Forgetting whitespace</strong> around <code>+</code> and <code>-</code> &mdash; the most common bug.</li>
  <li><strong>Dividing by units</strong> &mdash; the divisor must be unitless. <code>calc(100px / 2px)</code> is invalid.</li>
  <li><strong>Browser fallbacks</strong> &mdash; <code>calc()</code> is universally supported in 2026, but always have a fallback for unknown contexts: <code>width: 100%;  width: calc(100% - 1em);</code>.</li>
</ul>
'''

ANSWERS[23] = r'''
<p>The canonical responsive image gallery uses CSS Grid with <code>auto-fit</code> + <code>minmax()</code> &mdash; cards reflow naturally as the viewport changes, no media queries required. Combine with <code>object-fit</code> for consistent image sizing.</p>

<pre><code>&lt;section class="gallery"&gt;
  &lt;figure&gt;
    &lt;img src="img1.jpg" alt="..." loading="lazy"&gt;
    &lt;figcaption&gt;Forest path&lt;/figcaption&gt;
  &lt;/figure&gt;
  &lt;figure&gt;
    &lt;img src="img2.jpg" alt="..." loading="lazy"&gt;
    &lt;figcaption&gt;Mountain peak&lt;/figcaption&gt;
  &lt;/figure&gt;
  &lt;!-- ... more figures --&gt;
&lt;/section&gt;

&lt;style&gt;
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }
  .gallery figure {
    margin: 0;
    overflow: hidden;
    border-radius: 8px;
    background: #f0f0f0;
  }
  .gallery img {
    width: 100%;
    aspect-ratio: 4 / 3;             /* preserve consistent shape */
    object-fit: cover;                /* fill, crop if needed */
    display: block;
    transition: transform 0.3s;
  }
  .gallery figure:hover img {
    transform: scale(1.05);
  }
  .gallery figcaption {
    padding: 0.5em;
    font-size: 0.9em;
    color: #555;
  }
&lt;/style&gt;</code></pre>

<p><strong>How it adapts:</strong></p>
<ul>
  <li><strong>Wide screens:</strong> 4-5 columns side by side.</li>
  <li><strong>Tablets:</strong> 2-3 columns.</li>
  <li><strong>Phones:</strong> 1-2 columns.</li>
  <li>The browser computes columns based on container width, not viewport &mdash; so it works inside any container, including sidebars.</li>
</ul>

<p><strong>Aspect-ratio + object-fit</strong> &mdash; the modern combo:</p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>aspect-ratio: 4 / 3</code></td><td>Box maintains 4:3 shape regardless of width</td></tr>
  <tr><td><code>object-fit: cover</code></td><td>Image fills the box, cropping if necessary</td></tr>
  <tr><td><code>object-fit: contain</code></td><td>Image fits inside the box, may letterbox</td></tr>
  <tr><td><code>object-position: center</code></td><td>Where the image aligns when cropped</td></tr>
</table>

<p><strong>Masonry-like layout with varying heights</strong> &mdash; using <code>grid-row: span N</code> based on image aspect ratio:</p>
<pre><code>.masonry {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  grid-auto-rows: 10px;
  gap: 1rem;
}
.masonry figure {
  /* Each figure spans rows based on its content height */
  grid-row: span 30;     /* approximate; varies per item */
}
.masonry figure.tall {
  grid-row: span 50;
}</code></pre>

<p>For true masonry layout where items pack tightly, <strong>CSS native masonry</strong> is shipping in 2026 (well-supported in Chromium and Safari):</p>

<pre><code>.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  grid-template-rows: masonry;        /* Pinterest-style packing */
  gap: 1rem;
}</code></pre>

<p>Without this, third-party libraries like Masonry.js are required for tight packing. Native masonry eliminates the need.</p>

<p><strong>Performance optimizations:</strong></p>
<ul>
  <li><strong><code>loading="lazy"</code></strong> on <code>&lt;img&gt;</code> &mdash; defers loading until the image approaches the viewport.</li>
  <li><strong><code>srcset</code></strong> with multiple resolutions &mdash; phones don&rsquo;t download desktop-sized images.</li>
  <li><strong>Modern formats (AVIF, WebP)</strong> with <code>&lt;picture&gt;</code> + <code>&lt;source type&gt;</code> &mdash; 30-70% bandwidth savings.</li>
  <li><strong>Set <code>width</code> and <code>height</code> attributes</strong> on the HTML &mdash; reserves space, prevents layout shift (CLS).</li>
  <li><strong>Use <code>fetchpriority="high"</code></strong> on the LCP image (first visible image).</li>
</ul>

<p>For lightbox/zoom on click, libraries like PhotoSwipe or YooSlide handle pinch-zoom and swipe gestures. The pure-CSS gallery handles the layout perfectly; the lightbox is a separate concern.</p>
'''

ANSWERS[24] = r'''
<p>The <code>:nth-child()</code> pseudo-class selects elements based on their position among siblings, using a formula. It&rsquo;s one of CSS&rsquo;s most powerful selectors for patterned styling.</p>

<pre><code>li:nth-child(1)  { /* first child */ }
li:nth-child(3)  { /* third child */ }
li:nth-child(odd)  { background: #f5f5f5; }    /* 1, 3, 5, ... */
li:nth-child(even) { background: white; }      /* 2, 4, 6, ... */

li:nth-child(3n)   { color: red; }             /* every 3rd: 3, 6, 9, ... */
li:nth-child(3n+1) { color: blue; }            /* 1st, 4th, 7th, ... */
li:nth-child(-n+3) { font-weight: bold; }      /* first 3 elements */
li:nth-child(n+5)  { color: green; }           /* 5th onward */</code></pre>

<p><strong>The formula <code>an+b</code></strong> means: starting at <code>b</code>, increment by <code>a</code>. The browser computes <code>n</code> = 0, 1, 2, ... and matches elements at the resulting positions.</p>

<table>
  <tr><th>Formula</th><th>Matches</th></tr>
  <tr><td><code>2n</code> or <code>even</code></td><td>2, 4, 6, ...</td></tr>
  <tr><td><code>2n+1</code> or <code>odd</code></td><td>1, 3, 5, ...</td></tr>
  <tr><td><code>3n</code></td><td>3, 6, 9, ...</td></tr>
  <tr><td><code>3n+1</code></td><td>1, 4, 7, ...</td></tr>
  <tr><td><code>-n+3</code></td><td>3, 2, 1 (first 3)</td></tr>
  <tr><td><code>n+4</code></td><td>4, 5, 6, ... (4th onward)</td></tr>
</table>

<p><strong><code>:nth-child</code> vs <code>:nth-of-type</code></strong> &mdash; the critical distinction:</p>

<pre><code>&lt;article&gt;
  &lt;h2&gt;Title&lt;/h2&gt;
  &lt;p&gt;First paragraph&lt;/p&gt;
  &lt;p&gt;Second paragraph&lt;/p&gt;
  &lt;p&gt;Third paragraph&lt;/p&gt;
&lt;/article&gt;

p:nth-child(2) {
  /* Counts ALL siblings — matches the FIRST &lt;p&gt;, which is child 2 */
}

p:nth-of-type(2) {
  /* Counts only &lt;p&gt; siblings — matches the SECOND &lt;p&gt;, which is child 3 */
}</code></pre>

<p><strong>Reverse counting</strong> &mdash; counted from the end:</p>
<pre><code>li:nth-last-child(1)   { /* last child */ }
li:nth-last-child(2)   { /* second from end */ }
li:nth-last-child(-n+3) { /* last 3 children */ }</code></pre>

<p><strong>Modern <code>:nth-child(... of selector)</code></strong> (2026 well-supported) &mdash; filter siblings before counting:</p>
<pre><code>&lt;ul&gt;
  &lt;li class="active"&gt;A&lt;/li&gt;
  &lt;li&gt;B&lt;/li&gt;
  &lt;li class="active"&gt;C&lt;/li&gt;
  &lt;li class="active"&gt;D&lt;/li&gt;
&lt;/ul&gt;

li:nth-child(2 of .active) {
  /* Selects the SECOND li that has class "active" — matches C */
  color: red;
}</code></pre>

<p>This is hugely powerful &mdash; previously you could only count among all siblings, ignoring filters.</p>

<p><strong>Real-world patterns:</strong></p>
<pre><code>/* Zebra-striped table */
tbody tr:nth-child(odd) { background: #f9f9f9; }

/* Grid with bordered rows of 3 */
.card-grid &gt; *:nth-child(3n) {
  margin-right: 0;       /* remove right margin on every 3rd card */
}

/* First 3 list items get a special border */
li:nth-child(-n+3) {
  border-left: 4px solid #0066cc;
}

/* Skip the first item */
li:not(:first-child) {
  border-top: 1px solid #eee;
}

/* Items with even position among visible (modern) */
li:not([hidden]):nth-child(even of :not([hidden])) {
  background: #f5f5f5;
}</code></pre>

<p><strong>Performance:</strong> nth-child selectors are O(n) per element &mdash; the browser scans siblings to compute positions. For very large lists (1000+ items), be mindful in performance-critical CSS. For typical UI sizes, the cost is negligible.</p>

<p><strong>Common idioms with <code>:not</code> + nth-child:</strong></p>
<pre><code>li:not(:last-child) { border-bottom: 1px solid #eee; }
.menu li:not(:first-child) { margin-top: 0.5em; }</code></pre>
'''

ANSWERS[25] = r'''
<p>This question continues the previous one on <code>:nth-child()</code> &mdash; the source data has the question text split across Q24-25. This entry covers <strong><code>:nth-of-type()</code></strong> as the natural counterpart, plus practical examples of when to choose which.</p>

<p><strong><code>:nth-of-type()</code> counts only siblings of the same element type</strong>, ignoring different-type siblings. Compare:</p>

<pre><code>&lt;section&gt;
  &lt;h2&gt;Heading&lt;/h2&gt;
  &lt;p&gt;Paragraph 1&lt;/p&gt;     &lt;!-- 1st &lt;p&gt;, 2nd child overall --&gt;
  &lt;p&gt;Paragraph 2&lt;/p&gt;     &lt;!-- 2nd &lt;p&gt;, 3rd child overall --&gt;
  &lt;p&gt;Paragraph 3&lt;/p&gt;     &lt;!-- 3rd &lt;p&gt;, 4th child overall --&gt;
&lt;/section&gt;

p:nth-child(2) {
  /* Counts ALL siblings — matches the 1st &lt;p&gt; (because it's the 2nd child overall) */
  font-weight: bold;
}

p:nth-of-type(2) {
  /* Counts only &lt;p&gt; — matches the 2nd &lt;p&gt; */
  font-weight: bold;
}</code></pre>

<p><strong>Decision matrix &mdash; which to use:</strong></p>
<table>
  <tr><th>Case</th><th>Use</th></tr>
  <tr><td>Striping a table&rsquo;s rows (homogeneous)</td><td><code>:nth-child(odd)</code></td></tr>
  <tr><td>Styling article paragraphs (mixed siblings)</td><td><code>:nth-of-type(N)</code></td></tr>
  <tr><td>First child overall</td><td><code>:first-child</code></td></tr>
  <tr><td>First of a specific type</td><td><code>:first-of-type</code></td></tr>
  <tr><td>The Nth filtered result</td><td><code>:nth-child(N of .filter)</code> (2026)</td></tr>
</table>

<p><strong>Practical patterns where <code>:nth-of-type</code> shines:</strong></p>
<pre><code>/* Drop cap only on the first paragraph of an article */
article p:first-of-type::first-letter {
  font-size: 3em;
  float: left;
  font-family: Georgia, serif;
  margin-right: 0.1em;
}

/* Different padding on the first &lt;img&gt; in a gallery */
.gallery img:first-of-type {
  border: 3px solid gold;     /* highlight the cover photo */
}

/* Indent every other &lt;blockquote&gt; */
blockquote:nth-of-type(even) {
  margin-left: 4em;
}

/* Style the second &lt;h3&gt; specially */
article h3:nth-of-type(2) {
  border-top: 2px solid red;
}</code></pre>

<p><strong>Modern alternatives</strong> when type-counting feels awkward:</p>

<p><strong>1. <code>:has()</code> for context-aware styling:</strong></p>
<pre><code>article p:has(+ p) {
  /* Paragraphs followed by another paragraph */
  margin-bottom: 1em;
}

article p:not(:has(+ p)) {
  /* Last paragraph in a sequence */
  margin-bottom: 2em;
}</code></pre>

<p><strong>2. <code>:nth-child(N of selector)</code></strong> for filtered counting:</p>
<pre><code>li:nth-child(odd of .visible) {
  /* Only counts among visible items */
  background: #f5f5f5;
}</code></pre>

<p>The <code>of selector</code> syntax (2026 baseline) eliminates many cases where you previously had to use <code>:nth-of-type</code>.</p>

<p><strong>Specificity</strong> of these selectors:</p>
<table>
  <tr><th>Selector</th><th>Specificity</th></tr>
  <tr><td><code>:nth-child(2)</code></td><td>(0,0,1,0) &mdash; class-level</td></tr>
  <tr><td><code>:nth-of-type(2)</code></td><td>(0,0,1,0) &mdash; class-level</td></tr>
  <tr><td><code>p:nth-child(2)</code></td><td>(0,0,1,1) &mdash; class + element</td></tr>
  <tr><td><code>:first-child</code></td><td>(0,0,1,0)</td></tr>
</table>

<p><strong>Avoid using nth selectors for state.</strong> They&rsquo;re position-based, not state-based. If a list item should be highlighted because the user clicked it, use a class (<code>.active</code>), not <code>:nth-child(3)</code> &mdash; the position changes with sorting, filtering, or content updates, but the class persists.</p>
'''

ANSWERS[26] = r'''
<p>The <code>clip-path</code> property crops elements to custom shapes &mdash; circles, polygons, complex paths, even SVG references. Unlike <code>overflow: hidden</code> (which only clips to the box), <code>clip-path</code> can produce arbitrary geometry.</p>

<p><strong>Built-in shape functions:</strong></p>
<pre><code>.circle    { clip-path: circle(50%); }
.ellipse   { clip-path: ellipse(40% 25% at center); }
.rect      { clip-path: inset(10px 20px 30px 40px round 10px); }
.diamond   { clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); }
.triangle  { clip-path: polygon(50% 0%, 0% 100%, 100% 100%); }
.hexagon   { clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }
.chevron   { clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%); }</code></pre>

<p><strong>Polygon coordinates</strong> are pairs of <code>x y</code> percentages or lengths. <code>0% 0%</code> is top-left; <code>100% 100%</code> is bottom-right. Each pair defines a vertex of the polygon, traced in order.</p>

<table>
  <tr><th>Function</th><th>Purpose</th></tr>
  <tr><td><code>circle(radius at x y)</code></td><td>Circular crop</td></tr>
  <tr><td><code>ellipse(rx ry at x y)</code></td><td>Elliptical crop</td></tr>
  <tr><td><code>inset(top right bottom left round R)</code></td><td>Rectangular inset with optional rounded corners</td></tr>
  <tr><td><code>polygon(...)</code></td><td>Any straight-sided shape</td></tr>
  <tr><td><code>path("...")</code></td><td>SVG path data &mdash; arbitrary curves</td></tr>
  <tr><td><code>shape(...)</code></td><td>Higher-level shape syntax (2026 modern)</td></tr>
</table>

<p><strong>Animated reveals</strong> using <code>clip-path</code>:</p>
<pre><code>.reveal-on-hover {
  background: url("photo.jpg");
  width: 400px;
  height: 300px;
  clip-path: circle(20% at 30% 70%);
  transition: clip-path 0.5s ease;
}
.reveal-on-hover:hover {
  clip-path: circle(75% at 50% 50%);     /* expand to reveal */
}</code></pre>

<p>Animating between shapes works smoothly when both shapes have the same <strong>number of points</strong>. <code>circle()</code> &harr; <code>circle()</code> animates beautifully; <code>polygon(3 points)</code> &harr; <code>polygon(5 points)</code> doesn&rsquo;t interpolate cleanly.</p>

<p><strong>Complex path with SVG</strong> for irregular shapes:</p>
<pre><code>.blob {
  clip-path: path("M 50,0 C 80,0 100,30 100,60 C 100,90 70,100 40,90 C 10,80 0,40 20,20 Z");
  /* SVG path data — curves with control points */
}</code></pre>

<p>Use a tool like Clippy (bennettfeely.com/clippy) for visual editing &mdash; designing polygons by hand is error-prone.</p>

<p><strong>Reference an SVG element</strong> &mdash; ultimate control:</p>
<pre><code>&lt;svg width="0" height="0"&gt;
  &lt;defs&gt;
    &lt;clipPath id="my-shape"&gt;
      &lt;path d="M 0,0 L 100,0 L 100,100 L 0,100 Z"/&gt;
    &lt;/clipPath&gt;
  &lt;/defs&gt;
&lt;/svg&gt;

&lt;style&gt;
  .clipped { clip-path: url(#my-shape); }
&lt;/style&gt;</code></pre>

<p><strong>Modern <code>shape()</code> function</strong> (2026 in Chromium): more readable than polygon coordinates:</p>
<pre><code>.fancy {
  clip-path: shape(
    from 0 0,
    line to 100% 0,
    arc to 100% 100% of 50% cw,
    line to 0 100%,
    close
  );
}</code></pre>

<p><strong>Performance:</strong> <code>clip-path</code> creates a new stacking context. Animating it triggers GPU compositing. Use <code>will-change: clip-path</code> sparingly &mdash; only when you know an element will animate.</p>

<p><strong>Fallback:</strong> browsers without <code>clip-path</code> support display the unclipped element. Use <code>@supports (clip-path: circle())</code> to feature-detect and provide a fallback if the unclipped state would be ugly.</p>

<p>Common uses: avatar circles, content angles/diagonals, image cutouts that interact with surrounding text, decorative shapes (hexagons, ribbons, chevrons), animated reveal effects.</p>
'''

ANSWERS[27] = r'''
<p>CSS transitions interpolate property changes over time, triggered by state changes (hover, focus, class toggles). They&rsquo;re the simplest way to add motion &mdash; one line on the base, change the property, the browser smoothly animates between states.</p>

<pre><code>.btn {
  background: #0066cc;
  transform: translateY(0);
  transition: background 0.3s ease, transform 0.2s ease;
}
.btn:hover {
  background: #004999;
  transform: translateY(-2px);
}</code></pre>

<p><strong>The four transition properties:</strong></p>
<table>
  <tr><th>Property</th><th>Purpose</th><th>Default</th></tr>
  <tr><td><code>transition-property</code></td><td>Which properties to animate (or <code>all</code>)</td><td><code>all</code></td></tr>
  <tr><td><code>transition-duration</code></td><td>How long the transition takes</td><td><code>0s</code></td></tr>
  <tr><td><code>transition-timing-function</code></td><td>The easing curve</td><td><code>ease</code></td></tr>
  <tr><td><code>transition-delay</code></td><td>Wait time before starting</td><td><code>0s</code></td></tr>
</table>

<p><strong>The shorthand:</strong> <code>transition: property duration timing-function delay</code>.</p>

<pre><code>.element {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
  /* property duration timing delay */
}</code></pre>

<p><strong>Multiple properties &mdash; comma-separated:</strong></p>
<pre><code>.card {
  transition:
    transform 0.2s ease-out,
    box-shadow 0.3s ease,
    background 0.4s linear;
}</code></pre>

<p>Each property gets its own timing &mdash; they animate independently and concurrently.</p>

<p><strong>Timing functions &mdash; the curve that shapes the motion:</strong></p>
<table>
  <tr><th>Function</th><th>Feel</th></tr>
  <tr><td><code>linear</code></td><td>Constant speed (mechanical)</td></tr>
  <tr><td><code>ease</code></td><td>Slow start, fast middle, slow end (default)</td></tr>
  <tr><td><code>ease-in</code></td><td>Slow start; accelerates</td></tr>
  <tr><td><code>ease-out</code></td><td>Fast start; decelerates (most natural for UI)</td></tr>
  <tr><td><code>ease-in-out</code></td><td>Slow start AND end</td></tr>
  <tr><td><code>cubic-bezier(...)</code></td><td>Custom curve (use cubic-bezier.com)</td></tr>
  <tr><td><code>steps(N, start|end)</code></td><td>Discrete jumps (no smooth interpolation)</td></tr>
</table>

<p><strong>For UI feedback, <code>ease-out</code> usually feels best</strong> &mdash; quick to start (responds to action), gentle landing. Material Design&rsquo;s <code>cubic-bezier(0.4, 0, 0.2, 1)</code> is a popular variant.</p>

<p><strong>Apply transition to the BASE selector,</strong> not the hover state:</p>
<pre><code>/* CORRECT: animates both directions */
.btn { transition: background 0.3s; }
.btn:hover { background: red; }

/* WRONG: only animates entering hover, snaps back instantly */
.btn:hover { background: red; transition: background 0.3s; }</code></pre>

<p><strong>Properties that DON&rsquo;T transition</strong> (without special handling):</p>
<ul>
  <li><code>display</code> &mdash; can&rsquo;t transition between <code>none</code> and others (modern <code>display</code>: animatable with <code>transition-behavior: allow-discrete</code>).</li>
  <li><code>height: auto</code> &mdash; can&rsquo;t animate to/from auto without <code>interpolate-size</code> (2024+).</li>
  <li>Custom properties without <code>@property</code> registration.</li>
</ul>

<p><strong>Modern <code>@starting-style</code></strong> (2026) for entrance animations:</p>
<pre><code>.modal {
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.3s, transform 0.3s;

  @starting-style {
    opacity: 0;
    transform: scale(0.9);
  }
}
/* When the element is added to DOM, it starts at the @starting-style values
   and transitions to its actual values */</code></pre>

<p>Eliminates the JavaScript dance of "add element, force layout, add open class" &mdash; transitions on insertion just work.</p>

<p><strong>Performance:</strong> stick to <code>transform</code> and <code>opacity</code> for 60fps animation. Animating <code>width</code>, <code>height</code>, <code>top</code>, etc. triggers layout recalculation on every frame &mdash; expensive on complex pages. Always test on mid-tier mobile devices.</p>

<p><strong>Accessibility:</strong> respect <code>prefers-reduced-motion</code> by zeroing out transition durations for users who&rsquo;ve opted out.</p>
'''

ANSWERS[28] = r'''
<p>CSS custom properties make theming trivially easy &mdash; define theme values as variables, swap them with a single attribute or class change. Since variables cascade and inherit, one override at any DOM level updates everything below.</p>

<pre><code>:root {
  /* Light theme (default) */
  --color-bg:        #ffffff;
  --color-fg:        #1a1a1a;
  --color-primary:   #0066cc;
  --color-secondary: #ff6b35;
  --color-border:    #e0e0e0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
  --color-bg:        #1a1a1a;
  --color-fg:        #f0f0f0;
  --color-primary:   #4a90e2;
  --color-secondary: #ff8c42;
  --color-border:    #333333;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
}

body {
  background: var(--color-bg);
  color: var(--color-fg);
  transition: background 0.2s, color 0.2s;
}</code></pre>

<p><strong>Toggle theme via JavaScript:</strong></p>
<pre><code>function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("theme", theme);
}

// Restore on page load
const saved = localStorage.getItem("theme");
if (saved) setTheme(saved);

// Toggle
document.getElementById("toggle").addEventListener("click", () =&gt; {
  const current = document.documentElement.dataset.theme;
  setTheme(current === "dark" ? "light" : "dark");
});</code></pre>

<p><strong>Respect OS preference automatically:</strong></p>
<pre><code>@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    /* Apply dark theme by default if user hasn't manually chosen */
    --color-bg:  #1a1a1a;
    --color-fg:  #f0f0f0;
    /* ... */
  }
}</code></pre>

<p>Combined approach: respect OS preference, but allow user override that takes precedence and persists in localStorage.</p>

<p><strong>Multi-theme system</strong> &mdash; not just light/dark:</p>
<pre><code>[data-theme="default"] { --primary: #0066cc; --accent: #ff6b35; }
[data-theme="forest"]  { --primary: #2e7d32; --accent: #f57c00; }
[data-theme="ocean"]   { --primary: #0277bd; --accent: #00838f; }
[data-theme="sunset"]  { --primary: #c62828; --accent: #f57f17; }</code></pre>

<p><strong>Component-scoped overrides</strong> &mdash; not just root-level:</p>
<pre><code>.cta-section {
  --color-bg: #ff6b35;
  --color-fg: white;
  /* Children of .cta-section see overridden values */
}

.cta-section .btn {
  background: var(--color-bg);   /* uses override */
  color: var(--color-fg);
}</code></pre>

<p>Powerful pattern: define a button component using variables, then swap palettes by overriding variables at parent level. The button never changes its CSS.</p>

<p><strong>Modern color manipulation with <code>color-mix()</code></strong> (2026 baseline):</p>
<pre><code>:root {
  --primary: oklch(0.55 0.18 250);    /* base color */

  /* Generate variants programmatically */
  --primary-light: color-mix(in oklch, var(--primary) 70%, white);
  --primary-dark:  color-mix(in oklch, var(--primary) 70%, black);
  --primary-fade:  color-mix(in oklch, var(--primary) 30%, transparent);
}</code></pre>

<p><code>color-mix()</code> generates color variants from a single base color &mdash; the design system has one knob; tints/shades are derived. Sass functions like <code>lighten()</code> are no longer needed.</p>

<p><strong>Typed properties with <code>@property</code></strong> for animatable theme values:</p>
<pre><code>@property --gradient-angle {
  syntax: "&lt;angle&gt;";
  inherits: false;
  initial-value: 45deg;
}

[data-theme="default"] { --gradient-angle: 45deg; }
[data-theme="dark"]    { --gradient-angle: 135deg; }

.hero {
  background: linear-gradient(var(--gradient-angle), red, blue);
  transition: --gradient-angle 0.5s;   /* now animates between themes */
}</code></pre>

<p>Without <code>@property</code>, the angle would jump between themes. Registering it as typed unlocks smooth animation.</p>

<p><strong>Best practices:</strong> centralize tokens in <code>:root</code>; name semantically (<code>--color-success</code>, not <code>--green</code>); add a <code>transition</code> on body for smooth theme swaps; persist preference in localStorage; respect OS preference as a sensible default.</p>
'''

ANSWERS[29] = r'''
<p>The <code>@supports</code> rule is a feature query &mdash; it lets you apply CSS only if the browser supports a specific property/value combination. It&rsquo;s the CSS-side counterpart to JavaScript&rsquo;s <code>"feature" in window</code>.</p>

<pre><code>/* Apply only if 'display: grid' is supported */
@supports (display: grid) {
  .layout {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Apply only if NOT supported */
@supports not (display: grid) {
  .layout {
    display: flex;
    flex-wrap: wrap;
  }
}</code></pre>

<p><strong>Why this matters:</strong> CSS rules with unsupported properties are silently ignored. Without <code>@supports</code>, you can&rsquo;t reliably know whether your fancy CSS worked or fell back. Feature queries make graceful enhancement explicit.</p>

<p><strong>Combining conditions:</strong></p>
<pre><code>/* All must support */
@supports (display: grid) and (gap: 1em) {
  .grid { display: grid; gap: 1em; }
}

/* Either supported */
@supports (display: grid) or (display: flex) {
  /* CSS for any modern layout */
}

/* Negation */
@supports not (-webkit-touch-callout: none) {
  /* Not iOS Safari */
}</code></pre>

<p><strong>Common feature-detection patterns:</strong></p>

<p><strong>1. Container queries fallback:</strong></p>
<pre><code>.card { /* baseline using viewport queries */ }

@media (min-width: 768px) {
  .card { display: grid; }
}

/* Override with container queries if supported */
@supports (container-type: inline-size) {
  .card-wrapper { container-type: inline-size; }

  @container (min-width: 400px) {
    .card { display: grid; }
  }
}</code></pre>

<p><strong>2. <code>:has()</code> selector fallback:</strong></p>
<pre><code>.card.has-image { padding: 0; }   /* class added by JS */

@supports selector(:has(*)) {
  /* Modern browsers — use the native selector */
  .card:has(img) { padding: 0; }
}</code></pre>

<p>The <code>selector()</code> function inside <code>@supports</code> tests selector support, not just property/value support. Available since 2022; useful for newer selectors like <code>:has()</code>.</p>

<p><strong>3. Modern color formats:</strong></p>
<pre><code>.box {
  background: rgb(255, 100, 0);             /* fallback */
}

@supports (background: oklch(0.6 0.2 30)) {
  .box {
    background: oklch(0.6 0.2 30);          /* perceptually uniform */
  }
}</code></pre>

<p><strong>4. CSS custom properties:</strong></p>
<pre><code>.btn {
  background: blue;        /* fallback */
}

@supports (--custom: value) {
  /* Browsers with custom properties */
  :root { --primary: #0066cc; }
  .btn { background: var(--primary); }
}</code></pre>

<p><strong>The relationship between <code>@supports</code> and graceful degradation:</strong></p>
<ul>
  <li><strong>Without <code>@supports</code></strong>: write fallback CSS first, then the modern version after &mdash; later rules override if supported. Fragile when the browser parses unknown values.</li>
  <li><strong>With <code>@supports</code></strong>: explicit. Old browsers see baseline; modern browsers see enhancements. Self-documenting which features matter.</li>
</ul>

<p><strong>Modern alternative for sourcery: try-catch in CSS isn&rsquo;t a thing.</strong> But you can use <code>@supports</code> to layer enhancements:</p>
<pre><code>/* Layer 1: baseline (works everywhere) */
.gallery {
  display: flex;
  flex-wrap: wrap;
}

/* Layer 2: Grid replaces Flexbox if available */
@supports (display: grid) {
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* Layer 3: subgrid for nested grids */
@supports (grid-template-rows: subgrid) {
  .gallery .nested-grid {
    grid-template-rows: subgrid;
  }
}</code></pre>

<p>Each layer enhances; each unsupported layer falls back to the previous tier. Production-grade graceful enhancement.</p>

<p><strong>JavaScript counterpart:</strong> <code>CSS.supports(property, value)</code> tests the same thing imperatively. Useful when you need to make decisions in script based on CSS capability.</p>

<pre><code>if (CSS.supports("display", "grid")) {
  // ... use Grid features
}</code></pre>
'''

ANSWERS[30] = r'''
<p>Three CSS techniques produce a full-screen background image &mdash; <code>background-size: cover</code> on body, fixed-position overlays, or modern viewport units. Each handles edge cases like browser chrome and scrolling differently.</p>

<p><strong>Method 1: <code>background-size: cover</code> on body</strong> (simplest):</p>
<pre><code>body {
  background-image: url("/hero.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;     /* keep position during scroll */
  min-height: 100vh;
  margin: 0;
}</code></pre>

<p><code>cover</code> scales the image to fill the box without distorting, cropping if needed. <code>center</code> keeps important parts visible.</p>

<p><strong>Method 2: Fixed-position overlay</strong> (more flexible):</p>
<pre><code>&lt;div class="bg-image"&gt;&lt;/div&gt;
&lt;main&gt;Scrolls over the background&lt;/main&gt;

&lt;style&gt;
  .bg-image {
    position: fixed;
    inset: 0;                       /* top/right/bottom/left: 0 */
    z-index: -1;
    background: url("/hero.jpg") center / cover no-repeat;
  }
&lt;/style&gt;</code></pre>

<p>The fixed div sits behind everything (negative <code>z-index</code>); main content scrolls over it &mdash; creating the illusion of a static background. More control than <code>background-attachment: fixed</code> and better mobile performance.</p>

<p><strong>Method 3: Hero section with viewport units</strong>:</p>
<pre><code>.hero {
  height: 100vh;                     /* full viewport height */
  background:
    linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
    url("/hero.jpg") center / cover;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}</code></pre>

<p>The dark gradient overlay ensures text legibility regardless of the photo. Stacking gradients over images is the canonical "hero with text" pattern.</p>

<p><strong>The mobile <code>vh</code> issue</strong> &mdash; iOS Safari&rsquo;s URL bar shows/hides on scroll, changing viewport height. <code>100vh</code> can cause unwanted gaps:</p>

<table>
  <tr><th>Unit</th><th>Refers to</th></tr>
  <tr><td><code>vh</code></td><td>Largest possible viewport height (excludes browser chrome)</td></tr>
  <tr><td><code>svh</code></td><td>Smallest viewport height (with chrome visible)</td></tr>
  <tr><td><code>lvh</code></td><td>Largest viewport height (chrome hidden)</td></tr>
  <tr><td><code>dvh</code></td><td>Dynamic viewport height (changes with chrome)</td></tr>
</table>

<pre><code>.hero {
  /* Better than 100vh on mobile */
  min-height: 100dvh;            /* changes smoothly as chrome hides */
}

/* Or fall back gracefully */
.hero {
  min-height: 100vh;
  min-height: 100dvh;            /* preferred when supported */
}</code></pre>

<p><strong>Method 4: <code>&lt;picture&gt;</code> for responsive images</strong> &mdash; serve different images per screen size:</p>
<pre><code>&lt;picture&gt;
  &lt;source media="(max-width: 600px)" srcset="/hero-mobile.webp"&gt;
  &lt;source media="(max-width: 1200px)" srcset="/hero-tablet.webp"&gt;
  &lt;img src="/hero-desktop.webp" alt="" class="hero-img"&gt;
&lt;/picture&gt;

&lt;style&gt;
  .hero-img {
    width: 100%;
    height: 100vh;
    object-fit: cover;
  }
&lt;/style&gt;</code></pre>

<p>Mobile users download a smaller image &mdash; massive bandwidth savings. <code>object-fit: cover</code> on the <code>&lt;img&gt;</code> works just like <code>background-size: cover</code> for backgrounds.</p>

<p><strong>Performance considerations:</strong></p>
<ul>
  <li><strong>Preload the LCP image</strong> &mdash; <code>&lt;link rel="preload" as="image" href="hero.webp" fetchpriority="high"&gt;</code> in the head.</li>
  <li><strong>Use modern formats</strong> &mdash; AVIF (best compression) → WebP (good fallback) → JPEG. <code>&lt;picture&gt;</code> with <code>type</code> attributes handles negotiation.</li>
  <li><strong>Set <code>width</code> and <code>height</code></strong> on <code>&lt;img&gt;</code> &mdash; reserves layout space, prevents CLS (cumulative layout shift).</li>
  <li><strong>Avoid <code>background-attachment: fixed</code> on mobile</strong> &mdash; performance varies; can disable hardware acceleration.</li>
</ul>

<p><strong>Accessibility:</strong> if the background contains meaningful information, use <code>&lt;img&gt;</code> with <code>alt</code>; backgrounds are invisible to screen readers. For purely decorative imagery, CSS background is fine and more performant.</p>
'''

ANSWERS[31] = r'''
<p>Both remove elements from the normal flow to varying degrees, but they differ fundamentally in what they&rsquo;re positioned <em>relative to</em> and what happens to the space they occupy.</p>

<table>
  <tr><th></th><th><code>position: relative</code></th><th><code>position: absolute</code></th></tr>
  <tr><td>In normal flow?</td><td>Yes &mdash; the element keeps its space</td><td>No &mdash; removed entirely from flow</td></tr>
  <tr><td>Anchored to</td><td>Itself (its own natural position)</td><td>Nearest positioned ancestor (or viewport)</td></tr>
  <tr><td>Affects siblings?</td><td>Yes &mdash; reserves original space</td><td>No &mdash; siblings reflow as if it didn&rsquo;t exist</td></tr>
  <tr><td>Use for</td><td>Small offsets; creating an anchor for absolute children</td><td>Tooltips, dropdowns, modals, badges</td></tr>
</table>

<p><strong>Visualizing the difference:</strong></p>

<pre><code>&lt;div class="container"&gt;
  &lt;div class="box"&gt;Box A&lt;/div&gt;
  &lt;div class="box positioned"&gt;Positioned&lt;/div&gt;
  &lt;div class="box"&gt;Box C&lt;/div&gt;
&lt;/div&gt;</code></pre>

<p><strong>With <code>position: relative</code> and <code>top: 50px</code>:</strong></p>
<ul>
  <li>The "Positioned" box renders 50px below its natural position.</li>
  <li>Its original space is preserved &mdash; "Box C" stays where it was.</li>
  <li>You see a 50px gap above "Positioned" because the box moved without taking siblings.</li>
</ul>

<p><strong>With <code>position: absolute</code> and <code>top: 50px; left: 0</code>:</strong></p>
<ul>
  <li>"Positioned" is removed from flow.</li>
  <li>"Box C" moves up &mdash; takes "Positioned"&rsquo;s former space.</li>
  <li>"Positioned" jumps to 50px from the top of its containing block (the nearest positioned ancestor).</li>
</ul>

<p><strong>The most common pattern &mdash; relative on parent, absolute on child:</strong></p>

<pre><code>.card {
  position: relative;       /* not actually moved; just becomes an anchor */
}
.card .badge {
  position: absolute;
  top: -10px;
  right: -10px;
  /* Now anchored to .card, not page */
}</code></pre>

<p>Without <code>position: relative</code> on <code>.card</code>, the absolute badge would anchor to the next-up positioned ancestor &mdash; possibly the body, putting it in the wrong corner.</p>

<p><strong>Containing block rules</strong> &mdash; what does <code>top: 0</code> measure from?</p>
<table>
  <tr><th>Element type</th><th>Containing block</th></tr>
  <tr><td><code>position: static</code> / <code>relative</code></td><td>Nearest block ancestor (the parent)</td></tr>
  <tr><td><code>position: absolute</code></td><td>Nearest <em>positioned</em> ancestor (any non-static)</td></tr>
  <tr><td><code>position: fixed</code></td><td>Viewport</td></tr>
</table>

<p>If no positioned ancestor exists for an absolute element, it anchors to the initial containing block (the viewport).</p>

<p><strong>Real-world examples:</strong></p>

<p><strong>1. Tooltip pattern:</strong></p>
<pre><code>.tooltip-trigger {
  position: relative;
}
.tooltip {
  position: absolute;
  bottom: 100%;             /* directly above the trigger */
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 5px;
  padding: 0.5em 1em;
  background: #333;
  color: white;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}
.tooltip-trigger:hover .tooltip {
  opacity: 1;
}</code></pre>

<p><strong>2. Centered overlay using <code>inset: 0; margin: auto</code>:</strong></p>
<pre><code>.modal {
  position: fixed;
  inset: 0;                 /* top/right/bottom/left: 0 */
  margin: auto;             /* center within inset region */
  width: 400px;
  height: 300px;
}</code></pre>

<p>Setting <code>inset: 0</code> + <code>margin: auto</code> + explicit dimensions centers an absolutely-positioned element &mdash; cleaner than the <code>top: 50%; left: 50%; translate(-50%, -50%)</code> trick.</p>

<p><strong>3. Sticky badge in corner:</strong></p>
<pre><code>.product {
  position: relative;
}
.product .new-badge {
  position: absolute;
  top: 1em;
  right: 1em;
  background: red;
  color: white;
  padding: 0.2em 0.5em;
  border-radius: 999px;
  font-size: 0.75em;
}</code></pre>

<p><strong>The "absolutely positioned does not affect layout" rule</strong> is what makes overlays clean &mdash; tooltips, dropdowns, and modals don&rsquo;t push other content around.</p>

<p><strong>Modern alternative: anchor positioning</strong> (2026 in Chromium) eliminates the need for <code>position: relative</code> wrappers:</p>
<pre><code>.tooltip-trigger { anchor-name: --tooltip-anchor; }
.tooltip {
  position: absolute;
  position-anchor: --tooltip-anchor;
  top: anchor(top);
  /* Anchored by name, not by ancestry */
}</code></pre>

<p>Tooltips, dropdowns, and popovers can be in any DOM location and still anchor visually to their trigger &mdash; finally solving the "tooltip clipped by overflow:hidden parent" problem.</p>
'''

ANSWERS[32] = r'''
<p>A CSS-only tooltip uses <code>:hover</code> on a parent to reveal a child element &mdash; combined with <code>position: absolute</code> for positioning and <code>opacity</code>/<code>visibility</code> transitions for smooth appearance.</p>

<pre><code>&lt;span class="tooltip" data-tooltip="Helpful info here"&gt;
  Hover me
&lt;/span&gt;

&lt;style&gt;
  .tooltip {
    position: relative;
    border-bottom: 1px dotted #666;
    cursor: help;
  }

  /* Tooltip uses ::after with attr() to read the text */
  .tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-4px);
    padding: 0.4em 0.7em;
    background: #333;
    color: white;
    border-radius: 4px;
    font-size: 0.85em;
    white-space: nowrap;
    pointer-events: none;

    /* Hidden by default — opacity + visibility for transitions */
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
  }

  /* Show on hover OR keyboard focus (accessibility!) */
  .tooltip:hover::after,
  .tooltip:focus-visible::after {
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(-8px);
  }
&lt;/style&gt;</code></pre>

<p><strong>Why <code>opacity</code> + <code>visibility</code> instead of <code>display</code>:</strong></p>
<ul>
  <li><code>display: none</code> can&rsquo;t be transitioned &mdash; element appears/disappears instantly.</li>
  <li><code>opacity: 0</code> alone keeps the element interactive &mdash; users can&rsquo;t click through invisible tooltips.</li>
  <li><code>opacity</code> + <code>visibility</code> together: smooth fade and properly hidden when faded out.</li>
</ul>

<p><strong>Adding an arrow:</strong></p>
<pre><code>.tooltip::before {
  content: "";
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: -4px;
  border: 4px solid transparent;
  border-top-color: #333;        /* arrow points down */
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
}

.tooltip:hover::before {
  opacity: 1;
  visibility: visible;
}</code></pre>

<p>The CSS triangle trick: a 0-size element with thick borders shows triangular border segments. Setting one border to a color and others to transparent creates a triangle pointing in that direction.</p>

<p><strong>Limitations of CSS-only tooltips:</strong></p>
<table>
  <tr><th>Issue</th><th>Workaround</th></tr>
  <tr><td>Touch devices have no <code>:hover</code></td><td>Add a click/tap handler in JS</td></tr>
  <tr><td>Tooltip clipped by <code>overflow: hidden</code> parent</td><td>Use Popover API (modern) or portal (React)</td></tr>
  <tr><td>No keyboard dismiss (Escape)</td><td>JS event listener required</td></tr>
  <tr><td>Doesn&rsquo;t flip when near viewport edge</td><td>Anchor positioning or library</td></tr>
  <tr><td>Complex content (links, buttons)</td><td>Use a real popup, not a tooltip</td></tr>
</table>

<p><strong>The <code>title</code> attribute</strong> &mdash; the simplest tooltip, browser-native:</p>
<pre><code>&lt;button title="Save (Ctrl+S)"&gt;Save&lt;/button&gt;</code></pre>

<p>Free, no CSS needed, but browser-styled (you can&rsquo;t restyle), no keyboard access, and inconsistent across browsers. Acceptable for keyboard shortcuts; insufficient for design-critical tooltips.</p>

<p><strong>Modern Popover API</strong> (2026 baseline):</p>
<pre><code>&lt;button popovertarget="tip"
        aria-describedby="tip"&gt;Help&lt;/button&gt;
&lt;div id="tip" popover="hint"&gt;
  Click to undo your last action.
&lt;/div&gt;

&lt;style&gt;
  [popover] {
    background: #333;
    color: white;
    padding: 0.5em 1em;
    border: none;
    border-radius: 4px;
  }
&lt;/style&gt;</code></pre>

<p>The Popover API solves overflow-clipping (renders in the top layer), provides Escape-to-dismiss, focus management, and proper accessibility. Combined with CSS Anchor Positioning, it&rsquo;s the cleanest path to production tooltips.</p>

<p><strong>Accessibility checklist:</strong></p>
<ul>
  <li>Tooltip should appear on <code>:focus</code> AND <code>:hover</code> (keyboard users have no hover).</li>
  <li>Use <code>aria-describedby</code> linking the trigger to the tooltip&rsquo;s id.</li>
  <li>Don&rsquo;t hide critical info in tooltips &mdash; touch users (no hover) miss it.</li>
  <li>Use the Popover API or libraries (Floating UI, Tippy.js) for production needs.</li>
</ul>

<p>For complex tooltip needs (chained tooltips, follow-cursor, on-demand positioning), libraries like Floating UI handle edge cases. For most informational hover tooltips, the CSS-only pattern is enough.</p>
'''

ANSWERS[33] = r'''
<p>The <code>object-fit</code> property controls how a replaced element (image, video) fills its content box when its dimensions don&rsquo;t match the box&rsquo;s aspect ratio. It&rsquo;s the image-equivalent of <code>background-size</code>.</p>

<table>
  <tr><th>Value</th><th>Behavior</th></tr>
  <tr><td><code>fill</code></td><td>Stretch to fill, distort if needed (default)</td></tr>
  <tr><td><code>cover</code></td><td>Fill the box, crop edges to preserve aspect</td></tr>
  <tr><td><code>contain</code></td><td>Fit entirely, may letterbox if box is wider</td></tr>
  <tr><td><code>none</code></td><td>No scaling; use intrinsic size</td></tr>
  <tr><td><code>scale-down</code></td><td>Smaller of <code>none</code> or <code>contain</code></td></tr>
</table>

<pre><code>.cover {
  width: 200px;
  height: 200px;
  object-fit: cover;       /* fills 200x200 box, crops as needed */
  object-position: center; /* control crop alignment */
}

.contain {
  width: 200px;
  height: 200px;
  object-fit: contain;     /* fits inside, may show empty space */
  background: #f0f0f0;     /* fill empty space with bg color */
}</code></pre>

<p><strong>Why this matters for responsive images</strong> &mdash; when you set fixed dimensions on <code>&lt;img&gt;</code> without <code>object-fit</code>, images stretch or squash. <code>object-fit: cover</code> is essential for image grids with consistent shapes.</p>

<pre><code>.gallery img {
  width: 100%;
  aspect-ratio: 4 / 3;       /* enforce shape */
  object-fit: cover;          /* fill box without distortion */
  display: block;
}</code></pre>

<p>Now images of any source dimensions render as 4:3 boxes &mdash; portraits get cropped vertically, landscapes get cropped horizontally, all maintaining their aspect ratio without warping.</p>

<p><strong>Pairing with <code>aspect-ratio</code></strong> &mdash; modern responsive images:</p>
<pre><code>.video-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9;       /* like YouTube */
  object-fit: cover;
}

.product-photo {
  width: 100%;
  aspect-ratio: 1;            /* square */
  object-fit: cover;
}

.banner {
  width: 100%;
  aspect-ratio: 21 / 9;       /* ultrawide */
  object-fit: cover;
}</code></pre>

<p>One CSS pattern handles every image regardless of source dimensions &mdash; the box defines the shape, <code>object-fit: cover</code> handles the contents.</p>

<p><strong>The <code>object-position</code> property</strong> controls how the image is anchored within the box:</p>
<pre><code>.profile-photo {
  width: 200px;
  height: 200px;
  object-fit: cover;
  object-position: center top;     /* keep top of head visible when cropping */
}

/* Default is center center — the middle of the image stays visible */
/* For portraits, "top" or "center top" usually preserves faces */</code></pre>

<table>
  <tr><th>Position</th><th>Visible center</th></tr>
  <tr><td><code>center</code> (default)</td><td>Center of image</td></tr>
  <tr><td><code>top</code></td><td>Top of image (good for portraits)</td></tr>
  <tr><td><code>bottom</code></td><td>Bottom of image</td></tr>
  <tr><td><code>50% 30%</code></td><td>Custom anchor point</td></tr>
</table>

<p><strong>Comparing to background images:</strong></p>
<table>
  <tr><th>Property</th><th>For images (<code>&lt;img&gt;</code>)</th><th>For backgrounds</th></tr>
  <tr><td>Sizing</td><td><code>object-fit</code></td><td><code>background-size</code></td></tr>
  <tr><td>Positioning</td><td><code>object-position</code></td><td><code>background-position</code></td></tr>
  <tr><td>Repeating</td><td>N/A (single image)</td><td><code>background-repeat</code></td></tr>
</table>

<p>Same conceptual values; different property names. Use <code>&lt;img&gt;</code> for content images (semantic, has <code>alt</code>, indexable, lazy-loadable). Use background images for decorative content.</p>

<p><strong>Modern responsive images workflow:</strong></p>
<pre><code>&lt;picture&gt;
  &lt;source srcset="image.avif" type="image/avif"&gt;
  &lt;source srcset="image.webp" type="image/webp"&gt;
  &lt;img src="image.jpg"
       alt="..."
       loading="lazy"
       width="800"
       height="600"
       class="responsive-img"&gt;
&lt;/picture&gt;

&lt;style&gt;
  .responsive-img {
    width: 100%;
    aspect-ratio: 4 / 3;
    object-fit: cover;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>

<p>Combines: format negotiation (<code>&lt;picture&gt;</code>), modern format (AVIF), lazy loading, dimensions to prevent CLS, and consistent visual shape via aspect-ratio + object-fit. Production-grade image handling.</p>
'''

ANSWERS[34] = r'''
<p>CSS multi-column layouts come in two flavors with different goals: <strong>CSS columns</strong> (the <code>columns</code> property) for prose that flows naturally between columns like a newspaper, and <strong>CSS Grid</strong> for structured items where each is independent.</p>

<p><strong>CSS columns &mdash; flowing prose:</strong></p>
<pre><code>.article {
  columns: 3 250px;             /* up to 3 columns, each at least 250px */
  column-gap: 2em;
  column-rule: 1px solid #ddd;
  column-fill: balance;         /* equalize column heights */
}
.article h2 {
  column-span: all;             /* heading spans all columns */
  margin-bottom: 1em;
}
.article p {
  break-inside: avoid;          /* don't split paragraphs */
}</code></pre>

<p><strong>The <code>columns</code> shorthand</strong>: <code>columns: count count-or-width</code>. Common patterns:</p>
<ul>
  <li><code>columns: 3</code> &mdash; exactly 3 columns.</li>
  <li><code>columns: 250px</code> &mdash; columns at least 250px; browser computes count.</li>
  <li><code>columns: 3 250px</code> &mdash; up to 3 columns, each at least 250px (most flexible).</li>
</ul>

<p><strong>Column properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>column-count</code></td><td>Exact number of columns</td></tr>
  <tr><td><code>column-width</code></td><td>Minimum column width</td></tr>
  <tr><td><code>columns</code></td><td>Shorthand</td></tr>
  <tr><td><code>column-gap</code></td><td>Space between columns</td></tr>
  <tr><td><code>column-rule</code></td><td>Line between columns (border syntax)</td></tr>
  <tr><td><code>column-span</code></td><td><code>none</code> or <code>all</code> &mdash; element spans all columns</td></tr>
  <tr><td><code>column-fill</code></td><td><code>auto</code> or <code>balance</code> &mdash; balanced heights</td></tr>
  <tr><td><code>break-inside</code></td><td>Prevent splitting an element across columns</td></tr>
</table>

<p><strong>How columns flow:</strong> top of column 1 &rarr; bottom of column 1 &rarr; top of column 2 &rarr; bottom of column 2 &rarr; ... Like a newspaper.</p>

<p><strong>CSS Grid &mdash; structured items:</strong></p>
<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}</code></pre>

<p>Cards lay out left-to-right, top-to-bottom &mdash; one row at a time. Each card is independent; not parts of a flowing paragraph.</p>

<p><strong>Pick by content type:</strong></p>
<table>
  <tr><th></th><th>CSS columns</th><th>CSS Grid</th></tr>
  <tr><td>Best for</td><td>Article text, FAQ lists, tag clouds</td><td>Cards, photo galleries, dashboards</td></tr>
  <tr><td>Item flow</td><td>Top-to-bottom in column 1, then 2, ...</td><td>Each item placed independently</td></tr>
  <tr><td>Item shape</td><td>Continuous content (text)</td><td>Discrete blocks</td></tr>
  <tr><td>Heights</td><td>Browser balances</td><td>Each row aligns; spans possible</td></tr>
  <tr><td>Responsive</td><td><code>columns: 3 250px</code> &mdash; reflows automatically</td><td><code>auto-fit + minmax()</code> &mdash; reflows automatically</td></tr>
</table>

<p><strong>Avoid splitting elements</strong> across columns:</p>
<pre><code>.no-break {
  break-inside: avoid;
  /* Browser tries hard not to split this element */
}

/* Force a column break BEFORE an element */
.new-section {
  break-before: column;
}</code></pre>

<p>Equivalent properties for printing: <code>page-break-inside: avoid</code> for printed output. The <code>break-*</code> properties are the modern multipurpose version.</p>

<p><strong>Real-world: FAQ list</strong> using columns:</p>
<pre><code>.faq-list {
  columns: 2 350px;
  column-gap: 2em;
}
.faq-list .qa {
  break-inside: avoid;        /* keep Q&A together */
  margin-bottom: 1.5em;
}</code></pre>

<p><strong>Modern alternative for masonry-like layouts</strong> (CSS native masonry, 2026 Chromium):</p>
<pre><code>.masonry {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  grid-template-rows: masonry;       /* Pinterest-style packing */
  gap: 1rem;
}</code></pre>

<p>Native masonry packs items tightly without the gaps Grid leaves &mdash; previously required JavaScript libraries (Masonry.js, isotope).</p>

<p><strong>For most modern UIs in 2026, CSS Grid is the workhorse</strong> &mdash; cards, galleries, dashboards, layouts. <code>columns</code> shines for actual prose: articles, FAQ lists, tag clouds. Choose by intent: do items belong to a continuous flow (columns), or are they independent (Grid)?</p>
'''

ANSWERS[35] = r'''
<p>CSS Grid&rsquo;s <code>grid-template-areas</code> property defines named regions that elements can be placed into. It produces declarative, visually-readable layout code &mdash; the CSS reads like an ASCII diagram of the page.</p>

<pre><code>.layout {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header  header  header"
    "nav     main    aside"
    "footer  footer  footer";
  min-height: 100vh;
  gap: 1em;
}

header { grid-area: header; }
nav    { grid-area: nav;    }
main   { grid-area: main;   }
aside  { grid-area: aside;  }
footer { grid-area: footer; }</code></pre>

<p><strong>How to read the grid:</strong></p>
<ul>
  <li>Each string is a row.</li>
  <li>Each word in the string is a cell.</li>
  <li>Repeating the same name across cells creates a spanning area.</li>
  <li>The cell count must match <code>grid-template-columns</code>.</li>
  <li>The string count must match <code>grid-template-rows</code>.</li>
</ul>

<p>The example above: 3 columns &times; 3 rows, with the header spanning all 3 columns of row 1, footer spanning all 3 of row 3.</p>

<p><strong>Empty cells with <code>.</code> (period):</strong></p>
<pre><code>.gallery {
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "photo  photo  caption"
    ".      .      caption";
}
.photo   { grid-area: photo; }
.caption { grid-area: caption; }
/* Two cells in the bottom row are empty */</code></pre>

<p>Periods leave space without an associated element &mdash; useful for visual gaps in custom layouts.</p>

<p><strong>The <code>grid-template</code> shorthand</strong> combines columns, rows, and areas in one rule:</p>
<pre><code>.layout {
  display: grid;
  grid-template:
    "header header header" auto
    "nav    main   aside"  1fr
    "footer footer footer" auto
    / 200px 1fr 200px;
  min-height: 100vh;
}</code></pre>

<p>Row sizes go after each row&rsquo;s string; column sizes after the slash. Compact but harder to read for beginners; useful for design-system definitions.</p>

<p><strong>Responsive: rearrange areas per breakpoint:</strong></p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "header"
    "main"
    "aside"
    "nav"
    "footer";
}

@media (min-width: 768px) {
  .layout {
    grid-template-columns: 200px 1fr;
    grid-template-areas:
      "header  header"
      "nav     main"
      "aside   main"
      "footer  footer";
  }
}

@media (min-width: 1200px) {
  .layout {
    grid-template-columns: 200px 1fr 200px;
    grid-template-areas:
      "header  header  header"
      "nav     main    aside"
      "footer  footer  footer";
  }
}</code></pre>

<p><strong>This is the killer feature</strong>: rearrange visual layout entirely through CSS without changing HTML order. Mobile gets logical reading order; desktop gets the structured layout. Same markup, three different visual layouts.</p>

<p><strong>Constraints and gotchas:</strong></p>
<ul>
  <li><strong>Names cannot contain spaces or hyphens at the start</strong> &mdash; use camelCase or underscores.</li>
  <li><strong>Areas must be rectangular</strong> &mdash; you can&rsquo;t define an L-shaped or other non-rectangular area.</li>
  <li><strong>All declared cells must be filled</strong> &mdash; missing cells (or non-rectangular areas) make the rule invalid.</li>
  <li><strong>Adjacent same-name cells</strong> must touch on at least one edge to merge into one area.</li>
</ul>

<p><strong>Real-world: dashboard with sidebar:</strong></p>
<pre><code>.dashboard {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 60px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar main";
  height: 100vh;
}

.sidebar { grid-area: sidebar; background: #2c3e50; }
.header  { grid-area: header;  background: white; border-bottom: 1px solid #eee; }
.main    { grid-area: main;    overflow-y: auto; padding: 2em; }</code></pre>

<p>Compare to Flexbox or floats: this dashboard layout is one CSS rule, instantly readable. The CSS describes the layout visually &mdash; nothing else does.</p>

<p><strong>Comparing to <code>grid-column</code>/<code>grid-row</code>:</strong> using line numbers (<code>grid-column: 1 / 3</code>) is more flexible (you can place items anywhere); template-areas is more declarative (the layout is visible). For named-region layouts, areas usually win on readability.</p>
'''

ANSWERS[36] = r'''
<p>CSS blend modes determine how an element&rsquo;s content blends with what&rsquo;s underneath &mdash; like Photoshop layer modes. Two related properties: <code>mix-blend-mode</code> (blends an element with its parent or siblings) and <code>background-blend-mode</code> (blends an element&rsquo;s own backgrounds).</p>

<table>
  <tr><th>Mode</th><th>Effect</th></tr>
  <tr><td><code>normal</code></td><td>Default: top opaque covers below</td></tr>
  <tr><td><code>multiply</code></td><td>Darkens (white = transparent)</td></tr>
  <tr><td><code>screen</code></td><td>Lightens (black = transparent)</td></tr>
  <tr><td><code>overlay</code></td><td>Combines multiply and screen</td></tr>
  <tr><td><code>darken</code> / <code>lighten</code></td><td>Pixel-by-pixel min/max</td></tr>
  <tr><td><code>color-dodge</code> / <code>color-burn</code></td><td>Brighten or darken aggressively</td></tr>
  <tr><td><code>difference</code> / <code>exclusion</code></td><td>Inversion-based effects</td></tr>
  <tr><td><code>hue</code> / <code>saturation</code> / <code>color</code> / <code>luminosity</code></td><td>HSL-component blends</td></tr>
</table>

<p><strong>Common use cases for <code>mix-blend-mode</code>:</strong></p>

<p><strong>1. Text over image with high contrast</strong> &mdash; the canonical use:</p>
<pre><code>.hero {
  position: relative;
  background: url("/hero.jpg") center / cover;
  height: 60vh;
}
.hero h1 {
  color: white;
  mix-blend-mode: difference;     /* inverts based on background */
  font-size: 5em;
  /* Text appears as inverted color of underlying image */
}</code></pre>

<p>The <code>difference</code> mode subtracts pixel values &mdash; white text becomes the inverse of the background, ensuring legibility regardless of the photo.</p>

<p><strong>2. Overlapping shapes with color blending:</strong></p>
<pre><code>.circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  position: absolute;
  mix-blend-mode: multiply;
}
.circle.red    { background: red;    left: 0;    }
.circle.green  { background: green;  left: 80px; }
.circle.blue   { background: blue;   left: 160px;}
/* Overlapping regions show blended colors */</code></pre>

<p>This produces a color-mixing chart effect &mdash; a classic visual for color-mode demos.</p>

<p><strong>3. Photo color treatments:</strong></p>
<pre><code>.photo-overlay {
  background: rebeccapurple;
  mix-blend-mode: multiply;
  /* Tints the photo below purple — duotone-like effect */
}</code></pre>

<p><strong>The <code>background-blend-mode</code> property</strong> blends multiple backgrounds on the same element:</p>
<pre><code>.duotone {
  background:
    linear-gradient(rgba(0, 100, 255, 0.5), rgba(255, 100, 0, 0.5)),
    url("/photo.jpg") center / cover;
  background-blend-mode: multiply;
  /* Gradient blends with the photo, creating a duotone effect */
}</code></pre>

<p>The gradient and image are <em>two backgrounds on one element</em> &mdash; <code>background-blend-mode: multiply</code> mixes them. Without it, the gradient simply overlays.</p>

<p><strong>Stacking context warning:</strong> <code>mix-blend-mode</code> creates a new stacking context. If a sibling has <code>opacity: 0.5</code> or <code>transform</code>, blending may not work as expected because the sibling becomes its own context.</p>

<p><strong>Performance:</strong> blend modes trigger compositor work &mdash; cheap on modern GPUs but can be expensive on older mobile. Avoid stacking many blended elements; test on lower-tier devices.</p>

<p><strong>Difference between blending and opacity:</strong></p>
<table>
  <tr><th></th><th><code>opacity</code></th><th><code>mix-blend-mode</code></th></tr>
  <tr><td>What it does</td><td>Reduces overall transparency</td><td>Mathematically blends pixel colors</td></tr>
  <tr><td>Example</td><td>Faded image</td><td>Color-mixed image</td></tr>
  <tr><td>Background visible?</td><td>Yes (through transparency)</td><td>Yes (through blend math)</td></tr>
</table>

<p><code>opacity</code> blends uniformly through transparency. Blend modes do per-pixel math (multiply, screen, etc.) producing distinct visual effects unrelated to transparency.</p>

<p><strong>Real-world: hero overlay treatment</strong> &mdash; common design pattern:</p>
<pre><code>.hero {
  position: relative;
  background:
    linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
    url("/photo.jpg") center / cover;
  background-blend-mode: multiply;
  /* Photo appears darker and richer */
}
.hero h1 {
  color: white;
  /* No mix-blend-mode needed — overlay handles legibility */
}</code></pre>

<p>For precision color treatments (Instagram-style filters), use <code>filter</code> properties (saturation, hue-rotate, sepia) in addition to or instead of blend modes.</p>
'''

ANSWERS[37] = r'''
<p>Image overlays add color, gradient, or texture on top of images &mdash; for legibility (text over photos), branding (consistent color treatment), hover effects (reveal on hover), or visual storytelling.</p>

<p><strong>Method 1: <code>background-image</code> stack</strong> &mdash; gradient over image, single element:</p>
<pre><code>.hero {
  background:
    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url("/hero.jpg") center / cover;
  height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}</code></pre>

<p>Multiple backgrounds stack in the order listed &mdash; first listed is on top. The dark gradient (semi-transparent black) sits over the image, providing contrast for text. This is the most common pattern.</p>

<p><strong>Variations of the overlay:</strong></p>
<pre><code>/* Bottom-only fade — Netflix-style */
background:
  linear-gradient(to top, rgba(0,0,0,0.95) 0%, transparent 50%),
  url("show.jpg") center / cover;

/* Brand color tint */
background:
  linear-gradient(rgba(0, 102, 204, 0.6), rgba(0, 102, 204, 0.6)),
  url("photo.jpg") center / cover;

/* Vignette — radial dark edges */
background:
  radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.6) 100%),
  url("photo.jpg") center / cover;

/* Diagonal fade */
background:
  linear-gradient(135deg, rgba(255,107,53,0.7), rgba(0,102,204,0.7)),
  url("photo.jpg") center / cover;
background-blend-mode: multiply;</code></pre>

<p><strong>Method 2: <code>::before</code> pseudo-element</strong> &mdash; for HTML <code>&lt;img&gt;</code> elements where backgrounds can&rsquo;t be used:</p>
<pre><code>&lt;figure class="image-with-overlay"&gt;
  &lt;img src="photo.jpg" alt=""&gt;
  &lt;figcaption&gt;Caption text&lt;/figcaption&gt;
&lt;/figure&gt;

&lt;style&gt;
  .image-with-overlay {
    position: relative;
    margin: 0;
    overflow: hidden;
  }
  .image-with-overlay img {
    width: 100%;
    height: 300px;
    object-fit: cover;
    display: block;
  }
  .image-with-overlay::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    pointer-events: none;
  }
  .image-with-overlay figcaption {
    position: absolute;
    bottom: 1em;
    left: 1em;
    color: white;
    z-index: 1;            /* above the overlay */
  }
&lt;/style&gt;</code></pre>

<p><strong>Method 3: Hover-triggered overlay</strong> &mdash; reveal info on hover:</p>
<pre><code>&lt;figure class="card"&gt;
  &lt;img src="product.jpg" alt=""&gt;
  &lt;div class="overlay"&gt;
    &lt;h3&gt;Product Name&lt;/h3&gt;
    &lt;a href="#"&gt;View Details&lt;/a&gt;
  &lt;/div&gt;
&lt;/figure&gt;

&lt;style&gt;
  .card {
    position: relative;
    overflow: hidden;
    margin: 0;
  }
  .card img {
    width: 100%;
    transition: transform 0.4s;
  }
  .card .overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 102, 204, 0.85);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .card:hover img {
    transform: scale(1.05);     /* zoom slightly */
  }
  .card:hover .overlay {
    opacity: 1;                  /* reveal overlay */
  }
&lt;/style&gt;</code></pre>

<p>Combination of zoom on the image + fade-in overlay produces a polished interaction common on portfolio sites and product galleries.</p>

<p><strong>Method 4: <code>backdrop-filter</code></strong> &mdash; frosted-glass overlay:</p>
<pre><code>.glass-overlay {
  position: absolute;
  inset: 1em;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  border-radius: 12px;
  padding: 1em;
}</code></pre>

<p>The backdrop is blurred &mdash; producing iOS-style frosted-glass effects. Excellent for caption overlays on busy photo backgrounds.</p>

<p><strong>Method 5: <code>mix-blend-mode</code></strong> for color blending without transparency:</p>
<pre><code>.image-container {
  position: relative;
}
.image-container::after {
  content: "";
  position: absolute;
  inset: 0;
  background: rebeccapurple;
  mix-blend-mode: multiply;
  /* Tints the image below; opaque element but blended */
}</code></pre>

<p>Different visual effect from semi-transparent overlays &mdash; produces duotone-style color treatments.</p>

<p><strong>Accessibility:</strong> ensure overlay color provides enough contrast for text. WCAG AA requires 4.5:1 contrast for normal text, 3:1 for large/UI text. Test with a contrast checker; semi-transparent overlays sometimes appear to provide contrast but fail on bright photos.</p>

<p>For text directly over photos, dark overlays (rgba(0,0,0,0.4-0.6)) are nearly always sufficient. Bright background gradients can fail contrast on white text &mdash; verify before shipping.</p>
'''

ANSWERS[38] = r'''
<p>The <code>@keyframes</code> rule defines named animation sequences &mdash; the choreography that the <code>animation</code> property executes. Without keyframes, an animation has no instructions; it just runs through default state.</p>

<pre><code>@keyframes slide-in {
  from { transform: translateX(-100%); opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}

.toast {
  animation: slide-in 0.3s ease-out forwards;
}</code></pre>

<p><strong>Two equivalent syntaxes:</strong></p>
<table>
  <tr><th>Syntax</th><th>Meaning</th></tr>
  <tr><td><code>from { ... }</code></td><td>Same as <code>0% { ... }</code></td></tr>
  <tr><td><code>to { ... }</code></td><td>Same as <code>100% { ... }</code></td></tr>
  <tr><td><code>0%</code> through <code>100%</code></td><td>Specific points along the timeline</td></tr>
</table>

<p>Use <code>from</code>/<code>to</code> for two-step animations; use percentages for multi-step sequences.</p>

<p><strong>Multi-step animation:</strong></p>
<pre><code>@keyframes pulse {
  0%   { transform: scale(1);    opacity: 1;   }
  50%  { transform: scale(1.1);  opacity: 0.8; }
  100% { transform: scale(1);    opacity: 1;   }
}

.heartbeat {
  animation: pulse 1s ease-in-out infinite;
}</code></pre>

<p><strong>Properties to know:</strong></p>
<ul>
  <li><strong>Implicit interpolation</strong> &mdash; the browser fills in values between keyframes. <code>50%</code> doesn&rsquo;t need to specify every property; the browser tweens.</li>
  <li><strong>Properties not in keyframes</strong> stay at their normal CSS values during the animation.</li>
  <li><strong>Multiple selectors per keyframe block</strong> with commas:</li>
</ul>

<pre><code>@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
/* Same style at 0% and 100% — useful for "in and out" effects */</code></pre>

<p><strong>Keyframe-defined properties override the regular ones during animation:</strong></p>
<pre><code>.box {
  background: blue;            /* normal state */
  animation: color-shift 2s infinite;
}
@keyframes color-shift {
  from { background: red; }
  to   { background: yellow; }
}
/* During animation, background animates from red to yellow,
   not from blue. After animation ends, returns to blue. */</code></pre>

<p>To preserve the end state of an animation, use <code>animation-fill-mode: forwards</code>. To preserve the start state during a delay, use <code>backwards</code>. <code>both</code> does both.</p>

<p><strong>Naming and reuse:</strong></p>
<pre><code>/* Generic keyframes used by multiple components */
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.toast       { animation: fade-in 0.3s ease-out; }
.modal       { animation: fade-up 0.4s ease-out backwards; }
.notification { animation: fade-up 0.3s 0.1s ease-out backwards; }
/* Three components share the same keyframes */</code></pre>

<p><strong>Animatable properties</strong> &mdash; not everything can be animated. The CSS spec lists explicitly which properties are animatable. Common animatable: <code>transform</code>, <code>opacity</code>, <code>color</code>, <code>background-color</code>, <code>border-color</code>, <code>width</code>, <code>height</code>, <code>top</code>, <code>left</code>, <code>filter</code>. Non-animatable: <code>display</code> (without <code>transition-behavior: allow-discrete</code>), <code>position</code>, custom properties (without <code>@property</code>).</p>

<p><strong>The <code>steps()</code> timing function</strong> &mdash; for sprite-sheet animations:</p>
<pre><code>@keyframes walk {
  from { background-position: 0 0; }
  to   { background-position: -800px 0; }   /* 8 frames at 100px each */
}

.sprite {
  width: 100px;
  height: 100px;
  background: url("walk-sprite.png");
  animation: walk 1s steps(8) infinite;       /* 8 discrete steps, no smooth tween */
}</code></pre>

<p><code>steps(N)</code> divides the duration into N discrete jumps &mdash; perfect for frame-by-frame animations like sprite sheets, typewriter effects, or counter animations.</p>

<p><strong>Animatable custom properties with <code>@property</code></strong> (2026):</p>
<pre><code>@property --gradient-angle {
  syntax: "&lt;angle&gt;";
  inherits: false;
  initial-value: 0deg;
}

@keyframes spin-gradient {
  to { --gradient-angle: 360deg; }
}

.box {
  background: linear-gradient(var(--gradient-angle), red, blue);
  animation: spin-gradient 3s linear infinite;
}</code></pre>

<p>Without <code>@property</code> registration, the gradient angle would jump abruptly. Registering it as typed unlocks proper animation.</p>

<p><strong>Performance tip:</strong> animate properties on the compositor only (<code>transform</code>, <code>opacity</code>, <code>filter</code>). Avoid animating <code>width</code>, <code>height</code>, <code>top</code>, <code>margin</code> &mdash; they trigger layout recalculation on every frame.</p>

<p><strong>Modern: scroll-driven keyframe animations</strong> &mdash; animation progress tied to scroll position, not time:</p>
<pre><code>.scroll-fade {
  animation: fade-in linear;
  animation-timeline: view();
  animation-range: cover;
}</code></pre>
'''

ANSWERS[39] = r'''
<p>The <code>::before</code> and <code>::after</code> pseudo-elements insert generated content into an element &mdash; visually present but not in the DOM. They take a <code>content</code> property and behave like first and last child elements respectively.</p>

<pre><code>.btn::before {
  content: "&rarr; ";
}

.required::after {
  content: " *";
  color: red;
}

.tooltip[data-tip]::after {
  content: attr(data-tip);     /* read from data attribute */
}</code></pre>

<p><strong>The <code>content</code> property is required</strong> &mdash; without it, the pseudo-element doesn&rsquo;t render. <code>content: ""</code> (empty string) is valid for shape-only pseudo-elements like decorative arrows or borders.</p>

<p><strong>Content sources:</strong></p>
<table>
  <tr><th>Source</th><th>Example</th></tr>
  <tr><td>Literal string</td><td><code>content: "Hello"</code></td></tr>
  <tr><td>Empty (shape only)</td><td><code>content: ""</code></td></tr>
  <tr><td>Attribute value</td><td><code>content: attr(data-label)</code></td></tr>
  <tr><td>Counter</td><td><code>content: counter(section)</code></td></tr>
  <tr><td>URL (image)</td><td><code>content: url("icon.svg")</code></td></tr>
  <tr><td>Quotation marks</td><td><code>content: open-quote / close-quote</code></td></tr>
</table>

<p><strong>Common patterns:</strong></p>

<p><strong>1. Decorative shapes (no actual content):</strong></p>
<pre><code>/* Triangle pointer below an element */
.tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: #333;
}

/* Underline accent */
.heading {
  position: relative;
  padding-bottom: 0.5em;
}
.heading::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: red;
}</code></pre>

<p><strong>2. Reading data attributes:</strong></p>
<pre><code>&lt;span class="badge" data-count="5"&gt;Notifications&lt;/span&gt;

&lt;style&gt;
  .badge::after {
    content: "(" attr(data-count) ")";
    margin-left: 0.5em;
    color: red;
  }
&lt;/style&gt;</code></pre>

<p><strong>3. Counters &mdash; auto-numbering without a list:</strong></p>
<pre><code>article { counter-reset: section; }

article h2 {
  counter-increment: section;
}
article h2::before {
  content: counter(section, decimal-leading-zero) ". ";
  color: #999;
}
/* Renders: "01. Heading One", "02. Heading Two", ... */</code></pre>

<p><strong>4. Required field markers:</strong></p>
<pre><code>label.required::after {
  content: " *";
  color: red;
  speak: never;       /* hide from screen readers */
}</code></pre>

<p>The <code>speak: never</code> hint tells screen readers to ignore the asterisk &mdash; users hear the field label without "asterisk" being read out. Pair with <code>aria-required="true"</code> on the input for proper accessibility.</p>

<p><strong>5. Block quotes with smart quotes:</strong></p>
<pre><code>blockquote::before { content: open-quote;  font-size: 3em; color: #ddd; }
blockquote::after  { content: close-quote; font-size: 3em; color: #ddd; }
blockquote {
  quotes: "&ldquo;" "&rdquo;" "&lsquo;" "&rsquo;";   /* outer / inner pairs */
}</code></pre>

<p><strong>6. Gradient borders</strong> with <code>::before</code> / <code>::after</code>:</p>
<pre><code>.gradient-border {
  position: relative;
  padding: 1em;
  background: white;
}
.gradient-border::before {
  content: "";
  position: absolute;
  inset: -3px;
  z-index: -1;
  background: linear-gradient(45deg, #0066cc, #ff6b35);
  border-radius: inherit;
}</code></pre>

<p><strong>Limitations:</strong></p>
<ul>
  <li><strong>Not real DOM elements</strong> &mdash; can&rsquo;t be inspected as separate nodes; can&rsquo;t have event listeners.</li>
  <li><strong>Don&rsquo;t work on replaced elements</strong> &mdash; <code>&lt;img&gt;</code>, <code>&lt;input&gt;</code>, <code>&lt;video&gt;</code> can&rsquo;t have <code>::before</code>/<code>::after</code>. Wrap them in a div if needed.</li>
  <li><strong>Screen reader announcement varies</strong> &mdash; some announce <code>content</code> text, some don&rsquo;t. Don&rsquo;t put critical info in pseudo-elements.</li>
</ul>

<p><strong>Single-colon legacy:</strong> CSS2 used single colon (<code>:before</code>); CSS3 introduced double colon (<code>::before</code>) to distinguish pseudo-elements from pseudo-classes (<code>:hover</code>). Both syntaxes work in modern browsers, but always use <code>::</code> for pseudo-elements as the spec-correct form.</p>

<p>Pseudo-elements are essential for design system polish &mdash; subtle decorations, badges, indicators, separators &mdash; without polluting markup. Reserve them for purely visual content; don&rsquo;t hide important information in pseudo-elements where it might be lost to screen readers or copy operations.</p>
'''

ANSWERS[40] = r'''
<p>A responsive Flexbox navbar handles horizontal layout on desktop and collapses to a vertical menu on mobile. The pattern combines <code>display: flex</code>, <code>justify-content: space-between</code>, and a media query for the breakpoint switch &mdash; with optional checkbox-driven toggle for true CSS-only mobile behavior.</p>

<pre><code>&lt;nav class="navbar"&gt;
  &lt;a href="/" class="logo"&gt;Acme&lt;/a&gt;

  &lt;input type="checkbox" id="nav-toggle" class="nav-toggle"&gt;
  &lt;label for="nav-toggle" class="hamburger" aria-label="Toggle menu"&gt;
    &lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;
  &lt;/label&gt;

  &lt;ul class="nav-links"&gt;
    &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
  &lt;/ul&gt;
&lt;/nav&gt;

&lt;style&gt;
  .navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1em;
    background: white;
    border-bottom: 1px solid #eee;
  }

  .nav-links {
    display: flex;
    gap: 1.5em;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .nav-links a {
    color: #333;
    text-decoration: none;
    padding: 0.5em;
    border-radius: 4px;
    transition: background 0.2s;
  }
  .nav-links a:hover {
    background: #f0f8ff;
  }

  .nav-toggle {
    display: none;             /* hidden checkbox */
  }

  .hamburger {
    display: none;             /* hidden on desktop */
    cursor: pointer;
    flex-direction: column;
    gap: 4px;
  }
  .hamburger span {
    display: block;
    width: 24px;
    height: 3px;
    background: #333;
    border-radius: 2px;
  }

  /* Mobile breakpoint */
  @media (max-width: 768px) {
    .navbar {
      flex-wrap: wrap;
    }
    .hamburger {
      display: flex;            /* show hamburger button */
    }
    .nav-links {
      display: none;            /* hide menu by default */
      flex-direction: column;
      width: 100%;
      gap: 0;
      margin-top: 1em;
    }
    .nav-links li {
      width: 100%;
    }
    .nav-links a {
      display: block;
      padding: 0.75em;
    }
    /* When checkbox is checked, show menu */
    .nav-toggle:checked ~ .nav-links {
      display: flex;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>How it works:</strong></p>
<ul>
  <li><strong>Desktop (>768px)</strong>: <code>justify-content: space-between</code> pushes logo to the left and menu to the right. Hamburger is hidden.</li>
  <li><strong>Mobile (&le;768px)</strong>: Hamburger appears; menu is hidden by default. Clicking the hamburger checks the hidden checkbox, which the sibling combinator (<code>~</code>) uses to reveal the menu.</li>
</ul>

<p><strong>The hidden-checkbox technique</strong> is a CSS-only way to track click state &mdash; the label triggers the checkbox toggle, and CSS reads <code>:checked</code> to apply state-dependent styles. Works without JavaScript.</p>

<p><strong>Hamburger animation</strong> on toggle (transforming the three lines into an X):</p>
<pre><code>.hamburger span {
  transition: transform 0.3s, opacity 0.3s;
}

.nav-toggle:checked ~ .hamburger span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.nav-toggle:checked ~ .hamburger span:nth-child(2) {
  opacity: 0;
}
.nav-toggle:checked ~ .hamburger span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}</code></pre>

<p>Top line rotates 45&deg; down; bottom line rotates -45&deg; up; middle fades out. Result: an X.</p>

<p><strong>Accessibility considerations:</strong></p>
<ul>
  <li><strong>Real button preferred</strong> &mdash; the checkbox-label hack works but real <code>&lt;button aria-expanded&gt;</code> with JavaScript provides better ARIA states.</li>
  <li><strong>Keyboard navigation</strong> &mdash; the label/checkbox can be focused with Tab, and Space toggles. Add <code>label[for]</code> to ensure proper focus management.</li>
  <li><strong><code>aria-label</code> on the hamburger</strong> &mdash; tells screen readers what the icon does ("Toggle menu").</li>
  <li><strong>Focus styles</strong> &mdash; ensure the hamburger has a visible <code>:focus-visible</code> style.</li>
  <li><strong>Trap focus on mobile menu</strong> &mdash; advanced feature requiring JS.</li>
</ul>

<p><strong>Modern alternative: <code>&lt;dialog&gt;</code></strong> for full-screen mobile menus &mdash; provides proper ARIA, focus trap, and Escape-to-close natively. Combine with the Popover API for the cleanest accessible mobile menu.</p>

<p>For production navbars with full keyboard arrows, type-to-search, and ARIA, libraries like Radix UI or Headless UI&rsquo;s Disclosure handle the complete pattern. The CSS-only navbar is great for marketing sites; complex apps benefit from accessible component libraries.</p>
'''

ANSWERS[41] = r'''
<p>The <code>will-change</code> property hints to the browser that an element will be animated &mdash; allowing it to optimize ahead of time by promoting the element to its own composite layer. Used judiciously, it can fix janky animations; misused, it bloats memory and hurts performance.</p>

<pre><code>.box {
  will-change: transform, opacity;
}

.box.hidden {
  transform: translateY(-100%);
  opacity: 0;
}</code></pre>

<p><strong>What it does technically:</strong></p>
<ul>
  <li>Hints the browser to allocate a separate composite layer for the element.</li>
  <li>Allows the GPU to handle the listed properties without re-rasterizing.</li>
  <li>Prevents janky frames during the first animation cycle (the "warmup" lag).</li>
</ul>

<p><strong>When to use it:</strong></p>
<ul>
  <li>An element will animate <code>transform</code> or <code>opacity</code> on user interaction.</li>
  <li>You see jank on the first interaction (hover, click) but smooth performance on subsequent ones.</li>
  <li>Profile shows long paint or composite times during the first frame.</li>
</ul>

<p><strong>Common misuse:</strong></p>

<pre><code>/* WRONG — will-change on every element pre-emptively */
* {
  will-change: transform;       /* allocates layers for everything! */
}

/* WRONG — leaving will-change on after animation */
.modal {
  will-change: opacity;
  transition: opacity 0.3s;
}
/* The modal stays optimized forever, eating memory */</code></pre>

<p>Each <code>will-change</code> usage allocates GPU memory. On every element &mdash; or even many elements &mdash; you&rsquo;re asking the browser for far more memory than necessary. Memory pressure causes worse performance than the optimization saves.</p>

<p><strong>Best practice: enable just before animation, remove after:</strong></p>
<pre><code>.box {
  /* No will-change in the base style */
}

.box:hover {
  will-change: transform;       /* enable just before animation */
  transform: scale(1.05);
}

/* Or with JS for one-time animations */
element.style.willChange = "transform";
element.addEventListener("transitionend", () =&gt; {
  element.style.willChange = "auto";   /* remove after */
});</code></pre>

<p><strong>Values that <code>will-change</code> accepts:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>auto</code> (default)</td><td>No hints; browser optimizes normally</td></tr>
  <tr><td><code>scroll-position</code></td><td>Element will scroll</td></tr>
  <tr><td><code>contents</code></td><td>Element&rsquo;s content will change</td></tr>
  <tr><td>Any property name (e.g. <code>transform</code>)</td><td>That property will change</td></tr>
</table>

<p><strong>Properties that benefit most</strong> from will-change optimization:</p>
<ul>
  <li><code>transform</code> &mdash; offloaded to GPU, cheap to animate.</li>
  <li><code>opacity</code> &mdash; same.</li>
  <li><code>filter</code> &mdash; expensive without GPU, cheap with.</li>
  <li><code>scroll-position</code> &mdash; for elements with custom scrolling.</li>
</ul>

<p><strong>Properties that should NOT use will-change:</strong></p>
<ul>
  <li><code>width</code>, <code>height</code>, <code>top</code>, <code>margin</code> &mdash; these trigger layout recalculation regardless of layer status. <code>will-change</code> doesn&rsquo;t help.</li>
</ul>

<p><strong>The composite layer trade-off:</strong></p>
<table>
  <tr><th>Pro</th><th>Con</th></tr>
  <tr><td>Faster animations of <code>transform</code>/<code>opacity</code></td><td>More GPU memory used</td></tr>
  <tr><td>No "first-frame jank"</td><td>Initial layer creation has cost</td></tr>
  <tr><td>Animations don&rsquo;t cause repaint of surroundings</td><td>Total page memory increases</td></tr>
</table>

<p><strong>Alternative: implicit layer creation</strong></p>

<p>Several CSS properties create composite layers automatically:</p>
<ul>
  <li><code>transform: translate3d(0, 0, 0)</code> or <code>translateZ(0)</code> &mdash; the "layer hack."</li>
  <li><code>opacity</code> less than 1.</li>
  <li><code>position: fixed</code>.</li>
  <li><code>filter</code>.</li>
</ul>

<p>The <code>translateZ(0)</code> hack predates <code>will-change</code> &mdash; same effect (force GPU layer) but always on. <code>will-change</code> is the modern, hint-only version that the browser can ignore if memory is tight.</p>

<p><strong>Diagnosing animation performance:</strong></p>
<ol>
  <li>Open DevTools &rarr; Performance &rarr; record an animation.</li>
  <li>Look for "Long Tasks" or paint/layout work during the animation.</li>
  <li>If paint dominates, try <code>will-change: transform</code> on the animated element.</li>
  <li>If layout dominates, switch to GPU-friendly properties (<code>transform</code> instead of <code>top</code>).</li>
  <li>Re-profile and confirm improvement.</li>
</ol>

<p><strong>Rule of thumb:</strong> reach for <code>will-change</code> only after you&rsquo;ve identified jank, profiled it, and confirmed the issue is paint or composite time. Pre-optimization with <code>will-change</code> nearly always causes more problems than it solves.</p>
'''

ANSWERS[42] = r'''
<p>An accordion shows collapsible sections where clicking a header reveals/hides content. The cleanest CSS-only approach uses native <code>&lt;details&gt;</code> + <code>&lt;summary&gt;</code> &mdash; correct ARIA, keyboard support, and find-in-page integration come for free.</p>

<pre><code>&lt;div class="accordion"&gt;
  &lt;details name="faq"&gt;
    &lt;summary&gt;What is your return policy?&lt;/summary&gt;
    &lt;p&gt;30-day returns on unopened products...&lt;/p&gt;
  &lt;/details&gt;
  &lt;details name="faq"&gt;
    &lt;summary&gt;How long does shipping take?&lt;/summary&gt;
    &lt;p&gt;Standard shipping is 3-5 business days...&lt;/p&gt;
  &lt;/details&gt;
  &lt;details name="faq"&gt;
    &lt;summary&gt;Do you ship internationally?&lt;/summary&gt;
    &lt;p&gt;Yes, to over 50 countries...&lt;/p&gt;
  &lt;/details&gt;
&lt;/div&gt;

&lt;style&gt;
  .accordion details {
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 0.5em;
    overflow: hidden;
  }
  .accordion summary {
    padding: 1em 1.5em;
    cursor: pointer;
    background: #f8f9fa;
    list-style: none;          /* remove default triangle */
    font-weight: 600;
    user-select: none;
    position: relative;
    padding-right: 2.5em;
  }
  /* Hide the marker on Safari */
  .accordion summary::-webkit-details-marker { display: none; }

  /* Custom +/- indicator */
  .accordion summary::after {
    content: "+";
    position: absolute;
    right: 1em;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.4em;
    transition: transform 0.2s;
  }
  .accordion details[open] summary::after {
    content: "&minus;";
  }

  .accordion summary:hover {
    background: #e9ecef;
  }
  .accordion details[open] summary {
    border-bottom: 1px solid #ddd;
  }
  .accordion details &gt; *:not(summary) {
    padding: 1em 1.5em;
    margin: 0;
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>name</code> attribute (added 2024)</strong> creates exclusive accordions &mdash; opening one auto-closes others sharing the name:</p>

<pre><code>&lt;details name="faq"&gt;...&lt;/details&gt;
&lt;details name="faq"&gt;...&lt;/details&gt;
&lt;details name="faq"&gt;...&lt;/details&gt;
&lt;!-- Only one can be open at a time --&gt;</code></pre>

<p>Without <code>name</code>, multiple sections can be open simultaneously. Both modes have their place &mdash; UX choice.</p>

<p><strong>Built-in benefits of <code>&lt;details&gt;</code>:</strong></p>
<ul>
  <li>Keyboard accessible by default (Enter, Space).</li>
  <li>Screen readers announce as "disclosure widget, collapsed/expanded."</li>
  <li>Browser&rsquo;s find-in-page (Ctrl+F) auto-expands sections containing matches.</li>
  <li><code>toggle</code> event fires on state change &mdash; track in JS.</li>
  <li>Open by default with <code>open</code> attribute.</li>
</ul>

<p><strong>Animating expand/collapse</strong> &mdash; surprisingly tricky historically because <code>height: auto</code> can&rsquo;t be animated directly. Modern solutions:</p>

<p><strong>Method 1: <code>::details-content</code></strong> (well-supported in 2026 Chromium):</p>
<pre><code>.accordion details::details-content {
  height: 0;
  overflow: hidden;
  transition: height 0.3s ease, content-visibility 0.3s allow-discrete;
}
.accordion details[open]::details-content {
  height: auto;
}
.accordion details {
  interpolate-size: allow-keywords;     /* enable height: auto interpolation */
}</code></pre>

<p>Native disclosure animations &mdash; nothing else needed.</p>

<p><strong>Method 2: <code>interpolate-size</code></strong> (2024+) for <code>height: auto</code> animations:</p>
<pre><code>:root {
  interpolate-size: allow-keywords;
}

.accordion details {
  height: auto;
  overflow: hidden;
  transition: height 0.3s;
}
.accordion details:not([open]) {
  height: 2.5em;          /* approximately summary height */
}</code></pre>

<p><strong>Method 3: <code>max-height</code> hack</strong> for older browsers:</p>
<pre><code>.accordion details {
  max-height: 3em;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.accordion details[open] {
  max-height: 1000px;     /* generously larger than expected content */
}</code></pre>

<p>Trick: animate <code>max-height</code> to a value larger than the content. Works on all browsers but has the trade-off that very long content has visible delay reaching its target.</p>

<p><strong>Custom JavaScript accordion</strong> &mdash; for richer control:</p>
<pre><code>&lt;div class="js-accordion"&gt;
  &lt;button class="trigger" aria-expanded="false" aria-controls="panel-1"&gt;
    Section 1
  &lt;/button&gt;
  &lt;div id="panel-1" class="panel" hidden&gt;
    Content...
  &lt;/div&gt;
&lt;/div&gt;</code></pre>

<p>Triggers update <code>aria-expanded</code> and toggle <code>hidden</code> on the panel; CSS handles transitions. Libraries like Radix UI and Headless UI provide the full ARIA model with rich animation support.</p>

<p><strong>Why prefer <code>&lt;details&gt;</code> for most cases:</strong></p>
<table>
  <tr><th>Feature</th><th><code>&lt;details&gt;</code></th><th>Custom div+button</th></tr>
  <tr><td>Keyboard accessibility</td><td>Free</td><td>Manual</td></tr>
  <tr><td>Screen reader support</td><td>Free</td><td>Manual ARIA</td></tr>
  <tr><td>Find-in-page integration</td><td>Free</td><td>Doesn&rsquo;t work</td></tr>
  <tr><td>Animation</td><td>Native (2026 baseline)</td><td>Custom JS/CSS</td></tr>
  <tr><td>Code size</td><td>Tiny</td><td>Larger</td></tr>
</table>

<p>The <code>&lt;details&gt;</code> element is one of HTML&rsquo;s most underutilized elements &mdash; a polished accordion in 5 lines.</p>
'''

ANSWERS[43] = r'''
<p>Margin collapsing is a behavior unique to vertical margins between block elements: adjacent margins merge into a single margin equal to the largest of them, rather than adding up. Padding never collapses &mdash; padding values always add as expected.</p>

<table>
  <tr><th></th><th>Margin</th><th>Padding</th></tr>
  <tr><td>Collapses with adjacent siblings</td><td>Yes (vertical only)</td><td>No</td></tr>
  <tr><td>Collapses with parent</td><td>Yes (in some cases)</td><td>No</td></tr>
  <tr><td>Visible space</td><td>Largest of the two</td><td>Sum of both</td></tr>
</table>

<p><strong>Example: vertical margin between siblings:</strong></p>
<pre><code>&lt;p&gt;First paragraph&lt;/p&gt;
&lt;p&gt;Second paragraph&lt;/p&gt;

&lt;style&gt;
  p:first-child { margin-bottom: 30px; }
  p:last-child  { margin-top:    20px; }
&lt;/style&gt;
/* Visible gap = 30px (NOT 50px!) — the larger of the two wins */</code></pre>

<p><strong>Three margin-collapse scenarios:</strong></p>

<p><strong>1. Adjacent siblings:</strong></p>
<pre><code>.first  { margin-bottom: 30px; }
.second { margin-top:    20px; }
/* Combined gap = 30px */</code></pre>

<p><strong>2. Parent and first/last child</strong> &mdash; child&rsquo;s margin escapes to the parent:</p>
<pre><code>&lt;div class="parent"&gt;
  &lt;p class="child"&gt;Hello&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent { background: lightblue; }
  .child  { margin-top: 20px; background: orange; }
&lt;/style&gt;
/* The 20px margin "escapes" — pushes .parent down, not the .child within */</code></pre>

<p>The child&rsquo;s top margin appears to come out the top of the parent. The parent&rsquo;s background color shows below where the margin would have been &mdash; confusing but standard behavior.</p>

<p><strong>3. Empty blocks:</strong></p>
<pre><code>&lt;div&gt;&lt;/div&gt;       &lt;!-- empty, with margin: 20px --&gt;
/* The element's own top and bottom margins collapse together */</code></pre>

<p>An empty block&rsquo;s top and bottom margins collapse with each other, leaving a single margin.</p>

<p><strong>How to PREVENT margin collapse:</strong></p>
<table>
  <tr><th>Technique</th><th>Why it works</th></tr>
  <tr><td><code>display: flex</code> on parent</td><td>Flex container creates a new formatting context</td></tr>
  <tr><td><code>display: grid</code> on parent</td><td>Same &mdash; new formatting context</td></tr>
  <tr><td><code>overflow: hidden</code> (or <code>auto</code>)</td><td>Establishes block formatting context (BFC)</td></tr>
  <tr><td>Add padding or border</td><td>Separates the elements; prevents direct adjacency</td></tr>
  <tr><td><code>position: absolute</code> on element</td><td>Removes from flow, no collapse</td></tr>
</table>

<pre><code>.parent {
  display: flex;
  flex-direction: column;
  gap: 1em;
  /* Children no longer collapse — flex doesn't do margin collapse */
}</code></pre>

<p><strong>Modern best practice: use <code>gap</code></strong> &mdash; flex and grid <code>gap</code> property avoids margin-collapse confusion entirely:</p>
<pre><code>.stack {
  display: flex;
  flex-direction: column;
  gap: 1em;          /* always 1em between children, no surprises */
}</code></pre>

<p>Many design systems (Tailwind, Radix) prefer this over margin-based stacking precisely to avoid margin collapse&rsquo;s edge cases.</p>

<p><strong>The historical "lobotomized owl" technique:</strong></p>
<pre><code>* + * { margin-top: 1em; }
/* Adds top margin to every element except the first */</code></pre>

<p>Heydon Pickering&rsquo;s famous selector &mdash; "anything that follows anything" &mdash; was the standard solution before <code>gap</code>. Still works, but <code>display: flex; gap: 1em</code> is cleaner.</p>

<p><strong>Padding never has these issues:</strong></p>
<pre><code>.first  { padding-bottom: 30px; }
.second { padding-top:    20px; }
/* Visible gap = 50px — padding always adds */</code></pre>

<p>Padding is contained within the element&rsquo;s box. It never escapes; it never combines with adjacent boxes.</p>

<p><strong>Why margin collapse was designed:</strong> the original CSS designers wanted vertical rhythm in text-heavy documents. Setting <code>margin-bottom</code> on paragraphs would otherwise cause double-spacing where one heading meets the next paragraph. Collapse keeps the rhythm consistent.</p>

<p>Modern apps with grid and flex layouts rarely need this behavior &mdash; <code>gap</code> handles spacing more predictably. For long-form content (blogs, docs), margin collapse still serves the original purpose well.</p>
'''

ANSWERS[44] = r'''
<p>A CSS-only modal popup uses the <code>:target</code> pseudo-class or hidden checkbox to track open state, plus <code>position: fixed</code> for the overlay. Modern HTML provides <code>&lt;dialog&gt;</code> + the Popover API for proper accessibility &mdash; usually the better choice.</p>

<p><strong>Method 1: <code>:target</code> &mdash; URL fragment opens the modal:</strong></p>
<pre><code>&lt;a href="#contact-modal"&gt;Open Modal&lt;/a&gt;

&lt;div id="contact-modal" class="modal"&gt;
  &lt;div class="modal-backdrop"&gt;&lt;/div&gt;
  &lt;div class="modal-content"&gt;
    &lt;h2&gt;Contact Us&lt;/h2&gt;
    &lt;p&gt;Form content...&lt;/p&gt;
    &lt;a href="#" class="close"&gt;Close&lt;/a&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .modal {
    display: none;
  }
  .modal:target {
    display: flex;
    position: fixed;
    inset: 0;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
  }
  .modal-content {
    position: relative;
    background: white;
    padding: 2em;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }
  .close {
    position: absolute;
    top: 1em;
    right: 1em;
    font-size: 1.5em;
    text-decoration: none;
    color: #999;
  }
&lt;/style&gt;</code></pre>

<p><code>:target</code> matches when the URL fragment (after <code>#</code>) matches the element&rsquo;s ID. The link <code>href="#contact-modal"</code> opens the modal; <code>href="#"</code> closes it (clears the fragment).</p>

<p><strong>Method 2: Hidden checkbox</strong> &mdash; track open state without URL changes:</p>
<pre><code>&lt;input type="checkbox" id="modal-toggle" hidden&gt;
&lt;label for="modal-toggle" class="open-btn"&gt;Open Modal&lt;/label&gt;

&lt;div class="modal"&gt;
  &lt;label for="modal-toggle" class="modal-backdrop"&gt;&lt;/label&gt;
  &lt;div class="modal-content"&gt;
    &lt;label for="modal-toggle" class="close"&gt;&times;&lt;/label&gt;
    &lt;h2&gt;Contact Us&lt;/h2&gt;
    &lt;p&gt;Form content...&lt;/p&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .modal {
    display: none;
  }
  #modal-toggle:checked ~ .modal {
    display: flex;
    /* same modal styles as above */
  }
&lt;/style&gt;</code></pre>

<p>Clicking the label toggles the checkbox, which CSS reads via <code>:checked</code>. The backdrop label closes the modal when clicked.</p>

<p><strong>Method 3 (recommended): native <code>&lt;dialog&gt;</code></strong> &mdash; proper accessibility built in:</p>
<pre><code>&lt;button onclick="contactModal.showModal()"&gt;Open Modal&lt;/button&gt;

&lt;dialog id="contactModal"&gt;
  &lt;form method="dialog"&gt;
    &lt;h2&gt;Contact Us&lt;/h2&gt;
    &lt;p&gt;Form content...&lt;/p&gt;
    &lt;button&gt;Close&lt;/button&gt;
  &lt;/form&gt;
&lt;/dialog&gt;

&lt;style&gt;
  dialog {
    border: none;
    border-radius: 8px;
    padding: 2em;
    max-width: 500px;
    width: 90%;
  }
  dialog::backdrop {
    background: rgba(0, 0, 0, 0.5);
  }
&lt;/style&gt;</code></pre>

<p>The <code>&lt;dialog&gt;</code> element provides:</p>
<ul>
  <li><code>::backdrop</code> pseudo-element for the overlay.</li>
  <li>Escape key closes the modal automatically.</li>
  <li>Focus moves into the modal on open; returns to trigger on close.</li>
  <li>Renders in the top layer &mdash; above all z-index stacks.</li>
  <li>Form with <code>method="dialog"</code> closes the modal on submit.</li>
  <li>Proper ARIA roles built in (<code>role="dialog"</code>, <code>aria-modal="true"</code>).</li>
</ul>

<p><strong>Animating the dialog:</strong></p>
<pre><code>dialog {
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.2s, transform 0.2s, display 0.2s allow-discrete;
}

dialog[open] {
  opacity: 1;
  transform: scale(1);
}

@starting-style {
  dialog[open] {
    opacity: 0;
    transform: scale(0.95);
  }
}

dialog::backdrop {
  background: rgba(0, 0, 0, 0);
  transition: background 0.2s;
}
dialog[open]::backdrop {
  background: rgba(0, 0, 0, 0.5);
}</code></pre>

<p>The <code>@starting-style</code> rule (2026 baseline) defines initial values for entry transitions &mdash; previously required JavaScript. The <code>display: allow-discrete</code> transition behavior animates between <code>none</code> and <code>block</code> states.</p>

<p><strong>Accessibility comparison:</strong></p>
<table>
  <tr><th>Feature</th><th>CSS-only modal</th><th><code>&lt;dialog&gt;</code></th></tr>
  <tr><td>Keyboard focus management</td><td>Manual</td><td>Built-in</td></tr>
  <tr><td>Escape to close</td><td>Manual JS</td><td>Built-in</td></tr>
  <tr><td>Focus trap (can&rsquo;t Tab out)</td><td>Manual</td><td>Built-in (with <code>showModal()</code>)</td></tr>
  <tr><td>ARIA roles</td><td>Manual</td><td>Built-in</td></tr>
  <tr><td>Top-layer rendering</td><td>z-index battle</td><td>Built-in</td></tr>
</table>

<p>For production modals with form inputs, <code>&lt;dialog&gt;</code> + a small JS helper is the modern choice. The CSS-only approach is fine for simple "click to view" overlays without form interactions.</p>
'''

ANSWERS[45] = r'''
<p><code>float</code> was the dominant CSS layout technique from 1996 to ~2015 &mdash; before Flexbox and Grid existed. Originally designed to flow text around images (think magazines), developers co-opted it for entire page layouts. Today it&rsquo;s mostly a legacy property; modern CSS uses Grid and Flex instead.</p>

<pre><code>img.float-left {
  float: left;
  margin: 0 1em 1em 0;
  /* Text wraps around the image */
}

img.float-right {
  float: right;
  margin: 0 0 1em 1em;
}</code></pre>

<p>The remaining valid use case &mdash; magazine-style images with text wrapping around them &mdash; is what <code>float</code> was designed for. CSS Grid and Flex don&rsquo;t do text wrapping.</p>

<p><strong>Float values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>none</code></td><td>Default; no floating</td></tr>
  <tr><td><code>left</code></td><td>Element shifts to the left; content wraps right</td></tr>
  <tr><td><code>right</code></td><td>Element shifts to the right; content wraps left</td></tr>
  <tr><td><code>inline-start</code> / <code>inline-end</code></td><td>Logical equivalents (RTL-aware)</td></tr>
</table>

<p><strong>How floats affect surrounding content:</strong></p>
<ul>
  <li>The floated element is taken out of normal flow horizontally.</li>
  <li>Inline content (text, inline images) wraps around it.</li>
  <li>Block content acts as if the float doesn&rsquo;t exist for layout purposes.</li>
  <li>The parent container collapses to zero height if it has no other content (the famous "collapse" problem).</li>
</ul>

<p><strong>The legacy "float layout" pattern</strong> (DON&rsquo;T USE for new code):</p>
<pre><code>.layout::after {
  content: "";
  display: block;
  clear: both;     /* clearfix — restore parent height */
}
.sidebar  { float: left;  width: 25%; }
.main     { float: left;  width: 70%; }
.right    { float: right; width: 25%; }</code></pre>

<p>Three floated columns make up a 3-column page layout. The <code>::after</code> "clearfix" trick prevents the parent from collapsing. This was state-of-the-art in 2010; today it&rsquo;s archaeological code.</p>

<p><strong>Why floats failed for layout:</strong></p>
<ul>
  <li>Manual width math (must add to 100%).</li>
  <li>No vertical alignment.</li>
  <li>Source order = visual order (no reordering).</li>
  <li>"Clearfix" required to restore container heights.</li>
  <li>Equal-height columns required hacks.</li>
  <li>No gap support &mdash; spacing required precise margin tricks.</li>
</ul>

<p>Flexbox (2014) and Grid (2017) solved all of this. Floats remain only for the original use case: text-wrap around images.</p>

<p><strong>The <code>shape-outside</code> property</strong> &mdash; modern enhancement to floats:</p>
<pre><code>img.organic-wrap {
  float: left;
  shape-outside: circle(50%);
  /* Text wraps in a circular outline rather than rectangular */
  margin: 1em;
  width: 200px;
  height: 200px;
  border-radius: 50%;
}</code></pre>

<p>Text now wraps around the circular shape, not the rectangular bounding box. Combine with images, polygons, even SVG paths for organic text flows.</p>

<p><strong>Modern best practices:</strong></p>
<table>
  <tr><th>Need</th><th>Old: float</th><th>New: modern CSS</th></tr>
  <tr><td>Text wraps around image</td><td>float</td><td>float (still the only option)</td></tr>
  <tr><td>Multi-column layout</td><td>float + clearfix</td><td>Grid</td></tr>
  <tr><td>Sidebar + content</td><td>float</td><td>Grid or Flex</td></tr>
  <tr><td>Horizontal nav menu</td><td>float</td><td>Flex</td></tr>
  <tr><td>Equal-height columns</td><td>Float hacks</td><td>Grid (automatic)</td></tr>
</table>

<p><strong>If you encounter floats in legacy code:</strong></p>
<ul>
  <li>Look for <code>::after { content: ""; clear: both; display: block; }</code> &mdash; that&rsquo;s a clearfix.</li>
  <li>Look for <code>.row::before, .row::after { content: ""; display: table; clear: both; }</code> &mdash; another clearfix variant.</li>
  <li>Common in Bootstrap 3 era code (~2014); replaced in Bootstrap 4+ with Flexbox.</li>
</ul>

<p>Don&rsquo;t reach for <code>float</code> for layout in 2026. Use Grid for two-dimensional structures (page layouts, dashboards), Flex for one-dimensional rows (navbars, toolbars), and reserve floats for actual text-wrap-around-image use cases &mdash; the only place they still excel.</p>
'''

ANSWERS[46] = r'''
<p>Floats remove an element from normal flow horizontally but leave a "ghost" that affects subsequent content. Without clearing, the parent container collapses to zero height (because all children are floated out of flow), and following elements wrap around the floats unexpectedly. Clearing restores normal flow.</p>

<p><strong>The collapsing-parent problem:</strong></p>
<pre><code>&lt;div class="parent"&gt;
  &lt;div class="float-child"&gt;Floated&lt;/div&gt;
  &lt;div class="float-child"&gt;Floated&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent { background: lightblue; }
  .float-child { float: left; width: 100px; height: 100px; }
&lt;/style&gt;</code></pre>

<p><strong>Without clearing</strong>: <code>.parent</code> collapses to zero height. The blue background is invisible because there&rsquo;s no parent height to color &mdash; even though visually the floats fill space.</p>

<p><strong>Three classic ways to clear floats:</strong></p>

<p><strong>1. <code>clear</code> property on a following element</strong> &mdash; the original approach:</p>
<pre><code>&lt;div class="parent"&gt;
  &lt;div class="float-child"&gt;Floated&lt;/div&gt;
  &lt;div class="float-child"&gt;Floated&lt;/div&gt;
  &lt;div class="clear"&gt;&lt;/div&gt;       &lt;!-- clearing element --&gt;
&lt;/div&gt;

&lt;style&gt;
  .clear { clear: both; }
&lt;/style&gt;</code></pre>

<p>Adding an empty div with <code>clear: both</code> after the floats forces the parent to extend to contain everything. Works but adds non-semantic markup.</p>

<table>
  <tr><th><code>clear</code> value</th><th>Effect</th></tr>
  <tr><td><code>none</code></td><td>Default; element flows next to floats</td></tr>
  <tr><td><code>left</code></td><td>Element placed below any left-floated</td></tr>
  <tr><td><code>right</code></td><td>Element placed below any right-floated</td></tr>
  <tr><td><code>both</code></td><td>Element placed below all floats</td></tr>
</table>

<p><strong>2. The classic clearfix</strong> &mdash; pseudo-element trick:</p>
<pre><code>.clearfix::after {
  content: "";
  display: block;
  clear: both;
}

.parent { /* (becomes a clearfix container) */ }</code></pre>

<p>An invisible <code>::after</code> element is generated; its <code>clear: both</code> pushes the parent&rsquo;s computed height past all floats. No extra HTML required.</p>

<p><strong>3. Modern: establish a Block Formatting Context (BFC)</strong> &mdash; the cleanest approach:</p>
<pre><code>.parent {
  display: flow-root;
  /* Or any of these (with side effects): */
  /* overflow: hidden; */
  /* display: flex; */
  /* display: grid; */
}</code></pre>

<p><code>display: flow-root</code> creates a new BFC with no other side effects &mdash; the parent now contains its floats fully. Cleaner than <code>overflow: hidden</code> (which can clip content) or <code>display: flex</code> (which changes layout entirely).</p>

<p><strong>Why each works mechanically:</strong></p>
<ul>
  <li><strong>BFC (Block Formatting Context)</strong> is a layout containment region. Inside a BFC, floats <em>are</em> contained &mdash; they don&rsquo;t escape the parent&rsquo;s height calculation.</li>
  <li>By default, the body and other normal block elements don&rsquo;t establish BFCs &mdash; that&rsquo;s why floats escape.</li>
  <li><code>display: flow-root</code> is the modern explicit way to create a BFC.</li>
  <li>Older techniques (<code>overflow: hidden</code>, <code>display: table</code>, etc.) also create BFCs but with side effects.</li>
</ul>

<p><strong>Why this matters for legacy code:</strong></p>
<table>
  <tr><th>Pattern in old CSS</th><th>What it did</th></tr>
  <tr><td><code>.row::after { clear: both; ... }</code></td><td>Bootstrap 3 clearfix</td></tr>
  <tr><td><code>.row { overflow: hidden; }</code></td><td>BFC trick (with potential clipping)</td></tr>
  <tr><td><code>.row::before, .row::after { ... }</code></td><td>Belt-and-suspenders clearfix</td></tr>
</table>

<p>If you see these patterns in old code, they&rsquo;re clearing floats. Modern equivalent: replace floats with Flex/Grid; clearfix becomes unnecessary.</p>

<p><strong>For new code in 2026, almost certainly avoid floats entirely:</strong></p>
<pre><code>/* OLD: float-based row */
.row {
  display: flow-root;       /* clear floats inside */
}
.row .col {
  float: left;
  width: 33.33%;
}

/* NEW: flexbox row */
.row {
  display: flex;
  gap: 1em;
}
.row .col {
  flex: 1;
}</code></pre>

<p>The new code: shorter, more flexible, no clearing concerns, supports <code>gap</code>, equal heights for free.</p>

<p><strong>The remaining valid clearfix scenario:</strong> if you have floats for text-wrap-around-image (<code>shape-outside</code> use case), and the parent contains both wrapped text and the floated image, no clearfix is needed &mdash; the text already establishes the parent&rsquo;s height. Clearfix is only required when floats are the only content.</p>

<p>For the rare case you do need clearfix: <code>display: flow-root</code> on the parent is the cleanest, modern answer. Only fall back to <code>::after { clear: both }</code> if supporting truly ancient browsers.</p>
'''

ANSWERS[47] = r'''
<p>CSS specificity is the algorithm that determines which CSS rule wins when multiple rules target the same element. Higher specificity wins; ties break by source order. Calculating it correctly is essential for predictable styling.</p>

<p><strong>The specificity calculation</strong>: count the selector components in four categories:</p>

<table>
  <tr><th>Column</th><th>What counts</th><th>Weight</th></tr>
  <tr><td>1 (highest)</td><td>Inline styles (<code>style="..."</code>)</td><td>1000</td></tr>
  <tr><td>2</td><td>IDs (<code>#header</code>)</td><td>100 each</td></tr>
  <tr><td>3</td><td>Classes, attributes, pseudo-classes (<code>.btn</code>, <code>[type=text]</code>, <code>:hover</code>)</td><td>10 each</td></tr>
  <tr><td>4 (lowest)</td><td>Elements, pseudo-elements (<code>p</code>, <code>::before</code>)</td><td>1 each</td></tr>
</table>

<p>Specificity is written as <code>(a, b, c, d)</code> where a/b/c/d are the counts of each category.</p>

<p><strong>Examples:</strong></p>
<table>
  <tr><th>Selector</th><th>Specificity</th></tr>
  <tr><td><code>p</code></td><td>(0, 0, 0, 1)</td></tr>
  <tr><td><code>p span</code></td><td>(0, 0, 0, 2)</td></tr>
  <tr><td><code>.error</code></td><td>(0, 0, 1, 0)</td></tr>
  <tr><td><code>p.error</code></td><td>(0, 0, 1, 1)</td></tr>
  <tr><td><code>p:hover</code></td><td>(0, 0, 1, 1)</td></tr>
  <tr><td><code>[data-x="y"]</code></td><td>(0, 0, 1, 0)</td></tr>
  <tr><td><code>nav .item</code></td><td>(0, 0, 1, 1)</td></tr>
  <tr><td><code>.menu .item.active</code></td><td>(0, 0, 3, 0)</td></tr>
  <tr><td><code>#header</code></td><td>(0, 1, 0, 0)</td></tr>
  <tr><td><code>#header .nav</code></td><td>(0, 1, 1, 0)</td></tr>
  <tr><td><code>style="..."</code></td><td>(1, 0, 0, 0)</td></tr>
  <tr><td><code>!important</code></td><td>overrides everything in same origin</td></tr>
</table>

<p><strong>Comparison rule:</strong> compare left to right. The first non-zero column wins; counts in lower columns don&rsquo;t matter.</p>

<pre><code>.x.y.z         (0,0,3,0)   /* three classes */
p#main         (0,1,0,1)   /* one ID + one element — wins */
/* (0,1,...) beats (0,0,...) regardless of column 3 counts */</code></pre>

<p><strong>The IDs > classes rule:</strong> a single ID outranks any number of classes, attributes, or pseudo-classes. <code>#main</code> beats <code>.btn.active.large.primary</code> because IDs sit in column 2.</p>

<p><strong>Special selectors and specificity:</strong></p>
<table>
  <tr><th>Selector</th><th>Specificity</th></tr>
  <tr><td><code>*</code></td><td>(0, 0, 0, 0) &mdash; no contribution</td></tr>
  <tr><td><code>:is(a, .b)</code></td><td>Highest of arguments &mdash; <code>.b</code> here</td></tr>
  <tr><td><code>:where(...)</code></td><td>Always 0 &mdash; useful for low-specificity defaults</td></tr>
  <tr><td><code>:not(.b)</code></td><td>Same as <code>.b</code></td></tr>
  <tr><td><code>:has(.b)</code></td><td>Same as <code>.b</code></td></tr>
  <tr><td><code>::before</code></td><td>(0, 0, 0, 1) &mdash; element-level</td></tr>
</table>

<p><strong>The <code>:where()</code> trick:</strong></p>
<pre><code>/* This rule has 0 specificity — easy to override */
:where(.card) p {
  margin-bottom: 1em;
}

/* Override doesn't need higher specificity */
.card p {
  margin-bottom: 0;     /* wins because :where contributes 0 */
}</code></pre>

<p><code>:where()</code> is essential for design system base styles &mdash; you set defaults that consumers can override without specificity wars.</p>

<p><strong>Inline styles and <code>!important</code>:</strong></p>
<pre><code>&lt;p style="color: red;"&gt;...&lt;/p&gt;        &lt;!-- (1,0,0,0) wins over CSS --&gt;

/* Only !important can override inline */
p { color: blue !important; }

/* But !important on inline still wins */
&lt;p style="color: red !important;"&gt;...&lt;/p&gt;
/* This wins over external !important */</code></pre>

<p>The order of precedence with <code>!important</code> reverses: user-agent < user < author < author <code>!important</code> < user <code>!important</code>. Avoid <code>!important</code> in author CSS &mdash; it makes overrides exponentially harder.</p>

<p><strong>Cascade layers (2026 baseline)</strong> override specificity entirely:</p>
<pre><code>@layer reset, base, components, utilities;

@layer base { p { color: gray; } }
@layer components { p.error { color: red; } }
@layer utilities { p { color: blue; } }    /* wins over both */</code></pre>

<p>Later-declared layers always win over earlier layers, regardless of specificity. <code>p</code> in utilities (specificity 1) beats <code>p.error</code> in components (specificity 11) because layers stack independently.</p>

<p><strong>Specificity wars and how to avoid them:</strong></p>
<ul>
  <li>Prefer single-class selectors (<code>.btn-primary</code>) over deep nesting (<code>nav .menu .button</code>).</li>
  <li>Use cascade layers to organize architecture.</li>
  <li>Use <code>:where()</code> for low-specificity defaults.</li>
  <li>Reserve <code>!important</code> for utility classes only (Tailwind philosophy).</li>
  <li>Avoid IDs in CSS unless necessary (they&rsquo;re hard to override).</li>
  <li>Use class composition: <code>.btn.btn-primary.btn-large</code>, all single-class &mdash; predictable, layerable.</li>
</ul>

<p>Modern CSS architecture (BEM, ITCSS, design tokens) tries hard to keep specificity low and predictable. Specificity wars are a sign of architectural debt.</p>
'''

ANSWERS[48] = r'''
<p>A CSS-only carousel uses <code>scroll-snap</code> for native swipe-and-snap behavior &mdash; no JavaScript needed for basic functionality. Add <code>:target</code> or hidden checkboxes for navigation buttons; for full features (autoplay, indicators, infinite loop), JavaScript libraries are still standard.</p>

<pre><code>&lt;div class="carousel"&gt;
  &lt;img src="1.jpg" alt="Slide 1"&gt;
  &lt;img src="2.jpg" alt="Slide 2"&gt;
  &lt;img src="3.jpg" alt="Slide 3"&gt;
  &lt;img src="4.jpg" alt="Slide 4"&gt;
&lt;/div&gt;

&lt;style&gt;
  .carousel {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    height: 400px;
  }
  .carousel img {
    flex: 0 0 100%;            /* each image takes full width */
    height: 100%;
    scroll-snap-align: start;
    object-fit: cover;
  }

  /* Hide scrollbar */
  .carousel { scrollbar-width: none; }
  .carousel::-webkit-scrollbar { display: none; }
&lt;/style&gt;</code></pre>

<p><strong>How <code>scroll-snap</code> works:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>scroll-snap-type: x mandatory</code></td><td>Snap on x-axis; mandatory snapping (always lands on a snap point)</td></tr>
  <tr><td><code>scroll-snap-type: x proximity</code></td><td>Soft snap; only when user releases near a point</td></tr>
  <tr><td><code>scroll-snap-align: start</code></td><td>Each item snaps to the start (left edge in row)</td></tr>
  <tr><td><code>scroll-snap-align: center</code></td><td>Snap centered in viewport</td></tr>
  <tr><td><code>scroll-snap-stop: always</code></td><td>One snap per gesture (no skipping)</td></tr>
  <tr><td><code>scroll-padding</code></td><td>Offset where snapping aligns</td></tr>
</table>

<p>The user swipes; the browser snaps to the next image automatically. Native, performant, accessible (keyboard arrows scroll naturally).</p>

<p><strong>Adding indicator dots:</strong></p>
<pre><code>&lt;div class="carousel-container"&gt;
  &lt;div class="carousel"&gt;
    &lt;img src="1.jpg" id="slide1" alt=""&gt;
    &lt;img src="2.jpg" id="slide2" alt=""&gt;
    &lt;img src="3.jpg" id="slide3" alt=""&gt;
  &lt;/div&gt;
  &lt;div class="indicators"&gt;
    &lt;a href="#slide1" aria-label="Slide 1"&gt;&lt;/a&gt;
    &lt;a href="#slide2" aria-label="Slide 2"&gt;&lt;/a&gt;
    &lt;a href="#slide3" aria-label="Slide 3"&gt;&lt;/a&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .indicators {
    display: flex;
    justify-content: center;
    gap: 0.5em;
    padding: 1em;
  }
  .indicators a {
    width: 12px;
    height: 12px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 50%;
    transition: background 0.2s, transform 0.2s;
  }
  .indicators a:hover { background: rgba(0, 0, 0, 0.6); }
&lt;/style&gt;</code></pre>

<p>Clicking a dot uses anchor links + smooth scrolling to navigate. The carousel scrolls to the linked image, snapping into place.</p>

<p><strong>Highlighting the current dot</strong> &mdash; this is hard in pure CSS without scroll-driven animations. Modern approach using <code>:target</code>:</p>

<pre><code>.indicators a:target {
  background: #0066cc;
  transform: scale(1.2);
}</code></pre>

<p>This works only when the URL fragment matches a slide. For real-time highlighting based on scroll position, JavaScript IntersectionObserver is required.</p>

<p><strong>Modern: scroll-driven animations</strong> for indicator highlighting (2026 Chromium):</p>
<pre><code>.indicator {
  background: rgba(0, 0, 0, 0.3);
  animation: highlight linear;
  animation-timeline: scroll(.carousel inline);
  animation-range: contain 0% contain 100%;
}

@keyframes highlight {
  to { background: #0066cc; }
}</code></pre>

<p>Each indicator&rsquo;s color depends on scroll position &mdash; perfect synchronization without JavaScript.</p>

<p><strong>Prev/Next buttons</strong> &mdash; use anchor links to specific slides:</p>
<pre><code>&lt;a href="#slide1" class="prev"&gt;&larr;&lt;/a&gt;
&lt;a href="#slide2" class="next"&gt;&rarr;&lt;/a&gt;</code></pre>

<p>Combined with <code>scroll-behavior: smooth</code>, these buttons scroll the carousel one slide at a time.</p>

<p><strong>Limitations of CSS-only carousels:</strong></p>
<table>
  <tr><th>Feature</th><th>Possible in CSS?</th></tr>
  <tr><td>Snap to slides</td><td>Yes (scroll-snap)</td></tr>
  <tr><td>Touch swipe</td><td>Yes (native scroll)</td></tr>
  <tr><td>Mouse wheel</td><td>Yes (native scroll)</td></tr>
  <tr><td>Keyboard arrow keys</td><td>Yes (native scroll)</td></tr>
  <tr><td>Prev/Next buttons</td><td>Yes (anchor links)</td></tr>
  <tr><td>Indicator dots</td><td>Yes (anchor links)</td></tr>
  <tr><td>Active dot indicator</td><td>Hard (requires JS or scroll-driven animation)</td></tr>
  <tr><td>Autoplay</td><td>No (animation property can&rsquo;t scroll)</td></tr>
  <tr><td>Infinite loop</td><td>No</td></tr>
  <tr><td>Pause on hover</td><td>Hard</td></tr>
  <tr><td>Lazy loading next slide</td><td>Yes (loading="lazy" on img)</td></tr>
</table>

<p>For carousel use cases beyond simple swipeable galleries, JavaScript libraries (Swiper.js, Embla Carousel) handle the full feature set with proper accessibility.</p>

<p><strong>Why <code>scroll-snap</code> wins for image swipers</strong>: it uses native browser scrolling, which means accessibility (keyboard, screen reader, momentum) all work for free. Custom carousels often break these &mdash; users with disabilities can&rsquo;t navigate. <code>scroll-snap</code> is the accessible default.</p>
'''

ANSWERS[49] = r'''
<p>The <code>isolation</code> property creates a new <strong>stacking context</strong> without other side effects &mdash; useful when you need z-index scoping or to fix blend-mode interactions. It&rsquo;s a tool for CSS architecture, not visible styling.</p>

<pre><code>.card {
  isolation: isolate;
}</code></pre>

<p><strong>What it does:</strong> creates a new stacking context, just like <code>opacity: 0.99</code>, <code>transform</code>, or <code>filter</code> would &mdash; but without changing the visual rendering at all.</p>

<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>auto</code> (default)</td><td>No new stacking context</td></tr>
  <tr><td><code>isolate</code></td><td>Creates a new stacking context</td></tr>
</table>

<p><strong>Why this matters: scoping z-index:</strong></p>

<pre><code>&lt;div class="card"&gt;
  &lt;div class="badge" style="z-index: 9999;"&gt;NEW&lt;/div&gt;
&lt;/div&gt;
&lt;div class="modal" style="z-index: 100;"&gt;...&lt;/div&gt;</code></pre>

<p>Without <code>isolation: isolate</code> on the card, the badge&rsquo;s z-index of 9999 might pop above the modal &mdash; unwanted! With <code>isolation: isolate</code> on the card, the badge&rsquo;s z-index is scoped to that card; the modal still sits on top.</p>

<pre><code>.card {
  isolation: isolate;       /* badge's z-index can't escape this card */
}
.badge {
  z-index: 9999;            /* now relative to .card only */
}</code></pre>

<p>This is the cleanest way to scope z-index in component-based architectures. Each component declares <code>isolation: isolate</code>; internal stacking is contained.</p>

<p><strong>Without <code>isolation</code>, you&rsquo;d use side-effect tricks:</strong></p>
<pre><code>.card { transform: translateZ(0); }      /* creates stacking context */
.card { opacity: 0.999; }                /* same effect */
.card { will-change: transform; }        /* same effect */</code></pre>

<p>These all work but have unintended consequences (GPU layer, opacity blending, memory). <code>isolation: isolate</code> is purpose-built &mdash; it does the one thing you want and nothing else.</p>

<p><strong>The other use case: containing <code>mix-blend-mode</code>:</strong></p>
<pre><code>&lt;div class="card"&gt;
  &lt;div class="text" style="mix-blend-mode: difference;"&gt;Hello&lt;/div&gt;
&lt;/div&gt;
&lt;img src="bg.jpg"&gt;</code></pre>

<p>By default, <code>mix-blend-mode</code> blends with everything below, including the background image &mdash; which is rarely what you want. <code>isolation: isolate</code> on <code>.card</code> contains the blend to within the card:</p>

<pre><code>.card {
  isolation: isolate;       /* blend-mode children only blend within .card */
}
.text {
  mix-blend-mode: difference;
  /* Now blends with siblings inside .card, not the page */
}</code></pre>

<p>This pattern is essential for components using blend modes &mdash; without isolation, blend modes leak unpredictably across the page.</p>

<p><strong>What creates a stacking context</strong> &mdash; the full list:</p>
<ul>
  <li>The root element (<code>&lt;html&gt;</code>).</li>
  <li>Positioned elements with <code>z-index: &lt;number&gt;</code>.</li>
  <li>Elements with <code>opacity</code> &lt; 1.</li>
  <li>Elements with <code>transform</code>, <code>filter</code>, <code>perspective</code>, <code>clip-path</code>, <code>mask</code>, <code>backdrop-filter</code>.</li>
  <li>Elements with <code>isolation: isolate</code>.</li>
  <li>Flex/grid items with <code>z-index: &lt;number&gt;</code>.</li>
  <li>Elements with <code>position: fixed</code> or <code>sticky</code>.</li>
  <li>Elements with <code>contain: layout</code>, <code>contain: paint</code>, or <code>contain: strict</code>.</li>
</ul>

<p><strong>When to reach for <code>isolation: isolate</code>:</strong></p>
<ul>
  <li><strong>Component libraries</strong> &mdash; each component scopes its z-index. Buttons, cards, modals all start clean.</li>
  <li><strong>Mix-blend-mode interaction</strong> &mdash; contain the blending area to a specific component.</li>
  <li><strong>Refactoring legacy CSS</strong> &mdash; replace <code>transform: translateZ(0)</code> hacks that exist solely to create a stacking context.</li>
</ul>

<p><strong>Comparison with <code>contain</code>:</strong></p>
<table>
  <tr><th>Property</th><th>What it isolates</th></tr>
  <tr><td><code>isolation: isolate</code></td><td>Stacking context only</td></tr>
  <tr><td><code>contain: layout</code></td><td>Layout calculations</td></tr>
  <tr><td><code>contain: paint</code></td><td>Painting (also creates stacking context)</td></tr>
  <tr><td><code>contain: strict</code></td><td>Layout, paint, size, style</td></tr>
</table>

<p><code>contain</code> is a performance-oriented hint; <code>isolation</code> is purely about stacking. Use the right tool for the job.</p>

<p><strong>Summary</strong>: <code>isolation: isolate</code> is the explicit, side-effect-free way to create a stacking context. Component-based design systems benefit immensely &mdash; each component contains its z-index complexity, eliminating the <code>z-index: 9999</code> arms race between unrelated components.</p>
'''

ANSWERS[50] = r'''
<p>A responsive Flexbox card layout uses <code>flex-wrap</code> with <code>flex: 1 1 250px</code> &mdash; cards reflow naturally as the viewport changes, no media queries required. Combined with <code>display: flex; flex-direction: column</code> on each card, you get equal heights with consistent button alignment.</p>

<pre><code>&lt;section class="cards"&gt;
  &lt;article class="card"&gt;
    &lt;img src="1.jpg" alt=""&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;Wireless Headphones&lt;/h3&gt;
      &lt;p&gt;Premium noise-canceling over-ear headphones.&lt;/p&gt;
      &lt;a href="#" class="btn"&gt;Shop now&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;
  &lt;article class="card"&gt;...&lt;/article&gt;
  &lt;article class="card"&gt;...&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .cards {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .card {
    flex: 1 1 280px;        /* min 280px, grow equally, wrap when needed */

    display: flex;
    flex-direction: column;  /* enable button alignment */

    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }

  .card img {
    width: 100%;
    aspect-ratio: 4 / 3;
    object-fit: cover;
  }

  .card-body {
    padding: 1.5em;
    display: flex;
    flex-direction: column;
    flex: 1;                 /* fill remaining card height */
  }

  .card h3 {
    margin: 0 0 0.5em;
  }

  .card p {
    color: #666;
    margin: 0 0 1em;
    flex: 1;                 /* push button to bottom */
  }

  .card .btn {
    align-self: start;       /* button doesn't stretch */
    background: #0066cc;
    color: white;
    padding: 0.5em 1em;
    border-radius: 4px;
    text-decoration: none;
  }
&lt;/style&gt;</code></pre>

<p><strong>The key Flexbox magic for equal heights and aligned buttons:</strong></p>
<ol>
  <li><strong>Cards row uses <code>flex-wrap: wrap</code></strong> &mdash; reflows naturally.</li>
  <li><strong>Each card is a flex column</strong> &mdash; <code>display: flex; flex-direction: column</code>.</li>
  <li><strong>Card body grows to fill</strong> &mdash; <code>flex: 1</code> on the card body.</li>
  <li><strong>Description grows inside body</strong> &mdash; <code>flex: 1</code> on the <code>&lt;p&gt;</code>; pushes the button below.</li>
  <li><strong>Button stays at the natural size</strong> &mdash; <code>align-self: start</code> prevents it from stretching.</li>
</ol>

<p>Result: cards in the same row have equal heights; buttons line up across all cards regardless of description length. The classic "uniform card grid" pattern.</p>

<p><strong>Reading <code>flex: 1 1 280px</code></strong>:</p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td><code>flex-grow: 1</code></td><td>Grow to fill remaining space</td></tr>
  <tr><td><code>flex-shrink: 1</code></td><td>Shrink if necessary</td></tr>
  <tr><td><code>flex-basis: 280px</code></td><td>Preferred starting width</td></tr>
</table>

<p>Cards start at 280px wide; if there&rsquo;s extra space in a row, they grow equally; if not enough space for another, they wrap.</p>

<p><strong>Responsive behavior</strong> across viewport sizes:</p>
<ul>
  <li><strong>Wide screen (1400px)</strong>: 5 cards per row.</li>
  <li><strong>Desktop (1200px)</strong>: 4 cards per row.</li>
  <li><strong>Tablet (900px)</strong>: 3 cards per row.</li>
  <li><strong>Small tablet (600px)</strong>: 2 cards per row.</li>
  <li><strong>Phone (320px)</strong>: 1 card per row, full width.</li>
</ul>

<p>The browser handles all of this without explicit media queries.</p>

<p><strong>Comparison with CSS Grid:</strong></p>

<pre><code>/* Grid version */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}</code></pre>

<table>
  <tr><th></th><th>Flexbox <code>flex: 1 1 280px</code></th><th>Grid <code>auto-fit + minmax</code></th></tr>
  <tr><td>Last row behavior</td><td>Items expand to fill; varies per row</td><td>Items align to grid; consistent</td></tr>
  <tr><td>Item alignment</td><td>Each row independent</td><td>Strong column alignment</td></tr>
  <tr><td>Equal heights</td><td>Items in same row align (with align-items)</td><td>Always equal heights</td></tr>
  <tr><td>Item sizes</td><td>Can grow unevenly to fill</td><td>Always equal width per row</td></tr>
</table>

<p>For uniform card grids, Grid usually produces cleaner results &mdash; cards stay consistent widths regardless of how many fit per row. Flexbox excels when items naturally vary (tags, chips) and you want them to stretch to fill rows.</p>

<p><strong>Container queries enhancement</strong> (2026):</p>
<pre><code>.card { container-type: inline-size; }

.card-body { padding: 1em; }

@container (min-width: 350px) {
  .card-body { padding: 2em; }
  .card h3   { font-size: 1.5em; }
}</code></pre>

<p>Cards adapt their internal layout based on their own width, not the viewport &mdash; identical cards in a sidebar render compact; in the main column they render generously. Same component, different presentations.</p>

<p>For card-heavy interfaces (dashboards, e-commerce, content streams), this pattern is the workhorse of responsive design.</p>
'''

ANSWERS[51] = r'''
<p>The <code>content</code> property generates <strong>content from CSS</strong> &mdash; without modifying HTML &mdash; via the <code>::before</code> and <code>::after</code> pseudo-elements. It accepts strings, attribute values, counter outputs, gradients, images, and special keywords.</p>

<table>
  <tr><th>Value type</th><th>Example</th><th>Use</th></tr>
  <tr><td>String</td><td><code>content: "&rarr;"</code></td><td>Static text/symbols</td></tr>
  <tr><td><code>attr()</code></td><td><code>content: attr(data-tip)</code></td><td>Read HTML attribute</td></tr>
  <tr><td><code>counter()</code></td><td><code>content: counter(item)</code></td><td>Numbered output</td></tr>
  <tr><td><code>url()</code></td><td><code>content: url(icon.svg)</code></td><td>Insert image</td></tr>
  <tr><td><code>none</code> / <code>""</code></td><td>Empty pseudo-element</td><td>Required to render <code>::before</code></td></tr>
  <tr><td><code>open-quote</code> / <code>close-quote</code></td><td>Localized quotes</td><td>Pairs with <code>quotes</code> property</td></tr>
</table>

<p><strong>Reading attributes &mdash; the most common pattern:</strong></p>
<pre><code>&lt;span data-tooltip="Click for details"&gt;Help&lt;/span&gt;

&lt;style&gt;
  [data-tooltip] {
    position: relative;
  }
  [data-tooltip]::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    background: #333;
    color: white;
    padding: 0.4em 0.8em;
    border-radius: 4px;
    font-size: 0.85em;
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.2s;
  }
  [data-tooltip]:hover::after {
    opacity: 1;
  }
&lt;/style&gt;</code></pre>

<p><strong>Concatenation &mdash; modern CSS supports multi-value content:</strong></p>
<pre><code>.external::after {
  content: " (" attr(href) ")";
}

.required label::after {
  content: " *" / "required field";
  /* The "/" introduces alternative text for screen readers */
}</code></pre>

<p><strong>Counters for outline lists:</strong></p>
<pre><code>ol.steps {
  list-style: none;
  counter-reset: step;
}
ol.steps li::before {
  counter-increment: step;
  content: "Step " counter(step) ": ";
  font-weight: bold;
  color: #0066cc;
}</code></pre>

<p><strong>Limitations to know:</strong></p>
<ul>
  <li><strong>Generated content is invisible to most form fields and inputs</strong> &mdash; <code>::before</code> doesn&rsquo;t work on replaced elements like <code>&lt;img&gt;</code> or <code>&lt;input&gt;</code>.</li>
  <li><strong>Screen reader behavior varies</strong> &mdash; some announce generated content, some don&rsquo;t. Use the <code>"text" / "alt text"</code> syntax to provide accessible alternatives where browser support exists.</li>
  <li><strong>Generated text isn&rsquo;t selectable</strong> &mdash; users can&rsquo;t copy it like real DOM text.</li>
  <li><strong>SEO impact</strong> &mdash; search engines may or may not index generated content.</li>
</ul>

<p>Use <code>content</code> for decorative additions (icons, prefixes, separators) and dynamic display from data attributes. Don&rsquo;t use it for content that must be selectable, indexed, or read by all assistive technologies &mdash; that belongs in HTML.</p>
'''

ANSWERS[52] = r'''
<p>A sticky footer stays at the bottom of the viewport when content is short, but pushes down naturally when content grows tall. The modern solution uses <code>min-height: 100vh</code> on the page wrapper plus Flexbox or Grid &mdash; replacing 20 years of margin/negative-margin hacks.</p>

<p><strong>Flexbox approach (most common):</strong></p>
<pre><code>&lt;body&gt;
  &lt;header&gt;Site header&lt;/header&gt;
  &lt;main&gt;Content&lt;/main&gt;
  &lt;footer&gt;Sticky footer&lt;/footer&gt;
&lt;/body&gt;

&lt;style&gt;
  body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;     /* viewport-tall by default */
    margin: 0;
  }
  main {
    flex: 1;                /* fills remaining height */
  }
&lt;/style&gt;</code></pre>

<p>The <code>flex: 1</code> on <code>&lt;main&gt;</code> grows it to push the footer down when content is short. When content is tall, normal flow takes over and the footer sits below it.</p>

<p><strong>Grid approach &mdash; more declarative:</strong></p>
<pre><code>body {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}
/* header takes auto, main takes 1fr (fills), footer takes auto */</code></pre>

<p><strong>Compare with the legacy techniques:</strong></p>
<table>
  <tr><th>Technique</th><th>How it works</th><th>Drawback</th></tr>
  <tr><td>Flexbox <code>flex: 1</code></td><td>Main grows to fill</td><td>None &mdash; preferred</td></tr>
  <tr><td>Grid <code>1fr</code> row</td><td>Same idea, different syntax</td><td>None</td></tr>
  <tr><td>Negative margin (legacy)</td><td>Wrapper has padding-bottom = footer height; footer has negative margin-top</td><td>Requires fixed footer height; brittle</td></tr>
  <tr><td>Calc trick</td><td>Main has <code>min-height: calc(100vh - footer-height)</code></td><td>Requires fixed footer height</td></tr>
</table>

<p><strong>Modern viewport units &mdash; account for mobile chrome:</strong></p>
<pre><code>body {
  min-height: 100dvh;       /* dynamic viewport height */
  /* dvh accounts for browser UI showing/hiding on mobile */
}</code></pre>

<p>On iOS Safari, <code>100vh</code> may extend past the visible viewport because the URL bar can show or hide. <code>100dvh</code> updates dynamically as the bar moves, preventing scroll jumping.</p>

<p><strong>Common gotchas:</strong></p>
<ul>
  <li><strong>Forgetting <code>margin: 0</code> on body</strong> &mdash; default margins create a scrollbar even when content fits.</li>
  <li><strong>Using <code>height: 100vh</code> instead of <code>min-height</code></strong> &mdash; locks page to viewport size, clipping tall content.</li>
  <li><strong>Wrapping in another container</strong> with its own height &mdash; flex layout doesn&rsquo;t propagate; the inner main can&rsquo;t grow if the wrapper isn&rsquo;t flexed too.</li>
</ul>

<p>For 2026 sites, default to the Flexbox or Grid pattern. The CSS sticky footer problem &mdash; once a major source of layout bugs &mdash; is essentially solved by these features.</p>
'''

ANSWERS[53] = r'''
<p>CSS filter effects apply graphical processing &mdash; blurring, color shifting, brightness changes &mdash; using GPU-accelerated rendering. Filters compose through a single <code>filter</code> property accepting multiple functions in sequence.</p>

<table>
  <tr><th>Function</th><th>Effect</th><th>Common values</th></tr>
  <tr><td><code>blur(px)</code></td><td>Gaussian blur</td><td><code>5px</code>, <code>10px</code></td></tr>
  <tr><td><code>brightness(%)</code></td><td>Lightness multiplier</td><td><code>0.5</code> (dark), <code>1.5</code> (bright)</td></tr>
  <tr><td><code>contrast(%)</code></td><td>Contrast multiplier</td><td><code>0</code> (gray), <code>2</code> (high)</td></tr>
  <tr><td><code>grayscale(%)</code></td><td>Desaturate to gray</td><td><code>1</code> (full), <code>0.5</code> (partial)</td></tr>
  <tr><td><code>sepia(%)</code></td><td>Vintage tan tone</td><td><code>1</code> (full sepia)</td></tr>
  <tr><td><code>hue-rotate(deg)</code></td><td>Shift hue around color wheel</td><td><code>90deg</code>, <code>180deg</code></td></tr>
  <tr><td><code>invert(%)</code></td><td>Invert colors</td><td><code>1</code> (full), <code>0.5</code> (mid)</td></tr>
  <tr><td><code>saturate(%)</code></td><td>Saturation multiplier</td><td><code>0</code> (gray), <code>2</code> (vivid)</td></tr>
  <tr><td><code>drop-shadow()</code></td><td>Shadow that follows alpha</td><td>Like box-shadow but respects transparency</td></tr>
  <tr><td><code>opacity(%)</code></td><td>Transparency</td><td><code>0.5</code></td></tr>
</table>

<pre><code>img.vintage {
  filter: sepia(0.4) contrast(1.1) brightness(0.95);
}

img.spotlight {
  filter: brightness(0.7);
  transition: filter 0.3s;
}
img.spotlight:hover {
  filter: brightness(1);
}

img.bw-on-hover {
  filter: grayscale(1);
  transition: filter 0.4s;
}
img.bw-on-hover:hover {
  filter: grayscale(0);   /* color reveals */
}</code></pre>

<p><strong>Multiple filters compose</strong> &mdash; they apply in order, left-to-right:</p>
<pre><code>.processed {
  filter: blur(2px) saturate(1.5) brightness(0.9) hue-rotate(15deg);
}</code></pre>

<p><strong>The <code>drop-shadow</code> filter</strong> &mdash; unlike <code>box-shadow</code>, it follows the actual alpha channel of an image:</p>
<pre><code>img {
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
  /* PNG transparency is respected; shadow follows the silhouette */
}</code></pre>

<p>For PNG icons or SVG, <code>drop-shadow</code> looks correct where <code>box-shadow</code> would draw a rectangular shadow.</p>

<p><strong>Performance considerations:</strong></p>
<ul>
  <li><strong>Filters trigger compositing</strong> &mdash; the element gets its own layer. Light usage is GPU-accelerated and fast.</li>
  <li><strong>Animating filters</strong> generally performs well, especially <code>opacity</code>, <code>blur</code>, and <code>brightness</code>.</li>
  <li><strong>Heavy <code>blur</code> values</strong> can cause jank on lower-end devices &mdash; test on real hardware.</li>
  <li><strong>Filters apply to children too</strong> &mdash; a blurred parent blurs its content as well; isolate with a separate element if needed.</li>
</ul>

<p><strong><code>filter</code> vs <code>backdrop-filter</code></strong>: <code>filter</code> processes the element itself; <code>backdrop-filter</code> processes whatever is behind it (frosted glass effect). They serve different visual purposes.</p>
'''

ANSWERS[54] = r'''
<p>CSS-only spinners build looping animation from a single rotating element &mdash; no JavaScript, no images. The classic pattern uses a circle with a partially-colored border:</p>

<pre><code>&lt;div class="spinner"&gt;&lt;/div&gt;

&lt;style&gt;
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e0e0e0;
    border-top-color: #0066cc;     /* one segment colored */
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
&lt;/style&gt;</code></pre>

<p><strong>Common spinner variants:</strong></p>

<p><strong>1. Three bouncing dots:</strong></p>
<pre><code>.dot-spinner {
  display: flex;
  gap: 8px;
}
.dot-spinner span {
  width: 12px;
  height: 12px;
  background: #0066cc;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}
.dot-spinner span:nth-child(2) { animation-delay: 0.16s; }
.dot-spinner span:nth-child(3) { animation-delay: 0.32s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.5; }
  40%           { transform: scale(1);   opacity: 1; }
}</code></pre>

<p><strong>2. Conic gradient spinner</strong> &mdash; smooth gradient rotation:</p>
<pre><code>.conic-spinner {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: conic-gradient(transparent, #0066cc);
  animation: spin 1s linear infinite;
  /* Hollow center via mask */
  mask: radial-gradient(transparent 50%, black 51%);
}</code></pre>

<p><strong>3. Pulsing dot</strong> &mdash; minimal indicator:</p>
<pre><code>.pulse-dot {
  width: 16px;
  height: 16px;
  background: #0066cc;
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1);   opacity: 1; }
  50%      { transform: scale(1.5); opacity: 0.4; }
}</code></pre>

<p><strong>Accessibility &mdash; critical:</strong></p>
<pre><code>&lt;div class="spinner"
     role="status"
     aria-live="polite"
     aria-label="Loading"&gt;
  &lt;span class="sr-only"&gt;Loading...&lt;/span&gt;
&lt;/div&gt;</code></pre>

<ul>
  <li><strong><code>role="status"</code></strong> + <strong><code>aria-live="polite"</code></strong> &mdash; announces the spinner to screen readers when it appears.</li>
  <li><strong>Visually-hidden text label</strong> &mdash; describes the loading state for users who can&rsquo;t see the spinner.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong>:
<pre><code>@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: pulse 2s ease-in-out infinite;   /* gentler indicator */
  }
}</code></pre></li>
</ul>

<p>Performance-wise, animating <code>transform: rotate()</code> is GPU-accelerated and ideal &mdash; never animate <code>top</code>/<code>left</code> for spinner motion.</p>
'''

ANSWERS[55] = r'''
<p>The <code>scroll-behavior</code> property controls the <strong>scroll animation when navigating to anchors or programmatic scrolls</strong>. <code>smooth</code> animates the transition; <code>auto</code> jumps instantly (default).</p>

<pre><code>html {
  scroll-behavior: smooth;
}</code></pre>

<p>This single rule makes every anchor link (<code>&lt;a href="#section"&gt;</code>) and JavaScript <code>scrollTo()</code> call animate smoothly &mdash; no library required.</p>

<p><strong>Scoped smooth scroll</strong> &mdash; only specific containers:</p>
<pre><code>.scrollable-modal {
  scroll-behavior: smooth;
  overflow-y: auto;
}</code></pre>

<p><strong>Programmatic scroll behavior</strong> &mdash; the JavaScript <code>scrollTo</code>, <code>scrollIntoView</code>, and <code>scrollBy</code> methods accept a <code>behavior</code> option that overrides CSS:</p>
<pre><code>// Force smooth regardless of CSS
element.scrollIntoView({ behavior: "smooth", block: "start" });

// Force instant
window.scrollTo({ top: 0, behavior: "instant" });

// Use CSS default
window.scrollTo({ top: 0, behavior: "auto" });</code></pre>

<p><strong>Combine with <code>scroll-margin-top</code>:</strong></p>
<pre><code>html {
  scroll-behavior: smooth;
}

section[id] {
  scroll-margin-top: 80px;   /* offset for fixed header */
}</code></pre>

<p>Without <code>scroll-margin-top</code>, anchor links scroll the target element to the very top of the viewport &mdash; hiding it behind a fixed header. The property pads the scroll target so it lands below your header.</p>

<p><strong>Respect <code>prefers-reduced-motion</code>:</strong></p>
<pre><code>html {
  scroll-behavior: smooth;
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;   /* instant for users who opt out */
  }
}</code></pre>

<p>Users with vestibular disorders may find smooth scrolling motion-sickness-inducing. Always respect their preference.</p>

<p><strong>Modern related properties:</strong></p>
<table>
  <tr><th>Property</th><th>Purpose</th></tr>
  <tr><td><code>scroll-behavior</code></td><td>Animate scroll transitions</td></tr>
  <tr><td><code>scroll-margin</code> / <code>scroll-margin-top</code></td><td>Padding around scroll targets</td></tr>
  <tr><td><code>scroll-padding</code></td><td>Inner padding of scroll container</td></tr>
  <tr><td><code>scroll-snap-type</code></td><td>Snap to children when scrolling</td></tr>
  <tr><td><code>overscroll-behavior</code></td><td>Control scroll chaining and bounce</td></tr>
  <tr><td><code>scroll-timeline</code></td><td>Drive animations from scroll position (2024+)</td></tr>
</table>

<p>The <code>scroll-behavior</code> + <code>scroll-margin-top</code> + <code>scroll-snap</code> triad covers ~80% of modern scroll UX patterns without JavaScript &mdash; cleaner than the libraries that used to be required.</p>
'''

ANSWERS[56] = r'''
<p>A fixed background image stays in place as the page scrolls &mdash; achieved with <code>background-attachment: fixed</code> or by using a separate fixed-positioned element behind the content.</p>

<p><strong>Method 1: <code>background-attachment: fixed</code>:</strong></p>
<pre><code>body {
  background-image: url("/images/scenic.jpg");
  background-attachment: fixed;
  background-size: cover;
  background-position: center;
}</code></pre>

<p>The image is anchored to the viewport &mdash; content scrolls over it. Simple, declarative.</p>

<p><strong>Method 2: separate fixed element</strong> &mdash; gives more control:</p>
<pre><code>&lt;div class="bg-fixed"&gt;&lt;/div&gt;
&lt;main&gt;Content scrolls over the fixed background&lt;/main&gt;

&lt;style&gt;
  .bg-fixed {
    position: fixed;
    inset: 0;
    z-index: -1;
    background: url("/images/scenic.jpg") center / cover;
  }
&lt;/style&gt;</code></pre>

<p><strong>Critical caveats &mdash; <code>background-attachment: fixed</code> has performance and mobile issues:</strong></p>
<table>
  <tr><th>Issue</th><th>Detail</th></tr>
  <tr><td>Mobile browser bug</td><td>iOS Safari ignores <code>fixed</code> on <code>body</code> background; renders as <code>scroll</code></td></tr>
  <tr><td>Performance hit</td><td>Forces continuous repainting on scroll</td></tr>
  <tr><td>Stutter on weak GPUs</td><td>Mobile devices may lag on every scroll frame</td></tr>
  <tr><td>iOS workaround</td><td>Apply to a non-body element with <code>height: 100vh; overflow-y: scroll</code></td></tr>
</table>

<p><strong>Mobile-friendly alternative</strong> &mdash; CSS-only "parallax" with 3D transforms (better performance):</p>
<pre><code>.parallax-container {
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  perspective: 1px;
}
.parallax-bg {
  position: relative;
  height: 100vh;
  transform: translateZ(-1px) scale(2);
  background: url("scenic.jpg") center / cover;
}
.content {
  position: relative;
  background: white;
  padding: 2rem;
}</code></pre>

<p>The 3D transform uses GPU-only rendering, avoiding the repaint problem.</p>

<p><strong>Modern alternative: scroll-driven animations</strong> (2024+):</p>
<pre><code>@keyframes parallax {
  to { transform: translateY(-30%); }
}

.bg-image {
  animation: parallax linear;
  animation-timeline: scroll();
}</code></pre>

<p>Scroll-driven animations link element transforms directly to scroll position &mdash; performant and declarative. Well-supported in Chromium 2024+; check Baseline status before relying.</p>

<p><strong>Best practice in 2026:</strong> if you just want a static background that doesn&rsquo;t scroll with content, use a fixed-positioned div. <code>background-attachment: fixed</code> is the legacy approach with mobile gotchas. For parallax effects, use scroll-driven animations or 3D-transform-based techniques rather than fighting the property.</p>
'''

ANSWERS[57] = r'''
<p>The <code>overscroll-behavior</code> property controls what happens when scrolling reaches the boundary of an element &mdash; specifically, whether scroll events <strong>chain to ancestor elements</strong> and whether <strong>browser-level effects (rubber-banding, pull-to-refresh)</strong> trigger.</p>

<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>auto</code> (default)</td><td>Scroll chains to parent at boundaries</td></tr>
  <tr><td><code>contain</code></td><td>Stops scroll chaining; browser effects (refresh, glow) suppressed</td></tr>
  <tr><td><code>none</code></td><td>Stops chaining AND prevents rubber-banding/bounce</td></tr>
</table>

<pre><code>.modal-content {
  overflow-y: auto;
  overscroll-behavior: contain;
}</code></pre>

<p><strong>The classic problem it solves:</strong> a scrollable modal opens over a long page. The user scrolls the modal to the bottom; their next swipe scrolls the page underneath instead of doing nothing. With <code>overscroll-behavior: contain</code>, scroll events stop at the modal&rsquo;s edges &mdash; the body doesn&rsquo;t scroll.</p>

<p><strong>Per-axis control:</strong></p>
<pre><code>.horizontal-scroller {
  overflow-x: auto;
  overscroll-behavior-x: contain;   /* only restrict horizontal */
}

.disable-pull-refresh {
  overscroll-behavior-y: contain;   /* only Y axis */
}</code></pre>

<p><strong>Disable pull-to-refresh on mobile</strong> (a common request for web apps):</p>
<pre><code>body {
  overscroll-behavior-y: contain;
}</code></pre>

<p>By default, mobile browsers reload the page when the user pulls down at the top &mdash; usually unwanted in app-like SPAs.</p>

<p><strong>Three-value distinction:</strong></p>
<table>
  <tr><th></th><th>Scroll chains?</th><th>Bounce/rubber-band?</th><th>Pull-to-refresh?</th></tr>
  <tr><td><code>auto</code></td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
  <tr><td><code>contain</code></td><td>No</td><td>Yes</td><td>No</td></tr>
  <tr><td><code>none</code></td><td>No</td><td>No</td><td>No</td></tr>
</table>

<p><strong>Real-world use cases:</strong></p>
<ul>
  <li><strong>Modal dialogs</strong> &mdash; prevent body scroll bleeding when modal content scrolls.</li>
  <li><strong>Chat windows</strong> &mdash; user scrolls up in chat; page shouldn&rsquo;t scroll too.</li>
  <li><strong>App-like SPAs</strong> &mdash; disable pull-to-refresh that would reload state.</li>
  <li><strong>Maps and canvases</strong> &mdash; prevent page scroll when interacting with the map.</li>
  <li><strong>Image galleries</strong> &mdash; horizontal scrollers shouldn&rsquo;t affect vertical page scroll.</li>
</ul>

<p><strong>The pre-<code>overscroll-behavior</code> alternative</strong> &mdash; locking the body during modals &mdash; was clunky:</p>
<pre><code>// Old way: lock body scroll
function openModal() {
  document.body.style.overflow = "hidden";
  document.body.style.position = "fixed";
  document.body.style.width = "100%";
}</code></pre>

<p>This approach causes content to jump (scrollbar disappears, scroll position resets) and breaks inline forms. <code>overscroll-behavior: contain</code> on the modal solves the underlying issue without these side effects.</p>

<p>Browser support is universal in 2026 &mdash; use it freely.</p>
'''

ANSWERS[58] = r'''
<p>Nested Flexbox containers compose complex responsive layouts by handling one axis at a time. Each level of nesting controls a single dimension (row or column) &mdash; the composition models real layout patterns: page <code>&rarr;</code> sections <code>&rarr;</code> rows of items <code>&rarr;</code> individual items.</p>

<pre><code>&lt;div class="page"&gt;
  &lt;header&gt;
    &lt;a class="logo"&gt;Logo&lt;/a&gt;
    &lt;nav&gt;
      &lt;a&gt;Home&lt;/a&gt; &lt;a&gt;About&lt;/a&gt; &lt;a&gt;Contact&lt;/a&gt;
    &lt;/nav&gt;
    &lt;div class="actions"&gt;
      &lt;button&gt;Login&lt;/button&gt; &lt;button&gt;Sign up&lt;/button&gt;
    &lt;/div&gt;
  &lt;/header&gt;

  &lt;main&gt;
    &lt;article&gt;Main content&lt;/article&gt;
    &lt;aside&gt;
      &lt;div class="card"&gt;Card 1&lt;/div&gt;
      &lt;div class="card"&gt;Card 2&lt;/div&gt;
    &lt;/aside&gt;
  &lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .page {
    display: flex;
    flex-direction: column;       /* outer: vertical stack */
    min-height: 100vh;
  }

  header {
    display: flex;                 /* row of items */
    justify-content: space-between;
    align-items: center;
    padding: 1em 2em;
    flex-wrap: wrap;
    gap: 1em;
  }

  header nav {
    display: flex;                 /* nested: nav links horizontally */
    gap: 1.5em;
  }

  header .actions {
    display: flex;                 /* nested: action buttons */
    gap: 0.5em;
  }

  main {
    display: flex;                 /* article + aside side by side */
    flex: 1;                        /* fills remaining height */
    gap: 2em;
    padding: 2em;
  }
  main article { flex: 1; min-width: 0; }
  main aside {
    flex: 0 0 280px;
    display: flex;                 /* nested: vertical card stack */
    flex-direction: column;
    gap: 1em;
  }

  /* Mobile: collapse all to vertical */
  @media (max-width: 768px) {
    header { flex-direction: column; align-items: stretch; }
    main { flex-direction: column; }
    main aside { flex: none; }
  }
&lt;/style&gt;</code></pre>

<p><strong>The composition pattern explained:</strong></p>
<table>
  <tr><th>Level</th><th>Direction</th><th>Children</th></tr>
  <tr><td>.page</td><td>Column</td><td>Header / Main / Footer</td></tr>
  <tr><td>header</td><td>Row</td><td>Logo / Nav / Actions</td></tr>
  <tr><td>nav</td><td>Row</td><td>Individual links</td></tr>
  <tr><td>main</td><td>Row</td><td>Article / Aside</td></tr>
  <tr><td>aside</td><td>Column</td><td>Stacked cards</td></tr>
</table>

<p><strong>Key sizing patterns:</strong></p>
<ul>
  <li><strong><code>flex: 1</code></strong> &mdash; takes all remaining space.</li>
  <li><strong><code>flex: 0 0 280px</code></strong> &mdash; fixed width sidebar (no grow, no shrink, basis 280px).</li>
  <li><strong><code>flex: 1 1 250px</code></strong> &mdash; minimum 250px, grow equally, wrap when needed.</li>
  <li><strong><code>min-width: 0</code></strong> on flex children &mdash; allows them to shrink below content&rsquo;s natural width (default is <code>min-width: auto</code>, often surprising).</li>
</ul>

<p><strong>When to nest Flex vs reach for Grid</strong>: nested Flexbox handles 1D stacks at each level. If you need true 2D alignment (rows aligning across cells, items spanning grid lines), Grid is the better tool. Hybrid approaches &mdash; Grid at the page level, Flexbox inside each cell &mdash; combine the strengths of both.</p>
'''

ANSWERS[59] = r'''
<p><code>grid-template-areas</code> is one of the most expressive features in CSS &mdash; it lets you define a grid layout <strong>visually with named regions</strong>, then assign elements to those names. The CSS reads like ASCII art of the layout.</p>

<pre><code>&lt;div class="layout"&gt;
  &lt;header&gt;Header&lt;/header&gt;
  &lt;nav&gt;Navigation&lt;/nav&gt;
  &lt;main&gt;Main content&lt;/main&gt;
  &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: grid;
    grid-template-columns: 200px 1fr 200px;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header header header"
      "nav    main   aside"
      "footer footer footer";
    min-height: 100vh;
    gap: 1em;
  }

  header { grid-area: header; }
  nav    { grid-area: nav; }
  main   { grid-area: main; }
  aside  { grid-area: aside; }
  footer { grid-area: footer; }
&lt;/style&gt;</code></pre>

<p><strong>Rules for grid-template-areas:</strong></p>
<ul>
  <li><strong>Each row</strong> is a quoted string with column names separated by whitespace.</li>
  <li><strong>All rows must have the same column count.</strong></li>
  <li><strong>Repeating a name</strong> across rows or columns spans that area.</li>
  <li><strong><code>.</code> (dot)</strong> represents an empty cell (no element occupies it).</li>
  <li><strong>Areas must be rectangular</strong> &mdash; you can&rsquo;t make L or T shapes.</li>
</ul>

<p><strong>Empty cells with the dot:</strong></p>
<pre><code>.layout {
  grid-template-areas:
    "header header header"
    ".      main   ."         /* gaps left and right of main */
    "footer footer footer";
}</code></pre>

<p><strong>Responsive layouts &mdash; rearrange areas per breakpoint:</strong></p>
<pre><code>@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "nav"
      "main"
      "aside"
      "footer";
  }
}</code></pre>

<p>Same HTML, completely different layout &mdash; just by redefining the template-areas string. The visual order can differ from the source order without using <code>order</code>.</p>

<p><strong>Common use cases:</strong></p>
<table>
  <tr><th>Pattern</th><th>Example template</th></tr>
  <tr><td>Holy grail</td><td><code>"header header header" / "nav main aside" / "footer footer footer"</code></td></tr>
  <tr><td>Sidebar layout</td><td><code>"header header" / "aside main" / "footer footer"</code></td></tr>
  <tr><td>Magazine</td><td><code>"hero hero" / "intro sidebar" / "content content"</code></td></tr>
  <tr><td>Dashboard</td><td><code>"nav main main" / "nav stats stats"</code></td></tr>
</table>

<p><strong>Limitations:</strong></p>
<ul>
  <li><strong>Areas must form rectangles</strong> &mdash; an L-shape isn&rsquo;t allowed; the browser rejects the entire template.</li>
  <li><strong>No partial spans</strong> &mdash; if you need an element to span 1.5 columns, use line-based placement (<code>grid-column: 1 / 3</code>) instead.</li>
  <li><strong>Subgrid support</strong> doesn&rsquo;t inherit areas &mdash; nested grids define their own.</li>
</ul>

<p>For ~80% of page-level layouts, <code>grid-template-areas</code> is the clearest, most maintainable choice in CSS. The visual representation in the source file makes layout changes intuitive.</p>
'''

ANSWERS[60] = r'''
<p>A CSS-only lightbox uses the <code>:target</code> pseudo-class &mdash; clicking a link with <code>href="#image"</code> matches the corresponding <code>id="image"</code>, allowing styles to apply only when the element is "targeted" via URL fragment.</p>

<pre><code>&lt;div class="gallery"&gt;
  &lt;a href="#img1"&gt;&lt;img src="thumb1.jpg" alt=""&gt;&lt;/a&gt;
  &lt;a href="#img2"&gt;&lt;img src="thumb2.jpg" alt=""&gt;&lt;/a&gt;
  &lt;a href="#img3"&gt;&lt;img src="thumb3.jpg" alt=""&gt;&lt;/a&gt;
&lt;/div&gt;

&lt;!-- Lightbox overlays (hidden until targeted) --&gt;
&lt;div class="lightbox" id="img1"&gt;
  &lt;a href="#" class="close"&gt;&times;&lt;/a&gt;
  &lt;img src="full1.jpg" alt=""&gt;
&lt;/div&gt;
&lt;div class="lightbox" id="img2"&gt;
  &lt;a href="#" class="close"&gt;&times;&lt;/a&gt;
  &lt;img src="full2.jpg" alt=""&gt;
&lt;/div&gt;
&lt;!-- ... --&gt;

&lt;style&gt;
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1em;
  }
  .gallery img {
    width: 100%;
    cursor: zoom-in;
  }

  .lightbox {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s;
  }
  .lightbox:target {
    opacity: 1;
    pointer-events: auto;
  }
  .lightbox img {
    max-width: 90vw;
    max-height: 90vh;
    border-radius: 4px;
  }
  .close {
    position: absolute;
    top: 1em;
    right: 1em;
    color: white;
    font-size: 2em;
    text-decoration: none;
  }
&lt;/style&gt;</code></pre>

<p><strong>How it works:</strong></p>
<ol>
  <li>Each thumbnail is a link to a fragment ID (<code>#img1</code>).</li>
  <li>Each lightbox container has the matching ID.</li>
  <li>The <code>:target</code> pseudo-class matches the element whose ID is in the URL fragment.</li>
  <li>The default state is invisible (<code>opacity: 0; pointer-events: none</code>); <code>:target</code> reveals it.</li>
  <li>Clicking the close link sets the URL fragment to nothing &mdash; the lightbox hides.</li>
</ol>

<p><strong>Modern alternative: native <code>&lt;dialog&gt;</code> + Popover API</strong> &mdash; better accessibility:</p>
<pre><code>&lt;button popovertarget="lightbox-1"&gt;
  &lt;img src="thumb1.jpg" alt=""&gt;
&lt;/button&gt;

&lt;div id="lightbox-1" popover="auto"&gt;
  &lt;button popovertarget="lightbox-1" popovertargetaction="hide"&gt;&times;&lt;/button&gt;
  &lt;img src="full1.jpg" alt=""&gt;
&lt;/div&gt;

&lt;style&gt;
  [popover] {
    background: rgba(0, 0, 0, 0.9);
    border: none;
    padding: 0;
    margin: auto;
    inset: 0;
    width: 100vw;
    height: 100vh;
  }
  [popover] img { max-width: 90vw; max-height: 90vh; margin: auto; }
&lt;/style&gt;</code></pre>

<p>The Popover API (2024+ baseline) provides:</p>
<ul>
  <li><strong>Top-layer rendering</strong> &mdash; no z-index battles.</li>
  <li><strong>Esc key dismissal</strong> for free.</li>
  <li><strong>Light-dismiss</strong> (click outside to close) with <code>popover="auto"</code>.</li>
  <li><strong>Proper focus management</strong> &mdash; focus moves into the popover on open.</li>
</ul>

<p><strong>Trade-offs:</strong></p>
<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>:target</td><td>Pure CSS; works everywhere</td><td>Changes URL; back button loops</td></tr>
  <tr><td>Popover API</td><td>Native, accessible, top-layer</td><td>Requires Baseline 2024+</td></tr>
  <tr><td>JavaScript library</td><td>Full features (zoom, swipe)</td><td>Bundle size; complexity</td></tr>
</table>

<p>For new projects in 2026, prefer the Popover API. The <code>:target</code> approach is great for static demos and progressive-enhancement baselines.</p>
'''

ANSWERS[61] = r'''
<p>The <code>backdrop-filter</code> property applies graphical effects &mdash; primarily blur &mdash; to <strong>whatever is rendered behind a translucent element</strong>. It enables the modern "frosted glass" aesthetic seen in macOS, iOS, and Windows 11 UIs.</p>

<pre><code>&lt;div class="hero-bg"&gt;
  &lt;div class="frosted-card"&gt;
    &lt;h2&gt;Frosted glass&lt;/h2&gt;
    &lt;p&gt;Background blurred behind this card.&lt;/p&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .hero-bg {
    background: url("/images/colorful-pattern.jpg") center / cover;
    height: 60vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .frosted-card {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    padding: 2em;
    color: white;
  }
&lt;/style&gt;</code></pre>

<p><strong>Critical: the element must be at least slightly transparent</strong> &mdash; <code>backdrop-filter</code> processes pixels behind the element. If the element is fully opaque, you can&rsquo;t see anything behind it, so the filter has no visible effect.</p>

<p><strong>The <code>-webkit-</code> prefix</strong> is still required for Safari (even in 2026 some versions). Always include both.</p>

<p><strong>Same filter functions as <code>filter</code>:</strong></p>
<table>
  <tr><th>Function</th><th>Effect on backdrop</th></tr>
  <tr><td><code>blur(20px)</code></td><td>Soften pixels behind</td></tr>
  <tr><td><code>brightness(1.2)</code></td><td>Lighten everything behind</td></tr>
  <tr><td><code>contrast(0.8)</code></td><td>Reduce contrast behind</td></tr>
  <tr><td><code>saturate(1.5)</code></td><td>Vivid colors behind</td></tr>
  <tr><td><code>grayscale(1)</code></td><td>Desaturate behind</td></tr>
  <tr><td><code>hue-rotate(45deg)</code></td><td>Shift hues behind</td></tr>
</table>

<p><strong>Real-world applications:</strong></p>
<pre><code>/* Sticky nav over content */
.frosted-nav {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* iOS-style modal overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
}

/* Hero section text card */
.text-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}</code></pre>

<p><strong><code>filter</code> vs <code>backdrop-filter</code>:</strong></p>
<table>
  <tr><th></th><th><code>filter</code></th><th><code>backdrop-filter</code></th></tr>
  <tr><td>Processes</td><td>The element itself</td><td>What&rsquo;s behind the element</td></tr>
  <tr><td>Affects children</td><td>Yes (entire subtree)</td><td>No</td></tr>
  <tr><td>Common use</td><td>Modify images, hover effects</td><td>Frosted glass, modal overlays</td></tr>
</table>

<p><strong>Performance considerations:</strong></p>
<ul>
  <li><strong>Backdrop-filter is expensive</strong> &mdash; the browser must rasterize and process every pixel behind the element on each frame.</li>
  <li><strong>Animation</strong> can be laggy on lower-end mobile devices &mdash; test on real hardware.</li>
  <li><strong>Use sparingly</strong> &mdash; one or two frosted elements per view; not a sticky-everywhere pattern.</li>
  <li><strong>Provide a fallback</strong> for unsupported browsers:</li>
</ul>
<pre><code>.frosted {
  background: rgba(255, 255, 255, 0.7);   /* opaque fallback */
}
@supports (backdrop-filter: blur(10px)) {
  .frosted {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
  }
}</code></pre>

<p>The fallback shows a more opaque background where the filter isn&rsquo;t supported, ensuring the design still works.</p>
'''

ANSWERS[62] = r'''
<p>A pricing table compares plans side-by-side. CSS Grid handles the responsive layout naturally &mdash; cards reflow on small screens; the "highlighted" plan stands out with elevation and color.</p>

<pre><code>&lt;section class="pricing"&gt;
  &lt;article class="plan"&gt;
    &lt;h3&gt;Starter&lt;/h3&gt;
    &lt;p class="price"&gt;&lt;span&gt;$&lt;/span&gt;9&lt;span class="period"&gt;/mo&lt;/span&gt;&lt;/p&gt;
    &lt;ul class="features"&gt;
      &lt;li&gt;5 projects&lt;/li&gt;
      &lt;li&gt;10 GB storage&lt;/li&gt;
      &lt;li&gt;Email support&lt;/li&gt;
    &lt;/ul&gt;
    &lt;a href="#" class="btn"&gt;Get started&lt;/a&gt;
  &lt;/article&gt;

  &lt;article class="plan featured"&gt;
    &lt;span class="badge"&gt;Most Popular&lt;/span&gt;
    &lt;h3&gt;Pro&lt;/h3&gt;
    &lt;p class="price"&gt;&lt;span&gt;$&lt;/span&gt;29&lt;span class="period"&gt;/mo&lt;/span&gt;&lt;/p&gt;
    &lt;ul class="features"&gt;
      &lt;li&gt;Unlimited projects&lt;/li&gt;
      &lt;li&gt;100 GB storage&lt;/li&gt;
      &lt;li&gt;Priority support&lt;/li&gt;
      &lt;li&gt;Team collaboration&lt;/li&gt;
    &lt;/ul&gt;
    &lt;a href="#" class="btn btn-primary"&gt;Get started&lt;/a&gt;
  &lt;/article&gt;

  &lt;article class="plan"&gt;
    &lt;h3&gt;Enterprise&lt;/h3&gt;
    &lt;p class="price"&gt;&lt;span&gt;$&lt;/span&gt;99&lt;span class="period"&gt;/mo&lt;/span&gt;&lt;/p&gt;
    &lt;ul class="features"&gt;
      &lt;li&gt;Everything in Pro&lt;/li&gt;
      &lt;li&gt;1 TB storage&lt;/li&gt;
      &lt;li&gt;Dedicated support&lt;/li&gt;
      &lt;li&gt;SLA guarantee&lt;/li&gt;
    &lt;/ul&gt;
    &lt;a href="#" class="btn"&gt;Contact sales&lt;/a&gt;
  &lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .pricing {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5em;
    padding: 2em;
    max-width: 1100px;
    margin: 0 auto;
    align-items: stretch;     /* equal heights across cards */
  }
  .plan {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 2em;
    display: flex;
    flex-direction: column;
    text-align: center;
    position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .plan:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
  .plan.featured {
    border-color: #0066cc;
    border-width: 2px;
    transform: scale(1.05);
    box-shadow: 0 8px 24px rgba(0, 102, 204, 0.15);
    z-index: 1;
  }
  .badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: #0066cc;
    color: white;
    padding: 0.25em 1em;
    border-radius: 999px;
    font-size: 0.85em;
    font-weight: 600;
  }
  .price {
    font-size: 3em;
    font-weight: 700;
    margin: 0.5em 0;
  }
  .price span { font-size: 0.4em; vertical-align: super; }
  .period { font-weight: 400; color: #666; }
  .features {
    list-style: none;
    padding: 0;
    margin: 1.5em 0;
    flex: 1;          /* push button to bottom */
  }
  .features li {
    padding: 0.5em 0;
    border-bottom: 1px solid #f0f0f0;
  }
  .btn {
    background: white;
    border: 2px solid #0066cc;
    color: #0066cc;
    padding: 0.75em 1.5em;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
  }
  .btn-primary {
    background: #0066cc;
    color: white;
  }

  /* Mobile: featured doesn't scale up (causes overflow) */
  @media (max-width: 768px) {
    .plan.featured { transform: none; }
  }
&lt;/style&gt;</code></pre>

<p><strong>Key design tactics:</strong></p>
<ul>
  <li><strong><code>auto-fit + minmax(280px, 1fr)</code></strong> &mdash; cards reflow from 3-up to 2-up to 1-up automatically.</li>
  <li><strong><code>align-items: stretch</code></strong> &mdash; cards stretch to equal heights even with different content.</li>
  <li><strong><code>flex: 1</code> on features list</strong> &mdash; pushes the CTA button to the bottom of every card.</li>
  <li><strong><code>transform: scale(1.05)</code> on featured plan</strong> &mdash; visual hierarchy (revert on mobile to avoid overflow).</li>
  <li><strong>Border thickness shift</strong> on featured plan &mdash; calls attention without color overuse.</li>
</ul>

<p>For a comparison-style table (rows of features, columns of plans), use a true <code>&lt;table&gt;</code> or <code>display: grid</code> with explicit column/row positioning. The card-style above is for visual appeal; the table-style is for detailed comparison.</p>
'''

ANSWERS[63] = r'''
<p>Viewport units express lengths as <strong>percentages of the browser viewport</strong>. They&rsquo;re essential for full-screen layouts, fluid typography, and modern responsive design that doesn&rsquo;t depend on parent width.</p>

<table>
  <tr><th>Unit</th><th>Equals</th><th>Common use</th></tr>
  <tr><td><code>vw</code></td><td>1% of viewport <strong>width</strong></td><td>Fluid typography, full-width</td></tr>
  <tr><td><code>vh</code></td><td>1% of viewport <strong>height</strong></td><td>Hero sections, fullscreen</td></tr>
  <tr><td><code>vmin</code></td><td>1% of <strong>smaller</strong> dimension</td><td>Square aspect ratios</td></tr>
  <tr><td><code>vmax</code></td><td>1% of <strong>larger</strong> dimension</td><td>Landscape-vs-portrait awareness</td></tr>
</table>

<pre><code>.hero {
  height: 100vh;        /* full viewport height */
  width: 100vw;          /* full viewport width */
}

.full-bleed {
  /* Trick: extend a centered container to full viewport width */
  width: 100vw;
  margin-left: calc(50% - 50vw);
}

h1 {
  /* Fluid typography */
  font-size: clamp(2rem, 4vw + 1rem, 4rem);
}</code></pre>

<p><strong>The mobile viewport problem &mdash; and the new <code>dvh</code>, <code>svh</code>, <code>lvh</code> units (2022+):</strong></p>
<table>
  <tr><th>Unit</th><th>Description</th></tr>
  <tr><td><code>vh</code></td><td>Original; doesn&rsquo;t change as mobile UI shows/hides</td></tr>
  <tr><td><code>svh</code> (small)</td><td>Smallest possible viewport height (with all UI visible)</td></tr>
  <tr><td><code>lvh</code> (large)</td><td>Largest possible viewport height (UI hidden)</td></tr>
  <tr><td><code>dvh</code> (dynamic)</td><td>Updates as UI shows/hides &mdash; matches what&rsquo;s currently visible</td></tr>
</table>

<pre><code>/* The classic mobile bug */
.broken-hero {
  height: 100vh;       /* on iOS, may extend below the visible area */
}

/* The fix */
.fixed-hero {
  height: 100dvh;       /* always matches the actual visible viewport */
}</code></pre>

<p>On mobile, the URL bar shows when scrolling stops and hides while scrolling. <code>vh</code> uses the largest possible value &mdash; so a "100vh" element is partially below the URL bar when it&rsquo;s visible. <code>dvh</code> updates dynamically.</p>

<p><strong>Equivalent units exist for width:</strong> <code>svw</code>, <code>lvw</code>, <code>dvw</code>, <code>svi</code>/<code>lvi</code>/<code>dvi</code> (logical inline), <code>svb</code>/<code>lvb</code>/<code>dvb</code> (logical block).</p>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Square card adapts to viewport size */
.square {
  width: 50vmin;
  height: 50vmin;       /* always square; sizes to smaller viewport dimension */
}

/* Diagonal text spans viewport */
.diagonal {
  font-size: 5vmax;     /* uses the larger dimension */
}

/* Full-screen modal */
.modal {
  width: 100vw;
  height: 100dvh;
  position: fixed;
}

/* Section that's always at least 80% of viewport */
.section {
  min-height: 80vh;
}</code></pre>

<p><strong>Combine with <code>clamp()</code> for fluid typography</strong>:</p>
<pre><code>h1 {
  font-size: clamp(1.5rem, 3vw + 1rem, 4rem);
  /* Min 1.5rem, scales fluidly, max 4rem */
}</code></pre>

<p>Modern responsive typography &mdash; one rule replaces multiple media queries.</p>

<p><strong>Limitations:</strong></p>
<ul>
  <li><strong>Don&rsquo;t use <code>vw</code> for general spacing</strong> &mdash; padding/margin in <code>vw</code> changes wildly between phone and 4K monitor; ems/rems are usually better.</li>
  <li><strong>Be cautious with <code>vh</code> on iframe-embedded pages</strong> &mdash; it refers to the iframe&rsquo;s viewport, not the parent.</li>
  <li><strong>Avoid all-vw layouts</strong> for accessibility &mdash; users who zoom (Ctrl+) won&rsquo;t see scaling because vw is viewport-relative not zoom-relative.</li>
</ul>
'''

ANSWERS[64] = r'''
<p>A sticky sidebar follows the user as they scroll the main content &mdash; ideal for navigation, table-of-contents, or related-content panels. <code>position: sticky</code> + <code>align-self: start</code> in a Grid layout produces it cleanly with zero JavaScript.</p>

<pre><code>&lt;div class="layout"&gt;
  &lt;main&gt;
    &lt;article&gt;
      &lt;h1&gt;Long article title&lt;/h1&gt;
      &lt;p&gt;Lots of content...&lt;/p&gt;
      &lt;!-- Many paragraphs --&gt;
    &lt;/article&gt;
  &lt;/main&gt;

  &lt;aside class="sidebar"&gt;
    &lt;nav class="toc"&gt;
      &lt;h3&gt;Contents&lt;/h3&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="#intro"&gt;Introduction&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#methods"&gt;Methods&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#results"&gt;Results&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#conclusion"&gt;Conclusion&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/aside&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: grid;
    grid-template-columns: 1fr 250px;
    gap: 2em;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1em;
  }

  .sidebar {
    position: sticky;
    top: 1em;                  /* offset from viewport top */
    align-self: start;          /* don't stretch to main height */
    height: calc(100vh - 2em); /* limit height for tall content */
    overflow-y: auto;          /* internal scroll if too tall */
  }

  .toc {
    background: #f8f9fa;
    padding: 1em;
    border-radius: 8px;
  }
  .toc ul {
    list-style: none;
    padding: 0;
  }
  .toc a {
    display: block;
    padding: 0.5em;
    color: #333;
    text-decoration: none;
    border-radius: 4px;
  }
  .toc a:hover { background: #e9ecef; }

  /* Mobile: stack normally, no stickiness */
  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
    }
    .sidebar {
      position: static;
      height: auto;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>Why <code>align-self: start</code> matters:</strong> in a Grid layout, items default to <code>align-self: stretch</code>, which makes the sidebar stretch to match the main content&rsquo;s height. A stretched sidebar can&rsquo;t stick &mdash; it has no room to scroll past. <code>start</code> lets the sidebar take its natural height, freeing the rest of the cell for sticky behavior.</p>

<p><strong>The <code>top</code> value</strong> &mdash; the threshold below which the sidebar sticks. <code>top: 0</code> sticks at the very top; <code>top: 80px</code> sticks below a fixed header.</p>

<p><strong>Common gotcha: parent <code>overflow</code> breaks sticky</strong></p>
<table>
  <tr><th>Parent style</th><th>Sticky works?</th></tr>
  <tr><td><code>overflow: visible</code> (default)</td><td>Yes</td></tr>
  <tr><td><code>overflow: hidden</code></td><td>No &mdash; parent becomes scroll context</td></tr>
  <tr><td><code>overflow: auto</code></td><td>No</td></tr>
  <tr><td><code>overflow: clip</code></td><td>Sometimes &mdash; depends on overflow direction</td></tr>
</table>

<p>If sticky isn&rsquo;t working, check every ancestor for <code>overflow</code> properties &mdash; they&rsquo;re the most common cause.</p>

<p><strong>Sticky in Flexbox</strong> &mdash; trickier; needs explicit alignment:</p>
<pre><code>.flex-layout {
  display: flex;
  align-items: flex-start;     /* don't stretch */
  gap: 2em;
}
.flex-layout .sidebar {
  position: sticky;
  top: 1em;
  flex: 0 0 250px;
}</code></pre>

<p><strong>Internal scrolling for tall sidebars</strong> &mdash; if the sidebar content is too tall to fit the viewport, set <code>height: calc(100vh - 2em)</code> + <code>overflow-y: auto</code>. The sidebar sticks while scrolling its own content.</p>

<p>The pattern is one of the cleanest "library-grade" features that vanilla CSS now handles natively &mdash; replacing complex JavaScript implementations from earlier years.</p>
'''

ANSWERS[65] = r'''
<p>The <code>aspect-ratio</code> property locks an element to a specific width-to-height ratio. Set one dimension; the other computes automatically. It replaces a 20-year-old padding-bottom hack with a single declarative line.</p>

<pre><code>.video-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9;          /* width:height = 16:9 */
}

.square-card {
  width: 200px;
  aspect-ratio: 1;                /* shorthand for 1:1 */
}

.golden-rectangle {
  aspect-ratio: 1.618 / 1;        /* golden ratio */
}</code></pre>

<p><strong>How it computes:</strong></p>
<ul>
  <li><strong>Width set</strong> &mdash; height = width / ratio.</li>
  <li><strong>Height set</strong> &mdash; width = height * ratio.</li>
  <li><strong>Both set</strong> &mdash; explicit values win; ratio is ignored.</li>
  <li><strong>Neither set</strong> &mdash; uses content-derived sizing with the ratio applied.</li>
</ul>

<p><strong>Common ratio reference:</strong></p>
<table>
  <tr><th>Ratio</th><th>Use case</th></tr>
  <tr><td><code>16 / 9</code></td><td>HD video, modern monitors, YouTube</td></tr>
  <tr><td><code>4 / 3</code></td><td>Old TV, photo prints, classic compositions</td></tr>
  <tr><td><code>1 / 1</code></td><td>Instagram square, profile photos</td></tr>
  <tr><td><code>21 / 9</code></td><td>Ultrawide cinematic banners</td></tr>
  <tr><td><code>3 / 2</code></td><td>Standard photo prints, DSLR sensors</td></tr>
  <tr><td><code>9 / 16</code></td><td>Vertical video (TikTok, Stories)</td></tr>
  <tr><td><code>2 / 3</code></td><td>Movie posters, book covers</td></tr>
</table>

<p><strong>The pre-aspect-ratio "padding-bottom" hack</strong> (still useful as a fallback or for older browsers):</p>
<pre><code>.aspect-16-9-fallback {
  position: relative;
  padding-bottom: 56.25%;        /* 9 / 16 = 0.5625 = 56.25% */
  height: 0;
}
.aspect-16-9-fallback &gt; * {
  position: absolute;
  inset: 0;                      /* fill the box */
}</code></pre>

<p>It works because percentage padding is relative to the element&rsquo;s width &mdash; setting <code>padding-bottom: 56.25%</code> reserves space proportional to the width. Then absolute-positioned children fill the box.</p>

<p><strong>Modern <code>aspect-ratio</code> replaces this entirely:</strong></p>
<pre><code>.modern {
  aspect-ratio: 16 / 9;
  background: #000;
}
.modern &gt; iframe {
  width: 100%;
  height: 100%;             /* simple flow; no positioning needed */
}</code></pre>

<p><strong>Pair with <code>object-fit: cover</code></strong> on contained images for filled cropping:</p>
<pre><code>.thumbnail {
  aspect-ratio: 4 / 3;
  width: 100%;
}
.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;        /* crop to fill the box */
}</code></pre>

<p>Different image dimensions all render identically &mdash; the box stays 4:3, the image is cropped to fit.</p>

<p><strong>Real-world use cases:</strong></p>
<ul>
  <li><strong>Embedded videos</strong> &mdash; iframe responsive containers.</li>
  <li><strong>Photo galleries</strong> &mdash; uniform thumbnails regardless of source dimensions.</li>
  <li><strong>Card thumbnails</strong> &mdash; consistent shape across cards in a grid.</li>
  <li><strong>Logo/icon containers</strong> &mdash; locked square or circular containers.</li>
  <li><strong>Map placeholders</strong> &mdash; 16:9 or 4:3 areas before the map loads.</li>
  <li><strong>Skeleton loaders</strong> &mdash; reserve correct space to prevent layout shift.</li>
</ul>

<p>Always set <code>aspect-ratio</code> on placeholders that load images later &mdash; it&rsquo;s the easiest fix for Cumulative Layout Shift (CLS).</p>
'''

ANSWERS[66] = r'''
<p>Responsive tables face a fundamental conflict: tables work well with rectangular data, but mobile screens are narrow. Three primary strategies, each with trade-offs:</p>

<table>
  <tr><th>Strategy</th><th>Approach</th><th>Best for</th></tr>
  <tr><td>Horizontal scroll</td><td>Wrap table in scrollable container</td><td>Data-heavy tables, exact comparison</td></tr>
  <tr><td>Stacked rows</td><td>Each row becomes a card on mobile</td><td>5-10 columns, individual record viewing</td></tr>
  <tr><td>Hide secondary columns</td><td>Show only critical columns on mobile</td><td>Many columns where some are nice-to-have</td></tr>
</table>

<p><strong>Strategy 1: horizontal scroll</strong> &mdash; preserves the table fully:</p>
<pre><code>.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;     /* momentum on iOS */
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}
.table-wrapper table {
  width: 100%;
  min-width: 600px;            /* forces scroll on narrow screens */
  border-collapse: collapse;
}
.table-wrapper th,
.table-wrapper td {
  padding: 0.75em 1em;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;          /* prevent wrapping */
}</code></pre>

<p><strong>Strategy 2: stacked rows on mobile</strong> &mdash; transforms each row into a card:</p>
<pre><code>&lt;table class="responsive-table"&gt;
  &lt;thead&gt;
    &lt;tr&gt;&lt;th&gt;Name&lt;/th&gt;&lt;th&gt;Email&lt;/th&gt;&lt;th&gt;Role&lt;/th&gt;&lt;th&gt;Date&lt;/th&gt;&lt;/tr&gt;
  &lt;/thead&gt;
  &lt;tbody&gt;
    &lt;tr&gt;
      &lt;td data-label="Name"&gt;Alice Smith&lt;/td&gt;
      &lt;td data-label="Email"&gt;alice@x.com&lt;/td&gt;
      &lt;td data-label="Role"&gt;Admin&lt;/td&gt;
      &lt;td data-label="Date"&gt;2026-01-15&lt;/td&gt;
    &lt;/tr&gt;
  &lt;/tbody&gt;
&lt;/table&gt;

&lt;style&gt;
  @media (max-width: 600px) {
    .responsive-table {
      border-collapse: separate;
      border-spacing: 0;
    }
    .responsive-table thead {
      display: none;     /* hide column headers */
    }
    .responsive-table tr {
      display: block;
      margin-bottom: 1em;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 0.5em;
    }
    .responsive-table td {
      display: flex;
      justify-content: space-between;
      padding: 0.5em;
      border-bottom: 1px solid #f0f0f0;
    }
    .responsive-table td:last-child { border-bottom: none; }
    .responsive-table td::before {
      content: attr(data-label);     /* show column name */
      font-weight: 600;
      color: #555;
    }
  }
&lt;/style&gt;</code></pre>

<p>The <code>data-label</code> attribute carries the column name; CSS reads it via <code>attr()</code> in <code>::before</code>. Each row becomes a labeled key-value card on mobile.</p>

<p><strong>Strategy 3: hide secondary columns</strong>:</p>
<pre><code>.optional { display: table-cell; }   /* default */

@media (max-width: 768px) {
  .optional { display: none; }     /* hide on mobile */
}</code></pre>

<p>Identify the must-show columns and hide the rest behind a "show details" disclosure or expandable row.</p>

<p><strong>Modern CSS Grid alternative</strong> &mdash; render the table without table semantics:</p>
<pre><code>&lt;div class="grid-table" role="table"&gt;
  &lt;div role="row"&gt;
    &lt;div role="cell"&gt;Alice&lt;/div&gt;
    &lt;div role="cell"&gt;alice@x.com&lt;/div&gt;
    &lt;div role="cell"&gt;Admin&lt;/div&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .grid-table {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
  }
&lt;/style&gt;</code></pre>

<p>Lets you reflow on mobile with a different grid &mdash; but loses real table semantics and assistive-tech features. Better to use a real <code>&lt;table&gt;</code> with one of the strategies above.</p>

<p><strong>Recommendation:</strong> for data-heavy contexts (spreadsheet-like tables, financial data) use horizontal scroll. For record viewing (users, orders, products) use stacked rows. Match the strategy to the user&rsquo;s task on mobile.</p>
'''

ANSWERS[67] = r'''
<p>CSS counters provide <strong>automatic numbering for elements</strong> &mdash; mimicking ordered list behavior with arbitrary content (chapter numbers, table-of-contents, figure captions, hierarchical legal numbering). Combined with pseudo-elements, they replace much of what JavaScript previously handled.</p>

<p><strong>Three properties work together:</strong></p>
<table>
  <tr><th>Property</th><th>Purpose</th></tr>
  <tr><td><code>counter-reset</code></td><td>Initialize a counter (typically on parent)</td></tr>
  <tr><td><code>counter-increment</code></td><td>Increment for each occurrence</td></tr>
  <tr><td><code>counter()</code> in <code>content</code></td><td>Output the current value</td></tr>
</table>

<pre><code>&lt;ol class="custom-list"&gt;
  &lt;li&gt;First item&lt;/li&gt;
  &lt;li&gt;Second item&lt;/li&gt;
  &lt;li&gt;Third item&lt;/li&gt;
&lt;/ol&gt;

&lt;style&gt;
  .custom-list {
    list-style: none;        /* remove default markers */
    counter-reset: item;      /* start the counter */
    padding: 0;
  }
  .custom-list li {
    counter-increment: item;   /* +1 for each li */
    padding: 0.5em 0 0.5em 2em;
    position: relative;
  }
  .custom-list li::before {
    content: counter(item);
    position: absolute;
    left: 0;
    top: 0.5em;
    width: 1.5em;
    height: 1.5em;
    background: #0066cc;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
&lt;/style&gt;</code></pre>

<p><strong>Hierarchical (nested) numbering &mdash; legal-style "1.1.1":</strong></p>
<pre><code>&lt;ol class="legal"&gt;
  &lt;li&gt;Section title
    &lt;ol&gt;
      &lt;li&gt;Subsection
        &lt;ol&gt;
          &lt;li&gt;Subsubsection&lt;/li&gt;
        &lt;/ol&gt;
      &lt;/li&gt;
    &lt;/ol&gt;
  &lt;/li&gt;
&lt;/ol&gt;

&lt;style&gt;
  .legal,
  .legal ol {
    list-style: none;
    counter-reset: section;
    padding-left: 1em;
  }
  .legal li {
    counter-increment: section;
  }
  .legal li::before {
    content: counters(section, ".") " ";
    /* counters() (plural) joins the entire counter chain */
    font-weight: bold;
    color: #0066cc;
  }
&lt;/style&gt;</code></pre>

<p>The <strong><code>counters()</code> plural function</strong> joins all values in the counter chain with a separator &mdash; outputting "1", "1.1", "1.1.1" automatically.</p>

<p><strong>Multiple counters in one document</strong> &mdash; figures and equations:</p>
<pre><code>article {
  counter-reset: figure equation;
}
.figure {
  counter-increment: figure;
}
.figure::before {
  content: "Figure " counter(figure) ": ";
  font-weight: bold;
}
.equation {
  counter-increment: equation;
}
.equation::after {
  content: " (" counter(equation) ")";
  float: right;
}</code></pre>

<p><strong>Counter styles &mdash; not just numbers</strong>:</p>
<pre><code>.alpha li::before {
  content: counter(item, lower-alpha) ". ";
  /* a. b. c. d. */
}
.roman li::before {
  content: counter(item, upper-roman) ". ";
  /* I. II. III. */
}</code></pre>

<p>Available styles: <code>decimal</code>, <code>decimal-leading-zero</code>, <code>lower-alpha</code>, <code>upper-alpha</code>, <code>lower-roman</code>, <code>upper-roman</code>, <code>lower-greek</code>, plus localized variants like <code>cjk-ideographic</code>, <code>arabic-indic</code>.</p>

<p><strong>Custom counter styles</strong> via <code>@counter-style</code> (advanced):</p>
<pre><code>@counter-style emoji-numbers {
  system: cyclic;
  symbols: "&#127811;" "&#127812;" "&#127820;" "&#127813;";
  suffix: " ";
}

ul.fruit-list {
  list-style: emoji-numbers;
}</code></pre>

<p><strong>Why use CSS counters over manual <code>&lt;ol&gt;</code>:</strong></p>
<ul>
  <li><strong>Style any element</strong> &mdash; counter chapters with <code>&lt;h1&gt;</code>, not just <code>&lt;li&gt;</code>.</li>
  <li><strong>Hierarchical chains</strong> &mdash; "1.2.3" auto-generated.</li>
  <li><strong>Multiple parallel counters</strong> &mdash; figures and tables independently.</li>
  <li><strong>Custom prefixes</strong> &mdash; "Step 1:", "Question 1.", "&sect; 1.2".</li>
</ul>

<p>For long-form structured documents (legal, academic, technical books), CSS counters provide far more typographic control than the default <code>&lt;ol&gt;</code> behavior.</p>
'''

ANSWERS[68] = r'''
<p>A CSS-only flip card uses 3D transforms to rotate between two faces &mdash; the front shows by default; hover or click flips to reveal the back. Three properties make it work: <code>perspective</code>, <code>transform-style: preserve-3d</code>, and <code>backface-visibility: hidden</code>.</p>

<pre><code>&lt;div class="flip-card"&gt;
  &lt;div class="flip-inner"&gt;
    &lt;div class="flip-front"&gt;
      &lt;img src="profile.jpg" alt=""&gt;
      &lt;h3&gt;Hover for details&lt;/h3&gt;
    &lt;/div&gt;
    &lt;div class="flip-back"&gt;
      &lt;h3&gt;About this person&lt;/h3&gt;
      &lt;p&gt;Senior engineer with 10+ years experience...&lt;/p&gt;
      &lt;a href="#"&gt;Read more&lt;/a&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .flip-card {
    width: 250px;
    height: 350px;
    perspective: 1000px;       /* enables 3D space */
  }

  .flip-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;     /* children render in 3D */
    transition: transform 0.7s;
  }

  .flip-card:hover .flip-inner {
    transform: rotateY(180deg);
  }

  .flip-front,
  .flip-back {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;       /* hide when facing away */
    border-radius: 12px;
    padding: 1em;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .flip-front {
    background: white;
    border: 1px solid #e0e0e0;
  }
  .flip-front img {
    width: 80%;
    border-radius: 50%;
  }

  .flip-back {
    background: #0066cc;
    color: white;
    transform: rotateY(180deg);   /* start flipped, so we see it after rotation */
  }
&lt;/style&gt;</code></pre>

<p><strong>The three magic ingredients:</strong></p>
<ol>
  <li><strong><code>perspective: 1000px</code> on the parent</strong> &mdash; gives the 3D scene a viewing distance. Without it, rotation is flat (no perspective).</li>
  <li><strong><code>transform-style: preserve-3d</code></strong> &mdash; children render in their own 3D positions instead of being flattened.</li>
  <li><strong><code>backface-visibility: hidden</code></strong> &mdash; faces hide when rotated past 90&deg; (otherwise you&rsquo;d see the back of the front face overlaid on the back face).</li>
</ol>

<p><strong>Trigger variations:</strong></p>
<pre><code>/* Hover (default) */
.flip-card:hover .flip-inner {
  transform: rotateY(180deg);
}

/* Click using checkbox hack */
&lt;input type="checkbox" id="flip-toggle"&gt;
&lt;label for="flip-toggle"&gt;
  &lt;div class="flip-card"&gt;...&lt;/div&gt;
&lt;/label&gt;

#flip-toggle:checked + label .flip-inner {
  transform: rotateY(180deg);
}

/* Class toggle (with JavaScript) */
.flip-card.flipped .flip-inner {
  transform: rotateY(180deg);
}</code></pre>

<p><strong>Direction options:</strong></p>
<table>
  <tr><th>Transform</th><th>Direction</th></tr>
  <tr><td><code>rotateY(180deg)</code></td><td>Horizontal flip (around vertical axis)</td></tr>
  <tr><td><code>rotateX(180deg)</code></td><td>Vertical flip (around horizontal axis)</td></tr>
  <tr><td><code>rotate3d(1, 1, 0, 180deg)</code></td><td>Diagonal flip</td></tr>
</table>

<p><strong>Accessibility considerations:</strong></p>
<ul>
  <li><strong>Hover-only triggers fail on touch</strong> &mdash; mobile users have no hover. Use click/tap toggle on touch devices: <code>@media (hover: hover) { .flip-card:hover ... }</code>.</li>
  <li><strong>Hidden content invisible to focus</strong> &mdash; back face content can&rsquo;t receive keyboard focus while rotated; consider toggling visibility instead.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; instant flip rather than 0.7s rotation:
<pre><code>@media (prefers-reduced-motion: reduce) {
  .flip-inner { transition: none; }
}</code></pre></li>
</ul>

<p>For genuinely interactive flip cards (clickable details, complex content), pair the visual flip with proper ARIA expanded/collapsed semantics &mdash; pure CSS is for the visual; semantics come from markup.</p>
'''

ANSWERS[69] = r'''
<p>The <code>object-position</code> property controls <strong>where an image (or video) sits within its container box</strong> &mdash; especially useful with <code>object-fit: cover</code> or <code>contain</code> when the aspect ratios don&rsquo;t match. Default is <code>50% 50%</code> (centered).</p>

<pre><code>&lt;img src="portrait.jpg" alt="" class="thumbnail"&gt;

&lt;style&gt;
  .thumbnail {
    width: 200px;
    height: 100px;
    object-fit: cover;
    object-position: center top;     /* show top of image */
  }
&lt;/style&gt;</code></pre>

<p><strong>The relationship with <code>object-fit</code>:</strong></p>
<table>
  <tr><th>object-fit</th><th>Behavior</th><th>object-position controls</th></tr>
  <tr><td><code>fill</code> (default)</td><td>Stretches to fill, distorting</td><td>Nothing visible (no overflow)</td></tr>
  <tr><td><code>contain</code></td><td>Fits entirely inside box; may letterbox</td><td>Where image sits within letterbox space</td></tr>
  <tr><td><code>cover</code></td><td>Fills box, cropping if needed</td><td>Which part is shown vs cropped</td></tr>
  <tr><td><code>none</code></td><td>Native size; may overflow or be smaller</td><td>Position within container</td></tr>
  <tr><td><code>scale-down</code></td><td>Smaller of <code>none</code> and <code>contain</code></td><td>Position when smaller than box</td></tr>
</table>

<p><strong>Common position values:</strong></p>
<pre><code>img.face-shot {
  object-fit: cover;
  object-position: center top;     /* show face at top */
}

img.product-feature {
  object-fit: cover;
  object-position: 75% 25%;        /* feature in upper-right area */
}

img.left-aligned {
  object-fit: cover;
  object-position: left center;
}

img.bottom-aligned {
  object-fit: cover;
  object-position: bottom;          /* show bottom of image */
}</code></pre>

<p><strong>Coordinate system:</strong></p>
<ul>
  <li><strong>First value</strong> &mdash; horizontal position (<code>0%</code> = left, <code>50%</code> = center, <code>100%</code> = right).</li>
  <li><strong>Second value</strong> &mdash; vertical (<code>0%</code> = top, <code>100%</code> = bottom).</li>
  <li><strong>Single keyword</strong> &mdash; like <code>top</code> or <code>left</code>; the other axis defaults to <code>center</code>.</li>
  <li><strong>Negative values allowed</strong> &mdash; reveals area outside the natural image bounds.</li>
</ul>

<p><strong>Real-world: portrait photos in landscape thumbnails</strong>:</p>
<pre><code>.team-grid img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  object-position: center top;     /* always shows the face, not torso */
  border-radius: 50%;
}</code></pre>

<p>Without <code>object-position: center top</code>, square crop of a portrait often cuts off the head &mdash; with it, the upper portion (face) is preserved.</p>

<p><strong>Animation</strong> &mdash; <code>object-position</code> is animatable:</p>
<pre><code>.zoom-pan {
  object-fit: cover;
  object-position: 0% 50%;
  transition: object-position 0.5s;
}
.zoom-pan:hover {
  object-position: 100% 50%;     /* pan from left to right on hover */
}</code></pre>

<p>Smooth pan effects without changing image source.</p>

<p><strong>Together with <code>aspect-ratio</code></strong> &mdash; the modern responsive image trifecta:</p>
<pre><code>.responsive-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  object-position: center;
}</code></pre>

<p>Fluid width, locked aspect ratio, controlled cropping &mdash; covers most thumbnail use cases.</p>
'''

ANSWERS[70] = r'''
<p>A modern hero section uses CSS Grid for layout, with stacked backgrounds for visual depth, fluid typography via <code>clamp()</code>, and proper viewport sizing with <code>dvh</code> for mobile. The result: a striking, accessible, performant hero that adapts to any device.</p>

<pre><code>&lt;section class="hero"&gt;
  &lt;div class="hero-content"&gt;
    &lt;p class="eyebrow"&gt;New release&lt;/p&gt;
    &lt;h1&gt;Build remarkable products&lt;/h1&gt;
    &lt;p class="lead"&gt;The toolkit modern teams choose to ship faster.&lt;/p&gt;
    &lt;div class="cta-row"&gt;
      &lt;a href="/start" class="btn btn-primary"&gt;Get started&lt;/a&gt;
      &lt;a href="/demo" class="btn btn-secondary"&gt;Watch demo&lt;/a&gt;
    &lt;/div&gt;
  &lt;/div&gt;

  &lt;div class="hero-visual"&gt;
    &lt;img src="hero-illustration.svg" alt="" loading="eager"&gt;
  &lt;/div&gt;
&lt;/section&gt;

&lt;style&gt;
  .hero {
    /* Stacked backgrounds: gradient over image */
    background:
      linear-gradient(135deg, rgba(0, 102, 204, 0.05), rgba(255, 107, 53, 0.05)),
      url("hero-bg.jpg") center / cover no-repeat;

    min-height: 80dvh;        /* dynamic viewport height */

    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 4em;
    padding: 4em 2em;
    max-width: 1400px;
    margin: 0 auto;
  }

  .hero-content {
    display: flex;
    flex-direction: column;
    gap: 1em;
    max-width: 540px;
  }

  .eyebrow {
    color: #0066cc;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.85em;
    margin: 0;
  }

  h1 {
    font-size: clamp(2rem, 5vw + 1rem, 4rem);
    line-height: 1.1;
    margin: 0;
    letter-spacing: -0.02em;
  }

  .lead {
    font-size: clamp(1rem, 1.5vw + 0.5rem, 1.25rem);
    color: #555;
    line-height: 1.6;
    margin: 0;
  }

  .cta-row {
    display: flex;
    gap: 1em;
    margin-top: 1em;
  }

  .btn {
    padding: 0.85em 1.75em;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .btn-primary {
    background: #0066cc;
    color: white;
  }
  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 102, 204, 0.3);
  }
  .btn-secondary {
    background: white;
    color: #333;
    border: 2px solid #e0e0e0;
  }

  .hero-visual img {
    width: 100%;
    height: auto;
  }

  /* Mobile: stack */
  @media (max-width: 900px) {
    .hero {
      grid-template-columns: 1fr;
      gap: 2em;
      text-align: center;
      padding: 3em 1.5em;
    }
    .hero-content { align-items: center; }
    .cta-row { justify-content: center; }
    .hero-visual { order: -1; }   /* image first on mobile */
  }
&lt;/style&gt;</code></pre>

<p><strong>Key techniques explained:</strong></p>
<ul>
  <li><strong>Grid 1fr 1fr</strong> &mdash; equal halves for content and visual; collapses to single column on mobile.</li>
  <li><strong>min-height: 80dvh</strong> &mdash; dynamic viewport unit; reflects actual visible viewport, including mobile chrome adjustments.</li>
  <li><strong>clamp() typography</strong> &mdash; <code>clamp(2rem, 5vw + 1rem, 4rem)</code> scales fluidly between 2rem (small) and 4rem (large) without media queries.</li>
  <li><strong>Stacked backgrounds</strong> &mdash; gradient on top of an image gives subtle color tint without darkening overlay.</li>
  <li><strong><code>order: -1</code> on mobile</strong> &mdash; visual moves above the content via Grid order property.</li>
  <li><strong>letter-spacing: -0.02em</strong> on h1 &mdash; tightens large display text for modern look.</li>
</ul>

<p><strong>Performance optimizations:</strong></p>
<ul>
  <li><strong><code>loading="eager"</code></strong> on the hero image (it&rsquo;s above the fold).</li>
  <li><strong><code>fetchpriority="high"</code></strong> for LCP optimization.</li>
  <li><strong><code>&lt;link rel="preload"&gt;</code></strong> for the hero image in <code>&lt;head&gt;</code>.</li>
  <li><strong>Modern image formats</strong> (AVIF/WebP) with fallback via <code>&lt;picture&gt;</code>.</li>
</ul>

<p>The hero is typically your LCP (Largest Contentful Paint) element &mdash; optimizing it directly improves Core Web Vitals scores.</p>
'''

ANSWERS[71] = r'''
<p>The <code>contain</code> property is a <strong>performance optimization hint</strong> &mdash; it tells the browser that an element&rsquo;s rendering, layout, paint, or size effects don&rsquo;t propagate outside its boundaries. The browser can then skip work for unaffected siblings and ancestors during updates.</p>

<table>
  <tr><th>Value</th><th>Promise made</th></tr>
  <tr><td><code>none</code></td><td>No containment (default)</td></tr>
  <tr><td><code>size</code></td><td>Element&rsquo;s size doesn&rsquo;t depend on children</td></tr>
  <tr><td><code>layout</code></td><td>Children&rsquo;s layout doesn&rsquo;t affect outside elements</td></tr>
  <tr><td><code>paint</code></td><td>Descendants don&rsquo;t paint outside the element&rsquo;s box</td></tr>
  <tr><td><code>style</code></td><td>Style scope is contained (counter-reset, content)</td></tr>
  <tr><td><code>strict</code></td><td>Combination of size + layout + paint + style</td></tr>
  <tr><td><code>content</code></td><td>Combination of layout + paint + style (most common)</td></tr>
</table>

<pre><code>.card {
  contain: content;
  /* Browser knows: changes inside this card don't affect siblings */
}

.modal {
  contain: strict;
  height: 600px;
  width: 800px;
  /* Strongest containment; requires explicit size */
}

.list-item {
  contain: layout paint;
  /* List items can update independently */
}</code></pre>

<p><strong>Why it matters:</strong> when a single piece of content changes (text edit, list item update, animation), the browser normally checks if surrounding layout might be affected. <code>contain</code> tells the browser "no &mdash; only re-render inside this box," skipping work elsewhere.</p>

<p><strong>Real-world performance impact:</strong></p>
<ul>
  <li><strong>Long lists with frequent updates</strong> &mdash; chat messages, feed items, virtualized scrollers. Each item gets <code>contain: layout paint</code>; updates to one don&rsquo;t reflow the others.</li>
  <li><strong>Tooltips and popovers</strong> &mdash; <code>contain: layout</code> ensures the tooltip&rsquo;s appearing/disappearing doesn&rsquo;t shift the page.</li>
  <li><strong>Carousel slides</strong> &mdash; off-screen slides get <code>contain: strict</code> to skip painting them.</li>
  <li><strong>Cards in a grid</strong> &mdash; hovering one card with <code>contain: content</code> doesn&rsquo;t cascade re-layout to others.</li>
</ul>

<p><strong>Combined with <code>content-visibility: auto</code></strong> &mdash; even more powerful:</p>
<pre><code>.expensive-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
  /* Skip rendering off-screen sections entirely */
}</code></pre>

<p><code>content-visibility: auto</code> tells the browser to skip rendering an element when it&rsquo;s offscreen &mdash; reserving the space declared by <code>contain-intrinsic-size</code>. Result: a long article with hundreds of sections renders dramatically faster.</p>

<p><strong>Caveats:</strong></p>
<ul>
  <li><strong>Strict containment requires explicit size</strong> &mdash; <code>contain: strict</code> ignores intrinsic content size, so the element collapses unless you set width and height.</li>
  <li><strong>Layout containment changes some behaviors</strong> &mdash; <code>position: absolute</code> children are now positioned relative to the contained element; floats stay inside; <code>z-index</code> creates a new stacking context.</li>
  <li><strong>Misuse can break layouts</strong> &mdash; only apply containment where the promises actually hold.</li>
  <li><strong>Don&rsquo;t apply globally</strong> &mdash; the overhead of containment management can outweigh benefits if applied to every element.</li>
</ul>

<p><strong>When to use</strong>: long-form pages with many independent sections; carousels with many slides; lists with hundreds of items; complex dashboards with isolated widgets. <strong>When to skip</strong>: simple landing pages, small components, sites where rendering performance is already acceptable.</p>

<p>Measure first &mdash; use Performance tab in DevTools to identify expensive layout/paint operations, then apply <code>contain</code> strategically.</p>
'''

ANSWERS[72] = r'''
<p>A CSS-only timeline displays chronological events with visual flow &mdash; vertical line, alternating event cards, dot markers. Modern Grid + pseudo-elements handle it cleanly.</p>

<pre><code>&lt;ul class="timeline"&gt;
  &lt;li&gt;
    &lt;time&gt;Jan 2026&lt;/time&gt;
    &lt;h3&gt;Project kickoff&lt;/h3&gt;
    &lt;p&gt;Initial planning and team formation.&lt;/p&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;time&gt;Feb 2026&lt;/time&gt;
    &lt;h3&gt;Design phase complete&lt;/h3&gt;
    &lt;p&gt;Approved mockups and design system.&lt;/p&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;time&gt;Mar 2026&lt;/time&gt;
    &lt;h3&gt;MVP launched&lt;/h3&gt;
    &lt;p&gt;Beta version released to users.&lt;/p&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;time&gt;Apr 2026&lt;/time&gt;
    &lt;h3&gt;Public release&lt;/h3&gt;
    &lt;p&gt;Full launch with marketing campaign.&lt;/p&gt;
  &lt;/li&gt;
&lt;/ul&gt;

&lt;style&gt;
  .timeline {
    list-style: none;
    padding: 2em 0;
    position: relative;
    max-width: 600px;
    margin: 0 auto;
  }

  /* The vertical line */
  .timeline::before {
    content: "";
    position: absolute;
    left: 32px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e0e0e0;
  }

  .timeline li {
    position: relative;
    padding-left: 70px;
    padding-bottom: 2.5em;
  }

  /* Dot marker */
  .timeline li::before {
    content: "";
    position: absolute;
    left: 22px;
    top: 8px;
    width: 22px;
    height: 22px;
    background: #0066cc;
    border: 4px solid white;
    border-radius: 50%;
    box-shadow: 0 0 0 2px #0066cc;
  }

  .timeline time {
    display: block;
    color: #0066cc;
    font-weight: 600;
    font-size: 0.9em;
    margin-bottom: 0.25em;
  }
  .timeline h3 {
    margin: 0 0 0.5em;
  }
  .timeline p {
    color: #555;
    margin: 0;
  }
&lt;/style&gt;</code></pre>

<p><strong>Alternating layout (zigzag) &mdash; cards alternate left/right:</strong></p>
<pre><code>&lt;style&gt;
  .timeline-alt {
    list-style: none;
    padding: 2em 0;
    position: relative;
    max-width: 800px;
    margin: 0 auto;
  }
  .timeline-alt::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e0e0e0;
    transform: translateX(-50%);
  }
  .timeline-alt li {
    width: 50%;
    padding: 0 2em;
    margin-bottom: 2em;
    position: relative;
  }
  .timeline-alt li:nth-child(odd) {
    margin-left: 50%;          /* right side */
    text-align: left;
  }
  .timeline-alt li:nth-child(even) {
    text-align: right;          /* left side */
  }
  .timeline-alt li::before {
    content: "";
    position: absolute;
    top: 8px;
    width: 16px;
    height: 16px;
    background: #0066cc;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #0066cc;
  }
  .timeline-alt li:nth-child(odd)::before {
    left: -8px;
  }
  .timeline-alt li:nth-child(even)::before {
    right: -8px;
  }

  /* Mobile: collapse to single column */
  @media (max-width: 600px) {
    .timeline-alt::before {
      left: 1em;
    }
    .timeline-alt li,
    .timeline-alt li:nth-child(odd) {
      width: 100%;
      margin-left: 0;
      padding-left: 3em;
      text-align: left;
    }
    .timeline-alt li:nth-child(odd)::before,
    .timeline-alt li:nth-child(even)::before {
      left: 0.5em;
      right: auto;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>Modern enhancements:</strong></p>
<ul>
  <li><strong>Animate dots into view</strong> with scroll-driven animations: <code>animation-timeline: view()</code> reveals each dot as it scrolls into the viewport.</li>
  <li><strong>Different colors per status</strong>: <code>data-status="completed"</code> attribute selectors color dots green/yellow/red.</li>
  <li><strong>Connector lines between sequential dots</strong> with <code>::after</code> pseudo-elements.</li>
  <li><strong>Dates in <code>&lt;time&gt;</code> elements</strong> with proper <code>datetime</code> attributes for semantics.</li>
</ul>

<p><strong>Accessibility:</strong></p>
<ul>
  <li>Use a real <code>&lt;ol&gt;</code> if order matters; <code>&lt;ul&gt;</code> if it doesn&rsquo;t.</li>
  <li>Use <code>&lt;time datetime="2026-04-26"&gt;</code> for dates &mdash; readable to assistive tech and machine-parseable.</li>
  <li>Don&rsquo;t make dot markers convey meaning that isn&rsquo;t in the text &mdash; users with no CSS still see structure from the list.</li>
</ul>
'''

ANSWERS[73] = r'''
<p>CSS transforms apply 2D and 3D geometric operations to elements &mdash; <strong>rotation, scaling, translation, skew</strong>. They&rsquo;re GPU-accelerated, don&rsquo;t affect layout, and are the foundation of high-performance animations. The <code>transform</code> property accepts multiple functions composed in sequence.</p>

<p><strong>2D transform functions:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>translate(x, y)</code></td><td>Move element</td></tr>
  <tr><td><code>translateX(n)</code> / <code>translateY(n)</code></td><td>Single-axis move</td></tr>
  <tr><td><code>rotate(deg)</code></td><td>Rotate around center</td></tr>
  <tr><td><code>scale(n)</code> / <code>scale(x, y)</code></td><td>Resize uniformly or per-axis</td></tr>
  <tr><td><code>skewX(deg)</code> / <code>skewY(deg)</code></td><td>Slant on one axis</td></tr>
  <tr><td><code>matrix(a, b, c, d, e, f)</code></td><td>Combined low-level transform</td></tr>
</table>

<p><strong>3D transform functions:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>translate3d(x, y, z)</code></td><td>Move in 3D space</td></tr>
  <tr><td><code>translateZ(n)</code></td><td>Move toward/away from viewer</td></tr>
  <tr><td><code>rotateX</code> / <code>rotateY</code> / <code>rotateZ</code></td><td>Rotate around axis</td></tr>
  <tr><td><code>scale3d(x, y, z)</code></td><td>Scale in 3D</td></tr>
  <tr><td><code>perspective(n)</code></td><td>Set viewing distance</td></tr>
</table>

<pre><code>/* Animate scale on hover */
.card {
  transform: scale(1);
  transition: transform 0.3s ease;
}
.card:hover {
  transform: scale(1.05);
}

/* Continuous rotation */
.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Multiple transforms in one keyframe */
@keyframes complex-entry {
  from { transform: translateX(-50px) scale(0.8) rotate(-5deg); opacity: 0; }
  to   { transform: translateX(0)     scale(1)   rotate(0deg);  opacity: 1; }
}</code></pre>

<p><strong>Composition order matters &mdash; transforms apply right-to-left:</strong></p>
<pre><code>/* Translate first, THEN rotate around new position */
transform: rotate(45deg) translateX(100px);

/* Translate, THEN scale */
transform: scale(2) translateX(50px);
/* This produces translateX(100px) effectively, because scale doubles the movement */</code></pre>

<p><strong>Modern individual properties (2024+ Baseline)</strong> &mdash; cleaner than the shorthand:</p>
<pre><code>.card {
  translate: 0 0;
  rotate: 0deg;
  scale: 1;
  transition: translate 0.3s, rotate 0.3s, scale 0.3s;
}
.card:hover {
  translate: 0 -4px;
  scale: 1.05;
}</code></pre>

<p>Each property animates independently &mdash; you can change <code>scale</code> without resetting <code>rotate</code>. Solves the historical problem of needing to redeclare every transform when one changes.</p>

<p><strong>Why transforms are essential for animation performance:</strong></p>
<table>
  <tr><th>Animation</th><th>What it triggers</th><th>Cost</th></tr>
  <tr><td><code>top</code> / <code>left</code></td><td>Layout + Paint + Composite</td><td>Expensive</td></tr>
  <tr><td><code>width</code> / <code>height</code></td><td>Layout + Paint + Composite</td><td>Expensive</td></tr>
  <tr><td><code>margin</code> / <code>padding</code></td><td>Layout + Paint + Composite</td><td>Expensive</td></tr>
  <tr><td><code>transform</code></td><td>Composite only</td><td>Cheap (GPU)</td></tr>
  <tr><td><code>opacity</code></td><td>Composite only</td><td>Cheap (GPU)</td></tr>
</table>

<p>Animating <code>transform</code> and <code>opacity</code> stays at 60fps even on lower-end devices. Animating layout properties like <code>width</code> often jitters because the browser must re-flow the entire page on every frame.</p>

<p><strong>3D transform setup:</strong></p>
<pre><code>.scene {
  perspective: 1000px;        /* enables 3D */
}
.cube {
  transform-style: preserve-3d;     /* children render in 3D */
}
.face {
  backface-visibility: hidden;       /* hide faces facing away */
}</code></pre>

<p>The trio (perspective + preserve-3d + backface-visibility) is the foundation of 3D card flips, rotating menus, and immersive scenes.</p>

<p><strong>Common animation patterns:</strong></p>
<ul>
  <li><strong>Hover lift</strong>: <code>transform: translateY(-4px)</code></li>
  <li><strong>Click squish</strong>: <code>transform: scale(0.97)</code> on <code>:active</code></li>
  <li><strong>Slide-in entry</strong>: animate from <code>translateX(-100%)</code> to <code>translateX(0)</code></li>
  <li><strong>Fade-and-grow</strong>: combine <code>opacity</code> with <code>scale(0.95)</code> to <code>scale(1)</code></li>
  <li><strong>Carousel slide</strong>: <code>transform: translateX(-N * 100%)</code> per slide index</li>
</ul>
'''

ANSWERS[74] = r'''
<p>Equal-height columns are a Flexbox built-in: by default, items in a flex row stretch to match the tallest sibling. Combined with internal Flex/<code>margin-top: auto</code>, you get visual alignment of CTAs, footers, or other internal elements across cards.</p>

<pre><code>&lt;section class="card-row"&gt;
  &lt;article class="card"&gt;
    &lt;img src="1.jpg" alt=""&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;Short title&lt;/h3&gt;
      &lt;p&gt;Brief.&lt;/p&gt;
      &lt;a href="#" class="btn"&gt;Learn more&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;

  &lt;article class="card"&gt;
    &lt;img src="2.jpg" alt=""&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;A much longer title that wraps&lt;/h3&gt;
      &lt;p&gt;Lorem ipsum dolor sit amet, consectetur adipiscing.&lt;/p&gt;
      &lt;a href="#" class="btn"&gt;Learn more&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;

  &lt;article class="card"&gt;
    &lt;img src="3.jpg" alt=""&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;Medium title&lt;/h3&gt;
      &lt;p&gt;Some content here that goes on for a few lines explaining things.&lt;/p&gt;
      &lt;a href="#" class="btn"&gt;Learn more&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .card-row {
    display: flex;
    gap: 1.5em;
    /* align-items: stretch is the default — equalizes heights */
  }

  .card {
    flex: 1;                       /* equal widths */

    /* Internal flex column for vertical alignment */
    display: flex;
    flex-direction: column;

    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .card img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
  }

  .card-body {
    padding: 1.5em;
    display: flex;
    flex-direction: column;
    flex: 1;                       /* fill remaining card height */
  }

  .card h3 {
    margin: 0 0 0.5em;
  }

  .card p {
    color: #555;
    margin: 0;
    flex: 1;                       /* push CTA to bottom */
  }

  .btn {
    align-self: start;             /* button doesn't stretch */
    margin-top: 1em;
    padding: 0.5em 1.25em;
    background: #0066cc;
    color: white;
    border-radius: 4px;
    text-decoration: none;
  }
&lt;/style&gt;</code></pre>

<p><strong>Three layers of equal-height alignment:</strong></p>
<ol>
  <li><strong>Outer row</strong> &mdash; <code>display: flex</code> with default <code>align-items: stretch</code> equalizes card heights.</li>
  <li><strong>Inner card column</strong> &mdash; <code>display: flex; flex-direction: column; flex: 1</code> on <code>.card-body</code> fills remaining card height.</li>
  <li><strong>CTA alignment</strong> &mdash; <code>flex: 1</code> on the paragraph pushes the button to the bottom; result: all buttons aligned across cards regardless of content length.</li>
</ol>

<p><strong>Wrap responsively</strong> for narrow screens:</p>
<pre><code>.card-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5em;
}
.card {
  flex: 1 1 280px;          /* min 280px; wraps when no room */
}</code></pre>

<p>With <code>flex-wrap: wrap</code> + <code>flex: 1 1 280px</code>, cards reflow naturally:</p>
<ul>
  <li>Wide screens: 4-5 cards per row.</li>
  <li>Tablet: 2-3 cards per row.</li>
  <li>Phone: 1 card per row.</li>
</ul>
<p>Each row contains cards of equal height; rows are independent.</p>

<p><strong>The <code>align-items</code> alternatives</strong>:</p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>stretch</code> (default)</td><td>Items fill cross-axis &mdash; equal heights</td></tr>
  <tr><td><code>flex-start</code></td><td>Items align to top; heights vary</td></tr>
  <tr><td><code>flex-end</code></td><td>Items align to bottom</td></tr>
  <tr><td><code>center</code></td><td>Items vertically centered</td></tr>
  <tr><td><code>baseline</code></td><td>Items align by their text baselines</td></tr>
</table>

<p>Override <code>stretch</code> only when you specifically don&rsquo;t want equal heights &mdash; the default is usually what you want.</p>

<p><strong>Grid alternative</strong> &mdash; same effect, different syntax:</p>
<pre><code>.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5em;
  /* Items stretch to row height by default */
}</code></pre>

<p>Grid&rsquo;s strength: items in the same row align even when wrapping; Flexbox&rsquo;s wrapped rows are independent.</p>
'''

ANSWERS[75] = r'''
<p>The <code>mask</code> property uses an image (or gradient) as a transparency mask &mdash; visible where the mask is opaque, invisible where transparent. It enables sophisticated visual effects: cutout shapes, soft edges, animated reveals, and SVG-clipped graphics &mdash; without changing the source.</p>

<pre><code>.feathered {
  /* Soft fade at all edges */
  mask: radial-gradient(ellipse at center, black 50%, transparent 100%);
  -webkit-mask: radial-gradient(ellipse at center, black 50%, transparent 100%);
}

.diagonal-cut {
  /* Diagonal fade */
  mask: linear-gradient(135deg, black 50%, transparent 100%);
  -webkit-mask: linear-gradient(135deg, black 50%, transparent 100%);
}

.shape-mask {
  /* Use SVG as mask shape */
  mask-image: url("/icons/star.svg");
  -webkit-mask-image: url("/icons/star.svg");
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  background: linear-gradient(135deg, #0066cc, #ff6b35);
  /* The colored gradient fills only inside the star shape */
}</code></pre>

<p><strong>Mask sub-properties</strong> (parallel to <code>background-*</code>):</p>
<table>
  <tr><th>Property</th><th>Purpose</th></tr>
  <tr><td><code>mask-image</code></td><td>The mask source (URL or gradient)</td></tr>
  <tr><td><code>mask-size</code></td><td><code>cover</code>, <code>contain</code>, <code>auto</code>, or specific dimensions</td></tr>
  <tr><td><code>mask-position</code></td><td>Where in the box</td></tr>
  <tr><td><code>mask-repeat</code></td><td><code>no-repeat</code>, <code>repeat</code>, etc.</td></tr>
  <tr><td><code>mask-mode</code></td><td><code>luminance</code> (brightness-based) or <code>alpha</code> (default)</td></tr>
  <tr><td><code>mask-composite</code></td><td>Combine multiple masks (add, subtract, intersect, exclude)</td></tr>
</table>

<p><strong>Use case: monochrome icons from SVG outlines</strong> &mdash; ship one black SVG, color it with CSS:</p>
<pre><code>.icon {
  width: 24px;
  height: 24px;
  background: var(--icon-color, currentColor);
  mask: url("/icons/heart.svg") center / contain no-repeat;
  -webkit-mask: url("/icons/heart.svg") center / contain no-repeat;
}

.icon.danger { --icon-color: red; }
.icon.success { --icon-color: green; }</code></pre>

<p>The SVG provides the shape; CSS fills with whatever background works (color, gradient, image). Theme support is trivial.</p>

<p><strong>Compared to <code>clip-path</code>:</strong></p>
<table>
  <tr><th></th><th><code>mask</code></th><th><code>clip-path</code></th></tr>
  <tr><td>Source</td><td>Image or gradient (alpha-based)</td><td>Geometric shape (path/polygon)</td></tr>
  <tr><td>Soft edges</td><td>Yes (gradient mask = fade)</td><td>No (hard cut only)</td></tr>
  <tr><td>Best for</td><td>Soft fades, image-shaped cutouts</td><td>Geometric shapes (circles, polygons)</td></tr>
  <tr><td>Performance</td><td>Composite (GPU-friendly)</td><td>Composite (GPU-friendly)</td></tr>
</table>

<p><strong>Multiple stacked masks</strong> &mdash; comma-separated layers compose:</p>
<pre><code>.complex-mask {
  mask:
    radial-gradient(circle at 30% 50%, black 30%, transparent 30%),
    radial-gradient(circle at 70% 50%, black 30%, transparent 30%);
  mask-composite: add;
}</code></pre>

<p><strong>Animation</strong> &mdash; mask properties are animatable:</p>
<pre><code>.reveal {
  mask: linear-gradient(90deg, black, black, transparent, transparent);
  mask-size: 400% 100%;
  mask-position: 100% 0;
  transition: mask-position 0.6s;
}
.reveal:hover {
  mask-position: 0 0;          /* sweeps the reveal */
}</code></pre>

<p>The mask gradient slides across the element, revealing it left-to-right.</p>

<p><strong>Browser support &amp; the prefix issue:</strong> <code>mask</code> shipped without prefix in Firefox; Chromium and Safari still require <code>-webkit-mask</code> for full compatibility through 2026. Always include both for cross-browser support.</p>
'''

ANSWERS[76] = r'''
<p>A CSS-only star rating uses radio buttons with reverse stacking + the <code>~</code> general sibling combinator. Hovering a star highlights it AND all stars before it; the input&rsquo;s checked state persists the rating.</p>

<pre><code>&lt;form class="star-rating"&gt;
  &lt;input type="radio" name="rating" id="r5" value="5"&gt;
  &lt;label for="r5"&gt;5 stars&lt;/label&gt;
  &lt;input type="radio" name="rating" id="r4" value="4"&gt;
  &lt;label for="r4"&gt;4 stars&lt;/label&gt;
  &lt;input type="radio" name="rating" id="r3" value="3"&gt;
  &lt;label for="r3"&gt;3 stars&lt;/label&gt;
  &lt;input type="radio" name="rating" id="r2" value="2"&gt;
  &lt;label for="r2"&gt;2 stars&lt;/label&gt;
  &lt;input type="radio" name="rating" id="r1" value="1"&gt;
  &lt;label for="r1"&gt;1 star&lt;/label&gt;
&lt;/form&gt;

&lt;style&gt;
  .star-rating {
    display: inline-flex;
    flex-direction: row-reverse;     /* reverse so we can use ~ combinator */
    gap: 0.25em;
  }

  .star-rating input {
    display: none;
  }

  .star-rating label {
    cursor: pointer;
    font-size: 2em;
    color: #ddd;
    transition: color 0.15s;
  }
  .star-rating label::before {
    content: "&#9733;";              /* solid star */
  }

  /* Hover: highlight this label AND all that follow in reverse direction */
  .star-rating label:hover,
  .star-rating label:hover ~ label {
    color: #ffc107;
  }

  /* Checked: same effect for selected state */
  .star-rating input:checked ~ label {
    color: #ffc107;
  }

  /* Visually hide the text inside labels (accessibility-friendly) */
  .star-rating label span {
    position: absolute;
    width: 1px; height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
&lt;/style&gt;</code></pre>

<p><strong>Why <code>flex-direction: row-reverse</code>?</strong> CSS only has the <code>~</code> general sibling combinator (which selects following siblings), not a "previous sibling" selector. By reversing the visual order, we can use <code>~</code> to highlight stars to the right of the hovered/selected one &mdash; which corresponds to "lower" stars visually.</p>

<p><strong>Display-only star rating</strong> (showing existing rating, not interactive):</p>
<pre><code>&lt;div class="rating-display" data-rating="4"&gt;
  &lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;
&lt;/div&gt;

&lt;style&gt;
  .rating-display {
    display: inline-flex;
    gap: 0.25em;
    color: #ddd;
    font-size: 1.5em;
  }
  .rating-display span::before {
    content: "&#9733;";
  }
  .rating-display[data-rating="1"] span:nth-child(-n+1),
  .rating-display[data-rating="2"] span:nth-child(-n+2),
  .rating-display[data-rating="3"] span:nth-child(-n+3),
  .rating-display[data-rating="4"] span:nth-child(-n+4),
  .rating-display[data-rating="5"] span:nth-child(-n+5) {
    color: #ffc107;
  }
&lt;/style&gt;</code></pre>

<p><strong>Half-star ratings</strong> &mdash; require either an SVG icon or a CSS clip technique:</p>
<pre><code>.half-star {
  background: linear-gradient(90deg, #ffc107 50%, #ddd 50%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}</code></pre>

<p><strong>Accessibility considerations:</strong></p>
<ul>
  <li><strong>Keep the radio inputs functional</strong> &mdash; not <code>display: none</code> in modern best practice; use <code>.sr-only</code> visually-hidden technique so they remain keyboard-focusable.</li>
  <li><strong>Add visible focus styles</strong> on the labels when their input is focused: <code>input:focus + label { outline: 2px solid blue; }</code>.</li>
  <li><strong>Provide a fieldset and legend</strong>: <code>&lt;fieldset&gt;&lt;legend&gt;Rate this item&lt;/legend&gt; ... &lt;/fieldset&gt;</code> for screen readers.</li>
  <li><strong>Use <code>aria-label</code> on each label</strong> if just the text "5 stars" inside isn&rsquo;t enough context.</li>
</ul>

<p>Despite the radio input + flex-reverse trick being clever, modern projects often use a JavaScript-based rating component or an existing library &mdash; the pure-CSS approach struggles with half-stars, animations, and tablet/touch interactions. Use the CSS pattern when zero JavaScript is a real constraint; otherwise, a small JS component is more flexible.</p>
'''

ANSWERS[77] = r'''
<p>The <code>perspective</code> property defines <strong>how far the viewer is from the 3D scene</strong> &mdash; smaller values create more dramatic perspective (objects appear distorted at angles); larger values produce subtle perspective (almost orthographic).</p>

<p>Without perspective, 3D rotations look flat &mdash; rotating a card by <code>rotateY(45deg)</code> just appears to compress horizontally. Perspective gives objects a sense of depth.</p>

<pre><code>.scene {
  perspective: 1000px;        /* viewer distance */
}

.card {
  transform: rotateY(45deg);
  /* With parent perspective, this looks 3D — closer edge larger, farther edge smaller */
}</code></pre>

<p><strong>Perspective values &mdash; visual effect:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>200px</code></td><td>Extreme distortion; viewer very close</td></tr>
  <tr><td><code>500px</code></td><td>Strong perspective; dramatic angles</td></tr>
  <tr><td><code>1000px</code></td><td>Moderate; subtle depth (most common)</td></tr>
  <tr><td><code>2000px+</code></td><td>Almost flat; gentle perspective</td></tr>
  <tr><td><code>none</code></td><td>No perspective (flat)</td></tr>
</table>

<p><strong>Two ways to set perspective:</strong></p>

<p><strong>1. As a property on the parent</strong> &mdash; all children share the same viewing distance:</p>
<pre><code>.scene {
  perspective: 1000px;
}
.scene .item-1 { transform: rotateY(45deg); }
.scene .item-2 { transform: rotateX(30deg); }
/* Both render with the same perspective */</code></pre>

<p><strong>2. As part of the <code>transform</code> shorthand</strong> &mdash; per-element perspective:</p>
<pre><code>.card-1 {
  transform: perspective(500px) rotateY(45deg);
}
.card-2 {
  transform: perspective(2000px) rotateY(45deg);
  /* Same rotation; different visual effect */
}</code></pre>

<p>Use the parent property when multiple elements should appear in the same 3D scene (consistent vanishing point). Use the function when each element has its own independent transform.</p>

<p><strong>Common 3D pattern &mdash; flip card setup:</strong></p>
<pre><code>.flip-container {
  perspective: 1000px;
  width: 200px;
  height: 200px;
}
.flip-card {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;     /* children render in 3D */
  transition: transform 0.6s;
}
.flip-container:hover .flip-card {
  transform: rotateY(180deg);
}
.flip-card .face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
}</code></pre>

<p><strong>Three properties work together:</strong></p>
<ul>
  <li><strong><code>perspective</code></strong> &mdash; sets the viewing distance for the 3D scene.</li>
  <li><strong><code>transform-style: preserve-3d</code></strong> &mdash; children render in 3D space (instead of being flattened).</li>
  <li><strong><code>backface-visibility: hidden</code></strong> &mdash; faces of cards/elements hide when rotated past 90&deg;.</li>
</ul>

<p><strong>Adjusting the vanishing point with <code>perspective-origin</code></strong>:</p>
<pre><code>.scene {
  perspective: 1000px;
  perspective-origin: 50% 0;       /* vanishing point at top center */
}
/* Default is "50% 50%" (center). Adjust for camera angle effect. */</code></pre>

<p>Moving the perspective origin shifts how 3D-rotated children appear &mdash; useful for "looking up" or "looking down" effects.</p>

<p><strong>Practical use cases:</strong></p>
<ul>
  <li><strong>Card flip animations</strong> (most common).</li>
  <li><strong>Cube galleries</strong> &mdash; rotating navigations through 3D faces.</li>
  <li><strong>Tilt-on-hover effects</strong> &mdash; subtle 3D lift on cards.</li>
  <li><strong>Carousel transitions</strong> &mdash; coverflow-style gallery.</li>
  <li><strong>Hero animations</strong> &mdash; depth in product showcases.</li>
</ul>

<p><strong>Performance note:</strong> 3D transforms are GPU-accelerated and perform well. <code>preserve-3d</code> creates a new stacking context and rendering layer, so be aware that complex 3D scenes can affect z-index expectations and surrounding layout in subtle ways.</p>
'''

ANSWERS[78] = r'''
<p>A responsive navbar with hamburger menu shows full nav links on desktop and a toggle-able menu on mobile. The CSS-only approach uses a hidden checkbox + label combination &mdash; no JavaScript required for the toggle, though JS adds polish for accessibility.</p>

<pre><code>&lt;header class="navbar"&gt;
  &lt;a href="/" class="brand"&gt;Acme&lt;/a&gt;

  &lt;input type="checkbox" id="nav-toggle" class="nav-checkbox"&gt;
  &lt;label for="nav-toggle" class="hamburger" aria-label="Toggle menu"&gt;
    &lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;
  &lt;/label&gt;

  &lt;nav class="nav-menu"&gt;
    &lt;ul&gt;
      &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
  &lt;/nav&gt;
&lt;/header&gt;

&lt;style&gt;
  .navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1em 2em;
    background: white;
    border-bottom: 1px solid #eee;
  }

  .brand {
    font-weight: bold;
    font-size: 1.2em;
    text-decoration: none;
    color: #333;
  }

  /* Hide checkbox and hamburger on desktop */
  .nav-checkbox,
  .hamburger {
    display: none;
  }

  /* Desktop nav menu */
  .nav-menu ul {
    display: flex;
    gap: 2em;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .nav-menu a {
    color: #333;
    text-decoration: none;
  }
  .nav-menu a:hover {
    color: #0066cc;
  }

  /* Mobile (≤768px) */
  @media (max-width: 768px) {
    .hamburger {
      display: flex;
      flex-direction: column;
      gap: 5px;
      cursor: pointer;
      padding: 0.5em;
    }
    .hamburger span {
      width: 25px;
      height: 3px;
      background: #333;
      transition: transform 0.3s, opacity 0.3s;
    }

    /* Hamburger animates to X when checked */
    .nav-checkbox:checked + .hamburger span:nth-child(1) {
      transform: rotate(45deg) translate(6px, 6px);
    }
    .nav-checkbox:checked + .hamburger span:nth-child(2) {
      opacity: 0;
    }
    .nav-checkbox:checked + .hamburger span:nth-child(3) {
      transform: rotate(-45deg) translate(6px, -6px);
    }

    /* Mobile menu hidden by default */
    .nav-menu {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: white;
      border-top: 1px solid #eee;
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s;
    }
    .nav-checkbox:checked ~ .nav-menu {
      max-height: 400px;
    }
    .nav-menu ul {
      flex-direction: column;
      padding: 1em;
      gap: 0.5em;
    }
    .nav-menu a {
      display: block;
      padding: 0.5em;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>How the CSS-only toggle works:</strong></p>
<ol>
  <li><strong>Hidden checkbox</strong> tracks the open/closed state.</li>
  <li><strong>Label associated with the checkbox</strong> &mdash; clicking the hamburger toggles it.</li>
  <li><strong>Sibling combinator <code>~</code></strong> &mdash; <code>.nav-checkbox:checked ~ .nav-menu</code> matches the menu only when the checkbox is checked.</li>
  <li><strong>Animated hamburger-to-X</strong> &mdash; the three lines rotate to form an X when checked.</li>
</ol>

<p><strong>Accessibility improvements (require JavaScript):</strong></p>
<pre><code>&lt;button class="hamburger"
        aria-controls="nav-menu"
        aria-expanded="false"
        aria-label="Toggle navigation"&gt;
  &lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;
&lt;/button&gt;

&lt;script&gt;
  const button = document.querySelector(".hamburger");
  const menu = document.getElementById("nav-menu");

  button.addEventListener("click", () =&gt; {
    const isOpen = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!isOpen));
    menu.classList.toggle("open");
  });

  // Close on Esc
  document.addEventListener("keydown", (e) =&gt; {
    if (e.key === "Escape") {
      button.setAttribute("aria-expanded", "false");
      menu.classList.remove("open");
    }
  });
&lt;/script&gt;</code></pre>

<p>Proper ARIA attributes (<code>aria-expanded</code>, <code>aria-controls</code>) communicate state to screen readers; Esc key closes the menu; focus management ensures keyboard users can navigate.</p>

<p><strong>Modern alternative: <code>&lt;dialog&gt;</code> + Popover API</strong> &mdash; built-in dismiss-on-Esc, focus management, and top-layer rendering for full-screen mobile menus. Worth considering for greenfield projects.</p>
'''

ANSWERS[79] = r'''
<p><strong>Intrinsic sizing</strong> sizes elements based on their <em>content</em>; <strong>extrinsic sizing</strong> sizes them based on the available space (parent dimensions, viewport, or specified values). The distinction is foundational to understanding CSS layout behavior.</p>

<table>
  <tr><th></th><th>Intrinsic</th><th>Extrinsic</th></tr>
  <tr><td>Sized by</td><td>Content</td><td>Container/specified value</td></tr>
  <tr><td>Examples</td><td><code>auto</code>, <code>min-content</code>, <code>max-content</code>, <code>fit-content</code></td><td><code>100%</code>, <code>50vw</code>, <code>300px</code>, <code>1fr</code></td></tr>
  <tr><td>Reflows when</td><td>Content changes</td><td>Container changes</td></tr>
</table>

<p><strong>Intrinsic sizing keywords:</strong></p>
<table>
  <tr><th>Keyword</th><th>Meaning</th></tr>
  <tr><td><code>auto</code></td><td>Computed from content (default for height; for width depends on element type)</td></tr>
  <tr><td><code>min-content</code></td><td>Smallest size content can take without overflow (e.g., longest word)</td></tr>
  <tr><td><code>max-content</code></td><td>Largest natural size of content (no wrapping)</td></tr>
  <tr><td><code>fit-content</code></td><td>min(max-content, available)</td></tr>
  <tr><td><code>fit-content(n)</code></td><td><code>fit-content</code> with a maximum of <code>n</code></td></tr>
</table>

<pre><code>&lt;div class="container"&gt;
  &lt;p class="min"&gt;Hello world this is a long sentence to demonstrate&lt;/p&gt;
  &lt;p class="max"&gt;Hello world this is a long sentence to demonstrate&lt;/p&gt;
  &lt;p class="fit"&gt;Hello world this is a long sentence to demonstrate&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  .container { width: 300px; border: 1px solid; }
  .min { width: min-content; }    /* width = longest word ("demonstrate") */
  .max { width: max-content; }    /* width = full sentence (overflows) */
  .fit { width: fit-content; }    /* width = min(max-content, 300px) = 300px */
&lt;/style&gt;</code></pre>

<p><strong>Common practical uses:</strong></p>

<p><strong>1. Tables sized to content:</strong></p>
<pre><code>.data-table {
  width: max-content;       /* table fits content; doesn't fill parent */
}</code></pre>

<p><strong>2. Tooltips that wrap nicely:</strong></p>
<pre><code>.tooltip {
  width: max-content;
  max-width: 300px;
  /* Naturally wraps at 300px; otherwise sized to content */
}</code></pre>

<p><strong>3. Buttons that fit their label:</strong></p>
<pre><code>.btn {
  width: fit-content;       /* button = label width */
  padding: 0.5em 1em;
}</code></pre>

<p><strong>4. Grid columns sized to content:</strong></p>
<pre><code>.grid {
  display: grid;
  grid-template-columns: max-content 1fr;
  /* First column hugs content; second fills remaining */
}</code></pre>

<p><strong>The "default sizing" of various elements:</strong></p>
<table>
  <tr><th>Element type</th><th>Default width</th><th>Default height</th></tr>
  <tr><td>Block (<code>div</code>, <code>p</code>)</td><td>Extrinsic (100% of parent)</td><td>Intrinsic (content)</td></tr>
  <tr><td>Inline (<code>span</code>, <code>a</code>)</td><td>Intrinsic (content)</td><td>Intrinsic (content)</td></tr>
  <tr><td>Inline-block</td><td>Intrinsic (content)</td><td>Intrinsic (content)</td></tr>
  <tr><td>Replaced (<code>img</code>, <code>video</code>)</td><td>Intrinsic (natural size)</td><td>Intrinsic (natural size)</td></tr>
  <tr><td>Flex item</td><td>Depends on <code>flex-basis</code></td><td>Cross-axis stretch</td></tr>
</table>

<p><strong>Why this matters for layout:</strong></p>
<ul>
  <li><strong>Flexbox <code>flex-basis: 0</code></strong> &mdash; ignores intrinsic content; items size to <code>flex-grow</code> ratios. <code>flex-basis: auto</code> uses intrinsic size as a starting point.</li>
  <li><strong>Grid <code>auto</code> rows/columns</strong> &mdash; size based on intrinsic content of the largest item.</li>
  <li><strong>Image with no width/height attributes</strong> &mdash; uses intrinsic size; can cause CLS as it loads. Modern fix: aspect-ratio + width specifies extrinsically.</li>
  <li><strong>Long words breaking layout</strong> &mdash; happens when min-content of an element exceeds parent width.</li>
</ul>

<p><strong>The <code>writing-mode</code> connection:</strong> "intrinsic" applies to both block and inline directions but is most often discussed for the inline direction (typically width). For vertical writing modes, the same concepts apply to height.</p>
'''

ANSWERS[80] = r'''
<p>Masonry layouts pack items of varying heights into columns &mdash; like Pinterest. Pre-2024, this required JavaScript libraries (Masonry.js, Isotope) or column-based hacks. <strong>2024+ gives us native CSS masonry</strong> via Grid extensions, with several fallback strategies during the transition period.</p>

<p><strong>Method 1: <code>grid-template-rows: masonry</code></strong> &mdash; the future, currently only Firefox (with flag), behind feature flags elsewhere:</p>
<pre><code>.masonry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-template-rows: masonry;       /* Pinterest-style packing */
  gap: 1em;
}</code></pre>

<p>Browsers debate two competing proposals (Grid masonry vs new <code>display: masonry</code>); production-ready support remains limited through 2026.</p>

<p><strong>Method 2: CSS columns (most reliable today):</strong></p>
<pre><code>.masonry-columns {
  columns: 4 200px;            /* up to 4 columns, min 200px each */
  column-gap: 1em;
}
.masonry-columns &gt; * {
  break-inside: avoid;          /* don't split items across columns */
  margin-bottom: 1em;
  display: block;               /* required for proper sizing */
}</code></pre>

<p>This works in all browsers. Items flow top-to-bottom in column 1, then 2, then 3 &mdash; not the natural left-to-right order. For most masonry layouts (galleries, Pinterest-style), this column-flow is what users expect.</p>

<p><strong>Method 3: JavaScript-driven Grid (most flexible):</strong></p>
<pre><code>&lt;div class="masonry-grid"&gt;
  &lt;div class="item" style="--span: 30"&gt;...&lt;/div&gt;
  &lt;div class="item" style="--span: 18"&gt;...&lt;/div&gt;
  &lt;div class="item" style="--span: 25"&gt;...&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .masonry-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    grid-auto-rows: 10px;        /* small row height for fine control */
    gap: 1em;
  }
  .item {
    grid-row-end: span var(--span);
    /* Each item declares how many rows it spans */
  }
&lt;/style&gt;

&lt;script&gt;
  // After images load, calculate row span based on content height
  document.querySelectorAll(".item").forEach(item =&gt; {
    const height = item.getBoundingClientRect().height;
    const rowSpan = Math.ceil((height + 16) / (10 + 16));
    item.style.setProperty("--span", rowSpan);
  });
&lt;/script&gt;</code></pre>

<p>This gives row-by-row alignment (more like a true brick wall) but requires JavaScript to measure heights.</p>

<p><strong>Comparison of approaches:</strong></p>
<table>
  <tr><th>Method</th><th>Browser support</th><th>Order</th><th>JavaScript needed</th></tr>
  <tr><td>Native masonry (Grid)</td><td>Limited (2026)</td><td>Top-to-bottom</td><td>No</td></tr>
  <tr><td>CSS columns</td><td>All browsers</td><td>Top-to-bottom in columns</td><td>No</td></tr>
  <tr><td>Grid with row-span hack</td><td>All browsers</td><td>Left-to-right</td><td>Yes (measure heights)</td></tr>
  <tr><td>Library (Masonry.js)</td><td>All browsers</td><td>Configurable</td><td>Yes (the library)</td></tr>
</table>

<p><strong>For Pinterest-style "browse by column" feel</strong> &mdash; CSS columns are great. Source order is preserved, items reflow when columns wrap.</p>

<p><strong>For row-aligned masonry</strong> &mdash; native CSS grid masonry (when shipped) or JavaScript libraries.</p>

<p><strong>Modern responsive enhancements:</strong></p>
<pre><code>.masonry-columns {
  columns: 4 200px;
}
@media (max-width: 768px) { .masonry-columns { columns: 2 200px; } }
@media (max-width: 480px) { .masonry-columns { columns: 1; } }</code></pre>

<p>Or use the auto-flow naturally: <code>columns: 4 200px</code> automatically reduces columns when there&rsquo;s no room.</p>

<p><strong>Performance:</strong> CSS columns are very fast; the browser handles flow automatically. JavaScript-based masonry libraries can be slow with many items because they re-layout on every change. For 50+ items, prefer the columns approach.</p>
'''

ANSWERS[81] = r'''
<p>The <code>shape-outside</code> property makes <strong>floated elements have non-rectangular shapes for text wrapping</strong>. Text flows around circles, polygons, and image silhouettes &mdash; like magazine layouts where text hugs irregular shapes.</p>

<pre><code>&lt;article&gt;
  &lt;img src="profile.jpg" alt="" class="circle-profile"&gt;
  &lt;p&gt;Lorem ipsum dolor sit amet, consectetur adipiscing elit.
     The text wraps around this circular profile photo, creating
     a magazine-style layout that feels much more polished than
     traditional rectangular floats. As the paragraph continues,
     the text follows the circular outline of the image...&lt;/p&gt;
&lt;/article&gt;

&lt;style&gt;
  .circle-profile {
    float: left;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin: 0 1em 1em 0;

    shape-outside: circle(50%);    /* text wraps around circle, not box */
  }
&lt;/style&gt;</code></pre>

<p><strong>Critical: <code>shape-outside</code> only works on floated elements.</strong> Without <code>float: left</code> or <code>float: right</code>, the property has no effect.</p>

<p><strong>Shape function values:</strong></p>
<table>
  <tr><th>Function</th><th>Use</th></tr>
  <tr><td><code>circle(radius at x y)</code></td><td>Circle wrap</td></tr>
  <tr><td><code>ellipse(rx ry at x y)</code></td><td>Ellipse wrap</td></tr>
  <tr><td><code>polygon(x1 y1, x2 y2, ...)</code></td><td>Custom shape from points</td></tr>
  <tr><td><code>inset(top right bottom left)</code></td><td>Rectangle with insets</td></tr>
  <tr><td><code>url(image.png)</code></td><td>Use alpha channel of an image</td></tr>
  <tr><td><code>path("M 0 0 L 100 0 ...")</code></td><td>SVG path syntax</td></tr>
</table>

<p><strong>Wrapping around an image silhouette</strong> &mdash; powerful for product photos:</p>
<pre><code>.product {
  float: left;
  width: 200px;
  margin: 0 1em 1em 0;
  shape-outside: url("product-cutout.png");
  /* Text follows the alpha channel — fits around the product silhouette */
}</code></pre>

<p>The image must be served with appropriate CORS headers if cross-origin (set <code>crossorigin="anonymous"</code> on the <code>&lt;img&gt;</code> if applicable).</p>

<p><strong>Custom polygon shapes:</strong></p>
<pre><code>.triangle-wrap {
  float: left;
  width: 200px;
  height: 200px;
  background: navy;
  shape-outside: polygon(0 0, 100% 100%, 0 100%);
  clip-path: polygon(0 0, 100% 100%, 0 100%);
  /* clip-path shapes the visual; shape-outside shapes the text wrap */
}</code></pre>

<p>Pair <code>shape-outside</code> with <code>clip-path</code> using the same shape &mdash; the visual cuts to that shape AND text wraps around it.</p>

<p><strong>Padding via <code>shape-margin</code>:</strong></p>
<pre><code>.circle-with-padding {
  float: left;
  shape-outside: circle(50%);
  shape-margin: 1em;          /* extra space between text and shape */
}</code></pre>

<p>Without <code>shape-margin</code>, text touches the shape edge directly &mdash; usually you want some breathing room.</p>

<p><strong>Animation</strong> &mdash; <code>shape-outside</code> is animatable when shape function syntax matches:</p>
<pre><code>.morph {
  float: left;
  width: 200px;
  height: 200px;
  shape-outside: circle(50%);
  transition: shape-outside 0.5s;
}
.morph:hover {
  shape-outside: circle(75%);
  /* Smooth animation; both endpoints use circle() */
}</code></pre>

<p>Animation requires consistent shape syntax &mdash; you can&rsquo;t animate from <code>circle()</code> to <code>polygon()</code> directly.</p>

<p><strong>Real-world use cases:</strong></p>
<ul>
  <li><strong>Magazine articles</strong> &mdash; text wrapping around photos in editorial layouts.</li>
  <li><strong>Pull quotes</strong> &mdash; shaped quotation blocks with text flowing around.</li>
  <li><strong>Product pages</strong> &mdash; description hugging the product photo.</li>
  <li><strong>Profile bios</strong> &mdash; circular avatar with text wrapping.</li>
</ul>

<p><strong>Limitations:</strong></p>
<ul>
  <li><strong>Float-only</strong> &mdash; doesn&rsquo;t work with Flexbox or Grid items.</li>
  <li><strong>Limited to one side</strong> &mdash; text flows around the floated element on one side; can&rsquo;t make text flow on both sides of a centered element.</li>
  <li><strong>RTL behavior</strong> &mdash; <code>float: right</code> in RTL languages may need <code>float: inline-start</code> for logical direction.</li>
  <li><strong>Browser support</strong> &mdash; widely supported in 2026 but always a niche feature.</li>
</ul>

<p>Float-based layout for page structure is dead, but for inline text wrapping around media, <code>shape-outside</code> is the right tool &mdash; no Flexbox or Grid alternative exists.</p>
'''

ANSWERS[82] = r'''
<p>A CSS-only image slider uses <code>scroll-snap</code> to create swipeable, snap-aligned slides &mdash; native momentum scrolling, smooth snapping, no JavaScript. Add navigation buttons or dots with anchor links targeting each slide for full functionality.</p>

<pre><code>&lt;div class="slider"&gt;
  &lt;img src="1.jpg" alt="" id="slide-1"&gt;
  &lt;img src="2.jpg" alt="" id="slide-2"&gt;
  &lt;img src="3.jpg" alt="" id="slide-3"&gt;
  &lt;img src="4.jpg" alt="" id="slide-4"&gt;
&lt;/div&gt;

&lt;nav class="slider-nav"&gt;
  &lt;a href="#slide-1"&gt;1&lt;/a&gt;
  &lt;a href="#slide-2"&gt;2&lt;/a&gt;
  &lt;a href="#slide-3"&gt;3&lt;/a&gt;
  &lt;a href="#slide-4"&gt;4&lt;/a&gt;
&lt;/nav&gt;

&lt;style&gt;
  .slider {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    /* Hide native scrollbar */
    scrollbar-width: none;
  }
  .slider::-webkit-scrollbar {
    display: none;
  }

  .slider img {
    flex: 0 0 100%;
    scroll-snap-align: start;
    aspect-ratio: 16 / 9;
    object-fit: cover;
  }

  .slider-nav {
    display: flex;
    gap: 0.5em;
    justify-content: center;
    margin-top: 1em;
  }
  .slider-nav a {
    width: 12px;
    height: 12px;
    background: #ccc;
    border-radius: 50%;
    text-indent: -9999px;
    overflow: hidden;
    transition: background 0.2s;
  }
  .slider-nav a:hover {
    background: #888;
  }
&lt;/style&gt;</code></pre>

<p><strong>How <code>scroll-snap</code> creates the slider:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>scroll-snap-type: x mandatory</code></td><td>Container snaps on x-axis; mandatory = always snaps</td></tr>
  <tr><td><code>scroll-snap-align: start</code></td><td>Each child snaps with its start edge aligned</td></tr>
  <tr><td><code>scroll-behavior: smooth</code></td><td>Anchor link scrolls smoothly to target</td></tr>
  <tr><td><code>flex: 0 0 100%</code></td><td>Each slide is exactly viewport-wide</td></tr>
</table>

<p><strong>Adding prev/next buttons</strong> &mdash; pure CSS by clever use of <code>:target</code>:</p>
<pre><code>&lt;div class="slider-with-nav"&gt;
  &lt;a href="#slide-2" class="next-btn next-1"&gt;&rsaquo;&lt;/a&gt;
  &lt;a href="#slide-1" class="prev-btn prev-2"&gt;&lsaquo;&lt;/a&gt;

  &lt;div class="slider"&gt;
    &lt;img src="1.jpg" id="slide-1" alt=""&gt;
    &lt;img src="2.jpg" id="slide-2" alt=""&gt;
    &lt;!-- ... --&gt;
  &lt;/div&gt;
&lt;/div&gt;</code></pre>

<p>Each "next" button links to the next slide&rsquo;s ID; the smooth-scroll-behavior and scroll-snap combine to make it slide cleanly.</p>

<p><strong>Auto-advance with CSS animation</strong> (works for showcases; less for true sliders):</p>
<pre><code>@keyframes auto-slide {
  0%, 25%   { transform: translateX(0); }
  33%, 58%  { transform: translateX(-100%); }
  66%, 91%  { transform: translateX(-200%); }
  100%      { transform: translateX(-300%); }
}

.auto-slider {
  width: 400%;
  animation: auto-slide 16s linear infinite;
}</code></pre>

<p>Inflexible (no user interaction) but useful for hero banners that loop without controls.</p>

<p><strong>Modern enhancement: scroll-driven indicator</strong> &mdash; the active dot reflects scroll position:</p>
<pre><code>.slider-nav a {
  /* Base style */
}

/* Use :target-current to highlight matching slide */
.slider img:target-current ~ .slider-nav a[href="#" + id] {
  background: #0066cc;
}</code></pre>

<p>The <code>:target-current</code> pseudo-class (modern) tracks which scroll-snapped element is currently in view &mdash; perfect for active-state indicators without JavaScript.</p>

<p><strong>For production sliders</strong>, libraries like Swiper.js or Embla Carousel handle:</p>
<ul>
  <li>Touch/mouse drag with momentum</li>
  <li>Keyboard navigation (arrow keys)</li>
  <li>Autoplay with pause-on-hover</li>
  <li>Lazy loading of slides</li>
  <li>ARIA live regions for screen reader announcements</li>
  <li>Reduced-motion preference</li>
  <li>Infinite loop variations</li>
</ul>

<p>The CSS-only approach handles ~80% of slider needs &mdash; especially great for image galleries where touch swipe + snap is the primary interaction. Reach for libraries when you need the polish.</p>
'''

ANSWERS[83] = r'''
<p>CSS subgrid (Baseline 2024) lets <strong>nested grids inherit the parent grid&rsquo;s tracks</strong> instead of defining their own &mdash; finally enabling alignment of inner content across grid items, the long-standing limitation that drove people to libraries or table-based layouts.</p>

<p><strong>The problem subgrid solves:</strong></p>
<pre><code>&lt;!-- Without subgrid --&gt;
&lt;section class="card-grid"&gt;
  &lt;article class="card"&gt;
    &lt;img&gt;&lt;h3&gt;Short title&lt;/h3&gt;&lt;p&gt;Description...&lt;/p&gt;&lt;a&gt;CTA&lt;/a&gt;
  &lt;/article&gt;
  &lt;article class="card"&gt;
    &lt;img&gt;&lt;h3&gt;Much longer title that wraps&lt;/h3&gt;&lt;p&gt;Description...&lt;/p&gt;&lt;a&gt;CTA&lt;/a&gt;
  &lt;/article&gt;
&lt;/section&gt;</code></pre>

<p>Cards in a row stretch to the same height, but their internal sections (title, description, CTA) don&rsquo;t align across cards. The first card&rsquo;s description starts higher than the second&rsquo;s because of title length differences.</p>

<p><strong>Subgrid solution:</strong></p>
<pre><code>.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  grid-template-rows: auto auto auto auto;     /* image, title, description, CTA */
  gap: 1em;
}

.card {
  grid-row: span 4;             /* card spans 4 outer rows */
  display: grid;
  grid-template-rows: subgrid;   /* inherit parent rows */
  /* Each child of .card aligns to one of the 4 outer rows */
}

.card img { /* row 1 */ }
.card h3  { /* row 2 — all titles align */ }
.card p   { /* row 3 — all descriptions align */ }
.card a   { /* row 4 — all CTAs align */ }</code></pre>

<p>Now every card&rsquo;s title, description, and CTA align across columns &mdash; achieving the magazine-style consistency that previously required JavaScript or fixed heights.</p>

<p><strong>Subgrid columns example:</strong></p>
<pre><code>.outer-grid {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  gap: 1em;
}

.inner-content {
  grid-column: 1 / -1;          /* span all outer columns */
  display: grid;
  grid-template-columns: subgrid;
  gap: inherit;                   /* match parent gap */
}

.inner-content &gt; * {
  /* Children align to outer grid's columns */
}</code></pre>

<p>The inner grid uses the same column tracks as the outer &mdash; sub-elements naturally line up with sidebar boundaries above.</p>

<p><strong>Both directions:</strong></p>
<pre><code>.full-subgrid {
  display: grid;
  grid-template-columns: subgrid;
  grid-template-rows: subgrid;
  /* Inherits both columns AND rows from parent */
}</code></pre>

<p><strong>Key features:</strong></p>
<ul>
  <li><strong>Inherit only one or both axes</strong> &mdash; flexible.</li>
  <li><strong>Items still place freely</strong> within the inherited tracks.</li>
  <li><strong>Gap inherits</strong> by default unless overridden.</li>
  <li><strong>Named lines pass through</strong> &mdash; you can reference parent grid&rsquo;s named lines from inside.</li>
</ul>

<p><strong>Real-world use cases:</strong></p>
<ol>
  <li><strong>Card grids with aligned internals</strong> &mdash; titles, descriptions, CTAs aligned across columns regardless of content length variation.</li>
  <li><strong>Form layouts</strong> &mdash; labels and inputs aligning across multiple form sections.</li>
  <li><strong>Comparison tables</strong> built with grid &mdash; rows of features lining up across product columns.</li>
  <li><strong>Pricing tables</strong> &mdash; feature rows aligned across plans.</li>
  <li><strong>Magazine layouts</strong> &mdash; columns of articles with consistent typographic baseline.</li>
</ol>

<p><strong>Browser support (2026):</strong></p>
<table>
  <tr><th>Browser</th><th>Support</th></tr>
  <tr><td>Firefox</td><td>Yes (since 71, 2019)</td></tr>
  <tr><td>Safari</td><td>Yes (since 16)</td></tr>
  <tr><td>Chrome / Edge</td><td>Yes (since 117)</td></tr>
</table>

<p>Now Baseline since 2024 &mdash; safe to use in production. Provide a Flexbox fallback inside <code>@supports (grid-template-columns: subgrid)</code> only for legacy environments.</p>

<p><strong>Without subgrid, alternatives:</strong></p>
<ul>
  <li><strong>Equal-height with Flex</strong>: cards stretch but internals don&rsquo;t align.</li>
  <li><strong>Fixed dimensions</strong>: <code>height: 200px</code> on each section &mdash; brittle, breaks responsive design.</li>
  <li><strong>JavaScript</strong>: measure heights, set them programmatically &mdash; brittle, layout shift.</li>
</ul>

<p>Subgrid solved a 25-year-old layout problem cleanly. For complex card or article grids in 2026, it&rsquo;s the go-to.</p>
'''

ANSWERS[84] = r'''
<p>A CSS-only countdown timer is a contradiction in terms &mdash; CSS animations run for fixed durations but don&rsquo;t track real time, and they don&rsquo;t handle dynamic content updates. The closest CSS-only approach uses long animations with calculated keyframes; for true countdowns, JavaScript is essential.</p>

<p><strong>The CSS-only "fake countdown" pattern</strong> &mdash; visual countdown without showing actual numbers:</p>
<pre><code>&lt;div class="countdown"&gt;
  &lt;div class="bar"&gt;&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .countdown {
    width: 300px;
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
  }
  .bar {
    width: 100%;
    height: 100%;
    background: #0066cc;
    animation: countdown 60s linear forwards;
    transform-origin: left;
  }
  @keyframes countdown {
    from { transform: scaleX(1); }
    to   { transform: scaleX(0); }
  }
&lt;/style&gt;</code></pre>

<p>This animates a bar shrinking over 60 seconds. It&rsquo;s a visual indicator, not a true counter &mdash; no numeric display, doesn&rsquo;t reflect real time.</p>

<p><strong>Pseudo-numeric countdown using <code>@property</code> + counters</strong> (modern, ~2024+):</p>
<pre><code>@property --num {
  syntax: "&lt;integer&gt;";
  initial-value: 60;
  inherits: false;
}

.timer::before {
  counter-reset: timer var(--num);
  content: counter(timer);
  animation: count 60s linear forwards;
}

@keyframes count {
  from { --num: 60; }
  to   { --num: 0; }
}</code></pre>

<p>This animates the <code>--num</code> custom property from 60 to 0 over 60 seconds; the counter renders the integer value. Limitations: only counts whole numbers; can&rsquo;t format as MM:SS without complex math.</p>

<p><strong>The realistic JavaScript-based countdown:</strong></p>
<pre><code>&lt;div class="countdown" id="countdown"&gt;
  &lt;div class="time"&gt;
    &lt;span id="days"&gt;00&lt;/span&gt;:
    &lt;span id="hours"&gt;00&lt;/span&gt;:
    &lt;span id="minutes"&gt;00&lt;/span&gt;:
    &lt;span id="seconds"&gt;00&lt;/span&gt;
  &lt;/div&gt;
  &lt;div class="progress-track"&gt;
    &lt;div class="progress-bar" id="progress"&gt;&lt;/div&gt;
  &lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .countdown {
    text-align: center;
    font-family: ui-monospace, monospace;
    font-size: 2em;
  }
  .time span {
    display: inline-block;
    background: #1a1a1a;
    color: #fff;
    padding: 0.5em;
    border-radius: 4px;
    min-width: 1.5em;
  }
  .progress-track {
    margin-top: 1em;
    height: 6px;
    background: #f0f0f0;
    border-radius: 3px;
    overflow: hidden;
  }
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #0066cc, #ff6b35);
    transition: width 1s linear;
  }
&lt;/style&gt;

&lt;script&gt;
  const targetDate = new Date("2026-12-31T23:59:59").getTime();
  const startDate = Date.now();
  const totalDuration = targetDate - startDate;

  function updateCountdown() {
    const now = Date.now();
    const distance = targetDate - now;
    const elapsed = totalDuration - distance;

    if (distance &lt; 0) {
      document.getElementById("countdown").textContent = "Time's up!";
      return;
    }

    const days    = Math.floor(distance / 86400000);
    const hours   = Math.floor((distance / 3600000) % 24);
    const minutes = Math.floor((distance / 60000) % 60);
    const seconds = Math.floor((distance / 1000) % 60);

    document.getElementById("days").textContent    = String(days).padStart(2, "0");
    document.getElementById("hours").textContent   = String(hours).padStart(2, "0");
    document.getElementById("minutes").textContent = String(minutes).padStart(2, "0");
    document.getElementById("seconds").textContent = String(seconds).padStart(2, "0");

    const progress = (elapsed / totalDuration) * 100;
    document.getElementById("progress").style.width = `${progress}%`;
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);
&lt;/script&gt;</code></pre>

<p><strong>Why CSS alone falls short:</strong></p>
<ul>
  <li><strong>No way to render formatted time strings</strong> &mdash; CSS counters output integers, not "23:59:01".</li>
  <li><strong>Animations restart on page reload</strong> &mdash; can&rsquo;t persist real countdown progress without JavaScript.</li>
  <li><strong>Animations have fixed duration</strong> &mdash; they don&rsquo;t know about absolute target dates.</li>
  <li><strong>Time-based UI updates need <code>setInterval</code></strong> or <code>requestAnimationFrame</code> &mdash; pure CSS can&rsquo;t access wall-clock time.</li>
</ul>

<p><strong>Hybrid approach (best of both):</strong></p>
<pre><code>/* CSS handles visual smoothness */
.progress-bar {
  transition: width 1s linear;
}

/* JS sets target widths every second */
setInterval(() =&gt; {
  bar.style.width = `${calculateProgress()}%`;
}, 1000);</code></pre>

<p>JavaScript drives the data; CSS handles the smooth animation between updates &mdash; the cleanest production pattern.</p>

<p>Pure-CSS countdown timers exist as Codepen demos and visual showpieces but aren&rsquo;t suitable for actual applications. JavaScript + CSS animation is the right architecture for any real countdown.</p>
'''

ANSWERS[85] = r'''
<p>The <code>counter-reset</code> and <code>counter-increment</code> properties form the foundation of CSS counters &mdash; the mechanism for automatic numbering that goes far beyond the default <code>&lt;ol&gt;</code> behavior. <code>counter-reset</code> initializes a counter (typically on a parent); <code>counter-increment</code> adds to it (typically on each child); <code>counter()</code> in the <code>content</code> property displays the value.</p>

<table>
  <tr><th>Property</th><th>Syntax</th><th>Effect</th></tr>
  <tr><td><code>counter-reset</code></td><td><code>counter-reset: name [value]</code></td><td>Creates/resets counter to specified value (default 0)</td></tr>
  <tr><td><code>counter-increment</code></td><td><code>counter-increment: name [value]</code></td><td>Increments counter by specified value (default 1)</td></tr>
  <tr><td><code>counter-set</code></td><td><code>counter-set: name [value]</code></td><td>Sets counter to value (without "creating" effect of reset)</td></tr>
</table>

<pre><code>.steps {
  counter-reset: step;     /* initialize "step" counter to 0 */
  list-style: none;
}
.steps li {
  counter-increment: step;  /* +1 for each li */
}
.steps li::before {
  content: "Step " counter(step) ": ";
  font-weight: bold;
}</code></pre>

<p><strong>Custom increments &mdash; not just by 1:</strong></p>
<pre><code>.even-steps li {
  counter-increment: step 2;     /* counts 2, 4, 6, 8 */
}

.countdown li {
  counter-increment: countdown -1;     /* counts down */
}

.start-at-100 {
  counter-reset: section 99;     /* next increment makes it 100 */
}</code></pre>

<p><strong>Multiple counters in parallel</strong> &mdash; reset and increment several at once:</p>
<pre><code>article {
  counter-reset: chapter section figure;
}
h1 { counter-increment: chapter; counter-reset: section figure; }
h2 { counter-increment: section; counter-reset: figure; }
.figure { counter-increment: figure; }

h1::before { content: "Chapter " counter(chapter) ": "; }
h2::before { content: counter(chapter) "." counter(section) " "; }
.figure::before { content: "Fig. " counter(chapter) "." counter(figure) ": "; }</code></pre>

<p>Each new <code>h1</code> resets the section and figure counters &mdash; creating proper hierarchical numbering like Chapter 2 &rarr; 2.1, 2.2 &rarr; Fig. 2.1, 2.2 &mdash; a structure that resets correctly when entering a new chapter.</p>

<p><strong>Nested counters with <code>counters()</code> (plural):</strong></p>
<pre><code>ol.legal {
  counter-reset: section;
  list-style: none;
}
ol.legal li {
  counter-increment: section;
}
ol.legal li::before {
  content: counters(section, ".") " ";
  /* Output: "1 ", "1.1 ", "1.1.1 ", "1.2 ", "2 " ... */
}</code></pre>

<p>The <code>counters()</code> function (plural) joins the entire chain of nested counter values with a separator. Each nested <code>&lt;ol&gt;</code> creates a new counter; the outer counter persists, producing legal-style numbering.</p>

<p><strong>Counter scope &mdash; the subtle but critical rule:</strong></p>
<table>
  <tr><th>Where you reset</th><th>Counter scope</th></tr>
  <tr><td>On document root (<code>body</code>)</td><td>Document-wide</td></tr>
  <tr><td>On a parent element</td><td>Children and descendants</td></tr>
  <tr><td>On a sibling-level element</td><td>Restarts at that point</td></tr>
</table>

<p>Putting <code>counter-reset</code> on each <code>li</code> (instead of on the <code>ol</code>) would reset the counter for every item &mdash; making every list item show "1." That&rsquo;s a common mistake.</p>

<p><strong>Counter styles for output formatting:</strong></p>
<pre><code>li::before {
  content: counter(item, lower-roman) ". ";   /* i. ii. iii. */
}

li::before {
  content: counter(item, upper-alpha) ") ";   /* A) B) C) */
}

li::before {
  content: counter(item, decimal-leading-zero) ". ";   /* 01. 02. */
}</code></pre>

<p><strong>Modern enhancement: <code>@counter-style</code></strong> for fully custom number formats:</p>
<pre><code>@counter-style emoji-numbers {
  system: cyclic;
  symbols: "&#11088;" "&#129728;" "&#127775;" "&#128171;";
  suffix: " ";
}

ul {
  list-style: emoji-numbers;
}</code></pre>

<p>Define your own counter style with custom symbols (numbers, emoji, special characters) &mdash; supported in all modern browsers (Baseline 2024).</p>

<p><strong>Why use CSS counters over manual numbering:</strong></p>
<ul>
  <li><strong>Style any element</strong> &mdash; not just list items.</li>
  <li><strong>Auto-update</strong> when items are added/removed.</li>
  <li><strong>Hierarchical numbering</strong> works without JavaScript.</li>
  <li><strong>Multiple parallel counters</strong> for figures, tables, equations.</li>
  <li><strong>Styling separation</strong> &mdash; numbers are presentational, kept out of HTML.</li>
</ul>
'''

ANSWERS[86] = r'''
<p>Responsive layouts using <code>grid-template-areas</code> are CSS&rsquo;s most expressive layout feature &mdash; the visual ASCII-art representation of regions makes layout changes intuitive. The same elements rearrange completely between breakpoints by redefining the template strings.</p>

<pre><code>&lt;div class="page-layout"&gt;
  &lt;header&gt;Header&lt;/header&gt;
  &lt;nav&gt;Navigation&lt;/nav&gt;
  &lt;main&gt;Main content&lt;/main&gt;
  &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  .page-layout {
    display: grid;
    min-height: 100vh;
    gap: 1em;
    padding: 1em;

    /* Default: desktop layout */
    grid-template-columns: 200px 1fr 250px;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header header header"
      "nav    main   aside"
      "footer footer footer";
  }

  header { grid-area: header; }
  nav    { grid-area: nav; }
  main   { grid-area: main; }
  aside  { grid-area: aside; }
  footer { grid-area: footer; }

  /* Tablet: hide aside, expand main */
  @media (max-width: 1024px) {
    .page-layout {
      grid-template-columns: 200px 1fr;
      grid-template-areas:
        "header header"
        "nav    main"
        "aside  aside"
        "footer footer";
    }
  }

  /* Mobile: single column, reordered */
  @media (max-width: 768px) {
    .page-layout {
      grid-template-columns: 1fr;
      grid-template-areas:
        "header"
        "nav"
        "main"
        "aside"
        "footer";
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>Why this pattern is powerful:</strong></p>
<ul>
  <li><strong>Layout source order is decoupled from visual order</strong> &mdash; HTML stays semantic, CSS controls placement.</li>
  <li><strong>Adding/removing breakpoints</strong> just means defining new template strings.</li>
  <li><strong>Self-documenting</strong> &mdash; the template visually represents the layout.</li>
  <li><strong>Maintainable</strong> &mdash; changes to layout structure are local to the grid container.</li>
</ul>

<p><strong>Empty cells with the dot:</strong></p>
<pre><code>.complex {
  grid-template-areas:
    ".      header header"
    "sidebar main   .";
  /* The dot leaves cells empty */
}</code></pre>

<p><strong>Spanning multiple cells</strong> &mdash; repeat the area name:</p>
<pre><code>.layout {
  grid-template-areas:
    "hero hero hero"          /* hero spans 3 columns */
    "a    b    c"
    "footer footer footer";
}</code></pre>

<p><strong>Common responsive patterns:</strong></p>
<table>
  <tr><th>Pattern</th><th>Mobile</th><th>Tablet</th><th>Desktop</th></tr>
  <tr><td>Holy grail</td><td>1 col stack</td><td>1 col stack</td><td>3 col</td></tr>
  <tr><td>Sidebar layout</td><td>1 col stack</td><td>main / sidebar</td><td>sidebar / main</td></tr>
  <tr><td>Magazine</td><td>1 col stack</td><td>2 col</td><td>3-4 col grid</td></tr>
  <tr><td>Dashboard</td><td>Cards stack</td><td>2x2 cards</td><td>4x2 cards with sidebar</td></tr>
</table>

<p><strong>Modern enhancement &mdash; container queries</strong> for component-level responsiveness:</p>
<pre><code>.card {
  container-type: inline-size;
  display: grid;
  grid-template-areas:
    "image"
    "body";
}

@container (min-width: 500px) {
  .card {
    grid-template-columns: 200px 1fr;
    grid-template-areas: "image body";
  }
}</code></pre>

<p>The card rearranges based on its OWN width, not the viewport &mdash; a card in a sidebar uses the stacked layout while the same card in a wide main column uses the side-by-side layout. Component-driven responsive design.</p>

<p><strong>Order property as alternative</strong> (when <code>grid-template-areas</code> doesn&rsquo;t fit):</p>
<pre><code>.flex-layout {
  display: flex;
  flex-direction: column;
}

@media (max-width: 768px) {
  .nav { order: -1; }      /* nav before others */
  .footer { order: 99; }   /* footer last */
}</code></pre>

<p>Less expressive than grid-template-areas but works in flex contexts.</p>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Define areas at all breakpoints</strong> &mdash; never leave an area without placement.</li>
  <li><strong>Use the dot for explicit empty cells</strong> &mdash; clearer than ambiguous gaps.</li>
  <li><strong>Keep template strings aligned with whitespace</strong> &mdash; visual ASCII art aids comprehension.</li>
  <li><strong>Test at every breakpoint</strong> &mdash; transitions between layouts can introduce overflow or alignment bugs.</li>
</ul>
'''

ANSWERS[87] = r'''
<p>The <code>writing-mode</code> property controls <strong>the direction in which text flows</strong> &mdash; horizontal (default for English/Latin scripts) or vertical (used in traditional Chinese, Japanese, Mongolian, and for design effects in any language).</p>

<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>horizontal-tb</code> (default)</td><td>Lines stack top-to-bottom; characters flow left-to-right (or right-to-left for RTL)</td></tr>
  <tr><td><code>vertical-rl</code></td><td>Lines stack right-to-left; characters flow top-to-bottom (Japanese vertical)</td></tr>
  <tr><td><code>vertical-lr</code></td><td>Lines stack left-to-right; characters top-to-bottom (Mongolian)</td></tr>
  <tr><td><code>sideways-rl</code> / <code>sideways-lr</code></td><td>Latin chars rotated to read sideways (no character substitution)</td></tr>
</table>

<pre><code>/* Sidebar label rotated 90 degrees */
.vertical-label {
  writing-mode: vertical-rl;
  /* Reads top-to-bottom, columns right-to-left */
}

/* Cover-style design — large vertical title */
.book-cover h1 {
  writing-mode: vertical-rl;
  font-size: 3em;
  letter-spacing: 0.1em;
}

/* Sidewise text for chart axis labels */
.chart-y-axis {
  writing-mode: sideways-lr;
  /* Latin characters appear rotated 90deg counter-clockwise */
}</code></pre>

<p><strong>Critical concept: the "block" and "inline" axes flip:</strong></p>
<table>
  <tr><th>In horizontal-tb</th><th>In vertical-rl</th></tr>
  <tr><td>width = inline size</td><td>height = inline size</td></tr>
  <tr><td>height = block size</td><td>width = block size</td></tr>
  <tr><td>margin-left/right = inline-start/end</td><td>margin-top/bottom = inline-start/end</td></tr>
  <tr><td>padding-top/bottom = block-start/end</td><td>padding-left/right = block-start/end</td></tr>
</table>

<p>This is why <strong>logical properties</strong> (<code>margin-inline-start</code>, <code>padding-block-end</code>) matter &mdash; they automatically adapt to the writing mode without code changes.</p>

<p><strong>Practical use cases:</strong></p>
<ol>
  <li><strong>Multi-language sites</strong> &mdash; Japanese, Chinese, and Mongolian content in vertical layouts.</li>
  <li><strong>Design accents</strong> &mdash; vertical taglines, sidebar labels, magazine-style layouts.</li>
  <li><strong>Chart axis labels</strong> &mdash; rotated text along Y-axis without manual transforms.</li>
  <li><strong>Tab labels for vertical tabs</strong> &mdash; common in IDE-like interfaces.</li>
  <li><strong>Architecture diagrams</strong> &mdash; vertical column headers.</li>
</ol>

<p><strong>Combine with <code>text-orientation</code></strong> for specific character behaviors:</p>
<pre><code>.vertical-mixed {
  writing-mode: vertical-rl;
  text-orientation: mixed;     /* default: characters rotate naturally */
}
.vertical-upright {
  writing-mode: vertical-rl;
  text-orientation: upright;     /* every character upright (good for Asian fonts) */
}
.vertical-sideways {
  writing-mode: vertical-rl;
  text-orientation: sideways;     /* all rotated 90deg */
}</code></pre>

<p><strong>Vertical text vs CSS rotation</strong> &mdash; subtle but important:</p>
<table>
  <tr><th></th><th><code>writing-mode</code></th><th><code>transform: rotate(90deg)</code></th></tr>
  <tr><td>Affects layout</td><td>Yes (parent sees rotated dimensions)</td><td>No (visual only)</td></tr>
  <tr><td>Text selection</td><td>Natural (top-to-bottom)</td><td>Awkward (still left-to-right)</td></tr>
  <tr><td>Accessibility</td><td>Real text flow</td><td>Same as horizontal</td></tr>
  <tr><td>Use for</td><td>Actual vertical text</td><td>Visual rotations of full elements</td></tr>
</table>

<p>If you want a "Read more &rarr;" link rotated, use <code>transform</code>. If you want actual top-to-bottom flowing text where users select line by line vertically, use <code>writing-mode</code>.</p>

<p><strong>Animating writing-mode</strong> &mdash; not animatable directly. Use <code>transform: rotate()</code> for animated transitions and <code>writing-mode</code> for static end-states.</p>

<p><strong>RTL languages and writing-mode</strong>: <code>direction: rtl</code> handles right-to-left character order within a horizontal layout (Arabic, Hebrew). It&rsquo;s separate from <code>writing-mode</code>, which controls block-direction. Use both together for fully internationalized layouts.</p>
'''

ANSWERS[88] = r'''
<p>A toast notification is a brief, non-modal message that appears, stays for a few seconds, and disappears &mdash; success confirmations, errors, info alerts. The pattern combines CSS animations with JavaScript for state management.</p>

<pre><code>&lt;div class="toast-container" id="toasts"&gt;&lt;/div&gt;

&lt;style&gt;
  .toast-container {
    position: fixed;
    top: 1em;
    right: 1em;
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    z-index: 9999;
    pointer-events: none;       /* container doesn't block clicks */
  }

  .toast {
    background: white;
    color: #333;
    padding: 1em 1.5em;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-left: 4px solid #0066cc;
    min-width: 250px;
    max-width: 400px;
    pointer-events: auto;       /* but toasts themselves are clickable */

    /* Entry animation */
    animation: toast-in 0.3s ease-out, toast-out 0.3s ease-in 4.7s forwards;
  }

  .toast.success { border-left-color: #28a745; }
  .toast.error   { border-left-color: #dc3545; }
  .toast.warning { border-left-color: #ffc107; }

  @keyframes toast-in {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes toast-out {
    from {
      opacity: 1;
      transform: translateX(0);
      max-height: 100px;
      margin-bottom: 0.5em;
    }
    to {
      opacity: 0;
      transform: translateX(100%);
      max-height: 0;
      margin-bottom: 0;
      padding-top: 0;
      padding-bottom: 0;
    }
  }
&lt;/style&gt;

&lt;script&gt;
  function showToast(message, type = "info") {
    const container = document.getElementById("toasts");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.textContent = message;
    container.appendChild(toast);

    // Remove after animation completes (5s = 0.3 in + 4.4 stay + 0.3 out)
    setTimeout(() =&gt; toast.remove(), 5000);
  }

  // Usage
  showToast("Settings saved successfully", "success");
  showToast("Failed to load data", "error");
&lt;/script&gt;</code></pre>

<p><strong>Modern alternative: native Popover API</strong> (Baseline 2024+) for the toast container:</p>
<pre><code>&lt;div id="toast" popover="manual" class="toast"&gt;
  Settings saved successfully
&lt;/div&gt;

&lt;script&gt;
  function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.showPopover();
    setTimeout(() =&gt; toast.hidePopover(), 4000);
  }
&lt;/script&gt;</code></pre>

<p>Benefits of Popover API:</p>
<ul>
  <li><strong>Top-layer rendering</strong> &mdash; toast always appears above all other content; no z-index battles.</li>
  <li><strong>Esc key handling</strong> built in (with <code>popover="auto"</code>).</li>
  <li><strong>Better focus management</strong> for accessibility.</li>
</ul>

<p><strong>Critical accessibility patterns:</strong></p>
<table>
  <tr><th>Toast type</th><th>ARIA approach</th></tr>
  <tr><td>Success / info</td><td><code>role="status" aria-live="polite"</code></td></tr>
  <tr><td>Errors</td><td><code>role="alert" aria-live="assertive"</code></td></tr>
  <tr><td>Confirmations needing action</td><td>Should be a modal dialog, not a toast</td></tr>
</table>

<p><strong>Don&rsquo;t use toasts for critical messages</strong> that the user must acknowledge or that require action &mdash; toasts disappear; users may miss them. Use modals for those.</p>

<p><strong>Auto-dismiss timing:</strong></p>
<ul>
  <li><strong>3-5 seconds</strong> for short messages.</li>
  <li><strong>5-7 seconds</strong> for longer content.</li>
  <li><strong>Pause on hover</strong> &mdash; reset the timer when the user is reading.</li>
  <li><strong>No auto-dismiss for errors</strong> &mdash; let users dismiss manually.</li>
</ul>

<p><strong>Stacking multiple toasts:</strong></p>
<pre><code>.toast-container {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
}
/* Newest at top, gap separates them, exit animations remove cleanly */</code></pre>

<p>The container is a flex column &mdash; new toasts append; exit animation collapses height. Smooth visual flow.</p>

<p>Modern toast libraries (sonner, react-hot-toast) handle the stacking, queuing, swipe-to-dismiss, and reduced-motion concerns &mdash; using one is appropriate for production. The CSS pattern above is the foundation they all build on.</p>
'''

ANSWERS[89] = r'''
<p>The <code>scroll-snap</code> properties create <strong>snap points within scrollable containers</strong> &mdash; scrolling stops cleanly at predefined positions instead of arbitrary pixel positions. Native momentum scrolling, smooth snapping, no JavaScript &mdash; ideal for image carousels, full-page sections, and step-based interfaces.</p>

<table>
  <tr><th>Property</th><th>Where applied</th><th>Purpose</th></tr>
  <tr><td><code>scroll-snap-type</code></td><td>Scroll container</td><td>Define snap axis and strictness</td></tr>
  <tr><td><code>scroll-snap-align</code></td><td>Children</td><td>Snap point alignment within child</td></tr>
  <tr><td><code>scroll-snap-stop</code></td><td>Children</td><td>Force stop at every snap point</td></tr>
  <tr><td><code>scroll-padding</code></td><td>Scroll container</td><td>Inner padding around snap points</td></tr>
  <tr><td><code>scroll-margin</code></td><td>Children</td><td>Outer margin around child snap target</td></tr>
</table>

<p><strong>Horizontal image carousel:</strong></p>
<pre><code>&lt;div class="carousel"&gt;
  &lt;img src="1.jpg" alt=""&gt;
  &lt;img src="2.jpg" alt=""&gt;
  &lt;img src="3.jpg" alt=""&gt;
&lt;/div&gt;

&lt;style&gt;
  .carousel {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;     /* must snap on x axis */
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
  }
  .carousel img {
    flex: 0 0 100%;                       /* full width */
    scroll-snap-align: start;             /* snap with start edge aligned */
    aspect-ratio: 16 / 9;
    object-fit: cover;
  }
&lt;/style&gt;</code></pre>

<p><strong>Vertical full-page sections</strong> &mdash; each section snaps:</p>
<pre><code>html {
  scroll-snap-type: y mandatory;
}

section {
  scroll-snap-align: start;
  height: 100vh;
}</code></pre>

<p>Pages.io style; each scroll snaps to the next section.</p>

<p><strong><code>scroll-snap-type</code> values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>none</code></td><td>No snap (default)</td></tr>
  <tr><td><code>x mandatory</code></td><td>Always snap on x axis</td></tr>
  <tr><td><code>y mandatory</code></td><td>Always snap on y axis</td></tr>
  <tr><td><code>both mandatory</code></td><td>Snap on both axes (rare)</td></tr>
  <tr><td><code>x proximity</code></td><td>Snap on x only when close to a snap point</td></tr>
</table>

<p><strong><code>mandatory</code> vs <code>proximity</code></strong>:</p>
<ul>
  <li><strong><code>mandatory</code></strong> &mdash; scroll always lands on a snap point, even if the user releases mid-scroll. Best for image galleries, slides, paginated content.</li>
  <li><strong><code>proximity</code></strong> &mdash; snap only when the scroll naturally ends near a snap point. Less aggressive; good for long-form content with section markers.</li>
</ul>

<p><strong><code>scroll-snap-align</code> values:</strong></p>
<table>
  <tr><th>Value</th><th>Snap point</th></tr>
  <tr><td><code>start</code></td><td>Start edge of element aligns to scroll container start</td></tr>
  <tr><td><code>end</code></td><td>End edge aligns to container end</td></tr>
  <tr><td><code>center</code></td><td>Element centers in the container</td></tr>
  <tr><td><code>none</code></td><td>No snap (default)</td></tr>
</table>

<p><strong>Carousel with header offset</strong> &mdash; <code>scroll-padding-top</code>:</p>
<pre><code>html {
  scroll-snap-type: y mandatory;
  scroll-padding-top: 80px;       /* offset for fixed header */
}

section {
  scroll-snap-align: start;
}</code></pre>

<p>Without padding, sections snap behind the fixed header. With <code>scroll-padding-top: 80px</code>, snap targets are offset by the header height &mdash; sections appear correctly below the header.</p>

<p><strong><code>scroll-snap-stop: always</code></strong> &mdash; one snap per scroll gesture:</p>
<pre><code>.carousel img {
  scroll-snap-align: start;
  scroll-snap-stop: always;
  /* Each scroll gesture moves only ONE slide, not multiple */
}</code></pre>

<p>Default: scroll momentum can carry past multiple snap points. With <code>always</code>, each swipe always lands on the next adjacent slide &mdash; the typical carousel behavior users expect.</p>

<p><strong>Modern: scroll-driven indicators</strong> &mdash; the <code>:target-current</code> pseudo-class shows the active slide:</p>
<pre><code>.indicator-dot {
  background: gray;
}
.carousel img:target-current ~ .indicators .indicator-dot[href="#slide-X"] {
  background: blue;
  /* The dot for the currently-snapped slide is highlighted */
}</code></pre>

<p>Modern carousels can use <code>:target-current</code> for active-state indicators that update as the user scrolls &mdash; a feature impossible without JavaScript before.</p>

<p><strong>Browser support:</strong> universal in 2026; one of the most useful additions of the past five years for native scroll experiences.</p>

<p>Where it doesn&rsquo;t fit: arbitrary "fly to position" navigation that doesn&rsquo;t correspond to defined snap points. For those, JavaScript libraries are still better. But for image galleries, full-page sections, and step-by-step interfaces, scroll-snap is the right tool.</p>
'''

ANSWERS[90] = r'''
<p>Flexbox <code>flex-wrap</code> + <code>flex: 1 1 BASIS</code> is the cleanest pattern for "auto-flowing" responsive layouts &mdash; cards or sections wrap to multiple lines based on available width without media queries. The basis value defines the minimum size before wrapping; the grow factor distributes leftover space.</p>

<pre><code>&lt;section class="auto-grid"&gt;
  &lt;article&gt;Card 1&lt;/article&gt;
  &lt;article&gt;Card 2&lt;/article&gt;
  &lt;article&gt;Card 3&lt;/article&gt;
  &lt;article&gt;Card 4&lt;/article&gt;
  &lt;article&gt;Card 5&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .auto-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1em;
  }

  .auto-grid &gt; * {
    flex: 1 1 250px;
    /* flex-grow: 1, flex-shrink: 1, flex-basis: 250px */
    /* Min 250px before wrapping; grow equally to fill row */
  }
&lt;/style&gt;</code></pre>

<p><strong>How wrapping behaves:</strong></p>
<ul>
  <li><strong>Wide viewport (1500px)</strong>: 5 cards in one row, each ~290px wide.</li>
  <li><strong>Medium viewport (1000px)</strong>: 3 cards per row (third row has 2 cards).</li>
  <li><strong>Narrow viewport (600px)</strong>: 2 cards per row.</li>
  <li><strong>Phone (350px)</strong>: 1 card per row.</li>
</ul>

<p>No media queries; the breakpoints emerge from the math.</p>

<p><strong>The flex shorthand decoded:</strong></p>
<table>
  <tr><th>Shorthand</th><th>flex-grow</th><th>flex-shrink</th><th>flex-basis</th><th>Behavior</th></tr>
  <tr><td><code>flex: 1</code></td><td>1</td><td>1</td><td>0%</td><td>Equal width, ignores content</td></tr>
  <tr><td><code>flex: auto</code></td><td>1</td><td>1</td><td>auto</td><td>Sizes to content; grows to fill</td></tr>
  <tr><td><code>flex: 1 1 250px</code></td><td>1</td><td>1</td><td>250px</td><td>Min 250px; wraps when no room</td></tr>
  <tr><td><code>flex: 0 0 250px</code></td><td>0</td><td>0</td><td>250px</td><td>Fixed 250px; no grow/shrink</td></tr>
  <tr><td><code>flex: 1 1 auto</code></td><td>1</td><td>1</td><td>auto</td><td>Like <code>flex: auto</code></td></tr>
</table>

<p><strong>Trade-off vs Grid <code>auto-fit</code>:</strong></p>
<pre><code>/* Flexbox approach */
.flex-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}
.flex-grid &gt; * {
  flex: 1 1 250px;
  /* Last row: items fill the row by growing larger */
}

/* Grid approach */
.css-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1em;
  /* Last row: items keep their size; empty space remains on the right */
}</code></pre>

<table>
  <tr><th>Property</th><th>Flexbox wrap</th><th>Grid auto-fit</th></tr>
  <tr><td>Last row behavior</td><td>Items grow to fill width</td><td>Items stay at minmax size; empty space remains</td></tr>
  <tr><td>Equal-height rows</td><td>Independent rows</td><td>All rows use same column tracks</td></tr>
  <tr><td>Cell alignment across rows</td><td>No alignment between rows</td><td>Yes, columns align across rows</td></tr>
  <tr><td>Item placement</td><td>Source order only</td><td>Can reorder via grid-area</td></tr>
</table>

<p>For card-style layouts where the last row should fill the row width, Flexbox is best. For consistent column alignment across rows (like a true grid), CSS Grid is better. Use <code>auto-fill</code> instead of <code>auto-fit</code> in Grid to preserve column tracks even when fewer items.</p>

<p><strong>Common variations:</strong></p>

<p><strong>Center the last row:</strong></p>
<pre><code>.centered-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  justify-content: center;     /* center incomplete rows */
}
.centered-wrap &gt; * {
  flex: 0 1 250px;             /* don't grow; fixed width with shrink */
}</code></pre>

<p>Items stay 250px wide; incomplete rows are centered (more aesthetic for sparse content).</p>

<p><strong>Equal-height columns within rows:</strong></p>
<pre><code>.equal-rows {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}
.equal-rows &gt; * {
  flex: 1 1 250px;
  display: flex;
  flex-direction: column;
  /* Children stretch to row height by default */
}</code></pre>

<p>Cards in the same row equalize heights; new rows have independent heights.</p>

<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>Forgetting <code>flex-wrap: wrap</code></strong> &mdash; without it, items shrink instead of wrapping.</li>
  <li><strong>Using <code>flex-basis: 0%</code></strong> &mdash; ignores content; items size only by grow ratios. Often unwanted for card grids.</li>
  <li><strong>Box-sizing not <code>border-box</code></strong> &mdash; padding/border math throws off the wrap boundary.</li>
  <li><strong>Last row visually unbalanced</strong> &mdash; one wide card stretching to fill the row width can look odd. Consider <code>flex: 0 1 250px</code> + <code>justify-content: start</code> instead.</li>
</ul>
'''

ANSWERS[91] = r'''
<p>The <code>all</code> property is a CSS shorthand that <strong>resets every single property of an element to a specified value</strong> at once. It&rsquo;s a powerful tool for resetting styles for embedded components, third-party widgets, or to start fresh in a complex inheritance chain.</p>

<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>initial</code></td><td>Reset all properties to their CSS-defined initial values</td></tr>
  <tr><td><code>inherit</code></td><td>Make all properties inherit from parent</td></tr>
  <tr><td><code>unset</code></td><td>Each property: inherit if normally inherited, otherwise initial</td></tr>
  <tr><td><code>revert</code></td><td>Roll back to the user-agent (browser) default styling</td></tr>
  <tr><td><code>revert-layer</code></td><td>Roll back to the previous cascade layer (works with <code>@layer</code>)</td></tr>
</table>

<pre><code>.embedded-widget {
  all: initial;
  /* Resets every property to default — like styling from scratch */

  /* Now apply only what we want */
  font-family: inherit;
  font-size: 1rem;
  color: inherit;
}</code></pre>

<p><strong>Why this matters &mdash; reset complexity:</strong></p>
<p>Without <code>all</code>, resetting an element required listing every property:</p>
<pre><code>/* The old way */
.reset {
  margin: 0;
  padding: 0;
  font: inherit;
  color: inherit;
  background: none;
  border: none;
  text-align: left;
  vertical-align: baseline;
  /* ... and dozens more */
}</code></pre>

<p>With <code>all</code>, one declaration resets everything:</p>
<pre><code>.reset {
  all: initial;
}</code></pre>

<p><strong>Common use cases:</strong></p>

<p><strong>1. Embeddable third-party widgets</strong> &mdash; isolate from host site&rsquo;s styles:</p>
<pre><code>.my-widget {
  all: initial;
  /* Reset all inherited and cascading styles from the host page */
}
.my-widget * {
  all: revert;
  /* Inside, restore browser defaults so child elements behave normally */
}</code></pre>

<p><strong>2. Reset button/form elements</strong> &mdash; remove default browser styling:</p>
<pre><code>.custom-button {
  all: unset;
  /* Removes button styling — now style as needed */
  cursor: pointer;
  padding: 0.5em 1em;
  background: blue;
  color: white;
}</code></pre>

<p>Browser button defaults (background, border, padding, font) are erased &mdash; clean slate.</p>

<p><strong>3. Override a parent context:</strong></p>
<pre><code>.dark-theme .opt-out {
  all: revert;
  /* This element ignores dark theme; uses browser defaults */
}</code></pre>

<p><strong>The four reset values compared:</strong></p>
<pre><code>&lt;div class="parent"&gt;
  &lt;p class="initial"&gt;...&lt;/p&gt;
  &lt;p class="inherit"&gt;...&lt;/p&gt;
  &lt;p class="unset"&gt;...&lt;/p&gt;
  &lt;p class="revert"&gt;...&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent { color: red; font-size: 2em; }

  .initial { all: initial; }   /* Black text, default size */
  .inherit { all: inherit; }   /* Red text, 2em size */
  .unset   { all: unset; }     /* Red text (color inherits), default size (font-size doesn't inherit by default... wait, it does. Hmm.) */
  .revert  { all: revert; }    /* Browser default p styling */
&lt;/style&gt;</code></pre>

<p><strong>The subtle differences:</strong></p>
<table>
  <tr><th>Property type</th><th><code>initial</code></th><th><code>inherit</code></th><th><code>unset</code></th><th><code>revert</code></th></tr>
  <tr><td>Inheritable (color, font)</td><td>CSS initial</td><td>From parent</td><td>From parent</td><td>UA default</td></tr>
  <tr><td>Non-inheritable (margin)</td><td>CSS initial (0)</td><td>From parent</td><td>CSS initial</td><td>UA default</td></tr>
</table>

<p><strong><code>unset</code></strong> is "smart reset" &mdash; behaves like <code>inherit</code> for inheritable properties, like <code>initial</code> for non-inheritable. Often what you actually want.</p>

<p><strong><code>revert</code> &mdash; the user-agent fallback:</strong></p>
<pre><code>p { color: red; }

p.show-default {
  all: revert;
  /* Reverts to browser&rsquo;s default p styling — black text, 1em font-size */
}</code></pre>

<p><strong>Combine with <code>@layer</code></strong> for sophisticated cascade management:</p>
<pre><code>@layer base, components, utilities;

@layer base {
  button { background: gray; }
}

@layer components {
  .danger-btn { background: red; color: white; }
}

.disabled-btn {
  all: revert-layer;
  /* Roll back to the previous layer (base) — gray button styles apply */
}</code></pre>

<p><strong>Caveats:</strong></p>
<ul>
  <li><strong>Resets are powerful</strong> &mdash; <code>all: initial</code> wipes everything including helpful defaults like <code>display: block</code> on divs (which become inline). Test carefully.</li>
  <li><strong>Doesn&rsquo;t reset CSS variables</strong> (<code>--name</code>) &mdash; those are not standard properties.</li>
  <li><strong>Doesn&rsquo;t affect <code>direction</code> or <code>unicode-bidi</code></strong> on <code>initial</code> &mdash; those have special handling.</li>
  <li><strong>Use sparingly</strong> &mdash; for embedded components or true reset moments, not as a general styling tool.</li>
</ul>

<p>For most projects, <code>unset</code> is the most useful value &mdash; it&rsquo;s the "smart" reset for component starting points. <code>initial</code> is for total isolation. <code>revert</code> is for restoring browser defaults selectively.</p>
'''

ANSWERS[92] = r'''
<p>A CSS-only progress bar uses a colored inner element scaled to a percentage of the container. Multiple variants exist: linear bar (most common), striped/animated, indeterminate, segmented, and circular (covered separately).</p>

<p><strong>Native HTML progress element first &mdash; almost always the right answer:</strong></p>
<pre><code>&lt;progress value="60" max="100"&gt;60%&lt;/progress&gt;

&lt;style&gt;
  progress {
    width: 100%;
    height: 8px;
    -webkit-appearance: none;
    appearance: none;
    border: none;
    border-radius: 4px;
    overflow: hidden;
  }
  progress::-webkit-progress-bar {
    background: #f0f0f0;
  }
  progress::-webkit-progress-value {
    background: #0066cc;
    transition: width 0.3s ease;
  }
  progress::-moz-progress-bar {
    background: #0066cc;
  }
&lt;/style&gt;</code></pre>

<p>The <code>&lt;progress&gt;</code> element is semantic (assistive tech announces "60% complete"); the styling is browser-specific via vendor pseudo-elements but well-supported.</p>

<p><strong>CSS-only div-based progress bar</strong> &mdash; for designs that need full styling control:</p>
<pre><code>&lt;div class="progress" role="progressbar"
     aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"&gt;
  &lt;div class="progress-fill" style="width: 60%"&gt;&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .progress {
    width: 100%;
    height: 12px;
    background: #f0f0f0;
    border-radius: 6px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #0066cc, #4d8dd6);
    border-radius: 6px;
    transition: width 0.5s ease;
  }
&lt;/style&gt;</code></pre>

<p><strong>ARIA matters:</strong> <code>role="progressbar"</code> + <code>aria-valuenow</code>/<code>aria-valuemin</code>/<code>aria-valuemax</code> tells assistive tech the current state. Update <code>aria-valuenow</code> via JavaScript when progress changes.</p>

<p><strong>Animated stripes (loading indicator):</strong></p>
<pre><code>.progress-striped .progress-fill {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.2) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0.2) 75%,
    transparent 75%
  );
  background-size: 30px 30px;
  background-color: #0066cc;
  animation: stripes-move 1s linear infinite;
}

@keyframes stripes-move {
  from { background-position: 0 0; }
  to   { background-position: 30px 0; }
}</code></pre>

<p>The diagonal stripes "march" forward, giving the bar a sense of motion even when the actual percentage isn&rsquo;t changing &mdash; useful for indeterminate progress.</p>

<p><strong>Indeterminate progress</strong> &mdash; for unknown duration:</p>
<pre><code>.indeterminate {
  width: 100%;
  height: 4px;
  background: #f0f0f0;
  position: relative;
  overflow: hidden;
}
.indeterminate::before {
  content: "";
  position: absolute;
  top: 0;
  left: -50%;
  width: 50%;
  height: 100%;
  background: #0066cc;
  animation: indeterminate-slide 1.5s ease-in-out infinite;
}
@keyframes indeterminate-slide {
  from { left: -50%; }
  to   { left: 100%; }
}</code></pre>

<p>A 50%-wide highlight slides across the bar repeatedly &mdash; the user knows something&rsquo;s happening but can&rsquo;t see how close to done.</p>

<p><strong>Multi-step / segmented progress:</strong></p>
<pre><code>&lt;div class="step-progress" data-current="2"&gt;
  &lt;div class="step done"&gt;1&lt;/div&gt;
  &lt;div class="step done"&gt;2&lt;/div&gt;
  &lt;div class="step current"&gt;3&lt;/div&gt;
  &lt;div class="step"&gt;4&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .step-progress {
    display: flex;
    gap: 0;
    align-items: center;
  }
  .step {
    flex: 1;
    height: 30px;
    background: #f0f0f0;
    color: #888;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  .step.done {
    background: #0066cc;
    color: white;
  }
  .step.current {
    background: #4d8dd6;
    color: white;
  }
&lt;/style&gt;</code></pre>

<p><strong>Animated fill on view (modern, ~2024+)</strong> using scroll-driven animations:</p>
<pre><code>@keyframes fill {
  from { width: 0%; }
  to   { width: 100%; }
}

.progress-fill {
  animation: fill linear;
  animation-timeline: scroll();
  /* Width fills as user scrolls down the page */
}</code></pre>

<p>Reading-progress indicators &mdash; the bar fills based on scroll position. Pure CSS in modern browsers.</p>

<p><strong>JavaScript integration:</strong></p>
<pre><code>function updateProgress(percent) {
  const fill = document.querySelector(".progress-fill");
  const container = document.querySelector(".progress");
  fill.style.width = percent + "%";
  container.setAttribute("aria-valuenow", percent);
}</code></pre>

<p>Update both visual width and ARIA state together &mdash; never one without the other.</p>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Use <code>&lt;progress&gt;</code> when possible</strong> &mdash; it&rsquo;s semantic and accessible by default.</li>
  <li><strong>Provide context near the bar</strong>: "Uploading 42 of 100 files" or "60%" &mdash; numbers help users understand the rate.</li>
  <li><strong>Smooth transitions</strong> on width changes (<code>transition: width 0.3s ease</code>).</li>
  <li><strong>Indeterminate for true unknown durations</strong>; bar with percent for measurable progress.</li>
  <li><strong>Animate fills, not number labels</strong> &mdash; the visual smoothness is reassuring.</li>
</ul>
'''

ANSWERS[93] = r'''
<p>The <code>place-items</code> property is a shorthand for <code>align-items</code> + <code>justify-items</code> &mdash; controlling alignment of children on both axes in one declaration. It works in CSS Grid, where it&rsquo;s most powerful, and partially in Flexbox.</p>

<pre><code>.center-everything {
  display: grid;
  place-items: center;
  /* Equivalent: align-items: center; justify-items: center; */
  height: 100vh;
}</code></pre>

<p>One line centers all children both vertically and horizontally &mdash; the cleanest way to center anything in CSS.</p>

<p><strong>Syntax variations:</strong></p>
<table>
  <tr><th>Syntax</th><th>Effect</th></tr>
  <tr><td><code>place-items: center</code></td><td>Both axes: center</td></tr>
  <tr><td><code>place-items: start</code></td><td>Both axes: start</td></tr>
  <tr><td><code>place-items: end center</code></td><td>Block: end; Inline: center</td></tr>
  <tr><td><code>place-items: stretch start</code></td><td>Block: stretch; Inline: start</td></tr>
</table>

<p>The shorthand takes <code>&lt;align&gt; &lt;justify&gt;</code> &mdash; two values for separate axes. Single value applies to both.</p>

<p><strong>Key Grid alignment properties:</strong></p>
<table>
  <tr><th>Property</th><th>Controls</th><th>Applied to</th></tr>
  <tr><td><code>align-items</code></td><td>Block (vertical) alignment of all items</td><td>Container</td></tr>
  <tr><td><code>justify-items</code></td><td>Inline (horizontal) alignment of all items</td><td>Container</td></tr>
  <tr><td><code>place-items</code></td><td>Shorthand for both</td><td>Container</td></tr>
  <tr><td><code>align-self</code></td><td>Override align for one item</td><td>Item</td></tr>
  <tr><td><code>justify-self</code></td><td>Override justify for one item</td><td>Item</td></tr>
  <tr><td><code>place-self</code></td><td>Shorthand for align-self + justify-self</td><td>Item</td></tr>
  <tr><td><code>align-content</code></td><td>Block alignment of all rows (multi-row grids)</td><td>Container</td></tr>
  <tr><td><code>justify-content</code></td><td>Inline alignment of all columns</td><td>Container</td></tr>
  <tr><td><code>place-content</code></td><td>Shorthand for both</td><td>Container</td></tr>
</table>

<p><strong>The "items" vs "content" distinction:</strong></p>
<ul>
  <li><strong>place-items</strong> &mdash; aligns items WITHIN their grid cells.</li>
  <li><strong>place-content</strong> &mdash; aligns the entire grid track set within the container (when extra space exists).</li>
  <li><strong>place-self</strong> &mdash; per-item override.</li>
</ul>

<pre><code>.example {
  display: grid;
  grid-template-columns: 100px 100px;
  grid-template-rows: 100px 100px;
  width: 400px;
  height: 400px;
  border: 1px solid;

  /* Center each item in its cell */
  place-items: center;

  /* Center the entire grid track set within container */
  place-content: center;
}

.cell {
  width: 50px;
  height: 50px;
  background: blue;
}</code></pre>

<p>Result: the four cells are centered as a group within the container (400&times;400 with 200&times;200 grid centered = 100px margins all around), AND each 50&times;50 cell is centered within its 100&times;100 cell.</p>

<p><strong>Per-item override with <code>place-self</code></strong>:</p>
<pre><code>.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  place-items: center;            /* default: all centered */
}

.special {
  place-self: end stretch;        /* this item: bottom of cell, full width */
}</code></pre>

<p><strong>Flexbox usage</strong> &mdash; <code>place-items</code> works but with caveats:</p>
<pre><code>.flex-center {
  display: flex;
  place-items: center;
  /* In Flexbox, place-items maps to align-items + justify-items */
  /* But justify-items has no effect in Flexbox — Flexbox uses justify-content */
}

/* Better: */
.flex-center {
  display: flex;
  align-items: center;            /* cross-axis */
  justify-content: center;          /* main-axis */
}</code></pre>

<p>For Flexbox, manually set <code>align-items</code> + <code>justify-content</code> (NOT <code>justify-items</code>) &mdash; the centering behavior is similar but the property names differ.</p>

<p><strong>The classic centering recipes:</strong></p>
<table>
  <tr><th>Goal</th><th>CSS</th></tr>
  <tr><td>Center one element in viewport</td><td><code>body { display: grid; place-items: center; min-height: 100vh; }</code></td></tr>
  <tr><td>Center all items in a grid</td><td><code>display: grid; place-items: center;</code></td></tr>
  <tr><td>Center items + the grid itself</td><td><code>place-items: center; place-content: center;</code></td></tr>
  <tr><td>Center in Flexbox</td><td><code>display: flex; align-items: center; justify-content: center;</code></td></tr>
</table>

<p>Pre-2017 centering was famously hard (<code>position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);</code>). Now <code>place-items: center</code> is one line.</p>

<p><strong>Performance and rendering:</strong> alignment properties are pure layout calculations &mdash; no rendering performance penalty. Use freely.</p>
'''

ANSWERS[94] = r'''
<p>A sticky header within a Flexbox layout uses <code>position: sticky</code> on the header element with <code>top: 0</code>. The Flexbox layout positions the components; the sticky property locks the header to the viewport edge as content scrolls.</p>

<pre><code>&lt;div class="app"&gt;
  &lt;header class="sticky-header"&gt;
    &lt;a class="logo"&gt;Acme&lt;/a&gt;
    &lt;nav&gt;
      &lt;a&gt;Home&lt;/a&gt; &lt;a&gt;Products&lt;/a&gt; &lt;a&gt;About&lt;/a&gt;
    &lt;/nav&gt;
    &lt;button&gt;Sign in&lt;/button&gt;
  &lt;/header&gt;

  &lt;main&gt;
    &lt;article&gt;
      &lt;h1&gt;Article title&lt;/h1&gt;
      &lt;p&gt;Lots of content...&lt;/p&gt;
      &lt;!-- Many paragraphs --&gt;
    &lt;/article&gt;
  &lt;/main&gt;

  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .sticky-header {
    position: sticky;
    top: 0;
    z-index: 100;

    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1em 2em;
    background: white;
    border-bottom: 1px solid #eee;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0);
    transition: box-shadow 0.2s;
  }

  /* Optional: subtle shadow appears once the header is "stuck" */
  .sticky-header.scrolled {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  main {
    flex: 1;
    padding: 2em;
  }

  footer {
    background: #333;
    color: white;
    padding: 2em;
    text-align: center;
  }
&lt;/style&gt;</code></pre>

<p><strong>How <code>position: sticky</code> works:</strong></p>
<ol>
  <li>Element positions normally during scroll until its <code>top</code> threshold is reached.</li>
  <li>Once <code>top: 0</code> is exceeded, the element "sticks" &mdash; it stays at <code>top: 0</code> while parent scrolls past.</li>
  <li>When the parent fully scrolls past, the element scrolls with it (unsticking from view).</li>
</ol>

<p><strong>Critical: <code>position: sticky</code> can be broken by ancestor styles</strong>:</p>
<table>
  <tr><th>Ancestor style</th><th>Effect</th></tr>
  <tr><td><code>overflow: hidden</code></td><td>Sticky breaks &mdash; ancestor becomes scroll context</td></tr>
  <tr><td><code>overflow: auto</code></td><td>Same &mdash; sticky relative to that ancestor, not viewport</td></tr>
  <tr><td><code>overflow: clip</code></td><td>Sometimes breaks (depends on direction)</td></tr>
  <tr><td><code>height</code> shorter than content</td><td>Sticky element scrolls with the constrained height</td></tr>
  <tr><td><code>display: flex</code> with stretch</td><td>Sticky may stretch &mdash; use <code>align-self: start</code></td></tr>
</table>

<p>If your header isn&rsquo;t sticking, check every ancestor for <code>overflow</code>, <code>height</code>, and <code>display</code> issues.</p>

<p><strong>Adding a "stuck" visual indicator (modern):</strong></p>
<pre><code>.sticky-header {
  position: sticky;
  top: 0;
  background: white;
  transition: box-shadow 0.2s;
}

/* Modern: detect when sticky is actually stuck */
@supports (animation-timeline: scroll()) {
  .sticky-header {
    animation: header-stuck linear;
    animation-timeline: scroll();
    animation-range: 0 100px;
  }
  @keyframes header-stuck {
    to {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
    }
  }
}</code></pre>

<p>Scroll-driven animations let you transform the header as the page scrolls &mdash; shadow appears smoothly, background gets a subtle blur, all without JavaScript.</p>

<p><strong>JavaScript-based stuck detection</strong> (legacy or pre-Baseline):</p>
<pre><code>const header = document.querySelector(".sticky-header");
const sentinel = document.createElement("div");
header.before(sentinel);

const observer = new IntersectionObserver(
  ([entry]) =&gt; header.classList.toggle("scrolled", !entry.isIntersecting),
  { threshold: 0 }
);
observer.observe(sentinel);</code></pre>

<p>An invisible sentinel element sits above the header. When it scrolls out of view, the IntersectionObserver fires, and the "scrolled" class is added.</p>

<p><strong>Sticky vs Fixed positioning:</strong></p>
<table>
  <tr><th></th><th>Sticky</th><th>Fixed</th></tr>
  <tr><td>Source position</td><td>Stays in flow</td><td>Removed from flow</td></tr>
  <tr><td>Behavior</td><td>Sticks at threshold; scrolls with parent</td><td>Always at viewport position</td></tr>
  <tr><td>Affects layout</td><td>Yes (takes space)</td><td>No (overlay)</td></tr>
  <tr><td>Best for</td><td>Section-aware navigation</td><td>Persistent overlays (toolbars, FABs)</td></tr>
</table>

<p>For headers that should stick from the top of the page through scroll, sticky is right. For headers that always overlay regardless of position (rare), fixed is right.</p>

<p><strong>Combine sticky header with sticky table-of-contents:</strong></p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 1fr 250px;
  gap: 2em;
}
.sticky-header {
  position: sticky;
  top: 0;
  grid-column: 1 / -1;
  z-index: 100;
}
.sidebar-toc {
  position: sticky;
  top: 80px;             /* below the sticky header */
  align-self: start;
}</code></pre>

<p>Header sticks at top; TOC sticks below the header. Both use <code>position: sticky</code> &mdash; one of CSS&rsquo;s cleanest features for layered scroll experiences.</p>
'''

ANSWERS[95] = r'''
<p>The <code>scroll-margin</code> and <code>scroll-padding</code> properties offset scroll positions for anchored navigation, scroll-snap, and any programmatic scroll &mdash; the most common reason: preventing target content from hiding behind a fixed header.</p>

<table>
  <tr><th>Property</th><th>Applied to</th><th>Effect</th></tr>
  <tr><td><code>scroll-margin</code></td><td>The scroll TARGET</td><td>Adds outer space around the target</td></tr>
  <tr><td><code>scroll-padding</code></td><td>The scroll CONTAINER</td><td>Adds inner padding to the scroll viewport</td></tr>
</table>

<p><strong>The classic problem &mdash; anchor links hiding behind fixed header:</strong></p>
<pre><code>&lt;header class="fixed-header"&gt;Acme&lt;/header&gt;
&lt;main&gt;
  &lt;section id="features"&gt;...&lt;/section&gt;
  &lt;section id="pricing"&gt;...&lt;/section&gt;
&lt;/main&gt;
&lt;a href="#pricing"&gt;Pricing&lt;/a&gt;</code></pre>

<p>Clicking "Pricing" scrolls the section to the very top of the viewport &mdash; hidden behind the 80px-tall fixed header. Workarounds before <code>scroll-margin-top</code> required ugly invisible padding tricks or JavaScript.</p>

<p><strong>The clean solution &mdash; <code>scroll-margin-top</code></strong>:</p>
<pre><code>section[id] {
  scroll-margin-top: 80px;
  /* Anchor scrolls leave 80px above target — header stays visible */
}</code></pre>

<p>One line replaces all the legacy hacks. The browser knows to offset by 80px when scrolling to any section.</p>

<p><strong>Or via container with <code>scroll-padding-top</code>:</strong></p>
<pre><code>html {
  scroll-padding-top: 80px;
  /* Applies to ALL anchored scrolls in the document */
}</code></pre>

<p><strong>Choosing between the two:</strong></p>
<table>
  <tr><th>Use scroll-margin (target)</th><th>Use scroll-padding (container)</th></tr>
  <tr><td>Different targets need different offsets</td><td>All targets need the same offset</td></tr>
  <tr><td>Specific elements; not all sections</td><td>Document-wide rule</td></tr>
  <tr><td>Per-component encapsulation</td><td>Global header offset</td></tr>
</table>

<p>For most websites, <code>scroll-padding-top</code> on <code>html</code> is the simplest because the header is global. <code>scroll-margin-top</code> on individual sections is more flexible for components.</p>

<p><strong>Combining with <code>scroll-snap</code>:</strong></p>
<pre><code>.scroll-container {
  scroll-snap-type: y mandatory;
  scroll-padding-top: 60px;       /* offset for snap target */
  height: 100vh;
  overflow-y: auto;
}
.section {
  scroll-snap-align: start;
}</code></pre>

<p>Sections snap to start, but with a 60px offset &mdash; ideal when the snap container has a fixed header inside.</p>

<p><strong>Per-side properties:</strong></p>
<table>
  <tr><th>Property</th><th>Side</th></tr>
  <tr><td><code>scroll-margin-top</code></td><td>Top</td></tr>
  <tr><td><code>scroll-margin-bottom</code></td><td>Bottom</td></tr>
  <tr><td><code>scroll-margin-left</code></td><td>Left</td></tr>
  <tr><td><code>scroll-margin-right</code></td><td>Right</td></tr>
  <tr><td><code>scroll-margin</code></td><td>All four (shorthand)</td></tr>
  <tr><td><code>scroll-margin-block-start</code></td><td>Logical: top in horizontal-tb</td></tr>
  <tr><td><code>scroll-margin-inline-start</code></td><td>Logical: left in LTR</td></tr>
</table>

<p>Same pattern for <code>scroll-padding-*</code> on the container side.</p>

<p><strong>Real-world examples:</strong></p>

<p><strong>1. Documentation site with section navigation:</strong></p>
<pre><code>html {
  scroll-padding-top: 80px;   /* Below sticky doc header */
}

article :is(h1, h2, h3)[id] {
  scroll-margin-top: 100px;   /* Even more for headings */
}</code></pre>

<p>Headers and headings have slightly different offsets &mdash; per-element control.</p>

<p><strong>2. Image carousel with scroll-snap and visible thumbnails on either side:</strong></p>
<pre><code>.carousel {
  scroll-snap-type: x mandatory;
  scroll-padding: 0 60px;
  /* 60px padding lets adjacent slides peek into view */
}
.carousel img {
  scroll-snap-align: start;
}</code></pre>

<p>Each snapped image has 60px space on either side &mdash; users can see the next/previous image partially. Common pattern for "card carousels" with hint of next item.</p>

<p><strong>3. Long-form article with table of contents:</strong></p>
<pre><code>html {
  scroll-padding-top: 100px;
  scroll-behavior: smooth;
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}

article h2[id], article h3[id] {
  scroll-margin-top: 100px;
  /* TOC links land at correct position */
}</code></pre>

<p><strong>Common gotcha: <code>scroll-margin</code> doesn&rsquo;t work without scroll context</strong>:</p>
<ul>
  <li>The scroll container needs to actually scroll (have <code>overflow: auto</code> or be the viewport).</li>
  <li>The element needs to be within that scroll context.</li>
</ul>

<p>If <code>scroll-margin-top</code> is being ignored, check that the element is inside a scrollable container.</p>

<p><strong>Browser support</strong>: universal in 2026 (since ~2020 for both). Use freely.</p>
'''

ANSWERS[96] = r'''
<p>A vertical timeline displays chronological events along a vertical line &mdash; a common pattern for project history, resumes, changelogs. The CSS pattern uses pseudo-elements for the line and dots, with optional alternation of cards on either side.</p>

<pre><code>&lt;ol class="vertical-timeline"&gt;
  &lt;li&gt;
    &lt;time datetime="2024-01"&gt;January 2024&lt;/time&gt;
    &lt;h3&gt;Joined the company&lt;/h3&gt;
    &lt;p&gt;Started as a junior developer focused on frontend.&lt;/p&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;time datetime="2024-08"&gt;August 2024&lt;/time&gt;
    &lt;h3&gt;Led first major project&lt;/h3&gt;
    &lt;p&gt;Designed and shipped the analytics dashboard.&lt;/p&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;time datetime="2025-03"&gt;March 2025&lt;/time&gt;
    &lt;h3&gt;Promoted to senior&lt;/h3&gt;
    &lt;p&gt;Now leading a team of 4 developers.&lt;/p&gt;
  &lt;/li&gt;
&lt;/ol&gt;

&lt;style&gt;
  .vertical-timeline {
    list-style: none;
    padding: 2em 0 2em 3em;
    margin: 0;
    position: relative;
    max-width: 600px;
  }

  /* The vertical line */
  .vertical-timeline::before {
    content: "";
    position: absolute;
    left: 1em;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #0066cc, #4d8dd6);
  }

  .vertical-timeline li {
    position: relative;
    padding-left: 2em;
    padding-bottom: 2.5em;
  }

  /* Dot marker */
  .vertical-timeline li::before {
    content: "";
    position: absolute;
    left: -1.5em;
    top: 0.4em;
    width: 18px;
    height: 18px;
    background: white;
    border: 3px solid #0066cc;
    border-radius: 50%;
    z-index: 1;
  }

  .vertical-timeline time {
    color: #0066cc;
    font-weight: 600;
    font-size: 0.9em;
  }

  .vertical-timeline h3 {
    margin: 0.25em 0 0.5em;
  }

  .vertical-timeline p {
    color: #555;
    margin: 0;
  }
&lt;/style&gt;</code></pre>

<p><strong>Alternating left/right (zigzag) pattern:</strong></p>
<pre><code>&lt;style&gt;
  .timeline-zigzag {
    list-style: none;
    padding: 2em 0;
    margin: 0;
    position: relative;
    max-width: 800px;
  }

  /* Center vertical line */
  .timeline-zigzag::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #ddd;
    transform: translateX(-50%);
  }

  .timeline-zigzag li {
    width: 50%;
    padding: 1em 2em;
    position: relative;
    margin-bottom: 1em;
  }

  /* Odd items on right, even on left */
  .timeline-zigzag li:nth-child(odd) {
    margin-left: 50%;
    text-align: left;
  }

  .timeline-zigzag li:nth-child(even) {
    text-align: right;
  }

  /* Dot markers */
  .timeline-zigzag li::before {
    content: "";
    position: absolute;
    top: 1em;
    width: 16px;
    height: 16px;
    background: #0066cc;
    border: 3px solid white;
    border-radius: 50%;
    box-shadow: 0 0 0 2px #0066cc;
  }
  .timeline-zigzag li:nth-child(odd)::before {
    left: -8px;       /* dot on left edge of right card */
  }
  .timeline-zigzag li:nth-child(even)::before {
    right: -8px;      /* dot on right edge of left card */
  }

  /* Mobile: single column */
  @media (max-width: 600px) {
    .timeline-zigzag::before {
      left: 1em;
    }
    .timeline-zigzag li,
    .timeline-zigzag li:nth-child(odd) {
      width: 100%;
      margin-left: 0;
      padding-left: 3em;
      text-align: left;
    }
    .timeline-zigzag li:nth-child(odd)::before,
    .timeline-zigzag li:nth-child(even)::before {
      left: 0.5em;
      right: auto;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>Status colors with attribute selectors:</strong></p>
<pre><code>&lt;li data-status="completed"&gt;...&lt;/li&gt;
&lt;li data-status="current"&gt;...&lt;/li&gt;
&lt;li data-status="upcoming"&gt;...&lt;/li&gt;

&lt;style&gt;
  li[data-status="completed"]::before {
    background: #28a745;       /* green */
    border-color: #28a745;
  }
  li[data-status="current"]::before {
    background: #ffc107;       /* yellow */
    border-color: #ffc107;
    animation: pulse 1.5s ease-in-out infinite;
  }
  li[data-status="upcoming"]::before {
    background: white;          /* hollow */
    border-color: #ccc;
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.2); }
  }
&lt;/style&gt;</code></pre>

<p><strong>Modern: scroll-driven reveal animations</strong> &mdash; entries fade in as user scrolls:</p>
<pre><code>@supports (animation-timeline: view()) {
  .vertical-timeline li {
    animation: timeline-reveal linear;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
  @keyframes timeline-reveal {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
  }
}</code></pre>

<p>Each timeline entry slides in from the left as it scrolls into view. Pure CSS in modern browsers (2024+ Baseline).</p>

<p><strong>Accessibility:</strong></p>
<ul>
  <li><strong>Use <code>&lt;ol&gt;</code></strong> if order matters chronologically; <code>&lt;ul&gt;</code> if just a list.</li>
  <li><strong>Use <code>&lt;time datetime="..."&gt;</code></strong> &mdash; machines parse the structure; assistive tech can announce dates properly.</li>
  <li><strong>Don&rsquo;t convey meaning only via dot color</strong> &mdash; pair with text labels for status.</li>
  <li><strong>Logical heading hierarchy</strong> &mdash; if timeline is the page&rsquo;s primary content, use <code>h2</code>/<code>h3</code> appropriately.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; disable scroll-driven animations for opt-out users.</li>
</ul>

<p>For interactive timelines (clickable, expandable, filterable), pure CSS hits its limits &mdash; reach for a JavaScript framework or library. The above pattern handles ~90% of static "history" timelines without code.</p>
'''

ANSWERS[97] = r'''
<p>The <code>@layer</code> rule (Cascade Layers, Baseline 2022) introduced <strong>explicit ordering of CSS specificity by layer</strong>. Without layers, specificity battles led to !important overrides and brittle code; with layers, you can declare "framework styles always lose to my custom styles regardless of selector specificity."</p>

<p>Cascade layers add a new dimension to the cascade ordering rules. The order (highest precedence wins):</p>
<ol>
  <li>Importance (<code>!important</code> reverses order)</li>
  <li>Origin (user agent < user < author)</li>
  <li><strong>Cascade layer</strong> (later-declared layers win)</li>
  <li>Specificity (within same layer)</li>
  <li>Source order (within same specificity)</li>
</ol>

<pre><code>@layer base, framework, components, utilities;

@layer base {
  body { font-family: sans-serif; }
}

@layer framework {
  /* External library styles */
  .btn { background: blue; padding: 0.5em 1em; }
}

@layer components {
  /* Your component styles */
  .btn-special { background: red; }
}

@layer utilities {
  /* Atomic utilities */
  .text-center { text-align: center; }
  .hidden { display: none; }
}</code></pre>

<p><strong>Critical: declaration order matters</strong> &mdash; the first <code>@layer base, framework, components, utilities;</code> line establishes the order. Layers declared later (in source order) take precedence regardless of selector specificity.</p>

<p>So <code>.btn-special</code> in <code>components</code> always wins over <code>.btn</code> in <code>framework</code> &mdash; even though both have specificity 0,1,0 &mdash; because <code>components</code> is later in the layer order.</p>

<p><strong>Why this is revolutionary:</strong></p>
<table>
  <tr><th>Pre-layers approach</th><th>With layers</th></tr>
  <tr><td>Specificity wars</td><td>Layer order trumps specificity</td></tr>
  <tr><td>!important everywhere</td><td>!important rarely needed</td></tr>
  <tr><td>Framework hard to override</td><td>Framework in lower layer; your code wins</td></tr>
  <tr><td>Order in stylesheet matters</td><td>Layer order is explicit</td></tr>
  <tr><td>Brittle composition</td><td>Predictable cascade</td></tr>
</table>

<p><strong>Importing third-party CSS into a layer:</strong></p>
<pre><code>@import url("bootstrap.css") layer(framework);
@import url("./reset.css") layer(base);

@layer base, framework, components, utilities;

/* Your component styles outside any @layer */
.my-component { color: red; }
/* Unlayered styles have HIGHER precedence than ALL layers */</code></pre>

<p><strong>Anonymous (unnamed) layers</strong>:</p>
<pre><code>@layer {
  /* Anonymous layer — can't be referenced again */
  .foo { color: blue; }
}</code></pre>

<p>Useful for one-off groupings; can&rsquo;t be reordered or extended.</p>

<p><strong>Nested layers</strong>:</p>
<pre><code>@layer components {
  @layer base, modifiers;

  @layer base {
    .card { padding: 1em; }
  }

  @layer modifiers {
    .card-large { padding: 2em; }
  }
}</code></pre>

<p>Within "components", "modifiers" comes after "base" so modifier styles win over base ones &mdash; nested cascade control.</p>

<p><strong>The <code>!important</code> reversal &mdash; subtle but important:</strong></p>
<table>
  <tr><th>Origin</th><th>Important?</th><th>Layer order</th></tr>
  <tr><td>Author</td><td>Normal</td><td>Later layers WIN</td></tr>
  <tr><td>Author</td><td>!important</td><td>Earlier layers WIN (reversed!)</td></tr>
</table>

<p>For <code>!important</code> declarations, layer order is REVERSED &mdash; an early layer&rsquo;s !important beats a later layer&rsquo;s !important. This is intentional: it lets framework/base layers force critical defaults that components can&rsquo;t accidentally override.</p>

<p><strong>Real-world architecture:</strong></p>
<pre><code>/* The recommended setup */
@layer reset, base, themes, framework, components, layouts, utilities;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
}

@layer base {
  :root {
    --color-primary: #0066cc;
    --font-body: system-ui, sans-serif;
  }
  body { font-family: var(--font-body); }
}

@layer themes {
  [data-theme="dark"] {
    --color-primary: #4d8dd6;
  }
}

@layer framework {
  /* Tailwind, Bootstrap, etc. */
}

@layer components {
  .card { ... }
  .btn { ... }
}

@layer utilities {
  .visually-hidden { ... }
  .clearfix::after { ... }
}</code></pre>

<p><strong>Common patterns:</strong></p>
<ul>
  <li><strong>"Reset" first</strong> &mdash; lowest priority; can be overridden by everything.</li>
  <li><strong>"Utilities" last</strong> &mdash; highest priority; atomic helpers always win.</li>
  <li><strong>Framework lower than components</strong> &mdash; your component code overrides framework.</li>
  <li><strong>Themes between base and components</strong> &mdash; theme variables override base; components apply themes.</li>
</ul>

<p><strong>Browser support (2026)</strong>: universal. Baseline 2022; safe for all modern browsers without polyfills.</p>

<p><strong>Combine with the <code>:where()</code> pseudo-class</strong> for zero-specificity:</p>
<pre><code>@layer base {
  :where(h1, h2, h3) { font-weight: 600; }
  /* :where adds zero specificity — easily overridable */
}</code></pre>

<p>Layers handle macro-level cascade order; <code>:where</code> handles micro-level specificity. Together they give precise control over the cascade.</p>

<p><strong>The result</strong>: dramatically less !important, more predictable cascade behavior, easier framework integration. One of CSS&rsquo;s most impactful additions in the last decade.</p>
'''

ANSWERS[98] = r'''
<p>Combining CSS subgrid with media queries (or container queries) creates responsive layouts where nested grids inherit parent tracks &mdash; child elements maintain alignment across rearrangements. This is the cleanest pattern for card grids, comparison tables, and pricing matrices that need internal section alignment regardless of breakpoint.</p>

<pre><code>&lt;section class="card-grid"&gt;
  &lt;article class="card"&gt;
    &lt;img src="1.jpg" alt=""&gt;
    &lt;h3&gt;Short title&lt;/h3&gt;
    &lt;p&gt;Description text.&lt;/p&gt;
    &lt;a href="#"&gt;Read more&lt;/a&gt;
  &lt;/article&gt;
  &lt;article class="card"&gt;
    &lt;img src="2.jpg" alt=""&gt;
    &lt;h3&gt;A much longer title that wraps&lt;/h3&gt;
    &lt;p&gt;Lorem ipsum dolor sit amet.&lt;/p&gt;
    &lt;a href="#"&gt;Read more&lt;/a&gt;
  &lt;/article&gt;
  &lt;article class="card"&gt;
    &lt;img src="3.jpg" alt=""&gt;
    &lt;h3&gt;Medium length title&lt;/h3&gt;
    &lt;p&gt;Some content that goes on for two lines explaining things in detail.&lt;/p&gt;
    &lt;a href="#"&gt;Read more&lt;/a&gt;
  &lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    grid-template-rows: auto auto auto auto;     /* image, title, description, CTA */
    gap: 1.5em;
    padding: 2em;
  }

  .card {
    grid-row: span 4;             /* each card spans 4 outer rows */
    display: grid;
    grid-template-rows: subgrid;   /* INHERIT outer rows */
    gap: 0.75em;

    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    padding: 1em;
  }

  .card img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 8px;
  }

  .card h3 {
    margin: 0;
  }

  .card p {
    color: #555;
    margin: 0;
  }

  .card a {
    align-self: start;            /* don't stretch */
    color: #0066cc;
    text-decoration: none;
    font-weight: 600;
  }

  /* Responsive: rearrange on tablets */
  @media (max-width: 1024px) {
    .card-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  /* Mobile: single column, but subgrid still aligns title sections */
  @media (max-width: 600px) {
    .card-grid {
      grid-template-columns: 1fr;
      grid-template-rows: auto;     /* let cards size naturally */
    }
    .card {
      grid-row: auto;
      grid-template-rows: auto;     /* exit subgrid */
      gap: 0.5em;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>The magic of subgrid for responsive design:</strong></p>
<ul>
  <li><strong>All cards in a row align internally</strong> &mdash; regardless of which card has the longer title or shorter description.</li>
  <li><strong>Wrapping rows reset alignment</strong> &mdash; Row 1 and Row 2 cards align independently within their respective rows.</li>
  <li><strong>Maintains semantic structure</strong> &mdash; HTML stays clean.</li>
  <li><strong>Works at any breakpoint</strong> &mdash; the subgrid relationship is preserved as long as cards remain in the parent grid.</li>
</ul>

<p><strong>Pricing comparison example:</strong></p>
<pre><code>&lt;section class="plans"&gt;
  &lt;article class="plan"&gt;
    &lt;h3&gt;Starter&lt;/h3&gt;
    &lt;p class="price"&gt;$9&lt;/p&gt;
    &lt;ul class="features"&gt;
      &lt;li&gt;Feature 1&lt;/li&gt;
      &lt;li&gt;Feature 2&lt;/li&gt;
      &lt;li&gt;Feature 3&lt;/li&gt;
    &lt;/ul&gt;
    &lt;a class="cta" href="#"&gt;Choose Starter&lt;/a&gt;
  &lt;/article&gt;
  &lt;!-- More plans... --&gt;
&lt;/section&gt;

&lt;style&gt;
  .plans {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto auto 1fr auto;     /* heading, price, features (flex), cta */
    gap: 1em;
  }
  .plan {
    grid-row: span 4;
    display: grid;
    grid-template-rows: subgrid;
    /* All plans align: heading row, price row, features section, CTA row */
  }
&lt;/style&gt;</code></pre>

<p>Plan headings align across plans; prices align; features lists align (even if one plan has fewer features); CTAs align at the bottom. Without subgrid, achieving this required either fixed heights (brittle) or JavaScript measuring/setting heights.</p>

<p><strong>Combine with container queries</strong> &mdash; component-level responsive subgrid:</p>
<pre><code>.card-grid {
  container-type: inline-size;
  display: grid;
  grid-template-rows: auto auto auto auto;
}

@container (min-width: 600px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container (min-width: 1000px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}</code></pre>

<p>The card grid responds to its OWN width, not the viewport &mdash; same component works in a sidebar (1 column) or main content area (3 columns).</p>

<p><strong>Both axes:</strong></p>
<pre><code>.full-subgrid {
  display: grid;
  grid-template-columns: subgrid;
  grid-template-rows: subgrid;
  /* Inherit BOTH columns and rows from parent */
}</code></pre>

<p>Full subgrid inheritance lets you place children in any cell of the outer grid &mdash; useful for complex magazine-style layouts.</p>

<p><strong>Browser support (2026):</strong></p>
<table>
  <tr><th>Browser</th><th>Status</th></tr>
  <tr><td>Firefox</td><td>Yes (since 71, 2019)</td></tr>
  <tr><td>Safari</td><td>Yes (since 16, 2022)</td></tr>
  <tr><td>Chrome / Edge</td><td>Yes (since 117, 2023)</td></tr>
</table>

<p>Baseline 2024 &mdash; production-ready in 2026. Use without polyfills.</p>

<p><strong>Fallback for legacy browsers:</strong></p>
<pre><code>.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}
.card {
  flex: 1 1 280px;
}

@supports (grid-template-columns: subgrid) {
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    grid-template-rows: auto auto auto auto;
  }
  .card {
    grid-row: span 4;
    display: grid;
    grid-template-rows: subgrid;
  }
}</code></pre>

<p>Falls back to Flexbox layout (no internal alignment) for old browsers; gets full subgrid alignment for modern ones. Progressive enhancement.</p>
'''

ANSWERS[99] = r'''
<p>The <code>mix-blend-mode</code> property defines <strong>how an element&rsquo;s pixels blend with the colors below</strong> &mdash; like Photoshop layer blend modes. It enables sophisticated color effects, image overlays, and design accents that would otherwise require image processing.</p>

<table>
  <tr><th>Mode</th><th>Effect</th></tr>
  <tr><td><code>normal</code> (default)</td><td>No blending; element overlays</td></tr>
  <tr><td><code>multiply</code></td><td>Darkens; white becomes transparent</td></tr>
  <tr><td><code>screen</code></td><td>Lightens; black becomes transparent</td></tr>
  <tr><td><code>overlay</code></td><td>Multiplies dark, screens light</td></tr>
  <tr><td><code>darken</code></td><td>Picks darker of two colors</td></tr>
  <tr><td><code>lighten</code></td><td>Picks lighter of two colors</td></tr>
  <tr><td><code>color-dodge</code></td><td>Brightens based on overlay</td></tr>
  <tr><td><code>color-burn</code></td><td>Darkens based on overlay</td></tr>
  <tr><td><code>difference</code></td><td>Subtraction (creates inversion effects)</td></tr>
  <tr><td><code>exclusion</code></td><td>Like difference but lower contrast</td></tr>
  <tr><td><code>hue</code> / <code>saturation</code> / <code>color</code> / <code>luminosity</code></td><td>HSL component blending</td></tr>
</table>

<pre><code>&lt;div class="hero"&gt;
  &lt;img src="background.jpg" alt=""&gt;
  &lt;h1 class="text-blend"&gt;BLEND MODE&lt;/h1&gt;
&lt;/div&gt;

&lt;style&gt;
  .hero {
    position: relative;
    background: white;
  }
  .hero img {
    width: 100%;
    height: 400px;
    object-fit: cover;
  }
  .text-blend {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 6em;
    font-weight: 900;
    color: white;
    mix-blend-mode: difference;
    /* Text appears in the inverted color of whatever is behind it — always visible */
  }
&lt;/style&gt;</code></pre>

<p><strong>Common use cases:</strong></p>

<p><strong>1. Text legibility on any background</strong> &mdash; <code>difference</code>:</p>
<pre><code>.always-visible-text {
  color: white;
  mix-blend-mode: difference;
  /* Text inverts whatever&rsquo;s behind &mdash; always contrasts */
}</code></pre>

<p>White text with <code>difference</code> shows as black on light backgrounds, white on dark. Brilliant for hero headlines on photo backgrounds.</p>

<p><strong>2. Image color overlays:</strong></p>
<pre><code>.brand-overlay {
  position: relative;
}
.brand-overlay::after {
  content: "";
  position: absolute;
  inset: 0;
  background: #0066cc;
  mix-blend-mode: multiply;
  /* Image takes on a blue tint */
}</code></pre>

<p>Multiply with a solid color tints the underlying image &mdash; the look used by photo blogs and brand sites for consistent imagery.</p>

<p><strong>3. Vintage/duotone effects:</strong></p>
<pre><code>.duotone {
  filter: grayscale(1);
  position: relative;
}
.duotone::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, #ff6b35, #0066cc);
  mix-blend-mode: lighten;
}</code></pre>

<p>Grayscale image + colored gradient with <code>lighten</code> creates Spotify-style duotone images.</p>

<p><strong>4. Logo on busy background</strong> &mdash; using <code>luminosity</code>:</p>
<pre><code>.logo-on-photo {
  mix-blend-mode: luminosity;
  /* Logo takes the photo&rsquo;s lightness; logo&rsquo;s color is replaced by photo&rsquo;s */
}</code></pre>

<p><strong><code>mix-blend-mode</code> vs <code>background-blend-mode</code></strong>:</p>
<table>
  <tr><th></th><th><code>mix-blend-mode</code></th><th><code>background-blend-mode</code></th></tr>
  <tr><td>Affects</td><td>The element with siblings/parent</td><td>Multiple background layers within one element</td></tr>
  <tr><td>Common use</td><td>Text over image, overlay tints</td><td>Tint within a single element with multi-image background</td></tr>
</table>

<pre><code>/* background-blend-mode: blends within one element&rsquo;s backgrounds */
.element {
  background:
    linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
    url("photo.jpg");
  background-blend-mode: multiply;
}

/* mix-blend-mode: blends with what&rsquo;s rendered below */
.image1 { ... }
.image2 {
  mix-blend-mode: multiply;
  /* Blends with image1 if they overlap */
}</code></pre>

<p><strong>Stacking context note:</strong> <code>mix-blend-mode</code> creates a new stacking context. The blending happens within the nearest ancestor with <code>isolation: isolate</code> (or one that creates a stacking context).</p>

<pre><code>.section {
  isolation: isolate;
  /* Contains the blend within this section */
}
.section .blended {
  mix-blend-mode: multiply;
  /* Blends only with siblings inside .section, not anything outside */
}</code></pre>

<p>Without <code>isolate</code>, blends might interact with unexpected ancestor backgrounds. Use <code>isolation: isolate</code> to scope blends to a section.</p>

<p><strong>Visual examples &mdash; useful blend modes for design:</strong></p>
<ul>
  <li><strong>multiply</strong>: stamps, watermarks, photo overlays.</li>
  <li><strong>screen</strong>: light leaks, glare effects.</li>
  <li><strong>overlay</strong>: contrast-boosted overlays, "punchy" tinting.</li>
  <li><strong>difference</strong>: always-visible text, inverted highlights.</li>
  <li><strong>color</strong>: tinting (preserves luminance, replaces hue).</li>
  <li><strong>luminosity</strong>: structural overlays (uses lightness only).</li>
</ul>

<p><strong>Performance:</strong> blend modes are GPU-rasterized but require composing additional layers. Heavy use can affect performance on lower-end devices &mdash; test on real hardware. For decorative effects on a few elements per page, performance is fine.</p>

<p><strong>Browser support:</strong> universal in 2026.</p>
'''

ANSWERS[100] = r'''
<p>A circular progress bar shows progress as an arc around a circle &mdash; common for loading indicators, completion percentages, and dashboard widgets. Pure CSS uses SVG circles with <code>stroke-dasharray</code> manipulation; the modern approach combines that with <code>conic-gradient</code> for fill-based variants.</p>

<p><strong>Method 1: SVG with stroke-dasharray (most flexible):</strong></p>
<pre><code>&lt;div class="circular-progress" style="--progress: 75"&gt;
  &lt;svg viewBox="0 0 100 100"&gt;
    &lt;circle class="bg" cx="50" cy="50" r="45"/&gt;
    &lt;circle class="bar" cx="50" cy="50" r="45"/&gt;
  &lt;/svg&gt;
  &lt;span class="label"&gt;75%&lt;/span&gt;
&lt;/div&gt;

&lt;style&gt;
  .circular-progress {
    width: 150px;
    height: 150px;
    position: relative;
    --progress: 0;
  }
  .circular-progress svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);     /* start from top instead of right */
  }
  .circular-progress circle {
    fill: none;
    stroke-width: 8;
  }
  .bg {
    stroke: #f0f0f0;
  }
  .bar {
    stroke: #0066cc;
    stroke-linecap: round;
    stroke-dasharray: 283;          /* 2 * &pi; * 45 = circumference */
    stroke-dashoffset: calc(283 - (283 * var(--progress) / 100));
    transition: stroke-dashoffset 0.5s ease;
  }
  .label {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5em;
    font-weight: bold;
  }
&lt;/style&gt;</code></pre>

<p><strong>How <code>stroke-dasharray</code> + <code>stroke-dashoffset</code> works:</strong></p>
<ul>
  <li><strong><code>stroke-dasharray: 283</code></strong> &mdash; the circle&rsquo;s circumference (2&pi;r = 2 * 3.14 * 45 = 283).</li>
  <li><strong><code>stroke-dashoffset</code></strong> hides part of the stroke. <code>0</code> = full visible; <code>283</code> = invisible.</li>
  <li>For 75% progress: <code>stroke-dashoffset = 283 - (283 * 75 / 100) = 70.75</code> &mdash; reveals 75% of the circle.</li>
</ul>

<p><strong>Method 2: <code>conic-gradient</code></strong> &mdash; simpler for fill-style progress:</p>
<pre><code>&lt;div class="conic-progress" style="--progress: 75"&gt;
  &lt;span&gt;75%&lt;/span&gt;
&lt;/div&gt;

&lt;style&gt;
  .conic-progress {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background:
      conic-gradient(#0066cc calc(var(--progress) * 1%), #f0f0f0 0);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  .conic-progress::before {
    content: "";
    position: absolute;
    inset: 8px;
    background: white;
    border-radius: 50%;
    /* "Donut hole" — leaves the colored ring visible */
  }
  .conic-progress span {
    position: relative;
    font-size: 1.5em;
    font-weight: bold;
    z-index: 1;
  }
&lt;/style&gt;</code></pre>

<p>The <code>conic-gradient</code> creates a pie-slice effect; the inner white circle hides the center, leaving only a ring visible. Simpler markup but less flexibility than SVG.</p>

<p><strong>Animated progress fill</strong> using <code>@property</code> for animatable custom properties:</p>
<pre><code>@property --progress {
  syntax: "&lt;number&gt;";
  initial-value: 0;
  inherits: false;
}

.animate-fill {
  --progress: 0;
  background:
    conic-gradient(#0066cc calc(var(--progress) * 1%), #f0f0f0 0);
  animation: fill 2s ease-out forwards;
}

@keyframes fill {
  to { --progress: 75; }
}</code></pre>

<p>Without <code>@property</code>, you can&rsquo;t animate custom property values smoothly; the browser interpolates discrete steps. <code>@property</code> declares the type and lets the browser animate them as numbers.</p>

<p><strong>Multi-segment progress (rings):</strong></p>
<pre><code>.activity-rings {
  position: relative;
  width: 200px;
  height: 200px;
}
.ring-1, .ring-2, .ring-3 {
  position: absolute;
  border-radius: 50%;
  background: conic-gradient(var(--color) var(--pct), #eee 0);
}
.ring-1 { inset: 0;   --color: red;   --pct: 80%; }
.ring-2 { inset: 12px; --color: green; --pct: 60%; }
.ring-3 { inset: 24px; --color: blue;  --pct: 40%; }
.ring-1::before, .ring-2::before, .ring-3::before {
  content: "";
  position: absolute;
  inset: 8px;
  background: white;
  border-radius: 50%;
}</code></pre>

<p>Apple Watch-style activity rings &mdash; concentric circular progress bars layered.</p>

<p><strong>JavaScript update pattern:</strong></p>
<pre><code>function setProgress(percentage) {
  const progress = document.querySelector(".circular-progress");
  progress.style.setProperty("--progress", percentage);
  progress.querySelector(".label").textContent = percentage + "%";
  progress.setAttribute("aria-valuenow", percentage);
}
setProgress(75);</code></pre>

<p>The CSS variable drives both the SVG <code>stroke-dashoffset</code> calculation AND the conic-gradient angle &mdash; one source of truth.</p>

<p><strong>Accessibility:</strong></p>
<pre><code>&lt;div class="circular-progress"
     role="progressbar"
     aria-valuenow="75"
     aria-valuemin="0"
     aria-valuemax="100"
     aria-label="Loading progress"&gt;
  ...
&lt;/div&gt;</code></pre>

<p><code>role="progressbar"</code> + the three <code>aria-value*</code> attributes are essential. Update <code>aria-valuenow</code> when the percentage changes.</p>

<p><strong>Comparison of approaches:</strong></p>
<table>
  <tr><th>Method</th><th>Strength</th><th>Limitation</th></tr>
  <tr><td>SVG stroke-dasharray</td><td>Flexible animation, gradient strokes, glow effects</td><td>More complex math; SVG markup overhead</td></tr>
  <tr><td>conic-gradient</td><td>Simple, no SVG needed</td><td>Limited styling; no rounded ends; tricky animation</td></tr>
  <tr><td>SVG with @property</td><td>Smooth animation; modern</td><td>Requires modern browser</td></tr>
  <tr><td>Library (e.g., react-circular-progressbar)</td><td>Easy, polished</td><td>Bundle size</td></tr>
</table>

<p>For static or rarely-updated progress, conic-gradient is fine. For animated, interactive, or styled progress (rounded ends, gradient strokes, glow effects), SVG is the better choice.</p>
'''

ANSWERS[101] = r'''
<p>The <code>grid-template</code> property is a <strong>powerful shorthand combining grid-template-rows, grid-template-columns, and grid-template-areas in one declaration</strong>. While individual properties are clearer for simple grids, the shorthand makes complex layouts more compact and self-documenting when used well.</p>

<p><strong>Three forms of <code>grid-template</code>:</strong></p>

<p><strong>Form 1: Just rows / columns:</strong></p>
<pre><code>.simple {
  grid-template: auto 1fr auto / 200px 1fr 200px;
  /* Equivalent to:
     grid-template-rows: auto 1fr auto;
     grid-template-columns: 200px 1fr 200px;
  */
}</code></pre>

<p>The <code>/</code> separator divides rows from columns. Compact but cryptic for newcomers.</p>

<p><strong>Form 2: With template-areas (the powerful form):</strong></p>
<pre><code>.with-areas {
  grid-template:
    "header header header"  auto
    "nav    main   aside"   1fr
    "footer footer footer"  auto
    / 200px 1fr 250px;
}

/* Equivalent to:
   grid-template-areas:
     "header header header"
     "nav    main   aside"
     "footer footer footer";
   grid-template-rows: auto 1fr auto;
   grid-template-columns: 200px 1fr 250px;
*/</code></pre>

<p>Rows are defined inline with each template-area string &mdash; the row size goes after the area string. Columns follow the <code>/</code>. This visual grouping is highly readable for layout.</p>

<p><strong>Form 3: <code>none</code></strong> &mdash; reset:</p>
<pre><code>.reset {
  grid-template: none;
  /* Resets all three sub-properties to their initial values */
}</code></pre>

<p><strong>Practical example &mdash; complete page layout:</strong></p>
<pre><code>&lt;div class="page"&gt;
  &lt;header&gt;Header&lt;/header&gt;
  &lt;nav&gt;Navigation&lt;/nav&gt;
  &lt;main&gt;Main content&lt;/main&gt;
  &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  .page {
    display: grid;
    min-height: 100vh;
    gap: 1em;

    grid-template:
      "header header header"  auto
      "nav    main   aside"   1fr
      "footer footer footer"  auto
      / 200px 1fr 200px;
  }

  header { grid-area: header; }
  nav    { grid-area: nav; }
  main   { grid-area: main; }
  aside  { grid-area: aside; }
  footer { grid-area: footer; }

  /* Mobile: rearrange */
  @media (max-width: 768px) {
    .page {
      grid-template:
        "header" auto
        "nav"    auto
        "main"   1fr
        "aside"  auto
        "footer" auto
        / 1fr;
    }
  }
&lt;/style&gt;</code></pre>

<p>The <code>grid-template</code> shorthand makes the layout immediately readable &mdash; the visual structure is in the source.</p>

<p><strong>Comparison with separate properties:</strong></p>
<pre><code>/* Same result, separated form */
.page {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 200px 1fr 200px;
  grid-template-areas:
    "header header header"
    "nav    main   aside"
    "footer footer footer";
  gap: 1em;
}

/* Combined form */
.page {
  display: grid;
  grid-template:
    "header header header"  auto
    "nav    main   aside"   1fr
    "footer footer footer"  auto
    / 200px 1fr 200px;
  gap: 1em;
}</code></pre>

<table>
  <tr><th>Form</th><th>When to use</th></tr>
  <tr><td>Separate properties</td><td>Simple grids; teaching/learning; readability priority</td></tr>
  <tr><td>Combined shorthand</td><td>Complex layouts; templates that may be conditionally swapped</td></tr>
  <tr><td>Mixing</td><td>Avoid &mdash; choose one approach per grid</td></tr>
</table>

<p><strong>The <em>even shorter</em> shorthand: <code>grid</code></strong> includes implicit grid behavior:</p>
<pre><code>.page {
  display: grid;
  grid:
    "header header header"  auto
    "nav    main   aside"   1fr
    "footer footer footer"  auto
    / 200px 1fr 200px;
  /* Equivalent to grid-template + reset of grid-auto-* */
}</code></pre>

<p>The <code>grid</code> shorthand also resets <code>grid-auto-rows</code>, <code>grid-auto-columns</code>, and <code>grid-auto-flow</code>. Use sparingly &mdash; <code>grid-template</code> is usually clearer.</p>

<p><strong>Common patterns with <code>grid-template</code>:</strong></p>

<p><strong>Three-column with fixed sidebar:</strong></p>
<pre><code>grid-template:
  "header header" auto
  "nav    main"   1fr
  "footer footer" auto
  / 250px 1fr;</code></pre>

<p><strong>Hero with content below:</strong></p>
<pre><code>grid-template:
  "hero hero" 60vh
  "main aside" 1fr
  / 1fr 250px;</code></pre>

<p><strong>Card with image and content:</strong></p>
<pre><code>grid-template:
  "image"  auto
  "title"  auto
  "body"   1fr
  "actions" auto
  / 1fr;</code></pre>

<p><strong>Magazine 12-column adapted to template-areas:</strong></p>
<pre><code>.magazine {
  grid-template:
    ".      hero    hero    hero    hero    ."     400px
    "intro  intro   intro   sidebar sidebar sidebar" auto
    "content content content sidebar sidebar sidebar" 1fr
    / repeat(6, 1fr);
}</code></pre>

<p><strong>Subgrid with grid-template:</strong></p>
<pre><code>.parent {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
}
.child {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: subgrid;
  /* Inherits parent&rsquo;s tracks */
}</code></pre>

<p><strong>Tips for working with <code>grid-template</code>:</strong></p>
<ul>
  <li><strong>Align template strings vertically</strong> using whitespace &mdash; the visual representation aids comprehension.</li>
  <li><strong>Use the dot</strong> <code>.</code> for empty cells &mdash; explicit and clear.</li>
  <li><strong>Each template-area string must be quoted</strong>.</li>
  <li><strong>Row sizes can use any unit</strong> &mdash; <code>auto</code>, <code>1fr</code>, <code>min-content</code>, <code>200px</code>, <code>minmax(100px, 1fr)</code>.</li>
  <li><strong>Areas must form rectangles</strong> &mdash; can&rsquo;t make L-shapes.</li>
  <li><strong>Mind the <code>/</code> separator</strong> &mdash; columns come after; rows before.</li>
</ul>

<p>For 90% of layouts, the named <code>grid-template-areas</code> + separate <code>grid-template-rows</code> and <code>grid-template-columns</code> is the most readable approach. The combined <code>grid-template</code> shorthand shines for tightly-coupled layout definitions where the row/column/area relationship is the focus &mdash; like complex magazine layouts or templated page frames.</p>
'''
