"""Detailed answers for HTML Advanced questions."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p>HTML5 (officially a living standard since 2014) introduced a substantial set of features that turned HTML from a markup language into a platform for rich applications. Most of the &ldquo;HTML5 features&rdquo; people cite are now baseline web platform features in 2026.</p>
<p><strong>New semantic elements:</strong></p>
<ul>
  <li><code>&lt;header&gt;</code>, <code>&lt;footer&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;article&gt;</code>, <code>&lt;section&gt;</code>, <code>&lt;aside&gt;</code>, <code>&lt;nav&gt;</code> &mdash; replace generic <code>&lt;div&gt;</code> for landmark regions; screen readers expose them as navigation points.</li>
  <li><code>&lt;figure&gt;</code> + <code>&lt;figcaption&gt;</code> &mdash; bind images to their captions semantically.</li>
  <li><code>&lt;mark&gt;</code>, <code>&lt;time&gt;</code>, <code>&lt;output&gt;</code>, <code>&lt;progress&gt;</code>, <code>&lt;meter&gt;</code>, <code>&lt;details&gt;</code>, <code>&lt;summary&gt;</code>, <code>&lt;dialog&gt;</code>.</li>
</ul>
<p><strong>New form capabilities:</strong> input types (<code>email</code>, <code>url</code>, <code>tel</code>, <code>date</code>, <code>time</code>, <code>color</code>, <code>range</code>, <code>number</code>, <code>search</code>); attributes for built-in validation (<code>required</code>, <code>pattern</code>, <code>min</code>, <code>max</code>, <code>step</code>, <code>autocomplete</code>); the <code>&lt;datalist&gt;</code> autocomplete element. These eliminated tons of JavaScript validation libraries that dominated the 2000s.</p>
<p><strong>Native multimedia and graphics:</strong></p>
<ul>
  <li><code>&lt;audio&gt;</code> and <code>&lt;video&gt;</code> &mdash; replaced Flash plugins with first-class elements.</li>
  <li><code>&lt;canvas&gt;</code> &mdash; pixel-level 2D drawing API.</li>
  <li>Inline SVG &mdash; vector graphics that scale, animate, and interact like DOM elements.</li>
</ul>
<p><strong>JavaScript APIs introduced alongside HTML5:</strong> <code>localStorage</code>/<code>sessionStorage</code>, IndexedDB, Geolocation, Web Workers, WebSockets, Server-Sent Events, History API (<code>pushState</code>), Drag &amp; Drop, File API, application cache (now superseded by Service Workers), Web Audio, WebRTC, Notifications. Together these enabled true single-page applications.</p>
<p><strong>Document structure improvements:</strong> simpler <code>&lt;!DOCTYPE html&gt;</code> declaration, the <code>&lt;meta charset="UTF-8"&gt;</code> shorthand, the viewport meta tag for responsive design (<code>&lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;</code>), microdata via <code>itemprop</code>/<code>itemscope</code>, and ARIA attribute integration.</p>
<p><strong>What HTML5 didn&rsquo;t do</strong> is finalize a single feature set &mdash; it&rsquo;s a living standard that evolves continuously. Recent additions (2024-2026) include <code>&lt;dialog&gt;</code>, the popover API, <code>:has()</code> CSS selector, container queries, view transitions, and speculation rules. The spec at <code>html.spec.whatwg.org</code> is the source of truth.</p>
'''

ANSWERS[2] = r'''
<p>Semantic HTML uses elements that <strong>describe the meaning of their content</strong>, not just its appearance. <code>&lt;article&gt;</code> says &ldquo;this is a self-contained piece of content&rdquo;; <code>&lt;div&gt;</code> says nothing. The browser renders both as plain blocks &mdash; but semantic tags carry information that browsers, assistive tech, search engines, and other developers can use.</p>
<p><strong>Categories of semantic elements:</strong></p>
<table>
  <tr><th>Category</th><th>Examples</th></tr>
  <tr><td>Landmarks</td><td><code>&lt;header&gt;</code>, <code>&lt;nav&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;aside&gt;</code>, <code>&lt;footer&gt;</code></td></tr>
  <tr><td>Content sectioning</td><td><code>&lt;article&gt;</code>, <code>&lt;section&gt;</code>, <code>&lt;hgroup&gt;</code></td></tr>
  <tr><td>Text-level meaning</td><td><code>&lt;em&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;cite&gt;</code>, <code>&lt;code&gt;</code>, <code>&lt;kbd&gt;</code>, <code>&lt;mark&gt;</code>, <code>&lt;time&gt;</code></td></tr>
  <tr><td>Lists</td><td><code>&lt;ol&gt;</code>, <code>&lt;ul&gt;</code>, <code>&lt;dl&gt;</code> + <code>&lt;dt&gt;</code> + <code>&lt;dd&gt;</code></td></tr>
  <tr><td>Tables</td><td><code>&lt;table&gt;</code> + <code>&lt;thead&gt;</code> + <code>&lt;tbody&gt;</code> + <code>&lt;th scope&gt;</code></td></tr>
</table>
<p><strong>Why it matters &mdash; concrete benefits:</strong></p>
<ul>
  <li><strong>Accessibility:</strong> screen readers announce landmarks (<em>&ldquo;banner,&rdquo; &ldquo;navigation,&rdquo; &ldquo;main,&rdquo; &ldquo;complementary&rdquo;</em>) so users can jump between regions. <code>&lt;button&gt;</code> is announced as a button; <code>&lt;div onclick&gt;</code> isn&rsquo;t.</li>
  <li><strong>SEO:</strong> Google&rsquo;s crawler weights <code>&lt;article&gt;</code> content differently than navigation. <code>&lt;time datetime="..."&gt;</code> feeds rich snippets.</li>
  <li><strong>Reader mode:</strong> Safari/Firefox/Edge readers extract content from <code>&lt;article&gt;</code> and ignore <code>&lt;aside&gt;</code> &mdash; cleaner reading on mobile.</li>
  <li><strong>Default styling:</strong> semantic tags inherit sensible defaults (<code>&lt;em&gt;</code> italic, <code>&lt;strong&gt;</code> bold, <code>&lt;code&gt;</code> monospace).</li>
  <li><strong>Maintainability:</strong> reading <code>&lt;article&gt;&lt;header&gt;...&lt;/header&gt;...&lt;/article&gt;</code> conveys structure instantly; reading <code>&lt;div class="post"&gt;&lt;div class="header"&gt;</code> requires understanding your CSS conventions.</li>
</ul>
<p><strong>Common mistakes:</strong> using <code>&lt;section&gt;</code> as a generic wrapper (it should have a heading and represent a thematic group); using <code>&lt;article&gt;</code> for non-self-contained content; nesting <code>&lt;main&gt;</code> multiple times (only one per page); using <code>&lt;b&gt;</code>/<code>&lt;i&gt;</code> for emphasis when <code>&lt;strong&gt;</code>/<code>&lt;em&gt;</code> carry semantic weight.</p>
<p>The accessibility tree (visible in browser devtools under &ldquo;Accessibility&rdquo;) shows how your markup is exposed to assistive tech &mdash; if it&rsquo;s a wall of generic divs and the structure is invisible there, semantic improvements will pay off immediately.</p>
'''

ANSWERS[3] = r'''
<p>The <code>&lt;picture&gt;</code> element gives the browser a list of image candidates and lets it pick the best fit based on the viewport, format support, or pixel density. It&rsquo;s the fix for &ldquo;serve a different image to mobile vs desktop&rdquo; that <code>srcset</code> alone can&rsquo;t solve.</p>
<pre><code>&lt;picture&gt;
  &lt;!-- Modern format with art-direction crop --&gt;
  &lt;source media="(min-width: 1200px)"
          srcset="hero-wide.avif 1x, hero-wide@2x.avif 2x"
          type="image/avif"&gt;
  &lt;source media="(min-width: 1200px)"
          srcset="hero-wide.jpg 1x, hero-wide@2x.jpg 2x"&gt;

  &lt;!-- Mobile crop --&gt;
  &lt;source srcset="hero-square.avif" type="image/avif"&gt;
  &lt;source srcset="hero-square.webp" type="image/webp"&gt;

  &lt;!-- Fallback --&gt;
  &lt;img src="hero-square.jpg"
       alt="Coastline at sunrise"
       width="600" height="600"&gt;
&lt;/picture&gt;</code></pre>
<p><strong>How the browser chooses:</strong> it walks <code>&lt;source&gt;</code> elements top-to-bottom, picking the first one whose <code>media</code> matches and whose <code>type</code> the browser can decode. If no source matches, it falls back to the <code>&lt;img&gt;</code>. Within a chosen source, <code>srcset</code> + <code>sizes</code> resolve which density variant to fetch.</p>
<p><strong>Three problems <code>&lt;picture&gt;</code> solves that <code>&lt;img srcset&gt;</code> doesn&rsquo;t:</strong></p>
<table>
  <tr><th>Problem</th><th>Solution</th></tr>
  <tr><td>Art direction</td><td>Different crop on mobile vs desktop (<code>media</code> attribute)</td></tr>
  <tr><td>Format negotiation</td><td>AVIF for new browsers, JPEG fallback (<code>type</code> attribute)</td></tr>
  <tr><td>Conditional source</td><td>Show different image based on color scheme (<code>media="(prefers-color-scheme: dark)"</code>)</td></tr>
</table>
<p><strong>When to use it vs plain <code>&lt;img srcset&gt;</code>:</strong></p>
<ul>
  <li><strong>Use <code>&lt;img srcset&gt;</code></strong> for the same image at different resolutions (1x/2x/3x or different widths).</li>
  <li><strong>Use <code>&lt;picture&gt;</code></strong> when the image itself differs &mdash; cropped differently, alternate format, dark-mode variant.</li>
</ul>
<p>Performance hint: always include <code>width</code> and <code>height</code> on the fallback <code>&lt;img&gt;</code> &mdash; they prevent layout shift even when picture chooses a different source. Modern formats (AVIF saves 30-50% over JPEG; WebP saves 25-30%) directly improve LCP scores. Use <code>&lt;link rel="preload" as="image" imagesrcset="..." imagesizes="..."&gt;</code> to preload the LCP image with the same negotiation rules.</p>
'''

ANSWERS[4] = r'''
<p>The <code>&lt;template&gt;</code> element holds inert HTML &mdash; markup that&rsquo;s parsed but not rendered, with no scripts running and no images loading until you clone its contents into the live DOM. It&rsquo;s the foundation for client-side templating and Web Components.</p>
<pre><code>&lt;template id="card-template"&gt;
  &lt;article class="card"&gt;
    &lt;img src="" alt=""&gt;
    &lt;h3&gt;&lt;/h3&gt;
    &lt;p class="price"&gt;&lt;/p&gt;
    &lt;button class="add-to-cart"&gt;Add to cart&lt;/button&gt;
  &lt;/article&gt;
&lt;/template&gt;

&lt;div id="product-list"&gt;&lt;/div&gt;

&lt;script&gt;
  const template = document.getElementById("card-template");
  const list     = document.getElementById("product-list");

  function renderProduct(product) {
    // Clone — true to copy children deeply
    const node = template.content.cloneNode(true);

    node.querySelector("img").src   = product.image;
    node.querySelector("img").alt   = product.name;
    node.querySelector("h3").textContent       = product.name;
    node.querySelector(".price").textContent   = `$${product.price}`;

    list.appendChild(node);
  }

  for (const p of products) renderProduct(p);
&lt;/script&gt;</code></pre>
<p><strong>Why <code>&lt;template&gt;</code> beats <code>innerHTML</code>:</strong></p>
<ul>
  <li><strong>Inert when parsed</strong> &mdash; <code>&lt;script&gt;</code> tags don&rsquo;t execute, <code>&lt;img&gt;</code> tags don&rsquo;t request, <code>&lt;video autoplay&gt;</code> doesn&rsquo;t play, custom elements don&rsquo;t upgrade. The template is a <strong>document fragment</strong> in a separate inert document.</li>
  <li><strong>No string concatenation</strong> &mdash; you assign properties on real DOM nodes; no risk of broken HTML or HTML injection from user data.</li>
  <li><strong>Faster cloning</strong> &mdash; cloning a parsed fragment is cheaper than re-parsing HTML strings on every render.</li>
  <li><strong>Inspector-friendly</strong> &mdash; the template content is visible in DevTools.</li>
</ul>
<p><strong>Template + custom elements:</strong> Web Components use templates inside <code>connectedCallback</code> to populate a Shadow DOM. The pattern is so common that the platform exposes <code>HTMLTemplateElement.content</code> as a <code>DocumentFragment</code> for convenient cloning.</p>
<p><strong>Server-rendered apps</strong> use <code>&lt;template&gt;</code> for client-side hydration: the server inlines templates for components that may render later (modal dialogs, tooltips). HTMX, Astro, and Lit-based libraries lean heavily on this pattern.</p>
<p><strong>Limitations:</strong> templates can&rsquo;t hold interpolated values directly (no <code>{{name}}</code> syntax) &mdash; you fill placeholders with JavaScript. For declarative two-way binding, libraries like Lit, Stimulus, or AlpineJS layer expressions on top.</p>
'''

ANSWERS[5] = r'''
<p>The <code>&lt;slot&gt;</code> element is a placeholder inside a Web Component&rsquo;s Shadow DOM where the component&rsquo;s <em>light DOM</em> children get projected. It&rsquo;s how custom elements compose: the user puts content between the custom tags; the component decides where that content appears in its internal structure.</p>
<pre><code>// Define the component
class UserCard extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: "open" }).innerHTML = `
      &lt;style&gt;
        .card { border: 1px solid #ccc; padding: 1em; }
        ::slotted([slot="avatar"]) { border-radius: 50%; }
      &lt;/style&gt;
      &lt;div class="card"&gt;
        &lt;slot name="avatar"&gt;&lt;/slot&gt;
        &lt;h3&gt;&lt;slot name="name"&gt;Anonymous&lt;/slot&gt;&lt;/h3&gt;
        &lt;p&gt;&lt;slot&gt;No bio provided.&lt;/slot&gt;&lt;/p&gt;     &lt;!-- default slot --&gt;
      &lt;/div&gt;
    `;
  }
}
customElements.define("user-card", UserCard);

// Use it
&lt;user-card&gt;
  &lt;img slot="avatar" src="alice.jpg" width="60" height="60"&gt;
  &lt;span slot="name"&gt;Alice Chen&lt;/span&gt;
  Senior engineer with a passion for distributed systems.
&lt;/user-card&gt;</code></pre>
<p><strong>How slots work:</strong></p>
<ul>
  <li><strong>Named slots</strong> &mdash; <code>&lt;slot name="avatar"&gt;</code> matches children with <code>slot="avatar"</code>.</li>
  <li><strong>Default slot</strong> &mdash; <code>&lt;slot&gt;</code> with no name catches everything else.</li>
  <li><strong>Fallback content</strong> &mdash; anything between the slot tags shows when no children are projected.</li>
  <li><strong>Light DOM stays in the document</strong> &mdash; slotted children are still children of the host element from the page&rsquo;s perspective; only their <em>rendering position</em> moves.</li>
</ul>
<p><strong>The <code>::slotted()</code> selector</strong> styles projected content <em>from inside</em> the shadow DOM &mdash; but only one level deep. It targets the slotted element itself, not its descendants. Cross-tree styling is intentionally limited to keep encapsulation tight.</p>
<p><strong>Why slots matter:</strong> they make components <em>composable</em> the way HTML tags are. A consumer of <code>&lt;user-card&gt;</code> can put any markup into the bio slot &mdash; links, lists, formatted text &mdash; and the component just renders it. This is the killer feature of Shadow DOM: encapsulated styles inside, flexible composition outside.</p>
<p>Frameworks like Lit, Stencil, and Vue 3 (in custom-element mode) use slots heavily; React&rsquo;s equivalent concept is <code>children</code> + named props, but it&rsquo;s a runtime concept rather than a platform primitive.</p>
'''

ANSWERS[6] = r'''
<p>Custom data attributes &mdash; any attribute starting with <code>data-</code> &mdash; let you attach arbitrary metadata to elements without invalidating HTML or colliding with future spec attributes. They&rsquo;re the documented escape hatch for &ldquo;I need to associate some data with this element.&rdquo;</p>
<pre><code>&lt;article data-post-id="42"
         data-author-id="7"
         data-tags="javascript,react,performance"
         data-published="2026-04-25"
         data-edit-count="3"&gt;
  &lt;h2&gt;A title&lt;/h2&gt;
  ...
&lt;/article&gt;</code></pre>
<p><strong>Reading from JavaScript via <code>dataset</code>:</strong></p>
<pre><code>const article = document.querySelector("article");
article.dataset.postId;       // "42"  (kebab-case → camelCase)
article.dataset.tags;         // "javascript,react,performance"
article.dataset.published;    // "2026-04-25"

// Setting writes back to the attribute
article.dataset.editCount = "4";
// → &lt;article data-edit-count="4"&gt; in DOM</code></pre>
<p><strong>Use cases that matter:</strong></p>
<ul>
  <li><strong>Event delegation:</strong> a single document-level click listener reads <code>dataset.action</code> from the clicked element to dispatch.</li>
  <li><strong>Configuration:</strong> third-party widgets (analytics, embeds) read <code>data-*</code> on their script tag for setup options.</li>
  <li><strong>Test selectors:</strong> <code>data-testid</code> is the recommended way to target elements in tests &mdash; immune to CSS or text changes.</li>
  <li><strong>State indicators:</strong> <code>data-state="loading"</code> with CSS like <code>[data-state="loading"] { opacity: 0.5; }</code> &mdash; cleaner than toggling classes.</li>
  <li><strong>Server-rendered apps:</strong> hydration libraries (HTMX, Hotwire, Stimulus) read <code>data-controller</code>, <code>data-action</code>, <code>data-target</code> attributes to wire up behavior.</li>
  <li><strong>Pass server data to scripts:</strong> instead of inline <code>&lt;script&gt;</code> blobs, write <code>data-config='{"key":"value"}'</code> and parse it.</li>
</ul>
<p><strong>CSS access via <code>attr()</code>:</strong> <code>div::after { content: attr(data-tooltip); }</code>. Combined with attribute selectors (<code>[data-state="active"] { ... }</code>), data attributes drive a lot of declarative styling.</p>
<p><strong>Best practices:</strong></p>
<ul>
  <li>Don&rsquo;t store secrets &mdash; data attributes are visible in HTML.</li>
  <li>Don&rsquo;t store complex objects as JSON if you can model them as multiple attributes &mdash; attributes are strings, parsing JSON is overhead.</li>
  <li>Use kebab-case in HTML, camelCase via <code>dataset</code>.</li>
  <li>Don&rsquo;t use them where ARIA attributes apply &mdash; <code>aria-expanded</code>, not <code>data-expanded</code>, when the meaning is &ldquo;is this expanded.&rdquo;</li>
</ul>
<p>For very large data payloads, <code>&lt;script type="application/json"&gt;</code> blocks are cleaner than stuffing JSON into attributes.</p>
'''

ANSWERS[7] = r'''
<p><code>&lt;b&gt;</code> and <code>&lt;strong&gt;</code> both render bold text by default, but they carry <strong>completely different semantic meaning</strong>. The visual collision masks an important distinction that screen readers and search engines respect.</p>
<table>
  <tr><th></th><th><code>&lt;strong&gt;</code></th><th><code>&lt;b&gt;</code></th></tr>
  <tr><td>Meaning</td><td>Strong importance / urgency / seriousness</td><td>Stylistic offset; no inherent importance</td></tr>
  <tr><td>Screen readers</td><td>May change emphasis or vocal stress</td><td>No semantic announcement</td></tr>
  <tr><td>Use case</td><td>Warning text, key terms, must-read content</td><td>Keywords, product names, lead-in words</td></tr>
  <tr><td>Spec category</td><td>Phrasing content with emphasis</td><td>Phrasing content without emphasis</td></tr>
</table>
<p><strong>Examples that show the difference:</strong></p>
<pre><code>&lt;!-- &lt;strong&gt;: importance --&gt;
&lt;p&gt;&lt;strong&gt;Warning:&lt;/strong&gt; Do not pour water on the fryer.&lt;/p&gt;
&lt;p&gt;Pages requiring authentication will redirect to &lt;strong&gt;/login&lt;/strong&gt;
   if the session has expired.&lt;/p&gt;

&lt;!-- &lt;b&gt;: stylistic only --&gt;
&lt;p&gt;The &lt;b&gt;Acme Pro&lt;/b&gt; subscription includes priority support.&lt;/p&gt;
&lt;p&gt;In the kitchen, &lt;b&gt;Sarah&lt;/b&gt; reached for the knife.&lt;/p&gt;</code></pre>
<p>The product name and the character&rsquo;s name aren&rsquo;t <em>important</em> &mdash; they&rsquo;re visually distinguished for readability.</p>
<p><strong>Practical decision rule:</strong> ask &ldquo;if a screen reader emphasized this with vocal stress, would that match the author&rsquo;s intent?&rdquo; If yes, use <code>&lt;strong&gt;</code>. If you just want bold styling without changing meaning, use <code>&lt;b&gt;</code> &mdash; or better yet, a CSS class so styling stays in CSS.</p>
<p><strong>Modern best practice:</strong> for purely visual bolding (e.g., a numeric value styled bold in a card layout), use a <code>&lt;span&gt;</code> with a class. Save <code>&lt;b&gt;</code> for traditional typographic uses (lead-in words, ship names, taxonomy terms) where the bolding has reading-level meaning but not importance. Use <code>&lt;strong&gt;</code> when the content actually matters more than what surrounds it.</p>
<p><strong>Nesting:</strong> <code>&lt;strong&gt;&lt;strong&gt;...&lt;/strong&gt;&lt;/strong&gt;</code> increases relative importance per the spec, but no browser or screen reader reflects this in 2026 &mdash; treat it as a stylistic curio rather than a feature.</p>
<p>For italics, the same pattern applies: <code>&lt;em&gt;</code> for emphasis, <code>&lt;i&gt;</code> for stylistic italics (foreign words, taxonomic names, technical terms).</p>
'''

ANSWERS[8] = r'''
<p><code>&lt;i&gt;</code> and <code>&lt;em&gt;</code> both render italic by default but mean very different things. The HTML5 spec explicitly redefined them to differentiate <em>stylistic</em> italics from <em>emphatic</em> italics &mdash; a distinction screen readers honor.</p>
<table>
  <tr><th></th><th><code>&lt;em&gt;</code></th><th><code>&lt;i&gt;</code></th></tr>
  <tr><td>Meaning</td><td>Stress emphasis &mdash; changes sentence meaning</td><td>Alternate voice or mood &mdash; no emphasis</td></tr>
  <tr><td>Screen readers</td><td>May vocally stress the content</td><td>No special announcement</td></tr>
  <tr><td>Use case</td><td>Linguistic emphasis</td><td>Foreign words, technical terms, ship names, internal thoughts</td></tr>
</table>
<p><strong>Why the distinction changes meaning:</strong></p>
<pre><code>&lt;p&gt;I &lt;em&gt;know&lt;/em&gt; you said it would work.&lt;/p&gt;
&lt;!-- Stress on "know" — implies skepticism, contrast --&gt;

&lt;p&gt;The phrase &lt;i&gt;c&rsquo;est la vie&lt;/i&gt; is French for "that&rsquo;s life."&lt;/p&gt;
&lt;!-- Italics indicate foreign-language phrase, no emphasis --&gt;

&lt;p&gt;HMS &lt;i&gt;Discovery&lt;/i&gt; sailed in 1776.&lt;/p&gt;
&lt;!-- Italics for ship name (typographic convention) --&gt;

&lt;p&gt;The class &lt;i&gt;Mammalia&lt;/i&gt; includes humans.&lt;/p&gt;
&lt;!-- Italics for taxonomic name --&gt;

&lt;p&gt;She thought, &lt;i&gt;this can&rsquo;t be right&lt;/i&gt;.&lt;/p&gt;
&lt;!-- Italics for internal monologue --&gt;</code></pre>
<p>An <code>&lt;em&gt;</code> changes how the sentence should be read aloud; an <code>&lt;i&gt;</code> doesn&rsquo;t.</p>
<p><strong>The semantic stack:</strong></p>
<ul>
  <li><code>&lt;em&gt;</code> &mdash; emphasis (sentence-level stress).</li>
  <li><code>&lt;i&gt;</code> &mdash; alternate voice (typographic convention).</li>
  <li><code>&lt;cite&gt;</code> &mdash; title of a creative work; also italic by default but specifically for citations.</li>
  <li><code>&lt;dfn&gt;</code> &mdash; the term being defined; italic by default.</li>
  <li><code>&lt;var&gt;</code> &mdash; mathematical/programming variable; italic by default.</li>
</ul>
<p>Each defaults to italic, but they tell the browser <em>why</em> the text is italic. Screen readers, search engines, and dictionaries can use this information.</p>
<p><strong>For purely visual italics</strong> (an italicized caption, a stylistic flourish), use a CSS class &mdash; <code>font-style: italic</code> &mdash; rather than misusing semantic tags.</p>
<p><strong>Common mistake:</strong> defaulting to <code>&lt;em&gt;</code> for every italicized word. If the italics carry no spoken-emphasis meaning &mdash; book titles, technical jargon, foreign phrases &mdash; <code>&lt;i&gt;</code> or a more specific tag (<code>&lt;cite&gt;</code>, <code>&lt;dfn&gt;</code>) is more accurate. Same pattern as <code>&lt;b&gt;</code> vs <code>&lt;strong&gt;</code>: visual identity, semantic difference.</p>
'''

ANSWERS[9] = r'''
<p>The <code>&lt;dialog&gt;</code> element is the native modal/popover primitive. It handles focus management, the Escape key, the backdrop, and (since 2024) the top-layer rendering that previously required <code>position: fixed</code> + custom z-index management. It&rsquo;s a substantial replacement for the dozens of modal libraries that historically dominated.</p>
<pre><code>&lt;dialog id="confirm-dialog"&gt;
  &lt;form method="dialog"&gt;
    &lt;h2&gt;Delete this item?&lt;/h2&gt;
    &lt;p&gt;This action cannot be undone.&lt;/p&gt;
    &lt;menu&gt;
      &lt;button value="cancel" type="submit"&gt;Cancel&lt;/button&gt;
      &lt;button value="confirm" type="submit"&gt;Delete&lt;/button&gt;
    &lt;/menu&gt;
  &lt;/form&gt;
&lt;/dialog&gt;

&lt;script&gt;
  const dlg = document.getElementById("confirm-dialog");
  document.querySelector(".delete-btn").addEventListener("click", () =&gt; {
    dlg.showModal();
  });
  dlg.addEventListener("close", () =&gt; {
    if (dlg.returnValue === "confirm") {
      // proceed with delete
    }
  });
&lt;/script&gt;</code></pre>
<p><strong>Two opening modes:</strong></p>
<ul>
  <li><code>.showModal()</code> &mdash; modal; the dialog renders in the <strong>top layer</strong> (above everything regardless of z-index), the rest of the page becomes inert (clicks and keystrokes blocked), focus is trapped inside, and a <code>::backdrop</code> pseudo-element appears behind.</li>
  <li><code>.show()</code> &mdash; non-modal; the dialog floats but the page remains interactive. No focus trap, no backdrop.</li>
</ul>
<p><strong>Built-in behaviors:</strong></p>
<ul>
  <li><strong>Focus management:</strong> on open, focus moves to the first focusable child or the dialog itself; on close, focus returns to the element that opened it.</li>
  <li><strong>Escape key</strong> closes a modal dialog automatically.</li>
  <li><strong>Form submission via <code>method="dialog"</code></strong> closes the dialog and sets <code>returnValue</code> to the submit button&rsquo;s <code>value</code>.</li>
  <li><strong>Light dismiss</strong> (clicking outside the dialog) doesn&rsquo;t happen by default but is easy to add.</li>
</ul>
<pre><code>// light-dismiss pattern: clicking the backdrop closes the dialog
dlg.addEventListener("click", (e) =&gt; {
  if (e.target === dlg) dlg.close();
});</code></pre>
<p><strong>Styling the backdrop:</strong></p>
<pre><code>dialog::backdrop {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
dialog[open] {
  animation: fade-in 0.2s ease-out;
}</code></pre>
<p><strong>Top-layer rendering</strong> means the dialog escapes any <code>overflow: hidden</code> or stacking context constraints. This solved a decade of z-index whack-a-mole. The popover API (<code>popover</code> attribute) extends the same top-layer mechanism to non-modal popovers like menus and tooltips.</p>
<p><strong>Accessibility:</strong> the role is implicitly <code>dialog</code> (or <code>alertdialog</code> if you set it). Always include a label (heading or <code>aria-labelledby</code>) so screen readers announce what the dialog is about. <code>&lt;dialog&gt;</code> beats almost any custom modal &mdash; less code, correct accessibility, no library.</p>
'''

ANSWERS[10] = r'''
<p>ARIA (Accessible Rich Internet Applications) is a set of attributes that describe the role, state, and properties of elements to assistive technology &mdash; specifically when native HTML semantics fall short. ARIA is a bridge: HTML covers the common cases natively; ARIA covers everything else.</p>
<p><strong>Three categories of ARIA attributes:</strong></p>
<table>
  <tr><th>Category</th><th>What it conveys</th><th>Examples</th></tr>
  <tr><td>Roles</td><td>What kind of element this is</td><td><code>role="button"</code>, <code>role="navigation"</code>, <code>role="dialog"</code>, <code>role="tablist"</code></td></tr>
  <tr><td>Properties</td><td>Stable characteristics</td><td><code>aria-label</code>, <code>aria-labelledby</code>, <code>aria-describedby</code>, <code>aria-required</code></td></tr>
  <tr><td>States</td><td>Dynamic, change with interaction</td><td><code>aria-expanded</code>, <code>aria-checked</code>, <code>aria-hidden</code>, <code>aria-current</code>, <code>aria-busy</code></td></tr>
</table>
<p><strong>Examples in practice:</strong></p>
<pre><code>&lt;!-- Custom button (NEVER do this in real code; use &lt;button&gt;) --&gt;
&lt;div role="button"
     tabindex="0"
     aria-pressed="false"
     onclick="toggle()"
     onkeydown="if (event.key === 'Enter' || event.key === ' ') toggle()"&gt;
  Toggle theme
&lt;/div&gt;

&lt;!-- Icon-only button needs a label --&gt;
&lt;button aria-label="Close"&gt;
  &lt;svg&gt;&lt;path d="M6 6l12 12M18 6l-12 12"/&gt;&lt;/svg&gt;
&lt;/button&gt;

&lt;!-- Disclosure widget --&gt;
&lt;button aria-expanded="false" aria-controls="menu1"&gt;Menu&lt;/button&gt;
&lt;ul id="menu1" hidden&gt;...&lt;/ul&gt;

&lt;!-- Live region — announce updates --&gt;
&lt;div aria-live="polite" id="status"&gt;Saved at 4:32 PM&lt;/div&gt;

&lt;!-- Decorative SVG — hide from AT --&gt;
&lt;svg aria-hidden="true"&gt;...&lt;/svg&gt;</code></pre>
<p><strong>The first rule of ARIA:</strong> &ldquo;don&rsquo;t use ARIA.&rdquo; If a native element exists for what you&rsquo;re building, use it. <code>&lt;button&gt;</code> beats <code>&lt;div role="button" tabindex="0"&gt;</code> every time &mdash; the native version handles keyboard, focus, click, and form submission correctly with zero code.</p>
<p><strong>When ARIA earns its place:</strong></p>
<ul>
  <li>Custom widgets without native equivalents (combobox, tablist, tree, grid).</li>
  <li>Adding labels to icon-only controls (<code>aria-label</code>).</li>
  <li>Conveying dynamic state changes (<code>aria-expanded</code>, <code>aria-busy</code>).</li>
  <li>Live regions for content that updates without focus moving (toast notifications, chat messages).</li>
  <li>Hiding purely decorative elements (<code>aria-hidden="true"</code>).</li>
</ul>
<p><strong>Common ARIA mistakes:</strong></p>
<ul>
  <li>Adding <code>role="button"</code> to a real <code>&lt;button&gt;</code> &mdash; redundant, can override.</li>
  <li>Using <code>aria-label</code> on a control that has visible text &mdash; the label takes precedence over visible text and may diverge.</li>
  <li>Hiding interactive elements with <code>aria-hidden="true"</code> &mdash; users can still focus them via Tab, but screen readers don&rsquo;t announce them. Confusing.</li>
  <li>Using <code>aria-live</code> with <code>assertive</code> for non-urgent updates &mdash; interrupts the user&rsquo;s screen reader flow.</li>
</ul>
<p><strong>Testing:</strong> use NVDA + Firefox or VoiceOver + Safari to verify your ARIA does what you intended. The Chrome DevTools Accessibility panel shows the computed accessibility tree &mdash; what assistive tech actually sees.</p>
'''

ANSWERS[11] = r'''
<p>Lazy loading defers fetching of off-screen images until the user scrolls near them &mdash; saving bandwidth and improving initial page load. HTML5 provides this natively via the <code>loading</code> attribute, no JavaScript or library needed.</p>
<pre><code>&lt;!-- Native lazy loading — supported in all modern browsers --&gt;
&lt;img src="photo.jpg"
     alt="..."
     width="800" height="600"
     loading="lazy"&gt;

&lt;!-- Eager loading (default for images) — load immediately --&gt;
&lt;img src="hero.jpg" alt="Hero" loading="eager"&gt;

&lt;!-- Iframe lazy loading also works --&gt;
&lt;iframe src="https://youtube.com/embed/abc"
        title="Video"
        loading="lazy"&gt;&lt;/iframe&gt;</code></pre>
<p>The browser uses heuristics &mdash; viewport proximity, scroll velocity, network conditions &mdash; to decide when to fetch. Typically images within ~3000 pixels of the viewport start loading. The exact threshold isn&rsquo;t in the spec to allow optimization.</p>
<p><strong>Critical: always include <code>width</code> and <code>height</code></strong>. Without them, the browser doesn&rsquo;t know how much space to reserve, so the image &ldquo;pops in&rdquo; later, shifting layout (terrible CLS score). The numeric attributes (<em>not</em> CSS) establish the aspect ratio that lets the placeholder hold its shape.</p>
<p><strong>When to skip <code>loading="lazy"</code>:</strong></p>
<ul>
  <li><strong>LCP image</strong> &mdash; the largest image in the initial viewport. Lazy-loading it adds a delay before display. Use <code>loading="eager"</code> (or omit) and consider <code>fetchpriority="high"</code>.</li>
  <li><strong>Above-the-fold images</strong> in general &mdash; lazy loading them creates layout-shift risk.</li>
  <li><strong>Print scenarios</strong> &mdash; users printing the page need all images.</li>
</ul>
<p><strong>The <code>fetchpriority</code> attribute</strong> (2023+) gives more control:</p>
<pre><code>&lt;img src="hero.jpg" fetchpriority="high"&gt;     &lt;!-- LCP image --&gt;
&lt;img src="logo.png" fetchpriority="low"&gt;      &lt;!-- decorative, not critical --&gt;</code></pre>
<p><strong>JavaScript fallback</strong> for older browsers (rarely needed in 2026) uses <code>IntersectionObserver</code>:</p>
<pre><code>const observer = new IntersectionObserver((entries) =&gt; {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      entry.target.src = entry.target.dataset.src;
      observer.unobserve(entry.target);
    }
  }
});
document.querySelectorAll("img[data-src]")
        .forEach((img) =&gt; observer.observe(img));</code></pre>
<p><strong>Lazy loading + responsive images</strong> compose perfectly &mdash; <code>srcset</code> still negotiates which size to fetch, <code>loading="lazy"</code> still defers when. Combined with modern formats (AVIF, WebP), you get smaller images, lazy-loaded, with no JavaScript &mdash; a major win for Core Web Vitals.</p>
<p><strong>SEO note:</strong> Googlebot respects <code>loading="lazy"</code> when crawling, so lazy images are still indexed.</p>
'''

ANSWERS[12] = r'''
<p>The question asks about <code>&lt;o&gt;</code>, but <strong>there is no <code>&lt;o&gt;</code> element in HTML</strong>. This is a common confusion &mdash; people sometimes mistype <code>&lt;p&gt;</code>, <code>&lt;ol&gt;</code>, or <code>&lt;output&gt;</code>. Here are the elements that may be intended:</p>
<table>
  <tr><th>Element</th><th>Purpose</th></tr>
  <tr><td><code>&lt;ol&gt;</code></td><td>Ordered list (numbered items)</td></tr>
  <tr><td><code>&lt;output&gt;</code></td><td>Result of a calculation or user action</td></tr>
  <tr><td><code>&lt;option&gt;</code></td><td>Single option in a select or datalist</td></tr>
  <tr><td><code>&lt;optgroup&gt;</code></td><td>Group of options inside a select</td></tr>
  <tr><td><code>&lt;object&gt;</code></td><td>Embed external resource (PDF, applet, image)</td></tr>
</table>
<p><strong>The <code>&lt;output&gt;</code> element</strong> is a hidden gem &mdash; designed specifically for displaying results of calculations or form values, with built-in accessibility for live updates:</p>
<pre><code>&lt;form oninput="result.value = parseFloat(a.value) + parseFloat(b.value)"&gt;
  &lt;input type="number" id="a" name="a" value="0"&gt; +
  &lt;input type="number" id="b" name="b" value="0"&gt; =
  &lt;output name="result" for="a b"&gt;0&lt;/output&gt;
&lt;/form&gt;</code></pre>
<p>The <code>for</code> attribute lists IDs of inputs that affect this output &mdash; pure metadata for assistive tech and accessibility tools. Screen readers may announce the output as a result region rather than generic text.</p>
<p><strong>The <code>&lt;object&gt;</code> element</strong> embeds external resources with built-in fallback for unsupported types:</p>
<pre><code>&lt;object data="report.pdf"
        type="application/pdf"
        width="600" height="800"&gt;
  &lt;p&gt;Your browser can&rsquo;t display PDFs.
     &lt;a href="report.pdf"&gt;Download&lt;/a&gt;.&lt;/p&gt;
&lt;/object&gt;</code></pre>
<p>Anything between the open and close tags is fallback content for browsers that can&rsquo;t handle the embedded resource.</p>
<p><strong>The <code>&lt;ol&gt;</code> element</strong> is the ordered list, with attributes that <code>&lt;ul&gt;</code> doesn&rsquo;t have:</p>
<pre><code>&lt;ol type="A" start="3" reversed&gt;
  &lt;li&gt;Third item&lt;/li&gt;       &lt;!-- E (counts down) --&gt;
  &lt;li&gt;Second item&lt;/li&gt;      &lt;!-- D --&gt;
  &lt;li&gt;First item&lt;/li&gt;       &lt;!-- C --&gt;
&lt;/ol&gt;</code></pre>
<p><strong>If the question really intends <code>&lt;o&gt;</code></strong>: HTML lets you use any unrecognized tag &mdash; browsers will treat <code>&lt;o&gt;</code> as a generic inline element with no semantics, no styling, and no accessibility benefit. Don&rsquo;t do this. Custom semantics belong in custom elements (<code>&lt;my-component&gt;</code> with a hyphen) registered via the Custom Elements API.</p>
<p>The takeaway: stick to documented HTML elements. The MDN HTML element reference is the authoritative list of what exists; anything not on it is invalid.</p>
'''

ANSWERS[13] = r'''
<p>Shadow DOM is a browser-native encapsulation mechanism: a hidden DOM tree attached to an element that&rsquo;s isolated from the rest of the document &mdash; CSS doesn&rsquo;t leak in or out, query selectors don&rsquo;t cross the boundary, and IDs are scoped. It&rsquo;s the foundation that makes Web Components actually composable.</p>
<pre><code>class TweetEmbed extends HTMLElement {
  connectedCallback() {
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      &lt;style&gt;
        /* These styles ONLY apply inside this component */
        :host { display: block; max-width: 500px; }
        .tweet { border: 1px solid #ddd; padding: 1em; }
        h3 { color: #1da1f2; margin: 0; }
      &lt;/style&gt;
      &lt;article class="tweet"&gt;
        &lt;h3&gt;${this.getAttribute("author")}&lt;/h3&gt;
        &lt;p&gt;${this.getAttribute("content")}&lt;/p&gt;
      &lt;/article&gt;
    `;
  }
}
customElements.define("tweet-embed", TweetEmbed);</code></pre>
<p><strong>Three crucial isolation properties:</strong></p>
<ul>
  <li><strong>Style scoping</strong> &mdash; CSS in the shadow tree doesn&rsquo;t affect outer DOM; outer page CSS doesn&rsquo;t affect shadow DOM. <code>h3</code> inside the shadow only matches <em>shadow</em> h3s.</li>
  <li><strong>DOM scoping</strong> &mdash; <code>document.querySelectorAll("h3")</code> finds zero shadow elements. <code>shadowRoot.querySelector("h3")</code> finds them.</li>
  <li><strong>Event retargeting</strong> &mdash; events that bubble out of a shadow tree have their <code>target</code> rewritten to the host element, so outer listeners don&rsquo;t see internal structure.</li>
</ul>
<p><strong>Open vs closed shadows:</strong></p>
<table>
  <tr><th>Mode</th><th>External access</th><th>Use case</th></tr>
  <tr><td><code>open</code></td><td><code>element.shadowRoot</code> available externally</td><td>Most components &mdash; allows debugging and integration</td></tr>
  <tr><td><code>closed</code></td><td><code>element.shadowRoot</code> returns null</td><td>Rarely needed; doesn&rsquo;t prevent determined access</td></tr>
</table>
<p><strong>What crosses the shadow boundary:</strong></p>
<ul>
  <li><strong>Inheritable CSS</strong> (<code>color</code>, <code>font-family</code>) inherits from the host into the shadow.</li>
  <li><strong>CSS custom properties</strong> (<code>--theme-color</code>) cross freely &mdash; the standard theming mechanism.</li>
  <li><strong><code>::part()</code> pseudo-element</strong> &mdash; components opt-in to letting outer CSS style specific internal elements.</li>
  <li><strong>Slotted content</strong> &mdash; light-DOM children are projected through <code>&lt;slot&gt;</code> elements.</li>
</ul>
<p><strong>The <code>:host</code> selector</strong> styles the host element from inside the shadow. <code>:host(.featured)</code> targets the host when it has a class. <code>:host-context()</code> matches based on ancestors of the host.</p>
<p><strong>Where Shadow DOM shines:</strong> embedded widgets that must not be affected by the host page&rsquo;s CSS (third-party embeds, design system components, browser extensions injecting UI). For the cost of a slightly more complex API, you get bulletproof style isolation that <code>div + class</code> conventions never deliver. The <code>&lt;details&gt;</code>, <code>&lt;video&gt;</code>, and <code>&lt;input type="range"&gt;</code> elements all use shadow DOM internally &mdash; their controls are real elements you can&rsquo;t style without explicit CSS hooks.</p>
'''

ANSWERS[14] = r'''
<p>The <code>&lt;data&gt;</code> element pairs human-readable text with a machine-readable value via the <code>value</code> attribute. The visible text is what users read; the <code>value</code> is what scripts and tools consume.</p>
<pre><code>&lt;p&gt;
  Stock: &lt;data value="389"&gt;Three hundred and eighty-nine&lt;/data&gt; units
&lt;/p&gt;

&lt;p&gt;
  Released: &lt;data value="3.7.1"&gt;Version 3 (April 2026)&lt;/data&gt;
&lt;/p&gt;

&lt;ul&gt;
  &lt;li&gt;&lt;data value="98765"&gt;Acme Pro Widget&lt;/data&gt; &mdash; $49&lt;/li&gt;
  &lt;li&gt;&lt;data value="98766"&gt;Acme Lite Widget&lt;/data&gt; &mdash; $29&lt;/li&gt;
&lt;/ul&gt;</code></pre>
<p><strong>Where <code>&lt;data&gt;</code> fits:</strong></p>
<ul>
  <li><strong>Product SKUs / IDs</strong> &mdash; user sees product name, scripts read the SKU.</li>
  <li><strong>Friendly names for codes</strong> &mdash; show &ldquo;United States,&rdquo; emit ISO code <code>US</code> for processing.</li>
  <li><strong>Data attributes for UI components</strong> &mdash; e.g. a sortable list where the visible text is descriptive but the value is for sorting.</li>
  <li><strong>Microdata / structured data</strong> &mdash; <code>&lt;data&gt;</code> integrates with <code>itemprop</code> when the visible value differs from the indexed value.</li>
</ul>
<p><strong>For dates and times specifically, use <code>&lt;time&gt;</code></strong> &mdash; it&rsquo;s the specialized version with a <code>datetime</code> attribute that&rsquo;s machine-parseable:</p>
<pre><code>&lt;time datetime="2026-04-25T14:30:00Z"&gt;today at 2:30 PM&lt;/time&gt;
&lt;time datetime="2025"&gt;last year&lt;/time&gt;
&lt;time datetime="PT5M"&gt;5 minutes&lt;/time&gt;</code></pre>
<p><strong>Reading <code>&lt;data&gt;</code> from JavaScript:</strong></p>
<pre><code>const node = document.querySelector("data");
node.value;            // "389" — machine value
node.textContent;      // "Three hundred and eighty-nine" — display</code></pre>
<p><strong>How it differs from <code>data-*</code> attributes:</strong></p>
<table>
  <tr><th></th><th><code>&lt;data&gt;</code> element</th><th><code>data-*</code> attribute</th></tr>
  <tr><td>Visible to user</td><td>Yes</td><td>No</td></tr>
  <tr><td>Pairs display + machine values</td><td>Yes (built in)</td><td>No</td></tr>
  <tr><td>Best for</td><td>Inline values where both display and machine forms matter</td><td>Metadata not visible to users</td></tr>
</table>
<p><strong>Honest assessment:</strong> <code>&lt;data&gt;</code> is rarely seen in production. Most teams use <code>data-*</code> attributes or microdata (<code>itemprop</code>) for the same job. <code>&lt;data&gt;</code> earns its place when display and machine value genuinely differ in inline content &mdash; otherwise <code>&lt;span data-id="..."&gt;</code> is more common. Knowing it exists matters for accessibility audits and for parsers that look for it (some search engine crawlers, browser extensions).</p>
'''

ANSWERS[15] = r'''
<p>Microdata is HTML&rsquo;s built-in way to embed structured data in pages so search engines, browsers, and tools can extract meaning beyond the visible text. The HTML5 spec defines a small set of attributes &mdash; <code>itemscope</code>, <code>itemtype</code>, <code>itemprop</code>, <code>itemref</code>, <code>itemid</code> &mdash; that mark up entities and their properties.</p>
<pre><code>&lt;article itemscope itemtype="https://schema.org/Article"&gt;
  &lt;h1 itemprop="headline"&gt;Modern HTML Patterns&lt;/h1&gt;

  &lt;p&gt;By
    &lt;span itemprop="author" itemscope itemtype="https://schema.org/Person"&gt;
      &lt;span itemprop="name"&gt;Jane Smith&lt;/span&gt;
    &lt;/span&gt;
  &lt;/p&gt;

  &lt;time itemprop="datePublished" datetime="2026-04-25"&gt;
    April 25, 2026
  &lt;/time&gt;

  &lt;img itemprop="image"
       src="hero.jpg"
       alt="Article hero"&gt;

  &lt;div itemprop="articleBody"&gt;
    &lt;p&gt;Web development has evolved...&lt;/p&gt;
  &lt;/div&gt;
&lt;/article&gt;</code></pre>
<p><strong>The attribute roles:</strong></p>
<ul>
  <li><code>itemscope</code> &mdash; declares an element as a structured-data item.</li>
  <li><code>itemtype</code> &mdash; URL identifying the item&rsquo;s type (typically a Schema.org URL).</li>
  <li><code>itemprop</code> &mdash; names a property of the enclosing item.</li>
  <li><code>itemref</code> &mdash; references properties from elsewhere in the document by ID (when grouping isn&rsquo;t natural).</li>
  <li><code>itemid</code> &mdash; globally unique identifier for the item (URL).</li>
</ul>
<p><strong>What the markup unlocks:</strong></p>
<ul>
  <li><strong>Rich snippets in Google search</strong> &mdash; star ratings, prices, recipe times, breadcrumbs, FAQ answers, video thumbnails appear in search results when the markup is correct.</li>
  <li><strong>Browser features</strong> &mdash; reading mode, &ldquo;reader actions&rdquo; on iOS, &ldquo;copy as event&rdquo; for calendar items.</li>
  <li><strong>Voice assistants and answer boxes</strong> can extract facts directly.</li>
  <li><strong>Browser extensions</strong> like price trackers, recipe collectors, citation tools.</li>
</ul>
<p><strong>Schema.org</strong> is the shared vocabulary that defines hundreds of types: <code>Person</code>, <code>Organization</code>, <code>Product</code>, <code>Recipe</code>, <code>Event</code>, <code>Review</code>, <code>BreadcrumbList</code>, <code>FAQPage</code>, etc. Each type has documented properties.</p>
<p><strong>JSON-LD vs Microdata:</strong> Google now <em>prefers</em> <strong>JSON-LD</strong> embedded in <code>&lt;script type="application/ld+json"&gt;</code> blocks because it separates structured data from presentation:</p>
<pre><code>&lt;script type="application/ld+json"&gt;
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Modern HTML Patterns",
  "author": { "@type": "Person", "name": "Jane Smith" },
  "datePublished": "2026-04-25"
}
&lt;/script&gt;</code></pre>
<p>JSON-LD is easier to maintain &mdash; one block per page rather than scattered attributes &mdash; and supports things microdata can&rsquo;t (cross-references, deeper nesting). Most modern stacks use JSON-LD; microdata remains useful when the visible content already structures the data well, eliminating the duplication.</p>
<p>Test your structured data with Google&rsquo;s Rich Results Test to see exactly what gets extracted.</p>
'''

ANSWERS[16] = r'''
<p><code>&lt;details&gt;</code> + <code>&lt;summary&gt;</code> create a native disclosure widget &mdash; the user clicks the summary to expand or collapse the details. Built-in keyboard support, screen-reader announcement, and zero JavaScript required.</p>
<pre><code>&lt;details&gt;
  &lt;summary&gt;What&rsquo;s included in the Pro plan?&lt;/summary&gt;
  &lt;ul&gt;
    &lt;li&gt;Unlimited projects&lt;/li&gt;
    &lt;li&gt;24/7 priority support&lt;/li&gt;
    &lt;li&gt;Custom integrations&lt;/li&gt;
  &lt;/ul&gt;
&lt;/details&gt;

&lt;details open&gt;
  &lt;summary&gt;Cancellation policy&lt;/summary&gt;
  &lt;p&gt;Cancel anytime; no refund for the current period.&lt;/p&gt;
&lt;/details&gt;</code></pre>
<p><strong>Mechanism:</strong></p>
<ul>
  <li>The <code>&lt;summary&gt;</code> is the always-visible label.</li>
  <li>Everything else inside <code>&lt;details&gt;</code> is the expandable region.</li>
  <li>The <code>open</code> attribute reflects state &mdash; toggling it (via click, keyboard, or JS) opens/closes the panel.</li>
  <li>A <code>toggle</code> event fires on every state change.</li>
</ul>
<p><strong>Native accessibility:</strong></p>
<ul>
  <li>The disclosure widget role is implicit &mdash; screen readers announce &ldquo;collapsed&rdquo; or &ldquo;expanded.&rdquo;</li>
  <li>Tab focuses the summary; Enter and Space toggle.</li>
  <li>Find-in-page (Ctrl+F) traverses closed details and auto-expands them in modern browsers.</li>
  <li>Print stylesheets see the open state &mdash; only open sections print unless you override.</li>
</ul>
<p><strong>Accordion pattern with <code>name</code>:</strong> as of 2024, the <code>name</code> attribute makes details elements behave as a radio group &mdash; opening one closes the others.</p>
<pre><code>&lt;details name="faq"&gt;
  &lt;summary&gt;Question 1&lt;/summary&gt;
  &lt;p&gt;Answer 1&lt;/p&gt;
&lt;/details&gt;
&lt;details name="faq"&gt;
  &lt;summary&gt;Question 2&lt;/summary&gt;
  &lt;p&gt;Answer 2&lt;/p&gt;
&lt;/details&gt;</code></pre>
<p>This eliminates the JavaScript that accordion libraries used to require.</p>
<p><strong>Styling the marker</strong> (the disclosure triangle):</p>
<pre><code>summary { list-style: none; cursor: pointer; }
summary::-webkit-details-marker { display: none; }   /* legacy WebKit */
summary::before {
  content: "\25B6";    /* ▶ */
  display: inline-block;
  margin-right: 0.5em;
  transition: transform 0.2s;
}
details[open] summary::before {
  transform: rotate(90deg);
}</code></pre>
<p><strong>Animation:</strong> details/summary doesn&rsquo;t animate height by default. Modern CSS uses <code>::details-content</code> (Chrome 131+) or <code>interpolate-size: allow-keywords</code> for smooth height transitions; older approaches use JavaScript with explicit height calculations.</p>
<p><strong>When NOT to use details:</strong> menu items (use a real button + popover), modals (use <code>&lt;dialog&gt;</code>), or content that needs explicit ARIA roles. For straightforward expand/collapse, the native element is the right tool.</p>
'''

ANSWERS[17] = r'''
<p>Custom elements let you define new HTML tags with their own behavior, lifecycle, and shadow DOM. Once registered, you use <code>&lt;my-tag&gt;</code> like any built-in element &mdash; framework-free, browser-native components.</p>
<pre><code>class CountdownTimer extends HTMLElement {
  // 1. Observed attributes — changes trigger attributeChangedCallback
  static observedAttributes = ["seconds"];

  // 2. Element constructor (avoid DOM access here — children may not exist)
  constructor() {
    super();
    this._intervalId = null;
  }

  // 3. Connected to the document — set up DOM, listeners, timers
  connectedCallback() {
    this.attachShadow({ mode: "open" }).innerHTML = `
      &lt;style&gt;
        :host { display: inline-block; font-family: monospace; font-size: 2em; }
      &lt;/style&gt;
      &lt;span class="display"&gt;&lt;/span&gt;
    `;
    this._display = this.shadowRoot.querySelector(".display");
    this._update(Number(this.getAttribute("seconds")) || 60);
  }

  // 4. Disconnected — clean up
  disconnectedCallback() {
    if (this._intervalId) clearInterval(this._intervalId);
  }

  // 5. Attribute changed — react to attribute updates
  attributeChangedCallback(name, oldVal, newVal) {
    if (name === "seconds" &amp;&amp; this.isConnected) {
      this._update(Number(newVal));
    }
  }

  _update(seconds) {
    if (this._intervalId) clearInterval(this._intervalId);
    let remaining = seconds;
    const tick = () =&gt; {
      this._display.textContent = `${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, "0")}`;
      if (remaining &lt;= 0) { clearInterval(this._intervalId); this.dispatchEvent(new Event("done")); }
      remaining--;
    };
    tick();
    this._intervalId = setInterval(tick, 1000);
  }
}

// Register — name MUST contain a hyphen
customElements.define("countdown-timer", CountdownTimer);

// Use in HTML
&lt;countdown-timer seconds="120"&gt;&lt;/countdown-timer&gt;</code></pre>
<p><strong>The four lifecycle callbacks:</strong></p>
<table>
  <tr><th>Callback</th><th>Fires when</th></tr>
  <tr><td><code>constructor</code></td><td>Element created (avoid DOM operations)</td></tr>
  <tr><td><code>connectedCallback</code></td><td>Inserted into a document &mdash; ideal for setup</td></tr>
  <tr><td><code>disconnectedCallback</code></td><td>Removed from document &mdash; clean up timers, listeners</td></tr>
  <tr><td><code>attributeChangedCallback</code></td><td>Observed attribute changed</td></tr>
</table>
<p><strong>Two flavors of custom elements:</strong></p>
<ul>
  <li><strong>Autonomous</strong> &mdash; <code>extends HTMLElement</code>; new tag from scratch. Most common.</li>
  <li><strong>Customized built-in</strong> &mdash; <code>extends HTMLButtonElement</code>; enhance an existing element. Used as <code>&lt;button is="my-button"&gt;</code>. Safari historically didn&rsquo;t support these, so adoption has been mixed.</li>
</ul>
<p><strong>Naming rules:</strong> custom elements <em>must</em> have a hyphen in the name (<code>my-element</code>, not <code>myelement</code>) &mdash; this prevents collision with future standard elements.</p>
<p><strong>Lit, Stencil, FAST</strong> are popular libraries that build on custom elements with reactive templates and TypeScript-friendly APIs &mdash; the platform primitives plus ergonomics. Web Components don&rsquo;t replace React/Vue/Angular for app-scale work, but they&rsquo;re excellent for design systems, third-party widgets, and components that must work across multiple frameworks (a Lit component drops into React, Vue, and plain HTML identically).</p>
'''

ANSWERS[18] = r'''
<p><code>&lt;isindex&gt;</code> was an obsolete element from HTML&rsquo;s earliest days &mdash; circa 1993 &mdash; designed for primitive single-field search forms when forms didn&rsquo;t exist yet. It rendered as a single text input, and submitting it generated a GET request with the typed value as the entire query string.</p>
<pre><code>&lt;!-- Historical use (obsolete, do NOT use) --&gt;
&lt;isindex prompt="Search this index:"&gt;</code></pre>
<p>Pressing Enter would submit to the page&rsquo;s URL with <code>?searchterm</code> appended &mdash; with no <code>name=</code>, just the bare value.</p>
<p><strong>Why it was deprecated and removed:</strong></p>
<ul>
  <li><strong>Behavior was bizarre</strong> &mdash; it submitted to the current URL, not a configurable action.</li>
  <li><strong>Only one allowed per document</strong> &mdash; couldn&rsquo;t have multiple search fields.</li>
  <li><strong>It mixed presentation and behavior</strong> &mdash; both a UI element <em>and</em> a form-submission mechanism.</li>
  <li><strong>HTML 4.01</strong> deprecated it.</li>
  <li><strong>HTML5</strong> removed it entirely &mdash; modern browsers ignore it.</li>
</ul>
<p><strong>Modern equivalent:</strong></p>
<pre><code>&lt;form action="/search" method="get" role="search"&gt;
  &lt;label for="q"&gt;Search this site:&lt;/label&gt;
  &lt;input type="search" id="q" name="q" required&gt;
  &lt;button type="submit"&gt;Go&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p>The <code>&lt;form&gt;</code> + <code>&lt;input&gt;</code> + <code>&lt;label&gt;</code> + <code>&lt;button&gt;</code> combo is more flexible, accessible, and standards-compliant.</p>
<p><strong>Why this question matters in interviews:</strong> it tests whether you know HTML&rsquo;s history of evolution &mdash; that obsolete elements exist, that the spec deprecates and removes things, and that &ldquo;it&rsquo;s in HTML&rdquo; doesn&rsquo;t mean &ldquo;use it.&rdquo;</p>
<p><strong>Other obsolete elements you should never use:</strong></p>
<table>
  <tr><th>Obsolete element</th><th>Modern replacement</th></tr>
  <tr><td><code>&lt;isindex&gt;</code></td><td><code>&lt;input type="search"&gt;</code> in a form</td></tr>
  <tr><td><code>&lt;applet&gt;</code></td><td><code>&lt;object&gt;</code> or modern alternatives (Wasm, JS)</td></tr>
  <tr><td><code>&lt;basefont&gt;</code></td><td>CSS</td></tr>
  <tr><td><code>&lt;big&gt;</code>, <code>&lt;tt&gt;</code>, <code>&lt;font&gt;</code>, <code>&lt;center&gt;</code></td><td>CSS</td></tr>
  <tr><td><code>&lt;frame&gt;</code>, <code>&lt;frameset&gt;</code>, <code>&lt;noframes&gt;</code></td><td><code>&lt;iframe&gt;</code> + CSS layout</td></tr>
  <tr><td><code>&lt;keygen&gt;</code></td><td>Web Crypto API or WebAuthn</td></tr>
  <tr><td><code>&lt;marquee&gt;</code>, <code>&lt;blink&gt;</code></td><td>CSS animations (sparingly)</td></tr>
</table>
<p>Browsers retain partial support for some of these for legacy compatibility, but the spec doesn&rsquo;t require it &mdash; rendering can disappear at any point. The MDN compatibility table is the authoritative reference.</p>
'''

ANSWERS[19] = r'''
<p><code>&lt;progress&gt;</code> and <code>&lt;meter&gt;</code> both render gauge-like indicators, but they represent different things &mdash; <strong>progress toward completion</strong> vs <strong>a measurement within a range</strong>. Choosing the right one matters for accessibility and semantics.</p>
<table>
  <tr><th></th><th><code>&lt;progress&gt;</code></th><th><code>&lt;meter&gt;</code></th></tr>
  <tr><td>Represents</td><td>Task progress changing over time</td><td>A static measurement</td></tr>
  <tr><td>Indeterminate state</td><td>Yes &mdash; omit <code>value</code></td><td>No &mdash; always has a value</td></tr>
  <tr><td>Color zones</td><td>None &mdash; just a fill</td><td><code>low</code>, <code>high</code>, <code>optimum</code> regions</td></tr>
  <tr><td>Examples</td><td>File upload, page load, form-step indicator</td><td>Disk usage, score, quiz result, battery level</td></tr>
</table>
<p><strong><code>&lt;progress&gt;</code> examples:</strong></p>
<pre><code>&lt;!-- Determinate — known progress --&gt;
&lt;label for="upload"&gt;Uploading:&lt;/label&gt;
&lt;progress id="upload" value="42" max="100"&gt;42%&lt;/progress&gt;

&lt;!-- Indeterminate — unknown duration --&gt;
&lt;progress&gt;Loading...&lt;/progress&gt;</code></pre>
<p>Update via JS: <code>document.querySelector("progress").value = 50;</code>. The fallback text inside the tags shows in browsers without progress support (none in 2026, but assistive tech may read it).</p>
<p><strong><code>&lt;meter&gt;</code> with full attributes:</strong></p>
<pre><code>&lt;label for="disk"&gt;Disk usage:&lt;/label&gt;
&lt;meter id="disk"
       value="0.85"
       min="0"
       max="1"
       low="0.5"
       high="0.8"
       optimum="0.3"&gt;
  85% used
&lt;/meter&gt;</code></pre>
<p>The browser colors the meter based on which zone the value falls in:</p>
<ul>
  <li>Value in the optimum zone &rarr; green (good).</li>
  <li>Value in the &ldquo;safe but not optimal&rdquo; zone &rarr; yellow.</li>
  <li>Value in the danger zone (above <code>high</code> when <code>optimum</code> is low) &rarr; red.</li>
</ul>
<p>So &ldquo;disk 85% used&rdquo; renders red because the optimum is low (empty); &ldquo;test score 85%&rdquo; with high optimum renders green.</p>
<p><strong>Styling:</strong> the easy modern way is <code>accent-color</code>:</p>
<pre><code>progress { accent-color: #4caf50; }</code></pre>
<p>For deeper control, the underlying pseudo-elements differ by browser (<code>::-webkit-progress-bar</code>, <code>::-webkit-progress-value</code>, <code>::-moz-progress-bar</code>) &mdash; complex but doable.</p>
<p><strong>Accessibility:</strong> both elements are exposed to screen readers as appropriate roles. Pair with a visible <code>&lt;label for&gt;</code> or use <code>aria-label</code>. For progress that&rsquo;s critical to user understanding (file upload completion, multi-step forms), also announce major milestones via an <code>aria-live</code> region &mdash; the visual gauge alone can be missed.</p>
<p><strong>The decision rule:</strong> &ldquo;is this value <em>becoming</em> something?&rdquo; (uploading, building, loading) &rarr; <code>&lt;progress&gt;</code>. &ldquo;Is this a fixed measurement?&rdquo; &rarr; <code>&lt;meter&gt;</code>.</p>
'''

ANSWERS[20] = r'''
<p><code>&lt;keygen&gt;</code> was an obsolete HTML form element that generated a public/private key pair when a form was submitted &mdash; the public key went to the server, the private key stayed in the browser&rsquo;s key store. It was used for client certificate enrollment in early-2000s enterprise PKIs.</p>
<pre><code>&lt;!-- Historical use (obsolete, do NOT use) --&gt;
&lt;form action="/enroll" method="post"&gt;
  &lt;keygen name="userKey" challenge="random_value" keytype="RSA"&gt;
  &lt;button type="submit"&gt;Generate certificate&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Why it was deprecated and removed:</strong></p>
<ul>
  <li><strong>Inconsistent across browsers</strong> &mdash; key formats, UI, and key-store handling differed wildly.</li>
  <li><strong>Cryptographic limits</strong> &mdash; locked to specific algorithms (RSA), no curve support, no flexibility.</li>
  <li><strong>Dead UX</strong> &mdash; users were confused by &ldquo;generate certificate&rdquo; prompts.</li>
  <li><strong>Removed from HTML5</strong> circa 2017; Chrome dropped it in 57 (2017), Firefox in 69 (2019).</li>
</ul>
<p><strong>Modern replacement: Web Crypto API</strong> for keys, WebAuthn for authentication.</p>
<pre><code>// Generate an ECDSA key pair in the browser
const keyPair = await crypto.subtle.generateKey(
  {
    name: "ECDSA",
    namedCurve: "P-256",
  },
  true,                                       // exportable
  ["sign", "verify"],
);

// Export public key for server
const publicKey = await crypto.subtle.exportKey("spki", keyPair.publicKey);
const publicKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(publicKey)));

// Send public key to server with form
const formData = new FormData();
formData.append("publicKey", publicKeyBase64);
await fetch("/enroll", { method: "POST", body: formData });

// Store private key in IndexedDB or sign challenges client-side</code></pre>
<p><strong>For passwordless authentication, use WebAuthn</strong> (the standard underlying Passkeys, FIDO2, Windows Hello, Touch ID):</p>
<pre><code>// Register a new credential
const credential = await navigator.credentials.create({
  publicKey: {
    challenge:        new Uint8Array(serverChallenge),
    rp:               { name: "Acme Inc", id: "acme.com" },
    user:             { id: userIdBytes, name: "alice@acme.com", displayName: "Alice" },
    pubKeyCredParams: [{ type: "public-key", alg: -7 }],   // ES256
    authenticatorSelection: { userVerification: "required" },
  },
});

// Send credential to server for verification
await fetch("/auth/register", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ id: credential.id, attestation: credential.response }),
});</code></pre>
<p><strong>WebAuthn benefits over <code>&lt;keygen&gt;</code>:</strong></p>
<ul>
  <li>Hardware-backed keys (Secure Enclave, TPM, security keys).</li>
  <li>Phishing-resistant by design (origin-bound credentials).</li>
  <li>Modern algorithms (Ed25519, ECDSA, RSA).</li>
  <li>Rich UX (biometric prompts, security key flows).</li>
  <li>Cross-device passkey sync via cloud (Apple iCloud Keychain, Google Password Manager, 1Password).</li>
</ul>
<p>By 2026, all major sites and OSes support passkeys. The <code>&lt;keygen&gt;</code> use case is obsolete &mdash; modern browsers don&rsquo;t even render the element.</p>
'''

ANSWERS[21] = r'''
<p>HTML5 added a comprehensive set of validation attributes that browsers enforce automatically &mdash; users see a tooltip and submission is blocked when invalid. No JavaScript required for most checks.</p>
<pre><code>&lt;form action="/signup" method="post"&gt;
  &lt;label for="email"&gt;Email&lt;/label&gt;
  &lt;input type="email"
         id="email"
         name="email"
         required
         autocomplete="email"&gt;

  &lt;label for="username"&gt;Username (3-20 chars)&lt;/label&gt;
  &lt;input type="text"
         id="username"
         name="username"
         pattern="[A-Za-z0-9_]{3,20}"
         minlength="3"
         maxlength="20"
         required
         title="3 to 20 letters, digits, or underscores"&gt;

  &lt;label for="age"&gt;Age (must be 18+)&lt;/label&gt;
  &lt;input type="number"
         id="age"
         name="age"
         min="18"
         max="120"
         required&gt;

  &lt;label for="bio"&gt;Bio (max 200 chars)&lt;/label&gt;
  &lt;textarea id="bio" name="bio" maxlength="200"&gt;&lt;/textarea&gt;

  &lt;button type="submit"&gt;Sign up&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Validation attributes:</strong></p>
<table>
  <tr><th>Attribute</th><th>Effect</th></tr>
  <tr><td><code>required</code></td><td>Field must not be empty</td></tr>
  <tr><td><code>type="email"</code> / <code>url</code></td><td>Format check</td></tr>
  <tr><td><code>pattern="regex"</code></td><td>Custom regex match</td></tr>
  <tr><td><code>minlength</code> / <code>maxlength</code></td><td>String length bounds</td></tr>
  <tr><td><code>min</code> / <code>max</code></td><td>Numeric/date bounds</td></tr>
  <tr><td><code>step</code></td><td>Increment for number/date inputs</td></tr>
</table>
<p><strong>Style invalid fields with CSS pseudo-classes:</strong></p>
<pre><code>input:invalid:not(:placeholder-shown) {
  border-color: #c00;
}
input:valid {
  border-color: #0a0;
}
input:user-invalid {     /* only after user interaction (newer) */
  border-color: #c00;
}</code></pre>
<p>The <code>:user-invalid</code> pseudo-class (Chromium 119+, Firefox 88+) avoids showing red borders before the user has typed anything &mdash; better UX than <code>:invalid</code>.</p>
<p><strong>The Constraint Validation API</strong> for programmatic control:</p>
<pre><code>const input = document.querySelector("#username");

// Check validity
input.checkValidity();              // true / false
input.validity.valueMissing;        // true if required and empty
input.validity.patternMismatch;     // true if pattern fails
input.validity.tooShort;            // true if minlength fails

// Custom error message
if (someCondition) {
  input.setCustomValidity("Username already taken");
} else {
  input.setCustomValidity("");      // clears the error
}

// Trigger native UI for current errors
input.reportValidity();</code></pre>
<p><strong>Customizing the validation UI:</strong> by default, browsers show their own tooltip on submit. To replace this with custom UI, listen for the <code>invalid</code> event, call <code>preventDefault</code> on each invalid field, and render your own messages. The <code>:invalid</code> styles still apply for visual feedback.</p>
<p><strong>Always re-validate server-side.</strong> Client-side validation is UX, not security &mdash; users can disable JavaScript, modify the DOM in DevTools, or send raw HTTP requests. Server validation is the actual gate; client validation just makes the experience smoother. Modern stacks share schemas (Zod, Yup) between client and server so the rules don&rsquo;t drift.</p>
'''

ANSWERS[22] = r'''
<p>The <code>&lt;wbr&gt;</code> element marks a <strong>word break opportunity</strong> &mdash; a place where the browser may break a long, unbreakable string onto a new line if needed. It doesn&rsquo;t force a break; it just permits one.</p>
<pre><code>&lt;p&gt;
  Visit our site at https://example.com/very-long-path/&lt;wbr&gt;and-more-text/&lt;wbr&gt;continuing-here.html
&lt;/p&gt;

&lt;p&gt;
  Run npm install some-very-long-package-&lt;wbr&gt;name-that-might-overflow.
&lt;/p&gt;

&lt;code&gt;
  ABCDEFGHIJK&lt;wbr&gt;LMNOPQRSTUV&lt;wbr&gt;WXYZ
&lt;/code&gt;</code></pre>
<p><strong>What problem it solves:</strong> long strings without spaces &mdash; URLs, code, hex colors, German compound words, IDs, hashes &mdash; can overflow their container or force horizontal scrolling. <code>&lt;wbr&gt;</code> tells the browser &ldquo;here is a clean place to wrap, if needed.&rdquo;</p>
<p><strong>How it differs from related concepts:</strong></p>
<table>
  <tr><th>Mechanism</th><th>Behavior</th></tr>
  <tr><td><code>&lt;wbr&gt;</code></td><td>Optional break opportunity; only used if needed</td></tr>
  <tr><td><code>&lt;br&gt;</code></td><td>Forced line break; always breaks</td></tr>
  <tr><td><code>&amp;shy;</code> (soft hyphen)</td><td>Optional break with hyphen displayed if used</td></tr>
  <tr><td>CSS <code>word-break: break-all</code></td><td>Break anywhere &mdash; aggressive</td></tr>
  <tr><td>CSS <code>overflow-wrap: break-word</code></td><td>Break only when no other option fits</td></tr>
  <tr><td>CSS <code>hyphens: auto</code></td><td>Browser hyphenates with <code>lang</code> dictionary</td></tr>
</table>
<p><strong>Use cases for <code>&lt;wbr&gt;</code>:</strong></p>
<ul>
  <li><strong>URLs in body text</strong> &mdash; especially long pathnames or query strings.</li>
  <li><strong>Code snippets</strong> in documentation where line length is constrained.</li>
  <li><strong>Long compound words</strong> in German or technical jargon.</li>
  <li><strong>Long file paths</strong> like <code>/Users/jdoe/projects/&lt;wbr&gt;quarterly-report-2026-final-v3.docx</code>.</li>
</ul>
<p><strong>Modern preference:</strong> CSS often handles this better than scattering <code>&lt;wbr&gt;</code> through content. For URLs and similar:</p>
<pre><code>.url {
  word-break: break-word;     /* allow breaks at "words" first */
  overflow-wrap: anywhere;    /* fall back to anywhere */
}</code></pre>
<p>This avoids manually finding break points in URLs and keeps content readable. <code>&lt;wbr&gt;</code> is most useful when you want <em>specific</em> break points (semantic boundaries in a long string) rather than &ldquo;break wherever needed.&rdquo; A long compound term like &ldquo;<code>microservices&lt;wbr&gt;orchestration&lt;wbr&gt;framework</code>&rdquo; reads better when broken at meaningful points.</p>
<p><strong>Selection and copy behavior:</strong> <code>&lt;wbr&gt;</code> is a zero-width element &mdash; it doesn&rsquo;t affect text selection, search-in-page, or text copied to the clipboard (the copied string has no embedded character at the wbr position).</p>
<p><strong>Accessibility:</strong> screen readers ignore <code>&lt;wbr&gt;</code>. It&rsquo;s purely a visual/typographic hint to the browser.</p>
'''

ANSWERS[23] = r'''
<p>Combining <code>&lt;template&gt;</code> with Shadow DOM is the canonical pattern for creating encapsulated Web Components &mdash; the template defines the component&rsquo;s internal markup once, and each instance clones it into its shadow root for isolation.</p>
<pre><code>&lt;!-- Template defined once in the document --&gt;
&lt;template id="profile-card-template"&gt;
  &lt;style&gt;
    :host {
      display: inline-block;
      border: 1px solid var(--card-border, #ccc);
      border-radius: 8px;
      padding: 1em;
      max-width: 320px;
    }
    .name { font-size: 1.2em; font-weight: 600; }
    .role { color: #666; }
    img    { border-radius: 50%; }
    ::slotted(p) { margin: 0.5em 0; }
  &lt;/style&gt;
  &lt;img class="avatar" src="" alt=""&gt;
  &lt;div class="name"&gt;&lt;/div&gt;
  &lt;div class="role"&gt;&lt;/div&gt;
  &lt;slot&gt;&lt;/slot&gt;     &lt;!-- Light DOM children projected here --&gt;
&lt;/template&gt;

&lt;script&gt;
class ProfileCard extends HTMLElement {
  static get observedAttributes() { return ["name", "role", "avatar"]; }

  connectedCallback() {
    if (!this.shadowRoot) {
      // Clone template content into the shadow root once
      const template = document.getElementById("profile-card-template");
      this.attachShadow({ mode: "open" })
          .appendChild(template.content.cloneNode(true));
      this._refresh();
    }
  }

  attributeChangedCallback() {
    if (this.shadowRoot) this._refresh();
  }

  _refresh() {
    const sr = this.shadowRoot;
    sr.querySelector(".name").textContent = this.getAttribute("name") || "Anonymous";
    sr.querySelector(".role").textContent = this.getAttribute("role") || "";
    const img = sr.querySelector(".avatar");
    img.src = this.getAttribute("avatar") || "";
    img.alt = this.getAttribute("name") || "";
  }
}
customElements.define("profile-card", ProfileCard);
&lt;/script&gt;

&lt;!-- Use the component anywhere --&gt;
&lt;profile-card name="Jane Smith"
              role="Senior Engineer"
              avatar="/avatars/jane.jpg"&gt;
  &lt;p&gt;Specializes in distributed systems and observability.&lt;/p&gt;
&lt;/profile-card&gt;</code></pre>
<p><strong>Why this pattern works well:</strong></p>
<ul>
  <li><strong>Template is parsed once</strong> &mdash; cloning is cheap, faster than parsing HTML strings on every instance.</li>
  <li><strong>Shadow DOM isolates styles</strong> &mdash; the <code>.name</code> rule only matches inside this component, never colliding with page styles.</li>
  <li><strong>Slot enables composition</strong> &mdash; consumers put any markup as children; the component decides where to render it.</li>
  <li><strong>CSS custom properties cross the shadow boundary</strong> &mdash; <code>--card-border</code> in the template is set from outside CSS for theming.</li>
</ul>
<p><strong>Declarative Shadow DOM</strong> (2024+) lets you ship the shadow tree in HTML without JavaScript, perfect for SSR:</p>
<pre><code>&lt;profile-card name="Jane Smith"&gt;
  &lt;template shadowrootmode="open"&gt;
    &lt;style&gt;...&lt;/style&gt;
    &lt;img class="avatar" src="..."&gt;
    &lt;div class="name"&gt;Jane Smith&lt;/div&gt;
    &lt;slot&gt;&lt;/slot&gt;
  &lt;/template&gt;
  &lt;p&gt;Bio content&lt;/p&gt;
&lt;/profile-card&gt;</code></pre>
<p>The browser inflates the <code>&lt;template&gt;</code> with <code>shadowrootmode</code> directly into a shadow tree at parse time &mdash; the component has visible, styled output before any script runs.</p>
<p><strong>Lit, FAST, Stencil</strong> wrap this pattern with reactive bindings, TypeScript decorators, and ergonomic APIs. For straightforward components, the platform primitives shown here are entirely sufficient and ship zero runtime overhead. The pattern underlies every native HTML element &mdash; <code>&lt;input&gt;</code>, <code>&lt;video&gt;</code>, <code>&lt;details&gt;</code> all use shadow DOM internally for their controls.</p>
'''

ANSWERS[24] = r'''
<p>The <code>&lt;picture&gt;</code> element is the most powerful tool for responsive images &mdash; it solves three problems that <code>&lt;img srcset&gt;</code> alone can&rsquo;t address:</p>
<ol>
  <li><strong>Art direction</strong> &mdash; serve a different crop or composition based on viewport size.</li>
  <li><strong>Format negotiation</strong> &mdash; serve modern formats (AVIF, WebP) to browsers that support them, with JPEG fallback.</li>
  <li><strong>Conditional source</strong> &mdash; switch images based on color scheme, motion preferences, or other media queries.</li>
</ol>
<pre><code>&lt;picture&gt;
  &lt;!-- Mobile: cropped square version, in modern formats --&gt;
  &lt;source media="(max-width: 600px)"
          srcset="hero-mobile.avif"
          type="image/avif"&gt;
  &lt;source media="(max-width: 600px)"
          srcset="hero-mobile.webp"
          type="image/webp"&gt;
  &lt;source media="(max-width: 600px)"
          srcset="hero-mobile.jpg"&gt;

  &lt;!-- Desktop: wide landscape, modern formats --&gt;
  &lt;source srcset="hero-wide.avif" type="image/avif"&gt;
  &lt;source srcset="hero-wide.webp" type="image/webp"&gt;

  &lt;!-- Universal fallback --&gt;
  &lt;img src="hero-wide.jpg"
       alt="Coastline at sunrise"
       width="1600"
       height="900"
       loading="eager"
       fetchpriority="high"&gt;
&lt;/picture&gt;</code></pre>
<p><strong>Browser selection algorithm:</strong></p>
<ol>
  <li>Walk <code>&lt;source&gt;</code> elements top to bottom.</li>
  <li>Skip any whose <code>media</code> doesn&rsquo;t match the current viewport.</li>
  <li>Skip any whose <code>type</code> the browser can&rsquo;t decode.</li>
  <li>Use the first source that passes; if no <code>&lt;source&gt;</code> qualifies, fall back to <code>&lt;img&gt;</code>.</li>
  <li>Within the chosen source, <code>srcset</code> + <code>sizes</code> + DPR resolves the exact file.</li>
</ol>
<p><strong>Combining with srcset for resolution:</strong></p>
<pre><code>&lt;picture&gt;
  &lt;source media="(min-width: 1200px)"
          srcset="hero-wide-800.avif 800w,
                  hero-wide-1600.avif 1600w,
                  hero-wide-3200.avif 3200w"
          sizes="100vw"
          type="image/avif"&gt;
  &lt;img src="hero.jpg" alt="..." width="1600" height="900"&gt;
&lt;/picture&gt;</code></pre>
<p><strong>Dark-mode variants</strong> via media query:</p>
<pre><code>&lt;picture&gt;
  &lt;source media="(prefers-color-scheme: dark)"
          srcset="logo-dark.svg"&gt;
  &lt;img src="logo-light.svg" alt="Acme" width="200" height="60"&gt;
&lt;/picture&gt;</code></pre>
<p><strong>Performance considerations:</strong></p>
<ul>
  <li><strong>Width and height</strong> on the fallback <code>&lt;img&gt;</code> establish the aspect ratio &mdash; eliminates layout shift even when picture chooses a different source.</li>
  <li><strong>Order matters</strong> &mdash; AVIF (smallest) before WebP before JPEG.</li>
  <li><strong>fetchpriority="high"</strong> on LCP images.</li>
  <li><strong>Preload</strong> the LCP image with the same negotiation: <code>&lt;link rel="preload" as="image" imagesrcset="..." imagesizes="..."&gt;</code>.</li>
  <li><strong>Don&rsquo;t over-engineer</strong> &mdash; for product thumbnails or content images that don&rsquo;t need art direction, plain <code>&lt;img srcset&gt;</code> is enough and simpler.</li>
</ul>
<p><strong>Image CDNs</strong> (Cloudflare Images, Imgix, Cloudinary, Vercel) generate responsive variants on-the-fly and emit the right <code>&lt;picture&gt;</code> markup automatically. For most teams, this is the right level of abstraction &mdash; you write one <code>&lt;img&gt;</code> tag, the CDN handles negotiation, format selection, and caching.</p>
'''

ANSWERS[25] = r'''
<p><code>&lt;fieldset&gt;</code> groups related form controls together; <code>&lt;legend&gt;</code> labels the group. Together they create a semantic boundary that benefits accessibility, organization, and form-state management.</p>
<pre><code>&lt;form&gt;
  &lt;fieldset&gt;
    &lt;legend&gt;Account Details&lt;/legend&gt;

    &lt;label for="email"&gt;Email&lt;/label&gt;
    &lt;input type="email" id="email" name="email" required&gt;

    &lt;label for="password"&gt;Password&lt;/label&gt;
    &lt;input type="password" id="password" name="password" required&gt;
  &lt;/fieldset&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Shipping Preference&lt;/legend&gt;

    &lt;label&gt;
      &lt;input type="radio" name="shipping" value="standard" checked&gt;
      Standard (5-7 days)
    &lt;/label&gt;
    &lt;label&gt;
      &lt;input type="radio" name="shipping" value="express"&gt;
      Express (2-3 days)
    &lt;/label&gt;
    &lt;label&gt;
      &lt;input type="radio" name="shipping" value="overnight"&gt;
      Overnight
    &lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;button type="submit"&gt;Continue&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Why fieldset + legend matter:</strong></p>
<ul>
  <li><strong>Critical for radio groups and checkboxes</strong> &mdash; screen readers announce the legend when the user focuses on any radio button in the group, providing context (&ldquo;Shipping Preference, Standard, radio button, 1 of 3&rdquo;). Without a fieldset, the user only hears the individual option labels and may miss what question they&rsquo;re answering.</li>
  <li><strong>Logical grouping</strong> &mdash; visual users see a border around related fields (the default browser styling).</li>
  <li><strong>Bulk disable</strong> &mdash; <code>&lt;fieldset disabled&gt;</code> disables every input inside, including in nested fieldsets.</li>
  <li><strong>Form sections</strong> in long forms become navigable for assistive tech.</li>
</ul>
<p><strong>Bulk-disable example:</strong></p>
<pre><code>&lt;fieldset disabled&gt;
  &lt;legend&gt;Personal Info&lt;/legend&gt;
  &lt;input type="text" name="firstName"&gt;     &lt;!-- disabled --&gt;
  &lt;input type="text" name="lastName"&gt;      &lt;!-- disabled --&gt;
  &lt;select name="country"&gt;...&lt;/select&gt;       &lt;!-- disabled --&gt;
&lt;/fieldset&gt;</code></pre>
<p>Useful for &ldquo;loading&rdquo; states (disable all inputs while the form submits) or step-locked wizards (current step active, others disabled).</p>
<p><strong>Styling:</strong> default browser styles are an inset border with the legend overlaid on it. To remove or restyle:</p>
<pre><code>fieldset {
  border: none;
  padding: 0;
  margin: 0 0 1.5em 0;
}
legend {
  font-weight: 600;
  font-size: 1.1em;
  margin-bottom: 0.5em;
  padding: 0;
}</code></pre>
<p><strong>The legend pseudo-element trick:</strong> the legend visually overlays the top border of the fieldset by default &mdash; a unique typographic position that&rsquo;s otherwise hard to achieve. Some designs lean into this; modern designs typically remove the border entirely.</p>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Skipping fieldset for radio/checkbox groups &mdash; major accessibility regression.</li>
  <li>Using <code>&lt;p&gt;</code> or <code>&lt;h3&gt;</code> instead of <code>&lt;legend&gt;</code> &mdash; loses the semantic association.</li>
  <li>Wrapping non-form content in fieldset for visual styling &mdash; misuse.</li>
  <li>Multiple legends per fieldset &mdash; only the first counts; rest are ignored.</li>
</ul>
<p>The fieldset/legend pattern is one of HTML&rsquo;s oldest accessibility wins &mdash; it&rsquo;s been required reading in WCAG since 2.0. Skipping it is one of the most common audit findings on form-heavy sites.</p>
'''

ANSWERS[26] = r'''
<p>The <code>&lt;datalist&gt;</code> element provides browser-native autocomplete suggestions for text inputs. Unlike <code>&lt;select&gt;</code>, it allows arbitrary user input alongside suggestions &mdash; ideal for "type-or-pick" interactions like city pickers, search history, or tag autocomplete.</p>
<pre><code>&lt;label for="lang"&gt;Programming language:&lt;/label&gt;
&lt;input list="languages" id="lang" name="language" autocomplete="off"&gt;

&lt;datalist id="languages"&gt;
  &lt;option value="JavaScript"&gt;
  &lt;option value="TypeScript"&gt;
  &lt;option value="Python"&gt;
  &lt;option value="Rust"&gt;
  &lt;option value="Go"&gt;
&lt;/datalist&gt;</code></pre>
<p><strong>Mechanism:</strong> the input's <code>list</code> attribute references a <code>&lt;datalist&gt;</code> by ID. Browsers filter options as the user types and surface matches in a dropdown. The control remains a free-text field &mdash; users can submit values not in the list.</p>
<p><strong>Capabilities and limits:</strong></p>
<ul>
  <li>Works with most text-style inputs (<code>text</code>, <code>search</code>, <code>email</code>, <code>url</code>, <code>tel</code>) and even <code>date</code>, <code>time</code>, <code>number</code>, <code>range</code> (where supported).</li>
  <li>Filtering algorithm is browser-defined &mdash; usually substring or prefix; not customizable.</li>
  <li>Cannot show rich content (only plain text in options); cannot trigger fetch on each keystroke.</li>
  <li>Text content between option tags becomes the visible suggestion label, while <code>value</code> is what gets submitted: <code>&lt;option value="JFK"&gt;John F. Kennedy&lt;/option&gt;</code>.</li>
  <li>Limited keyboard a11y &mdash; some browsers don't announce filtered counts.</li>
</ul>
<p><strong>Dynamic population</strong> (server-driven autocomplete with debouncing):</p>
<pre><code>const input = document.querySelector('#search');
const list = document.querySelector('#suggestions');

let timer;
input.addEventListener('input', () =&gt; {
  clearTimeout(timer);
  timer = setTimeout(async () =&gt; {
    const res = await fetch(`/api/suggest?q=${encodeURIComponent(input.value)}`);
    const items = await res.json();
    list.innerHTML = items.map(i =&gt; `&lt;option value="${i}"&gt;`).join('');
  }, 200);
});</code></pre>
<p><strong>When to choose datalist vs alternatives:</strong> use datalist for simple, finite suggestion sets where free-text input is allowed. For richer combobox behavior &mdash; remote search with debouncing, custom rendering, async loading states, accessibility callouts &mdash; reach for a library (Headless UI Combobox, Downshift, React Aria) or build with ARIA's <code>role="combobox"</code> pattern. Datalist is great for quick wins; full comboboxes require more scaffolding but offer significantly better UX for power-user inputs.</p>
'''

ANSWERS[27] = r'''
<p><code>&lt;nav&gt;</code> and <code>&lt;aside&gt;</code> are both HTML5 sectioning elements that create accessibility landmarks &mdash; but they signal fundamentally different intent. Confusing them is a common semantic mistake that affects screen reader navigation.</p>
<p><strong><code>&lt;nav&gt;</code> &mdash; major navigation:</strong></p>
<ul>
  <li>Marks a section containing significant navigation links: primary nav, in-page table of contents, breadcrumbs, footer site map, pagination.</li>
  <li>Maps to ARIA <code>role="navigation"</code> automatically.</li>
  <li>Should not wrap incidental link clusters (e.g., a "Read more" link, social share icons, related-article tiles).</li>
  <li>Multiple <code>&lt;nav&gt;</code>s per page are valid; distinguish them with <code>aria-label</code> ("Main", "Footer", "Breadcrumb").</li>
</ul>
<p><strong><code>&lt;aside&gt;</code> &mdash; tangentially related content:</strong></p>
<ul>
  <li>Content related to but separable from the main flow: sidebars, pull quotes, advertising blocks, "related articles" widgets, author bios next to articles.</li>
  <li>Maps to ARIA <code>role="complementary"</code>.</li>
  <li>Removing the aside should not break the main content's meaning.</li>
  <li>Inside an <code>&lt;article&gt;</code>, the aside relates to that article specifically; outside articles, it relates to the whole page.</li>
</ul>
<pre><code>&lt;body&gt;
  &lt;header&gt;
    &lt;nav aria-label="Main"&gt;            &lt;!-- primary site nav --&gt;
      &lt;ul&gt;&lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;...&lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/header&gt;

  &lt;main&gt;
    &lt;article&gt;
      &lt;h1&gt;The Article&lt;/h1&gt;
      &lt;nav aria-label="Table of contents"&gt;     &lt;!-- TOC nav --&gt;
        &lt;ol&gt;&lt;li&gt;&lt;a href="#intro"&gt;Intro&lt;/a&gt;&lt;/li&gt;...&lt;/ol&gt;
      &lt;/nav&gt;
      &lt;p&gt;...&lt;/p&gt;
      &lt;aside&gt;                                   &lt;!-- author bio for THIS article --&gt;
        &lt;h3&gt;About the author&lt;/h3&gt;
        &lt;p&gt;Jane writes about...&lt;/p&gt;
      &lt;/aside&gt;
    &lt;/article&gt;

    &lt;aside aria-label="Related"&gt;                 &lt;!-- page-level sidebar --&gt;
      &lt;h3&gt;You might like&lt;/h3&gt;
      &lt;ul&gt;&lt;li&gt;&lt;a href="/x"&gt;Other article&lt;/a&gt;&lt;/li&gt;&lt;/ul&gt;
    &lt;/aside&gt;
  &lt;/main&gt;
&lt;/body&gt;</code></pre>
<p><strong>Why this matters operationally:</strong> screen reader users navigate by landmark using shortcut keys (e.g., NVDA's <kbd>D</kbd> for landmarks, JAWS's <kbd>R</kbd>). When you mark every footer-link cluster as <code>&lt;nav&gt;</code>, the landmark list becomes noisy and useful navs get buried. When you misuse <code>&lt;aside&gt;</code> for primary content, that content gets demoted to "complementary" and may be skipped entirely. Test with a screen reader's landmark navigation &mdash; if your structure feels right there, it's probably correct semantically.</p>
'''

ANSWERS[28] = r'''
<p>Inline SVG embeds vector graphics directly in the HTML document, where they become first-class DOM elements &mdash; styleable with CSS, scriptable with JavaScript, accessible to screen readers, and indexable by search engines.</p>
<pre><code>&lt;svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 100 100"
     width="100"
     height="100"
     role="img"
     aria-labelledby="logo-title logo-desc"&gt;
  &lt;title id="logo-title"&gt;Acme Corp logo&lt;/title&gt;
  &lt;desc id="logo-desc"&gt;A blue circle with a white star in the center&lt;/desc&gt;

  &lt;circle cx="50" cy="50" r="45" fill="#0055aa"/&gt;
  &lt;polygon points="50,15 60,40 87,40 65,57 73,82 50,67 27,82 35,57 13,40 40,40"
           fill="white"/&gt;
&lt;/svg&gt;</code></pre>
<p><strong>The viewBox is the heart of SVG scaling:</strong> <code>viewBox="0 0 100 100"</code> defines the internal coordinate system. The image scales to whatever <code>width</code>/<code>height</code> (or CSS dimensions) you give it &mdash; perfectly crisp at any resolution. Set <code>width</code>/<code>height</code> to <code>100%</code> in CSS for fully fluid sizing.</p>
<p><strong>Inline vs <code>&lt;img src="x.svg"&gt;</code> &mdash; key differences:</strong></p>
<table>
  <tr><th></th><th>Inline SVG</th><th>img/object/embed</th></tr>
  <tr><td>CSS targeting</td><td>Yes &mdash; style every path</td><td>Only the wrapping element</td></tr>
  <tr><td>JS interaction</td><td>Yes &mdash; addEventListener on shapes</td><td>Limited; need <code>&lt;object&gt;</code> with same-origin</td></tr>
  <tr><td>Caching</td><td>Cached with the HTML</td><td>Cached separately (good for repeated icons)</td></tr>
  <tr><td>Page weight</td><td>Inflates HTML payload</td><td>Lazy-loadable, parallelizable</td></tr>
  <tr><td>Accessibility</td><td><code>&lt;title&gt;</code> + <code>aria-labelledby</code></td><td><code>alt</code> attribute on img</td></tr>
</table>
<p><strong>Accessibility for inline SVG:</strong></p>
<ul>
  <li>For meaningful icons, add <code>role="img"</code> and a <code>&lt;title&gt;</code> child; reference it via <code>aria-labelledby</code>.</li>
  <li>For decorative icons (paired with adjacent text), use <code>aria-hidden="true"</code> &mdash; double-announcement is worse than nothing.</li>
  <li><code>&lt;desc&gt;</code> provides extended descriptions for complex graphics like charts.</li>
</ul>
<p><strong>Optimization workflow:</strong> design tools (Figma, Illustrator) export verbose SVG with metadata, hidden layers, and unnecessary precision. Run output through <strong>SVGO</strong> (CLI or build plugin) &mdash; it routinely reduces file size 60-80% without visual change. For icon systems, build a single sprite (<code>&lt;symbol&gt;</code> + <code>&lt;use&gt;</code>) or use a build tool (vite-plugin-svg-icons, SVGR) to import each SVG as a component.</p>
'''

ANSWERS[29] = r'''
<p>The <code>&lt;mark&gt;</code> element marks text as <em>relevant in the current context</em> &mdash; not just visually highlighted, but semantically called out as significant for the user's reading purpose. Browsers default-style it with a yellow background, but the meaning runs deeper than the styling.</p>
<pre><code>&lt;p&gt;Search results for &ldquo;&lt;mark&gt;quantum&lt;/mark&gt;&rdquo;:&lt;/p&gt;

&lt;article&gt;
  &lt;p&gt;In modern physics, &lt;mark&gt;quantum&lt;/mark&gt; mechanics describes
  the behavior of matter at atomic scales. The principle of
  &lt;mark&gt;quantum&lt;/mark&gt; superposition states...&lt;/p&gt;
&lt;/article&gt;</code></pre>
<p><strong>Canonical use cases:</strong></p>
<ul>
  <li><strong>Search-result highlighting</strong> &mdash; the matched query terms in returned text.</li>
  <li><strong>Reference annotations</strong> &mdash; quoting a passage and highlighting the part being discussed.</li>
  <li><strong>Recently-changed content</strong> &mdash; what's new since the user last visited.</li>
  <li><strong>Currency / relevance markers</strong> &mdash; highlighting "due today" items in a calendar view.</li>
</ul>
<p><strong>The semantic contrast matters:</strong></p>
<table>
  <tr><th>Tag</th><th>Means</th></tr>
  <tr><td><code>&lt;mark&gt;</code></td><td>Relevant in the current reading context</td></tr>
  <tr><td><code>&lt;strong&gt;</code></td><td>Inherently important / serious / urgent</td></tr>
  <tr><td><code>&lt;em&gt;</code></td><td>Stress emphasis on this word, changing meaning</td></tr>
  <tr><td><code>&lt;b&gt;</code></td><td>Stylistic offset only, no semantic weight</td></tr>
</table>
<p>"Search results for &lt;b&gt;quantum&lt;/b&gt;" is wrong &mdash; <code>&lt;b&gt;</code> implies stylistic offset, not contextual relevance. "Search results for &lt;strong&gt;quantum&lt;/strong&gt;" is also wrong &mdash; the term isn't intrinsically important; it's just relevant to <em>this user's search</em>.</p>
<p><strong>Screen reader behavior</strong> varies. NVDA and JAWS by default don't announce <code>&lt;mark&gt;</code> distinctly &mdash; the semantic value is more for visual users and search engines. To force announcement of "highlighted" text, layer ARIA: <code>&lt;mark role="mark" aria-label="Highlighted: quantum"&gt;</code>. Most apps don't bother because over-announcing distracts more than it helps; use <code>&lt;mark&gt;</code> for the visual + semantic contract and trust users to perceive context from the surrounding text.</p>
<p><strong>Custom styling:</strong> override the default yellow with CSS to match your design language &mdash; <code>mark { background: #fff3cd; padding: 0 0.2em; border-radius: 2px; }</code>.</p>
'''

ANSWERS[30] = r'''
<p>A "sticky footer" pattern keeps the footer at the bottom of the viewport when content is short, and at the bottom of the document when content is tall. The cleanest 2026 solution uses Flexbox or Grid on the body.</p>
<pre><code>&lt;body&gt;
  &lt;header&gt;...&lt;/header&gt;
  &lt;main&gt;
    &lt;p&gt;Page content (short or long)&lt;/p&gt;
  &lt;/main&gt;
  &lt;footer&gt;&copy; 2026 Acme&lt;/footer&gt;
&lt;/body&gt;

&lt;style&gt;
  /* Flexbox approach */
  body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    margin: 0;
  }
  main {
    flex: 1;        /* main takes all leftover space; footer pushed down */
  }
&lt;/style&gt;</code></pre>
<p><strong>How it works:</strong> the body fills at least the viewport height. The main is told to grow and consume remaining space. Header and footer keep their natural sizes. When content is short, main expands; when tall, main matches its content and the document scrolls normally with the footer at the bottom.</p>
<p><strong>CSS Grid alternative</strong> (more flexible for multi-row layouts):</p>
<pre><code>body {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;    /* header / main / footer */
  margin: 0;
}</code></pre>
<p><strong>Sticky footer vs fixed-position footer &mdash; not the same thing:</strong></p>
<ul>
  <li><strong>Sticky footer</strong> (above): footer is at the bottom of the viewport <em>when content is short</em>; flows normally when content is tall.</li>
  <li><strong>Fixed/pinned footer</strong>: footer is permanently visible at the bottom regardless of scroll position. Use <code>position: fixed; bottom: 0</code>.</li>
  <li><strong>position: sticky</strong>: hybrid; footer stays in flow but sticks to a position when scrolled past. Less common for footers.</li>
</ul>
<p><strong>Modern viewport units &mdash; <code>100vh</code> caveat:</strong> on mobile, <code>100vh</code> includes browser chrome at first then jumps when the URL bar hides, causing layout shift. Use <code>100dvh</code> (dynamic viewport height) instead &mdash; supported in all major browsers since 2022. For broader fallback:</p>
<pre><code>body { min-height: 100vh; min-height: 100dvh; }</code></pre>
<p>The older &mdash; and now obsolete &mdash; approach used negative margins and fixed footer heights. Flexbox/Grid eliminate that fragility entirely.</p>
'''

ANSWERS[31] = r'''
<p>The <code>&lt;abbr&gt;</code> element marks an abbreviation or acronym, and its <code>title</code> attribute provides the full expansion shown on hover and announced by some assistive tech.</p>
<pre><code>&lt;p&gt;The standard markup language for the web is
&lt;abbr title="HyperText Markup Language"&gt;HTML&lt;/abbr&gt;.
It works alongside &lt;abbr title="Cascading Style Sheets"&gt;CSS&lt;/abbr&gt;
and JavaScript.&lt;/p&gt;

&lt;p&gt;Standards bodies include the
&lt;abbr title="World Wide Web Consortium"&gt;W3C&lt;/abbr&gt; and the
&lt;abbr title="Web Hypertext Application Technology Working Group"&gt;WHATWG&lt;/abbr&gt;.&lt;/p&gt;</code></pre>
<p><strong>Behavior across user agents:</strong></p>
<ul>
  <li>Browsers underline with a dotted line by default; hover reveals the title as a tooltip.</li>
  <li>Mobile browsers don't show tooltips at all &mdash; users may never see the expansion.</li>
  <li>Screen readers vary: VoiceOver reads the expansion; NVDA may read just the abbreviation; JAWS announces "abbreviation" then the title (configurable).</li>
  <li>Search engines may use the title as additional context for the term.</li>
</ul>
<p><strong>The big tooltip caveat:</strong> the <code>title</code> attribute is <em>not a real tooltip mechanism</em>. It's mouse-only on desktop, invisible on mobile, hard to style, and inconsistently exposed to assistive tech. <strong>Don't put critical information in a <code>title</code> attribute</strong> &mdash; many users will never see it.</p>
<p><strong>Best-practice patterns:</strong></p>
<ol>
  <li><strong>Spell out on first use, abbreviate after</strong> &mdash; the standard journalism convention. Skip <code>&lt;abbr&gt;</code> if context already explains the term: "The HyperText Markup Language (HTML) is..."</li>
  <li><strong>Use <code>&lt;abbr&gt;</code> selectively</strong> for genuinely cryptic terms (technical acronyms, foreign abbreviations) where the expansion adds value beyond aesthetics.</li>
  <li><strong>Avoid wrapping every common acronym</strong> &mdash; "HTML", "API", "URL" don't benefit from <code>&lt;abbr&gt;</code> in a developer-audience context.</li>
</ol>
<p><strong>Accessible expansion patterns</strong> when expansions are critical: render the full term with the abbreviation in parentheses, or use a glossary page linked from each abbreviation's first occurrence.</p>
<p><strong>Acronym vs abbreviation:</strong> the deprecated <code>&lt;acronym&gt;</code> existed in HTML4 specifically for pronounced acronyms (NASA, FBI), distinct from spelled-out abbreviations (HTML, FBI). HTML5 dropped <code>&lt;acronym&gt;</code> because the distinction added no semantic value beyond <code>&lt;abbr&gt;</code> &mdash; the rendering and assistive tech behavior was identical.</p>
'''

ANSWERS[32] = r'''
<p>All three elements embed external content into a page, but they target different content types and offer very different security, scriptability, and UX tradeoffs. In 2026, <code>&lt;iframe&gt;</code> is the workhorse; <code>&lt;object&gt;</code> sees rare use; <code>&lt;embed&gt;</code> is essentially legacy.</p>
<pre><code>&lt;!-- iframe: embed an HTML document --&gt;
&lt;iframe src="/widget.html"
        title="Live status widget"
        width="600"
        height="400"
        sandbox="allow-scripts allow-same-origin"
        loading="lazy"&gt;
&lt;/iframe&gt;

&lt;!-- object: declarative embed with fallback content --&gt;
&lt;object data="report.pdf"
        type="application/pdf"
        width="600"
        height="800"&gt;
  &lt;p&gt;PDF preview unavailable.
     &lt;a href="report.pdf"&gt;Download report&lt;/a&gt;.&lt;/p&gt;
&lt;/object&gt;

&lt;!-- embed: void element, no fallback --&gt;
&lt;embed src="player.swf" type="application/x-shockwave-flash"&gt;</code></pre>
<p><strong>Capability comparison:</strong></p>
<table>
  <tr><th></th><th>iframe</th><th>object</th><th>embed</th></tr>
  <tr><td>Primary content</td><td>HTML documents</td><td>Any media (with type)</td><td>Plugin-style media</td></tr>
  <tr><td>Has fallback content</td><td>No (deprecated)</td><td>Yes (children)</td><td>No (void element)</td></tr>
  <tr><td>Sandbox attribute</td><td>Yes &mdash; rich security model</td><td>No</td><td>No</td></tr>
  <tr><td>Browsing context</td><td>Yes &mdash; nested browsing</td><td>Yes</td><td>Implementation-dependent</td></tr>
  <tr><td>Lazy-loading</td><td>Yes (<code>loading="lazy"</code>)</td><td>No</td><td>No</td></tr>
  <tr><td>2026 status</td><td>Modern, recommended</td><td>Niche</td><td>Largely legacy</td></tr>
</table>
<p><strong>Iframe security via <code>sandbox</code>:</strong> the most important reason iframe wins. <code>sandbox</code> applies a default-deny capability set; you grant only what's needed:</p>
<ul>
  <li><code>allow-scripts</code> &mdash; permits JavaScript.</li>
  <li><code>allow-same-origin</code> &mdash; treats the frame as same-origin (otherwise it's opaque).</li>
  <li><code>allow-forms</code>, <code>allow-popups</code>, <code>allow-modals</code>, <code>allow-downloads</code>, etc.</li>
  <li>Granting both <code>allow-scripts</code> AND <code>allow-same-origin</code> partially defeats the sandbox &mdash; the frame can remove its own <code>sandbox</code> attribute by reaching the parent. Only do this for trusted content.</li>
</ul>
<p><strong>Cross-document communication</strong> is via <code>postMessage</code>; always validate <code>event.origin</code> on receive. Use <code>Content-Security-Policy: frame-ancestors</code> to control who can embed your pages, and <code>X-Frame-Options</code> as a legacy fallback.</p>
<p><strong>When each fits:</strong> iframe for embedding live HTML widgets, payment forms (Stripe Elements), maps, video players. Object for inline PDF viewers with non-PDF fallback. Embed for legacy content where you have no other option.</p>
'''

ANSWERS[33] = r'''
<p>A responsive nav adapts to viewport width &mdash; horizontal links on desktop, a hamburger menu on mobile. The 2026 best-in-class approach uses CSS Container Queries or media queries with semantic markup and a CSS-only or progressively-enhanced JS toggle.</p>
<pre><code>&lt;nav class="primary-nav" aria-label="Primary"&gt;
  &lt;a href="/" class="brand"&gt;Acme&lt;/a&gt;

  &lt;button class="nav-toggle"
          aria-controls="nav-menu"
          aria-expanded="false"&gt;
    &lt;span class="visually-hidden"&gt;Menu&lt;/span&gt;
    &lt;svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"&gt;
      &lt;path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" fill="none"/&gt;
    &lt;/svg&gt;
  &lt;/button&gt;

  &lt;ul id="nav-menu" class="nav-menu"&gt;
    &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/docs"&gt;Docs&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/login"&gt;Log in&lt;/a&gt;&lt;/li&gt;
  &lt;/ul&gt;
&lt;/nav&gt;

&lt;style&gt;
  .primary-nav { display: flex; align-items: center; padding: 1rem; gap: 1rem; }
  .brand { font-weight: bold; margin-right: auto; }
  .nav-toggle { display: none; background: none; border: 0; cursor: pointer; }
  .nav-menu { display: flex; list-style: none; gap: 1.5rem; margin: 0; padding: 0; }

  @media (max-width: 700px) {
    .nav-toggle { display: block; }
    .nav-menu {
      display: none;
      position: absolute;
      top: 100%;
      left: 0; right: 0;
      flex-direction: column;
      padding: 1rem;
      background: white;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .nav-toggle[aria-expanded="true"] + .nav-menu { display: flex; }
  }
  .visually-hidden {
    position: absolute; width: 1px; height: 1px;
    overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap;
  }
&lt;/style&gt;

&lt;script&gt;
  const toggle = document.querySelector('.nav-toggle');
  toggle.addEventListener('click', () =&gt; {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
  });
&lt;/script&gt;</code></pre>
<p><strong>Accessibility-critical details:</strong></p>
<ul>
  <li><strong>Use <code>&lt;button&gt;</code> for the toggle</strong>, not <code>&lt;div&gt;</code>. Buttons are keyboard-focusable, fire on Enter/Space, and announce as buttons.</li>
  <li><strong><code>aria-controls</code> + <code>aria-expanded</code></strong> on the toggle so screen readers announce which menu it controls and its current state.</li>
  <li><strong>Hide decorative SVG</strong> with <code>aria-hidden="true"</code>; provide screen-reader-only text via <code>visually-hidden</code> class.</li>
  <li><strong>Focus management</strong> &mdash; when the menu opens, optionally move focus to the first item; on close (Esc key), return focus to the toggle.</li>
  <li><strong>Trap or close on outside click</strong> &mdash; mobile users expect tapping outside to dismiss.</li>
</ul>
<p><strong>Container Queries (modern alternative):</strong> for navs whose width depends on the parent rather than viewport (component libraries, multi-column layouts), use <code>@container</code> instead of <code>@media</code> &mdash; the nav adapts to its container's width regardless of viewport.</p>
<p><strong>Don't reach for a hamburger reflexively.</strong> If you have 3-5 links, fitting them in a horizontal bar is achievable down to ~360px. Hamburgers add a click and hide important destinations &mdash; valuable real estate goes to waste.</p>
'''

ANSWERS[34] = r'''
<p>Iframes are powerful but expose security, performance, and a11y pitfalls. Best practices in 2026 center on the <code>sandbox</code> attribute, lazy-loading, explicit titles, and origin policy.</p>
<p><strong>The non-negotiables:</strong></p>
<ul>
  <li><strong><code>title</code> attribute is required</strong> &mdash; screen readers announce it. Without one, users hear "frame" with no context. Treat as essential, not optional.</li>
  <li><strong>Use <code>sandbox</code> for untrusted content</strong> &mdash; embedded ads, user-submitted HTML, third-party widgets. Default-deny everything; explicitly grant <code>allow-scripts</code>, <code>allow-forms</code>, etc., only as needed.</li>
  <li><strong>Lazy-load below-the-fold iframes</strong> &mdash; <code>loading="lazy"</code> defers loading until the iframe approaches the viewport. Saves significant bandwidth on long pages with embedded videos or maps.</li>
  <li><strong>Set explicit dimensions</strong> &mdash; <code>width</code>/<code>height</code> attributes plus CSS prevent layout shift (CLS metric).</li>
  <li><strong>Specify <code>allow</code> for permissions policy</strong> &mdash; iframes can request <code>autoplay</code>, <code>fullscreen</code>, <code>geolocation</code>, etc. The <code>allow</code> attribute restricts which features the embedded content can use.</li>
</ul>
<pre><code>&lt;iframe
  src="https://untrusted-widget.example.com"
  title="Live commodity prices"
  width="600"
  height="400"
  loading="lazy"
  sandbox="allow-scripts"
  allow="fullscreen; clipboard-write"
  referrerpolicy="strict-origin-when-cross-origin"&gt;
&lt;/iframe&gt;</code></pre>
<p><strong>Sandbox capability flags worth knowing:</strong></p>
<table>
  <tr><th>Flag</th><th>Grants</th></tr>
  <tr><td>allow-scripts</td><td>JavaScript execution</td></tr>
  <tr><td>allow-same-origin</td><td>Treat as same origin (strong; combine carefully)</td></tr>
  <tr><td>allow-forms</td><td>Form submission</td></tr>
  <tr><td>allow-popups</td><td>window.open</td></tr>
  <tr><td>allow-modals</td><td>alert/confirm/prompt</td></tr>
  <tr><td>allow-downloads</td><td>File downloads</td></tr>
  <tr><td>allow-top-navigation</td><td>Navigate the parent window (almost never grant)</td></tr>
</table>
<p><strong>Server-side companion: clickjacking defense.</strong> Set <code>Content-Security-Policy: frame-ancestors 'self'</code> (or <code>'none'</code>) on your own pages so they can't be embedded by hostile sites. <code>X-Frame-Options: DENY</code> is the legacy header still recognized by older browsers.</p>
<p><strong>Cross-frame communication:</strong> use <code>window.postMessage</code> with strict origin checks on receive:</p>
<pre><code>// In parent
const iframe = document.querySelector('iframe');
iframe.contentWindow.postMessage({ type: 'config', theme: 'dark' }, 'https://widget.example.com');

// In iframe
window.addEventListener('message', (e) =&gt; {
  if (e.origin !== 'https://parent.example.com') return;   // CRITICAL
  if (e.data.type === 'config') applyConfig(e.data);
});</code></pre>
<p><strong>Performance:</strong> iframes block the parent's <code>load</code> event by default. For analytics/marketing widgets that don't need to be visible immediately, lazy-load is essentially free. Consider using <code>fetch</code> + <code>iframe.srcdoc</code> for synthesized content rather than network requests.</p>
'''

ANSWERS[35] = r'''
<p>A polyfill is JavaScript that implements a missing platform feature on older browsers, allowing modern code to run unchanged. The 2026 reality: polyfills are largely unnecessary for HTML5 because evergreen browsers cover everything &mdash; but <em>cutting-edge</em> features (Container Queries, View Transitions API, Popover, custom <code>showPicker</code> methods) sometimes need them for the long tail.</p>
<p><strong>The polyfill workflow:</strong></p>
<ol>
  <li><strong>Feature-detect</strong> &mdash; never rely on user-agent sniffing.</li>
  <li><strong>Conditionally load</strong> the polyfill only when missing (don't ship to capable browsers).</li>
  <li><strong>Implement the standard API</strong> as faithfully as possible &mdash; calling code shouldn't know it's polyfilled.</li>
</ol>
<pre><code>&lt;!-- Example: feature-detect <dialog> support --&gt;
&lt;script&gt;
  (function () {
    if (typeof HTMLDialogElement === 'undefined') {
      // Browser lacks &lt;dialog&gt;; load polyfill
      const s = document.createElement('script');
      s.src = '/vendor/dialog-polyfill.js';
      s.onload = () =&gt; {
        document.querySelectorAll('dialog').forEach(d =&gt; dialogPolyfill.registerDialog(d));
      };
      document.head.appendChild(s);
    }
  })();
&lt;/script&gt;</code></pre>
<p><strong>Polyfill categories:</strong></p>
<ul>
  <li><strong>Pure JS API polyfills</strong> &mdash; <code>fetch</code>, <code>Promise</code>, <code>Array.prototype.flat</code>. The cleanest case &mdash; just add a missing global or method. Often handled automatically by transpilers (Babel + core-js).</li>
  <li><strong>Element polyfills</strong> &mdash; <code>&lt;dialog&gt;</code>, <code>&lt;details&gt;</code>. Need to scan the DOM and inject behavior; require <code>MutationObserver</code> for dynamically-added elements.</li>
  <li><strong>CSS polyfills</strong> &mdash; Container Queries, CSS variables, <code>:has()</code>. Hardest category; usually require parsing stylesheets or adding inline styles. Often imperfect.</li>
  <li><strong>Web Components polyfills</strong> (Custom Elements, Shadow DOM) &mdash; from Google's <code>@webcomponents/webcomponentsjs</code>. Largely obsolete in 2026.</li>
</ul>
<p><strong>Modern delivery patterns:</strong></p>
<ul>
  <li><strong><code>polyfill.io</code></strong> &mdash; one URL serves only what the requesting browser needs (User-Agent-aware bundle). Stopped being maintained safely; recommend self-hosting or using <code>polyfill-fastly.io</code> in 2026.</li>
  <li><strong>Babel <code>@babel/preset-env</code> + core-js</strong> with <code>useBuiltIns: 'usage'</code> &mdash; only includes polyfills for features your code actually uses, sized to the browserslist target.</li>
  <li><strong>Differential bundling</strong> &mdash; serve modern bundles via <code>&lt;script type="module"&gt;</code> and legacy + polyfills via <code>&lt;script nomodule&gt;</code>.</li>
</ul>
<p><strong>When NOT to polyfill:</strong> if a feature is purely an enhancement (e.g., View Transitions for a smoother route change), let it gracefully degrade rather than ship a heavy polyfill. The cost of every byte of polyfill is paid by every user, including those who'd never see the difference.</p>
<p><strong>Progressive enhancement</strong> often beats polyfilling entirely: design for the lowest-common-denominator behavior, then layer modern features on top. The base experience works without JavaScript or modern CSS; advanced browsers get the upgrade.</p>
'''

ANSWERS[36] = r'''
<p>The <code>&lt;time&gt;</code> element marks dates, times, and durations as machine-readable. The visible text is for humans; the <code>datetime</code> attribute carries an unambiguous, parseable value for assistive tech, search engines, and JavaScript.</p>
<pre><code>&lt;p&gt;Published &lt;time datetime="2026-04-25"&gt;April 25, 2026&lt;/time&gt;&lt;/p&gt;

&lt;p&gt;Meeting at &lt;time datetime="2026-04-25T14:30:00-07:00"&gt;
  2:30 PM Pacific
&lt;/time&gt;&lt;/p&gt;

&lt;p&gt;Reading time: &lt;time datetime="PT8M"&gt;8 minutes&lt;/time&gt;&lt;/p&gt;

&lt;article&gt;
  &lt;header&gt;
    &lt;h1&gt;Article title&lt;/h1&gt;
    &lt;p&gt;
      &lt;time datetime="2026-04-25" pubdate&gt;April 25, 2026&lt;/time&gt;
      by Jane Smith
    &lt;/p&gt;
  &lt;/header&gt;
&lt;/article&gt;</code></pre>
<p><strong>Valid <code>datetime</code> formats</strong> (ISO 8601 / RFC 3339 subset):</p>
<table>
  <tr><th>Type</th><th>Example</th></tr>
  <tr><td>Year</td><td><code>2026</code></td></tr>
  <tr><td>Year-month</td><td><code>2026-04</code></td></tr>
  <tr><td>Date</td><td><code>2026-04-25</code></td></tr>
  <tr><td>Date + time + zone</td><td><code>2026-04-25T14:30:00-07:00</code></td></tr>
  <tr><td>Date + time UTC</td><td><code>2026-04-25T21:30:00Z</code></td></tr>
  <tr><td>Duration</td><td><code>PT2H30M</code> (2 hours 30 minutes)</td></tr>
  <tr><td>Time of day</td><td><code>14:30</code></td></tr>
  <tr><td>Week</td><td><code>2026-W17</code></td></tr>
</table>
<p><strong>Why this matters:</strong></p>
<ul>
  <li><strong>SEO &mdash; Schema.org / structured data:</strong> Google extracts <code>datetime</code> values for article publication dates, event times, and recipe cooking times. Without machine-readable dates, your "April 25, 2026" might be parsed wrong or ignored.</li>
  <li><strong>Localization:</strong> JavaScript can re-render the visible text in the user's locale: <code>document.querySelector('time').textContent = new Intl.DateTimeFormat(navigator.language).format(new Date(timeEl.dateTime))</code>.</li>
  <li><strong>Assistive tech:</strong> some screen readers announce the structured value, helping users who'd struggle with abbreviations like "5/4/26" (which day-month order?).</li>
  <li><strong>Sortability:</strong> CSS attribute selectors and JS can sort by <code>datetime</code> without parsing display strings: <code>elements.sort((a, b) =&gt; a.dateTime.localeCompare(b.dateTime))</code>.</li>
</ul>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Omitting <code>datetime</code> when the visible text is ambiguous &mdash; "April 25" without a year.</li>
  <li>Using locale-specific formats like "4/25/2026" in <code>datetime</code> &mdash; the attribute requires ISO 8601, not regional formats.</li>
  <li>Ignoring time zones &mdash; "2:30 PM" without offset is meaningless across regions. Either specify the zone (<code>-07:00</code>) or use UTC (<code>Z</code>).</li>
</ul>
<p><strong>The <code>pubdate</code> boolean</strong> existed in early HTML5 drafts to mark "this is the publication date for the nearest article." It was removed from the spec but harmless to leave; tools that recognized it have largely moved to Schema.org metadata instead.</p>
'''

ANSWERS[37] = r'''
<p>Accessible forms are built on a few non-negotiable patterns. HTML5 attributes do most of the heavy lifting; ARIA fills gaps where native semantics don't fit.</p>
<p><strong>The four foundations:</strong></p>
<ol>
  <li><strong>Every input has a programmatically-associated <code>&lt;label&gt;</code></strong> &mdash; either via <code>for</code>/<code>id</code> matching or by wrapping the input.</li>
  <li><strong>Group related fields with <code>&lt;fieldset&gt;</code> + <code>&lt;legend&gt;</code></strong> &mdash; especially radio/checkbox groups and address blocks.</li>
  <li><strong>Use the right input type</strong> &mdash; <code>type="email"</code>, <code>type="tel"</code>, <code>type="url"</code>, <code>type="number"</code>, <code>type="date"</code>. Each triggers correct mobile keyboards and built-in validation.</li>
  <li><strong>Provide error messages associated with their fields</strong> &mdash; <code>aria-describedby</code> + <code>aria-invalid</code> on submit failure.</li>
</ol>
<pre><code>&lt;form novalidate&gt;
  &lt;div class="field"&gt;
    &lt;label for="email"&gt;Email address (required)&lt;/label&gt;
    &lt;input type="email"
           id="email"
           name="email"
           required
           aria-describedby="email-help email-error"
           aria-invalid="false"
           autocomplete="email"&gt;
    &lt;p id="email-help" class="hint"&gt;
      We'll send a verification link.
    &lt;/p&gt;
    &lt;p id="email-error" class="error" role="alert" hidden&gt;&lt;/p&gt;
  &lt;/div&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;How did you hear about us?&lt;/legend&gt;
    &lt;label&gt;&lt;input type="radio" name="source" value="search"&gt; Search engine&lt;/label&gt;
    &lt;label&gt;&lt;input type="radio" name="source" value="friend"&gt; Friend&lt;/label&gt;
    &lt;label&gt;&lt;input type="radio" name="source" value="ad"&gt; Advertisement&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;button type="submit"&gt;Sign up&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Error handling pattern:</strong></p>
<pre><code>form.addEventListener('submit', (e) =&gt; {
  e.preventDefault();
  let firstInvalid = null;

  form.querySelectorAll('input').forEach(input =&gt; {
    const errorEl = document.getElementById(`${input.id}-error`);
    if (!input.checkValidity()) {
      input.setAttribute('aria-invalid', 'true');
      errorEl.textContent = input.validationMessage;
      errorEl.hidden = false;
      if (!firstInvalid) firstInvalid = input;
    } else {
      input.setAttribute('aria-invalid', 'false');
      errorEl.hidden = true;
    }
  });

  if (firstInvalid) {
    firstInvalid.focus();   // move focus to first error
  } else {
    form.submit();
  }
});</code></pre>
<p><strong>Critical accessibility details:</strong></p>
<ul>
  <li><strong>Don't rely on placeholder as a label</strong> &mdash; placeholder disappears on input and has poor contrast. Always have a visible label.</li>
  <li><strong><code>autocomplete</code> values matter</strong> &mdash; correct values (<code>email</code>, <code>name</code>, <code>tel</code>, <code>street-address</code>, etc.) let password managers and autofill work, which benefits motor-impaired users enormously.</li>
  <li><strong>Move focus to errors</strong> &mdash; on submit failure, focus the first invalid field so screen reader users hear the error immediately.</li>
  <li><strong>Live error announcements</strong> &mdash; <code>role="alert"</code> on a previously-empty error element causes screen readers to announce when text is added.</li>
  <li><strong>Sufficient color contrast</strong> &mdash; WCAG 2.2 requires 4.5:1 for text and 3:1 for UI components. Don't rely solely on color (red border) for error indication; pair with text.</li>
  <li><strong>Don't trap users with auto-submit</strong> &mdash; submitting on every keystroke breaks form review. Submit on explicit user action.</li>
</ul>
<p><strong>Test with a screen reader.</strong> Once. The first time you navigate your own form with VoiceOver, NVDA, or Orca, gaps become obvious. WCAG 2.2 forms criteria are largely about labeling and error messaging &mdash; the patterns above cover most of them.</p>
'''

ANSWERS[38] = r'''
<p>The <code>&lt;figcaption&gt;</code> element provides a caption for content inside a <code>&lt;figure&gt;</code>. It creates a <em>programmatic</em> association between the caption and its content, beyond what a visually-positioned paragraph could provide.</p>
<pre><code>&lt;figure&gt;
  &lt;img src="hubble-eagle.jpg" alt="Pillars of dust and gas in the Eagle Nebula"&gt;
  &lt;figcaption&gt;
    &lt;strong&gt;Figure 1.&lt;/strong&gt;
    The "Pillars of Creation" in the Eagle Nebula,
    photographed by the Hubble Space Telescope in 1995.
  &lt;/figcaption&gt;
&lt;/figure&gt;

&lt;figure&gt;
  &lt;pre&gt;&lt;code&gt;function add(a, b) { return a + b; }&lt;/code&gt;&lt;/pre&gt;
  &lt;figcaption&gt;Listing 3.2 &mdash; A simple addition function&lt;/figcaption&gt;
&lt;/figure&gt;

&lt;figure&gt;
  &lt;blockquote&gt;
    The unexamined life is not worth living.
  &lt;/blockquote&gt;
  &lt;figcaption&gt;&mdash; Socrates, &lt;cite&gt;Apology&lt;/cite&gt;&lt;/figcaption&gt;
&lt;/figure&gt;</code></pre>
<p><strong>Critical semantic distinctions:</strong></p>
<ul>
  <li><strong>The figure is self-contained.</strong> You should be able to move a <code>&lt;figure&gt;</code> elsewhere in the document &mdash; an appendix, a sidebar &mdash; without breaking the main text. If the surrounding paragraphs depend on the image's exact position to make sense, it shouldn't be a figure.</li>
  <li><strong>The caption isn't redundant with <code>alt</code>.</strong> The <code>alt</code> describes the image for users who can't see it; the <code>&lt;figcaption&gt;</code> labels and contextualizes the image for everyone (including sighted users). They serve different audiences and should usually contain different content.</li>
  <li><strong>Only one <code>&lt;figcaption&gt;</code> per <code>&lt;figure&gt;</code>.</strong> It must be either the first or last child of the figure.</li>
</ul>
<p><strong>Accessibility behavior:</strong></p>
<ul>
  <li>Screen readers announce the figure as a labeled region; the caption is associated with the figure's content.</li>
  <li>By default, the caption is announced after the image's alt text on most screen reader configurations.</li>
  <li>For an image where the caption fully describes the image, you can use <code>alt=""</code> to avoid duplicate announcement &mdash; but only if the caption truly conveys the visual content.</li>
</ul>
<p><strong>Beyond images:</strong> figures work for any self-contained content unit &mdash; code listings (with line numbers and a "Listing 3.2" caption), data tables (where the caption supplements the table's <code>&lt;caption&gt;</code> element), audio/video, mathematical formulas, diagrams. The pattern signals "here is a referenced piece of content" regardless of media.</p>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Using <code>&lt;figure&gt;</code> + <code>&lt;figcaption&gt;</code> for an image that's part of the prose flow &mdash; just use <code>&lt;img&gt;</code> with good <code>alt</code>.</li>
  <li>Putting the caption text in <code>title</code> attribute &mdash; <code>title</code> is a tooltip, not a caption.</li>
  <li>Wrapping a layout figure (like a header logo) in <code>&lt;figure&gt;</code> &mdash; the semantic implies the image is content worth referencing, which a logo isn't.</li>
</ul>
<p><strong>Citation pattern:</strong> the <code>&lt;cite&gt;</code> element inside a figcaption marks the title of a referenced work (book, article, painting). Combine with structured data (Schema.org's CreativeWork) for SEO benefits.</p>
'''

ANSWERS[39] = r'''
<p>The <code>&lt;bdi&gt;</code> (bidirectional isolate) element prevents text directionality from "leaking" between adjacent runs of text. It's essential when displaying user-generated content that might mix LTR (Latin scripts) and RTL (Arabic, Hebrew) characters &mdash; situations where the browser's automatic bidi algorithm produces wrong reading order.</p>
<p><strong>The problem it solves:</strong> when a username "&#1571;&#1581;&#1605;&#1583;" (Ahmed in Arabic, RTL) appears in a user list with a count, the browser tries to merge directional context with surrounding text. The number "5" can attach to the wrong side, the comma can flip, and the visual order becomes wrong.</p>
<pre><code>&lt;!-- Without bdi: number can attach to wrong side --&gt;
&lt;p&gt;User &lt;span&gt;&#1571;&#1581;&#1605;&#1583;&lt;/span&gt; has 5 messages&lt;/p&gt;

&lt;!-- With bdi: name is isolated, surrounding text reads cleanly --&gt;
&lt;p&gt;User &lt;bdi&gt;&#1571;&#1581;&#1605;&#1583;&lt;/bdi&gt; has 5 messages&lt;/p&gt;</code></pre>
<p><strong>How it works:</strong> <code>&lt;bdi&gt;</code> creates a directional boundary &mdash; the browser computes the contained text's directionality independently, treating it as an opaque unit when laying out neighboring text. The element has no default styling beyond direction handling.</p>
<pre><code>&lt;ul&gt;
  &lt;li&gt;User &lt;bdi&gt;Alice&lt;/bdi&gt; replied&lt;/li&gt;
  &lt;li&gt;User &lt;bdi&gt;&#1571;&#1581;&#1605;&#1583;&lt;/bdi&gt; replied&lt;/li&gt;
  &lt;li&gt;User &lt;bdi&gt;&#1497;&#1493;&#1505;&#1507;&lt;/bdi&gt; replied&lt;/li&gt;
  &lt;li&gt;User &lt;bdi&gt;Andr&eacute;&lt;/bdi&gt; replied&lt;/li&gt;
&lt;/ul&gt;</code></pre>
<p><strong>When you need <code>&lt;bdi&gt;</code> in 2026:</strong></p>
<ul>
  <li><strong>User-generated content rendered in templates</strong> &mdash; usernames, comments, search-result snippets where you don't control the language but do control surrounding chrome.</li>
  <li><strong>Internationalized UIs</strong> &mdash; product reviews, social feeds, chat applications.</li>
  <li><strong>Mixed-script lists</strong> &mdash; directories where some entries are Latin and some are Arabic/Hebrew/Persian.</li>
</ul>
<p><strong>Compared to alternatives:</strong></p>
<table>
  <tr><th>Tool</th><th>Behavior</th></tr>
  <tr><td><code>&lt;bdi&gt;</code></td><td>Auto-detect direction; isolate from surrounding text</td></tr>
  <tr><td><code>&lt;bdo dir="ltr"&gt;</code></td><td>Force a specific direction; no auto-detection</td></tr>
  <tr><td><code>dir="auto"</code> attribute</td><td>Apply auto-detection to any element (similar effect)</td></tr>
  <tr><td>Unicode control chars (U+2068, U+2069)</td><td>Same isolation, but invisible &mdash; harder to debug</td></tr>
</table>
<p><strong>The <code>dir="auto"</code> alternative</strong> works on any element and produces the same isolation behavior. Use <code>&lt;bdi&gt;</code> when you want the semantic intent of "this is a separate directional run" to be obvious in the markup; use <code>dir="auto"</code> on existing elements (<code>&lt;span dir="auto"&gt;</code>) when you don't want to introduce a new wrapping element.</p>
<p><strong>Why this matters:</strong> bidirectional rendering bugs are hard to spot if your team is monolingual. Even apps that "support" multiple languages often look wrong to RTL users because of leakage in chrome elements like timestamps, vote counts, and user mentions. <code>&lt;bdi&gt;</code> is a five-character fix that prevents weeks of post-launch bug reports from international users.</p>
'''

ANSWERS[40] = r'''
<p>The <code>&lt;track&gt;</code> element associates timed text with <code>&lt;video&gt;</code> or <code>&lt;audio&gt;</code> &mdash; subtitles, captions, descriptions, or chapter markers in WebVTT format. It's the accessibility cornerstone for media content; without tracks, deaf or hard-of-hearing users have no access to spoken audio.</p>
<pre><code>&lt;video controls width="640" height="360"&gt;
  &lt;source src="movie.mp4" type="video/mp4"&gt;
  &lt;source src="movie.webm" type="video/webm"&gt;

  &lt;track kind="captions"
         label="English"
         srclang="en"
         src="captions/movie.en.vtt"
         default&gt;
  &lt;track kind="captions"
         label="Spanish"
         srclang="es"
         src="captions/movie.es.vtt"&gt;
  &lt;track kind="subtitles"
         label="French (subtitles)"
         srclang="fr"
         src="subs/movie.fr.vtt"&gt;
  &lt;track kind="descriptions"
         label="English audio descriptions"
         srclang="en"
         src="desc/movie.en.vtt"&gt;
  &lt;track kind="chapters"
         label="Chapters"
         srclang="en"
         src="chapters.vtt"&gt;
&lt;/video&gt;</code></pre>
<p><strong>The five <code>kind</code> values:</strong></p>
<table>
  <tr><th>Kind</th><th>Purpose</th></tr>
  <tr><td><code>captions</code></td><td>Spoken dialogue + non-speech audio (sounds, music) &mdash; for deaf/HoH users</td></tr>
  <tr><td><code>subtitles</code></td><td>Translated dialogue &mdash; for users who don't speak the audio language</td></tr>
  <tr><td><code>descriptions</code></td><td>Spoken descriptions of visual content &mdash; for blind users (synthesized or pre-recorded)</td></tr>
  <tr><td><code>chapters</code></td><td>Chapter titles for navigation</td></tr>
  <tr><td><code>metadata</code></td><td>Programmatic data; not displayed to users</td></tr>
</table>
<p><strong>WebVTT format basics:</strong></p>
<pre><code>WEBVTT

NOTE Optional comment

1
00:00:01.000 --&gt; 00:00:04.000
Hello, welcome to the show.

2
00:00:04.500 --&gt; 00:00:08.000 line:0 align:start
&lt;v Speaker1&gt;This is who&rsquo;s talking.&lt;/v&gt;

3
00:00:08.500 --&gt; 00:00:11.000
Multiple lines work
on the same cue.</code></pre>
<p>Cues use <code>HH:MM:SS.mmm</code> timestamps; the optional cue settings after the timestamp control positioning. WebVTT supports inline tags (<code>&lt;v&gt;</code> for voice/speaker, <code>&lt;c&gt;</code> for class, <code>&lt;i&gt;</code>/<code>&lt;b&gt;</code>) and CSS styling via <code>::cue</code>.</p>
<p><strong>Critical attributes and behaviors:</strong></p>
<ul>
  <li><strong><code>default</code></strong> &mdash; one track per video can be marked default; the browser enables it automatically when the user's preferred language matches.</li>
  <li><strong><code>srclang</code></strong> &mdash; BCP 47 language tag (<code>en</code>, <code>es-MX</code>, <code>zh-Hant</code>); influences default-track selection and announcement.</li>
  <li><strong><code>label</code></strong> &mdash; the user-visible name in the track-selection menu.</li>
  <li><strong>CORS</strong> &mdash; cross-origin track files require <code>crossorigin</code> attribute on the video element AND CORS headers on the VTT file. Common gotcha.</li>
</ul>
<p><strong>Auto-generated captions vs human captions:</strong> auto-captioning (Whisper, Otter, YouTube auto-CC) reaches ~95% accuracy on clean audio &mdash; great as a starting point but not deployment-ready alone. Always have a human review pass for: speaker identification, technical terms, names, and non-speech audio cues like (laughter), (door slams). WCAG 2.2 SC 1.2.2 requires accurate captions; auto-captions alone don't meet the bar.</p>
<p><strong>Live streams</strong> use a different mechanism &mdash; live captions via WebSocket or Live VTT &mdash; outside the static <code>&lt;track&gt;</code> model. Services like Mux, Cloudflare Stream, and AWS Elemental MediaLive handle live caption injection.</p>
'''

ANSWERS[41] = r'''
<p>The Fullscreen API lets web pages take over the entire screen &mdash; useful for video players, presentations, games, and immersive experiences. Despite "HTML5" branding, it's a JavaScript API exposed on DOM elements rather than declarative HTML.</p>
<pre><code>&lt;video id="video" src="movie.mp4" controls&gt;&lt;/video&gt;
&lt;button id="fs-btn"&gt;Go fullscreen&lt;/button&gt;

&lt;script&gt;
  const btn = document.getElementById('fs-btn');
  const video = document.getElementById('video');

  btn.addEventListener('click', async () =&gt; {
    if (!document.fullscreenElement) {
      try {
        await video.requestFullscreen();
      } catch (err) {
        console.error('Fullscreen failed:', err);
      }
    } else {
      await document.exitFullscreen();
    }
  });

  document.addEventListener('fullscreenchange', () =&gt; {
    btn.textContent = document.fullscreenElement
      ? 'Exit fullscreen'
      : 'Go fullscreen';
  });

  document.addEventListener('fullscreenerror', (e) =&gt; {
    console.error('Fullscreen error:', e);
  });
&lt;/script&gt;</code></pre>
<p><strong>Core API surface:</strong></p>
<table>
  <tr><th>Method/Property</th><th>Purpose</th></tr>
  <tr><td><code>element.requestFullscreen()</code></td><td>Make element fullscreen (returns Promise)</td></tr>
  <tr><td><code>document.exitFullscreen()</code></td><td>Exit fullscreen mode</td></tr>
  <tr><td><code>document.fullscreenElement</code></td><td>The currently-fullscreen element (or null)</td></tr>
  <tr><td><code>document.fullscreenEnabled</code></td><td>Whether the API is available in this context</td></tr>
  <tr><td><code>fullscreenchange</code> event</td><td>Fires when entering or exiting</td></tr>
  <tr><td><code>fullscreenerror</code> event</td><td>Fires when request fails</td></tr>
</table>
<p><strong>The non-negotiable constraint:</strong> <code>requestFullscreen()</code> must be called from a user gesture (click, key press, touch). Browsers block it from arbitrary code &mdash; an obvious anti-popup measure. Errors silently if you try to call it during page load.</p>
<p><strong>CSS hooks:</strong> the <code>:fullscreen</code> pseudo-class lets you style elements differently when fullscreen:</p>
<pre><code>video:fullscreen {
  width: 100vw;
  height: 100vh;
  object-fit: contain;
  background: black;
}

/* Style the fullscreen backdrop */
video::backdrop {
  background: black;
}</code></pre>
<p><strong>Fullscreen for arbitrary elements</strong> &mdash; not just video. You can fullscreen a div, an iframe, or an entire SVG canvas:</p>
<pre><code>document.getElementById('app').requestFullscreen();</code></pre>
<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>iframe restrictions</strong> &mdash; embedded iframes need <code>allowfullscreen</code> attribute on the iframe AND the embedding page must allow it via Permissions Policy.</li>
  <li><strong>Mobile Safari quirks</strong> &mdash; iOS &lt;16 used <code>webkitEnterFullscreen()</code> on video elements specifically (not the standard API). 2026 baseline supports the standard API.</li>
  <li><strong>Don't auto-enter fullscreen on load</strong> &mdash; users find it disorienting; browsers block it anyway.</li>
  <li><strong>Provide an exit button</strong> &mdash; users may not know about <code>Esc</code>; mobile has no <code>Esc</code> key.</li>
</ul>
<p><strong>Related APIs in 2026:</strong></p>
<ul>
  <li><strong>Picture-in-Picture API</strong> (<code>video.requestPictureInPicture()</code>) &mdash; floating mini-window for video.</li>
  <li><strong>Screen Wake Lock API</strong> &mdash; prevents screen sleep during video playback or presentations.</li>
  <li><strong>Window Management API</strong> &mdash; multi-monitor placement for advanced apps.</li>
</ul>
<p>The Fullscreen API is mature and reliable. The bigger UX questions are <em>when</em> to enter fullscreen (not on load), how to exit (visible button + Esc), and how the surrounding UI adapts (CSS <code>:fullscreen</code> pseudo-class).</p>
'''

ANSWERS[42] = r'''
<p>The Ruby annotation elements provide pronunciation guides for East Asian characters &mdash; particularly Japanese furigana over kanji, but also Chinese pinyin, Korean hangul guides, and pedagogical content. They're rendered as small text positioned above (or beside) the base text.</p>
<pre><code>&lt;p&gt;
  &lt;ruby&gt;
    &#28450;&lt;rp&gt;(&lt;/rp&gt;&lt;rt&gt;kan&lt;/rt&gt;&lt;rp&gt;)&lt;/rp&gt;
    &#23383;&lt;rp&gt;(&lt;/rp&gt;&lt;rt&gt;ji&lt;/rt&gt;&lt;rp&gt;)&lt;/rp&gt;
  &lt;/ruby&gt;
&lt;/p&gt;</code></pre>
<p>This renders as &#28450;&#23383; (kanji) with "kan" displayed as small annotation above &#28450; and "ji" above &#23383;. In browsers without ruby support, the parentheses fallback shows: "&#28450;(kan)&#23383;(ji)".</p>
<p><strong>The three elements:</strong></p>
<table>
  <tr><th>Tag</th><th>Role</th></tr>
  <tr><td><code>&lt;ruby&gt;</code></td><td>Wrapper for the base text + annotations</td></tr>
  <tr><td><code>&lt;rt&gt;</code></td><td>Ruby text &mdash; the small annotation displayed above (the pronunciation)</td></tr>
  <tr><td><code>&lt;rp&gt;</code></td><td>Ruby parenthesis &mdash; fallback punctuation for browsers without ruby support</td></tr>
</table>
<p><strong>Common patterns:</strong></p>
<pre><code>&lt;!-- Per-character annotation (granular) --&gt;
&lt;ruby&gt;
  &#26085;&lt;rt&gt;ni&lt;/rt&gt;
  &#26412;&lt;rt&gt;hon&lt;/rt&gt;
  &#35486;&lt;rt&gt;go&lt;/rt&gt;
&lt;/ruby&gt;

&lt;!-- Whole-word annotation --&gt;
&lt;ruby&gt;
  &#26085;&#26412;&#35486;&lt;rt&gt;nihongo&lt;/rt&gt;
&lt;/ruby&gt;

&lt;!-- Pinyin for Chinese --&gt;
&lt;ruby&gt;
  &#20013;&lt;rt&gt;Zh&#333;ng&lt;/rt&gt;
  &#22269;&lt;rt&gt;gu&oacute;&lt;/rt&gt;
&lt;/ruby&gt;</code></pre>
<p><strong>The <code>&lt;rp&gt;</code> fallback:</strong> in browsers that don't render ruby (very rare in 2026, but historically a concern), the <code>&lt;rt&gt;</code> would appear inline as plain text. <code>&lt;rp&gt;</code> wraps fallback parentheses so the inline display still reads sensibly: "&#28450;(kan)&#23383;(ji)" instead of "&#28450;kan&#23383;ji". Modern browsers all hide <code>&lt;rp&gt;</code> by default.</p>
<p><strong>Use cases beyond Japanese:</strong></p>
<ul>
  <li><strong>Chinese pinyin</strong> &mdash; teaching materials, dictionaries.</li>
  <li><strong>Korean hangul</strong> over hanja (Chinese characters used in Korean contexts).</li>
  <li><strong>Phonetic guides</strong> for unusual or technical names in any language: "Smith&lt;rt&gt;smith&lt;/rt&gt;".</li>
  <li><strong>Glossing in linguistics</strong> &mdash; interlinear morpheme analysis (though specialized formats often handle this better).</li>
</ul>
<p><strong>CSS styling:</strong></p>
<pre><code>ruby {
  ruby-position: over;        /* over | under | inter-character */
  ruby-align: center;
}
rt {
  font-size: 0.6em;
  color: #666;
  font-weight: normal;
}</code></pre>
<p><strong>Advanced features:</strong> the spec also defines <code>&lt;rb&gt;</code> (ruby base) and <code>&lt;rtc&gt;</code> (ruby text container) for complex annotations &mdash; e.g., providing both pronunciation and meaning. Browser support for these is partial; most production usage stays with the basic <code>&lt;ruby&gt;</code> + <code>&lt;rt&gt;</code> + <code>&lt;rp&gt;</code> trio.</p>
<p><strong>Accessibility:</strong> screen readers announce both the base text and the ruby annotation. For native readers of the language, the ruby may be redundant noise; some screen readers offer settings to skip <code>&lt;rt&gt;</code> content. For learners, ruby provides essential pronunciation context.</p>
'''

ANSWERS[43] = r'''
<p>CSS Grid is the modern foundation for responsive grid layouts &mdash; a two-dimensional layout system with explicit control over both rows and columns. The <code>grid-template-columns</code> + <code>auto-fit</code>/<code>auto-fill</code> + <code>minmax()</code> trio handles the bulk of responsive cases without media queries.</p>
<pre><code>&lt;section class="card-grid"&gt;
  &lt;article class="card"&gt;Card 1&lt;/article&gt;
  &lt;article class="card"&gt;Card 2&lt;/article&gt;
  &lt;article class="card"&gt;Card 3&lt;/article&gt;
  &lt;article class="card"&gt;Card 4&lt;/article&gt;
  &lt;article class="card"&gt;Card 5&lt;/article&gt;
  &lt;article class="card"&gt;Card 6&lt;/article&gt;
&lt;/section&gt;

&lt;style&gt;
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }
  .card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  }
&lt;/style&gt;</code></pre>
<p><strong>How <code>auto-fit</code> + <code>minmax</code> works:</strong></p>
<ol>
  <li>Browser computes how many columns of <code>minmax(280px, 1fr)</code> fit in the container.</li>
  <li>Each column is at least 280px wide. If wider space is available, columns expand equally (<code>1fr</code>).</li>
  <li>When the container shrinks below 2 &times; 280px + gap, columns drop to 1; when it grows past 3 &times; 280px + gaps, a third column appears. No media queries needed.</li>
</ol>
<p><strong><code>auto-fit</code> vs <code>auto-fill</code>:</strong></p>
<ul>
  <li><strong><code>auto-fill</code></strong> &mdash; fills the row with empty tracks if there aren't enough items. Existing items keep their size; phantom columns reserve space.</li>
  <li><strong><code>auto-fit</code></strong> &mdash; collapses empty tracks; existing items expand to fill leftover space. Usually what you want.</li>
</ul>
<p><strong>Multi-zone layouts with named areas</strong> for app shells:</p>
<pre><code>.app-shell {
  display: grid;
  min-height: 100vh;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 240px 1fr;
  grid-template-rows: auto 1fr auto;
}
header { grid-area: header; }
nav    { grid-area: sidebar; }
main   { grid-area: main; }
footer { grid-area: footer; }

@media (max-width: 700px) {
  .app-shell {
    grid-template-areas:
      "header"
      "main"
      "sidebar"
      "footer";
    grid-template-columns: 1fr;
  }
}</code></pre>
<p>Named areas make complex layouts readable; the same HTML rearranges entirely with one media query rewriting the grid template.</p>
<p><strong>Modern features beyond the basics:</strong></p>
<ul>
  <li><strong>Subgrid</strong> &mdash; child grids inherit parent's tracks. Solves the "align card bodies even though card heights differ" problem.</li>
  <li><strong>Container Queries</strong> &mdash; <code>@container (min-width: 600px)</code> for components that adapt to their container, not the viewport. Essential for design systems.</li>
  <li><strong><code>grid-template-rows: masonry</code></strong> &mdash; Pinterest-style masonry layouts (Firefox-only as of 2026; spec evolving).</li>
  <li><strong><code>place-items</code> / <code>place-content</code></strong> &mdash; align items in cells with one shorthand instead of <code>align-items</code> + <code>justify-items</code>.</li>
</ul>
<p><strong>Grid vs Flexbox &mdash; rule of thumb:</strong> Grid for two-dimensional layout (cards, dashboards, page shells); Flexbox for one-dimensional (nav bars, button groups, form rows). Combine them &mdash; use Grid for page structure, Flexbox inside each cell. Both are universally supported in 2026; <code>display: grid</code> is no more "advanced" than <code>display: flex</code>.</p>
<p><strong>Performance:</strong> Grid is GPU-accelerated and scales to thousands of items without layout thrashing. The cost is initial layout calculation; for very-large grids (10k+ cells), virtualization libraries (TanStack Virtual, react-window) sit on top of CSS Grid.</p>
'''

ANSWERS[44] = r'''
<p>Web Components are a suite of standards that let you create reusable, encapsulated HTML elements &mdash; with their own templates, scoped styles, and lifecycle &mdash; that work in any framework or no framework at all. The bundle comprises four primary specs: Custom Elements, Shadow DOM, HTML Templates, and ES Modules. By 2026, they're a stable, baseline-supported web platform feature.</p>
<pre><code>&lt;!-- The custom element used like any HTML tag --&gt;
&lt;rating-stars value="4.5" max="5"&gt;&lt;/rating-stars&gt;

&lt;script type="module"&gt;
  class RatingStars extends HTMLElement {
    static observedAttributes = ['value', 'max'];

    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
      this.render();
    }

    attributeChangedCallback(name, oldVal, newVal) {
      if (oldVal !== newVal) this.render();
    }

    render() {
      const value = parseFloat(this.getAttribute('value')) || 0;
      const max   = parseInt(this.getAttribute('max')) || 5;
      const pct   = (value / max) * 100;

      this.shadowRoot.innerHTML = `
        &lt;style&gt;
          :host { display: inline-block; line-height: 1; }
          .stars { position: relative; font-size: 1.5em; }
          .empty { color: #ddd; }
          .filled {
            color: #ff9500;
            position: absolute;
            top: 0; left: 0;
            overflow: hidden;
            width: ${pct}%;
            white-space: nowrap;
          }
        &lt;/style&gt;
        &lt;span class="stars"&gt;
          &lt;span class="empty"&gt;&star;&star;&star;&star;&star;&lt;/span&gt;
          &lt;span class="filled"&gt;&starf;&starf;&starf;&starf;&starf;&lt;/span&gt;
        &lt;/span&gt;
      `;
    }
  }

  customElements.define('rating-stars', RatingStars);
&lt;/script&gt;</code></pre>
<p><strong>The four pillars in detail:</strong></p>
<table>
  <tr><th>Spec</th><th>What it does</th></tr>
  <tr><td>Custom Elements</td><td>Define new HTML tags with JavaScript classes</td></tr>
  <tr><td>Shadow DOM</td><td>Encapsulated subtree with scoped styles and DOM</td></tr>
  <tr><td>HTML Templates</td><td><code>&lt;template&gt;</code> + <code>&lt;slot&gt;</code> for reusable inert markup</td></tr>
  <tr><td>ES Modules</td><td>Standard import/export, replacing earlier HTML Imports</td></tr>
</table>
<p><strong>Lifecycle callbacks:</strong></p>
<ul>
  <li><code>connectedCallback()</code> &mdash; element added to DOM. Set up listeners, fetch data.</li>
  <li><code>disconnectedCallback()</code> &mdash; element removed. Clean up listeners, cancel timers.</li>
  <li><code>attributeChangedCallback(name, old, new)</code> &mdash; observed attribute changed. Re-render.</li>
  <li><code>adoptedCallback()</code> &mdash; moved to a new document.</li>
  <li><strong><code>static observedAttributes</code></strong> &mdash; required to receive attribute change callbacks.</li>
</ul>
<p><strong>Slots &mdash; light DOM projection:</strong></p>
<pre><code>&lt;!-- Component definition --&gt;
&lt;template id="card-template"&gt;
  &lt;div class="card"&gt;
    &lt;h2&gt;&lt;slot name="title"&gt;Default title&lt;/slot&gt;&lt;/h2&gt;
    &lt;div class="body"&gt;&lt;slot&gt;&lt;/slot&gt;&lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;!-- Usage projects content into named slots --&gt;
&lt;my-card&gt;
  &lt;span slot="title"&gt;Custom title&lt;/span&gt;
  &lt;p&gt;Body content goes in the default slot.&lt;/p&gt;
&lt;/my-card&gt;</code></pre>
<p><strong>Styling boundary:</strong> Shadow DOM strictly isolates styles. Outside CSS doesn't reach inside; inside <code>&lt;style&gt;</code> doesn't escape. The boundary is crossed by:</p>
<ul>
  <li><strong>CSS Custom Properties</strong> &mdash; inherited through Shadow DOM, so consumers can theme.</li>
  <li><strong><code>::part()</code></strong> &mdash; expose specific elements for outside styling: <code>&lt;button part="primary"&gt;</code>, then <code>my-component::part(primary) { ... }</code>.</li>
  <li><strong><code>:host</code></strong> &mdash; styles the component element itself from inside.</li>
</ul>
<p><strong>When Web Components shine:</strong> design systems shared across multiple frameworks (a button used in React + Vue + Astro projects), embeddable widgets (a checkout button on third-party sites), browser extensions injecting UI into arbitrary pages. Where they struggle: complex state management (frameworks do better), SSR (improving with Declarative Shadow DOM, but more complex than React/Vue's SSR).</p>
<p><strong>2026 ecosystem:</strong> Lit (Google) is the dominant framework for authoring Web Components &mdash; provides reactive properties, templating, and lifecycle helpers. Stencil (Ionic) compiles to vanilla Web Components plus framework-specific wrappers. Native Web Components without a library are perfectly viable for simple components.</p>
'''

ANSWERS[45] = r'''
<p>The <code>&lt;main&gt;</code> element marks the dominant content of the page &mdash; the unique content that distinguishes this page from others on the site. It maps to the ARIA <code>role="main"</code> landmark and provides a primary skip target for assistive tech and "Skip to content" links.</p>
<pre><code>&lt;body&gt;
  &lt;a href="#main" class="skip-link"&gt;Skip to main content&lt;/a&gt;

  &lt;header&gt;
    &lt;nav aria-label="Primary"&gt;...&lt;/nav&gt;
  &lt;/header&gt;

  &lt;main id="main"&gt;
    &lt;article&gt;
      &lt;h1&gt;Article title&lt;/h1&gt;
      &lt;p&gt;The actual content of this page...&lt;/p&gt;
    &lt;/article&gt;
  &lt;/main&gt;

  &lt;aside aria-label="Related"&gt;
    &lt;h2&gt;You might also like&lt;/h2&gt;
    &lt;ul&gt;...&lt;/ul&gt;
  &lt;/aside&gt;

  &lt;footer&gt;
    &lt;p&gt;&copy; 2026 Acme&lt;/p&gt;
  &lt;/footer&gt;
&lt;/body&gt;</code></pre>
<p><strong>Critical rules:</strong></p>
<ul>
  <li><strong>One <code>&lt;main&gt;</code> per page</strong> &mdash; technically multiple are allowed if all but one have <code>hidden</code>, but in practice keep it singular.</li>
  <li><strong>Don't nest inside other landmarks</strong> &mdash; <code>&lt;main&gt;</code> shouldn't be inside <code>&lt;header&gt;</code>, <code>&lt;nav&gt;</code>, <code>&lt;aside&gt;</code>, <code>&lt;footer&gt;</code>, or <code>&lt;article&gt;</code>. It's a top-level region.</li>
  <li><strong>Exclude repeated chrome</strong> &mdash; site header, primary nav, sidebars, footer all live <em>outside</em> <code>&lt;main&gt;</code>. Search results, forms, articles, and the unique focus of the page live <em>inside</em>.</li>
</ul>
<p><strong>The skip-link pattern</strong> is the textbook accessibility win. Keyboard users (and screen reader users) who press Tab on every page would otherwise traverse navigation links repeatedly before reaching content:</p>
<pre><code>.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  background: #000;
  color: white;
  padding: 1rem;
  z-index: 100;
}
.skip-link:focus {
  top: 0;        /* visible only when focused */
}</code></pre>
<p>Press Tab on page load &rarr; skip link appears &rarr; press Enter &rarr; focus moves to <code>#main</code> &rarr; tabbing now lands on real content. WCAG 2.4.1 (Bypass Blocks) treats this as a Level A requirement.</p>
<p><strong>Behavioral semantics:</strong></p>
<ul>
  <li>Screen readers expose <code>&lt;main&gt;</code> as a landmark; users navigate by landmark using shortcut keys.</li>
  <li>Search engines emphasize content inside <code>&lt;main&gt;</code> for "main content" SEO signals.</li>
  <li>Reader mode (Safari, Firefox) heavily prefers <code>&lt;main&gt;</code> when extracting content.</li>
</ul>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Using <code>&lt;div id="main"&gt;</code> instead of <code>&lt;main&gt;</code> &mdash; misses the landmark.</li>
  <li>Wrapping the entire body in <code>&lt;main&gt;</code> &mdash; defeats the purpose; should exclude header/footer.</li>
  <li>Multiple <code>&lt;main&gt;</code>s per page &mdash; assistive tech behavior is unpredictable.</li>
  <li>Repeating navigation or article-list chrome inside &mdash; users hear "main content" then encounter the same nav they just skipped.</li>
</ul>
<p><strong>Single-page apps:</strong> in SPAs, <code>&lt;main&gt;</code> often holds the route outlet. When the route changes, focus should programmatically move to <code>&lt;main&gt;</code> (or its first heading) so screen reader users hear the new content. React Router's <code>useLocation</code> + <code>useEffect</code> + <code>main.focus()</code> is a common pattern; tabIndex="-1" on the main makes it focusable without disturbing tab order.</p>
'''

ANSWERS[46] = r'''
<p>Print-friendly HTML pairs the right semantic structure with a print stylesheet that strips screen-only chrome, optimizes ink usage, manages page breaks, and preserves URLs for printed-out links.</p>
<pre><code>&lt;!-- Link a print-specific stylesheet --&gt;
&lt;link rel="stylesheet" href="screen.css" media="screen"&gt;
&lt;link rel="stylesheet" href="print.css" media="print"&gt;</code></pre>
<p><strong>Or use a single stylesheet with @media print:</strong></p>
<pre><code>/* In your main CSS */
@media print {
  /* Reset for paper */
  body {
    color: black;
    background: white;
    font-size: 11pt;       /* point sizes for print */
    line-height: 1.4;
  }

  /* Hide screen-only chrome */
  header nav, footer, .ads, .share-buttons,
  .comments, .sidebar, .skip-link {
    display: none;
  }

  /* Show URL after each link */
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-size: 0.85em;
    color: #555;
  }

  /* Don't print URL after internal/anchor links */
  a[href^="#"]::after,
  a[href^="javascript"]::after {
    content: "";
  }

  /* Page break controls */
  h1, h2, h3 {
    break-after: avoid;     /* don't orphan headings */
    page-break-after: avoid; /* legacy alias */
  }
  pre, blockquote, table, figure {
    break-inside: avoid;    /* keep code/quotes/tables on one page */
  }
  article {
    break-after: page;      /* one article per page */
  }

  /* Fit-to-page sizing */
  img {
    max-width: 100% !important;
    page-break-inside: avoid;
  }

  /* Show only first column of multi-column layouts */
  .columns {
    column-count: 1;
  }
}

/* Page setup */
@page {
  size: A4;            /* or letter, legal */
  margin: 2cm 1.5cm;

  @top-center {
    content: "Acme Annual Report 2026";
  }
  @bottom-right {
    content: "Page " counter(page) " of " counter(pages);
  }
}</code></pre>
<p><strong>Critical print considerations:</strong></p>
<ul>
  <li><strong>Use point sizes (<code>pt</code>) not pixels</strong> &mdash; <code>pt</code> maps reliably to printed dimensions; <code>px</code> behavior is browser-dependent.</li>
  <li><strong>Black text, white background</strong> &mdash; saves ink, improves legibility on paper.</li>
  <li><strong>Show link URLs</strong> &mdash; printed links lose their hyperlink semantics; the URL appearing after them recovers the information.</li>
  <li><strong>Page break controls</strong> &mdash; <code>break-before</code>, <code>break-after</code>, <code>break-inside</code> handle awkward page boundaries. Headings shouldn't end pages alone; tables shouldn't split mid-row.</li>
  <li><strong>Hide interactive UI</strong> &mdash; share buttons, comment forms, navigation, ads serve no purpose on paper.</li>
</ul>
<p><strong>The <code>@page</code> rule</strong> controls the page itself: size, margins, and named regions for headers/footers. Browser support varies; complex page-region layouts are best-effort with PDF-generation libraries.</p>
<p><strong>Page break properties:</strong></p>
<table>
  <tr><th>Property</th><th>Behavior</th></tr>
  <tr><td><code>break-before: page</code></td><td>Force a page break before this element</td></tr>
  <tr><td><code>break-after: avoid</code></td><td>Try not to break after this element</td></tr>
  <tr><td><code>break-inside: avoid</code></td><td>Keep this element on one page if possible</td></tr>
</table>
<p><strong>Testing print output</strong> via the browser's Print Preview is the only reliable workflow. Chrome DevTools' "Emulate CSS media: print" lets you iterate without paper. Print-to-PDF saves trees during testing.</p>
<p><strong>For complex print needs</strong> &mdash; invoices, reports, books &mdash; consider headless browser PDF generation (Puppeteer, Playwright). For server-side PDFs without a browser, libraries like wkhtmltopdf, Prince, or PDFKit handle the heavy lifting; Prince has the strongest CSS Paged Media support.</p>
'''

ANSWERS[47] = r'''
<p>The <code>&lt;blockquote&gt;</code> element marks an extended quotation set off from surrounding prose &mdash; multiple sentences or paragraphs cited from another source. Browsers default-style it with left/right indent; the semantic value goes much further than the visual.</p>
<pre><code>&lt;blockquote cite="https://www.gutenberg.org/files/1342/1342-h/1342-h.htm"&gt;
  &lt;p&gt;It is a truth universally acknowledged, that a single man
  in possession of a good fortune, must be in want of a wife.&lt;/p&gt;

  &lt;p&gt;However little known the feelings or views of such a man
  may be on his first entering a neighbourhood, this truth is so
  well fixed in the minds of the surrounding families...&lt;/p&gt;
&lt;/blockquote&gt;
&lt;p class="attribution"&gt;
  &mdash; Jane Austen, &lt;cite&gt;Pride and Prejudice&lt;/cite&gt; (1813)
&lt;/p&gt;</code></pre>
<p><strong>Key semantics:</strong></p>
<ul>
  <li><strong><code>cite</code> attribute</strong> &mdash; URL identifying the source. Not visible to users; consumed by machines (search engines, structured data extractors).</li>
  <li><strong>Block-level element</strong> &mdash; should contain block content (paragraphs, lists), not just inline text. Use <code>&lt;q&gt;</code> for short inline quotes.</li>
  <li><strong>Attribution goes outside</strong> &mdash; the spec is explicit: the <code>&lt;blockquote&gt;</code> contains only the quoted material. Author/source attribution goes in a sibling element, not inside.</li>
</ul>
<p><strong>The attribution debate:</strong> putting the citation inside <code>&lt;blockquote&gt;</code> is technically valid HTML (it's flow content) but semantically wrong &mdash; the attribution isn't part of what was quoted. The recommended pattern wraps the quote and its attribution in a <code>&lt;figure&gt;</code>:</p>
<pre><code>&lt;figure&gt;
  &lt;blockquote&gt;
    &lt;p&gt;The unexamined life is not worth living.&lt;/p&gt;
  &lt;/blockquote&gt;
  &lt;figcaption&gt;
    &mdash; Socrates, as recorded by Plato in &lt;cite&gt;Apology&lt;/cite&gt;
  &lt;/figcaption&gt;
&lt;/figure&gt;</code></pre>
<p>This is now widely recommended &mdash; figure provides the labeled-content semantic; figcaption holds the attribution; blockquote contains only the actual quoted text.</p>
<p><strong>Compared to <code>&lt;q&gt;</code> (inline quote):</strong></p>
<table>
  <tr><th></th><th>blockquote</th><th>q</th></tr>
  <tr><td>Use case</td><td>Multi-paragraph quotation set off from prose</td><td>Short inline quote within a sentence</td></tr>
  <tr><td>Display</td><td>Block; indented</td><td>Inline; auto-quoted by browser</td></tr>
  <tr><td>Quote marks</td><td>Author provides them as needed</td><td>Browser inserts locale-appropriate marks</td></tr>
</table>
<p><strong>Styling for emphasis:</strong></p>
<pre><code>blockquote {
  border-left: 4px solid #0055aa;
  padding-left: 1.5em;
  margin: 1.5em 0;
  font-style: italic;
  color: #444;
}

/* Decorative quote mark */
blockquote::before {
  content: "\201C";       /* Left double quotation mark */
  font-size: 4em;
  line-height: 0.1;
  color: #ccc;
  vertical-align: -0.4em;
}</code></pre>
<p><strong>Structured data:</strong> for SEO and rich-snippet eligibility, mark blockquotes with Schema.org's <code>Quotation</code> type or pair with article-level <code>creator</code> and <code>datePublished</code> properties.</p>
<p><strong>Accessibility:</strong> screen readers don't announce <code>&lt;blockquote&gt;</code> distinctly by default &mdash; the visual offset doesn't translate to audio. For users who'd benefit from explicit "quote begins/ends" announcement, layer ARIA: <code>&lt;blockquote role="region" aria-label="Quote from Pride and Prejudice"&gt;</code>. Most don't bother because reading flow usually conveys the quotation through context.</p>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Using <code>&lt;blockquote&gt;</code> just for indentation &mdash; use CSS <code>margin</code>/<code>padding</code> instead.</li>
  <li>Putting attribution inside (semantic mismatch) &mdash; use the figure pattern.</li>
  <li>Wrapping quotes that aren't actually external citations &mdash; if it's an emphasis or pull-quote of your own writing, <code>&lt;blockquote&gt;</code> isn't right.</li>
</ul>
'''

ANSWERS[48] = r'''
<p>ARIA (Accessible Rich Internet Applications) bridges the gap between HTML's built-in semantics and modern interactive UIs. The first rule of ARIA is "don't use ARIA" &mdash; native HTML elements have correct semantics built in, and adding ARIA to override them creates accessibility bugs. ARIA shines when you're building components that have no native HTML equivalent.</p>
<p><strong>The five rules of ARIA</strong> (W3C ARIA Authoring Practices, paraphrased):</p>
<ol>
  <li><strong>Use a native element if it exists.</strong> <code>&lt;button&gt;</code> beats <code>&lt;div role="button"&gt;</code>, every time.</li>
  <li><strong>Don't change native semantics</strong> unless absolutely necessary. <code>&lt;h2 role="button"&gt;</code> is almost always wrong.</li>
  <li><strong>All interactive ARIA controls must be keyboard-accessible</strong> &mdash; click handlers alone aren't enough; you need keyboard equivalents.</li>
  <li><strong>Don't suppress focus on focusable elements.</strong> <code>tabindex="-1"</code> on a button is usually a mistake.</li>
  <li><strong>Interactive elements need accessible names.</strong> Either visible text, <code>aria-label</code>, or <code>aria-labelledby</code>.</li>
</ol>
<p><strong>The three ARIA capabilities:</strong></p>
<table>
  <tr><th>Type</th><th>Examples</th><th>What they do</th></tr>
  <tr><td>Roles</td><td><code>role="button"</code>, <code>role="dialog"</code>, <code>role="alert"</code></td><td>Tell AT what kind of widget this is</td></tr>
  <tr><td>States</td><td><code>aria-expanded</code>, <code>aria-checked</code>, <code>aria-busy</code></td><td>Current state of widgets</td></tr>
  <tr><td>Properties</td><td><code>aria-label</code>, <code>aria-describedby</code>, <code>aria-required</code></td><td>Stable characteristics</td></tr>
</table>
<p><strong>The most-used ARIA patterns in practice:</strong></p>
<pre><code>&lt;!-- 1. Disclosure widgets (collapsibles, accordions, dropdowns) --&gt;
&lt;button aria-expanded="false" aria-controls="menu1"&gt;Filter&lt;/button&gt;
&lt;div id="menu1" hidden&gt;...&lt;/div&gt;

&lt;!-- 2. Live regions for dynamic content (toasts, chat messages, notifications) --&gt;
&lt;div role="status" aria-live="polite"&gt;
  Settings saved successfully.
&lt;/div&gt;

&lt;div role="alert" aria-live="assertive"&gt;
  Error: payment declined.
&lt;/div&gt;

&lt;!-- 3. Form errors --&gt;
&lt;input id="email"
       aria-invalid="true"
       aria-describedby="email-error"&gt;
&lt;p id="email-error" class="error"&gt;Please enter a valid email&lt;/p&gt;

&lt;!-- 4. Decorative content hidden from AT --&gt;
&lt;svg aria-hidden="true"&gt;...&lt;/svg&gt;

&lt;!-- 5. Naming icon-only buttons --&gt;
&lt;button aria-label="Close dialog"&gt;
  &lt;svg aria-hidden="true"&gt;...&lt;/svg&gt;
&lt;/button&gt;</code></pre>
<p><strong>Live regions explained:</strong></p>
<ul>
  <li><strong><code>aria-live="polite"</code></strong> &mdash; AT waits for current speech to finish before announcing. Use for non-urgent updates: toast notifications, save confirmations, status messages.</li>
  <li><strong><code>aria-live="assertive"</code></strong> &mdash; interrupts current speech immediately. Use sparingly; reserved for genuine emergencies (errors blocking submission, payment failures).</li>
  <li><strong><code>role="status"</code></strong> = polite implicitly; <strong><code>role="alert"</code></strong> = assertive implicitly. Use the role; the live attribute is redundant.</li>
  <li><strong>Empty live regions on page load</strong> &mdash; the region must exist when content arrives; injecting both the region and its content together can fail to announce on some screen readers.</li>
</ul>
<p><strong>WAI-ARIA Authoring Practices Guide (APG)</strong> is the canonical reference for complex widget patterns &mdash; combobox, treeview, datepicker, tabs, modal dialog. Each pattern documents the expected role/state/property/keyboard combination. Most production patterns are also implemented by accessible component libraries (Headless UI, Radix UI, React Aria); using a library is almost always less risky than rolling your own.</p>
<p><strong>Common ARIA mistakes:</strong></p>
<ul>
  <li><code>role="button"</code> on a <code>&lt;div&gt;</code> without keyboard handlers, focus styles, or proper announcement.</li>
  <li>Redundant ARIA: <code>&lt;button role="button"&gt;</code>, <code>&lt;a href role="link"&gt;</code>.</li>
  <li>Live regions injected after the message &mdash; nothing to announce because the region is brand new.</li>
  <li>Misusing <code>aria-hidden="true"</code> on focusable elements &mdash; AT users tab into something they can't perceive.</li>
  <li>Overuse of <code>aria-label</code> on text-bearing elements, where it overrides the visible label.</li>
</ul>
<p><strong>Testing:</strong> the only reliable verification is testing with a screen reader. Run NVDA or VoiceOver through one full task flow per release; automated testing (axe-core, Lighthouse) catches the easy 30% but misses semantic and contextual issues.</p>
'''

ANSWERS[49] = r'''
<p>"HTML5 Offline Web Applications" was the original AppCache standard for making sites work without a network. AppCache is now <strong>removed from all major browsers</strong> &mdash; deprecated in 2018 and removed by 2022. The modern replacement is <strong>Service Workers + Cache API</strong>, the foundation of Progressive Web Apps.</p>
<p><strong>Why AppCache failed:</strong></p>
<ul>
  <li>Manifest-driven, declarative system &mdash; no fine-grained control over caching strategy.</li>
  <li>Counterintuitive update model &mdash; hard to know when fresh content would actually be served.</li>
  <li>Bizarre fallback behavior &mdash; users could be permanently stuck with stale resources.</li>
  <li>"AppCache is a douchebag" &mdash; the legendary 2013 critique that catalyzed its replacement.</li>
</ul>
<p><strong>The 2026 model: Service Workers.</strong> A Service Worker is a JS script that runs in a separate worker thread, between the page and the network. It can intercept every request and decide: serve from cache, fetch from network, generate a response, or fall back gracefully.</p>
<pre><code>&lt;!-- Register the service worker from your page --&gt;
&lt;script&gt;
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(reg =&gt; console.log('SW registered:', reg.scope))
      .catch(err =&gt; console.error('SW registration failed:', err));
  }
&lt;/script&gt;</code></pre>
<pre><code>// sw.js — the service worker itself
const CACHE_VERSION = 'v3';
const CACHE_NAME = `app-cache-${CACHE_VERSION}`;
const PRECACHE = [
  '/',
  '/index.html',
  '/styles.css',
  '/app.js',
  '/offline.html',
  '/icons/icon-192.png',
];

// Install — pre-cache critical assets
self.addEventListener('install', (event) =&gt; {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =&gt; cache.addAll(PRECACHE))
  );
});

// Activate — clean up old caches
self.addEventListener('activate', (event) =&gt; {
  event.waitUntil(
    caches.keys().then(names =&gt;
      Promise.all(
        names.filter(n =&gt; n !== CACHE_NAME).map(n =&gt; caches.delete(n))
      )
    )
  );
});

// Fetch — cache-first with network fallback
self.addEventListener('fetch', (event) =&gt; {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cached =&gt; {
      if (cached) return cached;

      return fetch(event.request)
        .then(response =&gt; {
          // Cache successful responses for next time
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache =&gt; cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() =&gt; caches.match('/offline.html'));
    })
  );
});</code></pre>
<p><strong>Caching strategies</strong> (Workbox, the production library, formalized these):</p>
<table>
  <tr><th>Strategy</th><th>When to use</th></tr>
  <tr><td>Cache-first</td><td>App shell, static assets &mdash; fast, cached even when online</td></tr>
  <tr><td>Network-first</td><td>API responses &mdash; fresh data preferred; cache as fallback</td></tr>
  <tr><td>Stale-while-revalidate</td><td>Content that's tolerant of brief staleness &mdash; serve cache instantly, update background</td></tr>
  <tr><td>Cache-only</td><td>Versioned assets (hashed filenames) &mdash; never need to refetch</td></tr>
  <tr><td>Network-only</td><td>Operations that must round-trip &mdash; payments, auth</td></tr>
</table>
<p><strong>Beyond Cache API:</strong> a full PWA combines:</p>
<ul>
  <li><strong>Service Worker</strong> &mdash; intercepts requests, manages caches.</li>
  <li><strong>Web App Manifest</strong> (<code>manifest.json</code>) &mdash; tells browsers the app's name, icons, theme color, display mode for "Add to Home Screen".</li>
  <li><strong>IndexedDB</strong> &mdash; structured offline data storage (much more capable than LocalStorage).</li>
  <li><strong>Background Sync API</strong> &mdash; defer failed requests until network returns.</li>
  <li><strong>Web Push API</strong> &mdash; server-initiated notifications.</li>
</ul>
<p><strong>2026 production reality:</strong> roll your own service worker only for simple cases. For real apps, use <strong>Workbox</strong> &mdash; Google's library that handles versioning, precaching, route registration, expiration, and edge cases. Frameworks (Next.js with <code>next-pwa</code>, Astro with PWA integration) wire it up automatically.</p>
<p><strong>Testing offline support:</strong> Chrome DevTools Network tab &rarr; "Offline" throttling, or Application tab &rarr; Service Workers &rarr; "Offline". Lighthouse audits confirm PWA criteria: installable, fast on 3G, works offline.</p>
<p><strong>Caveat &mdash; offline first isn't always the goal.</strong> Most CRUD apps don't benefit much from offline; the user-experience gains accrue mostly to news, docs, productivity, and field-work apps. Decide whether offline is core to the use case before adopting the architectural complexity.</p>
'''

ANSWERS[50] = r'''
<p>HTML provides three semantic elements for code-related content: <code>&lt;code&gt;</code>, <code>&lt;pre&gt;</code>, and <code>&lt;samp&gt;</code>. They serve different purposes and combine in idiomatic patterns for code listings, inline mentions, and program output.</p>
<table>
  <tr><th>Tag</th><th>Meaning</th><th>Default style</th></tr>
  <tr><td><code>&lt;code&gt;</code></td><td>Source code (any length, any context)</td><td>Inline; monospace font</td></tr>
  <tr><td><code>&lt;pre&gt;</code></td><td>Preformatted text &mdash; preserve whitespace and line breaks</td><td>Block; monospace; whitespace preserved</td></tr>
  <tr><td><code>&lt;samp&gt;</code></td><td>Sample output from a program</td><td>Inline; monospace</td></tr>
  <tr><td><code>&lt;kbd&gt;</code></td><td>Keyboard input the user should type</td><td>Inline; monospace</td></tr>
  <tr><td><code>&lt;var&gt;</code></td><td>Variable name in math or programming</td><td>Inline; italic</td></tr>
</table>
<p><strong>Inline code references:</strong></p>
<pre><code>&lt;p&gt;Use the &lt;code&gt;Array.prototype.map()&lt;/code&gt; method
to transform each element. Pass a callback that
returns the new value.&lt;/p&gt;</code></pre>
<p><strong>Multi-line code blocks:</strong> the canonical pattern is <code>&lt;pre&gt;</code> + <code>&lt;code&gt;</code> nested. <code>&lt;pre&gt;</code> preserves whitespace and line breaks; <code>&lt;code&gt;</code> adds the "this is source code" semantic.</p>
<pre><code>&lt;pre&gt;&lt;code class="language-javascript"&gt;
function fibonacci(n) {
  if (n &lt; 2) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
&lt;/code&gt;&lt;/pre&gt;</code></pre>
<p><strong>The <code>language-*</code> class</strong> is the convention adopted by syntax highlighters (Prism, highlight.js, Shiki) &mdash; it tells the highlighter which grammar to apply. Highlighters then add token-level <code>&lt;span&gt;</code> wrappers with classes like <code>token keyword</code>, <code>token string</code> for CSS-driven coloring.</p>
<p><strong>Sample output and keyboard input:</strong></p>
<pre><code>&lt;p&gt;Run &lt;code&gt;ls -la&lt;/code&gt; to see all files.
You should see output like:&lt;/p&gt;

&lt;samp&gt;
total 24
drwxr-xr-x  2 user  staff   64 Apr 25 14:30 .
-rw-r--r--  1 user  staff  142 Apr 25 14:25 README.md
&lt;/samp&gt;

&lt;p&gt;Press &lt;kbd&gt;Ctrl&lt;/kbd&gt;+&lt;kbd&gt;C&lt;/kbd&gt; to interrupt.&lt;/p&gt;</code></pre>
<p><strong>The semantic distinction matters when:</strong></p>
<ul>
  <li><strong>Documentation tools</strong> extract code blocks for execution, syntax checking, or testing.</li>
  <li><strong>Reading mode</strong> in browsers preserves code formatting only when it recognizes the elements.</li>
  <li><strong>Search engines</strong> may treat code distinctly from prose.</li>
  <li><strong>Style</strong> &mdash; you can target each separately: <code>code { background: #f5f5f5; }</code>, <code>kbd { border: 1px solid #ccc; box-shadow: 0 1px 0 #ccc; }</code>.</li>
</ul>
<p><strong>Encoding HTML in code blocks:</strong> if the code itself contains <code>&lt;</code> or <code>&amp;</code>, you must escape them as <code>&amp;lt;</code> or <code>&amp;amp;</code>. Otherwise the browser parses them as actual tags. This is the bane of authoring HTML examples in HTML &mdash; markdown processors, MDX, and templating engines mostly handle it for you.</p>
<p><strong>Modern enhancements:</strong></p>
<ul>
  <li><strong>Copy buttons</strong> &mdash; standard pattern: <code>&lt;button&gt;</code> + Clipboard API. Position absolutely over <code>&lt;pre&gt;</code>.</li>
  <li><strong>Line numbers</strong> &mdash; CSS counters or library-specific. Add <code>tabindex="0"</code> on the <code>&lt;pre&gt;</code> for keyboard scrolling on overflow.</li>
  <li><strong>Diff highlighting</strong> &mdash; Shiki, Prism, and Bright support added/removed line markup.</li>
  <li><strong>Twoslash (Shiki Twoslash)</strong> &mdash; embeds TypeScript type info inline; great for technical docs.</li>
</ul>
<p><strong>Accessibility:</strong> long code blocks should be focusable for keyboard scrolling: <code>pre[tabindex="0"]</code>. Provide context with <code>aria-label</code>: <code>&lt;pre tabindex="0" aria-label="JavaScript code example"&gt;</code>. Some screen readers offer code-aware navigation when these tags are used; non-semantic <code>&lt;div&gt;</code> wrappers lose this.</p>
'''

ANSWERS[51] = r'''
<p>The <code>&lt;cite&gt;</code> element marks the <strong>title of a creative work</strong> &mdash; a book, film, song, painting, research paper, software, etc. It&rsquo;s narrowly defined: it&rsquo;s for <em>titles</em>, not for the people who created them or the URLs where they live.</p>

<pre><code>&lt;p&gt;My favorite novel is &lt;cite&gt;The Lord of the Rings&lt;/cite&gt;
   by J.R.R. Tolkien.&lt;/p&gt;

&lt;p&gt;The film &lt;cite&gt;Casablanca&lt;/cite&gt; was released in 1942.&lt;/p&gt;

&lt;blockquote cite="https://example.com/source"&gt;
  &lt;p&gt;Imagination is more important than knowledge.&lt;/p&gt;
  &lt;footer&gt;
    — &lt;cite&gt;What Life Means to Einstein&lt;/cite&gt;,
    Saturday Evening Post, 1929
  &lt;/footer&gt;
&lt;/blockquote&gt;</code></pre>

<p><strong>The crucial distinction:</strong></p>
<table>
  <tr><th>What you mean</th><th>Right tag</th></tr>
  <tr><td>Title of a work (novel, film, song, paper)</td><td><code>&lt;cite&gt;</code></td></tr>
  <tr><td>Author&rsquo;s name</td><td>Plain text or <code>&lt;span&gt;</code></td></tr>
  <tr><td>URL of a source</td><td><code>cite</code> attribute on <code>&lt;blockquote&gt;</code> or <code>&lt;q&gt;</code></td></tr>
  <tr><td>The quote itself</td><td><code>&lt;blockquote&gt;</code> or <code>&lt;q&gt;</code></td></tr>
</table>

<p><strong>Default styling</strong> &mdash; browsers italicize <code>&lt;cite&gt;</code> by default, mirroring the typographic convention for titles in print. Override with CSS as needed:</p>
<pre><code>cite {
  font-style: italic;
}
cite::before { content: "\201C"; }   /* opening curly quote */
cite::after  { content: "\201D"; }   /* closing curly quote */</code></pre>

<p><strong>The HTML4 vs HTML5 controversy:</strong> HTML4 allowed <code>&lt;cite&gt;</code> for the author&rsquo;s name as well. HTML5 narrowed it to just titles. Some style guides still wrap author names in <code>&lt;cite&gt;</code>. The W3C and WHATWG specs disagree slightly, but most modern usage follows WHATWG: titles only.</p>

<p><strong>Don&rsquo;t confuse with the <code>cite</code> attribute</strong> on <code>&lt;blockquote&gt;</code> and <code>&lt;q&gt;</code>:</p>
<pre><code>&lt;!-- The cite ATTRIBUTE holds a URL of the source --&gt;
&lt;blockquote cite="https://example.com/article-source"&gt;
  &lt;p&gt;Some quoted text.&lt;/p&gt;
&lt;/blockquote&gt;

&lt;!-- The &lt;cite&gt; ELEMENT holds a visible title --&gt;
&lt;p&gt;See &lt;cite&gt;The HTML Standard&lt;/cite&gt; for details.&lt;/p&gt;</code></pre>

<p>The attribute is invisible and machine-readable; the element is visible and human-readable. Most browsers don&rsquo;t expose the attribute&rsquo;s URL anywhere, so its practical impact is limited to scrapers and automated tooling.</p>
'''

ANSWERS[52] = r'''
<p>File uploads in HTML have a few non-obvious requirements that catch developers regularly. Get any of them wrong and uploads silently fail or arrive empty on the server.</p>

<p><strong>The minimal correct file upload form:</strong></p>
<pre><code>&lt;form action="/upload"
      method="post"
      enctype="multipart/form-data"&gt;

  &lt;label for="avatar"&gt;Profile picture:&lt;/label&gt;
  &lt;input type="file"
         id="avatar"
         name="avatar"
         accept="image/png, image/jpeg, image/webp"
         required&gt;

  &lt;button type="submit"&gt;Upload&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p><strong>Three things must be exactly right:</strong></p>
<ol>
  <li><strong><code>method="post"</code></strong> &mdash; <code>get</code> can&rsquo;t carry binary data; the server gets nothing.</li>
  <li><strong><code>enctype="multipart/form-data"</code></strong> &mdash; without it, only the filename is sent, not the actual bytes. This is the #1 file upload bug.</li>
  <li><strong><code>name</code> attribute on the input</strong> &mdash; without it, the file isn&rsquo;t part of the submission.</li>
</ol>

<p><strong>Useful attributes:</strong></p>
<table>
  <tr><th>Attribute</th><th>Purpose</th></tr>
  <tr><td><code>accept</code></td><td>Hint to file picker (extensions or MIME types). UX only &mdash; not a security check.</td></tr>
  <tr><td><code>multiple</code></td><td>Allow selecting many files at once</td></tr>
  <tr><td><code>capture="user"</code> / <code>environment</code></td><td>Mobile camera (front / back)</td></tr>
  <tr><td><code>required</code></td><td>Block submission with no file selected</td></tr>
</table>

<p><strong>Modern alternative: drag-and-drop with progress:</strong></p>
<pre><code>const input = document.getElementById("avatar");
input.addEventListener("change", async () =&gt; {
  const file = input.files[0];
  const fd = new FormData();
  fd.append("avatar", file);

  const xhr = new XMLHttpRequest();
  xhr.upload.onprogress = (e) =&gt; {
    if (e.lengthComputable) {
      progressBar.value = (e.loaded / e.total) * 100;
    }
  };
  xhr.open("POST", "/upload");
  xhr.send(fd);
});</code></pre>

<p>Using <code>FormData</code> + <code>XMLHttpRequest</code> (or <code>fetch</code> with <code>body: formData</code>) lets you show progress, handle responses without page reload, and add UI affordances like preview thumbnails.</p>

<p><strong>Server-side concerns</strong> (always required):</p>
<ul>
  <li><strong>File size limits</strong> &mdash; without them, users can fill your disk.</li>
  <li><strong>Verify file type by content</strong>, not just extension or browser-sent MIME (use file magic bytes).</li>
  <li><strong>Generate random filenames</strong> &mdash; never trust user-provided names (path traversal risk).</li>
  <li><strong>Direct-to-cloud uploads</strong> via signed URLs (S3, R2, Cloudinary) bypass your servers entirely &mdash; better for large files and high traffic.</li>
</ul>
'''

ANSWERS[53] = r'''
<p>These two semantic elements are easily confused but mean different things. <code>&lt;footer&gt;</code> describes a region of the page or article; <code>&lt;address&gt;</code> describes contact information for a person, organization, or article author.</p>

<table>
  <tr><th></th><th><code>&lt;footer&gt;</code></th><th><code>&lt;address&gt;</code></th></tr>
  <tr><td>What it represents</td><td>The footer of a section or page</td><td>Contact information for the nearest article or document</td></tr>
  <tr><td>Typical content</td><td>Copyright, navigation, related links, author info</td><td>Email, phone, postal address of an author/contact</td></tr>
  <tr><td>Default style</td><td>Block, normal weight</td><td>Block, italic</td></tr>
  <tr><td>Number per article</td><td>0-1 (footer of that article)</td><td>0-1 per article + 1 page-level</td></tr>
</table>

<p><strong>Common combination:</strong></p>
<pre><code>&lt;footer&gt;
  &lt;address&gt;
    &lt;a href="mailto:editor@example.com"&gt;editor@example.com&lt;/a&gt;
    &lt;br&gt;
    Acme Publishing, 123 Main St, City, ZIP
    &lt;br&gt;
    Phone: &lt;a href="tel:+15551234567"&gt;+1 (555) 123-4567&lt;/a&gt;
  &lt;/address&gt;
  &lt;p&gt;&amp;copy; 2026 Acme Publishing&lt;/p&gt;
&lt;/footer&gt;</code></pre>

<p>The <code>&lt;footer&gt;</code> contains the bottom-of-page region; the <code>&lt;address&gt;</code> contains specifically the contact details. They naturally pair.</p>

<p><strong>Per-article addresses:</strong></p>
<pre><code>&lt;article&gt;
  &lt;h2&gt;Getting Started with HTML&lt;/h2&gt;
  &lt;p&gt;Author bio:&lt;/p&gt;
  &lt;address&gt;
    Jane Smith, &lt;a href="mailto:jane@example.com"&gt;jane@example.com&lt;/a&gt;
  &lt;/address&gt;
  &lt;p&gt;In this guide we&rsquo;ll cover...&lt;/p&gt;
&lt;/article&gt;</code></pre>

<p>The article&rsquo;s <code>&lt;address&gt;</code> applies to that article&rsquo;s author. A page-level <code>&lt;address&gt;</code> in a top-level <code>&lt;footer&gt;</code> applies to the document as a whole.</p>

<p><strong>Common mistake: postal addresses in <code>&lt;address&gt;</code> for non-contact purposes:</strong></p>
<pre><code>&lt;!-- WRONG — this is just a street address, not contact info --&gt;
&lt;p&gt;The conference will be held at:&lt;/p&gt;
&lt;address&gt;
  Convention Center
  100 Main Street
&lt;/address&gt;

&lt;!-- RIGHT --&gt;
&lt;p&gt;The conference will be held at:&lt;/p&gt;
&lt;p&gt;
  Convention Center&lt;br&gt;
  100 Main Street
&lt;/p&gt;</code></pre>

<p><code>&lt;address&gt;</code> is for "how to contact the author of this content" &mdash; it&rsquo;s not a generic geographic-address element. The HTML spec is explicit about this.</p>

<p><strong>Browsers italicize <code>&lt;address&gt;</code></strong> by default; reset with CSS if your design wants different styling. Screen readers announce both as their semantic role, helping users understand which content is contact info versus general footer matter.</p>
'''

ANSWERS[54] = r'''
<p><code>&lt;canvas&gt;</code> is a <strong>raster bitmap drawing surface</strong> &mdash; you set its size, then draw into it imperatively with JavaScript. Unlike SVG (vector), canvas is pixel-based: once drawn, the result is just an array of pixels with no inherent structure.</p>

<p><strong>Two rendering contexts:</strong></p>
<table>
  <tr><th>Context</th><th>Use case</th></tr>
  <tr><td><code>2d</code></td><td>2D shapes, text, images, transformations</td></tr>
  <tr><td><code>webgl</code> / <code>webgl2</code></td><td>3D graphics via OpenGL ES; GPU-accelerated</td></tr>
  <tr><td><code>webgpu</code></td><td>Next-gen GPU compute and graphics (2026 widely supported)</td></tr>
</table>

<p><strong>2D drawing example:</strong></p>
<pre><code>&lt;canvas id="game" width="800" height="600"&gt;
  Your browser doesn&rsquo;t support canvas.
&lt;/canvas&gt;

&lt;script&gt;
  const canvas = document.getElementById("game");
  const ctx    = canvas.getContext("2d");

  // Filled rectangle
  ctx.fillStyle = "#0066cc";
  ctx.fillRect(50, 50, 200, 100);

  // Stroked path with curves
  ctx.strokeStyle = "#ff6b35";
  ctx.lineWidth   = 3;
  ctx.beginPath();
  ctx.moveTo(300, 50);
  ctx.bezierCurveTo(400, 0, 500, 200, 600, 100);
  ctx.stroke();

  // Text
  ctx.font = "24px sans-serif";
  ctx.fillStyle = "black";
  ctx.fillText("Hello, canvas!", 50, 250);

  // Image (after it loads)
  const img = new Image();
  img.onload = () =&gt; ctx.drawImage(img, 50, 300, 200, 150);
  img.src = "photo.jpg";
&lt;/script&gt;</code></pre>

<p><strong>Animation loop with <code>requestAnimationFrame</code>:</strong></p>
<pre><code>let x = 0;
function frame() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillRect(x, 100, 50, 50);
  x = (x + 2) % canvas.width;
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);</code></pre>

<p><strong>Canvas vs SVG &mdash; pick wisely:</strong></p>
<table>
  <tr><th></th><th>Canvas</th><th>SVG</th></tr>
  <tr><td>Model</td><td>Pixel buffer</td><td>Retained DOM tree</td></tr>
  <tr><td>Best for</td><td>Many objects (10k+), real-time animation, games, image processing</td><td>Few objects (&lt;1000), interactive shapes, icons, charts</td></tr>
  <tr><td>Resolution</td><td>Fixed; pixelates when scaled up</td><td>Vector; scales infinitely</td></tr>
  <tr><td>Accessibility</td><td>Hard &mdash; just pixels; needs ARIA + fallback DOM</td><td>Built in &mdash; titles, descriptions, semantic structure</td></tr>
  <tr><td>Hit testing</td><td>Manual coordinate math</td><td>Click events on shapes</td></tr>
</table>

<p><strong>High-DPI handling</strong> &mdash; without this step, canvas looks blurry on retina displays:</p>
<pre><code>const dpr  = window.devicePixelRatio || 1;
const rect = canvas.getBoundingClientRect();
canvas.width  = rect.width  * dpr;
canvas.height = rect.height * dpr;
canvas.style.width  = rect.width  + "px";
canvas.style.height = rect.height + "px";
ctx.scale(dpr, dpr);</code></pre>

<p><strong>Common use cases:</strong> particle simulations, games (Phaser, PixiJS), data visualization (Chart.js, Plotly), image editing, signature pads, drawing apps, AR/VR scenes via WebGL/WebGPU.</p>

<p><strong>Accessibility:</strong> canvas pixels are opaque to assistive tech. Provide a parallel DOM representation as fallback content inside <code>&lt;canvas&gt;</code>, or use the Accessibility Object Model. Otherwise screen readers see nothing.</p>
'''

ANSWERS[55] = r'''
<p>The <code>&lt;caption&gt;</code> element is a <strong>title for an entire table</strong>. It must be the first child of <code>&lt;table&gt;</code> and tells users (and assistive tech) what the table contains before they read it.</p>

<pre><code>&lt;table&gt;
  &lt;caption&gt;Quarterly Revenue by Region &mdash; 2026&lt;/caption&gt;
  &lt;thead&gt;
    &lt;tr&gt;
      &lt;th&gt;Region&lt;/th&gt;
      &lt;th&gt;Q1&lt;/th&gt;
      &lt;th&gt;Q2&lt;/th&gt;
      &lt;th&gt;Q3&lt;/th&gt;
      &lt;th&gt;Q4&lt;/th&gt;
    &lt;/tr&gt;
  &lt;/thead&gt;
  &lt;tbody&gt;
    &lt;tr&gt;&lt;td&gt;North&lt;/td&gt;&lt;td&gt;$125k&lt;/td&gt;&lt;td&gt;$142k&lt;/td&gt;&lt;td&gt;$158k&lt;/td&gt;&lt;td&gt;$170k&lt;/td&gt;&lt;/tr&gt;
  &lt;/tbody&gt;
&lt;/table&gt;</code></pre>

<p><strong>Why it matters more than a heading above the table:</strong></p>
<ul>
  <li><strong>Programmatically associated</strong> with the table &mdash; screen readers announce "table, [caption], 5 columns, 4 rows" as one unit when entering the table.</li>
  <li><strong>Stays bonded with the table</strong> in print, PDF export, and reader mode. A heading is a separate sibling element that can drift.</li>
  <li><strong>Keeps the document outline clean</strong> &mdash; no extra <code>&lt;h3&gt;</code> consuming a heading level just to label a table.</li>
</ul>

<p><strong>Positioning the caption</strong> &mdash; default is above the table:</p>
<pre><code>caption {
  caption-side: top;          /* default */
  caption-side: bottom;       /* moves caption below the table */

  font-weight: 600;
  font-size: 1.1em;
  text-align: left;
  padding: 0.5em;
  color: #333;
}</code></pre>

<p><strong>Adding a longer description</strong> &mdash; for complex tables, pair caption with <code>aria-describedby</code> pointing to a fuller explanation:</p>
<pre><code>&lt;table aria-describedby="rev-desc"&gt;
  &lt;caption&gt;Quarterly Revenue by Region &mdash; 2026&lt;/caption&gt;
  ...
&lt;/table&gt;
&lt;p id="rev-desc"&gt;
  This table compares quarterly revenue across four regions...
&lt;/p&gt;</code></pre>

<p>Screen readers announce the description on entering the table after the caption.</p>

<p><strong>Position rules:</strong></p>
<ul>
  <li><code>&lt;caption&gt;</code> must be the <strong>first child</strong> of <code>&lt;table&gt;</code>. Browsers will display it correctly even if you place it elsewhere, but the spec forbids it and validators flag it.</li>
  <li>Only one <code>&lt;caption&gt;</code> per table.</li>
  <li>Caption can contain inline content (text, links, <code>&lt;em&gt;</code>) but should be brief &mdash; one sentence.</li>
</ul>

<p>For data tables in standalone contexts &mdash; reports, dashboards, downloadable views &mdash; always include a caption. It&rsquo;s a small addition with significant accessibility and clarity benefits.</p>
'''

ANSWERS[56] = r'''
<p>The <code>placeholder</code> attribute provides hint text inside an empty input. It&rsquo;s a UX convenience &mdash; not a label substitute &mdash; and using it correctly requires understanding its limits.</p>

<pre><code>&lt;form&gt;
  &lt;label for="email"&gt;Email&lt;/label&gt;
  &lt;input type="email"
         id="email"
         name="email"
         placeholder="you@example.com"
         required&gt;

  &lt;label for="phone"&gt;Phone&lt;/label&gt;
  &lt;input type="tel"
         id="phone"
         name="phone"
         placeholder="+1 (555) 123-4567"&gt;

  &lt;label for="dob"&gt;Date of birth&lt;/label&gt;
  &lt;input type="text"
         id="dob"
         name="dob"
         placeholder="DD / MM / YYYY"
         pattern="\d{2}/\d{2}/\d{4}"&gt;
&lt;/form&gt;</code></pre>

<p><strong>Style the placeholder</strong> &mdash; use the <code>::placeholder</code> pseudo-element:</p>
<pre><code>input::placeholder {
  color: #999;
  font-style: italic;
  opacity: 1;          /* Firefox defaults to 0.54 */
}</code></pre>

<p><strong>Why placeholder is NOT a substitute for a label:</strong></p>
<ol>
  <li><strong>Disappears as soon as the user types</strong> &mdash; if they pause halfway through filling a multi-input form, they may forget what each field is for.</li>
  <li><strong>Often low contrast</strong> &mdash; defaults to gray, fails WCAG contrast requirements without overrides.</li>
  <li><strong>Inconsistent screen reader behavior</strong> &mdash; some announce it, some don&rsquo;t; never reliable as the only label source.</li>
  <li><strong>Confused with prefilled values</strong> &mdash; users may think the form is pre-filled and try to delete the placeholder.</li>
</ol>

<p><strong>The right pattern: visible label + format hint placeholder.</strong></p>
<pre><code>&lt;!-- WRONG — placeholder as label --&gt;
&lt;input type="email" placeholder="Email"&gt;

&lt;!-- RIGHT — proper label, placeholder for format hint --&gt;
&lt;label for="email"&gt;Email&lt;/label&gt;
&lt;input type="email" id="email" placeholder="you@example.com"&gt;</code></pre>

<p><strong>Floating label pattern</strong> &mdash; combines the visual elegance of placeholder-as-label with proper accessibility:</p>
<pre><code>&lt;div class="float-label"&gt;
  &lt;input type="email" id="email" placeholder=" "&gt;
  &lt;label for="email"&gt;Email&lt;/label&gt;
&lt;/div&gt;

&lt;style&gt;
  .float-label { position: relative; }
  .float-label label {
    position: absolute;
    left: 0.5em;
    top: 0.75em;
    pointer-events: none;
    transition: 0.2s;
    color: #888;
  }
  .float-label input:focus + label,
  .float-label input:not(:placeholder-shown) + label {
    transform: translateY(-1em) scale(0.85);
    color: #0066cc;
  }
&lt;/style&gt;</code></pre>

<p>The <code>placeholder=" "</code> (a single space) keeps the input technically non-empty for the <code>:not(:placeholder-shown)</code> selector, while staying visually empty. The label "floats" up when the field is focused or contains content. Best of both worlds.</p>
'''

ANSWERS[57] = r'''
<p>The <code>&lt;optgroup&gt;</code> element groups related options inside a <code>&lt;select&gt;</code>. It adds a non-selectable header and visual indentation, helping users navigate long dropdowns.</p>

<pre><code>&lt;label for="country"&gt;Country:&lt;/label&gt;
&lt;select id="country" name="country"&gt;
  &lt;option value=""&gt;-- Select --&lt;/option&gt;

  &lt;optgroup label="Americas"&gt;
    &lt;option value="us"&gt;United States&lt;/option&gt;
    &lt;option value="ca"&gt;Canada&lt;/option&gt;
    &lt;option value="mx"&gt;Mexico&lt;/option&gt;
    &lt;option value="br"&gt;Brazil&lt;/option&gt;
  &lt;/optgroup&gt;

  &lt;optgroup label="Europe"&gt;
    &lt;option value="uk"&gt;United Kingdom&lt;/option&gt;
    &lt;option value="de"&gt;Germany&lt;/option&gt;
    &lt;option value="fr"&gt;France&lt;/option&gt;
  &lt;/optgroup&gt;

  &lt;optgroup label="Asia Pacific"&gt;
    &lt;option value="jp"&gt;Japan&lt;/option&gt;
    &lt;option value="kr"&gt;South Korea&lt;/option&gt;
    &lt;option value="au"&gt;Australia&lt;/option&gt;
  &lt;/optgroup&gt;
&lt;/select&gt;</code></pre>

<p><strong>Key facts:</strong></p>
<ul>
  <li><strong>The <code>label</code> attribute</strong> on <code>&lt;optgroup&gt;</code> sets the visible group header text.</li>
  <li><strong>Group headers are non-selectable</strong> &mdash; clicking does nothing; they exist purely as visual separators.</li>
  <li><strong>Browser styling is fixed</strong> &mdash; native rendering varies (some bold, some indented, some both); CSS styling of <code>&lt;optgroup&gt;</code> and <code>&lt;option&gt;</code> is extremely limited.</li>
  <li><strong>Cannot nest optgroups</strong> &mdash; one level of grouping only; the spec forbids nesting.</li>
  <li><strong>Can disable a whole group</strong> with <code>&lt;optgroup label="..." disabled&gt;</code>.</li>
</ul>

<p><strong>Disabled groups</strong>:</p>
<pre><code>&lt;select&gt;
  &lt;optgroup label="Available now"&gt;
    &lt;option&gt;Plan A&lt;/option&gt;
    &lt;option&gt;Plan B&lt;/option&gt;
  &lt;/optgroup&gt;

  &lt;optgroup label="Coming soon" disabled&gt;
    &lt;option&gt;Plan C (June)&lt;/option&gt;
    &lt;option&gt;Plan D (July)&lt;/option&gt;
  &lt;/optgroup&gt;
&lt;/select&gt;</code></pre>

<p><strong>Accessibility benefits:</strong></p>
<ul>
  <li>Screen readers announce the group label when navigating into a new group: &ldquo;Americas, group, United States, option, 1 of 4.&rdquo;</li>
  <li>Visually scannable &mdash; users find their region quickly in a 200-country list.</li>
</ul>

<p><strong>Limitations and alternatives:</strong></p>
<ul>
  <li><strong>Cannot style</strong> &mdash; fonts, colors, padding mostly ignored. Browsers handle <code>&lt;select&gt;</code> rendering natively for OS consistency.</li>
  <li><strong>Cannot search</strong> &mdash; native <code>&lt;select&gt;</code> only matches by typing the first letter; for searchable dropdowns use a custom combobox or a library (Choices.js, react-select, downshift).</li>
  <li><strong>Cannot include images or rich content</strong> in options &mdash; plain text only.</li>
</ul>

<p>For most cases, native <code>&lt;optgroup&gt;</code> is sufficient and more accessible than custom alternatives. Reach for libraries only when the use case truly needs search, multi-select with chips, or rich item content.</p>
'''

ANSWERS[58] = r'''
<p>HTML doesn&rsquo;t have a native <code>tooltip</code> attribute, but the <code>title</code> attribute provides browser-rendered tooltips. They&rsquo;re inconsistent across platforms, often inaccessible to keyboard users, and impossible to style &mdash; so most production apps build custom CSS-based tooltips.</p>

<p><strong>Native <code>title</code> attribute</strong> &mdash; basic, free, but limited:</p>
<pre><code>&lt;button title="Save your changes (Ctrl+S)"&gt;Save&lt;/button&gt;
&lt;abbr title="HyperText Markup Language"&gt;HTML&lt;/abbr&gt;</code></pre>

<p>Hovering shows a system tooltip after a delay. Problems: appears only on hover (no keyboard access), styling is browser-controlled, can&rsquo;t contain rich content, screen readers may or may not announce it.</p>

<p><strong>CSS-only tooltip</strong> &mdash; pure HTML/CSS, no JavaScript:</p>
<pre><code>&lt;span class="tooltip" data-tooltip="More info about this item"&gt;
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
  .tooltip:hover::after,
  .tooltip:focus-visible::after {
    opacity: 1;
    transform: translateX(-50%) translateY(-8px);
  }
&lt;/style&gt;</code></pre>

<p><strong>Modern accessible solution: Popover API</strong> (2026 baseline):</p>
<pre><code>&lt;button popovertarget="tip1" aria-describedby="tip1"&gt;
  Help
&lt;/button&gt;
&lt;div id="tip1" popover="hint"&gt;
  &lt;p&gt;Click to undo your last action.&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  [popover] {
    background: #333;
    color: white;
    padding: 0.5em 1em;
    border-radius: 4px;
    border: none;
  }
&lt;/style&gt;</code></pre>

<p>The Popover API gives you a tooltip with proper focus management, dismiss-on-Escape, top-layer rendering (no z-index battles), and the ability to position with CSS Anchor Positioning.</p>

<p><strong>Accessibility checklist for any tooltip:</strong></p>
<ul>
  <li>Triggerable on focus, not just hover &mdash; keyboard users need access.</li>
  <li>Dismissible with Escape (Popover API does this for free).</li>
  <li>Use <code>aria-describedby</code> linking the trigger to the tooltip&rsquo;s id, so screen readers announce it.</li>
  <li>Don&rsquo;t hide critical info inside tooltips &mdash; touch users (no hover) miss it.</li>
</ul>

<p>For complex tooltip needs (chained tooltips, follow-cursor, on-demand positioning), libraries like Floating UI (formerly Popper.js) or Tippy.js handle edge cases &mdash; but the platform now covers ~90% of use cases natively.</p>
'''

ANSWERS[59] = r'''
<p>The <code>&lt;kbd&gt;</code> element marks <strong>user input the reader should type</strong> &mdash; keyboard keys, key combinations, voice commands, or anything the user must enter. Browsers render it in monospace by default, signaling "this is a key or command."</p>

<pre><code>&lt;p&gt;Press &lt;kbd&gt;Enter&lt;/kbd&gt; to submit.&lt;/p&gt;

&lt;p&gt;Save the file with &lt;kbd&gt;Ctrl&lt;/kbd&gt; + &lt;kbd&gt;S&lt;/kbd&gt;
   (or &lt;kbd&gt;Cmd&lt;/kbd&gt; + &lt;kbd&gt;S&lt;/kbd&gt; on macOS).&lt;/p&gt;

&lt;p&gt;In the terminal, type &lt;kbd&gt;npm install&lt;/kbd&gt; and press
   &lt;kbd&gt;Enter&lt;/kbd&gt;.&lt;/p&gt;</code></pre>

<p><strong>Combinations using nested <code>&lt;kbd&gt;</code>:</strong></p>
<pre><code>&lt;p&gt;Open dev tools with &lt;kbd&gt;&lt;kbd&gt;Ctrl&lt;/kbd&gt; + &lt;kbd&gt;Shift&lt;/kbd&gt; + &lt;kbd&gt;I&lt;/kbd&gt;&lt;/kbd&gt;.&lt;/p&gt;</code></pre>

<p>The outer <code>&lt;kbd&gt;</code> wraps the entire chord; inner ones mark each individual key. Useful for documentation generators that style chords differently.</p>

<p><strong>Custom styling like real keys:</strong></p>
<pre><code>kbd {
  display: inline-block;
  padding: 0.15em 0.5em;
  font-family: ui-monospace, monospace;
  font-size: 0.85em;
  background: linear-gradient(180deg, #fff 0%, #e8e8e8 100%);
  border: 1px solid #aaa;
  border-radius: 4px;
  box-shadow:
    0 1px 0 #aaa,
    inset 0 -1px 0 rgba(0,0,0,0.1);
  color: #333;
  margin: 0 0.1em;
}</code></pre>

<p>This gives a 3D pressed-key look that documentation sites (MDN, Stripe) commonly use.</p>

<p><strong>Family of inline code-related semantic elements</strong>:</p>
<table>
  <tr><th>Tag</th><th>Means</th><th>Example</th></tr>
  <tr><td><code>&lt;code&gt;</code></td><td>Source code</td><td>Use <code>&lt;code&gt;Array.map()&lt;/code&gt;</code></td></tr>
  <tr><td><code>&lt;kbd&gt;</code></td><td>Keyboard input</td><td>Press <code>&lt;kbd&gt;Esc&lt;/kbd&gt;</code></td></tr>
  <tr><td><code>&lt;samp&gt;</code></td><td>Sample output from program</td><td>Output: <code>&lt;samp&gt;Hello, World!&lt;/samp&gt;</code></td></tr>
  <tr><td><code>&lt;var&gt;</code></td><td>Variable in math/code</td><td>Solve for <code>&lt;var&gt;x&lt;/var&gt;</code></td></tr>
</table>

<p>These four tags pair conceptually:</p>
<pre><code>&lt;p&gt;Run &lt;kbd&gt;node app.js&lt;/kbd&gt; in the terminal.
The output will be:
&lt;samp&gt;Server listening on port 3000&lt;/samp&gt;.&lt;/p&gt;</code></pre>

<p><code>&lt;kbd&gt;</code> for what the user types, <code>&lt;samp&gt;</code> for what the program prints back.</p>

<p><strong>Accessibility note:</strong> screen readers don&rsquo;t typically distinguish <code>&lt;kbd&gt;</code> from regular text aurally &mdash; the content matters. The semantic tag mostly helps documentation tooling and CSS targeting; the visible styling carries most of the meaning to users.</p>
'''

ANSWERS[60] = r'''
<p>The Web Storage API gives every origin two <strong>persistent key-value stores</strong> accessible from JavaScript &mdash; a vastly simpler alternative to cookies for client-side data that doesn&rsquo;t need to be sent to the server.</p>

<p><strong>The two stores:</strong></p>
<table>
  <tr><th></th><th><code>localStorage</code></th><th><code>sessionStorage</code></th></tr>
  <tr><td>Lifetime</td><td>Persistent &mdash; survives browser restarts</td><td>Cleared when tab closes</td></tr>
  <tr><td>Scope</td><td>Per origin (protocol + host + port)</td><td>Per tab + origin</td></tr>
  <tr><td>Storage limit</td><td>~5-10 MB per origin</td><td>Same</td></tr>
  <tr><td>Sent with requests</td><td>No (unlike cookies)</td><td>No</td></tr>
</table>

<p><strong>Same API for both:</strong></p>
<pre><code>// Set
localStorage.setItem("theme", "dark");
localStorage.theme = "dark";       // alternate syntax (subscript)

// Get
const theme = localStorage.getItem("theme");      // "dark"

// Remove a single key
localStorage.removeItem("theme");

// Clear everything
localStorage.clear();

// Iterate
for (let i = 0; i &lt; localStorage.length; i++) {
  const key = localStorage.key(i);
  console.log(key, localStorage.getItem(key));
}</code></pre>

<p><strong>Storing complex data</strong> &mdash; values are always strings, so JSON-encode objects:</p>
<pre><code>const prefs = { theme: "dark", lang: "en", fontSize: 16 };

localStorage.setItem("prefs", JSON.stringify(prefs));

const restored = JSON.parse(localStorage.getItem("prefs") || "{}");</code></pre>

<p><strong>Listening for changes from other tabs</strong> (localStorage broadcasts):</p>
<pre><code>window.addEventListener("storage", (event) =&gt; {
  if (event.key === "theme") {
    applyTheme(event.newValue);
  }
});</code></pre>

<p>If the user changes the theme in one tab, all other tabs from the same origin receive a <code>storage</code> event &mdash; great for syncing UI across tabs without round-tripping the server.</p>

<p><strong>What to store and what NOT to store:</strong></p>
<table>
  <tr><th>OK</th><th>NOT OK</th></tr>
  <tr><td>UI preferences (theme, font size)</td><td>Auth tokens (XSS-vulnerable; use httpOnly cookies)</td></tr>
  <tr><td>Form drafts</td><td>Personal data (PII)</td></tr>
  <tr><td>Cache of small public data</td><td>Encryption keys</td></tr>
  <tr><td>Recently-viewed items</td><td>Anything you wouldn&rsquo;t want a third-party script to read</td></tr>
</table>

<p><strong>Critical security note:</strong> any JavaScript on the page can read all localStorage. If your site has an XSS vulnerability or includes any untrusted third-party script, all stored data leaks. Auth tokens belong in <code>HttpOnly</code> cookies (which JS can&rsquo;t read), not in localStorage.</p>

<p><strong>For larger or structured data, use IndexedDB:</strong></p>
<ul>
  <li>Megabytes to gigabytes of storage (vs ~5MB for localStorage).</li>
  <li>Indexable, queryable, transactional.</li>
  <li>Asynchronous (doesn&rsquo;t block the main thread).</li>
  <li>Wrappers like Dexie or idb make the API friendlier.</li>
</ul>
'''

ANSWERS[61] = r'''
<p>Both APIs share the exact same interface but differ in <strong>scope and lifetime</strong> &mdash; the difference often determines which one you should use.</p>

<table>
  <tr><th></th><th><code>sessionStorage</code></th><th><code>localStorage</code></th></tr>
  <tr><td>Lifetime</td><td>Until the tab closes</td><td>Until manually cleared (or browser settings clear it)</td></tr>
  <tr><td>Scope</td><td>Per tab AND per origin</td><td>Per origin (shared across tabs)</td></tr>
  <tr><td>Survives reload</td><td>Yes</td><td>Yes</td></tr>
  <tr><td>Survives tab close</td><td>No</td><td>Yes</td></tr>
  <tr><td>Survives browser close</td><td>No</td><td>Yes</td></tr>
  <tr><td>Shared between tabs</td><td>No (unless duplicated tab)</td><td>Yes (same origin)</td></tr>
  <tr><td>storage event fires in other tabs</td><td>No</td><td>Yes</td></tr>
</table>

<p><strong>Concrete behavior comparison:</strong></p>
<pre><code>// Tab A: example.com
localStorage.setItem("user", "alice");
sessionStorage.setItem("scratch", "tabA-only");

// Tab B: example.com (open in new tab)
console.log(localStorage.getItem("user"));        // "alice" — shared!
console.log(sessionStorage.getItem("scratch"));   // null — private to Tab A

// User closes Tab A
// localStorage in Tab B still has "alice"
// sessionStorage from Tab A is gone forever</code></pre>

<p><strong>When to use sessionStorage:</strong></p>
<ul>
  <li><strong>Multi-step form state</strong> &mdash; preserve progress across page navigation in one tab; lose it when the user closes the tab (finishes or abandons).</li>
  <li><strong>Per-tab scratch space</strong> &mdash; if the same user opens two product comparison flows in different tabs, each tab&rsquo;s data should stay isolated.</li>
  <li><strong>Sensitive temporary data</strong> &mdash; reduces exposure window; vanishes when the tab closes.</li>
  <li><strong>Tab-specific UI state</strong> &mdash; selected tab in a sidebar; should reset on new visit.</li>
</ul>

<p><strong>When to use localStorage:</strong></p>
<ul>
  <li><strong>User preferences</strong> &mdash; theme, language, font size that should persist forever.</li>
  <li><strong>Cached data</strong> &mdash; recently-viewed items, draft messages.</li>
  <li><strong>Logged-in UI hints</strong> &mdash; "completed onboarding" flag, dismissed banners.</li>
  <li><strong>Cross-tab sync</strong> &mdash; the <code>storage</code> event fires in other tabs when localStorage changes; useful for keeping state consistent.</li>
</ul>

<p><strong>The "duplicated tab" gotcha:</strong> if a user duplicates a tab (Ctrl+Click in some browsers), the new tab inherits the original&rsquo;s sessionStorage as a one-time copy. After that, they diverge &mdash; changes in either don&rsquo;t affect the other.</p>

<p><strong>Same security considerations apply to both:</strong> any JavaScript on the page can read all the data. Don&rsquo;t put auth tokens, passwords, or sensitive PII in either. Use <code>HttpOnly</code> cookies for auth.</p>

<p>If you find yourself wanting "share between tabs but vanish on close" or "per-tab but persistent," neither API fits cleanly &mdash; you need IndexedDB plus your own cleanup logic, or a backend with sessions. The Web Storage API was designed for the simple cases.</p>
'''

ANSWERS[62] = r'''
<p>A collapsible sidebar slides in/out on toggle. The cleanest pattern is CSS-only using a checkbox toggle &mdash; no JavaScript &mdash; with a JS-enhanced version for production accessibility.</p>

<p><strong>JavaScript version with proper accessibility:</strong></p>
<pre><code>&lt;button id="sidebarBtn"
        aria-controls="sidebar"
        aria-expanded="true"
        aria-label="Toggle sidebar"&gt;
  &lt;svg width="24" height="24"&gt;...&lt;/svg&gt;
&lt;/button&gt;

&lt;aside id="sidebar" class="sidebar"&gt;
  &lt;nav aria-label="Main"&gt;
    &lt;ul&gt;
      &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
      &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
  &lt;/nav&gt;
&lt;/aside&gt;

&lt;script&gt;
  const btn  = document.getElementById("sidebarBtn");
  const side = document.getElementById("sidebar");

  btn.addEventListener("click", () =&gt; {
    const isOpen = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!isOpen));
    side.classList.toggle("collapsed", isOpen);

    // Remember preference across reloads
    localStorage.setItem("sidebarCollapsed", String(isOpen));
  });

  // Restore saved state
  if (localStorage.getItem("sidebarCollapsed") === "true") {
    btn.setAttribute("aria-expanded", "false");
    side.classList.add("collapsed");
  }
&lt;/script&gt;

&lt;style&gt;
  .sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 1em;
    transition: width 0.3s, transform 0.3s;
    overflow: hidden;
  }
  .sidebar.collapsed {
    width: 60px;
  }
  .sidebar.collapsed .label {
    display: none;   /* hide text in collapsed mode */
  }
&lt;/style&gt;</code></pre>

<p><strong>Mobile considerations:</strong></p>
<ul>
  <li><strong>Overlay vs push</strong> &mdash; mobile sidebars often overlay the content (above) rather than pushing it (beside). Use <code>position: fixed</code> + <code>z-index</code> on mobile.</li>
  <li><strong>Backdrop dim</strong> &mdash; when open, dim the rest of the screen so users see what&rsquo;s focused.</li>
  <li><strong>Touch swipe to close</strong> &mdash; libraries handle this; vanilla requires <code>touchstart</code> / <code>touchmove</code> tracking.</li>
  <li><strong>Body scroll lock</strong> &mdash; prevent the underlying page from scrolling while the sidebar is open.</li>
</ul>

<p><strong>Accessibility checklist:</strong></p>
<ul>
  <li>Toggle button has <code>aria-controls</code> linking to the sidebar id.</li>
  <li><code>aria-expanded</code> reflects current state, updated on toggle.</li>
  <li>Sidebar has <code>aria-label</code> or contains a labeled <code>&lt;nav&gt;</code>.</li>
  <li>Focus moves into the sidebar when opened (if it&rsquo;s a modal-style overlay).</li>
  <li><code>Escape</code> key closes the sidebar.</li>
  <li>Trap focus inside the sidebar when modal-overlaying on mobile.</li>
</ul>

<p>Libraries like Headless UI and Radix Navigation Menu handle the full accessibility model for collapsible navigation patterns &mdash; saving days of work on edge cases.</p>
'''

ANSWERS[63] = r'''
<p>The <code>&lt;base&gt;</code> element specifies a <strong>default base URL and target for all relative URLs in a page</strong>. It must be in <code>&lt;head&gt;</code>, can appear at most once, and affects every link, image, form action, and resource reference that uses a relative URL.</p>

<pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
  &lt;base href="https://api.example.com/v2/"
        target="_blank"&gt;
&lt;/head&gt;
&lt;body&gt;
  &lt;!-- These resolve relative to https://api.example.com/v2/ --&gt;
  &lt;a href="docs"&gt;Docs&lt;/a&gt;          &lt;!-- → https://api.example.com/v2/docs --&gt;
  &lt;img src="logo.png"&gt;            &lt;!-- → https://api.example.com/v2/logo.png --&gt;
  &lt;link href="style.css"&gt;          &lt;!-- → https://api.example.com/v2/style.css --&gt;

  &lt;!-- Absolute URLs are unaffected --&gt;
  &lt;a href="https://other.com/x"&gt;External&lt;/a&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>

<p><strong>The two attributes:</strong></p>
<table>
  <tr><th>Attribute</th><th>Effect</th></tr>
  <tr><td><code>href</code></td><td>Base URL for resolving relative URLs</td></tr>
  <tr><td><code>target</code></td><td>Default <code>target</code> for all <code>&lt;a&gt;</code> and <code>&lt;form&gt;</code> elements</td></tr>
</table>

<p><strong>Common use cases:</strong></p>
<ul>
  <li><strong>Documentation copies</strong> &mdash; a single HTML file viewed on disk and on a web server, where you want all internal links to resolve to the production URL.</li>
  <li><strong>Email templates</strong> &mdash; force all relative URLs to load images from a CDN.</li>
  <li><strong>Single-Page Apps with deep paths</strong> &mdash; set the base so client-side router relative URLs resolve correctly.</li>
  <li><strong>Open all links in new tabs</strong> &mdash; <code>&lt;base target="_blank"&gt;</code> applies to every link automatically.</li>
</ul>

<p><strong>Why it&rsquo;s rarely used:</strong></p>
<ul>
  <li><strong>Affects everything</strong> &mdash; one base URL applies to <em>every</em> relative URL on the page. Easy to break unintended things.</li>
  <li><strong>Anchor links break</strong> &mdash; <code>&lt;a href="#section"&gt;</code> resolves to <code>BASE/page#section</code> instead of the current page&rsquo;s anchor. You must use absolute URLs for fragment links: <code>&lt;a href="page#section"&gt;</code>.</li>
  <li><strong>Form actions affected</strong> &mdash; relative <code>action</code> URLs resolve against the base, which may surprise developers.</li>
  <li><strong>Dynamic content struggles</strong> &mdash; once the base is set, JavaScript-injected URLs need to account for it.</li>
</ul>

<p><strong>SPA frameworks</strong> use <code>&lt;base&gt;</code> commonly:</p>
<pre><code>&lt;!-- Angular: app served from a sub-path --&gt;
&lt;base href="/admin/"&gt;</code></pre>

<p>Angular requires this for its router to work when the app is hosted at a sub-path. React Router and Vue Router can work without it but accept similar configuration.</p>

<p><strong>Modern alternatives:</strong> use absolute URLs everywhere, or use a build tool that rewrites relative paths during build (Vite, Webpack handle this with <code>publicPath</code>). The <code>&lt;base&gt;</code> element solves a real problem but introduces enough surprises that most modern apps avoid it.</p>
'''

ANSWERS[64] = r'''
<p>The <code>action</code> attribute on <code>&lt;form&gt;</code> specifies the URL where the form data is sent on submit. Combined with <code>method</code> and <code>enctype</code>, it forms the contract between the browser and your server.</p>

<pre><code>&lt;form action="/api/users"
      method="post"
      enctype="application/x-www-form-urlencoded"&gt;
  &lt;input name="email" type="email" required&gt;
  &lt;input name="name" type="text" required&gt;
  &lt;button type="submit"&gt;Sign up&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p>Submitting POSTs <code>email=...&amp;name=...</code> to <code>/api/users</code>.</p>

<p><strong>URL types accepted in <code>action</code>:</strong></p>
<ul>
  <li><strong>Absolute</strong>: <code>https://api.example.com/users</code> &mdash; sends to a different origin.</li>
  <li><strong>Root-relative</strong>: <code>/api/users</code> &mdash; same protocol/host as the page.</li>
  <li><strong>Path-relative</strong>: <code>users</code> &mdash; resolves against the current page&rsquo;s URL or any <code>&lt;base&gt;</code> tag.</li>
  <li><strong>Empty / omitted</strong>: defaults to the current page URL (form submits to itself).</li>
</ul>

<p><strong>Method choices:</strong></p>
<table>
  <tr><th>Method</th><th>Behavior</th></tr>
  <tr><td><code>get</code></td><td>Data appended to URL as query string. Cacheable, bookmarkable. Visible in URL/logs.</td></tr>
  <tr><td><code>post</code></td><td>Data in request body. Not bookmarkable. Required for files and large data.</td></tr>
  <tr><td><code>dialog</code></td><td>Closes a parent <code>&lt;dialog&gt;</code> element with the submit button&rsquo;s value as <code>returnValue</code>. No HTTP request.</td></tr>
</table>

<p><strong>Per-button overrides</strong> &mdash; submit buttons can override the form&rsquo;s action:</p>
<pre><code>&lt;form action="/posts" method="post"&gt;
  &lt;input name="title"&gt;
  &lt;textarea name="body"&gt;&lt;/textarea&gt;

  &lt;button type="submit"&gt;Publish&lt;/button&gt;

  &lt;button type="submit"
          formaction="/posts/draft"&gt;Save draft&lt;/button&gt;

  &lt;button type="submit"
          formaction="/posts/preview"
          formtarget="_blank"&gt;Preview&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p>Three submit buttons, three different endpoints, one form &mdash; no JavaScript needed.</p>

<p><strong>Modern approach with JavaScript:</strong> for most app interactions, intercept the submit and use <code>fetch</code> instead:</p>
<pre><code>form.addEventListener("submit", async (e) =&gt; {
  e.preventDefault();
  const fd = new FormData(form);
  const res = await fetch(form.action, {
    method: form.method,
    body: fd,
  });
  if (res.ok) showSuccess();
  else        showError();
});</code></pre>

<p>This gives you progress indicators, error handling, partial-page updates, and toast notifications &mdash; impossible with native form submission&rsquo;s page reload.</p>

<p><strong>Progressive enhancement</strong> &mdash; the form works without JavaScript (browser submits to action) AND with JavaScript (fetch handles it). Critical for accessibility, slow networks, and reliability.</p>

<p><strong>Same-origin restrictions:</strong> POSTing to a different origin works but the browser may not send cookies (depends on <code>credentials</code> mode in fetch, or the form&rsquo;s rendering context). For cross-origin APIs, configure CORS on the server side.</p>
'''

ANSWERS[65] = r'''
<p>The <code>&lt;noscript&gt;</code> element provides <strong>fallback content for browsers (or users) with JavaScript disabled</strong>. Anything inside <code>&lt;noscript&gt;</code> is only displayed when scripting isn&rsquo;t available.</p>

<pre><code>&lt;noscript&gt;
  &lt;div class="warning"&gt;
    &lt;p&gt;This site requires JavaScript to function fully.&lt;/p&gt;
    &lt;p&gt;Please &lt;a href="https://enable-javascript.com"&gt;enable JavaScript&lt;/a&gt;
       in your browser settings or use a different browser.&lt;/p&gt;
  &lt;/div&gt;
&lt;/noscript&gt;</code></pre>

<p><strong>What triggers <code>&lt;noscript&gt;</code> to render:</strong></p>
<ul>
  <li>JavaScript is disabled in browser settings.</li>
  <li>JavaScript is blocked by an extension (NoScript, uBlock).</li>
  <li>The browser doesn&rsquo;t support JavaScript at all (extremely rare).</li>
  <li>JavaScript fails to load or parse (network failure, syntax error blocking the bundle).</li>
</ul>

<p><strong>When JavaScript IS available, content inside <code>&lt;noscript&gt;</code> is parsed but not displayed</strong> &mdash; it sits in the DOM but with <code>display: none</code> applied by user-agent CSS.</p>

<p><strong>Common uses:</strong></p>
<table>
  <tr><th>Use case</th><th>Pattern</th></tr>
  <tr><td>Friendly error message</td><td>"Please enable JavaScript"</td></tr>
  <tr><td>Server-rendered fallback</td><td>Show a basic version of the UI</td></tr>
  <tr><td>Privacy-conscious analytics</td><td><code>&lt;noscript&gt;&lt;img src="track.gif?id=..."&gt;&lt;/noscript&gt;</code></td></tr>
</table>

<p><strong>Use sparingly &mdash; better alternatives exist:</strong></p>

<p><strong>1. CSS-based progressive enhancement</strong> &mdash; modern preferred approach:</p>
<pre><code>&lt;html class="no-js"&gt;
&lt;head&gt;
  &lt;script&gt;
    // Replace no-js with js as soon as JS runs
    document.documentElement.className = document.documentElement.className.replace("no-js", "js");
  &lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
  &lt;button class="js-only"&gt;Only shown with JS&lt;/button&gt;
  &lt;p class="no-js-only"&gt;Only shown without JS&lt;/p&gt;

  &lt;style&gt;
    .js .no-js-only { display: none; }
    .no-js .js-only { display: none; }
  &lt;/style&gt;
&lt;/body&gt;</code></pre>

<p>This pattern is more flexible than <code>&lt;noscript&gt;</code> &mdash; CSS rules can hide many elements with one class, and you can show different content per state without duplication.</p>

<p><strong>2. Server-side rendering</strong> &mdash; for content that absolutely must work without JS, render it as static HTML on the server. Frameworks like Next.js, Astro, and Remix do this by default.</p>

<p><strong>Caveats and gotchas:</strong></p>
<ul>
  <li><strong>Doesn&rsquo;t handle &ldquo;JavaScript is loading&rdquo; case</strong> &mdash; the user might briefly see your "JavaScript required" message before your bundle loads. Use the <code>html.no-js</code> trick to avoid this flash.</li>
  <li><strong>Inside <code>&lt;head&gt;</code>, <code>&lt;noscript&gt;</code> can only contain <code>&lt;link&gt;</code>, <code>&lt;style&gt;</code>, and <code>&lt;meta&gt;</code></strong> &mdash; useful for loading non-JS-deferred styles.</li>
  <li><strong>JavaScript-disabled users are extremely rare in 2026</strong> &mdash; estimated &lt;1% of total visits, often automated scrapers or accessibility tools that you should support via semantic HTML, not JS-required UI.</li>
</ul>

<p><strong>Modern philosophy:</strong> build the site so it works without JavaScript at all (server-rendered HTML, real form submissions, links to navigate). Then enhance with JavaScript for richer interactions. <code>&lt;noscript&gt;</code> becomes unnecessary because the no-JS experience is just a slightly less polished version of the JS experience &mdash; not a blocking error message.</p>
'''

ANSWERS[66] = r'''
<p>A flexbox-based responsive image gallery flows naturally across screen sizes &mdash; images wrap onto new rows as the container narrows, with consistent gaps and aspect ratios.</p>

<pre><code>&lt;section class="gallery"&gt;
  &lt;figure&gt;
    &lt;img src="img1.jpg" alt="Forest path in autumn" loading="lazy"&gt;
    &lt;figcaption&gt;Autumn forest&lt;/figcaption&gt;
  &lt;/figure&gt;
  &lt;figure&gt;
    &lt;img src="img2.jpg" alt="Mountain reflection in lake" loading="lazy"&gt;
    &lt;figcaption&gt;Mirror lake&lt;/figcaption&gt;
  &lt;/figure&gt;
  &lt;figure&gt;
    &lt;img src="img3.jpg" alt="Coastal cliff at sunset" loading="lazy"&gt;
    &lt;figcaption&gt;Coastal sunset&lt;/figcaption&gt;
  &lt;/figure&gt;
  &lt;figure&gt;
    &lt;img src="img4.jpg" alt="City skyline at night" loading="lazy"&gt;
    &lt;figcaption&gt;Night skyline&lt;/figcaption&gt;
  &lt;/figure&gt;
&lt;/section&gt;

&lt;style&gt;
  .gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }
  .gallery figure {
    flex: 1 1 250px;          /* grow, shrink, basis */
    margin: 0;
    overflow: hidden;
    border-radius: 8px;
    background: #f0f0f0;
  }
  .gallery img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
    transition: transform 0.3s;
  }
  .gallery figure:hover img {
    transform: scale(1.05);
  }
  .gallery figcaption {
    padding: 0.5em;
    text-align: center;
    color: #555;
    font-size: 0.9em;
  }
&lt;/style&gt;</code></pre>

<p><strong>The key flex shorthand:</strong></p>
<pre><code>flex: 1 1 250px;
/* equivalent to: */
flex-grow: 1;        /* fill available space */
flex-shrink: 1;      /* shrink if needed */
flex-basis: 250px;   /* preferred width */</code></pre>

<p>Each item starts at 250px wide; if there&rsquo;s extra space, items grow equally to fill it; if there&rsquo;s not enough room, items wrap to a new line. The result: 4 columns on wide screens, 3 on tablet, 2 on phone, 1 on tiny screens &mdash; all from one rule.</p>

<p><strong>Object-fit ensures consistent appearance</strong> regardless of source image dimensions:</p>
<pre><code>img {
  width: 100%;
  height: 200px;
  object-fit: cover;     /* crops to fill the box, preserving aspect ratio */
  /* alternatives:
     contain — fit entirely, may letterbox
     fill    — stretch to fill exactly (distorts)
     none    — no scaling
   */
}</code></pre>

<p><strong>CSS Grid alternative</strong> for cases where Flexbox feels limiting:</p>
<pre><code>.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}</code></pre>

<p>Grid version: same responsive behavior with a clearer semantic. Flex preserves item order more naturally; Grid gives stronger alignment control. For galleries, both work &mdash; pick whichever syntax feels clearer.</p>

<p><strong>Performance must-haves:</strong></p>
<ul>
  <li><code>loading="lazy"</code> on all but the first row of images.</li>
  <li>Use <code>srcset</code> with multiple resolutions so phones don&rsquo;t download desktop-sized images.</li>
  <li>Modern formats (AVIF, WebP) save 30-70% bandwidth.</li>
  <li>Set <code>width</code> and <code>height</code> attributes so the browser reserves space and doesn&rsquo;t cause layout shift as images load.</li>
</ul>

<p>For lightbox/zoom on click, libraries like PhotoSwipe handle pinch-zoom and swipe gestures.</p>
'''

ANSWERS[67] = r'''
<p><code>&lt;sub&gt;</code> renders subscript (text below the baseline); <code>&lt;sup&gt;</code> renders superscript (text above). They&rsquo;re semantic &mdash; meaning "this is mathematically or chemically a subscript/superscript" &mdash; not just visual styling.</p>

<pre><code>&lt;p&gt;The chemical formula for water is H&lt;sub&gt;2&lt;/sub&gt;O.&lt;/p&gt;

&lt;p&gt;Caffeine is C&lt;sub&gt;8&lt;/sub&gt;H&lt;sub&gt;10&lt;/sub&gt;N&lt;sub&gt;4&lt;/sub&gt;O&lt;sub&gt;2&lt;/sub&gt;.&lt;/p&gt;

&lt;p&gt;Einstein&rsquo;s famous equation: E = mc&lt;sup&gt;2&lt;/sup&gt;.&lt;/p&gt;

&lt;p&gt;The 4&lt;sup&gt;th&lt;/sup&gt; of July is American Independence Day.&lt;/p&gt;

&lt;p&gt;See section 2&lt;sup&gt;[1]&lt;/sup&gt; for details.&lt;/p&gt;</code></pre>

<p><strong>Default styling</strong> &mdash; both elements use <code>vertical-align: sub</code> or <code>super</code>, slightly smaller font size, and renders inline:</p>
<pre><code>sub, sup {
  font-size: 75%;
  line-height: 0;
  position: relative;
  vertical-align: baseline;
}
sub { bottom: -0.25em; }
sup { top: -0.5em; }</code></pre>

<p><strong>Common use cases:</strong></p>
<table>
  <tr><th>Use case</th><th>Tag</th></tr>
  <tr><td>Chemical formulas (H<sub>2</sub>O)</td><td><code>&lt;sub&gt;</code></td></tr>
  <tr><td>Math indices, sequences (a<sub>1</sub>, a<sub>2</sub>)</td><td><code>&lt;sub&gt;</code></td></tr>
  <tr><td>Exponents (x<sup>2</sup>, 10<sup>6</sup>)</td><td><code>&lt;sup&gt;</code></td></tr>
  <tr><td>Ordinals (1<sup>st</sup>, 2<sup>nd</sup>)</td><td><code>&lt;sup&gt;</code></td></tr>
  <tr><td>Footnote references</td><td><code>&lt;sup&gt;</code></td></tr>
  <tr><td>Trademark / copyright marks</td><td><code>&lt;sup&gt;</code> for &reg; or &trade;</td></tr>
</table>

<p><strong>Footnote pattern:</strong></p>
<pre><code>&lt;p&gt;The discovery&lt;sup&gt;&lt;a href="#fn1" id="fnref1"&gt;[1]&lt;/a&gt;&lt;/sup&gt;
   was groundbreaking.&lt;/p&gt;

&lt;footer&gt;
  &lt;ol&gt;
    &lt;li id="fn1"&gt;
      Smith et al., &lt;cite&gt;Nature&lt;/cite&gt;, 2024.
      &lt;a href="#fnref1"&gt;&#8617;&lt;/a&gt;
    &lt;/li&gt;
  &lt;/ol&gt;
&lt;/footer&gt;</code></pre>

<p>The <code>&lt;sup&gt;</code> wraps the visual indicator; the link inside provides accessible navigation to and from the footnote.</p>

<p><strong>Accessibility considerations:</strong></p>
<ul>
  <li>Screen readers usually read <code>&lt;sub&gt;</code> and <code>&lt;sup&gt;</code> content inline without special announcement &mdash; H<sub>2</sub>O is read as "H 2 O," ideally without indicating the visual position.</li>
  <li>This is generally fine for chemistry and math &mdash; the meaning comes from context.</li>
  <li>For superscript footnote references, ensure the link text and surrounding context make the purpose clear.</li>
</ul>

<p><strong>Don&rsquo;t use <code>&lt;sub&gt;</code> / <code>&lt;sup&gt;</code> for purely stylistic effects</strong> &mdash; small caps, callouts, decorative marks. CSS classes with <code>vertical-align</code> work better when there&rsquo;s no semantic meaning. Reserve these tags for actual mathematical, chemical, or numerical-position content.</p>

<p><strong>For complex math, consider MathML</strong> (<code>&lt;math&gt;</code>) or KaTeX/MathJax &mdash; <code>&lt;sub&gt;</code> / <code>&lt;sup&gt;</code> work for simple cases but break down for fractions, integrals, matrices, and complex expressions.</p>
'''

ANSWERS[68] = r'''
<p>A sticky header stays at the top of the viewport as the user scrolls past it. CSS <code>position: sticky</code> makes this trivial &mdash; no JavaScript needed, no fixed positioning quirks, no layout problems.</p>

<pre><code>&lt;header class="site-header"&gt;
  &lt;div class="header-inner"&gt;
    &lt;a href="/" class="logo"&gt;Acme&lt;/a&gt;

    &lt;nav aria-label="Main"&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/div&gt;
&lt;/header&gt;

&lt;main&gt;
  &lt;article&gt;...&lt;/article&gt;
&lt;/main&gt;

&lt;style&gt;
  .site-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: white;
    border-bottom: 1px solid #eee;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  .header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1em;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
&lt;/style&gt;</code></pre>

<p><strong>How <code>position: sticky</code> works:</strong></p>
<ol>
  <li>The element scrolls naturally with the page until its <code>top</code> threshold is reached.</li>
  <li>Once the element would scroll past <code>top: 0</code>, it sticks &mdash; rendering at <code>top: 0</code> while the user keeps scrolling content past it.</li>
  <li>It only sticks <em>within its containing scroll context</em> &mdash; if the parent stops scrolling, the sticky element scrolls with it (off-screen).</li>
</ol>

<p><strong>Sticky vs Fixed comparison:</strong></p>
<table>
  <tr><th></th><th><code>position: sticky</code></th><th><code>position: fixed</code></th></tr>
  <tr><td>Layout</td><td>Takes up space when not sticky</td><td>Removed from flow always</td></tr>
  <tr><td>Scroll behavior</td><td>Scrolls until threshold, then sticks</td><td>Always at fixed viewport position</td></tr>
  <tr><td>Containing block</td><td>Scrolls with parent if parent ends</td><td>Always relative to viewport</td></tr>
  <tr><td>Bottom margin space</td><td>Behaves like normal element</td><td>Content below jumps up</td></tr>
</table>

<p><strong>Common gotchas:</strong></p>
<ul>
  <li><strong>Parent <code>overflow: hidden</code> or <code>overflow: auto</code> breaks sticky</strong> &mdash; the parent becomes a new scroll container, and <code>sticky</code> only sticks within it (often invisibly).</li>
  <li><strong>Parent <code>overflow: clip</code> on a non-scrolling parent</strong> &mdash; same problem.</li>
  <li><strong>Sticky inside flexbox</strong> requires <code>align-self: flex-start</code> on the sticky element to give it room to stick.</li>
  <li><strong>Compact vs expanded</strong> &mdash; common pattern is to shrink the header on scroll using <code>IntersectionObserver</code> or scroll listeners.</li>
</ul>

<p><strong>Detect when the header has stuck</strong> for visual changes:</p>
<pre><code>const observer = new IntersectionObserver(
  ([entry]) =&gt; {
    document.querySelector(".site-header").classList.toggle("is-stuck", !entry.isIntersecting);
  },
  { threshold: 1 },
);
observer.observe(document.querySelector(".sentinel"));   // a 1px element above the header

&lt;style&gt;
  .site-header.is-stuck { padding: 0.5em 1em; }    /* compact when stuck */
&lt;/style&gt;</code></pre>

<p>This pattern shrinks the header gracefully when scrolled, restoring it when scrolled back to the top.</p>
'''

ANSWERS[69] = r'''
<p>Progressive enhancement is a design philosophy that builds content and functionality in <strong>layers of increasing capability</strong>. Start with semantic HTML that works everywhere; layer CSS for presentation; layer JavaScript for interactivity. Each layer enhances but doesn&rsquo;t depend on the next.</p>

<p><strong>The three layers:</strong></p>
<table>
  <tr><th>Layer</th><th>Provides</th><th>Without it</th></tr>
  <tr><td>Semantic HTML</td><td>Content + structure</td><td>Nothing works</td></tr>
  <tr><td>CSS</td><td>Visual design</td><td>Plain unstyled but usable</td></tr>
  <tr><td>JavaScript</td><td>Rich interactions</td><td>Slower but functional</td></tr>
</table>

<p><strong>Concrete example &mdash; a search form:</strong></p>
<pre><code>&lt;!-- Layer 1: works without CSS or JS --&gt;
&lt;form action="/search" method="get" role="search"&gt;
  &lt;label for="q"&gt;Search:&lt;/label&gt;
  &lt;input type="search" id="q" name="q" required&gt;
  &lt;button type="submit"&gt;Search&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p>Without any styling or scripts, this form fully works &mdash; it submits to <code>/search?q=...</code> and the server returns results.</p>

<pre><code>&lt;!-- Layer 2: CSS adds visual polish --&gt;
&lt;style&gt;
  form { display: flex; gap: 0.5em; }
  input { padding: 0.5em; flex: 1; }
  button { background: #0066cc; color: white; padding: 0.5em 1em; }
&lt;/style&gt;</code></pre>

<pre><code>&lt;!-- Layer 3: JS enhances with autocomplete and live results --&gt;
&lt;script&gt;
  const input = document.getElementById("q");
  const results = document.getElementById("results");

  input.addEventListener("input", debounce(async () =&gt; {
    if (input.value.length &lt; 2) return;
    const res = await fetch(`/search?q=${input.value}&amp;json=1`);
    const data = await res.json();
    renderResults(data);
  }, 300));
&lt;/script&gt;</code></pre>

<p>If JavaScript fails or is slow to load, the user submits the form normally and gets a server-rendered results page. If JavaScript works, they get fancy autocomplete and live results &mdash; same content, richer experience.</p>

<p><strong>Why progressive enhancement matters:</strong></p>
<ul>
  <li><strong>Resilience</strong> &mdash; a JS bundle fails to load (rare but happens); a CDN times out; a script throws on parse. The site still works.</li>
  <li><strong>Performance</strong> &mdash; HTML renders before JS executes; users see content faster.</li>
  <li><strong>Accessibility</strong> &mdash; semantic HTML is screen-reader-ready; ARIA + JS layered on top adds richness.</li>
  <li><strong>SEO</strong> &mdash; search engines index static HTML easily; client-rendered apps need extra work to be crawlable.</li>
  <li><strong>Reach</strong> &mdash; older browsers, low-power devices, users with slow connections all benefit.</li>
</ul>

<p><strong>Contrast: graceful degradation</strong> starts from the rich experience and scales down for less capable browsers. Progressive enhancement starts from the basic experience and scales up. Both achieve similar end states, but progressive enhancement is generally more robust because the baseline (semantic HTML) is the most stable foundation.</p>

<p><strong>Modern reality:</strong> the boundary blurs. Frameworks like Next.js, Remix, and Astro do server-side rendering by default &mdash; the HTML arrives before JS hydrates. This is progressive enhancement at the framework level: the page works pre-hydration; JS upgrades it.</p>

<p><strong>Test your progressive enhancement:</strong> disable JavaScript in DevTools and try every workflow. If something breaks, you&rsquo;ve missed a layer. Many SPAs fail this test &mdash; they show a blank screen without JS &mdash; because they skipped the foundation.</p>
'''

ANSWERS[70] = r'''
<p>A responsive video player adapts to different screen sizes while maintaining aspect ratio and offering useful playback controls. The native <code>&lt;video&gt;</code> element does most of the work; CSS handles the responsive sizing.</p>

<pre><code>&lt;figure class="video-wrapper"&gt;
  &lt;video controls
         poster="thumbnail.jpg"
         preload="metadata"
         playsinline&gt;
    &lt;source src="movie.webm" type="video/webm"&gt;
    &lt;source src="movie.mp4" type="video/mp4"&gt;

    &lt;!-- Captions track --&gt;
    &lt;track kind="captions"
           src="captions.en.vtt"
           srclang="en"
           label="English"
           default&gt;

    &lt;p&gt;Your browser doesn&rsquo;t support HTML5 video.
       &lt;a href="movie.mp4"&gt;Download the video&lt;/a&gt;.&lt;/p&gt;
  &lt;/video&gt;
  &lt;figcaption&gt;Product demo &mdash; 2 minutes&lt;/figcaption&gt;
&lt;/figure&gt;

&lt;style&gt;
  .video-wrapper {
    margin: 0;
    aspect-ratio: 16 / 9;
    max-width: 100%;
    background: #000;
  }
  .video-wrapper video {
    width: 100%;
    height: 100%;
    display: block;
  }
&lt;/style&gt;</code></pre>

<p><strong>Key attributes:</strong></p>
<table>
  <tr><th>Attribute</th><th>Purpose</th></tr>
  <tr><td><code>controls</code></td><td>Show native play/pause/volume/fullscreen</td></tr>
  <tr><td><code>poster</code></td><td>Image shown before play (LCP-friendly)</td></tr>
  <tr><td><code>preload="metadata"</code></td><td>Load duration/dimensions only, not full video</td></tr>
  <tr><td><code>playsinline</code></td><td>iOS: play inline instead of fullscreen takeover</td></tr>
  <tr><td><code>muted autoplay</code></td><td>Required combo for autoplay (browsers block sound)</td></tr>
  <tr><td><code>loop</code></td><td>Repeat on finish</td></tr>
</table>

<p><strong>Multiple sources for browser compatibility:</strong></p>
<pre><code>&lt;video controls&gt;
  &lt;source src="video.av1.mp4" type="video/mp4; codecs=av01.0.05M.08"&gt;
  &lt;source src="video.h265.mp4" type="video/mp4; codecs=hvc1"&gt;
  &lt;source src="video.h264.mp4" type="video/mp4"&gt;
&lt;/video&gt;</code></pre>

<p>The browser picks the first source it can decode. AV1 is most efficient (newest), H.265 second, H.264 universal fallback.</p>

<p><strong>Tracks for accessibility</strong> &mdash; WebVTT subtitles/captions:</p>
<pre><code>&lt;track kind="captions" src="en.vtt" srclang="en" label="English"&gt;
&lt;track kind="subtitles" src="es.vtt" srclang="es" label="Espa&ntilde;ol"&gt;
&lt;track kind="descriptions" src="audio-desc.vtt" srclang="en"&gt;
&lt;track kind="chapters" src="chapters.vtt"&gt;</code></pre>

<table>
  <tr><th>kind</th><th>For</th></tr>
  <tr><td>captions</td><td>Deaf/HoH users (transcription + sound effects)</td></tr>
  <tr><td>subtitles</td><td>Translation for hearing users</td></tr>
  <tr><td>descriptions</td><td>Audio descriptions for blind users</td></tr>
  <tr><td>chapters</td><td>Chapter markers</td></tr>
</table>

<p><strong>Adaptive bitrate streaming</strong> &mdash; for serious video, native <code>&lt;source&gt;</code> isn&rsquo;t enough. Use HLS (Apple&rsquo;s HTTP Live Streaming) or DASH:</p>
<pre><code>&lt;video id="player"&gt;&lt;/video&gt;
&lt;script type="module"&gt;
  import Hls from "hls.js";
  const video = document.getElementById("player");
  if (Hls.isSupported()) {
    new Hls().loadSource("video.m3u8");
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = "video.m3u8";   // Safari has native HLS
  }
&lt;/script&gt;</code></pre>

<p>HLS automatically adjusts quality based on network speed &mdash; the player switches between low/med/high streams seamlessly. Services like Mux, Cloudflare Stream, AWS IVS, and BunnyCDN handle encoding and delivery; building HLS yourself is a project.</p>
'''

ANSWERS[71] = r'''
<p><code>&lt;acronym&gt;</code> was an HTML4 element used to mark acronyms with an expansion in the <code>title</code> attribute. It was <strong>removed in HTML5</strong> in favor of the broader <code>&lt;abbr&gt;</code> element.</p>

<pre><code>&lt;!-- HTML4 (deprecated) --&gt;
&lt;acronym title="Hypertext Transfer Protocol"&gt;HTTP&lt;/acronym&gt;

&lt;!-- HTML5 (correct) --&gt;
&lt;abbr title="Hypertext Transfer Protocol"&gt;HTTP&lt;/abbr&gt;</code></pre>

<p><strong>Why <code>&lt;acronym&gt;</code> was deprecated:</strong></p>
<ul>
  <li><strong>The acronym/abbreviation distinction is fuzzy</strong> &mdash; HTML5 simplified by using one element. Linguistically, an acronym is pronounced as a word ("NASA," "scuba"), while an abbreviation is read letter-by-letter ("HTML," "CSS"), but most authors don&rsquo;t bother with the distinction.</li>
  <li><strong>Inconsistent browser implementations</strong> &mdash; some browsers underlined acronyms with a dotted line, others didn&rsquo;t. Behavior varied.</li>
  <li><strong>Redundant with <code>&lt;abbr&gt;</code></strong> &mdash; the existing <code>&lt;abbr&gt;</code> covered both cases functionally; killing one element simplified the spec.</li>
</ul>

<p><strong>Modern usage with <code>&lt;abbr&gt;</code>:</strong></p>
<pre><code>&lt;p&gt;The &lt;abbr title="World Health Organization"&gt;WHO&lt;/abbr&gt; published
   guidelines about &lt;abbr title="Coronavirus Disease 2019"&gt;COVID-19&lt;/abbr&gt;.&lt;/p&gt;

&lt;p&gt;Most browsers render &lt;abbr title="Cascading Style Sheets"&gt;CSS&lt;/abbr&gt;
   with a dotted underline; hover to see the expansion.&lt;/p&gt;

&lt;style&gt;
  abbr {
    cursor: help;
    border-bottom: 1px dotted currentColor;
  }
&lt;/style&gt;</code></pre>

<p><strong>Best practices for abbreviations:</strong></p>
<ul>
  <li><strong>Spell out on first use</strong> &mdash; "World Health Organization (WHO)" the first time, then just "WHO" thereafter. <code>&lt;abbr&gt;</code> alone doesn&rsquo;t replace this convention; it just adds a hover-to-reveal tooltip.</li>
  <li><strong>Don&rsquo;t mark every common abbreviation</strong> &mdash; "etc.", "e.g.", "Mr.", "ZIP code" are universally understood; marking them clutters the markup.</li>
  <li><strong>Title attribute is the expansion</strong> &mdash; full, unabbreviated form. Don&rsquo;t use it for definitions or descriptions.</li>
  <li><strong>Mobile users can&rsquo;t hover</strong> &mdash; the <code>title</code> tooltip is invisible on touch devices. For critical context, spell out in the body text.</li>
</ul>

<p><strong>Historical context: deprecated elements graveyard</strong> &mdash; HTML5 removed dozens of elements that overlapped with newer ones or fit better as CSS:</p>
<table>
  <tr><th>Removed</th><th>Replacement</th></tr>
  <tr><td><code>&lt;acronym&gt;</code></td><td><code>&lt;abbr&gt;</code></td></tr>
  <tr><td><code>&lt;applet&gt;</code></td><td><code>&lt;object&gt;</code> or <code>&lt;embed&gt;</code></td></tr>
  <tr><td><code>&lt;basefont&gt;</code>, <code>&lt;font&gt;</code></td><td>CSS <code>color</code>, <code>font-family</code></td></tr>
  <tr><td><code>&lt;big&gt;</code>, <code>&lt;tt&gt;</code></td><td>CSS <code>font-size</code>, <code>font-family: monospace</code></td></tr>
  <tr><td><code>&lt;center&gt;</code></td><td>CSS <code>text-align: center</code> or flex/grid</td></tr>
  <tr><td><code>&lt;frame&gt;</code>, <code>&lt;frameset&gt;</code>, <code>&lt;noframes&gt;</code></td><td><code>&lt;iframe&gt;</code></td></tr>
  <tr><td><code>&lt;keygen&gt;</code></td><td>WebAuthn / passkeys</td></tr>
  <tr><td><code>&lt;blink&gt;</code>, <code>&lt;marquee&gt;</code></td><td>CSS animations (and good taste)</td></tr>
</table>

<p>The pattern: HTML retreats from presentation to focus on structure and meaning; CSS handles look; JavaScript handles interaction. <code>&lt;acronym&gt;</code> failed this test &mdash; it was structure that overlapped with another structure element.</p>
'''

ANSWERS[72] = r'''
<p>The viewport <code>&lt;meta&gt;</code> tag tells mobile browsers <strong>how to render the page on the device</strong>. Without it, mobile browsers assume a 980-1024px desktop layout and zoom out, making text tiny. With it, the page renders at the actual device width.</p>

<p><strong>The standard tag every responsive site needs:</strong></p>
<pre><code>&lt;meta name="viewport"
      content="width=device-width, initial-scale=1.0"&gt;</code></pre>

<p>Place it inside <code>&lt;head&gt;</code> on every page.</p>

<p><strong>What each part does:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>width=device-width</code></td><td>Use the device&rsquo;s actual pixel width as the viewport width</td></tr>
  <tr><td><code>initial-scale=1.0</code></td><td>No initial zoom &mdash; render at 100%</td></tr>
  <tr><td><code>minimum-scale=1.0</code></td><td>Prevent users from zooming smaller</td></tr>
  <tr><td><code>maximum-scale=2.0</code></td><td>Cap zoom to 200%</td></tr>
  <tr><td><code>user-scalable=no</code></td><td>Disable pinch-zoom (DON&rsquo;T USE &mdash; accessibility violation)</td></tr>
</table>

<p><strong>Critical accessibility rule:</strong> never use <code>user-scalable=no</code> or <code>maximum-scale=1.0</code>. They prevent users with low vision from zooming &mdash; a major WCAG failure. The defaults are correct; don&rsquo;t restrict them.</p>

<p><strong>Without the viewport tag</strong> &mdash; a page on iPhone:</p>
<ul>
  <li>Browser assumes 980px-wide viewport.</li>
  <li>Renders the page at 980px wide.</li>
  <li>Scales down to fit the actual screen (~390px wide).</li>
  <li>Result: text is 1/3 the intended size; users must pinch-zoom every page.</li>
</ul>

<p><strong>With the viewport tag</strong>:</p>
<ul>
  <li>Browser uses the device&rsquo;s actual width as the viewport.</li>
  <li>Page renders at that width.</li>
  <li>Media queries for mobile breakpoints fire correctly.</li>
  <li>Result: native mobile rendering.</li>
</ul>

<p><strong>Modern additions worth knowing:</strong></p>
<pre><code>&lt;!-- Make the viewport extend behind the notch on iOS --&gt;
&lt;meta name="viewport"
      content="width=device-width, initial-scale=1.0, viewport-fit=cover"&gt;

&lt;!-- Then in CSS, use safe-area-inset for notch-safe padding --&gt;
&lt;style&gt;
  .header {
    padding-top: max(1rem, env(safe-area-inset-top));
    padding-left: max(1rem, env(safe-area-inset-left));
  }
&lt;/style&gt;</code></pre>

<p><strong><code>viewport-fit=cover</code></strong> tells iOS Safari to render the page edge-to-edge, including under the notch and home indicator. The CSS <code>env(safe-area-inset-*)</code> values let you avoid these areas selectively.</p>

<p><strong>Theme color</strong> &mdash; pair with the viewport tag:</p>
<pre><code>&lt;meta name="theme-color" content="#0066cc"&gt;
&lt;meta name="theme-color" content="#101316"
      media="(prefers-color-scheme: dark)"&gt;</code></pre>

<p>Mobile browsers tint the address bar and OS chrome to match. Provide a separate value for dark mode for full theme integration.</p>

<p><strong>Common mistakes:</strong></p>
<ul>
  <li>Forgetting the viewport tag entirely &mdash; mobile renders desktop-sized.</li>
  <li>Setting fixed pixel widths in CSS that exceed mobile width &mdash; horizontal scroll appears.</li>
  <li>Using non-responsive design with the viewport tag &mdash; the page renders at device width but content is too wide.</li>
</ul>

<p>The viewport tag is the single most important addition to any responsive site. Without it, all your media queries and flexible layouts are wasted on mobile.</p>
'''

ANSWERS[73] = r'''
<p>The <code>&lt;address&gt;</code> element marks <strong>contact information for the nearest article or document author</strong>. It&rsquo;s narrowly scoped &mdash; not a generic geographic-address element &mdash; and it associates contact info semantically with its containing article or page.</p>

<pre><code>&lt;article&gt;
  &lt;h2&gt;Annual Report 2026&lt;/h2&gt;
  &lt;p&gt;Detailed analysis of the year...&lt;/p&gt;

  &lt;footer&gt;
    &lt;address&gt;
      Authored by Jane Smith.
      Contact: &lt;a href="mailto:jane@example.com"&gt;jane@example.com&lt;/a&gt;
      &lt;br&gt;
      Acme Research Group, 123 Innovation Drive
      &lt;br&gt;
      Phone: &lt;a href="tel:+15551234567"&gt;+1 (555) 123-4567&lt;/a&gt;
    &lt;/address&gt;
  &lt;/footer&gt;
&lt;/article&gt;</code></pre>

<p><strong>The narrow definition:</strong></p>
<ul>
  <li><strong>Contact info for the article author</strong> when nested inside <code>&lt;article&gt;</code>.</li>
  <li><strong>Contact info for the document</strong> when in the page-level <code>&lt;footer&gt;</code>.</li>
  <li><strong>Not</strong> for arbitrary geographic addresses unrelated to authorship.</li>
</ul>

<p><strong>What goes inside:</strong></p>
<table>
  <tr><th>OK</th><th>Not OK</th></tr>
  <tr><td>Email links (<code>mailto:</code>)</td><td>Generic location addresses (use a paragraph)</td></tr>
  <tr><td>Phone links (<code>tel:</code>)</td><td>Office hours (use a separate paragraph)</td></tr>
  <tr><td>Postal addresses of the contact</td><td>Driving directions</td></tr>
  <tr><td>Social media handles</td><td>Generic locations like "the Eiffel Tower"</td></tr>
  <tr><td>Author/contact name</td><td>Random unrelated bio info</td></tr>
</table>

<p><strong>Correct vs incorrect uses:</strong></p>
<pre><code>&lt;!-- WRONG: this is just a geographic address, not author contact --&gt;
&lt;p&gt;The conference is at:&lt;/p&gt;
&lt;address&gt;
  Convention Center
  100 Main Street
  Anytown, CA 12345
&lt;/address&gt;

&lt;!-- RIGHT: a plain paragraph for an arbitrary address --&gt;
&lt;p&gt;The conference is at:&lt;br&gt;
   Convention Center&lt;br&gt;
   100 Main Street&lt;br&gt;
   Anytown, CA 12345&lt;/p&gt;

&lt;!-- RIGHT: address element for author contact --&gt;
&lt;article&gt;
  &lt;h2&gt;Conference Recap&lt;/h2&gt;
  &lt;p&gt;Here&rsquo;s what happened...&lt;/p&gt;
  &lt;address&gt;
    Reported by &lt;a rel="author" href="/authors/jane"&gt;Jane Smith&lt;/a&gt;
  &lt;/address&gt;
&lt;/article&gt;</code></pre>

<p><strong>Default styling and accessibility:</strong></p>
<ul>
  <li>Browsers italicize <code>&lt;address&gt;</code> by default &mdash; a typographic convention.</li>
  <li>Screen readers announce it as "address" or treat it as a region depending on the implementation.</li>
  <li>Override with CSS for any visual design.</li>
</ul>

<p><strong>Microdata pairing</strong> &mdash; <code>&lt;address&gt;</code> works well with schema.org markup:</p>
<pre><code>&lt;article itemscope itemtype="https://schema.org/Article"&gt;
  &lt;h2 itemprop="headline"&gt;Article Title&lt;/h2&gt;
  &lt;p&gt;...&lt;/p&gt;
  &lt;address itemprop="author" itemscope itemtype="https://schema.org/Person"&gt;
    &lt;span itemprop="name"&gt;Jane Smith&lt;/span&gt; -
    &lt;a itemprop="email" href="mailto:jane@example.com"&gt;jane@example.com&lt;/a&gt;
  &lt;/address&gt;
&lt;/article&gt;</code></pre>

<p>This combination makes both screen readers and search engines understand the article&rsquo;s author.</p>

<p>Using <code>&lt;address&gt;</code> incorrectly is one of the most common HTML mistakes &mdash; the spec&rsquo;s narrow definition catches developers who think it&rsquo;s for any address. Reserve it specifically for author/document contact information.</p>
'''

ANSWERS[74] = r'''
<p>Multiple file uploads use the <code>multiple</code> attribute on <code>&lt;input type="file"&gt;</code>. Combined with <code>accept</code> and proper form configuration, you can upload many files in one go &mdash; with progress, drag-and-drop, and previews built on top.</p>

<pre><code>&lt;form action="/upload"
      method="post"
      enctype="multipart/form-data"&gt;

  &lt;label for="docs"&gt;Upload documents:&lt;/label&gt;
  &lt;input type="file"
         id="docs"
         name="documents"
         accept=".pdf,.doc,.docx,.txt"
         multiple
         required&gt;

  &lt;output id="preview"&gt;&lt;/output&gt;

  &lt;button type="submit"&gt;Upload all&lt;/button&gt;
&lt;/form&gt;

&lt;script&gt;
  const input  = document.getElementById("docs");
  const output = document.getElementById("preview");

  input.addEventListener("change", () =&gt; {
    output.innerHTML = "";
    for (const file of input.files) {
      const li = document.createElement("li");
      li.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      output.appendChild(li);
    }
  });
&lt;/script&gt;</code></pre>

<p><strong>Key points:</strong></p>
<ul>
  <li><code>multiple</code> attribute on the input enables multi-select in the picker.</li>
  <li>The <code>name</code> stays the same; server receives an array.</li>
  <li><code>accept</code> filters the file picker to relevant types (UX hint, not security).</li>
  <li><code>input.files</code> is a <code>FileList</code> &mdash; iterable, indexable.</li>
</ul>

<p><strong>Drag-and-drop with progress</strong>:</p>
<pre><code>&lt;div id="dropzone" class="dropzone"&gt;
  Drop files here, or
  &lt;label for="picker" class="link"&gt;browse&lt;/label&gt;
  &lt;input type="file" id="picker" multiple hidden&gt;
&lt;/div&gt;
&lt;ul id="fileList"&gt;&lt;/ul&gt;

&lt;script&gt;
  const dropzone = document.getElementById("dropzone");
  const picker   = document.getElementById("picker");
  const list     = document.getElementById("fileList");

  // Prevent default to enable drop
  ["dragenter", "dragover", "dragleave", "drop"].forEach((e) =&gt;
    dropzone.addEventListener(e, (ev) =&gt; { ev.preventDefault(); ev.stopPropagation(); }),
  );
  dropzone.addEventListener("dragenter", () =&gt; dropzone.classList.add("active"));
  dropzone.addEventListener("dragleave", () =&gt; dropzone.classList.remove("active"));
  dropzone.addEventListener("drop", (e) =&gt; {
    dropzone.classList.remove("active");
    handleFiles(e.dataTransfer.files);
  });
  picker.addEventListener("change", () =&gt; handleFiles(picker.files));

  async function handleFiles(files) {
    for (const file of files) {
      const li = document.createElement("li");
      const progress = document.createElement("progress");
      progress.max = 100;
      li.textContent = file.name + " ";
      li.appendChild(progress);
      list.appendChild(li);

      const fd = new FormData();
      fd.append("file", file);

      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (e) =&gt; {
        if (e.lengthComputable) progress.value = (e.loaded / e.total) * 100;
      };
      xhr.onload = () =&gt; { li.textContent = file.name + " ✓"; };
      xhr.open("POST", "/upload");
      xhr.send(fd);
    }
  }
&lt;/script&gt;

&lt;style&gt;
  .dropzone {
    border: 2px dashed #aaa;
    padding: 2em;
    text-align: center;
    border-radius: 8px;
  }
  .dropzone.active {
    border-color: #0066cc;
    background: #f0f8ff;
  }
&lt;/style&gt;</code></pre>

<p><strong>Server-side handling</strong> (Node.js + Express + Multer):</p>
<pre><code>import multer from "multer";
const upload = multer({ dest: "uploads/", limits: { fileSize: 10_000_000 } });

app.post("/upload", upload.array("documents", 20), (req, res) =&gt; {
  const files = req.files;   // array of { filename, originalname, size, mimetype }
  // process each file...
  res.json({ uploaded: files.length });
});</code></pre>

<p><strong>Direct-to-cloud uploads</strong> (recommended for large files): generate signed URLs on the server, upload from the browser directly to S3 / R2 / Cloudinary. Avoids your server bandwidth and disk entirely.</p>

<p><strong>Production considerations:</strong> set max file size and count, validate types server-side by content (not just extension), generate random filenames, scan for malware, paginate when listing many uploads. Libraries like Uppy or Filepond handle resumable uploads, retries, and rich UIs.</p>
'''

ANSWERS[75] = r'''
<p>The <code>&lt;q&gt;</code> element marks an <strong>inline quotation</strong> &mdash; a short quote within a sentence or paragraph. Browsers automatically wrap the content in locale-appropriate quotation marks, so you don&rsquo;t type them yourself.</p>

<pre><code>&lt;p&gt;Einstein famously said &lt;q&gt;Imagination is more important than knowledge.&lt;/q&gt;&lt;/p&gt;

&lt;p&gt;She told me &lt;q cite="https://example.com/source"&gt;
  the meeting is canceled
&lt;/q&gt; before I could ask why.&lt;/p&gt;

&lt;!-- Nested quotes — inner gets different quote marks automatically --&gt;
&lt;p&gt;The professor explained,
   &lt;q&gt;In her famous paper, Smith wrote &lt;q&gt;all evidence points to climate change&lt;/q&gt;
   and the data has held up.&lt;/q&gt;&lt;/p&gt;</code></pre>

<p>The browser inserts <code>"</code> and <code>"</code> (curly quotes) automatically; you never type them. For nested quotes, the inner pair becomes single quotes <code>'...'</code> &mdash; matching English typographic convention.</p>

<p><strong>Locale-aware quotation marks:</strong></p>
<pre><code>&lt;p lang="en"&gt;She said &lt;q&gt;Hello&lt;/q&gt;.&lt;/p&gt;
&lt;!-- Renders: She said "Hello". --&gt;

&lt;p lang="fr"&gt;Elle a dit &lt;q&gt;Bonjour&lt;/q&gt;.&lt;/p&gt;
&lt;!-- Renders: Elle a dit «Bonjour». --&gt;

&lt;p lang="de"&gt;Sie sagte &lt;q&gt;Hallo&lt;/q&gt;.&lt;/p&gt;
&lt;!-- Renders: Sie sagte „Hallo". --&gt;</code></pre>

<p>Setting <code>lang</code> on the element (or any ancestor) lets the browser pick the right quotation marks for that language &mdash; English gets <code>"..."</code>, French gets <code>«&nbsp;...&nbsp;»</code> (with non-breaking spaces!), German gets <code>„..."</code>, and so on.</p>

<p><strong><code>&lt;q&gt;</code> vs <code>&lt;blockquote&gt;</code>:</strong></p>
<table>
  <tr><th></th><th><code>&lt;q&gt;</code></th><th><code>&lt;blockquote&gt;</code></th></tr>
  <tr><td>Display</td><td>Inline (within a paragraph)</td><td>Block (its own visual region)</td></tr>
  <tr><td>Quote marks</td><td>Auto-inserted by browser</td><td>None (you add manually if needed)</td></tr>
  <tr><td>Length</td><td>Short &mdash; a phrase or sentence</td><td>Long &mdash; multiple sentences/paragraphs</td></tr>
  <tr><td>Default style</td><td>Quote marks around content</td><td>Indented block</td></tr>
</table>

<p><strong>The <code>cite</code> attribute</strong> on <code>&lt;q&gt;</code> takes a URL identifying the source &mdash; same as on <code>&lt;blockquote&gt;</code>:</p>
<pre><code>&lt;p&gt;The article notes that
   &lt;q cite="https://example.com/article"&gt;HTML5 simplifies form validation&lt;/q&gt;.&lt;/p&gt;</code></pre>

<p>The attribute is invisible to users but available for scrapers and accessibility tools. Visible source attribution still requires a separate <code>&lt;cite&gt;</code> element or text.</p>

<p><strong>Custom quote marks via CSS:</strong></p>
<pre><code>q {
  quotes: "&laquo;" "&raquo;" "&lsaquo;" "&rsaquo;";   /* outer and inner pairs */
}
q::before { content: open-quote; }
q::after  { content: close-quote; }</code></pre>

<p>The <code>quotes</code> property defines pairs for nesting levels; <code>open-quote</code> and <code>close-quote</code> reference them in <code>::before</code> / <code>::after</code> pseudo-elements. Disable the default behavior with:</p>
<pre><code>q::before, q::after { content: ""; }</code></pre>

<p><strong>When to use <code>&lt;q&gt;</code> vs typing quote characters directly:</strong></p>
<ul>
  <li><strong>Use <code>&lt;q&gt;</code></strong> when the quote is structurally a quotation that benefits from semantic markup &mdash; locale-aware quote marks, possible CSS styling, machine readability.</li>
  <li><strong>Use literal characters</strong> (<code>&ldquo;...&rdquo;</code>) when the text just happens to be in quotes for typographic reasons, not because it&rsquo;s a quotation from another source.</li>
</ul>
'''

ANSWERS[76] = r'''
<p>Responsive card layouts use CSS Grid or Flexbox to flow card components across different screen widths. CSS Grid with <code>auto-fit</code> + <code>minmax</code> is the canonical pattern &mdash; cards reflow naturally without media queries.</p>

<pre><code>&lt;section class="cards"&gt;
  &lt;article class="card"&gt;
    &lt;img src="product1.jpg" alt="Product 1" loading="lazy"&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;Wireless Headphones&lt;/h3&gt;
      &lt;p class="price"&gt;$199.99&lt;/p&gt;
      &lt;p&gt;Premium noise-canceling headphones with 30-hour battery life.&lt;/p&gt;
      &lt;a href="/products/headphones" class="btn"&gt;Shop now&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;

  &lt;article class="card"&gt;
    &lt;img src="product2.jpg" alt="Product 2" loading="lazy"&gt;
    &lt;div class="card-body"&gt;
      &lt;h3&gt;Smart Watch&lt;/h3&gt;
      &lt;p class="price"&gt;$299.99&lt;/p&gt;
      &lt;p&gt;Track your fitness, calls, and notifications all day.&lt;/p&gt;
      &lt;a href="/products/watch" class="btn"&gt;Shop now&lt;/a&gt;
    &lt;/div&gt;
  &lt;/article&gt;

  &lt;!-- More cards... --&gt;
&lt;/section&gt;

&lt;style&gt;
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .card {
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }

  .card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  .card-body {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    flex: 1;          /* grows to fill card; pushes button to bottom */
  }

  .card h3 {
    margin: 0 0 0.5rem;
    font-size: 1.1rem;
  }

  .price {
    font-weight: 600;
    color: #0066cc;
    margin: 0 0 0.5rem;
  }

  .btn {
    margin-top: auto;     /* sticks to bottom of card */
    align-self: start;
    background: #0066cc;
    color: white;
    padding: 0.5rem 1rem;
    text-decoration: none;
    border-radius: 6px;
  }
&lt;/style&gt;</code></pre>

<p><strong>Why this works for any screen width:</strong></p>
<ul>
  <li><strong><code>auto-fit</code></strong> &mdash; fits as many columns as can have at least the minimum width.</li>
  <li><strong><code>minmax(280px, 1fr)</code></strong> &mdash; each column is at least 280px; if there&rsquo;s extra space, columns share it equally.</li>
  <li><strong>Cards wrap automatically</strong> when there&rsquo;s no room for another full-width card.</li>
  <li><strong>Single media query (or none) needed</strong> &mdash; the layout adapts based on available space, not specific breakpoints.</li>
</ul>

<p><strong>The flex tricks inside each card:</strong></p>
<ul>
  <li><strong><code>display: flex; flex-direction: column</code></strong> on the card &mdash; lets us control vertical alignment.</li>
  <li><strong><code>flex: 1</code> on the card body</strong> &mdash; takes remaining space, ensuring all cards in a row have equal heights even with different content lengths.</li>
  <li><strong><code>margin-top: auto</code> on the button</strong> &mdash; pushes it to the bottom of the card body. Across cards with varying text lengths, all buttons line up.</li>
</ul>

<p><strong>auto-fit vs auto-fill</strong> &mdash; subtle but important:</p>
<table>
  <tr><th></th><th><code>auto-fit</code></th><th><code>auto-fill</code></th></tr>
  <tr><td>With few items</td><td>Items stretch to fill the row</td><td>Items stay at min size; empty space remains</td></tr>
  <tr><td>Use when</td><td>You want cards to fill all available space</td><td>You want consistent card sizes regardless of count</td></tr>
</table>

<p>Use <code>auto-fit</code> for galleries and product grids; <code>auto-fill</code> for fixed-grid dashboards where cards shouldn&rsquo;t expand.</p>

<p><strong>Modern enhancements:</strong> CSS container queries (<code>@container</code>) let card content respond to the card&rsquo;s width, not the viewport width &mdash; allowing the same card to render differently in a sidebar vs main content. Aspect-ratio property keeps card shapes consistent regardless of content.</p>
'''

ANSWERS[77] = r'''
<p><code>&lt;script&gt;</code> embeds executable JavaScript (or other script types). <code>&lt;noscript&gt;</code> provides fallback content shown only when scripting is disabled or unavailable. They&rsquo;re paired conceptually &mdash; one runs when JavaScript works; the other replaces it when it doesn&rsquo;t.</p>

<table>
  <tr><th></th><th><code>&lt;script&gt;</code></th><th><code>&lt;noscript&gt;</code></th></tr>
  <tr><td>Purpose</td><td>Embed or load JavaScript</td><td>Fallback content for non-JS environments</td></tr>
  <tr><td>Visible</td><td>Never (script content is invisible)</td><td>Only when JS is disabled</td></tr>
  <tr><td>Runs</td><td>Yes (when JS is enabled)</td><td>Renders content when JS is disabled</td></tr>
  <tr><td>Common use</td><td>App logic, analytics, libraries</td><td>"Please enable JavaScript" message; tracking pixel fallback</td></tr>
</table>

<p><strong>Side-by-side example:</strong></p>
<pre><code>&lt;!-- Shows interactive widget when JS works --&gt;
&lt;div id="weather-widget"&gt;Loading weather...&lt;/div&gt;

&lt;script&gt;
  fetch("/api/weather")
    .then(r =&gt; r.json())
    .then(data =&gt; {
      document.getElementById("weather-widget").textContent =
        `${data.temp}&deg;F, ${data.conditions}`;
    });
&lt;/script&gt;

&lt;!-- Shows fallback when JS is unavailable --&gt;
&lt;noscript&gt;
  &lt;div&gt;
    &lt;p&gt;Weather widget requires JavaScript.&lt;/p&gt;
    &lt;p&gt;See &lt;a href="/weather"&gt;our weather page&lt;/a&gt; instead.&lt;/p&gt;
  &lt;/div&gt;
&lt;/noscript&gt;</code></pre>

<p><strong>Critical attributes on <code>&lt;script&gt;</code>:</strong></p>
<table>
  <tr><th>Attribute</th><th>Effect</th></tr>
  <tr><td><code>src</code></td><td>External script URL</td></tr>
  <tr><td><code>type="module"</code></td><td>ES modules; supports import/export</td></tr>
  <tr><td><code>defer</code></td><td>Download in parallel; execute after HTML parses</td></tr>
  <tr><td><code>async</code></td><td>Download in parallel; execute as soon as ready (out of order)</td></tr>
  <tr><td><code>nomodule</code></td><td>Run only in browsers WITHOUT module support (legacy)</td></tr>
  <tr><td><code>integrity</code></td><td>SRI hash for tamper detection on third-party scripts</td></tr>
  <tr><td><code>crossorigin</code></td><td>CORS mode for cross-origin scripts</td></tr>
</table>

<p><strong>Loading order &mdash; the priority hierarchy:</strong></p>
<pre><code>&lt;!-- Blocks parsing — avoid except in &lt;head&gt; for critical inline JS --&gt;
&lt;script src="blocking.js"&gt;&lt;/script&gt;

&lt;!-- Best for most external scripts: parses HTML, then runs in order --&gt;
&lt;script src="main.js" defer&gt;&lt;/script&gt;

&lt;!-- For independent scripts (analytics, ads): runs whenever ready --&gt;
&lt;script src="analytics.js" async&gt;&lt;/script&gt;

&lt;!-- ES modules: defer-like by default --&gt;
&lt;script type="module" src="app.mjs"&gt;&lt;/script&gt;</code></pre>

<p><strong>Inside <code>&lt;head&gt;</code>, <code>&lt;noscript&gt;</code> can only contain</strong> <code>&lt;link&gt;</code>, <code>&lt;style&gt;</code>, and <code>&lt;meta&gt;</code> &mdash; useful for loading CSS only when JS is disabled:</p>
<pre><code>&lt;head&gt;
  &lt;noscript&gt;
    &lt;link rel="stylesheet" href="no-js.css"&gt;
    &lt;style&gt;.js-only { display: none; }&lt;/style&gt;
  &lt;/noscript&gt;
&lt;/head&gt;</code></pre>

<p>Inside <code>&lt;body&gt;</code>, <code>&lt;noscript&gt;</code> can contain any flow content.</p>

<p><strong>When does <code>&lt;noscript&gt;</code> trigger?</strong></p>
<ul>
  <li>JavaScript explicitly disabled in browser settings.</li>
  <li>Extension blocks scripts (NoScript, uBlock).</li>
  <li>Network failure prevents script from loading.</li>
  <li>Browser doesn&rsquo;t support JavaScript (extremely rare).</li>
</ul>

<p><strong>Modern preference: progressive enhancement</strong> &mdash; build with semantic HTML that works without JS, then enhance. <code>&lt;noscript&gt;</code> becomes the rare case rather than the rule. The <code>html.no-js</code>/<code>.js</code> class swap is a more flexible alternative for showing/hiding content based on JS availability.</p>
'''

ANSWERS[78] = r'''
<p>HTML5 form validation makes <code>required</code> fields trivial &mdash; the browser blocks submission and shows a native error if any required field is empty. Combined with type validation and patterns, you get rich validation with no JavaScript.</p>

<pre><code>&lt;form action="/signup" method="post"&gt;
  &lt;label&gt;Full name &lt;span class="req" aria-hidden="true"&gt;*&lt;/span&gt;
    &lt;input type="text"
           name="name"
           required
           minlength="2"
           maxlength="100"&gt;
  &lt;/label&gt;

  &lt;label&gt;Email &lt;span class="req" aria-hidden="true"&gt;*&lt;/span&gt;
    &lt;input type="email"
           name="email"
           required
           autocomplete="email"&gt;
  &lt;/label&gt;

  &lt;label&gt;Password &lt;span class="req" aria-hidden="true"&gt;*&lt;/span&gt;
    &lt;input type="password"
           name="password"
           required
           minlength="8"
           autocomplete="new-password"&gt;
    &lt;small&gt;Minimum 8 characters&lt;/small&gt;
  &lt;/label&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Account type &lt;span class="req" aria-hidden="true"&gt;*&lt;/span&gt;&lt;/legend&gt;
    &lt;label&gt;&lt;input type="radio" name="type" value="personal" required&gt; Personal&lt;/label&gt;
    &lt;label&gt;&lt;input type="radio" name="type" value="business"&gt; Business&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;label&gt;
    &lt;input type="checkbox" name="terms" value="yes" required&gt;
    I agree to the &lt;a href="/terms"&gt;Terms of Service&lt;/a&gt;
    &lt;span class="req" aria-hidden="true"&gt;*&lt;/span&gt;
  &lt;/label&gt;

  &lt;p&gt;&lt;small&gt;&lt;span aria-hidden="true"&gt;*&lt;/span&gt; Required field&lt;/small&gt;&lt;/p&gt;

  &lt;button type="submit"&gt;Create account&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p><strong>Notes on each required field:</strong></p>
<ul>
  <li><strong>Text inputs</strong> &mdash; <code>required</code> blocks empty submission. <code>minlength</code>/<code>maxlength</code> add length constraints.</li>
  <li><strong>Email</strong> &mdash; type validates format AND <code>required</code> ensures it&rsquo;s filled.</li>
  <li><strong>Radio groups</strong> &mdash; only one radio in the group needs <code>required</code> &mdash; it makes the entire group required.</li>
  <li><strong>Checkbox</strong> &mdash; <code>required</code> on a checkbox forces the user to check it (perfect for terms agreement).</li>
</ul>

<p><strong>Style required fields with CSS:</strong></p>
<pre><code>input:required, textarea:required, select:required {
  border-left: 3px solid #f44336;
}

input:required:valid, textarea:required:valid {
  border-left-color: #4caf50;
}

/* Don't show red until user has interacted */
input:user-invalid {
  border-color: red;
  background: #ffebee;
}

.req {
  color: red;
  margin-left: 0.2em;
}</code></pre>

<p>The <code>:user-invalid</code> pseudo-class (well-supported in 2026) only matches <em>after</em> the user has interacted &mdash; preventing the form from looking error-laden when first opened.</p>

<p><strong>Custom validation messages:</strong></p>
<pre><code>const email = document.querySelector("input[name='email']");

email.addEventListener("invalid", () =&gt; {
  if (email.validity.valueMissing) {
    email.setCustomValidity("We need your email to send the confirmation");
  } else if (email.validity.typeMismatch) {
    email.setCustomValidity("That doesn&rsquo;t look like an email address");
  } else {
    email.setCustomValidity("");
  }
});

email.addEventListener("input", () =&gt; {
  email.setCustomValidity("");   // clear when user retries
});</code></pre>

<p><strong>Server-side validation is not optional</strong>. HTML validation is UX only &mdash; users can:</p>
<ul>
  <li>Disable JavaScript and bypass any client-side validation.</li>
  <li>Edit attributes in DevTools to remove <code>required</code>.</li>
  <li>Send raw HTTP requests bypassing the browser entirely.</li>
</ul>

<p>Always re-validate every field on the server. HTML validation reduces invalid submissions; server validation prevents invalid data from ever entering the system.</p>
'''

ANSWERS[79] = r'''
<p>The <code>&lt;small&gt;</code> element marks <strong>side comments, fine print, copyright notices, or legal disclaimers</strong> &mdash; text that&rsquo;s typographically smaller because it&rsquo;s less prominent, not because the author is shrinking it for visual reasons.</p>

<pre><code>&lt;footer&gt;
  &lt;small&gt;&amp;copy; 2026 Acme Corporation. All rights reserved.&lt;/small&gt;
&lt;/footer&gt;

&lt;p&gt;Free shipping on orders over $50.
   &lt;small&gt;Excludes oversized items and international destinations.&lt;/small&gt;&lt;/p&gt;

&lt;p&gt;Buy now, pay later with PayLater.
   &lt;small&gt;Subject to credit approval. Standard terms apply.&lt;/small&gt;&lt;/p&gt;</code></pre>

<p><strong>Default styling</strong> &mdash; browsers render <code>&lt;small&gt;</code> at a smaller font size (typically 80% of parent), but the semantic meaning is what counts. CSS lets you override the size while keeping the meaning.</p>

<p><strong><code>&lt;small&gt;</code> is semantic, not presentational:</strong></p>
<table>
  <tr><th>Tag</th><th>Means</th></tr>
  <tr><td><code>&lt;small&gt;</code></td><td>"This is a side comment or fine print" &mdash; smaller because it&rsquo;s less prominent</td></tr>
  <tr><td>CSS <code>font-size: 0.8em</code></td><td>"Render this smaller" &mdash; pure visual</td></tr>
</table>

<p><strong>Use <code>&lt;small&gt;</code> for:</strong></p>
<ul>
  <li>Copyright notices</li>
  <li>Legal disclaimers</li>
  <li>Fine print after a marketing claim</li>
  <li>Attributions and credits</li>
  <li>Side comments that supplement the main text</li>
  <li>Compliance text (terms apply, exclusions, restrictions)</li>
</ul>

<p><strong>Don&rsquo;t use <code>&lt;small&gt;</code> for:</strong></p>
<ul>
  <li>Visually decorative small text (use a CSS class)</li>
  <li>Headings or paragraphs that just happen to be smaller</li>
  <li>Reducing font size for layout reasons</li>
</ul>

<p><strong>Real-world pattern &mdash; product pricing with subtext:</strong></p>
<pre><code>&lt;article class="product"&gt;
  &lt;h2&gt;Premium Subscription&lt;/h2&gt;
  &lt;p class="price"&gt;
    $9.99/month
    &lt;small&gt;billed annually at $119.88, save 20% vs monthly&lt;/small&gt;
  &lt;/p&gt;
&lt;/article&gt;

&lt;style&gt;
  .price small {
    display: block;
    color: #666;
    font-weight: normal;
  }
&lt;/style&gt;</code></pre>

<p>The <code>&lt;small&gt;</code> wraps the secondary information; CSS <code>display: block</code> puts it on its own line. The semantic meaning ("this is fine print supplementing the price") is preserved.</p>

<p><strong>Accessibility:</strong></p>
<ul>
  <li>Screen readers don&rsquo;t announce <code>&lt;small&gt;</code> with any special inflection &mdash; they just read the content.</li>
  <li>The visual size reduction comes from CSS; the semantic role comes from the tag.</li>
  <li>Don&rsquo;t hide critical info inside <code>&lt;small&gt;</code> just to de-emphasize it &mdash; users may miss it. The fine print should remain readable.</li>
</ul>

<p><strong>WCAG considerations:</strong> small text must still meet contrast requirements (4.5:1 for normal text). Don&rsquo;t shrink to the point that low-vision users can&rsquo;t read; the semantic meaning of "smaller print" doesn&rsquo;t excuse poor accessibility.</p>

<p><strong>Stacking with other inline elements:</strong></p>
<pre><code>&lt;p&gt;
  &lt;strong&gt;Sale ends Friday!&lt;/strong&gt;
  &lt;small&gt;Selected items only. While supplies last.&lt;/small&gt;
&lt;/p&gt;</code></pre>

<p>Compose <code>&lt;small&gt;</code> with <code>&lt;strong&gt;</code>, <code>&lt;em&gt;</code>, links, and other inline elements naturally &mdash; each carries its own semantic meaning.</p>
'''

ANSWERS[80] = r'''
<p>The <code>&lt;optgroup&gt;</code> element groups related <code>&lt;option&gt;</code> children inside a <code>&lt;select&gt;</code>. Each group has a label (the <code>label</code> attribute), and browsers render the label as a non-selectable header above the group&rsquo;s options.</p>

<pre><code>&lt;label for="course"&gt;Choose a course:&lt;/label&gt;
&lt;select id="course" name="course"&gt;
  &lt;option value=""&gt;-- Select --&lt;/option&gt;

  &lt;optgroup label="Web Development"&gt;
    &lt;option value="html-101"&gt;HTML Fundamentals&lt;/option&gt;
    &lt;option value="css-101"&gt;CSS Mastery&lt;/option&gt;
    &lt;option value="js-201"&gt;JavaScript Advanced&lt;/option&gt;
    &lt;option value="react-301"&gt;React in Depth&lt;/option&gt;
  &lt;/optgroup&gt;

  &lt;optgroup label="Backend"&gt;
    &lt;option value="node-201"&gt;Node.js&lt;/option&gt;
    &lt;option value="python-201"&gt;Python for Web&lt;/option&gt;
    &lt;option value="dbs-201"&gt;Databases&lt;/option&gt;
  &lt;/optgroup&gt;

  &lt;optgroup label="DevOps"&gt;
    &lt;option value="docker-301"&gt;Docker &amp; Containers&lt;/option&gt;
    &lt;option value="k8s-401"&gt;Kubernetes&lt;/option&gt;
    &lt;option value="ci-201"&gt;CI/CD Pipelines&lt;/option&gt;
  &lt;/optgroup&gt;
&lt;/select&gt;</code></pre>

<p><strong>How browsers render optgroups:</strong></p>
<ul>
  <li>The <code>label</code> attribute appears as a bold or italic header (varies by OS).</li>
  <li>Options inside the group are slightly indented.</li>
  <li>The label itself is non-selectable &mdash; clicking does nothing.</li>
  <li>Keyboard navigation flows naturally through groups.</li>
</ul>

<p><strong>Disable an entire group:</strong></p>
<pre><code>&lt;optgroup label="Coming soon" disabled&gt;
  &lt;option&gt;Course A (June 2026)&lt;/option&gt;
  &lt;option&gt;Course B (July 2026)&lt;/option&gt;
&lt;/optgroup&gt;</code></pre>

<p>All options inside a disabled <code>&lt;optgroup&gt;</code> are unselectable but visually visible &mdash; useful for indicating future availability without removing them.</p>

<p><strong>Limitations to know:</strong></p>
<ul>
  <li><strong>Cannot nest</strong> &mdash; one level of grouping only. The HTML spec forbids <code>&lt;optgroup&gt;</code> inside another <code>&lt;optgroup&gt;</code>.</li>
  <li><strong>Limited styling</strong> &mdash; CSS targeting <code>&lt;optgroup&gt;</code> and <code>&lt;option&gt;</code> is poorly supported. Browsers handle <code>&lt;select&gt;</code> rendering natively for OS consistency.</li>
  <li><strong>No icons or rich content</strong> in option labels &mdash; plain text only.</li>
  <li><strong>No search filtering</strong> &mdash; native <code>&lt;select&gt;</code> only matches by typing the first letter.</li>
</ul>

<p><strong>Accessibility benefits:</strong></p>
<ul>
  <li>Screen readers announce the group label when navigation crosses into a new group: "Web Development, group, HTML Fundamentals, option, 1 of 4."</li>
  <li>Users with cognitive disabilities benefit from organized chunks of related options.</li>
  <li>Long lists become scannable &mdash; especially for international country pickers, course catalogs, product categories.</li>
</ul>

<p><strong>When to use a custom combobox instead:</strong></p>
<table>
  <tr><th>Need</th><th>Native <code>&lt;optgroup&gt;</code></th><th>Custom combobox</th></tr>
  <tr><td>Filter as you type</td><td>No</td><td>Yes</td></tr>
  <tr><td>Rich item content (icons, images)</td><td>No</td><td>Yes</td></tr>
  <tr><td>Multi-select with chips</td><td>No</td><td>Yes</td></tr>
  <tr><td>Free typing alongside suggestions</td><td>No (use <code>&lt;datalist&gt;</code>)</td><td>Yes</td></tr>
  <tr><td>OS-native rendering</td><td>Yes</td><td>No</td></tr>
  <tr><td>Mobile-friendly</td><td>Yes (native pickers)</td><td>Depends on library</td></tr>
</table>

<p>For most use cases, native <code>&lt;optgroup&gt;</code> is enough &mdash; especially on mobile, where native pickers are far better than custom JavaScript ones. Reach for libraries (Choices.js, react-select, downshift) only when you genuinely need search or rich content. The HTML <code>&lt;selectlist&gt;</code> proposal (in development) will eventually let you style native selects, eliminating much of this trade-off.</p>
'''

ANSWERS[81] = r'''
<p><code>&lt;fieldset&gt;</code> groups related form controls and creates a meaningful boundary &mdash; both visually (with a default border) and semantically (for assistive technology). <code>&lt;legend&gt;</code> labels the group with a heading.</p>

<pre><code>&lt;form action="/signup" method="post"&gt;
  &lt;fieldset&gt;
    &lt;legend&gt;Personal Information&lt;/legend&gt;

    &lt;label&gt;
      First name
      &lt;input name="firstName" required&gt;
    &lt;/label&gt;

    &lt;label&gt;
      Last name
      &lt;input name="lastName" required&gt;
    &lt;/label&gt;

    &lt;label&gt;
      Date of birth
      &lt;input type="date" name="dob" required&gt;
    &lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Contact Preferences&lt;/legend&gt;

    &lt;label&gt;&lt;input type="checkbox" name="contact" value="email"&gt; Email&lt;/label&gt;
    &lt;label&gt;&lt;input type="checkbox" name="contact" value="phone"&gt; Phone&lt;/label&gt;
    &lt;label&gt;&lt;input type="checkbox" name="contact" value="sms"&gt; SMS&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Account Type&lt;/legend&gt;

    &lt;label&gt;&lt;input type="radio" name="account" value="free" checked&gt; Free&lt;/label&gt;
    &lt;label&gt;&lt;input type="radio" name="account" value="pro"&gt; Pro ($9.99/mo)&lt;/label&gt;
    &lt;label&gt;&lt;input type="radio" name="account" value="enterprise"&gt; Enterprise (contact)&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;button type="submit"&gt;Create Account&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p><strong>Why this is essential for accessibility:</strong></p>

<p><strong>Screen readers announce the legend</strong> as part of every nested input. When focus enters a checkbox, the user hears "Contact Preferences, Email, checkbox" &mdash; the group label provides context for every choice within.</p>

<p><strong>Especially critical for radio buttons:</strong> without a fieldset, screen readers see three orphan radios without knowing they&rsquo;re mutually exclusive choices for one decision. With <code>&lt;fieldset&gt;</code>+<code>&lt;legend&gt;</code>, the question (legend) and choices (radios) are linked.</p>

<p><strong>The disabled superpower:</strong></p>
<pre><code>&lt;fieldset disabled&gt;
  &lt;legend&gt;Disabled while loading...&lt;/legend&gt;
  &lt;input name="a"&gt;
  &lt;input name="b"&gt;
  &lt;button&gt;Submit&lt;/button&gt;
&lt;/fieldset&gt;</code></pre>

<p>Adding <code>disabled</code> to a <code>&lt;fieldset&gt;</code> disables every form control inside it &mdash; useful for showing "saving..." states without disabling each input individually. Toggle from JavaScript:</p>
<pre><code>fieldset.disabled = true;       // disable all
await saveData();
fieldset.disabled = false;      // re-enable</code></pre>

<p><strong>Custom styling</strong> &mdash; the default border and legend look dated; modern designs override:</p>
<pre><code>fieldset {
  border: none;
  padding: 0;
  margin: 0 0 2em;
}
legend {
  font-weight: 600;
  font-size: 1.1em;
  margin-bottom: 0.5em;
  padding: 0;
  display: block;
  width: 100%;
}</code></pre>

<p>Even when visually plain, the semantic structure remains for assistive technology. Don&rsquo;t skip the elements just because the default appearance doesn&rsquo;t match your design.</p>

<p><strong>When to use a fieldset:</strong></p>
<table>
  <tr><th>Use case</th><th>Use fieldset?</th></tr>
  <tr><td>Group of radio buttons (one decision)</td><td>Always</td></tr>
  <tr><td>Group of related checkboxes (one question)</td><td>Always</td></tr>
  <tr><td>Multi-section long form (Personal info, Address, Payment)</td><td>Yes &mdash; helps users orient</td></tr>
  <tr><td>Single-input form</td><td>Skip &mdash; a label is enough</td></tr>
  <tr><td>Visual border without group meaning</td><td>Use a div + CSS border</td></tr>
</table>

<p><strong>Required group indication</strong> &mdash; for radios, mark only ONE input <code>required</code> in the group; the browser treats this as "the entire group requires a selection":</p>
<pre><code>&lt;fieldset&gt;
  &lt;legend&gt;Choose a plan *&lt;/legend&gt;
  &lt;label&gt;&lt;input type="radio" name="plan" value="free" required&gt; Free&lt;/label&gt;
  &lt;label&gt;&lt;input type="radio" name="plan" value="pro"&gt; Pro&lt;/label&gt;
&lt;/fieldset&gt;</code></pre>
'''

ANSWERS[82] = r'''
<p>Custom scrollbars are styled with the <code>::-webkit-scrollbar</code> family of pseudo-elements (Chromium and Safari) and the standardized <code>scrollbar-width</code> + <code>scrollbar-color</code> properties (Firefox and modern Chromium). The two systems coexist in 2026 &mdash; you write both for full coverage.</p>

<pre><code>&lt;div class="scroll-container"&gt;
  &lt;p&gt;Lots of scrollable content...&lt;/p&gt;
  &lt;p&gt;...repeat many times...&lt;/p&gt;
&lt;/div&gt;

&lt;style&gt;
  .scroll-container {
    height: 300px;
    overflow-y: auto;
    padding: 1em;
    border: 1px solid #ddd;
  }

  /* Modern standard (Firefox + Chromium 121+) */
  .scroll-container {
    scrollbar-width: thin;                /* auto | thin | none */
    scrollbar-color: #888 #f0f0f0;        /* thumb track */
  }

  /* WebKit / Chromium specifics for full styling control */
  .scroll-container::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  .scroll-container::-webkit-scrollbar-track {
    background: #f0f0f0;
    border-radius: 4px;
  }
  .scroll-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }
  .scroll-container::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
&lt;/style&gt;</code></pre>

<p><strong>The standard properties (preferred):</strong></p>
<table>
  <tr><th>Property</th><th>Values</th></tr>
  <tr><td><code>scrollbar-width</code></td><td><code>auto</code> (default) | <code>thin</code> | <code>none</code> (hide entirely)</td></tr>
  <tr><td><code>scrollbar-color</code></td><td><code>thumb track</code> &mdash; two color values</td></tr>
  <tr><td><code>scrollbar-gutter</code></td><td><code>auto</code> | <code>stable</code> | <code>stable both-edges</code> &mdash; reserves space</td></tr>
</table>

<p><strong>WebKit pseudo-elements</strong> (more granular control):</p>
<table>
  <tr><th>Pseudo</th><th>Targets</th></tr>
  <tr><td><code>::-webkit-scrollbar</code></td><td>The whole scrollbar</td></tr>
  <tr><td><code>::-webkit-scrollbar-track</code></td><td>The background track</td></tr>
  <tr><td><code>::-webkit-scrollbar-thumb</code></td><td>The draggable thumb</td></tr>
  <tr><td><code>::-webkit-scrollbar-button</code></td><td>The arrow buttons (often hidden)</td></tr>
  <tr><td><code>::-webkit-scrollbar-corner</code></td><td>Corner where vertical and horizontal meet</td></tr>
</table>

<p><strong>Hide scrollbar but keep scrolling:</strong></p>
<pre><code>.invisible-scroll {
  scrollbar-width: none;                /* Firefox */
}
.invisible-scroll::-webkit-scrollbar {
  display: none;                        /* WebKit */
}</code></pre>

<p>Useful for custom-built carousels or scroll-snap layouts where the scrollbar would distract.</p>

<p><strong>Avoid layout shift with <code>scrollbar-gutter</code>:</strong></p>
<pre><code>.always-reserve-space {
  overflow: auto;
  scrollbar-gutter: stable;
}</code></pre>

<p>Without this, content shifts when a scrollbar appears (after content grows). With <code>stable</code>, the gutter is always reserved &mdash; no jump.</p>

<p><strong>Caveats and accessibility considerations:</strong></p>
<ul>
  <li><strong>Don&rsquo;t hide scrollbars without a reason</strong> &mdash; users with motor impairments may need them; touch users have alternative gestures, but mouse users rely on scrollbars.</li>
  <li><strong>Maintain contrast</strong> &mdash; thumb should contrast against track for visibility.</li>
  <li><strong>Don&rsquo;t shrink scrollbars too thin</strong> &mdash; they become hard to grab on desktop.</li>
  <li><strong>Test on multiple platforms</strong> &mdash; macOS hides scrollbars by default until you scroll; Windows shows them always; mobile platforms have different conventions.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> if you animate scroll behavior.</li>
</ul>

<p><strong>For custom scroll experiences (smooth scrolling, scroll snap):</strong></p>
<pre><code>html {
  scroll-behavior: smooth;
}
.snap-container {
  scroll-snap-type: y mandatory;
  overflow-y: auto;
  height: 100vh;
}
.snap-item {
  scroll-snap-align: start;
  height: 100vh;
}</code></pre>

<p>These properties enable scroll snapping (each section locks into place) and smooth scrolling for anchor jumps &mdash; native, performant, no JavaScript needed.</p>
'''

ANSWERS[83] = r'''
<p>The <code>&lt;s&gt;</code> element marks <strong>text that is no longer accurate or relevant</strong> &mdash; not text that&rsquo;s been deleted from a document. It renders with strikethrough by default, but the meaning is semantic: "this used to be true; it isn&rsquo;t anymore."</p>

<pre><code>&lt;p&gt;The price is &lt;s&gt;$99.99&lt;/s&gt; $79.99 (sale!).&lt;/p&gt;

&lt;p&gt;Open Mon-Fri &lt;s&gt;9am-5pm&lt;/s&gt; &lt;ins&gt;8am-6pm starting June 1&lt;/ins&gt;.&lt;/p&gt;

&lt;p&gt;Status: &lt;s&gt;Out of stock&lt;/s&gt; In stock!&lt;/p&gt;</code></pre>

<p><strong>Default styling</strong> &mdash; browsers strikethrough <code>&lt;s&gt;</code> content automatically:</p>
<pre><code>s { text-decoration: line-through; }</code></pre>

<p><strong><code>&lt;s&gt;</code> vs <code>&lt;del&gt;</code> &mdash; the crucial distinction:</strong></p>
<table>
  <tr><th></th><th><code>&lt;s&gt;</code></th><th><code>&lt;del&gt;</code></th></tr>
  <tr><td>Means</td><td>"No longer accurate or relevant"</td><td>"Deleted from the document"</td></tr>
  <tr><td>Use for</td><td>Old prices, outdated info, superseded values</td><td>Edit history, document revisions</td></tr>
  <tr><td>Pairs with</td><td>(Implicit replacement nearby)</td><td><code>&lt;ins&gt;</code> for what&rsquo;s being added</td></tr>
  <tr><td>Has dates/cite</td><td>No</td><td>Yes (<code>cite</code>, <code>datetime</code>)</td></tr>
</table>

<p><strong>Concrete example illustrating the difference:</strong></p>
<pre><code>&lt;!-- &lt;s&gt;: this fact is now wrong/irrelevant --&gt;
&lt;p&gt;Earth has &lt;s&gt;9&lt;/s&gt; 8 planets (Pluto was reclassified).&lt;/p&gt;

&lt;!-- &lt;del&gt;: tracking edits to a document --&gt;
&lt;p&gt;The meeting is on &lt;del datetime="2026-04-20T10:00"&gt;Tuesday&lt;/del&gt;
   &lt;ins datetime="2026-04-20T10:00"&gt;Wednesday&lt;/ins&gt;.&lt;/p&gt;</code></pre>

<p>The first uses <code>&lt;s&gt;</code> because the old number "9" is no longer correct. The second uses <code>&lt;del&gt;</code> + <code>&lt;ins&gt;</code> because we&rsquo;re showing an edit to the document &mdash; with optional <code>datetime</code> attributes for the edit timestamps.</p>

<p><strong>Was <code>&lt;s&gt;</code> deprecated?</strong> Almost. HTML4 deprecated <code>&lt;s&gt;</code> as purely presentational. HTML5 brought it back with semantic meaning ("no longer accurate") to give authors a non-edit-tracking way to indicate strikethrough text. So:</p>
<ul>
  <li><strong>HTML4:</strong> <code>&lt;s&gt;</code> deprecated, "use CSS instead."</li>
  <li><strong>HTML5+:</strong> <code>&lt;s&gt;</code> reborn with refined meaning, valid and useful.</li>
</ul>

<p><strong>The related <code>&lt;strike&gt;</code> element</strong> WAS removed in HTML5 (replaced by <code>&lt;s&gt;</code> or CSS):</p>
<pre><code>&lt;!-- HTML4: deprecated --&gt;
&lt;strike&gt;Old text&lt;/strike&gt;

&lt;!-- HTML5+: use &lt;s&gt; for "no longer relevant" --&gt;
&lt;s&gt;Old text&lt;/s&gt;

&lt;!-- Or CSS for purely visual strikethrough --&gt;
&lt;span style="text-decoration: line-through"&gt;Decorative&lt;/span&gt;</code></pre>

<p><strong>Don&rsquo;t use <code>&lt;s&gt;</code> for:</strong></p>
<ul>
  <li>Edit history (use <code>&lt;del&gt;</code>).</li>
  <li>Pure decorative strikethrough (use a CSS class).</li>
  <li>Indicating completed to-do items (use <code>aria-checked</code> + CSS).</li>
</ul>

<p><strong>Accessibility note:</strong> screen readers don&rsquo;t typically announce <code>&lt;s&gt;</code> with any inflection &mdash; users hear the content as if it weren&rsquo;t struck through. For prices, the context (followed by a new price) usually makes the meaning clear. For critical information that the strikethrough conveys, add explicit text:</p>
<pre><code>&lt;p&gt;Was &lt;s&gt;$99.99&lt;/s&gt;, now $79.99 (save $20).&lt;/p&gt;
&lt;!-- The "Was" word makes the meaning explicit for screen readers --&gt;</code></pre>

<p>Or use <code>aria-label</code> on a wrapper to clarify when the visual strikethrough is the only meaning indicator.</p>
'''

ANSWERS[84] = r'''
<p>HTML5 + CSS multi-column layouts come in two flavors: <strong>CSS columns</strong> for fluid text that flows naturally between columns (like a newspaper), and <strong>CSS Grid</strong> for structured items placed in a grid (like cards or dashboards). Each suits different content.</p>

<p><strong>CSS columns &mdash; fluid text:</strong></p>
<pre><code>&lt;article class="magazine"&gt;
  &lt;h2&gt;The History of the Web&lt;/h2&gt;
  &lt;p&gt;The web has evolved dramatically since Tim Berners-Lee
  proposed it at CERN in 1989...&lt;/p&gt;
  &lt;p&gt;In the 1990s, designers worked with table layouts and
  static HTML. The introduction of CSS in 1996 separated
  presentation from content...&lt;/p&gt;
  &lt;p&gt;Today, modern techniques like Flexbox and Grid give
  developers unprecedented control over complex layouts...&lt;/p&gt;
&lt;/article&gt;

&lt;style&gt;
  .magazine {
    columns: 3 250px;            /* 3 columns, each at least 250px */
    column-gap: 2em;
    column-rule: 1px solid #ddd;
    column-fill: balance;        /* equalize column heights */
  }
  .magazine h2 {
    column-span: all;            /* heading spans all columns */
    margin-bottom: 1em;
  }
  .magazine p {
    margin-top: 0;
    break-inside: avoid;         /* prevent splitting paragraphs across columns */
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>columns</code> shorthand:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>column-count</code></td><td>Exact number of columns</td></tr>
  <tr><td><code>column-width</code></td><td>Minimum column width; browser determines count</td></tr>
  <tr><td><code>columns: 3 250px</code></td><td>Combo &mdash; up to 3 columns, but at least 250px each</td></tr>
  <tr><td><code>column-gap</code></td><td>Space between columns</td></tr>
  <tr><td><code>column-rule</code></td><td>Vertical line between columns (border-like syntax)</td></tr>
  <tr><td><code>column-span</code></td><td><code>none</code> or <code>all</code> &mdash; element spans all columns</td></tr>
</table>

<p><strong>CSS Grid for structured layouts:</strong></p>
<pre><code>&lt;section class="features"&gt;
  &lt;div class="feature"&gt;&lt;h3&gt;Fast&lt;/h3&gt;&lt;p&gt;Loads in milliseconds.&lt;/p&gt;&lt;/div&gt;
  &lt;div class="feature"&gt;&lt;h3&gt;Simple&lt;/h3&gt;&lt;p&gt;Zero configuration.&lt;/p&gt;&lt;/div&gt;
  &lt;div class="feature"&gt;&lt;h3&gt;Secure&lt;/h3&gt;&lt;p&gt;End-to-end encrypted.&lt;/p&gt;&lt;/div&gt;
  &lt;div class="feature"&gt;&lt;h3&gt;Open&lt;/h3&gt;&lt;p&gt;MIT-licensed.&lt;/p&gt;&lt;/div&gt;
&lt;/section&gt;

&lt;style&gt;
  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2em;
    padding: 2em;
  }
  .feature {
    padding: 1.5em;
    border: 1px solid #eee;
    border-radius: 8px;
  }
&lt;/style&gt;</code></pre>

<p><strong>Columns vs Grid &mdash; choose by content type:</strong></p>
<table>
  <tr><th></th><th>CSS columns</th><th>CSS Grid</th></tr>
  <tr><td>Best for</td><td>Article text flowing across columns</td><td>Independent items in a grid</td></tr>
  <tr><td>Content flow</td><td>Top-to-bottom in column 1, then 2, then 3</td><td>Each item placed independently</td></tr>
  <tr><td>Item heights</td><td>Browser balances</td><td>Each row aligns; items can span rows</td></tr>
  <tr><td>Responsive</td><td><code>columns: 3 250px</code> wraps automatically</td><td><code>auto-fit</code> + <code>minmax</code> wraps automatically</td></tr>
  <tr><td>Examples</td><td>Newspaper articles, FAQ lists, tag clouds</td><td>Cards, photo galleries, dashboards</td></tr>
</table>

<p><strong>Avoiding awkward breaks</strong> &mdash; the <code>break-inside</code> property prevents content from being split across columns or pages:</p>
<pre><code>.no-break { break-inside: avoid; }      /* never split this element */
.always-break { break-after: column; }   /* force a break after */</code></pre>

<p>Useful when a card or quote shouldn&rsquo;t be cut in half between two columns. Equivalent properties for print: <code>page-break-inside</code>.</p>

<p>For most content in 2026, CSS Grid is the workhorse. <code>columns</code> shines for actual prose &mdash; magazine layouts, long FAQ lists, tag clouds &mdash; where text should naturally flow.</p>
'''

ANSWERS[85] = r'''
<p>Graceful degradation is a design philosophy that builds for the <strong>full modern experience first</strong>, then ensures the site remains usable on older browsers or in restricted environments. Features that won&rsquo;t work fall back gracefully without breaking the page.</p>

<p>It&rsquo;s the conceptual <em>opposite</em> of progressive enhancement, though both achieve similar end states.</p>

<table>
  <tr><th></th><th>Progressive enhancement</th><th>Graceful degradation</th></tr>
  <tr><td>Starts with</td><td>Minimum baseline (semantic HTML)</td><td>Full modern experience</td></tr>
  <tr><td>Adds</td><td>Layers of enhancement</td><td>Fallbacks for older browsers</td></tr>
  <tr><td>Ensures</td><td>Old browsers get something usable</td><td>Old browsers don&rsquo;t see a broken page</td></tr>
  <tr><td>Mindset</td><td>"Build up"</td><td>"Build down"</td></tr>
</table>

<p><strong>Concrete graceful-degradation pattern</strong> &mdash; a slick CSS Grid layout with a flexbox fallback:</p>
<pre><code>&lt;style&gt;
  /* Baseline: flexbox works everywhere */
  .gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }
  .gallery &gt; * {
    flex: 1 1 250px;
  }

  /* Enhancement: Grid takes over in modern browsers */
  @supports (display: grid) {
    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1rem;
    }
  }
&lt;/style&gt;</code></pre>

<p>The <code>@supports</code> at-rule (feature query) checks browser capability at runtime. If <code>display: grid</code> works, use it; otherwise, the baseline flexbox layout still produces a usable result.</p>

<p><strong>JavaScript example &mdash; native dialog with library fallback:</strong></p>
<pre><code>if (typeof HTMLDialogElement !== "undefined") {
  // Modern browser — use native &lt;dialog&gt;
  document.getElementById("modal").showModal();
} else {
  // Old browser — show a custom modal library implementation
  showLegacyModal();
}</code></pre>

<p><strong>HTML5 fallback content patterns:</strong></p>
<pre><code>&lt;!-- &lt;video&gt; with download fallback --&gt;
&lt;video controls src="movie.mp4"&gt;
  &lt;p&gt;Your browser doesn&rsquo;t support video.
     &lt;a href="movie.mp4"&gt;Download the video&lt;/a&gt;.&lt;/p&gt;
&lt;/video&gt;

&lt;!-- &lt;canvas&gt; with text fallback --&gt;
&lt;canvas&gt;
  Your browser doesn&rsquo;t support canvas.
&lt;/canvas&gt;

&lt;!-- &lt;picture&gt; with format fallback --&gt;
&lt;picture&gt;
  &lt;source srcset="hero.avif" type="image/avif"&gt;
  &lt;source srcset="hero.webp" type="image/webp"&gt;
  &lt;img src="hero.jpg" alt="..."&gt;
&lt;/picture&gt;

&lt;!-- Form input fallback (older browsers don&rsquo;t support type="date") --&gt;
&lt;input type="date" name="dob" placeholder="YYYY-MM-DD"&gt;
&lt;!-- In legacy browsers, this falls back to type="text" automatically --&gt;</code></pre>

<p><strong>Cross-cutting strategies:</strong></p>
<ul>
  <li><strong>CSS feature queries (<code>@supports</code>)</strong> &mdash; conditional styling based on browser capability.</li>
  <li><strong>Polyfills</strong> &mdash; libraries that add missing APIs to older browsers (e.g. <code>core-js</code> for JavaScript).</li>
  <li><strong>Fallback elements</strong> &mdash; native HTML5 elements include fallback content for browsers that don&rsquo;t recognize them.</li>
  <li><strong>Type="text" fallback</strong> &mdash; unknown <code>type</code> attribute on inputs falls back to <code>text</code>; users get a less convenient but still usable input.</li>
  <li><strong>Browserslist + Babel</strong> &mdash; transpile modern JS down to ES2015 or earlier for older browsers.</li>
</ul>

<p><strong>Modern reality (2026):</strong> evergreen browsers (Chrome, Firefox, Safari, Edge) auto-update, so the gap between cutting-edge and "old" is much narrower than it was in 2015. Graceful degradation is mostly about supporting:</p>
<ul>
  <li>Specific corporate/locked-down environments (older Edge or IE in some industries).</li>
  <li>Smart TVs and embedded devices with stuck browsers.</li>
  <li>Users with extensions that disable features (NoScript, content blockers).</li>
  <li>Network failures or partial loads.</li>
</ul>

<p>For most modern projects, progressive enhancement is the more popular framing &mdash; build a robust baseline, layer on enhancements. But the techniques (feature queries, fallbacks, polyfills) are the same; the philosophy just differs in starting point.</p>
'''

ANSWERS[86] = r'''
<p><code>&lt;input type="color"&gt;</code> renders a <strong>native color picker</strong> in the browser. The user clicks the input and the OS&rsquo;s built-in color chooser appears (eyedropper, hex/RGB sliders, recent colors). The submitted value is a hex string like <code>#ff6b35</code>.</p>

<pre><code>&lt;form&gt;
  &lt;label&gt;
    Theme color:
    &lt;input type="color"
           name="theme"
           value="#0066cc"&gt;
  &lt;/label&gt;

  &lt;label&gt;
    Accent color:
    &lt;input type="color"
           name="accent"
           value="#ff6b35"
           list="brand-colors"&gt;
  &lt;/label&gt;

  &lt;datalist id="brand-colors"&gt;
    &lt;option&gt;#0066cc&lt;/option&gt;
    &lt;option&gt;#ff6b35&lt;/option&gt;
    &lt;option&gt;#28a745&lt;/option&gt;
    &lt;option&gt;#dc3545&lt;/option&gt;
  &lt;/datalist&gt;
&lt;/form&gt;</code></pre>

<p><strong>Behavior and constraints:</strong></p>
<ul>
  <li><strong>Value format is always 7-character hex</strong>: <code>#rrggbb</code> &mdash; lowercase, no alpha channel.</li>
  <li><strong>Default value</strong> required for proper rendering &mdash; defaults to <code>#000000</code> if omitted.</li>
  <li><strong>No alpha</strong> &mdash; native input doesn&rsquo;t support transparency. For RGBA, build a custom picker.</li>
  <li><strong>Limited styling</strong> &mdash; the swatch and picker are mostly OS-controlled; you can size the input but not redesign the picker UI.</li>
  <li><strong>The <code>list</code> attribute</strong> with a <code>&lt;datalist&gt;</code> provides preset suggestions (limited browser support &mdash; Firefox shows them; Chromium ignores).</li>
</ul>

<p><strong>Live update example &mdash; preview color changes:</strong></p>
<pre><code>&lt;form id="theme-form"&gt;
  &lt;label&gt;
    Background color:
    &lt;input type="color" id="bg" value="#f0f0f0"&gt;
  &lt;/label&gt;
  &lt;label&gt;
    Text color:
    &lt;input type="color" id="fg" value="#333333"&gt;
  &lt;/label&gt;
&lt;/form&gt;

&lt;div id="preview" class="preview"&gt;
  Sample text in chosen colors.
&lt;/div&gt;

&lt;script&gt;
  const bg = document.getElementById("bg");
  const fg = document.getElementById("fg");
  const preview = document.getElementById("preview");

  function update() {
    preview.style.background = bg.value;
    preview.style.color = fg.value;
  }
  bg.addEventListener("input", update);
  fg.addEventListener("input", update);
  update();
&lt;/script&gt;</code></pre>

<p>The <code>input</code> event fires on every change while the picker is open &mdash; great for real-time previews. The <code>change</code> event fires only when the picker closes.</p>

<p><strong>EyeDropper API for advanced cases:</strong></p>
<pre><code>// 2026: well-supported in Chromium browsers
button.addEventListener("click", async () =&gt; {
  if (!window.EyeDropper) {
    alert("Use the color input instead — your browser doesn&rsquo;t support EyeDropper.");
    return;
  }
  const eye = new EyeDropper();
  const result = await eye.open();
  console.log(result.sRGBHex);   // "#ff6b35"
});</code></pre>

<p>The EyeDropper API lets users sample colors from anywhere on screen &mdash; including outside the browser window in some implementations.</p>

<p><strong>Validation considerations:</strong></p>
<ul>
  <li>Always re-check on the server &mdash; the value should match <code>/^#[0-9a-f]{6}$/i</code>.</li>
  <li>Convert to other formats server-side if needed (RGB, HSL).</li>
  <li>For accessibility, ensure chosen colors meet WCAG contrast (4.5:1 for normal text, 3:1 for large/UI). Validate this and warn users.</li>
</ul>

<p><strong>When to build a custom color picker:</strong> if you need alpha (RGBA), HSL/HSV interfaces, theme palettes, custom swatches, or full styling control. Libraries: <code>iro.js</code>, <code>react-colorful</code> (1.5KB!), or design system pickers (Radix, shadcn). Otherwise, use native &mdash; it&rsquo;s free, accessible, and integrates with the user&rsquo;s OS.</p>
'''

ANSWERS[87] = r'''
<p><code>&lt;ins&gt;</code> and <code>&lt;del&gt;</code> mark <strong>edits to a document</strong> &mdash; <code>&lt;ins&gt;</code> for inserted (added) content, <code>&lt;del&gt;</code> for deleted (removed) content. They&rsquo;re used for tracking changes, version diffs, and editorial revisions.</p>

<pre><code>&lt;p&gt;The meeting is on
   &lt;del datetime="2026-04-20T10:00"&gt;Tuesday at 2pm&lt;/del&gt;
   &lt;ins datetime="2026-04-20T10:00"&gt;Wednesday at 3pm&lt;/ins&gt;.&lt;/p&gt;

&lt;p&gt;Total attendees:
   &lt;del&gt;42&lt;/del&gt;
   &lt;ins&gt;47&lt;/ins&gt;
   (5 last-minute additions)&lt;/p&gt;

&lt;article&gt;
  &lt;h2&gt;Privacy Policy&lt;/h2&gt;
  &lt;p&gt;We collect your &lt;del&gt;name and email&lt;/del&gt;
     &lt;ins&gt;name, email, and IP address&lt;/ins&gt; when you sign up.&lt;/p&gt;
&lt;/article&gt;</code></pre>

<p><strong>Default styling:</strong></p>
<table>
  <tr><th>Tag</th><th>Default style</th></tr>
  <tr><td><code>&lt;ins&gt;</code></td><td>Underlined</td></tr>
  <tr><td><code>&lt;del&gt;</code></td><td>Strikethrough</td></tr>
</table>

<p>Customize for clearer diff visualization:</p>
<pre><code>ins {
  background: #e6ffe6;
  text-decoration: none;
  color: #0a5d0a;
  padding: 0 0.2em;
}
del {
  background: #ffe6e6;
  color: #8b0000;
  padding: 0 0.2em;
}</code></pre>

<p><strong>Useful attributes:</strong></p>
<table>
  <tr><th>Attribute</th><th>Purpose</th></tr>
  <tr><td><code>cite</code></td><td>URL of a document explaining the change</td></tr>
  <tr><td><code>datetime</code></td><td>When the edit was made (ISO 8601 format)</td></tr>
</table>

<pre><code>&lt;p&gt;The price is now
   &lt;del cite="/changelog/2026-04-25"
        datetime="2026-04-25T09:00:00Z"&gt;$99.99&lt;/del&gt;
   &lt;ins cite="/changelog/2026-04-25"
        datetime="2026-04-25T09:00:00Z"&gt;$79.99&lt;/ins&gt;.&lt;/p&gt;</code></pre>

<p>The attributes are invisible to users but available to scrapers, version-tracking tools, and automated diff systems.</p>

<p><strong>Block-level vs inline:</strong> both elements are <em>transparent</em> &mdash; they take on the display behavior of their parent and can wrap either inline content or block content:</p>
<pre><code>&lt;!-- Inline edits within a paragraph --&gt;
&lt;p&gt;Visit &lt;del&gt;Paris&lt;/del&gt; &lt;ins&gt;Rome&lt;/ins&gt; this summer.&lt;/p&gt;

&lt;!-- Block-level: an entire deleted paragraph --&gt;
&lt;del&gt;
  &lt;p&gt;This entire paragraph is being removed in this edit.&lt;/p&gt;
&lt;/del&gt;

&lt;!-- Block-level: an entire inserted section --&gt;
&lt;ins&gt;
  &lt;article&gt;
    &lt;h2&gt;New Section&lt;/h2&gt;
    &lt;p&gt;This whole article is new.&lt;/p&gt;
  &lt;/article&gt;
&lt;/ins&gt;</code></pre>

<p><strong>Distinction from <code>&lt;s&gt;</code> (no longer accurate):</strong></p>
<table>
  <tr><th></th><th><code>&lt;del&gt;</code></th><th><code>&lt;s&gt;</code></th></tr>
  <tr><td>Means</td><td>"Removed from document"</td><td>"No longer accurate or relevant"</td></tr>
  <tr><td>Pairs with</td><td><code>&lt;ins&gt;</code> for replacement</td><td>(implicit replacement nearby)</td></tr>
  <tr><td>Has datetime</td><td>Yes</td><td>No</td></tr>
  <tr><td>Use for</td><td>Edit tracking, revisions</td><td>Old prices, outdated info</td></tr>
</table>

<p><strong>Real-world use cases:</strong></p>
<ul>
  <li><strong>Wiki / documentation systems</strong> &mdash; show edit history with strikethrough on removed text.</li>
  <li><strong>Legal documents</strong> &mdash; mark amendments to contracts, terms of service.</li>
  <li><strong>Version diffs</strong> &mdash; compare document versions side-by-side.</li>
  <li><strong>Code change reviews</strong> (though most use line-based diffs instead).</li>
  <li><strong>Editorial workflows</strong> &mdash; track what an editor added or removed before publishing.</li>
</ul>

<p><strong>Accessibility:</strong></p>
<ul>
  <li>Screen readers may or may not announce the edits as such &mdash; behavior varies.</li>
  <li>For critical edit tracking, add explicit text or visually-hidden cues:
    <pre><code>&lt;del&gt;&lt;span class="sr-only"&gt;Removed: &lt;/span&gt;old text&lt;/del&gt;
&lt;ins&gt;&lt;span class="sr-only"&gt;Added: &lt;/span&gt;new text&lt;/ins&gt;</code></pre>
  </li>
</ul>
'''

ANSWERS[88] = r'''
<p>Accordions show a list of collapsible sections where clicking a header expands to reveal content. The native <code>&lt;details&gt;</code> + <code>&lt;summary&gt;</code> combination handles this with zero JavaScript &mdash; correct keyboard, screen reader, and "find on page" behavior built in.</p>

<pre><code>&lt;div class="accordion"&gt;
  &lt;details name="faq"&gt;
    &lt;summary&gt;What is your return policy?&lt;/summary&gt;
    &lt;p&gt;We accept returns within 30 days of purchase.
       Items must be in original condition...&lt;/p&gt;
  &lt;/details&gt;

  &lt;details name="faq"&gt;
    &lt;summary&gt;How long does shipping take?&lt;/summary&gt;
    &lt;p&gt;Standard shipping takes 3-5 business days.
       Express shipping is 1-2 days.&lt;/p&gt;
  &lt;/details&gt;

  &lt;details name="faq"&gt;
    &lt;summary&gt;Do you ship internationally?&lt;/summary&gt;
    &lt;p&gt;Yes, we ship to over 50 countries.
       Customs fees may apply...&lt;/p&gt;
  &lt;/details&gt;

  &lt;details name="faq"&gt;
    &lt;summary&gt;Can I track my order?&lt;/summary&gt;
    &lt;p&gt;Once shipped, you&rsquo;ll receive a tracking number
       via email...&lt;/p&gt;
  &lt;/details&gt;
&lt;/div&gt;

&lt;style&gt;
  .accordion details {
    border: 1px solid #ddd;
    border-radius: 6px;
    margin-bottom: 0.5em;
    overflow: hidden;
  }
  .accordion summary {
    padding: 1em 1.5em;
    cursor: pointer;
    background: #f8f9fa;
    list-style: none;        /* hide default triangle */
    font-weight: 600;
    user-select: none;
    position: relative;
    padding-right: 2.5em;
  }
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
  .accordion details &gt; p {
    padding: 1em 1.5em;
    margin: 0;
  }

  /* Responsive: full-width on mobile */
  @media (max-width: 600px) {
    .accordion details {
      border-left: none;
      border-right: none;
      border-radius: 0;
    }
  }
&lt;/style&gt;</code></pre>

<p><strong>The <code>name</code> attribute creates radio-button behavior</strong> &mdash; opening one auto-closes others sharing the same name. New in 2024, well-supported by 2026:</p>
<pre><code>&lt;details name="faq"&gt;...&lt;/details&gt;
&lt;details name="faq"&gt;...&lt;/details&gt;</code></pre>

<p>Without the <code>name</code> attribute, multiple sections can be open simultaneously &mdash; sometimes desirable. Choose based on UX intent.</p>

<p><strong>Animated expand/collapse</strong> &mdash; modern CSS using the <code>interpolate-size</code> property:</p>
<pre><code>:root {
  interpolate-size: allow-keywords;
}

.accordion details {
  transition: height 0.3s ease;
  height: auto;
  overflow: hidden;
}
.accordion details:not([open]) {
  height: calc(2em + 1em);   /* approximately summary height */
}</code></pre>

<p>The <code>interpolate-size</code> property (2024+) lets browsers animate between explicit sizes and <code>auto</code>, which was previously impossible. For broader browser support, use the <code>height</code> property combined with <code>::details-content</code> (most modern Chromium browsers).</p>

<p><strong>Built-in benefits of <code>&lt;details&gt;</code>:</strong></p>
<ul>
  <li>Keyboard accessible by default (Enter, Space).</li>
  <li>Screen readers announce as "disclosure widget, collapsed/expanded."</li>
  <li>Browser&rsquo;s find-in-page (Ctrl/Cmd+F) auto-expands sections containing matches.</li>
  <li><code>toggle</code> event fires on state change &mdash; track analytics or save state.</li>
  <li>Can be open by default with <code>open</code> attribute.</li>
</ul>

<p><strong>For more control or rich animation</strong>, custom JavaScript accordions still have a place:</p>
<pre><code>&lt;div class="js-accordion"&gt;
  &lt;button class="acc-trigger" aria-expanded="false" aria-controls="panel1"&gt;
    Section 1
  &lt;/button&gt;
  &lt;div id="panel1" class="acc-panel" hidden&gt;
    &lt;p&gt;Content...&lt;/p&gt;
  &lt;/div&gt;
&lt;/div&gt;</code></pre>

<p>Libraries like Radix UI Accordion or Headless UI Disclosure handle the full ARIA model: keyboard arrows for navigation, animation, focus management, and unmount-on-close patterns.</p>
'''

ANSWERS[89] = r'''
<p>The <code>&lt;summary&gt;</code> element is the <strong>always-visible label inside a <code>&lt;details&gt;</code> element</strong>. Clicking it toggles the disclosure widget open or closed; the rest of the <code>&lt;details&gt;</code> content shows or hides based on the toggle state.</p>

<pre><code>&lt;details&gt;
  &lt;summary&gt;What&rsquo;s included in the warranty?&lt;/summary&gt;
  &lt;p&gt;Two-year coverage on parts and labor. Excludes
     damage from accidents or unauthorized modifications.&lt;/p&gt;
  &lt;p&gt;Contact support@example.com for warranty claims.&lt;/p&gt;
&lt;/details&gt;</code></pre>

<p><strong>Rules:</strong></p>
<ul>
  <li><strong>Must be the first child</strong> of <code>&lt;details&gt;</code>.</li>
  <li><strong>Only one <code>&lt;summary&gt;</code></strong> per <code>&lt;details&gt;</code>.</li>
  <li><strong>If omitted</strong>, browsers show a default label like "Details."</li>
  <li><strong>Can contain inline content</strong> (text, <code>&lt;strong&gt;</code>, <code>&lt;span&gt;</code>) &mdash; not block elements like <code>&lt;p&gt;</code>.</li>
</ul>

<p><strong>Built-in interactivity</strong> (no JavaScript needed):</p>
<ul>
  <li>Click toggles open/closed.</li>
  <li>Keyboard: Tab focuses the summary; Enter or Space toggles.</li>
  <li>Screen readers announce as "disclosure triangle, [summary text], collapsed/expanded."</li>
  <li>Browser&rsquo;s find-in-page (Ctrl/Cmd+F) auto-expands sections containing matched text.</li>
</ul>

<p><strong>Customizing the disclosure marker</strong> (the default arrow):</p>
<pre><code>summary {
  list-style: none;       /* remove default marker (modern syntax) */
  cursor: pointer;
  padding: 0.5em 1em;
  font-weight: 600;
  position: relative;
  padding-left: 2em;
}

/* Custom arrow that rotates on open */
summary::before {
  content: "&rsaquo;";
  position: absolute;
  left: 0.7em;
  top: 50%;
  transform: translateY(-50%);
  transition: transform 0.2s;
  color: #0066cc;
}
details[open] &gt; summary::before {
  transform: translateY(-50%) rotate(90deg);
}

/* For older Chromium browsers */
summary::-webkit-details-marker {
  display: none;
}</code></pre>

<p><strong>The <code>open</code> attribute</strong> on <code>&lt;details&gt;</code> sets the default state:</p>
<pre><code>&lt;details open&gt;
  &lt;summary&gt;Welcome!&lt;/summary&gt;
  &lt;p&gt;This section is open by default.&lt;/p&gt;
&lt;/details&gt;</code></pre>

<p><strong>Listening to state changes:</strong></p>
<pre><code>const details = document.querySelector("details");

details.addEventListener("toggle", () =&gt; {
  console.log("Now", details.open ? "open" : "closed");

  // Save preference
  localStorage.setItem("section-state", details.open);

  // Track analytics
  analytics.track("section_toggled", { open: details.open });
});</code></pre>

<p>The <code>toggle</code> event fires after every open or close. Useful for analytics, state persistence, or triggering animations.</p>

<p><strong>Accordion pattern using <code>name</code>:</strong></p>
<pre><code>&lt;details name="faq"&gt;
  &lt;summary&gt;Question 1&lt;/summary&gt;
  &lt;p&gt;Answer 1&lt;/p&gt;
&lt;/details&gt;
&lt;details name="faq"&gt;
  &lt;summary&gt;Question 2&lt;/summary&gt;
  &lt;p&gt;Answer 2&lt;/p&gt;
&lt;/details&gt;</code></pre>

<p>Sharing <code>name="faq"</code> creates radio-style behavior: opening one auto-closes the others. Without <code>name</code>, multiple sections stay open independently.</p>

<p><strong>Common use cases:</strong></p>
<ul>
  <li>FAQ sections (the canonical use).</li>
  <li>"Show more" / "Read more" expandable content.</li>
  <li>Settings panels with collapsible categories.</li>
  <li>Code documentation with collapsible examples.</li>
  <li>Comments with expandable replies.</li>
  <li>Mobile menus that expand on tap.</li>
</ul>

<p>Native <code>&lt;summary&gt;</code> + <code>&lt;details&gt;</code> replaces 90% of "I need a custom collapsible widget" libraries with built-in HTML &mdash; better accessibility, smaller bundle size, and zero implementation cost.</p>
'''

ANSWERS[90] = r'''
<p>Print stylesheets target the <code>print</code> media type to <strong>customize how a page renders when printed (or saved as PDF)</strong>. Browsers apply these rules instead of (or in addition to) screen styles.</p>

<p><strong>Three ways to attach print styles:</strong></p>
<pre><code>&lt;!-- 1. Separate stylesheet for print only --&gt;
&lt;link rel="stylesheet" href="print.css" media="print"&gt;

&lt;!-- 2. Inline in main stylesheet --&gt;
&lt;style&gt;
  body { font-size: 16px; }

  @media print {
    body { font-size: 12pt; }
    nav, footer, .ads { display: none; }
  }
&lt;/style&gt;

&lt;!-- 3. Print-only stylesheet imported via @import --&gt;
&lt;style&gt;
  @import "print.css" print;
&lt;/style&gt;</code></pre>

<p><strong>Common print-stylesheet patterns:</strong></p>
<pre><code>@media print {
  /* Use print-friendly units (pt, in, cm) instead of px */
  body {
    font-size: 11pt;
    line-height: 1.5;
    color: black;
    background: white;
  }

  /* Hide UI chrome that has no purpose on paper */
  nav, footer, .sidebar, .ads,
  .share-buttons, .comments, button,
  video, audio, .interactive {
    display: none !important;
  }

  /* Show URL after every link (so readers can find them) */
  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.85em;
    color: #555;
  }
  /* But not for fragment links or relative paths */
  a[href^="#"]::after,
  a[href^="javascript:"]::after,
  a[href^="mailto:"]::after {
    content: "";
  }

  /* Don&rsquo;t split important elements across pages */
  h1, h2, h3 { break-after: avoid; }
  table, figure, blockquote { break-inside: avoid; }
  img { break-inside: avoid; max-width: 100%; }

  /* Force a page break before/after */
  .page-break { break-before: page; }
  .new-section { break-before: page; }

  /* Optimize colors for grayscale print */
  * {
    background: transparent !important;
    box-shadow: none !important;
    color: black !important;
  }

  /* Better link visibility */
  a {
    text-decoration: underline;
    color: black;
  }

  /* Print headers and footers via @page */
  @page {
    size: A4;
    margin: 2cm;
  }
}</code></pre>

<p><strong>Page break properties:</strong></p>
<table>
  <tr><th>Property</th><th>Effect</th></tr>
  <tr><td><code>break-before: page</code></td><td>Force new page before</td></tr>
  <tr><td><code>break-after: page</code></td><td>Force new page after</td></tr>
  <tr><td><code>break-inside: avoid</code></td><td>Don&rsquo;t split this element</td></tr>
  <tr><td><code>break-inside: avoid-page</code></td><td>Don&rsquo;t split across page boundaries</td></tr>
</table>

<p>The legacy <code>page-break-*</code> properties also work but are deprecated in favor of <code>break-*</code>.</p>

<p><strong>The <code>@page</code> at-rule</strong> &mdash; controls the printed page itself:</p>
<pre><code>@page {
  size: A4;             /* or letter, legal, or "10cm 15cm" */
  margin: 2cm;
}

@page :first {
  margin-top: 4cm;       /* extra space on first page */
}

@page :left {
  margin-left: 3cm;      /* mirrored margins for two-sided printing */
}
@page :right {
  margin-right: 3cm;
}</code></pre>

<p><strong>Specific tips for print:</strong></p>
<ul>
  <li><strong>Use serif fonts</strong> &mdash; serifs improve readability on paper (Georgia, Cambria, Garamond).</li>
  <li><strong>Black on white</strong> for body text &mdash; saves ink, better contrast.</li>
  <li><strong>Show URLs in links</strong> &mdash; users can&rsquo;t click paper.</li>
  <li><strong>Hide interactive elements</strong> &mdash; buttons, videos, ads have no print purpose.</li>
  <li><strong>Add print-only content</strong> with <code>display: block !important</code> on classes that screen styles hide.</li>
  <li><strong>Test with Print Preview</strong> &mdash; Chrome and Firefox have excellent preview tools.</li>
</ul>

<p><strong>Print preview testing in DevTools:</strong> open the Rendering tab in Chrome DevTools, scroll to "Emulate CSS media type," and choose "print." The page now renders with print styles in the browser viewport &mdash; faster than constantly opening Print Preview.</p>

<p>Most modern sites have minimal print styles &mdash; users rarely print web pages. But for documentation, articles, recipes, and forms, a polished print stylesheet meaningfully improves the offline experience.</p>
'''

ANSWERS[91] = r'''
<p>The <code>&lt;var&gt;</code> element marks a <strong>variable in mathematical expressions or programming contexts</strong> &mdash; a placeholder name that stands for some value. Browsers render it in italic by default to match typographic conventions for variables.</p>

<pre><code>&lt;p&gt;The area of a rectangle is &lt;var&gt;width&lt;/var&gt; multiplied
   by &lt;var&gt;height&lt;/var&gt;.&lt;/p&gt;

&lt;p&gt;Solve for &lt;var&gt;x&lt;/var&gt;: 2&lt;var&gt;x&lt;/var&gt; + 3 = 11&lt;/p&gt;

&lt;p&gt;In the function &lt;code&gt;f(&lt;var&gt;n&lt;/var&gt;)&lt;/code&gt;, the variable
   &lt;var&gt;n&lt;/var&gt; represents the input number.&lt;/p&gt;

&lt;p&gt;Set the value of &lt;var&gt;username&lt;/var&gt; to your account name
   before running the script.&lt;/p&gt;</code></pre>

<p><strong>Default styling:</strong></p>
<pre><code>var {
  font-style: italic;
  /* No special font-family by default */
}</code></pre>

<p><strong>Family of inline code-related semantic elements:</strong></p>
<table>
  <tr><th>Tag</th><th>Means</th><th>Default style</th></tr>
  <tr><td><code>&lt;code&gt;</code></td><td>Source code</td><td>Monospace</td></tr>
  <tr><td><code>&lt;kbd&gt;</code></td><td>Keyboard input the user types</td><td>Monospace</td></tr>
  <tr><td><code>&lt;samp&gt;</code></td><td>Sample output from a program</td><td>Monospace</td></tr>
  <tr><td><code>&lt;var&gt;</code></td><td>Variable name in math/code</td><td>Italic</td></tr>
</table>

<p><strong>Combining the family in technical writing:</strong></p>
<pre><code>&lt;p&gt;Run &lt;kbd&gt;node app.js&lt;/kbd&gt; to start the server. Replace
   &lt;var&gt;PORT&lt;/var&gt; in the config with your desired port number,
   then check the output for &lt;samp&gt;Server listening on port &lt;var&gt;PORT&lt;/var&gt;&lt;/samp&gt;.&lt;/p&gt;</code></pre>

<p>Each tag has a distinct meaning: <code>kbd</code> for what to type, <code>var</code> for placeholder names, <code>samp</code> for what the program outputs.</p>

<p><strong>Common use cases:</strong></p>
<ul>
  <li><strong>Mathematical formulas</strong> &mdash; <code>E = m&lt;var&gt;c&lt;/var&gt;&lt;sup&gt;2&lt;/sup&gt;</code> (though MathML or KaTeX is better for complex math).</li>
  <li><strong>API documentation</strong> &mdash; <code>GET /users/&lt;var&gt;userId&lt;/var&gt;</code>.</li>
  <li><strong>Template placeholders</strong> &mdash; "Replace <code>&lt;var&gt;YOUR_API_KEY&lt;/var&gt;</code> with your actual key."</li>
  <li><strong>Algorithmic descriptions</strong> &mdash; "the input array <code>&lt;var&gt;arr&lt;/var&gt;</code> is sorted in O(<code>&lt;var&gt;n&lt;/var&gt; log &lt;var&gt;n&lt;/var&gt;</code>) time."</li>
  <li><strong>Type signatures in prose</strong> &mdash; "Pass <code>&lt;var&gt;callback&lt;/var&gt;</code> as the second argument."</li>
</ul>

<p><strong>Styling for technical docs:</strong></p>
<pre><code>var {
  font-style: italic;
  color: #d35400;          /* orange — variable color */
  background: rgba(211, 84, 0, 0.08);
  padding: 0 0.2em;
  border-radius: 3px;
}

/* Combined with code: differentiate visually */
code var {
  background: transparent;
  color: inherit;
  font-style: italic;
}</code></pre>

<p><strong>Don&rsquo;t use <code>&lt;var&gt;</code> for:</strong></p>
<ul>
  <li>Generic italics in regular text (use <code>&lt;em&gt;</code> for emphasis or CSS for style).</li>
  <li>Names of products, projects, or features (use plain text or <code>&lt;span&gt;</code>).</li>
  <li>Variables in actual code blocks (use <code>&lt;code&gt;</code> &mdash; the whole block is code).</li>
  <li>HTML attributes (those are also part of <code>&lt;code&gt;</code>).</li>
</ul>

<p><strong>Accessibility:</strong></p>
<ul>
  <li>Screen readers don&rsquo;t typically announce <code>&lt;var&gt;</code> with special inflection &mdash; the content matters more than the tag.</li>
  <li>Italic text from <code>&lt;var&gt;</code> doesn&rsquo;t convey the "this is a variable" meaning to most users; visual context (math, code) does.</li>
  <li>For documentation that&rsquo;s machine-parsed (style guides, generators), the semantic tag helps tools extract variable names accurately.</li>
</ul>

<p>It&rsquo;s a niche element. Most documentation just uses italics or <code>&lt;code&gt;</code> styling with a CSS class. Use <code>&lt;var&gt;</code> when you genuinely care about machine-readability of variable names &mdash; in textbook-quality technical writing or formal API docs.</p>
'''

ANSWERS[92] = r'''
<p>Responsive layouts use <strong>CSS media queries</strong> to apply different styles based on viewport size, orientation, color scheme, motion preferences, and more. Combined with flexible layouts (Flexbox, Grid) and relative units, they create designs that adapt across devices.</p>

<p><strong>Mobile-first approach</strong> &mdash; default styles for mobile, then enhance for larger screens:</p>
<pre><code>/* Default: mobile */
.container {
  display: block;
  padding: 1em;
}
.sidebar { display: none; }   /* hide on mobile */

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    display: grid;
    grid-template-columns: 1fr 250px;
    gap: 2em;
    padding: 2em;
  }
  .sidebar { display: block; }
}

/* Desktop and up */
@media (min-width: 1200px) {
  .container {
    grid-template-columns: 1fr 300px;
    max-width: 1400px;
    margin: 0 auto;
  }
}</code></pre>

<p><strong>Common breakpoint conventions</strong> (no fixed standard &mdash; pick what fits your design):</p>
<table>
  <tr><th>Breakpoint</th><th>Range</th><th>Typical device</th></tr>
  <tr><td>Mobile</td><td>0&ndash;599px</td><td>Phone</td></tr>
  <tr><td>Tablet</td><td>600&ndash;899px</td><td>Tablet portrait</td></tr>
  <tr><td>Small desktop</td><td>900&ndash;1199px</td><td>Tablet landscape, small laptop</td></tr>
  <tr><td>Desktop</td><td>1200&ndash;1599px</td><td>Standard laptop</td></tr>
  <tr><td>Large desktop</td><td>1600px+</td><td>Big monitor</td></tr>
</table>

<p><strong>Beyond width &mdash; useful media query types:</strong></p>
<pre><code>/* Orientation */
@media (orientation: landscape) {
  .gallery { columns: 4; }
}

/* High-DPI displays */
@media (min-resolution: 2dppx) {
  .logo { background-image: url(logo@2x.png); }
}

/* User preferences */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --fg: #f0f0f0;
  }
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

/* Hover capability */
@media (hover: hover) {
  .card:hover { transform: scale(1.05); }
}
@media (hover: none) {
  /* Touch devices — show buttons that would otherwise appear on hover */
  .card .actions { display: flex; }
}

/* Print */
@media print {
  nav, footer { display: none; }
  body { font-size: 12pt; color: black; }
}</code></pre>

<p><strong>Modern responsive techniques</strong> that often eliminate the need for breakpoints:</p>

<p><strong>1. <code>clamp()</code> for fluid typography:</strong></p>
<pre><code>h1 {
  font-size: clamp(1.5rem, 4vw + 1rem, 3.5rem);
  /* min: 1.5rem, scales with viewport, max: 3.5rem */
}</code></pre>

<p>One line replaces multiple media queries for font scaling.</p>

<p><strong>2. CSS Grid auto-fit:</strong></p>
<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}</code></pre>

<p>Cards reflow naturally without any breakpoint definitions.</p>

<p><strong>3. Container queries (2026 baseline)</strong> &mdash; styles based on the parent container, not the viewport:</p>
<pre><code>.card {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card-title { font-size: 1.5em; }
  .card { display: grid; grid-template-columns: 200px 1fr; }
}</code></pre>

<p>The same component renders differently in a sidebar (narrow) vs main content area (wide) &mdash; powerful for reusable components.</p>

<p><strong>4. Logical properties</strong> for international layouts:</p>
<pre><code>.box {
  margin-inline: auto;            /* logical equivalent of margin-left/right */
  padding-block: 1em;             /* logical equivalent of padding-top/bottom */
  border-inline-start: 3px solid blue;   /* "start" = left in LTR, right in RTL */
}</code></pre>

<p>Layouts adapt automatically to right-to-left languages.</p>

<p><strong>The <code>&lt;meta name="viewport"&gt;</code> tag is essential</strong> &mdash; without it, mobile renders desktop-sized:</p>
<pre><code>&lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;</code></pre>

<p>Always include this in your HTML head &mdash; it&rsquo;s the foundation that makes media queries work correctly on mobile.</p>
'''

ANSWERS[93] = r'''
<p>The <code>&lt;bdi&gt;</code> element (Bidirectional Isolation) <strong>isolates a span of text from its surrounding directional context</strong>. It&rsquo;s essential when displaying user-generated content that might be in a different direction (LTR/RTL) than the parent text &mdash; preventing layout corruption that the bidirectional algorithm would otherwise cause.</p>

<p><strong>The problem it solves:</strong></p>
<pre><code>&lt;!-- Without bdi: a username in Arabic embedded in English layout --&gt;
&lt;p&gt;User &lt;span&gt;مرحبا&lt;/span&gt; (15 posts) liked your photo.&lt;/p&gt;
&lt;!-- The Arabic text can flip "(15 posts)" weirdly because of bidi rules --&gt;</code></pre>

<p>The Unicode bidirectional algorithm tries to merge directionalities, sometimes flipping nearby punctuation or numbers in unexpected ways. The result: parentheses, hyphens, and adjacent text appear in the wrong place visually.</p>

<pre><code>&lt;!-- With bdi: the username is isolated; surrounding text stays clean --&gt;
&lt;p&gt;User &lt;bdi&gt;مرحبا&lt;/bdi&gt; (15 posts) liked your photo.&lt;/p&gt;
&lt;p&gt;User &lt;bdi&gt;Sarah&lt;/bdi&gt; (15 posts) liked your photo.&lt;/p&gt;
&lt;p&gt;User &lt;bdi&gt;ハナコ&lt;/bdi&gt; (15 posts) liked your photo.&lt;/p&gt;</code></pre>

<p>Each user&rsquo;s name renders in its native direction without affecting the surrounding "(15 posts) liked your photo" structure.</p>

<p><strong>Why it&rsquo;s essential for user-generated content:</strong></p>
<ul>
  <li>You can&rsquo;t know in advance whether a username, comment, or post will be LTR or RTL.</li>
  <li>Without isolation, an attacker could craft text with bidi override characters that visually flip URLs or commands &mdash; the "Trojan Source" attack.</li>
  <li>Numbers and punctuation embedded in mixed-direction text often appear in the wrong order.</li>
</ul>

<p><strong>Real-world example &mdash; a comment list:</strong></p>
<pre><code>&lt;ul&gt;
  &lt;li&gt;
    &lt;bdi&gt;Alice&lt;/bdi&gt; commented:
    &lt;bdi&gt;"Great article!"&lt;/bdi&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;bdi&gt;أحمد&lt;/bdi&gt; commented:
    &lt;bdi&gt;"شكرا على المعلومات"&lt;/bdi&gt;
  &lt;/li&gt;
  &lt;li&gt;
    &lt;bdi&gt;田中&lt;/bdi&gt; commented:
    &lt;bdi&gt;"とても役に立ちました"&lt;/bdi&gt;
  &lt;/li&gt;
&lt;/ul&gt;</code></pre>

<p>Each name and quoted text is bidi-isolated, so the surrounding structure ("commented:") doesn&rsquo;t get rearranged based on someone&rsquo;s name direction.</p>

<p><strong><code>&lt;bdi&gt;</code> vs <code>&lt;bdo&gt;</code> &mdash; very different elements:</strong></p>
<table>
  <tr><th></th><th><code>&lt;bdi&gt;</code></th><th><code>&lt;bdo&gt;</code></th></tr>
  <tr><td>Stands for</td><td>Bidirectional Isolation</td><td>Bidirectional Override</td></tr>
  <tr><td>Effect</td><td>Isolates from surrounding direction</td><td>Forces a specific direction</td></tr>
  <tr><td>Auto-detect direction?</td><td>Yes (uses content)</td><td>No (you specify with <code>dir</code>)</td></tr>
  <tr><td>Use for</td><td>Unknown-direction user input</td><td>Forcing direction for specific text</td></tr>
</table>

<pre><code>&lt;!-- &lt;bdi&gt;: detect and isolate --&gt;
&lt;p&gt;Hello, &lt;bdi&gt;[user-input here]&lt;/bdi&gt;!&lt;/p&gt;

&lt;!-- &lt;bdo&gt;: force direction --&gt;
&lt;p&gt;Reversed: &lt;bdo dir="rtl"&gt;Hello&lt;/bdo&gt;&lt;/p&gt;
&lt;!-- Renders: "olleH" --&gt;</code></pre>

<p><strong>Default behavior:</strong></p>
<ul>
  <li><code>&lt;bdi&gt;</code> renders inline with no visual difference &mdash; the effect is purely on text direction.</li>
  <li>The browser auto-detects the contained text&rsquo;s base direction (typically the first strong-direction character).</li>
  <li>You can override with <code>dir="rtl"</code> or <code>dir="ltr"</code> if needed.</li>
</ul>

<p><strong>When you need <code>&lt;bdi&gt;</code>:</strong></p>
<ul>
  <li><strong>Anywhere user-generated text appears</strong> &mdash; usernames, comments, file names, post titles.</li>
  <li><strong>Search results</strong> showing user content from various languages.</li>
  <li><strong>Chat applications</strong> with mixed-language messages.</li>
  <li><strong>International social media</strong>.</li>
</ul>

<p><strong>CSS-only alternative</strong> using the <code>unicode-bidi</code> property:</p>
<pre><code>.user-content {
  unicode-bidi: isolate;
}</code></pre>

<p>Functionally equivalent to <code>&lt;bdi&gt;</code> for the isolation effect. Use the element when you have semantic clarity about isolating user content; use the CSS property when you can&rsquo;t change the markup.</p>

<p><code>&lt;bdi&gt;</code> is one of those elements that 95% of authors don&rsquo;t need but 5% absolutely must use to avoid serious bugs. If your site supports multiple languages or accepts user input that might appear in mixed-direction contexts, sprinkle it everywhere user content appears.</p>
'''

ANSWERS[94] = r'''
<p>HTML5 inline form validation uses attributes that the browser checks <strong>as the user types and on submit</strong>. Combined with CSS pseudo-classes and the Constraint Validation API, you can build sophisticated validation UI without a single library.</p>

<pre><code>&lt;form id="signup"&gt;
  &lt;label&gt;
    Email:
    &lt;input type="email"
           name="email"
           required
           autocomplete="email"&gt;
  &lt;/label&gt;

  &lt;label&gt;
    Username (3-20 characters, letters and numbers only):
    &lt;input type="text"
           name="username"
           required
           pattern="[a-zA-Z0-9]{3,20}"
           minlength="3"
           maxlength="20"
           title="3-20 alphanumeric characters"&gt;
  &lt;/label&gt;

  &lt;label&gt;
    Password (min 8 characters with at least 1 number):
    &lt;input type="password"
           name="password"
           required
           minlength="8"
           pattern="(?=.*\d).{8,}"
           autocomplete="new-password"&gt;
  &lt;/label&gt;

  &lt;label&gt;
    Age (must be 13 or older):
    &lt;input type="number"
           name="age"
           required
           min="13"
           max="120"&gt;
  &lt;/label&gt;

  &lt;button type="submit"&gt;Create Account&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p><strong>The constraint attributes</strong>:</p>
<table>
  <tr><th>Attribute</th><th>Effect</th></tr>
  <tr><td><code>required</code></td><td>Empty value blocks submission</td></tr>
  <tr><td><code>type="email"</code> | <code>"url"</code> | <code>"tel"</code></td><td>Format check</td></tr>
  <tr><td><code>minlength</code> / <code>maxlength</code></td><td>Character count bounds</td></tr>
  <tr><td><code>min</code> / <code>max</code></td><td>Numeric / date bounds</td></tr>
  <tr><td><code>pattern</code></td><td>Regex validation (anchored automatically)</td></tr>
  <tr><td><code>step</code></td><td>Increment granularity</td></tr>
  <tr><td><code>title</code></td><td>Hint shown on validation error</td></tr>
</table>

<p><strong>CSS pseudo-classes for inline visual feedback:</strong></p>
<pre><code>/* Default state — no error indication */
input { border: 1px solid #ccc; }

/* Show error styling only after the user has interacted */
input:user-invalid {
  border-color: #d32f2f;
  background: #ffebee;
}
input:user-valid {
  border-color: #388e3c;
  background: #e8f5e9;
}

/* Required field indicator */
input:required + label::after {
  content: " *";
  color: #d32f2f;
}

/* Avoid flashing red on initial render */
input:placeholder-shown {
  border-color: #ccc;
}</code></pre>

<p>The <strong><code>:user-invalid</code></strong> pseudo-class (now widely supported) only matches after the user has interacted with the input &mdash; preventing the form from looking error-laden on initial load. The older <code>:invalid</code> matches immediately, often showing red errors for empty fields the user hasn&rsquo;t touched.</p>

<p><strong>Custom validation messages with the Constraint Validation API:</strong></p>
<pre><code>const email = document.querySelector("input[name='email']");
const password = document.querySelector("input[name='password']");
const confirm = document.querySelector("input[name='confirm']");

email.addEventListener("invalid", () =&gt; {
  if (email.validity.valueMissing) {
    email.setCustomValidity("Please enter your email address");
  } else if (email.validity.typeMismatch) {
    email.setCustomValidity("That doesn&rsquo;t look like a valid email");
  } else {
    email.setCustomValidity("");
  }
});

email.addEventListener("input", () =&gt; {
  email.setCustomValidity("");   // clear when user retries
});

// Cross-field validation: passwords must match
confirm.addEventListener("input", () =&gt; {
  confirm.setCustomValidity(
    confirm.value === password.value ? "" : "Passwords don&rsquo;t match"
  );
});</code></pre>

<p><strong>Validity object properties:</strong></p>
<table>
  <tr><th>Property</th><th>True when</th></tr>
  <tr><td><code>valueMissing</code></td><td>Required field is empty</td></tr>
  <tr><td><code>typeMismatch</code></td><td>Email/URL/tel format invalid</td></tr>
  <tr><td><code>patternMismatch</code></td><td>Regex pattern fails</td></tr>
  <tr><td><code>tooShort</code> / <code>tooLong</code></td><td>Length out of bounds</td></tr>
  <tr><td><code>rangeUnderflow</code> / <code>rangeOverflow</code></td><td>Number/date out of bounds</td></tr>
  <tr><td><code>stepMismatch</code></td><td>Doesn&rsquo;t match step increment</td></tr>
  <tr><td><code>customError</code></td><td><code>setCustomValidity</code> was called with non-empty string</td></tr>
  <tr><td><code>valid</code></td><td>All checks pass</td></tr>
</table>

<p><strong>Submit-time validation:</strong></p>
<pre><code>document.getElementById("signup").addEventListener("submit", (e) =&gt; {
  if (!e.target.checkValidity()) {
    e.preventDefault();
    e.target.reportValidity();   // shows native error tooltips
    return;
  }
  // submit normally if everything valid
});</code></pre>

<p><strong>Always re-validate server-side</strong>. HTML5 validation is UX only &mdash; users can edit attributes in DevTools, paste invalid values past patterns, or send raw HTTP requests entirely. Make the happy path smooth with HTML5; make the system safe with server-side checks.</p>
'''

ANSWERS[95] = r'''
<p>The <code>&lt;u&gt;</code> element marks <strong>text with a non-textual annotation</strong> &mdash; like a misspelled word, a proper name in Chinese (where underlines indicate names), or other non-emphatic visual cues. It renders with underline by default, but the meaning is semantic: "this text has special significance not captured by other tags."</p>

<pre><code>&lt;p&gt;The word &lt;u&gt;misteak&lt;/u&gt; is misspelled.&lt;/p&gt;

&lt;p&gt;The Chinese name &lt;u lang="zh"&gt;李明&lt;/u&gt; appears with the
   underline convention.&lt;/p&gt;

&lt;p&gt;The handwritten note read: &lt;u&gt;please call me back&lt;/u&gt;
   underlined for emphasis.&lt;/p&gt;</code></pre>

<p><strong>Default styling:</strong></p>
<pre><code>u { text-decoration: underline; }</code></pre>

<p><strong>Was <code>&lt;u&gt;</code> deprecated?</strong> Almost. HTML4 deprecated <code>&lt;u&gt;</code> as purely presentational. HTML5 brought it back with <em>refined semantic meaning</em>: text with non-textual annotation. So:</p>
<ul>
  <li><strong>HTML4:</strong> <code>&lt;u&gt;</code> deprecated, "use CSS instead."</li>
  <li><strong>HTML5+:</strong> <code>&lt;u&gt;</code> reborn for cases that aren&rsquo;t emphasis but need underline.</li>
</ul>

<p><strong>The big problem with <code>&lt;u&gt;</code>:</strong> underlined text on the web traditionally means "link." When users see underlined text, they often try to click. Using <code>&lt;u&gt;</code> for visual underlines confuses users.</p>

<p><strong>Specific use cases the spec recommends:</strong></p>
<ul>
  <li><strong>Misspelled words</strong> (red squiggly line in some implementations).</li>
  <li><strong>Chinese proper name marks</strong> &mdash; underlines historically denote proper nouns in Chinese typography.</li>
  <li><strong>Other typographic conventions</strong> where underline has special non-emphasis meaning.</li>
</ul>

<p><strong>What NOT to use <code>&lt;u&gt;</code> for:</strong></p>
<table>
  <tr><th>Use</th><th>Better tag/property</th></tr>
  <tr><td>Emphasis</td><td><code>&lt;em&gt;</code> or <code>&lt;strong&gt;</code></td></tr>
  <tr><td>Headings</td><td><code>&lt;h1&gt;</code> through <code>&lt;h6&gt;</code></td></tr>
  <tr><td>Document titles</td><td><code>&lt;cite&gt;</code> (italic) or CSS</td></tr>
  <tr><td>Foreign words</td><td><code>&lt;i&gt;</code> with <code>lang</code> attribute</td></tr>
  <tr><td>Decorative underline</td><td>CSS <code>text-decoration: underline</code></td></tr>
  <tr><td>Underlined link</td><td><code>&lt;a&gt;</code> (default underline)</td></tr>
</table>

<p><strong>Style misspellings distinctly</strong> &mdash; the spell-check style:</p>
<pre><code>u.misspelled {
  text-decoration: underline wavy red;
}</code></pre>

<p>The <code>wavy</code> style of <code>text-decoration</code> draws a squiggly line, mimicking native spell-check display. Use this in writing or grammar tools where you&rsquo;re visually flagging errors.</p>

<p><strong>Example with full styling:</strong></p>
<pre><code>&lt;p&gt;You&rsquo;ve made a few &lt;u class="error"&gt;misteaks&lt;/u&gt;
   in this sentence. Click for &lt;u class="suggestion"&gt;suggestions&lt;/u&gt;.&lt;/p&gt;

&lt;style&gt;
  u.error {
    text-decoration: underline wavy red;
    cursor: help;
  }
  u.suggestion {
    text-decoration: underline dotted #0066cc;
    cursor: pointer;
  }
&lt;/style&gt;</code></pre>

<p><strong>Accessibility:</strong></p>
<ul>
  <li>Screen readers don&rsquo;t announce <code>&lt;u&gt;</code> with any inflection &mdash; it&rsquo;s purely visual.</li>
  <li>Underlined text without other context is invisible to screen reader users &mdash; pair with explicit text or <code>aria-label</code> if the meaning matters.</li>
  <li>If the underline is decorative, use a CSS class with <code>text-decoration</code> instead of the semantic tag.</li>
</ul>

<p><strong>Reality check:</strong> <code>&lt;u&gt;</code> is rarely seen in practice. Most underline use cases fit better with <code>&lt;em&gt;</code>, <code>&lt;cite&gt;</code>, links, or CSS classes. The valid use cases (Chinese proper name marks, spell-check display) are niche but real. Generally: avoid <code>&lt;u&gt;</code> unless one of these specific cases applies, since the visual underline confuses users about clickability.</p>
'''

ANSWERS[96] = r'''
<p>A fixed navigation bar stays anchored to the viewport regardless of scroll. CSS <code>position: fixed</code> achieves it &mdash; or <code>position: sticky</code> for a more flexible variation that joins the page on scroll.</p>

<pre><code>&lt;header class="fixed-nav"&gt;
  &lt;div class="nav-inner"&gt;
    &lt;a href="/" class="logo"&gt;Acme&lt;/a&gt;

    &lt;nav aria-label="Main"&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/"&gt;Home&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/products"&gt;Products&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/pricing"&gt;Pricing&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/about"&gt;About&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;

    &lt;div class="nav-actions"&gt;
      &lt;a href="/login"&gt;Log in&lt;/a&gt;
      &lt;a href="/signup" class="btn"&gt;Sign up&lt;/a&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/header&gt;

&lt;main&gt;
  &lt;!-- Add padding-top equal to nav height to prevent content overlap --&gt;
  &lt;article&gt;Lots of scrolling content...&lt;/article&gt;
&lt;/main&gt;

&lt;style&gt;
  .fixed-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: white;
    border-bottom: 1px solid #eee;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    height: 60px;
  }
  .nav-inner {
    max-width: 1200px;
    margin: 0 auto;
    height: 100%;
    padding: 0 1em;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2em;
  }
  .logo { font-weight: bold; text-decoration: none; }
  .fixed-nav nav ul {
    display: flex;
    gap: 1.5em;
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .fixed-nav nav a { color: #333; text-decoration: none; }
  .fixed-nav nav a:hover { color: #0066cc; }

  /* Critical: offset main content so it doesn&rsquo;t hide behind the nav */
  main {
    padding-top: 60px;
  }
&lt;/style&gt;</code></pre>

<p><strong>Critical pattern: offset content</strong></p>
<p>Without <code>padding-top: 60px</code> on <code>&lt;main&gt;</code>, the first 60px of content hides behind the fixed nav on page load. Always pad the content area equal to the nav&rsquo;s height. Use a CSS variable to keep them in sync:</p>
<pre><code>:root {
  --nav-height: 60px;
}
.fixed-nav { height: var(--nav-height); }
main       { padding-top: var(--nav-height); }
section[id] { scroll-margin-top: var(--nav-height); }   /* anchor links land below nav */</code></pre>

<p><strong><code>scroll-margin-top</code></strong> is a critical addition &mdash; without it, anchor links (<code>#section</code>) scroll their target right under the fixed nav, hiding the heading.</p>

<p><strong>Fixed vs Sticky comparison:</strong></p>
<table>
  <tr><th></th><th><code>position: fixed</code></th><th><code>position: sticky</code></th></tr>
  <tr><td>Layout</td><td>Removed from flow always</td><td>Takes up space, then sticks</td></tr>
  <tr><td>Always visible</td><td>Yes</td><td>Only after scroll threshold</td></tr>
  <tr><td>Containing block</td><td>Viewport</td><td>Nearest scrollable ancestor</td></tr>
  <tr><td>Need to offset content</td><td>Always (padding-top)</td><td>Not initially</td></tr>
  <tr><td>Use when</td><td>Nav must always be visible</td><td>Nav can scroll with hero, then stick</td></tr>
</table>

<p><strong>Sticky variation</strong> &mdash; nav scrolls with hero, then sticks at top:</p>
<pre><code>.sticky-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  /* Otherwise same as fixed-nav */
}

/* No need for padding-top on main — sticky takes natural space */</code></pre>

<p>This pattern is increasingly preferred over fixed for site headers: hero takes full viewport without nav obstruction, but as the user scrolls past, the nav locks to the top.</p>

<p><strong>Hide on scroll down, show on scroll up</strong> (Medium-style behavior):</p>
<pre><code>let lastY = window.scrollY;
const nav = document.querySelector(".fixed-nav");

window.addEventListener("scroll", () =&gt; {
  const y = window.scrollY;
  if (y &gt; lastY &amp;&amp; y &gt; 100) {
    nav.classList.add("hidden");      // scrolling down
  } else {
    nav.classList.remove("hidden");   // scrolling up
  }
  lastY = y;
}, { passive: true });

&lt;style&gt;
  .fixed-nav {
    transition: transform 0.3s;
  }
  .fixed-nav.hidden {
    transform: translateY(-100%);
  }
&lt;/style&gt;</code></pre>

<p><strong>Mobile considerations:</strong></p>
<ul>
  <li><strong>Make it shorter on mobile</strong> &mdash; fixed nav consumes precious screen height; reduce to 50px or less.</li>
  <li><strong>Use <code>safe-area-inset-top</code></strong> for iOS notch/punch-hole support: <code>padding-top: max(1em, env(safe-area-inset-top))</code>.</li>
  <li><strong>Hamburger menu</strong> for nav links on small screens to save space.</li>
  <li><strong>Avoid covering important content</strong> on small viewports.</li>
</ul>
'''

ANSWERS[97] = r'''
<p>A definition list (<code>&lt;dl&gt;</code>) pairs <strong>terms with their definitions or descriptions</strong>. <code>&lt;dt&gt;</code> marks each term; <code>&lt;dd&gt;</code> marks the description that follows. They&rsquo;re semantic &mdash; ideal for glossaries, key-value metadata, FAQ structures, and any "name : value" pairing.</p>

<pre><code>&lt;dl&gt;
  &lt;dt&gt;HTML&lt;/dt&gt;
  &lt;dd&gt;HyperText Markup Language &mdash; the standard markup language
      for documents designed to be displayed in a web browser.&lt;/dd&gt;

  &lt;dt&gt;CSS&lt;/dt&gt;
  &lt;dd&gt;Cascading Style Sheets &mdash; a style sheet language used for
      describing the presentation of a document.&lt;/dd&gt;

  &lt;dt&gt;JavaScript&lt;/dt&gt;
  &lt;dd&gt;A programming language commonly used for creating
      interactive web content.&lt;/dd&gt;
&lt;/dl&gt;</code></pre>

<p><strong>Multiple terms or definitions</strong> for one entry &mdash; common in dictionaries:</p>
<pre><code>&lt;dl&gt;
  &lt;dt&gt;Internet&lt;/dt&gt;
  &lt;dt&gt;The Net&lt;/dt&gt;
  &lt;dt&gt;The Web&lt;/dt&gt;
  &lt;dd&gt;The global system of interconnected computer networks
      that uses the Internet protocol suite (TCP/IP).&lt;/dd&gt;

  &lt;dt&gt;Bug&lt;/dt&gt;
  &lt;dd&gt;An error or flaw in software causing incorrect behavior.&lt;/dd&gt;
  &lt;dd&gt;A small insect.&lt;/dd&gt;
  &lt;dd&gt;An informal verb meaning to bother or annoy.&lt;/dd&gt;
&lt;/dl&gt;</code></pre>

<p>Multiple <code>&lt;dt&gt;</code> can group synonyms with one definition; multiple <code>&lt;dd&gt;</code> after one <code>&lt;dt&gt;</code> can list multiple definitions of one term.</p>

<p><strong>Default styling</strong> &mdash; browsers indent <code>&lt;dd&gt;</code> beneath its <code>&lt;dt&gt;</code>:</p>
<pre><code>dl { margin: 1em 0; }
dt { font-weight: bold; }
dd { margin-left: 2em; margin-bottom: 0.5em; }</code></pre>

<p><strong>Modern Grid layout</strong> &mdash; render as a two-column key/value table:</p>
<pre><code>dl.metadata {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5em 1em;
  margin: 0;
}
dl.metadata dt {
  font-weight: 600;
  color: #555;
}
dl.metadata dd {
  margin: 0;
}</code></pre>

<pre><code>&lt;dl class="metadata"&gt;
  &lt;dt&gt;Author:&lt;/dt&gt;
  &lt;dd&gt;Jane Smith&lt;/dd&gt;
  &lt;dt&gt;Published:&lt;/dt&gt;
  &lt;dd&gt;&lt;time datetime="2026-04-25"&gt;April 25, 2026&lt;/time&gt;&lt;/dd&gt;
  &lt;dt&gt;Category:&lt;/dt&gt;
  &lt;dd&gt;Web Development&lt;/dd&gt;
  &lt;dt&gt;Read time:&lt;/dt&gt;
  &lt;dd&gt;5 minutes&lt;/dd&gt;
&lt;/dl&gt;</code></pre>

<p>This produces a clean two-column metadata block &mdash; perfect for article sidebars, product specifications, or technical reference pages.</p>

<p><strong>Use cases:</strong></p>
<ul>
  <li><strong>Glossaries</strong> &mdash; the original use case.</li>
  <li><strong>Metadata blocks</strong> &mdash; author, date, category for articles or products.</li>
  <li><strong>Technical specifications</strong> &mdash; dimensions, materials, weight, capacity.</li>
  <li><strong>FAQ sections</strong> &mdash; questions as <code>&lt;dt&gt;</code>, answers as <code>&lt;dd&gt;</code> (though <code>&lt;details&gt;</code>/<code>&lt;summary&gt;</code> is often better for collapsible FAQs).</li>
  <li><strong>Key-value pairs</strong> &mdash; configuration options, status fields.</li>
  <li><strong>Cast lists</strong> &mdash; "Director:", "Producer:", "Cinematographer:".</li>
</ul>

<p><strong>Wrapping with <code>&lt;div&gt;</code></strong> &mdash; HTML5 allows wrapping a term + description pair in a <code>&lt;div&gt;</code> for styling or structure (helpful for borders or hover effects on whole entries):</p>
<pre><code>&lt;dl&gt;
  &lt;div&gt;
    &lt;dt&gt;Term 1&lt;/dt&gt;
    &lt;dd&gt;Definition 1&lt;/dd&gt;
  &lt;/div&gt;
  &lt;div&gt;
    &lt;dt&gt;Term 2&lt;/dt&gt;
    &lt;dd&gt;Definition 2&lt;/dd&gt;
  &lt;/div&gt;
&lt;/dl&gt;</code></pre>

<p><strong>Don&rsquo;t use <code>&lt;dl&gt;</code> for:</strong></p>
<ul>
  <li><strong>Dialogs / conversations</strong> (the spec used to suggest this; it doesn&rsquo;t any more) &mdash; use semantic markup with <code>&lt;p&gt;</code> + speaker attribution.</li>
  <li><strong>Generic lists of items</strong> &mdash; use <code>&lt;ul&gt;</code> or <code>&lt;ol&gt;</code> instead.</li>
  <li><strong>Content that doesn&rsquo;t pair "name" with "value"</strong> &mdash; if there&rsquo;s no logical key/value relationship, <code>&lt;dl&gt;</code> isn&rsquo;t the right structure.</li>
</ul>

<p><strong>Accessibility</strong>: screen readers announce definition lists as "list, [N] items" and read each <code>&lt;dt&gt;</code>/<code>&lt;dd&gt;</code> pair clearly. Better than ad-hoc <code>&lt;p&gt;Author: Name&lt;/p&gt;</code> structures because the relationship is programmatically expressed.</p>
'''

ANSWERS[98] = r'''
<p>HTML5 form autocomplete uses the <code>autocomplete</code> attribute to tell browsers <strong>what kind of value belongs in each field</strong>, enabling intelligent autofill from saved profile data, password managers, and credit card vaults. Done right, signup forms fill in 1 second instead of 30.</p>

<pre><code>&lt;form action="/checkout" method="post"&gt;
  &lt;fieldset&gt;
    &lt;legend&gt;Contact&lt;/legend&gt;
    &lt;label&gt;Name &lt;input name="name" autocomplete="name"&gt;&lt;/label&gt;
    &lt;label&gt;Email &lt;input type="email" name="email" autocomplete="email"&gt;&lt;/label&gt;
    &lt;label&gt;Phone &lt;input type="tel" name="phone" autocomplete="tel"&gt;&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Shipping address&lt;/legend&gt;
    &lt;label&gt;Street &lt;input name="addr" autocomplete="shipping street-address"&gt;&lt;/label&gt;
    &lt;label&gt;City &lt;input name="city" autocomplete="shipping address-level2"&gt;&lt;/label&gt;
    &lt;label&gt;State &lt;input name="state" autocomplete="shipping address-level1"&gt;&lt;/label&gt;
    &lt;label&gt;ZIP &lt;input name="zip" autocomplete="shipping postal-code"&gt;&lt;/label&gt;
    &lt;label&gt;Country &lt;input name="country" autocomplete="shipping country"&gt;&lt;/label&gt;
  &lt;/fieldset&gt;

  &lt;fieldset&gt;
    &lt;legend&gt;Payment&lt;/legend&gt;
    &lt;label&gt;Card number
      &lt;input name="cc-num" autocomplete="cc-number" inputmode="numeric"&gt;
    &lt;/label&gt;
    &lt;label&gt;Name on card
      &lt;input name="cc-name" autocomplete="cc-name"&gt;
    &lt;/label&gt;
    &lt;label&gt;Expiration
      &lt;input name="cc-exp" autocomplete="cc-exp" placeholder="MM/YY"&gt;
    &lt;/label&gt;
    &lt;label&gt;Security code
      &lt;input name="cc-csc" autocomplete="cc-csc" inputmode="numeric"&gt;
    &lt;/label&gt;
  &lt;/fieldset&gt;
&lt;/form&gt;</code></pre>

<p><strong>Common autocomplete tokens:</strong></p>
<table>
  <tr><th>Token</th><th>For</th></tr>
  <tr><td><code>name</code> / <code>given-name</code> / <code>family-name</code></td><td>Full / first / last name</td></tr>
  <tr><td><code>email</code></td><td>Email address</td></tr>
  <tr><td><code>tel</code></td><td>Phone number</td></tr>
  <tr><td><code>street-address</code></td><td>Full street address (multi-line)</td></tr>
  <tr><td><code>address-line1</code> / <code>line2</code></td><td>Individual address lines</td></tr>
  <tr><td><code>address-level1</code></td><td>State / province</td></tr>
  <tr><td><code>address-level2</code></td><td>City</td></tr>
  <tr><td><code>postal-code</code></td><td>ZIP / postal code</td></tr>
  <tr><td><code>country</code></td><td>Country code (e.g. US)</td></tr>
  <tr><td><code>cc-number</code></td><td>Credit card number</td></tr>
  <tr><td><code>cc-exp</code> / <code>cc-csc</code></td><td>Card expiration / CVV</td></tr>
  <tr><td><code>username</code></td><td>Account username</td></tr>
  <tr><td><code>current-password</code></td><td>Login password</td></tr>
  <tr><td><code>new-password</code></td><td>Sign-up or change-password</td></tr>
  <tr><td><code>one-time-code</code></td><td>2FA / OTP from SMS</td></tr>
  <tr><td><code>off</code></td><td>Disable autocomplete entirely</td></tr>
</table>

<p><strong>Sectioned fields</strong> &mdash; prefix with <code>shipping</code> or <code>billing</code> for separate address sections:</p>
<pre><code>&lt;input autocomplete="shipping street-address"&gt;
&lt;input autocomplete="shipping postal-code"&gt;
&lt;input autocomplete="billing street-address"&gt;
&lt;input autocomplete="billing postal-code"&gt;</code></pre>

<p>The browser uses different saved addresses for each section &mdash; users with separate shipping/billing addresses get the right one auto-filled in each.</p>

<p><strong>The <code>one-time-code</code> token</strong> &mdash; a 2026 must-have for SMS-based 2FA:</p>
<pre><code>&lt;input type="text"
       inputmode="numeric"
       autocomplete="one-time-code"
       maxlength="6"
       pattern="\d{6}"&gt;</code></pre>

<p>iOS Safari (and increasingly Android) parses incoming SMS messages for codes and offers them via the keyboard suggestion bar. Users tap once instead of switching to Messages and back.</p>

<p><strong>Password manager integration</strong> &mdash; for sign-up vs sign-in:</p>
<pre><code>&lt;!-- Sign-up: hint password manager to suggest a strong new password --&gt;
&lt;input type="password" autocomplete="new-password"&gt;

&lt;!-- Sign-in: tell password manager to fill saved password --&gt;
&lt;input type="password" autocomplete="current-password"&gt;</code></pre>

<p><strong>WebAuthn / Passkeys integration:</strong></p>
<pre><code>&lt;input type="text"
       autocomplete="username webauthn"
       name="username"&gt;</code></pre>

<p>The <code>webauthn</code> token enables conditional UI &mdash; the browser shows passkey suggestions inline with the username field. User taps a passkey suggestion and signs in with biometrics, no password ever entered.</p>

<p><strong>Common mistakes that break autofill:</strong></p>
<ul>
  <li><strong>Using <code>name="email"</code> without <code>autocomplete="email"</code></strong> &mdash; browsers heuristically detect some fields, but explicit attributes are more reliable.</li>
  <li><strong>Combining first and last name into one field</strong> &mdash; many users have separate values; a combined field guesses wrong.</li>
  <li><strong><code>autocomplete="off"</code> as anti-spam</strong> &mdash; password managers ignore <code>off</code> for security/usability reasons; it just hurts users with no benefit.</li>
  <li><strong>Custom select widgets that hide native <code>&lt;select&gt;</code></strong> &mdash; autofill can&rsquo;t pre-fill a fake dropdown.</li>
</ul>

<p>Proper <code>autocomplete</code> attributes typically lift form completion rates 25-50% on mobile checkout flows. Tiny markup investment, massive UX win.</p>
'''

ANSWERS[99] = r'''
<p><code>&lt;menu&gt;</code> and <code>&lt;menuitem&gt;</code> have a <strong>complicated and largely cautionary history</strong>. Both were originally intended for context menus and toolbars; <code>&lt;menuitem&gt;</code> was removed from HTML5 entirely; <code>&lt;menu&gt;</code> was redefined as a semantic alias for <code>&lt;ul&gt;</code> in toolbars.</p>

<p><strong>Current state in 2026:</strong></p>
<table>
  <tr><th>Element</th><th>Status</th></tr>
  <tr><td><code>&lt;menu&gt;</code></td><td>Valid &mdash; semantic equivalent of <code>&lt;ul&gt;</code> for command/toolbar lists</td></tr>
  <tr><td><code>&lt;menuitem&gt;</code></td><td>Removed &mdash; never widely supported, deprecated and dropped</td></tr>
</table>

<p><strong>The current <code>&lt;menu&gt;</code> element:</strong></p>
<pre><code>&lt;menu&gt;
  &lt;li&gt;&lt;button onclick="bold()"&gt;Bold&lt;/button&gt;&lt;/li&gt;
  &lt;li&gt;&lt;button onclick="italic()"&gt;Italic&lt;/button&gt;&lt;/li&gt;
  &lt;li&gt;&lt;button onclick="underline()"&gt;Underline&lt;/button&gt;&lt;/li&gt;
&lt;/menu&gt;</code></pre>

<p>Renders identically to <code>&lt;ul&gt;</code> with the same default list styling. The semantic difference: <code>&lt;menu&gt;</code> is a list of commands; <code>&lt;ul&gt;</code> is a list of items. In practice, browsers and screen readers treat them similarly.</p>

<p><strong>Why <code>&lt;menuitem&gt;</code> was killed:</strong></p>
<ul>
  <li><strong>Only Firefox implemented it</strong> &mdash; meant for context menus (right-click), it never gained Chrome or Safari support.</li>
  <li><strong>Limited use case</strong> &mdash; required <code>contextmenu</code> attribute on a parent element, which itself was removed.</li>
  <li><strong>Better alternatives existed</strong> &mdash; native <code>&lt;dialog&gt;</code>, the Popover API, and Web Components cover the use cases.</li>
  <li><strong>Cleanup effort</strong> &mdash; spec maintainers removed unused features to simplify the standard.</li>
</ul>

<p>The original (now-defunct) syntax:</p>
<pre><code>&lt;!-- This NO LONGER WORKS in any browser --&gt;
&lt;menu type="context" id="my-menu"&gt;
  &lt;menuitem label="Save" onclick="save()"&gt;&lt;/menuitem&gt;
  &lt;menuitem label="Print" onclick="print()"&gt;&lt;/menuitem&gt;
&lt;/menu&gt;

&lt;div contextmenu="my-menu"&gt;Right-click me!&lt;/div&gt;</code></pre>

<p><strong>Modern alternatives for context menus and toolbars:</strong></p>

<p><strong>1. Toolbars &mdash; use <code>&lt;menu&gt;</code> or just buttons:</strong></p>
<pre><code>&lt;div role="toolbar" aria-label="Editor toolbar"&gt;
  &lt;button title="Bold"&gt;&lt;svg&gt;...&lt;/svg&gt;&lt;/button&gt;
  &lt;button title="Italic"&gt;&lt;svg&gt;...&lt;/svg&gt;&lt;/button&gt;
  &lt;button title="Underline"&gt;&lt;svg&gt;...&lt;/svg&gt;&lt;/button&gt;
&lt;/div&gt;</code></pre>

<p><strong>2. Context menus &mdash; build with the Popover API:</strong></p>
<pre><code>&lt;div id="target" oncontextmenu="event.preventDefault(); showMenu(event);"&gt;
  Right-click for options
&lt;/div&gt;

&lt;div id="ctxMenu" popover&gt;
  &lt;menu&gt;
    &lt;li&gt;&lt;button onclick="copy()"&gt;Copy&lt;/button&gt;&lt;/li&gt;
    &lt;li&gt;&lt;button onclick="paste()"&gt;Paste&lt;/button&gt;&lt;/li&gt;
    &lt;li&gt;&lt;button onclick="del()"&gt;Delete&lt;/button&gt;&lt;/li&gt;
  &lt;/menu&gt;
&lt;/div&gt;

&lt;script&gt;
  function showMenu(e) {
    const menu = document.getElementById("ctxMenu");
    menu.style.left = e.clientX + "px";
    menu.style.top  = e.clientY + "px";
    menu.showPopover();
  }
&lt;/script&gt;</code></pre>

<p>The Popover API + CSS Anchor Positioning provides everything <code>&lt;menuitem&gt;</code> tried to do, with full styling control and proper accessibility.</p>

<p><strong>3. Dropdown menus &mdash; use <code>&lt;details&gt;</code> or libraries:</strong></p>
<pre><code>&lt;details&gt;
  &lt;summary&gt;File&lt;/summary&gt;
  &lt;menu&gt;
    &lt;li&gt;&lt;a href="/new"&gt;New&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/open"&gt;Open&lt;/a&gt;&lt;/li&gt;
    &lt;li&gt;&lt;a href="/save"&gt;Save&lt;/a&gt;&lt;/li&gt;
  &lt;/menu&gt;
&lt;/details&gt;</code></pre>

<p>For accessible production menus with arrow-key navigation and proper ARIA, libraries like Radix Menu, Headless UI Menu, or shadcn/ui&rsquo;s DropdownMenu handle the complete menu pattern.</p>

<p><strong>What to know for interviews:</strong></p>
<ul>
  <li><strong><code>&lt;menu&gt;</code> still exists</strong> &mdash; same role as <code>&lt;ul&gt;</code> for command/toolbar lists.</li>
  <li><strong><code>&lt;menuitem&gt;</code> was removed</strong> &mdash; don&rsquo;t use it; it doesn&rsquo;t work.</li>
  <li><strong>Modern context menus</strong> use Popover API + custom JS; native context menus aren&rsquo;t a built-in HTML feature.</li>
  <li><strong>Arrow-key keyboard navigation</strong> in custom menus requires explicit JS handling (not built into <code>&lt;menu&gt;</code>).</li>
</ul>

<p>This is a great example of HTML&rsquo;s "remove what nobody uses" philosophy &mdash; <code>&lt;menuitem&gt;</code> joined <code>&lt;keygen&gt;</code>, <code>&lt;isindex&gt;</code>, and other failed elements in the spec graveyard. Knowing what doesn&rsquo;t exist is part of being an effective HTML author.</p>
'''

ANSWERS[100] = r'''
<p><code>&lt;link rel="preload"&gt;</code> tells the browser <strong>fetch this resource immediately at high priority</strong> &mdash; even before the parser would normally discover it. It&rsquo;s a performance optimization: critical fonts, hero images, and key scripts start loading earlier, improving Core Web Vitals.</p>

<pre><code>&lt;head&gt;
  &lt;!-- Preload the LCP (Largest Contentful Paint) image --&gt;
  &lt;link rel="preload"
        href="/hero.webp"
        as="image"
        type="image/webp"
        fetchpriority="high"&gt;

  &lt;!-- Preload a critical font --&gt;
  &lt;link rel="preload"
        href="/fonts/inter-var.woff2"
        as="font"
        type="font/woff2"
        crossorigin&gt;

  &lt;!-- Preload a critical script --&gt;
  &lt;link rel="preload"
        href="/critical.js"
        as="script"&gt;

  &lt;!-- Preload an early stylesheet --&gt;
  &lt;link rel="preload"
        href="/critical.css"
        as="style"&gt;
&lt;/head&gt;</code></pre>

<p><strong>The <code>as</code> attribute is mandatory</strong> &mdash; it tells the browser the resource type so the right priority and CORS policies apply:</p>
<table>
  <tr><th><code>as</code> value</th><th>Resource</th></tr>
  <tr><td><code>image</code></td><td>Images (<code>&lt;img&gt;</code>, CSS background)</td></tr>
  <tr><td><code>font</code></td><td>Web fonts</td></tr>
  <tr><td><code>style</code></td><td>Stylesheets</td></tr>
  <tr><td><code>script</code></td><td>JavaScript files</td></tr>
  <tr><td><code>video</code> / <code>audio</code></td><td>Media files</td></tr>
  <tr><td><code>fetch</code></td><td>Generic data (e.g. JSON for API calls)</td></tr>
  <tr><td><code>document</code></td><td>iframe documents</td></tr>
</table>

<p><strong>Critical detail: <code>crossorigin</code> on fonts.</strong> Fonts are always fetched in CORS mode, even from your own origin. Forgetting <code>crossorigin</code> on a font preload causes it to be fetched twice (once via preload, once again when the font is actually used). The font goes unused and the optimization backfires.</p>

<p><strong>The full family of resource hints:</strong></p>
<table>
  <tr><th>Hint</th><th>What it does</th><th>Use when</th></tr>
  <tr><td><code>preload</code></td><td>Fetch a specific resource immediately at high priority</td><td>Critical resource needed for current page</td></tr>
  <tr><td><code>prefetch</code></td><td>Fetch with low priority for likely-next navigation</td><td>Resource for a future page</td></tr>
  <tr><td><code>preconnect</code></td><td>Open TCP/TLS connection to an origin</td><td>You&rsquo;ll fetch from a known third-party origin</td></tr>
  <tr><td><code>dns-prefetch</code></td><td>Resolve DNS for an origin</td><td>Lighter version of preconnect</td></tr>
  <tr><td><code>modulepreload</code></td><td>Preload an ES module + its dependencies</td><td>Critical ES module entry point</td></tr>
</table>

<p><strong>Combining hints for maximum effect:</strong></p>
<pre><code>&lt;head&gt;
  &lt;!-- DNS resolution for third-party CDN --&gt;
  &lt;link rel="preconnect" href="https://cdn.example.com" crossorigin&gt;

  &lt;!-- Preload the hero image (LCP) --&gt;
  &lt;link rel="preload"
        href="https://cdn.example.com/hero.webp"
        as="image"
        fetchpriority="high"&gt;

  &lt;!-- Preload the next likely page --&gt;
  &lt;link rel="prefetch" href="/next-page.html" as="document"&gt;

  &lt;!-- Preload the main script --&gt;
  &lt;link rel="modulepreload" href="/app.js"&gt;
&lt;/head&gt;</code></pre>

<p><strong>Speculation Rules API</strong> (2026) &mdash; the modern successor to prefetch for entire navigations:</p>
<pre><code>&lt;script type="speculationrules"&gt;
{
  "prerender": [
    { "where": { "href_matches": "/products/*" }, "eagerness": "moderate" }
  ]
}
&lt;/script&gt;</code></pre>

<p>The browser pre-renders likely-next pages (full HTML+CSS+JS) so navigation feels instant. More aggressive than prefetch; works for first-party origins.</p>

<p><strong>When to use preload &mdash; and when NOT to:</strong></p>
<ul>
  <li><strong>Use it for:</strong>
    <ul>
      <li>The LCP image (your hero / above-the-fold visual).</li>
      <li>Critical fonts (especially when they&rsquo;d cause FOIT/FOUT).</li>
      <li>Above-the-fold scripts that block rendering.</li>
      <li>Fetch calls the page makes immediately on load.</li>
    </ul>
  </li>
  <li><strong>Don&rsquo;t use it for:</strong>
    <ul>
      <li>Below-the-fold images (lazy load instead).</li>
      <li>Resources used on other pages (use <code>prefetch</code>).</li>
      <li>Anything you&rsquo;re not sure will be used &mdash; an unused preload wastes bandwidth and is reported as a warning by Lighthouse.</li>
      <li>Too many resources &mdash; preloading everything is the same as preloading nothing; you push out priority for what actually matters.</li>
    </ul>
  </li>
</ul>

<p><strong>Validate your preload usage</strong>: Lighthouse and Chrome DevTools Performance tab show preload effectiveness. Look for warnings like "preload not used within a few seconds of load" &mdash; means the resource was preloaded unnecessarily.</p>

<p>Used judiciously, <code>&lt;link rel="preload"&gt;</code> can shave hundreds of milliseconds off LCP &mdash; one of the highest-impact, lowest-effort performance optimizations available.</p>
'''
