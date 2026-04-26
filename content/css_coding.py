"""Detailed answers for CSS Coding questions."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p>Use the <code>background-color</code> property &mdash; or the <code>background</code> shorthand:</p>
<pre><code>&lt;div class="box"&gt;Hello&lt;/div&gt;

&lt;style&gt;
  .box {
    background-color: lightblue;
    padding: 1em;
  }

  /* Shorthand also works */
  .box-alt {
    background: #ff6b35;
  }
&lt;/style&gt;</code></pre>
<p><strong>Color value formats:</strong></p>
<table>
  <tr><th>Format</th><th>Example</th></tr>
  <tr><td>Named</td><td><code>red</code>, <code>tomato</code>, <code>navy</code></td></tr>
  <tr><td>Hex</td><td><code>#0066cc</code></td></tr>
  <tr><td>RGB(A)</td><td><code>rgb(255 107 53 / 0.5)</code></td></tr>
  <tr><td>HSL</td><td><code>hsl(15 100% 60%)</code></td></tr>
  <tr><td>OKLCH (modern)</td><td><code>oklch(0.7 0.2 30)</code></td></tr>
</table>
<p><strong>Multiple targeted backgrounds</strong> &mdash; for design systems, define color tokens with CSS variables:</p>
<pre><code>:root {
  --bg-primary: #0066cc;
  --bg-warning: #ff6b35;
  --bg-success: #28a745;
}

.alert-info  { background: var(--bg-primary); }
.alert-warn  { background: var(--bg-warning); }
.alert-good  { background: var(--bg-success); }</code></pre>
<p>For semi-transparent backgrounds (overlays, glass effects), use RGBA or the modern <code>rgb(255 107 53 / 0.5)</code> syntax. The page beneath shows through &mdash; useful for hero overlays and dialog backdrops.</p>
'''

ANSWERS[2] = r'''
<p>Flexbox makes centering both axes a 3-line job &mdash; the canonical solution:</p>
<pre><code>&lt;div class="parent"&gt;
  &lt;div class="child"&gt;Centered!&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent {
    display: flex;
    justify-content: center;     /* horizontal */
    align-items: center;         /* vertical */
    min-height: 100vh;            /* take full viewport height */
  }
  .child {
    padding: 2em;
    background: lightblue;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><code>display: flex</code> &mdash; turns the parent into a flex container.</li>
  <li><code>justify-content</code> &mdash; aligns along the main axis (horizontal by default).</li>
  <li><code>align-items</code> &mdash; aligns along the cross axis (vertical by default).</li>
</ul>
<p><strong>Modern shorthand</strong> &mdash; the <code>place-items</code> property combines both:</p>
<pre><code>.parent {
  display: flex;
  place-items: center;          /* shorthand for align + justify */
  min-height: 100vh;
}</code></pre>
<p><strong>Grid alternative</strong> &mdash; same result, different syntax:</p>
<pre><code>.parent {
  display: grid;
  place-items: center;
  min-height: 100vh;
}</code></pre>
<p>Both work for any element size or count. This pattern replaces decades of margin: auto, transform translate, table-cell, and other centering hacks. <strong>Modern best practice</strong>: pick Flexbox for single-item centering, Grid for layout-grid-with-centered-items.</p>
'''

ANSWERS[3] = r'''
<p>Use the <code>border-radius</code> property &mdash; one rule, four corners:</p>
<pre><code>&lt;div class="box"&gt;Rounded&lt;/div&gt;

&lt;style&gt;
  .box {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 1em;
  }
&lt;/style&gt;</code></pre>
<p><strong>Asymmetric corners</strong> &mdash; specify each corner individually:</p>
<pre><code>/* clockwise: top-left, top-right, bottom-right, bottom-left */
.tab    { border-radius: 8px 8px 0 0; }     /* rounded top only */
.bubble { border-radius: 20px 20px 20px 0; } /* speech bubble */
.leaf   { border-radius: 50% 0; }            /* leaf shape */</code></pre>
<p><strong>Common shapes:</strong></p>
<table>
  <tr><th>Shape</th><th>border-radius</th></tr>
  <tr><td>Slight rounding</td><td><code>4px</code> &ndash; <code>8px</code></td></tr>
  <tr><td>Pronounced</td><td><code>12px</code> &ndash; <code>20px</code></td></tr>
  <tr><td>Pill (full vertical curve)</td><td><code>999px</code></td></tr>
  <tr><td>Circle (square element)</td><td><code>50%</code></td></tr>
</table>
<pre><code>.pill {
  border-radius: 999px;
  padding: 0.4em 1.2em;
  background: #0066cc;
  color: white;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;            /* perfect circle */
  object-fit: cover;
}</code></pre>
<p><strong>Elliptical corners</strong> &mdash; with a slash:</p>
<pre><code>.ellipse { border-radius: 50% / 25%; }   /* horizontal/vertical radii */</code></pre>
<p><code>border-radius</code> works on any element &mdash; divs, buttons, images, even inline elements. Combine with <code>overflow: hidden</code> to clip nested content (like images) to the rounded shape.</p>
'''

ANSWERS[4] = r'''
<p>Use <code>box-shadow</code>: <em>offset-x offset-y blur-radius color</em> (with optional spread):</p>
<pre><code>&lt;div class="card"&gt;Card with shadow&lt;/div&gt;

&lt;style&gt;
  .card {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 1.5em;
    border-radius: 8px;
    background: white;
  }
&lt;/style&gt;</code></pre>
<p><strong>Anatomy of <code>box-shadow</code>:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td>offset-x</td><td>Horizontal shift (positive = right)</td></tr>
  <tr><td>offset-y</td><td>Vertical shift (positive = down)</td></tr>
  <tr><td>blur-radius</td><td>How blurry (higher = softer)</td></tr>
  <tr><td>spread (optional)</td><td>Expand or shrink the shadow</td></tr>
  <tr><td>color</td><td>Often semi-transparent</td></tr>
  <tr><td><code>inset</code> (optional)</td><td>Inner shadow instead of outer</td></tr>
</table>
<p><strong>Elevation system</strong> &mdash; layered shadows for realistic depth (Material Design pattern):</p>
<pre><code>.elevation-1 { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24); }
.elevation-2 { box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23); }
.elevation-3 { box-shadow: 0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23); }</code></pre>
<p><strong>Inner shadow</strong> &mdash; pressed/inset look:</p>
<pre><code>.input { box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1); }</code></pre>
<p>Use semi-transparent colors so shadows blend with any background. Subtle shadows (alpha 0.05-0.15) feel modern; heavy ones feel dated.</p>
'''

ANSWERS[5] = r'''
<p>Use the <code>font-size</code> property:</p>
<pre><code>&lt;p&gt;Sample paragraph text.&lt;/p&gt;

&lt;style&gt;
  p {
    font-size: 18px;
  }
&lt;/style&gt;</code></pre>
<p><strong>Different units serve different purposes:</strong></p>
<table>
  <tr><th>Unit</th><th>Example</th><th>When to use</th></tr>
  <tr><td><code>px</code></td><td><code>18px</code></td><td>Precise control; ignored by user font preferences</td></tr>
  <tr><td><code>rem</code></td><td><code>1.125rem</code></td><td>Recommended &mdash; scales with root font-size</td></tr>
  <tr><td><code>em</code></td><td><code>1.125em</code></td><td>Relative to parent font-size (compounds)</td></tr>
  <tr><td><code>%</code></td><td><code>112.5%</code></td><td>Percentage of parent</td></tr>
  <tr><td><code>vw</code></td><td><code>2vw</code></td><td>Fluid &mdash; scales with viewport width</td></tr>
</table>
<p><strong>Why <code>rem</code> is preferred:</strong> users can override the browser&rsquo;s default font size for accessibility. Setting <code>font-size: 18px</code> ignores their preference; <code>1.125rem</code> respects it (assuming 16px default = 18px).</p>
<p><strong>Fluid typography with <code>clamp()</code></strong> &mdash; scales smoothly between min and max:</p>
<pre><code>p {
  font-size: clamp(1rem, 0.5rem + 1vw, 1.25rem);
  /* min 16px, scales with viewport, max 20px */
}

h1 {
  font-size: clamp(2rem, 5vw, 4rem);
  /* mobile: 2rem, desktop: 4rem, smooth in between */
}</code></pre>
<p><code>clamp()</code> eliminates the need for media queries on typography &mdash; one rule scales fluidly across all viewport sizes.</p>
'''

ANSWERS[6] = r'''
<p>CSS gradients are background images &mdash; use <code>linear-gradient()</code> for directional or <code>radial-gradient()</code> for circular:</p>
<pre><code>&lt;div class="box1"&gt;Linear&lt;/div&gt;
&lt;div class="box2"&gt;Radial&lt;/div&gt;

&lt;style&gt;
  .box1 {
    background: linear-gradient(45deg, #0066cc, #ff6b35);
    /* angle, color1, color2 */
    height: 200px;
  }

  .box2 {
    background: radial-gradient(circle, white, lightblue);
    height: 200px;
  }
&lt;/style&gt;</code></pre>
<p><strong>Direction options for linear:</strong></p>
<table>
  <tr><th>Direction</th><th>Effect</th></tr>
  <tr><td><code>to right</code></td><td>Left to right</td></tr>
  <tr><td><code>to bottom</code> (default)</td><td>Top to bottom</td></tr>
  <tr><td><code>to bottom right</code></td><td>Diagonal</td></tr>
  <tr><td><code>45deg</code></td><td>Custom angle</td></tr>
</table>
<p><strong>Multiple color stops</strong> &mdash; specify positions:</p>
<pre><code>.rainbow {
  background: linear-gradient(
    to right,
    red 0%,
    orange 16%,
    yellow 33%,
    green 50%,
    blue 67%,
    indigo 83%,
    violet 100%
  );
}</code></pre>
<p><strong>Conic gradient</strong> &mdash; rotates around a point (perfect for pie charts):</p>
<pre><code>.pie {
  background: conic-gradient(red 0% 25%, yellow 25% 50%, green 50% 100%);
  border-radius: 50%;
  width: 200px;
  height: 200px;
}</code></pre>
<p><strong>Hero overlay pattern</strong> &mdash; layer a dark gradient over an image for legible text:</p>
<pre><code>.hero {
  background:
    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url("hero.jpg") center / cover;
}</code></pre>
'''

ANSWERS[7] = r'''
<p>Use <code>font-weight: bold</code> &mdash; or a numeric value (100-900):</p>
<pre><code>&lt;p class="bold"&gt;Bold text&lt;/p&gt;
&lt;p class="bolder"&gt;Bolder text&lt;/p&gt;

&lt;style&gt;
  .bold   { font-weight: bold; }     /* equivalent to 700 */
  .bolder { font-weight: 900; }      /* extra bold */
&lt;/style&gt;</code></pre>
<p><strong>Numeric vs keyword values:</strong></p>
<table>
  <tr><th>Number</th><th>Keyword</th></tr>
  <tr><td>100</td><td>thin</td></tr>
  <tr><td>300</td><td>light</td></tr>
  <tr><td>400</td><td>normal (default)</td></tr>
  <tr><td>500</td><td>medium</td></tr>
  <tr><td>700</td><td>bold</td></tr>
  <tr><td>900</td><td>black / extra-bold</td></tr>
</table>
<p><strong>Caveat:</strong> the available weights depend on the font. Most fonts only ship 400 (regular) and 700 (bold). If you set <code>font-weight: 300</code> on a font without that weight, the browser falls back to the closest available.</p>
<p><strong>Variable fonts</strong> (Inter, Roboto Flex, Outfit) support every weight from 100-900 smoothly:</p>
<pre><code>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&amp;display=swap');

body { font-family: 'Inter', sans-serif; }
.subtle { font-weight: 250; }      /* fine-grained values */
.heavy  { font-weight: 850; }</code></pre>
<p><strong>Semantic alternative:</strong> use <code>&lt;strong&gt;</code> or <code>&lt;b&gt;</code> in HTML &mdash; browsers render them bold by default and screen readers may emphasize <code>&lt;strong&gt;</code> in the audio. Use <code>font-weight</code> in CSS for purely visual emphasis without semantic meaning.</p>
'''

ANSWERS[8] = r'''
<p>The canonical responsive grid: <code>auto-fit</code> + <code>minmax()</code> &mdash; columns reflow without media queries:</p>
<pre><code>&lt;section class="grid"&gt;
  &lt;article&gt;Card 1&lt;/article&gt;
  &lt;article&gt;Card 2&lt;/article&gt;
  &lt;article&gt;Card 3&lt;/article&gt;
  &lt;article&gt;Card 4&lt;/article&gt;
  &lt;article&gt;Card 5&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
  }
  .grid article {
    padding: 1.5em;
    background: white;
    border: 1px solid #eee;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it adapts to any viewport:</strong></p>
<ul>
  <li><strong>Wide screen (1200px+)</strong> &mdash; 4-5 columns side-by-side.</li>
  <li><strong>Tablet (768px)</strong> &mdash; 3 columns, then 2.</li>
  <li><strong>Phone (400px)</strong> &mdash; 1 column.</li>
</ul>
<p><strong>The <code>auto-fit</code> + <code>minmax</code> formula:</strong></p>
<table>
  <tr><th>Part</th><th>Effect</th></tr>
  <tr><td><code>auto-fit</code></td><td>Fit as many columns as possible</td></tr>
  <tr><td><code>minmax(250px, 1fr)</code></td><td>Each column at least 250px; share extra space equally</td></tr>
  <tr><td><code>gap: 1.5rem</code></td><td>Consistent spacing</td></tr>
</table>
<p><strong>auto-fit vs auto-fill:</strong> with few items, <code>auto-fit</code> stretches them to fill; <code>auto-fill</code> keeps them at min size with empty tracks. Use <code>auto-fit</code> for galleries; <code>auto-fill</code> for fixed-grid dashboards.</p>
<p>This single rule replaces a dozen media queries &mdash; the most powerful CSS Grid pattern in 2026.</p>
'''

ANSWERS[9] = r'''
<p>Use the <code>padding</code> property &mdash; controls internal spacing between content and border:</p>
<pre><code>&lt;div class="card"&gt;Padded content&lt;/div&gt;

&lt;style&gt;
  .card {
    padding: 1em;                    /* all sides */
    border: 1px solid #ccc;
    background: white;
  }
&lt;/style&gt;</code></pre>
<p><strong>Shorthand syntax &mdash; clockwise from top:</strong></p>
<table>
  <tr><th>Syntax</th><th>Sides affected</th></tr>
  <tr><td><code>padding: 10px</code></td><td>All four sides</td></tr>
  <tr><td><code>padding: 10px 20px</code></td><td>Top/bottom 10, left/right 20</td></tr>
  <tr><td><code>padding: 10px 20px 30px</code></td><td>Top, left/right, bottom</td></tr>
  <tr><td><code>padding: 10px 20px 30px 40px</code></td><td>Top, right, bottom, left (clockwise)</td></tr>
</table>
<p><strong>Individual sides</strong>:</p>
<pre><code>.card {
  padding-top: 1em;
  padding-right: 2em;
  padding-bottom: 1em;
  padding-left: 2em;
}</code></pre>
<p><strong>Logical properties</strong> (modern, RTL-friendly):</p>
<pre><code>.card {
  padding-block: 1em;       /* top + bottom */
  padding-inline: 2em;      /* left + right (or reversed in RTL) */
}</code></pre>
<p><strong>Important: <code>box-sizing</code></strong> &mdash; padding adds to width by default. With <code>box-sizing: border-box</code>, the width includes padding, simplifying layout:</p>
<pre><code>* { box-sizing: border-box; }   /* recommended global rule */</code></pre>
<p>Padding never collapses (unlike vertical margins) &mdash; predictable spacing every time.</p>
'''

ANSWERS[10] = r'''
<p>Use the <code>:hover</code> pseudo-class on the link:</p>
<pre><code>&lt;a href="/about"&gt;About us&lt;/a&gt;

&lt;style&gt;
  a {
    color: #0066cc;
    text-decoration: none;
    transition: color 0.2s;
  }
  a:hover {
    color: #cc0000;          /* red on hover */
    text-decoration: underline;
  }
&lt;/style&gt;</code></pre>
<p><strong>The <code>transition</code> property smooths the change</strong> &mdash; without it, the color jumps instantly. Apply transition to the base selector, not the hover state, so it works in both directions (entering and leaving).</p>
<p><strong>Link state pseudo-classes</strong> &mdash; full set, in correct order (LVHA):</p>
<pre><code>a:link    { color: blue; }       /* unvisited */
a:visited { color: purple; }      /* already visited */
a:hover   { color: red; }         /* mouse over */
a:active  { color: orange; }      /* being clicked */</code></pre>
<p>The order matters &mdash; later rules override earlier ones. Mnemonic: "<strong>L</strong>o<strong>V</strong>e <strong>HA</strong>te."</p>
<p><strong>Modern accessibility additions:</strong></p>
<pre><code>a:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}</code></pre>
<p><code>:focus-visible</code> shows focus rings only for keyboard users (not mouse clicks) &mdash; matches modern UX expectations while preserving accessibility.</p>
<p><strong>Touch devices</strong> have no hover &mdash; design hover effects as <em>enhancements</em>, not the only way to access info. Wrap hover-only effects in <code>@media (hover: hover)</code> if needed.</p>
'''

ANSWERS[11] = r'''
<p>Use the <code>width</code> property with a <code>%</code> value:</p>
<pre><code>&lt;div class="parent"&gt;
  &lt;div class="child"&gt;50% wide&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent {
    width: 600px;
    background: #eee;
    padding: 1em;
  }
  .child {
    width: 50%;              /* 50% of parent's width */
    background: #0066cc;
    color: white;
    padding: 1em;
  }
&lt;/style&gt;</code></pre>
<p>Result: child is 300px wide (50% of 600px), but <em>plus</em> its padding unless <code>box-sizing: border-box</code> is set.</p>
<p><strong>Width units overview:</strong></p>
<table>
  <tr><th>Unit</th><th>Reference</th></tr>
  <tr><td><code>%</code></td><td>Parent&rsquo;s width</td></tr>
  <tr><td><code>vw</code></td><td>Viewport width (1vw = 1%)</td></tr>
  <tr><td><code>px</code></td><td>Absolute pixels</td></tr>
  <tr><td><code>em</code> / <code>rem</code></td><td>Font-size based</td></tr>
  <tr><td><code>auto</code></td><td>Content-based</td></tr>
  <tr><td><code>fit-content</code></td><td>As wide as content needs</td></tr>
</table>
<p><strong>Constraints with min/max:</strong></p>
<pre><code>.flexible {
  width: 100%;
  max-width: 800px;          /* never wider than 800px */
  min-width: 320px;          /* never narrower than 320px */
}</code></pre>
<p><strong>Common pattern: centered content with max-width:</strong></p>
<pre><code>.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;            /* center horizontally */
  padding: 0 1rem;
}</code></pre>
<p>Best practice: combine percentage widths with max-width constraints &mdash; full-width on small screens, capped on large ones.</p>
'''

ANSWERS[12] = r'''
<p>Three different ways &mdash; each with different effects on layout and accessibility:</p>
<pre><code>&lt;div class="hide-display"&gt;Removed entirely&lt;/div&gt;
&lt;div class="hide-visibility"&gt;Invisible but takes space&lt;/div&gt;
&lt;div class="hide-opacity"&gt;Invisible but interactive&lt;/div&gt;

&lt;style&gt;
  .hide-display    { display: none; }       /* removed from layout */
  .hide-visibility { visibility: hidden; }  /* invisible, space remains */
  .hide-opacity    { opacity: 0; }           /* invisible, still interactive */
&lt;/style&gt;</code></pre>
<p><strong>Comparison:</strong></p>
<table>
  <tr><th>Method</th><th>Visible</th><th>Takes space</th><th>Screen reader</th><th>Click-through</th></tr>
  <tr><td><code>display: none</code></td><td>No</td><td>No</td><td>Hidden</td><td>N/A</td></tr>
  <tr><td><code>visibility: hidden</code></td><td>No</td><td>Yes</td><td>Hidden</td><td>No</td></tr>
  <tr><td><code>opacity: 0</code></td><td>No</td><td>Yes</td><td>Read</td><td>Yes</td></tr>
  <tr><td>HTML <code>hidden</code> attr</td><td>No</td><td>No</td><td>Hidden</td><td>N/A</td></tr>
</table>
<p><strong>Visually hidden but accessible to screen readers</strong> &mdash; the <code>.sr-only</code> pattern:</p>
<pre><code>.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}</code></pre>
<p>Use this for skip links, icon button labels, and other content that&rsquo;s redundant for sighted users but essential for assistive tech.</p>
<p><strong>Pick the right tool:</strong></p>
<ul>
  <li><strong>Remove entirely</strong> &rarr; <code>display: none</code></li>
  <li><strong>Preserve space</strong> &rarr; <code>visibility: hidden</code></li>
  <li><strong>Fade animation</strong> &rarr; <code>opacity: 0</code> with transition</li>
</ul>
'''

ANSWERS[13] = r'''
<p>Two CSS rules make any image fully responsive:</p>
<pre><code>&lt;img src="hero.jpg" alt="Hero" width="1200" height="600"&gt;

&lt;style&gt;
  img {
    max-width: 100%;
    height: auto;
  }
&lt;/style&gt;</code></pre>
<p><strong>What each rule does:</strong></p>
<ul>
  <li><code>max-width: 100%</code> &mdash; image never overflows its container.</li>
  <li><code>height: auto</code> &mdash; preserves the natural aspect ratio as width changes.</li>
</ul>
<p><strong>Apply globally</strong> &mdash; for all images, videos, iframes:</p>
<pre><code>img, video, iframe {
  max-width: 100%;
  height: auto;
}</code></pre>
<p><strong>Critical: include <code>width</code> and <code>height</code> attributes on the HTML</strong>. The browser uses them to reserve layout space, preventing the page from jumping as images load (CLS, Cumulative Layout Shift). The CSS still makes them responsive at runtime.</p>
<p><strong>Object-fit for cropping</strong> &mdash; when you need a specific aspect ratio:</p>
<pre><code>.thumbnail {
  width: 100%;
  height: 200px;
  object-fit: cover;       /* crops to fill, preserves aspect */
}

.contained {
  width: 100%;
  height: 200px;
  object-fit: contain;     /* fits entirely, may letterbox */
}</code></pre>
<p><strong>Modern responsive images with srcset</strong> &mdash; serve smaller images to phones:</p>
<pre><code>&lt;img
  src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1600.jpg 1600w"
  sizes="(max-width: 600px) 100vw, 50vw"
  alt="Hero"&gt;</code></pre>
<p>The browser picks the best size for the current viewport &mdash; saving bandwidth on mobile.</p>
'''

ANSWERS[14] = r'''
<p>Use <code>@keyframes</code> to define an animation, then apply it with the <code>animation</code> property:</p>
<pre><code>&lt;div class="pulse"&gt;Watch me change&lt;/div&gt;

&lt;style&gt;
  @keyframes color-pulse {
    0%   { background: #0066cc; }
    50%  { background: #ff6b35; }
    100% { background: #0066cc; }
  }

  .pulse {
    width: 200px;
    height: 100px;
    animation: color-pulse 2s infinite;
    /* name duration iteration-count */
  }
&lt;/style&gt;</code></pre>
<p><strong>Animation properties</strong>:</p>
<table>
  <tr><th>Property</th><th>What it controls</th></tr>
  <tr><td><code>animation-name</code></td><td>Which keyframes to use</td></tr>
  <tr><td><code>animation-duration</code></td><td>How long one cycle takes</td></tr>
  <tr><td><code>animation-iteration-count</code></td><td>Number of repeats (or <code>infinite</code>)</td></tr>
  <tr><td><code>animation-timing-function</code></td><td><code>linear</code>, <code>ease-in-out</code>, <code>cubic-bezier()</code></td></tr>
  <tr><td><code>animation-delay</code></td><td>Wait before starting</td></tr>
  <tr><td><code>animation-direction</code></td><td><code>normal</code>, <code>reverse</code>, <code>alternate</code></td></tr>
  <tr><td><code>animation-fill-mode</code></td><td><code>forwards</code> keeps end state</td></tr>
</table>
<p><strong>Shorthand syntax:</strong></p>
<pre><code>.pulse {
  animation: color-pulse 2s ease-in-out infinite alternate;
  /* name duration timing iteration direction */
}</code></pre>
<p><strong>Respect reduced-motion preference</strong> for accessibility:</p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  .pulse { animation: none; }
}</code></pre>
<p>Some users get nausea or vertigo from animations. Always honor their preference.</p>
'''

ANSWERS[15] = r'''
<p>Use the <code>text-align</code> property with the value <code>center</code>:</p>
<pre><code>&lt;p class="centered"&gt;This text is centered.&lt;/p&gt;
&lt;h1 class="centered"&gt;Page Title&lt;/h1&gt;

&lt;style&gt;
  .centered {
    text-align: center;
  }
&lt;/style&gt;</code></pre>
<p><strong>All <code>text-align</code> values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>left</code></td><td>Aligned to left (default for LTR languages)</td></tr>
  <tr><td><code>right</code></td><td>Aligned to right</td></tr>
  <tr><td><code>center</code></td><td>Centered</td></tr>
  <tr><td><code>justify</code></td><td>Stretched to fill, with even spacing</td></tr>
  <tr><td><code>start</code></td><td>Logical start (LTR = left, RTL = right)</td></tr>
  <tr><td><code>end</code></td><td>Logical end (LTR = right, RTL = left)</td></tr>
</table>
<p><strong>Modern logical values</strong> for international layouts:</p>
<pre><code>.heading {
  text-align: start;        /* left in English, right in Arabic */
}</code></pre>
<p><strong>Note: <code>text-align</code> works on inline content inside a block</strong> &mdash; text, links, inline images, and inline-block elements:</p>
<pre><code>&lt;div class="centered"&gt;
  &lt;span&gt;Centered text&lt;/span&gt;
  &lt;img src="icon.png" alt=""&gt;       &lt;!-- centered too --&gt;
  &lt;a href="#"&gt;link&lt;/a&gt;                   &lt;!-- centered --&gt;
&lt;/div&gt;</code></pre>
<p><strong>For centering block-level elements (like a div within another div), use:</strong></p>
<pre><code>.box { margin: 0 auto; width: 300px; }
/* or */
.parent { display: flex; justify-content: center; }</code></pre>
<p><code>text-align</code> is for inline content; Flexbox/Grid is for blocks.</p>
'''

ANSWERS[16] = r'''
<p>Use <code>position: fixed</code> with <code>top: 0</code> for a header that always stays at the top of the viewport:</p>
<pre><code>&lt;header class="fixed-header"&gt;
  &lt;a href="/"&gt;Logo&lt;/a&gt;
  &lt;nav&gt;
    &lt;a href="/"&gt;Home&lt;/a&gt;
    &lt;a href="/about"&gt;About&lt;/a&gt;
    &lt;a href="/contact"&gt;Contact&lt;/a&gt;
  &lt;/nav&gt;
&lt;/header&gt;

&lt;main&gt;
  &lt;article&gt;Page content here...&lt;/article&gt;
&lt;/main&gt;

&lt;style&gt;
  .fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;

    background: white;
    padding: 1em;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  /* Critical: offset the main content so it isn't hidden under header */
  main {
    padding-top: 70px;
  }
&lt;/style&gt;</code></pre>
<p><strong>Critical pattern: offset content below the header.</strong> Without <code>padding-top</code> on <code>&lt;main&gt;</code>, the first chunk of content hides behind the fixed header. Match the padding to the header&rsquo;s height.</p>
<p><strong>Sticky alternative</strong> &mdash; <code>position: sticky</code> scrolls naturally with the page, then sticks at the top:</p>
<pre><code>.sticky-header {
  position: sticky;
  top: 0;
  z-index: 100;
}

/* No padding-top needed on main — sticky takes natural space */</code></pre>
<p>Sticky is often preferred over fixed because:</p>
<ul>
  <li>No content offset needed.</li>
  <li>Header takes its natural space initially.</li>
  <li>Cleaner integration with existing layouts.</li>
</ul>
<p>Use fixed only when the header must <em>always</em> be visible (like an in-app toolbar). Use sticky for site headers that should disappear when scrolled to top.</p>
'''

ANSWERS[17] = r'''
<p>Use the <code>border</code> shorthand: <em>width style color</em>:</p>
<pre><code>&lt;div class="bordered"&gt;Content with border&lt;/div&gt;

&lt;style&gt;
  .bordered {
    border: 2px solid #0066cc;
    padding: 1em;
  }
&lt;/style&gt;</code></pre>
<p><strong>Border style options:</strong></p>
<table>
  <tr><th>Style</th><th>Visual</th></tr>
  <tr><td><code>solid</code></td><td>Continuous line (most common)</td></tr>
  <tr><td><code>dashed</code></td><td>Dashes</td></tr>
  <tr><td><code>dotted</code></td><td>Dots</td></tr>
  <tr><td><code>double</code></td><td>Two parallel lines</td></tr>
  <tr><td><code>groove</code> / <code>ridge</code> / <code>inset</code> / <code>outset</code></td><td>3D bevel effects (rarely used)</td></tr>
  <tr><td><code>none</code></td><td>No border (default)</td></tr>
</table>
<p><strong>Per-side borders</strong> &mdash; control each independently:</p>
<pre><code>.tab {
  border-top: 3px solid blue;
  border-right: none;
  border-bottom: 1px solid #ddd;
  border-left: none;
}

/* Shorthand for opposing sides */
.box {
  border-block: 1px solid;       /* top + bottom */
  border-inline: 2px dashed;     /* left + right */
}</code></pre>
<p><strong>Combine with border-radius for rounded shapes:</strong></p>
<pre><code>.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5em;
}</code></pre>
<p><strong>Outline alternative</strong> &mdash; <code>outline</code> draws outside the border, doesn&rsquo;t affect layout:</p>
<pre><code>.focused { outline: 2px solid blue; outline-offset: 2px; }</code></pre>
<p>Use <code>outline</code> for focus indicators &mdash; it doesn&rsquo;t shift layout when toggled.</p>
'''

ANSWERS[18] = r'''
<p>Use the <code>transition</code> property to animate property changes &mdash; especially for hover and focus states:</p>
<pre><code>&lt;a class="link"&gt;Hover me&lt;/a&gt;
&lt;button class="btn"&gt;Click me&lt;/button&gt;

&lt;style&gt;
  .link {
    color: #0066cc;
    text-decoration: none;
    transition: color 0.3s;
  }
  .link:hover {
    color: #ff6b35;
  }

  .btn {
    background: #0066cc;
    color: white;
    padding: 0.5em 1em;
    border: none;
    border-radius: 4px;
    transition: all 0.2s ease;
  }
  .btn:hover {
    background: #004999;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
&lt;/style&gt;</code></pre>
<p><strong>Transition syntax</strong>: <em>property duration timing-function delay</em></p>
<table>
  <tr><th>Part</th><th>Examples</th></tr>
  <tr><td>property</td><td><code>color</code>, <code>background</code>, <code>all</code>, <code>opacity</code></td></tr>
  <tr><td>duration</td><td><code>0.2s</code>, <code>200ms</code></td></tr>
  <tr><td>timing-function</td><td><code>ease</code>, <code>linear</code>, <code>ease-in-out</code>, <code>cubic-bezier(...)</code></td></tr>
  <tr><td>delay</td><td><code>0.1s</code> (optional)</td></tr>
</table>
<p><strong>Apply transition on the base selector, not <code>:hover</code></strong> &mdash; this way it works in both directions (entering and leaving the hover state).</p>
<p><strong>Multiple properties</strong> &mdash; comma-separate:</p>
<pre><code>.btn {
  transition:
    background 0.2s ease,
    transform 0.3s ease,
    box-shadow 0.3s ease;
}</code></pre>
<p>Different timing for each property creates more polished, layered animations. Avoid <code>transition: all</code> in production &mdash; it can animate unintended properties.</p>
'''

ANSWERS[19] = r'''
<p>Use the <code>cursor: pointer</code> property:</p>
<pre><code>&lt;button class="btn"&gt;Click me&lt;/button&gt;
&lt;div class="clickable"&gt;Custom button&lt;/div&gt;

&lt;style&gt;
  .btn {
    cursor: pointer;          /* hand cursor on hover */
    padding: 0.5em 1em;
    background: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
  }

  /* Make any element appear clickable */
  .clickable {
    cursor: pointer;
    padding: 1em;
    background: #f0f0f0;
  }
&lt;/style&gt;</code></pre>
<p><strong>Most useful cursor values:</strong></p>
<table>
  <tr><th>Value</th><th>Cursor shape</th><th>Use for</th></tr>
  <tr><td><code>default</code></td><td>Standard arrow</td><td>Default state</td></tr>
  <tr><td><code>pointer</code></td><td>Hand</td><td>Clickable elements</td></tr>
  <tr><td><code>text</code></td><td>I-beam</td><td>Text inputs</td></tr>
  <tr><td><code>not-allowed</code></td><td>Circle with slash</td><td>Disabled elements</td></tr>
  <tr><td><code>wait</code></td><td>Hourglass</td><td>Loading states</td></tr>
  <tr><td><code>help</code></td><td>Question mark</td><td>Tooltip available</td></tr>
  <tr><td><code>move</code></td><td>4-direction arrow</td><td>Draggable</td></tr>
  <tr><td><code>grab</code> / <code>grabbing</code></td><td>Open / closed hand</td><td>Drag affordance</td></tr>
</table>
<p><strong>Disabled state</strong> &mdash; combine cursor with opacity:</p>
<pre><code>.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}</code></pre>
<p><strong>Native elements already have <code>cursor: pointer</code></strong> &mdash; <code>&lt;a href&gt;</code> and most form elements. Add it to non-native clickable elements (divs, custom components) so users know they&rsquo;re interactive.</p>
<p>Don&rsquo;t use <code>cursor: pointer</code> on plain text or non-interactive elements &mdash; users expect it to mean "click me."</p>
'''

ANSWERS[20] = r'''
<p>Use the <code>text-shadow</code> property &mdash; same syntax as <code>box-shadow</code> but applies to text glyphs:</p>
<pre><code>&lt;h1 class="hero-title"&gt;Welcome&lt;/h1&gt;

&lt;style&gt;
  .hero-title {
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    /* offset-x offset-y blur color */
    font-size: 4em;
  }
&lt;/style&gt;</code></pre>
<p><strong>Anatomy:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td>offset-x</td><td>Horizontal shift</td></tr>
  <tr><td>offset-y</td><td>Vertical shift</td></tr>
  <tr><td>blur-radius</td><td>How blurry (0 = sharp, higher = softer)</td></tr>
  <tr><td>color</td><td>Often semi-transparent</td></tr>
</table>
<p><strong>Common patterns:</strong></p>
<pre><code>/* Subtle drop shadow for legibility */
.subtle {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Hard offset shadow (retro) */
.retro {
  text-shadow: 4px 4px 0 #ff6b35;
}

/* Glowing text */
.glow {
  text-shadow:
    0 0 5px #ff6b35,
    0 0 10px #ff6b35,
    0 0 20px #ff6b35;
}

/* 3D extruded text — multiple layered shadows */
.three-d {
  text-shadow:
    1px 1px 0 #ccc,
    2px 2px 0 #999,
    3px 3px 0 #666,
    4px 4px 0 #333;
}</code></pre>
<p><strong>Common use case:</strong> hero text over a busy background image &mdash; a slight dark shadow significantly improves legibility:</p>
<pre><code>.hero-text {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}</code></pre>
<p>Use sparingly &mdash; over-shadowed text looks dated. The most professional usage is subtle shadows that aid legibility without drawing attention.</p>
'''

ANSWERS[21] = r'''
<p>Combine <code>width: 100%</code> with <code>max-width</code> and <code>height: auto</code>:</p>
<pre><code>&lt;img src="banner.jpg"
     alt="Banner"
     width="1600" height="500"
     class="full-width"&gt;

&lt;style&gt;
  .full-width {
    width: 100%;             /* fill container */
    height: auto;             /* preserve aspect ratio */
    max-width: 100%;          /* never overflow */
    display: block;            /* removes inline whitespace below */
  }
&lt;/style&gt;</code></pre>
<p><strong>Why each property matters:</strong></p>
<ul>
  <li><code>width: 100%</code> &mdash; fills the parent container width.</li>
  <li><code>height: auto</code> &mdash; preserves the natural aspect ratio.</li>
  <li><code>display: block</code> &mdash; removes the small bottom whitespace inline images have.</li>
  <li><code>max-width: 100%</code> &mdash; safety net to prevent overflow.</li>
</ul>
<p><strong>Always include <code>width</code> and <code>height</code> attributes</strong> on the <code>&lt;img&gt;</code> tag. The browser uses them to reserve layout space, preventing content from jumping as the image loads.</p>
<p><strong>Combined with <code>object-fit</code> for cropping:</strong></p>
<pre><code>.banner {
  width: 100%;
  height: 400px;             /* fixed height */
  object-fit: cover;          /* crop to fill, preserve aspect */
}</code></pre>
<p>This makes the image fill a fixed-height container regardless of original dimensions &mdash; perfect for hero banners.</p>
<p><strong>Modern responsive images</strong> &mdash; serve different sizes based on viewport:</p>
<pre><code>&lt;img
  src="banner-800.jpg"
  srcset="banner-400.jpg 400w, banner-800.jpg 800w, banner-1600.jpg 1600w"
  sizes="100vw"
  alt="Banner"&gt;</code></pre>
<p>Phones download the 400px version; desktops get the 1600px version &mdash; saving bandwidth without sacrificing quality.</p>
'''

ANSWERS[22] = r'''
<p>Use the <code>::first-letter</code> pseudo-element &mdash; perfect for "drop cap" magazine-style typography:</p>
<pre><code>&lt;p class="article"&gt;In the beginning, there was just plain text...&lt;/p&gt;

&lt;style&gt;
  .article::first-letter {
    font-size: 3em;
    font-weight: bold;
    float: left;                /* text wraps around */
    line-height: 1;
    margin: 0 0.1em 0 0;
    color: #ff6b35;
    font-family: Georgia, serif;
  }
&lt;/style&gt;</code></pre>
<p><strong>Pseudo-elements use double colon</strong> (<code>::</code>) to distinguish them from pseudo-classes (single colon, like <code>:hover</code>). Both work, but <code>::</code> is the modern standard.</p>
<p><strong>Common pseudo-elements:</strong></p>
<table>
  <tr><th>Pseudo-element</th><th>Targets</th></tr>
  <tr><td><code>::first-letter</code></td><td>First letter of block content</td></tr>
  <tr><td><code>::first-line</code></td><td>First line of block content</td></tr>
  <tr><td><code>::before</code> / <code>::after</code></td><td>Generated content</td></tr>
  <tr><td><code>::placeholder</code></td><td>Form input placeholder</td></tr>
  <tr><td><code>::selection</code></td><td>User-selected text</td></tr>
  <tr><td><code>::marker</code></td><td>List bullets/numbers</td></tr>
</table>
<p><strong>Restrictions on <code>::first-letter</code>:</strong></p>
<ul>
  <li>Only the literal first letter (and any leading punctuation/quotation marks).</li>
  <li>Limited properties accepted: font, color, background, padding, margin, border, line-height, float.</li>
  <li>Doesn&rsquo;t apply to inline elements &mdash; the parent must be block-level.</li>
</ul>
<p><strong>Drop cap on first paragraph only:</strong></p>
<pre><code>article p:first-of-type::first-letter {
  font-size: 4em;
  float: left;
  line-height: 0.85;
  margin: 0.1em 0.1em 0 0;
  color: #c00;
}</code></pre>
<p>Combine <code>:first-of-type</code> with <code>::first-letter</code> so only the article&rsquo;s first paragraph gets the drop cap.</p>
'''

ANSWERS[23] = r'''
<p>Use Flexbox with <code>min-height: 100vh</code> &mdash; the footer naturally pushes to the bottom regardless of content length:</p>
<pre><code>&lt;body&gt;
  &lt;header&gt;Site Header&lt;/header&gt;
  &lt;main&gt;
    &lt;p&gt;Page content...&lt;/p&gt;
  &lt;/main&gt;
  &lt;footer&gt;Site Footer&lt;/footer&gt;
&lt;/body&gt;

&lt;style&gt;
  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  main {
    flex: 1;                   /* grows to fill remaining space */
  }
  footer {
    background: #2c3e50;
    color: white;
    padding: 1.5em;
    text-align: center;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><code>min-height: 100vh</code> &mdash; body is at least viewport height (more if content is taller).</li>
  <li><code>display: flex; flex-direction: column</code> &mdash; stacks header, main, footer vertically.</li>
  <li><code>flex: 1</code> on main &mdash; main grows to fill any extra space, pushing footer down.</li>
</ul>
<p>Result: short content &mdash; footer at bottom of viewport. Long content &mdash; footer below the content. Either way, no content gets cut off and no awkward gap appears.</p>
<p><strong>Grid alternative</strong> &mdash; equally clean:</p>
<pre><code>body {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
  /* header (auto), main (1fr fills), footer (auto) */
}</code></pre>
<p><strong>Modern viewport unit</strong> &mdash; <code>100dvh</code> accounts for mobile browser chrome (which can show/hide):</p>
<pre><code>body {
  min-height: 100dvh;          /* dynamic viewport height */
}</code></pre>
<p>Smoother on iOS Safari &mdash; the footer doesn&rsquo;t jump as the URL bar collapses.</p>
'''

ANSWERS[24] = r'''
<p>Flexbox makes responsive nav trivial &mdash; horizontal on desktop, stacked on mobile:</p>
<pre><code>&lt;nav class="main-nav"&gt;
  &lt;a href="/" class="logo"&gt;Logo&lt;/a&gt;
  &lt;ul class="nav-links"&gt;
    &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/services"&gt;Services&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
  &lt;/ul&gt;
&lt;/nav&gt;

&lt;style&gt;
  .main-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1em 2em;
    background: white;
    border-bottom: 1px solid #eee;
  }
  .nav-links {
    display: flex;
    gap: 2em;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .nav-links a {
    color: #333;
    text-decoration: none;
    transition: color 0.2s;
  }
  .nav-links a:hover {
    color: #0066cc;
  }

  /* Mobile: stack vertically */
  @media (max-width: 600px) {
    .main-nav {
      flex-direction: column;
      gap: 1em;
    }
    .nav-links {
      flex-direction: column;
      gap: 0.5em;
      width: 100%;
    }
    .nav-links a {
      display: block;
      padding: 0.5em;
      border-radius: 4px;
      background: #f8f9fa;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Layout breakdown:</strong></p>
<ul>
  <li>Outer flex with <code>justify-content: space-between</code> pushes logo left, nav links right.</li>
  <li>Inner flex on the link list lays them out horizontally with gaps.</li>
  <li>Media query collapses to vertical on phones.</li>
</ul>
<p>For a hamburger-style mobile menu, add a checkbox toggle (CSS-only) or a button + JavaScript for full ARIA accessibility. Libraries like Headless UI handle the complete pattern with keyboard navigation, focus traps, and ARIA states.</p>
'''

ANSWERS[25] = r'''
<p>Use the <code>opacity</code> property &mdash; values from <code>0</code> (invisible) to <code>1</code> (fully visible):</p>
<pre><code>&lt;div class="full"&gt;Fully visible&lt;/div&gt;
&lt;div class="half"&gt;Half opacity&lt;/div&gt;
&lt;div class="faded"&gt;Mostly faded&lt;/div&gt;

&lt;style&gt;
  .full  { opacity: 1; }      /* default — fully visible */
  .half  { opacity: 0.5; }    /* 50% — semi-transparent */
  .faded { opacity: 0.2; }    /* 20% — barely visible */
&lt;/style&gt;</code></pre>
<p><strong>How opacity differs from alpha colors:</strong></p>
<table>
  <tr><th></th><th><code>opacity: 0.5</code></th><th><code>rgba(0,0,0,0.5)</code></th></tr>
  <tr><td>Affects</td><td>Element AND children</td><td>Only the property using it</td></tr>
  <tr><td>Use for</td><td>Whole-element fading</td><td>Just background or color</td></tr>
</table>
<pre><code>.card {
  background: rgba(0, 0, 0, 0.5);   /* only background is semi-transparent */
  color: white;                       /* text stays opaque */
}

.fading-card {
  opacity: 0.5;                       /* whole card AND children fade */
}</code></pre>
<p><strong>Animated fade in/out</strong> &mdash; combine with <code>transition</code>:</p>
<pre><code>.fade {
  opacity: 0;
  transition: opacity 0.3s;
}
.fade.show {
  opacity: 1;
}</code></pre>
<p>Toggle the <code>.show</code> class via JavaScript to fade an element in or out smoothly.</p>
<p><strong>Disabled state pattern</strong>:</p>
<pre><code>.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;       /* block clicks */
}</code></pre>
<p>Don&rsquo;t use opacity to hide content from screen readers &mdash; <code>opacity: 0</code> still leaves the element accessible. Use <code>display: none</code> or <code>aria-hidden</code> if you need to hide it semantically.</p>
'''

ANSWERS[26] = r'''
<p>Use <code>border-radius: 50%</code> on a square element:</p>
<pre><code>&lt;div class="circle"&gt;&lt;/div&gt;
&lt;img src="avatar.jpg" alt="" class="avatar"&gt;

&lt;style&gt;
  .circle {
    width: 100px;
    height: 100px;             /* width = height for perfect circle */
    border-radius: 50%;
    background: #0066cc;
  }

  .avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;          /* crop image to circle */
  }
&lt;/style&gt;</code></pre>
<p><strong>Critical: width must equal height.</strong> If width and height differ, you get an ellipse, not a circle.</p>
<p><strong>Aspect-ratio</strong> &mdash; modern way to enforce square shape:</p>
<pre><code>.circle {
  width: 100px;
  aspect-ratio: 1;             /* enforces square */
  border-radius: 50%;
  background: #0066cc;
}</code></pre>
<p>This way, height auto-matches width &mdash; useful when width is responsive (like <code>width: 20%</code>).</p>
<p><strong>Common circle patterns:</strong></p>
<pre><code>/* Avatar with border */
.avatar {
  width: 60px;
  aspect-ratio: 1;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  object-fit: cover;
}

/* Status indicator */
.status-dot {
  width: 12px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #28a745;        /* green for online */
  display: inline-block;
}

/* Floating action button */
.fab {
  width: 56px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #ff6b35;
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}</code></pre>
<p><strong>For ovals/ellipses</strong> &mdash; use different width and height with <code>border-radius: 50%</code>:</p>
<pre><code>.oval { width: 200px; height: 100px; border-radius: 50%; }</code></pre>
'''

ANSWERS[27] = r'''
<p>Three methods for gradient borders &mdash; the modern <code>background-clip</code> technique works best with rounded corners:</p>
<p><strong>Method 1: <code>border-image</code></strong></p>
<pre><code>.gradient-border {
  border: 4px solid;
  border-image: linear-gradient(45deg, #0066cc, #ff6b35) 1;
  padding: 1em;
}</code></pre>
<p>The trailing <code>1</code> sets the slice value &mdash; without it, the gradient won&rsquo;t apply correctly. Limitation: doesn&rsquo;t work with <code>border-radius</code>.</p>
<p><strong>Method 2: background-clip with rounded corners</strong> (preferred):</p>
<pre><code>.gradient-border {
  padding: 1em;
  border-radius: 8px;
  background:
    linear-gradient(white, white) padding-box,
    linear-gradient(45deg, #0066cc, #ff6b35) border-box;
  border: 4px solid transparent;
}</code></pre>
<p>How it works: white solid background fills the inner area (padding-box); gradient fills the border area (border-box); the transparent border lets the gradient show through.</p>
<p><strong>Method 3: ::before pseudo-element</strong></p>
<pre><code>.gradient-border-3 {
  position: relative;
  padding: 1em;
  background: white;
  border-radius: 8px;
}
.gradient-border-3::before {
  content: "";
  position: absolute;
  inset: -4px;
  z-index: -1;
  border-radius: inherit;
  background: linear-gradient(45deg, #0066cc, #ff6b35);
}</code></pre>
<p><strong>Animated gradient border</strong> &mdash; method 2 with shifting background:</p>
<pre><code>.animated {
  background:
    linear-gradient(white, white) padding-box,
    linear-gradient(45deg, #0066cc, #ff6b35, #0066cc) border-box;
  background-size: 200% 200%;
  animation: shift 3s linear infinite;
}
@keyframes shift {
  to { background-position: 200% 0; }
}</code></pre>
<p>Method 2 is the gold standard &mdash; works with rounded corners, supports animation, browser-friendly.</p>
'''

ANSWERS[28] = r'''
<p>Media queries apply CSS conditionally based on viewport size, orientation, color scheme, etc:</p>
<pre><code>/* Mobile-first: default styles for mobile, then enhance */
.container {
  padding: 1em;
  display: block;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 2em;
    display: grid;
    grid-template-columns: 1fr 250px;
    gap: 2em;
  }
}

/* Desktop and up */
@media (min-width: 1200px) {
  .container {
    max-width: 1400px;
    margin: 0 auto;
    grid-template-columns: 1fr 300px;
  }
}</code></pre>
<p><strong>Common breakpoints:</strong></p>
<table>
  <tr><th>Range</th><th>Device</th></tr>
  <tr><td>0&ndash;599px</td><td>Mobile</td></tr>
  <tr><td>600&ndash;899px</td><td>Tablet portrait</td></tr>
  <tr><td>900&ndash;1199px</td><td>Tablet landscape, small laptop</td></tr>
  <tr><td>1200&ndash;1599px</td><td>Desktop</td></tr>
  <tr><td>1600px+</td><td>Large monitor</td></tr>
</table>
<p><strong>Useful media features beyond width:</strong></p>
<pre><code>/* User prefers dark mode */
@media (prefers-color-scheme: dark) {
  :root { --bg: #1a1a1a; --fg: white; }
}

/* User prefers reduced motion */
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}

/* High-DPI screens */
@media (min-resolution: 2dppx) {
  .logo { background-image: url(logo@2x.png); }
}

/* Hover-capable devices */
@media (hover: hover) {
  .card:hover { transform: scale(1.05); }
}

/* Print */
@media print {
  nav, footer { display: none; }
  body { font-size: 12pt; }
}</code></pre>
<p><strong>Don&rsquo;t forget the viewport meta tag</strong> &mdash; without it, mobile renders desktop-sized:</p>
<pre><code>&lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;</code></pre>
'''

ANSWERS[29] = r'''
<p>Use <code>background-image</code> &mdash; with <code>background-size</code>, <code>background-position</code>, and <code>background-repeat</code> for control:</p>
<pre><code>&lt;section class="hero"&gt;Hero content&lt;/section&gt;

&lt;style&gt;
  .hero {
    background-image: url("/images/hero.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    min-height: 400px;
    color: white;
    padding: 2em;
  }
&lt;/style&gt;</code></pre>
<p><strong>Key sub-properties:</strong></p>
<table>
  <tr><th>Property</th><th>Common values</th></tr>
  <tr><td><code>background-size</code></td><td><code>cover</code>, <code>contain</code>, <code>auto</code>, <code>200px</code>, <code>50%</code></td></tr>
  <tr><td><code>background-position</code></td><td><code>center</code>, <code>top right</code>, <code>50% 50%</code></td></tr>
  <tr><td><code>background-repeat</code></td><td><code>no-repeat</code>, <code>repeat</code>, <code>repeat-x</code></td></tr>
  <tr><td><code>background-attachment</code></td><td><code>scroll</code> (default), <code>fixed</code> (parallax)</td></tr>
</table>
<p><strong>Shorthand</strong> &mdash; combine in one rule:</p>
<pre><code>.hero {
  background: url("/hero.jpg") center / cover no-repeat;
  /* image position/size repeat */
}</code></pre>
<p><strong>Multiple backgrounds</strong> stack with comma separation. The first is on top:</p>
<pre><code>.hero {
  background:
    linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
    url("/hero.jpg") center / cover;
}</code></pre>
<p>This stacks a dark overlay over the image &mdash; a common pattern for legible text over busy photos.</p>
<p><strong>Common patterns:</strong></p>
<pre><code>/* Tiled pattern */
.pattern { background: url(tile.png) repeat; }

/* Fixed parallax */
.parallax { background: url(img.jpg) center / cover fixed; }

/* CSS gradient instead of image */
.gradient {
  background: linear-gradient(135deg, #0066cc, #ff6b35);
}</code></pre>
'''

ANSWERS[30] = r'''
<p>Define an animation with <code>@keyframes</code>, then apply it to an element with <code>animation</code>:</p>
<pre><code>&lt;div class="bouncer"&gt;Watch me bounce&lt;/div&gt;

&lt;style&gt;
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-30px); }
  }

  .bouncer {
    animation: bounce 1s ease-in-out infinite;
    /* name duration timing iteration */

    width: 100px;
    height: 100px;
    background: #0066cc;
  }
&lt;/style&gt;</code></pre>
<p><strong>Keyframe percentage values:</strong></p>
<table>
  <tr><th>Percentage</th><th>Means</th></tr>
  <tr><td><code>0%</code> or <code>from</code></td><td>Start of animation</td></tr>
  <tr><td><code>50%</code></td><td>Halfway through</td></tr>
  <tr><td><code>100%</code> or <code>to</code></td><td>End of animation</td></tr>
</table>
<p><strong>Multi-stage example:</strong></p>
<pre><code>@keyframes spin-and-fade {
  0%   { transform: rotate(0); opacity: 0; }
  25%  { transform: rotate(90deg); opacity: 1; }
  75%  { transform: rotate(270deg); opacity: 1; }
  100% { transform: rotate(360deg); opacity: 0; }
}

.element {
  animation: spin-and-fade 2s ease-in-out;
}</code></pre>
<p><strong>Animation properties:</strong></p>
<table>
  <tr><th>Property</th><th>Default</th><th>Example</th></tr>
  <tr><td><code>animation-duration</code></td><td>0s</td><td><code>2s</code>, <code>500ms</code></td></tr>
  <tr><td><code>animation-timing-function</code></td><td><code>ease</code></td><td><code>linear</code>, <code>ease-in-out</code></td></tr>
  <tr><td><code>animation-delay</code></td><td>0s</td><td><code>0.5s</code></td></tr>
  <tr><td><code>animation-iteration-count</code></td><td>1</td><td><code>infinite</code>, <code>3</code></td></tr>
  <tr><td><code>animation-direction</code></td><td><code>normal</code></td><td><code>alternate</code>, <code>reverse</code></td></tr>
  <tr><td><code>animation-fill-mode</code></td><td><code>none</code></td><td><code>forwards</code>, <code>backwards</code></td></tr>
</table>
<p><strong>Always respect reduced-motion preference:</strong></p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  .bouncer { animation: none; }
}</code></pre>
'''

ANSWERS[31] = r'''
<p>Use the <code>font-family</code> property with a font stack &mdash; comma-separated fallbacks:</p>
<pre><code>&lt;p class="serif"&gt;Serif paragraph&lt;/p&gt;
&lt;p class="sans"&gt;Sans-serif paragraph&lt;/p&gt;
&lt;p class="mono"&gt;Monospace paragraph&lt;/p&gt;

&lt;style&gt;
  .serif { font-family: Georgia, "Times New Roman", serif; }
  .sans  { font-family: "Inter", -apple-system, "Segoe UI", Roboto, sans-serif; }
  .mono  { font-family: "JetBrains Mono", Consolas, Monaco, monospace; }
&lt;/style&gt;</code></pre>
<p><strong>The browser tries each font in order</strong>; if not available, falls back to the next. The list <em>must</em> end with a generic family (<code>serif</code>, <code>sans-serif</code>, <code>monospace</code>) as the final safety net.</p>
<p><strong>Quote font names with spaces:</strong></p>
<pre><code>font-family: "Helvetica Neue", "Times New Roman", sans-serif;</code></pre>
<p><strong>Loading custom fonts via <code>@font-face</code>:</strong></p>
<pre><code>@font-face {
  font-family: "MyFont";
  src: url("/fonts/myfont.woff2") format("woff2"),
       url("/fonts/myfont.woff") format("woff");
  font-weight: 400;
  font-style: normal;
  font-display: swap;        /* show fallback while loading */
}

body { font-family: "MyFont", sans-serif; }</code></pre>
<p><strong>Loading from Google Fonts:</strong></p>
<pre><code>&lt;link rel="preconnect" href="https://fonts.googleapis.com"&gt;
&lt;link rel="preconnect" href="https://fonts.gstatic.com" crossorigin&gt;
&lt;link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;display=swap" rel="stylesheet"&gt;</code></pre>
<p><strong>System font stack</strong> &mdash; modern best practice; uses the OS&rsquo;s native UI font with no download:</p>
<pre><code>font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;</code></pre>
<p>Result: San Francisco on Apple, Segoe UI on Windows, Roboto on Android &mdash; native look, zero font-loading penalty.</p>
'''

ANSWERS[32] = r'''
<p>Set <code>display: grid</code> on a container and define columns/rows:</p>
<pre><code>&lt;div class="grid"&gt;
  &lt;div&gt;1&lt;/div&gt;
  &lt;div&gt;2&lt;/div&gt;
  &lt;div&gt;3&lt;/div&gt;
  &lt;div&gt;4&lt;/div&gt;
  &lt;div&gt;5&lt;/div&gt;
  &lt;div&gt;6&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  .grid &gt; div {
    background: #f0f8ff;
    padding: 1em;
    text-align: center;
  }
&lt;/style&gt;</code></pre>
<p><strong>Defining columns and rows:</strong></p>
<pre><code>/* 3 equal columns */
grid-template-columns: 1fr 1fr 1fr;

/* Shorthand */
grid-template-columns: repeat(3, 1fr);

/* Mixed sizes */
grid-template-columns: 200px 1fr 200px;

/* Responsive */
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));

/* Set rows too */
grid-template-rows: 100px 200px;
grid-template-rows: auto 1fr auto;   /* header / main / footer */</code></pre>
<p><strong>The <code>fr</code> unit</strong> represents a fraction of available space. <code>1fr 2fr 1fr</code> = three columns; the middle one gets twice the space.</p>
<p><strong>Gap between items:</strong></p>
<pre><code>.grid {
  display: grid;
  gap: 1rem;             /* both row + column */
  row-gap: 2rem;          /* override row gap */
  column-gap: 1rem;       /* override column gap */
}</code></pre>
<p><strong>Spanning multiple cells:</strong></p>
<pre><code>.featured {
  grid-column: span 2;     /* takes 2 columns */
  grid-row: span 2;         /* takes 2 rows */
}</code></pre>
<p>Grid is the most powerful layout system in CSS &mdash; replaces float-based and most flexbox-based layouts for 2D arrangements.</p>
'''

ANSWERS[33] = r'''
<p>Apply a gradient as the button&rsquo;s background:</p>
<pre><code>&lt;button class="btn-gradient"&gt;Sign Up&lt;/button&gt;

&lt;style&gt;
  .btn-gradient {
    background: linear-gradient(135deg, #0066cc, #ff6b35);
    color: white;
    border: none;
    padding: 0.8em 2em;
    border-radius: 6px;
    font-size: 1em;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .btn-gradient:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .btn-gradient:active {
    transform: translateY(0);
  }
&lt;/style&gt;</code></pre>
<p><strong>Gradient direction options:</strong></p>
<table>
  <tr><th>Syntax</th><th>Direction</th></tr>
  <tr><td><code>linear-gradient(to right, ...)</code></td><td>Left to right</td></tr>
  <tr><td><code>linear-gradient(135deg, ...)</code></td><td>Diagonal</td></tr>
  <tr><td><code>linear-gradient(to bottom, ...)</code></td><td>Top to bottom (default)</td></tr>
</table>
<p><strong>Animated gradient on hover</strong> &mdash; shifts the gradient on interaction:</p>
<pre><code>.btn-shifted {
  background: linear-gradient(135deg, #0066cc, #ff6b35, #0066cc);
  background-size: 200% 200%;
  background-position: 0% 50%;
  transition: background-position 0.5s;
  /* ...other styles */
}
.btn-shifted:hover {
  background-position: 100% 50%;
}</code></pre>
<p><strong>Multi-stop gradient</strong> &mdash; for more sophisticated colors:</p>
<pre><code>.btn-fancy {
  background: linear-gradient(
    135deg,
    #667eea 0%,
    #764ba2 50%,
    #f093fb 100%
  );
}</code></pre>
<p>Gradient buttons feel modern when subtle and dated when over-the-top &mdash; aim for two harmonious colors with a gentle angle. Pair with a hover transform for tactile feedback.</p>
'''

ANSWERS[34] = r'''
<p>Use the <code>:hover</code> pseudo-class to change properties when the mouse is over an element:</p>
<pre><code>&lt;button class="btn"&gt;Hover me&lt;/button&gt;
&lt;a href="#" class="link"&gt;Hover link&lt;/a&gt;

&lt;style&gt;
  .btn {
    background: #0066cc;
    color: white;
    padding: 0.5em 1em;
    border: none;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
  }
  .btn:hover {
    background: #ff6b35;          /* color change on hover */
  }

  .link {
    color: #0066cc;
    text-decoration: none;
    transition: color 0.3s;
  }
  .link:hover {
    color: #cc0000;
  }
&lt;/style&gt;</code></pre>
<p><strong>Always include a <code>transition</code></strong> for smooth color changes &mdash; without it, the change is instant and jarring. Apply it to the base selector, not <code>:hover</code>, so it works in both directions.</p>
<p><strong>Background color hover patterns:</strong></p>
<pre><code>/* Lighten on hover */
.card { background: #0066cc; }
.card:hover { background: #4d94e0; }

/* Darken on hover */
.btn { background: #0066cc; }
.btn:hover { background: #004999; }

/* Use color-mix() for derived colors (modern) */
.btn { background: #0066cc; }
.btn:hover { background: color-mix(in srgb, #0066cc 80%, black); }</code></pre>
<p><strong>Hover effects on different elements within a parent:</strong></p>
<pre><code>.card:hover .title {
  color: #0066cc;          /* parent hovered */
}

.card:hover .image {
  transform: scale(1.05);
}</code></pre>
<p><strong>Touch device caveat:</strong> hover doesn&rsquo;t exist on touch &mdash; design hover effects as enhancements, not the only access path. Wrap with <code>@media (hover: hover)</code> if needed.</p>
'''

ANSWERS[35] = r'''
<p>Use Flexbox with <code>align-items: center</code> &mdash; the cleanest way to vertically center text inside a div:</p>
<pre><code>&lt;div class="vcenter"&gt;
  Vertically centered text
&lt;/div&gt;

&lt;style&gt;
  .vcenter {
    display: flex;
    align-items: center;          /* vertical alignment */
    /* justify-content: center; */ /* uncomment to also horizontally center */

    height: 200px;
    background: #f0f8ff;
    padding: 1em;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><code>display: flex</code> &mdash; container becomes a flex container.</li>
  <li><code>align-items: center</code> &mdash; aligns flex items along the cross axis (vertical when direction is row).</li>
  <li>The text is treated as one anonymous flex item that gets centered.</li>
</ul>
<p><strong>Both axes centered</strong> &mdash; the canonical pattern:</p>
<pre><code>.center-everything {
  display: flex;
  justify-content: center;       /* horizontal */
  align-items: center;            /* vertical */
  height: 200px;
}</code></pre>
<p><strong>Modern shorthand</strong> &mdash; <code>place-items</code> combines both:</p>
<pre><code>.center {
  display: flex;
  place-items: center;            /* shorthand for align-items + justify-items */
  height: 200px;
}</code></pre>
<p><strong>Other vertical centering techniques (less common):</strong></p>
<table>
  <tr><th>Technique</th><th>When to use</th></tr>
  <tr><td>Flex / Grid</td><td>Modern default &mdash; works everywhere</td></tr>
  <tr><td><code>line-height</code> = container height</td><td>Single line of text only</td></tr>
  <tr><td><code>display: table-cell + vertical-align: middle</code></td><td>Legacy fallback</td></tr>
  <tr><td>Position + transform translate</td><td>Absolutely positioned children</td></tr>
</table>
<p>Flexbox handles all the cases the older techniques covered, with cleaner syntax.</p>
'''

ANSWERS[36] = r'''
<p>Use the <code>::before</code> or <code>::after</code> pseudo-element with a <code>content</code> property &mdash; this generates extra content visually without adding it to the HTML:</p>
<pre><code>&lt;p class="quote"&gt;Imagination is more important than knowledge.&lt;/p&gt;

&lt;style&gt;
  .quote::before {
    content: "\201C";        /* opening curly quote */
    font-size: 2em;
    color: #0066cc;
    margin-right: 0.2em;
  }
  .quote::after {
    content: "\201D";        /* closing curly quote */
    font-size: 2em;
    color: #0066cc;
  }
&lt;/style&gt;</code></pre>
<p><strong>Common pseudo-elements:</strong></p>
<table>
  <tr><th>Pseudo-element</th><th>Purpose</th></tr>
  <tr><td><code>::before</code></td><td>Generated content before the element</td></tr>
  <tr><td><code>::after</code></td><td>Generated content after the element</td></tr>
  <tr><td><code>::first-letter</code></td><td>First letter of block text</td></tr>
  <tr><td><code>::first-line</code></td><td>First line of block text</td></tr>
  <tr><td><code>::placeholder</code></td><td>Form input placeholder text</td></tr>
  <tr><td><code>::selection</code></td><td>Text selected by the user</td></tr>
  <tr><td><code>::marker</code></td><td>List item bullets / numbers</td></tr>
</table>
<p><strong>Decorative example &mdash; underline that grows on hover:</strong></p>
<pre><code>a {
  position: relative;
  text-decoration: none;
}
a::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: currentColor;
  transition: width 0.3s;
}
a:hover::after {
  width: 100%;
}</code></pre>
<p><strong>Note:</strong> <code>::before</code> and <code>::after</code> require <code>content</code> &mdash; even an empty string <code>content: ""</code> &mdash; or they don&rsquo;t render. Pseudo-elements use double colons (<code>::</code>); the older single-colon syntax (<code>:before</code>) still works for backward compatibility but isn&rsquo;t preferred.</p>
'''

ANSWERS[37] = r'''
<p>A CSS-only tooltip uses <code>::after</code> with the <code>content</code> property and shows on hover:</p>
<pre><code>&lt;span class="tooltip" data-tooltip="More info here"&gt;
  Hover me
&lt;/span&gt;

&lt;style&gt;
  .tooltip {
    position: relative;
    border-bottom: 1px dotted #666;
    cursor: help;
  }
  .tooltip::after {
    content: attr(data-tooltip);     /* read from data attribute */
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-4px);
    background: #333;
    color: white;
    padding: 0.4em 0.7em;
    border-radius: 4px;
    font-size: 0.85em;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }
  .tooltip:hover::after,
  .tooltip:focus-visible::after {
    opacity: 1;
  }
&lt;/style&gt;</code></pre>
<p><strong>Key techniques:</strong></p>
<ul>
  <li><code>attr(data-tooltip)</code> &mdash; reads the tooltip text from the HTML data attribute, so each element can have unique text.</li>
  <li><code>position: relative</code> on the trigger + <code>position: absolute</code> on the tooltip &mdash; tooltip positions relative to its container.</li>
  <li><code>transform: translateX(-50%)</code> &mdash; centers the tooltip horizontally.</li>
  <li><code>opacity</code> + <code>transition</code> &mdash; smooth fade in/out.</li>
  <li><code>pointer-events: none</code> &mdash; tooltip itself is non-interactive.</li>
  <li><code>:focus-visible</code> trigger &mdash; ensures keyboard users can see tooltips too.</li>
</ul>
<p>For more sophisticated tooltips with auto-positioning around viewport edges, use the modern Popover API or libraries like Floating UI &mdash; but pure CSS handles the common cases cleanly with full accessibility for keyboard users.</p>
'''

ANSWERS[38] = r'''
<p>Use CSS Grid with two columns &mdash; the simplest form is a fixed sidebar + flexible main content area:</p>
<pre><code>&lt;div class="layout"&gt;
  &lt;aside&gt;Sidebar content&lt;/aside&gt;
  &lt;main&gt;Main content&lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: grid;
    grid-template-columns: 250px 1fr;    /* fixed sidebar, flexible main */
    gap: 2em;
    padding: 1em;
  }

  /* Mobile: stack to single column */
  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Equal-width two-column variant:</strong></p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;     /* two equal columns */
  gap: 2em;
}</code></pre>
<p><strong>Auto-fit responsive variant</strong> &mdash; columns reflow naturally:</p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2em;
}</code></pre>
<p>This pattern adapts: 2 columns when there&rsquo;s room, 1 column when the viewport narrows below 600px.</p>
<p><strong>Grid units explained:</strong></p>
<table>
  <tr><th>Unit</th><th>Meaning</th></tr>
  <tr><td><code>1fr</code></td><td>1 fraction of available space</td></tr>
  <tr><td><code>250px</code></td><td>Fixed pixel width</td></tr>
  <tr><td><code>minmax(300px, 1fr)</code></td><td>At least 300px, expand to share space</td></tr>
  <tr><td><code>auto</code></td><td>Sized to content</td></tr>
</table>
<p>Mix and match. For example, <code>200px 1fr 200px</code> creates fixed-fluid-fixed (sidebar, main, complementary).</p>
'''

ANSWERS[39] = r'''
<p>Use <code>text-align: justify</code> to align text along both edges, with extra spacing distributed within lines:</p>
<pre><code>&lt;p class="justified"&gt;
  This paragraph is justified, meaning the text aligns flush
  to both the left and right margins. Browsers add extra space
  between words to make every line span the full width.
&lt;/p&gt;

&lt;style&gt;
  .justified {
    text-align: justify;
    max-width: 600px;
  }
&lt;/style&gt;</code></pre>
<p><strong>All <code>text-align</code> values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>left</code></td><td>Aligned to left (default for LTR)</td></tr>
  <tr><td><code>right</code></td><td>Aligned to right</td></tr>
  <tr><td><code>center</code></td><td>Centered</td></tr>
  <tr><td><code>justify</code></td><td>Both edges flush; words spaced apart</td></tr>
  <tr><td><code>start</code> / <code>end</code></td><td>Logical (LTR or RTL aware)</td></tr>
</table>
<p><strong>Improving justified text quality:</strong></p>
<pre><code>.justified {
  text-align: justify;
  hyphens: auto;                    /* allow hyphenation at line breaks */
  word-spacing: -0.05em;            /* slight tightening */
}

/* Optional: avoid the last (typically short) line being justified */
.justified::after {
  content: "";
  display: inline-block;
  width: 100%;
}</code></pre>
<p><strong>When to use justify:</strong></p>
<ul>
  <li><strong>Print-style content</strong> &mdash; books, magazines, formal documents.</li>
  <li><strong>Wide columns</strong> &mdash; works best at 60+ characters per line.</li>
  <li><strong>Avoid for narrow columns</strong> &mdash; creates "rivers" of white space that hurt readability.</li>
</ul>
<p>Always pair with <code>hyphens: auto</code> and a sensible <code>lang</code> attribute on the document so the browser can break words at appropriate syllable boundaries.</p>
'''

ANSWERS[40] = r'''
<p>Use the <code>transition</code> property on the base state &mdash; CSS smoothly interpolates between values when properties change:</p>
<pre><code>&lt;button class="smooth"&gt;Hover me&lt;/button&gt;

&lt;style&gt;
  .smooth {
    background: #0066cc;
    color: white;
    padding: 0.5em 1em;
    border: none;
    cursor: pointer;
    transition: background 0.3s ease;       /* property duration easing */
  }
  .smooth:hover {
    background: #ff6b35;        /* color smoothly transitions */
  }
&lt;/style&gt;</code></pre>
<p><strong>Transition shorthand &mdash; <code>property duration easing delay</code>:</strong></p>
<pre><code>transition: background 0.3s ease;
transition: color 0.5s ease-in-out 0.1s;
transition: all 0.2s;             /* transition all properties */</code></pre>
<p><strong>Transitioning multiple properties:</strong></p>
<pre><code>.btn {
  background: #0066cc;
  color: white;
  transform: scale(1);
  transition: background 0.3s, transform 0.2s, box-shadow 0.2s;
}
.btn:hover {
  background: #ff6b35;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}</code></pre>
<p><strong>Easing functions</strong>:</p>
<table>
  <tr><th>Function</th><th>Behavior</th></tr>
  <tr><td><code>linear</code></td><td>Constant speed</td></tr>
  <tr><td><code>ease</code></td><td>Slow start, fast middle, slow end (default)</td></tr>
  <tr><td><code>ease-in</code></td><td>Slow start, fast end</td></tr>
  <tr><td><code>ease-out</code></td><td>Fast start, slow end</td></tr>
  <tr><td><code>ease-in-out</code></td><td>Slow start and end</td></tr>
  <tr><td><code>cubic-bezier(...)</code></td><td>Custom curve</td></tr>
</table>
<p>Apply <code>transition</code> to the base state, not the hover state &mdash; that way the animation works in both directions (hover in AND hover out). Most properties can be transitioned, but a few (like <code>display</code>) cannot animate smoothly.</p>
'''

ANSWERS[41] = r'''
<p>Use the <code>vh</code> (viewport height) unit &mdash; <code>1vh</code> equals 1% of the viewport height:</p>
<pre><code>&lt;section class="full-screen"&gt;
  Content fills the viewport
&lt;/section&gt;

&lt;style&gt;
  .full-screen {
    height: 100vh;          /* full viewport height */
    background: #0066cc;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
  }
&lt;/style&gt;</code></pre>
<p><strong>Mobile viewport gotcha:</strong> on mobile (especially iOS Safari), <code>100vh</code> includes the address bar height &mdash; so initial content extends below the visible area. Modern alternatives solve this:</p>
<table>
  <tr><th>Unit</th><th>Behavior</th></tr>
  <tr><td><code>vh</code></td><td>Viewport height (mobile: includes browser chrome)</td></tr>
  <tr><td><code>svh</code></td><td>Small viewport height (always smaller, no chrome)</td></tr>
  <tr><td><code>lvh</code></td><td>Large viewport height (always larger, with chrome)</td></tr>
  <tr><td><code>dvh</code></td><td>Dynamic viewport height (changes with chrome)</td></tr>
</table>
<pre><code>.hero {
  height: 100dvh;             /* recommended for mobile-friendly hero */
}</code></pre>
<p><strong>Other viewport units:</strong></p>
<pre><code>.responsive {
  width:  50vw;             /* 50% of viewport width */
  height: 100vh;            /* full viewport height */
  font-size: 5vw;           /* 5% of viewport width — fluid type */
  padding: 2vmin;           /* 2% of smaller dimension */
}</code></pre>
<p><strong>Common pattern: full-screen hero with content centered:</strong></p>
<pre><code>.hero {
  min-height: 100dvh;
  display: grid;
  place-items: center;
}</code></pre>
<p>Use <code>min-height</code> rather than <code>height</code> if content might exceed the viewport &mdash; otherwise content overflow could clip.</p>
'''

ANSWERS[42] = r'''
<p>Use <code>background-attachment: fixed</code> to keep the background image in place while the page scrolls past:</p>
<pre><code>&lt;section class="parallax"&gt;
  &lt;h1&gt;Welcome&lt;/h1&gt;
  &lt;p&gt;Scroll to see the parallax effect.&lt;/p&gt;
&lt;/section&gt;

&lt;style&gt;
  .parallax {
    background-image: url("/landscape.jpg");
    background-attachment: fixed;       /* doesn't scroll */
    background-size: cover;
    background-position: center;

    min-height: 100vh;
    color: white;
    padding: 2em;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><code>background-attachment: fixed</code> &mdash; image is positioned relative to the viewport, not the element.</li>
  <li>As the page scrolls, content moves but the background stays.</li>
  <li>Often called the "parallax" effect.</li>
</ul>
<p><strong>Performance warning:</strong> on mobile, fixed backgrounds cause severe scroll jank because the browser has to re-render the background on every scroll frame. Many sites disable it on small viewports:</p>
<pre><code>.parallax {
  background-attachment: fixed;
}

/* Disable on mobile for smooth scrolling */
@media (max-width: 768px) {
  .parallax {
    background-attachment: scroll;
  }
}</code></pre>
<p><strong>iOS Safari quirk:</strong> <code>background-attachment: fixed</code> historically didn&rsquo;t work on iOS at all &mdash; backgrounds scrolled with the page. Modern iOS partially supports it, but performance is still problematic. Test on real devices.</p>
<p><strong>Modern alternative for parallax</strong>: CSS <code>perspective</code> + <code>transform: translateZ()</code> for GPU-accelerated scroll effects:</p>
<pre><code>.parallax-modern {
  perspective: 1000px;
  height: 100vh;
}
.parallax-modern .layer {
  transform: translateZ(-300px) scale(1.3);
}</code></pre>
<p>This 3D transform approach is far smoother than <code>background-attachment</code> on mobile.</p>
'''

ANSWERS[43] = r'''
<p>Use <code>border-radius</code> on an <code>&lt;img&gt;</code> &mdash; same property that rounds box corners works for images:</p>
<pre><code>&lt;img src="photo.jpg" alt="" class="rounded"&gt;
&lt;img src="avatar.jpg" alt="" class="circle"&gt;
&lt;img src="card.jpg" alt="" class="rounded-top"&gt;

&lt;style&gt;
  .rounded {
    border-radius: 12px;        /* slight rounding */
  }
  .circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;          /* perfect circle if width == height */
    object-fit: cover;            /* crop, preserve aspect */
  }
  .rounded-top {
    border-radius: 12px 12px 0 0;   /* only top corners */
  }
&lt;/style&gt;</code></pre>
<p><strong>Border-radius values:</strong></p>
<table>
  <tr><th>Syntax</th><th>Result</th></tr>
  <tr><td><code>border-radius: 12px</code></td><td>All corners rounded equally</td></tr>
  <tr><td><code>border-radius: 12px 0</code></td><td>Top-left and bottom-right; others square</td></tr>
  <tr><td><code>border-radius: 12px 12px 0 0</code></td><td>Top corners only (clockwise from top-left)</td></tr>
  <tr><td><code>border-radius: 50%</code></td><td>Circle (if image is square)</td></tr>
  <tr><td><code>border-radius: 999px</code></td><td>Pill shape (very rounded)</td></tr>
</table>
<p><strong>Avatar pattern:</strong></p>
<pre><code>.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;            /* center-crop image to fit */
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}</code></pre>
<p><strong>Image card with rounded top corners:</strong></p>
<pre><code>.card {
  border-radius: 12px;
  overflow: hidden;             /* clip child image to rounded corners */
}
.card img {
  width: 100%;
  display: block;
}</code></pre>
<p>The <code>overflow: hidden</code> on the parent is essential &mdash; without it, the image extends past the rounded corners. <code>display: block</code> on the image removes the small inline-spacing gap below.</p>
'''

ANSWERS[44] = r'''
<p>Use <code>@keyframes</code> with <code>transform: translateX()</code> &mdash; the most performant way to move elements:</p>
<pre><code>&lt;div class="slider"&gt;Sliding right!&lt;/div&gt;

&lt;style&gt;
  .slider {
    width: 100px;
    padding: 1em;
    background: #0066cc;
    color: white;
    animation: slideRight 2s ease-in-out infinite;
  }

  @keyframes slideRight {
    from { transform: translateX(0); }
    to   { transform: translateX(300px); }
  }
&lt;/style&gt;</code></pre>
<p><strong>Animation shorthand:</strong> <code>name duration easing delay iteration-count direction fill-mode play-state</code></p>
<pre><code>animation: slideRight 2s ease-in-out;            /* once */
animation: slideRight 2s ease-in-out infinite;   /* repeat forever */
animation: slideRight 2s ease-in-out 0.5s 3;     /* delay 0.5s, repeat 3 times */
animation: slideRight 2s ease-in-out infinite alternate;  /* back and forth */</code></pre>
<p><strong>Multi-stop animation</strong> &mdash; using percentages:</p>
<pre><code>@keyframes slidePath {
  0%   { transform: translateX(0); }
  25%  { transform: translateX(150px); }
  50%  { transform: translateX(300px); }
  75%  { transform: translateX(150px); }
  100% { transform: translateX(0); }
}</code></pre>
<p><strong>Why <code>transform</code> not <code>left</code>?</strong> <code>transform</code> is GPU-accelerated &mdash; smooth at 60fps. Animating <code>left</code>, <code>right</code>, <code>top</code>, <code>bottom</code>, <code>width</code>, or <code>height</code> triggers expensive layout recalculation each frame and can cause visible stutter on slower devices.</p>
<p><strong>Properties that animate cheaply:</strong></p>
<table>
  <tr><th>Cheap (GPU)</th><th>Expensive (CPU layout)</th></tr>
  <tr><td><code>transform</code></td><td><code>left</code>, <code>top</code>, <code>width</code>, <code>height</code></td></tr>
  <tr><td><code>opacity</code></td><td><code>margin</code>, <code>padding</code></td></tr>
  <tr><td><code>filter</code></td><td><code>border-width</code></td></tr>
</table>
<p>Animate transform and opacity whenever possible; reserve other properties for one-off transitions.</p>
'''

ANSWERS[45] = r'''
<p>Combine <code>border-radius</code> with the button&rsquo;s other styles:</p>
<pre><code>&lt;button class="btn-rounded"&gt;Click me&lt;/button&gt;

&lt;style&gt;
  .btn-rounded {
    background: #0066cc;
    color: white;
    border: none;
    padding: 0.75em 1.5em;
    border-radius: 6px;            /* slight rounding */
    cursor: pointer;
    font-size: 1em;
    transition: background 0.2s;
  }
  .btn-rounded:hover {
    background: #004999;
  }
&lt;/style&gt;</code></pre>
<p><strong>Border-radius variations:</strong></p>
<pre><code>/* Slightly rounded corners */
.btn-soft { border-radius: 4px; }

/* More rounded */
.btn-medium { border-radius: 8px; }

/* Very rounded card-like */
.btn-large { border-radius: 16px; }

/* Pill-shaped (fully rounded sides) */
.btn-pill { border-radius: 999px; }

/* Just one corner */
.btn-tab {
  border-radius: 8px 8px 0 0;     /* only top corners */
}</code></pre>
<p><strong>Pill button</strong> with the <code>999px</code> trick &mdash; an unrealistically large value clips to the full half-height:</p>
<pre><code>.btn-pill {
  border-radius: 999px;
  padding: 0.5em 1.5em;
}</code></pre>
<p><strong>Group of buttons with shared rounding</strong> &mdash; only outer corners rounded:</p>
<pre><code>.btn-group .btn:first-child {
  border-radius: 6px 0 0 6px;     /* round left side */
}
.btn-group .btn:last-child {
  border-radius: 0 6px 6px 0;     /* round right side */
}
.btn-group .btn:not(:first-child):not(:last-child) {
  border-radius: 0;                /* middle buttons stay square */
}</code></pre>
<p>This pattern creates segmented button bars where buttons appear connected with rounded outer corners only.</p>
'''

ANSWERS[46] = r'''
<p>Flexbox creates a responsive image gallery where images wrap onto new rows as the viewport narrows:</p>
<pre><code>&lt;section class="gallery"&gt;
  &lt;img src="img1.jpg" alt=""&gt;
  &lt;img src="img2.jpg" alt=""&gt;
  &lt;img src="img3.jpg" alt=""&gt;
  &lt;img src="img4.jpg" alt=""&gt;
  &lt;img src="img5.jpg" alt=""&gt;
&lt;/section&gt;

&lt;style&gt;
  .gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5em;
    padding: 0.5em;
  }
  .gallery img {
    flex: 1 1 200px;          /* grow, shrink, basis */
    height: 200px;
    object-fit: cover;
    border-radius: 4px;
    transition: transform 0.2s;
  }
  .gallery img:hover {
    transform: scale(1.03);
  }
&lt;/style&gt;</code></pre>
<p><strong>The flex shorthand explained:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td><code>flex-grow: 1</code></td><td>Fill remaining space proportionally</td></tr>
  <tr><td><code>flex-shrink: 1</code></td><td>Shrink if needed (default)</td></tr>
  <tr><td><code>flex-basis: 200px</code></td><td>Preferred starting width</td></tr>
</table>
<p>Each image starts at 200px wide. If extra space exists, images grow equally to fill it. If there&rsquo;s less than 200px per image, they wrap to a new line.</p>
<p><strong>Maintain aspect ratio</strong>:</p>
<pre><code>.gallery img {
  flex: 1 1 200px;
  aspect-ratio: 1;             /* square thumbnails */
  object-fit: cover;
}</code></pre>
<p>Or for landscape:</p>
<pre><code>.gallery img {
  flex: 1 1 250px;
  aspect-ratio: 4 / 3;         /* 4:3 landscape */
  object-fit: cover;
}</code></pre>
<p><strong>Performance:</strong> add <code>loading="lazy"</code> to <code>&lt;img&gt;</code> tags below the fold so they only load when scrolled into view.</p>
'''

ANSWERS[47] = r'''
<p>Use the <code>filter</code> property to apply visual effects &mdash; blur, grayscale, brightness, hue-rotate, and more:</p>
<pre><code>&lt;img src="photo.jpg" alt="" class="vintage"&gt;

&lt;style&gt;
  .vintage {
    filter: sepia(0.5) contrast(1.2) brightness(0.95);
  }
&lt;/style&gt;</code></pre>
<p><strong>Available filter functions:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>blur(5px)</code></td><td>Gaussian blur</td></tr>
  <tr><td><code>brightness(0.5)</code></td><td>Darken or lighten (1 = original)</td></tr>
  <tr><td><code>contrast(2)</code></td><td>Adjust contrast</td></tr>
  <tr><td><code>grayscale(1)</code></td><td>Convert to grayscale (1 = full)</td></tr>
  <tr><td><code>hue-rotate(90deg)</code></td><td>Rotate hue around the color wheel</td></tr>
  <tr><td><code>invert(1)</code></td><td>Invert colors</td></tr>
  <tr><td><code>opacity(0.5)</code></td><td>Make semi-transparent</td></tr>
  <tr><td><code>saturate(2)</code></td><td>Adjust saturation</td></tr>
  <tr><td><code>sepia(1)</code></td><td>Sepia tone</td></tr>
  <tr><td><code>drop-shadow(2px 2px 5px black)</code></td><td>Shadow that follows alpha shape</td></tr>
</table>
<p><strong>Combining filters &mdash; chain in one declaration:</strong></p>
<pre><code>.image-effect {
  filter: blur(2px) brightness(1.2) saturate(1.5);
}</code></pre>
<p><strong>Common patterns:</strong></p>
<pre><code>/* Black & white photo gallery */
.bw-img { filter: grayscale(1); transition: filter 0.3s; }
.bw-img:hover { filter: grayscale(0); }

/* Disabled / loading state */
.disabled { filter: grayscale(0.7) brightness(0.9); }

/* Drop shadow on transparent PNG (like icon) */
.icon { filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); }

/* Backdrop filter (background blur) */
.glass {
  backdrop-filter: blur(10px) saturate(1.8);
  background: rgba(255, 255, 255, 0.5);
}</code></pre>
<p><strong>backdrop-filter</strong> applies the filter to what&rsquo;s behind the element &mdash; perfect for "frosted glass" effects on overlays and headers.</p>
'''

ANSWERS[48] = r'''
<p>Use <code>transform: rotate()</code> with an angle in degrees, radians, or turns:</p>
<pre><code>&lt;div class="badge"&gt;NEW!&lt;/div&gt;

&lt;style&gt;
  .badge {
    background: red;
    color: white;
    padding: 0.5em 1em;
    transform: rotate(-15deg);    /* rotated 15 degrees counter-clockwise */
  }
&lt;/style&gt;</code></pre>
<p><strong>Rotation units:</strong></p>
<table>
  <tr><th>Unit</th><th>Example</th></tr>
  <tr><td><code>deg</code> (degrees)</td><td><code>rotate(45deg)</code></td></tr>
  <tr><td><code>rad</code> (radians)</td><td><code>rotate(0.5rad)</code></td></tr>
  <tr><td><code>turn</code></td><td><code>rotate(0.25turn)</code> = 90deg</td></tr>
</table>
<p><strong>Other transform functions:</strong></p>
<pre><code>.element {
  transform: translateX(50px);          /* move right 50px */
  transform: scale(1.5);                 /* 150% larger */
  transform: skewX(10deg);               /* skew horizontally */
  transform: rotate(45deg) scale(2);     /* multiple, applied right-to-left */
}</code></pre>
<p><strong>Animated rotation</strong>:</p>
<pre><code>.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}</code></pre>
<p><strong>3D rotation</strong> with <code>rotateX</code> and <code>rotateY</code>:</p>
<pre><code>.flip {
  transition: transform 0.6s;
  transform-style: preserve-3d;
}
.flip:hover {
  transform: rotateY(180deg);   /* horizontal flip */
}</code></pre>
<p>Add <code>perspective: 1000px</code> on a parent to give 3D rotations real depth. Without it, the rotation looks flat (just an inversion).</p>
<p><strong>Transform-origin</strong> changes the rotation pivot point (default is center):</p>
<pre><code>.element {
  transform: rotate(45deg);
  transform-origin: top left;     /* rotate around top-left corner */
}</code></pre>
'''

ANSWERS[49] = r'''
<p>Use <code>line-height</code> to set the vertical space between lines of text:</p>
<pre><code>&lt;p class="readable"&gt;Multiple lines of text...&lt;/p&gt;

&lt;style&gt;
  .readable {
    line-height: 1.6;        /* 1.6 &times; the font size */
  }
&lt;/style&gt;</code></pre>
<p><strong>Common values:</strong></p>
<table>
  <tr><th>Value</th><th>Use case</th></tr>
  <tr><td><code>1.0</code></td><td>Tight (display headings)</td></tr>
  <tr><td><code>1.2</code></td><td>Default for headings</td></tr>
  <tr><td><code>1.5</code></td><td>Comfortable body text</td></tr>
  <tr><td><code>1.6&ndash;1.8</code></td><td>Long-form articles</td></tr>
  <tr><td><code>2</code></td><td>Loose, double-spaced</td></tr>
</table>
<p><strong>Best practice: use unitless values</strong> &mdash; they inherit correctly:</p>
<pre><code>body { line-height: 1.5; }
/* Each child computes line-height as multiplier &times; its own font-size */

h1 { font-size: 32px; }    /* line-height = 48px */
p  { font-size: 16px; }    /* line-height = 24px */</code></pre>
<p>If you used <code>line-height: 24px</code>, all elements would inherit the literal 24px regardless of their font size &mdash; usually wrong.</p>
<p><strong>Other unit options</strong>:</p>
<pre><code>p { line-height: 1.5; }      /* unitless multiplier (preferred) */
p { line-height: 24px; }     /* fixed pixels */
p { line-height: 1.5em; }    /* em-based */
p { line-height: 150%; }     /* percentage of font size */
p { line-height: normal; }   /* browser default (~1.2) */</code></pre>
<p><strong>Accessibility:</strong> WCAG recommends <strong>line-height of at least 1.5</strong> for body text to help users with cognitive disabilities and dyslexia. Tighter line-heights make text harder to scan; looser line-heights help with readability but should be balanced against vertical density.</p>
'''

ANSWERS[50] = r'''
<p>A responsive nav with dropdowns: horizontal on desktop, collapsing to vertical on mobile, with submenu dropdowns on hover or click:</p>
<pre><code>&lt;nav class="nav"&gt;
  &lt;a href="/"&gt;Home&lt;/a&gt;
  &lt;a href="/about"&gt;About&lt;/a&gt;
  &lt;div class="dropdown"&gt;
    &lt;a href="#"&gt;Services &#9662;&lt;/a&gt;
    &lt;ul class="dropdown-menu"&gt;
      &lt;li&gt;&lt;a href="/web"&gt;Web Design&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/dev"&gt;Development&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/seo"&gt;SEO&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
  &lt;/div&gt;
  &lt;a href="/contact"&gt;Contact&lt;/a&gt;
&lt;/nav&gt;

&lt;style&gt;
  .nav {
    display: flex;
    gap: 1.5em;
    padding: 1em;
    background: #f8f9fa;
  }
  .nav a {
    color: #333;
    text-decoration: none;
  }
  .dropdown {
    position: relative;
  }
  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0.5em 0;
    list-style: none;
    margin: 0;
    min-width: 180px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

    /* Hidden by default */
    opacity: 0;
    pointer-events: none;
    transform: translateY(-4px);
    transition: opacity 0.2s, transform 0.2s;
  }
  .dropdown:hover .dropdown-menu,
  .dropdown:focus-within .dropdown-menu {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0);
  }
  .dropdown-menu a {
    display: block;
    padding: 0.5em 1em;
  }
  .dropdown-menu a:hover {
    background: #f0f0f0;
  }

  /* Mobile: stack vertically */
  @media (max-width: 600px) {
    .nav { flex-direction: column; }
    .dropdown-menu { position: static; opacity: 1; pointer-events: auto; transform: none; }
  }
&lt;/style&gt;</code></pre>
<p><strong>Key techniques:</strong></p>
<ul>
  <li><code>:hover</code> + <code>:focus-within</code> &mdash; opens menu for both mouse and keyboard.</li>
  <li><code>opacity</code> + <code>pointer-events</code> &mdash; hide visually but allow smooth fade-in.</li>
  <li>Mobile: collapse dropdowns inline (no positioning).</li>
</ul>
<p>For a full production menu (arrow-key navigation, dismiss-outside-click), libraries like Radix Menu provide complete ARIA support out of the box.</p>
'''

ANSWERS[51] = r'''
<p>Use the <code>text-decoration</code> property &mdash; controls underline, line-through, overline, and decoration line style:</p>
<pre><code>&lt;a href="/" class="no-underline"&gt;No underline&lt;/a&gt;
&lt;a href="/" class="underline"&gt;Underlined&lt;/a&gt;
&lt;a href="/" class="dashed"&gt;Dashed underline&lt;/a&gt;
&lt;a href="/" class="strike"&gt;Struck through&lt;/a&gt;

&lt;style&gt;
  .no-underline { text-decoration: none; }
  .underline    { text-decoration: underline; }
  .dashed       { text-decoration: underline dashed #888; }
  .strike       { text-decoration: line-through; }
&lt;/style&gt;</code></pre>
<p><strong>Text-decoration shorthand:</strong> <code>line style color thickness</code></p>
<pre><code>a {
  text-decoration: underline wavy red 2px;
}</code></pre>
<p><strong>All values:</strong></p>
<table>
  <tr><th>Property</th><th>Values</th></tr>
  <tr><td><code>text-decoration-line</code></td><td><code>none</code>, <code>underline</code>, <code>overline</code>, <code>line-through</code></td></tr>
  <tr><td><code>text-decoration-style</code></td><td><code>solid</code>, <code>double</code>, <code>dotted</code>, <code>dashed</code>, <code>wavy</code></td></tr>
  <tr><td><code>text-decoration-color</code></td><td>Any color value</td></tr>
  <tr><td><code>text-decoration-thickness</code></td><td>Length, percentage, or <code>auto</code></td></tr>
  <tr><td><code>text-underline-offset</code></td><td>Distance from text baseline</td></tr>
</table>
<p><strong>Modern underline customization:</strong></p>
<pre><code>a {
  text-decoration: underline;
  text-decoration-color: #0066cc;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;        /* push underline lower */
}</code></pre>
<p><strong>Spell-check style</strong> &mdash; wavy red:</p>
<pre><code>.misspelled {
  text-decoration: underline wavy red;
}</code></pre>
<p><strong>Removing underlines</strong> &mdash; common for navigation links and buttons:</p>
<pre><code>a { text-decoration: none; }
a:hover { text-decoration: underline; }    /* show on hover only */</code></pre>
<p>Don&rsquo;t remove underlines from inline article links &mdash; users rely on them to identify clickable text. Reserve <code>text-decoration: none</code> for navigation, buttons, or styled link components.</p>
'''

ANSWERS[52] = r'''
<p>Animate the <code>opacity</code> property with <code>@keyframes</code>:</p>
<pre><code>&lt;div class="fade-loop"&gt;Fading in and out&lt;/div&gt;

&lt;style&gt;
  .fade-loop {
    animation: fade 2s ease-in-out infinite;
  }

  @keyframes fade {
    0%, 100% { opacity: 0; }
    50%      { opacity: 1; }
  }
&lt;/style&gt;</code></pre>
<p>The element fades from invisible (0%) to fully visible (50%) and back to invisible (100%) &mdash; on a 2-second loop.</p>
<p><strong>One-shot fade-in</strong> &mdash; appears and stays:</p>
<pre><code>.fade-in {
  animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}</code></pre>
<p><strong>Pulsing effect</strong> &mdash; combine opacity with scale for a heartbeat:</p>
<pre><code>.pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1;  transform: scale(1); }
  50%      { opacity: 0.5; transform: scale(1.05); }
}</code></pre>
<p><strong>Fade between states (cross-fade)</strong> &mdash; useful for toast notifications:</p>
<pre><code>.toast {
  animation: toastShow 4s ease-in-out forwards;
}
@keyframes toastShow {
  0%   { opacity: 0; transform: translateY(20px); }
  10%  { opacity: 1; transform: translateY(0); }
  90%  { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-20px); }
}</code></pre>
<p>The <code>forwards</code> fill mode keeps the final state after the animation ends. Without it, the element snaps back to opacity 0.</p>
<p><strong>Performance tip:</strong> animating <code>opacity</code> is GPU-accelerated and runs at 60fps even on low-end devices &mdash; one of the cheapest CSS animations.</p>
'''

ANSWERS[53] = r'''
<p>Use the <code>margin</code> property to add space outside an element&rsquo;s border:</p>
<pre><code>.spaced {
  margin: 1em;                     /* all sides equal */
  margin: 10px 20px;               /* vertical horizontal */
  margin: 10px 20px 30px;          /* top horizontal bottom */
  margin: 10px 20px 30px 40px;     /* top right bottom left (clockwise) */
}

/* Individual sides */
.fine-tune {
  margin-top:    10px;
  margin-right:  20px;
  margin-bottom: 30px;
  margin-left:   40px;
}</code></pre>
<p><strong>Centering with auto margins:</strong></p>
<pre><code>.centered {
  width: 600px;
  margin: 0 auto;          /* zero top/bottom, auto sides → centered horizontally */
}</code></pre>
<p><strong>Negative margins</strong> &mdash; pull elements toward each other:</p>
<pre><code>.overlap-up {
  margin-top: -20px;        /* pulls up by 20px */
}</code></pre>
<p><strong>Margin collapse</strong> &mdash; a common gotcha. Vertical margins between adjacent block elements <em>collapse</em> to the larger of the two values:</p>
<pre><code>p { margin: 30px 0; }       /* 30px top and bottom */

/* Two paragraphs in a row produce 30px between them, not 60px */</code></pre>
<p>Margin collapse only happens vertically and only between block siblings. Padding doesn&rsquo;t collapse.</p>
<p><strong>Logical properties</strong> for international layouts:</p>
<pre><code>.element {
  margin-block: 1em;          /* top and bottom (or right/left in vertical writing) */
  margin-inline: 2em;          /* left and right (or top/bottom in vertical writing) */
}</code></pre>
<p>Logical properties adapt automatically to right-to-left languages.</p>
'''

ANSWERS[54] = r'''
<p>Define a CSS variable with the <code>--</code> prefix on <code>:root</code>, then reference it with <code>var()</code>:</p>
<pre><code>:root {
  --primary-color: #0066cc;
  --bg-color: #f0f8ff;
}

.box {
  background-color: var(--bg-color);
  border: 2px solid var(--primary-color);
  padding: 1em;
}

.btn {
  background: var(--primary-color);
  color: white;
}</code></pre>
<p><strong>Why use them?</strong></p>
<ul>
  <li>Define values once, use everywhere.</li>
  <li>Change a color in one place, update all uses.</li>
  <li>Theme switching becomes trivial (dark mode, brand colors).</li>
  <li>JavaScript can read and update them at runtime.</li>
</ul>
<p><strong>Dark mode toggle:</strong></p>
<pre><code>:root {
  --bg: white;
  --fg: #333;
}

[data-theme="dark"] {
  --bg: #1a1a1a;
  --fg: #f0f0f0;
}

body {
  background: var(--bg);
  color: var(--fg);
}</code></pre>
<p>Toggle the theme via JavaScript: <code>document.documentElement.setAttribute("data-theme", "dark")</code>. All elements using <code>var(--bg)</code> update automatically.</p>
<p><strong>Fallback values:</strong></p>
<pre><code>.element {
  color: var(--text-color, #333);   /* if --text-color undefined, use #333 */
  padding: var(--padding, 1em);
}</code></pre>
<p><strong>Reading from JavaScript:</strong></p>
<pre><code>const root = document.documentElement;
const value = getComputedStyle(root).getPropertyValue("--primary-color");
root.style.setProperty("--primary-color", "#ff0000");</code></pre>
<p>Unlike Sass variables (compile-time), CSS variables are dynamic at runtime &mdash; the browser updates everything that references them whenever you change them.</p>
'''

ANSWERS[55] = r'''
<p>Use <code>border</code> with <code>dashed</code> as the style:</p>
<pre><code>&lt;div class="dashed-box"&gt;Dashed border&lt;/div&gt;

&lt;style&gt;
  .dashed-box {
    border: 2px dashed #888;
    padding: 1em;
    margin: 1em;
  }
&lt;/style&gt;</code></pre>
<p><strong>All border styles:</strong></p>
<table>
  <tr><th>Style</th><th>Appearance</th></tr>
  <tr><td><code>solid</code></td><td>Continuous line (most common)</td></tr>
  <tr><td><code>dashed</code></td><td>Series of dashes</td></tr>
  <tr><td><code>dotted</code></td><td>Series of dots</td></tr>
  <tr><td><code>double</code></td><td>Two parallel solid lines</td></tr>
  <tr><td><code>groove</code></td><td>3D groove effect</td></tr>
  <tr><td><code>ridge</code></td><td>3D ridge effect</td></tr>
  <tr><td><code>inset</code> / <code>outset</code></td><td>Pressed in / popping out</td></tr>
  <tr><td><code>none</code></td><td>No border</td></tr>
</table>
<p><strong>Different style per side:</strong></p>
<pre><code>.mixed-borders {
  border-top:    2px solid red;
  border-right:  2px dashed blue;
  border-bottom: 2px dotted green;
  border-left:   2px double black;
}</code></pre>
<p><strong>Common patterns:</strong></p>
<pre><code>/* Drop zone for file upload */
.drop-zone {
  border: 3px dashed #aaa;
  border-radius: 8px;
  padding: 2em;
  text-align: center;
}

/* Clarifying section divider */
.section-break {
  border-bottom: 1px dotted #ccc;
  padding-bottom: 1em;
}

/* Empty state placeholder */
.empty {
  border: 2px dashed #ddd;
  padding: 2em;
  color: #999;
  text-align: center;
}</code></pre>
<p><strong>Customize dash pattern</strong> &mdash; CSS doesn&rsquo;t directly control dash spacing on standard borders. For finer control, use SVG or <code>border-image</code> with a custom pattern.</p>
'''

ANSWERS[56] = r'''
<p>CSS Grid with <code>auto-fit</code> and <code>minmax</code> creates card layouts that respond to any viewport without media queries:</p>
<pre><code>&lt;section class="cards"&gt;
  &lt;article class="card"&gt;Card 1&lt;/article&gt;
  &lt;article class="card"&gt;Card 2&lt;/article&gt;
  &lt;article class="card"&gt;Card 3&lt;/article&gt;
  &lt;article class="card"&gt;Card 4&lt;/article&gt;
  &lt;article class="card"&gt;Card 5&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
  }
  .card {
    background: white;
    padding: 1.5em;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
&lt;/style&gt;</code></pre>
<p><strong>How it adapts to any viewport:</strong></p>
<ul>
  <li><code>auto-fit</code> &mdash; fits as many columns as possible at the minimum width.</li>
  <li><code>minmax(280px, 1fr)</code> &mdash; each column is at least 280px; if extra space exists, columns expand equally to fill it.</li>
  <li>Wide screens: 4-5 columns. Tablet: 2-3 columns. Phone: 1 column. No media queries needed.</li>
</ul>
<p><strong><code>auto-fit</code> vs <code>auto-fill</code></strong> &mdash; subtle but important:</p>
<table>
  <tr><th></th><th><code>auto-fit</code></th><th><code>auto-fill</code></th></tr>
  <tr><td>Behavior with few items</td><td>Items stretch to fill row</td><td>Items stay at minimum size, leaving empty space</td></tr>
  <tr><td>Use for</td><td>Galleries, product grids that should fill space</td><td>Fixed-grid dashboards where cards stay consistent</td></tr>
</table>
<p><strong>Equal-height cards</strong> &mdash; Grid&rsquo;s natural behavior. All cards in a row stretch to match the tallest card&rsquo;s height. To align internal content, use flexbox inside the card:</p>
<pre><code>.card {
  display: flex;
  flex-direction: column;
}
.card .btn {
  margin-top: auto;        /* pushes button to bottom */
}</code></pre>
'''

ANSWERS[57] = r'''
<p>Use the <code>font-weight</code> property:</p>
<pre><code>p { font-weight: normal; }      /* 400 */
strong { font-weight: bold; }    /* 700 */
.thin { font-weight: 100; }
.light { font-weight: 300; }
.medium { font-weight: 500; }
.heavy { font-weight: 900; }</code></pre>
<p><strong>Numeric values 100-900:</strong></p>
<table>
  <tr><th>Number</th><th>Keyword</th></tr>
  <tr><td>100</td><td>thin / hairline</td></tr>
  <tr><td>200</td><td>extra light</td></tr>
  <tr><td>300</td><td>light</td></tr>
  <tr><td>400</td><td>normal (default)</td></tr>
  <tr><td>500</td><td>medium</td></tr>
  <tr><td>600</td><td>semi-bold</td></tr>
  <tr><td>700</td><td>bold</td></tr>
  <tr><td>800</td><td>extra bold</td></tr>
  <tr><td>900</td><td>black / heavy</td></tr>
</table>
<p><strong>Caveat: not all weights are available for every font.</strong> Most fonts only ship 400 (regular) and 700 (bold). If you specify <code>font-weight: 300</code> on a font without a light variant, the browser uses 400 (the closest available).</p>
<p><strong>Variable fonts</strong> support every weight 100-900 smoothly &mdash; including fractional values like <code>437</code>:</p>
<pre><code>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@100..900&amp;display=swap");

body { font-family: "Inter", sans-serif; }
h1   { font-weight: 750; }   /* fine-grained weight */</code></pre>
<p><strong>Using <code>bolder</code> and <code>lighter</code></strong> for relative weights:</p>
<pre><code>p { font-weight: 400; }
p strong { font-weight: bolder; }   /* one step heavier than 400 */</code></pre>
<p><strong>Semantic vs presentational:</strong> use HTML&rsquo;s <code>&lt;strong&gt;</code> element for content that&rsquo;s semantically important (browsers render it bold by default). Use <code>font-weight</code> for purely visual styling.</p>
'''

ANSWERS[58] = r'''
<p>Use <code>transform: scale()</code> on hover with a transition for smooth zoom:</p>
<pre><code>&lt;div class="zoom-card"&gt;Hover to zoom&lt;/div&gt;

&lt;style&gt;
  .zoom-card {
    background: #0066cc;
    color: white;
    padding: 2em;
    border-radius: 8px;
    transition: transform 0.3s ease;
    cursor: pointer;
  }
  .zoom-card:hover {
    transform: scale(1.05);     /* 5% larger */
  }
&lt;/style&gt;</code></pre>
<p><strong>Variations:</strong></p>
<pre><code>/* Subtle zoom */
.subtle:hover { transform: scale(1.02); }

/* Stronger zoom */
.strong:hover { transform: scale(1.1); }

/* Scale only horizontally */
.wide:hover { transform: scaleX(1.1); }

/* Combined with rotation */
.fancy:hover { transform: scale(1.1) rotate(5deg); }

/* Combined with translate (lift up + scale) */
.lift:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}</code></pre>
<p><strong>Image zoom in container</strong> &mdash; image scales but stays within fixed boundaries:</p>
<pre><code>&lt;div class="img-wrapper"&gt;
  &lt;img src="photo.jpg" alt=""&gt;
&lt;/div&gt;

&lt;style&gt;
  .img-wrapper {
    overflow: hidden;
    border-radius: 8px;
  }
  .img-wrapper img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.4s ease;
  }
  .img-wrapper:hover img {
    transform: scale(1.1);
  }
&lt;/style&gt;</code></pre>
<p>The <code>overflow: hidden</code> on the wrapper clips the scaled image &mdash; producing a Ken Burns-style zoom inside a fixed frame.</p>
<p><strong>Why <code>transform</code> not <code>width</code>?</strong> <code>transform: scale()</code> is GPU-accelerated &mdash; smooth at 60fps. Animating <code>width</code> triggers layout recalculation each frame and causes stutter.</p>
<p><strong>Touch devices have no hover</strong> &mdash; use <code>@media (hover: hover)</code> if the effect should apply only when hovering is possible:</p>
<pre><code>@media (hover: hover) {
  .card:hover { transform: scale(1.05); }
}</code></pre>
'''

ANSWERS[59] = r'''
<p>Use <code>width</code> and <code>height</code> with absolute or relative units:</p>
<pre><code>.box {
  width: 300px;
  height: 200px;
}

.percentage {
  width: 50%;          /* 50% of parent's width */
  height: 100vh;       /* full viewport height */
}

.responsive {
  width: 100%;
  max-width: 800px;    /* never exceed 800px */
  height: auto;        /* let content determine height */
}</code></pre>
<p><strong>Common units:</strong></p>
<table>
  <tr><th>Unit</th><th>Meaning</th></tr>
  <tr><td><code>px</code></td><td>Pixels (absolute)</td></tr>
  <tr><td><code>%</code></td><td>Percentage of parent</td></tr>
  <tr><td><code>em</code> / <code>rem</code></td><td>Multiple of font-size</td></tr>
  <tr><td><code>vw</code> / <code>vh</code></td><td>Viewport width / height percent</td></tr>
  <tr><td><code>auto</code></td><td>Browser computes from content</td></tr>
  <tr><td><code>fit-content</code></td><td>Just enough for content; up to specified max</td></tr>
</table>
<p><strong>Use <code>min-</code> and <code>max-</code> constraints:</strong></p>
<pre><code>.flexible {
  width: 100%;
  min-width: 320px;        /* never below 320px */
  max-width: 1200px;       /* never above 1200px */
  height: auto;
  min-height: 300px;       /* at least 300px tall */
}</code></pre>
<p><strong>Critical: use <code>box-sizing: border-box</code></strong> &mdash; without it, padding and border add to <code>width</code>, making layout calculations confusing:</p>
<pre><code>* { box-sizing: border-box; }

.card {
  width: 300px;
  padding: 20px;
  border: 1px solid;
  /* Total rendered width = 300px (not 342px) */
}</code></pre>
<p>This single global rule eliminates a major class of layout bugs.</p>
<p><strong>Aspect ratio</strong> for proportional sizing without fixing both dimensions:</p>
<pre><code>.video-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;     /* height computed automatically */
}</code></pre>
'''

ANSWERS[60] = r'''
<p>Three-column flex layout with responsive collapse:</p>
<pre><code>&lt;section class="three-col"&gt;
  &lt;article&gt;Column 1&lt;/article&gt;
  &lt;article&gt;Column 2&lt;/article&gt;
  &lt;article&gt;Column 3&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .three-col {
    display: flex;
    gap: 1.5em;
    padding: 1em;
  }
  .three-col article {
    flex: 1;                  /* equal-width columns */
    background: #f8f9fa;
    padding: 1.5em;
    border-radius: 8px;
  }

  /* Mobile: stack vertically */
  @media (max-width: 768px) {
    .three-col {
      flex-direction: column;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>The <code>flex: 1</code> shorthand</strong> means: grow to fill space, shrink when needed, preferred basis 0. Each column gets equal share.</p>
<p><strong>Wrapping variant</strong> &mdash; columns wrap onto new rows as space tightens:</p>
<pre><code>.three-col {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5em;
}
.three-col article {
  flex: 1 1 250px;       /* min 250px; wraps when no room */
}</code></pre>
<p>Result: 3 columns when wide, 2 columns at intermediate width, 1 column on phone. No media queries required.</p>
<p><strong>Grid alternative</strong> &mdash; same effect, more control:</p>
<pre><code>.three-col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5em;
}

@media (max-width: 768px) {
  .three-col {
    grid-template-columns: 1fr;
  }
}</code></pre>
<p><strong>Auto-fit Grid</strong>:</p>
<pre><code>.three-col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5em;
}</code></pre>
<p>Both Flexbox and Grid handle this layout. Flexbox preserves item ordering naturally; Grid offers stronger row alignment. For most three-column layouts, either works fine &mdash; pick the syntax you find clearer.</p>
'''

ANSWERS[61] = r'''
<p>Use <code>display: flex</code> on a container element &mdash; its direct children become flex items and lay out horizontally by default:</p>
<pre><code>&lt;div class="flex-container"&gt;
  &lt;div&gt;Item 1&lt;/div&gt;
  &lt;div&gt;Item 2&lt;/div&gt;
  &lt;div&gt;Item 3&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .flex-container {
    display: flex;
    gap: 1em;
    padding: 1em;
    background: #f0f0f0;
  }
&lt;/style&gt;</code></pre>
<p>That single rule unlocks Flexbox: children align in a row, and dozens of properties become available to control them.</p>
<p><strong>Common flex container properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>flex-direction</code></td><td><code>row</code> (default), <code>column</code>, <code>row-reverse</code></td></tr>
  <tr><td><code>justify-content</code></td><td>Main-axis alignment (horizontal in row)</td></tr>
  <tr><td><code>align-items</code></td><td>Cross-axis alignment (vertical in row)</td></tr>
  <tr><td><code>flex-wrap</code></td><td>Allow wrapping to next line</td></tr>
  <tr><td><code>gap</code></td><td>Space between items</td></tr>
</table>
<p><strong>Common flex-item properties:</strong></p>
<pre><code>.item-1 { flex: 1; }            /* grow to fill */
.item-2 { flex: 0 0 200px; }     /* fixed 200px, no grow/shrink */
.item-3 { flex: 2; }             /* grows twice as much as flex: 1 items */</code></pre>
<p><strong>The canonical centering pattern</strong>:</p>
<pre><code>.center-everything {
  display: flex;
  justify-content: center;       /* horizontal */
  align-items: center;            /* vertical */
  height: 100vh;
}</code></pre>
<p>Three lines center any content both horizontally and vertically &mdash; the most popular use of Flexbox.</p>
<p><strong><code>display: inline-flex</code></strong> works the same but the container itself is inline. Useful for inline composite elements.</p>
'''

ANSWERS[62] = r'''
<p>Animate <code>width</code> and <code>height</code> in <code>@keyframes</code> &mdash; or use <code>transform: scale()</code> for smoother performance:</p>
<p><strong>Method 1: animate width and height directly</strong> (simple but less performant):</p>
<pre><code>&lt;div class="grow"&gt;&lt;/div&gt;

&lt;style&gt;
  .grow {
    width: 50px;
    height: 50px;
    background: #0066cc;
    animation: grow 2s ease-in-out infinite;
  }

  @keyframes grow {
    0%, 100% {
      width: 50px;
      height: 50px;
    }
    50% {
      width: 200px;
      height: 200px;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Method 2: <code>transform: scale()</code></strong> &mdash; preferred, GPU-accelerated:</p>
<pre><code>.scale-grow {
  width: 100px;
  height: 100px;
  background: #0066cc;
  animation: scaleGrow 2s ease-in-out infinite;
}

@keyframes scaleGrow {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(2); }
}</code></pre>
<p><strong>Why prefer <code>transform: scale()</code>?</strong></p>
<table>
  <tr><th></th><th>Width/Height</th><th>Transform: scale()</th></tr>
  <tr><td>Triggers</td><td>Layout recalculation</td><td>GPU compositing only</td></tr>
  <tr><td>Performance</td><td>Slow (60fps not guaranteed)</td><td>Smooth at 60fps</td></tr>
  <tr><td>Affects layout</td><td>Yes &mdash; siblings shift</td><td>No &mdash; visual only</td></tr>
  <tr><td>Best for</td><td>Layout animations needed</td><td>Visual emphasis effects</td></tr>
</table>
<p><strong>Combined effect &mdash; pulsing button:</strong></p>
<pre><code>.pulse-btn {
  background: #ff6b35;
  color: white;
  padding: 1em 2em;
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 15px rgba(255, 107, 53, 0);
  }
}</code></pre>
<p>This creates a "ripple" effect &mdash; the button grows slightly while a colored shadow expands outward and fades.</p>
'''

ANSWERS[63] = r'''
<p>Apply <code>box-shadow</code> to a button for an elevated, clickable look:</p>
<pre><code>&lt;button class="btn-shadow"&gt;Click me&lt;/button&gt;

&lt;style&gt;
  .btn-shadow {
    background: #0066cc;
    color: white;
    border: none;
    padding: 0.75em 1.5em;
    border-radius: 6px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    transition: all 0.2s;
  }
  .btn-shadow:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);    /* deeper shadow on hover */
    transform: translateY(-1px);                  /* slight lift */
  }
  .btn-shadow:active {
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);   /* compress on click */
    transform: translateY(0);
  }
&lt;/style&gt;</code></pre>
<p><strong>Shadow value breakdown &mdash; <code>offset-x offset-y blur-radius color</code>:</strong></p>
<pre><code>box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
/*           |  |   |   |
             |  |   |   color (semi-transparent black)
             |  |   blur radius (softness)
             |  vertical offset (down)
             horizontal offset (none)
*/</code></pre>
<p><strong>Shadow patterns by depth:</strong></p>
<table>
  <tr><th>Use case</th><th>Shadow</th></tr>
  <tr><td>Subtle button</td><td><code>0 1px 2px rgba(0,0,0,0.1)</code></td></tr>
  <tr><td>Card</td><td><code>0 2px 8px rgba(0,0,0,0.1)</code></td></tr>
  <tr><td>Hover/elevated</td><td><code>0 4px 12px rgba(0,0,0,0.15)</code></td></tr>
  <tr><td>Modal / floating</td><td><code>0 25px 50px rgba(0,0,0,0.25)</code></td></tr>
  <tr><td>Inset / pressed</td><td><code>inset 0 2px 4px rgba(0,0,0,0.1)</code></td></tr>
</table>
<p><strong>Multiple shadows for layered depth:</strong></p>
<pre><code>.btn-fancy {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.12),
    0 1px 2px rgba(0, 0, 0, 0.24);
}</code></pre>
<p>Stack multiple shadows in one declaration with commas. Material Design uses this technique extensively to simulate light from above.</p>
'''

ANSWERS[64] = r'''
<p>A CSS-only image slider uses <code>scroll-snap</code> for smooth, native swipe-to-scroll behavior:</p>
<pre><code>&lt;div class="slider"&gt;
  &lt;img src="1.jpg" alt="Slide 1"&gt;
  &lt;img src="2.jpg" alt="Slide 2"&gt;
  &lt;img src="3.jpg" alt="Slide 3"&gt;
  &lt;img src="4.jpg" alt="Slide 4"&gt;
&lt;/div&gt;

&lt;style&gt;
  .slider {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    gap: 0;
  }
  .slider img {
    flex: 0 0 100%;
    scroll-snap-align: start;
    width: 100%;
    height: 400px;
    object-fit: cover;
  }

  /* Hide scrollbar */
  .slider::-webkit-scrollbar { display: none; }
  .slider { scrollbar-width: none; }
&lt;/style&gt;</code></pre>
<p><strong>Key properties:</strong></p>
<ul>
  <li><code>scroll-snap-type: x mandatory</code> &mdash; force snap to children on x-axis when scrolling stops.</li>
  <li><code>scroll-snap-align: start</code> on each child &mdash; tells browser to snap to the start edge.</li>
  <li><code>flex: 0 0 100%</code> &mdash; each image takes full container width (no grow, no shrink).</li>
</ul>
<p><strong>Add navigation buttons:</strong></p>
<pre><code>&lt;button onclick="scrollSlider(-1)" aria-label="Previous"&gt;&#10094;&lt;/button&gt;
&lt;button onclick="scrollSlider(1)"  aria-label="Next"&gt;&#10095;&lt;/button&gt;

&lt;script&gt;
  function scrollSlider(direction) {
    const slider = document.querySelector(".slider");
    slider.scrollBy({
      left: slider.clientWidth * direction,
      behavior: "smooth",
    });
  }
&lt;/script&gt;</code></pre>
<p><strong>Pagination dots:</strong></p>
<pre><code>&lt;div class="dots"&gt;
  &lt;button class="dot active"&gt;&lt;/button&gt;
  &lt;button class="dot"&gt;&lt;/button&gt;
  &lt;button class="dot"&gt;&lt;/button&gt;
&lt;/div&gt;</code></pre>
<p><strong>Scroll-snap stop</strong> &mdash; control whether scroll always stops at each snap point:</p>
<pre><code>scroll-snap-stop: always;     /* always stop at each (no skipping) */
scroll-snap-stop: normal;     /* default — can pass over with momentum */</code></pre>
<p>For a full production carousel with autoplay, indicators, lazy loading, and accessibility, libraries like Swiper.js or Embla Carousel handle edge cases.</p>
'''

ANSWERS[65] = r'''
<p>Apply a gradient to text with <code>background-clip: text</code> + <code>color: transparent</code>:</p>
<pre><code>&lt;h1 class="gradient-text"&gt;Gradient Text&lt;/h1&gt;

&lt;style&gt;
  .gradient-text {
    background: linear-gradient(45deg, #ff6b35, #f7931e, #ffd700);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 3em;
    font-weight: bold;
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><strong><code>background</code></strong> sets a gradient as the element&rsquo;s background.</li>
  <li><strong><code>background-clip: text</code></strong> tells the browser to clip the background to the shape of the text glyphs &mdash; only show it where text is.</li>
  <li><strong><code>color: transparent</code></strong> hides the actual text color, letting the gradient show through.</li>
</ul>
<p><strong>The <code>-webkit-</code> prefix</strong> is still needed for Safari and older Chromium engines &mdash; always include both for cross-browser support.</p>
<p><strong>Variations:</strong></p>
<pre><code>/* Three-color gradient */
.tri-color {
  background: linear-gradient(45deg, red, yellow, green);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* Animated gradient */
.animated-gradient {
  background: linear-gradient(45deg, #ff6b35, #00ccff, #ff6b35);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: shift 3s linear infinite;
}
@keyframes shift {
  to { background-position: -200% center; }
}</code></pre>
<p><strong>Fallback for unsupported browsers:</strong></p>
<pre><code>.gradient-text {
  color: #ff6b35;     /* fallback solid color */
  background: linear-gradient(45deg, #ff6b35, #ffd700);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}</code></pre>
<p>Modern browsers support <code>background-clip: text</code> universally in 2026, but the fallback color ensures legibility if anything goes wrong.</p>
'''

ANSWERS[66] = r'''
<p>Animate the <code>opacity</code> property to fade an element in or out:</p>
<pre><code>&lt;div class="fade-in"&gt;I fade in!&lt;/div&gt;
&lt;div class="pulse"&gt;I pulse!&lt;/div&gt;

&lt;style&gt;
  /* One-time fade in */
  .fade-in {
    animation: fadeIn 1s ease-in forwards;
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }

  /* Looping pulse */
  .pulse {
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.4; }
  }
&lt;/style&gt;</code></pre>
<p><strong>Key animation properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>animation-name</code></td><td>Which @keyframes to run</td></tr>
  <tr><td><code>animation-duration</code></td><td>How long (e.g., <code>1s</code>)</td></tr>
  <tr><td><code>animation-iteration-count</code></td><td><code>1</code>, <code>3</code>, or <code>infinite</code></td></tr>
  <tr><td><code>animation-fill-mode</code></td><td><code>forwards</code> keeps the end state</td></tr>
  <tr><td><code>animation-timing-function</code></td><td><code>ease</code>, <code>linear</code>, <code>ease-in-out</code></td></tr>
</table>
<p><code>animation: name duration timing-function delay iteration-count direction fill-mode</code> &mdash; the shorthand combines them all.</p>
<p><strong>Performance tip:</strong> opacity is GPU-accelerated &mdash; one of the cheapest properties to animate. Always prefer animating <code>opacity</code> and <code>transform</code> over properties like <code>width</code> or <code>top</code> that trigger layout recalculation.</p>
'''

ANSWERS[67] = r'''
<p>Use the <code>border</code> property on table-related elements. The trick: by default, table cells don&rsquo;t share borders &mdash; you get a doubled appearance unless you collapse them.</p>
<pre><code>&lt;table&gt;
  &lt;thead&gt;
    &lt;tr&gt;&lt;th&gt;Name&lt;/th&gt;&lt;th&gt;Email&lt;/th&gt;&lt;th&gt;Role&lt;/th&gt;&lt;/tr&gt;
  &lt;/thead&gt;
  &lt;tbody&gt;
    &lt;tr&gt;&lt;td&gt;Alice&lt;/td&gt;&lt;td&gt;alice@x.com&lt;/td&gt;&lt;td&gt;Admin&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Bob&lt;/td&gt;&lt;td&gt;bob@x.com&lt;/td&gt;&lt;td&gt;User&lt;/td&gt;&lt;/tr&gt;
  &lt;/tbody&gt;
&lt;/table&gt;

&lt;style&gt;
  table {
    border-collapse: collapse;     /* essential — single borders */
    width: 100%;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 0.75em 1em;
    text-align: left;
  }
  th {
    background: #f5f5f5;
    font-weight: 600;
  }
  tbody tr:nth-child(even) {
    background: #fafafa;
  }
&lt;/style&gt;</code></pre>
<p><strong>border-collapse values:</strong></p>
<table>
  <tr><th>Value</th><th>Behavior</th></tr>
  <tr><td><code>collapse</code></td><td>Adjacent borders share &mdash; single line between cells</td></tr>
  <tr><td><code>separate</code> (default)</td><td>Each cell has its own border &mdash; double lines visible</td></tr>
</table>
<p><strong>For separated borders</strong> with control over spacing:</p>
<pre><code>table {
  border-collapse: separate;
  border-spacing: 4px;          /* gap between cells */
}</code></pre>
<p><strong>Outer-only borders</strong> &mdash; just the table frame, no cell borders:</p>
<pre><code>table { border: 2px solid #333; border-collapse: collapse; }
th, td { padding: 0.75em; }
/* No border on cells */</code></pre>
<p>Always use <code>border-collapse: collapse</code> for traditional data tables &mdash; it&rsquo;s cleaner and matches user expectations.</p>
'''

ANSWERS[68] = r'''
<p>Combine CSS Grid for the page-level layout with Flexbox inside individual sections &mdash; each tool plays to its strengths:</p>
<pre><code>&lt;div class="layout"&gt;
  &lt;header&gt;Header&lt;/header&gt;
  &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;main&gt;
    &lt;div class="card-row"&gt;
      &lt;article class="card"&gt;Card 1&lt;/article&gt;
      &lt;article class="card"&gt;Card 2&lt;/article&gt;
      &lt;article class="card"&gt;Card 3&lt;/article&gt;
    &lt;/div&gt;
  &lt;/main&gt;
  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  /* Grid for the page-level structure */
  .layout {
    display: grid;
    grid-template-columns: 200px 1fr;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header header"
      "aside  main"
      "footer footer";
    min-height: 100vh;
    gap: 1em;
  }
  header { grid-area: header; background: #333; color: white; padding: 1em; }
  aside  { grid-area: aside;  background: #f5f5f5; padding: 1em; }
  main   { grid-area: main;   padding: 1em; }
  footer { grid-area: footer; background: #333; color: white; padding: 1em; }

  /* Flexbox inside main for the card row */
  .card-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1em;
  }
  .card {
    flex: 1 1 250px;
    background: white;
    padding: 1em;
    border: 1px solid #ddd;
    border-radius: 8px;
  }

  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
      grid-template-areas:
        "header"
        "aside"
        "main"
        "footer";
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>The pattern:</strong></p>
<ul>
  <li><strong>Grid</strong> for the overall page (header/sidebar/main/footer) &mdash; named areas make the structure declarative.</li>
  <li><strong>Flexbox</strong> for the card row inside main &mdash; cards reflow naturally with <code>flex-wrap</code>.</li>
</ul>
<p>Grid handles 2D layouts (rows + columns); Flexbox handles 1D (a row or column). Combine them as appropriate &mdash; they&rsquo;re complementary, not competing.</p>
'''

ANSWERS[69] = r'''
<p>The <code>z-index</code> property controls vertical stacking order. Higher values render on top:</p>
<pre><code>&lt;div class="bottom"&gt;Bottom layer&lt;/div&gt;
&lt;div class="middle"&gt;Middle layer&lt;/div&gt;
&lt;div class="top"&gt;Top layer&lt;/div&gt;

&lt;style&gt;
  div {
    position: absolute;     /* required for z-index */
    width: 200px;
    height: 200px;
    padding: 1em;
  }
  .bottom { background: red;    z-index: 1;  top: 50px;  left: 50px; }
  .middle { background: green;  z-index: 5;  top: 100px; left: 100px; }
  .top    { background: blue;   z-index: 10; top: 150px; left: 150px; }
&lt;/style&gt;</code></pre>
<p><strong>Critical requirement:</strong> z-index <strong>only works on positioned elements</strong> &mdash; those with <code>position</code> set to <code>relative</code>, <code>absolute</code>, <code>fixed</code>, or <code>sticky</code>. On default <code>position: static</code>, it&rsquo;s ignored.</p>
<p><strong>Common stacking conventions:</strong></p>
<table>
  <tr><th>Layer</th><th>Typical z-index</th></tr>
  <tr><td>Base content</td><td>0 / auto</td></tr>
  <tr><td>Sticky header</td><td>10</td></tr>
  <tr><td>Dropdown menus</td><td>100</td></tr>
  <tr><td>Modal overlay</td><td>1000</td></tr>
  <tr><td>Toast notifications</td><td>2000</td></tr>
</table>
<p><strong>CSS variables for stacking layers:</strong></p>
<pre><code>:root {
  --z-header:   10;
  --z-dropdown: 100;
  --z-modal:    1000;
  --z-toast:    2000;
}
.modal { z-index: var(--z-modal); }</code></pre>
<p>Centralizing layer values prevents the "z-index: 99999" arms race. Define a small set of named layers in your design system.</p>
'''

ANSWERS[70] = r'''
<p>Combine <code>:hover</code> with <code>transition</code> for a smooth color change on hover:</p>
<pre><code>&lt;button class="btn"&gt;Hover me&lt;/button&gt;

&lt;style&gt;
  .btn {
    background: #0066cc;
    color: white;
    padding: 0.75em 1.5em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background 0.3s ease;   /* smooth color change */
  }
  .btn:hover {
    background: #004999;                /* darker on hover */
  }
&lt;/style&gt;</code></pre>
<p><strong>Apply <code>transition</code> to the BASE selector,</strong> not the hover state &mdash; that way it animates in both directions (entering AND leaving the hover):</p>
<pre><code>.btn { transition: background 0.3s; }   /* GOOD: smooth on enter and leave */
.btn:hover { transition: ... }            /* WRONG: only smooth on enter */</code></pre>
<p><strong>Multiple property transitions:</strong></p>
<pre><code>.btn {
  background: #0066cc;
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition:
    background 0.3s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.btn:hover {
  background: #004999;
  transform: translateY(-2px);             /* slight lift */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}</code></pre>
<p>The shorthand <code>transition: all 0.3s</code> animates every changed property &mdash; convenient but slower than naming specific properties.</p>
<p><strong>Timing functions</strong> (curves):</p>
<table>
  <tr><th>Function</th><th>Feel</th></tr>
  <tr><td><code>linear</code></td><td>Constant speed</td></tr>
  <tr><td><code>ease</code></td><td>Default; slow start and end</td></tr>
  <tr><td><code>ease-in</code></td><td>Slow start, fast end</td></tr>
  <tr><td><code>ease-out</code></td><td>Fast start, slow end</td></tr>
  <tr><td><code>cubic-bezier(0.4, 0, 0.2, 1)</code></td><td>Custom curve (Material Design)</td></tr>
</table>
'''

ANSWERS[71] = r'''
<p>Define a CSS variable with <code>--name</code>, then reference with <code>var()</code>:</p>
<pre><code>&lt;div class="card"&gt;Card with variable color&lt;/div&gt;
&lt;div class="card alt"&gt;Different variable color&lt;/div&gt;

&lt;style&gt;
  :root {
    --card-bg: #f0f8ff;
    --card-bg-alt: #fff5e6;
  }

  .card {
    background-color: var(--card-bg);
    padding: 1em;
    border-radius: 8px;
  }

  .card.alt {
    background-color: var(--card-bg-alt);
  }
&lt;/style&gt;</code></pre>
<p><strong>Override per element or scope:</strong></p>
<pre><code>:root {
  --primary: #0066cc;
}

.theme-dark {
  --primary: #ff6b35;          /* override within this scope */
}

.btn {
  background: var(--primary);   /* inherits from nearest scope */
}</code></pre>
<p>The <code>.theme-dark .btn</code> uses orange; outside that scope, buttons are blue. CSS variables cascade through the DOM tree, so children inherit overrides.</p>
<p><strong>Fallback values</strong> for safety:</p>
<pre><code>.box {
  background: var(--bg-color, white);   /* white if --bg-color undefined */
}</code></pre>
<p><strong>Update from JavaScript</strong> for runtime theming:</p>
<pre><code>document.documentElement.style.setProperty("--primary", "#22c55e");
/* All elements using var(--primary) update instantly */</code></pre>
<p>This dynamic capability is what makes CSS variables more powerful than Sass variables &mdash; they update at runtime without recompiling.</p>
'''

ANSWERS[72] = r'''
<p>CSS Grid handles complex form layouts cleanly &mdash; one rule defines the grid, fields automatically place themselves:</p>
<pre><code>&lt;form class="form-grid"&gt;
  &lt;label&gt;First name&lt;input name="first"&gt;&lt;/label&gt;
  &lt;label&gt;Last name&lt;input name="last"&gt;&lt;/label&gt;
  &lt;label class="full"&gt;Email&lt;input type="email" name="email"&gt;&lt;/label&gt;
  &lt;label&gt;City&lt;input name="city"&gt;&lt;/label&gt;
  &lt;label&gt;State&lt;input name="state"&gt;&lt;/label&gt;
  &lt;label class="full"&gt;Message&lt;textarea name="message" rows="4"&gt;&lt;/textarea&gt;&lt;/label&gt;
  &lt;button class="full" type="submit"&gt;Submit&lt;/button&gt;
&lt;/form&gt;

&lt;style&gt;
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1em;
    max-width: 600px;
    margin: 0 auto;
    padding: 2em;
  }
  .form-grid label {
    display: flex;
    flex-direction: column;
    gap: 0.25em;
    font-size: 0.9em;
  }
  .form-grid input,
  .form-grid textarea {
    padding: 0.5em;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1em;
  }
  .form-grid .full {
    grid-column: 1 / -1;        /* span all columns */
  }
  .form-grid button {
    background: #0066cc;
    color: white;
    border: none;
    padding: 0.75em;
    border-radius: 4px;
    cursor: pointer;
  }

  /* Mobile: single column */
  @media (max-width: 600px) {
    .form-grid { grid-template-columns: 1fr; }
  }
&lt;/style&gt;</code></pre>
<p><strong>Key techniques:</strong></p>
<ul>
  <li><code>grid-template-columns: 1fr 1fr</code> &mdash; two equal columns.</li>
  <li><code>grid-column: 1 / -1</code> &mdash; element spans from column 1 to the last column (full width).</li>
  <li>Mobile media query collapses to single column.</li>
  <li>Each label is its own flex container for label-above-input layout.</li>
</ul>
<p>Compared to Flexbox, Grid is better for form layouts because two-column / full-width mixing is declarative &mdash; no flex-basis math.</p>
'''

ANSWERS[73] = r'''
<p>Use <code>tr:hover</code> to highlight rows on mouse-over:</p>
<pre><code>&lt;table class="data-table"&gt;
  &lt;thead&gt;
    &lt;tr&gt;&lt;th&gt;Name&lt;/th&gt;&lt;th&gt;Email&lt;/th&gt;&lt;th&gt;Role&lt;/th&gt;&lt;/tr&gt;
  &lt;/thead&gt;
  &lt;tbody&gt;
    &lt;tr&gt;&lt;td&gt;Alice&lt;/td&gt;&lt;td&gt;alice@x.com&lt;/td&gt;&lt;td&gt;Admin&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Bob&lt;/td&gt;&lt;td&gt;bob@x.com&lt;/td&gt;&lt;td&gt;User&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Carol&lt;/td&gt;&lt;td&gt;carol@x.com&lt;/td&gt;&lt;td&gt;Editor&lt;/td&gt;&lt;/tr&gt;
  &lt;/tbody&gt;
&lt;/table&gt;

&lt;style&gt;
  .data-table {
    width: 100%;
    border-collapse: collapse;
  }
  .data-table th,
  .data-table td {
    padding: 0.75em 1em;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  .data-table tbody tr {
    transition: background 0.15s;
  }
  .data-table tbody tr:hover {
    background: #f0f8ff;
    cursor: pointer;
  }
&lt;/style&gt;</code></pre>
<p><strong>Combine with zebra striping</strong> for clearer visual hierarchy:</p>
<pre><code>.data-table tbody tr:nth-child(even) {
  background: #fafafa;
}
.data-table tbody tr:hover {
  background: #e3f2fd;       /* darker than zebra; clear hover state */
}</code></pre>
<p><strong>Make rows clickable</strong> &mdash; usually rows wrap a link or trigger a JavaScript handler:</p>
<pre><code>.data-table tbody tr {
  cursor: pointer;
  transition: background 0.15s;
}
.data-table tbody tr:hover {
  background: #e3f2fd;
}

&lt;script&gt;
  document.querySelectorAll(".data-table tbody tr").forEach(row =&gt; {
    row.addEventListener("click", () =&gt; {
      window.location = "/users/" + row.dataset.id;
    });
  });
&lt;/script&gt;</code></pre>
<p>For accessibility, add <code>role="button"</code> + keyboard handlers, or use a real link element wrapping the row content. Pure CSS hover effects are great visual feedback but interactive rows need keyboard support too.</p>
'''

ANSWERS[74] = r'''
<p>Use the <code>transform: scale()</code> function:</p>
<pre><code>&lt;div class="card"&gt;Hover to scale&lt;/div&gt;
&lt;img class="grow-image" src="photo.jpg" alt=""&gt;

&lt;style&gt;
  .card {
    background: #0066cc;
    color: white;
    padding: 2em;
    transition: transform 0.3s ease;
  }
  .card:hover {
    transform: scale(1.05);          /* 5% larger */
  }

  .grow-image {
    width: 200px;
    transition: transform 0.4s ease;
  }
  .grow-image:hover {
    transform: scale(1.2);            /* 20% larger */
  }
&lt;/style&gt;</code></pre>
<p><strong>Scale variations:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>scale(1.5)</code></td><td>Both dimensions: 1.5x</td></tr>
  <tr><td><code>scale(1.5, 2)</code></td><td>X: 1.5x, Y: 2x</td></tr>
  <tr><td><code>scaleX(1.5)</code></td><td>Horizontal only</td></tr>
  <tr><td><code>scaleY(2)</code></td><td>Vertical only</td></tr>
  <tr><td><code>scale(0.5)</code></td><td>50% smaller</td></tr>
  <tr><td><code>scale(-1, 1)</code></td><td>Mirror horizontally</td></tr>
</table>
<p><strong>Combining transforms</strong> &mdash; scale, rotate, translate together:</p>
<pre><code>.card:hover {
  transform: scale(1.1) rotate(2deg) translateY(-5px);
}</code></pre>
<p>Order matters! Transforms apply right-to-left in the function list.</p>
<p><strong>Performance:</strong> <code>transform</code> is GPU-accelerated &mdash; scale animations are buttery-smooth. Compared to animating <code>width</code>/<code>height</code> directly (which triggers layout recalculation), <code>scale()</code> is far more efficient. Always prefer transforms for animation.</p>
<p><strong>Important:</strong> scaling affects the visual size only, not the layout space the element takes &mdash; siblings don&rsquo;t shift around when an element scales.</p>
'''

ANSWERS[75] = r'''
<p>Use a CSS variable with the <code>color</code> property:</p>
<pre><code>&lt;p class="primary-text"&gt;Primary color text&lt;/p&gt;
&lt;p class="secondary-text"&gt;Secondary color text&lt;/p&gt;

&lt;style&gt;
  :root {
    --primary-color: #0066cc;
    --secondary-color: #ff6b35;
    --text-color: #333;
  }

  body {
    color: var(--text-color);
  }
  .primary-text {
    color: var(--primary-color);
  }
  .secondary-text {
    color: var(--secondary-color);
  }
&lt;/style&gt;</code></pre>
<p><strong>Theme switching</strong> &mdash; change colors site-wide by overriding variables:</p>
<pre><code>:root {
  --text-color: #333;
  --bg-color: white;
}

[data-theme="dark"] {
  --text-color: #f0f0f0;
  --bg-color: #1a1a1a;
}

body {
  color: var(--text-color);
  background: var(--bg-color);
  transition: color 0.3s, background 0.3s;
}</code></pre>
<pre><code>// Toggle theme via JavaScript
document.documentElement.dataset.theme =
  document.documentElement.dataset.theme === "dark" ? "light" : "dark";</code></pre>
<p>Set <code>data-theme="dark"</code> on the <code>&lt;html&gt;</code> element; all elements using <code>var(--text-color)</code> instantly update to dark colors.</p>
<p><strong>Respect user preference automatically:</strong></p>
<pre><code>@media (prefers-color-scheme: dark) {
  :root {
    --text-color: #f0f0f0;
    --bg-color: #1a1a1a;
  }
}</code></pre>
<p>The OS dark mode setting drives the theme &mdash; no JavaScript required for the basic case.</p>
'''

ANSWERS[76] = r'''
<p>Combine <code>animation</code> with <code>transform: rotate()</code> in keyframes for continuous rotation:</p>
<pre><code>&lt;div class="spinner"&gt;&lt;/div&gt;
&lt;svg class="loader"&gt;&lt;circle r="20" cx="25" cy="25" stroke="#0066cc" stroke-width="4" fill="none"/&gt;&lt;/svg&gt;

&lt;style&gt;
  /* Continuous rotation */
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f0f0f0;
    border-top: 4px solid #0066cc;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
  }

  .loader {
    width: 50px;
    height: 50px;
    animation: spin 2s linear infinite;
  }
&lt;/style&gt;</code></pre>
<p><strong>Key components:</strong></p>
<ul>
  <li><code>animation: spin 1s linear infinite</code> &mdash; runs the spin keyframes for 1s, looping forever, at constant speed.</li>
  <li><code>linear</code> timing &mdash; constant rotation speed (no acceleration).</li>
  <li><code>infinite</code> &mdash; never stops.</li>
</ul>
<p><strong>Variations:</strong></p>
<pre><code>/* Slow rotation */
.slow { animation: spin 3s linear infinite; }

/* Reverse direction */
.reverse { animation: spin 1s linear infinite reverse; }

/* Pulse + rotate combined */
@keyframes spin-pulse {
  0%   { transform: rotate(0deg) scale(1); }
  50%  { transform: rotate(180deg) scale(1.1); }
  100% { transform: rotate(360deg) scale(1); }
}</code></pre>
<p><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; users with vestibular disorders may have motion disabled:</p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  .spinner { animation: none; }
}</code></pre>
<p>For loading spinners specifically, consider replacing rotation with a static graphic or simple opacity pulse for users who&rsquo;ve opted out of motion.</p>
'''

ANSWERS[77] = r'''
<p>Use a <code>linear-gradient</code> as the <code>background</code>:</p>
<pre><code>&lt;div class="grad-1"&gt;Linear horizontal&lt;/div&gt;
&lt;div class="grad-2"&gt;Linear diagonal&lt;/div&gt;
&lt;div class="grad-3"&gt;Multi-stop&lt;/div&gt;
&lt;div class="grad-4"&gt;Radial&lt;/div&gt;

&lt;style&gt;
  div {
    padding: 2em;
    color: white;
    margin-bottom: 1em;
    border-radius: 8px;
  }

  .grad-1 {
    background: linear-gradient(to right, #0066cc, #00ccff);
  }

  .grad-2 {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
  }

  .grad-3 {
    background: linear-gradient(to right, red, yellow, green, blue);
  }

  .grad-4 {
    background: radial-gradient(circle, #ff6b35, #c0392b);
  }
&lt;/style&gt;</code></pre>
<p><strong>Direction syntax:</strong></p>
<table>
  <tr><th>Syntax</th><th>Means</th></tr>
  <tr><td><code>to right</code></td><td>Left to right (90deg)</td></tr>
  <tr><td><code>to bottom</code></td><td>Top to bottom (180deg, default)</td></tr>
  <tr><td><code>to bottom right</code></td><td>Diagonal</td></tr>
  <tr><td><code>45deg</code></td><td>Specific angle</td></tr>
</table>
<p><strong>Color stops at specific positions:</strong></p>
<pre><code>.precise {
  background: linear-gradient(
    to right,
    red 0%,
    yellow 30%,
    green 60%,
    blue 100%
  );
}</code></pre>
<p><strong>Subtle gradients</strong> &mdash; the modern look uses very close colors:</p>
<pre><code>.subtle {
  background: linear-gradient(180deg, #f8f9fa, #e9ecef);
  /* Almost invisible — gives depth without distraction */
}</code></pre>
<p>Gradients are images &mdash; you can layer them, animate them with <code>background-size</code> + <code>background-position</code>, or use them in <code>border-image</code>.</p>
'''

ANSWERS[78] = r'''
<p>Use Flexbox with a fixed-width sidebar and flexible main content:</p>
<pre><code>&lt;div class="layout"&gt;
  &lt;aside&gt;
    &lt;nav&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="#"&gt;Dashboard&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Profile&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Settings&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/aside&gt;
  &lt;main&gt;
    &lt;h1&gt;Main content&lt;/h1&gt;
    &lt;p&gt;Lots of content here...&lt;/p&gt;
  &lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: flex;
    gap: 2em;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1em;
  }
  aside {
    flex: 0 0 250px;       /* fixed 250px, no grow, no shrink */
    background: #f5f5f5;
    padding: 1em;
    border-radius: 8px;
  }
  main {
    flex: 1;                /* fills remaining space */
    min-width: 0;            /* allow content to shrink */
  }
  aside ul {
    list-style: none;
    padding: 0;
  }
  aside a {
    display: block;
    padding: 0.5em;
    color: #333;
    text-decoration: none;
    border-radius: 4px;
  }
  aside a:hover {
    background: #e9ecef;
  }

  /* Mobile: stack vertically */
  @media (max-width: 768px) {
    .layout {
      flex-direction: column;
    }
    aside {
      flex: none;          /* take natural height */
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>The flex shorthands explained:</strong></p>
<ul>
  <li><code>flex: 0 0 250px</code> on sidebar &mdash; no grow, no shrink, basis 250px (locked width).</li>
  <li><code>flex: 1</code> on main &mdash; takes all remaining space.</li>
  <li><code>min-width: 0</code> on main &mdash; allows content to shrink (Flexbox defaults to <code>min-width: auto</code>, which can cause overflow).</li>
</ul>
<p>Mobile media query collapses to single column &mdash; aside on top, main below.</p>
'''

ANSWERS[79] = r'''
<p>Set the default <code>background-image</code>, then change it on <code>:hover</code>:</p>
<pre><code>&lt;div class="hero"&gt;Hover to change background&lt;/div&gt;

&lt;style&gt;
  .hero {
    background-image: url("/images/scene-1.jpg");
    background-size: cover;
    background-position: center;
    height: 400px;
    color: white;
    padding: 2em;
    transition: background-image 0.5s ease;
  }
  .hero:hover {
    background-image: url("/images/scene-2.jpg");
  }
&lt;/style&gt;</code></pre>
<p><strong>Smooth crossfade between images</strong> &mdash; <code>background-image</code> doesn&rsquo;t actually animate (it&rsquo;s instant), so use the opacity-overlay trick:</p>
<pre><code>&lt;div class="crossfade"&gt;Hover for smooth transition&lt;/div&gt;

&lt;style&gt;
  .crossfade {
    position: relative;
    height: 400px;
    background-image: url("/images/scene-1.jpg");
    background-size: cover;
  }
  .crossfade::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: url("/images/scene-2.jpg");
    background-size: cover;
    opacity: 0;
    transition: opacity 0.5s ease;
  }
  .crossfade:hover::after {
    opacity: 1;             /* fade in second image */
  }
&lt;/style&gt;</code></pre>
<p>The <code>::after</code> pseudo-element holds the second image, fading in over the first. Browsers can&rsquo;t directly transition <code>background-image</code>, but they can transition <code>opacity</code> &mdash; this trick gives the appearance of a smooth swap.</p>
<p><strong>Pre-load the hover image</strong> to prevent a flash on first hover:</p>
<pre><code>&lt;link rel="preload" as="image" href="/images/scene-2.jpg"&gt;</code></pre>
<p>Or include both images in <code>::before</code> and <code>::after</code> from the start &mdash; both load with the page.</p>
'''

ANSWERS[80] = r'''
<p>Animate the <code>color</code> property between values in <code>@keyframes</code>:</p>
<pre><code>&lt;p class="rainbow-text"&gt;Watch me change color!&lt;/p&gt;

&lt;style&gt;
  .rainbow-text {
    font-size: 2em;
    font-weight: bold;
    animation: rainbow 4s linear infinite;
  }

  @keyframes rainbow {
    0%   { color: red; }
    20%  { color: orange; }
    40%  { color: yellow; }
    60%  { color: green; }
    80%  { color: blue; }
    100% { color: red; }
  }
&lt;/style&gt;</code></pre>
<p><strong>Two-color pulse</strong> &mdash; simpler version:</p>
<pre><code>.attention-text {
  animation: blink 1s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { color: black; }
  50%      { color: red; }
}</code></pre>
<p><strong>Highlight on appear</strong> &mdash; smooth color reveal:</p>
<pre><code>.highlight {
  animation: highlight 2s ease-out forwards;
}
@keyframes highlight {
  from { color: orange; background: #fff3cd; }
  to   { color: black;  background: transparent; }
}</code></pre>
<p><strong>Tips for color animations:</strong></p>
<ul>
  <li><strong>Use <code>infinite</code></strong> for ongoing effects (pulses, rainbows).</li>
  <li><strong>Use <code>forwards</code> fill mode</strong> for one-time effects to keep the end state.</li>
  <li><strong>Animate <code>background-color</code></strong> instead of <code>color</code> for highlight effects.</li>
  <li><strong>Subtle is best</strong> &mdash; flashy text animations distract; reserve them for genuine attention-grabbers like notification badges.</li>
</ul>
<p><strong>Respect <code>prefers-reduced-motion</code>:</strong></p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  .rainbow-text { animation: none; }
}</code></pre>
'''

ANSWERS[81] = r'''
<p>Use individual side properties: <code>border-top</code>, <code>border-right</code>, <code>border-bottom</code>, <code>border-left</code>:</p>
<pre><code>&lt;div class="left-accent"&gt;Left border accent&lt;/div&gt;
&lt;div class="bottom-divider"&gt;Bottom divider&lt;/div&gt;
&lt;div class="quote"&gt;A bordered blockquote&lt;/div&gt;

&lt;style&gt;
  .left-accent {
    border-left: 4px solid #0066cc;
    padding: 1em;
    background: #f8f9fa;
  }

  .bottom-divider {
    border-bottom: 1px solid #e0e0e0;
    padding: 1em 0;
  }

  .quote {
    border-left: 4px solid #999;
    padding-left: 1em;
    font-style: italic;
    color: #666;
  }
&lt;/style&gt;</code></pre>
<p><strong>Logical properties</strong> &mdash; modern alternative that respects writing direction (RTL languages):</p>
<table>
  <tr><th>Physical</th><th>Logical</th></tr>
  <tr><td><code>border-left</code></td><td><code>border-inline-start</code></td></tr>
  <tr><td><code>border-right</code></td><td><code>border-inline-end</code></td></tr>
  <tr><td><code>border-top</code></td><td><code>border-block-start</code></td></tr>
  <tr><td><code>border-bottom</code></td><td><code>border-block-end</code></td></tr>
</table>
<pre><code>.callout {
  border-inline-start: 4px solid #0066cc;
  /* "left" in LTR; "right" in RTL automatically */
  padding-inline-start: 1em;
}</code></pre>
<p><strong>Different colors per side</strong> &mdash; quick way to do tabbed indicators:</p>
<pre><code>.tab-active {
  border-top:    3px solid #0066cc;
  border-left:   1px solid #ddd;
  border-right:  1px solid #ddd;
  border-bottom: 1px solid white;    /* hide bottom edge */
  padding: 0.5em 1em;
}</code></pre>
<p>Each side&rsquo;s shorthand: <code>border-X: width style color</code>.</p>
'''

ANSWERS[82] = r'''
<p>CSS Grid with named template areas creates clear, declarative page layouts:</p>
<pre><code>&lt;div class="page"&gt;
  &lt;header&gt;Site header&lt;/header&gt;
  &lt;main&gt;Main content area&lt;/main&gt;
  &lt;footer&gt;Site footer&lt;/footer&gt;
&lt;/div&gt;

&lt;style&gt;
  .page {
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header"
      "main"
      "footer";
    min-height: 100vh;
  }
  header {
    grid-area: header;
    background: #2c3e50;
    color: white;
    padding: 1em;
  }
  main {
    grid-area: main;
    padding: 2em;
  }
  footer {
    grid-area: footer;
    background: #34495e;
    color: white;
    padding: 1em;
    text-align: center;
  }
&lt;/style&gt;</code></pre>
<p><strong>Why this works for sticky-footer pages:</strong></p>
<ul>
  <li><code>min-height: 100vh</code> &mdash; page is always at least viewport height.</li>
  <li><code>grid-template-rows: auto 1fr auto</code> &mdash; header and footer take their natural height; main takes all the remaining space.</li>
  <li>Footer stays at the bottom even when content is short, but pushes down naturally when content grows tall.</li>
</ul>
<p><strong>Add a sidebar variant:</strong></p>
<pre><code>.page-with-sidebar {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header  header"
    "sidebar main"
    "footer  footer";
  min-height: 100vh;
}
aside { grid-area: sidebar; }</code></pre>
<p><strong>Mobile responsive</strong> &mdash; rearrange areas:</p>
<pre><code>@media (max-width: 768px) {
  .page-with-sidebar {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "sidebar"
      "main"
      "footer";
  }
}</code></pre>
<p>Named areas make these layouts self-documenting &mdash; the CSS describes the structure visually.</p>
'''

ANSWERS[83] = r'''
<p>Define a CSS variable for the size, then reference it in <code>font-size</code>:</p>
<pre><code>&lt;p class="text-sm"&gt;Small text&lt;/p&gt;
&lt;p class="text-base"&gt;Base size text&lt;/p&gt;
&lt;p class="text-lg"&gt;Larger text&lt;/p&gt;
&lt;h1 class="text-xl"&gt;Heading text&lt;/h1&gt;

&lt;style&gt;
  :root {
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.25rem;
    --text-xl: 2rem;
  }

  .text-sm   { font-size: var(--text-sm); }
  .text-base { font-size: var(--text-base); }
  .text-lg   { font-size: var(--text-lg); }
  .text-xl   { font-size: var(--text-xl); }
&lt;/style&gt;</code></pre>
<p><strong>Centralized typography scale</strong> &mdash; common in design systems:</p>
<pre><code>:root {
  /* Type scale */
  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-md:   1.125rem;
  --text-lg:   1.25rem;
  --text-xl:   1.5rem;
  --text-2xl:  1.875rem;
  --text-3xl:  2.25rem;
  --text-4xl:  3rem;
}</code></pre>
<p><strong>Responsive font sizes</strong> &mdash; update variables in media queries:</p>
<pre><code>:root {
  --text-xl: 1.5rem;
}

@media (min-width: 768px) {
  :root {
    --text-xl: 2rem;       /* larger on tablet+ */
  }
}

h1 { font-size: var(--text-xl); }   /* automatically responsive */</code></pre>
<p>Update one variable in a media query; all elements using <code>var(--text-xl)</code> resize automatically.</p>
<p><strong>Fluid typography with <code>clamp()</code></strong>:</p>
<pre><code>:root {
  --text-fluid: clamp(1.5rem, 3vw + 1rem, 3rem);
}
h1 { font-size: var(--text-fluid); }</code></pre>
<p>Combines variables with fluid sizing for the cleanest responsive typography.</p>
'''

ANSWERS[84] = r'''
<p>Use the <code>transform: skew()</code> function to slant elements diagonally:</p>
<pre><code>&lt;div class="skew-x"&gt;Skewed horizontally&lt;/div&gt;
&lt;div class="skew-y"&gt;Skewed vertically&lt;/div&gt;
&lt;div class="skew-both"&gt;Skewed both ways&lt;/div&gt;

&lt;style&gt;
  div {
    background: #0066cc;
    color: white;
    padding: 1em;
    margin: 1em;
    width: 200px;
  }

  .skew-x {
    transform: skewX(-15deg);          /* horizontal slant */
  }

  .skew-y {
    transform: skewY(10deg);            /* vertical slant */
  }

  .skew-both {
    transform: skew(-10deg, 5deg);      /* X and Y */
  }
&lt;/style&gt;</code></pre>
<p><strong>Skew functions:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>skewX(angle)</code></td><td>Slant horizontally</td></tr>
  <tr><td><code>skewY(angle)</code></td><td>Slant vertically</td></tr>
  <tr><td><code>skew(x, y)</code></td><td>Both axes</td></tr>
</table>
<p><strong>Counter-skew the content</strong> to keep text upright in a skewed container:</p>
<pre><code>&lt;div class="skew-card"&gt;
  &lt;span class="content"&gt;Upright text in skewed shape&lt;/span&gt;
&lt;/div&gt;

&lt;style&gt;
  .skew-card {
    transform: skewX(-10deg);
    background: #ff6b35;
    padding: 1em 2em;
    color: white;
  }
  .skew-card .content {
    display: inline-block;
    transform: skewX(10deg);     /* opposite skew on content */
  }
&lt;/style&gt;</code></pre>
<p>This is a classic ribbon/banner trick &mdash; the container leans, the text stays straight.</p>
<p><strong>Common use cases:</strong></p>
<ul>
  <li>Ribbon/banner effects.</li>
  <li>Quote blocks with leaning style.</li>
  <li>Card hover effects (slight skew = playful).</li>
  <li>Text decorations (skewed underlines).</li>
</ul>
<p>Use sparingly &mdash; subtle skew (5-15&deg;) feels modern; aggressive skew can look dated.</p>
'''

ANSWERS[85] = r'''
<p>Use <code>:hover</code> with the <code>color</code> property and a transition for smoothness:</p>
<pre><code>&lt;a href="#" class="link"&gt;Hover to change&lt;/a&gt;
&lt;p class="text"&gt;Hover the link above to see the change.&lt;/p&gt;

&lt;style&gt;
  .link {
    color: #0066cc;
    text-decoration: none;
    transition: color 0.2s;
  }
  .link:hover {
    color: #ff6b35;
  }
&lt;/style&gt;</code></pre>
<p><strong>Multi-property hover</strong> &mdash; combine color, decoration, and transform:</p>
<pre><code>.fancy-link {
  color: #0066cc;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}
.fancy-link:hover {
  color: #ff6b35;
  border-bottom-color: currentColor;     /* underline appears */
}</code></pre>
<p><strong>Hover animations on cards</strong> &mdash; using <code>currentColor</code>:</p>
<pre><code>.card {
  color: #333;
  border-left: 4px solid currentColor;
  transition: color 0.2s, transform 0.2s;
  padding: 1em;
}
.card:hover {
  color: #ff6b35;        /* both text and border change */
  transform: translateX(4px);
}</code></pre>
<p><code>currentColor</code> is a CSS keyword that resolves to the element&rsquo;s computed <code>color</code> &mdash; SVG icons and borders inherit text color automatically. Animating <code>color</code> animates everything that uses <code>currentColor</code>.</p>
<p><strong>Gotcha:</strong> some properties don&rsquo;t transition (like <code>color</code>) by default in older syntax. Always include <code>transition</code> on the base selector, not the hover state, so transitions work in both directions (hover-in AND hover-out).</p>
'''

ANSWERS[86] = r'''
<p>Nest flex containers to compose complex responsive layouts &mdash; each flex container handles a single dimension:</p>
<pre><code>&lt;div class="page"&gt;
  &lt;header class="header"&gt;
    &lt;a href="/" class="logo"&gt;Logo&lt;/a&gt;
    &lt;nav class="nav-links"&gt;
      &lt;a href="#"&gt;Home&lt;/a&gt;
      &lt;a href="#"&gt;About&lt;/a&gt;
    &lt;/nav&gt;
    &lt;div class="actions"&gt;
      &lt;button&gt;Login&lt;/button&gt;
      &lt;button&gt;Sign up&lt;/button&gt;
    &lt;/div&gt;
  &lt;/header&gt;

  &lt;main class="content"&gt;
    &lt;article&gt;Main content&lt;/article&gt;
    &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .header {
    display: flex;                    /* outer flex */
    justify-content: space-between;
    align-items: center;
    padding: 1em;
    background: white;
    border-bottom: 1px solid #eee;
  }

  .nav-links {
    display: flex;                    /* nested flex */
    gap: 1.5em;
  }

  .actions {
    display: flex;                    /* nested flex */
    gap: 0.5em;
  }

  .content {
    display: flex;                    /* main + sidebar */
    flex: 1;
    gap: 2em;
    padding: 2em;
  }
  .content article {
    flex: 1;                          /* fills available */
  }
  .content aside {
    flex: 0 0 250px;                  /* fixed width */
  }

  /* Mobile */
  @media (max-width: 768px) {
    .header { flex-wrap: wrap; }
    .content { flex-direction: column; }
    .content aside { flex: none; }
  }
&lt;/style&gt;</code></pre>
<p><strong>The pattern:</strong> each flex container handles one row or column. Composition gives you complex layouts without complex selectors.</p>
<p><strong>Key tips:</strong></p>
<ul>
  <li><code>flex: 1</code> = grow to fill remaining space.</li>
  <li><code>flex: 0 0 250px</code> = fixed width, no grow/shrink.</li>
  <li><code>flex-wrap: wrap</code> + <code>flex: 1 1 250px</code> = responsive auto-wrapping.</li>
</ul>
'''

ANSWERS[87] = r'''
<p>Set a base width on the element, then change it on <code>:hover</code> with a transition:</p>
<pre><code>&lt;div class="expander"&gt;Hover to expand&lt;/div&gt;
&lt;input type="search" class="search-bar" placeholder="Search..."&gt;
&lt;a href="#" class="grow-link"&gt;Hover me&lt;/a&gt;

&lt;style&gt;
  .expander {
    width: 200px;
    background: #0066cc;
    color: white;
    padding: 1em;
    transition: width 0.3s ease;
  }
  .expander:hover {
    width: 300px;
  }

  .search-bar {
    width: 150px;
    padding: 0.5em 1em;
    border: 1px solid #ccc;
    border-radius: 20px;
    transition: width 0.3s ease;
  }
  .search-bar:focus {
    width: 300px;             /* expand on focus */
  }

  .grow-link {
    display: inline-block;
    width: 100px;
    padding: 0.5em;
    background: #ff6b35;
    color: white;
    text-align: center;
    text-decoration: none;
    transition: width 0.2s;
  }
  .grow-link:hover {
    width: 150px;
  }
&lt;/style</code></pre>
<p><strong>Common pattern: expanding search bar</strong> &mdash; popular in headers:</p>
<pre><code>.search-input {
  width: 0;                  /* hidden by default */
  padding: 0;
  border: none;
  transition: width 0.3s, padding 0.3s;
}
.search-container:hover .search-input,
.search-input:focus {
  width: 200px;
  padding: 0.5em 1em;
  border: 1px solid #ccc;
}</code></pre>
<p><strong>Performance note:</strong> animating <code>width</code> triggers layout recalculation on every frame &mdash; expensive for complex pages. For better performance, use <code>transform: scaleX()</code> instead, which is GPU-accelerated:</p>
<pre><code>.fast-grow {
  transform: scaleX(1);
  transform-origin: left;
  transition: transform 0.3s;
}
.fast-grow:hover {
  transform: scaleX(1.5);    /* visually wider; no layout shift */
}</code></pre>
<p>Use <code>transform</code> when possible; reserve <code>width</code> animation for cases where actual layout change is the goal.</p>
'''

ANSWERS[88] = r'''
<p>Animate <code>background-position</code> for shimmer, marching stripes, or moving gradients:</p>
<pre><code>&lt;div class="shimmer"&gt;Shimmering effect&lt;/div&gt;
&lt;div class="stripes"&gt;Marching stripes&lt;/div&gt;

&lt;style&gt;
  /* Shimmer / loading skeleton */
  .shimmer {
    height: 80px;
    background: linear-gradient(
      90deg,
      #f0f0f0 0%,
      #e0e0e0 50%,
      #f0f0f0 100%
    );
    background-size: 200% 100%;
    animation: shimmer 2s linear infinite;
  }

  @keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  /* Marching stripes (progress bar style) */
  .stripes {
    height: 30px;
    background: repeating-linear-gradient(
      45deg,
      #0066cc,
      #0066cc 10px,
      #0055aa 10px,
      #0055aa 20px
    );
    animation: march 1s linear infinite;
  }

  @keyframes march {
    0%   { background-position: 0 0; }
    100% { background-position: 28px 0; }
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li><strong>Shimmer:</strong> background size larger than container; animation slides the position from left to right, creating the illusion of light moving across.</li>
  <li><strong>Stripes:</strong> repeating gradient + position shift = stripes appear to march. The shift distance must match the pattern repeat.</li>
</ul>
<p><strong>Common use cases:</strong></p>
<table>
  <tr><th>Pattern</th><th>Use for</th></tr>
  <tr><td>Shimmer</td><td>Loading skeletons</td></tr>
  <tr><td>Stripes</td><td>Active progress bars</td></tr>
  <tr><td>Conic gradient rotation</td><td>Loading spinners</td></tr>
  <tr><td>Diagonal sweep</td><td>Hero highlight effects</td></tr>
</table>
<p>Animating background position is GPU-accelerated &mdash; smooth even on lower-powered devices.</p>
'''

ANSWERS[89] = r'''
<p>Layer a <code>linear-gradient</code> over an image using the multiple backgrounds syntax:</p>
<pre><code>&lt;div class="hero"&gt;Text over gradient over image&lt;/div&gt;
&lt;div class="overlay-card"&gt;Photo with subtle vignette&lt;/div&gt;

&lt;style&gt;
  .hero {
    /* Stack: gradient on top, image underneath */
    background:
      linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
      url("/images/landscape.jpg");
    background-size: cover;
    background-position: center;
    height: 400px;
    color: white;
    padding: 2em;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2em;
  }

  .overlay-card {
    background:
      linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.7) 100%),
      url("/images/photo.jpg");
    background-size: cover;
    height: 300px;
    color: white;
    padding: 1em;
    display: flex;
    align-items: flex-end;
  }
&lt;/style&gt;</code></pre>
<p><strong>Key insight:</strong> the <code>background</code> property accepts comma-separated layers. Order matters &mdash; <strong>the first listed is on top</strong>.</p>
<p><strong>Common patterns:</strong></p>
<pre><code>/* Solid dark overlay for text legibility */
background:
  linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
  url("hero.jpg");

/* Bottom-only fade (Netflix-style) */
background:
  linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.9)),
  url("show.jpg");

/* Brand-color tint */
background:
  linear-gradient(rgba(0, 102, 204, 0.6), rgba(0, 102, 204, 0.6)),
  url("photo.jpg");

/* Vignette effect (radial dark edges) */
background:
  radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.5) 100%),
  url("photo.jpg");</code></pre>
<p><strong>Why this works:</strong> CSS gradients are images. The browser layers them like Photoshop layers &mdash; each can be a gradient, an image, or a solid color (via the <code>background-color</code> longhand). Combining them lets you achieve sophisticated visual effects with no extra image processing.</p>
'''

ANSWERS[90] = r'''
<p>Use <code>grid-template-columns</code> and <code>grid-template-rows</code> together to create a multi-cell grid:</p>
<pre><code>&lt;div class="grid-3x4"&gt;
  &lt;div&gt;1&lt;/div&gt;&lt;div&gt;2&lt;/div&gt;&lt;div&gt;3&lt;/div&gt;
  &lt;div&gt;4&lt;/div&gt;&lt;div&gt;5&lt;/div&gt;&lt;div&gt;6&lt;/div&gt;
  &lt;div&gt;7&lt;/div&gt;&lt;div&gt;8&lt;/div&gt;&lt;div&gt;9&lt;/div&gt;
  &lt;div&gt;10&lt;/div&gt;&lt;div&gt;11&lt;/div&gt;&lt;div&gt;12&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .grid-3x4 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);     /* 3 equal columns */
    grid-template-rows: repeat(4, 100px);       /* 4 rows of 100px */
    gap: 1em;
  }
  .grid-3x4 &gt; div {
    background: #0066cc;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }
&lt;/style&gt;</code></pre>
<p><strong>Spanning multiple cells</strong> &mdash; some items take more space:</p>
<pre><code>&lt;style&gt;
  .grid-dashboard {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: 200px 200px;
    gap: 1em;
  }
  .featured {
    grid-column: 1 / 3;       /* span columns 1-2 */
    grid-row: 1 / 3;           /* span rows 1-2 */
    background: #ff6b35;
  }
  .wide {
    grid-column: 3 / 5;       /* span columns 3-4 */
  }
&lt;/style&gt;</code></pre>
<p><strong>Responsive: change layout per breakpoint</strong>:</p>
<pre><code>.grid-dashboard {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
  .grid-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
  .featured {
    grid-column: 1 / 3;       /* span both columns */
    grid-row: auto;            /* reset row span */
  }
}

@media (max-width: 480px) {
  .grid-dashboard {
    grid-template-columns: 1fr;
  }
  .featured {
    grid-column: 1 / -1;
    grid-row: auto;
  }
}</code></pre>
<p><code>repeat(N, 1fr)</code> creates N equal-width columns. <code>auto-fit</code> + <code>minmax</code> creates fluid responsive grids without media queries.</p>
'''

ANSWERS[91] = r'''
<p>Two main techniques: <code>fill</code> for inline SVG, and CSS filters for SVGs loaded as images.</p>
<p><strong>Inline SVG &mdash; use <code>fill</code> or <code>currentColor</code>:</strong></p>
<pre><code>&lt;svg class="icon" viewBox="0 0 24 24"&gt;
  &lt;path d="M12 2L2 22h20L12 2z"/&gt;
&lt;/svg&gt;

&lt;style&gt;
  .icon {
    width: 24px;
    height: 24px;
    fill: #0066cc;        /* color the path */
  }

  .icon:hover {
    fill: #ff6b35;
  }
&lt;/style&gt;</code></pre>
<p><strong>The <code>currentColor</code> trick</strong> &mdash; SVG inherits the parent&rsquo;s text color:</p>
<pre><code>&lt;button class="btn"&gt;
  &lt;svg viewBox="0 0 24 24" fill="currentColor"&gt;
    &lt;path d="..."/&gt;
  &lt;/svg&gt;
  Click me
&lt;/button&gt;

&lt;style&gt;
  .btn {
    color: #0066cc;          /* drives both text AND icon */
    transition: color 0.2s;
  }
  .btn:hover {
    color: #ff6b35;          /* both change together */
  }
  .btn svg {
    width: 16px;
    height: 16px;
  }
&lt;/style&gt;</code></pre>
<p>This is the cleanest pattern &mdash; one color property drives both the icon and the text, and they always match.</p>
<p><strong>Multi-color SVG with CSS variables:</strong></p>
<pre><code>&lt;svg class="logo" viewBox="0 0 100 100"&gt;
  &lt;rect width="100" height="100" fill="var(--primary)"/&gt;
  &lt;circle cx="50" cy="50" r="20" fill="var(--accent)"/&gt;
&lt;/svg&gt;

&lt;style&gt;
  .logo {
    --primary: #0066cc;
    --accent: white;
  }
&lt;/style&gt;</code></pre>
<p><strong>SVG loaded as <code>&lt;img&gt;</code></strong> can&rsquo;t be styled directly &mdash; the image is opaque to CSS. Workarounds:</p>
<ul>
  <li>Use CSS <code>filter</code> for color shifts: <code>filter: brightness(0) invert(1);</code> turns black to white.</li>
  <li>Use a CSS <code>mask</code>: <code>mask: url(icon.svg); background: blue;</code>.</li>
  <li>Inline the SVG markup directly &mdash; the most flexible option.</li>
</ul>
<p>For full styling control, always inline SVG. Loading as <code>&lt;img&gt;</code> is best for decorative graphics that don&rsquo;t need theming.</p>
'''

ANSWERS[92] = r'''
<p>Combine <code>@keyframes</code> with <code>transform: translateY()</code> for a bouncing effect:</p>
<pre><code>&lt;div class="bounce-ball"&gt;&lt;/div&gt;
&lt;div class="loading-dots"&gt;
  &lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;&lt;span&gt;&lt;/span&gt;
&lt;/div&gt;

&lt;style&gt;
  /* Single bouncing ball */
  .bounce-ball {
    width: 40px;
    height: 40px;
    background: #0066cc;
    border-radius: 50%;
    animation: bounce 1s ease-in-out infinite;
  }

  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
      animation-timing-function: ease-out;
    }
    50% {
      transform: translateY(-50px);
      animation-timing-function: ease-in;
    }
  }

  /* Three-dot loader */
  .loading-dots {
    display: flex;
    gap: 0.5em;
  }
  .loading-dots span {
    width: 12px;
    height: 12px;
    background: #0066cc;
    border-radius: 50%;
    animation: bounce-dot 1s infinite;
  }
  .loading-dots span:nth-child(2) { animation-delay: 0.15s; }
  .loading-dots span:nth-child(3) { animation-delay: 0.3s; }

  @keyframes bounce-dot {
    0%, 100% { transform: translateY(0); }
    40%      { transform: translateY(-10px); }
  }
&lt;/style&gt;</code></pre>
<p><strong>Realistic physics</strong> &mdash; ease-out going up, ease-in coming down (mimics gravity):</p>
<pre><code>@keyframes realistic-bounce {
  0%   { transform: translateY(0);     animation-timing-function: ease-out; }
  50%  { transform: translateY(-100px); animation-timing-function: ease-in; }
  55%  { transform: translateY(-100px); }   /* slight pause at peak */
  100% { transform: translateY(0); }
}</code></pre>
<p><strong>Stagger animations</strong> &mdash; <code>animation-delay</code> creates a wave effect:</p>
<pre><code>.dots span:nth-child(1) { animation-delay: 0s; }
.dots span:nth-child(2) { animation-delay: 0.15s; }
.dots span:nth-child(3) { animation-delay: 0.3s; }</code></pre>
<p>Each dot starts its bounce slightly later, creating a satisfying "wave" loader pattern.</p>
<p><strong>Performance:</strong> <code>transform</code> is GPU-accelerated &mdash; bounces stay smooth even on weak devices, unlike animating <code>top</code> or <code>margin</code>.</p>
'''

ANSWERS[93] = r'''
<p>Use the <code>border</code> property on <code>&lt;td&gt;</code> and <code>&lt;th&gt;</code>. Combine with <code>border-collapse</code> on the table for clean single borders:</p>
<pre><code>&lt;table&gt;
  &lt;tr&gt;
    &lt;th&gt;Header 1&lt;/th&gt;&lt;th&gt;Header 2&lt;/th&gt;&lt;th&gt;Header 3&lt;/th&gt;
  &lt;/tr&gt;
  &lt;tr&gt;
    &lt;td&gt;Cell 1&lt;/td&gt;&lt;td&gt;Cell 2&lt;/td&gt;&lt;td&gt;Cell 3&lt;/td&gt;
  &lt;/tr&gt;
&lt;/table&gt;

&lt;style&gt;
  table {
    border-collapse: collapse;        /* single borders, no doubled */
    width: 100%;
  }

  th, td {
    border: 1px solid #ddd;
    padding: 0.75em 1em;
  }

  th {
    background: #f5f5f5;
    font-weight: bold;
  }
&lt;/style&gt;</code></pre>
<p><strong>Different border styles per cell:</strong></p>
<pre><code>/* First column gets a thicker left border */
td:first-child {
  border-left: 3px solid #0066cc;
}

/* Headers get a darker bottom border */
th {
  border-bottom: 2px solid #333;
}

/* Last row gets no bottom border */
tr:last-child td {
  border-bottom: none;
}</code></pre>
<p><strong>Hover effect on cells:</strong></p>
<pre><code>td {
  border: 1px solid #eee;
  transition: background 0.2s;
}
td:hover {
  background: #f0f8ff;
}</code></pre>
<p><strong>Borders only between cells (no outer)</strong> &mdash; common modern look:</p>
<pre><code>table {
  border-collapse: collapse;
}
td, th {
  border-bottom: 1px solid #eee;
  padding: 0.75em 1em;
}
tr:last-child td {
  border-bottom: none;     /* remove bottom border on last row */
}</code></pre>
<p>Always use <code>border-collapse: collapse</code> &mdash; without it, every cell&rsquo;s border is independent, creating an ugly doubled-border appearance.</p>
'''

ANSWERS[94] = r'''
<p>Use Flexbox with <code>flex: 1</code> on each item to distribute space equally:</p>
<pre><code>&lt;div class="equal-cols"&gt;
  &lt;div class="col"&gt;Column 1&lt;/div&gt;
  &lt;div class="col"&gt;Column 2&lt;/div&gt;
  &lt;div class="col"&gt;Column 3&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .equal-cols {
    display: flex;
    gap: 1em;
  }
  .col {
    flex: 1;                  /* each takes equal share */
    background: #f5f5f5;
    padding: 1em;
    border-radius: 4px;
  }

  /* Mobile: stack */
  @media (max-width: 600px) {
    .equal-cols {
      flex-direction: column;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>How <code>flex: 1</code> works:</strong> shorthand for <code>flex-grow: 1; flex-shrink: 1; flex-basis: 0%</code>. Each item starts with no preferred size and grows equally to fill all available space &mdash; resulting in equal widths regardless of content.</p>
<p><strong>Equal columns even with unequal content:</strong></p>
<pre><code>.col {
  flex: 1 1 0;              /* equal regardless of content */
  min-width: 0;             /* allow shrinking */
}</code></pre>
<p><strong>4 equal columns:</strong></p>
<pre><code>.equal-4 {
  display: flex;
  gap: 1em;
}
.equal-4 &gt; * {
  flex: 1;
}</code></pre>
<p><strong>Tricky: equal width with different sizes hint:</strong></p>
<pre><code>/* These have ratios 1:2:1 */
.col-1 { flex: 1; }
.col-2 { flex: 2; }    /* gets twice as much */
.col-3 { flex: 1; }</code></pre>
<p><strong>Wrap on narrower screens</strong>:</p>
<pre><code>.cols-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}
.cols-wrap &gt; * {
  flex: 1 1 250px;          /* min 250px before wrapping */
}</code></pre>
<p>For pure equal columns with no wrap, <code>flex: 1</code>; for responsive equal-or-wrap, <code>flex: 1 1 250px</code>.</p>
'''

ANSWERS[95] = r'''
<p>Use the <code>:active</code> pseudo-class for the click state. It applies during the active mouse press:</p>
<pre><code>&lt;button class="btn"&gt;Click me&lt;/button&gt;
&lt;a href="#" class="link"&gt;Click link&lt;/a&gt;

&lt;style&gt;
  .btn {
    background: #0066cc;
    color: white;
    padding: 0.75em 1.5em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .btn:hover  { background: #0055aa; }
  .btn:active { background: #ff6b35; }       /* changes during click */
&lt;/style&gt;</code></pre>
<p><strong>Visual click feedback</strong> &mdash; combine color + scale for a "press" effect:</p>
<pre><code>.btn-press {
  background: #0066cc;
  color: white;
  padding: 0.75em 1.5em;
  border: none;
  transition: all 0.1s;
}
.btn-press:active {
  background: #ff6b35;
  transform: scale(0.97);     /* slight squish */
}</code></pre>
<p><strong>Toggle on click using <code>:checked</code></strong> &mdash; persists state without JavaScript:</p>
<pre><code>&lt;input type="checkbox" id="toggle" hidden&gt;
&lt;label for="toggle" class="toggle-label"&gt;Click to toggle&lt;/label&gt;

&lt;style&gt;
  .toggle-label {
    display: inline-block;
    background: #ccc;
    padding: 0.5em 1em;
    cursor: pointer;
    transition: background 0.2s;
  }
  /* Style label when checkbox is checked (clicked) */
  #toggle:checked + .toggle-label {
    background: #ff6b35;
    color: white;
  }
&lt;/style&gt;</code></pre>
<p>The hidden checkbox tracks click state; the label visually represents it. Each click toggles between the two states.</p>
<p><strong>JavaScript click handler</strong> for richer behavior:</p>
<pre><code>&lt;script&gt;
  document.querySelector(".btn").addEventListener("click", e =&gt; {
    e.target.classList.toggle("active");
  });
&lt;/script&gt;

&lt;style&gt;
  .btn.active { background: #ff6b35; }
&lt;/style&gt;</code></pre>
<p>Use <code>:active</code> for transient feedback (during click); use a class toggle for persistent state changes.</p>
'''

ANSWERS[96] = r'''
<p>Use <code>transform: scaleX(-1)</code> for horizontal flip or <code>scaleY(-1)</code> for vertical:</p>
<pre><code>&lt;img class="flip-h" src="arrow.png" alt=""&gt;
&lt;img class="flip-v" src="arrow.png" alt=""&gt;
&lt;img class="flip-both" src="arrow.png" alt=""&gt;
&lt;img class="flip-3d" src="card.png" alt=""&gt;

&lt;style&gt;
  /* Horizontal flip (mirror) */
  .flip-h {
    transform: scaleX(-1);
  }

  /* Vertical flip (upside down) */
  .flip-v {
    transform: scaleY(-1);
  }

  /* Both: 180&deg; rotation effect */
  .flip-both {
    transform: scale(-1, -1);
    /* equivalent to: transform: rotate(180deg); */
  }

  /* 3D card flip on hover */
  .flip-3d {
    transition: transform 0.6s;
    transform-style: preserve-3d;
  }
  .flip-3d:hover {
    transform: rotateY(180deg);
  }
&lt;/style&gt;</code></pre>
<p><strong>Common use cases:</strong></p>
<table>
  <tr><th>Flip type</th><th>Use case</th></tr>
  <tr><td>Horizontal</td><td>Right arrow → left arrow</td></tr>
  <tr><td>Vertical</td><td>Reflection effect, upside-down icons</td></tr>
  <tr><td>3D rotateY</td><td>Card flip animation</td></tr>
  <tr><td>3D rotateX</td><td>Top-to-bottom flip</td></tr>
</table>
<p><strong>Flip card with both faces:</strong></p>
<pre><code>&lt;div class="flip-card"&gt;
  &lt;div class="card-front"&gt;Front&lt;/div&gt;
  &lt;div class="card-back"&gt;Back&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .flip-card {
    position: relative;
    width: 200px;
    height: 200px;
    transform-style: preserve-3d;
    transition: transform 0.8s;
  }
  .flip-card:hover {
    transform: rotateY(180deg);
  }
  .card-front, .card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;     /* hide when facing away */
  }
  .card-front { background: #0066cc; color: white; }
  .card-back  {
    background: #ff6b35;
    color: white;
    transform: rotateY(180deg);
  }
&lt;/style&gt;</code></pre>
<p><code>backface-visibility: hidden</code> hides the back of each face when it&rsquo;s facing away &mdash; essential for clean card flip animations.</p>
'''

ANSWERS[97] = r'''
<p>Use <code>max-width</code> on the container so it grows up to a limit, then stays fixed:</p>
<pre><code>&lt;div class="container"&gt;
  Content stays max 1200px wide on big screens, fills small screens.
&lt;/div&gt;

&lt;style&gt;
  .container {
    max-width: 1200px;        /* never wider than 1200px */
    width: 100%;               /* full available width below that */
    margin: 0 auto;            /* horizontally centered */
    padding: 0 1em;            /* breathing room on small screens */
  }
&lt;/style&gt;</code></pre>
<p><strong>The pattern explained:</strong></p>
<ul>
  <li><code>max-width: 1200px</code> &mdash; container caps at 1200px on wide screens.</li>
  <li><code>width: 100%</code> &mdash; below 1200px, fills the parent (full width).</li>
  <li><code>margin: 0 auto</code> &mdash; centers horizontally when narrower than parent.</li>
  <li><code>padding: 0 1em</code> &mdash; prevents content touching screen edges on mobile.</li>
</ul>
<p><strong>Common widths and their use cases:</strong></p>
<table>
  <tr><th>max-width</th><th>Used for</th></tr>
  <tr><td><code>640px</code></td><td>Reading-optimized articles (single column)</td></tr>
  <tr><td><code>800px</code></td><td>Long-form blog posts</td></tr>
  <tr><td><code>1024px</code></td><td>Standard page content</td></tr>
  <tr><td><code>1200px</code></td><td>Most marketing sites</td></tr>
  <tr><td><code>1440px</code></td><td>App dashboards, wide layouts</td></tr>
</table>
<p><strong>Multiple breakpoints</strong> &mdash; design system "container" class:</p>
<pre><code>.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 1em;
}

@media (min-width: 640px)  { .container { max-width: 640px; padding: 0 1.5em; } }
@media (min-width: 768px)  { .container { max-width: 768px; } }
@media (min-width: 1024px) { .container { max-width: 1024px; } }
@media (min-width: 1280px) { .container { max-width: 1280px; padding: 0 2em; } }</code></pre>
<p>Tailwind&rsquo;s <code>container</code> class works exactly this way &mdash; auto-applying breakpoint-specific max widths.</p>
'''

ANSWERS[98] = r'''
<p>Animate the <code>height</code> property in <code>@keyframes</code>. Animating between fixed pixel values is straightforward:</p>
<pre><code>&lt;div class="grow-shrink"&gt;Watch me grow&lt;/div&gt;

&lt;style&gt;
  .grow-shrink {
    width: 200px;
    height: 100px;
    background: #0066cc;
    color: white;
    padding: 1em;
    animation: grow 2s ease-in-out infinite alternate;
  }

  @keyframes grow {
    from { height: 100px; }
    to   { height: 200px; }
  }
&lt;/style</code></pre>
<p><strong>Animating to/from <code>auto</code></strong> doesn&rsquo;t work directly &mdash; CSS can&rsquo;t animate between explicit values and <code>auto</code>. The modern fix uses the new <code>interpolate-size</code> property (2024+):</p>
<pre><code>:root {
  interpolate-size: allow-keywords;
}

.collapsible {
  height: 0;
  overflow: hidden;
  transition: height 0.3s;
}
.collapsible.open {
  height: auto;
}</code></pre>
<p><strong>For older browsers,</strong> animate <code>max-height</code> with a "large enough" value:</p>
<pre><code>.collapsible {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.collapsible.open {
  max-height: 1000px;     /* set generously larger than possible content */
}</code></pre>
<p>The trick: animating <code>max-height</code> appears to expand smoothly because the actual height (controlled by content) is less than the max. The animation duration may complete before reaching the max, looking near-instant for short content &mdash; tune by adjusting the max value.</p>
<p><strong>Modern alternative: <code>::details-content</code></strong> for accordion-style panels (well-supported in 2026):</p>
<pre><code>details::details-content {
  height: 0;
  overflow: hidden;
  transition: height 0.3s, content-visibility 0.3s allow-discrete;
}
details[open]::details-content {
  height: auto;
}</code></pre>
<p>Native disclosure animations &mdash; no JavaScript or hacks needed.</p>
'''

ANSWERS[99] = r'''
<p>Apply <code>box-shadow</code> on the base button, then change it on <code>:hover</code> with a transition:</p>
<pre><code>&lt;button class="btn-shadow"&gt;Hover for shadow&lt;/button&gt;
&lt;button class="btn-lift"&gt;Lift on hover&lt;/button&gt;

&lt;style&gt;
  /* Subtle shadow grows on hover */
  .btn-shadow {
    background: #0066cc;
    color: white;
    padding: 0.75em 1.5em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s, transform 0.2s;
  }
  .btn-shadow:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  /* Lift effect (translate + shadow) */
  .btn-lift {
    background: #ff6b35;
    color: white;
    padding: 0.75em 1.5em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }
  .btn-lift:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  }
  .btn-lift:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
&lt;/style&gt;</code></pre>
<p><strong>Material Design elevation pattern:</strong></p>
<pre><code>.btn-elevated {
  /* Resting elevation: 2dp */
  box-shadow:
    0 2px 2px 0 rgba(0, 0, 0, 0.14),
    0 1px 5px 0 rgba(0, 0, 0, 0.12);
  transition: box-shadow 0.2s ease;
}

.btn-elevated:hover {
  /* Hover elevation: 4dp */
  box-shadow:
    0 4px 5px 0 rgba(0, 0, 0, 0.14),
    0 1px 10px 0 rgba(0, 0, 0, 0.12);
}

.btn-elevated:active {
  /* Pressed: 8dp */
  box-shadow:
    0 8px 10px 1px rgba(0, 0, 0, 0.14),
    0 3px 14px 2px rgba(0, 0, 0, 0.12);
}</code></pre>
<p>Material Design uses two stacked shadows for realism &mdash; a darker close shadow + a softer wider one. Each elevation level intensifies both. Subtle but noticeably premium.</p>
<p><strong>Animation tip:</strong> always apply <code>transition</code> to the BASE selector so it animates in both directions (hover-in AND hover-out).</p>
'''

ANSWERS[100] = r'''
<p>CSS Grid with <code>grid-template-columns</code> + <code>auto</code> + <code>1fr</code> creates a flexible-width sidebar with a fluid main content area:</p>
<pre><code>&lt;div class="layout"&gt;
  &lt;aside class="sidebar"&gt;
    &lt;nav&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="#"&gt;Dashboard&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Projects&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Settings&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/aside&gt;

  &lt;main&gt;
    &lt;h1&gt;Main content&lt;/h1&gt;
    &lt;p&gt;Content fills the remaining space...&lt;/p&gt;
  &lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: grid;
    grid-template-columns: minmax(200px, 250px) 1fr;
    gap: 2em;
    min-height: 100vh;
  }
  .sidebar {
    background: #f5f5f5;
    padding: 1em;
  }
  main {
    padding: 1em 2em;
    min-width: 0;             /* allow content to shrink */
  }
  .sidebar ul {
    list-style: none;
    padding: 0;
  }
  .sidebar a {
    display: block;
    padding: 0.5em;
    color: #333;
    text-decoration: none;
    border-radius: 4px;
  }
  .sidebar a:hover {
    background: #e9ecef;
  }

  /* Mobile: stack vertically */
  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Why <code>minmax(200px, 250px) 1fr</code>?</strong></p>
<ul>
  <li><strong>Sidebar:</strong> minimum 200px (won&rsquo;t shrink below); maximum 250px (won&rsquo;t grow beyond).</li>
  <li><strong>Main:</strong> takes all remaining space (<code>1fr</code>).</li>
  <li>Result: stable sidebar width with main content adapting to viewport.</li>
</ul>
<p><strong>Collapsible variant</strong> &mdash; toggle between full and icon-only sidebar:</p>
<pre><code>.layout {
  grid-template-columns: 250px 1fr;
  transition: grid-template-columns 0.3s;
}
.layout.collapsed {
  grid-template-columns: 60px 1fr;
}
.collapsed .sidebar .label {
  display: none;             /* hide text in collapsed mode */
}</code></pre>
<p><strong>Add a sticky sidebar</strong>:</p>
<pre><code>.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow-y: auto;
}</code></pre>
<p>Sidebar stays visible while main content scrolls &mdash; common dashboard pattern.</p>
'''
