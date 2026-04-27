ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Reconciliation</strong> is React&rsquo;s algorithm for determining what changed between two render outputs and updating the DOM as efficiently as possible. After a component re-renders, React produces a new tree of React elements (the &ldquo;virtual DOM&rdquo;) and compares it against the previous tree to compute the minimum set of DOM mutations.</p>

<p><strong>The diffing rules</strong> are deliberately simple to keep the algorithm O(n) instead of O(n³):</p>

<table>
  <tr><th>Rule</th><th>Behavior</th></tr>
  <tr><td>Different element types</td><td>Replace the whole subtree (e.g., <code>&lt;div&gt;</code> → <code>&lt;span&gt;</code>)</td></tr>
  <tr><td>Same type, different props</td><td>Keep DOM node, mutate only changed attributes</td></tr>
  <tr><td>Same component, new props</td><td>Reuse instance, run hooks/lifecycle with new props</td></tr>
  <tr><td>List items with stable keys</td><td>Match by key; reorder/insert/delete as needed</td></tr>
  <tr><td>List items without keys</td><td>Match by index &mdash; usually wrong if list reorders</td></tr>
</table>

<p><strong>Why keys matter</strong>: without them, React assumes positional matching. Inserting an item at the start of a list with index-based keys causes React to think every existing item changed. Stable keys (database IDs, UUIDs &mdash; not array indices) let React match items across renders even when order changes.</p>

<p><strong>React Fiber</strong> (since React 16) split reconciliation into two phases: a <strong>render phase</strong> (interruptible, builds work-in-progress tree) and a <strong>commit phase</strong> (synchronous, applies DOM mutations). This is what enables Concurrent Mode features like <code>useTransition</code>, <code>useDeferredValue</code>, and Suspense &mdash; React can pause work for high-priority updates and resume later.</p>

<p>In practice, reconciliation is invisible to most code. You write components; React figures out the minimal DOM mutations. Where it shows up: bad keys causing extra renders, type changes thrashing subtrees, or component types that change between renders (defining components inside other components is a common pitfall &mdash; new type each render = full unmount/remount).</p>
'''

ANSWERS[2] = r'''
<p>The <strong>virtual DOM</strong> is an in-memory representation of the UI as a tree of plain JavaScript objects (React elements). When state changes, React builds a new tree, compares it to the previous one, and applies the minimal set of mutations to the real DOM.</p>

<p><strong>Why it exists</strong>: real DOM operations are expensive (layout, paint, composite). Reading/writing DOM nodes individually triggers reflows. By batching changes through an intermediate representation, React minimizes work and provides a declarative programming model &mdash; you describe what the UI should look like, React figures out how to get there.</p>

<p><strong>The flow per update</strong>:</p>

<ol>
  <li>State changes via <code>setState</code> / hook update.</li>
  <li>React calls the component function/render again, producing new React elements.</li>
  <li>React diffs the new tree against the previous (Fiber tree).</li>
  <li>React commits minimum DOM mutations in a single pass.</li>
  <li>Browser paints the result.</li>
</ol>

<p><strong>Common misconception</strong>: virtual DOM isn&rsquo;t inherently faster than direct DOM manipulation done well. A hand-tuned imperative update can beat React. Virtual DOM&rsquo;s value is in <strong>predictability + maintainability</strong>: declarative code is easier to reason about, and React&rsquo;s diffing is fast enough that you almost never need to think about it.</p>

<table>
  <tr><th>Layer</th><th>What it represents</th></tr>
  <tr><td>JSX</td><td>Sugar for <code>React.createElement(...)</code> calls</td></tr>
  <tr><td>React element</td><td>Plain object: <code>{ type, props, children }</code></td></tr>
  <tr><td>Fiber node</td><td>Internal work unit; has parent/sibling/child links</td></tr>
  <tr><td>DOM node</td><td>Real <code>HTMLElement</code> in the browser</td></tr>
</table>

<p><strong>Modern alternatives</strong>: Svelte and SolidJS skip the virtual DOM entirely &mdash; they compile components to direct DOM updates at build time. Often faster for narrow benchmarks. React&rsquo;s VDOM is the trade-off for its component model and ecosystem; the React Compiler (R19+) closes some of the gap by auto-memoizing.</p>
'''

ANSWERS[3] = r'''
<p><strong>React portals</strong> render a component&rsquo;s output into a different part of the DOM tree than its parent &mdash; while keeping the React tree relationship intact (events, context, state). Created with <code>createPortal(children, container)</code>.</p>

<p><strong>The key insight</strong>: a portal lets you escape DOM-level constraints (overflow clipping, z-index stacking, CSS transforms) without breaking React&rsquo;s logical hierarchy. The component still receives Context from React parents and bubbles synthetic events upward through them &mdash; even though it lives in a separate DOM subtree.</p>

<pre><code>import { createPortal } from "react-dom";

function Modal({ children }) {
  return createPortal(
    &lt;div className="modal"&gt;{children}&lt;/div&gt;,
    document.getElementById("modal-root")
  );
}</code></pre>

<p><strong>Use cases</strong>:</p>

<table>
  <tr><th>Scenario</th><th>Why a portal</th></tr>
  <tr><td>Modals / dialogs</td><td>Avoid <code>overflow: hidden</code> on parent clipping the modal</td></tr>
  <tr><td>Tooltips</td><td>Render at <code>body</code> level to escape <code>position: relative</code> ancestors</td></tr>
  <tr><td>Dropdowns / popovers</td><td>Same as tooltips &mdash; need to escape stacking contexts</td></tr>
  <tr><td>Toast notifications</td><td>One container at root; any component can mount toasts there</td></tr>
  <tr><td>Embedding into 3rd-party DOM</td><td>Render React content inside non-React DOM regions</td></tr>
</table>

<p><strong>Event bubbling caveat</strong>: synthetic events bubble through the React tree, NOT the DOM tree. A click inside a portaled modal still bubbles to the parent component that rendered it &mdash; useful for click-outside detection but surprising if you expect DOM-level bubbling.</p>

<p><strong>Modern alternatives</strong>: HTML5&rsquo;s <code>&lt;dialog&gt;</code> element + the Popover API (<code>popover</code> attribute) handle many use cases natively in 2026, with built-in focus management and top-layer rendering. Libraries like Radix UI and shadcn/ui still use portals under the hood for compatibility &mdash; but new code can lean on platform features for simpler cases.</p>
'''

ANSWERS[4] = r'''
<p>React stores component state on <strong>Fiber nodes</strong> &mdash; internal work units that mirror the component tree. Each functional component instance has a Fiber with a linked list of hook records; class components store state directly on the Fiber.</p>

<p><strong>The mechanism, simplified</strong>:</p>

<ul>
  <li>When you call <code>useState(initial)</code>, React looks up the current hook slot on the Fiber. First render: creates a new hook record with <code>{ memoizedState, queue, next }</code>. Subsequent renders: reads the existing slot.</li>
  <li>Hook order is positional &mdash; React identifies hooks by call order, not by name. This is why hooks must be called unconditionally (the &ldquo;rules of hooks&rdquo;).</li>
  <li>Calling the setter pushes an update onto a queue. React schedules a re-render, processes the queue, and computes the new state.</li>
  <li>State updates are batched &mdash; multiple setState calls in the same event handler/effect produce one render.</li>
</ul>

<p><strong>Update queue mechanics</strong>: each setter pushes <code>{ action, next }</code>. On render, React replays the queue: <code>state = reducer(state, action)</code> for each. This is why functional updates compose correctly even when called multiple times in one tick:</p>

<pre><code>setCount(c =&gt; c + 1);   // queue: [+1]
setCount(c =&gt; c + 1);   // queue: [+1, +1]
setCount(c =&gt; c + 1);   // queue: [+1, +1, +1]
// final state: previous + 3</code></pre>

<p><strong>Concurrent rendering</strong>: React 18+ may pause rendering mid-tree, throw away the work-in-progress, and start over. The Fiber architecture supports this because the &ldquo;work-in-progress&rdquo; tree is separate from the &ldquo;current&rdquo; (committed) tree &mdash; only on commit do they swap.</p>

<table>
  <tr><th>State location</th><th>Type</th></tr>
  <tr><td>Function component <code>useState</code></td><td>Hook records on Fiber</td></tr>
  <tr><td>Class component <code>this.state</code></td><td>Class instance on Fiber</td></tr>
  <tr><td>Reducer (<code>useReducer</code>)</td><td>Same as useState (one queue per call)</td></tr>
  <tr><td>Refs (<code>useRef</code>)</td><td>Mutable object; not state &mdash; doesn&rsquo;t cause re-renders</td></tr>
  <tr><td>Context</td><td>Values flow via the Provider; consumers subscribe</td></tr>
</table>

<p><strong>Why this matters in practice</strong>: hook order is fragile. Conditional hooks break the positional matching. Defining a component inside another creates a new Fiber on every parent render &mdash; all internal state is lost.</p>
'''

ANSWERS[5] = r'''
<p><code>useContext</code> reads the nearest matching Context Provider&rsquo;s current value. It&rsquo;s React&rsquo;s built-in solution for sharing values across components without prop drilling &mdash; theme, current user, language, feature flags, dependency injection.</p>

<p><strong>The mechanism</strong>: Context creates a Provider component that publishes a value, and consumers (<code>useContext</code> or <code>&lt;Context.Consumer&gt;</code>) read it. When the Provider&rsquo;s value changes, ALL descendant consumers re-render &mdash; not just the ones whose specific data changed.</p>

<pre><code>const ThemeContext = createContext("light");

function App() {
  const [theme, setTheme] = useState("light");
  return (
    &lt;ThemeContext.Provider value={theme}&gt;
      &lt;Page /&gt;
    &lt;/ThemeContext.Provider&gt;
  );
}

function DeepChild() {
  const theme = useContext(ThemeContext);   // reads current value
  return &lt;div className={theme}&gt;...&lt;/div&gt;;
}</code></pre>

<p><strong>Common pitfalls</strong>:</p>

<table>
  <tr><th>Pitfall</th><th>Fix</th></tr>
  <tr><td>Provider value is a fresh object every render</td><td>Wrap in <code>useMemo</code> &mdash; otherwise all consumers re-render every time</td></tr>
  <tr><td>One context with many fields → over-rendering</td><td>Split into multiple smaller contexts; or use selector libraries</td></tr>
  <tr><td>Prop drilling avoidance taken too far</td><td>Context for app-wide concerns only; pass props for local needs</td></tr>
  <tr><td>Default value never used in real apps</td><td>Set it to a meaningful fallback or throw an error to catch missing Provider</td></tr>
</table>

<p><strong>Use cases that fit Context well</strong>: theme, locale, current user, dependency injection (e.g., providing a service instance to deep children). <strong>Use cases that don&rsquo;t</strong>: high-frequency updating values (mouse position, scroll), large state with many independent fields (use Zustand/Jotai/Redux instead).</p>

<p><strong>Selector pattern for fine-grained subscriptions</strong>: libraries like <code>use-context-selector</code> let consumers subscribe to a slice and re-render only when their slice changes. React 19&rsquo;s <code>use(Context)</code> hook reads context conditionally (allowed inside if/loops &mdash; unique to <code>use</code>); still triggers full subtree re-render on change.</p>

<p><strong>Context vs Redux vs Zustand</strong>: Context excels at infrequent app-wide values; Zustand/Jotai are better for granular subscriptions; Redux Toolkit shines when you need action logging, middleware, and complex state machines.</p>
'''

ANSWERS[6] = r'''
<p>Memoization in React caches a computed value or rendered output, returning the cached result when inputs haven&rsquo;t changed. React provides three primary tools: <strong><code>React.memo</code></strong> (component-level), <strong><code>useMemo</code></strong> (value-level), and <strong><code>useCallback</code></strong> (function reference-level).</p>

<table>
  <tr><th>Tool</th><th>Caches</th><th>Used for</th></tr>
  <tr><td><code>React.memo(Comp)</code></td><td>Component render output</td><td>Skip re-render when props are shallowly equal</td></tr>
  <tr><td><code>useMemo(fn, deps)</code></td><td>The return value of <code>fn</code></td><td>Expensive computations, stable object/array references</td></tr>
  <tr><td><code>useCallback(fn, deps)</code></td><td>The function reference</td><td>Stable handler identity for memoized children / hook deps</td></tr>
</table>

<p><strong>How <code>React.memo</code> works</strong>: wraps a component with a shallow-prop-equality check. If new props are <code>===</code> equal to previous props, React reuses the previous render output instead of calling the function again. Custom equality function can be passed as a second argument for fine-grained control.</p>

<pre><code>const ProductRow = React.memo(function ProductRow({ product, onSelect }) {
  // Only re-renders if `product` or `onSelect` change by reference
  return &lt;tr&gt;...&lt;/tr&gt;;
}, (prevProps, nextProps) =&gt; {
  // Optional custom comparator
  return prevProps.product.id === nextProps.product.id;
});</code></pre>

<p><strong>The reference-equality trap</strong>: passing a fresh object/array/function every render defeats memo. Combine <code>memo</code> with <code>useMemo</code>/<code>useCallback</code> in the parent.</p>

<p><strong>When memoization helps</strong>: large lists where most items don&rsquo;t change between renders, expensive derived data, components passed as props (e.g., to virtualized lists). <strong>When it doesn&rsquo;t</strong>: cheap components, components where most renders DO have changed props (memo&rsquo;s comparison wastes time without skipping anything).</p>

<p><strong>2026 reality &mdash; the React Compiler</strong>: included in React 19+, automatically applies memoization where beneficial by analyzing component code. Most manual <code>useMemo</code>/<code>useCallback</code>/<code>memo</code> calls become unnecessary in compiler-enabled projects. The compiler errs on the side of correctness; you can opt out with <code>"use no memo"</code> directive if needed.</p>

<p><strong>Profile before memoizing</strong>: React DevTools Profiler shows actual render times. Premature optimization adds complexity for no measured benefit; memoize what&rsquo;s actually slow.</p>
'''

ANSWERS[7] = r'''
<p>A <strong>higher-order component (HOC)</strong> is a function that takes a component and returns a new component with additional props or behavior. The pattern was the dominant code-sharing mechanism in React until hooks (2019) replaced most use cases.</p>

<pre><code>function withAuth(WrappedComponent) {
  return function ProtectedComponent(props) {
    const user = useAuth();
    if (!user) return &lt;Navigate to="/login" /&gt;;
    return &lt;WrappedComponent {...props} user={user} /&gt;;
  };
}

// Usage
const ProtectedDashboard = withAuth(Dashboard);</code></pre>

<p><strong>HOC conventions</strong>:</p>
<ul>
  <li>Named with <code>with*</code> prefix.</li>
  <li>Pass through original props with <code>{...props}</code>.</li>
  <li>Don&rsquo;t mutate the original component &mdash; return a new one.</li>
  <li>Forward refs with <code>React.forwardRef</code> if needed (refs aren&rsquo;t props).</li>
  <li>Hoist static methods if the wrapped component had them (<code>hoist-non-react-statics</code> library).</li>
  <li>Set <code>displayName</code> for better DevTools output: <code>ProtectedComponent.displayName = `withAuth(${WrappedComponent.displayName})`</code>.</li>
</ul>

<p><strong>HOC vs hooks</strong>: hooks won. Compare:</p>

<pre><code>// HOC pattern (older)
const PageWithAuth = withAuth(withLogger(withTheme(Page)));   // wrapper hell

// Hooks (modern)
function Page() {
  const user = useAuth();
  const logger = useLogger();
  const theme = useTheme();
  // ...
}</code></pre>

<p><strong>Why hooks replaced HOCs</strong>:</p>

<table>
  <tr><th>HOCs</th><th>Hooks</th></tr>
  <tr><td>Wrapper-hell trees in DevTools</td><td>Flat tree, easy to inspect</td></tr>
  <tr><td>Naming conflicts on props</td><td>No prop collision &mdash; values are local variables</td></tr>
  <tr><td>Hard to type with TypeScript</td><td>Hooks have natural type inference</td></tr>
  <tr><td>Awkward composition</td><td>Hooks compose naturally</td></tr>
  <tr><td>Hidden complexity in props</td><td>Explicit calls visible at use site</td></tr>
</table>

<p><strong>When HOCs still make sense in 2026</strong>: error boundaries (still must be class components &mdash; the only common HOC use case left), library APIs that need to inject behavior wholesale (<code>react-redux</code>&rsquo;s legacy <code>connect</code>, <code>react-router</code>&rsquo;s deprecated <code>withRouter</code>). For new code, <strong>prefer custom hooks</strong>; reach for HOCs only when wrapping behavior that hooks can&rsquo;t express (rare).</p>
'''

ANSWERS[8] = r'''
<p>Global state in large React apps means data that multiple unrelated components need to read or update &mdash; auth user, theme, cart, notifications, server data. The right tool depends on what kind of state and how it changes.</p>

<table>
  <tr><th>State type</th><th>Recommended (2026)</th><th>Why</th></tr>
  <tr><td>Server data (API responses)</td><td>TanStack Query / SWR</td><td>Caching, deduplication, refetch &mdash; specialized for async data</td></tr>
  <tr><td>Lightweight client state</td><td>Zustand / Jotai</td><td>Tiny bundles, granular subscriptions, hooks-native API</td></tr>
  <tr><td>Complex client state with team conventions</td><td>Redux Toolkit</td><td>Action logging, time-travel debugging, established patterns</td></tr>
  <tr><td>App-wide infrequent values (theme, locale)</td><td>React Context</td><td>Built-in, no library; OK for low-frequency updates</td></tr>
  <tr><td>URL state (filters, search)</td><td><code>useSearchParams</code> + Context</td><td>Shareable URLs, bookmarkable views</td></tr>
  <tr><td>Form state</td><td>React Hook Form</td><td>Form-specific concerns (validation, dirty tracking)</td></tr>
</table>

<p><strong>The critical distinction</strong>: server state vs client state. They have fundamentally different concerns:</p>

<ul>
  <li><strong>Server state</strong>: cached, can become stale, may need to refetch on focus, handled by TanStack Query/SWR. Don&rsquo;t put server data in Redux/Zustand &mdash; you&rsquo;re reimplementing what these libraries do.</li>
  <li><strong>Client state</strong>: owned by your app, transient (modal open, selected tab, draft form). Use Zustand/Jotai/Context.</li>
</ul>

<p><strong>Architecture for a typical large app</strong>:</p>

<pre><code>App
├── &lt;QueryClientProvider /&gt;           ← TanStack Query for server data
├── &lt;AuthProvider /&gt;                  ← Context for current user
├── &lt;ThemeProvider /&gt;                 ← Context for theme
├── Zustand store                       ← UI state (modals, sidebars, drafts)
└── React Router                        ← URL-driven page state</code></pre>

<p><strong>Avoid these antipatterns</strong>: putting all state in one giant Redux store (forces re-renders), using Context for high-frequency data (mouse position, scroll), prop-drilling 5+ levels (a Context or store is warranted).</p>

<p><strong>Migration in 2026</strong>: many teams are moving server data out of Redux into TanStack Query, keeping Redux Toolkit for genuine client state with complex transitions. New apps often skip Redux entirely &mdash; Zustand + TanStack Query covers most needs with less boilerplate.</p>
'''

ANSWERS[9] = r'''
<p><strong>Render props</strong> is a pattern where a component accepts a function as a prop and calls it to determine what to render. The function receives data/state from the wrapping component and returns JSX.</p>

<pre><code>function MouseTracker({ render }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useEffect(() =&gt; {
    const handler = (e) =&gt; setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () =&gt; window.removeEventListener("mousemove", handler);
  }, []);

  return render(pos);
}

// Usage
&lt;MouseTracker render={pos =&gt; (
  &lt;p&gt;Mouse at: ({pos.x}, {pos.y})&lt;/p&gt;
)} /&gt;</code></pre>

<p><strong>Variations</strong>: the prop is often called <code>render</code> or <code>children</code> (function-as-children pattern):</p>

<pre><code>&lt;MouseTracker&gt;
  {pos =&gt; &lt;p&gt;({pos.x}, {pos.y})&lt;/p&gt;}
&lt;/MouseTracker&gt;</code></pre>

<p>Both approaches let the consumer decide how to render the data &mdash; the wrapping component owns the logic; the caller owns the presentation.</p>

<p><strong>Historical context</strong>: render props (popularized ~2017) and HOCs were the two main code-sharing patterns before hooks. They solved problems hooks now solve more cleanly:</p>

<table>
  <tr><th>Goal</th><th>Render props (older)</th><th>Hooks (modern)</th></tr>
  <tr><td>Share state logic</td><td><code>&lt;Mouse&gt;{pos =&gt; ...}&lt;/Mouse&gt;</code></td><td><code>const pos = useMouse();</code></td></tr>
  <tr><td>Compose multiple sources</td><td>Nested render props (pyramid hell)</td><td>Multiple hooks, flat code</td></tr>
  <tr><td>TypeScript inference</td><td>Awkward callback types</td><td>Natural type inference</td></tr>
  <tr><td>JSX nesting</td><td>Components inside callbacks</td><td>Plain JSX</td></tr>
</table>

<p><strong>Where render props still make sense in 2026</strong>:</p>
<ul>
  <li><strong>Library APIs</strong> that need to expose internal state to the consumer&rsquo;s rendered output without dictating layout (e.g., <code>react-virtualized</code>, headless table libraries).</li>
  <li><strong>Compound components</strong> that pass measured data to children: <code>&lt;Resizable&gt;{({ width, height }) =&gt; ...}&lt;/Resizable&gt;</code>.</li>
  <li><strong>Conditional render orchestration</strong>: passing render functions for empty/error/loaded states.</li>
</ul>

<p><strong>For new application code</strong>: prefer custom hooks. Reach for render props only when you&rsquo;re writing reusable library components that need maximum layout flexibility.</p>
'''

ANSWERS[10] = r'''
<p><strong>Controlled components</strong> have their value driven by React state &mdash; every change goes through <code>onChange</code> + <code>setState</code>. <strong>Uncontrolled components</strong> manage their own internal state in the DOM; React reads it via refs only when needed.</p>

<table>
  <tr><th></th><th>Controlled</th><th>Uncontrolled</th></tr>
  <tr><td>Value source</td><td>React state</td><td>DOM (the input itself)</td></tr>
  <tr><td>Updates</td><td>Re-render on every keystroke</td><td>No re-renders during typing</td></tr>
  <tr><td>Read value</td><td>Already in state</td><td>Read via ref when needed</td></tr>
  <tr><td>Validation on every keystroke</td><td>Easy</td><td>Awkward</td></tr>
  <tr><td>Performance with large forms</td><td>Slower (many re-renders)</td><td>Faster</td></tr>
  <tr><td>Initial value</td><td><code>value={initial}</code></td><td><code>defaultValue={initial}</code></td></tr>
</table>

<p><strong>Controlled example</strong>:</p>

<pre><code>function Controlled() {
  const [name, setName] = useState("");
  return (
    &lt;input
      value={name}
      onChange={e =&gt; setName(e.target.value)}
    /&gt;
  );
}</code></pre>

<p><strong>Uncontrolled example</strong>:</p>

<pre><code>function Uncontrolled() {
  const inputRef = useRef(null);

  const handleSubmit = () =&gt; {
    console.log("Value:", inputRef.current.value);
  };

  return (
    &lt;&gt;
      &lt;input ref={inputRef} defaultValue="" /&gt;
      &lt;button onClick={handleSubmit}&gt;Submit&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>When to use controlled</strong>: real-time validation, conditional disabling based on input, transforming user input as they type (e.g., uppercase, masking). Most React forms historically used controlled by default.</p>

<p><strong>When to use uncontrolled</strong>: large forms (10+ fields) where re-rendering on every keystroke matters; integrating with non-React form code; file inputs (must be uncontrolled &mdash; you can&rsquo;t programmatically set <code>&lt;input type="file"&gt;</code>); React Hook Form&rsquo;s entire premise.</p>

<p><strong>React Hook Form&rsquo;s clever trick</strong>: it uses uncontrolled inputs by default for performance &mdash; the inputs manage their own values; RHF reads them via refs at submit time. Validation on blur or submit. The result: large forms with 50+ fields stay snappy.</p>

<p><strong>Common gotcha</strong>: don&rsquo;t mix &mdash; React warns if a component switches from controlled to uncontrolled mid-life (passing <code>value={undefined}</code> when it was previously a string, for example). Always provide an initial empty string or use the right mode from the start.</p>
'''

ANSWERS[11] = r'''
<p>React performance optimization happens at three levels: <strong>fewer renders</strong>, <strong>cheaper renders</strong>, and <strong>smaller bundles</strong>. Profile first &mdash; React DevTools Profiler shows what&rsquo;s slow; optimizing without measurement adds complexity for no benefit.</p>

<p><strong>Fewer renders &mdash; reduce work React does:</strong></p>

<table>
  <tr><th>Technique</th><th>Effect</th></tr>
  <tr><td><code>React.memo</code></td><td>Skip re-render when props are shallowly equal</td></tr>
  <tr><td><code>useMemo</code> / <code>useCallback</code></td><td>Stable references prevent breaking memo</td></tr>
  <tr><td>Move state down</td><td>Local state doesn&rsquo;t cause parent re-render</td></tr>
  <tr><td>Lift state only as far as needed</td><td>Less of the tree re-renders on updates</td></tr>
  <tr><td>Split contexts</td><td>Each consumer subscribes to less data</td></tr>
  <tr><td>Avoid inline objects/arrays in props</td><td>New reference each render breaks memoization</td></tr>
</table>

<p><strong>Cheaper renders &mdash; less work per render:</strong></p>
<ul>
  <li><strong>Virtualization</strong>: render only visible items in long lists (TanStack Virtual, react-window).</li>
  <li><strong>Defer work</strong>: <code>useTransition</code> marks updates as non-urgent; React keeps UI responsive while updating in the background.</li>
  <li><strong>Defer values</strong>: <code>useDeferredValue</code> shows stale data while a heavy computation completes.</li>
  <li><strong>Debounce input-driven work</strong>: filter on a 300ms-debounced value, not every keystroke.</li>
</ul>

<p><strong>Smaller bundles:</strong></p>
<ul>
  <li><strong>Code splitting</strong> with <code>React.lazy</code> + Suspense at routes/modals.</li>
  <li><strong>Tree shaking</strong>: prefer named imports over default; ensure <code>"sideEffects": false</code> in <code>package.json</code> when applicable.</li>
  <li><strong>Bundle analysis</strong>: <code>vite-bundle-visualizer</code> / <code>webpack-bundle-analyzer</code> to find unexpected weight.</li>
  <li><strong>Replace heavy deps</strong>: <code>date-fns</code> over <code>moment</code>; <code>preact-compat</code> for <code>preact</code>; build-time CSS for runtime CSS-in-JS.</li>
</ul>

<p><strong>2026-current tools</strong>: <strong>React Compiler</strong> (R19+) auto-applies memoization where beneficial &mdash; many manual <code>useMemo</code>/<code>useCallback</code> calls are unnecessary in compiler-enabled projects. <strong>React Server Components</strong> shift work to the server; client never sees server-component code. <strong>Million.js</strong> as a drop-in optimizer that re-implements parts of the VDOM for hot list rendering.</p>

<p><strong>The 80/20 rule</strong>: most apps are slow because of (1) un-virtualized large lists, (2) re-renders from inline object props, (3) too much in one Context. Fix these three before reaching for advanced techniques.</p>
'''

ANSWERS[12] = r'''
<p><strong>Server-side rendering (SSR)</strong> generates HTML on the server for each request, sends it to the browser, and then &ldquo;hydrates&rdquo; on the client by attaching React event handlers to the existing DOM. Benefits: faster First Contentful Paint, better SEO, content visible before JS loads.</p>

<p><strong>You don&rsquo;t implement SSR by hand in 2026</strong>. Use a framework:</p>

<table>
  <tr><th>Framework</th><th>Strengths</th></tr>
  <tr><td>Next.js</td><td>Most popular; React Server Components; excellent DX; Vercel-optimized</td></tr>
  <tr><td>Remix</td><td>Web fundamentals; nested routing; loaders/actions; great forms</td></tr>
  <tr><td>TanStack Start (new)</td><td>Type-safe, Vite-based, file routing</td></tr>
  <tr><td>Astro (with React)</td><td>Content-heavy sites; islands architecture</td></tr>
  <tr><td>Hand-rolled (Express + renderToPipeableStream)</td><td>Maximum control; significant complexity</td></tr>
</table>

<p><strong>How SSR works at a high level</strong>:</p>

<ol>
  <li>Browser requests <code>/products</code>.</li>
  <li>Server runs the React tree, calls component functions, fetches needed data (loaders).</li>
  <li>Server streams HTML back: <code>renderToPipeableStream(&lt;App /&gt;)</code> in modern React.</li>
  <li>Browser displays HTML immediately &mdash; users see content before JS loads.</li>
  <li>JS bundle loads. React hydrates &mdash; attaches event handlers, reuses existing DOM.</li>
  <li>App becomes interactive.</li>
</ol>

<p><strong>Streaming SSR</strong> (React 18+ <code>renderToPipeableStream</code>): server starts sending HTML before all data is ready. Suspense boundaries can show fallback HTML; their content streams in as data arrives. Result: TTFB stays low; users see partial UI fast.</p>

<p><strong>React Server Components (RSC)</strong>: a separate paradigm. Server components run only on the server, return serialized output, never ship to the browser. They can <code>await</code> data directly. Client components opt-in with <code>"use client"</code>. Available in Next.js App Router (the recommended approach in 2026).</p>

<pre><code>// app/products/page.jsx (Next.js Server Component — runs on server)
async function ProductsPage() {
  const products = await db.products.findMany();   // direct DB access
  return (
    &lt;ul&gt;
      {products.map(p =&gt; &lt;li key={p.id}&gt;{p.name}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>SSG vs SSR vs ISR vs CSR</strong>: SSR renders per request; <strong>SSG</strong> (static-site generation) renders at build time; <strong>ISR</strong> (incremental static regeneration) regenerates pages periodically; <strong>CSR</strong> (client-side rendering) sends an empty shell and renders in the browser. Most apps mix &mdash; static for marketing, SSR for dynamic, CSR for highly interactive.</p>
'''

ANSWERS[13] = r'''
<p><strong>Hydration</strong> is the process where React attaches event listeners to server-rendered HTML on the client &mdash; turning static markup into an interactive React app. The DOM is already there; React walks it, matching nodes to React elements, registering handlers, restoring state.</p>

<p><strong>Why it&rsquo;s necessary</strong>: SSR sends HTML, but HTML alone is not interactive. Buttons don&rsquo;t respond to clicks, forms don&rsquo;t handle submissions, hooks haven&rsquo;t run. Hydration is React&rsquo;s &ldquo;wake up&rdquo; pass.</p>

<pre><code>// Client entry (Next.js / React Router handle this for you)
import { hydrateRoot } from "react-dom/client";
import App from "./App";

hydrateRoot(document.getElementById("root"), &lt;App /&gt;);</code></pre>

<p><strong>The hydration mismatch problem</strong>: server-rendered HTML must match what the client renders. Differences cause warnings and (in strict cases) the entire subtree to be discarded and re-rendered.</p>

<table>
  <tr><th>Common cause</th><th>Symptom / Fix</th></tr>
  <tr><td><code>new Date()</code> in render</td><td>Different on server vs client; use stable date or render after mount</td></tr>
  <tr><td><code>Math.random()</code></td><td>Always different; use stable IDs or <code>useId</code></td></tr>
  <tr><td>Browser-only code (<code>window</code>, <code>localStorage</code>)</td><td>Guard with <code>typeof window !== "undefined"</code> or run in <code>useEffect</code></td></tr>
  <tr><td>Browser extensions modifying HTML</td><td>Ignored or <code>suppressHydrationWarning</code> on affected nodes</td></tr>
  <tr><td>Conditional rendering based on browser features</td><td>Render server-safe default; switch on mount via state</td></tr>
</table>

<p><strong>Selective hydration (React 18+)</strong>: with streaming SSR + Suspense, parts of the tree hydrate independently. If a high-priority interaction (a click) targets a not-yet-hydrated component, React prioritizes that subtree first. Result: interactive faster than full-tree hydration.</p>

<p><strong>Progressive hydration / islands architecture</strong>: only hydrate components that need interactivity; leave static content as plain HTML. Astro pioneered this; React 19 + RSC provides similar semantics &mdash; client components hydrate, server components don&rsquo;t.</p>

<p><strong>Hydration cost</strong>: parsing HTML and walking the React tree to attach handlers takes time, especially for large trees. Strategies to reduce:</p>
<ul>
  <li><strong>Smaller initial JS bundle</strong> &mdash; less code to parse before hydration starts.</li>
  <li><strong>Code splitting at route boundaries</strong> &mdash; only the current page&rsquo;s JS hydrates.</li>
  <li><strong>Server Components</strong> &mdash; their code never ships, no hydration needed.</li>
  <li><strong>Defer non-critical interactivity</strong> &mdash; comment forms, footer interactions can hydrate after page is interactive.</li>
</ul>

<p><strong>2026 trend</strong>: less hydration overall &mdash; React Server Components shift the model. Most page content stays as static HTML; only the genuinely-interactive parts (forms, dropdowns, modals) ship JS and hydrate.</p>
'''

ANSWERS[14] = r'''
<p><strong>React hooks</strong> are functions starting with <code>use</code> that let you tap into React features (state, lifecycle, context, refs) from functional components. Introduced in React 16.8 (Feb 2019), they replaced the need for class components and unified how reusable logic is shared.</p>

<p><strong>Why they were introduced</strong>:</p>

<table>
  <tr><th>Pre-hooks problem</th><th>How hooks solve it</th></tr>
  <tr><td>Stateful logic was tied to classes</td><td>Functional components can have state</td></tr>
  <tr><td>HOCs and render props caused wrapper hell</td><td>Custom hooks compose cleanly &mdash; flat code</td></tr>
  <tr><td>Lifecycle methods split related code</td><td>Effects co-locate setup + cleanup + dependencies</td></tr>
  <tr><td><code>this</code> binding bugs in class methods</td><td>No <code>this</code>; functions close over values naturally</td></tr>
  <tr><td>Hard to extract logic from a component</td><td>Custom hooks extract logic in one function</td></tr>
  <tr><td>Inconsistent class component patterns</td><td>Hooks impose a single pattern across teams</td></tr>
</table>

<p><strong>The lifecycle problem hooks solved</strong>: with classes, related logic was scattered:</p>

<pre><code>// Class — fetch on mount, cleanup on unmount, refetch on prop change
componentDidMount() { this.fetch(); this.subscribe(); }
componentDidUpdate(prev) { if (prev.id !== this.props.id) this.fetch(); }
componentWillUnmount() { this.cancel(); this.unsubscribe(); }

// Hooks — co-located by concern
useEffect(() =&gt; {
  fetch(id);
  return () =&gt; cancel();
}, [id]);
useEffect(() =&gt; {
  subscribe();
  return () =&gt; unsubscribe();
}, []);</code></pre>

<p><strong>Built-in hooks</strong>: <code>useState</code>, <code>useEffect</code>, <code>useContext</code>, <code>useReducer</code>, <code>useRef</code>, <code>useMemo</code>, <code>useCallback</code>, <code>useLayoutEffect</code>, <code>useImperativeHandle</code>, <code>useId</code>, <code>useTransition</code>, <code>useDeferredValue</code>, <code>useSyncExternalStore</code>, <code>useDebugValue</code>. <strong>React 19 added</strong>: <code>use</code> (read promise/context conditionally), <code>useActionState</code>, <code>useFormStatus</code>, <code>useOptimistic</code>.</p>

<p><strong>The two rules of hooks</strong>: (1) only call at the top level &mdash; not in conditionals/loops/nested functions; (2) only call from React function components or other hooks. The ESLint plugin <code>eslint-plugin-react-hooks</code> enforces both. Reason: React identifies hooks by call order; a conditional skip breaks the matching.</p>

<p><strong>2026 status</strong>: hooks are the primary React API. Class components still work but are rarely written for new code. Error boundaries are the lone exception &mdash; still must be classes (a hook equivalent has been discussed for future React versions but isn&rsquo;t shipped).</p>
'''

ANSWERS[15] = r'''
<p><code>useReducer</code> is React&rsquo;s built-in implementation of the reducer pattern: state transitions are described by pure functions of <code>(state, action) =&gt; newState</code>. It excels for state with multiple sub-values, multiple actions, or transitions where the next state depends on the previous one.</p>

<pre><code>const initialState = { items: [], filter: "all", loading: false };

function reducer(state, action) {
  switch (action.type) {
    case "ADD":         return { ...state, items: [...state.items, action.item] };
    case "REMOVE":      return { ...state, items: state.items.filter(i =&gt; i.id !== action.id) };
    case "TOGGLE":      return { ...state, items: state.items.map(i =&gt;
                          i.id === action.id ? { ...i, done: !i.done } : i
                        )};
    case "SET_FILTER":  return { ...state, filter: action.filter };
    case "LOADING":     return { ...state, loading: action.value };
    default:            throw new Error(`Unknown: ${action.type}`);
  }
}

function TodoApp() {
  const [state, dispatch] = useReducer(reducer, initialState);
  // dispatch({ type: "ADD", item: { id: 1, text: "Learn React" } });
}</code></pre>

<p><strong>useState vs useReducer</strong>:</p>

<table>
  <tr><th>useState</th><th>useReducer</th></tr>
  <tr><td>Simple values; few transitions</td><td>Complex objects; many transitions</td></tr>
  <tr><td>Independent state slices</td><td>State pieces that update together</td></tr>
  <tr><td>Inline updates in handlers</td><td>Named actions describe intent</td></tr>
  <tr><td>Hard to test (bound to component)</td><td>Reducer is a pure function &mdash; easy to unit test</td></tr>
  <tr><td>Scattered update logic</td><td>All transitions in one place</td></tr>
</table>

<p><strong>Lazy initialization</strong>: third argument computes initial state only once. Useful when initial state is expensive or derived from props/localStorage:</p>

<pre><code>const [state, dispatch] = useReducer(reducer, initialArg, init);

function init(initialArg) {
  return { ...computeFromArg(initialArg) };
}</code></pre>

<p><strong>Sharing state across the tree</strong>: combine <code>useReducer</code> with Context to create a mini-Redux without the library:</p>

<pre><code>const StateCtx = createContext(null);
const DispatchCtx = createContext(null);

function Provider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    &lt;StateCtx.Provider value={state}&gt;
      &lt;DispatchCtx.Provider value={dispatch}&gt;
        {children}
      &lt;/DispatchCtx.Provider&gt;
    &lt;/StateCtx.Provider&gt;
  );
}</code></pre>

<p>Splitting state and dispatch into two contexts means components that only dispatch (don&rsquo;t read state) won&rsquo;t re-render on state changes. <code>dispatch</code> identity is stable across renders.</p>

<p><strong>When to graduate to Redux Toolkit</strong>: action logging, time-travel debugging, devtools introspection, middleware (sagas, persistence), or many independent slices that share patterns. For component-local complex state, <code>useReducer</code> is ideal &mdash; no library, no boilerplate.</p>
'''

ANSWERS[16] = r'''
<p>Side effects in functional components are handled by <strong><code>useEffect</code></strong> for non-blocking effects (data fetch, subscriptions, timers) and <strong><code>useLayoutEffect</code></strong> for synchronous effects that must run before browser paint (DOM measurements, synchronous DOM mutations).</p>

<p><strong>The mental model</strong>: an effect describes a synchronization between your component and an external system &mdash; the network, a subscription, the DOM, a timer. React runs the effect after rendering, runs cleanup before re-running it or unmounting.</p>

<pre><code>useEffect(() =&gt; {
  // Set up the side effect
  const subscription = chatService.subscribe(roomId, onMessage);

  // Cleanup runs before next effect run or on unmount
  return () =&gt; subscription.unsubscribe();
}, [roomId]);  // re-syncs when roomId changes</code></pre>

<p><strong>Dependency array semantics</strong>:</p>

<table>
  <tr><th>Deps</th><th>When effect runs</th></tr>
  <tr><td>Omitted</td><td>After every render &mdash; rarely correct</td></tr>
  <tr><td><code>[]</code> empty</td><td>Once after mount; cleanup on unmount</td></tr>
  <tr><td><code>[a, b]</code></td><td>After mount; whenever <code>a</code> or <code>b</code> change</td></tr>
</table>

<p><strong>Cleanup is not optional</strong>. Subscriptions, timers, and event listeners must be torn down or they leak. The cleanup function runs before the next effect AND on unmount &mdash; React handles both cases the same way.</p>

<p><strong>Common side effect categories</strong>:</p>

<table>
  <tr><th>Effect</th><th>Pattern</th></tr>
  <tr><td>Fetch data</td><td>AbortController + cancellation flag</td></tr>
  <tr><td>Subscription</td><td>Subscribe + return unsubscribe</td></tr>
  <tr><td>Timer / interval</td><td>Set + return clear</td></tr>
  <tr><td>DOM event listener</td><td>Add + return remove</td></tr>
  <tr><td>Manual DOM manipulation</td><td>useLayoutEffect (synchronous, pre-paint)</td></tr>
  <tr><td>Logging / analytics</td><td>useEffect (post-paint, non-blocking)</td></tr>
</table>

<p><strong>Effects you DON&rsquo;T need</strong> (React docs emphasize this):</p>
<ul>
  <li><strong>Transforming data for rendering</strong> &mdash; do it inline or with <code>useMemo</code>; not in an effect that calls <code>setState</code>.</li>
  <li><strong>Handling user events</strong> &mdash; use event handlers; effects run after render, too late for &ldquo;the user clicked&rdquo; logic.</li>
  <li><strong>Resetting state on prop change</strong> &mdash; use a <code>key</code> prop to remount the component instead.</li>
  <li><strong>Expensive computation</strong> &mdash; <code>useMemo</code> caches the result; doesn&rsquo;t need an effect.</li>
</ul>

<p><strong>2026 alternatives for data fetching</strong>: TanStack Query, SWR, RTK Query handle the loading/error/refetch lifecycle better than raw <code>useEffect</code>. React 19&rsquo;s <code>use(promise)</code> with Suspense reads promises directly without effects. Reach for <code>useEffect</code> for non-data side effects (subscriptions, browser APIs, manual DOM).</p>

<p><strong>Strict Mode double-invocation</strong>: in dev, React runs effects twice on mount to surface bugs (missing cleanup, side effects in render). Effects must be idempotent &mdash; safe to run twice.</p>
'''

ANSWERS[17] = r'''
<p><code>useImperativeHandle</code> customizes what a parent receives when it attaches a ref to a component &mdash; instead of getting the underlying DOM node, the parent gets a curated object of methods you choose to expose.</p>

<pre><code>import { useRef, useImperativeHandle, forwardRef } from "react";

const FancyInput = forwardRef(function FancyInput(props, ref) {
  const inputRef = useRef(null);

  useImperativeHandle(ref, () =&gt; ({
    focus: () =&gt; inputRef.current.focus(),
    clear: () =&gt; { inputRef.current.value = ""; },
    select: () =&gt; inputRef.current.select()
  }), []);   // deps: when to recompute the imperative API

  return &lt;input ref={inputRef} {...props} /&gt;;
});

// Parent uses the imperative API
function App() {
  const ref = useRef(null);
  return (
    &lt;&gt;
      &lt;FancyInput ref={ref} /&gt;
      &lt;button onClick={() =&gt; ref.current.focus()}&gt;Focus&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>What problem it solves</strong>: forwarding refs typically gives the parent direct DOM access (<code>ref.current === HTMLInputElement</code>). That&rsquo;s often too much &mdash; the parent could call any DOM method, read internals, mutate styles. <code>useImperativeHandle</code> lets the child expose a deliberate API surface, hiding internal implementation details.</p>

<table>
  <tr><th>Without useImperativeHandle</th><th>With useImperativeHandle</th></tr>
  <tr><td>Parent gets full DOM node</td><td>Parent gets curated method object</td></tr>
  <tr><td>Implementation details leak</td><td>Internal structure can change without breaking parent</td></tr>
  <tr><td>Anything is callable</td><td>Only documented methods exposed</td></tr>
</table>

<p><strong>When to use it</strong>:</p>
<ul>
  <li><strong>Imperative APIs that don&rsquo;t fit the props model</strong>: <code>focus()</code>, <code>scrollIntoView()</code>, <code>play()</code>, <code>open()</code>. These are one-off commands, not state.</li>
  <li><strong>Component libraries</strong>: third-party widgets (custom date pickers, modal managers, video players) commonly expose imperative methods.</li>
  <li><strong>Animation triggers</strong>: <code>shake()</code>, <code>pulse()</code>, <code>highlightThenFade()</code>.</li>
</ul>

<p><strong>When NOT to use it</strong>: most parent-child communication should flow through props (data going down, callbacks coming up). Reach for imperative handles only when state-based communication is awkward &mdash; specifically, for one-shot commands that have no logical &ldquo;state&rdquo;.</p>

<p><strong>React 19 simplification</strong>: <code>forwardRef</code> is no longer required &mdash; <code>ref</code> is now a regular prop. The example becomes:</p>

<pre><code>function FancyInput({ ref, ...props }) {
  const inputRef = useRef(null);
  useImperativeHandle(ref, () =&gt; ({ focus, clear, select }), []);
  return &lt;input ref={inputRef} {...props} /&gt;;
}</code></pre>

<p><strong>Anti-pattern</strong>: don&rsquo;t use <code>useImperativeHandle</code> to expose state mutators (<code>setValue</code>, <code>setOpen</code>). That belongs in props with <code>value</code>/<code>onChange</code>. Reserve it for genuinely imperative actions.</p>
'''

ANSWERS[18] = r'''
<p>A <strong>custom hook</strong> is a function whose name starts with <code>use</code> and that calls other hooks. It encapsulates reusable stateful logic so components can share behavior without duplication or wrapper hell.</p>

<pre><code>// Custom hook: track an external value with localStorage sync
function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() =&gt; {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initial;
    } catch {
      return initial;
    }
  });

  useEffect(() =&gt; {
    try { localStorage.setItem(key, JSON.stringify(value)); }
    catch {}
  }, [key, value]);

  return [value, setValue];
}

// Use it
const [theme, setTheme] = useLocalStorage("theme", "light");</code></pre>

<p><strong>Convention rules</strong>: name starts with <code>use</code> (lints/validates hook usage); only call from React functions or other hooks; can call any built-in or custom hooks internally. Two consumers of the same custom hook get isolated state instances &mdash; just like calling <code>useState</code> twice.</p>

<p><strong>Common patterns</strong>:</p>

<table>
  <tr><th>Custom hook</th><th>Encapsulates</th></tr>
  <tr><td><code>useDebounce(value, delay)</code></td><td>Debounce rapid changes</td></tr>
  <tr><td><code>useFetch(url)</code></td><td>Data fetching with loading/error/data</td></tr>
  <tr><td><code>useMediaQuery(query)</code></td><td>Reactive media-query matching</td></tr>
  <tr><td><code>useOnClickOutside(ref, handler)</code></td><td>Detect clicks outside an element</td></tr>
  <tr><td><code>usePrevious(value)</code></td><td>Get the previous render&rsquo;s value</td></tr>
  <tr><td><code>useIntersectionObserver(ref)</code></td><td>Track element visibility</td></tr>
  <tr><td><code>useEventListener(type, handler)</code></td><td>Attach + clean up listener</td></tr>
</table>

<p><strong>Design principles for good custom hooks</strong>:</p>
<ul>
  <li><strong>Return values, not JSX</strong> &mdash; hooks compose with components, they don&rsquo;t replace them.</li>
  <li><strong>Stable function references</strong> &mdash; wrap returned callbacks in <code>useCallback</code> if consumers might use them as deps.</li>
  <li><strong>One concept per hook</strong> &mdash; a hook should have one reason to change. <code>useFormState</code> shouldn&rsquo;t also handle authentication.</li>
  <li><strong>Predictable signatures</strong> &mdash; mirror built-in hooks: <code>useFoo()</code> returns a tuple or object; setters are stable; deps are explicit.</li>
  <li><strong>Side-effect cleanup</strong> &mdash; if your hook subscribes to anything, return cleanup from the internal effect.</li>
</ul>

<p><strong>Custom hooks vs HOCs/render props</strong>: hooks won. Sharing logic via custom hooks produces flatter component trees, better TypeScript inference, and natural composition (you can use ten custom hooks side by side; ten HOCs nest pyramidally).</p>

<p><strong>Library hooks in 2026</strong>: <code>react-use</code>, <code>usehooks-ts</code>, <code>@uidotdev/usehooks</code>, <code>react-hook-form</code>, <code>@tanstack/react-query</code>, <code>@react-aria/*</code>. Most app-specific logic is still better as your own hook (custom to your domain), but these libraries cover hundreds of common cases.</p>
'''

ANSWERS[19] = r'''
<p><strong>Compound components</strong> is a pattern where a parent component shares implicit state with its children via Context, letting consumers compose UIs declaratively without prop drilling. The classic example is HTML&rsquo;s native <code>&lt;select&gt;</code> + <code>&lt;option&gt;</code> &mdash; the parent manages selection; children declare options.</p>

<pre><code>// Compound component: Tabs
const TabsContext = createContext(null);

function Tabs({ defaultValue, children }) {
  const [active, setActive] = useState(defaultValue);
  const value = useMemo(() =&gt; ({ active, setActive }), [active]);
  return &lt;TabsContext.Provider value={value}&gt;{children}&lt;/TabsContext.Provider&gt;;
}

function TabList({ children }) {
  return &lt;div role="tablist"&gt;{children}&lt;/div&gt;;
}

function Tab({ value, children }) {
  const { active, setActive } = useContext(TabsContext);
  return (
    &lt;button
      role="tab"
      aria-selected={active === value}
      onClick={() =&gt; setActive(value)}
    &gt;
      {children}
    &lt;/button&gt;
  );
}

function TabPanel({ value, children }) {
  const { active } = useContext(TabsContext);
  if (active !== value) return null;
  return &lt;div role="tabpanel"&gt;{children}&lt;/div&gt;;
}

// Attach for ergonomic API
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage — declarative, flexible composition
&lt;Tabs defaultValue="overview"&gt;
  &lt;Tabs.List&gt;
    &lt;Tabs.Tab value="overview"&gt;Overview&lt;/Tabs.Tab&gt;
    &lt;Tabs.Tab value="settings"&gt;Settings&lt;/Tabs.Tab&gt;
  &lt;/Tabs.List&gt;
  &lt;Tabs.Panel value="overview"&gt;Welcome&lt;/Tabs.Panel&gt;
  &lt;Tabs.Panel value="settings"&gt;Configure...&lt;/Tabs.Panel&gt;
&lt;/Tabs&gt;</code></pre>

<p><strong>Why this pattern wins for component libraries</strong>:</p>

<table>
  <tr><th>Compound components</th><th>Single-component config</th></tr>
  <tr><td>Flexible JSX composition</td><td>Rigid prop structure</td></tr>
  <tr><td>Each piece can be styled / wrapped</td><td>Hard to customize sub-pieces</td></tr>
  <tr><td>HTML-like semantic structure</td><td>Often abstract config objects</td></tr>
  <tr><td>Add intermediate elements freely</td><td>API rewrite needed</td></tr>
  <tr><td>Children are visible in JSX</td><td>Children obscured in props</td></tr>
</table>

<p><strong>vs the &ldquo;config object&rdquo; alternative</strong>:</p>

<pre><code>// Config-driven (less flexible)
&lt;Tabs
  tabs={[
    { value: "overview", label: "Overview", content: "Welcome" },
    { value: "settings", label: "Settings", content: "Configure..." }
  ]}
/&gt;</code></pre>

<p>The compound version lets you wrap a tab in a tooltip, add an icon between elements, or insert a divider &mdash; all without changing the API. The config version requires API extensions for each new variation.</p>

<p><strong>Real-world examples</strong>: <code>shadcn/ui</code>, <code>Radix UI</code>, <code>React Aria Components</code>, <code>Reach UI</code>, <code>Headless UI</code> &mdash; all major headless component libraries use this pattern. <code>Dialog.Root</code>, <code>Dialog.Trigger</code>, <code>Dialog.Content</code> is the standard ergonomic shape.</p>

<p><strong>Best practices</strong>: throw a clear error if a child is used without its Provider parent (<code>useTabsContext</code> hook can do this). Document required parent-child relationships. Memoize the Context value to prevent over-rendering.</p>
'''

ANSWERS[20] = r'''
<p>Functional components handle errors at three levels: <strong>try/catch in event handlers/effects</strong> (synchronous and async errors), <strong>error boundaries</strong> (rendering errors that bubble up), and <strong>data-library error states</strong> (TanStack Query <code>error</code>, etc.).</p>

<p><strong>Critically: error boundaries do NOT catch:</strong></p>
<ul>
  <li>Errors in event handlers.</li>
  <li>Async errors (setTimeout, promises that aren&rsquo;t awaited in render).</li>
  <li>Server-side rendering errors.</li>
  <li>Errors thrown in the boundary itself.</li>
</ul>

<p><strong>For event handler errors</strong>: standard try/catch, plus state for UI feedback.</p>

<pre><code>function SaveButton() {
  const [error, setError] = useState(null);

  const handleSave = async () =&gt; {
    setError(null);
    try {
      await api.save();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    &lt;&gt;
      &lt;button onClick={handleSave}&gt;Save&lt;/button&gt;
      {error &amp;&amp; &lt;p role="alert"&gt;{error}&lt;/p&gt;}
    &lt;/&gt;
  );
}</code></pre>

<p><strong>For effect errors</strong>: same pattern, inside the effect.</p>

<pre><code>useEffect(() =&gt; {
  let cancelled = false;

  async function load() {
    try {
      const data = await fetch(url).then(r =&gt; {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      });
      if (!cancelled) setData(data);
    } catch (err) {
      if (!cancelled) setError(err);
    }
  }
  load();
  return () =&gt; { cancelled = true; };
}, [url]);</code></pre>

<p><strong>For rendering errors</strong>: error boundaries (still must be class components in 2026; the only common class-component use case left). Functional code can use the <code>react-error-boundary</code> library for hook-friendly ergonomics:</p>

<pre><code>import { ErrorBoundary } from "react-error-boundary";

function FallbackUI({ error, resetErrorBoundary }) {
  return (
    &lt;div role="alert"&gt;
      &lt;p&gt;Something went wrong: {error.message}&lt;/p&gt;
      &lt;button onClick={resetErrorBoundary}&gt;Retry&lt;/button&gt;
    &lt;/div&gt;
  );
}

&lt;ErrorBoundary
  FallbackComponent={FallbackUI}
  onError={(err, info) =&gt; logToSentry(err, info)}
&gt;
  &lt;Dashboard /&gt;
&lt;/ErrorBoundary&gt;</code></pre>

<p><strong>Strategy &mdash; layered error handling</strong>:</p>

<table>
  <tr><th>Layer</th><th>Catches</th><th>Goal</th></tr>
  <tr><td>Page-level error boundary</td><td>Anything unexpected</td><td>Don&rsquo;t crash the app</td></tr>
  <tr><td>Feature-level error boundaries</td><td>Localized failures</td><td>Isolate bad widgets</td></tr>
  <tr><td>Try/catch in handlers</td><td>Predictable failures (network, validation)</td><td>Show actionable UI</td></tr>
  <tr><td>Data library error states</td><td>API errors</td><td>Built-in retry, error UI</td></tr>
  <tr><td>Logging service</td><td>All caught errors</td><td>Server-side observability</td></tr>
</table>

<p><strong>2026 stack</strong>: <code>react-error-boundary</code> + Sentry/Datadog for boundary errors; TanStack Query for data errors; try/catch for events. The combination handles the vast majority of error scenarios with minimal boilerplate. Suspense + the new <code>use(promise)</code> hook in React 19 lets error boundaries catch async errors thrown via Suspense &mdash; closing one of the longstanding gaps.</p>
'''

ANSWERS[21] = r'''
<p><strong>React Fiber</strong> is the rewrite of React&rsquo;s reconciliation engine, shipped in React 16 (Sept 2017). It replaced the old recursive stack-based reconciler with a linked-list of work units (Fibers) that React can pause, abort, and resume &mdash; enabling concurrent rendering features.</p>

<p><strong>Why Fiber was needed</strong>: the old reconciler walked the entire tree synchronously. Once started, it had to finish before the browser could paint or respond to input &mdash; long renders caused jank. Fiber splits work into chunks; React processes them, yields control to the browser between chunks, and resumes when it&rsquo;s safe.</p>

<p><strong>The two-phase architecture</strong>:</p>

<table>
  <tr><th>Phase</th><th>What happens</th><th>Interruptible?</th></tr>
  <tr><td>Render</td><td>Build work-in-progress Fiber tree; call component functions; diff with previous</td><td>Yes &mdash; can pause, abort, restart</td></tr>
  <tr><td>Commit</td><td>Apply DOM mutations; run effects; refs attach</td><td>No &mdash; synchronous, atomic</td></tr>
</table>

<p><strong>Fiber as a data structure</strong>: each Fiber represents one component instance with links to parent, sibling, and child. Together they form a tree-shaped linked list React can traverse iteratively (no recursion stack).</p>

<pre><code>// Conceptual Fiber shape
{
  type: "div" | Function | Class,
  props: {...},
  stateNode: HTMLElement | ComponentInstance,
  child: Fiber | null,         // first child
  sibling: Fiber | null,        // next sibling
  return: Fiber | null,         // parent
  alternate: Fiber | null,      // matching node in the other tree
  effectTag: "PLACEMENT" | "UPDATE" | "DELETION" | ...,
  // ... priority, hooks list, ...
}</code></pre>

<p><strong>What Fiber unlocked</strong>:</p>
<ul>
  <li><strong>Concurrent rendering</strong>: <code>useTransition</code>, <code>useDeferredValue</code> &mdash; React can keep UI responsive while a heavy update renders in the background.</li>
  <li><strong>Suspense for code &amp; data</strong>: components can pause rendering while waiting; React swaps in fallback UI.</li>
  <li><strong>Streaming SSR</strong>: server renders incrementally; HTML streams to the client as it&rsquo;s ready.</li>
  <li><strong>Selective hydration</strong>: parts of an SSR&rsquo;d tree hydrate independently; high-priority interactions hydrate first.</li>
  <li><strong>Time slicing</strong>: long renders broken into 5ms chunks; browser can paint and respond to events between chunks.</li>
  <li><strong>Priority-based scheduling</strong>: urgent updates (typing, clicks) preempt less-urgent ones (data refresh).</li>
</ul>

<p><strong>Performance characteristics</strong>: Fiber doesn&rsquo;t make any single render faster &mdash; it makes long renders less disruptive. A 50ms render still takes 50ms in total work, but Fiber spreads it across several frames, leaving room for the browser to paint and respond. The user perceives the app as smooth even though the same total work happens.</p>

<p><strong>2026 reality</strong>: Fiber is a foundational implementation detail you almost never interact with directly. Its API surface (concurrent rendering primitives) is the practical face of Fiber for application code.</p>
'''

ANSWERS[22] = r'''
<p>Lazy loading defers loading code until it&rsquo;s actually needed &mdash; smaller initial bundle, faster first paint, deferred work for sections users may never visit. React provides <code>React.lazy()</code> + Suspense for component-level splits; bundlers (Vite, Webpack) implement the chunk creation behind dynamic <code>import()</code>.</p>

<pre><code>import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Component code is fetched only when first rendered
const Dashboard = lazy(() =&gt; import("./pages/Dashboard"));
const Settings  = lazy(() =&gt; import("./pages/Settings"));
const Billing   = lazy(() =&gt; import("./pages/Billing"));

function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
        &lt;Routes&gt;
          &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
          &lt;Route path="/settings" element={&lt;Settings /&gt;} /&gt;
          &lt;Route path="/billing" element={&lt;Billing /&gt;} /&gt;
        &lt;/Routes&gt;
      &lt;/Suspense&gt;
    &lt;/BrowserRouter&gt;
  );
}</code></pre>

<p><strong>What happens at build time</strong>: bundlers detect dynamic <code>import()</code> calls and emit separate JS chunks. The main bundle stays small &mdash; doesn&rsquo;t include the lazy components. At runtime, React fetches the chunk when the component first renders, shows the Suspense fallback meanwhile, then renders.</p>

<p><strong>Common splitting strategies</strong>:</p>

<table>
  <tr><th>Strategy</th><th>What to split</th><th>Benefit</th></tr>
  <tr><td>Route-based</td><td>Each top-level route</td><td>Biggest payoff per dev effort</td></tr>
  <tr><td>Modal-based</td><td>Modals, dialogs</td><td>Only loaded when opened</td></tr>
  <tr><td>Tab-based</td><td>Each tab&rsquo;s content</td><td>Defer non-active tabs</td></tr>
  <tr><td>Conditional</td><td>Admin-only widgets</td><td>Most users never load</td></tr>
  <tr><td>Below-the-fold</td><td>Heavy components below viewport</td><td>Load on scroll</td></tr>
  <tr><td>Library-based</td><td>Heavy libraries (charts, editors)</td><td>Defer until interactive</td></tr>
</table>

<p><strong>Preloading on hover or proximity</strong>: trigger the import when the user is likely to navigate, before they click:</p>

<pre><code>const Dashboard = lazy(() =&gt; import("./Dashboard"));

&lt;Link
  to="/dashboard"
  onMouseEnter={() =&gt; import("./Dashboard")}   // start loading on hover
&gt;
  Dashboard
&lt;/Link&gt;</code></pre>

<p>By the time the user clicks, the chunk is often already in the cache. Next.js does this automatically for visible <code>&lt;Link&gt;</code> components.</p>

<p><strong>Pitfalls</strong>:</p>
<ul>
  <li><strong>Default exports required</strong>: <code>React.lazy</code> only works with default exports; for named, wrap manually: <code>lazy(() =&gt; import("./M").then(m =&gt; ({ default: m.Named })))</code>.</li>
  <li><strong>Don&rsquo;t over-split</strong>: too many chunks = many small HTTP requests; balance with <code>splitChunks</code> grouping.</li>
  <li><strong>Loading states matter</strong>: spinner-only fallbacks feel slow; use skeleton screens that match the eventual layout.</li>
  <li><strong>Cumulative layout shift</strong>: lazy-loaded blocks should reserve space (height/aspect-ratio) to avoid layout jumps.</li>
</ul>

<p><strong>Modern frameworks</strong>: Next.js, Remix, TanStack Start all do route-level splitting automatically. You write standard imports; the framework figures out chunks. Vite-based SPAs need explicit <code>React.lazy</code> per route. <strong>React Server Components</strong> obviate much of this &mdash; server-component code never ships at all.</p>
'''

ANSWERS[23] = r'''
<p><strong>Suspense for data fetching</strong> lets components &ldquo;wait&rdquo; for a promise to resolve before rendering, with React showing a fallback UI in the meantime. The component throws a promise; Suspense catches it; React re-renders the subtree when the promise resolves.</p>

<p>Originally used only for code splitting (<code>React.lazy</code>), Suspense became a general async-rendering primitive in React 18+. The cleanest API is <strong>React 19&rsquo;s <code>use(promise)</code> hook</strong>, which reads a promise directly and suspends until it resolves.</p>

<pre><code>import { use, Suspense } from "react";

function PostList({ postsPromise }) {
  const posts = use(postsPromise);   // suspends until promise resolves
  return (
    &lt;ul&gt;
      {posts.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}

function App() {
  // Start fetching as early as possible — at the parent level
  const promise = fetch("/api/posts").then(r =&gt; r.json());
  return (
    &lt;Suspense fallback={&lt;PostListSkeleton /&gt;}&gt;
      &lt;PostList postsPromise={promise} /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>Why this beats <code>useEffect</code> + loading state</strong>:</p>

<table>
  <tr><th>useEffect approach</th><th>Suspense + use approach</th></tr>
  <tr><td>Component renders empty, then fetches</td><td>Component renders with data; suspends if not ready</td></tr>
  <tr><td>Manual loading/error/data state</td><td>Suspense + error boundary handle both</td></tr>
  <tr><td>Each component manages own loading UI</td><td>One Suspense boundary covers many components</td></tr>
  <tr><td>Race conditions, stale closures</td><td>React handles consistency</td></tr>
  <tr><td>&ldquo;Waterfalls&rdquo; from sequential effects</td><td>Promises started early at parent &mdash; parallel</td></tr>
</table>

<p><strong>Streaming with nested Suspense</strong>: independent boundaries reveal as their data arrives.</p>

<pre><code>&lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
  &lt;Header /&gt;

  &lt;Suspense fallback={&lt;ContentSkeleton /&gt;}&gt;
    &lt;MainContent /&gt;
  &lt;/Suspense&gt;

  &lt;Suspense fallback={&lt;SidebarSkeleton /&gt;}&gt;
    &lt;Sidebar /&gt;
  &lt;/Suspense&gt;
&lt;/Suspense&gt;</code></pre>

<p>Header shows immediately; main and sidebar load in parallel and reveal as ready &mdash; no waterfall, smooth progressive UI.</p>

<p><strong>Library integrations</strong>:</p>
<ul>
  <li><strong>TanStack Query</strong>: opt-in via <code>{ suspense: true }</code> or <code>useSuspenseQuery</code> &mdash; integrates with Suspense boundaries.</li>
  <li><strong>SWR</strong>: <code>{ suspense: true }</code>.</li>
  <li><strong>Relay</strong>: native Suspense integration since 2021.</li>
  <li><strong>Next.js App Router</strong>: Suspense + RSC + streaming SSR all integrated.</li>
</ul>

<p><strong>Where Suspense data fetching shines</strong>: server components and SSR. Server-rendered pages can stream HTML chunk-by-chunk as data resolves &mdash; clients see content fast, JS isn&rsquo;t blocking. Combined with parallel data fetching at the route level, this eliminates classic SSR waterfalls.</p>

<p><strong>Caveats</strong>: client-side, you must memoize the promise &mdash; creating a new one on every render means it never resolves consistently. TanStack Query/SWR handle this for you. <code>use()</code> works with Context too: <code>const value = use(MyContext)</code> &mdash; readable in conditionals, unlike <code>useContext</code>.</p>
'''

ANSWERS[24] = r'''
<p><strong>TypeScript</strong> adds static type checking to JavaScript at compile time &mdash; catching errors before code runs, providing autocomplete, and documenting component APIs through types. In 2026, the React community has decisively moved to TypeScript-first; <code>create-react-app</code>, Vite, Next.js, Remix all default to TS.</p>

<p><strong>Concrete benefits in React</strong>:</p>

<table>
  <tr><th>Benefit</th><th>Example</th></tr>
  <tr><td>Component prop contracts</td><td>Compiler catches missing/wrong props at the call site</td></tr>
  <tr><td>Autocomplete on props/state/hooks</td><td>IDE knows your data shapes</td></tr>
  <tr><td>Refactoring confidence</td><td>Rename a prop &mdash; compiler shows every site that breaks</td></tr>
  <tr><td>Docs from code</td><td>Hover any component to see its props</td></tr>
  <tr><td>Catch null/undefined access</td><td><code>strictNullChecks</code> requires explicit handling</td></tr>
  <tr><td>API response types</td><td>Catch field-name mismatches between backend and frontend</td></tr>
</table>

<p><strong>Component props with TypeScript</strong>:</p>

<pre><code>type ButtonProps = {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent&lt;HTMLButtonElement&gt;) =&gt; void;
};

function Button({
  variant = "primary",
  size = "md",
  disabled,
  children,
  onClick
}: ButtonProps) {
  return (
    &lt;button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    &gt;
      {children}
    &lt;/button&gt;
  );
}

// Compiler error if used wrong:
&lt;Button variant="purple"&gt;...&lt;/Button&gt;   // ✗ "purple" not in union</code></pre>

<p><strong>Hooks with generics</strong>:</p>

<pre><code>// Inferred — TypeScript figures out the type
const [count, setCount] = useState(0);             // count: number

// Explicit — for nullable or complex types
const [user, setUser] = useState&lt;User | null&gt;(null);

// useReducer with full types
type Action = { type: "ADD"; item: Todo } | { type: "REMOVE"; id: number };
const [state, dispatch] = useReducer&lt;State, Action&gt;(reducer, init);</code></pre>

<p><strong>Common React types from <code>@types/react</code></strong>:</p>

<table>
  <tr><th>Type</th><th>Use for</th></tr>
  <tr><td><code>React.ReactNode</code></td><td>Anything renderable: string, element, array, null</td></tr>
  <tr><td><code>React.ReactElement</code></td><td>A single React element specifically</td></tr>
  <tr><td><code>React.FC&lt;Props&gt;</code></td><td>Function component (largely fallen out of favor; prefer plain functions)</td></tr>
  <tr><td><code>React.MouseEvent&lt;HTMLButtonElement&gt;</code></td><td>Typed click event</td></tr>
  <tr><td><code>React.ChangeEvent&lt;HTMLInputElement&gt;</code></td><td>Typed change event</td></tr>
  <tr><td><code>React.CSSProperties</code></td><td>Type for inline <code>style</code> prop</td></tr>
  <tr><td><code>React.PropsWithChildren&lt;P&gt;</code></td><td>Props that include <code>children</code></td></tr>
</table>

<p><strong>Inference with libraries</strong>: Zod schemas → TypeScript types via <code>z.infer&lt;typeof schema&gt;</code>. tRPC infers types from server to client. TanStack Query infers data types from query functions. The pattern is the same: write the source of truth once, infer types everywhere.</p>

<p><strong>Why TypeScript replaced PropTypes</strong>: PropTypes ran at runtime in development only; TypeScript catches errors at compile time. PropTypes can&rsquo;t describe complex shapes well; TypeScript&rsquo;s type system is far more expressive (unions, generics, mapped types). PropTypes was deprecated from React 15.5; TypeScript is the default for new projects in 2026.</p>
'''

ANSWERS[25] = r'''
<p>React with GraphQL means using a GraphQL client to fetch typed, declarative data. The dominant 2026 options are <strong>Apollo Client</strong>, <strong>urql</strong>, <strong>Relay</strong>, and <strong>TanStack Query + graphql-request</strong>.</p>

<table>
  <tr><th>Client</th><th>Best for</th><th>Bundle</th></tr>
  <tr><td>Apollo Client</td><td>Most popular; normalized cache; mature ecosystem</td><td>~33KB</td></tr>
  <tr><td>urql</td><td>Lighter, simpler; opt-in normalized cache</td><td>~7KB</td></tr>
  <tr><td>Relay</td><td>Meta&rsquo;s; very powerful; steepest learning curve</td><td>~25KB</td></tr>
  <tr><td>TanStack Query + graphql-request</td><td>Treat GraphQL as REST-ish queries</td><td>~15KB combined</td></tr>
</table>

<p><strong>Apollo Client with typed queries</strong>:</p>

<pre><code>import { ApolloClient, InMemoryCache, ApolloProvider, gql, useQuery, useMutation } from "@apollo/client";

const client = new ApolloClient({
  uri: "/graphql",
  cache: new InMemoryCache()
});

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      posts { id title likes }
    }
  }
`;

function UserProfile({ userId }) {
  const { data, loading, error, refetch } = useQuery(GET_USER, {
    variables: { id: userId }
  });

  if (loading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error) return &lt;p&gt;Error: {error.message}&lt;/p&gt;;

  return (
    &lt;&gt;
      &lt;h1&gt;{data.user.name}&lt;/h1&gt;
      &lt;ul&gt;
        {data.user.posts.map(p =&gt; (
          &lt;li key={p.id}&gt;{p.title} ({p.likes} likes)&lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Why GraphQL pairs well with React</strong>:</p>
<ul>
  <li><strong>Component-driven data</strong>: each component declares the fields it needs; client batches queries.</li>
  <li><strong>Normalized cache</strong>: a user fetched in one component is reused in another &mdash; one source of truth.</li>
  <li><strong>Optimistic updates</strong>: mutate locally, send request, reconcile or roll back.</li>
  <li><strong>Subscriptions</strong>: real-time updates via WebSocket transport.</li>
  <li><strong>Type generation</strong>: tools like GraphQL Code Generator produce TypeScript types from your schema.</li>
</ul>

<p><strong>Code generation workflow (recommended in 2026)</strong>:</p>

<pre><code># schema.graphql + queries.ts → generated types
npx graphql-codegen --config codegen.yml

# Generated types let you write fully typed components:
const { data } = useQuery&lt;GetUserQuery, GetUserQueryVariables&gt;(GET_USER, {
  variables: { id: userId }
});
// data.user is fully typed</code></pre>

<p><strong>Mutations and cache updates</strong>:</p>

<pre><code>const [likePost] = useMutation(LIKE_POST, {
  // Update cache after mutation succeeds
  update(cache, { data: { likePost } }) {
    cache.modify({
      id: cache.identify({ __typename: "Post", id: likePost.id }),
      fields: { likes: () =&gt; likePost.likes }
    });
  },
  // Or use optimistic UI
  optimisticResponse: {
    likePost: { __typename: "Post", id: postId, likes: currentLikes + 1 }
  }
});</code></pre>

<p><strong>When to choose GraphQL over REST</strong>: when your client needs flexible, deeply-nested data and you control the backend. <strong>When to stick with REST</strong>: simple CRUD; existing REST API; team unfamiliarity with GraphQL trade-offs (over-fetching the schema instead of under-fetching endpoints; N+1 query problems on the backend; cache complexity).</p>

<p><strong>Modern alternatives</strong>: <strong>tRPC</strong> for full-stack TypeScript apps gives end-to-end type safety without a schema language. Many teams now choose tRPC for internal APIs and reserve GraphQL for public APIs or federated services.</p>
'''

ANSWERS[26] = r'''
<p>The <strong>Context API</strong> is React&rsquo;s built-in mechanism to pass data through the component tree without prop drilling. <strong>Redux</strong> is a separate library implementing a centralized store with strict patterns (actions, reducers, immutability). They overlap conceptually but solve different problems at different scales.</p>

<table>
  <tr><th></th><th>Context API</th><th>Redux (Toolkit)</th></tr>
  <tr><td>Built-in?</td><td>Yes</td><td>No (separate package)</td></tr>
  <tr><td>Bundle cost</td><td>0 KB</td><td>~12 KB (RTK + react-redux)</td></tr>
  <tr><td>Selective subscription</td><td>No &mdash; all consumers re-render on any change</td><td>Yes &mdash; via <code>useSelector</code> + reference equality</td></tr>
  <tr><td>Devtools / time-travel</td><td>None</td><td>Excellent &mdash; replay actions, inspect state diffs</td></tr>
  <tr><td>Async patterns</td><td>Roll your own</td><td>Built-in (createAsyncThunk, RTK Query)</td></tr>
  <tr><td>Middleware</td><td>None</td><td>Logger, persistence, sagas, etc.</td></tr>
  <tr><td>Best for</td><td>Theming, locale, auth user, low-frequency global data</td><td>Large apps with complex state transitions</td></tr>
</table>

<p><strong>The selective-subscription difference matters most</strong>. With Context, every consumer re-renders when the value changes &mdash; even if they only care about one field. Redux&rsquo;s <code>useSelector</code> uses reference equality to skip re-renders when the selected slice is unchanged.</p>

<pre><code>// Context: cart item count change re-renders everything reading cart
const { items, total, addItem } = useContext(CartContext);

// Redux: only components reading total re-render when total changes
const total = useSelector(s =&gt; s.cart.total);</code></pre>

<p><strong>2026 reality</strong>: most new apps use neither directly. <strong>Zustand/Jotai</strong> for client state (Context-like ergonomics, Redux-like selective subscription, no provider boilerplate). <strong>TanStack Query</strong> for server state (caching, refetch, deduplication). Reach for Context for truly global low-frequency values; Redux for legacy or genuinely complex state machines.</p>
'''

ANSWERS[27] = r'''
<p>Code splitting breaks a single large bundle into smaller chunks loaded on demand &mdash; reducing initial load time. The browser only downloads what&rsquo;s needed for the current view; other features stream in as users navigate to them.</p>

<p><strong>Three splitting strategies</strong>:</p>

<table>
  <tr><th>Strategy</th><th>What gets split</th><th>Trigger</th></tr>
  <tr><td>Route-based</td><td>Each top-level route</td><td>Navigation</td></tr>
  <tr><td>Component-based</td><td>Modals, tabs, heavy widgets</td><td>User interaction</td></tr>
  <tr><td>Library-based</td><td>Heavy deps (charting, editor, video)</td><td>Render time</td></tr>
</table>

<p><strong>Implementation with <code>React.lazy</code> + <code>Suspense</code></strong>:</p>

<pre><code>import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

const Dashboard  = lazy(() =&gt; import("./pages/Dashboard"));
const Reports    = lazy(() =&gt; import("./pages/Reports"));
const Editor     = lazy(() =&gt; import("./pages/Editor"));

function App() {
  return (
    &lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
      &lt;Routes&gt;
        &lt;Route path="/" element={&lt;Dashboard /&gt;} /&gt;
        &lt;Route path="/reports" element={&lt;Reports /&gt;} /&gt;
        &lt;Route path="/editor" element={&lt;Editor /&gt;} /&gt;
      &lt;/Routes&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>The build tool</strong> (Vite, Webpack) detects dynamic imports and emits a separate chunk per <code>import()</code>. Each chunk is fetched on demand with a unique cache-busting hash.</p>

<p><strong>Prefetching</strong> for instant navigation:</p>

<pre><code>// Trigger import on hover — chunk preloads before user clicks
&lt;Link
  to="/reports"
  onMouseEnter={() =&gt; import("./pages/Reports")}
&gt;
  Reports
&lt;/Link&gt;</code></pre>

<p><strong>Benefits</strong>: smaller initial JS payload (faster Time To Interactive), better cache hits (unchanged chunks reused across deploys), parallel loading (browser fetches multiple chunks concurrently).</p>

<p><strong>Don&rsquo;t over-split</strong>: too many small chunks means too many network requests. Group related code; aim for chunks of 50-200 KB. <strong>Modern frameworks</strong> (Next.js, Remix, TanStack Start) auto-split routes &mdash; no manual <code>React.lazy</code> needed.</p>
'''

ANSWERS[28] = r'''
<p>Authentication in a React app has two halves: <strong>authentication</strong> (proving who the user is) and <strong>authorization</strong> (what they can access). The frontend coordinates the user-facing flow; security ultimately lives on the server.</p>

<p><strong>Three common auth strategies</strong>:</p>

<table>
  <tr><th>Strategy</th><th>How it works</th><th>Trade-offs</th></tr>
  <tr><td>JWT in localStorage</td><td>Server returns token; JS reads/sends it</td><td>Easy; vulnerable to XSS</td></tr>
  <tr><td>JWT in httpOnly cookie</td><td>Server sets cookie; browser auto-sends</td><td>XSS-safe; needs CSRF protection</td></tr>
  <tr><td>Session cookie + server</td><td>Traditional session; cookie ID maps to server-side session</td><td>Server stores session state; very secure</td></tr>
</table>

<p><strong>Modern setup &mdash; Auth context + API helper + protected routes</strong>:</p>

<pre><code>// useAuth hook — shared via Context
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Bootstrap on mount: check session/token validity
  useEffect(() =&gt; {
    fetch("/api/me", { credentials: "include" })
      .then(r =&gt; r.ok ? r.json() : null)
      .then(setUser)
      .finally(() =&gt; setLoading(false));
  }, []);

  const login = async (email, password) =&gt; {
    const res = await fetch("/api/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error("Login failed");
    setUser(await res.json());
  };

  const logout = async () =&gt; {
    await fetch("/api/logout", { method: "POST", credentials: "include" });
    setUser(null);
  };

  return (
    &lt;AuthContext.Provider value={{ user, loading, login, logout }}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  );
}

// Protected route guard
function ProtectedRoute({ children, requiredRole }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return &lt;Spinner /&gt;;
  if (!user)   return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  if (requiredRole &amp;&amp; user.role !== requiredRole)
    return &lt;Navigate to="/forbidden" replace /&gt;;
  return children;
}</code></pre>

<p><strong>Production stack in 2026</strong>: <strong>Clerk</strong>, <strong>Auth0</strong>, <strong>Supabase Auth</strong>, <strong>Firebase Auth</strong>, or <strong>NextAuth.js</strong> &mdash; they handle OAuth providers, MFA, password resets, session rotation, and audit logging. Don&rsquo;t roll your own auth from scratch &mdash; the cryptographic and protocol details are unforgiving.</p>

<p><strong>Defense in depth</strong>: client-side guards prevent unauthorized UI access, but server endpoints MUST re-validate every request. Never trust client-side <code>user.role</code> for authorization decisions on the server.</p>
'''

ANSWERS[29] = r'''
<p>The <strong>React DevTools Profiler</strong> records render performance and shows which components re-rendered, why, and how long each render took. Essential for diagnosing performance issues that aren&rsquo;t obvious from looking at the code.</p>

<p><strong>Recording a session</strong>:</p>
<ol>
  <li>Open DevTools → Profiler tab.</li>
  <li>Click the record button (●).</li>
  <li>Reproduce the slow interaction in your app.</li>
  <li>Click record again to stop.</li>
  <li>Inspect the resulting flamegraph.</li>
</ol>

<p><strong>What the flamegraph shows</strong>:</p>

<table>
  <tr><th>View</th><th>Reveals</th></tr>
  <tr><td>Flamegraph chart</td><td>Hierarchy of rendered components, time spent per render</td></tr>
  <tr><td>Ranked chart</td><td>Components sorted by render time &mdash; biggest offenders first</td></tr>
  <tr><td>Component view</td><td>Per-component history: how often it rendered, why, total time</td></tr>
  <tr><td>Commits</td><td>Each render cycle as a discrete bar &mdash; click to inspect</td></tr>
</table>

<p><strong>"Why did this render?"</strong> &mdash; enable in Settings (cog icon) → Profiler. After recording, hovering a component shows the trigger:</p>
<ul>
  <li><strong>Props changed</strong> &mdash; with field-by-field diff (most common cause).</li>
  <li><strong>State changed</strong> &mdash; component called <code>setState</code>.</li>
  <li><strong>Hooks changed</strong> &mdash; specific hook value differs from previous render.</li>
  <li><strong>Parent rendered</strong> &mdash; cascading re-render from above.</li>
</ul>

<p><strong>Common findings and fixes</strong>:</p>

<table>
  <tr><th>Symptom</th><th>Likely cause</th><th>Fix</th></tr>
  <tr><td>Component renders 50+ times for one click</td><td>State updates in render or chained effects</td><td>Batch state, use useReducer, find the loop</td></tr>
  <tr><td>Big subtree re-renders on parent state change</td><td>Inline objects/arrays/functions in props</td><td>useMemo/useCallback or React.memo on children</td></tr>
  <tr><td>List item renders all items on adding one</td><td>Missing or unstable keys</td><td>Use stable IDs as keys, not array indices</td></tr>
  <tr><td>Expensive child renders despite memo</td><td>Function/object props recreated each render</td><td>useCallback/useMemo at parent</td></tr>
</table>

<p><strong>Quantitative discipline</strong>: profile <em>before</em> optimizing. Profile <em>after</em> the fix to confirm improvement. Eyeballing &ldquo;this seems faster&rdquo; is unreliable &mdash; the Profiler gives concrete numbers (ms per render).</p>

<p><strong>2026 update</strong>: the React Compiler (production-ready in React 19) auto-applies memoization where beneficial &mdash; many cases that previously required manual <code>useMemo</code>/<code>useCallback</code> are handled automatically. The Profiler still earns its keep for measuring real-world impact.</p>
'''

ANSWERS[30] = r'''
<p>Both run side effects, but at different times in the render-commit cycle. <strong><code>useEffect</code></strong> fires <strong>after browser paint</strong> &mdash; non-blocking. <strong><code>useLayoutEffect</code></strong> fires <strong>synchronously after DOM mutation, before paint</strong> &mdash; blocks rendering until done.</p>

<table>
  <tr><th></th><th><code>useEffect</code></th><th><code>useLayoutEffect</code></th></tr>
  <tr><td>Timing</td><td>After browser paints</td><td>Before browser paints (synchronous)</td></tr>
  <tr><td>Blocks paint?</td><td>No</td><td>Yes &mdash; can delay UI updates</td></tr>
  <tr><td>Use case</td><td>99% of effects: fetch, subscribe, log, timers</td><td>DOM measurement → state update without flicker</td></tr>
  <tr><td>SSR</td><td>Runs normally</td><td>Doesn&rsquo;t run server-side; warns in SSR</td></tr>
</table>

<p><strong>The visible-flicker test</strong>: if rendering doesn&rsquo;t cause a visible &ldquo;jump&rdquo; between two states, use <code>useEffect</code>. If it does (e.g., element renders at <code>(0,0)</code> then snaps to position), <code>useLayoutEffect</code> updates state before the user sees the wrong state.</p>

<pre><code>// useLayoutEffect: position a tooltip based on target's measurements
function Tooltip({ targetRef }) {
  const tipRef = useRef(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useLayoutEffect(() =&gt; {
    if (!targetRef.current || !tipRef.current) return;
    const target = targetRef.current.getBoundingClientRect();
    const tip = tipRef.current.getBoundingClientRect();
    setPos({
      top: target.top - tip.height - 8,
      left: target.left + target.width / 2 - tip.width / 2
    });
  }, [targetRef]);

  return &lt;div ref={tipRef} style={pos}&gt;Tip text&lt;/div&gt;;
}

// useEffect: data fetch — paints loading state, then fetches in background
useEffect(() =&gt; {
  fetch(`/api/users/${id}`).then(r =&gt; r.json()).then(setUser);
}, [id]);</code></pre>

<p><strong>Why default to useEffect</strong>: it doesn&rsquo;t block the browser&rsquo;s rendering pipeline. Frequent <code>useLayoutEffect</code> usage degrades responsiveness because each one delays paint. Reserve it for measure-then-update DOM scenarios where flicker would otherwise be visible.</p>

<p><strong>SSR caveat</strong>: <code>useLayoutEffect</code> doesn&rsquo;t run on the server (no DOM to measure). React warns when SSR-rendered components use it. For isomorphic libraries, the common pattern is <code>useIsomorphicLayoutEffect</code> &mdash; equals <code>useLayoutEffect</code> in browsers, <code>useEffect</code> on the server.</p>
'''

ANSWERS[31] = r'''
<p>Conditional rendering returns different JSX based on state, props, or computed conditions. React supports several patterns; choose by readability and the kind of decision you&rsquo;re making.</p>

<p><strong>Five idiomatic patterns</strong>:</p>

<table>
  <tr><th>Pattern</th><th>When to use</th></tr>
  <tr><td>Ternary <code>cond ? A : B</code></td><td>Two alternatives</td></tr>
  <tr><td>Logical AND <code>cond &amp;&amp; A</code></td><td>Show or hide one element</td></tr>
  <tr><td>Early return</td><td>Loading/error/empty states at the top</td></tr>
  <tr><td><code>switch</code> or lookup object</td><td>3+ branches</td></tr>
  <tr><td>Component composition</td><td>Truly different layouts &mdash; render different components</td></tr>
</table>

<pre><code>// Early return for clarity (the &ldquo;guard&rdquo; pattern)
function UserProfile({ user, loading, error }) {
  if (loading) return &lt;Spinner /&gt;;
  if (error)   return &lt;ErrorState message={error} /&gt;;
  if (!user)   return &lt;EmptyState /&gt;;
  return &lt;ProfileView user={user} /&gt;;
}

// Lookup object &mdash; clearer than nested ternaries for many branches
const STATUS_VIEWS = {
  idle:      &lt;p&gt;Press start&lt;/p&gt;,
  running:   &lt;Spinner /&gt;,
  succeeded: &lt;SuccessIcon /&gt;,
  failed:    &lt;ErrorIcon /&gt;
};
return STATUS_VIEWS[status] || null;

// Logical AND for "show only if"
{user.isAdmin &amp;&amp; &lt;AdminPanel /&gt;}</code></pre>

<p><strong>The 0-rendering pitfall with <code>&amp;&amp;</code></strong>: when the left side is <code>0</code> (a falsy number), React renders <code>0</code> as text. Wrap with explicit boolean:</p>

<pre><code>// BUG: renders "0" when items.length is 0
{items.length &amp;&amp; &lt;ItemList items={items} /&gt;}

// FIX: explicit boolean
{items.length &gt; 0 &amp;&amp; &lt;ItemList items={items} /&gt;}
{!!items.length &amp;&amp; &lt;ItemList items={items} /&gt;}</code></pre>

<p><strong>Avoid deeply nested ternaries</strong> &mdash; once you have three or more branches, switch to a lookup or extract to a helper component. Nested ternaries are a readability tax with no compensating benefit.</p>

<p><strong>Don&rsquo;t hide via CSS what should be unmounted</strong>: <code>{shouldShow &amp;&amp; &lt;Heavy /&gt;}</code> avoids mounting <code>Heavy</code> until needed. <code>&lt;Heavy style={{ display: shouldShow ? "block" : "none" }} /&gt;</code> mounts it always, paying its render cost. Choose by whether the component is heavy or has side effects (timers, subscriptions).</p>
'''

ANSWERS[32] = r'''
<p>A large React app needs structure to stay maintainable as features grow. The dominant 2026 patterns are <strong>feature-based folders</strong> (preferred) over <strong>type-based folders</strong> (legacy), with strong conventions around imports, testing, and shared code.</p>

<p><strong>Feature-based structure</strong> (recommended):</p>

<pre><code>src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── types.ts
│   │   ├── routes.tsx
│   │   └── index.ts          ← public API
│   ├── billing/
│   ├── dashboard/
│   └── settings/
├── shared/
│   ├── components/           ← truly cross-feature primitives
│   ├── hooks/
│   ├── utils/
│   └── lib/                  ← API client, query client, etc.
├── pages/                    ← route entry points compose features
├── App.tsx
└── main.tsx</code></pre>

<p><strong>Type-based structure</strong> (avoid for large apps):</p>

<pre><code>src/components/, src/hooks/, src/services/, ...
// Hard to find related code; auth files scattered across many directories</code></pre>

<p><strong>Boundaries to enforce</strong>:</p>

<table>
  <tr><th>Rule</th><th>Why</th></tr>
  <tr><td>Features can import from <code>shared/</code></td><td>Shared utilities are dependency-free</td></tr>
  <tr><td>Features must NOT import from each other&rsquo;s internals</td><td>Loose coupling; only via published <code>index.ts</code></td></tr>
  <tr><td>Pages compose features via their public APIs</td><td>Pages = thin orchestration</td></tr>
  <tr><td>Tests live next to the code they test</td><td>Easy to find; encourages writing tests</td></tr>
</table>

<p><strong>TypeScript path aliases</strong> remove fragile relative imports:</p>

<pre><code>// tsconfig.json
{ "compilerOptions": { "paths": { "@/*": ["src/*"] } } }

// In code
import { Button } from "@/shared/components";
import { useAuth } from "@/features/auth";</code></pre>

<p><strong>Other discipline that pays off in large apps</strong>: shared design system (Tailwind + shadcn/ui or a component library); strict TypeScript with no <code>any</code>; ESLint with <code>react/exhaustive-deps</code> and import boundaries enforced; testing pyramid (unit > integration > e2e); CI that blocks merges on test/lint failures; Storybook for component documentation; well-defined Git workflow with PR reviews.</p>

<p><strong>Modular monolith over microfrontends</strong> for most teams: keep one repo, but enforce boundaries with <code>eslint-plugin-boundaries</code>. Microfrontends are valuable at the scale of dozens of teams; below that, the operational complexity outweighs the benefits.</p>
'''

ANSWERS[33] = r'''
<p>Form validation in React covers <strong>schema</strong> (what valid data looks like), <strong>timing</strong> (when to show errors), and <strong>UX</strong> (how to surface them). The 2026 standard combines <strong>React Hook Form</strong> (for state and submission flow) with <strong>Zod</strong> (for schema and TypeScript types).</p>

<p><strong>Why React Hook Form + Zod</strong>:</p>

<table>
  <tr><th>Feature</th><th>Manual <code>useState</code></th><th>RHF + Zod</th></tr>
  <tr><td>Re-renders on each keystroke</td><td>Yes (controlled)</td><td>No (uncontrolled by default)</td></tr>
  <tr><td>Validation logic</td><td>Hand-written, scattered</td><td>One Zod schema, type-inferred</td></tr>
  <tr><td>Async validation</td><td>Custom debouncing</td><td>Built-in</td></tr>
  <tr><td>Field arrays / nested</td><td>Painful</td><td><code>useFieldArray</code></td></tr>
  <tr><td>TypeScript types</td><td>Hand-typed</td><td>Inferred from schema</td></tr>
</table>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Valid email required"),
  password: z.string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "Must contain uppercase")
    .regex(/[0-9]/, "Must contain digit"),
  age: z.coerce.number().int().min(13, "Must be 13+")
});

type SignupData = z.infer&lt;typeof schema&gt;;     // typed automatically

function SignupForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm&lt;SignupData&gt;({
      resolver: zodResolver(schema),
      mode: "onTouched"   // validate after first blur, then live
    });

  const onSubmit = async (data: SignupData) =&gt; {
    await fetch("/api/signup", { method: "POST", body: JSON.stringify(data) });
  };

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)}&gt;
      &lt;input {...register("email")} /&gt;
      {errors.email &amp;&amp; &lt;p&gt;{errors.email.message}&lt;/p&gt;}

      &lt;input type="password" {...register("password")} /&gt;
      {errors.password &amp;&amp; &lt;p&gt;{errors.password.message}&lt;/p&gt;}

      &lt;input type="number" {...register("age")} /&gt;
      {errors.age &amp;&amp; &lt;p&gt;{errors.age.message}&lt;/p&gt;}

      &lt;button type="submit" disabled={isSubmitting}&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>The <code>mode</code> option</strong> controls when validation fires:</p>

<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td><code>onSubmit</code> (default)</td><td>Validate only on submit</td></tr>
  <tr><td><code>onBlur</code></td><td>Validate when field loses focus</td></tr>
  <tr><td><code>onTouched</code></td><td>Wait for first blur, then validate live</td></tr>
  <tr><td><code>onChange</code></td><td>Validate on every keystroke (noisiest)</td></tr>
  <tr><td><code>all</code></td><td>onChange + onBlur</td></tr>
</table>

<p><strong>Server-side validation matters too</strong>: validate the same Zod schema on the server (Node.js + Zod work identically). Client validation is for UX; server validation is the security boundary.</p>

<p><strong>React 19&rsquo;s <code>useActionState</code></strong> is a viable alternative for server-action-driven forms in Next.js / Remix &mdash; combines validation with submit state in fewer hooks.</p>
'''

ANSWERS[34] = r'''
<p>Side effects in Redux mean async work that can&rsquo;t live in reducers (which must be pure). Three middleware patterns dominate: <strong>thunks</strong> (simple), <strong>sagas</strong> (complex orchestration), and <strong>RTK Query</strong> (declarative server state).</p>

<table>
  <tr><th>Tool</th><th>What it&rsquo;s for</th><th>Complexity</th></tr>
  <tr><td><code>createAsyncThunk</code> (RTK)</td><td>Most async logic: API calls, sequenced dispatches</td><td>Low</td></tr>
  <tr><td>RTK Query</td><td>Server-state caching, mutations, polling</td><td>Low (declarative)</td></tr>
  <tr><td>redux-saga</td><td>Complex flows: cancellation, retries, debouncing, racing</td><td>High (generators)</td></tr>
  <tr><td>redux-observable</td><td>Reactive streams via RxJS &mdash; WebSocket pipelines, etc.</td><td>High</td></tr>
</table>

<p><strong><code>createAsyncThunk</code> &mdash; the default for most async</strong>:</p>

<pre><code>import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

export const fetchUser = createAsyncThunk(
  "user/fetch",
  async (userId, { rejectWithValue, signal }) =&gt; {
    try {
      const res = await fetch(`/api/users/${userId}`, { signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const userSlice = createSlice({
  name: "user",
  initialState: { data: null, status: "idle", error: null },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUser.pending,   (s) =&gt; { s.status = "loading"; })
      .addCase(fetchUser.fulfilled, (s, a) =&gt; { s.status = "ok"; s.data = a.payload; })
      .addCase(fetchUser.rejected,  (s, a) =&gt; { s.status = "error"; s.error = a.payload; });
  }
});</code></pre>

<p><strong>RTK Query &mdash; preferred for server-data CRUD</strong>:</p>

<pre><code>import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: ["User"],
  endpoints: (builder) =&gt; ({
    getUser:    builder.query({ query: (id) =&gt; `users/${id}`, providesTags: ["User"] }),
    updateUser: builder.mutation({
      query: ({ id, ...patch }) =&gt; ({
        url: `users/${id}`, method: "PATCH", body: patch
      }),
      invalidatesTags: ["User"]   // auto-refetch getUser after mutation
    })
  })
});

// Auto-generated hooks
export const { useGetUserQuery, useUpdateUserMutation } = api;</code></pre>

<p>One declaration generates: cache normalization, deduplication, polling, optimistic updates, hooks, dev tools integration. Replaces 50+ lines of <code>createAsyncThunk</code> + slice + reducer code.</p>

<p><strong>When sagas are worth the complexity</strong>: cancellable uploads, debounced search across many fields, multi-step wizards with rollback, complex authentication flows, WebSocket message orchestration. For typical CRUD apps, RTK Query covers the use cases at a fraction of the code.</p>

<p><strong>2026 default</strong>: RTK Query for server state; <code>createAsyncThunk</code> for non-fetch async; reach for sagas only when their power genuinely earns the learning curve.</p>
'''

ANSWERS[35] = r'''
<p><strong>Prop drilling</strong> is passing data through multiple intermediate components that don&rsquo;t use it themselves &mdash; just to deliver it to a deeply-nested descendant. Painful to maintain: rename a prop and you touch many files; add a new field and every layer must forward it.</p>

<pre><code>// Painful: theme drills through 4 layers to reach Button
function App({ theme }) {
  return &lt;Layout theme={theme} /&gt;;
}
function Layout({ theme }) {
  return &lt;Sidebar theme={theme} /&gt;;
}
function Sidebar({ theme }) {
  return &lt;NavItem theme={theme} /&gt;;
}
function NavItem({ theme }) {
  return &lt;Button theme={theme} /&gt;;   // FINALLY uses it
}</code></pre>

<p><strong>Five solutions ordered by complexity</strong>:</p>

<table>
  <tr><th>Approach</th><th>When to use</th></tr>
  <tr><td>Component composition (children)</td><td>Layout components &mdash; pass JSX as children, slots</td></tr>
  <tr><td>Context API</td><td>Truly app-wide values: theme, locale, auth user</td></tr>
  <tr><td>Custom hooks</td><td>Encapsulate the data + access logic</td></tr>
  <tr><td>Zustand / Jotai</td><td>Lightweight global state without provider boilerplate</td></tr>
  <tr><td>Redux / Redux Toolkit</td><td>Large app with complex state machines</td></tr>
</table>

<p><strong>Composition often replaces prop drilling entirely</strong>:</p>

<pre><code>// Instead of drilling theme down, accept JSX as children
function Layout({ children }) {
  return &lt;div className="layout"&gt;{children}&lt;/div&gt;;
}

function App() {
  const theme = useTheme();
  return (
    &lt;Layout&gt;
      &lt;Button theme={theme} /&gt;       // theme stays in App; no drilling
    &lt;/Layout&gt;
  );
}</code></pre>

<p><strong>Context for truly cross-cutting values</strong>:</p>

<pre><code>const ThemeContext = createContext("light");

function App() {
  const [theme, setTheme] = useState("light");
  return (
    &lt;ThemeContext.Provider value={theme}&gt;
      &lt;Layout /&gt;
    &lt;/ThemeContext.Provider&gt;
  );
}

function Button() {
  const theme = useContext(ThemeContext);   // jumps directly across the tree
  return &lt;button data-theme={theme}&gt;Click&lt;/button&gt;;
}</code></pre>

<p><strong>Don&rsquo;t over-Context</strong>: Context is global; every consumer re-renders when the value changes. Don&rsquo;t put fast-changing or component-specific data in Context. Reserve it for low-frequency, truly cross-cutting values.</p>

<p><strong>Heuristic</strong>: if a prop passes through more than 2-3 layers without being used, refactor. Small drilling is fine; deep drilling indicates that the data needs a different mechanism (Context, state library, or composition).</p>
'''

ANSWERS[36] = r'''
<p>Refs are React&rsquo;s escape hatch for accessing DOM nodes, storing mutable values that don&rsquo;t trigger re-renders, and exposing imperative APIs from components. Created with <code>useRef</code> in functional components or <code>createRef</code>/<code>React.createRef</code> in class components.</p>

<p><strong>Three primary use cases</strong>:</p>

<table>
  <tr><th>Use case</th><th>Pattern</th></tr>
  <tr><td>Access DOM node directly</td><td><code>&lt;input ref={inputRef} /&gt;</code> + <code>inputRef.current.focus()</code></td></tr>
  <tr><td>Persistent mutable value</td><td><code>const idRef = useRef(0); idRef.current++;</code> &mdash; no re-render</td></tr>
  <tr><td>Imperative API from child</td><td><code>useImperativeHandle</code> exposes specific methods</td></tr>
</table>

<pre><code>import { useRef, useEffect } from "react";

// Use case 1: DOM access — focus on mount
function SearchBar() {
  const inputRef = useRef(null);

  useEffect(() =&gt; {
    inputRef.current.focus();   // imperative DOM call
  }, []);

  return &lt;input ref={inputRef} placeholder="Search..." /&gt;;
}

// Use case 2: Mutable value across renders
function ClickCounter() {
  const clickCount = useRef(0);    // doesn't trigger re-render

  return &lt;button onClick={() =&gt; { clickCount.current++; }}&gt;
    Click (logged: {clickCount.current})
  &lt;/button&gt;;
  // Note: display lags because no re-render — use useState for UI values
}</code></pre>

<p><strong>Critical: refs vs state</strong>:</p>

<table>
  <tr><th></th><th>useRef</th><th>useState</th></tr>
  <tr><td>Triggers re-render?</td><td>No</td><td>Yes</td></tr>
  <tr><td>Value persists across renders?</td><td>Yes</td><td>Yes</td></tr>
  <tr><td>Mutation</td><td>Direct (<code>ref.current = x</code>)</td><td>Setter (<code>setX(x)</code>)</td></tr>
  <tr><td>Read in render?</td><td>Avoid (stale, no re-render guarantee)</td><td>Yes &mdash; primary purpose</td></tr>
  <tr><td>Use for</td><td>DOM nodes, timers, mutable counters, previous values</td><td>Anything that affects what&rsquo;s rendered</td></tr>
</table>

<p><strong>Common patterns</strong>:</p>

<pre><code>// Track previous value
function useprev(value) {
  const ref = useRef();
  useEffect(() =&gt; { ref.current = value; }, [value]);
  return ref.current;
}

// Store interval ID for cleanup
const intervalRef = useRef(null);
useEffect(() =&gt; {
  intervalRef.current = setInterval(() =&gt; {}, 1000);
  return () =&gt; clearInterval(intervalRef.current);
}, []);

// Forward refs to children (React 18 and below)
const FancyInput = forwardRef(function FancyInput(props, ref) {
  return &lt;input ref={ref} {...props} /&gt;;
});

// React 19+: ref is a regular prop, no forwardRef needed
function FancyInput({ ref, ...props }) {
  return &lt;input ref={ref} {...props} /&gt;;
}</code></pre>

<p><strong>Don&rsquo;t use refs as a substitute for state</strong>. If something should affect what&rsquo;s rendered, it&rsquo;s state. Refs are for things React shouldn&rsquo;t care about: DOM nodes, third-party library instances, mutable counters used in side effects.</p>
'''

ANSWERS[37] = r'''
<p>Drag-and-drop in React in 2026 is best done with <strong>dnd-kit</strong> &mdash; the modern, accessible, well-maintained library. The HTML5 Drag-and-Drop API works natively but lacks touch, accessibility, and animation support. <strong>react-beautiful-dnd</strong> (Atlassian) was the previous standard but is now unmaintained.</p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>HTML5 native</td><td>Zero deps; built-in</td><td>Broken on mobile; no a11y; no animations</td></tr>
  <tr><td>dnd-kit (recommended)</td><td>Modern, accessible, touch + keyboard, ~10KB</td><td>API more involved than alternatives</td></tr>
  <tr><td>react-beautiful-dnd</td><td>Easy API; great animations</td><td>Unmaintained since 2023; React 18+ unofficial</td></tr>
  <tr><td>react-dnd</td><td>Powerful; multi-backend (mouse, touch)</td><td>Heavy API; older codebases</td></tr>
</table>

<p><strong>dnd-kit basic sortable list</strong>:</p>

<pre><code>import {
  DndContext, closestCenter, PointerSensor, KeyboardSensor,
  useSensor, useSensors
} from "@dnd-kit/core";
import {
  arrayMove, SortableContext, sortableKeyboardCoordinates,
  useSortable, verticalListSortingStrategy
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function SortableItem({ id, label }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id });
  const style = { transform: CSS.Transform.toString(transform), transition };
  return (
    &lt;li ref={setNodeRef} style={style} {...attributes} {...listeners}&gt;
      {label}
    &lt;/li&gt;
  );
}

function App() {
  const [items, setItems] = useState([
    { id: "1", label: "First" }, { id: "2", label: "Second" }
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = ({ active, over }) =&gt; {
    if (!over || active.id === over.id) return;
    setItems(items =&gt; {
      const oldIndex = items.findIndex(i =&gt; i.id === active.id);
      const newIndex = items.findIndex(i =&gt; i.id === over.id);
      return arrayMove(items, oldIndex, newIndex);
    });
  };

  return (
    &lt;DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}&gt;
      &lt;SortableContext items={items} strategy={verticalListSortingStrategy}&gt;
        &lt;ul&gt;
          {items.map(i =&gt; &lt;SortableItem key={i.id} {...i} /&gt;)}
        &lt;/ul&gt;
      &lt;/SortableContext&gt;
    &lt;/DndContext&gt;
  );
}</code></pre>

<p><strong>dnd-kit&rsquo;s architecture</strong>: <code>DndContext</code> establishes the drag environment; <strong>sensors</strong> define input methods (pointer, touch, keyboard); <strong>collision detection</strong> determines drop targets; <strong>strategies</strong> control how items reflow during drag. Every layer is pluggable.</p>

<p><strong>Production patterns</strong>: persist new order to backend after each drag-end (debounced); use optimistic updates &mdash; UI reflects new order immediately, rollback on save failure; for Kanban-style multi-list, use one <code>DndContext</code> wrapping multiple <code>SortableContext</code>s; for grids, use <code>rectSortingStrategy</code>; for very large lists, virtualize with <code>@dnd-kit/sortable</code> + <code>react-virtual</code>.</p>
'''

ANSWERS[38] = r'''
<p>Integrating imperative third-party libraries (D3, Three.js, Mapbox, Chart.js) with React requires bridging React&rsquo;s declarative model with the library&rsquo;s direct DOM/canvas/WebGL manipulation. The dominant pattern: <strong>React owns the container; the library owns its contents</strong>.</p>

<p><strong>Three integration approaches</strong>:</p>

<table>
  <tr><th>Approach</th><th>When to use</th></tr>
  <tr><td>React for layout, library for visualization</td><td>Most cases &mdash; cleanest separation</td></tr>
  <tr><td>React-wrapped library</td><td>react-three-fiber for Three.js, visx for D3, etc.</td></tr>
  <tr><td>Pure React rendering of library data</td><td>Light wrappers around algorithms</td></tr>
</table>

<p><strong>Pattern 1: D3 for SVG with React owning the container</strong>:</p>

<pre><code>import { useRef, useEffect } from "react";
import * as d3 from "d3";

function BarChart({ data, width = 600, height = 300 }) {
  const svgRef = useRef(null);

  useEffect(() =&gt; {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();      // clear previous render

    const x = d3.scaleBand()
      .domain(data.map(d =&gt; d.label))
      .range([0, width]).padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d =&gt; d.value)])
      .range([height, 0]);

    svg.selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("x", d =&gt; x(d.label))
      .attr("y", d =&gt; y(d.value))
      .attr("width", x.bandwidth())
      .attr("height", d =&gt; height - y(d.value))
      .attr("fill", "#3b82f6");
  }, [data, width, height]);

  return &lt;svg ref={svgRef} width={width} height={height} /&gt;;
}</code></pre>

<p><strong>Pattern 2: react-three-fiber for Three.js (declarative wrapper)</strong>:</p>

<pre><code>import { Canvas, useFrame } from "@react-three/fiber";
import { useRef } from "react";

function Box() {
  const meshRef = useRef();
  useFrame(() =&gt; { meshRef.current.rotation.y += 0.01; });
  return (
    &lt;mesh ref={meshRef}&gt;
      &lt;boxGeometry args={[1, 1, 1]} /&gt;
      &lt;meshStandardMaterial color="orange" /&gt;
    &lt;/mesh&gt;
  );
}

function Scene() {
  return (
    &lt;Canvas&gt;
      &lt;ambientLight /&gt;
      &lt;Box /&gt;
    &lt;/Canvas&gt;
  );
}</code></pre>

<p><strong>Three rules for clean integration</strong>:</p>
<ul>
  <li><strong>Use refs to pin React&rsquo;s container</strong>; let the library mutate inside.</li>
  <li><strong>Cleanup in <code>useEffect</code> return</strong>: dispose of geometries, remove listeners, kill animations &mdash; otherwise leaks accumulate on re-render.</li>
  <li><strong>Don&rsquo;t mix</strong>: don&rsquo;t use React to render elements the library expects to control. Conflicts produce flicker, broken interactions, or memory leaks.</li>
</ul>

<p><strong>Library-specific React wrappers</strong> (highly recommended over manual integration):</p>

<table>
  <tr><th>Imperative</th><th>React wrapper</th></tr>
  <tr><td>Three.js</td><td>react-three-fiber</td></tr>
  <tr><td>D3</td><td>visx (Airbnb), Recharts, Nivo</td></tr>
  <tr><td>Mapbox GL</td><td>react-map-gl</td></tr>
  <tr><td>Leaflet</td><td>react-leaflet</td></tr>
  <tr><td>Chart.js</td><td>react-chartjs-2</td></tr>
</table>

<p>The wrappers handle lifecycle, prop syncing, and cleanup &mdash; orders of magnitude less boilerplate than manual integration.</p>
'''

ANSWERS[39] = r'''
<p>Keys are React&rsquo;s identity hint for list items &mdash; they tell the reconciler which elements correspond between renders. Without stable keys, React falls back to position-based matching, which causes incorrect state preservation, lost focus, and DOM mutations that should have been moves.</p>

<p><strong>What keys do</strong>:</p>

<table>
  <tr><th>Reconciler with stable keys</th><th>Reconciler without keys (or unstable)</th></tr>
  <tr><td>Identifies elements across renders</td><td>Matches by index position</td></tr>
  <tr><td>Move = move (preserves DOM, focus, state)</td><td>Move = update everything in between</td></tr>
  <tr><td>Insert = insert one</td><td>Insert at top = update every item</td></tr>
  <tr><td>Delete = remove one</td><td>Delete at top = shift all updates up</td></tr>
</table>

<pre><code>// Stable keys — React identifies items across renders
{users.map(user =&gt; (
  &lt;UserCard key={user.id} user={user} /&gt;
))}

// Anti-pattern: index as key
{users.map((user, i) =&gt; (
  &lt;UserCard key={i} user={user} /&gt;     // breaks when list reorders
))}</code></pre>

<p><strong>The bug index-as-key causes</strong>:</p>

<pre><code>// Initial: [Alice, Bob]
// Index keys: 0 → Alice, 1 → Bob

// User toggles a checkbox in Bob's row → component state holds checked=true at index 1

// Sort or insert at the top: [Carol, Alice, Bob]
// Index keys: 0 → Carol, 1 → Alice, 2 → Bob

// React thinks index 1 is the same component (it's now Alice).
// The "checked" state stays at index 1, so Alice appears checked.
// Bob (now at index 2) is treated as new — DOM rebuilt, focus lost.</code></pre>

<p><strong>Three rules</strong>:</p>
<ol>
  <li><strong>Use stable, unique IDs from your data</strong> &mdash; database IDs, UUIDs, or content-based hashes for static lists.</li>
  <li><strong>Don&rsquo;t use array index when the list can reorder, insert, or delete</strong>.</li>
  <li><strong>Index is acceptable when</strong> the list is static (never changes), or you guarantee items only ever append (never insert at start/middle).</li>
</ol>

<p><strong>Don&rsquo;t use random values</strong>:</p>

<pre><code>// BUG: new key on every render → React thinks every item is new
{items.map(item =&gt; &lt;Item key={Math.random()} {...item} /&gt;)}
{items.map(item =&gt; &lt;Item key={Date.now()} {...item} /&gt;)}</code></pre>

<p>Random keys defeat reconciliation entirely &mdash; every render rebuilds the DOM. Performance disaster; state and focus permanently lost.</p>

<p><strong>Composite keys for list items without natural IDs</strong>: <code>key={`${userId}-${date}`}</code> if combined fields are unique. For static option lists, the option value works: <code>key={option.value}</code>.</p>

<p><strong>Keys are local to siblings</strong>: two different lists can use the same key value safely. The reconciler only compares siblings within the same parent.</p>
'''

ANSWERS[40] = r'''
<p>React animations span CSS transitions (simplest), <strong>Framer Motion</strong> (most popular), <strong>React Spring</strong> (physics-based), and <strong>GSAP</strong> (timeline-heavy). Choose based on the kind of motion needed and complexity tolerance.</p>

<table>
  <tr><th>Library</th><th>Best for</th><th>Bundle</th></tr>
  <tr><td>CSS transitions/keyframes</td><td>Simple state-driven motion</td><td>0 KB</td></tr>
  <tr><td>Framer Motion</td><td>Most React projects; declarative; gestures + layout</td><td>~50 KB</td></tr>
  <tr><td>React Spring</td><td>Spring physics; data-driven animations</td><td>~25 KB</td></tr>
  <tr><td>GSAP</td><td>Complex timelines; non-React-specific</td><td>~30 KB</td></tr>
  <tr><td>Auto-Animate</td><td>Drop-in for list mount/unmount</td><td>~3 KB</td></tr>
</table>

<p><strong>Framer Motion &mdash; the dominant 2026 choice</strong>:</p>

<pre><code>import { motion, AnimatePresence } from "framer-motion";

function Modal({ isOpen, onClose }) {
  return (
    &lt;AnimatePresence&gt;
      {isOpen &amp;&amp; (
        &lt;motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        &gt;
          Modal content
        &lt;/motion.div&gt;
      )}
    &lt;/AnimatePresence&gt;
  );
}

// Layout animations — auto-animates size/position changes
&lt;motion.div layout&gt;
  {expanded &amp;&amp; &lt;ExtraContent /&gt;}
&lt;/motion.div&gt;

// Drag, hover, tap built in
&lt;motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  drag="x"
  dragConstraints={{ left: -100, right: 100 }}
/&gt;</code></pre>

<p><strong>Why Framer Motion dominates</strong>:</p>
<ul>
  <li><strong>Declarative API</strong> &mdash; describe states; library figures out the path.</li>
  <li><strong>Spring physics</strong> &mdash; natural-feeling motion (no easing-curve guesswork).</li>
  <li><strong><code>layout</code> prop</strong> auto-animates when an element&rsquo;s size or position changes &mdash; Magic.</li>
  <li><strong>Gestures</strong>: drag, hover, tap, focus all built in.</li>
  <li><strong>Choreography</strong>: <code>staggerChildren</code> to delay each child&rsquo;s animation.</li>
  <li><strong>Variants</strong>: named animation states reused across components.</li>
</ul>

<p><strong>Performance fundamentals</strong> (apply to any animation):</p>

<table>
  <tr><th>Animate this</th><th>Avoid animating this</th></tr>
  <tr><td>transform (translate, scale, rotate)</td><td>top, left, width, height</td></tr>
  <tr><td>opacity</td><td>margin, padding</td></tr>
  <tr><td>filter (limited)</td><td>color, background-color (causes paint)</td></tr>
</table>

<p><code>transform</code> and <code>opacity</code> are GPU-accelerated; the others trigger layout recalculations. For 60fps animations, especially on lower-end mobile devices, this distinction matters.</p>

<p><strong>Accessibility</strong>: respect <code>prefers-reduced-motion</code>. Framer Motion supports it via <code>useReducedMotion</code>; manually:</p>

<pre><code>@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}</code></pre>
'''

ANSWERS[41] = r'''
<p><code>useRef</code> creates a mutable container that persists across renders without triggering a re-render when its <code>.current</code> property changes. It&rsquo;s designed for two distinct purposes: <strong>accessing DOM nodes</strong> and <strong>storing mutable values that don&rsquo;t affect rendering</strong>.</p>

<p><strong>Use case: tracking mutable values that survive re-renders</strong></p>

<pre><code>import { useRef, useState, useEffect } from "react";

function StopWatch() {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef(null);   // hold interval ID across renders
  const startedAt   = useRef(null);   // when the timer started

  const start = () =&gt; {
    if (intervalRef.current) return;   // already running
    startedAt.current = Date.now();
    intervalRef.current = setInterval(() =&gt; {
      setElapsed(Date.now() - startedAt.current);
    }, 100);
  };

  const stop = () =&gt; {
    clearInterval(intervalRef.current);
    intervalRef.current = null;
  };

  // Cleanup on unmount
  useEffect(() =&gt; () =&gt; clearInterval(intervalRef.current), []);

  return (
    &lt;&gt;
      &lt;p&gt;{(elapsed / 1000).toFixed(1)}s&lt;/p&gt;
      &lt;button onClick={start}&gt;Start&lt;/button&gt;
      &lt;button onClick={stop}&gt;Stop&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Why <code>useRef</code> instead of state</strong> for the interval ID and start time: changing them shouldn&rsquo;t cause a re-render. Only <code>elapsed</code> drives what&rsquo;s on screen, so it&rsquo;s state. The interval ID is bookkeeping &mdash; it&rsquo;d be wasted work to re-render when it changes.</p>

<p><strong>The <code>usePrevious</code> idiom</strong>:</p>

<pre><code>function usePrevious(value) {
  const ref = useRef();
  useEffect(() =&gt; {
    ref.current = value;
  }, [value]);
  return ref.current;
}

function PriceTracker({ price }) {
  const prevPrice = usePrevious(price);
  const arrow = prevPrice == null ? "" : price &gt; prevPrice ? "↑" : "↓";
  return &lt;div&gt;{price} {arrow}&lt;/div&gt;;
}</code></pre>

<p><strong>Comparison with <code>useState</code></strong>:</p>

<table>
  <tr><th></th><th><code>useRef(initial)</code></th><th><code>useState(initial)</code></th></tr>
  <tr><td>Triggers re-render on change?</td><td>No</td><td>Yes</td></tr>
  <tr><td>Mutation syntax</td><td><code>ref.current = x</code></td><td><code>setX(x)</code></td></tr>
  <tr><td>Read in render</td><td>Discouraged (no re-render guarantee)</td><td>Standard</td></tr>
  <tr><td>Identity stable across renders?</td><td>Same object reference</td><td>Same setter; new value</td></tr>
</table>

<p><strong>Reading <code>.current</code> in render is a code smell</strong>: it suggests the value should drive UI, in which case it should be state. Refs are for things React shouldn&rsquo;t care about: timer IDs, previous values for comparison, third-party library instances, mutable counters used in side effects.</p>

<p><strong>Initial value is computed once</strong>: <code>useRef(expensiveCompute())</code> still calls <code>expensiveCompute()</code> on every render (even though the ref keeps its initial value). For lazy initialization, do <code>const ref = useRef(null); if (ref.current === null) ref.current = compute();</code>.</p>
'''

ANSWERS[42] = r'''
<p>Using array index as a list key tells React: &ldquo;the element at position N is the same element across renders.&rdquo; This breaks badly whenever the list reorders, has insertions/deletions in the middle, or items can be filtered.</p>

<p><strong>Three concrete bugs index-as-key causes</strong>:</p>

<table>
  <tr><th>Scenario</th><th>What goes wrong</th></tr>
  <tr><td>Insert at start</td><td>All items shift; React updates every existing component instead of inserting one</td></tr>
  <tr><td>Component-local state</td><td>Each &ldquo;moved&rdquo; component keeps its old state attached to the new item</td></tr>
  <tr><td>Form input focus</td><td>Focus jumps to a different field after sort or filter</td></tr>
  <tr><td>Optimization with React.memo</td><td>memo&rsquo;d components re-render when their position changes, even with same data</td></tr>
</table>

<p><strong>Concrete demonstration</strong>:</p>

<pre><code>// State: items = [
//   { id: 1, label: "Apple" },
//   { id: 2, label: "Banana" }
// ]

function Wrong() {
  return items.map((item, i) =&gt; (
    &lt;LabelInput key={i} label={item.label} /&gt;
  ));
}

function LabelInput({ label }) {
  const [draft, setDraft] = useState(label);
  return &lt;input value={draft} onChange={e =&gt; setDraft(e.target.value)} /&gt;;
}

// 1. User edits Banana's input → draft="Bananas!"
// 2. Item with id=3 (Cherry) is added at index 0
// 3. New list: [Cherry, Apple, Banana]
// 4. React, using index keys:
//    - index 0 was "Apple", now "Cherry" → updates label prop
//    - But the LOCAL state (draft) of the component at index 0 is preserved!
//    - So Cherry's input still shows "Bananas!" — Banana's leftover state</code></pre>

<p><strong>Stable IDs fix it</strong>:</p>

<pre><code>function Right() {
  return items.map(item =&gt; (
    &lt;LabelInput key={item.id} label={item.label} /&gt;   // stable ID
  ));
}

// React tracks each component by ID. Inserting Cherry at index 0:
// - Cherry: NEW (id=3) → mount with draft="Cherry" (initial)
// - Apple: same ID → keep its state
// - Banana: same ID → keep its state ("Bananas!")</code></pre>

<p><strong>When index keys are SAFE</strong>:</p>
<ul>
  <li>The list is <strong>static</strong> &mdash; never changes.</li>
  <li>The list <strong>only ever appends</strong> (never inserts/sorts/removes).</li>
  <li>Items have <strong>no local state</strong>, no inputs, no animations to preserve.</li>
  <li>The parent re-mounts everything anyway when data changes.</li>
</ul>

<p><strong>What to use instead of index</strong>:</p>

<table>
  <tr><th>Data shape</th><th>Key</th></tr>
  <tr><td>Database records</td><td><code>item.id</code></td></tr>
  <tr><td>API responses</td><td>Server-provided ID</td></tr>
  <tr><td>Generated client-side</td><td><code>crypto.randomUUID()</code> at creation</td></tr>
  <tr><td>Static lookup table</td><td>The unique value: <code>option.value</code> or <code>tag.name</code></td></tr>
  <tr><td>Composite</td><td><code>`${userId}-${timestamp}`</code> if combination is unique</td></tr>
</table>

<p>Don&rsquo;t use <code>Math.random()</code> or <code>Date.now()</code> at render time &mdash; new key on every render breaks reconciliation entirely. Generate the ID once at item creation and store it in your data.</p>
'''

ANSWERS[43] = r'''
<p>Infinite scroll loads more items as the user nears the bottom of the list. The modern, performant approach uses <strong><code>IntersectionObserver</code></strong> to watch a sentinel element &mdash; far better than scroll listeners that fire 60+ times per second.</p>

<p><strong>Three implementation approaches</strong>:</p>

<table>
  <tr><th>Approach</th><th>Trade-offs</th></tr>
  <tr><td>IntersectionObserver + sentinel</td><td>Modern, performant; minimal code</td></tr>
  <tr><td>Scroll event listener + threshold</td><td>Works everywhere; fires too often; needs throttling</td></tr>
  <tr><td>Library (react-infinite-scroll-component)</td><td>Quick setup; less control</td></tr>
</table>

<p><strong>IntersectionObserver pattern (recommended)</strong>:</p>

<pre><code>import { useState, useEffect, useRef } from "react";

function InfiniteList() {
  const [items, setItems] = useState([]);
  const [page, setPage]   = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const sentinelRef = useRef(null);

  // Fetch when page changes
  useEffect(() =&gt; {
    let cancelled = false;
    setLoading(true);
    fetch(`/api/items?page=${page}`)
      .then(r =&gt; r.json())
      .then(data =&gt; {
        if (cancelled) return;
        setItems(prev =&gt; [...prev, ...data.items]);
        setHasMore(data.items.length &gt; 0);
      })
      .finally(() =&gt; !cancelled &amp;&amp; setLoading(false));
    return () =&gt; { cancelled = true; };
  }, [page]);

  // Watch the sentinel — when it enters viewport, load next page
  useEffect(() =&gt; {
    if (loading || !hasMore) return;
    const observer = new IntersectionObserver(
      ([entry]) =&gt; { if (entry.isIntersecting) setPage(p =&gt; p + 1); },
      { rootMargin: "200px" }   // trigger 200px BEFORE entering view
    );
    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () =&gt; observer.disconnect();
  }, [loading, hasMore]);

  return (
    &lt;&gt;
      &lt;ul&gt;{items.map(it =&gt; &lt;li key={it.id}&gt;{it.title}&lt;/li&gt;)}&lt;/ul&gt;
      {hasMore &amp;&amp; &lt;div ref={sentinelRef} style={{ height: 1 }} /&gt;}
      {loading &amp;&amp; &lt;Spinner /&gt;}
      {!hasMore &amp;&amp; &lt;p&gt;End of list&lt;/p&gt;}
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Why this performs better than scroll listeners</strong>:</p>

<table>
  <tr><th></th><th>Scroll listener</th><th>IntersectionObserver</th></tr>
  <tr><td>Fires</td><td>~60×/sec while scrolling</td><td>Once when sentinel enters/leaves viewport</td></tr>
  <tr><td>Main thread</td><td>Synchronous; blocks rendering</td><td>Async; off main thread</td></tr>
  <tr><td>Mobile battery</td><td>Drains</td><td>Efficient</td></tr>
  <tr><td>Code complexity</td><td>Throttling, edge cases</td><td>Simple</td></tr>
</table>

<p><strong>For very long lists, virtualize</strong>: render only visible items with <strong>TanStack Virtual</strong> or <strong>react-window</strong>. Combined with infinite scroll, you can have 100,000 items rendered as 20 DOM nodes. Without virtualization, the DOM grows unbounded; eventually memory and rendering performance degrade noticeably.</p>

<p><strong>Modern alternative: TanStack Query&rsquo;s <code>useInfiniteQuery</code></strong> handles the pagination state, caching, and refetching automatically. The hook returns <code>data.pages</code>, <code>fetchNextPage</code>, <code>hasNextPage</code> &mdash; you only wire up the trigger (sentinel or button). Highly recommended for production.</p>
'''

ANSWERS[44] = r'''
<p>Both Context and Redux propagate data across components without prop drilling, but they differ in <strong>scope</strong>, <strong>performance characteristics</strong>, and <strong>tooling</strong>. The choice depends on the kind and frequency of state being managed.</p>

<table>
  <tr><th></th><th>Context API</th><th>Redux Toolkit</th></tr>
  <tr><td>Origin</td><td>Built into React</td><td>External library</td></tr>
  <tr><td>Bundle</td><td>0 KB</td><td>~12 KB</td></tr>
  <tr><td>Subscription</td><td>All consumers re-render on any change</td><td>Selective via <code>useSelector</code></td></tr>
  <tr><td>State shape constraint</td><td>None</td><td>Single global tree (slices)</td></tr>
  <tr><td>Update mechanism</td><td>Direct (any setter you expose)</td><td>Dispatched actions → reducers</td></tr>
  <tr><td>DevTools</td><td>None specific</td><td>Time travel, action log, state diff</td></tr>
  <tr><td>Async handling</td><td>Roll your own</td><td>createAsyncThunk, RTK Query</td></tr>
  <tr><td>Middleware</td><td>None</td><td>Logger, persistence, sagas</td></tr>
</table>

<p><strong>The performance distinction is the biggest practical difference</strong>:</p>

<pre><code>// Context: ALL consumers re-render on ANY change
const { user, theme, locale, cartTotal, notifications } = useContext(AppContext);
// If notifications adds an item, components reading only `user` re-render too.

// Redux: selective subscription via reference equality
const userName = useSelector(s =&gt; s.user.name);
// Only re-renders when s.user.name actually changes.</code></pre>

<p><strong>When to choose Context</strong>:</p>
<ul>
  <li>Genuinely cross-cutting, low-frequency values: theme, locale, current user, feature flags.</li>
  <li>Small to medium app where extra dependencies are unwarranted.</li>
  <li>Component-local subtree wide state (e.g., a complex form).</li>
</ul>

<p><strong>When to choose Redux Toolkit</strong>:</p>
<ul>
  <li>Many independent state slices that change at different rates.</li>
  <li>Complex state machines (multi-step wizards with rollback, undo/redo).</li>
  <li>Time-travel debugging matters (e.g., reproducing user-reported bugs).</li>
  <li>Team familiarity with Redux patterns; existing codebase.</li>
</ul>

<p><strong>The 2026 reality &mdash; consider neither</strong>:</p>
<ul>
  <li><strong>Zustand / Jotai</strong> for lightweight global state &mdash; selective subscription like Redux, no provider boilerplate, no actions/reducers ceremony.</li>
  <li><strong>TanStack Query / SWR</strong> for server state &mdash; cache, refetch, deduplication built in. Don&rsquo;t put server data in Redux or Context.</li>
  <li><strong>Server Components / RSC + Server Actions</strong> (Next.js 14+) &mdash; eliminates a lot of client state for data-driven apps.</li>
</ul>

<p><strong>The proper mental model</strong>: separate <strong>server state</strong> (data from APIs) from <strong>client state</strong> (UI state, form values, selected items). Use TanStack Query for server state in nearly all cases. For client state: <code>useState</code> first, lift up second, Context for true app-wide values, Zustand/Jotai for global, Redux only when its specific tooling earns its weight.</p>
'''

ANSWERS[45] = r'''
<p>Theme switching combines a <strong>state holder</strong> (current theme), <strong>persistence</strong> (so refreshes don&rsquo;t reset), <strong>system preference detection</strong>, and <strong>application</strong> (CSS variables, data attributes, or class names). The cleanest approach: theme state in Context drives a single <code>data-theme</code> attribute; CSS variables do the rest.</p>

<pre><code>import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

const ThemeContext = createContext&lt;{
  theme: Theme;
  effectiveTheme: "light" | "dark";
  setTheme: (t: Theme) =&gt; void;
}&gt;(null);

function ThemeProvider({ children }) {
  // 1) Load saved preference; default to system
  const [theme, setTheme] = useState&lt;Theme&gt;(() =&gt;
    (localStorage.getItem("theme") as Theme) || "system"
  );

  // 2) Resolve "system" to current OS preference
  const [effectiveTheme, setEffectiveTheme] = useState&lt;"light" | "dark"&gt;("light");

  useEffect(() =&gt; {
    const media = window.matchMedia("(prefers-color-scheme: dark)");

    const updateEffective = () =&gt; {
      if (theme === "system") {
        setEffectiveTheme(media.matches ? "dark" : "light");
      } else {
        setEffectiveTheme(theme);
      }
    };

    updateEffective();
    if (theme === "system") {
      media.addEventListener("change", updateEffective);
      return () =&gt; media.removeEventListener("change", updateEffective);
    }
  }, [theme]);

  // 3) Apply to document; persist preference
  useEffect(() =&gt; {
    document.documentElement.setAttribute("data-theme", effectiveTheme);
    localStorage.setItem("theme", theme);
  }, [theme, effectiveTheme]);

  return (
    &lt;ThemeContext.Provider value={{ theme, effectiveTheme, setTheme }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

const useTheme = () =&gt; useContext(ThemeContext);</code></pre>

<p><strong>CSS drives appearance via the data attribute</strong>:</p>

<pre><code>:root {
  --bg: white;
  --text: #111;
  --primary: #2563eb;
}

[data-theme="dark"] {
  --bg: #0f172a;
  --text: #e2e8f0;
  --primary: #60a5fa;
}

body { background: var(--bg); color: var(--text); }</code></pre>

<p><strong>Avoiding flash of incorrect theme</strong> on initial load: set the <code>data-theme</code> attribute before React hydrates, with an inline script in <code>&lt;head&gt;</code>:</p>

<pre><code>&lt;script&gt;
  (function() {
    var stored = localStorage.getItem("theme");
    var system = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    var theme = stored === "system" || !stored ? system : stored;
    document.documentElement.setAttribute("data-theme", theme);
  })();
&lt;/script&gt;</code></pre>

<p>Without this, users briefly see the default theme before React renders. The script runs synchronously before paint &mdash; no flicker.</p>

<p><strong>Why this approach over JavaScript-driven styling</strong>: CSS variables propagate instantly to every styled element. No prop drilling, no re-renders, no per-component theme logic. Tailwind&rsquo;s dark mode (<code>darkMode: ["class", '[data-theme="dark"]']</code>) integrates with this attribute pattern.</p>

<p><strong>Library options</strong>: <strong>next-themes</strong> for Next.js apps (handles SSR + flash prevention), <strong>shadcn/ui&rsquo;s theme toggle</strong> as a copy-paste reference. Don&rsquo;t reinvent the flash-prevention script &mdash; the edge cases are subtle.</p>
'''

ANSWERS[46] = r'''
<p><strong>Note: Enzyme is unmaintained as of 2024 and never officially supported React 18+.</strong> The 2026 testing standard is <strong>Vitest</strong> (or Jest) + <strong>React Testing Library</strong> (RTL) + <strong>userEvent</strong>. The question asks about Enzyme; the modern answer prioritizes RTL.</p>

<table>
  <tr><th></th><th>Enzyme (legacy)</th><th>RTL (2026 standard)</th></tr>
  <tr><td>React 18+ support</td><td>Unofficial only</td><td>First-class</td></tr>
  <tr><td>Test philosophy</td><td>Implementation details</td><td>User-visible behavior</td></tr>
  <tr><td>Common API</td><td><code>shallow</code>, <code>mount</code>, <code>find</code>, <code>state()</code></td><td><code>render</code>, <code>screen.getByRole</code></td></tr>
  <tr><td>Refactor safety</td><td>Tests break on internal changes</td><td>Survives refactors</td></tr>
  <tr><td>Accessibility coverage</td><td>None</td><td>Queries by role expose a11y issues</td></tr>
</table>

<p><strong>RTL test using user-centric queries</strong>:</p>

<pre><code>import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { rest } from "msw";
import { setupServer } from "msw/node";
import UserProfile from "./UserProfile";

// Mock API at the network layer (HTTP, not module mocking)
const server = setupServer(
  rest.get("/api/users/:id", (req, res, ctx) =&gt;
    res(ctx.json({ id: req.params.id, name: "Alice", email: "alice@example.com" }))
  )
);
beforeAll(() =&gt; server.listen());
afterEach(() =&gt; server.resetHandlers());
afterAll(() =&gt; server.close());

describe("UserProfile", () =&gt; {
  test("displays user data after fetch", async () =&gt; {
    render(&lt;UserProfile userId="1" /&gt;);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Alice" }))
      .toBeInTheDocument();
  });

  test("submits an updated email", async () =&gt; {
    const user = userEvent.setup();
    render(&lt;UserProfile userId="1" /&gt;);

    const emailField = await screen.findByLabelText(/email/i);
    await user.clear(emailField);
    await user.type(emailField, "new@example.com");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(await screen.findByText(/saved/i)).toBeInTheDocument();
  });
});</code></pre>

<p><strong>Three principles RTL teaches</strong>:</p>
<ol>
  <li><strong>Query by role first</strong> &mdash; <code>getByRole("button", { name: "Save" })</code> doubles as an accessibility test.</li>
  <li><strong>Test behavior, not implementation</strong> &mdash; if the component refactors from <code>useState</code> to <code>useReducer</code>, the test still passes.</li>
  <li><strong>Use <code>userEvent</code> over <code>fireEvent</code></strong> &mdash; simulates real user interactions (full event sequences, not single synthetic events).</li>
</ol>

<p><strong>If you must work in an Enzyme codebase</strong>: don&rsquo;t add new Enzyme tests. Migrate gradually &mdash; convert tests to RTL when you change the component anyway. For React 18+ with Enzyme, use <code>@cfaester/enzyme-adapter-react-18</code> (unofficial) but accept that breakage risk grows over time.</p>

<p><strong>Test pyramid for React apps</strong>: many unit tests for hooks and pure functions, integration tests for components (RTL), few end-to-end tests for critical user journeys (Playwright). Skip snapshots except for design-system primitives where any change should require explicit review.</p>
'''

ANSWERS[47] = r'''
<p><strong>Shallow rendering</strong> (Enzyme&rsquo;s <code>shallow()</code>) renders only the component under test and stub-renders its children &mdash; you see the top-level component&rsquo;s output but not what its children produce. Conceptually attractive for &ldquo;isolation&rdquo;, but in practice it&rsquo;s problematic and the modern testing community has moved away from it.</p>

<p><strong>How shallow rendering looked</strong>:</p>

<pre><code>// Enzyme — shallow render UserProfile, but DON'T render Avatar or PostList
import { shallow } from "enzyme";

const wrapper = shallow(&lt;UserProfile userId={1} /&gt;);

// Output looks like:
// &lt;div&gt;
//   &lt;Avatar src="..." /&gt;          ← rendered as a stub, not its actual output
//   &lt;PostList userId={1} /&gt;       ← stub
// &lt;/div&gt;

wrapper.find("Avatar").prop("src");   // can inspect props passed
wrapper.find("PostList").length;      // can count instances
// But you CAN'T see what Avatar or PostList actually render.</code></pre>

<p><strong>Problems with shallow rendering</strong>:</p>

<table>
  <tr><th>Problem</th><th>Why it matters</th></tr>
  <tr><td>Misses integration bugs</td><td>Bugs that emerge from how parent and child interact go undetected</td></tr>
  <tr><td>Tests implementation</td><td>Refactoring an internal component can break shallow tests with no behavior change</td></tr>
  <tr><td>Hooks don&rsquo;t play well</td><td><code>useEffect</code>, <code>useContext</code>, etc., behave inconsistently with shallow</td></tr>
  <tr><td>Modern React</td><td>Suspense, Concurrent features, Server Components don&rsquo;t fit the model</td></tr>
  <tr><td>Tightly couples test and structure</td><td>Tests assert &ldquo;renders an Avatar with src=...&rdquo; instead of &ldquo;shows the user&rsquo;s photo&rdquo;</td></tr>
</table>

<p><strong>The RTL philosophy: full render, query by behavior</strong>:</p>

<pre><code>// React Testing Library — full render, query like a user
import { render, screen } from "@testing-library/react";

render(&lt;UserProfile userId={1} /&gt;);

// Test what users actually see:
expect(screen.getByAltText("Alice's avatar")).toBeInTheDocument();
expect(screen.getByText(/3 posts/)).toBeInTheDocument();

// If UserProfile internally renders Avatar, PostList, or refactors to
// a single component, the test still works as long as the visible behavior
// is the same.</code></pre>

<p><strong>The mental shift</strong>:</p>

<table>
  <tr><th>Old way (Enzyme/shallow)</th><th>New way (RTL)</th></tr>
  <tr><td>&ldquo;Renders Avatar component&rdquo;</td><td>&ldquo;Shows user&rsquo;s photo&rdquo;</td></tr>
  <tr><td>&ldquo;Calls onSave handler with props&rdquo;</td><td>&ldquo;Submits form data to API&rdquo;</td></tr>
  <tr><td>&ldquo;Passes correct prop to child&rdquo;</td><td>&ldquo;Displays expected text after action&rdquo;</td></tr>
  <tr><td>&ldquo;Has state.count = 3&rdquo;</td><td>&ldquo;Displays &lsquo;3 items&rsquo; in cart&rdquo;</td></tr>
</table>

<p><strong>For &ldquo;true isolation&rdquo;</strong> &mdash; mock at network/module boundaries, not component boundaries:</p>
<ul>
  <li><strong>MSW</strong> mocks HTTP requests; component renders normally.</li>
  <li><strong><code>vi.mock</code></strong> mocks specific modules (e.g., heavy third-party).</li>
  <li><strong>Storybook</strong> isolates components for visual/manual testing.</li>
</ul>

<p>Shallow rendering as a general tool is largely abandoned. Mock at the right boundary (network or module), render fully, query by behavior &mdash; the tests are more useful and survive refactors.</p>
'''

ANSWERS[48] = r'''
<p><strong>Next.js</strong> is the dominant React framework for SSR/SSG/ISR/RSC in 2026. The current App Router (Next.js 13.4+) defaults to <strong>React Server Components</strong> &mdash; a fundamentally different rendering model than older Pages Router SSR.</p>

<table>
  <tr><th>Mode</th><th>What it does</th><th>Use for</th></tr>
  <tr><td>Server Components (default)</td><td>Renders on server; zero client JS</td><td>Most pages; data-driven UI</td></tr>
  <tr><td>Client Components (<code>"use client"</code>)</td><td>Hydrates client-side; interactive</td><td>Forms, hooks, browser APIs</td></tr>
  <tr><td>SSG (default for static routes)</td><td>Pre-renders at build time</td><td>Marketing, blog, docs</td></tr>
  <tr><td>ISR (<code>revalidate</code>)</td><td>Periodically regenerates static pages</td><td>Product catalogs, news</td></tr>
  <tr><td>SSR (dynamic routes)</td><td>Re-renders per request</td><td>Personalized dashboards</td></tr>
  <tr><td>Streaming + Suspense</td><td>Stream HTML as data resolves</td><td>Pages with mixed fast/slow data</td></tr>
</table>

<p><strong>App Router with Server Components &mdash; data fetching is just async</strong>:</p>

<pre><code>// app/products/page.tsx — Server Component (default)
async function ProductsPage() {
  const products = await fetch("https://api.example.com/products", {
    next: { revalidate: 60 }   // ISR: regenerate page every 60s
  }).then(r =&gt; r.json());

  return (
    &lt;ul&gt;
      {products.map(p =&gt; (
        &lt;li key={p.id}&gt;
          &lt;Link href={`/products/${p.id}`}&gt;{p.name}&lt;/Link&gt; &mdash; ${p.price}
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

export default ProductsPage;</code></pre>

<p>This component runs <strong>only on the server</strong>. The user receives pre-rendered HTML; the React tree is reconstructed on the client (hydration). Zero JavaScript for the data-fetching logic itself ships to the browser.</p>

<p><strong>Mixing server and client components</strong>:</p>

<pre><code>// app/products/page.tsx — server component
import AddToCartButton from "./AddToCartButton";   // client component

async function ProductsPage() {
  const products = await fetchProducts();
  return products.map(p =&gt; (
    &lt;article key={p.id}&gt;
      &lt;h2&gt;{p.name}&lt;/h2&gt;
      &lt;AddToCartButton productId={p.id} /&gt;        {/* client island */}
    &lt;/article&gt;
  ));
}

// app/AddToCartButton.tsx
"use client";
import { useState } from "react";

export default function AddToCartButton({ productId }) {
  const [adding, setAdding] = useState(false);
  return (
    &lt;button onClick={async () =&gt; {
      setAdding(true);
      await fetch(`/api/cart/${productId}`, { method: "POST" });
      setAdding(false);
    }}&gt;
      {adding ? "Adding..." : "Add to cart"}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Server Actions &mdash; mutations without API endpoints</strong>:</p>

<pre><code>// app/contact/actions.ts
"use server";
export async function submitContact(formData) {
  await db.contact.create({ data: Object.fromEntries(formData) });
  redirect("/thanks");
}

// app/contact/page.tsx
import { submitContact } from "./actions";
export default function Contact() {
  return &lt;form action={submitContact}&gt;...&lt;/form&gt;;   // works without JS!
}</code></pre>

<p><strong>Streaming with Suspense</strong>: each <code>&lt;Suspense&gt;</code> boundary streams HTML as its data resolves. Fast above-the-fold content arrives first; slow analytics widgets stream in independently.</p>

<p><strong>2026 alternatives</strong>: <strong>Remix</strong> (web standards-focused), <strong>TanStack Start</strong> (type-safe full-stack), <strong>Astro</strong> (content-heavy with islands of React). Next.js dominates by share, but Remix offers compelling ergonomics for forms and mutations.</p>
'''

ANSWERS[49] = r'''
<p>React supports both <strong>class components</strong> and <strong>functional components</strong>. Functional components with hooks (introduced in React 16.8, 2019) are now the standard; class components remain valid but are rarely written for new code.</p>

<table>
  <tr><th></th><th>Functional + hooks</th><th>Class components</th></tr>
  <tr><td>State</td><td><code>useState</code>, <code>useReducer</code></td><td><code>this.state</code> + <code>setState</code></td></tr>
  <tr><td>Lifecycle</td><td><code>useEffect</code> with deps</td><td><code>componentDidMount</code>, etc.</td></tr>
  <tr><td>Reusable logic</td><td>Custom hooks (clean composition)</td><td>HOCs, render props (clunky)</td></tr>
  <tr><td>Ref forwarding</td><td>React 19: ref as prop; older: <code>forwardRef</code></td><td>Native</td></tr>
  <tr><td>Lines of code</td><td>~50% less for typical components</td><td>More boilerplate</td></tr>
  <tr><td>Error boundaries</td><td>Not yet supported</td><td>Only way (must be class)</td></tr>
  <tr><td>Recommendation</td><td>Default for all new code</td><td>Legacy + error boundaries</td></tr>
</table>

<p><strong>Same component in both styles</strong>:</p>

<pre><code>// Functional with hooks
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() =&gt; {
    fetch(`/api/users/${userId}`).then(r =&gt; r.json()).then(setUser);
  }, [userId]);

  if (!user) return &lt;p&gt;Loading...&lt;/p&gt;;
  return &lt;h1&gt;{user.name}&lt;/h1&gt;;
}

// Class equivalent
import { Component } from "react";

class UserProfile extends Component {
  state = { user: null };

  componentDidMount() {
    this.loadUser();
  }
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) this.loadUser();
  }
  loadUser() {
    fetch(`/api/users/${this.props.userId}`)
      .then(r =&gt; r.json())
      .then(user =&gt; this.setState({ user }));
  }

  render() {
    if (!this.state.user) return &lt;p&gt;Loading...&lt;/p&gt;;
    return &lt;h1&gt;{this.state.user.name}&lt;/h1&gt;;
  }
}</code></pre>

<p><strong>Why hooks won</strong>:</p>
<ul>
  <li><strong>No <code>this</code> binding</strong> &mdash; class methods need <code>.bind</code> or arrow methods; hooks have closures.</li>
  <li><strong>Co-located logic</strong> &mdash; one effect = one concern. Classes scatter setup/teardown across <code>componentDidMount</code> / <code>componentWillUnmount</code>.</li>
  <li><strong>Custom hooks compose cleanly</strong> &mdash; reuse stateful logic by calling other hooks. HOCs and render props have wrapper-hell problems.</li>
  <li><strong>Better for tree-shaking</strong> &mdash; hooks are functions; classes always come with their methods.</li>
  <li><strong>Better TypeScript inference</strong>.</li>
  <li><strong>Smaller code</strong> &mdash; same component is ~30-50% shorter as a function.</li>
</ul>

<p><strong>The remaining class use case</strong>: <strong>error boundaries</strong>. As of React 19, the only way to catch errors during render is <code>componentDidCatch</code> + <code>getDerivedStateFromError</code> &mdash; class methods. The community wraps them in <code>react-error-boundary</code> so functional code stays untouched.</p>

<p><strong>For interview answers</strong>: lead with &ldquo;hooks are the standard&rdquo;, then explain class lifecycle equivalents to show you understand both. Don&rsquo;t recommend writing new class components except for error boundaries.</p>
'''

ANSWERS[50] = r'''
<p>Building a reusable component library means designing components that work outside any specific project, with clean APIs, predictable styling, full accessibility, and excellent developer experience. Major decisions: <strong>headless vs. styled</strong>, <strong>distribution mechanism</strong>, <strong>styling approach</strong>, <strong>typing</strong>, and <strong>versioning</strong>.</p>

<p><strong>Three architectural approaches</strong>:</p>

<table>
  <tr><th>Approach</th><th>Description</th><th>Examples</th></tr>
  <tr><td>Styled component library</td><td>Components ship with styles; consumers theme via tokens</td><td>Material UI, Chakra UI, Mantine</td></tr>
  <tr><td>Headless library</td><td>Components ship with logic + a11y, no styles; you bring CSS</td><td>Radix UI, Headless UI, React Aria</td></tr>
  <tr><td>Code-first / copy-in</td><td>You copy component source into your repo</td><td>shadcn/ui (the dominant 2026 pattern)</td></tr>
</table>

<p><strong>The shadcn/ui pattern (recommended for 2026 internal libraries)</strong>: components are copy-pasted into the consuming repo rather than installed as a package. Built on Radix UI primitives + Tailwind CSS. Consumers can edit any component freely; updates are pulled selectively.</p>

<pre><code>// Example: a Button component using class-variance-authority
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium " +
  "transition-colors focus-visible:outline-none focus-visible:ring-2 " +
  "disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:     "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-red-600 text-white hover:bg-red-700",
        outline:     "border border-input bg-background hover:bg-accent",
        ghost:       "hover:bg-accent",
        link:        "underline-offset-4 hover:underline text-primary"
      },
      size: { default: "h-10 px-4 py-2", sm: "h-9 px-3", lg: "h-11 px-8" }
    },
    defaultVariants: { variant: "default", size: "default" }
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes&lt;HTMLButtonElement&gt;,
          VariantProps&lt;typeof buttonVariants&gt; {}

export const Button = forwardRef&lt;HTMLButtonElement, ButtonProps&gt;(
  ({ className, variant, size, ...props }, ref) =&gt; (
    &lt;button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    /&gt;
  )
);
Button.displayName = "Button";</code></pre>

<p><strong>Six principles for production-quality components</strong>:</p>

<table>
  <tr><th>Principle</th><th>Why</th></tr>
  <tr><td>Forward refs</td><td>Consumers can imperatively control DOM node when needed</td></tr>
  <tr><td>Spread <code>...rest</code></td><td>Allow consumers to pass any HTML attribute, ARIA, data attributes</td></tr>
  <tr><td>Sensible defaults</td><td>Most calls should be <code>&lt;Button&gt;Click&lt;/Button&gt;</code> &mdash; nothing more</td></tr>
  <tr><td>Variants via composition</td><td>Use cva/clsx, not boolean prop explosion</td></tr>
  <tr><td>Strong TypeScript types</td><td>Auto-complete and inference for all variants</td></tr>
  <tr><td>Accessibility built in</td><td>Real <code>&lt;button&gt;</code> elements, ARIA, keyboard nav, focus rings</td></tr>
</table>

<p><strong>Distribution and versioning</strong>:</p>
<ul>
  <li><strong>npm package</strong> &mdash; classic; requires bundler (tsup, vite-plugin-dts).</li>
  <li><strong>Monorepo with Turborepo + Changesets</strong> &mdash; for multi-package libraries with semver.</li>
  <li><strong>Code-first / shadcn-style</strong> &mdash; ship a CLI that copies components into the consumer repo.</li>
  <li><strong>Storybook</strong> for visual documentation; required for adoption.</li>
  <li><strong>Strict semver</strong> &mdash; breaking changes require major bumps; never push breakage in patches.</li>
</ul>

<p>For startup teams in 2026: build on Radix UI primitives + Tailwind, copy from shadcn/ui as a starting point, document with Storybook, ship via internal npm or monorepo. Don&rsquo;t reinvent accessibility &mdash; Radix and React Aria handle the hard parts.</p>
'''

ANSWERS[51] = r'''
<p>Form management in React has evolved significantly &mdash; in 2026, best practices center on schema-validated, mostly uncontrolled forms with co-located validation, accessibility built in, and clear submission state.</p>

<p><strong>The recommended modern stack:</strong></p>

<table>
  <tr><th>Concern</th><th>Tool</th><th>Why</th></tr>
  <tr><td>Form state</td><td>React Hook Form</td><td>Uncontrolled by default; minimal re-renders; integrates with refs</td></tr>
  <tr><td>Validation schema</td><td>Zod</td><td>Type-safe, runs on server too, single source of truth</td></tr>
  <tr><td>Submission</td><td>Server Actions or async handler</td><td>React 19 useActionState aligns naturally; legacy supports custom handlers</td></tr>
  <tr><td>UI primitives</td><td>Radix / shadcn / React Aria</td><td>Accessibility, focus management, keyboard nav handled</td></tr>
</table>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Valid email required"),
  password: z.string().min(8, "Min 8 characters")
});
type FormData = z.infer&lt;typeof schema&gt;;

function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm&lt;FormData&gt;({ resolver: zodResolver(schema) });

  return (
    &lt;form onSubmit={handleSubmit(async (data) =&gt; { await login(data); })}&gt;
      &lt;label htmlFor="email"&gt;Email&lt;/label&gt;
      &lt;input id="email" {...register("email")} aria-invalid={!!errors.email} /&gt;
      {errors.email &amp;&amp; &lt;p role="alert"&gt;{errors.email.message}&lt;/p&gt;}

      &lt;button disabled={isSubmitting}&gt;
        {isSubmitting ? "Signing in..." : "Sign in"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Best practices checklist</strong>:</p>
<ul>
  <li><strong>Schema-driven validation</strong> &mdash; one Zod schema validates client and server.</li>
  <li><strong>Uncontrolled by default</strong> &mdash; React Hook Form uses refs; no re-render on every keystroke.</li>
  <li><strong>Validate on blur, re-validate on change after first error</strong> &mdash; users see errors only after interacting, but errors clear in real-time as they fix.</li>
  <li><strong>Disable submit during pending</strong> &mdash; prevents double submission.</li>
  <li><strong>Server errors map to fields</strong> &mdash; <code>setError("email", { message: "Already registered" })</code>.</li>
  <li><strong>Accessible markup</strong> &mdash; explicit <code>label htmlFor</code>, <code>aria-invalid</code>, <code>role="alert"</code> for errors, focus moves to first error on submit failure.</li>
  <li><strong>Avoid validation libraries that don&rsquo;t share with backend</strong> &mdash; Zod, Valibot, ArkType are full-stack-friendly.</li>
</ul>

<p><strong>For React 19 server-action forms</strong>, use the new <code>useActionState</code> + <code>useFormStatus</code> hooks &mdash; the form action signature receives FormData and returns the next state, eliminating boilerplate. RSC-driven apps (Next.js App Router, Remix v3) push this further with progressive enhancement: forms work without JS.</p>
'''

ANSWERS[52] = r'''
<p>Real-time data in React means UI updates as server state changes &mdash; without polling. Three primary mechanisms: <strong>WebSockets</strong> (bi-directional, full-duplex), <strong>Server-Sent Events</strong> (server → client only, simpler), and <strong>polling</strong> (last resort). Modern apps often abstract these via libraries.</p>

<p><strong>Native WebSocket pattern:</strong></p>

<pre><code>import { useEffect, useState, useRef } from "react";

function useWebSocket(url) {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("connecting");
  const wsRef = useRef(null);

  useEffect(() =&gt; {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen    = () =&gt; setStatus("open");
    ws.onclose   = () =&gt; setStatus("closed");
    ws.onerror   = () =&gt; setStatus("error");
    ws.onmessage = (e) =&gt; {
      const msg = JSON.parse(e.data);
      setMessages(prev =&gt; [...prev, msg]);
    };

    return () =&gt; ws.close();
  }, [url]);

  const send = (data) =&gt; wsRef.current?.send(JSON.stringify(data));

  return { messages, status, send };
}</code></pre>

<p><strong>Production WebSocket libraries</strong>: <strong>Socket.IO</strong> (auto-reconnect, fallbacks, rooms), <strong>Pusher</strong> / <strong>Ably</strong> (managed services with presence/channels), <strong>PartyKit</strong> (modern Cloudflare-based), <strong>Supabase Realtime</strong> (Postgres change streams). Each handles reconnection, message ordering, and backpressure that raw WebSockets don&rsquo;t.</p>

<p><strong>Real-time data approach comparison:</strong></p>

<table>
  <tr><th>Approach</th><th>Direction</th><th>Complexity</th><th>Use for</th></tr>
  <tr><td>Polling (interval)</td><td>Pull</td><td>Low</td><td>Infrequent updates, simple cases</td></tr>
  <tr><td>SSE (EventSource)</td><td>Server → client</td><td>Low-medium</td><td>Notifications, live tickers, AI streaming</td></tr>
  <tr><td>WebSocket</td><td>Bi-directional</td><td>Medium</td><td>Chat, live collaboration, multiplayer</td></tr>
  <tr><td>WebRTC data channel</td><td>Peer-to-peer</td><td>High</td><td>Latency-critical games, video calls</td></tr>
</table>

<p><strong>The TanStack Query approach</strong>: invalidate queries on socket events &mdash; the cache refetches automatically, keeping declarative data flow:</p>

<pre><code>const queryClient = useQueryClient();

useEffect(() =&gt; {
  socket.on("message:new", () =&gt; {
    queryClient.invalidateQueries({ queryKey: ["messages"] });
  });
}, []);</code></pre>

<p>This pattern keeps "what data exists" declarative (<code>useQuery</code>) while real-time signals only trigger refresh &mdash; you don&rsquo;t hand-merge socket payloads into local state. <strong>For collaborative editing</strong> (cursors, multi-user docs), consider <strong>Yjs</strong> or <strong>Automerge</strong> &mdash; CRDT-based libraries that handle conflict-free merging across clients.</p>
'''

ANSWERS[53] = r'''
<p>The most common React performance pitfalls aren&rsquo;t about React itself &mdash; they&rsquo;re patterns that cause unnecessary re-renders, work in the wrong place, or trigger expensive operations on every keystroke.</p>

<p><strong>The most damaging pitfalls and their fixes:</strong></p>

<table>
  <tr><th>Pitfall</th><th>Symptom</th><th>Fix</th></tr>
  <tr><td>Inline objects/arrays as props</td><td>Memoized children re-render constantly</td><td><code>useMemo</code> the value, or move outside component</td></tr>
  <tr><td>New function references every render</td><td>Same as above</td><td><code>useCallback</code> or React 19 Compiler</td></tr>
  <tr><td>Putting everything in a top-level Context</td><td>Whole tree re-renders on any change</td><td>Split into focused contexts, use Zustand/Jotai</td></tr>
  <tr><td>Big lists without virtualization</td><td>Scrolling lags; mount time slow</td><td>TanStack Virtual / react-window</td></tr>
  <tr><td>Synchronous expensive work in render</td><td>Slow first paint, dropped frames</td><td><code>useMemo</code>, web worker, defer with <code>useDeferredValue</code></td></tr>
  <tr><td>Index as <code>key</code> in dynamic lists</td><td>Wrong items reconcile, state mixes up</td><td>Stable IDs as keys</td></tr>
  <tr><td>State in too high a parent</td><td>Many siblings re-render unnecessarily</td><td>Push state down to where it&rsquo;s used</td></tr>
  <tr><td>Re-creating expensive selectors</td><td>Memoization defeated</td><td><code>createSelector</code> from reselect</td></tr>
  <tr><td>Loading entire libraries</td><td>Huge bundle</td><td>Tree-shake; dynamic imports for rare paths</td></tr>
  <tr><td>Missing cleanup in effects</td><td>Subscriptions leak; updates after unmount</td><td>Return cleanup function in <code>useEffect</code></td></tr>
</table>

<p><strong>The "inline objects" problem in detail:</strong></p>

<pre><code>// PROBLEM: new object every render → MemoChild always re-renders
function Parent({ user }) {
  return &lt;MemoChild config={{ theme: "dark", debug: true }} /&gt;;
}

// FIX: stable reference
function Parent({ user }) {
  const config = useMemo(() =&gt; ({ theme: "dark", debug: true }), []);
  return &lt;MemoChild config={config} /&gt;;
}</code></pre>

<p><strong>Diagnostic process</strong>: don&rsquo;t guess &mdash; <strong>profile</strong>. Open React DevTools Profiler, record an interaction, look for components rendering when they shouldn&rsquo;t. The flamegraph shows render times; click on any commit to see "why did this render" reasons. The <strong>react-scan</strong> tool (2024+) overlays render counts directly in the running app &mdash; instant visualization of waste.</p>

<p><strong>React 19&rsquo;s React Compiler</strong> auto-applies <code>useMemo</code>/<code>useCallback</code> where beneficial, eliminating most manual memoization. Once your codebase has the compiler enabled, several entries in this table become non-issues &mdash; the compiler stabilizes references automatically. Until then (or for cases the compiler can&rsquo;t verify), manual memoization remains necessary.</p>

<p>Don&rsquo;t over-optimize: most apps are fast by default. Reach for these techniques when profiling identifies a real problem, not preemptively.</p>
'''

ANSWERS[54] = r'''
<p>A custom data-fetching hook abstracts the common loading/error/data state machine into one reusable function. Roll-your-own teaches the pattern; production apps use <strong>TanStack Query</strong> or <strong>SWR</strong> for the same shape with caching, deduplication, and revalidation.</p>

<p><strong>Hand-rolled <code>useFetch</code>:</strong></p>

<pre><code>import { useState, useEffect, useCallback } from "react";

function useFetch&lt;T&gt;(url: string, options?: RequestInit) {
  const [data, setData] = useState&lt;T | null&gt;(null);
  const [error, setError] = useState&lt;Error | null&gt;(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(() =&gt; setRefreshKey(k =&gt; k + 1), []);

  useEffect(() =&gt; {
    if (!url) return;
    const ctrl = new AbortController();

    setLoading(true);
    setError(null);

    fetch(url, { ...options, signal: ctrl.signal })
      .then(r =&gt; {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch(e =&gt; e.name !== "AbortError" &amp;&amp; setError(e))
      .finally(() =&gt; setLoading(false));

    return () =&gt; ctrl.abort();
  }, [url, refreshKey]);

  return { data, error, loading, refresh };
}

// Usage
const { data, loading, error, refresh } = useFetch&lt;User[]&gt;("/api/users");</code></pre>

<p><strong>Limitations of hand-rolled</strong>: each component fetches independently (no cache sharing), no request deduplication (5 components hitting same URL fire 5 requests), no automatic refetch on focus/reconnect, no stale-while-revalidate semantics. These are the precise problems TanStack Query and SWR solve.</p>

<p><strong>The TanStack Query equivalent:</strong></p>

<pre><code>import { useQuery } from "@tanstack/react-query";

function useUsers() {
  return useQuery({
    queryKey: ["users"],
    queryFn: () =&gt; fetch("/api/users").then(r =&gt; r.json()),
    staleTime: 30_000   // data fresh for 30s; serve from cache, refetch in background after
  });
}

// Usage in any component — cache shared automatically
const { data, isLoading, error, refetch } = useUsers();</code></pre>

<p><strong>What you get for free</strong>: automatic caching by <code>queryKey</code>, deduplication (multiple components → one request), <code>staleTime</code> control, refetch on window focus, retry on error with exponential backoff, optimistic updates, infinite queries, mutation support with cache invalidation, devtools.</p>

<p><strong>When the custom hook still makes sense</strong>: simple internal apps with small data needs, learning React, when adding a dependency isn&rsquo;t worth it for two API calls. <strong>For production apps with more than ~5 endpoints</strong>, the library investment pays off many times over.</p>

<p><strong>For RSC / Suspense-based fetching</strong> (React 19+), the pattern shifts: components <code>use(promise)</code> and Suspense boundaries handle loading state &mdash; no hook needed. The shape of "data fetching in React" continues evolving as Server Components mature.</p>
'''

ANSWERS[55] = r'''
<p><code>useDebugValue</code> labels custom hooks in React DevTools, making them easier to identify when inspecting components. Library-grade hooks should add it; one-off hooks rarely need it.</p>

<p><strong>Without useDebugValue</strong>, custom hooks show up generically:</p>

<pre><code>// React DevTools displays:
//   1. Custom: { count: 5 }     ← which custom hook?
//   2. Custom: "online"          ← what does this mean?</code></pre>

<p><strong>With useDebugValue:</strong></p>

<pre><code>import { useState, useEffect, useDebugValue } from "react";

function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() =&gt; {
    const update = () =&gt; setIsOnline(navigator.onLine);
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () =&gt; {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  // Label this hook in DevTools
  useDebugValue(isOnline ? "Online" : "Offline");

  return isOnline;
}

// React DevTools now shows:
//   useOnlineStatus: "Online"</code></pre>

<p><strong>Format function for expensive labels:</strong></p>

<pre><code>function useDate(date) {
  // The format function only runs when DevTools inspects this hook
  useDebugValue(date, (d) =&gt; d.toLocaleDateString());
  return formatDate(date);
}</code></pre>

<p>The second argument is a formatter function &mdash; deferred until DevTools actually reads the value. Useful when formatting is expensive (e.g., date formatting, JSON stringification of complex objects).</p>

<p><strong>When to use it:</strong></p>

<table>
  <tr><th>Use it</th><th>Don&rsquo;t bother</th></tr>
  <tr><td>Library-distributed hooks (npm packages)</td><td>One-off hooks used only in this app</td></tr>
  <tr><td>Hooks with non-obvious internal state</td><td>Hooks that simply wrap useState</td></tr>
  <tr><td>Hooks where state interpretation needs context</td><td>Trivial hooks where the return value is self-explanatory</td></tr>
  <tr><td>Hooks with multiple internal hooks</td><td>Single-line wrappers around built-in hooks</td></tr>
</table>

<p><strong>Common in published libraries</strong>: TanStack Query labels each query with its key + status; React Hook Form labels form state; Zustand labels store slices. As a hook author publishing to npm, <code>useDebugValue</code> dramatically improves the DX of consumers debugging their apps.</p>

<p><strong>Production impact</strong>: zero. <code>useDebugValue</code> is a no-op in production builds &mdash; only DevTools in development reads the labels. Don&rsquo;t worry about performance.</p>

<p>This hook is one of React&rsquo;s underused features &mdash; many engineers don&rsquo;t know it exists. For interview answers: knowing it exists and when to use it (libraries, not apps) signals depth.</p>
'''

ANSWERS[56] = r'''
<p>File uploads in production-grade React apps require: progress tracking, drag-and-drop UX, multiple file support, client-side validation (size, type), chunked uploads for large files, and resilience to network failures. Native <code>fetch</code> doesn&rsquo;t support upload progress; <code>axios</code> or <code>XMLHttpRequest</code> do.</p>

<p><strong>Production patterns:</strong></p>

<table>
  <tr><th>Need</th><th>Approach</th></tr>
  <tr><td>Progress bar</td><td>axios <code>onUploadProgress</code> or XHR <code>upload.onprogress</code></td></tr>
  <tr><td>Drag-and-drop</td><td><code>react-dropzone</code> library or native HTML5 drag events</td></tr>
  <tr><td>Multiple files</td><td><code>multiple</code> attribute + <code>FileList</code> iteration</td></tr>
  <tr><td>Large file resilience</td><td>Chunked upload (S3 multipart, tus protocol, Cloudinary, Uploadcare)</td></tr>
  <tr><td>Image preprocessing</td><td><code>browser-image-compression</code> or canvas resize before upload</td></tr>
  <tr><td>Direct-to-S3 / CDN</td><td>Backend signs upload URL; client uploads directly to storage</td></tr>
</table>

<p><strong>Direct-to-storage upload (the production approach for large files):</strong></p>

<pre><code>// 1. Get a pre-signed URL from your backend (signs S3/Cloudinary)
const { uploadUrl, fileKey } = await fetch("/api/sign-upload", {
  method: "POST",
  body: JSON.stringify({ fileName: file.name, fileType: file.type })
}).then(r =&gt; r.json());

// 2. Upload directly to storage (skips your backend)
await axios.put(uploadUrl, file, {
  headers: { "Content-Type": file.type },
  onUploadProgress: (e) =&gt; {
    setProgress(Math.round((e.loaded / e.total) * 100));
  }
});

// 3. Notify backend the upload completed; backend records the fileKey
await fetch("/api/files/confirm", {
  method: "POST",
  body: JSON.stringify({ fileKey })
});</code></pre>

<p><strong>Why direct upload</strong>: routing 100MB through your API server consumes bandwidth, memory, and forks of your processes &mdash; crippling at scale. Direct upload lets the client stream straight to S3/Cloudinary while your API stays free to handle other requests.</p>

<p><strong>Resumable uploads with tus protocol:</strong></p>

<pre><code>import { Upload } from "tus-js-client";

const upload = new Upload(file, {
  endpoint: "/files",
  retryDelays: [0, 3000, 5000, 10000],
  metadata: { filename: file.name, filetype: file.type },
  onProgress: (sent, total) =&gt; setProgress((sent / total) * 100),
  onSuccess: () =&gt; console.log("Done")
});

upload.start();</code></pre>

<p>tus uploads in chunks; if connection drops, resumes from where it left off. Critical for video uploads, mobile networks, large datasets &mdash; without it, a 90% complete upload that fails is 90% of the bytes wasted.</p>

<p><strong>Validation matters</strong>: validate type (MIME + extension), size, and dimensions before uploading. Show user-friendly errors. Server must always re-validate &mdash; client validation is UX only, not security.</p>

<p><strong>For complete upload UI</strong>: <strong>Uppy</strong> (full-featured, multi-source: webcam, URL, Dropbox, Google Drive) or <strong>react-dropzone</strong> (just the drag-drop primitives, you build the UI). Both production-tested.</p>
'''

ANSWERS[57] = r'''
<p>"Lifting state up" is the React pattern for sharing state between sibling components: move the state to their nearest common ancestor and pass it down via props. It&rsquo;s the simplest form of state sharing &mdash; before reaching for Context or Redux, lift first.</p>

<p><strong>The problem &mdash; state in a leaf component:</strong></p>

<pre><code>// PROBLEM: TemperatureInput owns the temperature; BoilingVerdict can&rsquo;t see it

function App() {
  return (
    &lt;&gt;
      &lt;TemperatureInput /&gt;       {/* owns temperature state */}
      &lt;BoilingVerdict /&gt;          {/* needs the temperature; doesn&rsquo;t have access */}
    &lt;/&gt;
  );
}</code></pre>

<p><strong>The solution &mdash; lift state to common parent:</strong></p>

<pre><code>function App() {
  const [temperature, setTemperature] = useState(0);

  return (
    &lt;&gt;
      &lt;TemperatureInput value={temperature} onChange={setTemperature} /&gt;
      &lt;BoilingVerdict celsius={temperature} /&gt;
    &lt;/&gt;
  );
}

function TemperatureInput({ value, onChange }) {
  return (
    &lt;input
      type="number"
      value={value}
      onChange={e =&gt; onChange(Number(e.target.value))}
    /&gt;
  );
}

function BoilingVerdict({ celsius }) {
  return &lt;p&gt;{celsius &gt;= 100 ? "Boiling!" : "Not boiling"}&lt;/p&gt;;
}</code></pre>

<p>Now the parent owns the data; both children read from props. The parent is the "single source of truth" for that state.</p>

<p><strong>When to lift state up</strong>:</p>
<ul>
  <li>Two siblings need to display or modify the same state.</li>
  <li>One component derives information from another&rsquo;s state.</li>
  <li>Components need to stay in sync (e.g., two converters, master/detail views).</li>
</ul>

<p><strong>How far to lift &mdash; the rule</strong>: lift to the lowest common ancestor that needs the state. Lifting too high causes unnecessary re-renders in components that don&rsquo;t care; lifting too low means you can&rsquo;t share.</p>

<p><strong>The tradeoff &mdash; prop drilling</strong>: lifted state must pass through intermediate components as props, even if those intermediates don&rsquo;t use the state. This is "prop drilling" (Q35). When prop drilling becomes painful (3+ levels), reach for:</p>

<table>
  <tr><th>Pain level</th><th>Solution</th></tr>
  <tr><td>1-2 levels of prop passing</td><td>Live with it &mdash; explicit data flow is good</td></tr>
  <tr><td>3+ levels, occasional</td><td>Component composition (children as props)</td></tr>
  <tr><td>3+ levels, multiple branches</td><td>Context API for theme/auth/user</td></tr>
  <tr><td>Cross-cutting state, many components</td><td>Zustand / Jotai / Redux Toolkit</td></tr>
</table>

<p><strong>Composition can replace lifting</strong>: instead of <code>&lt;Layout sidebar={...} content={...} /&gt;</code>, use <code>&lt;Layout&gt;&lt;Sidebar /&gt;&lt;Content /&gt;&lt;/Layout&gt;</code> &mdash; children are passed in already-rendered, no prop forwarding needed. This is one of React&rsquo;s most underused techniques for keeping data flow simple.</p>

<p>Lifting state up is the foundational pattern; everything else (Context, Redux, Zustand) is an optimization for specific cases where lifting becomes unwieldy.</p>
'''

ANSWERS[58] = r'''
<p>Context-based theming centralizes theme state (light/dark/custom) in a Context provider, exposes it via a custom hook, and drives styling through CSS variables or library-specific theme objects. The pattern works for any React app regardless of styling approach.</p>

<p><strong>The complete pattern with persistence and system preference:</strong></p>

<pre><code>import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";
const ThemeContext = createContext&lt;{
  theme: Theme;
  setTheme: (t: Theme) =&gt; void;
  resolved: "light" | "dark";   // actual applied theme
} | null&gt;(null);

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState&lt;Theme&gt;(() =&gt; {
    return (localStorage.getItem("theme") as Theme) || "system";
  });

  // Resolve "system" to actual light/dark
  const [resolved, setResolved] = useState&lt;"light" | "dark"&gt;(() =&gt;
    theme === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
      : theme
  );

  // Watch for OS theme changes when in "system" mode
  useEffect(() =&gt; {
    if (theme !== "system") {
      setResolved(theme);
      return;
    }
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const update = () =&gt; setResolved(mq.matches ? "dark" : "light");
    update();
    mq.addEventListener("change", update);
    return () =&gt; mq.removeEventListener("change", update);
  }, [theme]);

  // Apply to document
  useEffect(() =&gt; {
    document.documentElement.dataset.theme = resolved;
  }, [resolved]);

  const setTheme = (t: Theme) =&gt; {
    setThemeState(t);
    localStorage.setItem("theme", t);
  };

  return (
    &lt;ThemeContext.Provider value={{ theme, setTheme, resolved }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

export const useTheme = () =&gt; {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
};</code></pre>

<p><strong>CSS using the data attribute:</strong></p>

<pre><code>:root {
  --bg: white;
  --text: #111;
  --primary: #007bff;
}

[data-theme="dark"] {
  --bg: #0a0a0a;
  --text: #f0f0f0;
  --primary: #4dabf7;
}

body { background: var(--bg); color: var(--text); }</code></pre>

<p><strong>Three details that matter</strong>:</p>

<table>
  <tr><th>Detail</th><th>Why</th></tr>
  <tr><td>Three-state (light/dark/system) not just toggle</td><td>"System" is what most users expect; respects OS preference</td></tr>
  <tr><td>Listen to <code>matchMedia</code> change event</td><td>OS theme changes mid-session; UI must follow</td></tr>
  <tr><td>Apply to <code>&lt;html&gt;</code> not <code>&lt;body&gt;</code></td><td>Affects scrollbar, native form colors, etc.</td></tr>
  <tr><td>Inline script before hydration</td><td>Prevents "flash of wrong theme" on initial load</td></tr>
</table>

<p><strong>Avoiding flash on initial load</strong>: include this small script in <code>&lt;head&gt;</code> before React hydrates:</p>

<pre><code>&lt;script&gt;
  (function () {
    const stored = localStorage.getItem("theme");
    const dark = stored === "dark" ||
      (stored !== "light" &amp;&amp; matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  })();
&lt;/script&gt;</code></pre>

<p><strong>For Tailwind CSS</strong>, configure <code>darkMode: ["class", '[data-theme="dark"]']</code> &mdash; Tailwind&rsquo;s <code>dark:</code> utilities then trigger off your data attribute. <strong>For component libraries</strong> (Material UI, Chakra), wrap in their ThemeProvider with values driven by your context. <strong>shadcn/ui</strong> uses CSS variables natively, so this pattern works directly with no integration.</p>
'''

ANSWERS[59] = r'''
<p>Redux and Context API solve different problems despite both providing "share state across components." Choosing between them &mdash; and knowing when to use neither &mdash; is a common architectural decision.</p>

<p><strong>The fundamental difference</strong>: Context is a <strong>delivery mechanism</strong> for values down the tree (avoiding prop drilling); Redux is a <strong>state management library</strong> with predictable update patterns, dev tools, and middleware. They aren&rsquo;t direct competitors &mdash; many apps use both.</p>

<table>
  <tr><th></th><th>Context API</th><th>Redux Toolkit</th></tr>
  <tr><td>Purpose</td><td>Pass values without prop drilling</td><td>Centralized state with predictable updates</td></tr>
  <tr><td>Bundle size</td><td>Built-in (0 KB)</td><td>~12 KB (RTK)</td></tr>
  <tr><td>Update mechanism</td><td>Re-renders all consumers on any value change</td><td>Selectors with shallow equality skip unaffected components</td></tr>
  <tr><td>Devtools</td><td>None native (React DevTools shows current value)</td><td>Time-travel, action log, state diff</td></tr>
  <tr><td>Middleware</td><td>None</td><td>Thunks, logging, persistence, RTK Query</td></tr>
  <tr><td>Async support</td><td>Manual (you wire it up)</td><td><code>createAsyncThunk</code> + RTK Query</td></tr>
  <tr><td>Setup boilerplate</td><td>Minimal</td><td>Slice + store + provider (one-time)</td></tr>
  <tr><td>Best for</td><td>Theme, auth, locale, low-frequency data</td><td>Complex domain state, many actions, undo/redo</td></tr>
</table>

<p><strong>The Context performance pitfall</strong>: every component that calls <code>useContext</code> re-renders when the context value changes. With one giant context holding everything, any update re-renders the whole subscriber list. Mitigations:</p>

<ul>
  <li><strong>Split contexts</strong> by concern &mdash; ThemeContext, AuthContext, NotificationContext separately.</li>
  <li><strong>Memoize the value</strong> &mdash; <code>useMemo(() =&gt; ({ ... }), [deps])</code> on the provider value.</li>
  <li><strong>Use selectors</strong> via <code>use-context-selector</code> library &mdash; component subscribes to specific fields only.</li>
</ul>

<p><strong>Redux&rsquo;s built-in solution</strong>: components select specific slices via <code>useSelector(state =&gt; state.user.name)</code>; React-Redux only re-renders when the selected value changes. No splitting required &mdash; the architecture handles granularity for you.</p>

<p><strong>The 2026 reality check</strong>: most new apps don&rsquo;t need Redux. The state landscape has split:</p>

<table>
  <tr><th>State type</th><th>Recommended tool</th></tr>
  <tr><td>Server data (API responses)</td><td>TanStack Query / SWR / RTK Query</td></tr>
  <tr><td>UI state (modals, forms, selections)</td><td>useState, useReducer</td></tr>
  <tr><td>Theme, auth, locale</td><td>Context API</td></tr>
  <tr><td>Cross-cutting client state</td><td>Zustand / Jotai (lightweight, simple API)</td></tr>
  <tr><td>Complex domain state with action history</td><td>Redux Toolkit</td></tr>
</table>

<p><strong>Decision flow</strong>: is the data from a server? → use TanStack Query (don&rsquo;t put server data in Redux/Context). Is it UI state local to one component? → useState. Is it shared across siblings? → lift state up. Does it cross many levels of the tree? → Context. Do you need action history, time-travel, complex middleware, or 50+ types of state changes? → Redux Toolkit.</p>

<p>Most apps in 2026 land at: TanStack Query + useState + Context (theme, auth) + Zustand (occasional cross-tree state). Redux remains common in established codebases and apps with genuine action-history needs.</p>
'''

ANSWERS[60] = r'''
<p>Accessibility (a11y) in React isn&rsquo;t about React-specific APIs &mdash; it&rsquo;s about generating semantically correct HTML, providing keyboard equivalents to mouse interactions, and respecting assistive technology conventions. React makes a11y harder than vanilla HTML in some ways (custom components hide native behavior) and easier in others (consistent patterns).</p>

<p><strong>The accessibility checklist for React apps:</strong></p>

<table>
  <tr><th>Concern</th><th>What to do</th></tr>
  <tr><td>Semantic HTML</td><td>Use <code>&lt;button&gt;</code>, <code>&lt;nav&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;article&gt;</code> &mdash; not <code>&lt;div onClick&gt;</code></td></tr>
  <tr><td>Form labels</td><td>Every input has a <code>&lt;label htmlFor&gt;</code> or <code>aria-label</code></td></tr>
  <tr><td>Keyboard navigation</td><td>All interactive elements reachable + operable via keyboard</td></tr>
  <tr><td>Focus management</td><td>Modal traps focus; close returns focus to trigger</td></tr>
  <tr><td>ARIA roles</td><td>Custom widgets need correct role + state attributes</td></tr>
  <tr><td>Color contrast</td><td>WCAG AA: 4.5:1 for normal text, 3:1 for large text</td></tr>
  <tr><td>Reduced motion</td><td>Respect <code>prefers-reduced-motion</code></td></tr>
  <tr><td>Screen reader announcements</td><td>Use <code>aria-live</code> for dynamic updates</td></tr>
  <tr><td>Skip links</td><td>"Skip to main content" link for keyboard users</td></tr>
</table>

<p><strong>The most common React-specific bug</strong>: <code>div onClick</code> instead of <code>button onClick</code>:</p>

<pre><code>// WRONG: not focusable, not announced as button, no Enter/Space activation
&lt;div onClick={handleClick}&gt;Click me&lt;/div&gt;

// RIGHT: keyboard accessible by default, announced correctly
&lt;button onClick={handleClick}&gt;Click me&lt;/button&gt;

// If you must use a div, simulate the button:
&lt;div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) =&gt; (e.key === "Enter" || e.key === " ") &amp;&amp; handleClick()}
&gt;
  Click me
&lt;/div&gt;</code></pre>

<p><strong>Focus management for modals:</strong></p>

<pre><code>function Modal({ isOpen, onClose, children }) {
  const triggerRef = useRef(null);
  const dialogRef  = useRef(null);

  useEffect(() =&gt; {
    if (!isOpen) return;
    triggerRef.current = document.activeElement;     // remember opener
    dialogRef.current?.focus();                      // focus dialog

    return () =&gt; {
      triggerRef.current?.focus();                    // restore on close
    };
  }, [isOpen]);
  // ...
}</code></pre>

<p><strong>Tools and libraries</strong>:</p>

<ul>
  <li><strong>eslint-plugin-jsx-a11y</strong> &mdash; lints JSX for common a11y mistakes; should be enabled by default.</li>
  <li><strong>axe-core</strong> &mdash; runtime accessibility scanner; <code>@axe-core/react</code> integrates with dev mode.</li>
  <li><strong>Radix UI / React Aria</strong> &mdash; headless components with full a11y baked in (focus management, ARIA, keyboard).</li>
  <li><strong>WAVE / Lighthouse</strong> &mdash; in-browser audits.</li>
  <li><strong>NVDA / VoiceOver / JAWS</strong> &mdash; screen readers. Test with at least one regularly.</li>
</ul>

<p><strong>Why use a headless library</strong>: building a fully accessible combobox, dialog, or menu by hand is dozens of hours of work to get right (focus traps, ARIA states, keyboard navigation specs from WAI-ARIA Authoring Practices). Radix or React Aria gives you 95% correctness for free.</p>

<p><strong>For dynamic announcements</strong>:</p>

<pre><code>// "X items added to cart" should announce to screen readers
&lt;div aria-live="polite" aria-atomic="true"&gt;
  {cartCount} items in cart
&lt;/div&gt;</code></pre>

<p><code>aria-live="polite"</code> announces after current speech finishes; <code>"assertive"</code> interrupts (use sparingly &mdash; for errors, alerts).</p>

<p>A11y isn&rsquo;t optional &mdash; it&rsquo;s legally required in many jurisdictions (ADA, EU Accessibility Act 2025), and good a11y improves UX for everyone (clean keyboard nav, clear labels, logical tab order benefit power users too).</p>
'''

ANSWERS[61] = r'''
<p><strong>Immer</strong> is a library that lets you write state updates as if mutating, while producing immutable updates under the hood. Redux Toolkit (RTK) bakes Immer into <code>createSlice</code> by default, eliminating most of the spread-operator gymnastics of classic Redux.</p>

<p><strong>Without Immer (classic Redux):</strong></p>

<pre><code>case "TODO_TOGGLED":
  return {
    ...state,
    todos: {
      ...state.todos,
      [action.id]: {
        ...state.todos[action.id],
        completed: !state.todos[action.id].completed
      }
    }
  };</code></pre>

<p><strong>With Immer (Redux Toolkit):</strong></p>

<pre><code>todoToggled(state, action) {
  state.todos[action.payload].completed = !state.todos[action.payload].completed;
}</code></pre>

<p>Both produce identical immutable state &mdash; Immer creates a draft proxy of the state, lets you mutate it, then computes a new immutable result by tracking which paths changed.</p>

<p><strong>Benefits of Immer with Redux:</strong></p>

<table>
  <tr><th>Benefit</th><th>Why it matters</th></tr>
  <tr><td>Less boilerplate</td><td>Code reads naturally; less spread chaining; fewer bugs</td></tr>
  <tr><td>Structural sharing</td><td>Unchanged parts share references; cheap to compare</td></tr>
  <tr><td>Type-safe mutations</td><td>TypeScript validates against the draft type</td></tr>
  <tr><td>Composability</td><td>Helper functions accepting drafts compose naturally</td></tr>
  <tr><td>Plays well with deeply nested state</td><td>Updating <code>state.users[id].profile.address.city</code> is one line</td></tr>
</table>

<p><strong>How Immer works (the magic)</strong>:</p>

<ol>
  <li>You hand Immer the current state and a function (the recipe).</li>
  <li>Immer creates a draft &mdash; a proxy that records mutations without changing the original.</li>
  <li>Your function mutates the draft naturally.</li>
  <li>Immer applies all recorded mutations to produce a new immutable state, with structural sharing (unchanged branches keep the same references).</li>
</ol>

<pre><code>import produce from "immer";

const next = produce(current, (draft) =&gt; {
  draft.users.push({ id: 3, name: "New" });
  draft.lastUpdated = Date.now();
});

// `current` unchanged; `next` is new immutable state</code></pre>

<p><strong>Important caveats:</strong></p>

<ul>
  <li><strong>Either mutate the draft, OR return a new value</strong> &mdash; not both.</li>
  <li><strong>Replacing the entire state</strong>: <code>return action.payload</code> works.</li>
  <li><strong>Don&rsquo;t mix</strong>: <code>state.x = 5; return { y: 1 }</code> throws.</li>
  <li><strong>Class instances aren&rsquo;t auto-frozen</strong>: Maps and Sets need <code>enableMapSet()</code> from immer.</li>
</ul>

<p><strong>Performance</strong>: Immer is fast enough for almost all use cases. The proxy overhead is small compared to network/render costs. If you have a hot loop processing 100,000 items, profile &mdash; in extreme cases, hand-written immutable code can be faster, but this is rarely the bottleneck.</p>

<p><strong>Beyond Redux</strong>: Immer is useful anywhere you need immutable updates &mdash; <code>useImmerReducer</code> for component-level reducers, Zustand has Immer middleware, even <code>setState</code> can use it via <code>useImmer</code>. <strong>For React 19 with the React Compiler</strong>, Immer&rsquo;s value persists &mdash; the compiler optimizes referential equality, but Immer makes the code itself cleaner.</p>
'''

ANSWERS[62] = r'''
<p>Responsive design in React is done primarily through CSS &mdash; not JavaScript. The browser is far more efficient at responding to viewport changes than re-rendering React components on every resize. JavaScript-based responsiveness (<code>useMediaQuery</code> hooks) is a last resort for cases where layout truly depends on render-time logic.</p>

<p><strong>The CSS-first toolkit:</strong></p>

<table>
  <tr><th>Technique</th><th>Best for</th></tr>
  <tr><td>Media queries</td><td>Layout switches at viewport breakpoints</td></tr>
  <tr><td>Container queries</td><td>Component responsive to its container, not viewport</td></tr>
  <tr><td>CSS Grid <code>auto-fit</code> + <code>minmax</code></td><td>Self-sizing column counts without breakpoints</td></tr>
  <tr><td>Flexbox</td><td>Flowing items that wrap naturally</td></tr>
  <tr><td>Viewport units (<code>dvh</code>, <code>svh</code>, <code>lvh</code>)</td><td>Mobile-safe full-height layouts</td></tr>
  <tr><td><code>clamp()</code></td><td>Fluid typography between min and max</td></tr>
  <tr><td><code>aspect-ratio</code></td><td>Image/video containers without padding hack</td></tr>
</table>

<p><strong>Container queries (the 2024+ game-changer):</strong></p>

<pre><code>.card-container {
  container-type: inline-size;
}

/* Card adapts to its container width, regardless of viewport */
@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 100px 1fr; gap: 16px; }
}</code></pre>

<p>Same component looks different in a wide vs narrow container &mdash; useful when the same component appears in main content (wide) and a sidebar (narrow). Media queries can&rsquo;t do this.</p>

<p><strong>When JavaScript is necessary &mdash; <code>useMediaQuery</code> hook:</strong></p>

<pre><code>function useMediaQuery(query) {
  const [matches, setMatches] = useState(() =&gt; window.matchMedia(query).matches);

  useEffect(() =&gt; {
    const mq = window.matchMedia(query);
    const handler = (e) =&gt; setMatches(e.matches);
    mq.addEventListener("change", handler);
    return () =&gt; mq.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

// Usage: render different components, not just style
function Nav() {
  const isMobile = useMediaQuery("(max-width: 768px)");
  return isMobile ? &lt;MobileMenu /&gt; : &lt;DesktopMenu /&gt;;
}</code></pre>

<p><strong>When JS-based responsiveness is correct</strong>: rendering different components, lazy-loading desktop-only features, conditional fetching of mobile-vs-desktop data. <strong>When it&rsquo;s wrong</strong>: simply changing CSS &mdash; do that in CSS.</p>

<p><strong>Mobile-first approach:</strong></p>

<pre><code>/* Default: mobile */
.grid { display: block; }

/* Tablet+ */
@media (min-width: 640px) {
  .grid { display: grid; grid-template-columns: 1fr 1fr; }
}

/* Desktop+ */
@media (min-width: 1024px) {
  .grid { grid-template-columns: 1fr 1fr 1fr; }
}</code></pre>

<p>Start mobile; add complexity at larger sizes. Mobile users get less CSS to parse; layouts cascade naturally up.</p>

<p><strong>For Tailwind CSS</strong>, the mobile-first prefix system maps directly: <code>className="block sm:grid sm:grid-cols-2 lg:grid-cols-3"</code>. <strong>For SSR</strong>, JS-based responsive components have a hydration mismatch problem &mdash; server doesn&rsquo;t know the viewport. Solutions: render mobile by default, hydrate to detected size; or use cookies/headers to detect on server.</p>

<p><strong>Don&rsquo;t use <code>window.innerWidth</code> in render</strong> &mdash; it doesn&rsquo;t trigger re-renders, breaks SSR. Always go through <code>matchMedia</code> + listener.</p>

<p>Modern responsive design is mostly CSS; React enters when you need to load different components or fundamentally restructure UI based on size. Default to CSS &mdash; it&rsquo;s faster and simpler.</p>
'''

ANSWERS[63] = r'''
<p>Error boundaries are React components that catch JavaScript errors in their child component tree, log them, and display a fallback UI instead of crashing the entire app. They&rsquo;re React&rsquo;s closest equivalent to a try/catch for the rendering lifecycle.</p>

<p><strong>What they catch:</strong></p>

<table>
  <tr><th>Caught</th><th>NOT caught</th></tr>
  <tr><td>Errors during render</td><td>Errors in event handlers (use try/catch)</td></tr>
  <tr><td>Errors in lifecycle methods</td><td>Asynchronous code (use try/catch in async)</td></tr>
  <tr><td>Errors in constructors of children</td><td>Server-side rendering errors (handle separately)</td></tr>
  <tr><td></td><td>Errors in the boundary component itself (need a parent boundary)</td></tr>
</table>

<p><strong>Implementation (still requires class component as of React 19):</strong></p>

<pre><code>import { Component } from "react";

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    Sentry.captureException(error, { contexts: { react: errorInfo } });
  }

  reset = () =&gt; this.setState({ hasError: false, error: null });

  render() {
    if (this.state.hasError) {
      return this.props.fallback?.(this.state.error, this.reset) || (
        &lt;div role="alert"&gt;
          &lt;h2&gt;Something went wrong&lt;/h2&gt;
          &lt;p&gt;{this.state.error?.message}&lt;/p&gt;
          &lt;button onClick={this.reset}&gt;Try again&lt;/button&gt;
        &lt;/div&gt;
      );
    }
    return this.props.children;
  }
}</code></pre>

<p><strong>The recommended library &mdash; <code>react-error-boundary</code>:</strong></p>

<pre><code>import { ErrorBoundary } from "react-error-boundary";

function Fallback({ error, resetErrorBoundary }) {
  return (
    &lt;div role="alert"&gt;
      &lt;p&gt;Something went wrong:&lt;/p&gt;
      &lt;pre&gt;{error.message}&lt;/pre&gt;
      &lt;button onClick={resetErrorBoundary}&gt;Try again&lt;/button&gt;
    &lt;/div&gt;
  );
}

&lt;ErrorBoundary
  FallbackComponent={Fallback}
  onError={(error, info) =&gt; logToService(error, info)}
  onReset={() =&gt; { /* clear bad state */ }}
&gt;
  &lt;Dashboard /&gt;
&lt;/ErrorBoundary&gt;</code></pre>

<p><strong>Strategic placement &mdash; multiple layers:</strong></p>

<pre><code>&lt;ErrorBoundary fallback={&lt;FullPageError /&gt;}&gt;       {/* outermost: catches everything */}
  &lt;Header /&gt;

  &lt;ErrorBoundary fallback={&lt;FeatureError /&gt;}&gt;     {/* feature-level: isolates */}
    &lt;Dashboard /&gt;
  &lt;/ErrorBoundary&gt;

  &lt;ErrorBoundary fallback={&lt;WidgetError /&gt;}&gt;      {/* widget-level: localized */}
    &lt;ThirdPartyWidget /&gt;
  &lt;/ErrorBoundary&gt;
&lt;/ErrorBoundary&gt;</code></pre>

<p>If the third-party widget crashes, only the widget shows an error &mdash; the rest of the app keeps working. Without nested boundaries, one bad component takes down everything.</p>

<p><strong>Combining with React Query</strong>: TanStack Query throws errors that error boundaries catch when <code>throwOnError: true</code>. Lets you handle data-fetching errors and render errors uniformly.</p>

<p><strong>Limitations &mdash; what you still need to handle yourself:</strong></p>
<ul>
  <li><strong>Event handlers</strong>: <code>try/catch</code> inside the handler.</li>
  <li><strong>Promises</strong>: <code>.catch(setError)</code> and render the error from state.</li>
  <li><strong>Async useEffect</strong>: catch errors and update state.</li>
  <li><strong>Server-side rendering</strong>: framework-specific (Next.js has <code>error.tsx</code> at the route level).</li>
</ul>

<p><strong>Future</strong>: React team has discussed a hook-based error boundary API for years; as of React 19, class components are still required. The <code>react-error-boundary</code> library is the de-facto standard until that ships.</p>

<p>Production app pattern: top-level boundary for catastrophic errors (logs + "refresh page" message), feature boundaries around major sections (logs + retry), and widget boundaries around third-party or risky components (silently degrade).</p>
'''

ANSWERS[64] = r'''
<p>Bundle size affects time-to-interactive on first load &mdash; especially on mobile networks. The optimization goal: ship the smallest JS needed for the initial view, defer the rest. Modern bundlers (Vite/Rollup, esbuild, Turbopack) automate most of this; the developer&rsquo;s job is enabling the right patterns.</p>

<p><strong>The bundle optimization toolkit:</strong></p>

<table>
  <tr><th>Technique</th><th>Impact</th><th>Cost</th></tr>
  <tr><td>Code splitting at routes</td><td>Big &mdash; only load current page&rsquo;s JS</td><td>Low &mdash; <code>React.lazy(() =&gt; import(...))</code></td></tr>
  <tr><td>Code splitting at components</td><td>Medium &mdash; lazy-load modals, charts</td><td>Low</td></tr>
  <tr><td>Tree shaking</td><td>Big with proper imports</td><td>Free if libs export correctly</td></tr>
  <tr><td>Replacing heavy deps</td><td>Big &mdash; moment.js (290KB) → date-fns (modular) or Temporal API</td><td>Migration time</td></tr>
  <tr><td>Modern build targets</td><td>Smaller polyfills/transpilation</td><td>Drop IE11; modern browsers only</td></tr>
  <tr><td>Compression (Brotli)</td><td>~25% smaller than gzip</td><td>Server config</td></tr>
  <tr><td>Image optimization</td><td>Often bigger win than JS</td><td>Use Next.js Image, Cloudinary, or imgproxy</td></tr>
  <tr><td>React Server Components</td><td>Can eliminate components from client bundle</td><td>Requires Next.js / Remix architecture</td></tr>
</table>

<p><strong>Route-based splitting:</strong></p>

<pre><code>const Dashboard = lazy(() =&gt; import("./pages/Dashboard"));
const Settings  = lazy(() =&gt; import("./pages/Settings"));

&lt;Suspense fallback={&lt;Loader /&gt;}&gt;
  &lt;Routes&gt;
    &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
    &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
    &lt;Route path="/settings"  element={&lt;Settings /&gt;} /&gt;
  &lt;/Routes&gt;
&lt;/Suspense&gt;</code></pre>

<p>Vite/Webpack splits each lazy import into a separate chunk. Users hitting <code>/</code> never download Dashboard or Settings code.</p>

<p><strong>Tree shaking gotchas:</strong></p>

<pre><code>// BAD — pulls entire lodash (~70KB)
import _ from "lodash";
_.debounce(fn, 300);

// GOOD — only imports debounce (~2KB)
import { debounce } from "lodash-es";    // ESM build
debounce(fn, 300);

// EVEN BETTER — single function
import debounce from "lodash.debounce";</code></pre>

<p>Tree shaking only works on ESM imports; CommonJS (<code>require</code>) imports the whole module. Library authors should ship <code>main</code> + <code>module</code> + <code>exports</code> fields in package.json with proper ESM.</p>

<p><strong>Diagnose with bundle analyzers:</strong></p>

<pre><code># Vite
npm run build -- --report
# Or: npx vite-bundle-visualizer

# Webpack
npm install --save-dev webpack-bundle-analyzer
# Then in webpack.config.js: new BundleAnalyzerPlugin()

# Next.js
ANALYZE=true npm run build</code></pre>

<p>Look for: large unexpected dependencies, duplicate libraries (different versions of React loaded), polyfills you don&rsquo;t need.</p>

<p><strong>Common culprits and replacements:</strong></p>

<table>
  <tr><th>Heavy</th><th>Lighter alternative</th></tr>
  <tr><td>moment.js (290KB)</td><td>date-fns (modular), dayjs (~7KB), Temporal API</td></tr>
  <tr><td>lodash full</td><td>lodash-es with named imports, or native ES2023+ methods</td></tr>
  <tr><td>axios</td><td>Native fetch (zero KB)</td></tr>
  <tr><td>jQuery</td><td>Modern DOM APIs (you don&rsquo;t need it in React)</td></tr>
  <tr><td>UUID library</td><td><code>crypto.randomUUID()</code> (built-in)</td></tr>
  <tr><td>Heavy chart libs</td><td>Recharts, Visx (smaller than D3 + Chart.js combined)</td></tr>
</table>

<p><strong>Performance budget</strong>: agree on a maximum gzipped initial bundle size (e.g., 200KB). Add a CI check that fails when exceeded. <strong>Keep an eye on</strong>: page weight (HTML + JS + CSS), critical render path, and Lighthouse&rsquo;s "Total Blocking Time" metric &mdash; these matter more than raw KB.</p>

<p><strong>Modern apps</strong> using Next.js with RSC can ship under 100KB initial JS for a dashboard &mdash; most logic runs server-side, client gets only the interactive bits.</p>
'''

ANSWERS[65] = r'''
<p>Suspense for data fetching is React&rsquo;s mechanism for declaratively waiting on async data &mdash; instead of every component managing its own loading state, a Suspense boundary catches the "I&rsquo;m not ready" signal from any descendant and renders a fallback. With React 19&rsquo;s <code>use()</code> hook, this pattern is finally first-class.</p>

<p><strong>The React 19 <code>use()</code> hook:</strong></p>

<pre><code>import { use, Suspense } from "react";

function Profile({ userPromise }) {
  const user = use(userPromise);    // suspends until promise resolves
  return &lt;h1&gt;{user.name}&lt;/h1&gt;;
}

function App() {
  // Promise created once, passed down — fetching starts immediately
  const userPromise = fetchUser(123);

  return (
    &lt;Suspense fallback={&lt;Spinner /&gt;}&gt;
      &lt;Profile userPromise={userPromise} /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>The mechanism</strong>: when <code>use(promise)</code> is called and the promise hasn&rsquo;t resolved, React throws the promise. Suspense catches it, renders the fallback, and re-renders the subtree when the promise resolves. Components don&rsquo;t need <code>useState</code> for loading or <code>useEffect</code> for fetching.</p>

<p><strong>Streaming with nested boundaries:</strong></p>

<pre><code>&lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
  &lt;Header /&gt;                           {/* fast, renders first */}

  &lt;Suspense fallback={&lt;ContentSkeleton /&gt;}&gt;
    &lt;MainContent /&gt;                     {/* loads independently */}
  &lt;/Suspense&gt;

  &lt;Suspense fallback={&lt;SidebarSkeleton /&gt;}&gt;
    &lt;Sidebar /&gt;                         {/* loads independently */}
  &lt;/Suspense&gt;
&lt;/Suspense&gt;</code></pre>

<p>Each section reveals as its data loads &mdash; no waterfall. The user sees the header immediately; main and sidebar appear when ready, in any order.</p>

<p><strong>Why this is better than <code>useEffect</code> + <code>useState</code>:</strong></p>

<table>
  <tr><th>Old pattern</th><th>Suspense pattern</th></tr>
  <tr><td>Loading state in every component</td><td>Loading boundary in one place</td></tr>
  <tr><td>Component-level race conditions</td><td>React handles via prioritization</td></tr>
  <tr><td>Render → fetch → re-render waterfall</td><td>Fetch starts before render (data passed as prop)</td></tr>
  <tr><td>SSR difficult</td><td>SSR streaming built-in</td></tr>
  <tr><td>Easy to forget to handle errors</td><td>Error boundaries catch all suspense errors</td></tr>
</table>

<p><strong>Avoid the waterfall trap</strong>:</p>

<pre><code>// BAD — sequential waterfall: A finishes, then B starts
function Page() {
  const a = use(fetchA());                  // waits
  const b = use(fetchB(a.id));              // can&rsquo;t start until a is done
  return &lt;Layout a={a} b={b} /&gt;;
}

// GOOD — parallel: both start immediately
function Page() {
  const aPromise = fetchA();
  const bPromise = fetchB();                 // parallel
  const a = use(aPromise);
  const b = use(bPromise);
  return &lt;Layout a={a} b={b} /&gt;;
}

// BEST — start at parent (data fetching outside the component)
function App() {
  const aPromise = fetchA();
  const bPromise = fetchB();                 // begin even earlier

  return (
    &lt;Suspense fallback={&lt;Skeleton /&gt;}&gt;
      &lt;Page aPromise={aPromise} bPromise={bPromise} /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>Pairing with libraries</strong>: TanStack Query supports Suspense via <code>useSuspenseQuery</code>. Apollo Client, urql, Relay, Next.js App Router all integrate. Most production data libraries either ship Suspense support or are adding it.</p>

<p><strong>Server Components alignment</strong>: in Next.js App Router, <code>async</code> server components <code>await</code> data and stream HTML to the client &mdash; no client-side <code>useEffect</code> or loading state. Suspense boundaries handle the streaming. The new mental model is: data fetches as close to the data as possible (server, when possible), client just renders.</p>

<p>Suspense for data fetching turns React into a coordinator of async work rather than a coordinator of state machines &mdash; cleaner, more performant, but requires libraries or RSC to use it well.</p>
'''

ANSWERS[66] = r'''
<p>SSR with Redux: the server creates a fresh store per request, dispatches initial actions to populate state, renders the React tree to HTML, and sends both the HTML and the serialized state to the client. The client hydrates the same tree with the same state, avoiding a content flash.</p>

<p><strong>The five-step flow:</strong></p>

<ol>
  <li>Request arrives → server creates new Redux store.</li>
  <li>Server dispatches initial async actions (e.g., <code>fetchUser</code>) and waits for completion.</li>
  <li>Server renders <code>&lt;Provider store={store}&gt;...&lt;/Provider&gt;</code> to HTML.</li>
  <li>Server serializes <code>store.getState()</code> into an inline <code>&lt;script&gt;</code>.</li>
  <li>Client reads the inline state, creates a store with it as initial state, hydrates.</li>
</ol>

<p><strong>Server-side (Express + Redux Toolkit):</strong></p>

<pre><code>import { renderToString } from "react-dom/server";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import rootReducer from "./store/rootReducer";
import { fetchInitialData } from "./store/initialDataSlice";

app.get("*", async (req, res) =&gt; {
  // 1. Fresh store per request — never share across requests
  const store = configureStore({ reducer: rootReducer });

  // 2. Pre-populate store with data needed for initial render
  await store.dispatch(fetchInitialData(req.url));

  // 3. Render to HTML
  const html = renderToString(
    &lt;Provider store={store}&gt;
      &lt;App url={req.url} /&gt;
    &lt;/Provider&gt;
  );

  // 4. Serialize state safely (escape XSS)
  const preloadedState = serialize(store.getState(), { isJSON: true });

  res.send(`
    &lt;!DOCTYPE html&gt;
    &lt;html&gt;
      &lt;body&gt;
        &lt;div id="root"&gt;${html}&lt;/div&gt;
        &lt;script&gt;
          window.__PRELOADED_STATE__ = ${preloadedState};
        &lt;/script&gt;
        &lt;script src="/client.js"&gt;&lt;/script&gt;
      &lt;/body&gt;
    &lt;/html&gt;
  `);
});</code></pre>

<p><strong>Client-side hydration:</strong></p>

<pre><code>import { hydrateRoot } from "react-dom/client";
import { configureStore } from "@reduxjs/toolkit";
import rootReducer from "./store/rootReducer";

// 5. Read server state and hydrate
const preloadedState = window.__PRELOADED_STATE__;
delete window.__PRELOADED_STATE__;     // clean up window pollution

const store = configureStore({
  reducer: rootReducer,
  preloadedState                       // start with server state
});

hydrateRoot(
  document.getElementById("root"),
  &lt;Provider store={store}&gt;
    &lt;App /&gt;
  &lt;/Provider&gt;
);</code></pre>

<p><strong>Critical safety rules:</strong></p>

<table>
  <tr><th>Rule</th><th>Why</th></tr>
  <tr><td>Never share store across requests</td><td>State leaks between users; security disaster</td></tr>
  <tr><td>Serialize state safely (escape XSS)</td><td>Use <code>serialize-javascript</code>; <code>JSON.stringify</code> doesn&rsquo;t escape <code>&lt;/script&gt;</code></td></tr>
  <tr><td>Don&rsquo;t put secrets in Redux state</td><td>Serialized state is visible in HTML source</td></tr>
  <tr><td>Hydrate with same data server rendered with</td><td>Mismatch causes hydration warnings/errors</td></tr>
  <tr><td>Wait for async actions on server</td><td>Otherwise renders empty state, defeats SSR purpose</td></tr>
</table>

<p><strong>For Next.js (Pages Router)</strong>: <code>getServerSideProps</code> can dispatch into a per-request store and return state via <code>props</code> for the page&rsquo;s initial state. Many Next apps in 2026 use the App Router instead, which is RSC-first and largely sidesteps Redux for server data.</p>

<p><strong>For Next.js (App Router) with Server Components</strong>: server data lives in the RSC layer, doesn&rsquo;t need Redux to bridge SSR. Redux remains useful for client-only state (UI-heavy local state, multi-step wizards). The split is cleaner: server data via RSC + TanStack Query; client UI state via Redux Toolkit or Zustand.</p>

<p><strong>2026 reality</strong>: SSR + Redux is increasingly rare for new projects. The framework solutions (Next.js App Router, Remix loaders, TanStack Start) handle data flow without Redux entirely. Use Redux SSR primarily for legacy migration or apps with genuinely complex client-side action logs that benefit from server hydration.</p>
'''

ANSWERS[67] = r'''
<p><strong>React Concurrent Mode</strong> (now stable since React 18) is a set of features that make React rendering interruptible &mdash; allowing React to pause work, prioritize urgent updates, and avoid blocking the main thread. The key shift: rendering became <strong>concurrent</strong> rather than always synchronous.</p>

<p><strong>The three concurrent features that shipped in React 18+:</strong></p>

<table>
  <tr><th>Feature</th><th>Purpose</th></tr>
  <tr><td><code>useTransition</code></td><td>Mark updates as low-priority; UI stays responsive during expensive renders</td></tr>
  <tr><td><code>useDeferredValue</code></td><td>Defer re-rendering with a stale value until React is idle</td></tr>
  <tr><td>Automatic batching</td><td>Multiple state updates in async callbacks batch into one render</td></tr>
  <tr><td>Streaming SSR with Suspense</td><td>Server streams HTML in chunks; nested Suspense boundaries reveal independently</td></tr>
</table>

<p><strong><code>useTransition</code> example &mdash; non-blocking filtering:</strong></p>

<pre><code>import { useState, useTransition } from "react";

function SearchableList({ items }) {
  const [query, setQuery] = useState("");
  const [filtered, setFiltered] = useState(items);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) =&gt; {
    setQuery(e.target.value);   // urgent — input updates immediately

    startTransition(() =&gt; {
      // Non-urgent — React can interrupt this if user keeps typing
      setFiltered(items.filter(i =&gt; i.name.includes(e.target.value)));
    });
  };

  return (
    &lt;&gt;
      &lt;input value={query} onChange={handleChange} /&gt;
      {isPending &amp;&amp; &lt;span&gt;Filtering...&lt;/span&gt;}
      &lt;ul style={{ opacity: isPending ? 0.6 : 1 }}&gt;
        {filtered.map(item =&gt; &lt;li key={item.id}&gt;{item.name}&lt;/li&gt;)}
      &lt;/ul&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>Without transitions: typing in the input on a list of 10,000 items would block on every keystroke &mdash; visible lag. With transitions: input stays smooth; the filter renders run in the background and yield to user input.</p>

<p><strong><code>useDeferredValue</code> example &mdash; same idea, simpler when state is in the same component:</strong></p>

<pre><code>function SearchableList({ items }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const filtered = items.filter(i =&gt; i.name.includes(deferredQuery));
  // ...
}</code></pre>

<p><code>deferredQuery</code> lags <code>query</code> &mdash; React updates it when idle.</p>

<p><strong>Why "concurrent" matters &mdash; the underlying mechanism</strong>:</p>

<ul>
  <li><strong>Pre-React 18</strong>: rendering was synchronous; once React started rendering, the main thread was blocked until done. Long renders = unresponsive UI.</li>
  <li><strong>React 18+</strong>: rendering is interruptible. React can yield to the browser to handle clicks, paint frames, run microtasks &mdash; then resume rendering.</li>
  <li><strong>Result</strong>: high-priority updates (typing, clicks, hovers) feel instant even when low-priority work is happening in the background.</li>
</ul>

<p><strong>Concurrent rendering also enables Suspense for data fetching</strong>: React can show a fallback while async data loads, and reveal the actual UI when ready &mdash; without throwing away other parts of the tree that finished earlier.</p>

<p><strong>You don&rsquo;t opt in &mdash; it&rsquo;s automatic</strong>: just by upgrading to React 18+ with <code>createRoot</code> instead of <code>ReactDOM.render</code>, your app gets concurrent rendering. The new hooks (<code>useTransition</code>, <code>useDeferredValue</code>) let you take advantage explicitly.</p>

<p><strong>React 19 builds on this</strong>: the <code>use()</code> hook for promises, Server Components, and the React Compiler all rely on concurrent foundations. Concurrent rendering isn&rsquo;t a feature you toggle &mdash; it&rsquo;s the runtime React now uses by default.</p>

<p><strong>Practical advice</strong>: for most apps, you don&rsquo;t need to think about concurrent features explicitly. Reach for <code>useTransition</code> when you have a specific expensive render that lags input (search filters over big lists, expensive charts, heavy reorganization on data change). Profile first; don&rsquo;t add transitions speculatively.</p>
'''

ANSWERS[68] = r'''
<p>Complex animations in React span: layout-driven transitions (mount/unmount, reorder), gesture-driven (drag, swipe, pinch), choreographed sequences (staggered reveals), physics-based (springs, momentum), and timeline-based (scrubbable, scroll-driven). Different needs map to different libraries.</p>

<p><strong>The library landscape (2026):</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td><strong>Framer Motion</strong></td><td>Most React animations &mdash; declarative, gestures, layout, springs</td></tr>
  <tr><td><strong>React Spring</strong></td><td>Physics-based; data-driven motion; very flexible</td></tr>
  <tr><td><strong>GSAP</strong></td><td>Complex timelines, scroll-driven, professional-grade</td></tr>
  <tr><td><strong>Auto-Animate</strong></td><td>Drop-in for list reorders; minimal config</td></tr>
  <tr><td><strong>CSS animations</strong></td><td>Simple state transitions; zero JS</td></tr>
  <tr><td><strong>View Transitions API</strong></td><td>Cross-page transitions; native browser API</td></tr>
</table>

<p><strong>Framer Motion patterns &mdash; the workhorse for most apps:</strong></p>

<pre><code>import { motion, AnimatePresence } from "framer-motion";

// Mount/unmount with exit animation
&lt;AnimatePresence mode="wait"&gt;
  {isOpen &amp;&amp; (
    &lt;motion.div
      key="modal"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    &gt;
      Modal content
    &lt;/motion.div&gt;
  )}
&lt;/AnimatePresence&gt;

// Layout animations — auto-animate when size/position changes
&lt;motion.div layout&gt;
  {expanded ? &lt;LongContent /&gt; : &lt;ShortContent /&gt;}
&lt;/motion.div&gt;

// Choreographed list with staggered children
&lt;motion.ul
  variants={{
    show: { transition: { staggerChildren: 0.1 } }
  }}
  initial="hidden"
  animate="show"
&gt;
  {items.map(item =&gt; (
    &lt;motion.li
      key={item.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        show:   { opacity: 1, y: 0 }
      }}
    &gt;
      {item.name}
    &lt;/motion.li&gt;
  ))}
&lt;/motion.ul&gt;

// Drag with constraints
&lt;motion.div drag dragConstraints={{ top: 0, bottom: 200 }} /&gt;</code></pre>

<p><strong>Layout animations</strong> are Framer Motion&rsquo;s killer feature: any change to size or position of a <code>motion.div</code> with the <code>layout</code> prop animates smoothly &mdash; including across reorders, parent layout shifts, and conditional rendering. Pre-2020, this was painful manual FLIP animation work.</p>

<p><strong>Performance fundamentals</strong>:</p>

<ul>
  <li><strong>Animate <code>transform</code> and <code>opacity</code></strong> &mdash; GPU-accelerated, no layout reflow.</li>
  <li><strong>Avoid animating <code>width</code>, <code>height</code>, <code>top</code>, <code>left</code>, <code>margin</code></strong> on hot elements &mdash; triggers layout, slow.</li>
  <li><strong>Use <code>will-change: transform</code></strong> for known-to-animate elements (sparingly &mdash; promotes to a compositor layer).</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; users with vestibular disorders depend on it.</li>
</ul>

<p><strong>Reduced motion in Framer Motion:</strong></p>

<pre><code>import { useReducedMotion } from "framer-motion";

function Animated() {
  const reduce = useReducedMotion();
  return (
    &lt;motion.div
      animate={{ y: 0 }}
      initial={{ y: reduce ? 0 : 50 }}    // skip animation if user prefers reduced motion
    /&gt;
  );
}</code></pre>

<p><strong>For scroll-driven animations</strong>: the native <strong>scroll-timeline CSS</strong> or Framer Motion&rsquo;s <code>useScroll</code> hook. Native CSS scroll-driven animations (<code>animation-timeline: scroll()</code>) shipped in Chrome 115+ and are perfect for parallax, progress indicators, scroll-triggered reveals &mdash; with zero JS.</p>

<p><strong>Cross-page transitions</strong>: the <strong>View Transitions API</strong> (Chrome 111+, increasing browser support) lets you animate between page states declaratively. Next.js and Remix have integrations; React Router v7 supports it natively.</p>

<p><strong>For complex orchestration</strong> (animations driven by data changes, multi-step sequences, animations that branch): React Spring&rsquo;s imperative API is more flexible than Framer Motion&rsquo;s declarative props. Choose based on whether your animation logic fits in render or needs to be programmatic.</p>
'''

ANSWERS[69] = r'''
<p><code>useMemo</code> and <code>useCallback</code> both memoize values across renders, but for different things: <code>useMemo</code> caches the <strong>result</strong> of a function; <code>useCallback</code> caches the <strong>function itself</strong>. They&rsquo;re close cousins &mdash; <code>useCallback(fn, deps)</code> is equivalent to <code>useMemo(() =&gt; fn, deps)</code>.</p>

<table>
  <tr><th></th><th><code>useMemo</code></th><th><code>useCallback</code></th></tr>
  <tr><td>What it caches</td><td>The result of calling a function</td><td>The function reference itself</td></tr>
  <tr><td>Returns</td><td>Whatever your function returns</td><td>The function</td></tr>
  <tr><td>Use for</td><td>Expensive computations, derived data, stable object/array refs</td><td>Stable function references for memoized children, hook deps</td></tr>
  <tr><td>Equivalent</td><td><code>useMemo(() =&gt; calc(), deps)</code></td><td><code>useMemo(() =&gt; fn, deps)</code> = <code>useCallback(fn, deps)</code></td></tr>
</table>

<p><strong>useMemo &mdash; cache derived data:</strong></p>

<pre><code>const filtered = useMemo(
  () =&gt; products.filter(p =&gt; p.price &lt; maxPrice),
  [products, maxPrice]
);
// filtered re-computes only when products or maxPrice change</code></pre>

<p><strong>useCallback &mdash; stable function reference:</strong></p>

<pre><code>const handleSave = useCallback((data) =&gt; {
  saveToServer(userId, data);
}, [userId]);
// handleSave is the same reference unless userId changes
// Memoized children using handleSave as a prop won&rsquo;t re-render unnecessarily</code></pre>

<p><strong>When each is genuinely useful</strong>:</p>

<table>
  <tr><th>Use useMemo when</th><th>Use useCallback when</th></tr>
  <tr><td>Computation is expensive (filter/sort 1000+ items, complex math)</td><td>Function is passed to memoized child (<code>React.memo</code>)</td></tr>
  <tr><td>Need stable object/array reference for memoized children</td><td>Function is a dependency of <code>useEffect</code>/<code>useMemo</code></td></tr>
  <tr><td>Need stable reference for context value</td><td>Function is exposed from a custom hook with stable-identity expectations</td></tr>
</table>

<p><strong>When NOT to use them</strong> &mdash; common over-applications:</p>

<ul>
  <li><strong>Cheap calculations</strong> &mdash; <code>x + y</code>, simple object construction. Memoization overhead exceeds savings.</li>
  <li><strong>Functions only used in JSX</strong> &mdash; not passed to memoized children. <code>useCallback</code> doesn&rsquo;t help.</li>
  <li><strong>Deps that change every render</strong> &mdash; if deps always differ, you&rsquo;re paying overhead to never hit the cache.</li>
  <li><strong>"Just to be safe"</strong> &mdash; premature memoization adds noise without benefit.</li>
</ul>

<p><strong>The "stable reference for memoized child" pattern:</strong></p>

<pre><code>const Child = memo(function Child({ onSave, items }) { /* ... */ });

function Parent() {
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);

  // WITHOUT useCallback/useMemo: every render = new refs = Child always re-renders
  const handleSave = () =&gt; { /* ... */ };
  const itemList = items.filter(i =&gt; i.active);

  // WITH: refs stable; Child only re-renders when items or relevant data changes
  const handleSave = useCallback(() =&gt; { /* ... */ }, []);
  const itemList = useMemo(() =&gt; items.filter(i =&gt; i.active), [items]);

  return &lt;Child onSave={handleSave} items={itemList} /&gt;;
}</code></pre>

<p>Without memoization, clicking a counter (changing <code>count</code>) would re-render <code>Child</code> even though its props didn&rsquo;t conceptually change. With <code>useCallback</code> + <code>useMemo</code>, the props remain referentially equal, <code>memo</code> bails out of the re-render.</p>

<p><strong>React 19&rsquo;s React Compiler</strong> automatically applies <code>useMemo</code>/<code>useCallback</code> where beneficial &mdash; the compiler analyzes your code and inserts memoization at compile time. With the compiler enabled, manual <code>useMemo</code>/<code>useCallback</code> becomes mostly unnecessary. For new code targeting React 19+, write naturally; let the compiler optimize.</p>

<p><strong>Mental model</strong>: <code>useMemo</code> is a cache for "the result of computing X with these inputs"; <code>useCallback</code> is a cache for "this exact function definition." Both exist to keep referential equality stable so memoization downstream isn&rsquo;t defeated.</p>
'''

ANSWERS[70] = r'''
<p>Integrating React with a CMS depends on the CMS type: <strong>headless</strong> (CMS provides content via API; React app renders) or <strong>traditional/coupled</strong> (CMS owns rendering; you embed React widgets). Modern stacks favor headless &mdash; React fully owns the UI; CMS is just a data source.</p>

<p><strong>The headless CMS landscape (2026):</strong></p>

<table>
  <tr><th>CMS</th><th>Style</th><th>Best for</th></tr>
  <tr><td>Sanity</td><td>Real-time, structured content; Studio is React</td><td>Editorial sites, complex schemas</td></tr>
  <tr><td>Contentful</td><td>Mature SaaS; rich API; localization built-in</td><td>Enterprise content sites</td></tr>
  <tr><td>Strapi</td><td>Open source, self-hostable</td><td>Cost-conscious; data ownership</td></tr>
  <tr><td>Payload</td><td>Code-first, TypeScript schema, self-hosted</td><td>Developers who want config-as-code</td></tr>
  <tr><td>Hygraph (GraphCMS)</td><td>GraphQL-native</td><td>Already using GraphQL stack</td></tr>
  <tr><td>Storyblok</td><td>Visual editing with components</td><td>Marketing teams editing live</td></tr>
  <tr><td>WordPress + REST/GraphQL</td><td>Familiar to editors; vast ecosystem</td><td>Migrating from existing WordPress</td></tr>
</table>

<p><strong>Typical integration pattern (Next.js + Sanity example):</strong></p>

<pre><code>import { sanityClient } from "./lib/sanity";

// Server Component fetches at build/request time
export default async function BlogPage({ params }) {
  const post = await sanityClient.fetch(
    `*[_type == "post" &amp;&amp; slug.current == $slug][0] {
      title,
      body,
      author-&gt;{ name, image },
      publishedAt
    }`,
    { slug: params.slug }
  );

  return (
    &lt;article&gt;
      &lt;h1&gt;{post.title}&lt;/h1&gt;
      &lt;PortableText value={post.body} /&gt;
      &lt;p&gt;By {post.author.name}&lt;/p&gt;
    &lt;/article&gt;
  );
}</code></pre>

<p><strong>The four critical decisions:</strong></p>

<table>
  <tr><th>Decision</th><th>Options</th></tr>
  <tr><td>When to fetch</td><td>Build-time (SSG), request-time (SSR), client-time (CSR), or revalidation (ISR)</td></tr>
  <tr><td>Content rendering</td><td>Plain markdown, rich text serializers (Portable Text, MDX), or HTML strings</td></tr>
  <tr><td>Image handling</td><td>CMS-provided image API, Cloudinary/imgix, Next.js Image</td></tr>
  <tr><td>Preview mode</td><td>Draft content viewing for editors before publish</td></tr>
</table>

<p><strong>Build-time vs request-time fetching:</strong></p>

<pre><code>// Static (build time) — best for blog posts, marketing pages
export async function generateStaticParams() {
  const posts = await sanityClient.fetch(`*[_type == "post"]{slug}`);
  return posts.map(p =&gt; ({ slug: p.slug.current }));
}

// Incremental Static Regeneration — rebuild on edit
export const revalidate = 60;   // re-fetch every 60 seconds

// On-demand revalidation via webhook from CMS
// CMS calls /api/revalidate when content changes — pages update instantly</code></pre>

<p><strong>Webhook-based revalidation</strong> is the modern pattern: CMS notifies your deploy when content changes; specific pages rebuild. Editor sees their edit live within seconds without a full deploy. Vercel and Netlify have first-class support.</p>

<p><strong>Rich text rendering &mdash; Portable Text (Sanity&rsquo;s format)</strong>:</p>

<pre><code>import { PortableText } from "@portabletext/react";

const components = {
  types: {
    image: ({ value }) =&gt; &lt;img src={urlForImage(value)} alt={value.alt} /&gt;,
    code:  ({ value }) =&gt; &lt;CodeBlock code={value.code} lang={value.language} /&gt;
  },
  marks: {
    link: ({ children, value }) =&gt; (
      &lt;a href={value.href} target="_blank" rel="noopener"&gt;{children}&lt;/a&gt;
    )
  }
};

&lt;PortableText value={post.body} components={components} /&gt;</code></pre>

<p>Each content block is rendered by a React component &mdash; full control over structured content. Better than serving HTML strings (XSS risk, no React component features).</p>

<p><strong>For e-commerce</strong>: Shopify, BigCommerce, Commerce.js follow the same pattern &mdash; product/cart APIs consumed by React. Many sites pair: <strong>Sanity for content + Shopify for commerce + Algolia for search</strong>, all behind a Next.js facade.</p>
'''

ANSWERS[71] = r'''
<p>State persistence keeps user data across page reloads, browser restarts, and sessions. React provides no built-in persistence &mdash; you choose the storage mechanism based on data sensitivity, size, and lifetime needs.</p>

<p><strong>Storage options:</strong></p>

<table>
  <tr><th>Mechanism</th><th>Persistence</th><th>Capacity</th><th>Use for</th></tr>
  <tr><td>localStorage</td><td>Forever (until cleared)</td><td>~5-10MB</td><td>Theme, language, drafts, non-sensitive prefs</td></tr>
  <tr><td>sessionStorage</td><td>Tab close</td><td>~5-10MB</td><td>Form drafts during a session, ephemeral wizard state</td></tr>
  <tr><td>IndexedDB</td><td>Forever</td><td>Hundreds of MB</td><td>Offline data, large structured stores, files</td></tr>
  <tr><td>Cookies (httpOnly)</td><td>Configurable</td><td>4KB</td><td>Auth tokens (server-readable)</td></tr>
  <tr><td>Server (database)</td><td>Forever, cross-device</td><td>Unlimited</td><td>User data, multi-device sync</td></tr>
</table>

<p><strong>Pattern 1 &mdash; <code>useLocalStorage</code> custom hook:</strong></p>

<pre><code>function useLocalStorage&lt;T&gt;(key: string, initial: T) {
  const [value, setValue] = useState&lt;T&gt;(() =&gt; {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initial;
    } catch { return initial; }
  });

  useEffect(() =&gt; {
    try { localStorage.setItem(key, JSON.stringify(value)); }
    catch { /* quota exceeded, etc. */ }
  }, [key, value]);

  // Multi-tab sync: listen for storage events from other tabs
  useEffect(() =&gt; {
    const handler = (e: StorageEvent) =&gt; {
      if (e.key === key &amp;&amp; e.newValue) {
        try { setValue(JSON.parse(e.newValue)); } catch {}
      }
    };
    window.addEventListener("storage", handler);
    return () =&gt; window.removeEventListener("storage", handler);
  }, [key]);

  return [value, setValue] as const;
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "light");</code></pre>

<p><strong>Pattern 2 &mdash; redux-persist for Redux:</strong></p>

<pre><code>import { persistReducer, persistStore } from "redux-persist";
import storage from "redux-persist/lib/storage";

const persistConfig = {
  key: "root",
  storage,
  whitelist: ["user", "preferences"],     // only persist these slices
  blacklist: ["transient"],                // never persist these
  version: 1,
  migrate: (state) =&gt; { /* version migration */ }
};

const persistedReducer = persistReducer(persistConfig, rootReducer);
const store = configureStore({ reducer: persistedReducer, /* ... */ });
const persistor = persistStore(store);

// Wrap App in PersistGate to wait for rehydration
&lt;Provider store={store}&gt;
  &lt;PersistGate loading={&lt;Spinner /&gt;} persistor={persistor}&gt;
    &lt;App /&gt;
  &lt;/PersistGate&gt;
&lt;/Provider&gt;</code></pre>

<p><strong>Pattern 3 &mdash; Zustand persist middleware:</strong></p>

<pre><code>import { create } from "zustand";
import { persist } from "zustand/middleware";

const useStore = create(
  persist(
    (set) =&gt; ({
      cart: [],
      addItem: (item) =&gt; set(s =&gt; ({ cart: [...s.cart, item] }))
    }),
    {
      name: "cart-storage",
      partialize: (state) =&gt; ({ cart: state.cart })   // persist only cart, not all state
    }
  )
);</code></pre>

<p><strong>Critical considerations:</strong></p>

<table>
  <tr><th>Concern</th><th>Approach</th></tr>
  <tr><td>Sensitive data</td><td>Never put auth tokens or PII in localStorage; use httpOnly cookies</td></tr>
  <tr><td>Schema versioning</td><td>Include version field; migrate old data on read</td></tr>
  <tr><td>Quota exceeded</td><td>Wrap setItem in try/catch; have fallback (in-memory only)</td></tr>
  <tr><td>SSR hydration mismatch</td><td>Read storage in <code>useEffect</code>, not during render &mdash; or guard with <code>typeof window</code></td></tr>
  <tr><td>Multi-tab sync</td><td>Listen for <code>storage</code> events; or use BroadcastChannel</td></tr>
  <tr><td>Cross-device sync</td><td>Sync to server; localStorage isn&rsquo;t enough</td></tr>
</table>

<p><strong>For offline-first apps</strong>, IndexedDB via libraries like <strong>Dexie</strong> or <strong>RxDB</strong> handles much larger datasets than localStorage. <strong>For TanStack Query</strong>, the <code>persistQueryClient</code> plugin caches API responses to localStorage/IndexedDB &mdash; instant loads on repeat visits.</p>

<p><strong>SSR / Next.js consideration</strong>: localStorage doesn&rsquo;t exist on the server. Persistent state must initialize on the client only, after hydration. Reading it during the initial server render or pre-hydration causes errors. Use <code>useEffect</code> to hydrate from storage post-mount.</p>
'''

ANSWERS[72] = r'''
<p>The "container vs presentational" pattern (popularized by Dan Abramov in 2015) splits components into: <strong>container</strong> components that fetch data, manage state, and orchestrate; and <strong>presentational</strong> components that just render UI from props. The pattern brought clarity to a confusing era &mdash; but with hooks, it&rsquo;s mostly obsolete in 2026.</p>

<p><strong>The classic split:</strong></p>

<pre><code>// PRESENTATIONAL — receives props, no state, no data fetching
function UserList({ users, onSelect, isLoading }) {
  if (isLoading) return &lt;Spinner /&gt;;
  return (
    &lt;ul&gt;
      {users.map(u =&gt; (
        &lt;li key={u.id} onClick={() =&gt; onSelect(u)}&gt;
          {u.name}
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

// CONTAINER — fetches data, manages state, passes to presentational
class UserListContainer extends Component {
  state = { users: [], isLoading: true };

  componentDidMount() {
    fetch("/api/users")
      .then(r =&gt; r.json())
      .then(users =&gt; this.setState({ users, isLoading: false }));
  }

  handleSelect = (user) =&gt; { /* ... */ };

  render() {
    return &lt;UserList
      users={this.state.users}
      isLoading={this.state.isLoading}
      onSelect={this.handleSelect}
    /&gt;;
  }
}</code></pre>

<p><strong>Why this pattern emerged</strong>: in 2015, components were classes; data-fetching code mixed with UI made tests painful and reuse limited. Splitting let you: test presentation easily (snapshots from props), reuse presentation across data sources, and reason about data flow.</p>

<p><strong>Why it&rsquo;s mostly obsolete in 2026</strong>: hooks dissolve the artificial split. Custom hooks encapsulate data + state + logic; components consume them. There&rsquo;s no need for a separate "container" wrapping a "presentational" &mdash; they merge naturally.</p>

<pre><code>// Modern equivalent — single component using a custom hook
function useUsers() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: () =&gt; fetch("/api/users").then(r =&gt; r.json())
  });
  return { users: data || [], isLoading, error };
}

function UserList({ onSelect }) {
  const { users, isLoading } = useUsers();

  if (isLoading) return &lt;Spinner /&gt;;
  return (
    &lt;ul&gt;
      {users.map(u =&gt; (
        &lt;li key={u.id} onClick={() =&gt; onSelect(u)}&gt;{u.name}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p>The <code>useUsers</code> hook plays the "container" role; the component renders. They co-locate cleanly without the ceremony.</p>

<p><strong>What&rsquo;s still useful from the original pattern</strong>:</p>

<ul>
  <li><strong>Pure UI components for design systems</strong> &mdash; <code>&lt;Button&gt;</code>, <code>&lt;Card&gt;</code>, <code>&lt;Input&gt;</code> taking only props, never fetching. This is just "presentational" by another name.</li>
  <li><strong>Separation of data and presentation in tests</strong> &mdash; mocking the hook makes tests deterministic without needing to mock fetch.</li>
  <li><strong>Composition</strong> &mdash; <code>&lt;DataProvider&gt;{(data) =&gt; &lt;UI data={data} /&gt;}&lt;/DataProvider&gt;</code> patterns still work for some cases.</li>
</ul>

<p><strong>Modern equivalents and where they apply:</strong></p>

<table>
  <tr><th>Old idea</th><th>2026 equivalent</th></tr>
  <tr><td>Container component</td><td>Custom hook + component using it</td></tr>
  <tr><td>Presentational component</td><td>Pure UI component (still valid for design systems)</td></tr>
  <tr><td>Connect HOC (Redux)</td><td><code>useSelector</code> / <code>useDispatch</code></td></tr>
  <tr><td>State-management container</td><td>Server-side data: TanStack Query; client UI state: useState/Zustand</td></tr>
</table>

<p><strong>For React Server Components</strong> (Next.js App Router, future direction): the new natural split is <strong>server components</strong> (data fetching, no interactivity) + <strong>client components</strong> (interactivity, no data fetching). This subsumes container/presentational with an architectural enforcement &mdash; the boundary is the network rather than a developer convention.</p>

<p><strong>Bottom line for interview answers</strong>: explain the pattern&rsquo;s history and rationale, then note that hooks made it less necessary, and modern apps achieve the same separation through custom hooks + pure UI components in design systems. Knowing the history shows depth; knowing it&rsquo;s outdated shows currency.</p>
'''

ANSWERS[73] = r'''
<p>WebSocket connections in React need: connection lifecycle management (open, close, reconnect), message handling, sharing the connection across components, and graceful cleanup on unmount. A custom hook plus Context (or a state library) typically handles this; production apps reach for libraries like Socket.IO.</p>

<p><strong>Custom hook for a single connection:</strong></p>

<pre><code>import { useEffect, useState, useRef, useCallback } from "react";

type Status = "connecting" | "open" | "closing" | "closed" | "error";

function useWebSocket(url: string) {
  const [status, setStatus] = useState&lt;Status&gt;("connecting");
  const [lastMessage, setLastMessage] = useState&lt;any&gt;(null);
  const wsRef = useRef&lt;WebSocket | null&gt;(null);
  const reconnectTimerRef = useRef&lt;ReturnType&lt;typeof setTimeout&gt; | null&gt;(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() =&gt; {
    setStatus("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () =&gt; {
      setStatus("open");
      reconnectAttemptsRef.current = 0;
    };

    ws.onclose = (e) =&gt; {
      setStatus("closed");
      // Reconnect with exponential backoff (max 30s)
      if (!e.wasClean) {
        const delay = Math.min(1000 * 2 ** reconnectAttemptsRef.current, 30000);
        reconnectAttemptsRef.current++;
        reconnectTimerRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () =&gt; setStatus("error");

    ws.onmessage = (e) =&gt; {
      try { setLastMessage(JSON.parse(e.data)); }
      catch { setLastMessage(e.data); }
    };
  }, [url]);

  useEffect(() =&gt; {
    connect();
    return () =&gt; {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data: any) =&gt; {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === "string" ? data : JSON.stringify(data));
    }
  }, []);

  return { status, lastMessage, send };
}</code></pre>

<p><strong>Sharing a connection across components &mdash; via Context:</strong></p>

<pre><code>const WSContext = createContext&lt;ReturnType&lt;typeof useWebSocket&gt; | null&gt;(null);

function WSProvider({ children, url }) {
  const ws = useWebSocket(url);
  return &lt;WSContext.Provider value={ws}&gt;{children}&lt;/WSContext.Provider&gt;;
}

const useWS = () =&gt; {
  const ctx = useContext(WSContext);
  if (!ctx) throw new Error("useWS must be used within WSProvider");
  return ctx;
};</code></pre>

<p>One connection serves the whole app &mdash; multiple components opening their own would waste server resources.</p>

<p><strong>Critical patterns the hook above implements:</strong></p>

<table>
  <tr><th>Pattern</th><th>Why</th></tr>
  <tr><td>Reconnection with exponential backoff</td><td>Handles network blips; max 30s prevents hammering server</td></tr>
  <tr><td>Track <code>readyState</code> before send</td><td>Sending on a closed socket throws; check first</td></tr>
  <tr><td>Cleanup on unmount</td><td>Prevents leaked connections in dev (StrictMode), tests, route changes</td></tr>
  <tr><td>Status state</td><td>UI can show "Reconnecting..." indicator</td></tr>
  <tr><td>JSON parsing wrapped</td><td>Server might send non-JSON; don&rsquo;t crash the app</td></tr>
</table>

<p><strong>Production libraries to consider:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>Socket.IO</td><td>Auto-reconnect, fallbacks (long polling), rooms, broadcasts</td></tr>
  <tr><td>react-use-websocket</td><td>Hook-based, well-tested, good defaults</td></tr>
  <tr><td>Pusher / Ably / Supabase Realtime</td><td>Managed services with channels, presence, history</td></tr>
  <tr><td>PartyKit</td><td>Cloudflare-native; simple multiplayer</td></tr>
  <tr><td>Yjs / Liveblocks</td><td>CRDTs for collaborative editing (cursors, multi-user docs)</td></tr>
</table>

<p><strong>Combining with TanStack Query</strong>: rather than holding socket data in component state, invalidate queries on socket events:</p>

<pre><code>useEffect(() =&gt; {
  if (lastMessage?.type === "USER_UPDATED") {
    queryClient.invalidateQueries({ queryKey: ["user", lastMessage.userId] });
  }
}, [lastMessage]);</code></pre>

<p>The query refetches automatically; UI updates via the same code path as initial loads. Avoids hand-merging socket payloads into local state &mdash; one source of truth.</p>

<p><strong>Authentication for WebSockets</strong>: pass token via query string (<code>ws://api/?token=...</code>) for the handshake, or use a cookie if same-origin. The standard WebSocket API doesn&rsquo;t support custom headers in the browser. Validate the token server-side on connect; close immediately if invalid.</p>
'''

ANSWERS[74] = r'''
<p><code>forwardRef</code> lets a component pass a ref through to a child DOM element. Without it, a parent that wants direct access to a custom component&rsquo;s underlying DOM (to focus an input, scroll into view, measure) couldn&rsquo;t reach it &mdash; refs only attach to DOM elements and class components, not function components by default.</p>

<p><strong>The classic pattern (React 18 and earlier):</strong></p>

<pre><code>import { forwardRef, useRef } from "react";

// Custom input that exposes its underlying input element via ref
const FancyInput = forwardRef&lt;HTMLInputElement, FancyInputProps&gt;(
  function FancyInput({ label, ...props }, ref) {
    return (
      &lt;label&gt;
        {label}
        &lt;input ref={ref} {...props} className="fancy-input" /&gt;
      &lt;/label&gt;
    );
  }
);

// Parent uses ref directly on the custom component
function Form() {
  const inputRef = useRef&lt;HTMLInputElement&gt;(null);

  useEffect(() =&gt; {
    inputRef.current?.focus();
  }, []);

  return &lt;FancyInput ref={inputRef} label="Name" /&gt;;
}</code></pre>

<p><strong>Without forwardRef</strong>: <code>&lt;FancyInput ref={inputRef} /&gt;</code> would warn that function components can&rsquo;t accept refs &mdash; the ref attaches to nothing.</p>

<p><strong>React 19 simplification &mdash; ref as a regular prop:</strong></p>

<pre><code>// React 19+: ref is just a prop, no forwardRef needed
function FancyInput({ label, ref, ...props }: FancyInputProps &amp; { ref?: Ref&lt;HTMLInputElement&gt; }) {
  return (
    &lt;label&gt;
      {label}
      &lt;input ref={ref} {...props} className="fancy-input" /&gt;
    &lt;/label&gt;
  );
}

// Parent — same usage as before
&lt;FancyInput ref={inputRef} label="Name" /&gt;</code></pre>

<p>React 19 deprecated <code>forwardRef</code> &mdash; <code>ref</code> is now a regular prop, eliminating the need for the wrapper. Existing <code>forwardRef</code> code still works (backward compatible); new code should use the prop form.</p>

<p><strong>Common use cases for forwarded refs:</strong></p>

<table>
  <tr><th>Use case</th><th>Why</th></tr>
  <tr><td>Focus management</td><td>Form libraries, modal focus on open, inline editing</td></tr>
  <tr><td>Scroll into view</td><td>Notifications, jump-to-error in long forms</td></tr>
  <tr><td>Measure element size</td><td>Tooltips, virtualization, animations</td></tr>
  <tr><td>Integrate with imperative libraries</td><td>D3, Three.js, video players, drag libraries</td></tr>
  <tr><td>Component libraries</td><td>Button, Input, etc. need to forward refs to underlying DOM</td></tr>
</table>

<p><strong>Combining with <code>useImperativeHandle</code> for custom APIs:</strong></p>

<pre><code>const FancyInput = forwardRef(function FancyInput(props, ref) {
  const inputRef = useRef&lt;HTMLInputElement&gt;(null);

  // Expose ONLY these methods to parent — not the raw DOM
  useImperativeHandle(ref, () =&gt; ({
    focus:    () =&gt; inputRef.current?.focus(),
    clear:    () =&gt; { if (inputRef.current) inputRef.current.value = ""; },
    getValue: () =&gt; inputRef.current?.value
  }), []);

  return &lt;input ref={inputRef} {...props} /&gt;;
});

// Parent gets the curated API
const inputApi = useRef(null);
inputApi.current?.focus();
inputApi.current?.clear();
const value = inputApi.current?.getValue();</code></pre>

<p>The parent gets a controlled API instead of full DOM access &mdash; can&rsquo;t accidentally call <code>.remove()</code>, set styles, etc. Useful for component library authors who want to expose specific behavior.</p>

<p><strong>Library design implications</strong>: any reusable component that wraps a DOM element should forward refs &mdash; otherwise consumers can&rsquo;t do focus management, animations, or DOM measurements. shadcn/ui, Radix, Material UI, Mantine all forward refs on every primitive component.</p>

<p><strong>Don&rsquo;t reach for refs first</strong>: most React UI is declarative state-driven. Use refs only when you genuinely need imperative DOM access. Common React mistakes include using refs to share state between components (use lifting or Context instead) and using refs to read DOM that&rsquo;s already in render output.</p>
'''

ANSWERS[75] = r'''
<p>A multi-step form (wizard) splits a long form into discrete steps. Patterns: maintain accumulated form state across steps, validate per step before advancing, allow back navigation without losing data, persist state for refresh resilience, show progress indicator.</p>

<p><strong>Production-ready architecture:</strong></p>

<pre><code>import { useReducer } from "react";

type WizardState = {
  step: number;
  data: {
    personal:  { name: string; email: string };
    address:   { street: string; city: string; zip: string };
    payment:   { cardNumber: string; expiry: string; cvv: string };
  };
  errors:    Record&lt;string, string&gt;;
};

type Action =
  | { type: "UPDATE_DATA"; section: keyof WizardState["data"]; values: any }
  | { type: "SET_ERRORS"; errors: Record&lt;string, string&gt; }
  | { type: "NEXT_STEP" }
  | { type: "PREV_STEP" }
  | { type: "RESET" };

function reducer(state: WizardState, action: Action): WizardState {
  switch (action.type) {
    case "UPDATE_DATA":
      return {
        ...state,
        data: { ...state.data, [action.section]: { ...state.data[action.section], ...action.values } },
        errors: {}
      };
    case "SET_ERRORS":
      return { ...state, errors: action.errors };
    case "NEXT_STEP":
      return { ...state, step: state.step + 1, errors: {} };
    case "PREV_STEP":
      return { ...state, step: Math.max(0, state.step - 1), errors: {} };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const initialState: WizardState = {
  step: 0,
  data: {
    personal: { name: "", email: "" },
    address:  { street: "", city: "", zip: "" },
    payment:  { cardNumber: "", expiry: "", cvv: "" }
  },
  errors: {}
};

const STEPS = ["Personal info", "Address", "Payment"];

function CheckoutWizard() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const validateCurrentStep = (): boolean =&gt; {
    const errors: Record&lt;string, string&gt; = {};

    if (state.step === 0) {
      if (!state.data.personal.name) errors.name = "Name required";
      if (!state.data.personal.email.includes("@")) errors.email = "Valid email required";
    } else if (state.step === 1) {
      if (!state.data.address.street) errors.street = "Street required";
      if (!/^\d{5}$/.test(state.data.address.zip)) errors.zip = "5-digit ZIP required";
    } else if (state.step === 2) {
      if (state.data.payment.cardNumber.length &lt; 13) errors.cardNumber = "Invalid card";
      if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(state.data.payment.expiry)) errors.expiry = "MM/YY";
    }

    if (Object.keys(errors).length &gt; 0) {
      dispatch({ type: "SET_ERRORS", errors });
      return false;
    }
    return true;
  };

  const next = () =&gt; { if (validateCurrentStep()) dispatch({ type: "NEXT_STEP" }); };
  const back = () =&gt; dispatch({ type: "PREV_STEP" });

  const submit = async () =&gt; {
    if (!validateCurrentStep()) return;
    await fetch("/api/checkout", { method: "POST", body: JSON.stringify(state.data) });
  };

  return (
    &lt;div&gt;
      {/* Progress bar */}
      &lt;ol style={{ display: "flex" }}&gt;
        {STEPS.map((label, i) =&gt; (
          &lt;li key={i} style={{
            flex: 1, padding: 8, textAlign: "center",
            background: i === state.step ? "#3b82f6" : i &lt; state.step ? "#10b981" : "#e5e7eb",
            color: i &lt;= state.step ? "white" : "#666"
          }}&gt;
            {label}
          &lt;/li&gt;
        ))}
      &lt;/ol&gt;

      {/* Step content */}
      {state.step === 0 &amp;&amp; &lt;PersonalStep state={state} dispatch={dispatch} /&gt;}
      {state.step === 1 &amp;&amp; &lt;AddressStep state={state} dispatch={dispatch} /&gt;}
      {state.step === 2 &amp;&amp; &lt;PaymentStep state={state} dispatch={dispatch} /&gt;}

      {/* Navigation */}
      &lt;div&gt;
        &lt;button onClick={back} disabled={state.step === 0}&gt;Back&lt;/button&gt;
        {state.step &lt; STEPS.length - 1
          ? &lt;button onClick={next}&gt;Next&lt;/button&gt;
          : &lt;button onClick={submit}&gt;Submit&lt;/button&gt;}
      &lt;/div&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Key architectural decisions:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td>Single accumulated state object</td><td>Going back doesn&rsquo;t lose data; final submit has everything</td></tr>
  <tr><td>useReducer over multiple useStates</td><td>Centralized transitions; easier to test reducer pure function</td></tr>
  <tr><td>Validate per step, not all at once</td><td>Don&rsquo;t block early steps for later step issues</td></tr>
  <tr><td>One step component per logical group</td><td>Easier to add/remove/reorder steps</td></tr>
  <tr><td>Persist state to localStorage (optional)</td><td>Survives accidental refresh on long forms</td></tr>
</table>

<p><strong>For production wizards</strong>: <strong>React Hook Form</strong> + <strong>Zod</strong> handles per-step schema validation cleanly &mdash; one Zod schema per step, validates before advancing. Pair with Framer Motion for slide transitions between steps. <strong>For very dynamic wizards</strong> (steps depend on previous answers), use a state machine library like <strong>XState</strong> &mdash; explicit state transitions prevent reaching impossible states.</p>

<p><strong>URL-driven wizards</strong>: store the current step in the URL (<code>/checkout/payment</code>). Users can refresh, share, or browser-back/forward through steps. Pair with React Router&rsquo;s nested routes for clean step components.</p>
'''

ANSWERS[76] = r'''
<p>Effective React debugging combines <strong>browser DevTools</strong>, <strong>React DevTools extension</strong>, source maps, and intentional logging strategies. The choice of tool depends on the bug class &mdash; render issues, state bugs, performance, async failures, or production errors all need different approaches.</p>

<p><strong>Toolkit by problem class:</strong></p>

<table>
  <tr><th>Problem</th><th>Primary tool</th></tr>
  <tr><td>Wrong UI rendered</td><td>React DevTools Components tab — inspect props/state/hooks; edit values live</td></tr>
  <tr><td>Unexpected re-renders</td><td>React DevTools Profiler — flamegraph + &ldquo;why did this render&rdquo;</td></tr>
  <tr><td>Slow interactions</td><td>Profiler + Performance tab + <code>why-did-you-render</code></td></tr>
  <tr><td>State doesn&rsquo;t update</td><td>DevTools Components — verify state. Check for stale closures, missing deps, mutation</td></tr>
  <tr><td>API/network failures</td><td>Network tab + console errors + Sentry breadcrumbs</td></tr>
  <tr><td>Infinite loops</td><td>Console &ldquo;Maximum update depth&rdquo; → check effect deps and setState in render</td></tr>
  <tr><td>Production-only bugs</td><td>Sentry/Datadog with source maps; LogRocket for session replay</td></tr>
</table>

<p><strong>Strict Mode in development</strong> intentionally double-invokes effects, reducers, and constructors to surface bugs that depend on these running once. If your effect breaks under Strict Mode, your effect has a bug, not Strict Mode. Production runs them once.</p>

<p><strong>Source maps</strong>: enable in production builds (Vite generates by default; Sentry uploads them) so stack traces reference your real source files instead of minified <code>main.[hash].js:1:99837</code>. Hide them from public download via <code>build.sourcemap: "hidden"</code> in Vite if security-sensitive.</p>

<p><strong>The <code>debugger</code> statement</strong> beats <code>console.log</code> for stepping through code paths &mdash; with DevTools open, execution pauses; you can inspect locals, walk the call stack, and resume. <strong>Conditional breakpoints</strong> in Sources tab are even better &mdash; pause only when <code>userId === 42</code>, no code edits needed.</p>

<p><strong>2026 production observability</strong>: <strong>Sentry</strong> (errors + performance), <strong>Datadog RUM</strong> (real user monitoring), <strong>LogRocket</strong> / <strong>FullStory</strong> (session replay) &mdash; together they catch the bugs you can&rsquo;t reproduce locally. Wire them in early, configure source map upload, and tag releases for diff visibility.</p>
'''

ANSWERS[77] = r'''
<p>Synchronizing state between multiple components requires choosing the right pattern based on <strong>distance</strong> (sibling, distant cousin, app-wide) and <strong>change frequency</strong>. Wrong choice creates either prop-drilling hell or unnecessary re-renders.</p>

<p><strong>The synchronization toolkit, by scope:</strong></p>

<table>
  <tr><th>Scope</th><th>Tool</th><th>Trade-off</th></tr>
  <tr><td>Parent &harr; child</td><td>Props + callbacks</td><td>Always works; verbose for deep trees</td></tr>
  <tr><td>Siblings</td><td>Lift state to common parent</td><td>Parent re-renders affect cousins</td></tr>
  <tr><td>Distant components</td><td>Context</td><td>Every consumer re-renders on context change</td></tr>
  <tr><td>App-wide, complex</td><td>Zustand / Redux Toolkit</td><td>External library; learning curve</td></tr>
  <tr><td>Server data</td><td>TanStack Query / SWR</td><td>Auto-syncs across all consumers via cache</td></tr>
  <tr><td>URL-driven</td><td>Search params (router)</td><td>Shareable, refresh-safe</td></tr>
  <tr><td>Cross-tab</td><td>BroadcastChannel / storage events</td><td>Same-origin only</td></tr>
</table>

<p><strong>Critical insight &mdash; don&rsquo;t put server data in client state</strong>. Storing API responses in Redux (then duplicating across components) means every consumer must implement its own refetch, cache invalidation, and stale-while-revalidate logic. <strong>TanStack Query</strong>&rsquo;s normalized cache automatically syncs all components reading the same query key &mdash; one mutation invalidates relevant queries everywhere.</p>

<p><strong>Cross-tab sync</strong> is overlooked but powerful: a user logs out in tab A; tabs B, C, D should also log out. <code>BroadcastChannel</code> sends messages to all same-origin tabs:</p>

<pre><code>const channel = new BroadcastChannel("auth");
// On logout:
channel.postMessage({ type: "LOGGED_OUT" });

// In every tab:
channel.onmessage = (e) =&gt; {
  if (e.data.type === "LOGGED_OUT") logoutLocally();
};</code></pre>

<p><strong>Deriving instead of synchronizing</strong>: if A and B should always show the same thing, don&rsquo;t store the same value twice and try to keep them in sync. Store it once; both components compute their view from that source. The bug class &ldquo;A and B disagreed&rdquo; disappears entirely when there&rsquo;s only one source of truth.</p>
'''

ANSWERS[78] = r'''
<p>The <strong>reducer pattern</strong> centralizes state updates into a pure function: <code>(state, action) =&gt; newState</code>. React exposes it via <code>useReducer</code> (component-local) and via Redux/RTK (app-wide). The pattern&rsquo;s strength is <strong>explicit state transitions</strong> &mdash; every change has a name and a single place where it&rsquo;s implemented.</p>

<p><strong>Three properties of a proper reducer:</strong></p>

<table>
  <tr><th>Property</th><th>Why</th></tr>
  <tr><td>Pure function</td><td>Same input → same output. Predictable, testable, time-travelable.</td></tr>
  <tr><td>Returns new state immutably</td><td>React relies on referential equality to detect changes. Mutation breaks rendering.</td></tr>
  <tr><td>No side effects</td><td>Effects (API calls, timers, logging) belong in middleware or effect hooks, not reducers.</td></tr>
</table>

<p><strong>When useReducer beats useState</strong>: state with multiple sub-values that update together (form state, wizard, cart); transitions that depend on previous state in non-trivial ways (toggling, filtering, undo); when the same logic spans many event handlers (centralize once); when state shape demands invariants (e.g., "<code>loading</code> and <code>data</code> can&rsquo;t both be set").</p>

<p><strong>Modern Redux Toolkit</strong> reduces reducer boilerplate dramatically. Mutations look mutable but Immer wraps them &mdash; the output is still immutable:</p>

<pre><code>const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    added(state, action) {
      state.push(action.payload);  // looks mutable, actually immutable via Immer
    },
    toggled(state, action) {
      const todo = state.find(t =&gt; t.id === action.payload);
      if (todo) todo.done = !todo.done;
    }
  }
});</code></pre>

<p><strong>Reducer + middleware composition</strong>: middleware sits between dispatch and reducer, enabling logging, async actions (Thunk), complex orchestration (Saga), or auto-generated server cache (RTK Query). The reducer stays pure; effects live in middleware.</p>

<p><strong>2026 reality</strong>: for new apps, default to <code>useReducer</code> for component-local complex state and <strong>Zustand</strong> for global state (lighter than Redux, similar pattern). Redux Toolkit remains the right choice for large apps with strong action-log requirements (audit trails, time-travel debugging, complex middleware ecosystems).</p>
'''

ANSWERS[79] = r'''
<p>Environment variables in React apps live in <strong><code>.env</code> files</strong>, are read at <strong>build time</strong> (not runtime), and require a <strong>build-tool prefix</strong> to reach client code. Misunderstanding any of these creates real bugs and security issues.</p>

<p><strong>Build-time vs runtime &mdash; the critical distinction</strong>: when you reference <code>import.meta.env.VITE_API_URL</code> in code, the bundler replaces it with the literal string at build time. Production builds bake in production env values. Same code can&rsquo;t use different env values across environments without rebuilding.</p>

<p><strong>The prefix system &mdash; required for security:</strong></p>

<table>
  <tr><th>Build tool</th><th>Client prefix</th><th>Access in code</th></tr>
  <tr><td>Vite</td><td><code>VITE_</code></td><td><code>import.meta.env.VITE_X</code></td></tr>
  <tr><td>CRA (deprecated)</td><td><code>REACT_APP_</code></td><td><code>process.env.REACT_APP_X</code></td></tr>
  <tr><td>Next.js</td><td><code>NEXT_PUBLIC_</code></td><td><code>process.env.NEXT_PUBLIC_X</code></td></tr>
  <tr><td>Next.js (server-only)</td><td>(no prefix)</td><td><code>process.env.X</code></td></tr>
</table>

<p>Variables without the prefix are NOT exposed to client bundles. This protects database credentials, API tokens, JWT secrets &mdash; if you accidentally name a server secret <code>VITE_DB_PASSWORD</code>, it ends up in your minified JS bundle, visible to anyone.</p>

<p><strong>File precedence</strong> (highest first): <code>.env.local</code> → <code>.env.development</code> / <code>.env.production</code> → <code>.env</code>. Commit <code>.env</code> with safe defaults; commit per-environment files; gitignore <code>.env.local</code> for personal/secret overrides.</p>

<p><strong>Safe vs unsafe to expose:</strong></p>

<table>
  <tr><th>Safe (client-side OK)</th><th>Unsafe (server-only)</th></tr>
  <tr><td>Public API URL</td><td>Database credentials, JWT signing key</td></tr>
  <tr><td>Stripe publishable key (<code>pk_live_*</code>)</td><td>Stripe secret key (<code>sk_live_*</code>)</td></tr>
  <tr><td>Google Analytics ID</td><td>Server-to-server API tokens</td></tr>
  <tr><td>Feature flag identifiers</td><td>OAuth client secrets</td></tr>
</table>

<p><strong>Runtime-mutable env</strong>: if you genuinely need different values per environment without rebuilding, ship a <code>/config.json</code> served by the host that the app fetches at startup. Or use a feature-flag service (LaunchDarkly, Statsig). Don&rsquo;t hack <code>window.__ENV</code> &mdash; it&rsquo;s a maintenance trap.</p>

<p><strong>TypeScript autocomplete</strong>: declare <code>ImportMetaEnv</code> in <code>vite-env.d.ts</code> with your variable types &mdash; misspellings and missing variables become compile errors. Production hosts (Vercel, Netlify) inject env values at build time from their dashboards; never commit production secrets to git, even in <code>.env.production</code>.</p>
'''

ANSWERS[80] = r'''
<p>Production error logging captures unhandled errors, sends them to a monitoring service with enough context to debug, and surfaces patterns through dashboards. <strong>Sentry</strong> dominates 2026; <strong>Datadog RUM</strong>, <strong>Bugsnag</strong>, and <strong>Rollbar</strong> are similar alternatives.</p>

<p><strong>What to capture for each error</strong>:</p>

<table>
  <tr><th>Field</th><th>Why</th></tr>
  <tr><td>Stack trace (with source maps)</td><td>Map minified errors back to source files</td></tr>
  <tr><td>User context (id, role)</td><td>Reproduce per-user; identify scope of impact</td></tr>
  <tr><td>Browser, OS, viewport</td><td>Spot platform-specific bugs</td></tr>
  <tr><td>Recent breadcrumbs</td><td>What user did before the error</td></tr>
  <tr><td>Network requests</td><td>Failed API calls right before the crash</td></tr>
  <tr><td>Release version + git SHA</td><td>When the bug was introduced</td></tr>
  <tr><td>Component stack (React)</td><td>Which component tree triggered it</td></tr>
</table>

<p><strong>Sentry setup with React</strong>:</p>

<pre><code>import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  release: __APP_VERSION__,             // injected at build
  environment: import.meta.env.MODE,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({ maskAllText: true })   // session replay
  ],
  tracesSampleRate: 0.1,                // 10% performance traces
  replaysSessionSampleRate: 0.1,        // 10% session replays
  replaysOnErrorSampleRate: 1.0,        // all sessions with errors
  beforeSend(event, hint) {
    // Filter noise — bot crawlers, expected errors
    if (hint.originalException?.message?.includes("ResizeObserver loop")) return null;
    return event;
  }
});

// Identify user after login
Sentry.setUser({ id: user.id, email: user.email });

// Wrap app with error boundary
const App = Sentry.withErrorBoundary(MyApp, {
  fallback: ErrorPage,
  beforeCapture: (scope) =&gt; scope.setTag("boundary", "root")
});</code></pre>

<p><strong>Layered error capture</strong>: error boundaries catch render errors; <code>window.onerror</code> + <code>onunhandledrejection</code> catch async failures; <code>fetch</code> wrapper catches HTTP errors with context. Sentry&rsquo;s SDK does most of this automatically &mdash; but you still need explicit error boundaries to render fallback UI (Sentry doesn&rsquo;t provide UX, just observability).</p>

<p><strong>Don&rsquo;t log everything</strong>: noisy errors (ResizeObserver loops, browser extension errors, network errors during navigation) drown out real bugs. Filter aggressively in <code>beforeSend</code>. Tag releases so you can compare error rates pre/post deploy. Set up alerts for new error types and rate spikes &mdash; the goal is "fewer surprises in production," not "more data."</p>

<p><strong>PII discipline</strong>: never log passwords, tokens, full credit card numbers. Sentry&rsquo;s data scrubbing helps, but defense-in-depth means not putting secrets into <code>console.log</code> calls in the first place. Many compliance frameworks (HIPAA, PCI) require this.</p>
'''

ANSWERS[81] = r'''
<p>Optimistic updates show the result of an action <strong>before</strong> the server confirms it &mdash; UI updates instantly, request fires in background, server response either confirms or rolls back. Critical for perceived performance: a "like" button that waits 200ms feels broken; one that updates instantly feels native.</p>

<p><strong>The pattern, in three steps:</strong></p>
<ol>
  <li><strong>Snapshot</strong> the current state.</li>
  <li><strong>Apply optimistic update</strong> immediately to local state.</li>
  <li><strong>Send request</strong>; on success leave it; on error revert to snapshot and notify user.</li>
</ol>

<p><strong>React 19&rsquo;s <code>useOptimistic</code> hook</strong>:</p>

<pre><code>import { useOptimistic, useState } from "react";

function LikeButton({ postId, initialLikes }) {
  const [likes, setLikes] = useState(initialLikes);
  const [optimisticLikes, addOptimisticLike] = useOptimistic(likes);

  const handleClick = async () =&gt; {
    addOptimisticLike(optimisticLikes + 1);   // instant UI update

    try {
      const newCount = await api.likePost(postId);
      setLikes(newCount);                      // confirm with server value
    } catch (err) {
      // useOptimistic auto-reverts on error or next render
      toast.error("Failed to like &mdash; please try again");
    }
  };

  return &lt;button onClick={handleClick}&gt;❤ {optimisticLikes}&lt;/button&gt;;
}</code></pre>

<p><strong>TanStack Query optimistic mutations</strong> (more powerful for cached lists):</p>

<pre><code>const mutation = useMutation({
  mutationFn: api.likePost,
  onMutate: async (postId) =&gt; {
    await queryClient.cancelQueries({ queryKey: ["posts"] });
    const previous = queryClient.getQueryData(["posts"]);

    queryClient.setQueryData(["posts"], (old) =&gt;
      old.map(p =&gt; p.id === postId ? { ...p, likes: p.likes + 1 } : p)
    );
    return { previous };
  },
  onError: (err, postId, context) =&gt; {
    // Rollback to previous data
    queryClient.setQueryData(["posts"], context.previous);
  },
  onSettled: () =&gt; queryClient.invalidateQueries({ queryKey: ["posts"] })
});</code></pre>

<p><strong>When to use optimistic updates:</strong></p>

<table>
  <tr><th>Good fit</th><th>Bad fit</th></tr>
  <tr><td>Likes, hearts, votes</td><td>Payment processing</td></tr>
  <tr><td>Adding/deleting list items</td><td>Form submissions with server validation</td></tr>
  <tr><td>Reordering, drag-and-drop</td><td>Anything with side effects (sending email)</td></tr>
  <tr><td>Toggle states (subscribe, follow)</td><td>Operations where rollback would confuse users</td></tr>
</table>

<p><strong>The hard part is rollback UX</strong>: if a like reverts after 2 seconds, users notice. Best to be conservative &mdash; show a toast explaining the failure, offer retry. For genuinely high-stakes operations (payments, deletions of important data), don&rsquo;t use optimistic updates &mdash; show a spinner and confirm on success. <strong>Reconciliation order matters</strong>: with concurrent likes from multiple tabs, the local optimistic count can diverge from server state; the <code>onSettled</code> refetch resolves this.</p>
'''

ANSWERS[82] = r'''
<p><strong>Memoization</strong> in React caches the result of a computation so it doesn&rsquo;t re-run when inputs haven&rsquo;t changed. The three primary tools: <strong><code>useMemo</code></strong> (cache values), <strong><code>useCallback</code></strong> (cache functions), and <strong><code>React.memo</code></strong> (skip re-render of a component). Each compares dependencies/props by reference equality.</p>

<p><strong>The three tools, side by side:</strong></p>

<table>
  <tr><th>Tool</th><th>Caches</th><th>Skips</th></tr>
  <tr><td><code>useMemo(fn, deps)</code></td><td>Return value of <code>fn</code></td><td>Re-running <code>fn</code> if deps unchanged</td></tr>
  <tr><td><code>useCallback(fn, deps)</code></td><td>Function reference</td><td>New function identity if deps unchanged</td></tr>
  <tr><td><code>React.memo(Component)</code></td><td>Component output</td><td>Re-render if props shallow-equal previous</td></tr>
</table>

<p><strong>Why all three exist together</strong>: stopping unnecessary renders requires referential stability through the chain. A memoized child only skips re-render when its props are <code>===</code> to the previous render. If the parent passes <code>{ a: 1, b: 2 }</code> as a prop, that&rsquo;s a new object every render &mdash; memo doesn&rsquo;t help. Wrap the object in <code>useMemo</code>; wrap callbacks in <code>useCallback</code>; the chain works.</p>

<pre><code>// All three working together
const Parent = ({ items }) =&gt; {
  const config = useMemo(() =&gt; ({ theme: "dark", ... }), []);
  const onSelect = useCallback((id) =&gt; { ... }, []);
  return &lt;ExpensiveList items={items} config={config} onSelect={onSelect} /&gt;;
};

const ExpensiveList = React.memo(({ items, config, onSelect }) =&gt; {
  // Only re-renders when items, config, or onSelect change by reference
});</code></pre>

<p><strong>Cost of memoization</strong>: every memoized value/function adds tracking overhead and dependency-array work. Memoization is only a net win when the work being skipped exceeds this overhead. For trivial calculations or components, manual memoization makes performance <em>worse</em>.</p>

<p><strong>Pitfalls</strong>:</p>
<ul>
  <li><strong>Missing deps</strong> &mdash; stale values, bugs that appear unpredictably. ESLint <code>react-hooks/exhaustive-deps</code> catches these.</li>
  <li><strong>Unstable deps</strong> &mdash; objects/arrays that change every render defeat memoization. Move them outside the component or memoize them too.</li>
  <li><strong>Custom equality functions</strong> &mdash; <code>React.memo</code> accepts a second argument for deep equality, but it&rsquo;s usually wrong. Match React&rsquo;s shallow-equal model; use stable references instead.</li>
</ul>

<p><strong>2026 reality</strong>: <strong>React Compiler</strong> (production-ready in React 19) auto-applies <code>useMemo</code>/<code>useCallback</code>/<code>memo</code> where beneficial. For new code with the compiler enabled, manual memoization is rarely needed &mdash; write naturally. For older codebases or compiler edge cases, the manual tools above remain essential. <strong>Profile before memoizing</strong>: React DevTools Profiler shows actual render times. Optimize what&rsquo;s actually slow, not what looks expensive.</p>
'''

ANSWERS[83] = r'''
<p><strong>Refs</strong> give you direct access to a DOM node or any mutable value that doesn&rsquo;t belong in render output. They escape React&rsquo;s declarative model intentionally &mdash; for the cases where it&rsquo;s the right tool: focus management, scrolling, measuring, integrating imperative third-party libraries, and persisting values across renders without triggering re-renders.</p>

<p><strong>The two ref shapes:</strong></p>

<table>
  <tr><th></th><th>Created by</th><th>Use for</th></tr>
  <tr><td>Simple ref</td><td><code>useRef(initial)</code></td><td>Single mutable value or DOM node</td></tr>
  <tr><td>Callback ref</td><td>Function passed to <code>ref</code> prop</td><td>Multiple nodes (e.g., dynamic list); reacting to mount/unmount</td></tr>
</table>

<p><strong>DOM access patterns</strong>:</p>

<pre><code>// Focus on mount
function AutofocusInput() {
  const inputRef = useRef(null);
  useEffect(() =&gt; { inputRef.current?.focus(); }, []);
  return &lt;input ref={inputRef} /&gt;;
}

// Scroll into view
function ScrollableList({ items, activeId }) {
  const refs = useRef(new Map());
  useEffect(() =&gt; {
    refs.current.get(activeId)?.scrollIntoView({ behavior: "smooth" });
  }, [activeId]);

  return items.map(item =&gt; (
    &lt;div
      key={item.id}
      ref={(el) =&gt; el ? refs.current.set(item.id, el) : refs.current.delete(item.id)}
    &gt;
      {item.text}
    &lt;/div&gt;
  ));
}

// Measure DOM
function MeasureBox() {
  const boxRef = useRef(null);
  const [size, setSize] = useState(null);
  useLayoutEffect(() =&gt; {
    const { width, height } = boxRef.current.getBoundingClientRect();
    setSize({ width, height });
  }, []);
  return &lt;div ref={boxRef}&gt;Box: {size?.width} × {size?.height}&lt;/div&gt;;
}</code></pre>

<p><strong>Ref vs state &mdash; when to choose which</strong>:</p>

<table>
  <tr><th>Use ref when</th><th>Use state when</th></tr>
  <tr><td>Value doesn&rsquo;t affect rendered output</td><td>Value affects what you render</td></tr>
  <tr><td>Updating shouldn&rsquo;t trigger render</td><td>Component should re-render on update</td></tr>
  <tr><td>Storing previous value, timer ID, mutable counter</td><td>User-visible counters, form fields, any UI state</td></tr>
</table>

<p><strong>Common imperative needs</strong>: third-party libraries that aren&rsquo;t React-aware (chart libs that need DOM, video players, autocomplete plugins, animation libs). Wrap them in a component that uses ref + <code>useEffect</code> to instantiate the library, and cleanup to destroy it.</p>

<p><strong>React 19 changes</strong>: <code>forwardRef</code> is no longer required; <code>ref</code> is now a regular prop. <code>useImperativeHandle</code> still exists for exposing curated APIs from a child to parent. <strong>Don&rsquo;t use refs to read state during render</strong> &mdash; that&rsquo;s a render bug waiting to happen. Refs are for side-effect interactions, not for sharing state across components (use state, context, or external store for that).</p>
'''

ANSWERS[84] = r'''
<p><strong><code>React.memo</code></strong> is a higher-order component that wraps a function component and skips re-rendering when its props are shallow-equal to the previous render. Used correctly, it eliminates wasted renders down expensive subtrees; used carelessly, it adds bookkeeping overhead with no benefit.</p>

<p><strong>How shallow comparison works</strong>: React compares each prop to its previous value with <code>Object.is</code>. Primitives (strings, numbers, booleans) compare by value &mdash; <code>"hello" === "hello"</code> is true. Objects/arrays/functions compare by reference &mdash; even <code>{ a: 1 } !== { a: 1 }</code>.</p>

<pre><code>const ExpensiveList = React.memo(function ExpensiveList({ items, onSelect }) {
  // Renders only when items or onSelect change by reference
  return items.map(item =&gt; (
    &lt;Row key={item.id} item={item} onSelect={onSelect} /&gt;
  ));
});</code></pre>

<p><strong>When React.memo helps:</strong></p>

<table>
  <tr><th>Scenario</th><th>Memo helps?</th></tr>
  <tr><td>Component re-renders often, but props rarely change</td><td>Yes &mdash; prime use case</td></tr>
  <tr><td>Component renders large/expensive subtree</td><td>Yes &mdash; if props are stable</td></tr>
  <tr><td>List item with stable item reference</td><td>Yes &mdash; classic optimization</td></tr>
  <tr><td>Component receives object/array props from non-memoized parent</td><td>No &mdash; new ref every render defeats memo</td></tr>
  <tr><td>Cheap component (a few elements)</td><td>No &mdash; comparison overhead exceeds savings</td></tr>
  <tr><td>Component renders different output every time anyway</td><td>No &mdash; nothing to skip</td></tr>
</table>

<p><strong>The memoization chain matters</strong>: <code>React.memo</code> on a child requires stable props from the parent. If parent passes <code>{ filter: search }</code> as a prop, that&rsquo;s a new object every render. Wrap with <code>useMemo</code>:</p>

<pre><code>// Parent
const filterConfig = useMemo(() =&gt; ({ filter: search }), [search]);
return &lt;ExpensiveList items={items} config={filterConfig} /&gt;;</code></pre>

<p>Same with callbacks &mdash; wrap them in <code>useCallback</code> to maintain reference stability.</p>

<p><strong>Custom equality function</strong> &mdash; second argument to <code>React.memo</code>:</p>

<pre><code>React.memo(Component, (prevProps, nextProps) =&gt; {
  return prevProps.user.id === nextProps.user.id;   // skip if same user
});</code></pre>

<p>Only reach for this when you have specific knowledge that shallow equality is wrong for your component (e.g., comparing only the id field of a deeply-nested object). Most cases should pass shallow equality and structure props for stability.</p>

<p><strong>2026 with React Compiler</strong>: the compiler auto-applies <code>memo</code> equivalents where beneficial &mdash; manual <code>React.memo</code> often becomes unnecessary in compiler-enabled projects. For older code or compiler edge cases, it remains the right tool. <strong>Profile first</strong>: React DevTools Profiler&rsquo;s &ldquo;Highlight updates when components render&rdquo; setting shows which components are re-rendering. Optimize what&rsquo;s actually re-rendering wastefully &mdash; don&rsquo;t add <code>React.memo</code> to everything &ldquo;for safety.&rdquo;</p>
'''

ANSWERS[85] = r'''
<p>Data fetching in SSR has two phases: <strong>fetch on server</strong> (during HTML generation) and <strong>hydrate on client</strong> (continue interaction). The challenge is avoiding double-fetch (server fetched, client refetches) while keeping data fresh. <strong>Next.js App Router</strong> with React Server Components is the dominant 2026 solution.</p>

<p><strong>The four primary data-fetching strategies in Next.js (2026):</strong></p>

<table>
  <tr><th>Strategy</th><th>When data fetches</th><th>Use for</th></tr>
  <tr><td>Server Components</td><td>On server, per request</td><td>User-specific pages, dashboards (default in App Router)</td></tr>
  <tr><td>Static generation</td><td>At build time</td><td>Marketing pages, blogs, docs</td></tr>
  <tr><td>ISR (revalidate)</td><td>Cached, regenerated periodically</td><td>Mostly-static with infrequent updates</td></tr>
  <tr><td>Client fetching (TanStack Query/SWR)</td><td>In browser after hydration</td><td>Interactive data, frequent updates, post-load</td></tr>
</table>

<p><strong>Server Components &mdash; the modern default</strong>:</p>

<pre><code>// app/dashboard/page.tsx — runs on server
async function DashboardPage() {
  const user = await getCurrentUser();
  const stats = await fetch(`https://api/stats/${user.id}`, {
    next: { revalidate: 60 }   // cache for 60s
  }).then(r =&gt; r.json());

  return (
    &lt;&gt;
      &lt;h1&gt;Hello, {user.name}&lt;/h1&gt;
      &lt;Stats data={stats} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>No client-side <code>useEffect</code>; no loading state; no API endpoint; just fetch in the component. Data ships embedded in the HTML; the bundle stays smaller (no fetch logic on client).</p>

<p><strong>Combining server and client fetching</strong>: server renders the initial state; <strong>TanStack Query</strong> hydrates on the client and continues with cache + background refetch. This is the production sweet spot:</p>

<pre><code>// Server Component
export default async function Page() {
  const queryClient = new QueryClient();
  await queryClient.prefetchQuery({
    queryKey: ["posts"],
    queryFn: fetchPosts
  });

  return (
    &lt;HydrationBoundary state={dehydrate(queryClient)}&gt;
      &lt;PostList /&gt;     {/* client component reads cached data via useQuery */}
    &lt;/HydrationBoundary&gt;
  );
}</code></pre>

<p><strong>Streaming with Suspense</strong>: server starts sending HTML before all data resolves; sections of the page reveal as their data becomes ready. Eliminates the all-or-nothing wait that classic SSR had.</p>

<p><strong>Pitfalls to avoid</strong>: don&rsquo;t fetch sensitive data in pre-rendered HTML (it ships to all users); don&rsquo;t use Server Components for data that changes per-keystroke (that&rsquo;s client work); don&rsquo;t block initial render on slow third-party APIs &mdash; use <code>&lt;Suspense&gt;</code> boundaries to isolate them. <strong>Cache strategy</strong> matters: <code>force-cache</code> for build-time-stable data, <code>no-store</code> for real-time, <code>revalidate: N</code> for ISR. The right policy per fetch is the difference between fast and slow apps.</p>
'''

ANSWERS[86] = r'''
<p>Search functionality has three implementations of increasing power: <strong>client-side filter</strong> (small datasets), <strong>debounced API search</strong> (medium datasets), and <strong>dedicated search service</strong> (large datasets, full-text, fuzzy matching, relevance ranking).</p>

<p><strong>Decision matrix:</strong></p>

<table>
  <tr><th>Dataset size</th><th>Approach</th><th>Tools</th></tr>
  <tr><td>&lt; 1,000 items</td><td>Client-side filter</td><td><code>Array.filter</code> + <code>useMemo</code></td></tr>
  <tr><td>1,000 - 100,000 items</td><td>Client-side fuzzy search</td><td><code>Fuse.js</code>, <code>fast-fuzzy</code></td></tr>
  <tr><td>100,000+ items, server-backed</td><td>Backend search endpoint</td><td>SQL <code>LIKE</code> / <code>tsvector</code> (Postgres)</td></tr>
  <tr><td>Millions+ items, full-text</td><td>Dedicated search engine</td><td>Algolia, Elasticsearch, Typesense, Meilisearch</td></tr>
</table>

<p><strong>Pattern 1 &mdash; client-side filter with debounce + useDeferredValue</strong>:</p>

<pre><code>function SearchableList({ items }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);

  const results = useMemo(() =&gt; {
    if (!deferredQuery) return items;
    const q = deferredQuery.toLowerCase();
    return items.filter(item =&gt;
      item.name.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q)
    );
  }, [items, deferredQuery]);

  return (
    &lt;&gt;
      &lt;input value={query} onChange={e =&gt; setQuery(e.target.value)} /&gt;
      &lt;p&gt;{results.length} results&lt;/p&gt;
      &lt;ul&gt;{results.map(r =&gt; &lt;li key={r.id}&gt;{r.name}&lt;/li&gt;)}&lt;/ul&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong><code>useDeferredValue</code></strong> keeps the input snappy while the expensive filter operation runs in the background &mdash; React prioritizes the input update.</p>

<p><strong>Pattern 2 &mdash; debounced server-side search with TanStack Query</strong>:</p>

<pre><code>function ServerSearch() {
  const [query, setQuery] = useState("");
  const [debouncedQuery] = useDebounce(query, 300);

  const { data, isFetching } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: () =&gt; fetch(`/api/search?q=${debouncedQuery}`).then(r =&gt; r.json()),
    enabled: debouncedQuery.length &gt;= 2,
    placeholderData: keepPreviousData    // smooth typing experience
  });

  return (
    &lt;&gt;
      &lt;input value={query} onChange={e =&gt; setQuery(e.target.value)} /&gt;
      {isFetching &amp;&amp; &lt;Spinner /&gt;}
      &lt;Results items={data || []} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Pattern 3 &mdash; Algolia for production search at scale</strong>:</p>

<pre><code>import { InstantSearch, SearchBox, Hits } from "react-instantsearch";
import { liteClient as algoliasearch } from "algoliasearch/lite";

const searchClient = algoliasearch("APP_ID", "SEARCH_KEY");

function App() {
  return (
    &lt;InstantSearch searchClient={searchClient} indexName="products"&gt;
      &lt;SearchBox /&gt;
      &lt;Hits hitComponent={ProductHit} /&gt;
    &lt;/InstantSearch&gt;
  );
}</code></pre>

<p>Algolia gives sub-50ms typo-tolerant search, faceting, geo, and analytics out of the box. Index your data; Algolia handles ranking. <strong>Self-hostable alternatives</strong>: Meilisearch (modern, fast, simple), Typesense (similar feature set), Elasticsearch (powerful but operational complexity).</p>

<p><strong>UX details that matter</strong>: keep input controlled and instant; show fetching state distinct from empty results; preserve previous results during refetch (don&rsquo;t flash); URL-sync the query for shareable searches; show "no results for X" with suggestions; handle null/empty input states; throttle requests; cancel stale requests (TanStack Query auto-handles this via query keys).</p>
'''

ANSWERS[87] = r'''
<p><strong>Portals</strong> render a child into a DOM node outside the parent component&rsquo;s DOM hierarchy. The component still belongs to the React tree (state, context, events bubble up); only the DOM placement changes. Essential for modals, tooltips, popovers, toasts, and dropdowns that need to escape parent <code>overflow</code>, <code>z-index</code>, or <code>transform</code> contexts.</p>

<p><strong>The mechanism</strong>:</p>

<pre><code>import { createPortal } from "react-dom";

function Modal({ children, onClose }) {
  return createPortal(
    &lt;div className="overlay" onClick={onClose}&gt;
      &lt;div className="dialog" onClick={e =&gt; e.stopPropagation()}&gt;
        {children}
      &lt;/div&gt;
    &lt;/div&gt;,
    document.body                  // render target
  );
}

// Usage anywhere in the tree
function ProductCard() {
  const [open, setOpen] = useState(false);
  return (
    &lt;article&gt;
      &lt;button onClick={() =&gt; setOpen(true)}&gt;Quick view&lt;/button&gt;
      {open &amp;&amp; (
        &lt;Modal onClose={() =&gt; setOpen(false)}&gt;
          &lt;h2&gt;Product details&lt;/h2&gt;
        &lt;/Modal&gt;
      )}
    &lt;/article&gt;
  );
}</code></pre>

<p><strong>Why portals exist &mdash; the CSS escape problem</strong>: a modal nested inside a card with <code>overflow: hidden</code> and <code>z-index: 0</code> can&rsquo;t escape those constraints. The modal gets clipped or appears behind other content. Portal moves the DOM node to <code>document.body</code> where neither constraint applies.</p>

<p><strong>What stays the same vs what changes:</strong></p>

<table>
  <tr><th>Same as if not portal</th><th>Different</th></tr>
  <tr><td>React tree (state, context, parent re-renders)</td><td>DOM hierarchy</td></tr>
  <tr><td>Event bubbling (events bubble through React tree)</td><td>CSS inheritance from new DOM parent</td></tr>
  <tr><td>Refs to portal contents</td><td>z-index stacking context</td></tr>
</table>

<p><strong>The event-bubbling subtlety</strong>: events bubble through the <strong>React</strong> tree, not the DOM tree. A click in a modal portal'd to <code>body</code> still fires <code>onClick</code> handlers on the parent component that rendered the modal. This is sometimes confusing (debug-wise) but usually what you want for state management.</p>

<p><strong>Modern alternatives in 2026</strong>:</p>

<table>
  <tr><th>Option</th><th>When</th></tr>
  <tr><td><code>&lt;dialog&gt;</code> element + <code>showModal()</code></td><td>Native browser modals; built-in focus trap and Escape; ARIA</td></tr>
  <tr><td>Popover API (<code>popover</code> attribute)</td><td>Tooltips, dropdowns; native positioning</td></tr>
  <tr><td>Radix UI Dialog / Popover</td><td>Production: full a11y, focus management, animations</td></tr>
  <tr><td>shadcn/ui Dialog</td><td>Tailwind-styled Radix wrapper</td></tr>
  <tr><td>Floating UI</td><td>Smart positioning (collision detection, viewport awareness)</td></tr>
</table>

<p><strong>Don&rsquo;t roll your own modal in production</strong>: focus trapping, return-focus on close, ARIA roles, scroll locking, escape handling, and click-outside detection are subtle. Libraries get this right; hand-rolled modals usually don&rsquo;t. The portal is just one piece of a proper modal &mdash; the rest is significant a11y plumbing.</p>
'''

ANSWERS[88] = r'''
<p>Hooks unify what class components did across <code>state</code>, <code>componentDidMount</code>, <code>componentDidUpdate</code>, and <code>componentWillUnmount</code>. The mental model shifts from "lifecycle phases" to "synchronizing with external systems via effects."</p>

<p><strong>The lifecycle equivalents:</strong></p>

<table>
  <tr><th>Class component</th><th>Hooks equivalent</th></tr>
  <tr><td><code>this.state</code> + <code>this.setState</code></td><td><code>useState</code></td></tr>
  <tr><td>Complex state with multiple keys</td><td><code>useReducer</code></td></tr>
  <tr><td><code>componentDidMount</code></td><td><code>useEffect(() =&gt; {...}, [])</code></td></tr>
  <tr><td><code>componentDidUpdate</code> (any prop/state)</td><td><code>useEffect(() =&gt; {...})</code> (no array)</td></tr>
  <tr><td><code>componentDidUpdate</code> (specific prop)</td><td><code>useEffect(() =&gt; {...}, [prop])</code></td></tr>
  <tr><td><code>componentWillUnmount</code></td><td><code>useEffect</code> cleanup function</td></tr>
  <tr><td><code>componentDidMount</code> + <code>componentWillUnmount</code></td><td>Single <code>useEffect</code> with setup + cleanup</td></tr>
  <tr><td><code>shouldComponentUpdate</code> / <code>PureComponent</code></td><td><code>React.memo</code></td></tr>
  <tr><td><code>getDerivedStateFromProps</code></td><td>Compute during render; memo with <code>useMemo</code></td></tr>
  <tr><td><code>componentDidCatch</code></td><td>(none yet &mdash; still need class for error boundaries)</td></tr>
</table>

<p><strong>The unifying pattern &mdash; useEffect for setup + cleanup together</strong>:</p>

<pre><code>// Class — split across lifecycle methods
class Chat extends Component {
  componentDidMount()    { this.subscription = api.subscribe(this.props.userId); }
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.subscription.unsubscribe();
      this.subscription = api.subscribe(this.props.userId);
    }
  }
  componentWillUnmount() { this.subscription.unsubscribe(); }
}

// Hook — co-located in one effect
function Chat({ userId }) {
  useEffect(() =&gt; {
    const subscription = api.subscribe(userId);
    return () =&gt; subscription.unsubscribe();
  }, [userId]);
}</code></pre>

<p><strong>Why this is better</strong>: setup + cleanup live next to each other; the dependency array makes the &ldquo;when does this re-run&rdquo; question explicit; you can&rsquo;t forget to unsubscribe (the <em>same</em> effect handles both setup and teardown).</p>

<p><strong>Subtle differences to know</strong>:</p>
<ul>
  <li><strong>Effects run after paint</strong>; <code>componentDidMount</code> runs after commit but before paint. Use <code>useLayoutEffect</code> for the latter behavior.</li>
  <li><strong>State is replaced, not merged</strong> &mdash; <code>setState({a: 1})</code> in classes merged; <code>setState({a: 1})</code> with hooks replaces. Use spread or <code>useReducer</code>.</li>
  <li><strong>Closures capture values</strong> &mdash; <code>useState</code> in handlers/timers captures the value at render time. Use updater form (<code>setX(prev =&gt; ...)</code>) or refs to avoid stale values.</li>
  <li><strong>Strict Mode double-invokes</strong> effects in development &mdash; surfaces missing cleanups or race conditions.</li>
</ul>

<p><strong>2026 reality</strong>: hooks are the primary API for React; class components are largely legacy. New code should be functional + hooks. The only place classes remain necessary is error boundaries (no hook equivalent yet, though discussed for future versions). Even legacy codebases mostly migrate gradually &mdash; you don&rsquo;t need to rewrite everything at once; functional and class components interoperate freely.</p>
'''

ANSWERS[89] = r'''
<p>Context-based state management uses React&rsquo;s built-in <strong>Context API</strong> + a state primitive (<code>useState</code> or <code>useReducer</code>) to share state across many components without prop-drilling. It&rsquo;s the simplest path to global state &mdash; no extra library &mdash; but has performance characteristics that make it suitable only for low-frequency updates.</p>

<p><strong>The pattern (Context + useReducer):</strong></p>

<pre><code>const StateContext = createContext(null);
const DispatchContext = createContext(null);

function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    &lt;StateContext.Provider value={state}&gt;
      &lt;DispatchContext.Provider value={dispatch}&gt;
        {children}
      &lt;/DispatchContext.Provider&gt;
    &lt;/StateContext.Provider&gt;
  );
}

const useAppState = () =&gt; useContext(StateContext);
const useAppDispatch = () =&gt; useContext(DispatchContext);</code></pre>

<p><strong>Splitting state and dispatch into two contexts</strong>: components that only dispatch (don&rsquo;t need to read state) won&rsquo;t re-render when state changes. This is a critical optimization &mdash; otherwise the entire subtree re-renders on every state change.</p>

<p><strong>Performance characteristics:</strong></p>

<table>
  <tr><th>Trade-off</th><th>Detail</th></tr>
  <tr><td>Every consumer re-renders on context change</td><td>No selectors; <code>useContext</code> always re-renders on value change</td></tr>
  <tr><td>Value must be referentially stable</td><td>New object every render = all consumers re-render</td></tr>
  <tr><td>No middleware</td><td>No undo/redo, no async helpers, no devtools by default</td></tr>
  <tr><td>No normalization</td><td>Manual cache management; data duplication risk</td></tr>
</table>

<p><strong>When Context-based state works well:</strong></p>
<ul>
  <li>Low-frequency app-wide state &mdash; theme, current user, locale, feature flags.</li>
  <li>Form state for a specific multi-step flow.</li>
  <li>Scoped state for a feature (e.g., a complex table&rsquo;s filter/sort/select state).</li>
</ul>

<p><strong>When to upgrade to a state library:</strong></p>

<table>
  <tr><th>Library</th><th>Use case</th></tr>
  <tr><td>Zustand</td><td>Lightweight global state with selective subscriptions; minimal boilerplate</td></tr>
  <tr><td>Jotai</td><td>Atomic state &mdash; small composable pieces; great for derived state</td></tr>
  <tr><td>Redux Toolkit</td><td>Complex apps with strong action-log requirements, time-travel, middleware ecosystem</td></tr>
  <tr><td>Valtio</td><td>Proxy-based; mutate-style API; good for game state and editors</td></tr>
</table>

<p><strong>Selective subscription is the key benefit of state libraries over Context</strong>:</p>

<pre><code>// Zustand — only re-renders when count changes (not when other state changes)
const count = useStore(state =&gt; state.count);

// Equivalent Context behavior would require splitting state into many contexts</code></pre>

<p><strong>2026 default for new apps</strong>: <strong>Zustand</strong> for client state, <strong>TanStack Query</strong> for server state, <strong>Context</strong> for theme/auth/locale (low-frequency). Redux remains common in large existing apps. Don&rsquo;t over-engineer &mdash; many apps run perfectly with just <code>useState</code> + Context for the bits that genuinely need to be global.</p>
'''

ANSWERS[90] = r'''
<p>TypeScript transforms React DX from "hope I got the props right" to "compiler tells me what&rsquo;s wrong before I run the code." It catches missing props, wrong types, undefined accesses, and renames refactor-safely. In 2026, TypeScript is the default for production React codebases.</p>

<p><strong>The five biggest wins:</strong></p>

<table>
  <tr><th>Win</th><th>What it catches</th></tr>
  <tr><td>Component props</td><td>Missing required props, wrong types, typos in prop names</td></tr>
  <tr><td>Hook returns</td><td><code>useQuery</code> data shape, <code>useState</code> setter signatures</td></tr>
  <tr><td>Event handlers</td><td><code>e.target.value</code> type, correct event types</td></tr>
  <tr><td>API responses</td><td>Match types between frontend and backend</td></tr>
  <tr><td>Refactors</td><td>Rename a prop → all usages updated; missing one → error</td></tr>
</table>

<p><strong>Component prop typing patterns</strong>:</p>

<pre><code>// Basic props with types
type ButtonProps = {
  label: string;
  onClick: () =&gt; void;
  variant?: "primary" | "secondary";   // discriminated union
  disabled?: boolean;
  children?: React.ReactNode;
};

function Button({ label, onClick, variant = "primary", disabled }: ButtonProps) {
  return (
    &lt;button onClick={onClick} disabled={disabled} className={`btn-${variant}`}&gt;
      {label}
    &lt;/button&gt;
  );
}

// Generic components — flexible types per usage
type ListProps&lt;T&gt; = {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
  keyExtractor: (item: T) =&gt; string;
};

function List&lt;T&gt;({ items, renderItem, keyExtractor }: ListProps&lt;T&gt;) {
  return (
    &lt;ul&gt;
      {items.map(item =&gt; (
        &lt;li key={keyExtractor(item)}&gt;{renderItem(item)}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>Hooks with TypeScript</strong>:</p>

<pre><code>// Inferred state types
const [count, setCount] = useState(0);            // count: number
const [user, setUser] = useState&lt;User | null&gt;(null);   // explicit when null

// useReducer with typed actions
type Action =
  | { type: "INCREMENT" }
  | { type: "SET_COUNT"; value: number };

const [state, dispatch] = useReducer(reducer, { count: 0 });
// dispatch({ type: "WRONG" });  ← compile error

// useRef with DOM type
const inputRef = useRef&lt;HTMLInputElement&gt;(null);
inputRef.current?.focus();</code></pre>

<p><strong>Event types &mdash; the cheat sheet</strong>:</p>

<pre><code>onClick: (e: React.MouseEvent&lt;HTMLButtonElement&gt;) =&gt; void
onChange: (e: React.ChangeEvent&lt;HTMLInputElement&gt;) =&gt; void
onSubmit: (e: React.FormEvent&lt;HTMLFormElement&gt;) =&gt; void
onKeyDown: (e: React.KeyboardEvent&lt;HTMLInputElement&gt;) =&gt; void</code></pre>

<p><strong>Inferring API types from Zod schemas</strong>:</p>

<pre><code>const userSchema = z.object({ id: z.string(), name: z.string() });
type User = z.infer&lt;typeof userSchema&gt;;
// User: { id: string; name: string }</code></pre>

<p>One source of truth &mdash; runtime validation + compile-time types.</p>

<p><strong>2026 TypeScript practices</strong>: prefer <code>type</code> over <code>interface</code> (more flexible composability); avoid <code>any</code> &mdash; use <code>unknown</code> for genuinely-unknown values; enable <code>strict</code> mode (<code>strictNullChecks</code> alone eliminates most null-related crashes); use <code>satisfies</code> for type-checked literals without losing inference. <strong>For tooling</strong>: TypeScript&rsquo;s LSP integration with VSCode/Cursor gives autocomplete, inline error feedback, and hover docs &mdash; the IDE experience is dramatically better than plain JS.</p>
'''

ANSWERS[91] = r'''
<p>Internationalization (i18n) makes a React app render correctly across locales: translated strings, locale-appropriate number/date/currency formats, RTL layouts, pluralization rules, and date math. The dominant 2026 library is <strong>react-i18next</strong>; <strong>FormatJS / react-intl</strong> and <strong>Lingui</strong> are alternatives.</p>

<p><strong>What i18n encompasses (it&rsquo;s more than translations):</strong></p>

<table>
  <tr><th>Concern</th><th>Tool</th></tr>
  <tr><td>String translation</td><td>i18next, FormatJS, Lingui</td></tr>
  <tr><td>Plurals (1 item / 2 items / 0 items)</td><td>ICU MessageFormat (built-in)</td></tr>
  <tr><td>Number/currency/date formatting</td><td>Native <code>Intl</code> APIs</td></tr>
  <tr><td>Right-to-left languages (Arabic, Hebrew)</td><td>CSS logical properties + <code>dir="rtl"</code></td></tr>
  <tr><td>Locale-aware sort/compare</td><td><code>Intl.Collator</code></td></tr>
  <tr><td>Time zones</td><td><code>Intl.DateTimeFormat</code> + Temporal API (when available)</td></tr>
</table>

<p><strong>react-i18next setup</strong>:</p>

<pre><code>import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import HttpBackend from "i18next-http-backend";

i18n
  .use(HttpBackend)               // load from /locales/{lng}/{ns}.json
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    supportedLngs: ["en", "es", "fr", "de", "ja", "ar"],
    interpolation: { escapeValue: false }   // React handles escaping
  });</code></pre>

<pre><code>// /public/locales/en/common.json
{
  "welcome": "Hello, {{name}}!",
  "items": "{{count}} item",
  "items_plural": "{{count}} items",
  "items_zero": "No items"
}

// Component
import { useTranslation } from "react-i18next";

function Greeting() {
  const { t, i18n } = useTranslation();

  return (
    &lt;&gt;
      &lt;p&gt;{t("welcome", { name: "Alice" })}&lt;/p&gt;
      &lt;p&gt;{t("items", { count: 5 })}&lt;/p&gt;

      &lt;select onChange={e =&gt; i18n.changeLanguage(e.target.value)}&gt;
        &lt;option value="en"&gt;English&lt;/option&gt;
        &lt;option value="es"&gt;Español&lt;/option&gt;
        &lt;option value="ja"&gt;日本語&lt;/option&gt;
      &lt;/select&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Use native Intl for formatting</strong> (don&rsquo;t put numbers/dates into translation strings):</p>

<pre><code>// Currency
new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(1234.56);
// "$1,234.56"

new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(1234.56);
// "1.234,56 €"

// Dates
new Intl.DateTimeFormat("ja-JP", { dateStyle: "long" }).format(new Date());
// "2026年4月27日"

// Relative time
new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(-1, "day");
// "yesterday"</code></pre>

<p><strong>RTL support with logical properties</strong>:</p>

<pre><code>/* Use logical properties — they auto-flip in RTL */
.card {
  margin-inline-start: 16px;   /* left in LTR, right in RTL */
  padding-inline: 12px;        /* horizontal padding both sides */
  text-align: start;            /* left in LTR, right in RTL */
  border-inline-end: 1px solid #ddd;
}

/* In React */
&lt;html lang={i18n.language} dir={i18n.dir()}&gt;</code></pre>

<p><strong>2026 best practices</strong>: keep translation keys descriptive (<code>"checkout.payment.cardNumberLabel"</code>, not <code>"label1"</code>); collaborate with translators via TMS like Lokalise, Crowdin, Phrase; lazy-load translation namespaces by route to keep initial bundle small; use <code>Intl</code> for everything formatting-related; test with pseudo-locales (<code>en-XA</code>) to catch hardcoded strings. <strong>Next.js 15+</strong> has first-class i18n via App Router segments per locale.</p>
'''

ANSWERS[92] = r'''
<p>React&rsquo;s <strong>concurrent features</strong> (React 18+) let React interrupt, prioritize, and batch renders intelligently &mdash; keeping the UI responsive even during expensive updates. The key APIs are <code>useTransition</code>, <code>useDeferredValue</code>, <code>Suspense</code>, and the <code>use()</code> hook (React 19+).</p>

<p><strong>The five primary concurrent APIs:</strong></p>

<table>
  <tr><th>API</th><th>Purpose</th></tr>
  <tr><td><code>useTransition</code></td><td>Mark a state update as low-priority &mdash; UI stays responsive during expensive renders</td></tr>
  <tr><td><code>useDeferredValue</code></td><td>Use a stale version of a value while a new version renders in background</td></tr>
  <tr><td><code>&lt;Suspense&gt;</code></td><td>Wait for async work (data, code) before rendering; show fallback in meantime</td></tr>
  <tr><td><code>use(promise)</code></td><td>React 19+: read promises directly with Suspense for async data</td></tr>
  <tr><td><code>useActionState</code></td><td>React 19+: form actions with built-in pending state</td></tr>
</table>

<p><strong>useTransition &mdash; the killer use case for typing in big lists</strong>:</p>

<pre><code>function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(allItems);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) =&gt; {
    setQuery(e.target.value);    // urgent — input must update instantly

    startTransition(() =&gt; {
      // expensive — can be interrupted by next keystroke
      setResults(filterAndRank(allItems, e.target.value));
    });
  };

  return (
    &lt;&gt;
      &lt;input value={query} onChange={handleChange} /&gt;
      {isPending &amp;&amp; &lt;Spinner /&gt;}
      &lt;ResultList items={results} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>Without <code>useTransition</code>, fast typing freezes the input until each filter completes. With it, React abandons the in-progress filter when a new keystroke arrives &mdash; input stays snappy.</p>

<p><strong>useDeferredValue &mdash; similar but works at consumer side</strong>:</p>

<pre><code>function SearchPage() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);

  // Heavy work uses deferredQuery — runs at low priority
  const results = useMemo(() =&gt; filterItems(allItems, deferredQuery), [deferredQuery]);

  return (
    &lt;&gt;
      &lt;input value={query} onChange={e =&gt; setQuery(e.target.value)} /&gt;
      &lt;ResultList items={results} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>When you can&rsquo;t control the setter (e.g., the filter is in a child receiving a prop), <code>useDeferredValue</code> defers re-rendering downstream while keeping the input&rsquo;s render urgent.</p>

<p><strong>The <code>use()</code> hook (React 19) &mdash; promises in components</strong>:</p>

<pre><code>function PostList({ postsPromise }) {
  const posts = use(postsPromise);   // suspends until promise resolves
  return &lt;ul&gt;{posts.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}&lt;/ul&gt;;
}

function App() {
  const promise = fetchPosts();
  return (
    &lt;Suspense fallback={&lt;Spinner /&gt;}&gt;
      &lt;PostList postsPromise={promise} /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p>Eliminates the loading-state ceremony &mdash; just <code>use(promise)</code>; Suspense handles the rest.</p>

<p><strong>Streaming SSR with Suspense</strong>: server starts sending HTML before all data resolves; sections of the page reveal progressively as their data becomes ready. This is what powers Next.js App Router&rsquo;s streaming model.</p>

<p><strong>When NOT to reach for these features</strong>: small lists, simple components, anything where rendering is already fast. Concurrent features add cognitive overhead; only use them where they solve a real responsiveness problem. Profile first &mdash; the React DevTools Profiler shows actual render times.</p>
'''

ANSWERS[93] = r'''
<p>Controlled forms have React state hold the input value; uncontrolled forms let the DOM hold it and read on submit. Both are valid; the choice depends on whether you need to <strong>react to every keystroke</strong> or just <strong>collect the final values</strong>.</p>

<p><strong>The decision framework:</strong></p>

<table>
  <tr><th></th><th>Controlled</th><th>Uncontrolled</th></tr>
  <tr><td>Source of truth</td><td>React state</td><td>DOM</td></tr>
  <tr><td>Read value via</td><td>State variable</td><td>Ref or FormData</td></tr>
  <tr><td>Re-renders per keystroke</td><td>Yes</td><td>No</td></tr>
  <tr><td>Validate as user types</td><td>Easy</td><td>Awkward</td></tr>
  <tr><td>Conditionally enable/disable based on input</td><td>Easy</td><td>Awkward</td></tr>
  <tr><td>Performance for huge forms</td><td>Slower (re-renders)</td><td>Faster</td></tr>
  <tr><td>React Hook Form default</td><td>(Optional)</td><td>Yes &mdash; for performance</td></tr>
</table>

<p><strong>Controlled &mdash; canonical pattern</strong>:</p>

<pre><code>function ControlledForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  return (
    &lt;form onSubmit={(e) =&gt; { e.preventDefault(); save({ name, email }); }}&gt;
      &lt;input value={name} onChange={e =&gt; setName(e.target.value)} /&gt;
      &lt;input value={email} onChange={e =&gt; setEmail(e.target.value)} /&gt;

      {/* Easy to react to state changes */}
      &lt;button disabled={!name || !email}&gt;Submit&lt;/button&gt;

      &lt;p&gt;Hi {name || "stranger"}!&lt;/p&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Uncontrolled &mdash; with refs</strong>:</p>

<pre><code>function UncontrolledForm() {
  const nameRef = useRef(null);
  const emailRef = useRef(null);

  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    save({
      name: nameRef.current.value,
      email: emailRef.current.value
    });
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input ref={nameRef} defaultValue="" /&gt;
      &lt;input ref={emailRef} defaultValue="" /&gt;
      &lt;button&gt;Submit&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Uncontrolled &mdash; with FormData (cleaner for many fields)</strong>:</p>

<pre><code>function FormDataForm() {
  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    save(data);   // { name: "...", email: "..." }
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input name="name" defaultValue="" /&gt;
      &lt;input name="email" defaultValue="" /&gt;
      &lt;button&gt;Submit&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>The middle path &mdash; React Hook Form</strong>: registers inputs as uncontrolled (no re-renders on keystroke) but provides validation, error tracking, and dirty-state observation. Best of both worlds &mdash; performance of uncontrolled with the ergonomics of controlled.</p>

<pre><code>const { register, handleSubmit, formState: { errors } } = useForm();

&lt;input {...register("email", { required: true })} /&gt;</code></pre>

<p><strong>React 19 form actions</strong> (<code>useActionState</code>) shift more work to the form action receiving FormData &mdash; aligning with Server Actions in Next.js. Components stay simple; logic moves to async functions that take FormData and return state.</p>

<p><strong>2026 recommendation</strong>: small forms with reactive UI (live validation, dependent fields) &rarr; controlled. Medium-to-large production forms &rarr; React Hook Form. Forms tied to server actions &rarr; React 19&rsquo;s <code>useActionState</code> with uncontrolled inputs and FormData. Avoid raw uncontrolled refs unless you have a specific reason &mdash; they&rsquo;re fine but less ergonomic than the alternatives.</p>
'''

ANSWERS[94] = r'''
<p>Protected routes restrict access to authenticated users (or users with specific roles). The pattern wraps protected pages with a guard component that redirects unauthenticated users to login &mdash; preserving their intended destination so they return there after sign-in.</p>

<p><strong>The core pattern (React Router v6+)</strong>:</p>

<pre><code>import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";

function ProtectedRoute({ children, requiredRole }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return &lt;LoadingScreen /&gt;;

  if (!user) {
    // Save destination; login can redirect back after success
    return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  }

  if (requiredRole &amp;&amp; user.role !== requiredRole) {
    return &lt;Navigate to="/forbidden" replace /&gt;;
  }

  return children;
}

// Route definitions
&lt;Routes&gt;
  &lt;Route path="/login" element={&lt;Login /&gt;} /&gt;
  &lt;Route path="/dashboard" element={
    &lt;ProtectedRoute&gt;&lt;Dashboard /&gt;&lt;/ProtectedRoute&gt;
  } /&gt;
  &lt;Route path="/admin" element={
    &lt;ProtectedRoute requiredRole="admin"&gt;&lt;AdminPanel /&gt;&lt;/ProtectedRoute&gt;
  } /&gt;
&lt;/Routes&gt;</code></pre>

<p><strong>The login form reads the original destination</strong>:</p>

<pre><code>function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const handleLogin = async (creds) =&gt; {
    await login(creds);
    navigate(from, { replace: true });   // back to where they came from
  };
}</code></pre>

<p><strong>Three subtleties that matter:</strong></p>

<table>
  <tr><th>Concern</th><th>Solution</th></tr>
  <tr><td>Loading state during auth check</td><td>Show loader while <code>isLoading</code>; without this, brief flash of "redirecting to login" even for authenticated users</td></tr>
  <tr><td>Direct URL navigation</td><td>SPA route fallback (server serves <code>index.html</code> for all paths) &mdash; otherwise <code>/dashboard</code> 404s on refresh</td></tr>
  <tr><td><code>replace</code> on redirect</td><td>Login page shouldn&rsquo;t pollute history &mdash; back button goes to where user came from, not back to /login</td></tr>
</table>

<p><strong>Loaders with React Router v6.4+ data API &mdash; cleaner approach</strong>:</p>

<pre><code>import { redirect } from "react-router-dom";

const dashboardLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  if (!user.canAccessDashboard) throw redirect("/forbidden");
  return user;
};

&lt;Route path="/dashboard" loader={dashboardLoader} element={&lt;Dashboard /&gt;} /&gt;</code></pre>

<p>Loaders run before render &mdash; no flash of authenticated content; no &ldquo;loading then redirect&rdquo; UX. This is the modern recommended pattern in React Router v6.4+ and v7, mirroring Remix.</p>

<p><strong>Server-side checks are mandatory</strong>: client-side route guards are a UX optimization, NOT security. Anyone can disable JS, modify the bundle, or call your API directly. Every protected API endpoint must verify auth on the server &mdash; the route guard just prevents authenticated users from seeing a broken UI.</p>

<p><strong>For Next.js apps</strong>, middleware (<code>middleware.ts</code>) handles route protection at the edge before any React code runs &mdash; faster and more secure than client-side guards. Modern auth libraries (Clerk, NextAuth.js, Supabase Auth) provide drop-in middleware integrations.</p>
'''

ANSWERS[95] = r'''
<p>Image lazy loading defers loading off-screen images until they&rsquo;re about to enter the viewport. Cuts initial page weight, accelerates first paint, and saves bandwidth for content users may never reach. The 2026 default: <strong>native browser lazy loading</strong> via <code>loading="lazy"</code>; libraries fill in for advanced needs.</p>

<p><strong>Native lazy loading &mdash; one attribute</strong>:</p>

<pre><code>&lt;img
  src="/large-photo.jpg"
  alt="Mountain at sunset"
  loading="lazy"
  width={800}
  height={600}
/&gt;</code></pre>

<p>Browser handles everything: defers download until image is near viewport, prioritizes visible images, respects prefers-reduced-data. Universal browser support since 2022. <strong>Always include <code>width</code> and <code>height</code> (or aspect-ratio CSS)</strong> &mdash; without them, you get layout shift as images load (CLS hits Core Web Vitals).</p>

<p><strong>What native lazy loading doesn&rsquo;t do</strong>:</p>

<table>
  <tr><th>Limitation</th><th>Solution</th></tr>
  <tr><td>No control over distance threshold</td><td>IntersectionObserver custom impl</td></tr>
  <tr><td>No blur-up / placeholder</td><td>LQIP (Low Quality Image Placeholder) libraries</td></tr>
  <tr><td>No automatic responsive sizing</td><td><code>srcset</code> + <code>sizes</code> attributes</td></tr>
  <tr><td>No format negotiation (WebP/AVIF)</td><td><code>&lt;picture&gt;</code> element or CDN</td></tr>
  <tr><td>No automatic CDN optimization</td><td>Image CDN (Cloudinary, imgix, Vercel)</td></tr>
</table>

<p><strong>Responsive images with native lazy loading</strong>:</p>

<pre><code>&lt;img
  src="/photo-800.jpg"
  srcSet="/photo-400.jpg 400w, /photo-800.jpg 800w, /photo-1600.jpg 1600w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1600px"
  alt="Mountain"
  loading="lazy"
  width={800}
  height={600}
/&gt;</code></pre>

<p>Browser picks the right size for the user&rsquo;s viewport and DPR. Phones don&rsquo;t download desktop-sized images.</p>

<p><strong>Modern format negotiation</strong>:</p>

<pre><code>&lt;picture&gt;
  &lt;source srcSet="/photo.avif" type="image/avif" /&gt;
  &lt;source srcSet="/photo.webp" type="image/webp" /&gt;
  &lt;img src="/photo.jpg" alt="..." loading="lazy" width={800} height={600} /&gt;
&lt;/picture&gt;</code></pre>

<p>Browsers pick AVIF if supported (smallest), WebP next, JPEG fallback. AVIF is typically 30-50% smaller than JPEG at equivalent quality.</p>

<p><strong>Next.js Image component</strong> &mdash; the production sweet spot for Next.js apps:</p>

<pre><code>import Image from "next/image";

&lt;Image
  src="/photo.jpg"
  alt="Mountain"
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."   // tiny LQIP
  priority={false}        // only true for above-fold critical images
/&gt;</code></pre>

<p>Auto-generates responsive srcsets, optimizes format (WebP/AVIF), serves from CDN, lazy loads, prevents layout shift. <strong>For non-Next apps</strong>: <strong>react-lazy-load-image-component</strong>, <strong>Cloudinary&rsquo;s react SDK</strong>, or build with native + IntersectionObserver for custom needs.</p>

<p><strong>The whole-page perspective</strong>: lazy loading is one of several image optimizations. The full stack is responsive sizes (<code>srcset</code>), modern formats (AVIF/WebP), lazy loading, CDN delivery, dimensions to prevent CLS, and image-CDN auto-optimization. Done well, image weight drops 60-80% with no perceptible quality loss.</p>
'''

ANSWERS[96] = r'''
<p>The <strong>Rules of Hooks</strong> are two non-negotiable constraints that React requires. Violating them causes subtle, hard-to-debug bugs &mdash; or simply makes hooks not work. They&rsquo;re enforced by ESLint via <code>eslint-plugin-react-hooks</code>.</p>

<p><strong>The two rules:</strong></p>

<table>
  <tr><th>Rule</th><th>Bad</th><th>Good</th></tr>
  <tr><td>1. Only call hooks at the top level</td><td>Inside loops, conditions, or nested functions</td><td>Top of component or custom hook</td></tr>
  <tr><td>2. Only call hooks from React functions</td><td>Class components, regular JS functions</td><td>Function components, other custom hooks</td></tr>
</table>

<p><strong>Rule 1 example &mdash; why order matters</strong>:</p>

<pre><code>// BAD — hook inside conditional
function Profile({ userId }) {
  if (userId) {
    const [data, setData] = useState(null);   // ✗ violates rule 1
  }
  // React expects N hooks in same order each render
  // Some renders have 1 hook, others have 0 — internal state misaligned
}

// GOOD — hook always at top, conditional logic inside
function Profile({ userId }) {
  const [data, setData] = useState(null);
  if (userId) { /* logic */ }
}</code></pre>

<p><strong>The mechanism behind rule 1</strong>: React tracks hook calls by call order, not by name. <code>useState</code> at index 0, <code>useEffect</code> at index 1, etc. If conditions change which hooks run, indexes shift &mdash; React reads state from the wrong hook. Bugs are non-deterministic and confusing.</p>

<p><strong>Rule 2 example</strong>:</p>

<pre><code>// BAD — calling hook in regular function
function getUserData(userId) {
  const [data, setData] = useState(null);   // ✗ not a React function
  return data;
}

// GOOD — custom hook (name starts with &ldquo;use&rdquo;)
function useUserData(userId) {
  const [data, setData] = useState(null);
  // ...
  return data;
}

// GOOD — used inside a component
function Profile({ userId }) {
  const data = useUserData(userId);
}</code></pre>

<p><strong>The "use" naming convention is enforced</strong>: ESLint&rsquo;s rule recognizes functions starting with <code>use</code> as custom hooks. Naming them anything else means hooks inside won&rsquo;t be checked &mdash; bugs slip through.</p>

<p><strong>Common violations and fixes:</strong></p>

<table>
  <tr><th>Violation</th><th>Fix</th></tr>
  <tr><td><code>if (a) useEffect(...)</code></td><td>Move condition inside effect</td></tr>
  <tr><td><code>data.map(d =&gt; useState(d))</code></td><td>Single useState with array; or restructure as components</td></tr>
  <tr><td>Early return before hooks</td><td>Move all hooks above any early returns</td></tr>
  <tr><td>Hook in a callback</td><td>Hooks must be in the function body, not callbacks</td></tr>
  <tr><td>Async function as component</td><td>Components are sync; use Server Components or move async to effect</td></tr>
</table>

<p><strong>The lint rule is your friend</strong> &mdash; configure <code>eslint-plugin-react-hooks</code> with errors enabled (not warnings). Catching violations at lint time saves debugging at runtime. The <code>react-hooks/exhaustive-deps</code> rule (also from this plugin) catches missing dependencies in effect arrays &mdash; another high-value bug class.</p>

<p><strong>Why these rules exist (the deeper reason)</strong>: hooks were designed to fit inside React&rsquo;s render cycle. The constraints aren&rsquo;t arbitrary &mdash; they&rsquo;re what makes hooks possible without per-component instance state or class boilerplate. Conditional hooks would require either tagging each hook with an identifier (verbose, error-prone) or React tracking hooks by call site (impossible in JS without compiler magic). The rules trade a small constraint for a clean API.</p>
'''

ANSWERS[97] = r'''
<p>State management in React Native uses the same React fundamentals as web (hooks, Context, external libraries) plus mobile-specific concerns: persistence across app restarts, AsyncStorage, sync between native modules, and offline-first patterns. <strong>Zustand</strong>, <strong>Redux Toolkit</strong>, and <strong>Jotai</strong> all work identically; <strong>TanStack Query</strong> handles server state.</p>

<p><strong>The state landscape in RN (2026):</strong></p>

<table>
  <tr><th>State type</th><th>Tool</th></tr>
  <tr><td>Local component state</td><td><code>useState</code>, <code>useReducer</code></td></tr>
  <tr><td>Lightweight global state</td><td>Zustand (most popular for RN)</td></tr>
  <tr><td>Server data</td><td>TanStack Query / Apollo Client</td></tr>
  <tr><td>Theme, locale, auth</td><td>React Context</td></tr>
  <tr><td>Complex state with middleware</td><td>Redux Toolkit + Redux Persist</td></tr>
  <tr><td>Persisted state</td><td>AsyncStorage / MMKV with state library</td></tr>
  <tr><td>Form state</td><td>React Hook Form (works identically to web)</td></tr>
</table>

<p><strong>Persistence with MMKV (faster than AsyncStorage)</strong>:</p>

<pre><code>import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { MMKV } from "react-native-mmkv";

const storage = new MMKV();

const zustandStorage = {
  setItem: (name, value) =&gt; storage.set(name, value),
  getItem: (name) =&gt; storage.getString(name) ?? null,
  removeItem: (name) =&gt; storage.delete(name)
};

const useAppStore = create(
  persist(
    (set) =&gt; ({
      user: null,
      preferences: { theme: "light" },
      setUser: (user) =&gt; set({ user }),
      setTheme: (theme) =&gt; set((s) =&gt; ({ preferences: { ...s.preferences, theme } }))
    }),
    {
      name: "app-store",
      storage: createJSONStorage(() =&gt; zustandStorage)
    }
  )
);</code></pre>

<p>State auto-restores on app launch &mdash; user stays logged in across restarts. <strong>MMKV</strong> is dramatically faster than AsyncStorage (synchronous reads, native-side serialization) and now standard in modern RN apps.</p>

<p><strong>TanStack Query with offline support</strong>:</p>

<pre><code>import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { persistQueryClient } from "@tanstack/react-query-persist-client";
import { createAsyncStoragePersister } from "@tanstack/query-async-storage-persister";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60 * 5 } }
});

const persister = createAsyncStoragePersister({
  storage: AsyncStorage   // or MMKV adapter
});

persistQueryClient({ queryClient, persister });</code></pre>

<p>Cached server data persists across app launches; users see content instantly while background refetch updates it &mdash; offline-first UX.</p>

<p><strong>RN-specific concerns:</strong></p>

<table>
  <tr><th>Concern</th><th>Approach</th></tr>
  <tr><td>App state changes (foreground/background)</td><td><code>AppState</code> API + listener; refetch on resume</td></tr>
  <tr><td>Network state</td><td><code>@react-native-community/netinfo</code>; pause queries when offline</td></tr>
  <tr><td>Optimistic mutations with sync</td><td>TanStack Query mutations + outbox pattern</td></tr>
  <tr><td>Cross-screen state via navigation</td><td>State libraries OR navigation params (not both)</td></tr>
  <tr><td>Push notification state</td><td>Background tasks + state library write</td></tr>
</table>

<p><strong>Don&rsquo;t put navigation state in your global store</strong>: React Navigation has its own state machine. Mixing creates desync bugs. Keep them separate; pass relevant data via route params or sync explicit fields. <strong>For real-time data</strong> (chat, presence), pair Zustand/Redux with WebSocket via custom hook + <code>useEffect</code>; or use libraries like Liveblocks or Convex with first-class RN support.</p>
'''

ANSWERS[98] = r'''
<p><code>useReducer</code> shines for <strong>complex state logic</strong>: many transitions, derived state, validation rules, undo/redo, or state shape that must maintain invariants. Where <code>useState</code> grows ugly fast, <code>useReducer</code> stays clean &mdash; all transitions live in one place, the reducer.</p>

<p><strong>When to graduate from useState to useReducer:</strong></p>

<table>
  <tr><th>Symptom</th><th>useReducer fixes</th></tr>
  <tr><td>5+ <code>useState</code> calls in one component</td><td>Single state object, single reducer</td></tr>
  <tr><td>Multiple setStates need to happen together</td><td>Atomic transition in one action</td></tr>
  <tr><td>Logic spans many event handlers</td><td>Centralized in reducer</td></tr>
  <tr><td>State must maintain invariants</td><td>Reducer enforces them</td></tr>
  <tr><td>Want to test transitions without rendering</td><td>Reducer is pure &mdash; unit-testable</td></tr>
  <tr><td>Need undo/redo</td><td>State snapshots fit naturally</td></tr>
</table>

<p><strong>A complex form wizard with validation, branching, and undo</strong>:</p>

<pre><code>type WizardState = {
  step: number;
  data: { personal: PersonalInfo; address: Address; payment: Payment };
  errors: Record&lt;string, string&gt;;
  history: WizardState[];
};

type Action =
  | { type: "UPDATE"; section: keyof WizardState["data"]; values: Partial&lt;...&gt; }
  | { type: "VALIDATE"; errors: Record&lt;string, string&gt; }
  | { type: "NEXT" }
  | { type: "PREV" }
  | { type: "UNDO" }
  | { type: "RESET" };

function reducer(state: WizardState, action: Action): WizardState {
  switch (action.type) {
    case "UPDATE":
      return {
        ...state,
        data: { ...state.data, [action.section]: { ...state.data[action.section], ...action.values } },
        errors: {},
        history: [...state.history, state]   // snapshot for undo
      };

    case "VALIDATE":
      return { ...state, errors: action.errors };

    case "NEXT":
      // Block advance if errors
      if (Object.keys(state.errors).length &gt; 0) return state;
      return { ...state, step: Math.min(state.step + 1, 2), history: [...state.history, state] };

    case "PREV":
      return { ...state, step: Math.max(state.step - 1, 0) };

    case "UNDO": {
      const previous = state.history[state.history.length - 1];
      if (!previous) return state;
      return { ...previous, history: state.history.slice(0, -1) };
    }

    case "RESET":
      return INITIAL_STATE;

    default:
      return state;
  }
}

function CheckoutWizard() {
  const [state, dispatch] = useReducer(reducer, INITIAL_STATE);

  return (
    &lt;&gt;
      {state.step === 0 &amp;&amp; &lt;PersonalStep data={state.data.personal} dispatch={dispatch} /&gt;}
      {state.step === 1 &amp;&amp; &lt;AddressStep data={state.data.address} dispatch={dispatch} /&gt;}
      {state.step === 2 &amp;&amp; &lt;PaymentStep data={state.data.payment} dispatch={dispatch} /&gt;}

      &lt;button onClick={() =&gt; dispatch({ type: "PREV" })} disabled={state.step === 0}&gt;Back&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch({ type: "NEXT" })}&gt;Next&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch({ type: "UNDO" })} disabled={!state.history.length}&gt;Undo&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Why this wins over many useStates</strong>:</p>
<ul>
  <li><strong>Atomic transitions</strong> &mdash; "advance step + clear errors + snapshot history" happens together. With multiple useStates, you&rsquo;d have race conditions.</li>
  <li><strong>Pure logic, testable</strong> &mdash; <code>expect(reducer(state, { type: "NEXT" }).step).toBe(1)</code> requires no rendering.</li>
  <li><strong>Documented transitions</strong> &mdash; reading the reducer tells you everything that can happen to state. With scattered <code>setState</code> calls, you trace through every component to learn the state machine.</li>
  <li><strong>Time-travel debugging</strong> &mdash; the action log is the change history; replay actions to reach any past state.</li>
</ul>

<p><strong>Lazy initializer for expensive setup</strong>:</p>

<pre><code>const [state, dispatch] = useReducer(reducer, undefined, init);
// init() runs once, returns initial state — useful when computing from props or storage</code></pre>

<p><strong>For app-wide complex state</strong>: lift this reducer into Context (Q89), or graduate to Redux Toolkit / Zustand. <code>useReducer</code> stays component-local; Redux Toolkit is essentially the same pattern app-wide with better tooling, middleware, and selectors.</p>
'''

ANSWERS[99] = r'''
<p>Nested routes let you compose UI by nesting routes inside a parent layout. The parent renders shared chrome (sidebar, header, breadcrumbs); the matching child fills in the content area via <code>&lt;Outlet /&gt;</code>. URL structure mirrors UI hierarchy.</p>

<p><strong>The pattern with React Router v6+</strong>:</p>

<pre><code>import { Routes, Route, Outlet, Link, NavLink } from "react-router-dom";

// Parent layout — shared chrome + outlet for nested content
function DashboardLayout() {
  return (
    &lt;div className="dashboard"&gt;
      &lt;aside&gt;
        &lt;NavLink to="overview"&gt;Overview&lt;/NavLink&gt;
        &lt;NavLink to="users"&gt;Users&lt;/NavLink&gt;
        &lt;NavLink to="settings"&gt;Settings&lt;/NavLink&gt;
      &lt;/aside&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;     {/* nested route renders here */}
      &lt;/main&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;Routes&gt;
      &lt;Route path="/" element={&lt;Home /&gt;} /&gt;

      &lt;Route path="/dashboard" element={&lt;DashboardLayout /&gt;}&gt;
        &lt;Route index element={&lt;DashboardHome /&gt;} /&gt;
        &lt;Route path="overview" element={&lt;Overview /&gt;} /&gt;
        &lt;Route path="users" element={&lt;UsersList /&gt;} /&gt;
        &lt;Route path="users/:userId" element={&lt;UserDetail /&gt;} /&gt;
        &lt;Route path="settings" element={&lt;Settings /&gt;} /&gt;
      &lt;/Route&gt;
    &lt;/Routes&gt;
  );
}</code></pre>

<p><strong>How URL matching maps to rendering</strong>:</p>

<table>
  <tr><th>URL</th><th>Renders</th></tr>
  <tr><td><code>/</code></td><td>Home</td></tr>
  <tr><td><code>/dashboard</code></td><td>DashboardLayout + DashboardHome (index)</td></tr>
  <tr><td><code>/dashboard/overview</code></td><td>DashboardLayout + Overview</td></tr>
  <tr><td><code>/dashboard/users</code></td><td>DashboardLayout + UsersList</td></tr>
  <tr><td><code>/dashboard/users/42</code></td><td>DashboardLayout + UserDetail (userId="42")</td></tr>
</table>

<p><strong>Index routes</strong>: <code>&lt;Route index element={...}/&gt;</code> matches when the parent path is hit without a child segment. Without it, <code>/dashboard</code> would render only the layout (empty outlet area).</p>

<p><strong>Multi-level nesting works the same way</strong>:</p>

<pre><code>&lt;Route path="/admin" element={&lt;AdminLayout /&gt;}&gt;
  &lt;Route path="users" element={&lt;UsersLayout /&gt;}&gt;
    &lt;Route index element={&lt;UsersList /&gt;} /&gt;
    &lt;Route path=":userId" element={&lt;UserLayout /&gt;}&gt;
      &lt;Route index element={&lt;UserOverview /&gt;} /&gt;
      &lt;Route path="posts" element={&lt;UserPosts /&gt;} /&gt;
      &lt;Route path="settings" element={&lt;UserSettings /&gt;} /&gt;
    &lt;/Route&gt;
  &lt;/Route&gt;
&lt;/Route&gt;</code></pre>

<p>Three layouts deep; URL mirrors the structure (<code>/admin/users/42/posts</code>).</p>

<p><strong>Benefits over flat routing</strong>:</p>

<table>
  <tr><th>Benefit</th><th>Why</th></tr>
  <tr><td>Co-located layouts</td><td>Each level&rsquo;s chrome is defined once</td></tr>
  <tr><td>Sibling navigation preserves layout state</td><td>Going /users → /settings keeps sidebar scroll position, etc.</td></tr>
  <tr><td>URL == UI hierarchy</td><td>Mental model matches user&rsquo;s view</td></tr>
  <tr><td>Per-segment data loading</td><td>Loaders can load data per route level</td></tr>
</table>

<p><strong>Loaders + nested routes (React Router v6.4+)</strong>:</p>

<pre><code>const dashboardLoader = async () =&gt; getCurrentUser();
const userLoader = async ({ params }) =&gt; getUser(params.userId);

createBrowserRouter([
  {
    path: "/dashboard",
    element: &lt;DashboardLayout /&gt;,
    loader: dashboardLoader,
    children: [
      {
        path: "users/:userId",
        element: &lt;UserDetail /&gt;,
        loader: userLoader
      }
    ]
  }
]);</code></pre>

<p>Each loader runs in parallel where possible &mdash; React Router waits for all of them, then renders the full nested tree. <strong>Next.js App Router</strong> goes even further: nested routes are file-system-based (each <code>page.tsx</code> in nested folders) with native streaming, server components, and per-segment loaders/error boundaries.</p>

<p><strong>Pitfalls</strong>: forgetting <code>&lt;Outlet /&gt;</code> in the parent (children never appear); forgetting the <code>index</code> route (parent path renders empty); using absolute paths inside nested routes (use relative paths so they compose).</p>
'''

ANSWERS[100] = r'''
<p>Scalable, maintainable React code is built on consistent patterns: clear file organization, type safety, separation of concerns, well-bounded components, deliberate state management, automated quality gates, and strong testing culture. The principles below scale a 10-component prototype into a 1000-component product.</p>

<p><strong>1. File organization &mdash; feature-based, not type-based:</strong></p>

<pre><code>src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── index.ts          ← public API barrel
│   ├── dashboard/
│   └── checkout/
├── shared/
│   ├── components/            ← truly reusable across features
│   ├── hooks/
│   ├── lib/                   ← pure utilities
│   └── ui/                    ← design system primitives
└── app/                       ← routes, providers, app shell</code></pre>

<p>Features stay self-contained; shared code is genuinely shared (used by multiple features). Avoid grouping by type (<code>components/</code>, <code>hooks/</code>, <code>utils/</code>) &mdash; it scales poorly because every feature change touches every folder.</p>

<p><strong>2. Component design principles:</strong></p>

<table>
  <tr><th>Principle</th><th>Why</th></tr>
  <tr><td>Single responsibility</td><td>One reason to change; easier to test, reuse, refactor</td></tr>
  <tr><td>Small components (~150 lines max)</td><td>Beyond this, split. Long components hide bugs.</td></tr>
  <tr><td>Props as the public API</td><td>Make required props explicit; use TypeScript</td></tr>
  <tr><td>Compose, don&rsquo;t inherit</td><td>Children, slots, render props &mdash; React favors composition</td></tr>
  <tr><td>Co-locate related code</td><td>Component + tests + styles + types together</td></tr>
</table>

<p><strong>3. Separation of concerns &mdash; the layered approach</strong>:</p>

<pre><code>UI components       → presentational, take props, no fetching
Custom hooks        → business logic, state, side effects
API clients         → talk to network; no React
Pure utilities      → no React; testable in isolation</code></pre>

<p>UI components depend on hooks; hooks depend on API clients; API clients depend on utilities. Nothing depends upward. This makes refactoring possible &mdash; swap an API, only the API client changes.</p>

<p><strong>4. State management discipline:</strong></p>

<table>
  <tr><th>State type</th><th>Tool</th></tr>
  <tr><td>UI state, ephemeral</td><td><code>useState</code></td></tr>
  <tr><td>Form state</td><td>React Hook Form + Zod</td></tr>
  <tr><td>Server data</td><td>TanStack Query</td></tr>
  <tr><td>Global client state</td><td>Zustand or Context</td></tr>
  <tr><td>URL state</td><td>Search params via router</td></tr>
</table>

<p>Use the simplest tool that fits. Don&rsquo;t put server data in Redux; don&rsquo;t use Context for high-frequency updates; don&rsquo;t use Zustand for what should be component-local.</p>

<p><strong>5. Type safety &mdash; non-negotiable for production</strong>: TypeScript with <code>strict: true</code>; types from Zod schemas (single source of truth for runtime + compile-time); <code>unknown</code> over <code>any</code>; discriminated unions for state machines; <code>satisfies</code> over assertion.</p>

<p><strong>6. Quality gates that prevent regression:</strong></p>

<table>
  <tr><th>Gate</th><th>Tool</th></tr>
  <tr><td>Code style</td><td>Prettier (auto-format on save)</td></tr>
  <tr><td>Code quality</td><td>ESLint + react-hooks plugin</td></tr>
  <tr><td>Type safety</td><td>tsc with --noEmit on PR</td></tr>
  <tr><td>Tests</td><td>Vitest + RTL on PR</td></tr>
  <tr><td>E2E</td><td>Playwright critical paths on PR</td></tr>
  <tr><td>Bundle size</td><td>size-limit / @next/bundle-analyzer</td></tr>
  <tr><td>Performance</td><td>Lighthouse CI on staging</td></tr>
</table>

<p>All run in CI. Fail the PR if anything fails. Don&rsquo;t merge red builds.</p>

<p><strong>7. Documentation that doesn&rsquo;t rot</strong>: TypeScript types are documentation; JSDoc on public APIs; Storybook for components; README per feature with the &ldquo;why&rdquo;; CHANGELOG for releases.</p>

<p><strong>8. The bigger picture</strong>: scalability isn&rsquo;t about premature abstraction. Most "clever" patterns (HOCs everywhere, complex generic hooks, framework-on-top-of-React) hurt more than they help. The teams that ship reliably for years use boring code: TypeScript, hooks, Zustand/TanStack Query, RTL tests, Prettier. <strong>Boring is good</strong>; novelty has costs. The goal is code your replacement can extend in a year &mdash; not code that demonstrates how clever you are.</p>
'''
