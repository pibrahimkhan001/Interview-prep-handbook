"""Detailed answers for CSS Basic questions."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>CSS</strong> stands for <strong>Cascading Style Sheets</strong>. It&rsquo;s the standard language used to control the visual presentation of HTML documents &mdash; colors, fonts, spacing, layout, animations, and responsive behavior.</p>

<p><strong>The three pillars of the web</strong> have separate concerns:</p>
<ul>
  <li><strong>HTML</strong> &mdash; structure and content (headings, paragraphs, lists).</li>
  <li><strong>CSS</strong> &mdash; presentation and layout (how things look).</li>
  <li><strong>JavaScript</strong> &mdash; behavior (what happens when users interact).</li>
</ul>

<pre><code>/* CSS rule structure */
selector {
  property: value;
  property: value;
}

/* Example */
h1 {
  color: navy;
  font-size: 32px;
}</code></pre>

<p><strong>Why "Cascading"?</strong> Multiple style rules can match the same element from different sources (browser defaults, external stylesheets, inline styles). The cascade defines which rule wins based on specificity, source order, and importance.</p>

<p>CSS makes the web flexible: the same HTML can look completely different across themes, devices, and contexts &mdash; just by swapping stylesheets. The current standard is CSS3, but in practice the spec is now modular and continuously updated by the W3C.</p>
'''

ANSWERS[2] = r'''
<p>There are three ways to apply CSS to HTML, each suiting different needs.</p>

<p><strong>1. External stylesheet</strong> (the standard approach):</p>
<pre><code>&lt;!-- In your HTML &lt;head&gt; --&gt;
&lt;link rel="stylesheet" href="styles.css"&gt;</code></pre>

<p>One <code>styles.css</code> file applies to many pages &mdash; consistent styling, easy to maintain, browser-cached for performance.</p>

<p><strong>2. Internal (embedded) styles</strong> &mdash; CSS inside a <code>&lt;style&gt;</code> tag in the HTML head:</p>
<pre><code>&lt;head&gt;
  &lt;style&gt;
    h1 { color: navy; }
    p { line-height: 1.6; }
  &lt;/style&gt;
&lt;/head&gt;</code></pre>

<p>Useful for one-off pages or critical above-the-fold styles loaded inline for performance.</p>

<p><strong>3. Inline styles</strong> &mdash; on a single element:</p>
<pre><code>&lt;p style="color: red; font-weight: bold;"&gt;Important text&lt;/p&gt;</code></pre>

<p>Highest specificity but hardest to maintain. Use sparingly &mdash; for dynamic JS-set styles or email templates where stylesheets don&rsquo;t work reliably.</p>

<p><strong>Best practice:</strong> external stylesheets for everything, with rare exceptions. They keep HTML clean, enable browser caching across pages, and let designers update styles without touching markup.</p>
'''

ANSWERS[3] = r'''
<p>Both ID and class selectors target elements with specific attributes, but they have important differences in <strong>uniqueness, syntax, and specificity</strong>.</p>

<table>
  <tr><th></th><th>ID selector</th><th>Class selector</th></tr>
  <tr><td>HTML attribute</td><td><code>id</code></td><td><code>class</code></td></tr>
  <tr><td>CSS prefix</td><td><code>#</code></td><td><code>.</code></td></tr>
  <tr><td>Uniqueness</td><td>Must be unique per page</td><td>Reusable across many elements</td></tr>
  <tr><td>Specificity</td><td>Higher (100)</td><td>Lower (10)</td></tr>
  <tr><td>Multiple per element</td><td>One ID per element</td><td>Many classes per element</td></tr>
</table>

<pre><code>&lt;div id="header"&gt;Site Header&lt;/div&gt;
&lt;p class="intro"&gt;Intro paragraph&lt;/p&gt;
&lt;p class="intro"&gt;Another intro paragraph&lt;/p&gt;

#header { background: navy; }       /* matches one element */
.intro  { font-size: 1.2em; }       /* matches all elements with class="intro" */</code></pre>

<p><strong>When to use which:</strong></p>
<ul>
  <li><strong>Class</strong> &mdash; for reusable styles. Most styling should use classes.</li>
  <li><strong>ID</strong> &mdash; for unique elements like the main header, fragment anchors (<code>#section-1</code>), or hooks for JavaScript.</li>
</ul>

<p><strong>Modern best practice:</strong> avoid IDs for styling because their high specificity makes overrides difficult. Use classes instead, and reserve IDs for anchor links and JavaScript targeting.</p>
'''

ANSWERS[4] = r'''
<p>An HTML element can have multiple classes by separating them with <strong>spaces</strong> in the <code>class</code> attribute. Each class&rsquo;s styles apply to the element, with later or more specific rules taking precedence.</p>

<pre><code>&lt;button class="btn btn-primary btn-large"&gt;Submit&lt;/button&gt;</code></pre>

<pre><code>.btn         { padding: 0.5em 1em; border-radius: 4px; cursor: pointer; }
.btn-primary { background: #0066cc; color: white; }
.btn-large   { font-size: 1.2em; padding: 0.75em 1.5em; }</code></pre>

<p>The button gets <strong>all three</strong> sets of styles combined &mdash; base button styling, primary color theme, and larger sizing.</p>

<p><strong>Why this is powerful:</strong></p>
<ul>
  <li><strong>Composable design</strong> &mdash; combine small, focused classes to build varied components.</li>
  <li><strong>DRY (Don&rsquo;t Repeat Yourself)</strong> &mdash; share common styles across many elements.</li>
  <li><strong>Modular CSS</strong> &mdash; the foundation of methodologies like BEM, OOCSS, and utility frameworks like Tailwind.</li>
</ul>

<p><strong>Example with conflicting properties:</strong></p>
<pre><code>.btn-primary { background: #0066cc; }
.btn-large   { background: red; }   /* later in CSS — wins */</code></pre>

<p>If two classes set the same property, the later rule in the stylesheet wins (assuming equal specificity). Order in the HTML <code>class</code> attribute doesn&rsquo;t matter &mdash; only the order in the CSS source.</p>

<p>Modern frameworks like Tailwind take this to an extreme: <code>class="px-4 py-2 bg-blue-500 text-white rounded"</code> &mdash; many tiny classes composing each element&rsquo;s look.</p>
'''

ANSWERS[5] = r'''
<p>The CSS box model describes how every HTML element is rendered as a rectangular box with four nested layers.</p>

<table>
  <tr><th>Layer</th><th>What it is</th></tr>
  <tr><td>Content</td><td>The actual text, image, or child elements</td></tr>
  <tr><td>Padding</td><td>Space between content and border (inside)</td></tr>
  <tr><td>Border</td><td>The line around the padding</td></tr>
  <tr><td>Margin</td><td>Space outside the border (between elements)</td></tr>
</table>

<pre><code>.box {
  width: 200px;
  padding: 20px;
  border: 5px solid black;
  margin: 30px;
}</code></pre>

<p><strong>Default behavior (<code>content-box</code>):</strong> the <code>width</code> applies only to the content. Total visible width = 200 (content) + 40 (padding) + 10 (border) = 250px. Margin adds 60px more for total layout space of 310px.</p>

<p><strong>Modern preferred behavior &mdash; <code>border-box</code>:</strong></p>
<pre><code>* { box-sizing: border-box; }

.box {
  width: 200px;     /* now includes padding and border */
  padding: 20px;
  border: 5px solid black;
  /* Total visible = 200px exactly */
}</code></pre>

<p>With <code>box-sizing: border-box</code>, <code>width</code> includes padding and border &mdash; far more intuitive. Adding the universal selector at the top of every project is standard practice in 2026.</p>

<p>The browser&rsquo;s DevTools "Computed" tab shows the box model visually for any element, color-coded by layer &mdash; an essential debugging tool.</p>
'''

ANSWERS[6] = r'''
<p>Centering horizontally is one of CSS&rsquo;s most common tasks. The right approach depends on what you&rsquo;re centering and the surrounding context.</p>

<p><strong>1. Center a block element (most common):</strong></p>
<pre><code>.container {
  width: 600px;
  margin: 0 auto;       /* auto left/right margins center it */
}</code></pre>

<p>Works for any block element with a defined width. The <code>auto</code> margins absorb equal amounts of horizontal space on each side.</p>

<p><strong>2. Center inline content (text, inline-block):</strong></p>
<pre><code>.parent {
  text-align: center;   /* centers inline children */
}</code></pre>

<p><strong>3. Center with Flexbox (modern, flexible):</strong></p>
<pre><code>.parent {
  display: flex;
  justify-content: center;
}</code></pre>

<p>Centers any child element along the main axis. Add <code>align-items: center</code> for vertical centering too.</p>

<p><strong>4. Center with Grid:</strong></p>
<pre><code>.parent {
  display: grid;
  place-items: center;   /* centers both horizontally and vertically */
}</code></pre>

<p>The most concise solution for centering a single child both horizontally and vertically.</p>

<p><strong>Quick reference:</strong></p>
<table>
  <tr><th>Need</th><th>Use</th></tr>
  <tr><td>Center a fixed-width box</td><td><code>margin: 0 auto</code></td></tr>
  <tr><td>Center text inside a container</td><td><code>text-align: center</code></td></tr>
  <tr><td>Center children flexibly</td><td>Flexbox <code>justify-content: center</code></td></tr>
  <tr><td>Center perfectly (both axes)</td><td>Grid <code>place-items: center</code></td></tr>
</table>
'''

ANSWERS[7] = r'''
<p>The <code>background-color</code> property sets the fill behind an element&rsquo;s content and padding.</p>

<pre><code>.banner {
  background-color: #0066cc;       /* hex */
  background-color: rgb(0, 102, 204);   /* rgb */
  background-color: hsl(210, 100%, 40%); /* hsl */
  background-color: cornflowerblue; /* named color */
}</code></pre>

<p>Any of these formats produce the same blue. Pick whichever is clearest for your context:</p>
<ul>
  <li><strong>Hex</strong> &mdash; concise, designer-familiar (<code>#rrggbb</code> or short <code>#rgb</code>).</li>
  <li><strong>RGB / RGBA</strong> &mdash; intuitive when you need transparency: <code>rgba(0, 102, 204, 0.5)</code>.</li>
  <li><strong>HSL / HSLA</strong> &mdash; easier to adjust hue/saturation/lightness manually.</li>
  <li><strong>Named colors</strong> &mdash; 140+ predefined names, useful for prototyping.</li>
</ul>

<p><strong>The <code>background</code> shorthand</strong> sets multiple background properties at once:</p>
<pre><code>.hero {
  background: #0066cc url("hero.jpg") center / cover no-repeat;
  /* color | image | position / size | repeat */
}</code></pre>

<p><strong>Transparent backgrounds</strong> let underlying elements show through:</p>
<pre><code>.overlay {
  background-color: rgba(0, 0, 0, 0.5);   /* 50% black overlay */
  background-color: transparent;          /* keyword for fully transparent */
}</code></pre>

<p>The <code>background-color</code> applies to the entire box including padding (but not margin). Modern color formats like <code>oklch()</code> and the <code>color()</code> function provide perceptually uniform color spaces, increasingly supported in 2026.</p>
'''

ANSWERS[8] = r'''
<p>CSS supports many ways to specify colors. Each format has its strengths.</p>

<table>
  <tr><th>Format</th><th>Example</th><th>Notes</th></tr>
  <tr><td>Named</td><td><code>red</code>, <code>cornflowerblue</code></td><td>140+ predefined names</td></tr>
  <tr><td>Hex 6-digit</td><td><code>#ff6b35</code></td><td>Most common in design tools</td></tr>
  <tr><td>Hex 3-digit</td><td><code>#f63</code></td><td>Shorthand for <code>#ff6633</code></td></tr>
  <tr><td>Hex with alpha</td><td><code>#ff6b35cc</code></td><td>Last 2 digits = transparency</td></tr>
  <tr><td>rgb / rgba</td><td><code>rgb(255, 107, 53)</code></td><td>0-255 per channel</td></tr>
  <tr><td>hsl / hsla</td><td><code>hsl(15, 100%, 60%)</code></td><td>Hue (0-360), saturation, lightness</td></tr>
  <tr><td>oklch</td><td><code>oklch(70% 0.2 30)</code></td><td>Perceptually uniform (modern)</td></tr>
  <tr><td>currentColor</td><td><code>currentColor</code></td><td>Inherits the element&rsquo;s text color</td></tr>
</table>

<pre><code>.box {
  color: #ff6b35;                       /* hex */
  background: rgb(255, 107, 53);        /* rgb */
  border-color: hsl(15, 100%, 60%);     /* hsl */
  outline-color: oklch(70% 0.2 30);     /* oklch */
}

.icon {
  fill: currentColor;   /* SVG icons inherit text color */
}</code></pre>

<p><strong>Transparency:</strong> RGB/HSL accept an alpha channel (0-1 or 0%-100%):</p>
<pre><code>rgba(255, 107, 53, 0.5)
rgb(255 107 53 / 50%)        /* modern syntax (no comma) */
hsl(15 100% 60% / 50%)</code></pre>

<p><strong>Modern preference:</strong> <code>hsl()</code> for designs (easy to adjust shades) or <code>oklch()</code> (perceptually uniform brightness across hues). Hex remains popular because design tools (Figma, Sketch) export it by default.</p>
'''

ANSWERS[9] = r'''
<p>Make text bold with the <code>font-weight</code> property. The most common values are <code>bold</code> and numeric weights from 100-900.</p>

<pre><code>.title       { font-weight: bold; }       /* equivalent to 700 */
.heavy       { font-weight: 900; }         /* maximum weight */
.semibold    { font-weight: 600; }
.regular     { font-weight: 400; }         /* normal — default */
.light       { font-weight: 300; }
.thin        { font-weight: 100; }</code></pre>

<p><strong>Numeric weights</strong> give precise control. Common values:</p>
<table>
  <tr><th>Value</th><th>Name</th></tr>
  <tr><td>100</td><td>Thin</td></tr>
  <tr><td>300</td><td>Light</td></tr>
  <tr><td>400</td><td>Normal (regular)</td></tr>
  <tr><td>500</td><td>Medium</td></tr>
  <tr><td>600</td><td>Semibold</td></tr>
  <tr><td>700</td><td>Bold</td></tr>
  <tr><td>900</td><td>Black (heavy)</td></tr>
</table>

<p><strong>Caveat:</strong> the actual weight depends on whether the font has that weight installed. If a font only ships with regular and bold, asking for 600 falls back to the closest available (usually 700 or browser-faked synthetic bold).</p>

<p><strong>Variable fonts</strong> support any weight on a continuous scale:</p>
<pre><code>@font-face {
  font-family: "Inter";
  src: url("inter-variable.woff2") format("woff2-variations");
  font-weight: 100 900;     /* range, not single value */
}

.flexible { font-weight: 437; }   /* any value within the range */</code></pre>

<p><strong>Don&rsquo;t use <code>&lt;b&gt;</code> for emphasis</strong> &mdash; use <code>&lt;strong&gt;</code> in HTML for semantic emphasis (also bold by default), or use CSS classes for purely visual bold without semantic meaning.</p>
'''

ANSWERS[10] = r'''
<p>Use the <code>border</code> property (or its individual longhand properties) to draw a line around an element.</p>

<p><strong>Shorthand</strong> &mdash; sets width, style, and color in one declaration:</p>
<pre><code>.box {
  border: 2px solid #333;
}</code></pre>

<p><strong>Longhand</strong> &mdash; control each side independently:</p>
<pre><code>.box {
  border-top:    1px solid red;
  border-right:  2px dashed blue;
  border-bottom: 3px dotted green;
  border-left:   4px double orange;
}</code></pre>

<p><strong>Border style values:</strong></p>
<table>
  <tr><th>Style</th><th>Result</th></tr>
  <tr><td><code>solid</code></td><td>Continuous line</td></tr>
  <tr><td><code>dashed</code></td><td>Series of dashes</td></tr>
  <tr><td><code>dotted</code></td><td>Series of dots</td></tr>
  <tr><td><code>double</code></td><td>Two parallel lines</td></tr>
  <tr><td><code>groove</code> / <code>ridge</code></td><td>3D effect (dated)</td></tr>
  <tr><td><code>none</code></td><td>No border</td></tr>
</table>

<p><strong>Rounded corners</strong> with <code>border-radius</code>:</p>
<pre><code>.card {
  border: 1px solid #ddd;
  border-radius: 8px;            /* same on all 4 corners */
}

.pill {
  border-radius: 999px;          /* fully rounded sides */
}

.fancy {
  border-radius: 10px 20px 30px 40px;   /* TL TR BR BL */
}</code></pre>

<p><strong>Border affects layout</strong> &mdash; without <code>box-sizing: border-box</code>, the border adds to the element&rsquo;s total size. Most modern projects set <code>box-sizing: border-box</code> globally to avoid this.</p>

<p>For decorative borders, also consider <code>outline</code> (doesn&rsquo;t affect layout) or <code>box-shadow</code> with spread (more flexible).</p>
'''

ANSWERS[11] = r'''
<p>Both <code>margin</code> and <code>padding</code> create space around content, but they sit on opposite sides of the border.</p>

<table>
  <tr><th></th><th>Padding</th><th>Margin</th></tr>
  <tr><td>Position</td><td>Inside the border</td><td>Outside the border</td></tr>
  <tr><td>Background</td><td>Filled with element&rsquo;s background</td><td>Transparent (always)</td></tr>
  <tr><td>Adds to element size</td><td>Yes (with default <code>box-sizing</code>)</td><td>No (separates from neighbors)</td></tr>
  <tr><td>Negative values</td><td>Not allowed</td><td>Allowed</td></tr>
  <tr><td>Collapses with neighbors</td><td>No</td><td>Yes (vertical margins collapse)</td></tr>
</table>

<pre><code>.card {
  padding: 20px;        /* space inside, between content and border */
  margin: 30px;         /* space outside, separating from other elements */
  border: 1px solid #ccc;
  background: lightyellow;
}</code></pre>

<p>Only the padding shows the yellow background; margin remains transparent.</p>

<p><strong>Shorthand syntax</strong> &mdash; same for both:</p>
<pre><code>padding: 10px;                    /* all 4 sides */
padding: 10px 20px;               /* vertical horizontal */
padding: 10px 20px 30px;          /* top horizontal bottom */
padding: 10px 20px 30px 40px;     /* top right bottom left (clockwise) */</code></pre>

<p><strong>Margin collapse</strong> &mdash; vertical margins between adjacent block elements collapse to the larger of the two:</p>
<pre><code>.a { margin-bottom: 30px; }
.b { margin-top:    20px; }
/* Space between .a and .b is 30px, not 50px */</code></pre>

<p>This is intentional &mdash; designers expect typographic spacing to use the larger margin, not stack them. Padding never collapses.</p>

<p><strong>Quick rule:</strong> use padding for space inside an element (around content); use margin for space outside (between elements).</p>
'''

ANSWERS[12] = r'''
<p>The <code>box-shadow</code> property adds shadows to elements, creating depth and visual hierarchy.</p>

<pre><code>.card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  /* offset-x | offset-y | blur | color */
}</code></pre>

<p><strong>The four (or five) values:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td>offset-x</td><td>Horizontal offset (positive = right)</td></tr>
  <tr><td>offset-y</td><td>Vertical offset (positive = down)</td></tr>
  <tr><td>blur-radius</td><td>How fuzzy the shadow is (0 = sharp)</td></tr>
  <tr><td>spread-radius (optional)</td><td>How much shadow expands or contracts</td></tr>
  <tr><td>color</td><td>Shadow color (often semi-transparent black)</td></tr>
</table>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Subtle elevation */
.shallow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12); }

/* Medium card */
.medium  { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }

/* Lifted */
.deep    { box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); }

/* Glow effect */
.glow    { box-shadow: 0 0 20px rgba(0, 102, 204, 0.5); }

/* Inset shadow (inside the element) */
.pressed { box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2); }

/* Multiple shadows stacked */
.layered {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.12),
    0 1px 2px rgba(0, 0, 0, 0.24);
}</code></pre>

<p><strong>Tips for realistic shadows:</strong></p>
<ul>
  <li><strong>Use semi-transparent colors</strong> (rgba with alpha 0.1-0.3) rather than solid gray.</li>
  <li><strong>Vertical offset only</strong> for most cases &mdash; light comes from above.</li>
  <li><strong>Larger blur for higher elevation</strong> &mdash; mimics how real shadows soften with distance.</li>
  <li><strong>Stack multiple shadows</strong> for nuanced depth (Material Design uses this technique).</li>
</ul>

<p>For text, use <code>text-shadow</code> with the same syntax minus the spread parameter.</p>
'''

ANSWERS[13] = r'''
<p>CSS supports two main gradient functions for background images: <code>linear-gradient()</code> and <code>radial-gradient()</code>. Both are technically images, used wherever an image URL works.</p>

<p><strong>Linear gradient</strong> &mdash; transitions colors along a line:</p>
<pre><code>.banner {
  background: linear-gradient(to right, #ff6b35, #f7c59f);
}

.diagonal {
  background: linear-gradient(135deg, navy, skyblue);
  /* angle in degrees: 0deg = upward, 90deg = right */
}

.sunset {
  background: linear-gradient(to bottom,
    #1a2980 0%,
    #26d0ce 50%,
    #ff6b35 100%);
}</code></pre>

<p><strong>Radial gradient</strong> &mdash; transitions colors from a center point outward:</p>
<pre><code>.spotlight {
  background: radial-gradient(circle, white, lightgray);
}

.offset-radial {
  background: radial-gradient(circle at top right,
    #ff6b35,
    #1a2980 70%);
}</code></pre>

<p><strong>Direction values for linear:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td><code>to right</code></td><td>Left to right</td></tr>
  <tr><td><code>to bottom</code></td><td>Top to bottom (default)</td></tr>
  <tr><td><code>to top right</code></td><td>Diagonal corner</td></tr>
  <tr><td><code>45deg</code></td><td>Custom angle</td></tr>
</table>

<p><strong>Multi-color gradients</strong> with stop positions:</p>
<pre><code>background: linear-gradient(to right,
  red 0%, orange 25%, yellow 50%, green 75%, blue 100%);</code></pre>

<p><strong>Conic gradient</strong> for pie-chart-like effects:</p>
<pre><code>background: conic-gradient(red, yellow, green, blue, red);</code></pre>

<p><strong>Combining with images</strong> &mdash; layer gradients over background images for text overlays:</p>
<pre><code>background:
  linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
  url("hero.jpg") center / cover;</code></pre>

<p>The dark gradient over the image creates a readable backdrop for white text. Multiple backgrounds stack with the first listed on top.</p>
'''

ANSWERS[14] = r'''
<p>The <code>display</code> property defines how an element generates a box and how it interacts with surrounding content. It&rsquo;s one of the most fundamental CSS properties.</p>

<table>
  <tr><th>Value</th><th>Behavior</th></tr>
  <tr><td><code>block</code></td><td>Takes full width; new line before and after; respects width/height</td></tr>
  <tr><td><code>inline</code></td><td>Flows with text; ignores width/height/vertical margins</td></tr>
  <tr><td><code>inline-block</code></td><td>Flows like inline but respects width/height</td></tr>
  <tr><td><code>none</code></td><td>Element is removed from the layout entirely</td></tr>
  <tr><td><code>flex</code></td><td>Flexbox container for 1D layouts</td></tr>
  <tr><td><code>grid</code></td><td>Grid container for 2D layouts</td></tr>
  <tr><td><code>contents</code></td><td>Element disappears but children remain</td></tr>
</table>

<pre><code>nav        { display: block; }
span       { display: inline; }
button     { display: inline-block; }
.layout    { display: flex; }
.grid      { display: grid; }
.hidden    { display: none; }</code></pre>

<p><strong>Each element has a default <code>display</code></strong> based on its tag:</p>
<ul>
  <li><strong>Block by default:</strong> <code>div</code>, <code>p</code>, <code>h1</code>-<code>h6</code>, <code>section</code>, <code>article</code>, <code>nav</code>, <code>li</code>.</li>
  <li><strong>Inline by default:</strong> <code>span</code>, <code>a</code>, <code>strong</code>, <code>em</code>, <code>img</code>.</li>
  <li><strong>Inline-block by default:</strong> <code>button</code>, <code>input</code>, <code>textarea</code>.</li>
</ul>

<p><strong>Toggle visibility</strong>:</p>
<pre><code>.toggle-hidden { display: none; }       /* removed from layout */
.toggle-visible { display: block; }     /* restored */</code></pre>

<p><code>display: none</code> hides the element completely &mdash; it takes no space and isn&rsquo;t accessible to screen readers. Use <code>visibility: hidden</code> if you want to hide while preserving space.</p>
'''

ANSWERS[15] = r'''
<p>CSS offers several ways to hide elements, each with different effects on layout and accessibility. Choose the right one based on intent.</p>

<table>
  <tr><th>Method</th><th>Layout space</th><th>Screen reader access</th><th>Use case</th></tr>
  <tr><td><code>display: none</code></td><td>None</td><td>Hidden</td><td>Completely remove</td></tr>
  <tr><td><code>visibility: hidden</code></td><td>Reserved</td><td>Hidden</td><td>Hide but reserve space</td></tr>
  <tr><td><code>opacity: 0</code></td><td>Reserved</td><td>Visible</td><td>Fade animations; still focusable</td></tr>
  <tr><td><code>height: 0; overflow: hidden</code></td><td>None</td><td>Possibly visible</td><td>Collapsible sections</td></tr>
  <tr><td><code>hidden</code> attribute</td><td>None</td><td>Hidden</td><td>Same as display: none</td></tr>
  <tr><td>Visually-hidden class</td><td>None visible</td><td>Visible</td><td>Skip links, screen-reader-only text</td></tr>
</table>

<pre><code>.removed     { display: none; }
.invisible   { visibility: hidden; }
.transparent { opacity: 0; }

/* Visually hidden but accessible (the standard pattern) */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}</code></pre>

<p><strong>Use <code>display: none</code></strong> when the element shouldn&rsquo;t exist for users at all (e.g., closed accordion content, toggled sections).</p>

<p><strong>Use <code>visibility: hidden</code></strong> for cases where you want layout space preserved (e.g., placeholder for content that will appear later).</p>

<p><strong>Use the <code>sr-only</code> pattern</strong> for content that should be invisible but accessible to screen readers (skip links, icon labels, descriptive text).</p>

<p><strong>Critical:</strong> never hide focusable elements (links, buttons, inputs) with just <code>opacity: 0</code> &mdash; they&rsquo;re still tabbable and clickable, creating "phantom" interactions. Add <code>pointer-events: none</code> and <code>aria-hidden="true"</code> if you must use opacity.</p>
'''

ANSWERS[16] = r'''
<p>Hover effects use the <code>:hover</code> pseudo-class to apply styles when the user&rsquo;s cursor is over an element. Combined with <code>transition</code>, they animate smoothly.</p>

<pre><code>.button {
  background: #0066cc;
  color: white;
  padding: 0.5em 1em;
  border-radius: 4px;
  transition: background 0.2s, transform 0.1s;
}

.button:hover {
  background: #0055aa;       /* darker on hover */
  transform: translateY(-2px); /* slight lift */
}

.button:active {
  transform: translateY(0);   /* press down on click */
}</code></pre>

<p><strong>Common hover effects:</strong></p>
<pre><code>/* Color change */
a:hover { color: navy; }

/* Underline appears */
.link:hover { text-decoration: underline; }

/* Scale up */
.card:hover { transform: scale(1.05); }

/* Shadow lift */
.card:hover { box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); }

/* Reveal hidden content */
.parent:hover .child { opacity: 1; }</code></pre>

<p><strong>The <code>transition</code> property</strong> makes hover changes smooth instead of instant:</p>
<pre><code>.button {
  transition: background 0.2s ease, transform 0.1s ease;
  /* property | duration | timing-function */
}</code></pre>

<p>Without <code>transition</code>, the change happens immediately when the cursor enters; with it, the change animates over the specified duration.</p>

<p><strong>Touch device caveat:</strong> there&rsquo;s no hover on touch screens. Use <code>@media (hover: hover)</code> to scope hover effects:</p>
<pre><code>@media (hover: hover) {
  .button:hover { transform: scale(1.05); }
}</code></pre>

<p>This prevents touch users from getting "stuck" hover states after tapping. Always provide focus styles too (<code>:focus-visible</code>) so keyboard users get the same feedback.</p>
'''

ANSWERS[17] = r'''
<p>Inline and block are the two fundamental display modes in HTML/CSS. Understanding the difference is essential for layout.</p>

<table>
  <tr><th></th><th>Inline</th><th>Block</th></tr>
  <tr><td>Layout</td><td>Flows in line with text</td><td>Stacks vertically; full width</td></tr>
  <tr><td>Width / height</td><td>Ignored (uses content size)</td><td>Respected</td></tr>
  <tr><td>Vertical margin</td><td>Ignored</td><td>Respected</td></tr>
  <tr><td>Horizontal margin</td><td>Respected</td><td>Respected</td></tr>
  <tr><td>Default examples</td><td><code>span</code>, <code>a</code>, <code>strong</code>, <code>em</code></td><td><code>div</code>, <code>p</code>, <code>h1</code>, <code>section</code></td></tr>
</table>

<pre><code>&lt;p&gt;
  Block paragraph contains
  &lt;span&gt;an inline span&lt;/span&gt;
  and
  &lt;strong&gt;inline strong text&lt;/strong&gt;.
&lt;/p&gt;

&lt;style&gt;
  /* This won&rsquo;t work — span ignores width */
  span { width: 200px; }

  /* But this works — block elements respect width */
  p { width: 600px; }
&lt;/style&gt;</code></pre>

<p><strong>Visual difference:</strong></p>
<ul>
  <li><strong>Inline:</strong> like words in a sentence &mdash; multiple sit on one line.</li>
  <li><strong>Block:</strong> like paragraphs &mdash; each on its own line, full container width.</li>
</ul>

<p><strong>Inline-block</strong> &mdash; the hybrid:</p>
<pre><code>span.button {
  display: inline-block;
  width: 100px;
  padding: 10px;
}</code></pre>

<p>Inline-block flows like inline text (multiple per line) but respects width/height like block. Useful for navigation items, buttons in a row, and badges.</p>

<p><strong>Convert with display:</strong></p>
<pre><code>span.special { display: block; }       /* span becomes block */
div.inline   { display: inline; }      /* div becomes inline (rare) */
nav a        { display: inline-block; } /* anchors become click-target boxes */</code></pre>

<p>Modern layouts mostly use <code>display: flex</code> or <code>display: grid</code>, but understanding inline vs block is still essential for text formatting and form elements.</p>
'''

ANSWERS[18] = r'''
<p>The <code>font-size</code> property controls how large text renders. CSS supports multiple unit types &mdash; choose the right one for your context.</p>

<pre><code>.large    { font-size: 32px; }       /* absolute pixels */
.medium   { font-size: 1.5em; }      /* relative to parent */
.small    { font-size: 1rem; }       /* relative to root */
.fluid    { font-size: 4vw; }        /* viewport width */
.named    { font-size: x-large; }    /* keyword */</code></pre>

<p><strong>The unit options:</strong></p>
<table>
  <tr><th>Unit</th><th>Relative to</th><th>Best for</th></tr>
  <tr><td><code>px</code></td><td>Absolute</td><td>Borders, fine-tuning</td></tr>
  <tr><td><code>em</code></td><td>Parent&rsquo;s font-size</td><td>Spacing scaled with text</td></tr>
  <tr><td><code>rem</code></td><td>Root <code>&lt;html&gt;</code> font-size</td><td>Most modern designs</td></tr>
  <tr><td><code>%</code></td><td>Parent&rsquo;s font-size</td><td>Older patterns</td></tr>
  <tr><td><code>vw</code> / <code>vh</code></td><td>Viewport size</td><td>Fluid hero text</td></tr>
  <tr><td><code>ch</code></td><td>Width of "0" character</td><td>Setting line widths</td></tr>
</table>

<p><strong>Rem is the modern default.</strong> Set base size on <code>:root</code>, then size everything in rem:</p>
<pre><code>:root { font-size: 16px; }    /* 1rem = 16px */

h1 { font-size: 2.5rem; }      /* 40px */
p  { font-size: 1rem; }        /* 16px */
.small { font-size: 0.875rem; } /* 14px */</code></pre>

<p>Users who change browser font size in accessibility settings see the whole site scale &mdash; impossible with px-everywhere designs.</p>

<p><strong>Fluid typography with <code>clamp()</code>:</strong></p>
<pre><code>h1 {
  font-size: clamp(1.5rem, 4vw + 1rem, 3.5rem);
  /* min: 1.5rem, scales with viewport, max: 3.5rem */
}</code></pre>

<p>One line replaces multiple media queries &mdash; text scales smoothly between minimum and maximum sizes based on viewport width.</p>
'''

ANSWERS[19] = r'''
<p>Make images responsive so they scale to fit their container without breaking layout. The standard pattern is two CSS rules.</p>

<pre><code>img {
  max-width: 100%;
  height: auto;
}</code></pre>

<p><strong>Why both:</strong></p>
<ul>
  <li><code>max-width: 100%</code> &mdash; image never grows wider than its container, but can be smaller.</li>
  <li><code>height: auto</code> &mdash; preserves aspect ratio when width changes.</li>
</ul>

<p>This single rule applied globally handles 95% of responsive image cases.</p>

<p><strong>Always include <code>width</code> and <code>height</code> attributes</strong> in HTML to prevent layout shift:</p>
<pre><code>&lt;img src="hero.jpg" alt="Hero" width="1200" height="600"&gt;</code></pre>

<p>The browser uses these to reserve correctly-proportioned space before the image loads. Combined with <code>height: auto</code> CSS, the image shows correctly while preventing CLS (Cumulative Layout Shift).</p>

<p><strong>For different viewport sizes</strong>, use <code>srcset</code> to serve smaller images on smaller screens:</p>
<pre><code>&lt;img src="hero-medium.jpg"
     srcset="hero-small.jpg 600w,
             hero-medium.jpg 1200w,
             hero-large.jpg 2400w"
     sizes="(max-width: 600px) 100vw, 1200px"
     alt="Hero"
     width="1200" height="600"&gt;</code></pre>

<p>The browser picks the best image based on viewport width and pixel density &mdash; phones download a 600px image, retina laptops get 2400px.</p>

<p><strong>Object-fit for cropping behavior:</strong></p>
<pre><code>.thumbnail {
  width: 200px;
  height: 200px;
  object-fit: cover;     /* crops to fill the box */
  /* alternatives: contain (letterbox), fill (stretch), none */
}</code></pre>

<p>Useful when images need consistent dimensions but shouldn&rsquo;t be distorted. Modern formats (WebP, AVIF) save 30-70% file size with the same visual quality.</p>
'''

ANSWERS[20] = r'''
<p>The <code>position</code> property controls how an element is positioned in the document flow. It has five main values, each with distinct behavior.</p>

<table>
  <tr><th>Value</th><th>Behavior</th></tr>
  <tr><td><code>static</code></td><td>Default &mdash; normal document flow; ignores top/right/bottom/left</td></tr>
  <tr><td><code>relative</code></td><td>Stays in flow but offset from its normal position</td></tr>
  <tr><td><code>absolute</code></td><td>Removed from flow; positioned relative to nearest positioned ancestor</td></tr>
  <tr><td><code>fixed</code></td><td>Removed from flow; positioned relative to the viewport</td></tr>
  <tr><td><code>sticky</code></td><td>Hybrid &mdash; relative until scrolled past a threshold, then fixed</td></tr>
</table>

<pre><code>.normal     { position: static; }                          /* default */
.offset     { position: relative; top: 10px; left: 20px; } /* offset from normal */
.float-card { position: absolute; top: 0; right: 0; }      /* relative to ancestor */
.always-top { position: fixed; top: 0; left: 0; right: 0; } /* relative to viewport */
.sticky-nav { position: sticky; top: 0; }                  /* sticks on scroll */</code></pre>

<p><strong>Positioning context</strong> &mdash; <code>absolute</code> elements look upward in the DOM for a positioned ancestor:</p>
<pre><code>.parent {
  position: relative;     /* establishes positioning context */
}
.parent .badge {
  position: absolute;
  top: 10px;
  right: 10px;            /* positioned relative to .parent */
}</code></pre>

<p>Without a positioned ancestor, <code>absolute</code> elements position relative to the viewport.</p>

<p><strong>Common patterns:</strong></p>
<ul>
  <li><strong>Fixed header:</strong> <code>position: fixed; top: 0;</code></li>
  <li><strong>Sticky table headers:</strong> <code>position: sticky; top: 0;</code></li>
  <li><strong>Tooltip / dropdown:</strong> <code>position: absolute</code> on the popover, <code>position: relative</code> on the trigger&rsquo;s parent.</li>
  <li><strong>Modal dialog:</strong> <code>position: fixed</code> with full-screen overlay.</li>
  <li><strong>Badge on card:</strong> <code>position: absolute</code> with parent having <code>position: relative</code>.</li>
</ul>

<p>Use <code>z-index</code> with positioned elements to control stacking order.</p>
'''

ANSWERS[21] = r'''
<p>A fixed header stays at the top of the viewport while the user scrolls. The standard pattern is <code>position: fixed</code> with proper offset for the content.</p>

<pre><code>&lt;header class="site-header"&gt;
  &lt;a href="/" class="logo"&gt;Acme&lt;/a&gt;
  &lt;nav&gt;
    &lt;a href="/"&gt;Home&lt;/a&gt;
    &lt;a href="/about"&gt;About&lt;/a&gt;
    &lt;a href="/contact"&gt;Contact&lt;/a&gt;
  &lt;/nav&gt;
&lt;/header&gt;

&lt;main&gt;
  &lt;!-- Lots of content --&gt;
&lt;/main&gt;

&lt;style&gt;
  .site-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: white;
    border-bottom: 1px solid #eee;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    z-index: 100;
    display: flex;
    align-items: center;
    padding: 0 1em;
  }

  /* Critical: pad the main content so it&rsquo;s not hidden under the header */
  main {
    padding-top: 60px;
  }
&lt;/style&gt;</code></pre>

<p><strong>The most common bug: forgetting the offset.</strong> Without <code>padding-top: 60px</code> on <code>main</code>, the first 60px of content sits behind the fixed header on page load &mdash; invisible.</p>

<p><strong>Modern alternative: <code>position: sticky</code></strong> &mdash; often a better choice:</p>
<pre><code>.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  /* Same other styles */
}
/* No padding-top needed on main — sticky takes natural space first */</code></pre>

<p><strong>Sticky vs fixed:</strong></p>
<table>
  <tr><th></th><th><code>fixed</code></th><th><code>sticky</code></th></tr>
  <tr><td>Layout space</td><td>None (need to offset content)</td><td>Reserved naturally</td></tr>
  <tr><td>Always visible</td><td>Yes</td><td>Only after scroll threshold</td></tr>
  <tr><td>Use when</td><td>Header must always show</td><td>Header can scroll with hero, then stick</td></tr>
</table>

<p><strong>Use <code>z-index</code></strong> high enough that the header stays above all content; <code>100</code> is a common convention.</p>
'''

ANSWERS[22] = r'''
<p>Pseudo-classes are keywords added to selectors that target an element in a specific <strong>state</strong> &mdash; not a different element, but the same element under certain conditions.</p>

<pre><code>a:hover        { color: red; }       /* when hovered */
a:focus        { outline: 2px solid blue; }   /* when focused */
a:visited      { color: purple; }    /* after the user clicked */
a:active       { color: orange; }    /* while being clicked */
input:disabled { opacity: 0.5; }     /* when disabled */
input:checked  { border-color: green; } /* checkbox/radio when checked */</code></pre>

<p><strong>The most common pseudo-classes:</strong></p>
<table>
  <tr><th>Pseudo-class</th><th>Matches</th></tr>
  <tr><td><code>:hover</code></td><td>Cursor over element</td></tr>
  <tr><td><code>:focus</code></td><td>Element has keyboard/JS focus</td></tr>
  <tr><td><code>:focus-visible</code></td><td>Focus from keyboard (not mouse)</td></tr>
  <tr><td><code>:active</code></td><td>Currently being clicked/pressed</td></tr>
  <tr><td><code>:visited</code></td><td>Link the user has visited</td></tr>
  <tr><td><code>:checked</code></td><td>Checked checkbox/radio</td></tr>
  <tr><td><code>:disabled</code> / <code>:enabled</code></td><td>Form element state</td></tr>
  <tr><td><code>:required</code> / <code>:optional</code></td><td>Form field requirement</td></tr>
  <tr><td><code>:first-child</code> / <code>:last-child</code></td><td>Position among siblings</td></tr>
  <tr><td><code>:nth-child(n)</code></td><td>Nth sibling (1-indexed)</td></tr>
  <tr><td><code>:not(selector)</code></td><td>Element NOT matching selector</td></tr>
  <tr><td><code>:empty</code></td><td>No children or text</td></tr>
</table>

<p><strong>Combining pseudo-classes:</strong></p>
<pre><code>button:hover:not(:disabled) {
  background: blue;
}

li:nth-child(odd) {
  background: #f5f5f5;
}

input:invalid:not(:placeholder-shown) {
  border-color: red;
}</code></pre>

<p><strong>Pseudo-classes vs pseudo-elements:</strong></p>
<ul>
  <li><strong>Pseudo-class</strong> (<code>:hover</code>) &mdash; targets an element in a state.</li>
  <li><strong>Pseudo-element</strong> (<code>::before</code>) &mdash; creates a virtual element.</li>
</ul>

<p>Single colon for pseudo-classes; double colon for pseudo-elements (modern syntax).</p>
'''

ANSWERS[23] = r'''
<p>Two pseudo-classes target the first child element: <code>:first-child</code> matches the first sibling regardless of type, while <code>:first-of-type</code> matches the first sibling of a specific type.</p>

<pre><code>li:first-child {
  font-weight: bold;
  color: navy;
}

p:first-of-type {
  font-size: 1.2em;
  margin-top: 0;
}</code></pre>

<p><strong>The difference matters when siblings have mixed types:</strong></p>
<pre><code>&lt;article&gt;
  &lt;h2&gt;Title&lt;/h2&gt;
  &lt;p&gt;First paragraph&lt;/p&gt;     &lt;!-- :first-of-type matches this --&gt;
  &lt;p&gt;Second paragraph&lt;/p&gt;
&lt;/article&gt;

&lt;style&gt;
  /* Doesn&rsquo;t match anything — the first child is &lt;h2&gt;, not &lt;p&gt; */
  p:first-child { color: red; }

  /* Matches "First paragraph" */
  p:first-of-type { color: red; }
&lt;/style&gt;</code></pre>

<p><strong>The rule:</strong> <code>:first-child</code> is strict &mdash; if the first sibling isn&rsquo;t of the type you&rsquo;re targeting, nothing matches. <code>:first-of-type</code> finds the first occurrence of that type.</p>

<p><strong>Common use cases:</strong></p>
<pre><code>/* No top margin on first paragraph (avoid double spacing) */
article p:first-of-type {
  margin-top: 0;
}

/* Bold the first item in any list */
ul li:first-child {
  font-weight: bold;
}

/* Special styling for the article&rsquo;s first heading */
article h2:first-of-type {
  font-size: 2em;
}</code></pre>

<p><strong>Related pseudo-classes:</strong></p>
<ul>
  <li><code>:last-child</code> / <code>:last-of-type</code> &mdash; the last sibling.</li>
  <li><code>:only-child</code> / <code>:only-of-type</code> &mdash; element is the only child.</li>
  <li><code>:nth-child(1)</code> &mdash; equivalent to <code>:first-child</code>.</li>
  <li><code>:first</code> &mdash; this is for paged media (print), not normal pages.</li>
</ul>

<p>For more complex cases, use <code>:nth-child()</code> or <code>:nth-of-type()</code> with formulas like <code>2n+1</code> (odd) or <code>3n</code> (every third).</p>
'''

ANSWERS[24] = r'''
<p>Both <code>:nth-child()</code> and <code>:nth-of-type()</code> match elements based on their position among siblings, but they count differently.</p>

<table>
  <tr><th></th><th><code>:nth-child(n)</code></th><th><code>:nth-of-type(n)</code></th></tr>
  <tr><td>Counts</td><td>All siblings</td><td>Only siblings of same type</td></tr>
  <tr><td>Position must match</td><td>Yes &mdash; AND type must match</td><td>Type checked, then nth among that type</td></tr>
  <tr><td>Use when</td><td>Position regardless of mixed types</td><td>Targeting specific type</td></tr>
</table>

<pre><code>&lt;article&gt;
  &lt;h2&gt;Title&lt;/h2&gt;          &lt;!-- 1st child overall, 1st h2 --&gt;
  &lt;p&gt;Para A&lt;/p&gt;            &lt;!-- 2nd child overall, 1st p --&gt;
  &lt;p&gt;Para B&lt;/p&gt;            &lt;!-- 3rd child overall, 2nd p --&gt;
  &lt;p&gt;Para C&lt;/p&gt;            &lt;!-- 4th child overall, 3rd p --&gt;
&lt;/article&gt;

&lt;style&gt;
  /* :nth-child(2) — the 2nd child of any type */
  p:nth-child(2) {
    color: red;          /* matches Para A (it IS the 2nd child AND is a p) */
  }

  /* :nth-child(1) p */
  p:nth-child(1) {
    color: blue;         /* matches NOTHING — the 1st child is h2, not p */
  }

  /* :nth-of-type(1) — the 1st p among all paragraphs */
  p:nth-of-type(1) {
    color: green;        /* matches Para A (the 1st p) */
  }

  /* Highlight every other paragraph */
  p:nth-of-type(odd) {
    background: #f5f5f5;
  }
&lt;/style&gt;</code></pre>

<p><strong>Common formulas:</strong></p>
<table>
  <tr><th>Formula</th><th>Matches</th></tr>
  <tr><td><code>1</code> or <code>2</code></td><td>The exact child</td></tr>
  <tr><td><code>odd</code></td><td>Odd-numbered children (1, 3, 5...)</td></tr>
  <tr><td><code>even</code></td><td>Even-numbered (2, 4, 6...)</td></tr>
  <tr><td><code>2n+1</code></td><td>Same as odd</td></tr>
  <tr><td><code>3n</code></td><td>Every third (3, 6, 9...)</td></tr>
  <tr><td><code>n+3</code></td><td>3rd onward</td></tr>
  <tr><td><code>-n+3</code></td><td>First 3</td></tr>
</table>

<p><strong>Quick rule:</strong></p>
<ul>
  <li>If your siblings are uniform (all <code>li</code> in a list), either works the same.</li>
  <li>If types are mixed (h2 + p in an article), use <code>:nth-of-type</code> for safer targeting.</li>
</ul>
'''

ANSWERS[25] = r'''
<p>Set <code>cursor: pointer</code> on an element to show the hand-pointer cursor on hover &mdash; the universal "this is clickable" indicator.</p>

<pre><code>.button {
  cursor: pointer;
}

.disabled {
  cursor: not-allowed;
}</code></pre>

<p><strong>Common cursor values:</strong></p>
<table>
  <tr><th>Value</th><th>Indicates</th></tr>
  <tr><td><code>pointer</code></td><td>Clickable (hand)</td></tr>
  <tr><td><code>default</code></td><td>Standard arrow</td></tr>
  <tr><td><code>text</code></td><td>Editable text (I-beam)</td></tr>
  <tr><td><code>wait</code></td><td>Loading (spinner)</td></tr>
  <tr><td><code>help</code></td><td>Help available (question mark)</td></tr>
  <tr><td><code>not-allowed</code></td><td>Action prohibited</td></tr>
  <tr><td><code>grab</code> / <code>grabbing</code></td><td>Draggable elements</td></tr>
  <tr><td><code>crosshair</code></td><td>Precision selection</td></tr>
  <tr><td><code>move</code></td><td>Element can be moved</td></tr>
  <tr><td><code>zoom-in</code> / <code>zoom-out</code></td><td>Zoomable</td></tr>
</table>

<p><strong>Important: native <code>&lt;button&gt;</code> doesn&rsquo;t show pointer cursor by default in browsers.</strong> You usually want to add it:</p>
<pre><code>button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
}</code></pre>

<p><strong>Real anchor links (<code>&lt;a href&gt;</code>)</strong> automatically get the pointer cursor &mdash; no CSS needed.</p>

<p><strong>Custom cursor images:</strong></p>
<pre><code>.special {
  cursor: url("custom.png") 4 4, auto;
  /* image | hotspot x y | fallback */
}</code></pre>

<p>Useful for games and creative tools, but custom cursors can confuse users in regular interfaces &mdash; use sparingly.</p>

<p><strong>Best practice:</strong> the cursor should always match what happens on click. <code>pointer</code> for clickable; <code>not-allowed</code> for disabled buttons; <code>text</code> for editable areas. Mismatches confuse users about whether something is interactive.</p>
'''

ANSWERS[26] = r'''
<p>The <code>:nth-of-type()</code> pseudo-class targets elements based on their position among <strong>siblings of the same tag type</strong>, while <code>:nth-child()</code> counts all children regardless of type.</p>

<p>This question often duplicates Q24 in different phrasing &mdash; both are about the same distinction. Here&rsquo;s a focused recap with practical patterns.</p>

<pre><code>&lt;ul&gt;
  &lt;li&gt;First&lt;/li&gt;
  &lt;li&gt;Second&lt;/li&gt;
  &lt;li&gt;Third&lt;/li&gt;
  &lt;li&gt;Fourth&lt;/li&gt;
  &lt;li&gt;Fifth&lt;/li&gt;
&lt;/ul&gt;

&lt;style&gt;
  /* Striped rows */
  li:nth-of-type(odd) {
    background: #f5f5f5;
  }

  /* Highlight every third item */
  li:nth-of-type(3n) {
    color: navy;
  }

  /* The 4th and beyond */
  li:nth-of-type(n+4) {
    font-style: italic;
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>n</code> formulas:</strong></p>
<table>
  <tr><th>Formula</th><th>Matches</th></tr>
  <tr><td><code>3</code></td><td>The 3rd sibling only</td></tr>
  <tr><td><code>3n</code></td><td>Every 3rd: 3, 6, 9...</td></tr>
  <tr><td><code>3n+1</code></td><td>Starting at 1, every 3rd: 1, 4, 7...</td></tr>
  <tr><td><code>n+3</code></td><td>From 3rd onward: 3, 4, 5...</td></tr>
  <tr><td><code>-n+3</code></td><td>First 3: 1, 2, 3</td></tr>
  <tr><td><code>odd</code> / <code>even</code></td><td>Same as <code>2n+1</code> / <code>2n</code></td></tr>
</table>

<p><strong>Real-world striped table example:</strong></p>
<pre><code>tbody tr:nth-of-type(even) {
  background: #f9f9f9;
}
tbody tr:hover {
  background: #e6f3ff;
}</code></pre>

<p>The combination produces alternating-row striping with hover highlight &mdash; a standard accessible table pattern.</p>

<p><strong>Modern <code>:nth-child(of selector)</code></strong> &mdash; widely supported in 2026:</p>
<pre><code>li:nth-child(odd of .visible) {
  background: yellow;
}</code></pre>

<p>This filters first by selector (<code>.visible</code>), then counts among the matches &mdash; previously impossible without JavaScript.</p>
'''

ANSWERS[27] = r'''
<p>Already covered in Q25 &mdash; this question repeats the cursor topic. Here&rsquo;s a quick reference focused on the use case.</p>

<pre><code>.clickable {
  cursor: pointer;
}</code></pre>

<p><strong>Apply to:</strong></p>
<ul>
  <li>Any clickable element that doesn&rsquo;t have it natively (<code>div</code>, <code>span</code>, <code>li</code>).</li>
  <li><code>&lt;button&gt;</code> elements (counterintuitively, browsers don&rsquo;t apply pointer by default).</li>
  <li>Custom widgets with <code>onclick</code> handlers.</li>
  <li>Images that link or trigger actions.</li>
</ul>

<p><strong>Don&rsquo;t apply to:</strong></p>
<ul>
  <li>Plain text that isn&rsquo;t clickable (confuses users).</li>
  <li>Disabled controls (use <code>cursor: not-allowed</code> instead).</li>
  <li>Form text inputs (the default <code>text</code> cursor is correct).</li>
</ul>

<p><strong>Best practice example:</strong></p>
<pre><code>/* Standard button styling baseline */
button {
  cursor: pointer;
  border: none;
  padding: 0.5em 1em;
  border-radius: 4px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Custom clickable card */
.card[role="button"] {
  cursor: pointer;
}</code></pre>

<p>Always pair clickable cursors with proper accessibility (role attributes, keyboard handlers, focus styles) so the visual affordance matches functional behavior.</p>
'''

ANSWERS[28] = r'''
<p>Use a <strong>type selector</strong> &mdash; just the tag name itself &mdash; to target every element of that type.</p>

<pre><code>p {
  line-height: 1.6;
  color: #333;
}

img {
  max-width: 100%;
  height: auto;
}

button {
  cursor: pointer;
  font-family: inherit;
}</code></pre>

<p>These rules apply to <strong>every</strong> matching element on the page. Type selectors have low specificity (1), so class and ID selectors easily override them.</p>

<p><strong>Universal selector</strong> targets all elements:</p>
<pre><code>* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}</code></pre>

<p>Common at the top of stylesheets to reset browser defaults. The <code>*</code> matches every element.</p>

<p><strong>Combining type with descendants/children:</strong></p>
<pre><code>article p { font-size: 1.1em; }              /* every p inside article */
nav &gt; ul { list-style: none; }                /* direct child ul of nav */
section + section { margin-top: 2em; }       /* section after another section */
h2 ~ p { color: #666; }                       /* p after h2 (siblings) */</code></pre>

<p><strong>Multiple types share styles:</strong></p>
<pre><code>h1, h2, h3, h4, h5, h6 {
  font-family: "Inter", sans-serif;
  line-height: 1.2;
}</code></pre>

<p>The comma is "OR" &mdash; styles apply to any element matching any selector in the list.</p>

<p><strong>Caution:</strong> broad type selectors (<code>* { ... }</code> with many properties) can have performance implications on huge pages. Modern browsers handle this well, but resetting too aggressively can override useful defaults you&rsquo;ll then need to reapply (focus rings, button styles).</p>
'''

ANSWERS[29] = r'''
<p>The <code>z-index</code> property controls the <strong>stacking order</strong> of positioned elements &mdash; which appears in front when boxes overlap. Higher values appear above lower ones.</p>

<pre><code>.modal {
  position: fixed;
  z-index: 1000;       /* on top of most content */
}

.dropdown {
  position: absolute;
  z-index: 100;
}

.tooltip {
  position: absolute;
  z-index: 50;
}</code></pre>

<p><strong>Critical rules:</strong></p>
<ul>
  <li><strong><code>z-index</code> only works on positioned elements</strong> &mdash; <code>relative</code>, <code>absolute</code>, <code>fixed</code>, <code>sticky</code>. <code>position: static</code> (the default) ignores z-index.</li>
  <li><strong>Default value is <code>auto</code></strong> &mdash; the element stacks based on document order.</li>
  <li><strong>Negative values</strong> place elements below their stacking context root.</li>
  <li><strong>Stacking contexts</strong> are isolated &mdash; a child&rsquo;s z-index can&rsquo;t escape its parent&rsquo;s stacking context.</li>
</ul>

<p><strong>Stacking contexts</strong> are created by:</p>
<ul>
  <li><code>position</code> + <code>z-index</code> (any non-auto value).</li>
  <li><code>opacity</code> less than 1.</li>
  <li><code>transform</code>, <code>filter</code>, <code>perspective</code> (any non-default value).</li>
  <li><code>isolation: isolate</code>.</li>
  <li><code>will-change</code> certain properties.</li>
</ul>

<p><strong>The "z-index war" anti-pattern:</strong></p>
<pre><code>/* DON&rsquo;T do this */
.thing { z-index: 999; }
.other { z-index: 9999; }
.modal { z-index: 99999; }
.urgent { z-index: 999999; }</code></pre>

<p>Manage z-index with a sensible scale instead:</p>
<pre><code>:root {
  --z-base: 1;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 1000;
  --z-toast: 2000;
}

.dropdown { z-index: var(--z-dropdown); }
.modal    { z-index: var(--z-modal); }</code></pre>

<p>Defining z-index tiers as variables prevents arbitrary value escalation. Modern <code>position: fixed</code> dialogs and the Popover API automatically use the top layer, eliminating most z-index needs.</p>
'''

ANSWERS[30] = r'''
<p>Create a flex container by applying <code>display: flex</code> to a parent element. All direct children become flex items that lay out along a single axis (row or column).</p>

<pre><code>.container {
  display: flex;
}</code></pre>

<pre><code>&lt;div class="container"&gt;
  &lt;div&gt;Item 1&lt;/div&gt;
  &lt;div&gt;Item 2&lt;/div&gt;
  &lt;div&gt;Item 3&lt;/div&gt;
&lt;/div&gt;</code></pre>

<p>By default, items lay out in a <strong>row</strong> from left to right, each taking only as much space as its content needs.</p>

<p><strong>Key flex container properties:</strong></p>
<table>
  <tr><th>Property</th><th>Purpose</th></tr>
  <tr><td><code>flex-direction</code></td><td>Row vs column (and reversed)</td></tr>
  <tr><td><code>flex-wrap</code></td><td>Allow items to wrap onto multiple lines</td></tr>
  <tr><td><code>justify-content</code></td><td>Align items along main axis</td></tr>
  <tr><td><code>align-items</code></td><td>Align items along cross axis</td></tr>
  <tr><td><code>gap</code></td><td>Space between items</td></tr>
</table>

<pre><code>.container {
  display: flex;
  flex-direction: row;        /* row | row-reverse | column | column-reverse */
  flex-wrap: wrap;             /* nowrap | wrap | wrap-reverse */
  justify-content: center;     /* flex-start | center | flex-end | space-between | space-around | space-evenly */
  align-items: center;         /* flex-start | center | flex-end | stretch | baseline */
  gap: 1rem;                   /* space between items */
}</code></pre>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Centered content */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* Horizontal nav with logo on left, links on right */
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Wrap items into rows */
.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}</code></pre>

<p>Flexbox is ideal for one-dimensional layouts &mdash; rows or columns. For two-dimensional grids, use CSS Grid instead.</p>
'''

ANSWERS[31] = r'''
<p>Align flex items horizontally with <code>justify-content</code> on the flex container. The values control how items distribute along the main axis (the horizontal axis when <code>flex-direction: row</code>).</p>

<pre><code>.container {
  display: flex;
  justify-content: center;     /* horizontal centering */
}</code></pre>

<p><strong>The <code>justify-content</code> values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>flex-start</code></td><td>Items packed at start (default)</td></tr>
  <tr><td><code>center</code></td><td>Items centered</td></tr>
  <tr><td><code>flex-end</code></td><td>Items packed at end</td></tr>
  <tr><td><code>space-between</code></td><td>Equal space between items; first/last touch edges</td></tr>
  <tr><td><code>space-around</code></td><td>Equal space around each item (half-space at edges)</td></tr>
  <tr><td><code>space-evenly</code></td><td>Equal space between all items including edges</td></tr>
</table>

<pre><code>.left    { display: flex; justify-content: flex-start; }
.center  { display: flex; justify-content: center; }
.right   { display: flex; justify-content: flex-end; }
.spread  { display: flex; justify-content: space-between; }</code></pre>

<p><strong>Visual difference between space-between, space-around, space-evenly:</strong></p>
<pre><code>/* space-between: |item  item  item| */
/* space-around:  |  item  item  item  | */
/* space-evenly:  |  item  item  item  | */</code></pre>

<p>The difference: <code>space-between</code> has no space at edges (items hug edges); <code>space-around</code> has half-space at edges; <code>space-evenly</code> has full equal space everywhere.</p>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Logo left, nav links right */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Centered hero buttons */
.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 1em;
}

/* Right-aligned form actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5em;
}</code></pre>

<p><strong>For column direction</strong> (<code>flex-direction: column</code>), <code>justify-content</code> aligns vertically &mdash; the main axis becomes vertical. Use <code>align-items</code> for the perpendicular axis (horizontal in column mode).</p>
'''

ANSWERS[32] = r'''
<p>Create a grid layout by applying <code>display: grid</code> to a parent and defining columns and rows with <code>grid-template-columns</code> and <code>grid-template-rows</code>.</p>

<pre><code>.container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;    /* three columns: 1/4, 2/4, 1/4 */
  grid-template-rows: auto 1fr auto;      /* header, content, footer */
  gap: 1rem;
}</code></pre>

<pre><code>&lt;div class="container"&gt;
  &lt;header&gt;Header&lt;/header&gt;
  &lt;aside&gt;Sidebar&lt;/aside&gt;
  &lt;main&gt;Main content&lt;/main&gt;
  &lt;aside&gt;Right sidebar&lt;/aside&gt;
  &lt;footer&gt;Footer&lt;/footer&gt;
&lt;/div&gt;</code></pre>

<p><strong>Grid track sizing units:</strong></p>
<table>
  <tr><th>Unit</th><th>Meaning</th></tr>
  <tr><td><code>1fr</code> / <code>2fr</code></td><td>Fractional unit &mdash; remaining space divided proportionally</td></tr>
  <tr><td><code>auto</code></td><td>Fits content size</td></tr>
  <tr><td><code>200px</code></td><td>Fixed width</td></tr>
  <tr><td><code>min-content</code></td><td>Smallest content size without overflow</td></tr>
  <tr><td><code>max-content</code></td><td>Content&rsquo;s preferred size</td></tr>
  <tr><td><code>minmax(200px, 1fr)</code></td><td>At least 200px, up to 1fr</td></tr>
</table>

<p><strong>Repeat for many columns:</strong></p>
<pre><code>.gallery {
  display: grid;
  grid-template-columns: repeat(4, 1fr);                       /* 4 equal columns */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* responsive */
}</code></pre>

<p>The <code>auto-fit</code> + <code>minmax()</code> combo creates responsive grids where columns automatically wrap based on container width &mdash; no media queries needed.</p>

<p><strong>Place items in specific cells</strong> using grid lines:</p>
<pre><code>.header {
  grid-column: 1 / -1;     /* span all columns */
}
.sidebar {
  grid-column: 1;
  grid-row: 2 / 4;
}
.main {
  grid-column: 2 / 4;      /* columns 2 to 4 */
  grid-row: 2;
}</code></pre>

<p><strong>Named areas</strong> for clearer layouts:</p>
<pre><code>.layout {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  grid-template-areas:
    "header header header"
    "sidebar main aside"
    "footer footer footer";
}
.layout header  { grid-area: header; }
.layout aside.left { grid-area: sidebar; }
.layout main    { grid-area: main; }
.layout aside.right { grid-area: aside; }
.layout footer  { grid-area: footer; }</code></pre>

<p>Grid is ideal for two-dimensional layouts; Flexbox handles one-dimensional rows or columns better.</p>
'''

ANSWERS[33] = r'''
<p>The <code>width</code> and <code>height</code> properties set explicit dimensions. CSS supports many unit types &mdash; choose based on whether you need fixed, relative, or content-based sizing.</p>

<pre><code>.box {
  width: 300px;
  height: 200px;
}

.responsive {
  width: 100%;
  height: 50vh;          /* half the viewport height */
}

.flexible {
  width: clamp(200px, 50%, 600px);
}</code></pre>

<p><strong>Length units:</strong></p>
<table>
  <tr><th>Unit</th><th>Meaning</th></tr>
  <tr><td><code>px</code></td><td>Absolute pixels</td></tr>
  <tr><td><code>%</code></td><td>Percentage of parent</td></tr>
  <tr><td><code>em</code></td><td>Relative to parent&rsquo;s font-size</td></tr>
  <tr><td><code>rem</code></td><td>Relative to root font-size</td></tr>
  <tr><td><code>vw</code> / <code>vh</code></td><td>Viewport width/height (1% of)</td></tr>
  <tr><td><code>auto</code></td><td>Browser computes from content</td></tr>
  <tr><td><code>fit-content</code></td><td>Content size, capped to available</td></tr>
</table>

<p><strong>Min and max constraints:</strong></p>
<pre><code>.constrained {
  width: 100%;
  max-width: 1200px;       /* never wider than 1200px */
  min-width: 300px;        /* never narrower than 300px */
}

.tall {
  min-height: 100vh;       /* at least full viewport */
}</code></pre>

<p>The <code>max-width</code> + percentage pattern is how most responsive containers work &mdash; fluid up to a maximum.</p>

<p><strong>The <code>aspect-ratio</code> property</strong> sets one dimension based on the other:</p>
<pre><code>.video {
  width: 100%;
  aspect-ratio: 16 / 9;    /* height calculated automatically */
}

.square-thumbnail {
  width: 200px;
  aspect-ratio: 1;          /* same as 1/1 */
}</code></pre>

<p>Eliminates the old "padding-bottom hack" for maintaining aspect ratios.</p>

<p><strong>Box-sizing affects width interpretation</strong>:</p>
<pre><code>* { box-sizing: border-box; }   /* width includes padding and border */</code></pre>

<p>Modern projects globally set <code>box-sizing: border-box</code> for intuitive sizing &mdash; padding and border don&rsquo;t add to declared width.</p>
'''

ANSWERS[34] = r'''
<p>Apply a background image with <code>background-image: url(...)</code>. Combine with sizing, positioning, and repeat properties for full control.</p>

<pre><code>.hero {
  background-image: url("hero.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  min-height: 500px;
}</code></pre>

<p><strong>The full set of background properties:</strong></p>
<table>
  <tr><th>Property</th><th>Purpose</th></tr>
  <tr><td><code>background-image</code></td><td>The image URL (or gradient)</td></tr>
  <tr><td><code>background-size</code></td><td><code>cover</code>, <code>contain</code>, or specific dimensions</td></tr>
  <tr><td><code>background-position</code></td><td>Where the image anchors (<code>center</code>, <code>top left</code>)</td></tr>
  <tr><td><code>background-repeat</code></td><td><code>no-repeat</code>, <code>repeat</code>, <code>repeat-x</code>, <code>repeat-y</code></td></tr>
  <tr><td><code>background-attachment</code></td><td><code>fixed</code> (parallax), <code>scroll</code>, <code>local</code></td></tr>
  <tr><td><code>background-clip</code></td><td>Limit background to <code>border-box</code>, <code>padding-box</code>, <code>content-box</code></td></tr>
</table>

<p><strong>Shorthand</strong> &mdash; combine multiple properties:</p>
<pre><code>.hero {
  background: url("hero.jpg") center / cover no-repeat;
  /* image | position / size | repeat */
}</code></pre>

<p><strong>Add a dark overlay for text readability</strong> &mdash; layer a gradient over the image:</p>
<pre><code>.hero-with-overlay {
  background:
    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url("hero.jpg") center / cover no-repeat;
  color: white;
}</code></pre>

<p>Multiple backgrounds stack with the first listed on top &mdash; the gradient creates a translucent dark layer over the image.</p>

<p><strong>Multiple background images</strong> for parallax-style effects:</p>
<pre><code>.layered {
  background:
    url("foreground.png") bottom / cover no-repeat,
    url("background.jpg") top / cover no-repeat;
}</code></pre>

<p><strong>Accessibility note:</strong> background images are decorative &mdash; screen readers ignore them. For meaningful images, use <code>&lt;img&gt;</code> with <code>alt</code> text instead.</p>

<p>Modern formats (WebP, AVIF) save 30-70% bandwidth. Use <code>image-set()</code> for retina-aware backgrounds:</p>
<pre><code>background-image: image-set(
  "hero.webp" 1x,
  "hero@2x.webp" 2x
);</code></pre>
'''

ANSWERS[35] = r'''
<p>Specify multiple fonts in the <code>font-family</code> property &mdash; the browser uses the first one available, falling back to the next if it&rsquo;s not installed.</p>

<pre><code>body {
  font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
}

code, pre {
  font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
}</code></pre>

<p>If the user doesn&rsquo;t have Inter installed, the browser tries Helvetica Neue, then Arial, then any system sans-serif. The list is read left to right.</p>

<p><strong>Always end with a generic family</strong> as the ultimate fallback:</p>
<table>
  <tr><th>Generic</th><th>Examples</th></tr>
  <tr><td><code>serif</code></td><td>Times, Cambria</td></tr>
  <tr><td><code>sans-serif</code></td><td>Arial, Helvetica</td></tr>
  <tr><td><code>monospace</code></td><td>Courier, Consolas</td></tr>
  <tr><td><code>cursive</code></td><td>Comic Sans, script fonts</td></tr>
  <tr><td><code>system-ui</code></td><td>OS&rsquo;s native UI font</td></tr>
</table>

<p><strong>Modern system font stack</strong> &mdash; fast and OS-appropriate:</p>
<pre><code>body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
               Roboto, "Helvetica Neue", Arial, sans-serif;
}</code></pre>

<p>This stack uses each operating system&rsquo;s native font (San Francisco on macOS, Segoe UI on Windows, Roboto on Android) &mdash; no font download needed, perfect rendering.</p>

<p><strong>Quoting font names with spaces:</strong></p>
<pre><code>font-family: "Helvetica Neue";       /* spaces require quotes */
font-family: Arial;                  /* single word, optional quotes */</code></pre>

<p><strong>Loading custom fonts with <code>@font-face</code></strong>:</p>
<pre><code>@font-face {
  font-family: "MyFont";
  src: url("/fonts/myfont.woff2") format("woff2");
  font-weight: 400;
  font-display: swap;     /* show fallback while loading */
}

body {
  font-family: "MyFont", system-ui, sans-serif;
}</code></pre>

<p><code>font-display: swap</code> shows the fallback font immediately and swaps to the custom font when loaded &mdash; prevents the dreaded "FOIT" (flash of invisible text) where the page is unreadable while fonts load.</p>
'''

ANSWERS[36] = r'''
<p>Make text italic with <code>font-style: italic</code>. The property has three valid values.</p>

<pre><code>.italic    { font-style: italic; }
.regular   { font-style: normal; }     /* default */
.oblique   { font-style: oblique; }    /* slanted, similar to italic */</code></pre>

<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>normal</code></td><td>Upright text (default)</td></tr>
  <tr><td><code>italic</code></td><td>Italic style of the font (if available)</td></tr>
  <tr><td><code>oblique</code></td><td>Synthetic slant (browser slants the regular font)</td></tr>
</table>

<p><strong>Italic vs oblique:</strong> true italic uses a separately-designed italic font face with cursive flourishes. Oblique just slants the regular font &mdash; less elegant but available for any font. Use <code>italic</code>; browsers fall back to oblique if italic isn&rsquo;t available.</p>

<p><strong>Don&rsquo;t use <code>&lt;i&gt;</code> for emphasis</strong> &mdash; use <code>&lt;em&gt;</code> in HTML for semantic emphasis (also italic by default), or use CSS for purely visual italics:</p>
<pre><code>.tagline {
  font-style: italic;
  color: #666;
}</code></pre>

<p><strong>Variable fonts</strong> support italic on a continuous slant axis:</p>
<pre><code>.fancy {
  font-variation-settings: "slnt" -10;   /* -10deg slant */
}</code></pre>

<p>Some variable fonts have an italic axis you can adjust precisely &mdash; from upright (0) to fully italic (-15 or so).</p>

<p><strong>Combining with other text properties:</strong></p>
<pre><code>.quote {
  font-style: italic;
  font-weight: normal;
  font-size: 1.1em;
  color: #555;
  border-left: 3px solid #ddd;
  padding-left: 1em;
}</code></pre>

<p>Italic text often signals quotes, foreign words, technical terms, or titles of works. Pair with semantic HTML (<code>&lt;cite&gt;</code> for titles, <code>&lt;dfn&gt;</code> for definitions) for full meaning.</p>
'''

ANSWERS[37] = r'''
<p>The <code>float</code> property removes an element from normal flow and pushes it to the left or right side of its container, with surrounding content wrapping around it. Originally used for layout; mostly replaced by Flexbox and Grid in modern CSS.</p>

<pre><code>.image-left {
  float: left;
  margin-right: 1em;
  margin-bottom: 0.5em;
}

.image-right {
  float: right;
  margin-left: 1em;
  margin-bottom: 0.5em;
}</code></pre>

<pre><code>&lt;img class="image-left" src="photo.jpg" alt="..."&gt;
&lt;p&gt;This text wraps around the floated image,
   flowing naturally beside it. Floats were
   originally designed for this magazine-style
   layout where text flows around figures.&lt;/p&gt;</code></pre>

<p><strong>Float values:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>left</code></td><td>Push to left; content wraps right</td></tr>
  <tr><td><code>right</code></td><td>Push to right; content wraps left</td></tr>
  <tr><td><code>none</code></td><td>Default; no floating</td></tr>
</table>

<p><strong>Modern, valid use case</strong> &mdash; magazine-style images with text wrap:</p>
<pre><code>article img {
  float: left;
  margin: 0 1em 1em 0;
  max-width: 50%;
}</code></pre>

<p>This pattern works well; floats remain the right tool for "text flows around an image" effects.</p>

<p><strong>Outdated uses</strong> (don&rsquo;t do these in 2026):</p>
<ul>
  <li><strong>Multi-column layouts</strong> &mdash; use Flexbox or Grid instead.</li>
  <li><strong>Centering</strong> &mdash; use <code>margin: 0 auto</code> or Flexbox.</li>
  <li><strong>Equal-height columns</strong> &mdash; use Grid.</li>
  <li><strong>Sidebar + main</strong> &mdash; use Grid template columns.</li>
</ul>

<p>Floats came from print-design conventions before CSS had real layout primitives. Pre-2017, every site used float-based grid systems (Bootstrap 3, foundation). Today, Flexbox handles 1D layouts and Grid handles 2D layouts &mdash; floats are reserved for text wrap around figures.</p>

<p><strong>One quirk:</strong> floats are removed from normal flow but still affect text. The parent doesn&rsquo;t expand to contain floated children &mdash; you need to "clear" them.</p>
'''

ANSWERS[38] = r'''
<p>When elements are floated, their parent often "collapses" because floats are removed from normal flow. Clear the floats so the parent contains them properly.</p>

<p><strong>Three common methods:</strong></p>

<p><strong>1. Clear after the floats:</strong></p>
<pre><code>&lt;div class="parent"&gt;
  &lt;img class="floated" src="..." alt="..."&gt;
  &lt;p&gt;Text...&lt;/p&gt;
  &lt;div class="clear"&gt;&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .clear { clear: both; }
&lt;/style&gt;</code></pre>

<p>The <code>clear</code> property pushes the element below any floats. Adds an extra empty div &mdash; not ideal.</p>

<p><strong>2. Clearfix hack</strong> (the modern preferred approach):</p>
<pre><code>.clearfix::after {
  content: "";
  display: block;
  clear: both;
}</code></pre>

<p>Apply <code>clearfix</code> to any container with floated children. The <code>::after</code> pseudo-element provides the clear without extra HTML.</p>

<pre><code>&lt;div class="parent clearfix"&gt;
  &lt;img class="floated" src="..." alt="..."&gt;
  &lt;p&gt;Text...&lt;/p&gt;
&lt;/div&gt;</code></pre>

<p><strong>3. Establish a new block formatting context:</strong></p>
<pre><code>.parent {
  overflow: auto;     /* or hidden */
}</code></pre>

<p>This forces the parent to contain floats. Side effect: hides any content that overflows; sometimes triggers scrollbars. Use <code>overflow: hidden</code> only if no overflow is desired anyway.</p>

<p><strong>Modern alternative:</strong> use <code>display: flow-root</code> &mdash; the cleanest solution:</p>
<pre><code>.parent {
  display: flow-root;
}</code></pre>

<p><code>flow-root</code> creates a new block formatting context (containing all floats) without any side effects on overflow or scroll. It&rsquo;s the right answer in 2026 &mdash; well-supported across all modern browsers.</p>

<p><strong>Comparison:</strong></p>
<table>
  <tr><th>Method</th><th>Notes</th></tr>
  <tr><td><code>clearfix</code></td><td>Most compatible; works everywhere</td></tr>
  <tr><td><code>overflow: hidden</code></td><td>Works but may clip content</td></tr>
  <tr><td><code>display: flow-root</code></td><td>Modern, clean, no side effects</td></tr>
</table>

<p>Best practice today: avoid floats for layout entirely &mdash; Flexbox and Grid eliminate the need to clear floats. Use floats only for magazine-style text wrap, where you typically don&rsquo;t need clearing.</p>
'''

ANSWERS[39] = r'''
<p>Build a navigation bar with a <code>&lt;nav&gt;</code> element containing a list of links, then style it with Flexbox for layout.</p>

<pre><code>&lt;nav class="main-nav" aria-label="Main"&gt;
  &lt;a href="/" class="logo"&gt;Acme&lt;/a&gt;
  &lt;ul&gt;
    &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
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
  .logo {
    font-weight: bold;
    font-size: 1.2em;
    text-decoration: none;
    color: #333;
  }
  .main-nav ul {
    display: flex;
    gap: 1.5em;
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .main-nav a {
    color: #333;
    text-decoration: none;
    padding: 0.5em 0;
  }
  .main-nav a:hover {
    color: #0066cc;
  }
  .main-nav a:focus-visible {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
  }
&lt;/style&gt;</code></pre>

<p><strong>Key choices:</strong></p>
<ul>
  <li><strong>Semantic <code>&lt;nav&gt;</code> + <code>&lt;ul&gt;</code></strong> &mdash; screen readers announce the navigation region; the list structure makes accessibility tools count items.</li>
  <li><strong><code>justify-content: space-between</code></strong> &mdash; pushes logo and nav links to opposite ends.</li>
  <li><strong><code>list-style: none; padding: 0; margin: 0</code></strong> &mdash; removes default bullets and indentation.</li>
  <li><strong><code>gap: 1.5em</code></strong> &mdash; consistent spacing between nav items.</li>
  <li><strong>Hover and focus styles</strong> &mdash; visual feedback for both mouse and keyboard users.</li>
</ul>

<p><strong>Active link styling:</strong></p>
<pre><code>.main-nav a[aria-current="page"] {
  color: #0066cc;
  font-weight: 600;
  border-bottom: 2px solid #0066cc;
}</code></pre>

<p>Mark the current page with <code>aria-current="page"</code> for accessibility, then style with the attribute selector.</p>

<p><strong>For mobile</strong>, add a hamburger menu pattern using a checkbox toggle (CSS-only) or JavaScript with <code>aria-expanded</code>. Below 768px, hide the nav and show a button that toggles a slide-down menu.</p>
'''

ANSWERS[40] = r'''
<p>Remove default bullets from a list with <code>list-style: none</code> on the <code>&lt;ul&gt;</code> or <code>&lt;ol&gt;</code>.</p>

<pre><code>ul.no-bullets {
  list-style: none;
  padding: 0;            /* remove default indentation */
  margin: 0;
}</code></pre>

<p><strong>Why three properties together:</strong></p>
<ul>
  <li><code>list-style: none</code> &mdash; removes the bullet markers.</li>
  <li><code>padding: 0</code> &mdash; removes the default left-padding browsers use to make room for bullets.</li>
  <li><code>margin: 0</code> &mdash; removes default vertical margin (optional).</li>
</ul>

<p>Just <code>list-style: none</code> alone leaves the items still indented &mdash; the browser had reserved space for bullets that are no longer there.</p>

<p><strong>The <code>list-style</code> shorthand</strong> sets multiple properties:</p>
<pre><code>list-style: type position image;
list-style: disc inside;
list-style: square outside;
list-style: none;
list-style: url("custom-bullet.png") inside;</code></pre>

<table>
  <tr><th>list-style-type</th><th>Result</th></tr>
  <tr><td><code>disc</code></td><td>● Filled circle (default for ul)</td></tr>
  <tr><td><code>circle</code></td><td>○ Empty circle</td></tr>
  <tr><td><code>square</code></td><td>■ Filled square</td></tr>
  <tr><td><code>decimal</code></td><td>1, 2, 3 (default for ol)</td></tr>
  <tr><td><code>lower-roman</code></td><td>i, ii, iii</td></tr>
  <tr><td><code>upper-alpha</code></td><td>A, B, C</td></tr>
  <tr><td><code>none</code></td><td>No marker</td></tr>
</table>

<p><strong>Custom bullets with <code>::marker</code></strong>:</p>
<pre><code>li::marker {
  color: #0066cc;
  font-size: 1.2em;
  content: "&#10003; ";    /* checkmark instead of bullet */
}</code></pre>

<p>The <code>::marker</code> pseudo-element styles the bullet without removing list semantics &mdash; better for accessibility than <code>list-style: none</code> + custom <code>::before</code>.</p>

<p><strong>Common pattern: nav lists.</strong> Remove bullets when using <code>&lt;ul&gt;</code> for navigation, breadcrumbs, or social media icons:</p>
<pre><code>nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 1em;
}</code></pre>

<p>Keep using <code>&lt;ul&gt;</code>+<code>&lt;li&gt;</code> for semantic meaning even when bullets are visually hidden &mdash; screen readers benefit from list structure.</p>
'''

ANSWERS[41] = r'''
<p>The <code>opacity</code> property controls element transparency &mdash; from 0 (fully transparent) to 1 (fully opaque). It applies to the entire element including its children.</p>

<pre><code>.transparent  { opacity: 0; }       /* invisible */
.semi         { opacity: 0.5; }     /* 50% see-through */
.opaque       { opacity: 1; }       /* default; fully visible */</code></pre>

<p><strong>Visible difference:</strong></p>
<pre><code>.fade-in {
  opacity: 0;
  transition: opacity 0.3s;
}
.fade-in.visible {
  opacity: 1;
}</code></pre>

<p>Toggle the <code>visible</code> class via JavaScript to fade content in or out smoothly.</p>

<p><strong>Critical: opacity affects ALL descendants.</strong></p>
<pre><code>.parent {
  opacity: 0.5;
}
/* The parent AND every child renders at 50% opacity — you can&rsquo;t override
   opacity on a child to make it more opaque than the parent */</code></pre>

<p>If you only want the background to be transparent (not the text), use <code>rgba()</code> color instead:</p>
<pre><code>.dark-overlay {
  background: rgba(0, 0, 0, 0.5);   /* semi-transparent background */
  color: white;                       /* fully opaque text */
}</code></pre>

<p><strong>opacity vs visibility vs display:</strong></p>
<table>
  <tr><th>Property</th><th>Layout space</th><th>Interactive</th><th>Screen reader</th></tr>
  <tr><td><code>opacity: 0</code></td><td>Reserved</td><td>Yes (still clickable!)</td><td>Yes</td></tr>
  <tr><td><code>visibility: hidden</code></td><td>Reserved</td><td>No</td><td>No</td></tr>
  <tr><td><code>display: none</code></td><td>None</td><td>No</td><td>No</td></tr>
</table>

<p><strong>Important gotcha:</strong> <code>opacity: 0</code> elements are still focusable and clickable. To fully hide while keeping fade-out animation, add <code>pointer-events: none</code> and <code>aria-hidden="true"</code>.</p>

<p><strong>Common use cases:</strong></p>
<ul>
  <li>Fade-in/fade-out animations.</li>
  <li>Disabled state visual hint (<code>opacity: 0.5</code>).</li>
  <li>Modal backdrops (<code>opacity: 0.7</code> on a black overlay).</li>
  <li>Hover effects (subtle dim or highlight).</li>
</ul>

<p>Modern CSS also has <code>filter: opacity(50%)</code> &mdash; same result as <code>opacity</code> but composable with other filter effects (blur, grayscale).</p>
'''

ANSWERS[42] = r'''
<p>Make an image circular with <code>border-radius: 50%</code> &mdash; this rounds all corners by half the smaller dimension, creating a perfect circle for square images and an oval for rectangles.</p>

<pre><code>.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;        /* crops if not square */
}</code></pre>

<pre><code>&lt;img class="avatar" src="profile.jpg" alt="Jane Smith"&gt;</code></pre>

<p><strong>Three rules together for reliable circles:</strong></p>
<ul>
  <li><strong>Equal width and height</strong> &mdash; otherwise you get an oval.</li>
  <li><strong><code>border-radius: 50%</code></strong> &mdash; rounds to perfect circle.</li>
  <li><strong><code>object-fit: cover</code></strong> &mdash; crops the image to fill the box without distortion.</li>
</ul>

<p>Without <code>object-fit: cover</code>, non-square source images stretch and distort. With it, the image is centered and cropped &mdash; the visible portion is whatever fits the circle.</p>

<p><strong>Pixel-precise circular avatars:</strong></p>
<pre><code>.avatar-xs { width: 24px;  height: 24px; }
.avatar-sm { width: 32px;  height: 32px; }
.avatar-md { width: 48px;  height: 48px; }
.avatar-lg { width: 64px;  height: 64px; }
.avatar-xl { width: 96px;  height: 96px; }

.avatar-xs, .avatar-sm, .avatar-md, .avatar-lg, .avatar-xl {
  border-radius: 50%;
  object-fit: cover;
  background: #e0e0e0;       /* placeholder while loading */
}</code></pre>

<p><strong>With border:</strong></p>
<pre><code>.avatar-bordered {
  border: 3px solid white;
  box-shadow: 0 0 0 1px #ddd;
}</code></pre>

<p>The <code>box-shadow</code> with no offset creates a subtle outline outside the white border.</p>

<p><strong>Status indicator</strong> on avatar:</p>
<pre><code>.avatar-wrapper {
  position: relative;
  display: inline-block;
}
.avatar-wrapper::after {
  content: "";
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #4caf50;       /* green = online */
  border: 2px solid white;
  border-radius: 50%;
}</code></pre>

<p>Position-absolute the status dot in the corner of the avatar wrapper. Common pattern in chat apps (online/away/offline).</p>

<p><strong>For non-square circular elements</strong> (oval shapes), use <code>border-radius: 50% / 50%</code> &mdash; explicit horizontal and vertical radius.</p>
'''

ANSWERS[43] = r'''
<p>Change flex item order with the <code>order</code> property. By default, items render in source order; <code>order</code> lets you visually reorder without changing HTML.</p>

<pre><code>.container {
  display: flex;
}
.item-1 { order: 3; }
.item-2 { order: 1; }
.item-3 { order: 2; }</code></pre>

<pre><code>&lt;div class="container"&gt;
  &lt;div class="item-1"&gt;A&lt;/div&gt;
  &lt;div class="item-2"&gt;B&lt;/div&gt;
  &lt;div class="item-3"&gt;C&lt;/div&gt;
&lt;/div&gt;

&lt;!-- Visual order: B, C, A (sorted by order value) --&gt;</code></pre>

<p><strong>How it works:</strong></p>
<ul>
  <li>Default order is 0.</li>
  <li>Items sort by <code>order</code> value, ascending.</li>
  <li>Negative values are valid &mdash; <code>order: -1</code> moves an item to the front.</li>
  <li>Items with the same value keep source order among themselves.</li>
</ul>

<p><strong>Common pattern: reorder for mobile</strong>:</p>
<pre><code>.layout {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .layout {
    flex-direction: row;
  }
  .sidebar { order: 1; }    /* sidebar on left */
  .main    { order: 2; }    /* main content next */
  .extras  { order: 3; }
}

@media (max-width: 767px) {
  .main    { order: 1; }    /* main content first on mobile */
  .sidebar { order: 2; }    /* sidebar after */
  .extras  { order: 3; }
}</code></pre>

<p>Mobile users see main content first; desktop users see sidebar first &mdash; same HTML, different visual orders.</p>

<p><strong>Critical accessibility caveat:</strong> <code>order</code> only changes <em>visual</em> order. Screen readers, keyboard tab order, and source order remain unchanged. Mismatch between visual and source order can confuse:</p>
<ul>
  <li><strong>Keyboard users</strong> tabbing through the page.</li>
  <li><strong>Screen reader users</strong> hearing items read in source order.</li>
  <li><strong>Print stylesheets</strong> that ignore <code>order</code>.</li>
</ul>

<p><strong>Best practice:</strong> use <code>order</code> for purely visual rearrangement only when source order remains logical. For meaningful reordering, change the actual HTML or use Grid&rsquo;s <code>grid-area</code> for more control. The same caveat applies to Grid&rsquo;s <code>order</code> property.</p>

<p><strong>Common mistake:</strong> using <code>order</code> to put a "Back" button after "Next" visually while keeping it before "Next" in HTML. Keyboard users hit Tab and land on Next first &mdash; surprising them.</p>
'''

ANSWERS[44] = r'''
<p>A sticky footer stays at the bottom of the viewport when content is short, but moves down as expected when content is long. Modern Flexbox makes this trivial.</p>

<pre><code>&lt;body&gt;
  &lt;header&gt;Site Header&lt;/header&gt;
  &lt;main&gt;Page Content&lt;/main&gt;
  &lt;footer&gt;Site Footer&lt;/footer&gt;
&lt;/body&gt;

&lt;style&gt;
  body {
    min-height: 100vh;
    margin: 0;
    display: flex;
    flex-direction: column;
  }
  main {
    flex: 1;     /* grows to fill available space */
  }
&lt;/style&gt;</code></pre>

<p><strong>How it works:</strong></p>
<ul>
  <li><code>min-height: 100vh</code> &mdash; body is at least viewport height.</li>
  <li><code>flex-direction: column</code> &mdash; stacks header, main, footer vertically.</li>
  <li><code>flex: 1</code> on main &mdash; main grows to fill any leftover space, pushing footer to the bottom.</li>
</ul>

<p>When content is short, main expands to fill the viewport; footer sits at the bottom. When content is long, main takes its natural size; footer appears below content as expected.</p>

<p><strong>Grid alternative</strong>:</p>
<pre><code>body {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}</code></pre>

<p>Three rows: header (auto), main (1fr fills space), footer (auto). Equivalent result, slightly more concise.</p>

<p><strong>Why not <code>position: fixed</code>?</strong></p>
<pre><code>/* Don&rsquo;t do this for sticky footer */
footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}</code></pre>

<p>Fixed positioning makes the footer cover content &mdash; never moves out of the way. Users on long pages always see the footer overlapping content. The Flexbox approach is "sticky to the bottom of viewport when content fits, naturally below content otherwise" &mdash; what users expect.</p>

<p><strong>Modern viewport units</strong> for safer mobile behavior:</p>
<pre><code>body {
  min-height: 100dvh;     /* dynamic viewport height */
}</code></pre>

<p><code>dvh</code> accounts for mobile browser address bars showing/hiding &mdash; <code>100vh</code> can mistakenly include the address bar height on iOS Safari, causing footer to push off-screen. <code>dvh</code> is the modern fix.</p>
'''

ANSWERS[45] = r'''
<p>Both <code>relative</code> and <code>absolute</code> positioning use offset properties (<code>top</code>, <code>right</code>, <code>bottom</code>, <code>left</code>), but they differ in <strong>what they&rsquo;re positioned relative to</strong> and how they affect surrounding content.</p>

<table>
  <tr><th></th><th><code>position: relative</code></th><th><code>position: absolute</code></th></tr>
  <tr><td>Relative to</td><td>Element&rsquo;s normal position</td><td>Nearest positioned ancestor (or viewport)</td></tr>
  <tr><td>Affects layout</td><td>Yes &mdash; reserves original space</td><td>No &mdash; removed from flow</td></tr>
  <tr><td>Surrounding content</td><td>Stays as if element wasn&rsquo;t offset</td><td>Wraps as if element doesn&rsquo;t exist</td></tr>
  <tr><td>Common use</td><td>Slight offset, or as anchor for absolute children</td><td>Tooltips, badges, dropdowns, modals</td></tr>
</table>

<p><strong>Relative example</strong> &mdash; offset from natural position:</p>
<pre><code>.shifted {
  position: relative;
  top: 20px;
  left: 30px;
  /* Element renders 20px down and 30px right of where it would normally sit.
     Original space is still reserved, so siblings don&rsquo;t shift. */
}</code></pre>

<p><strong>Absolute example</strong> &mdash; precisely placed within a positioned parent:</p>
<pre><code>.parent {
  position: relative;        /* establishes positioning context */
}
.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: red;
  color: white;
  padding: 0.2em 0.5em;
  border-radius: 4px;
}</code></pre>

<pre><code>&lt;div class="parent"&gt;
  Card content
  &lt;span class="badge"&gt;NEW&lt;/span&gt;
&lt;/div&gt;</code></pre>

<p>The badge sits in the top-right corner of the parent. Without <code>position: relative</code> on the parent, the badge would position relative to the viewport (or the next positioned ancestor up the tree).</p>

<p><strong>The "relative parent + absolute child" combo</strong> is the most common positioning pattern:</p>
<ul>
  <li>Tooltips on form fields.</li>
  <li>Status indicators on avatars.</li>
  <li>Close buttons on cards.</li>
  <li>Dropdown menus under buttons.</li>
  <li>Decorative overlays (corner ribbons, badges).</li>
</ul>

<p><strong>Edge cases:</strong></p>
<ul>
  <li><code>position: absolute</code> with <strong>no positioned ancestor</strong> &mdash; positions relative to the viewport (often a bug).</li>
  <li><code>position: relative</code> with <strong>no offsets</strong> &mdash; renders normally but creates a positioning context for absolute children.</li>
  <li>Absolute elements with <code>top: 0; right: 0; bottom: 0; left: 0</code> stretch to fill their positioned ancestor &mdash; useful for full-overlay effects.</li>
</ul>

<p>For modern centered layouts, Flexbox or Grid is usually clearer than absolute positioning.</p>
'''

ANSWERS[46] = r'''
<p>Add a shadow to text with <code>text-shadow</code>. Same syntax as <code>box-shadow</code> but without the <code>spread</code> parameter and applied only to text glyphs.</p>

<pre><code>.subtle-shadow {
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  /* offset-x | offset-y | blur | color */
}

.heavy-shadow {
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}</code></pre>

<p><strong>Four values</strong> (color is optional):</p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td>offset-x</td><td>Horizontal shift (positive = right)</td></tr>
  <tr><td>offset-y</td><td>Vertical shift (positive = down)</td></tr>
  <tr><td>blur-radius</td><td>Fuzziness (0 = sharp)</td></tr>
  <tr><td>color</td><td>Shadow color</td></tr>
</table>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Subtle text shadow */
.h1 {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Letterpress effect (classic) */
.letterpress {
  color: #444;
  text-shadow: 0 1px 0 #fff;     /* white shadow below for inset look */
  background: #d0d0d0;
}

/* Glow effect */
.neon {
  color: white;
  text-shadow:
    0 0 5px #ff00ff,
    0 0 15px #ff00ff,
    0 0 25px #ff00ff;
}

/* Outline (text stroke alternative) */
.outlined {
  color: white;
  text-shadow:
    -1px -1px 0 black,
     1px -1px 0 black,
    -1px  1px 0 black,
     1px  1px 0 black;
}</code></pre>

<p><strong>Hero text on busy backgrounds</strong> &mdash; improve readability:</p>
<pre><code>.hero h1 {
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
}</code></pre>

<p>White text on photo backgrounds reads better with a subtle dark shadow &mdash; users can read it even when the photo is bright in places.</p>

<p><strong>Multiple shadows</strong> stack &mdash; common for layered effects:</p>
<pre><code>.fancy {
  text-shadow:
    1px 1px 1px black,
    2px 2px 2px gray,
    3px 3px 3px lightgray;
}</code></pre>

<p>Modern alternative: <code>text-stroke</code> (with <code>-webkit-</code> prefix) for outlines, but <code>text-shadow</code> still works in more contexts and renders consistently. For heavy decorative effects, SVG text gives more control.</p>
'''

ANSWERS[47] = r'''
<p>Use the <code>linear-gradient()</code> function in <code>background</code> or <code>background-image</code>. Specify direction and color stops &mdash; the browser interpolates colors smoothly between them.</p>

<pre><code>.banner {
  background: linear-gradient(to right, #0066cc, #00aaff);
}

.diagonal {
  background: linear-gradient(135deg, navy, skyblue);
}

.multistep {
  background: linear-gradient(to bottom,
    #1a2980 0%,
    #26d0ce 50%,
    #ff6b35 100%);
}</code></pre>

<p><strong>Direction syntax:</strong></p>
<table>
  <tr><th>Syntax</th><th>Direction</th></tr>
  <tr><td><code>to right</code></td><td>Left to right</td></tr>
  <tr><td><code>to bottom</code></td><td>Top to bottom (default)</td></tr>
  <tr><td><code>to top right</code></td><td>Diagonal corner</td></tr>
  <tr><td><code>0deg</code></td><td>Bottom to top</td></tr>
  <tr><td><code>90deg</code></td><td>Left to right</td></tr>
  <tr><td><code>180deg</code></td><td>Top to bottom</td></tr>
  <tr><td><code>45deg</code></td><td>Diagonal (bottom-left to top-right)</td></tr>
</table>

<p><strong>Color stops</strong> &mdash; specify exact positions for color transitions:</p>
<pre><code>.sharp-edge {
  background: linear-gradient(to right,
    blue 0%,
    blue 50%,
    red 50%,
    red 100%);
  /* Hard edge at 50% — instant blue-to-red transition */
}

.soft-blend {
  background: linear-gradient(to right, blue, red);
  /* Smooth blue-to-red across full width */
}</code></pre>

<p><strong>Multiple color stops</strong> create rainbows:</p>
<pre><code>.rainbow {
  background: linear-gradient(to right,
    red, orange, yellow, green, blue, indigo, violet);
}</code></pre>

<p><strong>Repeating gradients</strong> for stripes:</p>
<pre><code>.striped {
  background: repeating-linear-gradient(
    45deg,
    #ddd,
    #ddd 10px,
    #f0f0f0 10px,
    #f0f0f0 20px);
}</code></pre>

<p><strong>Common use cases:</strong></p>
<ul>
  <li>Hero section backgrounds (vertical or diagonal gradients).</li>
  <li>Buttons with subtle depth (top to bottom slight gradient).</li>
  <li>Section dividers (gradient from one section&rsquo;s color to another).</li>
  <li>Loading skeletons with shimmer animation.</li>
  <li>Dark overlays on images: <code>linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5))</code>.</li>
</ul>

<p><strong>Modern color interpolation</strong> &mdash; specify color space:</p>
<pre><code>background: linear-gradient(in oklch, red, blue);
/* Smoother perceptual transition through purple */</code></pre>

<p>Without specifying, browsers use sRGB which can produce muddy mid-colors. <code>oklch</code> color space gives more vibrant, perceptually-correct gradients.</p>
'''

ANSWERS[48] = r'''
<p>The <code>outline</code> property draws a line around an element &mdash; similar to <code>border</code> but with one critical difference: it doesn&rsquo;t affect layout.</p>

<pre><code>.focused {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}</code></pre>

<p><strong>Outline vs border:</strong></p>
<table>
  <tr><th></th><th>Outline</th><th>Border</th></tr>
  <tr><td>Affects layout</td><td>No</td><td>Yes (adds to size)</td></tr>
  <tr><td>Per-side control</td><td>No (all 4 sides only)</td><td>Yes</td></tr>
  <tr><td>Rounded corners</td><td>Yes (<code>border-radius</code> rounds outline too)</td><td>Yes</td></tr>
  <tr><td>Default styling</td><td>Browser-specific (often blue)</td><td>None (must specify)</td></tr>
  <tr><td>Use case</td><td>Focus rings, debugging</td><td>Decorative borders</td></tr>
</table>

<pre><code>.outlined {
  outline: 3px dashed red;
  outline-offset: 5px;     /* gap between element and outline */
}</code></pre>

<p>Outline values are similar to border: <code>width style color</code>.</p>

<p><strong>Critical: never remove focus outlines without replacement</strong>:</p>
<pre><code>/* DON&rsquo;T do this — destroys keyboard accessibility */
*:focus { outline: none; }

/* DO this instead — replace with custom focus style */
*:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}</code></pre>

<p>Focus indicators tell keyboard users where they are on the page. Removing them makes your site unusable for anyone who can&rsquo;t use a mouse &mdash; a major WCAG violation.</p>

<p><strong>Modern approach with <code>:focus-visible</code></strong>:</p>
<ul>
  <li>The <code>:focus-visible</code> pseudo-class only matches <em>keyboard-induced</em> focus, not mouse clicks.</li>
  <li>Mouse users don&rsquo;t see the focus ring (it&rsquo;s visual noise after a click).</li>
  <li>Keyboard users see clear focus indicators where needed.</li>
  <li>Best of both worlds.</li>
</ul>

<pre><code>button {
  outline: none;     /* removes default focus ring */
}
button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}</code></pre>

<p><strong>Debugging</strong>:</p>
<pre><code>* {
  outline: 1px solid red;
}</code></pre>

<p>Add this temporarily to see the box of every element on the page &mdash; useful for diagnosing layout issues without disturbing the actual layout.</p>

<p><strong>Outline supports <code>border-radius</code></strong> in modern browsers &mdash; rounded outlines for rounded buttons match perfectly without extra work.</p>
'''

ANSWERS[49] = r'''
<p>The <code>calc()</code> function lets you do math in CSS values &mdash; mixing units, performing arithmetic, and creating responsive sizing that&rsquo;s impossible with single values alone.</p>

<pre><code>.box {
  width: calc(100% - 60px);    /* full parent width minus 60px */
  height: calc(100vh - 80px);  /* viewport height minus header */
  padding: calc(1em + 10px);
  font-size: calc(1rem + 0.5vw);
}</code></pre>

<p><strong>Supported operations:</strong></p>
<table>
  <tr><th>Operator</th><th>Use</th></tr>
  <tr><td><code>+</code></td><td>Addition (requires spaces around)</td></tr>
  <tr><td><code>-</code></td><td>Subtraction (requires spaces around)</td></tr>
  <tr><td><code>*</code></td><td>Multiplication (one side must be unitless)</td></tr>
  <tr><td><code>/</code></td><td>Division (right side must be unitless)</td></tr>
</table>

<p><strong>Critical syntax rule: spaces required around <code>+</code> and <code>-</code></strong>:</p>
<pre><code>width: calc(100% - 20px);    /* CORRECT */
width: calc(100%-20px);       /* BROKEN — interpreted as "100% with -20px appended" */
width: calc(100% -20px);      /* BROKEN — same problem */
width: calc(100%* 0.5);       /* OK — but for clarity, also space the * */</code></pre>

<p><strong>Real-world patterns:</strong></p>
<pre><code>/* Subtract fixed sidebar from full width */
.main {
  width: calc(100% - 250px);
}

/* Center using calc instead of margin: auto */
.centered {
  position: absolute;
  left: calc(50% - 100px);   /* if width is 200px */
  top: calc(50% - 50px);
}

/* Padding-based responsive container */
.container {
  width: calc(100% - 4em);   /* always 2em padding on each side */
  margin: 0 auto;
}

/* Responsive font that scales with viewport */
.responsive-text {
  font-size: calc(1rem + 0.5vw);
}

/* Equal-height columns minus gap */
.three-col {
  width: calc(33.333% - 1em);
  margin-right: 1em;
}</code></pre>

<p><strong>With CSS variables</strong>:</p>
<pre><code>:root {
  --header-height: 60px;
  --sidebar-width: 250px;
}

.main-content {
  height: calc(100vh - var(--header-height));
  margin-left: calc(var(--sidebar-width) + 1em);
}</code></pre>

<p>This pattern is common in dashboard layouts &mdash; everything anchors to known dimensions, and <code>calc()</code> keeps the math clean.</p>

<p><strong>Modern alternatives</strong>:</p>
<ul>
  <li><strong><code>min()</code> and <code>max()</code></strong> &mdash; pick the smaller/larger of two values.</li>
  <li><strong><code>clamp(min, preferred, max)</code></strong> &mdash; bounded fluid values.</li>
</ul>

<pre><code>width: min(100%, 1200px);          /* full width but capped at 1200px */
font-size: clamp(1rem, 2vw, 2rem); /* fluid between 1rem and 2rem */</code></pre>

<p>These often replace <code>calc()</code>-based responsive patterns more elegantly.</p>
'''

ANSWERS[50] = r'''
<p>Attribute selectors target elements based on their <strong>HTML attributes and values</strong>. They use square-bracket syntax and offer flexible matching beyond just exact equality.</p>

<pre><code>/* Has the attribute (any value) */
input[required] {
  border-left: 3px solid red;
}

/* Exact value match */
input[type="email"] {
  background: lightyellow;
}

/* Different match operators */
a[href^="https://"]   { color: green; }   /* starts with */
a[href$=".pdf"]        { color: orange; }  /* ends with */
a[href*="example"]     { color: blue; }    /* contains */
a[lang|="en"]          { font-style: italic; } /* en or en-* */
a[class~="active"]     { font-weight: bold; }  /* whitespace-separated word */</code></pre>

<p><strong>The match operators:</strong></p>
<table>
  <tr><th>Operator</th><th>Matches</th></tr>
  <tr><td><code>[attr]</code></td><td>Has the attribute</td></tr>
  <tr><td><code>[attr="value"]</code></td><td>Exact value</td></tr>
  <tr><td><code>[attr^="value"]</code></td><td>Starts with</td></tr>
  <tr><td><code>[attr$="value"]</code></td><td>Ends with</td></tr>
  <tr><td><code>[attr*="value"]</code></td><td>Contains substring</td></tr>
  <tr><td><code>[attr~="value"]</code></td><td>Whitespace-separated word</td></tr>
  <tr><td><code>[attr|="value"]</code></td><td>Exact or starts with "value-"</td></tr>
  <tr><td><code>[attr="value" i]</code></td><td>Case-insensitive (modern)</td></tr>
</table>

<p><strong>Powerful real-world patterns:</strong></p>
<pre><code>/* Style external links differently */
a[href^="http"]:not([href*="example.com"]) {
  background: url("external-icon.svg") no-repeat right center;
  padding-right: 1.2em;
}

/* Highlight required form fields */
input[required] + label::after {
  content: " *";
  color: red;
}

/* Show file type icons */
a[href$=".pdf"]::before  { content: "📄 "; }
a[href$=".zip"]::before  { content: "📦 "; }
a[href$=".doc"]::before  { content: "📝 "; }

/* Style by data attributes */
[data-state="loading"]   { opacity: 0.5; }
[data-state="error"]     { color: red; border-color: red; }
[data-state="success"]   { color: green; }

/* Active nav link */
nav a[aria-current="page"] {
  font-weight: 600;
  border-bottom: 2px solid currentColor;
}</code></pre>

<p><strong>Specificity:</strong> attribute selectors have the same specificity as classes (<code>0,1,0</code>), so they slot in cleanly with class-based stylesheets.</p>

<p><strong>Common use cases:</strong></p>
<ul>
  <li>Styling form inputs by type (<code>input[type="email"]</code>).</li>
  <li>Indicating external vs internal links.</li>
  <li>State indicators via data attributes.</li>
  <li>Active navigation items via <code>aria-current</code>.</li>
  <li>File type indicators on download links.</li>
</ul>

<p>Modern frameworks lean heavily on attribute selectors via data attributes &mdash; cleaner than adding CSS classes for every state.</p>
'''

ANSWERS[51] = r'''
<p>Both <code>visibility</code> and <code>display</code> can hide elements, but they behave differently in layout, accessibility, and animations.</p>

<table>
  <tr><th></th><th><code>visibility: hidden</code></th><th><code>display: none</code></th></tr>
  <tr><td>Visible</td><td>No</td><td>No</td></tr>
  <tr><td>Takes up space</td><td>Yes &mdash; reserved layout area</td><td>No &mdash; removed from flow</td></tr>
  <tr><td>Hidden from screen readers</td><td>Yes</td><td>Yes</td></tr>
  <tr><td>Children can override</td><td>Yes (with <code>visibility: visible</code>)</td><td>No</td></tr>
  <tr><td>Animatable</td><td>Yes</td><td>No (toggles instantly)</td></tr>
</table>

<pre><code>&lt;div class="invisible"&gt;Hidden but reserved&lt;/div&gt;
&lt;div class="gone"&gt;Removed entirely&lt;/div&gt;
&lt;div class="visible-after"&gt;After&lt;/div&gt;

&lt;style&gt;
  .invisible { visibility: hidden; }
  .gone      { display: none; }
&lt;/style&gt;</code></pre>

<p>With <code>visibility: hidden</code>, the box still occupies its space &mdash; the next element appears below where the hidden box would be. With <code>display: none</code>, the element is gone entirely; siblings move up.</p>

<p><strong>Choose by purpose:</strong></p>
<ul>
  <li><strong>Use <code>display: none</code></strong> for fully removing content (modal hidden by default, conditional sections).</li>
  <li><strong>Use <code>visibility: hidden</code></strong> when you want to reserve space (stable grid layouts, keeping consistent height).</li>
  <li><strong>Use <code>opacity: 0</code></strong> when you want fade animations or interactive-but-invisible (clicks still register).</li>
</ul>

<p>The third option, <code>opacity: 0</code>, makes the element invisible but still in the layout AND still clickable.</p>
'''

ANSWERS[52] = r'''
<p>The <code>transition</code> property animates changes to CSS values smoothly over time. Apply it on the element&rsquo;s default state, then change properties on hover, focus, or via JS.</p>

<pre><code>&lt;button class="btn"&gt;Hover me&lt;/button&gt;

&lt;style&gt;
  .btn {
    background: #0066cc;
    color: white;
    padding: 0.5em 1em;
    transition: background 0.3s, transform 0.2s;
  }
  .btn:hover {
    background: #003d7a;
    transform: translateY(-2px);
  }
&lt;/style&gt;</code></pre>

<p><strong>Transition shorthand:</strong></p>
<pre><code>transition: property duration timing-function delay;

/* Examples */
transition: all 0.3s ease;
transition: opacity 0.5s ease-in-out 0.1s;
transition: background 0.2s, transform 0.3s;   /* multiple */</code></pre>

<p><strong>Timing functions:</strong></p>
<table>
  <tr><th>Value</th><th>Curve</th></tr>
  <tr><td><code>linear</code></td><td>Constant speed</td></tr>
  <tr><td><code>ease</code> (default)</td><td>Slow start, fast middle, slow end</td></tr>
  <tr><td><code>ease-in</code></td><td>Slow start</td></tr>
  <tr><td><code>ease-out</code></td><td>Slow end</td></tr>
  <tr><td><code>cubic-bezier(...)</code></td><td>Custom curve</td></tr>
</table>

<p><strong>Performance tip:</strong> only transition <code>opacity</code> and <code>transform</code> properties for smooth 60fps animations &mdash; the GPU handles them. Properties like <code>width</code>, <code>height</code>, <code>top</code>, <code>left</code> trigger layout recalculation and feel janky.</p>

<pre><code>/* Smooth */
.fast { transition: transform 0.3s; }
.fast:hover { transform: scale(1.05); }

/* Janky on slow devices */
.slow { transition: width 0.3s; }
.slow:hover { width: 200px; }</code></pre>
'''

ANSWERS[53] = r'''
<p>Media queries apply different styles based on screen size, device features, or user preferences. They&rsquo;re the foundation of responsive design.</p>

<pre><code>/* Mobile-first: default styles for mobile */
.container {
  padding: 1em;
}
.sidebar { display: none; }

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    display: grid;
    grid-template-columns: 1fr 250px;
  }
  .sidebar { display: block; }
}

/* Desktop and up */
@media (min-width: 1200px) {
  .container {
    max-width: 1400px;
    margin: 0 auto;
  }
}</code></pre>

<p><strong>Common breakpoints (no fixed standard):</strong></p>
<table>
  <tr><th>Range</th><th>Device</th></tr>
  <tr><td>0&ndash;599px</td><td>Phone</td></tr>
  <tr><td>600&ndash;899px</td><td>Tablet portrait</td></tr>
  <tr><td>900&ndash;1199px</td><td>Tablet landscape, small laptop</td></tr>
  <tr><td>1200px+</td><td>Desktop</td></tr>
</table>

<p><strong>Beyond width:</strong></p>
<pre><code>/* Orientation */
@media (orientation: landscape) { ... }

/* User color scheme preference */
@media (prefers-color-scheme: dark) {
  body { background: #1a1a1a; color: #f0f0f0; }
}

/* Reduced motion preference (accessibility) */
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}

/* Hover capability (touch vs mouse) */
@media (hover: hover) {
  .card:hover { transform: scale(1.05); }
}

/* Print styles */
@media print {
  nav, footer { display: none; }
}</code></pre>

<p><strong>Always include the viewport meta tag</strong> in HTML or media queries won&rsquo;t fire correctly on mobile:</p>
<pre><code>&lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;</code></pre>
'''

ANSWERS[54] = r'''
<p>Several techniques make an element span the full width of its parent or the viewport.</p>

<p><strong>1. Default block elements:</strong></p>
<pre><code>&lt;header class="full"&gt;Full width header&lt;/header&gt;

&lt;style&gt;
  header { /* block elements naturally full width */ }
&lt;/style&gt;</code></pre>

<p>Block elements (<code>&lt;div&gt;</code>, <code>&lt;header&gt;</code>, <code>&lt;section&gt;</code>) are full-width of their parent by default.</p>

<p><strong>2. Explicit width: 100%:</strong></p>
<pre><code>.full {
  width: 100%;        /* fills the parent */
}</code></pre>

<p>Useful for inline-block or flex children that need to override their natural width.</p>

<p><strong>3. Full viewport width:</strong></p>
<pre><code>.viewport-wide {
  width: 100vw;       /* viewport width — ignores parent */
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}</code></pre>

<p>Useful for hero banners that need to break out of a constrained container and span the full screen width. The <code>50%</code>/<code>translateX(-50%)</code> trick centers the element horizontally regardless of where its parent ends.</p>

<p><strong>4. Full-bleed (modern, simpler):</strong></p>
<pre><code>.container {
  max-width: 1200px;
  margin: 0 auto;
}
.full-bleed {
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
}</code></pre>

<p>Negative margins push the element to the viewport edges. Combined with <code>overflow-x: hidden</code> on the body, this is the cleanest pattern for full-width sections inside a centered container.</p>

<p><strong>Edge case:</strong> beware of horizontal scrollbars. <code>100vw</code> includes the scrollbar width, while parents may not &mdash; subtle 15px overflow appears on Windows. Test before shipping.</p>
'''

ANSWERS[55] = r'''
<p>Use <code>:nth-child()</code> with <code>odd</code> or <code>even</code> to apply styles to alternating items &mdash; the classic "zebra stripe" pattern.</p>

<pre><code>&lt;ul class="list"&gt;
  &lt;li&gt;Item 1&lt;/li&gt;
  &lt;li&gt;Item 2&lt;/li&gt;
  &lt;li&gt;Item 3&lt;/li&gt;
  &lt;li&gt;Item 4&lt;/li&gt;
  &lt;li&gt;Item 5&lt;/li&gt;
&lt;/ul&gt;

&lt;style&gt;
  .list li:nth-child(odd) {
    background: #f5f5f5;
  }
  .list li:nth-child(even) {
    background: white;
  }
&lt;/style&gt;</code></pre>

<p>Items 1, 3, 5 get gray; items 2, 4 stay white.</p>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Zebra rows in a table */
tbody tr:nth-child(odd) {
  background: #f9f9f9;
}

/* Every 3rd item */
li:nth-child(3n) {
  margin-right: 0;
}

/* First 5 items */
li:nth-child(-n+5) {
  font-weight: bold;
}

/* All items after the 5th */
li:nth-child(n+6) {
  opacity: 0.5;
}</code></pre>

<p><strong>Formula explained:</strong></p>
<table>
  <tr><th>Expression</th><th>Selects</th></tr>
  <tr><td><code>odd</code> or <code>2n+1</code></td><td>1, 3, 5, ...</td></tr>
  <tr><td><code>even</code> or <code>2n</code></td><td>2, 4, 6, ...</td></tr>
  <tr><td><code>3n</code></td><td>3, 6, 9, ...</td></tr>
  <tr><td><code>3n+1</code></td><td>1, 4, 7, ...</td></tr>
  <tr><td><code>-n+3</code></td><td>1, 2, 3 only</td></tr>
</table>

<p>For modern alternatives, the <code>:nth-child(odd of .visible)</code> syntax filters by selector first, then applies <code>nth-child</code> &mdash; useful when items can be hidden dynamically.</p>
'''

ANSWERS[56] = r'''
<p>The <code>clip-path</code> property hides parts of an element by defining a visible region. The unclipped region shows; the rest is clipped away.</p>

<pre><code>&lt;img class="circle" src="photo.jpg" alt=""&gt;
&lt;div class="hexagon"&gt;Hexagonal&lt;/div&gt;
&lt;div class="arrow"&gt;Arrow shape&lt;/div&gt;

&lt;style&gt;
  /* Circle */
  .circle {
    clip-path: circle(50%);
  }

  /* Hexagon */
  .hexagon {
    clip-path: polygon(
      50% 0%,    /* top */
      100% 25%,
      100% 75%,
      50% 100%,  /* bottom */
      0% 75%,
      0% 25%
    );
  }

  /* Arrow shape */
  .arrow {
    clip-path: polygon(0 20%, 60% 20%, 60% 0, 100% 50%, 60% 100%, 60% 80%, 0 80%);
    background: navy;
    width: 200px;
    height: 100px;
  }
&lt;/style&gt;</code></pre>

<p><strong>Common clip-path shapes:</strong></p>
<table>
  <tr><th>Function</th><th>Creates</th></tr>
  <tr><td><code>circle(50%)</code></td><td>Circle (radius from center)</td></tr>
  <tr><td><code>ellipse(50% 30%)</code></td><td>Ellipse (rx, ry)</td></tr>
  <tr><td><code>inset(10px 20px)</code></td><td>Inset rectangle</td></tr>
  <tr><td><code>polygon(...)</code></td><td>Custom polygon (multiple x y points)</td></tr>
  <tr><td><code>path(...)</code></td><td>SVG path string &mdash; maximum flexibility</td></tr>
</table>

<p><strong>Animating clip-path:</strong></p>
<pre><code>.menu {
  clip-path: circle(0% at top right);
  transition: clip-path 0.4s;
}
.menu.open {
  clip-path: circle(150% at top right);
}</code></pre>

<p>Animations between two clip-path values reveal content with creative effects &mdash; circular reveals, slide-ins, custom shape transitions.</p>

<p>Use online tools like Clippy (bennettfeely.com/clippy/) to design polygon paths visually instead of guessing coordinates. Combined with <code>transform</code>, clip-path enables dramatic visual effects without image editing.</p>
'''

ANSWERS[57] = r'''
<p>Use <code>border-radius</code> to round button corners. Combined with padding, background, and transitions, you can create polished buttons with pure CSS.</p>

<pre><code>&lt;button class="btn"&gt;Click me&lt;/button&gt;
&lt;button class="btn-pill"&gt;Pill button&lt;/button&gt;
&lt;button class="btn-icon"&gt;&#x1F50D;&lt;/button&gt;

&lt;style&gt;
  /* Standard rounded button */
  .btn {
    background: #0066cc;
    color: white;
    border: none;
    padding: 0.6em 1.5em;
    border-radius: 6px;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.2s;
  }
  .btn:hover {
    background: #004999;
  }

  /* Pill-shaped (fully rounded) */
  .btn-pill {
    background: #ff6b35;
    color: white;
    padding: 0.5em 1.5em;
    border: none;
    border-radius: 999px;     /* huge value clips to height */
    cursor: pointer;
  }

  /* Circular icon button */
  .btn-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;       /* perfect circle */
    border: 1px solid #ccc;
    background: white;
    cursor: pointer;
  }
&lt;/style&gt;</code></pre>

<p><strong>Border-radius variations:</strong></p>
<table>
  <tr><th>Value</th><th>Effect</th></tr>
  <tr><td><code>border-radius: 4px</code></td><td>Slightly rounded corners</td></tr>
  <tr><td><code>border-radius: 8px</code></td><td>Modern rounded buttons</td></tr>
  <tr><td><code>border-radius: 999px</code></td><td>Pill / capsule shape</td></tr>
  <tr><td><code>border-radius: 50%</code></td><td>Circle (when width = height)</td></tr>
  <tr><td><code>border-radius: 8px 8px 0 0</code></td><td>Top corners only</td></tr>
</table>

<p><strong>Add depth with shadows:</strong></p>
<pre><code>.btn {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}
.btn:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}
.btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}</code></pre>

<p>The hover and active states give satisfying tactile feedback &mdash; the button "lifts" on hover and "presses" on click.</p>
'''

ANSWERS[58] = r'''
<p>Vertical centering is one of CSS&rsquo;s most asked questions. Modern Flexbox and Grid solve it in two lines.</p>

<p><strong>Flexbox (most common):</strong></p>
<pre><code>.parent {
  display: flex;
  align-items: center;        /* vertical center */
  justify-content: center;     /* horizontal center */
  height: 200px;
}</code></pre>

<p><strong>Grid (also two lines):</strong></p>
<pre><code>.parent {
  display: grid;
  place-items: center;        /* both axes */
  height: 200px;
}</code></pre>

<p>Both center any child element regardless of its size or type.</p>

<p><strong>Single line of text within an element:</strong></p>
<pre><code>.button {
  height: 40px;
  line-height: 40px;          /* equals height = vertical centering */
  text-align: center;
}</code></pre>

<p><code>line-height</code> equal to the element height centers single-line text. Doesn&rsquo;t work for multi-line text.</p>

<p><strong>Older techniques (rarely needed in 2026):</strong></p>
<pre><code>/* Absolute positioning + transform */
.parent { position: relative; }
.child {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Table cell trick */
.parent {
  display: table-cell;
  vertical-align: middle;
}</code></pre>

<p><strong>Vertical centering of multi-line text inside a fixed-height container:</strong></p>
<pre><code>.banner {
  height: 200px;
  display: flex;
  align-items: center;        /* vertical centering */
  justify-content: center;     /* horizontal */
  text-align: center;
}</code></pre>

<p>Flexbox is the modern answer for almost all centering needs &mdash; works for any content, any size, multi-line, with two lines of CSS.</p>
'''

ANSWERS[59] = r'''
<p>Flexbox makes responsive layouts simple. Set <code>display: flex</code> on a container and the children become flex items that can wrap, grow, shrink, and align flexibly.</p>

<pre><code>&lt;div class="container"&gt;
  &lt;div class="card"&gt;Card 1&lt;/div&gt;
  &lt;div class="card"&gt;Card 2&lt;/div&gt;
  &lt;div class="card"&gt;Card 3&lt;/div&gt;
  &lt;div class="card"&gt;Card 4&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .container {
    display: flex;
    flex-wrap: wrap;        /* allow items to wrap onto new lines */
    gap: 1rem;
    padding: 1rem;
  }
  .card {
    flex: 1 1 250px;        /* grow, shrink, basis */
    background: #f0f0f0;
    padding: 1em;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>flex</code> shorthand:</strong></p>
<pre><code>flex: 1 1 250px;
/* equivalent to: */
flex-grow: 1;       /* grow to fill available space */
flex-shrink: 1;     /* shrink if there's not enough room */
flex-basis: 250px;  /* preferred starting width */</code></pre>

<p>Cards fit naturally: 4 per row on wide screens, 2 on tablet, 1 on phone &mdash; no media queries needed.</p>

<p><strong>Container properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>flex-direction</code></td><td><code>row</code> (default), <code>column</code></td></tr>
  <tr><td><code>flex-wrap</code></td><td><code>nowrap</code> (default), <code>wrap</code></td></tr>
  <tr><td><code>justify-content</code></td><td>Main axis alignment (<code>center</code>, <code>space-between</code>)</td></tr>
  <tr><td><code>align-items</code></td><td>Cross axis alignment (<code>center</code>, <code>stretch</code>)</td></tr>
  <tr><td><code>gap</code></td><td>Space between items</td></tr>
</table>

<p><strong>Common pattern: navbar with logo + nav + actions:</strong></p>
<pre><code>.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1em;
}</code></pre>

<p>Three sections: logo (left), nav (middle), actions (right) &mdash; <code>space-between</code> distributes them across the width.</p>
'''

ANSWERS[60] = r'''
<p>Use the <code>color</code> property to change text color.</p>

<pre><code>&lt;p class="primary"&gt;Important text&lt;/p&gt;
&lt;p class="muted"&gt;Less important text&lt;/p&gt;
&lt;p class="error"&gt;Error message&lt;/p&gt;

&lt;style&gt;
  .primary { color: #0066cc; }
  .muted   { color: #666; }
  .error   { color: rgb(220, 53, 69); }

  /* Inheritance — children inherit color from parents */
  body {
    color: #333;
  }

  /* Specific elements */
  h1 { color: navy; }
  a  { color: #0066cc; }
  a:hover { color: #003d7a; }
&lt;/style&gt;</code></pre>

<p><strong>Color value formats:</strong></p>
<table>
  <tr><th>Format</th><th>Example</th></tr>
  <tr><td>Named</td><td><code>red</code>, <code>navy</code>, <code>tomato</code></td></tr>
  <tr><td>Hex</td><td><code>#ff6b35</code>, <code>#fff</code></td></tr>
  <tr><td>RGB</td><td><code>rgb(255 107 53)</code></td></tr>
  <tr><td>RGB with alpha</td><td><code>rgb(255 107 53 / 0.5)</code></td></tr>
  <tr><td>HSL</td><td><code>hsl(15 100% 60%)</code></td></tr>
  <tr><td>OKLCH</td><td><code>oklch(70% 0.2 30)</code></td></tr>
  <tr><td>Inherit from parent</td><td><code>currentColor</code> or omit (inherited)</td></tr>
</table>

<p><strong>Inheritance:</strong> <code>color</code> inherits down the DOM tree by default. Set it on <code>&lt;body&gt;</code> and all descendants pick it up unless overridden:</p>
<pre><code>body { color: #333; }
/* All text inherits #333 unless an element explicitly sets its own color */</code></pre>

<p><strong>The <code>currentColor</code> keyword</strong> &mdash; reuse the inherited text color in other properties:</p>
<pre><code>.button {
  color: navy;
  border: 1px solid currentColor;   /* matches text color */
  fill: currentColor;                /* SVG inside */
}</code></pre>

<p>This is great for icon buttons &mdash; the SVG icon automatically matches the text color, even on hover.</p>
'''

ANSWERS[61] = r'''
<p>Use <code>:nth-child()</code> with <code>odd</code> or <code>even</code> on <code>tbody tr</code> to create alternating row colors &mdash; the classic zebra-stripe table.</p>

<pre><code>&lt;table&gt;
  &lt;thead&gt;
    &lt;tr&gt;&lt;th&gt;Name&lt;/th&gt;&lt;th&gt;Email&lt;/th&gt;&lt;th&gt;Role&lt;/th&gt;&lt;/tr&gt;
  &lt;/thead&gt;
  &lt;tbody&gt;
    &lt;tr&gt;&lt;td&gt;Alice&lt;/td&gt;&lt;td&gt;alice@x.com&lt;/td&gt;&lt;td&gt;Admin&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Bob&lt;/td&gt;&lt;td&gt;bob@x.com&lt;/td&gt;&lt;td&gt;User&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Carol&lt;/td&gt;&lt;td&gt;carol@x.com&lt;/td&gt;&lt;td&gt;Editor&lt;/td&gt;&lt;/tr&gt;
    &lt;tr&gt;&lt;td&gt;Dave&lt;/td&gt;&lt;td&gt;dave@x.com&lt;/td&gt;&lt;td&gt;User&lt;/td&gt;&lt;/tr&gt;
  &lt;/tbody&gt;
&lt;/table&gt;

&lt;style&gt;
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 0.5em 1em;
    text-align: left;
  }
  thead {
    background: #333;
    color: white;
  }
  tbody tr:nth-child(odd) {
    background: #f5f5f5;
  }
  tbody tr:nth-child(even) {
    background: white;
  }
  tbody tr:hover {
    background: #fff8e1;
  }
&lt;/style&gt;</code></pre>

<p><strong>Why <code>tbody tr</code> specifically:</strong> targeting the <code>tbody</code> ensures the header row (<code>thead</code>) isn&rsquo;t affected by the zebra stripes &mdash; otherwise <code>:nth-child(odd)</code> on all rows would catch the header.</p>

<p><strong>Modern alternative: <code>:nth-of-type</code></strong> &mdash; same result with slightly clearer intent:</p>
<pre><code>tr:nth-of-type(odd) { background: #f5f5f5; }</code></pre>

<p><strong>Style only specific columns:</strong></p>
<pre><code>td:nth-child(2) { font-family: monospace; }   /* email column */
td:nth-child(3) { font-weight: 600; }          /* role column */</code></pre>

<p>Zebra striping improves readability &mdash; the eye more easily tracks which cells belong to the same row, especially in tables with many columns.</p>
'''

ANSWERS[62] = r'''
<p>The <code>max-width</code> property sets an upper limit on an element&rsquo;s width. The element can be narrower than this but never wider.</p>

<pre><code>&lt;div class="container"&gt;
  &lt;p&gt;Lots of content...&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  .container {
    max-width: 1200px;     /* never wider than 1200px */
    margin: 0 auto;        /* centers when narrower than viewport */
    padding: 1em;
  }
&lt;/style&gt;</code></pre>

<p>On a wide monitor, the container caps at 1200px. On a phone, it shrinks to fit. The <code>margin: 0 auto</code> centers the box once it hits its max width.</p>

<p><strong>Common max-width patterns:</strong></p>
<table>
  <tr><th>Use case</th><th>Typical value</th></tr>
  <tr><td>Article reading width</td><td><code>max-width: 65ch</code> (~65 characters)</td></tr>
  <tr><td>Standard container</td><td><code>max-width: 1200px</code></td></tr>
  <tr><td>Narrow container</td><td><code>max-width: 800px</code></td></tr>
  <tr><td>Modal dialog</td><td><code>max-width: 500px</code></td></tr>
  <tr><td>Form input</td><td><code>max-width: 400px</code></td></tr>
  <tr><td>Image cap</td><td><code>max-width: 100%</code></td></tr>
</table>

<p><strong>Reading width</strong> &mdash; use <code>ch</code> (character width) for body text:</p>
<pre><code>article {
  max-width: 70ch;       /* about 70 characters per line */
  margin: 0 auto;
}</code></pre>

<p>This produces optimal line lengths for reading (typography research suggests 50-75 characters per line).</p>

<p><strong>max-width vs width:</strong></p>
<table>
  <tr><th></th><th><code>width</code></th><th><code>max-width</code></th></tr>
  <tr><td>Behavior</td><td>Sets exact width</td><td>Sets upper limit</td></tr>
  <tr><td>Responsive</td><td>Often breaks on small screens</td><td>Naturally responsive</td></tr>
  <tr><td>Use for</td><td>Fixed-size elements</td><td>Most flexible layouts</td></tr>
</table>

<p>Combine with <code>min-width</code> for both bounds: <code>min-width: 300px</code> + <code>max-width: 600px</code>.</p>
'''

ANSWERS[63] = r'''
<p>Vertical centering used to be CSS&rsquo;s hardest problem. Modern Flexbox and Grid solve it in 2 lines.</p>

<p><strong>Flexbox (most common):</strong></p>
<pre><code>&lt;div class="parent"&gt;
  &lt;div class="centered"&gt;Centered both ways&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .parent {
    display: flex;
    align-items: center;        /* vertical */
    justify-content: center;     /* horizontal */
    height: 100vh;
  }
&lt;/style&gt;</code></pre>

<p><strong>Grid:</strong></p>
<pre><code>.parent {
  display: grid;
  place-items: center;          /* both axes */
  height: 100vh;
}</code></pre>

<p><strong>Single child &mdash; the modern shortcut</strong>:</p>
<pre><code>.parent {
  display: grid;
  height: 100vh;
}
.centered {
  margin: auto;            /* auto on all sides centers in grid container */
}</code></pre>

<p>This works because grid items respect <code>auto</code> margins on all sides &mdash; same as Flexbox.</p>

<p><strong>Older techniques (still useful in some cases):</strong></p>
<pre><code>/* Absolute positioning */
.parent { position: relative; }
.centered {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Single line of text */
.button {
  height: 40px;
  line-height: 40px;          /* matches height */
}</code></pre>

<p><strong>Vertical centering with auto-content height:</strong></p>
<pre><code>body {
  margin: 0;
  display: grid;
  place-items: center;
  min-height: 100vh;          /* full viewport height */
}</code></pre>

<p>This is the canonical "center anything in the viewport" pattern &mdash; use for splash screens, login pages, error pages, and full-page modals.</p>

<p>Always include <code>min-height: 100vh</code> (not just <code>height</code>) so content longer than the viewport scrolls naturally.</p>
'''

ANSWERS[64] = r'''
<p>Build CSS-only tooltips using the <code>title</code> attribute or, for richer styling, custom <code>::after</code> pseudo-elements.</p>

<p><strong>Basic title attribute (browser-rendered):</strong></p>
<pre><code>&lt;button title="Save your changes"&gt;Save&lt;/button&gt;
&lt;abbr title="HyperText Markup Language"&gt;HTML&lt;/abbr&gt;</code></pre>

<p>Hovering shows a system tooltip after a brief delay. Limitation: ugly default styling, can&rsquo;t be customized.</p>

<p><strong>Custom CSS tooltip (full control):</strong></p>
<pre><code>&lt;span class="tooltip" data-tooltip="Click to learn more"&gt;
  Hover me
&lt;/span&gt;

&lt;style&gt;
  .tooltip {
    position: relative;
    border-bottom: 1px dotted #666;
    cursor: help;
  }
  .tooltip::after {
    content: attr(data-tooltip);
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
    transition: opacity 0.2s, transform 0.2s;
  }
  .tooltip::before {
    /* Arrow pointing down to the trigger */
    content: "";
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #333;
    margin-bottom: -8px;
    opacity: 0;
    transition: opacity 0.2s;
  }
  .tooltip:hover::after,
  .tooltip:focus-visible::after,
  .tooltip:hover::before,
  .tooltip:focus-visible::before {
    opacity: 1;
    transform: translateX(-50%) translateY(-8px);
  }
&lt;/style&gt;</code></pre>

<p><strong>Why this works better than <code>title</code>:</strong></p>
<ul>
  <li>Fully styleable &mdash; colors, fonts, animations, arrows.</li>
  <li>Shows on focus too (<code>:focus-visible</code>) for keyboard users.</li>
  <li>Consistent across browsers and OS.</li>
</ul>

<p><strong>Modern accessible solution: Popover API</strong> (2026 baseline):</p>
<pre><code>&lt;button popovertarget="tip1" aria-describedby="tip1"&gt;Help&lt;/button&gt;
&lt;div id="tip1" popover="hint"&gt;Click to undo&lt;/div&gt;</code></pre>

<p>The Popover API gives proper focus management, dismiss-on-Escape, and top-layer rendering &mdash; without z-index battles. CSS Anchor Positioning lets you position the popover relative to its trigger automatically.</p>
'''

ANSWERS[65] = r'''
<p>The <code>transform</code> property applies 2D or 3D transformations to elements &mdash; translate (move), rotate, scale, skew, and matrix combinations. It&rsquo;s GPU-accelerated, making it perfect for smooth animations.</p>

<pre><code>.element {
  transform: translateX(100px);             /* move right */
  transform: translate(50px, 20px);          /* move x and y */
  transform: rotate(45deg);                  /* rotate */
  transform: scale(1.5);                     /* scale up */
  transform: skewX(20deg);                   /* skew */
}

/* Multiple transforms — applied left to right */
.combined {
  transform: rotate(45deg) scale(1.2) translateX(50px);
}</code></pre>

<p><strong>Common transform functions:</strong></p>
<table>
  <tr><th>Function</th><th>Effect</th></tr>
  <tr><td><code>translate(x, y)</code></td><td>Move element without affecting layout</td></tr>
  <tr><td><code>translateX(n)</code> / <code>translateY(n)</code></td><td>Single-axis move</td></tr>
  <tr><td><code>rotate(angle)</code></td><td>Rotate around center</td></tr>
  <tr><td><code>scale(n)</code></td><td>Resize (1.5 = 150%)</td></tr>
  <tr><td><code>skewX(angle)</code> / <code>skewY(angle)</code></td><td>Slant the element</td></tr>
  <tr><td><code>matrix(...)</code></td><td>All of the above in one</td></tr>
</table>

<p><strong>Why transform is preferred for animations:</strong></p>
<pre><code>/* JANKY — triggers layout recalc on every frame */
@keyframes slide-bad {
  to { left: 100px; }
}

/* SMOOTH — only compositor work, GPU-accelerated */
@keyframes slide-good {
  to { transform: translateX(100px); }
}</code></pre>

<p>Properties like <code>top</code>, <code>left</code>, <code>width</code>, <code>height</code> trigger expensive layout recalculations on every frame. <code>transform</code> and <code>opacity</code> only trigger compositing &mdash; the GPU handles the change without involving the CPU.</p>

<p><strong>3D transforms:</strong></p>
<pre><code>.card {
  transform: perspective(800px) rotateY(45deg);
  /* perspective adds 3D depth */
}</code></pre>

<p>Combined with <code>backface-visibility</code> and <code>transform-style: preserve-3d</code>, transforms enable card flips, 3D rotations, and parallax effects.</p>
'''

ANSWERS[66] = r'''
<p>Use the <code>rotate()</code> function within <code>transform</code>. Positive values rotate clockwise; negative values rotate counter-clockwise.</p>

<pre><code>&lt;div class="square"&gt;Tilted&lt;/div&gt;
&lt;div class="badge"&gt;NEW&lt;/div&gt;
&lt;div class="logo"&gt;&#x21BB;&lt;/div&gt;

&lt;style&gt;
  /* Static rotation */
  .square {
    transform: rotate(15deg);
    background: navy;
    color: white;
    padding: 1em;
  }

  /* Negative rotation (counter-clockwise) */
  .badge {
    transform: rotate(-30deg);
    background: red;
    color: white;
    padding: 0.3em 0.8em;
  }

  /* Hover rotation with transition */
  .logo {
    display: inline-block;
    transition: transform 0.3s;
  }
  .logo:hover {
    transform: rotate(360deg);
  }

  /* Continuous rotation animation */
  .spinner {
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
&lt;/style&gt;</code></pre>

<p><strong>Angle units:</strong></p>
<table>
  <tr><th>Unit</th><th>Example</th></tr>
  <tr><td><code>deg</code> (degrees)</td><td><code>rotate(45deg)</code> &mdash; most common</td></tr>
  <tr><td><code>turn</code></td><td><code>rotate(0.25turn)</code> &mdash; quarter turn = 90deg</td></tr>
  <tr><td><code>rad</code> (radians)</td><td><code>rotate(1rad)</code> &mdash; ~57.3 degrees</td></tr>
  <tr><td><code>grad</code></td><td><code>rotate(100grad)</code> &mdash; 100 grad = 90deg (rare)</td></tr>
</table>

<p><strong>Standalone <code>rotate</code> property (modern):</strong></p>
<pre><code>.element {
  rotate: 45deg;
  /* Same as transform: rotate(45deg), but doesn't reset translate/scale */
}</code></pre>

<p>The standalone <code>rotate</code> property is more convenient when you also use <code>transform</code> for translation or scaling &mdash; you can adjust each independently.</p>

<p><strong>Rotation around a custom point:</strong></p>
<pre><code>.element {
  transform-origin: top left;     /* default is center center */
  transform: rotate(45deg);
}</code></pre>

<p>By default elements rotate around their center; <code>transform-origin</code> changes the pivot point.</p>
'''

ANSWERS[67] = r'''
<p>Use the <code>:focus</code> or <code>:focus-visible</code> pseudo-class. They apply when an element receives keyboard or programmatic focus &mdash; essential for accessibility.</p>

<pre><code>&lt;input type="text" placeholder="Type here"&gt;
&lt;button&gt;Submit&lt;/button&gt;

&lt;style&gt;
  /* Style on focus (keyboard or click) */
  input:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
    background: #f0f8ff;
  }

  /* Modern: only show focus ring on keyboard, not click */
  button:focus-visible {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
  }
&lt;/style&gt;</code></pre>

<p><strong>The crucial <code>:focus-visible</code> distinction</strong>:</p>
<table>
  <tr><th></th><th><code>:focus</code></th><th><code>:focus-visible</code></th></tr>
  <tr><td>Triggers on click</td><td>Yes</td><td>No (browser heuristic)</td></tr>
  <tr><td>Triggers on Tab</td><td>Yes</td><td>Yes</td></tr>
  <tr><td>Use for</td><td>Always-visible focus indicator</td><td>Modern accessibility-friendly</td></tr>
</table>

<pre><code>/* Best practice — show focus ring only when needed */
button {
  outline: none;     /* remove default ring */
}
button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}</code></pre>

<p>Mouse users who click a button don&rsquo;t see a focus ring (it would look messy), but Tab users do (essential for accessibility).</p>

<p><strong>Never remove focus styles entirely</strong>:</p>
<pre><code>/* WRONG — breaks keyboard navigation for everyone */
button:focus { outline: none; }

/* RIGHT — replace the default ring with a custom one */
button:focus-visible {
  outline: 3px solid #ff6b35;
  outline-offset: 3px;
}</code></pre>

<p>Without focus indicators, keyboard users can&rsquo;t tell which element is selected &mdash; a major WCAG failure.</p>

<p><strong>Focus within a parent</strong> &mdash; <code>:focus-within</code> matches if any descendant has focus:</p>
<pre><code>.form-group:focus-within {
  background: #f0f8ff;
  border-color: #0066cc;
}</code></pre>

<p>Useful for highlighting an entire form group when the user focuses any input inside.</p>
'''

ANSWERS[68] = r'''
<p>CSS animations use <code>@keyframes</code> to define stages and the <code>animation</code> property to apply them. Unlike transitions (which animate between states), animations run autonomously.</p>

<pre><code>&lt;div class="bouncy"&gt;Bouncing!&lt;/div&gt;
&lt;div class="spinner"&gt;Loading...&lt;/div&gt;

&lt;style&gt;
  /* Define keyframes */
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-20px); }
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
  }

  /* Apply animations */
  .bouncy {
    animation: bounce 1s ease-in-out infinite;
  }
  .spinner {
    animation: spin 1s linear infinite;
  }
&lt;/style&gt;</code></pre>

<p><strong>Animation shorthand:</strong></p>
<pre><code>animation: name duration timing-function delay iteration-count direction fill-mode;

/* Examples */
animation: fade 0.5s ease-in;
animation: slide 0.3s ease-out 0.2s forwards;
animation: pulse 1s ease-in-out infinite;</code></pre>

<table>
  <tr><th>Property</th><th>Values</th></tr>
  <tr><td><code>animation-duration</code></td><td><code>1s</code>, <code>500ms</code></td></tr>
  <tr><td><code>animation-timing-function</code></td><td><code>linear</code>, <code>ease</code>, <code>ease-in-out</code>, <code>cubic-bezier(...)</code></td></tr>
  <tr><td><code>animation-delay</code></td><td><code>0.5s</code> &mdash; wait before starting</td></tr>
  <tr><td><code>animation-iteration-count</code></td><td><code>1</code>, <code>3</code>, <code>infinite</code></td></tr>
  <tr><td><code>animation-direction</code></td><td><code>normal</code>, <code>reverse</code>, <code>alternate</code></td></tr>
  <tr><td><code>animation-fill-mode</code></td><td><code>forwards</code> (keep end state), <code>backwards</code>, <code>both</code></td></tr>
</table>

<p><strong>Multi-stage keyframes:</strong></p>
<pre><code>@keyframes complex {
  0%   { opacity: 0; transform: scale(0.5); }
  50%  { opacity: 1; transform: scale(1.1); }
  100% { transform: scale(1); }
}</code></pre>

<p><strong>Respect user preferences:</strong></p>
<pre><code>@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}</code></pre>

<p>Users with motion sensitivities benefit greatly from this single rule.</p>
'''

ANSWERS[69] = r'''
<p>Use the <strong>descendant combinator</strong> (a space) to target all elements inside a parent, regardless of nesting depth.</p>

<pre><code>&lt;article&gt;
  &lt;h2&gt;Title&lt;/h2&gt;
  &lt;div&gt;
    &lt;p&gt;Nested paragraph&lt;/p&gt;
  &lt;/div&gt;
  &lt;p&gt;Direct paragraph&lt;/p&gt;
&lt;/article&gt;

&lt;style&gt;
  /* Selects ALL paragraphs inside article, at any depth */
  article p {
    line-height: 1.6;
    color: #333;
  }
&lt;/style&gt;</code></pre>

<p><strong>CSS combinators:</strong></p>
<table>
  <tr><th>Combinator</th><th>Selects</th></tr>
  <tr><td><code>A B</code> (descendant)</td><td>All B inside A, any depth</td></tr>
  <tr><td><code>A &gt; B</code> (child)</td><td>Direct children of A only</td></tr>
  <tr><td><code>A + B</code> (adjacent sibling)</td><td>B immediately after A</td></tr>
  <tr><td><code>A ~ B</code> (general sibling)</td><td>All B siblings after A</td></tr>
</table>

<p><strong>Examples:</strong></p>
<pre><code>/* All links inside nav (any depth) */
nav a { color: navy; }

/* Only direct child links */
nav &gt; a { font-weight: bold; }

/* The &lt;p&gt; immediately after each &lt;h2&gt; */
h2 + p { font-size: 1.1em; }

/* All &lt;p&gt; siblings after &lt;h2&gt; */
h2 ~ p { color: gray; }</code></pre>

<p><strong>Specificity stacks</strong> &mdash; deeper selectors are more specific:</p>
<pre><code>p              { color: black; }     /* 0,0,1 */
article p      { color: navy; }       /* 0,0,2 */
.post p        { color: red; }        /* 0,1,1 */
article .post p { color: green; }     /* 0,1,2 */</code></pre>

<p>Each part of the selector adds specificity. Higher specificity wins; ties go to the later rule.</p>

<p><strong>Modern alternatives:</strong> <code>:is()</code>, <code>:where()</code>, and <code>:has()</code> let you write cleaner selectors without specificity surprises:</p>
<pre><code>:is(article, section) p { line-height: 1.6; }   /* either parent */
:where(article) p { color: gray; }                /* same but 0 specificity */</code></pre>
'''

ANSWERS[70] = r'''
<p>Use the <code>text-shadow</code> property to add shadows to text. Same syntax as <code>box-shadow</code> but without spread or inset.</p>

<pre><code>&lt;h1 class="emboss"&gt;Embossed&lt;/h1&gt;
&lt;h2 class="glow"&gt;Glowing&lt;/h2&gt;
&lt;h3 class="layered"&gt;Layered&lt;/h3&gt;

&lt;style&gt;
  /* Subtle shadow for readability */
  .emboss {
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  }

  /* Glowing effect */
  .glow {
    color: white;
    text-shadow:
      0 0 5px #fff,
      0 0 10px #ff6b35,
      0 0 20px #ff6b35;
  }

  /* Stacked shadows for depth */
  .layered {
    color: white;
    text-shadow:
      0 1px 0 #ccc,
      0 2px 0 #c9c9c9,
      0 3px 0 #bbb,
      0 4px 6px rgba(0, 0, 0, 0.3);
  }
&lt;/style&gt;</code></pre>

<p><strong>Syntax:</strong></p>
<pre><code>text-shadow: x-offset y-offset blur color;</code></pre>

<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td>x-offset</td><td>Horizontal offset (positive = right)</td></tr>
  <tr><td>y-offset</td><td>Vertical offset (positive = down)</td></tr>
  <tr><td>blur</td><td>Blur radius (larger = softer; default 0)</td></tr>
  <tr><td>color</td><td>Shadow color</td></tr>
</table>

<p><strong>Common patterns:</strong></p>
<pre><code>/* Make light text readable on a busy background */
.over-image {
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.6);
}

/* 3D effect */
.three-d {
  color: red;
  text-shadow:
    1px 1px 0 #b30000,
    2px 2px 0 #800000,
    3px 3px 0 #4d0000;
}

/* Outline (no native CSS text-stroke widely supported) */
.outline {
  color: white;
  text-shadow:
    -1px -1px 0 #000,
     1px -1px 0 #000,
    -1px  1px 0 #000,
     1px  1px 0 #000;
}</code></pre>

<p><strong>Modern: <code>-webkit-text-stroke</code></strong> for outlined text:</p>
<pre><code>.outlined {
  color: white;
  -webkit-text-stroke: 2px black;
}</code></pre>

<p>Better support arrives every year for true text outlines &mdash; until then, the multi-shadow trick covers most cases.</p>
'''

ANSWERS[71] = r'''
<p>CSS Grid with <code>auto-fit</code> and <code>minmax</code> creates responsive grids that adapt to any viewport size &mdash; with no media queries.</p>

<pre><code>&lt;section class="grid"&gt;
  &lt;div class="item"&gt;Item 1&lt;/div&gt;
  &lt;div class="item"&gt;Item 2&lt;/div&gt;
  &lt;div class="item"&gt;Item 3&lt;/div&gt;
  &lt;div class="item"&gt;Item 4&lt;/div&gt;
  &lt;div class="item"&gt;Item 5&lt;/div&gt;
  &lt;div class="item"&gt;Item 6&lt;/div&gt;
&lt;/section&gt;

&lt;style&gt;
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }
  .item {
    background: #f0f0f0;
    padding: 1.5em;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>

<p><strong>The magic formula:</strong> <code>repeat(auto-fit, minmax(250px, 1fr))</code></p>
<ul>
  <li><code>auto-fit</code> &mdash; create as many columns as fit.</li>
  <li><code>minmax(250px, 1fr)</code> &mdash; each column at least 250px, grows to fill remaining space equally.</li>
  <li>Items wrap to new rows when there&rsquo;s no room for another full-width column.</li>
</ul>

<p>The result: 4 columns on wide screens, 3 on tablet, 2 on phone, 1 on tiny screens &mdash; all from one rule.</p>

<p><strong>auto-fit vs auto-fill</strong>:</p>
<table>
  <tr><th></th><th><code>auto-fit</code></th><th><code>auto-fill</code></th></tr>
  <tr><td>With few items</td><td>Stretches them to fill row</td><td>Leaves empty space</td></tr>
  <tr><td>Use when</td><td>Want items to expand</td><td>Want consistent sizes</td></tr>
</table>

<p><strong>Common Grid properties:</strong></p>
<pre><code>.grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;       /* 3 columns at proportions */
  grid-template-rows: 100px auto;
  gap: 1em;                                  /* spacing between items */
  grid-auto-flow: row;                       /* fill row by row (default) */
}

/* Span multiple cells */
.featured {
  grid-column: span 2;       /* takes 2 columns */
  grid-row: span 2;          /* takes 2 rows */
}</code></pre>

<p>Grid is more powerful than Flexbox for 2D layouts. Use Flexbox for 1D (rows or columns); Grid for 2D (rows AND columns).</p>
'''

ANSWERS[72] = r'''
<p>Several techniques make an element fill its parent&rsquo;s height. The right one depends on the parent&rsquo;s context.</p>

<p><strong>1. Percentage height (parent must have explicit height):</strong></p>
<pre><code>.parent {
  height: 400px;
}
.child {
  height: 100%;       /* fills parent */
}</code></pre>

<p>Doesn&rsquo;t work if the parent has <code>height: auto</code> &mdash; percentages need a defined parent height to calculate against.</p>

<p><strong>2. Viewport units (relative to viewport, not parent):</strong></p>
<pre><code>.fullscreen {
  height: 100vh;       /* full viewport height */
  min-height: 100vh;
}</code></pre>

<p>Useful for hero sections and modals. Watch out for mobile browsers where <code>100vh</code> includes URL bar height &mdash; modern <code>100dvh</code> (dynamic viewport height) handles this:</p>
<pre><code>.fullscreen {
  height: 100dvh;       /* mobile-aware viewport height */
}</code></pre>

<p><strong>3. Flexbox &mdash; child fills flex container:</strong></p>
<pre><code>.parent {
  display: flex;
  height: 400px;
  flex-direction: column;
}
.child {
  flex: 1;           /* takes remaining space */
}</code></pre>

<p><strong>4. Grid &mdash; child fills grid cell:</strong></p>
<pre><code>.parent {
  display: grid;
  height: 100vh;
  grid-template-rows: auto 1fr auto;   /* header, content, footer */
}
.content {
  /* automatically fills the 1fr row */
}</code></pre>

<p><strong>5. Absolute positioning:</strong></p>
<pre><code>.parent {
  position: relative;
}
.child {
  position: absolute;
  top: 0;
  bottom: 0;
}</code></pre>

<p>Stretches between top: 0 and bottom: 0 of the relative parent.</p>

<p><strong>The "sticky footer" pattern:</strong></p>
<pre><code>html, body { height: 100%; margin: 0; }
body {
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;             /* fills space, pushing footer down */
}</code></pre>

<p>Body fills the viewport; main grows to fill remaining space; footer stays at the bottom even with little content.</p>
'''

ANSWERS[73] = r'''
<p>Use <code>position: fixed</code> to pin a sidebar to one edge of the viewport, regardless of scroll.</p>

<pre><code>&lt;aside class="fixed-sidebar"&gt;
  &lt;nav&gt;
    &lt;a href="#section1"&gt;Section 1&lt;/a&gt;
    &lt;a href="#section2"&gt;Section 2&lt;/a&gt;
    &lt;a href="#section3"&gt;Section 3&lt;/a&gt;
  &lt;/nav&gt;
&lt;/aside&gt;

&lt;main&gt;
  &lt;section id="section1"&gt;Content...&lt;/section&gt;
  &lt;section id="section2"&gt;Content...&lt;/section&gt;
  &lt;section id="section3"&gt;Content...&lt;/section&gt;
&lt;/main&gt;

&lt;style&gt;
  .fixed-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 250px;
    height: 100vh;
    padding: 1em;
    background: #2c3e50;
    color: white;
    overflow-y: auto;       /* scroll if content exceeds viewport */
  }
  .fixed-sidebar nav {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
  }
  .fixed-sidebar a {
    color: white;
    padding: 0.5em;
    text-decoration: none;
    border-radius: 4px;
  }
  .fixed-sidebar a:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  /* Critical: offset main content to avoid overlap */
  main {
    margin-left: 250px;
    padding: 2em;
  }

  /* Mobile: hide sidebar or convert to drawer */
  @media (max-width: 768px) {
    .fixed-sidebar { display: none; }
    main { margin-left: 0; }
  }
&lt;/style&gt;</code></pre>

<p><strong>Critical patterns:</strong></p>
<ul>
  <li><strong>Offset main content</strong> with <code>margin-left</code> equal to sidebar width &mdash; otherwise content hides behind it.</li>
  <li><strong>Set <code>height: 100vh</code></strong> on the sidebar so it spans the full viewport.</li>
  <li><strong>Add <code>overflow-y: auto</code></strong> for long sidebar content that needs to scroll independently.</li>
  <li><strong>Mobile fallback</strong> &mdash; hide sidebar or convert to a slide-out drawer below 768px.</li>
</ul>

<p><strong>Modern alternative: <code>position: sticky</code></strong>:</p>
<pre><code>.sticky-sidebar {
  position: sticky;
  top: 1em;
  height: calc(100vh - 2em);
}</code></pre>

<p>Sticky takes natural space (no margin offset needed) and only sticks once scrolled to the threshold &mdash; better in many layouts than fixed.</p>
'''

ANSWERS[74] = r'''
<p>Use <code>background-image</code> with <code>background-size: cover</code> on a full-viewport element to fill the screen with an image.</p>

<pre><code>&lt;section class="hero"&gt;
  &lt;h1&gt;Welcome&lt;/h1&gt;
  &lt;p&gt;Discover something amazing.&lt;/p&gt;
&lt;/section&gt;

&lt;style&gt;
  .hero {
    background-image: url("/landscape.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
    padding: 2em;
  }
&lt;/style&gt;</code></pre>

<p><strong>Key properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>background-size: cover</code></td><td>Image fills the box, cropping if needed</td></tr>
  <tr><td><code>background-size: contain</code></td><td>Image fits entirely, may letterbox</td></tr>
  <tr><td><code>background-position: center</code></td><td>Focal point of the image</td></tr>
  <tr><td><code>background-repeat: no-repeat</code></td><td>Don&rsquo;t tile (essential for full-screen)</td></tr>
  <tr><td><code>background-attachment: fixed</code></td><td>Image stays put while content scrolls</td></tr>
</table>

<p><strong>Dark overlay for text readability:</strong></p>
<pre><code>.hero {
  background:
    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url("/landscape.jpg") center / cover no-repeat;
  color: white;
}</code></pre>

<p>Layered backgrounds: a 50%-opaque black gradient on top of the image. Text becomes readable regardless of the image content.</p>

<p><strong>Body-level full-screen:</strong></p>
<pre><code>body {
  margin: 0;
  background: url("/bg.jpg") center / cover no-repeat fixed;
  min-height: 100vh;
}</code></pre>

<p><code>background-attachment: fixed</code> creates a parallax effect &mdash; the image stays still while content scrolls over it.</p>

<p><strong>Performance tips:</strong></p>
<ul>
  <li>Preload the image: <code>&lt;link rel="preload" as="image" href="/bg.jpg"&gt;</code></li>
  <li>Use modern formats (AVIF, WebP) &mdash; 30-70% smaller than JPEG.</li>
  <li>Provide multiple resolutions via <code>image-set()</code> in CSS.</li>
  <li>Compress aggressively &mdash; users won&rsquo;t notice slight artifacts on a hero background.</li>
</ul>
'''

ANSWERS[75] = r'''
<p>Use <code>line-height</code> to control the vertical space between lines of text. The value can be a number, length, or percentage.</p>

<pre><code>&lt;p class="tight"&gt;Tight line spacing for headings.&lt;/p&gt;
&lt;p class="normal"&gt;Normal body text spacing.&lt;/p&gt;
&lt;p class="loose"&gt;Loose spacing for emphasis.&lt;/p&gt;

&lt;style&gt;
  .tight  { line-height: 1.2; }     /* tighter — for headings */
  .normal { line-height: 1.5; }     /* readable for body */
  .loose  { line-height: 2; }       /* spacious */
&lt;/style&gt;</code></pre>

<p><strong>Value types:</strong></p>
<table>
  <tr><th>Format</th><th>Example</th><th>Behavior</th></tr>
  <tr><td>Unitless number</td><td><code>1.5</code></td><td>Multiplies font-size; inherits properly</td></tr>
  <tr><td>Length</td><td><code>24px</code>, <code>1.5em</code></td><td>Fixed; doesn&rsquo;t scale with inherited font-size</td></tr>
  <tr><td>Percentage</td><td><code>150%</code></td><td>Of font-size at definition time</td></tr>
  <tr><td>Keyword</td><td><code>normal</code></td><td>Browser default (~1.2)</td></tr>
</table>

<p><strong>Always prefer unitless values</strong> &mdash; they inherit correctly:</p>
<pre><code>body { line-height: 1.5; }     /* inherited as a multiplier */
h1   { font-size: 32px; }       /* line-height becomes 48px */
p    { font-size: 16px; }       /* line-height becomes 24px */</code></pre>

<p>If you used <code>line-height: 24px</code> on body, all elements would inherit the literal 24px regardless of their font size &mdash; usually wrong.</p>

<p><strong>Recommended values:</strong></p>
<table>
  <tr><th>Use case</th><th>Line height</th></tr>
  <tr><td>Headings</td><td>1.1&ndash;1.3</td></tr>
  <tr><td>Body text</td><td>1.5&ndash;1.7</td></tr>
  <tr><td>UI labels (single line)</td><td>1 (or matches button height)</td></tr>
  <tr><td>Long-form articles</td><td>1.6&ndash;1.8</td></tr>
</table>

<p>The WCAG accessibility guideline recommends at least 1.5 line-height for body text. Tighter values cramp characters; looser values waste space and look airy.</p>

<p><strong>Vertically center single-line text</strong> by matching line-height to height:</p>
<pre><code>.button {
  height: 40px;
  line-height: 40px;     /* centers the text vertically */
  text-align: center;
}</code></pre>

<p>Doesn&rsquo;t work for multi-line content &mdash; use Flexbox instead in that case.</p>
'''

ANSWERS[76] = r'''
<p>Combine <code>border-radius</code> for rounded corners with <code>box-shadow</code> for the shadow:</p>
<pre><code>.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;                              /* rounded corners */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);       /* soft shadow */
  padding: 1.5em;
  background: white;
}</code></pre>
<p><strong>The combo creates an "elevated card" look:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>border-radius: 8px</code></td><td>Rounds all corners</td></tr>
  <tr><td><code>box-shadow: 0 4px 12px ...</code></td><td>Soft drop shadow below</td></tr>
  <tr><td><code>border</code></td><td>(Optional) thin border for definition</td></tr>
</table>
<p><strong>Variations:</strong></p>
<pre><code>/* Pill shape (very rounded) */
.pill { border-radius: 999px; }

/* Different corner radii */
.tab {
  border-radius: 8px 8px 0 0;
  /* top-left top-right bottom-right bottom-left */
}

/* Larger shadow for floating elements */
.modal {
  border-radius: 12px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

/* Multiple shadows for layered depth */
.fancy-card {
  border-radius: 8px;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.12),
    0 1px 2px rgba(0, 0, 0, 0.24);
}</code></pre>
<p>Material Design and most design systems use this pattern extensively. Subtle shadows with low opacity (0.05-0.15) feel modern; heavy shadows feel dated.</p>
'''

ANSWERS[77] = r'''
<p>CSS variables (officially <strong>custom properties</strong>) let you store values and reuse them throughout your stylesheet. Define with <code>--</code> prefix; access with <code>var()</code>.</p>
<pre><code>:root {
  --primary-color: #0066cc;
  --secondary-color: #ff6b35;
  --spacing: 1rem;
  --radius: 8px;
}

.btn {
  background: var(--primary-color);
  padding: var(--spacing);
  border-radius: var(--radius);
}

.alert {
  background: var(--secondary-color);
  padding: var(--spacing);
}</code></pre>
<p><strong>Why use them:</strong></p>
<ul>
  <li><strong>Centralize values</strong> &mdash; change a color in one place, update everywhere.</li>
  <li><strong>Theming</strong> &mdash; switch entire color schemes (dark mode, brand themes) by changing variables.</li>
  <li><strong>JavaScript can read/write them</strong> &mdash; runtime customization.</li>
  <li><strong>Cascade and inherit</strong> &mdash; like all CSS properties.</li>
</ul>
<p><strong>Dark mode example:</strong></p>
<pre><code>:root {
  --bg: white;
  --fg: #333;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --fg: #f0f0f0;
  }
}

body {
  background: var(--bg);
  color: var(--fg);
}</code></pre>
<p><strong>Fallback values</strong> &mdash; <code>var()</code> accepts a second argument:</p>
<pre><code>color: var(--primary-color, blue);   /* use blue if --primary-color undefined */</code></pre>
<p><strong>Read from JavaScript:</strong></p>
<pre><code>const root = document.documentElement;
root.style.setProperty("--primary-color", "#ff0000");</code></pre>
<p>Variables are dynamic at runtime &mdash; unlike Sass variables, which are compile-time only.</p>
'''

ANSWERS[78] = r'''
<p>Use <strong>state pseudo-classes</strong> to style elements based on their interactive state:</p>
<pre><code>.btn {
  background: #0066cc;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover    { background: #004999; }       /* mouse over */
.btn:focus    { outline: 2px solid #ff6b35; }  /* keyboard focus */
.btn:active   { transform: scale(0.98); }     /* clicking */
.btn:disabled { background: #ccc; cursor: not-allowed; }   /* disabled */</code></pre>
<p><strong>Common state pseudo-classes:</strong></p>
<table>
  <tr><th>Pseudo-class</th><th>State</th></tr>
  <tr><td><code>:hover</code></td><td>Mouse over element</td></tr>
  <tr><td><code>:focus</code></td><td>Has keyboard or click focus</td></tr>
  <tr><td><code>:focus-visible</code></td><td>Focused via keyboard (not mouse)</td></tr>
  <tr><td><code>:active</code></td><td>Currently being clicked</td></tr>
  <tr><td><code>:visited</code></td><td>Link previously visited</td></tr>
  <tr><td><code>:checked</code></td><td>Checkbox/radio is checked</td></tr>
  <tr><td><code>:disabled</code></td><td>Form element is disabled</td></tr>
  <tr><td><code>:required</code> / <code>:optional</code></td><td>Form field requirement</td></tr>
  <tr><td><code>:valid</code> / <code>:invalid</code></td><td>Validation state</td></tr>
</table>
<pre><code>/* Style invalid input fields */
input:invalid {
  border-color: red;
  background: #ffe6e6;
}

/* Style checked custom checkboxes */
input[type="checkbox"]:checked + label {
  font-weight: bold;
}

/* Show focus only for keyboard users */
.btn:focus { outline: none; }              /* hide for mouse */
.btn:focus-visible { outline: 2px solid; } /* show for keyboard */</code></pre>
<p>Use <code>:focus-visible</code> rather than <code>:focus</code> alone &mdash; it shows focus rings for keyboard users (who need them) but hides them for mouse clicks (which look noisy).</p>
'''

ANSWERS[79] = r'''
<p>Use the <code>:hover</code> state on a parent or sibling combined with the descendant or sibling selector:</p>
<p><strong>Show on hover of parent</strong> &mdash; the most common pattern:</p>
<pre><code>&lt;div class="card"&gt;
  &lt;img src="photo.jpg" alt=""&gt;
  &lt;button class="overlay-btn"&gt;Edit&lt;/button&gt;
&lt;/div&gt;

&lt;style&gt;
  .overlay-btn {
    opacity: 0;
    transition: opacity 0.2s;
  }
  .card:hover .overlay-btn {
    opacity: 1;          /* show when hovering the card */
  }
&lt;/style&gt;</code></pre>
<p><strong>Show on hover of sibling</strong> &mdash; using the adjacent sibling combinator (<code>+</code>) or general sibling combinator (<code>~</code>):</p>
<pre><code>&lt;input type="checkbox" id="toggle"&gt;
&lt;label for="toggle"&gt;Click me&lt;/label&gt;
&lt;div class="message"&gt;Hidden message&lt;/div&gt;

&lt;style&gt;
  .message {
    display: none;
  }
  /* When checkbox is checked, show the message */
  #toggle:checked ~ .message {
    display: block;
  }

  /* On hover of label, change the message style */
  label:hover ~ .message {
    color: blue;
  }
&lt;/style&gt;</code></pre>
<p><strong>Tooltip pattern</strong> &mdash; tooltip appears on hover:</p>
<pre><code>.tooltip-trigger {
  position: relative;
}
.tooltip {
  position: absolute;
  bottom: 100%;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}
.tooltip-trigger:hover .tooltip {
  opacity: 1;
}</code></pre>
<p><strong>Modern <code>:has()</code> selector</strong> opens up "show parent on child hover":</p>
<pre><code>/* Style parent when it contains a hovered link */
.card:has(a:hover) { border-color: blue; }</code></pre>
<p>This is the so-called "parent selector" &mdash; finally available in CSS as of 2023.</p>
'''

ANSWERS[80] = r'''
<p>Use the CSS <code>columns</code> property for newspaper-style multi-column text:</p>
<pre><code>.article {
  columns: 3 250px;            /* 3 columns, each at least 250px */
  column-gap: 2em;
  column-rule: 1px solid #ddd;
}</code></pre>
<p><strong>Properties available:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>column-count</code></td><td>Exact number of columns</td></tr>
  <tr><td><code>column-width</code></td><td>Minimum column width; browser computes count</td></tr>
  <tr><td><code>columns</code></td><td>Shorthand for both</td></tr>
  <tr><td><code>column-gap</code></td><td>Space between columns</td></tr>
  <tr><td><code>column-rule</code></td><td>Vertical line between columns (border-like)</td></tr>
  <tr><td><code>column-span: all</code></td><td>Element spans across all columns</td></tr>
</table>
<pre><code>.article h2 {
  column-span: all;            /* heading spans all columns */
  margin-bottom: 1em;
}
.article p {
  break-inside: avoid;          /* don't split paragraphs across columns */
}</code></pre>
<p><strong>Columns vs Grid &mdash; pick the right tool:</strong></p>
<ul>
  <li><strong>CSS columns</strong> &mdash; for fluid prose (newspaper article, FAQ list, tag cloud) where text flows naturally between columns.</li>
  <li><strong>CSS Grid</strong> &mdash; for structured items (cards, photo gallery, dashboard) where each item is independent.</li>
</ul>
<p>For card grids, Grid&rsquo;s <code>auto-fit</code> + <code>minmax</code> is more powerful:</p>
<pre><code>.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}</code></pre>
<p>Use <code>columns</code> only when the content really should flow continuously between columns &mdash; like body text in a magazine layout.</p>
'''

ANSWERS[81] = r'''
<p>The cleanest modern pattern uses CSS Grid with <code>auto-fit</code> + <code>minmax</code> &mdash; images reflow automatically without media queries:</p>
<pre><code>&lt;section class="gallery"&gt;
  &lt;img src="img1.jpg" alt=""&gt;
  &lt;img src="img2.jpg" alt=""&gt;
  &lt;img src="img3.jpg" alt=""&gt;
  &lt;img src="img4.jpg" alt=""&gt;
  &lt;img src="img5.jpg" alt=""&gt;
  &lt;img src="img6.jpg" alt=""&gt;
&lt;/section&gt;

&lt;style&gt;
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }
  .gallery img {
    width: 100%;
    height: 200px;
    object-fit: cover;          /* crop, preserve aspect */
    border-radius: 8px;
    display: block;
    transition: transform 0.3s;
  }
  .gallery img:hover {
    transform: scale(1.05);
  }
&lt;/style&gt;</code></pre>
<p><strong>How it adapts:</strong></p>
<ul>
  <li><code>auto-fit</code> &mdash; fits as many columns as possible at the minimum width.</li>
  <li><code>minmax(200px, 1fr)</code> &mdash; columns at least 200px; expand to fill extra space.</li>
  <li>On wide screens: 5+ columns. On phone: 1-2 columns. Browser computes automatically.</li>
</ul>
<p><strong>Flexbox alternative</strong> &mdash; same effect, different syntax:</p>
<pre><code>.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.gallery img {
  flex: 1 1 200px;
  height: 200px;
  object-fit: cover;
}</code></pre>
<p><strong>Performance:</strong> add <code>loading="lazy"</code> to <code>&lt;img&gt;</code> tags below the fold to defer loading until they&rsquo;re close to viewport. Use <code>srcset</code> for responsive image sizes.</p>
'''

ANSWERS[82] = r'''
<p>Use the <code>:last-child</code> pseudo-class:</p>
<pre><code>li:last-child {
  border-bottom: none;
  margin-bottom: 0;
}</code></pre>
<pre><code>&lt;ul&gt;
  &lt;li&gt;First&lt;/li&gt;
  &lt;li&gt;Middle&lt;/li&gt;
  &lt;li&gt;Last (no border-bottom)&lt;/li&gt;
&lt;/ul&gt;</code></pre>
<p><strong>Common pattern: remove trailing borders/separators on last items</strong>:</p>
<pre><code>.list-item {
  padding: 1em 0;
  border-bottom: 1px solid #eee;
}
.list-item:last-child {
  border-bottom: none;
}</code></pre>
<p><strong>Position-based selectors:</strong></p>
<table>
  <tr><th>Selector</th><th>Matches</th></tr>
  <tr><td><code>:first-child</code></td><td>First child of parent</td></tr>
  <tr><td><code>:last-child</code></td><td>Last child of parent</td></tr>
  <tr><td><code>:only-child</code></td><td>The only child (no siblings)</td></tr>
  <tr><td><code>:nth-child(n)</code></td><td>Specific position</td></tr>
  <tr><td><code>:nth-last-child(n)</code></td><td>Counted from the end</td></tr>
  <tr><td><code>:last-of-type</code></td><td>Last sibling of its element type</td></tr>
</table>
<p><strong><code>:last-of-type</code></strong> distinguishes from siblings of different types:</p>
<pre><code>&lt;article&gt;
  &lt;p&gt;First paragraph&lt;/p&gt;
  &lt;p&gt;Last paragraph&lt;/p&gt;
  &lt;footer&gt;Footer info&lt;/footer&gt;     /* this is the last-child */
&lt;/article&gt;

p:last-child  { /* matches NOTHING — &lt;footer&gt; is last */ }
p:last-of-type { /* matches the second &lt;p&gt; */ }</code></pre>
<p>Use <code>:last-child</code> when the element is genuinely the last of all children. Use <code>:last-of-type</code> when you want the last of a specific element type.</p>
'''

ANSWERS[83] = r'''
<p>A responsive nav stays horizontal on desktop and collapses on mobile. Flexbox handles the desktop layout cleanly:</p>
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
  }
  .nav-links a:hover {
    color: #0066cc;
  }

  /* Mobile: stack vertically */
  @media (max-width: 600px) {
    .main-nav {
      flex-direction: column;
      align-items: flex-start;
      gap: 1em;
    }
    .nav-links {
      flex-direction: column;
      gap: 0.5em;
      width: 100%;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Layout breakdown:</strong></p>
<ul>
  <li><code>display: flex</code> on the nav lays out logo + nav-links horizontally.</li>
  <li><code>justify-content: space-between</code> pushes them to opposite ends.</li>
  <li><code>display: flex</code> on the nav-links list lays out the items horizontally with spacing.</li>
  <li>Media query collapses to vertical on mobile.</li>
</ul>
<p>For a hamburger-style mobile menu, add a checkbox or button to toggle visibility &mdash; or use a JavaScript-based toggle for full ARIA accessibility.</p>
'''

ANSWERS[84] = r'''
<p>The <code>aspect-ratio</code> property (well-supported in 2026) preserves a width-to-height proportion as the element resizes:</p>
<pre><code>.video-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9;        /* width:height, like 16:9 video */
  background: #000;
  object-fit: cover;
}

.square {
  width: 200px;
  aspect-ratio: 1;             /* shorthand for 1:1 (square) */
}

.golden {
  aspect-ratio: 1.618 / 1;     /* golden ratio */
}</code></pre>
<p><strong>How it works:</strong></p>
<ul>
  <li>Set width or height; the other dimension is computed from the ratio.</li>
  <li>Set neither; the element computes both based on content + ratio.</li>
  <li>Set both; the explicit values win.</li>
</ul>
<p><strong>Pre-aspect-ratio hack</strong> &mdash; the padding-bottom trick:</p>
<pre><code>.aspect-16-9 {
  position: relative;
  padding-bottom: 56.25%;       /* 9/16 = 56.25% */
  height: 0;
}
.aspect-16-9 iframe {
  position: absolute;
  width: 100%;
  height: 100%;
}</code></pre>
<p>This was the standard technique for 20 years &mdash; uses the fact that percentage padding is relative to width. Modern <code>aspect-ratio</code> replaces it cleanly.</p>
<p><strong>Common uses:</strong></p>
<table>
  <tr><th>Element</th><th>Ratio</th></tr>
  <tr><td>Video</td><td><code>16 / 9</code></td></tr>
  <tr><td>Square photo</td><td><code>1</code></td></tr>
  <tr><td>Photo (4:3)</td><td><code>4 / 3</code></td></tr>
  <tr><td>Banner</td><td><code>21 / 9</code> (ultrawide)</td></tr>
  <tr><td>Card thumbnail</td><td><code>3 / 2</code></td></tr>
</table>
<p>Pair with <code>object-fit: cover</code> on contained images to fill the box without distortion.</p>
'''

ANSWERS[85] = r'''
<p>CSS Grid is ideal for card layouts &mdash; cards reflow to fit any screen size:</p>
<pre><code>&lt;section class="card-grid"&gt;
  &lt;article class="card"&gt;
    &lt;img src="1.jpg" alt=""&gt;
    &lt;h3&gt;Card 1&lt;/h3&gt;
    &lt;p&gt;Description here.&lt;/p&gt;
  &lt;/article&gt;
  &lt;article class="card"&gt;...&lt;/article&gt;
  &lt;article class="card"&gt;...&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
  }
  .card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
  }
  .card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
  }
  .card h3 {
    padding: 1em 1em 0.5em;
    margin: 0;
  }
  .card p {
    padding: 0 1em 1em;
    margin: 0;
    flex: 1;          /* push content; cards align bottoms */
  }
&lt;/style&gt;</code></pre>
<p><strong>Key Grid magic:</strong></p>
<ul>
  <li><code>repeat(auto-fit, minmax(280px, 1fr))</code> &mdash; cards reflow automatically. Wide screens: 4+ columns; phones: 1 column.</li>
  <li><code>gap: 1.5rem</code> &mdash; consistent spacing between cards.</li>
  <li><code>display: flex</code> on the card &mdash; lets us align internal elements vertically.</li>
  <li><code>flex: 1</code> on the description &mdash; ensures all cards in a row have equal heights.</li>
</ul>
<p><strong>Equal-height rows</strong> are a common Grid bonus: cards in the same row automatically stretch to the tallest card&rsquo;s height.</p>
'''

ANSWERS[86] = r'''
<p>Use <strong>attribute selectors</strong> with the <code>=</code> operator to match exact values:</p>
<pre><code>/* Inputs that are required */
input[required] { border-color: red; }

/* Links opening in new tab */
a[target="_blank"]::after {
  content: " &#8599;";
}

/* External links (start with http) */
a[href^="http"] { color: blue; }

/* PDF download links (end with .pdf) */
a[href$=".pdf"]::before { content: "&#128196; "; }

/* Links containing "github" */
a[href*="github.com"] { background: #f6f8fa; }</code></pre>
<p><strong>Attribute selector operators:</strong></p>
<table>
  <tr><th>Selector</th><th>Matches when value</th></tr>
  <tr><td><code>[attr]</code></td><td>Has the attribute</td></tr>
  <tr><td><code>[attr=value]</code></td><td>Equals exactly</td></tr>
  <tr><td><code>[attr^=value]</code></td><td>Starts with</td></tr>
  <tr><td><code>[attr$=value]</code></td><td>Ends with</td></tr>
  <tr><td><code>[attr*=value]</code></td><td>Contains substring</td></tr>
  <tr><td><code>[attr~=value]</code></td><td>Word match (whitespace-separated)</td></tr>
  <tr><td><code>[attr|=value]</code></td><td>Hyphen prefix (e.g., language codes)</td></tr>
</table>
<p><strong>Real-world examples:</strong></p>
<pre><code>/* Style all input types except text */
input:not([type="text"]) { ... }

/* Different styles per input type */
input[type="email"] { background-image: url(email-icon.svg); }
input[type="password"] { letter-spacing: 0.2em; }

/* Data attributes for state */
[data-state="loading"] { opacity: 0.5; cursor: wait; }
[data-state="error"]   { border-color: red; }

/* Language-specific styles */
:lang(en) { font-family: Georgia; }
:lang(zh) { font-family: "PingFang SC"; }</code></pre>
<p>Attribute selectors are essential for styling form inputs and integrating with JS-driven UIs that toggle <code>data-*</code> attributes for state.</p>
'''

ANSWERS[87] = r'''
<p>A responsive footer adapts from multi-column on desktop to stacked on mobile:</p>
<pre><code>&lt;footer class="site-footer"&gt;
  &lt;div class="footer-cols"&gt;
    &lt;section&gt;
      &lt;h4&gt;Company&lt;/h4&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/team"&gt;Team&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/careers"&gt;Careers&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/section&gt;
    &lt;section&gt;
      &lt;h4&gt;Products&lt;/h4&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/features"&gt;Features&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/section&gt;
    &lt;section&gt;
      &lt;h4&gt;Connect&lt;/h4&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/blog"&gt;Blog&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/section&gt;
  &lt;/div&gt;
  &lt;p class="copyright"&gt;&amp;copy; 2026 Acme Corp&lt;/p&gt;
&lt;/footer&gt;

&lt;style&gt;
  .site-footer {
    background: #2c3e50;
    color: white;
    padding: 3em 1.5em 1.5em;
  }
  .footer-cols {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2em;
    max-width: 1200px;
    margin: 0 auto;
  }
  .footer-cols h4 {
    margin-top: 0;
  }
  .footer-cols ul {
    list-style: none;
    padding: 0;
  }
  .footer-cols a {
    color: #ddd;
    text-decoration: none;
    line-height: 2;
  }
  .footer-cols a:hover {
    color: white;
  }
  .copyright {
    text-align: center;
    margin-top: 2em;
    font-size: 0.9em;
    color: #aaa;
  }
&lt;/style&gt;</code></pre>
<p>Grid&rsquo;s <code>auto-fit + minmax</code> handles responsiveness without explicit breakpoints: 4+ columns on wide screens, fewer columns as space tightens, single column on phones.</p>
'''

ANSWERS[88] = r'''
<p>Use the <code>min-height</code> property to set a floor &mdash; the element can grow taller, but never shorter:</p>
<pre><code>.hero {
  min-height: 400px;        /* at least 400px tall */
  padding: 2em;
}

.full-screen {
  min-height: 100vh;        /* full viewport height minimum */
}

.card {
  min-height: 200px;        /* uniform card heights at minimum */
}</code></pre>
<p><strong>Comparison with <code>height</code>:</strong></p>
<table>
  <tr><th></th><th><code>height</code></th><th><code>min-height</code></th></tr>
  <tr><td>Behavior</td><td>Locks to exact value</td><td>Sets a floor; can grow</td></tr>
  <tr><td>Content overflow</td><td>Clipped or scrolls</td><td>Element grows to fit</td></tr>
  <tr><td>Use when</td><td>Exact size required</td><td>Minimum required, content variable</td></tr>
</table>
<p><strong>Common pattern: full-height pages</strong>:</p>
<pre><code>html, body { height: 100%; }     /* enable percentage children */

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main {
  flex: 1;                       /* grows to fill */
}
.footer {
  /* sticks to bottom */
}</code></pre>
<p>This "sticky footer" pattern keeps the footer at the bottom even when content is short, while letting the page grow longer if content is tall.</p>
<p><strong>Modern alternative</strong>:</p>
<pre><code>.full-page {
  min-height: 100dvh;       /* dynamic viewport height — accounts for mobile chrome */
}</code></pre>
<p><code>dvh</code> (dynamic viewport height) accounts for browser UI showing/hiding on mobile &mdash; smoother than <code>vh</code> on iOS Safari.</p>
'''

ANSWERS[89] = r'''
<p>Use the native <code>&lt;progress&gt;</code> element &mdash; or build a custom one with two divs:</p>
<p><strong>Native (preferred):</strong></p>
<pre><code>&lt;progress value="65" max="100"&gt;65%&lt;/progress&gt;

&lt;style&gt;
  progress {
    width: 100%;
    height: 8px;
    accent-color: #0066cc;     /* modern way to color it */
  }
&lt;/style&gt;</code></pre>
<p><strong>Custom progress bar</strong> &mdash; for more styling control:</p>
<pre><code>&lt;div class="progress"
     role="progressbar"
     aria-valuenow="65"
     aria-valuemin="0"
     aria-valuemax="100"&gt;
  &lt;div class="progress-bar" style="width: 65%;"&gt;&lt;/div&gt;
&lt;/div&gt;

&lt;style&gt;
  .progress {
    width: 100%;
    height: 12px;
    background: #f0f0f0;
    border-radius: 6px;
    overflow: hidden;
  }
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #0066cc, #00ccff);
    transition: width 0.3s ease;
  }
&lt;/style&gt;</code></pre>
<p><strong>Animated stripes</strong> &mdash; classic loading look:</p>
<pre><code>.progress-bar.striped {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%
  );
  background-size: 1em 1em;
  animation: stripes 1s linear infinite;
}
@keyframes stripes {
  from { background-position: 0 0; }
  to   { background-position: 1em 0; }
}</code></pre>
<p><strong>Update from JavaScript</strong>:</p>
<pre><code>const bar = document.querySelector(".progress-bar");
bar.style.width = "75%";
bar.parentElement.setAttribute("aria-valuenow", "75");</code></pre>
<p>Always update both visual width and ARIA attributes &mdash; screen readers depend on them.</p>
'''

ANSWERS[90] = r'''
<p>Use the <code>font-family</code> property with a comma-separated list of fonts:</p>
<pre><code>body {
  font-family: "Inter", -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
}

h1, h2, h3 {
  font-family: Georgia, "Times New Roman", serif;
}

code {
  font-family: "JetBrains Mono", Consolas, Monaco, monospace;
}</code></pre>
<p><strong>Why a stack?</strong> The browser tries each font in order; if one isn&rsquo;t available, it tries the next. The list ends with a generic family (<code>sans-serif</code>, <code>serif</code>, <code>monospace</code>) as the final fallback.</p>
<p><strong>Quote font names with spaces:</strong></p>
<pre><code>font-family: "Helvetica Neue", "Times New Roman", sans-serif;
/* "Helvetica Neue" must be quoted */</code></pre>
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
<pre><code>&lt;head&gt;
  &lt;link rel="preconnect" href="https://fonts.googleapis.com"&gt;
  &lt;link rel="preconnect" href="https://fonts.gstatic.com" crossorigin&gt;
  &lt;link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;display=swap"
        rel="stylesheet"&gt;
&lt;/head&gt;

&lt;style&gt;
  body { font-family: "Inter", sans-serif; }
&lt;/style&gt;</code></pre>
<p><strong>System font stack</strong> &mdash; uses the OS&rsquo;s native UI font, with no download:</p>
<pre><code>font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;</code></pre>
<p>Fast, native, no font-loading penalty &mdash; preferred for app-like UIs.</p>
'''

ANSWERS[91] = r'''
<p>Use <code>position: sticky</code> with <code>top: 0</code> &mdash; the header scrolls naturally with the page until it reaches the top, then sticks:</p>
<pre><code>&lt;header class="sticky-header"&gt;
  &lt;a href="/"&gt;Logo&lt;/a&gt;
  &lt;nav&gt;
    &lt;a href="/"&gt;Home&lt;/a&gt;
    &lt;a href="/about"&gt;About&lt;/a&gt;
    &lt;a href="/contact"&gt;Contact&lt;/a&gt;
  &lt;/nav&gt;
&lt;/header&gt;

&lt;main&gt;
  &lt;article&gt;Lots of content...&lt;/article&gt;
&lt;/main&gt;

&lt;style&gt;
  .sticky-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: white;
    padding: 1em;
    border-bottom: 1px solid #eee;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
&lt;/style&gt;</code></pre>
<p><strong>Sticky vs Fixed:</strong></p>
<table>
  <tr><th></th><th><code>position: sticky</code></th><th><code>position: fixed</code></th></tr>
  <tr><td>Layout</td><td>Takes natural space, then sticks</td><td>Removed from flow always</td></tr>
  <tr><td>Need to offset content?</td><td>No</td><td>Yes (padding-top equal to header height)</td></tr>
  <tr><td>Visible at page top?</td><td>Yes (in flow)</td><td>Yes (always)</td></tr>
  <tr><td>Scrolls with hero?</td><td>Yes, until threshold</td><td>No, stays put</td></tr>
</table>
<p><strong>Common gotcha:</strong> <code>position: sticky</code> doesn&rsquo;t stick if any parent has <code>overflow: hidden</code> or <code>overflow: auto</code> &mdash; the parent becomes the scroll context. If sticky isn&rsquo;t working, check parent overflow settings.</p>
<p><strong>Add scroll-margin for anchor links:</strong></p>
<pre><code>section[id] {
  scroll-margin-top: 70px;     /* approximately header height */
}</code></pre>
<p>Without this, anchor links scroll the target right under the sticky header. <code>scroll-margin-top</code> creates breathing room.</p>
'''

ANSWERS[92] = r'''
<p>Two main approaches: <strong>horizontal scrolling</strong> for data preservation, or <strong>row stacking</strong> for mobile-friendly reading.</p>
<p><strong>Horizontal scroll on mobile</strong> &mdash; preserves the table structure:</p>
<pre><code>&lt;div class="table-wrapper"&gt;
  &lt;table&gt;
    &lt;thead&gt;
      &lt;tr&gt;
        &lt;th&gt;Name&lt;/th&gt;
        &lt;th&gt;Email&lt;/th&gt;
        &lt;th&gt;Role&lt;/th&gt;
        &lt;th&gt;Date&lt;/th&gt;
      &lt;/tr&gt;
    &lt;/thead&gt;
    &lt;tbody&gt;
      &lt;tr&gt;&lt;td&gt;Alice&lt;/td&gt;&lt;td&gt;alice@x.com&lt;/td&gt;&lt;td&gt;Admin&lt;/td&gt;&lt;td&gt;2026-01-15&lt;/td&gt;&lt;/tr&gt;
    &lt;/tbody&gt;
  &lt;/table&gt;
&lt;/div&gt;

&lt;style&gt;
  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  table {
    width: 100%;
    min-width: 500px;        /* forces scroll on narrow screens */
    border-collapse: collapse;
  }
  th, td {
    padding: 0.75em 1em;
    border-bottom: 1px solid #eee;
    text-align: left;
  }
&lt;/style&gt;</code></pre>
<p><strong>Stacked rows on mobile</strong> &mdash; each row becomes a vertical card:</p>
<pre><code>@media (max-width: 600px) {
  table, thead, tbody, tr, th, td {
    display: block;
  }
  thead { display: none; }      /* hide header */
  tr {
    border: 1px solid #ddd;
    margin-bottom: 1em;
    padding: 1em;
  }
  td {
    border: none;
    padding: 0.25em 0;
  }
  td::before {
    content: attr(data-label) ": ";
    font-weight: bold;
  }
}</code></pre>
<pre><code>&lt;td data-label="Email"&gt;alice@x.com&lt;/td&gt;</code></pre>
<p>The <code>data-label</code> attribute provides the column name for stacked view; CSS reads it via <code>attr()</code>. This works well for tables with 5-10 columns; more columns become unwieldy.</p>
'''

ANSWERS[93] = r'''
<p>Use the <code>::first-letter</code> pseudo-element to style the first letter of a paragraph or block element &mdash; perfect for "drop cap" magazine-style typography:</p>
<pre><code>p::first-letter {
  font-size: 3em;
  font-weight: bold;
  float: left;
  line-height: 1;
  margin-right: 0.1em;
  color: #ff6b35;
}</code></pre>
<pre><code>&lt;p&gt;In the beginning, there was just plain text...&lt;/p&gt;
&lt;!-- The "I" appears huge, orange, with text wrapping around it --&gt;</code></pre>
<p><strong>Pseudo-elements use double colon</strong> (<code>::</code>) to distinguish them from pseudo-classes (single colon, like <code>:hover</code>). Both work in modern browsers, but <code>::</code> is the standard.</p>
<p><strong>Common pseudo-elements:</strong></p>
<table>
  <tr><th>Pseudo-element</th><th>Targets</th></tr>
  <tr><td><code>::first-letter</code></td><td>First letter of block content</td></tr>
  <tr><td><code>::first-line</code></td><td>First line of block content</td></tr>
  <tr><td><code>::before</code> / <code>::after</code></td><td>Generated content before/after</td></tr>
  <tr><td><code>::placeholder</code></td><td>Form input placeholder text</td></tr>
  <tr><td><code>::selection</code></td><td>User-selected text</td></tr>
  <tr><td><code>::marker</code></td><td>List item bullets/numbers</td></tr>
</table>
<p><strong>Restrictions on <code>::first-letter</code>:</strong></p>
<ul>
  <li>Only the literal first letter (and any leading punctuation/quotation marks).</li>
  <li>Limited properties accepted: font, color, background, padding, margin, border, text-decoration, line-height, float.</li>
  <li>Doesn&rsquo;t apply to inline elements &mdash; the parent must be block-level.</li>
</ul>
<p><strong>Real-world drop cap with side-by-side layout:</strong></p>
<pre><code>article p:first-of-type::first-letter {
  font-family: Georgia, serif;
  font-size: 4em;
  font-weight: bold;
  float: left;
  margin: 0.1em 0.1em 0 0;
  line-height: 0.85;
  color: #c00;
}</code></pre>
<p>Combine with <code>:first-of-type</code> so only the article&rsquo;s first paragraph gets a drop cap.</p>
'''

ANSWERS[94] = r'''
<p>CSS Grid handles a sidebar + main content layout perfectly &mdash; collapsing to single column on mobile:</p>
<pre><code>&lt;div class="layout"&gt;
  &lt;aside&gt;
    &lt;nav&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/dashboard"&gt;Dashboard&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/projects"&gt;Projects&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/settings"&gt;Settings&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/aside&gt;

  &lt;main&gt;
    &lt;h1&gt;Welcome&lt;/h1&gt;
    &lt;p&gt;Main content area...&lt;/p&gt;
  &lt;/main&gt;
&lt;/div&gt;

&lt;style&gt;
  .layout {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 2em;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1em;
  }
  aside {
    background: #f8f9fa;
    padding: 1em;
    border-radius: 8px;
    position: sticky;
    top: 1em;
    align-self: start;     /* don't stretch to main height */
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
  aside a:hover { background: #e9ecef; }

  /* Mobile: stack vertically */
  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
    }
    aside {
      position: static;
    }
  }
&lt;/style&gt;</code></pre>
<p><strong>Key techniques:</strong></p>
<ul>
  <li><code>grid-template-columns: 250px 1fr</code> &mdash; sidebar fixed at 250px, main fills remaining space.</li>
  <li><code>position: sticky</code> on the aside &mdash; sidebar stays visible while main content scrolls.</li>
  <li><code>align-self: start</code> &mdash; prevents the sidebar from stretching to match the main content height.</li>
  <li>Media query collapses to single column on mobile.</li>
</ul>
<p>For a right sidebar instead, use <code>grid-template-columns: 1fr 250px</code>. For two sidebars, <code>200px 1fr 200px</code>.</p>
'''

ANSWERS[95] = r'''
<p>Use a gradient as the <code>border-image</code> source, or layer with backgrounds for a clean gradient border effect:</p>
<p><strong>Method 1: <code>border-image</code></strong></p>
<pre><code>.gradient-border {
  border: 4px solid;
  border-image: linear-gradient(45deg, #0066cc, #ff6b35) 1;
  padding: 1em;
}</code></pre>
<p>The trailing <code>1</code> sets the slice value &mdash; without it, the gradient won&rsquo;t apply to all sides correctly.</p>
<p><strong>Method 2: padding hack with backgrounds</strong></p>
<pre><code>.gradient-border-2 {
  position: relative;
  padding: 1em;
  background: white;
  background-clip: padding-box;
  border: 4px solid transparent;
  border-radius: 8px;
}
.gradient-border-2::before {
  content: "";
  position: absolute;
  inset: -4px;
  z-index: -1;
  background: linear-gradient(45deg, #0066cc, #ff6b35);
  border-radius: inherit;
}</code></pre>
<p><strong>Method 3 (modern): <code>background</code> with mask</strong> &mdash; works with rounded corners:</p>
<pre><code>.gradient-border-3 {
  padding: 1em;
  border-radius: 8px;
  background:
    linear-gradient(white, white) padding-box,
    linear-gradient(45deg, #0066cc, #ff6b35) border-box;
  border: 4px solid transparent;
}</code></pre>
<p>The double-background trick layers a solid white inside (padding-box) and a gradient outside (border-box). Where the transparent border sits, the gradient shows through.</p>
<p><strong>Animated gradient border:</strong></p>
<pre><code>.gradient-border-3 {
  background-size: 200% 200%;
  animation: shift 3s linear infinite;
}
@keyframes shift {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}</code></pre>
<p>Method 3 is the most flexible &mdash; supports rounded corners and animation cleanly.</p>
'''

ANSWERS[96] = r'''
<p>The <strong>visually-hidden CSS pattern</strong> hides content visually but keeps it accessible to screen readers. It&rsquo;s essential for skip links, descriptive labels, and supplementary text that&rsquo;s redundant for sighted users.</p>
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
<pre><code>&lt;!-- Skip link for keyboard users --&gt;
&lt;a href="#main" class="sr-only sr-only-focusable"&gt;Skip to content&lt;/a&gt;

&lt;!-- Icon button with hidden text label --&gt;
&lt;button&gt;
  &lt;svg&gt;...&lt;/svg&gt;
  &lt;span class="sr-only"&gt;Close dialog&lt;/span&gt;
&lt;/button&gt;

&lt;!-- Form field with hidden label --&gt;
&lt;label for="search" class="sr-only"&gt;Search the site&lt;/label&gt;
&lt;input id="search" type="search" placeholder="Search"&gt;</code></pre>
<p><strong>What NOT to use:</strong></p>
<table>
  <tr><th>Method</th><th>Problem</th></tr>
  <tr><td><code>display: none</code></td><td>Removes from screen readers too</td></tr>
  <tr><td><code>visibility: hidden</code></td><td>Removes from screen readers too</td></tr>
  <tr><td><code>opacity: 0</code></td><td>Visually invisible but takes layout space</td></tr>
  <tr><td><code>height: 0</code> alone</td><td>Some screen readers ignore</td></tr>
</table>
<p><strong>Show on focus</strong> &mdash; for skip links, the link should appear when keyboard-focused:</p>
<pre><code>.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: 0.5em 1em;
  margin: 0;
  clip: auto;
  background: yellow;
  color: black;
  z-index: 100;
}</code></pre>
<p>This pattern reveals the skip link when keyboard-focused but hides it from sighted users by default. Most accessible site templates include this CSS.</p>
'''

ANSWERS[97] = r'''
<p>A hero section is a large eye-catching banner at the top of a page. Modern responsive heroes use Flexbox or Grid for centering, with a background image and overlay for legibility:</p>
<pre><code>&lt;section class="hero"&gt;
  &lt;div class="hero-content"&gt;
    &lt;h1&gt;Build Something Great&lt;/h1&gt;
    &lt;p&gt;Powerful tools for modern teams.&lt;/p&gt;
    &lt;a href="/signup" class="btn-primary"&gt;Get Started&lt;/a&gt;
  &lt;/div&gt;
&lt;/section&gt;

&lt;style&gt;
  .hero {
    /* Stacked backgrounds: dark overlay + image */
    background:
      linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
      url("/hero.jpg") center / cover no-repeat;

    min-height: 60vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
    padding: 2em;
  }
  .hero-content {
    max-width: 700px;
  }
  .hero h1 {
    font-size: clamp(2em, 5vw, 4em);   /* fluid: 2em min, 4em max */
    margin: 0 0 0.5em;
  }
  .hero p {
    font-size: 1.2em;
    margin-bottom: 2em;
    opacity: 0.95;
  }
  .btn-primary {
    display: inline-block;
    background: #ff6b35;
    color: white;
    padding: 0.9em 2em;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 600;
  }
&lt;/style&gt;</code></pre>
<p><strong>Responsive techniques used:</strong></p>
<ul>
  <li><code>min-height: 60vh</code> &mdash; sized relative to viewport, scales naturally.</li>
  <li><code>clamp()</code> for the heading &mdash; size scales between 2em and 4em based on viewport width.</li>
  <li>Flexbox centering works for any content size or count.</li>
  <li>Stacked backgrounds (gradient over image) ensure text legibility on any photo.</li>
</ul>
<p><strong>Performance:</strong> use <code>fetchpriority="high"</code> + <code>&lt;link rel="preload"&gt;</code> on the hero image so it loads before LCP measurement.</p>
'''

ANSWERS[98] = r'''
<p>Use the <code>line-height</code> property &mdash; it controls the vertical spacing between lines of text. The most common value is a unitless number (a multiplier of font size).</p>
<pre><code>p { line-height: 1.5; }     /* 1.5 &times; font-size */

h1 { line-height: 1.2; }    /* tighter for headings */

.spacious { line-height: 2; }   /* generous spacing */</code></pre>
<p><strong>Best practice: use unitless values</strong> &mdash; they inherit correctly:</p>
<pre><code>body { line-height: 1.5; }    /* applies a multiplier */

h1 { font-size: 32px; }        /* line-height becomes 48px */
p  { font-size: 16px; }        /* line-height becomes 24px */</code></pre>
<p>If you used <code>line-height: 24px</code> on body, all elements would inherit the literal 24px regardless of their font size &mdash; usually not what you want.</p>
<p><strong>Recommended values</strong>:</p>
<table>
  <tr><th>Content type</th><th>Suggested line-height</th></tr>
  <tr><td>Display headings (large)</td><td>1.0&ndash;1.2</td></tr>
  <tr><td>Body text</td><td>1.4&ndash;1.6</td></tr>
  <tr><td>Long-form articles</td><td>1.6&ndash;1.8</td></tr>
  <tr><td>Captions / fine print</td><td>1.3&ndash;1.4</td></tr>
</table>
<p><strong>Accessibility:</strong> WCAG recommends <strong>line-height of at least 1.5</strong> for body text to help users with cognitive disabilities and dyslexia. Tighter line-heights make text harder to scan.</p>
<p><strong>Vertical rhythm</strong> &mdash; advanced typography sets all line-heights to multiples of a base value (e.g., 24px), creating a consistent baseline grid throughout the page. Modern frameworks like Tailwind use this approach with their spacing scale.</p>
'''

ANSWERS[99] = r'''
<p>Use <code>position: fixed</code> &mdash; the element stays anchored to the viewport regardless of scrolling:</p>
<pre><code>.scroll-to-top {
  position: fixed;
  bottom: 2em;
  right: 2em;
  z-index: 100;

  background: #0066cc;
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}</code></pre>
<p>Common uses for <code>position: fixed</code>:</p>
<ul>
  <li>Fixed headers (always visible at top).</li>
  <li>Floating action buttons (FAB).</li>
  <li>Modal dialogs (covering the entire viewport).</li>
  <li>"Back to top" buttons.</li>
  <li>Sticky chat widgets.</li>
  <li>Toast notifications.</li>
</ul>
<p><strong>Critical:</strong> fixed elements are removed from the document flow. They don&rsquo;t take up space, so you may need to add padding to other elements to prevent overlap:</p>
<pre><code>.fixed-header {
  position: fixed;
  top: 0;
  height: 60px;
}
main {
  padding-top: 60px;       /* prevent content from hiding under header */
}</code></pre>
<p><strong>Show only when scrolled:</strong></p>
<pre><code>.scroll-to-top {
  opacity: 0;
  transition: opacity 0.3s;
}
.scroll-to-top.visible {
  opacity: 1;
}

&lt;script&gt;
  window.addEventListener("scroll", () =&gt; {
    document.querySelector(".scroll-to-top")
      .classList.toggle("visible", window.scrollY &gt; 300);
  });
&lt;/script&gt;</code></pre>
<p>Show the button only after the user has scrolled past 300px &mdash; common pattern for "scroll to top" controls.</p>
'''

ANSWERS[100] = r'''
<p>Make a button span the full width of its container with <code>width: 100%</code> and <code>display: block</code> if needed:</p>
<pre><code>.btn-full {
  display: block;          /* span full width if needed */
  width: 100%;
  padding: 0.9em 1em;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  text-align: center;
}</code></pre>
<p><strong>Inside flex/grid containers</strong>, the button stretches naturally:</p>
<pre><code>.form {
  display: flex;
  flex-direction: column;
  gap: 1em;
}
.form button {
  width: 100%;             /* fills flex container */
}</code></pre>
<p><strong>For text links styled as buttons</strong>:</p>
<pre><code>.btn-link {
  display: block;
  width: 100%;
  padding: 0.9em 1em;
  text-align: center;
  text-decoration: none;
  background: #0066cc;
  color: white;
  border-radius: 4px;
  box-sizing: border-box;
}</code></pre>
<p><strong>Best practice: use <code>box-sizing: border-box</code></strong> &mdash; without it, padding adds to the 100% width and the button overflows its container.</p>
<p><strong>Mobile pattern</strong> &mdash; full-width on mobile, normal on desktop:</p>
<pre><code>.btn {
  padding: 0.9em 2em;
  background: #0066cc;
}

@media (max-width: 600px) {
  .btn {
    width: 100%;
    display: block;
  }
}</code></pre>
<p>Full-width buttons on mobile improve tap accuracy &mdash; the larger target is easier to hit. Reserve them for primary actions; secondary actions should be visually less prominent.</p>
'''

ANSWERS[101] = r'''
<p>Flexbox handles multi-column layouts that respond to viewport size with <code>flex-wrap</code>:</p>
<pre><code>&lt;section class="features"&gt;
  &lt;article&gt;
    &lt;h3&gt;Fast&lt;/h3&gt;
    &lt;p&gt;Loads in milliseconds.&lt;/p&gt;
  &lt;/article&gt;
  &lt;article&gt;
    &lt;h3&gt;Simple&lt;/h3&gt;
    &lt;p&gt;Zero configuration.&lt;/p&gt;
  &lt;/article&gt;
  &lt;article&gt;
    &lt;h3&gt;Secure&lt;/h3&gt;
    &lt;p&gt;Encrypted by default.&lt;/p&gt;
  &lt;/article&gt;
  &lt;article&gt;
    &lt;h3&gt;Open&lt;/h3&gt;
    &lt;p&gt;MIT-licensed.&lt;/p&gt;
  &lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .features {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    padding: 1.5rem;
  }
  .features article {
    flex: 1 1 250px;        /* grow, shrink, basis */
    padding: 1.5em;
    background: white;
    border: 1px solid #eee;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>
<p><strong>The <code>flex: 1 1 250px</code> shorthand:</strong></p>
<table>
  <tr><th>Value</th><th>Meaning</th></tr>
  <tr><td><code>flex-grow: 1</code></td><td>Fill extra space equally with siblings</td></tr>
  <tr><td><code>flex-shrink: 1</code></td><td>Shrink if needed</td></tr>
  <tr><td><code>flex-basis: 250px</code></td><td>Preferred starting width</td></tr>
</table>
<p>Result: items start at 250px wide; if there&rsquo;s extra space, they grow equally. If there&rsquo;s no room, they wrap to a new line.</p>
<p><strong>How it adapts:</strong></p>
<ul>
  <li>Wide screen: 4 columns side-by-side.</li>
  <li>Tablet: 2-3 columns wrap onto two rows.</li>
  <li>Phone: 1 column stacked.</li>
</ul>
<p><strong>Comparison with Grid:</strong> Flexbox preserves item order and gives natural wrapping. Grid (<code>auto-fit + minmax</code>) provides stronger alignment and fixed-row behavior. Both work for this pattern; pick the syntax you find clearer.</p>
'''

ANSWERS[102] = r'''
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
    flex: 0 0 100%;          /* each takes full width */
    scroll-snap-align: start;
    object-fit: cover;
    height: 400px;
  }

  /* Optional: hide scrollbar */
  .slider::-webkit-scrollbar { display: none; }
  .slider { scrollbar-width: none; }
&lt;/style&gt;</code></pre>
<p><strong>How <code>scroll-snap</code> works:</strong></p>
<ul>
  <li><code>scroll-snap-type: x mandatory</code> &mdash; the container will snap to children on the x-axis when scrolled.</li>
  <li><code>scroll-snap-align: start</code> on each item &mdash; tells the browser to snap to the start of each item.</li>
  <li>User swipes; browser smoothly snaps to the next image.</li>
</ul>
<p><strong>Add nav buttons</strong> for prev/next (basic JS):</p>
<pre><code>&lt;button onclick="scrollSlider(-1)"&gt;&lt;&lt;/button&gt;
&lt;button onclick="scrollSlider(1)"&gt;&gt;&lt;/button&gt;

&lt;script&gt;
  function scrollSlider(direction) {
    const slider = document.querySelector(".slider");
    slider.scrollBy({
      left: slider.clientWidth * direction,
      behavior: "smooth",
    });
  }
&lt;/script&gt;</code></pre>
<p><strong>Add pagination dots</strong> &mdash; one per slide, clickable to jump.</p>
<p><strong>For a true production carousel</strong> with autoplay, lazy loading, and rich accessibility (keyboard navigation, ARIA live regions, reduced-motion support), use a library like Swiper.js or Embla Carousel. The pure-CSS version handles ~80% of slider needs with zero JavaScript.</p>
'''
